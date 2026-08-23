# F0 -- Model Biaya PER-REZIM (koreksi metodologi)

**Kesalahan sebelumnya:** kappa/expectancy dihitung dari rata-rata spread di SELURUH riwayat sekaligus. Salah -- biaya dalam bps = spread_USD/harga, dan harga emas berubah besar antar tahun (2012 ~$1650-1800, sekarang jauh lebih tinggi). Merata-ratakan bps lintas rezim harga berbeda menghasilkan angka yang TIDAK mewakili kondisi tahun manapun.

**Metodologi yang benar (diterapkan mulai sekarang):**
- **DAYA STATISTIK** (IC, t-stat, K_eff, T_confirm) -> diukur di SELURUH riwayat yang ada (2021-2026). Itu gunanya riwayat panjang: sampel besar.
- **KELAYAKAN BIAYA** (kappa, expectancy bersih, L11) -> diukur HANYA di **3 tahun terakhir yang tersedia** (2024-2026), rezim biaya yang relevan untuk eksekusi NYATA hari ini, bukan rezim harga 2012.


## Tabel kappa PER TAHUN KALENDER -- XAUUSD, H240, skenario worst BERSYARAT Q10 (spread<=p50, FULL, tidak disembunyikan)

| tahun | harga rata-rata | spread p25 bps | spread p50 bps (basis worst) | sigma M5 bps | biaya worst bps | sigma H240 bps | **kappa H240 worst** | n bar M5 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 1792.9 | 1.770 | 1.978 | 4.192 | 11.24 | 29.05 | **0.387** | 32,832 |
| 2022 | 1802.5 | 1.886 | 2.159 | 5.136 | 12.32 | 35.59 | **0.346** | 89,856 |
| 2023 | 1943.4 | 1.602 | 1.748 | 4.288 | 10.04 | 29.71 | **0.338** | 90,144 |
| 2024 **<-rezim-sekarang** | 2389.1 | 1.498 | 1.638 | 4.692 | 9.52 | 32.50 | **0.293** | 90,432 |
| 2025 **<-rezim-sekarang** | 3443.1 | 1.567 | 1.832 | 6.070 | 10.73 | 42.05 | **0.255** | 90,144 |
| 2026 **<-rezim-sekarang** | 4572.4 | 1.368 | 1.627 | 10.495 | 10.26 | 72.71 | **0.141** | 57,600 |

## Biaya worst-case: SELURUH riwayat vs rezim-sekarang

| rezim | tahun | biaya worst H240 (bps) |
|---|---|---:|
| Seluruh riwayat (dicampur, TIDAK dipakai lagi untuk kelayakan) | 2021-2026 | 10.63 |
| **Rezim sekarang (dipakai untuk kelayakan biaya)** | 2024-2026 | **10.13** |

## Expectancy bersih (gross edge - biaya) berdampingan: biaya-LAMA vs biaya-BARU, per tau

Sinyal sintetis, 100 seed per IC, dievaluasi pada blok H240 dari **data rezim-sekarang saja** (2024-2026, n=4961 blok). Ambang selektivitas tau EKSPLISIT (bukan diturunkan dari target frekuensi) -- edge per trade = IC * sigma * E[z||z|>tau], E[z|.] naik dengan tau.


**tau=1.0**

| IC | gross edge (bps) | net @ biaya-LAMA (10.6bps) | net @ biaya-BARU (10.1bps) |
|---:|---:|---:|---:|
| 0.03 | 2.24 | -8.38 | -7.89 |
| 0.05 | 3.66 | -6.96 | -6.47 |
| 0.08 | 5.79 | -4.84 | -4.34 |
| 0.15 | 10.73 | 0.10 | 0.60 |
| 0.3 | 21.06 | 10.43 | 10.93 |

**tau=1.5**

| IC | gross edge (bps) | net @ biaya-LAMA (10.6bps) | net @ biaya-BARU (10.1bps) |
|---:|---:|---:|---:|
| 0.03 | 2.72 | -7.90 | -7.41 |
| 0.05 | 4.61 | -6.02 | -5.52 |
| 0.08 | 7.46 | -3.17 | -2.67 |
| 0.15 | 14.41 | 3.78 | 4.28 |
| 0.3 | 30.43 | 19.81 | 20.30 |

## Pernyataan metodologi (wajib dicantumkan di semua laporan turunan)

> **Sinyal divalidasi di 2021-2026 (6 tahun). Kelayakan biaya divalidasi di 2024-2026 (3 tahun terakhir) -- rezim biaya yang relevan untuk eksekusi hari ini.**
