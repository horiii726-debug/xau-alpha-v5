# SISTEM TRADING XAU v7.1 -- HASIL AKHIR: NOL SURVIVOR

**Status: SELESAI diuji, NOL survivor.** Ini jawaban sah (sesuai instruksi:
*"Kalau tetap nol setelah G1-G4, laporkan nol"*). Bagian A-E dari
`SISTEM_TRADING_V7.md` **tidak dikerjakan** -- tidak ada apapun untuk
dibangun di atasnya.

## Ringkasan 3 langkah

| Langkah | Isi | Hasil |
|---|---|---|
| **L1** | Autopsi arm demeaned long-only (CUSUM) -- 4 uji | **1/4 lolos.** t-stat eff_N=0.72 (n mentah 11.942, eff_N cuma 991 -- rasio keunikan 8.3%), walk-forward 4/10 dengan 254% PnL dari 2 jendela, biaya worst negatif. |
| **L2** | Unduh XAUUSD H1 2003-2026 (203k bar, 31 detik) | **Verifikasi LOLOS.** 6 tahun negatif (2013 -27.9%, 2014, 2015, 2018, 2021, 2022) -- bear market 2012-2015 sekarang tercakup. |
| **L3** | Ulang Lomba 2 & 4 di data penuh, gerbang G1-G4 di DEPAN peringkat | **NOL survivor di keduanya.** Lomba 4: 0/36 kombinasi. Lomba 2: 0/42 kombinasi. **83/84 gagal di G1 (simetri long/short).** |

Detail penuh: `L1_AUTOPSI_DEMEANED.md`, `L2_DATA_VERIFICATION.md`,
`L3_LOMBA4_H1.md`, `L3_LOMBA2_H1.md`. Lomba 5 (SL/TP) **tidak dijalankan** --
tidak ada entry yang lolos untuk dikunci sebagai dasar uji barrier.

## Angka kunci

```
L1 -- arm demeaned long-only (CUSUM @H=1d):
  n mentah=11942, eff_N=991.5 (rasio keunikan 8.3%)
  t-stat(eff_N)=0.722, p=0.4707        <- jauh dari signifikan
  walk-forward: 4/10, 254.7% PnL dari 2 jendela  <- makin buruk dari versi mentah
  biaya worst: expectancy -1.06bps      <- negatif

L3 -- Lomba 4 (entry), H1 2003-2026, 36 kombinasi (6 peserta x 3 horizon x 2 tau):
  34 gagal G1 (simetri)   2 gagal G4 (walk-forward)   0 lolos semua

L3 -- Lomba 2 (tren), H1 2003-2026, 42 kombinasi (7 peserta x 3 N x 2 tau):
  41 gagal G1 (simetri)   1 gagal G2 (demeaned)        0 lolos semua
```

## Kesimpulan jujur

**Tidak ada edge arah yang bisa dieksploitasi di XAU pada horizon 6 jam
sampai 5 hari, dengan kelas rumus yang diuji (momentum, reversal, breakout,
drift-burst, CUSUM, dan enam estimator kemiringan), pada biaya prop firm,
setelah data diperluas ke 23 tahun dan gerbang simetri long/short dipasang
di depan.**

Ini bukan "belum cukup diuji". 84 kombinasi diuji di data yang sekarang
memuat bull run (2003-2011, 2019-2026), bear market penuh (2012-2015,
-27.9% di 2013 saja), dan periode sideways/turun (2016-2019, 2018, 2021-2022)
-- persis rezim yang hilang di riset-riset sebelumnya. 83 dari 84 tetap
gagal di gerbang PALING DASAR (G1: untung di long DAN short) -- bukan gagal
di uji lanjutan yang lebih halus.

**Kesalahan yang diakui dan sudah diperbaiki dalam proses ini:** Lomba 4
(sebelum V7.1) melaporkan CUSUM menang +14.1 bps tanpa memeriksa simetri
long/short atau stabilitas lintas rezim -- persis kontradiksi dengan Lomba 2
(tren, tidak ada juara) yang seharusnya sudah jadi tanda bahaya sebelum
Bagian A-E ditulis. Gerbang G1-G4 sekarang wajib di depan untuk SEMUA lomba
arah berikutnya, permanen.

## Tiga pilihan jalan ke depan (sesuai dokumen V7.1, tidak ditambah-tambah)

| Pilihan | Isi | Cocok prop firm? |
|---|---|---|
| **A. Ganti horizon** | Naik ke H=5-20 hari (bukan cuma sampai 5 hari yang sudah diuji) -- biaya relatif sigma jadi jauh lebih kecil. | Ya, tapi trade/tahun sedikit -- belum diuji di V7.1 ini |
| **B. Ganti kelas edge** | Bukan arah: spread lintas-aset (XAU/XAG, XAU/DXY), musiman sesi, event-driven (FOMC/NFP). | Ya -- belum diuji sama sekali |
| **C. Terima beta** | Emas long-only, vol-target 8-10%, rebalance -- strategi nyata dan jujur. | **TIDAK** -- prop firm melarang |

**Yang dilarang keras** (sesuai instruksi): menurunkan ambang G1-G4,
membuang gerbang simetri, atau kembali menguji cuma di 2021-2026. Tidak ada
satupun dari itu dilakukan di sini.

## Tidak ada file berikut, dan itu keputusan yang benar

`reports/A_keluarga_entry.md`, `B_sizing_gerbang.md`, `C_router.md`,
`D_sistem_utuh.md`, `E_metalabeling.md`, `dashboard_v7.png`,
`config/sistem_final.yaml` -- **tidak dibuat.** Membuatnya berarti mengkodekan
aturan EA di atas nol sinyal yang terbukti tidak dua-arah, setelah dua ronde
pengujian (2021-2026 lalu 2003-2026) menunjukkan hasil yang sama. HOLDOUT
(15% terakhir, ~2023-2026) **tidak pernah dibuka** -- tidak ada sistem yang
lolos sampai ke tahap itu.
