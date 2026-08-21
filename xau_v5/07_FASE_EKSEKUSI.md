# 07 — URUTAN FASE EKSEKUSI, STOP CONDITION & CARA KERJA

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML disalin **verbatim**. Nol perubahan aturan, ambang, atau rumus.


**Urutan fase tidak boleh diubah.** Ini bukan preferensi gaya kerja — tiap fase adalah gerbang
yang menentukan apakah fase berikutnya masuk akal dijalankan.

```
F0  fondasi + biaya + K_eff    ──► gerbang mati: K_eff kurang → STOP
F1  infrastruktur validasi     ──► gerbang mati: uji kebocoran gagal → STOP
F2  GERBANG PAYOFF (entry acak)──► gerbang mati: nol lolos → STOP TOTAL      ← TES PERTAMA
F2b pilot pemilihan horizon    ──► gerbang mati: t_pooled < 3.0 → STOP
F3  verifikasi DOI & registry
F4  divisi estimasi  V, Q, T
F5  divisi X — EXIT & SIZING   ← prioritas tertinggi
F6  divisi E — screening arah
F7  divisi M — meta-labeling & ML
F8  freeze & pre-register
F9  CONFIRM (maks 8 slot)
F10 GOLDEN HOLDOUT — sekali tembak
F11 paket deployment
```

Perhatikan F2 dan F5: **struktur payoff divalidasi dulu, exit diuji sebelum entry.**
Kebalikan dari cara kebanyakan orang, dan itu memang disengaja.

## Fase

```yaml
phases:

  - id: F0
    nama: "Fondasi, audit data, model biaya"
    tujuan: "Repo bersih, data terverifikasi, biaya terukur dari sumber publik + tick nyata"
    output: [config/v5.yaml, config/v5.yaml.sha256, reports/F0_data_audit.md,
             reports/F0_cost_model.md, reports/F0_universe.md]
    lulus:
      - "Daftar instrumen panel yang BENAR-BENAR tersedia + spread & komisi masing-masing"
      - "Spread terukur dari tick Dukascopy: rata-rata & persentil 50/75/90/99 per sesi & per jam"
      - "Angka komisi, swap, dan aturan drawdown prop firm sudah dicari dan diisi (bukan ditebak)"
      - "Audit data: gap, duplikat, outlier, jam libur, hash data dicatat"
      - "SELURUH pengukuran di power_analysis.e selesai: rasio keunikan, matriks korelasi PnL, K_eff, t_single, K_eff yang dibutuhkan"
      - "screen_max dihitung dari K_eff terukur (trial_budget.screen_max_ditentukan_oleh), BUKAN diasumsikan"
      - "config di-hash dan di-commit SEBELUM apapun dijalankan"
    gagal:
      biaya_tidak_ketemu: "tandai UNVERIFIED, pakai skenario worst + penalti 1.5, JANGAN ditebak"
      K_eff_kurang: >
        Kalau K_eff terukur < K_eff yang dibutuhkan pada IC 0.05 -> BERHENTI
        dan lapor SEBELUM menjalankan kandidat apapun. Jangan lanjut dengan
        berharap. Lihat power_analysis.e.gerbang_F0.

  - id: F1
    nama: "Infrastruktur validasi"
    tujuan: "Alat ukurnya dulu. Jangan mengukur pakai alat yang belum diuji."
    output: [src/stats/nulls.py, src/stats/effective_n.py, src/validation/cpcv.py,
             src/validation/montecarlo.py, src/costs/, tests/]
    lulus:
      - "pytest hijau"
      - "UJI KEBOCORAN (§L10) LOLOS: fitur lookahead sengaja mengalahkan semua null"
      - "Sinyal acak murni TIDAK mengalahkan null manapun"
      - "Matriks korelasi null + jumlah null independen efektif dilaporkan"
    gagal: "Fitur lookahead tidak mengalahkan null -> BUG DI NULL. Perbaiki. Jangan lanjut."

  - id: F2
    nama: "GERBANG STRUKTUR PAYOFF (entry ACAK, belum ada rumus)"
    tujuan: "Apakah distribusi return menyediakan asimetri mekanis?"
    output: [reports/F2_payoff_gate.json, reports/F2_ringkasan.md]
    lulus: "Ada >=1 kombinasi (k_sl,k_tp) lolos semua syarat payoff_gate.syarat_lolos"
    gagal: "STOP TOTAL. Lihat payoff_gate.kalau_nol_lolos. DILARANG melonggarkan apapun."

  - id: F2b
    nama: "PEMILIHAN HORIZON lewat pilot kecil"
    tujuan: >
      Menentukan 1-2 horizon yang dipakai untuk seluruh registri, TANPA
      menjalankan 507 varian di 6 horizon (yang akan menghasilkan 3042 trial
      dan dijamin nol survivor).
    pilot_set:
      jumlah_formula: 12
      pilihan: [E01, E10, E22, E30, E60, E72, E90, X01, X06, X32, V01, Q08]
      alasan_pilihan: "murah secara komputasi, mewakili keluarga berbeda, semua tier-1"
      varian_per_formula: 1
      total_baris_ledger: 72
    yang_diukur_per_horizon:
      - "kappa = biaya_bps / volatilitas_horizon_bps (dari durasi barrier-hit NYATA)"
      - "BR efektif = trades/tahun * rasio keunikan sampel"
      - "K_eff dari matriks korelasi PnL antar instrumen PADA horizon itu"
      - "t_single yang bisa dicapai pada IC 0.03 dan 0.05"
      - "t_pooled = t_single * sqrt(K_eff)"
    lulus: >
      Pilih horizon dengan t_pooled tertinggi pada IC 0.05, DENGAN SYARAT
      t_pooled >= 3.0. Maksimal 2 horizon dipilih.
    gagal: >
      Kalau TIDAK ADA horizon yang mencapai t_pooled >= 3.0 pada IC 0.05 ->
      BERHENTI dan lapor. Artinya data yang tersedia tidak cukup untuk
      membuktikan edge berkekuatan wajar di horizon manapun. Menjalankan 507
      kandidat setelah itu hanya membuang waktu komputasi.
      Opsi yang dilaporkan ke user: tambah instrumen berkorelasi rendah,
      perpanjang riwayat, atau turunkan target trades/tahun.
    catatan: >
      Fase ini BUKAN pencarian sinyal. Ini pengukuran kapasitas statistik data.
      Hasilnya menentukan apakah sisa proyek masuk akal dijalankan.

  - id: F3
    nama: "Kumpulkan & saring kandidat (di atas kertas)"
    tujuan: "Verifikasi seluruh formula di file ini + tambah kandidat baru sampai anggaran"
    output: [registry/candidates_v5.yaml, registry/rejected_log.md, reports/F3_doi_verification.csv]
    lulus:
      - ">=90% DOI terverifikasi resolve"
      - "Nol DOI karangan"
      - "Nol rumus ritel"
      - "Semua yang ditolak tercatat + alasannya"
      - "Jumlah varian <= anggaran dari F0"
    gagal: "DOI tidak ketemu -> NEED_LOOKUP, boleh screening, dilarang CONFIRM. DILARANG mengarang."

  - id: F4
    nama: "Divisi estimasi (V, Q, T)"
    tujuan: "Kunci alat ukur volatilitas, spread, intensitas tick"
    output: [reports/F4_estimation_champions.md]
    lulus: "Juara per horizon lewat Model Confidence Set; imbang -> pilih tersederhana"
    gagal: "Tidak ada yang mengalahkan baseline naif -> pakai baseline, catat"

  - id: F5
    nama: "Divisi X — Exit & Sizing"
    tujuan: "PRIORITAS TERTINGGI. Belum pernah diuji sekalipun di riset sebelumnya."
    output: [reports/F5_exit_sizing.md]
    lulus: "Ada aturan exit/sizing yang mengalahkan baseline pada seluruh gates.direction, termasuk MC2"
    gagal: "Nol lolos -> laporkan, lanjut F6 dengan barrier terbaik dari F2"

  - id: F6
    nama: "Screening arah (divisi E)"
    tujuan: "Saring kandidat entry pada partisi SCREEN, panel penuh"
    output: [reports/F6_screening.md, ledger_trials.csv]
    gagal: "Nol survivor -> jalankan protokol_nol_lolos. JANGAN menambah kandidat."

  - id: F7
    nama: "Meta-labeling & ML (divisi M)"
    tujuan: "Naikkan presisi sinyal yang ada, bukan cari sinyal baru"
    output: [reports/F7_meta_ml.md]
    lulus: "Mengalahkan baseline linear teregularisasi DAN sinyal primer polos"
    gagal: "Tidak mengalahkan baseline -> pakai sinyal primer polos, catat"

  - id: F8
    nama: "Freeze & pre-register"
    tujuan: "Kunci semuanya sebelum CONFIRM"
    output: [PREREGISTRATION.md, config hash di-commit]
    lulus: "Semua parameter, ambang, aturan keputusan terkunci dan ter-hash"
    gagal: "Ada parameter yang masih akan-ditentukan-nanti -> belum boleh lanjut"

  - id: F9
    nama: "CONFIRM (maksimal 8 slot)"
    tujuan: "Validasi penuh survivor di partisi CONFIRM"
    output: [reports/F9_confirm.md]
    lulus: "Seluruh gates.direction tercentang, tanpa satupun dilonggarkan"
    gagal: "Slot habis tanpa yang lolos -> divisi tidak menghasilkan juara. Berhenti. DILARANG menambah slot."

  - id: F10
    nama: "GOLDEN HOLDOUT (sekali tembak)"
    tujuan: "Vonis akhir di data yang tidak pernah disentuh"
    output: [reports/F10_holdout_verdict.md]
    lulus: "Expectancy net positif + MC2 lolos + degradasi vs CONFIRM < 50%"
    gagal: "Tidak lolos -> SELESAI. Holdout tidak bisa dibuka dua kali. Dilarang menyetel ulang lalu mencoba lagi."

  - id: F11
    nama: "Paket deployment (hanya kalau F10 lolos)"
    tujuan: "Aturan live + kill switch, ditulis SEBELUM uang masuk"
    output: [DEPLOYMENT.md]
    lulus: "Ukuran posisi, kill switch drawdown, ambang tracking error, jadwal peninjauan — tertulis & terkunci sebelum trade pertama"
```

## Stop condition — absolut

Nomor 6 adalah yang paling sering dilanggar: *masalah yang tidak diatur file ini → BERHENTI, tanya user, jangan putuskan sendiri.*

```yaml
stop_conditions:
  0: "F0: K_eff terukur < K_eff yang dibutuhkan pada IC 0.05 -> BERHENTI sebelum kandidat pertama. Data tidak cukup untuk membuktikan apapun."
  1: "F2 (gerbang payoff) GAGAL di semua horizon & instrumen -> BERHENTI TOTAL. DILARANG melonggarkan margin, mengganti arm penentu, atau menghapus syarat sisi short."
  1b: "F2b: tidak ada horizon dengan t_pooled >= 3.0 pada IC 0.05 -> BERHENTI. Jangan jalankan 507 kandidat di data yang kapasitas statistiknya tidak cukup."
  2: "Uji kebocoran (F1) gagal -> BERHENTI. Pipeline validasinya sendiri yang rusak."
  3: "pytest merah di fase manapun -> BERHENTI. Perbaiki."
  4: "Butuh mengubah ambang, confirm_max, atau membuka holdout kedua kali -> BERHENTI. Butuh OVERRIDE V5 tertulis."
  5: "Kandidat butuh data di luar [ohlc, tick_time, tick_spread] -> TOLAK kandidatnya. Jangan cari proxy."
  6: "Masalah yang tidak diatur file ini -> BERHENTI. Tanya user. Jangan putuskan sendiri."
```

## Cara kerja

```yaml
working_rules:
  1: "Baca file ini penuh sebelum mengetik satu baris kode."
  2: "Kerjakan SATU fase, lalu BERHENTI dan lapor sebelum fase berikutnya."
  3: "Commit per fase: 'v5 FASE Fn — <judul>'."
  4: "Setiap laporan memuat: angka apa adanya, apa yang gagal, apa yang dilewati, apa yang belum yakin."
  5: "Kalau tidak yakin — BILANG TIDAK YAKIN. Dilarang menebak angka, sitasi, atau hasil yang belum dihitung."
  6: "Kalau hasilnya jelek — LAPORKAN JELEKNYA. Jangan dipoles. Sistem ini dipakai dengan uang nyata."
  7: "Dilarang melonggarkan gerbang manapun tanpa OVERRIDE V5 tertulis dari user."
  8: "Setiap varian dari grid params = 1 baris ledger. Hitung dan laporkan totalnya di tiap fase."
```

## Pelajaran dari riset sebelumnya

Dibawa sebagai **pelajaran**, bukan kode. Nol warisan kode dari v3/v4.

```yaml
lessons_carried:
  1: "Struktur payoff divalidasi DULU, baru cari sinyal. Riset sebelumnya kebalik dan membuang 3 tahun."
  2: "P-value tanpa bobot keunikan = halusinasi. Metode naif melaporkan 16 dari 112 kandidat signifikan; setelah dikoreksi tersisa 0-1."
  3: "Null benchmark harus ada sebagai KODE. Kalau cuma aturan di dokumen, dia tidak pernah menyaring apapun."
  4: "Biaya dihitung dari durasi holding NYATA dalam bps. Memakai batas waktu maksimum meremehkan biaya 3x."
  5: "Kandidat arah: memilih peringkat 1 dari daftar yang semuanya nol = memilih keberuntungan terbesar."
  6: "Gerbang yang mustahil dilewati (B09 foresight) membunuh semua kandidat tanpa membedakan mutu."
  7: "Effective N 26 membuat kelulusan mustahil secara aritmetika, berapapun jumlah kandidatnya."
  8: "Menambah kandidat menaikkan ambang untuk semua kandidat lain."
  9: "VWAP-band dan keluarga Kalman sebagai anchor mean-reversion sudah diuji dan mati total."
  10: "Order flow tidak bisa dipakai di venue CFD — volume MT5 adalah tick count, DOM adalah buku sintetis."
```
