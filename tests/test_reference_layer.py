import pandas as pd

from src.panels.build_business_cycle_panel import build_business_cycle_panel
from src.panels.build_macro_regime_flags import build_macro_regime_flags
from src.panels.build_property_cycle_panel import build_property_cycle_panel
from src.overlays.build_downturn_overlay_tables import build_downturn_overlay_tables
from src.overlays.build_industry_risk_scores import build_industry_risk_scores
from src.overlays.build_property_market_overlays import build_property_market_overlays
from src.arrears_environment import build_base_arrears_environment
from src.overlays.downturn_overlay_core import build_property_downturn_overlays
from src.panels.property_cycle_core import build_property_cycle_table
from src.panels.region_risk_core import build_region_risk_table


def _sample_approvals_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "region": "Australia",
                "state": "Australia",
                "region_group": "Commercial",
                "property_segment": "Offices",
                "approvals_as_of_date": "2026-02-01",
                "approvals_change_pct": -35.7,
                "approvals_momentum_pct": -64.0,
                "approvals_source_dataset": "ABS Building Approvals - Non-residential",
                "structural_segment_score": 4.1,
            },
            {
                "region": "Australia",
                "state": "Australia",
                "region_group": "Industrial",
                "property_segment": "Warehouses",
                "approvals_as_of_date": "2026-02-01",
                "approvals_change_pct": 69.3,
                "approvals_momentum_pct": -9.1,
                "approvals_source_dataset": "ABS Building Approvals - Non-residential",
                "structural_segment_score": 2.4,
            },
        ]
    )


def _empty_activity_summary() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "region",
            "state",
            "region_group",
            "property_segment",
            "activity_as_of_date",
            "commencements_change_pct",
            "commencements_momentum_pct",
            "completions_change_pct",
            "completions_momentum_pct",
            "activity_source_dataset",
        ]
    )


def _empty_finance_summary() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "region",
            "state",
            "region_group",
            "property_segment",
            "housing_finance_as_of_date",
            "housing_finance_change_pct",
            "housing_finance_momentum_pct",
            "housing_finance_source_dataset",
        ]
    )


def _cash_rate_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "as_of_date": "2026-03-16",
                "cash_rate_latest_pct": 3.85,
                "cash_rate_change_1y_pctpts": -0.25,
                "cash_rate_trend": "Falling",
                "source_dataset": "RBA F1 cash-rate table",
            }
        ]
    )


def test_region_risk_table_uses_proxy_inputs_when_optional_sources_missing() -> None:
    region_risk = build_region_risk_table(
        _sample_approvals_summary(),
        _empty_activity_summary(),
        _empty_finance_summary(),
        _cash_rate_summary(),
    )

    offices_score = float(region_risk.loc[region_risk["property_segment"] == "Offices", "region_risk_score"].iloc[0])
    warehouses_score = float(region_risk.loc[region_risk["property_segment"] == "Warehouses", "region_risk_score"].iloc[0])

    assert offices_score > warehouses_score
    assert (region_risk["building_activity_trend"] == "Proxy from approvals trend").all()
    assert region_risk["housing_finance_trend"].str.contains("cash-rate backdrop").all()


def test_property_cycle_table_flags_negative_segment_as_downturn() -> None:
    property_cycle = build_property_cycle_table(
        _sample_approvals_summary(),
        _empty_activity_summary(),
    )

    offices_stage = property_cycle.loc[property_cycle["property_segment"] == "Offices", "cycle_stage"].iloc[0]
    warehouses_stage = property_cycle.loc[property_cycle["property_segment"] == "Warehouses", "cycle_stage"].iloc[0]

    assert offices_stage == "downturn"
    assert warehouses_stage in {"growth", "neutral", "slowing"}


def test_arrears_environment_defaults_to_low_improving_when_context_missing() -> None:
    arrears_environment = build_base_arrears_environment(
        _cash_rate_summary(),
        pd.DataFrame(columns=["as_of_date", "arrears_environment_level", "arrears_trend", "notes", "source_note"]),
        pd.DataFrame(columns=["as_of_date", "notes", "source_note"]),
    )

    row = arrears_environment.iloc[0]
    assert row["arrears_environment_level"] == "Low"
    assert row["arrears_trend"] == "Improving"
    assert float(row["macro_housing_risk_score"]) < 2.5
    assert "local transformation instructions" in row["notes"]


def test_property_downturn_overlays_are_monotonic() -> None:
    property_cycle = build_property_cycle_table(
        _sample_approvals_summary(),
        _empty_activity_summary(),
    )
    arrears_environment = build_base_arrears_environment(
        _cash_rate_summary(),
        pd.DataFrame(columns=["as_of_date", "arrears_environment_level", "arrears_trend", "notes", "source_note"]),
        pd.DataFrame(columns=["as_of_date", "notes", "source_note"]),
    )

    overlays = build_property_downturn_overlays(arrears_environment, property_cycle)
    pd_multipliers = overlays["pd_multiplier"].tolist()
    haircuts = overlays["property_value_haircut"].tolist()

    assert overlays["scenario"].tolist() == ["base", "mild", "moderate", "severe"]
    assert pd_multipliers == sorted(pd_multipliers)
    assert haircuts == sorted(haircuts)
    assert haircuts[0] == 0.0


def test_canonical_panel_overlay_builders_are_importable() -> None:
    assert callable(build_business_cycle_panel)
    assert callable(build_property_cycle_panel)
    assert callable(build_macro_regime_flags)
    assert callable(build_industry_risk_scores)
    assert callable(build_property_market_overlays)
    assert callable(build_downturn_overlay_tables)


def test_industry_base_risk_level_matches_pd_multiplier() -> None:
    """Every published row's risk-level label and pd_multiplier must come
    from the same band in ``SCORE_TO_MULTIPLIER_LADDER``.

    This invariant catches the regression class that the original Issue 7
    found by manual inspection: if ``score_to_risk_level`` and
    ``score_to_pd_multiplier`` ever drift apart (e.g. one is updated
    without the other), the contract starts publishing a label that
    contradicts the multiplier in the same row.
    """
    from src.overlays.build_industry_risk_scores import (
        SCORE_TO_MULTIPLIER_LADDER,
        build_industry_risk_scores,
    )

    scores = build_industry_risk_scores()
    expected = {label: multiplier for _lower, _upper, label, multiplier in SCORE_TO_MULTIPLIER_LADDER}

    for _, row in scores.iterrows():
        label = row["industry_base_risk_level"]
        multiplier = row["pd_multiplier"]
        assert label in expected, f"Unknown band label on row {row['anzsic_division_code']}: {label!r}"
        assert multiplier == expected[label], (
            f"Row {row['anzsic_division_code']}: label={label!r} implies "
            f"multiplier {expected[label]} but row carries {multiplier}. "
            "score_to_risk_level and score_to_pd_multiplier are out of sync."
        )


def test_property_market_overlays_publishes_pd_multiplier_and_segment_code() -> None:
    overlays = build_property_market_overlays()

    assert "pd_multiplier" in overlays.columns
    assert "property_segment_code" in overlays.columns

    multiplier_values = set(overlays["pd_multiplier"].dropna().unique().tolist())
    assert multiplier_values.issubset({0.90, 0.95, 1.00, 1.10, 1.15}), (
        f"pd_multiplier contains values outside the published ladder: {multiplier_values}"
    )

    # The contract is exactly five rows — one per segment code. The PD
    # workbook's lookup is ``df[df['property_segment_code'] == code].iloc[0]``
    # so duplicate codes would make the lookup ambiguous.
    assert overlays["property_segment_code"].is_unique, (
        f"property_segment_code must be unique across rows; "
        f"found duplicates: {overlays['property_segment_code'].value_counts().to_dict()}"
    )
    assert len(overlays) == 5, (
        f"property_market_overlays must have exactly 5 rows (one per segment code); "
        f"found {len(overlays)}"
    )
    expected_codes = {"RES", "CRE", "IND", "RET", "CON"}
    actual_codes = set(overlays["property_segment_code"])
    assert actual_codes == expected_codes, (
        f"Expected exactly the codes {expected_codes}, got {actual_codes}"
    )
