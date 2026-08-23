# RINGKASAN AKHIR -- XAU ALPHA RESEARCH v6

**Status: BERHENTI (final).** Dua gerbang mati independen gagal, GM-3 diuji ulang
setelah 2 koreksi metodologi eksplisit dan tetap gagal. Nol kandidat dijalankan
ke F2+. Ini jawaban sah (§07 E langkah 7).

## Apa yang lolos

- **6 keputusan OVERRIDE V6** disetujui, dicatat & di-hash (`PREREGISTRATION.md`).
- **Audit data FINAL** XAUUSD/XAGUSD 2021-2026, 100% lengkap, bersih.
- **L10 (uji kebocoran) LOLOS** -- pytest 4/4 hijau, alat ukur validasi terbukti benar.
- **L11 dijalankan penuh 2x** (sebelum & sesudah 2 koreksi), dengan diagnosis
  per-filter yang membuktikan gerbang statistiknya SEHAT (F_B02/F_B05/F_BR
  lolos 94-100%) -- yang gagal murni `F_EXPECT` (ekonomi biaya vs edge).
- **Dua koreksi metodologi diterapkan & divalidasi:**
  1. Biaya "worst" bersyarat Q10_SPREAD_PERCENTILE_GATE (p50, bukan p90) --
     biaya turun dari 23.84 ke **10.13 bps**.
  2. Selektivitas via ambang tau eksplisit [1.0, 1.5] pada |signal| (bukan
     threshold dari target frekuensi) -- edge/trade naik ~2.5x di tau=1.5.
- **Margin membaik ~3x** (dari -19.51bps ke -6.15bps di IC=0.05) tapi **tetap
  negatif** -- vonis yang lebih kuat karena sudah melalui 2 ronde koreksi yang
  menguntungkan kandidat.

## Apa yang gagal

1. **GM-1 & GM-1b (F0):** K_eff=1.6281 (K=2, ambang 3.0/4.0), T_confirm=2.75thn
   (ambang 11thn). Matematis pasti untuk K=2.
2. **GM-3 (F1), INDEPENDEN dari #1, diuji 2x setelah koreksi:** transmitansi
   **0.0% di tau=1.0 DAN tau=1.5**, semua IC (0.03/0.05/0.08). Untuk lolos di
   IC=0.05/tau=1.5 butuh gross edge >=10.13bps -- setara **IC efektif ~0.13**,
   3x di atas batas atas rentang realistis (0.05) yang dinyatakan spec sendiri.

## Angka-angka kunci (final, setelah koreksi)

| Angka | Nilai | Ambang | Vonis |
|---|---:|---:|---|
| K_eff (eigenvalue, K=2) | 1.6281 | >=3.0 / >=4.0 | GAGAL |
| T_confirm | 2.75 thn | >=11 thn | GAGAL |
| Biaya worst H240 (rezim-sekarang, KOREKSI Q10) | 10.13 bps | -- | turun dari 23.84bps |
| Gross edge @IC=0.05, tau=1.5 | 3.98 bps | perlu >=10.13bps | GAGAL, kurang ~6.15bps |
| Transmitansi rantai penuh, tau terbaik | 0.0% | >=50% | GAGAL |
| Gerbang paling mematikan | F_EXPECT | -- | ekonomi, bukan statistik |

## Rekomendasi jujur

**Jangan pakai uang asli.** Bukan karena strategi gagal diuji -- karena struktur
biaya XAUUSD H240 vs edge realistis (IC 0.02-0.05) sudah terbukti dua kali, dengan
metodologi yang diperbaiki dua kali, memberi hasil konsisten: **defisit ~6bps per
trade yang tidak bisa ditutup lewat seleksi sinyal lebih ketat saja**.

Ini bukan "belum cukup diuji" -- ini "sudah diuji dengan cukup ketat, dan
jawabannya tidak layak pada horizon/instrumen ini". Jalan yang tersisa (divisi X
exit optimal, instrumen/horizon lain) ada di `STOP_REPORT.md`, tapi tidak satupun
terjamin membalik defisit 6bps.

Detail lengkap: `reports/STOP_REPORT.md` (riwayat 3-iterasi koreksi biaya).
Dashboard 10-panel: `reports/dashboard.png`.
Status panel 5-instrumen (GM-1/GM-1b): unduhan masih berjalan, tidak mengubah
vonis GM-3 di atas.
