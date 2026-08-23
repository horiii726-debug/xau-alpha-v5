# 04 — SEMESTA INSTRUMEN, RIWAYAT & HORIZON

> 🔄 Ini blok tempat "membeli sampel" benar-benar dikerjakan — hal yang ditulis di v3,
> v4, v5 tapi tidak pernah dilaksanakan.

---

## Bagian A — Kenapa panel, bukan tambah kandidat

```
Satu hipotesis di 1 instrumen  : eff N kecil, K_eff = 1, tidak ada penambalan
Satu hipotesis di K instrumen  : TETAP 1 BARIS LEDGER, tapi
                                 t_pooled  = t_single * sqrt(K_eff)
                                 IR_porto  = IR_single * sqrt(K_eff)
```

**Panel menaikkan daya statistik DAN Sharpe portofolio sekaligus, dengan biaya nol
baris ledger tambahan.** Menambah kandidat melakukan kebalikannya: menaikkan `SR_0`
untuk semua kandidat lain tanpa menambah sampel apapun.

Itu sebabnya v6 **menaikkan panel dari 1 ke 8** dan **menurunkan kandidat dari 507 ke ≤120**.

---

## Bagian B — Panel

```yaml
universe:
  inti: [XAUUSD]                    # instrumen target, dilaporkan terpisah

  panel_v6:
    logam:  [XAUUSD, XAGUSD]
    fx:     [EURUSD, USDJPY]
    indeks: [US100, US30]
    energi: [USOIL, NATGAS]
    K: 8

  alasan_pemilihan: >
    Empat kelas aset yang penggeraknya berbeda: logam mulia (real yield, bank sentral),
    FX mayor (kebijakan moneter), indeks ekuitas (risk sentiment), energi (supply/demand
    fisik). Tujuannya MEMINIMALKAN korelasi PnL strategi, bukan memaksimalkan jumlah.

  target:
    K_eff_minimal: 2.5              # gerbang mati GM-1
    K_eff_target: 3.9
    rho_pnl_maksimal: 0.20
```

### Aturan panel

| # | Aturan |
|---|---|
| 1 | Hipotesis diuji pada SEMUA instrumen panel dengan parameter yang **SAMA**. |
| 2 | **DILARANG menyetel parameter per instrumen** — itu overfit terselubung. |
| 3 | Bukti digabung: **pooled t-statistic dengan clustering per instrumen**. |
| 4 | XAUUSD dilaporkan terpisah sebagai instrumen target. |
| 5 | Instrumen tanpa data biaya **TIDAK BOLEH dieksekusi** — hanya boleh ikut perhitungan lintas-seksi (§L12). |
| 6 | 🔄 Panel bisa **mengecil**, tidak bisa membesar setelah F0 dikunci. Menambah instrumen setelah melihat hasil = mencari partisi yang lebih ramah (§O8). |

### 🔄 Perbaikan filter #17

v5: *"syarat lolos: konsisten di ≥60% instrumen panel"*.

**Kenapa itu salah arah:** menuntut konsistensi lintas instrumen berkorelasi adalah
menguji apakah sinyal Anda memuat **faktor bersama**. Edge yang benar-benar khas emas
(real yield, pembelian bank sentral, permintaan safe-haven) justru dibunuh oleh filter itu.

**v6:**

```yaml
  aturan_konsistensi_panel:
    gerbang_resmi: "pooled t-stat dengan clustering per instrumen >= ambang tahapnya"
    # clustering sudah memperhitungkan korelasi silang. Itu estimator yang benar.

    flag_bukan_gerbang:
      - id: SIGN_CONSISTENCY
        ukuran: "proporsi instrumen dengan tanda expectancy sama"
        ambang_flag: 0.60
        aksi: "di bawah 0.60 -> FLAG, dicatat, WAJIB dijelaskan. BUKAN auto-reject."
      - id: SINGLE_ASSET_ONLY
        definisi: "signifikan HANYA di XAUUSD"
        aksi: >
          Tidak auto-reject. Wajib lolos uji tambahan: signifikan di >=2 dari 3
          sub-periode XAUUSD yang terpisah, DAN punya mekanisme yang menjelaskan
          kenapa khas emas. Kalau dua-duanya lolos -> boleh lanjut dengan penanda.

    panel_insufficient:
      kondisi: "K < 5 instrumen tersedia pada horizon/periode itu"
      aksi: "tandai PANEL_INSUFFICIENT. Jangan dihitung lolos maupun gugur."
```

---

## Bagian C — 🔄 Riwayat: rezim yang hilang

Sampel v5 (2021-08 → 2026-08) hanya memuat **satu rezim: emas naik**. Terlihat jelas
di hasil F2 — sisi long menang ~20 poin persen, sisi short hampir tidak pernah menang.
Arm `demeaned` menangkap itu dengan benar dan menggugurkan semuanya. Sistemnya bekerja.

Tapi artinya: **sisi short tidak pernah diuji dengan adil**, karena sampelnya tidak
memuat pasar turun.

| periode | rezim emas | kenapa penting |
|---|---|---|
| 2003–2011 | naik kuat | pembanding |
| **2011–2015** | **turun keras** | ← sisi short akhirnya diuji adil |
| **2015–2019** | **sideways** | ← rezim tanpa drift |
| 2019–2026 | naik | yang sudah dipunyai |

Ini bukan cuma soal `sqrt(T)`. **Strategi multi-keluarga (§09) tidak bisa divalidasi
sama sekali tanpa rezim yang berbeda-beda** — Anda tidak bisa membuktikan bahwa
mean-reversion menang di pasar ranging kalau sampel Anda tidak punya pasar ranging.

```yaml
riwayat:
  target: "2003-01 s/d sekarang"
  sumber: dukascopy
  wajib_diaudit_di_F0:
    - "tanggal mulai NYATA per instrumen"
    - "gap, duplikat, outlier, jam libur"
    - "perubahan spesifikasi kontrak (mis. ukuran tick) sepanjang riwayat"
    - "hash snapshot dicatat (L6)"
```

### 🔄 Keputusan jendela pooling — dideklarasikan SEBELUM run

Instrumen punya tanggal mulai berbeda. Ada trade-off nyata:

| opsi | K | ρ_PnL | K_eff | T_confirm | t_single | **t_pooled** |
|---|---:|---:|---:|---:|---:|---:|
| **TIER-A** (riwayat panjang, panel kecil) | 4 | 0.20 | 2.50 | 12.65 thn | 2.077 | **3.28** |
| **TIER-B** (panel penuh, riwayat pendek) | 8 | 0.15 | 3.90 | 7.70 thn | 1.620 | **3.20** |

Dua-duanya mendarat di sekitar 3.2 — jadi keputusannya **tidak menentukan hidup-mati**,
tapi tetap wajib dideklarasikan lebih dulu.

```yaml
  aturan_jendela:
    prosedur: >
      1. F0 mengukur K_eff NYATA untuk TIER-A dan TIER-B dari korelasi PnL baseline.
      2. Hitung t_pooled untuk keduanya.
      3. DEKLARASIKAN yang dipakai, di-hash, SEBELUM kandidat pertama.
      4. Yang tidak dipakai boleh dijalankan sebagai UJI ROBUSTNESS SEKUNDER —
         hasilnya dilaporkan tapi TIDAK mengubah vonis.
    dilarang: >
      Menjalankan dua-duanya lalu memilih yang hasilnya lebih bagus. Itu
      dua percobaan dilaporkan sebagai satu (§O9).
```

---

## Bagian D — Horizon

### 🔄 Filter "≥300 trade/tahun" diganti "BR_eff ≥ 100/tahun"

Akar kontradiksi #16-vs-#1 (§00 Temuan 6): jumlah trade bukan besaran yang menentukan
daya statistik. Yang menentukan adalah **jumlah taruhan independen**.

```yaml
  gerbang_frekuensi_v6:
    lama:  "trades_per_tahun >= 300"        # DIHAPUS
    baru:  "BR_eff >= 100 per tahun"        # BR_eff = trades * rasio_keunikan
    alasan: >
      Horizon-netral. H240 dengan 220 trade (BR_eff 136) memberi lebih banyak
      informasi daripada H60 dengan 400 trade (BR_eff 72). Filter lama justru
      mengarahkan sistem ke kolom yang paling miskin informasi, lalu membunuhnya
      lewat biaya.
    catatan: "Ini BUKAN pelonggaran — H60 dengan 400 trade GAGAL filter baru (72 < 100)."
```

### Aritmetika biaya per horizon

| horizon | gerak khas | biaya RT (base) | biaya % dari gerak | BR_eff |
|---|---:|---:|---:|---:|
| H15 | 10.2 bps | 3.6 bps | **35.4%** | 90 |
| H60 | 20.4 bps | 3.6 bps | **17.7%** | 72 |
| H120 | 28.9 bps | 3.6 bps | 12.5% | 105 |
| **H240** | **40.8 bps** | 3.6 bps | **8.9%** | **136** |
| H1D | 100.0 bps | 3.6 bps | 3.6% | 102 |

**Biaya per trade TETAP, geraknya yang membesar.** Horizon panjang lebih mudah
menghasilkan expectancy positif tanpa menemukan rumus baru satupun.

### Grid horizon

```yaml
horizons:
  grid:
    - {label: H15,  bar: M5,  max_hold_bars: 3,   menit: 15,   status: "diuji di pilot F2b"}
    - {label: H30,  bar: M5,  max_hold_bars: 6,   menit: 30,   status: "diuji di pilot F2b"}
    - {label: H60,  bar: M5,  max_hold_bars: 12,  menit: 60,   status: "diuji di pilot F2b"}
    - {label: H120, bar: M15, max_hold_bars: 8,   menit: 120,  status: "diuji di pilot F2b"}
    - {label: H240, bar: M15, max_hold_bars: 16,  menit: 240,  status: "diuji di pilot F2b — kandidat terkuat menurut aritmetika"}
    - {label: H1D,  bar: H1,  max_hold_bars: 24,  menit: 1440, status: "PARKED sampai angka swap ketemu (menembus rollover)"}

  aturan:
    - "Horizon adalah bagian dari HIPOTESIS. Horizon berbeda = eksperimen berbeda."
    - "DILARANG menjalankan registri penuh di 6 horizon sekaligus."
    - "Horizon dipilih di F2b lewat pilot kecil, lalu registri penuh HANYA di 1-2 horizon terpilih."
    - "Hasil SEMUA horizon wajib dilaporkan berdampingan, termasuk yang tidak dipilih."
```

> **Catatan jujur soal preferensi scalping.** Anda memilih scalping. Aritmetikanya
> tidak mendukung: pada H15 biaya menelan **35%** dari gerak khas dan `BR_eff` cuma 90.
> v6 tetap menguji H15–H60 di pilot F2b supaya keputusannya datang dari data, bukan
> dari saya. Tapi kalau pilot memilih H240, **itu jawaban yang harus diterima** —
> memaksa horizon pendek berarti membayar 4× biaya untuk informasi yang lebih sedikit.

---

**Lanjut ke `05_PARTISI_LABELING.md`.**
