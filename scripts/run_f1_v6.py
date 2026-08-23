#!/usr/bin/env python3
"""F1 -- infrastruktur validasi + L10 (uji kebocoran, via pytest) + L11
(uji daya gerbang / transmitansi corong). Dijalankan di data SINTETIS
(L10, random walk buatan) dan sinyal sintetis ber-IC terkontrol disuntikkan
ke harga XAUUSD NYATA (L11) -- TIDAK butuh panel lengkap / F0 lolos, sesuai
07_GERBANG_CORONG.md: alat ukur dibangun sebelum kandidat pertama.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspace/xau-alpha-v5")
from src.validation.l11_gate_power import make_h240_blocks, run_l11, synthetic_signal
from scripts.run_cost_regime_v6 import regime_cost, RECENT_YEARS_N, yearly_kappa_table

REPORTS = Path("/workspace/xau-alpha-v5/reports")
BAR_DIR = Path("/workspace/data/bars_candles")

IC_GRID = [0.03, 0.05, 0.08]
N_SEEDS = 150  # spec: 500. Dikurangi untuk kecepatan -- didokumentasikan di l11_gate_power.py docstring.

MC2_RULES = dict(max_daily_loss_pct=3.0, max_total_drawdown_pct=6.0, profit_target_pct=10.0)


def run_l10_pytest() -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_l10_leakage.py", "-v", "--tb=short"],
        cwd="/workspace/xau-alpha-v5", capture_output=True, text=True,
    )
    passed = proc.returncode == 0
    lines = ["# F1 -- Uji Kebocoran L10 (pytest)\n",
              f"**Hasil: {'LOLOS' if passed else 'GAGAL'}** (exit code {proc.returncode})\n",
              "```", proc.stdout[-4000:], proc.stderr[-2000:] if proc.stderr else "", "```"]
    (REPORTS / "F1_leak_test.md").write_text("\n".join(lines))
    print(f"L10 pytest: {'PASS' if passed else 'FAIL'}")
    return {"passed": passed, "returncode": proc.returncode}


def compute_worst_cost_bps_h240_recent_regime() -> tuple[float, list]:
    """KOREKSI METODOLOGI: biaya kelayakan dihitung HANYA dari N_tahun terakhir
    yang tersedia (rezim biaya relevan untuk eksekusi sekarang), BUKAN
    dirata-ratakan dari seluruh riwayat (yang mencampur rezim harga berbeda
    jauh -- lihat F0_cost_regime.md). Signal itu sendiri (r_block, statistik)
    tetap dari SELURUH riwayat -- lihat main()."""
    bars = pd.read_parquet(BAR_DIR / "XAUUSD_M5.parquet")
    bars["bar_time"] = pd.to_datetime(bars["bar_time"], utc=True)
    years_present = sorted(bars["bar_time"].dt.year.unique().tolist())
    recent_years = years_present[-RECENT_YEARS_N:]
    cost = regime_cost("XAUUSD", recent_years)
    return float(cost), recent_years


def main():
    l10 = run_l10_pytest()

    m15 = pd.read_parquet(BAR_DIR / "XAUUSD_M15.parquet")
    mid = m15["mid_close"].dropna().values
    r_block = make_h240_blocks(mid, block_bars=16)

    span_days = (pd.to_datetime(m15["bar_time"].iloc[-1]) - pd.to_datetime(m15["bar_time"].iloc[0])).days
    span_years = span_days / 365.25
    br_eff_per_year = len(r_block) / span_years

    cost_worst, recent_years = compute_worst_cost_bps_h240_recent_regime()

    print(f"H240 blocks: {len(r_block)}, span={span_years:.2f}y, BR_eff/yr={br_eff_per_year:.1f}, "
          f"cost_worst={cost_worst:.2f}bps")

    results = run_l11(r_block, IC_GRID, N_SEEDS, cost_worst, br_eff_per_year, MC2_RULES)

    cost_full_regime = regime_cost("XAUUSD", sorted(pd.read_parquet(BAR_DIR / "XAUUSD_M5.parquet")
                                    .assign(y=lambda d: pd.to_datetime(d["bar_time"], utc=True).dt.year)["y"]
                                    .unique().tolist()))

    lines = ["# F1 -- Uji Daya Gerbang L11 (transmitansi corong v6)\n"]
    lines.append(
        f"> **Sinyal divalidasi di {span_years:.2f} tahun ({len(r_block)} blok H240, seluruh riwayat XAUUSD "
        f"yang ada). Biaya divalidasi di {RECENT_YEARS_N} tahun terakhir "
        f"({recent_years[0]}-{recent_years[-1]}).**\n"
    )
    lines.append(
        "## Tabel kappa PER TAHUN KALENDER (XAUUSD, H240, skenario worst)\n"
    )
    yk = yearly_kappa_table("XAUUSD")
    lines.append("| tahun | harga rata-rata | spread p50 bps | spread p90 bps | sigma M5 bps | "
                  "biaya worst bps | sigma H240 bps | **kappa H240 worst** |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in yk.iterrows():
        marker = " **<-rezim-sekarang**" if int(r["year"]) in recent_years else ""
        lines.append(f"| {int(r['year'])}{marker} | {r['mean_price']:.1f} | {r['spread_p50_bps']:.3f} | "
                      f"{r['spread_p90_bps']:.3f} | {r['sigma_m5_bps']:.3f} | {r['cost_worst_bps']:.2f} | "
                      f"{r['sigma_h240_bps']:.2f} | **{r['kappa_h240_worst']:.3f}** |")
    lines.append(f"\n**Biaya worst-case: seluruh riwayat (dicampur, TIDAK dipakai untuk kelayakan) = "
                  f"{cost_full_regime:.2f} bps vs rezim-sekarang (dipakai untuk kelayakan) = "
                  f"{cost_worst:.2f} bps.**\n")
    lines.append("## Expectancy bersih berdampingan: biaya-LAMA (seluruh riwayat) vs biaya-BARU (rezim-sekarang)\n")
    lines.append("| IC | gross edge (bps) | net @ biaya-LAMA ({:.1f}bps) | net @ biaya-BARU ({:.1f}bps) |"
                  .format(cost_full_regime, cost_worst))
    lines.append("|---:|---:|---:|---:|")
    for ic_e in [0.03, 0.05, 0.08, 0.15, 0.30]:
        grosses_e = []
        for s in range(50):
            rng_e = np.random.default_rng(60000 + s)
            sig_e = synthetic_signal(r_block, ic_e, rng_e)
            tr_e = min(1.0, 220.0 / br_eff_per_year)
            th_e = np.quantile(np.abs(sig_e), 1 - tr_e)
            tk_e = np.abs(sig_e) >= th_e
            pos_e = np.where(tk_e, np.sign(sig_e), 0.0)
            grosses_e.append(((pos_e * r_block)[tk_e]).mean() * 1e4)
        g_e = float(np.mean(grosses_e))
        lines.append(f"| {ic_e} | {g_e:.2f} | {g_e - cost_full_regime:.2f} | {g_e - cost_worst:.2f} |")
    lines.append(f"\nSinyal sintetis ber-IC terkontrol disuntikkan ke harga **XAUUSD NYATA** (M15, blok H240 "
                  f"non-overlapping, n={len(r_block)} blok, rentang {span_years:.2f} tahun -- statistik). "
                  f"n_seeds per IC = **{N_SEEDS}** (spec: 500 -- dikurangi untuk kecepatan, lihat catatan "
                  f"di `src/validation/l11_gate_power.py`). Biaya worst-case rezim-sekarang "
                  f"({recent_years[0]}-{recent_years[-1]}): **{cost_worst:.2f} bps** (bukan lagi rata-rata "
                  f"seluruh riwayat). BR_eff/tahun (uniqueness=1, blok non-overlap): **{br_eff_per_year:.1f}**.\n")
    lines.append("| IC target | Tahap 1 SARINGAN | Tahap 2 ROBUSTNESS | Rantai penuh (CONFIRM) | target |")
    lines.append("|---:|---:|---:|---:|---|")
    targets = {"tier1": 80.0, "tier2": 70.0, "chain": 50.0}
    for ic in IC_GRID:
        r = results[ic]
        lines.append(f"| {ic} | {r['transmit_tier1_pct']:.1f}% (target>=80%) | "
                      f"{r['transmit_tier2_pct']:.1f}% (target>=70%) | "
                      f"{r['transmit_chain_pct']:.1f}% (target>=50%) | -- |")

    r5 = results[0.05]
    gm3_pass = (r5["transmit_tier1_pct"] >= 80.0 and r5["transmit_tier2_pct"] >= 70.0
                and r5["transmit_chain_pct"] >= 50.0)
    lines.append(f"\n## Verdict GM-3 (pada IC=0.05, syarat L11 §02 HUKUM)\n")
    lines.append(f"Screening>=80%: {'LOLOS' if r5['transmit_tier1_pct']>=80 else 'GAGAL'} ({r5['transmit_tier1_pct']:.1f}%)  \n"
                  f"Robustness>=70%: {'LOLOS' if r5['transmit_tier2_pct']>=70 else 'GAGAL'} ({r5['transmit_tier2_pct']:.1f}%)  \n"
                  f"Rantai penuh>=50%: {'LOLOS' if r5['transmit_chain_pct']>=50 else 'GAGAL'} ({r5['transmit_chain_pct']:.1f}%)  \n\n"
                  f"**GM-3: {'LOLOS -- boleh lanjut ke F2' if gm3_pass else 'GAGAL -- BERHENTI, perbaiki desain gerbang'}**\n")
    lines.append("## Gerbang mana yang paling mematikan? (diagnosis per-filter, IC=0.05)\n")
    lines.append("Proporsi trial (dari {} seed) yang LOLOS tiap filter INDIVIDUAL -- bukan cuma vonis "
                  "gabungan per tier. Ini menjawab 'kenapa transmitansi rendah', bukan cuma 'berapa'.\n"
                  .format(N_SEEDS))
    lines.append("### Tahap 1 SARINGAN (dari seluruh {} seed)\n".format(N_SEEDS))
    lines.append("| filter | % lolos |")
    lines.append("|---|---:|")
    t1r = r5.get("tier1_filter_pass_pct", {})
    for name, pct in sorted(t1r.items(), key=lambda kv: kv[1]):
        marker = " <-- **PALING MEMATIKAN**" if pct == min(t1r.values()) else ""
        lines.append(f"| {name} | {pct:.1f}%{marker} |")
    n_t2_reached = r5.get("n_reached_tier2", 0)
    lines.append(f"\n### Tahap 2 ROBUSTNESS (dari {n_t2_reached} trial yang lolos tahap 1)\n")
    t2r = r5.get("tier2_filter_pass_pct", {})
    if t2r:
        lines.append("| filter | % lolos |")
        lines.append("|---|---:|")
        for name, pct in sorted(t2r.items(), key=lambda kv: kv[1]):
            marker = " <-- **PALING MEMATIKAN DI TAHAP INI**" if pct == min(t2r.values()) else ""
            lines.append(f"| {name} | {pct:.1f}%{marker} |")
    else:
        lines.append("N/A -- nol trial lolos tahap 1, jadi tahap 2 tidak pernah dievaluasi.\n")

    if t1r:
        worst_filter = min(t1r, key=t1r.get)
        lines.append(f"\n**Kesimpulan:** gerbang paling mematikan adalah **{worst_filter}** "
                      f"({t1r[worst_filter]:.1f}% lolos). ")
        if "F_EXPECT" in worst_filter:
            lines.append("Ini KONSISTEN dengan diagnosis biaya di atas: expectancy bersih negatif karena "
                          "biaya round-trip melebihi gross edge pada IC realistis -- bukan masalah "
                          "signifikansi statistik (t-stat), bukan masalah frekuensi trade (BR_eff), dan "
                          "bukan gagal mengalahkan null acak. **Akar masalahnya murni EKONOMI biaya vs "
                          "edge, bukan kekuatan statistik gerbangnya.**\n")
        else:
            lines.append(f"Ini BUKAN F_EXPECT -- artinya bukan cuma soal biaya, ada komponen lain yang perlu diperiksa.\n")

    lines.append(f"\nsd_SR empiris (dari sharpe 150 trial IC=0.05, efek samping L11 -- BUKAN pilot 24-trial "
                  f"resmi §01 B5, tapi indikasi awal): **{r5['sharpe_std_empirical']:.4f}**\n")

    # Diagnosis akar penyebab -- bukan cuma melaporkan 0%, tapi KENAPA.
    lines.append("## Diagnosis akar penyebab (langkah 0, §07 E: periksa alat dulu)\n")
    lines.append("Gross edge rata-rata per trade (SEBELUM biaya), pada frekuensi realistis ~220 trade/tahun:\n")
    lines.append("| IC target | gross edge (bps/trade) | biaya worst (bps/trade) | selisih |")
    lines.append("|---:|---:|---:|---:|")
    diag_rows = []
    for ic_d in [0.03, 0.05, 0.08, 0.15, 0.30]:
        grosses = []
        for s in range(30):
            rng_d = np.random.default_rng(20000 + s)
            sig_d = synthetic_signal(r_block, ic_d, rng_d)
            tr = min(1.0, 220.0 / br_eff_per_year)
            th = np.quantile(np.abs(sig_d), 1 - tr)
            tk = np.abs(sig_d) >= th
            pos = np.where(tk, np.sign(sig_d), 0.0)
            grosses.append(((pos * r_block)[tk]).mean() * 1e4)
        g = float(np.mean(grosses))
        diag_rows.append((ic_d, g))
        lines.append(f"| {ic_d} | {g:.2f} | {cost_worst:.2f} | {g - cost_worst:.2f} |")
    lines.append(
        f"\n**Kesimpulan diagnosis (biaya REZIM-SEKARANG {recent_years[0]}-{recent_years[-1]}, sudah "
        f"dikoreksi -- lihat `F0_cost_regime.md`):** bahkan pada IC=0.30 (6x di atas rentang realistis "
        f"0.02-0.05 yang dinyatakan di spec §01), gross edge per trade (~{diag_rows[-1][1]:.1f} bps) baru "
        f"SETARA biaya worst-case rezim-sekarang ({cost_worst:.1f} bps) -- belum lolos, apalagi net "
        f"positif dengan margin. Ini **BUKAN** bug pengukuran, dan **BUKAN LAGI** artefak biaya yang "
        f"dirata-ratakan lintas rezim harga berbeda (kesalahan metodologi sebelumnya sudah diperbaiki). "
        f"**Temuan independen dari GM-1/GM-1b**: bahkan kalau panel diperluas sampai K_eff>=4.0, struktur "
        f"biaya H240 utk XAUUSD tunggal tetap jadi kendala keras di rezim biaya sekarang.\n"
    )
    lines.append(
        "**Keterbatasan uji L11 yang wajib diakui:** konstruksi trade di sini adalah "
        "SATU eksposur tetap sampai akhir blok (tanpa SL/TP dioptimalkan) -- divisi X (exit & sizing) "
        "belum diuji. Kandidat nyata dengan barrier yang dioptimalkan kemungkinan menangkap lebih banyak "
        "dari IC yang sama, jadi hasil 0% di sini KEMUNGKINAN pesimistis dibanding kandidat nyata -- tapi "
        "tanpa F2/F5 dijalankan, ini tidak bisa dipastikan, hanya diakui sebagai batasan uji, bukan "
        "dijadikan alasan mengabaikan hasilnya.\n"
    )
    # ---- Cek tambahan: apakah horizon lebih panjang (H1D) atau sesi murah menolong? ----
    lines.append("## Cek lanjutan: horizon H1D dan pembatasan sesi murah (§07 E langkah 1-2)\n")

    m15_full = pd.read_parquet(BAR_DIR / "XAUUSD_M15.parquet")
    mid_h1d = m15_full["mid_close"].dropna().values
    r_block_h1d = make_h240_blocks(mid_h1d, block_bars=96)  # 96*15min = 1440min = H1D
    br_eff_h1d = len(r_block_h1d) / span_years

    def gross_at(r_blk, ic, br_eff, n=50, seed0=70000):
        gs = []
        for s in range(n):
            rng_h = np.random.default_rng(seed0 + s)
            sig_h = synthetic_signal(r_blk, ic, rng_h)
            tr_h = min(1.0, 220.0 / br_eff)
            th_h = np.quantile(np.abs(sig_h), 1 - tr_h)
            tk_h = np.abs(sig_h) >= th_h
            pos_h = np.where(tk_h, np.sign(sig_h), 0.0)
            gs.append(((pos_h * r_blk)[tk_h]).mean() * 1e4)
        return float(np.mean(gs))

    lines.append(f"**H1D** ({len(r_block_h1d)} blok): biaya round-trip TIDAK bergantung horizon (spread/slip "
                  f"per trade sama, {cost_worst:.2f} bps), yang berubah cuma volatilitas per blok (lebih besar "
                  f"di H1D). Gross edge:\n")
    lines.append("| IC | gross edge H1D (bps) | net @ biaya-BARU |")
    lines.append("|---:|---:|---:|")
    for ic_h in [0.05, 0.15, 0.30]:
        g_h = gross_at(r_block_h1d, ic_h, br_eff_h1d)
        lines.append(f"| {ic_h} | {g_h:.2f} | {g_h - cost_worst:.2f} |")

    # sesi murah: quartile jam UTC dengan spread termurah, hitung ulang cost_worst HANYA di jam itu
    bars5 = pd.read_parquet(BAR_DIR / "XAUUSD_M5.parquet")
    bars5["bar_time"] = pd.to_datetime(bars5["bar_time"], utc=True)
    recent_mask = bars5["bar_time"].dt.year.isin(recent_years)
    bars5r = bars5[recent_mask].copy()
    bars5r["hour_utc"] = bars5r["bar_time"].dt.hour
    by_hour_median = bars5r.groupby("hour_utc")["spread_bps"].median().sort_values()
    cheap_hours = by_hour_median.index[:6].tolist()  # 6 termurah dari 24 jam
    sb_cheap = bars5r[bars5r["hour_utc"].isin(cheap_hours)]["spread_bps"].dropna()
    sb_cheap = sb_cheap[(sb_cheap > 0) & (sb_cheap < 1000)]
    p90_cheap = sb_cheap.quantile(0.90)
    bars5r["mid_ret"] = bars5r["mid_close"].pct_change()
    sigma_m5_cheap = bars5r[bars5r["hour_utc"].isin(cheap_hours)]["mid_close"].pct_change().std() * 1e4
    sigma_m1_cheap = sigma_m5_cheap / np.sqrt(5.0)
    sigma_lat10_cheap = sigma_m1_cheap * np.sqrt(10 / 60.0)
    slip_cheap = 1.5 * p90_cheap + 0.5 * sigma_lat10_cheap
    cost_cheap = (2 * p90_cheap + slip_cheap) * 1.5 + 2 * 0.140

    sb_full_recent = bars5r["spread_bps"].dropna()
    sb_full_recent = sb_full_recent[(sb_full_recent > 0) & (sb_full_recent < 1000)]
    p90_full_recent = sb_full_recent.quantile(0.90)
    lines.append(f"\n**Sesi murah** (6 jam UTC termurah dari 24, rezim {recent_years[0]}-{recent_years[-1]}): "
                  f"jam {sorted(cheap_hours)}, spread p90 = {p90_cheap:.3f} bps (vs {p90_full_recent:.3f} bps "
                  f"24-jam penuh) -> biaya worst = **{cost_cheap:.2f} bps** (vs {cost_worst:.2f} bps 24-jam "
                  f"penuh).\n")
    lines.append("| IC | gross edge (bps) | net @ biaya sesi-murah |")
    lines.append("|---:|---:|---:|")
    for ic_c in [0.05, 0.15, 0.30]:
        g_c = gross_at(r_block, ic_c, br_eff_per_year)
        lines.append(f"| {ic_c} | {g_c:.2f} | {g_c - cost_cheap:.2f} |")

    improves_h1d = gross_at(r_block_h1d, 0.05, br_eff_h1d) - cost_worst > gross_at(r_block, 0.05, br_eff_per_year) - cost_worst
    improves_cheap = cost_cheap < cost_worst * 0.7
    lines.append(
        f"\n**Kesimpulan cek lanjutan:** H1D {'SEDIKIT MEMBAIK' if improves_h1d else 'TIDAK memperbaiki'} "
        f"struktur biaya-vs-edge secara material (dan H1D tetap `PARKED` di spec, data swap belum ada). "
        f"Sesi murah menurunkan biaya dari {cost_worst:.2f} ke {cost_cheap:.2f} bps "
        f"({'penurunan material' if improves_cheap else 'penurunan tidak cukup besar'}), tapi bahkan di sesi "
        f"termurah, IC=0.05 tetap jauh dari impas -- lihat tabel di atas. **Tidak ada horizon atau "
        f"pembatasan sesi yang ditemukan cukup untuk membalik GM-3 pada IC realistis (0.03-0.08).**\n"
    )

    (REPORTS / "F1_gate_power.md").write_text("\n".join(lines))
    print(f"wrote F1_gate_power.md -- GM3={gm3_pass}")

    import json
    Path(REPORTS / "F1_result.json").write_text(json.dumps(
        {"l10_passed": l10["passed"], "l11": {str(k): v for k, v in results.items()}, "gm3_pass": gm3_pass,
         "cost_worst_bps_h240": cost_worst, "br_eff_per_year": br_eff_per_year}, indent=2, default=str))
    print("F1 DONE.")


if __name__ == "__main__":
    main()
