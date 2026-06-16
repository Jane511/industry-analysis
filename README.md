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

---

## 1. Macro conditions for credit assessment & risk management

A lender's loss rate is driven as much by *the environment it lends into* as by any single
borrower. Before scoring an industry or a deal, the engine reads where the economy currently
sits — these are the **economy-wide conditions a credit team assesses against**, each at its
latest observed level from a named public series. They form the **base** of every stress
scenario and condition PD and LGD across the whole book.

| Macro condition | Current level | What it signals for credit risk | Source |
|---|---|---|---|
| GDP growth (real, YoY) | 1.8% | Below-trend growth — softer revenue, slower deleveraging | ABS 5206 National Accounts |
| Unemployment rate | 4.1% | Low — supports household & SME debt-servicing | ABS 6202 Labour Force |
| Cash rate | 4.35% (+0.5pp YoY) | Restrictive — debt-servicing pressure on leveraged borrowers | RBA F1 (live) |
| Inflation (CPI, YoY) | 3.2% | Above target — cost-of-living squeeze on cash flow | ABS 6401 CPI |
| Wage growth (WPI, YoY) | 3.5% | Roughly matching CPI — thin real-income buffer | ABS 6345 Wage Price Index |
| House-price growth (YoY) | 4.0% | Positive — supportive residential collateral | ABS 6416 Residential Property Price Index |
| Exchange rate (TWI, change) | 0.0% | Stable — neutral for FX-exposed corporates | RBA F11 |
| Industry / sector output (YoY) | 2.0% | Modest — sector-revenue channel for SME / corporate | ABS 8155 + 5676 |
| Commercial-property prices | 0.0% | *assumption* — flat, anchored to RBA FSR commentary | *assumption* |
| Office vacancy rate | 12.0% | *assumption* — elevated, office segment under pressure | *assumption* |
| CRE rents | 0.0% | *assumption* | *assumption* |
| CRE cap rates | 6.0% | *assumption* | *assumption* |

**Macro regime (latest, as of 2026-06-15):** cash-rate regime **restrictive / rising**,
arrears **Low / Improving**, overall macro-regime flag **base**
([`macro_regime_flags.csv`](outputs/contracts/macro_regime_flags.csv)). The cash-rate regime is
real RBA F1; the arrears level/trend is a labelled qualitative assumption from the RBA FSR.

*A "base" regime means the engine applies no recession overlay at current readings — but it
pre-computes the stress dials in Section 2 so a downturn can be costed instantly.*

---

## 2. Macro drivers for stress testing — per product and per industry

Stress testing asks: *if conditions deteriorate, how much worse does expected loss get, and for
whom?* The engine takes the Section 1 base levels and pushes them through four scenarios —
**base → mild → moderate → severe** — then routes each shocked driver to the products and
industries it actually moves.

### 2a. The macro drivers that get shocked

Twelve drivers, each with a base level (Section 1) and an illustrative shock path. Mild is
calibrated to the Basel CRE36.51 minimum (two consecutive quarters of ~zero GDP growth); severe
is a GFC-like but plausible path. The four CRE rows are labelled assumptions.

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
Source: [`macro_scenario_paths.csv`](outputs/contracts/macro_scenario_paths.csv).

A portfolio-wide downturn overlay translates these paths into the headline PD / LGD / CCF
multipliers (and property-value haircut) a model multiplies through —
[`downturn_overlay_table.csv`](outputs/contracts/downturn_overlay_table.csv):

| Scenario | PD × | LGD × | CCF × | Property haircut |
|---|--:|--:|--:|--:|
| base | 1.0 | 1.0 | 1.00 | 0.00 |
| mild | 1.2 | 1.1 | 1.05 | 0.05 |
| moderate | 1.5 | 1.2 | 1.10 | 0.10 |
| severe | 2.0 | 1.3 | 1.20 | 0.20 |

### 2b. Which drivers stress which product

Different lending products fail for different reasons, so each portfolio is stressed against the
drivers that matter to it (illustrative weights, not estimated betas — the weights inside each
PD / LGD / EAD parameter sum to 1.0). Source:
[`portfolio_macro_sensitivity.csv`](outputs/contracts/portfolio_macro_sensitivity.csv).

| Product / portfolio | PD driven mainly by | LGD driven mainly by | EAD driven mainly by |
|---|---|---|---|
| **Residential mortgages** | unemployment (.45), cash rate (.25), wage growth (.20) | **house prices (.70)**, unemployment (.20) | cash rate (.50), unemployment (.30) |
| **Credit cards** | unemployment (.50), wage growth (.30), inflation (.20) | unemployment (.50), inflation (.30) | GDP (.40), cash rate (.35) |
| **SME lending** | GDP (.35), unemployment (.25), cash rate (.20), sector output (.20) | CRE prices (.45), house prices (.35), sector output (.20) | cash rate (.40), GDP (.35), sector output (.25) |
| **Corporate lending** | GDP (.40), sector output (.30), cash rate (.15), FX (.15) | sector output (.45), CRE prices (.30), FX (.25) | cash rate (.45), GDP (.35), sector output (.20) |
| **Commercial property (CRE)** | CRE prices (.30), vacancy (.30), rents (.20), cash rate (.20) | CRE prices (.40), cap rates (.35), rents (.25) | cash rate (.50), vacancy (.30) |
| **Development finance** | CRE prices (.35), GDP (.25), vacancy (.20), cash rate (.20) | CRE prices (.55), cap rates (.25), rents (.20) | cash rate (.45), CRE prices (.30), GDP (.25) |

How to read it: residential mortgage **LGD** is overwhelmingly a **house-price** story (collateral
channel), while its **PD** is a **labour-market and rate** story (debt-servicing). CRE and
development finance pivot on **property values, vacancy and cap rates**; SME and corporate pivot
on **GDP and sector output**. The roll-up is demonstrated on a committed demo book — illustrative
portfolio EL ≈ **1.9× mild, 3.2× moderate, 5.6× severe** (exposure-weighted, no diversification
benefit, per APG 113 para 92).

### 2c. Which drivers stress which industry

Industries are stressed through their own current-conditions inputs — the same components that
feed the score in Section 3. Demand growth is a volatile approvals/indicator proxy (base
effects), so it is read alongside employment and margins, not alone. Source:
[`business_cycle_panel.csv`](outputs/contracts/business_cycle_panel.csv).

| Industry | Employment YoY | EBITDA margin | Demand YoY | Macro (current-conditions) score |
|---|--:|--:|--:|--:|
| Agriculture, Forestry and Fishing | −5.1% | 14.6% | +58% | 3.20 |
| Mining | −5.1% | 47.3% | — | 2.80 |
| Manufacturing | −0.9% | 9.2% | +56% | 3.20 |
| Retail Trade | −0.5% | 7.8% | +68% | 3.20 |
| Wholesale Trade | −8.7% | 6.1% | +69% | 3.20 |
| Arts and Recreation Services | −5.8% | 13.5% | −56% | 3.80 |

For SME and corporate books these industry signals connect directly to the **sector-output**
driver in the per-product table above: a sector with falling employment and thin margins is
exactly where the sector-output shock bites hardest. Full per-industry detail for all 18
divisions is **Section 5** of the Technical report.

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
