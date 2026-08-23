# PREREGISTRATION — XAU ALPHA RESEARCH v6

**Locked:** 2026-08-23 (sebelum F0 dijalankan)
**Sumber spesifikasi:** `XAU_ALPHA_V6/` (paket lengkap CLAUDE.md, 00–10, semua DIVISI_*, `_verifikasi/`)

## Keputusan OVERRIDE V6 — disetujui user secara tertulis

| # | Keputusan | Status |
|---|---|---|
| 1 | Corong bertingkat (§07) menggantikan 17-gerbang-sekaligus-di-screening | **SETUJU** |
| 2 | F2 jadi PENGUKURAN, bukan STOP TOTAL (§05 C) | **SETUJU** |
| 3 | Koreksi satuan `beta` slippage: `sigma_bar` → `sigma_latensi` (§03 C2) | **SETUJU** |
| 4 | Ledger dipisah arah vs estimasi (§O10) | **SETUJU** |
| 5 | `sd_SR` diukur di F0 sebelum anggaran dikunci (§01 B5) | **SETUJU** |
| 6 | Syarat kelayakan gabungan `K_eff >= 4.0` DAN `T_confirm >= 11 thn` (§01 B4b) | **SETUJU** |

## Deviasi eksplisit dari spesifikasi — dinyatakan SEBELUM F0 dijalankan

Instruksi user secara eksplisit **menolak** menunggu pengumpulan riwayat 20 tahun /
panel 8 instrumen penuh sebelum mulai: *"JANGAN 11 TAHUN GA UDAH CUKUP DATA APA
ADANYA AJA. LANGSUNG KERJAKAN DENGAN DATA 5 TAHUN ITU SEMUA."*

Konsekuensi yang dicatat di sini secara eksplisit, SEBELUM angka apapun dilihat
(§O1 pre-registration):

- **Panel yang benar-benar punya data terverifikasi: K=2** (XAUUSD, XAGUSD; sumber
  Dukascopy M1 bid/ask candle, 2021-08-22 s/d berjalan). 6 instrumen panel v6 lainnya
  (EURUSD, USDJPY, US100, US30, USOIL, NATGAS) **TIDAK diunduh** — baik karena tidak
  diminta eksplisit, maupun karena kode Dukascopy & point-value untuk USDJPY/US100/
  US30/NATGAS tidak tersedia terverifikasi di codebase yang ada (hanya XAUUSD, XAGUSD,
  EURUSD, LIGHTCMDUSD/USOIL yang punya definisi point-value teruji).
- **Riwayat: ~5 tahun (2021-08 s/d sekarang), bukan target 2003+.**
- Konsekuensi matematis yang **sudah bisa dinyatakan sebelum menjalankan apapun**:
  dengan K=2, `K_eff` (metode eigenvalue) **terikat secara matematis ke rentang
  (1, 2]** — TIDAK MUNGKIN mencapai `K_eff >= 3.0` (GM-1), apalagi `>= 4.0` (GM-1b),
  berapapun korelasi PnL-nya. Ini bukan hasil ukur — ini konsekuensi aljabar dari
  `K_eff = (sum lambda)^2 / sum(lambda^2)` pada matriks korelasi 2x2, yang dicatat
  di sini SEBELUM data dijalankan supaya tidak disalahartikan sebagai "temuan".
- Dengan T~5 tahun, partisi CONFIRM (55%) memberi `T_confirm ~= 2.75 tahun`, jauh di
  bawah syarat `>= 11 tahun` (GM-1b).

**Kesimpulan yang dicatat sebelum F0 dijalankan:** run ini **hampir pasti berhenti di
GM-1/GM-1b di F0**, secara struktural, bukan karena bug atau nasib buruk. Dijalankan
tetap atas instruksi eksplisit user untuk mendapatkan angka NYATA (bukan diprediksi)
dan diagnostik F0 lengkap (audit data, model biaya, spread, kappa) yang tetap berguna
sebagai fondasi kalau panel diperluas nanti.

## Hash

Config terkunci di `config/v6.yaml`. Hash SHA-256 dicatat di `config/v6.yaml.sha256`
setelah file ini di-commit.
