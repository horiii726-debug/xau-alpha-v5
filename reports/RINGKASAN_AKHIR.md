# RINGKASAN AKHIR -- XAU ALPHA RESEARCH v6

**Status: BERHENTI di F0.** Nol kandidat dijalankan. Ini jawaban sah (§07 E langkah 7).

## Apa yang lolos

- **6 keputusan OVERRIDE V6** dicatat SETUJU dan di-hash di `PREREGISTRATION.md` /
  `config/v6.yaml.sha256`.
- **Audit data**: XAUUSD (2021-08-22 s/d 2026-08-22, 1827 file hari) dan XAGUSD
  (2021-08-22 s/d berjalan) -- **nol duplikat timestamp, nol hari kerja hilang,
  nol hari dengan lompatan >5%/menit** di kedua instrumen. Data Dukascopy M1
  bid/ask bersih untuk apa yang diaudit.
- **Model biaya v6** (koreksi beta `sigma_latensi`, bukan `sigma_bar`) dihitung
  penuh dengan spread NYATA dari tick Dukascopy, komisi terverifikasi resmi
  (FTMO 0.140bps, FundedNext 0.160bps per sisi metals) -- lihat `F0_cost_model.md`.
- **K_eff dihitung dari korelasi PnL NYATA** (bukan diasumsikan): metode eigenvalue,
  panel yang tersedia.

## Apa yang gagal

- **GM-1 (K_eff >= 3.0): GAGAL.** K_eff terukur **1.6562** (panel K=2: XAUUSD,
  XAGUSD -- 6 dari 8 instrumen spec v6 TIDAK diunduh, lihat `PREREGISTRATION.md`).
- **GM-1b (syarat gabungan): GAGAL.** K_eff 1.6562 < 4.0, T_confirm **2.11 tahun**
  < 11 tahun.
- Kedua kegagalan ini **matematis pasti** untuk K=2 (K_eff eigenvalue terikat ke
  rentang (1,2] untuk semua kemungkinan korelasi) -- dicatat di PREREGISTRATION.md
  **sebelum** angka dihitung, supaya tidak disalahartikan sebagai "kejutan" atau
  "gerbang rusak" (bandingkan protokol L11 §07E langkah 0 -- ini BUKAN itu; alat
  ukurnya benar, sampelnya yang tidak cukup, secara struktural).
- GM-2 (sd_SR/N_maks), GM-4, GM-5, pilot 24-trial, dan seluruh F1-F11 **sengaja
  tidak dijalankan** -- menjalankannya berarti menghitung anggaran untuk registri
  yang sudah pasti gagal DSR, pola yang menyebabkan v1-v5 gagal lima kali.

## Angka-angka kunci

| Angka | Nilai | Ambang | Vonis |
|---|---:|---:|---|
| K_eff (eigenvalue, K=2) | 1.6562 | >=3.0 (GM-1) / >=4.0 (GM-1b) | GAGAL |
| rho_PnL baseline XAU-XAG | 0.4556 | <=0.10 (target spec §01 B4b) | jauh di atas target |
| T_confirm (55% dari riwayat bersama) | 2.11 thn | >=11 thn (GM-1b) | GAGAL |
| Riwayat bersama XAU-XAG | 3.84 thn (saat F0 dijalankan) | target 20 thn | jauh di bawah |
| Biaya round-trip worst, XAUUSD | lihat F0_cost_model.md | -- | terukur, belum verified (swap/markup TIDAK_KETEMU) |
| P(breach 6% DD), risk 0.25%, Sharpe ASUMSI 1.15 | ~3.4% (simulasi 10rb jalur) | <=5% (MC2) | LOLOS -- tapi ini ASUMSI Sharpe, bukan kandidat nyata |

## Rekomendasi jujur

**Jangan pakai uang asli berdasarkan run ini -- belum ada satupun kandidat yang
diuji.** Ini bukan "strategi yang gagal", ini "proyek yang belum sampai ke tahap
menguji strategi apapun", karena fondasi statistiknya (jumlah instrumen independen)
belum cukup untuk menopang gerbang yang dirancang.

Tiga jalan ke depan ada di `reports/STOP_REPORT.md` (opsi A/B/C). Yang paling
konsisten dengan tujuan riset multi-instrumen v6: **perluas panel ke >=4-5
instrumen dengan korelasi PnL rendah** -- tapi ini butuh verifikasi kode Dukascopy
dan point-value instrumen yang belum ada di codebase (USDJPY, US100, US30,
NATGAS), yang sengaja TIDAK ditebak di run ini karena risiko silently merusak
data harga.

Dashboard lengkap (10 panel, termasuk yang ditandai eksplisit "TIDAK TERCAPAI"
untuk tahap yang tidak pernah dijalankan) ada di `reports/dashboard.png`.
