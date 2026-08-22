"""Divisi X -- exit berbasis optimal stopping / deteksi tercepat
(X20-X24), verbatim math from DIVISI_X_EXIT_SL_TP_SIZING.md. Each
function scans a return sequence FROM ENTRY and returns the bar offset
(0-indexed from entry, causal -- only uses r[0..t] to decide at t) where
the rule triggers an exit, or None if it never triggers within the
given sequence (caller falls back to vertical/max_hold exit).

f0/f1 for the sequential tests: null = N(0, sigma^2) (no drift), alt =
N(mu1, sigma^2) (drift of magnitude mu1) -- a directional exit trigger
(detects the position's edge has reversed/decayed), sigma from the
entry-time vol estimate (kept fixed for the trade's duration, consistent
with how the barrier's own sigma is fixed at entry in X01).
"""
import numpy as np


def _log_likelihood_ratio(r: float, mu1: float, sigma: float) -> float:
    """ln[f1(r)/f0(r)] for f0=N(0,sigma^2), f1=N(mu1,sigma^2) -- reduces to
    a linear function of r (standard Gaussian LLR)."""
    if sigma <= 0:
        return 0.0
    return (mu1 * r - 0.5 * mu1**2) / (sigma**2)


def x20_sprt_exit(returns_since_entry: np.ndarray, mu1: float, sigma: float, alpha_err: float, beta_err: float) -> int:
    """LLR_t = sum ln(f1/f0), keluar saat LLR>=ln((1-b)/a) (mengkonfirmasi
    drift positif -- alarm ARAH SALAH terhadap posisi) atau
    LLR<=ln(b/(1-a)) (mengkonfirmasi tidak ada drift / drift negatif --
    edge sudah habis). Returns exit bar offset or -1 if never triggered."""
    upper = np.log((1 - beta_err) / alpha_err)
    lower = np.log(beta_err / (1 - alpha_err))
    llr = 0.0
    for t, r in enumerate(returns_since_entry):
        llr += _log_likelihood_ratio(r, mu1, sigma)
        if llr >= upper or llr <= lower:
            return t
    return -1


def x21_shiryaev_roberts_exit(returns_since_entry: np.ndarray, mu1: float, sigma: float, A: float) -> int:
    """R_t = (1+R_{t-1})*L_t, L_t = likelihood ratio (not log). Keluar saat
    R_t >= A."""
    R = 0.0
    for t, r in enumerate(returns_since_entry):
        llr = _log_likelihood_ratio(r, mu1, sigma)
        L_t = np.exp(np.clip(llr, -50, 50))
        R = (1 + R) * L_t
        if R >= A:
            return t
    return -1


def x22_quickest_detection_exit(returns_since_entry: np.ndarray, mu1: float, sigma: float, h: float) -> int:
    """CUSUM: g_t = max(0, g_{t-1} + ln(f1/f0)), keluar saat g_t >= h."""
    g = 0.0
    for t, r in enumerate(returns_since_entry):
        llr = _log_likelihood_ratio(r, mu1, sigma)
        g = max(0.0, g + llr)
        if g >= h:
            return t
    return -1


def x23_sell_at_ultimate_maximum(prices_since_entry: np.ndarray, c: float) -> int:
    """Keluar saat P_t <= (1-c)*max_{s<=t}(P_s). c dari grid (parameter
    langsung, bukan diestimasi per-trade -- solusi batas bebas penuh perlu
    drift/vol, didekati di sini dengan c tetap dari grid, konsisten dengan
    cara parameter lain di registry dipakai sebagai grid bukan dioptimasi
    per-observasi)."""
    running_max = -np.inf
    for t, p in enumerate(prices_since_entry):
        running_max = max(running_max, p)
        if p <= (1 - c) * running_max:
            return t
    return -1


def x24_free_boundary_exit(prices_since_entry: np.ndarray, mu_hat: float, sigma_hat: float, grid_points: int = 200) -> int:
    """Aproksimasi numerik batas bebas untuk optimal stopping pada
    Brownian bermean-drift, via backward induction. b(t) = ambang
    keuntungan-berjalan terkecil yang membuat berhenti lebih baik
    daripada lanjut. Keluar saat keuntungan berjalan menyentuh b(t)."""
    T = len(prices_since_entry)
    if T < 2:
        return -1
    p0 = prices_since_entry[0]
    running_profit = (prices_since_entry - p0) / p0

    max_profit = np.nanmax(np.abs(running_profit)) if len(running_profit) else 0.01
    x_grid = np.linspace(-max_profit * 2, max_profit * 2, grid_points)
    dx = x_grid[1] - x_grid[0]

    V = np.maximum(x_grid, 0.0)
    boundaries = np.zeros(T)
    for t in range(T - 2, -1, -1):
        drift_steps = np.clip(np.round((mu_hat) / dx).astype(int), -grid_points // 4, grid_points // 4)
        vol_steps = max(1, int(round(sigma_hat / dx)))
        V_next = np.empty_like(V)
        for i in range(grid_points):
            j_up = min(grid_points - 1, i + vol_steps + drift_steps)
            j_dn = max(0, i - vol_steps + drift_steps)
            cont_value = 0.5 * V[j_up] + 0.5 * V[j_dn]
            V_next[i] = max(x_grid[i], cont_value)
        stop_mask = V_next <= x_grid + 1e-9
        boundaries[t] = x_grid[np.argmax(stop_mask)] if stop_mask.any() else max_profit * 2
        V = V_next

    for t in range(T):
        if running_profit[t] >= boundaries[t] and running_profit[t] > 0:
            return t
    return -1
