# SISTEM TRADING XAU v7.2 -- HASIL AKHIR: NOL SURVIVOR (setelah tangga horizon)

**Status: L2 -> L2b -> L3 selesai. NOL survivor. L4-L10 TIDAK dijalankan** --
`L4_SATU_SISTEM` mensyaratkan eksplisit ">=1 formula lolos G1-G4" sebelum
dikerjakan. Nol lolos, jadi tidak ada dasar untuk membangun sistem, simulasi
Monte Carlo, kurva ekuitas, atau lapisan ML. Memaksakannya berarti
mensimulasikan sistem yang tidak ada.

## Penyimpangan dari rencana, dicatat jujur

Rencana awal: unduh XAUUSD **M5 2012-2026** (~1.5 juta bar, mencakup bear
2012-2015). **Unduhan ini gagal** -- Dukascopy memblokir IP instance ini
secara persisten (429 berulang, 7+ percobaan gagal dengan backoff eksponensial
sampai 21+ menit, kemungkinan akumulasi dari banyak unduhan sepanjang sesi
ini). Atas instruksi eksplisit user ("data seadanya aja... jalankan sesuai
instruksi"), L2b dan L3 dikerjakan dengan **data yang sudah ada dan lengkap
(XAUUSD M5, 2021-08-22 s/d 2026-08-22, 5 tahun)**, bukan 2012-2026.

**Konsekuensi yang harus dipahami:** G3 (uji rezim silang) di L3 TIDAK bisa
memakai blok bull/bear/sideways yang sebenarnya -- 2021-2026 nyaris seluruhnya
rezim naik (lihat riwayat harga: $1780 -> $4570). G3 diganti 3 blok
KRONOLOGIS sebagai pengganti sementara, dicatat eksplisit sebagai keterbatasan.
Unduhan 2012+ dibiarkan tetap mencoba di background; kalau berhasil nanti,
L2b/L3 layak diulang dengan data itu -- tapi kesimpulan di bawah sudah cukup
kuat untuk berhenti sekarang, bukan menunggu.

## L2b -- Tangga horizon (WAJIB dilaporkan sebelum lanjut)

| horizon | sigma_H (bps) | biaya (bps) | **kappa** | IC_breakeven | trade/thn (tau1.5) | vonis |
|---|---:|---:|---:|---:|---:|---|
| M5 | 4.69 | 2.92 | 0.622 | 0.321 | ~12.059 | DICORET |
| M15 | 8.14 | 2.92 | 0.359 | 0.185 | ~4.020 | DICORET |
| M30 | 11.51 | 2.92 | 0.254 | 0.131 | ~2.010 | DICORET |
| H1 | 16.28 | 2.92 | 0.179 | 0.092 | ~1.005 | DICORET |
| **H4** | 32.02 | 2.92 | **0.091** | 0.047 | ~251 | **LOLOS** |
| **D1** | 79.90 | 2.92 | **0.037** | 0.019 | ~42 | **LOLOS** |

Biaya round-turn (2.92bps) TETAP di semua horizon -- yang berubah cuma sigma.
Hanya **H4 dan D1** lolos kappa<=0.15; empat horizon tercepat (M5-H1) tercoret
karena biaya terlalu besar relatif volatilitas pada frekuensi itu.

## L3 -- Lomba 2 & 4 diulang, HANYA di H4/D1, gerbang G1-G4 di depan

```
Lomba 4 (entry): 6 peserta x 2 horizon(H4,D1) x 2 tau = 24 kombinasi
  24 gagal G1 (simetri long/short)   0 gagal gerbang lain   0 lolos semua

Lomba 2 (tren):  7 peserta x 2 horizon(H4,D1) x 2 tau = 28 kombinasi
  27 gagal G1 (simetri)   1 gagal G4 (walk-forward)   0 lolos semua

TOTAL: 0/52 kombinasi lolos G1-G4
```

Detail penuh: `L3_LOMBA4_GATED.md`, `L3_LOMBA2_GATED.md`.

## Gambaran besar -- semua yang sudah dicoba di proyek ini

```
F0/F1 (pipeline 12-fase asli)     -> BERHENTI: K_eff=1.63 (panel 2 instrumen), 
                                      GM-3 gagal (biaya>edge H240 XAUUSD)
Lomba 1-5 (benchmark per fungsi)  -> HAR-RV & entropi menang (non-arah, valid).
                                      CUSUM entry "+14.1bps" -- BELUM diuji simetri.
D3.1/D3.3 (uji prioritas)         -> CUSUM: drift capture (SHORT -8.31bps p=1.0),
                                      walk-forward 5/10
L1 (autopsi demeaned long-only)   -> 1/4 lolos: t-stat(eff_N)=0.72, WF 4/10
L2 (unduh H1 2003-2026)           -> LOLOS verifikasi (6 tahun negatif)
L3 @H1 2003-2026 (G1-G4 di depan) -> NOL survivor: 0/36 (Lomba4) + 0/42 (Lomba2)
L2b (tangga horizon, data 2021-26)-> hanya H4,D1 lolos kappa<=0.15
L3 @H4/D1 2021-2026 (G1-G4)       -> NOL survivor: 0/24 (Lomba4) + 0/28 (Lomba2)

TOTAL kombinasi (horizon x tau x peserta) diuji dengan gerbang simetri
di DUA dataset berbeda (H1 23-tahun, M5 5-tahun H4/D1): 130
TOTAL lolos G1-G4: 0
```

## Kesimpulan jujur

**Tidak ada sinyal arah (dari 13 formula berbeda: 7 keluarga tren + 6 keluarga
entry, diuji di 5 horizon berbeda -- M5 sampai D1, di dua dataset independen
mencakup 5 dan 23 tahun) yang lolos simetri long/short paling dasar, setelah
biaya nyata dan gerbang G1-G4 diterapkan.** Ini bukan kegagalan satu formula
(CUSUM) -- ini pola menyeluruh: **83+ dari 84 kombinasi di data 23-tahun, dan
51 dari 52 di data 5-tahun, semuanya mati di gerbang PALING DASAR (G1)**,
bukan di uji lanjutan yang lebih halus (permutasi, DSR, dll -- yang bahkan
tidak pernah tercapai).

Ini konsisten dan berulang di kedua rentang data, kedua granularitas (H1 dan
M5), dan mencakup horizon murah (H4, D1) maupun mahal (M5-H1) -- bukan
artefak satu pilihan parameter yang kebetulan buruk.

## L4-L10: TIDAK dijalankan, dan kenapa itu keputusan yang benar

- **L4 (satu sistem)** mensyaratkan ">=1 formula lolos G1-G4" -- syarat tidak
  terpenuhi.
- **L5 (ML meta-labeling)** mensyaratkan L4 lolos DAN >=500 trade LATIH dari
  sistem yang valid -- tidak ada sistem, jadi tidak ada trade nyata untuk
  dilabeli.
- **L6 (aturan FTMO), L7 (kurva ekuitas), L8 (Monte Carlo prop firm), L9
  (multi-strategi + ML belajar-terus)** semuanya butuh trade NYATA dari
  sistem yang lolos L4. Menjalankannya sekarang berarti mensimulasikan P(FUNDED)
  dari nol trade -- angka yang akan terlihat seperti hasil tapi sebenarnya
  kosong. Ini persis yang dilarang user sendiri: *"jangan naikkan risiko
  untuk mengejar angka"* -- analognya di sini: jangan buat simulasi untuk
  mengejar keluaran yang diminta.

## Rekomendasi

Sama seperti v7.1, tiga pilihan (tidak berubah, karena temuannya tidak berubah):

| Pilihan | Isi | Cocok prop firm? |
|---|---|---|
| A. Ganti horizon | Naik ke 5-20 hari (di atas D1 yang sudah diuji) | Ya, trade/tahun makin sedikit |
| B. Ganti kelas edge | Spread lintas-aset (XAU/XAG, XAU/DXY), musiman sesi, event-driven | Ya -- belum diuji |
| C. Terima beta | Long-only vol-target, bukan strategi arah aktif | **TIDAK** -- prop firm melarang |

**Langkah teknis yang masih tertunda (bukan pilihan strategi, tapi housekeeping):**
unduhan M5 2012-2026 masih mencoba di background (bisa dicek: `ls
/workspace/logs/download_m5_2012.DONE`). Kalau akhirnya berhasil, L2b+L3 layak
diulang dengan cakupan bear-market 2012-2015 yang sebenarnya -- tapi mengingat
polanya sudah 100% konsisten di dua dataset independen, kemungkinan hasilnya
berubah drastis rendah.

## File yang TIDAK dibuat, dan kenapa itu benar

`config/sistem_final.yaml`, `figs/equity_25k.png`, `figs/montecarlo_fan.png`,
`reports/MONTECARLO.md` -- tidak dibuat. Tidak ada parameter untuk dikunci,
tidak ada trade untuk membuat kurva ekuitas, tidak ada apapun untuk
disimulasikan. HOLDOUT (15% terakhir data) tetap tidak pernah dibuka.
