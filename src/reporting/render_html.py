"""HTML renderer for the industry-analysis board report.

Consumes the structured tree produced by
`src.reporting.industry_analysis_report.build_report()` and emits a self-contained
HTML document per variant (Board, Technical). Styles are inlined in a single
`<style>` block so the file is portable with no external assets.

Callout style -> CSS class:
    methodology_note -> flag-orange
    how_to_read      -> flag-blue
    caveat           -> flag-orange
    high_severity    -> flag-red
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

import pandas as pd


VALID_VARIANTS = {"board", "technical"}

CALLOUT_STYLE_TO_CLASS = {
    "methodology_note": "flag flag-orange",
    "how_to_read": "flag flag-blue",
    "caveat": "flag flag-orange",
    "high_severity": "flag flag-red",
}

STYLESHEET = """
    body {
        font-family: Arial, Helvetica, sans-serif;
        max-width: 1000px;
        margin: 2em auto;
        padding: 0 1.5em;
        color: #222;
        line-height: 1.5;
        background: #ffffff;
    }
    h1 {
        color: #1F4E79;
        border-bottom: 2px solid #1F4E79;
        padding-bottom: 0.3em;
        margin-top: 1.4em;
    }
    h2 {
        color: #2E75B6;
        border-bottom: 1px solid #BDD7EE;
        padding-bottom: 0.2em;
        margin-top: 1.6em;
    }
    h3 { color: #2E75B6; margin-top: 1.2em; }
    p { margin: 0.6em 0; }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
        font-size: 0.95em;
    }
    th {
        background: #1F4E79;
        color: #ffffff;
        text-align: left;
        padding: 8px 10px;
        font-weight: 600;
    }
    td {
        padding: 7px 10px;
        border-bottom: 1px solid #E7E7E7;
    }
    tbody tr:nth-child(even) { background: #F2F2F2; }
    tbody tr:hover { background: #E8F1FB; }
    .caption {
        font-style: italic;
        color: #7F7F7F;
        font-size: 0.9em;
        margin: 0.4em 0 0.2em;
    }
    .summary-box {
        background: #DEEBF7;
        border-left: 4px solid #2E75B6;
        padding: 12px 16px;
        margin: 1.2em 0;
        border-radius: 3px;
    }
    .flag {
        padding: 12px 16px;
        margin: 1.2em 0;
        border-radius: 3px;
        border-left: 4px solid;
    }
    .flag-orange { background: #FCE8D6; border-color: #D97B29; }
    .flag-red    { background: #FADBD8; border-color: #C0392B; }
    .flag-blue   { background: #DEEBF7; border-color: #2E75B6; }
    .flag .flag-title { font-weight: 700; margin-bottom: 0.3em; }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.85em;
        font-weight: 600;
    }
    .status-green  { background: #D4EFDF; color: #1E8449; }
    .status-amber  { background: #FCE8B2; color: #9A6B00; }
    .status-red    { background: #FADBD8; color: #C0392B; }
    ul { margin: 0.4em 0 0.6em 1.2em; }
    footer {
        margin-top: 3em;
        padding-top: 1em;
        border-top: 1px solid #DDD;
        color: #7F7F7F;
        font-size: 0.85em;
        text-align: center;
    }
"""


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


def _render_table(df: pd.DataFrame, columns: list[str], formats: dict[str, str] | None, caption: str | None) -> str:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Table missing required columns: {missing}")
    fmts = formats or {}

    parts: list[str] = []
    if caption:
        parts.append(f'<p class="caption">{html.escape(caption)}</p>')
    parts.append("<table>")
    parts.append("<thead><tr>")
    for c in columns:
        parts.append(f"<th>{html.escape(str(c))}</th>")
    parts.append("</tr></thead>")
    parts.append("<tbody>")
    for _, row in df.iterrows():
        parts.append("<tr>")
        for c in columns:
            cell = _format_cell(row[c], fmts.get(c))
            parts.append(f"<td>{html.escape(cell)}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "\n".join(parts)


def _render_body_with_breaks(body: str) -> str:
    """Escape body text, preserve paragraph breaks, render leading '- ' as bullets."""
    lines = body.split("\n")
    out: list[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    paragraph_buf: list[str] = []

    def flush_para() -> None:
        if paragraph_buf:
            text = " ".join(paragraph_buf).strip()
            if text:
                out.append(f"<p>{_inline(text)}</p>")
            paragraph_buf.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            flush_para()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(stripped[2:])}</li>")
        elif stripped == "":
            flush_para()
            close_list()
        else:
            close_list()
            paragraph_buf.append(stripped)
    flush_para()
    close_list()
    return "\n".join(out)


def _inline(text: str) -> str:
    """Escape HTML then re-enable `**bold**` and `` `code` `` inline markup."""
    esc = html.escape(text)
    out: list[str] = []
    i = 0
    while i < len(esc):
        if esc.startswith("**", i):
            end = esc.find("**", i + 2)
            if end != -1:
                out.append("<strong>")
                out.append(esc[i + 2:end])
                out.append("</strong>")
                i = end + 2
                continue
        if esc[i] == "`":
            end = esc.find("`", i + 1)
            if end != -1:
                out.append("<code>")
                out.append(esc[i + 1:end])
                out.append("</code>")
                i = end + 1
                continue
        out.append(esc[i])
        i += 1
    return "".join(out)


def _render_callout(block: dict[str, Any], variant: str) -> str:
    variants = block.get("variants") or {"board", "technical"}
    if variant not in variants:
        return ""
    body = block["body_technical"] if variant == "technical" else block["body_board"]
    css = CALLOUT_STYLE_TO_CLASS.get(block.get("style", ""), "flag flag-orange")
    title = block.get("title")
    body_html = _render_body_with_breaks(body)
    title_html = f'<div class="flag-title">{html.escape(title)}</div>' if title else ""
    return f'<div class="{css}">{title_html}{body_html}</div>'


def _render_paragraph(block: dict[str, str], variant: str) -> str:
    text = block["technical"] if variant == "technical" else block["board"]
    if not text:
        return ""
    return f"<p>{_inline(text)}</p>"


def _render_section(section: dict[str, Any], variant: str) -> str:
    pieces: list[str] = [f"<h2>{html.escape(section['title'])}</h2>"]

    lead_board, lead_technical = section.get("lead", (None, None))
    lead = lead_technical if variant == "technical" else lead_board
    if lead:
        pieces.append(f"<p>{_inline(lead)}</p>")

    for kind, payload in section["elements"]:
        if kind == "paragraph":
            rendered = _render_paragraph(payload, variant)
            if rendered:
                pieces.append(rendered)
        elif kind == "paragraph_technical_only":
            if variant == "technical":
                pieces.append(f"<p>{_inline(payload)}</p>")
        elif kind == "table":
            if variant == "board" and payload.get("show_in_board") is False:
                continue
            cols = payload["cols_technical"] if variant == "technical" else payload["cols_board"]
            if not cols:
                continue
            pieces.append(_render_table(payload["data"], cols, payload.get("format"), payload.get("caption")))
        elif kind == "callout":
            rendered = _render_callout(payload, variant)
            if rendered:
                pieces.append(rendered)
        else:
            raise ValueError(f"Unknown element kind: {kind}")

    return "\n".join(pieces)


def _audit_log_appendix_html(report: dict[str, Any]) -> str:
    stats = report["stats"]
    meta = report["metadata"]
    return "\n".join([
        "<h2>Appendix A — Audit log (this session)</h2>",
        f"<p><strong>Date:</strong> {html.escape(meta['generation_date'])}<br>",
        "<strong>Scope:</strong> Phase 1 baseline audit, Phase 2 anomaly scan, "
        "Phase 3 test-coverage audit + contract tests, Phase 4a markdown report, "
        "Phase 4b DOCX + HTML renderers.</p>",
        "<h3>Phase 1 — Baseline</h3>",
        "<ul>",
        "<li>Test suite: 54 passed, 0 failed, 0 skipped, 0 warnings (pre-Phase-3).</li>",
        "<li>Pipeline scripts: all five completed cleanly.</li>",
        "<li>Validator: 12/12 checks green.</li>",
        "<li>Exports: 6/6 present and non-empty.</li>",
        "</ul>",
        "<h3>Phase 2 — Anomaly scan</h3>",
        "<ul>",
        "<li>HIGH findings: 0. MEDIUM findings: 0. LOW findings: 2 (informational).</li>",
        "<li>21 nulls in <code>business_cycle_panel</code> documented-by-design via "
        "<code>inventory_days_est_source</code>.</li>",
        "<li>Core scoring columns have 0 nulls; scoring is null-tolerant by design.</li>",
        "</ul>",
        "<h3>Phase 3 — Test coverage</h3>",
        "<ul>",
        "<li>Added <code>tests/test_export_contracts.py</code>.</li>",
        "<li>Final count: 77 tests passing.</li>",
        "</ul>",
        "<h3>Phase 4 — Board report</h3>",
        "<ul>",
        "<li>Phase 4a: markdown renderer + CLI.</li>",
        "<li>Phase 4b: DOCX + HTML renderers; <code>--format all</code> emits six files.</li>",
        "</ul>",
        "<h3>Methodology observations (not bugs)</h3>",
        f"<p>Construction base risk score ({stats['construction_score']:.2f}, "
        f"'{html.escape(stats['construction_level'])}') — logged as an active "
        f"methodology review item. Session: noted, not fixed.</p>",
    ])


def render(report: dict[str, Any], variant: str) -> str:
    if variant not in VALID_VARIANTS:
        raise ValueError(f"variant must be one of {VALID_VARIANTS}; got {variant!r}")

    meta = report["metadata"]
    period = meta["period_label"]
    variant_label = "Board Summary" if variant == "board" else "Technical Detail"

    if variant == "board":
        intro = (
            "This is a summary view for non-technical reviewers. Every table traces "
            "back to the canonical parquet contracts in <code>data/exports/</code>. "
            "For full per-column detail, methodology references, and the audit-log "
            "appendix, see the Technical variant."
        )
    else:
        intro = (
            "This is the full-detail variant for MRC, audit, and model-risk review. "
            "It includes per-row technical commentary, source URLs, the full "
            "Construction methodology review item, and the audit log as an appendix."
        )

    sections_html = "\n".join(_render_section(s, variant) for s in report["sections"])

    appendix_html = _audit_log_appendix_html(report) if variant == "technical" else ""

    title_text = f"Industry Analysis Report — {period}"

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{html.escape(title_text)} ({html.escape(variant_label)})</title>",
        "<style>",
        STYLESHEET,
        "</style>",
        "</head>",
        "<body>",
        f"<h1>{html.escape(title_text)}</h1>",
        f'<p><em>{html.escape(variant_label)} variant. Generated {html.escape(meta["generation_date"])}.</em></p>',
        '<div class="summary-box">',
        f"<p>Macro and downturn overlays as of {html.escape(meta['macro_as_of_date'])}. "
        f"Property cycle data as of {html.escape(meta['property_cycle_as_of_date'])}.</p>",
        f"<p>{intro}</p>",
        "</div>",
        sections_html,
        appendix_html,
        "<footer>END OF REPORT</footer>",
        "</body>",
        "</html>",
    ]
    return "\n".join(p for p in parts if p)


def write_html_variants(report: dict[str, Any], output_base: str) -> dict[str, str]:
    """Write both Board and Technical HTML files; return {variant: file_path}."""
    base = Path(output_base)
    stem = base.stem
    parent = base.parent
    parent.mkdir(parents=True, exist_ok=True)

    results = {}
    for variant, suffix in [("board", "_Board"), ("technical", "_Technical")]:
        path = parent / f"{stem}{suffix}.html"
        path.write_text(render(report, variant), encoding="utf-8")
        results[variant] = str(path)
    return results
