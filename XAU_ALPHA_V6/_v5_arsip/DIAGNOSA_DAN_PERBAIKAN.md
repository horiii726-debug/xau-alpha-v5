# DIAGNOSA MASALAH INTI & TAHAP PERBAIKAN

> Ditulis setelah F1–F7 dijalankan di XAUUSD (2021-08 s/d 2026-08).
> Status: **v1 sampai v5 — nol survivor, lima kali berturut-turut.**
>
> Dokumen ini menjawab satu pertanyaan: **kenapa selalu nol, dan apa yang
> sebenarnya harus diperbaiki.**
>
> Ini bukan dokumen untuk melonggarkan gerbang. Ini dokumen untuk memperbaiki
> *desain pengujiannya*, supaya gerbang yang ketat itu akhirnya bisa
> menyaring — bukan membunuh semuanya tanpa membedakan.

---

## RINGKASAN EKSEKUTIF

**Masalah utamanya bukan rumus. Bukan juga ambang. Tapi tiga hal ini:**

| # | Masalah inti | Akibat |
|---|---|---|
| 1 | Sampel terlalu kecil untuk ambang yang dipasang | t maksimum ≈ **0,81** melawan ambang **3,0** — mustahil secara aritmetika |
| 2 | 17 filter dijalankan sekaligus di screening | **83–94% edge asli ikut mati**, bukan cuma yang palsu |
| 3 | Lima versi menambah kandidat, tidak pernah menambah sampel | Tiap kandidat baru justru **menaikkan ambang** untuk semua kandidat lain |

**Yang belum pernah dicoba dalam 5 versi: memperbesar sampelnya.**

---

## BAGIAN 1 — APA YANG SUDAH DIJALANKAN & HASILNYA

| Fase | Isi | Hasil |
|---|---|---|
| F0 | Data + biaya | ⚠️ **Belum selesai** — XAUUSD 100% (5 thn), XAGUSD 66%, biaya masih proxy |
| F1 | Alat ukur (null, CPCV, MC, DSR) | ✅ **LULUS** — 30/30 test, uji kebocoran IC 0,80 kalahkan 8 null |
| F2 | Gerbang payoff, entry ACAK | ❌ Nol lolos, 5 horizon |
| Protokol L2 | Jendela sesi & jam murah | ❌ Nol lolos |
| F4 | Estimator volatilitas & spread (V, Q) | ✅ **ADA YANG LOLOS** — Bipower, MedRV, Corwin-Schultz |
| F5 | Exit & sizing (X), 34 kombinasi | ❌ Nol lolos, terbaik **−1,81 bps** |
| F6 | Entry (E), 55 sinyal | ⏸️ **BELUM SELESAI** — baru smoke test |
| F7 | ML & meta-labeling (M) | ❌ Nol lolos — **tapi meta-labeling terbukti menaikkan sinyal mentah** |

### Tiga hal yang sering terlewat dibaca

**F4 punya survivor.** Bipower variation, MedRV, dan Corwin-Schultz lolos.
Itu bukan nol. Alat ukur volatilitas dan spread Anda sudah punya juara —
dan itu dipakai oleh semua divisi lain.

**F6 belum benar-benar dijalankan.** 55 sinyal entry masih `PENDING`.
Jadi vonis "nol lolos" saat ini **belum lengkap** — bagian yang paling
menentukan justru belum diuji.

**Meta-labeling terbukti bekerja.** Dia menaikkan sinyal mentah secara
signifikan. Artinya mekanismenya hidup; yang belum ketemu itu sinyal primernya.

---

## BAGIAN 2 — BUG YANG DITEMUKAN & DIPERBAIKI

Empat bug ini penting karena kalau lolos, hasilnya akan **terlihat bagus
padahal palsu**:

| Bug | Dampak kalau tidak ketahuan |
|---|---|
| QLIKE meledak ke 10⁸⁰ (bug floor pembagi) | Seluruh peringkat F4 salah |
| Permutasi MC1 hampa — objek yang dipermutasi salah | Null terlalu lemah, kandidat sampah terlihat menang |
| Tie-break SL/TP salah di bar M5/M15 | Backtest terlalu optimis (~350 sinyal terkoreksi) |
| Shape mismatch array | Hasil diam-diam salah, tidak crash |

Semuanya sudah diperbaiki. Hasil F4 ke atas baru valid **setelah** perbaikan ini.

---

## BAGIAN 3 — MASALAH INTI, SATU PER SATU

### 🔴 MASALAH 1 — Sampel tidak cukup untuk ambang yang dipasang

Partisi SCREEN cuma **313 hari** (20% dari 5 tahun), **1 instrumen**.

```
t = IR × √T
313 hari ≈ 0,86 tahun
IC 0,05 → IR 0,87
t = 0,87 × √0,86 = 0,81
```

**Maksimum yang bisa dicapai: t ≈ 0,81. Ambangnya 3,0.**

Sinyal sebagus apapun akan gugur. Ini bukan soal kualitas rumus —
ini soal tidak cukup data untuk membuktikan apapun.

Penambalnya cuma satu: `t_pooled = t_single × √K_eff`.
Dengan 1 instrumen, `K_eff = 1`, jadi tidak ada penambalan sama sekali.

---

### 🔴 MASALAH 2 — 17 filter sekaligus membunuh edge asli

Ini yang paling sering tidak disadari. Hitungannya:

Anggap sinyal yang **benar-benar punya edge** punya peluang 80% lolos
tiap filter (sudah murah hati untuk sampel 313 hari).

```
8 filter yang butuh sampel besar:
0,80 ^ 8 = 0,17   →  83% edge ASLI mati

Kalau peluangnya 70%:
0,70 ^ 8 = 0,058  →  94% edge ASLI mati
```

Namanya *multiple hurdle problem*. Makin banyak gerbang berurutan,
makin besar peluang membunuh yang benar — bukan cuma yang salah.

Gerbang yang membunuh 94% edge asli **bukan gerbang yang ketat.**
Itu gerbang yang tidak menyaring apapun — informasinya nol,
persis seperti B09 `PERFECT_FORESIGHT` yang sudah Anda larang
masuk `must_beat_all` dengan alasan yang sama.

---

### 🔴 MASALAH 3 — Dua filter yang tidak bisa dijawab / saling bertentangan

**Filter #17 — "konsisten di ≥60% instrumen panel"**
Panel Anda 1 instrumen. Filter ini bukan ketat — dia **tidak terdefinisi**.
Otomatis lolos atau otomatis gugur, dua-duanya tidak bermakna.

**Filter #16 vs Filter #1 — saling menyabotase**

```
#16 minta ≥300 trade/tahun     → butuh sinyal sering
sinyal sering                   → holding pendek
holding pendek                  → biaya makan 7,9% dari gerak
biaya besar                     → #1 (expectancy net positif) GUGUR
```

Memenuhi #16 justru menghancurkan #1. Tidak ada kandidat yang bisa
memenuhi keduanya di horizon pendek dengan biaya prop firm.

Pembanding: hold 24 menit → biaya **7,9%** dari gerak.
Hold 4 jam → biaya **2,5%**. Tiga kali lebih mudah, tanpa menemukan
satu rumus baru pun.

---

### 🟠 MASALAH 4 — Sampel cuma satu rezim

2021–2026 emas naik terus. Terlihat jelas di hasil F2:

- Sisi **long** menang besar (~20 poin persen)
- Sisi **short** hampir tidak pernah menang

Itu **drift capture**, bukan struktur payoff. Arm `demeaned` menangkapnya
dengan benar dan menggugurkan semuanya — sistemnya bekerja.

Tapi artinya: sisi short **tidak pernah diuji dengan adil**, karena
sampelnya tidak memuat pasar turun.

Dukascopy punya XAUUSD sejak **2003**. Periode 2011–2015 emas turun keras,
2015–2019 sideways. Itu justru rezim yang dibutuhkan.

---

### 🟠 MASALAH 5 — Biaya masih tebakan

Semua masih `LOOKUP` / proxy ~3 bps:

- Markup spread prop firm — belum ketemu
- Komisi per lot — belum ketemu
- Swap long/short/triple day — belum ketemu
- `max_daily_loss_pct`, `max_total_drawdown_pct`, `profit_target_pct` — belum ketemu

Akibat langsung: **MC2 tidak bisa jalan.** Dan MC2 adalah satu-satunya
uji yang menjawab *"akun saya selamat atau tidak?"*

Sistem bisa untung di atas kertas tapi `P(breach) = 40%` — 4 dari 10 kali
akun mati sebelum sempat menghasilkan.

---

### 🔴 MASALAH 6 — Pola v1 sampai v5

| Versi | Sampel | Kandidat | Ambang | Hasil |
|---|---|---|---|---|
| v3 | eff N **26** | 112 | t 3,0 | 0 |
| v4 | eff N kecil | 222 | t 3,0 | 0 |
| v5 | 313 hari, **1 instrumen** | 507 | t 3,0 | 0 |

Yang berubah tiap versi: **jumlah kandidat**.
Yang tidak pernah berubah: **ukuran sampel**.

Dan menambah kandidat justru **memperburuk** — tiap kandidat baru
menaikkan ambang DSR untuk semua kandidat lain. 507 kandidat di sampel
kecil lebih buruk daripada 50 kandidat di sampel kecil.

> Ini tertulis di file Anda sendiri: `lessons_carried.8` —
> *"Menambah kandidat menaikkan ambang untuk semua kandidat lain."*
>
> Dan di kontrak kejujuran: *"Memperbesar SAMPEL supaya kandidat bagus
> punya kesempatan nyata lolos. Bukan menurunkan ambang."*
>
> Itu sudah tertulis sejak awal. Yang belum dikerjakan: melaksanakannya.

---

## BAGIAN 4 — TAHAP PERBAIKAN

Urut dari yang paling murah dan paling berdampak.

---

### TAHAP 0 — Ubah gerbang: dari tembok jadi corong
**Biaya: nol. Waktu: 1 jam. Dampak: sangat besar.**

Institusi tidak memasang 17 gerbang sekaligus. Mereka pakai corong bertingkat.

| Tahap | Filter | Ambang t | Vonis |
|---|---|---|---|
| Screening | 5 filter integritas | ≥ 1,5 | `SHORTLIST` |
| Robustness | + 5 filter stabilitas | ≥ 2,0 | `KANDIDAT` |
| Confirm | 17 penuh | ≥ 3,0 | `TERBUKTI` |

**Yang berubah bukan kejujurannya — tapi KAPAN tiap gerbang dipasang.**

Screening yang membunuh semuanya = Anda tidak pernah tahu kandidat mana
yang layak dibawa ke tahap berikutnya. Itu yang terjadi di v1–v5.

**Yang TIDAK boleh berubah, di semua tahap:**

- Holdout tetap terkunci, dibuka **sekali** seumur proyek
- Larangan `argmax` / `sort` / `nlargest` di divisi arah
- Tiap varian tetap 1 baris ledger
- Kandidat `SHORTLIST` **DILARANG** disebut terbukti
- Kandidat `SHORTLIST` **DILARANG** dipakai uang asli

**Perbaikan dua filter bermasalah:**

- **#17 panel** → tandai `PANEL_INSUFFICIENT` selama panel < 5 instrumen.
  Jangan dihitung lolos maupun gugur.
- **#16 trade/tahun** → turunkan jadi ≥100 di tahap 1–2. Tetap 300 di CONFIRM.

---

### TAHAP 1 — Selesaikan yang belum diuji
**Biaya: nol (data sudah ada). Waktu: beberapa jam.**

Belum tersentuh sama sekali:

- **F6 — 55 sinyal entry divisi E** ← paling menentukan, masih `PENDING`
- **Adendum Z** — 3 kandidat z-score, 17 varian, status usulan
- **X04, X05, X12, X13, X14, X24** — exit yang belum diuji
- **CatBoost, XGBoost monotone, LightGBM** — model tree-ensemble, belum tersentuh
- **Divisi T** (intensitas tick) — butuh data tick, belum ada

**Wajib dilakukan di F6:** untuk tiap sinyal yang expectancy **kotornya**
positif, uji ulang dengan 5 exit terbaik dari F5. Kombinasi entry × exit,
bukan entry sendirian.

Alasannya: F5 gugur karena exit diuji di atas **entry acak**. Exit tidak
bisa menciptakan arah — dia cuma membentuk ulang distribusi. Nilai divisi X
baru muncul kalau digabung dengan sinyal berarah.

**Angka yang wajib dilaporkan:**

- Berapa sinyal yang expectancy **kotornya** positif
- Berapa bps biaya harus turun supaya **bersihnya** positif
- **t-stat tertinggi yang tercapai berapa** ← ini yang paling penting

> **Cara membaca t-stat tertinggi:**
> - t terbaik ≈ **0,5–1,0** → sinyalnya memang lemah. Masalahnya rumus.
> - t terbaik ≈ **2,0–2,8** → sinyalnya ada, sampelnya yang kurang. Masalahnya data.
>
> Dua diagnosis itu butuh obat yang berbeda. Jangan lanjut ke Tahap 2
> sebelum angka ini keluar.

---

### TAHAP 2 — Beli sampel
**Ini yang belum pernah dikerjakan dalam 5 versi.**

**2a. Perbesar panel** — dampak terbesar

```
K_eff = K / (1 + (K−1)·ρ̄)

K=1   → K_eff 1,00  → t_pooled = t_single       (sekarang)
K=4,  ρ̄ 0,15 → K_eff 2,86  → t × 1,69
K=8,  ρ̄ 0,15 → K_eff 3,90  → t × 1,97
K=15, ρ̄ 0,15 → K_eff 4,74  → t × 2,18
```

Dengan `K_eff = 3,9`, sinyal yang sekarang t = 1,5 jadi **t ≈ 2,96**.
Nyaris menyentuh 3,0 — tanpa mengubah satu rumus pun.

Instrumen yang disarankan (korelasi PnL rendah, bukan korelasi harga):
`XAUUSD, XAGUSD, EURUSD, USDJPY, US100, US30, USOIL, NATGAS`

Pakai candle **M1 bid/ask**, bukan tick. Jauh lebih cepat.

**2b. Perpanjang riwayat** — memberi rezim yang hilang

Dukascopy punya XAUUSD sejak **2003**.

| Periode | Rezim | Kenapa penting |
|---|---|---|
| 2003–2011 | naik kuat | pembanding |
| **2011–2015** | **turun keras** | ← sisi short akhirnya diuji adil |
| **2015–2019** | **sideways** | ← rezim tanpa drift |
| 2019–2026 | naik | yang Anda punya sekarang |

5 tahun → 20 tahun berarti `√T` naik **2×**. Sinyal t = 1,5 jadi **t ≈ 3,0**.

**2a dan 2b digabung: pengali sekitar 3,9×.** t = 1,0 jadi t = 3,9.

Itu bedanya antara nol survivor dan punya kandidat nyata — **tanpa
menurunkan ambang satu titik pun.**

---

### TAHAP 3 — Lengkapi biaya nyata
**Waktu: 1–2 jam riset manual.**

Cari di halaman resmi FTMO / FundedNext / minimal 1 prop firm lain:

- Markup spread XAUUSD & XAGUSD
- Komisi per lot round-trip
- Swap long / short / triple swap day
- `max_daily_loss_pct`, `max_total_drawdown_pct`, `profit_target_pct`

Tidak ketemu → tulis `TIDAK_KETEMU`. **Dilarang menebak.**

Tanpa ini **MC2 mati**, dan MC2 satu-satunya uji yang menjawab
*"akun saya selamat?"*.

---

### TAHAP 4 — Jalankan ulang dengan gerbang bertingkat
Registri penuh 524 varian, panel diperbesar, riwayat diperpanjang,
gerbang corong Tahap 0.

Baru di sini angka hasilnya bisa dipercaya.

---

### TAHAP 5 — Confirm & Holdout
- F8 kunci & pre-register — hash di-commit
- F9 CONFIRM, maksimal 8 slot, **17 filter penuh, tanpa kelonggaran**
- F10 HOLDOUT, sekali tembak, degradasi vs CONFIRM harus < 50%

---

### TAHAP 6 — Forward test sebelum uang asli
**Ini yang membuat `cost_verified` akhirnya bisa jadi `true`.**

- Demo prop firm, minimal **200 trade**
- Bandingkan fill nyata vs yang dimodelkan
- Hitung ulang slippage dari fill nyata
- Jalankan ulang MC2 dengan biaya terverifikasi

Baru setelah itu: uang asli, ukuran kecil, kill switch aktif.

---

## BAGIAN 5 — URUTAN KERJA

```
TAHAP 0  ubah gerbang jadi corong         nol biaya    ← KERJAKAN DULU
TAHAP 1  selesaikan F6, F7, X, Adendum Z  nol biaya    ← lalu ini
   │
   └─► baca t-stat tertinggi:
         t ≈ 0,5–1,0  → sinyal lemah, masalahnya rumus
         t ≈ 2,0–2,8  → sinyal ada, masalahnya sampel → lanjut Tahap 2
   │
TAHAP 2  beli sampel (panel + riwayat)    beberapa jam download
TAHAP 3  biaya nyata prop firm            1–2 jam riset
TAHAP 4  jalankan ulang penuh
TAHAP 5  confirm + holdout
TAHAP 6  forward test demo
   │
   └─► uang asli
```

**Tahap 0 dan 1 tidak butuh download apapun.** Kerjakan itu dulu.
Angka t-stat tertinggi dari Tahap 1 yang menentukan apakah Tahap 2 sepadan.

---

## BAGIAN 6 — YANG TIDAK BOLEH DILAKUKAN

| Godaan | Kenapa fatal |
|---|---|
| Turunkan ambang CONFIRM sampai ada yang lolos | Anda dapat pemenang palsu, lalu kehilangan uang asli |
| Tambah kandidat lagi (v6 dengan 800 rumus) | Menaikkan ambang untuk semua kandidat lain. v1–v5 sudah membuktikan |
| Hapus `require_short_side_pass` | 33 kombinasi drift-capture langsung "lolos". Mereka mati begitu emas berhenti naik |
| Buka holdout dua kali | Holdout hanya sekali. Dibuka dua kali = sudah bukan holdout |
| Pakai kandidat `SHORTLIST` untuk uang asli | `SHORTLIST` artinya belum terbukti. Titik |
| Ganti arm penentu dari `demeaned` ke `raw` | Anda akan mengukur drift, bukan edge |

---

## PENUTUP — JAWABAN JUJURNYA

**Apakah 17 filter sekaligus itu masalah besar?**
Ya. Di sampel sebesar ini, dia membunuh 83–94% edge asli. Itu bukan
saringan ketat — itu saringan yang tidak memberi informasi apa-apa.

**Apakah ambangnya salah?**
Tidak. Ambang 3,0 itu benar dan standar institusi. Yang salah adalah
menuntut t = 3,0 dari sampel yang secara matematis maksimal cuma bisa
memberi **0,81**.

**Apakah rumusnya jelek?**
Belum ketahuan — dan itu masalahnya. **F6 belum selesai.** 55 sinyal entry
belum benar-benar diuji. Vonis apapun sekarang masih prematur.

**Apakah setelah semua ini dijamin ada yang lolos?**
Tidak. Dan itu memang tertulis di kontrak kejujuran Anda sendiri.
Yang bisa dijanjikan: edge **bisa terdeteksi kalau memang ada**.
Sampel tidak menciptakan edge — dia cuma membuka mata Anda.

**Yang paling mahal bukan hasil nol.**
Yang paling mahal adalah melonggarkan gerbang sampai sesuatu "lolos",
lalu menaruh uang asli di belakangnya.

Lima versi nol survivor itu menyakitkan. Lima versi yang menghasilkan
pemenang palsu akan jauh lebih mahal.
