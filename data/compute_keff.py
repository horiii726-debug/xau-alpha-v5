#!/usr/bin/env python3
"""F0 power-analysis measurements (power_analysis.e in 00_KONTRAK_DAN_KELAYAKAN.md):
- uniqueness ratio per instrument (proxy: from a baseline triple-barrier-style
  labeling on M5 bars, since full CPCV infra is F1 -- this is the F0-stage
  baseline strategy PnL used ONLY to measure correlation structure, not a
  candidate itself)
- correlation matrix of baseline strategy PnL across the panel
- K_eff via eigenvalue method: K_eff = (sum(lambda))^2 / sum(lambda^2)
- K_eff via equicorrelated method: K_eff = K / (1 + (K-1)*rho_bar)
- t_single at IC 0.03 and IC 0.05 (T_confirm = 4.0 years per 00_KONTRAK)
- K_eff required = (3.0 / t_single)^2
- writes reports/F0_universe.md (K_eff section)

Baseline strategy for PnL correlation: entry each bar with sign(momentum
over L=12 M5 bars), holding 12 bars, no cost -- deliberately the crudest
possible common signal, used ONLY to measure cross-instrument correlation
structure (the panel's shared-risk-factor exposure), not as a real
candidate. This matches the project's own framing: "matriks korelasi PnL
STRATEGI baseline antar instrumen" -- a baseline, not a candidate.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

BAR_DIR = Path("/workspace/data/bars_candles")
REPORTS_DIR = Path("/workspace/reports")
SYMBOLS = ["XAUUSD", "XAGUSD", "EURUSD", "LIGHTCMDUSD"]

T_CONFIRM_YEARS = 4.0
T_TARGET = 3.0


def baseline_pnl_series(bars: pd.DataFrame, L: int = 12, hold: int = 12) -> pd.Series:
    mid = bars["mid_close"] if "mid_close" in bars.columns else (bars["ask_close"] + bars["bid_close"]) / 2
    mom = mid.pct_change(L)
    sig = np.sign(mom).shift(1)  # causal: signal known at bar close, acted on next bar
    ret = mid.pct_change()
    strat_ret = sig * ret
    return strat_ret.dropna()


def uniqueness_ratio(n_bars: int, hold: int) -> float:
    # crude proxy: average concurrency under fixed-holding-period labels = hold
    # uniqueness ~ 1 / avg_concurrency for non-overlapping-adjusted labels
    if n_bars == 0:
        return float("nan")
    return 1.0 / hold


def main():
    lines = ["# F0 — Power Analysis (K_eff, uniqueness, screen_max)\n"]
    lines.append(
        "Baseline strategi untuk mengukur korelasi PnL: sign(momentum M5 L=12), "
        "hold 12 bar, TANPA biaya. Ini BUKAN kandidat -- hanya alat ukur struktur "
        "korelasi panel, sesuai power_analysis.c.catatan_penting.\n"
    )

    pnl_series = {}
    for symbol in SYMBOLS:
        f = BAR_DIR / f"{symbol}_M5.parquet"
        if not f.exists():
            lines.append(f"- {symbol}: TIDAK ADA DATA BAR (belum diagregasi)")
            continue
        bars = pd.read_parquet(f)
        if len(bars) < 100:
            lines.append(f"- {symbol}: bar terlalu sedikit ({len(bars)}), dilewati")
            continue
        ret = baseline_pnl_series(bars)
        pnl_series[symbol] = ret
        lines.append(f"- {symbol}: {len(bars):,} bar M5, {len(ret):,} return baseline")

    if len(pnl_series) < 2:
        lines.append("\n**TIDAK CUKUP INSTRUMEN dengan data untuk menghitung matriks korelasi. K_eff TIDAK BISA DIHITUNG.**")
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        (REPORTS_DIR / "F0_universe.md").write_text("\n".join(lines))
        print("\n".join(lines))
        return

    # align on common index
    df = pd.DataFrame(pnl_series).dropna()
    lines.append(f"\nJumlah observasi bersama (setelah align & dropna): {len(df):,}\n")

    corr = df.corr()
    lines.append("## Matriks korelasi PnL baseline\n")
    lines.append(corr.round(3).to_string())
    lines.append("")

    eigvals = np.linalg.eigvalsh(corr.values)
    eigvals = np.clip(eigvals, 0, None)  # numerical safety
    K_eff_eigen = (eigvals.sum() ** 2) / (eigvals**2).sum()

    K = len(pnl_series)
    offdiag = corr.values[~np.eye(K, dtype=bool)]
    rho_bar = offdiag.mean()
    K_eff_equicorr = K / (1 + (K - 1) * rho_bar)

    lines.append(f"K = {K} instrumen dengan data")
    lines.append(f"rho_bar (korelasi rata-rata berpasangan) = {rho_bar:.4f}")
    lines.append(f"K_eff (metode eigenvalue) = {K_eff_eigen:.3f}")
    lines.append(f"K_eff (metode equicorrelated) = {K_eff_equicorr:.3f}")
    lines.append("")

    for ic, label in [(0.05, "dasar"), (0.03, "pesimistis")]:
        BR = 300  # trades/year target from statistics.min_trades_per_year
        IR = ic * np.sqrt(BR)
        t_single = IR * np.sqrt(T_CONFIRM_YEARS)
        K_eff_needed = (T_TARGET / t_single) ** 2 if t_single > 0 else float("inf")
        lines.append(f"### IC={ic} ({label})")
        lines.append(f"IR = IC*sqrt(BR={BR}) = {IR:.4f}")
        lines.append(f"t_single = IR*sqrt(T_confirm={T_CONFIRM_YEARS}) = {t_single:.4f}")
        lines.append(f"K_eff dibutuhkan = (3.0/t_single)^2 = {K_eff_needed:.3f}")
        lines.append("")

    K_eff_measured = min(K_eff_eigen, K_eff_equicorr)  # conservative: report the lower
    lines.append(f"## Verdict gerbang F0\n")
    lines.append(f"K_eff terukur (dipakai, konservatif = min dari 2 metode) = {K_eff_measured:.3f}")

    if K_eff_measured < 3:
        lines.append("\n**K_eff < 3 -> BERHENTI. Jangan jalankan kandidat apapun (stop_conditions.0).**")
        screen_max = None
    else:
        screen_max = max(219, min(500, int(np.floor(50 * K_eff_measured))))
        lines.append(f"\nscreen_max = max(219, min(500, floor(50*{K_eff_measured:.3f}))) = {screen_max}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "F0_universe.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
