# LOMBA 5 -- SL/TP

**Entry DIKUNCI**: pemenang Lomba 4 = CUSUM, H=1d, tau=1.5 (expectancy net Lomba 4: +14.1bps, p=0.000). 6701 entri di TEST.

Barrier simetris = k * vol_estimate, **k=2.0 TETAP untuk semua peserta** -- yang berbeda HANYA metode estimasi vol. Biaya round-trip: 2.885bps (sama seperti Lomba 4). Simulasi first-passage pada M1 (bukan M5) untuk akurasi SL/TP.


| peserta                |   n_trades |   expectancy_net_bps |   premature_stop_ratio |   mae_mfe_efficiency_median |   p_value_boot |
|:-----------------------|-----------:|---------------------:|-----------------------:|----------------------------:|---------------:|
| EmpiricalQuantile(p90) |       6701 |              19.8201 |                 0.016  |                      0.126  |              0 |
| POT-GPD                |       6701 |              19.4682 |                 0.0003 |                      0.1133 |              0 |
| GARCH                  |       6701 |              11.5991 |                 0.2024 |                      0.1899 |              0 |
| Parkinson              |       6701 |               8.9726 |                 0.188  |                      0.1336 |              0 |

**Menang: EmpiricalQuantile(p90)** (expectancy net=19.820bps vs baseline/Parkinson=8.973bps). p-value bootstrap=0.0000 (signifikan).
