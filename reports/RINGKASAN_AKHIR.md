# RINGKASAN AKHIR -- XAU ALPHA RESEARCH v6

**Status: BERHENTI di F0 DAN F1 (dua gerbang mati independen).** Nol kandidat
dijalankan. Ini jawaban sah (§07 E langkah 7).

## Apa yang lolos

- **6 keputusan OVERRIDE V6** dicatat SETUJU dan di-hash di `PREREGISTRATION.md` /
  `config/v6.yaml.sha256`.
- **Audit data FINAL**: XAUUSD & XAGUSD, 2021-08-22 s/d 2026-08-22, **1827/1827
  hari lengkap kedua-duanya** -- nol duplikat timestamp, nol hari kerja hilang,
  nol lompatan >5%/menit.
- **Model biaya v6** (koreksi beta `sigma_latensi`) dihitung penuh dari spread
  NYATA Dukascopy + komisi resmi FTMO/FundedNext -- `F0_cost_model.md`.
- **K_eff dari korelasi PnL NYATA** (eigenvalue method) -- `F0_universe.md`.
- **L10 (uji kebocoran) LOLOS** -- pytest 4/4 hijau (`F1_leak_test.md`), alat ukur
  validasi sendiri sudah terbukti benar.
- **L11 (uji daya gerbang) dijalankan penuh** -- 450 trial (3 IC x 150 seed) sinyal
  sintetis pada harga XAUUSD nyata, plus cek tambahan H1D -- `F1_gate_power.md`.
- **Unduhan panel 8-instrumen dimulai** (`scripts/download_dukascopy.py`, berjalan
  di background) -- 5/8 ter-verifikasi, tanggal mulai nyata ditemukan lewat binary
  search (XAUUSD kembali sampai **1999**, bukan 2003 seperti dugaan spec).

## Apa yang gagal

1. **GM-1 & GM-1b (F0): GAGAL.** K_eff terukur **1.6281** (panel K=2 -- ambang 3.0/4.0).
   T_confirm **2.75 tahun** (ambang 11 tahun). Matematis pasti untuk K=2, dicatat
   SEBELUM angka dihitung.
2. **GM-3 (F1): GAGAL, INDEPENDEN dari #1.** Transmitansi corong **0.0%** di semua
   tahap & semua IC (0.03/0.05/0.08) untuk XAUUSD H240. Akar penyebab: biaya
   round-trip worst-case terukur (28.22 bps) jauh melebihi gross edge yang bisa
   ditangkap sinyal ber-IC realistis (bahkan IC=0.30 baru impas). Kappa H240
   terukur (0.678) ~2x kappa acuan spec (0.327). Sudah dicek H1D juga -- serupa.

## Angka-angka kunci

| Angka | Nilai | Ambang | Vonis |
|---|---:|---:|---|
| K_eff (eigenvalue, K=2, FINAL) | 1.6281 | >=3.0 (GM-1) / >=4.0 (GM-1b) | GAGAL |
| rho_PnL baseline XAU-XAG | 0.4779 | <=0.10 (target spec) | jauh di atas target |
| T_confirm (55% riwayat bersama, FINAL) | 2.75 thn | >=11 thn (GM-1b) | GAGAL |
| Transmitansi L11 rantai penuh @IC0.05 | 0.0% | >=50% (GM-3) | GAGAL |
| Gross edge @IC0.30 vs biaya worst H240 | ~28 bps vs 28.22 bps | -- | baru impas, bukan lolos |
| Kappa H240 XAUUSD (worst) | 0.678 | acuan spec 0.327 | ~2x lebih berat |
| P(breach 6% DD), risk 0.25%, Sharpe ASUMSI 1.15 | ~3.4% (10rb jalur simulasi) | <=5% (MC2) | LOLOS -- tapi ASUMSI Sharpe, bukan kandidat nyata |

## Rekomendasi jujur

**Jangan pakai uang asli berdasarkan run ini -- belum ada satupun kandidat yang
diuji.** ADA DUA masalah struktural terpisah, bukan satu:

1. **Panel terlalu kecil** (K=2 vs target 8) -- sedang diatasi, unduhan berjalan
   (realita: ~1-2 hari lagi untuk 5 instrumen x hingga 27 tahun riwayat).
2. **Biaya H240 XAUUSD terlalu besar relatif edge realistis** -- memperluas panel
   TIDAK otomatis mengatasi ini. Perlu diuji ulang di horizon lain, sesi
   berbiaya-rendah, atau dengan exit yang dioptimalkan (divisi X, belum diuji)
   setelah panel selesai diunduh.

**Catatan kejujuran soal L11:** hasil 0% memakai eksposur horizon-tetap tanpa
SL/TP dioptimalkan -- kandidat nyata dengan divisi X mungkin menangkap lebih
banyak dari IC yang sama. Tidak bisa dipastikan tanpa F2/F5 dijalankan, jadi
diakui sebagai batasan uji, bukan alasan mengabaikan hasilnya.

Detail lengkap & 3 opsi jalan ke depan: `reports/STOP_REPORT.md`.
Dashboard 10-panel (real data + panel "TIDAK TERCAPAI" yang jujur): `reports/dashboard.png`.
