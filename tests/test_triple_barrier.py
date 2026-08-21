import numpy as np
from src.labeling.triple_barrier import triple_barrier_labels, parkinson_sigma, breakeven_mekanis


def test_breakeven_mekanis_symmetric_case():
    assert np.isclose(breakeven_mekanis(1.0, 1.0), 0.5)
    assert np.isclose(breakeven_mekanis(1.0, 2.0), 1 / 3)


def test_parkinson_sigma_positive_and_causal():
    n = 200
    rng = np.random.default_rng(0)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.001, n)))
    high = close * (1 + np.abs(rng.normal(0, 0.001, n)))
    low = close * (1 - np.abs(rng.normal(0, 0.001, n)))
    sigma = parkinson_sigma(high, low, window=20)
    assert np.all(np.isnan(sigma[:19]))  # not enough history yet
    assert np.all(sigma[19:] > 0)


def test_long_tp_hit_before_sl():
    # entry at bar 5, open=100. TP well above entry price, price rallies straight to it at bar 7.
    n = 20
    open_ = np.full(n, 100.0)
    high = np.full(n, 100.5)
    low = np.full(n, 99.5)
    close = np.full(n, 100.0)
    # bar 7 spikes up to trigger TP (k_tp=1, sigma=0.02 -> TP=102)
    high[7] = 103.0
    sigma = np.full(n, 0.02)

    result = triple_barrier_labels(
        open_, high, low, close,
        entry_bar_idx=np.array([5]), direction=np.array([1]), sigma=sigma,
        k_sl=1.0, k_tp=1.0, max_hold_bars=10,
    )
    assert result.outcome[0] == 1  # TP
    assert result.bars_held[0] == 3  # bars 5,6,7 -> held 3 bars
    assert result.ret[0] > 0


def test_short_sl_hit():
    n = 20
    open_ = np.full(n, 100.0)
    high = np.full(n, 100.5)
    low = np.full(n, 99.5)
    close = np.full(n, 100.0)
    # short entry: SL triggers if price RISES past entry*(1+k_sl*sigma)
    high[6] = 103.0
    sigma = np.full(n, 0.02)

    result = triple_barrier_labels(
        open_, high, low, close,
        entry_bar_idx=np.array([5]), direction=np.array([-1]), sigma=sigma,
        k_sl=1.0, k_tp=1.0, max_hold_bars=10,
    )
    assert result.outcome[0] == -1  # SL
    assert result.ret[0] < 0


def test_vertical_exit_when_neither_barrier_touched():
    n = 20
    open_ = np.full(n, 100.0)
    high = np.full(n, 100.1)
    low = np.full(n, 99.9)
    close = np.full(n, 100.0)
    close[9] = 100.05  # small drift, exit price at vertical bar
    sigma = np.full(n, 0.05)  # wide barriers, won't be touched by 0.1% moves

    result = triple_barrier_labels(
        open_, high, low, close,
        entry_bar_idx=np.array([5]), direction=np.array([1]), sigma=sigma,
        k_sl=1.0, k_tp=1.0, max_hold_bars=5,
    )
    assert result.outcome[0] == 0  # vertical
    assert result.bars_held[0] == 5


def test_missing_sigma_produces_no_trade():
    n = 10
    open_ = np.full(n, 100.0)
    high = np.full(n, 101.0)
    low = np.full(n, 99.0)
    close = np.full(n, 100.0)
    sigma = np.full(n, np.nan)
    result = triple_barrier_labels(
        open_, high, low, close,
        entry_bar_idx=np.array([5]), direction=np.array([1]), sigma=sigma,
        k_sl=1.0, k_tp=1.0, max_hold_bars=3,
    )
    assert result.outcome[0] == 0
    assert result.ret[0] == 0.0
