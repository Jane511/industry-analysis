# Output Data Provenance

## Directly sourced from Australian public datasets

The following output fields are directly loaded from ABS or RBA files already present in `data/raw/public`:

- `industry_public_benchmarks.csv`
  - `ebitda_margin_pct_latest`
  - `ebitda_margin_change_pctpts`
  - `gross_operating_profit_to_sales_ratio_latest`
  - `gross_operating_profit_to_sales_ratio_yoy_change`
  - `inventories_to_sales_ratio_latest`
  - `inventories_to_sales_ratio_yoy_change`
  - `employment_yoy_growth_pct`
  - `demand_proxy_building_type`
  - `demand_yoy_growth_pct`
- `industry_base_risk_scorecard.csv`
  - `employment_yoy_growth_pct`
  - `ebitda_margin_pct_latest`
  - `gross_operating_profit_to_sales_ratio_latest`
  - `inventories_to_sales_ratio_latest`
  - `demand_proxy_building_type`
  - `demand_yoy_growth_pct`
  - `cash_rate_latest_pct`
  - `cash_rate_change_1y_pctpts`

## Deterministically derived from Australian public datasets

These outputs use rules, scorecards, or transformations built from public ABS/RBA data rather than direct published series:

- `industry_classification_foundation.csv`
  - `cyclical_score`
  - `rate_sensitivity_score`
  - `demand_dependency_score`
  - `external_shock_score`
  - `classification_risk_score`
- `industry_base_risk_scorecard.csv`
  - `macro_risk_score`
  - `industry_base_risk_score`
  - `industry_base_risk_level`
  - `inventory_days_est`
  - `inventory_days_yoy_change`
  - `inventory_stock_build_risk`
- `industry_generated_benchmarks.csv`
  - `inventory_days_benchmark`
  - `inventory_days_yoy_change`
  - `inventory_stock_build_risk`
  - `inventory_days_benchmark_source`
  - `debt_to_ebitda_benchmark`
  - `icr_benchmark`
- `industry_public_benchmarks.csv`
  - `inventory_days_est`
  - `inventory_days_yoy_change`
  - `inventory_stock_build_risk`
  - `inventory_days_est_source`
- `industry_portfolio_proxy.csv`
  - `current_exposure_pct`
- `concentration_limits.csv`
  - `risk_level`
  - `industry_base_risk_score`
  - `concentration_limit_pct`
  - `headroom_pct`
  - `breach`
  - `utilisation_pct`
- `watchlist_triggers.csv`
  - all rows are derived from public-data signals using trigger rules

## Generated because public datasets do not provide the banking field directly

The following outputs rely on generated data because no borrower-specific public dataset or bank policy dataset is included in the repo:

- `borrower_benchmark_comparison.csv`
  - `borrower_name`
  - `revenue`
  - `ebitda`
  - `total_debt`
  - `interest_expense`
  - `accounts_receivable`
  - `accounts_payable`
  - `inventory`
  - `cogs_or_purchases`
  - `ebitda_margin_pct`
  - `debt_to_ebitda`
  - `icr`
  - `ar_days`
  - `ap_days`
  - `inventory_days`
  - all borrower-level score columns
  - `bottom_up_risk_score`
- `borrower_industry_risk_scorecard.csv`
  - all borrower rows
  - `bottom_up_risk_score`
  - `final_industry_risk_score`
  - `risk_level`
- `pricing_grid.csv`
  - all borrower rows
  - `base_margin_pct`
  - `industry_loading_pct`
  - `indicative_rate_pct`
  - `all_in_rate_pct`
- `policy_overlay.csv`
  - all borrower rows
  - `max_lvr_pct`
  - `review_frequency`
  - `approval_authority`
  - `additional_conditions`

## Dataset gap assessment

No currently referenced source files are missing for the direct public metrics already used by the pipeline.

The remaining generated fields are not missing because of absent downloads. They are generated because the required fields are not published in the current free public-data layer used by this project:

- borrower-level financial statements by sector sample
- sector debt / EBITDA benchmarks
- sector interest coverage benchmarks
- sector AP day benchmarks when PTRS is unavailable
- true bank portfolio exposure by sector
- bank pricing grids
- bank policy overlays

## Public PTRS proxy layer after official source reconstruction

When the official PTRS publications are downloaded and reconstructed into `data/raw/public/ptrs/PTRS_MultiCycle_AR_Days_Model_Official.xlsx`, the following fields are sourced from official Payment Times Reporting Scheme publications rather than from the generic benchmark formula:

- `industry_generated_benchmarks.csv`
  - `ar_days_benchmark`
  - `ar_days_stress_benchmark`
  - `ar_days_severe_benchmark`
  - `ap_days_benchmark`
  - `ap_days_stress_benchmark`
  - `ap_days_severe_benchmark`
  - `ptrs_cycle8_avg_payment_days`
  - `ptrs_cycle9_avg_payment_days`
  - `ptrs_cycle8_paid_on_time_pct`
  - `ptrs_cycle9_paid_on_time_pct`
  - `ptrs_latest_cycle_used`
