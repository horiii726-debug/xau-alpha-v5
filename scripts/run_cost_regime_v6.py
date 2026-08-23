#!/usr/bin/env python3
"""Perbaikan metodologi: pisahkan DAYA STATISTIK (diukur di SELURUH riwayat)
dari KELAYAKAN BIAYA (diukur HANYA di rezim biaya relevan -- 3 tahun
terakhir). Alasan: biaya bps = spread_USD/harga. Emas $350 -> ~52bps,
emas $4400 -> ~5.5bps -- rentang 10x. Merata-ratakan kappa lintas rezim
harga yang beda jauh menghasilkan angka yang tidak mewakili kondisi manapun.

Menulis reports/F0_cost_regime.md: tabel kappa PER TAHUN KALENDER penuh,
expectancy bersih di rezim LAMA vs BARU berdampingan, dan pernyataan
metodologi eksplisit.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspace/xau-alpha-v5")
from src.validation.l11_gate_power import make_h240_blocks, synthetic_signal

BAR_DIR = Path("/workspace/data/bars_candles")
REPORTS = Path("/workspace/xau-alpha-v5/reports")

RECENT_YEARS_N = 3


def cost_worst_bps(spread_p50: float, sigma_lat10_bps: float) -> float:
    """KOREKSI: skenario biaya WAJIB bersyarat pada Q10_SPREAD_PERCENTILE_GATE.
    Q10 hanya izinkan entry saat spread <= p50 -- jadi distribusi biaya yang
    relevan untuk expectancy adalah spread YANG LOLOS gerbang (dibatasi p50),
    BUKAN p90 seluruh sampel (yang mencakup periode yang Q10 sendiri akan
    tolak). Menghitung p90 sambil punya gerbang yang melarang p90 = menghukum
    dua kali. Skenario worst sekarang: spread=p50, alpha=1.5, penalty=1.5
    (alpha/penalty TETAP ketat -- yang diperbaiki cuma spread mana yang jadi
    basis, bukan konservatisme keseluruhan)."""
    slip = 1.5 * spread_p50 + 0.5 * sigma_lat10_bps
    komisi_rt = 2 * 0.140
    return (2 * spread_p50 + slip) * 1.5 + komisi_rt


def cost_best_bps(spread_p25: float, sigma_lat1_bps: float) -> float:
    slip = 0.5 * spread_p25 + 0.0 * sigma_lat1_bps
    komisi_rt = 2 * 0.140
    return (2 * spread_p25 + slip) * 1.0 + komisi_rt


def yearly_kappa_table(symbol: str) -> pd.DataFrame:
    m5 = pd.read_parquet(BAR_DIR / f"{symbol}_M5.parquet")
    m5["bar_time"] = pd.to_datetime(m5["bar_time"], utc=True)
    m5["year"] = m5["bar_time"].dt.year
    m5["mid_ret"] = m5["mid_close"].pct_change()

    rows = []
    for year, g in m5.groupby("year"):
        sb = g["spread_bps"].dropna()
        sb = sb[(sb > 0) & (sb < 1000)]
        if len(sb) < 100:
            continue
        p25, p50 = sb.quantile([0.25, 0.50])
        sigma_m5 = g["mid_ret"].std() * 1e4
        sigma_m1 = sigma_m5 / np.sqrt(5.0)
        sigma_lat10 = sigma_m1 * np.sqrt(10 / 60.0)
        cost_worst = cost_worst_bps(p50, sigma_lat10)
        sigma_h240 = sigma_m5 * np.sqrt(240 / 5.0)
        kappa_h240 = cost_worst / sigma_h240
        mean_price = g["mid_close"].mean()
        rows.append({"year": year, "mean_price": mean_price, "spread_p25_bps": p25,
                      "spread_p50_bps": p50, "sigma_m5_bps": sigma_m5,
                      "cost_worst_bps": cost_worst, "sigma_h240_bps": sigma_h240,
                      "kappa_h240_worst": kappa_h240, "n_bars": len(g)})
    return pd.DataFrame(rows)


def regime_cost(symbol: str, years: list[int]) -> float:
    """Biaya 'worst' bersyarat Q10 (spread<=p50) -- lihat cost_worst_bps()."""
    m5 = pd.read_parquet(BAR_DIR / f"{symbol}_M5.parquet")
    m5["bar_time"] = pd.to_datetime(m5["bar_time"], utc=True)
    sub = m5[m5["bar_time"].dt.year.isin(years)]
    sb = sub["spread_bps"].dropna()
    sb = sb[(sb > 0) & (sb < 1000)]
    p50 = sb.quantile(0.50)
    sub = sub.copy()
    sub["mid_ret"] = sub["mid_close"].pct_change()
    sigma_m5 = sub["mid_ret"].std() * 1e4
    sigma_m1 = sigma_m5 / np.sqrt(5.0)
    sigma_lat10 = sigma_m1 * np.sqrt(10 / 60.0)
    return cost_worst_bps(p50, sigma_lat10)


def gross_edge_at_ic(r_block: np.ndarray, ic: float, n_seeds: int, tau: float,
                      br_eff_per_year_full: float = None) -> float:
    """tau: ambang |signal| EKSPLISIT (bukan diturunkan dari target frekuensi
    trade) -- selektivitas nyata, lihat l11_gate_power.trial()."""
    grosses = []
    for s in range(n_seeds):
        rng = np.random.default_rng(50000 + s)
        signal = synthetic_signal(r_block, ic, rng)
        tk = np.abs(signal) >= tau
        pos = np.where(tk, np.sign(signal), 0.0)
        grosses.append(((pos * r_block)[tk]).mean() * 1e4)
    return float(np.mean(grosses))


def main():
    symbol = "XAUUSD"
    yk = yearly_kappa_table(symbol)
    years_present = sorted(yk["year"].unique().tolist())
    recent_years = years_present[-RECENT_YEARS_N:]
    full_years = years_present

    lines = ["# F0 -- Model Biaya PER-REZIM (koreksi metodologi)\n"]
    lines.append(
        "**Kesalahan sebelumnya:** kappa/expectancy dihitung dari rata-rata spread di SELURUH "
        "riwayat sekaligus. Salah -- biaya dalam bps = spread_USD/harga, dan harga emas berubah "
        "besar antar tahun (2012 ~$1650-1800, sekarang jauh lebih tinggi). Merata-ratakan bps "
        "lintas rezim harga berbeda menghasilkan angka yang TIDAK mewakili kondisi tahun manapun.\n"
    )
    lines.append(
        f"**Metodologi yang benar (diterapkan mulai sekarang):**\n"
        f"- **DAYA STATISTIK** (IC, t-stat, K_eff, T_confirm) -> diukur di SELURUH riwayat yang ada "
        f"({years_present[0]}-{years_present[-1]}). Itu gunanya riwayat panjang: sampel besar.\n"
        f"- **KELAYAKAN BIAYA** (kappa, expectancy bersih, L11) -> diukur HANYA di **{RECENT_YEARS_N} "
        f"tahun terakhir yang tersedia** ({recent_years[0]}-{recent_years[-1]}), rezim biaya yang "
        f"relevan untuk eksekusi NYATA hari ini, bukan rezim harga 2012.\n"
    )
    lines.append(f"\n## Tabel kappa PER TAHUN KALENDER -- {symbol}, H240, skenario worst BERSYARAT Q10 "
                  f"(spread<=p50, FULL, tidak disembunyikan)\n")
    lines.append("| tahun | harga rata-rata | spread p25 bps | spread p50 bps (basis worst) | sigma M5 bps | "
                  "biaya worst bps | sigma H240 bps | **kappa H240 worst** | n bar M5 |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in yk.iterrows():
        marker = " **<-rezim-sekarang**" if r["year"] in recent_years else ""
        lines.append(f"| {int(r['year'])}{marker} | {r['mean_price']:.1f} | {r['spread_p25_bps']:.3f} | "
                      f"{r['spread_p50_bps']:.3f} | {r['sigma_m5_bps']:.3f} | {r['cost_worst_bps']:.2f} | "
                      f"{r['sigma_h240_bps']:.2f} | **{r['kappa_h240_worst']:.3f}** | {int(r['n_bars']):,} |")

    cost_full = regime_cost(symbol, full_years)
    cost_recent = regime_cost(symbol, recent_years)
    lines.append(f"\n## Biaya worst-case: SELURUH riwayat vs rezim-sekarang\n")
    lines.append(f"| rezim | tahun | biaya worst H240 (bps) |")
    lines.append(f"|---|---|---:|")
    lines.append(f"| Seluruh riwayat (dicampur, TIDAK dipakai lagi untuk kelayakan) | {full_years[0]}-{full_years[-1]} | {cost_full:.2f} |")
    lines.append(f"| **Rezim sekarang (dipakai untuk kelayakan biaya)** | {recent_years[0]}-{recent_years[-1]} | **{cost_recent:.2f}** |")

    m15 = pd.read_parquet(BAR_DIR / f"{symbol}_M15.parquet")
    m15["bar_time"] = pd.to_datetime(m15["bar_time"], utc=True)
    mid_full = m15["mid_close"].dropna().values
    r_block_full = make_h240_blocks(mid_full, 16)
    span_years_full = (m15["bar_time"].max() - m15["bar_time"].min()).days / 365.25
    br_eff_full = len(r_block_full) / span_years_full

    m15_recent = m15[m15["bar_time"].dt.year.isin(recent_years)]
    mid_recent = m15_recent["mid_close"].dropna().values
    r_block_recent = make_h240_blocks(mid_recent, 16)
    span_years_recent = (m15_recent["bar_time"].max() - m15_recent["bar_time"].min()).days / 365.25
    br_eff_recent = len(r_block_recent) / max(span_years_recent, 0.1)

    lines.append(f"\n## Expectancy bersih (gross edge - biaya) berdampingan: biaya-LAMA vs biaya-BARU, per tau\n")
    lines.append(f"Sinyal sintetis, 100 seed per IC, dievaluasi pada blok H240 dari **data rezim-sekarang "
                  f"saja** ({recent_years[0]}-{recent_years[-1]}, n={len(r_block_recent)} blok). Ambang "
                  f"selektivitas tau EKSPLISIT (bukan diturunkan dari target frekuensi) -- edge per trade "
                  f"= IC * sigma * E[z||z|>tau], E[z|.] naik dengan tau.\n")
    for tau_v in [1.0, 1.5]:
        lines.append(f"\n**tau={tau_v}**\n")
        lines.append("| IC | gross edge (bps) | net @ biaya-LAMA ({:.1f}bps) | net @ biaya-BARU ({:.1f}bps) |"
                      .format(cost_full, cost_recent))
        lines.append("|---:|---:|---:|---:|")
        for ic in [0.03, 0.05, 0.08, 0.15, 0.30]:
            gross = gross_edge_at_ic(r_block_recent, ic, 100, tau_v)
            lines.append(f"| {ic} | {gross:.2f} | {gross - cost_full:.2f} | {gross - cost_recent:.2f} |")

    lines.append(
        f"\n## Pernyataan metodologi (wajib dicantumkan di semua laporan turunan)\n\n"
        f"> **Sinyal divalidasi di {years_present[0]}-{years_present[-1]} ({len(years_present)} tahun). "
        f"Kelayakan biaya divalidasi di {recent_years[0]}-{recent_years[-1]} ({RECENT_YEARS_N} tahun "
        f"terakhir) -- rezim biaya yang relevan untuk eksekusi hari ini.**\n"
    )
    (REPORTS / "F0_cost_regime.md").write_text("\n".join(lines))
    print(f"wrote F0_cost_regime.md -- cost_full={cost_full:.2f} cost_recent={cost_recent:.2f}")

    import json
    Path(REPORTS / "cost_regime_result.json").write_text(json.dumps(
        {"symbol": symbol, "years_present": years_present, "recent_years": recent_years,
         "cost_full_bps": cost_full, "cost_recent_bps": cost_recent,
         "br_eff_recent_per_year": br_eff_recent}, indent=2, default=str))


if __name__ == "__main__":
    main()
