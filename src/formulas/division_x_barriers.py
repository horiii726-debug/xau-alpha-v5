"""Divisi X -- barrier variants (X02-X05) & EVT tail stops (X10-X14),
verbatim math from DIVISI_X_EXIT_SL_TP_SIZING.md. All fit on TRAIN-window
data only where the formula calls for estimation (§L3).
"""
import numpy as np
import pandas as pd
from scipy import stats


def x02_asymmetric_barrier_skew(realized_skew: np.ndarray, base_ratio: float, w: float) -> np.ndarray:
    """ratio = base_ratio * (1 + w*skew_realized) -- returns k_tp/k_sl ratio
    per bar, to be applied against a base k_sl."""
    return base_ratio * (1 + w * realized_skew)


def x03_time_decay_barrier(k_sl0: float, k_tp0: float, d: float, t: np.ndarray, T: int) -> tuple:
    """k_sl(t) = k_sl0*exp(-d*t/T), k_tp(t) = k_tp0*exp(-d*t/T) -- t = bars
    since entry, T = max_hold. Returns (k_sl_t, k_tp_t) arrays."""
    decay = np.exp(-d * t / T)
    return k_sl0 * decay, k_tp0 * decay


def x04_empirical_quantile_barrier(mfe_train: np.ndarray, mae_train: np.ndarray, q_tp: float, q_sl: float) -> tuple:
    """TP = quantile_q_tp(MFE historis), SL = quantile_q_sl(MAE historis),
    dihitung pada jendela LATIH saja. Returns (tp_mult, sl_mult) as
    multipliers on entry price (already 1+x / 1-x form expected by caller)."""
    tp_mult = np.quantile(mfe_train, q_tp)
    sl_mult = np.quantile(mae_train, q_sl)
    return tp_mult, sl_mult


def x05_vol_tercile_conditional_barrier(sigma: np.ndarray, tercile_window: int, ratio_tight: tuple, ratio_wide: tuple) -> np.ndarray:
    """Pilih (k_sl,k_tp) berbeda per tersile volatilitas (dihitung dari
    jendela LATIH). Returns an array of (k_sl,k_tp) tuples per bar, packed
    as an (n,2) array: low/mid tercile -> ratio_tight, high tercile -> ratio_wide."""
    n = len(sigma)
    out = np.zeros((n, 2))
    for t in range(tercile_window, n):
        window = sigma[t - tercile_window : t]
        p33, p66 = np.percentile(window[~np.isnan(window)], [33, 66]) if np.any(~np.isnan(window)) else (np.nan, np.nan)
        if np.isnan(sigma[t]):
            out[t] = ratio_tight
        elif sigma[t] > p66:
            out[t] = ratio_wide
        else:
            out[t] = ratio_tight
    return out


def x10_pot_gpd_stop(excess_train: np.ndarray, u: float, p_stop: float) -> float:
    """Peaks-over-threshold GPD: fit xi, beta on excess=X-u for X>u (train
    window), SL = u + (beta/xi)*[(n/(Nu*(1-p)))^xi - 1]."""
    excess_train = excess_train[excess_train > 0]
    if len(excess_train) < 20:
        return np.nan
    xi, loc, beta = stats.genpareto.fit(excess_train, floc=0)
    n = len(excess_train)
    nu = len(excess_train)
    if abs(xi) < 1e-6:
        return u + beta * -np.log(nu / n * (1 - p_stop))
    return u + (beta / xi) * ((n / (nu * (1 - p_stop))) ** xi - 1)


def x11_hill_tail_stop(returns_train: np.ndarray, k_frac: float) -> float:
    """alpha_Hill = [(1/k)*sum(ln(X_(i)/X_(k+1)))]^-1, k = k_frac * n order
    statistics of |returns|. SL diskalakan terbalik terhadap alpha (tail
    lebih tebal -> alpha kecil -> stop lebih lebar)."""
    abs_r = np.sort(np.abs(returns_train))[::-1]
    k = max(2, int(k_frac * len(abs_r)))
    top_k = abs_r[:k]
    x_k1 = abs_r[k] if k < len(abs_r) else abs_r[-1]
    if x_k1 <= 0:
        return np.nan
    log_ratios = np.log(top_k / x_k1)
    alpha_hill = 1.0 / (log_ratios.mean() + 1e-12)
    return 1.0 / alpha_hill  # scale factor, inversely related to tail thickness


def x12_cvar_optimal_stop(losses_train: np.ndarray, beta: float) -> float:
    """min_z[z + 1/((1-beta)*N) * sum(max(L_j-z,0))] -- SL = z* dari
    optimasi (grid search sederhana, cukup untuk 1D convex problem ini)."""
    z_grid = np.linspace(np.percentile(losses_train, 50), np.percentile(losses_train, 99.5), 200)
    n = len(losses_train)
    best_z, best_val = z_grid[0], np.inf
    for z in z_grid:
        val = z + (1 / ((1 - beta) * n)) * np.sum(np.maximum(losses_train - z, 0))
        if val < best_val:
            best_val, best_z = val, z
    return best_z


def x13_conditional_evt_stop(sigma_t: float, z_residuals_train: np.ndarray, p: float) -> float:
    """Tahap 1: sigma_t dari model volatilitas (caller-supplied). Tahap 2:
    GPD pada residual terstandar z_t = r_t/sigma_t. SL_t = sigma_t * q_p(z)."""
    z_residuals_train = z_residuals_train[np.isfinite(z_residuals_train)]
    if len(z_residuals_train) < 30:
        return np.nan
    q = np.quantile(np.abs(z_residuals_train), p)
    return sigma_t * q


def x14_semiparametric_tail_stop(returns_train: np.ndarray, u_percentile: float) -> float:
    """Badan dari ECDF empiris, ekor dari hukum pangkat (indeks Hill),
    disambung pada ambang u (percentile)."""
    abs_r = np.abs(returns_train)
    u = np.percentile(abs_r, u_percentile)
    tail = abs_r[abs_r > u]
    if len(tail) < 10:
        return u
    hill_alpha = 1.0 / np.mean(np.log(tail / u))
    return u * (1 + 1.0 / max(hill_alpha, 0.1))
