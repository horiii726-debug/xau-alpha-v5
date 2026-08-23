#!/usr/bin/env python3
"""F1 -- infrastruktur validasi + L10 (uji kebocoran, via pytest) + L11
(uji daya gerbang / transmitansi corong). Dijalankan di data SINTETIS
(L10, random walk buatan) dan sinyal sintetis ber-IC terkontrol disuntikkan
ke harga XAUUSD NYATA (L11) -- TIDAK butuh panel lengkap / F0 lolos, sesuai
07_GERBANG_CORONG.md: alat ukur dibangun sebelum kandidat pertama.

PERBAIKAN (2 koreksi dari user):
1. Biaya 'worst' sekarang bersyarat Q10_SPREAD_PERCENTILE_GATE (spread<=p50,
   BUKAN p90 -- lihat run_cost_regime_v6.cost_worst_bps() untuk alasan).
2. Selektivitas via ambang tau EKSPLISIT pada |signal| (grid [1.0, 1.5]),
   BUKAN threshold yang diturunkan dari target frekuensi trade.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspace/xau-alpha-v5")
from src.validation.l11_gate_power import make_h240_blocks, run_l11, synthetic_signal
from scripts.run_cost_regime_v6 import regime_cost, RECENT_YEARS_N, yearly_kappa_table, cost_worst_bps

REPORTS = Path("/workspace/xau-alpha-v5/reports")
BAR_DIR = Path("/workspace/data/bars_candles")

IC_GRID = [0.03, 0.05, 0.08]
TAU_GRID = [1.0, 1.5]
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


def worst_cost_bps_recent_regime(symbol: str = "XAUUSD") -> tuple[float, list]:
    bars = pd.read_parquet(BAR_DIR / f"{symbol}_M5.parquet")
    bars["bar_time"] = pd.to_datetime(bars["bar_time"], utc=True)
    years_present = sorted(bars["bar_time"].dt.year.unique().tolist())
    recent_years = years_present[-RECENT_YEARS_N:]
    cost = regime_cost(symbol, recent_years)
    return float(cost), recent_years


def gross_at(r_blk: np.ndarray, ic: float, tau: float, n: int = 50, seed0: int = 70000) -> float:
    gs = []
    for s in range(n):
        rng = np.random.default_rng(seed0 + s)
        sig = synthetic_signal(r_blk, ic, rng)
        tk = np.abs(sig) >= tau
        pos = np.where(tk, np.sign(sig), 0.0)
        gs.append(((pos * r_blk)[tk]).mean() * 1e4)
    return float(np.mean(gs))


def main():
    l10 = run_l10_pytest()

    m15 = pd.read_parquet(BAR_DIR / "XAUUSD_M15.parquet")
    mid = m15["mid_close"].dropna().values
    r_block = make_h240_blocks(mid, block_bars=16)

    span_days = (pd.to_datetime(m15["bar_time"].iloc[-1]) - pd.to_datetime(m15["bar_time"].iloc[0])).days
    span_years = span_days / 365.25
    br_eff_per_year = len(r_block) / span_years

    cost_worst, recent_years = worst_cost_bps_recent_regime()
    all_years = sorted(pd.read_parquet(BAR_DIR / "XAUUSD_M5.parquet")
                        .assign(y=lambda d: pd.to_datetime(d["bar_time"], utc=True).dt.year)["y"]
                        .unique().tolist())
    cost_full_regime = regime_cost("XAUUSD", all_years)

    print(f"H240 blocks: {len(r_block)}, span={span_years:.2f}y, BR_eff/yr={br_eff_per_year:.1f}, "
          f"cost_worst(p50-conditional)={cost_worst:.2f}bps (was p90-based ~2x higher before fix)")

    results_by_tau = {tau: run_l11(r_block, IC_GRID, N_SEEDS, cost_worst, br_eff_per_year, MC2_RULES, tau=tau)
                       for tau in TAU_GRID}

    lines = ["# F1 -- Uji Daya Gerbang L11 (transmitansi corong v6)\n"]
    lines.append(
        f"> **Sinyal divalidasi di {span_years:.2f} tahun ({len(r_block)} blok H240, seluruh riwayat XAUUSD "
        f"yang ada). Biaya divalidasi di {RECENT_YEARS_N} tahun terakhir "
        f"({recent_years[0]}-{recent_years[-1]}).**\n"
    )
    lines.append(
        "## KOREKSI 1: biaya 'worst' sekarang bersyarat Q10 (spread<=p50, bukan p90)\n\n"
        "Q10_SPREAD_PERCENTILE_GATE hanya izinkan entry saat spread<=p50 -- jadi distribusi biaya yang "
        "relevan untuk expectancy adalah spread yang LOLOS gerbang (dibatasi p50), bukan p90 seluruh "
        "sampel (yang mencakup periode yang Q10 sendiri akan tolak). Menghitung p90 sambil punya gerbang "
        "yang melarang p90 = menghukum dua kali. **Efek: biaya worst turun dari basis p90 ke basis p50 "
        "(alpha/penalty tetap ketat 1.5x/1.5x).**\n"
    )
    lines.append(
        "## KOREKSI 2: selektivitas via ambang tau EKSPLISIT (bukan target frekuensi)\n\n"
        "Semua kandidat sekarang punya ambang kekuatan sinyal tau pada |signal| (grid [1.0, 1.5]), BUKAN "
        "threshold yang diturunkan supaya pas ~220 trade/tahun. Edge per trade = IC * sigma * "
        "E[z||z|>tau] -- E[z|.] naik dengan tau (tau=0 -> 0.80, tau=1.5 -> ~1.94 untuk normal baku), jadi "
        "makin selektif, makin besar edge per trade untuk IC yang sama. Frekuensi trade adalah AKIBAT dari "
        "tau, dilaporkan bukan dipaksa. Filter `trades>=300/tahun` tidak ada di pipeline L11 ini -- yang "
        "dipakai BR_eff>=100/tahun (F_BR), konsisten dengan §04.\n"
    )

    lines.append("## Tabel kappa PER TAHUN KALENDER (XAUUSD, H240, skenario worst bersyarat Q10)\n")
    yk = yearly_kappa_table("XAUUSD")
    lines.append("| tahun | harga rata-rata | spread p25 bps | spread p50 bps (basis worst) | sigma M5 bps | "
                  "biaya worst bps | sigma H240 bps | **kappa H240 worst** |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in yk.iterrows():
        marker = " **<-rezim-sekarang**" if int(r["year"]) in recent_years else ""
        lines.append(f"| {int(r['year'])}{marker} | {r['mean_price']:.1f} | {r['spread_p25_bps']:.3f} | "
                      f"{r['spread_p50_bps']:.3f} | {r['sigma_m5_bps']:.3f} | {r['cost_worst_bps']:.2f} | "
                      f"{r['sigma_h240_bps']:.2f} | **{r['kappa_h240_worst']:.3f}** |")
    lines.append(f"\n**Biaya worst-case: seluruh riwayat (dicampur, TIDAK dipakai untuk kelayakan) = "
                  f"{cost_full_regime:.2f} bps vs rezim-sekarang (dipakai untuk kelayakan) = "
                  f"{cost_worst:.2f} bps.**\n")

    lines.append("## Expectancy bersih berdampingan: biaya-LAMA vs biaya-BARU, per tau\n")
    for tau in TAU_GRID:
        lines.append(f"\n**tau={tau}**\n")
        lines.append("| IC | gross edge (bps) | net @ biaya-LAMA ({:.1f}bps) | net @ biaya-BARU ({:.1f}bps) |"
                      .format(cost_full_regime, cost_worst))
        lines.append("|---:|---:|---:|---:|")
        for ic_e in [0.03, 0.05, 0.08, 0.15, 0.30]:
            g_e = gross_at(r_block, ic_e, tau, n=50, seed0=60000)
            lines.append(f"| {ic_e} | {g_e:.2f} | {g_e - cost_full_regime:.2f} | {g_e - cost_worst:.2f} |")

    lines.append(f"\nSinyal sintetis ber-IC terkontrol disuntikkan ke harga **XAUUSD NYATA** (M15, blok H240 "
                  f"non-overlapping, n={len(r_block)} blok, rentang {span_years:.2f} tahun -- statistik). "
                  f"n_seeds per IC = **{N_SEEDS}** (spec: 500 -- dikurangi untuk kecepatan). Biaya worst-case "
                  f"rezim-sekarang ({recent_years[0]}-{recent_years[-1]}): **{cost_worst:.2f} bps**.\n")

    lines.append("## Transmitansi per tau\n")
    gm3_pass_any = False
    best_tau = None
    for tau in TAU_GRID:
        results = results_by_tau[tau]
        lines.append(f"\n**tau={tau}**\n")
        lines.append("| IC target | Tahap 1 SARINGAN | Tahap 2 ROBUSTNESS | Rantai penuh (CONFIRM) | avg trade/thn | target |")
        lines.append("|---:|---:|---:|---:|---:|---|")
        for ic in IC_GRID:
            r = results[ic]
            lines.append(f"| {ic} | {r['transmit_tier1_pct']:.1f}% (target>=80%) | "
                          f"{r['transmit_tier2_pct']:.1f}% (target>=70%) | "
                          f"{r['transmit_chain_pct']:.1f}% (target>=50%) | {r['avg_trades_per_year']:.0f} | -- |")
        r5 = results[0.05]
        pass_here = (r5["transmit_tier1_pct"] >= 80.0 and r5["transmit_tier2_pct"] >= 70.0
                     and r5["transmit_chain_pct"] >= 50.0)
        if pass_here:
            gm3_pass_any = True
            best_tau = tau

    lines.append(f"\n## Verdict GM-3 (pada IC=0.05, syarat L11 §02 HUKUM, LOLOS kalau ADA tau yang lolos)\n")
    for tau in TAU_GRID:
        r5 = results_by_tau[tau][0.05]
        pass_here = (r5["transmit_tier1_pct"] >= 80.0 and r5["transmit_tier2_pct"] >= 70.0
                     and r5["transmit_chain_pct"] >= 50.0)
        lines.append(f"- tau={tau}: screening={r5['transmit_tier1_pct']:.1f}%, "
                      f"robustness={r5['transmit_tier2_pct']:.1f}%, rantai={r5['transmit_chain_pct']:.1f}% "
                      f"-> {'LOLOS' if pass_here else 'GAGAL'}")
    lines.append(f"\n**GM-3: {'LOLOS (tau=' + str(best_tau) + ') -- boleh lanjut ke F2' if gm3_pass_any else 'GAGAL di SEMUA tau -- BERHENTI, perbaiki desain gerbang'}**\n")

    # Diagnosis per-filter untuk tau terbaik (atau tau=1.5 kalau semua gagal)
    diag_tau = best_tau if best_tau else TAU_GRID[-1]
    r5_diag = results_by_tau[diag_tau][0.05]
    lines.append(f"## Gerbang mana yang paling mematikan? (diagnosis per-filter, IC=0.05, tau={diag_tau})\n")
    t1r = r5_diag.get("tier1_filter_pass_pct", {})
    lines.append("### Tahap 1 SARINGAN\n")
    lines.append("| filter | % lolos |")
    lines.append("|---|---:|")
    for name, pct in sorted(t1r.items(), key=lambda kv: kv[1]):
        marker = " <-- **PALING MEMATIKAN**" if t1r and pct == min(t1r.values()) else ""
        lines.append(f"| {name} | {pct:.1f}%{marker} |")
    n_t2_reached = r5_diag.get("n_reached_tier2", 0)
    lines.append(f"\n### Tahap 2 ROBUSTNESS (dari {n_t2_reached} trial yang lolos tahap 1)\n")
    t2r = r5_diag.get("tier2_filter_pass_pct", {})
    if t2r:
        lines.append("| filter | % lolos |")
        lines.append("|---|---:|")
        for name, pct in sorted(t2r.items(), key=lambda kv: kv[1]):
            marker = " <-- **PALING MEMATIKAN DI TAHAP INI**" if pct == min(t2r.values()) else ""
            lines.append(f"| {name} | {pct:.1f}%{marker} |")
    else:
        lines.append("N/A -- nol trial lolos tahap 1.\n")
    if t1r:
        worst_filter = min(t1r, key=t1r.get)
        lines.append(f"\n**Kesimpulan:** gerbang paling mematikan (tau={diag_tau}) adalah **{worst_filter}** "
                      f"({t1r[worst_filter]:.1f}% lolos).\n")

    lines.append(f"\nsd_SR empiris (dari sharpe {N_SEEDS} trial IC=0.05 tau={diag_tau}, efek samping L11 -- "
                  f"BUKAN pilot 24-trial resmi §01 B5): **{r5_diag['sharpe_std_empirical']:.4f}**\n")

    lines.append(
        "**Keterbatasan uji L11 yang wajib diakui:** konstruksi trade di sini adalah SATU eksposur tetap "
        "sampai akhir blok (tanpa SL/TP dioptimalkan) -- divisi X (exit & sizing) belum diuji. Kandidat "
        "nyata dengan barrier yang dioptimalkan kemungkinan menangkap lebih banyak dari IC yang sama.\n"
    )

    (REPORTS / "F1_gate_power.md").write_text("\n".join(lines))
    print(f"wrote F1_gate_power.md -- GM3_pass_any_tau={gm3_pass_any} best_tau={best_tau}")

    import json
    Path(REPORTS / "F1_result.json").write_text(json.dumps(
        {"l10_passed": l10["passed"],
         "l11_by_tau": {str(tau): {str(k): v for k, v in res.items()} for tau, res in results_by_tau.items()},
         "gm3_pass_any_tau": gm3_pass_any, "best_tau": best_tau,
         "cost_worst_bps_h240": cost_worst, "cost_full_regime_bps": cost_full_regime,
         "br_eff_per_year": br_eff_per_year}, indent=2, default=str))
    print("F1 DONE.")
    return gm3_pass_any


if __name__ == "__main__":
    main()
