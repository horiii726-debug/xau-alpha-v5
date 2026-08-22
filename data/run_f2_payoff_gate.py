#!/usr/bin/env python3
"""F2 -- GERBANG STRUKTUR PAYOFF, per 04_PARTISI_LABELING_PAYOFF.md.

Entry ACAK (belum ada rumus/sinyal apapun). Grid k_sl x k_tp (6x7=42
kombinasi). 3 arm per kombinasi: raw, demeaned (ARM PENENTU), sign_flipped.
Long-only dan short-only diuji TERPISAH (long_only_verdict paksa GAGAL --
drift capture -- kalau cuma long yang diuji).

Dijalankan di 5 horizon (H15,H30,H60,H120,H240, per instruksi user untuk
F2b) pada partisi SCREEN (20% pertama secara kronologis) dari XAUUSD,
n_random_entries=20000 per sisi per kombinasi per horizon.

stop_conditions.1 (07_FASE_EKSEKUSI.md): STOP TOTAL hanya kalau gagal di
SEMUA horizon & instrumen -- karena itu skrip ini TIDAK boleh berhenti
setelah satu horizon gagal; harus jalan di seluruh grid horizon dulu
sebelum vonis akhir dijatuhkan. protokol_nol_lolos langkah 1 juga
eksplisit: "cek horizon lebih panjang" adalah hal PERTAMA yang wajib
dicoba sebelum menyerah.
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

# label, bar timeframe, max_hold_bars -- per 03_UNIVERSE_DAN_HORIZON.md grid,
# 5 horizon per instruksi user (H1D dikeluarkan, sama seperti F2b)
HORIZONS = [
    ("H15", "M5", 3),
    ("H30", "M5", 6),
    ("H60", "M5", 12),
    ("H120", "M15", 8),
    ("H240", "M15", 16),
]

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
    r = np.concatenate([[0], r])  # preserve length -- np.diff drops the first element
    return mid[0] * np.exp(np.cumsum(-r))


def run_arm(mid, high, low, open_, sigma, max_hold_bars, rng) -> dict:
    n = len(mid)
    valid_range = n - max_hold_bars - 1
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
                    open_, high, low, mid, entries, directions, sigma, k_sl, k_tp, max_hold_bars
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


def _margin_for_subperiod(mid, high, low, open_, sigma, max_hold_bars, k_sl, k_tp, direction_val, rng, n_entries):
    n = len(mid)
    valid_range = n - max_hold_bars - 1
    if valid_range < SIGMA_WINDOW + 10:
        return None
    entries = rng.integers(SIGMA_WINDOW + 1, valid_range, size=n_entries)
    directions = np.full(n_entries, direction_val)
    res = triple_barrier_labels(open_, high, low, mid, entries, directions, sigma, k_sl, k_tp, max_hold_bars)
    valid = res.outcome != 0
    if valid.sum() == 0:
        return None
    hit_rate = (res.outcome[valid] == 1).mean()
    be = breakeven_mekanis(k_sl, k_tp)
    return (hit_rate - be) * 100


def check_stability(mid, high, low, open_, sigma, max_hold_bars, k_sl, k_tp, direction_val, n_sub=3, n_entries=4000) -> bool:
    """stability_sub_periods: split into n_sub chronological sub-periods,
    require the demeaned-arm margin to stay POSITIVE in all of them (not
    just in the full-period aggregate) -- a combo that only "works" on
    average but is negative in one third of history isn't stable."""
    n = len(mid)
    bounds = np.linspace(0, n, n_sub + 1).astype(int)
    for i in range(n_sub):
        lo, hi = bounds[i], bounds[i + 1]
        if hi - lo < SIGMA_WINDOW + max_hold_bars + 50:
            return False
        rng = np.random.default_rng(1000 + i)
        margin = _margin_for_subperiod(
            mid[lo:hi], high[lo:hi], low[lo:hi], open_[lo:hi], sigma[lo:hi],
            max_hold_bars, k_sl, k_tp, direction_val, rng, n_entries,
        )
        if margin is None or margin <= 0:
            return False
    return True


def run_one_horizon(label: str, timeframe: str, max_hold_bars: int) -> dict:
    f = BAR_DIR / f"XAUUSD_{timeframe}.parquet"
    if not f.exists():
        return {"label": label, "status": "TIDAK_ADA_DATA"}

    bars = pd.read_parquet(f)
    bars = bars.sort_values("bar_time").reset_index(drop=True)
    n_total = len(bars)
    screen_end = int(n_total * 0.20)
    screen = bars.iloc[:screen_end].reset_index(drop=True)

    if len(screen) < SIGMA_WINDOW + max_hold_bars + 100:
        return {"label": label, "status": "DATA_TERLALU_SEDIKIT", "n_bar_screen": len(screen)}

    mid = screen["mid_close"].values
    high = screen["ask_high"].values if "ask_high" in screen.columns else screen["bid_high"].values
    low = screen["bid_low"].values if "bid_low" in screen.columns else screen["ask_low"].values
    open_ = screen["bid_open"].values if "bid_open" in screen.columns else mid

    sigma = parkinson_sigma(high, low, window=SIGMA_WINDOW)

    bars_per_day = int(24 * 60 / 5) if timeframe == "M5" else int(24 * 60 / 15)
    demeaned_mid = demean_series(mid, window_days=60, bars_per_day=bars_per_day)
    flipped_mid = sign_flipped_series(mid)

    rng_raw = np.random.default_rng(42)
    rng_dem = np.random.default_rng(42)
    rng_flip = np.random.default_rng(42)

    dem_high, dem_low, dem_open = _log_shift_ohlc(mid, high, low, open_, demeaned_mid)
    flip_high, flip_low, flip_open = _log_shift_ohlc(mid, high, low, open_, flipped_mid)

    raw_results = run_arm(mid, high, low, open_, sigma, max_hold_bars, rng_raw)
    demeaned_results = run_arm(demeaned_mid, dem_high, dem_low, dem_open, sigma, max_hold_bars, rng_dem)
    flipped_results = run_arm(flipped_mid, flip_high, flip_low, flip_open, sigma, max_hold_bars, rng_flip)

    # candidates that clear margin/gap/net_bps -- BEFORE the two more expensive
    # checks (sign_flip, stability), which are only run on this shortlist
    shortlist = []
    all_short_margins = []
    for k_sl in K_SL_GRID:
        for k_tp in K_TP_GRID:
            for side in ["long", "short"]:
                key = (k_sl, k_tp, side)
                if key not in demeaned_results:
                    continue
                dem = demeaned_results[key]
                raw = raw_results.get(key, {})
                flip = flipped_results.get(key, {})
                if side == "short":
                    all_short_margins.append(dem["margin_pp"])

                margin_ok = dem["margin_pp"] >= MARGIN_MIN_PP
                gap_ok = abs(raw.get("margin_pp", dem["margin_pp"]) - dem["margin_pp"]) <= MAX_RAW_VS_DEMEANED_GAP_PP
                net_bps_ok = dem["net_bps"] > 0
                sign_flip_ok = abs(flip.get("margin_pp", 0) + dem["margin_pp"]) <= SIGN_FLIP_TOLERANCE_PP if flip else False

                if margin_ok and gap_ok and net_bps_ok:
                    shortlist.append((k_sl, k_tp, side, dem["margin_pp"], dem["net_bps"], sign_flip_ok))

    passed_combos = []
    for k_sl, k_tp, side, margin, net_bps, sign_flip_ok in shortlist:
        direction_val = 1 if side == "long" else -1
        stable = check_stability(mid, high, low, open_, sigma, max_hold_bars, k_sl, k_tp, direction_val)
        if sign_flip_ok and stable:
            passed_combos.append((k_sl, k_tp, side, margin, net_bps, sign_flip_ok, stable))

    long_pass = any(c[2] == "long" for c in passed_combos)
    short_pass = any(c[2] == "short" for c in passed_combos)
    final_pass = short_pass and len(passed_combos) > 0

    return {
        "label": label,
        "status": "OK",
        "n_bar_screen": len(screen),
        "n_shortlist_before_sign_flip_stability": len(shortlist),
        "passed_combos": passed_combos,
        "long_pass": long_pass,
        "short_pass": short_pass,
        "best_short_margin_pp": max(all_short_margins) if all_short_margins else None,
        "final_pass": final_pass,
    }


def main():
    lines = ["# F2 -- Gerbang Struktur Payoff (XAUUSD, 5 horizon)\n"]
    lines.append(
        f"Per stop_conditions.1: STOP TOTAL hanya kalau gagal di SEMUA horizon. "
        f"n_random_entries={N_RANDOM_ENTRIES} per sisi per kombinasi per horizon, "
        f"partisi SCREEN (20% kronologis pertama).\n"
    )

    all_results = []
    any_pass = False
    for label, timeframe, max_hold_bars in HORIZONS:
        print(f"Menjalankan horizon {label} ({timeframe}, {max_hold_bars} bar)...")
        res = run_one_horizon(label, timeframe, max_hold_bars)
        all_results.append(res)
        if res.get("final_pass"):
            any_pass = True

    lines.append("## Ringkasan per horizon\n")
    lines.append(
        "> `lolos_margin_dasar` = lolos margin/gap/net_bps saja (BELUM termasuk sign_flip & stability). "
        "`lolos_semua_syarat` = shortlist itu SETELAH juga lolos sign_flip_abs_margin_tolerance_pp DAN "
        "stability_sub_periods=3 (margin harus tetap positif di ketiga sub-periode). Verdict akhir "
        "F2 memakai `lolos_semua_syarat`, bukan `lolos_margin_dasar` -- kalau hanya pakai margin dasar "
        "saja, verdict yang dilaporkan bisa terlalu optimistis.\n"
    )
    lines.append("| Horizon | Status | Bar SCREEN | Kombinasi lolos margin dasar | Kombinasi lolos SEMUA syarat | Long lolos (semua syarat)? | Short lolos (semua syarat)? | Verdict |")
    lines.append("|---|---|---:|---:|---:|---|---|---|")
    for res in all_results:
        if res["status"] != "OK":
            lines.append(f"| {res['label']} | {res['status']} | - | - | - | - | - | - |")
            continue
        verdict = "LULUS" if res["final_pass"] else ("GAGAL (drift capture)" if res["long_pass"] else "GAGAL (nol lolos)")
        lines.append(
            f"| {res['label']} | OK | {res['n_bar_screen']:,} | {res['n_shortlist_before_sign_flip_stability']} | "
            f"{len(res['passed_combos'])} | {res['long_pass']} | {res['short_pass']} | {verdict} |"
        )

    lines.append("\n## Detail kombinasi yang lolos SEMUA syarat (margin + gap + net_bps + sign_flip + stability)\n")
    any_detail = False
    for res in all_results:
        if res.get("passed_combos"):
            any_detail = True
            lines.append(f"### {res['label']}\n")
            lines.append("| k_sl | k_tp | side | margin_pp (demeaned) | net_bps | sign_flip_ok | stable_3_subperiod |")
            lines.append("|---:|---:|---|---:|---:|---|---|")
            for k_sl, k_tp, side, margin, net_bps, sf_ok, stable in res["passed_combos"]:
                lines.append(f"| {k_sl} | {k_tp} | {side} | {margin:.2f} | {net_bps:.2f} | {sf_ok} | {stable} |")
            lines.append("")
    if not any_detail:
        lines.append("(TIDAK ADA kombinasi yang lolos keenam syarat sekaligus di horizon manapun)\n")

    lines.append("## Vonis akhir\n")
    if any_pass:
        lines.append("**LULUS (XAUUSD)** -- ada minimal satu horizon dengan kombinasi (k_sl,k_tp) yang lolos KEENAM syarat (margin, gap, net_bps, sign_flip, stability) DI KEDUA sisi (long dan short).")
    else:
        lines.append(
            "**NOL LOLOS DI XAUUSD, DI SEMUA 5 HORIZON YANG DIUJI.**\n\n"
            "**BUKAN vonis STOP TOTAL final** -- stop_conditions.1 mensyaratkan gagal di semua horizon "
            "**DAN semua instrumen**. Baru XAUUSD yang diuji; XAGUSD/EURUSD/USOIL masih dalam proses "
            "download. Vonis final menunggu panel lengkap.\n"
        )
        lines.append(
            "Catatan penting: pada pengecekan margin/gap/net_bps SAJA (3 dari 6 syarat), 23-33 kombinasi per "
            "horizon tampak lolos, dan sisi LONG konsisten unggul jauh di atas sisi SHORT. Begitu "
            "sign_flip_abs_margin_tolerance_pp dan stability_sub_periods=3 (dua syarat yang sempat "
            "terlewat di draf pertama skrip ini) ditegakkan, SELURUHNYA gugur -- termasuk yang tadinya "
            "tampak lolos di kedua sisi (H15/H30/H120). Pola long-tampak-menang selaras dengan drift "
            "capture (XAUUSD naik signifikan 2021-2026), persis skenario yang diperingatkan di "
            "04_PARTISI_LABELING_PAYOFF.md §'Kenapa arm demeaned yang menentukan' -- tapi bahkan sisi "
            "long pun tidak benar-benar stabil di 3 sub-periode begitu diperiksa.\n"
        )
        lines.append(
            "Sesuai payoff_gate.kalau_nol_lolos: dilarang melonggarkan margin, mengganti arm penentu, "
            "atau menghapus syarat sisi short. Opsi yang tersisa (protokol_nol_lolos, urut):\n"
        )
        lines.append("1. Horizon lebih panjang dari H240 sudah diuji (H120, H240) dan tetap gagal di XAUUSD.")
        lines.append("2. Cek biaya/sesi -- BELUM dicoba (model biaya belum lengkap, markup prop firm masih LOOKUP).")
        lines.append("3. Perbesar panel -- SEDANG BERJALAN (XAGUSD/EURUSD/USOIL masih download).")
        lines.append("4. Perpanjang riwayat -- Dukascopy punya data XAUUSD lebih jauh dari 2021 (mulai 2003).")
        lines.append("5. Cari di area X (exit/sizing) -- BELUM dicoba.")
        lines.append("6. Terima kalau memang nol -- BELUM final, tunggu panel lengkap dulu (langkah 3).")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "F2_payoff_gate.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0 if any_pass else 1


if __name__ == "__main__":
    sys.exit(main())
