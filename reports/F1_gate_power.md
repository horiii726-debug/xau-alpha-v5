# F1 -- Uji Daya Gerbang L11 (transmitansi corong v6)

> **Sinyal divalidasi di 5.00 tahun (9395 blok H240, seluruh riwayat XAUUSD yang ada). Biaya divalidasi di 3 tahun terakhir (2024-2026).**

## Tabel kappa PER TAHUN KALENDER (XAUUSD, H240, skenario worst)

| tahun | harga rata-rata | spread p50 bps | spread p90 bps | sigma M5 bps | biaya worst bps | sigma H240 bps | **kappa H240 worst** |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 1792.9 | 1.978 | 6.237 | 4.192 | 33.60 | 29.05 | **1.157** |
| 2022 | 1802.5 | 2.159 | 6.497 | 5.136 | 35.09 | 35.59 | **0.986** |
| 2023 | 1943.4 | 1.748 | 5.239 | 4.288 | 28.37 | 29.71 | **0.955** |
| 2024 **<-rezim-sekarang** | 2389.1 | 1.638 | 3.715 | 4.692 | 20.43 | 32.50 | **0.628** |
| 2025 **<-rezim-sekarang** | 3443.1 | 1.832 | 4.596 | 6.070 | 25.24 | 42.05 | **0.600** |
| 2026 **<-rezim-sekarang** | 4572.4 | 1.627 | 5.522 | 10.495 | 30.70 | 72.71 | **0.422** |

**Biaya worst-case: seluruh riwayat (dicampur, TIDAK dipakai untuk kelayakan) = 28.22 bps vs rezim-sekarang (dipakai untuk kelayakan) = 23.84 bps.**

## Expectancy bersih berdampingan: biaya-LAMA (seluruh riwayat) vs biaya-BARU (rezim-sekarang)

| IC | gross edge (bps) | net @ biaya-LAMA (28.2bps) | net @ biaya-BARU (23.8bps) |
|---:|---:|---:|---:|
| 0.03 | 2.48 | -25.74 | -21.36 |
| 0.05 | 4.17 | -24.05 | -19.67 |
| 0.08 | 6.58 | -21.64 | -17.26 |
| 0.15 | 12.85 | -15.37 | -10.99 |
| 0.3 | 27.43 | -0.80 | 3.59 |

Sinyal sintetis ber-IC terkontrol disuntikkan ke harga **XAUUSD NYATA** (M15, blok H240 non-overlapping, n=9395 blok, rentang 5.00 tahun -- statistik). n_seeds per IC = **150** (spec: 500 -- dikurangi untuk kecepatan, lihat catatan di `src/validation/l11_gate_power.py`). Biaya worst-case rezim-sekarang (2024-2026): **23.84 bps** (bukan lagi rata-rata seluruh riwayat). BR_eff/tahun (uniqueness=1, blok non-overlap): **1880.3**.

| IC target | Tahap 1 SARINGAN | Tahap 2 ROBUSTNESS | Rantai penuh (CONFIRM) | target |
|---:|---:|---:|---:|---|
| 0.03 | 0.0% (target>=80%) | 0.0% (target>=70%) | 0.0% (target>=50%) | -- |
| 0.05 | 0.0% (target>=80%) | 0.0% (target>=70%) | 0.0% (target>=50%) | -- |
| 0.08 | 0.0% (target>=80%) | 0.0% (target>=70%) | 0.0% (target>=50%) | -- |

## Verdict GM-3 (pada IC=0.05, syarat L11 §02 HUKUM)

Screening>=80%: GAGAL (0.0%)  
Robustness>=70%: GAGAL (0.0%)  
Rantai penuh>=50%: GAGAL (0.0%)  

**GM-3: GAGAL -- BERHENTI, perbaiki desain gerbang**

## Gerbang mana yang paling mematikan? (diagnosis per-filter, IC=0.05)

Proporsi trial (dari 150 seed) yang LOLOS tiap filter INDIVIDUAL -- bukan cuma vonis gabungan per tier. Ini menjawab 'kenapa transmitansi rendah', bukan cuma 'berapa'.

### Tahap 1 SARINGAN (dari seluruh 150 seed)

| filter | % lolos |
|---|---:|
| F_EXPECT (net>0) | 0.0% <-- **PALING MEMATIKAN** |
| F_T15 (t>=1.5) | 0.0% <-- **PALING MEMATIKAN** |
| F_B02 (beat random-matched) | 95.3% |
| F_B05 (beat coin-flip) | 98.7% |
| F_BR (BR_eff>=100/thn) | 100.0% |

### Tahap 2 ROBUSTNESS (dari 0 trial yang lolos tahap 1)

N/A -- nol trial lolos tahap 1, jadi tahap 2 tidak pernah dievaluasi.


**Kesimpulan:** gerbang paling mematikan adalah **F_EXPECT (net>0)** (0.0% lolos). 
Ini KONSISTEN dengan diagnosis biaya di atas: expectancy bersih negatif karena biaya round-trip melebihi gross edge pada IC realistis -- bukan masalah signifikansi statistik (t-stat), bukan masalah frekuensi trade (BR_eff), dan bukan gagal mengalahkan null acak. **Akar masalahnya murni EKONOMI biaya vs edge, bukan kekuatan statistik gerbangnya.**


sd_SR empiris (dari sharpe 150 trial IC=0.05, efek samping L11 -- BUKAN pilot 24-trial resmi §01 B5, tapi indikasi awal): **0.3000**

## Diagnosis akar penyebab (langkah 0, §07 E: periksa alat dulu)

Gross edge rata-rata per trade (SEBELUM biaya), pada frekuensi realistis ~220 trade/tahun:

| IC target | gross edge (bps/trade) | biaya worst (bps/trade) | selisih |
|---:|---:|---:|---:|
| 0.03 | 2.70 | 23.84 | -21.14 |
| 0.05 | 4.33 | 23.84 | -19.51 |
| 0.08 | 6.88 | 23.84 | -16.96 |
| 0.15 | 13.32 | 23.84 | -10.52 |
| 0.3 | 27.96 | 23.84 | 4.12 |

**Kesimpulan diagnosis (biaya REZIM-SEKARANG 2024-2026, sudah dikoreksi -- lihat `F0_cost_regime.md`):** bahkan pada IC=0.30 (6x di atas rentang realistis 0.02-0.05 yang dinyatakan di spec §01), gross edge per trade (~28.0 bps) baru SETARA biaya worst-case rezim-sekarang (23.8 bps) -- belum lolos, apalagi net positif dengan margin. Ini **BUKAN** bug pengukuran, dan **BUKAN LAGI** artefak biaya yang dirata-ratakan lintas rezim harga berbeda (kesalahan metodologi sebelumnya sudah diperbaiki). **Temuan independen dari GM-1/GM-1b**: bahkan kalau panel diperluas sampai K_eff>=4.0, struktur biaya H240 utk XAUUSD tunggal tetap jadi kendala keras di rezim biaya sekarang.

**Keterbatasan uji L11 yang wajib diakui:** konstruksi trade di sini adalah SATU eksposur tetap sampai akhir blok (tanpa SL/TP dioptimalkan) -- divisi X (exit & sizing) belum diuji. Kandidat nyata dengan barrier yang dioptimalkan kemungkinan menangkap lebih banyak dari IC yang sama, jadi hasil 0% di sini KEMUNGKINAN pesimistis dibanding kandidat nyata -- tapi tanpa F2/F5 dijalankan, ini tidak bisa dipastikan, hanya diakui sebagai batasan uji, bukan dijadikan alasan mengabaikan hasilnya.

## Cek lanjutan: horizon H1D dan pembatasan sesi murah (§07 E langkah 1-2)

**H1D** (1565 blok): biaya round-trip TIDAK bergantung horizon (spread/slip per trade sama, 23.84 bps), yang berubah cuma volatilitas per blok (lebih besar di H1D). Gross edge:

| IC | gross edge H1D (bps) | net @ biaya-BARU |
|---:|---:|---:|
| 0.05 | 5.78 | -18.06 |
| 0.15 | 16.45 | -7.39 |
| 0.3 | 30.91 | 7.07 |

**Sesi murah** (6 jam UTC termurah dari 24, rezim 2024-2026): jam [7, 8, 16, 18, 19, 20], spread p90 = 4.029 bps (vs 4.305 bps 24-jam penuh) -> biaya worst = **23.37 bps** (vs 23.84 bps 24-jam penuh).

| IC | gross edge (bps) | net @ biaya sesi-murah |
|---:|---:|---:|
| 0.05 | 3.90 | -19.47 |
| 0.15 | 12.76 | -10.61 |
| 0.3 | 27.58 | 4.21 |

**Kesimpulan cek lanjutan:** H1D SEDIKIT MEMBAIK struktur biaya-vs-edge secara material (dan H1D tetap `PARKED` di spec, data swap belum ada). Sesi murah menurunkan biaya dari 23.84 ke 23.37 bps (penurunan tidak cukup besar), tapi bahkan di sesi termurah, IC=0.05 tetap jauh dari impas -- lihat tabel di atas. **Tidak ada horizon atau pembatasan sesi yang ditemukan cukup untuk membalik GM-3 pada IC realistis (0.03-0.08).**
