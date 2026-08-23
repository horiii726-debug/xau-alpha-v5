#!/usr/bin/env python3
"""V7.1 LANGKAH 3 -- ulang LOMBA 4 (entry) di XAUUSD H1 2003-2026, dengan
gerbang G1-G4 WAJIB di DEPAN peringkat (bukan uji belakangan). Biaya TETAP
dikalibrasi dari tick 2021-2026 yang sudah ada. HOLDOUT (15% terakhir) tidak
disentuh.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m1, measure_cost_bps, FIG_DIR, REPORTS
from gates_g1g4 import run_all_gates

warnings.filterwarnings("ignore")

BARS_H1 = Path("/workspace/data/bars_h1/XAUUSD_H1.parquet")
LATIH_FRAC = 0.60
UJI_FRAC = 0.25
TAU_GRID = [1.0, 1.5]
H_GRID_H1 = {"6h": 6, "1d": 24, "5d": 120}  # bar H1


def rolling_z(x: pd.Series, window: int) -> pd.Series:
    m = x.rolling(window).mean()
    s = x.rolling(window).std()
    return (x - m) / s.replace(0, np.nan)


def mad_z(x: pd.Series, window: int) -> pd.Series:
    med = x.rolling(window).median()
    mad = (x - med).abs().rolling(window).median()
    return 0.6745 * (x - med) / mad.replace(0, np.nan)


def build_signals_h1(h1: pd.DataFrame) -> pd.DataFrame:
    mid = h1["mid_close"]
    ret1 = np.log(mid).diff()
    sigma = ret1.rolling(96).std()  # ~4 hari

    df = pd.DataFrame(index=h1.index)
    df["MAD-Zscore-momentum"] = mad_z(mid, 48)
    mom = (mid - mid.shift(24)) / (sigma * np.sqrt(24))
    df["Momentum-VolScaled"] = mom
    df["ShortHorizon-Reversal"] = -mom
    roll_max = mid.shift(1).rolling(48).max()
    roll_min = mid.shift(1).rolling(48).min()
    roll_mid = (roll_max + roll_min) / 2
    roll_range = (roll_max - roll_min).replace(0, np.nan)
    orb = (mid - roll_mid) / roll_range * 2
    df["ORB"] = rolling_z(orb, 48)
    mu_hat = ret1.rolling(12).mean()
    sigma_hat = ret1.rolling(12).std()
    df["DriftBurst-tstat"] = np.sqrt(12) * mu_hat / sigma_hat.replace(0, np.nan)
    z1 = (ret1 - ret1.rolling(200).mean()) / ret1.rolling(200).std().replace(0, np.nan)
    cusum_pos = np.zeros(len(df)); cusum_neg = np.zeros(len(df))
    z1v = z1.fillna(0).values
    for i in range(1, len(z1v)):
        cusum_pos[i] = max(0.0, cusum_pos[i-1] + z1v[i] - 0.5)
        cusum_neg[i] = min(0.0, cusum_neg[i-1] + z1v[i] + 0.5)
    cusum_stat = np.where(cusum_pos > 5.0, cusum_pos, np.where(cusum_neg < -5.0, cusum_neg, 0.0))
    df["CUSUM"] = rolling_z(pd.Series(cusum_stat, index=df.index), 200)
    return df


def main():
    h1 = pd.read_parquet(BARS_H1)
    n_total = len(h1)
    latih_end = int(n_total * LATIH_FRAC)
    uji_end = int(n_total * (LATIH_FRAC + UJI_FRAC))
    latih_uji_mask = np.zeros(n_total, dtype=bool)
    latih_uji_mask[:uji_end] = True
    print(f"H1 total={n_total:,} bar. LATIH+UJI (dipakai)={uji_end:,} bar "
          f"({h1['bar_time'].iloc[0]} s/d {h1['bar_time'].iloc[uji_end-1]}). "
          f"HOLDOUT (tidak disentuh)={n_total-uji_end:,} bar.")

    m1 = load_m1()
    m1_train_mask = np.zeros(len(m1), dtype=bool)
    m1_train_mask[: int(len(m1) * 0.70)] = True
    cost_info = measure_cost_bps(m1, m1_train_mask)
    cost_bps = cost_info["round_trip_cost_bps"]
    print(f"Biaya (tetap dari tick 2021-2026): {cost_bps:.3f}bps")

    signals = build_signals_h1(h1)
    mid = h1["mid_close"].values
    logp = np.log(mid)
    bar_time = h1["bar_time"].values

    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))
    roll_mean_60d = day_ret.rolling(60 * 24, min_periods=24 * 10).mean()
    demeaned_logp = np.cumsum((day_ret - roll_mean_60d.fillna(0)).values)

    regime_bounds = [
        ("2003-2011 bull", np.datetime64("2003-01-01"), np.datetime64("2012-01-01")),
        ("2012-2015 BEAR", np.datetime64("2012-01-01"), np.datetime64("2016-01-01")),
        ("2016-cutoff mixed", np.datetime64("2016-01-01"), h1["bar_time"].iloc[uji_end - 1].to_datetime64()),
    ]
    print("Blok rezim:", [(r[0]) for r in regime_bounds])

    report = ["# V7.1 LANGKAH 3 -- Lomba 4 (Entry) diulang di XAUUSD H1 2003-2026, gerbang G1-G4 di DEPAN\n",
              f"H1 total={n_total:,} bar. LATIH+UJI dipakai={uji_end:,} bar "
              f"({h1['bar_time'].iloc[0]} s/d {h1['bar_time'].iloc[uji_end-1]}). HOLDOUT (15% terakhir) "
              f"tidak disentuh. Biaya (tetap dari tick 2021-2026): **{cost_bps:.3f}bps**.\n",
              f"Blok rezim G3: {regime_bounds[0][0]}, {regime_bounds[1][0]}, {regime_bounds[2][0]}.\n"]

    all_gate_results = {}
    survivors = []
    for hname, H in H_GRID_H1.items():
        fwd = (np.roll(logp, -H) - logp) * 1e4
        fwd[-H:] = np.nan
        fwd_demeaned = (np.roll(demeaned_logp, -H) - demeaned_logp) * 1e4
        fwd_demeaned[-H:] = np.nan

        for tau in TAU_GRID:
            for name in signals.columns:
                z = signals[name].values
                take = (np.abs(z) >= tau) & latih_uji_mask & np.isfinite(fwd)
                n = int(take.sum())
                if n < 100:
                    continue
                direction = np.sign(z)[take]
                gross = direction * fwd[take]
                net = gross - cost_bps
                net_demeaned = direction * fwd_demeaned[take] - cost_bps
                entry_idx = np.where(take)[0]
                entry_bt = bar_time[take]

                gates = run_all_gates(direction, net, net_demeaned, entry_bt, entry_idx, uji_end, regime_bounds)
                key = (hname, tau, name)
                all_gate_results[key] = gates
                status = "LOLOS SEMUA" if gates["overall_pass"] else f"GAGAL di {gates['stopped_at']}"
                print(f"[{hname} tau={tau}] {name}: n={n}, {status}")
                if gates["overall_pass"]:
                    survivors.append({"horizon": hname, "tau": tau, "peserta": name, "n_trades": n,
                                       "expectancy_net_bps": float(net.mean())})

    report.append(f"\n## Ringkasan: {len(survivors)} kombinasi (horizon,tau,peserta) LOLOS G1-G4 dari "
                   f"{len(all_gate_results)} yang diuji\n")

    if survivors:
        surv_df = pd.DataFrame(survivors).sort_values("expectancy_net_bps", ascending=False)
        report.append(surv_df.round(4).to_markdown(index=False))
        print(f"\n{'='*60}\n{len(survivors)} SURVIVOR:\n{surv_df.to_string(index=False)}\n{'='*60}")
    else:
        report.append("\n**NOL survivor.** Tidak ada kombinasi (horizon, tau, peserta) yang lolos "
                       "G1-G4 di data 23-tahun. Detail kegagalan tiap kombinasi di bawah.\n")
        print(f"\n{'='*60}\nNOL SURVIVOR dari {len(all_gate_results)} kombinasi diuji\n{'='*60}")

    # detail kegagalan per gerbang (ringkas: hitung di gerbang mana tiap kombinasi berhenti)
    stop_counts = {}
    for key, g in all_gate_results.items():
        stop_counts[g["stopped_at"] or "LOLOS"] = stop_counts.get(g["stopped_at"] or "LOLOS", 0) + 1
    report.append(f"\n## Di gerbang mana kombinasi paling banyak gugur\n\n"
                   + "\n".join(f"- {k}: {v} kombinasi" for k, v in sorted(stop_counts.items(), key=lambda x: -x[1])))
    print("\nDistribusi gerbang gugur:", stop_counts)

    # contoh detail G1 untuk kombinasi CUSUM H=1d tau=1.5 (pembanding vs sebelumnya)
    cusum_key = ("1d", 1.5, "CUSUM")
    if cusum_key in all_gate_results:
        g = all_gate_results[cusum_key]
        report.append(f"\n## Detail CUSUM @H=1d tau=1.5 (pembanding vs temuan sebelumnya di data 2021-2026)\n\n"
                       f"G1 simetri: {g['g1']}\n")

    (REPORTS / "L3_LOMBA4_H1.md").write_text("\n".join(report))

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = list(stop_counts.keys())
    values = [stop_counts[k] for k in labels]
    colors = ["#2ca02c" if k == "LOLOS" else "#d62728" for k in labels]
    ax.bar(labels, values, color=colors)
    ax.set_title(f"L3 Lomba 4 (H1, 2003-2026): {len(survivors)}/{len(all_gate_results)} kombinasi lolos G1-G4")
    ax.set_ylabel("jumlah kombinasi (horizon x tau x peserta)")
    plt.tight_layout()
    out_png = FIG_DIR / "l3_lomba4_h1_gates.png"
    plt.savefig(out_png, dpi=120)
    print(f"saved {out_png}")

    return len(survivors) > 0


if __name__ == "__main__":
    passed = main()
    sys.exit(0 if passed else 1)
