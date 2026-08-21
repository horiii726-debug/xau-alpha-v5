# 04 — PARTISI, LABELING & GERBANG STRUKTUR PAYOFF

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML disalin **verbatim**. Nol perubahan aturan, ambang, atau rumus.


**Ini file yang berisi tes pertama, dan tes pertama TIDAK BOLEH DIUBAH URUTANNYA.**

Pertanyaan yang dijawab di sini bukan *"sinyal apa yang bagus?"* tapi
*"apakah distribusi return emas menyediakan asimetri mekanis yang bisa dieksploitasi sama sekali —
dengan entry **ACAK**, tanpa sinyal apapun?"*

Kalau jawabannya tidak, seluruh pencarian sinyal di divisi E dan M adalah pemborosan.
Riset sebelumnya melakukan ini terbalik dan membuang 3 tahun.

## Kenapa arm `demeaned` yang menentukan

Sampel punya drift raksasa. Entry acak di pasar yang naik terus **bukan** entry acak — itu long beta.
Tanpa arm `demeaned`, gerbang bisa lolos karena drift, bukan karena struktur payoff.
Hasil long-only otomatis divonis **GAGAL** dan dicatat sebagai *drift capture*.

## Angka yang sudah terukur sebelumnya (pembanding, bukan target)

Pada barrier `k_sl=1.5 / k_tp=2.5` (RR 1:1.67): breakeven mekanis **37.50%**, hit rate aktual **37.86%**,
coin-flip net **40.49%**. Artinya pasar memberi ~38% pada RR 1.67. Menuntut 60% pada RR 2.0
menuntut IC jauh di atas 0.15 — di luar jangkauan realistis.

## Partisi data

Holdout dikunci `.LOCKED` 0-byte sampai FASE 10. Dibuka **sekali seumur proyek** (§O7).

```yaml
partitions:
  scheme: chronological_three_way
  screen_fraction: 0.20
  confirm_fraction: 0.60
  holdout_fraction: 0.20
  embargo_days_between: 10
  holdout_lock: ".LOCKED 0-byte sampai FASE 10"
```

## Labeling triple-barrier

Estimator volatilitas untuk barrier = `V01_PARKINSON`. **BUKAN ATR** — ATR dilarang total.

```yaml
labeling:
  method: triple_barrier
  vol_estimator_untuk_barrier: V01_PARKINSON     # BUKAN ATR
  sample_weight: lopez_de_prado_uniqueness
  aturan:
    - "Bobot keunikan WAJIB. Label tumpang tindih tidak dihitung sebagai observasi penuh."
    - "Eksekusi paling cepat di pembukaan bar berikutnya (L9)."
    - "Vertical barrier = max_hold_bars sesuai horizon."
```

## Gerbang struktur payoff — TES PERTAMA

⛔ Kalau gerbang ini nol lolos di semua horizon & instrumen → **BERHENTI TOTAL**. DILARANG melonggarkan margin, mengganti arm penentu, atau menghapus syarat sisi short.

```yaml
payoff_gate:
  nama: "GERBANG STRUKTUR PAYOFF — dijalankan PALING AWAL, entry ACAK"
  pertanyaan: >
    Adakah kombinasi (k_sl, k_tp) yang mengalahkan titik impas mekanisnya
    sendiri, dengan entry ACAK, tanpa sinyal apapun?
  k_sl_grid: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
  k_tp_grid: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
  n_random_entries: 20000
  arms:
    raw:          "return apa adanya — angka pelaporan"
    demeaned:     "return dikurangi mean bergulir 60 hari — ARM PENENTU"
    sign_flipped: "seluruh seri dibalik tandanya — uji simetri"
  decisive_arm: demeaned
  kenapa_demeaned: >
    Sampel punya drift raksasa. Entry acak di pasar yang naik terus BUKAN entry
    acak — itu long beta. Tanpa arm ini, gerbang bisa lolos karena drift, bukan
    karena struktur payoff.
  syarat_lolos:
    margin_min_pp: 2.0
    margin_diukur_di_arm: demeaned
    max_raw_vs_demeaned_gap_pp: 1.0
    sign_flip_abs_margin_tolerance_pp: 0.5
    require_positive_net_bps: true
    require_short_side_pass: true
    stability_sub_periods: 3
  long_only_verdict: "GAGAL — dicatat sebagai drift capture, bukan payoff asymmetry"
  kalau_nol_lolos: >
    Nol di SEMUA horizon dan SEMUA instrumen -> BERHENTI TOTAL. Laporkan persis:
    "Dengan entry acak, tidak ada kombinasi SL/TP yang mengalahkan titik
    impasnya sendiri. Distribusi return tidak menyediakan asimetri mekanis yang
    bisa dieksploitasi."
    DILARANG melonggarkan margin, mengganti arm penentu, atau menghapus syarat
    sisi short.
```
