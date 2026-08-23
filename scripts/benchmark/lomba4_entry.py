#!/usr/bin/env python3
"""LOMBA 4 -- ENTRY. Target: tanda return H bar ke depan. Semua sinyal
di-z-score-kan lalu diberi ambang kekuatan tau=[1.0,1.5] (bukan cuma sign()).
Biaya round-trip diukur dari data NYATA (spread jam aktif saja, dari TRAIN),
dicetak eksplisit sebelum dipakai. Baseline: entry ACAK, holding & biaya
dicocokkan. Data M5, vectorized (bukan loop per-titik -- semua sinyal di
sini closed-form / rolling, jadi cepat untuk seluruh seri).
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
from common import load_m5, chronological_split, bootstrap_pvalue, spearman_ic, FIG_DIR, REPORTS, measure_cost_bps, load_m1

warnings.filterwarnings("ignore")

H_GRID = {"1h": 12, "4h": 48, "1d": 288}  # M5 bars
TAU_GRID = [1.0, 1.5]
L_MOM = 24        # lookback for momentum/reversal (2h)
L_ORB = 48        # opening-range lookback (4h)
L_DRIFT = 12      # drift-burst window (1h)
L_MAD = 48        # MAD z-score window
CUSUM_K = 0.5     # CUSUM slack (in local std units)
CUSUM_H = 5.0     # CUSUM threshold


def rolling_z(x: pd.Series, window: int) -> pd.Series:
    m = x.rolling(window).mean()
    s = x.rolling(window).std()
    return (x - m) / s.replace(0, np.nan)


def mad_z(x: pd.Series, window: int) -> pd.Series:
    med = x.rolling(window).median()
    mad = (x - med).abs().rolling(window).median()
    return 0.6745 * (x - med) / mad.replace(0, np.nan)


def build_signals(m5: pd.DataFrame) -> pd.DataFrame:
    mid = m5["mid_close"]
    ret1 = np.log(mid).diff()
    sigma = ret1.rolling(96).std()  # local vol, ~8h window on M5

    df = pd.DataFrame(index=m5.index)
    # 1. z-score MAD atas sinyal momentum harga (robust momentum)
    df["MAD-Zscore-momentum"] = mad_z(mid, L_MAD)
    # 2. momentum vol-scaled
    mom = (mid - mid.shift(L_MOM)) / (sigma * np.sqrt(L_MOM))
    df["Momentum-VolScaled"] = mom
    # 3. short-horizon reversal (arah dibalik dari momentum)
    df["ShortHorizon-Reversal"] = -mom
    # 4. opening range breakout: posisi relatif thd rolling max/min L_ORB bar SEBELUMNYA
    roll_max = mid.shift(1).rolling(L_ORB).max()
    roll_min = mid.shift(1).rolling(L_ORB).min()
    roll_mid = (roll_max + roll_min) / 2
    roll_range = (roll_max - roll_min).replace(0, np.nan)
    orb = (mid - roll_mid) / roll_range * 2  # normalized position in [-1,1]-ish, treat as z-like
    df["ORB"] = rolling_z(orb, L_ORB)
    # 5. drift burst t-stat: mean(ret)/std(ret) pada window pendek (kernel seragam sederhana)
    mu_hat = ret1.rolling(L_DRIFT).mean()
    sigma_hat = ret1.rolling(L_DRIFT).std()
    df["DriftBurst-tstat"] = np.sqrt(L_DRIFT) * mu_hat / sigma_hat.replace(0, np.nan)
    # 6. CUSUM: statistik kumulatif standar return, direset saat lewati ambang
    z1 = (ret1 - ret1.rolling(200).mean()) / ret1.rolling(200).std().replace(0, np.nan)
    cusum_pos = np.zeros(len(df))
    cusum_neg = np.zeros(len(df))
    z1v = z1.fillna(0).values
    for i in range(1, len(z1v)):
        cusum_pos[i] = max(0.0, cusum_pos[i - 1] + z1v[i] - CUSUM_K)
        cusum_neg[i] = min(0.0, cusum_neg[i - 1] + z1v[i] + CUSUM_K)
    cusum_stat = np.where(cusum_pos > CUSUM_H, cusum_pos, np.where(cusum_neg < -CUSUM_H, cusum_neg, 0.0))
    df["CUSUM"] = rolling_z(pd.Series(cusum_stat, index=df.index), 200)
    return df


def run():
    m5 = load_m5()
    m1 = load_m1()
    n_total = len(m5)
    train_mask, test_mask = chronological_split(n_total, 0.70)

    cost_info = measure_cost_bps(m1, chronological_split(len(m1), 0.70)[0])
    round_trip_bps = cost_info["round_trip_cost_bps"]

    signals = build_signals(m5)
    mid = m5["mid_close"].values
    logp = np.log(mid)

    report_lines = ["# LOMBA 4 -- ENTRY\n",
                     f"**Biaya round-trip terukur (jam trading aktif saja, dari TRAIN):** "
                     f"spread median={cost_info['spread_median_bps']:.3f}bps, "
                     f"komisi FTMO round-trip={cost_info['komisi_roundtrip_bps']:.3f}bps, "
                     f"slippage(0.5x spread)={cost_info['slippage_bps']:.3f}bps -> "
                     f"**TOTAL={round_trip_bps:.3f}bps** (n={cost_info['n_bars_used']:,} bar M1 jam aktif).\n",
                     "\nTarget: tanda return H bar ke depan. Tiap sinyal di-z-score, entry hanya kalau "
                     "|z|>=tau. Baseline: entry ACAK dicocokkan jumlah trade & holding period per (H,tau).\n"]

    fig, axes = plt.subplots(1, 3, figsize=(19, 6))
    fig.suptitle(f"LOMBA 4 -- ENTRY: expectancy bersih (bps), biaya={round_trip_bps:.2f}bps", fontsize=13, fontweight="bold")

    all_results = {}
    for h_i, (hname, H) in enumerate(H_GRID.items()):
        fwd_ret_bps = (np.roll(logp, -H) - logp) * 1e4
        fwd_ret_bps[-H:] = np.nan

        for tau_i, tau in enumerate(TAU_GRID):
            rows = []
            for name in signals.columns:
                z = signals[name].values
                take = np.abs(z) >= tau
                direction = np.sign(z)
                test_take = take & test_mask & np.isfinite(fwd_ret_bps) & np.isfinite(z)
                n_trades = int(test_take.sum())
                if n_trades < 20:
                    rows.append({"peserta": name, "tau": tau, "n_trades": n_trades, "IC": np.nan,
                                 "hit_rate": np.nan, "expectancy_net_bps": np.nan, "p_value_boot": np.nan})
                    continue
                ic = spearman_ic(z[test_mask & np.isfinite(fwd_ret_bps)], fwd_ret_bps[test_mask & np.isfinite(fwd_ret_bps)])
                gross = direction[test_take] * fwd_ret_bps[test_take]
                net = gross - round_trip_bps
                hit = float((np.sign(gross) > 0).mean())
                pval = bootstrap_pvalue(net)
                rows.append({"peserta": name, "tau": tau, "n_trades": n_trades, "IC": ic,
                             "hit_rate": hit, "expectancy_net_bps": float(net.mean()), "p_value_boot": pval})

            # baseline: random direction, matched n_trades (use avg across participants at this H,tau) & holding=H
            avg_n = int(np.nanmean([r["n_trades"] for r in rows if r["n_trades"] >= 20])) if any(r["n_trades"] >= 20 for r in rows) else 0
            if avg_n >= 20:
                rng = np.random.default_rng(42)
                valid_test_idx = np.where(test_mask & np.isfinite(fwd_ret_bps))[0]
                entries = rng.choice(valid_test_idx, size=min(avg_n, len(valid_test_idx)), replace=False)
                rand_dir = rng.choice([-1.0, 1.0], size=len(entries))
                gross_b = rand_dir * fwd_ret_bps[entries]
                net_b = gross_b - round_trip_bps
                rows.append({"peserta": "BASELINE (entry acak)", "tau": tau, "n_trades": len(entries),
                             "IC": 0.0, "hit_rate": float((np.sign(gross_b) > 0).mean()),
                             "expectancy_net_bps": float(net_b.mean()), "p_value_boot": np.nan})

            df = pd.DataFrame(rows).sort_values("expectancy_net_bps", ascending=False)
            all_results[(hname, tau)] = df
            print(f"\n=== Lomba 4 -- H={hname} tau={tau} ===")
            print(df.to_string(index=False))
            winner = df.iloc[0]
            base_rows = df[df.peserta.str.contains("BASELINE")]
            base_exp = base_rows["expectancy_net_bps"].values[0] if len(base_rows) else np.nan
            print(f"WINNER: {winner['peserta']} expectancy_net={winner['expectancy_net_bps']:.3f}bps "
                  f"(baseline={base_exp:.3f}bps)")

            report_lines.append(f"\n## H={hname}, tau={tau}\n")
            report_lines.append(df.round(4).to_markdown(index=False))
            sig = pd.notna(winner['p_value_boot']) and winner['p_value_boot'] < 0.05
            report_lines.append(f"\n**Menang: {winner['peserta']}** (expectancy bersih={winner['expectancy_net_bps']:.3f}bps "
                                 f"vs baseline {base_exp:.3f}bps). p-value bootstrap="
                                 f"{winner['p_value_boot']}. ({'signifikan' if sig else 'TIDAK signifikan/NA'}).\n")

        # plot: tau=1.5 panel per horizon
        ax = axes[h_i]
        df_plot = all_results[(hname, 1.5)].sort_values("expectancy_net_bps")
        colors = ["#888888" if "BASELINE" in p else ("#2ca02c" if v > 0 else "#d62728")
                  for v, p in zip(df_plot["expectancy_net_bps"], df_plot["peserta"])]
        ax.barh(df_plot["peserta"], df_plot["expectancy_net_bps"], color=colors)
        ax.axvline(0, color="black", linestyle="-", linewidth=0.8)
        ax.set_title(f"H={hname}, tau=1.5")
        ax.set_xlabel("expectancy net (bps)")

    plt.tight_layout()
    out_png = FIG_DIR / "lomba4_entry.png"
    plt.savefig(out_png, dpi=120)
    print(f"\nsaved {out_png}")
    (REPORTS / "LOMBA4_ENTRY.md").write_text("\n".join(report_lines))
    return all_results


if __name__ == "__main__":
    run()
