"""Canonical contract-export orchestration for upstream overlays."""

from __future__ import annotations

import pandas as pd

from src.config import (
    ALL_CONTRACT_EXPORTS,
    CONTRACTS_DIR,
)
from src.contract_exports import CONTRACT_EXPORT_KEYS
from src.output import save_csv
from src.overlays.build_downturn_overlay_tables import build_downturn_overlay_tables
from src.overlays.build_industry_risk_scores import build_industry_risk_scores
from src.overlays.build_property_market_overlays import (
    build_property_market_overlays,
    build_property_market_overlays_by_building_type,
)
from src.panels.build_business_cycle_panel import build_business_cycle_panel
from src.panels.build_industry_failure_rates import build_industry_failure_rates
from src.panels.build_industry_financial_benchmarks import (
    build_industry_financial_benchmarks,
)
from src.panels.build_macro_context_panel import build_macro_context_panel
from src.panels.build_macro_regime_flags import build_macro_regime_flags
from src.panels.build_property_cycle_panel import build_property_cycle_panel
from src.panels.build_property_reference_panel import build_property_reference_panel


def _prepare_directories() -> None:
    CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)


def export_contracts() -> dict[str, pd.DataFrame]:
    _prepare_directories()

    business_cycle_panel = build_business_cycle_panel()
    property_cycle_panel = build_property_cycle_panel()
    macro_regime_flags = build_macro_regime_flags()
    industry_risk_scores = build_industry_risk_scores(panel=business_cycle_panel)
    property_market_overlays = build_property_market_overlays(panel=property_cycle_panel)
    property_market_overlays_by_building_type = build_property_market_overlays_by_building_type(
        panel=property_cycle_panel
    )
    downturn_overlay_table = build_downturn_overlay_tables(property_cycle_panel=property_cycle_panel)
    industry_failure_rates = build_industry_failure_rates()
    industry_financial_benchmarks = build_industry_financial_benchmarks(
        panel=business_cycle_panel
    )
    macro_context = build_macro_context_panel()
    property_market_detail = build_property_reference_panel()

    outputs = {
        "industry_risk_scores": industry_risk_scores,
        "property_market_overlays": property_market_overlays,
        "downturn_overlay_table": downturn_overlay_table,
        "macro_regime_flags": macro_regime_flags,
        "industry_failure_rates": industry_failure_rates,
        "industry_financial_benchmarks": industry_financial_benchmarks,
        "macro_context": macro_context,
        "property_market_detail": property_market_detail,
        "business_cycle_panel": business_cycle_panel,
        "property_cycle_panel": property_cycle_panel,
        "property_market_overlays_by_building_type": property_market_overlays_by_building_type,
    }

    for key in CONTRACT_EXPORT_KEYS:
        export_path = ALL_CONTRACT_EXPORTS[key]
        save_csv(outputs[key], export_path)

    return outputs
