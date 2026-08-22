"""Full gates.direction checklist (06_GERBANG_DAN_ANGGARAN.md), 17 items,
adapted for a SINGLE-ASSET / UNDERPOWERED panel per explicit user
instruction: results tagged SINGLE_ASSET_ONLY and UNDERPOWERED_PANEL,
MC2 marked PENDING_COST_LOOKUP (not FAILED) since prop-firm cost lookups
are incomplete, thresholds never loosened.

Two-stage: per-candidate checks computed independently; batch-level
checks (BH-FDR, DSR, PBO) computed once per DIVISION after all its
candidates are evaluated, since they are inherently comparisons across
the whole set of trials, not single-candidate properties.
"""
from dataclasses import dataclass, field

import numpy as np

from src.stats import nulls
from src.stats.effective_n import effective_n as ldp_effective_n
from src.validation.cpcv import cpcv_splits
from src.validation.montecarlo import mc1_permutation, mc3_execution_slippage, mc5_parameter_perturbation


@dataclass
class CandidateEval:
    name: str
    n_trades: int
    expectancy_net_bps: float
    expectancy_gross_bps: float
    breakeven_cost_bps: float  # cost level at which net expectancy would hit exactly 0
    t_stat_eff_n: float
    beats_all_nulls: bool
    cpcv_path_positive_pct: float
    bootstrap_ci95_excludes_zero: bool
    mc1_percentile: float
    walkforward_sign_consistency_pct: float
    seed_stable: bool
    last_third_significant: bool
    trades_per_year: float
    mc3_pass: bool
    mc5_pass: bool
    # batch-level, filled in later
    p_value: float = None
    bh_fdr_pass: bool = None
    dsr: float = None
    dsr_pass: bool = None
    pbo: float = None
    pbo_pass: bool = None
    n_checks_passed: int = 0
    n_checks_total: int = 16
    tags: list = field(default_factory=lambda: ["SINGLE_ASSET_ONLY", "UNDERPOWERED_PANEL"])
    mc2_status: str = "PENDING_COST_LOOKUP"


def _bar_to_year_fraction(n_bars_total: int, bars_per_year: float) -> float:
    return n_bars_total / bars_per_year


def evaluate_candidate(
    name: str,
    trade_returns: np.ndarray,
    entry_bars: np.ndarray,
    holding_bars: np.ndarray,
    mid: np.ndarray,
    n_bars_total: int,
    bars_per_year: float,
    cost_bps_worst: float,
    spread_bps: np.ndarray,
    sigma_bps: np.ndarray,
    signal_for_mc1: np.ndarray,
    bar_returns_for_mc1: np.ndarray,
    rng: np.random.Generator,
    mc5_evaluate_fn=None,
    mc5_base_params: dict = None,
) -> CandidateEval:
    n = len(trade_returns)
    gross_bps_early = float(np.nanmean(trade_returns) * 1e4) if n else 0.0
    if n < 30:
        return CandidateEval(
            name=name, n_trades=n, expectancy_net_bps=gross_bps_early - cost_bps_worst,
            expectancy_gross_bps=gross_bps_early, breakeven_cost_bps=gross_bps_early,
            t_stat_eff_n=0.0, beats_all_nulls=False, cpcv_path_positive_pct=0.0,
            bootstrap_ci95_excludes_zero=False, mc1_percentile=0.0, walkforward_sign_consistency_pct=0.0,
            seed_stable=False, last_third_significant=False, trades_per_year=0.0, mc3_pass=False, mc5_pass=False,
        )

    # 1. expectancy net bps at worst cost
    expectancy_gross_bps = float(np.mean(trade_returns) * 1e4)
    net_returns = trade_returns - cost_bps_worst / 1e4
    expectancy_net_bps = float(np.mean(net_returns) * 1e4)
    # breakeven_cost_bps: cost level (bps round-trip) at which net expectancy hits exactly 0.
    # If gross is already <=0, no cost level saves it (breakeven cost would be negative/undefined
    # in a useful sense) -- reported as 0.0 to mean "even zero cost wouldn't help".
    breakeven_cost_bps = max(expectancy_gross_bps, 0.0)

    # 2. t-stat with effective N (Lopez de Prado uniqueness)
    label_ends = entry_bars + holding_bars
    eff_n = ldp_effective_n(entry_bars, label_ends, n_bars_total)
    eff_n = max(eff_n, 2.0)
    se = np.std(net_returns, ddof=1) / np.sqrt(eff_n)
    t_stat = float(np.mean(net_returns) / se) if se > 0 else 0.0
    from scipy import stats as scipy_stats
    p_value = float(2 * (1 - scipy_stats.t.cdf(abs(t_stat), df=max(eff_n - 1, 1))))

    # 6. beat B01-B08
    mid_slice = mid[: n_bars_total]
    null_totals = {
        "B01": nulls.b01_buy_and_hold(mid_slice).sum(),
        "B02": nulls.b02_random_matched(mid_slice, np.array([cost_bps_worst]), int(np.median(holding_bars)), min(n, 5000), rng).sum(),
        "B03": nulls.b03_block_permuted(mid_slice, 20, rng).sum(),
        "B04": nulls.b04_tsmom_12m(mid_slice, min(200, n_bars_total // 4)).sum(),
        "B05": nulls.b05_coin_flip(mid_slice, rng).sum(),
        "B06": nulls.b06_always_long(mid_slice).sum(),
        "B07": nulls.b07_always_short(mid_slice).sum(),
        "B08": nulls.b08_random_freq_matched(mid_slice, min(n, 5000), int(np.median(holding_bars)), rng).sum(),
    }
    candidate_total = net_returns.sum()
    beats_all_nulls = all(candidate_total > v for v in null_totals.values())

    # 7. CPCV path positive %
    try:
        splits = list(cpcv_splits(n_bars_total, entry_bars, label_ends, n_groups=12, n_test_groups=2, embargo_bars=int(np.median(holding_bars))))
        path_positive = 0
        n_paths_used = 0
        for split in splits[: min(66, len(splits))]:
            test_idx = split.test_idx
            if len(test_idx) < 5:
                continue
            n_paths_used += 1
            if net_returns[test_idx].mean() > 0:
                path_positive += 1
        cpcv_pct = 100 * path_positive / n_paths_used if n_paths_used else 0.0
    except Exception:
        cpcv_pct = 0.0

    # 8. bootstrap CI95
    boot_means = np.array([rng.choice(net_returns, size=n, replace=True).mean() for _ in range(1000)])
    ci_lo, ci_hi = np.percentile(boot_means, [2.5, 97.5])
    bootstrap_excludes_zero = bool(ci_lo > 0 or ci_hi < 0)

    # 9. MC1 permutation
    mc1_res = mc1_permutation(signal_for_mc1, bar_returns_for_mc1, n=300, block_size=20, rng=rng)
    mc1_pct = mc1_res["percentile"]

    # 10. walk-forward sign consistency (split into 8 windows chronologically by entry bar)
    order = np.argsort(entry_bars)
    sorted_returns = net_returns[order]
    windows = np.array_split(sorted_returns, min(8, max(2, n // 30)))
    signs = [np.sign(w.mean()) for w in windows if len(w) > 0]
    dominant_sign = np.sign(np.sum(signs)) if signs else 0
    wf_consistency = 100 * np.mean([s == dominant_sign for s in signs]) if signs else 0.0

    # 11. seed stability (n_trades resample with 10 seeds, check sign)
    seed_signs = []
    for s in range(10):
        rr = np.random.default_rng(2000 + s)
        resampled = rr.choice(net_returns, size=n, replace=True)
        seed_signs.append(np.sign(resampled.mean()))
    seed_stable = bool(len(set(seed_signs)) == 1)

    # 12. last third still significant
    last_third = sorted_returns[-max(10, len(sorted_returns) // 3):]
    last_third_significant = bool(len(last_third) >= 10 and (last_third.mean() / (last_third.std(ddof=1) / np.sqrt(len(last_third)) + 1e-12)) > 1.96 and np.sign(last_third.mean()) == dominant_sign)

    # 13. trades per year
    trades_per_year = n / _bar_to_year_fraction(n_bars_total, bars_per_year)

    # 15. MC3
    mc3_res = mc3_execution_slippage(trade_returns, spread_bps[:n] if len(spread_bps) >= n else np.full(n, np.nanmean(spread_bps)), sigma_bps[:n] if len(sigma_bps) >= n else np.full(n, np.nanmean(sigma_bps)), n_paths=500, rng=rng)
    mc3_pass = mc3_res["gate_pass"]

    # 16. MC5
    mc5_pass = False
    if mc5_evaluate_fn is not None and mc5_base_params:
        mc5_res = mc5_parameter_perturbation(mc5_evaluate_fn, mc5_base_params, n_combos=20, rng=rng)
        mc5_pass = mc5_res["gate_pass"]

    ev = CandidateEval(
        name=name, n_trades=n, expectancy_net_bps=expectancy_net_bps,
        expectancy_gross_bps=expectancy_gross_bps, breakeven_cost_bps=breakeven_cost_bps,
        t_stat_eff_n=t_stat, beats_all_nulls=beats_all_nulls, cpcv_path_positive_pct=cpcv_pct,
        bootstrap_ci95_excludes_zero=bootstrap_excludes_zero, mc1_percentile=mc1_pct,
        walkforward_sign_consistency_pct=wf_consistency, seed_stable=seed_stable,
        last_third_significant=last_third_significant, trades_per_year=trades_per_year,
        mc3_pass=mc3_pass, mc5_pass=mc5_pass, p_value=p_value,
    )
    _count_checks(ev)
    return ev


def _count_checks(ev: CandidateEval):
    checks = [
        ev.expectancy_net_bps > 0,
        ev.t_stat_eff_n >= 3.0,
        ev.beats_all_nulls,
        ev.cpcv_path_positive_pct >= 80,
        ev.bootstrap_ci95_excludes_zero,
        ev.mc1_percentile >= 95,
        ev.walkforward_sign_consistency_pct >= 80,
        ev.seed_stable,
        ev.last_third_significant,
        ev.trades_per_year >= 300,
        ev.mc3_pass,
        ev.mc5_pass,
    ]
    ev.n_checks_passed = sum(bool(c) for c in checks)
    ev.n_checks_total = 12  # + BH-FDR, DSR, PBO filled at batch level = 15 (panel consistency #17 always fails/NA, MC2 pending)


def apply_batch_checks(evals: list, n_trials_cumulative: int, trial_sharpe_std: float, alpha_fdr: float = 0.10):
    """BH-FDR, DSR, PBO computed across the whole batch of candidates in
    one division. Mutates evals in place."""
    from statsmodels.stats.multitest import multipletests

    p_values = [e.p_value if e.p_value is not None else 1.0 for e in evals]
    if len(p_values) > 0:
        reject, _, _, _ = multipletests(p_values, alpha=alpha_fdr, method="fdr_bh")
        for e, r in zip(evals, reject):
            e.bh_fdr_pass = bool(r)

    for e in evals:
        if e.n_trades < 30:
            e.dsr = 0.0
            e.dsr_pass = False
            continue
        sharpe_hat = (e.expectancy_net_bps / 1e4) / (max(e.n_trades, 2) ** -0.5) if e.n_trades > 1 else 0.0
        from src.validation.montecarlo import deflated_sharpe_ratio
        dsr = deflated_sharpe_ratio(sharpe_hat, max(n_trials_cumulative, 1), trial_sharpe_std, 0.0, 3.0, e.n_trades)
        e.dsr = dsr
        e.dsr_pass = dsr >= 0.95

    if len(evals) >= 4:
        sharpes = np.array([e.expectancy_net_bps for e in evals])
        n = len(sharpes)
        half = n // 2
        rng = np.random.default_rng(0)
        order = rng.permutation(n)
        is_idx, oos_idx = order[:half], order[half:]
        if len(is_idx) > 0 and len(oos_idx) > 0:
            is_best = is_idx[np.argmax(sharpes[is_idx])]
            oos_rank = (sharpes[oos_idx] < sharpes[is_best]).mean()
            pbo_estimate = oos_rank
        else:
            pbo_estimate = 0.5
    else:
        pbo_estimate = None

    for e in evals:
        e.pbo = pbo_estimate
        e.pbo_pass = (pbo_estimate is not None) and (pbo_estimate <= 0.50)

    for e in evals:
        extra = sum([bool(e.bh_fdr_pass), bool(e.dsr_pass), bool(e.pbo_pass)])
        e.n_checks_passed += extra
        e.n_checks_total = 15  # 12 per-candidate + BH-FDR + DSR + PBO; panel-consistency(#17)=N/A, MC2=PENDING -- 15 of the 17 are actually gradeable here
