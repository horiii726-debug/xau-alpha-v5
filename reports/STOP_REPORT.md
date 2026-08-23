# STOP REPORT -- F0, XAU ALPHA RESEARCH v6

**Status: BERHENTI di F0.** Gerbang mati GM-1 dan GM-1b sama-sama gagal. Ini bukan
kegagalan alat ukur (bandingkan §07 E langkah 0, protokol L11) -- ini konsekuensi
matematis langsung dari ukuran panel yang tersedia, dinyatakan **sebelum** run ini
dijalankan (lihat `PREREGISTRATION.md`).

## Gerbang mana yang kena, angka terukurnya berapa

| Gerbang | Ambang | Terukur | Vonis |
|---|---|---:|---|
| **GM-1** | K_eff >= 3.0 | **1.6562** | **GAGAL** |
| **GM-1b** (gabungan) | K_eff >= 4.0 **dan** T_confirm >= 11 thn | K_eff 1.6562, T_confirm 2.11 thn | **GAGAL** (dua-duanya) |

Detail perhitungan: `reports/F0_universe.md`, `reports/F0_power.md`.

- **K_eff = 1.6562** dari korelasi PnL strategi baseline XAUUSD-XAGUSD terukur
  **rho = 0.4556** (baseline: sign momentum M5 lookback 12, hold 12 bar, tanpa biaya
  -- alat ukur struktur korelasi, bukan kandidat).
- Untuk panel **K=2**, `K_eff_eigen = 2 / (1 + rho^2)` **terikat secara aljabar ke
  rentang (1, 2]** untuk *semua* nilai rho yang mungkin. **Tidak ada korelasi PnL
  yang bisa membuat panel 2-instrumen lolos GM-1 (>=3.0), apalagi GM-1b (>=4.0).**
  Ini diketahui sebelum data dilihat (dicatat di PREREGISTRATION.md) dan angka
  terukur di atas hanya mengonfirmasinya.
- **T_confirm = 2.11 tahun** dari riwayat bersama terukur XAUUSD-XAGUSD (2021-08-22
  s/d 2025-06-25 saat run ini dieksekusi, download masih berjalan sampai
  2026-08-22 -- akan diperbarui, tapi 55% dari ~5 tahun tidak akan pernah mendekati
  11 tahun berapapun sisa datanya).

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
spec §01 B4b).**
Spec v6 sendiri menyatakan panel 8-instrumen berkorelasi rendah (rho_PnL <= 0.10)
dengan riwayat >=20 tahun adalah **satu-satunya** konfigurasi yang terukur lolos
GM-3 (transmitansi corong) di dokumen sumber. Butuh: (1) verifikasi kode Dukascopy
& point-value yang benar untuk EURUSD (sudah ada di `download_candles.py`), USDJPY,
US100, US30, USOIL (LIGHTCMDUSD sudah ada), NATGAS -- **saya sengaja tidak
menebak kode/point-value instrumen yang belum terverifikasi** (melanggar §D1/D4
kalau salah skala harga, datanya jadi silently corrupt); (2) unduh riwayat
sepanjang mungkin (Dukascopy umumnya punya FX major sejak awal 2000-an, indeks
CFD & energi biasanya lebih pendek -- perlu diaudit per instrumen seperti XAU/XAG
di atas); (3) jalankan ulang `data/run_f0_v6.py` dengan panel yang diperluas.
Estimasi kerja: menit-jam untuk verifikasi kode+unduh per instrumen tambahan,
tergantung rate-limit Dukascopy (~1 req/detik, backoff otomatis -- lihat log
unduhan XAU/XAG barusan yang kadang kena 503 dan perlu cooldown).

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
