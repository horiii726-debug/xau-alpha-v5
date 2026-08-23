# REFERENSI — STATUS VERIFIKASI SITASI

> §D1: **DILARANG mengarang DOI, sitasi, nama jurnal, atau angka hasil.**
> Tidak ketemu = `NEED_LOOKUP` atau `TIDAK_KETEMU`. Satu sitasi palsu membatalkan
> seluruh registry.
>
> §D2: kandidat wajib punya identitas sumber terverifikasi (DOI **atau** SSRN ID
> **atau** NBER WP) sebelum masuk CONFIRM.
>
> **Tanggal verifikasi: 22 Agustus 2026.**

---

## ✅ Terverifikasi — identitas dilihat langsung dari halaman penerbit

| formula | sitasi | identitas terverifikasi |
|---|---|---|
| `MOM08_TSMOM_TIMESERIES` | Moskowitz, Ooi & Pedersen, *Time series momentum*, Journal of Financial Economics, 104(2), 2012 | SSRN `2089463` · ScienceDirect PII `S0304405X11002613` |
| `MOM11_EXTREME_PROXIMITY` | George & Hwang, *The 52-week high and momentum investing*, Journal of Finance, 59(5), 2004 | DOI `10.1111/j.1540-6261.2004.00695.x` |
| `MRV02_OU_SSCORE_PANEL` | Avellaneda & Lee, *Statistical arbitrage in the US equities market*, Quantitative Finance, 10(7), 761–782, 2010 | DOI `10.1080/14697680903124632` |
| `MRV03_LIQUIDITY_PROVISION_REVERSAL` | Nagel, *Evaporating liquidity*, Review of Financial Studies, 25(7), 2005–2039, 2012 | SSRN `1988706` · NBER `w17653` |
| `MRV05_CONTRARIAN_DECOMPOSITION` | Lo & MacKinlay, *When are contrarian profits due to stock market overreaction?*, Review of Financial Studies, 3(2), 175–205, 1990 | SSRN `227214` · NBER `w2977` |
| `BRK01_ORB_SESSION` | Zarattini & Aziz, *Can day trading really be profitable? … opening range breakout (ORB) …*, SSRN, 2023 | SSRN `4416622` |

**5 dari 6 terbit di jurnal peer-reviewed peringkat teratas** (JFE, JF, QF, RFS ×2).

---

## ⚠️ Terverifikasi ada, TAPI bukan peer-reviewed

| formula | sitasi | status | konsekuensi §D2 |
|---|---|---|---|
| `BRK01_ORB_SESSION` | Zarattini & Aziz, SSRN 2023 | **SSRN working paper** | boleh screening, **DILARANG CONFIRM** tanpa sumber peer-reviewed pendukung |
| `BRK07_BOCPD_RUNLENGTH` | Adams & MacKay, *Bayesian online changepoint detection*, arXiv:0710.3742, 2007 | **arXiv preprint** — arXiv ID **BUKAN** identitas yang diterima §D2 (hanya DOI / SSRN / NBER) | `NEED_LOOKUP`, boleh screening, **DILARANG CONFIRM** |

**Untuk `BRK01`:** mekanisme dasarnya (pemusatan aliran order di pembukaan sesi)
punya dukungan peer-reviewed lewat literatur intraday momentum — Gao, Han, Li & Zhou,
*Market intraday momentum*, JFE 2018 (dipakai di `MOM01`). Kalau `BRK01` lolos tahap 2,
sumber peer-reviewed langsung **wajib dicari sebelum F9**.

---

## 🔴 `NEED_LOOKUP` — wajib diverifikasi di F3

Gerbang F3: **≥90% sitasi resolve, NOL sitasi karangan.**

### Formula baru v6

| formula | sitasi | catatan |
|---|---|---|
| `MRV04_MAD_ZSCORE_GATE` | Iglewicz & Hoaglin, *How to detect and handle outliers*, ASQC Basic References in Quality Control vol 16, 1993 | monograf ASQC, bukan artikel jurnal — DOI mungkin tidak ada |
| `MOM09`, `MOM10` | Asness, Moskowitz & Pedersen, *Value and momentum everywhere*, Journal of Finance, 68(3), 2013 | jurnal peringkat teratas, DOI hampir pasti ada — belum saya lihat langsung |
| `BRK02_POT_EXCEEDANCE` | Coles, *An introduction to statistical modeling of extreme values*, Springer, 2001 | buku teks standar EVT |
| `BRK03_VOL_CONTRACTION_EXPANSION` | Bollerslev, *GARCH*, Journal of Econometrics, 1986 | sitasi untuk **fakta** pengelompokan volatilitas, **bukan** untuk strateginya |

### 🔴 Yang TIDAK ADA sumbernya sama sekali

| formula | status | tindakan wajib |
|---|---|---|
| **`BRK04_RANGE_COMPRESSION_BREAK`** | **`NEED_LOOKUP` — saya TIDAK MENEMUKAN sumber peer-reviewed untuk bentuk ini** | Cari di literatur volatility clustering / range-based trading / Taylor effect. **Kalau tidak ketemu sampai F3 → masuk `rejected_log` dengan alasan "tidak ada sumber terverifikasi", BUKAN dijalankan dengan sitasi karangan.** |

> Saya menuliskannya apa adanya alih-alih menempelkan sitasi yang kelihatan masuk akal.
> Itu yang diminta §D1, dan itu satu-satunya cara registry ini tetap bisa dipercaya.

### Formula warisan v5

**Seluruh 129 formula v5 masih `doi: NEED_LOOKUP` — nol yang diverifikasi.**
Diakui sendiri di `meta.revisi.sisa_kelemahan_yang_diakui` v5:

> *"129 sitasi masih ditulis dari ingatan, NOL diverifikasi. Wajib dicek di F3."*

Status itu **tidak berubah** — saya tidak memverifikasi ulang 129 sitasi warisan
dalam sesi ini. Yang saya verifikasi adalah **6 sitasi untuk formula baru v6**.

**Beban kerja F3 yang sebenarnya:**

| kelompok | formula | status |
|---|---:|---|
| warisan v5, aktif di v6 (arah + estimasi) | **95** | `NEED_LOOKUP` — belum ada yang diverifikasi |
| baru v6 | **6** | ✅ **terverifikasi** |
| baru v6 | **5** | `NEED_LOOKUP` |
| baru v6 | **1** | 🔴 tidak ada sumber (`BRK04`) |
| **total registri aktif** | **107** | 42 arah + 65 estimasi |

Gerbang F3 menuntut **≥90% resolve** → dari 107 formula aktif dibutuhkan **≥97 terverifikasi**.
Saat ini **6**.

> **Ini pekerjaan nyata yang belum dimulai, bukan formalitas.** Perkiraan kasar:
> 101 sitasi × ~3 menit pencarian = **5–6 jam kerja**. Sebagian besar akan resolve
> dengan mudah (jurnal peringkat teratas, penulis dan tahun sudah benar), tapi
> **setiap satu wajib benar-benar dibuka**, bukan diasumsikan.
>
> Alternatif yang sah kalau F3 tidak bisa mencapai 90%: turunkan jumlah formula aktif
> sampai yang terverifikasi mencapai 90% dari sisanya. Itu **mengecilkan registri**,
> yang justru menolong DSR (§08 B). Bukan bencana.

---

## Sumber biaya & aturan akun

Diakses 22 Agustus 2026. Detail lengkap di `03_DATA_DAN_BIAYA.md`.

| # | sumber | yang diambil | status |
|---|---|---|---|
| 1 | [FTMO — Trading Objectives](https://ftmo.com/en/trading-objectives/) | target profit, max daily loss, max loss, min hari, 1-step vs 2-step | ✅ resmi |
| 2 | [cTrader — FTMO trading conditions](https://ctrader.com/prop-firms/ftmo) | komisi per kelas aset (metals 0.0014%), leverage | ✅ resmi (platform) |
| 3 | [FundedNext — CFDs Trading Objectives](https://fundednext.com/general-rules/cfds/trading-objectives) | aturan per model Stellar | ✅ resmi |
| 4 | [FundedNext Help — Commission charges](https://help.fundednext.com/en/articles/10701368-what-are-the-commission-charges-for-stellar-challenges-and-fundednext-accounts) | komisi metals 0.0016% + contoh XAUUSD terverifikasi | ✅ resmi |
| 5 | [FTMO — What is a swap](https://ftmo.com/en/blog/what-is-a-swap-and-for-whom-is-it-important/) | triple swap Rabu→Kamis (forex) | ✅ resmi (blog) |
| 6 | [The Payout Report — FTMO Feb 2026](https://thepayoutreport.com/ftmo-february-2026-updates/) | perubahan leverage gold | ⚠️ sekunder |
| 7 | [GoldSniper — FTMO gold](https://www.goldsniper.io/brokers/ftmo-gold-trading) | kisaran spread XAUUSD $0.15–0.30 | ⚠️ sekunder |
| 8 | [For Traders — FundedNext rules](https://fortraders.com/blog/fundednext-rules) | drawdown berbasis ekuitas, aturan berita | ⚠️ sekunder |

### Yang masih `TIDAK_KETEMU`

| item | konsekuensi |
|---|---|
| markup spread prop firm di atas raw | spread dimodelkan dari tick + skenario, ditandai `UNVERIFIED` |
| swap XAUUSD long/short (poin/lot/malam) | **kandidat yang menembus rollover DITOLAK** sampai angkanya ada |
| triple swap day untuk **metals** | forex terkonfirmasi Rabu→Kamis; metals belum |
| komisi per-sisi vs round-trip | diasumsikan **per sisi** (konservatif), ditandai `KOMISI_SIDE_UNCONFIRMED` |
| slippage nyata | `TIDAK_ADA_SUMBER_PUBLIK` — dimodelkan + penalti 1.5× |

**Semua ini dicari langsung di area klien / support prop firm sebelum F9.**
`cost_verified` tetap `false` sampai F12 forward test selesai.
