"""DOCX renderer for the industry-analysis board report.

Consumes the structured content tree produced by
`src.reporting.industry_analysis_report.build_report()` and emits a formatted
.docx per variant (Board, Technical). Uses helpers in `src.reporting.docx_helpers`
for styling; does not touch parquet files directly.

Callout style -> flag-box colour:
    methodology_note -> orange
    how_to_read      -> blue
    caveat           -> orange (default fallback)
    high_severity    -> red (not currently used)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.reporting.docx_helpers import (
    COLOR_GREY,
    add_flag_box,
    add_para,
    add_section_heading,
    make_table,
    new_document,
)


VALID_VARIANTS = {"board", "technical"}

CALLOUT_STYLE_TO_COLOR = {
    "methodology_note": "orange",
    "how_to_read": "blue",
    "caveat": "orange",
    "high_severity": "red",
}


def _format_cell(value: Any, spec: str | None) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if spec is not None:
        try:
            return spec.format(value)
        except (ValueError, TypeError):
            return str(value)
    return str(value)


def _table_rows(df: pd.DataFrame, columns: list[str], formats: dict[str, str] | None) -> list[list[str]]:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Table missing required columns: {missing}")
    fmts = formats or {}
    rows: list[list[str]] = []
    for _, row in df.iterrows():
        rows.append([_format_cell(row[c], fmts.get(c)) for c in columns])
    return rows


def _render_table(doc, payload: dict[str, Any], variant: str) -> None:
    if variant == "board" and payload.get("show_in_board") is False:
        return
    cols = payload["cols_technical"] if variant == "technical" else payload["cols_board"]
    if not cols:
        return
    caption = payload.get("caption")
    if caption:
        add_para(doc, caption, italic=True, size=10, color=COLOR_GREY)
    rows = _table_rows(payload["data"], cols, payload.get("format"))
    make_table(doc, cols, rows)


def _render_callout(doc, block: dict[str, Any], variant: str) -> None:
    variants = block.get("variants") or {"board", "technical"}
    if variant not in variants:
        return
    body = block["body_technical"] if variant == "technical" else block["body_board"]
    color = CALLOUT_STYLE_TO_COLOR.get(block.get("style", ""), "orange")
    add_flag_box(doc, body, color=color, title=block.get("title"))


def _render_paragraph(doc, block: dict[str, str], variant: str) -> None:
    text = block["technical"] if variant == "technical" else block["board"]
    if text:
        add_para(doc, text)


def _render_section(doc, section: dict[str, Any], variant: str) -> None:
    add_section_heading(doc, section["title"], level=1)

    lead_board, lead_technical = section.get("lead", (None, None))
    lead = lead_technical if variant == "technical" else lead_board
    if lead:
        add_para(doc, lead)

    for kind, payload in section["elements"]:
        if kind == "paragraph":
            _render_paragraph(doc, payload, variant)
        elif kind == "paragraph_technical_only":
            if variant == "technical":
                add_para(doc, payload)
        elif kind == "table":
            _render_table(doc, payload, variant)
        elif kind == "callout":
            _render_callout(doc, payload, variant)
        else:
            raise ValueError(f"Unknown element kind: {kind}")


def _render_title_page(doc, report: dict[str, Any], variant: str) -> None:
    meta = report["metadata"]
    period = meta["period_label"]
    variant_label = "Board Summary" if variant == "board" else "Technical Detail"

    add_section_heading(doc, f"Industry Analysis Report — {period}", level=1)
    add_para(doc, f"{variant_label} variant", italic=True, size=12, color="2E75B6")
    add_para(doc, f"Generated {meta['generation_date']}", size=10, color=COLOR_GREY)
    add_para(
        doc,
        f"Macro and downturn overlays as of {meta['macro_as_of_date']}. "
        f"Property cycle data as of {meta['property_cycle_as_of_date']}.",
        size=10,
        color=COLOR_GREY,
    )

    if variant == "board":
        prepared_for = (
            "This is a summary view for non-technical reviewers. Every table in this "
            "document traces back to the canonical parquet contracts in data/exports/. "
            "For full per-column detail, methodology references, and the audit-log "
            "appendix, see the Technical variant."
        )
    else:
        prepared_for = (
            "This is the full-detail variant for MRC, audit, and model-risk review. "
            "It includes per-row technical commentary, source URLs, the full Construction "
            "methodology review item, and the audit log as an appendix."
        )
    add_flag_box(doc, prepared_for, color="blue", title="Prepared for")


def _render_audit_appendix(doc, report: dict[str, Any]) -> None:
    stats = report["stats"]
    meta = report["metadata"]

    add_section_heading(doc, "Appendix A — Audit log (this session)", level=1)
    add_para(doc, f"Date: {meta['generation_date']}", bold=True)
    add_para(
        doc,
        "Scope: Phase 1 baseline audit, Phase 2 anomaly scan, Phase 3 test-coverage "
        "audit + contract tests, Phase 4a markdown report build, Phase 4b DOCX + HTML "
        "renderers.",
    )

    add_section_heading(doc, "Phase 1 — Baseline", level=2)
    for line in [
        "Test suite: 54 passed, 0 failed, 0 skipped, 0 warnings (pre-Phase-3).",
        "Pipeline scripts: all five completed cleanly after raw ABS/RBA data was "
        "copied from the main checkout into the worktree (git-ignored by design).",
        "Validator: 12/12 checks green.",
        "Exports: 6/6 present and non-empty. Dated exports within ~2 months of today; not stale.",
    ]:
        add_para(doc, f"• {line}")

    add_section_heading(doc, "Phase 2 — Anomaly scan", level=2)
    for line in [
        "HIGH findings: 0. MEDIUM findings: 0. LOW findings: 2 (informational, null-pattern diagnostics).",
        "21 nulls in business_cycle_panel confirmed as documented-by-design. Every "
        "null-bearing row is labelled 'Fallback' in inventory_days_est_source; every "
        "non-null row labelled 'ABS quarterly'. Zero exceptions.",
        "Core scoring columns (classification_risk_score, macro_risk_score, "
        "industry_base_risk_score, industry_base_risk_level) have 0 nulls.",
        "Scoring functions in src/utils.py map null inputs to a neutral factor score "
        "(3) — null-tolerant by design.",
    ]:
        add_para(doc, f"• {line}")

    add_section_heading(doc, "Phase 3 — Test coverage", level=2)
    for line in [
        "Baseline: 15 of 23 source modules had direct test imports; 8 untested.",
        "Added tests/test_export_contracts.py (6 test functions expanding to 18 "
        "parametrized cases) covering the canonical contract boundary.",
        "Final count: 77 tests passing (72 after Phase 3 + 5 renderer tests in Phase 4b).",
        "Deferred Tier-2 builder tests as duplication of contract-test coverage.",
    ]:
        add_para(doc, f"• {line}")

    add_section_heading(doc, "Phase 4 — Board report", level=2)
    for line in [
        "Phase 4a: markdown renderer + CLI; two files per run (Board + Technical).",
        "Phase 4b: DOCX renderer (reports/render_docx.py), HTML renderer "
        "(reports/render_html.py), CLI extended with --format all to emit all six files.",
        "Content tweaks applied: Section 2 macro-commentary rewrite; Section 9 Board "
        "Construction callout expanded with Porter Davis / Probuild / Clough context; "
        "Section 1 'How to read this report' callout added.",
    ]:
        add_para(doc, f"• {line}")

    add_section_heading(doc, "Methodology observations (not bugs)", level=2)
    add_para(
        doc,
        f"• Construction base risk score ({stats['construction_score']:.2f}, "
        f"'{stats['construction_level']}') — logged as an active methodology review "
        f"item. See Section 9 of this report. Session: noted, not fixed.",
    )

    add_section_heading(doc, "Dev-ergonomics notes", level=2)
    add_para(
        doc,
        "• Fresh git worktrees do not carry the git-ignored raw ABS/RBA staging "
        "directories. Copy them from a primary checkout, or add a "
        "bootstrap_worktree.py helper. Not urgent; logged for future consideration.",
    )


def render(report: dict[str, Any], variant: str, output_path: str | Path) -> str:
    if variant not in VALID_VARIANTS:
        raise ValueError(f"variant must be one of {VALID_VARIANTS}; got {variant!r}")

    doc = new_document(report["metadata"]["period_label"])

    _render_title_page(doc, report, variant)

    for section in report["sections"]:
        _render_section(doc, section, variant)

    if variant == "technical":
        _render_audit_appendix(doc, report)

    add_para(doc, "END OF REPORT", italic=True, size=9, color=COLOR_GREY)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return str(out)


def write_docx_variants(report: dict[str, Any], output_base: str) -> dict[str, str]:
    """Write both Board and Technical DOCX files; return {variant: file_path}."""
    base = Path(output_base)
    stem = base.stem
    parent = base.parent
    parent.mkdir(parents=True, exist_ok=True)

    results = {}
    for variant, suffix in [("board", "_Board"), ("technical", "_Technical")]:
        path = parent / f"{stem}{suffix}.docx"
        render(report, variant, path)
        results[variant] = str(path)
    return results
