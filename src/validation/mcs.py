"""Model Confidence Set (Hansen, Lunde & Nason 2011), simplified bootstrap
implementation. Iteratively eliminates the worst-performing model (by
bootstrap test against the best-so-far) until no candidate is
significantly worse than the rest at level alpha, or one model remains.
Tie-break: among statistically-equivalent finalists, keep the simplest
(fewest n_parameters), per §O6.
"""
import numpy as np


def qlike_loss(realized_var: np.ndarray, forecast_var: np.ndarray, min_forecast_var: float = None) -> np.ndarray:
    """QLIKE(t) = RV/F - ln(RV/F) - 1, lower is better.

    QLIKE is well known to be extremely sensitive to near-zero forecasts
    (the ratio RV/F explodes as F->0). A forecast_var of literally 0 (or
    numerically indistinguishable from 0) happens for real on quiet M1
    bars with no price movement in the trailing window -- that's a
    degenerate, UNDEFINED evaluation point, not a "very bad forecast".
    First version floored forecast_var at 1e-300 to avoid a hard
    division error, which let the ratio blow up to 10^80+ and silently
    dominate the mean loss for any estimator that ever hits a quiet
    window (confirmed in F4: V05/V12 showed "average" QLIKE in the
    trillions, entirely driven by a handful of degenerate bars). Fixed:
    forecasts below min_forecast_var (default: 1e-6 of the median
    positive forecast_var in this call, i.e. relative to the estimator's
    own typical scale) are treated as undefined (NaN) and excluded,
    rather than scored with an exploding ratio."""
    forecast_var = np.asarray(forecast_var, dtype=np.float64)
    if min_forecast_var is None:
        positive = forecast_var[forecast_var > 0]
        min_forecast_var = np.median(positive) * 1e-6 if len(positive) else 0.0
    usable = forecast_var > max(min_forecast_var, 0.0)
    ratio = np.where(usable, realized_var / np.where(usable, forecast_var, 1.0), np.nan)
    with np.errstate(invalid="ignore"):
        return np.where(ratio > 0, ratio - np.log(ratio) - 1, np.nan)


def model_confidence_set(losses: dict, n_params: dict, alpha: float = 0.10, n_boot: int = 1000, rng=None) -> dict:
    """losses: {model_name: 1d loss array, all same length, NaN-aligned}.
    Returns dict with 'survivors' (list of model names in the final MCS)
    and 'eliminated' (ordered list of (model, p_value) eliminated, worst first)."""
    rng = rng or np.random.default_rng(0)
    names = list(losses.keys())
    L = np.column_stack([losses[n] for n in names])
    valid_rows = ~np.isnan(L).any(axis=1)
    L = L[valid_rows]
    n_obs = L.shape[0]
    if n_obs < 30:
        return {"survivors": names, "eliminated": [], "note": "TERLALU_SEDIKIT_OBSERVASI_UNTUK_MCS"}

    active = list(range(len(names)))
    eliminated = []

    while len(active) > 1:
        sub_L = L[:, active]
        mean_losses = sub_L.mean(axis=0)
        worst_idx_local = np.argmax(mean_losses)
        best_idx_local = np.argmin(mean_losses)
        if worst_idx_local == best_idx_local:
            break

        diff = sub_L[:, worst_idx_local] - sub_L[:, best_idx_local]
        observed_stat = diff.mean() / (diff.std(ddof=1) / np.sqrt(n_obs) + 1e-12)

        block_size = max(5, n_obs // 20)
        n_blocks = n_obs // block_size
        boot_stats = np.empty(n_boot)
        for b in range(n_boot):
            block_starts = rng.integers(0, n_obs - block_size, size=n_blocks)
            idx = np.concatenate([np.arange(s, s + block_size) for s in block_starts])
            boot_diff = diff[idx]
            boot_stats[b] = (boot_diff.mean() - diff.mean()) / (boot_diff.std(ddof=1) / np.sqrt(len(boot_diff)) + 1e-12)

        p_value = (np.abs(boot_stats) >= abs(observed_stat)).mean()

        if p_value < alpha:
            eliminated.append((names[active[worst_idx_local]], float(p_value)))
            active.pop(worst_idx_local)
        else:
            break

    survivors = [names[i] for i in active]
    if len(survivors) > 1:
        survivors.sort(key=lambda n: n_params.get(n, 0))
        simplest = survivors[0]
        return {
            "survivors": survivors,
            "eliminated": eliminated,
            "tie_break_simplest": simplest,
            "note": f"{len(survivors)} model tidak berbeda signifikan pada alpha={alpha} -- dipilih tersederhana",
        }
    return {"survivors": survivors, "eliminated": eliminated, "tie_break_simplest": survivors[0] if survivors else None}
