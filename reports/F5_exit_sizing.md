# F5 -- Divisi X (Exit, SL/TP & Sizing) -- PRIORITAS TERTINGGI

XAUUSD, entry ACAK (long+short 50/50), horizon H60, 8000 entri per kombinasi. SINGLE_ASSET_ONLY, UNDERPOWERED_PANEL. cost_bps_worst=3.0 (proksi -- markup prop firm masih LOOKUP, MC2 PENDING_COST_LOOKUP di semua kandidat). 36 kombinasi diuji (baris ledger), grid dari registry, tidak disetel di luar grid.

## Ringkasan: 36 kandidat diuji, 0 lolos >=13/15 centang tergradasi

| Kandidat | N trade | Expectancy net bps | t-stat | Checks (dari 15) | DSR | BH-FDR | PBO |
|---|---:|---:|---:|---:|---:|---|---:|
| X10_POT_GPD_u95_p0.99_ksl4.76 | 5855 | -1.81 | -13.71 | 5/15 | 0.000 | True | 1.000 |
| X21_SHIRYAEV_ROBERTS_A10 | 4000 | -2.51 | -13.66 | 5/15 | 0.000 | True | 1.000 |
| X21_SHIRYAEV_ROBERTS_A30 | 4000 | -2.56 | -12.11 | 5/15 | 0.000 | True | 1.000 |
| X22_CUSUM_h3 | 4000 | -2.59 | -12.15 | 5/15 | 0.000 | True | 1.000 |
| X32_VOL_TARGETING_tv50 | 8000 | -2.59 | -3.58 | 5/15 | 0.000 | True | 1.000 |
| X32_VOL_TARGETING_tv100 | 8000 | -2.59 | -3.58 | 5/15 | 0.000 | True | 1.000 |
| X32_VOL_TARGETING_tv150 | 8000 | -2.59 | -3.58 | 5/15 | 0.000 | True | 1.000 |
| X22_CUSUM_h5 | 4000 | -2.64 | -10.71 | 5/15 | 0.000 | True | 1.000 |
| X21_SHIRYAEV_ROBERTS_A100 | 4000 | -2.67 | -11.40 | 5/15 | 0.000 | True | 1.000 |
| X33_DRAWDOWN_CONSTRAINED_g2.0_fmax1.0 | 8000 | -2.71 | -21.65 | 5/15 | 0.000 | True | 1.000 |
| X33_DRAWDOWN_CONSTRAINED_g1.0_fmax1.0 | 8000 | -2.74 | -17.51 | 5/15 | 0.000 | True | 1.000 |
| X22_CUSUM_h8 | 4000 | -2.76 | -10.40 | 5/15 | 0.000 | True | 1.000 |
| X23_ULTIMATE_MAX_c0.2 | 4000 | -2.82 | -9.74 | 5/15 | 0.000 | True | 1.000 |
| X23_ULTIMATE_MAX_c0.35 | 4000 | -2.82 | -9.74 | 5/15 | 0.000 | True | 1.000 |
| X23_ULTIMATE_MAX_c0.5 | 4000 | -2.82 | -9.74 | 5/15 | 0.000 | True | 1.000 |
| X33_DRAWDOWN_CONSTRAINED_g2.0_fmax0.5 | 8000 | -2.86 | -45.58 | 5/15 | 0.000 | True | 1.000 |
| X06_VERTICAL_ONLY_BASELINE | 8000 | -2.86 | -11.88 | 5/15 | 0.000 | True | 1.000 |
| X10_POT_GPD_u90_p0.95_ksl2.14 | 6507 | -2.86 | -32.58 | 5/15 | 0.000 | True | 1.000 |
| X33_DRAWDOWN_CONSTRAINED_g1.0_fmax0.5 | 8000 | -2.87 | -36.67 | 5/15 | 0.000 | True | 1.000 |
| X20_SPRT_a0.05_b0.1 | 4000 | -2.97 | -55.57 | 5/15 | 0.000 | True | 1.000 |
| X20_SPRT_a0.1_b0.2 | 4000 | -2.99 | -64.70 | 5/15 | 0.000 | True | 1.000 |
| X31_FRACTIONAL_KELLY_lam0.1_f0.000 | 8000 | -3.00 | 0.00 | 4/15 | 0.000 | False | 1.000 |
| X31_FRACTIONAL_KELLY_lam0.25_f0.000 | 8000 | -3.00 | 0.00 | 4/15 | 0.000 | False | 1.000 |
| X31_FRACTIONAL_KELLY_lam0.33_f0.000 | 8000 | -3.00 | 0.00 | 4/15 | 0.000 | False | 1.000 |
| X31_FRACTIONAL_KELLY_lam0.5_f0.000 | 8000 | -3.00 | 0.00 | 4/15 | 0.000 | False | 1.000 |
| X03_TIME_DECAY_d1.0 | 3000 | -3.17 | -29.20 | 5/15 | 0.000 | True | 1.000 |
| X03_TIME_DECAY_d0.6 | 3000 | -3.18 | -28.55 | 5/15 | 0.000 | True | 1.000 |
| X03_TIME_DECAY_d0.3 | 3000 | -3.43 | -31.37 | 5/15 | 0.000 | True | 1.000 |
| X11_HILL_TAIL_kfrac0.05_ksl0.76 | 7308 | -3.61 | -80.55 | 5/15 | 0.000 | True | 1.000 |
| X11_HILL_TAIL_kfrac0.1_ksl0.88 | 7304 | -3.63 | -73.69 | 5/15 | 0.000 | True | 1.000 |
| X11_HILL_TAIL_kfrac0.15_ksl0.99 | 7301 | -3.63 | -68.75 | 5/15 | 0.000 | True | 1.000 |
| X02_ASYM_SKEW_base1.5_w0.5 | 7260 | -3.69 | -50.81 | 5/15 | 0.000 | True | 1.000 |
| X02_ASYM_SKEW_base1.5_w1.0 | 7250 | -3.71 | -51.33 | 5/15 | 0.000 | True | 1.000 |
| X01_TRIPLE_BARRIER_ksl1.5_ktp2.5 | 7202 | -3.77 | -49.24 | 5/15 | 0.000 | True | 1.000 |
| X02_ASYM_SKEW_base2.0_w1.0 | 7163 | -3.82 | -48.20 | 5/15 | 0.000 | True | 1.000 |
| X02_ASYM_SKEW_base2.0_w0.5 | 7158 | -3.86 | -47.45 | 5/15 | 0.000 | True | 1.000 |

## Vonis F5

**NOL kandidat lolos >=13/15 checks.** Dicatat apa adanya -- lanjut ke F6 (divisi independen).

Kandidat dengan expectancy tertinggi (belum lolos ambang penuh): X10_POT_GPD_u95_p0.99_ksl4.76, -1.81 bps, 5/15 checks.