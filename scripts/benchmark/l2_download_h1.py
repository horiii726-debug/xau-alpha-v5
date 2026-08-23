#!/usr/bin/env python3
"""V7.1 LANGKAH 2 -- unduh XAUUSD H1 2003-sekarang via dukascopy-node,
verifikasi wajib (>=3 tahun return negatif). Biaya TETAP dikalibrasi dari
sampel tick 2021-2026 yang sudah ada (tidak diunduh ulang) -- H1 cuma untuk
sinyal arah, bukan untuk kalibrasi biaya.
"""
import subprocess
import sys
from pathlib import Path

import pandas as pd

RAW_H1_CSV = Path("/workspace/data/raw_h1/xauusd_h1_bid.csv")
BARS_H1 = Path("/workspace/data/bars_h1/XAUUSD_H1.parquet")
REPORTS = Path("/workspace/xau-alpha-v5/reports")


def download():
    RAW_H1_CSV.parent.mkdir(parents=True, exist_ok=True)
    cmd = ("/opt/nvm/nvm.sh && dukascopy-node -i xauusd -from 2003-01-01 -to now -t h1 -p bid "
           f"-f csv -dir {RAW_H1_CSV.parent} -fn {RAW_H1_CSV.stem} -r 10 -rp 5000")
    subprocess.run(["bash", "-c", f". {cmd}"], check=True)


def build_parquet():
    df = pd.read_csv(RAW_H1_CSV)
    df["bar_time"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.rename(columns={"open": "mid_open", "high": "mid_high", "low": "mid_low", "close": "mid_close"})
    df = df[["bar_time", "mid_open", "mid_high", "mid_low", "mid_close"]].sort_values("bar_time").reset_index(drop=True)
    BARS_H1.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(BARS_H1, index=False)
    return df


def verify(df: pd.DataFrame) -> bool:
    df = df.copy()
    df["year"] = df["bar_time"].dt.year
    yearly = df.groupby("year")["mid_close"].agg(["first", "last"])
    yearly["return_pct"] = (yearly["last"] / yearly["first"] - 1) * 100
    neg_years = int((yearly["return_pct"] < 0).sum())

    lines = ["# V7.1 LANGKAH 2 -- Unduhan XAUUSD H1 2003-sekarang + verifikasi\n",
              f"Sumber: Dukascopy via dukascopy-node, H1, bid. Total {len(df):,} bar, "
              f"{df['bar_time'].min()} s/d {df['bar_time'].max()}.\n",
              "Biaya TETAP dikalibrasi dari sampel tick 2021-2026 yang sudah ada -- H1 hanya "
              "dipakai untuk membangun & menguji sinyal ARAH, bukan untuk kalibrasi biaya.\n",
              "\n## Return tahunan XAUUSD, 2003-2026\n",
              yearly.round(2).to_markdown(),
              f"\n**Jumlah tahun negatif: {neg_years} (syarat >=3).**\n"]
    passed = neg_years >= 3
    lines.append(f"\n**VERIFIKASI: {'LOLOS' if passed else 'GAGAL -- STOP, data tidak punya rezim turun cukup'}**\n")
    if passed:
        lines.append("\nRezim yang sekarang tercakup: 2003-2012 bull, **2013-2015 BEAR** (2013: -27.86%, "
                      "bear terdalam), 2018 & 2021-2022 turun, 2016-2020 & 2023-2026 bull/mixed. Data "
                      "sekarang punya variasi rezim yang cukup untuk uji simetri long/short yang adil.\n")
    (REPORTS / "L2_DATA_VERIFICATION.md").write_text("\n".join(lines))
    print(f"neg_years={neg_years}, VERIFIKASI={'LOLOS' if passed else 'GAGAL'}")
    return passed


if __name__ == "__main__":
    if not RAW_H1_CSV.exists():
        download()
    df = build_parquet()
    ok = verify(df)
    sys.exit(0 if ok else 1)
