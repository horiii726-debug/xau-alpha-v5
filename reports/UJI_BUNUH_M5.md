# UJI BUNUH M5

## 1. Biaya round-turn nyata (M5, jam aktif, LATIH)

spread p50=1.760bps, p90=2.316bps, komisi=0.280bps.
**Biaya BASE (p50, slip 0.5x)=2.920bps. Biaya WORST (p90, slip 1.5x)=6.071bps.**


## 2. Sigma per bar M5 (realized)

**4.693 bps/bar.**


## 3. Winrate breakeven per hold

|   hold |   sigma_hold_bps |   p_breakeven |
|-------:|-----------------:|--------------:|
|      1 |           4.6926 |        0.8899 |
|      3 |           8.1278 |        0.7251 |
|      6 |          11.4944 |        0.6592 |
|     12 |          16.2555 |        0.6125 |
|     24 |          22.9888 |        0.5796 |

## 4. Winrate aktual vs breakeven

| peserta            |   hold |      n |   winrate_aktual |   p_breakeven |   selisih |
|:-------------------|-------:|-------:|-----------------:|--------------:|----------:|
| CUSUM              |      1 |  26643 |           0.4858 |        0.8899 |   -0.4041 |
| CUSUM              |      3 |  26643 |           0.4841 |        0.7251 |   -0.241  |
| CUSUM              |      6 |  26643 |           0.4815 |        0.6592 |   -0.1777 |
| CUSUM              |     12 |  26643 |           0.4883 |        0.6125 |   -0.1242 |
| CUSUM              |     24 |  26643 |           0.4961 |        0.5796 |   -0.0835 |
| MAC05_cot_crowding |      1 | 258911 |           0.3926 |        0.8899 |   -0.4972 |
| MAC05_cot_crowding |      3 | 258909 |           0.395  |        0.7251 |   -0.3301 |
| MAC05_cot_crowding |      6 | 258906 |           0.399  |        0.6592 |   -0.2602 |
| MAC05_cot_crowding |     12 | 258900 |           0.4064 |        0.6125 |   -0.2061 |
| MAC05_cot_crowding |     24 | 258888 |           0.411  |        0.5796 |   -0.1686 |
| MAC07_ridge_combo  |      1 | 122112 |           0.3729 |        0.8899 |   -0.517  |
| MAC07_ridge_combo  |      3 | 122112 |           0.3758 |        0.7251 |   -0.3493 |
| MAC07_ridge_combo  |      6 | 122112 |           0.3813 |        0.6592 |   -0.2779 |
| MAC07_ridge_combo  |     12 | 122112 |           0.3892 |        0.6125 |   -0.2233 |
| MAC07_ridge_combo  |     24 | 122112 |           0.394  |        0.5796 |   -0.1856 |

## 5. Plafon Oracle (arah selalu benar)

|   hold |   gross_oracle_bps |   net_oracle_base_bps |   net_oracle_worst_bps |
|-------:|-------------------:|----------------------:|-----------------------:|
|      1 |              3.744 |                 0.825 |                 -2.327 |
|      3 |              6.485 |                 3.566 |                  0.414 |
|      6 |              9.171 |                 6.252 |                  3.1   |
|     12 |             12.97  |                10.051 |                  6.899 |
|     24 |             18.343 |                15.423 |                 12.272 |

## 6. Persentase bar |return|>2x biaya

|   hold |   pct_bar_gt_2x_biaya |
|-------:|----------------------:|
|      1 |                 16.85 |
|      3 |                 32.09 |
|      6 |                 42.37 |
|     12 |                 52.11 |
|     24 |                 60.7  |

## VONIS

**M5 MATI -- winrate aktual < breakeven di SEMUA hold & peserta**
