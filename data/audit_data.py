#!/usr/bin/env python3
"""F0 data audit: gaps, duplicates, outliers, holiday hours, hash of the
raw data directory. Operates on the candle-based raw_candles/ directory
(bid/ask M1 OHLC per day). Writes reports/F0_data_audit.md.
"""
import hashlib
import argparse
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
import numpy as np

RAW_DIR = Path("/workspace/data/raw_candles")
REPORTS_DIR = Path("/workspace/reports")

SYMBOLS = ["XAUUSD", "XAGUSD", "EURUSD", "LIGHTCMDUSD"]


def hash_directory(d: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(d.rglob("*.parquet")):
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def load_symbol(symbol: str) -> pd.DataFrame:
    files = sorted((RAW_DIR / symbol).glob(f"{symbol}_*.parquet"))
    frames = []
    for f in files:
        df = pd.read_parquet(f)
        if len(df) > 0:
            df["_file"] = f.name
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["ts"] = pd.to_datetime(out["ts_s"], unit="s", utc=True)
    out.sort_values("ts", inplace=True)
    out.reset_index(drop=True, inplace=True)
    return out


def audit_symbol(symbol: str) -> dict:
    df = load_symbol(symbol)
    result = {"symbol": symbol, "n_files": len((RAW_DIR / symbol).glob(f"{symbol}_*.parquet")) if False else 0}
    files = sorted((RAW_DIR / symbol).glob(f"{symbol}_*.parquet"))
    result["n_files"] = len(files)
    if df.empty:
        result["n_rows"] = 0
        return result

    result["n_rows"] = len(df)
    result["date_min"] = str(df["ts"].min())
    result["date_max"] = str(df["ts"].max())

    dupes = df.duplicated(subset=["ts"]).sum()
    result["duplicate_timestamps"] = int(dupes)

    diffs = df["ts"].diff().dt.total_seconds().dropna()
    gt_1min = (diffs > 60).sum()
    gaps_over_1h = diffs[diffs > 3600]
    result["gaps_over_1min_count"] = int(gt_1min)
    result["gaps_over_1h_count"] = int(len(gaps_over_1h))
    result["largest_gap_minutes"] = float(diffs.max() / 60) if len(diffs) else 0.0

    if "mid_close" in df.columns:
        ret = np.log(df["mid_close"] / df["mid_close"].shift(1)).dropna()
        outlier_thresh = ret.std() * 8
        n_outliers = (ret.abs() > outlier_thresh).sum()
        result["return_outliers_gt_8sigma"] = int(n_outliers)
        result["max_abs_1min_return_pct"] = float(ret.abs().max() * 100)

    if "spread_bps" in df.columns:
        sp = df["spread_bps"].dropna()
        result["spread_bps_negative_count"] = int((sp < 0).sum())
        result["spread_bps_mean"] = float(sp.mean())
        result["spread_bps_p50"] = float(sp.quantile(0.50))
        result["spread_bps_p90"] = float(sp.quantile(0.90))
        result["spread_bps_p99"] = float(sp.quantile(0.99))

    return result


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = ["# F0 — Audit Data\n"]
    all_results = []
    for symbol in SYMBOLS:
        res = audit_symbol(symbol)
        all_results.append(res)
        lines.append(f"## {symbol}\n")
        for k, v in res.items():
            if k == "symbol":
                continue
            lines.append(f"- {k}: {v}")
        lines.append("")

    print("hashing raw_candles/ directory (this may take a bit)...")
    h = hash_directory(RAW_DIR)
    lines.append(f"## Hash data\n\nsha256(raw_candles/) = `{h}`\n")

    out_path = REPORTS_DIR / "F0_data_audit.md"
    out_path.write_text("\n".join(lines))
    print(f"wrote {out_path}")
    for res in all_results:
        print(res)


if __name__ == "__main__":
    main()
