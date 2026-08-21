#!/usr/bin/env python3
"""Aggregate per-day tick parquet files into M5/M15 OHLC bars + per-bar
spread stats (mean, p50/p75/p90/p99), using MID price for OHLC (bid/ask
avg) and tracking ask/bid separately for spread. Writes one parquet per
symbol per timeframe covering the whole downloaded range.
"""
import sys
import argparse
import logging
from pathlib import Path

import pandas as pd
import numpy as np

RAW_DIR = Path("/workspace/data/raw")
BAR_DIR = Path("/workspace/data/bars")

TIMEFRAMES = {"M5": "5min", "M15": "15min"}


def load_symbol_ticks(symbol: str) -> pd.DataFrame:
    files = sorted((RAW_DIR / symbol).glob(f"{symbol}_*.parquet"))
    if not files:
        return pd.DataFrame(columns=["ts_ms", "ask", "bid", "ask_vol", "bid_vol"])
    frames = [pd.read_parquet(f) for f in files]
    df = pd.concat(frames, ignore_index=True)
    if len(df) == 0:
        return df
    df["ts"] = pd.to_datetime(df["ts_ms"], unit="ms", utc=True)
    df.sort_values("ts", inplace=True)
    df.set_index("ts", inplace=True)
    df["mid"] = (df["ask"] + df["bid"]) / 2.0
    df["spread_bps"] = (df["ask"] - df["bid"]) / df["mid"] * 1e4
    return df


def make_bars(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    if len(df) == 0:
        return pd.DataFrame()
    ohlc = df["mid"].resample(freq).ohlc()
    vol = (df["ask_vol"] + df["bid_vol"]).resample(freq).sum().rename("tick_volume")
    n_ticks = df["mid"].resample(freq).count().rename("n_ticks")
    spread_mean = df["spread_bps"].resample(freq).mean().rename("spread_bps_mean")
    spread_p50 = df["spread_bps"].resample(freq).quantile(0.50).rename("spread_bps_p50")
    spread_p75 = df["spread_bps"].resample(freq).quantile(0.75).rename("spread_bps_p75")
    spread_p90 = df["spread_bps"].resample(freq).quantile(0.90).rename("spread_bps_p90")
    spread_p99 = df["spread_bps"].resample(freq).quantile(0.99).rename("spread_bps_p99")
    bars = pd.concat(
        [ohlc, vol, n_ticks, spread_mean, spread_p50, spread_p75, spread_p90, spread_p99], axis=1
    )
    bars = bars.dropna(subset=["open"])  # drop bars with zero ticks
    bars.reset_index(inplace=True)
    bars.rename(columns={"ts": "bar_time"}, inplace=True)
    return bars


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", nargs="+", default=["XAUUSD", "XAGUSD", "EURUSD", "LIGHTCMDUSD"])
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    log = logging.getLogger("aggregate")

    BAR_DIR.mkdir(parents=True, exist_ok=True)

    for symbol in args.symbols:
        log.info(f"loading ticks for {symbol}...")
        df = load_symbol_ticks(symbol)
        log.info(f"{symbol}: {len(df):,} ticks loaded")
        if len(df) == 0:
            continue
        for label, freq in TIMEFRAMES.items():
            bars = make_bars(df, freq)
            out = BAR_DIR / f"{symbol}_{label}.parquet"
            bars.to_parquet(out, index=False)
            log.info(f"{symbol} {label}: {len(bars):,} bars -> {out}")


if __name__ == "__main__":
    main()
