# 10 — URUTAN FASE, STOP CONDITION & CARA KERJA

> **Urutan fase tidak boleh diubah.** Tiap fase adalah gerbang yang menentukan apakah
> fase berikutnya masuk akal dijalankan.

---

## Peta

```
F0   fondasi, biaya, K_eff, sd_SR      ──► ⛔ GM-1..GM-5 → STOP
F1   infrastruktur + L10 + L11         ──► ⛔ transmitansi <50% → STOP, PERBAIKI GERBANG
F2   PENGUKURAN struktur payoff        ──►    keluaran: shortlist barrier + IC_minimum
F2b  pilot pemilihan horizon (72 baris)──► ⛔ t_pooled < 3.0 di semua horizon → STOP
F3   verifikasi sitasi & dedup         ──►    ≥90% resolve, nol sitasi karangan
F4   divisi estimasi V, Q, S           ──►    Model Confidence Set → fitur rezim untuk router
F5   divisi X — exit & sizing          ──►    prioritas mengikuti hasil F2
F6   tiga keluarga E, TERPISAH         ──►    corong: SHORTLIST → KANDIDAT
F7   divisi M — meta-labeling          ──►    wajib kalahkan baseline linear
F7b  ROUTER multi-strategi             ──►    wajib kalahkan N1, N2, N3
F8   freeze & pre-register             ──►    hash di-commit; L11 diulang
F9   CONFIRM — maks 8 slot             ──►    17 centang penuh, tanpa kelonggaran
F10  GOLDEN HOLDOUT — sekali tembak    ──►    degradasi vs CONFIRM < 50%
F11  paket deployment                  ──►    kill switch ditulis sebelum uang masuk
F12  FORWARD TEST demo ≥200 fill       ──►    cost_verified akhirnya bisa jadi true
```

🔄 **Yang berubah dari v5:** F1 dapat gerbang mati baru (L11). F2 bukan STOP TOTAL lagi.
F6 dipecah per keluarga. F7b (router) baru. F12 (forward test) dinaikkan jadi fase resmi —
di v5 dia cuma catatan.

---

## Fase

```yaml
phases:

- id: F0
  nama: "Fondasi, audit data, model biaya, pengukuran daya"
  output: [config/v6.yaml, config/v6.yaml.sha256, reports/F0_data_audit.md,
           reports/F0_cost_model.md, reports/F0_universe.md, reports/F0_power.md]
  lulus:
    - "Matriks ketersediaan riwayat per instrumen (§03) — DIAUDIT, bukan diduga"
    - "Audit data: gap, duplikat, outlier, jam libur, perubahan spesifikasi kontrak, hash dicatat"
    - "Spread terukur dari tick Dukascopy: rata-rata & persentil 50/75/90/99 per sesi & per jam, dalam BPS"
    - "Biaya prop firm terisi dari halaman resmi + URL + tanggal (§03 B). Yang tidak ketemu ditulis TIDAK_KETEMU."
    - "Rasio keunikan sampel DIUKUR per instrumen per horizon"
    - "Matriks korelasi PnL STRATEGI antar instrumen -> K_eff lewat eigenvalue"
    - "Keputusan jendela pooling TIER-A vs TIER-B dideklarasikan & di-hash"
    - "🔄 sd_SR DIUKUR dari pilot 24 trial -> N_maks dihitung -> anggaran_arah ditetapkan"
    - "🔄 skew & kurt empiris diukur -> penyebut DSR"
    - "config di-hash & di-commit SEBELUM apapun dijalankan"
  gerbang_mati:
    GM-1:  "K_eff terukur < 3.0 -> STOP (ambang v5 dipertahankan)"
    GM-1b: "K_eff < 4.0 ATAU T_confirm < 11 thn -> STOP (syarat gabungan §01 B4b)"
    GM-2:  "N_maks dari sd_SR < 23 (LANTAI) -> STOP, lihat §08 D3"
    GM-4:  "t_pooled CONFIRM @IC 0.05 < 3.0 -> STOP"
    GM-5:  >
      P(breach) > 5% pada ukuran posisi TERKECIL yang masih memenuhi BR_eff >= 100/thn
      -> STOP untuk akun prop firm. Strateginya mungkin nyata tapi tidak muat di
      kendala akunnya. Dihitung dari MC2 memakai aturan TERKETAT (§03 B3).
  gagal_lunak:
    biaya_tidak_ketemu: "tandai UNVERIFIED, pakai skenario worst + penalti 1.5. JANGAN ditebak."

- id: F1
  nama: "Infrastruktur validasi + DUA uji wajib"
  tujuan: "Alat ukurnya dulu. Jangan mengukur pakai alat yang belum diuji."
  output: [src/stats/nulls.py, src/stats/effective_n.py, src/validation/cpcv.py,
           src/validation/montecarlo.py, src/costs/, src/router/, tests/,
           reports/F1_leak_test.md, reports/F1_gate_power.md]
  lulus:
    - "pytest hijau, termasuk 4 uji regresi bug v5 (§06 Bagian F)"
    - "§L10 UJI KEBOCORAN LOLOS: fitur lookahead sengaja mengalahkan semua null"
    - "Sinyal acak murni TIDAK mengalahkan null manapun"
    - "🔄 §L11 UJI DAYA GERBANG LOLOS: transmitansi >=80% screening, >=70% robustness, >=50% rantai penuh, pada IC 0.05"
    - "🔄 §L12e uji kebocoran lintas-seksi LOLOS"
    - "Matriks korelasi null + jumlah null independen efektif dilaporkan"
    - "Klasifikasi KILL vs FLAG tiap gerbang DITETAPKAN OTOMATIS dari hasil L11 (§07 D)"
  gerbang_mati:
    GM-3: >
      Transmitansi < 50% -> STOP. PERBAIKI DESAIN GERBANG (urutan, tahapan, KILL vs FLAG).
      DILARANG menurunkan ambang CONFIRM. DILARANG lanjut ke F2.
    leak: "Fitur lookahead tidak mengalahkan null -> BUG DI NULL. Perbaiki. Jangan lanjut."

- id: F2
  nama: "PENGUKURAN struktur payoff (entry ACAK)"
  # 🔄 BUKAN gerbang mati lagi — lihat §05 Bagian C untuk alasan teoretisnya
  tujuan: "Ukur permukaan titik impas, simpangan dari optional stopping, dan IC_minimum"
  output: [reports/F2_payoff_surface.json, reports/F2_ringkasan.md]
  keluaran_wajib:
    - "permukaan titik impas mekanis atas (k_sl, k_tp)"
    - "permukaan simpangan Delta vs martingale sintetis + CI bootstrap"
    - "permukaan IC_minimum yang dibutuhkan, pada biaya best/base/worst"
    - "SHORTLIST maks 3 barrier dengan IC_minimum terendah -> dibawa ke F5/F6"
    - "durasi hit barrier NYATA -> input kappa"
  ledger: ledger_diagnostik
  tidak_ada_stop_total: >
    Delta tidak beda dari nol adalah TEMUAN, bukan kegagalan: artinya bentuk exit
    sendirian tidak bisa menciptakan edge, seluruh edge harus datang dari
    pengondisian entry. Divisi X turun prioritas, F6 naik prioritas. Lanjut.

- id: F2b
  nama: "PEMILIHAN HORIZON lewat pilot kecil"
  pilot_set:
    formula: [MOM01, MOM04, MOM05, MOM08, MRV01, MRV03, BRK01, BRK03, BRK05, X06, V01, Q08]
    varian_per_formula: 1
    horizon: 6
    total_baris: 72
    ledger: ledger_diagnostik
    catatan: >
      🔄 Pilot HANYA berisi tier-1. MOM07 (eks E72_THEIL_SEN) dikeluarkan — tier-2,
      O(w^2) per bar; v5 keliru mengklaim pilotnya "semua tier-1". Diganti MOM05_MANN_KENDALL.
      MRV02 juga dikeluarkan (tier-2: PCA + AR(1) refit per bar) — diganti MRV03 (tier-1).
  yang_diukur_per_horizon:
    - "kappa = biaya_bps / volatilitas_horizon_bps, dari durasi barrier-hit NYATA"
    - "BR_eff = trades/tahun x rasio keunikan"
    - "K_eff dari matriks korelasi PnL antar instrumen PADA horizon itu"
    - "t_single dan t_pooled pada IC 0.03 dan 0.05"
  lulus: "Pilih horizon dengan t_pooled tertinggi pada IC 0.05, SYARAT t_pooled >= 3.0. Maksimal 2 horizon."
  gagal: >
    Tidak ada horizon dengan t_pooled >= 3.0 pada IC 0.05 -> BERHENTI dan lapor.
    Menjalankan 82 kandidat setelah itu hanya membuang waktu komputasi.
    Opsi yang dilaporkan: tambah instrumen berkorelasi rendah, perpanjang riwayat,
    atau turunkan target frekuensi (naikkan keunikan).
  catatan: "Fase ini BUKAN pencarian sinyal. Ini pengukuran kapasitas statistik data."

- id: F3
  nama: "Verifikasi sitasi, dedup, kunci registri"
  output: [registry/candidates_v6.yaml, registry/rejected_log.md, reports/F3_citation_verification.csv]
  lulus:
    - ">=90% sitasi terverifikasi resolve (DOI atau SSRN ID atau NBER WP)"
    - "NOL sitasi karangan"
    - "NOL rumus ritel"
    - "Dedup dijalankan di partisi screen SEBELUM eksekusi: korelasi PnL >=0.90 -> alias/auto-kill"
    - "🔄 Dedup LINTAS KELUARGA: korelasi >=0.90 antar keluarga berbeda -> taksonomi salah, WAJIB diselesaikan"
    - "Jumlah varian <= anggaran_arah dari F0"
    - "Setiap formula punya TEPAT SATU tier komputasi (diverifikasi otomatis)"
    - "Setiap kandidat arah punya family & prior_sign yang dideklarasikan (§O11)"
  gagal: "Sitasi tidak ketemu -> NEED_LOOKUP, boleh screening, DILARANG masuk CONFIRM. DILARANG mengarang."

- id: F4
  nama: "Divisi estimasi — V, Q, S"
  tujuan: "Kunci alat ukur volatilitas, spread, dan REZIM"
  ledger: ledger_estimasi
  output: [reports/F4_estimation_champions.md]
  lulus: "Juara per horizon lewat Model Confidence Set alpha=0.10; imbang -> pilih tersederhana"
  gagal: "Tidak ada yang mengalahkan baseline naif -> pakai baseline, catat, jangan dipaksakan"
  catatan_penting: >
    Hanya fitur rezim yang LOLOS MCS di sini yang boleh masuk router F7b.
    Router DILARANG memakai fitur yang belum lolos gerbangnya sendiri.
  sudah_diketahui_dari_v5: "V07_BIPOWER, V08_MEDRV, Q02_CORWIN_SCHULTZ sudah LOLOS. Konfirmasi ulang di sampel baru."

- id: F5
  nama: "Divisi X — Exit & Sizing"
  ledger: ledger_arah
  prioritas: "ditentukan hasil F2 — lihat §05 C2"
  output: [reports/F5_exit_sizing.md]
  lulus: "Aturan exit/sizing yang mengalahkan X06 baseline lewat corong tahap 1-2, termasuk MC2"
  gagal: "Nol lolos -> laporkan, lanjut F6 dengan barrier shortlist dari F2"
  catatan: >
    Pelajaran v5: X gugur karena exit diuji di atas ENTRY ACAK. Exit tidak bisa
    menciptakan arah — dia hanya membentuk ulang distribusi. Nilai divisi X baru
    muncul digabung dengan sinyal berarah. Karena itu X33_DRAWDOWN_CONSTRAINED_SIZING
    tetap wajib (dia bentuk matematis aturan prop firm), tapi exit lain diuji ULANG
    di F6 sebagai kombinasi entry x exit.

- id: F6
  nama: "Tiga keluarga entry — DIUJI TERPISAH"
  ledger: ledger_arah
  output: [reports/F6_MOM.md, reports/F6_MRV.md, reports/F6_BRK.md, ledger_arah.csv]
  prosedur:
    - "Tiap keluarga (MOM, MRV, BRK) melewati corong tahap 1 lalu tahap 2, TERPISAH"
    - "Tiap keluarga dapat vonis sendiri: SHORTLIST / KANDIDAT / gugur"
    - "🔄 Untuk tiap sinyal dengan expectancy KOTOR positif: uji ulang dengan 3 barrier shortlist dari F2 (kombinasi entry x exit)"
    - "Uji interaksi prior (§09 D): apakah tiap keluarga menang di rezim yang diprediksi?"
  angka_yang_WAJIB_dilaporkan:
    - "berapa sinyal yang expectancy KOTORNYA positif, per keluarga"
    - "berapa bps biaya harus turun supaya BERSIHNYA positif"
    - "t tertinggi yang tercapai, per keluarga  <- PALING PENTING (§07 E langkah 3)"
    - "tanda interaksi rezim vs prior_sign yang dipra-registrasi"
  gagal: "Nol survivor -> protokol_nol_lolos §07 E, MULAI DARI LANGKAH 0. JANGAN menambah kandidat."

- id: F7
  nama: "Meta-labeling & ML (divisi M)"
  ledger: ledger_arah
  output: [reports/F7_meta_ml.md]
  prioritas: "M11_META_LABELING duluan — satu-satunya mekanisme yang TERBUKTI bekerja di v5"
  lulus: "Mengalahkan baseline linear teregularisasi (M06/M07) DAN sinyal primer polos"
  gagal: "Tidak mengalahkan baseline -> pakai sinyal primer polos, catat"
  peringatan_anggaran: "Grid hyperparameter <= 8 per model (§06 E). Grid 100 = 100 baris = seluruh anggaran."

- id: F7b
  nama: "🔄 ROUTER multi-strategi"
  ledger: ledger_arah
  prasyarat: ">= 2 keluarga lolos corong tahap 2. Kalau cuma 1 -> TIDAK ADA ROUTER (§09 F)."
  output: [reports/F7b_router.md]
  lulus:
    - "mengalahkan N1_EQUAL_WEIGHT_STATIC"
    - "mengalahkan N2_BEST_SINGLE_FAMILY (via MCS, bukan argmax)"
    - "mengalahkan N3_REGIME_SHUFFLE di atas persentil 95  <- PALING PENTING"
    - "tanda interaksi rezim SESUAI prior yang dipra-registrasi"
    - "grep src/router/ untuk sort|argmax|idxmax|nlargest|max( -> NOL hasil"
  gagal:
    kalah_N3: "Deteksi rezimnya derau. Buang router, pakai bobot sama (N1). Laporkan."
    kalah_N1: "Informasi rezim tidak menambah nilai. Pakai bobot sama. Laporkan."
    tanda_terbalik: "SIGN_FLIP_SUSPECT. DILARANG membalik prior lalu menyebutnya penemuan."

- id: F8
  nama: "Freeze & pre-register"
  output: [PREREGISTRATION.md, config hash di-commit]
  lulus:
    - "Semua parameter, ambang, aturan keputusan terkunci dan ter-hash"
    - "Tanda prior router terkunci"
    - "🔄 L11 DIULANG pada registry final — transmitansi masih >=50%"
    - "meta.locked_on dan config_sha256 TERISI (v5 membiarkannya null — §Temuan Audit 5)"
  gagal: "Ada parameter yang masih akan-ditentukan-nanti -> belum boleh lanjut"

- id: F9
  nama: "CONFIRM (maksimal 8 slot)"
  partisi: CONFIRM
  output: [reports/F9_confirm.md]
  lulus: "SELURUH 17 centang gates.direction, tanpa satupun dilonggarkan"
  gagal: "Slot habis tanpa yang lolos -> tidak ada juara. Berhenti. DILARANG menambah slot."

- id: F10
  nama: "GOLDEN HOLDOUT (sekali tembak)"
  output: [reports/F10_holdout_verdict.md]
  lulus: "Expectancy net positif + MC2 lolos + degradasi vs CONFIRM < 50%"
  gagal: "Tidak lolos -> SELESAI. Holdout tidak bisa dibuka dua kali."

- id: F11
  nama: "Paket deployment (hanya kalau F10 lolos)"
  output: [DEPLOYMENT.md]
  lulus: >
    Ukuran posisi (dari MC2, bukan dari keinginan), kill switch drawdown, ambang
    tracking error, jadwal peninjauan — tertulis & terkunci sebelum trade pertama.

- id: F12
  nama: "🔄 FORWARD TEST demo (fase resmi, bukan catatan)"
  tujuan: "Satu-satunya jalan cost_verified jadi true"
  lulus:
    - "Demo prop firm, minimal 200 fill nyata"
    - "Bandingkan fill nyata vs yang dimodelkan; hitung ulang slippage dari fill"
    - "Konfirmasi komisi per-sisi vs round-trip (§03 B1 — masih AMBIGU)"
    - "Jalankan ulang MC2 dengan biaya terverifikasi"
    - "Degradasi vs HOLDOUT < 50%"
  baru_setelah_itu: "uang asli, ukuran kecil, kill switch aktif"
```

---

## Stop condition — absolut

```yaml
stop_conditions:
  0:  "F0: K_eff < 3.0 -> BERHENTI"
  0a: "F0: K_eff < 4.0 ATAU T_confirm < 11 thn -> BERHENTI (syarat gabungan, transmitansi <50%)"
  0b: "F0: N_maks dari sd_SR < LANTAI 23 -> BERHENTI (§08 D3)"
  0c: "F0: t_pooled CONFIRM @IC 0.05 < 3.0 -> BERHENTI"
  0d: "F0: P(breach) > 5% di ukuran posisi terkecil yang layak -> BERHENTI (GM-5)"
  1:  "🔄 F1: transmitansi L11 < 50% -> BERHENTI. PERBAIKI GERBANG, bukan ambang."
  2:  "F1: uji kebocoran L10 gagal -> BERHENTI. Pipeline validasinya sendiri rusak."
  2b: "F1: uji kebocoran lintas-seksi L12e gagal -> BERHENTI. Penyelarasan sesi bermasalah."
  3:  "pytest merah di fase manapun -> BERHENTI. Perbaiki."
  4:  "F2b: tidak ada horizon dengan t_pooled >= 3.0 -> BERHENTI."
  5:  "Butuh mengubah ambang, confirm_max, atau membuka holdout kedua kali -> BERHENTI. OVERRIDE V6 tertulis."
  6:  "Kandidat butuh data di luar [ohlc, tick_time, tick_spread] -> TOLAK kandidatnya. Jangan cari proxy."
  7:  "Masalah yang tidak diatur file ini -> BERHENTI. Tanya user. Jangan putuskan sendiri."
```

> **Nomor 7 yang paling sering dilanggar.**

---

## Cara kerja

```yaml
working_rules:
  1: "Baca SELURUH file inti (00-10) sebelum mengetik satu baris kode."
  2: "Kerjakan SATU fase, lalu BERHENTI dan lapor sebelum fase berikutnya."
  3: "Commit per fase: 'v6 FASE Fn — <judul>'."
  4: "Setiap laporan memuat: angka apa adanya, apa yang gagal, apa yang dilewati, apa yang belum yakin."
  5: "Kalau tidak yakin — BILANG TIDAK YAKIN. Dilarang menebak angka, sitasi, atau hasil yang belum dihitung."
  6: "Kalau hasilnya jelek — LAPORKAN JELEKNYA. Jangan dipoles. Sistem ini dipakai dengan uang nyata."
  7: "Dilarang melonggarkan gerbang manapun tanpa OVERRIDE V6 tertulis dari user."
  8: "Setiap varian dari grid params = 1 baris ledger. Hitung dan laporkan totalnya di tiap fase."
  9: "🔄 Setiap tabel angka di dokumen ini WAJIB dihitung ulang dari rumusnya. Beda -> pakai hasil hitung, laporkan."
  10: "🔄 Setiap laporan mencantumkan: 'BIAYA BELUM TERVERIFIKASI' sampai F12 selesai."
```

---

## Pelajaran yang dibawa

```yaml
lessons_carried:
  1:  "Struktur payoff diukur DULU, tapi kegagalannya BUKAN alasan berhenti — optional stopping menjaminnya gagal."
  2:  "P-value tanpa bobot keunikan = halusinasi. 16 dari 112 'signifikan' jadi 0-1 setelah dikoreksi."
  3:  "Null benchmark harus ada sebagai KODE. Kalau cuma aturan di dokumen, dia tidak pernah menyaring."
  4:  "Biaya dihitung dari durasi holding NYATA dalam bps. Batas waktu maksimum meremehkan biaya 3x."
  5:  "Kandidat arah: memilih peringkat 1 dari daftar yang semuanya nol = memilih keberuntungan terbesar."
  6:  "Gerbang yang mustahil dilewati membunuh semua kandidat tanpa membedakan mutu."
  7:  "Effective N kecil membuat kelulusan mustahil secara aritmetika, berapapun jumlah kandidatnya."
  8:  "Menambah kandidat menaikkan ambang untuk semua kandidat lain — lewat SR_0 di DSR."
  9:  "VWAP-band dan Kalman sebagai anchor mean-reversion sudah diuji dan mati total."
  10: "Order flow tidak bisa dipakai di venue CFD — volume MT5 tick count, DOM buku sintetis."
  11: "🔄 Gerbang yang tidak pernah diukur transmitansinya adalah gerbang yang tidak Anda pahami."
  12: "🔄 DSR tidak bisa diperbaiki dengan menambah sampel. Hanya N dan sd_SR yang menolong."
  13: "🔄 Pendeteksi rezim bukan sinyal arah. Mengujinya dengan gerbang arah menjamin kegagalan."
  14: "🔄 Kendala prop firm bisa mengikat lebih keras daripada edge-nya. Hitung MC2 SEBELUM memilih kandidat."
```

---

**Selesai. Kembali ke `CLAUDE.md` untuk peta file divisi.**
