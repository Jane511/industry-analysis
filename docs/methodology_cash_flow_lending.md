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
- contract exports in `data/exports/` (core + optional explainability panels)

Downstream repos use these exports for:
- PD model conditioning and scorecard overlays
- LGD and EL context adjustments
- pricing and return-hurdle overlays
- stress scenario context

This repo does **not** do:
- loan-level PD/LGD/EAD/cure/path model fitting
- borrower scorecards as final decision engines
- pricing decision engines
- portfolio stress engines

---

## 3) Basic credit concepts (beginner-friendly)

### What is cash flow lending?
Cash flow lending is lending where repayment mainly depends on a borrower’s ongoing operating cash flow (sales, margin, working-capital performance), not primarily on selling property security.

### Why macro and industry data matters
Even strong borrowers are affected by:
- sector demand changes
- employment and margin pressure
- inventory build-up
- interest-rate changes

Public macro/industry data helps credit teams avoid judging borrowers in isolation from the external cycle.

### What are panels and overlays?
- **Panel**: a structured table of consistent metrics over industries/segments and dates.
- **Overlay**: a risk interpretation layer derived from panel signals (for example, an industry risk score used as a model input or policy context).

---

## 4) Public datasets used

## Core datasets

| Source | Dataset | What it measures | Why it matters for cash flow lending | How used in repo |
|---|---|---|---|---|
| ABS | Australian Industry (`81550DO001_202324.xlsx`) | Annual sector sales, employment, wages, profit, EBITDA | Structural sector resilience and cyclicality | Stage-1 structural features and margin/growth anchors |
| ABS | Business Indicators profit ratio (`56760022...`) | Gross operating profit / sales ratio (quarterly) | Current earnings resilience signal | Macro panel profitability level/trend scoring |
| ABS | Business Indicators inventory ratio (`56760023...`) | Inventories / sales ratio (quarterly) | Working-capital pressure and stock build risk | Inventory-days estimate, YoY inventory pressure, stock-build flag |
| ABS | Labour Force by industry (`6291004...`) | Employment trend by industry | Demand and operating health proxy | Employment YoY growth score in macro panel |
| ABS | Building Approvals non-residential (`87310051...`) | Forward non-residential approvals by type | Sector demand proxy for linked industries | Demand proxy mapping for industry macro signals |
| RBA | F1 cash-rate table (`rba_f1_data.csv`) | Current policy rate and movement | Funding conditions and repayment pressure context | Cash-rate regime and backdrop fields in panels |
| PTRS regulator publications | Cycle 8/9 and guidance PDFs | Official payment-time behavior by industry | Receivables/payables behavior proxy for working-capital interpretation | Workbook reconstruction and AR/AP benchmark context |

### Optional staged context datasets

These may be staged locally (not always available):
- RBA arrears commentary extract
- APRA property/banking context extract
- ASIC insolvency extract (manual-stage compatible)

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
- **Output meaning**: “state of the cycle” flags that downstream repos can join by date.

### C) Industry risk scores (`industry_risk_scores`)
- **Purpose**: canonical sector overlay table for cash flow lending use cases.
- **Inputs**: business cycle panel.
- **High-level logic**: select and publish core scoring fields used by downstream teams.
- **Output meaning**: concise table of sector-level risk overlays and key macro backdrop fields.

### D) Supporting context for cross-segment consistency
- Property-cycle and downturn outputs are generated in the same repo for full-stack overlay consistency, but cash-flow downstream consumers mainly rely on business-cycle and industry-score exports.

---

## 6) Segment-specific methodology — cash flow lending

For SME/mid-market cash-flow lending, this repo supports three practical questions:

1. **Is the borrower’s sector currently getting riskier or safer?**  
   Industry base risk scores and macro signals answer this.

2. **Are working-capital conditions tightening?**  
   Inventory and payment-time related public signals provide directional context.

3. **Should underwriting assumptions be more conservative this period?**  
   Macro-regime flags provide cycle-aware conditioning for downstream PD/EL/pricing repos.

### Relevant industry examples
- Construction, Retail, Accommodation/Food, Transport, Manufacturing, Agriculture are typically more cycle-sensitive.
- Professional services and Health are typically more defensive (still cyclical, but differently exposed).

### How downstream projects use outputs
- pull `industry_risk_scores.parquet` for sector overlay features (core)
- pull `macro_regime_flags.parquet` for regime conditioning logic (core)
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
- pricing and hurdle logic
- stress projections
- governance and portfolio decisions

What they expect from this repo:
- stable schemas in `data/exports/`
- consistent effective-date conventions
- transparent source lineage

---

## 8) Operational workflow

Canonical run order:
1. `python scripts/download_public_data.py`  
   - downloads network-dependent PTRS source files and reconstructs the workbook
2. `python scripts/export_contracts.py`  
   - writes canonical parquet contracts to `data/exports/`
   - derives secondary CSV inspection outputs to `outputs/tables/`
3. `python scripts/validate_upstream.py`  
   - validates required core outputs and optional explainability panels

Optional preflight steps:
- `python scripts/build_public_panels.py` (build panel/reference CSVs in `data/processed/public/`)
- `python scripts/build_overlays.py` (build overlay tables in-memory for sanity checks)

Where outputs are stored:
- **Canonical contracts**: `data/exports/`
- **Inspection tables**: `outputs/tables/` (secondary, derived from canonical parquet exports)

What staff should check each run:
- all four core parquet files exist and are non-empty:
  - `industry_risk_scores.parquet`
  - `property_market_overlays.parquet`
  - `downturn_overlay_table.parquet`
  - `macro_regime_flags.parquet`
- optional explainability panels if needed by consumers:
  - `business_cycle_panel.parquet`
  - `property_cycle_panel.parquet`
- `as_of_date`/period fields align with staged source vintages
- no unexpected missing values in critical score fields
- `source_note` clearly describes any proxy fallback

---

## 9) Glossary

- **PD**: probability of default.
- **LGD**: loss given default.
- **EAD**: exposure at default.
- **EL**: expected loss (typically PD × LGD × EAD).
- **Macro regime**: a labeled economic state (for example restrictive-rates/easing/downturn-watch).
- **Industry overlay**: sector-level risk adjustment context derived from public data.
- **Proxy metric**: an indirect but explainable measure used when direct internal metrics are unavailable publicly.
- **Contract export**: stable upstream table intended for downstream system consumption.

---

## 10) Limitations

- Public data overlays are **context layers**, not borrower-level truth.
- Outputs are **sector-level** and **cycle-level**, not transaction-specific credit decisions.
- Some fields are deterministic proxies (for transparency), not institution-calibrated model coefficients.
- Optional datasets may be missing; proxy behavior is explicit but still approximate.
- Downstream repos must perform their own calibration, governance, and model validation before production use.

---

## Practical quality notes for new staff

- If download fails, check network policy first; this is expected in restricted environments.
- If export fails, ensure parquet engine dependency is installed (`pyarrow` or `fastparquet`).
- Always treat this repo as upstream context infrastructure, not final credit-decision logic.
