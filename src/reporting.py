"""Workbook-backed chart pack and formal PDF report generation."""

from __future__ import annotations

from pathlib import Path
import gc
from io import BytesIO
import time
import textwrap

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image

from src.config import REPO_ROOT
from src.credit import BASE_MARGIN_PCT, POLICY_RULES, PRICING_LOADING
from src.portfolio import CONCENTRATION_LIMITS
from src.output import save_csv
from src import visualisation as viz


REPORT_WORKBOOK_RELATIVE = "data/processed/industry_risk_reporting_workbook.xlsx"
REPORT_STYLE = {
    "header_bg": "#12324a",
    "header_text": "#ffffff",
    "page_bg": "#ffffff",
    "panel_bg": "#f7f9fb",
    "panel_border": "#d9e2ec",
    "text_primary": "#102a43",
    "text_secondary": "#486581",
    "muted": "#6b7c93",
}

PUBLIC_DATA_VINTAGES = [
    (
        "ABS Australian Industry",
        "FY 2022-23 and FY 2023-24 annual values from the 2023-24 release",
        "Annual; refresh after each new ABS Australian Industry release",
    ),
    (
        "ABS Business Indicators - Gross Operating Profit / Sales Ratio",
        "Quarterly series through December 2025",
        "Quarterly",
    ),
    (
        "ABS Business Indicators - Inventories / Sales Ratio",
        "Quarterly series through December 2025",
        "Quarterly",
    ),
    (
        "ABS Labour Force by Industry",
        "Monthly series through February 2026",
        "Monthly",
    ),
    (
        "ABS Building Approvals (Non-Residential)",
        "Monthly series through February 2026",
        "Monthly",
    ),
    (
        "RBA F1 cash-rate table",
        "Local CSV snapshot published 2 April 2026, with the latest staged observation dated 16 March 2026",
        "Refresh when a newer RBA snapshot is staged or the policy-rate series changes",
    ),
    (
        "PTRS",
        "Cycle 8 (July 2025) and Cycle 9 (January 2026) publications, plus March 2025 guidance",
        "Refresh when a new PTRS cycle publication is released",
    ),
]

SECTOR_CORE_SOURCE_PERIOD = (
    "Annual ABS FY 2022-23 to FY 2023-24; quarterly ABS series to Dec 2025; "
    "monthly ABS series to Feb 2026; RBA snapshot published 2 Apr 2026."
)
PTRS_SOURCE_PERIOD = "PTRS Cycle 8 (Jul 2025) and Cycle 9 (Jan 2026)."
INVENTORY_SOURCE_PERIOD = "ABS inventory ratio to Dec 2025 plus ABS annual FY 2023-24 margin data."
OVERLAY_SOURCE_PERIOD = "PTRS Jul 2025 and Jan 2026 plus ABS inventory ratio to Dec 2025."


CHART_DEFINITIONS = [
    {
        "chart_id": "C01",
        "chart_title": "Industry Risk Dimensions Heatmap",
        "chart_file": "industry_risk_heatmap.png",
        "source_sheet": "chart_data_heatmap",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/industry_base_risk_scorecard.csv",
        "metric_basis": "Public ABS/RBA metrics plus public-data-derived classification scores",
        "source_period": SECTOR_CORE_SOURCE_PERIOD,
    },
    {
        "chart_id": "C02",
        "chart_title": "Industry Base Risk Score by Sector",
        "chart_file": "industry_base_risk_score.png",
        "source_sheet": "chart_data_industry_s",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/industry_base_risk_scorecard.csv",
        "metric_basis": "Public ABS/RBA metrics plus public-data-derived classification scores",
        "source_period": SECTOR_CORE_SOURCE_PERIOD,
    },
    {
        "chart_id": "C03",
        "chart_title": "Employment Growth by Industry",
        "chart_file": "industry_employment_growth.png",
        "source_sheet": "chart_data_industry_s",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/industry_base_risk_scorecard.csv",
        "metric_basis": "Public ABS labour-force series",
        "source_period": "ABS Labour Force monthly series to Feb 2026.",
    },
    {
        "chart_id": "C04",
        "chart_title": "Borrower Industry Risk Scorecard",
        "chart_file": "borrower_industry_risk_scorecard.png",
        "source_sheet": "chart_data_borrower",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/borrower_industry_risk_scorecard.csv",
        "metric_basis": "Synthetic borrower archetype financials combined with public sector metrics",
        "source_period": f"{SECTOR_CORE_SOURCE_PERIOD} Synthetic borrower archetypes are model-generated.",
    },
    {
        "chart_id": "C05",
        "chart_title": "Indicative Pricing by Borrower",
        "chart_file": "pricing_grid.png",
        "source_sheet": "chart_data_pricing",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/pricing_grid.csv",
        "metric_basis": "Illustrative pricing assumptions combined with borrower score outputs",
        "source_period": f"{SECTOR_CORE_SOURCE_PERIOD} Pricing settings are illustrative rather than sourced.",
    },
    {
        "chart_id": "C06",
        "chart_title": "Sector Concentration: Current Exposure vs Limit",
        "chart_file": "concentration_dashboard.png",
        "source_sheet": "chart_data_concentrat",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/concentration_limits.csv",
        "metric_basis": "Portfolio exposure proxy plus illustrative concentration limit settings",
        "source_period": f"{SECTOR_CORE_SOURCE_PERIOD} Exposure and limit settings are illustrative.",
    },
    {
        "chart_id": "C07",
        "chart_title": "Industry Watchlist Trigger Count",
        "chart_file": "watchlist_summary.png",
        "source_sheet": "chart_data_watchlist",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/watchlist_triggers.csv",
        "metric_basis": "Public ABS/RBA signals converted into watchlist rules",
        "source_period": SECTOR_CORE_SOURCE_PERIOD,
    },
    {
        "chart_id": "C08",
        "chart_title": "Industry Stress Test Impact",
        "chart_file": "stress_test_impact.png",
        "source_sheet": "chart_data_stress",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/industry_stress_test_matrix.csv",
        "metric_basis": "Public ABS/RBA metrics with simplified APRA-informed stress assumptions",
        "source_period": SECTOR_CORE_SOURCE_PERIOD,
    },
    {
        "chart_id": "C09",
        "chart_title": "AR Days Benchmark and Stress by Industry",
        "chart_file": "working_capital_ar_days.png",
        "source_sheet": "chart_data_wc_ar",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/industry_working_capital_risk_metrics.csv",
        "metric_basis": "PTRS public payment-times tables when available, otherwise fallback proxy formula",
        "source_period": PTRS_SOURCE_PERIOD,
    },
    {
        "chart_id": "C10",
        "chart_title": "AP Days Benchmark and Stress by Industry",
        "chart_file": "working_capital_ap_days.png",
        "source_sheet": "chart_data_wc_ap",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/industry_working_capital_risk_metrics.csv",
        "metric_basis": "PTRS public payment-times tables when available, otherwise fallback proxy formula",
        "source_period": PTRS_SOURCE_PERIOD,
    },
    {
        "chart_id": "C11",
        "chart_title": "Inventory Days and Stock-Build Risk by Industry",
        "chart_file": "working_capital_inventory.png",
        "source_sheet": "chart_data_wc_inv",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/industry_working_capital_risk_metrics.csv",
        "metric_basis": "ABS quarterly inventories/sales ratio converted to estimated inventory days plus stock-build overlay",
        "source_period": INVENTORY_SOURCE_PERIOD,
    },
    {
        "chart_id": "C12",
        "chart_title": "Working-Capital Overlay Scores for PD, Scorecard, and LGD",
        "chart_file": "working_capital_overlay.png",
        "source_sheet": "chart_data_wc_overlay",
        "source_workbook": REPORT_WORKBOOK_RELATIVE,
        "source_table": "output/tables/industry_working_capital_risk_metrics.csv",
        "metric_basis": "Deterministic overlay scores derived from AR, AP, inventory, and cash-conversion-cycle metrics",
        "source_period": OVERLAY_SOURCE_PERIOD,
    },
]


def _public_data_vintage_markdown_lines() -> list[str]:
    lines = [
        "## Current Public Data Vintages Used",
        "",
        "The current generated outputs are based on the following staged source vintages. If any of these files are refreshed, rerun `python scripts/run_pipeline.py` so the workbook, tables, markdown outputs, and PDF report are rebuilt from the newer periods.",
        "",
    ]
    for dataset, period, cadence in PUBLIC_DATA_VINTAGES:
        lines.append(f"- **{dataset}**: {period}. Update cadence: {cadence}.")
    lines.append("")
    return lines


def _public_data_vintage_cover_text() -> str:
    return (
        "Current source vintages in this report: ABS Australian Industry FY 2022-23 to FY 2023-24; "
        "ABS Business Indicators series to December 2025; ABS labour and approvals series to February 2026; "
        "RBA F1 local snapshot published 2 April 2026 using the latest staged observation dated 16 March 2026; "
        "PTRS Cycle 8 July 2025 and Cycle 9 January 2026. Refresh cadence: annual, quarterly, monthly, rate-change driven, "
        "and per new PTRS cycle respectively."
    )


def _fit_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy()


def build_reporting_workbook(
    foundation_df: pd.DataFrame,
    macro_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    borrower_compare_df: pd.DataFrame,
    industry_working_capital_df: pd.DataFrame,
    borrower_working_capital_df: pd.DataFrame,
    scorecard_df: pd.DataFrame,
    pricing_df: pd.DataFrame,
    policy_df: pd.DataFrame,
    concentration_df: pd.DataFrame,
    watchlist_df: pd.DataFrame,
    stress_df: pd.DataFrame,
    workbook_path: Path,
    chart_table_path: Path,
    executive_summary_path: Path,
) -> Path:
    workbook_path.parent.mkdir(parents=True, exist_ok=True)
    chart_table_path.parent.mkdir(parents=True, exist_ok=True)
    executive_summary_path.parent.mkdir(parents=True, exist_ok=True)

    public_metrics = macro_df.reindex(
        columns=[
            "sector_key",
            "industry",
            "classification_risk_score",
            "macro_risk_score",
            "industry_base_risk_score",
            "industry_base_risk_level",
            "sales_m_latest",
            "employment_000_latest",
            "employment_yoy_growth_pct",
            "wages_to_sales_pct_latest",
            "ebitda_margin_pct_latest",
            "gross_operating_profit_to_sales_ratio_latest",
            "inventories_to_sales_ratio_latest",
            "inventory_days_est",
            "inventory_days_yoy_change",
            "inventory_stock_build_risk",
            "inventory_days_est_source",
            "demand_proxy_building_type",
            "demand_yoy_growth_pct",
            "cash_rate_latest_pct",
            "cash_rate_change_1y_pctpts",
        ]
    ).copy()
    public_metrics["metric_origin"] = "ABS/RBA public datasets"

    hardcoded_sector_benchmarks = benchmark_df.reindex(
        columns=[
            "sector_key",
            "industry",
            "debt_to_ebitda_benchmark",
            "icr_benchmark",
            "ar_days_benchmark",
            "ap_days_benchmark",
            "inventory_days_benchmark",
            "inventory_days_yoy_change",
            "inventory_stock_build_risk",
            "inventory_days_benchmark_source",
            "ar_days_benchmark_source",
            "ap_days_benchmark_source",
        ]
    ).copy()
    hardcoded_sector_benchmarks["hardcoded_input_flag"] = "Mixed"
    hardcoded_sector_benchmarks["hardcoded_reason"] = (
        "Debt/EBITDA and ICR remain deterministic proxy benchmarks; AR/AP timing uses reconstructed official PTRS tables when available, otherwise fallback proxy formulas"
    )

    hardcoded_borrowers = borrower_compare_df[
        [
            "borrower_name",
            "industry",
            "revenue",
            "ebitda",
            "total_debt",
            "interest_expense",
            "accounts_receivable",
            "accounts_payable",
            "inventory",
            "cogs_or_purchases",
            "ebitda_margin_pct",
            "debt_to_ebitda",
            "icr",
            "ar_days",
            "ap_days",
            "inventory_days",
            "borrower_profile_source",
        ]
    ].copy()
    hardcoded_borrowers["hardcoded_input_flag"] = "Y"
    hardcoded_borrowers["hardcoded_reason"] = (
        "Borrower-level financial statements are not available from public industry datasets"
    )

    hardcoded_portfolio = concentration_df[["industry", "current_exposure_pct"]].copy()
    hardcoded_portfolio["hardcoded_input_flag"] = "Y"
    hardcoded_portfolio["hardcoded_reason"] = (
        "Actual internal portfolio exposure by sector is not available in the public dataset layer and remains a workbook input"
    )

    pricing_settings = pd.DataFrame(
        [
            {"setting_group": "pricing", "setting_name": f"{level}_industry_loading_pct", "value": value}
            for level, value in PRICING_LOADING.items()
        ]
        + [{"setting_group": "pricing", "setting_name": "base_margin_pct", "value": BASE_MARGIN_PCT}]
        + [
            {"setting_group": "concentration_limit", "setting_name": f"{level}_limit_pct", "value": value}
            for level, value in CONCENTRATION_LIMITS.items()
        ]
        + [
            {
                "setting_group": "policy",
                "setting_name": f"{level}_{field}",
                "value": value,
            }
            for level, fields in POLICY_RULES.items()
            for field, value in fields.items()
        ]
    )
    pricing_settings["hardcoded_input_flag"] = "Y"
    pricing_settings["hardcoded_reason"] = (
        "Pricing, policy settings, and concentration limits are internal credit settings"
    )

    chart_data_heatmap = macro_df.merge(
        foundation_df[
            [
                "sector_key",
                "cyclical_score",
                "rate_sensitivity_score",
                "demand_dependency_score",
                "external_shock_score",
            ]
        ],
        on="sector_key",
        how="left",
    )

    chart_data_industry_scores = public_metrics.copy()
    chart_data_borrower_scorecard = scorecard_df.copy()
    chart_data_pricing = pricing_df.copy()
    chart_data_concentration = concentration_df.copy()
    chart_data_watchlist = watchlist_df.copy()
    chart_data_stress = stress_df.copy()
    chart_data_wc_industry = industry_working_capital_df.copy()
    chart_data_wc_borrower = borrower_working_capital_df.copy()
    chart_data_wc_ar = industry_working_capital_df[
        [
            "industry",
            "ar_days_benchmark",
            "ar_days_stress_benchmark",
            "ar_stress_uplift_days",
            "ptrs_paid_on_time_pct_latest",
            "ar_collection_score",
            "receivables_realisation_score",
        ]
    ].copy()
    chart_data_wc_ap = industry_working_capital_df[
        [
            "industry",
            "ap_days_benchmark",
            "ap_days_stress_benchmark",
            "ap_stress_uplift_days",
            "ptrs_paid_on_time_pct_latest",
            "ap_supplier_stretch_score",
        ]
    ].copy()
    chart_data_wc_inventory = industry_working_capital_df[
        [
            "industry",
            "inventory_days_benchmark",
            "inventory_days_yoy_change",
            "inventory_stock_build_risk",
            "inventory_liquidity_score",
            "inventory_stock_build_score",
            "cash_conversion_cycle_benchmark_days",
            "cash_conversion_cycle_score",
        ]
    ].copy()
    chart_data_wc_overlay = industry_working_capital_df[
        [
            "industry",
            "working_capital_pd_overlay_score",
            "working_capital_scorecard_overlay_score",
            "working_capital_lgd_overlay_score",
            "pd_primary_driver",
            "scorecard_primary_driver",
            "lgd_primary_driver",
        ]
    ].copy()

    chart_table = pd.DataFrame(CHART_DEFINITIONS)
    save_csv(chart_table, chart_table_path)

    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        pd.DataFrame(
            [
                {
                    "section": "Purpose",
                    "detail": "Workbook-backed reporting pack for charts and formal PDF generation",
                },
                {
                    "section": "Public metrics",
                    "detail": "Public metrics in this workbook are sourced from downloaded ABS/RBA datasets, including estimated inventory days derived from ABS quarterly inventory ratios and, for AR/AP timing when available, reconstructed official PTRS tables",
                },
                {
                    "section": "Working-capital overlays",
                    "detail": "Separate AR, AP, inventory, cash-conversion-cycle, and PD/scorecard/LGD overlay sheets are included so working-capital signals can be reviewed independently from the core scorecard",
                },
                {
                    "section": "Hard-coded inputs retained",
                    "detail": "Sector debt/EBITDA and ICR proxies, borrower financials, internal portfolio exposure, pricing settings, policy settings, and concentration limits",
                },
                {
                    "section": "Chart generation rule",
                    "detail": "All charts in the PDF must read from this workbook rather than directly from raw code outputs",
                },
            ]
        ).to_excel(writer, sheet_name="README", index=False)
        _fit_columns(public_metrics).to_excel(writer, sheet_name="public_metrics", index=False)
        _fit_columns(hardcoded_sector_benchmarks).to_excel(writer, sheet_name="hardcoded_sector_bm", index=False)
        _fit_columns(hardcoded_borrowers).to_excel(writer, sheet_name="hardcoded_borrowers", index=False)
        _fit_columns(hardcoded_portfolio).to_excel(writer, sheet_name="hardcoded_portfolio", index=False)
        _fit_columns(pricing_settings).to_excel(writer, sheet_name="hardcoded_bank_sets", index=False)
        _fit_columns(chart_data_heatmap).to_excel(writer, sheet_name="chart_data_heatmap", index=False)
        _fit_columns(chart_data_industry_scores).to_excel(writer, sheet_name="chart_data_industry_s", index=False)
        _fit_columns(chart_data_borrower_scorecard).to_excel(writer, sheet_name="chart_data_borrower", index=False)
        _fit_columns(chart_data_pricing).to_excel(writer, sheet_name="chart_data_pricing", index=False)
        _fit_columns(chart_data_concentration).to_excel(writer, sheet_name="chart_data_concentrat", index=False)
        _fit_columns(chart_data_watchlist).to_excel(writer, sheet_name="chart_data_watchlist", index=False)
        _fit_columns(chart_data_stress).to_excel(writer, sheet_name="chart_data_stress", index=False)
        _fit_columns(chart_data_wc_industry).to_excel(writer, sheet_name="working_capital_ind", index=False)
        _fit_columns(chart_data_wc_borrower).to_excel(writer, sheet_name="working_capital_bor", index=False)
        _fit_columns(chart_data_wc_ar).to_excel(writer, sheet_name="chart_data_wc_ar", index=False)
        _fit_columns(chart_data_wc_ap).to_excel(writer, sheet_name="chart_data_wc_ap", index=False)
        _fit_columns(chart_data_wc_inventory).to_excel(writer, sheet_name="chart_data_wc_inv", index=False)
        _fit_columns(chart_data_wc_overlay).to_excel(writer, sheet_name="chart_data_wc_overlay", index=False)
        _fit_columns(chart_table).to_excel(writer, sheet_name="chart_table", index=False)
        _fit_columns(policy_df).to_excel(writer, sheet_name="policy_overlay", index=False)

    build_executive_summary(
        executive_summary_path,
        macro_df,
        scorecard_df,
        concentration_df,
        watchlist_df,
        stress_df,
        industry_working_capital_df,
        borrower_working_capital_df,
        chart_table_path,
        workbook_path,
    )

    return workbook_path


def _read_sheet(workbook_path: Path, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(workbook_path, sheet_name=sheet_name)


def build_executive_summary(
    output_path: Path,
    macro_df: pd.DataFrame,
    scorecard_df: pd.DataFrame,
    concentration_df: pd.DataFrame,
    watchlist_df: pd.DataFrame,
    stress_df: pd.DataFrame,
    industry_working_capital_df: pd.DataFrame,
    borrower_working_capital_df: pd.DataFrame,
    chart_table_path: Path,
    workbook_path: Path,
) -> None:
    try:
        workbook_display = workbook_path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        workbook_display = workbook_path.as_posix()
    try:
        chart_table_display = chart_table_path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        chart_table_display = chart_table_path.as_posix()
    highest_sector = macro_df.sort_values("industry_base_risk_score", ascending=False).iloc[0]
    lowest_sector = macro_df.sort_values("industry_base_risk_score", ascending=True).iloc[0]
    strongest_employment = macro_df.dropna(subset=["employment_yoy_growth_pct"]).sort_values(
        "employment_yoy_growth_pct", ascending=False
    ).iloc[0]
    weakest_employment = macro_df.dropna(subset=["employment_yoy_growth_pct"]).sort_values(
        "employment_yoy_growth_pct"
    ).iloc[0]

    highest_borrower = scorecard_df.sort_values("final_industry_risk_score", ascending=False).iloc[0]
    lowest_borrower = scorecard_df.sort_values("final_industry_risk_score", ascending=True).iloc[0]
    top_util = concentration_df.sort_values("utilisation_pct", ascending=False).iloc[0]
    breaches = concentration_df[concentration_df["breach"] == True]  # noqa: E712

    watchlist_counts = watchlist_df.groupby("industry").size().sort_values(ascending=False)
    top_watchlist = watchlist_counts.index[0] if not watchlist_counts.empty else "None"
    top_watchlist_count = int(watchlist_counts.iloc[0]) if not watchlist_counts.empty else 0
    biggest_scenario = (
        stress_df.groupby("scenario_name", as_index=False)["stress_delta"]
        .mean()
        .sort_values("stress_delta", ascending=False)
        .iloc[0]
    )

    highest_ar = industry_working_capital_df.sort_values("ar_days_benchmark", ascending=False).iloc[0]
    biggest_ar_uplift = industry_working_capital_df.sort_values("ar_stress_uplift_days", ascending=False).iloc[0]
    highest_ap = industry_working_capital_df.sort_values("ap_days_benchmark", ascending=False).iloc[0]
    highest_inventory = industry_working_capital_df.sort_values("inventory_days_benchmark", ascending=False).iloc[0]
    highest_scorecard_overlay = industry_working_capital_df.sort_values(
        "working_capital_scorecard_overlay_score", ascending=False
    ).iloc[0]
    highest_pd_overlay = industry_working_capital_df.sort_values(
        "working_capital_pd_overlay_score", ascending=False
    ).iloc[0]
    highest_lgd_overlay = industry_working_capital_df.sort_values(
        "working_capital_lgd_overlay_score", ascending=False
    ).iloc[0]
    highest_borrower_wc = borrower_working_capital_df.sort_values(
        "working_capital_pd_metric_score", ascending=False
    ).iloc[0]

    lines = [
        "# Executive Summary",
        "",
        "This reporting pack now generates a separate working-capital layer for AR, AP, and inventory signals because those metrics can inform borrower scorecards today and can later support PD and LGD thinking. Public ABS and RBA datasets remain the source for the sector view, PTRS becomes the primary AR/AP benchmark source when available, and the remaining borrower, policy, and pricing fields remain explicit proxies or synthetic assumptions.",
        "",
        "This is an APRA-informed analytical workflow rather than a replica of any internal industry risk methodology. The sector overlays, appetite framing, monitoring triggers, stress themes, and ESG treatment are aligned to prudential themes, while borrower metrics, benchmark ratios, concentration exposure, and pricing remain transparent proxies or synthetic assumptions.",
        "",
        "## Current Deliverables",
        "",
        f"- Workbook: `{workbook_display}`",
        f"- Chart table: `{chart_table_display}`",
        "- Chart explanations: `output/chart_explanations.md`",
        "- Formal PDF report: `industry_risk_formal_report.pdf`",
        "",
    ]
    lines.extend(_public_data_vintage_markdown_lines())
    lines.extend(
        [
            "## Current Sector View",
            "",
            f"- Highest current industry base risk score: **{highest_sector['industry']}** at **{highest_sector['industry_base_risk_score']:.2f}**",
            f"- Lowest current industry base risk score: **{lowest_sector['industry']}** at **{lowest_sector['industry_base_risk_score']:.2f}**",
            f"- Strongest employment growth: **{strongest_employment['industry']}** at **{strongest_employment['employment_yoy_growth_pct']:+.1f}% YoY**",
            f"- Weakest employment growth: **{weakest_employment['industry']}** at **{weakest_employment['employment_yoy_growth_pct']:+.1f}% YoY**",
            "",
            "## Borrower and Portfolio View",
            "",
            f"- Highest borrower archetype score: **{highest_borrower['borrower_name']}** at **{highest_borrower['final_industry_risk_score']:.2f}**",
            f"- Lowest borrower archetype score: **{lowest_borrower['borrower_name']}** at **{lowest_borrower['final_industry_risk_score']:.2f}**",
            f"- Highest concentration utilisation: **{top_util['industry']}** at **{top_util['utilisation_pct']:.1f}%** of limit",
            f"- Current concentration breaches: **{', '.join(breaches['industry']) if not breaches.empty else 'None'}**",
            "",
            "## Working-Capital View",
            "",
            f"- Highest sector AR benchmark: **{highest_ar['industry']}** at **{highest_ar['ar_days_benchmark']:.1f} days**",
            f"- Largest AR stress uplift: **{biggest_ar_uplift['industry']}** at **+{biggest_ar_uplift['ar_stress_uplift_days']:.1f} days**",
            f"- Highest sector AP benchmark: **{highest_ap['industry']}** at **{highest_ap['ap_days_benchmark']:.1f} days**",
            f"- Highest inventory benchmark: **{highest_inventory['industry']}** at **{highest_inventory['inventory_days_benchmark']:.1f} days** with **{highest_inventory['inventory_stock_build_risk']}** stock-build risk",
            f"- Highest working-capital scorecard overlay: **{highest_scorecard_overlay['industry']}** at **{highest_scorecard_overlay['working_capital_scorecard_overlay_score']:.2f}**",
            f"- Highest working-capital PD overlay: **{highest_pd_overlay['industry']}** at **{highest_pd_overlay['working_capital_pd_overlay_score']:.2f}**",
            f"- Highest working-capital LGD overlay: **{highest_lgd_overlay['industry']}** at **{highest_lgd_overlay['working_capital_lgd_overlay_score']:.2f}**",
            f"- Highest borrower working-capital PD metric score: **{highest_borrower_wc['borrower_name']}** at **{highest_borrower_wc['working_capital_pd_metric_score']:.2f}**",
            "",
            "## Monitoring View",
            "",
            f"- Most watchlist triggers: **{top_watchlist}** with **{top_watchlist_count}**",
            f"- Largest average stress scenario uplift: **{biggest_scenario['scenario_name']}** at **{biggest_scenario['stress_delta']:.2f}** score points",
            "",
            "## Report Use",
            "",
            "The PDF is designed as a formal chart pack for credit and portfolio discussion. Each chart is tied to a workbook source sheet and includes a written explanation so the chart set can be reviewed without reopening the raw pipeline code.",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _build_commentary(what_it_shows: str, current_read: str, credit_relevance: str) -> str:
    return (
        f"What it shows: {what_it_shows}\n\n"
        f"Current read: {current_read}\n\n"
        f"Credit relevance: {credit_relevance}"
    )


def _chart_explanations(
    heatmap_df: pd.DataFrame,
    industry_df: pd.DataFrame,
    borrower_df: pd.DataFrame,
    pricing_df: pd.DataFrame,
    concentration_df: pd.DataFrame,
    watchlist_df: pd.DataFrame,
    stress_df: pd.DataFrame,
    industry_working_capital_df: pd.DataFrame,
) -> dict[str, str]:
    highest_sector = industry_df.sort_values("industry_base_risk_score", ascending=False).iloc[0]
    lowest_sector = industry_df.sort_values("industry_base_risk_score", ascending=True).iloc[0]

    worst_employment = industry_df.dropna(subset=["employment_yoy_growth_pct"]).sort_values("employment_yoy_growth_pct").iloc[0]
    best_employment = industry_df.dropna(subset=["employment_yoy_growth_pct"]).sort_values("employment_yoy_growth_pct", ascending=False).iloc[0]

    highest_borrower = borrower_df.sort_values("final_industry_risk_score", ascending=False).iloc[0]
    lowest_borrower = borrower_df.sort_values("final_industry_risk_score", ascending=True).iloc[0]

    highest_rate = pricing_df.sort_values("all_in_rate_pct", ascending=False).iloc[0]
    lowest_rate = pricing_df.sort_values("all_in_rate_pct", ascending=True).iloc[0]

    top_util = concentration_df.sort_values("utilisation_pct", ascending=False).iloc[0]
    breaches = concentration_df[concentration_df["breach"] == True]  # noqa: E712

    watchlist_counts = watchlist_df.groupby("industry").size().sort_values(ascending=False)
    top_watchlist = watchlist_counts.index[0] if not watchlist_counts.empty else "None"
    top_watchlist_count = int(watchlist_counts.iloc[0]) if not watchlist_counts.empty else 0

    worst_stress = (
        stress_df.groupby("industry", as_index=False)["stressed_industry_risk_score"]
        .max()
        .sort_values("stressed_industry_risk_score", ascending=False)
        .iloc[0]
    )
    biggest_scenario = (
        stress_df.groupby("scenario_name", as_index=False)["stress_delta"]
        .mean()
        .sort_values("stress_delta", ascending=False)
        .iloc[0]
    )

    dominant_dimension = (
        heatmap_df[
            [
                "cyclical_score",
                "rate_sensitivity_score",
                "demand_dependency_score",
                "external_shock_score",
            ]
        ]
        .mean()
        .sort_values(ascending=False)
        .index[0]
        .replace("_score", "")
        .replace("_", " ")
    )

    breach_text = (
        f"{len(breaches)} sector breaches are shown, led by {breaches.iloc[0]['industry']}."
        if not breaches.empty
        else "No sector currently breaches the illustrative concentration limits."
    )
    pricing_text = (
        f"The highest all-in rate is {highest_rate['all_in_rate_pct']:.2f}% for {highest_rate['borrower_name']}, "
        f"versus {lowest_rate['all_in_rate_pct']:.2f}% for {lowest_rate['borrower_name']}."
        if float(highest_rate["all_in_rate_pct"]) != float(lowest_rate["all_in_rate_pct"])
        else f"All borrower archetypes currently price at a uniform {highest_rate['all_in_rate_pct']:.2f}% all-in rate under the hard-coded pricing settings."
    )

    highest_ar = industry_working_capital_df.sort_values("ar_days_benchmark", ascending=False).iloc[0]
    highest_ap = industry_working_capital_df.sort_values("ap_days_benchmark", ascending=False).iloc[0]
    highest_inventory = industry_working_capital_df.sort_values("inventory_days_benchmark", ascending=False).iloc[0]
    highest_pd_overlay = industry_working_capital_df.sort_values(
        "working_capital_pd_overlay_score", ascending=False
    ).iloc[0]
    highest_scorecard_overlay = industry_working_capital_df.sort_values(
        "working_capital_scorecard_overlay_score", ascending=False
    ).iloc[0]
    highest_lgd_overlay = industry_working_capital_df.sort_values(
        "working_capital_lgd_overlay_score", ascending=False
    ).iloc[0]

    return {
        "C01": _build_commentary(
            "This heatmap decomposes the structural industry view into the four classification dimensions used in the model, then shows how those dimensions accumulate into the macro composite. Darker shading indicates a higher structural contribution to sector risk.",
            f"{dominant_dimension.capitalize()} is the strongest average pressure across the portfolio view, and {highest_sector['industry']} remains the most severe sector overall at {highest_sector['industry_base_risk_score']:.2f}. The chart is useful for identifying whether sector risk is being driven by one concentrated weakness or by a broad-based structural profile.",
            "In a formal credit pack, this chart helps explain why a sector ranks where it does before management moves to pricing, concentration, or monitoring actions. It supports top-down sector challenge rather than borrower-specific approval decisions.",
        ),
        "C02": _build_commentary(
            "This ranking is the core sector risk league table. It converts the structural classification view and the public macro overlay into one comparable sector score on a 1 to 5 scale.",
            f"{highest_sector['industry']} is currently the highest-risk sector at {highest_sector['industry_base_risk_score']:.2f}, while {lowest_sector['industry']} is lowest at {lowest_sector['industry_base_risk_score']:.2f}. The spread between the highest and lowest sectors shows that the current public-data read is materially differentiated rather than flat.",
            "A portfolio or industry committee would typically use this chart to identify sectors for growth, maintenance, selective origination, or restriction. It is the central ranking view that anchors the rest of the report.",
        ),
        "C03": _build_commentary(
            "This chart isolates employment growth because it is one of the cleanest public indicators of sector operating momentum and labour demand. Positive growth generally signals healthier demand conditions, while negative growth can indicate weaker activity or cost pressure.",
            f"{best_employment['industry']} shows the strongest YoY employment growth at {best_employment['employment_yoy_growth_pct']:+.1f}%, while {worst_employment['industry']} is weakest at {worst_employment['employment_yoy_growth_pct']:+.1f}%. That dispersion provides a direct cross-check on the broader sector ranking.",
            "In a formal sector reporting pack, employment is not usually used alone to set appetite, but it is a useful corroborating trend line when analysts assess whether a sector is stabilising, softening, or moving onto watchlist review.",
        ),
        "C04": _build_commentary(
            "This scorecard translates the sector view into one synthetic borrower archetype per industry so the industry analysis can be linked to borrower-level decisioning. The archetypes are deliberately transparent and should be read as illustrative comparators rather than real obligors.",
            f"{highest_borrower['borrower_name']} is currently the highest-risk archetype at {highest_borrower['final_industry_risk_score']:.2f}, while {lowest_borrower['borrower_name']} is lowest at {lowest_borrower['final_industry_risk_score']:.2f}. The chart therefore shows how sector risk can carry through to a borrower-facing scorecard even before lender-specific qualitative factors are added.",
            "A corporate credit team could use this style of view to show how industry pressure changes the expected score distribution across a target origination pipeline. It is most useful as an explanatory layer, not as a production rating model.",
        ),
        "C05": _build_commentary(
            "This chart converts the borrower score outcome into indicative pricing above the cash rate using the repo's transparent pricing grid. It separates the common base margin from the industry loading so the user can see how much of pricing is attributable to sector risk.",
            pricing_text,
            "In formal reporting, this type of page is useful because it shows whether the pricing framework is directionally consistent with risk appetite. It should still be read as illustrative because actual pricing would also depend on structure, security, tenor, return hurdles, and relationship economics.",
        ),
        "C06": _build_commentary(
            "This chart compares the proxy sector exposure mix against illustrative concentration limits. It highlights where the current portfolio shape would be above, near, or comfortably below the stated internal tolerance.",
            f"The highest utilisation is {top_util['industry']} at {top_util['utilisation_pct']:.1f}% of limit. {breach_text}",
            "This is the style of chart a portfolio forum would use to decide whether to slow new flow, require stronger structure, or actively rebalance the book. It is especially useful when combined with the sector risk ranking so management can distinguish high exposure in low-risk sectors from high exposure in stressed sectors.",
        ),
        "C07": _build_commentary(
            "This chart converts selected public-data warning signals into a sector watchlist count. It is designed to summarise monitoring pressure rather than absolute risk, so multiple triggers indicate where a sector may need more frequent review even if it is not the single highest-risk sector.",
            f"{top_watchlist} has the highest number of triggers at {top_watchlist_count}. That indicates a sector where the public signals are clustering negatively rather than showing only one isolated weak data point.",
            "A portfolio or risk team would typically use this kind of page to prioritise review resources, refresh covenant monitoring, and challenge whether current pipeline settings remain appropriate for the affected sectors.",
        ),
        "C08": _build_commentary(
            "This chart applies the simplified scenario framework to the current sector view and shows the stressed score under the worst scenario by industry. It is intended to demonstrate directional vulnerability rather than a full severe-but-plausible capital stress model.",
            f"{biggest_scenario['scenario_name']} produces the largest average uplift at {biggest_scenario['stress_delta']:.2f} score points, and {worst_stress['industry']} reaches the highest stressed score at {worst_stress['stressed_industry_risk_score']:.2f}. This highlights which sectors deteriorate fastest when the scenario overlay is applied.",
            "A formal portfolio report would use this page to support management actions such as tighter appetite, higher monitoring frequency, or stronger underwriting expectations in sectors that are both risky today and highly stress-sensitive.",
        ),
        "C09": _build_commentary(
            "This chart isolates receivables collection timing from the wider scorecard by comparing base AR days to the stressed AR benchmark. It is designed to show where collection cycles are structurally longer and where payment timing can deteriorate most under stress.",
            f"{highest_ar['industry']} currently has the longest AR benchmark at {highest_ar['ar_days_benchmark']:.1f} days, with a stress benchmark of {highest_ar['ar_days_stress_benchmark']:.1f} days. Sectors with both high base AR days and large stress uplift should be read as more exposed to collection slippage and cash-conversion pressure.",
            "From a credit perspective, this page is relevant to borrower scorecards and PD interpretation because weaker collection performance can reduce liquidity headroom and increase the probability of financial stress before leverage ratios visibly worsen.",
        ),
        "C10": _build_commentary(
            "This chart shows supplier-payment timing separately from receivables and inventory. It compares base AP days with the stressed AP benchmark so the user can identify where working-capital support may depend on extended creditor funding.",
            f"{highest_ap['industry']} currently has the longest AP benchmark at {highest_ap['ap_days_benchmark']:.1f} days, with the stress benchmark extending to {highest_ap['ap_days_stress_benchmark']:.1f} days. Longer payable cycles can improve cash conversion mechanically, but they can also point to supplier stretch when conditions tighten.",
            "In a formal working-capital review, AP metrics matter because an apparently acceptable cash-conversion position can still be fragile if it is being achieved by leaning on suppliers. That is why this chart is presented separately instead of being netted inside the CCC alone.",
        ),
        "C11": _build_commentary(
            "This chart converts the ABS inventories-to-sales ratio into estimated inventory days and overlays the stock-build flag. It therefore separates simple inventory duration from the broader question of whether stock is building into weaker conditions.",
            f"{highest_inventory['industry']} has the highest inventory benchmark at {highest_inventory['inventory_days_benchmark']:.1f} days and is flagged {highest_inventory['inventory_stock_build_risk']} on stock build. Sectors with long inventory duration and elevated build risk are more likely to experience cash lock-up or weaker inventory liquidity if demand softens.",
            "This page is particularly relevant to scorecard and LGD thinking. Inventory that is slow-moving or building into weaker trading conditions may both weaken current liquidity and reduce expected recoverability in a downside case.",
        ),
        "C12": _build_commentary(
            "This chart aggregates the AR, AP, inventory, and cash-conversion-cycle signals into three separate overlays: one for scorecard interpretation, one for PD interpretation, and one for LGD interpretation. The purpose is to prevent a single working-capital signal from doing every job.",
            f"{highest_scorecard_overlay['industry']} has the highest scorecard overlay at {highest_scorecard_overlay['working_capital_scorecard_overlay_score']:.2f}, {highest_pd_overlay['industry']} has the highest PD overlay at {highest_pd_overlay['working_capital_pd_overlay_score']:.2f}, and {highest_lgd_overlay['industry']} has the highest LGD overlay at {highest_lgd_overlay['working_capital_lgd_overlay_score']:.2f}. The different overlays show that current operating stress, default pressure, and recoverability pressure are related but not identical.",
            "This is the most management-oriented working-capital page in the pack. It helps a credit or portfolio forum see whether a sector's issue is mainly operating pressure, rising default risk, or recoverability weakness, which leads to different underwriting or monitoring responses.",
        ),
    }


def _write_chart_explanations(path: Path, chart_table: pd.DataFrame, explanations: dict[str, str]) -> None:
    lines = ["# Chart Explanations", ""]
    lines.extend(_public_data_vintage_markdown_lines())
    for row in chart_table.itertuples(index=False):
        lines.append(f"## {row.chart_id} {row.chart_title}")
        lines.append(f"Source workbook: `{row.source_workbook}`")
        lines.append(f"Source sheet: `{row.source_sheet}`")
        lines.append(f"Primary output table: `{row.source_table}`")
        lines.append(f"Metric basis: {row.metric_basis}")
        lines.append(f"Source period: {row.source_period}")
        lines.append("")
        lines.extend(explanations[row.chart_id].split("\n\n"))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _add_panel(fig: plt.Figure, x: float, y: float, w: float, h: float, facecolor: str) -> None:
    panel = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.005,rounding_size=0.012",
        linewidth=0.9,
        edgecolor=REPORT_STYLE["panel_border"],
        facecolor=facecolor,
        transform=fig.transFigure,
        clip_on=False,
        zorder=-5,
    )
    fig.add_artist(panel)


def _wrap_paragraphs(text: str, width: int) -> str:
    paragraphs = [segment.strip() for segment in text.split("\n\n") if segment.strip()]
    return "\n\n".join(textwrap.fill(paragraph, width=width) for paragraph in paragraphs)


def _render_pdf_report(
    pdf_path: Path,
    chart_table: pd.DataFrame,
    explanations: dict[str, str],
    chart_buffers: dict[str, BytesIO],
) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(pdf_path) as pdf:
        cover = plt.figure(figsize=(8.27, 11.69))
        cover.patch.set_facecolor(REPORT_STYLE["page_bg"])
        cover.add_artist(
            Rectangle((0, 0.93), 1, 0.07, transform=cover.transFigure, color=REPORT_STYLE["header_bg"], zorder=-10)
        )
        cover.text(0.08, 0.955, "Australian Industry Risk Analysis", fontsize=21, fontweight="bold", color=REPORT_STYLE["header_text"])
        cover.text(0.08, 0.905, "Formal Chart Report", fontsize=13, fontweight="bold", color=REPORT_STYLE["text_primary"])
        cover.text(0.92, 0.905, REPORT_WORKBOOK_RELATIVE, fontsize=8.5, color=REPORT_STYLE["muted"], ha="right")
        _add_panel(cover, 0.07, 0.62, 0.86, 0.25, REPORT_STYLE["panel_bg"])
        _add_panel(cover, 0.07, 0.09, 0.86, 0.49, REPORT_STYLE["panel_bg"])
        cover.text(0.09, 0.84, "Report Scope", fontsize=11.5, fontweight="bold", color=REPORT_STYLE["text_primary"])
        cover.text(
            0.09,
            0.81,
            _wrap_paragraphs(
                "This report consolidates the chart pack for industry risk analysis. Public ABS/RBA metrics are used wherever available. "
                "The report also uses estimated inventory days derived from ABS quarterly inventories/sales ratios rather than a direct official inventory-turnover-days series. "
                "AR/AP timing is anchored to reconstructed official PTRS publications when available, and the report now includes separate working-capital overlays for scorecard, PD, and LGD interpretation. "
                "The remaining explicit proxy or synthetic inputs are sector debt/EBITDA and ICR benchmarks, borrower archetype financials, "
                "internal portfolio exposure by sector, and internal pricing/policy settings.",
                width=88,
            ),
            fontsize=10.2,
            va="top",
            color=REPORT_STYLE["text_primary"],
        )
        cover.text(0.09, 0.715, "Current Source Vintages", fontsize=11.0, fontweight="bold", color=REPORT_STYLE["text_primary"])
        cover.text(
            0.09,
            0.69,
            _wrap_paragraphs(_public_data_vintage_cover_text(), width=90),
            fontsize=9.0,
            va="top",
            color=REPORT_STYLE["text_primary"],
        )
        cover.text(0.09, 0.55, "Included Charts", fontsize=11.5, fontweight="bold", color=REPORT_STYLE["text_primary"])
        y = 0.515
        for row in chart_table.itertuples(index=False):
            cover.text(0.10, y, f"{row.chart_id}", fontsize=9, color=REPORT_STYLE["text_secondary"], fontweight="bold")
            cover.text(0.15, y, row.chart_title, fontsize=9.6, color=REPORT_STYLE["text_primary"])
            cover.text(0.91, y, row.source_table, fontsize=7.8, color=REPORT_STYLE["muted"], ha="right")
            y -= 0.032
        cover.text(0.08, 0.05, "Workbook-backed report layout with source sheets and output-table references on each page.", fontsize=8.2, color=REPORT_STYLE["muted"])
        pdf.savefig(cover)
        plt.close(cover)

        for page_number, row in enumerate(chart_table.itertuples(index=False), start=2):
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.patch.set_facecolor(REPORT_STYLE["page_bg"])
            fig.add_artist(
                Rectangle((0, 0.94), 1, 0.06, transform=fig.transFigure, color=REPORT_STYLE["header_bg"], zorder=-10)
            )
            fig.text(0.08, 0.962, f"{row.chart_id} {row.chart_title}", fontsize=15.5, fontweight="bold", color=REPORT_STYLE["header_text"])
            _add_panel(fig, 0.07, 0.82, 0.86, 0.10, "#ffffff")
            _add_panel(fig, 0.07, 0.39, 0.86, 0.38, REPORT_STYLE["panel_bg"])
            _add_panel(fig, 0.07, 0.11, 0.86, 0.23, REPORT_STYLE["panel_bg"])

            fig.text(0.09, 0.885, "Source Workbook", fontsize=8.5, fontweight="bold", color=REPORT_STYLE["text_secondary"])
            fig.text(0.09, 0.865, row.source_workbook, fontsize=8.5, color=REPORT_STYLE["text_primary"])
            fig.text(0.33, 0.885, "Source Sheet", fontsize=8.5, fontweight="bold", color=REPORT_STYLE["text_secondary"])
            fig.text(0.33, 0.865, row.source_sheet, fontsize=8.5, color=REPORT_STYLE["text_primary"])
            fig.text(0.52, 0.885, "Primary Output Table", fontsize=8.5, fontweight="bold", color=REPORT_STYLE["text_secondary"])
            fig.text(0.52, 0.865, row.source_table, fontsize=8.5, color=REPORT_STYLE["text_primary"])
            fig.text(0.09, 0.837, "Metric Basis", fontsize=8.5, fontweight="bold", color=REPORT_STYLE["text_secondary"])
            fig.text(0.09, 0.819, _wrap_paragraphs(row.metric_basis, 48), fontsize=8.3, color=REPORT_STYLE["muted"], va="top")
            fig.text(0.52, 0.837, "Source Period", fontsize=8.5, fontweight="bold", color=REPORT_STYLE["text_secondary"])
            fig.text(0.52, 0.819, _wrap_paragraphs(row.source_period, 48), fontsize=8.3, color=REPORT_STYLE["muted"], va="top")

            fig.text(0.09, 0.745, "Chart", fontsize=11.2, fontweight="bold", color=REPORT_STYLE["text_primary"])
            ax_img = fig.add_axes([0.10, 0.43, 0.80, 0.29])
            chart_buffers[row.chart_file].seek(0)
            with Image.open(chart_buffers[row.chart_file]) as chart_image:
                ax_img.imshow(np.array(chart_image))
            ax_img.axis("off")

            commentary = _wrap_paragraphs(explanations[row.chart_id], 102)
            fig.text(0.09, 0.305, "Management Commentary", fontsize=11.2, fontweight="bold", color=REPORT_STYLE["text_primary"])
            commentary_ax = fig.add_axes([0.09, 0.135, 0.82, 0.145])
            commentary_ax.axis("off")
            commentary_ax.text(
                0,
                1,
                commentary,
                fontsize=9.4,
                color=REPORT_STYLE["text_primary"],
                va="top",
                ha="left",
                linespacing=1.35,
                transform=commentary_ax.transAxes,
            )
            fig.text(0.08, 0.06, f"Page {page_number}", fontsize=8.2, color=REPORT_STYLE["muted"])
            pdf.savefig(fig)
            plt.close(fig)


def _cleanup_chart_images(charts_dir: Path) -> None:
    for image_path in charts_dir.glob("*.png"):
        for _ in range(5):
            try:
                image_path.unlink(missing_ok=True)
                break
            except PermissionError:
                gc.collect()
                time.sleep(0.2)


def build_formal_chart_report(workbook_path: Path, charts_dir: Path, pdf_path: Path, explanation_path: Path) -> None:
    charts_dir.mkdir(parents=True, exist_ok=True)

    heatmap_df = _read_sheet(workbook_path, "chart_data_heatmap")
    industry_df = _read_sheet(workbook_path, "chart_data_industry_s")
    borrower_df = _read_sheet(workbook_path, "chart_data_borrower")
    pricing_df = _read_sheet(workbook_path, "chart_data_pricing")
    concentration_df = _read_sheet(workbook_path, "chart_data_concentrat")
    watchlist_df = _read_sheet(workbook_path, "chart_data_watchlist")
    stress_df = _read_sheet(workbook_path, "chart_data_stress")
    working_capital_ar_df = _read_sheet(workbook_path, "chart_data_wc_ar")
    working_capital_ap_df = _read_sheet(workbook_path, "chart_data_wc_ap")
    working_capital_inventory_df = _read_sheet(workbook_path, "chart_data_wc_inv")
    working_capital_overlay_df = _read_sheet(workbook_path, "chart_data_wc_overlay")
    working_capital_industry_df = _read_sheet(workbook_path, "working_capital_ind")
    chart_table = _read_sheet(workbook_path, "chart_table")

    chart_buffers = {
        "industry_risk_heatmap.png": BytesIO(),
        "industry_base_risk_score.png": BytesIO(),
        "industry_employment_growth.png": BytesIO(),
        "borrower_industry_risk_scorecard.png": BytesIO(),
        "pricing_grid.png": BytesIO(),
        "concentration_dashboard.png": BytesIO(),
        "watchlist_summary.png": BytesIO(),
        "stress_test_impact.png": BytesIO(),
        "working_capital_ar_days.png": BytesIO(),
        "working_capital_ap_days.png": BytesIO(),
        "working_capital_inventory.png": BytesIO(),
        "working_capital_overlay.png": BytesIO(),
    }
    viz.plot_risk_heatmap(heatmap_df, chart_buffers["industry_risk_heatmap.png"])
    viz.plot_risk_bar_chart(industry_df, chart_buffers["industry_base_risk_score.png"])
    viz.plot_employment_growth(industry_df, chart_buffers["industry_employment_growth.png"])
    viz.plot_borrower_scorecard(borrower_df, chart_buffers["borrower_industry_risk_scorecard.png"])
    viz.plot_pricing_grid(pricing_df, chart_buffers["pricing_grid.png"])
    viz.plot_concentration_dashboard(concentration_df, chart_buffers["concentration_dashboard.png"])
    viz.plot_watchlist_summary(watchlist_df, chart_buffers["watchlist_summary.png"])
    viz.plot_stress_test_impact(stress_df, chart_buffers["stress_test_impact.png"])
    viz.plot_working_capital_ar(working_capital_ar_df, chart_buffers["working_capital_ar_days.png"])
    viz.plot_working_capital_ap(working_capital_ap_df, chart_buffers["working_capital_ap_days.png"])
    viz.plot_working_capital_inventory(
        working_capital_inventory_df,
        chart_buffers["working_capital_inventory.png"],
    )
    viz.plot_working_capital_overlay(
        working_capital_overlay_df,
        chart_buffers["working_capital_overlay.png"],
    )

    explanations = _chart_explanations(
        heatmap_df,
        industry_df,
        borrower_df,
        pricing_df,
        concentration_df,
        watchlist_df,
        stress_df,
        working_capital_industry_df,
    )
    _write_chart_explanations(explanation_path, chart_table, explanations)
    _render_pdf_report(pdf_path, chart_table, explanations, chart_buffers)

    _cleanup_chart_images(charts_dir)
