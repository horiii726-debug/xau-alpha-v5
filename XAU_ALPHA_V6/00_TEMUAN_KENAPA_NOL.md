# 00 — KENAPA v1–v5 SELALU NOL: TIGA GERBANG YANG MUSTAHIL DILEWATI

> **Baca file ini pertama. Jangan lewati.**
> Semua angka di bawah adalah **hasil hitung**, bukan salinan. Script verifikasinya
> ada di `_verifikasi/` dan WAJIB dijalankan ulang sebelum F0 dikunci.

---

## Ringkasan satu paragraf

Nol survivor lima kali berturut-turut **bukan** karena rumusnya jelek dan **bukan**
karena pasarnya tidak punya edge. Penyebabnya: sistem v5 memasang **tiga gerbang yang
secara matematis tidak bisa dilewati kandidat manapun**, lalu menjalankan 507 kandidat
melewatinya. Gerbang yang membunuh 100% kandidat — yang bagus maupun yang jelek —
tidak menyaring apapun. Informasinya nol. Itu persis alasan yang dipakai v5 sendiri
untuk melarang `B09_PERFECT_FORESIGHT` masuk `must_beat_all`.

Ketiga gerbang itu dipasang tanpa pernah dihitung apakah bisa dilewati.

---

## Temuan 1 🔴 — Ambang t = 3.0 dipasang di partisi TERKECIL

Partisi SCREEN v5 = 313 hari (0.857 tahun), **1 instrumen**, horizon H60.

```
BR_eff   = trades/thn x rasio_keunikan = 400 x 0.18 = 72
IR       = IC x sqrt(BR_eff)           = 0.05 x sqrt(72)   = 0.424
t_single = IR x sqrt(T_tahun)          = 0.424 x sqrt(0.857) = 0.393
K_eff    = 1  (satu instrumen)  ->  t_pooled = 0.393
```

**t maksimum yang bisa dicapai: 0.39. Ambangnya 3.0.**

Untuk mencapai t = 3.0 dari titik itu dibutuhkan sampel **58 kali lipat**.

> Dokumen `DIAGNOSA_DAN_PERBAIKAN.md` menulis t maksimum ≈ 0.81. Angka itu memakai
> BR = 300 **tanpa** mengalikan rasio keunikan. Dengan keunikan 0.18 yang diukur di
> riset sendiri, angka sebenarnya **0.39** — dua kali lebih buruk dari yang dikira.

Ini bukan gerbang ketat. Ini gerbang yang menuntut bukti yang datanya tidak sanggup berikan.

---

## Temuan 2 🔴 — DSR ≥ 0.95 tidak bisa dilewati pada IC yang realistis, **berapapun sampelnya**

Ini temuan yang paling penting dan **tidak ada di dokumen diagnosa manapun sebelumnya.**

DSR membandingkan Sharpe kandidat terhadap **Sharpe maksimum yang muncul dari N trial
karena kebetulan** (`SR_0`), yang dihitung dari **sebaran Sharpe antar trial** (`sd_SR`):

```
DSR = Phi[ (SR_hat - SR_0) * sqrt(T-1) / sqrt(1 - skew*SR + ((kurt-1)/4)*SR^2) ]
```

Perhatikan: kalau `SR_hat < SR_0`, pembilangnya **negatif**. Memperbesar `T` justru
membuat DSR makin kecil. **Menambah sampel tidak menolong sama sekali.**

Sharpe yang DIBUTUHKAN untuk lolos DSR 0.95 (T_confirm 12.65 thn, skew 0, kurt 3):

| N trial | sd_SR 0.20 | sd_SR 0.25 | sd_SR 0.35 | sd_SR 0.50 |
|---:|---:|---:|---:|---:|
| 10 | 0.88 | 0.98 | 1.18 | 1.49 |
| 50 | 1.06 | 1.20 | 1.50 | 1.96 |
| 200 | 1.18 | 1.36 | 1.73 | 2.30 |
| **500** | **1.25** | **1.45** | **1.87** | **2.51** |

Sharpe yang BISA dicapai (konfigurasi terbaik yang realistis — 8 instrumen,
ρ_PnL 0.10, `K_eff` 4.71, `BR_portofolio` 643):

| IC | IR portofolio |
|---:|---:|
| 0.03 | 0.76 |
| **0.05** | **1.27** |
| 0.07 | 1.77 |

**v5 menjalankan N = 507 dengan IC realistis 0.05.**
Sharpe wajib **1.45**, Sharpe tercapai **1.15**. Selisih **0.30 Sharpe** — permanen.

> **Ini kontradiksi internal di dalam dokumen v5 sendiri.** File `00_KONTRAK` menulis
> *"IC sinyal nyata biasanya 0.02–0.05"* DAN `06_GERBANG` menulis *"DSR ≥ 0.95,
> screen_max 500"*. Dua kalimat itu tidak bisa dua-duanya benar. Selama keduanya
> berdiri, hasilnya dijamin nol — di data manapun, dengan rumus apapun.

**N maksimum yang masih meloloskan kandidat IC 0.05:**

| konfigurasi | sd_SR 0.15 | 0.20 | **0.25** |
|---|---:|---:|---:|
| TIER-A (4 instr, 23 thn) — IR 0.92 | 55 | **14** 🔴 | **7** 🔴 |
| TIER-B (8 instr, 14 thn) — IR 1.15 | 43 | **12** 🔴 | **6** 🔴 |
| **TARGET (8 instr, ρ0.10, 20 thn) — IR 1.27** | >3000 | **253** ✅ | **49** ✅ |

🔴 = di bawah LANTAI registri (23) → BERHENTI (§08 D3)

Anggaran kandidat **bukan pilihan gaya kerja**. Dia keluaran dari `sd_SR` yang terukur.
`sd_SR` **WAJIB DIUKUR di F0**. Selama belum diukur, jumlah kandidat yang boleh
dijalankan tidak diketahui.

---

## Temuan 3 🔴 — Gerbang payoff F2 hampir tautologis gagal

F2 bertanya: dengan entry **acak**, adakah `(k_sl, k_tp)` yang mengalahkan titik impas
mekanisnya sendiri pada arm `demeaned`?

**Teorema optional stopping** menjawab pertanyaan itu sebelum satu baris kode dijalankan:
untuk martingale dengan jalur kontinu, **setiap** aturan berhenti memberi `E[PnL] = 0`.
Arm `demeaned` dibuat justru untuk membuang drift — artinya membuat deretnya mendekati
martingale **secara konstruksi**. Maka arm penentu itu **harus** gagal, kecuali ada
ketergantungan JALUR (autokorelasi, klaster volatilitas) yang berinteraksi dengan barrier.

Jadi F2 versi v5 adalah gerbang yang:

- lolos hanya kalau ada struktur jalur — yang itu **sinyal**, bukan "struktur payoff"
- gagal di semua kasus lain **karena teorema, bukan karena pasarnya**
- dan kegagalannya memicu **STOP TOTAL** — memblokir seluruh proyek

Ini kesalahan yang sama persis dengan B09 `PERFECT_FORESIGHT`, dan v5 sudah melarang
B09 dengan alasan itu. F2 lolos dari larangan yang sama hanya karena tidak ada yang
menghitungnya.

---

## Temuan 4 🟠 — Kesalahan kategori: 38 dari 56 formula divisi E bukan sinyal arah

Permutation entropy tidak memberi tahu long atau short. Hurst tidak. Dimensi korelasi
tidak. Lyapunov tidak. Semuanya mengukur **keadaan pasar**, bukan **arah**.

v5 memaksa mereka mengeluarkan arah, lalu menguji mereka dengan `gates.direction`
(17 centang, expectancy bersih, t ≥ 3.0). Itu seperti menilai termometer dari
kemampuannya menebak cuaca besok.

29 di antaranya aktif di v6 sebagai divisi S; 9 sisanya (tier-3 mahal) `PARKED`.

Akibatnya tiga sekaligus:

1. mereka **dijamin gagal** — targetnya bukan yang mereka ukur
2. mereka **menghabiskan anggaran arah** — sekitar 88 varian, dan tiap varian menaikkan `SR_0` untuk semua kandidat lain
3. **router multi-strategi yang Anda minta tidak pernah terbangun**, padahal bahannya sudah ada di situ

Di v6 mereka pindah ke **divisi S (Struktur/Rezim)** dengan gerbang `estimation`
(Model Confidence Set) dan target yang benar-benar terukur.

---

## Temuan 5 🟠 — Parameter `beta` di model slippage salah satuan

v5: `slippage_bps = alpha * spread_bps + beta * sigma_BAR_bps`, dengan `beta` grid `[0, 0.25, 0.5]`.

`sigma_BAR` adalah volatilitas **satu bar penuh** (5–15 menit). Tapi slippage terjadi
antara sinyal dan fill — **hitungan detik**, bukan 5 menit.

| acuan | sigma | slippage pada beta = 0.5 |
|---|---:|---:|
| sigma M5 | 5.89 bps | **2.95 bps** |
| sigma M15 | 10.21 bps | **5.10 bps** |
| sigma 3 detik | 0.59 bps | 0.29 bps |

Karena **seluruh gerbang dihitung pada skenario `worst`** (yang memakai beta 0.5),
satu parameter yang tidak pernah dikalibrasi menentukan hidup-mati seluruh proyek:

| satuan beta | biaya round-trip `worst` @gold 3000 | kappa H240 |
|---|---:|---:|
| `sigma_bar` (v5) | 21.31 bps | **0.522** — membunuh semua kandidat |
| `sigma_latensi` (v6) | 13.36 bps | 0.327 |

> Ini **koreksi satuan**, bukan pelonggaran gerbang. Tapi dia mengubah hasil, jadi
> statusnya **butuh persetujuan tertulis Anda** dan di-hash sebelum F2. Lihat §03.

---

## Temuan 6 🟠 — Dua filter yang saling menyabotase, satu yang tidak terdefinisi

**Filter #16 (≥300 trade/tahun) melawan Filter #1 (expectancy bersih positif).**
Trade sering → holding pendek → biaya makan porsi besar dari gerak → expectancy negatif.
Memenuhi #16 menghancurkan #1. Tidak ada kandidat yang bisa memenuhi keduanya di
horizon pendek dengan biaya prop firm.

Akar masalahnya: **jumlah trade bukan besaran yang benar.** Yang menentukan daya
statistik adalah **jumlah taruhan INDEPENDEN** (Grinold breadth):

| horizon | trade/thn | keunikan | **BR_eff** |
|---|---:|---:|---:|
| H15 | 900 | 0.10 | 90 |
| H60 | 400 | 0.18 | **72** |
| H120 | 300 | 0.35 | 105 |
| **H240** | **220** | **0.62** | **136** |
| H1D | 120 | 0.85 | 102 |

**H240 dengan 220 trade memberi lebih banyak informasi daripada H60 dengan 400 trade.**
Filter #16 di v5 justru mengarahkan sistem ke kolom yang paling miskin informasi.

**Filter #17 (konsisten di ≥60% instrumen panel)** dengan panel 1 instrumen bukan ketat —
dia **tidak terdefinisi**. Dan bahkan dengan panel besar filter ini salah arah: menuntut
konsistensi lintas instrumen berkorelasi adalah menguji apakah sinyal Anda memuat
**faktor bersama** — edge khas emas (real yield, pembelian bank sentral) justru dibunuh.

---

## Temuan 7 🔴 — Kendala prop firm mengikat lebih keras daripada edge-nya

Ini belum pernah dihitung sama sekali karena angka aturan akun masih `LOOKUP`.
Sekarang angkanya ada (lihat §03). Simulasi 30.000 jalur, Sharpe 1.15, 250 trade:

**FundedNext Stellar 1-Step (daily 3%, maxDD 6% statis) — aturan terketat:**

| risk/trade | P(breach 250 trade) | vonis gate ≤5% |
|---:|---:|---|
| 0.15% | 0.04% | LOLOS |
| **0.25%** | **3.58%** | **LOLOS** |
| 0.50% | 45.42% | GAGAL |
| 1.00% | 98.78% | GAGAL |

**Imbal hasil tahunan pada ukuran posisi yang lolos:**

| risk/trade | vol tahunan | return @Sharpe 1.15 |
|---:|---:|---:|
| 0.25% | 3.95% | **4.55%** |
| 0.50% | 7.91% | 9.09% (tapi P(breach) 45%) |

> Aspirasi `K2` di v5 berbunyi *"~240% per tahun pada 300 trade, risiko 1% per trade"*.
> Pada risiko 1% per trade, **P(breach) = 98.8%**. Aspirasi itu bukan agresif —
> secara aritmetika **tidak bisa dijalankan** di akun prop firm manapun.

Frontier keputusan yang sebenarnya (FTMO 2-Step, target +10%):

| risk | Sharpe | P(capai target) | P(breach) | median trade s/d target |
|---:|---:|---:|---:|---:|
| 0.25% | 1.15 | 97.8% | 1.1% | 452 |
| 0.50% | 1.15 | 88.0% | 12.0% | 185 |
| 1.00% | 1.15 | 70.2% | 29.8% | 60 |
| 0.25% | 1.60 | 99.7% | 0.2% | 344 |
| 0.50% | 1.60 | 95.2% | 4.8% | 154 |

**Ukuran posisi bukan detail yang diurus belakangan. Dia menentukan apakah proyeknya
masuk akal sama sekali.**

---

## Temuan 8 — Pola v1 sampai v5

| Versi | Sampel | Kandidat | Ambang | Hasil |
|---|---|---:|---|---|
| v3 | eff N 26 | 112 | t 3.0 | 0 |
| v4 | eff N kecil | 222 | t 3.0 | 0 |
| v5 | 313 hari, 1 instrumen | 507 | t 3.0 | 0 |
| **v6** | **≥20 thn × K_eff ≥4.0** | **≤81, lantai 23** | **corong bertahap, CONFIRM tetap 3.0** | ? |

Yang berubah tiap versi: **jumlah kandidat naik**.
Yang tidak pernah berubah: **ukuran sampel**.

Dan menambah kandidat **memperburuk** — tiap trial baru menaikkan `SR_0` untuk semua
kandidat lain. **507 kandidat di sampel kecil jauh lebih buruk daripada 50 kandidat
di sampel kecil.**

v6 membalik dua-duanya: **sampel naik belasan kali, kandidat turun ~6x.**

---

## Transmitansi gerbang — angka yang merangkum semuanya

**Transmitansi** = `P(kandidat lolos | edge NYATA memang ada)`.
Diukur lewat simulasi 200.000 jalur, memodelkan bahwa gerbang-gerbang itu saling
berkorelasi (mereka mengukur ulang besaran yang sama), bukan independen.

| konfigurasi | t tercapai | **transmitansi** |
|---|---:|---:|
| v5: 17 gerbang di partisi SCREEN | 0.39 | **0.17%** |
| v5: 17 gerbang seandainya t = 2.0 | 2.00 | 11.5% |
| v5: 17 gerbang seandainya t = 3.5 | 3.50 | 63.9% |
| **v6 corong @ TIER-A** (4 instr, 23 thn) | 2.21 / 3.28 | **24.8%** 🔴 |
| **v6 corong @ TIER-B** (8 instr, 14 thn) | 2.16 / 3.20 | **21.6%** 🔴 |
| **v6 corong @ TARGET** (8 instr, ρ 0.10, 20 thn) | 2.83 / 4.20 | **64.7%** ✅ |
| **v6 corong @ TARGET+** (8 instr, ρ 0.10, 23 thn) | 3.04 / 4.51 | **75.9%** ✅ |

Gerbang v5 meloloskan **1 dari 588** sinyal yang benar-benar punya edge.
Gerbang v6 pada konfigurasi TARGET meloloskan **2 dari 3**.

> 🔴 **PERINGATAN YANG PALING PENTING:** corong saja **tidak cukup**. Pada TIER-A dan
> TIER-B transmitansi hanya naik ke ~22–25%, **masih di bawah gerbang mati GM-3 (50%)**.
> Yang membuatnya lolos adalah **kombinasi** corong + `ρ_PnL ≤ 0.10` + riwayat ≥ 20 thn.
> **Memperbaiki gerbang tanpa memperbaiki sampel tetap menghasilkan nol.**

> **Ambang CONFIRM tidak diubah satu titik pun.** Tetap 17 centang, tetap t ≥ 3.0,
> tetap DSR, tetap PBO, tetap MC2. Yang berubah cuma dua hal:
> **(a) kapan tiap gerbang dipasang, dan (b) berapa besar sampel di bawahnya.**

---

## Apa yang bukan penyebabnya

Supaya jelas apa yang **tidak** perlu diperbaiki:

- **Bukan rumusnya.** F6 (55 sinyal entry) belum pernah benar-benar dijalankan — masih `PENDING`. Vonis apapun soal kualitas rumus masih prematur.
- **Bukan alat ukurnya.** F1 lulus 30/30 test, uji kebocoran IC 0.80 mengalahkan 8 null. Infrastrukturnya sehat.
- **Bukan divisi V dan Q.** Mereka **punya survivor**: Bipower variation, MedRV, Corwin-Schultz. Alat ukur volatilitas dan spread sudah punya juara.
- **Bukan meta-labeling.** Sudah terbukti menaikkan sinyal mentah. Mekanismenya hidup.

Empat hal itu **dibawa utuh ke v6**. Nol kode dibuang.

---

## Urutan keputusan yang memblokir F0

Tidak boleh menghitung `screen_max` sebelum lima hal ini diputuskan:

| # | Keputusan | Konsekuensi kalau tidak diputuskan |
|---|---|---|
| 1 | Korong bertingkat (§07) menggantikan 17-sekaligus-di-screening | transmitansi tetap 0.17%, hasil dijamin nol |
| 2 | F2 jadi PENGUKURAN, bukan STOP TOTAL (§05) | proyek terblokir di gerbang yang gagal karena teorema |
| 3 | Koreksi satuan `beta` slippage (§03) | kappa `worst` 0.52, semua kandidat mati di biaya |
| 4 | Ledger dipisah arah vs estimasi (§08) | `SR_0` dihitung dari N yang salah, DSR mustahil |
| 5 | `sd_SR` diukur di F0 sebelum anggaran dikunci | jumlah kandidat yang aman tidak diketahui |
| 6 | Syarat kelayakan gabungan §01 B4b (`K_eff ≥ 4.0` **DAN** `T_confirm ≥ 11 thn`) | corong lolos di atas kertas tapi transmitansi nyata < 50% → nol lagi |

Keenamnya **OVERRIDE V6 tertulis** (§O8). Diputuskan **sebelum** F0 selesai, bukan
setelah melihat hasil.

---

**Lanjut ke `01_KONTRAK_DAN_POWER.md`.**
