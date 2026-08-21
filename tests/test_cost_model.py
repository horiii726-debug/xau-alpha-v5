import numpy as np
from src.costs.cost_model import slippage_bps, realized_spread_cost_bps, total_cost_bps, kappa, SCENARIOS


def test_worst_scenario_has_highest_penalty():
    assert SCENARIOS["worst"]["extra_penalty"] > SCENARIOS["base"]["extra_penalty"]
    assert SCENARIOS["worst"]["spread_percentile"] > SCENARIOS["base"]["spread_percentile"] > SCENARIOS["best"]["spread_percentile"]


def test_slippage_formula():
    spread = np.array([2.0])
    sigma = np.array([10.0])
    slip = slippage_bps(spread, sigma, alpha=1.5, beta=0.5)
    assert np.isclose(slip[0], 1.5 * 2.0 + 0.5 * 10.0)


def test_missing_lookup_flagged_not_defaulted():
    spread = np.array([2.0, 2.5])
    sigma = np.array([10.0, 12.0])
    result = total_cost_bps(spread, sigma, "worst", markup_prop_firm_pct=None, commission_usd_per_lot=None, notional_usd_per_lot=100000)
    assert "markup_prop_firm_pct" in result["missing_lookups"]
    assert "commission_usd_per_lot" in result["missing_lookups"]
    assert result["cost_verified"] is False
    # the measured-only component should still be usable
    assert (result["cost_bps_measured_component_only"] > 0).all()


def test_kappa_forbids_zero_division_returns_inf():
    assert kappa(5.0, 0.0) == float("inf")


def test_kappa_ratio():
    assert np.isclose(kappa(4.0, 2.0), 2.0)
