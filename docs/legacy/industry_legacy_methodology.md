# Clean Methodology Reference

This document is a clean rewrite of the retained legacy industry-analysis methodology in this repository. It is designed for:

- readers who are not technical
- readers who want to understand what the project is doing without reading Python
- credit or risk reviewers who want to trace each output back to its source data and formula

Scope note:

- this file is retained as a legacy methodology reference for reviewer continuity
- this file covers the legacy industry workflow that writes to `output/tables/`, `output/`, and `industry_risk_formal_report.pdf`
- the current property-reference-layer methodology lives in `docs/project_overview.md`, `docs/methodology_region_risk.md`, `docs/methodology_property_cycle.md`, `docs/methodology_arrears_environment.md`, and `docs/methodology_downturn_overlays.md`

The goal of this legacy workflow is not to reproduce an internal institutional model. The goal is to show, in a transparent way, how Australian public data can be turned into a structured industry risk analysis workflow.

## 1. Executive Summary

At a high level, this legacy workflow does five things:

1. It uses public Australian data to build a sector-level risk view.
2. It converts that public data into simple credit-style metrics such as margin pressure, inventory pressure, payment timing, and stress sensitivity.
3. It creates one synthetic borrower archetype per industry so the sector analysis can be linked to a borrower-style scorecard.
4. It translates the risk results into portfolio-style outputs such as pricing, policy, concentration, watchlists, and stress testing.
5. It produces a workbook-backed report so the logic is traceable.

The key point for non-technical readers is this:

- public data is used wherever possible
- when public data does not directly publish an internal credit metric, the project uses a fixed rule or formula
- those fixed rules are called deterministic proxy rules
- the output is a transparent analytical workflow, not a production credit model

## 2. What The Public Datasets Mean

The legacy industry workflow uses seven main public datasets.

| Dataset ID | Dataset | Plain-English Meaning | Main Use In The Project |
|---|---|---|---|
| `ABS-AI` | ABS Australian Industry | Annual industry totals such as sales, employment, wages, EBITDA, and operating profit | Structural sector view, margins, sales growth, portfolio proxy |
| `ABS-BI-22` | ABS Business Indicators: Gross Operating Profit / Sales Ratio | Quarterly profitability ratio by industry | Margin level and margin trend |
| `ABS-BI-23` | ABS Business Indicators: Inventories / Sales Ratio | Quarterly inventory intensity by industry | Inventory days estimate and stock-build risk |
| `ABS-LF` | ABS Labour Force by Industry | Monthly employment trend by industry | Employment growth signal |
| `ABS-BA` | ABS Building Approvals (Non-Residential) | Monthly non-residential approvals by building type | Demand proxy for selected sectors |
| `RBA-F1` | RBA Cash Rate | Official Australian cash rate time series | Interest-rate backdrop and pricing reference |
| `PTRS` | Payment Times Reporting Scheme publications | Public payment timing by industry | AR and AP benchmark timing proxy |

### Current Public Data Vintages Used

The current staged source vintages used by the model are:

- `ABS Australian Industry`: FY `2022-23` and FY `2023-24` annual values from the `2023-24` release
- `ABS Business Indicators - Gross Operating Profit / Sales Ratio`: quarterly series through `December 2025`
- `ABS Business Indicators - Inventories / Sales Ratio`: quarterly series through `December 2025`
- `ABS Labour Force by Industry`: monthly series through `February 2026`
- `ABS Building Approvals (Non-Residential)`: monthly series through `February 2026`
- `RBA F1`: local CSV snapshot published `2 April 2026`, with the latest staged observation dated `16 March 2026`
- `PTRS`: Cycle `8` (`July 2025`) and Cycle `9` (`January 2026`) publications, plus `March 2025` guidance

Suggested refresh cadence:

- annual for `ABS Australian Industry`
- quarterly for `ABS Business Indicators`
- monthly for `ABS Labour Force` and `ABS Building Approvals`
- whenever a newer `RBA F1` file is staged or the cash-rate series changes
- whenever a new `PTRS` cycle publication is released

## 3. Important Credit Terms

| Term | Plain-English Meaning |
|---|---|
| `EBITDA margin` | How much operating earnings a business keeps from each dollar of revenue before interest, tax, depreciation, and amortisation |
| `AR days` | How many days it takes to collect money from customers on average |
| `AP days` | How many days it takes to pay suppliers on average |
| `Inventory days` | How many days stock sits before being sold or used |
| `Cash conversion cycle` | The number of days cash is tied up in working capital; simplified as `AR days + inventory days - AP days` |
| `Debt / EBITDA` | A simple leverage ratio: debt divided by operating earnings |
| `ICR` | Interest coverage ratio: operating earnings divided by interest cost |
| `PD` | Probability of default: the chance a borrower may fail to repay |
| `LGD` | Loss given default: how much a lender may lose if default happens |
| `LVR` | Loan-to-value ratio: loan amount divided by collateral value |
| `Covenant` | A rule or test inside a loan agreement that the borrower must meet |

## 4. End-To-End Logic In One View

The project follows this flow:

1. `Stage 1: Foundation`
   Industry structure is scored using annual ABS industry data.
2. `Stage 2: Macro View`
   Current public signals such as employment, margins, inventory, demand, and rates are added.
3. `Stage 3: Benchmarks`
   Sector benchmark ratios are created for leverage, coverage, AR, AP, and inventory.
4. `Stage 4: Working Capital Overlays`
   AR, AP, inventory, and cash conversion cycle are converted into scorecard / PD / LGD-style overlays.
5. `Stage 5: Bottom-Up Archetypes`
   One synthetic borrower is created per industry and scored against the industry benchmarks.
6. `Stage 6: Final Borrower Scorecard`
   Structural, macro, and bottom-up views are blended into one final borrower industry score.
7. `Stage 7-9: Portfolio Outputs`
   Pricing, policy, concentration, appetite, stress testing, ESG, watchlists, and reporting outputs are produced.

## 5. How The Final Industry Analysis Is Built

There are three main layers.

### 5.1 Structural Industry Layer

This answers:

- Is the sector naturally cyclical?
- Is it sensitive to rates?
- Is it highly dependent on demand?
- Is it exposed to external shocks?

The output is:

```text
classification_risk_score
```

### 5.2 Current Macro Layer

This answers:

- Is employment improving or deteriorating?
- Are margins strong or weak?
- Is inventory building up?
- Is sector demand improving or worsening?

The output is:

```text
macro_risk_score
```

### 5.3 Synthetic Borrower Layer

This answers:

- If a typical borrower in that sector looked slightly weaker than the benchmark, how risky would it look?

The output is:

```text
bottom_up_risk_score
```

### 5.4 Final Borrower Industry Score

The final borrower-style risk score is:

```text
final_industry_risk_score
= 0.35 × classification_risk_score
+ 0.30 × macro_risk_score
+ 0.35 × bottom_up_risk_score
```

Important note:

- the working-capital overlay tables do **not** currently feed this final score directly
- they sit beside it as additional interpretation for scorecard, PD, and LGD thinking

## 6. Core Build Tables (Not In `output/tables`, But Essential)

These tables are saved in `data/processed/` and drive the final output tables.

### 6.1 `industry_classification_foundation.csv`

**Purpose**

Create the structural industry view.

**Public data used**

- `ABS-AI`: sales, employment, wages, EBITDA

**Main calculations**

```text
sales_growth_pct_foundation
= ((sales_2023_24 / sales_2022_23) - 1) × 100
```

`cyclical_score`

- if sales growth `< 0%` -> `5`
- if `< 2%` -> `4`
- if `< 6%` -> `3`
- if `< 12%` -> `2`
- otherwise -> `1`

`rate_sensitivity_score`

Raw score from `ebitda_margin_pct_foundation`:

- `< 6%` -> `5`
- `< 9%` -> `4`
- `< 12%` -> `3`
- `< 16%` -> `2`
- otherwise -> `1`

Then blended with a sector anchor:

```text
blended_score = round((raw_score + sector_anchor) / 2)
```

`demand_dependency_score`

Raw score from sales growth:

- `< -8%` -> `5`
- `< -2%` -> `4`
- `< 2%` -> `3`
- `< 6%` -> `2`
- otherwise -> `1`

Then blended with a sector anchor.

`external_shock_score`

First calculate:

```text
signal
= max(0, 10 - ebitda_margin_pct_foundation) / 2
+ max(0, 2 - sales_growth_pct_foundation / 4)
```

Then map:

- `> 4.5` -> `5`
- `> 3.0` -> `4`
- `> 2.0` -> `3`
- `> 1.0` -> `2`
- otherwise -> `1`

Then blend with a sector anchor.

`classification_risk_score`

```text
classification_risk_score
= average(
  cyclical_score,
  rate_sensitivity_score,
  demand_dependency_score,
  external_shock_score
)
```

**What the metrics mean**

| Metric | Meaning |
|---|---|
| `cyclical_score` | How exposed the sector appears to the business cycle |
| `rate_sensitivity_score` | How vulnerable the sector is to higher rates or tighter financing conditions |
| `demand_dependency_score` | How much the sector depends on healthy customer demand |
| `external_shock_score` | How exposed the sector appears to shocks such as weak growth or thin earnings buffers |
| `classification_risk_score` | One combined structural sector-risk score |

### 6.2 `industry_macro_view_public_signals.csv`

**Purpose**

Add current public economic signals on top of the structural industry view.

**Public data used**

- `ABS-AI`: annual sales, margins, wages
- `ABS-BI-22`: profitability ratio
- `ABS-BI-23`: inventory ratio
- `ABS-LF`: employment trend
- `ABS-BA`: demand proxy
- `RBA-F1`: cash rate

**What the raw public fields mean**

| Field | Plain-English Meaning |
|---|---|
| `gross_operating_profit_to_sales_ratio_latest` | The share of sales that remains as gross operating profit in the latest quarter |
| `inventories_to_sales_ratio_latest` | Inventory relative to sales in the latest quarter |
| `employment_yoy_growth_pct` | Year-on-year employment growth in the sector |
| `demand_yoy_growth_pct` | A forward-looking demand proxy using building approvals for selected sectors |
| `cash_rate_latest_pct` | Latest official cash rate |

**Main calculations**

`sales_growth_pct`

```text
sales_growth_pct
= ((sales_m_latest / sales_m_prev) - 1) × 100
```

`ebitda_margin_change_pctpts`

```text
ebitda_margin_change_pctpts
= ebitda_margin_pct_latest - ebitda_margin_pct_prev
```

`gross_operating_profit_to_sales_ratio_yoy_change`

```text
latest_ratio - ratio_12_months_ago
```

`inventories_to_sales_ratio_yoy_change`

```text
latest_inventory_ratio - inventory_ratio_12_months_ago
```

`inventory_days_est`

If ABS inventory ratio exists:

```text
inventory_days_est
= inventories_to_sales_ratio_latest × 91.25 / estimated_cogs_to_sales_ratio

estimated_cogs_to_sales_ratio
= clip(1 - margin_ratio, 0.45, 0.95)
```

Where `margin_ratio` comes from:

- `gross_operating_profit_to_sales_ratio_latest` first
- otherwise `ebitda_margin_pct_latest / 100`

If the ABS inventory ratio is missing, the project uses a fallback rule based on:

- sector inventory relevance
- margin level
- sales growth
- demand growth
- wages-to-sales ratio

`inventory_days_yoy_change`

```text
inventory_days_yoy_change
= inventory_days_est - inventory_days_prev_est
```

`inventory_stock_build_risk`

This is a points-based flag.
Points are added for:

- high inventory days
- inventory days rising year-on-year
- inventory ratio rising year-on-year
- rising stock combined with weak sales, weak demand, or weaker margins

Points are reduced for low- or medium-inventory sectors.

Final mapping:

- `>= 4.0` -> `High`
- `>= 2.5` -> `Elevated`
- `>= 1.0` -> `Moderate`
- otherwise -> `Low`

**Macro score thresholds**

| Score | Rule |
|---|---|
| `employment_score` | `<0 = 5`, `<1 = 4`, `<2.5 = 3`, `<4 = 2`, else `1` |
| `margin_level_score` | ratio or percentage version of margin: very low margin scores `5`, very strong margin scores `1` |
| `margin_trend_score` | sharp decline scores `5`, strong improvement scores `1` |
| `inventory_score` | `round(0.7 × inventory_days_level_score + 0.3 × stock_build_score)` |
| `demand_score` | `<-20 = 5`, `<-5 = 4`, `<5 = 3`, `<20 = 2`, else `1` |

Important note:

- in the macro layer, `inventory_stock_build_risk` is mapped to scores as `Low = 1`, `Moderate = 2`, `Elevated = 4`, `High = 5`

`macro_risk_score`

```text
macro_risk_score
= average(
  employment_score,
  margin_level_score,
  margin_trend_score,
  inventory_score,
  demand_score
)
```

`industry_base_risk_score`

```text
industry_base_risk_score
= 0.55 × classification_risk_score
+ 0.45 × macro_risk_score
```

`industry_base_risk_level`

- `<= 2.0` -> `Low`
- `<= 3.0` -> `Medium`
- `<= 4.0` -> `Elevated`
- `> 4.0` -> `High`

### 6.3 `borrower_benchmark_comparison.csv`

**Purpose**

Create one synthetic borrower archetype per sector and compare it with the sector benchmark.

**Public data used**

- all key drivers come from the macro and benchmark layers above

**Main calculations**

`stress_factor`

```text
stress_factor
= max(0.15, ((classification_risk_score + macro_risk_score) / 2 - 2.2) / 4)
```

`revenue`

```text
revenue = clip(industry_sales / 40,000, 6,000,000, 22,000,000)
```

`ebitda`

```text
margin = max(2.0, ebitda_margin_pct_latest - stress_factor × 3.2)
ebitda = revenue × margin / 100
```

`total_debt`

```text
debt_to_ebitda = debt_to_ebitda_benchmark × (1 + stress_factor × 0.22)
total_debt = ebitda × debt_to_ebitda
```

`interest_expense`

```text
icr = max(1.1, icr_benchmark - stress_factor × 0.45)
interest_expense = ebitda / icr
```

`accounts_receivable`

```text
ar_days = ar_days_benchmark × (1 + stress_factor × 0.10)
accounts_receivable = revenue × ar_days / 365
```

`accounts_payable`

```text
ap_days = ap_days_benchmark × (1 + stress_factor × 0.06)
accounts_payable = cogs_or_purchases × ap_days / 365
```

`inventory`

```text
inventory_days = inventory_days_benchmark × (1 + stress_factor × 0.12)
inventory = cogs_or_purchases × inventory_days / 365
```

`bottom_up_risk_score`

This is the mean of six borrower-to-benchmark gap scores:

- `ebitda_margin_score`
- `debt_to_ebitda_score`
- `icr_score`
- `ar_days_score`
- `ap_days_score`
- `inventory_days_score`

## 7. Output Tables In `output/tables`

This section explains every CSV currently written to `output/tables`.

### 7.1 `industry_base_risk_scorecard.csv`

**Role**

This is the main sector ranking table for the project.

**Columns**

| Column | Where It Comes From | Meaning |
|---|---|---|
| `industry` | Foundation | Sector display name |
| `classification_risk_score` | Stage 1 | Structural sector risk |
| `macro_risk_score` | Stage 2 | Current public-data risk view |
| `industry_base_risk_score` | Stage 2 | Combined sector risk score |
| `industry_base_risk_level` | Stage 2 | Band: Low / Medium / Elevated / High |
| `employment_yoy_growth_pct` | ABS-LF | Employment momentum |
| `ebitda_margin_pct_latest` | ABS-AI | Annual earnings margin |
| `gross_operating_profit_to_sales_ratio_latest` | ABS-BI-22 | Quarterly profitability ratio |
| `inventories_to_sales_ratio_latest` | ABS-BI-23 | Quarterly inventory intensity ratio |
| `inventory_days_est` | Derived from ABS-BI-23 and margin | Estimated inventory duration |
| `inventory_days_yoy_change` | Derived | Whether inventory duration is rising or falling |
| `inventory_stock_build_risk` | Derived | Whether inventory appears to be building riskily |
| `demand_proxy_building_type` | ABS-BA mapping | Which approvals series was used as the demand proxy |
| `demand_yoy_growth_pct` | ABS-BA | Directional demand signal |
| `cash_rate_latest_pct` | RBA-F1 | Latest cash rate |
| `cash_rate_change_1y_pctpts` | RBA-F1 | One-year change in cash rate |

### 7.2 `industry_public_benchmarks.csv`

**Role**

This is the clean public-metrics table without the main risk scores.

**Columns**

| Column | Meaning |
|---|---|
| `ebitda_margin_pct_latest` | Annual EBITDA margin from ABS Australian Industry |
| `ebitda_margin_change_pctpts` | Change in annual EBITDA margin |
| `gross_operating_profit_to_sales_ratio_latest` | Latest quarterly profitability ratio |
| `gross_operating_profit_to_sales_ratio_yoy_change` | Profitability change over one year |
| `inventories_to_sales_ratio_latest` | Latest inventory intensity ratio |
| `inventories_to_sales_ratio_yoy_change` | Inventory intensity change over one year |
| `inventory_days_est` | Estimated inventory days from public data |
| `inventory_days_yoy_change` | Year-on-year change in estimated inventory days |
| `inventory_stock_build_risk` | Risk flag showing whether stock is building |
| `inventory_days_est_source` | Whether the estimate came from ABS ratio conversion or fallback logic |
| `employment_yoy_growth_pct` | Employment growth from ABS labour-force data |
| `demand_proxy_building_type` | Demand proxy chosen for the sector |
| `demand_yoy_growth_pct` | Demand proxy year-on-year growth |

### 7.3 `industry_generated_benchmarks.csv`

**Role**

This converts the public data into sector benchmark ratios that are more familiar to credit users.

**Key equations**

`ar_days_benchmark` fallback:

```text
18
+ 0.22 × inventory_days_benchmark
+ 3.2 × classification_risk_score
- 0.35 × profit_margin_pct
```

Then clipped to:

```text
5 to 75 days
```

For Retail and Accommodation:

```text
ar_days_benchmark_formula = ar_base × 0.35
```

`ap_days_benchmark` fallback:

```text
24
+ 0.18 × inventory_days_benchmark
+ 2.5 × macro_risk_score
- 0.20 × profit_margin_pct
```

Then clipped to:

```text
20 to 70 days
```

`debt_to_ebitda_benchmark`

```text
1.2
+ 0.07 × max(0, 18 - profit_margin_pct)
+ 0.22 × classification_risk_score
+ 0.12 × macro_risk_score
+ inventory_days_benchmark / 120
```

Then clipped to:

```text
1.5x to 4.5x
```

`icr_benchmark`

```text
5.3
- 0.75 × debt_to_ebitda_benchmark
+ 0.04 × profit_margin_pct
- 0.10 × (classification_risk_score - 3)
```

Then clipped to:

```text
1.5x to 4.5x
```

**Important PTRS note**

If PTRS is available:

- `ar_days_benchmark` uses PTRS public payment timing
- `ap_days_benchmark` uses PTRS public payment timing
- `ar_days_stress_benchmark` and `ap_days_stress_benchmark` use PTRS stress points
- `ar_days_severe_benchmark` and `ap_days_severe_benchmark` use PTRS severe points

If PTRS is not available:

- the fallback formulas above are used

**Columns**

| Column | Meaning |
|---|---|
| `debt_to_ebitda_benchmark` | Sector leverage benchmark |
| `icr_benchmark` | Sector interest coverage benchmark |
| `ar_days_benchmark` | Sector receivables timing benchmark |
| `ar_days_stress_benchmark` | Sector stressed AR timing |
| `ar_days_severe_benchmark` | Sector severe AR timing |
| `ap_days_benchmark` | Sector payable timing benchmark |
| `ap_days_stress_benchmark` | Sector stressed AP timing |
| `ap_days_severe_benchmark` | Sector severe AP timing |
| `inventory_days_benchmark` | Sector inventory duration benchmark |
| `ptrs_cycle8_avg_payment_days`, `ptrs_cycle9_avg_payment_days` | Official public PTRS timing reference points |
| `ptrs_cycle8_paid_on_time_pct`, `ptrs_cycle9_paid_on_time_pct` | Official public PTRS timeliness reference points |
| `ar_days_benchmark_source`, `ap_days_benchmark_source` | Whether PTRS or fallback formula was used |

### 7.4 `industry_working_capital_risk_metrics.csv`

**Role**

This is the dedicated AR / AP / inventory / cash-conversion-cycle overlay table.

**Important interpretation**

This table does **not** create a real PD or LGD model. It creates structured overlay scores that help interpret:

- operating pressure
- default pressure
- recoverability pressure

**Key equations**

`ar_stress_uplift_days`

```text
ar_days_stress_benchmark - ar_days_benchmark
```

`ar_severe_uplift_days`

```text
ar_days_severe_benchmark - ar_days_benchmark
```

`ap_stress_uplift_days`

```text
ap_days_stress_benchmark - ap_days_benchmark
```

`ap_severe_uplift_days`

```text
ap_days_severe_benchmark - ap_days_benchmark
```

`cash_conversion_cycle_benchmark_days`

```text
ar_days_benchmark + inventory_days_benchmark - ap_days_benchmark
```

`cash_conversion_cycle_stress_days`

```text
ar_days_stress_benchmark + inventory_days_benchmark - ap_days_benchmark
```

`cash_conversion_cycle_uplift_days`

```text
cash_conversion_cycle_stress_days - cash_conversion_cycle_benchmark_days
```

`ptrs_paid_on_time_pct_latest`

```text
ptrs_cycle9_paid_on_time_pct
if missing, ptrs_cycle8_paid_on_time_pct
```

**Working-capital component scoring**

`ar_collection_score`

```text
average(
  score_receivable_days(ar_days_benchmark),
  score_uplift_days(ar_stress_uplift_days),
  score_paid_on_time(ptrs_paid_on_time_pct_latest)
)
```

`receivables_realisation_score`

```text
average(
  score_uplift_days(ar_stress_uplift_days),
  score_uplift_days(ar_severe_uplift_days),
  score_paid_on_time(ptrs_paid_on_time_pct_latest)
)
```

`ap_supplier_stretch_score`

```text
average(
  score_payable_days(ap_days_benchmark),
  score_uplift_days(ap_stress_uplift_days),
  score_paid_on_time(ptrs_paid_on_time_pct_latest)
)
```

`inventory_liquidity_score`

- `<=10 = 1`
- `<=20 = 2`
- `<=35 = 3`
- `<=50 = 4`
- `>50 = 5`

`inventory_stock_build_score`

- `Low = 1`
- `Moderate = 3`
- `Elevated = 4`
- `High = 5`

`cash_conversion_cycle_score`

- `<=5 = 1`
- `<=15 = 2`
- `<=30 = 3`
- `<=45 = 4`
- `>45 = 5`

**Overlay equations**

`working_capital_scorecard_overlay_score`

```text
average(
  ar_collection_score,
  ap_supplier_stretch_score,
  inventory_liquidity_score,
  cash_conversion_cycle_score
)
```

`working_capital_pd_overlay_score`

```text
average(
  working_capital_scorecard_overlay_score,
  inventory_stock_build_score,
  receivables_realisation_score
)
```

`working_capital_lgd_overlay_score`

```text
average(
  receivables_realisation_score,
  inventory_liquidity_score,
  inventory_stock_build_score
)
```

**What the three overlays mean**

| Overlay | Meaning |
|---|---|
| `working_capital_scorecard_overlay_score` | Current operating working-capital pressure |
| `working_capital_pd_overlay_score` | Whether working-capital stress looks more likely to turn into default pressure |
| `working_capital_lgd_overlay_score` | Whether receivables and inventory look weaker from a recoverability point of view |

### 7.5 `borrower_working_capital_risk_metrics.csv`

**Role**

This applies the working-capital overlay logic to the synthetic borrower archetypes.

**Key equations**

`cash_conversion_cycle_days`

```text
ar_days + inventory_days - ap_days
```

`cash_conversion_cycle_benchmark_days`

```text
ar_days_benchmark + inventory_days_benchmark - ap_days_benchmark
```

`cash_conversion_cycle_gap_days`

```text
cash_conversion_cycle_days - cash_conversion_cycle_benchmark_days
```

`receivables_headroom_to_stress_days`

```text
ar_days_stress_benchmark - ar_days
```

`payables_headroom_to_stress_days`

```text
ap_days_stress_benchmark - ap_days
```

`receivables_realisation_score` and `supplier_stretch_score`

- `>=15 days headroom = 1`
- `>=10 = 2`
- `>=5 = 3`
- `>=0 = 4`
- `<0 = 5`

`working_capital_scorecard_metric_score`

```text
average(
  ar_days_score,
  ap_days_score,
  inventory_days_score,
  cash_conversion_cycle_score
)
```

`working_capital_pd_metric_score`

```text
average(
  working_capital_scorecard_metric_score,
  working_capital_pd_overlay_score,
  receivables_realisation_score,
  inventory_stock_build_score
)
```

`working_capital_lgd_metric_score`

```text
average(
  receivables_realisation_score,
  inventory_days_score,
  working_capital_lgd_overlay_score
)
```

**What this table means**

This is still synthetic because the borrower rows are synthetic. It shows how a later borrower scorecard, PD view, or LGD view could use:

- borrower-specific AR / AP / inventory gaps
- borrower-specific CCC pressure
- industry-level overlay context

### 7.6 `borrower_industry_risk_scorecard.csv`

**Role**

This is the final borrower-style ranking table.

**Equation**

```text
final_industry_risk_score
= 0.35 × classification_risk_score
+ 0.30 × macro_risk_score
+ 0.35 × bottom_up_risk_score
```

`risk_level`

- `<= 2.0` -> `Low`
- `<= 3.0` -> `Medium`
- `<= 4.0` -> `Elevated`
- `> 4.0` -> `High`

**Columns**

| Column | Meaning |
|---|---|
| `classification_risk_score` | Structural industry risk |
| `macro_risk_score` | Current public-data risk |
| `bottom_up_risk_score` | Synthetic borrower-to-benchmark risk |
| `final_industry_risk_score` | Final borrower-style score |
| `risk_level` | Final risk band |

### 7.7 `industry_portfolio_proxy.csv`

**Role**

Estimate a simple sector exposure mix because actual internal portfolio exposure data is not public.

**Equation**

```text
sales_share = sector_sales / total_sales
employment_share = sector_employment / total_employment

current_exposure_pct
= (0.70 × sales_share + 0.30 × employment_share) × 100
```

**Meaning**

- `sales_share` represents economic size
- `employment_share` represents sector scale and breadth
- the 70/30 blend acts as a transparent proxy for lending exposure

**Columns**

| Column | Meaning |
|---|---|
| `industry` | Sector name |
| `current_exposure_pct` | Proxy portfolio share allocated to the sector |
| `exposure_proxy_source` | Narrative description of the proxy method |

### 7.8 `concentration_limits.csv`

**Role**

Compare the portfolio proxy with simple illustrative sector limits.

**Rules**

`concentration_limit_pct`

- `Low` -> `25.0`
- `Medium` -> `20.0`
- `Elevated` -> `15.0`
- `High` -> `10.0`

`headroom_pct`

```text
concentration_limit_pct - current_exposure_pct
```

`breach`

```text
current_exposure_pct > concentration_limit_pct
```

`utilisation_pct`

```text
(current_exposure_pct / concentration_limit_pct) × 100
```

**Columns**

| Column | Meaning |
|---|---|
| `industry` | Sector name |
| `risk_level` | Sector base-risk band |
| `industry_base_risk_score` | Sector base-risk score |
| `concentration_limit_pct` | Illustrative sector limit |
| `current_exposure_pct` | Proxy current sector exposure |
| `headroom_pct` | Remaining room before breaching the limit |
| `breach` | True / False breach flag |
| `utilisation_pct` | Percent of limit currently used |

### 7.9 `pricing_grid.csv`

**Role**

Translate the borrower score into an indicative pricing output.

**Equation**

```text
indicative_rate_pct = base_margin_pct + industry_loading_pct
all_in_rate_pct = cash_rate_pct + indicative_rate_pct
```

**Rules**

- `base_margin_pct = 2.50`
- `industry_loading_pct`
  - `Low = 0.00`
  - `Medium = 0.25`
  - `Elevated = 0.50`
  - `High = 1.00`

**Meaning**

This is an illustrative pricing bridge from risk to price. It is not a production pricing engine.

**Columns**

| Column | Meaning |
|---|---|
| `borrower_name` | Synthetic borrower name |
| `industry` | Borrower sector |
| `risk_level` | Final borrower risk band |
| `final_industry_risk_score` | Final borrower-style score |
| `cash_rate_pct` | Latest cash rate |
| `base_margin_pct` | Common base credit margin |
| `industry_loading_pct` | Sector-risk loading |
| `indicative_rate_pct` | Margin above cash rate |
| `all_in_rate_pct` | Total indicative lending rate |

### 7.10 `policy_overlay.csv`

**Role**

Attach simple policy settings to each borrower risk level.

**Rules**

| Risk Level | Max LVR | Review Frequency | Approval Authority | Additional Conditions |
|---|---:|---|---|---|
| `Low` | `80` | Annual | Standard delegated authority | None |
| `Medium` | `75` | Annual | Standard delegated authority | Industry section in credit memo required |
| `Elevated` | `65` | Semi-annual | Senior credit officer | Enhanced due diligence; stress-test cash flows |
| `High` | `50` | Quarterly | Credit committee | New lending subject to committee approval; mandatory collateral revaluation |

**Columns**

| Column | Meaning |
|---|---|
| `borrower_name` | Synthetic borrower name |
| `industry` | Borrower sector |
| `risk_level` | Final borrower risk band |
| `final_industry_risk_score` | Final borrower-style score |
| `max_lvr_pct` | Maximum illustrative loan-to-value ratio |
| `review_frequency` | Expected review timing |
| `approval_authority` | Indicative approval level |
| `additional_conditions` | Indicative extra underwriting requirements |

### 7.11 `industry_credit_appetite_strategy.csv`

**Role**

Turn sector risk into an appetite-style portfolio strategy.

**Rules**

| Industry Base Risk Level | Credit Appetite Stance | Max Tenor | Review Frequency |
|---|---|---:|---|
| `Low` | Grow | 7 years | Annual |
| `Medium` | Maintain | 5 years | Annual |
| `Elevated` | Selective | 3 years | Quarterly |
| `High` | Restrict | 2 years | Quarterly |

This table also adds:

- covenant intensity
- collateral expectation
- portfolio action
- ESG flag and focus area
- due-diligence standard

**Columns**

| Column | Meaning |
|---|---|
| `industry` | Sector name |
| `industry_base_risk_level` | Sector risk band |
| `industry_base_risk_score` | Sector score |
| `credit_appetite_stance` | Growth stance: Grow / Maintain / Selective / Restrict |
| `max_tenor_years` | Longest preferred facility tenor |
| `covenant_intensity` | Expected strength of covenant package |
| `collateral_expectation` | Expected security strength |
| `review_frequency` | Target portfolio-review cycle |
| `portfolio_action` | Plain-English action for origination strategy |
| `esg_sensitive_sector` | Whether the sector is flagged for ESG sensitivity |
| `esg_focus_area` | Main ESG topic to watch |
| `due_diligence_standard` | Screening intensity |
| `practice_rationale` | Note explaining the APRA / practice-alignment framing |

### 7.12 `industry_stress_test_matrix.csv`

**Role**

Show how sector scores move under simple scenario shocks.

**Scenario rules**

| Scenario | Added To `macro_risk_score` |
|---|---:|
| `Rate shock` | `+0.35` |
| `Demand shock` | `+0.50` |
| `Margin squeeze` | `+0.45` |
| `Employment decline` | `+0.40` |

**Equations**

```text
stressed_macro_risk_score
= min(5.0, base_macro_risk_score + scenario_severity)
```

```text
stressed_industry_risk_score
= 0.55 × classification_risk_score
+ 0.45 × stressed_macro_risk_score
```

```text
stress_delta
= stressed_industry_risk_score - base_industry_risk_score
```

`implied_monitoring_action`

- `>= 3.5` -> `Escalate sector review`
- `>= 3.0` -> `Maintain heightened monitoring`
- otherwise -> `Monitor through BAU cycle`

**Columns**

| Column | Meaning |
|---|---|
| `industry` | Sector name |
| `scenario_name` | Scenario being applied |
| `base_macro_risk_score` | Current macro score before stress |
| `stressed_macro_risk_score` | Macro score after scenario shock |
| `base_industry_risk_score` | Current base sector score |
| `stressed_industry_risk_score` | Sector score after stress |
| `stress_delta` | Amount the sector score worsens under stress |
| `implied_monitoring_action` | Suggested action after stress |

### 7.13 `industry_esg_sensitivity_overlay.csv`

**Role**

Flag sectors that require additional ESG attention.

**Rule**

The project uses a fixed sector map:

- Agriculture -> climate, water, land use
- Manufacturing -> energy, waste, contamination
- Construction -> contractor practices, embodied carbon, WHS
- Accommodation & Food -> labour practices, energy and waste intensity
- Transport -> transition, emissions, safety

**Columns**

| Column | Meaning |
|---|---|
| `esg_sensitive_sector` | Whether the sector is on the defined ESG-sensitive list |
| `esg_focus_area` | Main ESG issue to watch |
| `credit_policy_overlay` | Policy effect for ESG-sensitive sectors |
| `monitoring_expectation` | Review expectation |
| `source_note` | Reminder that this is a practice-style overlay |

### 7.14 `watchlist_triggers.csv`

**Role**

Highlight sectors needing monitoring attention.

**Trigger rules**

| Trigger | Rule |
|---|---|
| `Negative employment growth` | `employment_yoy_growth_pct < 0` |
| `Declining margin trend` | `margin_trend_score >= 4` |
| `Elevated base risk score` | `industry_base_risk_score >= 3.5` |
| `Extreme signal` | any component score equals `5` |

**Meaning**

This table is not another rating table. It is a monitoring queue.

**Columns**

| Column | Meaning |
|---|---|
| `industry` | Sector name |
| `trigger` | Which monitoring rule was breached |
| `value` | Short evidence line showing the breached value |
| `recommended_action` | Suggested management response |

### 7.15 `chart_table.csv`

**Role**

This is the reporting metadata table used to build the markdown explanations and PDF report.

**Columns**

| Column | Meaning |
|---|---|
| `chart_id` | Chart number used in the report |
| `chart_title` | Display title |
| `chart_file` | Image filename used in the chart pack |
| `source_sheet` | Workbook sheet used to draw the chart |
| `source_workbook` | Workbook file containing the source sheet |
| `source_table` | Primary CSV table behind the chart |
| `metric_basis` | Plain-English note on what the chart measures |

## 8. Which Metrics Work Together To Produce The Final Analysis

This is the most important section for non-technical readers.

### 8.1 The Main Sector Ranking

These metrics work together:

- `cyclical_score`
- `rate_sensitivity_score`
- `demand_dependency_score`
- `external_shock_score`

They create:

```text
classification_risk_score
```

Then these metrics work together:

- `employment_score`
- `margin_level_score`
- `margin_trend_score`
- `inventory_score`
- `demand_score`

They create:

```text
macro_risk_score
```

Then:

```text
industry_base_risk_score
= 0.55 × classification_risk_score
+ 0.45 × macro_risk_score
```

That is the main industry-level analysis.

### 8.2 The Borrower-Style View

These borrower metrics work together:

- `ebitda_margin_score`
- `debt_to_ebitda_score`
- `icr_score`
- `ar_days_score`
- `ap_days_score`
- `inventory_days_score`

They create:

```text
bottom_up_risk_score
```

Then:

```text
final_industry_risk_score
= 0.35 × classification_risk_score
+ 0.30 × macro_risk_score
+ 0.35 × bottom_up_risk_score
```

This is the final borrower-style score used for pricing and policy overlays.

### 8.3 The Working-Capital Interpretation

These do **not** currently change the final score directly, but they help explain risk in more detail:

- `ar_collection_score`
- `ap_supplier_stretch_score`
- `inventory_liquidity_score`
- `cash_conversion_cycle_score`
- `receivables_realisation_score`
- `inventory_stock_build_score`

They create:

- `working_capital_scorecard_overlay_score`
- `working_capital_pd_overlay_score`
- `working_capital_lgd_overlay_score`

In plain English:

- the main score tells you the overall borrower-style risk view
- the working-capital overlays tell you whether the weakness looks more like operating pressure, default pressure, or recoverability pressure

## 9. What Is Still Synthetic Or Assumed

The following items are **not** directly published by the public datasets and are therefore proxy-based or synthetic:

- sector debt / EBITDA benchmark
- sector ICR benchmark
- borrower-level financial statements
- borrower archetype rows
- portfolio exposure mix
- pricing loadings
- credit-policy settings
- concentration limits

That is normal for a structured project like this. The important point is that the assumptions are visible and formula-based, not hidden.

## 10. Final Takeaway

If someone from a non-credit background asks, "What does this project actually do?", the simplest answer is:

> It takes official Australian public datasets, turns them into industry risk signals, builds simple credit-style benchmark ratios and synthetic borrower examples, then converts the results into a portfolio-style risk report with pricing, concentration, monitoring, and working-capital overlays.

If someone asks, "Is this an internal production model?", the correct answer is:

> No. It is an APRA-informed analytical workflow built from public data and transparent proxy rules.
