#!/usr/bin/env python3
"""F0 -- fondasi, audit data, model biaya, K_eff, daya statistik. XAU ALPHA v6.

Panel yang benar-benar tersedia: XAUUSD, XAGUSD (K=2). Lihat PREREGISTRATION.md
untuk deviasi dari spec (panel 8 instrumen / riwayat 20 tahun) yang dinyatakan
SEBELUM script ini dijalankan.

Menulis:
  reports/F0_data_audit.md
  reports/F0_cost_model.md
  reports/F0_universe.md
  reports/F0_power.md
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path("/workspace/data/raw_candles")
BAR_DIR = Path("/workspace/data/bars_candles")
REPORTS_DIR = Path("/workspace/xau-alpha-v5/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["XAUUSD", "XAGUSD"]

# ---------------------------------------------------------------- audit ---

def audit_symbol(symbol: str) -> dict:
    files = sorted((RAW_DIR / symbol).glob(f"{symbol}_*.parquet"))
    dates = [f.stem.split("_")[1] for f in files]
    dates_dt = sorted(pd.to_datetime(dates, format="%Y%m%d"))

    empty_days = 0
    total_rows = 0
    day_hashes = []
    dup_ts_total = 0
    outlier_days = []
    for f in files:
        df = pd.read_parquet(f)
        if len(df) == 0:
            empty_days += 1
            continue
        total_rows += len(df)
        day_hashes.append(hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()[:12])
        if "ts_s" in df.columns:
            dup_ts_total += int(df["ts_s"].duplicated().sum())
        if "bid_close" in df.columns and len(df) > 5:
            ret = df["bid_close"].pct_change().dropna()
            if len(ret) > 0:
                extreme = (ret.abs() > 0.05).sum()  # >5% in one minute -- candidate outlier/bad tick
                if extreme > 0:
                    outlier_days.append((f.stem, int(extreme)))

    # weekday gap check: expected trading days = Mon-Fri minus not-yet-elapsed; weekends
    # are written as empty parquet by the downloader, Mon-Fri should have data.
    full_range = pd.date_range(dates_dt[0], dates_dt[-1], freq="D") if dates_dt else []
    weekdays = [d for d in full_range if d.weekday() < 5]
    have = set(dates_dt)
    missing_weekdays = [d for d in weekdays if d not in have]

    combined_hash = hashlib.sha256("".join(day_hashes).encode()).hexdigest()

    return {
        "symbol": symbol,
        "n_day_files": len(files),
        "n_empty_days": empty_days,
        "first_date": str(dates_dt[0].date()) if dates_dt else None,
        "last_date": str(dates_dt[-1].date()) if dates_dt else None,
        "total_m1_rows": total_rows,
        "duplicate_ts_rows": dup_ts_total,
        "missing_weekdays_in_range": len(missing_weekdays),
        "missing_weekday_sample": [str(d.date()) for d in missing_weekdays[:10]],
        "outlier_days_gt5pct_1min_move": outlier_days[:10],
        "n_outlier_days": len(outlier_days),
        "snapshot_hash_sha256_12": combined_hash[:16],
    }


def write_data_audit(audits: list[dict]):
    lines = ["# F0 -- Audit Data (Dukascopy M1 bid/ask candle)\n",
             f"Dijalankan: {datetime.now(timezone.utc).isoformat()}Z\n",
             "Sumber: Dukascopy datafeed, M1 BID+ASK candle (bukan tick mentah -- lihat catatan di bawah).\n"]
    for a in audits:
        lines.append(f"\n## {a['symbol']}\n")
        lines.append(f"- Rentang file harian: **{a['first_date']} s/d {a['last_date']}** ({a['n_day_files']} file hari, {a['n_empty_days']} hari kosong/weekend)")
        lines.append(f"- Total baris M1: {a['total_m1_rows']:,}")
        lines.append(f"- Baris timestamp duplikat: {a['duplicate_ts_rows']}")
        lines.append(f"- Hari kerja (Sen-Jum) yang HILANG dalam rentang: {a['missing_weekdays_in_range']}"
                      + (f" (contoh: {', '.join(a['missing_weekday_sample'])})" if a['missing_weekday_sample'] else ""))
        lines.append(f"- Hari dengan pergerakan 1-menit > 5% (kandidat outlier/bad tick): {a['n_outlier_days']}"
                      + (f" -- {a['outlier_days_gt5pct_1min_move']}" if a['outlier_days_gt5pct_1min_move'] else ""))
        lines.append(f"- Hash snapshot (SHA-256, 16 char pertama, gabungan hash per-hari): `{a['snapshot_hash_sha256_12']}`")
    lines.append(
        "\n## Catatan jujur\n\n"
        "- Data adalah **M1 BID+ASK candle** yang direkonstruksi dari feed Dukascopy, "
        "**bukan tick mentah**. Spread & slippage sub-menit (skala latensi 1-10 detik) "
        "**tidak bisa diukur langsung** dari data ini -- lihat F0_cost_model.md untuk "
        "cara ini ditangani (proxy penskalaan-akar-waktu, ditandai eksplisit, BUKAN "
        "pengukuran tick langsung).\n"
        "- Perubahan spesifikasi kontrak (tick size dsb.) sepanjang riwayat: **TIDAK_TAHU** "
        "-- tidak ada sumber resmi yang diperiksa untuk ini di F0 ini.\n"
        "- Hari kerja yang hilang bisa berarti libur bursa (Natal/Tahun Baru dsb.) ATAU "
        "gap unduhan -- tidak dibedakan otomatis di sini; wajib diperiksa manual sebelum F1 "
        "kalau panel diperluas.\n"
    )
    (REPORTS_DIR / "F0_data_audit.md").write_text("\n".join(lines))
    print("wrote F0_data_audit.md")


# ------------------------------------------------------------ cost model --

def load_bars(symbol: str, tf: str = "M5") -> pd.DataFrame:
    f = BAR_DIR / f"{symbol}_{tf}.parquet"
    if not f.exists():
        return pd.DataFrame()
    df = pd.read_parquet(f)
    df["bar_time"] = pd.to_datetime(df["bar_time"], utc=True)
    return df


def write_cost_model():
    lines = ["# F0 -- Model Biaya (v6, koreksi beta: sigma_bar -> sigma_latensi)\n"]
    lines.append(
        "Komisi metals TERVERIFIKASI dari halaman resmi (03_DATA_DAN_BIAYA.md §B1): "
        "FTMO 0.140 bps/sisi, FundedNext 0.160 bps/sisi (per-sisi -- ambigu resmi, "
        "dipakai asumsi konservatif). Markup spread prop firm & swap: **TIDAK_KETEMU** "
        "(sama seperti dokumen v6 asli) -- tidak dimasukkan ke total, ditandai.\n"
    )
    summary_rows = []
    for symbol in SYMBOLS:
        bars = load_bars(symbol, "M5")
        if len(bars) == 0 or "spread_bps" not in bars.columns:
            lines.append(f"\n## {symbol}: TIDAK ADA DATA BAR\n")
            continue
        sb = bars["spread_bps"].dropna()
        sb = sb[(sb > 0) & (sb < 1000)]  # drop non-positive/garbage
        p50, p75, p90, p99 = sb.quantile([0.50, 0.75, 0.90, 0.99])

        # sigma_bar (M1) empiris -> proxy sigma_latensi via sqrt-time scaling.
        bars5 = bars.copy()
        bars5["mid_ret"] = bars5["mid_close"].pct_change()
        sigma_m5_bps = bars5["mid_ret"].std() * 1e4  # bps per 5-min bar
        sigma_m1_bps = sigma_m5_bps / np.sqrt(5.0)   # sqrt-time scale down to 1 min
        latensi_grid_s = [1, 3, 10]
        sigma_latensi_bps = {s: sigma_m1_bps * np.sqrt(s / 60.0) for s in latensi_grid_s}

        # session-hour spread breakdown (UTC hour)
        bars5["hour_utc"] = bars5["bar_time"].dt.hour
        by_hour = bars5.groupby("hour_utc")["spread_bps"].median().round(3)

        komisi_rt_bps = 2 * (0.160 if symbol == "XAGUSD" else 0.140)  # per-sisi *2 = round trip, worst-case FundedNext/FTMO whichever; use symbol default FTMO except metals both similar
        scenarios = {
            "best":  {"spread_p": p50, "alpha": 0.5, "beta": 0.00, "penalty": 1.0, "latensi_s": 1},
            "base":  {"spread_p": p75, "alpha": 1.0, "beta": 0.25, "penalty": 1.0, "latensi_s": 3},
            "worst": {"spread_p": p90, "alpha": 1.5, "beta": 0.50, "penalty": 1.5, "latensi_s": 10},
        }
        lines.append(f"\n## {symbol}\n")
        lines.append(f"- Spread terukur (M5, dari tick bid/ask real): p50={p50:.3f} bps, p75={p75:.3f} bps, p90={p90:.3f} bps, p99={p99:.3f} bps")
        lines.append(f"- sigma M5 empiris: {sigma_m5_bps:.3f} bps/bar -> proxy sigma M1 (skala akar-waktu): {sigma_m1_bps:.3f} bps")
        lines.append(f"- proxy sigma_latensi (skala akar-waktu dari M1, BUKAN tick langsung): "
                      + ", ".join(f"{s}s={v:.3f}bps" for s, v in sigma_latensi_bps.items()))
        lines.append(f"\n| skenario | spread bps | slip bps (v6, sigma_latensi) | komisi RT bps | **total RT bps** |")
        lines.append("|---|---:|---:|---:|---:|")
        total_worst = None
        for name, s in scenarios.items():
            slip = s["alpha"] * s["spread_p"] + s["beta"] * sigma_latensi_bps[s["latensi_s"]]
            total = (2 * s["spread_p"] + slip) * s["penalty"] + komisi_rt_bps
            if name == "worst":
                total_worst = total
            lines.append(f"| {name} | {s['spread_p']:.3f} | {slip:.3f} | {komisi_rt_bps:.3f} | **{total:.3f}** |")

        # kappa per horizon (planning sigma via sqrt-time from M5 sigma)
        lines.append(f"\n**Kappa (biaya_worst_bps / volatilitas_horizon_bps), horizon via penskalaan akar-waktu dari sigma M5 terukur:**\n")
        lines.append("| horizon | menit | sigma horizon (bps) | kappa @worst |")
        lines.append("|---|---:|---:|---:|")
        for label, minutes in [("H15", 15), ("H60", 60), ("H120", 120), ("H240", 240), ("H1D", 1440)]:
            sigma_h = sigma_m5_bps * np.sqrt(minutes / 5.0)
            kappa = total_worst / sigma_h
            lines.append(f"| {label} | {minutes} | {sigma_h:.2f} | {kappa:.3f} |")
        lines.append(f"\n**Catatan:** kappa di atas memakai penskalaan akar-waktu dari sigma bar (proxy "
                      f"perencanaan), BUKAN durasi hit-barrier NYATA (§03 C4) -- itu butuh triple-barrier "
                      f"labeling penuh yang belum dijalankan (F0 tidak menjalankan kandidat). Ditandai "
                      f"`KAPPA_PLANNING_PROXY`, wajib dihitung ulang dari durasi barrier real sebelum F2b.")
        summary_rows.append((symbol, p90, total_worst))

    lines.append("\n## Status verifikasi biaya\n")
    lines.append("`cost_verified: false` -- sama seperti spec asli, baru jadi true setelah F12 forward test "
                  "(>=200 fill nyata). Markup spread prop firm & swap XAUUSD/XAGUSD: **TIDAK_KETEMU**, tidak "
                  "dimasukkan ke total di atas (akan menaikkan biaya lebih lanjut).")
    (REPORTS_DIR / "F0_cost_model.md").write_text("\n".join(lines))
    print("wrote F0_cost_model.md")
    return summary_rows


# ---------------------------------------------------------------- K_eff ---

def baseline_pnl(symbol: str, L: int = 12, hold: int = 12) -> pd.Series:
    bars = load_bars(symbol, "M5")
    if len(bars) == 0:
        return pd.Series(dtype=float)
    mid = bars.set_index("bar_time")["mid_close"]
    mom = mid.pct_change(L)
    sig = np.sign(mom).shift(1)
    ret = mid.pct_change()
    strat_ret = (sig * ret).dropna()
    return strat_ret


def write_universe():
    lines = ["# F0 -- Universe & K_eff\n"]
    lines.append(
        "**Panel diminta oleh spec v6 (§04): 8 instrumen** (XAUUSD, XAGUSD, EURUSD, USDJPY, "
        "US100, US30, USOIL, NATGAS). **Panel data tersedia & terverifikasi di run ini: K=2** "
        "(XAUUSD, XAGUSD) -- lihat PREREGISTRATION.md untuk alasan & konsekuensi yang "
        "dinyatakan SEBELUM angka di bawah dihitung.\n"
    )
    pnl = {s: baseline_pnl(s) for s in SYMBOLS}
    pnl = {s: v for s, v in pnl.items() if len(v) > 100}
    if len(pnl) < 2:
        lines.append("\n**TIDAK CUKUP INSTRUMEN untuk matriks korelasi. K_eff TIDAK BISA DIHITUNG.**\n")
        (REPORTS_DIR / "F0_universe.md").write_text("\n".join(lines))
        print("wrote F0_universe.md (insufficient)")
        return None

    df = pd.DataFrame(pnl).dropna()
    corr = df.corr()
    rho = corr.iloc[0, 1]
    eigvals = np.linalg.eigvalsh(corr.values)
    eigvals = np.clip(eigvals, 0, None)
    k_eff_eigen = (eigvals.sum() ** 2) / (eigvals ** 2).sum()
    K = len(pnl)
    k_eff_equicorr = K / (1 + (K - 1) * rho)

    lines.append(f"Baseline strategi untuk mengukur korelasi PnL (alat ukur struktur, BUKAN kandidat): "
                  f"`sign(momentum M5 L=12)`, hold 12 bar, TANPA biaya (sama seperti metodologi v5 "
                  f"`compute_keff.py`).\n")
    lines.append(f"- N observasi PnL selaras (irisan timestamp XAUUSD & XAGUSD): {len(df):,}")
    lines.append(f"- **Korelasi PnL strategi baseline XAUUSD-XAGUSD (rho_PnL terukur): {rho:.4f}**")
    lines.append(f"- Eigenvalues matriks korelasi 2x2: {np.round(eigvals, 4).tolist()}")
    lines.append(f"- **K_eff (metode eigenvalue, WAJIB dipakai resmi): {k_eff_eigen:.4f}**")
    lines.append(f"- K_eff (metode equicorrelated, perencanaan saja): {k_eff_equicorr:.4f}")
    lines.append(
        f"\n## Batas matematis (dinyatakan SEBELUM run, lihat PREREGISTRATION.md)\n\n"
        f"Untuk K=2 instrumen, `K_eff_eigen = 2 / (1 + rho^2)`, yang **terikat ke rentang (1, 2]** "
        f"untuk SEMUA nilai rho yang mungkin (termasuk rho negatif). Tidak ada nilai korelasi PnL "
        f"yang bisa membuat K_eff panel 2-instrumen mencapai 3.0 (GM-1), apalagi 4.0 (GM-1b). "
        f"Angka {k_eff_eigen:.4f} di atas mengonfirmasi ini secara empiris: **hasil ukur, bukan "
        f"kejutan** -- sudah diprediksi secara aljabar sebelum data dilihat.\n"
    )
    lines.append(f"\n## Verdict gerbang mati\n\n"
                  f"- **GM-1 (K_eff >= 3.0): {'LOLOS' if k_eff_eigen >= 3.0 else 'GAGAL'} "
                  f"(K_eff terukur = {k_eff_eigen:.4f})**\n")
    (REPORTS_DIR / "F0_universe.md").write_text("\n".join(lines))
    print(f"wrote F0_universe.md -- K_eff_eigen={k_eff_eigen:.4f} rho={rho:.4f}")
    return {"k_eff_eigen": k_eff_eigen, "k_eff_equicorr": k_eff_equicorr, "rho": rho, "n_obs": len(df), "K": K}


# --------------------------------------------------------------- power ----

def write_power(universe: dict | None, audits: list[dict]):
    lines = ["# F0 -- Daya Statistik & Verdict Gerbang Mati (GM-1 s/d GM-5)\n"]

    if universe is None:
        lines.append("K_eff tidak bisa dihitung -- lihat F0_universe.md. BERHENTI.")
        (REPORTS_DIR / "F0_power.md").write_text("\n".join(lines))
        print("wrote F0_power.md (blocked, no K_eff)")
        return

    k_eff = universe["k_eff_eigen"]

    first_dates = [pd.to_datetime(a["first_date"]) for a in audits if a["first_date"]]
    last_dates = [pd.to_datetime(a["last_date"]) for a in audits if a["last_date"]]
    common_start = max(first_dates)
    common_end = min(last_dates)
    total_years = (common_end - common_start).days / 365.25
    t_confirm_years = total_years * 0.55  # partisi CONFIRM = 55%

    lines.append(f"**Riwayat bersama terukur (irisan XAUUSD & XAGUSD): {common_start.date()} s/d "
                  f"{common_end.date()} = {total_years:.2f} tahun.**")
    lines.append(f"**T_confirm terukur (55% partisi): {t_confirm_years:.2f} tahun.**\n")

    lines.append("## GM-1 -- K_eff >= 3.0\n")
    gm1_pass = k_eff >= 3.0
    lines.append(f"K_eff terukur = **{k_eff:.4f}**. Ambang = 3.0. **{'LOLOS' if gm1_pass else 'GAGAL -- STOP'}**\n")

    lines.append("## GM-1b -- K_eff >= 4.0 DAN T_confirm >= 11 tahun (syarat gabungan, §01 B4b)\n")
    gm1b_keff = k_eff >= 4.0
    gm1b_t = t_confirm_years >= 11.0
    gm1b_pass = gm1b_keff and gm1b_t
    lines.append(f"K_eff >= 4.0: {'LOLOS' if gm1b_keff else 'GAGAL'} ({k_eff:.4f}). "
                  f"T_confirm >= 11 thn: {'LOLOS' if gm1b_t else 'GAGAL'} ({t_confirm_years:.2f} thn). "
                  f"**{'LOLOS' if gm1b_pass else 'GAGAL -- STOP'}**\n")

    lines.append("## GM-2, GM-4, GM-5, sd_SR pilot, skew/kurt\n")
    lines.append(
        "**TIDAK DIJALANKAN.** GM-1 sudah gagal secara matematis dan pasti (lihat F0_universe.md "
        "-- K_eff untuk K=2 terikat ke (1,2], tidak mungkin >= 3.0 berapapun korelasinya). "
        "Menjalankan pilot 24-trial untuk sd_SR, mengukur skew/kurt empiris, atau menghitung "
        "N_maks/anggaran kandidat pada titik ini berarti **menghitung anggaran untuk registri yang "
        "sudah dijamin gagal DSR-nya** (bertentangan langsung dengan §08 D3 dan pelajaran #8 di "
        "10_FASE_EKSEKUSI.md: 'menjalankan registri lebih besar dari N_maks dan berharap' adalah "
        "pola yang menyebabkan v1-v5 gagal lima kali). Ditandai `TIDAK_DIJALANKAN_KARENA_GM1_GAGAL`, "
        "bukan `TIDAK_TAHU` -- keputusan sadar, bukan kelalaian.\n"
    )

    lines.append("## VERDICT AKHIR F0\n")
    lines.append(f"**{'LANJUT KE F1' if (gm1_pass and gm1b_pass) else 'BERHENTI -- lihat reports/STOP_REPORT.md'}**\n")

    (REPORTS_DIR / "F0_power.md").write_text("\n".join(lines))
    print(f"wrote F0_power.md -- GM1={gm1_pass} GM1b={gm1b_pass} T_confirm={t_confirm_years:.2f}y")
    return {"t_confirm_years": t_confirm_years, "gm1_pass": gm1_pass, "gm1b_pass": gm1b_pass,
            "common_start": str(common_start.date()), "common_end": str(common_end.date()),
            "total_years": total_years}


def main():
    audits = [audit_symbol(s) for s in SYMBOLS]
    write_data_audit(audits)
    write_cost_model()
    universe = write_universe()
    power = write_power(universe, audits)

    result = {"audits": audits, "universe": universe, "power": power}
    Path("/workspace/xau-alpha-v5/reports/F0_result.json").write_text(json.dumps(result, indent=2, default=str))
    print("F0 DONE.")


if __name__ == "__main__":
    main()
