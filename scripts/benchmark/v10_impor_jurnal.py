#!/usr/bin/env python3
"""V10 -- IMPOR RUMUS DARI JURNAL. Kelas informasi BARU (bukan varian harga),
diambil dari literatur akademik terverifikasi (DOI/SSRN resolve, dicek manual
lewat WebSearch/WebFetch sebelum kode ini ditulis -- lihat PREREG di bawah
untuk sitasi lengkap tiap formula). Anggaran keras: MAKSIMAL 20 formula.
Gerbang G1-G6 SAMA PERSIS dengan L13/L15 (G6 baru: dekai pasca-publikasi).

ATURAN YANG DIIKUTI KETAT:
- Parameter ASLI dari paper di lintasan pertama (tau=1.0 default proyek untuk
  paper yang bukan aturan-trading eksplisit; grid tambahan HANYA jika lolos G1).
- Tanda diprediksi SEBELUM diuji (lihat predicted_sign di PREREG) -- kalau
  tanda kebalikannya yang lolos, itu DIBUANG dan dicatat sebagai data-mining,
  BUKAN dipakai.
- Korelasi terhadap registry lama diuji SEBELUM kandidat diterima ke gerbang.
- Semua estimator kausal (bar t pakai data <=t saja); makro/COT/GVZ dilag 1
  hari penuh dari tanggal RILIS; fit regresi/kointegrasi HANYA di LATIH.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m1, load_m5, measure_cost_bps, REPORTS, FIG_DIR
from src.stats.effective_n import effective_n as ldp_effective_n
from l13_lomba_makro import load_xau_d1, load_macro, build_macro_features, build_signals as build_mac_signals
from lomba4_entry import build_signals as build_signals_m5
from lomba2_tren import ols_slope_tstat, KalmanDrift
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

LATIH_FRAC = 0.60
UJI_FRAC = 0.25
TAU_DEFAULT = 1.0

# ================= PRE-REGISTRASI (ditulis SEBELUM sinyal diuji) =================
PREREG = {
    "XAS01": dict(
        kelas="Lintas-aset lead-lag",
        citation="Escribano & Granger (1998), Journal of Forecasting 17(2):81-107",
        doi="10.1002/(SICI)1099-131X(199803)17:2<81::AID-FOR680>3.0.CO;2-",
        tahun_terbit=1998, sampel_asli="Gold & silver spot London, harian, 1971-1994",
        mekanisme="Gold dan silver berbagi faktor jangka-panjang logam-mulia bersama; deviasi gold dari hubungan kointegrasi historisnya dengan silver cenderung kembali (mean-revert).",
        tanda_prediksi="ECT positif (gold relatif mahal vs silver) -> gold TURUN; sign(sinyal)=-sign(ECT)."),
    "OPT01": dict(
        kelas="Options-implied",
        citation="Nguyen, Prokopczuk & Wese Simen (2019), Journal of International Money and Finance 94:140-159",
        doi="10.1016/j.jimonfin.2019.02.011",
        tahun_terbit=2019, sampel_asli="Opsi emas COMEX, 2004-2016",
        mekanisme="Variance risk premium (implied vol GVZ dikurangi realized vol) mengompensasi penjual opsi atas risiko volatilitas; VRP tinggi historisnya memprediksi risk premium gold positif.",
        tanda_prediksi="VRP positif (implied>realized) -> gold NAIK; sign(sinyal)=sign(VRP)."),
    "COT02": dict(
        kelas="Crowding/positioning (keluarga MAC05)",
        citation="Chen & Mo (2023), Journal of Commodity Markets 31, art.100337 (SSRN abstract_id=4166076)",
        doi="SSRN:4166076",
        tahun_terbit=2023, sampel_asli="CFTC Disaggregated COT emas, 2006-06 s/d 2022-02",
        mekanisme="Money manager (DCOT) berbeda dari Non-Commercial legacy (MAC05) -- kategori spekulatif lebih sempit dan lebih 'hot money'; posisi net yang sangat crowded secara historis mendahului pembalikan saat crowding terurai.",
        tanda_prediksi="z(mm_net) tinggi (crowded long) -> gold TURUN; sign(sinyal)=-sign(z_mm_net)."),
    "MIC01": dict(
        kelas="Order flow proxy (tick)",
        citation="Amihud (2002), Journal of Financial Markets 5(1):31-56",
        doi="10.1016/S1386-4181(01)00024-6",
        tahun_terbit=2002, sampel_asli="Saham NYSE, 1964-1997 (bulanan)",
        mekanisme="Rasio |return|/volume mengukur dampak-harga per unit aliran order; periode illikuid (dampak-harga tinggi) secara historis dikompensasi dengan return berikutnya lebih tinggi (premi likuiditas).",
        tanda_prediksi="ILLIQ tinggi -> gold NAIK; sign(sinyal)=sign(z_ILLIQ). CATATAN: volume asli Amihud=dolar volume saham; di sini dipakai bid_vol Dukascopy (proksi tick, BUKAN volume eksekusi sebenarnya krn XAU OTC/CFD)."),
    "MIC02": dict(
        kelas="Order flow proxy (tick)",
        citation="Kyle (1985), Econometrica 53(6):1315-1335",
        doi="10.2307/1913210",
        tahun_terbit=1985, sampel_asli="Model teoretis (bukan empiris pasar tunggal)",
        mekanisme="Koefisien regresi perubahan harga pada aliran order bertanda (lambda) mengukur intensitas informed trading relatif noise trading; lambda tinggi historisnya berasosiasi dengan kelanjutan (persistence) arah harga.",
        tanda_prediksi="lambda tinggi -> arah HARI BERJALAN berlanjut ke hari berikutnya; sign(sinyal)=sign(return_hari_ini) DIGERBANG oleh |z_lambda|>=tau."),
    "MIC03": dict(
        kelas="Order flow proxy (tick)",
        citation="Roll (1984), The Journal of Finance 39(4):1127-1139",
        doi="10.1111/j.1540-6261.1984.tb03897.x",
        tahun_terbit=1984, sampel_asli="Model teoretis + ilustrasi empiris obligasi korporasi AS",
        mekanisme="Kovariansi serial negatif perubahan harga berasal dari bid-ask bounce; besarnya (spread implisit) adalah proksi biaya likuiditas -- mekanisme premi-likuiditas sama seperti MIC01.",
        tanda_prediksi="spread implisit lebar -> gold NAIK; sign(sinyal)=sign(z_spread)."),
    "SEA01": dict(
        kelas="Musiman",
        citation="Lakonishok & Smidt (1988), Review of Financial Studies 1(4):403-425",
        doi="10.1093/rfs/1.4.403",
        tahun_terbit=1988, sampel_asli="DJIA, 1897-1986",
        mekanisme="Arus kas institusional turn-of-month (gaji, rebalancing dana pensiun/reksadana) terkonsentrasi di hari terakhir bulan + 3 hari pertama bulan berikutnya; paper asli menemukan HAMPIR SELURUH return positif terkonsentrasi di jendela ini (implikasi: luar-TOM mendekati datar/negatif) -- diuji-transfer ke gold (bukan ekuitas, kelas aset berbeda).",
        tanda_prediksi="TOM window -> gold NAIK; luar-TOM -> gold TIDAK naik (komplemen dari temuan asli); sign(sinyal)=+1 saat TOM, -1 lainnya."),
    "SEA02": dict(
        kelas="Musiman",
        citation="French (1980), Journal of Financial Economics 8(1):55-69 [mekanisme]; Kohli (2012), Investment Management and Financial Innovations 9(2) [konfirmasi keberadaan efek hari-minggu pada emas]",
        doi="10.1016/0304-405X(80)90021-5",
        tahun_terbit=1980, sampel_asli="S&P500, 1953-1977 (French); Gold & silver 1980-2012 (Kohli)",
        mekanisme="Akumulasi informasi akhir pekan dan kondisi likuiditas/penyelesaian berbeda antar hari perdagangan menghasilkan pola return sistematis per hari (efek weekend klasik); Kohli (2012) mengonfirmasi KEBERADAAN efek hari-minggu pada emas tanpa merinci tanda per-hari -- tanda yang diuji di sini mengambil pola klasik French (Senin negatif, Jumat positif), BUKAN angka spesifik Kohli (ditandai eksplisit).",
        tanda_prediksi="Senin -> gold TURUN, Jumat -> gold NAIK (hari lain dikecualikan); sign(sinyal)=-1 Senin, +1 Jumat."),
    "EVT01": dict(
        kelas="Event-driven",
        citation="Lucca & Moench (2015), The Journal of Finance 70(1):329-371",
        doi="10.1111/jofi.12196",
        tahun_terbit=2015, sampel_asli="Indeks ekuitas AS, 1994-2011 (jendela 24 jam pra-FOMC)",
        mekanisme="Resolusi ketidakpastian kebijakan moneter terkompresi di 24 jam sebelum pengumuman FOMC terjadwal menghasilkan drift ekuitas naik yang kuat; sebagai aset safe-haven yang secara historis berkorelasi negatif dengan sentimen risk-on ekuitas, gold diprediksi menunjukkan drift BERLAWANAN pada jendela yang sama.",
        tanda_prediksi="Hari bursa terakhir sebelum tanggal keputusan FOMC -> gold TURUN; hari lain -> gold TIDAK turun (komplemen); sign(sinyal)=-1 pra-FOMC, +1 lainnya. CATATAN: tanggal FOMC diverifikasi HANYA 2021-2026 dari federalreserve.gov/monetarypolicy/fomccalendars.htm (halaman resmi hanya menyimpan riwayat ~5 tahun) -- TIDAK ditebak untuk tahun sebelumnya."),
}

FOMC_DATES_VERIFIED = pd.to_datetime([
    "2021-01-27", "2021-03-17", "2021-04-28", "2021-06-16", "2021-07-28", "2021-09-22", "2021-11-03", "2021-12-15",
    "2022-01-26", "2022-03-16", "2022-05-04", "2022-06-15", "2022-07-27", "2022-09-21", "2022-11-02", "2022-12-14",
    "2023-02-01", "2023-03-22", "2023-05-03", "2023-06-14", "2023-07-26", "2023-09-20", "2023-11-01", "2023-12-13",
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10",
    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09",
])

DIBUANG_SEBELUM_UJI = [
    dict(id="TERM01-03 (contango/backwardation, convenience yield, lease rate)",
         alasan="DATA_TIDAK_TERSEDIA -- GOFO/LBMA lease rate dihentikan 2015, tidak ada API gratis untuk kurva futures COMEX multi-maturity (Stooq diblokir bot-check JS, FirstRateData/Kaggle berbayar, FRED tidak punya seri lease rate). Formula dari Gorton & Rouwenhorst (2006, NBER w10595) dan Erb & Harvey (2006, FAJ 62(2):69-97) valid secara sitasi tapi tidak bisa diimplementasikan tanpa data kurva."),
    dict(id="XAS02 (GDX miners lead-lag gold)",
         alasan="TIDAK_ADA_SITASI_AKADEMIK -- pencarian hanya menemukan artikel industri/blog (Sprott, discoveryalert, dst), bukan paper peer-review dengan mekanisme dan tanda yang bisa dipra-registrasi. Ditolak per aturan anti-ngasal (tanpa mekanisme -> tolak)."),
    dict(id="OPT02 (skew opsi emas)", alasan="DATA_TIDAK_TERSEDIA -- perlu rantai opsi (option chain) lengkap, tidak ada sumber gratis."),
    dict(id="OPT03 (struktur tenor GVZ)", alasan="DATA_TIDAK_TERSEDIA -- FRED hanya punya GVZCLS front-month, tidak ada tenor lain gratis."),
    dict(id="COT03 (rasio konsentrasi top-4/top-8 trader)",
         alasan="SITASI_TIDAK_TERVERIFIKASI -- kandidat paper (management-review.org, 'Traders Concentration, Hedging Pressure, and Risk...') PDF tidak bisa diparse untuk verifikasi DOI/mekanisme dalam anggaran riset; bukan berarti idenya salah, tapi aturan anti-ngasal melarang mengarang detail yang tidak terverifikasi. Data konsentrasi (Conc_Net_LE_4/8_TDR) SUDAH terunduh di dcot_gold.parquet kalau nanti sitasi valid ditemukan."),
    dict(id="EVT02 (CPI/NFP surprise-day momentum, Christie-David/Chaudhry/Koch 2000)",
         alasan="DATA_TIDAK_TERSEDIA_LENGKAP -- mekanisme dan sitasi (JEB 52(5):405-421, DOI 10.1016/S0148-6195(00)00029-1) TERVERIFIKASI, tapi jadwal tanggal rilis CPI/NFP presisi multi-tahun tidak berhasil diverifikasi lewat sumber gratis dalam anggaran waktu riset ini (beda dengan FOMC yang halaman resminya langsung memberi tabel). Tidak ditebak."),
    dict(id="SEA03 (sesi London/NY overlap)",
         alasan="MISMATCH_HORIZON -- mekanisme (Ranaldo 2009, J. Banking & Finance 33(12):2199-2206, DOI 10.1016/j.jbankfin.2009.05.019) TERVERIFIKASI, tapi efeknya secara definisi berskala intraday-jam; UJI_BUNUH_M5 sudah membuktikan M5 mati, dan menguji versi 'return D1 tutup-ke-tutup dikondisikan sesi mana yang buka' mengencerkan mekanisme aslinya sampai tidak representatif. Dibuang karena horizon, bukan gagal gerbang."),
]


def zscore(x: pd.Series, window: int = 252, min_periods: int = 60) -> pd.Series:
    m = x.rolling(window, min_periods=min_periods).mean()
    s = x.rolling(window, min_periods=min_periods).std()
    return (x - m) / s.replace(0, np.nan)


# ================= Bangun kerangka D1 dasar + fitur =================

def build_base_frame():
    d1 = load_xau_d1()
    d1["date"] = pd.to_datetime(d1["date"]).astype("datetime64[ns]")
    return d1


def build_xag_d1():
    xag = pd.read_parquet("/workspace/data/bars_candles/XAGUSD_M5.parquet", columns=["bar_time", "mid_close"])
    xag["date"] = pd.to_datetime(xag["bar_time"]).dt.date
    d1 = xag.groupby("date").agg(xag_close=("mid_close", "last")).reset_index()
    d1["date"] = pd.to_datetime(d1["date"]).astype("datetime64[ns]")
    return d1.sort_values("date").reset_index(drop=True)


def build_dcot():
    dcot = pd.read_parquet("/workspace/data/macro/dcot_gold.parquet")
    dcot["date"] = pd.to_datetime(dcot["date"]).astype("datetime64[ns]")
    return dcot


def build_micro_daily():
    """Amihud, Kyle-lambda, Roll-spread harian dari M5 XAU (2021-2026)."""
    m5 = load_m5()
    m5 = m5.copy()
    m5["date"] = m5["bar_time"].dt.date
    logp = np.log(m5["mid_close"].values)
    ret = np.diff(logp, prepend=logp[0])
    m5["ret"] = ret
    m5["bid_vol_safe"] = m5["bid_vol"].clip(lower=1e-6)
    m5["amihud_bar"] = np.abs(m5["ret"]) / m5["bid_vol_safe"]
    m5["signed_flow"] = np.sign(m5["ret"]) * m5["bid_vol"]

    rows = []
    for date, g in m5.groupby("date"):
        if len(g) < 50:
            continue
        illiq = float(g["amihud_bar"].replace([np.inf, -np.inf], np.nan).mean())
        r = g["ret"].values
        f = g["signed_flow"].values
        if np.std(f) > 1e-9:
            beta = np.cov(f, r)[0, 1] / np.var(f)
        else:
            beta = np.nan
        cov1 = np.cov(r[:-1], r[1:])[0, 1] if len(r) > 5 else np.nan
        roll_spread = 2 * np.sqrt(-cov1) if pd.notna(cov1) and cov1 < 0 else 0.0
        day_ret_close_to_close = float(g["ret"].sum())
        rows.append({"date": pd.Timestamp(date), "illiq": illiq, "kyle_lambda": beta,
                      "roll_spread": roll_spread, "day_ret_bps": day_ret_close_to_close * 1e4})
    out = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    out["date"] = pd.to_datetime(out["date"]).astype("datetime64[ns]")
    return out


def lag1(df, date_col, value_cols):
    d = df.copy()
    d[date_col] = (pd.to_datetime(d[date_col]) + pd.Timedelta(days=1)).astype("datetime64[ns]")
    return d[[date_col] + value_cols]


def build_all_signals(d1, fred, cot_legacy, dcot, xag_d1, micro):
    n_total = len(d1)
    latih_end = int(n_total * LATIH_FRAC)
    logp = np.log(d1["mid_close"].values)
    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))

    sig = pd.DataFrame({"date": d1["date"]})

    # ---- SEA01: turn-of-month ----
    dts = pd.DatetimeIndex(d1["date"])
    is_month_end = dts.to_series(index=range(len(dts))).apply(lambda d: (d + pd.offsets.BDay(1)).month != d.month)
    day_of_month_pos = np.zeros(n_total, dtype=int)
    tom = np.zeros(n_total)
    last_month = None
    trading_day_seq = 0
    for i, d in enumerate(dts):
        if last_month != d.month:
            trading_day_seq = 0
            last_month = d.month
        trading_day_seq += 1
        day_of_month_pos[i] = trading_day_seq
    is_first3 = day_of_month_pos <= 3
    is_last_day = np.array([bool(is_month_end.iloc[i]) for i in range(n_total)])
    tom_mask = is_first3 | is_last_day
    sig["SEA01_turn_of_month"] = np.where(tom_mask, 1.0, -1.0)

    # ---- SEA02: day-of-week (Senin turun, Jumat naik, lainnya NaN) ----
    dow = dts.dayofweek.values  # Mon=0..Sun=6
    sea02 = np.full(n_total, np.nan)
    sea02[dow == 0] = -1.0
    sea02[dow == 4] = 1.0
    sig["SEA02_day_of_week"] = sea02

    # ---- EVT01: pra-FOMC (hari bursa terakhir sebelum tanggal keputusan) ----
    evt01 = np.full(n_total, np.nan)
    date_arr = pd.DatetimeIndex(d1["date"])
    idx_map = {d: i for i, d in enumerate(date_arr)}
    for fdate in FOMC_DATES_VERIFIED:
        prior = date_arr[date_arr < fdate]
        if len(prior) == 0:
            continue
        pre_day = prior.max()
        if pre_day in idx_map:
            evt01[idx_map[pre_day]] = -1.0
    in_fomc_window = (date_arr >= FOMC_DATES_VERIFIED.min()) & (date_arr <= FOMC_DATES_VERIFIED.max())
    evt01[np.isnan(evt01) & in_fomc_window] = 1.0
    sig["EVT01_pre_fomc"] = evt01

    # ---- OPT01: gold VRP (GVZ - realized vol 22d) ----
    fred2 = fred[["date", "GVZCLS"]].copy()
    fred2["date"] = pd.to_datetime(fred2["date"]).astype("datetime64[ns]")
    fred2 = lag1(fred2, "date", ["GVZCLS"])
    m = d1.merge(fred2, on="date", how="left")
    rv22 = day_ret.rolling(22, min_periods=15).std() * np.sqrt(252) * 100
    vrp = m["GVZCLS"].values - rv22.values
    sig["OPT01_gold_vrp"] = zscore(pd.Series(vrp), window=252)

    # ---- XAS01: gold-silver cointegration ECT ----
    m = d1.merge(xag_d1, on="date", how="left")
    valid_xas = m["xag_close"].notna().values
    logx, logs = np.log(d1["mid_close"].values), np.full(n_total, np.nan)
    logs[valid_xas] = np.log(m.loc[valid_xas, "xag_close"].values)
    # XAG hanya tersedia 2021-2026 (jauh setelah latih_end global 2003-2026);
    # pakai 60% PERTAMA dari rentang valid XAG sendiri untuk fit kointegrasi,
    # bukan latih_end global -- supaya ada porsi LATIH yang genuinely sebelum UJI.
    valid_idx = np.where(valid_xas)[0]
    local_latih_end = valid_idx[int(len(valid_idx) * LATIH_FRAC)] if len(valid_idx) > 50 else 0
    fit_mask = valid_xas.copy()
    fit_mask[local_latih_end:] = False
    if fit_mask.sum() > 100:
        X = np.column_stack([np.ones(fit_mask.sum()), logs[fit_mask]])
        beta, *_ = np.linalg.lstsq(X, logx[fit_mask], rcond=None)
        ect = np.full(n_total, np.nan)
        ect[valid_xas] = logx[valid_xas] - (beta[0] + beta[1] * logs[valid_xas])
        sig["XAS01_gold_silver_ect"] = -zscore(pd.Series(ect), window=60, min_periods=30)
    else:
        sig["XAS01_gold_silver_ect"] = np.nan

    # ---- COT02: managed money crowding (DCOT) ----
    dcot2 = dcot[["date", "mm_net"]].copy()
    dcot2 = lag1(dcot2, "date", ["mm_net"])
    m = d1.merge(dcot2, on="date", how="left").sort_values("date")
    m["mm_net"] = m["mm_net"].ffill(limit=6)
    z_mm = zscore(m["mm_net"].reset_index(drop=True), window=52 * 5, min_periods=52)
    sig["COT02_managed_money_crowd"] = -z_mm

    # ---- MIC01-03: micro daily (2021-2026) ----
    micro2 = micro.copy()
    micro2 = lag1(micro2, "date", ["illiq", "kyle_lambda", "roll_spread", "day_ret_bps"])
    m = d1.merge(micro2, on="date", how="left")
    sig["MIC01_amihud"] = zscore(m["illiq"], window=60, min_periods=30)
    z_lambda = zscore(m["kyle_lambda"], window=60, min_periods=30)
    prior_ret_sign = np.sign(m["day_ret_bps"].values)
    valid_mic02 = np.isfinite(z_lambda.values) & np.isfinite(prior_ret_sign)
    mic02 = np.where(valid_mic02, prior_ret_sign * np.abs(z_lambda.values), np.nan)
    sig["MIC02_kyle_lambda_gated"] = mic02
    sig["MIC02_z_gate"] = z_lambda  # dipakai untuk tau (magnitude gate terpisah dari arah)
    sig["MIC03_roll_spread"] = zscore(m["roll_spread"], window=60, min_periods=30)

    return sig


def build_registry(d1, fred, cot_legacy):
    """Registry sinyal LAMA (v6-v9) untuk uji korelasi -- diagregasi ke D1."""
    n_total = len(d1)
    latih_end = int(n_total * LATIH_FRAC)
    reg = pd.DataFrame({"date": d1["date"]})

    m5 = load_m5()
    sig_m5 = build_signals_m5(m5)
    sig_m5["date"] = m5["bar_time"].dt.date
    daily_m5 = sig_m5.groupby("date").last().reset_index()
    daily_m5["date"] = pd.to_datetime(daily_m5["date"]).astype("datetime64[ns]")
    reg = reg.merge(daily_m5, on="date", how="left", suffixes=("", "_m5reg"))

    fred_lag = fred.copy()
    fred_lag["date"] = pd.to_datetime(fred_lag["date"]).astype("datetime64[ns]")
    cot_lag = cot_legacy.copy()
    df_mac = build_macro_features(d1, fred_lag, cot_lag)
    mac_sig = build_mac_signals(df_mac, latih_end)
    for c in mac_sig.columns:
        reg[c] = mac_sig[c].values

    logp = pd.Series(np.log(d1["mid_close"].values))
    reg["TREND_ols_20d"] = logp.rolling(21).apply(lambda y: ols_slope_tstat(y.values)[0], raw=False)
    kf_std = float(np.std(np.diff(np.log(d1["mid_close"].values[:latih_end]))))
    px = d1["mid_close"].values
    kf = KalmanDrift(q_level=(kf_std * px[0]) ** 2 * 0.01, q_drift=(kf_std * px[0]) ** 2 * 1e-4, r_obs=(kf_std * px[0]) ** 2 * 4)
    reg["TREND_kalman_drift"] = kf.run(px)

    return reg


def screen_correlation(sig, registry, candidate_cols):
    rows = []
    for c in candidate_cols:
        if c not in sig.columns:
            continue
        s = sig[c].astype(float)
        best_abs, best_name = 0.0, None
        for r in registry.columns:
            if r == "date":
                continue
            rr = registry[r].astype(float)
            common = s.notna() & rr.notna()
            if common.sum() < 100:
                continue
            corr = float(np.corrcoef(s[common], rr[common])[0, 1])
            if abs(corr) > best_abs:
                best_abs, best_name = abs(corr), r
        rows.append({"peserta": c, "max_abs_corr": best_abs, "vs": best_name})
    return pd.DataFrame(rows)


def check_g1(direction, net_d):
    l, s = direction > 0, direction < 0
    pl = net_d[l].sum() if l.any() else np.nan
    ps = net_d[s].sum() if s.any() else np.nan
    return (pd.notna(pl) and pd.notna(ps) and pl > 0 and ps > 0), pl, ps


def check_g3(direction, net, entry_bt, regime_bounds):
    res = []
    for name, s0, s1 in regime_bounds:
        m = (entry_bt >= s0) & (entry_bt < s1)
        n = int(m.sum())
        exp = float(net[m].mean()) if n >= 10 else np.nan
        res.append((name, n, exp))
    npos = sum(1 for _, n, e in res if pd.notna(e) and e > 0)
    return npos >= 2, res


def check_g4(net, entry_idx, uji_end, n_windows=10):
    edges = np.linspace(0, uji_end, n_windows + 1).astype(int)
    wf = []
    for w in range(n_windows):
        lo, hi = edges[w], edges[w + 1]
        m = (entry_idx >= lo) & (entry_idx < hi)
        n = int(m.sum())
        exp = float(net[m].mean()) if n >= 5 else np.nan
        pnl = float(net[m].sum()) if n >= 5 else 0.0
        wf.append((w + 1, n, exp, pnl))
    npos = sum(1 for _, n, e, p in wf if pd.notna(e) and e > 0)
    total_pnl = sum(p for _, n, e, p in wf)
    top2 = sorted(wf, key=lambda x: -abs(x[3]))[:2]
    top2_share = sum(x[3] for x in top2) / total_pnl if total_pnl != 0 else np.nan
    passed = npos >= 7 and pd.notna(top2_share) and abs(top2_share) <= 0.60
    return passed, npos, top2_share, wf


def check_g6(net, entry_bt, pub_year):
    cutoff = pd.Timestamp(f"{pub_year}-01-01")
    post = entry_bt >= cutoff
    n_post = int(post.sum())
    if n_post < 10:
        return None, n_post
    exp_post = float(net[post].mean())
    return exp_post > 0, n_post


def evaluate_formula(fid, z, d1, regime_bounds, uji_end, latih_uji_mask, cost_base, cost_worst, day_ret_demeaned_bps, day_ret_bps, extra_gate=None, tau_grid=(1.0,)):
    date_arr = d1["date"].values
    pub_year = PREREG[fid]["tahun_terbit"]
    rows = []
    for tau in tau_grid:
        if extra_gate is not None:
            take = (np.abs(extra_gate) >= tau) & latih_uji_mask & np.isfinite(day_ret_bps) & np.isfinite(z)
        else:
            take = (np.abs(z) >= tau) & latih_uji_mask & np.isfinite(day_ret_bps) & np.isfinite(z)
        n = int(take.sum())
        if n < 30:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "n<30"})
            continue
        direction = np.sign(z)[take]
        net_base = direction * day_ret_bps[take] - cost_base
        net_demeaned = direction * day_ret_demeaned_bps[take] - cost_base
        net_worst = direction * day_ret_bps[take] - cost_worst
        entry_idx = np.where(take)[0]
        entry_bt = date_arr[take]

        g1, pl, ps = check_g1(direction, net_demeaned)
        rev_g1, rev_pl, rev_ps = check_g1(-direction, -net_demeaned)
        note = " [CATATAN: tanda TERBALIK akan LOLOS G1 -- data mining, TETAP DIBUANG]" if (not g1 and rev_g1) else ""
        if not g1:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G1",
                          "pnl_long_demean": pl, "pnl_short_demean": ps, "catatan": note})
            continue
        g2 = float(net_worst.mean()) > 0
        if not g2:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G2",
                          "expectancy_worst": float(net_worst.mean())})
            continue
        g3, g3_detail = check_g3(direction, net_base, entry_bt, regime_bounds)
        if not g3:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G3", "g3_detail": g3_detail})
            continue
        g4, g4_npos, g4_top2, _ = check_g4(net_base, entry_idx, uji_end)
        if not g4:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G4",
                          "wf_positive": g4_npos, "wf_top2_share": g4_top2})
            continue
        starts = entry_idx; ends = np.minimum(entry_idx + 1, len(d1))
        eff_n = ldp_effective_n(starts, ends, len(d1))
        se = net_base.std(ddof=1) / np.sqrt(max(eff_n, 2))
        t_stat = net_base.mean() / se if se > 0 else 0.0
        g5 = t_stat >= 3.0
        if not g5:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G5", "eff_n": eff_n, "t_stat": t_stat})
            continue
        g6, n_post = check_g6(net_base, pd.Series(entry_bt), pub_year)
        if g6 is None:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G6_n_kurang", "n_post_pub": n_post})
            continue
        if not g6:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G6", "n_post_pub": n_post})
            continue
        rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "LOLOS",
                      "expectancy_base_bps": float(net_base.mean()), "eff_n": eff_n, "t_stat": t_stat, "n_post_pub": n_post})
    return rows


def main():
    d1 = build_base_frame()
    fred, cot_legacy = load_macro()
    dcot = build_dcot()
    xag_d1 = build_xag_d1()
    print("Membangun fitur mikro harian dari M5 (Amihud/Kyle/Roll)...")
    micro = build_micro_daily()

    n_total = len(d1)
    latih_end = int(n_total * LATIH_FRAC)
    uji_end = int(n_total * (LATIH_FRAC + UJI_FRAC))
    latih_uji_mask = np.zeros(n_total, dtype=bool); latih_uji_mask[:uji_end] = True
    print(f"D1 XAU total={n_total:,} ({d1['date'].iloc[0].date()} s/d {d1['date'].iloc[uji_end-1].date()}), LATIH+UJI={uji_end:,}")

    m1 = load_m1()
    m1_mask = np.zeros(len(m1), dtype=bool); m1_mask[: int(len(m1) * 0.70)] = True
    cost_info = measure_cost_bps(m1, m1_mask)
    cost_base = cost_info["round_trip_cost_bps"]
    spread_p90 = m1.loc[m1_mask, "spread_bps"].dropna().pipe(lambda s: s[(s > 0) & (s < 500)]).quantile(0.90)
    cost_worst = spread_p90 * 2.5 + 0.28
    print(f"Biaya base={cost_base:.3f}bps, worst={cost_worst:.3f}bps")

    print("Membangun 9 sinyal V10...")
    sig = build_all_signals(d1, fred, cot_legacy, dcot, xag_d1, micro)

    print("Membangun registry sinyal LAMA (v6-v9) untuk uji korelasi...")
    registry = build_registry(d1, fred, cot_legacy)

    candidate_cols = ["XAS01_gold_silver_ect", "OPT01_gold_vrp", "COT02_managed_money_crowd",
                       "MIC01_amihud", "MIC02_kyle_lambda_gated", "MIC03_roll_spread",
                       "SEA01_turn_of_month", "SEA02_day_of_week", "EVT01_pre_fomc"]
    corr_df = screen_correlation(sig, registry, candidate_cols)
    print("\n=== UJI KORELASI vs REGISTRY LAMA (sebelum gerbang) ===")
    print(corr_df.round(4).to_string(index=False))

    CORR_THRESH = 0.30
    lolos_korelasi = corr_df[corr_df["max_abs_corr"] <= CORR_THRESH]["peserta"].tolist()
    gagal_korelasi = corr_df[corr_df["max_abs_corr"] > CORR_THRESH]

    logp = np.log(d1["mid_close"].values)
    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))
    roll_mean_60d = day_ret.rolling(60, min_periods=15).mean()
    demeaned_logp = np.cumsum((day_ret - roll_mean_60d.fillna(0)).values)
    day_ret_bps = (np.roll(logp, -1) - logp) * 1e4; day_ret_bps[-1] = np.nan
    day_ret_demeaned_bps = (np.roll(demeaned_logp, -1) - demeaned_logp) * 1e4; day_ret_demeaned_bps[-1] = np.nan

    regime_bounds = [
        ("2003-2011 bull", np.datetime64("2003-01-01"), np.datetime64("2012-01-01")),
        ("2012-2015 BEAR", np.datetime64("2012-01-01"), np.datetime64("2016-01-01")),
        ("2016-cutoff", np.datetime64("2016-01-01"), pd.Timestamp(d1["date"].iloc[uji_end - 1]).to_datetime64()),
    ]

    all_rows = []
    dibuang_korelasi = []
    for _, r in gagal_korelasi.iterrows():
        dibuang_korelasi.append(f"{r['peserta']}: korelasi {r['max_abs_corr']:.3f} vs {r['vs']} (>0.30) -- DITOLAK SEBELUM GERBANG")
        print(f"DITOLAK (korelasi): {r['peserta']} = {r['max_abs_corr']:.3f} vs {r['vs']}")

    print(f"\n=== GERBANG G1-G6 (hanya kandidat lolos uji korelasi) ===")
    for fid_full in lolos_korelasi:
        fid = fid_full.split("_")[0]
        extra_gate = sig["MIC02_z_gate"].values if fid == "MIC02" else None
        rows = evaluate_formula(fid, sig[fid_full].values, d1, regime_bounds, uji_end, latih_uji_mask,
                                  cost_base, cost_worst, day_ret_demeaned_bps, day_ret_bps,
                                  extra_gate=extra_gate, tau_grid=(TAU_DEFAULT,))
        # grid tambahan HANYA kalau lintasan pertama lolos G1 (maks 3 varian total)
        first_g1_pass = any(x["stopped_at"] not in ("n<30", "G1") for x in rows)
        if first_g1_pass and fid not in ("SEA01", "SEA02", "EVT01"):
            extra_rows = evaluate_formula(fid, sig[fid_full].values, d1, regime_bounds, uji_end, latih_uji_mask,
                                            cost_base, cost_worst, day_ret_demeaned_bps, day_ret_bps,
                                            extra_gate=extra_gate, tau_grid=(1.5, 2.0))
            rows += extra_rows
        all_rows += rows
        for r in rows:
            print(f"  {fid} tau={r['tau']}: n={r['n']}, stopped_at={r['stopped_at']}")

    df_rows = pd.DataFrame(all_rows)
    stop_counts = df_rows["stopped_at"].value_counts().to_dict() if len(df_rows) else {}
    survivors = df_rows[df_rows["stopped_at"] == "LOLOS"] if len(df_rows) else pd.DataFrame()
    total_trial = len(df_rows) + len(gagal_korelasi)

    print(f"\nDistribusi gerbang gugur: {stop_counts}")
    print(f"TOTAL SURVIVOR: {len(survivors)}/{len(df_rows)} (dari {len(candidate_cols)} formula diuji, {len(dibuang_korelasi)} ditolak pra-gerbang)")
    print(f"TOTAL TRIAL untuk DSR: {total_trial}")

    # ================= LAPORAN =================
    lines = ["# V10 -- IMPOR RUMUS DARI JURNAL\n",
              f"**Anggaran: {len(PREREG)} formula diimplementasikan dari {len(PREREG) + len(DIBUANG_SEBELUM_UJI)} kandidat "
              f"yang diriset (di bawah plafon 20). {len(DIBUANG_SEBELUM_UJI)} dibuang SEBELUM implementasi "
              f"(data tidak tersedia / sitasi tak terverifikasi / mismatch horizon / tanpa mekanisme). "
              f"TOTAL TRIAL untuk DSR = {total_trial} (9 formula x tau-grid bertingkat + kandidat gagal uji korelasi).**\n",
              "\n## Tabel Pra-Registrasi (ditulis SEBELUM sinyal diuji)\n",
              "| ID | Kelas | Sitasi | DOI/SSRN | Tahun | Sampel Asli | Mekanisme | Tanda Diprediksi |",
              "|---|---|---|---|---:|---|---|---|"]
    for fid, info in PREREG.items():
        lines.append(f"| {fid} | {info['kelas']} | {info['citation']} | {info['doi']} | {info['tahun_terbit']} | "
                      f"{info['sampel_asli']} | {info['mekanisme']} | {info['tanda_prediksi']} |")

    lines.append("\n## Kandidat DIBUANG sebelum implementasi (dengan alasan)\n")
    for d in DIBUANG_SEBELUM_UJI:
        lines.append(f"- **{d['id']}**: {d['alasan']}")

    lines.append(f"\n## Uji Korelasi vs Registry Lama (ambang |r|<=0.30, diuji SEBELUM gerbang)\n")
    lines.append(corr_df.round(4).to_markdown(index=False))
    if dibuang_korelasi:
        lines.append("\n**Ditolak karena korelasi:**\n\n" + "\n".join(f"- {x}" for x in dibuang_korelasi))

    lines.append(f"\n## Biaya & kerangka D1\n\nBiaya base={cost_base:.3f}bps, worst={cost_worst:.3f}bps. "
                  f"D1 XAU {d1['date'].iloc[0].date()} s/d {d1['date'].iloc[uji_end-1].date()} "
                  f"(HOLDOUT 15% terakhir tidak disentuh). Cakupan data per formula BERBEDA-BEDA (lihat catatan G3 di "
                  f"tabel hasil) -- XAS01/MIC01-03/EVT01 hanya 2021-2026 (XAG, M5 micro, FOMC terverifikasi), "
                  f"COT02 dari 2006, OPT01 dari 2008 (GVZ), SEA01/SEA02 penuh 2003-2026.\n")

    lines.append(f"\n## Hasil G1-G6 per kombinasi (tau x peserta)\n")
    if len(df_rows):
        lines.append(df_rows.to_markdown(index=False))
    lines.append(f"\n## Distribusi gerbang gugur\n\n" + "\n".join(f"- {k}: {v}" for k, v in sorted(stop_counts.items(), key=lambda x: -x[1])))

    if len(survivors):
        lines.append(f"\n## SURVIVOR ({len(survivors)})\n\n" + survivors.round(4).to_markdown(index=False))
        lines.append(f"\n## L14 -- syarat terpenuhi, lanjut Bagian B-E dengan formula ini SAJA.\n")
    else:
        lines.append("\n## NOL SURVIVOR\n\nSyarat L14 (>=1 lolos G1-G6) TIDAK terpenuhi. Bagian B-E tidak dikerjakan. "
                      "Nol dari 9 rumus jurnal berkualitas adalah jawaban, bukan alasan mencari 20 lagi.\n")

    (REPORTS / "V10_IMPOR_JURNAL.md").write_text("\n".join(lines))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    ax = axes[0]
    if stop_counts:
        labels = list(stop_counts.keys()); values = [stop_counts[k] for k in labels]
        colors = ["#2ca02c" if k == "LOLOS" else "#d62728" for k in labels]
        ax.bar(labels, values, color=colors)
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_title(f"V10: {len(survivors)}/{len(df_rows)} lolos G1-G6")
    ax.set_ylabel("jumlah kombinasi")

    ax = axes[1]
    ax.barh(corr_df["peserta"], corr_df["max_abs_corr"], color=["#d62728" if v > CORR_THRESH else "#2ca02c" for v in corr_df["max_abs_corr"]])
    ax.axvline(CORR_THRESH, color="black", linestyle="--", linewidth=0.8)
    ax.set_xlabel("|korelasi| maks vs registry lama")
    ax.set_title("Uji korelasi (sebelum gerbang)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "v10_impor_jurnal.png", dpi=120)
    print(f"saved {FIG_DIR / 'v10_impor_jurnal.png'}")

    return survivors


if __name__ == "__main__":
    s = main()
    sys.exit(0 if len(s) else 1)
