from __future__ import annotations

import re

import pandas as pd

from src.contract_exports import CONTRACT_EXPORT_SPECS
from src.reporting.industry_analysis_report import (
    _source_registry,
    build_report,
    load_public_manifest,
)
from src.reporting.render_markdown import render


EXPECTED_SECTION_TITLES = [
    "1. Executive Summary",
    "2. Headline Numbers",
    "3. Data Sources Inventory",
    "4. Transformations Applied",
    "5. Detailed Analysis",
    "6. Lineage / Traceability",
    "7. What's Not In This Report",
    "8. Validation and Caveats",
]


def _table(report, section_id: str, caption: str) -> pd.DataFrame:
    section = next(s for s in report["sections"] if s["id"] == section_id)
    return next(
        payload["data"]
        for kind, payload in section["elements"]
        if kind == "table" and payload["caption"] == caption
    )


def _rendered_section_titles(markdown: str) -> list[str]:
    return re.findall(r"^## (.+)$", markdown, flags=re.MULTILINE)


def test_board_report_completeness_contract() -> None:
    """Executable definition of a complete Board report.

    The report must disclose every registered source, every canonical export,
    the analytical rows behind the numbers, traceability, missing/manual
    sources, and validation status in a fixed Board-readable order.
    """
    manifest = load_public_manifest()
    report = build_report(manifest=manifest)
    markdown = render(report, "board")

    assert _rendered_section_titles(markdown)[:8] == EXPECTED_SECTION_TITLES

    inventory = _table(report, "data_sources_inventory", "Data Sources Inventory")
    assert len(inventory) == len(_source_registry(manifest))
    assert inventory["Source key"].is_unique
    assert set([
        "Source key",
        "Publisher / origin",
        "URL or landing page",
        "File type",
        "Period or vintage",
        "Retrieved / fetched timestamp",
        "File size or row count",
        "Status",
        "Hash / version identifier",
    ]).issubset(inventory.columns)
    assert "missing" in set(inventory["Status"]) or "manually staged" in set(inventory["Status"])

    transformations = _table(report, "transformations_applied", "Transformations Applied")
    assert len(transformations) == len(CONTRACT_EXPORT_SPECS)
    assert transformations["Output filename"].is_unique
    assert set(spec.csv_path.name for spec in CONTRACT_EXPORT_SPECS) == set(transformations["Output filename"])
    contract_csv_names = {path.name for path in CONTRACT_EXPORT_SPECS[0].csv_path.parent.glob("*.csv")}
    # The macro-stress contracts are produced by a separate builder
    # (src/overlays/macro_stress_core.py) and covered by tests/test_macro_stress.py,
    # so they sit outside this upstream-transformation completeness check.
    macro_stress_contracts = {
        "macro_scenario_paths.csv", "portfolio_macro_sensitivity.csv", "macro_context.csv",
    }
    assert contract_csv_names - macro_stress_contracts == set(transformations["Output filename"])
    assert set(transformations["Validation status"].str.split(":", n=1).str[0]) <= {"PASS", "WARN", "FAIL"}

    detail_counts = report["completeness"]["detail_export_rows"]
    for spec in CONTRACT_EXPORT_SPECS:
        caption = f"Full detail rows from {spec.key}.csv"
        detail = _table(report, "detailed_analysis", caption)
        assert len(detail) == detail_counts[spec.key]
        assert len(detail) == len(pd.read_csv(spec.csv_path))

    lineage = _table(report, "lineage_traceability", "Lineage / Traceability")
    assert len(lineage) == len(CONTRACT_EXPORT_SPECS)
    for value in lineage["Reference hops"]:
        assert "source inventory row" in value
        assert value.count("->") <= 3

    not_captured = _table(report, "not_in_report", "Data not yet captured / out of scope")
    problem_sources = inventory[inventory["Status"].isin(["missing", "manually staged", "outdated"])]
    assert set(problem_sources["Source key"]) == set(not_captured["Source key"])

    validation = _table(report, "validation_caveats", "Contract validation summary")
    assert set(validation["Status"]) == {"PASS"}


def test_missing_source_fixture_is_visible_in_inventory_and_gap_section() -> None:
    """A registered source with neither a manifest entry nor an on-disk file
    must appear with status="missing" in the inventory and reappear in the
    "Data not yet captured" section. ``cpi_all_groups_xlsx`` is a registered
    public source that the engine does not currently stage, so it serves as a
    naturally-missing fixture without needing to manipulate test state."""
    manifest = load_public_manifest()
    report = build_report(manifest=manifest)

    inventory = _table(report, "data_sources_inventory", "Data Sources Inventory")
    cpi_row = inventory[inventory["Source key"] == "cpi_all_groups_xlsx"].iloc[0]
    assert cpi_row["Status"] == "missing"

    not_captured = _table(report, "not_in_report", "Data not yet captured / out of scope")
    row = not_captured[not_captured["Source key"] == "cpi_all_groups_xlsx"].iloc[0]
    assert "Awaiting next release" in row["Required action"]
