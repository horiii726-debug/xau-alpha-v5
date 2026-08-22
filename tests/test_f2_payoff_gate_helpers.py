import sys
sys.path.insert(0, "/workspace/data")

import numpy as np
from run_f2_payoff_gate import demean_series, sign_flipped_series, _log_shift_ohlc


def test_demean_series_preserves_length():
    mid = np.array([100.0, 101.0, 99.0, 102.0, 103.0, 104.0, 102.5])
    d = demean_series(mid, window_minutes=2)
    assert len(d) == len(mid)


def test_sign_flipped_series_preserves_length():
    """Regression test: first version dropped the first element (np.diff
    shrinks by 1, and unlike demean_series it wasn't padded back), which
    crashed _log_shift_ohlc with a shape mismatch the first time the F2
    script was smoke-tested against real partial data."""
    mid = np.array([100.0, 101.0, 99.0, 102.0, 103.0, 104.0, 102.5])
    s = sign_flipped_series(mid)
    assert len(s) == len(mid)


def test_sign_flipped_series_actually_flips_direction():
    mid = np.array([100.0, 102.0, 101.0, 105.0])  # net upward drift
    flipped = sign_flipped_series(mid)
    # original ends up, flipped should end down (or at least not exceed original's net move)
    orig_total_logret = np.log(mid[-1] / mid[0])
    flipped_total_logret = np.log(flipped[-1] / flipped[0])
    assert np.sign(orig_total_logret) != np.sign(flipped_total_logret) or np.isclose(flipped_total_logret, 0)


def test_log_shift_ohlc_preserves_lengths_and_relative_order():
    mid = np.array([100.0, 101.0, 102.0])
    high = mid + 0.5
    low = mid - 0.5
    open_ = mid - 0.1
    new_mid = mid * 1.01  # uniform shift up
    nh, nl, no = _log_shift_ohlc(mid, high, low, open_, new_mid)
    assert len(nh) == len(nl) == len(no) == len(mid)
    assert np.all(nh > nl)  # high still above low after shift
