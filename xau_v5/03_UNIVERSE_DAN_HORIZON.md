# 03 — SEMESTA INSTRUMEN & HORIZON

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML disalin **verbatim**. Nol perubahan aturan, ambang, atau rumus.


Ini blok yang memperbaiki masalah terbesar riset sebelumnya: **eff N ~26**. Pada sampel segitu
tidak ada kandidat yang bisa lolos, berapapun jumlahnya. Bukan karena tidak ada edge — karena
tidak cukup data untuk membuktikannya.

**Solusinya bukan menurunkan ambang, tapi membeli sampel:** uji hipotesis yang SAMA di 25 instrumen
sekaligus. Satu hipotesis di 25 instrumen tetap **1 baris ledger**, tapi 25x sampel.

> **Peringatan yang paling sering dilanggar orang:** 8 instrumen tidak berkorelasi lebih berharga
> daripada 25 instrumen yang saling berkorelasi 0.3. Panel dipilih untuk **meminimalkan korelasi PnL**,
> bukan memaksimalkan jumlah instrumen. Lihat `DIVISI_K_KORELASI.md`.

Soal horizon: biaya per trade **tetap**, geraknya yang membesar. Hold 4 jam menelan 2.5% dari gerak,
hold 24 menit menelan 7.9%. Horizon 4 jam **3x lebih mudah** menghasilkan expectancy positif tanpa
menemukan rumus baru satupun. User memilih scalping — itu dihormati, tapi hasil semua horizon
wajib dilaporkan berdampingan.

## Semesta instrumen

```yaml
universe:
  masalah: >
    Menguji satu hipotesis pada satu instrumen di satu horizon menghasilkan
    eff N ~26. Pada sampel itu tidak ada kandidat yang bisa lolos, berapapun
    jumlahnya.
  solusi: >
    Uji hipotesis YANG SAMA di banyak instrumen sekaligus, gabungkan buktinya.
    Satu hipotesis di 25 instrumen = 1 BARIS LEDGER (tetap satu hipotesis),
    tapi 25x sampel. Ambang tidak naik, sampel naik.
    Ini praktik standar riset faktor institusional.

  target:
    instrumen_minimal: 15
    instrumen_target: 25
    eff_n_panel_minimal: 600
    eff_n_panel_target: 800

  inti: [XAUUSD]
  kandidat_panel:
    logam:  [XAGUSD, XPTUSD, XPDUSD]
    fx:     [EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD, EURJPY, GBPJPY]
    indeks: [US30, US100, US500, GER40, UK100, JP225, EU50, AUS200]
    energi: [USOIL, UKOIL, NATGAS]

  langkah_wajib_fase_0: >
    Cek instrumen mana yang BENAR-BENAR tersedia di akun prop firm, beserta
    spread dan komisinya masing-masing. Jangan asumsikan. Instrumen tanpa data
    biaya TIDAK MASUK panel.

  aturan_panel:
    - "Hipotesis diuji pada SEMUA instrumen panel dengan parameter yang SAMA"
    - "DILARANG menyetel parameter per instrumen (itu overfit terselubung)"
    - "Bukti digabung: pooled t-statistic dengan clustering per instrumen"
    - "XAUUSD dilaporkan terpisah sebagai instrumen target"
    - "Kandidat yang HANYA bekerja di XAUUSD -> tandai SINGLE_ASSET_ONLY, curigai overfit"
    - "Syarat lolos: konsisten di >= 60% instrumen panel"
```

## Grid horizon

Horizon adalah bagian dari **hipotesis** (§H20). Registri penuh DILARANG dijalankan di 6 horizon sekaligus — pilih dulu lewat pilot F2b.

```yaml
horizons:
  catatan: >
    Riset sebelumnya mengunci scalping ~24 menit TANPA pernah menguji apakah
    itu pilihan yang benar. v5 menguji beberapa horizon dan membiarkan data
    memilih. User memilih scalping, jadi horizon pendek diprioritaskan, TAPI
    hasil semua horizon WAJIB dilaporkan berdampingan.
  aritmetika_biaya:
    hold_24_menit: {gerak_usd: 8.86,  biaya_usd: 0.70, biaya_pct_dari_gerak: 7.9}
    hold_4_jam:    {gerak_usd: 27.78, biaya_usd: 0.70, biaya_pct_dari_gerak: 2.5}
    arti: >
      Biaya per trade TETAP, geraknya yang membesar. Horizon 4 jam 3x lebih
      mudah menghasilkan expectancy positif tanpa menemukan rumus baru satupun.
  grid:
    - {label: H15,  bar: M5,  max_hold_bars: 3,   menit: 15}
    - {label: H30,  bar: M5,  max_hold_bars: 6,   menit: 30}
    - {label: H60,  bar: M5,  max_hold_bars: 12,  menit: 60}    # prioritas user
    - {label: H120, bar: M15, max_hold_bars: 8,   menit: 120}
    - {label: H240, bar: M15, max_hold_bars: 16,  menit: 240}
    - {label: H1D,  bar: H1,  max_hold_bars: 24,  menit: 1440}  # pembanding
```
