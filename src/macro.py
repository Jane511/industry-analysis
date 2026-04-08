"""Stage 2: macro and sector-trend signals built from public data."""

from pathlib import Path
import pandas as pd
import numpy as np
from src.load_public_data import load_rba_cash_rate, parse_abs_timeseries_xlsx, parse_labour_force, parse_building_approvals, parse_australian_industry_totals
from src.output import save_csv
from src.utils import normalise_text, score_employment_growth, score_margin_level, score_margin_trend, score_demand_growth, risk_band


def _sector_key(value: str) -> str:
    key = normalise_text(value)
    if key == 'health care and social assistance private':
        return 'health care and social assistance'
    return key


def _latest_and_yoy(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    measure = df['measure'].iloc[0]
    for industry, g in df.groupby('industry'):
        g = g.sort_values('date').dropna(subset=['value'])
        if g.empty:
            continue
        latest = g.iloc[-1]
        prev = g[g['date'] <= latest['date'] - pd.DateOffset(years=1)]
        prev = prev.iloc[-1] if not prev.empty else None
        rows.append({
            'industry': industry,
            f'{measure}_latest': float(latest['value']),
            f'{measure}_latest_date': latest['date'].date().isoformat(),
            f'{measure}_yoy_change': (float(latest['value']) - float(prev['value'])) if prev is not None else np.nan,
        })
    return pd.DataFrame(rows)

def _resolve_public_file(public_dir: Path, filename: str) -> Path:
    direct_path = public_dir / filename
    if direct_path.exists():
        return direct_path

    parent_path = public_dir.parent / filename
    if parent_path.exists():
        return parent_path

    raise FileNotFoundError(f"Could not find {filename} in {public_dir} or {public_dir.parent}")


DEMAND_PROXY_MAP = {
    'construction': 'Total Non-residential',
    'retail trade': 'Retail and wholesale trade buildings',
    'accommodation and food services': 'Short term accommodation buildings',
    'health care and social assistance': 'Health buildings',
    'transport postal and warehousing': 'Warehouses',
    'professional scientific and technical services': 'Offices',
    'manufacturing': 'Industrial Buildings - Total',
    'agriculture forestry and fishing': 'Agricultural and aquacultural buildings',
    'wholesale trade': 'Warehouses',
}


LOW_RELIABILITY_DEMAND_PROXY_SECTORS = {
    'health care and social assistance',
    'professional scientific and technical services',
}


QUARTER_DAYS = 91.25
INVENTORY_HIGH_RELEVANCE_SECTORS = {
    'agriculture forestry and fishing',
    'manufacturing',
    'wholesale trade',
    'retail trade',
}
INVENTORY_MEDIUM_RELEVANCE_SECTORS = {
    'construction',
    'accommodation and food services',
    'transport postal and warehousing',
}
INVENTORY_FALLBACK_BASE_DAYS = {
    'high': 28.0,
    'medium': 18.0,
    'low': 8.0,
}
INVENTORY_FALLBACK_BOUNDS = {
    'high': (12.0, 75.0),
    'medium': (8.0, 45.0),
    'low': (5.0, 20.0),
}
INVENTORY_STOCK_BUILD_RISK_MAP = {
    'Low': 1,
    'Moderate': 2,
    'Elevated': 4,
    'High': 5,
}


def _inventory_relevance(sector_key: str) -> str:
    if sector_key in INVENTORY_HIGH_RELEVANCE_SECTORS:
        return 'high'
    if sector_key in INVENTORY_MEDIUM_RELEVANCE_SECTORS:
        return 'medium'
    return 'low'


def _to_ratio(value: float) -> float:
    if pd.isna(value):
        return np.nan
    value = float(value)
    return value / 100 if value > 1 else value


def _margin_ratio_latest(row: pd.Series) -> float:
    margin_ratio = _to_ratio(row.get('gross_operating_profit_to_sales_ratio_latest'))
    if pd.notna(margin_ratio):
        return margin_ratio
    return _to_ratio(row.get('ebitda_margin_pct_latest'))


def _margin_ratio_prev(row: pd.Series) -> float:
    latest_ratio = _to_ratio(row.get('gross_operating_profit_to_sales_ratio_latest'))
    yoy_change = row.get('gross_operating_profit_to_sales_ratio_yoy_change')
    if pd.notna(latest_ratio) and pd.notna(yoy_change):
        return latest_ratio - float(yoy_change)

    latest_margin_pct = row.get('ebitda_margin_pct_latest')
    margin_change_pctpts = row.get('ebitda_margin_change_pctpts')
    if pd.notna(latest_margin_pct) and pd.notna(margin_change_pctpts):
        return (float(latest_margin_pct) - float(margin_change_pctpts)) / 100

    return np.nan


def _estimate_inventory_days_from_ratio(inventory_ratio: float, margin_ratio: float) -> float:
    if pd.isna(inventory_ratio):
        return np.nan

    margin_ratio = 0.10 if pd.isna(margin_ratio) else float(margin_ratio)
    cogs_ratio = float(np.clip(1 - margin_ratio, 0.45, 0.95))
    # ABS business-indicators inventories/sales ratios are quarterly original ratios,
    # so the conversion to turnover days uses a quarter-length period rather than 365 days.
    return round(float(inventory_ratio) * QUARTER_DAYS / cogs_ratio, 1)


def _fallback_inventory_days(row: pd.Series) -> float:
    relevance = _inventory_relevance(row['sector_key'])
    base_days = INVENTORY_FALLBACK_BASE_DAYS[relevance]

    margin_pct = row.get('ebitda_margin_pct_latest')
    if pd.isna(margin_pct):
        margin_pct = _to_ratio(row.get('gross_operating_profit_to_sales_ratio_latest')) * 100
    if pd.notna(margin_pct):
        margin_pct = float(margin_pct)
        if margin_pct < 8:
            base_days += 4
        elif margin_pct < 12:
            base_days += 2

    sales_growth = row.get('sales_growth_pct')
    if pd.notna(sales_growth) and float(sales_growth) < 0:
        base_days += min(abs(float(sales_growth)) / 3, 8)

    demand_growth = row.get('demand_yoy_growth_pct')
    if pd.notna(demand_growth) and float(demand_growth) < 0:
        base_days += min(abs(float(demand_growth)) / 8, 8)

    wages_ratio = row.get('wages_to_sales_pct_latest')
    if relevance == 'low' and pd.notna(wages_ratio) and float(wages_ratio) > 30:
        base_days -= 2

    lower, upper = INVENTORY_FALLBACK_BOUNDS[relevance]
    return round(float(np.clip(base_days, lower, upper)), 1)


def _derive_inventory_days_est(row: pd.Series) -> float:
    inventory_days = _estimate_inventory_days_from_ratio(
        row.get('inventories_to_sales_ratio_latest'),
        _margin_ratio_latest(row),
    )
    if pd.notna(inventory_days):
        return inventory_days
    return _fallback_inventory_days(row)


def _derive_inventory_days_prev_est(row: pd.Series) -> float:
    latest_ratio = row.get('inventories_to_sales_ratio_latest')
    ratio_yoy_change = row.get('inventories_to_sales_ratio_yoy_change')
    if pd.notna(latest_ratio) and pd.notna(ratio_yoy_change):
        prev_ratio = float(latest_ratio) - float(ratio_yoy_change)
        if prev_ratio < 0:
            return np.nan
        return _estimate_inventory_days_from_ratio(prev_ratio, _margin_ratio_prev(row))
    return np.nan


def _inventory_days_source(row: pd.Series) -> str:
    if pd.notna(row.get('inventories_to_sales_ratio_latest')):
        return 'ABS quarterly inventories/sales ratio converted to estimated inventory days'
    return 'Fallback inventory-days estimate derived from public margin, sales, demand, and sector inventory profile'


def _inventory_stock_build_risk(row: pd.Series) -> str:
    points = 0.0
    days_est = row.get('inventory_days_est')
    days_yoy_change = row.get('inventory_days_yoy_change')
    ratio_yoy_change = row.get('inventories_to_sales_ratio_yoy_change')
    sales_growth = row.get('sales_growth_pct')
    demand_growth = row.get('demand_yoy_growth_pct')
    margin_yoy_change = row.get('gross_operating_profit_to_sales_ratio_yoy_change')
    relevance = _inventory_relevance(row['sector_key'])

    if pd.notna(days_est):
        if float(days_est) >= 60:
            points += 2
        elif float(days_est) >= 35:
            points += 1

    if pd.notna(days_yoy_change):
        if float(days_yoy_change) >= 12:
            points += 2
        elif float(days_yoy_change) >= 5:
            points += 1

    if pd.notna(ratio_yoy_change):
        if float(ratio_yoy_change) >= 0.05:
            points += 2
        elif float(ratio_yoy_change) >= 0.02:
            points += 1

    stock_rising = (
        (pd.notna(days_yoy_change) and float(days_yoy_change) > 0)
        or (pd.notna(ratio_yoy_change) and float(ratio_yoy_change) > 0)
    )
    if stock_rising:
        if pd.notna(sales_growth) and float(sales_growth) <= 0:
            points += 1
        if pd.notna(demand_growth) and float(demand_growth) < 0:
            points += 1
        if pd.notna(margin_yoy_change) and float(margin_yoy_change) < 0:
            points += 1

    if relevance == 'low':
        points = max(0, points - 1)
    elif relevance == 'medium' and points > 0:
        points -= 0.5

    if points >= 4:
        return 'High'
    if points >= 2.5:
        return 'Elevated'
    if points >= 1:
        return 'Moderate'
    return 'Low'


def _score_inventory_days_est(days_est: float) -> int:
    if pd.isna(days_est):
        return 3
    if days_est < 10:
        return 1
    if days_est < 25:
        return 2
    if days_est < 40:
        return 3
    if days_est < 60:
        return 4
    return 5


def _score_inventory_risk(row: pd.Series) -> int:
    level_score = _score_inventory_days_est(row.get('inventory_days_est'))
    build_score = INVENTORY_STOCK_BUILD_RISK_MAP.get(row.get('inventory_stock_build_risk'), 3)
    return int(np.clip(round(0.7 * level_score + 0.3 * build_score), 1, 5))

def build_macro_view(classification_df: pd.DataFrame, public_dir: Path, processed_dir: Path) -> pd.DataFrame:
    ai = parse_australian_industry_totals(public_dir / '81550DO001_202324.xlsx')
    ai['sector_key'] = ai['sector'].map(_sector_key)
    ai_latest = ai[ai['year'] == '2023-24'].copy()
    ai_prev = ai[ai['year'] == '2022-23'].copy()
    ai_summary = ai_latest[['sector_key','sector','sales_m','employment_000','ebitda_margin_pct','op_profit_margin_pct','wages_to_sales_pct']].merge(
        ai_prev[['sector_key','sales_m','ebitda_margin_pct']], on='sector_key', suffixes=('_latest','_prev'), how='left'
    )
    ai_summary['sales_growth_pct'] = (ai_summary['sales_m_latest'] / ai_summary['sales_m_prev'] - 1) * 100
    ai_summary['ebitda_margin_change_pctpts'] = ai_summary['ebitda_margin_pct_latest'] - ai_summary['ebitda_margin_pct_prev']
    ai_summary = ai_summary.rename(columns={'wages_to_sales_pct': 'wages_to_sales_pct_latest'})

    profit = parse_abs_timeseries_xlsx(public_dir / '56760022_dec2025_profit_ratio.xlsx', 'gross_operating_profit_to_sales_ratio')
    inventory = parse_abs_timeseries_xlsx(public_dir / '56760023_dec2025_inventory_ratio.xlsx', 'inventories_to_sales_ratio')
    profit_summary = _latest_and_yoy(profit)
    inventory_summary = _latest_and_yoy(inventory)
    profit_summary['sector_key'] = profit_summary['industry'].map(_sector_key)
    inventory_summary['sector_key'] = inventory_summary['industry'].map(_sector_key)

    labour = parse_labour_force(public_dir / '6291004_feb2026_labour_force_industry.xlsx')
    labour = labour[labour['series_type'] == 'Trend'].copy()
    labour_rows = []
    for industry, g in labour.groupby('industry'):
        g = g.sort_values('date').dropna(subset=['value'])
        latest = g.iloc[-1]
        prev = g[g['date'] <= latest['date'] - pd.DateOffset(years=1)]
        prev = prev.iloc[-1] if not prev.empty else None
        labour_rows.append({
            'industry': industry,
            'employment_latest_000': float(latest['value']),
            'employment_latest_date': latest['date'].date().isoformat(),
            'employment_yoy_growth_pct': ((float(latest['value']) / float(prev['value']) - 1) * 100) if prev is not None else np.nan,
        })
    labour_summary = pd.DataFrame(labour_rows)
    labour_summary['sector_key'] = labour_summary['industry'].map(_sector_key)

    approvals = parse_building_approvals(public_dir / '87310051_feb2026_building_approvals_nonres.xlsx')
    approvals = approvals[approvals['sector_group'] == 'Total Sectors'].copy()
    approval_rows = []
    for building_type, g in approvals.groupby('building_type'):
        g = g.sort_values('date').dropna(subset=['value'])
        latest = g.iloc[-1]
        prev = g[g['date'] <= latest['date'] - pd.DateOffset(years=1)]
        prev = prev.iloc[-1] if not prev.empty else None
        approval_rows.append({
            'building_type': building_type,
            'building_value_latest_k': float(latest['value']),
            'building_latest_date': latest['date'].date().isoformat(),
            'building_yoy_growth_pct': ((float(latest['value']) / float(prev['value']) - 1) * 100) if prev is not None and prev['value'] else np.nan,
        })
    approval_summary = pd.DataFrame(approval_rows)

    demand_rows = []
    for sector_key, building_type in DEMAND_PROXY_MAP.items():
        row = approval_summary[approval_summary['building_type'] == building_type]
        if not row.empty:
            demand_growth = row.iloc[0]['building_yoy_growth_pct']
            if sector_key in LOW_RELIABILITY_DEMAND_PROXY_SECTORS:
                demand_growth = np.nan
            demand_rows.append({
                'sector_key': sector_key,
                'demand_proxy_building_type': building_type,
                'demand_yoy_growth_pct': demand_growth,
            })
    demand_proxy = pd.DataFrame(demand_rows)

    cash = load_rba_cash_rate(_resolve_public_file(public_dir, 'rba_f1_data.csv')).sort_values('date')
    cash_latest = float(cash.iloc[-1]['Cash Rate Target'])
    cash_prev = float(cash[cash['date'] <= cash['date'].max() - pd.DateOffset(years=1)].iloc[-1]['Cash Rate Target'])
    cash_change_1y = cash_latest - cash_prev

    public = classification_df[['sector_key','anzsic_division_code','industry','internal_grouping_example','classification_risk_score']].copy()
    public = public.merge(
        ai_summary[
            [
                'sector_key',
                'sales_m_latest',
                'employment_000',
                'ebitda_margin_pct_latest',
                'ebitda_margin_change_pctpts',
                'sales_growth_pct',
                'wages_to_sales_pct_latest',
            ]
        ],
        on='sector_key',
        how='left',
    )
    public = public.rename(columns={'employment_000': 'employment_000_latest'})
    public = public.merge(profit_summary[['sector_key','gross_operating_profit_to_sales_ratio_latest','gross_operating_profit_to_sales_ratio_yoy_change']], on='sector_key', how='left')
    public = public.merge(inventory_summary[['sector_key','inventories_to_sales_ratio_latest','inventories_to_sales_ratio_yoy_change']], on='sector_key', how='left')
    public = public.merge(labour_summary[['sector_key','employment_yoy_growth_pct']], on='sector_key', how='left')
    public = public.merge(demand_proxy, on='sector_key', how='left')
    public['cash_rate_latest_pct'] = cash_latest
    public['cash_rate_change_1y_pctpts'] = cash_change_1y
    public['inventory_days_est'] = public.apply(_derive_inventory_days_est, axis=1)
    public['inventory_days_prev_est'] = public.apply(_derive_inventory_days_prev_est, axis=1)
    public['inventory_days_yoy_change'] = (public['inventory_days_est'] - public['inventory_days_prev_est']).round(1)
    public['inventory_days_est_source'] = public.apply(_inventory_days_source, axis=1)
    public['inventory_stock_build_risk'] = public.apply(_inventory_stock_build_risk, axis=1)

    public['employment_score'] = public['employment_yoy_growth_pct'].apply(score_employment_growth)
    public['margin_level_score'] = public['gross_operating_profit_to_sales_ratio_latest'].combine_first(public['ebitda_margin_pct_latest']).apply(score_margin_level)
    public['margin_trend_score'] = public['gross_operating_profit_to_sales_ratio_yoy_change'].combine_first(public['ebitda_margin_change_pctpts']).apply(score_margin_trend)
    public['inventory_score'] = public.apply(_score_inventory_risk, axis=1)
    public['demand_score'] = public['demand_yoy_growth_pct'].apply(score_demand_growth)
    public['macro_risk_score'] = public[['employment_score','margin_level_score','margin_trend_score','inventory_score','demand_score']].mean(axis=1).round(2)
    public['industry_base_risk_score'] = (0.55 * public['classification_risk_score'] + 0.45 * public['macro_risk_score']).round(2)
    public['industry_base_risk_level'] = public['industry_base_risk_score'].apply(risk_band)
    public = public.drop(columns=['inventory_days_prev_est'])

    save_csv(public, processed_dir / 'industry_macro_view_public_signals.csv')
    return public
