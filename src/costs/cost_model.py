"""Cost model per 02_DATA_DAN_BIAYA.md. Unit: bps. All gates evaluated on
the `worst` scenario. cost_verified stays False throughout v5 -- no fill
data exists to calibrate slippage against.
"""
from dataclasses import dataclass, field

import numpy as np

SCENARIOS = {
    "best": {"spread_percentile": 50, "slippage_alpha": 0.5, "slippage_beta": 0.00, "extra_penalty": 1.0},
    "base": {"spread_percentile": 75, "slippage_alpha": 1.0, "slippage_beta": 0.25, "extra_penalty": 1.0},
    "worst": {"spread_percentile": 90, "slippage_alpha": 1.5, "slippage_beta": 0.50, "extra_penalty": 1.5},
}
GATE_SCENARIO = "worst"


@dataclass
class CostModelInputs:
    markup_prop_firm_pct: float | None = None  # LOOKUP
    commission_usd_per_lot_roundtrip: float | None = None  # LOOKUP
    swap_long_points: float | None = None  # LOOKUP
    swap_short_points: float | None = None  # LOOKUP
    triple_swap_day: str | None = None  # LOOKUP, usually Wednesday for metals
    status_notes: dict = field(default_factory=dict)


def slippage_bps(spread_bps: np.ndarray, sigma_bar_bps: np.ndarray, alpha: float, beta: float) -> np.ndarray:
    """slippage_bps = alpha * spread_bps_saat_eksekusi + beta * sigma_bar_bps"""
    return alpha * spread_bps + beta * sigma_bar_bps


def realized_spread_cost_bps(spread_at_exec_bps: np.ndarray, slip_bps: np.ndarray) -> np.ndarray:
    """biaya_realized_bps = (2 * s_eksekusi + slippage_model) / harga_bar * 1e4
    -- here spread_at_exec_bps is ALREADY in bps (spread/price*1e4), so the
    round-trip cost is simply 2x that spread plus the slippage bps."""
    return 2 * spread_at_exec_bps + slip_bps


def total_cost_bps(
    spread_bps: np.ndarray,
    sigma_bar_bps: np.ndarray,
    scenario: str,
    markup_prop_firm_pct: float | None,
    commission_usd_per_lot: float | None,
    notional_usd_per_lot: float,
) -> dict:
    """Combine measured spread + modeled slippage + (if available) prop
    firm markup and commission into a total round-trip cost in bps. Any
    LOOKUP field that's still None is EXCLUDED from the number and flagged,
    never defaulted to zero or guessed."""
    s = SCENARIOS[scenario]
    slip = slippage_bps(spread_bps, sigma_bar_bps, s["slippage_alpha"], s["slippage_beta"])
    base_cost = realized_spread_cost_bps(spread_bps, slip) * s["extra_penalty"]

    missing = []
    total = base_cost.copy()
    if markup_prop_firm_pct is not None:
        total = total + markup_prop_firm_pct * 1e2  # pct -> bps
    else:
        missing.append("markup_prop_firm_pct")
    if commission_usd_per_lot is not None:
        commission_bps = commission_usd_per_lot / notional_usd_per_lot * 1e4
        total = total + commission_bps
    else:
        missing.append("commission_usd_per_lot")

    return {
        "cost_bps_measured_component_only": base_cost,
        "cost_bps_with_available_lookups": total,
        "missing_lookups": missing,
        "cost_verified": False,
        "scenario": scenario,
    }


def kappa(cost_bps_roundtrip: float, realized_vol_bps_over_actual_holding: float) -> float:
    """kappa = biaya_round_trip_bps / volatilitas_pada_durasi_holding_NYATA_bps.
    MUST be computed from measured hit-barrier duration, never from
    max_hold (forbid_max_hold: true) -- caller is responsible for passing
    a volatility already scaled to the ACTUAL realized holding duration."""
    if realized_vol_bps_over_actual_holding <= 0:
        return float("inf")
    return cost_bps_roundtrip / realized_vol_bps_over_actual_holding
