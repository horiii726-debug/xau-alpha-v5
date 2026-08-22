#!/usr/bin/env python3
"""F7 -- Divisi M (ML & Meta-labeling).

M06/M07/M08 (Lasso/Ridge/ElasticNet) BASELINE WAJIB (aturan M6): model
lain harus mengalahkan ini. Validasi HANYA CPCV purged+embargo (M1) --
K-fold biasa DILARANG. Fitur: sekumpulan estimator CONTINU (bukan sudah
di-threshold) dari formula V/E yang sudah dihitung, memprediksi return
forward H60, lalu threshold prediksi jadi sinyal +1/-1/0, dievaluasi
lewat gate_checklist yang sama seperti F5/F6.

M11 meta-labeling (PRIORITAS TERTINGGI divisi M): primer = sinyal E
dengan expectancy terbaik dari F6 (meski tidak lolos ambang penuh --
"terbaik yang ada" tetap dipakai sebagai primer, sesuai instruksi jalan
terus), sekunder = classifier biner (regularized logistic) memprediksi
menang/kalah trade primer, threshold 0.5/0.6.
"""
import sys
sys.path.insert(0, "/workspace")

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

REPORTS_DIR = Path("/workspace/reports")
COST_BPS_WORST = 3.0
MAX_HOLD_BARS = 60
SIGMA_WINDOW = 96
BARS_PER_YEAR = 365 * 24 * 60
K_SL, K_TP = 1.5, 2.5


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

    def run_linear_model(name, model_fn, threshold_pctl=60):
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
        run_linear_model(f"M06_LASSO_a{alpha}", lambda a=alpha: models["M06_LASSO"](a))

    print("\n=== M07 RIDGE (baseline wajib) ===")
    for alpha in [0.01, 0.1, 1.0, 10.0]:
        run_linear_model(f"M07_RIDGE_a{alpha}", lambda a=alpha: models["M07_RIDGE"](a))

    print("\n=== M08 ELASTIC NET ===")
    for alpha in [0.01, 0.1, 1.0]:
        for l1r in [0.3, 0.7]:
            run_linear_model(f"M08_ELASTICNET_a{alpha}_l1{l1r}", lambda a=alpha, l=l1r: models["M08_ELASTIC_NET"](a, l))

    print("\n=== M11 Meta-labeling (prioritas tertinggi divisi M) ===")
    primary_signal = pf.e01_intraday_momentum(mid, 12)  # terbaik F6 pada expectancy (masih negatif, tapi 'terbaik yang ada')
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
            name="M_PRIMARY_UNFILTERED_E01_L12", trade_returns=res_primary.ret[primary_valid],
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
    lines.append(
        f"XAUUSD, fitur kontinu (momentum/drift-burst/Mann-Kendall/realized-skew/sigma), target "
        f"return forward H60, CPCV purged+embargo (12 dari 66 path per model -- subset demi anggaran "
        f"komputasi, tetap purged+embargo, K-fold biasa TIDAK dipakai sesuai M1). SINGLE_ASSET_ONLY, "
        f"UNDERPOWERED_PANEL. Model tree-ensemble (M01-M05,M09,M10,CatBoost/XGBoost/LightGBM) TIDAK "
        f"diuji -- paket belum terpasang di lingkungan ini, di luar anggaran waktu untuk instalasi+uji.\n"
    )
    passing = [e for e in all_evals if e.n_checks_passed >= 13]
    lines.append(f"## Ringkasan: {len(all_evals)} kandidat diuji, {len(passing)} lolos >=13/15 centang\n")
    lines.append("| Kandidat | N trade | Expectancy net bps | t-stat | Checks (dari 15) | DSR |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for e in sorted(all_evals, key=lambda x: -x.expectancy_net_bps):
        lines.append(f"| {e.name} | {e.n_trades} | {e.expectancy_net_bps:.2f} | {e.t_stat_eff_n:.2f} | {e.n_checks_passed}/{e.n_checks_total} | {e.dsr:.3f} |")

    lines.append(f"\n## Vonis F7\n")
    if passing:
        best = max(passing, key=lambda x: x.n_checks_passed)
        lines.append(f"**Ada kandidat yang lolos ambang tinggi.** Terbaik: {best.name}.")
    else:
        lines.append("**NOL kandidat lolos >=13/15 checks.**")
        if all_evals:
            best_by_exp = max(all_evals, key=lambda x: x.expectancy_net_bps)
            lines.append(f"\nKandidat dengan expectancy tertinggi: {best_by_exp.name}, {best_by_exp.expectancy_net_bps:.2f} bps.")

        m11_evals = [e for e in all_evals if e.name.startswith("M11")]
        primary_eval = next((e for e in all_evals if e.name.startswith("M_PRIMARY")), None)
        if m11_evals and primary_eval:
            best_m11 = max(m11_evals, key=lambda x: x.expectancy_net_bps)
            lines.append(
                f"\nAturan M6/prioritas M11: meta-labeling terbaik ({best_m11.name}, "
                f"{best_m11.expectancy_net_bps:.2f}bps) vs primer polos ({primary_eval.expectancy_net_bps:.2f}bps) -- "
                f"{'meta-labeling MENGALAHKAN primer' if best_m11.expectancy_net_bps > primary_eval.expectancy_net_bps else 'primer polos TETAP lebih baik, meta-labeling TIDAK membantu di sini'}."
            )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "F7_meta_ml.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0 if passing else 1


if __name__ == "__main__":
    sys.exit(main())
