#!/usr/bin/env python3
"""F7 -- Divisi M (ML & Meta-labeling).

M06/M07/M08 (Lasso/Ridge/ElasticNet) BASELINE WAJIB (aturan M6): model
lain harus mengalahkan ini. M01 (CatBoost), M02 (XGBoost, monotone
constraint positif pada fitur bertipe momentum -- prior kelanjutan tren),
M03 (LightGBM) ditambahkan sebagai model tree-ensemble. Validasi HANYA
CPCV purged+embargo (M1) -- K-fold biasa DILARANG. Fitur: sekumpulan
estimator CONTINU (bukan sudah di-threshold) dari formula V/E yang sudah
dihitung, memprediksi return forward H60, lalu threshold prediksi jadi
sinyal +1/-1/0, dievaluasi lewat gate_checklist yang sama seperti F5/F6.

M11 meta-labeling (PRIORITAS TERTINGGI divisi M): primer = sinyal E
dengan net-expectancy terbaik dari F6_screening.md (sinyal DASAR, bukan
kombinasi entry x exit -- meta-labeling pakai baseline X01 sendiri),
diambil dari laporan F6 yang sudah selesai, bukan ditebak/di-hardcode.
Sekunder = classifier biner (regularized logistic) memprediksi menang/
kalah trade primer, threshold 0.5/0.6.
"""
import sys
sys.path.insert(0, "/workspace")

import re
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Lasso, Ridge, ElasticNet, LogisticRegression
from sklearn.preprocessing import StandardScaler

from src.labeling.triple_barrier import triple_barrier_labels, parkinson_sigma
from src.formulas import pilot_f2b as pf
from src.formulas import division_e as de
from src.validation.cpcv import cpcv_splits
from src.validation.gate_checklist import evaluate_candidate, apply_batch_checks
from run_f4_estimation import load_m1_full
from run_f6_division_e import build_all_base_signals

try:
    from catboost import CatBoostRegressor
except ImportError:
    CatBoostRegressor = None
try:
    from xgboost import XGBRegressor
except ImportError:
    XGBRegressor = None
try:
    from lightgbm import LGBMRegressor
except ImportError:
    LGBMRegressor = None
TREE_LIBS_AVAILABLE = all(c is not None for c in (CatBoostRegressor, XGBRegressor, LGBMRegressor))

REPORTS_DIR = Path("/workspace/reports")
COST_BPS_WORST = 3.0
MAX_HOLD_BARS = 60
SIGMA_WINDOW = 96
BARS_PER_YEAR = 365 * 24 * 60
K_SL, K_TP = 1.5, 2.5


def load_best_f6_base_signal_name():
    """Parse reports/F6_screening.md's full ledger table for the base
    signal (name without '_x_' -- i.e. not an entry x exit combo) with
    the highest net expectancy_bps. Returns None if the report is missing
    or unparseable -- caller must handle that explicitly, not guess."""
    report_path = REPORTS_DIR / "F6_screening.md"
    if not report_path.exists():
        return None
    text = report_path.read_text()
    best_name, best_net = None, -1e18
    for line in text.splitlines():
        m = re.match(r"\|\s*([A-Za-z0-9_.]+)\s*\|\s*(\d+)\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|", line)
        if not m:
            continue
        name = m.group(1)
        if name in ("Kandidat",) or "_x_" in name:
            continue
        try:
            net_bps = float(m.group(4))
        except ValueError:
            continue
        if net_bps > best_net:
            best_name, best_net = name, net_bps
    return best_name


def build_continuous_features(mid, high, low, open_, sigma, n):
    """Continuous (pre-threshold) versions of several E/V signals, for
    the linear models to actually regress on -- feeding them already-
    thresholded +-1 signals would throw away most of the information."""
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    feats = {}
    feats["mom_12"] = np.concatenate([[0] * 12, (mid[12:] - mid[:-12]) / mid[:-12]])
    feats["mom_48"] = np.concatenate([[0] * 48, (mid[48:] - mid[:-48]) / mid[:-48]])
    feats["vol_scaled_mom_12"] = pf.e01_intraday_momentum(mid, 12)  # already causal sign; kept as weak feature
    feats["drift_burst"] = np.nan_to_num(
        (pd.Series(r).rolling(6).mean().values * np.sqrt(6)) / (pd.Series(r).rolling(24).std().values + 1e-12), nan=0.0
    )
    feats["mann_kendall_z"] = _mann_kendall_z_series(mid, window=48)
    feats["sigma_bps"] = np.nan_to_num(sigma * 1e4, nan=np.nanmedian(sigma) * 1e4)
    feats["realized_skew_48"] = _realized_skew_series(r, window=48)
    X = np.column_stack([feats[k] for k in feats])
    return X, list(feats.keys())


def _mann_kendall_z_series(mid, window):
    n = len(mid)
    out = np.zeros(n)
    for t in range(window, n, 5):  # subsample every 5 bars for speed, forward-fill between
        x = mid[t - window : t]
        s = 0
        for i in range(len(x)):
            s += np.sum(np.sign(x[i + 1 :] - x[i]))
        out[t] = s
    out = pd.Series(out).replace(0, np.nan).ffill().fillna(0).values
    return out / (window**2)  # normalize roughly to O(1)


def _realized_skew_series(r, window):
    n = len(r)
    out = np.zeros(n)
    roll = pd.Series(r).rolling(window)
    rv = roll.apply(lambda x: np.sum(x**2), raw=True).values
    r3 = roll.apply(lambda x: np.sum(x**3), raw=True).values
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.sqrt(window) * r3 / np.power(np.maximum(rv, 1e-15), 1.5)
    return np.nan_to_num(out, nan=0.0)


def main():
    print("Memuat data...")
    m1 = load_m1_full("XAUUSD")
    n_total = len(m1)
    screen = m1.iloc[: int(n_total * 0.20)].reset_index(drop=True)

    mid = screen["mid_close"].values
    high = screen["ask_high"].values
    low = screen["bid_low"].values
    open_ = screen["bid_open"].values
    spread_bps = screen["spread_bps"].values
    sigma = parkinson_sigma(high, low, window=SIGMA_WINDOW)
    sigma_bps = sigma * 1e4
    n = len(mid)
    bar_returns = np.diff(np.log(mid), prepend=np.log(mid[0]))

    print("Membangun fitur kontinu...")
    X_full, feat_names = build_continuous_features(mid, high, low, open_, sigma, n)

    fwd_ret = np.full(n, np.nan)
    for t in range(n - MAX_HOLD_BARS):
        fwd_ret[t] = mid[t + MAX_HOLD_BARS] / mid[t] - 1

    valid_rows = (~np.isnan(X_full).any(axis=1)) & (~np.isnan(fwd_ret)) & (np.arange(n) > SIGMA_WINDOW)
    idx_valid = np.where(valid_rows)[0]
    sample_idx = idx_valid[:: max(1, len(idx_valid) // 15000)]  # subsample for CPCV cost
    X = X_full[sample_idx]
    y = fwd_ret[sample_idx]
    label_starts = sample_idx
    label_ends = np.minimum(sample_idx + MAX_HOLD_BARS, n - 1)

    print(f"{len(sample_idx):,} sampel valid untuk CPCV. Menjalankan CPCV purged+embargo (12x2=66 path, subset dipakai)...")

    all_evals = []
    models = {
        "M06_LASSO": lambda alpha: Lasso(alpha=alpha, max_iter=5000),
        "M07_RIDGE": lambda alpha: Ridge(alpha=alpha),
        "M08_ELASTIC_NET": lambda alpha, l1r: ElasticNet(alpha=alpha, l1_ratio=l1r, max_iter=5000),
    }

    def run_regression_model(name, model_fn, threshold_pctl=60):
        oof_pred = np.full(len(sample_idx), np.nan)
        splits = list(cpcv_splits(n, label_starts, label_ends, n_groups=12, n_test_groups=2, embargo_bars=MAX_HOLD_BARS))
        for split in splits[:12]:  # subset of paths for compute budget, still purged+embargo
            train_idx, test_idx = split.train_idx, split.test_idx
            if len(train_idx) < 100 or len(test_idx) < 20:
                continue
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X[train_idx])  # §L3: fit scaler on TRAIN fold only
            X_test = scaler.transform(X[test_idx])
            model = model_fn()
            model.fit(X_train, y[train_idx])
            pred = model.predict(X_test)
            oof_pred[test_idx] = pred

        has_pred = ~np.isnan(oof_pred)
        if has_pred.sum() < 100:
            print(f"  {name}: TERLALU SEDIKIT prediksi OOF, dilewati")
            return
        thresh = np.percentile(np.abs(oof_pred[has_pred]), threshold_pctl)
        signal = np.where(oof_pred > thresh, 1, np.where(oof_pred < -thresh, -1, 0))

        sig_positions = sample_idx[has_pred][signal[has_pred] != 0]
        sig_directions = signal[has_pred][signal[has_pred] != 0]
        if len(sig_positions) < 30:
            print(f"  {name}: TERLALU SEDIKIT sinyal setelah threshold, dilewati")
            return
        entry_bars = sig_positions + 1
        valid_entries = entry_bars < (n - MAX_HOLD_BARS - 1)
        entry_bars, sig_directions = entry_bars[valid_entries], sig_directions[valid_entries]
        res = triple_barrier_labels(open_, high, low, mid, entry_bars, sig_directions.astype(np.int64), sigma, K_SL, K_TP, MAX_HOLD_BARS)
        valid = res.outcome != 0
        if valid.sum() < 30:
            print(f"  {name}: TERLALU SEDIKIT trade valid, dilewati")
            return
        full_signal = np.zeros(n)
        full_signal[sig_positions[valid_entries][valid]] = sig_directions[valid_entries][valid]
        ev = evaluate_candidate(
            name=name, trade_returns=res.ret[valid], entry_bars=entry_bars[valid], holding_bars=res.bars_held[valid],
            mid=mid, n_bars_total=n, bars_per_year=BARS_PER_YEAR, cost_bps_worst=COST_BPS_WORST,
            spread_bps=spread_bps, sigma_bps=sigma_bps, signal_for_mc1=full_signal,
            bar_returns_for_mc1=bar_returns, rng=np.random.default_rng(hash(name) % (2**31)),
        )
        all_evals.append(ev)
        print(f"  {name}: n={ev.n_trades} exp={ev.expectancy_net_bps:.2f}bps t={ev.t_stat_eff_n:.2f} checks={ev.n_checks_passed}/12(+batch)")

    print("\n=== M06 LASSO (baseline wajib) ===")
    for alpha in [0.001, 0.01, 0.1, 1.0]:
        run_regression_model(f"M06_LASSO_a{alpha}", lambda a=alpha: models["M06_LASSO"](a))

    print("\n=== M07 RIDGE (baseline wajib) ===")
    for alpha in [0.01, 0.1, 1.0, 10.0]:
        run_regression_model(f"M07_RIDGE_a{alpha}", lambda a=alpha: models["M07_RIDGE"](a))

    print("\n=== M08 ELASTIC NET ===")
    for alpha in [0.01, 0.1, 1.0]:
        for l1r in [0.3, 0.7]:
            run_regression_model(f"M08_ELASTICNET_a{alpha}_l1{l1r}", lambda a=alpha, l=l1r: models["M08_ELASTIC_NET"](a, l))

    if TREE_LIBS_AVAILABLE:
        # Prior monotonik: fitur bertipe momentum/trend diberi constraint +1 (momentum tinggi ->
        # ekspektasi return forward lebih tinggi, prior kelanjutan tren). sigma_bps & realized_skew
        # tidak punya prior arah yang jelas -> 0 (tidak dikonstrain).
        mono_map = {
            "mom_12": 1, "mom_48": 1, "vol_scaled_mom_12": 1, "drift_burst": 1,
            "mann_kendall_z": 1, "sigma_bps": 0, "realized_skew_48": 0,
        }
        xgb_monotone = tuple(mono_map[f] for f in feat_names)

        print("\n=== M01 CATBOOST ===")
        for depth in [4, 6]:
            for lr in [0.03, 0.1]:
                run_regression_model(
                    f"M01_CATBOOST_d{depth}_lr{lr}",
                    lambda d=depth, l=lr: CatBoostRegressor(
                        depth=d, learning_rate=l, iterations=200, loss_function="RMSE",
                        verbose=False, allow_writing_files=False,
                    ),
                )

        print("\n=== M02 XGBOOST (monotone) ===")
        for depth in [3, 5]:
            for lr in [0.03, 0.1]:
                run_regression_model(
                    f"M02_XGBOOST_MONO_d{depth}_lr{lr}",
                    lambda d=depth, l=lr: XGBRegressor(
                        max_depth=d, learning_rate=l, n_estimators=200,
                        monotone_constraints=xgb_monotone, tree_method="hist", verbosity=0,
                    ),
                )

        print("\n=== M03 LIGHTGBM ===")
        for depth in [4, 6]:
            for lr in [0.03, 0.1]:
                run_regression_model(
                    f"M03_LIGHTGBM_d{depth}_lr{lr}",
                    lambda d=depth, l=lr: LGBMRegressor(max_depth=d, learning_rate=l, n_estimators=200, verbosity=-1),
                )
    else:
        print("\n=== M01/M02/M03 tree-ensemble DILEWATI: library tidak terpasang ===")

    print("\n=== M11 Meta-labeling (prioritas tertinggi divisi M) ===")
    best_f6_name = load_best_f6_base_signal_name()
    if best_f6_name is None:
        print("  F6_screening.md tidak ditemukan/tidak terparse -- fallback ke E01_MOMENTUM_L12 (TIDAK DIVALIDASI sebagai 'terbaik').")
        best_f6_name = "E01_MOMENTUM_L12_FALLBACK_TIDAK_TERVALIDASI"
        primary_signal = pf.e01_intraday_momentum(mid, 12)
    else:
        base_signals = dict(build_all_base_signals(mid, high, low, open_, np.concatenate([[mid[0]], mid[:-1]]), sigma))
        if best_f6_name not in base_signals:
            print(f"  Nama '{best_f6_name}' dari F6_screening.md tidak cocok dengan registry build_all_base_signals -- fallback ke E01_MOMENTUM_L12.")
            best_f6_name = "E01_MOMENTUM_L12_FALLBACK_TIDAK_TERVALIDASI"
            primary_signal = pf.e01_intraday_momentum(mid, 12)
        else:
            print(f"  Primer M11 = sinyal E dengan net expectancy tertinggi di F6_screening.md: {best_f6_name}")
            primary_signal = base_signals[best_f6_name]
    sig_bars = np.where(primary_signal[:-1] != 0)[0]
    sig_bars = sig_bars[(sig_bars > SIGMA_WINDOW) & (sig_bars < n - MAX_HOLD_BARS - 2)]
    entry_bars_primary = sig_bars + 1
    directions_primary = primary_signal[sig_bars].astype(np.int64)
    res_primary = triple_barrier_labels(open_, high, low, mid, entry_bars_primary, directions_primary, sigma, K_SL, K_TP, MAX_HOLD_BARS)
    primary_valid = res_primary.outcome != 0
    primary_win = (res_primary.outcome[primary_valid] == 1).astype(int)
    meta_X = X_full[entry_bars_primary[primary_valid]]
    meta_label_starts = entry_bars_primary[primary_valid]
    meta_label_ends = np.minimum(meta_label_starts + MAX_HOLD_BARS, n - 1)

    for threshold in [0.5, 0.6]:
        oof_prob = np.full(primary_valid.sum(), np.nan)
        splits = list(cpcv_splits(n, meta_label_starts, meta_label_ends, n_groups=12, n_test_groups=2, embargo_bars=MAX_HOLD_BARS))
        for split in splits[:12]:
            train_idx, test_idx = split.train_idx, split.test_idx
            if len(train_idx) < 50 or len(test_idx) < 10 or len(np.unique(primary_win[train_idx])) < 2:
                continue
            scaler = StandardScaler()
            X_train = scaler.fit_transform(meta_X[train_idx])
            X_test = scaler.transform(meta_X[test_idx])
            clf = LogisticRegression(max_iter=1000, C=1.0)
            clf.fit(X_train, primary_win[train_idx])
            oof_prob[test_idx] = clf.predict_proba(X_test)[:, 1]

        has_pred = ~np.isnan(oof_prob)
        take_trade = has_pred & (oof_prob >= threshold)
        if take_trade.sum() < 30:
            print(f"  M11_META_LABELING_t{threshold}: TERLALU SEDIKIT trade lolos filter, dilewati")
            continue
        filtered_ret = res_primary.ret[primary_valid][take_trade]
        filtered_entries = meta_label_starts[take_trade]
        filtered_holds = res_primary.bars_held[primary_valid][take_trade]
        full_signal = np.zeros(n)
        full_signal[filtered_entries] = directions_primary[primary_valid][take_trade]
        ev = evaluate_candidate(
            name=f"M11_META_LABELING_t{threshold}", trade_returns=filtered_ret, entry_bars=filtered_entries,
            holding_bars=filtered_holds, mid=mid, n_bars_total=n, bars_per_year=BARS_PER_YEAR,
            cost_bps_worst=COST_BPS_WORST, spread_bps=spread_bps, sigma_bps=sigma_bps,
            signal_for_mc1=full_signal, bar_returns_for_mc1=bar_returns,
            rng=np.random.default_rng(hash(f"M11_{threshold}") % (2**31)),
        )
        all_evals.append(ev)
        print(f"  M11_META_LABELING_t{threshold}: n={ev.n_trades} exp={ev.expectancy_net_bps:.2f}bps t={ev.t_stat_eff_n:.2f} checks={ev.n_checks_passed}/12(+batch)")

    # unfiltered primary for comparison (M6: must beat "sinyal primer polos")
    if primary_valid.sum() >= 30:
        full_signal_primary = np.zeros(n)
        full_signal_primary[entry_bars_primary[primary_valid]] = directions_primary[primary_valid]
        ev_primary = evaluate_candidate(
            name=f"M_PRIMARY_UNFILTERED_{best_f6_name}", trade_returns=res_primary.ret[primary_valid],
            entry_bars=entry_bars_primary[primary_valid], holding_bars=res_primary.bars_held[primary_valid],
            mid=mid, n_bars_total=n, bars_per_year=BARS_PER_YEAR, cost_bps_worst=COST_BPS_WORST,
            spread_bps=spread_bps, sigma_bps=sigma_bps, signal_for_mc1=full_signal_primary,
            bar_returns_for_mc1=bar_returns, rng=np.random.default_rng(999),
        )
        all_evals.append(ev_primary)
        print(f"  M_PRIMARY_UNFILTERED (pembanding M6): n={ev_primary.n_trades} exp={ev_primary.expectancy_net_bps:.2f}bps")

    print(f"\n{len(all_evals)} kandidat M dievaluasi. Menjalankan batch check...")
    apply_batch_checks(all_evals, n_trials_cumulative=len(all_evals) + 34 + 55, trial_sharpe_std=0.3)

    lines = ["# F7 -- Divisi M (ML & Meta-labeling)\n"]
    tree_note = (
        "M01 CatBoost, M02 XGBoost (monotone), M03 LightGBM DIUJI." if TREE_LIBS_AVAILABLE else
        "M01/M02/M03 (CatBoost/XGBoost/LightGBM) TIDAK diuji -- library tidak terpasang."
    )
    lines.append(
        f"XAUUSD, fitur kontinu (momentum/drift-burst/Mann-Kendall/realized-skew/sigma), target "
        f"return forward H60, CPCV purged+embargo (12 dari 66 path per model -- subset demi anggaran "
        f"komputasi, tetap purged+embargo, K-fold biasa TIDAK dipakai sesuai M1). SINGLE_ASSET_ONLY, "
        f"UNDERPOWERED_PANEL. M06/M07/M08 (Lasso/Ridge/ElasticNet) baseline wajib. {tree_note} "
        f"M11 meta-labeling primer = {best_f6_name} (net-expectancy terbaik dari F6_screening.md).\n"
    )

    positive_gross = [e for e in all_evals if e.expectancy_gross_bps > 0]

    lines.append("## Empat pertanyaan Anda\n")
    lines.append(f"**1. Berapa sinyal expectancy KOTORNYA positif?** {len(positive_gross)} dari {len(all_evals)} kandidat M.\n")
    if positive_gross:
        lines.append("| Kandidat | Expectancy kotor (bps) | N trade |")
        lines.append("|---|---:|---:|")
        for e in sorted(positive_gross, key=lambda x: -x.expectancy_gross_bps):
            lines.append(f"| {e.name} | {e.expectancy_gross_bps:.3f} | {e.n_trades} |")
        lines.append("")

    lines.append("**2. Berapa bps biaya harus turun supaya bersih positif?**\n")
    all_sorted = sorted(all_evals, key=lambda x: -x.expectancy_net_bps)
    best_overall = all_sorted[0] if all_sorted else None
    if best_overall and best_overall.expectancy_gross_bps > 0:
        drop_needed = COST_BPS_WORST - best_overall.breakeven_cost_bps
        lines.append(
            f"Kandidat terbaik keseluruhan ({best_overall.name}): expectancy kotor "
            f"{best_overall.expectancy_gross_bps:.3f} bps, breakeven cost = {best_overall.breakeven_cost_bps:.3f} bps. "
            f"Biaya saat ini {COST_BPS_WORST} bps proxy -> **perlu turun {drop_needed:.3f} bps** supaya net tepat impas."
        )
    elif best_overall:
        lines.append(
            f"**Tidak ada kandidat dengan expectancy kotor positif sama sekali** (terbaik: {best_overall.name}, "
            f"kotor {best_overall.expectancy_gross_bps:.3f} bps). Penurunan biaya berapa pun TIDAK AKAN membuatnya "
            f"positif -- masalahnya di sinyal/model, bukan di biaya."
        )
    lines.append("")

    lines.append("**3. Kandidat mana yang paling dekat lolos, kurang di centang mana?**\n")
    if all_evals:
        closest = max(all_evals, key=lambda x: x.n_checks_passed)
        checks_detail = {
            "expectancy>0": closest.expectancy_net_bps > 0, "t_stat>=3.0": closest.t_stat_eff_n >= 3.0,
            "beat_all_nulls": closest.beats_all_nulls, "cpcv>=80%": closest.cpcv_path_positive_pct >= 80,
            "bootstrap_ci95": closest.bootstrap_ci95_excludes_zero, "mc1>=p95": closest.mc1_percentile >= 95,
            "walkforward>=80%": closest.walkforward_sign_consistency_pct >= 80, "seed_stable": closest.seed_stable,
            "last_third_sig": closest.last_third_significant, "trades/yr>=300": closest.trades_per_year >= 300,
            "mc3": closest.mc3_pass, "mc5": closest.mc5_pass, "bh_fdr": closest.bh_fdr_pass,
            "dsr>=0.95": closest.dsr_pass, "pbo<=0.50": closest.pbo_pass,
        }
        missing = [k for k, v in checks_detail.items() if not v]
        passed_list = [k for k, v in checks_detail.items() if v]
        lines.append(f"**{closest.name}** -- {closest.n_checks_passed}/{closest.n_checks_total} centang.")
        lines.append(f"Lolos: {', '.join(passed_list) if passed_list else '(tidak ada)'}")
        lines.append(f"Kurang di: {', '.join(missing) if missing else '(tidak ada -- lolos semua)'}\n")

    lines.append("**4. t-stat tertinggi yang tercapai?**\n")
    if all_evals:
        best_t = max(all_evals, key=lambda x: x.t_stat_eff_n)
        t_val = best_t.t_stat_eff_n
        if t_val < 0:
            interp = "NEGATIF -- arah sinyal salah/tidak ada edge sama sekali di sisi ini, bukan soal sampel kurang."
        elif t_val < 2.0:
            interp = "sinyal LEMAH -- bahkan dengan sampel besar pun kemungkinan tidak akan cukup, ini masalah SINYAL, bukan masalah data."
        elif t_val < 3.0:
            interp = "sinyal ADA tapi SAMPEL KURANG -- t-stat mendekati ambang 3.0, perbesar panel/riwayat data bisa jadi cukup untuk menyeberang ambang, ini masalah DATA bukan masalah sinyal."
        else:
            interp = "SUDAH DI ATAS ambang 3.0 -- seharusnya lolos centang t-stat, cek centang lain yang menahannya."
        lines.append(f"**t = {t_val:.3f}** ({best_t.name}). Interpretasi: {interp}")
    lines.append("")

    passing = [e for e in all_evals if e.n_checks_passed >= 13]
    lines.append(f"## Ringkasan lengkap: {len(all_evals)} kandidat diuji, {len(passing)} lolos >=13/15 centang\n")
    lines.append("| Kandidat | N trade | Gross bps | Net bps | Breakeven cost bps | t-stat | Checks (dari 15) | DSR | PBO |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for e in all_sorted:
        lines.append(
            f"| {e.name} | {e.n_trades} | {e.expectancy_gross_bps:.2f} | {e.expectancy_net_bps:.2f} | "
            f"{e.breakeven_cost_bps:.2f} | {e.t_stat_eff_n:.2f} | {e.n_checks_passed}/{e.n_checks_total} | "
            f"{e.dsr:.3f} | {e.pbo if e.pbo is not None else float('nan'):.3f} |"
        )

    lines.append(f"\n## Vonis F7\n")
    if passing:
        best = max(passing, key=lambda x: x.n_checks_passed)
        lines.append(f"**Ada kandidat yang lolos ambang tinggi.** Terbaik: {best.name}.")
    else:
        lines.append("**NOL kandidat lolos >=13/15 checks.**")

    m11_evals = [e for e in all_evals if e.name.startswith("M11")]
    primary_eval = next((e for e in all_evals if e.name.startswith("M_PRIMARY")), None)
    if m11_evals and primary_eval:
        best_m11 = max(m11_evals, key=lambda x: x.expectancy_net_bps)
        lines.append(
            f"\nAturan M6/prioritas M11: meta-labeling terbaik ({best_m11.name}, "
            f"{best_m11.expectancy_net_bps:.2f}bps) vs primer polos ({primary_eval.expectancy_net_bps:.2f}bps) -- "
            f"{'meta-labeling MENGALAHKAN primer' if best_m11.expectancy_net_bps > primary_eval.expectancy_net_bps else 'primer polos TETAP lebih baik, meta-labeling TIDAK membantu di sini'}."
        )

    if TREE_LIBS_AVAILABLE:
        tree_evals = [e for e in all_evals if e.name.startswith(("M01_", "M02_", "M03_"))]
        linear_evals = [e for e in all_evals if e.name.startswith(("M06_", "M07_", "M08_"))]
        if tree_evals and linear_evals:
            best_tree = max(tree_evals, key=lambda x: x.expectancy_net_bps)
            best_linear = max(linear_evals, key=lambda x: x.expectancy_net_bps)
            lines.append(
                f"\nAturan M6 (tree-ensemble vs baseline linear): tree terbaik ({best_tree.name}, "
                f"{best_tree.expectancy_net_bps:.2f}bps) vs linear terbaik ({best_linear.name}, "
                f"{best_linear.expectancy_net_bps:.2f}bps) -- "
                f"{'tree MENGALAHKAN linear' if best_tree.expectancy_net_bps > best_linear.expectancy_net_bps else 'linear TETAP lebih baik, tree-ensemble TIDAK membantu di sini, wajib gagal per aturan M6'}."
            )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "F7_meta_ml.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0 if passing else 1


if __name__ == "__main__":
    sys.exit(main())
