"""Divisi E -- Entry/Arah, formula tambahan di luar 7 yang sudah ada di
pilot_f2b.py (E01,E10,E22,E30,E60,E70,E90). Verbatim math dari
DIVISI_E_ENTRY_ARAH.md. Semua causal (signal[t] hanya pakai data s.d.
bar t, diterapkan ke return (t,t+1] oleh caller -- lihat F6 runner).
"""
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats


def e02_vol_scaled_momentum(mid: np.ndarray, sigma: np.ndarray, L: int, theta: float) -> np.ndarray:
    """z = (C_t-C_{t-L})/(sigma_t*sqrt(L)), sig = sign(z)*1(|z|>theta)"""
    n = len(mid)
    z = np.full(n, np.nan)
    z[L:] = (mid[L:] - mid[:-L]) / (sigma[L:] * np.sqrt(L) * mid[:-L] + 1e-15)
    sig = np.sign(z) * (np.abs(z) > theta)
    return np.nan_to_num(sig, nan=0.0)


def e03_short_horizon_reversal(mid: np.ndarray, sigma: np.ndarray, L: int, theta: float) -> np.ndarray:
    """z = (C_t-C_{t-L})/(sigma_t*sqrt(L)), sig = -sign(z)*1(|z|>theta)"""
    return -e02_vol_scaled_momentum(mid, sigma, L, theta)


def e04_session_gap_continuation(open_: np.ndarray, prev_close: np.ndarray, sigma: np.ndarray, theta: float) -> np.ndarray:
    """gap = (O_t-C_{t-1})/C_{t-1}, sig = sign(gap)*1(|gap|>theta*sigma)"""
    gap = (open_ - prev_close) / prev_close
    sig = np.sign(gap) * (np.abs(gap) > theta * sigma)
    return np.nan_to_num(sig, nan=0.0)


def e11_variance_ratio_wright(mid: np.ndarray, q: int, window: int) -> np.ndarray:
    """VR berbasis rank/sign (Wright 2000), pendekatan: pakai rank dari
    return alih-alih nilai mentah untuk VR, distribusi valid sampel kecil."""
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    n = len(r)
    sig = np.full(n, np.nan)
    for t in range(window + q, n):
        seg = r[t - window : t]
        ranks = scipy_stats.rankdata(seg)
        r1 = ranks - ranks.mean()
        rq = pd.Series(r1).rolling(q).sum().dropna().values
        var1, varq = np.var(r1), np.var(rq) if len(rq) > 1 else np.nan
        if np.isnan(varq) or var1 <= 0:
            continue
        vr = varq / (q * var1)
        trend_dir = np.sign(mid[t - 1] - mid[t - 5]) if t >= 5 else 0
        sig[t] = trend_dir if vr > 1 else -trend_dir
    return np.nan_to_num(sig, nan=0.0)


def e20_hurst_rs(mid: np.ndarray, window: int) -> np.ndarray:
    """H dari slope ln(R/S) vs ln(n) pada beberapa sub-window. sig =
    sign(momentum) kalau H>0.5 (persisten), fade kalau H<0.5."""
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    n_bars = len(mid)
    sig = np.full(n_bars, np.nan)
    sub_ns = [window // 4, window // 2, window]
    for t in range(window, n_bars):
        seg = r[t - window : t]
        rs_vals = []
        for sub_n in sub_ns:
            n_chunks = len(seg) // sub_n
            if n_chunks < 1:
                continue
            rs_chunk = []
            for c in range(n_chunks):
                chunk = seg[c * sub_n : (c + 1) * sub_n]
                mean_adj = np.cumsum(chunk - chunk.mean())
                R = mean_adj.max() - mean_adj.min()
                S = chunk.std(ddof=1)
                if S > 0:
                    rs_chunk.append(R / S)
            if rs_chunk:
                rs_vals.append((sub_n, np.mean(rs_chunk)))
        if len(rs_vals) < 2:
            continue
        log_n = np.log([v[0] for v in rs_vals])
        log_rs = np.log([max(v[1], 1e-10) for v in rs_vals])
        H = np.polyfit(log_n, log_rs, 1)[0]
        recent_dir = np.sign(mid[t - 1] - mid[t - 5]) if t >= 5 else 0
        sig[t] = recent_dir if H > 0.5 else (-recent_dir if H < 0.5 else 0)
    return np.nan_to_num(sig, nan=0.0)


def e50_fft_dominant_period(mid: np.ndarray, window: int) -> np.ndarray:
    """Periode dominan dari FFT, sig dari arah harga relatif fase siklus
    (proxy sederhana: posisi dalam siklus dominan -> momentum jika di
    bagian naik siklus)."""
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    n_bars = len(mid)
    sig = np.full(n_bars, np.nan)
    for t in range(window, n_bars):
        seg = r[t - window : t] - r[t - window : t].mean()
        fft_vals = np.fft.rfft(seg)
        power = np.abs(fft_vals) ** 2
        if len(power) < 3:
            continue
        dom_freq_idx = np.argmax(power[1:]) + 1
        phase = np.angle(fft_vals[dom_freq_idx])
        sig[t] = np.sign(np.cos(phase))
    return np.nan_to_num(sig, nan=0.0)


def e54_spectral_entropy(mid: np.ndarray, window: int, thresh: float = 0.7) -> np.ndarray:
    """SE = -sum p_f*ln(p_f)/ln(N_f). Low SE (concentrated spectrum) ->
    trade in momentum direction; high SE (near-white-noise) -> flat."""
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    n_bars = len(mid)
    sig = np.full(n_bars, np.nan)
    for t in range(window, n_bars):
        seg = r[t - window : t] - r[t - window : t].mean()
        fft_vals = np.fft.rfft(seg)
        power = np.abs(fft_vals) ** 2
        p = power / (power.sum() + 1e-15)
        p = p[p > 0]
        se = -np.sum(p * np.log(p)) / np.log(len(p)) if len(p) > 1 else 1.0
        recent_dir = np.sign(mid[t - 1] - mid[t - 5]) if t >= 5 else 0
        sig[t] = recent_dir if se < thresh else 0
    return np.nan_to_num(sig, nan=0.0)


def e64_realized_skewness_signal(mid: np.ndarray, window: int) -> np.ndarray:
    """RSkew = sqrt(N)*sum(r_i^3)/RV^1.5. sig = sign(RSkew) (momentum in
    skew direction -- positive skew historically associated with
    continuation per some literature; direction taken directly from sign)."""
    r = np.diff(np.log(mid), prepend=np.log(mid[0]))
    n_bars = len(mid)
    sig = np.full(n_bars, np.nan)
    for t in range(window, n_bars):
        seg = r[t - window : t]
        rv = np.sum(seg**2)
        if rv <= 0:
            continue
        rskew = np.sqrt(window) * np.sum(seg**3) / rv**1.5
        sig[t] = np.sign(rskew)
    return np.nan_to_num(sig, nan=0.0)


def e71_cox_stuart(mid: np.ndarray, window: int) -> np.ndarray:
    """Bandingkan x_i dengan x_{i+n/2}, uji binomial tanda."""
    n_bars = len(mid)
    sig = np.full(n_bars, np.nan)
    half = window // 2
    for t in range(window, n_bars):
        seg = mid[t - window : t]
        diffs = seg[half:] - seg[:half]
        n_pos = (diffs > 0).sum()
        n_neg = (diffs < 0).sum()
        if n_pos + n_neg == 0:
            continue
        sig[t] = 1.0 if n_pos > n_neg else (-1.0 if n_neg > n_pos else 0.0)
    return np.nan_to_num(sig, nan=0.0)


def e73_runs_test(mid: np.ndarray, window: int) -> np.ndarray:
    """R = jumlah runtun tanda, Z-stat vs harapan acak. sig = -sign(Z)
    (Z tinggi -> terlalu banyak runtun pendek -> mean-reverting -> fade;
    Z rendah -> runtun panjang -> trending -> follow)."""
    r = np.sign(np.diff(mid, prepend=mid[0]))
    n_bars = len(mid)
    sig = np.full(n_bars, np.nan)
    for t in range(window, n_bars):
        seg = r[t - window : t]
        seg_nz = seg[seg != 0]
        if len(seg_nz) < 10:
            continue
        n1 = (seg_nz > 0).sum()
        n2 = (seg_nz < 0).sum()
        runs = 1 + np.sum(seg_nz[1:] != seg_nz[:-1])
        n_tot = n1 + n2
        exp_r = 2 * n1 * n2 / n_tot + 1
        var_r = (2 * n1 * n2 * (2 * n1 * n2 - n_tot)) / (n_tot**2 * (n_tot - 1)) if n_tot > 1 else 0
        if var_r <= 0:
            continue
        z = (runs - exp_r) / np.sqrt(var_r)
        recent_dir = np.sign(mid[t - 1] - mid[t - 5]) if t >= 5 else 0
        sig[t] = recent_dir if z < 0 else (-recent_dir if z > 0 else 0)
    return np.nan_to_num(sig, nan=0.0)


def e80_quantile_regression_slope(mid: np.ndarray, window: int, tau: float) -> np.ndarray:
    """min_b sum rho_tau(y-b*t). Pendekatan iteratif sederhana (IRLS-lite)
    untuk slope regresi kuantil linear pada jendela kausal."""
    n_bars = len(mid)
    sig = np.full(n_bars, np.nan)
    x = np.arange(window, dtype=np.float64)
    for t in range(window, n_bars):
        y = mid[t - window : t]
        b = np.polyfit(x, y, 1)[0]  # OLS start
        for _ in range(5):
            resid = y - b * x
            w = np.where(resid >= 0, tau, 1 - tau) / (np.abs(resid) + 1e-6)
            b = np.sum(w * x * y) / (np.sum(w * x * x) + 1e-12)
        sig[t] = np.sign(b)
    return np.nan_to_num(sig, nan=0.0)


def e81_huber_slope(mid: np.ndarray, window: int, c: float = 1.345) -> np.ndarray:
    """M-estimator Huber untuk slope robust."""
    n_bars = len(mid)
    sig = np.full(n_bars, np.nan)
    x = np.arange(window, dtype=np.float64)
    x_c = x - x.mean()
    for t in range(window, n_bars):
        y = mid[t - window : t]
        b = np.polyfit(x, y, 1)[0]
        for _ in range(5):
            resid = y - b * x
            scale = np.median(np.abs(resid)) * 1.4826 + 1e-9
            u = resid / scale
            w = np.where(np.abs(u) <= c, 1.0, c / np.abs(u))
            b = np.sum(w * x_c * y) / (np.sum(w * x_c * x_c) + 1e-12)
        sig[t] = np.sign(b)
    return np.nan_to_num(sig, nan=0.0)


E_FORMULAS_EXTRA = {
    "E02": e02_vol_scaled_momentum,
    "E03": e03_short_horizon_reversal,
    "E04": e04_session_gap_continuation,
    "E11": e11_variance_ratio_wright,
    "E20": e20_hurst_rs,
    "E50": e50_fft_dominant_period,
    "E54": e54_spectral_entropy,
    "E64": e64_realized_skewness_signal,
    "E71": e71_cox_stuart,
    "E73": e73_runs_test,
    "E80": e80_quantile_regression_slope,
    "E81": e81_huber_slope,
}
