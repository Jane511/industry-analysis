"""Portfolio monitoring — watchlist triggers based on industry risk signals."""

import pandas as pd


def build_watchlist(macro_df: pd.DataFrame) -> pd.DataFrame:
    """Flag industries that trip one or more watchlist triggers.

    Triggers:
    - Negative employment growth
    - Declining margin trend (margin_trend_score >= 4)
    - Industry base risk score >= 3.5 (deep Elevated territory)
    - Any single component score = 5 (extreme signal)
    """
    triggers = []
    component_cols = ['employment_score', 'margin_level_score', 'margin_trend_score',
                      'inventory_score', 'demand_score']

    for _, row in macro_df.iterrows():
        industry = row['industry']

        if pd.notna(row.get('employment_yoy_growth_pct')) and row['employment_yoy_growth_pct'] < 0:
            triggers.append({
                'industry': industry,
                'trigger': 'Negative employment growth',
                'value': f"{row['employment_yoy_growth_pct']:+.1f}%",
                'recommended_action': 'Review sector exposure and borrower performance',
            })

        if pd.notna(row.get('margin_trend_score')) and row['margin_trend_score'] >= 4:
            triggers.append({
                'industry': industry,
                'trigger': 'Declining margin trend',
                'value': f"Margin trend score = {row['margin_trend_score']:.0f}",
                'recommended_action': 'Request updated financials from borrowers in this sector',
            })

        if pd.notna(row.get('industry_base_risk_score')) and row['industry_base_risk_score'] >= 3.5:
            triggers.append({
                'industry': industry,
                'trigger': 'Elevated base risk score',
                'value': f"Base score = {row['industry_base_risk_score']:.2f}",
                'recommended_action': 'Tighten new lending criteria; escalate to credit committee',
            })

        for col in component_cols:
            if col in row and pd.notna(row[col]) and row[col] == 5:
                label = col.replace('_score', '').replace('_', ' ').title()
                triggers.append({
                    'industry': industry,
                    'trigger': f'Extreme signal — {label}',
                    'value': f"{col} = 5",
                    'recommended_action': f'Investigate {label.lower()} driver; consider watchlist placement',
                })

    return pd.DataFrame(triggers)
