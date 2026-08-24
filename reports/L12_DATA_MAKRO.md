# L12 -- Data Makro (FRED + CFTC COT)

## Ketersediaan tiap seri FRED

| seri | nama | n_valid | mulai | akhir |
|---|---|---:|---|---|
| DFII10 | real_yield_10y | 5,913 | 2003-01-02 | 2026-08-20 |
| DGS10 | nominal_10y | 16,144 | 1962-01-02 | 2026-08-20 |
| T10YIE | breakeven_10y | 5,914 | 2003-01-02 | 2026-08-21 |
| DTWEXBGS | dxy_broad | 5,169 | 2006-01-02 | 2026-08-14 |
| DEXUSEU | eurusd | 6,926 | 1999-01-04 | 2026-08-14 |
| DEXJPUS | usdjpy | 13,941 | 1971-01-04 | 2026-08-14 |
| VIXCLS | vix | 9,256 | 1990-01-02 | 2026-08-20 |
| GVZCLS | gvz_gold_vol | 4,585 | 2008-06-03 | 2026-08-20 |

## CFTC COT Gold

Tersedia: 1233 baris mingguan, 2003-01-07 s/d 2026-08-18


Semua data diselaraskan ke D1 dengan **LAG 1 HARI PENUH** saat dipakai di L13 -- file mentah di sini BELUM di-lag, itu dilakukan saat penggabungan dengan harga XAU.
