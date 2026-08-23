# DIVISI E2 — MEAN REVERSION / PEMBALIKAN OVEREXTENSION

> Bagian dari **XAU ALPHA RESEARCH v6**. Keluarga `MRV`.
> Formula dari v5 disalin **verbatim**. Formula 🆕 adalah tambahan dengan sitasi terverifikasi.

| | |
|---|---|
| **Keluarga** | `MRV` |
| **Tipe divisi** | `direction` |
| **Ledger** | `ledger_arah.csv` |
| **Formula** | 6 |
| **Varian** | 12 |
| **Fase** | F6 |
| **Gerbang** | corong §07 — tahap 1 (t≥1.5) → tahap 2 (t≥2.0) → CONFIRM (17 centang, t≥3.0) |
| **`prior_regime`** | anti-persisten (VR<1), volatilitas NORMAL/kontraksi, spread pulih cepat |
| **`prior_sign`** | **`−`** — kinerja MRV **turun** saat persistensi naik |

## ⛔ Peringatan yang harus dibaca sebelum apapun di file ini

**Bentuk mean-reversion yang paling umum dipakai orang DILARANG di sistem ini:**

```
z_t = (P_t − MA_n(P)) / sigma_n(P)     →  beli kalau z < −2, jual kalau z > +2
```

Itu **Bollinger Bands ditulis ulang dengan notasi statistik**. Tiga pasal dilanggar sekaligus:

| pasal | bunyinya |
|---|---|
| `anti_rumus_ritel.dilarang_total` | "Bollinger Bands" — terdaftar eksplisit |
| `vwap_dan_kalman.dilarang` | "DILARANG dipakai sebagai anchor mean-reversion" |
| `lessons_carried.9` | "VWAP-band dan Kalman sebagai anchor mean-reversion **sudah diuji dan mati total**" |

Angka dari riset Anda sendiri untuk bentuk ini: **persentil permutasi 2.7%** — bukan
sekadar tidak signifikan, tapi **lebih buruk daripada acak**, dan mati di kelima uji
robustness. Keluarga Kalman: **korelasi 1.000 antar varian**.

**Yang membedakan legal dari tidak bukan namanya — tapi APA yang di-standardisasi:**

| bentuk | yang di-standardisasi | vonis |
|---|---|---|
| Bollinger terselubung | **harga** terhadap rata-rata bergulirnya sendiri | ⛔ dilarang, sudah mati |
| `MRV02` | **residual** setelah faktor panel dibuang | ✅ boleh — Avellaneda & Lee |
| `MRV04` | **nilai sinyal** yang sudah ada, sebagai gerbang kekuatan | ✅ boleh — lapisan normalisasi |

Setiap formula di divisi ini berdiri pada mekanisme **kompensasi penyediaan likuiditas**,
bukan pada "harga jauh dari rata-rata maka balik". Itu bedanya.

## Mekanisme keluarga

> Peserta yang menuntut eksekusi **segera** membayar konsesi harga kepada penyedia
> likuiditas yang bersedia menampung inventori. Anda dibayar sebagai penampung.
> Kompensasinya adalah **biaya modal nyata** — tidak hilang selama modal tidak gratis.

**Lawan transaksi:** peserta yang menuntut likuiditas segera dan membayar premi untuk itu.

**Mati saat:** tren kuat — yang "murah" terus jadi lebih murah.

## Aturan yang mengikat

- **DILARANG memberi peringkat** (§O5). Grep `sort|argmax|idxmax|nlargest|max\(` di `select_champion()` → harus NOL.
- Setiap varian = **1 baris ledger**. Panel 1 hipotesis di 8 instrumen tetap **1 baris**.
- Semua fitur **wajib kausal** (§L1, §L2). Eksekusi paling cepat di pembukaan `t+1` (§L9).
- `MRV02` lintas-seksi → **§L12 berlaku penuh**, termasuk uji kebocoran §L12e.
- `prior_sign = −` **DIPRA-REGISTRASI**. Kalau ternyata MRV justru menang di rezim persisten → `SIGN_FLIP_SUSPECT`, dilarang masuk CONFIRM (§O11).

## Daftar isi

| ID | Varian | n_param | Tier | Asal | Rumus (ringkas) |
|---|---:|---:|---|---|---|
| `MRV01_SHORT_HORIZON_REVERSAL` 🔒 | 2 | 2 | T1 | E03 | `z = (C_t−C_{t−L})/(σ_t√L)` ; `sig = −sign(z)·1(\|z\|>θ)` |
| `MRV02_OU_SSCORE_PANEL` 🔒🆕 | 2 | 3 | T2 | baru | s-score OU pada **residual** setelah faktor panel |
| `MRV03_LIQUIDITY_PROVISION_REVERSAL` 🔒🆕 | 2 | 2 | T1 | baru | pembalikan dikondisikan **keadaan likuiditas** |
| `MRV04_MAD_ZSCORE_GATE` 🆕 | 2 | 2 | T1 | baru | z-score MAD atas **nilai sinyal** — gerbang, bukan arah |
| `MRV05_CONTRARIAN_DECOMPOSITION` 🆕 | 2 | 2 | T2 | baru | pisah autokovarians-sendiri vs silang-serial |
| `MRV06_SIGNED_JUMP_REVERSAL` | 2 | 1 | T1 | E63 | `SJV = RS⁺ − RS⁻` ; cabang **pembalikan** |

🔒 = tidak boleh dipangkas (§08 D1) · 🆕 = baru di v6

---

## Spesifikasi

### `MRV01_SHORT_HORIZON_REVERSAL` 🔒

```yaml
  - id: MRV01_SHORT_HORIZON_REVERSAL
    v5_id: E03_SHORT_HORIZON_REVERSAL
    division: E2
    family: MRV
    prior_sign: "-"
    division_type: direction
    formula: "z = (C_t - C_{t-L}) / (sigma_t*sqrt(L)) ; sig = -sign(z) * 1(|z| > theta)"
    params: {L: [3, 6], theta: [2.0]}      # 🔄 v5 6 varian -> 2
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    tier: tier_1_murah
    catatan_penting: >
      Ini men-standardisasi RETURN terhadap volatilitasnya, BUKAN harga terhadap
      rata-rata bergulirnya. Bedanya bukan kosmetik: tidak ada garis tengah yang
      "seharusnya" dituju harga. Yang diukur adalah apakah gerak terlalu besar
      relatif deraunya sendiri.
    mechanism:
      claim: "Gerak yang terlalu besar relatif volatilitasnya sebagian berbalik karena sebagian gerak itu adalah premi likuiditas bukan informasi"
      counterparty: "Peserta yang menuntut eksekusi segera dan membayar konsesi harga kepada penyedia likuiditas yang bersedia menampung"
      decay: "Kompensasi bagi penampung inventori adalah biaya modal nyata sehingga pembalikan sebagian tidak hilang selama modal tidak gratis"
    provenance:
      citation: "Chordia, Roll & Subrahmanyam, Evidence on the speed of convergence to market efficiency, Journal of Financial Economics, 2005"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### 🆕 `MRV02_OU_SSCORE_PANEL` 🔒

Ini bentuk mean-reversion yang **sah** dan yang memanfaatkan panel 8 instrumen.
Bedanya dengan Bollinger bukan kosmetik: yang di-standardisasi adalah **residual
setelah faktor bersama dibuang**, bukan harga terhadap rata-ratanya sendiri.

```yaml
  - id: MRV02_OU_SSCORE_PANEL
    family: MRV
    prior_sign: "-"
    division_type: direction
    status: BARU_V6
    tier: tier_2_sedang
    formula: >
      LANGKAH 1 — buang faktor bersama panel (semua kausal, jendela berakhir di t):
        Pada jendela latih yang berakhir di bar t, hitung PCA atas matriks return
        panel (K instrumen). Ambil m komponen utama pertama (m = 1 atau 2).
        Regresikan return tiap instrumen k terhadap m faktor itu:
          r_{k,s} = alpha_k + SUM_j beta_{kj} * F_{j,s} + eps_{k,s}
        Koefisien beta di-fit HANYA pada jendela latih (§L3).

      LANGKAH 2 — residual kumulatif jadi proses OU:
        X_{k,s} = SUM_{u<=s} eps_{k,u}         (residual kumulatif)
        Fit AR(1) pada X:  X_{k,s+1} = a + b*X_{k,s} + zeta
        Parameter OU:  kappa = -ln(b) * (bar per tahun)
                       m_eq  = a / (1 - b)
                       sigma_eq = sd(zeta) / sqrt(1 - b^2)

      LANGKAH 3 — s-score:
        s_{k,t} = (X_{k,t} - m_eq) / sigma_eq

      ENTRY:  long  kalau s <= -s_masuk
              short kalau s >= +s_masuk
      EXIT:   kalau |s| <= s_keluar  ATAU vertical barrier horizon tercapai

      SYARAT KELAYAKAN (wajib, bukan opsional):
        - b harus di dalam (0, 1). Kalau b >= 1 -> tidak mean-reverting, SKIP bar itu.
        - Waktu paruh = ln(2)/kappa HARUS <= max_hold_bars horizon. Kalau lebih
          lama daripada horizon, mean reversion-nya tidak akan sempat terjadi
          sebelum vertical barrier -> SKIP. Ini gerbang yang paling sering dilupakan
          orang dan penyebab utama strategi stat-arb gagal di horizon pendek.
    params: {n_faktor: [1, 2], s_masuk: [1.5], s_keluar: [0.5], fit_window: [288]}
    variants: 2
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Setelah komponen yang bergerak bersama seluruh panel dibuang, sisa pergerakan satu instrumen adalah tekanan sementara dari arus yang tidak berhubungan informasi sehingga cenderung kembali ke keseimbangannya"
      counterparty: "Peserta yang harus melikuidasi atau membangun posisi besar di satu instrumen dalam waktu terbatas dan menggeser harga relatif terhadap kelompoknya tanpa alasan fundamental"
      decay: "Kecepatan kembalinya ditentukan modal arbitrase yang tersedia, yang menyusut justru saat guncangan besar, sehingga efeknya tidak bisa dihabiskan seluruhnya"
    provenance:
      citation: "Avellaneda & Lee, Statistical arbitrage in the US equities market, Quantitative Finance, 10(7), 761-782, 2010"
      doi: "10.1080/14697680903124632"
      verified: true
      peer_reviewed: true
    catatan_kausalitas: >
      §L12 berlaku PENUH. PCA di-fit hanya pada fold latih (§L3, §L4).
      Instrumen yang barnya belum tutup pada t dikeluarkan, BUKAN forward-fill.
      Minimum 4 instrumen tersedia, kalau kurang -> bar dilewati.
      Uji kebocoran §L12e WAJIB dijalankan khusus untuk formula ini.
    catatan_anti_bollinger: >
      Pertanyaan yang harus bisa dijawab: "apa yang membuat ini bukan Bollinger?"
      Jawaban: Bollinger membandingkan harga dengan rata-rata harga ITU SENDIRI —
      tidak ada teori kenapa harga harus kembali ke rata-ratanya sendiri.
      Di sini harga dibandingkan dengan apa yang DIPREDIKSI faktor panel, dan
      residualnya punya model dinamika eksplisit (OU) dengan syarat kelayakan yang
      bisa gagal. Kalau residualnya ternyata tidak mean-reverting (b >= 1), formula
      ini MENOLAK memberi sinyal. Bollinger tidak pernah menolak apapun.
```

### 🆕 `MRV03_LIQUIDITY_PROVISION_REVERSAL` 🔒

```yaml
  - id: MRV03_LIQUIDITY_PROVISION_REVERSAL
    family: MRV
    prior_sign: "-"
    division_type: direction
    status: BARU_V6
    tier: tier_1_murah
    formula: >
      Pembalikan yang DIKONDISIKAN pada keadaan likuiditas, bukan pembalikan tanpa syarat:
        rev_t   = -sign( r_{t-L:t} )                       (arah pembalikan mentah)
        stress_t = keadaan likuiditas dari divisi Q (juara MCS F4):
                     stress_t = 1 kalau spread_t >= kuantil-p jendela referensi
                                 ATAU Q06_SPREAD_VELOCITY > kuantil-p
                                 (likuiditas sedang MENIPIS)
        sig_t = rev_t * 1( stress_t = 1 ) * 1( |z_t| > theta )
        z_t   = (C_t - C_{t-L}) / (sigma_t * sqrt(L))
      Artinya: HANYA ambil pembalikan ketika gerak terjadi bersamaan dengan likuiditas
      yang sedang menipis — yaitu saat gerak itu paling mungkin berupa premi likuiditas
      dan bukan informasi.
      SEMUA kuantil dari jendela yang berakhir di t, di-fit pada fold latih (§L1, §L3).
    params: {L: [3, 6], theta: [1.5], stress_pct: [75]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc, tick_spread]
    mechanism:
      claim: "Imbal hasil strategi pembalikan adalah kompensasi bagi penyedia likuiditas dan naik justru ketika kapasitas penyediaan likuiditas sedang menipis, sehingga menyaring pembalikan berdasarkan keadaan likuiditas memisahkan pembalikan yang dibayar dari pembalikan yang tidak"
      counterparty: "Peserta yang harus keluar posisi saat likuiditas sedang menipis dan membayar konsesi harga jauh lebih besar daripada dalam kondisi normal"
      decay: "Modal penyedia likuiditas justru mundur ketika volatilitas melonjak, sehingga kompensasinya membesar tepat saat pesaing paling sedikit — kondisi yang tidak bisa diarbitrase habis"
    provenance:
      citation: "Nagel, Evaporating liquidity, Review of Financial Studies, 25(7), 2005-2039, 2012"
      ssrn_id: "1988706"
      nber_wp: "w17653"
      verified: true
      peer_reviewed: true
    catatan_penting: >
      Ini formula yang paling langsung memakai aset yang sudah Anda punya tapi belum
      dipakai: spread tick NYATA dari Dukascopy. Catatan sumber v5 sendiri berbunyi
      "spread tick nyata sudah dimiliki tapi selama ini HANYA dipakai sebagai biaya,
      belum pernah diuji sebagai informasi." Ini pengujiannya.
    catatan_biaya: >
      IRONI YANG WAJIB DIUKUR: formula ini masuk justru saat spread LEBAR, yaitu saat
      biaya paling mahal. Gerbang Q10_SPREAD_PERCENTILE_GATE bisa memblokirnya
      sepenuhnya. Interaksi ini WAJIB dilaporkan eksplisit: berapa proporsi sinyal
      yang diblokir gerbang biaya, dan berapa expectancy sisanya. Kalau 90% sinyal
      diblokir, formula ini tidak bisa dijalankan — dan itu temuan, bukan kegagalan.
```

### 🆕 `MRV04_MAD_ZSCORE_GATE`

```yaml
  - id: MRV04_MAD_ZSCORE_GATE
    family: MRV
    prior_sign: "-"
    division_type: direction
    status: BARU_V6      # promosi dari ADENDUM_Z v5 (Z01), status usulan -> aktif
    tier: tier_1_murah
    formula: >
      Modified z-score Iglewicz-Hoaglin atas NILAI SINYAL (bukan atas harga):
        m_t   = median( s_{t-n+1..t} )
        MAD_t = median( |s_i - m_t| ),  i = t-n+1..t
        z_t   = 0.6745 * (s_t - m_t) / MAD_t
      s = keluaran sinyal kandidat divisi E yang SUDAH lolos corong tahap 2, bukan harga.
      Entry hanya diambil kalau |z_t| >= tau. Arah tetap ditentukan sinyal aslinya,
      TIDAK dibalik. Ini GERBANG KEKUATAN SINYAL, bukan sinyal mean-reversion.
      Semua kuantitas dari jendela yang berakhir di bar t (kausal, §L1).
      Konstanta 0.6745 = Phi^-1(0.75), menyetarakan MAD dengan sigma pada normal.
      MAD_t = 0 -> sinyal dilewati (tidak ada trade). JANGAN dibagi epsilon.
    params: {window: [96, 288], tau: [1.5]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    fitur_input: "keluaran sinyal kandidat divisi E yang lolos corong tahap 2"
    mechanism:
      claim: "Median dan MAD tidak terpengaruh satu bar ekstrem sehingga ambang kekuatan sinyal tidak melar tepat setelah bar berita ketika standar deviasi biasa melonjak dan mematikan sinyal justru di saat geraknya paling besar"
      counterparty: "Peserta yang menormalkan sinyalnya dengan mean dan standar deviasi biasa lalu ambangnya bergeser sendiri setiap ada satu outlier dan sistemnya berhenti mengambil trade di kondisi yang justru paling menguntungkan"
      decay: "Ketahanan terhadap outlier adalah sifat matematis estimator bukan pola pasar sehingga tidak bisa diarbitrase habis oleh pelaku lain"
    provenance:
      citation: "Iglewicz & Hoaglin, How to detect and handle outliers, ASQC Basic References in Quality Control vol 16, 1993"
      doi: NEED_LOOKUP
      peer_reviewed: true
      catatan: "Monograf ASQC, bukan artikel jurnal. Kalau DOI tidak resolve -> NEED_LOOKUP, boleh screening, DILARANG masuk CONFIRM (§D2)."
    catatan_klasifikasi: >
      Formula ini ditaruh di keluarga MRV karena mekanismenya menyaring overextension.
      TAPI dia bekerja sebagai LAPISAN di atas sinyal keluarga lain, bukan sebagai
      sinyal arah mandiri. Kalau dia diterapkan pada sinyal MOM, dia diuji sebagai
      varian MOM+gate, dan baris ledger-nya masuk keluarga sinyal dasarnya.
      Ini WAJIB dicatat di kolom notes supaya tidak ada hipotesis dihitung dua kali.
    catatan_dedup: >
      Risiko korelasi terhadap MOM02 (dua-duanya menyaring dengan ambang kekuatan).
      Bedanya: MOM02 menskala RETURN dengan volatilitas; MRV04 menstandardisasi NILAI
      SINYAL dengan median/MAD dan dipakai sebagai gerbang. Kalau korelasi PnL >= 0.90
      terhadap MOM02 -> alias, tidak masuk registry (§dedup). Diputuskan angka.
```

### 🆕 `MRV05_CONTRARIAN_DECOMPOSITION`

Formula ini bukan cuma kandidat — dia **diagnostik**. Dia memberi tahu apakah
keuntungan pembalikan datang dari over-reaksi (yang bisa diperdagangkan di satu
instrumen) atau dari lead-lag antar instrumen (yang butuh panel).

```yaml
  - id: MRV05_CONTRARIAN_DECOMPOSITION
    family: MRV
    prior_sign: "-"
    division_type: direction
    status: BARU_V6
    tier: tier_2_sedang
    formula: >
      Dekomposisi keuntungan strategi kontrarian berbobot lintas instrumen panel:
        Bobot: w_{k,t} = -(1/K) * ( r_{k,t-1} - r_bar_{t-1} )
               r_bar = rata-rata return panel pada bar t-1
        Keuntungan: pi_t = SUM_k w_{k,t} * r_{k,t}

        E[pi] dipecah jadi tiga bagian:
          C  = kontribusi SILANG-SERIAL  (lead-lag antar instrumen)
          O  = kontribusi AUTOKOVARIANS-SENDIRI (over-reaksi tiap instrumen)
          sigma_mu = sebaran mean return antar instrumen (bias, bukan edge)
          E[pi] = C - O - sigma_mu

      Sinyal perdagangan = w_{k,t} itu sendiri, dinormalisasi dan diambang.
      DEKOMPOSISI-nya dilaporkan sebagai DIAGNOSTIK wajib, bukan sebagai gerbang.
      §L12 berlaku penuh (penyelarasan sesi, larangan forward-fill).
    params: {L: [1, 3], theta: [1.0]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Keuntungan strategi kontrarian bisa berasal dari over-reaksi masing-masing instrumen atau dari keterlambatan satu instrumen bereaksi terhadap instrumen lain, dan dekomposisinya memberi tahu mekanisme mana yang sedang bekerja"
      counterparty: "Peserta yang menyimpulkan ada over-reaksi dari keuntungan kontrarian padahal sumbernya keterlambatan lintas instrumen, lalu menerapkan strateginya di satu instrumen tempat mekanismenya tidak ada"
      decay: "Keterlambatan lintas instrumen menyusut seiring integrasi venue, tapi over-reaksi individu bertahan selama ada peserta yang bereaksi berlebihan terhadap kabar"
    provenance:
      citation: "Lo & MacKinlay, When are contrarian profits due to stock market overreaction?, Review of Financial Studies, 3(2), 175-205, 1990"
      ssrn_id: "227214"
      nber_wp: "w2977"
      verified: true
      peer_reviewed: true
    nilai_diagnostik: >
      Ini yang membuat formula ini layak anggaran meski mungkin gagal sebagai kandidat:
        C >> O  -> keuntungan dari LEAD-LAG. Strategi satu-instrumen di XAUUSD
                   TIDAK AKAN bekerja. Panel wajib. Ini menjelaskan kenapa MRV01
                   gagal di v5 (satu instrumen).
        O >> C  -> keuntungan dari OVER-REAKSI. Strategi satu-instrumen bisa bekerja.
        sigma_mu dominan -> yang terukur cuma sebaran drift antar instrumen,
                   BUKAN edge. Ini perangkap yang paling sering menipu orang.
      Ketiga angka WAJIB dilaporkan di F6, terlepas dari lolos atau tidaknya kandidat.
```

### `MRV06_SIGNED_JUMP_REVERSAL`

```yaml
  - id: MRV06_SIGNED_JUMP_REVERSAL
    v5_id: E63_SIGNED_JUMP_VARIATION
    family: MRV
    prior_sign: "-"
    division_type: direction
    tier: tier_1_murah
    formula: >
      SJV = RS_plus - RS_minus
        RS_plus  = SUM_i[ r_i^2 * 1(r_i > 0) ]
        RS_minus = SUM_i[ r_i^2 * 1(r_i < 0) ]
      🔄 CABANG PEMBALIKAN (v6): sig = -sign(SJV) * 1(|SJV| > theta * RV)
      v5 menjalankan formula ini dengan tanda AMBIGU ("sinyal dari tanda dan besar SJV")
      tanpa menetapkan arahnya. v6 menetapkan cabang PEMBALIKAN secara eksplisit dan
      MEMPRA-REGISTRASINYA, karena mekanismenya (tekanan likuidasi satu sisi) memprediksi
      pembalikan, bukan kelanjutan. Cabang kelanjutan TIDAK dijalankan — menjalankan
      dua-duanya berarti dua hipotesis dilaporkan sebagai satu (§O9).
    params: {window: [48, 96], theta: [0.3]}
    variants: 2
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Volatilitas yang terkonsentrasi di satu sisi menandakan tekanan likuidasi searah dan bukan kedatangan informasi, sehingga sebagian gerak itu adalah konsesi harga yang kembali setelah tekanannya selesai"
      counterparty: "Peserta yang wajib melikuidasi posisi rugi dalam jendela waktu terbatas dan menerima harga apapun sampai eksposurnya bersih"
      decay: "Asimetri berasal dari perbedaan urgensi likuidasi posisi rugi versus realisasi posisi untung, perilaku manusia yang bertahan"
    provenance:
      citation: "Patton & Sheppard, Good volatility bad volatility signed jumps and the persistence of volatility, Review of Economics and Statistics, 2015"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

---

## Catatan pemangkasan

Urutan pemangkasan divisi ini (§08 D2):

1. `MRV05` (tier-2, paling mahal) — potong pertama, **tapi dekomposisinya tetap dijalankan sekali sebagai diagnostik** di `ledger_diagnostik`, bukan sebagai kandidat
2. `MRV06`, `MRV04` → 1 varian
3. `MRV04` dibuang (dia lapisan, bukan sinyal mandiri)
4. **Lantai: `MRV01`, `MRV02`, `MRV03` @ 1 varian = 3 varian.** Ketiganya mewakili tiga
   mekanisme berbeda: overextension murni, residual panel, dan kondisi likuiditas.
