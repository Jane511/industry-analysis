from pathlib import Path
import pandas as pd
from src.output import save_csv
from src.utils import risk_band

def build_scorecard(bottom_up_df: pd.DataFrame, processed_dir: Path, output_tables_dir: Path) -> pd.DataFrame:
    df = bottom_up_df.copy()
    df['final_industry_risk_score'] = (
        0.35 * df['classification_risk_score'] +
        0.30 * df['macro_risk_score'] +
        0.35 * df['bottom_up_risk_score']
    ).round(2)
    df['risk_level'] = df['final_industry_risk_score'].apply(risk_band)
    summary = df[['borrower_name','industry','classification_risk_score','macro_risk_score','bottom_up_risk_score','final_industry_risk_score','risk_level']].sort_values(['final_industry_risk_score','borrower_name'], ascending=[False, True])
    save_csv(summary, processed_dir / 'borrower_industry_risk_scorecard.csv')
    save_csv(summary, output_tables_dir / 'borrower_industry_risk_scorecard.csv')
    return summary
