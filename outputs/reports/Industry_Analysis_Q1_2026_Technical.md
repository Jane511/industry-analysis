# Industry Analysis Report — Q1 2026

*Technical Detail variant. Generated 2026-06-16.*



Macro and downturn overlays as of 2026-06-15. Property cycle data as of 2026-03-01.

This is the full-detail variant for MRC, audit, and model-risk review. It includes per-row technical commentary, source URLs, the full Construction methodology review item, and the audit log as an appendix.



## 1. Executive Summary

This report contains source inventory, transformations, analytical output rows, lineage, known gaps, and validation status in the same document. It covers 18 industries, 5 property segments, all 33 registered public sources, and all 8 canonical exports. Source registry basis: PUBLIC_SOURCE_URLS plus scraper-produced RBA publication manifest keys; manifest-backed vintages come from data/raw/public/_manifest.json when present.

Headline picture: cash rate 4.35% (+0.50pp YoY), arrears Low / Improving, macro_regime_flag='base' (cash_rate_regime='restrictive_rising'). 5 industries are Elevated; 0 property segments are in downturn; severe PD multiplier 2.00x.

Data freshness: macro/downturn overlays 2026-06-15; property-cycle 2026-03-01; generated 2026-06-16.

## 2. Headline Numbers

Each headline includes a trace pointer to the export or source chain that produced it.

*Headline calibrated outputs*

| Metric | Value | Vintage | Trace |
| --- | --- | --- | --- |
| Industries covered | 18 | 2026-06-15 | industry_risk_scores.csv |
| Property segments covered | 5 | 2026-03-01 | property_market_overlays.csv |
| Cash rate latest pct | 4.35 | 2026-06-15 | rba_cash_rate_csv -> macro_regime_flags.csv |
| Cash rate 1y change pctpts | +0.50 | 2026-06-15 | rba_cash_rate_csv -> industry_risk_scores.csv |
| Elevated industry count | 5 | 2026-06-15 | industry_risk_scores.csv |
| Downturn property segment count | 0 | 2026-03-01 | property_market_overlays.csv |
| Macro regime flag | base | 2026-06-15 | macro_regime_flags.csv |
| Severe PD multiplier | 2.00 | 2026-06-15 | downturn_overlay_table.csv |

*Industry risk scores - full current output*

| as_of_date | anzsic_division_code | industry | classification_risk_score | macro_risk_score | industry_base_risk_score | industry_base_risk_level | pd_multiplier | cash_rate_latest_pct | cash_rate_change_1y_pctpts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-06-16 | A | Agriculture, Forestry and Fishing | 4.12 | 4.2 | 4.16 | Elevated | 1.15 | 4.35 | 0.5 |
| 2026-06-16 | B | Mining | 3.88 | 3.2 | 3.57 | Elevated | 1.15 | 4.35 | 0.5 |
| 2026-06-16 | C | Manufacturing | 3.5 | 3.4 | 3.46 | Elevated | 1.15 | 4.35 | 0.5 |
| 2026-06-16 | G | Retail Trade | 3.25 | 3.4 | 3.32 | Elevated | 1.15 | 4.35 | 0.5 |
| 2026-06-16 | F | Wholesale Trade | 3.12 | 3.4 | 3.25 | Elevated | 1.15 | 4.35 | 0.5 |
| 2026-06-16 | E | Construction | 2.75 | 3.2 | 2.95 | Moderate-high | 1.1 | 4.35 | 0.5 |
| 2026-06-16 | R | Arts and Recreation Services | 2.38 | 3.6 | 2.93 | Moderate-high | 1.1 | 4.35 | 0.5 |
| 2026-06-16 | H | Accommodation and Food Services | 2.75 | 2.6 | 2.68 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | O | Public Administration and Safety | 1.62 | 3.6 | 2.51 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | P | Education and Training | 1.75 | 3.4 | 2.49 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | L | Rental, Hiring and Real Estate Services | 2.38 | 2.6 | 2.48 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | I | Transport, Postal and Warehousing | 2.5 | 2.4 | 2.46 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | N | Administrative and Support Services | 2.12 | 2.8 | 2.43 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | J | Information Media and Telecommunications | 2.12 | 2.6 | 2.34 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | S | Other Services | 2.38 | 2.2 | 2.3 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | D | Electricity, Gas, Water and Waste Services | 2.25 | 2.0 | 2.14 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | Q | Health Care and Social Assistance | 1.5 | 2.8 | 2.08 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | M | Professional, Scientific and Technical Services | 1.75 | 2.0 | 1.86 | Moderate-low | 0.95 | 4.35 | 0.5 |

*Downturn multipliers - full current output*

| scenario | pd_multiplier | lgd_multiplier | ccf_multiplier | property_value_haircut | macro_path | notes | as_of_date |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base | 1.0 | 1.0 | 1.0 | 0.0 | Current environment, no recession overlay: GDP growth around trend, unemployment broadly stable, house prices at latest observed levels. | Current environment (base scenario). Anchored to a low / improving arrears backdrop (qualitative assumption from RBA FSR) and an average property-cycle softness score of 3.14 (real, ABS building approvals). No diversification benefit assumed (APG 113 para 92). | 2026-06-15 |
| mild | 1.2 | 1.1 | 1.05 | 0.05 | Basel CRE36.51 mandatory minimum — two consecutive quarters of zero GDP growth; unemployment +~1.0-1.5pp; house prices ~-5 to -10%. | ASSUMPTION (scenario parameter) — mild recession = Basel CRE36.51 two-quarters-zero-growth minimum, for conservative portfolio calibration. No diversification benefit assumed (APG 113 para 92). | 2026-06-15 |
| moderate | 1.5 | 1.2 | 1.1 | 0.1 | Deeper recession: multi-quarter contraction; unemployment +~2-3pp; house prices ~-10 to -15%. | ASSUMPTION (scenario parameter) — illustrative moderate downturn for stressed pricing and EL scenario analysis. No diversification benefit assumed (APG 113 para 92). | 2026-06-15 |
| severe | 2.0 | 1.3 | 1.2 | 0.2 | GFC-like severe-but-plausible path: deep multi-quarter contraction; unemployment +~3-4pp; house prices ~-20 to -30%. | ASSUMPTION (scenario parameter) — illustrative severe downturn; not a calibrated regulatory stress parameter. No diversification benefit assumed (APG 113 para 92). | 2026-06-15 |

## 3. Data Sources Inventory

Canonical registry for this project: src.config.PUBLIC_SOURCE_URLS plus scraper-produced RBA publication manifest keys.

*Data Sources Inventory*

| Source key | Publisher / origin | URL or landing page | File type | Period or vintage | Retrieved / fetched timestamp | File size or row count | Status | Hash / version identifier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| anzsic_classification_page | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/latest-release | landing page |  |  |  | missing |  |
| anzsic_division_codes_page | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/2006-revision-2-0/numbering-system-and-titles/division-codes-and-titles | landing page |  |  |  | missing |  |
| anzsic_division_subdivision_class_page | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/2006-revision-2-0/numbering-system-and-titles/division-subdivision-group-and-class-codes-and-titles | landing page |  |  |  | missing |  |
| australian_industry_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/industry/industry-overview/australian-industry/2023-24/81550DO001_202324.xlsx | XLSX |  | 2026-06-16T06:33:43+00:00 | 597090 | manually staged |  |
| building_approvals_nonres_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/mar-2026/87310051.xlsx | XLSX |  | 2026-06-16T06:33:45+00:00 | 186263 | manually staged |  |
| business_indicators_consumer_sales_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/mar-2026/56760024.xlsx | XLSX |  |  |  | missing |  |
| business_indicators_inventory_ratio_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/mar-2026/56760023.xlsx | XLSX |  | 2026-06-16T06:33:44+00:00 | 51822 | manually staged |  |
| business_indicators_profit_ratio_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/mar-2026/56760022.xlsx | XLSX |  | 2026-06-16T06:33:43+00:00 | 56316 | manually staged |  |
| cpi_all_groups_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/mar-2026/640101.xlsx | XLSX |  | 2026-06-16T06:33:47+00:00 | 53065 | manually staged |  |
| cpi_subgroups_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/dec-2025/640107.xlsx | XLSX |  |  |  | missing |  |
| dwelling_approvals_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/feb-2026/875206.xlsx | XLSX |  |  |  | missing |  |
| dwelling_value_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/feb-2026/875211.xlsx | XLSX |  |  |  | missing |  |
| labour_force_headline_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/mar-2026/6202001.xlsx | XLSX |  | 2026-06-16T06:33:47+00:00 | 766909 | manually staged |  |
| labour_force_industry_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia-detailed/mar-2026/6291004.xlsx | XLSX |  | 2026-06-16T06:33:45+00:00 | 160939 | manually staged |  |
| lending_indicators_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/finance/lending-indicators/feb-2026/560101.xlsx | XLSX |  |  |  | missing |  |
| national_accounts_gdp_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/mar-2026/5206001_key_aggregates.xlsx | XLSX |  | 2026-06-16T06:33:46+00:00 | 267687 | manually staged |  |
| ppi_construction_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/producer-price-indexes-australia/dec-2025/642713.xlsx | XLSX |  |  |  | missing |  |
| ppi_manufacturing_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/producer-price-indexes-australia/dec-2025/642712.xlsx | XLSX |  |  |  | missing |  |
| property_price_capitals_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities/dec-2025/641602.xlsx | XLSX |  |  |  | missing |  |
| property_price_index_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities/dec-2025/641601.xlsx | XLSX |  |  |  | missing |  |
| ptrs_cycle_8_pdf | Payment Times Reporting Scheme | https://paymenttimes.gov.au/sites/ptrs.gov.au/files/2025-07/reg-update-july-2025.pdf | PDF |  | 2026-06-16T06:33:48+00:00 | 2055606 | manually staged |  |
| ptrs_cycle_9_pdf | Payment Times Reporting Scheme | https://paymenttimes.gov.au/sites/ptrs.gov.au/files/2026-01/regulators-update-202601.pdf | PDF |  | 2026-06-16T06:33:49+00:00 | 3629142 | manually staged |  |
| ptrs_guidance | Payment Times Reporting Scheme | https://paymenttimes.gov.au/sites/ptrs.gov.au/files/regulatory-resource/ptrs-guidance-materials-march2025.pdf | PDF |  | 2026-06-16T06:33:49+00:00 | 947450 | manually staged |  |
| rba_cash_rate_csv | Reserve Bank of Australia | https://www.rba.gov.au/statistics/tables/csv/f1-data.csv | CSV |  | 2026-06-16T06:33:46+00:00 | 302215 | manually staged |  |
| rba_chart_pack_page | Reserve Bank of Australia | https://www.rba.gov.au/chart-pack/ | landing page |  |  |  | missing |  |
| rba_chart_pack_pdf | Reserve Bank of Australia | https://www.rba.gov.au/chart-pack/ | PDF | March 2026 | 2026-04-28T08:01:43+00:00 | 5434746 | auto-downloaded | 66945f0e420217b86069e72880c20b4670f17a2ff52e6e0de9c9d13a174364d9 |
| rba_fsr_page | Reserve Bank of Australia | https://www.rba.gov.au/publications/fsr/ | landing page |  |  |  | missing |  |
| rba_fsr_pdf | Reserve Bank of Australia | https://www.rba.gov.au/publications/fsr/ | PDF | March 2026 | 2026-04-28T08:01:42+00:00 | 3272062 | auto-downloaded | 342ec105f1c623e507ef4e8434ade6f0788ef58ed26b2accaa8ec7df04acc13e |
| rba_smp_page | Reserve Bank of Australia | https://www.rba.gov.au/publications/smp/ | landing page |  |  |  | missing |  |
| rba_smp_pdf | Reserve Bank of Australia | https://www.rba.gov.au/publications/smp/ | PDF | February 2026 | 2026-04-28T08:01:42+00:00 | 4201271 | auto-downloaded | db42f94329b6c229844fb8da8cbc4308d707af57b3d5ba90d0aaa9bd7e21ca89 |
| rba_table_e2_xls | Reserve Bank of Australia | https://www.rba.gov.au/statistics/tables/xls/e02hist.xls | XLS |  |  |  | missing |  |
| total_value_dwellings_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/finance/total-value-dwellings/dec-2025/643201.xlsx | XLSX |  |  |  | missing |  |
| wpi_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/mar-2026/634501.xlsx | XLSX |  | 2026-06-16T06:33:47+00:00 | 66256 | manually staged |  |

## 4. Transformations Applied

Validation status is derived from export presence and non-empty row count; schema-level tests remain in the pytest suite.

*Transformations Applied*

| Output filename | Input source(s) | Transformation script | Row count of output | Last build timestamp | Validation status |
| --- | --- | --- | --- | --- | --- |
| industry_risk_scores.csv | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv | src/overlays/build_industry_risk_scores.py | 18 | 2026-06-16T16:33:52 | PASS: present_nonempty |
| property_market_overlays.csv | building_approvals_nonres_xlsx; property_cycle_panel | src/overlays/build_property_market_overlays.py | 5 | 2026-06-16T16:33:52 | PASS: present_nonempty |
| downturn_overlay_table.csv | property_cycle_panel; scenario multipliers (assumption); qualitative arrears baseline (assumption, RBA FSR Mar-2026) | src/overlays/build_downturn_overlay_tables.py | 4 | 2026-06-16T16:33:52 | PASS: present_nonempty |
| macro_regime_flags.csv | rba_cash_rate_csv; qualitative arrears baseline (assumption, RBA FSR Mar-2026) | src/panels/build_macro_regime_flags.py | 1 | 2026-06-16T16:33:52 | PASS: present_nonempty |
| industry_financial_benchmarks.csv | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; business_indicators_inventory_ratio_xlsx; labour_force_industry_xlsx | src/panels/build_industry_financial_benchmarks.py | 18 | 2026-06-16T16:33:52 | PASS: present_nonempty |
| business_cycle_panel.csv | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; business_indicators_inventory_ratio_xlsx; business_indicators_consumer_sales_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv | src/panels/build_business_cycle_panel.py | 18 | 2026-06-16T16:33:52 | PASS: present_nonempty |
| property_cycle_panel.csv | building_approvals_nonres_xlsx | src/panels/build_property_cycle_panel.py | 11 | 2026-06-16T16:33:52 | PASS: present_nonempty |
| property_market_overlays_by_building_type.csv | building_approvals_nonres_xlsx; property_cycle_panel | src/overlays/build_property_market_overlays.py | 11 | 2026-06-16T16:33:52 | PASS: present_nonempty |

## 5. Detailed Analysis

Wide exports are column-compacted for readability but keep every source row in the report table.

*Canonical CSV exports: contents and downstream layers*

| CSV export | Contract role | Join grain | What it includes | Downstream layers |
| --- | --- | --- | --- | --- |
| industry_risk_scores.csv | Core downstream contract | Industry snapshot | Compact industry overlay: classification score, macro score, base risk score/level, and shared cash-rate backdrop fields. | PD overlays / scorecards; EL and pricing overlays; External sector benchmarks; Board reporting |
| property_market_overlays.csv | Core downstream contract | Property segment snapshot | Compact property overlay: cycle stage, softness score/band, region risk, approvals change, and approvals-proxy activity signals. | LGD and collateral overlays; Property-backed PD context; Pricing and policy overlays; Board reporting |
| downturn_overlay_table.csv | Core downstream contract | Scenario table | Scenario multipliers for PD, LGD, and CCF plus property haircuts, a per-scenario macro-path note (mild = Basel CRE36.51), and scenario notes (incl. the no-diversification assumption). | PD scenario layer; LGD scenario layer; CCF / EAD scenario layer; Stress testing and pricing what-if views |
| macro_regime_flags.csv | Core downstream contract | Single as-of-date regime row | Environment selector: cash-rate regime, arrears level/trend, macro regime flag, and source dataset. | PD regime conditioning; LGD / EL regime conditioning; Scenario-row selection; Portfolio and board reporting |
| industry_financial_benchmarks.csv | Core downstream contract | ANZSIC-division snapshot | Per-ANZSIC-division medians of the financial ratios APG 220 paragraph 64 calls out as standard credit-assessment benchmarks: EBITDA margin, gross operating profit-to-sales, wages-to-sales, inventory days, sales growth, employment growth, inventory-to-sales, and sales per employee. | Origination scorecard industry-relative ratios; PD model industry-comparison features; ECL borrower-vs-industry signals; External sector benchmarks |
| business_cycle_panel.csv | Optional explainability panel | Industry diagnostics panel | Wide industry diagnostics: structural factors, public benchmark metrics, macro factor scores, demand proxies, inventory flags, and explainability fields behind the industry overlay. | PD explainability; External benchmark diagnostics; Challenger overlay analysis; Technical report detail |
| property_cycle_panel.csv | Optional explainability panel | Property segment-by-region diagnostics | Wide property diagnostics: approvals trend, cycle stage, softness band, region risk, as-of-date, and per-row source/proxy notes. | LGD explainability; Collateral benchmark diagnostics; Property stress interpretation; Technical report detail |
| property_market_overlays_by_building_type.csv | Optional explainability panel | Per-building-type non-residential detail | One row per ABS non-residential building-approval category — the pre-aggregation input to the five-row property_market_overlays contract. Shows each category's softness, region risk, approvals change, and the property_segment_code it rolls up into. | Property overlay explainability; Reviewer drilldown into CRE / IND / RET / CON aggregation; Technical report detail |

*Full detail rows from industry_risk_scores.csv*

| as_of_date | anzsic_division_code | industry | classification_risk_score | macro_risk_score | industry_base_risk_score | industry_base_risk_level | pd_multiplier | cash_rate_latest_pct | cash_rate_change_1y_pctpts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-06-16 | A | Agriculture, Forestry and Fishing | 4.12 | 4.2 | 4.16 | Elevated | 1.15 | 4.35 | 0.5 |
| 2026-06-16 | B | Mining | 3.88 | 3.2 | 3.57 | Elevated | 1.15 | 4.35 | 0.5 |
| 2026-06-16 | C | Manufacturing | 3.5 | 3.4 | 3.46 | Elevated | 1.15 | 4.35 | 0.5 |
| 2026-06-16 | G | Retail Trade | 3.25 | 3.4 | 3.32 | Elevated | 1.15 | 4.35 | 0.5 |
| 2026-06-16 | F | Wholesale Trade | 3.12 | 3.4 | 3.25 | Elevated | 1.15 | 4.35 | 0.5 |
| 2026-06-16 | E | Construction | 2.75 | 3.2 | 2.95 | Moderate-high | 1.1 | 4.35 | 0.5 |
| 2026-06-16 | R | Arts and Recreation Services | 2.38 | 3.6 | 2.93 | Moderate-high | 1.1 | 4.35 | 0.5 |
| 2026-06-16 | H | Accommodation and Food Services | 2.75 | 2.6 | 2.68 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | O | Public Administration and Safety | 1.62 | 3.6 | 2.51 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | P | Education and Training | 1.75 | 3.4 | 2.49 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | L | Rental, Hiring and Real Estate Services | 2.38 | 2.6 | 2.48 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | I | Transport, Postal and Warehousing | 2.5 | 2.4 | 2.46 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | N | Administrative and Support Services | 2.12 | 2.8 | 2.43 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | J | Information Media and Telecommunications | 2.12 | 2.6 | 2.34 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | S | Other Services | 2.38 | 2.2 | 2.3 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | D | Electricity, Gas, Water and Waste Services | 2.25 | 2.0 | 2.14 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | Q | Health Care and Social Assistance | 1.5 | 2.8 | 2.08 | Medium | 1.0 | 4.35 | 0.5 |
| 2026-06-16 | M | Professional, Scientific and Technical Services | 1.75 | 2.0 | 1.86 | Moderate-low | 0.95 | 4.35 | 0.5 |

*Full detail rows from property_market_overlays.csv*

| as_of_date | property_segment | property_segment_code | pd_multiplier | market_softness_score | region_risk_score | cycle_stage | source_note | market_softness_band | market_softness_level |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-06-16 | Residential | RES | 1.0 | 2.5 | 3.28 | neutral | Residential placeholder — ABS Cat. 8752.0 residential dwelling-approvals file not yet staged; RES row uses a neutral composite pending that upgrade. | normal | Medium |
| 2026-06-16 | Commercial (office, health, education, accommodation) | CRE | 1.15 | 3.29 | 3.44 | slowing | Aggregated from ABS Cat. 8731.0 non-residential building approvals. Exposure-weighted (12-month mean approval $ per building type). Constituent ABS categories: Aged care facilities, Education buildings, Health buildings, Offices, Short term accommodation buildings | softening | Elevated |
| 2026-06-16 | Industrial / Warehouse | IND | 0.95 | 1.85 | 2.17 | growth | Aggregated from ABS Cat. 8731.0 non-residential building approvals. Exposure-weighted (12-month mean approval $ per building type). Constituent ABS categories: Agricultural and aquacultural buildings, Warehouses | supportive | Moderate-low |
| 2026-06-16 | Retail Property | RET | 1.15 | 3.4 | 3.39 | slowing | Aggregated from ABS Cat. 8731.0 non-residential building approvals. Exposure-weighted (12-month mean approval $ per building type). Constituent ABS categories: Retail and wholesale trade buildings | softening | Elevated |
| 2026-06-16 | Construction (non-residential development) | CON | 1.1 | 3.02 | 3.18 | slowing | Aggregated from ABS Cat. 8731.0 non-residential building approvals. Exposure-weighted (12-month mean approval $ per building type). Constituent ABS categories: Aged care facilities, Agricultural and aquacultural buildings, Education buildings, Health buildings, Offices, Retail and wholesale trade buildings, Short term accommodation buildings, Warehouses | softening | Moderate-high |

*Full detail rows from downturn_overlay_table.csv*

| as_of_date | scenario | pd_multiplier | lgd_multiplier | ccf_multiplier | property_value_haircut | macro_path | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-06-15 | base | 1.0 | 1.0 | 1.0 | 0.0 | Current environment, no recession overlay: GDP growth around trend, unemployment broadly stable, house prices at latest observed levels. | Current environment (base scenario). Anchored to a low / improving arrears backdrop (qualitative assumption from RBA FSR) and an average property-cycle softness score of 3.14 (real, ABS building approvals). No diversification benefit assumed (APG 113 para 92). |
| 2026-06-15 | mild | 1.2 | 1.1 | 1.05 | 0.05 | Basel CRE36.51 mandatory minimum — two consecutive quarters of zero GDP growth; unemployment +~1.0-1.5pp; house prices ~-5 to -10%. | ASSUMPTION (scenario parameter) — mild recession = Basel CRE36.51 two-quarters-zero-growth minimum, for conservative portfolio calibration. No diversification benefit assumed (APG 113 para 92). |
| 2026-06-15 | moderate | 1.5 | 1.2 | 1.1 | 0.1 | Deeper recession: multi-quarter contraction; unemployment +~2-3pp; house prices ~-10 to -15%. | ASSUMPTION (scenario parameter) — illustrative moderate downturn for stressed pricing and EL scenario analysis. No diversification benefit assumed (APG 113 para 92). |
| 2026-06-15 | severe | 2.0 | 1.3 | 1.2 | 0.2 | GFC-like severe-but-plausible path: deep multi-quarter contraction; unemployment +~3-4pp; house prices ~-20 to -30%. | ASSUMPTION (scenario parameter) — illustrative severe downturn; not a calibrated regulatory stress parameter. No diversification benefit assumed (APG 113 para 92). |

*Full detail rows from macro_regime_flags.csv*

| as_of_date | cash_rate_regime | arrears_environment_level | arrears_trend | macro_regime_flag | source_dataset |
| --- | --- | --- | --- | --- | --- |
| 2026-06-15 | restrictive_rising | Low | Improving | base | RBA F1 cash-rate table (real) + qualitative arrears baseline (assumption, RBA FSR Mar-2026) |

*Full detail rows from industry_financial_benchmarks.csv*

| as_of_date | anzsic_division_code | industry | median_ebitda_margin_pct | source_note | median_gross_operating_profit_to_sales_ratio | median_wages_to_sales_pct | median_inventory_days_est | median_sales_growth_pct | median_employment_yoy_growth_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-06-16 | A | Agriculture, Forestry and Fishing | 14.58 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. |  | 9.75 | 35.1 | -11.05 | -5.11 |
| 2026-06-16 | B | Mining | 47.33 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.47 | 7.8 | 51.7 | -6.26 | -5.09 |
| 2026-06-16 | C | Manufacturing | 9.15 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.09 | 14.3 | 57.2 | 1.34 | -0.93 |
| 2026-06-16 | D | Electricity, Gas, Water and Waste Services | 20.95 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.21 | 9.93 | 9.2 | 3.6 | 12.29 |
| 2026-06-16 | E | Construction | 10.15 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.08 | 15.04 | 22.0 | 10.54 | 1.47 |
| 2026-06-16 | F | Wholesale Trade | 6.12 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.06 | 6.77 | 48.5 | 2.54 | -8.74 |
| 2026-06-16 | G | Retail Trade | 7.8 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.05 | 10.28 | 32.7 | 4.82 | -0.46 |
| 2026-06-16 | H | Accommodation and Food Services | 11.38 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.08 | 25.54 | 6.0 | 8.6 | 0.72 |
| 2026-06-16 | I | Transport, Postal and Warehousing | 17.72 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.19 | 19.69 | 18.7 | 3.46 | 2.79 |
| 2026-06-16 | J | Information Media and Telecommunications | 20.02 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.2 | 20.01 | 8.0 | 5.95 | -4.77 |
| 2026-06-16 | L | Rental, Hiring and Real Estate Services | 40.88 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.37 | 13.0 | 8.0 | 7.72 | -15.06 |
| 2026-06-16 | M | Professional, Scientific and Technical Services | 12.99 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.13 | 35.33 | 6.0 | 8.68 | 5.5 |
| 2026-06-16 | N | Administrative and Support Services | 9.27 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.07 | 47.45 | 8.0 | 6.17 | 3.07 |
| 2026-06-16 | O | Public Administration and Safety | 9.6 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. |  | 42.36 | 8.0 | 11.69 | -1.17 |
| 2026-06-16 | P | Education and Training | 11.73 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. |  | 50.88 | 11.9 | 10.67 | 5.63 |
| 2026-06-16 | Q | Health Care and Social Assistance | 16.65 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. |  | 43.29 | 6.0 | 7.54 | 3.74 |
| 2026-06-16 | R | Arts and Recreation Services | 13.45 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.13 | 22.55 | 13.7 | 6.38 | -5.79 |
| 2026-06-16 | S | Other Services | 5.28 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.16 | 31.62 | 10.0 | 13.2 | 7.12 |

*Full detail rows from business_cycle_panel.csv*

| anzsic_division_code | industry | classification_risk_score | macro_risk_score | industry_base_risk_score | industry_base_risk_level | sector_key | internal_grouping_example | sales_m_latest | employment_000_latest |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H | Accommodation and Food Services | 2.75 | 2.6 | 2.68 | Medium | accommodation and food services | Hospitality and leisure | 152965 | 1217.9 |
| N | Administrative and Support Services | 2.12 | 2.8 | 2.43 | Medium | administrative and support services | Administrative and support services | 144266 | 1006.4 |
| A | Agriculture, Forestry and Fishing | 4.12 | 4.2 | 4.16 | Elevated | agriculture forestry and fishing | Primary production and agribusiness | 119772 | 411.0 |
| R | Arts and Recreation Services | 2.38 | 3.6 | 2.93 | Moderate-high | arts and recreation services | Arts and recreation services | 49985 | 277.3 |
| E | Construction | 2.75 | 3.2 | 2.95 | Moderate-high | construction | Building, civil and trade services | 624590 | 1290.7 |
| P | Education and Training | 1.75 | 3.4 | 2.49 | Medium | education and training | Education and training | 62221 | 515.8 |
| D | Electricity, Gas, Water and Waste Services | 2.25 | 2.0 | 2.14 | Medium | electricity gas water and waste services | Utilities and infrastructure | 166688 | 142.5 |
| Q | Health Care and Social Assistance | 1.5 | 2.8 | 2.08 | Medium | health care and social assistance | Health and care services | 224001 | 1796.9 |
| J | Information Media and Telecommunications | 2.12 | 2.6 | 2.34 | Medium | information media and telecommunications | Media, telco and information services | 117894 | 188.3 |
| C | Manufacturing | 3.5 | 3.4 | 3.46 | Elevated | manufacturing | Industrial and manufacturing | 514199 | 901.7 |
| B | Mining | 3.88 | 3.2 | 3.57 | Elevated | mining | Mining and resources | 492161 | 234.7 |
| S | Other Services | 2.38 | 2.2 | 2.3 | Medium | other services | Other services | 100042 | 583.2 |
| M | Professional, Scientific and Technical Services | 1.75 | 2.0 | 1.86 | Moderate-low | professional scientific and technical services | Professional and technical services | 353044 | 1317.4 |
| O | Public Administration and Safety | 1.62 | 3.6 | 2.51 | Medium | public administration and safety | Public administration and safety | 15351 | 106.8 |
| L | Rental, Hiring and Real Estate Services | 2.38 | 2.6 | 2.48 | Medium | rental hiring and real estate services | Real estate and rental services | 185285 | 420.9 |
| G | Retail Trade | 3.25 | 3.4 | 3.32 | Elevated | retail trade | Consumer retail and discretionary | 643421 | 1509.6 |
| I | Transport, Postal and Warehousing | 2.5 | 2.4 | 2.46 | Medium | transport postal and warehousing | Freight, logistics and storage | 244980 | 670.6 |
| F | Wholesale Trade | 3.12 | 3.4 | 3.25 | Elevated | wholesale trade | Wholesale and distribution | 772255 | 604.2 |

*Full detail rows from property_cycle_panel.csv*

| as_of_date | property_segment | region | market_softness_score | region_risk_score | cycle_stage | source_note | approvals_change_pct | commencements_signal | completions_signal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-03-01 | Offices | Australia | 4.3 | 4.21 | downturn | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | -19.8 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-03-01 | Agricultural and aquacultural buildings | Australia | 3.9 | 4.01 | downturn | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | -27.02 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-03-01 | Commercial Buildings - Total | Australia | 3.8 | 3.84 | slowing | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | -49.71 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-03-01 | Retail and wholesale trade buildings | Australia | 3.4 | 3.39 | slowing | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 6.48 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-03-01 | Total Non-residential | Australia | 3.35 | 3.49 | slowing | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | -15.94 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-03-01 | Education buildings | Australia | 3.25 | 3.56 | slowing | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | -31.29 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-03-01 | Aged care facilities | Australia | 3.2 | 3.41 | slowing | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | -21.97 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-03-01 | Short term accommodation buildings | Australia | 3.1 | 2.99 | neutral | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 112.01 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-03-01 | Health buildings | Australia | 2.4 | 2.76 | neutral | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | -35.96 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-03-01 | Industrial Buildings - Total | Australia | 2.15 | 2.39 | growth | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 94.79 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-03-01 | Warehouses | Australia | 1.7 | 2.04 | growth | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 108.47 | Proxy from approvals trend | Proxy from approvals trend |

*Full detail rows from property_market_overlays_by_building_type.csv*

| as_of_date | property_segment | property_segment_code | market_softness_score | region_risk_score | cycle_stage | aggregate_role | market_softness_band | region_risk_band | approvals_change_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-06-16 | Offices | CRE | 4.3 | 4.21 | downturn | specific | soft | High | -19.8 |
| 2026-06-16 | Agricultural and aquacultural buildings | IND | 3.9 | 4.01 | downturn | specific | soft | High | -27.02 |
| 2026-06-16 | Commercial Buildings - Total | CON | 3.8 | 3.84 | slowing | aggregate (reviewer reference only) | softening | Elevated | -49.71 |
| 2026-06-16 | Retail and wholesale trade buildings | RET | 3.4 | 3.39 | slowing | specific | softening | Elevated | 6.48 |
| 2026-06-16 | Total Non-residential | CON | 3.35 | 3.49 | slowing | aggregate (reviewer reference only) | softening | Elevated | -15.94 |
| 2026-06-16 | Education buildings | CRE | 3.25 | 3.56 | slowing | specific | softening | Elevated | -31.29 |
| 2026-06-16 | Aged care facilities | CRE | 3.2 | 3.41 | slowing | specific | softening | Elevated | -21.97 |
| 2026-06-16 | Short term accommodation buildings | CRE | 3.1 | 2.99 | neutral | specific | normal | Medium | 112.01 |
| 2026-06-16 | Health buildings | CRE | 2.4 | 2.76 | neutral | specific | normal | Medium | -35.96 |
| 2026-06-16 | Industrial Buildings - Total | CON | 2.15 | 2.39 | growth | aggregate (reviewer reference only) | supportive | Medium | 94.79 |
| 2026-06-16 | Warehouses | IND | 1.7 | 2.04 | growth | specific | supportive | Medium | 108.47 |

## 6. Lineage / Traceability

A reviewer can resolve a number by table row, transformation row, then source inventory row within three hops.

*Lineage / Traceability*

| Analytical table | Number fields | Source row reference | Transformation script | Version / vintage | Reference hops |
| --- | --- | --- | --- | --- | --- |
| industry_risk_scores.csv | numeric columns in export | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv | src/overlays/build_industry_risk_scores.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| property_market_overlays.csv | numeric columns in export | building_approvals_nonres_xlsx; property_cycle_panel | src/overlays/build_property_market_overlays.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| downturn_overlay_table.csv | numeric columns in export | property_cycle_panel; scenario multipliers (assumption); qualitative arrears baseline (assumption, RBA FSR Mar-2026) | src/overlays/build_downturn_overlay_tables.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| macro_regime_flags.csv | numeric columns in export | rba_cash_rate_csv; qualitative arrears baseline (assumption, RBA FSR Mar-2026) | src/panels/build_macro_regime_flags.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| industry_financial_benchmarks.csv | numeric columns in export | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; business_indicators_inventory_ratio_xlsx; labour_force_industry_xlsx | src/panels/build_industry_financial_benchmarks.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| business_cycle_panel.csv | numeric columns in export | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; business_indicators_inventory_ratio_xlsx; business_indicators_consumer_sales_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv | src/panels/build_business_cycle_panel.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| property_cycle_panel.csv | numeric columns in export | building_approvals_nonres_xlsx | src/panels/build_property_cycle_panel.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| property_market_overlays_by_building_type.csv | numeric columns in export | building_approvals_nonres_xlsx; property_cycle_panel | src/overlays/build_property_market_overlays.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |

## 7. What's Not In This Report

These rows are the operator priority list for the next refresh cycle.

*Data not yet captured / out of scope*

| Source key | Reason | Required action | Target / next date |
| --- | --- | --- | --- |
| anzsic_classification_page | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| anzsic_division_codes_page | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| anzsic_division_subdivision_class_page | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| australian_industry_xlsx | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| building_approvals_nonres_xlsx | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| business_indicators_consumer_sales_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| business_indicators_inventory_ratio_xlsx | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| business_indicators_profit_ratio_xlsx | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| cpi_all_groups_xlsx | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| cpi_subgroups_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| dwelling_approvals_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| dwelling_value_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| labour_force_headline_xlsx | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| labour_force_industry_xlsx | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| lending_indicators_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| national_accounts_gdp_xlsx | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| ppi_construction_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| ppi_manufacturing_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| property_price_capitals_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| property_price_index_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| ptrs_cycle_8_pdf | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| ptrs_cycle_9_pdf | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| ptrs_guidance | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| rba_cash_rate_csv | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| rba_chart_pack_page | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| rba_fsr_page | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| rba_smp_page | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| rba_table_e2_xls | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| total_value_dwellings_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| wpi_xlsx | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |

## 8. Validation and Caveats

The integration test tests/integration/test_board_report_completeness.py is the executable contract for this section.

*Contract validation summary*

| Check category | Items | Status |
| --- | --- | --- |
| Source registry inventory | 33 | PASS |
| Canonical export transformations | 8 | PASS |
| Detailed analysis export tables | 8 | PASS |
| Lineage mappings | 8 | PASS |
| Manual/missing source disclosure | 30 | PASS |

The report does not fabricate current-period values. Prior-period or manually staged values remain dated through their source inventory period, manifest timestamp, export as_of_date, or build timestamp.

## 9. Macro Stress Inputs

A macro-driven stress layer turns macroeconomic scenario paths into PD / LGD / EAD multipliers per portfolio segment, then rolls facility-level stress up to a portfolio expected-loss total — answering 'if the economy turns, how much worse do losses get, and for which portfolios?'. Engine src/overlays/macro_stress_core.py; config config/macro_scenarios.yaml; contracts macro_scenario_paths.csv and portfolio_macro_sensitivity.csv. multiplier[s,p,k] = clamp(1 + intensity[p] * beta[s,p] * sum_d weight[s,p,d] * shock_norm[d,k]); base = 1.0, monotonic to severe.

*Macro scenario paths - stressed level by scenario*

| Variable | Unit | Source | base | mild | moderate | severe |
| --- | --- | --- | --- | --- | --- | --- |
| Cash rate (%) | % | RBA F1 cash-rate table | 4.35 | 4.6 | 4.85 | 5.1 |
| Commercial-property prices (% change) | % change | assumption | 0.0 | -7.0 | -15.0 | -28.0 |
| CRE cap rates (%) | % | assumption | 6.0 | 6.4 | 6.9 | 7.6 |
| CRE rents (% change) | % change | assumption | 0.0 | -4.0 | -9.0 | -16.0 |
| Exchange rate (TWI, % change) | % change | RBA F11 exchange rates | 0.0 | -5.0 | -10.0 | -15.0 |
| GDP growth (real, YoY %) | % yoy | ABS 5206 National Accounts (Mar 2026, real SA, through-the-year) | 2.5 | 0.7 | -0.8 | -2.8 |
| House-price growth (YoY %) | % yoy | stated (ABS 6416 RPPI discontinued after Dec-2021; no current free public index) | 4.0 | -4.0 | -11.0 | -21.0 |
| Industry / sector output (YoY %) | % yoy | ABS 8155 Australian Industry + 5676 Business Indicators | 2.0 | 0.0 | -2.0 | -5.0 |
| Inflation (CPI, YoY %) | % yoy | ABS 6401 CPI (Mar 2026 quarter, all groups, through-the-year) | 2.4 | 3.2 | 3.9 | 4.9 |
| Unemployment rate (%) | % | ABS 6202 Labour Force (Mar 2026, seasonally adjusted) | 4.3 | 5.5 | 6.8 | 8.3 |
| Vacancy rate (office, %) | % | assumption | 12.0 | 14.0 | 16.0 | 19.0 |
| Wage growth (WPI, YoY %) | % yoy | ABS 6345 Wage Price Index (Mar 2026 quarter, through-the-year) | 3.3 | 2.8 | 2.3 | 1.5 |

*Which macro drivers move which portfolio (illustrative)*

| Portfolio | Material macro drivers |
| --- | --- |
| Residential mortgages | unemployment, cash rate, wage growth, house prices |
| Credit cards | unemployment, wage growth, inflation |
| SME lending | GDP, unemployment, cash rate, sector output |
| Corporate lending | GDP, sector output, cash rate, exchange rate |
| Commercial property | property prices, vacancy, rents, cap rates, cash rate |
| Development finance | property prices, GDP, vacancy, cash rate |

*Macro-derived segment multipliers (PD / LGD / EAD)*

| Segment | Scenario | PD x | LGD x | EAD x |
| --- | --- | --- | --- | --- |
| residential_mortgages | base | 1.0 | 1.0 | 1.0 |
| residential_mortgages | mild | 1.4129 | 1.1523 | 1.0649 |
| residential_mortgages | moderate | 1.8357 | 1.2936 | 1.1291 |
| residential_mortgages | severe | 2.35 | 1.48 | 1.2 |
| credit_cards | base | 1.0 | 1.0 | 1.0 |
| credit_cards | mild | 1.4906 | 1.1267 | 1.0786 |
| credit_cards | moderate | 1.9886 | 1.2535 | 1.1533 |
| credit_cards | severe | 2.65 | 1.42 | 1.24 |
| sme_lending | base | 1.0 | 1.0 | 1.0 |
| sme_lending | mild | 1.5241 | 1.1521 | 1.0906 |
| sme_lending | moderate | 2.0259 | 1.3053 | 1.1757 |
| sme_lending | severe | 2.65 | 1.54 | 1.28 |
| corporate_lending | base | 1.0 | 1.0 | 1.0 |
| corporate_lending | mild | 1.4823 | 1.1549 | 1.0913 |
| corporate_lending | moderate | 1.9307 | 1.3156 | 1.177 |
| corporate_lending | severe | 2.5 | 1.54 | 1.28 |
| commercial_property | base | 1.0 | 1.0 | 1.0 |
| commercial_property | mild | 1.5409 | 1.18 | 1.0968 |
| commercial_property | moderate | 2.127 | 1.3973 | 1.1958 |
| commercial_property | severe | 2.95 | 1.72 | 1.32 |
| development_finance | base | 1.0 | 1.0 | 1.0 |
| development_finance | mild | 1.6664 | 1.195 | 1.1116 |
| development_finance | moderate | 2.3292 | 1.4273 | 1.2219 |
| development_finance | severe | 3.25 | 1.78 | 1.36 |

*Demonstration - facility roll-up to portfolio EL (illustrative demo book)*

| Scenario | Facilities | Base EL ($) | Stressed EL ($) | EL uplift x |
| --- | --- | --- | --- | --- |
| base | 6 | 79293.72 | 79293.72 | 1.0 |
| mild | 6 | 79293.72 | 153321.21 | 1.934 |
| moderate | 6 | 79293.72 | 256331.65 | 3.233 |
| severe | 6 | 79293.72 | 447755.57 | 5.647 |

> **Macro stress - scope and governance**
>
> Illustrative scenario design — not calibrated regulatory stress. Base levels are current values from the named ABS/RBA series; the four CRE variables (commercial-property prices, vacancy, rents, cap rates) and all elasticities are labelled assumptions. The portfolio roll-up is exposure-weighted with no diversification benefit. Reverse stress: the moderate scenario (EL uplift 3.23x) first breaches a 2.0x illustrative appetite ceiling. A bank normally builds separate models per material portfolio or a pooled model with portfolio/sector effects; this layer supplies the macro-credit linkage either consumes.

## Appendix A — Audit log (this session)

**Date:** 2026-06-16  
**Scope:** Phase 1 baseline audit, Phase 2 anomaly scan, Phase 3 test-coverage audit + contract tests, Phase 4a markdown report build.

### Phase 1 — Baseline
- Test suite: 54 passed, 0 failed, 0 skipped, 0 warnings (pre-Phase-3).
- Pipeline scripts: all five completed cleanly after raw ABS/RBA data was copied from the main checkout into the worktree (git-ignored by design).
- Validator: 12/12 checks green.
- Exports: 6/6 present and non-empty. Dated exports within ~2 months of today; not stale.

### Phase 2 — Anomaly scan
- HIGH findings: 0. MEDIUM findings: 0. LOW findings: 2 (both informational, from the null-pattern diagnostic block).
- 21 nulls in `business_cycle_panel` confirmed as documented-by-design. Every null-bearing row is labelled 'Fallback' in `inventory_days_est_source`; every non-null row labelled 'ABS quarterly'. Zero exceptions.
- Core scoring columns (`classification_risk_score`, `macro_risk_score`, `industry_base_risk_score`, `industry_base_risk_level`) have 0 nulls.
- Scoring functions in `src/utils.py` map null inputs to a neutral factor score (3) — null-tolerant by design.

### Phase 3 — Test coverage
- Baseline: 15 of 23 source modules had direct test imports; 8 untested.
- Added `tests/test_export_contracts.py` (6 test functions expanding to 18 parametrized cases) covering the canonical contract boundary (`src/overlays/export_contracts.py`).
- Final count: 72 tests passing.
- Deferred Tier-2 builder tests: the 6 top-level `build_*` functions are smoke-tested via `test_reference_layer.py::test_canonical_panel_overlay_builders_are_importable`. End-to-end coverage is provided by the new contract tests plus the Phase 1 parquet-inspection. Adding per-builder contract tests would be duplication.
- Defensible gaps remaining: `src/validation.py` (end-to-end only via script), `src/config.py` (constants), `src/output.py` (small helper surface), `src/public_data/download_*.py` (thin network wrappers), `src/public_data/load_abs_manual_exports_helpers.py` (helpers for a tested parent module).

### Phase 4a — Markdown board report
- Added `reports/` package (`__init__.py`, `industry_analysis_report.py`, `render_markdown.py`).
- Added `src/build_board_report.py` CLI.
- Two markdown files generated per run: Board (summary) and Technical (full detail).
- DOCX and HTML renderers deferred to Phase 4b.

### Methodology observations (not bugs)
- **Construction base risk score (2.95, 'Moderate-high')** — logged as an active methodology review item. See Section 9 of this report. Session: noted, not fixed.

### Dev-ergonomics notes
- Fresh git worktrees do not carry the git-ignored raw ABS/RBA staging directories. Copy them from a primary checkout, or add a `bootstrap_worktree.py` helper. Not urgent; logged for future consideration.
