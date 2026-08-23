#!/usr/bin/env python3
"""Orkestrator unduhan dukascopy-node yang lebih andal daripada bash:
concurrency=2 (worker pool), exponential backoff sendiri di atas 429
(retry bawaan CLI -r/-rp terbukti tidak menyelamatkan dari 429 di request
awal -- lihat log percobaan sebelumnya), dan begitu bid+ask satu instrumen
selesai, LANGSUNG dikonversi ke parquet lalu CSV mentahnya dihapus (hemat
disk, dan progress per-instrumen jadi permanen tanpa perlu simpan CSV besar).

CATATAN JUJUR: dukascopy-node CLI TIDAK mendukung bid+ask sekaligus dalam
satu request (dicek langsung: `-p bid,ask` ditolak, cuma terima nilai
tunggal). Jadi tetap 10 request (5 instrumen x 2 sisi), bukan 5.
"""
import os
import subprocess
import sys
import time
import shutil
import threading
import queue
from pathlib import Path
from datetime import date

sys.path.insert(0, "/workspace/xau-alpha-v5")

FROM = "2012-01-01"
CSV_DIR = Path("/workspace/data/raw_node/csv")
LOG_DIR = Path("/workspace/logs")
CSV_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

INSTRUMENTS = ["xauusd", "xagusd", "eurusd", "usdjpy", "lightcmdusd"]
MAX_CONCURRENT = 2
MAX_ATTEMPTS = 8
BACKOFF_BASE_S = 20  # 20, 40, 80, 160, 320, 640, 1280, 2560 (~1.4h ceiling worst case)

NODE_BIN = "/opt/nvm/versions/node/v24.19.0/bin/dukascopy-node"
NODE_ENV_BIN_DIR = "/opt/nvm/versions/node/v24.19.0/bin"


def log(msg: str):
    ts = time.strftime("%H:%M:%S")
    line = f"{ts} {msg}"
    print(line, flush=True)


def download_side(inst: str, side: str) -> bool:
    """Returns True on success (non-empty file, exit 0)."""
    out_csv = CSV_DIR / f"{inst}_{side}.csv"
    log_path = LOG_DIR / f"node_{inst}_{side}.log"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        cmd = [
            NODE_BIN, "-i", inst, "-from", FROM, "-to", "now", "-t", "m1", "-p", side,
            "-f", "csv", "-dir", str(CSV_DIR), "-fn", f"{inst}_{side}",
            "-r", "3", "-rp", "3000", "-bs", "5", "-bp", "2000",
        ]
        env = os.environ.copy()
        env["PATH"] = f"{NODE_ENV_BIN_DIR}:{env.get('PATH', '')}"
        returncode = None
        with open(log_path, "a") as lf:
            lf.write(f"\n=== attempt {attempt}/{MAX_ATTEMPTS} {time.strftime('%H:%M:%S')} ===\n")
            try:
                proc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, env=env, timeout=1800)
                returncode = proc.returncode
            except subprocess.TimeoutExpired:
                lf.write("\n=== TIMEOUT after 1800s, killed ===\n")
                returncode = -1
        ok = returncode == 0 and out_csv.exists() and out_csv.stat().st_size > 1000
        if ok:
            n_lines = sum(1 for _ in open(out_csv))
            log(f"[{inst}_{side}] SUCCESS attempt {attempt}: {n_lines:,} lines, "
                f"{out_csv.stat().st_size/1e6:.1f}MB")
            return True
        delay = BACKOFF_BASE_S * (2 ** (attempt - 1))
        log(f"[{inst}_{side}] FAILED attempt {attempt}/{MAX_ATTEMPTS} (exit={returncode}), "
            f"backoff {delay}s")
        if attempt < MAX_ATTEMPTS:
            time.sleep(delay)
    log(f"[{inst}_{side}] GAVE UP after {MAX_ATTEMPTS} attempts")
    return False


def process_instrument(inst: str, results: dict):
    bid_ok = download_side(inst, "bid")
    ask_ok = download_side(inst, "ask")
    results[inst] = {"bid_ok": bid_ok, "ask_ok": ask_ok}
    if bid_ok and ask_ok:
        log(f"[{inst}] both sides OK -> converting to parquet")
        try:
            from scripts.merge_node_csv_to_bars import load_side, DISPLAY, M1_DIR, BAR_DIR, TIMEFRAMES
            import pandas as pd
            display = DISPLAY[inst]
            bid = load_side(inst, "bid")
            ask = load_side(inst, "ask")
            m1 = bid.join(ask, how="outer").sort_index()
            m1["mid_close"] = (m1["bid_close"] + m1["ask_close"]) / 2.0
            m1["spread_bps"] = (m1["ask_close"] - m1["bid_close"]) / m1["mid_close"] * 1e4
            M1_DIR.mkdir(parents=True, exist_ok=True)
            m1.reset_index().to_parquet(M1_DIR / f"{display}_M1.parquet", index=False)
            for label, freq in TIMEFRAMES.items():
                agg = {}
                for s in ("bid", "ask"):
                    for c in ("open", "high", "low", "close"):
                        col = f"{s}_{c}"
                        agg[col] = "first" if c == "open" else ("max" if c == "high" else ("min" if c == "low" else "last"))
                bars = m1.resample(freq).agg(agg)
                bars = bars.dropna(subset=["bid_close", "ask_close"], how="all")
                bars["mid_close"] = (bars["bid_close"] + bars["ask_close"]) / 2.0
                bars["spread_bps"] = (bars["ask_close"] - bars["bid_close"]) / bars["mid_close"] * 1e4
                spread_stats = pd.DataFrame({
                    "spread_bps_p50": m1["spread_bps"].resample(freq).quantile(0.50),
                    "spread_bps_p90": m1["spread_bps"].resample(freq).quantile(0.90),
                    "n_m1_bars": m1["spread_bps"].resample(freq).count(),
                })
                bars = bars.join(spread_stats).reset_index().rename(columns={"ts": "bar_time"})
                bars.to_parquet(BAR_DIR / f"{display}_{label}.parquet", index=False)
            log(f"[{inst}] parquet written: M1 {len(m1):,} rows, range "
                f"{m1.index.min()} .. {m1.index.max()}")
            (CSV_DIR / f"{inst}_bid.csv").unlink(missing_ok=True)
            (CSV_DIR / f"{inst}_ask.csv").unlink(missing_ok=True)
            log(f"[{inst}] raw CSV deleted (parquet kept)")
            results[inst]["parquet_ok"] = True
        except Exception as e:
            log(f"[{inst}] PARQUET CONVERSION FAILED: {e}")
            results[inst]["parquet_ok"] = False
    else:
        results[inst]["parquet_ok"] = False


def main():
    results = {}
    q = queue.Queue()
    for inst in INSTRUMENTS:
        q.put(inst)

    def worker():
        while True:
            try:
                inst = q.get_nowait()
            except queue.Empty:
                return
            log(f"=== WORKER starting instrument: {inst} ===")
            process_instrument(inst, results)
            log(f"=== WORKER finished instrument: {inst} ===")

    threads = [threading.Thread(target=worker) for _ in range(MAX_CONCURRENT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    log("=== ALL INSTRUMENTS PROCESSED ===")
    for inst, r in results.items():
        log(f"  {inst}: bid={r['bid_ok']} ask={r['ask_ok']} parquet={r.get('parquet_ok')}")
    (LOG_DIR / "download_dukascopy_node_v2.DONE").write_text(
        "\n".join(f"{inst}: {r}" for inst, r in results.items()))
    log("DONE FILE WRITTEN")


if __name__ == "__main__":
    main()
