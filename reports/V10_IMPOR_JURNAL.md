# V10 -- IMPOR RUMUS DARI JURNAL

**Anggaran: 9 formula diimplementasikan dari 16 kandidat yang diriset (di bawah plafon 20). 7 dibuang SEBELUM implementasi (data tidak tersedia / sitasi tak terverifikasi / mismatch horizon / tanpa mekanisme). TOTAL TRIAL untuk DSR = 13 (9 formula x tau-grid bertingkat + kandidat gagal uji korelasi).**


## Tabel Pra-Registrasi (ditulis SEBELUM sinyal diuji)

| ID | Kelas | Sitasi | DOI/SSRN | Tahun | Sampel Asli | Mekanisme | Tanda Diprediksi |
|---|---|---|---|---:|---|---|---|
| XAS01 | Lintas-aset lead-lag | Escribano & Granger (1998), Journal of Forecasting 17(2):81-107 | 10.1002/(SICI)1099-131X(199803)17:2<81::AID-FOR680>3.0.CO;2- | 1998 | Gold & silver spot London, harian, 1971-1994 | Gold dan silver berbagi faktor jangka-panjang logam-mulia bersama; deviasi gold dari hubungan kointegrasi historisnya dengan silver cenderung kembali (mean-revert). | ECT positif (gold relatif mahal vs silver) -> gold TURUN; sign(sinyal)=-sign(ECT). |
| OPT01 | Options-implied | Nguyen, Prokopczuk & Wese Simen (2019), Journal of International Money and Finance 94:140-159 | 10.1016/j.jimonfin.2019.02.011 | 2019 | Opsi emas COMEX, 2004-2016 | Variance risk premium (implied vol GVZ dikurangi realized vol) mengompensasi penjual opsi atas risiko volatilitas; VRP tinggi historisnya memprediksi risk premium gold positif. | VRP positif (implied>realized) -> gold NAIK; sign(sinyal)=sign(VRP). |
| COT02 | Crowding/positioning (keluarga MAC05) | Chen & Mo (2023), Journal of Commodity Markets 31, art.100337 (SSRN abstract_id=4166076) | SSRN:4166076 | 2023 | CFTC Disaggregated COT emas, 2006-06 s/d 2022-02 | Money manager (DCOT) berbeda dari Non-Commercial legacy (MAC05) -- kategori spekulatif lebih sempit dan lebih 'hot money'; posisi net yang sangat crowded secara historis mendahului pembalikan saat crowding terurai. | z(mm_net) tinggi (crowded long) -> gold TURUN; sign(sinyal)=-sign(z_mm_net). |
| MIC01 | Order flow proxy (tick) | Amihud (2002), Journal of Financial Markets 5(1):31-56 | 10.1016/S1386-4181(01)00024-6 | 2002 | Saham NYSE, 1964-1997 (bulanan) | Rasio |return|/volume mengukur dampak-harga per unit aliran order; periode illikuid (dampak-harga tinggi) secara historis dikompensasi dengan return berikutnya lebih tinggi (premi likuiditas). | ILLIQ tinggi -> gold NAIK; sign(sinyal)=sign(z_ILLIQ). CATATAN: volume asli Amihud=dolar volume saham; di sini dipakai bid_vol Dukascopy (proksi tick, BUKAN volume eksekusi sebenarnya krn XAU OTC/CFD). |
| MIC02 | Order flow proxy (tick) | Kyle (1985), Econometrica 53(6):1315-1335 | 10.2307/1913210 | 1985 | Model teoretis (bukan empiris pasar tunggal) | Koefisien regresi perubahan harga pada aliran order bertanda (lambda) mengukur intensitas informed trading relatif noise trading; lambda tinggi historisnya berasosiasi dengan kelanjutan (persistence) arah harga. | lambda tinggi -> arah HARI BERJALAN berlanjut ke hari berikutnya; sign(sinyal)=sign(return_hari_ini) DIGERBANG oleh |z_lambda|>=tau. |
| MIC03 | Order flow proxy (tick) | Roll (1984), The Journal of Finance 39(4):1127-1139 | 10.1111/j.1540-6261.1984.tb03897.x | 1984 | Model teoretis + ilustrasi empiris obligasi korporasi AS | Kovariansi serial negatif perubahan harga berasal dari bid-ask bounce; besarnya (spread implisit) adalah proksi biaya likuiditas -- mekanisme premi-likuiditas sama seperti MIC01. | spread implisit lebar -> gold NAIK; sign(sinyal)=sign(z_spread). |
| SEA01 | Musiman | Lakonishok & Smidt (1988), Review of Financial Studies 1(4):403-425 | 10.1093/rfs/1.4.403 | 1988 | DJIA, 1897-1986 | Arus kas institusional turn-of-month (gaji, rebalancing dana pensiun/reksadana) terkonsentrasi di hari terakhir bulan + 3 hari pertama bulan berikutnya; paper asli menemukan HAMPIR SELURUH return positif terkonsentrasi di jendela ini (implikasi: luar-TOM mendekati datar/negatif) -- diuji-transfer ke gold (bukan ekuitas, kelas aset berbeda). | TOM window -> gold NAIK; luar-TOM -> gold TIDAK naik (komplemen dari temuan asli); sign(sinyal)=+1 saat TOM, -1 lainnya. |
| SEA02 | Musiman | French (1980), Journal of Financial Economics 8(1):55-69 [mekanisme]; Kohli (2012), Investment Management and Financial Innovations 9(2) [konfirmasi keberadaan efek hari-minggu pada emas] | 10.1016/0304-405X(80)90021-5 | 1980 | S&P500, 1953-1977 (French); Gold & silver 1980-2012 (Kohli) | Akumulasi informasi akhir pekan dan kondisi likuiditas/penyelesaian berbeda antar hari perdagangan menghasilkan pola return sistematis per hari (efek weekend klasik); Kohli (2012) mengonfirmasi KEBERADAAN efek hari-minggu pada emas tanpa merinci tanda per-hari -- tanda yang diuji di sini mengambil pola klasik French (Senin negatif, Jumat positif), BUKAN angka spesifik Kohli (ditandai eksplisit). | Senin -> gold TURUN, Jumat -> gold NAIK (hari lain dikecualikan); sign(sinyal)=-1 Senin, +1 Jumat. |
| EVT01 | Event-driven | Lucca & Moench (2015), The Journal of Finance 70(1):329-371 | 10.1111/jofi.12196 | 2015 | Indeks ekuitas AS, 1994-2011 (jendela 24 jam pra-FOMC) | Resolusi ketidakpastian kebijakan moneter terkompresi di 24 jam sebelum pengumuman FOMC terjadwal menghasilkan drift ekuitas naik yang kuat; sebagai aset safe-haven yang secara historis berkorelasi negatif dengan sentimen risk-on ekuitas, gold diprediksi menunjukkan drift BERLAWANAN pada jendela yang sama. | Hari bursa terakhir sebelum tanggal keputusan FOMC -> gold TURUN; hari lain -> gold TIDAK turun (komplemen); sign(sinyal)=-1 pra-FOMC, +1 lainnya. CATATAN: tanggal FOMC diverifikasi HANYA 2021-2026 dari federalreserve.gov/monetarypolicy/fomccalendars.htm (halaman resmi hanya menyimpan riwayat ~5 tahun) -- TIDAK ditebak untuk tahun sebelumnya. |

## Kandidat DIBUANG sebelum implementasi (dengan alasan)

- **TERM01-03 (contango/backwardation, convenience yield, lease rate)**: DATA_TIDAK_TERSEDIA -- GOFO/LBMA lease rate dihentikan 2015, tidak ada API gratis untuk kurva futures COMEX multi-maturity (Stooq diblokir bot-check JS, FirstRateData/Kaggle berbayar, FRED tidak punya seri lease rate). Formula dari Gorton & Rouwenhorst (2006, NBER w10595) dan Erb & Harvey (2006, FAJ 62(2):69-97) valid secara sitasi tapi tidak bisa diimplementasikan tanpa data kurva.
- **XAS02 (GDX miners lead-lag gold)**: TIDAK_ADA_SITASI_AKADEMIK -- pencarian hanya menemukan artikel industri/blog (Sprott, discoveryalert, dst), bukan paper peer-review dengan mekanisme dan tanda yang bisa dipra-registrasi. Ditolak per aturan anti-ngasal (tanpa mekanisme -> tolak).
- **OPT02 (skew opsi emas)**: DATA_TIDAK_TERSEDIA -- perlu rantai opsi (option chain) lengkap, tidak ada sumber gratis.
- **OPT03 (struktur tenor GVZ)**: DATA_TIDAK_TERSEDIA -- FRED hanya punya GVZCLS front-month, tidak ada tenor lain gratis.
- **COT03 (rasio konsentrasi top-4/top-8 trader)**: SITASI_TIDAK_TERVERIFIKASI -- kandidat paper (management-review.org, 'Traders Concentration, Hedging Pressure, and Risk...') PDF tidak bisa diparse untuk verifikasi DOI/mekanisme dalam anggaran riset; bukan berarti idenya salah, tapi aturan anti-ngasal melarang mengarang detail yang tidak terverifikasi. Data konsentrasi (Conc_Net_LE_4/8_TDR) SUDAH terunduh di dcot_gold.parquet kalau nanti sitasi valid ditemukan.
- **EVT02 (CPI/NFP surprise-day momentum, Christie-David/Chaudhry/Koch 2000)**: DATA_TIDAK_TERSEDIA_LENGKAP -- mekanisme dan sitasi (JEB 52(5):405-421, DOI 10.1016/S0148-6195(00)00029-1) TERVERIFIKASI, tapi jadwal tanggal rilis CPI/NFP presisi multi-tahun tidak berhasil diverifikasi lewat sumber gratis dalam anggaran waktu riset ini (beda dengan FOMC yang halaman resminya langsung memberi tabel). Tidak ditebak.
- **SEA03 (sesi London/NY overlap)**: MISMATCH_HORIZON -- mekanisme (Ranaldo 2009, J. Banking & Finance 33(12):2199-2206, DOI 10.1016/j.jbankfin.2009.05.019) TERVERIFIKASI, tapi efeknya secara definisi berskala intraday-jam; UJI_BUNUH_M5 sudah membuktikan M5 mati, dan menguji versi 'return D1 tutup-ke-tutup dikondisikan sesi mana yang buka' mengencerkan mekanisme aslinya sampai tidak representatif. Dibuang karena horizon, bukan gagal gerbang.

## Uji Korelasi vs Registry Lama (ambang |r|<=0.30, diuji SEBELUM gerbang)

| peserta                   |   max_abs_corr | vs                        |
|:--------------------------|---------------:|:--------------------------|
| XAS01_gold_silver_ect     |         0.2829 | MAC05_cot_crowding        |
| OPT01_gold_vrp            |         0.1387 | MAC04_residual_meanrevert |
| COT02_managed_money_crowd |         0.5989 | MAC05_cot_crowding        |
| MIC01_amihud              |         0.0728 | TREND_kalman_drift        |
| MIC02_kyle_lambda_gated   |         0.047  | Momentum-VolScaled        |
| MIC03_roll_spread         |         0.0909 | TREND_kalman_drift        |
| SEA01_turn_of_month       |         0.0891 | MAC01_realyield           |
| SEA02_day_of_week         |         0.1275 | Momentum-VolScaled        |
| EVT01_pre_fomc            |         0.0375 | DriftBurst-tstat          |

**Ditolak karena korelasi:**

- COT02_managed_money_crowd: korelasi 0.599 vs MAC05_cot_crowding (>0.30) -- DITOLAK SEBELUM GERBANG

## Biaya & kerangka D1

Biaya base=2.885bps, worst=13.305bps. D1 XAU 2003-05-05 s/d 2023-02-20 (HOLDOUT 15% terakhir tidak disentuh). Cakupan data per formula BERBEDA-BEDA (lihat catatan G3 di tabel hasil) -- XAS01/MIC01-03/EVT01 hanya 2021-2026 (XAG, M5 micro, FOMC terverifikasi), COT02 dari 2006, OPT01 dari 2008 (GVZ), SEA01/SEA02 penuh 2003-2026.


## Hasil G1-G6 per kombinasi (tau x peserta)

| peserta   |   tau |    n | stopped_at   |   expectancy_worst |   pnl_long_demean |   pnl_short_demean | catatan                                                               |
|:----------|------:|-----:|:-------------|-------------------:|------------------:|-------------------:|:----------------------------------------------------------------------|
| XAS01     |   1   |  221 | G2           |           -3.6952  |           nan     |           nan      | nan                                                                   |
| XAS01     |   1.5 |  128 | G1           |          nan       |          -250.412 |           688.436  |                                                                       |
| XAS01     |   2   |   58 | G1           |          nan       |          -160.035 |           620.421  |                                                                       |
| OPT01     |   1   | 1177 | G1           |          nan       |         -2838.84  |         -2743.65   | [CATATAN: tanda TERBALIK akan LOLOS G1 -- data mining, TETAP DIBUANG] |
| MIC01     |   1   |  141 | G1           |          nan       |           158.896 |          -208.675  |                                                                       |
| MIC02     |   1   |   61 | G1           |          nan       |           204.239 |           -60.2999 |                                                                       |
| MIC03     |   1   |  123 | G2           |           -7.75095 |           nan     |           nan      | nan                                                                   |
| MIC03     |   1.5 |   40 | G1           |          nan       |          -527.126 |           nan      |                                                                       |
| MIC03     |   2   |   14 | n<30         |          nan       |           nan     |           nan      | nan                                                                   |
| SEA01     |   1   | 7194 | G1           |          nan       |         -1783.05  |        -16103.2    | [CATATAN: tanda TERBALIK akan LOLOS G1 -- data mining, TETAP DIBUANG] |
| SEA02     |   1   | 2066 | G1           |          nan       |         -5200.15  |          -215.264  | [CATATAN: tanda TERBALIK akan LOLOS G1 -- data mining, TETAP DIBUANG] |
| EVT01     |   1   |  753 | G1           |          nan       |         -2478.73  |          -243.846  | [CATATAN: tanda TERBALIK akan LOLOS G1 -- data mining, TETAP DIBUANG] |

## Distribusi gerbang gugur

- G1: 9
- G2: 2
- n<30: 1

## NOL SURVIVOR

Syarat L14 (>=1 lolos G1-G6) TIDAK terpenuhi. Bagian B-E tidak dikerjakan. Nol dari 9 rumus jurnal berkualitas adalah jawaban, bukan alasan mencari 20 lagi.
