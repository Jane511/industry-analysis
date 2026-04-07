# Methodology — Data Sources, Derivation Logic, and Output Reference

This document explains every output table produced by the pipeline: what each metric means, which public dataset it comes from, and exactly how it is calculated.

The methodology is designed for portfolio demonstration. It is APRA-informed and bank-inspired, but it does not claim to reproduce any Australian bank's internal industry model, borrower risk grading system, pricing engine, or concentration reporting stack. Where public data does not contain a banking field directly, the pipeline uses transparent proxy logic or synthetic assumptions.

---

## Public Data Sources Used

| ID | Dataset | File | Publisher | Period |
|----|---------|------|-----------|--------|
| **ABS-AI** | Australian Industry 2023-24 | `81550DO001_202324.xlsx` (Table_1) | Australian Bureau of Statistics | FY 2022-23 and FY 2023-24 |
| **ABS-BI-22** | Business Indicators — Gross Operating Profit / Sales Ratio | `56760022_dec2025_profit_ratio.xlsx` (Data1) | ABS | Quarterly time series to Dec 2025 |
| **ABS-BI-23** | Business Indicators — Inventories / Sales Ratio | `56760023_dec2025_inventory_ratio.xlsx` (Data1) | ABS | Quarterly time series to Dec 2025 |
| **ABS-LF** | Labour Force, Australia, Detailed | `6291004_feb2026_labour_force_industry.xlsx` (Data1) | ABS | Monthly time series to Feb 2026 |
| **ABS-BA** | Building Approvals — Non-Residential | `87310051_feb2026_building_approvals_nonres.xlsx` (Data1) | ABS | Monthly time series to Feb 2026 |
| **RBA-F1** | Interest Rates and Yields — Money Market | `rba_f1_data.csv` | Reserve Bank of Australia | Daily to current |

All files are downloaded from publicly available ABS and RBA data portals. URLs are documented in `src/config.py`.

---

## Pipeline Overview

```
ABS Australian Industry ─┬─► Stage 1: Foundation (classification scores)
                          │
ABS Business Indicators ──┤
ABS Labour Force ─────────┼─► Stage 2: Macro View (economic signal scores)
ABS Building Approvals ───┤
RBA Cash Rate ────────────┘
                               │
                               ├─► Stage 3: Benchmarks (generated financial benchmarks)
                               │
                               ├─► Stage 4: Bottom-Up (archetype borrower vs benchmark)
                               │
                               ├─► Stage 5: Scorecard (final weighted risk score)
                               │
                               ├─► Stage 6: Credit Application (pricing, policy, concentration)
                               │
                               ├─► Stage 7: Bank Practice (appetite, stress test, ESG)
                               │
                               └─► Stage 8: Portfolio Monitoring (watchlist triggers)
```

---

## Output Table 1: `industry_classification_foundation.csv`

**Purpose:** Assign structural risk characteristics to each ANZSIC industry division using public financial data.

**Source:** ABS-AI (Table_1) — FY 2022-23 and FY 2023-24

### How the ABS file is parsed

The parser (`load_public_data.parse_australian_industry_totals`) reads Table_1, finds rows starting with "Total" (e.g., "Total Agriculture, Forestry and Fishing"), then reads the three following rows (three fiscal years) to extract: employment ('000), wages ($M), sales ($M), operating profit before tax ($M), EBITDA ($M), and industry value added ($M). From these it calculates:

- `ebitda_margin_pct` = EBITDA / Sales x 100
- `op_profit_margin_pct` = Operating Profit / Sales x 100
- `wages_to_sales_pct` = Wages / Sales x 100

### Metric derivations

| Column | Source | Derivation |


| `cyclical_score` | ABS-AI | Based on **sales growth %** (FY23-24 vs FY22-23). Negative growth = 5, 0-2% = 4, 2-6% = 3, 6-12% = 2, >12% = 1. Captures how volatile the sector's revenue is across business cycles. |

| `rate_sensitivity_score` | ABS-AI | Based on **wage pressure vs margin** = wages_to_sales_pct - ebitda_margin_pct. High wage costs relative to margins mean the sector has less buffer against rate rises. Pressure >25pp = 5, 15-25 = 4, 8-15 = 3, 2-8 = 2, <2 = 1. |

| `demand_dependency_score` | ABS-AI | Signal = wages_to_sales_pct / 8 - sales_growth_pct / 4. High labour intensity combined with weak growth signals dependence on consumer/business demand. >4.5 = 5, 3.5-4.5 = 4, 2.5-3.5 = 3, 1.5-2.5 = 2, <1.5 = 1. |

| `external_shock_score` | ABS-AI | Signal = max(0, 14 - margin) + wages/6 + min(employment/700, 2.5). Combines thin margins (less buffer), high labour costs (workforce disruption risk), and large workforce (scale of impact). >10.5 = 5, 8.5-10.5 = 4, 6.5-8.5 = 3, 4.5-6.5 = 2, <4.5 = 1. |

| `classification_risk_score` | Derived | **Mean** of the four component scores above. |

| `sales_growth_pct_foundation` | ABS-AI | (Sales FY23-24 / Sales FY22-23 - 1) x 100 |

| `ebitda_margin_pct_foundation` | ABS-AI | EBITDA / Sales x 100 for FY 2023-24 |

| `wages_to_sales_pct_foundation` | ABS-AI | Wages / Sales x 100 for FY 2023-24 |

| `employment_000_foundation` | ABS-AI | Employment in thousands for FY 2023-24 |

---

## Output Table 2: `industry_macro_view_public_signals.csv`

**Purpose:** Overlay current economic signals on top of the structural classification to detect which sectors are improving or deteriorating.

**Sources:** ABS-AI, ABS-BI-22, ABS-BI-23, ABS-LF, ABS-BA, RBA-F1

### Metric derivations

| Column | Source | Derivation |
|--------|--------|------------|
| `sales_m_latest` | ABS-AI | Total sales/service income ($M) for FY 2023-24 |

| `employment_000_latest` | ABS-AI | Employment at end of June 2024 ('000) |

| `ebitda_margin_pct_latest` | ABS-AI | EBITDA / Sales x 100 for FY 2023-24 |

| `ebitda_margin_change_pctpts` | ABS-AI | EBITDA margin FY23-24 minus EBITDA margin FY22-23 (percentage point change) |

| `sales_growth_pct` | ABS-AI | (Sales FY23-24 / Sales FY22-23 - 1) x 100 |

| `wages_to_sales_pct_latest` | ABS-AI | Wages / Sales x 100 for FY 2023-24 |

| `gross_operating_profit_to_sales_ratio_latest` | ABS-BI-22 | Most recent quarterly value from the time series. The ABS file has column headers in the format "Series ID ; Industry ; Measure". The parser extracts the industry name from the third semicolon-delimited segment, reads all quarterly data, and takes the latest non-null observation. |

| `gross_operating_profit_to_sales_ratio_yoy_change` | ABS-BI-22 | Latest value minus the value from 12 months earlier in the same time series. |

| `inventories_to_sales_ratio_latest` | ABS-BI-23 | Same parsing logic as ABS-BI-22, applied to the inventories/sales ratio file. Latest quarterly observation. |

| `inventories_to_sales_ratio_yoy_change` | ABS-BI-23 | Latest value minus value from 12 months prior. |

| `employment_yoy_growth_pct` | ABS-LF | The parser reads monthly Trend series by industry division. For each industry: (latest month's employment / employment 12 months earlier - 1) x 100. |

| `demand_proxy_building_type` | ABS-BA | Each industry is mapped to a non-residential building type (e.g., Construction → "Total Non-residential", Retail → "Retail and wholesale trade buildings", Health Care → "Health buildings"). This mapping is defined in `build_macro_view.py`. |

| `demand_yoy_growth_pct` | ABS-BA | For the mapped building type: (latest month's approval value / value 12 months earlier - 1) x 100. Acts as a forward-looking demand proxy. |

| `cash_rate_latest_pct` | RBA-F1 | The "Cash Rate Target" column from the most recent row in the RBA CSV. |

| `cash_rate_change_1y_pctpts` | RBA-F1 | Latest cash rate minus the cash rate from 12 months earlier. |

### Scoring (all on 1-5 scale, 1 = low risk, 5 = high risk)

| Score Column | Input | Thresholds |
|-------------|-------|------------|
| `employment_score` | `employment_yoy_growth_pct` | <0% = 5, 0-1% = 4, 1-2.5% = 3, 2.5-4% = 2, >4% = 1. Missing = 3. |
| `margin_level_score` | `gross_operating_profit_to_sales_ratio_latest` (fallback: `ebitda_margin_pct_latest`) | <8% = 5, 8-12% = 4, 12-18% = 3, 18-25% = 2, >25% = 1. Handles both ratio (0-1) and percentage (0-100) scales. Missing = 3. |
| `margin_trend_score` | `gross_operating_profit_to_sales_ratio_yoy_change` (fallback: `ebitda_margin_change_pctpts`) | Large decline = 5, decline = 4, flat = 3, improvement = 2, strong improvement = 1. Handles both ratio and percentage scales. Missing = 3. |
| `inventory_score` | `inventories_to_sales_ratio_latest` | >0.70 = 5, 0.50-0.70 = 4, 0.30-0.50 = 3, 0.15-0.30 = 2, <0.15 = 1. Missing = 3. |
| `demand_score` | `demand_yoy_growth_pct` | <-20% = 5, -20% to -5% = 4, -5% to +5% = 3, 5-20% = 2, >20% = 1. Missing = 3. |

### Composite scores

| Column | Derivation |
|--------|------------|
| `macro_risk_score` | Mean of the 5 component scores above |
| `industry_base_risk_score` | **55%** x classification_risk_score + **45%** x macro_risk_score |
| `industry_base_risk_level` | Low (score ≤ 2.0), Medium (≤ 3.0), Elevated (≤ 4.0), High (> 4.0) |

---

## Output Table 3: `industry_base_risk_scorecard.csv`

**Purpose:** Summary view of the 9 industries ranked by base risk score, combining classification and macro dimensions.

This is a filtered view of `industry_macro_view_public_signals.csv` sorted by `industry_base_risk_score` descending. All columns are derived in Stages 1 and 2 above.

| Column | Source stage |
|--------|-------------|
| `industry` | Stage 1 |
| `classification_risk_score` | Stage 1 (mean of 4 structural scores) |
| `macro_risk_score` | Stage 2 (mean of 5 signal scores) |
| `industry_base_risk_score` | Stage 2 (55/45 blend) |
| `industry_base_risk_level` | Stage 2 (risk band mapping) |
| `employment_yoy_growth_pct` | Stage 2 from ABS-LF |
| `ebitda_margin_pct_latest` | Stage 2 from ABS-AI |
| `gross_operating_profit_to_sales_ratio_latest` | Stage 2 from ABS-BI-22 |
| `inventories_to_sales_ratio_latest` | Stage 2 from ABS-BI-23 |
| `demand_proxy_building_type` | Stage 2 mapping to ABS-BA building type |
| `demand_yoy_growth_pct` | Stage 2 from ABS-BA |
| `cash_rate_latest_pct` | Stage 2 from RBA-F1 |
| `cash_rate_change_1y_pctpts` | Stage 2 from RBA-F1 |

---

## Output Table 4: `industry_public_benchmarks.csv`

**Purpose:** Public macro metrics for each sector without risk scores — useful as a standalone reference table.

All columns are direct extracts from Stage 2 (see Table 2 above for sources). No additional derivation.

---

## Output Table 5: `industry_generated_benchmarks.csv`

**Purpose:** Generate financial benchmark proxies (leverage, coverage, working capital) for each industry using public data and deterministic bank-style estimation rules, since public data does not directly provide banking ratios like Debt/EBITDA or ICR.

**Source:** Stage 2 macro view (which itself comes from ABS-AI, ABS-BI-22, ABS-BI-23)

### Metric derivations

| Column | Primary Source | Derivation |
|--------|---------------|------------|
| `ebitda_margin_pct_latest` | ABS-AI or ABS-BI-22 | Direct from Stage 2. Priority: gross operating profit/sales ratio, then EBITDA margin. Converted to percentage if provided as ratio. |
| `inventory_days_benchmark` | ABS-BI-23 | **If inventory ratio available:** inventory_to_sales_ratio x 365 / COGS_ratio, where COGS_ratio = clip(1 - margin, 0.45, 0.95). **If not available:** estimated from wages ratio and demand growth — base 20 days, minus wage intensity effect, plus demand-decline adjustment. Clipped to 5-90 days. |
| `ar_days_benchmark` | Derived | 18 + (inventory_days x 0.22) + (classification_risk_score x 3.2) - (profit_margin x 0.35). For low-receivable sectors (Retail, Accommodation), result is multiplied by 0.35 (cash/card-based businesses collect faster). Clipped to 5-75 days. |
| `ap_days_benchmark` | Derived | 24 + (inventory_days x 0.18) + (macro_risk_score x 2.5) - (profit_margin x 0.20). Clipped to 20-70 days. |
| `debt_to_ebitda_benchmark` | Derived | 1.2 + max(0, 18 - profit_margin) x 0.07 + classification_risk_score x 0.22 + macro_risk_score x 0.12 + inventory_days / 120. Lower-margin, higher-risk, inventory-heavy sectors carry more debt relative to earnings. Clipped to 1.5-4.5x. |
| `icr_benchmark` | Derived | 5.3 - (debt_to_ebitda x 0.75) + (profit_margin x 0.04) - (classification_risk_score - 3) x 0.10. Higher leverage means lower coverage; higher margins provide more earnings buffer. Clipped to 1.5-4.5x. |

**Design rationale:** These benchmarks use publicly observable industry characteristics (margins, inventory intensity, risk scores) as inputs to deterministic rules that approximate the type of sector benchmarking logic a bank credit team might use. They are not statistical estimates, observed bank benchmarks, or validated internal policy settings.

---

## Output Table 6: `borrower_benchmark_comparison.csv`

**Purpose:** Generate one synthetic borrower archetype per industry, then score their financial ratios against the industry benchmark proxies from Table 5.

**Source:** Stage 2 macro view + Stage 3 benchmarks

### Archetype borrower generation

Each borrower is constructed as a synthetic "stressed version" of the industry benchmark proxy, simulating a borrower that is slightly weaker than the sector average:

| Borrower field | Derivation |
|---------------|------------|
| `revenue` | Industry total sales / 40,000 (scaled to a single mid-market company), clipped to $6M-$22M |
| `ebitda` | Revenue x margin, where margin = max(2%, EBITDA_margin - stress x 3.2) |
| `total_debt` | EBITDA x debt_to_ebitda_benchmark x (1 + stress x 0.22) |
| `interest_expense` | EBITDA / ICR, where ICR = max(1.1, ICR_benchmark - stress x 0.45) |
| `accounts_receivable` | Revenue x AR_days / 365, where AR_days = benchmark x (1 + stress x 0.10) |
| `accounts_payable` | COGS x AP_days / 365, where AP_days = benchmark x (1 + stress x 0.06) |
| `inventory` | COGS x inventory_days / 365, where inventory_days = benchmark x (1 + stress x 0.12) |

Where **stress factor** = max(0.15, (classification_score + macro_score) / 2 - 2.2) / 4. Higher-risk sectors generate borrowers that deviate further from benchmarks.

### Gap scoring (1-5 scale)

| Score column | Metric compared | Logic |
|-------------|----------------|-------|
| `ebitda_margin_score` | Actual margin vs industry EBITDA margin | "Lower is worse": ≥5pp above = 1, at benchmark = 2, up to 5pp below = 3, up to 10pp below = 4, >10pp below = 5 |
| `debt_to_ebitda_score` | Actual D/E vs benchmark | "Higher is worse": at or below = 1, up to 15% above = 2, up to 35% = 3, up to 60% = 4, >60% above = 5 |
| `icr_score` | Actual ICR vs benchmark | ≥benchmark+1.5x = 1, at benchmark = 2, down to -0.5x = 3, down to -1.0x = 4, lower = 5 |
| `ar_days_score` | Actual vs benchmark | Same "higher is worse" gap logic as D/E |
| `ap_days_score` | Actual vs benchmark | Same logic |
| `inventory_days_score` | Actual vs benchmark | Same logic |
| `bottom_up_risk_score` | — | **Mean** of the 6 scores above |

---

## Output Table 7: `borrower_industry_risk_scorecard.csv`

**Purpose:** Final integrated risk score combining all three risk dimensions.

### Final score derivation

```
final_industry_risk_score = 35% x classification_risk_score
                          + 30% x macro_risk_score
                          + 35% x bottom_up_risk_score
```

| Weight | Component | What it captures |
|--------|-----------|-----------------|
| 35% | Classification | Structural industry characteristics (cyclicality, rate sensitivity, demand dependency, external shock) |
| 30% | Macro | Current economic signals (employment, margins, inventory, demand, cash rate) |
| 35% | Bottom-up | Synthetic borrower financial health relative to sector benchmark proxies |

**Risk level mapping:**

| Score | Band | Meaning |
|-------|------|---------|
| ≤ 2.0 | Low | Structurally resilient sector, strong macro signals, borrower outperforming |
| 2.0 - 3.0 | Medium | Moderate sector risk, mixed signals, borrower near benchmark |
| 3.0 - 4.0 | Elevated | Structural weaknesses, deteriorating signals, or borrower underperforming |
| > 4.0 | High | High structural risk, weak macro, and significant borrower stress |

---

## Output Table 8: `industry_portfolio_proxy.csv`

**Purpose:** Estimate a proxy portfolio exposure mix using public economic data, since actual bank portfolio data is not public.

**Source:** ABS-AI (sales and employment by industry)

### Derivation

```
current_exposure_pct = (70% x sales_share + 30% x employment_share) x 100
```

Where:
- `sales_share` = industry sales / total sales across all 9 industries (from ABS-AI FY 2023-24)
- `employment_share` = industry employment / total employment across all 9 industries (from ABS-AI FY 2023-24)

**Rationale:** Bank lending broadly tracks economic activity. Sales share reflects revenue-generating capacity (drives borrowing demand); employment share reflects workforce scale (correlated with business count and loan volume). The 70/30 weighting tilts toward revenue as the primary driver of credit demand.

---

## Output Table 9: `concentration_limits.csv`

**Purpose:** Compare the proxy portfolio exposure to illustrative risk-based concentration limits.

**Sources:** Stage 2 (risk levels) + Table 8 (portfolio proxy)

| Column | Derivation |
|--------|------------|
| `concentration_limit_pct` | Mapped from industry base risk level: Low = 25%, Medium = 20%, Elevated = 15%, High = 10%. This is an illustrative policy grid, not an observed bank concentration framework. |
| `current_exposure_pct` | From Table 8 (portfolio proxy) |
| `headroom_pct` | Limit - current exposure |
| `breach` | True if current exposure exceeds the limit |
| `utilisation_pct` | (Current exposure / limit) x 100 |

---

## Output Table 10: `pricing_grid.csv`

**Purpose:** Translate borrower risk levels into illustrative lending rates.

**Source:** Stage 5 scorecard (risk levels) + RBA-F1 (cash rate)

### Rate calculation

```
all_in_rate = cash_rate + base_margin + industry_loading
```

| Component | Source / Rule |
|-----------|-------------|
| `cash_rate_pct` | RBA-F1 latest cash rate target |
| `base_margin_pct` | Fixed at 2.50% (illustrative policy assumption) |
| `industry_loading_pct` | Mapped from risk level: Low = +0.00%, Medium = +0.25%, Elevated = +0.50%, High = +1.00%. This does not represent an internal bank pricing model. |
| `indicative_rate_pct` | base_margin + industry_loading (rate above cash rate) |
| `all_in_rate_pct` | cash_rate + indicative_rate (total borrower rate) |

---

## Output Table 11: `policy_overlay.csv`

**Purpose:** Define credit policy restrictions for each borrower based on their industry risk level.

**Source:** Stage 5 scorecard (risk levels)

| Risk Level | Max LVR | Review Frequency | Approval Authority | Additional Conditions |
|-----------|---------|-------------------|--------------------|-----------------------|
| Low | 80% | Annual | Standard delegated authority | None |
| Medium | 75% | Annual | Standard delegated authority | Industry section in credit memo required |
| Elevated | 65% | Semi-annual | Senior credit officer | Enhanced due diligence; stress-test cash flows |
| High | 50% | Quarterly | Credit committee | New lending subject to committee approval; mandatory collateral revaluation |

No public data is used directly. The rules are bank-style policy mappings applied to the risk levels derived from public data, intended to illustrate how sector risk can feed downstream approval settings.

---

## Output Table 12: `industry_credit_appetite_strategy.csv`

**Purpose:** Define a credit appetite framework for each sector, aligned to APRA prudential themes and public Australian bank disclosures.

**Source:** Stage 2 (industry base risk levels)

| Column | Derivation |
|--------|------------|
| `credit_appetite_stance` | Mapped from risk level: Low = "Grow", Medium = "Maintain", Elevated = "Selective", High = "Restrict" |
| `max_tenor_years` | Low = 7, Medium = 5, Elevated = 3, High = 2 |
| `covenant_intensity` | Low = "Standard", Medium = "Standard plus trigger monitoring", Elevated = "Enhanced covenant package", High = "Full covenant package with hard triggers" |
| `collateral_expectation` | Graduated from "Normal security standards" to "Cash dominion or strong collateral support expected" |
| `review_frequency` | Elevated and High = "Quarterly", Low and Medium = "Annual" |
| `esg_sensitive_sector` | True for Agriculture, Manufacturing, Construction, Accommodation, Transport (based on a defined sector map) |
| `esg_focus_area` | Specific ESG themes per sector (e.g., Agriculture = "Climate variability, water stress, land use") |

---

## Output Table 13: `industry_stress_test_matrix.csv`

**Purpose:** Test how each industry's risk score would change under four adverse scenarios.

**Source:** Stage 2 macro risk scores

### Scenarios

| Scenario | Shock applied to macro_risk_score |
|----------|----------------------------------|
| Rate shock | +0.35 |
| Employment decline | +0.40 |
| Margin squeeze | +0.45 |
| Demand shock | +0.50 |

These are simplified score shocks rather than full severe-but-plausible stress tests built from borrower cash flows or portfolio systems.

### Derivation

```
stressed_macro_risk_score = min(5.0, base_macro_risk_score + severity)
stressed_industry_risk_score = 55% x classification_risk_score + 45% x stressed_macro_risk_score
stress_delta = stressed_industry_risk_score - base_industry_risk_score
```

### Monitoring action mapping

| Stressed score | Action |
|---------------|--------|
| ≥ 3.5 | Escalate sector review |
| ≥ 3.0 | Maintain heightened monitoring |
| < 3.0 | Monitor through BAU cycle |

---

## Output Table 14: `industry_esg_sensitivity_overlay.csv`

**Purpose:** Flag sectors with elevated environmental, social, or governance risk that require additional credit review.

**Source:** Defined sector mapping (not data-driven)

| Sector | ESG Focus Area |
|--------|---------------|
| Agriculture | Climate variability, water stress, land use |
| Manufacturing | Energy intensity, waste, contamination |
| Construction | Contractor practices, embodied carbon, WHS |
| Accommodation & Food | Labour practices, energy and waste intensity |
| Transport | Fuel transition, fleet emissions, safety |
| All others | No elevated sector overlay |

ESG-sensitive sectors get "Enhanced ESG due diligence" at origination and annual review. Non-sensitive sectors receive "Standard ESG screening". This is a static sector overlay, not a substitute for transaction-level ESG review.

---

## Output Table 15: `watchlist_triggers.csv`

**Purpose:** Flag sectors that trip early-warning indicators requiring monitoring attention.

**Source:** Stage 2 macro view (scores and raw metrics)

### Trigger rules

| Trigger | Condition | Source metric |
|---------|-----------|--------------|
| Negative employment growth | `employment_yoy_growth_pct` < 0 | ABS-LF |
| Declining margin trend | `margin_trend_score` ≥ 4 | ABS-BI-22 / ABS-AI |
| Elevated base risk score | `industry_base_risk_score` ≥ 3.5 | Composite (Stage 2) |
| Extreme signal | Any of the 5 component scores = 5 | ABS-LF, ABS-BI-22, ABS-BI-23, ABS-BA |

Each trigger includes a `recommended_action` (e.g., "Review sector exposure", "Request updated financials", "Escalate to credit committee").

---

## Data Flow Summary

```
┌──────────────────────────────────────────────────────────────┐
│                    PUBLIC DATA SOURCES                        │
├──────────────┬──────────────┬─────────┬──────────┬───────────┤
│  ABS         │  ABS         │ ABS     │ ABS      │ RBA       │
│  Australian  │  Business    │ Labour  │ Building │ Cash Rate │
│  Industry    │  Indicators  │ Force   │ Approvals│ F1        │
│  (8155.0)    │  (5676.0)    │(6291.0) │ (8731.0) │           │
└──────┬───────┴──────┬───────┴────┬────┴─────┬────┴─────┬─────┘
       │              │            │          │          │
       ▼              │            │          │          │
  ┌─────────┐         │            │          │          │
  │ Stage 1 │         │            │          │          │
  │Foundation│         │            │          │          │
  │ 4 scores │         │            │          │          │
  └────┬─────┘         │            │          │          │
       │               ▼            ▼          ▼          ▼
       │         ┌───────────────────────────────────────────┐
       └────────►│              Stage 2: Macro View          │
                 │  5 signal scores + base risk score        │
                 └──────┬──────────────┬────────────────┬────┘
                        │              │                │
                        ▼              ▼                ▼
                 ┌────────────┐ ┌────────────┐  ┌──────────────┐
                 │  Stage 3   │ │  Stage 8   │  │   Stage 7    │
                 │ Benchmarks │ │ Monitoring │  │Bank Practice │
                 │ (D/E, ICR, │ │ (watchlist)│  │(appetite,    │
                 │ AR/AP/Inv) │ │            │  │ stress, ESG) │
                 └─────┬──────┘ └────────────┘  └──────────────┘
                       │
                       ▼
                 ┌────────────┐
                 │  Stage 4   │
                 │ Bottom-Up  │
                 │(archetypes │
                 │ vs bench.) │
                 └─────┬──────┘
                       │
                       ▼
                 ┌────────────┐
                 │  Stage 5   │
                 │ Scorecard  │
                 │ (35/30/35) │
                 └─────┬──────┘
                       │
                       ▼
                 ┌──────────────┐
                 │   Stage 6    │
                 │Credit Appln. │
                 │(pricing,     │
                 │ policy,      │
                 │ concentration│
                 └──────────────┘
```

---

## Transparency Notes

1. **No manual input folder is required.** The live pipeline runs from downloaded public ABS/RBA files plus explicit workbook-held banking assumptions documented in the reporting pack.

2. **Benchmark estimation is deterministic, not statistical.** Where public data does not provide a banking metric directly (e.g., Debt/EBITDA, ICR, AR/AP/Inventory days), the pipeline uses transparent rule-based formulas that combine available public signals (margins, risk scores, inventory ratios) into plausible industry benchmark proxies. These rules are documented in `src/build_benchmarks.py`.

3. **Archetype borrowers are synthetic.** The bottom-up borrower profiles are generated from industry data, not from real company financials. They represent illustrative mid-market borrower archetypes in each sector, stressed slightly below the benchmark proxy to simulate a credit assessment scenario.

4. **Scoring thresholds are fixed policy rules.** The 1-5 scoring bands for each metric (e.g., employment growth, margin level) are defined as deterministic threshold tables in `src/utils.py`. They do not change with the data. They are illustrative policy settings used for consistency, not observed internal bank thresholds.

5. **All weights are explicit.** Classification vs Macro = 55/45. Final score = 35% Classification + 30% Macro + 35% Bottom-Up. These weights are hardcoded and documented.
