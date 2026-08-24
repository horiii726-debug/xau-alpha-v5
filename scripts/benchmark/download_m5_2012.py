#!/usr/bin/env python3
"""Unduh XAUUSD M5 bid+ask 2012-2026 dengan retry+backoff eksponensial
(dukascopy-node -r/-rp bawaan terbukti tidak cukup untuk 429 di request awal)."""
import os
import subprocess
import sys
import time
from pathlib import Path

CSV_DIR = Path("/workspace/data/raw_m5_2012/csv")
LOG_DIR = Path("/workspace/logs")
CSV_DIR.mkdir(parents=True, exist_ok=True)
NODE_BIN = "/opt/nvm/versions/node/v24.19.0/bin/dukascopy-node"
NODE_ENV_BIN_DIR = "/opt/nvm/versions/node/v24.19.0/bin"
MAX_ATTEMPTS = 10
BACKOFF_BASE_S = 20


def log(msg):
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


def download_side(side: str) -> bool:
    out_csv = CSV_DIR / f"xauusd_m5_{side}.csv"
    log_path = LOG_DIR / f"m5_2012_{side}.log"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        cmd = [NODE_BIN, "-i", "xauusd", "-from", "2012-01-01", "-to", "now", "-t", "m5", "-p", side,
               "-f", "csv", "-dir", str(CSV_DIR), "-fn", f"xauusd_m5_{side}",
               "-r", "3", "-rp", "3000", "-bs", "5", "-bp", "2000"]
        env = os.environ.copy()
        env["PATH"] = f"{NODE_ENV_BIN_DIR}:{env.get('PATH', '')}"
        with open(log_path, "a") as lf:
            lf.write(f"\n=== attempt {attempt}/{MAX_ATTEMPTS} {time.strftime('%H:%M:%S')} ===\n")
            try:
                proc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, env=env, timeout=900)
                rc = proc.returncode
            except subprocess.TimeoutExpired:
                rc = -1
        ok = rc == 0 and out_csv.exists() and out_csv.stat().st_size > 1000
        if ok:
            n_lines = sum(1 for _ in open(out_csv))
            log(f"[{side}] SUCCESS attempt {attempt}: {n_lines:,} lines, {out_csv.stat().st_size/1e6:.1f}MB")
            return True
        delay = BACKOFF_BASE_S * (2 ** (attempt - 1))
        log(f"[{side}] FAILED attempt {attempt}/{MAX_ATTEMPTS} (rc={rc}), backoff {delay}s")
        if attempt < MAX_ATTEMPTS:
            time.sleep(delay)
    log(f"[{side}] GAVE UP")
    return False


def main():
    ok_bid = download_side("bid")
    ok_ask = download_side("ask")
    log(f"DONE bid={ok_bid} ask={ok_ask}")
    (LOG_DIR / "download_m5_2012.DONE").write_text(f"bid={ok_bid} ask={ok_ask}")
    return ok_bid and ok_ask


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
