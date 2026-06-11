"""Tests for the industry_financial_benchmarks contract export.

Each "median" published is an industry-aggregate ratio sourced from ABS
public aggregates (closest available proxy for an industry median). These
tests guard the contract grain, schema, value plausibility, and the
join-grain integrity that downstream credit-risk consumers depend on.
"""

from __future__ import annotations

import pandas as pd

from src.overlays.build_industry_risk_scores import build_industry_risk_scores
from src.panels.build_industry_financial_benchmarks import (
    build_industry_financial_benchmarks,
)


def test_builder_produces_one_row_per_covered_anzsic_division() -> None:
    """All 18 commercial divisions present, one row each."""
    df = build_industry_financial_benchmarks()
    assert df["anzsic_division_code"].is_unique
    assert len(df) == 18
    expected = set("ABCDEFGHIJLMNOPQRS")  # K (Financial) deliberately excluded
    assert set(df["anzsic_division_code"]) == expected


def test_required_columns_present() -> None:
    df = build_industry_financial_benchmarks()
    required = {
        "anzsic_division_code",
        "industry",
        "median_ebitda_margin_pct",
        "median_gross_operating_profit_to_sales_ratio",
        "median_wages_to_sales_pct",
        "median_inventory_days_est",
        "median_sales_growth_pct",
        "median_employment_yoy_growth_pct",
        "median_inventory_to_sales_ratio",
        "median_sales_per_employee_thousands",
        "benchmark_method",
        "source_note",
        "as_of_date",
    }
    missing = required - set(df.columns)
    assert not missing, f"Missing columns: {missing}"


def test_benchmark_values_are_in_plausible_ranges() -> None:
    """Sanity-check ranges to catch unit-of-measure or sign errors.

    EBITDA margin upper bound widened to 60% from the brief's 40% because
    Mining (Division B) has a published industry-aggregate EBITDA margin
    of ~47% in the current ABS Cat. 8155.0 release — a real feature of
    Australian resource industries, not a unit error.
    """
    df = build_industry_financial_benchmarks()
    assert df["median_ebitda_margin_pct"].between(-5, 60).all()
    assert df["median_gross_operating_profit_to_sales_ratio"].dropna().between(0, 0.5).all()
    assert df["median_wages_to_sales_pct"].between(0, 60).all()
    inv_days = df["median_inventory_days_est"]
    assert inv_days.dropna().between(0, 250).all()
    assert df["median_sales_growth_pct"].between(-30, 60).all()


def test_benchmarks_join_cleanly_to_industry_risk_scores() -> None:
    """Every benchmark row must have a corresponding risk-score row.

    This is the integrity check that downstream consumers depend on —
    a borrower in industry X must find both a multiplier (from
    industry_risk_scores) and ratio benchmarks (from this contract)
    keyed by the same anzsic_division_code.
    """
    benchmarks = build_industry_financial_benchmarks()
    scores = build_industry_risk_scores()
    bench_codes = set(benchmarks["anzsic_division_code"])
    score_codes = set(scores["anzsic_division_code"])
    assert bench_codes == score_codes, (
        f"Benchmarks codes {bench_codes - score_codes} not in scores; "
        f"scores codes {score_codes - bench_codes} not in benchmarks"
    )


def test_as_of_date_is_present_and_iso() -> None:
    df = build_industry_financial_benchmarks()
    assert "as_of_date" in df.columns
    assert df["as_of_date"].nunique() == 1
    pd.to_datetime(df["as_of_date"].iloc[0])


def test_explicit_warning_about_percentiles_in_source_note() -> None:
    """Source note must explicitly tell consumers that p25/p75 aren't
    available in this version, so they don't accidentally try to use
    estimated_p25 columns that don't exist.
    """
    df = build_industry_financial_benchmarks()
    note = df["source_note"].iloc[0]
    assert "p25" in note.lower() or "percentile" in note.lower()
