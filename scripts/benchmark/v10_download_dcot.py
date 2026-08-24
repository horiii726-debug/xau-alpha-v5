#!/usr/bin/env python3
"""V10 -- unduh CFTC Disaggregated COT (2006-2026), ekstrak GOLD, simpan
Managed Money net position + rasio konsentrasi top-4/top-8. Sumber:
https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/
(diverifikasi resolve via curl -I sebelum diunduh)."""
import zipfile
from pathlib import Path

import pandas as pd
import requests

RAW = Path("/workspace/data/macro/dcot_raw")
RAW.mkdir(parents=True, exist_ok=True)
OUT = Path("/workspace/data/macro/dcot_gold.parquet")

COLS = ["Market_and_Exchange_Names", "Report_Date_as_YYYY-MM-DD",
        "M_Money_Positions_Long_All", "M_Money_Positions_Short_All",
        "Conc_Net_LE_4_TDR_Long_All", "Conc_Net_LE_4_TDR_Short_All",
        "Conc_Net_LE_8_TDR_Long_All", "Conc_Net_LE_8_TDR_Short_All"]


def main():
    hist_zip = RAW / "hist_2006_2016.zip"
    if not hist_zip.exists():
        r = requests.get("https://www.cftc.gov/files/dea/history/fut_disagg_txt_hist_2006_2016.zip", timeout=60)
        r.raise_for_status()
        hist_zip.write_bytes(r.content)

    frames = []
    with zipfile.ZipFile(hist_zip) as zf:
        fname = [n for n in zf.namelist() if n.endswith(".txt")][0]
        with zf.open(fname) as f:
            df = pd.read_csv(f, low_memory=False, usecols=COLS)
    gold = df[df["Market_and_Exchange_Names"].str.strip() == "GOLD - COMMODITY EXCHANGE INC."].copy()
    frames.append(gold)
    print(f"2006-2016 (hist): {len(gold)} baris gold")

    for year in range(2017, 2027):
        yzip = RAW / f"y{year}.zip"
        if not yzip.exists():
            r = requests.get(f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip", timeout=60)
            if r.status_code != 200:
                print(f"{year}: HTTP {r.status_code}, dilewati")
                continue
            yzip.write_bytes(r.content)
        try:
            with zipfile.ZipFile(yzip) as zf:
                fname = [n for n in zf.namelist() if n.endswith(".txt")][0]
                with zf.open(fname) as f:
                    df = pd.read_csv(f, low_memory=False, usecols=lambda c: c in COLS)
            gold = df[df["Market_and_Exchange_Names"].str.strip() == "GOLD - COMMODITY EXCHANGE INC."].copy()
            frames.append(gold)
            print(f"{year}: {len(gold)} baris gold")
        except Exception as e:
            print(f"{year}: GAGAL -- {e}")

    out = pd.concat(frames, ignore_index=True)
    out["date"] = pd.to_datetime(out["Report_Date_as_YYYY-MM-DD"])
    out["mm_long"] = pd.to_numeric(out["M_Money_Positions_Long_All"], errors="coerce")
    out["mm_short"] = pd.to_numeric(out["M_Money_Positions_Short_All"], errors="coerce")
    out["mm_net"] = out["mm_long"] - out["mm_short"]
    out["conc_net4_long"] = pd.to_numeric(out["Conc_Net_LE_4_TDR_Long_All"], errors="coerce")
    out["conc_net4_short"] = pd.to_numeric(out["Conc_Net_LE_4_TDR_Short_All"], errors="coerce")
    out["conc_net8_long"] = pd.to_numeric(out["Conc_Net_LE_8_TDR_Long_All"], errors="coerce")
    out["conc_net8_short"] = pd.to_numeric(out["Conc_Net_LE_8_TDR_Short_All"], errors="coerce")
    out = out[["date", "mm_long", "mm_short", "mm_net",
               "conc_net4_long", "conc_net4_short", "conc_net8_long", "conc_net8_short"]]
    out = out.sort_values("date").drop_duplicates(subset="date").reset_index(drop=True)
    out.to_parquet(OUT, index=False)
    print(f"\nTotal: {len(out)} baris mingguan, {out['date'].min().date()} s/d {out['date'].max().date()}")
    print(f"Disimpan: {OUT}")


if __name__ == "__main__":
    main()
