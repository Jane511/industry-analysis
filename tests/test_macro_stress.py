"""Tests for the macro-driven stress engine (MACRO-STRESS).

Pure-function tests on committed inputs only (config + committed demo book);
no network or staged public data required.
"""
from __future__ import annotations

import pandas as pd
import pytest

from src.config import RAW_DIR
from src.overlays.macro_stress_core import (
    PARAMETERS,
    build_demo_portfolio_stress,
    build_demo_portfolio_summary,
    build_macro_scenario_paths,
    build_portfolio_macro_sensitivity,
    compute_segment_multipliers,
    load_macro_config,
)

SCEN_ORDER = {"base": 0, "mild": 1, "moderate": 2, "severe": 3}


@pytest.fixture(scope="module")
def cfg() -> dict:
    return load_macro_config()


def test_panel_complete_12x4(cfg) -> None:
    paths = build_macro_scenario_paths(cfg)
    assert len(cfg["variables"]) == 12
    assert set(paths["scenario"]) == {"base", "mild", "moderate", "severe"}
    # one row per variable x scenario, no gaps
    assert len(paths) == 12 * 4
    assert paths.groupby("variable")["scenario"].nunique().eq(4).all()


def test_panel_tags_real_vs_assumption(cfg) -> None:
    paths = build_macro_scenario_paths(cfg)
    assert (paths["source_or_assumption"].str.len() > 0).all()
    # the four CRE-ish variables are honestly tagged as assumptions
    assumed = set(paths.loc[paths["source_or_assumption"] == "assumption", "variable"])
    assert {"commercial_property_prices", "vacancy_rate", "cre_rents", "cre_cap_rates"} <= assumed


def test_base_shocks_are_zero(cfg) -> None:
    paths = build_macro_scenario_paths(cfg)
    base = paths[paths["scenario"] == "base"]
    assert (base["shock"] == 0).all()
    assert (base["shock_norm"] == 0).all()


def test_sensitivity_coverage_min_three_drivers(cfg) -> None:
    sens = build_portfolio_macro_sensitivity(cfg)
    counts = sens.groupby(["segment", "parameter"]).size()
    assert (counts >= 3).all(), f"some segment/parameter has <3 drivers:\n{counts[counts < 3]}"
    # every segment covers all three parameters
    for segment in cfg["portfolio_sensitivities"]:
        assert set(sens[sens.segment == segment]["parameter"]) == set(PARAMETERS)


def test_sensitivity_weights_sum_to_one(cfg) -> None:
    sens = build_portfolio_macro_sensitivity(cfg)
    sums = sens.groupby(["segment", "parameter"])["sensitivity_weight"].sum()
    assert (abs(sums - 1.0) < 1e-9).all(), f"weights not summing to 1.0:\n{sums}"


def test_crosswalk_every_driver_in_panel(cfg) -> None:
    paths = build_macro_scenario_paths(cfg)
    sens = build_portfolio_macro_sensitivity(cfg)
    panel_vars = set(paths["variable"])
    assert set(sens["driver"]) <= panel_vars


def test_multipliers_base_is_unity_and_monotonic(cfg) -> None:
    mult = compute_segment_multipliers(cfg)
    cols = ["pd_multiplier", "lgd_multiplier", "ead_multiplier"]
    base = mult[mult.scenario == "base"]
    assert (base[cols] == 1.0).all().all()
    for _, group in mult.groupby("segment"):
        ordered = group.sort_values("scenario", key=lambda s: s.map(SCEN_ORDER))
        for col in cols:
            vals = ordered[col].tolist()
            assert vals == sorted(vals), f"{col} not monotonic: {vals}"


def test_multipliers_respect_ceiling(cfg) -> None:
    mult = compute_segment_multipliers(cfg)
    ceil = cfg["meta"]["multiplier_ceiling"]
    assert (mult["pd_multiplier"] <= ceil["PD"]).all()
    assert (mult["lgd_multiplier"] <= ceil["LGD"]).all()
    assert (mult["ead_multiplier"] <= ceil["EAD"]).all()


def test_demo_rollup_base_unity_and_monotonic(cfg) -> None:
    demo = pd.read_csv(RAW_DIR / "demo_portfolio.csv")
    facility = build_demo_portfolio_stress(demo, cfg)
    summary = build_demo_portfolio_summary(facility)
    # every demo facility maps to a canonical segment
    assert facility["segment_canonical"].isin(cfg["portfolio_sensitivities"]).all()
    base = summary[summary.scenario == "base"].iloc[0]
    assert base["portfolio_el_uplift_x"] == pytest.approx(1.0)
    ordered = summary.sort_values("scenario", key=lambda s: s.map(SCEN_ORDER))
    uplift = ordered["portfolio_el_uplift_x"].tolist()
    assert uplift == sorted(uplift)
    assert uplift[-1] > uplift[0]  # severe strictly worse than base
