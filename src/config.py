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
RAW_PUBLIC_DIR_RBA = RAW_PUBLIC_DIR / "rba"
RAW_PUBLIC_DIR_COTALITY = RAW_PUBLIC_DIR / "cotality"
RAW_PUBLIC_DIR_DOMAIN = RAW_PUBLIC_DIR / "domain"
RAW_PUBLIC_DIR_SQM = RAW_PUBLIC_DIR / "sqm"
RAW_PUBLIC_DIR_STATE_RENTAL_BONDS = RAW_PUBLIC_DIR / "state_rental_bonds"

# Expected ABS macro / property-reference filenames. The catalogue numbers are
# stable; only the date-suffix portion rotates each release.
ABS_MACRO_FILENAMES = {
    "cpi_all_groups": "64010001_dec2025_cpi_all_groups.xlsx",
    "cpi_subgroups": "64010007_dec2025_cpi_subgroups.xlsx",
    "ppi_manufacturing": "64270012_dec2025_ppi_manufacturing.xlsx",
    "ppi_construction": "64270013_dec2025_ppi_construction.xlsx",
    "dwelling_approvals": "87520006_feb2026_dwelling_approvals.xlsx",
    "dwelling_value": "87520011_feb2026_dwelling_value.xlsx",
}
ABS_PROPERTY_REFERENCE_FILENAMES = {
    "property_price_index": "64160001_dec2025_property_price_index.xlsx",
    "property_price_capitals": "64160002_dec2025_property_price_capitals.xlsx",
    "total_value_dwellings": "64320001_dec2025_total_value_dwellings.xlsx",
    "lending_indicators": "56010001_feb2026_lending_indicators.xlsx",
}
# NOTE: the property-detail panel (Cotality / Domain / SQM / state rental bonds
# and the RBA FSR aggregate CSV) was removed when synthetic stubs were purged —
# the engine runs on real ABS/RBA/PTRS data only. See the README
# "Not included (pending real data)" note for the real sources those would need.

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
CONTRACTS_DIR = OUTPUT_DIR / "contracts"
LEGACY_PARQUET_EXPORTS_DIR = REPO_ROOT / "data" / "exports"
EXPORT_BUSINESS_CYCLE_PANEL_CSV = CONTRACTS_DIR / "business_cycle_panel.csv"
EXPORT_PROPERTY_CYCLE_PANEL_CSV = CONTRACTS_DIR / "property_cycle_panel.csv"
EXPORT_MACRO_REGIME_FLAGS_CSV = CONTRACTS_DIR / "macro_regime_flags.csv"
EXPORT_INDUSTRY_RISK_SCORES_CSV = CONTRACTS_DIR / "industry_risk_scores.csv"
EXPORT_PROPERTY_MARKET_OVERLAYS_CSV = CONTRACTS_DIR / "property_market_overlays.csv"
EXPORT_PROPERTY_MARKET_OVERLAYS_BY_BUILDING_TYPE_CSV = (
    CONTRACTS_DIR / "property_market_overlays_by_building_type.csv"
)
EXPORT_DOWNTURN_OVERLAY_TABLE_CSV = CONTRACTS_DIR / "downturn_overlay_table.csv"
EXPORT_INDUSTRY_FINANCIAL_BENCHMARKS_CSV = (
    CONTRACTS_DIR / "industry_financial_benchmarks.csv"
)

# Canonical downstream contract (required) — real public data only (ABS/RBA/PTRS)
CORE_CONTRACT_EXPORTS = {
    "industry_risk_scores": EXPORT_INDUSTRY_RISK_SCORES_CSV,
    "property_market_overlays": EXPORT_PROPERTY_MARKET_OVERLAYS_CSV,
    "downturn_overlay_table": EXPORT_DOWNTURN_OVERLAY_TABLE_CSV,
    "macro_regime_flags": EXPORT_MACRO_REGIME_FLAGS_CSV,
    "industry_financial_benchmarks": EXPORT_INDUSTRY_FINANCIAL_BENCHMARKS_CSV,
}

# Optional explainability panels (published with the contract)
OPTIONAL_EXPLAINABILITY_EXPORTS = {
    "business_cycle_panel": EXPORT_BUSINESS_CYCLE_PANEL_CSV,
    "property_cycle_panel": EXPORT_PROPERTY_CYCLE_PANEL_CSV,
    "property_market_overlays_by_building_type": EXPORT_PROPERTY_MARKET_OVERLAYS_BY_BUILDING_TYPE_CSV,
}

ALL_CONTRACT_EXPORTS = {
    **CORE_CONTRACT_EXPORTS,
    **OPTIONAL_EXPLAINABILITY_EXPORTS,
}

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
    # Workstream A — ABS macro overlay catalogues
    "cpi_all_groups_xlsx": "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/dec-2025/640101.xlsx",
    "cpi_subgroups_xlsx": "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/dec-2025/640107.xlsx",
    "ppi_manufacturing_xlsx": "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/producer-price-indexes-australia/dec-2025/642712.xlsx",
    "ppi_construction_xlsx": "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/producer-price-indexes-australia/dec-2025/642713.xlsx",
    "dwelling_approvals_xlsx": "https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/feb-2026/875206.xlsx",
    "dwelling_value_xlsx": "https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/feb-2026/875211.xlsx",
    # Workstream B — property reference ABS catalogues
    "property_price_index_xlsx": "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities/dec-2025/641601.xlsx",
    "property_price_capitals_xlsx": "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities/dec-2025/641602.xlsx",
    "total_value_dwellings_xlsx": "https://www.abs.gov.au/statistics/economy/finance/total-value-dwellings/dec-2025/643201.xlsx",
    "lending_indicators_xlsx": "https://www.abs.gov.au/statistics/economy/finance/lending-indicators/feb-2026/560101.xlsx",
    # Workstream B — RBA tables and FSR
    "rba_table_e2_xls": "https://www.rba.gov.au/statistics/tables/xls/e02hist.xls",
    "rba_fsr_page": "https://www.rba.gov.au/publications/fsr/",
    "rba_smp_page": "https://www.rba.gov.au/publications/smp/",
    "rba_chart_pack_page": "https://www.rba.gov.au/chart-pack/",
    # Workstream B — manual-extraction sources (HTML / PDF only)
    "cotality_hvi_page": "https://www.cotality.com/au/news-research/insights/home-value-index/",
    "cotality_auction_clearance_page": "https://www.cotality.com/au/our-data/auction-results",
    "domain_quarterly_page": "https://www.domain.com.au/research/house-price-report/",
    "sqm_headline_page": "https://sqmresearch.com.au/",
    "nsw_rental_bonds_page": "https://www.fairtrading.nsw.gov.au/",
    "vic_rental_report_page": "https://www.dffh.vic.gov.au/publications/rental-report",
    "qld_median_rents_page": "https://www.rta.qld.gov.au/about-the-rta/research-and-reports/median-rents-quarterly-data",
}
