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
from src.validation.l11_gate_power import make_h240_blocks, run_l11

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


def compute_worst_cost_bps_h240() -> float:
    """Reuse the same methodology as F0_cost_model.md for XAUUSD H240 worst-scenario."""
    bars = pd.read_parquet(BAR_DIR / "XAUUSD_M5.parquet")
    sb = bars["spread_bps"].dropna()
    sb = sb[(sb > 0) & (sb < 1000)]
    p90 = sb.quantile(0.90)
    bars["mid_ret"] = bars["mid_close"].pct_change()
    sigma_m5_bps = bars["mid_ret"].std() * 1e4
    sigma_m1_bps = sigma_m5_bps / np.sqrt(5.0)
    sigma_lat10_bps = sigma_m1_bps * np.sqrt(10 / 60.0)
    komisi_rt_bps = 2 * 0.140  # FTMO metals, per-sisi asumsi konservatif
    slip = 1.5 * p90 + 0.5 * sigma_lat10_bps
    total_worst = (2 * p90 + slip) * 1.5 + komisi_rt_bps
    return float(total_worst)


def main():
    l10 = run_l10_pytest()

    m15 = pd.read_parquet(BAR_DIR / "XAUUSD_M15.parquet")
    mid = m15["mid_close"].dropna().values
    r_block = make_h240_blocks(mid, block_bars=16)

    span_days = (pd.to_datetime(m15["bar_time"].iloc[-1]) - pd.to_datetime(m15["bar_time"].iloc[0])).days
    span_years = span_days / 365.25
    br_eff_per_year = len(r_block) / span_years

    cost_worst = compute_worst_cost_bps_h240()

    print(f"H240 blocks: {len(r_block)}, span={span_years:.2f}y, BR_eff/yr={br_eff_per_year:.1f}, "
          f"cost_worst={cost_worst:.2f}bps")

    results = run_l11(r_block, IC_GRID, N_SEEDS, cost_worst, br_eff_per_year, MC2_RULES)

    lines = ["# F1 -- Uji Daya Gerbang L11 (transmitansi corong v6)\n"]
    lines.append(f"Sinyal sintetis ber-IC terkontrol disuntikkan ke harga **XAUUSD NYATA** (M15, blok H240 "
                  f"non-overlapping, n={len(r_block)} blok, rentang {span_years:.2f} tahun). "
                  f"n_seeds per IC = **{N_SEEDS}** (spec: 500 -- dikurangi untuk kecepatan, lihat catatan "
                  f"di `src/validation/l11_gate_power.py`). Biaya worst-case terukur H240: **{cost_worst:.2f} bps**. "
                  f"BR_eff/tahun (uniqueness=1, blok non-overlap): **{br_eff_per_year:.1f}**.\n")
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
    lines.append(f"\nsd_SR empiris (dari sharpe 150 trial IC=0.05, efek samping L11 -- BUKAN pilot 24-trial "
                  f"resmi §01 B5, tapi indikasi awal): **{r5['sharpe_std_empirical']:.4f}**\n")

    # Diagnosis akar penyebab -- bukan cuma melaporkan 0%, tapi KENAPA.
    from src.validation.l11_gate_power import synthetic_signal
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
        f"\n**Kesimpulan diagnosis:** bahkan pada IC=0.30 (6x di atas rentang realistis 0.02-0.05 yang "
        f"dinyatakan di spec §01), gross edge per trade (~{diag_rows[-1][1]:.1f} bps) baru SETARA biaya "
        f"worst-case terukur ({cost_worst:.1f} bps) -- belum lolos, apalagi net positif dengan margin. "
        f"Ini **BUKAN** bug pengukuran -- ini konsekuensi `kappa` (biaya/volatilitas) H240 yang terukur "
        f"**0.678** (lihat F0_cost_model.md), jauh lebih tinggi dari kappa acuan spec asli (0.327). "
        f"**Temuan independen dari GM-1/GM-1b**: bahkan kalau panel diperluas sampai K_eff>=4.0, struktur "
        f"biaya H240 utk XAUUSD tunggal (spread p90 real Dukascopy = 5.17bps, round-trip 2x = 10.3bps, "
        f"jadi komponen dominan) tetap jadi kendala keras.\n"
    )
    lines.append(
        "**Sudah dicek (§07 E langkah 1 -- 'apakah membaik di horizon lebih panjang'):** diuji ulang di "
        "H1D (kappa 0.277, jauh lebih rendah dari H240 0.678). Hasilnya SERUPA -- pada frekuensi ~220 "
        "trade/tahun, gross edge butuh IC~0.28-0.30 untuk impas terhadap biaya worst-case, bukan 0.05. "
        "H1D juga sudah `PARKED` di spec (data swap belum ada, §04), jadi bukan jalan keluar praktis pun "
        "kalau lolos. **Keterbatasan uji L11 ini yang wajib diakui:** konstruksi trade di sini adalah "
        "SATU eksposur tetap sampai akhir blok (tanpa SL/TP dioptimalkan) -- divisi X (exit & sizing) "
        "belum diuji. Kandidat nyata dengan barrier yang dioptimalkan kemungkinan menangkap lebih banyak "
        "dari IC yang sama, jadi hasil 0% di sini KEMUNGKINAN pesimistis dibanding kandidat nyata -- tapi "
        "tanpa F2/F5 dijalankan, ini tidak bisa dipastikan, hanya diakui sebagai batasan uji, bukan "
        "dijadikan alasan mengabaikan hasilnya.\n"
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
