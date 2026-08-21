# 01 — HUKUM: ANTI-LOOKAHEAD, ANTI-OVERFIT, ANTI-RUMUS RITEL

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML disalin **verbatim**. Nol perubahan aturan, ambang, atau rumus.


**Pelanggaran satu pasal di sini = seluruh hasil batal.** Bukan peringatan gaya bahasa — itu aturannya.

Empat kelompok hukum:

| Kelompok | Isi | Yang dilindungi |
|---|---|---|
| `anti_lookahead` | L1–L10 | Backtest tidak boleh melihat masa depan. L10 adalah **uji kebocoran wajib**: bangun fitur yang sengaja bocor, dia HARUS menang. Kalau tidak, pipeline validasinya yang rusak. |
| `anti_overfit` | O1–O9 | Pre-registration, ledger, DSR, larangan argmax, holdout sekali tembak. |
| `anti_rumus_ritel` | daftar larangan + padanan akademik | RSI, MACD, Bollinger, order block, FVG, volume profile — semua mati. Tiap larangan punya **pengganti berbasis jurnal**. |
| `anti_data_palsu` | D1–D4 | Satu sitasi karangan membatalkan seluruh registry. |

> **Catatan VWAP & Kalman:** boleh sebagai benchmark biaya / estimator keadaan laten.
> **DILARANG** sebagai anchor mean-reversion — bentuk itu sudah diuji dan mati total (persentil permutasi 2.7%, lebih buruk dari acak).

## Seluruh hukum

```yaml
laws:

  anti_lookahead:
    L1: "Fitur pada bar t HANYA memakai data yang tersedia saat bar t tutup."
    L2: >
      Semua filter/estimator WAJIB kausal. DILARANG: centered moving average,
      Savitzky-Golay non-kausal, filtfilt, smoothing dua arah, interpolasi
      yang melihat ke depan.
    L3: "Scaler/PCA/normalisasi di-fit HANYA pada fold latih, lalu diterapkan ke fold uji."
    L4: "Seleksi fitur dilakukan DI DALAM loop cross-validation, bukan sebelum."
    L5: >
      Label triple-barrier memang melihat ke depan (itu target, bukan bocor).
      TAPI sampel yang labelnya tumpang tindih dengan periode uji WAJIB dibuang
      dari latih (purging) + embargo.
    L6: "Dilarang data yang direvisi ke belakang. Satu snapshot, hash dicatat."
    L7: "Biaya & slippage diterapkan saat eksekusi simulasi, bukan dikurangkan di akhir."
    L8: "Posisi tidak menembus gap weekend/libur kecuali dimodelkan eksplisit."
    L9: "Sinyal dari bar t dieksekusi paling cepat di pembukaan bar t+1."
    L10_uji_wajib: >
      Bangun satu fitur yang SENGAJA bocor (memakai return masa depan). Fitur
      itu HARUS menghasilkan IC > 0.5 dan mengalahkan semua null. Kalau tidak,
      pipeline validasinya sendiri yang rusak. Jalankan SEBELUM kandidat pertama.

  anti_overfit:
    O1: "Pre-registration. Semua parameter & ambang ditulis dan di-hash SEBELUM melihat hasil."
    O2: "Setiap konfigurasi yang dijalankan = 1 baris ledger. Sweep 42 = 42 baris."
    O3: "DSR memakai jumlah trial kumulatif sebenarnya dari ledger."
    O4: "Anggaran parameter: n_parameters <= eff_N_panel / 20. Melebihi -> PARKED."
    O5: >
      Kandidat ARAH: select_champion() DILARANG punya sort/argmax/idxmax/
      nlargest/max(). Hanya filter terhadap ambang. Memilih peringkat 1 dari
      daftar yang semuanya tidak berbeda dari nol = memilih keberuntungan.
    O6: "Kandidat ESTIMASI: Model Confidence Set alpha=0.10. Kalau imbang, pilih yang PALING SEDERHANA."
    O7: "HOLDOUT dibuka SEKALI seumur proyek. Sebelum itu .LOCKED 0-byte."
    O8: "Ambang DILARANG diubah setelah melihat hasil. Ubah = OVERRIDE V5 + ulang dari awal."
    O9: "Dilarang melaporkan 'terbaik dari N percobaan' tanpa menyebut N."

  anti_rumus_ritel:
    dilarang_total:
      - ATR sebagai estimator volatilitas
      - EMA/SMA crossover sebagai sinyal
      - RSI
      - Stochastic oscillator
      - MACD
      - Bollinger Bands
      - Ichimoku
      - Fibonacci retracement
      - pivot point
      - supply demand zone
      - order block
      - fair value gap
      - support resistance manual
      - candlestick pattern
      - Elliott wave
      - parabolic SAR
      - chandelier exit
      - ATR trailing stop
      - volume profile / POC        # volume MT5 = tick count, bukan lot
    alasan: >
      Tidak punya sumber peer-reviewed, tidak punya turunan statistik yang bisa
      diuji, dan parameternya tidak punya pembenaran selain kebiasaan.
    padanan_akademik_wajib:
      # DIPERBAIKI r5: 5 dari 6 baris sebelumnya menunjuk ID yang SALAH.
      # Penyebab: blok laws ditulis SEBELUM blok formulas, pakai ID sementara,
      # lalu tidak pernah direkonsiliasi. Semua ID di bawah sudah diverifikasi
      # ada di blok formulas.
      ATR:             [V01_PARKINSON, V02_GARMAN_KLASS, V03_ROGERS_SATCHELL, V04_YANG_ZHANG]
      EMA_crossover:   [E10_VARIANCE_RATIO_LM, E11_VARIANCE_RATIO_WRIGHT, E12_AUTOMATIC_VARIANCE_RATIO]
      Bollinger:       [X04_EMPIRICAL_QUANTILE_BARRIER, X10_POT_GPD_STOP]
      RSI_Stochastic:  [E70_MANN_KENDALL, E71_COX_STUART, E73_RUNS_TEST, E74_BARTELS_RANK_TEST]
      ATR_trail:       [X20_SPRT_EXIT, X12_CVAR_OPTIMAL_STOP, X22_QUICKEST_DETECTION_EXIT]
      pivot_SR:        [E90_CUSUM_CHANGEPOINT, E91_PELT_SEGMENTATION]
      MACD:            [E60_DRIFT_BURST_TSTAT, E01_INTRADAY_MOMENTUM]
      volume_profile:  [DILARANG_TANPA_PENGGANTI]   # volume MT5 = tick count
    vwap_dan_kalman:
      status: BOLEH_DENGAN_SYARAT
      dilarang: >
        DILARANG dipakai sebagai anchor mean-reversion (sinyal "harga jauh dari
        VWAP/Kalman maka balik arah"). Bentuk itu sudah diuji di riset
        sebelumnya dan mati total: VWAP bands persentil permutasi 2.7% (lebih
        buruk dari acak), keluarga Kalman korelasi 1.000 antar varian, semua
        mati di lima uji robustness.
      diizinkan:
        - VWAP sebagai benchmark biaya eksekusi (bukan sinyal arah)
        - Kalman sebagai estimator keadaan laten (drift/volatilitas tersembunyi)

  anti_data_palsu:
    D1: >
      DILARANG mengarang DOI, sitasi, nama jurnal, atau angka hasil.
      Tidak ketemu = tulis NEED_LOOKUP atau TIDAK_KETEMU.
      Satu sitasi palsu membatalkan seluruh registry.
    D2: "Kandidat wajib punya DOI terverifikasi sebelum masuk CONFIRM."
    D3: "Dilarang mengisi mechanism dengan kalimat generik. Kosong lebih baik daripada karangan."
    D4: "Angka yang tidak bisa dihitung ditulis TIDAK_BISA_DIHITUNG + alasan. Dilarang angka perkiraan tanpa label."
```

---

## Konsekuensi praktis untuk yang menulis kode

- Tiap fitur baru: tanya *"apa yang diketahui pasar pada detik bar ini tutup?"* Kalau jawabannya butuh bar berikutnya — buang.
- Tiap `select_champion()` untuk divisi arah: grep sendiri kodenya untuk `sort`, `argmax`, `idxmax`, `nlargest`, `max(`. Ada satu saja → langgar §O5.
- Tiap ambang: sudah ter-hash sebelum melihat hasil? Kalau belum → langgar §O1.
- Tiap DOI: sudah resolve? Kalau belum → tulis `NEED_LOOKUP`, jangan karang.
