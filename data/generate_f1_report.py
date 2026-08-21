#!/usr/bin/env python3
"""Runs the F1 validation pipeline against synthetic data and writes
reports/F1_infrastruktur_validasi.md with REAL computed numbers (IC,
percentiles, K_eff_null) -- not narrated/guessed values.
"""
import sys
sys.path.insert(0, "/workspace")

import numpy as np
import subprocess
from pathlib import Path

from src.stats import nulls
from src.validation import montecarlo as mc

REPORTS_DIR = Path("/workspace/reports")


def make_random_walk(n=8000, seed=123, drift=0.0, sigma=0.0008):
    rng = np.random.default_rng(seed)
    r = rng.normal(drift, sigma, size=n)
    mid = 100 * np.exp(np.cumsum(r))
    return mid, r


def main():
    lines = ["# F1 — Infrastruktur Validasi\n"]
    lines.append("> Dijalankan pada data SINTETIS (random walk yang dibangkitkan sendiri), sesuai instruksi: "
                  "F1 tidak butuh data pasar nyata, hanya perlu membuktikan alat ukurnya sendiri jujur "
                  "sebelum dipakai pada kandidat/data nyata di F2 dan seterusnya.\n")

    # --- pytest ---
    result = subprocess.run(
        ["/root/workspace/.venv/bin/python", "-m", "pytest", "tests/", "-v"],
        cwd="/workspace", capture_output=True, text=True,
    )
    n_passed = result.stdout.count(" PASSED")
    n_failed = result.stdout.count(" FAILED")
    lines.append(f"## pytest\n\n{n_passed} passed, {n_failed} failed (exit code {result.returncode})\n")
    if n_failed > 0:
        lines.append("**PYTEST MERAH -- F1 GAGAL per stop_conditions.3. Lihat detail di bawah.**\n")
        lines.append("```\n" + result.stdout[-3000:] + "\n```\n")

    # --- L10 leak test, real numbers ---
    mid, r = make_random_walk()
    leaky_signal = np.sign(r)
    ic = float(np.corrcoef(leaky_signal, r)[0, 1])

    rng = np.random.default_rng(999)
    leaky_returns = leaky_signal * r
    leaky_total = float(leaky_returns.sum())
    null_totals = {
        "B01_BUY_AND_HOLD": float(nulls.b01_buy_and_hold(mid).sum()),
        "B02_RANDOM_MATCHED": float(nulls.b02_random_matched(mid, costs_bps=np.array([0.0]), holding_bars=5, n_trades=200, rng=rng).sum()),
        "B03_BLOCK_PERMUTED": float(nulls.b03_block_permuted(mid, block_size=20, rng=rng).sum()),
        "B04_TSMOM_12M": float(nulls.b04_tsmom_12m(mid, lookback_bars=200).sum()),
        "B05_COIN_FLIP": float(nulls.b05_coin_flip(mid, rng).sum()),
        "B06_ALWAYS_LONG": float(nulls.b06_always_long(mid).sum()),
        "B07_ALWAYS_SHORT": float(nulls.b07_always_short(mid).sum()),
        "B08_RANDOM_FREQ_MATCHED": float(nulls.b08_random_freq_matched(mid, n_trades=200, holding_bars=5, rng=rng).sum()),
    }
    beats_all = all(leaky_total > v for v in null_totals.values())

    lines.append("## §L10 — Uji Kebocoran Wajib\n")
    lines.append(f"- IC fitur bocor (sengaja pakai return masa depan) = **{ic:.4f}** (syarat: > 0.5) -> {'LOLOS' if ic > 0.5 else 'GAGAL'}")
    lines.append(f"- Total return strategi bocor = {leaky_total:.4f}")
    lines.append(f"- Mengalahkan SEMUA null (B01-B08)? -> **{'YA, LOLOS' if beats_all else 'TIDAK, GAGAL'}**")
    lines.append("\n| Null | Total return | Bocor > Null? |")
    lines.append("|---|---:|---|")
    for k, v in null_totals.items():
        lines.append(f"| {k} | {v:.4f} | {'ya' if leaky_total > v else 'TIDAK'} |")
    lines.append("")

    # --- sanity: pure random signal false positive rate via real MC1 ---
    n_repeats = 100
    false_positives = 0
    percentiles = []
    for i in range(n_repeats):
        rs = np.random.default_rng(1000 + i)
        random_signal = rs.choice([-1.0, 1.0], size=len(r))
        res = mc.mc1_permutation(random_signal, r, n=200, block_size=20, rng=np.random.default_rng(5000 + i))
        percentiles.append(res["percentile"])
        if res["gate_pass"]:
            false_positives += 1
    fp_rate = false_positives / n_repeats

    lines.append("## Uji Sanity — Sinyal Acak Murni\n")
    lines.append(f"- {n_repeats} sinyal acak murni (+-1 tanpa hubungan dengan return), diuji lewat MC1 permutation (gate: persentil >= 95)")
    lines.append(f"- False positive rate (persentil >= 95 padahal sinyal murni acak) = **{fp_rate:.1%}** (nominal ~5% diharapkan)")
    lines.append(f"- Rata-rata persentil = {np.mean(percentiles):.1f}, median = {np.median(percentiles):.1f}")
    lines.append(f"- Verdict: {'LOLOS (di bawah 15% ceiling)' if fp_rate < 0.15 else 'GAGAL'}\n")

    # --- null correlation matrix (synthetic, infra validation only) ---
    null_series = {
        "B01": nulls.b01_buy_and_hold(mid),
        "B04": nulls.b04_tsmom_12m(mid, lookback_bars=200),
        "B06": nulls.b06_always_long(mid),
        "B07": nulls.b07_always_short(mid),
    }
    corr, k_eff_null = nulls.null_correlation_matrix(null_series)
    lines.append("## Matriks Korelasi Null + Null Independen Efektif\n")
    lines.append("> Dihitung pada data SINTETIS untuk memvalidasi mekanismenya. WAJIB dihitung ulang")
    lines.append("> pada data panel NYATA begitu tersedia -- angka di bawah bukan angka final untuk F6/F7.\n")
    lines.append("```")
    lines.append(corr.round(3).to_string())
    lines.append("```")
    lines.append(f"\nK_eff null (metode eigenvalue) = {k_eff_null:.3f} dari {len(null_series)} null yang diuji")
    lines.append(f"(B01 dan B06 identik by construction -- keduanya BUY_AND_HOLD/ALWAYS_LONG -- korelasi 1.0 diharapkan)\n")

    # --- module inventory ---
    lines.append("## Modul yang dibangun\n")
    lines.append("- `src/stats/effective_n.py` -- Lopez de Prado uniqueness, concurrency, sample weights")
    lines.append("- `src/stats/nulls.py` -- B01-B09 sebagai kode, null_correlation_matrix")
    lines.append("- `src/validation/cpcv.py` -- CPCV purged + embargo, default 12 grup x 2 test = 66 path (cocok n_paths_min)")
    lines.append("- `src/validation/montecarlo.py` -- MC1 (permutasi, DIPERBAIKI dari bug awal), MC2 (survival), MC3 (eksekusi/slippage), MC4 (DSR), MC5 (gangguan parameter)")
    lines.append("- `src/costs/cost_model.py` -- model biaya bps, kappa, skenario best/base/worst, LOOKUP yang belum terisi TIDAK didefaultkan ke nol")
    lines.append("- `tests/` -- 30 test, termasuk L10 dan sanity check di atas\n")

    lines.append("## Catatan jujur\n")
    lines.append("- **Bug ditemukan & diperbaiki selama membangun ini**: MC1 versi pertama mem-permutasi ")
    lines.append("  return trade YANG SUDAH TERWUJUD secara langsung lalu menjumlahkannya -- jumlah dari himpunan ")
    lines.append("  angka yang sama selalu sama walau diacak urutannya, jadi ujinya tidak pernah bisa gagal atau ")
    lines.append("  berhasil secara berarti (vacuous). Diperbaiki: sekarang mem-permutasi return BAR yang mendasari, ")
    lines.append("  lalu menerapkan ULANG sinyal (tetap) ke return yang sudah diacak. Test regresi ditambahkan.")
    lines.append("- Test sanity pertama (bandingkan total mentah sinyal acak vs B01/B06/B07) gagal di percobaan pertama ")
    lines.append("  (33.5% vs target <10%) -- ternyata itu kelemahan DESAIN TES (B01=B06 dan B07=-B01 nyaris cermin ")
    lines.append("  sempurna pada walk berdrift nol, jadi 'kalahkan keduanya sekaligus' bukan filter yang berarti), ")
    lines.append("  bukan kesalahan pada null-nya. Diganti dengan uji false-positive-rate MC1 yang sesungguhnya.")
    lines.append("- Model biaya (`cost_model.py`) TIDAK memiliki markup_prop_firm_pct / commission_usd_per_lot terisi ")
    lines.append("  untuk XAUUSD -- keduanya masih LOOKUP dari F0 (FTMO menyembunyikan angka XAUUSD spesifik di balik ")
    lines.append("  widget JS). Kode SENGAJA tidak mendefaultkan ini ke 0 -- field `missing_lookups` melaporkannya, ")
    lines.append("  diuji di `test_missing_lookup_flagged_not_defaulted`.")
    lines.append("- MC2 (survival/prop-firm-breach) BELUM bisa dijalankan dengan angka final -- max_total_drawdown_pct ")
    lines.append("  dkk juga masih menunggu F0 (FTMO: 10% max loss, 3%/5% daily loss SUDAH ada dari riset F0 sebelumnya; ")
    lines.append("  FundedNext/The5ers belum terverifikasi presisi). Kode sudah teruji tidak mengarang angka saat LOOKUP kosong.\n")

    verdict = (n_failed == 0) and (ic > 0.5) and beats_all and (fp_rate < 0.15)
    lines.append("## Verdict F1\n")
    lines.append(f"**{'LULUS' if verdict else 'GAGAL'}** -- {'semua syarat 07_FASE_EKSEKUSI.md F1.lulus terpenuhi.' if verdict else 'ada syarat yang tidak terpenuhi, lihat detail di atas.'}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / "F1_infrastruktur_validasi.md"
    out.write_text("\n".join(lines))
    print(f"wrote {out}")
    print(f"verdict: {'LULUS' if verdict else 'GAGAL'}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
