#!/usr/bin/env python3
"""F2 -- GERBANG STRUKTUR PAYOFF, per 04_PARTISI_LABELING_PAYOFF.md.

Entry ACAK (belum ada rumus/sinyal apapun). Grid k_sl x k_tp (6x7=42
kombinasi). 3 arm per kombinasi: raw, demeaned (ARM PENENTU), sign_flipped.
Long-only dan short-only diuji TERPISAH (long_only_verdict paksa GAGAL --
drift capture -- kalau cuma long yang diuji).

REVISI: barrier touch dicek pada bar M1 (bukan M5/M15 teragregasi) --
lebih akurat karena tie-break SL/TP-tersentuh-bersamaan hanya benar-benar
ambigu kalau terjadi di bar M1 yang SAMA. Mengecek di M5/M15 membuat kasus
"ambigu" jauh lebih sering dari yang sebenarnya (satu window 5-15 menit
gampang menyentuh dua-duanya meski urutannya sebenarnya jelas di level
menit). max_hold_bars sekarang = jumlah menit horizon secara langsung
(H15=15 bar M1, dst).

Dijalankan pada partisi SCREEN (20% pertama secara kronologis) dari
XAUUSD, n_random_entries=20000 per sisi per kombinasi per horizon.
"""
import sys
sys.path.insert(0, "/workspace")

import numpy as np
import pandas as pd
from pathlib import Path

from src.labeling.triple_barrier import triple_barrier_labels, parkinson_sigma, breakeven_mekanis

RAW_DIR = Path("/workspace/data/raw_candles")
REPORTS_DIR = Path("/workspace/reports")

K_SL_GRID = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
K_TP_GRID = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
N_RANDOM_ENTRIES = 20000

# label -> horizon in MINUTES = max_hold_bars langsung di M1
HORIZONS = [("H15", 15), ("H30", 30), ("H60", 60), ("H120", 120), ("H240", 240)]

SIGMA_WINDOW = 96  # V01_PARKINSON window (bar M1), mid grid choice
MARGIN_MIN_PP = 2.0
MAX_RAW_VS_DEMEANED_GAP_PP = 1.0
SIGN_FLIP_TOLERANCE_PP = 0.5
STABILITY_SUB_PERIODS = 3


def load_m1(symbol: str) -> pd.DataFrame:
    files = sorted((RAW_DIR / symbol).glob(f"{symbol}_*.parquet"))
    frames = []
    for f in files:
        df = pd.read_parquet(f)
        if len(df) > 0 and "ts_s" in df.columns:
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["ts"] = pd.to_datetime(out["ts_s"], unit="s", utc=True)
    out.sort_values("ts", inplace=True)
    out.reset_index(drop=True, inplace=True)
    out["mid_close"] = (out["bid_close"] + out["ask_close"]) / 2.0
    return out


def _log_shift_ohlc(mid, high, low, open_, new_mid):
    """Apply the SAME per-bar log-shift used to turn `mid` into `new_mid`
    to high/low/open too, so intrabar range structure (needed for barrier
    touches) stays consistent with the transformed close series instead of
    silently reusing untransformed high/low against a transformed mid."""
    shift = np.log(new_mid) - np.log(mid)
    return high * np.exp(shift), low * np.exp(shift), open_ * np.exp(shift)


def demean_series(mid: np.ndarray, window_minutes: int) -> np.ndarray:
    r = np.diff(np.log(mid))
    roll_mean = pd.Series(r).rolling(window_minutes, min_periods=window_minutes).mean().values
    demeaned_r = r - np.nan_to_num(roll_mean, nan=0.0)
    demeaned_r = np.concatenate([[0], demeaned_r])
    return mid[0] * np.exp(np.cumsum(demeaned_r))


def sign_flipped_series(mid: np.ndarray) -> np.ndarray:
    r = np.diff(np.log(mid))
    r = np.concatenate([[0], r])
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
                res = triple_barrier_labels(open_, high, low, mid, entries, directions, sigma, k_sl, k_tp, max_hold_bars)
                valid = res.outcome != 0
                n_valid = valid.sum()
                if n_valid == 0:
                    continue
                hit_rate = (res.outcome[valid] == 1).mean()
                margin_pp = (hit_rate - be) * 100
                net_bps = res.ret[valid].mean() * 1e4
                ambiguous_pct = res.ambiguous[valid].mean() * 100
                results[(k_sl, k_tp, side)] = {
                    "breakeven_pct": be * 100, "hit_rate_pct": hit_rate * 100,
                    "margin_pp": margin_pp, "net_bps": net_bps,
                    "n_valid": int(n_valid), "ambiguous_pct": ambiguous_pct,
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
    n = len(mid)
    bounds = np.linspace(0, n, n_sub + 1).astype(int)
    for i in range(n_sub):
        lo, hi = bounds[i], bounds[i + 1]
        if hi - lo < SIGMA_WINDOW + max_hold_bars + 50:
            return False
        rng = np.random.default_rng(1000 + i)
        margin = _margin_for_subperiod(mid[lo:hi], high[lo:hi], low[lo:hi], open_[lo:hi], sigma[lo:hi], max_hold_bars, k_sl, k_tp, direction_val, rng, n_entries)
        if margin is None or margin <= 0:
            return False
    return True


def run_one_horizon(label: str, max_hold_bars: int, screen: pd.DataFrame) -> dict:
    if len(screen) < SIGMA_WINDOW + max_hold_bars + 100:
        return {"label": label, "status": "DATA_TERLALU_SEDIKIT", "n_bar_screen": len(screen)}

    mid = screen["mid_close"].values
    high = screen["ask_high"].values
    low = screen["bid_low"].values
    open_ = screen["bid_open"].values

    sigma = parkinson_sigma(high, low, window=SIGMA_WINDOW)
    demeaned_mid = demean_series(mid, window_minutes=60 * 24 * 60)  # 60 hari dalam menit
    flipped_mid = sign_flipped_series(mid)

    rng_raw = np.random.default_rng(42)
    rng_dem = np.random.default_rng(42)
    rng_flip = np.random.default_rng(42)

    dem_high, dem_low, dem_open = _log_shift_ohlc(mid, high, low, open_, demeaned_mid)
    flip_high, flip_low, flip_open = _log_shift_ohlc(mid, high, low, open_, flipped_mid)

    raw_results = run_arm(mid, high, low, open_, sigma, max_hold_bars, rng_raw)
    demeaned_results = run_arm(demeaned_mid, dem_high, dem_low, dem_open, sigma, max_hold_bars, rng_dem)
    flipped_results = run_arm(flipped_mid, flip_high, flip_low, flip_open, sigma, max_hold_bars, rng_flip)

    shortlist = []
    all_short_margins = []
    all_ambiguous_pcts = []
    for k_sl in K_SL_GRID:
        for k_tp in K_TP_GRID:
            for side in ["long", "short"]:
                key = (k_sl, k_tp, side)
                if key not in demeaned_results:
                    continue
                dem = demeaned_results[key]
                raw = raw_results.get(key, {})
                flip = flipped_results.get(key, {})
                all_ambiguous_pcts.append(dem["ambiguous_pct"])
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

    return {
        "label": label, "status": "OK", "n_bar_screen": len(screen),
        "n_shortlist_before_sign_flip_stability": len(shortlist),
        "passed_combos": passed_combos, "long_pass": long_pass, "short_pass": short_pass,
        "best_short_margin_pp": max(all_short_margins) if all_short_margins else None,
        "final_pass": short_pass and len(passed_combos) > 0,
        "avg_ambiguous_pct": float(np.mean(all_ambiguous_pcts)) if all_ambiguous_pcts else None,
        "max_ambiguous_pct": float(np.max(all_ambiguous_pcts)) if all_ambiguous_pcts else None,
    }


def main():
    print("Memuat M1 XAUUSD...")
    m1 = load_m1("XAUUSD")
    print(f"{len(m1):,} bar M1 dimuat")
    n_total = len(m1)
    screen_end = int(n_total * 0.20)
    screen = m1.iloc[:screen_end].reset_index(drop=True)
    print(f"Partisi SCREEN: {len(screen):,} bar M1 ({len(screen)/1440:.1f} hari)")

    lines = ["# F2 -- Gerbang Struktur Payoff (XAUUSD, 5 horizon, granularitas M1)\n"]
    lines.append(
        f"Barrier touch dicek pada bar M1 (bukan M5/M15 teragregasi) supaya tie-break "
        f"SL-duluan-kalau-ambigu hanya diterapkan pada kasus yang BENAR-BENAR ambigu di "
        f"level menit. Partisi SCREEN: {len(screen):,} bar M1 ({len(screen)/1440:.1f} hari). "
        f"n_random_entries={N_RANDOM_ENTRIES} per sisi per kombinasi per horizon.\n"
    )

    all_results = []
    any_pass = False
    for label, max_hold_bars in HORIZONS:
        print(f"Menjalankan horizon {label} ({max_hold_bars} bar M1)...")
        res = run_one_horizon(label, max_hold_bars, screen)
        all_results.append(res)
        if res.get("final_pass"):
            any_pass = True

    lines.append("## Kasus ambigu (SL & TP kesentuh di bar M1 yang sama) per horizon\n")
    lines.append("| Horizon | Rata-rata % trade ambigu (semua kombinasi) | Maksimum % trade ambigu |")
    lines.append("|---|---:|---:|")
    for res in all_results:
        if res["status"] != "OK":
            continue
        avg_a = f"{res['avg_ambiguous_pct']:.3f}%" if res["avg_ambiguous_pct"] is not None else "-"
        max_a = f"{res['max_ambiguous_pct']:.3f}%" if res["max_ambiguous_pct"] is not None else "-"
        lines.append(f"| {res['label']} | {avg_a} | {max_a} |")
    lines.append("")

    lines.append("## Ringkasan per horizon\n")
    lines.append(
        "> `lolos_margin_dasar` = lolos margin/gap/net_bps saja. `lolos_semua_syarat` = "
        "shortlist itu SETELAH juga lolos sign_flip_abs_margin_tolerance_pp DAN "
        "stability_sub_periods=3.\n"
    )
    lines.append("| Horizon | Status | Bar SCREEN | Lolos margin dasar | Lolos SEMUA syarat | Long lolos? | Short lolos? | Verdict |")
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

    lines.append("\n## Detail kombinasi yang lolos SEMUA syarat\n")
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
        lines.append("**LULUS (XAUUSD)** -- ada minimal satu horizon dengan kombinasi yang lolos keenam syarat DI KEDUA sisi.")
    else:
        lines.append(
            "**NOL LOLOS DI XAUUSD, DI SEMUA 5 HORIZON YANG DIUJI (granularitas M1).**\n\n"
            "Bukan vonis stop_conditions.1 final -- itu butuh gagal di semua instrumen juga. "
            "Panel: XAUUSD lengkap, XAGUSD sebagian (~609/1826 hari), EURUSD/USOIL kosong "
            "(download dihentikan atas instruksi user). Hasil selanjutnya (F4-F7) berjalan "
            "sebagai EKSPLORASI pada panel tidak lengkap, ditandai SINGLE_ASSET_ONLY / "
            "UNDERPOWERED_PANEL sesuai instruksi.\n"
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "F2_payoff_gate.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0 if any_pass else 1


if __name__ == "__main__":
    sys.exit(main())
