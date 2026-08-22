# F6 -- Divisi E (Entry/Arah) + Adendum Z

> ⚠️ **BELUM SELESAI -- INI HASIL SMOKE TEST, BUKAN RUN PENUH.** Dijalankan
> pada 50.000 bar M1 pertama saja (~11% dari partisi SCREEN penuh, ~451.008
> bar), murni untuk mengecek skrip tidak crash sebelum run sesungguhnya. Run
> penuh sempat dilaunch tapi DIHENTIKAN (pkill) sebelum selesai atas
> instruksi user ("STOP semua proses yang jalan"), sebelum sempat menulis
> laporan akhir yang sebenarnya. Angka di bawah TIDAK mewakili hasil final
> F6 -- jangan dipakai sebagai vonis, hanya arah kasar. Perintah untuk
> melanjutkan: `python data/run_f6_division_e.py` (~10 menit, lihat
> RESUME.md).

XAUUSD, exit baseline X01 (k_sl=1.5,k_tp=2.5, H60 -- F5 tidak menemukan exit lebih baik). Entry di SETIAP bar sinyal formula != 0 (bukan acak), eksekusi t+1 (L9). SINGLE_ASSET_ONLY, UNDERPOWERED_PANEL. 55 kombinasi diuji dari registry 19 formula (7 pilot + 12 tambahan) -- BUKAN 56 penuh, lihat catatan cakupan. **Skala data: 50.000/451.008 bar (~11%) -- SMOKE TEST.**

## Adendum Z -- TIDAK BISA diuji

Z02/Z03 (cross-sectional) butuh >1 instrumen -- panel cuma XAUUSD. Z01 butuh sinyal E yang SUDAH lolos F6 sebagai input untuk digerbangi -- kalau nol E yang lolos (lihat di bawah), Z01 tidak punya apapun untuk digerbangi. Dilaporkan sebagai gap nyata, bukan dilewati diam-diam.

## Ringkasan: 55 kandidat diuji, 0 lolos >=13/15 centang

| Kandidat | N trade | Expectancy net bps | t-stat | Checks (dari 15) | DSR | BH-FDR | PBO |
|---|---:|---:|---:|---:|---:|---|---:|
| E80_QUANTREG_tau0.25 | 7033 | -1.46 | -7.63 | 5/15 | 0.000 | True | 0.964 |
| E80_QUANTREG_tau0.5 | 7033 | -1.46 | -7.63 | 5/15 | 0.000 | True | 0.964 |
| E80_QUANTREG_tau0.75 | 7033 | -1.46 | -7.63 | 5/15 | 0.000 | True | 0.964 |
| E03_REVERSAL_L6_t2.0 | 73 | -2.15 | -2.36 | 5/15 | 0.000 | True | 0.964 |
| E03_REVERSAL_L6_t1.5 | 207 | -2.49 | -4.40 | 5/15 | 0.000 | True | 0.964 |
| E03_REVERSAL_L12_t2.0 | 74 | -2.67 | -2.87 | 5/15 | 0.000 | True | 0.964 |
| E02_VOLSCALED_MOM_L6_t1.0 | 574 | -2.80 | -7.52 | 6/15 | 0.000 | True | 0.964 |
| E01_MOMENTUM_L48 | 6909 | -2.85 | -16.75 | 6/15 | 0.000 | True | 0.964 |
| E81_HUBER_SLOPE | 6976 | -2.90 | -17.10 | 5/15 | 0.000 | True | 0.964 |
| E02_VOLSCALED_MOM_L24_t1.0 | 581 | -2.92 | -5.94 | 6/15 | 0.000 | True | 0.964 |
| E71_COX_STUART_w48 | 6730 | -2.93 | -17.34 | 5/15 | 0.000 | True | 0.964 |
| E01_MOMENTUM_L24 | 6802 | -2.94 | -16.95 | 6/15 | 0.000 | True | 0.964 |
| E70_MANN_KENDALL_w48 | 6908 | -2.97 | -17.61 | 5/15 | 0.000 | True | 0.964 |
| E70_MANN_KENDALL_w96 | 6996 | -3.02 | -18.91 | 5/15 | 0.000 | True | 0.964 |
| E50_FFT_PERIOD_w96 | 7091 | -3.04 | -17.98 | 5/15 | 0.000 | True | 0.964 |
| E71_COX_STUART_w96 | 6925 | -3.04 | -18.93 | 5/15 | 0.000 | True | 0.964 |
| E64_REALIZED_SKEW_w288 | 7140 | -3.05 | -19.16 | 5/15 | 0.000 | True | 0.964 |
| E70_MANN_KENDALL_w24 | 6796 | -3.06 | -17.97 | 5/15 | 0.000 | True | 0.964 |
| E02_VOLSCALED_MOM_L12_t0.5 | 2195 | -3.06 | -13.74 | 6/15 | 0.000 | True | 0.964 |
| E60_DRIFT_BURST_hm12_hv48 | 6745 | -3.07 | -17.42 | 6/15 | 0.000 | True | 0.964 |
| E01_MOMENTUM_L12 | 6746 | -3.07 | -17.43 | 6/15 | 0.000 | True | 0.964 |
| E02_VOLSCALED_MOM_L24_t0.5 | 2173 | -3.08 | -12.79 | 6/15 | 0.000 | True | 0.964 |
| E03_REVERSAL_L12_t1.5 | 185 | -3.10 | -5.00 | 5/15 | 0.000 | True | 0.964 |
| E30_ENTROPY_w288 | 129 | -3.10 | -1.78 | 5/15 | 0.000 | False | 0.964 |
| E73_RUNS_TEST_w48 | 6579 | -3.11 | -17.89 | 5/15 | 0.000 | True | 0.964 |
| E71_COX_STUART_w24 | 6406 | -3.15 | -18.61 | 5/15 | 0.000 | True | 0.964 |
| E03_REVERSAL_L3_t1.5 | 214 | -3.15 | -6.29 | 5/15 | 0.000 | True | 0.964 |
| E02_VOLSCALED_MOM_L6_t0.5 | 2206 | -3.16 | -15.31 | 6/15 | 0.000 | True | 0.964 |
| E02_VOLSCALED_MOM_L12_t1.0 | 580 | -3.16 | -7.80 | 6/15 | 0.000 | True | 0.964 |
| E50_FFT_PERIOD_w288 | 7195 | -3.16 | -19.25 | 5/15 | 0.000 | True | 0.964 |
| E20_HURST_w576 | 6695 | -3.17 | -18.27 | 5/15 | 0.000 | True | 0.964 |
| E60_DRIFT_BURST_hm6_hv24 | 6705 | -3.18 | -17.91 | 6/15 | 0.000 | True | 0.964 |
| E01_MOMENTUM_L6 | 6706 | -3.18 | -17.92 | 6/15 | 0.000 | True | 0.964 |
| E73_RUNS_TEST_w24 | 6492 | -3.19 | -18.40 | 5/15 | 0.000 | True | 0.964 |
| E64_REALIZED_SKEW_w96 | 7022 | -3.22 | -19.77 | 5/15 | 0.000 | True | 0.964 |
| E20_HURST_w288 | 6695 | -3.24 | -18.79 | 5/15 | 0.000 | True | 0.964 |
| E64_REALIZED_SKEW_w48 | 6936 | -3.25 | -19.96 | 5/15 | 0.000 | True | 0.964 |
| E11_VR_WRIGHT_q2 | 6701 | -3.25 | -19.03 | 5/15 | 0.000 | True | 0.964 |
| E22_DFA_w288_p2 | 6690 | -3.25 | -19.02 | 5/15 | 0.000 | True | 0.964 |
| E73_RUNS_TEST_w96 | 6660 | -3.26 | -18.99 | 5/15 | 0.000 | True | 0.964 |
| E22_DFA_w288_p1 | 6698 | -3.26 | -19.07 | 5/15 | 0.000 | True | 0.964 |
| E10_VARIANCE_RATIO_q8 | 6632 | -3.30 | -19.05 | 5/15 | 0.000 | True | 0.964 |
| E10_VARIANCE_RATIO_q16 | 6632 | -3.31 | -19.30 | 5/15 | 0.000 | True | 0.964 |
| E10_VARIANCE_RATIO_q4 | 6634 | -3.32 | -19.15 | 5/15 | 0.000 | True | 0.964 |
| E22_DFA_w96_p2 | 6702 | -3.33 | -19.52 | 6/15 | 0.000 | True | 0.964 |
| E11_VR_WRIGHT_q4 | 6697 | -3.34 | -19.74 | 5/15 | 0.000 | True | 0.964 |
| E22_DFA_w96_p1 | 6696 | -3.35 | -19.79 | 5/15 | 0.000 | True | 0.964 |
| E10_VARIANCE_RATIO_q2 | 6640 | -3.37 | -19.50 | 5/15 | 0.000 | True | 0.964 |
| E11_VR_WRIGHT_q8 | 6696 | -3.37 | -20.09 | 5/15 | 0.000 | True | 0.964 |
| E90_CUSUM_k0.5_h4.0 | 98 | -3.86 | -6.61 | 6/15 | 0.000 | True | 0.964 |
| E03_REVERSAL_L3_t2.0 | 74 | -3.89 | -4.90 | 5/15 | 0.000 | True | 0.964 |
| E30_ENTROPY_w48 | 63 | -5.08 | -2.96 | 6/15 | 0.000 | True | 0.964 |
| E30_ENTROPY_w96 | 116 | -5.26 | -3.64 | 6/15 | 0.000 | True | 0.964 |
| E04_GAP_CONT_t1.0 | 266 | -7.06 | -95.33 | 5/15 | 0.000 | True | 0.964 |
| E04_GAP_CONT_t0.5 | 4213 | -8.65 | -140.42 | 6/15 | 0.000 | True | 0.964 |

## Vonis F6

**NOL kandidat lolos >=13/15 checks.** Dicatat apa adanya -- lanjut ke F7 (divisi independen).

Kandidat dengan expectancy tertinggi (belum lolos ambang penuh): E80_QUANTREG_tau0.25, -1.46 bps, 5/15 checks.

## Catatan cakupan (jujur)

19/56 formula E diuji (34 varian), plus Adendum Z 0/3 (gap data, lihat atas). Formula yang TIDAK diuji: E05-E09 (tidak ada di registry asli -- penomoran memang meloncat), E12, E21, E23-E29, E31-E36, E40-E45 (nonlinear/chaos, tier-3 mahal), E51-E53/E55, E61-E63/E65, E72/E74/E82/E83 (butuh implementasi Theil-Sen/Siegel/RANSAC robust slope tambahan), E91-E97 (changepoint/dependency lanjutan, sebagian tier-3). Ini eksplorasi breadth-first pada anggaran waktu terbatas, BUKAN klaim registry penuh teruji.