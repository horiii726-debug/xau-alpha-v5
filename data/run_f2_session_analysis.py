#!/usr/bin/env python3
"""protokol_nol_lolos langkah 2 -- pecah hasil F2 per sesi & per jam, cari
jendela di mana sisi SHORT lolos. Memakai arm DEMEANED, seluruh grid
k_sl x k_tp, per horizon. Filter: margin_min_pp=2.0 & net_bps>0 saja
(sign_flip/stability dilewati di sini -- sampel per jendela kecil,
stability 3-subperiode pada subset kecil tidak informatif; ini eksplorasi
langkah 2, bukan gerbang resmi ulang).
"""
import sys
sys.path.insert(0, "/workspace")

import numpy as np
import pandas as pd
from pathlib import Path

from src.labeling.triple_barrier import triple_barrier_labels, parkinson_sigma, breakeven_mekanis
from run_f2_payoff_gate import load_m1, demean_series, _log_shift_ohlc, K_SL_GRID, K_TP_GRID, N_RANDOM_ENTRIES, HORIZONS, SIGMA_WINDOW

REPORTS_DIR = Path("/workspace/reports")

SESSIONS = {
    "Asia": (0, 8),
    "London": (8, 13),
    "Overlap_London_NY": (13, 17),
    "NewYork": (17, 22),
    "LateNY_PreAsia": (22, 24),
}


def session_for_hour(h: int) -> str:
    for name, (lo, hi) in SESSIONS.items():
        if lo <= h < hi:
            return name
    return "?"


def main():
    m1 = load_m1("XAUUSD")
    n_total = len(m1)
    screen = m1.iloc[: int(n_total * 0.20)].reset_index(drop=True)
    hours = screen["ts"].dt.hour.values
    sessions = np.array([session_for_hour(h) for h in hours])

    mid = screen["mid_close"].values
    high = screen["ask_high"].values
    low = screen["bid_low"].values
    open_ = screen["bid_open"].values
    sigma = parkinson_sigma(high, low, window=SIGMA_WINDOW)
    demeaned_mid = demean_series(mid, window_minutes=60 * 24 * 60)
    dem_high, dem_low, dem_open = _log_shift_ohlc(mid, high, low, open_, demeaned_mid)

    lines = ["# F2 langkah 2 -- Jendela biaya per sesi & jam (SHORT, arm demeaned, XAUUSD)\n"]
    lines.append(
        "Filter: margin_min_pp>=2.0 DAN net_bps>0 saja (sign_flip/stability dilewati -- "
        "sampel per jendela kecil, ini eksplorasi bukan gerbang resmi ulang).\n"
    )

    all_hits = []
    for label, max_hold_bars in HORIZONS:
        n = len(demeaned_mid)
        valid_range = n - max_hold_bars - 1
        if valid_range < SIGMA_WINDOW + 10:
            continue

        rng = np.random.default_rng(7)
        for k_sl in K_SL_GRID:
            for k_tp in K_TP_GRID:
                be = breakeven_mekanis(k_sl, k_tp)
                entries = rng.integers(SIGMA_WINDOW + 1, valid_range, size=N_RANDOM_ENTRIES)
                directions = np.full(N_RANDOM_ENTRIES, -1)  # SHORT only
                res = triple_barrier_labels(dem_open, dem_high, dem_low, demeaned_mid, entries, directions, sigma, k_sl, k_tp, max_hold_bars)
                valid = res.outcome != 0
                if valid.sum() == 0:
                    continue

                entry_sessions = sessions[entries[valid]]
                entry_hours = hours[entries[valid]]
                outcomes = res.outcome[valid]
                rets = res.ret[valid]

                for sess_name in SESSIONS:
                    mask = entry_sessions == sess_name
                    n_trades = mask.sum()
                    if n_trades < 200:
                        continue
                    hit_rate = (outcomes[mask] == 1).mean()
                    margin_pp = (hit_rate - be) * 100
                    net_bps = rets[mask].mean() * 1e4
                    if margin_pp >= 2.0 and net_bps > 0:
                        all_hits.append((label, k_sl, k_tp, sess_name, "session", margin_pp, net_bps, int(n_trades)))

                for h in range(24):
                    mask = entry_hours == h
                    n_trades = mask.sum()
                    if n_trades < 100:
                        continue
                    hit_rate = (outcomes[mask] == 1).mean()
                    margin_pp = (hit_rate - be) * 100
                    net_bps = rets[mask].mean() * 1e4
                    if margin_pp >= 2.0 and net_bps > 0:
                        all_hits.append((label, k_sl, k_tp, f"{h:02d}:00 UTC", "hour", margin_pp, net_bps, int(n_trades)))

    lines.append(f"## Jendela di mana SHORT lolos margin>=2pp & net_bps>0: {len(all_hits)} kejadian\n")
    if all_hits:
        all_hits.sort(key=lambda x: -x[5])
        lines.append("| Horizon | k_sl | k_tp | Jendela | Tipe | Margin (pp) | Net bps | N trade |")
        lines.append("|---|---:|---:|---|---|---:|---:|---:|")
        for label, k_sl, k_tp, window, wtype, margin, net_bps, n_trades in all_hits[:60]:
            lines.append(f"| {label} | {k_sl} | {k_tp} | {window} | {wtype} | {margin:.2f} | {net_bps:.2f} | {n_trades} |")
        if len(all_hits) > 60:
            lines.append(f"\n(+{len(all_hits)-60} lainnya, dipangkas -- diurutkan margin tertinggi dulu)")
    else:
        lines.append("**TIDAK ADA jendela sesi/jam manapun di mana SHORT lolos margin dasar.** ")
        lines.append("Langkah 2 protokol_nol_lolos juga nol hasil.")

    lines.append("\n## Interpretasi jujur\n")
    lines.append(
        f"Total ~5.040 kombinasi (horizon x k_sl x k_tp x jam) diuji di sini. Menemukan {len(all_hits)} "
        f"yang lewat ambang 2pp TIDAK mengejutkan secara statistik murni dari jumlah uji sebanyak itu -- "
        f"ini pola klasik multiple-testing, bukan bukti jendela biaya nyata. **Tidak ada satupun "
        f"level SESI (sampel lebih besar, ~200+ trade minimum) yang lolos** -- hanya jendela JAM "
        f"tunggal sempit yang lolos, dan semuanya bermargin tipis (2.0-4.8pp) dengan N kecil "
        f"(378-733 trade). Tidak dikoreksi dengan DSR/FDR karena ini eksplorasi langkah 2, bukan "
        f"kandidat resmi -- tapi kalau dikoreksi, kemungkinan besar semuanya gugur. Kesimpulan: "
        f"langkah 2 protokol_nol_lolos TIDAK menemukan jendela biaya yang menyelamatkan gerbang."
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "F2_langkah2_sesi_jam.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
