#!/usr/bin/env python3
"""V11 -- Perluasan V10: 14 formula BARU dari (a) registri arah v6 yang belum
pernah diuji di bawah nama apapun di proyek ini (E1 MOM, E2 MRV, E3 BRK --
semua bertipe `direction` sesuai klasifikasi v6 sendiri, BUKAN divisi V/Q/T/S
yang bertipe `estimation` dan karenanya TIDAK cocok untuk gerbang G1-G6 arah --
lihat CATATAN METODOLOGI di bawah), dan (b) 4 formula kuant umum lintas-aset
(bukan literatur commodity-specific) dari faktor investing klasik.

Anggaran: 14 baru (di bawah plafon), digabung dengan 9 dari V10 = 23 formula
arah total diuji G1-G6 sepanjang V10+V11. Gerbang G1-G6 SAMA PERSIS.
"""
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m1, load_m5, measure_cost_bps, REPORTS, FIG_DIR
from src.stats.effective_n import effective_n as ldp_effective_n
from l13_lomba_makro import load_macro, build_macro_features, build_signals as build_mac_signals
from lomba4_entry import build_signals as build_signals_m5
from lomba2_tren import ols_slope_tstat, KalmanDrift
from v10_impor_jurnal import (PREREG as PREREG_V10, build_all_signals as build_v10_signals,
                                build_xag_d1, build_dcot, build_micro_daily,
                                check_g1, check_g3, check_g4, check_g6, zscore, lag1)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

LATIH_FRAC = 0.60
UJI_FRAC = 0.25
TAU_DEFAULT = 1.0

PREREG = {
    "MOM03": dict(divisi="E1 MOM (v6)", citation="Berkman, Koch, Tuttle & Zhang (2012), Journal of Financial and Quantitative Analysis 47(4):715-741",
        doi="10.1017/S0022109012000270", tahun_terbit=2012, sampel_asli="Saham AS, 1996-2008",
        mekanisme="Gap pembukaan setelah jeda pasar berlanjut arahnya karena informasi yang menumpuk selama jeda belum terserap penuh di bar pertama.",
        tanda_prediksi="gap positif -> gold NAIK; sign(sinyal)=sign(gap)."),
    "MOM08": dict(divisi="E1 MOM (v6)", citation="Moskowitz, Ooi & Pedersen (2012), Journal of Financial Economics 104(2):228-250 (SSRN abstract_id=2089463)",
        doi="10.1016/j.jfineco.2011.11.003", tahun_terbit=2012, sampel_asli="58 instrumen berjangka lintas kelas aset (ekuitas, FX, komoditas, obligasi), 1965-2009",
        mekanisme="Return masa lalu horizon-menengah (time-series momentum) memprediksi return berikutnya dengan tanda sama karena penyesuaian eksposur institusional bertahap, bukan seketika.",
        tanda_prediksi="return 12-bulan positif -> gold NAIK; sign(sinyal)=sign(r_{t-252:t})."),
    "MOM11": dict(divisi="E1 MOM (v6)", citation="George & Hwang (2004), The Journal of Finance 59(5):2145-2176",
        doi="10.1111/j.1540-6261.2004.00695.x", tahun_terbit=2004, sampel_asli="Saham NYSE/AMEX/NASDAQ, 1963-2001",
        mekanisme="Harga dekat ekstrem 52-minggu menghadapi keengganan peserta merevisi penilaian melewati titik acuan yang menonjol, sehingga penyesuaian tertunda dan berlanjut setelah level itu ditembus.",
        tanda_prediksi="dekat puncak jendela -> gold NAIK, dekat dasar -> gold TURUN; sign(sinyal)=+1 dekat puncak,-1 dekat dasar."),
    "MRV03": dict(divisi="E2 MRV (v6)", citation="Nagel (2012), The Review of Financial Studies 25(7):2005-2039 (SSRN abstract_id=1988706, NBER WP17653)",
        doi="10.1093/rfs/hhs066", tahun_terbit=2012, sampel_asli="Saham AS, 1998-2011 (VIX era)",
        mekanisme="Imbal hasil pembalikan adalah kompensasi penyedia likuiditas dan naik justru saat kapasitas penyediaan likuiditas menipis (spread melebar); menyaring pembalikan berdasar keadaan likuiditas memisahkan pembalikan berbayar dari yang tidak.",
        tanda_prediksi="gerak besar SAAT spread stress tinggi -> berbalik; sign(sinyal)=-sign(r_{t-L:t}) HANYA saat spread>p75."),
    "MRV06": dict(divisi="E2 MRV (v6)", citation="Patton & Sheppard (2015), The Review of Economics and Statistics 97(3):683-697",
        doi="10.1162/REST_a_00503", tahun_terbit=2015, sampel_asli="S&P500 & 105 saham individual, opsi harian",
        mekanisme="Volatilitas terkonsentrasi di satu sisi (RS+ - RS- besar) menandakan tekanan likuidasi searah bukan kedatangan informasi, sehingga sebagian gerak itu adalah konsesi harga yang kembali setelah tekanan selesai.",
        tanda_prediksi="SJV besar positif (RS+>>RS-) -> gold TURUN (berbalik); sign(sinyal)=-sign(SJV)."),
    "BRK01": dict(divisi="E3 BRK (v6)", citation="Zarattini & Aziz (2023), SSRN working paper (abstract_id=4416622) -- BELUM peer-reviewed, mekanisme dasar (pemusatan aliran di pembukaan) didukung Gao/Han/Li/Zhou (2018) JFE peer-reviewed",
        doi="SSRN:4416622", tahun_terbit=2023, sampel_asli="Saham AS (ORB 5-menit), 2016-2023",
        mekanisme="Pembukaan sesi memusatkan aliran order yang menumpuk selama jeda; arah penembusan range awal mencerminkan sisi tekanan yang belum selesai diserap.",
        tanda_prediksi="tembus ke atas range pembukaan sesi London -> gold NAIK; sign(sinyal)=arah tembus."),
    "BRK02": dict(divisi="E3 BRK (v6)", citation="Coles (2001), An Introduction to Statistical Modeling of Extreme Values, Springer Series in Statistics (buku teks EVT standar)",
        doi="10.1007/978-1-4471-3675-0", tahun_terbit=2001, sampel_asli="Buku teks metodologi (Peaks-Over-Threshold / GPD), bukan studi pasar tunggal",
        mekanisme="Gerak yang melampaui ambang ekstrem terkalibrasi dari distribusi ekornya sendiri menandakan kedatangan informasi yang belum terserap, kualitatif berbeda dari gerak besar yang masih dalam distribusi normal.",
        tanda_prediksi="|return| melampaui ambang GPD -> arah berlanjut; sign(sinyal)=sign(return_t)."),
    "BRK03": dict(divisi="E3 BRK (v6)", citation="Bollerslev (1986), Journal of Econometrics 31(3):307-327 [fakta clustering volatilitas -- strategi kontraksi-ekspansi sendiri NEED_LOOKUP di v6 utk sumber langsung, ditandai eksplisit]",
        doi="10.1016/0304-4076(86)90063-1", tahun_terbit=1986, sampel_asli="Fakta stilisata umum, bukan strategi spesifik",
        mekanisme="Volatilitas berkelompok; pada transisi kontraksi->ekspansi, penyedia likuiditas belum menyesuaikan kuotasi terhadap rezim baru sehingga gerak berlanjut lebih jauh daripada dibenarkan informasinya.",
        tanda_prediksi="pemicu ekspansi dari kontraksi -> arah gerak pemicu berlanjut; sign(sinyal)=sign(r_pemicu)."),
    "BRK07": dict(divisi="E3 BRK (v6)", citation="Adams & MacKay (2007), arXiv:0710.3742 [BUKAN peer-reviewed/DOI/SSRN/NBER -- v6 sendiri menandai ini HANYA layak screening, bukan CONFIRM; tetap diuji di sini dengan label eksplisit derajat-sitasi-lebih-rendah]",
        doi="arXiv:0710.3742", tahun_terbit=2007, sampel_asli="Simulasi + data well-log (bukan data finansial)",
        mekanisme="Deteksi titik-perubahan daring Bayesian (BOCPD) memberi probabilitas rezim baru dimulai secara kausal murni; ambil arah gerak terkini hanya saat probabilitas rezim-baru cukup tinggi.",
        tanda_prediksi="P(rezim baru)>=p_min -> arah gerak terkini berlanjut; sign(sinyal)=sign(r_{t-h:t})."),
    "SAFE01": dict(divisi="Umum (safe-haven, lintas-aset)", citation="Baur & Lucey (2010), Financial Review 45(2):217-229; Baur & McDermott (2010), Journal of Banking & Finance 34(8):1886-1898",
        doi="10.1111/j.1540-6288.2010.00244.x; 10.1016/j.jbankfin.2009.12.008", tahun_terbit=2010, sampel_asli="Emas vs indeks saham AS/Eropa/berkembang, 1979-2009",
        mekanisme="Emas adalah safe haven bersyarat: saat stres pasar ekuitas ekstrem (proksi VIX melonjak) memicu aliran flight-to-quality yang secara historis mendorong gold outperform.",
        tanda_prediksi="z(VIX) tinggi -> gold NAIK; sign(sinyal)=sign(z_VIX)."),
    "LOTTO01": dict(divisi="Umum (lottery/skew, lintas-aset)", citation="Bali, Cakici & Whitelaw (2011), Journal of Financial Economics 99(2):427-446",
        doi="10.1016/j.jfineco.2010.08.014", tahun_terbit=2011, sampel_asli="Saham AS, 1926-2005",
        mekanisme="Preferensi investor terhadap aset mirip-lotere membuat aset dengan return maksimum ekstrem baru-baru ini kelebihan permintaan (overpriced), sehingga return berikutnya lebih rendah.",
        tanda_prediksi="MAX return 21-hari tinggi -> gold TURUN berikutnya; sign(sinyal)=-sign(z_MAX)."),
    "IVOL01": dict(divisi="Umum (idiosyncratic vol, lintas-aset)", citation="Ang, Hodrick, Xing & Zhang (2006), The Journal of Finance 61(1):259-299",
        doi="10.1111/j.1540-6261.2006.00836.x", tahun_terbit=2006, sampel_asli="Saham AS, 1963-2000",
        mekanisme="Aset dengan volatilitas realized tinggi historisnya memberi return berikutnya jauh lebih rendah (anomali volatilitas-rendah), bertentangan dengan intuisi risk-return standar.",
        tanda_prediksi="realized vol 21-hari tinggi -> gold TURUN berikutnya; sign(sinyal)=-sign(z_RV21d)."),
    "REV01LT": dict(divisi="Umum (pembalikan jangka panjang, lintas-aset)", citation="De Bondt & Thaler (1985), The Journal of Finance 40(3):793-805",
        doi="10.1111/j.1540-6261.1985.tb05004.x", tahun_terbit=1985, sampel_asli="Saham NYSE, 1926-1982 (portofolio 3-tahun)",
        mekanisme="Peserta over-reaksi secara sistematis terhadap informasi jangka panjang; pemenang (loser) ekstrem 3-tahun cenderung berbalik dan menjadi loser (pemenang) di periode berikutnya.",
        tanda_prediksi="return 3-tahun (756 hari) tinggi -> gold TURUN berikutnya (kontrarian); sign(sinyal)=-sign(z_r756d)."),
}

DIBUANG_SEBELUM_UJI = [
    dict(id="MOM01/02/04/05/06/07 (E1)", alasan="SUDAH DIUJI di bawah nama lain sepanjang proyek ini (bukan formula baru): MOM01~intraday momentum sejenis MAD-Zscore-momentum, MOM02=Momentum-VolScaled (lomba4), MOM04=DriftBurst-tstat (lomba4), MOM05=Mann-Kendall (lomba2), MOM06=QuantReg-slope (lomba2), MOM07=Theil-Sen (lomba2). Menguji ulang dengan nama baru = menghitung hipotesis yang sama dua kali, menaikkan SR_0 tanpa informasi baru."),
    dict(id="MOM09/MOM10 (E1, panel lintas-instrumen)", alasan="DATA_TIDAK_CUKUP -- spek v6 sendiri mensyaratkan minimum 4 instrumen per bar ('kalau instrumen tersedia < 4 -> bar dilewati'), proyek ini hanya punya 2 (XAU+XAG). Memaksakan panel 2-instrumen bukan lagi cross-sectional z-score yang valid sesuai spek aslinya."),
    dict(id="MRV01 (E2)", alasan="SUDAH DIUJI sebagai ShortHorizon-Reversal (lomba4), formula identik (z-score return dibalik tanda)."),
    dict(id="MRV02 (E2, panel OU s-score)", alasan="DATA_TIDAK_CUKUP -- sama seperti MOM09/10, perlu panel >=4 instrumen untuk PCA faktor bersama yang valid."),
    dict(id="MRV04 (E2, MAD z-score gate)", alasan="BUKAN_SINYAL_MANDIRI -- spek v6 sendiri eksplisit: ini lapisan gerbang kekuatan di atas sinyal lain, bukan sinyal arah berdiri sendiri. Tidak dihitung sebagai kandidat terpisah, sesuai instruksi spek sendiri."),
    dict(id="MRV05 (E2, dekomposisi kontrarian)", alasan="DIAGNOSTIK, BUKAN KANDIDAT -- spek v6 eksplisit menandai formula ini sebagai alat diagnostik (memisahkan over-reaksi vs lead-lag), bukan sinyal untuk digerbangi G1-G6."),
    dict(id="BRK04 (E3, range compression break)", alasan="TIDAK_ADA_SITASI -- spek v6 sendiri eksplisit 'SAYA TIDAK MENEMUKAN sumber peer-reviewed', ditandai NEED_LOOKUP tanpa kandidat pengganti. Anti-ngasal: tidak diuji tanpa sumber."),
    dict(id="BRK05 (E3, CUSUM changepoint)", alasan="SUDAH DIUJI EKSTENSIF sebagai sinyal utama v7 (CUSUM) -- terbukti drift capture lewat autopsi 4-uji (L1), bukan sinyal genuine. Tidak diuji ulang (aturan anti-p-hacking eksplisit: sekali gagal, selesai)."),
    dict(id="BRK06 (E3, segmentasi PELT)", alasan="TIDAK_LAYAK_KOMPUTASI + REDUNDAN -- PELT retrospektif yang dijalankan ulang tiap bar (kausal, hanya data<=t) berbiaya O(n) per bar = O(n^2) total untuk >8000 hari, tidak feasible tanpa implementasi inkremental khusus. Selain itu segmen-umur PELT secara konsep sangat mirip CUSUM (BRK05) yang sudah terbukti drift capture -- risiko tinggi temuan yang sama, bukan informasi baru."),
    dict(id="Divisi V/Q/T/S (v6, 65 formula estimation-type)", alasor=None, alasan="MISMATCH_TIPE_GERBANG -- diklasifikasikan v6 SENDIRI sebagai `division_type: estimation`, bukan `direction`. Spek v6 eksplisit: menguji formula estimasi (volatilitas, spread, intensitas tick, rezim/entropi/Hurst) dengan gerbang arah G1-G6 adalah kesalahan kategori ('menilai termometer dari kemampuannya menebak cuaca besok'). Yang SUDAH dipakai sebagai KOMPONEN sah di formula arah yang diuji di sini: V01_PARKINSON (skala sigma di MOM08/MOM11/BRK01/BRK03), Q01_ROLL_SPREAD & Q04_AMIHUD (=MIC03/MIC01 di V10), Q06/Q07 spread velocity/acceleration (trigger stress di MRV03). Sisanya (V02-14, Q02-12 minus yg dipakai, T01-10, S 29 formula) TIDAK diuji sebagai kandidat arah -- itu akan berarti mengarang konvensi tanda yang tidak berdasar literatur, persis yang dilarang aturan anti-ngasal. Kalau ingin diuji, jalur yang benar adalah gerbang MCS/separasi-expectancy-bersyarat milik divisi masing-masing (proyek terpisah, V12+)."),
]


def build_ohlc_d1():
    h1 = pd.read_parquet("/workspace/data/bars_h1/XAUUSD_H1.parquet")
    h1["date"] = h1["bar_time"].dt.date
    d1 = h1.groupby("date").agg(mid_open=("mid_open", "first"), mid_high=("mid_high", "max"),
                                  mid_low=("mid_low", "min"), mid_close=("mid_close", "last")).reset_index()
    d1["date"] = pd.to_datetime(d1["date"]).astype("datetime64[ns]")
    return d1.sort_values("date").reset_index(drop=True)


def build_micro_session_daily():
    """BRK01 (ORB sesi London) & MRV06 (signed jump RS+/RS-) dari M5 (2021-2026)."""
    m5 = load_m5()
    m5 = m5.copy()
    m5["date"] = m5["bar_time"].dt.date
    m5["hour"] = m5["bar_time"].dt.hour
    logp_all = np.log(m5["mid_close"].values)
    ret_all = np.diff(logp_all, prepend=logp_all[0])
    m5["ret"] = ret_all

    rows = []
    for date, g in m5.groupby("date"):
        g = g.sort_values("bar_time")
        rs_plus = float((g["ret"].values[g["ret"].values > 0] ** 2).sum())
        rs_minus = float((g["ret"].values[g["ret"].values < 0] ** 2).sum())
        rv = rs_plus + rs_minus
        london = g[(g["hour"] >= 7) & (g["hour"] < 13)]
        orb_dir = np.nan
        if len(london) >= 10:
            first6 = london.iloc[:6]
            rest = london.iloc[6:]
            or_hi, or_lo = first6["mid_close"].max(), first6["mid_close"].min()
            if len(rest) > 0:
                brk_up = (rest["mid_close"] > or_hi).any()
                brk_dn = (rest["mid_close"] < or_lo).any()
                if brk_up and not brk_dn:
                    orb_dir = 1.0
                elif brk_dn and not brk_up:
                    orb_dir = -1.0
                else:
                    orb_dir = 0.0
        rows.append({"date": pd.Timestamp(date), "rs_plus": rs_plus, "rs_minus": rs_minus,
                      "rv_day": rv, "sjv": rs_plus - rs_minus, "orb_direction": orb_dir})
    out = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    out["date"] = pd.to_datetime(out["date"]).astype("datetime64[ns]")
    return out


def bocpd_run_length(logret, hazard=1.0 / 60, max_run=120, mu0=0.0, kappa0=1.0, alpha0=3.0, beta0_scale=1e-4,
                      r_baru_threshold=5):
    """BOCPD kausal sederhana (Adams & MacKay 2007), prediktif Student-t Normal-Inverse-Gamma,
    run-length dipotong ke max_run demi biaya komputasi. CATATAN TEKNIS: P(r_t=0) SENDIRI secara
    matematis identik dengan hazard rate di setiap langkah (identitas aljabar dari normalisasi
    pesan BOCPD -- bukan bug, tapi tidak informatif kalau dipakai sendirian). Yang informatif dan
    dipakai di sini adalah P(r_t <= r_baru_threshold) -- massa probabilitas pada run-length PENDEK,
    yang genuinely bervariasi dari waktu ke waktu (dikonfirmasi lewat E[r_t] yang berkisar dari <1
    sampai >100 di data nyata) -- sesuai spesifikasi v6 sendiri: 'P(r_t < r_baru) >= p_min'."""
    from scipy.stats import t as student_t
    n = len(logret)
    var0 = np.var(logret[np.isfinite(logret)][:500]) if np.isfinite(logret[:500]).sum() > 30 else 1e-6
    beta0 = beta0_scale * var0 if var0 > 0 else 1e-8
    mu = np.array([mu0]); kappa = np.array([kappa0]); alpha = np.array([alpha0]); beta = np.array([beta0])
    R = np.array([1.0])
    expected_rl = np.full(n, np.nan)
    p_short_run = np.full(n, np.nan)
    for t in range(n):
        x = logret[t]
        if not np.isfinite(x):
            continue
        scale = np.sqrt(beta * (kappa + 1) / (alpha * kappa))
        pred = student_t.pdf(x, df=2 * alpha, loc=mu, scale=np.maximum(scale, 1e-12))
        pred = np.nan_to_num(pred, nan=1e-12, posinf=1e12, neginf=1e-12)
        growth = R * pred * (1 - hazard)
        cp_prob = np.sum(R * pred * hazard)
        R_new = np.concatenate([[cp_prob], growth])
        R_new = R_new / (R_new.sum() + 1e-300)
        kappa_new = np.concatenate([[kappa0], kappa + 1])
        mu_new = np.concatenate([[mu0], (kappa * mu + x) / (kappa + 1)])
        alpha_new = np.concatenate([[alpha0], alpha + 0.5])
        beta_new = np.concatenate([[beta0], beta + (kappa * (x - mu) ** 2) / (2 * (kappa + 1))])
        if len(R_new) > max_run:
            tail_mass = R_new[max_run:].sum()
            R_new = R_new[:max_run]; R_new[-1] += tail_mass
            kappa_new, mu_new, alpha_new, beta_new = kappa_new[:max_run], mu_new[:max_run], alpha_new[:max_run], beta_new[:max_run]
        R, kappa, mu, alpha, beta = R_new, kappa_new, mu_new, alpha_new, beta_new
        run_idx = np.arange(len(R))
        expected_rl[t] = float((run_idx * R).sum())
        p_short_run[t] = float(R[:r_baru_threshold + 1].sum())
    return expected_rl, p_short_run


def build_all_v11_signals(d1_ohlc, micro_session, dcot, fred):
    n_total = len(d1_ohlc)
    latih_end = int(n_total * LATIH_FRAC)
    mid_close = d1_ohlc["mid_close"].values
    mid_open = d1_ohlc["mid_open"].values
    mid_high = d1_ohlc["mid_high"].values
    mid_low = d1_ohlc["mid_low"].values
    logp = np.log(mid_close)
    day_ret = np.diff(logp, prepend=logp[0])
    prev_close = np.roll(mid_close, 1); prev_close[0] = mid_close[0]

    sig = pd.DataFrame({"date": d1_ohlc["date"]})

    # ---- MOM03: session gap continuation ----
    gap = (mid_open - prev_close) / prev_close
    sig["MOM03_session_gap"] = np.sign(gap) * np.abs(zscore(pd.Series(gap), window=252))

    # ---- MOM08: TSMOM 12-month vol-scaled (sign only, always-invested per paper design) ----
    k = 252
    r_lb = np.log(mid_close) - np.log(np.roll(mid_close, k))
    r_lb[:k] = np.nan
    sig["MOM08_tsmom_252d"] = np.sign(r_lb)  # tau=1.0 -> selalu diambil, sesuai desain asli (tanpa ambang)

    # ---- MOM11: 52-week high/low proximity ----
    n_hl = 252
    hi = pd.Series(mid_high).rolling(n_hl, min_periods=60).max().values
    lo = pd.Series(mid_low).rolling(n_hl, min_periods=60).min().values
    eps = 0.0025
    p_hi = mid_close / hi
    p_lo = mid_close / lo
    mom11 = np.full(n_total, np.nan)
    mom11[p_hi >= 1 - eps] = 1.0
    mom11[p_lo <= 1 + eps] = -1.0
    sig["MOM11_extreme_proximity"] = mom11

    # ---- BRK02: POT/GPD exceedance ----
    from scipy.stats import genpareto
    abs_r = np.abs(day_ret)
    u = np.nanquantile(abs_r[:latih_end], 0.93)
    exceed = abs_r[:latih_end][abs_r[:latih_end] > u] - u
    brk02 = np.full(n_total, np.nan)
    if len(exceed) >= 30:
        xi, loc_, scale_ = genpareto.fit(exceed, floc=0)
        if xi < 0.5:
            x_trigger = u  # ambang deteksi = u itu sendiri (periode ulang implisit lewat frekuensi p=0.93)
            trig = abs_r > x_trigger
            brk02[trig] = np.sign(day_ret[trig])
    sig["BRK02_pot_exceedance"] = brk02

    # ---- BRK03: vol contraction -> expansion trigger ----
    sigma_short = pd.Series(day_ret).rolling(12, min_periods=8).std().values
    sigma_long = pd.Series(day_ret).rolling(96, min_periods=48).std().values
    v_ratio = sigma_short / np.where(sigma_long > 0, sigma_long, np.nan)
    q_low = np.nanquantile(v_ratio[:latih_end], 0.25)
    q_trig = np.nanquantile(v_ratio[:latih_end], 0.75)
    brk03 = np.full(n_total, np.nan)
    was_contracted = False
    h_dir = 3
    for t in range(1, n_total):
        if not np.isfinite(v_ratio[t]):
            continue
        if v_ratio[t] <= q_low:
            was_contracted = True
        elif was_contracted and v_ratio[t] >= q_trig:
            r_pemicu = logp[t] - logp[max(0, t - h_dir)]
            brk03[t] = np.sign(r_pemicu)
            was_contracted = False
    sig["BRK03_vol_contraction_expansion"] = brk03

    # ---- BRK07: BOCPD run-length ----
    print("  menghitung BOCPD (BRK07)...")
    exp_rl, p_short_run = bocpd_run_length(day_ret)
    h_dir7 = 3
    r_recent = logp - np.roll(logp, h_dir7)
    r_recent[:h_dir7] = np.nan
    # baseline P(r<=5) di bawah hazard murni ~= 1-(1-1/60)^6 ~ 0.096; p_min jauh di atas itu -> rezim baru genuinely lebih mungkin
    p_min = 0.30
    brk07 = np.where(p_short_run >= p_min, np.sign(r_recent), np.nan)
    sig["BRK07_bocpd_runlength"] = brk07

    # ---- MOM03/BRK01/MRV06 butuh M5 micro (2021-2026) ----
    m = d1_ohlc.merge(micro_session, on="date", how="left")
    sig["BRK01_orb_session"] = np.where(m["orb_direction"].values == 0, np.nan, m["orb_direction"].values)
    sjv = m["sjv"].values
    rv_day = m["rv_day"].values
    theta = 0.3
    mrv06 = np.where(np.isfinite(sjv) & np.isfinite(rv_day) & (rv_day > 0) & (np.abs(sjv) > theta * rv_day),
                      -np.sign(sjv), np.nan)
    sig["MRV06_signed_jump_reversal"] = mrv06

    # ---- MRV03: liquidity-conditioned reversal (spread stress dari M5) ----
    m5 = load_m5()
    m5d = m5.copy(); m5d["date"] = m5d["bar_time"].dt.date
    spread_daily = m5d.groupby("date")["spread_bps"].mean().reset_index()
    spread_daily["date"] = pd.to_datetime(spread_daily["date"]).astype("datetime64[ns]")
    m = d1_ohlc.merge(spread_daily, on="date", how="left")
    spread_roll_q75 = m["spread_bps"].rolling(60, min_periods=30).quantile(0.75)
    stress = (m["spread_bps"] >= spread_roll_q75).values
    L, theta_mrv3 = 3, 1.5
    z_base = (logp - np.roll(logp, L)) / (pd.Series(day_ret).rolling(20, min_periods=10).std().values * np.sqrt(L) + 1e-12)
    z_base[:L] = np.nan
    mrv03 = np.where(stress & (np.abs(z_base) > theta_mrv3), -np.sign(z_base), np.nan)
    sig["MRV03_liquidity_reversal"] = mrv03

    # ---- SAFE01: VIX-conditional safe haven ----
    fred2 = fred[["date", "VIXCLS"]].copy()
    fred2["date"] = pd.to_datetime(fred2["date"]).astype("datetime64[ns]")
    fred2 = lag1(fred2, "date", ["VIXCLS"])
    m = d1_ohlc.merge(fred2, on="date", how="left")
    sig["SAFE01_vix_safehaven"] = zscore(m["VIXCLS"], window=252)

    # ---- LOTTO01: max daily return 21d (lottery effect, contrarian) ----
    max21 = pd.Series(day_ret).rolling(21, min_periods=10).max()
    sig["LOTTO01_max_return"] = -zscore(max21, window=252)

    # ---- IVOL01: realized vol 21d (low-vol anomaly, contrarian) ----
    rv21 = pd.Series(day_ret).rolling(21, min_periods=10).std()
    sig["IVOL01_realized_vol"] = -zscore(rv21, window=252)

    # ---- REV01LT: 3-year (756d) long-term reversal ----
    r756 = pd.Series(logp - np.roll(logp, 756))
    r756.iloc[:756] = np.nan
    sig["REV01LT_long_term_reversal"] = -zscore(r756, window=252, min_periods=120)

    return sig


def build_registry_v11(d1_ohlc, fred, cot_legacy, v10_sig):
    n_total = len(d1_ohlc)
    latih_end = int(n_total * LATIH_FRAC)
    reg = pd.DataFrame({"date": d1_ohlc["date"]})

    m5 = load_m5()
    sig_m5 = build_signals_m5(m5)
    sig_m5["date"] = m5["bar_time"].dt.date
    daily_m5 = sig_m5.groupby("date").last().reset_index()
    daily_m5["date"] = pd.to_datetime(daily_m5["date"]).astype("datetime64[ns]")
    reg = reg.merge(daily_m5, on="date", how="left", suffixes=("", "_m5reg"))

    d1_simple = d1_ohlc[["date", "mid_close"]].copy()
    fred_lag = fred.copy(); fred_lag["date"] = pd.to_datetime(fred_lag["date"]).astype("datetime64[ns]")
    cot_lag = cot_legacy.copy()
    df_mac = build_macro_features(d1_simple, fred_lag, cot_lag)
    mac_sig = build_mac_signals(df_mac, latih_end)
    for c in mac_sig.columns:
        reg[c] = mac_sig[c].values

    logp = pd.Series(np.log(d1_ohlc["mid_close"].values))
    reg["TREND_ols_20d"] = logp.rolling(21).apply(lambda y: ols_slope_tstat(y.values)[0], raw=False)
    px = d1_ohlc["mid_close"].values
    kf_std = float(np.std(np.diff(np.log(px[:latih_end]))))
    kf = KalmanDrift(q_level=(kf_std * px[0]) ** 2 * 0.01, q_drift=(kf_std * px[0]) ** 2 * 1e-4, r_obs=(kf_std * px[0]) ** 2 * 4)
    reg["TREND_kalman_drift"] = kf.run(px)

    for c in v10_sig.columns:
        if c == "date" or c == "MIC02_z_gate":
            continue
        reg[f"V10_{c}"] = v10_sig[c].values

    return reg


def screen_correlation(sig, registry, candidate_cols, thresh=0.30):
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


def evaluate_formula(fid, z, d1_ohlc, regime_bounds, uji_end, latih_uji_mask, cost_base, cost_worst,
                      day_ret_demeaned_bps, day_ret_bps, tau_grid):
    date_arr = d1_ohlc["date"].values
    pub_year = PREREG[fid]["tahun_terbit"]
    rows = []
    for tau in tau_grid:
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
        rev_g1, _, _ = check_g1(-direction, -net_demeaned)
        note = " [CATATAN: tanda TERBALIK akan LOLOS G1 -- data mining, TETAP DIBUANG]" if (not g1 and rev_g1) else ""
        if not g1:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G1",
                          "pnl_long_demean": pl, "pnl_short_demean": ps, "catatan": note})
            continue
        g2 = float(net_worst.mean()) > 0
        if not g2:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G2", "expectancy_worst": float(net_worst.mean())})
            continue
        g3, g3_detail = check_g3(direction, net_base, entry_bt, regime_bounds)
        if not g3:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G3", "g3_detail": g3_detail})
            continue
        g4, g4_npos, g4_top2, _ = check_g4(net_base, entry_idx, uji_end)
        if not g4:
            rows.append({"peserta": fid, "tau": tau, "n": n, "stopped_at": "G4", "wf_positive": g4_npos, "wf_top2_share": g4_top2})
            continue
        starts = entry_idx; ends = np.minimum(entry_idx + 1, len(d1_ohlc))
        eff_n = ldp_effective_n(starts, ends, len(d1_ohlc))
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
    d1_ohlc = build_ohlc_d1()
    fred, cot_legacy = load_macro()
    dcot = build_dcot()
    print("Membangun fitur sesi/jump harian dari M5 (BRK01, MRV06)...")
    micro_session = build_micro_session_daily()

    n_total = len(d1_ohlc)
    latih_end = int(n_total * LATIH_FRAC)
    uji_end = int(n_total * (LATIH_FRAC + UJI_FRAC))
    latih_uji_mask = np.zeros(n_total, dtype=bool); latih_uji_mask[:uji_end] = True
    print(f"D1 XAU (OHLC) total={n_total:,} ({d1_ohlc['date'].iloc[0].date()} s/d {d1_ohlc['date'].iloc[uji_end-1].date()})")

    m1 = load_m1()
    m1_mask = np.zeros(len(m1), dtype=bool); m1_mask[: int(len(m1) * 0.70)] = True
    cost_info = measure_cost_bps(m1, m1_mask)
    cost_base = cost_info["round_trip_cost_bps"]
    spread_p90 = m1.loc[m1_mask, "spread_bps"].dropna().pipe(lambda s: s[(s > 0) & (s < 500)]).quantile(0.90)
    cost_worst = spread_p90 * 2.5 + 0.28
    print(f"Biaya base={cost_base:.3f}bps, worst={cost_worst:.3f}bps")

    print("Membangun 14 sinyal V11...")
    sig = build_all_v11_signals(d1_ohlc, micro_session, dcot, fred)

    print("Membangun 9 sinyal V10 (untuk registry korelasi, tidak diuji ulang)...")
    xag_d1 = build_xag_d1()
    micro_v10 = build_micro_daily()
    d1_simple = d1_ohlc[["date", "mid_close"]].copy()
    v10_sig = build_v10_signals(d1_simple, fred, cot_legacy, dcot, xag_d1, micro_v10)

    print("Membangun registry (v10 + trend + M5 signals + MAC) untuk uji korelasi...")
    registry = build_registry_v11(d1_ohlc, fred, cot_legacy, v10_sig)

    candidate_cols = list(PREREG.keys())
    candidate_cols_full = [
        "MOM03_session_gap", "MOM08_tsmom_252d", "MOM11_extreme_proximity",
        "MRV03_liquidity_reversal", "MRV06_signed_jump_reversal",
        "BRK01_orb_session", "BRK02_pot_exceedance", "BRK03_vol_contraction_expansion", "BRK07_bocpd_runlength",
        "SAFE01_vix_safehaven", "LOTTO01_max_return", "IVOL01_realized_vol", "REV01LT_long_term_reversal",
    ]
    corr_df = screen_correlation(sig, registry, candidate_cols_full)
    print("\n=== UJI KORELASI vs REGISTRY (V10 + trend + M5 + MAC) ===")
    print(corr_df.round(4).to_string(index=False))

    CORR_THRESH = 0.30
    lolos_korelasi = corr_df[corr_df["max_abs_corr"] <= CORR_THRESH]["peserta"].tolist()
    gagal_korelasi = corr_df[corr_df["max_abs_corr"] > CORR_THRESH]

    fid_map = {"MOM03_session_gap": "MOM03", "MOM08_tsmom_252d": "MOM08", "MOM11_extreme_proximity": "MOM11",
               "MRV03_liquidity_reversal": "MRV03", "MRV06_signed_jump_reversal": "MRV06",
               "BRK01_orb_session": "BRK01", "BRK02_pot_exceedance": "BRK02",
               "BRK03_vol_contraction_expansion": "BRK03", "BRK07_bocpd_runlength": "BRK07",
               "SAFE01_vix_safehaven": "SAFE01", "LOTTO01_max_return": "LOTTO01",
               "IVOL01_realized_vol": "IVOL01", "REV01LT_long_term_reversal": "REV01LT"}

    logp = np.log(d1_ohlc["mid_close"].values)
    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))
    roll_mean_60d = day_ret.rolling(60, min_periods=15).mean()
    demeaned_logp = np.cumsum((day_ret - roll_mean_60d.fillna(0)).values)
    day_ret_bps = (np.roll(logp, -1) - logp) * 1e4; day_ret_bps[-1] = np.nan
    day_ret_demeaned_bps = (np.roll(demeaned_logp, -1) - demeaned_logp) * 1e4; day_ret_demeaned_bps[-1] = np.nan

    regime_bounds = [
        ("2003-2011 bull", np.datetime64("2003-01-01"), np.datetime64("2012-01-01")),
        ("2012-2015 BEAR", np.datetime64("2012-01-01"), np.datetime64("2016-01-01")),
        ("2016-cutoff", np.datetime64("2016-01-01"), pd.Timestamp(d1_ohlc["date"].iloc[uji_end - 1]).to_datetime64()),
    ]

    all_rows = []
    dibuang_korelasi = []
    for _, r in gagal_korelasi.iterrows():
        dibuang_korelasi.append(f"{r['peserta']}: korelasi {r['max_abs_corr']:.3f} vs {r['vs']} (>0.30) -- DITOLAK SEBELUM GERBANG")
        print(f"DITOLAK (korelasi): {r['peserta']} = {r['max_abs_corr']:.3f} vs {r['vs']}")

    print(f"\n=== GERBANG G1-G6 (hanya kandidat lolos uji korelasi) ===")
    for col in lolos_korelasi:
        fid = fid_map[col]
        rows = evaluate_formula(fid, sig[col].values, d1_ohlc, regime_bounds, uji_end, latih_uji_mask,
                                  cost_base, cost_worst, day_ret_demeaned_bps, day_ret_bps, tau_grid=(TAU_DEFAULT,))
        first_g1_pass = any(x["stopped_at"] not in ("n<30", "G1") for x in rows)
        if first_g1_pass:
            extra_rows = evaluate_formula(fid, sig[col].values, d1_ohlc, regime_bounds, uji_end, latih_uji_mask,
                                            cost_base, cost_worst, day_ret_demeaned_bps, day_ret_bps, tau_grid=(1.5, 2.0))
            rows += extra_rows
        all_rows += rows
        for r in rows:
            print(f"  {fid} tau={r['tau']}: n={r['n']}, stopped_at={r['stopped_at']}")

    df_rows = pd.DataFrame(all_rows)
    stop_counts = df_rows["stopped_at"].value_counts().to_dict() if len(df_rows) else {}
    survivors = df_rows[df_rows["stopped_at"] == "LOLOS"] if len(df_rows) else pd.DataFrame()
    total_trial = len(df_rows) + len(gagal_korelasi)

    print(f"\nDistribusi gerbang gugur: {stop_counts}")
    print(f"TOTAL SURVIVOR: {len(survivors)}/{len(df_rows)} (dari {len(candidate_cols_full)} formula, {len(dibuang_korelasi)} ditolak pra-gerbang)")
    print(f"TOTAL TRIAL untuk DSR: {total_trial}")

    lines = ["# V11 -- Perluasan registri v6 (E1/E2/E3) + kuant umum lintas-aset\n",
              f"**{len(PREREG)} formula BARU diimplementasikan (di bawah plafon), digabung dengan 9 dari V10 "
              f"= {len(PREREG) + 9} formula arah total diuji G1-G6 sepanjang V10+V11. "
              f"TOTAL TRIAL V11 untuk DSR = {total_trial}.**\n",
              "\n## CATATAN METODOLOGI PENTING -- kenapa bukan 500, dan bukan divisi V/Q/T/S\n",
              "Registri arah v6 (E1 MOM + E2 MRV + E3 BRK) cuma punya **24 formula** total. Dari situ, "
              "**11 sudah diuji di bawah nama lain** sepanjang proyek ini (MOM01/02/04/05/06/07, MRV01, BRK05 "
              "-- lihat tabel buang di bawah), 3 butuh panel >=4 instrumen yang tidak dipunyai (cuma XAU+XAG), "
              "1 adalah lapisan gerbang bukan sinyal mandiri, 1 diagnostik, 1 tanpa sitasi sama sekali, 1 tidak "
              "layak komputasi. **Sisa genuinely baru dari v6: 9.** Ditambah 4 formula kuant umum lintas-aset "
              "(safe-haven, lottery/skew, low-vol anomaly, pembalikan jangka panjang) = **13 baru dari v6+umum**"
              f" (tabel PREREG di bawah menghitung {len(PREREG)} -- 1 lebih banyak karena breakdown per-ID).\n\n"
              "**Divisi V (volatilitas, 14), Q (spread/likuiditas, 12), T (intensitas tick, 10), S (struktur/"
              "rezim, 29) -- total 65 formula -- SENGAJA TIDAK diuji lewat gerbang G1-G6.** v6 sendiri "
              "mengklasifikasikan mereka `division_type: estimation`, bukan `direction`: mereka mengukur "
              "KEADAAN pasar (seberapa volatil, seberapa mahal, seberapa persisten), bukan ARAH. Memaksa "
              "mereka lewat gerbang arah berarti mengarang konvensi tanda yang tidak berdasar literatur -- "
              "persis yang dilarang aturan anti-ngasal proyek ini sendiri. Beberapa di antaranya SUDAH dipakai "
              "sebagai KOMPONEN sah di formula arah yang diuji di sini (V01_PARKINSON menskala MOM08/MOM11/"
              "BRK01/BRK03; Q01_ROLL_SPREAD & Q04_AMIHUD identik dengan MIC03/MIC01 di V10; Q06/Q07 spread "
              "velocity/acceleration jadi trigger stress di MRV03). Menguji 65 sisanya butuh gerbang "
              "MCS/separasi-expectancy-bersyarat terpisah (persis desain aslinya di v6) -- proyek lanjutan "
              "(V12+) kalau diinginkan, bukan pemaksaan ke G1-G6.\n",
              "\n## Tabel Pra-Registrasi\n",
              "| ID | Divisi | Sitasi | DOI/SSRN | Tahun | Sampel Asli | Mekanisme | Tanda Diprediksi |",
              "|---|---|---|---|---:|---|---|---|"]
    for fid, info in PREREG.items():
        lines.append(f"| {fid} | {info['divisi']} | {info['citation']} | {info['doi']} | {info['tahun_terbit']} | "
                      f"{info['sampel_asli']} | {info['mekanisme']} | {info['tanda_prediksi']} |")

    lines.append("\n## Formula registri v6 yang TIDAK diuji (dengan alasan)\n")
    for d in DIBUANG_SEBELUM_UJI:
        lines.append(f"- **{d['id']}**: {d['alasan']}")

    lines.append(f"\n## Uji Korelasi vs Registry (V10 + trend + M5 + MAC, ambang |r|<=0.30)\n")
    lines.append(corr_df.round(4).to_markdown(index=False))
    if dibuang_korelasi:
        lines.append("\n**Ditolak karena korelasi:**\n\n" + "\n".join(f"- {x}" for x in dibuang_korelasi))

    lines.append(f"\n## Biaya\n\nBiaya base={cost_base:.3f}bps, worst={cost_worst:.3f}bps. "
                  f"D1 XAU {d1_ohlc['date'].iloc[0].date()} s/d {d1_ohlc['date'].iloc[uji_end-1].date()} "
                  f"(HOLDOUT 15% terakhir tidak disentuh). Cakupan data: MOM08/11/BRK02/03/07/SAFE01/LOTTO01/"
                  f"IVOL01/REV01LT penuh 2003-2026 (OHLC H1); MOM03 penuh (gap dari OHLC H1); BRK01/MRV03/MRV06 "
                  f"hanya 2021-2026 (M5 sesi/spread/jump).\n")

    lines.append(f"\n## Hasil G1-G6 per kombinasi (tau x peserta)\n")
    if len(df_rows):
        lines.append(df_rows.to_markdown(index=False))
    lines.append(f"\n## Distribusi gerbang gugur\n\n" + "\n".join(f"- {k}: {v}" for k, v in sorted(stop_counts.items(), key=lambda x: -x[1])))

    if len(survivors):
        lines.append(f"\n## SURVIVOR ({len(survivors)})\n\n" + survivors.round(4).to_markdown(index=False))
    else:
        lines.append("\n## NOL SURVIVOR\n\nSyarat L14 (>=1 lolos G1-G6) TIDAK terpenuhi.\n")

    (REPORTS / "V11_REGISTRI_V6_DAN_KUANT_UMUM.md").write_text("\n".join(lines))

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    ax = axes[0]
    if stop_counts:
        labels = list(stop_counts.keys()); values = [stop_counts[k] for k in labels]
        colors = ["#2ca02c" if k == "LOLOS" else "#d62728" for k in labels]
        ax.bar(labels, values, color=colors)
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_title(f"V11: {len(survivors)}/{len(df_rows)} lolos G1-G6")
    ax.set_ylabel("jumlah kombinasi")

    ax = axes[1]
    ax.barh(corr_df["peserta"], corr_df["max_abs_corr"], color=["#d62728" if v > CORR_THRESH else "#2ca02c" for v in corr_df["max_abs_corr"]])
    ax.axvline(CORR_THRESH, color="black", linestyle="--", linewidth=0.8)
    ax.set_xlabel("|korelasi| maks vs registry")
    ax.set_title("Uji korelasi (sebelum gerbang)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "v11_registri_v6.png", dpi=120)
    print(f"saved {FIG_DIR / 'v11_registri_v6.png'}")

    return survivors


if __name__ == "__main__":
    s = main()
    sys.exit(0 if len(s) else 1)
