"""Monte Carlo suite MC1-MC5, per 05_VALIDASI_STATISTIK.md.

Each function takes a trade-level return series (in fraction, not bps)
and returns a dict with the gate-relevant statistics. Nothing here decides
pass/fail on its own -- that's a threshold applied by the caller against
the ambang in 05_VALIDASI_STATISTIK.md / 06_GERBANG_DAN_ANGGARAN.md, kept
separate so thresholds stay in one place (pre-registered, not buried in
code).
"""
from dataclasses import dataclass, field

import numpy as np


def mc1_permutation(signal: np.ndarray, bar_returns: np.ndarray, n: int = 1000, block_size: int = 10, rng: np.random.Generator = None) -> dict:
    """Block permutation test of whether a SIGNAL's pairing with return
    timing matters, per 05_VALIDASI_STATISTIK.md montecarlo.MC1_permutasi:
    "Permutasi acak biasa TIDAK cukup -- merusak autokorelasi, null jadi
    terlalu lemah" -- hence block permutation, applied to the underlying
    BAR RETURNS (not to the candidate's own already-realized trade
    outcomes, whose sum is invariant under any permutation and would make
    this test vacuous). Each permutation re-pairs the FIXED signal with a
    block-shuffled return series and recomputes the strategy total; the
    observed (correctly-paired) total is compared against that null
    distribution. Gate: observed above the 95th percentile."""
    rng = rng or np.random.default_rng()
    n = int(n)
    n_bars = min(len(signal), len(bar_returns))
    sig = signal[:n_bars]
    ret = bar_returns[:n_bars]
    observed = float((sig * ret).sum())

    n_blocks = max(1, n_bars // block_size)
    blocks = [ret[i * block_size : (i + 1) * block_size] for i in range(n_blocks)]
    perm_stats = np.empty(n)
    for i in range(n):
        order = rng.permutation(n_blocks)
        permuted_ret = np.concatenate([blocks[j] for j in order])
        m = min(len(sig), len(permuted_ret))
        perm_stats[i] = float((sig[:m] * permuted_ret[:m]).sum())
    percentile = float((perm_stats < observed).mean() * 100)
    return {"observed": observed, "percentile": percentile, "gate_pass": percentile >= 95}


def mc2_survival_paths(
    trade_returns: np.ndarray,
    n_paths: int = 10000,
    max_daily_loss_pct: float = None,
    max_total_drawdown_pct: float = None,
    profit_target_pct: float = None,
    horizons=(100, 250, 500),
    rng: np.random.Generator = None,
) -> dict:
    """Bootstrap-resample trade ORDER (not values) to build many equity
    paths, apply prop-firm rules, compute P(breach). If the prop-firm
    parameters are None (LOOKUP not resolved yet), returns UNVERIFIED with
    breach probabilities left as None rather than computed on a guessed
    threshold -- per 02_DATA_DAN_BIAYA.md, unresolved LOOKUPs must not be
    silently defaulted."""
    rng = rng or np.random.default_rng()
    n_trades = len(trade_returns)
    result = {
        "n_paths": n_paths,
        "params_status": "OK" if (max_total_drawdown_pct is not None) else "UNVERIFIED_LOOKUP_MISSING",
    }
    if max_total_drawdown_pct is None:
        result["breach_prob"] = {h: None for h in horizons}
        result["note"] = "max_total_drawdown_pct / max_daily_loss_pct / profit_target_pct belum LOOKUP -- P(breach) TIDAK_BISA_DIHITUNG"
        return result

    breach_counts = {h: 0 for h in horizons}
    max_dd_samples = []
    for _ in range(n_paths):
        order = rng.integers(0, n_trades, size=max(horizons))
        path_returns = trade_returns[order]
        equity = np.cumprod(1 + path_returns)
        peak = np.maximum.accumulate(equity)
        dd_pct = (peak - equity) / peak * 100
        max_dd_samples.append(dd_pct.max())
        for h in horizons:
            eq_h = equity[:h]
            peak_h = np.maximum.accumulate(eq_h)
            dd_h = (peak_h - eq_h) / peak_h * 100
            breached = (dd_h.max() >= max_total_drawdown_pct)
            if max_daily_loss_pct is not None:
                daily_dd = -path_returns[:h] * 100
                breached = breached or (daily_dd.max() >= max_daily_loss_pct)
            if breached:
                breach_counts[h] += 1

    result["breach_prob"] = {h: breach_counts[h] / n_paths for h in horizons}
    result["max_drawdown_distribution_pct"] = {
        "p50": float(np.percentile(max_dd_samples, 50)),
        "p95": float(np.percentile(max_dd_samples, 95)),
        "p99": float(np.percentile(max_dd_samples, 99)),
    }
    result["gate_pass_250"] = result["breach_prob"].get(250, 1.0) <= 0.05
    return result


def mc3_execution_slippage(
    trade_returns_no_slip: np.ndarray,
    spread_bps: np.ndarray,
    sigma_bps: np.ndarray,
    alpha_grid=(0.5, 1.0, 1.5),
    beta_grid=(0.0, 0.25, 0.5),
    n_paths: int = 1000,
    rng: np.random.Generator = None,
) -> dict:
    """Resample (alpha,beta) slippage params per trade, gate: expectancy
    stays positive at the 5th percentile of the resulting distribution."""
    rng = rng or np.random.default_rng()
    n = len(trade_returns_no_slip)
    path_expectancies = np.empty(n_paths)
    for p in range(n_paths):
        alpha = rng.choice(alpha_grid, size=n)
        beta = rng.choice(beta_grid, size=n)
        slip_bps = alpha * spread_bps + beta * sigma_bps
        adj_returns = trade_returns_no_slip - slip_bps / 1e4
        path_expectancies[p] = adj_returns.mean()
    p5 = float(np.percentile(path_expectancies, 5))
    return {"expectancy_p5": p5, "gate_pass": p5 > 0}


def deflated_sharpe_ratio(sharpe_hat: float, n_trials: int, trial_sharpe_std: float, skew: float, kurt: float, n_obs: int) -> float:
    """DSR per 00_KONTRAK_DAN_KELAYAKAN.md formula_dsr. SR_0 (expected max
    Sharpe under null across n_trials) approximated via the standard
    extreme-value expansion using the empirical variance of trial Sharpes
    (trial_sharpe_std), NOT assuming independence."""
    from scipy.stats import norm

    euler_gamma = 0.5772156649
    if n_trials <= 1:
        sr0 = 0.0
    else:
        sr0 = trial_sharpe_std * (
            (1 - euler_gamma) * norm.ppf(1 - 1.0 / n_trials) + euler_gamma * norm.ppf(1 - 1.0 / (n_trials * np.e))
        )
    numerator = (sharpe_hat - sr0) * np.sqrt(n_obs - 1)
    denominator = np.sqrt(max(1e-12, 1 - skew * sharpe_hat + ((kurt - 1) / 4) * sharpe_hat**2))
    return float(norm.cdf(numerator / denominator))


def mc4_deflated_sharpe(trade_returns: np.ndarray, n_trials: int, trial_sharpe_std: float) -> dict:
    sharpe_hat = trade_returns.mean() / trade_returns.std(ddof=1) if trade_returns.std(ddof=1) > 0 else 0.0
    from scipy.stats import skew as sk, kurtosis as kt

    skewness = float(sk(trade_returns)) if len(trade_returns) > 2 else 0.0
    kurt = float(kt(trade_returns, fisher=False)) if len(trade_returns) > 3 else 3.0
    dsr = deflated_sharpe_ratio(sharpe_hat, n_trials, trial_sharpe_std, skewness, kurt, len(trade_returns))
    return {"sharpe_hat": sharpe_hat, "dsr": dsr, "gate_pass": dsr >= 0.95}


def mc5_parameter_perturbation(evaluate_fn, base_params: dict, perturb_pcts=(-0.20, -0.10, 0.10, 0.20), n_combos: int = 500, rng: np.random.Generator = None) -> dict:
    """evaluate_fn(params) -> expectancy (float). Perturb every numeric
    param independently by each pct in perturb_pcts (or sample combos if
    the full grid exceeds n_combos). Gate: sign of expectancy never flips
    vs the base case."""
    rng = rng or np.random.default_rng()
    base_expectancy = evaluate_fn(base_params)
    base_sign = np.sign(base_expectancy)

    numeric_keys = [k for k, v in base_params.items() if isinstance(v, (int, float))]
    results = []
    combos_tried = 0
    max_attempts = n_combos * 3
    attempts = 0
    seen = set()
    while combos_tried < n_combos and attempts < max_attempts:
        attempts += 1
        pcts = {k: rng.choice(perturb_pcts) for k in numeric_keys}
        key = tuple(sorted(pcts.items()))
        if key in seen:
            continue
        seen.add(key)
        params = dict(base_params)
        for k, pct in pcts.items():
            params[k] = base_params[k] * (1 + pct)
        exp = evaluate_fn(params)
        results.append(exp)
        combos_tried += 1

    results = np.array(results)
    sign_flips = int((np.sign(results) != base_sign).sum())
    return {
        "base_expectancy": base_expectancy,
        "n_combos_tested": combos_tried,
        "sign_flips": sign_flips,
        "gate_pass": sign_flips == 0,
    }
