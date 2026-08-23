# 07 — GERBANG CORONG: DARI TEMBOK JADI SARINGAN BERTINGKAT

> 🔄 Ini file inti perbaikan v6. Baca sampai habis sebelum menyentuh kode gerbang.
>
> **Ambang CONFIRM tidak diubah satu titik pun.** Yang berubah: **kapan** tiap gerbang
> dipasang, dan **berapa besar sampel** di bawahnya.

---

## Bagian A — Masalahnya, dengan angka

### A1 — Transmitansi

**Transmitansi** `T = P(kandidat lolos | edge NYATA memang ada)`.

Ini besaran yang v5 tidak pernah hitung, dan ketiadaannya adalah penyebab langsung
lima versi nol.

Diukur lewat simulasi 200.000 jalur. Modelnya **tidak** mengasumsikan gerbang independen —
gerbang-gerbang itu mengukur ulang besaran yang sama, jadi:

```
z_g = t_true + sqrt(rho_g)*Z_bersama + sqrt(1-rho_g)*eps_g
gerbang g lolos kalau z_g >= hurdle_g
rho_g = seberapa besar gerbang g mengukur hal yang sama dengan gerbang lain
```

**Hasil untuk desain v5 (17 gerbang sekaligus di partisi SCREEN):**

| t yang tercapai | transmitansi | 4 gerbang paling mematikan |
|---:|---:|---|
| **0.39 (v5 nyata)** | **0.17%** | t≥3.0 (0%), DSR (1%), BH-FDR (1%), bootstrap CI (6%) |
| 2.00 (andai) | 11.5% | t≥3.0 (16%), DSR (18%), BH-FDR (27%), bootstrap (52%) |
| 3.50 (andai) | 63.9% | t≥3.0 (69%), DSR (73%), BH-FDR (82%), bootstrap (94%) |

**Gerbang v5 meloloskan 1 dari 588 sinyal yang benar-benar punya edge.**

Perhatikan baris ketiga: gerbang yang sama, dengan sampel yang cukup, meloloskan 64%.
**Gerbangnya tidak terlalu ketat. Sampelnya yang tidak cukup untuk gerbang itu.**

### A2 — Kenapa ini bukan soal "17 itu terlalu banyak"

Dokumen diagnosa sebelumnya menyimpulkan *"17 filter sekaligus membunuh 83–94% edge asli"*
dengan hitungan `0.8^8`. Hitungan itu **mengasumsikan gerbang independen**, dan itu
salah — gerbang-gerbang ini sangat berkorelasi (semuanya fungsi dari `t` yang sama).

Simulasi yang memodelkan korelasi memberi angka **lebih buruk lagi** (0.17%, bukan 6–17%),
tapi dengan **diagnosis berbeda**: yang membunuh bukan *jumlah* gerbangnya, melainkan
**tiga gerbang yang mustahil dilewati pada `t = 0.39`**: `t≥3.0`, `DSR≥0.95`, `BH-FDR`.

Bedanya penting untuk obatnya:

| diagnosis | obat |
|---|---|
| "terlalu banyak gerbang" | kurangi jumlah gerbang ← **salah, melemahkan sistem** |
| "gerbang tak-mungkin dipasang terlalu dini" | **pindahkan gerbang itu ke partisi yang punya daya** ← benar |

v6 memakai obat kedua. **Jumlah gerbang di CONFIRM tetap 17.**

---

## Bagian B — Corong v6

### B1 — Prinsip

```
Ambang tiap tahap DITURUNKAN DARI daya partisinya, bukan dipilih.

Aturan penetapan:
    ambang_tahap = ambang tertinggi yang masih memberi
                   P(lolos | IC 0.05) >= target_transmitansi tahap itu

target_transmitansi:  screening 0.80 | robustness 0.70 | rantai penuh 0.50
```

Ini bukan "menurunkan bar". Ini **menaruh bar di tempat yang datanya sanggup menopang**,
dan menaruh bar penuh di tempat sampelnya paling besar.

### B2 — 🔴 Kesalahan desain di draf awal v6, dan perbaikannya

Draf awal v6 menaruh **t≥2.0, bootstrap CI95 (1.96), dan permutasi p95 (1.65)** di
tahap yang sama. Ketiganya diukur pada `t_pooled` screen ≈ 2.2:

| gerbang | P(lolos) sendirian pada t=2.21 |
|---|---:|
| t ≥ 2.0 | 58.1% |
| bootstrap CI95 | 60.0% |
| permutasi p95 | 71.4% |
| kalahkan B01–B08 | 86.6% |
| MC5 ±20% | 93.5% |
| stabil 10 seed | 92.0% |

**Tiga yang pertama adalah UJI SIGNIFIKANSI YANG SAMA diulang tiga kali** (korelasi ke
faktor bersama 0.95 / 0.90 / 0.80). Menumpuknya di satu tahap berarti menghitung bukti
yang sama tiga kali — tiap pengulangan hanya menambah **peluang gagal**, bukan informasi.
Itu versi kecil dari kesalahan yang sama dengan v5.

**Perbaikan: tahap dikelompokkan menurut JENIS BUKTI, bukan menurut kekuatan ambang.**

### B3 — Tiga tahap

| tahap | partisi | jenis bukti | filter | ambang t | vonis |
|---|---|---|---:|---:|---|
| **1. SARINGAN** | SCREEN | signifikansi dasar | 5 | **≥1.5** | `SHORTLIST` |
| **2. ROBUSTNESS** | SCREEN | **STABILITAS** — korelasi rendah ke `t` | 6 | — | `KANDIDAT` |
| **3. CONFIRM** | CONFIRM | signifikansi penuh + semua sisanya | **17** | **≥3.0** | `TERBUKTI` |

```yaml
tahap_1_saringan:
  jenis_bukti: "signifikansi dasar — apakah ada apa-apanya sama sekali"
  vonis_lolos: SHORTLIST
  filter:
    - {id: F_EXPECT, uji: "expectancy_net_bps > 0 pada biaya WORST"}
    - {id: F_T15,    uji: "pooled t (effective_N + clustering) >= 1.5"}
    - {id: F_B02,    uji: "kalahkan B02_RANDOM_MATCHED"}
    - {id: F_B05,    uji: "kalahkan B05_COIN_FLIP"}
    - {id: F_BR,     uji: "BR_eff >= 100 per tahun"}

tahap_2_robustness:
  jenis_bukti: >
    STABILITAS. TIDAK ADA uji signifikansi ulang di sini — bootstrap CI, permutasi,
    dan DSR semuanya PINDAH ke CONFIRM, tempat t paling besar. Yang diuji di sini
    adalah apakah hasilnya bertahan saat kondisinya digoyang.
  vonis_lolos: KANDIDAT
  filter:
    - {id: F_MC5,   uji: "tanda expectancy tidak berubah pada gangguan parameter +/-20%"}
    - {id: F_SEED,  uji: "stabil di 10 seed, tanda tidak flip"}
    - {id: F_WF,    uji: "walkforward konsistensi tanda >= 80%"}
    - {id: F_THIRD, uji: "sepertiga terakhir masih signifikan"}
    - {id: F_CPCV,  uji: "CPCV path positif >= 80%"}
    - {id: F_MC2,   uji: "MC2 P(breach 250 trade) <= 5%"}
  catatan_MC2_dini: >
    MC2 sengaja dipindah MAJU ke tahap 2. Alasannya §00 Temuan 7: kendala prop firm
    mengikat lebih keras daripada edge-nya. Kandidat yang tidak bisa dijalankan pada
    ukuran posisi yang selamat TIDAK LAYAK dibawa ke CONFIRM, berapapun t-nya.

tahap_3_confirm:
  jenis_bukti: "signifikansi penuh — 17 centang, TERMASUK bootstrap, permutasi, DSR"
  partisi: CONFIRM
  vonis_lolos: TERBUKTI
  slot_maksimum: 8
  slot_locked: true
  TIDAK_ADA_KELONGGARAN: true
```

### B3b — Transmitansi hasil restruktur

| konfigurasi | t_screen | t_confirm | tahap 1 | tahap 2 | tahap 3 | **rantai** |
|---|---:|---:|---:|---:|---:|---:|
| **v5** (17 gerbang di SCREEN) | 0.39 | — | — | — | — | **0.17%** |
| TIER-A (4 instr, 23 thn) | 2.21 | 3.28 | 73.7% | 61.0% | 55.3% | **24.8%** 🔴 |
| TIER-B (8 instr, 14 thn) | 2.16 | 3.20 | 71.7% | 58.3% | 51.6% | **21.6%** 🔴 |
| **TARGET (8 instr, ρ 0.10, 20 thn)** | **2.83** | **4.20** | — | — | — | **64.7%** ✅ |
| TARGET+ (8 instr, ρ 0.10, 23 thn) | 3.04 | 4.51 | — | — | — | **75.9%** ✅ |

🔴 = **di bawah GM-3 (50%) → BERHENTI di F1.**

**Yang harus dibaca dari tabel ini, dan ini yang paling penting di seluruh paket v6:**

> Restruktur corong saja **TIDAK CUKUP**. Pada konfigurasi TIER-A dan TIER-B,
> transmitansi hanya naik dari 0.17% ke ~22–25% — **masih di bawah gerbang mati GM-3.**
>
> Yang membuatnya lolos adalah **kombinasi** corong + `ρ_PnL ≤ 0.10` + riwayat ≥ 20 tahun.
> Lihat §01 B4b. **Corong tanpa sampel yang cukup tetap menghasilkan nol.**

Ambang CONFIRM tetap **17 centang, t ≥ 3.0, DSR ≥ 0.95**. Yang berubah hanya
**kapan** tiap gerbang dipasang dan **berapa besar sampel** di bawahnya.

### B4 — Yang TIDAK berubah, di semua tahap

| tetap | |
|---|---|
| Holdout terkunci, dibuka **sekali** seumur proyek | ✅ §O7 |
| Larangan `argmax`/`sort`/`nlargest` di divisi arah | ✅ §O5 |
| Tiap varian tetap **1 baris ledger** | ✅ §O2 |
| Biaya dihitung pada skenario **worst** di semua tahap | ✅ §03 |
| Bobot keunikan wajib di semua p-value | ✅ |
| `require_short_side_pass` untuk kandidat arah | ✅ |
| CONFIRM = 17 centang, t ≥ 3.0, DSR ≥ 0.95 | ✅ |

### B5 — Aturan yang mengikat status

```
SHORTLIST  = belum terbukti apa-apa. Boleh dibawa ke tahap 2. TITIK.
KANDIDAT   = layak dibawa ke CONFIRM. Belum terbukti.
TERBUKTI   = lolos 17 centang di CONFIRM.

DILARANG menyebut SHORTLIST atau KANDIDAT sebagai "terbukti", di laporan manapun.
DILARANG memakai SHORTLIST atau KANDIDAT untuk UANG ASLI, dengan alasan apapun.
Hanya TERBUKTI yang boleh lanjut ke HOLDOUT. Hanya yang lolos HOLDOUT yang
boleh masuk forward test. Hanya yang lolos forward test yang boleh uang asli.
```

---

## Bagian C — Checklist CONFIRM (17 centang, tidak diubah)

```yaml
gates_direction_confirm:
  selection_rule: threshold_only
  forbid_argmax: true
  checklist:
    1:  expectancy_net_bps_positif_pada_biaya_worst
    2:  t_stat_dengan_effective_n >= 3.0
    3:  lolos_BH_FDR_q_0.10
    4:  DSR >= 0.95
    5:  PBO <= 0.50
    6:  mengalahkan_B01_sampai_B08
    7:  CPCV_path_positif >= 80%
    8:  bootstrap_CI95_tidak_memuat_nol
    9:  permutasi_blok_di_atas_persentil_95
    10: walkforward_konsistensi_tanda >= 80%
    11: stabil_di_10_seed
    12: sepertiga_terakhir_masih_signifikan
    13: BR_eff >= 100_per_tahun            # 🔄 dulu: trades_per_tahun >= 300
    14: MC2_P_breach_250_trade <= 5%
    15: MC3_expectancy_positif_di_persentil_5
    16: MC5_tidak_runtuh_pada_plus_minus_20pct
    17: pooled_t_dengan_clustering_lolos    # 🔄 dulu: konsisten_di_minimal_60pct_instrumen

gates_estimation:
  # divisi V, Q, T, S — target terukur, boleh diperingkat
  selection_rule: model_confidence_set
  alpha: 0.10
  tie_break: paling_sederhana
  checklist:
    - masuk_model_confidence_set
    - mengalahkan_baseline_naif
    - stabil_lintas_sub_periode
```

### 🔄 Dua centang yang diganti — dan kenapa itu bukan pelonggaran

**Centang 13:** `trades ≥ 300/thn` → `BR_eff ≥ 100/thn`

| horizon | trade/thn | keunikan | BR_eff | aturan lama | aturan baru |
|---|---:|---:|---:|---|---|
| H60 | 400 | 0.18 | 72 | ✅ lolos | ❌ **gagal** |
| H240 | 220 | 0.62 | 136 | ❌ gagal | ✅ lolos |

Aturan baru **lebih ketat** untuk horizon pendek. Dia menolak H60/400-trade yang
diloloskan aturan lama, karena 400 trade yang tumpang tindih hanya memberi informasi
setara 72 taruhan independen. Yang diperbaiki bukan ketatnya — **satuannya**.

**Centang 17:** `konsisten ≥60% instrumen` → `pooled t dengan clustering`

Clustering per instrumen sudah memperhitungkan korelasi silang antar instrumen —
itu estimator yang benar untuk panel. "Konsisten di 60% instrumen" adalah aturan
jempol yang, pada instrumen berkorelasi, sebenarnya menguji **muatan faktor bersama**,
bukan robustness. Konsistensi tanda tetap dihitung dan dilaporkan sebagai **FLAG**
(§04 Bagian B).

---

## Bagian D — Gerbang KILL vs FLAG

Bukan semua gerbang layak membunuh. Beberapa mengukur hal yang penting tapi dengan
daya rendah pada sampel yang ada — memakai mereka sebagai KILL adalah melempar koin.

```yaml
klasifikasi_gerbang:
  KILL:
    # membunuh kandidat. Dipakai hanya kalau daya ujinya memadai.
    definisi: "gerbang yang, pada IC 0.05, punya P(lolos) >= 0.85 di partisi tempat dia dipasang"
    contoh: [F_EXPECT, F_T15, F_T20, F_B02, F_BR, DSR_di_CONFIRM, MC2]

  FLAG:
    # dicatat, wajib dijelaskan, TIDAK auto-membunuh.
    definisi: "gerbang yang daya ujinya di bawah 0.85 pada sampel yang ada"
    contoh: [SIGN_CONSISTENCY, SINGLE_ASSET_ONLY, PANEL_INSUFFICIENT, UNDERPOWERED_SCREEN]
    aturan: >
      Kandidat dengan >= 2 FLAG tidak boleh masuk CONFIRM tanpa penjelasan tertulis
      yang dipra-registrasi. FLAG bukan izin mengabaikan — dia perintah untuk menjelaskan.

  aturan_penetapan: >
    Klasifikasi KILL vs FLAG DITETAPKAN OTOMATIS oleh hasil uji L11 di F1,
    BUKAN dipilih manual. Gerbang yang di L11 meloloskan < 85% sinyal ber-IC 0.05
    otomatis turun jadi FLAG di tahap itu. Ini menghilangkan ruang penilaian subjektif.

  PENGECUALIAN_MUTLAK_CONFIRM: >
    🔴 Aturan demosi otomatis di atas TIDAK BERLAKU di tahap CONFIRM.
    SELURUH 17 centang CONFIRM adalah KILL, permanen, tanpa kecuali, berapapun
    transmitansi terukurnya. Kalau sebuah gerbang CONFIRM meloloskan < 85%, itu
    BUKAN alasan menurunkannya jadi FLAG — itu sinyal bahwa SAMPELNYA kurang,
    dan jawabannya GM-3 (BERHENTI, perbaiki sampel), bukan melemahkan CONFIRM.
    Tanpa pengecualian ini, aturan demosi otomatis adalah lubang yang bisa
    melonggarkan CONFIRM tanpa ada yang mendeklarasikan. Draf awal v6 punya lubang itu.
```

---

## Bagian E — Protokol kalau nol lolos

Kerjakan **URUT dari atas**. Laporkan tiap langkah sebelum lanjut.

```yaml
protokol_nol_lolos:
  # 🔄 langkah 0 adalah yang baru dan yang paling penting
  0_periksa_alat_dulu:
    perintah: "Jalankan L11. Berapa transmitansi terukur?"
    jika_transmitansi_di_bawah_50pct: >
      Ini BUKAN temuan tentang pasar. Ini alat ukur yang rusak.
      Perbaiki desain gerbang. DILARANG menurunkan ambang CONFIRM.
      DILARANG melaporkan 'tidak ada edge' sebelum langkah ini bersih.
    jika_transmitansi_di_atas_50pct: "lanjut ke langkah 1"

  1_periksa_horizon:
    "Apakah membaik di horizon lebih panjang? Biaya menelan 35% gerak di H15 vs 8.9% di H240."

  2_periksa_biaya:
    "Adakah sesi/jam dengan spread jauh lebih murah? Membatasi trading ke jendela biaya
     rendah kadang membalik expectancy tanpa mengubah sinyal."

  3_periksa_t_tertinggi:
    perintah: "Berapa t tertinggi yang tercapai di seluruh registry?"
    t_0.5_sampai_1.0: "sinyalnya memang lemah. Masalahnya RUMUS."
    t_2.0_sampai_2.8: "sinyalnya ada, sampelnya kurang. Masalahnya DATA -> langkah 4."
    catatan: "Dua diagnosis ini butuh obat berbeda. Jangan lanjut sebelum angka ini keluar."

  4_perbesar_panel:
    "eff N dan Sharpe portofolio dua-duanya naik sqrt(K_eff). Pengungkit terkuat."

  5_perpanjang_riwayat:
    "Dukascopy punya data lebih jauh. Rezim turun 2011-2015 dan sideways 2015-2019 belum dipakai."

  6_area_yang_belum_disentuh:
    "exit & sizing, ruin theory, optimal stopping. BUKAN menambah kandidat entry."

  7_terima_kalau_memang_nol:
    "Laporkan tanpa dilunakkan. Itu jawaban yang menghemat uang."

  dilarang_di_semua_langkah:
    - melonggarkan ambang CONFIRM
    - menambah kandidat
    - mengganti definisi statistik
    - mencari partisi data yang lebih ramah
    - membuka holdout kedua kali
    - mengganti arm penentu F2 dari demeaned ke raw
    - menghapus require_short_side_pass
```

### 🔄 Kenapa langkah 0 ada

v1–v5 melaporkan "nol survivor" lima kali dan menyimpulkan hal berbeda tiap kali
(rumusnya kurang, kandidatnya kurang, barriernya salah). **Tidak satupun dari lima
laporan itu memeriksa apakah gerbangnya sanggup meloloskan apapun.**

Transmitansi terukur v5 = 0.17%. Artinya: bahkan kalau ada sinyal sempurna ber-IC 0.05
di dalam 507 kandidat itu, peluang dia lolos ≈ **1 dari 588**. Dengan 507 kandidat yang
sebagian besar tidak punya edge, hasil nol **tidak memberi informasi apapun tentang pasar**.

Langkah 0 mencegah kesimpulan yang salah itu terulang untuk keenam kalinya.

---

**Lanjut ke `08_ANGGARAN_DAN_LEDGER.md`.**
