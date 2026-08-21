#!/usr/bin/env python3
"""Aggregate per-day M1 bid/ask candle parquet (raw_candles/) into M5/M15
bars + per-bar spread stats. Unlike the tick-based aggregator, this
resamples already-built M1 candles (open=first, high=max, low=min,
close=last, vol=sum) rather than raw ticks.
"""
import argparse
import logging
from pathlib import Path

import pandas as pd
import numpy as np

RAW_DIR = Path("/workspace/data/raw_candles")
BAR_DIR = Path("/workspace/data/bars_candles")
TIMEFRAMES = {"M5": "5min", "M15": "15min"}
SYMBOLS = ["XAUUSD", "XAGUSD", "EURUSD", "LIGHTCMDUSD"]


def load_symbol_m1(symbol: str) -> pd.DataFrame:
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
    out.set_index("ts", inplace=True)
    return out


def resample_ohlc(m1: pd.DataFrame, freq: str) -> pd.DataFrame:
    if len(m1) == 0:
        return pd.DataFrame()
    agg = {}
    for side in ["bid", "ask"]:
        agg[f"{side}_open"] = "first"
        agg[f"{side}_high"] = "max"
        agg[f"{side}_low"] = "min"
        agg[f"{side}_close"] = "last"
        agg[f"{side}_vol"] = "sum"
    present = {k: v for k, v in agg.items() if k in m1.columns}
    bars = m1.resample(freq).agg(present)
    bars = bars.dropna(subset=[c for c in ["bid_close", "ask_close"] if c in bars.columns], how="all")
    if "bid_close" in bars.columns and "ask_close" in bars.columns:
        bars["mid_close"] = (bars["bid_close"] + bars["ask_close"]) / 2.0
        bars["spread_bps"] = (bars["ask_close"] - bars["bid_close"]) / bars["mid_close"] * 1e4

    spread_stats = None
    if "spread_bps" in m1.columns:
        spread_stats = pd.DataFrame(
            {
                "spread_bps_mean": m1["spread_bps"].resample(freq).mean(),
                "spread_bps_p50": m1["spread_bps"].resample(freq).quantile(0.50),
                "spread_bps_p75": m1["spread_bps"].resample(freq).quantile(0.75),
                "spread_bps_p90": m1["spread_bps"].resample(freq).quantile(0.90),
                "spread_bps_p99": m1["spread_bps"].resample(freq).quantile(0.99),
                "n_m1_bars": m1["spread_bps"].resample(freq).count(),
            }
        )
        bars = bars.join(spread_stats)

    bars.reset_index(inplace=True)
    bars.rename(columns={"ts": "bar_time"}, inplace=True)
    return bars


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", nargs="+", default=SYMBOLS)
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    log = logging.getLogger("aggregate_candles")
    BAR_DIR.mkdir(parents=True, exist_ok=True)

    for symbol in args.symbols:
        m1 = load_symbol_m1(symbol)
        log.info(f"{symbol}: {len(m1):,} M1 candles loaded")
        if len(m1) == 0:
            continue
        for label, freq in TIMEFRAMES.items():
            bars = resample_ohlc(m1, freq)
            out = BAR_DIR / f"{symbol}_{label}.parquet"
            bars.to_parquet(out, index=False)
            log.info(f"{symbol} {label}: {len(bars):,} bars -> {out}")


if __name__ == "__main__":
    main()
