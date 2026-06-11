# Methodology Manual — Property-Backed Lending Overlays

> **Real-data-only update:** the engine runs on real public data only (ABS / RBA / PTRS); all synthetic/staged data has been removed. The `industry_failure_rates`, `property_market_detail`, and `macro_context` exports were **removed** because they cannot be built from real data without staging extra sources (ASIC Series 1A insolvencies + ABS Cat. 8165.0; ABS residential property price indexes; ABS CPI/PPI). Sections below describing those exports are retained as forward-looking methodology but are **not currently built** — see the README "Not included (pending real data)" note.

## 1) Purpose

This manual explains how `industry-analysis` builds public-data overlays for **property-backed commercial lending** (for example, investment property, bridging, development, and construction-related credit where collateral and market conditions are central).

Plain-English summary: the repo converts public property-cycle and macro context into reusable overlay tables so downstream LGD/PD/stress/pricing repos can apply consistent assumptions.

---

## 2) How this repo fits into the overall system

`industry-analysis` is the upstream overlay/data-conditioning layer.

It produces:
- property-cycle panels
- region/segment risk signals
- macro-regime and arrears environment context
- property-market overlays
- downturn scenario overlay tables
- realised insolvency rates per ANZSIC division (cross-sector validation anchor)
- per-ANZSIC industry financial-ratio benchmarks (APG 220 paragraph 64) — used by property-borrower scorecards alongside collateral signals
- contract exports under `data/exports/` (six core + three optional explainability panels)

Downstream repos use these tables for:
- collateral stress assumptions
- downturn scenario conditioning
- conservative policy overlays in borrower-level models
- borrower-vs-industry ratio scoring for the operating company that owns the property

It does **not** perform:
- borrower/facility model fitting
- valuation engine logic
- final lending policy decisioning
- enterprise stress engine orchestration

---

## 3) Basic credit concepts (beginner-friendly)

### What is property-backed lending?
Property-backed lending relies partly on property collateral value and market liquidity, not only borrower cash flow.
Examples: development finance, bridging finance, investment property lending.

### Why property + macro data matters
Property risk changes with:
- construction pipeline and approvals momentum
- financing conditions (interest-rate backdrop)
- arrears environment
- segment-specific softness (for example offices vs industrial)

### Why industry-relative borrower ratios still matter for property-backed lending
Even where collateral is the primary repayment source, APG 220 paragraph 64 expects ADIs to compare borrower financial ratios (interest coverage, gearing, leverage) to **relevant industry benchmarks**. For property-backed deals, "the borrower's industry" is often Construction (Division E), Rental/Hiring/Real Estate Services (Division L), or the operating sector that occupies the asset (Retail, Industrial, Healthcare). The repo's `industry_financial_benchmarks` contract publishes the per-ANZSIC reference values that origination scorecards use to evaluate the borrower's ratios — so property-backed lending teams have the same APG-220-aligned reference points as cash-flow-lending teams, applied to the operating-company side of the deal.

### What are panels and overlays here?
- **Property-cycle panel**: explains cycle stage and softness by segment.
- **Property-market overlays**: compact risk indicators for downstream use.
- **Downturn overlays**: scenario multipliers/haircuts for stress interpretation.
- **Industry financial benchmarks**: per-ANZSIC reference medians for borrower-ratio comparison.

---

## 4) Public datasets used (very important)

| Source | Dataset | What it measures | Why it matters for property-backed lending | How used in repo |
|---|---|---|---|---|
| ABS | Building Approvals — Non-residential (`87310051...`) | Forward approvals trend by building type | Early cycle signal for supply/demand and development activity | Core approvals trend input for property cycle and region/segment risk |
| ABS (optional staged) | Building Activity extract | Commencements/completions confirmation | Validates whether approvals are translating into real pipeline activity | Enhances cycle signal quality; otherwise repo uses explicit approvals proxy |
| ABS (optional staged) | Lending Indicators extract | Finance demand momentum | Context for market financing conditions | Enhances region/segment finance signal; otherwise cash-rate proxy used |
| ABS | Australian Industry (`81550DO001...`) | Annual sector sales, employment, wages, profit, EBITDA | Operating-company financial profile per ANZSIC division | Source for `median_ebitda_margin_pct`, `median_wages_to_sales_pct`, `median_sales_growth_pct`, `median_sales_per_employee_thousands` in `industry_financial_benchmarks` |
| ABS | Business Indicators (`56760022/23...`) | Quarterly profit-to-sales and inventory ratios | Operating-company working-capital and earnings benchmarks | Source for `median_gross_operating_profit_to_sales_ratio`, `median_inventory_to_sales_ratio`, `median_inventory_days_est` |
| ABS | Labour Force by industry (`6291004...`) | Employment trend by industry | Operating-company employment momentum | Source for `median_employment_yoy_growth_pct` |
| ABS | Counts of Australian Businesses (Cat. 8165.0) | Active business counts per ANZSIC division | Denominator for industry failure rates | Backing series for `industry_failure_rates.active_businesses` |
| RBA | F1 cash-rate table (`rba_f1_data.csv`) | Current cash-rate level and 1-year change | Funding-cost and serviceability pressure backdrop | Cash-rate summary, regime derivation, fallback trend proxy |
| RBA (optional staged) | Housing arrears context extract | Qualitative arrears environment | Early stress context for collateral-linked portfolios | Arrears environment construction |
| APRA (optional staged) | Property/banking context extract | Supervisory context notes | Adds prudential context to property risk interpretation | Appended to arrears/macro notes |
| ASIC | Series 1A insolvency statistics | Companies entering external administration, by ANZSIC | Realised stress signal — particularly important for Construction (Division E) where builder collapses drive collateral-completion risk | Numerator for `industry_failure_rates.failure_rate_pct` (TTM) |
| PTRS regulator publications | Payment timing by industry | Supplier/customer payment behavior proxy | Supports broader downturn narrative and overlays | Used in repo-wide overlay context (not a direct property valuation series) |

---

## 5) Derived information created from public data (critical)

### A) Property cycle panel (`property_cycle_panel`)
- **Purpose**: summarize current cycle position for property segments.
- **Inputs**: approvals + optional activity + cash-rate context + structural segment sensitivity.
- **High-level logic**:
  - compute approvals change and momentum
  - add commencements/completions signal when available
  - fallback to approvals proxy when activity is missing (explicitly labeled)
  - blend trend signals into cycle stage and softness score
- **Output meaning**: segment-level cycle direction and softness context.

### B) Region/segment risk logic (embedded in panel build)
- **Purpose**: provide reusable risk bands for segment/region joins.
- **Inputs**: approvals + optional activity + optional lending + cash-rate fallback.
- **High-level logic**:
  - combine structural sensitivity with trend/funding proxies
  - generate `region_risk_score` and band
  - keep source notes explicit on proxy paths
- **Output meaning**: practical overlay for collateral and policy conservatism by segment.

### C) Macro regime flags (`macro_regime_flags`)
- **Purpose**: label overall environment that affects collateral stress severity.
- **Inputs**: cash-rate summary + optional arrears/APRA context.
- **High-level logic**: map level/trend/qualitative arrears to regime labels and watch flags.
- **Output meaning**: one-row regime control table used by downstream models.

### D) Property market overlays (`property_market_overlays`)
- **Purpose**: compact table for downstream systems.
- **Inputs**: property-cycle panel.
- **High-level logic**: publish key cycle and risk fields plus normalized softness band.
- **Output meaning**: easy-to-join overlay output for property-linked portfolios. Exactly five rows — one per canonical `property_segment_code` (`RES`, `CRE`, `IND`, `RET`, `CON`). Pre-aggregation per-building-type detail is published separately on `property_market_overlays_by_building_type`.

### E) Downturn overlay table (`downturn_overlay_table`)
- **Purpose**: scenario table for property-linked stress assumptions.
- **Inputs**: arrears environment + property-cycle softness.
- **High-level logic**:
  - anchor scenario severity to current softness and arrears backdrop
  - produce base/mild/moderate/severe rows
  - output multiplier/haircut fields transparently (PD ×, LGD ×, CCF ×, property value haircut)
- **Output meaning**: scenario assumptions table for downstream stress interpretation; not a calibrated regulatory capital model. Tested invariants: base scenario = 1.0 across all multipliers, monotonic base ≤ mild ≤ moderate ≤ severe.

### F) Industry failure rates (`industry_failure_rates`)
- **Purpose**: realised insolvency rate per ANZSIC division. Especially relevant for property-backed lending in Construction (E) and Rental/Hiring/Real Estate Services (L) — sector-specific stress in these divisions directly affects collateral-completion risk on development and investment-property exposures.
- **Inputs**: ASIC Series 1A insolvency counts ÷ ABS Cat. 8165.0 active-business counts.
- **High-level logic**: compute trailing-twelve-month insolvency count per division, divide by active businesses, also publish year-on-year change in the rate.
- **Output meaning**: current-state validation anchor that cross-checks the assumed Construction stress level against realised builder-insolvency experience.

### G) Industry financial benchmarks (`industry_financial_benchmarks`)
- **Purpose**: per-ANZSIC-division medians of the financial ratios APG 220 paragraph 64 calls out as the standard credit-assessment benchmarks. Used in property-backed lending for the operating-company side of the deal — borrower's interest coverage, gearing, leverage, and other ratios are compared to the medians for the borrower's ANZSIC division.
- **Inputs**: business cycle panel only — no new ABS catalogues required. The benchmark builder is a thin re-shaping of values already derived for the macro_risk_score.
- **Published medians**: EBITDA margin, gross operating profit-to-sales, wages-to-sales, inventory days, sales growth, employment growth, inventory-to-sales, sales per employee. See `README_technical.md` for the full column-by-column schema.
- **Method label**: every value is published with an explicit method note flagging it as an ABS aggregate (industry-weighted; closest public proxy for industry median), not a firm-level distribution median.
- **Out of scope** (deliberate, future passes): per-industry p25/p75 percentiles; sub-sector/subdivision granularity; computed ratios needing firm-level inputs (DSCR, current ratio, debtor/creditor days, net-debt-to-EBITDA).

---

## 6) Segment-specific methodology — property-backed lending

### How property + macro + region data is used
Property-backed lending teams need collateral-aware context:
- are segments in growth, neutral, slowing, or downturn phase?
- is financing backdrop restrictive or easing?
- are signs of market softness concentrated in specific segments?

The repo answers these via:
- cycle stage labels
- market softness scores/bands
- region/segment risk scoring
- macro regime flags
- downturn scenario overlays

For the **operating-company side** of property-backed deals (the lessee in commercial real estate, the construction company on a development, the property developer on a build-to-sell), the repo additionally provides:
- `industry_financial_benchmarks` for borrower-vs-industry ratio comparison (APG 220 paragraph 64 alignment)
- `industry_failure_rates` for sector-specific insolvency trend — Construction (E) and Rental/Hiring/Real Estate Services (L) are the most-watched divisions for property-backed exposures

### Product relevance examples
- **Bridging**: sensitive to liquidity/exit timing and short-term value moves. Uses `property_market_overlays.market_softness_score` and `cycle_stage`; downturn overlay's `property_value_haircut` directly conditions exit-value assumptions.
- **Development/construction**: sensitive to approvals/activity pipeline, funding backdrop, and **builder solvency** (Construction insolvency rates from `industry_failure_rates`). Borrower's financial ratios should be compared to Construction division medians from `industry_financial_benchmarks`.
- **Investment property lending**: sensitive to broader cycle stage, refinancing conditions, and arrears environment. Operating-company tenant covenants benefit from APG-220-aligned ratio benchmarking against the tenant's ANZSIC division.

### Downstream usage pattern
- join property overlays to facility-level datasets by segment/date
- apply downturn overlay assumptions in stress views
- condition LGD and haircut assumptions on cycle/regime context
- use `industry_financial_benchmarks` inside the borrower scorecard for industry-relative ratio scoring on the operating-company side
- use `industry_failure_rates` (especially the Construction row) to anchor builder-insolvency stress assumptions

---

## 7) Downstream usage

Likely primary consumers:
- `LGD-commercial`
- `stress-testing-commercial`
- `expected-loss-engine-commercial`
- `RAROC-pricing-and-return-hurdle`
- `PD-and-scorecard-commercial` (macro context joins; benchmark joins for borrower ratios)

Downstream repos typically do:
- collateral valuation stress translation
- facility-level model conditioning
- borrower-vs-industry ratio scoring
- scenario reporting and governance

This repo supplies:
- standardized upstream context tables
- explicit lineage and effective-date fields
- stable contract export filenames
- consistent `anzsic_division_code` join grain across `industry_risk_scores`, `industry_failure_rates`, and `industry_financial_benchmarks`

---

## 8) Operational workflow

Canonical run order:
1. `python src/download_public_data.py` (network-dependent PTRS download/rebuild)
2. `python src/export_contracts.py`
3. `python src/validate_upstream.py`

Optional preflight steps:
- `python src/build_public_panels.py` (build panel/reference CSVs in `data/processed/public/`)
- `python src/build_overlays.py` (build overlay tables in-memory for sanity checks)

Where outputs are stored:
- canonical downstream contracts: `data/exports/`
- canonical CSV contracts: `outputs/contracts/`

Core contract outputs:
- `data/exports/industry_risk_scores.parquet`
- `data/exports/property_market_overlays.parquet`
- `data/exports/downturn_overlay_table.parquet`
- `data/exports/macro_regime_flags.parquet`
- `data/exports/industry_failure_rates.parquet`
- `data/exports/industry_financial_benchmarks.parquet`

Optional explainability panels:
- `data/exports/business_cycle_panel.parquet`
- `data/exports/property_cycle_panel.parquet`
- `data/exports/property_market_overlays_by_building_type.parquet`

What staff should check:
- files exist and are non-empty
- cycle stage and risk bands are populated on `property_market_overlays`
- `source_note` clearly indicates when fallback proxies were used (property approvals, property building-activity, ASIC stub)
- `as_of_date` aligns with latest staged source vintages
- `industry_financial_benchmarks` row count is 18 and joins cleanly to `industry_risk_scores` on `anzsic_division_code`

---

## 9) Glossary

- **Collateral haircut**: reduction applied to collateral value under stress.
- **Cycle stage**: directional market state (growth/neutral/slowing/downturn).
- **Market softness**: composite indicator of weaker property conditions.
- **Arrears environment**: qualitative/quantitative view of repayment stress backdrop.
- **Regime flag**: compact label used to condition downstream models.
- **Proxy**: transparent substitute metric used when a preferred dataset is unavailable.
- **Scenario multipliers**: factors applied in downstream stress views (for example PD/LGD/CCF adjustments).
- **APG 220**: APRA Prudential Practice Guide on credit risk management — paragraph 64 specifies industry-benchmarked financial ratios as a standard credit-assessment input. Applies to the operating-company side of property-backed deals.
- **Industry-aggregate ratio**: ratio computed from ABS-published industry totals (e.g. total industry sales ÷ total industry COGS); mathematically a weighted-average industry ratio. Published as `median_*` in the benchmark contract because that is the term APG 220 uses; the closest publicly-available proxy for the firm-level distribution median.
- **Failure rate**: realised insolvency count per industry, divided by active business count, expressed as a percentage. Construction (E) and Rental/Hiring/Real Estate Services (L) are the divisions most-watched for property-backed lending.

---

## 10) Limitations

- Public property overlays provide **macro/segment context**, not asset-by-asset valuation.
- Outputs are not substitutes for transaction-level due diligence or valuation review.
- Current staged inputs can be national/segment level rather than granular regional data, depending on available files.
- Some series may use explicit fallback proxies when optional datasets are missing.
- Downturn table is illustrative and transparent, but not a calibrated prudential stress framework.
- `industry_financial_benchmarks` publishes industry-aggregate ratios labelled `median_*` — the closest publicly-available proxy for the firm-level median APG 220 calls out, but not a true firm-level distribution median. Downstream consumers needing true firm-level p25/p75 percentiles must compute them from internal portfolio data.
- `industry_failure_rates` denominator falls back to a fixed table (derived from ABS Cat. 8165.0 summary) when a live extract is not staged. Source note flags the fallback. Construction (E) is the most material division to validate against an authoritative live extract before relying on the rate for property-backed stress assumptions.
- Final borrower-level and portfolio-level calibration remains a downstream responsibility.

---

## Practical quality notes for new staff

- If network download is blocked, stage required public files manually and rerun.
- If parquet export fails, install dependencies from `requirements.txt`.
- Use `source_note` and validation outputs to confirm whether the run used primary datasets or fallback proxies.
- For property-backed lending, treat `industry_financial_benchmarks` as the APG-220-aligned reference for the operating-company side of the deal and pair it with the property overlays for the collateral side.
