# LOMBA 2 -- TREN / KEMIRINGAN

Target: t-stat slope OLS pada window N bar KE DEPAN (standardisasi otomatis via se(slope)). Prediktor dari window N bar SEBELUM t. Data M5, subsampling 4000 titik evaluasi merata sepanjang seri.


## N=12 bar

| peserta           |   IC_spearman |   sign_accuracy |   n_test |   p_value_boot_vs_50pct |
|:------------------|--------------:|----------------:|---------:|------------------------:|
| Kalman-drift      |       -0.0021 |          0.4008 |     1200 |                       1 |
| Mann-Kendall-Z    |       -0.0155 |          0.4938 |     1200 |                       0 |
| QuantReg(tau=0.5) |       -0.0156 |          0.4192 |     1200 |                       1 |
| Huber             |       -0.0184 |          0.4175 |     1200 |                       1 |
| OLS               |       -0.02   |          0.4975 |     1200 |                       0 |
| Theil-Sen         |       -0.0239 |          0.4948 |     1200 |                       0 |
| Siegel-RepMedian  |       -0.0309 |          0.4957 |     1200 |                       0 |

**Menang: Kalman-drift** (IC=-0.0021, akurasi tanda=0.401 vs baseline OLS IC=-0.0200). p-value(akurasi tanda vs 50%)=1.0000 (TIDAK signifikan).


## N=24 bar

| peserta           |   IC_spearman |   sign_accuracy |   n_test |   p_value_boot_vs_50pct |
|:------------------|--------------:|----------------:|---------:|------------------------:|
| Kalman-drift      |        0.0342 |          0.4183 |     1200 |                  1      |
| Siegel-RepMedian  |        0.0021 |          0.4844 |     1200 |                  0.0045 |
| Theil-Sen         |       -0.0029 |          0.4755 |     1200 |                  0.002  |
| OLS               |       -0.0038 |          0.4743 |     1200 |                  0.0005 |
| Mann-Kendall-Z    |       -0.0099 |          0.4732 |     1200 |                  0.0015 |
| QuantReg(tau=0.5) |       -0.01   |          0.4025 |     1200 |                  1      |
| Huber             |       -0.0127 |          0.3978 |     1199 |                  1      |

**Menang: Kalman-drift** (IC=0.0342, akurasi tanda=0.418 vs baseline OLS IC=-0.0038). p-value(akurasi tanda vs 50%)=1.0000 (TIDAK signifikan).


## N=48 bar

| peserta           |   IC_spearman |   sign_accuracy |   n_test |   p_value_boot_vs_50pct |
|:------------------|--------------:|----------------:|---------:|------------------------:|
| QuantReg(tau=0.5) |        0.0344 |          0.425  |     1200 |                  1      |
| Theil-Sen         |        0.0336 |          0.499  |     1200 |                  0.0005 |
| OLS               |        0.0327 |          0.4901 |     1200 |                  0.0015 |
| Huber             |        0.032  |          0.4245 |     1199 |                  1      |
| Siegel-RepMedian  |        0.0286 |          0.4979 |     1200 |                  0.0025 |
| Mann-Kendall-Z    |        0.0277 |          0.4921 |     1200 |                  0.002  |
| Kalman-drift      |        0.0207 |          0.4233 |     1200 |                  1      |

**Menang: QuantReg(tau=0.5)** (IC=0.0344, akurasi tanda=0.425 vs baseline OLS IC=0.0327). p-value(akurasi tanda vs 50%)=1.0000 (TIDAK signifikan).
