# STOP REPORT -- F0 & F1, XAU ALPHA RESEARCH v6

> **UPDATE setelah F1 dijalankan:** F1 (uji L11, transmitansi corong) GAGAL secara
> **independen** dari masalah panel F0 di bawah. Lihat "Temuan F1" di bagian bawah
> dokumen ini -- ini bukan cuma soal K_eff, ada kendala biaya/horizon terpisah yang
> juga harus diatasi.

**Status: BERHENTI di F0.** Gerbang mati GM-1 dan GM-1b sama-sama gagal. Ini bukan
kegagalan alat ukur (bandingkan §07 E langkah 0, protokol L11) -- ini konsekuensi
matematis langsung dari ukuran panel yang tersedia, dinyatakan **sebelum** run ini
dijalankan (lihat `PREREGISTRATION.md`).

## Gerbang mana yang kena, angka terukurnya berapa

| Gerbang | Ambang | Terukur | Vonis |
|---|---|---:|---|
| **GM-1** | K_eff >= 3.0 | **1.6281** | **GAGAL** |
| **GM-1b** (gabungan) | K_eff >= 4.0 **dan** T_confirm >= 11 thn | K_eff 1.6281, T_confirm 2.75 thn | **GAGAL** (dua-duanya) |
| **GM-3** (F1, L11) | transmitansi rantai penuh @IC0.05 >= 50% | **0.0%** | **GAGAL** (independen dari GM-1) |

Angka di atas FINAL (data XAUUSD & XAGUSD 100% lengkap 2021-08-22 s/d 2026-08-22,
1827/1827 hari, nol gap, nol duplikat).

Detail perhitungan: `reports/F0_universe.md`, `reports/F0_power.md`.

- **K_eff = 1.6562** dari korelasi PnL strategi baseline XAUUSD-XAGUSD terukur
  **rho = 0.4556** (baseline: sign momentum M5 lookback 12, hold 12 bar, tanpa biaya
  -- alat ukur struktur korelasi, bukan kandidat).
- Untuk panel **K=2**, `K_eff_eigen = 2 / (1 + rho^2)` **terikat secara aljabar ke
  rentang (1, 2]** untuk *semua* nilai rho yang mungkin. **Tidak ada korelasi PnL
  yang bisa membuat panel 2-instrumen lolos GM-1 (>=3.0), apalagi GM-1b (>=4.0).**
  Ini diketahui sebelum data dilihat (dicatat di PREREGISTRATION.md) dan angka
  terukur di atas hanya mengonfirmasinya.
- **T_confirm = 2.75 tahun** dari riwayat bersama FINAL XAUUSD-XAGUSD (2021-08-22
  s/d 2026-08-22, data 100% lengkap). 55% dari 5 tahun tidak akan pernah mendekati
  11 tahun -- ini bukan lagi angka sementara.

## Temuan F1 -- GM-3 gagal, INDEPEN dari masalah panel

F1 (uji L11 -- transmitansi corong) dijalankan pada XAUUSD sendiri (tidak butuh
panel lengkap, sesuai instruksi). Sinyal sintetis ber-IC terkontrol (0.03/0.05/0.08,
150 seed per IC) disuntikkan ke harga XAUUSD nyata, horizon H240, dijalankan lewat
corong 3-tingkat v6. **Transmitansi 0.0% di SEMUA tahap, semua IC.**

**Akar penyebab (bukan bug pengukuran, sudah didiagnosis penuh di
`F0_cost_model.md` & `F1_gate_power.md`):** biaya round-trip worst-case XAUUSD
terukur nyata (28.22 bps, dari spread p90 Dukascopy asli) jauh lebih besar
daripada gross edge yang bisa ditangkap sinyal ber-IC realistis pada frekuensi
~220 trade/tahun -- bahkan pada IC=0.30 (6x di atas rentang realistis 0.02-0.05),
gross edge (~28 bps) baru IMPAS, belum lolos gerbang manapun. Sudah dicek di H1D
juga (kappa lebih rendah, 0.277) -- hasil serupa, dan H1D sendiri `PARKED` karena
data swap belum ada.

**Kappa H240 terukur (0.678) hampir 2x kappa acuan di dokumen spec asli (0.327)**
-- kemungkinan karena spread p90 Dukascopy real yang saya ukur lebih lebar
daripada asumsi perencanaan di dokumen sumber.

**Catatan kejujuran soal keterbatasan uji ini:** L11 di sini memakai eksposur
horizon-tetap tanpa SL/TP dioptimalkan (divisi X belum diuji). Kandidat nyata
dengan barrier optimal mungkin menangkap lebih banyak dari IC yang sama -- jadi
0% di sini kemungkinan pesimistis dibanding kandidat nyata, tapi tidak bisa
dipastikan tanpa F2/F5 dijalankan.

**Implikasi:** memperluas panel (mengatasi GM-1/GM-1b) TIDAK otomatis mengatasi
GM-3 -- ini kendala kedua yang independen, kemungkinan butuh horizon berbeda,
sesi berbiaya-rendah, atau exit yang dioptimalkan (bukan cuma panel lebih besar).

## Kenapa langkah-langkah lain di F0 (sd_SR pilot, skew/kurt, GM-2/4/5) dilewati

Begitu GM-1 gagal secara matematis pasti, menjalankan pilot 24-trial untuk mengukur
`sd_SR` (dan menurunkan `N_maks`/anggaran kandidat darinya) berarti menghitung
anggaran untuk registri yang **sudah pasti gagal DSR** sebelum satu kandidat pun
diuji. §08 D3 dan pelajaran #8 (`10_FASE_EKSEKUSI.md`) menyebut pola ini persis
sebagai penyebab v1-v5 gagal lima kali: *"menjalankan registri lebih besar dari
N_maks dan berharap."* Melewatinya di sini adalah keputusan sadar (ditandai
`TIDAK_DIJALANKAN_KARENA_GM1_GAGAL`), bukan kelalaian.

## Yang SUDAH dihitung dan tetap berguna

Data audit, model biaya (dengan koreksi beta v6: `sigma_latensi` bukan `sigma_bar`),
spread real per instrumen, dan kappa per horizon di `F0_data_audit.md` /
`F0_cost_model.md` **tidak bergantung pada ukuran panel** -- semuanya tetap valid
dan jadi fondasi kalau panel diperluas.

## 3 opsi konkret untuk melewati gerbang ini

**Opsi A -- Perluas panel ke K>=4-5 instrumen berkorelasi rendah (disarankan per
spec §01 B4b). SEDANG BERJALAN.**
`scripts/download_dukascopy.py` sudah dijalankan (nohup, resumable): 5/8 instrumen
ter-verifikasi lewat probe harga nyata (XAUUSD, XAGUSD, EURUSD, USOIL, **USDJPY**)
-- US100/US30/NATGAS **UNRESOLVED** (kode Dukascopy yang dicoba semua 404, sengaja
tidak ditebak lebih jauh). Tanggal mulai NYATA yang ditemukan lewat binary search:
**XAUUSD 1999-09-01, XAGUSD 1999-01-01, EURUSD & USDJPY 2003-05-04, USOIL
2011-09-23** -- jauh lebih awal dari dugaan "2003" di dokumen spec.
**Realitas waktu: unduhan 27 tahun x 5 instrumen pada rate-limit Dukascopy
(~0.2-0.4 hari-data/detik, dengan backoff 503 berkala) akan makan ~1-2 hari,
bukan menit-jam** -- estimasi di paragraf ini sebelumnya salah, dikoreksi di sini.
Berjalan di background, F0 akan di-rerun otomatis setelah selesai. **Tapi ingat
temuan F1 di atas: memperluas panel TIDAK otomatis mengatasi GM-3.**

**Opsi B -- Terima bahwa panel XAU-XAG (K=2) tidak bisa menjalankan protokol v6
seperti dirancang, dan alihkan ke strategi berbeda: pair-trading/spread-trading
XAU-XAG.**
K_eff dan syarat gabungan v6 dirancang untuk portofolio arah multi-instrumen
independen -- bukan relevan untuk strategi relative-value 2 aset (mis. rasio
XAU/XAG, cointegration, OU spread). Itu proyek riset yang BERBEDA dengan gerbang
statistik yang berbeda pula (bukan K_eff/DSR portofolio, tapi uji stasioneritas
spread, half-life OU, dst.) -- di luar cakupan dokumen v6 yang ada. Perlu
spesifikasi baru kalau ini arah yang diminta.

**Opsi C -- Terima hasil apa adanya: laporkan nol, hentikan riset arah multi-
instrumen sampai data lebih tersedia.**
Sesuai §07 Bagian E langkah 7 (*"Terima kalau memang nol. Laporkan tanpa
dilunakkan."*): dengan data yang ada sekarang, protokol v6 tidak bisa dijalankan
melewati F0 secara jujur. Menjalankan F1-F11 dengan panel K=2 berarti menjalankan
registri yang gerbangnya sendiri sudah menyatakan mustahil lolos -- persis pola
yang menyebabkan nol lima kali berturut-turut di v1-v5.

## Rekomendasi

**Opsi A** adalah yang paling konsisten dengan tujuan asli (multi-strategi arah,
panel besar) DAN dengan instruksi kecepatan user -- tapi butuh instrumen tambahan
dengan kode/skala yang terverifikasi benar, yang belum tersedia di codebase ini.
Ini keputusan yang butuh input user (instrumen mana, sumber verifikasi kode
Dukascopy) -- bukan sesuatu yang aman ditebak.
