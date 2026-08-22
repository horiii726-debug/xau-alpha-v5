# F7 -- Divisi M (ML & Meta-labeling)

XAUUSD, fitur kontinu (momentum/drift-burst/Mann-Kendall/realized-skew/sigma), target return forward H60, CPCV purged+embargo (12 dari 66 path per model -- subset demi anggaran komputasi, tetap purged+embargo, K-fold biasa TIDAK dipakai sesuai M1). SINGLE_ASSET_ONLY, UNDERPOWERED_PANEL. Model tree-ensemble (M01-M05,M09,M10,CatBoost/XGBoost/LightGBM) TIDAK diuji -- paket belum terpasang di lingkungan ini, di luar anggaran waktu untuk instalasi+uji.

## Ringkasan: 17 kandidat diuji, 0 lolos >=13/15 centang

| Kandidat | N trade | Expectancy net bps | t-stat | Checks (dari 15) | DSR |
|---|---:|---:|---:|---:|---:|
| M11_META_LABELING_t0.5 | 2181 | -0.89 | -2.50 | 5/15 | 0.000 |
| M_PRIMARY_UNFILTERED_E01_L12 | 351973 | -3.38 | -133.91 | 5/15 | 0.000 |
| M07_RIDGE_a1.0 | 5226 | -3.76 | -41.96 | 5/15 | 0.000 |
| M07_RIDGE_a0.01 | 5226 | -3.76 | -42.00 | 5/15 | 0.000 |
| M07_RIDGE_a0.1 | 5226 | -3.76 | -42.00 | 5/15 | 0.000 |
| M07_RIDGE_a10.0 | 5227 | -3.76 | -41.97 | 5/15 | 0.000 |
| M06_LASSO_a0.001 | 4501 | -3.86 | -42.29 | 5/15 | 0.000 |
| M06_LASSO_a0.01 | 4501 | -3.86 | -42.29 | 5/15 | 0.000 |
| M06_LASSO_a0.1 | 4501 | -3.86 | -42.29 | 5/15 | 0.000 |
| M06_LASSO_a1.0 | 4501 | -3.86 | -42.29 | 5/15 | 0.000 |
| M08_ELASTICNET_a0.01_l10.3 | 4501 | -3.86 | -42.29 | 5/15 | 0.000 |
| M08_ELASTICNET_a0.01_l10.7 | 4501 | -3.86 | -42.29 | 5/15 | 0.000 |
| M08_ELASTICNET_a0.1_l10.3 | 4501 | -3.86 | -42.29 | 5/15 | 0.000 |
| M08_ELASTICNET_a0.1_l10.7 | 4501 | -3.86 | -42.29 | 5/15 | 0.000 |
| M08_ELASTICNET_a1.0_l10.3 | 4501 | -3.86 | -42.29 | 5/15 | 0.000 |
| M08_ELASTICNET_a1.0_l10.7 | 4501 | -3.86 | -42.29 | 5/15 | 0.000 |
| M11_META_LABELING_t0.6 | 55 | -4.77 | -2.43 | 5/15 | 0.000 |

## Vonis F7

**NOL kandidat lolos >=13/15 checks.**

Kandidat dengan expectancy tertinggi: M11_META_LABELING_t0.5, -0.89 bps.

Aturan M6/prioritas M11: meta-labeling terbaik (M11_META_LABELING_t0.5, -0.89bps) vs primer polos (-3.38bps) -- meta-labeling MENGALAHKAN primer.