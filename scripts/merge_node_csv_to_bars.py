#!/usr/bin/env python3
"""Gabungkan CSV bid+ask dari dukascopy-node jadi M1 parquet per instrumen,
lalu resample ke M5/M15 (skema kolom sama seperti pipeline lama: bid_*,
ask_*, spread, mid_close, spread_bps) -- supaya run_f0_v6.py / run_f1_v6.py
jalan tanpa perubahan.
"""
import sys
from pathlib import Path

import pandas as pd

CSV_DIR = Path("/workspace/data/raw_node/csv")
M1_DIR = Path("/workspace/data/raw_node/m1")
BAR_DIR = Path("/workspace/data/bars_candles")
TIMEFRAMES = {"M5": "5min", "M15": "15min"}

DISPLAY = {"xauusd": "XAUUSD", "xagusd": "XAGUSD", "eurusd": "EURUSD",
           "usdjpy": "USDJPY", "lightcmdusd": "USOIL"}


def load_side(inst_code: str, side: str) -> pd.DataFrame:
    f = CSV_DIR / f"{inst_code}_{side}.csv"
    if not f.exists() or f.stat().st_size == 0:
        return pd.DataFrame()
    df = pd.read_csv(f)
    df["ts"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("ts")[["open", "high", "low", "close"]]
    df.columns = [f"{side}_{c}" for c in df.columns]
    return df


def main():
    M1_DIR.mkdir(parents=True, exist_ok=True)
    BAR_DIR.mkdir(parents=True, exist_ok=True)
    for inst_code, display in DISPLAY.items():
        bid = load_side(inst_code, "bid")
        ask = load_side(inst_code, "ask")
        if len(bid) == 0 or len(ask) == 0:
            print(f"{display}: MISSING bid or ask CSV -- skip")
            continue
        m1 = bid.join(ask, how="outer").sort_index()
        m1["mid_close"] = (m1["bid_close"] + m1["ask_close"]) / 2.0
        m1["spread_bps"] = (m1["ask_close"] - m1["bid_close"]) / m1["mid_close"] * 1e4
        m1_out = M1_DIR / f"{display}_M1.parquet"
        m1.reset_index().to_parquet(m1_out, index=False)
        print(f"{display}: M1 {len(m1):,} rows -> {m1_out} "
              f"({m1.index.min()} .. {m1.index.max()})")

        for label, freq in TIMEFRAMES.items():
            agg = {}
            for side in ("bid", "ask"):
                for c in ("open", "high", "low", "close"):
                    col = f"{side}_{c}"
                    agg[col] = "first" if c == "open" else ("max" if c == "high" else ("min" if c == "low" else "last"))
            bars = m1.resample(freq).agg(agg)
            bars = bars.dropna(subset=["bid_close", "ask_close"], how="all")
            bars["mid_close"] = (bars["bid_close"] + bars["ask_close"]) / 2.0
            bars["spread_bps"] = (bars["ask_close"] - bars["bid_close"]) / bars["mid_close"] * 1e4
            spread_stats = pd.DataFrame({
                "spread_bps_mean": m1["spread_bps"].resample(freq).mean(),
                "spread_bps_p50": m1["spread_bps"].resample(freq).quantile(0.50),
                "spread_bps_p75": m1["spread_bps"].resample(freq).quantile(0.75),
                "spread_bps_p90": m1["spread_bps"].resample(freq).quantile(0.90),
                "spread_bps_p99": m1["spread_bps"].resample(freq).quantile(0.99),
                "n_m1_bars": m1["spread_bps"].resample(freq).count(),
            })
            bars = bars.join(spread_stats)
            bars.reset_index(inplace=True)
            bars.rename(columns={"ts": "bar_time"}, inplace=True)
            out = BAR_DIR / f"{display}_{label}.parquet"
            bars.to_parquet(out, index=False)
            print(f"{display} {label}: {len(bars):,} bars -> {out}")


if __name__ == "__main__":
    main()
