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

Every figure is the **Q1 2026 vintage** — pipeline `DATA_AS_OF = 2026-06-16`. Every quarterly /
monthly ABS series now reports **through the March 2026 quarter** (the end of Q1 2026); the cash
rate is refreshed live. The reference period each real source actually reports for:

| Source / series | Catalogue | Reference period reported |
| --- | --- | --- |
| Australian Industry — financial ratios, structure | ABS 8155.0 | **FY 2023–24** (annual — FY 2024–25 not yet released) |
| Business Indicators — profit / margins | ABS 5676.0 | **Mar 2026 quarter** |
| Business Indicators — inventories | ABS 5676.0 | **Mar 2026 quarter** |
| Labour Force, Detailed — industry employment | ABS 6291.0 | **Mar 2026** |
| Building Approvals, non-residential — property cycle | ABS 8731.0 | **Mar 2026** |
| Cash rate | RBA F1 | **Live** — latest available |
| GDP, unemployment, CPI, WPI | ABS 5206 / 6202 / 6401 / 6345 | **Observed — Mar 2026** (live-fetched + parsed each run) |
| House prices, exchange rate (TWI), sector-output proxy | ABS 6416 *(discontinued 2021)* · RBA F11 · ABS 8155+5676 | **Stated** — no clean current free series |

The four economy-wide headline levels (GDP, unemployment, CPI, WPI) are now **fetched live from the
ABS releases and parsed** ([`download_macro_indicators.py`](src/public_data/download_macro_indicators.py)),
joining the live cash rate; the rest stay stated (the ABS residential price index was discontinued
after Dec-2021, and there is no clean free series for the TWI change or the sector-output proxy).
The macro **stress shocks** in Section 2 are scenario-design assumptions (config vintage `2026-Q1`),
not dated observations. The committed cache + full per-file attribution are in
[`data/cache/ATTRIBUTION.md`](data/cache/ATTRIBUTION.md).

---

## 1. Macro conditions for credit assessment & risk management

A lender's loss rate is driven as much by *the environment it lends into* as by any single
borrower. Before scoring an industry or a deal, the engine reads where the economy and the
property markets currently sit — the conditions a credit team assesses against. The headline rates
are **live-fetched from the latest ABS/RBA releases**; a few series with no clean current public
series are stated (and flagged as such). Together they form the **base** of every stress scenario
in Section 2.

### 1a. Economy-wide conditions

The broad drivers that condition PD and LGD across the whole book, regardless of product.

| Macro condition | Current level | What it signals for credit risk | Source |
|---|---|---|---|
| GDP growth (real, YoY) | 2.5% | Around trend — moderate revenue growth | ABS 5206 (Mar 2026, live) |
| Unemployment rate | 4.3% | Low — supports household & SME debt-servicing | ABS 6202 (Mar 2026, live) |
| Cash rate | 4.35% (+0.5pp YoY) | Restrictive — debt-servicing pressure on leveraged borrowers | RBA F1 (live) |
| Inflation (CPI, YoY) | 2.4% | Back inside the 2–3% band — easing cost-of-living pressure | ABS 6401 (Mar 2026, live) |
| Wage growth (WPI, YoY) | 3.3% | Now outpacing CPI — modest positive real-income growth | ABS 6345 (Mar 2026, live) |
| Exchange rate (TWI, change) | 0.0% | Stable — neutral for FX-exposed corporates | RBA F11 *(stated)* |
| Industry / sector output (YoY) | 2.0% | Modest — sector-revenue channel for SME / corporate | ABS 8155 + 5676 *(stated)* |

### 1b. Property conditions

Property-secured lending splits into **residential** and **commercial** — they sit on different
cycles, so the engine reads them separately.

**Residential property.** The residential signal is **house-price growth: +4.0% YoY** — the
collateral channel for residential mortgages, where a fall lifts mortgage LGD (Section 2b). *This
one is **stated**, not live: the ABS Residential Property Price Index (Cat. 6416) was **discontinued
after the Dec-2021 quarter** and has no clean free replacement index, so it stays a labelled reading
pending a new public source.*

**Commercial property (CRE).** Read two ways:

*(i) Price & yield levels* — labelled **assumptions** (no clean free quarterly public series;
anchored to RBA FSR commentary). These feed the CRE stress paths in Section 2a:

| CRE condition | Current level | Reading |
|---|---|---|
| Commercial-property prices | 0.0% | Flat |
| Office vacancy rate | 12.0% | Elevated — office segment under pressure |
| CRE rents | 0.0% | Flat |
| CRE cap rates | 6.0% | — |

*(ii) Building-type cycle* — **real ABS data** (Cat. 8731 non-residential building approvals,
Mar 2026). This is where CRE risk actually concentrates right now: **offices remain the softest
segment** (a clear downturn), now joined by agricultural buildings, while warehouses are the
firmest (still in growth). The softness score runs 1 (firm) → 5 (soft); "PD if standalone" is the
overlay that segment would carry on its own.

![Commercial property softness by building type, from ABS non-residential building approvals — offices softest, warehouses firmest](outputs/charts/property_market_softness.png)

| Building type | Cycle stage | Softness (1 firm → 5 soft) | Approvals YoY | PD if standalone |
|---|---|--:|--:|--:|
| Offices | downturn | 4.30 | −19.8% | 1.15× |
| Agricultural & aquacultural buildings | downturn | 3.90 | −27.0% | 1.15× |
| Retail & wholesale trade buildings | slowing | 3.40 | +6.5% | 1.15× |
| Education buildings | slowing | 3.25 | −31.3% | 1.15× |
| Aged care facilities | slowing | 3.20 | −22.0% | 1.10× |
| Short-term accommodation buildings | neutral | 3.10 | +112.0% | 1.10× |
| Health buildings | neutral | 2.40 | −36.0% | 1.00× |
| Warehouses | growth | 1.70 | +108.5% | 0.95× |

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

Stress testing answers one question a credit team is always asked: **if the economy turns bad, how
much more does the bank lose?**

A recession doesn't create a loss directly. It first hurts the **borrower** (less income) and the
**collateral** (lower property prices), and *that* shows up three ways — more borrowers default,
the bank loses more on each one, and bigger balances are owing when they do:

> weak economy → borrowers & property hurt → higher **PD**, **LGD**, **EAD** → higher loss

- **PD** *(probability of default)* — the chance a borrower stops paying.
- **LGD** *(loss given default)* — after the collateral is sold, the share of the money owed that
  the bank still loses.
- **EAD** *(exposure at default)* — how much is owed at the moment of default.
- **Loss = PD × LGD × EAD** — push all three up and the loss multiplies quickly.

**What this layer builds.** It turns one economic scenario into a set of **"dials"** — how many
times worse PD, LGD and EAD get for each type of loan. A downstream model multiplies those dials
onto its own loans to get the stressed loss. There are three standard ways to build such dials,
simplest first:

| Method | What it is | Used here? |
| --- | --- | --- |
| **Multiplier** | judgement-based "×2 in a severe recession" factors | ✅ **this layer** — fits simple / sector-level work |
| **Rating migration** | re-grade each borrower under the stressed scenario | a loan-level model would |
| **Statistical model** | a regression trained on years of real default data | a big, data-rich bank would |

This layer uses the **multiplier** method: it works at the public, sector level and needs no
borrower-by-borrower default history. So these are **illustrative dials, not a fitted model** — a
ready-to-use starting overlay, not a calibrated PD. A bank with the data would replace them with a
statistical model and validate it every year.

> **Scope — the engine-room step only.** This layer turns a scenario into PD/LGD/EAD dials and stops
> there; the rest of a real stress test (projecting capital, setting management actions, reporting to
> the board) stays with the modelling and capital teams. Regulatory anchors honoured: `mild` = two
> quarters of ~zero growth (Basel CRE36.51); `severe` is GFC-like but plausible (APS 220 §72); the
> roll-up takes **no diversification benefit** (APG 113 §92); and everything is flagged illustrative,
> to be independently validated in production (APS 220 §76).

### 2a. Step 1 — the economic scenario (the "what if")

Twelve drivers. **`base` is where each sits today** (Section 1); **`mild` / `moderate` / `severe`
add a worsening shock on top** — `mild` is a textbook mild recession (two quarters of ~zero
growth), `severe` is a GFC-like path. Source:
[`macro_scenario_paths.csv`](outputs/contracts/macro_scenario_paths.csv).

| Macro driver | Base | Mild | Moderate | Severe |
|---|--:|--:|--:|--:|
| GDP growth (real, YoY) | 2.5% | 0.7% | −0.8% | −2.8% |
| Unemployment rate | 4.3% | 5.5% | 6.8% | 8.3% |
| Cash rate | 4.35% | 4.6% | 4.85% | 5.1% |
| Inflation (CPI, YoY) | 2.4% | 3.2% | 3.9% | 4.9% |
| Wage growth (WPI, YoY) | 3.3% | 2.8% | 2.3% | 1.5% |
| House-price growth (YoY) | 4.0% | −4.0% | −11.0% | −21.0% |
| Exchange rate (TWI, change) | 0.0% | −5.0% | −10.0% | −15.0% |
| Industry / sector output (YoY) | 2.0% | 0.0% | −2.0% | −5.0% |
| Commercial-property prices* | 0.0% | −7.0% | −15.0% | −28.0% |
| Office vacancy rate* | 12.0% | 14.0% | 16.0% | 19.0% |
| CRE rents* | 0.0% | −4.0% | −9.0% | −16.0% |
| CRE cap rates* | 6.0% | 6.4% | 6.9% | 7.6% |

\* labelled assumption — no clean free quarterly public series.

### 2b. Step 2 — turn the scenario into per-product dials

Different loans break for different reasons, so each product reacts to its **own short list of
drivers**. The number next to each driver is its **share of the blame** for that product — the
shares add up to 100%. It says *which* drivers matter and in what proportion — **not how big the hit
is**. The size of the hit is set separately, by how sensitive that product is (Section 2c). The
arrow shows the bad direction (**↑** = worse when it rises, **↓** = worse when it falls). Source:
[`portfolio_macro_sensitivity.csv`](outputs/contracts/portfolio_macro_sensitivity.csv).

> **Two disciplines the textbooks insist on, both built in.** (1) A driver can legitimately hit PD,
> LGD **and** EAD through *different* channels — e.g. rising unemployment means more defaults *and*
> weaker sale prices *and* more arrears — but you must never **double-count** the *same* effect
> twice. (2) These shares are illustrative, not fitted regression coefficients; in a *severe*
> recession every driver is at its worst at once, so the shares wash out and the product's overall
> sensitivity does the work — the shares matter most in *milder* scenarios, where some drivers move
> more than others.

**Worked example — residential mortgages.** The point is that the three quantities respond to
*different* drivers, so the engine maps them separately:

- **PD** — *will they default?* A jobs-and-rates story: unemployment ↑ (0.45 share), then cash
  rate ↑ (0.25), wage growth ↓ (0.20), inflation ↑ (0.10).
- **LGD** — *how much is lost if they do?* Almost entirely **house prices ↓** (0.70), because
  collateral recovery falls; unemployment and cash rate are minor.
- **EAD** — *how much is owed?* Mostly cash rate ↑ (0.50) and unemployment ↑ (0.30).

The same split for every product (shares in brackets):

| Product / portfolio | PD — main drivers (share) | LGD — main drivers (share) | EAD — main drivers (share) |
|---|---|---|---|
| **Residential mortgages** | unemployment ↑ (0.45), cash rate ↑ (0.25), wage growth ↓ (0.20), inflation ↑ (0.10) | house prices ↓ (0.70), unemployment ↑ (0.20), cash rate ↑ (0.10) | cash rate ↑ (0.50), unemployment ↑ (0.30), GDP ↓ (0.20) |
| **Credit cards** | unemployment ↑ (0.50), wage growth ↓ (0.30), inflation ↑ (0.20) | unemployment ↑ (0.50), inflation ↑ (0.30), wage growth ↓ (0.20) | GDP ↓ (0.40), cash rate ↑ (0.35), unemployment ↑ (0.25) |
| **SME lending** | GDP ↓ (0.35), unemployment ↑ (0.25), cash rate ↑ (0.20), sector output ↓ (0.20) | CRE prices ↓ (0.45), house prices ↓ (0.35), sector output ↓ (0.20) | cash rate ↑ (0.40), GDP ↓ (0.35), sector output ↓ (0.25) |
| **Corporate lending** | GDP ↓ (0.40), sector output ↓ (0.30), cash rate ↑ (0.15), FX ↓ (0.15) | sector output ↓ (0.45), CRE prices ↓ (0.30), FX ↓ (0.25) | cash rate ↑ (0.45), GDP ↓ (0.35), sector output ↓ (0.20) |
| **Commercial property (CRE)** | CRE prices ↓ (0.30), vacancy ↑ (0.30), rents ↓ (0.20), cash rate ↑ (0.20) | CRE prices ↓ (0.40), cap rates ↑ (0.35), rents ↓ (0.25) | cash rate ↑ (0.50), vacancy ↑ (0.30), CRE prices ↓ (0.20) |
| **Development finance** | CRE prices ↓ (0.35), GDP ↓ (0.25), vacancy ↑ (0.20), cash rate ↑ (0.20) | CRE prices ↓ (0.55), cap rates ↑ (0.25), rents ↓ (0.20) | cash rate ↑ (0.45), CRE prices ↓ (0.30), GDP ↓ (0.25) |

The pattern: **household products** (mortgages, cards) pivot on the **labour market**; **business
products** (SME, corporate) on **GDP and sector output**; **property products** (CRE, development
finance) on **property values, vacancy and cap rates**. *(Development finance's textbook drivers —
presales and construction costs — have no free public series, so GDP and office-vacancy stand in as
proxies here.)*

### 2c. Step 3 — the dials a downstream PD/LGD/EAD model plugs in

Combining the scenario (2a) with each product's driver mix (2b) — then scaling by how sensitive the
product is and capping the result — gives **the deliverable**: a PD / LGD / EAD stress multiplier
("dial") for every product, in every scenario
([`macro_stress_segment_multipliers.csv`](outputs/reports/macro_stress_segment_multipliers.csv)).
A monitoring model multiplies these onto its own base numbers; stressed
**loss = stressed PD × stressed LGD × stressed EAD**.

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
| Agriculture, Forestry and Fishing | −5.1% | 14.6% | −27% | 4.20 |
| Mining | −5.1% | 47.3% | — | 3.20 |
| Manufacturing | −0.9% | 9.2% | +95% | 3.40 |
| Retail Trade | −0.5% | 7.8% | +6% | 3.40 |
| Wholesale Trade | −8.7% | 6.1% | +108% | 3.40 |
| Arts and Recreation Services | −5.8% | 13.5% | −46% | 3.60 |

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
| → Demand proxy YoY | −27% | Weak (volatile base effect) → high demand score |
| Macro (current-conditions) score | **4.20** | Average of the five components above |

**Blend:** `0.55 × 4.12 + 0.45 × 4.20 = 4.16` → **Elevated** band (≥ 3.23) → **1.15× PD overlay**.

That `1.15×` is the deal-level industry overlay a PD model multiplies through. These are
point-in-time, illustrative current-conditions overlays — *not* calibrated PD estimates.

### All 18 ANZSIC divisions, scored

![Australian industry credit-risk scores by ANZSIC division — base risk score 1 (low) to 5 (high), coloured by risk band](docs/charts/industry_risk_scores.png)

Headline: **5 industries score Elevated, 2 Moderate-high, 10 Medium, 1 Moderate-low** (as of
2026-06-16; [`industry_risk_scores.csv`](outputs/contracts/industry_risk_scores.csv)). No industry
currently sits in the Low or High band.

| Industry | Classification | Macro | Base score | Level | PD overlay |
| --- | --: | --: | --: | --- | --: |
| Agriculture, Forestry and Fishing | 4.12 | 4.20 | **4.16** | Elevated | 1.15× |
| Mining | 3.88 | 3.20 | **3.57** | Elevated | 1.15× |
| Manufacturing | 3.50 | 3.40 | **3.46** | Elevated | 1.15× |
| Retail Trade | 3.25 | 3.40 | **3.32** | Elevated | 1.15× |
| Wholesale Trade | 3.12 | 3.40 | **3.25** | Elevated | 1.15× |
| Construction | 2.75 | 3.20 | 2.95 | Moderate-high | 1.10× |
| Arts and Recreation Services | 2.38 | 3.60 | 2.93 | Moderate-high | 1.10× |
| Accommodation and Food Services | 2.75 | 2.60 | 2.68 | Medium | 1.00× |
| Public Administration and Safety | 1.62 | 3.60 | 2.51 | Medium | 1.00× |
| Education and Training | 1.75 | 3.40 | 2.49 | Medium | 1.00× |
| Rental, Hiring and Real Estate Services | 2.38 | 2.60 | 2.48 | Medium | 1.00× |
| Transport, Postal and Warehousing | 2.50 | 2.40 | 2.46 | Medium | 1.00× |
| Administrative and Support Services | 2.12 | 2.80 | 2.43 | Medium | 1.00× |
| Information Media and Telecommunications | 2.12 | 2.60 | 2.34 | Medium | 1.00× |
| Other Services | 2.38 | 2.20 | 2.30 | Medium | 1.00× |
| Electricity, Gas, Water and Waste Services | 2.25 | 2.00 | 2.14 | Medium | 1.00× |
| Health Care and Social Assistance | 1.50 | 2.80 | 2.08 | Medium | 1.00× |
| Professional, Scientific and Technical Services | 1.75 | 2.00 | 1.86 | Moderate-low | 0.95× |

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
(`DATA_AS_OF = 2026-06-16`); the committed cache and its source attribution live in
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
