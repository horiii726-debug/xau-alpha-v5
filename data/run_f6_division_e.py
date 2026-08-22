#!/usr/bin/env python3
"""F6 -- Divisi E (Entry/Arah) + Adendum Z.

Setiap formula E menghasilkan sinyal +1/-1/0 per bar (causal). Entry
diambil di SETIAP bar sinyal != 0 (bukan entry acak -- ini yang
membedakan F6 dari F2/F5), dieksekusi di bar t+1 (L9), exit pakai
barrier X01 baseline (k_sl=1.5,k_tp=2.5, H60) karena F5 tidak menemukan
exit yang lebih baik dari baseline. gate_checklist penuh, threshold
only per §O5 (TIDAK ADA argmax/sort di pemilihan -- laporan urut
expectancy HANYA untuk keterbacaan, bukan untuk memilih juara).

Adendum Z (Z01-Z03): TIDAK BISA diuji di sini. Z02/Z03 butuh data
cross-sectional panel (>1 instrumen) yang tidak tersedia -- XAUUSD saja.
Z01 butuh sinyal E yang SUDAH lolos F6 sebagai input -- tidak ada yang
lolos untuk digerbangi (lihat hasil di bawah). Dilaporkan sebagai gap,
bukan dilewati diam-diam.
"""
import sys
sys.path.insert(0, "/workspace")

import numpy as np
import pandas as pd
from pathlib import Path

from src.labeling.triple_barrier import triple_barrier_labels, parkinson_sigma
from src.formulas import pilot_f2b as pf
from src.formulas import division_e as de
from src.validation.gate_checklist import evaluate_candidate, apply_batch_checks
from run_f4_estimation import load_m1_full

REPORTS_DIR = Path("/workspace/reports")
COST_BPS_WORST = 3.0
MAX_HOLD_BARS = 60
SIGMA_WINDOW = 96
BARS_PER_YEAR = 365 * 24 * 60
K_SL, K_TP = 1.5, 2.5  # baseline barrier, F5 found no better exit


def signal_to_trades(signal, open_, high, low, mid, sigma, n, max_sample=20000):
    sig_bars = np.where(signal[:-1] != 0)[0]  # exclude last bar (no t+1 to execute)
    sig_bars = sig_bars[(sig_bars > SIGMA_WINDOW) & (sig_bars < n - MAX_HOLD_BARS - 2)]
    if len(sig_bars) > max_sample:
        rng = np.random.default_rng(0)
        sig_bars = rng.choice(sig_bars, size=max_sample, replace=False)
        sig_bars.sort()
    if len(sig_bars) == 0:
        return None, None, None
    entry_bars = sig_bars + 1  # L9: execute at NEXT bar's open
    directions = signal[sig_bars].astype(np.int64)
    res = triple_barrier_labels(open_, high, low, mid, entry_bars, directions, sigma, K_SL, K_TP, MAX_HOLD_BARS)
    valid = res.outcome != 0
    return res.ret[valid], res.bars_held[valid], entry_bars[valid]


def main():
    print("Memuat data...")
    m1 = load_m1_full("XAUUSD")
    n_total = len(m1)
    screen = m1.iloc[: int(n_total * 0.20)].reset_index(drop=True)

    mid = screen["mid_close"].values
    high = screen["ask_high"].values
    low = screen["bid_low"].values
    open_ = screen["bid_open"].values
    prev_close = np.concatenate([[mid[0]], mid[:-1]])
    spread_bps = screen["spread_bps"].values
    sigma = parkinson_sigma(high, low, window=SIGMA_WINDOW)
    sigma_bps = sigma * 1e4
    n = len(mid)
    bar_returns = np.diff(np.log(mid), prepend=np.log(mid[0]))

    all_evals = []

    def run_and_eval(cand_name, signal):
        trade_returns, holding_bars, entry_bars_used = signal_to_trades(signal, open_, high, low, mid, sigma, n)
        if trade_returns is None or len(trade_returns) < 30:
            print(f"  {cand_name}: TERLALU SEDIKIT TRADE, dilewati")
            return None
        ev = evaluate_candidate(
            name=cand_name, trade_returns=trade_returns, entry_bars=entry_bars_used, holding_bars=holding_bars,
            mid=mid, n_bars_total=n, bars_per_year=BARS_PER_YEAR, cost_bps_worst=COST_BPS_WORST,
            spread_bps=spread_bps, sigma_bps=sigma_bps, signal_for_mc1=signal[:-1].astype(float),
            bar_returns_for_mc1=bar_returns, rng=np.random.default_rng(hash(cand_name) % (2**31)),
        )
        all_evals.append(ev)
        print(f"  {cand_name}: n={ev.n_trades} exp={ev.expectancy_net_bps:.2f}bps t={ev.t_stat_eff_n:.2f} checks={ev.n_checks_passed}/12(+batch)")
        return ev

    print("\n=== Formula pilot (7): E01,E10,E22,E30,E60,E70,E90 ===")
    for L in [6, 12, 24, 48]:
        run_and_eval(f"E01_MOMENTUM_L{L}", pf.e01_intraday_momentum(mid, L))
    for q in [2, 4, 8, 16]:
        run_and_eval(f"E10_VARIANCE_RATIO_q{q}", pf.e10_variance_ratio_lm(mid, q, window=200))
    for window in [96, 288]:
        for poly in [1, 2]:
            run_and_eval(f"E22_DFA_w{window}_p{poly}", pf.e22_dfa_alpha(mid, window, poly))
    for window in [48, 96, 288]:
        run_and_eval(f"E30_ENTROPY_w{window}", pf.e30_shannon_entropy_sign(mid, window, m=3))
    for h_mean, h_vol in [(6, 24), (12, 48)]:
        run_and_eval(f"E60_DRIFT_BURST_hm{h_mean}_hv{h_vol}", pf.e60_drift_burst_tstat(mid, h_mean, h_vol))
    for window in [24, 48, 96]:
        run_and_eval(f"E70_MANN_KENDALL_w{window}", pf.e70_mann_kendall(mid, window))
    for k_mult, h_mult in [(0.5, 4.0), (1.0, 6.0)]:
        run_and_eval(f"E90_CUSUM_k{k_mult}_h{h_mult}", pf.e90_cusum_changepoint(mid, k_mult, h_mult, window=96))

    print("\n=== Formula tambahan (12) ===")
    for L in [6, 12, 24]:
        for theta in [0.5, 1.0]:
            run_and_eval(f"E02_VOLSCALED_MOM_L{L}_t{theta}", de.e02_vol_scaled_momentum(mid, sigma, L, theta))
    for L in [3, 6, 12]:
        for theta in [1.5, 2.0]:
            run_and_eval(f"E03_REVERSAL_L{L}_t{theta}", de.e03_short_horizon_reversal(mid, sigma, L, theta))
    # CATATAN: E04 aslinya soal gap "setelah jeda pasar" (weekend/libur), bukan transisi bar-ke-bar.
    # Di M1 tanpa penanda sesi eksplisit, prev_close di sini cuma bar M1 sebelumnya -- BUKAN gap sesi
    # sungguhan. Hasilnya (t-stat ekstrem, lihat laporan) kemungkinan artefak varians nyaris-nol dari
    # "gap" M1-ke-M1 yang memang nyaris tidak ada, bukan temuan asli. Diuji & dilaporkan APA ADANYA
    # dengan caveat ini, bukan disembunyikan atau diam-diam diperbaiki tanpa transparansi.
    for theta in [0.5, 1.0, 1.5]:
        run_and_eval(f"E04_GAP_CONT_t{theta}_CAVEAT_bukan_gap_sesi_asli", de.e04_session_gap_continuation(open_, prev_close, sigma, theta))
    for q in [2, 4, 8]:
        run_and_eval(f"E11_VR_WRIGHT_q{q}", de.e11_variance_ratio_wright(mid, q, window=200))
    for window in [288, 576]:
        run_and_eval(f"E20_HURST_w{window}", de.e20_hurst_rs(mid, window))
    for window in [96, 288]:
        run_and_eval(f"E50_FFT_PERIOD_w{window}", de.e50_fft_dominant_period(mid, window))
    for window in [96, 288]:
        run_and_eval(f"E54_SPECTRAL_ENTROPY_w{window}", de.e54_spectral_entropy(mid, window))
    for window in [48, 96, 288]:
        run_and_eval(f"E64_REALIZED_SKEW_w{window}", de.e64_realized_skewness_signal(mid, window))
    for window in [24, 48, 96]:
        run_and_eval(f"E71_COX_STUART_w{window}", de.e71_cox_stuart(mid, window))
    for window in [24, 48, 96]:
        run_and_eval(f"E73_RUNS_TEST_w{window}", de.e73_runs_test(mid, window))
    for tau in [0.25, 0.5, 0.75]:
        run_and_eval(f"E80_QUANTREG_tau{tau}", de.e80_quantile_regression_slope(mid, window=48, tau=tau))
    run_and_eval("E81_HUBER_SLOPE", de.e81_huber_slope(mid, window=48))

    print(f"\n{len(all_evals)} kandidat E dievaluasi. Menjalankan batch check...")
    apply_batch_checks(all_evals, n_trials_cumulative=len(all_evals) + 34 + 35, trial_sharpe_std=0.3)

    lines = ["# F6 -- Divisi E (Entry/Arah) + Adendum Z\n"]
    lines.append(
        f"XAUUSD, exit baseline X01 (k_sl=1.5,k_tp=2.5, H60 -- F5 tidak menemukan exit lebih baik). "
        f"Entry di SETIAP bar sinyal formula != 0 (bukan acak), eksekusi t+1 (L9). SINGLE_ASSET_ONLY, "
        f"UNDERPOWERED_PANEL. {len(all_evals)} kombinasi diuji dari registry 19 formula (7 pilot + 12 "
        f"tambahan) -- BUKAN 56 penuh, lihat catatan cakupan.\n"
    )
    lines.append("## Adendum Z -- TIDAK BISA diuji\n")
    lines.append(
        "Z02/Z03 (cross-sectional) butuh >1 instrumen -- panel cuma XAUUSD. Z01 butuh sinyal E yang "
        "SUDAH lolos F6 sebagai input untuk digerbangi -- kalau nol E yang lolos (lihat di bawah), "
        "Z01 tidak punya apapun untuk digerbangi. Dilaporkan sebagai gap nyata, bukan dilewati diam-diam.\n"
    )

    passing = [e for e in all_evals if e.n_checks_passed >= 13]
    lines.append(f"## Ringkasan: {len(all_evals)} kandidat diuji, {len(passing)} lolos >=13/15 centang\n")
    lines.append("| Kandidat | N trade | Expectancy net bps | t-stat | Checks (dari 15) | DSR | BH-FDR | PBO |")
    lines.append("|---|---:|---:|---:|---:|---:|---|---:|")
    for e in sorted(all_evals, key=lambda x: -x.expectancy_net_bps):
        lines.append(
            f"| {e.name} | {e.n_trades} | {e.expectancy_net_bps:.2f} | {e.t_stat_eff_n:.2f} | "
            f"{e.n_checks_passed}/{e.n_checks_total} | {e.dsr:.3f} | {e.bh_fdr_pass} | {e.pbo:.3f} |"
        )

    lines.append(f"\n## Vonis F6\n")
    if passing:
        best = max(passing, key=lambda x: x.n_checks_passed)
        lines.append(f"**Ada kandidat yang lolos ambang tinggi.** Terbaik: {best.name} ({best.n_checks_passed}/15, {best.expectancy_net_bps:.2f} bps).")
    else:
        lines.append("**NOL kandidat lolos >=13/15 checks.** Dicatat apa adanya -- lanjut ke F7 (divisi independen).")
        if all_evals:
            best_by_exp = max(all_evals, key=lambda x: x.expectancy_net_bps)
            lines.append(f"\nKandidat dengan expectancy tertinggi (belum lolos ambang penuh): {best_by_exp.name}, {best_by_exp.expectancy_net_bps:.2f} bps, {best_by_exp.n_checks_passed}/15 checks.")

    lines.append(
        f"\n## Catatan cakupan (jujur)\n\n19/56 formula E diuji (34 varian), plus Adendum Z 0/3 "
        f"(gap data, lihat atas). Formula yang TIDAK diuji: E05-E09 (tidak ada di registry asli -- "
        f"penomoran memang meloncat), E12, E21, E23-E29, E31-E36, E40-E45 (nonlinear/chaos, tier-3 "
        f"mahal), E51-E53/E55, E61-E63/E65, E72/E74/E82/E83 (butuh implementasi Theil-Sen/Siegel/RANSAC "
        f"robust slope tambahan), E91-E97 (changepoint/dependency lanjutan, sebagian tier-3). Ini "
        f"eksplorasi breadth-first pada anggaran waktu terbatas, BUKAN klaim registry penuh teruji."
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "F6_screening.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0 if passing else 1


if __name__ == "__main__":
    sys.exit(main())
