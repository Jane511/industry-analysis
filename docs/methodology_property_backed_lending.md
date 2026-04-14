# Methodology Manual — Property-Backed Lending Overlays

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
- contract exports under `data/exports/`

Downstream repos use these tables for:
- collateral stress assumptions
- downturn scenario conditioning
- conservative policy overlays in borrower-level models

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

### What are panels and overlays here?
- **Property-cycle panel**: explains cycle stage and softness by segment.
- **Property-market overlays**: compact risk indicators for downstream use.
- **Downturn overlays**: scenario multipliers/haircuts for stress interpretation.

---

## 4) Public datasets used (very important)

| Source | Dataset | What it measures | Why it matters for property-backed lending | How used in repo |
|---|---|---|---|---|
| ABS | Building Approvals — Non-residential (`87310051...`) | Forward approvals trend by building type | Early cycle signal for supply/demand and development activity | Core approvals trend input for property cycle and region/segment risk |
| ABS (optional staged) | Building Activity extract | Commencements/completions confirmation | Validates whether approvals are translating into real pipeline activity | Enhances cycle signal quality; otherwise repo uses explicit approvals proxy |
| ABS (optional staged) | Lending Indicators extract | Finance demand momentum | Context for market financing conditions | Enhances region/segment finance signal; otherwise cash-rate proxy used |
| RBA | F1 cash-rate table (`rba_f1_data.csv`) | Current cash-rate level and 1-year change | Funding-cost and serviceability pressure backdrop | Cash-rate summary, regime derivation, fallback trend proxy |
| RBA (optional staged) | Housing arrears context extract | Qualitative arrears environment | Early stress context for collateral-linked portfolios | Arrears environment construction |
| APRA (optional staged) | Property/banking context extract | Supervisory context notes | Adds prudential context to property risk interpretation | Appended to arrears/macro notes |
| PTRS regulator publications | Payment timing by industry | Supplier/customer payment behavior proxy | Supports broader downturn narrative and overlays | Used in repo-wide overlay context (not a direct property valuation series) |
| ASIC (optional staged) | Insolvency extract | Insolvency counts by industry | Additional deterioration signal | Optional contextual overlay input |

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
- **Output meaning**: easy-to-join overlay output for property-linked portfolios.

### E) Downturn overlay table (`downturn_overlay_table`)
- **Purpose**: scenario table for property-linked stress assumptions.
- **Inputs**: arrears environment + property-cycle softness.
- **High-level logic**:
  - anchor scenario severity to current softness and arrears backdrop
  - produce base/mild/moderate/severe rows
  - output multiplier/haircut fields transparently
- **Output meaning**: scenario assumptions table for downstream stress interpretation; not a calibrated regulatory capital model.

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

### Product relevance examples
- **Bridging**: sensitive to liquidity/exit timing and short-term value moves.
- **Development/construction**: sensitive to approvals/activity pipeline and funding backdrop.
- **Investment property lending**: sensitive to broader cycle stage, refinancing conditions, and arrears environment.

### Downstream usage pattern
- join property overlays to facility-level datasets by segment/date
- apply downturn overlay assumptions in stress views
- condition LGD and haircut assumptions on cycle/regime context

---

## 7) Downstream usage

Likely primary consumers:
- `LGD-commercial`
- `stress-testing-commercial`
- `expected-loss-engine-commercial`
- `RAROC-pricing-and-return-hurdle`
- `PD-and-scorecard-commercial` (macro context joins)

Downstream repos typically do:
- collateral valuation stress translation
- facility-level model conditioning
- scenario reporting and governance

This repo supplies:
- standardized upstream context tables
- explicit lineage and effective-date fields
- stable contract export filenames

---

## 8) Operational workflow

Canonical run order:
1. `python scripts/download_public_data.py` (network-dependent PTRS download/rebuild)
2. `python scripts/build_public_panels.py`
3. `python scripts/build_overlays.py`
4. `python scripts/export_contracts.py`
5. `python scripts/validate_upstream.py`

Where outputs are stored:
- canonical downstream contracts: `data/exports/`
- inspection CSVs: `outputs/tables/`

Required property-related contract outputs:
- `data/exports/property_cycle_panel.parquet`
- `data/exports/macro_regime_flags.parquet`
- `data/exports/property_market_overlays.parquet`
- `data/exports/downturn_overlay_table.parquet`

What staff should check:
- files exist and are non-empty
- cycle stage and risk bands are populated
- `source_note` clearly indicates when fallback proxies were used
- `as_of_date` aligns with latest staged source vintages

---

## 9) Glossary

- **Collateral haircut**: reduction applied to collateral value under stress.
- **Cycle stage**: directional market state (growth/neutral/slowing/downturn).
- **Market softness**: composite indicator of weaker property conditions.
- **Arrears environment**: qualitative/quantitative view of repayment stress backdrop.
- **Regime flag**: compact label used to condition downstream models.
- **Proxy**: transparent substitute metric used when a preferred dataset is unavailable.
- **Scenario multipliers**: factors applied in downstream stress views (for example PD/LGD/CCF adjustments).

---

## 10) Limitations

- Public property overlays provide **macro/segment context**, not asset-by-asset valuation.
- Outputs are not substitutes for transaction-level due diligence or valuation review.
- Current staged inputs can be national/segment level rather than granular regional data, depending on available files.
- Some series may use explicit fallback proxies when optional datasets are missing.
- Downturn table is illustrative and transparent, but not a calibrated prudential stress framework.
- Final borrower-level and portfolio-level calibration remains a downstream responsibility.

---

## Practical quality notes for new staff

- If network download is blocked, stage required public files manually and rerun.
- If parquet export fails, install dependencies from `requirements.txt`.
- Use `source_note` and validation outputs to confirm whether the run used primary datasets or fallback proxies.
