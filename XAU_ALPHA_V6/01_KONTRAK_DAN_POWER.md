# 01 — KONTRAK KEJUJURAN & ANALISIS DAYA

> Menggantikan `00_KONTRAK_DAN_KELAYAKAN.md` v5. Perubahan ditandai 🔄.
> Semua tabel WAJIB dihitung ulang dari rumusnya. Kalau hasil hitung beda, **pakai
> hasil hitung dan laporkan**.

---

## Bagian A — Kontrak kejujuran

### K1 — "Jangan sampai yang lolos 0"

| | |
|---|---|
| **Status** | TIDAK BISA DIJANJIKAN |
| **Alasan** | Sistem validasi jujur HARUS bisa mengeluarkan nol. Sistem yang dijamin menghasilkan pemenang berarti gerbangnya tidak menyaring apapun — itu mesin pembenaran, bukan mesin riset. |

**🔄 Yang berubah di v6:** v5 menjawab keluhan ini dengan *"memperbesar sampel"* — tapi
tidak pernah melakukannya. v6 melakukannya, dan menambah satu hal yang v5 tidak punya:

> **Transmitansi gerbang diukur SEBELUM kandidat pertama dijalankan** (§07, uji `L11`).
> Kalau gerbangnya membunuh sinyal sintetis ber-IC 0.05 lebih dari 50% waktu,
> **gerbangnya yang diperbaiki, bukan ambangnya yang diturunkan.**

Itu bedanya antara "nol karena pasarnya memang tidak memberi" dan "nol karena alat
ukurnya rusak". v1–v5 tidak pernah bisa membedakan keduanya. v6 bisa.

Kalau setelah semua ini hasilnya tetap nol **dengan transmitansi terukur > 50%**, itu
temuan nyata tentang pasarnya. Wajib dilaporkan apa adanya. Jauh lebih murah daripada
menemukannya lewat akun yang habis.

### K2 — "60% win rate dengan RR 1:2"

| | |
|---|---|
| **Status** | DICATAT SEBAGAI ASPIRASI, BUKAN GERBANG |

Aritmetika yang sudah terukur di riset sendiri:

```
barrier k_sl=1.5 / k_tp=2.5 (RR 1:1.67)
breakeven mekanis : 37.50%
hit rate aktual   : 37.86%     <- margin 0.36 poin persen, SEBELUM biaya
coin flip net     : 40.49%
```

Pasar memberi ~38% pada RR 1.67. Menuntut 60% pada RR 2.0 menuntut IC jauh di atas 0.15,
sementara IC sinyal nyata 0.02–0.05.

**🔄 Tambahan v6 — angka yang sebelumnya tidak pernah dihitung:**

Aspirasi itu berbunyi *"~240%/tahun pada 300 trade, risiko 1% per trade"*.
Pada risiko 1% per trade di aturan prop firm terketat, **P(breach) = 98.8%**.

Bukan agresif. **Tidak bisa dijalankan.** Ukuran posisi yang lolos MC2 adalah
**≤0.25% per trade**, yang pada Sharpe 1.15 memberi **~4.5% per tahun**.

Itu angka jujurnya. Kalau angka itu tidak layak untuk tujuan Anda, keputusan yang
benar adalah mengubah tujuan atau instrumennya — **bukan** memperbesar ukuran posisi
sampai akunnya mati.

**Keputusan:** gerbang dinilai pada **expectancy bersih setelah biaya**, bukan win rate.
Kombinasi apapun yang expectancy-nya positif dan lolos seluruh uji = LULUS, meski win
rate 40%. Menyetel sistem mengejar angka win rate tertentu = definisi overfitting.

### K3 — "Banyak kandidat biar hasilnya tidak 0"

| | |
|---|---|
| **Status** | 🔄 **DIBALIK.** Menambah kandidat adalah penyebab nol, bukan obatnya. |

Bukti aritmetiknya ada di §00 Temuan 2. Ringkasnya: tiap trial baru menaikkan `SR_0`
(Sharpe maksimum yang muncul dari kebetulan), dan `SR_0` adalah tembok yang harus
dilewati kandidat Anda. Pada 507 trial, temboknya **1.45 Sharpe**; kandidat IC 0.05
hanya sanggup **1.15**.

**Aturan mengikat v6:**

```
Jumlah kandidat yang boleh DIJALANKAN = keluaran dari sd_SR yang TERUKUR di F0.
Bukan keinginan. Bukan negosiasi.

Pencarian ide       : TIDAK DIBATASI (gratis, tidak masuk ledger)
Yang dibatasi       : jumlah yang dijalankan di data
```

---

## Bagian B — Analisis daya

### B1 — Fundamental Law (Grinold)

```
IR = IC * sqrt(BR_eff)
```

| simbol | arti |
|---|---|
| `IR` | information ratio ≈ Sharpe strategi |
| `IC` | korelasi antara sinyal dan return berikutnya |
| `BR_eff` | jumlah taruhan **INDEPENDEN** per tahun |

**`BR_eff` bukan jumlah trade.** Label yang tumpang tindih tidak independen:

```
BR_eff_single = trades_per_tahun x rasio_keunikan_sampel
```

| horizon | trade/thn | keunikan | BR_eff | IR@IC 0.03 | IR@IC 0.05 |
|---|---:|---:|---:|---:|---:|
| H15 | 900 | 0.10 | 90 | 0.285 | 0.474 |
| H60 | 400 | 0.18 | 72 | 0.255 | 0.424 |
| H120 | 300 | 0.35 | 105 | 0.307 | 0.512 |
| **H240** | **220** | **0.62** | **136** | **0.350** | **0.584** |
| H1D | 120 | 0.85 | 102 | 0.303 | 0.505 |

> Angka `trade/thn` dan `keunikan` di tabel ini adalah **rencana, bukan pengukuran**.
> WAJIB DIUKUR di F0 per instrumen per horizon. Kalau berbeda, tabel ini diganti
> dengan hasil ukur dan seluruh anggaran dihitung ulang.

### B2 — 🔄 BR harus dihitung LINTAS PANEL

Ini yang v5 lewatkan. Menjalankan sinyal yang sama di panel `K` instrumen tidak
mengalikan taruhan dengan `K` — mengalikannya dengan `K_eff`:

```
BR_eff_portofolio = BR_eff_single * K_eff
IR_portofolio     = IC * sqrt(BR_eff_portofolio) = IR_single * sqrt(K_eff)
```

Konsisten dengan `t_pooled = t_single * sqrt(K_eff)` — dua-duanya naik `sqrt(K_eff)`.
**Panel menaikkan daya statistik DAN Sharpe portofolio sekaligus.** Itu sebabnya
memperbesar panel adalah pengungkit terkuat yang tersisa.

```
BR_eff_single H240      = 136
K_eff panel 8 @rho 0.15 = 3.90
BR_eff_portofolio       = 532
IR_portofolio @IC 0.05  = 1.154
```

### B3 — `K_eff` — jumlah instrumen independen efektif

```
metode 1 (WAJIB, dipakai sebagai angka resmi):
  K_eff = (SUM lambda_i)^2 / SUM(lambda_i^2)
  lambda = eigenvalue matriks korelasi PnL STRATEGI antar instrumen

metode 2 (perkiraan perencanaan saja):
  K_eff = K / (1 + (K-1)*rho_bar)
```

Tabel metode 2 — **wajib dihitung ulang, jangan disalin:**

| K | ρ=0.05 | ρ=0.10 | ρ=0.15 | ρ=0.20 | ρ=0.30 |
|---:|---:|---:|---:|---:|---:|
| 1 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 4 | 3.48 | 3.08 | 2.76 | 2.50 | 2.11 |
| 6 | 4.80 | 4.00 | 3.43 | 3.00 | 2.40 |
| **8** | 5.93 | 4.71 | **3.90** | 3.33 | 2.58 |
| 15 | 8.82 | 6.25 | 4.84 | 3.95 | 2.88 |
| 25 | 11.36 | 7.35 | 5.43 | 4.31 | 3.05 |

> ⚠️ Korelasi yang dihitung HARUS korelasi **PnL STRATEGI**, BUKAN korelasi harga.
> Dua instrumen bisa berkorelasi harga tinggi tapi PnL strateginya rendah, dan sebaliknya.
>
> ⚠️ Panel dipilih untuk **MEMINIMALKAN korelasi PnL**, bukan memaksimalkan jumlah
> instrumen. 8 instrumen tidak berkorelasi lebih berharga daripada 25 instrumen
> yang saling berkorelasi 0.3 — lihat baris K=8 ρ=0.05 (5.93) vs K=25 ρ=0.30 (3.05).

### B4 — Deteksi statistik

```
t_single = IR_single * sqrt(T_tahun)
t_pooled = t_single * sqrt(K_eff)
```

> ⚠️ **KOREKSI PENTING.** Draf awal v6 menghitung `t_pooled` dengan mencampur
> **riwayat panjang** (23 tahun, hanya tersedia untuk 4 instrumen) dengan **K_eff panel
> penuh** (3.90, hanya tersedia kalau 8 instrumen ada). Dua-duanya tidak bisa benar
> bersamaan. Tabel di bawah menghitung tiap konfigurasi secara **konsisten**.

**Dua konfigurasi yang benar-benar mungkin** (angka riwayat WAJIB diganti hasil audit F0):

| | TIER-A | TIER-B |
|---|---|---|
| instrumen | 4 (XAU, XAG, EUR, JPY) | 8 (panel penuh) |
| ρ_PnL asumsi | 0.20 | 0.15 |
| **K_eff** | **2.50** | **3.90** |
| riwayat bersama | 23 thn | 14 thn |
| `BR_portofolio` | 341 | 532 |
| **`IR_portofolio` @IC 0.05** | **0.923** | **1.154** |
| t_pooled SCREEN (25%) | **2.21** | **2.16** |
| **t_pooled CONFIRM (55%)** | **3.28** | **3.20** |
| t_pooled HOLDOUT (20%) | 1.98 | 1.93 |
| CONFIRM @IC 0.03 pesimistis | 1.97 | 1.92 |

**Dua-duanya melewati ambang 3.0 di CONFIRM — tapi dengan margin tipis, bukan 4.10
seperti yang ditulis draf awal.** Dan dua-duanya **GAGAL** gerbang transmitansi GM-3
(§07). Lihat B4b.

### B4b — 🔴 Syarat kelayakan gabungan: ρ_PnL adalah pengungkit yang menentukan

Transmitansi rantai penuh (§07) dihitung untuk berbagai konfigurasi:

| K | ρ_PnL | K_eff | riwayat | t_screen | t_confirm | **transmitansi rantai** |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 0.20 | 2.50 | 23 thn | 2.21 | 3.28 | **24.6%** 🔴 |
| 8 | 0.15 | 3.90 | 14 thn | 2.16 | 3.20 | **21.6%** 🔴 |
| 6 | 0.15 | 3.43 | 20 thn | 2.42 | 3.59 | 37.2% 🔴 |
| 8 | 0.15 | 3.90 | 20 thn | 2.58 | 3.83 | 48.4% 🔴 |
| **6** | **0.10** | **4.00** | **20 thn** | **2.61** | **3.87** | **50.4%** ✅ |
| **8** | **0.10** | **4.71** | **20 thn** | **2.83** | **4.20** | **64.7%** ✅ |
| **8** | **0.10** | **4.71** | **23 thn** | **3.04** | **4.51** | **75.9%** ✅ |
| **10** | **0.10** | **5.26** | **20 thn** | **3.00** | **4.44** | **73.7%** ✅ |

**Yang dibaca dari tabel ini:**

1. **`ρ_PnL` lebih menentukan daripada jumlah instrumen.** K=8 pada ρ=0.15 memberi
   48.4%; K=6 pada ρ=0.10 memberi 50.4% — **panel lebih kecil tapi lebih tidak
   berkorelasi MENANG.** Ini persis peringatan yang sudah ada sejak v5 dan sekarang
   ada angkanya.
2. **Riwayat 14 tahun tidak cukup**, berapapun panelnya, pada ρ=0.15.
3. Konfigurasi yang lolos butuh **ρ_PnL ≤ 0.10 DAN riwayat ≥ 20 tahun**.

```yaml
syarat_kelayakan_gabungan_F0:
  # Diukur di F0. Bukan asumsi. Ini yang menentukan proyek jalan atau tidak.
  wajib_terpenuhi_BERSAMAAN:
    K_eff_terukur: ">= 4.0"
    T_confirm_terukur: ">= 11.0 tahun"
  konsekuensi_kalau_tidak_terpenuhi: >
    Transmitansi rantai di bawah 50% -> GM-3 -> BERHENTI.
    Pilihan yang sah: (a) cari instrumen dengan korelasi PnL lebih rendah sampai
    K_eff >= 4.0, (b) perpanjang riwayat bersama, (c) terima bahwa data yang ada
    tidak cukup dan laporkan. DILARANG melanjutkan dengan berharap.
  catatan_penting: >
    Panel 8 instrumen yang saya usulkan (XAU, XAG, EUR, JPY, US100, US30, USOIL,
    NATGAS) BELUM TENTU mencapai rho_PnL 0.10. Itu WAJIB DIUKUR. Kalau rho terukur
    0.15, panel harus diubah komposisinya — bukan dipaksakan.
```

> **Pernyataan jujur yang wajib dicantumkan di setiap laporan:**
> Desain v6 sanggup mendeteksi edge pada **IC 0.05** HANYA kalau syarat gabungan di
> atas terpenuhi. Pada **IC 0.03 dia tidak sanggup** di konfigurasi manapun
> (`t_pooled` CONFIRM maksimum 1.97). Kalau edge yang ada di pasar besarnya IC 0.03,
> proyek ini akan melaporkan nol — dan itu **bukan** bukti edge-nya tidak ada.

### B5 — 🔄 Anggaran kandidat diturunkan dari DSR

Blok ini tidak ada di v5, dan ketiadaannya adalah penyebab utama nol.

```
SR_0 = sqrt(Var_SR) * [ (1-gamma)*Phi^-1(1 - 1/N) + gamma*Phi^-1(1 - 1/(N*e)) ]
gamma = 0.5772156649 (Euler-Mascheroni)

DSR = Phi[ (SR_hat - SR_0)*sqrt(T-1) / sqrt(1 - skew*SR_hat + ((kurt-1)/4)*SR_hat^2) ]
```

**Syarat kelayakan anggaran:** `N_maks` = N terbesar yang masih memenuhi `DSR >= 0.95`.

**`N_maks` per konfigurasi** (skew 0, kurt 3 — WAJIB diganti momen empiris):

| konfigurasi | `IR_port` | `T_cnf` | sd_SR 0.10 | 0.15 | 0.20 | 0.25 |
|---|---:|---:|---:|---:|---:|---:|
| TIER-A (4 instr, 23 thn) | 0.923 | 12.65 | 2240 | 55 | **14** 🔴 | **7** 🔴 |
| TIER-B (8 instr, 14 thn) | 1.154 | 7.70 | 1329 | 43 | **12** 🔴 | **6** 🔴 |
| **TARGET (8 instr, ρ 0.10, 20 thn)** | **1.267** | **11.00** | >3000 | >3000 | **253** ✅ | **49** ✅ |

🔴 = di bawah LANTAI registri (23) → §08 D3 **BERHENTI**

**Dua hal yang dibaca dari tabel ini:**

1. **`sd_SR` adalah kendala yang paling mengikat.** Pada konfigurasi TARGET, turun dari
   sd 0.25 ke 0.20 menaikkan `N_maks` dari 49 ke 253 — **lima kali lipat**. Tidak ada
   pengungkit lain sekuat ini.
2. **Pada TIER-A dan TIER-B, `N_maks` di bawah lantai registri.** Artinya: pada
   konfigurasi itu, **tidak ada registri sekecil apapun yang bisa lolos DSR** kecuali
   `sd_SR` ≤ 0.15.

**Prosedur mengikat di F0:**

1. Jalankan **pilot 24 trial** yang mewakili seluruh keluarga formula
2. Ukur `sd_SR` **empiris** dari 24 Sharpe itu (bukan diasumsikan)
3. Ukur `skew` dan `kurt` empiris dari distribusi return kandidat
4. Hitung `N_maks` dari rumus di atas
5. `anggaran_arah = min(81, N_maks)`
6. Kalau `N_maks < 23` (LANTAI) → **BERHENTI**. Lihat §08 D3.

> **`sd_SR` sebagian bisa dikendalikan, dan itu satu-satunya kabar baik di blok ini.**
> Trial yang semuanya varian dari sedikit keluarga, diuji dengan cara sama, akan punya
> Sharpe yang berkerumun → `sd_SR` kecil → `N_maks` besar. Melempar 507 hal yang tidak
> berhubungan ke satu ledger membuat `sd_SR` besar dan `N_maks` runtuh.
>
> **Registri yang fokus bukan cuma lebih murah — secara matematis dia lebih mungkin
> menghasilkan survivor.** Kebalikan total dari strategi v1–v5.

### B6 — Yang WAJIB DIUKUR di F0

Semua di bawah adalah **PENGUKURAN**, bukan asumsi. Anggaran dihitung DARI hasil ini.

| # | Yang diukur | Menentukan |
|---|---|---|
| 1 | rasio keunikan sampel per instrumen per horizon | `BR_eff` |
| 2 | matriks korelasi **PnL strategi** baseline antar instrumen | `K_eff` |
| 3 | `K_eff` lewat metode eigenvalue | `t_pooled`, `BR_portofolio` |
| 4 | 🔄 `sd_SR` dari pilot 24 trial | **`N_maks` — anggaran kandidat** |
| 5 | 🔄 `skew`, `kurt` empiris return kandidat | penyebut DSR |
| 6 | 🔄 transmitansi gerbang (uji `L11`) | apakah corongnya berfungsi |
| 7 | ketersediaan riwayat per instrumen | jendela pooling (TIER-A vs TIER-B) |
| 8 | spread terukur per sesi per jam, dalam bps | model biaya |
| 9 | 🔄 `P(breach)` per ukuran posisi (MC2) | ukuran posisi maksimum |

### B7 — Gerbang mati F0

```
GM-1  K_eff terukur < 3.0                      -> BERHENTI.
      (ambang v5 dipertahankan APA ADANYA. Draf awal v6 sempat menurunkannya
       ke 2.5 tanpa deklarasi — itu pelonggaran tidak sah dan sudah dibatalkan.)

GM-1b K_eff >= 3.0 TAPI syarat gabungan B4b tidak terpenuhi
      (K_eff < 4.0 ATAU T_confirm < 11 thn)     -> BERHENTI. Transmitansi < 50%.

GM-2  N_maks dari sd_SR < 23 (LANTAI registri) -> BERHENTI. Lihat §08 D3.

GM-3  transmitansi corong (uji L11) < 50%      -> BERHENTI. Perbaiki GERBANGNYA.
                                                  DILARANG menurunkan ambang.

GM-4  t_pooled CONFIRM @IC 0.05 < 3.0          -> BERHENTI. Data tidak cukup.

GM-5  P(breach) > 5% di ukuran posisi TERKECIL  -> BERHENTI untuk akun prop firm.
      yang masih memenuhi BR_eff >= 100/thn        Strateginya mungkin nyata tapi
                                                   tidak muat di kendala akunnya.
```

**DILARANG melanjutkan dengan berharap.**

---

## Bagian C — Anggaran komputasi

Aturan utama tidak berubah: **formula murah dijalankan penuh, formula mahal hanya
untuk survivor atau pada subsampel.**

| tier | kompleksitas | aturan |
|---|---|---|
| **T1 murah** | O(n) / O(n log n); O(1)..O(w) per bar | jalankan penuh di seluruh panel & horizon terpilih |
| **T2 sedang** | O(n log n) berat; O(w²) per bar dengan w ≤ 96 | jalankan penuh, batasi jendela terpanjang, wajib vektorisasi/Numba. Ukur waktu di F1 dulu. |
| **T3 mahal** | O(n²) global; O(w²)..O(w³) per bar dengan w ≥ 288 | **DILARANG penuh saat screening.** Subsampel 20% partisi screen di 5 instrumen paling tidak berkorelasi. Yang lolos ambang awal baru dijalankan penuh. |

**Aturan tier:** setiap formula WAJIB punya **tepat satu** tier. Diverifikasi otomatis di F1.

**Kejujuran subsampel:** subsampel MENURUNKAN daya uji. Kandidat T3 yang gagal di
subsampel WAJIB ditandai `UNDERPOWERED_SCREEN`, **bukan** `REJECTED`.

**🔄 Perbaikan dari audit v5:**
- `E72_THEIL_SEN` (kini `MOM07`) dikonfirmasi **T2** (dua-duanya O(w²) per bar). Wajib implementasi bergulir inkremental **atau** batasi `w ≤ 48`.
- `E72` **dikeluarkan dari pilot set** F2b — v5 mengklaim pilot "semua tier-1" padahal E72 tier-2. Diganti `E70_MANN_KENDALL` (tier-1, keluarga tren yang sama).

**Wajib dilaporkan di F1:**
- waktu eksekusi per formula per instrumen per horizon (**diukur**, bukan ditebak)
- estimasi total jam komputasi untuk F4–F8
- kalau estimasi > 72 jam: **BERHENTI**, lapor, usulkan pemangkasan

---

**Lanjut ke `02_HUKUM.md`.**
