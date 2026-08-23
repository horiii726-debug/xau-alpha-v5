#!/usr/bin/env python3
"""PRIORITAS (sebelum Bagian A-E apapun dibangun): uji pembunuh D3.1 (drift
capture -- pisah PnL long vs short, plus arm DEMEANED) dan D3.3 (walk-forward
10 jendela) untuk CUSUM @ H=1d, tau=1.5 (juara Lomba 4).

Partisi v7: LATIH 60% / UJI 25% / HOLDOUT 15%. Uji ini jalan di LATIH+UJI
(85% pertama) -- HOLDOUT (15% terakhir) TIDAK disentuh, disimpan untuk uji
sistem utuh di Bagian D nanti (dibuka SEKALI).
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
from common import load_m5, load_m1, measure_cost_bps, bootstrap_pvalue, FIG_DIR, REPORTS
from lomba4_entry import build_signals, H_GRID

warnings.filterwarnings("ignore")

TAU_LOCKED = 1.5
H_M5 = H_GRID["1d"]

LATIH_FRAC = 0.60
UJI_FRAC = 0.25
# HOLDOUT_FRAC = 0.15 -- tidak disentuh di sini


def main():
    m5 = load_m5()
    m1 = load_m1()
    n_total = len(m5)
    latih_end = int(n_total * LATIH_FRAC)
    uji_end = int(n_total * (LATIH_FRAC + UJI_FRAC))
    # holdout = [uji_end:] -- TIDAK DISENTUH

    print(f"LATIH: 0..{latih_end} ({latih_end} bar) | UJI: {latih_end}..{uji_end} ({uji_end-latih_end} bar) | "
          f"HOLDOUT: {uji_end}..{n_total} ({n_total-uji_end} bar, TIDAK DISENTUH)")

    latih_uji_mask = np.zeros(n_total, dtype=bool)
    latih_uji_mask[:uji_end] = True  # 85% pertama, dipakai utk uji prioritas ini

    m1_train_mask = np.zeros(len(m1), dtype=bool)
    m1_latih_end = int(len(m1) * LATIH_FRAC)
    m1_train_mask[:m1_latih_end] = True
    cost_info = measure_cost_bps(m1, m1_train_mask)
    cost_bps = cost_info["round_trip_cost_bps"]

    signals = build_signals(m5)
    cusum_z = signals["CUSUM"].values
    mid = m5["mid_close"].values
    logp = np.log(mid)
    fwd_ret_bps_raw = (np.roll(logp, -H_M5) - logp) * 1e4
    fwd_ret_bps_raw[-H_M5:] = np.nan

    # arm DEMEANED: buang mean bergulir 60 hari (60*H_M5 bar M5) dari return
    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))
    roll_mean_60d = day_ret.rolling(60 * H_M5, min_periods=H_M5 * 5).mean()
    demeaned_logp = logp - np.cumsum(roll_mean_60d.fillna(0).values)
    fwd_ret_bps_demeaned = (np.roll(demeaned_logp, -H_M5) - demeaned_logp) * 1e4
    fwd_ret_bps_demeaned[-H_M5:] = np.nan

    take = (np.abs(cusum_z) >= TAU_LOCKED) & latih_uji_mask & np.isfinite(fwd_ret_bps_raw)
    direction = np.sign(cusum_z)

    report_lines = ["# D3 -- UJI PRIORITAS (drift capture + walk-forward), CUSUM @H=1d tau=1.5\n",
                     f"Dijalankan di LATIH+UJI (85% pertama, {uji_end:,} bar M5). HOLDOUT (15% terakhir, "
                     f"{n_total-uji_end:,} bar) **TIDAK disentuh**, disimpan untuk uji sistem utuh Bagian D.\n",
                     f"Biaya round-trip terukur (jam aktif, dari LATIH): **{cost_bps:.3f} bps**.\n"]

    # ============================= D3.1 DRIFT CAPTURE =============================
    print("\n=== D3.1 -- DRIFT CAPTURE (long vs short, raw & demeaned) ===")
    report_lines.append("## D3.1 -- Drift capture (pisah PnL long vs short)\n")

    rows = []
    for arm_name, fwd in [("RAW", fwd_ret_bps_raw), ("DEMEANED (buang mean 60hr bergulir)", fwd_ret_bps_demeaned)]:
        arm_take = take & np.isfinite(fwd)
        for side_name, side_mask in [("LONG", arm_take & (direction > 0)), ("SHORT", arm_take & (direction < 0)),
                                       ("GABUNGAN", arm_take)]:
            n = int(side_mask.sum())
            if n < 20:
                rows.append({"arm": arm_name, "sisi": side_name, "n_trades": n, "expectancy_net_bps": np.nan, "p_value": np.nan})
                continue
            dir_side = direction[side_mask] if side_name != "GABUNGAN" else direction[side_mask]
            gross = dir_side * fwd[side_mask]
            net = gross - cost_bps
            pval = bootstrap_pvalue(net)
            rows.append({"arm": arm_name, "sisi": side_name, "n_trades": n,
                         "expectancy_net_bps": float(net.mean()), "p_value": pval})

    drift_df = pd.DataFrame(rows)
    print(drift_df.to_string(index=False))
    report_lines.append(drift_df.round(4).to_markdown(index=False))

    raw_short = drift_df[(drift_df.arm == "RAW") & (drift_df.sisi == "SHORT")].iloc[0]
    raw_long = drift_df[(drift_df.arm == "RAW") & (drift_df.sisi == "LONG")].iloc[0]
    demeaned_short = drift_df[(drift_df.arm.str.contains("DEMEANED")) & (drift_df.sisi == "SHORT")].iloc[0]
    drift_capture_verdict = raw_short["expectancy_net_bps"] <= 0
    report_lines.append(
        f"\n**Verdict D3.1:** SHORT (raw) expectancy = {raw_short['expectancy_net_bps']:.3f}bps "
        f"(n={int(raw_short['n_trades'])}, p={raw_short['p_value']:.4f}). LONG (raw) = "
        f"{raw_long['expectancy_net_bps']:.3f}bps. SHORT (demeaned) = {demeaned_short['expectancy_net_bps']:.3f}bps.\n\n"
        f"{'**GAGAL -- SHORT <= 0, ini kemungkinan besar DRIFT CAPTURE (beta emas), BUKAN alpha murni.**' if drift_capture_verdict else '**LOLOS -- SHORT juga net-positif, bukan sekadar menumpang tren naik emas.**'}\n"
    )
    print(f"\nD3.1 VERDICT: {'GAGAL (drift capture)' if drift_capture_verdict else 'LOLOS'}")

    # ============================= D3.3 WALK-FORWARD =============================
    print("\n=== D3.3 -- WALK-FORWARD (10 jendela berurutan) ===")
    report_lines.append("\n## D3.3 -- Walk-forward (10 jendela berurutan, LATIH+UJI)\n")

    idx_range = np.arange(uji_end)
    window_edges = np.linspace(0, uji_end, 11).astype(int)
    wf_rows = []
    for w in range(10):
        lo, hi = window_edges[w], window_edges[w + 1]
        wmask = np.zeros(n_total, dtype=bool)
        wmask[lo:hi] = True
        wtake = take & wmask & np.isfinite(fwd_ret_bps_raw)
        n = int(wtake.sum())
        if n < 10:
            wf_rows.append({"jendela": w + 1, "bar_mulai": lo, "bar_akhir": hi, "n_trades": n, "expectancy_net_bps": np.nan})
            continue
        gross = direction[wtake] * fwd_ret_bps_raw[wtake]
        net = gross - cost_bps
        wf_rows.append({"jendela": w + 1, "bar_mulai": lo, "bar_akhir": hi, "n_trades": n,
                         "expectancy_net_bps": float(net.mean())})

    wf_df = pd.DataFrame(wf_rows)
    print(wf_df.to_string(index=False))
    report_lines.append(wf_df.round(4).to_markdown(index=False))

    n_positive = int((wf_df["expectancy_net_bps"] > 0).sum())
    wf_verdict_pass = n_positive >= 7
    report_lines.append(f"\n**Verdict D3.3:** {n_positive}/10 jendela positif (syarat >=7/10). "
                         f"{'**LOLOS**' if wf_verdict_pass else '**GAGAL**'}.\n")
    print(f"\nD3.3 VERDICT: {n_positive}/10 positif -- {'LOLOS' if wf_verdict_pass else 'GAGAL'}")

    # ============================= OVERALL =============================
    overall_pass = (not drift_capture_verdict) and wf_verdict_pass
    report_lines.append(f"\n## VERDICT KESELURUHAN (gerbang sebelum lanjut Bagian A-E)\n\n"
                         f"D3.1 (bukan drift capture): {'LOLOS' if not drift_capture_verdict else 'GAGAL'}  \n"
                         f"D3.3 (walk-forward >=7/10): {'LOLOS' if wf_verdict_pass else 'GAGAL'}  \n\n"
                         f"**{'LOLOS DUA-DUANYA -- LANJUT ke Bagian A-E.' if overall_pass else 'GAGAL SALAH SATU -- STOP, jangan lanjut ke Bagian A-E.'}**\n")
    print(f"\n{'='*60}\nOVERALL: {'LOLOS -- LANJUT' if overall_pass else 'GAGAL -- STOP'}\n{'='*60}")

    # ---- plot ----
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    ax = axes[0]
    plot_d = drift_df[drift_df.sisi != "GABUNGAN"]
    for i, arm in enumerate(plot_d.arm.unique()):
        sub = plot_d[plot_d.arm == arm]
        colors = ["#2ca02c" if v > 0 else "#d62728" for v in sub["expectancy_net_bps"]]
        ax.bar([f"{s}\n({arm[:6]})" for s in sub["sisi"]], sub["expectancy_net_bps"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("D3.1 -- Expectancy net: LONG vs SHORT")
    ax.set_ylabel("expectancy net (bps)")

    ax = axes[1]
    colors = ["#2ca02c" if v > 0 else "#d62728" for v in wf_df["expectancy_net_bps"].fillna(0)]
    ax.bar(wf_df["jendela"], wf_df["expectancy_net_bps"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(f"D3.3 -- Walk-forward 10 jendela ({n_positive}/10 positif)")
    ax.set_xlabel("jendela (kronologis)")
    ax.set_ylabel("expectancy net (bps)")

    plt.tight_layout()
    out_png = FIG_DIR / "d3_priority_tests.png"
    plt.savefig(out_png, dpi=120)
    print(f"saved {out_png}")

    (REPORTS / "D3_PRIORITY_TESTS.md").write_text("\n".join(report_lines))
    return overall_pass


if __name__ == "__main__":
    passed = main()
    sys.exit(0 if passed else 1)
