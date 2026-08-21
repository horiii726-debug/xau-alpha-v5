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
>
> **Revisi ronde 2 (2026-08-21):** tiga hal yang dilaporkan di §6 versi
> pertama sudah diputuskan user. Lihat §6 untuk resolusinya. `patch_sha256`
> di §7 dihitung ulang dari versi final ini.

---

## Ringkasan keputusan (setelah ronde 2)

| # | Temuan / Adendum | Keputusan user |
|---|---|---|
| 1 | Tangga pemangkasan tidak capai anggarannya sendiri | Opsi (a)+(b): tambah langkah 7 + ubah rumus `screen_max` |
| 2 | K_eff=3 → nol slot untuk E dan M | **DICABUT ronde 2** — gugur setelah langkah 7 diterapkan, lihat §6.1 |
| 3 | 4 angka potongan salah hitung | Koreksi L1, L2, L3, L5 + angka sisa M |
| 3b | M12/M13 (7 varian) tidak tercakup langkah 3 | **BARU ronde 2** — ditambahkan ke daftar buang langkah 3, lihat §6.2 |
| 3c | L2 (-26): E97 sudah nol, tidak bisa "dikecilkan" | **BARU ronde 2** — daftar formula L2 dikoreksi (E24 menggantikan E97), lihat §6.3 |
| 4 | `pilot_set` F2b memuat E72 (bukan tier-1) | Ganti E72 → `E70_MANN_KENDALL` |
| Z | 17 varian Adendum Z (Z01–Z03) | Opsi A — dibayar dari anggaran divisi E lewat langkah 2 |

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
      aksi: "E tier-2 grid besar dikecilkan ke maks 3 varian (E33, E35, E80, E02, E03, E22, E24)"
      potong: -26           # KOREKSI dari klaim asli -29 (Temuan 3), formula list dikoreksi ronde 2 — lihat §6.3
      catatan: "E97 DIKELUARKAN dari daftar (sudah nol dari langkah 1), digantikan E24 (6 varian, belum tersentuh langkah manapun) — lihat §6.3"
      E_setelah: 151         # 177-26
    3:
      aksi: "M dipangkas ke baseline + meta-labeling saja: buang M01-M05, M09, M10, M14, M15, M12, M13"
      potong: -59           # KOREKSI ronde 1: -53->-52 (Temuan 3). KOREKSI ronde 2: -52->-59 (M12+M13 ditambahkan, §6.2)
      sisa_M_total: "M06 (4) + M07 (4) + M08 (6) + M11 (8) = 22 — ini SEKARANG total sisa M yang sebenarnya, bukan cuma subset eksplisit"
      catatan: "M12 (3) dan M13 (4) ditambahkan ke daftar buang di ronde 2 — lihat §6.2. Prinsip langkah 3 adalah 'sisakan baseline wajib (M6) + meta-labeling saja' — M12/M13 bukan keduanya."
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
  lantai_keras_komposisi: "X 114 (tidak boleh dipangkas) + V/Q/T 36 (langkah 5) + M 22 (langkah 3, M12/M13 ikut dipangkas — §6.2) + E 47 (langkah 1+7) = 219"
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

## 2. Temuan 2 — DICABUT (ronde 2)

> **Temuan 2 gugur setelah Temuan 1 diterapkan — lantai 219 sudah menyediakan
> slot untuk E dan M.**

Teks aturan eksplisit yang sebelumnya ditulis di sini ("K_eff antara 3 dan 4:
hanya divisi X + baseline estimasi yang dijalankan, divisi E dan M ditunda")
**dihapus**. Alasan lengkap di §6.1. Ringkas: setelah langkah 7 (§1) berlaku,
`screen_max` di K_eff=3 adalah 219 (bukan 150), dan komposisi lantai 219 itu
sendiri sudah memuat E=47 dan M=22 — bukan nol. Premis Temuan 2 tidak berlaku
lagi begitu Temuan 1 diterapkan.

---

## 3. Koreksi angka (Temuan 3) — ringkasan

| Langkah | Klaim asli | Ronde 1 | Ronde 2 (final) |
|---|---:|---:|---:|
| L1 (E tier-3 dibuang) | -37 | -32 | **-32** (tidak berubah) |
| L2 (E tier-2 grid ke maks 3) | -29 | -26 | **-26** (angka sama, daftar formula dikoreksi — §6.3) |
| L3 (M dipangkas ke baseline+meta) | -53 | -52 | **-59** (M12/M13 ditambahkan — §6.2) |
| L3 — sisa M | 10 | 22 (eksplisit, ada gap 7 tersembunyi) | **22** (total sebenarnya, gap tertutup) |
| L5 (V/Q/T ke 1 varian/formula) | -60 | -67 | **-67** (tidak berubah) |

Total setelah L1+L2+L3+L5 (sebelum L7): 507-32-26-59-67 = **323**.
Setelah L7 (E ke 1 varian/formula, -104 dari E): 323-104 = **219**. Cocok
dengan lantai keras §1.1, dan sekarang tidak ada lagi angka yang tidak
tereskonsiliasi (bandingkan dengan versi ronde 1 yang masih punya gap 7 di M).

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

## 6. Resolusi ronde 2 — tiga temuan tambahan, semuanya sudah diputuskan user

Tiga hal di bawah muncul saat menyusun versi pertama patch ini (merekonsiliasi
angka §1–§5 sampai level formula individual). Dilaporkan tanpa diputuskan
sepihak di ronde 1; user memutuskan ketiganya di ronde 2. Dicatat di sini
untuk jejak audit.

### 6.1 — Tegangan Temuan 1 vs Temuan 2 → **Temuan 2 dicabut**

Sebelum langkah 7 ditambahkan, K_eff=3 menghasilkan `screen_max`=150, dan
komposisi minimum X+V/Q/T saja sudah 114+36=150 — habis, nol sisa untuk E dan
M. Itu premis Temuan 2. Setelah langkah 7 diterapkan, `screen_max` di K_eff=3
menjadi 219, dan lantai 219 itu sendiri sudah memuat E=47 dan M=22.

**Keputusan user:** Temuan 2 dicabut. "Temuan 1 menang." Teks aturan
eksplisit K_eff 3-4 dihapus dari §2, digantikan catatan pencabutan.

### 6.2 — M12/M13 (7 varian) tidak disebut di langkah manapun → **ditambahkan ke langkah 3**

`M12_KALMAN_LATENT_DRIFT` (3) dan `M13_KALMAN_LATENT_VOL` (4) tidak muncul di
daftar buang ataupun daftar sisa langkah 3 manapun. Kalau langkah 3 dijalankan
persis seperti tertulis, M12/M13 otomatis tetap ada — sisa M sungguhan jadi
22+7=29, bukan 22 — dan lantai keras jadi 226, bukan 219.

**Keputusan user:** M12 dan M13 memang seharusnya ikut dipangkas — prinsip
langkah 3 adalah "sisakan baseline wajib (M06/M07/M08) + meta-labeling
(M11) saja," dan M12/M13 bukan keduanya; daftarnya yang lupa mencantumkan.
Ditambahkan ke daftar buang langkah 3 (§1). Potong langkah 3 naik dari -52
jadi **-59**. Lantai tetap **219**.

### 6.3 — L2 (-26): E97 sudah nol, tidak bisa "dikecilkan" → **daftar formula dikoreksi**

L2 asli menyebut 7 formula (E33, E35, E80, **E97**, E02, E03, E22), tapi E97
sudah nol varian sejak langkah 1 — tidak ada yang bisa "dikecilkan 6→3" pada
formula yang sudah tidak ada. Rekonsiliasi ronde 1 saya (hanya 6 formula hidup,
E33+E35+E80+E02+E03+E22) memberi -23, bukan -26 — jadi saya tandai sebagai gap
yang belum jelas asalnya.

**Keputusan user:** angka **-26** yang benar, bukan revisi saya (-23). Formula
yang hidup di langkah 2 bukan 6 tapi 7: E33, E35, E80, E02, E03, E22, **E24**
(E24_HIGUCHI_FD, 6 varian, tier-2, belum tersentuh langkah manapun —
menggantikan posisi E97 yang sudah nol). Potongan: 9→3(-6) + 8→3(-5) +
6→3×5(-15) = **-26**. Verifikasi saya: variant count E24 dari
`DIVISI_E_ENTRY_ARAH.md` = 6 (window×k_max = 3×2), cocok dengan perhitungan
di atas.

⚠️ **Catatan untuk jejak audit, bukan bantahan:** teks langkah 2 verbatim di
`06_GERBANG_DAN_ANGGARAN.md` secara eksplisit menulis "E97" dalam daftarnya,
bukan "E24" — jadi ini bukan salah baca saya atas sumber, tapi substitusi
formula yang disengaja (E97→E24) supaya -26 bisa direalisasikan pada formula
yang benar-benar masih hidup. Diperlakukan setara dengan substitusi Temuan 4
(E72→E70): keduanya OVERRIDE V5 eksplisit atas daftar formula tertentu, bukan
perubahan ambang atau rumus. Dicatat di §1 langkah 2 dan di sini agar siapapun
yang menulis kode L2 di F0 tahu alasannya.

---

## 7. Pre-registration lock

```yaml
meta_override:
  locked_on: "2026-08-21"
  revisi: "ronde 2 — lihat §6 untuk resolusi 3 temuan tambahan dari ronde 1"
  base_source_sha256: "264fe974c1c1fa70b155b8a4f6b2c865860ef948194c3041d2df648b0a9d0b30"
  scope: "Hanya keputusan anggaran/tangga pemangkasan/Adendum Z di file ini (PATCH_01_ANGGARAN.md). BUKAN pengunci config/v5.yaml F0 — file itu belum dibuat."
  patch_sha256: "lihat PATCH_01_ANGGARAN.md.sha256 (sidecar, dihitung ulang dari versi final ronde 2)"
  catatan: >
    XAU_ALPHA_V5.yaml (sumber asli, 3352 baris) tidak ditemukan di filesystem
    ini — hanya 19 file split markdown di xau_v5/. Hash sumber di atas
    dikutip dari dokumentasi (CLAUDE.md, AUDIT_TEMUAN.md), BELUM diverifikasi
    ulang dari file aslinya karena filenya tidak ada di sini. Ditandai
    UNVERIFIED, bukan ditebak sebagai benar.
```
