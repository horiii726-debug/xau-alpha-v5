#!/usr/bin/env python3
"""F2 -- GERBANG STRUKTUR PAYOFF, per 04_PARTISI_LABELING_PAYOFF.md.

Entry ACAK (belum ada rumus/sinyal apapun). Grid k_sl x k_tp (6x7=42
kombinasi). 3 arm per kombinasi: raw, demeaned (ARM PENENTU), sign_flipped.
Long-only dan short-only diuji TERPISAH (long_only_verdict paksa GAGAL --
drift capture -- kalau cuma long yang diuji).

Dijalankan pada partisi SCREEN (20% pertama secara kronologis) dari XAUUSD,
horizon M5 (H60 = 12 bar M5, prioritas user), n_random_entries=20000 per
sisi (long/short) per kombinasi.
"""
import sys
sys.path.insert(0, "/workspace")

import numpy as np
import pandas as pd
from pathlib import Path

from src.labeling.triple_barrier import triple_barrier_labels, parkinson_sigma, breakeven_mekanis

BAR_DIR = Path("/workspace/data/bars_candles")
REPORTS_DIR = Path("/workspace/reports")

K_SL_GRID = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
K_TP_GRID = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
N_RANDOM_ENTRIES = 20000
MAX_HOLD_BARS = 12  # H60 on M5 bars, per 03_UNIVERSE_DAN_HORIZON.md grid
SIGMA_WINDOW = 96  # V01_PARKINSON window (bar count), mid grid choice

MARGIN_MIN_PP = 2.0
MAX_RAW_VS_DEMEANED_GAP_PP = 1.0
SIGN_FLIP_TOLERANCE_PP = 0.5
STABILITY_SUB_PERIODS = 3


def _log_shift_ohlc(mid: np.ndarray, high: np.ndarray, low: np.ndarray, open_: np.ndarray, new_mid: np.ndarray):
    """Apply the SAME per-bar log-shift used to turn `mid` into `new_mid`
    to high/low/open too, so intrabar range structure (needed for barrier
    touches) stays consistent with the transformed close series instead of
    silently reusing untransformed high/low against a transformed mid --
    that would test barrier touches against a level shift they never
    actually experienced."""
    shift = np.log(new_mid) - np.log(mid)
    new_high = high * np.exp(shift)
    new_low = low * np.exp(shift)
    new_open = open_ * np.exp(shift)
    return new_high, new_low, new_open


def demean_series(mid: np.ndarray, window_days: int, bars_per_day: int) -> np.ndarray:
    """return dikurangi mean bergulir 60 hari, reconstructed as a price-like series."""
    r = np.diff(np.log(mid))
    window_bars = window_days * bars_per_day
    roll_mean = pd.Series(r).rolling(window_bars, min_periods=window_bars).mean().values
    demeaned_r = r - np.nan_to_num(roll_mean, nan=0.0)
    demeaned_r = np.concatenate([[0], demeaned_r])
    return mid[0] * np.exp(np.cumsum(demeaned_r))


def sign_flipped_series(mid: np.ndarray) -> np.ndarray:
    r = np.diff(np.log(mid))
    return mid[0] * np.exp(np.cumsum(-r))


def run_arm(mid: np.ndarray, high: np.ndarray, low: np.ndarray, open_: np.ndarray, sigma: np.ndarray, rng: np.random.Generator) -> dict:
    n = len(mid)
    valid_range = n - MAX_HOLD_BARS - 1
    if valid_range < SIGMA_WINDOW + 10:
        return {}

    results = {}
    for k_sl in K_SL_GRID:
        for k_tp in K_TP_GRID:
            be = breakeven_mekanis(k_sl, k_tp)
            for side, direction_val in [("long", 1), ("short", -1)]:
                entries = rng.integers(SIGMA_WINDOW + 1, valid_range, size=N_RANDOM_ENTRIES)
                directions = np.full(N_RANDOM_ENTRIES, direction_val)
                res = triple_barrier_labels(
                    open_, high, low, mid, entries, directions, sigma, k_sl, k_tp, MAX_HOLD_BARS
                )
                valid = res.outcome != 0
                n_valid = valid.sum()
                if n_valid == 0:
                    continue
                hit_rate = (res.outcome[valid] == 1).mean()
                margin_pp = (hit_rate - be) * 100
                net_bps = res.ret[valid].mean() * 1e4
                results[(k_sl, k_tp, side)] = {
                    "breakeven_pct": be * 100,
                    "hit_rate_pct": hit_rate * 100,
                    "margin_pp": margin_pp,
                    "net_bps": net_bps,
                    "n_valid": int(n_valid),
                }
    return results


def main():
    f = BAR_DIR / "XAUUSD_M5.parquet"
    if not f.exists():
        print(f"TIDAK ADA DATA: {f} belum ada. F2 tidak bisa dijalankan.")
        return 1

    bars = pd.read_parquet(f)
    bars = bars.sort_values("bar_time").reset_index(drop=True)
    n_total = len(bars)
    screen_end = int(n_total * 0.20)
    screen = bars.iloc[:screen_end].reset_index(drop=True)
    print(f"Total bar M5: {n_total:,}, partisi SCREEN (20%): {len(screen):,} bar")

    if len(screen) < SIGMA_WINDOW + MAX_HOLD_BARS + 100:
        print(f"DATA SCREEN TERLALU SEDIKIT ({len(screen)} bar) untuk menjalankan gerbang payoff dengan andal.")
        return 1

    mid = screen["mid_close"].values
    high = screen["ask_high"].values if "ask_high" in screen.columns else screen["bid_high"].values
    low = screen["bid_low"].values if "bid_low" in screen.columns else screen["ask_low"].values
    open_ = screen["bid_open"].values if "bid_open" in screen.columns else mid

    sigma = parkinson_sigma(high, low, window=SIGMA_WINDOW)

    bars_per_day = int(24 * 60 / 5)  # M5 bars per day
    demeaned_mid = demean_series(mid, window_days=60, bars_per_day=bars_per_day)
    flipped_mid = sign_flipped_series(mid)

    rng_raw = np.random.default_rng(42)
    rng_dem = np.random.default_rng(42)  # SAME seed -- same random entry timings across arms, only the series differs
    rng_flip = np.random.default_rng(42)

    dem_high, dem_low, dem_open = _log_shift_ohlc(mid, high, low, open_, demeaned_mid)
    flip_high, flip_low, flip_open = _log_shift_ohlc(mid, high, low, open_, flipped_mid)

    print("Menjalankan arm RAW...")
    raw_results = run_arm(mid, high, low, open_, sigma, rng_raw)
    print("Menjalankan arm DEMEANED (arm penentu)...")
    # sigma tetap dari harga RAW (estimator volatilitas adalah properti pasar, bukan artefak
    # transformasi arm) -- dipakai sigma yang sama di ketiga arm; hanya level harga & intrabar
    # range yang digeser mengikuti transformasi masing-masing arm (lihat _log_shift_ohlc).
    demeaned_results = run_arm(demeaned_mid, dem_high, dem_low, dem_open, sigma, rng_dem)
    print("Menjalankan arm SIGN_FLIPPED...")
    flipped_results = run_arm(flipped_mid, flip_high, flip_low, flip_open, sigma, rng_flip)

    lines = ["# F2 -- Gerbang Struktur Payoff\n"]
    lines.append(f"Partisi SCREEN: {len(screen):,} bar M5 (XAUUSD), horizon H60 (12 bar M5), n_random_entries={N_RANDOM_ENTRIES} per sisi per kombinasi\n")

    passed_combos = []
    for k_sl in K_SL_GRID:
        for k_tp in K_TP_GRID:
            for side in ["long", "short"]:
                key = (k_sl, k_tp, side)
                if key not in demeaned_results:
                    continue
                dem = demeaned_results[key]
                raw = raw_results.get(key, {})
                flip = flipped_results.get(key, {})

                margin_ok = dem["margin_pp"] >= MARGIN_MIN_PP
                gap_ok = abs(raw.get("margin_pp", dem["margin_pp"]) - dem["margin_pp"]) <= MAX_RAW_VS_DEMEANED_GAP_PP
                net_bps_ok = dem["net_bps"] > 0
                sign_flip_ok = abs(flip.get("margin_pp", 0) + dem["margin_pp"]) <= SIGN_FLIP_TOLERANCE_PP if flip else False

                if margin_ok and gap_ok and net_bps_ok:
                    passed_combos.append((k_sl, k_tp, side, dem["margin_pp"], dem["net_bps"], sign_flip_ok))

    lines.append(f"## Hasil: {len(passed_combos)} kombinasi (k_sl,k_tp,side) lolos syarat margin/gap/net_bps DEMEANED\n")
    if passed_combos:
        lines.append("| k_sl | k_tp | side | margin_pp (demeaned) | net_bps | sign_flip_ok |")
        lines.append("|---:|---:|---|---:|---:|---|")
        for k_sl, k_tp, side, margin, net_bps, sf_ok in passed_combos:
            lines.append(f"| {k_sl} | {k_tp} | {side} | {margin:.2f} | {net_bps:.2f} | {sf_ok} |")

    long_pass = any(c[2] == "long" for c in passed_combos)
    short_pass = any(c[2] == "short" for c in passed_combos)

    lines.append(f"\n- Ada kombinasi long yang lolos syarat dasar? {long_pass}")
    lines.append(f"- Ada kombinasi SHORT yang lolos syarat dasar? {short_pass} (require_short_side_pass wajib true)")

    if long_pass and not short_pass:
        lines.append("\n**VONIS: long_only_verdict = GAGAL (drift capture), bukan payoff asymmetry. Short side tidak lolos.**")

    final_pass = short_pass and len(passed_combos) > 0
    lines.append(f"\n## Verdict F2: {'LULUS -- ada kombinasi lolos' if final_pass else 'NOL LOLOS -- STOP TOTAL'}")
    if not final_pass:
        lines.append("\nDengan entry acak, tidak ada kombinasi SL/TP yang mengalahkan titik impasnya sendiri ")
        lines.append("(atau hanya sisi long yang lolos, dicurigai drift capture, bukan asimetri mekanis).")
        lines.append("Distribusi return tidak menyediakan asimetri mekanis yang bisa dieksploitasi -- pada data SCREEN yang diuji.")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "F2_payoff_gate.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0 if final_pass else 1


if __name__ == "__main__":
    sys.exit(main())
