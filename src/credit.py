"""Borrower-level pricing and policy overlays."""

import pandas as pd


# ---------------------------------------------------------------------------
# Pricing grid
# ---------------------------------------------------------------------------
PRICING_LOADING = {
    'Low': 0.00,
    'Medium': 0.25,
    'Elevated': 0.50,
    'High': 1.00,
}

BASE_MARGIN_PCT = 2.50  # base margin above cash rate


def build_pricing_grid(scorecard_df: pd.DataFrame, cash_rate: float) -> pd.DataFrame:
    """Map each borrower's risk level to an indicative lending rate.

    Rate = cash_rate + base_margin + industry_risk_loading.
    """
    df = scorecard_df.copy()
    df['cash_rate_pct'] = cash_rate
    df['base_margin_pct'] = BASE_MARGIN_PCT
    df['industry_loading_pct'] = df['risk_level'].map(PRICING_LOADING)
    df['indicative_rate_pct'] = df['base_margin_pct'] + df['industry_loading_pct']
    df['all_in_rate_pct'] = df['cash_rate_pct'] + df['indicative_rate_pct']
    return df[['borrower_name', 'industry', 'risk_level', 'final_industry_risk_score',
               'cash_rate_pct', 'base_margin_pct', 'industry_loading_pct',
               'indicative_rate_pct', 'all_in_rate_pct']]


# ---------------------------------------------------------------------------
# Policy overlay
# ---------------------------------------------------------------------------
POLICY_RULES = {
    'Low': {
        'max_lvr_pct': 80,
        'review_frequency': 'Annual',
        'approval_authority': 'Standard delegated authority',
        'additional_conditions': 'None',
    },
    'Medium': {
        'max_lvr_pct': 75,
        'review_frequency': 'Annual',
        'approval_authority': 'Standard delegated authority',
        'additional_conditions': 'Industry section in credit memo required',
    },
    'Elevated': {
        'max_lvr_pct': 65,
        'review_frequency': 'Semi-annual',
        'approval_authority': 'Senior credit officer',
        'additional_conditions': 'Enhanced due diligence; stress-test cash flows',
    },
    'High': {
        'max_lvr_pct': 50,
        'review_frequency': 'Quarterly',
        'approval_authority': 'Credit committee',
        'additional_conditions': 'New lending subject to committee approval; mandatory collateral revaluation',
    },
}


def build_policy_overlay(scorecard_df: pd.DataFrame) -> pd.DataFrame:
    """Attach credit policy restrictions based on industry risk level."""
    rows = []
    for _, r in scorecard_df.iterrows():
        level = r['risk_level']
        rules = POLICY_RULES.get(level, POLICY_RULES['Medium'])
        rows.append({
            'borrower_name': r['borrower_name'],
            'industry': r['industry'],
            'risk_level': level,
            'final_industry_risk_score': r['final_industry_risk_score'],
            **rules,
        })
    return pd.DataFrame(rows)

