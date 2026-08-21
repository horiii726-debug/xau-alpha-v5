import numpy as np
from src.formulas import division_x_sizing as xs


def test_x30_kelly_matches_hand_calc():
    # classic textbook example: p=0.6, b=1 (even money) -> f* = 0.2
    f = xs.x30_kelly_full(0.6, 1.0)
    assert np.isclose(f, 0.2)


def test_x30_kelly_negative_edge_gives_negative_f():
    f = xs.x30_kelly_full(0.4, 1.0)
    assert f < 0  # negative edge -> Kelly says don't bet (or bet against)


def test_x31_fractional_kelly_scales_linearly():
    full = xs.x30_kelly_full(0.6, 1.0)
    half = xs.x31_fractional_kelly(0.6, 1.0, lam=0.5)
    assert np.isclose(half, full * 0.5)


def test_x32_vol_targeting_inverse_relationship():
    sigma = np.array([0.001, 0.002, 0.0005])
    size = xs.x32_volatility_targeting(sigma, target_vol_bps=10.0, size_cap=100.0)
    # higher sigma -> smaller size
    assert size[1] < size[0] < size[2]


def test_x32_respects_size_cap():
    sigma = np.array([0.00001])  # tiny vol -> huge uncapped size
    size = xs.x32_volatility_targeting(sigma, target_vol_bps=100.0, size_cap=3.0)
    assert size[0] == 3.0


def test_x33_drawdown_constrained_full_size_at_peak():
    equity = np.array([100.0, 105.0, 110.0])  # always at new peak -> DD=0
    f = xs.x33_drawdown_constrained_sizing(equity, dd_limit_pct=10.0, gamma=1.0, f_max=1.0)
    assert np.allclose(f, 1.0)


def test_x33_drawdown_constrained_shrinks_at_drawdown_limit():
    equity = np.array([100.0, 90.0])  # 10% drawdown from peak
    f = xs.x33_drawdown_constrained_sizing(equity, dd_limit_pct=10.0, gamma=1.0, f_max=1.0)
    assert np.isclose(f[1], 0.0, atol=1e-6)  # at the limit -> size shrinks to 0


def test_x33_never_negative():
    equity = np.array([100.0, 50.0])  # 50% drawdown, past a 10% limit
    f = xs.x33_drawdown_constrained_sizing(equity, dd_limit_pct=10.0, gamma=1.0, f_max=1.0)
    assert np.all(f >= 0)


def test_x34_cdar_zero_f_always_feasible():
    rng = np.random.default_rng(0)
    trade_returns = rng.normal(0.001, 0.02, 500)
    f = xs.x34_cdar_sizing(trade_returns, beta=0.95, dd_limit_pct=5.0)
    assert f >= 0.0


def test_x34_tighter_limit_gives_smaller_or_equal_f():
    rng = np.random.default_rng(1)
    trade_returns = rng.normal(0.001, 0.02, 500)
    f_loose = xs.x34_cdar_sizing(trade_returns, beta=0.95, dd_limit_pct=20.0)
    f_tight = xs.x34_cdar_sizing(trade_returns, beta=0.95, dd_limit_pct=5.0)
    assert f_tight <= f_loose


def test_x35_positive_edge_gives_positive_f():
    rng = np.random.default_rng(2)
    trade_returns = rng.normal(0.01, 0.02, 300)  # clear positive edge
    f = xs.x35_risk_of_ruin_constrained(trade_returns, epsilon=0.05, target_R=2.0, rng=np.random.default_rng(3))
    assert f > 0
