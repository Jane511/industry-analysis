"""Structure contract for the 3-section report.

The report mirrors README sections 1-3: macro conditions, stress drivers
(per product/industry), and the industry credit-risk score. Board variant only;
the legacy completeness sections (source inventory, lineage, validation,
technical audit appendix) were removed.
"""
from __future__ import annotations

from src.reporting.industry_analysis_report import build_report
from src.reporting.render_markdown import render


EXPECTED_TITLES = [
    "1. Macro conditions for credit assessment & risk management",
    "2. Macro drivers for stress testing - per product and per industry",
    "3. How the industry credit-risk score is calculated",
]


def _table_captions(section: dict) -> list[str]:
    return [payload["caption"] for kind, payload in section["elements"] if kind == "table"]


def test_report_has_three_readme_sections() -> None:
    report = build_report()
    assert [s["title"] for s in report["sections"]] == EXPECTED_TITLES


def test_each_section_carries_its_key_tables() -> None:
    s1, s2, s3 = build_report()["sections"]
    s1_caps = " ".join(_table_captions(s1)).lower()
    assert "conditions" in s1_caps and "building type" in s1_caps
    s2_caps = " ".join(_table_captions(s2)).lower()
    assert "scenario paths" in s2_caps and "segment multipliers" in s2_caps
    assert any("scores" in c.lower() for c in _table_captions(s3))


def test_board_markdown_renders_three_sections_only() -> None:
    md = render(build_report(), "board")
    for title in EXPECTED_TITLES:
        assert f"## {title}" in md
    # legacy completeness / technical artefacts must be gone
    assert "Data Sources Inventory" not in md
    assert "Lineage / Traceability" not in md
    assert "Appendix A" not in md
