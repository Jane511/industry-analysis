"""Property-reference module — multi-source free aggregation.

Each loader returns a DataFrame with the canonical schema for its source.
When a source file is absent, the loader returns an empty DataFrame with
the canonical columns rather than raising. This is the graceful-degradation
contract the brief calls out under TASK 16: the build must succeed across
the spectrum from "ABS sources only" to "all sources staged".
"""

from src.property_reference.load_abs_property import (
    load_abs_lending_indicators,
    load_abs_property_price_index,
    load_abs_total_value_dwellings,
)
from src.property_reference.load_cotality_free import (
    load_cotality_auction_clearance,
    load_cotality_hvi,
)
from src.property_reference.load_domain_quarterly import load_domain_quarterly
from src.property_reference.load_rba_property import (
    load_rba_fsr_aggregates,
    load_rba_table_e2,
)
from src.property_reference.load_sqm_headline import load_sqm_headline
from src.property_reference.load_state_rental_bonds import (
    STATE_RENTAL_BOND_LOADERS,
    load_state_rental_bonds_act,
    load_state_rental_bonds_nsw,
    load_state_rental_bonds_nt,
    load_state_rental_bonds_qld,
    load_state_rental_bonds_sa,
    load_state_rental_bonds_tas,
    load_state_rental_bonds_vic,
    load_state_rental_bonds_wa,
)

__all__ = [
    "load_abs_lending_indicators",
    "load_abs_property_price_index",
    "load_abs_total_value_dwellings",
    "load_cotality_auction_clearance",
    "load_cotality_hvi",
    "load_domain_quarterly",
    "load_rba_fsr_aggregates",
    "load_rba_table_e2",
    "load_sqm_headline",
    "load_state_rental_bonds_act",
    "load_state_rental_bonds_nsw",
    "load_state_rental_bonds_nt",
    "load_state_rental_bonds_qld",
    "load_state_rental_bonds_sa",
    "load_state_rental_bonds_tas",
    "load_state_rental_bonds_vic",
    "load_state_rental_bonds_wa",
    "STATE_RENTAL_BOND_LOADERS",
]
