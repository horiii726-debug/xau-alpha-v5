# F0 -- Daya Statistik & Verdict Gerbang Mati (GM-1 s/d GM-5)

**Riwayat bersama terukur (irisan XAUUSD & XAGUSD): 2021-08-22 s/d 2025-06-25 = 3.84 tahun.**
**T_confirm terukur (55% partisi): 2.11 tahun.**

## GM-1 -- K_eff >= 3.0

K_eff terukur = **1.6562**. Ambang = 3.0. **GAGAL -- STOP**

## GM-1b -- K_eff >= 4.0 DAN T_confirm >= 11 tahun (syarat gabungan, §01 B4b)

K_eff >= 4.0: GAGAL (1.6562). T_confirm >= 11 thn: GAGAL (2.11 thn). **GAGAL -- STOP**

## GM-2, GM-4, GM-5, sd_SR pilot, skew/kurt

**TIDAK DIJALANKAN.** GM-1 sudah gagal secara matematis dan pasti (lihat F0_universe.md -- K_eff untuk K=2 terikat ke (1,2], tidak mungkin >= 3.0 berapapun korelasinya). Menjalankan pilot 24-trial untuk sd_SR, mengukur skew/kurt empiris, atau menghitung N_maks/anggaran kandidat pada titik ini berarti **menghitung anggaran untuk registri yang sudah dijamin gagal DSR-nya** (bertentangan langsung dengan §08 D3 dan pelajaran #8 di 10_FASE_EKSEKUSI.md: 'menjalankan registri lebih besar dari N_maks dan berharap' adalah pola yang menyebabkan v1-v5 gagal lima kali). Ditandai `TIDAK_DIJALANKAN_KARENA_GM1_GAGAL`, bukan `TIDAK_TAHU` -- keputusan sadar, bukan kelalaian.

## VERDICT AKHIR F0

**BERHENTI -- lihat reports/STOP_REPORT.md**
