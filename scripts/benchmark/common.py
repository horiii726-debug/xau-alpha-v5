"""Utilitas bersama untuk 5 lomba benchmark. Data: XAUUSD M1/M5 yang SUDAH
ada (5 tahun, tidak ada unduhan baru). Split kronologis 70/30, fit HANYA di
train, semua estimator kausal (pakai data sampai bar t saja untuk keputusan
di t).
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RAW_M1_DIR = Path("/workspace/data/raw_candles/XAUUSD")
BAR_DIR = Path("/workspace/data/bars_candles")
CONSOLIDATED_M1 = Path("/workspace/data/bars_candles/XAUUSD_M1_consolidated.parquet")
REPORTS = Path("/workspace/xau-alpha-v5/reports")
FIG_DIR = REPORTS / "figs"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def load_m1(force_rebuild: bool = False) -> pd.DataFrame:
    """Load consolidated M1 mid-price series (bid/ask/mid/spread_bps), build
    once from raw daily files then cache as parquet."""
    if CONSOLIDATED_M1.exists() and not force_rebuild:
        df = pd.read_parquet(CONSOLIDATED_M1)
        df["ts"] = pd.to_datetime(df["ts"], utc=True)
        return df
    files = sorted(RAW_M1_DIR.glob("XAUUSD_*.parquet"))
    frames = []
    for f in files:
        d = pd.read_parquet(f)
        if len(d) > 0 and "ts_s" in d.columns:
            frames.append(d)
    out = pd.concat(frames, ignore_index=True)
    out["ts"] = pd.to_datetime(out["ts_s"], unit="s", utc=True)
    out = out.sort_values("ts").drop_duplicates(subset="ts").reset_index(drop=True)
    out["mid_close"] = (out["bid_close"] + out["ask_close"]) / 2.0
    out["mid_high"] = (out["bid_high"] + out["ask_high"]) / 2.0
    out["mid_low"] = (out["bid_low"] + out["ask_low"]) / 2.0
    out["mid_open"] = (out["bid_open"] + out["ask_open"]) / 2.0
    out["spread_bps"] = (out["ask_close"] - out["bid_close"]) / out["mid_close"] * 1e4
    keep = ["ts", "mid_open", "mid_high", "mid_low", "mid_close", "bid_close", "ask_close", "spread_bps"]
    out = out[keep]
    out.to_parquet(CONSOLIDATED_M1, index=False)
    return out


def load_m5() -> pd.DataFrame:
    df = pd.read_parquet(BAR_DIR / "XAUUSD_M5.parquet")
    df["bar_time"] = pd.to_datetime(df["bar_time"], utc=True)
    return df


def chronological_split(n: int, train_frac: float = 0.70):
    """Return (train_idx, test_idx) as boolean masks, chronological (no shuffle)."""
    cut = int(n * train_frac)
    train = np.zeros(n, dtype=bool)
    train[:cut] = True
    return train, ~train


def active_hours_mask(ts: pd.Series) -> pd.Series:
    """Buang jam rollover (21:00-23:00 UTC) dan akhir pekan -- sesuai
    instruksi biaya. Jam sepi lain (00:00-01:00 UTC, biasanya volume tipis
    antara sesi NY tutup & Sydney/Tokyo ramai) juga dikeluarkan dari
    pengukuran spread representatif."""
    hour = ts.dt.hour
    dow = ts.dt.dayofweek  # 0=Mon .. 6=Sun
    weekend = dow >= 5
    rollover = (hour >= 21) & (hour < 23)
    quiet = (hour >= 0) & (hour < 1)
    return ~(weekend | rollover | quiet)


def measure_cost_bps(m1: pd.DataFrame, train_mask: np.ndarray) -> dict:
    """Biaya round-trip dalam bps, diukur HANYA di jam trading aktif, dari
    data TRAIN saja (supaya konsisten dengan 'fit hanya di train'). Dicetak
    eksplisit sebelum dipakai di Lomba 4/5."""
    active = active_hours_mask(m1["ts"])
    sb = m1.loc[train_mask & active, "spread_bps"].dropna()
    sb = sb[(sb > 0) & (sb < 500)]
    spread_median = float(sb.median())
    spread_p75 = float(sb.quantile(0.75))
    komisi_bps = 2 * 0.0014 * 100  # 0.0014% per sisi -> bps: 0.0014/100*1e4 = 0.14bps/sisi
    slippage_bps = 0.5 * spread_median
    round_trip_bps = spread_median + komisi_bps + slippage_bps
    result = {
        "spread_median_bps": spread_median,
        "spread_p75_bps": spread_p75,
        "komisi_roundtrip_bps": komisi_bps,
        "slippage_bps": slippage_bps,
        "round_trip_cost_bps": round_trip_bps,
        "n_bars_used": int((train_mask & active).sum()),
    }
    print("=== BIAYA TERUKUR (jam aktif saja, dari TRAIN) ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    return result


def bootstrap_pvalue(diff: np.ndarray, n_boot: int = 2000, seed: int = 0) -> float:
    """One-sided bootstrap p-value: P(bootstrap mean diff <= 0), untuk uji
    'peserta mengalahkan baseline secara signifikan'. diff = metrik_peserta
    (arah 'lebih tinggi lebih baik') - metrik_baseline, per-observasi."""
    rng = np.random.default_rng(seed)
    diff = diff[np.isfinite(diff)]
    if len(diff) < 10:
        return 1.0
    boot_means = np.array([rng.choice(diff, size=len(diff), replace=True).mean() for _ in range(n_boot)])
    return float((boot_means <= 0).mean())


def spearman_ic(pred: np.ndarray, target: np.ndarray) -> float:
    mask = np.isfinite(pred) & np.isfinite(target)
    if mask.sum() < 10:
        return np.nan
    rho, _ = stats.spearmanr(pred[mask], target[mask])
    return float(rho)


def sign_accuracy(pred: np.ndarray, target: np.ndarray) -> float:
    mask = np.isfinite(pred) & np.isfinite(target) & (pred != 0)
    if mask.sum() < 10:
        return np.nan
    return float((np.sign(pred[mask]) == np.sign(target[mask])).mean())


def qlike(pred_var: np.ndarray, realized_var: np.ndarray) -> float:
    """QLIKE loss (lower is better): RV/pred - log(RV/pred) - 1."""
    mask = np.isfinite(pred_var) & np.isfinite(realized_var) & (pred_var > 0) & (realized_var > 0)
    if mask.sum() < 10:
        return np.nan
    ratio = realized_var[mask] / pred_var[mask]
    return float(np.mean(ratio - np.log(ratio) - 1))


def qlike_median(pred_var: np.ndarray, realized_var: np.ndarray) -> float:
    """QLIKE median -- robust ke outlier ekor (mean QLIKE meledak kalau pred
    kebetulan sangat dekat nol, sering terjadi pada baseline observasi
    tunggal). Dilaporkan berdampingan dengan mean, bukan pengganti."""
    mask = np.isfinite(pred_var) & np.isfinite(realized_var) & (pred_var > 0) & (realized_var > 0)
    if mask.sum() < 10:
        return np.nan
    ratio = realized_var[mask] / pred_var[mask]
    return float(np.median(ratio - np.log(ratio) - 1))


def rmse(pred: np.ndarray, target: np.ndarray) -> float:
    mask = np.isfinite(pred) & np.isfinite(target)
    if mask.sum() < 10:
        return np.nan
    return float(np.sqrt(np.mean((pred[mask] - target[mask]) ** 2)))


def mincer_zarnowitz_r2(pred_var: np.ndarray, realized_var: np.ndarray) -> float:
    """R^2 dari regresi realized_var ~ a + b*pred_var (OLS), estimator baik
    kalau a~0, b~1, R^2 tinggi -- di sini kita laporkan R^2 saja sebagai
    ringkasan daya jelas."""
    mask = np.isfinite(pred_var) & np.isfinite(realized_var)
    if mask.sum() < 10:
        return np.nan
    x, y = pred_var[mask], realized_var[mask]
    slope, intercept, r, p, se = stats.linregress(x, y)
    return float(r ** 2)


def auc_score(pred_prob_or_score: np.ndarray, target_binary: np.ndarray) -> float:
    from sklearn.metrics import roc_auc_score
    mask = np.isfinite(pred_prob_or_score) & np.isfinite(target_binary)
    if mask.sum() < 10 or len(np.unique(target_binary[mask])) < 2:
        return np.nan
    return float(roc_auc_score(target_binary[mask], pred_prob_or_score[mask]))
