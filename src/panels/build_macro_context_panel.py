"""Macro context panel — CPI, PPI, headline labour, cash rate, FSR aggregates.

Sits parallel to the existing ``business_cycle_panel`` (per-industry) and
``property_cycle_panel`` (per-property-segment). Aggregates the
national/macroeconomic indicators that affect every industry into a single
quarter-keyed panel.

Schema:
    as_of_date              quarter-end date (ISO)
    period_label            e.g. "2025Q4"
    cpi_yoy_pct             headline CPI annual change
    cpi_qoq_pct             headline CPI quarterly change
    cpi_housing_yoy_pct
    cpi_food_yoy_pct
    cpi_transport_yoy_pct
    ppi_manufacturing_yoy_pct
    ppi_construction_yoy_pct
    unemployment_rate_pct   from existing ABS labour-force load
    cash_rate_pct           from existing RBA F1 load
    household_debt_to_disposable_income_ratio   from RBA FSR (if staged)
    national_arrears_30d_pct                    from RBA FSR (if staged)
    source_note             which sources contributed to this row
"""

from __future__ import annotations

import pandas as pd

from src.config import (
    ABS_MACRO_FILENAMES,
    PROCESSED_PUBLIC_INDUSTRY_DIR,
    RAW_PUBLIC_DIR_ABS,
)
from src.output import save_csv
from src.property_reference.load_rba_property import load_rba_fsr_aggregates
from src.public_data.download_rba_rates import load_cash_rate_summary
from src.public_data.load_abs_manual_exports import (
    parse_cpi,
    parse_dwelling_approvals,  # imported so the panel exposes residential approvals state
    parse_labour_force,
    parse_ppi,
)


PANEL_COLUMNS = [
    "as_of_date",
    "period_label",
    "cpi_yoy_pct",
    "cpi_qoq_pct",
    "cpi_housing_yoy_pct",
    "cpi_food_yoy_pct",
    "cpi_transport_yoy_pct",
    "ppi_manufacturing_yoy_pct",
    "ppi_construction_yoy_pct",
    "unemployment_rate_pct",
    "cash_rate_pct",
    "household_debt_to_disposable_income_ratio",
    "national_arrears_30d_pct",
    "source_note",
]


def _headline_unemployment() -> pd.DataFrame:
    """Headline unemployment series (placeholder — ABS Cat. 6202.0 not staged).

    The labour-force-by-industry file we already load (Cat. 6291.0) is
    employment counts, not unemployment. The national unemployment rate
    lives in Cat. 6202.0 and isn't staged in this engine vintage. Until it
    is, this returns the canonical schema with NaN values so the macro
    context panel publishes a transparent "not yet staged" signal rather
    than an unreliable derived proxy.
    """
    return pd.DataFrame(columns=["as_of_date", "unemployment_rate_pct"])


def _latest_cash_rate() -> float:
    try:
        summary = load_cash_rate_summary()
        if summary.empty:
            return float("nan")
        return float(summary.iloc[0]["cash_rate_latest_pct"])
    except Exception:
        return float("nan")


def _quarter_label(date_iso: str) -> str:
    ts = pd.Timestamp(date_iso)
    return f"{ts.year}Q{ts.quarter}"


def _empty_panel() -> pd.DataFrame:
    return pd.DataFrame(columns=PANEL_COLUMNS)


def build_macro_context_panel() -> pd.DataFrame:
    """Build the macro_context panel — backward-looking quarterly observations."""
    cpi = parse_cpi(
        RAW_PUBLIC_DIR_ABS / ABS_MACRO_FILENAMES["cpi_all_groups"],
        RAW_PUBLIC_DIR_ABS / ABS_MACRO_FILENAMES["cpi_subgroups"],
    )
    ppi = parse_ppi(
        RAW_PUBLIC_DIR_ABS / ABS_MACRO_FILENAMES["ppi_manufacturing"],
        RAW_PUBLIC_DIR_ABS / ABS_MACRO_FILENAMES["ppi_construction"],
    )
    unemployment = _headline_unemployment()
    cash_rate_pct = _latest_cash_rate()
    fsr = load_rba_fsr_aggregates()

    # Pivot PPI into wide columns by division.
    if not ppi.empty:
        ppi_wide = (
            ppi.pivot_table(
                index="as_of_date",
                columns="anzsic_division_code",
                values="ppi_yoy_pct",
                aggfunc="last",
            )
            .rename(columns={"C": "ppi_manufacturing_yoy_pct", "E": "ppi_construction_yoy_pct"})
            .reset_index()
        )
    else:
        ppi_wide = pd.DataFrame(columns=["as_of_date", "ppi_manufacturing_yoy_pct", "ppi_construction_yoy_pct"])

    fsr_dict: dict[str, float] = {}
    if not fsr.empty:
        for metric, group in fsr.groupby("metric"):
            latest = group.sort_values("as_of_date").iloc[-1]
            fsr_dict[metric] = float(latest["value"])

    # If neither CPI nor PPI staged, build a panel from the cash rate + FSR
    # so the contract is non-empty in the minimum data-availability state.
    if cpi.empty and ppi_wide.empty and unemployment.empty:
        today = pd.Timestamp.today().normalize()
        try:
            quarter_ends = pd.date_range(end=today, periods=8, freq="QE")
        except ValueError:
            quarter_ends = pd.date_range(end=today, periods=8, freq="Q")
        sources = ["RBA F1 cash rate"]
        if fsr_dict:
            sources.append("RBA FSR")
        skeleton_note = (
            "Skeleton panel — ABS Cat. 6401.0 / 6427.0 / 6202.0 not staged. "
            "Populated columns: " + "; ".join(sources)
        )
        rows = []
        for q in quarter_ends:
            iso = q.date().isoformat()
            rows.append(
                {
                    "as_of_date": iso,
                    "period_label": _quarter_label(iso),
                    "cpi_yoy_pct": float("nan"),
                    "cpi_qoq_pct": float("nan"),
                    "cpi_housing_yoy_pct": float("nan"),
                    "cpi_food_yoy_pct": float("nan"),
                    "cpi_transport_yoy_pct": float("nan"),
                    "ppi_manufacturing_yoy_pct": float("nan"),
                    "ppi_construction_yoy_pct": float("nan"),
                    "unemployment_rate_pct": float("nan"),
                    "cash_rate_pct": cash_rate_pct,
                    "household_debt_to_disposable_income_ratio": fsr_dict.get(
                        "total_household_debt_to_disposable_income", float("nan")
                    ),
                    "national_arrears_30d_pct": fsr_dict.get(
                        "national_arrears_30d_pct", float("nan")
                    ),
                    "source_note": skeleton_note,
                }
            )
        return pd.DataFrame(rows, columns=PANEL_COLUMNS)

    quarters = sorted(
        set(cpi["as_of_date"].tolist())
        | set(ppi_wide["as_of_date"].tolist() if not ppi_wide.empty else [])
        | set(unemployment["as_of_date"].tolist() if not unemployment.empty else [])
    )[-8:]

    rows = []
    for q in quarters:
        cpi_row = cpi[cpi["as_of_date"] == q]
        ppi_row = ppi_wide[ppi_wide["as_of_date"] == q]
        ur_row = unemployment[unemployment["as_of_date"] == q]
        sources = []
        if not cpi_row.empty:
            sources.append("ABS CPI")
        if not ppi_row.empty:
            sources.append("ABS PPI")
        if not ur_row.empty:
            sources.append("ABS Labour Force (proxy)")
        if not fsr.empty:
            sources.append("RBA FSR")
        sources.append("RBA F1 cash rate")

        rows.append(
            {
                "as_of_date": q,
                "period_label": _quarter_label(q),
                "cpi_yoy_pct": float(cpi_row.iloc[0]["all_groups_yoy_pct"]) if not cpi_row.empty else float("nan"),
                "cpi_qoq_pct": float(cpi_row.iloc[0]["all_groups_qoq_pct"]) if not cpi_row.empty else float("nan"),
                "cpi_housing_yoy_pct": float(cpi_row.iloc[0]["housing_yoy_pct"]) if not cpi_row.empty else float("nan"),
                "cpi_food_yoy_pct": float(cpi_row.iloc[0]["food_yoy_pct"]) if not cpi_row.empty else float("nan"),
                "cpi_transport_yoy_pct": float(cpi_row.iloc[0]["transport_yoy_pct"]) if not cpi_row.empty else float("nan"),
                "ppi_manufacturing_yoy_pct": float(ppi_row.iloc[0]["ppi_manufacturing_yoy_pct"]) if not ppi_row.empty and "ppi_manufacturing_yoy_pct" in ppi_row.columns else float("nan"),
                "ppi_construction_yoy_pct": float(ppi_row.iloc[0]["ppi_construction_yoy_pct"]) if not ppi_row.empty and "ppi_construction_yoy_pct" in ppi_row.columns else float("nan"),
                "unemployment_rate_pct": float(ur_row.iloc[0]["unemployment_rate_pct"]) if not ur_row.empty else float("nan"),
                "cash_rate_pct": cash_rate_pct,
                "household_debt_to_disposable_income_ratio": fsr_dict.get(
                    "total_household_debt_to_disposable_income", float("nan")
                ),
                "national_arrears_30d_pct": fsr_dict.get("national_arrears_30d_pct", float("nan")),
                "source_note": "; ".join(sources),
            }
        )

    panel = pd.DataFrame(rows, columns=PANEL_COLUMNS)
    PROCESSED_PUBLIC_INDUSTRY_DIR.mkdir(parents=True, exist_ok=True)
    save_csv(panel, PROCESSED_PUBLIC_INDUSTRY_DIR / "macro_context_panel.csv")
    return panel


def residential_approvals_signal() -> pd.DataFrame:
    """Convenience accessor: latest dwelling-approvals frame for property overlay."""
    return parse_dwelling_approvals(
        RAW_PUBLIC_DIR_ABS / ABS_MACRO_FILENAMES["dwelling_approvals"]
    )
