# F2 -- Gerbang Struktur Payoff (XAUUSD, 5 horizon, granularitas M1)

Barrier touch dicek pada bar M1 (bukan M5/M15 teragregasi) supaya tie-break SL-duluan-kalau-ambigu hanya diterapkan pada kasus yang BENAR-BENAR ambigu di level menit. Partisi SCREEN: 451,008 bar M1 (313.2 hari). n_random_entries=20000 per sisi per kombinasi per horizon.

## Kasus ambigu (SL & TP kesentuh di bar M1 yang sama) per horizon

| Horizon | Rata-rata % trade ambigu (semua kombinasi) | Maksimum % trade ambigu |
|---|---:|---:|
| H15 | 1.388% | 23.814% |
| H30 | 1.478% | 23.865% |
| H60 | 1.660% | 24.080% |
| H120 | 1.766% | 23.980% |
| H240 | 1.864% | 24.160% |

## Ringkasan per horizon

> `lolos_margin_dasar` = lolos margin/gap/net_bps saja. `lolos_semua_syarat` = shortlist itu SETELAH juga lolos sign_flip_abs_margin_tolerance_pp DAN stability_sub_periods=3.

| Horizon | Status | Bar SCREEN | Lolos margin dasar | Lolos SEMUA syarat | Long lolos? | Short lolos? | Verdict |
|---|---|---:|---:|---:|---|---|---|
| H15 | OK | 451,008 | 36 | 0 | False | False | GAGAL (nol lolos) |
| H30 | OK | 451,008 | 38 | 0 | False | False | GAGAL (nol lolos) |
| H60 | OK | 451,008 | 42 | 0 | False | False | GAGAL (nol lolos) |
| H120 | OK | 451,008 | 42 | 0 | False | False | GAGAL (nol lolos) |
| H240 | OK | 451,008 | 42 | 0 | False | False | GAGAL (nol lolos) |

## Detail kombinasi yang lolos SEMUA syarat

(TIDAK ADA kombinasi yang lolos keenam syarat sekaligus di horizon manapun)

## Vonis akhir

**NOL LOLOS DI XAUUSD, DI SEMUA 5 HORIZON YANG DIUJI (granularitas M1).**

Bukan vonis stop_conditions.1 final -- itu butuh gagal di semua instrumen juga. Panel: XAUUSD lengkap, XAGUSD sebagian (~609/1826 hari), EURUSD/USOIL kosong (download dihentikan atas instruksi user). Hasil selanjutnya (F4-F7) berjalan sebagai EKSPLORASI pada panel tidak lengkap, ditandai SINGLE_ASSET_ONLY / UNDERPOWERED_PANEL sesuai instruksi.
