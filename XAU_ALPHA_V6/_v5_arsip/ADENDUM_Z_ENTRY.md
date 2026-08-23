# ADENDUM Z — KANDIDAT Z-SCORE UNTUK ENTRY (TAMBAHAN BARU)

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
>
> 🆕 **INI SATU-SATUNYA FILE YANG BERISI KONTEN BARU.** Semua file lain di paket ini adalah
> pemecahan verbatim dari sumber. Di sini ada 3 formula yang **belum ada** di registry v5.
> Statusnya: **USULAN, BELUM DISETUJUI.** Tidak boleh masuk ledger sebelum §Z.4 diselesaikan.

---

## Z.0 — Kenapa file ini ada

Permintaan: *"kalau rumus z-score tidak ada, ambil kandidat baru yang fungsinya untuk entry."*

Hasil pencarian di seluruh 3.352 baris `XAU_ALPHA_V5.yaml`:

```
grep -i "zscore|z_score|z-score"  →  0 hasil
```

Benar, tidak ada. Jadi ini memang tambahan, bukan penulisan ulang.

---

## Z.1 — Peringatan yang harus dibaca lebih dulu

Saya tidak akan menambahkan z-score dalam bentuk yang paling umum dipakai orang, karena
**bentuk itu dilarang oleh sistem Anda sendiri**, dan saya diminta tidak mengubah sistemnya.

Bentuk yang dilarang:

```
z_t = (P_t − MA_n(P)) / sigma_n(P)      →  beli kalau z < −2, jual kalau z > +2
```

Itu **Bollinger Bands ditulis ulang dengan notasi statistik**. Tiga pasal yang dilanggar sekaligus:

| Pasal | Bunyinya |
|---|---|
| `laws.anti_rumus_ritel.dilarang_total` | "Bollinger Bands" — terdaftar eksplisit |
| `laws.anti_rumus_ritel.vwap_dan_kalman.dilarang` | "DILARANG dipakai sebagai anchor mean-reversion (sinyal 'harga jauh dari VWAP/Kalman maka balik arah')" |
| `lessons_carried.9` | "VWAP-band dan keluarga Kalman sebagai anchor mean-reversion **sudah diuji dan mati total**" |

Angka dari riset Anda sebelumnya untuk bentuk ini: **persentil permutasi 2.7%** — bukan sekadar
tidak signifikan, tapi **lebih buruk daripada acak**, dan mati di kelima uji robustness.

Menamainya "z-score" tidak mengubah apapun. Rumusnya identik. Kalau saya menambahkannya,
saya menambahkan bangkai yang sudah dikubur dua kali dan memberinya nama baru. Itu bukan
menuruti permintaan — itu membakar uang Anda dengan sopan.

**Jadi yang saya tambahkan adalah tiga bentuk z-score yang tidak melanggar satupun pasal di atas,
dan fungsinya tetap untuk entry.** Bedanya ada di *apa yang di-z-score-kan*:

| Bentuk | Yang di-standardisasi | Vonis |
|---|---|---|
| Bollinger terselubung | **harga** terhadap rata-rata bergulirnya sendiri | ⛔ dilarang, sudah mati |
| `Z01` | **nilai sinyal** yang sudah ada, untuk menyaring kekuatannya | ✅ boleh — lapisan normalisasi |
| `Z02` | **lintas instrumen** pada satu titik waktu | ✅ boleh — riset faktor standar |
| `Z03` | **selisih** XAU terhadap median panel | ✅ boleh — momentum lintas-aset |

`Z02` dan `Z03` bukan penemuan saya — itu bentuk baku riset faktor institusional (peringkat
lintas-aset pada tiap tanggal), dan kebetulan **justru memakai arsitektur panel 25 instrumen yang
sudah Anda bangun** di §universe. Aset yang sudah dibayar tapi belum dipakai untuk entry.

---

## Z.2 — Spesifikasi formula

Format mengikuti persis blok `formulas:` di sumber, supaya bisa langsung di-append kalau disetujui.

### `Z01_ROBUST_MAD_ZSCORE_GATE`

```yaml
  - id: Z01_ROBUST_MAD_ZSCORE_GATE
    division: E
    division_type: direction
    status: USULAN_BARU_V5_ADENDUM_Z      # belum masuk registry resmi
    formula: >
      Modified z-score Iglewicz-Hoaglin atas NILAI SINYAL (bukan atas harga):
      m_t   = median( s_{t-n+1..t} )
      MAD_t = median( |s_i - m_t| ), i = t-n+1..t
      z_t   = 0.6745 * (s_t - m_t) / MAD_t
      s = keluaran sinyal kandidat divisi E yang SUDAH lolos gerbang, bukan harga.
      Entry hanya diambil kalau |z_t| >= tau. Arah tetap ditentukan oleh sinyal aslinya,
      TIDAK dibalik. Ini gerbang kekuatan sinyal, bukan sinyal mean-reversion.
      Semua kuantitas dihitung dari jendela yang berakhir di bar t (kausal, §L1).
      Konstanta 0.6745 = Phi^{-1}(0.75), menyetarakan MAD dengan sigma pada distribusi normal.
      MAD_t = 0 -> sinyal dilewati (tidak ada trade), JANGAN dibagi epsilon.
    params: {window: [48, 96, 288], tau: [1.0, 1.5, 2.0]}
    variants: 9
    n_parameters: 2
    data_required: [ohlc]
    fitur_input: "keluaran sinyal kandidat divisi E yang lolos F6"
    mechanism:
      claim: "Median dan MAD tidak terpengaruh satu bar ekstrem, sehingga ambang kekuatan sinyal tidak melar tepat setelah bar berita ketika standar deviasi biasa melonjak dan mematikan sinyal justru di saat geraknya paling besar"
      counterparty: "Peserta yang menormalkan sinyalnya dengan mean dan standar deviasi biasa, lalu ambangnya bergeser sendiri setiap ada satu outlier dan sistemnya berhenti mengambil trade di kondisi yang justru paling menguntungkan"
      decay: "Ketahanan terhadap outlier adalah sifat matematis estimator, bukan pola pasar, sehingga tidak bisa diarbitrase habis oleh pelaku lain"
    provenance:
      citation: "Iglewicz & Hoaglin, How to Detect and Handle Outliers, ASQC Basic References in Quality Control vol 16, 1993"
      doi: NEED_LOOKUP
      peer_reviewed: true
    tier: tier_1_murah
    catatan_dedup: >
      Risiko korelasi terhadap E02_VOL_SCALED_MOMENTUM. Bedanya: E02 menskala RETURN dengan
      volatilitas; Z01 menstandardisasi NILAI SINYAL dengan median/MAD dan dipakai sebagai
      gerbang, bukan sebagai sinyal arah. Kalau korelasi PnL >= 0.90 terhadap E02 -> alias,
      tidak masuk registry (§dedup). Diputuskan oleh angka, bukan oleh argumen ini.
```

### `Z02_CROSS_SECTIONAL_PANEL_ZSCORE`

```yaml
  - id: Z02_CROSS_SECTIONAL_PANEL_ZSCORE
    division: E
    division_type: direction
    status: USULAN_BARU_V5_ADENDUM_Z
    formula: >
      Standardisasi LINTAS INSTRUMEN pada tiap timestamp, bukan lintas waktu:
      Pada bar t, untuk K instrumen panel dengan nilai sinyal s_{k,t}:
      mu_t    = median_k( s_{k,t} )
      MAD_t   = median_k( |s_{k,t} - mu_t| )
      z_{k,t} = 0.6745 * (s_{k,t} - mu_t) / MAD_t
      Entry long pada instrumen dengan z >= +tau, short pada z <= -tau.
      TIDAK ada informasi masa depan: seluruh nilai berasal dari bar t yang sudah tutup
      di seluruh instrumen (§L1). Instrumen yang barnya belum tutup pada t karena beda
      jam sesi WAJIB dikeluarkan dari perhitungan lintas-seksi bar itu, bukan di-forward-fill.
      Timestamp diselaraskan ke UTC dan hanya bar dengan penutupan yang benar-benar
      terjadi <= t yang ikut. Ini syarat kausalitas yang paling mudah dilanggar di formula ini.
    params: {signal_window: [48, 96], tau: [1.0, 1.5]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    fitur_input: "sinyal yang sama diterapkan ke seluruh instrumen panel"
    mechanism:
      claim: "Standardisasi lintas seksi membuang komponen yang bergerak bersama di seluruh panel dan menyisakan komponen khas instrumen, sehingga yang diuji adalah sinyal murni dan bukan beta pasar yang menyamar jadi sinyal"
      counterparty: "Peserta yang menilai tiap instrumen sendiri-sendiri dan mengambil posisi yang sebenarnya cuma taruhan arah dolar atau arah risiko global, lalu menanggung risiko faktor yang tidak pernah dia niatkan"
      decay: "Peringkat lintas seksi berubah tiap bar dan tidak menghasilkan level tetap yang bisa dihafal peserta lain, tetapi keuntungannya menyusut kalau panelnya menyempit"
    provenance:
      citation: "Asness, Moskowitz & Pedersen, Value and momentum everywhere, Journal of Finance, 2013"
      doi: NEED_LOOKUP
      peer_reviewed: true
    tier: tier_1_murah
    catatan_arsitektur: >
      Formula ini memakai panel 25 instrumen yang SUDAH dibangun di §universe untuk keperluan
      K_eff. Tidak butuh data baru, tidak butuh instrumen baru, tidak butuh biaya komputasi
      di luar yang sudah dianggarkan.
    catatan_biaya: >
      PERINGATAN: entry lintas-seksi berarti trading di instrumen SELAIN XAUUSD. Model biaya
      per instrumen (spread, komisi, swap) WAJIB sudah terisi di F0 untuk setiap instrumen yang
      bisa kena entry. Instrumen tanpa data biaya TIDAK BOLEH dieksekusi, hanya boleh jadi
      bagian dari perhitungan lintas-seksi (§universe.langkah_wajib_fase_0).
```

### `Z03_ZSCORE_DIVERGENCE_XAU_VS_PANEL`

```yaml
  - id: Z03_ZSCORE_DIVERGENCE_XAU_VS_PANEL
    division: E
    division_type: direction
    status: USULAN_BARU_V5_ADENDUM_Z
    formula: >
      Selisih z-score lintas-seksi XAU terhadap median panel:
      d_t = z_{XAU,t} - median_k( z_{k,t} )
      dengan z_{k,t} dari Z02.
      Entry long kalau d_t >= +tau, short kalau d_t <= -tau.
      Arah mengikuti tanda d_t (kelanjutan kekuatan relatif), TIDAK dibalik.
      Semua nilai dari bar t yang sudah tutup (§L1). Aturan penyelarasan sesi
      dan larangan forward-fill dari Z02 berlaku penuh di sini.
    params: {signal_window: [48, 96], tau: [1.0, 1.5]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    fitur_input: "z lintas-seksi dari Z02"
    mechanism:
      claim: "Kekuatan relatif satu aset terhadap kelompoknya bertahan dalam horizon pendek karena aliran realokasi antar aset dieksekusi bertahap dan tidak selesai dalam satu bar"
      counterparty: "Manajer yang harus merealokasi antar kelas aset dalam jendela waktu tertentu dan rela membayar kelanjutan harga demi menyelesaikan perpindahan tepat waktu"
      decay: "Kecepatan realokasi meningkat seiring otomatisasi eksekusi, sehingga jendela tempat efek ini hidup menyempit dari tahun ke tahun"
    provenance:
      citation: "Asness, Moskowitz & Pedersen, Value and momentum everywhere, Journal of Finance, 2013"
      doi: NEED_LOOKUP
      peer_reviewed: true
    tier: tier_1_murah
    catatan_dedup: >
      Risiko korelasi tinggi terhadap Z02 secara konstruksi (memakai z yang sama).
      WAJIB dicek dedup 0.90 terhadap Z02 SEBELUM keduanya dijalankan. Kalau lewat ambang,
      jalankan SATU saja. Menjalankan keduanya = menghitung satu hipotesis dua kali dan
      menaikkan ambang untuk semua kandidat lain tanpa menambah informasi (§lessons_carried.8).
```

---

## Z.3 — Yang TIDAK saya lakukan, dan alasannya

| Tidak dilakukan | Alasan |
|---|---|
| Menambah z-score harga vs MA | = Bollinger. Dilarang §anti_rumus_ritel, sudah mati di persentil permutasi 2.7% |
| Mengubah satupun formula V/Q/T/X/E/M yang sudah ada | Diminta jangan diubah, dan memang tidak perlu |
| Mengubah ambang, gerbang, atau `screen_max` | §O8 — ubah ambang = OVERRIDE V5 + ulang dari awal |
| Menaikkan `total_ledger_max` dari 572 supaya 17 varian ini muat | Menambah kandidat menaikkan ambang untuk semua kandidat lain. Lihat §Z.4 |
| Mengarang DOI supaya terlihat rapi | §D1 — satu sitasi palsu membatalkan seluruh registry. Semua `NEED_LOOKUP` |

---

## Z.4 — ⛔ GERBANG PERSETUJUAN: 17 varian ini belum boleh dijalankan

Ini bukan formalitas. Anggaran trial Anda **sudah penuh**:

```
Registry sekarang : 507 varian
screen_max        : <= 500          → sudah harus dipangkas 7
Adendum Z         : +17 varian      → total 524, lewat 24 dari batas
```

Dan menambah kandidat **bukan tindakan gratis** — §lessons_carried.8:
*"Menambah kandidat menaikkan ambang untuk semua kandidat lain."* Ambang DSR dihitung dari
`ledger_cumulative`. 17 varian baru menaikkan rintangan bagi 507 kandidat yang sudah ada.

Jadi ada **tiga pilihan, dan hanya tiga**:

**(A) Bayar dari anggaran E — rekomendasi saya**
Pangkas 17 varian dari divisi E sesuai `tangga_pemangkasan` langkah 2 (kecilkan grid E33 9→3,
E35 8→3, E80 6→3 sudah menghasilkan −17). Total ledger **tidak berubah**. X tetap utuh 114.
Ini yang saya sarankan: Z01–Z03 dibayar oleh E, bukan ditumpuk di atas E.

**(B) Kecilkan grid Adendum Z**
Z01 `tau` → `[1.5]` saja, Z02 & Z03 `signal_window` → `[96]` saja. Hasilnya 3+2+2 = **7 varian**.
Cukup untuk menguji apakah bentuknya hidup, tanpa memakan anggaran besar.

**(C) OVERRIDE V5 tertulis dari Anda**
Naikkan `screen_max`. Konsekuensinya eksplisit dan tidak bisa ditawar: **ambang DSR naik untuk
semua kandidat**, termasuk 114 varian divisi X yang merupakan prioritas tertinggi Anda.
Saya tidak menyarankan ini.

> Sampai salah satu dipilih, status ketiganya tetap `USULAN_BARU_V5_ADENDUM_Z` dan
> **tidak boleh masuk `ledger_trials.csv`**.

---

## Z.5 — Kalau disetujui, urutan kerjanya

1. **F3** — verifikasi DOI Iglewicz-Hoaglin (1993) dan Asness-Moskowitz-Pedersen (2013). Tidak resolve → `NEED_LOOKUP`, boleh screening, **dilarang** masuk CONFIRM.
2. **F3** — dedup: Z01 vs `E02`, Z03 vs `Z02`, dan ketiganya vs graveyard. Ambang 0.90, dihitung di partisi screen.
3. **F1** — uji kebocoran §L10 khusus Z02/Z03: bangun versi yang sengaja memakai bar yang belum tutup di instrumen lain. Versi bocor itu **harus** menang telak. Kalau tidak, penyelarasan sesi lintas-instrumen Anda bermasalah — dan itu adalah titik kebocoran nomor satu di formula lintas-seksi.
4. **F0** — pastikan model biaya per instrumen sudah terisi untuk setiap instrumen yang bisa kena entry dari Z02.
5. **F6** — jalankan bersama divisi E, gerbang `gates.direction` penuh, 17 centang, biaya `worst`.
6. Lolos → CONFIRM (maks 8 slot, tidak ditambah). Tidak lolos → masuk graveyard, dicatat, **jangan disetel ulang**.
