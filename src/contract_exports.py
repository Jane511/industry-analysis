"""Canonical metadata for published CSV exports.

This module keeps a single source of truth for what each contract export
contains and which downstream layers are expected to consume it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.config import ALL_CONTRACT_EXPORTS


@dataclass(frozen=True)
class ContractExportSpec:
    key: str
    csv_path: Path
    contract_role: str
    join_grain: str
    includes: str
    downstream_layers: tuple[str, ...]


CONTRACT_EXPORT_SPECS: tuple[ContractExportSpec, ...] = (
    ContractExportSpec(
        key="industry_risk_scores",
        csv_path=ALL_CONTRACT_EXPORTS["industry_risk_scores"],
        contract_role="Core downstream contract",
        join_grain="Industry snapshot",
        includes=(
            "Compact industry overlay: classification score, macro score, base risk "
            "score/level, and shared cash-rate backdrop fields."
        ),
        downstream_layers=(
            "PD overlays / scorecards",
            "EL and pricing overlays",
            "External sector benchmarks",
            "Board reporting",
        ),
    ),
    ContractExportSpec(
        key="property_market_overlays",
        csv_path=ALL_CONTRACT_EXPORTS["property_market_overlays"],
        contract_role="Core downstream contract",
        join_grain="Property segment snapshot",
        includes=(
            "Compact property overlay: cycle stage, softness score/band, region risk, "
            "approvals change, and approvals-proxy activity signals."
        ),
        downstream_layers=(
            "LGD and collateral overlays",
            "Property-backed PD context",
            "Pricing and policy overlays",
            "Board reporting",
        ),
    ),
    ContractExportSpec(
        key="downturn_overlay_table",
        csv_path=ALL_CONTRACT_EXPORTS["downturn_overlay_table"],
        contract_role="Core downstream contract",
        join_grain="Scenario table",
        includes=(
            "Scenario multipliers for PD, LGD, and CCF plus property haircuts, a "
            "per-scenario macro-path note (mild = Basel CRE36.51), and scenario "
            "notes (incl. the no-diversification assumption)."
        ),
        downstream_layers=(
            "PD scenario layer",
            "LGD scenario layer",
            "CCF / EAD scenario layer",
            "Stress testing and pricing what-if views",
        ),
    ),
    ContractExportSpec(
        key="macro_regime_flags",
        csv_path=ALL_CONTRACT_EXPORTS["macro_regime_flags"],
        contract_role="Core downstream contract",
        join_grain="Single as-of-date regime row",
        includes=(
            "Environment selector: cash-rate regime, arrears level/trend, macro regime "
            "flag, and source dataset."
        ),
        downstream_layers=(
            "PD regime conditioning",
            "LGD / EL regime conditioning",
            "Scenario-row selection",
            "Portfolio and board reporting",
        ),
    ),
    ContractExportSpec(
        key="industry_financial_benchmarks",
        csv_path=ALL_CONTRACT_EXPORTS["industry_financial_benchmarks"],
        contract_role="Core downstream contract",
        join_grain="ANZSIC-division snapshot",
        includes=(
            "Per-ANZSIC-division medians of the financial ratios APG 220 paragraph 64 "
            "calls out as standard credit-assessment benchmarks: EBITDA margin, gross "
            "operating profit-to-sales, wages-to-sales, inventory days, sales growth, "
            "employment growth, inventory-to-sales, and sales per employee."
        ),
        downstream_layers=(
            "Origination scorecard industry-relative ratios",
            "PD model industry-comparison features",
            "ECL borrower-vs-industry signals",
            "External sector benchmarks",
        ),
    ),
    ContractExportSpec(
        key="business_cycle_panel",
        csv_path=ALL_CONTRACT_EXPORTS["business_cycle_panel"],
        contract_role="Optional explainability panel",
        join_grain="Industry diagnostics panel",
        includes=(
            "Wide industry diagnostics: structural factors, public benchmark metrics, "
            "macro factor scores, demand proxies, inventory flags, and explainability "
            "fields behind the industry overlay."
        ),
        downstream_layers=(
            "PD explainability",
            "External benchmark diagnostics",
            "Challenger overlay analysis",
            "Technical report detail",
        ),
    ),
    ContractExportSpec(
        key="property_cycle_panel",
        csv_path=ALL_CONTRACT_EXPORTS["property_cycle_panel"],
        contract_role="Optional explainability panel",
        join_grain="Property segment-by-region diagnostics",
        includes=(
            "Wide property diagnostics: approvals trend, cycle stage, softness band, "
            "region risk, as-of-date, and per-row source/proxy notes."
        ),
        downstream_layers=(
            "LGD explainability",
            "Collateral benchmark diagnostics",
            "Property stress interpretation",
            "Technical report detail",
        ),
    ),
    ContractExportSpec(
        key="property_market_overlays_by_building_type",
        csv_path=ALL_CONTRACT_EXPORTS["property_market_overlays_by_building_type"],
        contract_role="Optional explainability panel",
        join_grain="Per-building-type non-residential detail",
        includes=(
            "One row per ABS non-residential building-approval category — the "
            "pre-aggregation input to the five-row property_market_overlays "
            "contract. Shows each category's softness, region risk, approvals "
            "change, and the property_segment_code it rolls up into."
        ),
        downstream_layers=(
            "Property overlay explainability",
            "Reviewer drilldown into CRE / IND / RET / CON aggregation",
            "Technical report detail",
        ),
    ),
)


CONTRACT_EXPORT_KEYS = tuple(spec.key for spec in CONTRACT_EXPORT_SPECS)


def build_contract_export_summary_rows() -> list[dict[str, str]]:
    """Return report-ready rows describing each canonical CSV export."""
    rows: list[dict[str, str]] = []
    for spec in CONTRACT_EXPORT_SPECS:
        rows.append(
            {
                "CSV export": spec.csv_path.name,
                "Contract role": spec.contract_role,
                "Join grain": spec.join_grain,
                "What it includes": spec.includes,
                "Downstream layers": "; ".join(spec.downstream_layers),
            }
        )
    return rows
