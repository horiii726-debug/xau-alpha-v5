import numpy as np
from src.stats import nulls


def make_random_walk(n=5000, seed=0, drift=0.0, sigma=0.001):
    rng = np.random.default_rng(seed)
    r = rng.normal(drift, sigma, size=n)
    mid = 100 * np.exp(np.cumsum(r))
    return mid


def test_b01_b06_buy_and_hold_are_identical():
    mid = make_random_walk()
    assert np.allclose(nulls.b01_buy_and_hold(mid), nulls.b06_always_long(mid))


def test_b07_always_short_is_negation_of_b06():
    mid = make_random_walk()
    assert np.allclose(nulls.b07_always_short(mid), -nulls.b06_always_long(mid))


def test_b05_coin_flip_zero_mean_on_zero_drift_walk():
    mid = make_random_walk(n=20000, drift=0.0, seed=1)
    rng = np.random.default_rng(42)
    ret = nulls.b05_coin_flip(mid, rng)
    # zero-drift random walk, arah acak independen dari return realized -> mean ~ 0
    assert abs(ret.mean()) < 0.001


def test_b09_perfect_foresight_beats_everything_by_construction():
    mid = make_random_walk(n=2000, seed=2)
    foresight = nulls.b09_perfect_foresight(mid)
    b01 = nulls.b01_buy_and_hold(mid)
    assert (foresight >= 0).all()  # abs() by construction, always non-negative
    assert foresight.sum() > b01.sum()  # foresight strictly dominates a directional null


def test_b03_block_permuted_preserves_total_variance_roughly():
    mid = make_random_walk(n=5000, seed=3)
    rng = np.random.default_rng(7)
    original = np.diff(np.log(mid))
    permuted = nulls.b03_block_permuted(mid, block_size=20, rng=rng)
    assert abs(original.std() - permuted.std()) < 0.2 * original.std()


def test_null_correlation_matrix_b01_b06_perfectly_correlated():
    mid = make_random_walk(n=3000, seed=4)
    b01 = nulls.b01_buy_and_hold(mid)
    b06 = nulls.b06_always_long(mid)
    corr, k_eff = nulls.null_correlation_matrix({"B01": b01, "B06": b06})
    assert np.isclose(corr.loc["B01", "B06"], 1.0, atol=1e-6)
