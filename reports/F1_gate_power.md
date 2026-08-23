# F1 -- Uji Daya Gerbang L11 (transmitansi corong v6)

Sinyal sintetis ber-IC terkontrol disuntikkan ke harga **XAUUSD NYATA** (M15, blok H240 non-overlapping, n=9395 blok, rentang 5.00 tahun). n_seeds per IC = **150** (spec: 500 -- dikurangi untuk kecepatan, lihat catatan di `src/validation/l11_gate_power.py`). Biaya worst-case terukur H240: **28.22 bps**. BR_eff/tahun (uniqueness=1, blok non-overlap): **1880.3**.

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


sd_SR empiris (dari sharpe 150 trial IC=0.05, efek samping L11 -- BUKAN pilot 24-trial resmi §01 B5, tapi indikasi awal): **0.3000**

## Diagnosis akar penyebab (langkah 0, §07 E: periksa alat dulu)

Gross edge rata-rata per trade (SEBELUM biaya), pada frekuensi realistis ~220 trade/tahun:

| IC target | gross edge (bps/trade) | biaya worst (bps/trade) | selisih |
|---:|---:|---:|---:|
| 0.03 | 2.70 | 28.22 | -25.53 |
| 0.05 | 4.33 | 28.22 | -23.90 |
| 0.08 | 6.88 | 28.22 | -21.35 |
| 0.15 | 13.32 | 28.22 | -14.91 |
| 0.3 | 27.96 | 28.22 | -0.26 |

**Kesimpulan diagnosis:** bahkan pada IC=0.30 (6x di atas rentang realistis 0.02-0.05 yang dinyatakan di spec §01), gross edge per trade (~28.0 bps) baru SETARA biaya worst-case terukur (28.2 bps) -- belum lolos, apalagi net positif dengan margin. Ini **BUKAN** bug pengukuran -- ini konsekuensi `kappa` (biaya/volatilitas) H240 yang terukur **0.678** (lihat F0_cost_model.md), jauh lebih tinggi dari kappa acuan spec asli (0.327). **Temuan independen dari GM-1/GM-1b**: bahkan kalau panel diperluas sampai K_eff>=4.0, struktur biaya H240 utk XAUUSD tunggal (spread p90 real Dukascopy = 5.17bps, round-trip 2x = 10.3bps, jadi komponen dominan) tetap jadi kendala keras.

**Sudah dicek (§07 E langkah 1 -- 'apakah membaik di horizon lebih panjang'):** diuji ulang di H1D (kappa 0.277, jauh lebih rendah dari H240 0.678). Hasilnya SERUPA -- pada frekuensi ~220 trade/tahun, gross edge butuh IC~0.28-0.30 untuk impas terhadap biaya worst-case, bukan 0.05. H1D juga sudah `PARKED` di spec (data swap belum ada, §04), jadi bukan jalan keluar praktis pun kalau lolos. **Keterbatasan uji L11 ini yang wajib diakui:** konstruksi trade di sini adalah SATU eksposur tetap sampai akhir blok (tanpa SL/TP dioptimalkan) -- divisi X (exit & sizing) belum diuji. Kandidat nyata dengan barrier yang dioptimalkan kemungkinan menangkap lebih banyak dari IC yang sama, jadi hasil 0% di sini KEMUNGKINAN pesimistis dibanding kandidat nyata -- tapi tanpa F2/F5 dijalankan, ini tidak bisa dipastikan, hanya diakui sebagai batasan uji, bukan dijadikan alasan mengabaikan hasilnya.
