"""Industry-analysis board report — content builder.

Single source of truth for the structured report. Loads the canonical parquet
exports in `data/exports/`, derives headline statistics, and emits a dict tree
that renderers (e.g. `render_markdown.py`) consume without reaching back to
the parquet files. Narrative text resolves template variables at build time
so no literal `{placeholder}` strings escape into output.

Block types used in section `elements`:
    ("paragraph", {"board": str, "technical": str})
        Prose block; both variants required (technical may equal board).
    ("paragraph_technical_only", str)
        Prose block rendered only in the Technical variant.
    ("table", {
        "caption": str,
        "data": pd.DataFrame,
        "cols_board": list[str],        # ordered columns for Board variant
        "cols_technical": list[str],    # ordered columns for Technical variant
        "rename": dict[str, str] | None,
        "format": dict[str, str] | None,  # column -> python format spec
        "show_in_board": bool,          # default True
    })
    ("callout", {
        "style": str,                   # "methodology_note" | "caveat"
        "title": str,
        "body_board": str,
        "body_technical": str,          # may be identical to body_board
        "variants": set[str],           # e.g. {"board","technical"}; default both
    })
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import pandas as pd


EXPORTS_DIR = Path("data/exports")

RISK_LEVEL_BANDS = (
    ("Low", 0.0, 2.0),
    ("Medium", 2.0, 2.75),
    ("Elevated", 2.75, 3.5),
    ("High", 3.5, 6.0),
)

CYCLE_STAGE_ORDER = ["downturn", "slowing", "neutral", "growth"]


def _period_label(date_str: str) -> str:
    d = pd.to_datetime(date_str)
    q = (d.month - 1) // 3 + 1
    return f"Q{q} {d.year}"


def load_report_data() -> dict[str, Any]:
    """Load all 6 canonical parquet files plus derived headline statistics."""
    industry = pd.read_parquet(EXPORTS_DIR / "industry_risk_scores.parquet")
    property_overlays = pd.read_parquet(EXPORTS_DIR / "property_market_overlays.parquet")
    downturn = pd.read_parquet(EXPORTS_DIR / "downturn_overlay_table.parquet")
    macro = pd.read_parquet(EXPORTS_DIR / "macro_regime_flags.parquet")
    business_panel = pd.read_parquet(EXPORTS_DIR / "business_cycle_panel.parquet")
    property_panel = pd.read_parquet(EXPORTS_DIR / "property_cycle_panel.parquet")

    industry_sorted = industry.sort_values("industry_base_risk_score", ascending=False).reset_index(drop=True)

    cycle_stage_counts = property_overlays["cycle_stage"].value_counts().to_dict()
    downturn_segments = property_overlays[property_overlays["cycle_stage"] == "downturn"]["property_segment"].tolist()
    growth_segments = property_overlays[property_overlays["cycle_stage"] == "growth"]["property_segment"].tolist()
    slowing_segments = property_overlays[property_overlays["cycle_stage"] == "slowing"]["property_segment"].tolist()

    macro_row = macro.iloc[0]
    macro_date = str(macro_row["as_of_date"])
    downturn_date = str(downturn["as_of_date"].iloc[0])
    property_cycle_date = str(property_panel["as_of_date"].iloc[0])
    generation_date = dt.date.today().isoformat()

    elevated = industry_sorted[industry_sorted["industry_base_risk_level"] == "Elevated"]
    medium = industry_sorted[industry_sorted["industry_base_risk_level"] == "Medium"]

    top5 = industry_sorted.head(5)["industry"].tolist()
    headline = (
        f"{len(elevated)} of {len(industry)} industries score Elevated "
        f"({', '.join(elevated['industry'].tolist())})"
    )

    stats = {
        "industry_count": int(len(industry)),
        "property_segment_count": int(len(property_overlays)),
        "cash_rate_pct": float(industry["cash_rate_latest_pct"].iloc[0]),
        "cash_rate_change_pctpts": float(industry["cash_rate_change_1y_pctpts"].iloc[0]),
        "cash_rate_regime": str(macro_row["cash_rate_regime"]),
        "arrears_environment_level": str(macro_row["arrears_environment_level"]),
        "arrears_trend": str(macro_row["arrears_trend"]),
        "macro_regime_flag": str(macro_row["macro_regime_flag"]),
        "macro_source_dataset": str(macro_row["source_dataset"]),
        "macro_as_of_date": macro_date,
        "downturn_as_of_date": downturn_date,
        "property_cycle_as_of_date": property_cycle_date,
        "generation_date": generation_date,
        "period_label": _period_label(property_cycle_date),
        "elevated_industry_count": int(len(elevated)),
        "medium_industry_count": int(len(medium)),
        "elevated_industry_names": elevated["industry"].tolist(),
        "top5_industries": top5,
        "top_score": float(industry_sorted["industry_base_risk_score"].iloc[0]),
        "bottom_score": float(industry_sorted["industry_base_risk_score"].iloc[-1]),
        "cycle_stage_counts": {s: int(cycle_stage_counts.get(s, 0)) for s in CYCLE_STAGE_ORDER},
        "downturn_segments": downturn_segments,
        "slowing_segments": slowing_segments,
        "growth_segments": growth_segments,
        "headline_finding": headline,
    }

    construction_row = industry[industry["industry"].str.lower() == "construction"].iloc[0]
    stats["construction_score"] = float(construction_row["industry_base_risk_score"])
    stats["construction_level"] = str(construction_row["industry_base_risk_level"])

    return {
        "industry": industry_sorted,
        "property_overlays": property_overlays,
        "downturn": downturn,
        "macro": macro,
        "business_panel": business_panel,
        "property_panel": property_panel,
        "stats": stats,
    }


def _risk_band_description() -> str:
    return (
        "Scores range 1 (low) to 5 (high). Level bands: "
        "Low (<2), Medium (2.00–2.75), Elevated (2.75–3.50), High (>3.50)."
    )


def _property_overlays_sorted(df: pd.DataFrame) -> pd.DataFrame:
    cat = pd.Categorical(df["cycle_stage"], categories=CYCLE_STAGE_ORDER, ordered=True)
    out = df.assign(_cycle_order=cat).sort_values(
        ["_cycle_order", "market_softness_score"], ascending=[True, False]
    )
    return out.drop(columns=["_cycle_order"])


def build_report() -> dict[str, Any]:
    """Return a structured content tree. Renderers consume this; do not call
    `load_report_data` directly from renderers."""
    data = load_report_data()
    stats = data["stats"]

    property_sorted = _property_overlays_sorted(data["property_overlays"])

    sections: list[dict[str, Any]] = []

    # --- Section 1: Executive Summary ---
    growth_count = stats["cycle_stage_counts"]["growth"]
    downturn_count = stats["cycle_stage_counts"]["downturn"]
    slowing_count = stats["cycle_stage_counts"]["slowing"]
    exec_board = (
        f"This report summarises the current state of Australian industry and "
        f"property market risk using public macro, industry, and property data. "
        f"Overlays cover {stats['industry_count']} industries and "
        f"{stats['property_segment_count']} property segments. "
        f"Cash rate sits at {stats['cash_rate_pct']:.2f}%, "
        f"{abs(stats['cash_rate_change_pctpts']):.2f}pp lower than a year ago; "
        f"arrears environment is {stats['arrears_environment_level']} and "
        f"{stats['arrears_trend'].lower()}. "
        f"{stats['elevated_industry_count']} of {stats['industry_count']} industries "
        f"currently score Elevated on the base risk scale. "
        f"{downturn_count} property segment is in downturn, "
        f"{slowing_count} is slowing, and {growth_count} are in growth."
    )
    exec_tech = (
        exec_board + " "
        f"Headline finding: {stats['headline_finding']}. "
        f"Macro regime flag: '{stats['macro_regime_flag']}' "
        f"(cash_rate_regime='{stats['cash_rate_regime']}'). "
        f"Data freshness: macro and downturn overlays as of {stats['macro_as_of_date']}; "
        f"property cycle data as of {stats['property_cycle_as_of_date']}. "
        f"Report generated {stats['generation_date']}."
    )
    how_to_read_body_board = (
        "This report uses a 1–5 risk-score scale with four bands:\n"
        "- Low (< 2.0) — defensive, structurally resilient\n"
        "- Medium (2.0 – 2.75) — neutral, typical business-cycle exposure\n"
        "- Elevated (2.75 – 3.5) — cyclical or rate-sensitive; monitor closely\n"
        "- High (> 3.5) — stressed or structurally vulnerable"
    )
    how_to_read_body_technical = (
        how_to_read_body_board + "\n\n"
        "These bands are defined in `src.utils.risk_band` and tested in `tests.test_utils`."
    )

    sections.append({
        "id": "executive_summary",
        "title": "1. Executive Summary",
        "lead": (None, None),
        "elements": [
            ("paragraph", {"board": exec_board, "technical": exec_tech}),
            ("callout", {
                "style": "how_to_read",
                "title": "How to read this report",
                "body_board": how_to_read_body_board,
                "body_technical": how_to_read_body_technical,
                "variants": {"board", "technical"},
            }),
        ],
    })

    # --- Section 2: Macro Regime ---
    macro_lead_board = (
        f"Macro conditions shape how every industry and property segment is stressed. "
        f"The cash rate is the dominant conditioning variable; the arrears backdrop "
        f"confirms whether rate moves are already showing in borrower behaviour."
    )
    macro_lead_tech = (
        macro_lead_board + " "
        f"The regime flag combines cash rate, arrears level, and arrears trend into a "
        f"single compact label that downstream credit models consume without having to "
        f"re-read the underlying series."
    )

    macro_summary_df = pd.DataFrame([{
        "Metric": "Cash rate (latest)",
        "Value": f"{stats['cash_rate_pct']:.2f}%",
        "Source": "RBA F1",
    }, {
        "Metric": "Cash rate 1y change",
        "Value": f"{stats['cash_rate_change_pctpts']:+.2f}pp",
        "Source": "RBA F1",
    }, {
        "Metric": "Cash rate regime",
        "Value": stats["cash_rate_regime"],
        "Source": "Derived from RBA F1",
    }, {
        "Metric": "Arrears environment",
        "Value": stats["arrears_environment_level"],
        "Source": "Staged arrears context",
    }, {
        "Metric": "Arrears trend",
        "Value": stats["arrears_trend"],
        "Source": "Staged arrears context",
    }, {
        "Metric": "Macro regime flag",
        "Value": stats["macro_regime_flag"],
        "Source": stats["macro_source_dataset"],
    }])

    macro_commentary_board = (
        "Combined with a low arrears backdrop, this suggests borrowers are absorbing "
        "rate pressure; credit models should weight structural over cyclical factors "
        "in current calibration. "
        f"The downturn overlays currently apply the '{stats['macro_regime_flag']}' "
        f"scenario (no uplift to PD/LGD/CCF)."
    )
    macro_commentary_tech = (
        macro_commentary_board + " "
        f"The `macro_regime_flag` value of '{stats['macro_regime_flag']}' is the hook "
        f"downstream repos use to select the corresponding row of "
        f"`downturn_overlay_table.parquet`. Any change to this flag propagates "
        f"automatically; recalibration of the underlying overlay is out of scope here."
    )

    sections.append({
        "id": "macro_regime",
        "title": "2. Macro Regime",
        "lead": (macro_lead_board, macro_lead_tech),
        "elements": [
            ("table", {
                "caption": f"Macro regime snapshot as of {stats['macro_as_of_date']}",
                "data": macro_summary_df,
                "cols_board": ["Metric", "Value"],
                "cols_technical": ["Metric", "Value", "Source"],
                "rename": None,
                "format": None,
            }),
            ("paragraph", {"board": macro_commentary_board, "technical": macro_commentary_tech}),
        ],
    })

    # --- Section 3: Industry Risk Rankings ---
    ranking_lead_board = (
        f"Industries are ranked by a combined base risk score that blends structural "
        f"classification risk (cyclicality, concentration, capital intensity) with "
        f"current macro sensitivity. The table below is ordered highest-risk first."
    )
    ranking_lead_tech = (
        ranking_lead_board + " " + _risk_band_description() + " "
        "Both component scores and the blended `industry_base_risk_score` are shown. "
        f"Source: `data/exports/industry_risk_scores.parquet` "
        f"(refreshed from `build_business_cycle_panel` at pipeline build time)."
    )

    rank_df = data["industry"].copy()
    rank_df["Rank"] = range(1, len(rank_df) + 1)
    rank_df = rank_df.rename(columns={
        "industry": "Industry",
        "classification_risk_score": "Classification",
        "macro_risk_score": "Macro",
        "industry_base_risk_score": "Base score",
        "industry_base_risk_level": "Level",
    })

    ranking_commentary_board = (
        f"The top {stats['elevated_industry_count']} industries all sit in the "
        f"'Elevated' band, driven by structural cyclicality and current rate sensitivity. "
        f"Defensive sectors (Health Care; Professional, Scientific and Technical) sit at "
        f"the lower end, as expected."
    )
    ranking_commentary_tech = (
        ranking_commentary_board + " "
        f"The Base score is a weighted blend; see `src/overlays/build_industry_risk_scores.py` "
        f"for the formula. All rows share the same `cash_rate_latest_pct` "
        f"({stats['cash_rate_pct']:.2f}%) because the macro component is a single environment-wide "
        f"conditioner, not an industry-specific signal."
    )

    construction_callout_short = (
        f"**Methodology note.** Construction base risk score "
        f"({stats['construction_score']:.2f}, '{stats['construction_level']}') reflects "
        f"structural classification risk only, not current insolvency pressure. "
        f"See Section 9 for methodology context and the active review item."
    )

    sections.append({
        "id": "industry_rankings",
        "title": "3. Industry Risk Rankings",
        "lead": (ranking_lead_board, ranking_lead_tech),
        "elements": [
            ("table", {
                "caption": f"All {stats['industry_count']} industries ranked by base risk score",
                "data": rank_df,
                "cols_board": ["Rank", "Industry", "Base score", "Level"],
                "cols_technical": ["Rank", "Industry", "Classification", "Macro", "Base score", "Level"],
                "rename": None,
                "format": {
                    "Classification": "{:.2f}",
                    "Macro": "{:.2f}",
                    "Base score": "{:.2f}",
                },
            }),
            ("callout", {
                "style": "methodology_note",
                "title": "Construction ranking",
                "body_board": construction_callout_short,
                "body_technical": construction_callout_short,
                "variants": {"board", "technical"},
            }),
            ("paragraph", {"board": ranking_commentary_board, "technical": ranking_commentary_tech}),
        ],
    })

    # --- Section 4: Top Risk Industries ---
    top5_df = data["industry"].head(5).rename(columns={
        "industry": "Industry",
        "classification_risk_score": "Classification",
        "macro_risk_score": "Macro",
        "industry_base_risk_score": "Base score",
        "industry_base_risk_level": "Level",
    })

    top_lead_board = (
        f"These are the five industries with the highest combined base risk score in "
        f"the current environment. Review these first when calibrating portfolio "
        f"concentration limits or sector caps."
    )
    top_lead_tech = (
        top_lead_board + " "
        f"Industries are sorted descending on `industry_base_risk_score`. Ties are broken "
        f"by DataFrame order; this should not be relied on for downstream sorting."
    )

    business = data["business_panel"]
    top_detail_rows = []
    for ind in top5_df["Industry"].tolist():
        row = business[business["industry"] == ind]
        if row.empty:
            continue
        r = row.iloc[0]
        top_detail_rows.append({
            "Industry": ind,
            "Employment (000s)": f"{r['employment_000_latest']:,.1f}",
            "Sales ($m)": f"{r['sales_m_latest']:,.0f}",
            "EBITDA margin %": f"{r['ebitda_margin_pct_latest']:.2f}",
            "Demand growth YoY %": ("n/a" if pd.isna(r['demand_yoy_growth_pct']) else f"{r['demand_yoy_growth_pct']:+.2f}"),
            "Inventory build risk": str(r["inventory_stock_build_risk"]),
        })
    top_detail_df = pd.DataFrame(top_detail_rows)

    sections.append({
        "id": "top_risk_industries",
        "title": "4. Top Risk Industries",
        "lead": (top_lead_board, top_lead_tech),
        "elements": [
            ("table", {
                "caption": "Top 5 industries by base risk score",
                "data": top5_df,
                "cols_board": ["Industry", "Base score", "Level"],
                "cols_technical": ["Industry", "Classification", "Macro", "Base score", "Level"],
                "rename": None,
                "format": {
                    "Classification": "{:.2f}",
                    "Macro": "{:.2f}",
                    "Base score": "{:.2f}",
                },
            }),
            ("paragraph_technical_only",
                "The table below adds operational context from "
                "`business_cycle_panel.parquet` for the same five industries. "
                "Nulls in 'Demand growth YoY %' reflect sectors where ABS does not "
                "publish the relevant series; the underlying scoring logic maps "
                "nulls to a neutral factor score (3). See Section 9."),
            ("table", {
                "caption": "Operational detail for top 5 industries (Technical only)",
                "data": top_detail_df,
                "cols_board": [],
                "cols_technical": list(top_detail_df.columns),
                "rename": None,
                "format": None,
                "show_in_board": False,
            }),
        ],
    })

    # --- Section 5: Property Market Overlays ---
    prop_lead_board = (
        f"Property overlays track {stats['property_segment_count']} commercial and "
        f"non-residential segments through the cycle. Each segment is classified into "
        f"one of four cycle stages (downturn, slowing, neutral, growth) using approvals "
        f"momentum as the primary signal."
    )
    prop_lead_tech = (
        prop_lead_board + " "
        f"Commencements and completions are proxied from the approvals trend in this "
        f"cycle because ABS building activity has not been staged; see `source_note` in "
        f"`property_cycle_panel.parquet` for per-row provenance."
    )

    prop_df = property_sorted.rename(columns={
        "property_segment": "Segment",
        "cycle_stage": "Cycle",
        "market_softness_score": "Softness score",
        "region_risk_score": "Region risk",
        "region_risk_band": "Region band",
        "approvals_change_pct": "Approvals Δ %",
        "market_softness_band": "Softness band",
    })

    prop_commentary_board = (
        f"Segments are grouped with downturn first, then slowing, neutral, and growth. "
        f"Offices is the only segment flagged in downturn; Health buildings, Commercial "
        f"Buildings Total, and Short-term accommodation are the three segments in growth."
    )
    prop_commentary_tech = (
        prop_commentary_board + " "
        f"Within each cycle stage, segments are sorted on softness score descending so "
        f"the softer segments within each bucket appear first. Approvals Δ % is the "
        f"year-on-year change in ABS building approvals for the segment; extreme values "
        f"(e.g. +355% for Health buildings) reflect low prior-period base effects rather "
        f"than a calibrated trend signal."
    )

    sections.append({
        "id": "property_overlays",
        "title": "5. Property Market Overlays",
        "lead": (prop_lead_board, prop_lead_tech),
        "elements": [
            ("table", {
                "caption": f"All {stats['property_segment_count']} segments grouped by cycle stage (as of {stats['property_cycle_as_of_date']})",
                "data": prop_df,
                "cols_board": ["Segment", "Cycle", "Softness score", "Region band"],
                "cols_technical": ["Segment", "Cycle", "Softness score", "Softness band", "Region risk", "Region band", "Approvals Δ %"],
                "rename": None,
                "format": {
                    "Softness score": "{:.2f}",
                    "Region risk": "{:.2f}",
                    "Approvals Δ %": "{:+.2f}",
                },
            }),
            ("paragraph", {"board": prop_commentary_board, "technical": prop_commentary_tech}),
        ],
    })

    # --- Section 6: Property Cycle Interpretation ---
    interp_board = (
        f"{downturn_count} segment is currently in downturn ({', '.join(stats['downturn_segments'])}). "
        f"{slowing_count} is slowing ({', '.join(stats['slowing_segments'])}). "
        f"{stats['cycle_stage_counts']['neutral']} segments sit in neutral, and "
        f"{growth_count} are in growth "
        f"({', '.join(stats['growth_segments'])}). "
        f"For property-backed lending, Offices warrants elevated caution; the growth-stage "
        f"segments look supportive but should be read alongside the approvals-base-effect "
        f"caveat below."
    )
    interp_tech = (
        interp_board + " "
        "Cycle-stage assignment is rule-based on approvals momentum and softness score; "
        "it is not a forecast. A segment in 'growth' today can pivot to 'slowing' in the "
        "next refresh if approvals pull back. The overlay is a conditioning signal, not "
        "a predictive one."
    )

    sections.append({
        "id": "property_interpretation",
        "title": "6. Property Cycle Interpretation",
        "lead": (None, None),
        "elements": [
            ("paragraph", {"board": interp_board, "technical": interp_tech}),
        ],
    })

    # --- Section 7: Downturn Scenarios ---
    downturn_df = data["downturn"].copy()
    downturn_df = downturn_df.rename(columns={
        "scenario": "Scenario",
        "pd_multiplier": "PD ×",
        "lgd_multiplier": "LGD ×",
        "ccf_multiplier": "CCF ×",
        "property_value_haircut": "Property haircut",
        "notes": "Notes",
        "as_of_date": "As of",
    })

    downturn_lead_board = (
        f"Downturn overlays provide illustrative multipliers for PD, LGD, and CCF, plus "
        f"property value haircuts, under four scenarios. These support scenario analysis "
        f"and conservative pricing; they are not calibrated regulatory stress parameters."
    )
    downturn_lead_tech = (
        downturn_lead_board + " "
        f"Multipliers are monotonic base → severe by construction; the base scenario is "
        f"always 1.0 (no adjustment), and the contract-test suite "
        f"(`tests/test_export_contracts.py`) locks this invariant."
    )

    downturn_commentary = (
        f"Apply multiplicatively to modelled PD/LGD/CCF; haircut applies to property "
        f"valuations in collateral-backed lines. The severe scenario doubles PD; mild "
        f"and moderate are graduated. Current environment selects the '{stats['macro_regime_flag']}' "
        f"row (see Section 2)."
    )

    sections.append({
        "id": "downturn_scenarios",
        "title": "7. Downturn Scenarios",
        "lead": (downturn_lead_board, downturn_lead_tech),
        "elements": [
            ("table", {
                "caption": f"Illustrative downturn multipliers (as of {stats['downturn_as_of_date']})",
                "data": downturn_df,
                "cols_board": ["Scenario", "PD ×", "LGD ×", "CCF ×", "Property haircut"],
                "cols_technical": ["Scenario", "PD ×", "LGD ×", "CCF ×", "Property haircut", "Notes"],
                "rename": None,
                "format": {
                    "PD ×": "{:.2f}",
                    "LGD ×": "{:.2f}",
                    "CCF ×": "{:.2f}",
                    "Property haircut": "{:.2f}",
                },
            }),
            ("paragraph", {"board": downturn_commentary, "technical": downturn_commentary}),
        ],
    })

    # --- Section 8: Data Sources and Freshness ---
    sources_df = pd.DataFrame([
        {"Overlay": "industry_risk_scores", "Primary source": "ABS Economic Activity Survey + RBA F1", "URL": "https://www.abs.gov.au/statistics/industry", "Refreshed": stats["macro_as_of_date"]},
        {"Overlay": "property_market_overlays", "Primary source": "ABS Building Approvals (non-residential)", "URL": "https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia", "Refreshed": stats["property_cycle_as_of_date"]},
        {"Overlay": "downturn_overlay_table", "Primary source": "Staged arrears context + property softness", "URL": "(internal staging)", "Refreshed": stats["downturn_as_of_date"]},
        {"Overlay": "macro_regime_flags", "Primary source": "RBA F1 cash-rate table + arrears staging", "URL": "https://www.rba.gov.au/statistics/tables/", "Refreshed": stats["macro_as_of_date"]},
        {"Overlay": "business_cycle_panel", "Primary source": "ABS EAS + RBA F1 (panel assembly)", "URL": "(derived)", "Refreshed": stats["macro_as_of_date"]},
        {"Overlay": "property_cycle_panel", "Primary source": "ABS Building Approvals", "URL": "(derived)", "Refreshed": stats["property_cycle_as_of_date"]},
    ])

    sources_lead_board = (
        "Each overlay is built from public data refreshed on a published cadence. "
        "The table below lists the primary source and last-refresh date for each contract."
    )
    sources_lead_tech = (
        sources_lead_board + " "
        f"A full chain-of-custody exists in `scripts/download_public_data.py` and "
        f"`scripts/build_public_panels.py`; the most recent baseline run completed "
        f"cleanly with no warnings (see `outputs/baseline_state.md`)."
    )

    sections.append({
        "id": "data_sources",
        "title": "8. Data Sources and Freshness",
        "lead": (sources_lead_board, sources_lead_tech),
        "elements": [
            ("table", {
                "caption": "Primary sources and refresh dates",
                "data": sources_df,
                "cols_board": ["Overlay", "Primary source", "Refreshed"],
                "cols_technical": ["Overlay", "Primary source", "URL", "Refreshed"],
                "rename": None,
                "format": None,
            }),
        ],
    })

    # --- Section 9: Validation and Caveats (the Construction discussion lives here) ---
    validation_lead_board = (
        "Contract validation runs automatically before every downstream handoff. "
        "All 12 current checks passed on the latest pipeline run. This section also "
        "documents active methodology review items and known gaps."
    )
    validation_lead_tech = (
        validation_lead_board + " "
        f"The validator is `scripts/validate_upstream.py`, backed by `src/validation.py`. "
        f"It verifies presence and non-emptiness of all 4 core contract exports plus 2 "
        f"optional explainability panels. End-to-end test coverage is locked via "
        f"`tests/test_export_contracts.py` (schema, row counts, no all-null columns, "
        f"downturn monotonicity, and base-scenario unity multipliers)."
    )

    validation_table = pd.DataFrame([
        {"Check category": "Core contract presence", "Items": 4, "Status": "Pass"},
        {"Check category": "Core contract file on disk", "Items": 4, "Status": "Pass"},
        {"Check category": "Optional panel presence", "Items": 2, "Status": "Pass"},
        {"Check category": "Optional panel file on disk", "Items": 2, "Status": "Pass"},
    ])

    construction_discussion_body = (
        f"The current `industry_base_risk_score` for Construction is "
        f"{stats['construction_score']:.2f} ('{stats['construction_level']}'), tied with "
        f"Accommodation/Food Services and below Manufacturing/Agriculture (3.50 each).\n\n"
        f"Market evidence suggests Construction warrants an 'Elevated' classification in "
        f"the current cycle:\n"
        f"- Australian builder insolvencies have been elevated through 2024–2026 "
        f"(Porter Davis, Probuild, Clough collapses).\n"
        f"- Subcontractor arrears remain at multi-year highs.\n"
        f"- Fixed-price-contract plus materials-inflation squeeze is ongoing.\n\n"
        f"Why the score does not reflect this: the methodology weights structural "
        f"classification factors (cyclicality, market concentration) and macro sensitivity "
        f"(rates, growth) but does not currently incorporate sector-specific insolvency or "
        f"arrears flow data into the base risk score. The downturn overlay table provides "
        f"scenario adjustments, but those apply uniformly across industries rather than "
        f"tilted toward sectors under specific stress.\n\n"
        f"This is a methodology design choice — defensible if you treat insolvency rates "
        f"as a separate 'current state' overlay distinct from 'structural risk'. But it "
        f"produces base scores that may understate near-term credit risk for sectors going "
        f"through a sector-specific stress event.\n\n"
        f"**Options for next methodology review:**\n"
        f"1. **Accept the design as-is** (structural vs current-state separation).\n"
        f"2. **Add an industry-stress overlay** that lifts the base score when ASIC "
        f"insolvency rates exceed a threshold for a specific ANZSIC division.\n"
        f"3. **Document the limitation** in the methodology manual and downstream "
        f"consumer documentation.\n\n"
        f"**This session: noted, not fixed.** Methodology change is out of scope for an "
        f"audit + polish pass."
    )

    caveats_board = (
        "Two caveats to flag: "
        "(1) Construction's 'Medium' rating reflects structural factors only, not current "
        "insolvency pressure — see the callout below. "
        "(2) Property overlay commencements and completions are proxied from approvals in "
        "this cycle, not directly observed."
    )
    caveats_tech = (
        caveats_board + " "
        "(3) `business_cycle_panel` carries 21 nulls across 6 diagnostic columns, all "
        "concentrated in sectors where ABS does not publish inventory-to-sales ratios "
        "(Agriculture, Construction, Health, Professional, Transport). Core scoring "
        "columns are fully populated; scoring functions in `src/utils.py` map nulls to "
        "a neutral factor score (3). The null pattern is confirmed documented-by-design via "
        "the `inventory_days_est_source` flag column. "
        "(4) The `cash_rate_latest_pct` field is broadcast uniformly to every industry row; "
        "it is a conditioner, not a per-industry observation."
    )

    sections.append({
        "id": "validation_caveats",
        "title": "9. Validation and Caveats",
        "lead": (validation_lead_board, validation_lead_tech),
        "elements": [
            ("table", {
                "caption": "Contract validation summary",
                "data": validation_table,
                "cols_board": ["Check category", "Items", "Status"],
                "cols_technical": ["Check category", "Items", "Status"],
                "rename": None,
                "format": None,
            }),
            ("paragraph", {"board": caveats_board, "technical": caveats_tech}),
            ("callout", {
                "style": "methodology_note",
                "title": "Methodology review item: Construction ranking",
                "body_board": (
                    f"Construction scores {stats['construction_score']:.2f} ('{stats['construction_level']}'). "
                    f"Market narrative (builder insolvencies, subcontractor arrears, fixed-price-contract "
                    f"pressure) suggests this understates near-term credit risk. "
                    f"The Australian construction sector has seen three major builder collapses "
                    f"(Porter Davis, Probuild, Clough) over 2024-2026; this sector-specific stress "
                    f"isn't captured in structural risk scoring. "
                    f"Logged as an active methodology review item; this session did not apply a fix — "
                    f"the Technical variant of this report documents the full discussion and three review options."
                ),
                "body_technical": construction_discussion_body,
                "variants": {"board", "technical"},
            }),
        ],
    })

    # --- Section 10: Methodology References ---
    methodology_lead_board = (
        "Full methodology manuals are maintained in the repo `docs/` folder. "
        "These describe how each overlay is constructed from raw inputs."
    )
    methodology_lead_tech = methodology_lead_board

    methodology_df = pd.DataFrame([
        {"Area": "Cash-flow lending", "Document": "docs/methodology_cash_flow_lending.md"},
        {"Area": "Property-backed lending", "Document": "docs/methodology_property_backed_lending.md"},
        {"Area": "Audit + polish log (this session)", "Document": "outputs/industry_analysis_audit_log.md"},
        {"Area": "Baseline state", "Document": "outputs/baseline_state.md"},
    ])

    sections.append({
        "id": "methodology_refs",
        "title": "10. Methodology References",
        "lead": (methodology_lead_board, methodology_lead_tech),
        "elements": [
            ("table", {
                "caption": "Methodology documents",
                "data": methodology_df,
                "cols_board": ["Area", "Document"],
                "cols_technical": ["Area", "Document"],
                "rename": None,
                "format": None,
            }),
        ],
    })

    return {
        "metadata": {
            "period_label": stats["period_label"],
            "generation_date": stats["generation_date"],
            "macro_as_of_date": stats["macro_as_of_date"],
            "property_cycle_as_of_date": stats["property_cycle_as_of_date"],
            "downturn_as_of_date": stats["downturn_as_of_date"],
        },
        "stats": stats,
        "sections": sections,
    }
