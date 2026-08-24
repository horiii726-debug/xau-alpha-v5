# L11 -- G1 (simetri) diuji ulang pada return DEMEANED

Alasan: emas naik ~11.6%/thn 2003-2026 (headwind ~4.62bps/hari untuk SEMUA short di return mentah). G1 sebelumnya berpotensi bias menolak alpha nyata. Diuji ulang: SEMUA 130 kombinasi sebelumnya, G1 dicek pada return DEMEANED (60-hari rolling mean dibuang).


**TOTAL: 5/130 lolos G1-demeaned.**


## Kombinasi yang lolos G1-demeaned

| family    | horizon   |   tau | peserta               |      n |   pnl_long_demean |   pnl_short_demean | G1_demeaned_pass   |
|:----------|:----------|------:|:----------------------|-------:|------------------:|-------------------:|:-------------------|
| H1-Lomba4 | 5d        |   1   | ShortHorizon-Reversal | 145769 |         107010    |           152593   | True               |
| H1-Lomba4 | 5d        |   1   | ORB                   |  48748 |         110782    |           111899   | True               |
| H1-Lomba4 | 5d        |   1   | CUSUM                 |   7008 |           1376.51 |            33657.3 | True               |
| H1-Lomba4 | 5d        |   1.5 | ShortHorizon-Reversal | 145683 |         107513    |           151409   | True               |
| H1-Lomba4 | 5d        |   1.5 | ORB                   |  25342 |          40768.6  |            34301.1 | True               |

## Per keluarga

| family    |   sum |   count |
|:----------|------:|--------:|
| H1-Lomba2 |     0 |      42 |
| H1-Lomba4 |     5 |      36 |
| M5-Lomba2 |     0 |      28 |
| M5-Lomba4 |     0 |      24 |

## Verdict L11

**5 lolos -- perlu diperiksa lebih lanjut sebelum lanjut L12**
