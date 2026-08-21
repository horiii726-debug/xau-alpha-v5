# PATCH 01 — ANGGARAN, TANGGA PEMANGKASAN & ADENDUM Z (OVERRIDE V5)

> **Status: DIKUNCI.** OVERRIDE V5 tertulis dari user, 2026-08-21.
> Menjawab `AUDIT_TEMUAN.md` Temuan 1–4 dan `ADENDUM_Z_ENTRY.md` §Z.4.
>
> File ini **tidak mengubah** satupun dari 19 file verbatim lain di `xau_v5/`.
> Ia adalah lapisan keputusan resmi di atasnya, sah menurut §O8
> ("ambang dilarang diubah setelah melihat hasil — ubah = OVERRIDE V5 + ulang
> dari awal"). Belum ada hasil yang dilihat sampai titik ini — keputusan di
> bawah murni pre-registration, konsisten dengan §O1.
>
> **F0 belum dimulai.** Patch ini adalah syarat sebelum F0, bukan bagian dari F0.

---

## Ringkasan lima keputusan

| # | Temuan / Adendum | Keputusan user |
|---|---|---|
| 1 | Tangga pemangkasan tidak capai anggarannya sendiri | Opsi (a)+(b): tambah langkah 7 + ubah rumus `screen_max` |
| 2 | K_eff=3 → nol slot untuk E dan M | Tulis aturan eksplisit — dicatat sebagai hasil sah |
| 3 | 4 angka potongan salah hitung | Koreksi L1, L2, L3, L5 + angka sisa M |
| 4 | `pilot_set` F2b memuat E72 (bukan tier-1) | Ganti E72 → `E70_MANN_KENDALL` |
| Z | 17 varian Adendum Z (Z01–Z03) | Opsi A — dibayar dari anggaran divisi E lewat langkah 2 |

⚠️ **Baca §6 sebelum memakai angka di §2** — ada satu tegangan antara keputusan
Temuan 1 dan Temuan 2 yang baru ketemu saat menyusun patch ini.

---

## 1. Tangga pemangkasan — versi terkoreksi + langkah baru

Komposisi registri (tidak berubah, verbatim): `X:114, E:209, M:81, V:41, Q:35, T:27, TOTAL:507`

```yaml
tangga_pemangkasan_v2:  # menggantikan trial_budget.tangga_pemangkasan di 06_GERBANG_DAN_ANGGARAN.md
  urutan_pangkas:
    1:
      aksi: "E tier-3 (E40-E45, E95-E97) dibuang total — 9 formula, nol tersisa"
      potong: -32          # KOREKSI dari klaim asli -37 (Temuan 3)
      E_setelah: 177        # 209-32, dari 56 formula jadi 47 formula
    2:
      aksi: "E tier-2 grid besar dikecilkan ke maks 3 varian (E33, E35, E80, E97, E02, E03, E22)"
      potong: -26           # KOREKSI dari klaim asli -29 (Temuan 3)
      catatan: "E97 sudah nol dari langkah 1 — lihat §6.1 untuk detail rekonsiliasi"
      E_setelah: 151         # 177-26
    3:
      aksi: "M dipangkas ke baseline + meta-labeling saja: buang M01-M05, M09, M10, M14, M15"
      potong: -52           # KOREKSI dari klaim asli -53 (Temuan 3)
      sisakan_eksplisit: "M06 (4) + M07 (4) + M08 (6) + M11 (8) = 22"   # KOREKSI dari klaim asli "10"
      catatan: "M12/M13 tidak disebut langkah ini — lihat §6.2"
    4:
      aksi: "E tier-1 dengan grid besar dikecilkan ke 2 varian per formula"
      potong: adaptif        # tidak diubah — potong secukupnya untuk capai target, dihitung di F0
    5:
      aksi: "V/Q/T disisakan 1 varian per formula (jendela tengah) — 36 formula, 1 varian tiap"
      potong: -67           # KOREKSI dari klaim asli -60 (Temuan 3)
    6:
      aksi: "X — dipangkas TERAKHIR, hanya varian, bukan formula"
      catatan: "tidak dipakai di skenario manapun dalam patch ini; X tetap 114 di seluruh contoh §1.2"
    7:            # BARU — jawaban Temuan 1
      aksi: "E disisakan 1 varian per formula (jendela tengah) — 47 formula tersisa (setelah langkah 1), 1 varian tiap"
      potong_dari_E: -104    # dari 151 (setelah langkah 2) ke 47
      alasan: >
        Tangga lama berhenti di langkah 5 dan tidak bisa mencapai screen_max
        200 pada K_eff=4 (AUDIT_TEMUAN.md Temuan 1). Langkah ini adalah lantai
        teoretis E, dipakai HANYA kalau anggaran masih belum tercapai setelah
        langkah 1-5.
  tidak_boleh_dipangkas_dalam_kondisi_apapun: "tidak berubah dari 06_GERBANG_DAN_ANGGARAN.md"
```

### 1.1 Rumus `screen_max` baru

```yaml
trial_budget_v2:
  screen_max_lama: "min(500, floor(50 * K_eff_terukur))"           # DIGANTIKAN
  screen_max_baru: "max(219, min(500, floor(50 * K_eff_terukur)))" # BERLAKU MULAI PATCH INI
  lantai_keras: 219
  lantai_keras_komposisi: "X 114 (tidak boleh dipangkas) + V/Q/T 36 (langkah 5) + M 22 (langkah 3, lihat §6.2) + E 47 (langkah 1+7) = 219"
  breakeven_K_eff: 4.38   # 219/50 — di atas titik ini, formula lama dan baru identik
```

### 1.2 Tabel `screen_max` pada beberapa K_eff (dihitung langsung dari rumus baru §1.1 — tidak bergantung pada detail cascade §6)

| K_eff terukur | `min(500, floor(50×K_eff))` | `screen_max` baru | Catatan |
|---:|---:|---:|---|
| 3.0 | 150 | **219** | lantai mengikat |
| 4.0 | 200 | **219** | lantai mengikat — ini skenario asli Temuan 1 |
| 4.38 | 219 | **219** | titik impas |
| 5.0 | 250 | 250 | lantai tidak lagi mengikat |
| 6.0 | 300 | 300 | |
| 8.0 | 400 | 400 | |
| 10.0 | 500 | 500 | sama seperti sebelumnya |

Untuk K_eff di luar tabel ini (terutama K_eff 5–10 dengan target di antara 219 dan
500), langkah 4 (adaptif) yang menutup selisihnya. Angka presisi langkah 4 per
K_eff **belum dihitung** di patch ini — itu pekerjaan F0 begitu K_eff terukur
sungguhan tersedia, bukan sesuatu yang bisa ditentukan di muka dari daftar
formula saja.

---

## 2. Aturan eksplisit K_eff 3–4 (Temuan 2)

Teks yang Anda minta, ditulis verbatim sebagai tambahan ke `tangga_pemangkasan`:

> **K_eff antara 3 dan 4: hanya divisi X + baseline estimasi yang dijalankan.
> Divisi E dan M ditunda sampai panel diperluas. Ini hasil yang sah, bukan
> kegagalan.**

⚠️ **Lihat §6.3 — teks ini kemungkinan sudah tidak menggambarkan keadaan
sebenarnya setelah langkah 7 (§1) diterapkan.** Saya tulis verbatim sesuai
instruksi, tapi mohon dikonfirmasi ulang sebelum dipakai sebagai aturan
operasional F0.

---

## 3. Koreksi angka (Temuan 3) — ringkasan

| Langkah | Klaim asli | Angka terkoreksi (dipakai mulai patch ini) |
|---|---:|---:|
| L1 (E tier-3 dibuang) | -37 | **-32** |
| L2 (E tier-2 grid ke maks 3) | -29 | **-26** |
| L3 (M dipangkas ke baseline+meta) | -53 | **-52** |
| L3 — sisa M (eksplisit) | 10 | **22** |
| L5 (V/Q/T ke 1 varian/formula) | -60 | **-67** |

---

## 4. Pilot F2b — E72 diganti E70 (Temuan 4)

```yaml
pilot_set_v2:  # menggantikan pilot_set di 07_FASE_EKSEKUSI.md §F2b
  jumlah_formula: 12
  pilihan: [E01, E10, E22, E30, E60, E70, E90, X01, X06, X32, V01, Q08]  # E72 -> E70
  alasan_pilihan: "murah secara komputasi, mewakili keluarga berbeda, semua tier-1 — SEKARANG BENAR (E70_MANN_KENDALL tier-1, bukan tier-2 seperti E72)"
  varian_per_formula: 1
  total_baris_ledger: 72   # TIDAK BERUBAH — substitusi 1-untuk-1, sama-sama 1 varian per formula
```

---

## 5. Adendum Z — Opsi A disetujui (§Z.4)

**Keputusan:** Z01–Z03 (17 varian: Z01=9, Z02=4, Z03=4) dibayar dari anggaran
divisi E lewat mekanisme langkah 2 (§1). Z01–Z03 pindah status dari
`USULAN_BARU_V5_ADENDUM_Z` menjadi **disetujui masuk registri**, dengan syarat
tetap berlaku dari `ADENDUM_Z_ENTRY.md` §Z.5 (verifikasi DOI, dedup vs E02/Z02,
uji kebocoran L10 khusus Z02/Z03, model biaya per instrumen untuk Z02).

Rekonsiliasi angka (pakai L2 terkoreksi §3, bukan klaim asli adendum "-17"):

```
Registri dasar                : 507
+ Z01 + Z02 + Z03              : +17  -> 524
- langkah 2 (terkoreksi)       : -26  -> 498
```

Hasil bersih: **498**, yaitu 9 di bawah baseline 507 — bukan persis 507 seperti
klaim asli `ADENDUM_Z_ENTRY.md` §Z.4 opsi A ("Total ledger tidak berubah").
Ini **lebih konservatif** dari yang dijanjikan (anggaran lebih longgar, bukan
lebih ketat), karena L2 terkoreksi (-26) memotong lebih banyak dari klaim asli
adendum (-17). X, M, V, Q, T semuanya tetap utuh seperti dijanjikan. Dilaporkan
apa adanya, bukan dipaksa pas ke 507.

---

## 6. Temuan tambahan — ditemukan saat menyusun patch ini, DILAPORKAN bukan DIPUTUSKAN

Tiga hal di bawah muncul saat saya mencoba merekonsiliasi angka §1–§5
sampai ke level formula individual. Saya **tidak** menyelesaikannya sepihak —
saya pakai angka yang Anda tentukan di semua tempat, tapi mencatat gap-nya di
sini sesuai §stop_conditions.6 ("masalah yang tidak diatur file ini →
berhenti, tanya user").

### 6.1 — L2 (-26): rekonsiliasi formula-per-formula tidak bulat

L2 menyebut 7 formula (E33, E35, E80, **E97**, E02, E03, E22), tapi E97 sudah
nol varian sejak langkah 1 — tidak ada yang bisa "dikecilkan 6→3" pada formula
yang sudah tidak ada. Kalau E97 dikeluarkan sepenuhnya dari perhitungan, potongan
ketat dari 6 formula yang tersisa (E33, E35, E80, E02, E03, E22) adalah **-23**,
bukan -26. Angka -26 yang Anda pakai cocok secara aritmetika kalau E97 tetap
dihitung sebagai bagian dari jumlah (6+5+3+3+3+3+3=26), tapi itu menghitung
sesuatu yang sudah tidak ada. Saya memakai **-26** (angka Anda) di seluruh
patch ini, tapi selisih 3 varian ini belum sepenuhnya jelas asalnya dan perlu
dicek ulang saat kode L2 ditulis di F0.

### 6.2 — M12/M13 (7 varian) tidak disebut di langkah manapun

`M12_KALMAN_LATENT_DRIFT` (3 varian) dan `M13_KALMAN_LATENT_VOL` (4 varian) —
total 7 varian — tidak muncul di langkah 3 (atau langkah manapun) di
`tangga_pemangkasan`, baik versi asli maupun versi terkoreksi. Kalau langkah 3
dijalankan persis seperti tertulis (buang M01-M05, M09, M10, M14, M15; sisakan
M06, M07, M08, M11), M12/M13 otomatis **tetap ada** — sisa M sungguhan jadi
22+7=**29**, bukan 22.

Tapi lantai keras 219 (§1.1) yang sudah Anda kunci HANYA konsisten kalau M=22
di titik lantai (114+36+22+47=219; kalau M=29, lantai jadi 226, bukan 219).
Artinya supaya 219 benar, M12/M13 harus ikut tidak dijalankan di titik lantai —
tapi tidak ada langkah eksplisit yang memerintahkan itu. Saya pakai 219 dan
M=22 sesuai keputusan Anda, tapi status M12/M13 di titik lantai **belum
diatur**. Rekomendasi: tambahkan catatan eksplisit di langkah 3 bahwa M12/M13
ikut dipangkas di titik lantai, atau putuskan mereka tetap hidup dan terima
lantai jadi 226.

### 6.3 — Tegangan antara Temuan 1 (langkah 7) dan Temuan 2 (aturan K_eff 3-4)

Ini yang paling penting untuk dibaca ulang.

Sebelum langkah 7 ditambahkan, K_eff=3 menghasilkan `screen_max`=150, dan
komposisi minimum X+V/Q/T saja sudah 114+36=150 — **habis**, nol sisa untuk E
dan M. Itu premis Temuan 2.

**Setelah langkah 7 diterapkan** (§1), `screen_max` pada K_eff=3 menjadi **219**
(lantai mengikat), dan komposisi lantai 219 itu SENDIRI sudah menyediakan
**E=47** dan **M=22** — bukan nol. Dengan kata lain: perbaikan Temuan 1 sudah
secara struktural menyelesaikan masalah Temuan 2. Pada K_eff manapun ≥3, divisi
E dan M **selalu** dapat alokasi minimum (47 dan 22), tidak pernah nol lagi.

Teks Temuan 2 yang Anda minta ("hanya X + baseline estimasi, E dan M ditunda")
sudah saya tulis verbatim di §2 karena itu instruksi eksplisit Anda, tapi
secara matematis **premisnya tidak lagi berlaku** setelah §1 diterapkan. Kalau
kedua keputusan ini dipakai bersamaan tanpa diperjelas, akan ada kontradiksi
langsung: §1 bilang E dan M dapat 47+22 slot di K_eff=3, §2 bilang E dan M
ditunda sepenuhnya di rentang K_eff yang sama.

**Perlu diputuskan:** hapus teks §2 (karena sudah tidak relevan setelah §1),
atau simpan §2 untuk kasus lain yang belum saya pahami maksudnya?

---

## 7. Pre-registration lock

```yaml
meta_override:
  locked_on: "2026-08-21"
  base_source_sha256: "264fe974c1c1fa70b155b8a4f6b2c865860ef948194c3041d2df648b0a9d0b30"
  scope: "Hanya keputusan anggaran/tangga pemangkasan/Adendum Z di file ini (PATCH_01_ANGGARAN.md). BUKAN pengunci config/v5.yaml F0 — file itu belum dibuat."
  patch_sha256: "lihat PATCH_01_ANGGARAN.md.sha256 (sidecar, dihitung setelah file ini final)"
  catatan: >
    XAU_ALPHA_V5.yaml (sumber asli, 3352 baris) tidak ditemukan di filesystem
    ini — hanya 19 file split markdown di xau_v5/. Hash sumber di atas
    dikutip dari dokumentasi (CLAUDE.md, AUDIT_TEMUAN.md), BELUM diverifikasi
    ulang dari file aslinya karena filenya tidak ada di sini. Ditandai
    UNVERIFIED, bukan ditebak sebagai benar.
```
