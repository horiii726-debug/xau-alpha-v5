# V7.1 LANGKAH 1 -- Autopsi arm DEMEANED long-only (CUSUM @H=1d tau=1.5)

Arm demeaned LONG-only, 11942 trade, dijalankan di LATIH+UJI (85% pertama, 383,356 bar M5). Biaya BASE (Uji 1-3, sama seperti D3 sebelumnya): **2.919bps**. Biaya WORST (khusus Uji 4): spread_p90(jam aktif)=2.305bps + komisi=0.280bps + slippage(alpha=1.5)=3.457bps = **6.042bps**.

## Uji 1 -- Signifikansi dengan eff_N

n mentah=11942, **eff_N=991.5** (rasio keunikan=0.0830 -- holding 1 hari tumpang tindih banyak, N efektif jauh lebih kecil dari N mentah). mean net=2.060bps, **t-stat(eff_N)=0.722**, p=0.4707.

**GAGAL** (syarat t>=3.0).


## Uji 2 -- Walk-forward (demeaned long-only)

|   jendela |   n_trades |   expectancy_net_bps |
|----------:|-----------:|---------------------:|
|         1 |       1217 |              -6.2878 |
|         2 |       1105 |              -9.0064 |
|         3 |       1151 |               7.5183 |
|         4 |       1352 |              -7.6994 |
|         5 |       1418 |             -12.9024 |
|         6 |       1413 |               3.3609 |
|         7 |       1163 |              -1.7461 |
|         8 |       1174 |              -2.6564 |
|         9 |        990 |              28.7055 |
|        10 |        959 |              35.7008 |

4/10 jendela positif. Kontribusi 2 jendela PnL terbesar terhadap total: **254.7%** (syarat <=60%).

**GAGAL** (syarat >=7/10 DAN tidak terkonsentrasi >60% di 2 jendela).


## Uji 3 -- Permutasi blok (1000x, block_size=72 bar)

Observed total return (bps-equivalent sum)=59456.1, berada di **persentil 95.6** dari distribusi null (permutasi blok).

**LOLOS** (syarat >=persentil 95).


## Uji 4 -- Biaya worst-case

Expectancy net @ biaya worst (6.042bps) = **-1.064bps**.

**GAGAL** (syarat >0).


## VERDICT L1

Uji 1 (t-stat eff_N>=3.0): GAGAL  
Uji 2 (walk-forward >=7/10, tak terkonsentrasi): GAGAL  
Uji 3 (permutasi blok >=persentil 95): LOLOS  
Uji 4 (expectancy>0 @ biaya worst): GAGAL  

**1/4 lolos.** **GAGAL -- arm demeaned juga mati sebagai sinyal. 3 dari 4 uji gagal.**
