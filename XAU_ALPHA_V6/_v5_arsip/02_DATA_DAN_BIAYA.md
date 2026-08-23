# 02 — DATA & MODEL BIAYA (TANPA MT5)

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML disalin **verbatim**. Nol perubahan aturan, ambang, atau rumus.


Biaya adalah **penentu hidup-mati** di scalping, bukan detail administratif. Riset sebelumnya
meremehkan biaya **3x lipat** karena menghitung `kappa` dari batas waktu maksimum, bukan dari
durasi hit barrier yang **nyata**.

Yang mengikat:

- Biaya dinyatakan dalam **bps**, bukan USD. `$0.41 @ 1836 = 2.23 bps` tapi `$0.41 @ 4390 = 0.93 bps` — kandidat yang diuji di rezim harga rendah akan tampak membaik sendiri di rezim harga tinggi tanpa alasan ekonomi.
- Spread **terukur dari tick bid/ask Dukascopy**, bukan dari angka publikasi broker.
- Slippage **tidak bisa diverifikasi** tanpa fill nyata → dimodelkan konservatif, ditandai ESTIMASI, plus **penalti ketidaktahuan 1.5x** di skenario worst.
- **Seluruh gerbang kelayakan dihitung pada skenario `worst`.** Bukan `base`, bukan `best`.
- `cost_verified: false` sepanjang v5. Tiap laporan **wajib** mencantumkan bahwa biaya belum terverifikasi.

> Prinsip mengikat: kalau sebuah data tidak tersedia **live pada detik entry**, DILARANG dipakai di backtest.

## Sumber data & larangan

```yaml
data:
  harga_dan_tick:
    sumber: dukascopy
    catatan: "HANYA harga & tick. DILARANG dipakai untuk biaya apapun."
    format: tick bid/ask + timestamp
    hash_wajib_dicatat: true
  spread_terukur:
    sumber: dukascopy_tick_bid_ask
    catatan: >
      Ini spread NYATA yang terukur, bukan estimasi. Dipakai sebagai DASAR
      model biaya karena log MT5 tidak dipakai.
  dilarang_total:
    - volume MT5            # itu tick count, bukan lot tertransaksi
    - DOM / depth of market # buku sintetis broker
    - order flow / signed volume
    - consolidated tape     # tidak eksis di OTC spot gold
    - data makro sebagai sinyal   # boleh sebagai jadwal blackout saja
  prinsip_mengikat: >
    Kalau sebuah data tidak tersedia LIVE pada detik entry, DILARANG dipakai
    di backtest.
```

## Model biaya

`markup_prop_firm_pct`, `komisi`, `swap` masih `LOOKUP` — **wajib dicari di halaman spesifikasi FTMO/FundedNext di F0**, jangan ditebak.

```yaml
cost_model:
  unit: bps
  price_reference: contemporaneous_bar_close
  catatan_kenapa_bps: >
    Biaya USD tetap terlihat makin murah saat harga naik.
    $0.41 @ 1836 = 2.23 bps; $0.41 @ 4390 = 0.93 bps.
    Kandidat yang diuji di rezim harga rendah akan tampak membaik sendiri di
    rezim harga tinggi tanpa alasan ekonomi. Itu bias murni.

  sumber_biaya:
    metode: TANPA_MT5
    komponen:

      spread:
        sumber_utama: dukascopy_tick_bid_ask       # TERUKUR, bukan estimasi
        cara_hitung: >
          Untuk setiap bar, hitung spread rata-rata dan persentil 50/75/90/99
          dari tick bid-ask di dalam bar itu. Simpan per sesi dan per jam.
          Ini jadi dasar biaya, bukan angka publikasi broker.
        markup_prop_firm_pct: LOOKUP
        catatan_markup: >
          Prop firm menambah markup di atas spread raw. Cari angka resmi di
          halaman spesifikasi FTMO / FundedNext (bagian trading conditions atau
          spread table untuk XAUUSD). Isi angkanya, JANGAN ditebak.
          Kalau tidak ketemu, pakai skenario di bawah dan tandai UNVERIFIED.

      komisi:
        satuan: USD_per_lot_round_trip
        nilai: LOOKUP
        catatan: >
          Cari di halaman spesifikasi akun FTMO / FundedNext untuk XAUUSD.
          Banyak prop firm membundel komisi ke spread untuk logam (komisi = 0),
          tapi WAJIB dicek, jangan diasumsikan.

      swap:
        satuan: point_per_lot_per_malam
        long: LOOKUP
        short: LOOKUP
        triple_swap_day: LOOKUP        # biasanya Rabu untuk logam, WAJIB dicek
        relevansi: >
          Untuk scalping intraday, swap TIDAK berlaku selama posisi ditutup
          sebelum rollover. WAJIB dimodelkan HANYA untuk kandidat berhorizon
          yang bisa menembus rollover. Kandidat yang menembus rollover tanpa
          model swap = DITOLAK.

      slippage:
        status: TIDAK_ADA_SUMBER_PUBLIK
        catatan_jujur: >
          Slippage nyata TIDAK dipublikasikan prop firm manapun dan TIDAK bisa
          di-Google. Angka yang beredar di internet adalah klaim marketing.
          Karena log MT5 tidak dipakai, slippage WAJIB DIMODELKAN secara
          konservatif dari tick nyata, dan hasilnya ditandai sebagai ESTIMASI.
        model:
          formula: "slippage_bps = alpha * spread_bps_saat_eksekusi + beta * sigma_bar_bps"
          alpha_grid: [0.5, 1.0, 1.5]
          beta_grid: [0.0, 0.25, 0.5]
          catatan: >
            Kalibrasi tidak mungkin tanpa fill nyata. Karena itu SEMUA gate
            kelayakan dihitung pada kombinasi TERBURUK dari grid ini.
        penalti_ketidaktahuan:
          faktor: 1.5
          diterapkan_pada: skenario_worst
          alasan: >
            Karena slippage tidak terverifikasi, ditambahkan margin keamanan
            50%. Ini SENGAJA membuat gerbang lebih ketat, bukan lebih longgar.

  skenario:
    best:  {spread_percentile: 50, slippage_alpha: 0.5, slippage_beta: 0.00}
    base:  {spread_percentile: 75, slippage_alpha: 1.0, slippage_beta: 0.25}
    worst: {spread_percentile: 90, slippage_alpha: 1.5, slippage_beta: 0.50, extra_penalty: 1.5}

  gate_dihitung_pada: worst
  cost_verified: false
  catatan_cost_verified: >
    Tetap false sepanjang v5 karena tidak ada fill nyata. Setiap laporan WAJIB
    mencantumkan "BIAYA BELUM TERVERIFIKASI — hasil bisa berubah signifikan
    setelah fill nyata tersedia". Kalau nanti user menyediakan fill nyata,
    SELURUH gerbang kelayakan dihitung ulang.

  kappa:
    definisi: "biaya_round_trip_bps / volatilitas_pada_durasi_holding_NYATA_bps"
    aturan: >
      WAJIB dihitung dari durasi hit barrier yang TERUKUR, bukan dari batas
      waktu maksimum. Kesalahan ini membuat riset sebelumnya meremehkan biaya
      3x lipat (0.025 dilaporkan vs 0.079 sebenarnya).
    forbid_max_hold: true
    laporan_wajib_mencantumkan: [durasi_aktual, batas_maksimum]
```
