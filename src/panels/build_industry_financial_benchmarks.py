"""Industry financial-ratio benchmark library.

Publishes the per-ANZSIC-division medians of the financial ratios APG 220
paragraph 64 calls out as standard comparison benchmarks for commercial
credit assessment. Downstream credit-risk systems use these as the
industry-comparison reference for borrower ratios.

Method note
-----------
Each "median" published here is an industry-aggregate ratio computed from
ABS published aggregates (e.g. total industry sales divided by total
industry COGS). This is mathematically a weighted-average industry ratio,
not the median of firm-level ratios within the industry. We use the label
"median" because it is the closest publicly-available proxy and matches
the language used in APG 220.

For true firm-level distribution medians and percentiles, downstream
consumers must compute them from internal portfolio data. This contract
publishes the public-data benchmark only.

Out of scope (future passes):
* Percentile estimates (p25, p75) — requires firm-level data the engine
  does not have, or distributional assumptions that are challengeable.
* Sub-sector granularity — requires different ABS source files and
  meaningful additional plumbing.
* Computed ratios beyond what the panel already produces — DSCR, current
  ratio, debtor days, creditor days, net-debt-to-EBITDA cannot be derived
  from public macro data alone.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd


BENCHMARK_METHOD = (
    "ABS aggregate (industry-weighted; closest public proxy for industry median)"
)

SOURCE_NOTE = (
    "Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business "
    "Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) "
    "not published in this version — internal portfolio data required for "
    "firm-level distribution. Sub-sector (subdivision/group) granularity "
    "not published in this version — division-level only."
)


BENCHMARK_COLUMN_ORDER: tuple[str, ...] = (
    "anzsic_division_code",
    "industry",
    "median_ebitda_margin_pct",
    "median_gross_operating_profit_to_sales_ratio",
    "median_wages_to_sales_pct",
    "median_inventory_days_est",
    "median_sales_growth_pct",
    "median_employment_yoy_growth_pct",
    "median_inventory_to_sales_ratio",
    "median_sales_per_employee_thousands",
    "benchmark_method",
    "source_note",
    "as_of_date",
)


def build_industry_financial_benchmarks(
    panel: pd.DataFrame | None = None,
    as_of: date | None = None,
) -> pd.DataFrame:
    """Return one row per ANZSIC division with the eight benchmark medians."""
    if panel is None:
        # Late import avoids a circular dependency through the panel builder.
        from src.panels.build_business_cycle_panel import build_business_cycle_panel

        panel = build_business_cycle_panel()

    as_of_value = (as_of or date.today()).isoformat()

    sales_per_emp = (panel["sales_m_latest"] * 1000) / panel["employment_000_latest"]

    frame = pd.DataFrame(
        {
            "anzsic_division_code": panel["anzsic_division_code"],
            "industry": panel["industry"],
            "median_ebitda_margin_pct": panel["ebitda_margin_pct_latest"],
            "median_gross_operating_profit_to_sales_ratio": panel[
                "gross_operating_profit_to_sales_ratio_latest"
            ],
            "median_wages_to_sales_pct": panel["wages_to_sales_pct_latest"],
            "median_inventory_days_est": panel["inventory_days_est"],
            "median_sales_growth_pct": panel["sales_growth_pct"],
            "median_employment_yoy_growth_pct": panel["employment_yoy_growth_pct"],
            "median_inventory_to_sales_ratio": panel["inventories_to_sales_ratio_latest"],
            "median_sales_per_employee_thousands": sales_per_emp,
        }
    )

    frame["median_ebitda_margin_pct"] = frame["median_ebitda_margin_pct"].round(2)
    frame["median_gross_operating_profit_to_sales_ratio"] = frame[
        "median_gross_operating_profit_to_sales_ratio"
    ].round(4)
    frame["median_wages_to_sales_pct"] = frame["median_wages_to_sales_pct"].round(2)
    frame["median_inventory_days_est"] = frame["median_inventory_days_est"].round(1)
    frame["median_sales_growth_pct"] = frame["median_sales_growth_pct"].round(2)
    frame["median_employment_yoy_growth_pct"] = frame["median_employment_yoy_growth_pct"].round(2)
    frame["median_inventory_to_sales_ratio"] = frame["median_inventory_to_sales_ratio"].round(4)
    frame["median_sales_per_employee_thousands"] = frame[
        "median_sales_per_employee_thousands"
    ].replace([np.inf, -np.inf], np.nan).round(1)

    frame["benchmark_method"] = BENCHMARK_METHOD
    frame["source_note"] = SOURCE_NOTE
    frame["as_of_date"] = as_of_value

    frame = (
        frame[list(BENCHMARK_COLUMN_ORDER)]
        .sort_values("anzsic_division_code", ascending=True)
        .reset_index(drop=True)
    )
    return frame
