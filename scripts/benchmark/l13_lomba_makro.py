#!/usr/bin/env python3
"""L13 -- LOMBA MAKRO. Horizon D1 saja (satu-satunya lolos kappa di L2b).
7 formula makro (real yield, DXY, breakeven, COT), gerbang G1-G5 di DEPAN,
sama persis dengan L3 (G1 sekarang pada return DEMEANED, koreksi L11).
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m1, measure_cost_bps, bootstrap_pvalue, REPORTS, FIG_DIR
from src.stats.effective_n import effective_n as ldp_effective_n
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

LATIH_FRAC = 0.60
UJI_FRAC = 0.25
TAU_GRID = [1.0, 1.5]


def load_xau_d1():
    h1 = pd.read_parquet("/workspace/data/bars_h1/XAUUSD_H1.parquet")
    h1["date"] = h1["bar_time"].dt.date
    d1 = h1.groupby("date").agg(mid_close=("mid_close", "last")).reset_index()
    d1["date"] = pd.to_datetime(d1["date"])
    return d1.sort_values("date").reset_index(drop=True)


def load_macro():
    fred = pd.read_parquet("/workspace/data/macro/fred_daily.parquet")
    cot = pd.read_parquet("/workspace/data/macro/cot_gold.parquet")
    return fred, cot


def build_macro_features(d1: pd.DataFrame, fred: pd.DataFrame, cot: pd.DataFrame) -> pd.DataFrame:
    """Semua fitur di-LAG 1 HARI PENUH: nilai dipakai di keputusan hari t
    adalah observasi FRED/COT paling akhir yang tersedia SEBELUM t (as-of merge,
    lalu digeser 1 hari lagi untuk margin aman rilis sore/malam)."""
    df = d1.copy()
    df["date"] = pd.to_datetime(df["date"]).astype("datetime64[ns]")
    fred_lag = fred.copy()
    fred_lag["date"] = (pd.to_datetime(fred_lag["date"]) + pd.Timedelta(days=1)).astype("datetime64[ns]")
    df = pd.merge_asof(df.sort_values("date"), fred_lag.sort_values("date"), on="date", direction="backward")

    cot_lag = cot.copy()
    cot_lag["date"] = (pd.to_datetime(cot_lag["date"]) + pd.Timedelta(days=1)).astype("datetime64[ns]")
    df = pd.merge_asof(df.sort_values("date"), cot_lag[["date", "net_noncomm"]].sort_values("date"),
                        on="date", direction="backward")

    df["d_realyield_5d"] = df["DFII10"].diff(5)
    df["d_dxy_5d"] = df["DTWEXBGS"].diff(5)
    df["d_breakeven_5d"] = df["T10YIE"].diff(5)
    df["gold_ret_1d"] = np.log(df["mid_close"]).diff()
    df["z_cot"] = (df["net_noncomm"] - df["net_noncomm"].rolling(52).mean()) / df["net_noncomm"].rolling(52).std()
    return df


def zscore(x: pd.Series, window: int = 252) -> pd.Series:
    m = x.rolling(window, min_periods=60).mean()
    s = x.rolling(window, min_periods=60).std()
    return (x - m) / s.replace(0, np.nan)


def build_signals(df: pd.DataFrame, latih_end: int) -> pd.DataFrame:
    """SEMUA kolom keluaran adalah nilai KONTINU (bukan +-1 biner) di mana
    sign()=arah dan |nilai|=kekuatan -- supaya ambang tau punya arti (bukan
    tau diterapkan ke z-score dari sinyal yang sudah biner, yang mustahil
    dilewati di tau tinggi). MAC01 dan MAC02 secara struktur jadi identik
    (dua-duanya = -z(d_realyield_5d)) -- dicatat eksplisit, sama seperti
    kasus OLS di Lomba 2 sebelumnya, bukan disembunyikan."""
    sig = pd.DataFrame(index=df.index)
    sig["MAC01_realyield"] = -zscore(df["d_realyield_5d"])
    sig["MAC02_realyield_z"] = -zscore(df["d_realyield_5d"])
    sig["MAC03_dxy"] = -zscore(df["d_dxy_5d"])

    # MAC04: residual emas setelah regresi pada d_realyield + d_dxy (fit LATIH saja), mean-revert
    from sklearn.linear_model import LinearRegression
    X_full = df[["d_realyield_5d", "d_dxy_5d"]].fillna(0).values
    y_full = df["gold_ret_1d"].fillna(0).values
    valid = df[["d_realyield_5d", "d_dxy_5d", "gold_ret_1d"]].notna().all(axis=1).values
    train_fit = valid.copy()
    train_fit[latih_end:] = False
    lr = LinearRegression().fit(X_full[train_fit], y_full[train_fit])
    resid = y_full - lr.predict(X_full)
    resid_s = pd.Series(resid, index=df.index)
    resid_s[~valid] = np.nan
    sig["MAC04_residual_meanrevert"] = -zscore(resid_s, window=60)

    sig["MAC05_cot_crowding"] = -df["z_cot"]  # crowding tinggi -> kontrarian (reversal)
    # MAC06: kontinu = z(breakeven naik) - z(realyield naik) -- positif saat
    # breakeven naik DAN realyield turun (inflasi tanpa hawkish), arah dari sign()
    z_be = zscore(df["d_breakeven_5d"])
    z_ry = zscore(df["d_realyield_5d"])
    sig["MAC06_infl_no_hawkish"] = z_be - z_ry

    # MAC07: Ridge(MAC01_raw z, MAC03_raw z) -> kombinasi, fit LATIH saja
    z1 = zscore(df["d_realyield_5d"]).fillna(0).values.reshape(-1, 1)
    z3 = zscore(df["d_dxy_5d"]).fillna(0).values.reshape(-1, 1)
    X7 = np.hstack([z1, z3])
    y7 = df["gold_ret_1d"].shift(-1).fillna(0).values  # target 1-hari ke depan
    valid7 = np.isfinite(X7).all(axis=1) & np.isfinite(y7)
    train7 = valid7.copy(); train7[latih_end:] = False
    ridge = Ridge(alpha=1.0).fit(X7[train7], y7[train7])
    combo = ridge.predict(X7)
    combo_s = pd.Series(combo, index=df.index)
    combo_s[~valid7] = np.nan
    sig["MAC07_ridge_combo"] = zscore(combo_s, window=252)

    return sig


def main():
    d1 = load_xau_d1()
    fred, cot = load_macro()
    df = build_macro_features(d1, fred, cot)
    n_total = len(df)
    latih_end = int(n_total * LATIH_FRAC)
    uji_end = int(n_total * (LATIH_FRAC + UJI_FRAC))
    print(f"D1 total={n_total:,} hari ({df['date'].iloc[0].date()} s/d {df['date'].iloc[uji_end-1].date()}), "
          f"LATIH+UJI={uji_end:,}. HOLDOUT (15% terakhir) tidak disentuh.")

    m1 = load_m1()
    m1_mask = np.zeros(len(m1), dtype=bool); m1_mask[: int(len(m1) * 0.70)] = True
    cost_info = measure_cost_bps(m1, m1_mask)
    cost_base = cost_info["round_trip_cost_bps"]
    spread_p90 = m1.loc[m1_mask, "spread_bps"].dropna().pipe(lambda s: s[(s > 0) & (s < 500)]).quantile(0.90)
    cost_worst = spread_p90 * 2.5 + 0.28  # spread_p90*(1+1.5) + komisi, formula sama seperti sebelumnya
    print(f"Biaya base={cost_base:.3f}bps, biaya worst={cost_worst:.3f}bps")

    signals = build_signals(df, latih_end)
    logp = np.log(df["mid_close"].values)
    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))
    roll_mean_60d = day_ret.rolling(60, min_periods=15).mean()
    demeaned_logp = np.cumsum((day_ret - roll_mean_60d.fillna(0)).values)

    fwd_bps = (np.roll(logp, -1) - logp) * 1e4; fwd_bps[-1] = np.nan
    fwd_bps_demeaned = (np.roll(demeaned_logp, -1) - demeaned_logp) * 1e4; fwd_bps_demeaned[-1] = np.nan

    bar_time = df["date"].values
    regime_bounds = [
        ("2003-2011 bull", np.datetime64("2003-01-01"), np.datetime64("2012-01-01")),
        ("2012-2015 BEAR", np.datetime64("2012-01-01"), np.datetime64("2016-01-01")),
        ("2016-cutoff", np.datetime64("2016-01-01"), pd.Timestamp(df["date"].iloc[uji_end-1]).to_datetime64()),
    ]
    latih_uji_mask = np.zeros(n_total, dtype=bool); latih_uji_mask[:uji_end] = True

    def check_g1(direction, net_d):
        l, s = direction > 0, direction < 0
        pl = net_d[l].sum() if l.any() else np.nan
        ps = net_d[s].sum() if s.any() else np.nan
        return (pl > 0) and (ps > 0), pl, ps

    def check_g3(direction, net, entry_bt):
        res = []
        for name, s0, s1 in regime_bounds:
            m = (entry_bt >= s0) & (entry_bt < s1)
            n = int(m.sum())
            exp = float(net[m].mean()) if n >= 10 else np.nan
            res.append((name, n, exp))
        npos = sum(1 for _, n, e in res if pd.notna(e) and e > 0)
        return npos >= 2, res

    def check_g4(net, entry_idx, n_windows=10):
        edges = np.linspace(0, uji_end, n_windows + 1).astype(int)
        wf = []
        for w in range(n_windows):
            lo, hi = edges[w], edges[w+1]
            m = (entry_idx >= lo) & (entry_idx < hi)
            n = int(m.sum())
            exp = float(net[m].mean()) if n >= 5 else np.nan
            pnl = float(net[m].sum()) if n >= 5 else 0.0
            wf.append((w+1, n, exp, pnl))
        npos = sum(1 for _, n, e, p in wf if pd.notna(e) and e > 0)
        total_pnl = sum(p for _, n, e, p in wf)
        top2 = sorted(wf, key=lambda x: -abs(x[3]))[:2]
        top2_share = sum(x[3] for x in top2) / total_pnl if total_pnl != 0 else np.nan
        passed = npos >= 7 and pd.notna(top2_share) and abs(top2_share) <= 0.60
        return passed, npos, top2_share, wf

    rows = []
    survivors = []
    for tau in TAU_GRID:
        for name in signals.columns:
            z = signals[name].values
            take = (np.abs(z) >= tau) & latih_uji_mask & np.isfinite(fwd_bps) & np.isfinite(z)
            n = int(take.sum())
            if n < 30:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "n<30"})
                continue
            direction = np.sign(z)[take]
            net_base = direction * fwd_bps[take] - cost_base
            net_demeaned = direction * fwd_bps_demeaned[take] - cost_base
            net_worst = direction * fwd_bps[take] - cost_worst
            entry_idx = np.where(take)[0]
            entry_bt = bar_time[take]

            g1, pl, ps = check_g1(direction, net_demeaned)
            if not g1:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "G1",
                              "pnl_long_demean": pl, "pnl_short_demean": ps})
                continue
            g2 = float(net_worst.mean()) > 0
            if not g2:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "G2",
                              "expectancy_worst": float(net_worst.mean())})
                continue
            g3, g3_detail = check_g3(direction, net_base, entry_bt)
            if not g3:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "G3", "g3_detail": g3_detail})
                continue
            g4, g4_npos, g4_top2, g4_detail = check_g4(net_base, entry_idx)
            if not g4:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "G4",
                              "wf_positive": g4_npos, "wf_top2_share": g4_top2})
                continue
            starts = entry_idx; ends = np.minimum(entry_idx + 1, n_total)
            eff_n = ldp_effective_n(starts, ends, n_total)
            se = net_base.std(ddof=1) / np.sqrt(max(eff_n, 2))
            t_stat = net_base.mean() / se if se > 0 else 0.0
            g5 = t_stat >= 3.0
            if not g5:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "G5",
                              "eff_n": eff_n, "t_stat": t_stat})
                continue
            rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "LOLOS",
                          "expectancy_base_bps": float(net_base.mean()), "eff_n": eff_n, "t_stat": t_stat})
            survivors.append({"peserta": name, "tau": tau, "n": n,
                               "expectancy_base_bps": float(net_base.mean()), "t_stat_effn": t_stat})
            print(f"tau={tau} {name}: LOLOS SEMUA G1-G5! t={t_stat:.2f} exp={net_base.mean():.3f}bps")

    for r in rows:
        print(f"tau={r['tau']} {r['peserta']}: n={r['n']}, stopped_at={r['stopped_at']}")

    # baseline buy-and-hold + random entry
    bh_ret = fwd_bps[latih_uji_mask & np.isfinite(fwd_bps)]
    bh_net = bh_ret - cost_base / len(bh_ret)  # biaya sekali di awal, diabaikan per-hari (BnH)
    rng = np.random.default_rng(0)
    rand_dir = rng.choice([-1.0, 1.0], size=len(bh_ret))
    rand_net = rand_dir * bh_ret - cost_base
    print(f"\nBaseline buy-and-hold: mean={bh_ret.mean():.3f}bps/hari, total={bh_ret.sum():.1f}bps")
    print(f"Baseline entry acak: mean={rand_net.mean():.3f}bps")

    stop_counts = {}
    for r in rows:
        stop_counts[r["stopped_at"]] = stop_counts.get(r["stopped_at"], 0) + 1
    print(f"\nDistribusi gerbang gugur: {stop_counts}")
    print(f"\nTOTAL SURVIVOR: {len(survivors)}/{len(rows)}")

    lines = ["# L13 -- LOMBA MAKRO (horizon D1, gerbang G1-G5 di depan)\n",
              f"D1={n_total:,} hari ({df['date'].iloc[0].date()} s/d {df['date'].iloc[uji_end-1].date()}), "
              f"LATIH+UJI dipakai={uji_end:,}. Biaya base={cost_base:.3f}bps, worst={cost_worst:.3f}bps. "
              f"Baseline buy-and-hold: {bh_ret.mean():.3f}bps/hari.\n",
              f"\n## Hasil per kombinasi (tau x peserta)\n"]
    rdf = pd.DataFrame(rows)
    lines.append(rdf.to_markdown(index=False))
    lines.append(f"\n## Distribusi gerbang gugur\n\n" + "\n".join(f"- {k}: {v}" for k, v in sorted(stop_counts.items(), key=lambda x: -x[1])))
    if survivors:
        lines.append(f"\n## SURVIVOR ({len(survivors)})\n\n" + pd.DataFrame(survivors).round(4).to_markdown(index=False))
    else:
        lines.append("\n## NOL SURVIVOR\n")
    (REPORTS / "L13_LOMBA_MAKRO.md").write_text("\n".join(lines))

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = list(stop_counts.keys()); values = [stop_counts[k] for k in labels]
    colors = ["#2ca02c" if k == "LOLOS" else "#d62728" for k in labels]
    ax.bar(labels, values, color=colors)
    ax.set_title(f"L13 Lomba Makro (D1, 2003-2026): {len(survivors)}/{len(rows)} lolos G1-G5")
    ax.set_ylabel("jumlah kombinasi")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "l13_lomba_makro.png", dpi=120)
    print(f"saved {FIG_DIR / 'l13_lomba_makro.png'}")

    return survivors


if __name__ == "__main__":
    s = main()
    sys.exit(0 if s else 1)
