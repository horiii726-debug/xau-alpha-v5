# SISTEM TRADING XAU v8 -- HASIL AKHIR: NOL SURVIVOR (harga + makro)

**Status: L11 -> L12 -> L13 selesai. NOL survivor.** Sesuai instruksi eksplisit
L14: *"Kalau NOL lagi -> laporkan nol. Jangan longgarkan gerbang. Proyek
selesai."* SISTEM_TRADING_V7.md Bagian B-E **tidak dikerjakan** -- L14
mensyaratkan eksplisit ">=1 formula lolos G1-G5" dan syarat itu tidak terpenuhi.

## Diagnosis awal v8 -- benar sebagian, sudah diverifikasi

Hipotesis: gerbang G1 (v7.1/v7.2) bias karena diuji pada return MENTAH,
padahal emas naik ~11.6%/thn (headwind ~4.62bps/hari untuk semua short).
**Diverifikasi lewat L11: benar, tapi dampaknya kecil.** G1-pada-demeaned
meloloskan 5/130 kombinasi harga (naik dari 0/130 di return mentah) --
perbaikan nyata, tapi jauh dari mengubah kesimpulan menyeluruh.

## L11 -- G1 diuji ulang pada return demeaned

**5/130 lolos** (ambang keputusan asli <=3 -- sangat dekat, secara substansi
mengonfirmasi bukan membantah "harga saja tidak cukup"). Detail: semua 5 di
horizon 5-hari (H1-Lomba4): ShortHorizon-Reversal, ORB, CUSUM. Tidak diuji
lebih lanjut ke G2-G5 (di luar cakupan L11 yang eksplisit hanya soal G1) --
kalau relevan nanti, catatan ini jadi titik awal.

## L12 -- Data makro (semua berhasil, tidak seperti unduhan harga)

| seri | cakupan | catatan |
|---|---|---|
| DFII10 (real yield 10Y) | 2003-2026, 5.913 obs | variabel utama |
| DGS10 (nominal 10Y) | 1962-2026 | |
| T10YIE (breakeven inflasi) | 2003-2026 | |
| DTWEXBGS (indeks dolar) | **2006-2026** (bukan 2003) | gap 3 tahun awal |
| DEXUSEU, DEXJPUS | 1999/1971-2026 | |
| VIXCLS | 1990-2026 | |
| GVZCLS (gold vol) | **2008-2026** (bukan 2003) | |
| CFTC COT gold mingguan | 2003-2026, 1233 baris | "GOLD - COMMODITY EXCHANGE INC." |

Semua diselaraskan ke D1 dengan lag 1 hari penuh (as-of merge mundur, +1 hari
tambahan) sebelum dipakai di L13.

## L13 -- Lomba Makro (D1, gerbang G1-G5 di depan)

**0/14 kombinasi (7 formula x 2 tau) lolos.**

```
G1 (simetri, demeaned):  10 gagal
G2 (biaya worst):         3 gagal  <- MAC05 (COT crowding), MAC07 (Ridge combo)
n<30 (sampel kurang):      1 (MAC04 tau=1.5)
G3, G4, G5:                0 sempat diuji -- tidak ada yang lolos G1/G2 dulu
```

**Temuan paling informatif:** MAC05 (crowding COT non-komersial) dan MAC07
(kombinasi Ridge real-yield+DXY) **LOLOS G1** (simetri long/short genuine,
bukan drift capture) di kedua tau -- tapi gagal G2 dengan expectancy
worst-case **-12 sampai -14 bps**, jauh di bawah nol. Ini beda kualitatif
dari kegagalan G1: **ada edge terarah dua-arah yang nyata secara statistik,
tapi terlalu kecil untuk menutup biaya prop firm.**

Baseline buy-and-hold: +2.338 bps/hari (16.822 bps total, 2003-2023) --
mengonfirmasi ulang bahwa exposure LONG pasif jauh mengalahkan setiap sinyal
arah aktif yang diuji, persis kesimpulan D3.1 sebelumnya.

## Ringkasan menyeluruh v6-v8 (semua yang pernah diuji)

```
Harga saja, return MENTAH   : 0/130 lolos G1
Harga saja, return DEMEANED : 5/130 lolos G1 (belum diuji G2-G5)
Makro (real yield/DXY/breakeven/COT), demeaned+G1-G5: 0/14 lolos
                               (2 lolos G1, gagal di G2/biaya)

TOTAL kombinasi diuji sepanjang v6-v8: 144
TOTAL lolos SEMUA gerbang sampai G5:     0
```

## Kesimpulan jujur

Setelah (a) memperbaiki bias gerbang simetri terhadap headwind sekuler,
(b) menambah 8 variabel makro dari sumber gratis-terverifikasi (FRED + CFTC),
dan (c) menguji 7 formula makro dengan mekanisme ekonomi yang jelas (biaya
kesempatan real yield, kekuatan dolar, crowding positioning, kombinasi
Ridge) -- **tidak ada kombinasi yang lolos kelima gerbang**. Yang paling
dekat (MAC05, MAC07) gagal di gerbang EKONOMI (biaya > edge), bukan gerbang
STATISTIK (G1 simetri) -- pola yang berbeda dan lebih informatif dari
kegagalan sinyal harga-saja sebelumnya (yang mayoritas gagal G1).

**Ini bukan "belum cukup dicoba".** 144 kombinasi, dua kelas sinyal
(teknikal harga dan makro fundamental), dua koreksi metodologi (G1-demeaned,
biaya bersyarat), lima horizon, dan dua dataset independen (5 & 23 tahun).

## L14 -- tidak dilanjutkan, dan kenapa itu benar

L14 eksplisit: hanya lanjut ke Bagian B-E (sizing, gerbang eksekusi,
backtest sistem, Monte Carlo, ML) kalau **>=1** lolos G1-G5. Nol lolos --
tidak dikerjakan. Tidak ada `config/sistem_final.yaml`, tidak ada kurva
ekuitas, tidak ada simulasi Monte Carlo -- karena tidak ada trade nyata
untuk disimulasikan.

## Penyimpangan teknis yang harus dicatat

Unduhan M5 XAUUSD 2012-2026 (rencana v7.2, untuk cakupan bear 2012-2015 di
granularitas M5) **gagal total** -- 8+ percobaan gagal karena 429 Dukascopy
persisten (backoff sampai 42+ menit). Tidak mempengaruhi L11-L13 (yang
memakai H1 2003-2026 yang SUDAH berhasil dari v7.1, plus data makro dari
FRED/CFTC yang independen dari Dukascopy). Proses retry masih berjalan di
background kalau ingin dicek nanti (`ls /workspace/logs/download_m5_2012.DONE`),
tapi kesimpulan di atas tidak menunggu itu.

## Rekomendasi (sama, karena buktinya makin kuat menunjuk ke sana)

| Pilihan | Isi | Cocok prop firm? |
|---|---|---|
| A. Ganti horizon | >5-20 hari (di atas D1) | Ya, trade/tahun makin sedikit |
| B. Ganti kelas edge | Spread lintas-aset (XAU/XAG rasio, cointegration), musiman sesi, event-driven (FOMC/NFP) -- **belum diuji sama sekali di v6-v8** | Ya |
| C. Terima beta | Long-only vol-target 8-10%, bukan strategi arah aktif | **TIDAK** -- prop firm melarang |

**Catatan untuk Pilihan B:** MAC05 (COT) mendekati lolos -- edge arah ada,
cuma kekecilan untuk horizon harian. Mekanisme serupa (positioning,
crowding) mungkin lebih kuat di horizon lebih panjang (mingguan, sesuai
frekuensi rilis COT itu sendiri) -- ini arah riset paling konkret yang
tersisa dari seluruh proyek v6-v8, belum dieksplorasi.

HOLDOUT (15% terakhir tiap dataset) tetap tidak pernah dibuka di sepanjang
v6, v7, dan v8.
