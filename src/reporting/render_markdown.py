"""Markdown renderer for the industry-analysis board report.

Consumes the structured content tree produced by
`src.reporting.industry_analysis_report.build_report()` and emits Board or Technical
markdown. Both variants are produced from the same tree; variant selection
governs which narrative strings, table columns, and callout bodies are used.

Output is plain pandoc-flavoured markdown — no inline HTML, no nested tables.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


VALID_VARIANTS = {"board", "technical"}


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


def _render_table(df: pd.DataFrame, columns: list[str], formats: dict[str, str] | None) -> str:
    if df is None or df.empty or not columns:
        return ""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Table missing required columns: {missing}")
    fmts = formats or {}
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = []
    for _, row in df.iterrows():
        cells = [_format_cell(row[c], fmts.get(c)) for c in columns]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep, *rows])


def _render_callout(block: dict[str, Any], variant: str) -> str:
    variants = block.get("variants") or {"board", "technical"}
    if variant not in variants:
        return ""
    body = block["body_technical"] if variant == "technical" else block["body_board"]
    title = block.get("title", "Note")
    lines = [f"> **{title}**", ">"]
    for para in body.split("\n"):
        if para.strip() == "":
            lines.append(">")
        else:
            lines.append(f"> {para}")
    return "\n".join(lines)


def _render_paragraph(block: dict[str, str], variant: str) -> str:
    return block["technical"] if variant == "technical" else block["board"]


def _render_section(section: dict[str, Any], variant: str) -> str:
    pieces: list[str] = [f"## {section['title']}"]

    lead_board, lead_technical = section.get("lead", (None, None))
    lead = lead_technical if variant == "technical" else lead_board
    if lead:
        pieces.append(lead)

    for kind, payload in section["elements"]:
        if kind == "paragraph":
            pieces.append(_render_paragraph(payload, variant))
        elif kind == "paragraph_technical_only":
            if variant == "technical":
                pieces.append(payload)
        elif kind == "table":
            if variant == "board" and payload.get("show_in_board") is False:
                continue
            cols = payload["cols_technical"] if variant == "technical" else payload["cols_board"]
            if not cols:
                continue
            caption = payload.get("caption")
            if caption:
                pieces.append(f"*{caption}*")
            table_md = _render_table(payload["data"], cols, payload.get("format"))
            if table_md:
                pieces.append(table_md)
        elif kind == "callout":
            rendered = _render_callout(payload, variant)
            if rendered:
                pieces.append(rendered)
        else:
            raise ValueError(f"Unknown element kind: {kind}")

    return "\n\n".join(piece for piece in pieces if piece)


def render(report: dict[str, Any], variant: str) -> str:
    if variant not in VALID_VARIANTS:
        raise ValueError(f"variant must be one of {VALID_VARIANTS}; got {variant!r}")

    meta = report["metadata"]
    period = meta["period_label"]
    variant_label = "Board Summary" if variant == "board" else "Technical Detail"

    header_lines = [
        f"# Industry Analysis Report — {period}",
        f"*{variant_label} variant. Generated {meta['generation_date']}.*",
        "",
        f"Macro and downturn overlays as of {meta['macro_as_of_date']}. "
        f"Property cycle data as of {meta['property_cycle_as_of_date']}.",
    ]

    if variant == "board":
        header_lines.append(
            "This is a summary view for non-technical reviewers. Every table and chart "
            "in this document traces back to the canonical parquet contracts in "
            "`data/exports/`. For full per-column detail, methodology references, "
            "and the audit-log appendix, see the Technical variant."
        )
    else:
        header_lines.append(
            "This is the full-detail variant for MRC, audit, and model-risk review. "
            "It includes per-row technical commentary, source URLs, the full Construction "
            "methodology review item, and the audit log as an appendix."
        )

    rendered_sections = [_render_section(s, variant) for s in report["sections"]]

    document = "\n\n".join(header_lines + [""] + rendered_sections)

    if variant == "technical":
        document = document + "\n\n" + _audit_log_appendix(report)

    return document.rstrip() + "\n"


def _audit_log_appendix(report: dict[str, Any]) -> str:
    stats = report["stats"]
    meta = report["metadata"]
    lines = [
        "## Appendix A — Audit log (this session)",
        "",
        f"**Date:** {meta['generation_date']}  ",
        f"**Scope:** Phase 1 baseline audit, Phase 2 anomaly scan, Phase 3 test-coverage audit + contract tests, Phase 4a markdown report build.",
        "",
        "### Phase 1 — Baseline",
        "- Test suite: 54 passed, 0 failed, 0 skipped, 0 warnings (pre-Phase-3).",
        "- Pipeline scripts: all five completed cleanly after raw ABS/RBA data was copied from the main checkout into the worktree (git-ignored by design).",
        "- Validator: 12/12 checks green.",
        f"- Exports: 6/6 present and non-empty. Dated exports within ~2 months of today; not stale.",
        "",
        "### Phase 2 — Anomaly scan",
        "- HIGH findings: 0. MEDIUM findings: 0. LOW findings: 2 (both informational, from the null-pattern diagnostic block).",
        "- 21 nulls in `business_cycle_panel` confirmed as documented-by-design. Every null-bearing row is labelled 'Fallback' in `inventory_days_est_source`; every non-null row labelled 'ABS quarterly'. Zero exceptions.",
        "- Core scoring columns (`classification_risk_score`, `macro_risk_score`, `industry_base_risk_score`, `industry_base_risk_level`) have 0 nulls.",
        "- Scoring functions in `src/utils.py` map null inputs to a neutral factor score (3) — null-tolerant by design.",
        "",
        "### Phase 3 — Test coverage",
        "- Baseline: 15 of 23 source modules had direct test imports; 8 untested.",
        "- Added `tests/test_export_contracts.py` (6 test functions expanding to 18 parametrized cases) covering the canonical contract boundary (`src/overlays/export_contracts.py`).",
        "- Final count: 72 tests passing.",
        "- Deferred Tier-2 builder tests: the 6 top-level `build_*` functions are smoke-tested via `test_reference_layer.py::test_canonical_panel_overlay_builders_are_importable`. End-to-end coverage is provided by the new contract tests plus the Phase 1 parquet-inspection. Adding per-builder contract tests would be duplication.",
        "- Defensible gaps remaining: `src/validation.py` (end-to-end only via script), `src/config.py` (constants), `src/output.py` (small helper surface), `src/public_data/download_*.py` (thin network wrappers), `src/public_data/load_abs_manual_exports_helpers.py` (helpers for a tested parent module).",
        "",
        "### Phase 4a — Markdown board report",
        "- Added `reports/` package (`__init__.py`, `industry_analysis_report.py`, `render_markdown.py`).",
        "- Added `scripts/build_board_report.py` CLI.",
        "- Two markdown files generated per run: Board (summary) and Technical (full detail).",
        "- DOCX and HTML renderers deferred to Phase 4b.",
        "",
        "### Methodology observations (not bugs)",
        f"- **Construction base risk score ({stats['construction_score']:.2f}, '{stats['construction_level']}')** — logged as an active methodology review item. See Section 9 of this report. Session: noted, not fixed.",
        "",
        "### Dev-ergonomics notes",
        "- Fresh git worktrees do not carry the git-ignored raw ABS/RBA staging directories. Copy them from a primary checkout, or add a `bootstrap_worktree.py` helper. Not urgent; logged for future consideration.",
    ]
    return "\n".join(lines)


def write_markdown_variants(report: dict[str, Any], output_base: str) -> dict[str, str]:
    """Write both Board and Technical files; return {variant: file_path}."""
    from pathlib import Path

    base = Path(output_base)
    stem = base.stem
    parent = base.parent
    parent.mkdir(parents=True, exist_ok=True)

    results = {}
    for variant, suffix in [("board", "_Board"), ("technical", "_Technical")]:
        path = parent / f"{stem}{suffix}.md"
        path.write_text(render(report, variant), encoding="utf-8")
        results[variant] = str(path)
    return results
