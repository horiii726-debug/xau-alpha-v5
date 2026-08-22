# F7 -- Divisi M (ML & Meta-labeling)

**PERINGATAN: ini hasil SMOKE TEST (30.000 bar, ~7% dari partisi screen
penuh 451.008 bar), BUKAN run skala penuh.** Kode M01/M02/M03 (tree-
ensemble) dan pemilihan primer M11 dinamis dari F6 sudah selesai ditulis
dan divalidasi lewat smoke test ini (terbukti jalan tanpa error, logika
pemilihan primer F6 terbukti bekerja), TAPI belum pernah dijalankan di
data penuh -- F6 sendiri belum selesai (lihat F6_screening.md), jadi
primer M11 di bawah ini (E80_QUANTREG_tau0.25) dipilih dari hasil F6
SMOKE-TEST lama, BUKAN dari 11 sinyal F6 skala-penuh yang baru selesai
(yang mana E80 belum sempat diuji ulang di skala penuh). Angka-angka di
bawah TIDAK BOLEH dibaca sebagai hasil final divisi M.

XAUUSD, fitur kontinu (momentum/drift-burst/Mann-Kendall/realized-skew/sigma), target return forward H60, CPCV purged+embargo (12 dari 66 path per model -- subset demi anggaran komputasi, tetap purged+embargo, K-fold biasa TIDAK dipakai sesuai M1). SINGLE_ASSET_ONLY, UNDERPOWERED_PANEL. M06/M07/M08 (Lasso/Ridge/ElasticNet) baseline wajib. M01 CatBoost, M02 XGBoost (monotone), M03 LightGBM DIUJI. M11 meta-labeling primer = E80_QUANTREG_tau0.25 (net-expectancy terbaik dari F6_screening.md).

## Empat pertanyaan Anda

**1. Berapa sinyal expectancy KOTORNYA positif?** 8 dari 29 kandidat M.

| Kandidat | Expectancy kotor (bps) | N trade |
|---|---:|---:|
| M11_META_LABELING_t0.6 | 2.794 | 503 |
| M11_META_LABELING_t0.5 | 1.768 | 4700 |
| M_PRIMARY_UNFILTERED_E80_QUANTREG_tau0.25 | 1.076 | 23236 |
| M07_RIDGE_a10.0 | 0.027 | 6871 |
| M07_RIDGE_a1.0 | 0.026 | 6871 |
| M07_RIDGE_a0.01 | 0.026 | 6871 |
| M07_RIDGE_a0.1 | 0.026 | 6871 |
| M03_LIGHTGBM_d4_lr0.03 | 0.011 | 7008 |

**2. Berapa bps biaya harus turun supaya bersih positif?**

Kandidat terbaik keseluruhan (M11_META_LABELING_t0.6): expectancy kotor 2.794 bps, breakeven cost = 2.794 bps. Biaya saat ini 3.0 bps proxy -> **perlu turun 0.206 bps** supaya net tepat impas.

**3. Kandidat mana yang paling dekat lolos, kurang di centang mana?**

**M11_META_LABELING_t0.5** -- 6/15 centang.
Lolos: bootstrap_ci95, mc1>=p95, walkforward>=80%, seed_stable, trades/yr>=300, bh_fdr
Kurang di: expectancy>0, t_stat>=3.0, beat_all_nulls, cpcv>=80%, last_third_sig, mc3, mc5, dsr>=0.95, pbo<=0.50

**4. t-stat tertinggi yang tercapai?**

**t = -0.675** (M11_META_LABELING_t0.6). Interpretasi: NEGATIF -- arah sinyal salah/tidak ada edge sama sekali di sisi ini, bukan soal sampel kurang.

## Ringkasan lengkap: 29 kandidat diuji, 0 lolos >=13/15 centang

| Kandidat | N trade | Gross bps | Net bps | Breakeven cost bps | t-stat | Checks (dari 15) | DSR | PBO |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M11_META_LABELING_t0.6 | 503 | 2.79 | -0.21 | 2.79 | -0.68 | 2/15 | 0.000 | 1.000 |
| M11_META_LABELING_t0.5 | 4700 | 1.77 | -1.23 | 1.77 | -8.45 | 6/15 | 0.000 | 1.000 |
| M_PRIMARY_UNFILTERED_E80_QUANTREG_tau0.25 | 23236 | 1.08 | -1.92 | 1.08 | -19.25 | 5/15 | 0.000 | 1.000 |
| M07_RIDGE_a10.0 | 6871 | 0.03 | -2.97 | 0.03 | -20.00 | 5/15 | 0.000 | 1.000 |
| M07_RIDGE_a1.0 | 6871 | 0.03 | -2.97 | 0.03 | -20.03 | 5/15 | 0.000 | 1.000 |
| M07_RIDGE_a0.01 | 6871 | 0.03 | -2.97 | 0.03 | -20.03 | 5/15 | 0.000 | 1.000 |
| M07_RIDGE_a0.1 | 6871 | 0.03 | -2.97 | 0.03 | -20.03 | 5/15 | 0.000 | 1.000 |
| M03_LIGHTGBM_d4_lr0.03 | 7008 | 0.01 | -2.99 | 0.01 | -19.04 | 5/15 | 0.000 | 1.000 |
| M02_XGBOOST_MONO_d3_lr0.1 | 8949 | -0.04 | -3.04 | 0.00 | -22.29 | 5/15 | 0.000 | 1.000 |
| M01_CATBOOST_d4_lr0.03 | 8212 | -0.11 | -3.11 | 0.00 | -21.67 | 5/15 | 0.000 | 1.000 |
| M02_XGBOOST_MONO_d3_lr0.03 | 9218 | -0.21 | -3.21 | 0.00 | -23.86 | 5/15 | 0.000 | 1.000 |
| M02_XGBOOST_MONO_d5_lr0.03 | 9163 | -0.67 | -3.67 | 0.00 | -32.46 | 5/15 | 0.000 | 1.000 |
| M01_CATBOOST_d6_lr0.1 | 9246 | -0.78 | -3.78 | 0.00 | -34.90 | 5/15 | 0.000 | 1.000 |
| M03_LIGHTGBM_d4_lr0.1 | 9258 | -0.90 | -3.90 | 0.00 | -36.49 | 5/15 | 0.000 | 1.000 |
| M03_LIGHTGBM_d6_lr0.1 | 9066 | -0.91 | -3.91 | 0.00 | -36.39 | 5/15 | 0.000 | 1.000 |
| M03_LIGHTGBM_d6_lr0.03 | 9283 | -0.94 | -3.94 | 0.00 | -36.58 | 5/15 | 0.000 | 1.000 |
| M06_LASSO_a0.001 | 7173 | -1.32 | -4.32 | 0.00 | -42.75 | 5/15 | 0.000 | 1.000 |
| M06_LASSO_a0.01 | 7173 | -1.32 | -4.32 | 0.00 | -42.75 | 5/15 | 0.000 | 1.000 |
| M06_LASSO_a0.1 | 7173 | -1.32 | -4.32 | 0.00 | -42.75 | 5/15 | 0.000 | 1.000 |
| M06_LASSO_a1.0 | 7173 | -1.32 | -4.32 | 0.00 | -42.75 | 5/15 | 0.000 | 1.000 |
| M08_ELASTICNET_a0.01_l10.3 | 7173 | -1.32 | -4.32 | 0.00 | -42.75 | 5/15 | 0.000 | 1.000 |
| M08_ELASTICNET_a0.01_l10.7 | 7173 | -1.32 | -4.32 | 0.00 | -42.75 | 5/15 | 0.000 | 1.000 |
| M08_ELASTICNET_a0.1_l10.3 | 7173 | -1.32 | -4.32 | 0.00 | -42.75 | 5/15 | 0.000 | 1.000 |
| M08_ELASTICNET_a0.1_l10.7 | 7173 | -1.32 | -4.32 | 0.00 | -42.75 | 5/15 | 0.000 | 1.000 |
| M08_ELASTICNET_a1.0_l10.3 | 7173 | -1.32 | -4.32 | 0.00 | -42.75 | 5/15 | 0.000 | 1.000 |
| M08_ELASTICNET_a1.0_l10.7 | 7173 | -1.32 | -4.32 | 0.00 | -42.75 | 5/15 | 0.000 | 1.000 |
| M01_CATBOOST_d4_lr0.1 | 9350 | -1.58 | -4.58 | 0.00 | -47.31 | 5/15 | 0.000 | 1.000 |
| M01_CATBOOST_d6_lr0.03 | 9349 | -1.64 | -4.64 | 0.00 | -47.61 | 5/15 | 0.000 | 1.000 |
| M02_XGBOOST_MONO_d5_lr0.1 | 9339 | -1.65 | -4.65 | 0.00 | -48.50 | 5/15 | 0.000 | 1.000 |

## Vonis F7

**NOL kandidat lolos >=13/15 checks.**

Aturan M6/prioritas M11: meta-labeling terbaik (M11_META_LABELING_t0.6, -0.21bps) vs primer polos (-1.92bps) -- meta-labeling MENGALAHKAN primer.

Aturan M6 (tree-ensemble vs baseline linear): tree terbaik (M03_LIGHTGBM_d4_lr0.03, -2.99bps) vs linear terbaik (M07_RIDGE_a10.0, -2.97bps) -- linear TETAP lebih baik, tree-ensemble TIDAK membantu di sini, wajib gagal per aturan M6.