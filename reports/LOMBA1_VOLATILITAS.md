# LOMBA 1 -- VOLATILITAS

Target: realized variance window berikutnya (dari M1 log-return^2). Metrik utama QLIKE (lebih rendah lebih baik). Split 70/30 kronologis, fit hanya di train.


## Horizon 1h

| peserta                   |   QLIKE_mean |   QLIKE_median |   RMSE |   MZ_R2 |   QLIKE_vs_baseline |   p_value_boot |   n_test |
|:--------------------------|-------------:|---------------:|-------:|--------:|--------------------:|---------------:|---------:|
| HAR-RV                    |       0.353  |         0.0941 |      0 |  0.2447 |            -2258.01 |              0 |     8500 |
| MedRV                     |       0.4016 |         0.1003 |      0 |  0.1878 |            -2257.96 |              0 |     8500 |
| Bipower                   |       0.392  |         0.1006 |      0 |  0.1859 |            -2257.97 |              0 |     8500 |
| MinRV                     |       0.4293 |         0.1034 |      0 |  0.1859 |            -2257.94 |              0 |     8500 |
| EWMA(0.97)                |       0.5008 |         0.1557 |      0 |  0.1625 |            -2257.86 |              0 |     8500 |
| GARCH(1,1)-student-t      |       0.9364 |         0.1573 |      0 |  0.1855 |            -2257.43 |              0 |     8500 |
| Garman-Klass              |       0.5704 |         0.1574 |      0 |  0.2204 |            -2257.79 |              0 |     8500 |
| GARCH(1,1)-normal         |       0.9585 |         0.159  |      0 |  0.1848 |            -2257.41 |              0 |     8500 |
| Parkinson                 |       0.6484 |         0.1664 |      0 |  0.1981 |            -2257.72 |              0 |     8500 |
| EWMA(0.94)                |       0.6626 |         0.1753 |      0 |  0.1647 |            -2257.7  |              0 |     8500 |
| Rogers-Satchell           |       0.7499 |         0.1792 |      0 |  0.2132 |            -2257.62 |              0 |     8500 |
| Yang-Zhang(w20)           |       0.5929 |         0.1818 |      0 |  0.1732 |            -2257.77 |              0 |     8500 |
| BASELINE (close-to-close) |    2258.37   |         0.7894 |      0 |  0.0966 |                0    |            nan |    11276 |

> **Catatan robustness:** `QLIKE_mean` baseline meledak (2258.4) karena baseline (return kuadrat SATU periode) kadang kebetulan hampir nol -> rasio RV/pred meledak. Ini properti nyata dari estimator naive (dikonfirmasi manual, bukan bug), bukan alasan mengabaikannya -- karena itu **`QLIKE_median` dipakai untuk peringkat** (lebih robust ke ekor), `QLIKE_mean` tetap dilaporkan apa adanya untuk transparansi.


**Menang: HAR-RV** (QLIKE_median=0.0941 vs baseline 0.7894). p-value bootstrap=0.0000 (signifikan pada alpha=0.05).


## Horizon 4h

| peserta                   |   QLIKE_mean |   QLIKE_median |   RMSE |   MZ_R2 |   QLIKE_vs_baseline |   p_value_boot |   n_test |
|:--------------------------|-------------:|---------------:|-------:|--------:|--------------------:|---------------:|---------:|
| HAR-RV                    |       0.4335 |         0.128  | 0.0001 |  0.3606 |            -21359.9 |              0 |     2322 |
| Yang-Zhang(w20)           |       0.4567 |         0.1372 | 0.0001 |  0.2664 |            -21359.9 |              0 |     2322 |
| EWMA(0.94)                |       0.4834 |         0.1387 | 0.0001 |  0.2562 |            -21359.9 |              0 |     2322 |
| EWMA(0.97)                |       0.4593 |         0.1422 | 0.0001 |  0.2001 |            -21359.9 |              0 |     2322 |
| GARCH(1,1)-normal         |       0.6039 |         0.1497 | 0.0001 |  0.2903 |            -21359.7 |              0 |     2322 |
| Bipower                   |       0.6221 |         0.233  | 0.0001 |  0.3364 |            -21359.7 |              0 |     2322 |
| MedRV                     |       0.6426 |         0.2338 | 0.0001 |  0.3443 |            -21359.7 |              0 |     2322 |
| MinRV                     |       0.6587 |         0.2376 | 0.0001 |  0.3267 |            -21359.7 |              0 |     2322 |
| Garman-Klass              |       0.9873 |         0.2796 | 0.0001 |  0.2672 |            -21359.3 |              0 |     2322 |
| Parkinson                 |       1.1008 |         0.2823 | 0.0001 |  0.2851 |            -21359.2 |              0 |     2322 |
| GARCH(1,1)-student-t      |       0.7268 |         0.2876 | 0.0001 |  0.1916 |            -21359.6 |              0 |     2322 |
| Rogers-Satchell           |       1.2504 |         0.3101 | 0.0001 |  0.2162 |            -21359.1 |              0 |     2322 |
| BASELINE (close-to-close) |   21360.3    |         1.045  | 0.0001 |  0.1916 |                 0   |            nan |     2819 |

> **Catatan robustness:** `QLIKE_mean` baseline meledak (21360.3) karena baseline (return kuadrat SATU periode) kadang kebetulan hampir nol -> rasio RV/pred meledak. Ini properti nyata dari estimator naive (dikonfirmasi manual, bukan bug), bukan alasan mengabaikannya -- karena itu **`QLIKE_median` dipakai untuk peringkat** (lebih robust ke ekor), `QLIKE_mean` tetap dilaporkan apa adanya untuk transparansi.


**Menang: HAR-RV** (QLIKE_median=0.1280 vs baseline 1.0450). p-value bootstrap=0.0000 (signifikan pada alpha=0.05).


## Horizon 1d

| peserta                   |   QLIKE_mean |   QLIKE_median |   RMSE |   MZ_R2 |   QLIKE_vs_baseline |   p_value_boot |   n_test |
|:--------------------------|-------------:|---------------:|-------:|--------:|--------------------:|---------------:|---------:|
| HAR-RV                    |       0.3615 |         0.0637 | 0.0004 |  0.2667 |            -366.512 |              0 |      466 |
| GARCH(1,1)-student-t      |       0.4057 |         0.0864 | 0.0004 |  0.1595 |            -366.468 |              0 |      466 |
| Yang-Zhang(w20)           |       0.4312 |         0.0961 | 0.0004 |  0.1021 |            -366.443 |              0 |      466 |
| GARCH(1,1)-normal         |       0.4266 |         0.0979 | 0.0004 |  0.2241 |            -366.447 |              0 |      466 |
| EWMA(0.94)                |       0.4356 |         0.1025 | 0.0004 |  0.1527 |            -366.438 |              0 |      466 |
| EWMA(0.97)                |       0.4809 |         0.1234 | 0.0004 |  0.1097 |            -366.393 |              0 |      466 |
| Bipower                   |       1.5177 |         0.1239 | 0.0004 |  0.2036 |            -365.356 |              0 |      466 |
| MinRV                     |       1.6953 |         0.1269 | 0.0004 |  0.2009 |            -365.179 |              0 |      466 |
| MedRV                     |       1.6414 |         0.1273 | 0.0004 |  0.1963 |            -365.233 |              0 |      466 |
| Garman-Klass              |       1.9626 |         0.2476 | 0.0005 |  0.1882 |            -364.911 |              0 |      466 |
| Parkinson                 |       1.9451 |         0.2851 | 0.0005 |  0.1732 |            -364.929 |              0 |      466 |
| Rogers-Satchell           |       3.5329 |         0.3465 | 0.0006 |  0.1826 |            -363.341 |              0 |      466 |
| BASELINE (close-to-close) |     366.874  |         1.0229 | 0.0007 |  0.0705 |               0     |            nan |      470 |

> **Catatan robustness:** `QLIKE_mean` baseline meledak (366.9) karena baseline (return kuadrat SATU periode) kadang kebetulan hampir nol -> rasio RV/pred meledak. Ini properti nyata dari estimator naive (dikonfirmasi manual, bukan bug), bukan alasan mengabaikannya -- karena itu **`QLIKE_median` dipakai untuk peringkat** (lebih robust ke ekor), `QLIKE_mean` tetap dilaporkan apa adanya untuk transparansi.


**Menang: HAR-RV** (QLIKE_median=0.0637 vs baseline 1.0229). p-value bootstrap=0.0000 (signifikan pada alpha=0.05).
