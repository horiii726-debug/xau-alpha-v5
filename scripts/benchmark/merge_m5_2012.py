#!/usr/bin/env python3
"""Gabungkan CSV bid+ask M5 (2012-2026) jadi satu parquet dengan mid_close +
spread_bps -- dipakai L2b, L3 (Lomba 1 refit, 2, 3, 4, 5) dan seterusnya."""
from pathlib import Path

import pandas as pd

CSV_DIR = Path("/workspace/data/raw_m5_2012/csv")
OUT = Path("/workspace/data/bars_m5_2012/XAUUSD_M5_2012.parquet")


def load_side(side: str) -> pd.DataFrame:
    df = pd.read_csv(CSV_DIR / f"xauusd_m5_{side}.csv")
    df["ts"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("ts")[["open", "high", "low", "close"]]
    df.columns = [f"{side}_{c}" for c in df.columns]
    return df


def main():
    bid = load_side("bid")
    ask = load_side("ask")
    m5 = bid.join(ask, how="outer").sort_index()
    m5["mid_open"] = (m5["bid_open"] + m5["ask_open"]) / 2.0
    m5["mid_high"] = (m5["bid_high"] + m5["ask_high"]) / 2.0
    m5["mid_low"] = (m5["bid_low"] + m5["ask_low"]) / 2.0
    m5["mid_close"] = (m5["bid_close"] + m5["ask_close"]) / 2.0
    m5["spread_bps"] = (m5["ask_close"] - m5["bid_close"]) / m5["mid_close"] * 1e4
    m5 = m5.reset_index().rename(columns={"ts": "bar_time"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    m5.to_parquet(OUT, index=False)
    print(f"{len(m5):,} bar M5 tersimpan -> {OUT}, rentang {m5['bar_time'].min()} s/d {m5['bar_time'].max()}")


if __name__ == "__main__":
    main()
