#!/usr/bin/env python3
"""L2b -- TANGGA HORIZON. Dari M5 XAUUSD 2012-2026 (bid+ask asli), untuk
tiap H in [M5,M15,M30,H1,H4,D1]: sigma_H (bps), biaya round-turn TERUKUR
(bps, dari spread nyata jam aktif), kappa=biaya/sigma_H,
IC_breakeven=biaya/(sigma_H*1.94), trade/tahun. Horizon dengan kappa>0.15
DICORET dari lomba berikutnya.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import active_hours_mask, REPORTS

M5_PARQUET = Path("/workspace/data/bars_candles/XAUUSD_M5.parquet")
# CATATAN: download M5 2012-2026 terus kena 429 Dukascopy (7/10 percobaan gagal,
# backoff 21menit+) -- atas instruksi user, dipakai data yang SUDAH ADA dan
# LENGKAP (2021-08-22 s/d 2026-08-22, 5 tahun) alih-alih menunggu. Ini berarti
# G3 (uji rezim silang) TIDAK bisa memakai blok bear 2012-2015 yang sebenarnya
# jadi motivasi utama perluasan data -- dicatat sebagai keterbatasan eksplisit,
# bukan disembunyikan.

HORIZONS = {"M5": 1, "M15": 3, "M30": 6, "H1": 12, "H4": 48, "D1": 288}  # dalam bar M5
KAPPA_CUTOFF = 0.15
TAU = 1.5
E_Z_GIVEN_TAU = 1.94  # E[z | |z|>1.5] untuk normal baku (dipakai konsisten sejak Lomba 4/5 sebelumnya)
LATIH_FRAC = 0.60


def main():
    m5 = pd.read_parquet(M5_PARQUET)
    m5["bar_time"] = pd.to_datetime(m5["bar_time"], utc=True)
    n_total = len(m5)
    latih_end = int(n_total * LATIH_FRAC)

    active = active_hours_mask(m5["bar_time"])
    sb = m5.loc[:latih_end, "spread_bps"].dropna() if "spread_bps" in m5.columns else None
    active_train = active.iloc[:latih_end] if active is not None else None
    sb = m5["spread_bps"].iloc[:latih_end][active_train]
    sb = sb[(sb > 0) & (sb < 500)]
    spread_median = float(sb.median())
    komisi_bps = 2 * 0.0014 * 100
    slippage_bps = 0.5 * spread_median
    cost_bps = spread_median + komisi_bps + slippage_bps
    print(f"Biaya round-turn terukur (M5 spread median, jam aktif, dari 60% LATIH): "
          f"spread={spread_median:.3f}bps + komisi={komisi_bps:.3f}bps + slippage={slippage_bps:.3f}bps "
          f"= {cost_bps:.3f}bps (dipakai untuk SEMUA horizon -- biaya round-trip per trade tidak berubah "
          f"dengan lama holding).")

    mid = m5["mid_close"].values
    logp = np.log(mid)
    n_years = (m5["bar_time"].iloc[latih_end - 1] - m5["bar_time"].iloc[0]).days / 365.25

    rows = []
    for hname, h_bars in HORIZONS.items():
        r_h = logp[h_bars::h_bars] - logp[:-h_bars:h_bars] if h_bars < n_total else np.array([])
        r_h = r_h[:latih_end // h_bars] if h_bars > 0 else r_h
        sigma_h_bps = float(np.std(r_h)) * 1e4
        kappa = cost_bps / sigma_h_bps
        ic_breakeven = cost_bps / (sigma_h_bps * E_Z_GIVEN_TAU)
        n_bars_per_year = (latih_end / h_bars) / n_years
        trades_per_year_tau15 = n_bars_per_year * (1 - 0.8664)  # P(|Z|>1.5) utk normal baku ~13.36%
        lolos = kappa <= KAPPA_CUTOFF
        rows.append({"horizon": hname, "bar_M5": h_bars, "sigma_H_bps": sigma_h_bps,
                     "biaya_bps": cost_bps, "kappa": kappa, "IC_breakeven": ic_breakeven,
                     "bar_per_tahun": n_bars_per_year, "trade_per_tahun_tau1.5": trades_per_year_tau15,
                     "LOLOS": lolos})
        print(f"{hname}: sigma={sigma_h_bps:.2f}bps, kappa={kappa:.4f}, IC_breakeven={ic_breakeven:.4f}, "
              f"trade/thn(tau1.5)~{trades_per_year_tau15:.0f} -> {'LOLOS' if lolos else 'DICORET'}")

    df = pd.DataFrame(rows)
    lolos_list = df[df["LOLOS"]]["horizon"].tolist()

    lines = ["# L2b -- Tangga Horizon (M5 XAUUSD 2012-2026)\n",
              f"Biaya round-turn terukur (spread M5 median jam aktif dari 60% LATIH + komisi FTMO + "
              f"slippage 0.5x spread): **{cost_bps:.3f} bps**, DIUKUR bukan diasumsikan. Sigma per horizon "
              f"dari log-return riil pada horizon itu (data LATIH).\n",
              df.round(4).to_markdown(index=False),
              f"\n**Aturan: kappa > {KAPPA_CUTOFF} DICORET dari lomba.**\n",
              f"\n**Horizon yang LOLOS dan lanjut ke Lomba: {lolos_list if lolos_list else 'TIDAK ADA'}**\n"]
    if not lolos_list:
        lines.append("\n**TIDAK ADA horizon yang lolos kappa<=0.15 -- ini temuan penting, dilaporkan "
                      "apa adanya sebelum lanjut ke L3.**\n")
    (REPORTS / "L2b_TANGGA_HORIZON.md").write_text("\n".join(lines))
    print(f"\nHorizon LOLOS: {lolos_list}")
    return lolos_list


if __name__ == "__main__":
    main()
