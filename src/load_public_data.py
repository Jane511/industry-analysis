from pathlib import Path
import pandas as pd

def load_rba_cash_rate(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=[0,2,3,4,5,6,7,8,9,10], encoding='utf-8-sig')
    df = df.rename(columns={'Title':'date'})
    df['date'] = pd.to_datetime(df['date'], format='%d-%b-%Y', errors='coerce')
    df['Cash Rate Target'] = pd.to_numeric(df['Cash Rate Target'], errors='coerce')
    return df[['date','Cash Rate Target']].dropna()

def parse_abs_timeseries_xlsx(path: Path, measure_name: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name='Data1', header=None)
    dates = pd.to_datetime(df.iloc[9:,0], format='mixed', errors='coerce')
    out = []
    for j in range(1, df.shape[1]):
        header = df.iloc[0, j]
        if pd.isna(header):
            continue
        industry = str(header).split(';')[2].strip() if ';' in str(header) else str(header)
        values = pd.to_numeric(df.iloc[9:,j], errors='coerce')
        tmp = pd.DataFrame({'date': dates, 'value': values}).dropna(subset=['date'])
        tmp['industry'] = industry
        tmp['measure'] = measure_name
        out.append(tmp)
    return pd.concat(out, ignore_index=True)

def parse_labour_force(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name='Data1', header=None)
    dates = pd.to_datetime(df.iloc[9:,0], format='mixed', errors='coerce')
    out = []
    for j in range(1, df.shape[1]):
        industry_raw = df.iloc[0, j]
        series_type = df.iloc[2, j]
        if pd.isna(industry_raw) or pd.isna(series_type):
            continue
        industry = str(industry_raw).split(';')[0].strip()
        values = pd.to_numeric(df.iloc[9:,j], errors='coerce')
        tmp = pd.DataFrame({'date': dates, 'value': values}).dropna(subset=['date'])
        tmp['industry'] = industry
        tmp['series_type'] = series_type
        out.append(tmp)
    return pd.concat(out, ignore_index=True)

def parse_building_approvals(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name='Data1', header=None)
    dates = pd.to_datetime(df.iloc[9:,0], format='mixed', errors='coerce')
    out = []
    for j in range(1, df.shape[1]):
        header = df.iloc[0, j]
        if pd.isna(header):
            continue
        parts = [p.strip() for p in str(header).split(';') if p.strip()]
        if len(parts) < 3:
            continue
        values = pd.to_numeric(df.iloc[9:,j], errors='coerce')
        tmp = pd.DataFrame({'date': dates, 'value': values}).dropna(subset=['date'])
        tmp['sector_group'] = parts[1]
        tmp['building_type'] = parts[2]
        out.append(tmp)
    return pd.concat(out, ignore_index=True)

def parse_australian_industry_totals(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name='Table_1', header=None)
    df.columns = ['label','employment_000','wages_m','sales_m','total_income_m','total_expenses_m','op_profit_before_tax_m','ebitda_m','industry_value_added_m']
    records = []
    for i, row in df.iterrows():
        label = row['label']
        if isinstance(label, str) and label.lower().startswith('total '):
            for k in range(1,4):
                year_row = df.iloc[i+k]
                records.append({
                    'sector': label.replace('Total ','').strip(),
                    'year': str(year_row['label']),
                    'employment_000': year_row['employment_000'],
                    'wages_m': year_row['wages_m'],
                    'sales_m': year_row['sales_m'],
                    'op_profit_before_tax_m': year_row['op_profit_before_tax_m'],
                    'ebitda_m': year_row['ebitda_m'],
                    'industry_value_added_m': year_row['industry_value_added_m'],
                })
    out = pd.DataFrame(records)
    out['ebitda_margin_pct'] = out['ebitda_m'] / out['sales_m'] * 100
    out['op_profit_margin_pct'] = out['op_profit_before_tax_m'] / out['sales_m'] * 100
    out['wages_to_sales_pct'] = out['wages_m'] / out['sales_m'] * 100
    return out
