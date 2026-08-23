# 05 — PARTISI, LABELING & PENGUKURAN STRUKTUR PAYOFF

> 🔄 Perubahan terbesar: gerbang payoff F2 diubah dari **STOP TOTAL** jadi
> **PENGUKURAN**. Alasannya teorema, bukan preferensi. Baca §C.

---

## Bagian A — Partisi

```yaml
partitions:
  scheme: chronological_three_way
  screen_fraction:  0.25
  confirm_fraction: 0.55
  holdout_fraction: 0.20
  embargo_days_between: 10
  holdout_lock: ".LOCKED 0-byte sampai FASE F10"
```

Dua konfigurasi (§01 B4 — **jangan dicampur**):

| partisi | fraksi | TIER-A (23 thn, K_eff 2.50) | TIER-B (14 thn, K_eff 3.90) |
|---|---:|---|---|
| SCREEN | 25% | 5.75 thn → t_pooled **2.21** | 3.50 thn → t_pooled **2.16** |
| CONFIRM | 55% | 12.65 thn → t_pooled **3.28** | 7.70 thn → t_pooled **3.20** |
| HOLDOUT | 20% | 4.60 thn → t_pooled **1.98** | 2.80 thn → t_pooled **1.93** |

Konfigurasi TARGET yang lolos GM-3 (8 instr, ρ_PnL 0.10, 20 thn): SCREEN t **2.83**,
CONFIRM t **4.20**. Lihat §01 B4b.

**🔄 Kenapa 25/55/20 dan bukan 20/60/20 seperti v5:**

Corong bertingkat (§07) menjalankan **dua** tahap penyaringan di partisi SCREEN
(screening t≥1.5, lalu robustness t≥2.0). Dua tahap butuh daya lebih besar daripada
satu. Menaikkan SCREEN dari 20% ke 25% menaikkan `t_pooled` screen sekitar 12% —
cukup untuk menjalankan tahap-1 pada t≥1.5 dengan transmitansi memadai.

CONFIRM turun dari 60% ke 55% dan tetap memberi `t_pooled` di atas 3.0 di semua
konfigurasi yang layak — ambang 3.0 tidak diubah.

> Fraksi partisi adalah **parameter pre-registrasi (§O1)**. Dikunci di F0, di-hash,
> tidak boleh diubah setelah melihat hasil.

---

## Bagian B — Labeling

```yaml
labeling:
  method: triple_barrier
  vol_estimator_untuk_barrier: V01_PARKINSON     # BUKAN ATR — ATR dilarang total
  sample_weight: lopez_de_prado_uniqueness

  aturan:
    - "Bobot keunikan WAJIB. Label tumpang tindih tidak dihitung sebagai observasi penuh."
    - "Eksekusi paling cepat di pembukaan bar berikutnya (L9)."
    - "Vertical barrier = max_hold_bars sesuai horizon."
    - "Purging + embargo untuk semua label yang tumpang tindih dengan periode uji (L5)."

  # DIPERBAIKI: bug yang ditemukan setelah run v5
  tie_break_sl_tp:
    masalah: >
      Kalau SL dan TP dua-duanya tersentuh di dalam bar M5/M15 yang sama, backtest v5
      memilih yang menguntungkan. Itu optimis palsu (~350 sinyal terkoreksi).
    aturan_v6: >
      Kalau dua-duanya tersentuh dalam bar yang sama -> SELALU pilih SL (pesimistis).
      Kalau tersedia data tick, gunakan urutan tick NYATA. Kalau tidak, SL menang.
      DILARANG memilih berdasarkan mana yang menguntungkan.

  rasio_keunikan:
    status: WAJIB_DIUKUR_PER_INSTRUMEN_PER_HORIZON
    dipakai_untuk: "BR_eff, bobot sampel, effective N di semua p-value"
    assertion: "p-value yang dihitung tanpa bobot keunikan WAJIB ditolak oleh kode (assert)"
```

---

## Bagian C — 🔄 F2: dari GERBANG MATI jadi PENGUKURAN

### C1 — Kenapa F2 versi v5 hampir tautologis gagal

F2 v5 bertanya: dengan entry **acak**, adakah `(k_sl, k_tp)` yang mengalahkan titik
impas mekanisnya sendiri pada arm `demeaned`?

**Teorema optional stopping** menjawabnya sebelum satu baris kode dijalankan:

> Untuk martingale dengan jalur kontinu dan aturan berhenti yang terbatas,
> `E[PnL] = 0` untuk **setiap** aturan berhenti.

Arm `demeaned` dibuat justru untuk membuang drift — artinya membuat deretnya mendekati
martingale **secara konstruksi**. Maka arm penentu itu **harus** memberi nol, kecuali
ada:

1. **ketergantungan jalur** (autokorelasi, klaster volatilitas) yang berinteraksi dengan barrier, atau
2. **efek diskretisasi** (barrier dilewati di antara bar, bukan tepat di barrier)

Dua-duanya kecil. Jadi F2 v5 adalah gerbang yang gagal **karena matematika**, lalu
kegagalannya memicu `STOP TOTAL` yang memblokir seluruh proyek.

**Ini kesalahan yang sama persis dengan `B09_PERFECT_FORESIGHT`** — gerbang yang mustahil
dilewati, membunuh semua kandidat tanpa membedakan mutu, informasinya nol. v5 sudah
melarang B09 dengan alasan itu. F2 lolos dari larangan yang sama hanya karena tidak
ada yang menghitungnya.

### C2 — F2 versi v6: PENGUKURAN

Pertanyaannya diganti dari pertanyaan ya/tidak yang jawabannya sudah diketahui teorema,
menjadi pertanyaan kuantitatif yang jawabannya berguna:

```yaml
payoff_measurement:
  nama: "F2 — PENGUKURAN STRUKTUR PAYOFF (entry ACAK)"

  pertanyaan_v6:
    1: "Berapa titik impas MEKANIS untuk tiap (k_sl, k_tp)?"
    2: "Berapa SIMPANGAN empiris dari prediksi optional-stopping? (= premi ketergantungan jalur)"
    3: "Pada tiap (k_sl,k_tp), berapa besar IC MINIMUM yang dibutuhkan supaya
        expectancy bersih positif setelah biaya worst?"
    4: "Barrier mana yang paling MURAH dalam arti IC-minimum itu?"

  k_sl_grid: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
  k_tp_grid: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
  n_random_entries: 20000

  arms:
    raw:          "return apa adanya — angka pelaporan"
    demeaned:     "return dikurangi mean bergulir 60 hari — ARM PENENTU untuk simpangan"
    sign_flipped: "seluruh seri dibalik tandanya — uji simetri"
    martingale_sintetis: >
      BARU v6. Bootstrap blok dari return demeaned, dirandomisasi supaya
      autokorelasinya HILANG. Ini adalah null teoretis: E[PnL] harus = 0.
      Simpangan = (arm demeaned) - (arm martingale_sintetis).
      Inilah yang MENGUKUR premi ketergantungan jalur, bukan drift.

  keluaran_wajib:
    - "permukaan titik impas mekanis atas (k_sl, k_tp)"
    - "permukaan simpangan Delta(k_sl,k_tp) + CI bootstrap"
    - "permukaan IC_minimum yang dibutuhkan, pada biaya best/base/worst"
    - "SHORTLIST maksimal 3 barrier dengan IC_minimum terendah -> dibawa ke F5/F6"
    - "durasi hit barrier NYATA per kombinasi -> input kappa (§03)"

  # TIDAK ADA STOP TOTAL
  interpretasi:
    delta_signifikan_positif: >
      Ada ketergantungan jalur yang bisa dieksploitasi lewat bentuk barrier.
      Divisi X (exit/sizing) punya ruang nyata. Prioritaskan.
    delta_tidak_beda_dari_nol: >
      TEMUAN, BUKAN KEGAGALAN. Artinya: bentuk exit sendirian tidak bisa
      menciptakan edge — seluruh edge harus datang dari PENGONDISIAN ENTRY.
      Lanjut ke F5/F6 memakai barrier dengan IC_minimum terendah.
      Divisi X diturunkan prioritasnya dari 'tertinggi' ke 'pendukung'.
    delta_signifikan_negatif: >
      Barrier justru merusak. Pertimbangkan exit vertical-only (X06) sebagai baseline.

  long_only_verdict: "GAGAL — dicatat sebagai drift capture, bukan payoff asymmetry"
```

### C3 — Yang TETAP dari v5

Supaya jelas bahwa ini bukan pelonggaran:

| tetap ada | |
|---|---|
| arm `demeaned` tetap arm penentu | ✅ tidak diganti ke `raw` |
| `require_short_side_pass` | ✅ tetap wajib untuk kandidat ARAH di F5/F6 |
| hasil long-only tetap divonis drift capture | ✅ |
| entry acak, 20.000 entry | ✅ |
| stabilitas 3 sub-periode | ✅ |

Yang dihapus **hanya** `STOP TOTAL` — karena gerbang yang gagal karena teorema tidak
boleh memblokir proyek.

### C4 — Angka pembanding yang sudah terukur

Dari riset sebelumnya, pada barrier `k_sl=1.5 / k_tp=2.5` (RR 1:1.67):

```
breakeven mekanis  : 37.50%
hit rate aktual    : 37.86%      <- simpangan +0.36 pp, SEBELUM biaya
coin flip net      : 40.49%
```

Simpangan +0.36 poin persen itu **persis besaran yang F2 v6 dirancang untuk mengukur
dengan CI**. v5 melihat angka itu, membandingkannya dengan `margin_min_pp: 2.0`,
dan menggugurkannya — tanpa pernah bertanya apakah 2.0 pp itu besaran yang mungkin
ada di bawah optional stopping.

> **Margin 2.0 pp pada entry acak menuntut premi ketergantungan jalur yang sangat besar.
> Untuk perbandingan: seluruh biaya round-trip `base` (3.6 bps) setara sekitar 0.09 pp
> pada barrier H240. Menuntut 2.0 pp dari struktur payoff murni adalah menuntut
> 22x biaya transaksi datang gratis dari bentuk barrier saja.**

---

## Bagian D — Definisi rezim (dipakai §09)

Label rezim dibutuhkan router multi-strategi. Semua **kausal** (§L13a), semua dari
divisi yang sudah punya juara MCS.

```yaml
regime_definitions:
  catatan: >
    Label rezim BUKAN kandidat arah dan TIDAK masuk ledger_arah.
    Mereka fitur keadaan, dinilai di ledger_estimasi lewat divisi S.

  sumbu_1_persistensi:
    ukuran: "E10_VARIANCE_RATIO_LM (VR) atau juara MCS divisi S keluarga persistensi"
    trending:  "VR > 1 + ambang"
    ranging:   "VR < 1 - ambang"
    netral:    "selain itu"
    ambang: "dari kuantil bergulir jendela latih, BUKAN nilai tetap"

  sumbu_2_volatilitas:
    ukuran: "juara MCS divisi V (kandidat: V07_BIPOWER, V08_MEDRV — dua-duanya LOLOS di v5)"
    kontraksi: "sigma_t < kuantil-33 jendela referensi"
    ekspansi:  "sigma_t > kuantil-67"
    normal:    "selain itu"

  sumbu_3_biaya:
    ukuran: "Q10_SPREAD_PERCENTILE_GATE + Q08_SPREAD_TO_VOL_RATIO (kappa real-time)"
    murah:  "kappa_t < kuantil-50"
    mahal:  "kappa_t > kuantil-75  -> DILARANG entry apapun (gerbang keras)"

  aturan_kausalitas:
    - "Semua kuantil dari jendela yang berakhir di bar t (L1)"
    - "Kuantil di-fit HANYA di fold latih (L3)"
    - "DILARANG segmentasi retrospektif sebagai fitur live (L13a)"
    - "Umur rezim berjalan boleh dipakai; titik balik yang ditandai belakangan TIDAK"
```

---

**Lanjut ke `06_VALIDASI_STATISTIK.md`.**
