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
from src.formulas import division_x_stopping as xst
from src.validation.gate_checklist import evaluate_candidate, apply_batch_checks
from run_f4_estimation import load_m1_full

REPORTS_DIR = Path("/workspace/reports")
COST_BPS_WORST = 3.0
MAX_HOLD_BARS = 60
SIGMA_WINDOW = 96
BARS_PER_YEAR = 365 * 24 * 60
K_SL, K_TP = 1.5, 2.5  # baseline barrier, F5 found no better exit

# 5 exit terbaik dari F5 (net expectancy_bps tertinggi di ledger_trials.csv,
# tipe exit BERBEDA-BEDA -- bukan sizing/duplikat), dipakai utk entry x exit combo.
TOP5_F5_EXITS = [
    ("X10_POT_GPD_ksl4.76_ktp2.0", "barrier", {"k_sl": 4.76, "k_tp": 2.0}),
    ("X21_SHIRYAEV_ROBERTS_A10", "stopping", {"fn": "sr", "A": 10}),
    ("X21_SHIRYAEV_ROBERTS_A30", "stopping", {"fn": "sr", "A": 30}),
    ("X22_CUSUM_h3", "stopping", {"fn": "cusum", "h": 3}),
    ("X22_CUSUM_h5", "stopping", {"fn": "cusum", "h": 5}),
]


def get_signal_entries(signal, n, max_sample=20000):
    """Extract raw (entry_bar, direction) pairs from a signal, independent
    of exit choice -- so the SAME entry set can be re-tested against
    different exits."""
    sig_bars = np.where(signal[:-1] != 0)[0]
    sig_bars = sig_bars[(sig_bars > SIGMA_WINDOW) & (sig_bars < n - MAX_HOLD_BARS - 2)]
    if len(sig_bars) > max_sample:
        rng = np.random.default_rng(0)
        sig_bars = rng.choice(sig_bars, size=max_sample, replace=False)
        sig_bars.sort()
    if len(sig_bars) == 0:
        return None, None
    entry_bars = sig_bars + 1  # L9
    directions = signal[sig_bars].astype(np.int64)
    return entry_bars, directions


def apply_exit(exit_name, exit_type, params, entry_bars, directions, open_, high, low, mid, sigma, n):
    if exit_type == "barrier":
        res = triple_barrier_labels(open_, high, low, mid, entry_bars, directions, sigma, params["k_sl"], params["k_tp"], MAX_HOLD_BARS)
        valid = res.outcome != 0
        return res.ret[valid], res.bars_held[valid], entry_bars[valid]

    sigma_median = float(np.nanmedian(sigma))
    mu1 = 1.5 * sigma_median
    rets, holds, used = [], [], []
    for e, dr in zip(entry_bars, directions):
        path = mid[e : min(e + MAX_HOLD_BARS, n)]
        if len(path) < 2:
            continue
        r_path = np.diff(np.log(path)) * dr
        if params["fn"] == "sr":
            t_exit = xst.x21_shiryaev_roberts_exit(r_path, mu1, sigma_median, params["A"])
        else:
            t_exit = xst.x22_quickest_detection_exit(r_path, mu1, sigma_median, params["h"])
        t_exit = t_exit if t_exit >= 0 else len(path) - 1
        ret = (path[min(t_exit + 1, len(path) - 1)] - path[0]) / path[0] * dr
        rets.append(ret); holds.append(t_exit + 1); used.append(e)
    return np.array(rets), np.array(holds), np.array(used)


def build_all_base_signals(mid, high, low, open_, prev_close, sigma, verbose=False):
    """All 19-formula/56-variant base E signal grid, factored out so F7's
    meta-labeling (M11) can reuse the exact same signal a name refers to
    instead of re-deriving parameters from a string. A GENERATOR (not a
    dict-building function) so callers see progress incrementally instead
    of a silent multi-minute wait -- several of these formulas are naive
    per-bar Python loops that genuinely take tens of seconds to minutes
    EACH at the full ~451k-bar screen scale (not a bug, just real cost;
    verified via isolated benchmarking, not a stuck/hung process)."""
    import time as _time

    def _emit(name, fn):
        t0 = _time.time()
        sig = fn()
        if verbose:
            print(f"    [sinyal siap] {name}: {_time.time() - t0:.1f}s")
        return name, sig

    for L in [6, 12, 24, 48]:
        yield _emit(f"E01_MOMENTUM_L{L}", lambda L=L: pf.e01_intraday_momentum(mid, L))
    for q in [2, 4, 8, 16]:
        yield _emit(f"E10_VARIANCE_RATIO_q{q}", lambda q=q: pf.e10_variance_ratio_lm(mid, q, window=200))
    for window in [96, 288]:
        for poly in [1, 2]:
            yield _emit(f"E22_DFA_w{window}_p{poly}", lambda w=window, p=poly: pf.e22_dfa_alpha(mid, w, p))
    for window in [48, 96, 288]:
        yield _emit(f"E30_ENTROPY_w{window}", lambda w=window: pf.e30_shannon_entropy_sign(mid, w, m=3))
    for h_mean, h_vol in [(6, 24), (12, 48)]:
        yield _emit(f"E60_DRIFT_BURST_hm{h_mean}_hv{h_vol}", lambda hm=h_mean, hv=h_vol: pf.e60_drift_burst_tstat(mid, hm, hv))
    for window in [24, 48, 96]:
        yield _emit(f"E70_MANN_KENDALL_w{window}", lambda w=window: pf.e70_mann_kendall(mid, w))
    for k_mult, h_mult in [(0.5, 4.0), (1.0, 6.0)]:
        yield _emit(f"E90_CUSUM_k{k_mult}_h{h_mult}", lambda k=k_mult, h=h_mult: pf.e90_cusum_changepoint(mid, k, h, window=96))
    for L in [6, 12, 24]:
        for theta in [0.5, 1.0]:
            yield _emit(f"E02_VOLSCALED_MOM_L{L}_t{theta}", lambda L=L, th=theta: de.e02_vol_scaled_momentum(mid, sigma, L, th))
    for L in [3, 6, 12]:
        for theta in [1.5, 2.0]:
            yield _emit(f"E03_REVERSAL_L{L}_t{theta}", lambda L=L, th=theta: de.e03_short_horizon_reversal(mid, sigma, L, th))
    # CATATAN: E04 aslinya soal gap "setelah jeda pasar" (weekend/libur), bukan transisi bar-ke-bar.
    # Di M1 tanpa penanda sesi eksplisit, prev_close di sini cuma bar M1 sebelumnya -- BUKAN gap sesi
    # sungguhan. Diuji & dilaporkan APA ADANYA dengan caveat ini di nama sinyal, bukan disembunyikan.
    for theta in [0.5, 1.0, 1.5]:
        yield _emit(f"E04_GAP_CONT_t{theta}_CAVEAT_bukan_gap_sesi_asli", lambda th=theta: de.e04_session_gap_continuation(open_, prev_close, sigma, th))
    for q in [2, 4, 8]:
        yield _emit(f"E11_VR_WRIGHT_q{q}", lambda q=q: de.e11_variance_ratio_wright(mid, q, window=200))
    for window in [288, 576]:
        yield _emit(f"E20_HURST_w{window}", lambda w=window: de.e20_hurst_rs(mid, w))
    for window in [96, 288]:
        yield _emit(f"E50_FFT_PERIOD_w{window}", lambda w=window: de.e50_fft_dominant_period(mid, w))
    for window in [96, 288]:
        yield _emit(f"E54_SPECTRAL_ENTROPY_w{window}", lambda w=window: de.e54_spectral_entropy(mid, w))
    for window in [48, 96, 288]:
        yield _emit(f"E64_REALIZED_SKEW_w{window}", lambda w=window: de.e64_realized_skewness_signal(mid, w))
    for window in [24, 48, 96]:
        yield _emit(f"E71_COX_STUART_w{window}", lambda w=window: de.e71_cox_stuart(mid, w))
    for window in [24, 48, 96]:
        yield _emit(f"E73_RUNS_TEST_w{window}", lambda w=window: de.e73_runs_test(mid, w))
    for tau in [0.25, 0.5, 0.75]:
        yield _emit(f"E80_QUANTREG_tau{tau}", lambda t=tau: de.e80_quantile_regression_slope(mid, window=48, tau=t))
    yield _emit("E81_HUBER_SLOPE", lambda: de.e81_huber_slope(mid, window=48))


def signal_to_trades(signal, open_, high, low, mid, sigma, n, max_sample=20000):
    entry_bars, directions = get_signal_entries(signal, n, max_sample)
    if entry_bars is None:
        return None, None, None
    return apply_exit("X01_baseline", "barrier", {"k_sl": K_SL, "k_tp": K_TP}, entry_bars, directions, open_, high, low, mid, sigma, n)


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
    signal_by_name = {}

    def run_and_eval(cand_name, signal):
        signal_by_name[cand_name] = signal
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
        print(f"  {cand_name}: n={ev.n_trades} gross={ev.expectancy_gross_bps:.2f}bps net={ev.expectancy_net_bps:.2f}bps t={ev.t_stat_eff_n:.2f} checks={ev.n_checks_passed}/12(+batch)")
        return ev

    print("\n=== 19 formula E (7 pilot + 12 tambahan), 56 varian ===")
    for name, signal in build_all_base_signals(mid, high, low, open_, prev_close, sigma, verbose=True):
        run_and_eval(name, signal)

    n_base_evals = len(all_evals)
    positive_gross = [e for e in all_evals if e.expectancy_gross_bps > 0]
    print(f"\n{len(all_evals)} sinyal dasar dievaluasi (exit X01 baseline). "
          f"{len(positive_gross)} punya expectancy KOTOR positif -> diuji ulang dengan 5 exit terbaik F5.")

    combo_evals = []
    for base_ev in positive_gross:
        signal = signal_by_name[base_ev.name]
        entry_bars, directions = get_signal_entries(signal, n)
        if entry_bars is None:
            continue
        for exit_name, exit_type, params in TOP5_F5_EXITS:
            combo_name = f"{base_ev.name}_x_{exit_name}"
            trade_returns, holding_bars, entry_bars_used = apply_exit(
                exit_name, exit_type, params, entry_bars, directions, open_, high, low, mid, sigma, n
            )
            if trade_returns is None or len(trade_returns) < 30:
                continue
            ev = evaluate_candidate(
                name=combo_name, trade_returns=trade_returns, entry_bars=entry_bars_used, holding_bars=holding_bars,
                mid=mid, n_bars_total=n, bars_per_year=BARS_PER_YEAR, cost_bps_worst=COST_BPS_WORST,
                spread_bps=spread_bps, sigma_bps=sigma_bps, signal_for_mc1=signal[:-1].astype(float),
                bar_returns_for_mc1=bar_returns, rng=np.random.default_rng(hash(combo_name) % (2**31)),
            )
            combo_evals.append(ev)
            print(f"  {combo_name}: n={ev.n_trades} gross={ev.expectancy_gross_bps:.2f}bps net={ev.expectancy_net_bps:.2f}bps t={ev.t_stat_eff_n:.2f} checks={ev.n_checks_passed}/12(+batch)")

    all_evals.extend(combo_evals)
    print(f"\n{len(all_evals)} kandidat E total (termasuk {len(combo_evals)} kombinasi entry x exit). Menjalankan batch check...")
    apply_batch_checks(all_evals, n_trials_cumulative=len(all_evals) + 34 + 35, trial_sharpe_std=0.3)

    lines = ["# F6 -- Divisi E (Entry/Arah) + Adendum Z -- RUN PENUH\n"]
    lines.append(
        f"XAUUSD, partisi SCREEN penuh (~451.008 bar M1, ~313 hari). Sinyal dasar: exit X01 baseline "
        f"(k_sl=1.5,k_tp=2.5, H60). Sinyal dengan expectancy KOTOR positif diuji ulang dengan 5 exit "
        f"terbaik dari F5 (entry x exit combo). Entry di SETIAP bar sinyal formula != 0 (bukan acak), "
        f"eksekusi t+1 (L9). SINGLE_ASSET_ONLY, UNDERPOWERED_PANEL. {n_base_evals} sinyal dasar dari "
        f"19/56 formula (7 pilot + 12 tambahan) + {len(combo_evals)} kombinasi entry x exit = "
        f"{len(all_evals)} baris ledger total dari fase ini.\n"
    )
    lines.append("## Adendum Z -- TIDAK BISA diuji\n")
    lines.append(
        "Z02/Z03 (cross-sectional) butuh >1 instrumen -- panel cuma XAUUSD+sebagian XAGUSD. Z01 butuh "
        "sinyal E yang SUDAH lolos F6 sebagai input untuk digerbangi -- kalau nol E yang lolos (lihat "
        "di bawah), Z01 tidak punya apapun untuk digerbangi. Dilaporkan sebagai gap nyata.\n"
    )

    # --- Jawaban 4 pertanyaan spesifik ---
    lines.append("## Empat pertanyaan Anda\n")
    lines.append(f"**1. Berapa sinyal expectancy KOTORNYA positif?** {len(positive_gross)} dari {n_base_evals} sinyal dasar "
                 f"(sebelum kombinasi exit).\n")
    if positive_gross:
        lines.append("| Sinyal | Expectancy kotor (bps) | N trade |")
        lines.append("|---|---:|---:|")
        for e in sorted(positive_gross, key=lambda x: -x.expectancy_gross_bps):
            lines.append(f"| {e.name} | {e.expectancy_gross_bps:.3f} | {e.n_trades} |")
        lines.append("")

    lines.append("**2. Berapa bps biaya harus turun supaya bersih positif?**\n")
    all_candidates_sorted = sorted(all_evals, key=lambda x: -x.expectancy_net_bps)
    best_overall = all_candidates_sorted[0] if all_candidates_sorted else None
    if best_overall and best_overall.expectancy_gross_bps > 0:
        drop_needed = COST_BPS_WORST - best_overall.breakeven_cost_bps
        lines.append(
            f"Kandidat terbaik keseluruhan ({best_overall.name}): expectancy kotor "
            f"{best_overall.expectancy_gross_bps:.3f} bps, breakeven cost = {best_overall.breakeven_cost_bps:.3f} bps. "
            f"Biaya saat ini {COST_BPS_WORST} bps proxy -> **perlu turun {drop_needed:.3f} bps** ({drop_needed/COST_BPS_WORST*100:.0f}% "
            f"dari proxy) supaya net tepat impas, lebih lagi untuk net positif sungguhan."
        )
    elif best_overall:
        lines.append(
            f"**Tidak ada kandidat dengan expectancy kotor positif sama sekali** (terbaik: {best_overall.name}, "
            f"kotor {best_overall.expectancy_gross_bps:.3f} bps). Penurunan biaya berapa pun TIDAK AKAN membuatnya "
            f"positif -- masalahnya bukan di biaya, sinyalnya sendiri sudah kalah sebelum biaya dihitung."
        )
    lines.append("")

    lines.append("**3. Sinyal mana yang paling dekat lolos, kurang di centang mana?**\n")
    if all_evals:
        closest = max(all_evals, key=lambda x: x.n_checks_passed)
        checks_detail = {
            "expectancy>0": closest.expectancy_net_bps > 0, "t_stat>=3.0": closest.t_stat_eff_n >= 3.0,
            "beat_all_nulls": closest.beats_all_nulls, "cpcv>=80%": closest.cpcv_path_positive_pct >= 80,
            "bootstrap_ci95": closest.bootstrap_ci95_excludes_zero, "mc1>=p95": closest.mc1_percentile >= 95,
            "walkforward>=80%": closest.walkforward_sign_consistency_pct >= 80, "seed_stable": closest.seed_stable,
            "last_third_sig": closest.last_third_significant, "trades/yr>=300": closest.trades_per_year >= 300,
            "mc3": closest.mc3_pass, "mc5": closest.mc5_pass, "bh_fdr": closest.bh_fdr_pass,
            "dsr>=0.95": closest.dsr_pass, "pbo<=0.50": closest.pbo_pass,
        }
        missing = [k for k, v in checks_detail.items() if not v]
        passed_list = [k for k, v in checks_detail.items() if v]
        lines.append(f"**{closest.name}** -- {closest.n_checks_passed}/{closest.n_checks_total} centang.")
        lines.append(f"Lolos: {', '.join(passed_list) if passed_list else '(tidak ada)'}")
        lines.append(f"Kurang di: {', '.join(missing) if missing else '(tidak ada -- lolos semua)'}\n")

    lines.append("**4. t-stat tertinggi yang tercapai?**\n")
    if all_evals:
        best_t = max(all_evals, key=lambda x: x.t_stat_eff_n)
        t_val = best_t.t_stat_eff_n
        if t_val < 0:
            interp = "NEGATIF -- arah sinyal salah/tidak ada edge sama sekali di sisi ini, bukan soal sampel kurang."
        elif t_val < 2.0:
            interp = "sinyal LEMAH -- bahkan dengan sampel besar pun kemungkinan tidak akan cukup, ini masalah SINYAL, bukan masalah data."
        elif t_val < 3.0:
            interp = "sinyal ADA tapi SAMPEL KURANG -- t-stat mendekati ambang 3.0, perbesar panel/riwayat data bisa jadi cukup untuk menyeberang ambang, ini masalah DATA bukan masalah sinyal."
        else:
            interp = "SUDAH DI ATAS ambang 3.0 -- seharusnya lolos centang t-stat, cek centang lain yang menahannya."
        lines.append(f"**t = {t_val:.3f}** ({best_t.name}). Interpretasi: {interp}")
    lines.append("")

    passing = [e for e in all_evals if e.n_checks_passed >= 13]
    lines.append(f"## Ringkasan lengkap: {len(all_evals)} kandidat diuji, {len(passing)} lolos >=13/15 centang\n")
    lines.append("| Kandidat | N trade | Gross bps | Net bps | Breakeven cost bps | t-stat | Checks (dari 15) | DSR | PBO |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for e in all_candidates_sorted:
        lines.append(
            f"| {e.name} | {e.n_trades} | {e.expectancy_gross_bps:.2f} | {e.expectancy_net_bps:.2f} | "
            f"{e.breakeven_cost_bps:.2f} | {e.t_stat_eff_n:.2f} | {e.n_checks_passed}/{e.n_checks_total} | "
            f"{e.dsr:.3f} | {e.pbo if e.pbo is not None else float('nan'):.3f} |"
        )

    lines.append(f"\n## Vonis F6\n")
    if passing:
        best = max(passing, key=lambda x: x.n_checks_passed)
        lines.append(f"**Ada kandidat yang lolos ambang tinggi.** Terbaik: {best.name} ({best.n_checks_passed}/15, {best.expectancy_net_bps:.2f} bps).")
    else:
        lines.append("**NOL kandidat lolos >=13/15 checks.** Dicatat apa adanya -- lanjut ke F7 (divisi independen).")

    lines.append(
        f"\n## Catatan cakupan (jujur)\n\n19/56 formula E diuji sebagai sinyal dasar ({n_base_evals} varian "
        f"berhasil dievaluasi, sisanya dilewati karena n_trade<30) + "
        f"{len(combo_evals)} kombinasi entry x exit dari sinyal berkotor-positif. Adendum Z 0/3 (gap data). "
        f"Formula yang TIDAK diuji: E12, E21, E23-E29, E31-E36, E40-E45 (nonlinear/chaos, tier-3 mahal), "
        f"E51-E53/E55, E61-E63/E65, E72/E74/E82/E83 (butuh Theil-Sen/Siegel/RANSAC robust slope), "
        f"E91-E97 (changepoint/dependency lanjutan, sebagian tier-3). Eksplorasi breadth-first, "
        f"BUKAN klaim registry penuh teruji."
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "F6_screening.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0 if passing else 1


if __name__ == "__main__":
    sys.exit(main())
