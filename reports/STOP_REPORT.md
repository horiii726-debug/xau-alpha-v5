# STOP REPORT (FINAL) -- XAU ALPHA RESEARCH v6

**Status: BERHENTI.** Dua gerbang mati independen gagal: **GM-1/GM-1b** (F0, ukuran
panel) dan **GM-3** (F1, biaya vs edge). GM-3 diuji ulang setelah DUA koreksi
metodologi yang diminta user, dan **tetap gagal** -- ini bukan lagi artefak
pengukuran, ini temuan tervalidasi.

## Riwayat koreksi (transparansi penuh)

Laporan ini melalui 3 iterasi biaya, tiap kali lebih ketat/lebih benar:

| iterasi | basis biaya worst | cost_worst H240 (rezim-sekarang) | net @ IC=0.05, tau terbaik |
|---|---|---:|---:|
| 1 (awal) | rata-rata SELURUH riwayat (6 thn), p90 | 28.22 bps | -19.51 bps |
| 2 (rezim) | HANYA 3 thn terakhir, p90 | 23.84 bps | -19.67 bps -> -6.02 bps* |
| **3 (final)** | **HANYA 3 thn terakhir, bersyarat Q10 (p50) + tau eksplisit** | **10.13 bps** | **-6.15 bps (tau=1.5)** |

*iterasi 2 memakai threshold-dari-frekuensi; angka -6.02 muncul setelah tau
eksplisit ditambahkan di iterasi 3 dengan biaya iterasi 2 -- baris ini digabung
untuk menunjukkan efek KEDUA koreksi berjalan bertahap, bukan sekali lompat.

**Margin membaik ~3x dari iterasi 1 ke 3** (dari -19.5bps ke -6.15bps di IC=0.05).
Tapi tetap NEGATIF. Ini adalah vonis yang lebih kuat, bukan lebih lemah -- sudah
melalui dua ronde koreksi metodologi yang seharusnya menguntungkan kandidat kalau
ada kesalahan ukur yang tersisa, dan hasilnya tetap gagal.

## Dua koreksi yang diterapkan

**Koreksi 1 -- biaya bersyarat Q10_SPREAD_PERCENTILE_GATE:** Q10 hanya izinkan
entry saat spread<=p50. Menghitung skenario "worst" dari p90 seluruh sampel berarti
menghukum kandidat dua kali (sekali oleh Q10 yang menolak periode spread lebar,
sekali lagi oleh model biaya yang tetap memakai p90 itu). Diperbaiki: worst = p50,
alpha=1.5, penalty=1.5 (ketatnya dipertahankan, basisnya yang diperbaiki).
**Efek: biaya worst turun dari 23.84 ke 10.13 bps (rezim sekarang).**

**Koreksi 2 -- selektivitas via tau eksplisit:** kandidat sekarang punya ambang
kekuatan sinyal tau pada |signal| (grid [1.0, 1.5]), bukan threshold yang dipaksa
untuk menghasilkan ~220 trade/tahun. Formula: edge/trade = IC * sigma * E[z||z|>tau].
tau=1.5 -> E[z]=1.94 (vs E[z]=0.80 tanpa seleksi) -- **hampir 2.5x lipat edge per
trade untuk IC yang sama**, dengan konsekuensi frekuensi turun ke ~252 trade/tahun
(masih lolos F_BR>=100/thn).

## Gerbang mana yang kena, angka final

| Gerbang | Ambang | Terukur | Vonis |
|---|---|---:|---|
| **GM-1** | K_eff >= 3.0 | 1.6281 (K=2, lihat catatan panel di bawah) | **GAGAL** |
| **GM-1b** | K_eff>=4.0 & T_confirm>=11thn | 1.6281 / 2.75 thn | **GAGAL** |
| **GM-3** | transmitansi rantai>=50% @IC0.05 | **0.0% di tau=1.0 DAN tau=1.5** | **GAGAL** |

**Gerbang paling mematikan (tau=1.5, IC=0.05, diagnosis per-filter):** `F_EXPECT`
(expectancy net>0) -- lolos **0.0%** dari 150 seed. Semua filter LAIN (kalahkan
null acak, frekuensi trade) lolos 94-100%. **Vonis bersih: gerbang statistiknya
sehat, murni soal ekonomi -- biaya round-trip (10.13bps) masih ~1.5x lebih besar
dari gross edge tertangkap (3.98bps) pada IC=0.05, tau=1.5, bahkan setelah kedua
koreksi.**

## Kesimpulan jujur

**Kemungkinan besar: XAU intraday (H240) di biaya prop firm memang tidak layak
pada IC realistis (0.02-0.05), dan itu jawaban yang sah** -- persis seperti yang
diantisipasi user sendiri sebagai kemungkinan hasil. Ini bukan kegagalan gerbang,
bukan kesalahan ukur (sudah dikoreksi dua kali dengan hasil konsisten), dan bukan
sesuatu yang bisa diperbaiki dengan memperbesar panel (GM-1/GM-1b) -- dua masalah
ini independen.

Untuk IC=0.05 lolos di tau=1.5, dibutuhkan gross edge >= 10.13bps -- yang berarti
IC efektif >= ~0.13 (3x di atas batas atas rentang realistis 0.05 yang dinyatakan
di spec §01). Kalau edge nyata di pasar untuk setup ini sebesar itu, ini akan
lolos. Tidak ada bukti bahwa itu benar.

## Status panel (GM-1/GM-1b) -- belum final

Unduhan data 5-instrumen (XAUUSD, XAGUSD, EURUSD, USDJPY, USOIL, 2012-2026) masih
berjalan di background, terkendala rate-limit Dukascopy berat. Sesuai instruksi
user: kalau download gagal total, F0 akan dijalankan ulang dengan 2 instrumen yang
ada (XAUUSD/XAGUSD) dan ditandai `PANEL_INSUFFICIENT` -- tetap informatif walau
tidak bisa CONFIRM. **Ini tidak mengubah vonis GM-3 di atas** -- GM-3 independen
dari ukuran panel.

## Yang TIDAK dilakukan (sesuai instruksi eksplisit)

F2 sampai F11 **tidak dijalankan** -- syarat eksplisit user ("kalau masih <50%
setelah kedua perbaikan: BERHENTI") terpenuhi. Melanjutkan ke F2 dengan gerbang
F1 gagal akan melanggar §O8 proyek ini sendiri.

## Opsi yang tersisa (untuk referensi, bukan rekomendasi aktif)

1. **Divisi X (exit dioptimalkan)** -- L11 di sini pakai eksposur horizon-tetap
   tanpa SL/TP. Barrier optimal MUNGKIN menangkap lebih banyak dari IC yang sama
   -- tapi ini butuh membangun F2 (payoff measurement) dan F5 (divisi X) penuh,
   pekerjaan besar untuk hasil yang tidak terjamin memperbaiki margin -6.15bps.
2. **Instrumen/horizon lain** -- GM-3 diuji khusus di XAUUSD H240. Belum diuji di
   XAGUSD, EURUSD, USDJPY, atau horizon selain H240/H1D.
3. **Terima hasil apa adanya** -- sesuai §07 E langkah 7.
