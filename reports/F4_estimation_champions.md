# F4 -- Divisi Estimasi (V, Q, T)

XAUUSD, partisi SCREEN, 451,008 bar M1. SINGLE_ASSET_ONLY -- panel belum lengkap.

## Divisi T -- BLOKIR

T01-T10 (Hawkes, ACD, dispersion index, tick-clock) semuanya butuh **timestamp kedatangan tick individual** (tick_time). Setelah beralih dari tick .bi5 ke candle M1 (demi kecepatan download -- lihat commit sebelumnya), data itu tidak ada lagi; M1 candle hanya menyimpan OHLC + volume agregat per menit, bukan waktu antar-tick. **Divisi T tidak dijalankan di F4 ini** -- bukan dilewati diam-diam, ini gap data yang nyata dan perlu diputuskan: unduh ulang tick untuk sampel kecil kalau T dianggap penting, atau terima T kosong untuk eksplorasi ini.

## Divisi V -- hasil (28 varian diuji dari 41 total di registry)

Target: QLIKE vs realized variance forward 60 menit.

| Varian | QLIKE rata-rata | Status MCS |
|---|---:|---|
| V07_BIPOWER_w96 | 0.4599 | SURVIVOR |
| V09_MINRV_w96 | 0.5820 | SURVIVOR |
| V08_MEDRV_w96 | 0.6088 | SURVIVOR |
| V13_GARCH11_BASELINE | 0.8687 | SURVIVOR |
| V07_BIPOWER_w48 | 1.5542 | SURVIVOR |
| V09_MINRV_w48 | 5.3160 | SURVIVOR |
| V08_MEDRV_w48 | 7.5066 | SURVIVOR |
| V03_ROGERS_SATCHELL_w48 | 22.7151 | tersingkir (p=0.000) |
| V03_ROGERS_SATCHELL_w96 | 23.0992 | tersingkir (p=0.000) |
| V03_ROGERS_SATCHELL_w12 | 23.1752 | tersingkir (p=0.000) |
| V02_GARMAN_KLASS_w48 | 23.9003 | tersingkir (p=0.000) |
| V02_GARMAN_KLASS_w96 | 24.3007 | tersingkir (p=0.000) |
| V02_GARMAN_KLASS_w12 | 24.3969 | tersingkir (p=0.000) |
| V04_YANG_ZHANG_w48 | 25.0062 | tersingkir (p=0.000) |
| V04_YANG_ZHANG_w96 | 25.3911 | tersingkir (p=0.000) |
| V04_YANG_ZHANG_w12 | 25.4394 | tersingkir (p=0.000) |
| V01_PARKINSON_w48 | 28.0757 | tersingkir (p=0.000) |
| V01_PARKINSON_w96 | 28.4575 | tersingkir (p=0.000) |
| V01_PARKINSON_w12 | 28.8552 | tersingkir (p=0.000) |
| V10_REALIZED_SEMIVAR_w96 | 36.8383 | tersingkir (p=0.000) |
| V10_REALIZED_SEMIVAR_w48 | 70.1027 | tersingkir (p=0.002) |
| V05_CLOSE_TO_CLOSE_w96 | 90.1251 | tersingkir (p=0.000) |
| V05_CLOSE_TO_CLOSE_w12 | 155.6538 | tersingkir (p=0.000) |
| V10_REALIZED_SEMIVAR_w12 | 159.0393 | tersingkir (p=0.026) |
| V05_CLOSE_TO_CLOSE_w48 | 342.6068 | tersingkir (p=0.000) |
| V12_EWMA_l0.97 | 565.4520 | tersingkir (p=0.000) |
| V12_EWMA_l0.94 | 4318.0984 | tersingkir (p=0.000) |
| V12_EWMA_l0.99 | 153318.0420 | tersingkir (p=0.000) |

**MCS survivors (alpha=0.10):** ['V07_BIPOWER_w48', 'V08_MEDRV_w48', 'V09_MINRV_w48', 'V07_BIPOWER_w96', 'V08_MEDRV_w96', 'V09_MINRV_w96', 'V13_GARCH11_BASELINE']

**Juara (tie-break tersederhana):** V07_BIPOWER_w48

## Divisi Q -- hasil (7 varian diuji dari 35 total di registry)

Target: MAE terhadap spread realized (ask_close-bid_close) bar M1 -- BUKAN tick individual (data tick sudah tidak ada, lihat gap Divisi T di atas).

| Varian | MAE (bps) | Status MCS |
|---|---:|---|
| Q02_CORWIN_SCHULTZ_w48 | 0.3305 | SURVIVOR |
| Q02_CORWIN_SCHULTZ_w96 | 0.3679 | tersingkir (p=0.002) |
| Q01_ROLL_w48 | 2.0366 | tersingkir (p=0.000) |
| Q01_ROLL_w96 | 2.0800 | tersingkir (p=0.000) |
| Q01_ROLL_w288 | 2.1878 | tersingkir (p=0.000) |
| Q03_ABDI_RANALDO_w48 | 2.5977 | tersingkir (p=0.000) |
| Q03_ABDI_RANALDO_w96 | 2.6129 | tersingkir (p=0.000) |

**MCS survivors (alpha=0.10):** ['Q02_CORWIN_SCHULTZ_w48']

**Juara (tie-break tersederhana):** Q02_CORWIN_SCHULTZ_w48

## Catatan cakupan (jujur)

V: 28/41 varian diuji (V06, V11, V14 dilewati -- V11 HAR-RV & V14 realized kernel butuh refit/loop per-bar yang terlalu mahal untuk dijalankan penuh di eksplorasi ini; V06 realized range perlu data sub-interval yang tidak dimiliki dari M1 tunggal). Q: 7/35 varian diuji (Q04-Q12 dilewati -- butuh n_ticks per bar atau tick_size yang belum dikalibrasi, atau bergantung pada estimator V/lainnya yang belum final). T: 0/27, blokir data (lihat atas). Ini SINGLE_ASSET_ONLY, hasil eksplorasi bukan bukti.