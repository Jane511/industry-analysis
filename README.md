![CI](https://github.com/Jane511/industry-analysis/actions/workflows/ci.yml/badge.svg)

# Australian Industry & Property Risk Reference Layer

**Turns real public Australian data (ABS / RBA / PTRS) into the macro layer a credit team
applies *before* it models individual borrowers — the current macro conditions to assess
against, the macro drivers to stress, and a 1–5 industry credit-risk score with a ready-to-use
PD overlay per ANZSIC division.**

> **Real public data only.** Sources are ABS, RBA and the Payment Times Reporting Scheme (PTRS).
> All synthetic / staged / illustrative data has been removed; the only non-data inputs are
> clearly-labelled methodology *assumptions* (stress shocks, scoring weights, and four CRE
> variables with no clean free public series).

## Full detail is in the reports — this README is the summary

The README explains the *method* and the headline numbers. Every figure, source row,
transformation and the full per-industry / per-scenario detail live in the two reports:

| Report | For | Open |
| --- | --- | --- |
| **Board** | Plain-English executive summary, headline findings | [md](outputs/reports/Industry_Analysis_Q1_2026_Board.md) · [html](outputs/reports/Industry_Analysis_Q1_2026_Board.html) · [docx](outputs/reports/Industry_Analysis_Q1_2026_Board.docx) |
| **Technical** | Full source inventory, transformations, validation, all per-industry detail | [md](outputs/reports/Industry_Analysis_Q1_2026_Technical.md) · [html](outputs/reports/Industry_Analysis_Q1_2026_Technical.html) · [docx](outputs/reports/Industry_Analysis_Q1_2026_Technical.docx) |

The model-ready data sits in eight CSV "contracts" in [`outputs/contracts/`](outputs/contracts/)
— the stable interface any downstream PD / LGD / ECL model reads.

## Data vintage & reporting periods

Every figure is the **2026-Q1 vintage** — pipeline `DATA_AS_OF = 2026-02-28`, with contracts
stamped **2026-06-16** after a live cash-rate refresh. The reference period each real source
actually reports for:

| Source / series | Catalogue | Reference period reported |
| --- | --- | --- |
| Australian Industry — financial ratios, structure | ABS 8155.0 | **FY 2023–24** (annual) |
| Business Indicators — profit / margins | ABS 5676.0 | **Dec 2025 quarter** |
| Business Indicators — inventories | ABS 5676.0 | **Dec 2025 quarter** |
| Labour Force, Detailed — industry employment | ABS 6291.0 | **Feb 2026** (monthly) |
| Building Approvals, non-residential — property cycle | ABS 8731.0 | **Feb 2026** (monthly) |
| Cash rate | RBA F1 | **Live** — latest available |
| Economy-wide levels — GDP, unemployment, CPI, WPI, house prices, TWI | ABS 5206 / 6202 / 6401 / 6345 / 6416 · RBA F11 | **Stated current readings** at the 2026-Q1 vintage |

The macro **stress shocks** in Section 2 are scenario-design assumptions (config vintage
`2026-Q1`), not dated observations. The committed real-data cache and its full per-file
attribution are in [`data/cache/ATTRIBUTION.md`](data/cache/ATTRIBUTION.md).

---

## 1. Macro conditions for credit assessment & risk management

A lender's loss rate is driven as much by *the environment it lends into* as by any single
borrower. Before scoring an industry or a deal, the engine reads where the economy and the
property markets currently sit — the conditions a credit team assesses against. Each figure
below is the latest observed level from a named public series, and together they form the
**base** of every stress scenario in Section 2.

### 1a. Economy-wide conditions

The broad drivers that condition PD and LGD across the whole book, regardless of product.

| Macro condition | Current level | What it signals for credit risk | Source |
|---|---|---|---|
| GDP growth (real, YoY) | 1.8% | Below-trend growth — softer revenue, slower deleveraging | ABS 5206 National Accounts |
| Unemployment rate | 4.1% | Low — supports household & SME debt-servicing | ABS 6202 Labour Force |
| Cash rate | 4.35% (+0.5pp YoY) | Restrictive — debt-servicing pressure on leveraged borrowers | RBA F1 (live) |
| Inflation (CPI, YoY) | 3.2% | Above target — cost-of-living squeeze on cash flow | ABS 6401 CPI |
| Wage growth (WPI, YoY) | 3.5% | Roughly matching CPI — thin real-income buffer | ABS 6345 Wage Price Index |
| Exchange rate (TWI, change) | 0.0% | Stable — neutral for FX-exposed corporates | RBA F11 |
| Industry / sector output (YoY) | 2.0% | Modest — sector-revenue channel for SME / corporate | ABS 8155 + 5676 |

### 1b. Property conditions

Property-secured lending splits into **residential** and **commercial** — they sit on different
cycles, so the engine reads them separately.

**Residential property.** The residential signal is **house-price growth: +4.0% YoY** (ABS 6416
Residential Property Price Index). This is the collateral channel for residential mortgages — when
it falls, mortgage LGD rises (Section 2b). *This is a **national** figure. State / capital-city
splits (ABS 6432) are not yet staged, so there is no by-state residential breakdown here; it will
be added once that source is in place.*

**Commercial property (CRE).** Read two ways:

*(i) Price & yield levels* — labelled **assumptions** (no clean free quarterly public series;
anchored to RBA FSR commentary). These feed the CRE stress paths in Section 2a:

| CRE condition | Current level | Reading |
|---|---|---|
| Commercial-property prices | 0.0% | Flat |
| Office vacancy rate | 12.0% | Elevated — office segment under pressure |
| CRE rents | 0.0% | Flat |
| CRE cap rates | 6.0% | — |

*(ii) Building-type cycle* — **real ABS data** (Cat. 8731 non-residential building approvals).
This is where CRE risk actually concentrates right now: **offices are in a clear downturn**
(approvals −36% YoY) while health buildings and warehouses still grow. The softness score runs
1 (firm) → 5 (soft); "PD if standalone" is the overlay that segment would carry on its own.

![Commercial property softness by building type, from ABS non-residential building approvals — offices softest, health buildings firmest](outputs/charts/property_market_softness.png)

| Building type | Cycle stage | Softness (1 firm → 5 soft) | Approvals YoY | PD if standalone |
|---|---|--:|--:|--:|
| Offices | downturn | 4.30 | −35.7% | 1.15× |
| Education buildings | slowing | 3.25 | −21.4% | 1.15× |
| Retail & wholesale trade buildings | neutral | 3.15 | +68.5% | 1.10× |
| Short-term accommodation buildings | growth | 2.85 | +113.7% | 1.10× |
| Aged care facilities | neutral | 2.70 | +219.9% | 1.00× |
| Agricultural & aquacultural buildings | neutral | 2.65 | +58.4% | 1.00× |
| Warehouses | neutral | 2.20 | +69.3% | 1.00× |
| Health buildings | growth | 1.65 | +355.0% | 0.95× |

The table lists the eight specific building types; the chart additionally shows three "Total …"
bars, which are aggregate reference lines only. The five-segment rollup these building types feed
(CRE / Retail / Industrial / Construction / Residential) is in
[`property_market_overlays.csv`](outputs/contracts/property_market_overlays.csv). Approvals are a
forward-looking proxy for building activity (commencements/completions are not yet staged), and
the high positive YoY figures reflect volatile low-base months, so they are read for *direction*,
not magnitude.

### 1c. Macro regime

**Latest (as of 2026-06-15):** cash-rate regime **restrictive / rising**, arrears
**Low / Improving**, overall macro-regime flag **base**
([`macro_regime_flags.csv`](outputs/contracts/macro_regime_flags.csv)). The cash-rate regime is
real RBA F1; the arrears level/trend is a labelled qualitative assumption from the RBA FSR. A
"base" regime means no recession overlay is applied at current readings — but the engine
pre-computes the stress dials in Section 2 so a downturn can be costed instantly.

---

## 2. Macro drivers for stress testing — per product and per industry

Stress testing runs the book through a **severe-but-plausible** scenario to see how defaults and
losses move (Basel CRE36.50; APS 220 §70–72). The full bank exercise has eleven steps — scope,
scenarios, **macro path**, **map the path to PD / LGD / EAD**, apply to the book, project capital,
contingency actions, limits, board reporting, validation, documentation.

**This layer delivers the front of that process and hands the result downstream as a ready-to-use
input.** It is the *top-down macro-credit linkage*: it turns one macro scenario into a **PD / LGD /
EAD stress multiplier for every portfolio segment and every industry**. A downstream
**PD / LGD / EAD portfolio-monitoring model then multiplies these factors onto its own facilities**
(the bottom-up step) and carries on with capital projection, contingency actions and board
reporting — those steps stay with the modelling and capital functions, not here.

In the language of the standard process: this repo produces **Step 3 (the scenario macro path)**
and **Step 4 (the map to PD / LGD / EAD)**; Steps 5–11 belong to the model that consumes it.

What it honours from the compliance guidance — and what it does **not** claim to be:

| Aligned with | How this layer applies it |
| --- | --- |
| **Basel CRE36.51** — mild-recession minimum | `mild` = two consecutive quarters of ~zero GDP growth (the standard technical-recession definition) |
| **APS 220 §72** — severe but plausible | `severe` is a GFC-like, internally consistent path — not a tail fantasy |
| **APG 113 §92** — no diversification benefit | the roll-up assumes **no** diversification offset; segments are summed exposure-weighted |
| **APS 220 §76** — validation | flagged **illustrative, not calibrated**: in production the paths come from a macro model and the weights from estimated betas, both independently validated at least annually |

> **Not a capital stress test.** This is the macro-credit *input*, not the bank's ICAAP / Pillar 1
> exercise. It does not project capital, evolve the balance sheet, or set management actions. Four
> CRE variables are labelled assumptions (no clean free quarterly public series).

### 2a. The scenario macro path (the shocks a downstream model receives)

Twelve drivers, each with the Section 1 base level and an illustrative shock path across
**base → mild → moderate → severe**. Source:
[`macro_scenario_paths.csv`](outputs/contracts/macro_scenario_paths.csv).

| Macro driver | Base | Mild | Moderate | Severe |
|---|--:|--:|--:|--:|
| GDP growth (real, YoY) | 1.8% | 0.0% | −1.5% | −3.5% |
| Unemployment rate | 4.1% | 5.3% | 6.6% | 8.1% |
| Cash rate | 4.35% | 4.6% | 4.85% | 5.1% |
| Inflation (CPI, YoY) | 3.2% | 4.0% | 4.7% | 5.7% |
| Wage growth (WPI, YoY) | 3.5% | 3.0% | 2.5% | 1.7% |
| House-price growth (YoY) | 4.0% | −4.0% | −11.0% | −21.0% |
| Exchange rate (TWI, change) | 0.0% | −5.0% | −10.0% | −15.0% |
| Industry / sector output (YoY) | 2.0% | 0.0% | −2.0% | −5.0% |
| Commercial-property prices* | 0.0% | −7.0% | −15.0% | −28.0% |
| Office vacancy rate* | 12.0% | 14.0% | 16.0% | 19.0% |
| CRE rents* | 0.0% | −4.0% | −9.0% | −16.0% |
| CRE cap rates* | 6.0% | 6.4% | 6.9% | 7.6% |

\* labelled assumption — no clean free quarterly public series.

### 2b. Mapping the path to each product's PD / LGD / EAD

The map is *per product*, because different products fail for different reasons. For each one the
layer splits risk into the three quantities a loss model needs and records which drivers move each:

- **PD** — *probability of default*: how likely the borrower is to stop paying.
- **LGD** — *loss given default*: the share of the balance lost once they default (a collateral story).
- **EAD** — *exposure at default*: how much is drawn / owing when default hits.

Each driver carries a **weight** for how much it moves that quantity. **Weights sum to 1.0 within
each of PD / LGD / EAD** — so a 0.45 driver moves it about twice as much as a 0.20 driver. The
arrow shows the stress direction (**↑** = worse when the driver rises, **↓** = worse when it
falls). These are illustrative weights, not estimated betas. Source:
[`portfolio_macro_sensitivity.csv`](outputs/contracts/portfolio_macro_sensitivity.csv).

**Worked example — residential mortgages**, read as three separate stories:

- **PD** worsens when the **labour market and rates** turn: unemployment ↑ (0.45) does most of the
  work, then cash rate ↑ (0.25), wage growth ↓ (0.20), inflation ↑ (0.10).
- **LGD** is almost entirely a **collateral** story: house prices ↓ (0.70) dominate, with
  unemployment ↑ (0.20) and cash rate ↑ (0.10) secondary.
- **EAD** grows as stressed borrowers draw down: cash rate ↑ (0.50), unemployment ↑ (0.30),
  GDP ↓ (0.20).

So in the *severe* scenario a −21% house-price move drives mortgage **LGD**, while the +4pp jump in
unemployment drives mortgage **PD** — two different drivers, two different quantities. The same
split for every product:

| Product / portfolio | PD — main drivers (weight) | LGD — main drivers (weight) | EAD — main drivers (weight) |
|---|---|---|---|
| **Residential mortgages** | unemployment ↑ (0.45), cash rate ↑ (0.25), wage growth ↓ (0.20), inflation ↑ (0.10) | house prices ↓ (0.70), unemployment ↑ (0.20), cash rate ↑ (0.10) | cash rate ↑ (0.50), unemployment ↑ (0.30), GDP ↓ (0.20) |
| **Credit cards** | unemployment ↑ (0.50), wage growth ↓ (0.30), inflation ↑ (0.20) | unemployment ↑ (0.50), inflation ↑ (0.30), wage growth ↓ (0.20) | GDP ↓ (0.40), cash rate ↑ (0.35), unemployment ↑ (0.25) |
| **SME lending** | GDP ↓ (0.35), unemployment ↑ (0.25), cash rate ↑ (0.20), sector output ↓ (0.20) | CRE prices ↓ (0.45), house prices ↓ (0.35), sector output ↓ (0.20) | cash rate ↑ (0.40), GDP ↓ (0.35), sector output ↓ (0.25) |
| **Corporate lending** | GDP ↓ (0.40), sector output ↓ (0.30), cash rate ↑ (0.15), FX ↓ (0.15) | sector output ↓ (0.45), CRE prices ↓ (0.30), FX ↓ (0.25) | cash rate ↑ (0.45), GDP ↓ (0.35), sector output ↓ (0.20) |
| **Commercial property (CRE)** | CRE prices ↓ (0.30), vacancy ↑ (0.30), rents ↓ (0.20), cash rate ↑ (0.20) | CRE prices ↓ (0.40), cap rates ↑ (0.35), rents ↓ (0.25) | cash rate ↑ (0.50), vacancy ↑ (0.30), CRE prices ↓ (0.20) |
| **Development finance** | CRE prices ↓ (0.35), GDP ↓ (0.25), vacancy ↑ (0.20), cash rate ↑ (0.20) | CRE prices ↓ (0.55), cap rates ↑ (0.25), rents ↓ (0.20) | cash rate ↑ (0.45), CRE prices ↓ (0.30), GDP ↓ (0.25) |

The pattern: **household products** (mortgages, cards) pivot on the **labour market**; **business
products** (SME, corporate) pivot on **GDP and sector output**; **property products** (CRE,
development finance) pivot on **property values, vacancy and cap rates**.

### 2c. The output — stress multipliers a PD/LGD/EAD monitoring model plugs in

Combining the scenario path (2a) with each product's driver mix (2b) — scaled by a per-segment
magnitude factor and a multiplier ceiling — yields **the deliverable**: a PD / LGD / EAD stress
multiplier for every segment, in every scenario
([`macro_stress_segment_multipliers.csv`](outputs/reports/macro_stress_segment_multipliers.csv)).
A monitoring model reads these and multiplies them onto its own base estimates; stressed
**EL = stressed PD × stressed LGD × stressed EAD**.

Severe-scenario multipliers (mild and moderate are in the contract; PD rises most because default
is the most cyclical parameter):

| Segment | PD × | LGD × | EAD × |
|---|--:|--:|--:|
| Residential mortgages | 2.35 | 1.48 | 1.20 |
| Credit cards | 2.65 | 1.42 | 1.24 |
| SME lending | 2.65 | 1.54 | 1.28 |
| Corporate lending | 2.50 | 1.54 | 1.28 |
| Commercial property (CRE) | 2.95 | 1.72 | 1.32 |
| Development finance | 3.25 | 1.78 | 1.36 |

Property-secured segments (CRE, development finance) carry the largest multipliers — consistent
with the office downturn in Section 1b. For a quick portfolio-wide cross-check, a simpler headline
overlay (PD ×1.2 / 1.5 / 2.0 across mild / moderate / severe, plus LGD, CCF and a property-value
haircut) is in [`downturn_overlay_table.csv`](outputs/contracts/downturn_overlay_table.csv).

Applied to a committed demo book, these multipliers give an illustrative portfolio expected-loss
uplift of **1.9× mild, 3.2× moderate, 5.6× severe** (exposure-weighted, **no diversification
benefit** per APG 113 §92; [`macro_stress_demo_summary.csv`](outputs/reports/macro_stress_demo_summary.csv)).
A real monitoring model would apply the same multipliers to its actual facilities.

### 2d. The industry dimension — per-ANZSIC stress input

The same input has an **industry** axis. Each division's current-conditions inputs (employment,
margins, demand) set how hard the **sector-output** driver in 2b bites for SME and corporate books,
and feed the per-industry PD overlay in Section 3. Source:
[`business_cycle_panel.csv`](outputs/contracts/business_cycle_panel.csv).

| Industry | Employment YoY | EBITDA margin | Demand YoY | Macro (current-conditions) score |
|---|--:|--:|--:|--:|
| Agriculture, Forestry and Fishing | −5.1% | 14.6% | +58% | 3.20 |
| Mining | −5.1% | 47.3% | — | 2.80 |
| Manufacturing | −0.9% | 9.2% | +56% | 3.20 |
| Retail Trade | −0.5% | 7.8% | +68% | 3.20 |
| Wholesale Trade | −8.7% | 6.1% | +69% | 3.20 |
| Arts and Recreation Services | −5.8% | 13.5% | −56% | 3.80 |

A sector with falling employment and thin margins is exactly where the sector-output shock bites
hardest, so a downstream SME / corporate model can scale its sector-output sensitivity by the
industry's score. Demand growth is a volatile approvals/indicator proxy (base effects), so it is
read alongside employment and margins, not alone. Full per-industry detail for all 18 divisions is
**Section 5** of the [Technical report](outputs/reports/Industry_Analysis_Q1_2026_Technical.md).

---

## 3. How the industry credit-risk score is calculated

Each ANZSIC division gets a single **1 (low risk) → 5 (high risk)** score that blends a
**structural** view with a **current-conditions** view, then maps to a risk level and a PD
overlay. The whole calculation is in
[src/panels/macro_signals.py](src/panels/macro_signals.py) (scoring) and
[src/overlays/build_industry_risk_scores.py](src/overlays/build_industry_risk_scores.py) (ladder).

**Step 1 — macro (current-conditions) score.** Five components, each scored 1 → 5 from ABS
business-indicator series, then averaged:

| Component | Higher risk when… | Source |
|---|---|---|
| Employment score | industry employment YoY growth is falling | ABS 6291 Labour Force |
| Margin level score | profit-to-sales / EBITDA margin is thin | ABS 5676 / 8155 |
| Margin trend score | margin is deteriorating YoY | ABS 5676 / 8155 |
| Inventory score | inventory days / stock-build risk is rising | ABS 5676 |
| Demand score | demand-proxy YoY growth is weak | ABS approvals / indicators |

`macro_risk_score = mean(employment, margin level, margin trend, inventory, demand)`

**Step 2 — blend with structural risk.** `classification_risk_score` (1–5) captures the
structural risk of the division (cyclicality, capital intensity, revenue concentration):

`industry_base_risk_score = 0.55 × classification_risk_score + 0.45 × macro_risk_score`

**Step 3 — map to level + PD overlay** via a five-band ladder:

| Base score | Level | PD multiplier |
|---|---|--:|
| < 1.60 | Low | 0.90× |
| 1.60 – 2.00 | Moderate-low | 0.95× |
| 2.00 – 2.80 | Medium | 1.00× |
| 2.80 – 3.23 | Moderate-high | 1.10× |
| ≥ 3.23 | Elevated | 1.15× |

### Worked example — Agriculture, Forestry and Fishing

| Input | Value | Why |
|---|--:|---|
| Classification (structural) score | **4.12** | Structurally cyclical — weather- and commodity-exposed, concentrated revenue |
| → Employment YoY | −5.1% | Falling employment → high employment score |
| → EBITDA margin | 14.6% | Mid → moderate margin score |
| → Demand proxy YoY | +58% | Strong (volatile base effect) → low demand score |
| Macro (current-conditions) score | **3.20** | Average of the five components above |

**Blend:** `0.55 × 4.12 + 0.45 × 3.20 = 3.71` → **Elevated** band (≥ 3.23) → **1.15× PD overlay**.

That `1.15×` is the deal-level industry overlay a PD model multiplies through. These are
point-in-time, illustrative current-conditions overlays — *not* calibrated PD estimates.

### All 18 ANZSIC divisions, scored

![Australian industry credit-risk scores by ANZSIC division — base risk score 1 (low) to 5 (high), coloured by risk band](docs/charts/industry_risk_scores.png)

Headline: **4 industries score Elevated, 2 Moderate-high, 12 Medium** (as of 2026-06-16;
[`industry_risk_scores.csv`](outputs/contracts/industry_risk_scores.csv)). No industry currently
sits in the Low or High band.

| Industry | Classification | Macro | Base score | Level | PD overlay |
| --- | --: | --: | --: | --- | --: |
| Agriculture, Forestry and Fishing | 4.12 | 3.20 | **3.71** | Elevated | 1.15× |
| Mining | 3.88 | 2.80 | **3.39** | Elevated | 1.15× |
| Manufacturing | 3.50 | 3.20 | **3.36** | Elevated | 1.15× |
| Retail Trade | 3.25 | 3.20 | **3.23** | Elevated | 1.15× |
| Wholesale Trade | 3.12 | 3.20 | 3.16 | Moderate-high | 1.10× |
| Arts and Recreation Services | 2.38 | 3.80 | 3.02 | Moderate-high | 1.10× |
| Accommodation and Food Services | 2.75 | 2.60 | 2.68 | Medium | 1.00× |
| Construction | 2.75 | 2.60 | 2.68 | Medium | 1.00× |
| Transport, Postal and Warehousing | 2.50 | 2.80 | 2.64 | Medium | 1.00× |
| Information Media and Telecommunications | 2.12 | 3.00 | 2.52 | Medium | 1.00× |
| Public Administration and Safety | 1.62 | 3.60 | 2.51 | Medium | 1.00× |
| Education and Training | 1.75 | 3.40 | 2.49 | Medium | 1.00× |
| Rental, Hiring and Real Estate Services | 2.38 | 2.60 | 2.48 | Medium | 1.00× |
| Administrative and Support Services | 2.12 | 2.80 | 2.43 | Medium | 1.00× |
| Other Services | 2.38 | 2.20 | 2.30 | Medium | 1.00× |
| Electricity, Gas, Water and Waste Services | 2.25 | 2.00 | 2.14 | Medium | 1.00× |
| Health Care and Social Assistance | 1.50 | 2.80 | 2.08 | Medium | 1.00× |
| Professional, Scientific and Technical Services | 1.75 | 2.40 | 2.04 | Medium | 1.00× |

*Per-industry component detail and the source rows behind every number are in **Section 5** of
the [Technical report](outputs/reports/Industry_Analysis_Q1_2026_Technical.md).*

---

## What this produces

**Eight CSV "contracts"** in [`outputs/contracts/`](outputs/contracts/) — the stable interface
any downstream PD / LGD / ECL model reads: `industry_risk_scores`, `downturn_overlay_table`,
`macro_regime_flags`, `macro_scenario_paths`, `portfolio_macro_sensitivity`,
`property_market_overlays`, `industry_financial_benchmarks` (APG 220 §64 ratios per industry),
plus the explainability panels (`business_cycle_panel`, `property_cycle_panel`,
`property_market_overlays_by_building_type`).

**A two-variant report** in [`outputs/reports/`](outputs/reports/) — Board and Technical, each in
`.md` / `.html` / `.docx` (links at the top of this README).

### What this demonstrates (for a credit-risk role)

| Area | In this project |
| --- | --- |
| **PD overlays** | Per-industry base risk scores and a `pd_multiplier` per ANZSIC division, ready to condition a PD model or scorecard. |
| **Stress testing** | Base / mild / moderate / severe macro paths routed to per-product and per-industry PD / LGD / EAD drivers, plus portfolio-wide multipliers and property haircuts. |
| **LGD / collateral** | Property-market overlays (cycle stage, softness, region risk) feeding LGD and collateral assumptions. |
| **APRA APG 220 grounding** | Per-industry medians of the financial ratios APG 220 §64 names as standard credit-assessment benchmarks. |
| **Australian regulatory landscape** | Works directly with ABS industry / building-approval / labour releases, the RBA cash-rate table and FSR, and the Payment Times Reporting Scheme. |
| **Data engineering & governance** | ETL from XLSX / CSV / PDF into validated CSV contracts; source inventory + lineage in every report; reproducible outputs; pytest suite; real-data-only discipline with assumptions labelled, never presented as data. |

Written in **Python** (pandas, openpyxl, pdfplumber, python-docx, matplotlib). The skills transfer
directly to SAS / SQL / R model-development and validation work.

---

## Running it — one command

```bash
python -m venv .venv
.venv\Scripts\activate                 # Windows; macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py
```

`run_pipeline.py` auto-downloads the real public data (ABS / RBA / PTRS); if any source is
unreachable it falls back to a committed real-data cache, so it always produces the reports —
online or offline. The flow runs end to end: **fetch → build panels + overlays → export the 8 CSV
contracts → validate → render the Board + Technical report**. The data vintage is pinned
(`DATA_AS_OF = 2026-02-28`); the committed cache and its source attribution live in
[`data/cache/`](data/cache/). Methodology notes:
[cash-flow lending](docs/methodology_cash_flow_lending.md) and
[property-backed lending](docs/methodology_property_backed_lending.md).

---

## Data sources (all real, public)

| Source | Provides |
| --- | --- |
| ABS — Australian Industry (8155.0), Business Indicators (5676.0), Labour Force (6291.0) | Industry financial ratios, activity, employment |
| ABS — Building Approvals, non-residential (8731.0) | Property-cycle and segment signals |
| RBA — F1 cash-rate table, Financial Stability Review, SMP, Chart Pack | Rate regime and stress context |
| Payment Times Reporting Scheme (PTRS) | Payment-stress signal |

---

## How this fits with my other projects

This repo is the **macro / industry / property overlay** layer of a single commercial credit-risk
stack — the upstream context a lender applies *before* modelling individual borrowers:

| Layer | Repo | What it does |
| --- | --- | --- |
| **Macro & industry overlays** | **this repo** | ABS/RBA/PTRS → industry risk scores, property overlays, downturn stress |
| **External benchmarks** | [external-benchmark](https://github.com/Jane511/external-benchmark) | Bank & regulator Pillar 3 disclosures → PD / LGD / EAD reference points |
| **Consumer modelling** | [consumer-credit-pd-ead-scorecard](https://github.com/Jane511/consumer-credit-pd-ead-scorecard) | Borrower-level PD / EAD scorecards |
| **Mortgage modelling** | mortgage PD/LGD/EAD repo *(link pending)* | Property-backed PD / LGD / EAD |

The flow: **macro/industry overlays + external benchmarks → modelling → validation.** This repo is
*top-down* (sector data from ABS/RBA/PTRS); `external-benchmark` is *bottom-up* (bank/regulator
disclosures). The modelling repos consume both.

## Scope — what it does and does not decide

The engine assembles and scores **public, sector-level** signals into reusable overlays. It
deliberately does **not** set a borrower's final PD, an internal-portfolio LGD, a regulatory
capital number, or any loan-level model — those belong to the modelling repos that consume these
overlays. Keeping that boundary sharp — public reference data here, modelling judgement there — is
what makes the outputs trustworthy as an industry benchmark.

---

*Built by Jane Wu. Real public data only (ABS/RBA/PTRS); a sector-level reference layer, not a
firm-level credit model. Released under the [MIT License](LICENSE).*
