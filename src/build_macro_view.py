from pathlib import Path
import pandas as pd
import numpy as np
from src.load_public_data import load_rba_cash_rate, parse_abs_timeseries_xlsx, parse_labour_force, parse_building_approvals, parse_australian_industry_totals
from src.output import save_csv
from src.utils import normalise_text, score_employment_growth, score_margin_level, score_margin_trend, score_inventory_ratio, score_demand_growth, risk_band


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

    demand_map = {
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
    demand_rows = []
    for sector_key, building_type in demand_map.items():
        row = approval_summary[approval_summary['building_type'] == building_type]
        if not row.empty:
            demand_rows.append({
                'sector_key': sector_key,
                'demand_proxy_building_type': building_type,
                'demand_yoy_growth_pct': row.iloc[0]['building_yoy_growth_pct'],
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

    public['employment_score'] = public['employment_yoy_growth_pct'].apply(score_employment_growth)
    public['margin_level_score'] = public['gross_operating_profit_to_sales_ratio_latest'].combine_first(public['ebitda_margin_pct_latest']).apply(score_margin_level)
    public['margin_trend_score'] = public['gross_operating_profit_to_sales_ratio_yoy_change'].combine_first(public['ebitda_margin_change_pctpts']).apply(score_margin_trend)
    public['inventory_score'] = public['inventories_to_sales_ratio_latest'].apply(score_inventory_ratio)
    public['demand_score'] = public['demand_yoy_growth_pct'].apply(score_demand_growth)
    public['macro_risk_score'] = public[['employment_score','margin_level_score','margin_trend_score','inventory_score','demand_score']].mean(axis=1).round(2)
    public['industry_base_risk_score'] = (0.55 * public['classification_risk_score'] + 0.45 * public['macro_risk_score']).round(2)
    public['industry_base_risk_level'] = public['industry_base_risk_score'].apply(risk_band)

    save_csv(public, processed_dir / 'industry_macro_view_public_signals.csv')
    return public
