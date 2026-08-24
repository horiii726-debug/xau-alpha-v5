# SISTEM TRADING XAU v9 -- HASIL AKHIR: M5 MATI, MINGGUAN JUGA NOL

**Status: UJI_BUNUH_M5 -> L15 selesai.** Sesuai VONIS rule eksplisit: M5 mati di
semua hold & semua peserta -> lanjut otomatis ke uji mingguan MAC05/MAC07 (tanpa
konfirmasi, sesuai pra-otorisasi). L15 juga nol survivor. Bagian B-E
(SISTEM_TRADING_V7.md) **masih tidak dikerjakan** -- syarat L14 (>=1 lolos G1-G5)
belum pernah terpenuhi di v6/v7/v8/v9.

## UJI_BUNUH_M5 -- gerbang struktural sebelum bangun apapun

Cek matematis murni: terlepas dari kualitas sinyal apapun, apakah M5 punya ruang
profit setelah biaya nyata. Data: M5 2021-2026 (yang sudah ada, sesuai instruksi
eksplisit -- unduhan 2012-2026 tidak ditunggu).

**1. Biaya round-turn nyata** (jam aktif, LATIH): spread p50=1.760bps,
p90=2.316bps, komisi=0.280bps. **Biaya BASE=2.920bps, WORST=6.071bps.**

**2. Sigma per bar M5 (realized)**: 4.693bps/bar.

**3. Winrate breakeven** (p_be = (biaya/(0.7979*sigma_hold)+1)/2):

| hold (bar M5) | sigma_hold | p_breakeven |
|---:|---:|---:|
| 1 | 4.69bps | **88.99%** |
| 3 | 8.13bps | **72.51%** |
| 6 | 11.49bps | **65.92%** |
| 12 | 16.26bps | **61.25%** |
| 24 | 22.99bps | **57.96%** |

**4. Winrate aktual (CUSUM, MAC05, MAC07) vs breakeven -- SEMUA GAGAL:**

| peserta | hold=1 | hold=3 | hold=6 | hold=12 | hold=24 |
|---|---:|---:|---:|---:|---:|
| CUSUM | 48.6% | 48.4% | 48.2% | 48.8% | 49.6% |
| MAC05 (COT, broadcast D1->M5) | 39.3% | 39.5% | 39.9% | 40.6% | 41.1% |
| MAC07 (Ridge, broadcast D1->M5) | 37.3% | 37.6% | 38.1% | 38.9% | 39.4% |

Semua di bawah breakeven di semua hold, dengan margin besar (-8 s/d -52 poin
persentase). CUSUM konsisten dekat 50% (kebisingan murni, cocok dengan autopsi
sebelumnya bahwa CUSUM adalah drift capture, bukan sinyal arah asli). MAC05/MAC07
malah **konsisten di bawah 50%** ketika arah harian mereka disiarkan (broadcast)
ke tiap bar M5 dalam hari itu -- catatan jujur: ini kemungkinan bukan bug, tapi
sinyal makro harian memang tidak dirancang untuk memprediksi pergerakan 5 menit;
menyiarkannya ke granularitas M5 mayoritas menangkap derau intraday yang tidak
berkorelasi (atau berkorelasi negatif) dengan arah harian.

**5. Plafon Oracle** (arah selalu benar, batas ATAS mutlak untuk M5):

| hold | gross | net @base | net @worst |
|---:|---:|---:|---:|
| 1 | 3.74bps | 0.82bps | **-2.33bps** |
| 3 | 6.49bps | 3.57bps | 0.41bps |
| 6 | 9.17bps | 6.25bps | 3.10bps |
| 12 | 12.97bps | 10.05bps | 6.90bps |
| 24 | 18.34bps | 15.42bps | 12.27bps |

Bahkan dengan arah **100% benar**, biaya worst-case memakan seluruh gross di
hold=1 (net negatif). Ruang gerak nyata hanya muncul di hold>=3, dan itu pun
mengandalkan kondisi biaya terbaik.

**6. % bar dengan pergerakan cukup besar** (|return|>2x biaya): hold=1 cuma
16.85% (di bawah ambang 20% -- mayoritas bar melawan biaya yang tak tertutupi),
hold>=3 cukup (32-61%).

### VONIS UJI_BUNUH_M5

**M5 MATI -- winrate aktual < breakeven di SEMUA hold dan SEMUA peserta.**
Sesuai instruksi, berhenti di sini untuk M5, tidak lanjut ke sizing/ML/Monte
Carlo di granularitas ini, dan langsung lanjut ke uji mingguan yang
dipra-otorisasi.

## L15 -- MAC05 & MAC07 di horizon MINGGUAN (5 hari), G1-G5 PERSIS SAMA

Alasan (sesuai instruksi): COT dirilis mingguan; biaya round-turn dibayar SEKALI
per trade (tidak berskala dengan horizon) sedangkan sigma naik ~sqrt(5)=2.236x --
maka kappa (biaya/sigma) turun ~2.236x dibanding D1 (L13). Sinyal TIDAK diubah
sama sekali, hanya target forward return dari 1 hari jadi 5 hari. Gerbang
G1-G5 identik dengan L13/L11 (tidak dilonggarkan).

**Kappa terverifikasi turun sesuai prediksi**: kappa D1=0.0292 -> kappa
W1=0.0131 (turun 2.236x, persis sqrt(5) seperti prediksi).

| peserta | tau | n | gerbang gugur | catatan |
|---|---:|---:|---|---|
| MAC05_cot_crowding | 1.0 | 4,189 | G2 | expectancy_worst=-7.467bps |
| MAC07_ridge_combo | 1.0 | 2,154 | G2 | expectancy_worst=-3.615bps |
| MAC05_cot_crowding | 1.5 | 2,474 | G2 | expectancy_worst=-15.429bps |
| MAC07_ridge_combo | 1.5 | 1,092 | **G1** | pnl_long=-296.5, pnl_short=+3909.2 (simetri pecah di sampel mingguan, tau tinggi) |

**TOTAL SURVIVOR L15: 0/4.**

Catatan jujur: expectancy_worst MAC05/MAC07 tau=1.0 memang membaik dibanding D1
(L13 melaporkan -12 s/d -14bps di D1; di W1 jadi -7.47bps dan -3.62bps) --
konsisten dengan prediksi kappa turun. Tapi masih negatif, dan MAC07 tau=1.5
malah gagal lebih awal (G1, simetri pecah) di horizon mingguan -- kemungkinan
n mengecil (1,092, lebih sedikit observasi mingguan non-tumpang-tindih efektif)
membuat estimasi long/short kurang stabil. **Perbaikan kappa nyata, tapi tidak
cukup untuk membalik expectancy jadi positif.**

## Ringkasan menyeluruh v6-v9 (semua yang pernah diuji)

```
Harga saja, return MENTAH          : 0/130 lolos G1
Harga saja, return DEMEANED        : 5/130 lolos G1 (belum diuji G2-G5)
Makro (D1, demeaned+G1-G5)         : 0/14 lolos (2 lolos G1, gagal G2)
M5 kill-test (biaya vs sigma)      : 0/15 kombinasi/hold lolos breakeven
Makro (MINGGUAN, G1-G5 sama persis): 0/4 lolos (kappa turun 2.24x, masih G2/G1 gagal)

TOTAL kombinasi/uji diuji sepanjang v6-v9: 163
TOTAL lolos SEMUA gerbang sampai G5:         0
```

## Kesimpulan jujur

Setelah menguji lima kelas pendekatan berbeda -- harga mentah, harga demeaned,
makro harian (real yield/DXY/breakeven/COT), kelayakan struktural M5 (biaya vs
volatilitas murni, terlepas dari sinyal), dan makro mingguan (horizon yang
sesuai frekuensi rilis data itu sendiri) -- **tidak ada satupun yang lolos
kelima gerbang statistik/ekonomi**. Pola yang konsisten di semua percobaan:
edge arah yang genuinely simetris (lolos G1) ada tapi secara sistematis lebih
kecil dari biaya prop-firm-realistis (gagal G2). Memperbaiki horizon (D1->W1)
memperbaiki rasio biaya/sigma secara terukur dan sesuai prediksi teoretis, tapi
belum cukup untuk membalik tanda expectancy.

**Ini bukan "belum cukup dicoba".** 163 kombinasi/uji, lima kelas sinyal, tiga
koreksi metodologi berturut (G1-demeaned, biaya bersyarat, kappa horizon-aware),
enam horizon (M5 hold 1-24 bar, D1, W1), dan tiga dataset independen (M5
2021-2026, H1 2003-2026, makro 2003-2026).

## Rekomendasi (posisi sekarang, setelah UJI_BUNUH_M5 + L15)

| Pilihan | Isi | Status |
|---|---|---|
| A. Horizon lebih panjang lagi | Bulanan (20+ hari) -- kappa akan turun lagi ~2x dari W1 | **Belum diuji** -- arah paling konkret berikutnya jika mau dilanjutkan, sesuai pola kappa yang sudah terbukti terprediksi |
| B. Kelas edge baru | Spread lintas-aset (XAU/XAG), musiman sesi, event-driven (FOMC/NFP) | Belum diuji sama sekali di v6-v9 |
| C. Terima beta | Long-only vol-target | **TIDAK** -- dilarang aturan prop firm |

M5 (semua horizon intraday <=24 bar/2 jam) **resmi ditutup** -- VONIS
UJI_BUNUH_M5 eksplisit melarang lanjut ke sizing/ML/Monte Carlo di granularitas
ini. Kalau opsi A (bulanan) dikejar, pola L15 (kappa terprediksi turun ~sqrt(N))
memberi ekspektasi realistis: expectancy MAC05 mungkin butuh horizon >1 bulan
untuk benar-benar positif secara worst-case, dengan konsekuensi frekuensi trade
yang sangat rendah (cocok untuk gaya prop firm konservatif, tapi perlu recheck
apakah masih memenuhi target return FTMO dalam periode evaluasi terbatas).

HOLDOUT (15% terakhir tiap dataset) tetap tidak pernah dibuka di sepanjang
v6, v7, v8, dan v9.
