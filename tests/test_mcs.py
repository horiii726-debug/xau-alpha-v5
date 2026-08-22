import numpy as np
from src.validation.mcs import qlike_loss, model_confidence_set


def test_qlike_zero_at_perfect_forecast():
    rv = np.array([1.0, 2.0, 0.5])
    loss = qlike_loss(rv, rv)
    assert np.allclose(loss, 0.0, atol=1e-10)


def test_qlike_positive_for_imperfect_forecast():
    rv = np.array([1.0, 2.0])
    forecast = np.array([2.0, 1.0])
    loss = qlike_loss(rv, forecast)
    assert np.all(loss > 0)


def test_mcs_eliminates_clearly_worse_model():
    rng = np.random.default_rng(0)
    n = 2000
    good = np.abs(rng.normal(0.1, 0.05, n))  # low loss
    bad = np.abs(rng.normal(2.0, 0.3, n))  # clearly higher loss
    result = model_confidence_set({"good": good, "bad": bad}, {"good": 1, "bad": 1}, alpha=0.10, n_boot=300, rng=rng)
    assert "bad" in [e[0] for e in result["eliminated"]]
    assert "good" in result["survivors"]


def test_mcs_keeps_statistically_indistinguishable_models_and_tie_breaks_simplest():
    rng = np.random.default_rng(1)
    n = 2000
    a = np.abs(rng.normal(0.5, 0.1, n))
    b = a + rng.normal(0, 0.001, n)  # nearly identical performance
    result = model_confidence_set({"complex": a, "simple": b}, {"complex": 5, "simple": 1}, alpha=0.10, n_boot=300, rng=rng)
    assert set(result["survivors"]) == {"complex", "simple"}
    assert result["tie_break_simplest"] == "simple"


def test_mcs_too_few_observations_returns_all_as_survivors():
    result = model_confidence_set({"a": np.array([1.0, 2.0]), "b": np.array([3.0, 4.0])}, {"a": 1, "b": 1})
    assert result["survivors"] == ["a", "b"]
    assert "note" in result
