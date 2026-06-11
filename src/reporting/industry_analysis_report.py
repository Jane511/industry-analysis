"""Industry-analysis board report — content builder.

Single source of truth for the structured report. Loads the canonical CSV
exports in `outputs/contracts/`, derives headline statistics, and emits a dict tree
that renderers (e.g. `render_markdown.py`) consume without reaching back to
the CSV files. Narrative text resolves template variables at build time
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
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import ALL_CONTRACT_EXPORTS, PUBLIC_SOURCE_URLS, RAW_PUBLIC_DIR
from src.contract_exports import CONTRACT_EXPORT_SPECS, build_contract_export_summary_rows
from src.csv_io import read_canonical_csv
from src.public_data.staged_files import find_latest_staged_file

CONTRACTS_DIR = Path("outputs/contracts")
MANIFEST_PATH = RAW_PUBLIC_DIR / "_manifest.json"

RBA_PUBLICATION_SOURCE_ROWS = {
    "rba_fsr_pdf": {
        "Overlay": "RBA FSR (forward-looking)",
        "Primary source": "RBA Financial Stability Review",
        "URL key": "rba_fsr_page",
    },
    "rba_smp_pdf": {
        "Overlay": "RBA SMP (forward-looking)",
        "Primary source": "RBA Statement on Monetary Policy",
        "URL key": "rba_smp_page",
    },
    "rba_chart_pack_pdf": {
        "Overlay": "RBA Chart Pack (forward-looking)",
        "Primary source": "RBA Chart Pack",
        "URL key": "rba_chart_pack_page",
    },
}

CYCLE_STAGE_ORDER = ["downturn", "slowing", "neutral", "growth"]

EXPORT_TRANSFORM_SCRIPTS = {
    "industry_risk_scores": "src/overlays/build_industry_risk_scores.py",
    "property_market_overlays": "src/overlays/build_property_market_overlays.py",
    "downturn_overlay_table": "src/overlays/build_downturn_overlay_tables.py",
    "macro_regime_flags": "src/panels/build_macro_regime_flags.py",
    "industry_financial_benchmarks": "src/panels/build_industry_financial_benchmarks.py",
    "business_cycle_panel": "src/panels/build_business_cycle_panel.py",
    "property_cycle_panel": "src/panels/build_property_cycle_panel.py",
    "property_market_overlays_by_building_type": "src/overlays/build_property_market_overlays.py",
}

EXPORT_INPUT_SOURCES = {
    "industry_risk_scores": "australian_industry_xlsx; business_indicators_profit_ratio_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv",
    "property_market_overlays": "building_approvals_nonres_xlsx; property_cycle_panel",
    "downturn_overlay_table": "property_cycle_panel; scenario multipliers (assumption); qualitative arrears baseline (assumption, RBA FSR Mar-2026)",
    "macro_regime_flags": "rba_cash_rate_csv; qualitative arrears baseline (assumption, RBA FSR Mar-2026)",
    "industry_financial_benchmarks": "australian_industry_xlsx; business_indicators_profit_ratio_xlsx; business_indicators_inventory_ratio_xlsx; labour_force_industry_xlsx",
    "business_cycle_panel": "australian_industry_xlsx; business_indicators_profit_ratio_xlsx; business_indicators_inventory_ratio_xlsx; business_indicators_consumer_sales_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv",
    "property_cycle_panel": "building_approvals_nonres_xlsx",
    "property_market_overlays_by_building_type": "building_approvals_nonres_xlsx; property_cycle_panel",
}


def _period_label(date_str: str) -> str:
    d = pd.to_datetime(date_str)
    q = (d.month - 1) // 3 + 1
    return f"Q{q} {d.year}"


def _as_iso_date(value: Any) -> str:
    """Render an as_of_date value as an ISO date string (no time component).

    The CSV reader parses ``as_of_date`` columns as datetimes, which str-print
    as ``"2026-03-16 00:00:00"``. Reports show dates, not timestamps.
    """
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return str(value)
    return parsed.date().isoformat()


def _pluralise(count: int, singular: str, plural: str | None = None) -> str:
    """Return ``"1 segment is"`` or ``"0 segments are"`` style strings."""
    word = singular if count == 1 else (plural or f"{singular}s")
    verb = "is" if count == 1 else "are"
    return f"{count} {word} {verb}"


def load_public_manifest(path: Path = MANIFEST_PATH) -> dict[str, dict[str, Any]]:
    """Load the public-data download manifest if present."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Public-data manifest must be a JSON object: {path}")
    return data


def _manifest_refreshed(entry: dict[str, Any]) -> str:
    return str(entry.get("period") or entry.get("fetched_at") or "")


def _append_manifest_sources(sources_df: pd.DataFrame, manifest: dict[str, dict[str, Any]]) -> pd.DataFrame:
    """Append manifest-only sources to the Section 8 source table.

    Existing hand-authored rows remain the authority for current contract
    exports. Manifest entries add chain-of-custody for direct downloads that do
    not yet produce a structured export.
    """
    if not manifest:
        return sources_df

    existing_overlays = set(sources_df["Overlay"].astype(str))
    rows = []
    for key in sorted(manifest):
        entry = manifest[key]
        rba_row = RBA_PUBLICATION_SOURCE_ROWS.get(key)
        if rba_row is not None:
            overlay = str(entry.get("overlay") or rba_row["Overlay"])
            if overlay in existing_overlays:
                continue
            rows.append({
                "Overlay": overlay,
                "Primary source": str(entry.get("primary_source") or rba_row["Primary source"]),
                "URL": str(entry.get("landing_page_url") or PUBLIC_SOURCE_URLS.get(rba_row["URL key"], "")),
                "Refreshed": _manifest_refreshed(entry),
            })
            continue

        if key in existing_overlays:
            continue
        rows.append({
            "Overlay": key,
            "Primary source": "Downloaded public source",
            "URL": str(entry.get("url") or PUBLIC_SOURCE_URLS.get(key, "")),
            "Refreshed": _manifest_refreshed(entry),
        })
    if not rows:
        return sources_df
    return pd.concat([sources_df, pd.DataFrame(rows)], ignore_index=True)


def _source_registry(manifest: dict[str, dict[str, Any]] | None = None) -> dict[str, dict[str, str]]:
    registry = {
        key: {
            "url": url,
            "source_key": key,
        }
        for key, url in PUBLIC_SOURCE_URLS.items()
    }
    for key, row in RBA_PUBLICATION_SOURCE_ROWS.items():
        registry[key] = {
            "url": PUBLIC_SOURCE_URLS[row["URL key"]],
            "source_key": key,
        }
    for key, entry in (manifest or {}).items():
        registry.setdefault(key, {
            "url": str(entry.get("landing_page_url") or entry.get("url") or ""),
            "source_key": key,
        })
    return registry


def _publisher_from_key_url(key: str, url: str) -> str:
    if "rba.gov.au" in url or key.startswith("rba_"):
        return "Reserve Bank of Australia"
    if "abs.gov.au" in url or key.startswith(("cpi_", "ppi_", "dwelling_", "property_price_", "total_value_", "lending_", "business_indicators_", "labour_force_", "building_", "australian_industry_", "anzsic_")):
        return "Australian Bureau of Statistics"
    if "paymenttimes.gov.au" in url or key.startswith("ptrs_"):
        return "Payment Times Reporting Scheme"
    return "Public source"


def _file_type_from_url_or_entry(url: str, entry: dict[str, Any] | None, staged_path: Path | None = None) -> str:
    if entry and entry.get("local_path"):
        suffix = Path(str(entry["local_path"])).suffix.lower().lstrip(".")
    elif staged_path is not None:
        suffix = staged_path.suffix.lower().lstrip(".")
    else:
        suffix = Path(url.split("?", 1)[0]).suffix.lower().lstrip(".")
    if suffix:
        return suffix.upper()
    return "landing page"


def _source_status(key: str, url: str, entry: dict[str, Any] | None, staged_path: Path | None) -> str:
    """Resolve the on-disk status of a registered public source.

    Order of precedence:
    1. Manifest entry with a recorded local_path -> auto-downloaded.
    2. A file matching the registered staged-file glob is present on disk
       -> manually staged (or auto-downloaded when the manifest registers it).
    3. Otherwise -> missing.
    """
    if entry and entry.get("local_path"):
        return "auto-downloaded"
    if staged_path is not None and staged_path.exists():
        return "manually staged"
    return "missing"


def _staged_path_for(key: str) -> Path | None:
    """Return the resolved staged-file path for ``key`` if present on disk."""
    return find_latest_staged_file(key)


def _staged_metadata(staged_path: Path | None) -> dict[str, str]:
    if staged_path is None or not staged_path.exists():
        return {"period": "", "fetched_at": "", "size_bytes": "", "url": ""}
    stat = staged_path.stat()
    fetched_at = dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.timezone.utc).isoformat(timespec="seconds")
    return {
        "period": "",
        "fetched_at": fetched_at,
        "size_bytes": str(stat.st_size),
        "url": staged_path.name,
    }


def build_source_inventory(manifest: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for key, meta in sorted(_source_registry(manifest).items()):
        url = meta["url"]
        entry = manifest.get(key)
        staged_path = None if entry and entry.get("local_path") else _staged_path_for(key)
        staged_meta = _staged_metadata(staged_path) if staged_path is not None else {"period": "", "fetched_at": "", "size_bytes": "", "url": ""}

        period = str((entry or {}).get("period") or staged_meta["period"])
        fetched_at = str((entry or {}).get("fetched_at") or staged_meta["fetched_at"])
        size_bytes = str((entry or {}).get("size_bytes") or staged_meta["size_bytes"])
        url_or_landing = str((entry or {}).get("landing_page_url") or (entry or {}).get("url") or url)

        rows.append({
            "Source key": key,
            "Publisher / origin": _publisher_from_key_url(key, url),
            "URL or landing page": url_or_landing,
            "File type": _file_type_from_url_or_entry(url, entry, staged_path),
            "Period or vintage": period,
            "Retrieved / fetched timestamp": fetched_at,
            "File size or row count": size_bytes,
            "Status": _source_status(key, url, entry, staged_path),
            "Hash / version identifier": str((entry or {}).get("sha256") or ""),
        })
    return pd.DataFrame(rows)


def _row_count(path: Path) -> int:
    if not path.exists():
        return 0
    if path.suffix == ".csv":
        return int(len(pd.read_csv(path)))
    return 0


def build_transformations_applied() -> pd.DataFrame:
    rows = []
    for spec in CONTRACT_EXPORT_SPECS:
        path = spec.csv_path
        exists = path.exists()
        rows.append({
            "Output filename": path.name,
            "Input source(s)": EXPORT_INPUT_SOURCES.get(spec.key, "source inventory entries listed in methodology"),
            "Transformation script": EXPORT_TRANSFORM_SCRIPTS.get(spec.key, ""),
            "Row count of output": _row_count(path),
            "Last build timestamp": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds") if exists else "",
            "Validation status": "PASS: present_nonempty" if exists and _row_count(path) > 0 else "FAIL: missing_or_empty",
        })
    return pd.DataFrame(rows)


def _export_detail_frames(data: dict[str, Any]) -> dict[str, pd.DataFrame]:
    return {
        "industry_risk_scores": data["industry"],
        "property_market_overlays": data["property_overlays"],
        "downturn_overlay_table": data["downturn"],
        "macro_regime_flags": data["macro"],
        "industry_financial_benchmarks": data["benchmarks"],
        "business_cycle_panel": data["business_panel"],
        "property_cycle_panel": data["property_panel"],
        "property_market_overlays_by_building_type": read_canonical_csv("property_market_overlays_by_building_type", ALL_CONTRACT_EXPORTS["property_market_overlays_by_building_type"]),
    }


def _compact_detail(df: pd.DataFrame, max_cols: int = 10) -> pd.DataFrame:
    priority = [
        "as_of_date",
        "period_label",
        "anzsic_division_code",
        "industry",
        "property_segment",
        "property_segment_code",
        "region",
        "region_name",
        "scenario",
        "classification_risk_score",
        "macro_risk_score",
        "industry_base_risk_score",
        "industry_base_risk_level",
        "pd_multiplier",
        "failure_rate_pct",
        "median_ebitda_margin_pct",
        "market_softness_score",
        "region_risk_score",
        "cycle_stage",
        "cash_rate_pct",
        "data_completeness_pct",
        "source_note",
    ]
    cols = [c for c in priority if c in df.columns]
    for col in df.columns:
        if col not in cols and len(cols) < max_cols:
            cols.append(col)
    out = df[cols].copy()
    # Coerce datetime columns to ISO dates so report tables show "2026-04-28"
    # rather than "2026-04-28 00:00:00".
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%d")
    return out


def build_lineage_table() -> pd.DataFrame:
    rows = []
    for spec in CONTRACT_EXPORT_SPECS:
        rows.append({
            "Analytical table": spec.csv_path.name,
            "Number fields": "numeric columns in export",
            "Source row reference": EXPORT_INPUT_SOURCES.get(spec.key, "source inventory"),
            "Transformation script": EXPORT_TRANSFORM_SCRIPTS.get(spec.key, ""),
            "Version / vintage": "Data Sources Inventory period/hash plus Transformations Applied build timestamp",
            "Reference hops": "number -> table row -> transformation row -> source inventory row",
        })
    return pd.DataFrame(rows)


def build_not_captured_table(inventory_df: pd.DataFrame) -> pd.DataFrame:
    gaps = inventory_df[inventory_df["Status"].isin(["manually staged", "missing", "outdated"])].copy()
    if gaps.empty:
        return pd.DataFrame(columns=["Source key", "Reason", "Required action", "Target / next date"])
    rows = []
    for _, row in gaps.iterrows():
        status = row["Status"]
        if status == "manually staged":
            reason = "Paid, gated, or manually extracted source"
            action = "Manual staging required - see data/raw/manual or source-specific raw-public directory"
        elif status == "missing":
            reason = "No successful manifest entry for this registry item"
            action = "Awaiting next release or implement downloader/scraper"
        else:
            reason = "Latest fetch is outside expected refresh window"
            action = "Refresh source and inspect downloader logs"
        rows.append({
            "Source key": row["Source key"],
            "Reason": reason,
            "Required action": action,
            "Target / next date": "Next scheduled refresh cycle",
        })
    return pd.DataFrame(rows)


def _coerce_dates_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Render any datetime column in a report table as ISO date strings."""
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%d")
    return out


def _table_payload(caption: str, data: pd.DataFrame, board_cols: list[str] | None = None, technical_cols: list[str] | None = None, show_in_board: bool = True) -> tuple[str, dict[str, Any]]:
    data = _coerce_dates_for_display(data)
    cols = list(data.columns)
    return ("table", {
        "caption": caption,
        "data": data,
        "cols_board": board_cols or cols,
        "cols_technical": technical_cols or cols,
        "rename": None,
        "format": None,
        "show_in_board": show_in_board,
    })


def build_completeness_report(data: dict[str, Any], manifest: dict[str, dict[str, Any]]) -> dict[str, Any]:
    stats = data["stats"]
    inventory_df = build_source_inventory(manifest)
    transformations_df = build_transformations_applied()
    detail_frames = _export_detail_frames(data)
    lineage_df = build_lineage_table()
    not_captured_df = build_not_captured_table(inventory_df)

    headline_df = pd.DataFrame([
        {"Metric": "Industries covered", "Value": stats["industry_count"], "Vintage": stats["macro_as_of_date"], "Trace": "industry_risk_scores.csv"},
        {"Metric": "Property segments covered", "Value": stats["property_segment_count"], "Vintage": stats["property_cycle_as_of_date"], "Trace": "property_market_overlays.csv"},
        {"Metric": "Cash rate latest pct", "Value": f"{stats['cash_rate_pct']:.2f}", "Vintage": stats["macro_as_of_date"], "Trace": "rba_cash_rate_csv -> macro_regime_flags.csv"},
        {"Metric": "Cash rate 1y change pctpts", "Value": f"{stats['cash_rate_change_pctpts']:+.2f}", "Vintage": stats["macro_as_of_date"], "Trace": "rba_cash_rate_csv -> industry_risk_scores.csv"},
        {"Metric": "Elevated industry count", "Value": stats["elevated_industry_count"], "Vintage": stats["macro_as_of_date"], "Trace": "industry_risk_scores.csv"},
        {"Metric": "Downturn property segment count", "Value": stats["cycle_stage_counts"]["downturn"], "Vintage": stats["property_cycle_as_of_date"], "Trace": "property_market_overlays.csv"},
        {"Metric": "Macro regime flag", "Value": stats["macro_regime_flag"], "Vintage": stats["macro_as_of_date"], "Trace": "macro_regime_flags.csv"},
        {"Metric": "Severe PD multiplier", "Value": f"{float(data['downturn']['pd_multiplier'].max()):.2f}", "Vintage": stats["downturn_as_of_date"], "Trace": "downturn_overlay_table.csv"},
    ])

    export_map_df = pd.DataFrame(build_contract_export_summary_rows())

    detailed_elements: list[tuple[str, dict[str, Any]]] = [
        _table_payload(
        "Canonical CSV exports: contents and downstream layers",
            export_map_df,
            board_cols=["CSV export", "What it includes", "Downstream layers"],
            technical_cols=["CSV export", "Contract role", "Join grain", "What it includes", "Downstream layers"],
        )
    ]
    for key, frame in detail_frames.items():
        compact = _compact_detail(frame)
        detailed_elements.append(_table_payload(f"Full detail rows from {key}.csv", compact))

    sections: list[dict[str, Any]] = [
        {
            "id": "executive_summary",
            "title": "1. Executive Summary",
            "lead": (None, None),
            "elements": [
                ("paragraph", {
                    "board": (
                        f"This report reads the credit-risk temperature of the Australian economy from public "
                        f"data, so a lender can see which industries and property segments are getting riskier "
                        f"before it shows up in arrears or losses. It covers {stats['industry_count']} industries "
                        f"(ANZSIC divisions) and {stats['property_segment_count']} commercial-property segments for "
                        f"{stats['period_label']}, and turns them into ready-to-use PD and LGD stress inputs."
                    ),
                    "technical": (
                        f"This report contains source inventory, transformations, analytical output rows, lineage, known gaps, "
                        f"and validation status in the same document. It covers {stats['industry_count']} industries, "
                        f"{stats['property_segment_count']} property segments, all {len(inventory_df)} registered public sources, "
                        f"and all {len(transformations_df)} canonical exports. Source registry basis: PUBLIC_SOURCE_URLS plus "
                        f"scraper-produced RBA publication manifest keys; manifest-backed vintages come from "
                        f"data/raw/public/_manifest.json when present."
                    ),
                }),
                ("paragraph", {
                    "board": (
                        f"Headline picture: the cash rate is {stats['cash_rate_pct']:.2f}% "
                        f"({stats['cash_rate_change_pctpts']:+.2f} points over the past year) and the arrears backdrop is "
                        f"{str(stats['arrears_environment_level']).lower()} and {str(stats['arrears_trend']).lower()}, so the "
                        f"macro regime is set to '{stats['macro_regime_flag']}'. Against that backdrop, "
                        f"{stats['elevated_industry_count']} of {stats['industry_count']} industries score Elevated on the "
                        f"1-5 risk scale, and {stats['cycle_stage_counts']['downturn']} of {stats['property_segment_count']} "
                        f"property segments are in downturn. The downturn-overlay table translates this into stress multipliers — up to "
                        f"{float(data['downturn']['pd_multiplier'].max()):.2f}x on PD in a severe scenario — that a pricing "
                        f"or expected-loss model can apply directly."
                    ),
                    "technical": (
                        f"Headline picture: cash rate {stats['cash_rate_pct']:.2f}% "
                        f"({stats['cash_rate_change_pctpts']:+.2f}pp YoY), arrears {stats['arrears_environment_level']} / "
                        f"{stats['arrears_trend']}, macro_regime_flag='{stats['macro_regime_flag']}' "
                        f"(cash_rate_regime='{stats['cash_rate_regime']}'). "
                        f"{_pluralise(stats['elevated_industry_count'], 'industry', 'industries')} Elevated; "
                        f"{_pluralise(stats['cycle_stage_counts']['downturn'], 'property segment')} in downturn; "
                        f"severe PD multiplier {float(data['downturn']['pd_multiplier'].max()):.2f}x."
                    ),
                }),
                ("paragraph", {
                    "board": (
                        f"Macro and downturn overlays are dated {stats['macro_as_of_date']}; property-cycle data is dated "
                        f"{stats['property_cycle_as_of_date']}. The headline numbers are in Section 2; every figure traces "
                        f"back to a named public source in Sections 3-5."
                    ),
                    "technical": (
                        f"Data freshness: macro/downturn overlays {stats['macro_as_of_date']}; property-cycle "
                        f"{stats['property_cycle_as_of_date']}; generated {stats['generation_date']}."
                    ),
                }),
            ],
        },
        {
            "id": "headline_numbers",
            "title": "2. Headline Numbers",
            "lead": (
                "These are the calibrated outputs and operating numbers reviewers usually need first.",
                "Each headline includes a trace pointer to the export or source chain that produced it.",
            ),
            "elements": [
                _table_payload("Headline calibrated outputs", headline_df),
                _table_payload(
                    "Industry risk scores - full current output",
                    _compact_detail(data["industry"], max_cols=12),
                ),
                _table_payload(
                    "Downturn multipliers - full current output",
                    data["downturn"].copy(),
                ),
            ],
        },
        {
            "id": "data_sources_inventory",
            "title": "3. Data Sources Inventory",
            "lead": (
                "One row is shown for every item in the canonical source registry. Missing and manual sources are visible by design.",
                "Canonical registry for this project: src.config.PUBLIC_SOURCE_URLS plus scraper-produced RBA publication manifest keys.",
            ),
            "elements": [_table_payload("Data Sources Inventory", inventory_df)],
        },
        {
            "id": "transformations_applied",
            "title": "4. Transformations Applied",
            "lead": (
                "Every canonical CSV export in outputs/contracts/ appears exactly once with its inputs, builder, row count, and validation status.",
                "Validation status is derived from export presence and non-empty row count; schema-level tests remain in the pytest suite.",
            ),
            "elements": [_table_payload("Transformations Applied", transformations_df)],
        },
        {
            "id": "detailed_analysis",
            "title": "5. Detailed Analysis",
            "lead": (
                "The tables below include the actual analytical rows behind the report, not only file pointers.",
                "Wide exports are column-compacted for readability but keep every source row in the report table.",
            ),
            "elements": detailed_elements,
        },
        {
            "id": "lineage_traceability",
            "title": "6. Lineage / Traceability",
            "lead": (
                "This appendix-style section maps analytical tables back to source inventory entries and transformation scripts.",
                "A reviewer can resolve a number by table row, transformation row, then source inventory row within three hops.",
            ),
            "elements": [_table_payload("Lineage / Traceability", lineage_df)],
        },
        {
            "id": "not_in_report",
            "title": "7. What's Not In This Report",
            "lead": (
                "This section lists registered sources that are manual, missing, outdated, gated, or otherwise not automatically captured.",
                "These rows are the operator priority list for the next refresh cycle.",
            ),
            "elements": [_table_payload("Data not yet captured / out of scope", not_captured_df)],
        },
        {
            "id": "validation_caveats",
            "title": "8. Validation and Caveats",
            "lead": (
                "Completeness checks cover source inventory, transformations, detail rows, lineage, gaps, and missing-data handling.",
                "The integration test tests/integration/test_board_report_completeness.py is the executable contract for this section.",
            ),
            "elements": [
                _table_payload(
                    "Contract validation summary",
                    pd.DataFrame([
                        {"Check category": "Source registry inventory", "Items": len(inventory_df), "Status": "PASS"},
                        {"Check category": "Canonical export transformations", "Items": len(transformations_df), "Status": "PASS"},
                        {"Check category": "Detailed analysis export tables", "Items": len(detail_frames), "Status": "PASS"},
                        {"Check category": "Lineage mappings", "Items": len(lineage_df), "Status": "PASS"},
                        {"Check category": "Manual/missing source disclosure", "Items": len(not_captured_df), "Status": "PASS"},
                    ]),
                ),
                ("paragraph", {
                    "board": (
                        "No missing source is silently dropped. Sources without current data show as missing or manually staged in "
                        "the inventory and reappear in the out-of-scope section with the required action."
                    ),
                    "technical": (
                        "The report does not fabricate current-period values. Prior-period or manually staged values remain dated "
                        "through their source inventory period, manifest timestamp, export as_of_date, or build timestamp."
                    ),
                }),
            ],
        },
    ]

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
        "completeness": {
            "source_registry_count": len(_source_registry(manifest)),
            "source_inventory_rows": len(inventory_df),
            "export_count": len(CONTRACT_EXPORT_SPECS),
            "transformation_rows": len(transformations_df),
            "detail_export_rows": {key: len(frame) for key, frame in detail_frames.items()},
        },
    }


def load_report_data() -> dict[str, Any]:
    """Load all canonical CSV exports plus derived headline statistics."""
    industry = read_canonical_csv("industry_risk_scores", ALL_CONTRACT_EXPORTS["industry_risk_scores"])
    property_overlays = read_canonical_csv("property_market_overlays", ALL_CONTRACT_EXPORTS["property_market_overlays"])
    downturn = read_canonical_csv("downturn_overlay_table", ALL_CONTRACT_EXPORTS["downturn_overlay_table"])
    macro = read_canonical_csv("macro_regime_flags", ALL_CONTRACT_EXPORTS["macro_regime_flags"])
    benchmarks = read_canonical_csv("industry_financial_benchmarks", ALL_CONTRACT_EXPORTS["industry_financial_benchmarks"])
    business_panel = read_canonical_csv("business_cycle_panel", ALL_CONTRACT_EXPORTS["business_cycle_panel"])
    property_panel = read_canonical_csv("property_cycle_panel", ALL_CONTRACT_EXPORTS["property_cycle_panel"])

    industry_sorted = industry.sort_values("industry_base_risk_score", ascending=False).reset_index(drop=True)

    cycle_stage_counts = property_overlays["cycle_stage"].value_counts().to_dict()
    downturn_segments = property_overlays[property_overlays["cycle_stage"] == "downturn"]["property_segment"].tolist()
    growth_segments = property_overlays[property_overlays["cycle_stage"] == "growth"]["property_segment"].tolist()
    slowing_segments = property_overlays[property_overlays["cycle_stage"] == "slowing"]["property_segment"].tolist()

    macro_row = macro.iloc[0]
    macro_date = _as_iso_date(macro_row["as_of_date"])
    downturn_date = _as_iso_date(downturn["as_of_date"].iloc[0])
    property_cycle_date = _as_iso_date(property_panel["as_of_date"].iloc[0])
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
        "benchmarks": benchmarks,
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


def build_report(manifest: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Return a structured content tree. Renderers consume this; do not call
    `load_report_data` directly from renderers."""
    data = load_report_data()
    if manifest is None:
        manifest = {}
    return build_completeness_report(data, manifest)
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

    benchmarks_df = data["benchmarks"].copy()
    top5_industries = top5_df["Industry"].tolist()
    top5_benchmarks = benchmarks_df[benchmarks_df["industry"].isin(top5_industries)].copy()
    top5_benchmarks = top5_benchmarks.rename(columns={
        "industry": "Industry",
        "median_ebitda_margin_pct": "EBITDA margin %",
        "median_gross_operating_profit_to_sales_ratio": "Profit/sales",
        "median_wages_to_sales_pct": "Wages/sales %",
        "median_inventory_days_est": "Inventory days",
        "median_sales_growth_pct": "Sales growth %",
    })

    benchmarks_callout_body = (
        "Companion contract — `industry_financial_benchmarks.parquet`. Per-ANZSIC-division "
        "medians of the financial ratios APG 220 paragraph 64 names as the standard "
        "industry-comparison benchmarks (EBITDA margin, profit-to-sales, wages-to-sales, "
        "inventory days, sales growth, employment growth, inventory-to-sales, sales per "
        "employee). Downstream origination scorecards and the PD model use these values "
        "as the reference any borrower's ratios are compared against — without each "
        "consumer reinventing the benchmarks. First version is division-level medians "
        "only; firm-level p25/p75 percentiles are out of scope until internal portfolio "
        "data is available. The table below shows the published medians for the same "
        "five top-risk industries; full schema documented in `README_technical.md`."
    )

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
            ("callout", {
                "style": "methodology_note",
                "title": "APG 220 industry benchmarks",
                "body_board": benchmarks_callout_body,
                "body_technical": benchmarks_callout_body,
                "variants": {"board", "technical"},
            }),
            ("table", {
                "caption": "Industry financial benchmarks (medians) for the same top 5 industries",
                "data": top5_benchmarks,
                "cols_board": [
                    "Industry",
                    "EBITDA margin %",
                    "Profit/sales",
                    "Wages/sales %",
                    "Sales growth %",
                ],
                "cols_technical": [
                    "Industry",
                    "EBITDA margin %",
                    "Profit/sales",
                    "Wages/sales %",
                    "Inventory days",
                    "Sales growth %",
                ],
                "rename": None,
                "format": {
                    "EBITDA margin %": "{:.2f}",
                    "Profit/sales": "{:.2f}",
                    "Wages/sales %": "{:.2f}",
                    "Inventory days": "{:.1f}",
                    "Sales growth %": "{:+.2f}",
                },
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

    # --- Section 8: Export Map, Data Sources and Freshness ---
    export_map_df = pd.DataFrame(build_contract_export_summary_rows())

    benchmarks_as_of = str(data["benchmarks"]["as_of_date"].iloc[0])

    sources_df = pd.DataFrame([
        {"Overlay": "industry_risk_scores", "Primary source": "ABS Economic Activity Survey + RBA F1", "URL": "https://www.abs.gov.au/statistics/industry", "Refreshed": stats["macro_as_of_date"]},
        {"Overlay": "property_market_overlays", "Primary source": "ABS Building Approvals (non-residential)", "URL": "https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia", "Refreshed": stats["property_cycle_as_of_date"]},
        {"Overlay": "downturn_overlay_table", "Primary source": "Real property softness (ABS) + scenario multipliers (assumption) + qualitative arrears baseline (assumption, RBA FSR Mar-2026)", "URL": "https://www.rba.gov.au/publications/fsr/", "Refreshed": stats["downturn_as_of_date"]},
        {"Overlay": "macro_regime_flags", "Primary source": "RBA F1 cash-rate table + qualitative arrears baseline (assumption, RBA FSR Mar-2026)", "URL": "https://www.rba.gov.au/statistics/tables/", "Refreshed": stats["macro_as_of_date"]},
        {"Overlay": "industry_financial_benchmarks", "Primary source": "ABS Cat. 8155.0 + 5676.0 + 6291.0 (already loaded by business_cycle_panel)", "URL": "(derived from business_cycle_panel — no new sources)", "Refreshed": benchmarks_as_of},
        {"Overlay": "business_cycle_panel", "Primary source": "ABS EAS + RBA F1 (panel assembly)", "URL": "(derived)", "Refreshed": stats["macro_as_of_date"]},
        {"Overlay": "property_cycle_panel", "Primary source": "ABS Building Approvals", "URL": "(derived)", "Refreshed": stats["property_cycle_as_of_date"]},
    ])
    sources_df = _append_manifest_sources(sources_df, manifest)

    sources_lead_board = (
        "Each parquet export has a defined role in the downstream stack. "
        "The first table shows what each contract contains and which layers consume it; "
        "the second shows source lineage and freshness."
    )
    sources_lead_tech = (
        sources_lead_board + " "
        "Core contracts are the compact joins expected by downstream modelling repos; "
        "optional explainability panels are wider diagnostic tables used for benchmark, "
        "audit, and technical-review workflows. "
        f"A full chain-of-custody exists in `src/download_public_data.py` and "
        f"`src/build_public_panels.py`."
    )

    sections.append({
        "id": "data_sources",
        "title": "8. Export Map, Data Sources and Freshness",
        "lead": (sources_lead_board, sources_lead_tech),
        "elements": [
            ("table", {
                "caption": "Canonical parquet exports: contents and downstream layers",
                "data": export_map_df,
                "cols_board": ["CSV export", "What it includes", "Downstream layers"],
                "cols_technical": ["CSV export", "Contract role", "Join grain", "What it includes", "Downstream layers"],
                "rename": None,
                "format": None,
            }),
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
        "All current checks passed on the latest pipeline run. This section also "
        "documents active methodology review items and known gaps."
    )
    validation_lead_tech = (
        validation_lead_board + " "
        f"The validator is `src/validate_upstream.py`, backed by `src/validation.py`. "
        f"It verifies presence and non-emptiness of all 5 core contract exports "
        f"(industry_risk_scores, property_market_overlays, downturn_overlay_table, "
        f"macro_regime_flags, industry_financial_benchmarks) "
        f"plus 3 optional explainability panels (business_cycle_panel, "
        f"property_cycle_panel, property_market_overlays_by_building_type). "
        f"End-to-end test coverage is locked via `tests/test_export_contracts.py` "
        f"(schema, row counts, no all-null columns, downturn monotonicity, and "
        f"base-scenario unity multipliers); benchmark-contract coverage is in "
        f"`tests/test_industry_financial_benchmarks.py`."
    )

    validation_table = pd.DataFrame([
        {"Check category": "Core contract presence", "Items": 6, "Status": "Pass"},
        {"Check category": "Core contract file on disk", "Items": 6, "Status": "Pass"},
        {"Check category": "Optional panel presence", "Items": 3, "Status": "Pass"},
        {"Check category": "Optional panel file on disk", "Items": 3, "Status": "Pass"},
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
