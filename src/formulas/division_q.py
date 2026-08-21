"""Divisi Q -- Spread & Likuiditas (estimation type). 12 formula, verbatim
math from DIVISI_Q_SPREAD_LIKUIDITAS.md. All causal (trailing windows).
"""
import numpy as np
import pandas as pd


def q01_roll_spread(close: np.ndarray, window: int) -> np.ndarray:
    """s = 2*sqrt(-Cov(r_t, r_{t-1})) kalau Cov<0, selain itu tidak terdefinisi (NaN)."""
    r = np.diff(np.log(close), prepend=np.log(close[0]))
    r_lag = np.concatenate([[np.nan], r[:-1]])
    n = len(r)
    out = np.full(n, np.nan)
    for t in range(window, n):
        r1 = r[t - window : t]
        r0 = r_lag[t - window : t]
        valid = ~np.isnan(r0)
        if valid.sum() < 10:
            continue
        cov = np.cov(r1[valid], r0[valid])[0, 1]
        if cov < 0:
            out[t] = 2 * np.sqrt(-cov)
    return out


def q02_corwin_schultz(high: np.ndarray, low: np.ndarray, window: int) -> np.ndarray:
    """s = 2*(exp(alpha)-1)/(1+exp(alpha)), alpha dari rasio beta (2 hari)
    dan gamma (2 hari gabungan) berbasis high-low."""
    hl = np.log(high / low) ** 2
    n = len(high)
    out = np.full(n, np.nan)
    for t in range(2, n):
        beta = hl[t - 1] + hl[t]
        h2 = max(high[t - 1], high[t])
        l2 = min(low[t - 1], low[t])
        gamma = np.log(h2 / l2) ** 2
        denom = 3 - 2 * np.sqrt(2)
        alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / denom - np.sqrt(gamma / denom)
        s = 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))
        out[t] = max(0, s)
    if window > 2:
        out = pd.Series(out).rolling(window).mean().values
    return out


def q03_abdi_ranaldo(high: np.ndarray, low: np.ndarray, close: np.ndarray, window: int) -> np.ndarray:
    """s = 2*sqrt(max(E[(c_t-eta_t)*(c_t-eta_{t+1})], 0)), eta=(h+l)/2 log."""
    eta = (np.log(high) + np.log(low)) / 2
    c = np.log(close)
    n = len(close)
    term = np.full(n, np.nan)
    for t in range(n - 1):
        term[t] = (c[t] - eta[t]) * (c[t] - eta[t + 1])
    out = np.full(n, np.nan)
    for t in range(window, n):
        seg = term[t - window : t]
        valid = seg[~np.isnan(seg)]
        if len(valid) < 10:
            continue
        e = max(valid.mean(), 0)
        out[t] = 2 * np.sqrt(e)
    return out


def q04_amihud_illiquidity(close: np.ndarray, n_ticks_per_bar: np.ndarray, window: int) -> np.ndarray:
    """ILLIQ = (1/n) * sum[|r_i| / aktivitas_i], aktivitas = jumlah tick per bar."""
    r = np.diff(np.log(close), prepend=np.log(close[0]))
    with np.errstate(invalid="ignore", divide="ignore"):
        term = np.abs(r) / np.maximum(n_ticks_per_bar, 1)
    return pd.Series(term).rolling(window).mean().values


def q05_effective_tick(close: np.ndarray, tick_size: float, window: int) -> np.ndarray:
    """s_eff = sum[gamma_j * s_j], gamma_j = probabilitas kelompok tick j.
    Approximated via the fraction of prices landing on multiples of
    tick_size, 2*tick_size, etc. (Holden 2009 simplified clustering)."""
    n = len(close)
    frac = (close / tick_size) % 1.0
    on_tick = (np.abs(frac) < 0.05) | (np.abs(frac - 1) < 0.05)
    gamma = pd.Series(on_tick.astype(float)).rolling(window).mean().values
    return gamma * tick_size * 2


def q06_spread_velocity(spread: np.ndarray, k: int) -> np.ndarray:
    """v_t = (s_t - s_{t-k}) / k"""
    n = len(spread)
    out = np.full(n, np.nan)
    out[k:] = (spread[k:] - spread[:-k]) / k
    return out


def q07_spread_acceleration(spread: np.ndarray, k: int) -> np.ndarray:
    """a_t = s_t - 2*s_{t-k} + s_{t-2k}"""
    n = len(spread)
    out = np.full(n, np.nan)
    out[2 * k :] = spread[2 * k :] - 2 * spread[k : n - k] + spread[: n - 2 * k]
    return out


def q08_spread_to_vol_ratio(spread_bps: np.ndarray, sigma_bps: np.ndarray) -> np.ndarray:
    """kappa_t = s_t_bps / sigma_t_bps"""
    with np.errstate(invalid="ignore", divide="ignore"):
        return spread_bps / sigma_bps


def q09_spread_resiliency(spread: np.ndarray, ref_window: int) -> np.ndarray:
    """tau = jumlah bar sampai s_t kembali ke persentil-50 jendela referensi
    setelah melewati persentil-90."""
    n = len(spread)
    out = np.full(n, np.nan)
    for t in range(ref_window, n):
        ref = spread[t - ref_window : t]
        p50 = np.percentile(ref, 50)
        p90 = np.percentile(ref, 90)
        if spread[t] <= p90:
            continue
        tau = None
        for h in range(1, min(ref_window, n - t)):
            if spread[t + h] <= p50:
                tau = h
                break
        out[t] = tau if tau is not None else np.nan
    return out


def q10_spread_percentile_gate(spread: np.ndarray, percentile: float, ref_window: int) -> np.ndarray:
    """gate_t = 1 jika s_t <= persentil_p(s) pada jendela referensi."""
    n = len(spread)
    gate = np.zeros(n)
    for t in range(ref_window, n):
        ref = spread[t - ref_window : t]
        thresh = np.percentile(ref, percentile)
        gate[t] = 1.0 if spread[t] <= thresh else 0.0
    return gate


def q11_spread_regime_break(spread: np.ndarray, window: int) -> np.ndarray:
    """ICSS: D_k = (C_k/C_T) - k/T, patahan saat max|D_k| melewati nilai
    kritis. Returns the ICSS statistic (max|D_k|) per trailing window --
    caller applies the critical-value threshold."""
    n = len(spread)
    out = np.full(n, np.nan)
    for t in range(window, n):
        seg = spread[t - window : t] ** 2
        cumsum = np.cumsum(seg)
        C_T = cumsum[-1]
        if C_T <= 0:
            continue
        k = np.arange(1, len(seg) + 1)
        D_k = cumsum / C_T - k / len(seg)
        out[t] = np.max(np.abs(D_k))
    return out


def q12_realized_spread_cost(spread_at_exec_bps: np.ndarray, slippage_model_bps: np.ndarray) -> np.ndarray:
    """biaya_realized_bps = 2*s_eksekusi + slippage_model (already in bps)."""
    return 2 * spread_at_exec_bps + slippage_model_bps
