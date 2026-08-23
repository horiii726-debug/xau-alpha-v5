# DIVISI E1 — MOMENTUM / KELANJUTAN ARAH

> Bagian dari **XAU ALPHA RESEARCH v6**. Keluarga `MOM`.
> Formula yang dibawa dari v5 disalin **verbatim** — nol perubahan rumus, nol
> perubahan grid parameter. Formula 🆕 adalah tambahan dengan sitasi terverifikasi.

| | |
|---|---|
| **Keluarga** | `MOM` |
| **Tipe divisi** | `direction` |
| **Ledger** | `ledger_arah.csv` |
| **Formula** | 11 |
| **Varian** | 20 |
| **Fase** | F6 |
| **Gerbang** | corong §07 — tahap 1 (t≥1.5) → tahap 2 (t≥2.0) → CONFIRM (17 centang, t≥3.0) |
| **`prior_regime`** | persisten (VR>1, Hurst>0.5), volatilitas EKSPANSI, drift burst aktif |
| **`prior_sign`** | **`+`** — kinerja MOM naik saat persistensi naik |

## Mekanisme keluarga

> Aliran order besar dipecah dan dieksekusi bertahap. Jejaknya tidak bisa dihilangkan
> tanpa membayar dampak harga lebih besar. Anda dibayar karena menyediakan kelanjutan
> harga bagi pihak yang **wajib** menyelesaikan eksekusi dalam jendela waktu tertentu.

**Lawan transaksi:** manajer yang harus menyelesaikan eksekusi besar dalam jendela
waktu tetap dan rela membayar kelanjutan harga demi kepastian selesai.

**Mati saat:** pasar ranging — tiap entry kelanjutan langsung dibalik.

## Aturan yang mengikat

- **DILARANG memberi peringkat.** `select_champion()` tidak boleh punya `sort`/`argmax`/`idxmax`/`nlargest`/`max()` (§O5).
- Setiap varian = **1 baris ledger**. Panel 1 hipotesis di 8 instrumen tetap **1 baris**.
- Semua fitur **wajib kausal** (§L1, §L2). Sinyal bar `t` dieksekusi paling cepat di pembukaan `t+1` (§L9).
- Formula lintas-seksi (MOM09, MOM10) tunduk penuh pada **§L12** — larangan forward-fill, penyelarasan UTC, minimum 4 instrumen per bar, dan uji kebocoran §L12e.
- Scaler/normalisasi di-fit hanya pada fold latih (§L3). Seleksi fitur di dalam loop CV (§L4).
- `prior_sign` **DIPRA-REGISTRASI**. Tanda interaksi terbalik → `SIGN_FLIP_SUSPECT` (§O11).

## Daftar isi

| ID | Varian | n_param | Tier | Asal | Rumus (ringkas) |
|---|---:|---:|---|---|---|
| `MOM01_INTRADAY_MOMENTUM` 🔒 | 2 | 1 | T1 | E01 | `sig = sign((C_t − C_{t−L})/C_{t−L})` |
| `MOM02_VOL_SCALED_MOMENTUM` | 2 | 2 | T1 | E02 | `z = (C_t−C_{t−L})/(σ_t·√L)` ; `sig = sign(z)·1(\|z\|>θ)` |
| `MOM03_SESSION_GAP_CONTINUATION` | 2 | 1 | T1 | E04 | `gap = (O_t−C_{t−1})/C_{t−1}` ; `sig = sign(gap)·1(\|gap\|>θσ)` |
| `MOM04_DRIFT_BURST_TSTAT` | 2 | 2 | T1 | E60 | `T_t = √h_n · μ̂_t / σ̂_t` |
| `MOM05_MANN_KENDALL` | 2 | 1 | T1 | E70 | `S = Σ_{i<j} sign(x_j−x_i)` ; `Z = (S−sign(S))/√Var(S)` |
| `MOM06_QUANTILE_REG_SLOPE` | 2 | 2 | T1 | E80 | `min_b Σ ρ_τ(y_i − b·t_i)` |
| `MOM07_THEIL_SEN_SLOPE` | 1 | 1 | **T2** | E72 | `β = median_{i<j} (x_j−x_i)/(j−i)` — **w ≤ 48** |
| `MOM08_TSMOM_TIMESERIES` 🔒🆕 | 2 | 1 | T1 | baru | `sig = sign(r_{t−k:t}) · (σ_target/σ_t)` |
| `MOM09_XS_ZSCORE_PANEL` 🔒🆕 | 2 | 2 | T1 | baru | z-score **lintas instrumen** pada tiap timestamp |
| `MOM10_XS_DIVERGENCE_XAU` 🆕 | 1 | 2 | T1 | baru | `d_t = z_{XAU,t} − median_k(z_{k,t})` |
| `MOM11_EXTREME_PROXIMITY` 🆕 | 2 | 2 | T1 | baru | `p_t = C_t / max(H_{t−n:t})` — kedekatan ke ekstrem |

🔒 = tidak boleh dipangkas (§08 D1) · 🆕 = baru di v6

---

## Spesifikasi

### `MOM01_INTRADAY_MOMENTUM` 🔒

```yaml
  - id: MOM01_INTRADAY_MOMENTUM
    v5_id: E01_INTRADAY_MOMENTUM
    division: E1
    family: MOM
    prior_sign: "+"
    division_type: direction
    formula: "sig = sign( (C_t - C_{t-L}) / C_{t-L} ) ; L = lookback bar"
    params: {L: [12, 24]}          # 🔄 v5: [6,12,24,48] -> dipangkas ke 2 varian
    variants: 2
    n_parameters: 1
    data_required: [ohlc]
    tier: tier_1_murah
    mechanism:
      claim: "Return interval awal memprediksi arah sisa horizon karena aliran order yang tertunda dieksekusi bertahap"
      counterparty: "Peserta yang harus menyelesaikan eksekusi besar dalam jendela waktu tetap dan rela membayar kelanjutan harga demi kepastian selesai"
      decay: "Pemecahan order adalah keharusan biaya bagi pihak besar, jejaknya tidak bisa dihilangkan tanpa membayar dampak harga lebih besar"
    provenance:
      citation: "Gao, Han, Li & Zhou, Market intraday momentum, Journal of Financial Economics, 2018"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### `MOM02_VOL_SCALED_MOMENTUM`

```yaml
  - id: MOM02_VOL_SCALED_MOMENTUM
    v5_id: E02_VOL_SCALED_MOMENTUM
    family: MOM
    prior_sign: "+"
    formula: "z = (C_t - C_{t-L}) / (sigma_t * sqrt(L)) ; sig = sign(z) * 1(|z| > theta)"
    params: {L: [12, 24], theta: [1.0]}     # 🔄 dipangkas dari 6 varian
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    tier: tier_1_murah
    catatan_sigma: "sigma_t dari juara MCS divisi V (F4), BUKAN ATR. ATR dilarang total."
    mechanism:
      claim: "Momentum yang dinormalisasi volatilitas menahan sinyal saat range melebar sehingga hanya gerak yang besar relatif terhadap deraunya yang dianggap informatif"
      counterparty: "Peserta yang memakai ambang absolut dan sistematis salah kalibrasi ketika rezim volatilitas berubah"
      decay: "Normalisasi menggeser ambang tiap rezim sehingga tidak ada level tetap yang bisa dihafal pasar"
    provenance:
      citation: "Barroso & Santa-Clara, Momentum has its moments, Journal of Financial Economics, 2015"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### `MOM03_SESSION_GAP_CONTINUATION`

```yaml
  - id: MOM03_SESSION_GAP_CONTINUATION
    v5_id: E04_SESSION_GAP_CONTINUATION
    family: MOM
    prior_sign: "+"
    formula: "gap = (O_t - C_{t-1})/C_{t-1} setelah jeda pasar ; sig = sign(gap) * 1(|gap| > theta*sigma)"
    params: {theta: [0.5, 1.0]}
    variants: 2
    n_parameters: 1
    data_required: [ohlc]
    tier: tier_1_murah
    catatan_L8: "Gap weekend WAJIB dimodelkan eksplisit (§L8). Posisi tidak menembus gap kecuali dimodelkan."
    mechanism:
      claim: "Gap harga saat pembukaan kembali berlanjut arahnya karena informasi yang menumpuk selama jeda belum terserap penuh di bar pertama"
      counterparty: "Pembuat pasar yang membuka kuotasi lebar setelah jeda dan tetap salah harga karena tidak punya harga referensi yang likuid"
      decay: "Jeda perdagangan adalah fitur venue yang tidak bisa dihapus sehingga penumpukan informasi selalu terulang"
    provenance:
      citation: "Berkman, Koch, Tuttle & Zhang, Paying attention overnight returns and the hidden cost of buying at the open, Journal of Financial and Quantitative Analysis, 2012"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### `MOM04_DRIFT_BURST_TSTAT`

```yaml
  - id: MOM04_DRIFT_BURST_TSTAT
    v5_id: E60_DRIFT_BURST_TSTAT
    family: MOM
    prior_sign: "+"
    formula: "T_t = sqrt(h_n) * mu_hat_t / sigma_hat_t ; mu_hat = drift kernel-weighted, sigma_hat = vol kernel-weighted"
    params: {h_mean: [6, 12], h_vol: [48]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    tier: tier_1_murah
    mechanism:
      claim: "Rasio drift terhadap volatilitas lokal mendeteksi ledakan drift sesaat yang secara teori adalah satu-satunya bentuk tren yang bisa dibedakan dari derau pada frekuensi tinggi"
      counterparty: "Penyedia likuiditas yang terus mengutip dua sisi saat drift meledak dan menanggung kerugian seleksi merugikan sampai menarik kuotasi"
      decay: "Ledakan drift terjadi saat likuiditas menipis mendadak dan penyedia likuiditas tidak bisa menghindarinya tanpa berhenti mengutip"
    provenance:
      citation: "Christensen, Oomen & Reno, The drift burst hypothesis, Journal of Econometrics, 2022"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### `MOM05_MANN_KENDALL`

```yaml
  - id: MOM05_MANN_KENDALL
    v5_id: E70_MANN_KENDALL
    family: MOM
    prior_sign: "+"
    formula: "S = SUM_{i<j} sign(x_j - x_i) ; Z = (S - sign(S))/sqrt(Var(S))"
    params: {window: [48, 96]}
    variants: 2
    n_parameters: 1
    data_required: [ohlc]
    tier: tier_1_murah
    catatan: "🔄 Dipakai di pilot F2b menggantikan E72 (yang tier-2, bukan tier-1 seperti diklaim v5)."
    mechanism:
      claim: "Uji tren Mann-Kendall memakai tanda selisih semua pasangan sehingga mendeteksi tren monoton tanpa mengasumsikan bentuk distribusi return yang berekor tebal"
      counterparty: "Peserta yang memakai uji berbasis asumsi normal pada return berekor tebal dan menerima kesimpulan yang tidak valid"
      decay: "Uji nonparametrik lebih lemah dayanya sehingga hanya menangkap tren yang cukup kuat"
    provenance:
      citation: "Mann, Nonparametric tests against trend, Econometrica, 1945"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### `MOM06_QUANTILE_REG_SLOPE`

```yaml
  - id: MOM06_QUANTILE_REG_SLOPE
    v5_id: E80_QUANTILE_REGRESSION_SLOPE
    family: MOM
    prior_sign: "+"
    formula: "min_b SUM rho_tau(y_i - b*t_i) ; rho_tau(u) = u*(tau - 1(u<0))"
    params: {tau: [0.50], window: [24, 48]}    # 🔄 v5 6 varian -> 2
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    tier: tier_1_murah
    mechanism:
      claim: "Kemiringan regresi kuantil mengukur arah pada kuantil tertentu bukan rata-ratanya sehingga tidak tertarik oleh ekor yang jarang tapi besar"
      counterparty: "Peserta yang memakai kuadrat terkecil dan estimasi arahnya digeser beberapa bar lompatan yang tidak mewakili kondisi normal"
      decay: "Perbedaan antara median dan rata-rata hanya besar di data miring yang khas emas"
    provenance:
      citation: "Koenker & Bassett, Regression quantiles, Econometrica, 1978"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### `MOM07_THEIL_SEN_SLOPE`

```yaml
  - id: MOM07_THEIL_SEN_SLOPE
    v5_id: E72_THEIL_SEN_SLOPE
    family: MOM
    prior_sign: "+"
    formula: "beta = median over i<j of (x_j - x_i)/(j - i)"
    params: {window: [48]}
    variants: 1
    n_parameters: 1
    data_required: [ohlc]
    tier: tier_2_sedang       # 🔄 DIKOREKSI: v5 menaruhnya di pilot "semua tier-1". SALAH.
    aturan_komputasi: >
      O(w^2) per bar. Pada w=96 itu ~4600 operasi per bar per instrumen.
      WAJIB implementasi bergulir inkremental ATAU batasi w <= 48. v6 memakai w=48.
      DIKELUARKAN dari pilot F2b.
    mechanism:
      claim: "Kemiringan Theil-Sen adalah median dari semua kemiringan pasangan sehingga tahan sampai hampir sepertiga data merupakan pencilan"
      counterparty: "Peserta yang mengukur kemiringan tren dengan kuadrat terkecil dan estimasinya tertarik jauh oleh beberapa bar berita"
      decay: "Ketahanan terhadap pencilan berharga justru di emas yang sering melompat"
    provenance:
      citation: "Sen, Estimates of the regression coefficient based on Kendall tau, Journal of the American Statistical Association, 1968"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### 🆕 `MOM08_TSMOM_TIMESERIES` 🔒

Mengisi lubang nyata: v5 memakai TSMOM sebagai **null** (`B04_TSMOM_12M`) tapi tidak
pernah sebagai **kandidat**. Padahal ini efek momentum yang paling terdokumentasi
lintas kelas aset, termasuk komoditas.

```yaml
  - id: MOM08_TSMOM_TIMESERIES
    family: MOM
    prior_sign: "+"
    division_type: direction
    status: BARU_V6
    formula: >
      Momentum deret waktu berskala volatilitas, diadaptasi ke horizon intraday:
        r_lookback = ln(C_t / C_{t-k})
        sig_arah   = sign(r_lookback)
        ukuran     = sigma_target / sigma_t          (skala volatilitas, dibatasi <= 2x)
        posisi     = sig_arah * ukuran
      sigma_t dari juara MCS divisi V pada jendela yang berakhir di bar t (kausal, L1).
      sigma_target = median sigma_t pada fold LATIH saja (L3).
      k dinyatakan dalam BAR, diskalakan ke horizon yang dipilih di F2b.
      Ukuran posisi akhir TETAP tunduk pada batas MC2 (§06) — skala volatilitas
      TIDAK BOLEH menaikkan risiko per trade melewati batas yang lolos MC2.
    params: {k_mult: [4, 12]}       # k = k_mult x max_hold_bars horizon
    variants: 2
    n_parameters: 1
    data_required: [ohlc]
    tier: tier_1_murah
    mechanism:
      claim: "Return masa lalu pada horizon menengah memprediksi return berikutnya dengan tanda yang sama karena peserta menyerap informasi bertahap dan menyesuaikan eksposur secara berangsur, bukan seketika"
      counterparty: "Institusi yang merebalans eksposur mengikuti mandat dan jendela waktu tertentu, dan menerima harga yang bergerak melawan mereka selama proses penyesuaian berlangsung"
      decay: "Efeknya menyusut saat lebih banyak modal mengejarnya dan menguat kembali setelah periode kerugian besar mengusir modal itu, sehingga berayun tapi tidak hilang"
    provenance:
      citation: "Moskowitz, Ooi & Pedersen, Time series momentum, Journal of Financial Economics, 104(2), 2012"
      ssrn_id: "2089463"
      sciencedirect_pii: "S0304405X11002613"
      verified: true
      peer_reviewed: true
    catatan_dedup: >
      Risiko korelasi terhadap MOM01 (dua-duanya sign of past return). Bedanya:
      MOM01 tanpa skala volatilitas dan lookback pendek; MOM08 dengan skala
      volatilitas dan lookback jauh lebih panjang. Kalau korelasi PnL >= 0.90
      terhadap MOM01 -> alias, jalankan SATU saja (§dedup). Diputuskan angka.
    catatan_null: >
      B04_TSMOM_12M tetap dipakai sebagai NULL. MOM08 sebagai kandidat WAJIB
      mengalahkan B04 — versi intraday harus lebih baik daripada versi 12 bulan,
      kalau tidak, tidak ada alasan menjalankannya intraday.
```

### 🆕 `MOM09_XS_ZSCORE_PANEL` 🔒

Memakai panel 8 instrumen yang **sudah dibangun** untuk keperluan `K_eff` — aset yang
sudah dibayar tapi belum pernah dipakai untuk entry.

```yaml
  - id: MOM09_XS_ZSCORE_PANEL
    family: MOM
    prior_sign: "+"
    division_type: direction
    status: BARU_V6      # promosi dari ADENDUM_Z v5 (Z02), status usulan -> aktif
    formula: >
      Standardisasi LINTAS INSTRUMEN pada tiap timestamp, bukan lintas waktu:
        Pada bar t, untuk K instrumen panel dengan nilai sinyal s_{k,t}:
          mu_t    = median_k( s_{k,t} )
          MAD_t   = median_k( |s_{k,t} - mu_t| )
          z_{k,t} = 0.6745 * (s_{k,t} - mu_t) / MAD_t
        Entry long pada instrumen dengan z >= +tau, short pada z <= -tau.
        s = momentum berskala volatilitas (MOM02) diterapkan SERAGAM ke semua instrumen.
        Konstanta 0.6745 = Phi^-1(0.75), menyetarakan MAD dengan sigma pada normal.
        MAD_t = 0 -> bar dilewati. JANGAN dibagi epsilon.
      KAUSALITAS (§L12 berlaku PENUH):
        - instrumen yang barnya belum tutup pada t WAJIB dikeluarkan, BUKAN forward-fill
        - timestamp diselaraskan ke UTC; hanya penutupan yang benar-benar <= t
        - kalau instrumen tersedia < 4 -> bar dilewati
        - jumlah instrumen yang ikut dicatat per bar
    params: {signal_window: [48, 96], tau: [1.0]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    tier: tier_1_murah
    mechanism:
      claim: "Standardisasi lintas seksi membuang komponen yang bergerak bersama di seluruh panel dan menyisakan komponen khas instrumen, sehingga yang diuji adalah sinyal murni dan bukan beta pasar yang menyamar jadi sinyal"
      counterparty: "Peserta yang menilai tiap instrumen sendiri-sendiri dan mengambil posisi yang sebenarnya cuma taruhan arah dolar atau arah risiko global, lalu menanggung risiko faktor yang tidak pernah dia niatkan"
      decay: "Peringkat lintas seksi berubah tiap bar dan tidak menghasilkan level tetap yang bisa dihafal peserta lain, tetapi keuntungannya menyusut kalau panelnya menyempit"
    provenance:
      citation: "Asness, Moskowitz & Pedersen, Value and momentum everywhere, Journal of Finance, 68(3), 2013"
      doi: NEED_LOOKUP
      peer_reviewed: true
    catatan_biaya: >
      PERINGATAN: entry lintas-seksi berarti trading di instrumen SELAIN XAUUSD.
      Model biaya per instrumen (spread, komisi, swap) WAJIB sudah terisi di F0 untuk
      SETIAP instrumen yang bisa kena entry. Instrumen tanpa data biaya TIDAK BOLEH
      dieksekusi — hanya boleh jadi bagian perhitungan lintas-seksi (§04).
    catatan_uji_wajib: "§L12e — versi yang sengaja memakai bar belum tutup HARUS menang telak."
```

### 🆕 `MOM10_XS_DIVERGENCE_XAU`

```yaml
  - id: MOM10_XS_DIVERGENCE_XAU
    family: MOM
    prior_sign: "+"
    division_type: direction
    status: BARU_V6      # promosi dari ADENDUM_Z v5 (Z03)
    formula: >
      Selisih z-score lintas-seksi XAU terhadap median panel:
        d_t = z_{XAU,t} - median_k( z_{k,t} )   dengan z dari MOM09
        Entry long kalau d_t >= +tau, short kalau d_t <= -tau.
        Arah mengikuti TANDA d_t (kelanjutan kekuatan relatif), TIDAK dibalik.
      Aturan penyelarasan sesi dan larangan forward-fill dari MOM09 berlaku PENUH.
    params: {signal_window: [96], tau: [1.0]}
    variants: 1
    n_parameters: 2
    data_required: [ohlc]
    tier: tier_1_murah
    mechanism:
      claim: "Kekuatan relatif satu aset terhadap kelompoknya bertahan dalam horizon pendek karena aliran realokasi antar aset dieksekusi bertahap dan tidak selesai dalam satu bar"
      counterparty: "Manajer yang harus merealokasi antar kelas aset dalam jendela waktu tertentu dan rela membayar kelanjutan harga demi menyelesaikan perpindahan tepat waktu"
      decay: "Kecepatan realokasi meningkat seiring otomatisasi eksekusi, sehingga jendela tempat efek ini hidup menyempit dari tahun ke tahun"
    provenance:
      citation: "Asness, Moskowitz & Pedersen, Value and momentum everywhere, Journal of Finance, 68(3), 2013"
      doi: NEED_LOOKUP
      peer_reviewed: true
    catatan_dedup: >
      Risiko korelasi TINGGI terhadap MOM09 secara konstruksi (memakai z yang sama).
      WAJIB dicek dedup 0.90 terhadap MOM09 SEBELUM keduanya dijalankan. Kalau lewat
      ambang, jalankan SATU saja. Menjalankan keduanya = menghitung satu hipotesis
      dua kali dan menaikkan SR_0 untuk semua kandidat lain tanpa menambah informasi.
    keunggulan_untuk_tujuan_anda: >
      Ini satu-satunya kandidat yang secara eksplisit menghasilkan sinyal UNTUK XAUUSD
      dari informasi panel. Kalau lolos, dia memberi entry di instrumen target tanpa
      harus mengeksekusi di instrumen lain (yang biayanya belum lengkap).
```

### 🆕 `MOM11_EXTREME_PROXIMITY`

Ini jawaban yang sah untuk kebutuhan trading berbasis **level**. Bentuk ritelnya
(support/resistance manual, pivot) dilarang total. Bentuk ini punya jurnal peringkat
teratas, mekanisme perilaku yang jelas, dan bisa diuji.

```yaml
  - id: MOM11_EXTREME_PROXIMITY
    family: MOM
    prior_sign: "+"
    division_type: direction
    status: BARU_V6
    formula: >
      Kedekatan harga ke ekstrem jendela, diadaptasi dari '52-week high' ke intraday:
        hi_t = max( H_{t-n+1..t} )
        lo_t = min( L_{t-n+1..t} )
        p_hi = C_t / hi_t          (mendekati 1 = dekat puncak jendela)
        p_lo = C_t / lo_t          (mendekati 1 = dekat dasar jendela)
        sig  = +1 jika p_hi >= 1 - eps      (dekat puncak -> kelanjutan NAIK)
               -1 jika p_lo <= 1 + eps      (dekat dasar  -> kelanjutan TURUN)
                0 selain itu
      Semua kuantitas dari jendela yang BERAKHIR di bar t (kausal, §L1).
      eps dinyatakan dalam kelipatan sigma_t (juara MCS divisi V), BUKAN persentase
      tetap — supaya kalibrasinya tidak rusak saat level emas berubah dua kali lipat.
    params: {n: [96, 288], eps_sigma: [0.25]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    tier: tier_1_murah
    mechanism:
      claim: "Harga yang mendekati ekstrem jendelanya menghadapi keengganan peserta untuk merevisi penilaian melewati titik acuan yang menonjol, sehingga penyesuaian harga tertunda dan berlanjut setelah titik itu ditembus"
      counterparty: "Peserta yang memakai ekstrem masa lalu sebagai titik acuan psikologis dan menahan atau membalik posisi di situ, lalu terpaksa menyesuaikan setelah level itu tidak bertahan"
      decay: "Efek penjangkaran berasal dari cara manusia memproses titik acuan yang menonjol, dan bertahan selama ada peserta manusia, tapi melemah di instrumen yang didominasi eksekusi otomatis"
    provenance:
      citation: "George & Hwang, The 52-week high and momentum investing, Journal of Finance, 59(5), 2004"
      doi: "10.1111/j.1540-6261.2004.00695.x"
      verified: true
      peer_reviewed: true
    catatan_anti_ritel: >
      Ini BUKAN support/resistance manual. Bedanya: (a) levelnya ditentukan rumus dari
      jendela tetap, bukan digambar tangan; (b) ambangnya diskala volatilitas, bukan
      angka tetap; (c) punya mekanisme perilaku dari jurnal peringkat teratas;
      (d) bisa diuji, dipermutasi, dan digugurkan seperti kandidat lain.
      Kalau dia gagal gerbang, dia mati — sama seperti yang lain.
```

---

## Catatan pemangkasan

Kalau anggaran memaksa (§08 D2), urutan pemangkasan divisi ini:

1. `MOM07` (tier-2, paling mahal) — potong pertama
2. `MOM06`, `MOM05`, `MOM03` → 1 varian
3. `MOM02`, `MOM04`, `MOM11` → 1 varian
4. `MOM10` dibuang (berkorelasi tinggi dengan `MOM09` secara konstruksi)
5. **Lantai: `MOM01`, `MOM08`, `MOM09` @ 1 varian = 3 varian.** Tidak boleh kurang —
   ketiganya mewakili tiga mekanisme momentum yang berbeda (intraday flow, time-series,
   cross-sectional).
