# F2 -- Gerbang Struktur Payoff (XAUUSD, 5 horizon)

Per stop_conditions.1: STOP TOTAL hanya kalau gagal di SEMUA horizon. n_random_entries=20000 per sisi per kombinasi per horizon, partisi SCREEN (20% kronologis pertama).

## Ringkasan per horizon

> `lolos_margin_dasar` = lolos margin/gap/net_bps saja (BELUM termasuk sign_flip & stability). `lolos_semua_syarat` = shortlist itu SETELAH juga lolos sign_flip_abs_margin_tolerance_pp DAN stability_sub_periods=3 (margin harus tetap positif di ketiga sub-periode). Verdict akhir F2 memakai `lolos_semua_syarat`, bukan `lolos_margin_dasar` -- kalau hanya pakai margin dasar saja, verdict yang dilaporkan bisa terlalu optimistis.

| Horizon | Status | Bar SCREEN | Kombinasi lolos margin dasar | Kombinasi lolos SEMUA syarat | Long lolos (semua syarat)? | Short lolos (semua syarat)? | Verdict |
|---|---|---:|---:|---:|---|---|---|
| H15 | OK | 90,201 | 33 | 0 | False | False | GAGAL (nol lolos) |
| H30 | OK | 90,201 | 30 | 0 | False | False | GAGAL (nol lolos) |
| H60 | OK | 90,201 | 30 | 0 | False | False | GAGAL (nol lolos) |
| H120 | OK | 30,067 | 26 | 0 | False | False | GAGAL (nol lolos) |
| H240 | OK | 30,067 | 23 | 0 | False | False | GAGAL (nol lolos) |

## Detail kombinasi yang lolos SEMUA syarat (margin + gap + net_bps + sign_flip + stability)

(TIDAK ADA kombinasi yang lolos keenam syarat sekaligus di horizon manapun)

## Vonis akhir

**NOL LOLOS DI XAUUSD, DI SEMUA 5 HORIZON YANG DIUJI.**

**BUKAN vonis STOP TOTAL final** -- stop_conditions.1 mensyaratkan gagal di semua horizon **DAN semua instrumen**. Baru XAUUSD yang diuji; XAGUSD/EURUSD/USOIL masih dalam proses download. Vonis final menunggu panel lengkap.

Catatan penting: pada pengecekan margin/gap/net_bps SAJA (3 dari 6 syarat), 23-33 kombinasi per horizon tampak lolos, dan sisi LONG konsisten unggul jauh di atas sisi SHORT. Begitu sign_flip_abs_margin_tolerance_pp dan stability_sub_periods=3 (dua syarat yang sempat terlewat di draf pertama skrip ini) ditegakkan, SELURUHNYA gugur -- termasuk yang tadinya tampak lolos di kedua sisi (H15/H30/H120). Pola long-tampak-menang selaras dengan drift capture (XAUUSD naik signifikan 2021-2026), persis skenario yang diperingatkan di 04_PARTISI_LABELING_PAYOFF.md §'Kenapa arm demeaned yang menentukan' -- tapi bahkan sisi long pun tidak benar-benar stabil di 3 sub-periode begitu diperiksa.

Sesuai payoff_gate.kalau_nol_lolos: dilarang melonggarkan margin, mengganti arm penentu, atau menghapus syarat sisi short. Opsi yang tersisa (protokol_nol_lolos, urut):

1. Horizon lebih panjang dari H240 sudah diuji (H120, H240) dan tetap gagal di XAUUSD.
2. Cek biaya/sesi -- BELUM dicoba (model biaya belum lengkap, markup prop firm masih LOOKUP).
3. Perbesar panel -- SEDANG BERJALAN (XAGUSD/EURUSD/USOIL masih download).
4. Perpanjang riwayat -- Dukascopy punya data XAUUSD lebih jauh dari 2021 (mulai 2003).
5. Cari di area X (exit/sizing) -- BELUM dicoba.
6. Terima kalau memang nol -- BELUM final, tunggu panel lengkap dulu (langkah 3).