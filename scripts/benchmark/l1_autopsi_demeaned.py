#!/usr/bin/env python3
"""V7.1 LANGKAH 1 -- Autopsi arm DEMEANED long-only (CUSUM @H=1d tau=1.5).
4 uji, KEEMPAT harus lolos:
  1. Signifikansi dengan eff_N (Lopez de Prado uniqueness), t>=3.0
  2. Walk-forward 10 jendela pada arm demeaned long-only, >=7/10, tidak
     boleh terkonsentrasi di 2 jendela terakhir
  3. Permutasi blok 1000x -- observed harus > persentil 95 null
  4. Biaya worst (spread p90 jam aktif + komisi + slippage alpha=1.5) --
     expectancy harus > 0

Dijalankan di LATIH+UJI (85% pertama) -- HOLDOUT tetap tidak disentuh.
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
from common import load_m5, load_m1, bootstrap_pvalue, measure_cost_bps, FIG_DIR, REPORTS
from lomba4_entry import build_signals, H_GRID
from src.stats.effective_n import effective_n as ldp_effective_n

warnings.filterwarnings("ignore")

TAU_LOCKED = 1.5
H_M5 = H_GRID["1d"]
LATIH_FRAC = 0.60
UJI_FRAC = 0.25


def measure_cost_worst(m1: pd.DataFrame, train_mask: np.ndarray) -> dict:
    from common import active_hours_mask
    active = active_hours_mask(m1["ts"])
    sb = m1.loc[train_mask & active, "spread_bps"].dropna()
    sb = sb[(sb > 0) & (sb < 500)]
    spread_p90 = float(sb.quantile(0.90))
    komisi_bps = 2 * 0.0014 * 100
    slippage_bps = 1.5 * spread_p90
    total = spread_p90 + komisi_bps + slippage_bps
    return {"spread_p90_bps": spread_p90, "komisi_bps": komisi_bps,
            "slippage_bps": slippage_bps, "cost_worst_bps": total}


def main():
    m5 = load_m5()
    m1 = load_m1()
    n_total = len(m5)
    latih_end = int(n_total * LATIH_FRAC)
    uji_end = int(n_total * (LATIH_FRAC + UJI_FRAC))
    latih_uji_mask = np.zeros(n_total, dtype=bool)
    latih_uji_mask[:uji_end] = True

    m1_train_mask = np.zeros(len(m1), dtype=bool)
    m1_train_mask[: int(len(m1) * LATIH_FRAC)] = True

    signals = build_signals(m5)
    cusum_z = signals["CUSUM"].values
    mid = m5["mid_close"].values
    logp = np.log(mid)

    # demeaned price series (sama seperti d3_priority_tests.py)
    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))
    roll_mean_60d = day_ret.rolling(60 * H_M5, min_periods=H_M5 * 5).mean()
    demeaned_per_bar_ret = (day_ret - roll_mean_60d.fillna(0)).values
    demeaned_logp = np.cumsum(demeaned_per_bar_ret)
    fwd_ret_bps_demeaned = (np.roll(demeaned_logp, -H_M5) - demeaned_logp) * 1e4
    fwd_ret_bps_demeaned[-H_M5:] = np.nan

    direction = np.sign(cusum_z)
    take_long = (cusum_z >= TAU_LOCKED) & latih_uji_mask & np.isfinite(fwd_ret_bps_demeaned)
    entry_positions = np.where(take_long)[0]
    n_trades = len(entry_positions)
    print(f"Arm demeaned LONG-only: {n_trades} trade (LATIH+UJI, {uji_end:,} bar)")

    cost_info_base = measure_cost_bps(m1, m1_train_mask)
    cost_base_bps = cost_info_base["round_trip_cost_bps"]  # dipakai Uji 1-3 (sama seperti D3 sebelumnya)
    cost_worst_info = measure_cost_worst(m1, m1_train_mask)
    cost_worst = cost_worst_info["cost_worst_bps"]  # dipakai KHUSUS Uji 4
    print(f"Biaya BASE (dipakai Uji 1-3, sama seperti D3): {cost_base_bps:.3f}bps")
    print(f"Biaya WORST (dipakai KHUSUS Uji 4): spread_p90={cost_worst_info['spread_p90_bps']:.3f}bps + "
          f"komisi={cost_worst_info['komisi_bps']:.3f}bps + slippage(alpha1.5)={cost_worst_info['slippage_bps']:.3f}bps "
          f"= {cost_worst:.3f}bps")

    raw_gross = fwd_ret_bps_demeaned[entry_positions]  # direction always +1 (long-only)

    report = ["# V7.1 LANGKAH 1 -- Autopsi arm DEMEANED long-only (CUSUM @H=1d tau=1.5)\n",
              f"Arm demeaned LONG-only, {n_trades} trade, dijalankan di LATIH+UJI (85% pertama, "
              f"{uji_end:,} bar M5). Biaya BASE (Uji 1-3, sama seperti D3 sebelumnya): "
              f"**{cost_base_bps:.3f}bps**. Biaya WORST (khusus Uji 4): spread_p90(jam aktif)="
              f"{cost_worst_info['spread_p90_bps']:.3f}bps + komisi={cost_worst_info['komisi_bps']:.3f}bps + "
              f"slippage(alpha=1.5)={cost_worst_info['slippage_bps']:.3f}bps = **{cost_worst:.3f}bps**.\n"]

    # ============ UJI 1: signifikansi dengan eff_N ============
    print("\n=== UJI 1 -- Signifikansi dengan eff_N (Lopez de Prado) ===")
    starts = entry_positions
    ends = np.minimum(entry_positions + H_M5, n_total)
    eff_n = ldp_effective_n(starts, ends, n_total)
    net_base = raw_gross - cost_base_bps
    mean_net = net_base.mean()
    se = net_base.std(ddof=1) / np.sqrt(eff_n)
    t_stat_effn = mean_net / se if se > 0 else 0.0
    from scipy import stats as scipy_stats
    p_value_t = float(2 * (1 - scipy_stats.t.cdf(abs(t_stat_effn), df=max(eff_n - 1, 1))))
    uji1_pass = t_stat_effn >= 3.0
    print(f"n_raw={n_trades}, eff_N={eff_n:.1f} (rasio keunikan={eff_n/n_trades:.4f}), "
          f"mean_net={mean_net:.3f}bps, t-stat(eff_N)={t_stat_effn:.3f}, p={p_value_t:.4f}")
    print(f"UJI 1: {'LOLOS' if uji1_pass else 'GAGAL'} (syarat t>=3.0)")
    report.append(f"## Uji 1 -- Signifikansi dengan eff_N\n\n"
                   f"n mentah={n_trades}, **eff_N={eff_n:.1f}** (rasio keunikan={eff_n/n_trades:.4f} -- "
                   f"holding 1 hari tumpang tindih banyak, N efektif jauh lebih kecil dari N mentah). "
                   f"mean net={mean_net:.3f}bps, **t-stat(eff_N)={t_stat_effn:.3f}**, p={p_value_t:.4f}.\n\n"
                   f"**{'LOLOS' if uji1_pass else 'GAGAL'}** (syarat t>=3.0).\n")

    # ============ UJI 2: walk-forward pada arm demeaned long-only ============
    print("\n=== UJI 2 -- Walk-forward 10 jendela (demeaned long-only) ===")
    window_edges = np.linspace(0, uji_end, 11).astype(int)
    wf_rows = []
    for w in range(10):
        lo, hi = window_edges[w], window_edges[w + 1]
        wmask = (entry_positions >= lo) & (entry_positions < hi)
        n = int(wmask.sum())
        if n < 10:
            wf_rows.append({"jendela": w + 1, "n_trades": n, "expectancy_net_bps": np.nan})
            continue
        net = raw_gross[wmask] - cost_base_bps
        wf_rows.append({"jendela": w + 1, "n_trades": n, "expectancy_net_bps": float(net.mean())})
    wf_df = pd.DataFrame(wf_rows)
    print(wf_df.to_string(index=False))
    n_positive = int((wf_df["expectancy_net_bps"] > 0).sum())
    pnl_per_window = (wf_df["expectancy_net_bps"].fillna(0) * wf_df["n_trades"])
    total_pnl = pnl_per_window.sum()
    top2_share = pnl_per_window.nlargest(2).sum() / total_pnl if total_pnl != 0 else np.nan
    uji2_pass = (n_positive >= 7) and (abs(top2_share) <= 0.60)
    print(f"{n_positive}/10 positif, kontribusi 2 jendela terbesar = {top2_share*100:.1f}% dari total PnL")
    print(f"UJI 2: {'LOLOS' if uji2_pass else 'GAGAL'} (syarat >=7/10 DAN <=60% dari 2 jendela)")
    report.append(f"\n## Uji 2 -- Walk-forward (demeaned long-only)\n\n" + wf_df.round(4).to_markdown(index=False))
    report.append(f"\n{n_positive}/10 jendela positif. Kontribusi 2 jendela PnL terbesar terhadap total: "
                   f"**{top2_share*100:.1f}%** (syarat <=60%).\n\n**{'LOLOS' if uji2_pass else 'GAGAL'}** "
                   f"(syarat >=7/10 DAN tidak terkonsentrasi >60% di 2 jendela).\n")

    # ============ UJI 3: permutasi blok 1000x ============
    print("\n=== UJI 3 -- Permutasi blok 1000x ===")
    rng = np.random.default_rng(7)
    block_size = max(1, H_M5 // 4)
    n_bars_perm = uji_end
    n_blocks = n_bars_perm // block_size
    observed_total = float(raw_gross.sum())
    perm_totals = np.empty(1000)
    ret_arr = demeaned_per_bar_ret[:n_bars_perm]
    blocks = [ret_arr[i * block_size:(i + 1) * block_size] for i in range(n_blocks)]
    for p in range(1000):
        order = rng.permutation(n_blocks)
        permuted = np.concatenate([blocks[j] for j in order])
        permuted_logp = np.cumsum(permuted)
        m = len(permuted_logp)
        fwd_perm = np.full(m, np.nan)
        valid_end = m - H_M5
        fwd_perm[:valid_end] = (permuted_logp[H_M5:] - permuted_logp[:valid_end]) * 1e4
        entries_in_range = entry_positions[entry_positions < valid_end]
        perm_totals[p] = np.nansum(fwd_perm[entries_in_range])
    percentile = float((perm_totals < observed_total).mean() * 100)
    uji3_pass = percentile >= 95
    print(f"observed_total={observed_total:.1f}, percentile_vs_null={percentile:.1f}")
    print(f"UJI 3: {'LOLOS' if uji3_pass else 'GAGAL'} (syarat >=persentil 95)")
    report.append(f"\n## Uji 3 -- Permutasi blok (1000x, block_size={block_size} bar)\n\n"
                   f"Observed total return (bps-equivalent sum)={observed_total:.1f}, berada di "
                   f"**persentil {percentile:.1f}** dari distribusi null (permutasi blok).\n\n"
                   f"**{'LOLOS' if uji3_pass else 'GAGAL'}** (syarat >=persentil 95).\n")

    # ============ UJI 4: biaya worst ============
    print("\n=== UJI 4 -- Biaya worst-case ===")
    net_worst = raw_gross - cost_worst
    exp_worst = float(net_worst.mean())
    uji4_pass = exp_worst > 0
    print(f"expectancy @ biaya worst ({cost_worst:.3f}bps) = {exp_worst:.3f}bps")
    print(f"UJI 4: {'LOLOS' if uji4_pass else 'GAGAL'} (syarat >0)")
    report.append(f"\n## Uji 4 -- Biaya worst-case\n\nExpectancy net @ biaya worst "
                   f"({cost_worst:.3f}bps) = **{exp_worst:.3f}bps**.\n\n"
                   f"**{'LOLOS' if uji4_pass else 'GAGAL'}** (syarat >0).\n")

    # ============ VERDICT ============
    n_pass = sum([uji1_pass, uji2_pass, uji3_pass, uji4_pass])
    overall_pass = n_pass == 4
    print(f"\n{'='*60}\nL1 VERDICT: {n_pass}/4 lolos -- {'LOLOS SEMUA, ada alpha kecil di bawah drift, LANJUTKAN' if overall_pass else 'GAGAL (' + str(4-n_pass) + ' dari 4) -- arm demeaned juga mati'}\n{'='*60}")
    report.append(f"\n## VERDICT L1\n\n"
                   f"Uji 1 (t-stat eff_N>=3.0): {'LOLOS' if uji1_pass else 'GAGAL'}  \n"
                   f"Uji 2 (walk-forward >=7/10, tak terkonsentrasi): {'LOLOS' if uji2_pass else 'GAGAL'}  \n"
                   f"Uji 3 (permutasi blok >=persentil 95): {'LOLOS' if uji3_pass else 'GAGAL'}  \n"
                   f"Uji 4 (expectancy>0 @ biaya worst): {'LOLOS' if uji4_pass else 'GAGAL'}  \n\n"
                   f"**{n_pass}/4 lolos.** {'**LOLOS SEMUA -- ada alpha kecil di bawah drift, lanjutkan riset (bukan langsung ke sistem trading).**' if overall_pass else f'**GAGAL -- arm demeaned juga mati sebagai sinyal. {4-n_pass} dari 4 uji gagal.**'}\n")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    ax = axes[0]
    colors = ["#2ca02c" if v > 0 else "#d62728" for v in wf_df["expectancy_net_bps"].fillna(0)]
    ax.bar(wf_df["jendela"], wf_df["expectancy_net_bps"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(f"Uji 2: Walk-forward ({n_positive}/10 positif)")
    ax.set_xlabel("jendela"); ax.set_ylabel("expectancy net (bps)")

    ax = axes[1]
    ax.hist(perm_totals, bins=50, color="#888888", alpha=0.8)
    ax.axvline(observed_total, color="#2ca02c" if uji3_pass else "#d62728", linewidth=2, label=f"observed (persentil {percentile:.0f})")
    ax.set_title("Uji 3: Permutasi blok vs observed")
    ax.legend(fontsize=8)

    ax = axes[2]
    checks = ["Uji1\nt-stat", "Uji2\nWF", "Uji3\nPermutasi", "Uji4\nBiaya worst"]
    passes = [uji1_pass, uji2_pass, uji3_pass, uji4_pass]
    ax.bar(checks, [1] * 4, color=["#2ca02c" if p else "#d62728" for p in passes])
    ax.set_ylim(0, 1.3)
    ax.set_yticks([])
    ax.set_title(f"Verdict L1: {n_pass}/4 lolos")
    for i, p in enumerate(passes):
        ax.text(i, 1.05, "LOLOS" if p else "GAGAL", ha="center", fontsize=10, fontweight="bold")

    plt.tight_layout()
    out_png = FIG_DIR / "l1_autopsi_demeaned.png"
    plt.savefig(out_png, dpi=120)
    print(f"saved {out_png}")

    (REPORTS / "L1_AUTOPSI_DEMEANED.md").write_text("\n".join(report))
    return overall_pass


if __name__ == "__main__":
    passed = main()
    sys.exit(0 if passed else 1)
