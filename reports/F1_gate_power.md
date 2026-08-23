# F1 -- Uji Daya Gerbang L11 (transmitansi corong v6)

> **Sinyal divalidasi di 5.00 tahun (9395 blok H240, seluruh riwayat XAUUSD yang ada). Biaya divalidasi di 3 tahun terakhir (2024-2026).**

## KOREKSI 1: biaya 'worst' sekarang bersyarat Q10 (spread<=p50, bukan p90)

Q10_SPREAD_PERCENTILE_GATE hanya izinkan entry saat spread<=p50 -- jadi distribusi biaya yang relevan untuk expectancy adalah spread yang LOLOS gerbang (dibatasi p50), bukan p90 seluruh sampel (yang mencakup periode yang Q10 sendiri akan tolak). Menghitung p90 sambil punya gerbang yang melarang p90 = menghukum dua kali. **Efek: biaya worst turun dari basis p90 ke basis p50 (alpha/penalty tetap ketat 1.5x/1.5x).**

## KOREKSI 2: selektivitas via ambang tau EKSPLISIT (bukan target frekuensi)

Semua kandidat sekarang punya ambang kekuatan sinyal tau pada |signal| (grid [1.0, 1.5]), BUKAN threshold yang diturunkan supaya pas ~220 trade/tahun. Edge per trade = IC * sigma * E[z||z|>tau] -- E[z|.] naik dengan tau (tau=0 -> 0.80, tau=1.5 -> ~1.94 untuk normal baku), jadi makin selektif, makin besar edge per trade untuk IC yang sama. Frekuensi trade adalah AKIBAT dari tau, dilaporkan bukan dipaksa. Filter `trades>=300/tahun` tidak ada di pipeline L11 ini -- yang dipakai BR_eff>=100/tahun (F_BR), konsisten dengan §04.

## Tabel kappa PER TAHUN KALENDER (XAUUSD, H240, skenario worst bersyarat Q10)

| tahun | harga rata-rata | spread p25 bps | spread p50 bps (basis worst) | sigma M5 bps | biaya worst bps | sigma H240 bps | **kappa H240 worst** |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 1792.9 | 1.770 | 1.978 | 4.192 | 11.24 | 29.05 | **0.387** |
| 2022 | 1802.5 | 1.886 | 2.159 | 5.136 | 12.32 | 35.59 | **0.346** |
| 2023 | 1943.4 | 1.602 | 1.748 | 4.288 | 10.04 | 29.71 | **0.338** |
| 2024 **<-rezim-sekarang** | 2389.1 | 1.498 | 1.638 | 4.692 | 9.52 | 32.50 | **0.293** |
| 2025 **<-rezim-sekarang** | 3443.1 | 1.567 | 1.832 | 6.070 | 10.73 | 42.05 | **0.255** |
| 2026 **<-rezim-sekarang** | 4572.4 | 1.368 | 1.627 | 10.495 | 10.26 | 72.71 | **0.141** |

**Biaya worst-case: seluruh riwayat (dicampur, TIDAK dipakai untuk kelayakan) = 10.63 bps vs rezim-sekarang (dipakai untuk kelayakan) = 10.13 bps.**

## Expectancy bersih berdampingan: biaya-LAMA vs biaya-BARU, per tau


**tau=1.0**

| IC | gross edge (bps) | net @ biaya-LAMA (10.6bps) | net @ biaya-BARU (10.1bps) |
|---:|---:|---:|---:|
| 0.03 | 1.83 | -8.79 | -8.30 |
| 0.05 | 3.11 | -7.52 | -7.02 |
| 0.08 | 4.91 | -5.71 | -5.22 |
| 0.15 | 9.24 | -1.39 | -0.89 |
| 0.3 | 18.15 | 7.52 | 8.01 |

**tau=1.5**

| IC | gross edge (bps) | net @ biaya-LAMA (10.6bps) | net @ biaya-BARU (10.1bps) |
|---:|---:|---:|---:|
| 0.03 | 2.38 | -8.25 | -7.75 |
| 0.05 | 3.98 | -6.65 | -6.15 |
| 0.08 | 6.34 | -4.29 | -3.79 |
| 0.15 | 12.36 | 1.73 | 2.23 |
| 0.3 | 26.16 | 15.54 | 16.03 |

Sinyal sintetis ber-IC terkontrol disuntikkan ke harga **XAUUSD NYATA** (M15, blok H240 non-overlapping, n=9395 blok, rentang 5.00 tahun -- statistik). n_seeds per IC = **150** (spec: 500 -- dikurangi untuk kecepatan). Biaya worst-case rezim-sekarang (2024-2026): **10.13 bps**.

## Transmitansi per tau


**tau=1.0**

| IC target | Tahap 1 SARINGAN | Tahap 2 ROBUSTNESS | Rantai penuh (CONFIRM) | avg trade/thn | target |
|---:|---:|---:|---:|---:|---|
| 0.03 | 0.0% (target>=80%) | 0.0% (target>=70%) | 0.0% (target>=50%) | 597 | -- |
| 0.05 | 0.0% (target>=80%) | 0.0% (target>=70%) | 0.0% (target>=50%) | 597 | -- |
| 0.08 | 0.0% (target>=80%) | 0.0% (target>=70%) | 0.0% (target>=50%) | 597 | -- |

**tau=1.5**

| IC target | Tahap 1 SARINGAN | Tahap 2 ROBUSTNESS | Rantai penuh (CONFIRM) | avg trade/thn | target |
|---:|---:|---:|---:|---:|---|
| 0.03 | 0.0% (target>=80%) | 0.0% (target>=70%) | 0.0% (target>=50%) | 252 | -- |
| 0.05 | 0.0% (target>=80%) | 0.0% (target>=70%) | 0.0% (target>=50%) | 252 | -- |
| 0.08 | 0.0% (target>=80%) | 0.0% (target>=70%) | 0.0% (target>=50%) | 251 | -- |

## Verdict GM-3 (pada IC=0.05, syarat L11 §02 HUKUM, LOLOS kalau ADA tau yang lolos)

- tau=1.0: screening=0.0%, robustness=0.0%, rantai=0.0% -> GAGAL
- tau=1.5: screening=0.0%, robustness=0.0%, rantai=0.0% -> GAGAL

**GM-3: GAGAL di SEMUA tau -- BERHENTI, perbaiki desain gerbang**

## Gerbang mana yang paling mematikan? (diagnosis per-filter, IC=0.05, tau=1.5)

### Tahap 1 SARINGAN

| filter | % lolos |
|---|---:|
| F_EXPECT (net>0) | 0.0% <-- **PALING MEMATIKAN** |
| F_T15 (t>=1.5) | 0.0% <-- **PALING MEMATIKAN** |
| F_B02 (beat random-matched) | 94.0% |
| F_B05 (beat coin-flip) | 100.0% |
| F_BR (BR_eff>=100/thn) | 100.0% |

### Tahap 2 ROBUSTNESS (dari 0 trial yang lolos tahap 1)

N/A -- nol trial lolos tahap 1.


**Kesimpulan:** gerbang paling mematikan (tau=1.5) adalah **F_EXPECT (net>0)** (0.0% lolos).


sd_SR empiris (dari sharpe 150 trial IC=0.05 tau=1.5, efek samping L11 -- BUKAN pilot 24-trial resmi §01 B5): **0.3000**

**Keterbatasan uji L11 yang wajib diakui:** konstruksi trade di sini adalah SATU eksposur tetap sampai akhir blok (tanpa SL/TP dioptimalkan) -- divisi X (exit & sizing) belum diuji. Kandidat nyata dengan barrier yang dioptimalkan kemungkinan menangkap lebih banyak dari IC yang sama.
