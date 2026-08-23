#!/usr/bin/env python3
"""Download Dukascopy M1 BID+ASK candles (one request per side per day,
instead of 24 tick requests per day) and store per-symbol per-day parquet
with open/high/low/close for both bid and ask, plus per-minute spread
(ask_close - bid_close). Same measured IP-level rate limit applies as the
tick pipeline -- kept single-stream and paced. Resumable.
"""
import sys
import time
import lzma
import argparse
import logging
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

import requests
import pandas as pd
import numpy as np

SYMBOLS = {
    "XAUUSD": 1000.0,
    "XAGUSD": 1000.0,
    "EURUSD": 100000.0,
    "LIGHTCMDUSD": 1000.0,  # Dukascopy code for "USOIL"
}

BASE_URL = "https://datafeed.dukascopy.com/datafeed"
RAW_DIR = Path("/workspace/data/raw_candles")
CANDLE_DTYPE = np.dtype(
    [("ts_s", ">i4"), ("open", ">i4"), ("close", ">i4"), ("low", ">i4"), ("high", ">i4"), ("vol", ">f4")]
)

REQUEST_DELAY = 1.0  # lowered from 0.42s after repeated 503s -- ~1 req/s
BACKOFF_ON_429 = 45.0
BACKOFF_STEPS = [5, 10, 20, 40, 80, 120]  # escalating backoff for 503/network errors
LONG_COOLDOWN_AFTER_CONSECUTIVE_FAILS = 20  # circuit breaker: after this many in a row, sleep 30min and retry
LONG_COOLDOWN_SECONDS = 1800


def fetch_side(session: requests.Session, symbol: str, day: date, side: str, log) -> bytes:
    url = f"{BASE_URL}/{symbol}/{day.year}/{day.month - 1:02d}/{day.day:02d}/{side}_candles_min_1.bi5"
    consecutive_fails = 0
    backoff_idx = 0
    while True:
        try:
            r = session.get(url, timeout=20)
        except requests.RequestException as e:
            consecutive_fails += 1
            delay = BACKOFF_STEPS[min(backoff_idx, len(BACKOFF_STEPS) - 1)]
            log.warning(f"network error {url}: {e} (fail #{consecutive_fails}), retry in {delay}s")
            time.sleep(delay)
            backoff_idx += 1
            if consecutive_fails >= LONG_COOLDOWN_AFTER_CONSECUTIVE_FAILS:
                log.warning(f"{consecutive_fails} consecutive fails -- long cooldown {LONG_COOLDOWN_SECONDS}s, then resetting backoff")
                time.sleep(LONG_COOLDOWN_SECONDS)
                consecutive_fails = 0
                backoff_idx = 0
            continue
        if r.status_code == 200:
            return r.content
        elif r.status_code == 404:
            return b""
        elif r.status_code == 429:
            log.warning(f"429 rate-limited at {symbol} {day} {side} -- cooling down {BACKOFF_ON_429}s")
            time.sleep(BACKOFF_ON_429)
            continue
        elif r.status_code == 503:
            consecutive_fails += 1
            delay = BACKOFF_STEPS[min(backoff_idx, len(BACKOFF_STEPS) - 1)]
            log.warning(f"503 at {symbol} {day} {side} (fail #{consecutive_fails}), retry in {delay}s")
            time.sleep(delay)
            backoff_idx += 1
            if consecutive_fails >= LONG_COOLDOWN_AFTER_CONSECUTIVE_FAILS:
                log.warning(f"{consecutive_fails} consecutive fails -- long cooldown {LONG_COOLDOWN_SECONDS}s, then resetting backoff")
                time.sleep(LONG_COOLDOWN_SECONDS)
                consecutive_fails = 0
                backoff_idx = 0
            continue
        else:
            time.sleep(3)
            continue


def decompress_side(comp: bytes) -> np.ndarray:
    if not comp:
        return np.empty(0, dtype=CANDLE_DTYPE)
    try:
        raw = lzma.decompress(comp)
    except lzma.LZMAError:
        return np.empty(0, dtype=CANDLE_DTYPE)
    n = len(raw) // 24
    if n == 0:
        return np.empty(0, dtype=CANDLE_DTYPE)
    return np.frombuffer(raw[: n * 24], dtype=CANDLE_DTYPE)


def build_day_dataframe(day: date, point: float, bid_raw: bytes, ask_raw: bytes) -> pd.DataFrame:
    bid = decompress_side(bid_raw)
    ask = decompress_side(ask_raw)
    if len(bid) == 0 and len(ask) == 0:
        return pd.DataFrame()

    day_start = int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp())

    def to_df(arr, prefix):
        if len(arr) == 0:
            return pd.DataFrame(columns=["ts_s"])
        d = pd.DataFrame(
            {
                "ts_s": arr["ts_s"].astype("int64") + day_start,
                f"{prefix}_open": arr["open"].astype("float64") / point,
                f"{prefix}_high": arr["high"].astype("float64") / point,
                f"{prefix}_low": arr["low"].astype("float64") / point,
                f"{prefix}_close": arr["close"].astype("float64") / point,
                f"{prefix}_vol": arr["vol"].astype("float32"),
            }
        )
        return d

    bdf = to_df(bid, "bid")
    adf = to_df(ask, "ask")
    if len(bdf) == 0:
        merged = adf
    elif len(adf) == 0:
        merged = bdf
    else:
        merged = pd.merge(bdf, adf, on="ts_s", how="outer")
    merged.sort_values("ts_s", inplace=True)
    merged.reset_index(drop=True, inplace=True)
    if "bid_close" in merged.columns and "ask_close" in merged.columns:
        merged["spread"] = merged["ask_close"] - merged["bid_close"]
        merged["mid_close"] = (merged["ask_close"] + merged["bid_close"]) / 2.0
        merged["spread_bps"] = merged["spread"] / merged["mid_close"] * 1e4
    return merged


def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2021-08-22")
    ap.add_argument("--end", default="2026-08-22")
    ap.add_argument("--symbols", default=",".join(SYMBOLS.keys()),
                     help="comma-separated subset of symbols to download")
    args = ap.parse_args()

    requested = [s.strip() for s in args.symbols.split(",") if s.strip()]
    unknown = [s for s in requested if s not in SYMBOLS]
    if unknown:
        raise SystemExit(f"unknown symbols: {unknown}. known: {list(SYMBOLS.keys())}")
    active_symbols = {s: SYMBOLS[s] for s in requested}

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S", stream=sys.stdout)
    log = logging.getLogger("download_candles")

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    day_tasks = []
    for symbol, point in active_symbols.items():
        out_dir = RAW_DIR / symbol
        out_dir.mkdir(parents=True, exist_ok=True)
        for day in daterange(start, end):
            out_path = out_dir / f"{symbol}_{day:%Y%m%d}.parquet"
            if out_path.exists() and out_path.stat().st_size > 0:
                continue
            day_tasks.append((symbol, day, point, out_path))

    total_days = len(day_tasks)
    log.info(f"Pending day-tasks: {total_days} (2 requests/day: BID+ASK candles, paced)")

    session = requests.Session()
    session.headers.update({"User-Agent": "xau-alpha-v5-research/1.0"})

    t0 = time.time()
    completed = 0
    total_rows = 0

    for symbol, day, point, out_path in day_tasks:
        if day.weekday() == 5:
            pd.DataFrame().to_parquet(out_path, index=False)
            completed += 1
            continue

        bid_raw = fetch_side(session, symbol, day, "BID", log)
        time.sleep(REQUEST_DELAY)
        ask_raw = fetch_side(session, symbol, day, "ASK", log)
        time.sleep(REQUEST_DELAY)

        df = build_day_dataframe(day, point, bid_raw, ask_raw)
        df.to_parquet(out_path, index=False)
        total_rows += len(df)
        completed += 1

        if completed % 20 == 0 or completed == total_days:
            elapsed = time.time() - t0
            rate = completed / elapsed if elapsed > 0 else 0
            eta_h = (total_days - completed) / rate / 3600 if rate > 0 else float("inf")
            log.info(
                f"progress {completed}/{total_days} ({100*completed/total_days:.1f}%) "
                f"rows_so_far={total_rows:,} rate={rate:.3f} days/s eta={eta_h:.2f}h"
            )

    log.info(f"DONE. {completed}/{total_days} days. total_rows={total_rows:,}")


if __name__ == "__main__":
    main()
