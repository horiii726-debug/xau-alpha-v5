"""Divisi V -- Volatilitas (estimation type). 14 formula, verbatim math
from DIVISI_V_VOLATILITAS.md. All causal: sigma[t] uses only bars up to
and including t (a trailing window ending at t), never future bars.
"""
import numpy as np
import pandas as pd


def _rolling_apply_causal(arr: np.ndarray, window: int, fn) -> np.ndarray:
    n = len(arr)
    out = np.full(n, np.nan)
    for t in range(window - 1, n):
        out[t] = fn(arr[t - window + 1 : t + 1])
    return out


def v01_parkinson(high: np.ndarray, low: np.ndarray, window: int) -> np.ndarray:
    """sigma^2 = (1/(4*n*ln2)) * sum[(ln(H/L))^2]"""
    log_hl2 = np.log(high / low) ** 2
    c = 1.0 / (4 * np.log(2))
    roll_sum = pd.Series(log_hl2).rolling(window).sum().values
    return np.sqrt(c * roll_sum / window)


def v02_garman_klass(high: np.ndarray, low: np.ndarray, open_: np.ndarray, close: np.ndarray, window: int) -> np.ndarray:
    """sigma^2 = (1/n)*sum[0.5*(ln(H/L))^2 - (2ln2-1)*(ln(C/O))^2]"""
    term = 0.5 * np.log(high / low) ** 2 - (2 * np.log(2) - 1) * np.log(close / open_) ** 2
    roll_mean = pd.Series(term).rolling(window).mean().values
    return np.sqrt(np.clip(roll_mean, 0, None))


def v03_rogers_satchell(high: np.ndarray, low: np.ndarray, open_: np.ndarray, close: np.ndarray, window: int) -> np.ndarray:
    """sigma^2 = (1/n)*sum[ln(H/C)*ln(H/O) + ln(L/C)*ln(L/O)]"""
    term = np.log(high / close) * np.log(high / open_) + np.log(low / close) * np.log(low / open_)
    roll_mean = pd.Series(term).rolling(window).mean().values
    return np.sqrt(np.clip(roll_mean, 0, None))


def v04_yang_zhang(high: np.ndarray, low: np.ndarray, open_: np.ndarray, close: np.ndarray, window: int) -> np.ndarray:
    """sigma^2 = sigma_overnight^2 + k*sigma_open_close^2 + (1-k)*sigma_RS^2
    k = 0.34/(1.34 + (n+1)/(n-1))"""
    n = window
    k = 0.34 / (1.34 + (n + 1) / (n - 1))
    prev_close = pd.Series(close).shift(1).values
    overnight = np.log(open_ / prev_close)
    oc = np.log(close / open_)

    sigma_on2 = pd.Series(overnight).rolling(window).var(ddof=1).values

    sigma_oc2 = pd.Series(oc).rolling(window).var(ddof=1).values

    rs_term = np.log(high / close) * np.log(high / open_) + np.log(low / close) * np.log(low / open_)
    sigma_rs2 = pd.Series(rs_term).rolling(window).mean().values

    sigma2 = sigma_on2 + k * sigma_oc2 + (1 - k) * np.clip(sigma_rs2, 0, None)
    return np.sqrt(np.clip(sigma2, 0, None))


def v05_close_to_close(close: np.ndarray, window: int) -> np.ndarray:
    """sigma^2 = (1/(n-1)) * sum[(r_i - rbar)^2]"""
    r = np.diff(np.log(close), prepend=np.log(close[0]))
    return pd.Series(r).rolling(window).std(ddof=1).values


def v06_realized_range(high: np.ndarray, low: np.ndarray, window: int, subsample: int) -> np.ndarray:
    """RRV = (1/(4ln2)) * sum[(ln(H_i)-ln(L_i))^2] over sub-intervals.
    Approximated here using `subsample` sub-windows within each `window`
    period (true intrabar sub-interval data isn't available from M1
    candle bars beyond what's already M1-granular; subsample partitions
    the M1-bar-level window itself)."""
    log_hl2 = np.log(high / low) ** 2
    c = 1.0 / (4 * np.log(2))
    sub_size = max(1, window // subsample)
    roll_sum = pd.Series(log_hl2).rolling(sub_size).sum().rolling(subsample).sum().values
    return np.sqrt(c * roll_sum / window)


def v07_bipower_variation(close: np.ndarray, window: int) -> np.ndarray:
    """BV = (pi/2) * (n/(n-1)) * sum[|r_i|*|r_{i-1}|]"""
    r = np.diff(np.log(close), prepend=np.log(close[0]))
    abs_r = np.abs(r)
    prod = abs_r * np.concatenate([[0], abs_r[:-1]])
    roll_sum = pd.Series(prod).rolling(window).sum().values
    n = window
    return (np.pi / 2) * (n / (n - 1)) * roll_sum


def v08_medrv(close: np.ndarray, window: int) -> np.ndarray:
    """MedRV = (pi/(6-4sqrt3+pi)) * (n/(n-2)) * sum[median(|r_{i-1}|,|r_i|,|r_{i+1}|)^2]"""
    r = np.diff(np.log(close), prepend=np.log(close[0]))
    abs_r = np.abs(r)
    n_bars = len(r)
    med = np.full(n_bars, np.nan)
    for i in range(1, n_bars - 1):
        med[i] = np.median([abs_r[i - 1], abs_r[i], abs_r[i + 1]])
    roll_sum = pd.Series(med**2).rolling(window).sum().values
    c = np.pi / (6 - 4 * np.sqrt(3) + np.pi)
    n = window
    return c * (n / (n - 2)) * roll_sum


def v09_minrv(close: np.ndarray, window: int) -> np.ndarray:
    """MinRV = (pi/(pi-2)) * (n/(n-1)) * sum[min(|r_i|,|r_{i+1}|)^2]"""
    r = np.diff(np.log(close), prepend=np.log(close[0]))
    abs_r = np.abs(r)
    n_bars = len(r)
    mn = np.full(n_bars, np.nan)
    for i in range(n_bars - 1):
        mn[i] = min(abs_r[i], abs_r[i + 1])
    roll_sum = pd.Series(mn**2).rolling(window).sum().values
    c = np.pi / (np.pi - 2)
    n = window
    return c * (n / (n - 1)) * roll_sum


def v10_realized_semivariance(close: np.ndarray, window: int) -> np.ndarray:
    """RS_plus - RS_minus"""
    r = np.diff(np.log(close), prepend=np.log(close[0]))
    rs_plus = pd.Series(np.where(r > 0, r**2, 0)).rolling(window).sum().values
    rs_minus = pd.Series(np.where(r < 0, r**2, 0)).rolling(window).sum().values
    return rs_plus - rs_minus


def v11_har_rv(rv_daily: np.ndarray, lags=(1, 5, 22)) -> np.ndarray:
    """RV_{t+1} = c + b_d*RV_t^(d) + b_w*RV_t^(w) + b_m*RV_t^(m). Returns the
    fitted RV_{t+1} forecast using a rolling OLS fit (refit each bar on
    trailing history only -- causal)."""
    d, w, m = lags
    n = len(rv_daily)
    rv_d = rv_daily
    rv_w = pd.Series(rv_daily).rolling(w).mean().values
    rv_m = pd.Series(rv_daily).rolling(m).mean().values
    forecast = np.full(n, np.nan)
    min_train = m + 30
    for t in range(min_train, n - 1):
        X = np.column_stack([np.ones(t - min_train), rv_d[min_train:t], rv_w[min_train:t], rv_m[min_train:t]])
        y = rv_d[min_train + 1 : t + 1]
        valid = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
        if valid.sum() < 10:
            continue
        coeffs, *_ = np.linalg.lstsq(X[valid], y[valid], rcond=None)
        x_now = np.array([1, rv_d[t], rv_w[t], rv_m[t]])
        if not np.isnan(x_now).any():
            forecast[t + 1] = x_now @ coeffs
    return forecast


def v12_ewma_variance(close: np.ndarray, lam: float = 0.94) -> np.ndarray:
    """sigma_t^2 = lambda*sigma_{t-1}^2 + (1-lambda)*r_t^2"""
    r = np.diff(np.log(close), prepend=np.log(close[0]))
    n = len(r)
    sigma2 = np.full(n, np.nan)
    sigma2[0] = r[0] ** 2
    for t in range(1, n):
        sigma2[t] = lam * sigma2[t - 1] + (1 - lam) * r[t] ** 2
    return np.sqrt(sigma2)


def v13_garch11_baseline(close: np.ndarray) -> np.ndarray:
    """sigma_t^2 = omega + alpha*e_{t-1}^2 + beta*sigma_{t-1}^2. Simple
    fixed-parameter GARCH(1,1) (typical omega/alpha/beta, not refit per
    bar -- PEMBANDING WAJIB per spec, not meant to be optimized)."""
    r = np.diff(np.log(close), prepend=np.log(close[0]))
    n = len(r)
    omega, alpha, beta = 1e-6, 0.1, 0.85
    sigma2 = np.full(n, np.nan)
    sigma2[0] = np.var(r[: min(50, n)])
    for t in range(1, n):
        sigma2[t] = omega + alpha * r[t - 1] ** 2 + beta * sigma2[t - 1]
    return np.sqrt(sigma2)


def v14_realized_kernel(close: np.ndarray, bandwidth_H: int = 10) -> np.ndarray:
    """RK = sum_{h=-H}^{H} k(h/(H+1)) * gamma_h, Parzen kernel, gamma_h =
    sum r_i*r_{i-h}. Causal: computed on a trailing window ending at t."""
    r = np.diff(np.log(close), prepend=np.log(close[0]))
    n = len(r)
    window = 4 * bandwidth_H

    def parzen(x):
        ax = abs(x)
        if ax <= 0.5:
            return 1 - 6 * ax**2 + 6 * ax**3
        elif ax <= 1:
            return 2 * (1 - ax) ** 3
        return 0.0

    out = np.full(n, np.nan)
    for t in range(window, n):
        seg = r[t - window : t]
        rk = 0.0
        for h in range(-bandwidth_H, bandwidth_H + 1):
            if h >= 0:
                gamma_h = np.sum(seg[: len(seg) - h] * seg[h:]) if h < len(seg) else 0
            else:
                gamma_h = np.sum(seg[-h:] * seg[: len(seg) + h])
            rk += parzen(h / (bandwidth_H + 1)) * gamma_h
        out[t] = max(0, rk)
    return np.sqrt(out)
