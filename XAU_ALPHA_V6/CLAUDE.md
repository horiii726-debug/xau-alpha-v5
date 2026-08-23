# XAU ALPHA RESEARCH v6 — INSTRUKSI KERJA

> **Untuk Claude Code. Ini pintu masuk. Baca file 00–10 penuh sebelum mengetik satu baris kode.**
>
> v6 dibangun setelah **v1–v5 menghasilkan nol survivor lima kali berturut-turut**.
> Penyebabnya sudah ditemukan dan dihitung. Bukan rumusnya, bukan pasarnya —
> **tiga gerbang yang secara matematis tidak bisa dilewati kandidat manapun.**
> Baca `00_TEMUAN_KENAPA_NOL.md` sebelum apapun.

---

## ⛔ ENAM KEPUTUSAN YANG MEMBLOKIR F0

Jangan hitung anggaran, jangan jalankan kandidat apapun, sebelum keenam ini
diputuskan user secara tertulis. Semuanya **OVERRIDE V6** (§O8).

| # | Keputusan | Konsekuensi kalau tidak diputuskan |
|---|---|---|
| 1 | **Corong bertingkat** (§07) menggantikan 17-gerbang-sekaligus-di-screening | transmitansi tetap **0.17%** — hasil dijamin nol untuk keenam kalinya |
| 2 | **F2 jadi PENGUKURAN**, bukan STOP TOTAL (§05 C) | proyek terblokir di gerbang yang gagal karena **teorema optional stopping**, bukan karena pasarnya |
| 3 | **Koreksi satuan `beta`** slippage (§03 C2) | kappa `worst` 0.52 di H240 — semua kandidat mati di biaya |
| 4 | **Ledger dipisah** arah vs estimasi (§O10) | `SR_0` dihitung dari N yang salah, DSR mustahil dilewati |
| 5 | **`sd_SR` diukur di F0** sebelum anggaran dikunci | jumlah kandidat yang aman **tidak diketahui** |
| 6 | **Syarat kelayakan gabungan** §01 B4b: `K_eff ≥ 4.0` **DAN** `T_confirm ≥ 11 thn` | corong lolos di atas kertas tapi transmitansi nyata **< 50%** → nol untuk keenam kalinya |

---

## Tujuh aturan yang tidak bisa ditawar

1. **Baca file 00–10 penuh sebelum mengetik satu baris kode.**
2. **Kerjakan SATU fase, lalu BERHENTI dan lapor** sebelum fase berikutnya.
3. Commit per fase: `v6 FASE Fn — <judul>`.
4. Tiap laporan memuat: **angka apa adanya, apa yang gagal, apa yang dilewati, apa yang belum yakin.**
5. **Kalau tidak yakin — bilang tidak yakin.** Dilarang menebak angka, sitasi, atau hasil.
6. **Kalau hasilnya jelek — laporkan jeleknya.** Jangan dipoles. Ini dipakai dengan uang nyata.
7. Dilarang melonggarkan gerbang manapun tanpa **OVERRIDE V6 tertulis dari user**.

Ditambah yang paling sering dilanggar:

> **§stop_conditions.7** — masalah yang tidak diatur file ini → **BERHENTI, tanya user,
> jangan putuskan sendiri.**

Dan yang baru di v6:

> **§L11** — sebelum kandidat pertama, ukur **transmitansi gerbang**. Kalau gerbang
> Anda membunuh sinyal sintetis ber-IC 0.05 lebih dari separuh waktu, **perbaiki
> gerbangnya, bukan turunkan ambangnya.**

---

## Apa yang berubah dari v5 — ringkas

| | v5 | v6 |
|---|---|---|
| Sampel screen | 313 hari × K_eff 1 | **≥5 thn × K_eff ≥4.0** (disyaratkan, §01 B4b) |
| Riwayat | 2021–2026 (satu rezim: naik) | **≥20 thn** (naik, turun, sideways) |
| Kandidat arah | 507 varian | **82 varian** (−84%), lantai 23 |
| Ambang saringan | t ≥ 3.0 (mustahil, t maks 0.39) | **t ≥ 1.5**, naik ke 3.0 di CONFIRM |
| **Ambang CONFIRM** | **17 centang, t ≥ 3.0** | **17 centang, t ≥ 3.0 — TIDAK BERUBAH** |
| Transmitansi gerbang | **0.17%** (tidak pernah diukur) | **64.7%** pada konfigurasi TARGET — dan **gerbang mati** kalau < 50% |
| Gerbang payoff F2 | STOP TOTAL | **PENGUKURAN** — gagal karena teorema |
| Anggaran kandidat | dipilih (500) | **diturunkan dari kelayakan DSR** |
| Biaya prop firm | seluruhnya `LOOKUP` — MC2 tidak bisa jalan | **terisi dari halaman resmi** — MC2 jalan |
| Divisi E | 56 formula "arah" | **dipecah 3 keluarga + 29 pindah ke divisi S** |
| Multi-strategi | tidak ada | **MOM / MRV / BRK + router bounded tilt** |
| Breakout | **tidak ada satupun** | **7 formula (4 baru dari jurnal)** |

**Angka yang paling penting:** gerbang v5 meloloskan **1 dari 588** sinyal yang
benar-benar punya edge. Ambang CONFIRM v6 identik dengan v5 — yang berubah **kapan**
gerbang dipasang dan **berapa besar sampel** di bawahnya.

> 🔴 **Tapi baca ini sebelum optimis.** Transmitansi v6 **tergantung sampelnya**:
>
> | konfigurasi | transmitansi | vonis |
> |---|---:|---|
> | 4 instrumen, ρ_PnL 0.20, 23 thn | 24.8% | 🔴 **GAGAL GM-3** |
> | 8 instrumen, ρ_PnL 0.15, 14 thn | 21.6% | 🔴 **GAGAL GM-3** |
> | 8 instrumen, ρ_PnL 0.10, 20 thn | **64.7%** | ✅ lolos |
>
> **Memperbaiki gerbang tanpa memperbaiki sampel tetap menghasilkan nol.**
> Syarat yang benar-benar mengikat: **`ρ_PnL ≤ 0.10` DAN riwayat ≥ 20 tahun.**
> Panel yang lebih kecil tapi lebih tidak berkorelasi **mengalahkan** panel besar
> yang berkorelasi — 6 instrumen @ρ0.10 (50.4%) menang atas 8 instrumen @ρ0.15 (48.4%).

---

## Peta file

### Inti — baca berurutan

| File | Isi | Kapan |
|---|---|---|
| `00_TEMUAN_KENAPA_NOL.md` | **8 temuan: tiga gerbang mustahil, kesalahan kategori, satuan slippage salah, kendala prop firm** | **PERTAMA** |
| `01_KONTRAK_DAN_POWER.md` | Kontrak kejujuran, Fundamental Law, K_eff, **anggaran diturunkan dari DSR** | sebelum F0 |
| `02_HUKUM.md` | L1–L13, O1–O11, anti-rumus-ritel, anti-data-palsu. **L11 & L12 baru** | sebelum menulis kode |
| `03_DATA_DAN_BIAYA.md` | Dukascopy harga saja, **biaya FTMO/FundedNext TERISI**, koreksi satuan beta | F0 |
| `04_UNIVERSE_HORIZON.md` | Panel 8 instrumen, riwayat 2003+, jendela pooling, BR_eff | F0, F2b |
| `05_PARTISI_LABELING.md` | Partisi 25/55/20, triple-barrier, **F2 jadi pengukuran**, definisi rezim | F2 |
| `06_VALIDASI_STATISTIK.md` | Null B01–B09 + **N1/N2/N3 router**, MC1–**MC6**, ambang, dedup, ML | F1 dan seterusnya |
| `07_GERBANG_CORONG.md` | **CORONG 3 TINGKAT**, transmitansi, KILL vs FLAG, protokol nol lolos | tiap gerbang |
| `08_ANGGARAN_DAN_LEDGER.md` | 3 ledger terpisah, anggaran dari DSR, **tangga pemangkasan yang sampai lantainya** | F0, F3 |
| `09_MULTISTRATEGI.md` | **MOM/MRV/BRK, router bounded tilt, cara mengujinya tanpa menipu diri** | F6, F7b |
| `10_FASE_EKSEKUSI.md` | F0–F12, stop condition, cara kerja, pelajaran | peta jalan |

### Divisi — registry formula

| File | Divisi | Formula | Varian | Fase | Ledger |
|---|---|---:|---:|---|---|
| `DIVISI_E1_MOMENTUM.md` | **E1 — MOM** | 11 | 20 | F6 | arah |
| `DIVISI_E2_MEANREV.md` | **E2 — MRV** | 6 | 12 | F6 | arah |
| `DIVISI_E3_BREAKOUT.md` | **E3 — BRK** 🆕 | 7 | 14 | F6 | arah |
| `DIVISI_X_EXIT_SIZING.md` | X — exit & sizing | 10 | 20 | F5 | arah |
| `DIVISI_M_ML_METALABELING.md` | M — ML & meta-labeling | 5 | 12 | F7 | arah |
| *(di `08_ANGGARAN`)* | ROUTER multi-strategi 🆕 | 3 | 4 | F7b | arah |
| | **TOTAL ARAH** | **42** | **82** | | |
| `DIVISI_S_STRUKTUR_REZIM.md` | **S — struktur & rezim** 🆕 | 29 | 29 | F4 | estimasi |
| `DIVISI_V_VOLATILITAS.md` | V — volatilitas | 14 | 41 | F4 | estimasi |
| `DIVISI_Q_SPREAD_LIKUIDITAS.md` | Q — spread & likuiditas | 12 | 35 | F4 | estimasi |
| `DIVISI_T_INTENSITAS_TICK.md` | T — intensitas tick | 10 | 27 | F4 | estimasi (`PARKED`) |
| | **TOTAL ESTIMASI** | **65** | **132** | | |

### Pendukung

| File | Isi |
|---|---|
| `REFERENSI_TERVERIFIKASI.md` | 6 sitasi ✅ terverifikasi, 5 `NEED_LOOKUP`, **1 tanpa sumber (dilaporkan apa adanya)** |
| `_verifikasi/` | script Python yang menghasilkan **setiap angka** di paket ini — wajib dijalankan ulang |
| `_v5_arsip/` | seluruh paket v5 apa adanya, untuk rujukan |

---

## Urutan fase

```
F0   fondasi, biaya, K_eff, sd_SR      ──► ⛔ GM-1..GM-5 → STOP
F1   infrastruktur + L10 + L11         ──► ⛔ transmitansi <50% → STOP, PERBAIKI GERBANG
F2   PENGUKURAN struktur payoff        ──►    keluaran: shortlist barrier + IC_minimum
F2b  pilot horizon (72 baris)          ──► ⛔ t_pooled < 3.0 di semua horizon → STOP
F3   verifikasi sitasi & dedup         ──►    ≥90% resolve, nol karangan
F4   estimasi V, Q, S                  ──►    MCS → fitur rezim untuk router
F5   divisi X — exit & sizing          ──►    prioritas mengikuti hasil F2
F6   tiga keluarga E, TERPISAH         ──►    corong: SHORTLIST → KANDIDAT
F7   divisi M — meta-labeling          ──►    wajib kalahkan baseline linear
F7b  ROUTER multi-strategi             ──►    wajib kalahkan N1, N2, N3
F8   freeze & pre-register             ──►    hash di-commit; L11 diulang
F9   CONFIRM — maks 8 slot             ──►    17 centang penuh, tanpa kelonggaran
F10  GOLDEN HOLDOUT — sekali tembak    ──►    degradasi vs CONFIRM < 50%
F11  paket deployment                  ──►    kill switch sebelum uang masuk
F12  FORWARD TEST demo ≥200 fill       ──►    cost_verified akhirnya bisa true
```

---

## Yang paling mudah dilanggar tanpa sadar

| Jebakan | Pasal | Cara mengecek sendiri |
|---|---|---|
| Memilih kandidat terbaik dari daftar | §O5 | `grep -nE "sort\|argmax\|idxmax\|nlargest\|max\(" select_champion` — ada satu saja, langgar |
| p-value tanpa bobot keunikan | §statistics | 16 dari 112 "signifikan" jadi 0–1 setelah dikoreksi. Assertion wajib menolak |
| kappa dari batas waktu maksimum | §03 C4 | Meremehkan biaya **3×**. Wajib dari durasi hit barrier NYATA |
| Normalisasi pakai statistik seluruh sampel | §L3 | Fit **hanya** di fold latih |
| Seleksi fitur sebelum loop CV | §L4 | Harus **di dalam** loop |
| **Forward-fill instrumen yang barnya belum tutup** | **§L12a** | **Titik bocor nomor satu di formula lintas-seksi** |
| **PELT retrospektif sebagai fitur live** | **§L13a** | Hanya umur segmen berjalan yang kausal |
| Registri penuh di 6 horizon | §08 E | 82 × 6 = 492 baris — dijamin nol. Pilih horizon di F2b |
| Menambah kandidat saat nol lolos | §07 E | Menambah kandidat **menaikkan `SR_0`** untuk semua kandidat lain |
| **Menyimpulkan "tidak ada edge" tanpa mengukur transmitansi** | **§07 E langkah 0** | **Kesalahan yang diulang lima kali** |
| Menamai ulang rumus ritel dengan notasi statistik | §02 | Lihat `DIVISI_E2_MEANREV.md` — peringatan z-score |

---

## Yang tidak bisa dijanjikan sistem ini

**Nol survivor tetap hasil yang sah.** Sistem validasi jujur harus bisa mengeluarkan nol.

Tapi v6 menambah satu hal yang v1–v5 tidak punya: **kemampuan membedakan
"nol karena pasarnya" dari "nol karena alat ukurnya rusak"** (§L11). Lima laporan nol
sebelumnya tidak pernah bisa membedakan keduanya — dan transmitansi terukur 0.17%
menunjukkan bahwa kelimanya kemungkinan besar salah diagnosis.

**Yang bisa dijanjikan:** kalau syarat kelayakan gabungan terpenuhi (`K_eff ≥ 4.0`
**dan** `T_confirm ≥ 11 thn`) dan edge ber-IC 0.05 ada di dalam registri, dia punya
peluang **~65%** lolos ke CONFIRM, bukan 0.17%.

**Yang TIDAK bisa dijanjikan:**

1. **Deteksi edge ber-IC 0.03.** Pada IC 0.03, `t_pooled` CONFIRM maksimum **1.97** —
   jauh dari 3.0, di konfigurasi manapun. Kalau edge yang ada di pasar besarnya
   IC 0.03, v6 melaporkan nol, dan itu **bukan** bukti edge-nya tidak ada.
2. **Bahwa panel yang saya usulkan mencapai ρ_PnL 0.10.** Itu **belum diukur**.
   Kalau ρ terukur 0.15, panel harus diubah komposisinya — bukan dipaksakan.
   Ada kemungkinan nyata v6 **berhenti di F0 atau F1**, dan kalau itu terjadi,
   berhenti adalah jawaban yang benar.

### Dan angka yang paling perlu Anda terima

Kendala prop firm mengikat lebih keras daripada edge-nya:

```
risk 0.25%/trade  ->  P(breach) 3.6%   LOLOS  ->  return tahunan ~4.5% (Sharpe 1.15)
risk 1.00%/trade  ->  P(breach) 98.8%  GAGAL
```

Aspirasi "240%/tahun pada risiko 1% per trade" **tidak bisa dijalankan** — bukan
karena kurang agresif, tapi karena pada risiko itu akunnya mati 99 dari 100 kali.

Kalau ~4.5%/tahun tidak layak untuk tujuan Anda, keputusan yang benar adalah mengubah
tujuan atau instrumennya — **bukan** memperbesar ukuran posisi sampai akunnya habis.

---

## Sebelum mulai — yang perlu dikirim

| # | Yang dibutuhkan | Kenapa |
|---|---|---|
| 1 | **Keputusan atas 5 item OVERRIDE V6** di atas | memblokir F0 |
| 2 | **File `DIVISI_X_EXIT_SL_TP_SIZING.md` v5** | tidak ikut terkirim; spesifikasi 22 formula X tidak ada. Jangan jalankan F5 dengan rumus yang ditebak |
| 3 | **File `VIEW_REZIM.md`, `VIEW_TREN.md`, `VIEW_KORELASI.md` v5** | terdaftar di manifest v5 tapi tidak terkirim. Bukan penghalang (view tidak menambah kandidat), tapi berguna |
