# 02 — HUKUM: ANTI-LOOKAHEAD, ANTI-OVERFIT, ANTI-KEBOCORAN PANEL, ANTI-RUMUS RITEL

> **Pelanggaran satu pasal = seluruh hasil batal.** Bukan peringatan gaya bahasa.
> 🔄 = baru atau berubah di v6.

---

## L — Anti-lookahead

| # | Pasal |
|---|---|
| **L1** | Fitur pada bar `t` HANYA memakai data yang tersedia saat bar `t` tutup. |
| **L2** | Semua filter/estimator WAJIB kausal. DILARANG: centered moving average, Savitzky-Golay non-kausal, `filtfilt`, smoothing dua arah, interpolasi yang melihat ke depan. |
| **L3** | Scaler/PCA/normalisasi di-fit HANYA pada fold latih, lalu diterapkan ke fold uji. |
| **L4** | Seleksi fitur dilakukan DI DALAM loop cross-validation, bukan sebelum. |
| **L5** | Label triple-barrier memang melihat ke depan (itu target, bukan bocor). TAPI sampel yang labelnya tumpang tindih dengan periode uji WAJIB dibuang dari latih (purging) + embargo. |
| **L6** | Dilarang data yang direvisi ke belakang. Satu snapshot, hash dicatat. |
| **L7** | Biaya & slippage diterapkan saat eksekusi simulasi, bukan dikurangkan di akhir. |
| **L8** | Posisi tidak menembus gap weekend/libur kecuali dimodelkan eksplisit. |
| **L9** | Sinyal dari bar `t` dieksekusi paling cepat di pembukaan bar `t+1`. |
| **L10** | **UJI KEBOCORAN WAJIB.** Bangun satu fitur yang SENGAJA bocor (memakai return masa depan). Fitur itu HARUS menghasilkan IC > 0.5 dan mengalahkan semua null. Kalau tidak, pipeline validasinya sendiri yang rusak. Jalankan SEBELUM kandidat pertama. |

### 🔄 L11 — UJI DAYA GERBANG (baru, wajib, pasangan L10)

> **Ini pasal terpenting yang v5 tidak punya, dan ketiadaannya adalah penyebab
> langsung nol survivor lima kali.**

L10 menguji bahwa sinyal **curang** menang. Itu setengah pemeriksaan.
L11 menguji bahwa sinyal **jujur dan realistis** selamat.

```
Prosedur wajib (dijalankan di F1, SEBELUM kandidat pertama):

1. Bangun sinyal sintetis dengan IC yang DIKONTROL, disuntikkan ke data harga NYATA:
     signal_t = IC_target * z_futuro_t + sqrt(1 - IC_target^2) * noise_t
   dengan z_futuro = return masa depan yang distandardisasi.
   IC_target diambil dari grid: [0.03, 0.05, 0.08]

2. Jalankan sinyal itu lewat SELURUH tumpukan gerbang, apa adanya, tanpa kelonggaran.

3. Ulangi 500 kali dengan seed berbeda.

4. Catat TRANSMITANSI = proporsi yang lolos, per tahap dan untuk rantai penuh.

SYARAT LOLOS L11:
    transmitansi tahap SCREENING   >= 0.80  pada IC 0.05
    transmitansi tahap ROBUSTNESS  >= 0.70  pada IC 0.05
    transmitansi RANTAI PENUH      >= 0.50  pada IC 0.05

GAGAL -> BERHENTI. Perbaiki DESAIN GERBANGNYA (urutan, tahapan, gerbang mana yang
         KILL vs FLAG). DILARANG menurunkan ambang CONFIRM.
```

**Kenapa ini bukan pelonggaran:** L11 tidak mengubah ambang manapun. Dia cuma
**mengukur** apakah gerbang yang Anda pasang sanggup meloloskan sesuatu yang memang
bagus. Gerbang yang membunuh 99.8% edge nyata bukan gerbang ketat — dia gerbang rusak,
dan tanpa L11 Anda tidak akan pernah tahu bedanya.

Angka terukur: desain v5 **0.17%**. Desain v6 **tergantung konfigurasi sampel** —
24.8% pada TIER-A, 21.6% pada TIER-B (dua-duanya GAGAL), **64.7%** pada konfigurasi
TARGET (8 instrumen, ρ_PnL 0.10, riwayat 20 thn). Lihat §07 B3b.

**Konsekuensinya:** L11 bukan formalitas. Pada dua dari empat konfigurasi yang
dipertimbangkan, v6 **berhenti di F1** — dan itu memang perilaku yang benar.

### 🔄 L12 — Anti-kebocoran lintas-seksi (baru)

Formula panel/lintas-seksi punya titik bocor yang tidak ada di formula satu instrumen.
Ini **titik kebocoran nomor satu** di riset faktor.

| # | Aturan |
|---|---|
| **L12a** | Instrumen yang barnya belum tutup pada `t` (beda jam sesi) WAJIB dikeluarkan dari perhitungan lintas-seksi bar itu. **DILARANG forward-fill.** |
| **L12b** | Timestamp diselaraskan ke UTC. Hanya bar yang penutupannya benar-benar terjadi `<= t` yang ikut. |
| **L12c** | Median/mean/rank lintas-seksi dihitung dari instrumen yang tersedia pada `t` saja. Jumlah instrumen yang ikut WAJIB dicatat per bar. |
| **L12d** | Kalau instrumen yang tersedia pada bar `t` < 4, bar itu **dilewati** — bukan dihitung dengan panel pincang. |
| **L12e** | **Uji kebocoran khusus lintas-seksi (wajib):** bangun versi yang SENGAJA memakai bar yang belum tutup di instrumen lain. Versi bocor itu HARUS menang telak. Kalau tidak, penyelarasan sesi Anda bermasalah. |
| **L12f** | Survivorship: instrumen yang datanya baru mulai di tengah sampel TIDAK boleh masuk perhitungan lintas-seksi sebelum tanggal mulainya. Matriks ketersediaan wajib dilaporkan di F0. |

### 🔄 L13 — Anti-kebocoran rezim & router (baru)

Router multi-strategi menambah permukaan bocor baru.

| # | Aturan |
|---|---|
| **L13a** | Label rezim pada bar `t` HANYA dari data `<= t`. Deteksi rezim yang "menengok ke belakang untuk menandai titik balik" (PELT/segmentasi retrospektif) DILARANG dipakai sebagai fitur live — hanya boleh sebagai **umur segmen berjalan** yang kausal. |
| **L13b** | Parameter router (ambang tilt, hazard, jendela) di-fit HANYA pada fold latih, di dalam loop CV. |
| **L13c** | Arah tilt tiap keluarga **DI-PRA-REGISTRASI** sebelum melihat hasil. Tilt yang tandanya terbalik dari yang dipra-registrasi = **GAGAL**, bukan "penemuan". |
| **L13d** | Router WAJIB dibandingkan terhadap `N3_REGIME_SHUFFLE`: label rezim diacak sambil mempertahankan distribusi durasi rezim. Router yang tidak mengalahkan label acak = derau. |

---

## O — Anti-overfit

| # | Pasal |
|---|---|
| **O1** | Pre-registration. Semua parameter & ambang ditulis dan di-hash SEBELUM melihat hasil. |
| **O2** | Setiap konfigurasi yang dijalankan = 1 baris ledger. Sweep 42 = 42 baris. |
| **O3** | 🔄 DSR memakai jumlah trial kumulatif dari ledger **selection-problem yang sama**. Lihat O10. |
| **O4** | Anggaran parameter: `n_parameters <= eff_N_panel / 20`. Melebihi → `PARKED`. |
| **O5** | Kandidat ARAH: `select_champion()` DILARANG punya `sort` / `argmax` / `idxmax` / `nlargest` / `max()`. Hanya filter terhadap ambang. Memilih peringkat 1 dari daftar yang semuanya tidak berbeda dari nol = memilih keberuntungan. |
| **O6** | Kandidat ESTIMASI: Model Confidence Set α=0.10. Kalau imbang, pilih yang PALING SEDERHANA. |
| **O7** | HOLDOUT dibuka SEKALI seumur proyek. Sebelum itu `.LOCKED` 0-byte. |
| **O8** | Ambang DILARANG diubah setelah melihat hasil. Ubah = OVERRIDE V6 tertulis + ulang dari awal. |
| **O9** | Dilarang melaporkan "terbaik dari N percobaan" tanpa menyebut N. |

### 🔄 O10 — Ledger dipisah per masalah seleksi (baru)

v5 menghitung DSR dari **satu** ledger gabungan. Itu salah secara statistik dan mahal
secara anggaran: trial estimasi (divisi V/Q/T/S) diseleksi dengan **Model Confidence Set**,
bukan dengan Sharpe. Memasukkan mereka ke `N` untuk DSR menaikkan `SR_0` untuk kandidat
arah tanpa alasan — mereka bukan bagian dari masalah seleksi yang sama.

```
ledger_arah.csv       -> divisi E1/E2/E3, X, M, ROUTER
                         N ini yang dipakai DSR.
ledger_estimasi.csv   -> divisi V, Q, T, S
                         diseleksi lewat MCS. TIDAK masuk N untuk DSR.
ledger_diagnostik.csv -> F2 pengukuran payoff, uji L10/L11, kalibrasi biaya
                         BUKAN seleksi strategi. TIDAK masuk N manapun.
```

**Aturan mengikat:** sebuah trial masuk `ledger_arah` **jika dan hanya jika** hasilnya
bisa menyebabkan sebuah aturan arah dipilih atau dibuang. Kalau tidak — dia bukan
bagian dari masalah seleksi itu.

> ⚠️ Ini **perubahan material** yang menaikkan anggaran efektif. Butuh persetujuan
> tertulis Anda dan di-hash sebelum F0 dikunci.

### 🔄 O11 — Setiap kandidat wajib mendeklarasikan keluarga & arah prior (baru)

```yaml
family: MOM | MRV | BRK        # wajib, satu saja
prior_regime: <kondisi di mana keluarga ini DIHARAPKAN menang>
prior_sign: + | -              # arah interaksi yang dipra-registrasi
```

Deklarasi ini **mengikat**. Kandidat yang hasilnya bagus tapi dengan tanda interaksi
**terbalik** dari yang dideklarasikan ditandai `SIGN_FLIP_SUSPECT` dan **tidak boleh
masuk CONFIRM** tanpa hipotesis baru yang dipra-registrasi ulang dari awal.

Ini yang membedakan "menemukan efek yang diprediksi" dari "mengaduk data sampai ada
yang keluar".

---

## Anti-rumus ritel

### Dilarang total

```
ATR sebagai estimator volatilitas    RSI                    Stochastic oscillator
MACD                                 Bollinger Bands        Ichimoku
Fibonacci retracement                pivot point            supply demand zone
order block                          fair value gap         support resistance manual
candlestick pattern                  Elliott wave           parabolic SAR
chandelier exit                      ATR trailing stop      volume profile / POC
EMA/SMA crossover sebagai sinyal
```

**Alasan:** tidak punya sumber peer-reviewed, tidak punya turunan statistik yang bisa
diuji, dan parameternya tidak punya pembenaran selain kebiasaan.

### Padanan akademik wajib

| dilarang | pengganti |
|---|---|
| ATR | `V01_PARKINSON`, `V02_GARMAN_KLASS`, `V03_ROGERS_SATCHELL`, `V04_YANG_ZHANG` (juara MCS divisi V) |
| EMA crossover | **divisi S** (`E10`/`E11`/`E12` — kini fitur REZIM, bukan sinyal arah) → dipakai lewat router §09, bukan sebagai entry langsung |
| Bollinger | `X04_EMPIRICAL_QUANTILE_BARRIER`, `X10_POT_GPD_STOP` |
| RSI / Stochastic | `MOM05_MANN_KENDALL`; sisa keluarga uji tren nonparametrik v5 (E71/E73/E74) **tidak dibawa ke v6** — dipangkas anggaran |
| ATR trailing stop | `X20_SPRT_EXIT`, `X12_CVAR_OPTIMAL_STOP`, `X22_QUICKEST_DETECTION_EXIT` |
| pivot / support-resistance | `BRK05_CUSUM_CHANGEPOINT`, `BRK06_PELT_SEGMENTATION`, 🔄 `MOM11_EXTREME_PROXIMITY` |
| MACD | `MOM04_DRIFT_BURST_TSTAT`, `MOM01_INTRADAY_MOMENTUM` |
| volume profile | **DILARANG TANPA PENGGANTI** (volume MT5 = tick count) |
| 🔄 breakout garis manual | `BRK01_ORB_SESSION`, `BRK02_POT_EXCEEDANCE`, `BRK03_VOL_CONTRACTION_EXPANSION` |

> ⚠️ **Perhatikan prefiks ID.** Null benchmark memakai `B01`–`B09` (`B01_BUY_AND_HOLD`,
> `B02_RANDOM_MATCHED`, …). Formula breakout memakai **`BRK01`–`BRK07`**. Dua ruang nama
> yang berbeda — jangan tertukar. Draf awal v6 sempat menulis `B01`–`B04` untuk breakout;
> itu tabrakan ID dan sudah diperbaiki.
>
> 🔄 **Baris `pivot / support-resistance` dan `breakout` adalah tambahan v6.**
> Sebelumnya "level" tidak punya padanan legal sama sekali, jadi kebutuhan nyata untuk
> trading berbasis level tidak tersalurkan. `B04_EXTREME_PROXIMITY` (George & Hwang,
> Journal of Finance 2004) adalah bentuk level yang punya jurnal, punya mekanisme
> perilaku yang jelas (anchoring), dan bisa diuji.

### VWAP & Kalman

| status | |
|---|---|
| **DILARANG** | dipakai sebagai anchor mean-reversion (sinyal "harga jauh dari VWAP/Kalman maka balik arah"). Sudah diuji dan mati total: VWAP bands persentil permutasi **2.7%** (lebih buruk dari acak), keluarga Kalman korelasi **1.000** antar varian, semua mati di lima uji robustness. |
| **DIIZINKAN** | VWAP sebagai benchmark biaya eksekusi (bukan sinyal arah); Kalman sebagai estimator keadaan laten (drift/volatilitas tersembunyi). |

### 🔄 Aturan z-score (dari Adendum Z, dinaikkan jadi hukum)

| bentuk | yang di-standardisasi | vonis |
|---|---|---|
| `z = (P - MA(P)) / sigma(P)` | **harga** terhadap rata-rata bergulirnya sendiri | ⛔ **Bollinger ditulis ulang dengan notasi statistik.** Dilarang. |
| `MRV04_MAD_ZSCORE_GATE` | **nilai sinyal** yang sudah ada, sebagai gerbang kekuatan | ✅ boleh — lapisan normalisasi |
| `MOM09_XS_ZSCORE_PANEL` | **lintas instrumen** pada satu titik waktu | ✅ boleh — riset faktor standar |
| `MRV02_OU_SSCORE` | **residual** setelah faktor panel dibuang | ✅ boleh — Avellaneda & Lee |

Menamainya "z-score" tidak mengubah apapun kalau rumusnya identik dengan Bollinger.
Yang menentukan legal atau tidak adalah **apa yang di-standardisasi**, bukan namanya.

---

## Anti-data palsu

| # | Pasal |
|---|---|
| **D1** | DILARANG mengarang DOI, sitasi, nama jurnal, atau angka hasil. Tidak ketemu = tulis `NEED_LOOKUP` atau `TIDAK_KETEMU`. **Satu sitasi palsu membatalkan seluruh registry.** |
| **D2** | Kandidat wajib punya identitas sumber terverifikasi (DOI **atau** SSRN ID **atau** NBER WP) sebelum masuk CONFIRM. |
| **D3** | Dilarang mengisi `mechanism` dengan kalimat generik. Kosong lebih baik daripada karangan. |
| **D4** | Angka yang tidak bisa dihitung ditulis `TIDAK_BISA_DIHITUNG` + alasan. Dilarang angka perkiraan tanpa label. |
| 🔄 **D5** | Angka biaya, aturan akun, dan spesifikasi broker WAJIB mencantumkan **URL sumber + tanggal akses**. Angka dari sumber sekunder (blog, agregator) ditandai `SEKUNDER` dan tidak boleh dipakai di gerbang CONFIRM tanpa konfirmasi ke halaman resmi. |

---

## Konsekuensi praktis untuk yang menulis kode

- Tiap fitur baru: tanya *"apa yang diketahui pasar pada detik bar ini tutup?"* Kalau jawabannya butuh bar berikutnya — buang.
- Tiap `select_champion()` divisi arah: grep sendiri kodenya —
  `grep -nE "sort|argmax|idxmax|nlargest|max\(" select_champion` — ada satu saja → langgar §O5.
- Tiap ambang: sudah ter-hash sebelum melihat hasil? Kalau belum → langgar §O1.
- Tiap DOI: sudah resolve? Kalau belum → tulis `NEED_LOOKUP`, jangan karang.
- 🔄 Tiap formula lintas-seksi: sudah lulus uji `L12e`? Kalau belum → jangan dijalankan.
- 🔄 Sebelum kandidat pertama: sudah lulus `L10` **dan** `L11`? Dua-duanya, bukan salah satu.

---

**Lanjut ke `03_DATA_DAN_BIAYA.md`.**
