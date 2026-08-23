# 03 — DATA & MODEL BIAYA

> 🔄 File ini berubah paling banyak dari v5. Seluruh `LOOKUP` yang memblokir MC2
> sekarang **terisi dari halaman resmi**, dengan URL dan tanggal akses.
> Yang masih tidak ketemu ditulis `TIDAK_KETEMU` — **tidak ditebak**.
>
> **Tanggal riset: 22 Agustus 2026.**

---

## Bagian A — Sumber data

```yaml
data:
  harga_dan_tick:
    sumber: dukascopy
    catatan: "HANYA harga & tick. DILARANG dipakai untuk biaya apapun."
    format: tick bid/ask + timestamp
    hash_wajib_dicatat: true
    rentang_target: "2003-01 s/d sekarang untuk XAUUSD; per instrumen WAJIB diaudit di F0"

  spread_terukur:
    sumber: dukascopy_tick_bid_ask
    catatan: >
      Spread NYATA terukur, dipakai sebagai DASAR bentuk model biaya (persentil,
      pola per sesi/jam). TAPI level absolutnya WAJIB dikalibrasi terhadap markup
      prop firm — Dukascopy adalah ECN, prop firm menambahkan markup di atasnya.

  biaya_eksekusi:
    sumber: halaman_resmi_FTMO_dan_FundedNext
    catatan: "Lihat Bagian B. Tiap angka wajib punya URL + tanggal akses."

  dilarang_total:
    - volume MT5              # itu tick count, bukan lot tertransaksi
    - DOM / depth of market   # buku sintetis broker
    - order flow / signed volume
    - consolidated tape       # tidak eksis di OTC spot gold
    - data makro sebagai sinyal   # boleh sebagai jadwal blackout saja

  prinsip_mengikat: >
    Kalau sebuah data tidak tersedia LIVE pada detik entry, DILARANG dipakai di backtest.
```

### 🔄 Matriks ketersediaan riwayat — WAJIB DIAUDIT DI F0

Ini menentukan jendela pooling dan karena itu menentukan `t_pooled`. Belum diaudit;
**tabel di bawah adalah dugaan yang WAJIB diganti dengan hasil audit.**

| instrumen | mulai (dugaan) | status |
|---|---|---|
| XAUUSD | 2003 | `WAJIB_AUDIT` |
| XAGUSD | 2003 | `WAJIB_AUDIT` |
| EURUSD | 2003 | `WAJIB_AUDIT` |
| USDJPY | 2003 | `WAJIB_AUDIT` |
| US100 | ~2010 | `WAJIB_AUDIT` |
| US30 | ~2010 | `WAJIB_AUDIT` |
| USOIL | ~2010 | `WAJIB_AUDIT` |
| NATGAS | ~2012 | `WAJIB_AUDIT` |

---

## Bagian B — 🔄 BIAYA NYATA PROP FIRM (sebelumnya seluruhnya `LOOKUP`)

### B1 — Komisi

| firm | kelas aset | komisi | dalam bps notional | status |
|---|---|---|---:|---|
| **FTMO** | forex | $5 per lot | — | ✅ terverifikasi |
| **FTMO** | **metals (XAUUSD)** | **0.0014% × volume** | **0.140 bps** | ✅ terverifikasi |
| FTMO | indices | tanpa komisi | 0 | ✅ terverifikasi |
| FTMO | energy | 0.001% × volume | 0.100 bps | ✅ terverifikasi |
| **FundedNext** | **metals (XAUUSD)** | **0.0016% × volume** | **0.160 bps** | ✅ terverifikasi |
| FundedNext | crypto | 0.04% × volume | 4.0 bps | ✅ terverifikasi |

**Verifikasi silang** (contoh resmi FundedNext): 1 lot XAUUSD @ $4,466.22

```
1 lot x 100 oz x 4466.22 x 0.000016 = $7.15
Halaman resmi menulis $7.14  ->  COCOK
```

> ⚠️ **AMBIGU — WAJIB DIKONFIRMASI SEBELUM F9:** halaman tidak menyatakan apakah
> komisi dikenakan **per sisi** atau **round-trip**. Sampai dikonfirmasi, model biaya
> memakai asumsi **per sisi** (lebih konservatif): `komisi_RT = 2 × 0.16 = 0.32 bps`.
> Tandai `KOMISI_SIDE_UNCONFIRMED` di setiap laporan.
>
> Struktur komisi FundedNext berlaku efektif **12/01/2026** untuk semua model.

### B2 — Spread

| sumber | angka | status |
|---|---|---|
| FTMO XAUUSD, jam standar | $0.15 – $0.30 | ⚠️ `SEKUNDER` — bukan halaman resmi |

**Konsekuensi §D5:** angka ini **tidak boleh dipakai di gerbang CONFIRM** tanpa
konfirmasi resmi. Untuk screening dan robustness, dipakai dengan penanda `UNVERIFIED`.

**Yang dipakai sebagai dasar sesungguhnya:** bentuk distribusi spread (persentil per
sesi per jam) **diukur dari tick Dukascopy**, lalu level-nya digeser dengan markup
prop firm. Markup itu sendiri = `TIDAK_KETEMU` (lihat B4).

### B3 — Aturan akun (input MC2 — sebelumnya kosong, MC2 tidak bisa jalan)

| model | profit target | max daily loss | max drawdown | min hari | catatan |
|---|---|---:|---|---:|---|
| **FTMO 2-Step** | 10% / 5% | 5% | 10% **statis** | 4 | — |
| **FTMO 1-Step** | 10% | 3% | 10% **trailing EOD** | — | best day ≤50% |
| **FundedNext Stellar 2-Step** | 8% / 5% | 5% | 10% **statis** | 5 | konsistensi payout |
| **FundedNext Stellar 1-Step** | 10% | 3% | 6% **statis** | 2 | konsistensi payout |
| **FundedNext Stellar Lite** | 8% / 4% | 4% | 8% **statis** | 5 | risiko/trade ≤1% |
| FundedNext Stellar Instant | — | — | 6% **trailing** | — | — |

Detail FTMO: max daily loss dihitung ulang tiap 00:00 CE(S)T dari **saldo** hari itu,
tapi aturannya berlaku pada **ekuitas** (saldo + P/L posisi terbuka ± swap − komisi).

**Leverage metals FTMO:** 1:30 (2-Step). Sumber lain menyebut naik ke 1:50 per
1 Feb 2026 untuk XAUUSD/XAUEUR/XAUAUD di akun standard. Konflik → tandai
`LEVERAGE_KONFLIK`, WAJIB dikonfirmasi. Tidak mengikat gerbang (sizing dibatasi MC2,
bukan margin), tapi wajib dicatat.

```yaml
mc2_aturan_yang_dipakai:
  # Gate dihitung pada aturan TERKETAT. Lolos di sini = lolos di semua model lain.
  nama: "FundedNext Stellar 1-Step"
  max_daily_loss_pct: 3.0
  max_total_drawdown_pct: 6.0
  drawdown_type: statis
  profit_target_pct: 10.0
  wajib_juga_dilaporkan:
    - "FTMO 2-Step (daily 5%, maxDD 10% statis) — model paling longgar"
```

### B4 — Yang masih TIDAK KETEMU

| item | status | konsekuensi |
|---|---|---|
| markup spread prop firm di atas raw | `TIDAK_KETEMU` | spread dimodelkan dari tick + skenario markup; ditandai `UNVERIFIED` |
| swap XAUUSD long (poin/lot/malam) | `TIDAK_KETEMU` | **kandidat yang menembus rollover DITOLAK** sampai angkanya ada |
| swap XAUUSD short | `TIDAK_KETEMU` | idem |
| triple swap day untuk metals | `TIDAK_KETEMU` | untuk forex terkonfirmasi Rabu→Kamis; metals belum |
| slippage nyata | `TIDAK_ADA_SUMBER_PUBLIK` | dimodelkan konservatif + penalti 1.5× |

> **DILARANG MENEBAK.** Angka-angka ini dicari langsung di area klien / support prop firm
> sebelum F9. Sampai itu terjadi, aturan `swap`: **posisi tidak boleh menembus rollover**
> untuk horizon H15–H240. Untuk H1D, kandidat otomatis `PARKED` sampai swap terisi.

---

## Bagian C — Model biaya

### C1 — Kenapa bps, bukan USD

Biaya USD tetap terlihat makin murah saat harga naik. Ini bukan detail administratif —
**sampel 2003–2026 memuat harga emas dari ~$350 sampai ~$4,400.**

Biaya round-trip yang sama dalam USD, dinyatakan dalam bps:

| harga emas | spread $0.20 | spread $0.60 | komisi RT | total RT (spread $0.20) |
|---:|---:|---:|---:|---:|
| 1200 | 1.667 bps | 5.000 bps | 0.32 | **1.99 bps** |
| 1800 | 1.111 | 3.333 | 0.32 | 1.43 |
| 2400 | 0.833 | 2.500 | 0.32 | 1.15 |
| 3200 | 0.625 | 1.875 | 0.32 | 0.95 |
| 4400 | 0.455 | 1.364 | 0.32 | **0.78 bps** |

**Rentangnya 2.6×.** Kandidat yang diuji di rezim harga rendah akan tampak membaik
sendiri di rezim harga tinggi tanpa alasan ekonomi. Itu bias murni, dan di sampel
23 tahun dia besar.

```yaml
cost_model:
  unit: bps
  price_reference: contemporaneous_bar_close   # WAJIB kontemporer, bukan harga akhir sampel
```

### C2 — 🔄 KOREKSI SATUAN: acuan `beta` di model slippage

**Masalah di v5:**

```
slippage_bps = alpha * spread_bps + beta * sigma_BAR_bps
beta grid: [0.0, 0.25, 0.5]
```

`sigma_BAR` = volatilitas **satu bar penuh** (5–15 menit). Tapi slippage terjadi antara
sinyal dan fill — **hitungan detik**.

| acuan | sigma | slippage pada beta=0.5 |
|---|---:|---:|
| sigma M5 | 5.89 bps | **2.95 bps** |
| sigma M15 | 10.21 bps | **5.10 bps** |
| sigma 1 detik | 0.34 bps | 0.17 bps |
| sigma 3 detik | 0.59 bps | 0.29 bps |
| sigma 10 detik | 1.08 bps | 0.54 bps |

Karena **semua gerbang dihitung pada skenario `worst`** (beta 0.5), satu parameter yang
tidak pernah dikalibrasi menentukan hidup-mati proyek:

| satuan | biaya RT `worst` @gold 3000 | kappa H240 |
|---|---:|---:|
| `sigma_bar` (v5) | **21.31 bps** | **0.522** ← membunuh semua kandidat |
| `sigma_latensi` (v6) | 13.36 bps | 0.327 |

**🔄 Usulan v6 — BUTUH PERSETUJUAN TERTULIS ANDA:**

```yaml
  slippage:
    status: TIDAK_ADA_SUMBER_PUBLIK
    formula: "slippage_bps = alpha * spread_bps + beta * sigma_LATENSI_bps"
    sigma_latensi: "volatilitas terealisasi pada jendela latensi, diukur dari tick Dukascopy"
    latensi_grid_detik: [1, 3, 10]
    alpha_grid: [0.5, 1.0, 1.5]
    beta_grid: [0.0, 0.25, 0.5]
    catatan: >
      Ini KOREKSI SATUAN, bukan pelonggaran gerbang. Slippage secara fisik terjadi
      pada skala latensi, bukan skala bar. TAPI dia mengubah hasil, jadi statusnya
      OVERRIDE V6 dan wajib di-hash sebelum F2.
    kalau_ditolak: >
      Kalau Anda menolak koreksi ini, model v5 dipertahankan APA ADANYA dan
      dicatat bahwa kappa worst 0.522 pada H240 — dan bahwa pada kappa segitu
      nol survivor adalah hasil yang HAMPIR PASTI, terlepas dari kualitas rumus.
```

### C3 — Skenario biaya

```yaml
  skenario:
    best:  {spread_percentile: 50, slippage_alpha: 0.5, slippage_beta: 0.00, penalty: 1.0}
    base:  {spread_percentile: 75, slippage_alpha: 1.0, slippage_beta: 0.25, penalty: 1.0}
    worst: {spread_percentile: 90, slippage_alpha: 1.5, slippage_beta: 0.50, penalty: 1.5}

  gate_dihitung_pada: worst
  penalti_ketidaktahuan:
    faktor: 1.5
    alasan: "slippage tidak terverifikasi -> margin keamanan 50%. SENGAJA membuat gerbang lebih ketat."
```

Contoh terhitung (gold 3000, latensi 3 detik, sigma_latensi 0.59 bps):

| skenario | spread $ | spread bps | slip/sisi | komisi RT | **TOTAL RT** | **kappa H240** |
|---|---:|---:|---:|---:|---:|---:|
| best | 0.20 | 0.667 | 0.333 | 0.32 | **1.65 bps** | 0.041 |
| base | 0.30 | 1.000 | 1.147 | 0.32 | **3.62 bps** | 0.089 |
| worst | 0.60 | 2.000 | 3.295 | 0.32 | **13.36 bps** | **0.327** |

### C4 — Kappa

```yaml
  kappa:
    definisi: "biaya_round_trip_bps / volatilitas_pada_durasi_holding_NYATA_bps"
    aturan: >
      WAJIB dihitung dari durasi hit barrier yang TERUKUR, bukan dari batas waktu
      maksimum. Kesalahan itu membuat riset sebelumnya meremehkan biaya 3x lipat
      (0.025 dilaporkan vs 0.079 sebenarnya).
    forbid_max_hold: true
    laporan_wajib_mencantumkan: [durasi_aktual, batas_maksimum]
```

Kappa per horizon, dihitung pada **skenario yang benar-benar dipakai gerbang** (§C3,
gold 3000). Sigma harian emas ~100 bps — **WAJIB diukur ulang per rezim di F0**:

| horizon | sigma horizon | kappa @best (1.65 bps) | kappa @base (3.62) | **kappa @worst (13.36)** |
|---|---:|---:|---:|---:|
| H15 | 10.2 bps | 0.162 | 0.355 | **1.310** |
| H60 | 20.4 bps | 0.081 | 0.177 | **0.655** |
| H120 | 28.9 bps | 0.057 | 0.125 | **0.462** |
| **H240** | **40.8 bps** | **0.040** | **0.089** | **0.327** |
| H1D | 100.0 bps | 0.017 | 0.036 | **0.134** |

> ⚠️ **Gerbang dihitung pada `worst`.** Kolom terakhir yang mengikat. Pada H15,
> kappa worst **1.31** berarti biaya melebihi seluruh gerak khas horizon itu —
> H15 dan H60 hampir pasti tidak layak pada struktur biaya prop firm.
>
> ⚠️ `sigma horizon` di tabel ini memakai penskalaan √waktu dari batas maksimum.
> Itu **hanya untuk perencanaan**. Angka yang mengikat WAJIB dari **durasi hit
> barrier NYATA** (`forbid_max_hold: true`) — memakai batas maksimum meremehkan
> biaya sekitar 3×, kesalahan yang sudah terjadi di v5.

> v5 mengukur kappa **0.079** di horizon ~24 menit. Naik ke H240 memotong kappa
> sekitar **4×** — tanpa menemukan satu rumus baru pun.

### C5 — `cost_verified`

```yaml
  cost_verified: false
  catatan_wajib_di_setiap_laporan: >
    "BIAYA BELUM TERVERIFIKASI. Komisi metals terverifikasi dari halaman resmi
    (FTMO 0.0014%, FundedNext 0.0016%) tapi ambigu per-sisi vs round-trip.
    Spread dari sumber sekunder. Markup prop firm dan swap TIDAK KETEMU.
    Slippage dimodelkan, tidak diukur. Hasil bisa berubah signifikan setelah
    fill nyata tersedia."
  kapan_jadi_true: "hanya setelah FASE F12 forward test, minimal 200 fill nyata"
```

---

## Sumber

Diakses 22 Agustus 2026:

- [FTMO — Trading Objectives](https://ftmo.com/en/trading-objectives/) — target profit, daily loss, max loss, min hari
- [cTrader — FTMO Prop Challenge, trading conditions](https://ctrader.com/prop-firms/ftmo) — komisi per kelas aset, leverage
- [FTMO — What is a swap](https://ftmo.com/en/blog/what-is-a-swap-and-for-whom-is-it-important/) — triple swap Rabu→Kamis (forex)
- [FundedNext — CFDs Trading Objectives](https://fundednext.com/general-rules/cfds/trading-objectives) — aturan per model Stellar
- [FundedNext Help — Commission charges](https://help.fundednext.com/en/articles/10701368-what-are-the-commission-charges-for-stellar-challenges-and-fundednext-accounts) — komisi metals 0.0016%, contoh XAUUSD
- [The Payout Report — FTMO Feb 2026 updates](https://thepayoutreport.com/ftmo-february-2026-updates/) — perubahan leverage gold *(sekunder)*
- [GoldSniper — FTMO gold trading](https://www.goldsniper.io/brokers/ftmo-gold-trading) — kisaran spread XAUUSD *(sekunder)*
- [For Traders — FundedNext rules](https://fortraders.com/blog/fundednext-rules) — drawdown berbasis ekuitas, aturan berita *(sekunder)*

---

**Lanjut ke `04_UNIVERSE_HORIZON.md`.**
