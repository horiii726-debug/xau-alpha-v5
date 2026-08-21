import numpy as np
from src.formulas import division_q as q


def make_market(n=2000, seed=0):
    rng = np.random.default_rng(seed)
    r = rng.normal(0, 0.0008, n)
    close = 100 * np.exp(np.cumsum(r))
    high = close * (1 + np.abs(rng.normal(0, 0.0004, n)))
    low = close * (1 - np.abs(rng.normal(0, 0.0004, n)))
    spread = np.abs(rng.normal(2.0, 0.5, n))  # bps-like synthetic spread series
    return close, high, low, spread


def test_q01_roll_spread_nonneg_where_defined():
    close, high, low, spread = make_market()
    # induce genuine negative lag-1 autocovariance (bid-ask bounce) so Roll is defined:
    # alternate a small +/- bounce on top of the walk
    bounce = np.array([0.0002 if i % 2 == 0 else -0.0002 for i in range(len(close))])
    close_bounced = close * (1 + bounce)
    s = q.q01_roll_spread(close_bounced, window=100)
    valid = s[~np.isnan(s)]
    assert len(valid) > 0
    assert np.all(valid >= 0)


def test_q02_corwin_schultz_nonneg():
    close, high, low, spread = make_market()
    s = q.q02_corwin_schultz(high, low, window=10)
    valid = s[~np.isnan(s)]
    assert len(valid) > 0
    assert np.all(valid >= 0)


def test_q03_abdi_ranaldo_nonneg():
    close, high, low, spread = make_market()
    s = q.q03_abdi_ranaldo(high, low, close, window=96)
    valid = s[~np.isnan(s)]
    assert len(valid) > 0
    assert np.all(valid >= 0)


def test_q04_amihud_nonneg():
    close, high, low, spread = make_market()
    n_ticks = np.full(len(close), 50.0)
    illiq = q.q04_amihud_illiquidity(close, n_ticks, window=48)
    valid = illiq[~np.isnan(illiq)]
    assert len(valid) > 0
    assert np.all(valid >= 0)


def test_q06_spread_velocity_zero_for_constant_spread():
    spread = np.full(500, 2.0)
    v = q.q06_spread_velocity(spread, k=3)
    valid = v[~np.isnan(v)]
    assert np.allclose(valid, 0.0)


def test_q07_spread_acceleration_zero_for_linear_spread():
    spread = np.linspace(1.0, 5.0, 500)  # linear trend -> zero acceleration
    a = q.q07_spread_acceleration(spread, k=5)
    valid = a[~np.isnan(a)]
    assert np.allclose(valid, 0.0, atol=1e-8)


def test_q08_ratio_scales_correctly():
    spread_bps = np.array([2.0, 4.0])
    sigma_bps = np.array([1.0, 2.0])
    ratio = q.q08_spread_to_vol_ratio(spread_bps, sigma_bps)
    assert np.allclose(ratio, [2.0, 2.0])


def test_q09_resiliency_detects_recovery_time():
    n = 300
    spread = np.full(n, 2.0)
    spread[100] = 20.0  # spike above p90 of trailing window
    spread[101:105] = 15.0
    spread[105:] = 2.0  # recovers to p50 at bar 105
    tau = q.q09_spread_resiliency(spread, ref_window=96)
    # at t=100, spike -- should measure recovery time to bar 105ish
    assert not np.isnan(tau[100])
    assert tau[100] > 0


def test_q10_percentile_gate_binary():
    close, high, low, spread = make_market()
    gate = q.q10_spread_percentile_gate(spread, percentile=50, ref_window=96)
    valid_region = gate[96:]
    assert set(np.unique(valid_region)).issubset({0.0, 1.0})
    # roughly half should pass a 50th percentile gate
    assert 0.3 < valid_region.mean() < 0.7


def test_q11_regime_break_bounded_0_1():
    close, high, low, spread = make_market()
    d = q.q11_spread_regime_break(spread, window=200)
    valid = d[~np.isnan(d)]
    assert len(valid) > 0
    assert np.all(valid >= 0)
    assert np.all(valid <= 1.0)


def test_q12_realized_spread_cost_additive():
    s = np.array([2.0, 3.0])
    slip = np.array([1.0, 1.5])
    cost = q.q12_realized_spread_cost(s, slip)
    assert np.allclose(cost, [5.0, 7.5])
