# F0 -- Audit Data (Dukascopy M1 bid/ask candle)

Dijalankan: 2026-08-23T16:25:14.399067+00:00Z

Sumber: Dukascopy datafeed, M1 BID+ASK candle (bukan tick mentah -- lihat catatan di bawah).


## XAUUSD

- Rentang file harian: **2021-08-22 s/d 2026-08-22** (1827 file hari, 261 hari kosong/weekend)
- Total baris M1: 2,255,040
- Baris timestamp duplikat: 0
- Hari kerja (Sen-Jum) yang HILANG dalam rentang: 0
- Hari dengan pergerakan 1-menit > 5% (kandidat outlier/bad tick): 0
- Hash snapshot (SHA-256, 16 char pertama, gabungan hash per-hari): `11478e492a3f75ea`

## XAGUSD

- Rentang file harian: **2021-08-22 s/d 2026-08-22** (1827 file hari, 261 hari kosong/weekend)
- Total baris M1: 2,255,040
- Baris timestamp duplikat: 0
- Hari kerja (Sen-Jum) yang HILANG dalam rentang: 0
- Hari dengan pergerakan 1-menit > 5% (kandidat outlier/bad tick): 0
- Hash snapshot (SHA-256, 16 char pertama, gabungan hash per-hari): `0c5806f52900f3b9`

## Catatan jujur

- Data adalah **M1 BID+ASK candle** yang direkonstruksi dari feed Dukascopy, **bukan tick mentah**. Spread & slippage sub-menit (skala latensi 1-10 detik) **tidak bisa diukur langsung** dari data ini -- lihat F0_cost_model.md untuk cara ini ditangani (proxy penskalaan-akar-waktu, ditandai eksplisit, BUKAN pengukuran tick langsung).
- Perubahan spesifikasi kontrak (tick size dsb.) sepanjang riwayat: **TIDAK_TAHU** -- tidak ada sumber resmi yang diperiksa untuk ini di F0 ini.
- Hari kerja yang hilang bisa berarti libur bursa (Natal/Tahun Baru dsb.) ATAU gap unduhan -- tidak dibedakan otomatis di sini; wajib diperiksa manual sebelum F1 kalau panel diperluas.
