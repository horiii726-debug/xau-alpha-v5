# SISTEM TRADING XAU v11 -- HASIL AKHIR: 22 FORMULA ARAH BARU (V10+V11), NOL SELAMAT

**Status: UJI_BUNUH_M5 -> L15 -> V10 -> V11 selesai.** V11 memperluas V10
dengan 13 formula baru: 9 dari registri arah v6 sendiri (E1 MOM/E2 MRV/E3 BRK
-- yang genuinely belum pernah diuji di bawah nama apapun) + 4 formula kuant
umum lintas-aset (safe-haven, lottery/skew, low-vol anomaly, pembalikan
jangka panjang), semua dengan sitasi DOI/SSRN terverifikasi manual. 8/13
ditolak uji korelasi (>0.30 vs registry lama -- tingkat penolakan tinggi,
temuan itu sendiri informatif: ruang informasi baru dari transformasi harga
makin jenuh). **0/5 sisanya lolos G1-G6.** Total formula arah unik diuji
sepanjang V10+V11: **22 (9 dari V10 + 13 dari V11), 0 lolos semua gerbang.**

**Catatan metodologi penting (V11):** divisi V (volatilitas), Q (spread/
likuiditas), T (intensitas tick), S (struktur/rezim) di registri v6 --
65 formula lagi -- SENGAJA TIDAK dipaksa lewat gerbang arah G1-G6. v6
sendiri mengklasifikasikan mereka `estimation`, bukan `direction`: mereka
mengukur KEADAAN pasar, bukan ARAH, dan memaksakan gerbang arah padanya
berarti mengarang konvensi tanda yang tidak berdasar literatur -- justru
melanggar aturan anti-ngasal proyek ini sendiri. Beberapa sudah dipakai
sebagai KOMPONEN sah di formula arah yang diuji (Parkinson menskala
MOM08/11/BRK01/03; Roll & Amihud = MIC03/01 di V10). Detail lengkap:
`reports/V10_IMPOR_JURNAL.md`. Bagian B-E (SISTEM_TRADING_V7.md) **masih tidak
dikerjakan** -- syarat L14 belum pernah terpenuhi di v6/v7/v8/v9/v10.

## V10 -- Impor rumus dari jurnal (kelas informasi baru)

Anggaran keras: maksimal 20 formula baru, sitasi WAJIB DOI/SSRN terverifikasi
(dicek manual lewat pencarian web, bukan dikarang), tanda diprediksi SEBELUM
diuji, parameter asli paper di lintasan pertama, gerbang G1-G6 (G6 baru: dekai
pasca-publikasi McLean & Pontiff 2016) SAMA PERSIS dengan L13/L15.

**9 formula diimplementasikan** (dari 16 kandidat yang diriset): XAS01
(kointegrasi gold-silver, Escribano & Granger 1998), OPT01 (variance risk
premium gold, Nguyen/Prokopczuk/Wese Simen 2019, J. Int'l Money & Finance),
COT02 (crowding Managed Money DCOT, Chen & Mo 2023), MIC01-03 (Amihud 2002,
Kyle 1985, Roll 1984 -- proksi order flow dari data tick M5), SEA01 (turn-of-
month, Lakonishok & Smidt 1988), SEA02 (efek hari-minggu, French 1980 + Kohli
2012), EVT01 (pra-FOMC ditransfer ke gold, Lucca & Moench 2015).

**7 kandidat dibuang SEBELUM implementasi** (jujur, bukan disembunyikan):
struktur berjangka/lease rate (data tidak tersedia gratis -- GOFO dihentikan
2015), GDX lead-lag (tidak ada sitasi akademik, hanya blog industri), skew
opsi & term structure GVZ (data tidak tersedia), rasio konsentrasi COT
(sitasi tidak bisa diverifikasi -- PDF korup), CPI/NFP surprise-day (jadwal
rilis presisi tidak terverifikasi), sesi London/NY (mismatch horizon --
mekanismenya intraday-jam sedangkan M5 sudah terbukti mati).

**Uji korelasi vs registry lama (ambang |r|<=0.30, SEBELUM gerbang):** COT02
ditolak (korelasi 0.599 vs MAC05_cot_crowding -- terlalu mirip sinyal COT lama
yang sudah diuji). 8 sisanya lolos uji korelasi (|r| 0.04-0.28).

**Hasil G1-G6 (8 formula x tau-grid bertingkat = 12 kombinasi, total trial
13 termasuk COT02):**

```
G1 (simetri, demeaned): 9 gagal
G2 (biaya worst):        2 gagal (XAS01 tau=1.0, MIC03 tau=1.0)
n<30:                    1 (MIC03 tau=2.0)
G3-G6:                   0 sempat diuji -- tidak ada yang lolos G1/G2 dulu

TOTAL SURVIVOR: 0/12
```

**Temuan yang harus dicatat jujur:** 4 formula (OPT01 gold VRP, SEA01
turn-of-month, SEA02 hari-minggu, EVT01 pra-FOMC) menunjukkan pola G1 GAGAL
dengan tanda pra-registrasi, TAPI kalau tandanya dibalik, G1 akan LOLOS --
**dan G1 di V10 SUDAH diuji pada return DEMEANED 60-hari sejak awal** (koreksi
metodologi L11 sudah dibakukan di gerbang, bukan raw). Jadi ini bukan soal
headwind sekuler yang belum dikoreksi -- deviasinya genuine setelah demean.
Sesuai aturan eksplisit ("kalau baru berhasil dengan tanda terbalik -> itu
data mining, BUANG"), keempatnya **tetap dibuang, tidak dibalik**. Temuan ini
tetap informatif: gold punya asimetri long/short musiman/event yang signifikan
secara statistik bahkan setelah demean, tapi ARAHNYA konsisten berlawanan dari
mekanisme yang diprediksi di literatur asal (ekuitas/aset lain). Kemungkinan
penjelasan: mekanisme akademik (turn-of-month institusional, weekend effect,
pra-FOMC risk premium) dibangun untuk ekuitas dengan basis investor dan struktur
kepemilikan berbeda total dari gold; mengimpor TANDA-nya mentah-mentah ke gold
adalah asumsi yang salah, bukan berarti gold tidak punya struktur musiman sama
sekali. Arah riset paling konkret berikutnya kalau dilanjutkan: pra-registrasi
ulang keempat formula ini dengan mekanisme gold-spesifik (bukan transfer
langsung dari ekuitas) SEBELUM melihat data lagi -- bukan membalik tanda
berdasarkan hasil yang sudah terlihat (itu tetap data mining).

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

## Ringkasan menyeluruh v6-v11 (semua yang pernah diuji)

```
Harga saja, return MENTAH          : 0/130 lolos G1
Harga saja, return DEMEANED        : 5/130 lolos G1 (belum diuji G2-G5)
Makro (D1, demeaned+G1-G5)         : 0/14 lolos (2 lolos G1, gagal G2)
M5 kill-test (biaya vs sigma)      : 0/15 kombinasi/hold lolos breakeven
Makro (MINGGUAN, G1-G5 sama persis): 0/4 lolos (kappa turun 2.24x, masih G2/G1 gagal)
Kelas informasi baru (jurnal, D1)  : 0/12 lolos G1-G6 (V10: 9 formula, 4 nyaris
                                      lolos G1 tapi HANYA dgn tanda terbalik)
Registri v6 (E1/E2/E3) + kuant umum: 0/5 lolos G1-G6 (V11: 13 formula, 8
                                      ditolak pra-gerbang krn korelasi >0.30)

TOTAL kombinasi/uji diuji sepanjang v6-v11: 189 (176 + 13 trial V11)
TOTAL lolos SEMUA gerbang sampai G6:          0
```

## Kesimpulan jujur

Setelah menguji tujuh kelas pendekatan berbeda -- harga mentah, harga demeaned,
makro harian (real yield/DXY/breakeven/COT legacy), kelayakan struktural M5
(biaya vs volatilitas murni, terlepas dari sinyal), makro mingguan (horizon
sesuai frekuensi rilis data), kelas informasi BARU dari literatur akademik
(kointegrasi lintas-aset, variance risk premium, crowding DCOT, proksi order
flow tick, musiman, event-driven pra-FOMC), dan registri arah v6 sendiri
(momentum/mean-reversion/breakout) plus faktor kuant umum lintas-aset
(safe-haven, lottery, low-vol anomaly, pembalikan jangka panjang) -- **tidak
ada satupun yang lolos gerbang statistik/ekonomi lengkap**. Polanya konsisten
dan makin kuat lintas kelas: edge yang genuinely simetris (lolos G1) memang
ada di beberapa tempat, tapi (a) di kelas harga/makro secara sistematis lebih
kecil dari biaya prop-firm-realistis (gagal G2), (b) di kelas musiman/event
V10, ADA asimetri statistik nyata bahkan setelah demean -- tapi arahnya
berlawanan dari mekanisme akademik yang diimpor (dibuang sesuai aturan
anti-data-mining, tidak dibalik), dan (c) di V11, **mayoritas (8/13) formula
baru justru terlalu MIRIP dengan sinyal yang sudah diuji** (korelasi >0.30) --
temuan tersendiri: ruang informasi genuinely baru dari transformasi harga/
volume/likuiditas sudah cukup jenuh setelah 6 putaran riset. Memperbaiki
horizon (D1->W1) memperbaiki rasio biaya/sigma secara terukur dan sesuai
prediksi teoretis, tapi belum cukup untuk membalik tanda expectancy.

**Ini bukan "belum cukup dicoba".** 189 kombinasi/uji, tujuh kelas sinyal
(termasuk 22 formula dari jurnal akademik/registri v6 terverifikasi DOI/SSRN
di V10+V11), lima koreksi metodologi berturut (G1-demeaned, biaya bersyarat,
kappa horizon-aware, uji korelasi pra-gerbang, dekai pasca-publikasi G6),
enam horizon (M5 hold 1-24 bar, D1, W1), dan lima dataset independen (M5
2021-2026, H1 2003-2026, makro FRED/CFTC 2003-2026, DCOT 2006-2026, XAG
2021-2026).

## Rekomendasi (posisi sekarang, setelah UJI_BUNUH_M5 -> L15 -> V10 -> V11)

| Pilihan | Isi | Status |
|---|---|---|
| A. Horizon lebih panjang lagi | Bulanan (20+ hari) -- kappa akan turun lagi ~2x dari W1 | **Belum diuji** -- arah paling konkret untuk kelas MAKRO (MAC05/07) |
| B. Mekanisme musiman/event gold-spesifik | Pra-registrasi ULANG (bukan balik tanda) untuk OPT01/SEA01/SEA02/EVT01 dengan teori yang dibangun untuk gold, bukan transfer mentah dari ekuitas | **Belum diuji** -- arah paling konkret untuk kelas V10, didukung temuan asimetri statistik nyata (G1 gagal tipis dgn tanda benar) |
| C. Kelas edge lain yang masih tersisa | Struktur berjangka (perlu data kurva futures berbayar), CPI/NFP (perlu jadwal rilis presisi), skew opsi (perlu option chain) -- semua terhambat DATA, bukan terbukti gagal | Belum bisa diuji dengan sumber gratis |
| D. Terima beta | Long-only vol-target | **TIDAK** -- dilarang aturan prop firm |

M5 (semua horizon intraday <=24 bar/2 jam) **resmi ditutup** -- VONIS
UJI_BUNUH_M5 eksplisit melarang lanjut ke sizing/ML/Monte Carlo di granularitas
ini. Kalau opsi A (bulanan) dikejar, pola L15 (kappa terprediksi turun ~sqrt(N))
memberi ekspektasi realistis: expectancy MAC05 mungkin butuh horizon >1 bulan
untuk benar-benar positif secara worst-case, dengan konsekuensi frekuensi trade
yang sangat rendah (cocok untuk gaya prop firm konservatif, tapi perlu recheck
apakah masih memenuhi target return FTMO dalam periode evaluasi terbatas).

HOLDOUT (15% terakhir tiap dataset) tetap tidak pernah dibuka di sepanjang
v6, v7, v8, v9, dan v10.
