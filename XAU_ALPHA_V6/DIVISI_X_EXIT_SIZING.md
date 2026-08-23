# DIVISI X — EXIT, SL/TP & SIZING

> Bagian dari **XAU ALPHA RESEARCH v6**. Keluarga: **lintas keluarga** (dipakai semua).
>
> ⚠️ **CATATAN PENTING:** file `DIVISI_X_EXIT_SL_TP_SIZING.md` v5 **tidak ikut terkirim**
> dalam paket yang saya terima — dia terdaftar di manifest `CLAUDE.md` v5 (22 formula /
> 114 varian) tapi filenya tidak ada. Spesifikasi rumus lengkap di bawah karena itu
> **belum bisa disalin verbatim**. Yang ada di sini adalah ID, peran, dan aturan v6.
>
> **Sebelum F5: kirimkan file X v5, atau konfirmasi bahwa spesifikasinya perlu
> ditulis ulang dari awal.** Jangan menjalankan F5 dengan rumus yang ditebak.

| | |
|---|---|
| **Tipe divisi** | `direction` |
| **Ledger** | `ledger_arah.csv` |
| **Formula v5** | 22 (114 varian) |
| **Formula v6** | 10 (20 varian) — dipangkas 82% |
| **Fase** | F5 |
| **Gerbang** | corong §07 |

---

## 🔄 Perubahan prioritas dari v5

v5 menempatkan divisi X sebagai **prioritas tertinggi**, dengan alasan: *"belum pernah
diuji sekalipun di riset sebelumnya."* Alasan itu benar. Tapi hasil run v5 dan
analisis §05 Bagian C mengubah gambarannya.

### Kenapa X gugur di v5

X diuji di atas **entry acak** (34 kombinasi, terbaik −1.81 bps). Itu bukan kegagalan
divisi X — itu konsekuensi matematis:

> **Exit tidak bisa menciptakan arah.** Dia hanya membentuk ulang distribusi.
> Di bawah optional stopping, pada martingale, **setiap** aturan berhenti memberi
> `E[PnL] = 0`. Menguji exit di atas entry acak berarti menguji apakah bentuk barrier
> bisa menciptakan edge dari nol — dan teorema mengatakan tidak bisa.

**Nilai divisi X baru muncul kalau digabung dengan sinyal berarah.**

### Prioritas v6 ditentukan hasil F2

```yaml
prioritas_X_v6:
  ditentukan_oleh: "permukaan simpangan Delta dari F2 (§05 C2)"

  kalau_Delta_signifikan_positif:
    arti: "ada ketergantungan jalur yang bisa dieksploitasi lewat bentuk barrier"
    prioritas_X: TINGGI
    aksi: "jalankan X penuh di F5 sebelum F6"

  kalau_Delta_tidak_beda_dari_nol:
    arti: "bentuk exit sendirian tidak menciptakan edge — semua edge dari entry"
    prioritas_X: PENDUKUNG
    aksi: >
      X TIDAK dijalankan sebagai kandidat mandiri di F5. Yang dijalankan hanya
      X06 (baseline) dan X33 (aturan prop firm). Sisanya diuji di F6 sebagai
      KOMBINASI entry x exit, bukan sendirian.
    catatan: "Ini yang PALING MUNGKIN terjadi berdasarkan teori dan hasil v5."

  kalau_Delta_signifikan_negatif:
    arti: "barrier justru merusak"
    aksi: "pakai X06_VERTICAL_ONLY sebagai exit default, catat"
```

---

## Aturan yang mengikat

- **DILARANG memberi peringkat** (§O5). Grep `sort|argmax|idxmax|nlargest|max\(` → NOL.
- Setiap varian = **1 baris ledger**.
- Estimator volatilitas untuk barrier = **`V01_PARKINSON`** (atau juara MCS divisi V dari F4). **BUKAN ATR** — ATR dilarang total (§02).
- **`ATR trailing stop` dan `chandelier exit` DILARANG.** Padanan legal: `X20_SPRT_EXIT`, `X12_CVAR_OPTIMAL_STOP`, `X22_QUICKEST_DETECTION_EXIT`.
- Tie-break SL/TP: kalau keduanya tersentuh di bar yang sama → **SELALU pilih SL** (§05 Bagian B). Bug v5 yang sudah diperbaiki.
- Semua sizing tunduk pada **batas MC2** (§06 D). Sizing yang lolos backtest tapi gagal MC2 = **DITOLAK**.

---

## Daftar isi v6

| ID | Varian | Tier | Status | Peran |
|---|---:|---|---|---|
| `X06_VERTICAL_ONLY_BASELINE` 🔒 | 1 | T1 | wajib | baseline pembanding — exit hanya di vertical barrier |
| `X33_DRAWDOWN_CONSTRAINED_SIZING` 🔒 | 3 | T1 | wajib | **bentuk matematis aturan prop firm** |
| `X04_EMPIRICAL_QUANTILE_BARRIER` | 2 | T2 | aktif | barrier dari kuantil empiris (pengganti Bollinger) |
| `X10_POT_GPD_STOP` | 2 | T2 | aktif | stop dari EVT peaks-over-threshold |
| `X12_CVAR_OPTIMAL_STOP` | 2 | T2 | aktif | stop optimal berbasis CVaR (pengganti ATR trail) |
| `X20_SPRT_EXIT` | 2 | T2 | aktif | sequential probability ratio test untuk exit |
| `X22_QUICKEST_DETECTION_EXIT` | 2 | T2 | aktif | quickest detection (pengganti ATR trail) |
| `X30_VOL_TARGET_SIZING` | 2 | T1 | aktif | sizing menargetkan volatilitas |
| `X31_KELLY_FRACTIONAL` | 2 | T2 | aktif | Kelly fraksional |
| `X32_RISK_PARITY_SIZING` | 2 | T1 | aktif | risk parity lintas keluarga |
| **TOTAL** | **20** | | | |

🔒 = tidak boleh dipangkas (§08 D1)

**Dikeluarkan dari v6** (dari 22 formula v5 → 10): `X01` (jadi F2, bukan kandidat),
`X02`, `X03`, `X05`, `X11`, `X13`, `X14`, `X21`, `X23`, `X24`, `X34`, `X35`.
`X13`, `X14`, `X23`, `X24`, `X34`, `X35` semuanya **tier-3** — dikeluarkan karena
biaya komputasi tidak sebanding dengan prioritas divisi ini setelah revisi di atas.

---

## Dua formula yang tidak boleh hilang

### `X06_VERTICAL_ONLY_BASELINE` 🔒

Exit **hanya** di vertical barrier (batas waktu horizon). Tanpa SL, tanpa TP.

**Kenapa wajib:** ini pembanding yang menjawab pertanyaan *"apakah barrier menambah
nilai sama sekali?"*. Tanpa baseline ini, Anda tidak bisa tahu apakah SL/TP membantu
atau justru merusak. Riset v5 tidak pernah punya angka pembanding yang bersih untuk ini.

### `X33_DRAWDOWN_CONSTRAINED_SIZING` 🔒

**Ini formula paling penting di seluruh divisi X untuk tujuan Anda.** Dia adalah
bentuk matematis dari aturan akun prop firm.

```yaml
  - id: X33_DRAWDOWN_CONSTRAINED_SIZING
    peran: "menerjemahkan aturan prop firm jadi batas ukuran posisi yang mengikat"
    input_wajib_dari_F0:
      max_daily_loss_pct: 3.0      # FundedNext Stellar 1-Step (TERKETAT)
      max_total_drawdown_pct: 6.0
      drawdown_type: statis
    prinsip: >
      Ukuran posisi dibatasi supaya P(breach) dalam horizon yang relevan tetap di
      bawah 5% (gerbang MC2), BUKAN supaya return maksimal.
    angka_yang_sudah_dihitung: >
      Simulasi 30.000 jalur, Sharpe 1.15, 250 trade (§06 D):
        risk 0.15% -> P(breach) 0.04%   LOLOS
        risk 0.25% -> P(breach) 3.58%   LOLOS
        risk 0.50% -> P(breach) 45.4%   GAGAL
        risk 1.00% -> P(breach) 98.8%   GAGAL
      Batas praktis: <= 0.25% per trade pada aturan terketat.
    konsekuensi_yang_wajib_diterima: >
      Pada risk 0.25% dan Sharpe 1.15, imbal hasil tahunan ~4.5%.
      Aspirasi v5 "240%/tahun pada risiko 1% per trade" TIDAK BISA DIJALANKAN —
      pada risiko 1%, P(breach) = 98.8%.
      Ini bukan pilihan gaya. Ini aritmetika kendala akun.
```

---

## Aturan wajib untuk F5/F6

```yaml
prosedur_X_v6:
  di_F5:
    - "Jalankan X06 dan X33 SELALU — mereka baseline dan kendala, bukan kandidat opsional"
    - "Formula X lain dijalankan HANYA kalau F2 menunjukkan Delta signifikan positif"
    - "Kalau tidak: X lain ditunda ke F6 sebagai kombinasi entry x exit"

  di_F6:
    - >
      Untuk tiap sinyal entry dengan expectancy KOTOR positif, uji ulang dengan
      3 barrier shortlist dari F2 DAN dengan exit dari X yang aktif.
      Ini kombinasi entry x exit — dan ini yang tidak pernah dilakukan v5.
    - >
      Kombinasi entry x exit dihitung sebagai 1 BARIS LEDGER per kombinasi.
      Anggarannya wajib dihitung dan dilaporkan SEBELUM dijalankan.

  peringatan_anggaran: >
    5 entry x 3 barrier x 3 exit = 45 baris — lebih dari separuh anggaran arah.
    WAJIB dibatasi: maksimal 3 entry teratas per keluarga (lolos tahap 2)
    x 2 barrier x 2 exit = 12 kombinasi per keluarga.
    Pemilihan "3 teratas" DILARANG memakai argmax — pakai filter ambang tahap 2,
    dan kalau lebih dari 3 yang lolos, jalankan SEMUA yang lolos atau tidak sama sekali.
```

---

## Catatan pemangkasan

1. `X31`, `X12`, `X20`, `X22` (tier-2) → potong pertama
2. `X04`, `X10` → 1 varian, lalu dibuang
3. `X30`, `X32` → 1 varian, lalu dibuang
4. **Lantai: `X06` (1) + `X33` (3) = 4 varian.** Keduanya tidak boleh hilang —
   satu adalah baseline, satu adalah kendala akun.
