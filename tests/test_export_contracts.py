"""Contract test for src/overlays/export_contracts.py.

Locks in the schema and minimum row counts that downstream repos depend on.
This test exists to catch silent contract drift: if a builder accidentally
drops a column or produces an empty frame, this test fails immediately.
"""
from __future__ import annotations

import pandas as pd
import pytest

from src.config import ALL_CONTRACT_EXPORTS
from src.overlays.export_contracts import export_contracts


CONTRACT_SCHEMAS = {
    "industry_risk_scores": {
        "min_rows": 9,
        "required_cols": [
            "industry",
            "classification_risk_score",
            "macro_risk_score",
            "industry_base_risk_score",
            "industry_base_risk_level",
        ],
    },
    "property_market_overlays": {
        "min_rows": 9,
        "required_cols": [
            "property_segment",
            "cycle_stage",
            "market_softness_score",
            "region_risk_score",
        ],
    },
    "downturn_overlay_table": {
        "min_rows": 4,
        "required_cols": [
            "scenario",
            "pd_multiplier",
            "lgd_multiplier",
            "ccf_multiplier",
            "property_value_haircut",
        ],
    },
    "macro_regime_flags": {
        "min_rows": 1,
        "required_cols": [],
    },
}


@pytest.fixture(scope="module")
def exports() -> dict[str, pd.DataFrame]:
    """Run the full export pipeline once and reuse the returned frames."""
    return export_contracts()


@pytest.mark.parametrize("key,spec", CONTRACT_SCHEMAS.items())
def test_export_file_exists_on_disk(exports, key, spec):
    path = ALL_CONTRACT_EXPORTS[key]
    assert path.exists(), f"Required contract export missing on disk: {path}"


@pytest.mark.parametrize("key,spec", CONTRACT_SCHEMAS.items())
def test_export_has_min_rows(exports, key, spec):
    df = exports[key]
    assert len(df) >= spec["min_rows"], (
        f"{key} has {len(df)} rows, expected >= {spec['min_rows']}"
    )


@pytest.mark.parametrize("key,spec", CONTRACT_SCHEMAS.items())
def test_export_has_required_columns(exports, key, spec):
    df = exports[key]
    missing = [c for c in spec["required_cols"] if c not in df.columns]
    assert not missing, f"{key} missing required columns: {missing}"


@pytest.mark.parametrize("key,spec", CONTRACT_SCHEMAS.items())
def test_export_has_no_all_null_columns(exports, key, spec):
    df = exports[key]
    all_null = [c for c in df.columns if df[c].isna().all()]
    assert not all_null, f"{key} has all-null columns: {all_null}"


def test_downturn_multipliers_monotonic(exports):
    """Base <= mild <= moderate <= severe across all multiplier columns."""
    df = exports["downturn_overlay_table"].set_index("scenario").reindex(
        ["base", "mild", "moderate", "severe"]
    )
    for mult in ["pd_multiplier", "lgd_multiplier", "ccf_multiplier"]:
        if mult not in df.columns:
            continue
        vals = df[mult].dropna().tolist()
        assert vals == sorted(vals), f"{mult} not monotonic: {vals}"


def test_downturn_base_is_unity(exports):
    """Base scenario must have all multipliers = 1.0 (no adjustment)."""
    df = exports["downturn_overlay_table"]
    base = df[df["scenario"] == "base"].iloc[0]
    for mult in ["pd_multiplier", "lgd_multiplier", "ccf_multiplier"]:
        if mult not in base:
            continue
        assert base[mult] == 1.0, f"base {mult} = {base[mult]}, expected 1.0"
