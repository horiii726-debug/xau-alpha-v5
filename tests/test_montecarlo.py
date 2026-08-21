import numpy as np
from src.validation import montecarlo as mc


def test_mc1_permutation_flags_signal_that_truly_predicts_returns():
    rng = np.random.default_rng(0)
    bar_returns = rng.normal(0.0, 0.01, size=2000)
    # a signal genuinely correlated with same-bar return (stand-in for a
    # real predictive signal correctly paired with its outcome)
    signal = np.sign(bar_returns) * 1.0
    result = mc.mc1_permutation(signal, bar_returns, n=500, block_size=10, rng=np.random.default_rng(1))
    assert result["gate_pass"] is True
    assert result["percentile"] >= 95


def test_mc1_permutation_does_not_flag_signal_uncorrelated_with_returns():
    rng = np.random.default_rng(2)
    bar_returns = rng.normal(0.0, 0.01, size=2000)
    unrelated_signal = np.random.default_rng(99).choice([-1.0, 1.0], size=2000)
    result = mc.mc1_permutation(unrelated_signal, bar_returns, n=500, block_size=10, rng=np.random.default_rng(3))
    assert result["percentile"] < 95


def test_mc1_permuting_a_realized_return_series_directly_would_be_vacuous():
    """Regression guard for the original design bug: summing a PERMUTED
    but otherwise fixed set of numbers always returns the same sum, so
    MC1 must never permute a candidate's own already-realized trade
    returns directly -- it must permute the underlying bar returns and
    re-apply the (fixed) signal each time."""
    trade_returns = np.random.default_rng(5).normal(0.02, 0.01, size=300)
    rng = np.random.default_rng(6)
    for _ in range(5):
        permuted = rng.permutation(trade_returns)
        assert np.isclose(permuted.sum(), trade_returns.sum())


def test_mc2_missing_lookup_does_not_fabricate_breach_prob():
    trade_returns = np.random.default_rng(4).normal(0.001, 0.01, size=200)
    result = mc.mc2_survival_paths(trade_returns, n_paths=100, max_total_drawdown_pct=None)
    assert result["params_status"] == "UNVERIFIED_LOOKUP_MISSING"
    assert all(v is None for v in result["breach_prob"].values())


def test_mc2_computes_breach_prob_when_params_available():
    rng = np.random.default_rng(5)
    trade_returns = rng.normal(0.0005, 0.02, size=300)
    result = mc.mc2_survival_paths(
        trade_returns, n_paths=200, max_daily_loss_pct=5.0, max_total_drawdown_pct=10.0, profit_target_pct=10.0, rng=rng
    )
    assert result["params_status"] == "OK"
    assert 0.0 <= result["breach_prob"][250] <= 1.0


def test_mc4_dsr_penalizes_more_trials():
    trade_returns = np.random.default_rng(6).normal(0.01, 0.02, size=500)
    low_trials = mc.mc4_deflated_sharpe(trade_returns, n_trials=5, trial_sharpe_std=0.1)
    high_trials = mc.mc4_deflated_sharpe(trade_returns, n_trials=500, trial_sharpe_std=0.1)
    assert high_trials["dsr"] <= low_trials["dsr"]


def test_mc5_detects_sign_flip():
    def evaluate(params):
        # expectancy crosses zero as 'edge' param shrinks below 0
        return params["edge"] - 0.5

    base = {"edge": 1.0}
    result = mc.mc5_parameter_perturbation(evaluate, base, perturb_pcts=(-0.6, -0.3, 0.3, 0.6), n_combos=10)
    assert result["sign_flips"] > 0
    assert result["gate_pass"] is False


def test_mc5_no_flip_when_robust():
    def evaluate(params):
        return params["edge"] * 10  # always positive for positive edge param, never crosses 0

    base = {"edge": 1.0}
    result = mc.mc5_parameter_perturbation(evaluate, base, perturb_pcts=(-0.2, -0.1, 0.1, 0.2), n_combos=10)
    assert result["sign_flips"] == 0
    assert result["gate_pass"] is True
