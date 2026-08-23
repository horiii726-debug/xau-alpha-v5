# F0 -- Model Biaya PER-REZIM (koreksi metodologi)

**Kesalahan sebelumnya:** kappa/expectancy dihitung dari rata-rata spread di SELURUH riwayat sekaligus. Salah -- biaya dalam bps = spread_USD/harga, dan harga emas berubah besar antar tahun (2012 ~$1650-1800, sekarang jauh lebih tinggi). Merata-ratakan bps lintas rezim harga berbeda menghasilkan angka yang TIDAK mewakili kondisi tahun manapun.

**Metodologi yang benar (diterapkan mulai sekarang):**
- **DAYA STATISTIK** (IC, t-stat, K_eff, T_confirm) -> diukur di SELURUH riwayat yang ada (2021-2026). Itu gunanya riwayat panjang: sampel besar.
- **KELAYAKAN BIAYA** (kappa, expectancy bersih, L11) -> diukur HANYA di **3 tahun terakhir yang tersedia** (2024-2026), rezim biaya yang relevan untuk eksekusi NYATA hari ini, bukan rezim harga 2012.


## Tabel kappa PER TAHUN KALENDER -- XAUUSD, H240, skenario worst (FULL, tidak disembunyikan)

| tahun | harga rata-rata | spread p50 bps | spread p90 bps | sigma M5 bps | biaya worst bps | sigma H240 bps | **kappa H240 worst** | n bar M5 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 1792.9 | 1.978 | 6.237 | 4.192 | 33.60 | 29.05 | **1.157** | 32,832 |
| 2022 | 1802.5 | 2.159 | 6.497 | 5.136 | 35.09 | 35.59 | **0.986** | 89,856 |
| 2023 | 1943.4 | 1.748 | 5.239 | 4.288 | 28.37 | 29.71 | **0.955** | 90,144 |
| 2024 **<-rezim-sekarang** | 2389.1 | 1.638 | 3.715 | 4.692 | 20.43 | 32.50 | **0.628** | 90,432 |
| 2025 **<-rezim-sekarang** | 3443.1 | 1.832 | 4.596 | 6.070 | 25.24 | 42.05 | **0.600** | 90,144 |
| 2026 **<-rezim-sekarang** | 4572.4 | 1.627 | 5.522 | 10.495 | 30.70 | 72.71 | **0.422** | 57,600 |

## Biaya worst-case: SELURUH riwayat vs rezim-sekarang

| rezim | tahun | biaya worst H240 (bps) |
|---|---|---:|
| Seluruh riwayat (dicampur, TIDAK dipakai lagi untuk kelayakan) | 2021-2026 | 28.22 |
| **Rezim sekarang (dipakai untuk kelayakan biaya)** | 2024-2026 | **23.84** |

## Expectancy bersih (gross edge - biaya) berdampingan: biaya-LAMA vs biaya-BARU

Sinyal sintetis, threshold ~220 trade/tahun, 100 seed per IC, dievaluasi pada blok H240 dari **data rezim-sekarang saja** (2024-2026, n=4961 blok) -- gross edge itu sendiri TIDAK berubah dengan rezim biaya, yang berubah adalah biaya yang dikurangkan.

| IC | gross edge (bps) | net @ biaya-LAMA (seluruh riwayat, 28.2bps) | net @ biaya-BARU (rezim-sekarang, 23.8bps) |
|---:|---:|---:|---:|
| 0.03 | 2.86 | -25.36 | -20.98 |
| 0.05 | 4.79 | -23.43 | -19.05 |
| 0.08 | 7.78 | -20.44 | -16.05 |
| 0.15 | 14.93 | -13.30 | -8.91 |
| 0.3 | 31.99 | 3.77 | 8.15 |

## Pernyataan metodologi (wajib dicantumkan di semua laporan turunan)

> **Sinyal divalidasi di 2021-2026 (6 tahun). Kelayakan biaya divalidasi di 2024-2026 (3 tahun terakhir) -- rezim biaya yang relevan untuk eksekusi hari ini.**
