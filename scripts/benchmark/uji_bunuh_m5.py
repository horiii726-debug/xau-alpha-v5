#!/usr/bin/env python3
"""UJI_BUNUH_M5 -- gerbang sanity SEBELUM membangun apapun lebih lanjut.
Cek struktural: apakah M5 secara matematis punya ruang untuk profit setelah
biaya nyata, terlepas dari kualitas sinyal apapun.
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
from common import load_m5, load_m1, active_hours_mask, REPORTS, FIG_DIR
from lomba4_entry import build_signals

warnings.filterwarnings("ignore")

E_ABS_Z = 0.7979  # E[|Z|] untuk normal baku = sqrt(2/pi)
HOLDS = [1, 3, 6, 12, 24]  # bar M5
TAU = 1.5
LATIH_FRAC = 0.60


def main():
    m5 = load_m5()
    n_total = len(m5)
    latih_end = int(n_total * LATIH_FRAC)
    active = active_hours_mask(m5["bar_time"]).to_numpy()

    # ---- 1. biaya round-turn NYATA ----
    spread_arr = m5["spread_bps"].to_numpy()
    mask_cost = np.zeros(n_total, dtype=bool)
    mask_cost[:latih_end] = True
    mask_cost &= active & np.isfinite(spread_arr) & (spread_arr > 0) & (spread_arr < 500)
    sb = pd.Series(spread_arr[mask_cost])
    spread_p50 = float(sb.quantile(0.50))
    spread_p90 = float(sb.quantile(0.90))
    komisi_bps = 2 * 0.0014 * 100
    slip_p50 = 0.5 * spread_p50
    slip_p90 = 1.5 * spread_p90
    cost_base = spread_p50 + komisi_bps + slip_p50
    cost_worst = spread_p90 + komisi_bps + slip_p90
    print(f"=== 1. BIAYA ROUND-TURN NYATA (M5, jam aktif, LATIH) ===")
    print(f"  spread p50={spread_p50:.3f}bps, p90={spread_p90:.3f}bps, komisi={komisi_bps:.3f}bps")
    print(f"  biaya BASE (p50, slip 0.5x)  = {cost_base:.3f}bps")
    print(f"  biaya WORST (p90, slip 1.5x) = {cost_worst:.3f}bps")

    # ---- 2. sigma per bar M5 (realized) ----
    mid = m5["mid_close"].values
    logp = np.log(mid)
    ret1 = np.diff(logp, prepend=logp[0])
    sigma_1bar_bps = float(np.std(ret1[1:latih_end])) * 1e4
    print(f"\n=== 2. SIGMA PER BAR M5 (realized, LATIH) ===")
    print(f"  sigma_1bar = {sigma_1bar_bps:.3f} bps")

    # ---- 3. winrate breakeven per hold ----
    print(f"\n=== 3. WINRATE BREAKEVEN per hold (biaya BASE={cost_base:.3f}bps) ===")
    p_be = {}
    for h in HOLDS:
        sigma_h = sigma_1bar_bps * np.sqrt(h)
        p = (cost_base / (E_ABS_Z * sigma_h) + 1) / 2
        p_be[h] = p
        print(f"  hold={h:>2} bar: sigma_hold={sigma_h:7.2f}bps, p_breakeven={p:.4f} ({p*100:.2f}%)")

    # ---- 4. winrate AKTUAL: CUSUM (M5 native), MAC05/MAC07 (broadcast dari D1) ----
    print(f"\n=== 4. WINRATE AKTUAL vs BREAKEVEN ===")
    signals = build_signals(m5)
    cusum_z = signals["CUSUM"].values
    take_cusum = (np.abs(cusum_z) >= TAU)
    direction_cusum = np.sign(cusum_z)

    # muat MAC05/MAC07 dari L13, broadcast D1->M5 (lag sudah ada di konstruksinya)
    mac_available = Path("/workspace/data/macro/fred_daily.parquet").exists()
    mac_signals_m5 = {}
    if mac_available:
        try:
            sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
            from l13_lomba_makro import load_xau_d1, load_macro, build_macro_features, build_signals as build_macro_signals
            d1 = load_xau_d1()
            fred, cot = load_macro()
            dfm = build_macro_features(d1, fred, cot)
            latih_end_d1 = int(len(dfm) * LATIH_FRAC)
            mac_sig_d1 = build_macro_signals(dfm, latih_end_d1)
            dfm["date_only"] = dfm["date"].dt.date
            m5_dates = m5["bar_time"].dt.date
            for col in ["MAC05_cot_crowding", "MAC07_ridge_combo"]:
                lut = dict(zip(dfm["date_only"], mac_sig_d1[col].values))
                mac_signals_m5[col] = m5_dates.map(lut).values.astype(float)
        except Exception as e:
            print(f"  (macro broadcast gagal: {e} -- MAC05/MAC07 dilewati)")

    results = []
    for name, take, direction in [("CUSUM", take_cusum, direction_cusum)] + [
        (col, np.abs(vals) >= 1.0, np.sign(vals)) for col, vals in mac_signals_m5.items()
    ]:
        for h in HOLDS:
            fwd = (np.roll(logp, -h) - logp) * 1e4
            fwd[-h:] = np.nan
            take_h = take & np.isfinite(fwd) & np.isfinite(direction)
            n = int(take_h.sum())
            if n < 30:
                results.append({"peserta": name, "hold": h, "n": n, "winrate_aktual": np.nan,
                                 "p_breakeven": p_be[h], "selisih": np.nan})
                continue
            correct = (np.sign(direction[take_h]) == np.sign(fwd[take_h]))
            wr = float(correct.mean())
            results.append({"peserta": name, "hold": h, "n": n, "winrate_aktual": wr,
                             "p_breakeven": p_be[h], "selisih": wr - p_be[h]})
            flag = "LOLOS" if wr > p_be[h] else "GAGAL"
            print(f"  {name:20s} hold={h:>2}: n={n:>7} winrate_aktual={wr:.4f} vs breakeven={p_be[h]:.4f} "
                  f"(selisih={wr-p_be[h]:+.4f}) -> {flag}")

    any_pass = any(r["selisih"] > 0 for r in results if pd.notna(r.get("selisih")))

    # ---- 5. plafon Oracle ----
    print(f"\n=== 5. PLAFON ORACLE (arah selalu benar) ===")
    oracle_rows = []
    for h in HOLDS:
        sigma_h = sigma_1bar_bps * np.sqrt(h)
        gross_oracle = E_ABS_Z * sigma_h
        net_oracle_base = gross_oracle - cost_base
        net_oracle_worst = gross_oracle - cost_worst
        oracle_rows.append({"hold": h, "gross_oracle_bps": gross_oracle,
                             "net_oracle_base_bps": net_oracle_base, "net_oracle_worst_bps": net_oracle_worst})
        print(f"  hold={h:>2}: gross={gross_oracle:6.2f}bps, net@base={net_oracle_base:6.2f}bps, "
              f"net@worst={net_oracle_worst:6.2f}bps")

    # ---- 6. % bar dengan |return| > 2x biaya ----
    print(f"\n=== 6. Persentase bar M5 dengan |return| > 2x biaya round-turn ===")
    pct_rows = []
    for h in HOLDS:
        fwd = (np.roll(logp, -h) - logp) * 1e4
        fwd = fwd[np.isfinite(fwd)]
        pct = float((np.abs(fwd) > 2 * cost_base).mean()) * 100
        pct_rows.append({"hold": h, "pct_bar_gt_2x_biaya": pct})
        flag = "cukup" if pct >= 20 else "TERLALU SEDIKIT (<20%)"
        print(f"  hold={h:>2}: {pct:.2f}% bar |return|>2x biaya -> {flag}")

    verdict = "M5 HIDUP -- ada kombinasi winrate>breakeven" if any_pass else "M5 MATI -- winrate aktual < breakeven di SEMUA hold & peserta"
    print(f"\n{'='*70}\nVONIS: {verdict}\n{'='*70}")

    # ---- laporan ----
    lines = ["# UJI BUNUH M5\n",
              f"## 1. Biaya round-turn nyata (M5, jam aktif, LATIH)\n\n"
              f"spread p50={spread_p50:.3f}bps, p90={spread_p90:.3f}bps, komisi={komisi_bps:.3f}bps.\n"
              f"**Biaya BASE (p50, slip 0.5x)={cost_base:.3f}bps. Biaya WORST (p90, slip 1.5x)={cost_worst:.3f}bps.**\n",
              f"\n## 2. Sigma per bar M5 (realized)\n\n**{sigma_1bar_bps:.3f} bps/bar.**\n",
              f"\n## 3. Winrate breakeven per hold\n\n" + pd.DataFrame(
                  [{"hold": h, "sigma_hold_bps": sigma_1bar_bps*np.sqrt(h), "p_breakeven": p_be[h]} for h in HOLDS]
              ).round(4).to_markdown(index=False),
              f"\n## 4. Winrate aktual vs breakeven\n\n" + pd.DataFrame(results).round(4).to_markdown(index=False),
              f"\n## 5. Plafon Oracle (arah selalu benar)\n\n" + pd.DataFrame(oracle_rows).round(3).to_markdown(index=False),
              f"\n## 6. Persentase bar |return|>2x biaya\n\n" + pd.DataFrame(pct_rows).round(2).to_markdown(index=False),
              f"\n## VONIS\n\n**{verdict}**\n"]
    (REPORTS / "UJI_BUNUH_M5.md").write_text("\n".join(lines))

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    ax = axes[0]
    x = np.arange(len(HOLDS))
    w = 0.35
    res_df = pd.DataFrame(results)
    cusum_wr = [res_df[(res_df.peserta == "CUSUM") & (res_df.hold == h)]["winrate_aktual"].values[0] for h in HOLDS]
    be_wr = [p_be[h] for h in HOLDS]
    ax.bar(x - w/2, cusum_wr, w, label="winrate aktual (CUSUM)", color="#4a6fa5")
    ax.bar(x + w/2, be_wr, w, label="winrate breakeven", color="#d62728")
    ax.set_xticks(x); ax.set_xticklabels([str(h) for h in HOLDS])
    ax.set_xlabel("hold (bar M5)"); ax.set_ylabel("winrate")
    ax.set_title("Winrate aktual (CUSUM) vs breakeven")
    ax.legend(fontsize=8)

    ax = axes[1]
    odf = pd.DataFrame(oracle_rows)
    ax.plot(odf["hold"], odf["net_oracle_base_bps"], marker="o", label="net oracle @base")
    ax.plot(odf["hold"], odf["net_oracle_worst_bps"], marker="s", label="net oracle @worst")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("hold (bar M5)"); ax.set_ylabel("net bps/trade (oracle)")
    ax.set_title("Plafon Oracle (arah selalu benar)")
    ax.legend(fontsize=8)

    ax = axes[2]
    pdf = pd.DataFrame(pct_rows)
    ax.bar([str(h) for h in HOLDS], pdf["pct_bar_gt_2x_biaya"], color="#4a6fa5")
    ax.axhline(20, color="red", linestyle="--", label="ambang 20%")
    ax.set_xlabel("hold (bar M5)"); ax.set_ylabel("% bar |return|>2x biaya")
    ax.set_title("Bar dengan pergerakan cukup besar")
    ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "uji_bunuh_m5.png", dpi=120)
    print(f"saved {FIG_DIR / 'uji_bunuh_m5.png'}")

    return any_pass


if __name__ == "__main__":
    passed = main()
    sys.exit(0 if passed else 1)
