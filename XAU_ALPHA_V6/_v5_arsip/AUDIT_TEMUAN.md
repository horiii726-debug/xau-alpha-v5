# AUDIT TEMUAN — hasil pemeriksaan `XAU_ALPHA_V5.yaml`

> sha256 sumber: `264fe974c1c1fa70b155b8a4f6b2c865860ef948194c3041d2df648b0a9d0b30`
> 3.352 baris · 129 formula · 507 varian · diperiksa saat pemecahan file.
>
> **Tidak satupun temuan di bawah saya perbaiki di file sumber.** Semuanya butuh keputusan Anda.
> File-file divisi di paket ini adalah salinan verbatim, termasuk bagian yang salah hitung.

---

## Ringkasan

| # | Temuan | Tingkat | Fase terdampak |
|---|---|---|---|
| 1 | Tangga pemangkasan **tidak bisa mencapai anggarannya sendiri** | 🔴 **MATERIAL** | F0 → F6 |
| 2 | K_eff = 3 menyisakan **nol slot** untuk divisi E dan M | 🔴 **MATERIAL** | F0 |
| 3 | Empat angka potongan di `tangga_pemangkasan` salah hitung | 🟠 sedang | F0 |
| 4 | `pilot_set` F2b memuat E72 (tier-2) tapi diklaim "semua tier-1" | 🟡 ringan | F2b |
| 5 | `meta.locked_on` dan `config_sha256` masih `null` | 🟡 ringan | sebelum F2 |
| 6 | 129 sitasi, **nol** terverifikasi | 🟡 diakui sendiri | F3 |
| 7 | Seluruh angka biaya masih `LOOKUP` | 🟡 diakui sendiri | F0 |

**Yang LOLOS diperiksa** (bukan temuan — konfirmasi bahwa r5 memang beres):

- ✅ Komposisi registri **persis** cocok: X 114, E 209, M 81, V 41, Q 35, T 27 = **507**
- ✅ Tier komputasi: **129 dari 129** formula punya **tepat satu** tier. Nol duplikat, nol yang terlewat
- ✅ Seluruh ID di `padanan_akademik_wajib` benar-benar ada di blok `formulas` (perbaikan r5 sahih)
- ✅ Seluruh ID di `tidak_boleh_dipangkas` ada dan bisa dilacak
- ✅ `T17` yang disebut sudah dihapus di r5 memang tidak ada lagi

---

## 🔴 Temuan 1 — Tangga pemangkasan tidak bisa mencapai anggarannya sendiri

`§trial_budget.tangga_pemangkasan.contoh_hasil_pemangkasan` menjanjikan:

```
K_eff  4, budget 200 : "pangkas langkah 1-5 -> ~200. X utuh 114, estimasi 36, E ~40, M 10"
K_eff  6, budget 300 : "pangkas langkah 1-3 -> 388, lalu langkah 4 -> ~300"
K_eff 10, budget 500 : "pangkas langkah 1 saja -> 470 varian"
```

Saya jalankan tangganya dari angka varian yang sebenarnya:

| Skenario | Klaim file | Hasil hitung | Selisih |
|---|---:|---:|---:|
| K_eff 10 → L1 saja | 470 | **475** | +5 (masih < 500, aman) |
| K_eff 6 → L1–L3, lalu L4 | ~300 | **364** | **+64, LEWAT BATAS** |
| K_eff 4 → L1–L5 | ~200 | **290** | **+90, LEWAT BATAS** |

Lebih jauh: bahkan kalau langkah 4 didorong ke **lantai teoretisnya** — 1 varian per formula E,
padahal aturannya sendiri menulis "kecilkan ke **2** varian" — hasilnya tetap **219**, masih di atas 200.

```
lantai absolut = X 114 (tidak boleh dipangkas) + estimasi 36 + M 22 + E 47 = 219
```

**Kenapa ini material:** kalau F0 mengukur K_eff = 4, `screen_max` otomatis jadi 200. Tangga
pemangkasan lalu diminta memangkas ke 200 dan **tidak bisa**. Yang akan terjadi di lapangan adalah
salah satu dari dua hal, dan keduanya buruk:

- pemangkasan darurat yang **tidak diatur file ini** → melanggar §stop_conditions.6 dan §O1 (pre-registration), atau
- anggaran diam-diam dilewati → **DSR dihitung dengan N yang salah**, dan seluruh gerbang statistik jadi longgar tanpa ada yang sadar

**Yang perlu Anda putuskan** — salah satu:

1. Tambah **langkah 7** ke tangga: "E disisakan 1 varian per formula (jendela tengah)" → lantai 219, dan terima 219 sebagai lantai keras
2. Ubah rumus anggaran jadi `screen_max = max(219, min(500, floor(50 × K_eff)))` — jujur bahwa ada lantai struktural
3. Longgarkan aturan "X tidak pernah dipangkas sampai langkah terakhir" — **saya tidak menyarankan ini**, X adalah prioritas tertinggi Anda dan satu-satunya divisi yang belum pernah diuji

Apapun pilihannya, ini **OVERRIDE V5 tertulis** (§O8) dan harus diputuskan **sebelum F0 selesai**,
bukan setelah melihat hasil.

---

## 🔴 Temuan 2 — K_eff = 3 menyisakan nol slot untuk E dan M

`§trial_budget` menetapkan `screen_max = min(500, floor(50 × K_eff))`, dan
`tangga_pemangkasan` menetapkan K_eff < 3 → berhenti total.

Jadi K_eff = 3 adalah **kasus batas yang masih diizinkan berjalan**. Aritmetikanya:

```
screen_max pada K_eff 3        = 150
X (tidak boleh dipangkas)      = 114
V/Q/T lantai (1 varian/formula)=  36
                                 ----
sisa untuk divisi E dan M      =   0
```

Artinya pada K_eff = 3, sistem ini **secara matematis tidak bisa menguji satupun sinyal entry**.
Yang bisa dijalankan hanya divisi X plus alat ukur.

Ini belum tentu salah — bisa jadi justru kesimpulan yang benar dan konsisten dengan seluruh
filosofi file ini (*struktur payoff dulu, sinyal belakangan*). Tapi **tidak tertulis di manapun**,
dan tim yang menemukannya saat F0 akan mengiranya bug.

**Rekomendasi:** tulis eksplisit di `tangga_pemangkasan` —
*"K_eff antara 3 dan 4: hanya divisi X + baseline estimasi yang dijalankan. Divisi E dan M
ditunda sampai panel diperluas. Ini hasil yang sah, bukan kegagalan."*

---

## 🟠 Temuan 3 — Empat angka potongan salah hitung

| Langkah | Klaim | Hitung | Catatan |
|---|---:|---:|---|
| L1 — E tier-3 (E40–E45, E95–E97) | −37 | **−32** | 9 formula, varian: 4+2+2+4+4+2+4+4+6 |
| L2 — kecilkan grid ke maks 3 | −29 | **−29** | angkanya benar, **tapi memuat E97 yang sudah dibuang di L1** → efektif hanya **−26** |
| L3 — buang M selain baseline & meta-labeling | −53 | **−52** | |
| L5 — V/Q/T sisakan 1 varian per formula | −60 | **−67** | 36 formula, 103 varian → 103−36 |

Tambahan: `contoh_hasil_pemangkasan` menyebut sisa **M = 10** setelah L3.
Formula yang disisakan L3 adalah M06 (4) + M07 (4) + M08 (6) + M11 (8) = **22**, bukan 10.

Tidak ada yang berbahaya secara langsung di sini — tapi angka-angka inilah yang dipakai
Temuan 1, dan kalau dipakai mentah untuk merencanakan anggaran, rencananya meleset.

---

## 🟡 Temuan 4 — `pilot_set` F2b: E72 bukan tier-1

```yaml
pilot_set:
  pilihan: [E01, E10, E22, E30, E60, E72, E90, X01, X06, X32, V01, Q08]
  alasan_pilihan: "murah secara komputasi, mewakili keluarga berbeda, semua tier-1"
```

Saya cek 12-duanya. Sebelas benar tier-1. **`E72_THEIL_SEN_SLOPE` adalah tier-2** —
dan `compute_budget.catatan_E72_E82` justru memperingatkan bahwa dia O(w²) per bar, sekitar
**4.600 operasi per bar per instrumen** pada w=96.

F2b menjalankan 12 formula × 6 horizon × seluruh panel. Memasukkan satu formula kuadratik ke
fase yang dirancang murah adalah kontradiksi kecil tapi nyata, dan F2b adalah fase yang
menentukan apakah sisa proyek dijalankan sama sekali.

**Pilihan:** ganti E72 dengan `E70_MANN_KENDALL` atau `E80_QUANTILE_REGRESSION_SLOPE`
(dua-duanya tier-1, keluarga tren yang sama), **atau** batasi w ≤ 48 khusus untuk pilot dan
catat penyimpangannya. Jangan biarkan menggantung.

---

## 🟡 Temuan 5 — Kunci pre-registration masih kosong

```yaml
meta:
  locked_on: null
  config_sha256: null    # WAJIB diisi & di-commit sebelum FASE 2
```

`§O1` menuntut semua parameter dan ambang ditulis dan di-hash **sebelum melihat hasil**.
Selama dua field ini `null`, secara teknis **tidak ada yang ter-pre-register**, dan §O8
("ambang dilarang diubah setelah melihat hasil") tidak punya baseline untuk dibandingkan.

Untuk referensi, hash file sumber apa adanya saat ini:

```
sha256(XAU_ALPHA_V5.yaml) = 264fe974c1c1fa70b155b8a4f6b2c865860ef948194c3041d2df648b0a9d0b30
```

Kalau Anda memperbaiki Temuan 1–4, hash ini berubah — dan yang **wajib di-commit adalah hash
versi final**, bukan yang ini. Kunci setelah perbaikan, bukan sebelum.

---

## 🟡 Temuan 6 & 7 — sudah diakui sendiri di `meta.revisi.sisa_kelemahan_yang_diakui`

Saya konfirmasi keduanya masih berlaku, tidak ada yang berubah:

- **129 sitasi, nol diverifikasi.** Semua `doi: NEED_LOOKUP`. Gerbang F3 menuntut ≥90% resolve. Ini pekerjaan nyata yang belum dimulai, bukan formalitas.
- **Seluruh angka biaya `LOOKUP`:** `markup_prop_firm_pct`, `komisi`, `swap` (long/short/triple day), dan seluruh `terapkan_aturan_prop_firm` di MC2 (`max_daily_loss_pct`, `max_total_drawdown_pct`, `profit_target_pct`). Tanpa ini MC2 tidak bisa dijalankan sama sekali — dan MC2 adalah satu-satunya gerbang yang menjawab *"apakah akunnya selamat?"*

Yang terakhir itu yang paling saya khawatirkan dari sisi uang nyata. Expectancy positif dengan
`P(breach) = 40%` adalah sistem yang menghancurkan akun sebelum sempat menghasilkan, dan sekarang
angka untuk menghitungnya belum ada satupun.

---

## Urutan yang saya sarankan

1. Putuskan **Temuan 1** (lantai tangga pemangkasan) — ini memblokir perhitungan anggaran F0
2. Tulis eksplisit **Temuan 2** ke dalam file
3. Perbaiki angka **Temuan 3**, ganti pilihan pilot **Temuan 4**
4. Putuskan Adendum Z (`ADENDUM_Z_ENTRY.md` §Z.4) — juga menyangkut anggaran, jadi sekalian
5. **Baru** isi `locked_on` + `config_sha256`, commit, dan mulai F0

Mengunci hash sebelum langkah 1–4 selesai berarti mengunci angka yang sudah diketahui salah.
