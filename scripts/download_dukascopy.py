#!/usr/bin/env python3
"""Unduh candle M1 BID+ASK Dukascopy untuk panel v6 (8 instrumen).

Untuk instrumen yang kode Dukascopy / point-value-nya TIDAK terverifikasi di
codebase sebelumnya (USDJPY, US100, US30, NATGAS), script ini TIDAK MENEBAK:
dia mengambil satu hari sampel, mencoba kandidat (kode, point-value), dan
menerima kombinasi itu HANYA kalau harga hasil decode masuk akal (dibandingkan
rentang harga dunia-nyata yang diketahui). Kalau tidak ada / ambigu, instrumen
itu ditandai UNRESOLVED dan TIDAK diunduh -- dilaporkan, bukan didiamkan.

Tanggal mulai per instrumen TIDAK diasumsikan -- dicari lewat binary search
(bukan menebak "2003") lalu dilaporkan sebagai tanggal mulai NYATA.

Resumable: file hari yang sudah ada (ukuran > 0, atau file kosong penanda
weekend/no-data) dilewati.

Simpan ke: /workspace/data/raw/<DISPLAY_NAME>/<DISPLAY_NAME>_YYYYMMDD.parquet
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

BASE_URL = "https://datafeed.dukascopy.com/datafeed"
RAW_DIR = Path("/workspace/data/raw")
REPORT_PATH = RAW_DIR / "DOWNLOAD_REPORT.md"

CANDLE_DTYPE = np.dtype(
    [("ts_s", ">i4"), ("open", ">i4"), ("close", ">i4"), ("low", ">i4"), ("high", ">i4"), ("vol", ">f4")]
)

REQUEST_DELAY = 1.0
BACKOFF_ON_429 = 45.0
BACKOFF_STEPS = [5, 10, 20, 40, 80, 120]
LONG_COOLDOWN_AFTER_CONSECUTIVE_FAILS = 20
LONG_COOLDOWN_SECONDS = 1800

# display_name -> {codes: [kandidat kode dukascopy urut prioritas],
#                   points: [kandidat point-value urut prioritas],
#                   plausible: (lo, hi) rentang harga dunia-nyata wajar,
#                   verified: True kalau sudah pernah terbukti benar (data lama)}
INSTRUMENTS = {
    "XAUUSD":  {"codes": ["XAUUSD"],   "points": [1000.0],   "plausible": (200, 10000),  "verified": True},
    "XAGUSD":  {"codes": ["XAGUSD"],   "points": [1000.0],   "plausible": (2, 200),      "verified": True},
    "EURUSD":  {"codes": ["EURUSD"],   "points": [100000.0], "plausible": (0.7, 1.7),    "verified": True},
    "USOIL":   {"codes": ["LIGHTCMDUSD"], "points": [1000.0], "plausible": (5, 250),     "verified": True},
    "USDJPY":  {"codes": ["USDJPY"], "points": [1000.0, 100000.0, 100.0],
                "plausible": (50, 250), "verified": False},
    "US100":   {"codes": ["USA100.IDX", "USATECH.IDX", "US100.IDX"],
                "points": [100.0, 10.0, 1000.0, 1.0],
                "plausible": (3000, 35000), "verified": False},
    "US30":    {"codes": ["USA30.IDX", "US30.IDX"],
                "points": [100.0, 10.0, 1000.0, 1.0],
                "plausible": (12000, 60000), "verified": False},
    "NATGAS":  {"codes": ["NATGASUSD", "LIGHTGASUSD"],
                "points": [1000.0, 10000.0, 100.0],
                "plausible": (0.3, 25), "verified": False},
}


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


def fetch_raw(session: requests.Session, code: str, day: date, side: str, log, quiet=False) -> tuple[bytes, int]:
    """Return (content, status_code). Used both for probing (quiet) and real download (with retry)."""
    url = f"{BASE_URL}/{code}/{day.year}/{day.month - 1:02d}/{day.day:02d}/{side}_candles_min_1.bi5"
    try:
        r = session.get(url, timeout=20)
        return r.content, r.status_code
    except requests.RequestException as e:
        if not quiet:
            log.warning(f"network error {url}: {e}")
        return b"", -1


def fetch_side_resilient(session: requests.Session, code: str, day: date, side: str, log) -> bytes:
    consecutive_fails = 0
    backoff_idx = 0
    while True:
        content, status = fetch_raw(session, code, day, side, log)
        if status == 200:
            return content
        elif status == 404:
            return b""
        elif status == 429:
            log.warning(f"429 rate-limited at {code} {day} {side} -- cooling down {BACKOFF_ON_429}s")
            time.sleep(BACKOFF_ON_429)
            continue
        else:
            consecutive_fails += 1
            delay = BACKOFF_STEPS[min(backoff_idx, len(BACKOFF_STEPS) - 1)]
            log.warning(f"status={status} at {code} {day} {side} (fail #{consecutive_fails}), retry in {delay}s")
            time.sleep(delay)
            backoff_idx += 1
            if consecutive_fails >= LONG_COOLDOWN_AFTER_CONSECUTIVE_FAILS:
                log.warning(f"{consecutive_fails} consecutive fails -- long cooldown {LONG_COOLDOWN_SECONDS}s")
                time.sleep(LONG_COOLDOWN_SECONDS)
                consecutive_fails = 0
                backoff_idx = 0
            continue


def build_day_dataframe(day: date, point: float, bid_raw: bytes, ask_raw: bytes) -> pd.DataFrame:
    bid = decompress_side(bid_raw)
    ask = decompress_side(ask_raw)
    if len(bid) == 0 and len(ask) == 0:
        return pd.DataFrame()
    day_start = int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp())

    def to_df(arr, prefix):
        if len(arr) == 0:
            return pd.DataFrame(columns=["ts_s"])
        return pd.DataFrame({
            "ts_s": arr["ts_s"].astype("int64") + day_start,
            f"{prefix}_open": arr["open"].astype("float64") / point,
            f"{prefix}_high": arr["high"].astype("float64") / point,
            f"{prefix}_low": arr["low"].astype("float64") / point,
            f"{prefix}_close": arr["close"].astype("float64") / point,
            f"{prefix}_vol": arr["vol"].astype("float32"),
        })

    bdf, adf = to_df(bid, "bid"), to_df(ask, "ask")
    merged = adf if len(bdf) == 0 else (bdf if len(adf) == 0 else pd.merge(bdf, adf, on="ts_s", how="outer"))
    merged.sort_values("ts_s", inplace=True)
    merged.reset_index(drop=True, inplace=True)
    if "bid_close" in merged.columns and "ask_close" in merged.columns:
        merged["spread"] = merged["ask_close"] - merged["bid_close"]
        merged["mid_close"] = (merged["ask_close"] + merged["bid_close"]) / 2.0
        merged["spread_bps"] = merged["spread"] / merged["mid_close"] * 1e4
    return merged


# ------------------------------------------------------ resolve code/point --

def resolve_instrument(session: requests.Session, display: str, spec: dict, log) -> dict | None:
    """Probe a recent trading day, try (code, point) combos, accept the first
    that yields plausible real-world prices. Returns {"code":..., "point":...}
    or None if unresolved (nothing plausible found)."""
    if spec.get("verified"):
        return {"code": spec["codes"][0], "point": spec["points"][0]}

    probe_day = date.today() - timedelta(days=3)
    while probe_day.weekday() >= 5:
        probe_day -= timedelta(days=1)

    lo, hi = spec["plausible"]
    for code in spec["codes"]:
        bid_raw, status = fetch_raw(session, code, probe_day, "BID", log, quiet=True)
        if status != 200 or not bid_raw:
            log.info(f"  probe {display}: code={code} status={status} (no data at {probe_day})")
            continue
        arr = decompress_side(bid_raw)
        if len(arr) == 0:
            continue
        closes_raw = arr["close"].astype("float64")
        for point in spec["points"]:
            price = np.median(closes_raw / point)
            plausible = lo <= price <= hi
            log.info(f"  probe {display}: code={code} point={point} -> median_price={price:.4f} "
                      f"plausible[{lo},{hi}]={plausible}")
            if plausible:
                return {"code": code, "point": point}
    return None


def find_earliest_date(session: requests.Session, code: str, point: float, log,
                        lo: date = date(1999, 1, 1), hi: date | None = None) -> date | None:
    """Binary search for the earliest date with non-empty BID data. Assumes
    availability is monotonic (once data starts, it continues) -- true for
    Dukascopy's historical archive."""
    hi = hi or date.today()

    def has_data(d: date) -> bool:
        content, status = fetch_raw(session, code, d, "BID", log, quiet=True)
        time.sleep(0.3)
        if status != 200 or not content:
            return False
        return len(decompress_side(content)) > 0

    # bracket: confirm hi has data, confirm lo does not
    if not has_data(hi):
        # try scanning back a bit in case `hi` itself is a data-free day near the edge
        probe = hi
        for _ in range(10):
            probe -= timedelta(days=1)
            if has_data(probe):
                hi = probe
                break
        else:
            return None

    if has_data(lo):
        return lo  # data goes back at least this far; caller's lo bound is not tight

    days_lo, days_hi = lo.toordinal(), hi.toordinal()
    while days_hi - days_lo > 1:
        mid = (days_lo + days_hi) // 2
        d = date.fromordinal(mid)
        if has_data(d):
            days_hi = mid
        else:
            days_lo = mid
    return date.fromordinal(days_hi)


# --------------------------------------------------------------- download --

def download_symbol(session: requests.Session, display: str, code: str, point: float,
                     start: date, end: date, log) -> dict:
    out_dir = RAW_DIR / display
    out_dir.mkdir(parents=True, exist_ok=True)

    day_tasks = []
    d = start
    while d <= end:
        out_path = out_dir / f"{display}_{d:%Y%m%d}.parquet"
        if not out_path.exists():
            day_tasks.append((d, out_path))
        d += timedelta(days=1)

    total = len(day_tasks)
    log.info(f"[{display}] pending day-tasks: {total} (resume: {(end-start).days+1-total} already done)")
    t0 = time.time()
    completed = 0
    total_rows = 0

    for day, out_path in day_tasks:
        if day.weekday() == 5:
            pd.DataFrame().to_parquet(out_path, index=False)
            completed += 1
            continue
        bid_raw = fetch_side_resilient(session, code, day, "BID", log)
        time.sleep(REQUEST_DELAY)
        ask_raw = fetch_side_resilient(session, code, day, "ASK", log)
        time.sleep(REQUEST_DELAY)
        df = build_day_dataframe(day, point, bid_raw, ask_raw)
        df.to_parquet(out_path, index=False)
        total_rows += len(df)
        completed += 1
        if completed % 30 == 0 or completed == total:
            elapsed = time.time() - t0
            rate = completed / elapsed if elapsed > 0 else 0
            eta_h = (total - completed) / rate / 3600 if rate > 0 else float("inf")
            log.info(f"[{display}] progress {completed}/{total} ({100*completed/max(total,1):.1f}%) "
                      f"rows={total_rows:,} rate={rate:.3f} d/s eta={eta_h:.2f}h")

    return {"display": display, "code": code, "point": point, "start": str(start), "end": str(end),
            "days_downloaded_this_run": completed, "total_rows_this_run": total_rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--end", default=None, help="default: today")
    ap.add_argument("--instruments", default=",".join(INSTRUMENTS.keys()))
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S", stream=sys.stdout)
    log = logging.getLogger("download_dukascopy")

    end = date.fromisoformat(args.end) if args.end else date.today()
    wanted = [s.strip() for s in args.instruments.split(",") if s.strip()]
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "xau-alpha-v6-research/1.0"})

    resolved = {}
    unresolved = []
    log.info("=== Tahap 1: resolusi kode & point-value (probe, bukan tebak) ===")
    for display in wanted:
        spec = INSTRUMENTS[display]
        r = resolve_instrument(session, display, spec, log)
        if r is None:
            unresolved.append(display)
            log.warning(f"[{display}] UNRESOLVED -- tidak ada kombinasi (kode,point) yang masuk akal. DILEWATI.")
        else:
            resolved[display] = r
            log.info(f"[{display}] RESOLVED -- code={r['code']} point={r['point']}")

    log.info("=== Tahap 2: cari tanggal mulai NYATA (binary search) ===")
    earliest = {}
    for display, r in resolved.items():
        d0 = find_earliest_date(session, r["code"], r["point"], log)
        earliest[display] = d0
        log.info(f"[{display}] tanggal mulai NYATA: {d0}")

    log.info("=== Tahap 3: unduh (resumable) ===")
    results = []
    for display, r in resolved.items():
        d0 = earliest[display]
        if d0 is None:
            log.warning(f"[{display}] tidak ditemukan tanggal mulai -- dilewati")
            continue
        res = download_symbol(session, display, r["code"], r["point"], d0, end, log)
        results.append(res)

    lines = ["# Laporan Unduhan Dukascopy -- panel v6\n",
             f"Dijalankan sampai: {datetime.now(timezone.utc).isoformat()}Z\n"]
    lines.append("## Tanggal mulai NYATA per instrumen\n")
    lines.append("| instrumen | kode dukascopy | point | tanggal mulai NYATA | rentang diminta s/d |")
    lines.append("|---|---|---:|---|---|")
    for display in wanted:
        if display in resolved:
            r = resolved[display]
            lines.append(f"| {display} | {r['code']} | {r['point']} | **{earliest.get(display)}** | {end} |")
        else:
            lines.append(f"| {display} | -- | -- | **UNRESOLVED** | -- |")
    if unresolved:
        lines.append(f"\n## UNRESOLVED ({len(unresolved)})\n\nTidak diunduh -- kode/point-value tidak "
                      f"terverifikasi masuk akal dari probe: {', '.join(unresolved)}. Ini SENGAJA, bukan "
                      f"error diam-diam -- lebih baik data hilang daripada data salah skala.")
    REPORT_PATH.write_text("\n".join(lines))
    log.info(f"Laporan ditulis ke {REPORT_PATH}")
    log.info("DONE.")


if __name__ == "__main__":
    main()
