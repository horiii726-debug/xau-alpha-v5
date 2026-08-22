# F6 -- Divisi E (Entry/Arah) + Adendum Z -- RUN PARSIAL, DIHENTIKAN MANUAL

**PERINGATAN: run ini TIDAK SELESAI.** Dihentikan atas instruksi eksplisit user
sebelum semua 56 sinyal dasar selesai dievaluasi. Yang ada di bawah ini adalah
11 dari 56 sinyal dasar (E01 x4, E10 x4, E22_w96 x2, E22_w288_p1), dievaluasi
di data SKALA PENUH (451.008 bar M1, bukan smoke test) sebelum dihentikan.

## Riwayat teknis run ini (jujur, biar tidak salah baca angkanya nanti)

1. Percobaan pertama macet >10 menit tanpa progres pada E10_VARIANCE_RATIO_LM.
   Diinvestigasi: `e10_variance_ratio_lm` menghitung ulang rolling-sum di
   SELURUH array di dalam loop per-bar -- O(n^2), ~2x10^11 operasi pada skala
   penuh. Diperbaiki (hitung sekali di luar loop), diverifikasi output numerik
   identik, full test suite (103/103) tetap lolos.
2. Run kedua: refactor internal (`build_all_base_signals`) sempat membuat
   proses diam total sampai SEMUA 56 sinyal selesai dihitung baru mulai
   mencetak progres -- terlihat seperti macet padahal jalan. Diperbaiki jadi
   generator yang mencetak progres per sinyal.
3. Run ketiga (ini): jalan normal, progres terlihat live. E01 (4 varian) dan
   E10 (4 varian, sudah cepat pasca-perbaikan, ~8s/varian) selesai. E22 DFA
   mulai terasa berat (~110-240s/varian, TIDAK ada bug -- ini implementasi
   loop-per-bar Python murni yang memang berat di skala 451K bar, sudah
   di-benchmark terpisah untuk konfirmasi bukan bug). Baru selesai 3/4 varian
   E22 (window 96 p1, p2, window 288 p1) saat user minta STOP.

## 11 sinyal yang SEMPAT dievaluasi (data PENUH, checks di bawah ini masih
PARSIAL -- hanya 12 gerbang non-batch, BELUM termasuk BH-FDR/DSR/PBO karena
`apply_batch_checks` butuh SELURUH kandidat terkumpul dulu dan tidak pernah
jalan di run yang dihentikan ini)

| Kandidat | N trade | Gross bps | Net bps | t-stat | Checks parsial (dari 12) |
|---|---:|---:|---:|---:|---:|
| E01_MOMENTUM_L6 | 19721 | -0.34 | -3.34 | -67.35 | 5/12 |
| E01_MOMENTUM_L12 | 19722 | -0.37 | -3.37 | -67.92 | 5/12 |
| E01_MOMENTUM_L24 | 19678 | -0.43 | -3.43 | -69.00 | 5/12 |
| E01_MOMENTUM_L48 | 19631 | -0.29 | -3.29 | -66.10 | 5/12 |
| E10_VARIANCE_RATIO_q2 | 19709 | -0.20 | -3.20 | -63.57 | 4/12 |
| E10_VARIANCE_RATIO_q4 | 19707 | -0.19 | -3.19 | -63.19 | 4/12 |
| E10_VARIANCE_RATIO_q8 | 19702 | -0.21 | -3.21 | -63.78 | 4/12 |
| E10_VARIANCE_RATIO_q16 | 19696 | -0.20 | -3.20 | -63.45 | 4/12 |
| E22_DFA_w96_p1 | 19705 | -0.29 | -3.29 | -65.74 | 5/12 |
| E22_DFA_w96_p2 | 19705 | -0.25 | -3.25 | -64.89 | 4/12 |
| E22_DFA_w288_p1 | 19711 | -0.26 | -3.26 | -65.20 | 5/12 |

**Semua 11 gross bps NEGATIF.** Tidak ada satupun yang mendekati positif --
berbeda dari smoke-test 30K-bar sebelumnya yang sempat menunjukkan beberapa
sinyal lain (E80, E03, E02, dst -- BUKAN yang di atas) dengan gross positif
kecil. Sinyal E80/E03/E02 dkk BELUM sempat dihitung ulang di skala penuh
sebelum dihentikan -- statusnya benar-benar TIDAK DIKETAHUI di skala penuh,
bukan "gagal", bukan "belum tentu lolos". Genuinely untested at this scale.

## Yang TIDAK sempat dijalankan sama sekali di skala penuh

- 45 dari 56 sinyal dasar (E22 sisanya, E30, E60, E70, E90, E02, E03, E04,
  E11, E20, E50, E54, E64, E71, E73, E80, E81)
- SEMUA kombinasi entry x exit (filter gross-positif tidak sempat jalan)
- `apply_batch_checks` (BH-FDR, DSR, PBO) untuk kandidat manapun -- checks
  di tabel atas HANYA 12 gerbang non-batch, BUKAN 15 penuh
- Adendum Z (sudah diketahui TIDAK BISA diuji -- gap data cross-sectional
  dan gap sinyal-lolos-untuk-digerbangi, lihat sesi sebelumnya)

## Vonis F6

**TIDAK ADA VONIS.** Run dihentikan sebelum cukup data untuk menyimpulkan
apapun tentang divisi E secara keseluruhan. 11 sinyal yang sempat diuji
semuanya gross negatif, tapi itu bukan sampel yang representatif dari 56
formula -- E01 (momentum naif) dan E10/E22 (mean-reversion/persistence
statistik) secara historis memang bukan kandidat kuat di M1 XAUUSD tanpa
biaya sekalipun. Next step: lanjutkan run dari titik ini (bukan dari nol --
lihat RESUME.md).
