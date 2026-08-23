# SISTEM TRADING XAU v7 -- STOP di Uji Prioritas

**Status: BERHENTI sebelum Bagian A dimulai.** Sesuai instruksi eksplisit:
*"Kalau CUSUM gagal dua itu [D3.1 drift capture, D3.3 walk-forward], STOP dan
lapor -- sisanya percuma."* CUSUM gagal **KEDUANYA**. Bagian A-E (keluarga
MOM/MRV, sizing, router, backtest sistem utuh, ML) **tidak dikerjakan** --
membangunnya di atas sinyal yang gagal uji dasar akan membuang waktu untuk
hasil yang sudah bisa diprediksi tidak berarti.

Detail penuh & angka: `reports/D3_PRIORITY_TESTS.md`, grafik:
`reports/figs/d3_priority_tests.png`.

## Apa yang ditemukan

**D3.1 -- Drift capture: GAGAL.**

| Sisi | Expectancy net (raw) | p-value | Expectancy net (demeaned) |
|---|---:|---:|---:|
| LONG | **+7.88 bps** | 0.0000 | +2.06 bps |
| SHORT | **-8.31 bps** | 1.0000 | -2.91 bps |
| Gabungan | -0.10 bps | 0.5625 | -0.39 bps |

SHORT negatif dan tidak signifikan di kedua arm (raw maupun demeaned). Bahkan
setelah membuang tren rata-rata bergulir 60 hari, pola LONG-untung/SHORT-rugi
tetap ada (walau mengecil). **Ini tanda tangan klasik drift capture** --
CUSUM tidak mendeteksi "perubahan rezim" yang genuinely dua-arah; dia
menumpang tren naik emas dan hanya menang saat kebetulan searah dengannya.

**D3.3 -- Walk-forward: GAGAL.**

5 dari 10 jendela positif (syarat >=7/10). Yang positif justru menumpuk di
jendela 9 dan 10 (paling akhir, +10.8bps dan +8.8bps) -- persis periode
menjelang rentang yang dipakai sebagai partisi UJI di Lomba 4 sebelumnya.
**Kemenangan +14.1bps yang dilaporkan di Lomba 4 adalah artefak dari menguji
HANYA di periode itu**, bukan kinerja yang stabil sepanjang waktu.

## Kenapa ini masuk akal (bukan kejutan yang seharusnya tidak terjadi)

Sampel 2021-2026 didominasi kenaikan emas dari ~$1780 ke ~$4570 (lihat
`F0_cost_regime.md` -- tabel harga rata-rata per tahun dari riset F0/F1
sebelumnya). Sinyal apapun yang cenderung LONG lebih sering akan tampak
"menang" kalau diuji di jendela waktu yang didominasi tren naik, terutama di
periode 2024-2026 (harga naik dari $2389 ke $4572, +91%). Ini persis pola
yang sudah diperingatkan sejak dokumen v5/v6 lama: *"sampel 2021-2026 hanya
memuat satu rezim: emas naik... sisi short tidak pernah diuji dengan adil."*
Lomba 4 (dan Lomba 5 yang menumpang di atasnya) tidak sengaja mengulangi
kesalahan yang sama karena keduanya tidak memisahkan long/short maupun
menguji stabilitas lintas waktu -- baru ketahuan sekarang di uji prioritas ini.

## Apa yang TETAP valid dari 5 Lomba sebelumnya

- **Lomba 1 (HAR-RV menang volatilitas)** -- tidak terpengaruh, ini soal
  akurasi prediksi varians, bukan arah, tidak ada bias long/short.
- **Lomba 3 (entropi menang rezim)** -- juga tidak arah-spesifik (AUC untuk
  klasifikasi trending/ranging, dua kelas seimbang secara konstruksi), tapi
  BELUM diuji drift-capture/walk-forward sendiri -- statusnya "kemungkinan
  aman" bukan "terbukti aman".
- **Lomba 2 (tren)** -- sudah dilaporkan tidak ada pemenang, tidak berubah.
- **Lomba 4 & 5 (CUSUM entry + barrier)** -- **DIBATALKAN sebagai temuan.**
  Angka +14.1bps dan +19.8bps yang dilaporkan sebelumnya **valid secara
  komputasi** (bukan bug) tapi **tidak valid sebagai bukti edge** -- keduanya
  adalah produk sampel yang bias-tren, bukan sinyal yang robust.

## Rekomendasi jujur

**Jangan lanjutkan ke Bagian A-E di atas fondasi CUSUM.** Dua jalan ke depan:

1. **Ulangi Lomba 4 dengan D3.1/D3.3 sebagai gerbang WAJIB, bukan uji
   belakangan** -- setiap kandidat entry (termasuk keluarga MOM/MRV yang
   belum diuji) harus lolos long-vs-short DAN walk-forward SEBELUM
   dinyatakan menang, bukan setelah. Kandidat lain di Lomba 4 (MAD-Zscore,
   Momentum-VolScaled, dll) juga perlu diuji ulang dengan gerbang ini --
   belum tentu mereka lolos, belum tentu juga semuanya gagal seperti CUSUM.
2. **Perpanjang riwayat data** -- 5 tahun (2021-2026) mustahil memuat rezim
   emas turun/sideways yang cukup untuk menguji sisi short secara adil.
   Perluasan data yang sempat dicoba sebelumnya (dukascopy-node, mundur ke
   2012) relevan lagi di sini, bukan cuma untuk K_eff.

**Tidak ada dashboard sistem akhir atau `config/sistem_final.yaml`** --
membuatnya sekarang berarti mengkodekan aturan EA di atas sinyal yang
terbukti drift capture, persis kesalahan yang coba dihindari proyek ini
sejak awal.
