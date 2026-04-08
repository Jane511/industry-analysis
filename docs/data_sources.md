# Data Sources

This repo uses official Australian public data for the public-data layer.

## Classification
- https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/latest-release
- https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/2006-revision-2-0/numbering-system-and-titles/division-codes-and-titles
- https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/2006-revision-2-0/numbering-system-and-titles/division-subdivision-group-and-class-codes-and-titles

## Public macro / industry datasets
- https://www.abs.gov.au/statistics/industry/industry-overview/australian-industry/2023-24/81550DO001_202324.xlsx
- https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/dec-2025/56760022.xlsx
- https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/dec-2025/56760023.xlsx
- https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia-detailed/feb-2026/6291004.xlsx
- https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/feb-2026/87310051.xlsx
- https://www.rba.gov.au/statistics/tables/csv/f1-data.csv

## Optional public AR benchmark source
- https://paymenttimes.gov.au/sites/ptrs.gov.au/files/2025-07/reg-update-july-2025.pdf
- https://paymenttimes.gov.au/sites/ptrs.gov.au/files/2026-01/regulators-update-202601.pdf
- https://paymenttimes.gov.au/sites/ptrs.gov.au/files/regulatory-resource/ptrs-guidance-materials-march2025.pdf

The repo can download those official PTRS publications and automatically rebuild `data/raw/public/ptrs/PTRS_MultiCycle_AR_Days_Model_Official.xlsx` from the published cycle tables.

## Current source vintages used by the model

| Dataset | Local file | Current period used | Suggested refresh cadence |
|---|---|---|---|
| ABS Australian Industry | `data/raw/public/abs/81550DO001_202324.xlsx` | FY `2022-23` and FY `2023-24` annual values | Annual |
| ABS Business Indicators - Profit ratio | `data/raw/public/abs/56760022_dec2025_profit_ratio.xlsx` | Quarterly series through `December 2025` | Quarterly |
| ABS Business Indicators - Inventory ratio | `data/raw/public/abs/56760023_dec2025_inventory_ratio.xlsx` | Quarterly series through `December 2025` | Quarterly |
| ABS Labour Force Detailed by industry | `data/raw/public/abs/6291004_feb2026_labour_force_industry.xlsx` | Monthly series through `February 2026` | Monthly |
| ABS Building Approvals - Non-residential | `data/raw/public/abs/87310051_feb2026_building_approvals_nonres.xlsx` | Monthly series through `February 2026` | Monthly |
| RBA F1 cash-rate table | `data/raw/public/rba_f1_data.csv` | Local snapshot published `2 April 2026`, latest staged observation `16 March 2026` | Refresh when a newer RBA snapshot is staged |
| PTRS | `data/raw/public/ptrs/PTRS_MultiCycle_AR_Days_Model_Official.xlsx` rebuilt from official PDFs | Cycle `8` (`July 2025`) and Cycle `9` (`January 2026`) publications, plus `March 2025` guidance | Refresh on each new PTRS cycle publication |

After refreshing any of those files, rerun `python scripts/run_pipeline.py` so the model outputs and reporting pack are rebuilt from the new source periods.

## Generated non-public layers
Where the public datasets do not expose a direct credit metric, the repo generates deterministic, APRA-informed proxy metrics from the public ABS/RBA signals instead of relying on user-entered non-public workbook inputs.
