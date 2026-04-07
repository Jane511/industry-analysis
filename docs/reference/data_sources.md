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

## Generated non-public layers
Where the public datasets do not expose a direct banking metric, the repo generates deterministic, APRA-informed proxy metrics from the public ABS/RBA signals instead of relying on user-entered bank-only workbook inputs.
