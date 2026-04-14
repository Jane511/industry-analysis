from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Raw input directories
RAW_DIR = REPO_ROOT / "data" / "raw"
RAW_ABS_DIR = RAW_DIR / "abs"
RAW_APRA_DIR = RAW_DIR / "apra"
RAW_RBA_DIR = RAW_DIR / "rba"
RAW_MANUAL_DIR = RAW_DIR / "manual"
RAW_PUBLIC_DIR = REPO_ROOT / "data" / "raw" / "public"
RAW_PUBLIC_DIR_ABS = RAW_PUBLIC_DIR / "abs"
RAW_PUBLIC_DIR_PTRS = RAW_PUBLIC_DIR / "ptrs"

# Processed directories
PROCESSED_ROOT_DIR = REPO_ROOT / "data" / "processed"
PROCESSED_DIR = PROCESSED_ROOT_DIR
PROCESSED_PROPERTY_DIR = PROCESSED_ROOT_DIR / "property"
PROCESSED_INDUSTRY_DIR = PROCESSED_ROOT_DIR / "industry"
PROCESSED_PROPERTY_REFERENCE_DIR = PROCESSED_PROPERTY_DIR
PROCESSED_INDUSTRY_REFERENCE_DIR = PROCESSED_INDUSTRY_DIR

# Canonical processed-public directories (new boundary-aligned contract)
PROCESSED_PUBLIC_DIR = PROCESSED_ROOT_DIR / "public"
PROCESSED_PUBLIC_INDUSTRY_DIR = PROCESSED_PUBLIC_DIR / "industry"
PROCESSED_PUBLIC_PROPERTY_DIR = PROCESSED_PUBLIC_DIR / "property"
PROCESSED_PUBLIC_PROPERTY_REFERENCE_DIR = PROCESSED_PUBLIC_DIR / "property_reference"

# Outputs
OUTPUT_DIR = REPO_ROOT / "outputs"
OUTPUT_TABLES_DIR = OUTPUT_DIR / "tables"
OUTPUT_CHARTS_DIR = OUTPUT_DIR / "charts"
OUTPUT_REPORTS_DIR = OUTPUT_DIR / "reports"

# Canonical export location (contract outputs)
EXPORTS_DIR = REPO_ROOT / "data" / "exports"
EXPORT_BUSINESS_CYCLE_PANEL_PARQUET = EXPORTS_DIR / "business_cycle_panel.parquet"
EXPORT_PROPERTY_CYCLE_PANEL_PARQUET = EXPORTS_DIR / "property_cycle_panel.parquet"
EXPORT_MACRO_REGIME_FLAGS_PARQUET = EXPORTS_DIR / "macro_regime_flags.parquet"
EXPORT_INDUSTRY_RISK_SCORES_PARQUET = EXPORTS_DIR / "industry_risk_scores.parquet"
EXPORT_PROPERTY_MARKET_OVERLAYS_PARQUET = EXPORTS_DIR / "property_market_overlays.parquet"
EXPORT_DOWNTURN_OVERLAY_TABLE_PARQUET = EXPORTS_DIR / "downturn_overlay_table.parquet"

# Canonical visible table names
OUTPUT_INDUSTRY_RISK_SCORES_CSV = OUTPUT_TABLES_DIR / "industry_risk_scores.csv"
OUTPUT_PROPERTY_MARKET_OVERLAYS_CSV = OUTPUT_TABLES_DIR / "property_market_overlays.csv"
OUTPUT_DOWNTURN_OVERLAY_TABLE_CSV = OUTPUT_TABLES_DIR / "downturn_overlay_table.csv"

# Reporting paths
DOCS_DIR = REPO_ROOT / "docs"
DELIVERABLES_DIR = OUTPUT_REPORTS_DIR
REPORT_WORKBOOK_PATH = PROCESSED_PUBLIC_INDUSTRY_DIR / "industry_risk_reporting_workbook.xlsx"
REPORT_WORKBOOK_RELATIVE = REPORT_WORKBOOK_PATH.relative_to(REPO_ROOT).as_posix()
PTRS_AR_WORKBOOK_FILENAME = "PTRS_MultiCycle_AR_Days_Model_Official.xlsx"

PUBLIC_SOURCE_URLS = {
    "anzsic_classification_page": "https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/latest-release",
    "anzsic_division_codes_page": "https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/2006-revision-2-0/numbering-system-and-titles/division-codes-and-titles",
    "anzsic_division_subdivision_class_page": "https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/2006-revision-2-0/numbering-system-and-titles/division-subdivision-group-and-class-codes-and-titles",
    "australian_industry_xlsx": "https://www.abs.gov.au/statistics/industry/industry-overview/australian-industry/2023-24/81550DO001_202324.xlsx",
    "business_indicators_profit_ratio_xlsx": "https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/dec-2025/56760022.xlsx",
    "business_indicators_inventory_ratio_xlsx": "https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/dec-2025/56760023.xlsx",
    "business_indicators_consumer_sales_xlsx": "https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/dec-2025/56760024.xlsx",
    "labour_force_industry_xlsx": "https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia-detailed/feb-2026/6291004.xlsx",
    "building_approvals_nonres_xlsx": "https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/feb-2026/87310051.xlsx",
    "rba_cash_rate_csv": "https://www.rba.gov.au/statistics/tables/csv/f1-data.csv",
    "ptrs_cycle_8_pdf": "https://paymenttimes.gov.au/sites/ptrs.gov.au/files/2025-07/reg-update-july-2025.pdf",
    "ptrs_cycle_9_pdf": "https://paymenttimes.gov.au/sites/ptrs.gov.au/files/2026-01/regulators-update-202601.pdf",
    "ptrs_guidance": "https://paymenttimes.gov.au/sites/ptrs.gov.au/files/regulatory-resource/ptrs-guidance-materials-march2025.pdf",
}
