"""Build canonical property-market overlay table.

The PD workbook's three property-backed products (bridging, development,
commercial_property) look up their industry-neutral-to-deal-level multiplier
from this overlay. Each lookup is ``overlay[overlay['property_segment_code']
== code].iloc[0]['pd_multiplier']`` — so the contract must publish exactly
one row per canonical ``property_segment_code`` in
``{RES, CRE, IND, RET, CON}``.

What this builder produces
--------------------------

* ``build_property_market_overlays`` — the **contract** export: exactly five
  rows, one per segment code. Each row's score and multiplier are
  exposure-weighted aggregations of the constituent building-approval
  categories that map to that code. The shared
  ``SCORE_TO_MULTIPLIER_LADDER`` is applied once, after aggregation, so the
  published ``pd_multiplier`` corresponds to the aggregated composite.

* ``build_property_market_overlays_by_building_type`` — the **explainability**
  export: one row per ABS building-approval category (typically 11) with each
  category's own softness, region-risk, approvals-change, and the
  ``property_segment_code`` it rolls up into. Reviewers who want to see the
  constituent building types can inspect this table without re-running the
  pipeline.

Notes on the CON (Construction) row
-----------------------------------

``CON`` stands for "Construction (non-residential development)" and represents
the non-residential construction pipeline as a whole. It is computed from the
**sum / exposure-weighted mean of the specific non-residential categories**
(offices, retail, industrial, warehouses, health, education, accommodation,
aged care, agricultural). The ABS "Total Non-residential" line is excluded
from the CON aggregate because it is itself the all-category sum and would
double-count. The two mid-level aggregates ("Commercial Buildings - Total"
and "Industrial Buildings - Total") are also excluded for the same reason —
they are retained on the explainability export for reviewer reference only.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from src.overlays.build_industry_risk_scores import score_to_pd_multiplier, score_to_risk_level
from src.panels.build_macro_context_panel import residential_approvals_signal


PROPERTY_REFERENCE_DERIVED_COLUMNS = (
    "median_dwelling_price_aud",
    "annual_price_change_pct",
    "peak_to_trough_decline_pct",
    "auction_clearance_rate_pct",
    "median_days_on_market",
    "median_vendor_discount_pct",
    "vacancy_rate_pct",
    "median_weekly_rent_aud",
    "rental_yield_gross_pct",
    "as_of_property_reference_date",
    "property_reference_status",
    "contributing_sources",
)


# Maps each ABS building-approval category to the canonical property segment
# code the PD workbook consumes. The three aggregate labels ("Total
# Non-residential", "Commercial Buildings - Total", "Industrial Buildings -
# Total") are intentionally absent from this map: they are kept on the
# explainability export (via BUILDING_TYPE_EXPLAINABILITY_ROLE below) but
# excluded from the five-row contract so CON / CRE / IND are not double-
# counted.
PROPERTY_SEGMENT_CODE_MAP: dict[str, str] = {
    "Offices": "CRE",
    "Education buildings": "CRE",
    "Short term accommodation buildings": "CRE",
    "Aged care facilities": "CRE",
    "Health buildings": "CRE",
    "Warehouses": "IND",
    "Agricultural and aquacultural buildings": "IND",
    "Retail and wholesale trade buildings": "RET",
}

# Aggregate rows we surface on the explainability export but exclude from
# the contract aggregation. Their role on the explainability export is
# strictly reviewer-reference.
AGGREGATE_BUILDING_TYPES: frozenset[str] = frozenset(
    {
        "Total Non-residential",
        "Commercial Buildings - Total",
        "Industrial Buildings - Total",
    }
)

# Published segment-code universe — every row on the contract carries one
# of these, and every code appears exactly once.
VALID_PROPERTY_SEGMENT_CODES: tuple[str, ...] = ("RES", "CRE", "IND", "RET", "CON")

# Stable display names per segment code (used as ``property_segment`` on the
# contract export). Downstream consumers read by code, not by display name,
# but board reviewers read the display name.
PROPERTY_SEGMENT_DISPLAY_NAMES: dict[str, str] = {
    "RES": "Residential",
    "CRE": "Commercial (office, health, education, accommodation)",
    "IND": "Industrial / Warehouse",
    "RET": "Retail Property",
    "CON": "Construction (non-residential development)",
}

_RESIDENTIAL_PLACEHOLDER_SOURCE_NOTE = (
    "Residential placeholder — ABS Cat. 8752.0 residential dwelling-approvals "
    "file not yet staged; RES row uses a neutral composite pending that upgrade."
)
_RESIDENTIAL_NEUTRAL_SCORE = 2.50


def _residential_signal_from_approvals() -> dict | None:
    """Derive an RES-row signal from ABS Cat. 8752.0 residential approvals.

    Returns ``None`` if the file is absent so the caller falls back to the
    placeholder. When present, returns the softness/region-risk/approvals-
    change triplet plus a real source note.
    """
    approvals = residential_approvals_signal()
    if approvals.empty:
        return None
    total_row = approvals[approvals["dwelling_type"] == "total"]
    if total_row.empty:
        total_row = approvals.iloc[[-1]]
    yoy = float(total_row.iloc[0]["yoy_pct_change"])
    trend = float(total_row.iloc[0].get("trend_3m_yoy_pct", float("nan")))
    # Map approvals YoY into the same 1–5 softness scale used elsewhere:
    # strong growth → low softness (1.5); flat → 2.5; deep decline → 4.0+.
    if pd.isna(yoy):
        score = _RESIDENTIAL_NEUTRAL_SCORE
    else:
        score = float(np.clip(2.5 - yoy / 30.0, 1.2, 4.5))
    return {
        "softness": round(score, 2),
        "approvals_change_pct": round(yoy, 2) if not pd.isna(yoy) else float("nan"),
        "trend_3m_yoy_pct": round(trend, 2) if not pd.isna(trend) else float("nan"),
        "source_note": (
            f"Residential signal from ABS Cat. 8752.0 dwelling approvals "
            f"(YoY={yoy:.1f}%, 3m trend YoY={trend:.1f}%). "
            f"{total_row.iloc[0]['source_note']}"
        ),
    }


def _cycle_stage_from_score(score: float) -> str:
    """Map a composite softness score to the four-band cycle-stage label.

    Mirrors the thresholds used in ``src/panels/property_cycle_core`` so the
    aggregated contract rows carry a cycle_stage consistent with the panel.
    """
    if pd.isna(score):
        return "neutral"
    if score < 2.0:
        return "growth"
    if score < 2.8:
        return "neutral"
    if score < 3.5:
        return "slowing"
    return "downturn"


def _softness_band_from_stage(stage: str) -> str:
    return {
        "downturn": "soft",
        "slowing": "softening",
        "neutral": "normal",
        "growth": "supportive",
    }.get(stage, "normal")


def _region_band_from_score(score: float) -> str:
    if pd.isna(score):
        return "Medium"
    if score < 2.0:
        return "Low"
    if score < 3.0:
        return "Medium"
    if score < 3.8:
        return "Elevated"
    return "High"


def _exposure_weights_by_building_type(approvals_frame: pd.DataFrame | None) -> dict[str, float]:
    """Return a dict of building_type → 12-month-mean approval value.

    When the raw approvals frame isn't available (tests, panel-only runs),
    returns an empty dict so callers fall back to a simple mean.
    """
    if approvals_frame is None or approvals_frame.empty:
        return {}
    if "value" not in approvals_frame.columns or "date" not in approvals_frame.columns:
        return {}

    frame = approvals_frame.dropna(subset=["date", "value"]).copy()
    if frame.empty:
        return {}

    latest_date = frame["date"].max()
    cutoff = latest_date - pd.DateOffset(years=1)
    window = frame[frame["date"] > cutoff]
    if window.empty:
        window = frame

    grouped = window.groupby("property_segment")["value"].mean()
    return {segment: float(value) for segment, value in grouped.items() if pd.notna(value)}


def _weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    """Exposure-weighted mean; falls back to simple mean when weights sum to zero."""
    if values.empty:
        return float("nan")
    weight_total = float(weights.sum())
    if weight_total <= 0:
        return float(values.mean())
    return float((values * weights).sum() / weight_total)


def _build_per_building_type(
    panel: pd.DataFrame,
    as_of_iso: str,
) -> pd.DataFrame:
    """Produce the explainability table — one row per ABS building type.

    Every row the panel emits is kept (including the three aggregate labels).
    The ``property_segment_code`` column is populated for the specific types
    and set to ``"CON"`` on the three aggregate rows so reviewers can see
    that those aggregates contribute to the CON construction-pipeline signal.
    """
    detail = panel[
        [
            "property_segment",
            "cycle_stage",
            "market_softness_score",
            "region_risk_score",
            "region_risk_band",
            "approvals_change_pct",
            "commencements_signal",
            "completions_signal",
        ]
    ].copy()
    detail["market_softness_band"] = detail["cycle_stage"].map(
        {
            "downturn": "soft",
            "slowing": "softening",
            "neutral": "normal",
            "growth": "supportive",
        }
    ).fillna("normal")

    def code_or_reference(segment: str) -> str:
        if segment in PROPERTY_SEGMENT_CODE_MAP:
            return PROPERTY_SEGMENT_CODE_MAP[segment]
        if segment in AGGREGATE_BUILDING_TYPES:
            return "CON"
        return ""

    detail["property_segment_code"] = detail["property_segment"].map(code_or_reference)
    detail["aggregate_role"] = detail["property_segment"].map(
        lambda s: "aggregate (reviewer reference only)" if s in AGGREGATE_BUILDING_TYPES else "specific"
    )
    detail["pd_multiplier_if_standalone"] = detail["market_softness_score"].apply(score_to_pd_multiplier)
    detail["as_of_date"] = as_of_iso

    column_order = [
        "property_segment",
        "property_segment_code",
        "aggregate_role",
        "cycle_stage",
        "market_softness_score",
        "market_softness_band",
        "region_risk_score",
        "region_risk_band",
        "approvals_change_pct",
        "commencements_signal",
        "completions_signal",
        "pd_multiplier_if_standalone",
        "as_of_date",
    ]
    return detail[column_order].reset_index(drop=True)


def _aggregate_group(
    detail: pd.DataFrame,
    weights: dict[str, float],
    *,
    segments: list[str],
) -> tuple[float, float, float]:
    """Return (softness, region_risk, approvals_change) for a code group."""
    subset = detail[detail["property_segment"].isin(segments)].copy()
    if subset.empty:
        return float("nan"), float("nan"), float("nan")
    subset["_weight"] = subset["property_segment"].map(weights).fillna(1.0)
    softness = _weighted_mean(subset["market_softness_score"], subset["_weight"])
    region_risk = _weighted_mean(subset["region_risk_score"], subset["_weight"])
    approvals = _weighted_mean(subset["approvals_change_pct"].astype(float), subset["_weight"])
    return softness, region_risk, approvals


def _contract_row(
    code: str,
    softness: float,
    region_risk: float,
    approvals_change: float,
    commencements_signal: str,
    completions_signal: str,
    source_note: str,
    as_of_iso: str,
) -> dict[str, object]:
    stage = _cycle_stage_from_score(softness)
    return {
        "property_segment": PROPERTY_SEGMENT_DISPLAY_NAMES[code],
        "property_segment_code": code,
        "cycle_stage": stage,
        "market_softness_score": round(softness, 2) if not pd.isna(softness) else np.nan,
        "market_softness_band": _softness_band_from_stage(stage),
        "market_softness_level": score_to_risk_level(softness) if not pd.isna(softness) else "Medium",
        "region_risk_score": round(region_risk, 2) if not pd.isna(region_risk) else np.nan,
        "region_risk_band": _region_band_from_score(region_risk),
        "approvals_change_pct": round(approvals_change, 2) if not pd.isna(approvals_change) else np.nan,
        "commencements_signal": commencements_signal,
        "completions_signal": completions_signal,
        "pd_multiplier": score_to_pd_multiplier(softness if not pd.isna(softness) else 2.50),
        "source_note": source_note,
        "as_of_date": as_of_iso,
    }


CONTRACT_COLUMN_ORDER: tuple[str, ...] = (
    "property_segment_code",
    "property_segment",
    "cycle_stage",
    "market_softness_score",
    "market_softness_band",
    "market_softness_level",
    "region_risk_score",
    "region_risk_band",
    "approvals_change_pct",
    "commencements_signal",
    "completions_signal",
    "pd_multiplier",
    "source_note",
    "as_of_date",
)


def build_property_market_overlays_by_building_type(
    panel: pd.DataFrame | None = None,
    as_of: date | None = None,
) -> pd.DataFrame:
    """Return the explainability table — one row per ABS building type."""
    if panel is None:
        from src.panels.build_property_cycle_panel import build_property_cycle_panel

        panel = build_property_cycle_panel()
    as_of_iso = (as_of or date.today()).isoformat()
    return _build_per_building_type(panel, as_of_iso)


def build_property_market_overlays(
    panel: pd.DataFrame | None = None,
    as_of: date | None = None,
    approvals_frame: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Return the contract table — exactly five rows, one per segment code.

    Callers may pass ``approvals_frame`` (the raw per-month approvals frame
    from ``load_building_approvals_reference``) to enable exposure-weighted
    aggregation. When absent, the builder falls back to simple-mean
    aggregation and this is documented in the row's ``source_note``.
    """
    if panel is None:
        from src.panels.build_property_cycle_panel import build_property_cycle_panel

        panel = build_property_cycle_panel()

    as_of_iso = (as_of or date.today()).isoformat()

    if approvals_frame is None:
        try:
            from src.public_data.load_abs_manual_exports_helpers import (
                load_building_approvals_reference,
            )

            approvals_frame = load_building_approvals_reference()
        except Exception:  # noqa: BLE001 — broad by design; explainability loader is optional.
            approvals_frame = None

    weights = _exposure_weights_by_building_type(approvals_frame)
    weighting_note = (
        "Exposure-weighted (12-month mean approval $ per building type)."
        if weights
        else "Simple-mean aggregation (raw approval values unavailable)."
    )

    detail = panel[
        [
            "property_segment",
            "cycle_stage",
            "market_softness_score",
            "region_risk_score",
            "region_risk_band",
            "approvals_change_pct",
            "commencements_signal",
            "completions_signal",
        ]
    ].copy()

    # The CON (construction pipeline) aggregate uses every specific
    # non-residential category we have a code mapping for. Excluding the
    # three aggregate rows (Total Non-residential, Commercial Total,
    # Industrial Total) avoids double-counting.
    cre_segments = [s for s, c in PROPERTY_SEGMENT_CODE_MAP.items() if c == "CRE"]
    ind_segments = [s for s, c in PROPERTY_SEGMENT_CODE_MAP.items() if c == "IND"]
    ret_segments = [s for s, c in PROPERTY_SEGMENT_CODE_MAP.items() if c == "RET"]
    con_segments = list(PROPERTY_SEGMENT_CODE_MAP.keys())

    base_source = (
        "Aggregated from ABS Cat. 8731.0 non-residential building approvals. "
        + weighting_note
    )

    rows: list[dict[str, object]] = []

    # RES — residential row. Pulls real signal from ABS Cat. 8752.0 dwelling
    # approvals when staged; otherwise falls back to the documented placeholder
    # composite so the PD workbook's bridging product still has a non-null lookup.
    res_signal = _residential_signal_from_approvals()
    if res_signal is not None:
        rows.append(
            _contract_row(
                "RES",
                res_signal["softness"],
                detail["region_risk_score"].mean() if not detail.empty else 2.5,
                res_signal["approvals_change_pct"],
                "Residential approvals (Cat. 8752.0)",
                "Residential approvals (Cat. 8752.0)",
                res_signal["source_note"],
                as_of_iso,
            )
        )
    else:
        rows.append(
            _contract_row(
                "RES",
                _RESIDENTIAL_NEUTRAL_SCORE,
                detail["region_risk_score"].mean() if not detail.empty else 2.5,
                float("nan"),
                "Residential placeholder (no signal)",
                "Residential placeholder (no signal)",
                _RESIDENTIAL_PLACEHOLDER_SOURCE_NOTE,
                as_of_iso,
            )
        )

    for code, segments in [
        ("CRE", cre_segments),
        ("IND", ind_segments),
        ("RET", ret_segments),
        ("CON", con_segments),
    ]:
        softness, region_risk, approvals_change = _aggregate_group(detail, weights, segments=segments)
        present = sorted(set(segments).intersection(detail["property_segment"]))
        source_note = (
            f"{base_source} Constituent ABS categories: "
            + (", ".join(present) if present else "<none matched in panel>")
        )
        rows.append(
            _contract_row(
                code,
                softness,
                region_risk,
                approvals_change,
                "Proxy from approvals trend",
                "Proxy from approvals trend",
                source_note,
                as_of_iso,
            )
        )

    contract = pd.DataFrame(rows)
    contract = contract[list(CONTRACT_COLUMN_ORDER)]
    # Preserve the {RES, CRE, IND, RET, CON} ordering.
    contract["_sort"] = contract["property_segment_code"].map(
        {code: index for index, code in enumerate(VALID_PROPERTY_SEGMENT_CODES)}
    )
    contract = contract.sort_values("_sort").drop(columns=["_sort"]).reset_index(drop=True)
    contract = _enrich_with_property_reference(contract)
    return contract


def _enrich_with_property_reference(contract: pd.DataFrame) -> pd.DataFrame:
    """Append property-reference-derived columns to the 5-row contract.

    For RES: aggregate across the 8 capital cities (combined property type).
    For CRE/IND/RET/CON: the property-reference panel covers residential only,
    so these rows carry nulls in the new columns and a status flag.
    """
    from src.panels.build_property_reference_panel import build_property_reference_panel

    try:
        ref_panel = build_property_reference_panel()
    except Exception as exc:  # noqa: BLE001 — degrade gracefully on any failure
        ref_panel = pd.DataFrame()

    contract = contract.copy()
    for col in PROPERTY_REFERENCE_DERIVED_COLUMNS:
        contract[col] = float("nan") if col not in {
            "property_reference_status",
            "contributing_sources",
            "as_of_property_reference_date",
        } else None

    if ref_panel.empty:
        contract["property_reference_status"] = "not_available"
        contract["contributing_sources"] = "<none>"
        contract["as_of_property_reference_date"] = ""
        return contract

    capitals = ref_panel[ref_panel["region_type"] == "capital"].copy()
    suburbs = ref_panel[ref_panel["region_type"].isin({"suburb", "sa3", "sa4", "postcode"})]

    # Use the latest as_of_date in the panel as the reference vintage.
    if capitals.empty:
        latest_iso = ref_panel["as_of_date"].max()
    else:
        latest_iso = capitals["as_of_date"].max()
    capitals_latest = capitals[capitals["as_of_date"] == latest_iso]

    res_metrics = {
        "median_dwelling_price_aud": float(capitals_latest["cotality_median_value_aud"].mean(skipna=True)),
        "annual_price_change_pct": float(capitals_latest["cotality_annual_change_pct"].mean(skipna=True)),
        "peak_to_trough_decline_pct": float(capitals_latest["cotality_peak_to_trough_decline_pct"].mean(skipna=True)),
        "auction_clearance_rate_pct": float(capitals_latest["cotality_auction_clearance_quarter_avg_pct"].mean(skipna=True)),
        "median_days_on_market": float(capitals_latest["domain_median_dom"].mean(skipna=True)),
        "median_vendor_discount_pct": float(capitals_latest["domain_vendor_discount_pct"].mean(skipna=True)),
        "vacancy_rate_pct": float(capitals_latest["sqm_vacancy_rate_pct"].mean(skipna=True)),
        "median_weekly_rent_aud": float(suburbs["rental_bond_median_weekly_rent_aud"].mean(skipna=True)) if not suburbs.empty else float("nan"),
        "rental_yield_gross_pct": float(capitals_latest["domain_rental_yield_gross_pct"].mean(skipna=True)),
    }
    contributing = sorted(
        {
            piece.strip()
            for entry in capitals_latest["contributing_sources"].dropna()
            for piece in str(entry).split(";")
            if piece.strip() and piece.strip() != "<none>"
        }
    )
    if not suburbs.empty:
        contributing.append("State rental bonds")

    has_any = any(pd.notna(v) for v in res_metrics.values())
    status = "available" if has_any else "not_available"
    if status == "available":
        # Per Task 12, the property-reference panel covers residential only;
        # commercial segments carry nulls + an explicit flag.
        for col, val in res_metrics.items():
            contract.loc[contract["property_segment_code"] == "RES", col] = (
                round(val, 2) if pd.notna(val) else float("nan")
            )
        contract.loc[contract["property_segment_code"] == "RES", "property_reference_status"] = "available"
        contract.loc[contract["property_segment_code"] == "RES", "contributing_sources"] = "; ".join(contributing) or "<none>"
        contract.loc[contract["property_segment_code"] == "RES", "as_of_property_reference_date"] = latest_iso

        contract.loc[contract["property_segment_code"] != "RES", "property_reference_status"] = (
            "residential_only_in_v1"
        )
        contract.loc[contract["property_segment_code"] != "RES", "contributing_sources"] = "<commercial coverage out of scope>"
        contract.loc[contract["property_segment_code"] != "RES", "as_of_property_reference_date"] = latest_iso
    else:
        contract["property_reference_status"] = "not_available"
        contract["contributing_sources"] = "<none>"
        contract["as_of_property_reference_date"] = ""

    return contract
