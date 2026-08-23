# 08 — ANGGARAN KANDIDAT, TANGGA PEMANGKASAN & LEDGER

> 🔄 Anggaran v6 **diturunkan dari syarat kelayakan DSR**, bukan dipilih.
> v5 memilih 500 tanpa pernah memeriksa apakah 500 bisa dilewati. Tidak bisa.

---

## Bagian A — Ledger dipisah per masalah seleksi (§O10)

```yaml
ledger_arah.csv:
  isi: "divisi E1/E2/E3 (MOM/MRV/BRK), X, M, ROUTER"
  seleksi: threshold_only, forbid_argmax
  dipakai_untuk: "N pada DSR dan BH-FDR"

ledger_estimasi.csv:
  isi: "divisi V, Q, T, S"
  seleksi: model_confidence_set alpha=0.10
  dipakai_untuk: "MCS. TIDAK masuk N untuk DSR — masalah seleksi berbeda."

ledger_diagnostik.csv:
  isi: "F2 pengukuran payoff, uji L10/L11/L12e, kalibrasi biaya, dedup"
  dipakai_untuk: "diagnostik. BUKAN seleksi strategi. TIDAK masuk N manapun."
```

**Aturan penentu:** sebuah trial masuk `ledger_arah` **jika dan hanya jika** hasilnya
bisa menyebabkan sebuah **aturan arah** dipilih atau dibuang.

> ⚠️ **Perubahan material.** v5 menghitung DSR dari satu ledger gabungan, sehingga
> 74 trial estimasi menaikkan `SR_0` untuk kandidat arah tanpa alasan statistik.
> Perubahan ini menaikkan anggaran efektif dan **butuh persetujuan tertulis Anda.**

**Kolom ledger (semua ledger):**

```
trial_id, timestamp, candidate_id, formula_id, division, family, prior_sign,
instrument_set, horizon, params_hash, partition, stage, n_trades, eff_n, br_eff,
ic, t_stat, p_raw, p_effN, expectancy_bps_worst, sharpe, max_dd, capture_ratio,
flags, status, notes
```

**Aturan ledger:**

- Sweep 42 kombinasi = **42 baris**
- Percobaan gagal/dibatalkan/error **TETAP dicatat**
- Panel 1 hipotesis di 8 instrumen = **1 BARIS** (satu hipotesis)
- Grid hyperparameter ML 8 kombinasi = **8 baris**
- Ledger dimulai **KOSONG**. Trial v3/v4/v5 tidak diwarisi — instrumen, horizon, riwayat, dan struktur label berbeda.
- 🔄 Kolom `stage` wajib: `SCREENING` / `ROBUSTNESS` / `CONFIRM`

---

## Bagian B — Aturan anggaran

```yaml
trial_budget:
  # 🔄 Rumus v5 (screen_max = min(500, 50*K_eff)) DIHAPUS.
  # Alasan: tidak pernah memeriksa apakah N-nya bisa lolos DSR. Tidak bisa.

  rumus_v6:
    langkah_1: "F0 ukur sd_SR empiris dari pilot 24 trial"
    langkah_2: "F0 ukur skew & kurt empiris return kandidat"
    langkah_3: |
      Hitung N_maks = N terbesar yang masih memenuhi:
        SR_0(N, sd_SR) + 1.645*sqrt(1 - skew*SR + ((kurt-1)/4)*SR^2)/sqrt(T_confirm - 1)
          <= SR_portofolio_tercapai
      dengan SR_portofolio = IC_dasar * sqrt(BR_eff_single * K_eff)
    langkah_4: "anggaran_arah = min(82, N_maks)"   # BUKAN max(LANTAI, ...) — lihat catatan
    langkah_5: "kalau N_maks < LANTAI -> BERHENTI. Lihat Bagian D."

  LANTAI: 23        # dihitung di Bagian D — diakui eksplisit, tidak disembunyikan
  PLAFON: 82        # = ukuran registri penuh v6

  catatan_lantai: >
    LANTAI adalah ukuran registri terkecil yang masih bisa menguji ketiga keluarga.
    Dia BUKAN batas bawah anggaran. Kalau N_maks < 23, anggaran TIDAK dinaikkan ke 23 —
    proyek BERHENTI (§D3). Menjalankan registri lebih besar dari N_maks berarti
    menjalankan sesuatu yang dijamin gagal DSR, dan itu yang terjadi lima kali.

  confirm_max: 8
  confirm_max_locked: true
  holdout_shots: 1
  naikkan_butuh: "OVERRIDE V6 tertulis dari user"
```

**N maksimum terhadap `sd_SR`** — bergantung konfigurasi sampel (§01 B5):

| konfigurasi | `IR_port` | `T_cnf` | sd 0.15 | sd 0.20 | sd 0.25 |
|---|---:|---:|---:|---:|---:|
| TIER-A (4 instr, 23 thn) | 0.923 | 12.65 | 55 | **14** 🔴 | **7** 🔴 |
| TIER-B (8 instr, 14 thn) | 1.154 | 7.70 | 43 | **12** 🔴 | **6** 🔴 |
| **TARGET (8 instr, ρ 0.10, 20 thn)** | **1.267** | **11.00** | >3000 | **253** ✅ | **49** ✅ |

🔴 = di bawah LANTAI 23 → §D3 **BERHENTI**

**Vonis untuk registri v6 (82 varian):** hanya lolos di konfigurasi TARGET dengan
`sd_SR ≤ 0.20`. Di semua konfigurasi lain, registri **wajib dipangkas** lewat tangga
§D2 — dan pada TIER-A/TIER-B dengan `sd_SR ≥ 0.20`, bahkan LANTAI 23 pun terlalu besar.

> **`sd_SR` sebagian bisa dikendalikan.** Registri yang fokus — sedikit keluarga,
> diuji dengan cara yang sama — menghasilkan Sharpe yang berkerumun, `sd_SR` kecil,
> `N_maks` besar. Melempar 507 hal yang tidak berhubungan ke satu ledger membuat
> `sd_SR` besar dan `N_maks` runtuh.
>
> **Registri yang fokus bukan cuma lebih murah — secara matematis dia lebih mungkin
> menghasilkan survivor.** Ini kebalikan total dari strategi v1–v5.

---

## Bagian C — Komposisi registri v6

### C1 — Ledger arah: 42 formula / **82 varian**

| divisi | formula | varian |
|---|---:|---:|
| E1 MOMENTUM | 11 | 20 |
| E2 MEAN REVERSION | 6 | 12 |
| E3 BREAKOUT | 7 | 14 |
| X EXIT & SIZING | 10 | 20 |
| M ML & META-LABELING | 5 | **12** (grid dipangkas dari 32 — lihat catatan) |
| ROUTER MULTI-STRATEGI | 3 | 4 |
| **TOTAL** | **42** | **82** |

> 🔄 **Catatan divisi M:** grid v5 untuk 5 formula yang disisakan berjumlah **32 varian**
> (M01 8, M02 8, M06 4, M07 4, M11 8). v6 memangkasnya jadi **12**:
> M06 → 2 (`lambda` [0.01, 0.1]), M07 → 2 (`lambda` [0.1, 1.0]),
> M11 → 4 (`primary` × `threshold`, `secondary_model` dikunci ke M06),
> M01 → 2, M02 → 2. Pemangkasan ini **wajib** — §06 E: grid ML ≤ 8 per model,
> dan 32 varian ML saja sudah melebihi `N_maks` di sebagian besar konfigurasi.

**Perbandingan v5 → v6: 507 → 82 varian (−84%).**
Sementara sampel naik dari 0.86 thn × K_eff 1 ke ≥11 thn × K_eff ≥4.0 (§01 B4b).

**12 formula baru dari jurnal/SSRN** (sitasi terverifikasi — lihat `REFERENSI_TERVERIFIKASI.md`):
MOM08, MOM09, MOM10, MOM11, MRV02, MRV03, MRV04, MRV05, BRK01, BRK02, BRK03, BRK04.

### C2 — Ledger estimasi: 65 formula / **132 varian**

| divisi | formula | varian | catatan |
|---|---:|---:|---|
| V volatilitas | 14 | **41** | dibawa **utuh** dari v5; V07 Bipower & V08 MedRV **sudah LOLOS** |
| Q spread & likuiditas | 12 | **35** | dibawa **utuh**; Q02 Corwin-Schultz **sudah LOLOS** |
| T intensitas tick | 10 | **27** | `PARKED` sampai data tick tersedia |
| **S struktur & rezim** | **29** | **29** | 🔄 **BARU** — 1 varian per formula |
| **TOTAL** | **65** | **132** | |

> 🔄 **Koreksi:** draf awal v6 menulis 75 varian untuk blok ini. Itu salah — file
> `DIVISI_V/Q/T` dibawa **verbatim** dari v5 dengan grid parameter utuh (41/35/27),
> bukan dipangkas. Angka yang benar **132**.
>
> **Ini tidak menaikkan tekanan pada DSR** karena `ledger_estimasi` terpisah dari
> `ledger_arah` (§O10) dan diseleksi lewat MCS, bukan Sharpe. Yang naik hanya
> **biaya komputasi** — dan itu wajib dilaporkan di F1 (§01 Bagian C).
>
> Kalau anggaran komputasi F1 menunjukkan > 72 jam, pangkas V/Q ke jendela tengah
> (1 varian per formula) → 14+12+27+29 = **82 varian**, atau `PARKED`-kan T → **55**.

### C3 — 🔄 Divisi S: 29 formula yang dipindah dari divisi E

**Kesalahan kategori v5:** formula-formula ini tidak memberi arah. Permutation entropy
tidak bilang long atau short. Hurst tidak. VR tidak (`sign(VR-1)` untuk tren,
`-sign(VR-1)` untuk balik arah — **ambiguitas itu sendiri bukti bahwa VR mengukur
rezim, bukan arah**).

Mereka pindah ke gerbang `estimation` dengan target yang benar-benar terukur, dan
mereka **memberi bahan untuk router multi-strategi** (§09).

| keluarga | formula |
|---|---|
| **Persistensi & rasio varians** (3) | `E10_VARIANCE_RATIO_LM`, `E11_VARIANCE_RATIO_WRIGHT`, `E12_AUTOMATIC_VARIANCE_RATIO` |
| **Memori panjang & dimensi fraktal** (8) | `E20_HURST_RS`, `E21_MODIFIED_RS_LO`, `E22_DFA_ALPHA`, `E23_MFDFA_WIDTH`, `E24_HIGUCHI_FD`, `E25_KATZ_FD`, `E26_PETROSIAN_FD`, `E27_RANGE_ROUGHNESS_RATIO` |
| **Entropi & kompleksitas** (7) | `E30_SHANNON_ENTROPY_SIGN`, `E31_APPROXIMATE_ENTROPY`, `E32_SAMPLE_ENTROPY`, `E33_PERMUTATION_ENTROPY`, `E34_WEIGHTED_PERMUTATION_ENTROPY`, `E35_DISPERSION_ENTROPY`, `E36_LEMPEL_ZIV_COMPLEXITY` |
| **Spektral, siklus & fase** (6) | `E50_FFT_DOMINANT_PERIOD`, `E51_HILBERT_INSTANT_PHASE`, `E52_HILBERT_INSTANT_FREQUENCY`, `E53_WAVELET_SCALE_ENERGY`, `E54_SPECTRAL_ENTROPY`, `E55_SSA_COMPONENT_SHARE` |
| **Momen realized & lompatan** (4) | `E61_LEE_MYKLAND_JUMP`, `E62_BIPOWER_JUMP_RATIO`, `E64_REALIZED_SKEWNESS`, `E65_REALIZED_KURTOSIS` |
| **Anomali struktural** (1) | `E93_MATRIX_PROFILE_DISCORD` |

**`PARKED` di v6 (9 formula, tier-3 mahal, tidak dijalankan):**
`E40_LYAPUNOV`, `E41_RQA_DET`, `E42_RQA_LAM`, `E43_CORR_DIM`, `E44_BDS`, `E45_ZERO_ONE`,
`E95_MUTUAL_INFO`, `E96_TRANSFER_ENTROPY`, `E97_DISTANCE_CORR`.

> Bukan dibuang — `PARKED`. Kalau v6 menghasilkan survivor dan anggaran tersisa,
> mereka antre pertama. Kalau v6 nol, menjalankan mereka tidak akan menolong.

**Target terukur divisi S** (supaya gerbang MCS punya arti):

```yaml
divisi_S_target:
  primer: >
    Separasi expectancy bersyarat: apakah membagi sampel dengan fitur ini menghasilkan
    dua sub-sampel yang expectancy baseline-nya BERBEDA SECARA SIGNIFIKAN?
    Metrik: selisih expectancy antar kuantil ekstrem, dengan CI bootstrap.
  sekunder: >
    Prediksi rezim: akurasi keluar-sampel memprediksi label rezim periode berikutnya
    (label rezim dari §05 Bagian D). Metrik: AUC.
  baseline_naif: "rezim persisten — 'besok sama dengan hari ini'"
  aturan: "yang tidak mengalahkan baseline naif -> pakai baseline, catat, jangan dipaksakan"
```

---

## Bagian D — 🔄 Tangga pemangkasan yang SAMPAI di lantainya

Temuan Audit v5 #1: tangga pemangkasan v5 menjanjikan ~200 tapi lantai strukturalnya
219 — **tangga itu tidak bisa mencapai anggarannya sendiri**, dan tidak ada yang menyadari.

v6 memperbaikinya dengan cara paling sederhana: **hitung lantainya, tulis eksplisit,
dan buat aturan untuk kasus di mana lantai pun terlalu besar.**

### D1 — Yang tidak boleh dipangkas dalam kondisi apapun

| formula | varian | alasan |
|---|---:|---|
| `X06_VERTICAL_ONLY_BASELINE` | 1 | baseline pembanding wajib |
| `X33_DRAWDOWN_CONSTRAINED_SIZING` | 3 | bentuk matematis aturan prop firm — tanpa ini MC2 tidak punya arti |
| `M06_LASSO` | 2 | baseline wajib aturan M6 |
| `M07_RIDGE` | 2 | baseline wajib aturan M6 |
| `M11_META_LABELING` | 2 | satu-satunya mekanisme yang TERBUKTI bekerja di v5 |
| `MOM01_INTRADAY_MOMENTUM` | 1 | jangkar keluarga MOM |
| `MRV01_SHORT_HORIZON_REVERSAL` | 1 | jangkar keluarga MRV |
| `MRV02_OU_SSCORE_PANEL` | 1 | jangkar MRV berbasis panel |
| `BRK01_ORB_SESSION` | 1 | jangkar keluarga BRK |
| `MOM08_TSMOM` | 1 | jangkar MOM lintas-horizon |
| `MOM09_XS_ZSCORE_PANEL` | 1 | jangkar momentum lintas-seksi |
| `MRV03_LIQUIDITY_PROVISION_REVERSAL` | 1 | jangkar MRV berbasis likuiditas |
| `BRK02_POT_EXCEEDANCE` | 1 | jangkar BRK berbasis EVT |
| `BRK03_VOL_CONTRACTION_EXPANSION` | 1 | jangkar BRK berbasis volatilitas |
| `RTR01_BOUNDED_TILT` | 2 | router — inti multi-strategi |
| `RTR02_EQUAL_WEIGHT` | 1 | null N1, pembanding wajib router |
| `RTR03_MCS_SINGLE` | 1 | null N2, pembanding wajib router |
| **LANTAI** | **23** | |

Estimasi yang tidak boleh dipangkas: `V01_PARKINSON` (labeling & penskalaan barrier),
`V05_CLOSE_TO_CLOSE` (baseline), `Q10_SPREAD_PERCENTILE_GATE` (gerbang biaya),
`Q12_REALIZED_SPREAD_COST` (perhitungan biaya).

### D2 — Urutan pemangkasan

Prinsip: yang dipangkas duluan adalah yang **prioritasnya paling rendah** dan
**biayanya paling mahal**. Ketiga keluarga E (MOM/MRV/BRK) dipangkas **sejajar** —
tidak ada keluarga yang dikorbankan untuk keluarga lain, karena premis multi-strategi
runtuh kalau satu keluarga dihapus.

| langkah | tindakan | potong | sisa |
|---|---|---:|---:|
| — | awal | — | **82** |
| L1 | buang model pohon M01, M02 (2+2 varian v6) | −4 | 78 |
| L2 | X sizing sekunder (X30, X31, X32) → 1 varian | −3 | 75 |
| L3 | X exit sekunder (X04, X10, X12, X20, X22) → 1 varian | −5 | 70 |
| L4 | seluruh E (MOM/MRV/BRK) → **1 varian per formula** (46→24) | −22 | 48 |
| L5 | `M11_META_LABELING` 4 → 2 varian | −2 | 46 |
| L6 | buang X exit sekunder seluruhnya (5 formula) | −5 | 41 |
| L7 | buang X sizing sekunder seluruhnya (3 formula) | −3 | 38 |
| L8 | tiap keluarga E → **hanya formula jangkar** (MOM 11→3, MRV 6→3, BRK 7→3) | −15 | **23** |
| — | **LANTAI** | | **23** |

> Kalau `N_maks` < 23, tangga ini **tidak menolong**. Yang berlaku adalah §D3: BERHENTI.

**Tangga diverifikasi sampai lantainya: 82 −4 −3 −5 −22 −2 −5 −3 −15 = 23. Daftar
terlindungi §D1 juga berjumlah 23. Konsisten.**

### D3 — 🔴 Kalau `N_maks` < LANTAI

```yaml
kalau_N_maks_di_bawah_lantai:
  kondisi: "sd_SR terukur menghasilkan N_maks < 23"
  vonis: BERHENTI
  laporan_wajib: >
    "Pada sd_SR terukur = X, tidak ada registri sekecil apapun yang bisa lolos
    DSR 0.95 dengan Sharpe portofolio yang dicapai IC 0.05. Gerbang DSR dan target
    IC yang realistis tidak bisa dipenuhi bersamaan."
  pilihan_yang_sah:
    a: >
      PERSEMPIT keluarga kandidat sampai sd_SR turun. Sharpe yang berkerumun
      = SR_0 kecil = N_maks besar. Ini pilihan pertama, dan gratis.
    b: >
      NAIKKAN Sharpe portofolio: perbesar K_eff (tambah instrumen berkorelasi rendah)
      atau naikkan BR_eff (horizon dengan keunikan lebih tinggi).
    c: >
      TERIMA bahwa DSR 0.95 tidak bisa dipenuhi, dan LAPORKAN itu sebagai temuan.
      Jangan diam-diam menjalankan registri yang dijamin gagal — itu yang terjadi
      lima kali sebelumnya.
  yang_DILARANG:
    - "menurunkan ambang DSR tanpa OVERRIDE V6 tertulis"
    - "menjalankan registri lebih besar dari N_maks dan berharap"
    - "menghitung DSR dengan N yang lebih kecil dari jumlah trial yang benar-benar dijalankan"
```

---

## Bagian E — Aturan horizon & anggaran

```yaml
aturan_horizon:
  prinsip: "Horizon adalah bagian dari HIPOTESIS. Horizon berbeda = eksperimen berbeda."
  dilarang: "menjalankan registri penuh di 6 horizon sekaligus (81 x 6 = 486 -> dijamin nol)"
  prosedur:
    F2b_pilot:
      formula: 12
      pilihan: [MOM01, MOM04, MOM05, MOM08, MRV01, MRV03, BRK01, BRK03, BRK05, X06, V01, Q08]
      varian_per_formula: 1
      horizon: 6
      total_baris: 72
      ledger: ledger_diagnostik      # 🔄 pilot horizon BUKAN seleksi strategi
      catatan: >
        🔄 Pilot HANYA tier-1. MOM07 (eks E72) dan MRV02 (PCA+AR1 per bar) DIKELUARKAN —
        dua-duanya tier-2. Diganti MOM05_MANN_KENDALL dan MRV03 (tier-1).
        v5 mengklaim pilotnya 'semua tier-1' padahal E72 tier-2 — kesalahan yang sama
        hampir terulang di draf awal v6.
    setelah_pilot: "registri penuh HANYA di 1-2 horizon terpilih"

total_maksimum_baris:
  ledger_diagnostik: "72 pilot + L10/L11/L12e + dedup + kalibrasi biaya"
  ledger_estimasi:   132  # atau 82 kalau V/Q dipangkas ke jendela tengah
  ledger_arah:       "<= min(120, N_maks), lantai 23"
```

---

## Bagian F — Kalau nol lolos

```yaml
kalau_nol_lolos:
  wajib_ditulis_persis: >
    "Nol kandidat lolos. Transmitansi gerbang terukur = X% (uji L11).
     Kalau X >= 50%: ini temuan tentang pasarnya, bukan kegagalan proses.
     Kalau X < 50%: ini kegagalan alat ukur, BUKAN temuan tentang pasar."
  dilarang:
    - melonggarkan ambang
    - menambah kandidat
    - mengganti definisi statistik
    - mencari partisi data yang lebih ramah
  yang_boleh: "lihat protokol_nol_lolos di §07 Bagian E — kerjakan URUT dari langkah 0"
```

---

**Lanjut ke `09_MULTISTRATEGI.md`.**
