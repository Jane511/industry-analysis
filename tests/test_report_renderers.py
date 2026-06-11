"""Cross-renderer tests for the industry-analysis board report.

These tests verify the Phase 4b renderers (markdown, DOCX, HTML) operate
deterministically, emit the correct variant-specific content, and leave no
unresolved `{placeholder}` strings in output.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
from docx import Document

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.reporting.industry_analysis_report import build_report  # noqa: E402
from src.reporting.render_docx import write_docx_variants  # noqa: E402
from src.reporting.render_html import render as render_html  # noqa: E402
from src.reporting.render_markdown import render as render_markdown  # noqa: E402


@pytest.fixture(scope="module")
def report():
    return build_report()


def test_markdown_output_deterministic(report):
    """Two successive renders of the same report produce byte-identical markdown."""
    first_board = render_markdown(report, "board")
    second_board = render_markdown(report, "board")
    first_tech = render_markdown(report, "technical")
    second_tech = render_markdown(report, "technical")
    assert first_board == second_board
    assert first_tech == second_tech
    assert first_board != first_tech


def test_markdown_includes_contract_export_map(report):
    """Board and Technical markdown include the parquet export usage summary."""
    board = render_markdown(report, "board")
    technical = render_markdown(report, "technical")

    assert "3. Data Sources Inventory" in board
    assert "4. Transformations Applied" in board
    assert "5. Detailed Analysis" in board
    assert "6. Lineage / Traceability" in board
    assert "Canonical CSV exports: contents and downstream layers" in board
    assert "industry_risk_scores.csv" in board
    assert "PD overlays / scorecards" in board

    assert "Contract role" in technical
    assert "Join grain" in technical
    assert "property_cycle_panel.csv" in technical
    assert "Collateral benchmark diagnostics" in technical


def test_all_four_variants_produce_files(tmp_path, report):
    """`--format all` via CLI produces all six files; each is non-empty."""
    output_base = tmp_path / "Industry_Analysis_Test"
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "src" / "build_board_report.py"),
            "--format", "all",
            "--output", str(output_base),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"

    expected = [
        "Industry_Analysis_Test_Board.md",
        "Industry_Analysis_Test_Technical.md",
        "Industry_Analysis_Test_Board.docx",
        "Industry_Analysis_Test_Technical.docx",
        "Industry_Analysis_Test_Board.html",
        "Industry_Analysis_Test_Technical.html",
    ]
    for name in expected:
        path = tmp_path / name
        assert path.exists(), f"Missing expected output: {name}"
        assert path.stat().st_size > 1024, f"Output too small: {name}"


def test_docx_contains_source_inventory_before_transformations(tmp_path, report):
    """Board DOCX follows the completeness section order."""
    output_base = tmp_path / "Industry_Analysis_DocxTest"
    write_docx_variants(report, str(output_base))

    board_path = tmp_path / "Industry_Analysis_DocxTest_Board.docx"
    doc = Document(str(board_path))

    paragraphs = [p.text for p in doc.paragraphs]

    section3_idx = next(
        (i for i, t in enumerate(paragraphs) if t.startswith("3. Data Sources Inventory")),
        None,
    )
    section4_idx = next(
        (i for i, t in enumerate(paragraphs) if t.startswith("4. Transformations Applied")),
        None,
    )
    assert section3_idx is not None, "Section 3 heading missing"
    assert section4_idx is not None, "Section 4 heading missing"
    assert section4_idx > section3_idx

    table_text = "\n".join(
        cell.text for table in doc.tables for row in table.rows for cell in row.cells
    )
    assert "Data Sources Inventory" in table_text
    assert "Transformations Applied" in table_text


def test_docx_technical_has_appendix(tmp_path, report):
    """Technical DOCX contains Appendix A; Board DOCX does not."""
    output_base = tmp_path / "Industry_Analysis_AppxTest"
    write_docx_variants(report, str(output_base))

    board_doc = Document(str(tmp_path / "Industry_Analysis_AppxTest_Board.docx"))
    tech_doc = Document(str(tmp_path / "Industry_Analysis_AppxTest_Technical.docx"))

    board_text = "\n".join(p.text for p in board_doc.paragraphs)
    tech_text = "\n".join(p.text for p in tech_doc.paragraphs)

    assert "Appendix A" in tech_text, "Technical DOCX should include Appendix A"
    assert "Appendix A" not in board_text, "Board DOCX should not include Appendix A"


def test_html_has_no_broken_placeholders(report):
    """HTML output contains no unresolved `{variable}` template strings."""
    placeholder_re = re.compile(r"\{[a-z_][a-z0-9_]*\}")
    for variant in ("board", "technical"):
        rendered = render_html(report, variant)
        assert rendered.startswith("<!DOCTYPE html>"), f"{variant}: missing doctype"
        assert "<style>" in rendered, f"{variant}: missing inline stylesheet"
        hits = placeholder_re.findall(rendered)
        assert not hits, f"{variant}: unresolved placeholders found: {hits[:5]}"
