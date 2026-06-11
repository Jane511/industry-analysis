# Methodology Manual — Cash Flow Lending Overlays

## 1) Purpose

This manual explains how `industry-analysis` builds **public-data overlays** used to support credit decisions for **cash flow lending** (for example, SME and mid-market corporate lending where repayment capacity is mainly from business cash generation, not collateral sale).

It is written for new staff with no credit-risk background.
Plain-English summary: we take trusted public datasets, turn them into consistent sector and macro signals, and publish contract outputs that downstream model repos can consume.

---

## 2) How this repo fits into the overall system

`industry-analysis` is the **upstream public-data and overlay engine** in the portfolio stack.

It produces:
- cleaned and standardized public-data panels
- business-cycle and macro-regime indicators
- industry overlay scores
- realised insolvency rates per ANZSIC division (validation anchor)
- per-ANZSIC industry financial-ratio benchmarks (APG 220 paragraph 64)
- contract exports in `data/exports/` (six core + three optional explainability panels)

Downstream repos use these exports for:
- PD model conditioning and scorecard overlays
- LGD and EL context adjustments
- pricing and return-hurdle overlays
- stress scenario context
- borrower-vs-industry ratio scoring (origination scorecard)

This repo does **not** do:
- loan-level PD/LGD/EAD/cure/path model fitting
- borrower scorecards as final decision engines
- pricing decision engines
- portfolio stress engines

---

## 3) Basic credit concepts (beginner-friendly)

### What is cash flow lending?
Cash flow lending is lending where repayment mainly depends on a borrower's ongoing operating cash flow (sales, margin, working-capital performance), not primarily on selling property security.

### Why macro and industry data matters
Even strong borrowers are affected by:
- sector demand changes
- employment and margin pressure
- inventory build-up
- interest-rate changes

Public macro/industry data helps credit teams avoid judging borrowers in isolation from the external cycle.

### Why industry-relative financial ratios matter (APG 220 paragraph 64)
APG 220 paragraph 64 says: *"Typically, ADIs will use a range of financial ratios to support their credit risk assessment. Key areas of focus might include interest coverage, gearing and leverage, which can be compared to relevant industry benchmarks. It is important that differences in industry sectors and sub-sectors are taken into account."*

A borrower's EBITDA margin of 9% is "weak" if the industry median is 17% (Health Care), "average" if it's 9% (Manufacturing), and "strong" if it's 5% (Other Services). Without published industry medians, every downstream credit assessment system has to compute these benchmarks independently — leading to inconsistency, duplicated effort, and weak audit defensibility. The repo publishes an `industry_financial_benchmarks` contract so all consumers use the same reference.

### What are panels and overlays?
- **Panel**: a structured table of consistent metrics over industries/segments and dates.
- **Overlay**: a risk interpretation layer derived from panel signals (for example, an industry risk score used as a model input or policy context).

---

## 4) Public datasets used

### Core datasets

| Source | Dataset | What it measures | Why it matters for cash flow lending | How used in repo |
|---|---|---|---|---|
| ABS | Australian Industry (`81550DO001_202324.xlsx`) | Annual sector sales, employment, wages, profit, EBITDA | Structural sector resilience and cyclicality | Stage-1 structural features and margin/growth anchors; feeds `median_ebitda_margin_pct`, `median_wages_to_sales_pct`, `median_sales_growth_pct`, `median_sales_per_employee_thousands` in `industry_financial_benchmarks` |
| ABS | Business Indicators profit ratio (`56760022...`) | Gross operating profit / sales ratio (quarterly) | Current earnings resilience signal | Macro panel profitability level/trend scoring; feeds `median_gross_operating_profit_to_sales_ratio` |
| ABS | Business Indicators inventory ratio (`56760023...`) | Inventories / sales ratio (quarterly) | Working-capital pressure and stock build risk | Inventory-days estimate, YoY inventory pressure, stock-build flag; feeds `median_inventory_days_est` and `median_inventory_to_sales_ratio` |
| ABS | Labour Force by industry (`6291004...`) | Employment trend by industry | Demand and operating health proxy | Employment YoY growth score in macro panel; feeds `median_employment_yoy_growth_pct` |
| ABS | Building Approvals non-residential (`87310051...`) | Forward non-residential approvals by type | Sector demand proxy for linked industries | Demand proxy mapping for industry macro signals |
| ABS | Counts of Australian Businesses (Cat. 8165.0) | Active business counts per ANZSIC division | Denominator for industry failure rates | Backing series for `industry_failure_rates.active_businesses` |
| RBA | F1 cash-rate table (`rba_f1_data.csv`) | Current policy rate and movement | Funding conditions and repayment pressure context | Cash-rate regime and backdrop fields in panels |
| ASIC | Series 1A insolvency statistics | Companies entering external administration, by ANZSIC | Realised stress signal for validation/calibration | Numerator for `industry_failure_rates.failure_rate_pct` (TTM) |
| PTRS regulator publications | Cycle 8/9 and guidance PDFs | Official payment-time behavior by industry | Receivables/payables behavior proxy for working-capital interpretation | Workbook reconstruction and AR/AP benchmark context |

### Optional staged context datasets

These may be staged locally (not always available):
- RBA arrears commentary extract
- APRA property/banking context extract

When missing, the repo uses transparent proxy logic and records this in `source_note`.

---

## 5) Derived information created from public data (critical)

### A) Business cycle panel (`business_cycle_panel`)
- **Purpose**: central industry + macro table for non-property lending overlays.
- **Inputs**: ABS industry, ABS business indicators, ABS labour force, ABS approvals, RBA F1.
- **High-level logic**:
  - compute structural industry scores (cyclicality, rate sensitivity, demand dependency, external shock)
  - compute macro signal scores (employment, margin level/trend, inventory pressure, demand proxy)
  - blend into base industry risk score and risk band
- **Output meaning**: ranked and explainable sector risk context for upstream overlaying.

### B) Macro regime flags (`macro_regime_flags`)
- **Purpose**: compact regime state for downstream model conditioning.
- **Inputs**: RBA cash-rate summary + optional arrears/property context.
- **High-level logic**: map rate level/change and arrears environment into regime labels (for example restrictive/easing/downturn-watch conditions).
- **Output meaning**: "state of the cycle" flags that downstream repos can join by date.

### C) Industry risk scores (`industry_risk_scores`)
- **Purpose**: canonical sector overlay table for cash flow lending use cases.
- **Inputs**: business cycle panel.
- **High-level logic**: select and publish core scoring fields used by downstream teams.
- **Output meaning**: concise table of sector-level risk overlays and key macro backdrop fields.

### D) Industry failure rates (`industry_failure_rates`)
- **Purpose**: realised insolvency rate per ANZSIC division. Free, government-data equivalent of paid sector-outlook feeds.
- **Inputs**: ASIC Series 1A insolvency counts ÷ ABS Cat. 8165.0 active-business counts.
- **High-level logic**: compute trailing-twelve-month insolvency count per division, divide by active businesses, also publish year-on-year change in the rate.
- **Output meaning**: current-state validation anchor — downstream PD-model and ECL teams compare model-implied PDs against this realised rate to detect drift or sector-specific stress not captured elsewhere.

### E) Industry financial benchmarks (`industry_financial_benchmarks`)
- **Purpose**: per-ANZSIC-division medians of the financial ratios APG 220 paragraph 64 calls out as the standard credit-assessment benchmarks.
- **Inputs**: business cycle panel only — no new ABS catalogues required. The benchmark builder is a thin re-shaping of values already derived for the macro_risk_score.
- **Published medians**:
  - `median_ebitda_margin_pct` (ABS Cat. 8155.0)
  - `median_gross_operating_profit_to_sales_ratio` (ABS Cat. 5676.0)
  - `median_wages_to_sales_pct` (ABS Cat. 8155.0)
  - `median_inventory_days_est` (engine-derived from ABS Cat. 5676.0)
  - `median_sales_growth_pct` (ABS Cat. 8155.0)
  - `median_employment_yoy_growth_pct` (ABS Cat. 6291.0)
  - `median_inventory_to_sales_ratio` (ABS Cat. 5676.0)
  - `median_sales_per_employee_thousands` (derived: `sales_m_latest * 1000 / employment_000_latest`)
- **Method label**: every value is published with the explicit method note `"ABS aggregate (industry-weighted; closest public proxy for industry median)"`. Mathematically these are weighted-average industry ratios computed from ABS aggregates, not the median of firm-level ratios within the industry. We use the label "median" because it matches the language of APG 220 and is the closest publicly-available proxy.
- **Output meaning**: the reference any borrower's ratio is compared against. Origination scorecards and the PD model use these to compute industry-relative borrower features (e.g. "this borrower's leverage is 1.3 standard deviations above industry median") without each consumer reinventing the benchmarks.
- **Out of scope** (deliberate, future passes): per-industry p25/p75 percentile estimates (require firm-level data); sub-sector / subdivision granularity; computed ratios needing firm-level inputs (DSCR, current ratio, debtor/creditor days, net-debt-to-EBITDA).

### F) Supporting context for cross-segment consistency
- Property-cycle and downturn outputs are generated in the same repo for full-stack overlay consistency, but cash-flow downstream consumers mainly rely on business-cycle, industry-score, failure-rate, and benchmark exports.

---

## 6) Segment-specific methodology — cash flow lending

For SME/mid-market cash-flow lending, this repo supports four practical questions:

1. **Is the borrower's sector currently getting riskier or safer?**
   Industry base risk scores and macro signals answer this.

2. **Are working-capital conditions tightening?**
   Inventory and payment-time related public signals provide directional context.

3. **Should underwriting assumptions be more conservative this period?**
   Macro-regime flags provide cycle-aware conditioning for downstream PD/EL/pricing repos.

4. **How does this borrower's financial profile compare to the typical company in their industry?**
   `industry_financial_benchmarks` provides the per-ANZSIC reference values for borrower-vs-industry ratio comparisons (APG 220 paragraph 64).

### How the benchmarks support the credit grade vs. PD multiplier separation

Industry remains a **borrower characteristic** (informing the credit grade) and **never multiplies the post-grade PD**. This repo publishes two complementary signals:

- `industry_risk_scores.pd_multiplier` — applied **before** the grade is assigned, as part of the macro/industry conditioning of the score.
- `industry_financial_benchmarks` — used **inside** the grade derivation, as the comparison reference for borrower ratios that feed the scorecard.

Both signals are sourced from the same underlying `business_cycle_panel`, ensuring consistency between the macro overlay and the borrower-level features.

### Relevant industry examples
- Construction, Retail, Accommodation/Food, Transport, Manufacturing, Agriculture are typically more cycle-sensitive.
- Professional services and Health are typically more defensive (still cyclical, but differently exposed).
- Mining has a structurally elevated industry-aggregate EBITDA margin (~47% in current vintage) — a real feature of resource industries, not a unit error. The benchmark will move materially with commodity-price cycles.

### How downstream projects use outputs
- pull `industry_risk_scores.parquet` for sector overlay features (core)
- pull `macro_regime_flags.parquet` for regime conditioning logic (core)
- pull `industry_failure_rates.parquet` for realised-rate validation/anchoring (core)
- pull `industry_financial_benchmarks.parquet` for borrower-vs-industry ratio scoring (core)
- optionally pull `business_cycle_panel.parquet` for detailed explainability fields

---

## 7) Downstream usage

Likely consumer repos:
- `PD-and-scorecard-commercial`
- `expected-loss-engine-commercial`
- `RAROC-pricing-and-return-hurdle`
- `stress-testing-commercial`
- `LGD-commercial` (for macro-context joins)

What they do:
- borrower-level and facility-level model fitting/calibration
- borrower-vs-industry ratio scoring inside the scorecard
- pricing and hurdle logic
- stress projections
- governance and portfolio decisions

What they expect from this repo:
- stable schemas in `data/exports/`
- consistent effective-date conventions
- transparent source lineage
- benchmarks join-grain (`anzsic_division_code`) consistent with industry_risk_scores

---

## 8) Operational workflow

Canonical run order:
1. `python src/download_public_data.py`
   - downloads network-dependent PTRS source files and reconstructs the workbook
2. `python src/export_contracts.py`
   - writes canonical CSV contracts to `outputs/contracts/`
3. `python src/validate_upstream.py`
   - validates required core outputs and optional explainability panels

Optional preflight steps:
- `python src/build_public_panels.py` (build panel/reference CSVs in `data/processed/public/`)
- `python src/build_overlays.py` (build overlay tables in-memory for sanity checks)

Where outputs are stored:
- **Canonical contracts**: `data/exports/`
- **Canonical CSV contracts**: `outputs/contracts/`

What staff should check each run:
- all six core parquet files exist and are non-empty:
  - `industry_risk_scores.parquet`
  - `property_market_overlays.parquet`
  - `downturn_overlay_table.parquet`
  - `macro_regime_flags.parquet`
  - `industry_failure_rates.parquet`
  - `industry_financial_benchmarks.parquet`
- optional explainability panels if needed by consumers:
  - `business_cycle_panel.parquet`
  - `property_cycle_panel.parquet`
  - `property_market_overlays_by_building_type.parquet`
- `as_of_date`/period fields align with staged source vintages
- no unexpected missing values in critical score fields
- `source_note` clearly describes any proxy fallback or APG 220 limitations
- `industry_financial_benchmarks` row count is 18 and joins cleanly to `industry_risk_scores` on `anzsic_division_code`

---

## 9) Glossary

- **PD**: probability of default.
- **LGD**: loss given default.
- **EAD**: exposure at default.
- **EL**: expected loss (typically PD × LGD × EAD).
- **APG 220**: APRA Prudential Practice Guide on credit risk management — paragraph 64 specifies industry-benchmarked financial ratios as a standard credit-assessment input.
- **Macro regime**: a labeled economic state (for example restrictive-rates/easing/downturn-watch).
- **Industry overlay**: sector-level risk adjustment context derived from public data.
- **Industry-aggregate ratio**: ratio computed from ABS-published industry totals (e.g. total industry sales ÷ total industry COGS); mathematically a weighted-average industry ratio.
- **Firm-level distribution median**: the 50th-percentile value when individual firms in an industry are ranked by a ratio. Not directly available from ABS aggregates; requires firm-level data (out of scope for this repo).
- **Failure rate**: realised insolvency count per industry, divided by active business count, expressed as a percentage.
- **Proxy metric**: an indirect but explainable measure used when direct internal metrics are unavailable publicly.
- **Contract export**: stable upstream table intended for downstream system consumption.

---

## 10) Limitations

- Public data overlays are **context layers**, not borrower-level truth.
- Outputs are **sector-level** and **cycle-level**, not transaction-specific credit decisions.
- Some fields are deterministic proxies (for transparency), not institution-calibrated model coefficients.
- Optional datasets may be missing; proxy behavior is explicit but still approximate.
- `industry_financial_benchmarks` publishes industry-aggregate ratios labelled `median_*` — the closest publicly-available proxy for the firm-level median APG 220 calls out, but not a true firm-level distribution median. Downstream consumers needing true firm-level p25/p75 percentiles must compute them from internal portfolio data.
- `industry_failure_rates` denominator falls back to a fixed table (derived from ABS Cat. 8165.0 summary) when a live extract is not staged. Source note flags the fallback.
- Downstream repos must perform their own calibration, governance, and model validation before production use.

---

## Practical quality notes for new staff

- If download fails, check network policy first; this is expected in restricted environments.
- If export fails, ensure parquet engine dependency is installed (`pyarrow` or `fastparquet`).
- If ASIC Series 1A is not staged and `ASIC_USE_STUB` is unset, `export_contracts.py` will fail loud — this is intentional, do not bypass.
- Always treat this repo as upstream context infrastructure, not final credit-decision logic.
- `industry_financial_benchmarks` is APG 220 compliance scaffolding — use it as the authoritative industry comparison reference rather than recomputing benchmarks per downstream consumer.
