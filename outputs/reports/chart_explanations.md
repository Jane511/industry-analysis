# Chart Explanations

## Current Public Data Vintages Used

The current generated outputs are based on the following staged source vintages. If any of these files are refreshed, rerun `python scripts/run_pipeline.py` so the workbook, tables, markdown outputs, and PDF report are rebuilt from the newer periods.

- **ABS Australian Industry**: FY 2022-23 and FY 2023-24 annual values from the 2023-24 release. Update cadence: Annual; refresh after each new ABS Australian Industry release.
- **ABS Business Indicators - Gross Operating Profit / Sales Ratio**: Quarterly series through December 2025. Update cadence: Quarterly.
- **ABS Business Indicators - Inventories / Sales Ratio**: Quarterly series through December 2025. Update cadence: Quarterly.
- **ABS Labour Force by Industry**: Monthly series through February 2026. Update cadence: Monthly.
- **ABS Building Approvals (Non-Residential)**: Monthly series through February 2026. Update cadence: Monthly.
- **RBA F1 cash-rate table**: Local CSV snapshot published 2 April 2026, with the latest staged observation dated 16 March 2026. Update cadence: Refresh when a newer RBA snapshot is staged or the policy-rate series changes.
- **PTRS**: Cycle 8 (July 2025) and Cycle 9 (January 2026) publications, plus March 2025 guidance. Update cadence: Refresh when a new PTRS cycle publication is released.

## C01 Industry Risk Dimensions Heatmap
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_heatmap`
Primary output table: `outputs/tables/industry_base_risk_scorecard.csv`
Metric basis: Public ABS/RBA metrics plus public-data-derived classification scores
Source period: Annual ABS FY 2022-23 to FY 2023-24; quarterly ABS series to Dec 2025; monthly ABS series to Feb 2026; RBA snapshot published 2 Apr 2026.

What it shows: This heatmap decomposes the structural industry view into the four classification dimensions used in the model, then shows how those dimensions accumulate into the macro composite. Darker shading indicates a higher structural contribution to sector risk.
Current read: Rate sensitivity is the strongest average pressure across the portfolio view, and Agriculture, Forestry And Fishing remains the most severe sector overall at 3.50. The chart is useful for identifying whether sector risk is being driven by one concentrated weakness or by a broad-based structural profile.
Credit relevance: In a formal credit pack, this chart helps explain why a sector ranks where it does before management moves to pricing, concentration, or monitoring actions. It supports top-down sector challenge rather than borrower-specific approval decisions.

## C02 Industry Base Risk Score by Sector
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_industry_s`
Primary output table: `outputs/tables/industry_base_risk_scorecard.csv`
Metric basis: Public ABS/RBA metrics plus public-data-derived classification scores
Source period: Annual ABS FY 2022-23 to FY 2023-24; quarterly ABS series to Dec 2025; monthly ABS series to Feb 2026; RBA snapshot published 2 Apr 2026.

What it shows: This ranking is the core sector risk league table. It converts the structural classification view and the public macro overlay into one comparable sector score on a 1 to 5 scale.
Current read: Agriculture, Forestry And Fishing is currently the highest-risk sector at 3.50, while Transport, Postal And Warehousing is lowest at 2.14. The spread between the highest and lowest sectors shows that the current public-data read is materially differentiated rather than flat.
Credit relevance: A portfolio or industry committee would typically use this chart to identify sectors for growth, maintenance, selective origination, or restriction. It is the central ranking view that anchors the rest of the report.

## C03 Employment Growth by Industry
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_industry_s`
Primary output table: `outputs/tables/industry_base_risk_scorecard.csv`
Metric basis: Public ABS labour-force series
Source period: ABS Labour Force monthly series to Feb 2026.

What it shows: This chart isolates employment growth because it is one of the cleanest public indicators of sector operating momentum and labour demand. Positive growth generally signals healthier demand conditions, while negative growth can indicate weaker activity or cost pressure.
Current read: Professional, Scientific And Technical Services shows the strongest YoY employment growth at +5.5%, while Wholesale Trade is weakest at -8.7%. That dispersion provides a direct cross-check on the broader sector ranking.
Credit relevance: In a formal sector reporting pack, employment is not usually used alone to set appetite, but it is a useful corroborating trend line when analysts assess whether a sector is stabilising, softening, or moving onto watchlist review.

## C04 Borrower Industry Risk Scorecard
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_borrower`
Primary output table: `outputs/tables/borrower_industry_risk_scorecard.csv`
Metric basis: Synthetic borrower archetype financials combined with public sector metrics
Source period: Annual ABS FY 2022-23 to FY 2023-24; quarterly ABS series to Dec 2025; monthly ABS series to Feb 2026; RBA snapshot published 2 Apr 2026. Synthetic borrower archetypes are model-generated.

What it shows: This scorecard translates the sector view into one synthetic borrower archetype per industry so the industry analysis can be linked to borrower-level decisioning. The archetypes are deliberately transparent and should be read as illustrative comparators rather than real obligors.
Current read: Agriculture, Forestry And Fishing Archetype is currently the highest-risk archetype at 3.09, while Transport, Postal And Warehousing Archetype is lowest at 2.20. The chart therefore shows how sector risk can carry through to a borrower-facing scorecard even before lender-specific qualitative factors are added.
Credit relevance: A corporate credit team could use this style of view to show how industry pressure changes the expected score distribution across a target origination pipeline. It is most useful as an explanatory layer, not as a production rating model.

## C05 Indicative Pricing by Borrower
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_pricing`
Primary output table: `outputs/tables/pricing_grid.csv`
Metric basis: Illustrative pricing assumptions combined with borrower score outputs
Source period: Annual ABS FY 2022-23 to FY 2023-24; quarterly ABS series to Dec 2025; monthly ABS series to Feb 2026; RBA snapshot published 2 Apr 2026. Pricing settings are illustrative rather than sourced.

What it shows: This chart converts the borrower score outcome into indicative pricing above the cash rate using the repo's transparent pricing grid. It separates the common base margin from the industry loading so the user can see how much of pricing is attributable to sector risk.
Current read: The highest all-in rate is 6.85% for Agriculture, Forestry And Fishing Archetype, versus 6.60% for Wholesale Trade Archetype.
Credit relevance: In formal reporting, this type of page is useful because it shows whether the pricing framework is directionally consistent with risk appetite. It should still be read as illustrative because actual pricing would also depend on structure, security, tenor, return hurdles, and relationship economics.

## C06 Sector Concentration: Current Exposure vs Limit
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_concentrat`
Primary output table: `outputs/tables/concentration_limits.csv`
Metric basis: Portfolio exposure proxy plus illustrative concentration limit settings
Source period: Annual ABS FY 2022-23 to FY 2023-24; quarterly ABS series to Dec 2025; monthly ABS series to Feb 2026; RBA snapshot published 2 Apr 2026. Exposure and limit settings are illustrative.

What it shows: This chart compares the proxy sector exposure mix against illustrative concentration limits. It highlights where the current portfolio shape would be above, near, or comfortably below the stated internal tolerance.
Current read: The highest utilisation is Retail Trade at 113.3% of limit. 2 sector breaches are shown, led by Retail Trade.
Credit relevance: This is the style of chart a portfolio forum would use to decide whether to slow new flow, require stronger structure, or actively rebalance the book. It is especially useful when combined with the sector risk ranking so management can distinguish high exposure in low-risk sectors from high exposure in stressed sectors.

## C07 Industry Watchlist Trigger Count
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_watchlist`
Primary output table: `outputs/tables/watchlist_triggers.csv`
Metric basis: Public ABS/RBA signals converted into watchlist rules
Source period: Annual ABS FY 2022-23 to FY 2023-24; quarterly ABS series to Dec 2025; monthly ABS series to Feb 2026; RBA snapshot published 2 Apr 2026.

What it shows: This chart converts selected public-data warning signals into a sector watchlist count. It is designed to summarise monitoring pressure rather than absolute risk, so multiple triggers indicate where a sector may need more frequent review even if it is not the single highest-risk sector.
Current read: Agriculture, Forestry And Fishing has the highest number of triggers at 5. That indicates a sector where the public signals are clustering negatively rather than showing only one isolated weak data point.
Credit relevance: A portfolio or risk team would typically use this kind of page to prioritise review resources, refresh covenant monitoring, and challenge whether current pipeline settings remain appropriate for the affected sectors.

## C08 Industry Stress Test Impact
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_stress`
Primary output table: `outputs/tables/industry_stress_test_matrix.csv`
Metric basis: Public ABS/RBA metrics with simplified APRA-informed stress assumptions
Source period: Annual ABS FY 2022-23 to FY 2023-24; quarterly ABS series to Dec 2025; monthly ABS series to Feb 2026; RBA snapshot published 2 Apr 2026.

What it shows: This chart applies the simplified scenario framework to the current sector view and shows the stressed score under the worst scenario by industry. It is intended to demonstrate directional vulnerability rather than a full severe-but-plausible capital stress model.
Current read: Demand shock produces the largest average uplift at 0.23 score points, and Agriculture, Forestry And Fishing reaches the highest stressed score at 3.73. This highlights which sectors deteriorate fastest when the scenario overlay is applied.
Credit relevance: A formal portfolio report would use this page to support management actions such as tighter appetite, higher monitoring frequency, or stronger underwriting expectations in sectors that are both risky today and highly stress-sensitive.

## C09 AR Days Benchmark and Stress by Industry
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_wc_ar`
Primary output table: `outputs/tables/industry_working_capital_risk_metrics.csv`
Metric basis: PTRS public payment-times tables when available, otherwise fallback proxy formula
Source period: PTRS Cycle 8 (Jul 2025) and Cycle 9 (Jan 2026).

What it shows: This chart isolates receivables collection timing from the wider scorecard by comparing base AR days to the stressed AR benchmark. It is designed to show where collection cycles are structurally longer and where payment timing can deteriorate most under stress.
Current read: Manufacturing currently has the longest AR benchmark at 33.7 days, with a stress benchmark of 48.0 days. Sectors with both high base AR days and large stress uplift should be read as more exposed to collection slippage and cash-conversion pressure.
Credit relevance: From a credit perspective, this page is relevant to borrower scorecards and PD interpretation because weaker collection performance can reduce liquidity headroom and increase the probability of financial stress before leverage ratios visibly worsen.

## C10 AP Days Benchmark and Stress by Industry
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_wc_ap`
Primary output table: `outputs/tables/industry_working_capital_risk_metrics.csv`
Metric basis: PTRS public payment-times tables when available, otherwise fallback proxy formula
Source period: PTRS Cycle 8 (Jul 2025) and Cycle 9 (Jan 2026).

What it shows: This chart shows supplier-payment timing separately from receivables and inventory. It compares base AP days with the stressed AP benchmark so the user can identify where working-capital support may depend on extended creditor funding.
Current read: Manufacturing currently has the longest AP benchmark at 33.7 days, with the stress benchmark extending to 48.0 days. Longer payable cycles can improve cash conversion mechanically, but they can also point to supplier stretch when conditions tighten.
Credit relevance: In a formal working-capital review, AP metrics matter because an apparently acceptable cash-conversion position can still be fragile if it is being achieved by leaning on suppliers. That is why this chart is presented separately instead of being netted inside the CCC alone.

## C11 Inventory Days and Stock-Build Risk by Industry
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_wc_inv`
Primary output table: `outputs/tables/industry_working_capital_risk_metrics.csv`
Metric basis: ABS quarterly inventories/sales ratio converted to estimated inventory days plus stock-build overlay
Source period: ABS inventory ratio to Dec 2025 plus ABS annual FY 2023-24 margin data.

What it shows: This chart converts the ABS inventories-to-sales ratio into estimated inventory days and overlays the stock-build flag. It therefore separates simple inventory duration from the broader question of whether stock is building into weaker conditions.
Current read: Manufacturing has the highest inventory benchmark at 52.7 days and is flagged Moderate on stock build. Sectors with long inventory duration and elevated build risk are more likely to experience cash lock-up or weaker inventory liquidity if demand softens.
Credit relevance: This page is particularly relevant to scorecard and LGD thinking. Inventory that is slow-moving or building into weaker trading conditions may both weaken current liquidity and reduce expected recoverability in a downside case.

## C12 Working-Capital Overlay Scores for PD, Scorecard, and LGD
Source workbook: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
Source sheet: `chart_data_wc_overlay`
Primary output table: `outputs/tables/industry_working_capital_risk_metrics.csv`
Metric basis: Deterministic overlay scores derived from AR, AP, inventory, and cash-conversion-cycle metrics
Source period: PTRS Jul 2025 and Jan 2026 plus ABS inventory ratio to Dec 2025.

What it shows: This chart aggregates the AR, AP, inventory, and cash-conversion-cycle signals into three separate overlays: one for scorecard interpretation, one for PD interpretation, and one for LGD interpretation. The purpose is to prevent a single working-capital signal from doing every job.
Current read: Manufacturing has the highest scorecard overlay at 4.08, Manufacturing has the highest PD overlay at 3.58, and Manufacturing has the highest LGD overlay at 3.89. The different overlays show that current operating stress, default pressure, and recoverability pressure are related but not identical.
Credit relevance: This is the most management-oriented working-capital page in the pack. It helps a credit or portfolio forum see whether a sector's issue is mainly operating pressure, rising default risk, or recoverability weakness, which leads to different underwriting or monitoring responses.
