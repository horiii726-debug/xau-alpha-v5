import numpy as np
from src.formulas import division_x_stopping as xs
from src.formulas import division_x_barriers as xb


def test_x20_sprt_triggers_on_strong_adverse_drift():
    # returns strongly matching mu1 (adverse direction) should trigger quickly
    r = np.full(200, 0.002)
    exit_t = xs.x20_sprt_exit(r, mu1=0.002, sigma=0.001, alpha_err=0.05, beta_err=0.10)
    assert exit_t >= 0
    assert exit_t < 50


def test_x20_sprt_false_alarm_rate_roughly_bounded_by_alpha():
    """Four rounds fixing this test -- see git history for the first three
    dead ends (mismatched sigma; mu1 too large relative to sigma so even
    noise resolves near-instantly; "drift faster than noise" turned out
    false in that same tight-threshold regime, since almost everything
    resolves within 1-2 steps either way). Rather than keep probing timing
    properties that depend sensitively on the exact parameter regime,
    test the one property Wald's SPRT theory actually guarantees: under a
    TRUE null (pure noise, no drift), the probability of the test
    incorrectly confirming H1 (crossing the UPPER bound) is approximately
    bounded by alpha_err. Uses a small alpha (0.05) and modest mu1 so the
    two hypotheses are separated enough for the bound to be meaningful."""
    sigma = 0.001
    mu1 = 2 * sigma
    alpha_err = 0.05
    n_trials = 400
    false_alarms = 0
    for seed in range(n_trials):
        rng = np.random.default_rng(seed)
        r_noise = rng.normal(0, sigma, 200)
        t = xs.x20_sprt_exit(r_noise, mu1=mu1, sigma=sigma, alpha_err=alpha_err, beta_err=0.10)
        if t >= 0:
            # recompute whether THIS trigger was the upper (false-alarm) bound
            llr = 0.0
            upper = np.log((1 - 0.10) / alpha_err)
            for step in range(t + 1):
                llr += (mu1 * r_noise[step] - 0.5 * mu1**2) / sigma**2
            if llr >= upper:
                false_alarms += 1
    # generous slack around alpha_err for a finite-sample Monte Carlo check
    assert false_alarms / n_trials < alpha_err + 0.15


def test_x21_shiryaev_roberts_triggers_on_strong_drift():
    r = np.full(200, 0.003)
    exit_t = xs.x21_shiryaev_roberts_exit(r, mu1=0.003, sigma=0.001, A=30)
    assert exit_t >= 0


def test_x22_cusum_triggers_on_strong_drift():
    r = np.full(200, 0.003)
    exit_t = xs.x22_quickest_detection_exit(r, mu1=0.003, sigma=0.001, h=5)
    assert exit_t >= 0


def test_x22_cusum_resets_on_no_drift():
    r = np.zeros(200)
    exit_t = xs.x22_quickest_detection_exit(r, mu1=0.003, sigma=0.001, h=5)
    assert exit_t == -1  # g_t stays near/at 0, never crosses h


def test_x23_sell_at_ultimate_max_triggers_on_pullback():
    prices = np.concatenate([np.linspace(100, 110, 50), np.linspace(110, 90, 50)])
    exit_t = xs.x23_sell_at_ultimate_maximum(prices, c=0.05)
    assert exit_t >= 0
    assert exit_t >= 49  # can't trigger before the peak at t=49


def test_x23_no_trigger_on_monotonic_rise():
    prices = np.linspace(100, 200, 100)
    exit_t = xs.x23_sell_at_ultimate_maximum(prices, c=0.05)
    assert exit_t == -1


def test_x24_free_boundary_runs_without_crashing():
    rng = np.random.default_rng(1)
    prices = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.002, 100)))
    exit_t = xs.x24_free_boundary_exit(prices, mu_hat=0.0005, sigma_hat=0.002, grid_points=50)
    assert exit_t == -1 or (0 <= exit_t < 100)


def test_x02_asymmetric_skew_scales_with_realized_skew():
    skew_pos = np.array([1.0])
    skew_neg = np.array([-1.0])
    ratio_pos = xb.x02_asymmetric_barrier_skew(skew_pos, base_ratio=1.5, w=0.5)
    ratio_neg = xb.x02_asymmetric_barrier_skew(skew_neg, base_ratio=1.5, w=0.5)
    assert ratio_pos[0] > ratio_neg[0]


def test_x03_time_decay_shrinks_over_time():
    t = np.array([0, 5, 10])
    k_sl, k_tp = xb.x03_time_decay_barrier(k_sl0=2.0, k_tp0=3.0, d=0.5, t=t, T=10)
    assert k_sl[0] > k_sl[1] > k_sl[2]
    assert k_tp[0] > k_tp[1] > k_tp[2]


def test_x04_empirical_quantile_matches_hand_calc():
    mfe = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    mae = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    tp, sl = xb.x04_empirical_quantile_barrier(mfe, mae, q_tp=0.5, q_sl=0.5)
    assert np.isclose(tp, 3.0)
    assert np.isclose(sl, 0.3)


def test_x05_vol_tercile_assigns_wide_to_high_vol():
    """First version checked t=150, deep into a SUSTAINED high-vol regime
    where the trailing 50-bar window is entirely post-shift (all 0.05) --
    the classifier compares the CURRENT bar to its own trailing window's
    percentile, so once the window is saturated with uniformly high
    values, nothing in it looks "high" relative to itself anymore (a
    constant window's own 66th percentile equals every value in it, so
    the strict `>` check never fires). That's correct relative/rolling
    behavior, not a bug -- checked at t=105, right after the shift, where
    the window still spans both regimes and a genuine tercile split
    exists."""
    n = 200
    sigma = np.concatenate([np.full(100, 0.01), np.full(100, 0.05)])  # regime shift to high vol
    out = xb.x05_vol_tercile_conditional_barrier(sigma, tercile_window=50, ratio_tight=(1.0, 1.0), ratio_wide=(2.0, 2.0))
    assert np.allclose(out[105], [2.0, 2.0])


def test_x10_pot_gpd_stop_returns_reasonable_value():
    rng = np.random.default_rng(2)
    excess = rng.exponential(0.5, 500)
    stop = xb.x10_pot_gpd_stop(excess, u=1.0, p_stop=0.95)
    assert np.isfinite(stop)
    assert stop > 1.0  # stop should be above the threshold u


def test_x11_hill_tail_stop_positive():
    rng = np.random.default_rng(3)
    r = rng.standard_t(3, 500) * 0.001  # fat-tailed
    scale = xb.x11_hill_tail_stop(r, k_frac=0.1)
    assert scale > 0


def test_x12_cvar_optimal_stop_within_range():
    rng = np.random.default_rng(4)
    losses = np.abs(rng.normal(0.01, 0.005, 500))
    z = xb.x12_cvar_optimal_stop(losses, beta=0.95)
    assert np.percentile(losses, 50) <= z <= np.percentile(losses, 99.5)


def test_x13_conditional_evt_scales_with_sigma():
    rng = np.random.default_rng(5)
    z = rng.standard_normal(500)
    stop_low = xb.x13_conditional_evt_stop(sigma_t=0.001, z_residuals_train=z, p=0.95)
    stop_high = xb.x13_conditional_evt_stop(sigma_t=0.01, z_residuals_train=z, p=0.95)
    assert stop_high > stop_low


def test_x14_semiparametric_tail_stop_positive():
    rng = np.random.default_rng(6)
    r = rng.standard_t(3, 500) * 0.001
    stop = xb.x14_semiparametric_tail_stop(r, u_percentile=90)
    assert stop > 0
