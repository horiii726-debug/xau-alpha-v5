# DIVISI E3 — BREAKOUT / EKSPANSI RANGE

> Bagian dari **XAU ALPHA RESEARCH v6**. Keluarga `BRK`.
> **Divisi ini hampir seluruhnya BARU.** v5 tidak punya kandidat breakout satupun —
> lubang nyata, karena breakout adalah salah satu dari tiga keluarga yang Anda minta.

| | |
|---|---|
| **Keluarga** | `BRK` |
| **Tipe divisi** | `direction` |
| **Ledger** | `ledger_arah.csv` |
| **Formula** | 7 (4 baru) |
| **Varian** | 14 |
| **Fase** | F6 |
| **Gerbang** | corong §07 — tahap 1 (t≥1.5) → tahap 2 (t≥2.0) → CONFIRM (17 centang, t≥3.0) |
| **`prior_regime`** | volatilitas KONTRAKSI diikuti EKSPANSI, changepoint baru, batas sesi |
| **`prior_sign`** | **`+`** — kinerja BRK naik saat transisi kontraksi→ekspansi |

## Kenapa divisi ini tidak ada di v5

v5 melarang total: order block, fair value gap, support-resistance manual, pivot point,
supply-demand zone. **Semuanya benar dilarang** — tidak ada satupun yang punya sumber
peer-reviewed atau turunan statistik yang bisa diuji.

Tapi larangan itu meninggalkan lubang: **tidak ada padanan akademik untuk breakout
sama sekali.** Tabel `padanan_akademik_wajib` v5 punya baris untuk ATR, EMA crossover,
Bollinger, RSI, MACD, pivot — tapi tidak untuk breakout. Akibatnya seluruh keluarga
strategi hilang dari registri, dan sistem jadi buta terhadap rezim transisi volatilitas.

v6 menutup lubang itu dengan empat formula yang punya sumber terverifikasi, mekanisme
yang bisa dijelaskan, dan parameter yang punya pembenaran selain kebiasaan.

## Mekanisme keluarga

> Volatilitas **berkelompok** — ini salah satu fakta stilisata paling kokoh di
> ekonometrika keuangan. Setelah kontraksi, ekspansi datang. Dan pada saat ekspansi,
> penyedia likuiditas **menarik kuotasi** karena menduga ada arus terinformasi,
> sehingga gerak berlanjut lebih jauh daripada yang dibenarkan informasinya.

**Lawan transaksi:** penyedia likuiditas yang menarik kuotasi saat menduga ada arus
terinformasi, dan peserta yang memasang order melawan level dan tersapu.

**Mati saat:** volatilitas datar berkepanjangan — semua breakout palsu, biaya menumpuk.

## Aturan yang mengikat

- **DILARANG memberi peringkat** (§O5). Grep `sort|argmax|idxmax|nlargest|max\(` → NOL.
- Setiap varian = **1 baris ledger**. Panel 1 hipotesis di 8 instrumen tetap **1 baris**.
- Semua fitur **wajib kausal** (§L1, §L2). Eksekusi paling cepat di pembukaan `t+1` (§L9).
- **Level breakout WAJIB dihitung dari jendela yang berakhir di bar `t`.** Level yang
  "digambar" dengan melihat ke depan adalah pelanggaran §L1 paling umum di keluarga ini.
- `E91_PELT` retrospektif → hanya boleh dipakai sebagai **umur segmen berjalan** yang
  kausal, bukan sebagai penanda titik balik (§L13a).
- `prior_sign = +` **DIPRA-REGISTRASI** (§O11).

## ⛔ Batas terhadap rumus ritel

| dilarang | kenapa | padanan legal di divisi ini |
|---|---|---|
| support/resistance manual | digambar tangan, tidak bisa diuji | `BRK02` (ambang EVT), `MOM11` (ekstrem jendela) |
| order block, fair value gap | tidak punya sumber, tidak punya turunan statistik | tidak ada — tetap dilarang |
| Donchian channel polos | parameternya tanpa pembenaran | `BRK01` (range sesi, jendela dari struktur pasar), `BRK04` |
| volume profile / POC | volume MT5 = tick count, bukan lot | **DILARANG TANPA PENGGANTI** |

**Yang membedakan `BRK01` dari "breakout garis manual":** jendela range-nya ditentukan
oleh **struktur sesi pasar** (pembukaan sesi — kejadian institusional nyata dengan
lonjakan likuiditas terukur), bukan dipilih karena terlihat bagus di chart. Ambangnya
diskala volatilitas, bukan angka tetap. Dan dia bisa gagal gerbang seperti kandidat lain.

## Daftar isi

| ID | Varian | n_param | Tier | Asal | Rumus (ringkas) |
|---|---:|---:|---|---|---|
| `BRK01_ORB_SESSION` 🔒🆕 | 4 | 2 | T1 | baru | tembus range N bar pertama sesi |
| `BRK02_POT_EXCEEDANCE` 🔒🆕 | 2 | 2 | T2 | baru | ambang EVT peaks-over-threshold pada range |
| `BRK03_VOL_CONTRACTION_EXPANSION` 🔒🆕 | 2 | 2 | T1 | baru | rasio σ pendek/panjang + pemicu ekspansi |
| `BRK04_RANGE_COMPRESSION_BREAK` 🆕 | 2 | 2 | T1 | baru | kompresi range → tembus batas kompresi |
| `BRK05_CUSUM_CHANGEPOINT` | 2 | 2 | T1 | E90 | `S⁺ = max(0, S⁺+(x−μ₀−k))` ; alarm `S⁺>h` |
| `BRK06_PELT_SEGMENTATION` | 1 | 2 | T2 | E91 | umur & arah segmen (kausal saja) |
| `BRK07_BOCPD_RUNLENGTH` | 1 | 3 | T2 | E92 | `P(r_t\|x_{1:t})` rekursif dengan hazard |

🔒 = tidak boleh dipangkas (§08 D1) · 🆕 = baru di v6

---

## Spesifikasi

### 🆕 `BRK01_ORB_SESSION` 🔒

```yaml
  - id: BRK01_ORB_SESSION
    division: E3
    family: BRK
    prior_sign: "+"
    division_type: direction
    status: BARU_V6
    tier: tier_1_murah
    formula: >
      Opening Range Breakout, didefinisikan per SESI (bukan per hari kalender):
        Sesi didefinisikan UTC: Asia 00:00-07:00, London 07:00-13:00, NY 13:00-21:00.
        Untuk sesi yang dimulai di bar t0:
          OR_hi = max( H_{t0 .. t0+N-1} )
          OR_lo = min( L_{t0 .. t0+N-1} )
          OR_range = OR_hi - OR_lo
        Untuk bar t > t0+N-1 di dalam sesi yang sama:
          sig = +1 kalau C_t > OR_hi + eps    (tembus ke atas)
                -1 kalau C_t < OR_lo - eps    (tembus ke bawah)
                 0 selain itu
          eps = eps_sigma * sigma_t   (sigma dari juara MCS divisi V — BUKAN ATR)

        SYARAT KELAYAKAN (wajib, bukan opsional):
          OR_range harus <= q_max * median(OR_range jendela latih).
          Range pembukaan yang sudah lebar berarti ekspansinya SUDAH terjadi —
          menembusnya berarti mengejar gerak yang sudah selesai. Kalau OR_range
          di atas ambang, sesi itu DILEWATI.

        Satu entry per sesi per arah. Exit di vertical barrier horizon ATAU akhir sesi,
        mana yang lebih dulu.
      Semua kuantitas dari bar yang SUDAH TUTUP (§L1). Median jendela latih saja (§L3).
    params: {N: [3, 6], eps_sigma: [0.10], q_max: [0.8, 1.0]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Pembukaan sesi memusatkan aliran order yang menumpuk selama jeda dan arah penembusan range awal mencerminkan sisi mana yang tekanannya belum selesai diserap, sehingga gerak berlanjut sampai tekanan itu habis"
      counterparty: "Penyedia likuiditas yang mengutip dua sisi di awal sesi tanpa tahu arah tekanan yang menumpuk, dan menanggung seleksi merugikan sampai menarik kuotasi atau melebarkan spread"
      decay: "Pemusatan aliran di pembukaan sesi adalah konsekuensi zona waktu pusat perdagangan yang tidak bisa dihapus, tapi ukuran efeknya menyusut saat lebih banyak peserta beroperasi 24 jam"
    provenance:
      citation: "Zarattini & Aziz, Can day trading really be profitable? Evidence of sustainable long-term profits from opening range breakout (ORB) day trading strategy vs benchmark in the US stock market, SSRN, 2023"
      ssrn_id: "4416622"
      verified: true
      peer_reviewed: false
      catatan_status: >
        SSRN working paper, BUKAN artikel peer-reviewed. Menurut §D2 dia boleh masuk
        screening tapi DILARANG masuk CONFIRM tanpa sumber peer-reviewed pendukung.
        Mekanisme dasarnya (pemusatan aliran di pembukaan) punya dukungan peer-reviewed
        lewat literatur intraday momentum (Gao-Han-Li-Zhou 2018, dipakai di MOM01).
        Kalau BRK01 lolos tahap 2, WAJIB dicari sumber peer-reviewed sebelum F9.
    catatan_transfer: >
      PERINGATAN JUJUR: sumbernya menguji ORB di EKUITAS AS dengan pembukaan lelang
      harian yang jelas. XAUUSD adalah OTC spot 24 jam TANPA lelang pembukaan.
      Analogi "pembukaan sesi" di sini lebih lemah daripada di ekuitas. Ini WAJIB
      ditulis di laporan F6. Kalau BRK01 gagal, penjelasan pertama yang harus diperiksa
      adalah ketiadaan struktur pembukaan yang sebenarnya, bukan kegagalan mekanismenya.
    catatan_anti_ritel: >
      Bedanya dengan "breakout garis manual": (a) jendela range dari struktur SESI —
      kejadian institusional dengan lonjakan likuiditas terukur, bukan dipilih karena
      terlihat bagus; (b) ambang diskala volatilitas, bukan pips tetap; (c) punya syarat
      kelayakan yang bisa MENOLAK memberi sinyal; (d) bisa gagal gerbang dan mati.
```

### 🆕 `BRK02_POT_EXCEEDANCE` 🔒

Ini padanan akademik yang benar untuk "harga menembus level penting". Levelnya
ditentukan **teori nilai ekstrem**, bukan digambar tangan.

```yaml
  - id: BRK02_POT_EXCEEDANCE
    family: BRK
    prior_sign: "+"
    division_type: direction
    status: BARU_V6
    tier: tier_2_sedang
    formula: >
      Peaks-Over-Threshold dengan distribusi Pareto Tergeneralisasi:
        LANGKAH 1 — ambang:
          u = kuantil-p dari |r| pada jendela latih yang berakhir di bar t   (p = 0.90 atau 0.95)
        LANGKAH 2 — fit GPD pada pelampauan:
          y_i = |r_i| - u  untuk semua |r_i| > u
          Fit GPD(xi, beta) pada {y_i} lewat maximum likelihood, jendela latih saja.
        LANGKAH 3 — level pemicu:
          Level pelampauan dengan periode ulang T_ret:
            x_T = u + (beta/xi) * ( (n/N_u * T_ret)^xi - 1 )
          n = jumlah observasi jendela, N_u = jumlah pelampauan
        ENTRY:
          sig = sign(r_t) kalau |r_t| >= x_T
                0 selain itu

        SYARAT KELAYAKAN:
          - N_u >= 30, kalau kurang -> fit tidak dapat dipercaya, SKIP
          - xi < 0.5, kalau lebih -> varians tak hingga, estimasi tidak stabil, SKIP
      Semua fit HANYA pada fold latih (§L3, §L4). Semua jendela berakhir di t (§L1).
    params: {p_threshold: [0.90, 0.95], T_ret: [50], fit_window: [576]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Gerak yang melampaui ambang ekstrem yang dikalibrasi dari distribusi ekornya sendiri menandakan kedatangan informasi yang belum terserap penuh, dan berbeda secara kualitatif dari gerak besar yang masih di dalam distribusi normalnya"
      counterparty: "Peserta yang memakai ambang tetap dalam pips atau persentase dan kalibrasinya rusak setiap kali rezim volatilitas berpindah, sehingga menandai gerak biasa sebagai luar biasa dan sebaliknya"
      decay: "Kalibrasi ekor adalah sifat statistik distribusi, bukan pola yang bisa dihapus arbitrase, tetapi ambangnya bergeser tiap rezim sehingga harus diestimasi ulang terus"
    provenance:
      citation: "Coles, An introduction to statistical modeling of extreme values, Springer Series in Statistics, 2001"
      doi: NEED_LOOKUP
      peer_reviewed: true
      catatan: "Buku teks standar EVT. Metode POT-GPD juga sudah dipakai di X10_POT_GPD_STOP v5."
    catatan_konsistensi: >
      v5 sudah memakai POT-GPD sebagai PENGGANTI Bollinger untuk STOP (X10_POT_GPD_STOP).
      BRK02 memakai mesin yang sama untuk ENTRY. Konsisten dengan tabel padanan
      akademik v5 sendiri, cuma di sisi yang belum pernah diuji.
    catatan_dedup: >
      Risiko korelasi terhadap BRK03 (dua-duanya bereaksi terhadap gerak besar).
      Bedanya: BRK02 mengambang pada BESARNYA gerak tunggal; BRK03 pada TRANSISI
      rezim volatilitas. Cek dedup 0.90 wajib.
```

### 🆕 `BRK03_VOL_CONTRACTION_EXPANSION` 🔒

```yaml
  - id: BRK03_VOL_CONTRACTION_EXPANSION
    family: BRK
    prior_sign: "+"
    division_type: direction
    status: BARU_V6
    tier: tier_1_murah
    formula: >
      Rasio volatilitas jangka pendek terhadap jangka panjang, plus pemicu ekspansi:
        v_t = sigma_pendek_t / sigma_panjang_t
        sigma dari juara MCS divisi V (F4) — BUKAN ATR.

        KEADAAN KONTRAKSI:  v_t <= q_low   (kuantil rendah jendela referensi)
        PEMICU EKSPANSI:    v_t menyeberang dari <= q_low ke >= q_trig

        sig = sign( r_{t-h:t} ) pada bar ketika pemicu terjadi
              0 selain itu
        h = jendela pendek penentu arah (arah ekspansi = arah gerak yang memicunya)

        Satu sinyal per episode kontraksi. Setelah memicu, TIDAK ADA sinyal lagi
        sampai v_t kembali ke bawah q_low. Ini mencegah satu episode ekspansi
        dihitung berkali-kali (yang akan meledakkan jumlah trade dan biaya).
      Semua kuantil dari jendela yang berakhir di t, di-fit pada fold latih (§L1, §L3).
    params: {n_pendek: [12, 24], n_panjang: [96], q_low: [0.25], q_trig: [0.75], h: [3]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Volatilitas berkelompok sehingga periode tenang diikuti periode aktif, dan pada saat transisi penyedia likuiditas belum menyesuaikan kuotasi terhadap rezim baru sehingga gerak berlanjut lebih jauh daripada yang dibenarkan informasinya"
      counterparty: "Penyedia likuiditas yang mengutip berdasarkan volatilitas terkini dan terlambat melebarkan spread ketika rezim berpindah, sehingga menanggung kerugian sampai kalibrasinya menyusul"
      decay: "Pengelompokan volatilitas adalah fakta stilisata yang paling kokoh di data keuangan dan tidak bisa diarbitrase habis, tetapi kecepatan penyesuaian penyedia likuiditas terus meningkat sehingga jendela keuntungannya menyempit"
    provenance:
      citation: "Bollerslev, Generalized autoregressive conditional heteroskedasticity, Journal of Econometrics, 1986"
      doi: NEED_LOOKUP
      peer_reviewed: true
      catatan: >
        Sitasi ini untuk FAKTA pengelompokan volatilitasnya, bukan untuk strategi
        perdagangannya. Strategi kontraksi-ekspansi sendiri TIDAK punya sumber
        peer-reviewed langsung yang saya verifikasi. Ditandai NEED_LOOKUP untuk
        sumber strategi. Boleh screening, DILARANG CONFIRM tanpa sumber (§D2).
```

### 🆕 `BRK04_RANGE_COMPRESSION_BREAK`

```yaml
  - id: BRK04_RANGE_COMPRESSION_BREAK
    family: BRK
    prior_sign: "+"
    division_type: direction
    status: BARU_V6
    tier: tier_1_murah
    formula: >
      Kompresi range diikuti penembusan batas kompresinya:
        R_t = max(H_{t-n+1..t}) - min(L_{t-n+1..t})       (range jendela n)
        c_t = R_t / median(R jendela referensi latih)     (rasio kompresi)

        KEADAAN TERKOMPRESI: c_t <= q_comp
        Saat terkompresi, catat batas:
          hi_c = max(H jendela n),  lo_c = min(L jendela n)

        sig = +1 kalau C_t > hi_c + eps_sigma*sigma_t
              -1 kalau C_t < lo_c - eps_sigma*sigma_t
               0 selain itu
        Batas hi_c/lo_c DIBEKUKAN pada saat kompresi terdeteksi dan tidak diperbarui
        sampai penembusan terjadi atau kompresinya berakhir.
      Semua dari jendela yang berakhir di t (§L1). Median dari fold latih (§L3).
    params: {n: [24, 48], q_comp: [0.5], eps_sigma: [0.10]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Range yang menyempit menandakan keseimbangan sementara antara pembeli dan penjual dan penembusan batasnya menandakan keseimbangan itu pecah, sehingga posisi yang dibangun di dalam range terpaksa disesuaikan serentak"
      counterparty: "Peserta yang membangun posisi melawan batas range dengan asumsi range bertahan, dan terpaksa menutup serentak ketika batasnya tidak bertahan"
      decay: "Perilaku membangun posisi di dalam range adalah strategi yang selalu punya peserta, tapi ukuran dislokasinya bergantung berapa banyak modal yang terjebak di dalamnya"
    provenance:
      citation: NEED_LOOKUP
      doi: NEED_LOOKUP
      peer_reviewed: false
      catatan_kejujuran: >
        SAYA TIDAK MENEMUKAN sumber peer-reviewed untuk bentuk ini secara spesifik.
        Ditulis NEED_LOOKUP sesuai §D1 — DILARANG mengarang sitasi.
        Konsekuensi §D2: boleh screening, DILARANG masuk CONFIRM sampai sumber ketemu.
        Kalau tidak ketemu sampai F3, kandidat ini masuk rejected_log dengan alasan
        "tidak ada sumber terverifikasi", BUKAN dijalankan dengan sitasi karangan.
      kandidat_pencarian: "literatur volatility clustering, range-based trading, Taylor effect"
```

### `BRK05_CUSUM_CHANGEPOINT`

```yaml
  - id: BRK05_CUSUM_CHANGEPOINT
    v5_id: E90_CUSUM_CHANGEPOINT
    family: BRK
    prior_sign: "+"
    division_type: direction
    tier: tier_1_murah
    formula: >
      S_t^+ = max(0, S_{t-1}^+ + (x_t - mu0 - k))    ; alarm saat S_t^+ > h
      S_t^- = min(0, S_{t-1}^- + (x_t - mu0 + k))    ; alarm saat S_t^- < -h
      🔄 v6 menetapkan: sig = +1 pada alarm sisi positif, -1 pada alarm sisi negatif.
      v5 tidak menetapkan arah secara eksplisit. Arah ditetapkan dan DIPRA-REGISTRASI:
      alarm CUSUM menandakan pergeseran mean SEDANG BERLANGSUNG, jadi arahnya
      mengikuti tanda pergeseran (kelanjutan), bukan melawannya.
      mu0 dan skala x dari fold latih saja (§L3).
    params: {k_mult: [0.5, 1.0], h_mult: [5.0]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Statistik jumlah kumulatif mendeteksi pergeseran rata-rata return secepat mungkin secara teori sehingga awal fase terarah ditandai lebih awal daripada oleh penghalus"
      counterparty: "Peserta yang menunggu konfirmasi rata-rata bergerak dan selalu masuk setelah sebagian besar pergeseran sudah terjadi"
      decay: "Ambang deteksi menentukan pertukaran antara kecepatan dan sinyal palsu, tidak ada setelan unggul di semua rezim"
    provenance:
      citation: "Page, Continuous inspection schemes, Biometrika, 1954"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### `BRK06_PELT_SEGMENTATION`

```yaml
  - id: BRK06_PELT_SEGMENTATION
    v5_id: E91_PELT_SEGMENTATION
    family: BRK
    prior_sign: "+"
    division_type: direction
    tier: tier_2_sedang
    formula: >
      min SUM_i [ C(y_{t_{i-1}+1:t_i}) + beta ] dengan pemangkasan
      fitur = UMUR SEGMEN BERJALAN dan ARAH SEGMEN
      sig = sign(arah segmen berjalan) * 1( umur_segmen <= umur_maks )
      Sinyal hanya aktif di AWAL segmen baru — segmen tua berarti gerakannya sudah selesai.
    params: {beta_mult: [1.5], min_seg: [12], umur_maks: [12]}
    variants: 1
    n_parameters: 2
    data_required: [ohlc]
    peringatan_L13a: >
      ⛔ PELT adalah algoritma RETROSPEKTIF — dia menemukan titik perubahan optimal
      dengan melihat SELURUH deret. Memakainya apa adanya sebagai fitur live adalah
      pelanggaran §L1 yang paling halus dan paling sering lolos tanpa ketahuan.
      YANG DIIZINKAN: jalankan PELT hanya pada data <= t, ambil UMUR SEGMEN TERAKHIR
      yang sedang berjalan. DILARANG memakai posisi titik balik yang ditandai
      belakangan setelah data sesudahnya terlihat.
      Uji wajib: bandingkan fitur versi kausal vs versi retrospektif. Versi
      retrospektif HARUS jauh lebih baik. Kalau sama -> implementasi kausalnya bocor.
    mechanism:
      claim: "Segmentasi PELT menemukan titik perubahan optimal secara eksak dengan biaya linier sehingga seluruh riwayat bisa disegmentasi ulang tiap bar tanpa aproksimasi"
      counterparty: "Peserta yang memakai segmentasi heuristik dan mendapat batas segmen berbeda tergantung urutan pemrosesan"
      decay: "Hasil bergantung penalti yang harus dikalibrasi terhadap derau sampel"
    provenance:
      citation: "Killick, Fearnhead & Eckley, Optimal detection of changepoints with a linear computational cost, Journal of the American Statistical Association, 2012"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### `BRK07_BOCPD_RUNLENGTH`

```yaml
  - id: BRK07_BOCPD_RUNLENGTH
    v5_id: E92_BOCPD_RUNLENGTH
    family: BRK
    prior_sign: "+"
    division_type: direction
    tier: tier_2_sedang
    formula: >
      P(r_t | x_1:t) rekursif dengan fungsi hazard H(r)
      fitur = E[r_t] = umur rezim terprediksi
      sig = sign( r_{t-h:t} ) * 1( P(r_t < r_baru) >= p_min )
      Yaitu: ambil arah gerak terkini HANYA ketika probabilitas bahwa rezim baru
      saja dimulai cukup tinggi. BOCPD KAUSAL secara konstruksi — itu keunggulannya
      dibanding PELT.
    params: {hazard: [0.01], p_min: [0.5], h: [3]}
    variants: 1
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Deteksi titik perubahan daring Bayesian menghasilkan distribusi panjang run sehingga memberi probabilitas bukan keputusan biner tentang umur rezim berjalan"
      counterparty: "Peserta yang memakai deteksi biner dan berpindah strategi penuh pada sinyal yang masih sangat tidak pasti"
      decay: "Kualitas hasil bergantung spesifikasi hazard dan prior yang harus dibenarkan tiap sampel"
    provenance:
      citation: "Adams & MacKay, Bayesian online changepoint detection, arXiv preprint arXiv:0710.3742, 2007"
      doi: NEED_LOOKUP
      peer_reviewed: false
      catatan: >
        arXiv preprint. §D2 menerima DOI / SSRN ID / NBER WP — arXiv ID BUKAN salah satunya.
        Boleh screening, DILARANG CONFIRM sampai sumber peer-reviewed ditemukan.
```

---

## Catatan biaya khusus keluarga BRK

Keluarga ini punya masalah biaya yang **spesifik dan wajib diukur eksplisit**:

> **Breakout masuk justru saat volatilitas melonjak — yaitu saat spread paling lebar.**

Interaksi dengan `Q10_SPREAD_PERCENTILE_GATE` bisa mematikan seluruh keluarga ini.

**Wajib dilaporkan di F6 untuk setiap kandidat BRK:**

1. proporsi sinyal yang **diblokir** gerbang biaya `Q10`
2. expectancy sinyal yang lolos gerbang vs yang diblokir
3. `kappa` rata-rata **pada bar entry BRK**, dibandingkan `kappa` rata-rata keseluruhan

Kalau >80% sinyal diblokir gerbang biaya, keluarga BRK **tidak bisa dijalankan** pada
struktur biaya prop firm — dan itu **temuan yang wajib dilaporkan**, bukan alasan
melonggarkan gerbang biaya.

---

## Catatan pemangkasan

Urutan pemangkasan divisi ini (§08 D2):

1. `BRK06`, `BRK07` (tier-2) — potong pertama
2. `BRK04` (sitasi `NEED_LOOKUP`, paling lemah dasarnya) — potong kedua
3. `BRK05` → 1 varian
4. **Lantai: `BRK01`, `BRK02`, `BRK03` @ 1 varian = 3 varian.** Ketiganya mewakili tiga
   mekanisme berbeda: struktur sesi, ambang ekstrem, dan transisi volatilitas.
