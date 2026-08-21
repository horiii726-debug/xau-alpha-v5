"""Divisi X -- Position sizing family (X30-X35), verbatim math from
DIVISI_X_EXIT_SL_TP_SIZING.md. All estimated from TRAIN-fold data only
(caller's responsibility to pass only historical/train-window p,b,f_max
etc -- §L3: fit only on train fold).
"""
import numpy as np


def x30_kelly_full(p_win: float, payoff_ratio_b: float) -> float:
    """f* = (p*b - q)/b, p=P(menang), q=1-p, b=rasio payoff.
    SEMUA diestimasi dari fold LATIH saja (caller's responsibility)."""
    q = 1 - p_win
    if payoff_ratio_b <= 0:
        return 0.0
    f = (p_win * payoff_ratio_b - q) / payoff_ratio_b
    return f


def x31_fractional_kelly(p_win: float, payoff_ratio_b: float, lam: float) -> float:
    """f = lambda * f_Kelly. lambda dari grid, BUKAN dioptimalkan ke hasil."""
    f_kelly = x30_kelly_full(p_win, payoff_ratio_b)
    return lam * f_kelly


def x32_volatility_targeting(sigma_hat: np.ndarray, target_vol_bps: float, size_cap: float) -> np.ndarray:
    """size_t = target_vol / sigma_hat_t, dibatasi size_max."""
    sigma_bps = sigma_hat * 1e4
    with np.errstate(invalid="ignore", divide="ignore"):
        size = target_vol_bps / sigma_bps
    return np.clip(np.nan_to_num(size, nan=0.0, posinf=size_cap), 0, size_cap)


def x33_drawdown_constrained_sizing(equity_curve: np.ndarray, dd_limit_pct: float, gamma: float, f_max: float) -> np.ndarray:
    """f_t = f_max * (1 - DD_t/DD_limit)^gamma, DD_t = drawdown berjalan
    dari puncak ekuitas. WAJIB -- bentuk matematis persis aturan drawdown
    prop firm, tidak boleh dipangkas (§tangga_pemangkasan)."""
    peak = np.maximum.accumulate(equity_curve)
    dd_pct = np.where(peak > 0, (peak - equity_curve) / peak * 100, 0.0)
    ratio = np.clip(1 - dd_pct / dd_limit_pct, 0, None)
    return f_max * ratio**gamma


def x34_cdar_sizing(trade_returns: np.ndarray, beta: float, dd_limit_pct: float, f_grid: np.ndarray = None) -> float:
    """min f sedemikian CDaR_beta(f) <= batas. CDaR = rata-rata drawdown
    pada (1-beta) skenario terburuk. Grid-search over f (caller can pass
    a finer f_grid; default coarse grid here for a self-contained utility)."""
    if f_grid is None:
        f_grid = np.linspace(0.01, 2.0, 100)
    best_f = 0.0
    for f in f_grid:
        scaled = trade_returns * f
        equity = np.cumprod(1 + scaled)
        peak = np.maximum.accumulate(equity)
        dd = (peak - equity) / peak * 100
        n_tail = max(1, int(len(dd) * (1 - beta)))
        cdar = np.sort(dd)[-n_tail:].mean()
        if cdar <= dd_limit_pct:
            best_f = f
        else:
            break
    return best_f


def x35_risk_of_ruin_constrained(trade_returns: np.ndarray, epsilon: float, target_R: float, f_grid: np.ndarray = None, n_paths: int = 2000, rng: np.random.Generator = None) -> float:
    """Pilih f terbesar sedemikian P(ruin sebelum target) <= epsilon,
    dihitung lewat simulasi bootstrap jalur (MC2-style)."""
    rng = rng or np.random.default_rng()
    if f_grid is None:
        f_grid = np.linspace(0.01, 2.0, 50)
    n_trades = len(trade_returns)
    best_f = 0.0
    for f in sorted(f_grid):
        ruin_count = 0
        for _ in range(n_paths):
            order = rng.integers(0, n_trades, size=n_trades * 3)
            path_returns = trade_returns[order] * f
            equity = np.cumprod(1 + path_returns)
            ruined = np.any(equity <= 1e-6)
            hit_target = np.any(equity >= target_R)
            if ruined and (not hit_target or np.argmax(equity <= 1e-6) < np.argmax(equity >= target_R)):
                ruin_count += 1
        p_ruin = ruin_count / n_paths
        if p_ruin <= epsilon:
            best_f = f
        else:
            break
    return best_f
