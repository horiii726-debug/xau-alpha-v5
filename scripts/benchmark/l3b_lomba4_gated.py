#!/usr/bin/env python3
"""L3 -- ulang LOMBA 4 (entry) di data M5 2021-2026 (yang tersedia), HANYA
horizon yang lolos L2b (H4, D1), gerbang G1-G4 di depan.

KETERBATASAN DICATAT: data 2021-2026 TIDAK punya bear market nyata (unduhan
2012+ terblokir 429 persisten Dukascopy, dilanjutkan dengan data tersedia atas
instruksi user). G3 di sini memakai 3 blok KRONOLOGIS (bukan bull/bear/sideways
yang sebenarnya) sebagai pengganti sementara -- dicatat eksplisit sebagai
keterbatasan, bukan gerbang rezim yang dimaksud aslinya.
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
from common import load_m5, load_m1, measure_cost_bps, FIG_DIR, REPORTS
from gates_g1g4 import run_all_gates
from lomba4_entry import build_signals

warnings.filterwarnings("ignore")

LATIH_FRAC = 0.60
UJI_FRAC = 0.25
TAU_GRID = [1.0, 1.5]
H_GRID_GATED = {"H4": 48, "D1": 288}  # bar M5, hanya yang lolos L2b


def main():
    m5 = load_m5()
    n_total = len(m5)
    latih_end = int(n_total * LATIH_FRAC)
    uji_end = int(n_total * (LATIH_FRAC + UJI_FRAC))
    latih_uji_mask = np.zeros(n_total, dtype=bool)
    latih_uji_mask[:uji_end] = True
    bar_time = m5["bar_time"].values

    m1 = load_m1()
    m1_train_mask = np.zeros(len(m1), dtype=bool)
    m1_train_mask[: int(len(m1) * 0.70)] = True
    cost_bps = measure_cost_bps(m1, m1_train_mask)["round_trip_cost_bps"]

    signals = build_signals(m5)
    mid = m5["mid_close"].values
    logp = np.log(mid)

    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))
    roll_mean_60d = day_ret.rolling(60 * 288, min_periods=288 * 10).mean()
    demeaned_logp = np.cumsum((day_ret - roll_mean_60d.fillna(0)).values)

    # KETERBATASAN: bukan blok rezim bull/bear/sideways asli -- 3 blok
    # kronologis dari data yang tersedia (2021-2026, didominasi bull).
    t0 = pd.Timestamp(bar_time[0])
    t_uji_end = pd.Timestamp(bar_time[uji_end - 1])
    span = (t_uji_end - t0) / 3
    regime_bounds = [
        (f"blok-1 ({t0.date()} s/d {(t0+span).date()})", np.datetime64(t0), np.datetime64(t0 + span)),
        (f"blok-2 ({(t0+span).date()} s/d {(t0+2*span).date()})", np.datetime64(t0 + span), np.datetime64(t0 + 2 * span)),
        (f"blok-3 ({(t0+2*span).date()} s/d {t_uji_end.date()})", np.datetime64(t0 + 2 * span), np.datetime64(t_uji_end)),
    ]

    report = ["# L3 -- Lomba 4 (Entry) diulang, gerbang G1-G4 di depan, HANYA horizon lolos L2b (H4, D1)\n",
              "**Keterbatasan dicatat secara eksplisit:** data 2021-2026 (unduhan 2012+ terblokir 429 "
              "persisten Dukascopy) TIDAK memuat bear market nyata. G3 di sini memakai 3 blok KRONOLOGIS "
              "dari data yang ada, BUKAN blok bull/bear/sideways yang jadi tujuan asli perluasan data. "
              "Hasil G3 di sini harus dibaca sebagai 'stabil sepanjang 5 tahun bull', bukan 'stabil lintas "
              "rezim harga berbeda'.\n",
              f"Biaya (dari tick, jam aktif): {cost_bps:.3f}bps. Blok G3: " +
              ", ".join(r[0] for r in regime_bounds) + "\n"]

    all_results = {}
    survivors = []
    for hname, H in H_GRID_GATED.items():
        fwd = (np.roll(logp, -H) - logp) * 1e4
        fwd[-H:] = np.nan
        fwd_demeaned = (np.roll(demeaned_logp, -H) - demeaned_logp) * 1e4
        fwd_demeaned[-H:] = np.nan

        for tau in TAU_GRID:
            for name in signals.columns:
                z = signals[name].values
                take = (np.abs(z) >= tau) & latih_uji_mask & np.isfinite(fwd)
                n = int(take.sum())
                if n < 50:
                    continue
                direction = np.sign(z)[take]
                gross = direction * fwd[take]
                net = gross - cost_bps
                net_demeaned = direction * fwd_demeaned[take] - cost_bps
                entry_idx = np.where(take)[0]
                entry_bt = bar_time[take]

                gates = run_all_gates(direction, net, net_demeaned, entry_bt, entry_idx, uji_end, regime_bounds)
                key = (hname, tau, name)
                all_results[key] = gates
                status = "LOLOS SEMUA" if gates["overall_pass"] else f"GAGAL di {gates['stopped_at']}"
                print(f"[{hname} tau={tau}] {name}: n={n}, {status}")
                if gates["overall_pass"]:
                    survivors.append({"horizon": hname, "tau": tau, "peserta": name, "n_trades": n,
                                       "expectancy_net_bps": float(net.mean())})

    report.append(f"\n## Ringkasan: {len(survivors)} kombinasi lolos G1-G4 dari {len(all_results)} diuji\n")
    if survivors:
        surv_df = pd.DataFrame(survivors).sort_values("expectancy_net_bps", ascending=False)
        report.append(surv_df.round(4).to_markdown(index=False))
        print(f"\nSURVIVOR:\n{surv_df.to_string(index=False)}")
    else:
        report.append("\n**NOL survivor.**\n")
        print("\nNOL SURVIVOR")

    stop_counts = {}
    for key, g in all_results.items():
        stop_counts[g["stopped_at"] or "LOLOS"] = stop_counts.get(g["stopped_at"] or "LOLOS", 0) + 1
    report.append("\n## Gerbang gugur\n\n" + "\n".join(f"- {k}: {v}" for k, v in sorted(stop_counts.items(), key=lambda x: -x[1])))
    print("Distribusi gerbang gugur:", stop_counts)

    (REPORTS / "L3_LOMBA4_GATED.md").write_text("\n".join(report))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    labels = list(stop_counts.keys())
    values = [stop_counts[k] for k in labels]
    colors = ["#2ca02c" if k == "LOLOS" else "#d62728" for k in labels]
    ax.bar(labels, values, color=colors)
    ax.set_title(f"L3 Lomba 4 (H4+D1, 2021-2026): {len(survivors)}/{len(all_results)} lolos G1-G4")
    ax.set_ylabel("jumlah kombinasi")
    plt.tight_layout()
    out_png = FIG_DIR / "l3_lomba4_gated.png"
    plt.savefig(out_png, dpi=120)
    print(f"saved {out_png}")

    return survivors, all_results


if __name__ == "__main__":
    survivors, _ = main()
    sys.exit(0 if survivors else 1)
