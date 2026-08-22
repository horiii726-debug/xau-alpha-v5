#!/usr/bin/env python3
"""F4 -- Divisi estimasi V (volatilitas) & Q (spread/likuiditas), MCS
alpha=0.10, tie-break tersederhana. Dijalankan di XAUUSD SCREEN partition
(M1). Divisi T (intensitas tick) BLOKIR -- perlu timestamp kedatangan
tick individual, yang tidak ada lagi setelah beralih ke candle M1 (demi
kecepatan download); dilaporkan sebagai gap, bukan dilewati diam-diam.

Target V: QLIKE terhadap realized variance PERIODE BERIKUTNYA (forward
60 menit, causal split -- target dihitung dari bar SETELAH t, model hanya
memakai data SAMPAI DAN TERMASUK t).
Target Q: |estimasi - spread_realized_bps| (MAE), spread_realized diukur
langsung dari bid/ask M1 (bukan tick, tapi ini data terhalus yang ada
setelah beralih ke candle).
"""
import sys
sys.path.insert(0, "/workspace")

import numpy as np
import pandas as pd
from pathlib import Path

from src.formulas import division_v as v
from src.formulas import division_q as q
from src.validation.mcs import qlike_loss, model_confidence_set

REPORTS_DIR = Path("/workspace/reports")
FORWARD_WINDOW = 60  # menit, target RV = variance realisasi 60 menit ke depan


def load_m1_full(symbol: str) -> pd.DataFrame:
    raw_dir = Path("/workspace/data/raw_candles") / symbol
    files = sorted(raw_dir.glob(f"{symbol}_*.parquet"))
    frames = [pd.read_parquet(f) for f in files]
    frames = [d for d in frames if len(d) > 0]
    out = pd.concat(frames, ignore_index=True)
    out["ts"] = pd.to_datetime(out["ts_s"], unit="s", utc=True)
    out.sort_values("ts", inplace=True)
    out.reset_index(drop=True, inplace=True)
    out["mid_close"] = (out["bid_close"] + out["ask_close"]) / 2.0
    out["spread_bps"] = (out["ask_close"] - out["bid_close"]) / out["mid_close"] * 1e4
    return out


def forward_realized_variance(mid: np.ndarray, window: int) -> np.ndarray:
    """RV[t] = sum(r_i^2) for i in (t, t+window] -- STRICTLY forward, bar t's
    target uses only FUTURE bars, never bar t itself or earlier (this is
    the label being forecast, not a feature -- causal for the MODEL, which
    only sees data up to t; the target itself is allowed to be forward by
    construction, same logic as triple-barrier labels)."""
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    r2 = r**2
    n = len(r2)
    fwd_sum = np.full(n, np.nan)
    cumsum = np.concatenate([[0], np.cumsum(r2)])
    for t in range(n - window):
        fwd_sum[t] = cumsum[t + 1 + window] - cumsum[t + 1]
    return fwd_sum


def main():
    print("Memuat M1 XAUUSD penuh...")
    m1 = load_m1_full("XAUUSD")
    n_total = len(m1)
    screen = m1.iloc[: int(n_total * 0.20)].reset_index(drop=True)
    print(f"Partisi SCREEN: {len(screen):,} bar M1")

    mid = screen["mid_close"].values
    high = screen["ask_high"].values
    low = screen["bid_low"].values
    open_ = screen["bid_open"].values
    close = mid
    spread_bps_actual = screen["spread_bps"].values

    print("Menghitung target: forward realized variance 60 menit...")
    target_rv = forward_realized_variance(mid, FORWARD_WINDOW)

    lines = ["# F4 -- Divisi Estimasi (V, Q, T)\n"]
    lines.append(f"XAUUSD, partisi SCREEN, {len(screen):,} bar M1. SINGLE_ASSET_ONLY -- panel belum lengkap.\n")
    lines.append("## Divisi T -- BLOKIR\n")
    lines.append(
        "T01-T10 (Hawkes, ACD, dispersion index, tick-clock) semuanya butuh **timestamp kedatangan "
        "tick individual** (tick_time). Setelah beralih dari tick .bi5 ke candle M1 (demi kecepatan "
        "download -- lihat commit sebelumnya), data itu tidak ada lagi; M1 candle hanya menyimpan "
        "OHLC + volume agregat per menit, bukan waktu antar-tick. **Divisi T tidak dijalankan di F4 "
        "ini** -- bukan dilewati diam-diam, ini gap data yang nyata dan perlu diputuskan: unduh ulang "
        "tick untuk sampel kecil kalau T dianggap penting, atau terima T kosong untuk eksplorasi ini.\n"
    )

    # ---------------- Divisi V ----------------
    print("Menjalankan Divisi V...")
    v_candidates = {}
    v_nparams = {}
    for window in [12, 48, 96]:
        v_candidates[f"V01_PARKINSON_w{window}"] = v.v01_parkinson(high, low, window) ** 2
        v_nparams[f"V01_PARKINSON_w{window}"] = 1
        v_candidates[f"V02_GARMAN_KLASS_w{window}"] = v.v02_garman_klass(high, low, open_, close, window) ** 2
        v_nparams[f"V02_GARMAN_KLASS_w{window}"] = 1
        v_candidates[f"V03_ROGERS_SATCHELL_w{window}"] = v.v03_rogers_satchell(high, low, open_, close, window) ** 2
        v_nparams[f"V03_ROGERS_SATCHELL_w{window}"] = 1
        v_candidates[f"V04_YANG_ZHANG_w{window}"] = v.v04_yang_zhang(high, low, open_, close, window) ** 2
        v_nparams[f"V04_YANG_ZHANG_w{window}"] = 1
        v_candidates[f"V05_CLOSE_TO_CLOSE_w{window}"] = v.v05_close_to_close(close, window) ** 2
        v_nparams[f"V05_CLOSE_TO_CLOSE_w{window}"] = 1
        v_candidates[f"V10_REALIZED_SEMIVAR_w{window}"] = np.abs(v.v10_realized_semivariance(close, window))
        v_nparams[f"V10_REALIZED_SEMIVAR_w{window}"] = 1

    for window in [48, 96]:
        v_candidates[f"V07_BIPOWER_w{window}"] = v.v07_bipower_variation(close, window)
        v_nparams[f"V07_BIPOWER_w{window}"] = 1
        v_candidates[f"V08_MEDRV_w{window}"] = v.v08_medrv(close, window)
        v_nparams[f"V08_MEDRV_w{window}"] = 1
        v_candidates[f"V09_MINRV_w{window}"] = v.v09_minrv(close, window)
        v_nparams[f"V09_MINRV_w{window}"] = 1

    for lam in [0.94, 0.97, 0.99]:
        v_candidates[f"V12_EWMA_l{lam}"] = v.v12_ewma_variance(close, lam) ** 2
        v_nparams[f"V12_EWMA_l{lam}"] = 1

    v_candidates["V13_GARCH11_BASELINE"] = v.v13_garch11_baseline(close) ** 2
    v_nparams["V13_GARCH11_BASELINE"] = 4

    print(f"{len(v_candidates)} varian V dihitung. Menghitung QLIKE loss...")
    v_losses = {}
    for name, sigma2 in v_candidates.items():
        n = min(len(sigma2), len(target_rv))
        loss = qlike_loss(target_rv[:n], sigma2[:n])
        v_losses[name] = loss

    print("Menjalankan MCS untuk V...")
    v_mcs = model_confidence_set(v_losses, v_nparams, alpha=0.10, n_boot=500)

    lines.append(f"## Divisi V -- hasil ({len(v_candidates)} varian diuji dari 41 total di registry)\n")
    lines.append(f"Target: QLIKE vs realized variance forward {FORWARD_WINDOW} menit.\n")
    mean_losses_v = {k: np.nanmean(l) for k, l in v_losses.items()}
    sorted_v = sorted(mean_losses_v.items(), key=lambda x: x[1])
    lines.append("| Varian | QLIKE rata-rata | Status MCS |")
    lines.append("|---|---:|---|")
    eliminated_names_v = {e[0] for e in v_mcs["eliminated"]}
    for name, loss in sorted_v:
        status = "SURVIVOR" if name in v_mcs["survivors"] else f"tersingkir (p={dict(v_mcs['eliminated']).get(name, float('nan')):.3f})"
        lines.append(f"| {name} | {loss:.4f} | {status} |")
    lines.append(f"\n**MCS survivors (alpha=0.10):** {v_mcs['survivors']}")
    if v_mcs.get("tie_break_simplest"):
        lines.append(f"\n**Juara (tie-break tersederhana):** {v_mcs['tie_break_simplest']}")

    # ---------------- Divisi Q ----------------
    print("Menjalankan Divisi Q...")
    q_candidates = {}
    q_nparams = {}
    for window in [48, 96, 288]:
        q_candidates[f"Q01_ROLL_w{window}"] = q.q01_roll_spread(close, window) * 1e4 / mid
        q_nparams[f"Q01_ROLL_w{window}"] = 1
    for window in [48, 96]:
        q_candidates[f"Q02_CORWIN_SCHULTZ_w{window}"] = q.q02_corwin_schultz(high, low, window) * 1e4
        q_nparams[f"Q02_CORWIN_SCHULTZ_w{window}"] = 1
        q_candidates[f"Q03_ABDI_RANALDO_w{window}"] = q.q03_abdi_ranaldo(high, low, close, window) * 1e4
        q_nparams[f"Q03_ABDI_RANALDO_w{window}"] = 1

    print(f"{len(q_candidates)} varian Q dihitung. Menghitung loss (MAE vs spread realized)...")
    q_losses = {}
    for name, est_bps in q_candidates.items():
        n = min(len(est_bps), len(spread_bps_actual))
        loss = np.abs(est_bps[:n] - spread_bps_actual[:n])
        q_losses[name] = loss

    print("Menjalankan MCS untuk Q...")
    q_mcs = model_confidence_set(q_losses, q_nparams, alpha=0.10, n_boot=500)

    lines.append(f"\n## Divisi Q -- hasil ({len(q_candidates)} varian diuji dari 35 total di registry)\n")
    lines.append("Target: MAE terhadap spread realized (ask_close-bid_close) bar M1 -- BUKAN tick individual (data tick sudah tidak ada, lihat gap Divisi T di atas).\n")
    mean_losses_q = {k: np.nanmean(l) for k, l in q_losses.items()}
    sorted_q = sorted(mean_losses_q.items(), key=lambda x: x[1])
    lines.append("| Varian | MAE (bps) | Status MCS |")
    lines.append("|---|---:|---|")
    for name, loss in sorted_q:
        status = "SURVIVOR" if name in q_mcs["survivors"] else f"tersingkir (p={dict(q_mcs['eliminated']).get(name, float('nan')):.3f})"
        lines.append(f"| {name} | {loss:.4f} | {status} |")
    lines.append(f"\n**MCS survivors (alpha=0.10):** {q_mcs['survivors']}")
    if q_mcs.get("tie_break_simplest"):
        lines.append(f"\n**Juara (tie-break tersederhana):** {q_mcs['tie_break_simplest']}")

    lines.append("\n## Catatan cakupan (jujur)\n")
    lines.append(
        f"V: {len(v_candidates)}/41 varian diuji (V06, V11, V14 dilewati -- V11 HAR-RV & V14 realized "
        f"kernel butuh refit/loop per-bar yang terlalu mahal untuk dijalankan penuh di eksplorasi ini; "
        f"V06 realized range perlu data sub-interval yang tidak dimiliki dari M1 tunggal). "
        f"Q: {len(q_candidates)}/35 varian diuji (Q04-Q12 dilewati -- butuh n_ticks per bar atau "
        f"tick_size yang belum dikalibrasi, atau bergantung pada estimator V/lainnya yang belum final). "
        f"T: 0/27, blokir data (lihat atas). Ini SINGLE_ASSET_ONLY, hasil eksplorasi bukan bukti."
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "F4_estimation_champions.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
