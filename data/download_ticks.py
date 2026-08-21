#!/usr/bin/env python3
"""Download Dukascopy historical tick data for the F0 panel and store as
per-symbol per-day parquet files. Resumable: skips days whose output file
already exists.

IMPORTANT: this datafeed enforces a strict aggregate (IP-level) rate limit,
empirically measured at ~2-3 requests/second. Parallel/concurrent fetching
was tested and makes things WORSE (triggers sustained 429 blocks across all
connections, not just soft per-request throttling). This script is
therefore intentionally SINGLE-STREAM and paced -- do not parallelize it.
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
    "LIGHTCMDUSD": 1000.0,  # Dukascopy code for "USOIL" (Light Sweet Crude Oil CFD)
}

BASE_URL = "https://datafeed.dukascopy.com/datafeed"
RAW_DIR = Path("/workspace/data/raw")
TICK_DTYPE = np.dtype([("ms", ">i4"), ("ask", ">i4"), ("bid", ">i4"), ("askv", ">f4"), ("bidv", ">f4")])

REQUEST_DELAY = 0.42  # ~2.4 req/s -- measured safe margin below the ~3.3 req/s throttle threshold
BACKOFF_ON_429 = 45.0  # seconds to cool down if we still get rate-limited (observed to be sustained, not per-request)


def fetch_hour(session: requests.Session, symbol: str, day: date, hour: int, log) -> bytes:
    url = f"{BASE_URL}/{symbol}/{day.year}/{day.month - 1:02d}/{day.day:02d}/{hour:02d}h_ticks.bi5"
    while True:
        try:
            r = session.get(url, timeout=20)
        except requests.RequestException as e:
            log.warning(f"network error {url}: {e}, retry in 5s")
            time.sleep(5)
            continue
        if r.status_code == 200:
            return r.content
        elif r.status_code == 404:
            return b""
        elif r.status_code == 429:
            log.warning(f"429 rate-limited at {symbol} {day} {hour}h -- cooling down {BACKOFF_ON_429}s")
            time.sleep(BACKOFF_ON_429)
            continue
        elif r.status_code == 503:
            time.sleep(5)
            continue
        else:
            log.warning(f"unexpected HTTP {r.status_code} for {url}, retry in 3s")
            time.sleep(3)
            continue


def decompress_hour(comp: bytes) -> np.ndarray:
    if not comp:
        return np.empty(0, dtype=TICK_DTYPE)
    try:
        raw = lzma.decompress(comp)
    except lzma.LZMAError:
        return np.empty(0, dtype=TICK_DTYPE)
    n = len(raw) // 20
    if n == 0:
        return np.empty(0, dtype=TICK_DTYPE)
    return np.frombuffer(raw[: n * 20], dtype=TICK_DTYPE)


def build_day_dataframe(day: date, point: float, hour_bytes: dict) -> pd.DataFrame:
    frames = []
    for hour, comp in hour_bytes.items():
        arr = decompress_hour(comp)
        if len(arr) == 0:
            continue
        base_ms = int(datetime(day.year, day.month, day.day, hour, tzinfo=timezone.utc).timestamp() * 1000)
        ts_ms = base_ms + arr["ms"].astype("int64")
        frames.append(
            pd.DataFrame(
                {
                    "ts_ms": ts_ms,
                    "ask": arr["ask"].astype("float64") / point,
                    "bid": arr["bid"].astype("float64") / point,
                    "ask_vol": arr["askv"].astype("float32"),
                    "bid_vol": arr["bidv"].astype("float32"),
                }
            )
        )
    if not frames:
        return pd.DataFrame(columns=["ts_ms", "ask", "bid", "ask_vol", "bid_vol"])
    df = pd.concat(frames, ignore_index=True)
    df.sort_values("ts_ms", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2021-08-22")
    ap.add_argument("--end", default="2026-08-21")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S", stream=sys.stdout)
    log = logging.getLogger("download")

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    day_tasks = []
    for symbol, point in SYMBOLS.items():
        out_dir = RAW_DIR / symbol
        out_dir.mkdir(parents=True, exist_ok=True)
        for day in daterange(start, end):
            out_path = out_dir / f"{symbol}_{day:%Y%m%d}.parquet"
            if out_path.exists() and out_path.stat().st_size > 0:
                continue
            day_tasks.append((symbol, day, point, out_path))

    total_days = len(day_tasks)
    log.info(f"Pending day-tasks: {total_days} (single-stream, paced ~{1/REQUEST_DELAY:.1f} req/s)")

    session = requests.Session()
    session.headers.update({"User-Agent": "xau-alpha-v5-research/1.0"})

    t0 = time.time()
    completed = 0
    total_ticks = 0

    for symbol, day, point, out_path in day_tasks:
        if day.weekday() == 5:  # Saturday: markets fully closed, no requests needed
            pd.DataFrame(columns=["ts_ms", "ask", "bid", "ask_vol", "bid_vol"]).to_parquet(out_path, index=False)
            completed += 1
            continue

        hour_bytes = {}
        for hour in range(24):
            hour_bytes[hour] = fetch_hour(session, symbol, day, hour, log)
            time.sleep(REQUEST_DELAY)

        df = build_day_dataframe(day, point, hour_bytes)
        df.to_parquet(out_path, index=False)
        total_ticks += len(df)
        completed += 1

        if completed % 10 == 0 or completed == total_days:
            elapsed = time.time() - t0
            rate = completed / elapsed if elapsed > 0 else 0
            eta_h = (total_days - completed) / rate / 3600 if rate > 0 else float("inf")
            log.info(
                f"progress {completed}/{total_days} ({100*completed/total_days:.1f}%) "
                f"ticks_so_far={total_ticks:,} rate={rate:.3f} days/s eta={eta_h:.2f}h"
            )

    log.info(f"DONE. {completed}/{total_days} days. total_ticks={total_ticks:,}")


if __name__ == "__main__":
    main()
