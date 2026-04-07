from pathlib import Path

import pandas as pd

from src.output import save_csv


ESG_SENSITIVE_SECTORS = {
    "agriculture forestry and fishing": "Climate variability, water stress, land use",
    "manufacturing": "Energy intensity, waste, contamination",
    "construction": "Contractor practices, embodied carbon, WHS",
    "accommodation and food services": "Labour practices, energy and waste intensity",
    "transport postal and warehousing": "Fuel transition, fleet emissions, safety",
}


def build_industry_credit_appetite_strategy(macro_df: pd.DataFrame, processed_dir: Path) -> pd.DataFrame:
    rows = []
    for _, row in macro_df.iterrows():
        level = row["industry_base_risk_level"]
        if level == "Low":
            stance = "Grow"
            tenor = 7
            covenant = "Standard"
            collateral = "Normal security standards"
            action = "Target growth within portfolio limits"
        elif level == "Medium":
            stance = "Maintain"
            tenor = 5
            covenant = "Standard plus trigger monitoring"
            collateral = "Normal security with sector-specific mitigants"
            action = "Selective new lending and tighter exceptions"
        elif level == "Elevated":
            stance = "Selective"
            tenor = 3
            covenant = "Enhanced covenant package"
            collateral = "Strong collateral and tighter structure"
            action = "Prioritise stronger sponsors and lower leverage"
        else:
            stance = "Restrict"
            tenor = 2
            covenant = "Full covenant package with hard triggers"
            collateral = "Cash dominion or strong collateral support expected"
            action = "Restrict growth and escalate all exceptions"

        sector_key = row["sector_key"]
        esg_theme = ESG_SENSITIVE_SECTORS.get(sector_key, "")
        due_diligence = "Enhanced ESG due diligence" if esg_theme else "Standard ESG screening"

        rows.append(
            {
                "industry": row["industry"],
                "industry_base_risk_level": level,
                "industry_base_risk_score": row["industry_base_risk_score"],
                "credit_appetite_stance": stance,
                "max_tenor_years": tenor,
                "covenant_intensity": covenant,
                "collateral_expectation": collateral,
                "review_frequency": "Quarterly" if level in {"Elevated", "High"} else "Annual",
                "portfolio_action": action,
                "esg_sensitive_sector": bool(esg_theme),
                "esg_focus_area": esg_theme,
                "due_diligence_standard": due_diligence,
                "practice_rationale": (
                    "Aligned to APS 220/APG 220 style sector appetite, concentration, monitoring and risk/reward settings"
                ),
            }
        )

    out = pd.DataFrame(rows).sort_values(["industry_base_risk_score", "industry"], ascending=[False, True])
    save_csv(out, processed_dir / "industry_credit_appetite_strategy.csv")
    return out


def build_industry_stress_test_matrix(macro_df: pd.DataFrame, processed_dir: Path) -> pd.DataFrame:
    scenarios = [
        ("Rate shock", 0.35),
        ("Demand shock", 0.50),
        ("Margin squeeze", 0.45),
        ("Employment decline", 0.40),
    ]
    rows = []
    for _, row in macro_df.iterrows():
        base_score = float(row["industry_base_risk_score"])
        for scenario_name, severity in scenarios:
            stressed_macro = min(5.0, float(row["macro_risk_score"]) + severity)
            stressed_base = round(0.55 * float(row["classification_risk_score"]) + 0.45 * stressed_macro, 2)
            rows.append(
                {
                    "industry": row["industry"],
                    "scenario_name": scenario_name,
                    "base_macro_risk_score": row["macro_risk_score"],
                    "stressed_macro_risk_score": round(stressed_macro, 2),
                    "base_industry_risk_score": base_score,
                    "stressed_industry_risk_score": stressed_base,
                    "stress_delta": round(stressed_base - base_score, 2),
                    "implied_monitoring_action": (
                        "Escalate sector review"
                        if stressed_base >= 3.5
                        else "Maintain heightened monitoring"
                        if stressed_base >= 3.0
                        else "Monitor through BAU cycle"
                    ),
                }
            )

    out = pd.DataFrame(rows).sort_values(["industry", "stressed_industry_risk_score"], ascending=[True, False])
    save_csv(out, processed_dir / "industry_stress_test_matrix.csv")
    return out


def build_industry_esg_overlay(macro_df: pd.DataFrame, processed_dir: Path) -> pd.DataFrame:
    rows = []
    for _, row in macro_df.iterrows():
        sector_key = row["sector_key"]
        theme = ESG_SENSITIVE_SECTORS.get(sector_key, "")
        rows.append(
            {
                "industry": row["industry"],
                "esg_sensitive_sector": bool(theme),
                "esg_focus_area": theme if theme else "No elevated sector overlay",
                "credit_policy_overlay": (
                    "Restricted appetite or enhanced due diligence"
                    if theme
                    else "Standard policy settings"
                ),
                "monitoring_expectation": (
                    "Obligor ESG review at origination and annual review"
                    if theme
                    else "Standard credit review cycle"
                ),
                "source_note": (
                    "Built to reflect Australian bank practice of maintaining high-risk ESG/sensitive sector overlays"
                ),
            }
        )
    out = pd.DataFrame(rows).sort_values(["esg_sensitive_sector", "industry"], ascending=[False, True])
    save_csv(out, processed_dir / "industry_esg_sensitivity_overlay.csv")
    return out
