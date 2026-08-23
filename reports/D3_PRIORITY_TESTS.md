# D3 -- UJI PRIORITAS (drift capture + walk-forward), CUSUM @H=1d tau=1.5

Dijalankan di LATIH+UJI (85% pertama, 383,356 bar M5). HOLDOUT (15% terakhir, 67,652 bar) **TIDAK disentuh**, disimpan untuk uji sistem utuh Bagian D.

Biaya round-trip terukur (jam aktif, dari LATIH): **2.919 bps**.

## D3.1 -- Drift capture (pisah PnL long vs short)

| arm                                 | sisi     |   n_trades |   expectancy_net_bps |   p_value |
|:------------------------------------|:---------|-----------:|---------------------:|----------:|
| RAW                                 | LONG     |      11942 |               7.8847 |    0      |
| RAW                                 | SHORT    |      11622 |              -8.3104 |    1      |
| RAW                                 | GABUNGAN |      23564 |              -0.1029 |    0.5625 |
| DEMEANED (buang mean 60hr bergulir) | LONG     |      11942 |               2.0599 |    0.0055 |
| DEMEANED (buang mean 60hr bergulir) | SHORT    |      11622 |              -2.9097 |    1      |
| DEMEANED (buang mean 60hr bergulir) | GABUNGAN |      23564 |              -0.3911 |    0.7505 |

**Verdict D3.1:** SHORT (raw) expectancy = -8.310bps (n=11622, p=1.0000). LONG (raw) = 7.885bps. SHORT (demeaned) = -2.910bps.

**GAGAL -- SHORT <= 0, ini kemungkinan besar DRIFT CAPTURE (beta emas), BUKAN alpha murni.**


## D3.3 -- Walk-forward (10 jendela berurutan, LATIH+UJI)

|   jendela |   bar_mulai |   bar_akhir |   n_trades |   expectancy_net_bps |
|----------:|------------:|------------:|-----------:|---------------------:|
|         1 |           0 |       38335 |       2513 |              -4.563  |
|         2 |       38335 |       76671 |       2157 |               1.906  |
|         3 |       76671 |      115006 |       2346 |              -0.9165 |
|         4 |      115006 |      153342 |       2420 |               1.0937 |
|         5 |      153342 |      191678 |       2866 |              -8.3749 |
|         6 |      191678 |      230013 |       2591 |              -2.8071 |
|         7 |      230013 |      268349 |       2225 |              -3.852  |
|         8 |      268349 |      306684 |       2374 |               1.8611 |
|         9 |      306684 |      345020 |       2023 |              10.8403 |
|        10 |      345020 |      383356 |       2049 |               8.7517 |

**Verdict D3.3:** 5/10 jendela positif (syarat >=7/10). **GAGAL**.


## VERDICT KESELURUHAN (gerbang sebelum lanjut Bagian A-E)

D3.1 (bukan drift capture): GAGAL  
D3.3 (walk-forward >=7/10): GAGAL  

**GAGAL SALAH SATU -- STOP, jangan lanjut ke Bagian A-E.**
