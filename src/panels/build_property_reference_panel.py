"""Property reference panel — multi-source free aggregation.

Aggregates 10 free public sources into a single panel keyed by
``(region_id, property_type, as_of_date)``. Each source contributes the
columns where it has data; absent sources produce nulls. The panel is
published as ``property_market_detail.parquet`` (Task 13) and consumed
by ``build_property_market_overlays`` to enrich the 5-row contract.

Region granularity:
    - National + 8 capital city + combined regional: covered by ABS, Cotality, Domain, SQM, Lending
    - Suburb: covered by Domain (top suburbs) and state rental bond data
"""

from __future__ import annotations

import pandas as pd

from src.config import PROCESSED_PUBLIC_PROPERTY_REFERENCE_DIR
from src.output import save_csv
from src.property_reference import (
    load_abs_lending_indicators,
    load_abs_property_price_index,
    load_abs_total_value_dwellings,
    load_cotality_auction_clearance,
    load_cotality_hvi,
    load_domain_quarterly,
    load_sqm_headline,
)
from src.property_reference.load_state_rental_bonds import (
    CANONICAL_RENTAL_BOND_COLUMNS,
    STATE_RENTAL_BOND_LOADERS,
)


PANEL_COLUMNS = [
    "as_of_date",
    "region_id",
    "region_name",
    "region_type",
    "state",
    "property_type",
    # ABS-derived (capital city, quarterly)
    "abs_price_index_value",
    "abs_price_index_yoy_pct",
    "abs_price_index_qoq_pct",
    # Cotality-derived (capital city, monthly)
    "cotality_median_value_aud",
    "cotality_quarterly_change_pct",
    "cotality_annual_change_pct",
    "cotality_peak_to_trough_decline_pct",
    "cotality_auction_clearance_quarter_avg_pct",
    # Domain-derived (capital + selected suburbs)
    "domain_median_price_aud",
    "domain_quarterly_change_pct",
    "domain_annual_change_pct",
    "domain_median_dom",
    "domain_vendor_discount_pct",
    "domain_rental_yield_gross_pct",
    # SQM-derived (capital, weekly aggregated to quarterly)
    "sqm_vacancy_rate_pct",
    "sqm_vendor_discount_pct",
    "sqm_stock_on_market",
    # State rental bonds (suburb level where available)
    "rental_bond_median_weekly_rent_aud",
    "rental_bond_sample_size_n",
    # ABS lending indicators (state level)
    "abs_new_housing_finance_aud_millions",
    "abs_new_finance_yoy_pct",
    # ABS total value of dwellings (state level)
    "total_value_dwellings_aud_millions",
    # Data quality
    "data_completeness_pct",
    "contributing_sources",
    "source_note",
]

# Capital city → state lookup, plus the regional-fallback rows.
_CAPITAL_TO_STATE = {
    "Sydney": "NSW",
    "Melbourne": "VIC",
    "Brisbane": "QLD",
    "Adelaide": "SA",
    "Perth": "WA",
    "Hobart": "TAS",
    "Darwin": "NT",
    "Canberra": "ACT",
}


def _normalise_region(name: str) -> str:
    return str(name).strip().title() if pd.notna(name) else ""


def _make_id(region_name: str, property_type: str, as_of_date: str) -> str:
    return f"{region_name}|{property_type}|{as_of_date}".lower().replace(" ", "_")


def _build_capital_city_rows(
    cotality: pd.DataFrame,
    cotality_auction: pd.DataFrame,
    abs_index: pd.DataFrame,
    domain: pd.DataFrame,
    sqm: pd.DataFrame,
    abs_lending: pd.DataFrame,
    abs_total_value: pd.DataFrame,
) -> pd.DataFrame:
    """Build one row per (capital city, property_type, as_of_date)."""
    rows: list[dict] = []

    # Source coverage seed: union of (region, property_type, as_of_date) from
    # capital-level sources.
    seeds = set()
    for src, region_col, type_col in [
        (cotality, "region", "property_type"),
        (domain[domain["region_type"] == "capital"] if not domain.empty else domain, "region", "property_type"),
    ]:
        if src is None or src.empty:
            continue
        for _, r in src.iterrows():
            region_name = _normalise_region(r[region_col])
            if region_name in {"Combined_Capitals", "Combined_Regional", "National"}:
                continue
            seeds.add((region_name, str(r[type_col]).lower(), str(r["as_of_date"])))

    if not seeds and not abs_index.empty:
        for _, r in abs_index.iterrows():
            seeds.add((_normalise_region(r["region"]), "combined", str(r["as_of_date"])))

    if not seeds:
        # No capital-level data anywhere — return an empty frame with the
        # correct columns. Caller still appends suburb rows from rental bonds.
        return pd.DataFrame(columns=PANEL_COLUMNS)

    auction_lookup = (
        cotality_auction.set_index(["region", "as_of_date"])
        if not cotality_auction.empty
        else pd.DataFrame()
    )
    sqm_lookup = (
        sqm.assign(region=lambda df: df["region"].astype(str).str.title())
           .set_index(["region", "as_of_date"])
        if not sqm.empty
        else pd.DataFrame()
    )

    for region_name, property_type, as_of in sorted(seeds):
        state = _CAPITAL_TO_STATE.get(region_name, "")
        cot = cotality[
            (cotality["region"].astype(str).str.title() == region_name)
            & (cotality["property_type"].astype(str).str.lower() == property_type)
            & (cotality["as_of_date"].astype(str) == as_of)
        ]
        cot_combined = cotality[
            (cotality["region"].astype(str).str.title() == region_name)
            & (cotality["property_type"].astype(str).str.lower() == "combined")
            & (cotality["as_of_date"].astype(str) == as_of)
        ]
        cot_use = cot if not cot.empty else cot_combined

        dom = domain[
            (domain["region"].astype(str).str.title() == region_name)
            & (domain["property_type"].astype(str).str.lower() == property_type)
            & (domain["as_of_date"].astype(str) == as_of)
        ]
        # ABS Cat. 6416.0 region label for capital cities is "Sydney", etc.
        abs_row = abs_index[
            (abs_index["region"].astype(str).str.title() == region_name)
            & (abs_index["as_of_date"].astype(str) == as_of)
        ]

        contributing = []
        if not cot_use.empty:
            contributing.append("Cotality HVI")
        if not dom.empty:
            contributing.append("Domain Quarterly")
        if not abs_row.empty:
            contributing.append("ABS Cat. 6416.0")

        # Auction clearance keyed by region only (e.g. "sydney").
        auction_value = float("nan")
        if not auction_lookup.empty:
            try:
                auction_value = float(
                    auction_lookup.loc[(region_name.lower(), as_of), "quarter_avg_clearance_rate_pct"]
                )
                contributing.append("Cotality auction clearance")
            except KeyError:
                pass

        # SQM keyed by Title-case region.
        sqm_vacancy = sqm_vendor = sqm_stock = float("nan")
        if not sqm_lookup.empty:
            try:
                sqm_row = sqm_lookup.loc[(region_name, as_of)]
                sqm_vacancy = float(sqm_row["vacancy_rate_pct"])
                sqm_vendor = float(sqm_row["vendor_discount_pct"])
                sqm_stock = float(sqm_row["stock_on_market_count"])
                contributing.append("SQM headline")
            except KeyError:
                pass

        # Lending and total-value at state level, joined by state.
        lending_yoy = float("nan")
        lending_value = float("nan")
        if not abs_lending.empty and state:
            lending_match = abs_lending[abs_lending["state"].astype(str).str.upper().str.contains(state)]
            if not lending_match.empty:
                lending_value = float(lending_match.iloc[0]["abs_new_housing_finance_aud_millions"])
                lending_yoy = float(lending_match.iloc[0]["abs_new_finance_yoy_pct"])
                contributing.append("ABS Cat. 5601.0")

        total_value = float("nan")
        if not abs_total_value.empty and state:
            tv_match = abs_total_value[abs_total_value["state"].astype(str).str.upper().str.contains(state)]
            if not tv_match.empty:
                total_value = float(tv_match.iloc[0]["total_value_dwellings_aud_millions"])
                contributing.append("ABS Cat. 6432.0")

        row = {
            "as_of_date": as_of,
            "region_id": _make_id(region_name, property_type, as_of),
            "region_name": region_name,
            "region_type": "capital",
            "state": state,
            "property_type": property_type,
            "abs_price_index_value": float(abs_row.iloc[0]["abs_price_index_value"]) if not abs_row.empty else float("nan"),
            "abs_price_index_yoy_pct": float(abs_row.iloc[0]["abs_price_index_yoy_pct"]) if not abs_row.empty else float("nan"),
            "abs_price_index_qoq_pct": float(abs_row.iloc[0]["abs_price_index_qoq_pct"]) if not abs_row.empty else float("nan"),
            "cotality_median_value_aud": float(cot_use.iloc[0]["median_value_aud"]) if not cot_use.empty else float("nan"),
            "cotality_quarterly_change_pct": float(cot_use.iloc[0]["quarterly_pct_change"]) if not cot_use.empty else float("nan"),
            "cotality_annual_change_pct": float(cot_use.iloc[0]["annual_pct_change"]) if not cot_use.empty else float("nan"),
            "cotality_peak_to_trough_decline_pct": float(cot_use.iloc[0]["peak_to_trough_decline_pct"]) if not cot_use.empty else float("nan"),
            "cotality_auction_clearance_quarter_avg_pct": auction_value,
            "domain_median_price_aud": float(dom.iloc[0]["median_price_aud"]) if not dom.empty else float("nan"),
            "domain_quarterly_change_pct": float(dom.iloc[0]["quarterly_pct_change"]) if not dom.empty else float("nan"),
            "domain_annual_change_pct": float(dom.iloc[0]["annual_pct_change"]) if not dom.empty else float("nan"),
            "domain_median_dom": float(dom.iloc[0]["median_days_on_market"]) if not dom.empty else float("nan"),
            "domain_vendor_discount_pct": float(dom.iloc[0]["median_vendor_discount_pct"]) if not dom.empty else float("nan"),
            "domain_rental_yield_gross_pct": float(dom.iloc[0]["median_rental_yield_gross_pct"]) if not dom.empty else float("nan"),
            "sqm_vacancy_rate_pct": sqm_vacancy,
            "sqm_vendor_discount_pct": sqm_vendor,
            "sqm_stock_on_market": sqm_stock,
            "rental_bond_median_weekly_rent_aud": float("nan"),
            "rental_bond_sample_size_n": float("nan"),
            "abs_new_housing_finance_aud_millions": lending_value,
            "abs_new_finance_yoy_pct": lending_yoy,
            "total_value_dwellings_aud_millions": total_value,
            "data_completeness_pct": float("nan"),  # filled in _add_data_completeness
            "contributing_sources": "; ".join(contributing) if contributing else "<none>",
            "source_note": "Capital-city aggregation",
        }
        rows.append(row)

    return pd.DataFrame(rows, columns=PANEL_COLUMNS)


def _build_suburb_rows(
    domain: pd.DataFrame,
    rental_bonds: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict] = []

    if not domain.empty:
        suburb_domain = domain[domain["region_type"] == "suburb"]
        for _, r in suburb_domain.iterrows():
            region_name = _normalise_region(r["region"])
            property_type = str(r["property_type"]).lower()
            as_of = str(r["as_of_date"])
            row = {col: float("nan") for col in PANEL_COLUMNS}
            row.update(
                {
                    "as_of_date": as_of,
                    "region_id": _make_id(region_name, property_type, as_of),
                    "region_name": region_name,
                    "region_type": "suburb",
                    "state": str(r.get("state", "")),
                    "property_type": property_type,
                    "domain_median_price_aud": float(r["median_price_aud"]),
                    "domain_quarterly_change_pct": float(r["quarterly_pct_change"]),
                    "domain_annual_change_pct": float(r["annual_pct_change"]),
                    "domain_median_dom": float(r["median_days_on_market"]),
                    "domain_vendor_discount_pct": float(r["median_vendor_discount_pct"]),
                    "domain_rental_yield_gross_pct": float(r["median_rental_yield_gross_pct"]),
                    "contributing_sources": "Domain Quarterly (suburb)",
                    "source_note": "Domain top-suburb row",
                }
            )
            rows.append(row)

    if not rental_bonds.empty:
        for _, r in rental_bonds.iterrows():
            region_name = _normalise_region(r["region"])
            property_type = str(r["property_type"]).lower()
            as_of = str(r["as_of_date"])
            region_id = _make_id(region_name, property_type, as_of)
            existing = next((row for row in rows if row["region_id"] == region_id), None)
            if existing is not None:
                existing["rental_bond_median_weekly_rent_aud"] = float(r["median_weekly_rent_aud"])
                existing["rental_bond_sample_size_n"] = float(r["sample_size_n"])
                existing["contributing_sources"] = (
                    f"{existing['contributing_sources']}; State rental bond ({r['state']})"
                )
            else:
                row = {col: float("nan") for col in PANEL_COLUMNS}
                row.update(
                    {
                        "as_of_date": as_of,
                        "region_id": region_id,
                        "region_name": region_name,
                        "region_type": str(r["region_type"]) if r["region_type"] in {"suburb", "sa3", "sa4", "postcode"} else "suburb",
                        "state": str(r["state"]),
                        "property_type": property_type,
                        "rental_bond_median_weekly_rent_aud": float(r["median_weekly_rent_aud"]),
                        "rental_bond_sample_size_n": float(r["sample_size_n"]),
                        "contributing_sources": f"State rental bond ({r['state']})",
                        "source_note": str(r["source_note"]),
                    }
                )
                rows.append(row)

    if not rows:
        return pd.DataFrame(columns=PANEL_COLUMNS)
    return pd.DataFrame(rows, columns=PANEL_COLUMNS)


_SOURCE_VALUE_COLUMNS = [
    "abs_price_index_value",
    "cotality_median_value_aud",
    "cotality_auction_clearance_quarter_avg_pct",
    "domain_median_price_aud",
    "sqm_vacancy_rate_pct",
    "rental_bond_median_weekly_rent_aud",
    "abs_new_housing_finance_aud_millions",
    "total_value_dwellings_aud_millions",
]


def _add_data_completeness(panel: pd.DataFrame) -> pd.DataFrame:
    if panel.empty:
        return panel
    panel = panel.copy()
    populated = panel[_SOURCE_VALUE_COLUMNS].notna().sum(axis=1)
    panel["data_completeness_pct"] = (populated / len(_SOURCE_VALUE_COLUMNS) * 100).round(1)
    return panel


def _empty_panel() -> pd.DataFrame:
    return pd.DataFrame(columns=PANEL_COLUMNS)


def build_property_reference_panel() -> pd.DataFrame:
    """Aggregate all 10 free property-reference sources into a single panel.

    Always returns a non-empty frame when at least one source is staged
    (degraded with nulls otherwise). When *no* source is staged at all,
    returns an empty frame with the canonical schema — the caller decides
    whether to fail or proceed.
    """
    cotality = load_cotality_hvi()
    cotality_auction = load_cotality_auction_clearance()
    abs_index = load_abs_property_price_index()
    domain = load_domain_quarterly()
    sqm = load_sqm_headline()
    abs_lending = load_abs_lending_indicators()
    abs_total_value = load_abs_total_value_dwellings()

    rental_bond_frames = []
    for loader in STATE_RENTAL_BOND_LOADERS:
        df = loader()
        if not df.empty:
            rental_bond_frames.append(df)
    rental_bonds = (
        pd.concat(rental_bond_frames, ignore_index=True)
        if rental_bond_frames
        else pd.DataFrame(columns=CANONICAL_RENTAL_BOND_COLUMNS)
    )

    capital_rows = _build_capital_city_rows(
        cotality, cotality_auction, abs_index, domain, sqm, abs_lending, abs_total_value
    )
    suburb_rows = _build_suburb_rows(domain, rental_bonds)
    panel = pd.concat([capital_rows, suburb_rows], ignore_index=True)
    if panel.empty:
        return _empty_panel()
    panel = _add_data_completeness(panel)
    panel = panel.sort_values(["region_type", "state", "region_name", "property_type", "as_of_date"]).reset_index(drop=True)

    PROCESSED_PUBLIC_PROPERTY_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    save_csv(panel, PROCESSED_PUBLIC_PROPERTY_REFERENCE_DIR / "property_reference_panel.csv")
    return panel
