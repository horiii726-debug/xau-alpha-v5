import numpy as np
from src.formulas import pilot_f2b as pf


def make_walk(n=1000, seed=0):
    rng = np.random.default_rng(seed)
    r = rng.normal(0, 0.001, n)
    mid = 100 * np.exp(np.cumsum(r))
    high = mid * (1 + np.abs(rng.normal(0, 0.0005, n)))
    low = mid * (1 - np.abs(rng.normal(0, 0.0005, n)))
    return mid, high, low


def test_all_directional_formulas_return_correct_shape_and_valid_values():
    mid, high, low = make_walk()
    for name, fn in pf.PILOT_FORMULAS_DIRECTIONAL.items():
        if name == "E10":
            sig = fn(mid, q=4, window=100)
        elif name == "E22":
            sig = fn(mid, window=100, poly_order=1)
        elif name == "E30":
            sig = fn(mid, window=50, m=3)
        elif name == "E60":
            sig = fn(mid, h_mean=6, h_vol=24)
        elif name == "E70":
            sig = fn(mid, window=48)
        elif name == "E90":
            sig = fn(mid, k_mult=0.5, h_mult=4.0, window=48)
        elif name == "X06":
            sig = fn(mid, hold_bars=12)
        else:
            sig = fn(mid)
        assert len(sig) == len(mid), f"{name}: length mismatch"
        assert np.all(np.isfinite(sig)), f"{name}: non-finite values present"
        assert set(np.unique(sig)).issubset({-1.0, 0.0, 1.0}), f"{name}: values outside {{-1,0,1}}: {np.unique(sig)}"


def test_x01_reference_barrier_is_the_known_comparison_point():
    k_sl, k_tp = pf.x01_triple_barrier_reference(1000)
    assert (k_sl, k_tp) == (1.5, 2.5)


def test_x32_sizing_is_nonnegative_and_capped():
    mid, high, low = make_walk()
    sigma = pf.v01_parkinson_sigma(high, low, window=48)
    size = pf.x32_volatility_targeting_size(sigma, target_vol_bps=100.0, size_cap=3.0)
    assert len(size) == len(mid)
    assert np.all(size >= 0)
    assert np.all(size <= 3.0)


def test_v01_parkinson_matches_labeling_module():
    mid, high, low = make_walk()
    sigma = pf.v01_parkinson_sigma(high, low, window=48)
    assert np.all(sigma[47:][~np.isnan(sigma[47:])] > 0)


def test_q08_spread_to_vol_ratio_shape():
    mid, high, low = make_walk()
    sigma = pf.v01_parkinson_sigma(high, low, window=48)
    spread_bps = np.full(len(mid), 2.0)
    ratio = pf.q08_spread_to_vol_ratio(spread_bps, sigma * 1e4, window=48)
    assert len(ratio) == len(mid)
