"""F2b pilot set -- 12 formula, 1 varian tiap (mid-grid parameter), per
07_FASE_EKSEKUSI.md §F2b (E72 diganti E70 per PATCH_01_ANGGARAN.md §4).

Each function takes a bar dataframe (columns: mid_close, high proxy via
ask_high/bid_high if present) and returns a causal +-1 signal array
(signal[t] decided using data up to and including bar t's close, meant to
be applied to the return realized OVER (t, t+1], consistent with L9 --
caller is responsible for the actual shift/execution-timing when turning
this into a trade).

Formulas without an inherent "direction" (entropy, changepoint) get a
CONSTRUCTED direction (documented per-function) purely so F2b has a
signal to measure capacity with -- this is NOT a claim that the
construction is a good trading rule. F2b measures panel/horizon
STATISTICAL CAPACITY (kappa, BR_efektif, K_eff, t_pooled), not formula
quality; that's F6's job.
"""
import numpy as np
import pandas as pd


def _causal_shift(sig: np.ndarray) -> np.ndarray:
    """Shift signal by 1 bar so sig[t] was known at bar t-1's close (pure
    safety net for callers that forget -- prefer causal construction in
    each formula directly)."""
    return np.concatenate([[0.0], sig[:-1]])


def e01_intraday_momentum(mid: np.ndarray, L: int = 12) -> np.ndarray:
    sig = np.full(len(mid), np.nan)
    sig[L:] = np.sign((mid[L:] - mid[:-L]) / mid[:-L])
    return np.nan_to_num(sig, nan=0.0)


def e10_variance_ratio_lm(mid: np.ndarray, q: int = 4, window: int = 200) -> np.ndarray:
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    sig = np.full(len(mid), np.nan)
    rq_full = pd.Series(r).rolling(q).sum().values  # computed ONCE (was recomputed per-bar -- O(n^2))
    for t in range(window + q, len(mid)):
        r1 = r[t - window : t]
        rq = rq_full[t - window : t]
        var1 = np.var(r1)
        varq = np.var(rq[~np.isnan(rq)])
        if var1 <= 0 or len(rq[~np.isnan(rq)]) < 2:
            continue
        vr = varq / (q * var1)
        sig[t] = np.sign(vr - 1)  # VR>1 -> trending -> follow recent direction
    trend_dir = np.sign(np.diff(mid, prepend=mid[0]))
    return np.nan_to_num(sig, nan=0.0) * np.where(np.isnan(sig), 0, trend_dir)


def e22_dfa_alpha(mid: np.ndarray, window: int = 288, poly_order: int = 1) -> np.ndarray:
    """DFA alpha exponent (persistence). alpha>0.5 -> persistent (follow
    recent direction), alpha<0.5 -> anti-persistent (fade recent direction)."""
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    sig = np.full(len(mid), np.nan)
    n_scales = [window // k for k in (8, 4, 2, 1) if window // k >= 20]
    for t in range(window, len(mid)):
        y = np.cumsum(r[t - window : t] - r[t - window : t].mean())
        fluct = []
        for n in n_scales:
            n_boxes = len(y) // n
            if n_boxes < 2:
                continue
            rms = []
            for b in range(n_boxes):
                seg = y[b * n : (b + 1) * n]
                x = np.arange(n)
                coeffs = np.polyfit(x, seg, poly_order)
                trend = np.polyval(coeffs, x)
                rms.append(np.sqrt(np.mean((seg - trend) ** 2)))
            fluct.append((n, np.mean(rms)))
        if len(fluct) < 2:
            continue
        ns = np.log([f[0] for f in fluct])
        fs = np.log([f[1] for f in fluct if f[1] > 0]) if all(f[1] > 0 for f in fluct) else None
        if fs is None or len(fs) != len(ns):
            continue
        alpha = np.polyfit(ns, fs, 1)[0]
        recent_dir = np.sign(mid[t - 1] - mid[t - 5]) if t >= 5 else 0
        sig[t] = recent_dir if alpha > 0.5 else -recent_dir
    return np.nan_to_num(sig, nan=0.0)


def e30_shannon_entropy_sign(mid: np.ndarray, window: int = 96, m: int = 3) -> np.ndarray:
    """CONSTRUCTED direction: low entropy (more structure) -> follow recent
    momentum; high entropy (near-random) -> flat (0). Entropy has no
    inherent sign; this pairs it with momentum direction as a filter."""
    r = np.sign(np.diff(np.log(mid), prepend=np.log(mid[0])))
    sig = np.full(len(mid), np.nan)
    for t in range(window, len(mid)):
        patterns = [tuple(r[t - window + i : t - window + i + m]) for i in range(window - m)]
        counts = pd.Series(patterns).value_counts(normalize=True)
        H = -(counts * np.log2(counts)).sum()
        H_max = np.log2(2**m)
        low_entropy = H < 0.85 * H_max
        recent_dir = np.sign(mid[t] - mid[t - 5]) if t >= 5 else 0
        sig[t] = recent_dir if low_entropy else 0
    return np.nan_to_num(sig, nan=0.0)


def e60_drift_burst_tstat(mid: np.ndarray, h_mean: int = 6, h_vol: int = 24) -> np.ndarray:
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    mu_hat = pd.Series(r).rolling(h_mean).mean().values
    sigma_hat = pd.Series(r).rolling(h_vol).std().values
    with np.errstate(invalid="ignore", divide="ignore"):
        t_stat = np.sqrt(h_mean) * mu_hat / sigma_hat
    return np.nan_to_num(np.sign(t_stat), nan=0.0)


def e70_mann_kendall(mid: np.ndarray, window: int = 48) -> np.ndarray:
    sig = np.full(len(mid), np.nan)
    for t in range(window, len(mid)):
        x = mid[t - window : t]
        s = 0
        for i in range(len(x)):
            s += np.sum(np.sign(x[i + 1 :] - x[i]))
        sig[t] = np.sign(s)
    return np.nan_to_num(sig, nan=0.0)


def e90_cusum_changepoint(mid: np.ndarray, k_mult: float = 0.5, h_mult: float = 4.0, window: int = 96) -> np.ndarray:
    """CONSTRUCTED direction: on a changepoint alarm, follow the direction
    of the post-alarm drift (mu_hat since the alarm)."""
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    sig = np.full(len(mid), 0.0)
    s_pos, s_neg = 0.0, 0.0
    mu0 = 0.0
    sigma = pd.Series(r).rolling(window).std().values
    for t in range(window, len(mid)):
        if np.isnan(sigma[t]) or sigma[t] <= 0:
            continue
        k = k_mult * sigma[t]
        h = h_mult * sigma[t]
        s_pos = max(0, s_pos + (r[t] - mu0 - k))
        s_neg = min(0, s_neg + (r[t] - mu0 + k))
        if s_pos > h:
            sig[t] = 1.0
            s_pos = 0.0
        elif s_neg < -h:
            sig[t] = -1.0
            s_neg = 0.0
    return sig


def x01_triple_barrier_reference(n_bars: int) -> tuple:
    """X01 in the F2b pilot isn't a direction-generator -- it's the
    reference barrier structure (k_sl=1.5, k_tp=2.5, the riset-sebelumnya
    comparison point used throughout 00/04) applied with RANDOM entries,
    same spirit as the F2 payoff gate but at pilot scale. Returns the
    (k_sl, k_tp) tuple for the caller to apply via triple_barrier_labels."""
    return (1.5, 2.5)


def x06_vertical_only_baseline(mid: np.ndarray, hold_bars: int) -> np.ndarray:
    """No signal to generate -- vertical-only exit is direction-agnostic
    by construction (X06_VERTICAL_ONLY_BASELINE has n_parameters=0).
    Returns a constant long-only signal since a directionless baseline
    still needs a stance to be a 'strategy' in the F2b PnL-correlation
    sense; direction is arbitrary here (always long), consistent with how
    X06 is documented as a payoff-only baseline, not a direction candidate."""
    return np.ones(len(mid))


def x32_volatility_targeting_size(sigma_hat: np.ndarray, target_vol_bps: float = 100.0, size_cap: float = 3.0) -> np.ndarray:
    """Not a direction -- a POSITION SIZE multiplier, per X32's actual
    definition (division X, sizing family). Paired with a direction signal
    from elsewhere (F2b pairs it with E01 momentum direction, since X32 has
    no direction of its own)."""
    sigma_bps = sigma_hat * 1e4
    with np.errstate(invalid="ignore", divide="ignore"):
        size = target_vol_bps / sigma_bps
    return np.clip(np.nan_to_num(size, nan=0.0), 0, size_cap)


def v01_parkinson_sigma(high: np.ndarray, low: np.ndarray, window: int = 48) -> np.ndarray:
    from src.labeling.triple_barrier import parkinson_sigma

    return parkinson_sigma(high, low, window)


def q08_spread_to_vol_ratio(spread_bps: np.ndarray, sigma_bps: np.ndarray, window: int = 48) -> np.ndarray:
    """kappa_t = spread_bps / sigma_bps -- NOT a direction, a cost-gate
    filter (division Q, cost family). F2b uses it to flag bars where
    trading is cheap relative to opportunity, paired with a direction
    signal from elsewhere."""
    with np.errstate(invalid="ignore", divide="ignore"):
        ratio = pd.Series(spread_bps).rolling(window).mean().values / sigma_bps
    return np.nan_to_num(ratio, nan=np.inf)


PILOT_FORMULAS_DIRECTIONAL = {
    "E01": e01_intraday_momentum,
    "E10": e10_variance_ratio_lm,
    "E22": e22_dfa_alpha,
    "E30": e30_shannon_entropy_sign,
    "E60": e60_drift_burst_tstat,
    "E70": e70_mann_kendall,
    "E90": e90_cusum_changepoint,
    "X06": x06_vertical_only_baseline,
}
# X01 (barrier reference), X32 (sizing), V01 (vol estimator), Q08 (cost
# filter) are NOT direction generators by their own definition in the
# registry -- they modify/filter/size a direction signal rather than
# produce one. Kept as separate functions above, combined explicitly by
# the F2b runner rather than forced into a fake "direction".
