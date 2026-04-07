from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_PUBLIC_DIR = REPO_ROOT / "data" / "raw" / "public"
RAW_PUBLIC_DIR_ABS = RAW_PUBLIC_DIR / "abs"
RAW_PUBLIC_DIR_PTRS = RAW_PUBLIC_DIR / "ptrs"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_TABLES_DIR = REPO_ROOT / "output" / "tables"
OUTPUT_CHARTS_DIR = REPO_ROOT / "output" / "charts"
DOCS_DIR = REPO_ROOT / "docs"
DELIVERABLES_DIR = OUTPUT_DIR
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
