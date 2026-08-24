#!/usr/bin/env python3
"""L12 -- unduh data makro gratis: FRED (CSV langsung, tanpa API key) + CFTC
COT emas mingguan (legacy, sejak 2003). Semua diselaraskan ke D1 dengan LAG 1
HARI PENUH (rilis sore/malam -- t hanya boleh pakai data sampai t-1).
"""
import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

OUT_DIR = Path("/workspace/data/macro")
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS = Path("/workspace/xau-alpha-v5/reports")

FRED_SERIES = {
    "DFII10": "real_yield_10y",
    "DGS10": "nominal_10y",
    "T10YIE": "breakeven_10y",
    "DTWEXBGS": "dxy_broad",
    "DEXUSEU": "eurusd",
    "DEXJPUS": "usdjpy",
    "VIXCLS": "vix",
    "GVZCLS": "gvz_gold_vol",
}


def fetch_fred(series_id: str) -> pd.DataFrame:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["date", series_id]
    df["date"] = pd.to_datetime(df["date"])
    df[series_id] = pd.to_numeric(df[series_id], errors="coerce")
    return df


def fetch_all_fred() -> dict:
    results = {}
    for sid, name in FRED_SERIES.items():
        try:
            df = fetch_fred(sid)
            n_valid = df[sid].notna().sum()
            first_valid = df.loc[df[sid].notna(), "date"].min()
            last_valid = df.loc[df[sid].notna(), "date"].max()
            print(f"{sid} ({name}): {n_valid:,} obs valid, {first_valid.date()} s/d {last_valid.date()}")
            results[sid] = {"name": name, "df": df, "n_valid": n_valid,
                              "first": first_valid, "last": last_valid}
        except Exception as e:
            print(f"{sid}: GAGAL -- {e}")
            results[sid] = None
    return results


def fetch_cot_gold(year_start=2003, year_end=2026) -> pd.DataFrame:
    frames = []
    for year in range(year_start, year_end + 1):
        url = f"https://www.cftc.gov/files/dea/history/deacot{year}.zip"
        try:
            r = requests.get(url, timeout=60)
            if r.status_code != 200:
                print(f"COT {year}: HTTP {r.status_code}, dilewati")
                continue
            zf = zipfile.ZipFile(io.BytesIO(r.content))
            fname = zf.namelist()[0]
            with zf.open(fname) as f:
                df = pd.read_csv(f, low_memory=False)
            df.columns = [c.strip() for c in df.columns]
            gold = df[df["Market and Exchange Names"].str.strip() == "GOLD - COMMODITY EXCHANGE INC."].copy()
            if len(gold) == 0:
                print(f"COT {year}: tidak ada baris GOLD, dilewati")
                continue
            gold["date"] = pd.to_datetime(gold["As of Date in Form YYYY-MM-DD"])
            gold["noncomm_long"] = pd.to_numeric(gold["Noncommercial Positions-Long (All)"], errors="coerce")
            gold["noncomm_short"] = pd.to_numeric(gold["Noncommercial Positions-Short (All)"], errors="coerce")
            gold["net_noncomm"] = gold["noncomm_long"] - gold["noncomm_short"]
            frames.append(gold[["date", "noncomm_long", "noncomm_short", "net_noncomm"]])
            print(f"COT {year}: {len(gold)} baris gold")
        except Exception as e:
            print(f"COT {year}: GAGAL -- {e}")
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True).sort_values("date").drop_duplicates(subset="date")
    return out


def main():
    print("=== FRED ===")
    fred_results = fetch_all_fred()

    merged = None
    for sid, res in fred_results.items():
        if res is None:
            continue
        d = res["df"][["date", sid]]
        merged = d if merged is None else merged.merge(d, on="date", how="outer")
    merged = merged.sort_values("date").reset_index(drop=True)

    print("\n=== CFTC COT Gold (weekly, legacy) ===")
    cot = fetch_cot_gold()
    if len(cot) > 0:
        print(f"COT total: {len(cot)} baris, {cot['date'].min().date()} s/d {cot['date'].max().date()}")
        cot.to_parquet(OUT_DIR / "cot_gold.parquet", index=False)
    else:
        print("COT: TIDAK ADA DATA -- MAC05 akan ditandai TIDAK_TERSEDIA")

    merged.to_parquet(OUT_DIR / "fred_daily.parquet", index=False)

    lines = ["# L12 -- Data Makro (FRED + CFTC COT)\n", "## Ketersediaan tiap seri FRED\n",
              "| seri | nama | n_valid | mulai | akhir |", "|---|---|---:|---|---|"]
    for sid, res in fred_results.items():
        if res is None:
            lines.append(f"| {sid} | -- | -- | GAGAL | -- |")
        else:
            lines.append(f"| {sid} | {res['name']} | {res['n_valid']:,} | {res['first'].date()} | {res['last'].date()} |")
    lines.append(f"\n## CFTC COT Gold\n\n{'Tersedia: ' + str(len(cot)) + ' baris mingguan, ' + str(cot['date'].min().date()) + ' s/d ' + str(cot['date'].max().date()) if len(cot) > 0 else 'TIDAK TERSEDIA'}\n")
    lines.append(f"\nSemua data diselaraskan ke D1 dengan **LAG 1 HARI PENUH** saat dipakai di L13 -- "
                  f"file mentah di sini BELUM di-lag, itu dilakukan saat penggabungan dengan harga XAU.\n")
    (REPORTS / "L12_DATA_MAKRO.md").write_text("\n".join(lines))
    print(f"\nDisimpan: {OUT_DIR}/fred_daily.parquet, {OUT_DIR}/cot_gold.parquet")


if __name__ == "__main__":
    main()
