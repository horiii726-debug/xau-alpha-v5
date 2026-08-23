# F0 -- Model Biaya (v6, koreksi beta: sigma_bar -> sigma_latensi)

Komisi metals TERVERIFIKASI dari halaman resmi (03_DATA_DAN_BIAYA.md §B1): FTMO 0.140 bps/sisi, FundedNext 0.160 bps/sisi (per-sisi -- ambigu resmi, dipakai asumsi konservatif). Markup spread prop firm & swap: **TIDAK_KETEMU** (sama seperti dokumen v6 asli) -- tidak dimasukkan ke total, ditandai.


## XAUUSD

- Spread terukur (M5, dari tick bid/ask real): p50=1.814 bps, p75=2.371 bps, p90=5.166 bps, p99=11.352 bps
- sigma M5 empiris: 6.005 bps/bar -> proxy sigma M1 (skala akar-waktu): 2.685 bps
- proxy sigma_latensi (skala akar-waktu dari M1, BUKAN tick langsung): 1s=0.347bps, 3s=0.600bps, 10s=1.096bps

| skenario | spread bps | slip bps (v6, sigma_latensi) | komisi RT bps | **total RT bps** |
|---|---:|---:|---:|---:|
| best | 1.814 | 0.907 | 0.280 | **4.815** |
| base | 2.371 | 2.521 | 0.280 | **7.543** |
| worst | 5.166 | 8.297 | 0.280 | **28.223** |

**Kappa (biaya_worst_bps / volatilitas_horizon_bps), horizon via penskalaan akar-waktu dari sigma M5 terukur:**

| horizon | menit | sigma horizon (bps) | kappa @worst |
|---|---:|---:|---:|
| H15 | 15 | 10.40 | 2.714 |
| H60 | 60 | 20.80 | 1.357 |
| H120 | 120 | 29.42 | 0.959 |
| H240 | 240 | 41.60 | 0.678 |
| H1D | 1440 | 101.90 | 0.277 |

**Catatan:** kappa di atas memakai penskalaan akar-waktu dari sigma bar (proxy perencanaan), BUKAN durasi hit-barrier NYATA (§03 C4) -- itu butuh triple-barrier labeling penuh yang belum dijalankan (F0 tidak menjalankan kandidat). Ditandai `KAPPA_PLANNING_PROXY`, wajib dihitung ulang dari durasi barrier real sebelum F2b.

## XAGUSD

- Spread terukur (M5, dari tick bid/ask real): p50=12.498 bps, p75=13.784 bps, p90=18.603 bps, p99=60.390 bps
- sigma M5 empiris: 12.635 bps/bar -> proxy sigma M1 (skala akar-waktu): 5.650 bps
- proxy sigma_latensi (skala akar-waktu dari M1, BUKAN tick langsung): 1s=0.729bps, 3s=1.263bps, 10s=2.307bps

| skenario | spread bps | slip bps (v6, sigma_latensi) | komisi RT bps | **total RT bps** |
|---|---:|---:|---:|---:|
| best | 12.498 | 6.249 | 0.320 | **31.566** |
| base | 13.784 | 14.100 | 0.320 | **41.989** |
| worst | 18.603 | 29.058 | 0.320 | **99.715** |

**Kappa (biaya_worst_bps / volatilitas_horizon_bps), horizon via penskalaan akar-waktu dari sigma M5 terukur:**

| horizon | menit | sigma horizon (bps) | kappa @worst |
|---|---:|---:|---:|
| H15 | 15 | 21.88 | 4.557 |
| H60 | 60 | 43.77 | 2.278 |
| H120 | 120 | 61.90 | 1.611 |
| H240 | 240 | 87.54 | 1.139 |
| H1D | 1440 | 214.42 | 0.465 |

**Catatan:** kappa di atas memakai penskalaan akar-waktu dari sigma bar (proxy perencanaan), BUKAN durasi hit-barrier NYATA (§03 C4) -- itu butuh triple-barrier labeling penuh yang belum dijalankan (F0 tidak menjalankan kandidat). Ditandai `KAPPA_PLANNING_PROXY`, wajib dihitung ulang dari durasi barrier real sebelum F2b.

## Status verifikasi biaya

`cost_verified: false` -- sama seperti spec asli, baru jadi true setelah F12 forward test (>=200 fill nyata). Markup spread prop firm & swap XAUUSD/XAGUSD: **TIDAK_KETEMU**, tidak dimasukkan ke total di atas (akan menaikkan biaya lebih lanjut).