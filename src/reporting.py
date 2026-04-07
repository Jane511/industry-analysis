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
from PIL import Image

from src.credit_application import BASE_MARGIN_PCT, CONCENTRATION_LIMITS, POLICY_RULES, PRICING_LOADING
from src.output import save_csv
from src import visualisation as viz


CHART_DEFINITIONS = [
    {
        "chart_id": "C01",
        "chart_title": "Industry Risk Dimensions Heatmap",
        "chart_file": "industry_risk_heatmap.png",
        "source_sheet": "chart_data_heatmap",
        "metric_basis": "Public ABS/RBA metrics plus public-data-derived classification scores",
    },
    {
        "chart_id": "C02",
        "chart_title": "Industry Base Risk Score by Sector",
        "chart_file": "industry_base_risk_score.png",
        "source_sheet": "chart_data_industry_s",
        "metric_basis": "Public ABS/RBA metrics plus public-data-derived classification scores",
    },
    {
        "chart_id": "C03",
        "chart_title": "Employment Growth by Industry",
        "chart_file": "industry_employment_growth.png",
        "source_sheet": "chart_data_industry_s",
        "metric_basis": "Public ABS labour-force series",
    },
    {
        "chart_id": "C04",
        "chart_title": "Borrower Industry Risk Scorecard",
        "chart_file": "borrower_industry_risk_scorecard.png",
        "source_sheet": "chart_data_borrower",
        "metric_basis": "Workbook hard-coded borrower archetype financials combined with public sector metrics",
    },
    {
        "chart_id": "C05",
        "chart_title": "Indicative Pricing by Borrower",
        "chart_file": "pricing_grid.png",
        "source_sheet": "chart_data_pricing",
        "metric_basis": "Workbook hard-coded pricing settings combined with workbook borrower score outputs",
    },
    {
        "chart_id": "C06",
        "chart_title": "Sector Concentration: Current Exposure vs Limit",
        "chart_file": "concentration_dashboard.png",
        "source_sheet": "chart_data_concentrat",
        "metric_basis": "Workbook hard-coded bank sector exposure plus hard-coded limit settings",
    },
    {
        "chart_id": "C07",
        "chart_title": "Industry Watchlist Trigger Count",
        "chart_file": "watchlist_summary.png",
        "source_sheet": "chart_data_watchlist",
        "metric_basis": "Public ABS/RBA signals converted into watchlist rules",
    },
    {
        "chart_id": "C08",
        "chart_title": "Industry Stress Test Impact",
        "chart_file": "stress_test_impact.png",
        "source_sheet": "chart_data_stress",
        "metric_basis": "Public ABS/RBA metrics with bank-style stress assumptions",
    },
]


def _fit_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c)[:31] for c in out.columns]
    return out


def build_reporting_workbook(
    foundation_df: pd.DataFrame,
    macro_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    borrower_compare_df: pd.DataFrame,
    scorecard_df: pd.DataFrame,
    pricing_df: pd.DataFrame,
    policy_df: pd.DataFrame,
    concentration_df: pd.DataFrame,
    watchlist_df: pd.DataFrame,
    stress_df: pd.DataFrame,
    workbook_path: Path,
    chart_table_path: Path,
) -> Path:
    workbook_path.parent.mkdir(parents=True, exist_ok=True)
    chart_table_path.parent.mkdir(parents=True, exist_ok=True)

    public_metrics = macro_df[
        [
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
            "demand_proxy_building_type",
            "demand_yoy_growth_pct",
            "cash_rate_latest_pct",
            "cash_rate_change_1y_pctpts",
        ]
    ].copy()
    public_metrics["metric_origin"] = "ABS/RBA public datasets"

    hardcoded_sector_benchmarks = benchmark_df[
        [
            "sector_key",
            "industry",
            "debt_to_ebitda_benchmark",
            "icr_benchmark",
            "ar_days_benchmark",
            "ap_days_benchmark",
        ]
    ].copy()
    hardcoded_sector_benchmarks["hardcoded_input_flag"] = "Y"
    hardcoded_sector_benchmarks["hardcoded_reason"] = (
        "Public ABS/RBA datasets do not publish sector leverage, ICR, or AR/AP day banking benchmarks directly"
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
        "Actual bank portfolio exposure by sector is internal bank information and must remain a workbook input"
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
        "Bank pricing, policy settings, and concentration limits are internal credit policy inputs"
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
                    "detail": "All public metrics in this workbook are sourced from downloaded ABS/RBA datasets already held in the repository",
                },
                {
                    "section": "Hard-coded inputs retained",
                    "detail": "Sector debt/EBITDA, ICR, AR/AP benchmarks, borrower financials, bank portfolio exposure, pricing and policy settings",
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
        _fit_columns(chart_table).to_excel(writer, sheet_name="chart_table", index=False)
        _fit_columns(policy_df).to_excel(writer, sheet_name="policy_overlay", index=False)

    return workbook_path


def _read_sheet(workbook_path: Path, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(workbook_path, sheet_name=sheet_name)


def _chart_explanations(
    heatmap_df: pd.DataFrame,
    industry_df: pd.DataFrame,
    borrower_df: pd.DataFrame,
    pricing_df: pd.DataFrame,
    concentration_df: pd.DataFrame,
    watchlist_df: pd.DataFrame,
    stress_df: pd.DataFrame,
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
        f"{len(breaches)} sector breach(es) are shown, led by {breaches.iloc[0]['industry']}."
        if not breaches.empty
        else "No sector currently breaches the hard-coded concentration limits."
    )
    pricing_text = (
        f"The highest all-in rate is {highest_rate['all_in_rate_pct']:.2f}% for {highest_rate['borrower_name']}, "
        f"versus {lowest_rate['all_in_rate_pct']:.2f}% for {lowest_rate['borrower_name']}."
        if float(highest_rate["all_in_rate_pct"]) != float(lowest_rate["all_in_rate_pct"])
        else f"All borrower archetypes currently price at a uniform {highest_rate['all_in_rate_pct']:.2f}% all-in rate under the hard-coded pricing settings."
    )

    return {
        "C01": (
            f"The heatmap shows how public-data-derived classification dimensions accumulate into the industry view. "
            f"Across the portfolio, {dominant_dimension} is the most severe average dimension, while "
            f"{highest_sector['industry']} carries the highest base score at {highest_sector['industry_base_risk_score']:.2f}."
        ),
        "C02": (
            f"This ranking is the core sector risk view for credit analysis. {highest_sector['industry']} is currently the highest-risk sector "
            f"at {highest_sector['industry_base_risk_score']:.2f}, while {lowest_sector['industry']} is lowest at "
            f"{lowest_sector['industry_base_risk_score']:.2f}. These scores combine public ABS/RBA signals with public-data-derived classification scores."
        ),
        "C03": (
            f"Employment growth is one of the cleanest public signals for near-term sector momentum. "
            f"{best_employment['industry']} shows the strongest YoY growth at {best_employment['employment_yoy_growth_pct']:+.1f}%, "
            f"while {worst_employment['industry']} is weakest at {worst_employment['employment_yoy_growth_pct']:+.1f}%."
        ),
        "C04": (
            f"This scorecard uses workbook hard-coded borrower archetype financial statements because borrower-level accounts are not public. "
            f"{highest_borrower['borrower_name']} is the highest-risk archetype at {highest_borrower['final_industry_risk_score']:.2f}, "
            f"while {lowest_borrower['borrower_name']} is lowest at {lowest_borrower['final_industry_risk_score']:.2f}."
        ),
        "C05": (
            f"Indicative pricing is driven by the workbook hard-coded pricing settings layered onto borrower risk scores. "
            f"{pricing_text}"
        ),
        "C06": (
            f"This chart compares workbook hard-coded bank sector exposure against workbook hard-coded concentration limits. "
            f"The highest utilisation is {top_util['industry']} at {top_util['utilisation_pct']:.1f}% of limit. {breach_text}"
        ),
        "C07": (
            f"Watchlist counts translate public ABS/RBA warning signals into a monitoring queue. "
            f"{top_watchlist} has the highest number of triggers at {top_watchlist_count}, which should drive intensified sector review and obligor screening."
        ),
        "C08": (
            f"The stress matrix applies bank-style scenario shocks to the public-data sector view. "
            f"{biggest_scenario['scenario_name']} produces the largest average uplift at {biggest_scenario['stress_delta']:.2f} score points, "
            f"and {worst_stress['industry']} reaches the highest stressed score at {worst_stress['stressed_industry_risk_score']:.2f}."
        ),
    }


def _write_chart_explanations(path: Path, chart_table: pd.DataFrame, explanations: dict[str, str]) -> None:
    lines = ["# Chart Explanations", ""]
    for row in chart_table.itertuples(index=False):
        lines.append(f"## {row.chart_id} {row.chart_title}")
        lines.append(explanations[row.chart_id])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _render_pdf_report(
    pdf_path: Path,
    chart_table: pd.DataFrame,
    explanations: dict[str, str],
    chart_buffers: dict[str, BytesIO],
) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(pdf_path) as pdf:
        cover = plt.figure(figsize=(8.27, 11.69))
        cover.text(0.08, 0.92, "Australian Industry Risk Analysis", fontsize=22, fontweight="bold")
        cover.text(0.08, 0.88, "Workbook-backed chart report", fontsize=14)
        cover.text(
            0.08,
            0.80,
            textwrap.fill(
                "This report consolidates the chart pack for industry risk analysis. Public ABS/RBA metrics are used wherever available. "
                "The only hard-coded workbook inputs retained are sector debt/EBITDA, ICR, AR/AP benchmarks, borrower archetype financials, "
                "bank portfolio exposure by sector, and bank pricing/policy settings.",
                width=90,
            ),
            fontsize=11,
            va="top",
        )
        cover.text(0.08, 0.68, "Included charts", fontsize=13, fontweight="bold")
        y = 0.64
        for row in chart_table.itertuples(index=False):
            cover.text(0.10, y, f"{row.chart_id}  {row.chart_title}", fontsize=10)
            y -= 0.035
        pdf.savefig(cover, bbox_inches="tight")
        plt.close(cover)

        for row in chart_table.itertuples(index=False):
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(0.08, 0.96, f"{row.chart_id} {row.chart_title}", fontsize=16, fontweight="bold")
            fig.text(0.08, 0.93, f"Source sheet: {row.source_sheet}", fontsize=9, color="#555555")
            fig.text(0.08, 0.91, f"Metric basis: {row.metric_basis}", fontsize=9, color="#555555")

            ax_img = fig.add_axes([0.08, 0.34, 0.84, 0.52])
            chart_buffers[row.chart_file].seek(0)
            with Image.open(chart_buffers[row.chart_file]) as chart_image:
                ax_img.imshow(np.array(chart_image))
            ax_img.axis("off")

            explanation = textwrap.fill(explanations[row.chart_id], width=95)
            fig.text(0.08, 0.28, "Explanation", fontsize=12, fontweight="bold")
            fig.text(0.08, 0.25, explanation, fontsize=10.5, va="top")
            pdf.savefig(fig, bbox_inches="tight")
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
    }
    viz.plot_risk_heatmap(heatmap_df, chart_buffers["industry_risk_heatmap.png"])
    viz.plot_risk_bar_chart(industry_df, chart_buffers["industry_base_risk_score.png"])
    viz.plot_employment_growth(industry_df, chart_buffers["industry_employment_growth.png"])
    viz.plot_borrower_scorecard(borrower_df, chart_buffers["borrower_industry_risk_scorecard.png"])
    viz.plot_pricing_grid(pricing_df, chart_buffers["pricing_grid.png"])
    viz.plot_concentration_dashboard(concentration_df, chart_buffers["concentration_dashboard.png"])
    viz.plot_watchlist_summary(watchlist_df, chart_buffers["watchlist_summary.png"])
    viz.plot_stress_test_impact(stress_df, chart_buffers["stress_test_impact.png"])

    explanations = _chart_explanations(
        heatmap_df,
        industry_df,
        borrower_df,
        pricing_df,
        concentration_df,
        watchlist_df,
        stress_df,
    )
    _write_chart_explanations(explanation_path, chart_table, explanations)
    _render_pdf_report(pdf_path, chart_table, explanations, chart_buffers)

    _cleanup_chart_images(charts_dir)
