# V11 -- Perluasan registri v6 (E1/E2/E3) + kuant umum lintas-aset

**13 formula BARU diimplementasikan (di bawah plafon), digabung dengan 9 dari V10 = 22 formula arah total diuji G1-G6 sepanjang V10+V11. TOTAL TRIAL V11 untuk DSR = 13.**


## CATATAN METODOLOGI PENTING -- kenapa bukan 500, dan bukan divisi V/Q/T/S

Registri arah v6 (E1 MOM + E2 MRV + E3 BRK) cuma punya **24 formula** total. Dari situ, **11 sudah diuji di bawah nama lain** sepanjang proyek ini (MOM01/02/04/05/06/07, MRV01, BRK05 -- lihat tabel buang di bawah), 3 butuh panel >=4 instrumen yang tidak dipunyai (cuma XAU+XAG), 1 adalah lapisan gerbang bukan sinyal mandiri, 1 diagnostik, 1 tanpa sitasi sama sekali, 1 tidak layak komputasi. **Sisa genuinely baru dari v6: 9.** Ditambah 4 formula kuant umum lintas-aset (safe-haven, lottery/skew, low-vol anomaly, pembalikan jangka panjang) = **13 baru dari v6+umum** (tabel PREREG di bawah menghitung 13 -- 1 lebih banyak karena breakdown per-ID).

**Divisi V (volatilitas, 14), Q (spread/likuiditas, 12), T (intensitas tick, 10), S (struktur/rezim, 29) -- total 65 formula -- SENGAJA TIDAK diuji lewat gerbang G1-G6.** v6 sendiri mengklasifikasikan mereka `division_type: estimation`, bukan `direction`: mereka mengukur KEADAAN pasar (seberapa volatil, seberapa mahal, seberapa persisten), bukan ARAH. Memaksa mereka lewat gerbang arah berarti mengarang konvensi tanda yang tidak berdasar literatur -- persis yang dilarang aturan anti-ngasal proyek ini sendiri. Beberapa di antaranya SUDAH dipakai sebagai KOMPONEN sah di formula arah yang diuji di sini (V01_PARKINSON menskala MOM08/MOM11/BRK01/BRK03; Q01_ROLL_SPREAD & Q04_AMIHUD identik dengan MIC03/MIC01 di V10; Q06/Q07 spread velocity/acceleration jadi trigger stress di MRV03). Menguji 65 sisanya butuh gerbang MCS/separasi-expectancy-bersyarat terpisah (persis desain aslinya di v6) -- proyek lanjutan (V12+) kalau diinginkan, bukan pemaksaan ke G1-G6.


## Tabel Pra-Registrasi

| ID | Divisi | Sitasi | DOI/SSRN | Tahun | Sampel Asli | Mekanisme | Tanda Diprediksi |
|---|---|---|---|---:|---|---|---|
| MOM03 | E1 MOM (v6) | Berkman, Koch, Tuttle & Zhang (2012), Journal of Financial and Quantitative Analysis 47(4):715-741 | 10.1017/S0022109012000270 | 2012 | Saham AS, 1996-2008 | Gap pembukaan setelah jeda pasar berlanjut arahnya karena informasi yang menumpuk selama jeda belum terserap penuh di bar pertama. | gap positif -> gold NAIK; sign(sinyal)=sign(gap). |
| MOM08 | E1 MOM (v6) | Moskowitz, Ooi & Pedersen (2012), Journal of Financial Economics 104(2):228-250 (SSRN abstract_id=2089463) | 10.1016/j.jfineco.2011.11.003 | 2012 | 58 instrumen berjangka lintas kelas aset (ekuitas, FX, komoditas, obligasi), 1965-2009 | Return masa lalu horizon-menengah (time-series momentum) memprediksi return berikutnya dengan tanda sama karena penyesuaian eksposur institusional bertahap, bukan seketika. | return 12-bulan positif -> gold NAIK; sign(sinyal)=sign(r_{t-252:t}). |
| MOM11 | E1 MOM (v6) | George & Hwang (2004), The Journal of Finance 59(5):2145-2176 | 10.1111/j.1540-6261.2004.00695.x | 2004 | Saham NYSE/AMEX/NASDAQ, 1963-2001 | Harga dekat ekstrem 52-minggu menghadapi keengganan peserta merevisi penilaian melewati titik acuan yang menonjol, sehingga penyesuaian tertunda dan berlanjut setelah level itu ditembus. | dekat puncak jendela -> gold NAIK, dekat dasar -> gold TURUN; sign(sinyal)=+1 dekat puncak,-1 dekat dasar. |
| MRV03 | E2 MRV (v6) | Nagel (2012), The Review of Financial Studies 25(7):2005-2039 (SSRN abstract_id=1988706, NBER WP17653) | 10.1093/rfs/hhs066 | 2012 | Saham AS, 1998-2011 (VIX era) | Imbal hasil pembalikan adalah kompensasi penyedia likuiditas dan naik justru saat kapasitas penyediaan likuiditas menipis (spread melebar); menyaring pembalikan berdasar keadaan likuiditas memisahkan pembalikan berbayar dari yang tidak. | gerak besar SAAT spread stress tinggi -> berbalik; sign(sinyal)=-sign(r_{t-L:t}) HANYA saat spread>p75. |
| MRV06 | E2 MRV (v6) | Patton & Sheppard (2015), The Review of Economics and Statistics 97(3):683-697 | 10.1162/REST_a_00503 | 2015 | S&P500 & 105 saham individual, opsi harian | Volatilitas terkonsentrasi di satu sisi (RS+ - RS- besar) menandakan tekanan likuidasi searah bukan kedatangan informasi, sehingga sebagian gerak itu adalah konsesi harga yang kembali setelah tekanan selesai. | SJV besar positif (RS+>>RS-) -> gold TURUN (berbalik); sign(sinyal)=-sign(SJV). |
| BRK01 | E3 BRK (v6) | Zarattini & Aziz (2023), SSRN working paper (abstract_id=4416622) -- BELUM peer-reviewed, mekanisme dasar (pemusatan aliran di pembukaan) didukung Gao/Han/Li/Zhou (2018) JFE peer-reviewed | SSRN:4416622 | 2023 | Saham AS (ORB 5-menit), 2016-2023 | Pembukaan sesi memusatkan aliran order yang menumpuk selama jeda; arah penembusan range awal mencerminkan sisi tekanan yang belum selesai diserap. | tembus ke atas range pembukaan sesi London -> gold NAIK; sign(sinyal)=arah tembus. |
| BRK02 | E3 BRK (v6) | Coles (2001), An Introduction to Statistical Modeling of Extreme Values, Springer Series in Statistics (buku teks EVT standar) | 10.1007/978-1-4471-3675-0 | 2001 | Buku teks metodologi (Peaks-Over-Threshold / GPD), bukan studi pasar tunggal | Gerak yang melampaui ambang ekstrem terkalibrasi dari distribusi ekornya sendiri menandakan kedatangan informasi yang belum terserap, kualitatif berbeda dari gerak besar yang masih dalam distribusi normal. | |return| melampaui ambang GPD -> arah berlanjut; sign(sinyal)=sign(return_t). |
| BRK03 | E3 BRK (v6) | Bollerslev (1986), Journal of Econometrics 31(3):307-327 [fakta clustering volatilitas -- strategi kontraksi-ekspansi sendiri NEED_LOOKUP di v6 utk sumber langsung, ditandai eksplisit] | 10.1016/0304-4076(86)90063-1 | 1986 | Fakta stilisata umum, bukan strategi spesifik | Volatilitas berkelompok; pada transisi kontraksi->ekspansi, penyedia likuiditas belum menyesuaikan kuotasi terhadap rezim baru sehingga gerak berlanjut lebih jauh daripada dibenarkan informasinya. | pemicu ekspansi dari kontraksi -> arah gerak pemicu berlanjut; sign(sinyal)=sign(r_pemicu). |
| BRK07 | E3 BRK (v6) | Adams & MacKay (2007), arXiv:0710.3742 [BUKAN peer-reviewed/DOI/SSRN/NBER -- v6 sendiri menandai ini HANYA layak screening, bukan CONFIRM; tetap diuji di sini dengan label eksplisit derajat-sitasi-lebih-rendah] | arXiv:0710.3742 | 2007 | Simulasi + data well-log (bukan data finansial) | Deteksi titik-perubahan daring Bayesian (BOCPD) memberi probabilitas rezim baru dimulai secara kausal murni; ambil arah gerak terkini hanya saat probabilitas rezim-baru cukup tinggi. | P(rezim baru)>=p_min -> arah gerak terkini berlanjut; sign(sinyal)=sign(r_{t-h:t}). |
| SAFE01 | Umum (safe-haven, lintas-aset) | Baur & Lucey (2010), Financial Review 45(2):217-229; Baur & McDermott (2010), Journal of Banking & Finance 34(8):1886-1898 | 10.1111/j.1540-6288.2010.00244.x; 10.1016/j.jbankfin.2009.12.008 | 2010 | Emas vs indeks saham AS/Eropa/berkembang, 1979-2009 | Emas adalah safe haven bersyarat: saat stres pasar ekuitas ekstrem (proksi VIX melonjak) memicu aliran flight-to-quality yang secara historis mendorong gold outperform. | z(VIX) tinggi -> gold NAIK; sign(sinyal)=sign(z_VIX). |
| LOTTO01 | Umum (lottery/skew, lintas-aset) | Bali, Cakici & Whitelaw (2011), Journal of Financial Economics 99(2):427-446 | 10.1016/j.jfineco.2010.08.014 | 2011 | Saham AS, 1926-2005 | Preferensi investor terhadap aset mirip-lotere membuat aset dengan return maksimum ekstrem baru-baru ini kelebihan permintaan (overpriced), sehingga return berikutnya lebih rendah. | MAX return 21-hari tinggi -> gold TURUN berikutnya; sign(sinyal)=-sign(z_MAX). |
| IVOL01 | Umum (idiosyncratic vol, lintas-aset) | Ang, Hodrick, Xing & Zhang (2006), The Journal of Finance 61(1):259-299 | 10.1111/j.1540-6261.2006.00836.x | 2006 | Saham AS, 1963-2000 | Aset dengan volatilitas realized tinggi historisnya memberi return berikutnya jauh lebih rendah (anomali volatilitas-rendah), bertentangan dengan intuisi risk-return standar. | realized vol 21-hari tinggi -> gold TURUN berikutnya; sign(sinyal)=-sign(z_RV21d). |
| REV01LT | Umum (pembalikan jangka panjang, lintas-aset) | De Bondt & Thaler (1985), The Journal of Finance 40(3):793-805 | 10.1111/j.1540-6261.1985.tb05004.x | 1985 | Saham NYSE, 1926-1982 (portofolio 3-tahun) | Peserta over-reaksi secara sistematis terhadap informasi jangka panjang; pemenang (loser) ekstrem 3-tahun cenderung berbalik dan menjadi loser (pemenang) di periode berikutnya. | return 3-tahun (756 hari) tinggi -> gold TURUN berikutnya (kontrarian); sign(sinyal)=-sign(z_r756d). |

## Formula registri v6 yang TIDAK diuji (dengan alasan)

- **MOM01/02/04/05/06/07 (E1)**: SUDAH DIUJI di bawah nama lain sepanjang proyek ini (bukan formula baru): MOM01~intraday momentum sejenis MAD-Zscore-momentum, MOM02=Momentum-VolScaled (lomba4), MOM04=DriftBurst-tstat (lomba4), MOM05=Mann-Kendall (lomba2), MOM06=QuantReg-slope (lomba2), MOM07=Theil-Sen (lomba2). Menguji ulang dengan nama baru = menghitung hipotesis yang sama dua kali, menaikkan SR_0 tanpa informasi baru.
- **MOM09/MOM10 (E1, panel lintas-instrumen)**: DATA_TIDAK_CUKUP -- spek v6 sendiri mensyaratkan minimum 4 instrumen per bar ('kalau instrumen tersedia < 4 -> bar dilewati'), proyek ini hanya punya 2 (XAU+XAG). Memaksakan panel 2-instrumen bukan lagi cross-sectional z-score yang valid sesuai spek aslinya.
- **MRV01 (E2)**: SUDAH DIUJI sebagai ShortHorizon-Reversal (lomba4), formula identik (z-score return dibalik tanda).
- **MRV02 (E2, panel OU s-score)**: DATA_TIDAK_CUKUP -- sama seperti MOM09/10, perlu panel >=4 instrumen untuk PCA faktor bersama yang valid.
- **MRV04 (E2, MAD z-score gate)**: BUKAN_SINYAL_MANDIRI -- spek v6 sendiri eksplisit: ini lapisan gerbang kekuatan di atas sinyal lain, bukan sinyal arah berdiri sendiri. Tidak dihitung sebagai kandidat terpisah, sesuai instruksi spek sendiri.
- **MRV05 (E2, dekomposisi kontrarian)**: DIAGNOSTIK, BUKAN KANDIDAT -- spek v6 eksplisit menandai formula ini sebagai alat diagnostik (memisahkan over-reaksi vs lead-lag), bukan sinyal untuk digerbangi G1-G6.
- **BRK04 (E3, range compression break)**: TIDAK_ADA_SITASI -- spek v6 sendiri eksplisit 'SAYA TIDAK MENEMUKAN sumber peer-reviewed', ditandai NEED_LOOKUP tanpa kandidat pengganti. Anti-ngasal: tidak diuji tanpa sumber.
- **BRK05 (E3, CUSUM changepoint)**: SUDAH DIUJI EKSTENSIF sebagai sinyal utama v7 (CUSUM) -- terbukti drift capture lewat autopsi 4-uji (L1), bukan sinyal genuine. Tidak diuji ulang (aturan anti-p-hacking eksplisit: sekali gagal, selesai).
- **BRK06 (E3, segmentasi PELT)**: TIDAK_LAYAK_KOMPUTASI + REDUNDAN -- PELT retrospektif yang dijalankan ulang tiap bar (kausal, hanya data<=t) berbiaya O(n) per bar = O(n^2) total untuk >8000 hari, tidak feasible tanpa implementasi inkremental khusus. Selain itu segmen-umur PELT secara konsep sangat mirip CUSUM (BRK05) yang sudah terbukti drift capture -- risiko tinggi temuan yang sama, bukan informasi baru.
- **Divisi V/Q/T/S (v6, 65 formula estimation-type)**: MISMATCH_TIPE_GERBANG -- diklasifikasikan v6 SENDIRI sebagai `division_type: estimation`, bukan `direction`. Spek v6 eksplisit: menguji formula estimasi (volatilitas, spread, intensitas tick, rezim/entropi/Hurst) dengan gerbang arah G1-G6 adalah kesalahan kategori ('menilai termometer dari kemampuannya menebak cuaca besok'). Yang SUDAH dipakai sebagai KOMPONEN sah di formula arah yang diuji di sini: V01_PARKINSON (skala sigma di MOM08/MOM11/BRK01/BRK03), Q01_ROLL_SPREAD & Q04_AMIHUD (=MIC03/MIC01 di V10), Q06/Q07 spread velocity/acceleration (trigger stress di MRV03). Sisanya (V02-14, Q02-12 minus yg dipakai, T01-10, S 29 formula) TIDAK diuji sebagai kandidat arah -- itu akan berarti mengarang konvensi tanda yang tidak berdasar literatur, persis yang dilarang aturan anti-ngasal. Kalau ingin diuji, jalur yang benar adalah gerbang MCS/separasi-expectancy-bersyarat milik divisi masing-masing (proyek terpisah, V12+).

## Uji Korelasi vs Registry (V10 + trend + M5 + MAC, ambang |r|<=0.30)

| peserta                         |   max_abs_corr | vs                            |
|:--------------------------------|---------------:|:------------------------------|
| MOM03_session_gap               |         0.1474 | Momentum-VolScaled            |
| MOM08_tsmom_252d                |         0.332  | V10_COT02_managed_money_crowd |
| MOM11_extreme_proximity         |         0.7598 | TREND_ols_20d                 |
| MRV03_liquidity_reversal        |         0      | nan                           |
| MRV06_signed_jump_reversal      |         0.5726 | Momentum-VolScaled            |
| BRK01_orb_session               |         0.1652 | CUSUM                         |
| BRK02_pot_exceedance            |         0.3557 | Momentum-VolScaled            |
| BRK03_vol_contraction_expansion |         0.164  | MAC03_dxy                     |
| BRK07_bocpd_runlength           |         0.3354 | V10_MIC02_kyle_lambda_gated   |
| SAFE01_vix_safehaven            |         0.2943 | V10_XAS01_gold_silver_ect     |
| LOTTO01_max_return              |         0.3496 | V10_OPT01_gold_vrp            |
| IVOL01_realized_vol             |         0.5506 | V10_OPT01_gold_vrp            |
| REV01LT_long_term_reversal      |         0.487  | TREND_kalman_drift            |

**Ditolak karena korelasi:**

- MOM08_tsmom_252d: korelasi 0.332 vs V10_COT02_managed_money_crowd (>0.30) -- DITOLAK SEBELUM GERBANG
- MOM11_extreme_proximity: korelasi 0.760 vs TREND_ols_20d (>0.30) -- DITOLAK SEBELUM GERBANG
- MRV06_signed_jump_reversal: korelasi 0.573 vs Momentum-VolScaled (>0.30) -- DITOLAK SEBELUM GERBANG
- BRK02_pot_exceedance: korelasi 0.356 vs Momentum-VolScaled (>0.30) -- DITOLAK SEBELUM GERBANG
- BRK07_bocpd_runlength: korelasi 0.335 vs V10_MIC02_kyle_lambda_gated (>0.30) -- DITOLAK SEBELUM GERBANG
- LOTTO01_max_return: korelasi 0.350 vs V10_OPT01_gold_vrp (>0.30) -- DITOLAK SEBELUM GERBANG
- IVOL01_realized_vol: korelasi 0.551 vs V10_OPT01_gold_vrp (>0.30) -- DITOLAK SEBELUM GERBANG
- REV01LT_long_term_reversal: korelasi 0.487 vs TREND_kalman_drift (>0.30) -- DITOLAK SEBELUM GERBANG

## Biaya

Biaya base=2.885bps, worst=13.305bps. D1 XAU 2003-05-05 s/d 2023-02-20 (HOLDOUT 15% terakhir tidak disentuh). Cakupan data: MOM08/11/BRK02/03/07/SAFE01/LOTTO01/IVOL01/REV01LT penuh 2003-2026 (OHLC H1); MOM03 penuh (gap dari OHLC H1); BRK01/MRV03/MRV06 hanya 2021-2026 (M5 sesi/spread/jump).


## Hasil G1-G6 per kombinasi (tau x peserta)

| peserta   |   tau |    n | stopped_at   |   pnl_long_demean |   pnl_short_demean | catatan                                                               |
|:----------|------:|-----:|:-------------|------------------:|-------------------:|:----------------------------------------------------------------------|
| MOM03     |     1 |  479 | G1           |         -3956.5   |          -2085.07  | [CATATAN: tanda TERBALIK akan LOLOS G1 -- data mining, TETAP DIBUANG] |
| MRV03     |     1 |    5 | n<30         |           nan     |            nan     | nan                                                                   |
| BRK01     |     1 |  145 | G1           |          -213.464 |            387.334 |                                                                       |
| BRK03     |     1 |  120 | G1           |          -575.174 |            963.613 |                                                                       |
| SAFE01    |     1 | 1987 | G1           |         -4108.44  |          -3831.46  | [CATATAN: tanda TERBALIK akan LOLOS G1 -- data mining, TETAP DIBUANG] |

## Distribusi gerbang gugur

- G1: 4
- n<30: 1

## NOL SURVIVOR

Syarat L14 (>=1 lolos G1-G6) TIDAK terpenuhi.
