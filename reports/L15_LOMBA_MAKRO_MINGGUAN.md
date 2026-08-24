# L15 -- MAC05 & MAC07 di horizon MINGGUAN (5 hari), gerbang G1-G5 SAMA PERSIS seperti L13

Alasan: M5 terbukti MATI (UJI_BUNUH_M5 -- winrate aktual < breakeven di semua hold & semua peserta termasuk MAC05/MAC07). COT dirilis mingguan; menguji sinyal ini di horizon sesuai frekuensi rilisnya sendiri, bukan mengubah sinyal atau melonggarkan gerbang.


D1=8,464 hari (2003-05-05 s/d 2023-02-20), LATIH+UJI dipakai=7,194. Biaya base=2.885bps, worst=13.305bps (TETAP -- dibayar sekali per trade).


sigma harian=98.716bps -> sigma 5-hari=220.736bps (naik 2.236x). kappa D1=0.0292 -> kappa W1=0.0131 (turun 2.236x).


## Hasil per kombinasi (tau x peserta)

| peserta            |   tau |    n | stopped_at   |   expectancy_worst |   pnl_long_demean |   pnl_short_demean |
|:-------------------|------:|-----:|:-------------|-------------------:|------------------:|-------------------:|
| MAC05_cot_crowding |   1   | 4189 | G2           |           -7.4675  |           nan     |             nan    |
| MAC07_ridge_combo  |   1   | 2154 | G2           |           -3.61537 |           nan     |             nan    |
| MAC05_cot_crowding |   1.5 | 2474 | G2           |          -15.4285  |           nan     |             nan    |
| MAC07_ridge_combo  |   1.5 | 1092 | G1           |          nan       |          -296.491 |            3909.19 |

## Distribusi gerbang gugur

- G2: 3
- G1: 1

## NOL SURVIVOR

Syarat L14 (>=1 lolos G1-G5) TIDAK terpenuhi. Bagian B-E tidak dikerjakan.
