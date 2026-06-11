"""Tests for property-reference loaders (Task 9 deliverable)."""

from __future__ import annotations

import pandas as pd

from src.property_reference import (
    load_abs_lending_indicators,
    load_abs_property_price_index,
    load_abs_total_value_dwellings,
    load_cotality_auction_clearance,
    load_cotality_hvi,
    load_domain_quarterly,
    load_rba_fsr_aggregates,
    load_rba_table_e2,
    load_sqm_headline,
    load_state_rental_bonds_act,
    load_state_rental_bonds_nsw,
    load_state_rental_bonds_nt,
    load_state_rental_bonds_qld,
    load_state_rental_bonds_sa,
    load_state_rental_bonds_tas,
    load_state_rental_bonds_vic,
    load_state_rental_bonds_wa,
)
from src.property_reference.load_state_rental_bonds import (
    CANONICAL_RENTAL_BOND_COLUMNS,
)


_FREE_LOADERS = (
    load_cotality_hvi,
    load_cotality_auction_clearance,
    load_domain_quarterly,
    load_sqm_headline,
    load_state_rental_bonds_nsw,
    load_state_rental_bonds_vic,
    load_state_rental_bonds_qld,
    load_state_rental_bonds_sa,
    load_state_rental_bonds_wa,
    load_state_rental_bonds_tas,
    load_state_rental_bonds_nt,
    load_state_rental_bonds_act,
    load_abs_property_price_index,
    load_abs_total_value_dwellings,
    load_abs_lending_indicators,
    load_rba_table_e2,
    load_rba_fsr_aggregates,
)


def test_each_loader_returns_dataframe_with_columns() -> None:
    """Every loader returns a DataFrame, never raises for a missing input."""
    for loader in _FREE_LOADERS:
        df = loader()
        assert isinstance(df, pd.DataFrame), f"{loader.__name__} did not return DataFrame"
        # Even the empty-frame degraded path must declare canonical columns.
        assert len(df.columns) > 0, f"{loader.__name__} returned a frame with no columns"


def test_state_rental_bond_loaders_canonical_schema() -> None:
    """All eight state loaders share the canonical 9-column schema."""
    canonical = set(CANONICAL_RENTAL_BOND_COLUMNS)
    for loader in (
        load_state_rental_bonds_nsw,
        load_state_rental_bonds_vic,
        load_state_rental_bonds_qld,
        load_state_rental_bonds_sa,
        load_state_rental_bonds_wa,
        load_state_rental_bonds_tas,
        load_state_rental_bonds_nt,
        load_state_rental_bonds_act,
    ):
        df = loader()
        assert set(df.columns) == canonical, (
            f"{loader.__name__} schema {set(df.columns)} != canonical {canonical}"
        )


def test_cotality_hvi_stub_data_loaded() -> None:
    """The committed cotality_hvi_2025Q4.csv stub should populate the loader."""
    df = load_cotality_hvi()
    assert not df.empty
    assert "median_value_aud" in df.columns
    assert df["median_value_aud"].notna().any()


def test_state_rental_bonds_stub_per_state() -> None:
    for loader in (
        load_state_rental_bonds_nsw,
        load_state_rental_bonds_vic,
        load_state_rental_bonds_qld,
        load_state_rental_bonds_sa,
        load_state_rental_bonds_wa,
        load_state_rental_bonds_tas,
        load_state_rental_bonds_nt,
        load_state_rental_bonds_act,
    ):
        df = loader()
        # Each state has a committed Q4 2025 stub; loader must surface it.
        assert not df.empty, f"{loader.__name__} returned empty despite committed stub"
        assert df["median_weekly_rent_aud"].notna().any()
