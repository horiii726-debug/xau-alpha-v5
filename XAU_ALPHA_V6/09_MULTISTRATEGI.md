# 09 — MULTI-STRATEGI: MOMENTUM / MEAN REVERSION / BREAKOUT

> 🔄 File baru. Ini permintaan utama Anda: *"jadikan semua jadi multi-strategi,
> Momentum / Mean Rev / Breakout, biar tidak patokan di satu kondisi market."*
>
> Yang membuat ini bisa dikerjakan tanpa merusak statistiknya adalah **divisi S**
> (§08 C3) — 29 pendeteksi rezim yang di v5 salah ditempatkan sebagai sinyal arah.
> Bahannya sudah ada sejak v5. Yang belum ada: tempat yang benar untuk memakainya.

---

## Bagian A — Kenapa satu strategi selalu kalah

Sampel v5 (2021–2026) hanya memuat satu rezim: **emas naik**. Hasil F2 memperlihatkannya
telanjang — sisi long menang ~20 poin persen, sisi short hampir tidak pernah.

Sistem yang disetel di satu rezim akan:

- terlihat hebat di backtest rezim itu
- mati begitu rezimnya berganti
- dan Anda **tidak akan tahu** sampai uangnya sudah masuk

Multi-strategi bukan soal punya lebih banyak sinyal. **Ini soal punya sinyal yang
mekanisme untungnya berbeda, sehingga rezim yang mematikan satu keluarga justru
menghidupkan keluarga lain.**

---

## Bagian B — Tiga keluarga

Tiap kandidat arah WAJIB mendeklarasikan keluarganya (§O11). Satu keluarga saja.

```yaml
families:

  MOM:
    nama: "Momentum / kelanjutan arah"
    mekanisme_untung: >
      Aliran order besar dipecah dan dieksekusi bertahap. Jejaknya tidak bisa
      dihilangkan tanpa membayar dampak harga lebih besar. Anda dibayar karena
      menyediakan kelanjutan harga bagi pihak yang WAJIB menyelesaikan eksekusi.
    lawan_transaksi: "manajer yang harus menyelesaikan eksekusi besar dalam jendela waktu tetap"
    prior_regime: "persisten (VR > 1, Hurst > 0.5), volatilitas EKSPANSI, drift burst aktif"
    prior_sign: "+"    # kinerja MOM NAIK saat persistensi naik
    mati_saat: "pasar ranging — tiap entry kelanjutan langsung dibalik"

  MRV:
    nama: "Mean reversion / pembalikan overextension"
    mekanisme_untung: >
      Peserta yang menuntut eksekusi SEGERA membayar konsesi harga kepada penyedia
      likuiditas. Anda dibayar sebagai penampung inventori. Kompensasinya adalah
      biaya modal nyata — tidak hilang selama modal tidak gratis.
    lawan_transaksi: "peserta yang menuntut likuiditas segera dan membayar premi untuk itu"
    prior_regime: "anti-persisten (VR < 1), volatilitas NORMAL/kontraksi, spread pulih cepat"
    prior_sign: "-"    # kinerja MRV TURUN saat persistensi naik
    mati_saat: "tren kuat — 'murah' terus jadi lebih murah"
    peringatan_keras: >
      Bentuk mean-reversion yang DILARANG: harga vs rata-rata bergulirnya sendiri
      (= Bollinger / VWAP band / Kalman anchor). Sudah diuji, mati total, persentil
      permutasi 2.7%. Lihat §02. MRV di v6 memakai residual lintas-seksi dan
      kompensasi likuiditas — mekanisme yang berbeda, bukan nama yang berbeda.

  BRK:
    nama: "Breakout / ekspansi range"
    mekanisme_untung: >
      Volatilitas berkelompok. Setelah kontraksi, ekspansi datang; dan pada saat
      ekspansi, penyedia likuiditas menarik kuotasi sehingga gerak berlanjut lebih
      jauh daripada yang dibenarkan informasinya.
    lawan_transaksi: "penyedia likuiditas yang menarik kuotasi saat menduga ada arus terinformasi"
    prior_regime: "volatilitas KONTRAKSI diikuti ekspansi, changepoint baru, batas sesi"
    prior_sign: "+"    # kinerja BRK NAIK saat transisi kontraksi->ekspansi
    mati_saat: "volatilitas datar berkepanjangan — semua breakout palsu"
```

### Kenapa tiga ini, bukan lima atau dua

Tiga keluarga ini **menghabiskan ruang mekanisme** untuk trading harga murni:
harga bergerak searah (MOM), harga kembali (MRV), atau harga berpindah rezim (BRK).
Keluarga keempat manapun akan berkorelasi tinggi dengan salah satu dari tiga ini —
dan §06 Bagian C (`vs_cross_family`) akan menangkapnya sebagai duplikat.

---

## Bagian C — Router: bagaimana ketiganya digabung

### C1 — Tiga opsi, dan kenapa dua di antaranya salah

| opsi | cara kerja | masalah |
|---|---|---|
| **(a) Hard switch** | hanya satu keluarga aktif per rezim | **Membelah eff N.** 3 rezim = tiap keluarga cuma dapat 1/3 sampel. Persis peringatan `VIEW_REZIM` v5 sendiri. Dan salah klasifikasi rezim = nol posisi di saat yang salah. |
| **(b) Bobot sama selalu** | ketiganya jalan terus, bobot tetap | Tidak fleksibel — persis yang Anda minta dihindari. Dan keluarga yang sedang mati menyeret yang sedang hidup. |
| **(c) Bounded tilt** ✅ | ketiganya **selalu** dialokasikan; bobot dimiringkan mengikuti rezim, tapi **dijepit** | **Ini yang dipakai.** |

### C2 — `RTR01_BOUNDED_TILT`

```yaml
router:
  id: RTR01_BOUNDED_TILT
  division: ROUTER
  division_type: direction
  ledger: ledger_arah
  variants: 2
  n_parameters: 2

  formula: >
    Bobot dasar tiap keluarga f:
      w0_f = risk_parity(f) = (1/sigma_f) / SUM_g (1/sigma_g)
      sigma_f = volatilitas PnL keluarga f, jendela bergulir KAUSAL

    Skor rezim tiap keluarga (dari divisi S, semua kausal):
      s_f(t) = SUM_j beta_fj * z_j(t)
      z_j    = fitur rezim ke-j, distandardisasi pakai kuantil jendela LATIH saja
      beta_fj TANDANYA DIPRA-REGISTRASI dari prior_sign keluarga f (§O11)

    Tilt yang DIJEPIT:
      m_f(t) = clip( 1 + lambda * tanh(s_f(t)), 1-c, 1+c )
      c = 0.5    <- JEPITAN. Tidak ada keluarga yang pernah di bawah 0.5x atau di atas 1.5x
      lambda = 1.0

    Bobot akhir:
      w_f(t) = w0_f * m_f(t) / SUM_g (w0_g * m_g(t))

  params: {lambda: [0.5, 1.0], c: [0.5]}

  sifat_yang_membuat_ini_aman:
    tidak_membelah_effN: >
      Tiap keluarga TETAP dievaluasi di SELURUH sampel. Tilt mengubah bobot,
      tidak mematikan keluarga. eff N tiap keluarga utuh.
    fleksibel_tapi_terbatas: >
      Jepitan 0.5x-1.5x berarti keluarga terlemah tetap dapat sepertiga bobot
      relatif terhadap yang terkuat. Rezim salah klasifikasi TIDAK pernah
      menghasilkan nol eksposur ke keluarga yang sebenarnya benar.
    anggaran_parameter_kecil: >
      lambda dan c = 2 parameter bebas. Tanda beta DIPRA-REGISTRASI, bukan di-fit
      bebas. Ruang overfitnya kecil dibandingkan hard-switch yang butuh ambang
      per rezim per keluarga.
    satu_hipotesis: >
      Seluruh portofolio multi-strategi = 1 HIPOTESIS = 2 baris ledger (2 varian
      lambda). BUKAN 3 x N. Ini yang membuat multi-strategi muat di anggaran 81.
```

### C3 — Fitur rezim yang masuk router

Semua dari divisi S / V / Q, semua **hanya yang lolos MCS di F4**. Router **tidak boleh**
memakai fitur rezim yang belum lolos gerbangnya sendiri.

> ⚠️ **`S_CHANGEPOINT_AGE` adalah fitur DIVISI S, bukan keluaran `BRK05`/`BRK07`.**
> Mesin deteksinya sama (CUSUM / BOCPD) tapi yang dipakai router adalah **umur segmen
> berjalan** — besaran keadaan, dihitung kausal, dinilai di `ledger_estimasi` lewat MCS.
> **DILARANG** memasukkan keluaran kandidat arah (`BRK05`/`BRK07`) sebagai fitur router:
> itu memakai hasil seleksi arah untuk membobot arah — melingkar, dan bocor.

| sumbu | fitur | MOM | MRV | BRK |
|---|---|:---:|:---:|:---:|
| persistensi | juara MCS keluarga VR/Hurst/DFA | **+** | **−** | 0 |
| transisi volatilitas | `sigma_pendek / sigma_panjang` dari juara MCS divisi V | **+** | 0 | **+** |
| level volatilitas | juara MCS divisi V | 0 | **−** | 0 |
| kebaruan changepoint | `S_CHANGEPOINT_AGE` — umur segmen berjalan, dihitung KAUSAL di divisi S | 0 | **+** | **−** |
| resiliensi spread | `Q09_SPREAD_RESILIENCY` | 0 | **+** | 0 |

**Tanda di tabel ini DIPRA-REGISTRASI.** Di-hash sebelum F0. Kandidat yang hasilnya
bagus tapi dengan tanda terbalik → `SIGN_FLIP_SUSPECT`, **tidak boleh masuk CONFIRM**
(§O11). Itu yang membedakan "menemukan efek yang diprediksi" dari "mengaduk data".

### C4 — Gerbang biaya mengalahkan router

```yaml
gerbang_keras_biaya:
  aturan: >
    Kalau kappa_t (Q08) > kuantil-75 jendela referensi ATAU Q10_SPREAD_PERCENTILE_GATE = 0,
    SELURUH keluarga -> bobot NOL. Tidak ada entry, apapun kata router.
  alasan: >
    Ini bukan keputusan alokasi, ini keputusan kelayakan. Edge setipis IC 0.05
    tidak selamat dari eksekusi di persentil biaya teratas. Gerbang biaya dievaluasi
    SEBELUM router, dan menimpanya.
```

---

## Bagian D — Cara menguji router tanpa menipu diri sendiri

Router **wajib** mengalahkan tiga null. Semuanya di §06 Bagian A.

| null | apa yang diuji | arti kalau router kalah |
|---|---|---|
| **N1_EQUAL_WEIGHT_STATIC** | apakah informasi rezim menambah nilai | Router tidak berguna. Pakai bobot sama, catat, selesai. |
| **N2_BEST_SINGLE_FAMILY** (via MCS, bukan argmax) | apakah diversifikasi keluarga terbayar | Jalankan satu keluarga saja. |
| **N3_REGIME_SHUFFLE** ⭐ | **apakah deteksi rezimnya nyata** | **Yang paling penting.** Keunggulan router berasal dari struktur alokasi, bukan dari deteksi rezim. Buang routernya. |

```yaml
N3_REGIME_SHUFFLE:
  prosedur: >
    Acak deret label rezim dengan BLOCK SHUFFLE yang mempertahankan distribusi
    durasi rezim. Jalankan router dengan label palsu itu. Ulangi 1000 kali.
  gate: "router asli di atas persentil 95 dari distribusi N3"
  kenapa_block_shuffle: >
    Per-bar shuffle akan menghancurkan persistensi rezim dan membuat null terlalu
    lemah — router akan menang karena alasan yang salah (dia diuntungkan oleh
    label yang persisten, bukan oleh label yang BENAR).
```

### Uji tambahan: interaksi berarah

```yaml
uji_interaksi_prior:
  tujuan: "Apakah tiap keluarga benar-benar menang di rezim yang diprediksi?"
  prosedur: >
    Untuk tiap keluarga f, regresikan PnL_f terhadap fitur rezim yang relevan.
    Koefisien interaksinya HARUS bertanda sama dengan prior_sign yang dipra-registrasi.
  hasil:
    tanda_benar_signifikan: "bukti KONFIRMATORI. Tandanya diprediksi sebelum melihat data."
    tanda_benar_tidak_signifikan: "tidak ada bukti. Router turun jadi bobot sama (N1)."
    tanda_TERBALIK: >
      GAGAL. Ditandai SIGN_FLIP_SUSPECT. DILARANG membalik prior dan menyebutnya
      penemuan — itu mengaduk data. Kalau ada alasan teoretis kuat untuk membalik,
      itu HIPOTESIS BARU yang wajib dipra-registrasi ulang dan diuji di data
      yang belum disentuh.
```

---

## Bagian E — Alokasi tanpa melanggar §O5

Aturan `forbid_argmax` berlaku penuh di divisi arah. Router **tidak melanggarnya**:

```yaml
kepatuhan_O5:
  yang_dilarang: "memilih PERINGKAT 1 dari daftar kandidat berdasarkan kinerja"
  yang_dilakukan_router: >
    Membobot SELURUH keluarga yang LOLOS AMBANG, dengan bobot dari (a) risk parity —
    fungsi volatilitas, bukan kinerja; dan (b) tilt rezim — fungsi keadaan pasar
    dengan tanda yang dipra-registrasi, bukan fungsi kinerja.
  tidak_ada_pemilihan_pemenang: >
    Tidak ada keluarga yang "menang". Yang lolos ambang masuk portofolio.
    Yang tidak lolos tidak masuk. Tidak ada sort, tidak ada argmax, tidak ada max().
  pemeriksaan_wajib: >
    grep -nE "sort|argmax|idxmax|nlargest|max\(" src/router/
    Harus NOL hasil. Sama seperti select_champion().

  catatan_risk_parity: >
    Bobot 1/sigma memakai volatilitas PnL, BUKAN Sharpe atau return. Volatilitas
    bisa diestimasi jauh lebih andal daripada mean di sampel terbatas — itu
    alasan risk parity dipakai, bukan karena dia optimal.
```

---

## Bagian F — Kalau cuma satu keluarga yang lolos

Kemungkinan nyata, dan harus ada aturannya sebelum hasilnya keluar.

```yaml
skenario_hasil:
  tiga_keluarga_lolos:
    aksi: "Jalankan router penuh. Ini hasil terbaik yang mungkin."
  dua_keluarga_lolos:
    aksi: >
      Jalankan router dengan 2 keluarga. Jepitan tetap 0.5x-1.5x.
      Catat bahwa keluarga ketiga tidak lolos dan di rezim apa dia seharusnya menang —
      itu memberi tahu rezim mana yang tidak tercakup.
  satu_keluarga_lolos:
    aksi: >
      TIDAK ADA ROUTER. Jalankan keluarga tunggal itu apa adanya.
      DILARANG memaksa keluarga yang gagal masuk portofolio demi 'diversifikasi'.
      Diversifikasi ke dalam strategi yang tidak terbukti bukan diversifikasi —
      itu menambah biaya tanpa menambah edge.
    wajib_dilaporkan: >
      "Sistem ini TIDAK multi-strategi. Dia strategi tunggal keluarga X, dan
      akan mati kalau rezim yang menguntungkannya berakhir." Ditulis apa adanya.
  nol_keluarga_lolos:
    aksi: "protokol_nol_lolos §07 Bagian E, mulai dari langkah 0 (periksa alat dulu)."
```

> **Peringatan jujur.** Anda meminta sistem yang fleksibel di semua kondisi pasar.
> v6 membangun kerangkanya dengan benar. Tapi kerangka itu **tidak bisa menciptakan**
> keluarga yang bekerja — dia hanya bisa menggabungkan keluarga yang terbukti bekerja.
> Kalau hanya satu keluarga yang lolos, jawaban jujurnya adalah "sistem ini tidak
> multi-strategi", **bukan** memasukkan dua keluarga gagal supaya terlihat lengkap.

---

## Bagian G — Urutan kerja

```
F4   divisi S & V & Q -> fitur rezim mana yang lolos MCS
      |
      +-> hanya yang LOLOS yang boleh masuk router
F5   divisi X — exit & sizing (prioritas mengikuti hasil F2, lihat §05 C2)
F6   tiga keluarga E diuji TERPISAH, masing-masing lewat corong penuh
      |
      +-> tiap keluarga dapat vonis sendiri: SHORTLIST / KANDIDAT / gugur
F7   divisi M — meta-labeling di atas keluarga yang lolos
F7b  ROUTER — digabung, diuji terhadap N1/N2/N3
      |
      +-> router hanya diuji kalau >= 2 keluarga lolos tahap 2
F8   freeze & pre-register (termasuk tanda prior router)
F9   CONFIRM
```

**Aturan mengikat:** router **tidak boleh** dijalankan sebelum keluarga-keluarganya
punya vonis sendiri. Menggabungkan dulu lalu menguji belakangan berarti Anda tidak
akan pernah tahu keluarga mana yang membawa hasilnya.

---

**Lanjut ke `10_FASE_EKSEKUSI.md`.**
