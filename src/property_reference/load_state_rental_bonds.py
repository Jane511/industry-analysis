"""Loaders for state government rental-bond data (8 states/territories).

Each state's tenancy authority publishes quarterly rental data with suburb-
or SA-level medians. The eight loaders share a canonical schema; per-state
heterogeneity is normalised at extraction time and carried as ``combined``
in the bedrooms / property_type fields when a state doesn't break that out.
"""

from __future__ import annotations

import pandas as pd

from src.config import (
    RAW_PUBLIC_DIR_STATE_RENTAL_BONDS,
    STATE_RENTAL_BOND_GLOBS,
)
from src.property_reference._common import (
    empty_with_columns,
    resolve_latest_by_glob,
    validate_required_columns,
)


CANONICAL_RENTAL_BOND_COLUMNS = [
    "as_of_date",
    "state",
    "region_type",
    "region",
    "property_type",
    "bedrooms",
    "median_weekly_rent_aud",
    "sample_size_n",
    "source_note",
]


def _load_state(state_key: str, expected_state: str) -> pd.DataFrame:
    path = resolve_latest_by_glob(
        RAW_PUBLIC_DIR_STATE_RENTAL_BONDS,
        STATE_RENTAL_BOND_GLOBS[state_key],
    )
    if path is None:
        return empty_with_columns(CANONICAL_RENTAL_BOND_COLUMNS)
    df = pd.read_csv(path, comment="#")
    validate_required_columns(df, CANONICAL_RENTAL_BOND_COLUMNS, path)
    out = df[CANONICAL_RENTAL_BOND_COLUMNS].copy()
    # Defensive: every row in this file should be the named state.
    out["state"] = out["state"].astype(str).str.upper().str.strip()
    if not (out["state"] == expected_state).all():
        out["state"] = expected_state
    return out


def load_state_rental_bonds_nsw() -> pd.DataFrame:
    return _load_state("nsw", "NSW")


def load_state_rental_bonds_vic() -> pd.DataFrame:
    return _load_state("vic", "VIC")


def load_state_rental_bonds_qld() -> pd.DataFrame:
    return _load_state("qld", "QLD")


def load_state_rental_bonds_sa() -> pd.DataFrame:
    return _load_state("sa", "SA")


def load_state_rental_bonds_wa() -> pd.DataFrame:
    return _load_state("wa", "WA")


def load_state_rental_bonds_tas() -> pd.DataFrame:
    return _load_state("tas", "TAS")


def load_state_rental_bonds_nt() -> pd.DataFrame:
    return _load_state("nt", "NT")


def load_state_rental_bonds_act() -> pd.DataFrame:
    return _load_state("act", "ACT")


STATE_RENTAL_BOND_LOADERS = (
    load_state_rental_bonds_nsw,
    load_state_rental_bonds_vic,
    load_state_rental_bonds_qld,
    load_state_rental_bonds_sa,
    load_state_rental_bonds_wa,
    load_state_rental_bonds_tas,
    load_state_rental_bonds_nt,
    load_state_rental_bonds_act,
)
