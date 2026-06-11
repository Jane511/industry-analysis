# Industry Analysis Report — Q1 2026

*Technical Detail variant. Generated 2026-06-11.*



Macro and downturn overlays as of 2026-03-16. Property cycle data as of 2026-02-01.

This is the full-detail variant for MRC, audit, and model-risk review. It includes per-row technical commentary, source URLs, the full Construction methodology review item, and the audit log as an appendix.



## 1. Executive Summary

This report contains source inventory, transformations, analytical output rows, lineage, known gaps, and validation status in the same document. It covers 18 industries, 5 property segments, all 37 registered public sources, and all 11 canonical exports. Source registry basis: PUBLIC_SOURCE_URLS plus scraper-produced RBA publication manifest keys; manifest-backed vintages come from data/raw/public/_manifest.json when present.

Headline picture: cash rate 3.85% (-0.25pp YoY), arrears Low / Improving, macro_regime_flag='base' (cash_rate_regime='neutral_easing'). 4 industries are Elevated; 0 property segments are in downturn; severe PD multiplier 2.00x.

Data freshness: macro/downturn overlays 2026-03-16; property-cycle 2026-02-01; generated 2026-06-11.

## 2. Headline Numbers

Each headline includes a trace pointer to the export or source chain that produced it.

*Headline calibrated outputs*

| Metric | Value | Vintage | Trace |
| --- | --- | --- | --- |
| Industries covered | 18 | 2026-03-16 | industry_risk_scores.csv |
| Property segments covered | 5 | 2026-02-01 | property_market_overlays.csv |
| Cash rate latest pct | 3.85 | 2026-03-16 | rba_cash_rate_csv -> macro_regime_flags.csv |
| Cash rate 1y change pctpts | -0.25 | 2026-03-16 | rba_cash_rate_csv -> industry_risk_scores.csv |
| Elevated industry count | 4 | 2026-03-16 | industry_risk_scores.csv |
| Downturn property segment count | 0 | 2026-02-01 | property_market_overlays.csv |
| Macro regime flag | base | 2026-03-16 | macro_regime_flags.csv |
| Severe PD multiplier | 2.00 | 2026-03-16 | downturn_overlay_table.csv |

*Industry risk scores - full current output*

| as_of_date | anzsic_division_code | industry | classification_risk_score | macro_risk_score | industry_base_risk_score | industry_base_risk_level | pd_multiplier | cash_rate_latest_pct | cash_rate_change_1y_pctpts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-04-29 | A | Agriculture, Forestry and Fishing | 4.12 | 3.2 | 3.71 | Elevated | 1.15 | 3.85 | -0.25 |
| 2026-04-29 | B | Mining | 3.88 | 2.8 | 3.39 | Elevated | 1.15 | 3.85 | -0.25 |
| 2026-04-29 | C | Manufacturing | 3.5 | 3.2 | 3.36 | Elevated | 1.15 | 3.85 | -0.25 |
| 2026-04-29 | G | Retail Trade | 3.25 | 3.2 | 3.23 | Elevated | 1.15 | 3.85 | -0.25 |
| 2026-04-29 | F | Wholesale Trade | 3.12 | 3.2 | 3.16 | Moderate-high | 1.1 | 3.85 | -0.25 |
| 2026-04-29 | R | Arts and Recreation Services | 2.38 | 3.8 | 3.02 | Moderate-high | 1.1 | 3.85 | -0.25 |
| 2026-04-29 | H | Accommodation and Food Services | 2.75 | 2.6 | 2.68 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | E | Construction | 2.75 | 2.6 | 2.68 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | I | Transport, Postal and Warehousing | 2.5 | 2.8 | 2.64 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | J | Information Media and Telecommunications | 2.12 | 3.0 | 2.52 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | O | Public Administration and Safety | 1.62 | 3.6 | 2.51 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | P | Education and Training | 1.75 | 3.4 | 2.49 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | L | Rental, Hiring and Real Estate Services | 2.38 | 2.6 | 2.48 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | N | Administrative and Support Services | 2.12 | 2.8 | 2.43 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | S | Other Services | 2.38 | 2.2 | 2.3 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | D | Electricity, Gas, Water and Waste Services | 2.25 | 2.0 | 2.14 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | Q | Health Care and Social Assistance | 1.5 | 2.8 | 2.08 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | M | Professional, Scientific and Technical Services | 1.75 | 2.4 | 2.04 | Medium | 1.0 | 3.85 | -0.25 |

*Downturn multipliers - full current output*

| scenario | pd_multiplier | lgd_multiplier | ccf_multiplier | property_value_haircut | notes | as_of_date |
| --- | --- | --- | --- | --- | --- | --- |
| base | 1.0 | 1.0 | 1.0 | 0.0 | Current staged environment. Anchored to a low / improving arrears backdrop and an average property-cycle softness score of 2.73. | 2026-03-16 |
| mild | 1.2 | 1.1 | 1.05 | 0.05 | Illustrative mild downturn overlay for conservative portfolio calibration. | 2026-03-16 |
| moderate | 1.5 | 1.2 | 1.1 | 0.1 | Illustrative moderate downturn overlay for stressed pricing and EL scenario analysis. | 2026-03-16 |
| severe | 2.0 | 1.3 | 1.2 | 0.2 | Illustrative severe downturn overlay. Not a calibrated regulatory stress parameter. | 2026-03-16 |

## 3. Data Sources Inventory

Canonical registry for this project: src.config.PUBLIC_SOURCE_URLS plus scraper-produced RBA publication manifest keys.

*Data Sources Inventory*

| Source key | Publisher / origin | URL or landing page | File type | Period or vintage | Retrieved / fetched timestamp | File size or row count | Status | Hash / version identifier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| anzsic_classification_page | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/latest-release | landing page |  |  |  | missing |  |
| anzsic_division_codes_page | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/2006-revision-2-0/numbering-system-and-titles/division-codes-and-titles | landing page |  |  |  | missing |  |
| anzsic_division_subdivision_class_page | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-anzsic/2006-revision-2-0/numbering-system-and-titles/division-subdivision-group-and-class-codes-and-titles | landing page |  |  |  | missing |  |
| australian_industry_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/industry/industry-overview/australian-industry/2023-24/81550DO001_202324.xlsx | XLSX |  | 2026-04-04T00:14:08+00:00 | 597090 | manually staged |  |
| building_approvals_nonres_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/feb-2026/87310051.xlsx | XLSX |  | 2026-04-04T00:14:08+00:00 | 185814 | manually staged |  |
| business_indicators_consumer_sales_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/dec-2025/56760024.xlsx | XLSX |  |  |  | missing |  |
| business_indicators_inventory_ratio_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/dec-2025/56760023.xlsx | XLSX |  | 2026-04-04T00:14:08+00:00 | 51783 | manually staged |  |
| business_indicators_profit_ratio_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia/dec-2025/56760022.xlsx | XLSX |  | 2026-04-04T00:14:08+00:00 | 56253 | manually staged |  |
| cotality_auction_clearance_page | Cotality | https://www.cotality.com/au/our-data/auction-results | landing page |  |  |  | manually staged |  |
| cotality_hvi_page | Cotality | https://www.cotality.com/au/news-research/insights/home-value-index/ | landing page |  |  |  | manually staged |  |
| cpi_all_groups_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/dec-2025/640101.xlsx | XLSX |  |  |  | missing |  |
| cpi_subgroups_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/dec-2025/640107.xlsx | XLSX |  |  |  | missing |  |
| domain_quarterly_page | Domain | https://www.domain.com.au/research/house-price-report/ | landing page |  |  |  | manually staged |  |
| dwelling_approvals_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/feb-2026/875206.xlsx | XLSX |  |  |  | missing |  |
| dwelling_value_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia/feb-2026/875211.xlsx | XLSX |  |  |  | missing |  |
| labour_force_industry_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia-detailed/feb-2026/6291004.xlsx | XLSX |  | 2026-04-04T00:14:08+00:00 | 160939 | manually staged |  |
| lending_indicators_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/finance/lending-indicators/feb-2026/560101.xlsx | XLSX |  |  |  | missing |  |
| nsw_rental_bonds_page | State rental bond authorities | https://www.fairtrading.nsw.gov.au/ | AU |  |  |  | manually staged |  |
| ppi_construction_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/producer-price-indexes-australia/dec-2025/642713.xlsx | XLSX |  |  |  | missing |  |
| ppi_manufacturing_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/producer-price-indexes-australia/dec-2025/642712.xlsx | XLSX |  |  |  | missing |  |
| property_price_capitals_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities/dec-2025/641602.xlsx | XLSX |  |  |  | missing |  |
| property_price_index_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/residential-property-price-indexes-eight-capital-cities/dec-2025/641601.xlsx | XLSX |  |  |  | missing |  |
| ptrs_cycle_8_pdf | Payment Times Reporting Scheme | https://paymenttimes.gov.au/sites/ptrs.gov.au/files/2025-07/reg-update-july-2025.pdf | PDF |  | 2026-04-07T01:41:27+00:00 | 2055606 | manually staged |  |
| ptrs_cycle_9_pdf | Payment Times Reporting Scheme | https://paymenttimes.gov.au/sites/ptrs.gov.au/files/2026-01/regulators-update-202601.pdf | PDF |  | 2026-04-07T01:41:27+00:00 | 3629142 | manually staged |  |
| ptrs_guidance | Payment Times Reporting Scheme | https://paymenttimes.gov.au/sites/ptrs.gov.au/files/regulatory-resource/ptrs-guidance-materials-march2025.pdf | PDF |  | 2026-04-07T01:41:27+00:00 | 947450 | manually staged |  |
| qld_median_rents_page | Public source | https://www.rta.qld.gov.au/about-the-rta/research-and-reports/median-rents-quarterly-data | landing page |  |  |  | missing |  |
| rba_cash_rate_csv | Reserve Bank of Australia | https://www.rba.gov.au/statistics/tables/csv/f1-data.csv | CSV |  | 2026-04-04T00:14:08+00:00 | 298051 | manually staged |  |
| rba_chart_pack_page | Reserve Bank of Australia | https://www.rba.gov.au/chart-pack/ | landing page |  |  |  | missing |  |
| rba_chart_pack_pdf | Reserve Bank of Australia | https://www.rba.gov.au/chart-pack/ | PDF | March 2026 | 2026-04-28T08:01:43+00:00 | 5434746 | auto-downloaded | 66945f0e420217b86069e72880c20b4670f17a2ff52e6e0de9c9d13a174364d9 |
| rba_fsr_page | Reserve Bank of Australia | https://www.rba.gov.au/publications/fsr/ | landing page |  |  |  | missing |  |
| rba_fsr_pdf | Reserve Bank of Australia | https://www.rba.gov.au/publications/fsr/ | PDF | March 2026 | 2026-04-28T08:01:42+00:00 | 3272062 | auto-downloaded | 342ec105f1c623e507ef4e8434ade6f0788ef58ed26b2accaa8ec7df04acc13e |
| rba_smp_page | Reserve Bank of Australia | https://www.rba.gov.au/publications/smp/ | landing page |  |  |  | missing |  |
| rba_smp_pdf | Reserve Bank of Australia | https://www.rba.gov.au/publications/smp/ | PDF | February 2026 | 2026-04-28T08:01:42+00:00 | 4201271 | auto-downloaded | db42f94329b6c229844fb8da8cbc4308d707af57b3d5ba90d0aaa9bd7e21ca89 |
| rba_table_e2_xls | Reserve Bank of Australia | https://www.rba.gov.au/statistics/tables/xls/e02hist.xls | XLS |  |  |  | missing |  |
| sqm_headline_page | SQM Research | https://sqmresearch.com.au/ | AU |  |  |  | manually staged |  |
| total_value_dwellings_xlsx | Australian Bureau of Statistics | https://www.abs.gov.au/statistics/economy/finance/total-value-dwellings/dec-2025/643201.xlsx | XLSX |  |  |  | missing |  |
| vic_rental_report_page | State rental bond authorities | https://www.dffh.vic.gov.au/publications/rental-report | landing page |  |  |  | manually staged |  |

## 4. Transformations Applied

Validation status is derived from export presence and non-empty row count; schema-level tests remain in the pytest suite.

*Transformations Applied*

| Output filename | Input source(s) | Transformation script | Row count of output | Last build timestamp | Validation status |
| --- | --- | --- | --- | --- | --- |
| industry_risk_scores.csv | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv | src/overlays/build_industry_risk_scores.py | 18 | 2026-04-29T10:00:55 | PASS: present_nonempty |
| property_market_overlays.csv | building_approvals_nonres_xlsx; property_market_detail; property_cycle_panel | src/overlays/build_property_market_overlays.py | 5 | 2026-04-29T10:00:55 | PASS: present_nonempty |
| downturn_overlay_table.csv | property_cycle_panel; rba_fsr_page; staged arrears context | src/overlays/build_downturn_overlay_tables.py | 4 | 2026-04-29T10:00:55 | PASS: present_nonempty |
| macro_regime_flags.csv | rba_cash_rate_csv; staged arrears context | src/panels/build_macro_regime_flags.py | 1 | 2026-04-29T10:00:55 | PASS: present_nonempty |
| industry_failure_rates.csv | asic insolvency public extracts; ABS active-business counts | src/panels/build_industry_failure_rates.py | 18 | 2026-04-29T10:00:55 | PASS: present_nonempty |
| industry_financial_benchmarks.csv | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; business_indicators_inventory_ratio_xlsx; labour_force_industry_xlsx | src/panels/build_industry_financial_benchmarks.py | 18 | 2026-04-29T10:00:55 | PASS: present_nonempty |
| business_cycle_panel.csv | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; business_indicators_inventory_ratio_xlsx; business_indicators_consumer_sales_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv | src/panels/build_business_cycle_panel.py | 18 | 2026-04-29T10:00:55 | PASS: present_nonempty |
| property_cycle_panel.csv | building_approvals_nonres_xlsx; property reference staged sources | src/panels/build_property_cycle_panel.py | 11 | 2026-04-29T10:00:55 | PASS: present_nonempty |
| macro_context.csv | cpi_all_groups_xlsx; cpi_subgroups_xlsx; ppi_manufacturing_xlsx; ppi_construction_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv; rba_fsr_page | src/panels/build_macro_context_panel.py | 8 | 2026-04-29T10:00:55 | PASS: present_nonempty |
| property_market_detail.csv | property_price_index_xlsx; property_price_capitals_xlsx; total_value_dwellings_xlsx; lending_indicators_xlsx; rba_table_e2_xls; cotality_hvi_page; domain_quarterly_page; sqm_headline_page; state rental bond pages | src/panels/build_property_reference_panel.py | 68 | 2026-04-29T10:00:55 | PASS: present_nonempty |
| property_market_overlays_by_building_type.csv | building_approvals_nonres_xlsx; property_cycle_panel | src/overlays/build_property_market_overlays.py | 11 | 2026-04-29T10:00:55 | PASS: present_nonempty |

## 5. Detailed Analysis

Wide exports are column-compacted for readability but keep every source row in the report table.

*Canonical CSV exports: contents and downstream layers*

| CSV export | Contract role | Join grain | What it includes | Downstream layers |
| --- | --- | --- | --- | --- |
| industry_risk_scores.csv | Core downstream contract | Industry snapshot | Compact industry overlay: classification score, macro score, base risk score/level, and shared cash-rate backdrop fields. | PD overlays / scorecards; EL and pricing overlays; External sector benchmarks; Board reporting |
| property_market_overlays.csv | Core downstream contract | Property segment snapshot | Compact property overlay: cycle stage, softness score/band, region risk, approvals change, and approvals-proxy activity signals. | LGD and collateral overlays; Property-backed PD context; Pricing and policy overlays; Board reporting |
| downturn_overlay_table.csv | Core downstream contract | Scenario table | Scenario multipliers for PD, LGD, and CCF plus property haircuts and scenario notes. | PD scenario layer; LGD scenario layer; CCF / EAD scenario layer; Stress testing and pricing what-if views |
| macro_regime_flags.csv | Core downstream contract | Single as-of-date regime row | Environment selector: cash-rate regime, arrears level/trend, macro regime flag, and source dataset. | PD regime conditioning; LGD / EL regime conditioning; Scenario-row selection; Portfolio and board reporting |
| industry_failure_rates.csv | Core downstream contract | ANZSIC-division snapshot | Realised insolvency counts (ASIC Series 1A) divided by ABS active-business counts per ANZSIC division, plus YoY change in the rate. | PD backtest and validation; ECL current-state anchoring; Governance concentration reporting; External sector benchmarks |
| industry_financial_benchmarks.csv | Core downstream contract | ANZSIC-division snapshot | Per-ANZSIC-division medians of the financial ratios APG 220 paragraph 64 calls out as standard credit-assessment benchmarks: EBITDA margin, gross operating profit-to-sales, wages-to-sales, inventory days, sales growth, employment growth, inventory-to-sales, and sales per employee. | Origination scorecard industry-relative ratios; PD model industry-comparison features; ECL borrower-vs-industry signals; External sector benchmarks |
| business_cycle_panel.csv | Optional explainability panel | Industry diagnostics panel | Wide industry diagnostics: structural factors, public benchmark metrics, macro factor scores, demand proxies, inventory flags, and explainability fields behind the industry overlay. | PD explainability; External benchmark diagnostics; Challenger overlay analysis; Technical report detail |
| property_cycle_panel.csv | Optional explainability panel | Property segment-by-region diagnostics | Wide property diagnostics: approvals trend, cycle stage, softness band, region risk, as-of-date, and per-row source/proxy notes. | LGD explainability; Collateral benchmark diagnostics; Property stress interpretation; Technical report detail |
| macro_context.csv | Core downstream contract | Quarter snapshot (national) | Macro context per quarter — CPI all-groups + housing/food/transport subgroup YoY/QoQ change, PPI manufacturing & construction YoY, headline labour proxy, RBA cash rate, RBA FSR aggregates (household debt ratio, national arrears rate). | PD macro context features; Scenario / stress testing macro overlay; Board reporting headline cycle commentary; External macro benchmarks |
| property_market_detail.csv | Core downstream contract | (region_id, property_type, as_of_date) | Multi-source free property panel — capital city + suburb rows. ABS Cat. 6416.0 / 6432.0 / 5601.0, Cotality HVI + auction clearance, Domain Quarterly capitals + top suburbs, SQM headline, RBA Table E2, and 8-state rental bond medians, with a data_completeness_pct flag and a contributing_sources column on every row. | Property-backed PD context (richer than 5-row overlay); LGD collateral-region sensitivity; Scenario builder property inputs; Board reporting property deep-dives |
| property_market_overlays_by_building_type.csv | Optional explainability panel | Per-building-type non-residential detail | One row per ABS non-residential building-approval category — the pre-aggregation input to the five-row property_market_overlays contract. Shows each category's softness, region risk, approvals change, and the property_segment_code it rolls up into. | Property overlay explainability; Reviewer drilldown into CRE / IND / RET / CON aggregation; Technical report detail |

*Full detail rows from industry_risk_scores.csv*

| as_of_date | anzsic_division_code | industry | classification_risk_score | macro_risk_score | industry_base_risk_score | industry_base_risk_level | pd_multiplier | cash_rate_latest_pct | cash_rate_change_1y_pctpts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-04-29 | A | Agriculture, Forestry and Fishing | 4.12 | 3.2 | 3.71 | Elevated | 1.15 | 3.85 | -0.25 |
| 2026-04-29 | B | Mining | 3.88 | 2.8 | 3.39 | Elevated | 1.15 | 3.85 | -0.25 |
| 2026-04-29 | C | Manufacturing | 3.5 | 3.2 | 3.36 | Elevated | 1.15 | 3.85 | -0.25 |
| 2026-04-29 | G | Retail Trade | 3.25 | 3.2 | 3.23 | Elevated | 1.15 | 3.85 | -0.25 |
| 2026-04-29 | F | Wholesale Trade | 3.12 | 3.2 | 3.16 | Moderate-high | 1.1 | 3.85 | -0.25 |
| 2026-04-29 | R | Arts and Recreation Services | 2.38 | 3.8 | 3.02 | Moderate-high | 1.1 | 3.85 | -0.25 |
| 2026-04-29 | H | Accommodation and Food Services | 2.75 | 2.6 | 2.68 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | E | Construction | 2.75 | 2.6 | 2.68 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | I | Transport, Postal and Warehousing | 2.5 | 2.8 | 2.64 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | J | Information Media and Telecommunications | 2.12 | 3.0 | 2.52 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | O | Public Administration and Safety | 1.62 | 3.6 | 2.51 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | P | Education and Training | 1.75 | 3.4 | 2.49 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | L | Rental, Hiring and Real Estate Services | 2.38 | 2.6 | 2.48 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | N | Administrative and Support Services | 2.12 | 2.8 | 2.43 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | S | Other Services | 2.38 | 2.2 | 2.3 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | D | Electricity, Gas, Water and Waste Services | 2.25 | 2.0 | 2.14 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | Q | Health Care and Social Assistance | 1.5 | 2.8 | 2.08 | Medium | 1.0 | 3.85 | -0.25 |
| 2026-04-29 | M | Professional, Scientific and Technical Services | 1.75 | 2.4 | 2.04 | Medium | 1.0 | 3.85 | -0.25 |

*Full detail rows from property_market_overlays.csv*

| as_of_date | property_segment | property_segment_code | pd_multiplier | market_softness_score | region_risk_score | cycle_stage | source_note | market_softness_band | market_softness_level |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-04-29 | Residential | RES | 1.0 | 2.5 | 2.69 | neutral | Residential placeholder — ABS Cat. 8752.0 residential dwelling-approvals file not yet staged; RES row uses a neutral composite pending that upgrade. | normal | Medium |
| 2026-04-29 | Commercial (office, health, education, accommodation) | CRE | 1.1 | 3.06 | 3.03 | slowing | Aggregated from ABS Cat. 8731.0 non-residential building approvals. Exposure-weighted (12-month mean approval $ per building type). Constituent ABS categories: Aged care facilities, Education buildings, Health buildings, Offices, Short term accommodation buildings | softening | Moderate-high |
| 2026-04-29 | Industrial / Warehouse | IND | 1.0 | 2.23 | 2.37 | neutral | Aggregated from ABS Cat. 8731.0 non-residential building approvals. Exposure-weighted (12-month mean approval $ per building type). Constituent ABS categories: Agricultural and aquacultural buildings, Warehouses | normal | Medium |
| 2026-04-29 | Retail Property | RET | 1.1 | 3.15 | 2.95 | slowing | Aggregated from ABS Cat. 8731.0 non-residential building approvals. Exposure-weighted (12-month mean approval $ per building type). Constituent ABS categories: Retail and wholesale trade buildings | softening | Moderate-high |
| 2026-04-29 | Construction (non-residential development) | CON | 1.1 | 2.92 | 2.9 | slowing | Aggregated from ABS Cat. 8731.0 non-residential building approvals. Exposure-weighted (12-month mean approval $ per building type). Constituent ABS categories: Aged care facilities, Agricultural and aquacultural buildings, Education buildings, Health buildings, Offices, Retail and wholesale trade buildings, Short term accommodation buildings, Warehouses | softening | Moderate-high |

*Full detail rows from downturn_overlay_table.csv*

| as_of_date | scenario | pd_multiplier | lgd_multiplier | ccf_multiplier | property_value_haircut | notes |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-03-16 | base | 1.0 | 1.0 | 1.0 | 0.0 | Current staged environment. Anchored to a low / improving arrears backdrop and an average property-cycle softness score of 2.73. |
| 2026-03-16 | mild | 1.2 | 1.1 | 1.05 | 0.05 | Illustrative mild downturn overlay for conservative portfolio calibration. |
| 2026-03-16 | moderate | 1.5 | 1.2 | 1.1 | 0.1 | Illustrative moderate downturn overlay for stressed pricing and EL scenario analysis. |
| 2026-03-16 | severe | 2.0 | 1.3 | 1.2 | 0.2 | Illustrative severe downturn overlay. Not a calibrated regulatory stress parameter. |

*Full detail rows from macro_regime_flags.csv*

| as_of_date | cash_rate_regime | arrears_environment_level | arrears_trend | macro_regime_flag | source_dataset |
| --- | --- | --- | --- | --- | --- |
| 2026-03-16 | neutral_easing | Low | Improving | base | RBA F1 cash-rate table + staged arrears context |

*Full detail rows from industry_failure_rates.csv*

| as_of_date | anzsic_division_code | industry | failure_rate_pct | source_note | insolvency_count_ttm | active_businesses | failure_rate_yoy_change_pctpts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-04-29 | A | Agriculture Forestry And Fishing | 0.177 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 203 | 115000 | 0.02 |
| 2026-04-29 | B | Mining | 1.059 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 108 | 10200 | 0.157 |
| 2026-04-29 | C | Manufacturing | 0.891 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 731 | 82000 | 0.141 |
| 2026-04-29 | D | Electricity Gas Water And Waste Services | 1.0 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 65 | 6500 | 0.169 |
| 2026-04-29 | E | Construction | 0.969 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 4166 | 430000 | 0.162 |
| 2026-04-29 | F | Wholesale Trade | 0.753 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 452 | 60000 | 0.123 |
| 2026-04-29 | G | Retail Trade | 0.841 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 1009 | 120000 | 0.123 |
| 2026-04-29 | H | Accommodation And Food Services | 1.96 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 1862 | 95000 | 0.341 |
| 2026-04-29 | I | Transport Postal And Warehousing | 0.556 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 528 | 95000 | 0.089 |
| 2026-04-29 | J | Information Media And Telecommunications | 1.136 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 284 | 25000 | 0.196 |
| 2026-04-29 | L | Rental Hiring And Real Estate Services | 0.173 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 451 | 260000 | 0.033 |
| 2026-04-29 | M | Professional Scientific And Technical Services | 0.242 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 921 | 380000 | 0.037 |
| 2026-04-29 | N | Administrative And Support Services | 0.339 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 407 | 120000 | 0.059 |
| 2026-04-29 | O | Public Administration And Safety | 0.733 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 22 | 3000 | 0.2 |
| 2026-04-29 | P | Education And Training | 0.584 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 146 | 25000 | 0.136 |
| 2026-04-29 | Q | Health Care And Social Assistance | 0.3 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 465 | 155000 | 0.05 |
| 2026-04-29 | R | Arts And Recreation Services | 1.14 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 342 | 30000 | 0.203 |
| 2026-04-29 | S | Other Services | 1.525 | SYNTHETIC DEVELOPMENT STUB — Synthetic stub reflecting ASIC Series 1A FY23-FY25 approximate proportions | Fallback active-business counts derived from ABS Cat. 8165.0 summary release (June 2024) plus ABS 81550DO001 cross-checks. Replace with a live 8165.0 extract in data/raw/public/abs/ when available. | 1525 | 100000 | 0.242 |

*Full detail rows from industry_financial_benchmarks.csv*

| as_of_date | anzsic_division_code | industry | median_ebitda_margin_pct | source_note | median_gross_operating_profit_to_sales_ratio | median_wages_to_sales_pct | median_inventory_days_est | median_sales_growth_pct | median_employment_yoy_growth_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-04-29 | A | Agriculture, Forestry and Fishing | 14.58 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. |  | 9.75 | 31.7 | -11.05 | -5.11 |
| 2026-04-29 | B | Mining | 47.33 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.48 | 7.8 | 43.9 | -6.26 | -5.09 |
| 2026-04-29 | C | Manufacturing | 9.15 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.1 | 14.3 | 52.7 | 1.34 | -0.93 |
| 2026-04-29 | D | Electricity, Gas, Water and Waste Services | 20.95 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.2 | 9.93 | 9.1 | 3.6 | 12.29 |
| 2026-04-29 | E | Construction | 10.15 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.08 | 15.04 | 20.0 | 10.54 | 1.47 |
| 2026-04-29 | F | Wholesale Trade | 6.12 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.07 | 6.77 | 46.1 | 2.54 | -8.74 |
| 2026-04-29 | G | Retail Trade | 7.8 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.07 | 10.28 | 30.4 | 4.82 | -0.46 |
| 2026-04-29 | H | Accommodation and Food Services | 11.38 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.1 | 25.54 | 6.1 | 8.6 | 0.72 |
| 2026-04-29 | I | Transport, Postal and Warehousing | 17.72 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.21 | 19.69 | 25.4 | 3.46 | 2.79 |
| 2026-04-29 | J | Information Media and Telecommunications | 20.02 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.19 | 20.01 | 8.0 | 5.95 | -4.77 |
| 2026-04-29 | L | Rental, Hiring and Real Estate Services | 40.88 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.37 | 13.0 | 8.0 | 7.72 | -15.06 |
| 2026-04-29 | M | Professional, Scientific and Technical Services | 12.99 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.13 | 35.33 | 6.0 | 8.68 | 5.5 |
| 2026-04-29 | N | Administrative and Support Services | 9.27 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.07 | 47.45 | 8.0 | 6.17 | 3.07 |
| 2026-04-29 | O | Public Administration and Safety | 9.6 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. |  | 42.36 | 8.0 | 11.69 | -1.17 |
| 2026-04-29 | P | Education and Training | 11.73 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. |  | 50.88 | 10.7 | 10.67 | 5.63 |
| 2026-04-29 | Q | Health Care and Social Assistance | 16.65 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. |  | 43.29 | 6.0 | 7.54 | 3.74 |
| 2026-04-29 | R | Arts and Recreation Services | 13.45 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.12 | 22.55 | 15.0 | 6.38 | -5.79 |
| 2026-04-29 | S | Other Services | 5.28 | Derived from ABS Cat. 8155.0 Australian Industry, Cat. 5676.0 Business Indicators, Cat. 6291.0 Labour Force Detailed. Percentiles (p25/p75) not published in this version — internal portfolio data required for firm-level distribution. Sub-sector (subdivision/group) granularity not published in this version — division-level only. | 0.14 | 31.62 | 10.0 | 13.2 | 7.12 |

*Full detail rows from business_cycle_panel.csv*

| anzsic_division_code | industry | classification_risk_score | macro_risk_score | industry_base_risk_score | industry_base_risk_level | sector_key | internal_grouping_example | sales_m_latest | employment_000_latest |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H | Accommodation and Food Services | 2.75 | 2.6 | 2.68 | Medium | accommodation and food services | Hospitality and leisure | 152965 | 1217.9 |
| N | Administrative and Support Services | 2.12 | 2.8 | 2.43 | Medium | administrative and support services | Administrative and support services | 144266 | 1006.4 |
| A | Agriculture, Forestry and Fishing | 4.12 | 3.2 | 3.71 | Elevated | agriculture forestry and fishing | Primary production and agribusiness | 119772 | 411.0 |
| R | Arts and Recreation Services | 2.38 | 3.8 | 3.02 | Moderate-high | arts and recreation services | Arts and recreation services | 49985 | 277.3 |
| E | Construction | 2.75 | 2.6 | 2.68 | Medium | construction | Building, civil and trade services | 624590 | 1290.7 |
| P | Education and Training | 1.75 | 3.4 | 2.49 | Medium | education and training | Education and training | 62221 | 515.8 |
| D | Electricity, Gas, Water and Waste Services | 2.25 | 2.0 | 2.14 | Medium | electricity gas water and waste services | Utilities and infrastructure | 166688 | 142.5 |
| Q | Health Care and Social Assistance | 1.5 | 2.8 | 2.08 | Medium | health care and social assistance | Health and care services | 224001 | 1796.9 |
| J | Information Media and Telecommunications | 2.12 | 3.0 | 2.52 | Medium | information media and telecommunications | Media, telco and information services | 117894 | 188.3 |
| C | Manufacturing | 3.5 | 3.2 | 3.36 | Elevated | manufacturing | Industrial and manufacturing | 514199 | 901.7 |
| B | Mining | 3.88 | 2.8 | 3.39 | Elevated | mining | Mining and resources | 492161 | 234.7 |
| S | Other Services | 2.38 | 2.2 | 2.3 | Medium | other services | Other services | 100042 | 583.2 |
| M | Professional, Scientific and Technical Services | 1.75 | 2.4 | 2.04 | Medium | professional scientific and technical services | Professional and technical services | 353044 | 1317.4 |
| O | Public Administration and Safety | 1.62 | 3.6 | 2.51 | Medium | public administration and safety | Public administration and safety | 15351 | 106.8 |
| L | Rental, Hiring and Real Estate Services | 2.38 | 2.6 | 2.48 | Medium | rental hiring and real estate services | Real estate and rental services | 185285 | 420.9 |
| G | Retail Trade | 3.25 | 3.2 | 3.23 | Elevated | retail trade | Consumer retail and discretionary | 643421 | 1509.6 |
| I | Transport, Postal and Warehousing | 2.5 | 2.8 | 2.64 | Medium | transport postal and warehousing | Freight, logistics and storage | 244980 | 670.6 |
| F | Wholesale Trade | 3.12 | 3.2 | 3.16 | Moderate-high | wholesale trade | Wholesale and distribution | 772255 | 604.2 |

*Full detail rows from property_cycle_panel.csv*

| as_of_date | property_segment | region | market_softness_score | region_risk_score | cycle_stage | source_note | approvals_change_pct | commencements_signal | completions_signal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-02-01 | Offices | Australia | 4.3 | 4.03 | downturn | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | -35.72 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-02-01 | Education buildings | Australia | 3.25 | 3.38 | slowing | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | -21.37 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-02-01 | Retail and wholesale trade buildings | Australia | 3.15 | 2.95 | neutral | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 68.47 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-02-01 | Short term accommodation buildings | Australia | 2.85 | 2.55 | growth | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 113.7 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-02-01 | Aged care facilities | Australia | 2.7 | 2.73 | neutral | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 219.88 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-02-01 | Agricultural and aquacultural buildings | Australia | 2.65 | 2.58 | neutral | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 58.37 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-02-01 | Total Non-residential | Australia | 2.6 | 2.55 | neutral | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 71.46 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-02-01 | Industrial Buildings - Total | Australia | 2.4 | 2.45 | neutral | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 55.53 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-02-01 | Commercial Buildings - Total | Australia | 2.3 | 2.15 | growth | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 165.42 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-02-01 | Warehouses | Australia | 2.2 | 2.35 | neutral | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 69.32 | Proxy from approvals trend | Proxy from approvals trend |
| 2026-02-01 | Health buildings | Australia | 1.65 | 1.82 | growth | ABS Building Approvals - Non-residential; building activity not staged; commencements and completions proxied from approvals trend | 355.03 | Proxy from approvals trend | Proxy from approvals trend |

*Full detail rows from macro_context.csv*

| as_of_date | period_label | cash_rate_pct | source_note | cpi_yoy_pct | cpi_qoq_pct | cpi_housing_yoy_pct | cpi_food_yoy_pct | cpi_transport_yoy_pct | ppi_manufacturing_yoy_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2024-06-30 | 2024Q2 | 3.85 | Skeleton panel — ABS Cat. 6401.0 / 6427.0 / 6202.0 not staged. Populated columns: RBA F1 cash rate; RBA FSR |  |  |  |  |  |  |
| 2024-09-30 | 2024Q3 | 3.85 | Skeleton panel — ABS Cat. 6401.0 / 6427.0 / 6202.0 not staged. Populated columns: RBA F1 cash rate; RBA FSR |  |  |  |  |  |  |
| 2024-12-31 | 2024Q4 | 3.85 | Skeleton panel — ABS Cat. 6401.0 / 6427.0 / 6202.0 not staged. Populated columns: RBA F1 cash rate; RBA FSR |  |  |  |  |  |  |
| 2025-03-31 | 2025Q1 | 3.85 | Skeleton panel — ABS Cat. 6401.0 / 6427.0 / 6202.0 not staged. Populated columns: RBA F1 cash rate; RBA FSR |  |  |  |  |  |  |
| 2025-06-30 | 2025Q2 | 3.85 | Skeleton panel — ABS Cat. 6401.0 / 6427.0 / 6202.0 not staged. Populated columns: RBA F1 cash rate; RBA FSR |  |  |  |  |  |  |
| 2025-09-30 | 2025Q3 | 3.85 | Skeleton panel — ABS Cat. 6401.0 / 6427.0 / 6202.0 not staged. Populated columns: RBA F1 cash rate; RBA FSR |  |  |  |  |  |  |
| 2025-12-31 | 2025Q4 | 3.85 | Skeleton panel — ABS Cat. 6401.0 / 6427.0 / 6202.0 not staged. Populated columns: RBA F1 cash rate; RBA FSR |  |  |  |  |  |  |
| 2026-03-31 | 2026Q1 | 3.85 | Skeleton panel — ABS Cat. 6401.0 / 6427.0 / 6202.0 not staged. Populated columns: RBA F1 cash rate; RBA FSR |  |  |  |  |  |  |

*Full detail rows from property_market_detail.csv*

| as_of_date | region_name | data_completeness_pct | source_note | region_id | region_type | state | property_type | abs_price_index_value | abs_price_index_yoy_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-12-31 | Canberra | 37.5 | Capital-city aggregation | canberra|combined|2025-12-31 | capital | ACT | combined |  |  |
| 2025-12-31 | Canberra | 50.0 | Capital-city aggregation | canberra|house|2025-12-31 | capital | ACT | house |  |  |
| 2025-12-31 | Canberra | 50.0 | Capital-city aggregation | canberra|unit|2025-12-31 | capital | ACT | unit |  |  |
| 2025-12-31 | Sydney | 37.5 | Capital-city aggregation | sydney|combined|2025-12-31 | capital | NSW | combined |  |  |
| 2025-12-31 | Sydney | 50.0 | Capital-city aggregation | sydney|house|2025-12-31 | capital | NSW | house |  |  |
| 2025-12-31 | Sydney | 37.5 | Capital-city aggregation | sydney|houses|2025-12-31 | capital | NSW | houses |  |  |
| 2025-12-31 | Sydney | 50.0 | Capital-city aggregation | sydney|unit|2025-12-31 | capital | NSW | unit |  |  |
| 2025-12-31 | Sydney | 37.5 | Capital-city aggregation | sydney|units|2025-12-31 | capital | NSW | units |  |  |
| 2025-12-31 | Darwin | 25.0 | Capital-city aggregation | darwin|combined|2025-12-31 | capital | NT | combined |  |  |
| 2025-12-31 | Darwin | 37.5 | Capital-city aggregation | darwin|house|2025-12-31 | capital | NT | house |  |  |
| 2025-12-31 | Darwin | 37.5 | Capital-city aggregation | darwin|unit|2025-12-31 | capital | NT | unit |  |  |
| 2025-12-31 | Brisbane | 37.5 | Capital-city aggregation | brisbane|combined|2025-12-31 | capital | QLD | combined |  |  |
| 2025-12-31 | Brisbane | 50.0 | Capital-city aggregation | brisbane|house|2025-12-31 | capital | QLD | house |  |  |
| 2025-12-31 | Brisbane | 37.5 | Capital-city aggregation | brisbane|houses|2025-12-31 | capital | QLD | houses |  |  |
| 2025-12-31 | Brisbane | 50.0 | Capital-city aggregation | brisbane|unit|2025-12-31 | capital | QLD | unit |  |  |
| 2025-12-31 | Brisbane | 37.5 | Capital-city aggregation | brisbane|units|2025-12-31 | capital | QLD | units |  |  |
| 2025-12-31 | Adelaide | 37.5 | Capital-city aggregation | adelaide|combined|2025-12-31 | capital | SA | combined |  |  |
| 2025-12-31 | Adelaide | 50.0 | Capital-city aggregation | adelaide|house|2025-12-31 | capital | SA | house |  |  |
| 2025-12-31 | Adelaide | 50.0 | Capital-city aggregation | adelaide|unit|2025-12-31 | capital | SA | unit |  |  |
| 2025-12-31 | Hobart | 25.0 | Capital-city aggregation | hobart|combined|2025-12-31 | capital | TAS | combined |  |  |
| 2025-12-31 | Hobart | 37.5 | Capital-city aggregation | hobart|house|2025-12-31 | capital | TAS | house |  |  |
| 2025-12-31 | Hobart | 37.5 | Capital-city aggregation | hobart|unit|2025-12-31 | capital | TAS | unit |  |  |
| 2025-12-31 | Melbourne | 37.5 | Capital-city aggregation | melbourne|combined|2025-12-31 | capital | VIC | combined |  |  |
| 2025-12-31 | Melbourne | 50.0 | Capital-city aggregation | melbourne|house|2025-12-31 | capital | VIC | house |  |  |
| 2025-12-31 | Melbourne | 37.5 | Capital-city aggregation | melbourne|houses|2025-12-31 | capital | VIC | houses |  |  |
| 2025-12-31 | Melbourne | 50.0 | Capital-city aggregation | melbourne|unit|2025-12-31 | capital | VIC | unit |  |  |
| 2025-12-31 | Melbourne | 37.5 | Capital-city aggregation | melbourne|units|2025-12-31 | capital | VIC | units |  |  |
| 2025-12-31 | Perth | 37.5 | Capital-city aggregation | perth|combined|2025-12-31 | capital | WA | combined |  |  |
| 2025-12-31 | Perth | 50.0 | Capital-city aggregation | perth|house|2025-12-31 | capital | WA | house |  |  |
| 2025-12-31 | Perth | 50.0 | Capital-city aggregation | perth|unit|2025-12-31 | capital | WA | unit |  |  |
| 2025-12-31 | Australian Capital Territory | 12.5 | ACAT ACT Rental Q4 2025 (development stub) | australian_capital_territory|combined|2025-12-31 | sa4 | ACT | combined |  |  |
| 2025-12-31 | Hunter Valley Exc Newcastle | 12.5 | NSW Fair Trading Rental Bond Board Q4 2025 (development stub) | hunter_valley_exc_newcastle|combined|2025-12-31 | sa4 | NSW | combined |  |  |
| 2025-12-31 | Sydney - Inner West | 12.5 | NSW Fair Trading Rental Bond Board Q4 2025 (development stub) | sydney_-_inner_west|combined|2025-12-31 | sa4 | NSW | combined |  |  |
| 2025-12-31 | Sydney - Outer West And Blue Mountains | 12.5 | NSW Fair Trading Rental Bond Board Q4 2025 (development stub) | sydney_-_outer_west_and_blue_mountains|combined|2025-12-31 | sa4 | NSW | combined |  |  |
| 2025-12-31 | Darwin | 12.5 | NT Consumer Affairs Q4 2025 (development stub) | darwin|combined|2025-12-31 | sa4 | NT | combined |  |  |
| 2025-12-31 | Brisbane - Inner City | 12.5 | RTA Median Rents Q4 2025 (development stub) | brisbane_-_inner_city|combined|2025-12-31 | sa4 | QLD | combined |  |  |
| 2025-12-31 | Gold Coast | 12.5 | RTA Median Rents Q4 2025 (development stub) | gold_coast|combined|2025-12-31 | sa4 | QLD | combined |  |  |
| 2025-12-31 | Adelaide - Central And Hills | 12.5 | SA Consumer & Business Services Q4 2025 (development stub) | adelaide_-_central_and_hills|combined|2025-12-31 | sa4 | SA | combined |  |  |
| 2025-12-31 | Hobart | 12.5 | TAS CBOS Q4 2025 (development stub) | hobart|combined|2025-12-31 | sa4 | TAS | combined |  |  |
| 2025-12-31 | Geelong | 12.5 | Victorian Rental Report Q4 2025 (development stub) | geelong|combined|2025-12-31 | sa4 | VIC | combined |  |  |
| 2025-12-31 | Melbourne - Inner | 12.5 | Victorian Rental Report Q4 2025 (development stub) | melbourne_-_inner|combined|2025-12-31 | sa4 | VIC | combined |  |  |
| 2025-12-31 | Melbourne - West | 12.5 | Victorian Rental Report Q4 2025 (development stub) | melbourne_-_west|combined|2025-12-31 | sa4 | VIC | combined |  |  |
| 2025-12-31 | Perth - Inner | 12.5 | WA DMIRS Q4 2025 (development stub) | perth_-_inner|combined|2025-12-31 | sa4 | WA | combined |  |  |
| 2025-12-31 | Canberra Central | 12.5 | ACAT ACT Rental Q4 2025 (development stub) | canberra_central|unit|2025-12-31 | suburb | ACT | unit |  |  |
| 2025-12-31 | Yarralumla | 12.5 | ACAT ACT Rental Q4 2025 (development stub) | yarralumla|house|2025-12-31 | suburb | ACT | house |  |  |
| 2025-12-31 | Mosman | 25.0 | Domain top-suburb row | mosman|house|2025-12-31 | suburb | NSW | house |  |  |
| 2025-12-31 | Newcastle | 12.5 | NSW Fair Trading Rental Bond Board Q4 2025 (development stub) | newcastle|house|2025-12-31 | suburb | NSW | house |  |  |
| 2025-12-31 | Parramatta | 25.0 | Domain top-suburb row | parramatta|unit|2025-12-31 | suburb | NSW | unit |  |  |
| 2025-12-31 | Sydney Cbd | 12.5 | NSW Fair Trading Rental Bond Board Q4 2025 (development stub) | sydney_cbd|unit|2025-12-31 | suburb | NSW | unit |  |  |
| 2025-12-31 | Darwin Cbd | 12.5 | NT Consumer Affairs Q4 2025 (development stub; bedrooms not broken out) | darwin_cbd|unit|2025-12-31 | suburb | NT | unit |  |  |
| 2025-12-31 | Palmerston | 12.5 | NT Consumer Affairs Q4 2025 (development stub) | palmerston|house|2025-12-31 | suburb | NT | house |  |  |
| 2025-12-31 | Brisbane City | 12.5 | RTA Median Rents Q4 2025 (development stub) | brisbane_city|unit|2025-12-31 | suburb | QLD | unit |  |  |
| 2025-12-31 | Cairns | 12.5 | RTA Median Rents Q4 2025 (development stub) | cairns|house|2025-12-31 | suburb | QLD | house |  |  |
| 2025-12-31 | New Farm | 25.0 | Domain top-suburb row | new_farm|house|2025-12-31 | suburb | QLD | house |  |  |
| 2025-12-31 | South Brisbane | 25.0 | Domain top-suburb row | south_brisbane|unit|2025-12-31 | suburb | QLD | unit |  |  |
| 2025-12-31 | Surfers Paradise | 12.5 | RTA Median Rents Q4 2025 (development stub) | surfers_paradise|unit|2025-12-31 | suburb | QLD | unit |  |  |
| 2025-12-31 | Adelaide Cbd | 12.5 | SA Consumer & Business Services Q4 2025 (development stub) | adelaide_cbd|unit|2025-12-31 | suburb | SA | unit |  |  |
| 2025-12-31 | Unley | 25.0 | Domain top-suburb row | unley|house|2025-12-31 | suburb | SA | house |  |  |
| 2025-12-31 | Hobart Cbd | 12.5 | TAS Consumer Building & Occupational Services Q4 2025 (development stub) | hobart_cbd|unit|2025-12-31 | suburb | TAS | unit |  |  |
| 2025-12-31 | Launceston | 12.5 | TAS CBOS Q4 2025 (development stub) | launceston|house|2025-12-31 | suburb | TAS | house |  |  |
| 2025-12-31 | Sandy Bay | 12.5 | TAS CBOS Q4 2025 (development stub) | sandy_bay|house|2025-12-31 | suburb | TAS | house |  |  |
| 2025-12-31 | Footscray | 25.0 | Domain top-suburb row | footscray|unit|2025-12-31 | suburb | VIC | unit |  |  |
| 2025-12-31 | Geelong | 12.5 | Victorian Rental Report Q4 2025 (development stub) | geelong|house|2025-12-31 | suburb | VIC | house |  |  |
| 2025-12-31 | Melbourne Cbd | 12.5 | Victorian Rental Report Q4 2025 (development stub) | melbourne_cbd|unit|2025-12-31 | suburb | VIC | unit |  |  |
| 2025-12-31 | Toorak | 25.0 | Domain top-suburb row | toorak|house|2025-12-31 | suburb | VIC | house |  |  |
| 2025-12-31 | Cottesloe | 25.0 | Domain top-suburb row | cottesloe|house|2025-12-31 | suburb | WA | house |  |  |
| 2025-12-31 | Fremantle | 12.5 | WA DMIRS Q4 2025 (development stub) | fremantle|house|2025-12-31 | suburb | WA | house |  |  |
| 2025-12-31 | Perth Cbd | 12.5 | WA DMIRS Q4 2025 (development stub) | perth_cbd|unit|2025-12-31 | suburb | WA | unit |  |  |

*Full detail rows from property_market_overlays_by_building_type.csv*

| as_of_date | property_segment | property_segment_code | market_softness_score | region_risk_score | cycle_stage | aggregate_role | market_softness_band | region_risk_band | approvals_change_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-04-29 | Offices | CRE | 4.3 | 4.03 | downturn | specific | soft | High | -35.72 |
| 2026-04-29 | Education buildings | CRE | 3.25 | 3.38 | slowing | specific | softening | Elevated | -21.37 |
| 2026-04-29 | Retail and wholesale trade buildings | RET | 3.15 | 2.95 | neutral | specific | normal | Medium | 68.47 |
| 2026-04-29 | Short term accommodation buildings | CRE | 2.85 | 2.55 | growth | specific | supportive | Medium | 113.7 |
| 2026-04-29 | Aged care facilities | CRE | 2.7 | 2.73 | neutral | specific | normal | Medium | 219.88 |
| 2026-04-29 | Agricultural and aquacultural buildings | IND | 2.65 | 2.58 | neutral | specific | normal | Medium | 58.37 |
| 2026-04-29 | Total Non-residential | CON | 2.6 | 2.55 | neutral | aggregate (reviewer reference only) | normal | Medium | 71.46 |
| 2026-04-29 | Industrial Buildings - Total | CON | 2.4 | 2.45 | neutral | aggregate (reviewer reference only) | normal | Medium | 55.53 |
| 2026-04-29 | Commercial Buildings - Total | CON | 2.3 | 2.15 | growth | aggregate (reviewer reference only) | supportive | Medium | 165.42 |
| 2026-04-29 | Warehouses | IND | 2.2 | 2.35 | neutral | specific | normal | Medium | 69.32 |
| 2026-04-29 | Health buildings | CRE | 1.65 | 1.82 | growth | specific | supportive | Low | 355.03 |

## 6. Lineage / Traceability

A reviewer can resolve a number by table row, transformation row, then source inventory row within three hops.

*Lineage / Traceability*

| Analytical table | Number fields | Source row reference | Transformation script | Version / vintage | Reference hops |
| --- | --- | --- | --- | --- | --- |
| industry_risk_scores.csv | numeric columns in export | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv | src/overlays/build_industry_risk_scores.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| property_market_overlays.csv | numeric columns in export | building_approvals_nonres_xlsx; property_market_detail; property_cycle_panel | src/overlays/build_property_market_overlays.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| downturn_overlay_table.csv | numeric columns in export | property_cycle_panel; rba_fsr_page; staged arrears context | src/overlays/build_downturn_overlay_tables.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| macro_regime_flags.csv | numeric columns in export | rba_cash_rate_csv; staged arrears context | src/panels/build_macro_regime_flags.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| industry_failure_rates.csv | numeric columns in export | asic insolvency public extracts; ABS active-business counts | src/panels/build_industry_failure_rates.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| industry_financial_benchmarks.csv | numeric columns in export | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; business_indicators_inventory_ratio_xlsx; labour_force_industry_xlsx | src/panels/build_industry_financial_benchmarks.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| business_cycle_panel.csv | numeric columns in export | australian_industry_xlsx; business_indicators_profit_ratio_xlsx; business_indicators_inventory_ratio_xlsx; business_indicators_consumer_sales_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv | src/panels/build_business_cycle_panel.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| property_cycle_panel.csv | numeric columns in export | building_approvals_nonres_xlsx; property reference staged sources | src/panels/build_property_cycle_panel.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| macro_context.csv | numeric columns in export | cpi_all_groups_xlsx; cpi_subgroups_xlsx; ppi_manufacturing_xlsx; ppi_construction_xlsx; labour_force_industry_xlsx; rba_cash_rate_csv; rba_fsr_page | src/panels/build_macro_context_panel.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
| property_market_detail.csv | numeric columns in export | property_price_index_xlsx; property_price_capitals_xlsx; total_value_dwellings_xlsx; lending_indicators_xlsx; rba_table_e2_xls; cotality_hvi_page; domain_quarterly_page; sqm_headline_page; state rental bond pages | src/panels/build_property_reference_panel.py | Data Sources Inventory period/hash plus Transformations Applied build timestamp | number -> table row -> transformation row -> source inventory row |
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
| cotality_auction_clearance_page | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| cotality_hvi_page | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| cpi_all_groups_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| cpi_subgroups_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| domain_quarterly_page | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| dwelling_approvals_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| dwelling_value_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| labour_force_industry_xlsx | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| lending_indicators_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| nsw_rental_bonds_page | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| ppi_construction_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| ppi_manufacturing_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| property_price_capitals_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| property_price_index_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| ptrs_cycle_8_pdf | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| ptrs_cycle_9_pdf | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| ptrs_guidance | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| qld_median_rents_page | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| rba_cash_rate_csv | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| rba_chart_pack_page | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| rba_fsr_page | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| rba_smp_page | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| rba_table_e2_xls | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| sqm_headline_page | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |
| total_value_dwellings_xlsx | No successful manifest entry for this registry item | Awaiting next release or implement downloader/scraper | Next scheduled refresh cycle |
| vic_rental_report_page | Paid, gated, or manually extracted source | Manual staging required - see data/raw/manual or source-specific raw-public directory | Next scheduled refresh cycle |

## 8. Validation and Caveats

The integration test tests/integration/test_board_report_completeness.py is the executable contract for this section.

*Contract validation summary*

| Check category | Items | Status |
| --- | --- | --- |
| Source registry inventory | 37 | PASS |
| Canonical export transformations | 11 | PASS |
| Detailed analysis export tables | 11 | PASS |
| Lineage mappings | 11 | PASS |
| Manual/missing source disclosure | 34 | PASS |

The report does not fabricate current-period values. Prior-period or manually staged values remain dated through their source inventory period, manifest timestamp, export as_of_date, or build timestamp.

## Appendix A — Audit log (this session)

**Date:** 2026-06-11  
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
- **Construction base risk score (2.68, 'Medium')** — logged as an active methodology review item. See Section 9 of this report. Session: noted, not fixed.

### Dev-ergonomics notes
- Fresh git worktrees do not carry the git-ignored raw ABS/RBA staging directories. Copy them from a primary checkout, or add a `bootstrap_worktree.py` helper. Not urgent; logged for future consideration.
