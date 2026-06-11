# Australian Industry & Property Risk Reference Layer

**Turns real public Australian data (ABS / RBA / PTRS) into credit-risk
overlays — industry risk scores, property-cycle signals, and downturn PD/LGD
stress multipliers — with a board-ready report.**

> **Real public data only.** This repo uses only real public sources
> (ABS, RBA, PTRS). All synthetic / staged / illustrative data has been
> removed; the only non-data inputs are clearly-labelled methodology
> *assumptions* (stress multipliers, scoring weights).

## See it in 30 seconds

- **One export:** [`outputs/contracts/industry_risk_scores.csv`](outputs/contracts/industry_risk_scores.csv) — every ANZSIC industry scored 1–5 with a PD multiplier.
- **One notebook:** [`notebooks/00_repo_overview.ipynb`](notebooks/00_repo_overview.ipynb) — the guided tour.
- **One picture:**

![Industry credit-risk scores](docs/charts/industry_risk_scores.png)

---

## Why this matters for credit risk

A lender's loss rate is driven as much by *where* it lends — which industries
and property segments — as by individual borrowers. This engine reads public
data and answers three questions a credit-risk team asks every cycle, in a
form a PD/LGD/ECL model can consume directly:

- **Industry / sector risk scoring** — which of the 18 ANZSIC divisions are
  structurally or cyclically riskier right now, as a 1–5 score and a ready-to-use
  `pd_multiplier` per division.
- **Downturn / stress overlays** — base / mild / moderate / severe PD, LGD, and
  CCF multipliers plus property-value haircuts for scenario and expected-loss
  analysis.
- **Macro-cycle positioning** — where the rate and arrears cycle sits, as a
  single regime flag that conditions PD and LGD.

Everything traces back to a named public source and reporting date, and the
same inputs always produce the same outputs — the discipline a model-risk or
validation function expects.

---

## What this produces

**Eight CSV "contracts"** in [`outputs/contracts/`](outputs/contracts/) — the
stable interface any downstream PD/LGD/ECL model reads. Live samples from the
current real-data build:

**`industry_risk_scores.csv`** — top 5 of 18 industries by risk:

| ANZSIC | Industry | Base risk score | Band | PD multiplier |
| --- | --- | --- | --- | --- |
| A | Agriculture, Forestry and Fishing | 3.71 | Elevated | 1.15 |
| B | Mining | 3.39 | Elevated | 1.15 |
| C | Manufacturing | 3.36 | Elevated | 1.15 |
| G | Retail Trade | 3.23 | Elevated | 1.15 |
| F | Wholesale Trade | 3.16 | Moderate-high | 1.10 |

**`downturn_overlay_table.csv`** — stress multipliers (methodology *assumptions*,
nudged by real ABS property softness):

| Scenario | PD × | LGD × | CCF × | Property haircut |
| --- | --- | --- | --- | --- |
| base | 1.0 | 1.0 | 1.00 | 0.00 |
| mild | 1.2 | 1.1 | 1.05 | 0.05 |
| moderate | 1.5 | 1.2 | 1.10 | 0.10 |
| severe | 2.0 | 1.3 | 1.20 | 0.20 |

![Downturn stress multipliers](docs/charts/downturn_multipliers.png)

**`macro_regime_flags.csv`** — current cycle position (cash-rate regime is real
RBA F1; arrears level/trend is a labelled qualitative assumption from the RBA FSR):
`cash_rate_regime = neutral_easing`, `arrears = Low / Improving`,
`macro_regime_flag = base` (as of 2026-03-16).

**`property_market_overlays.csv`** — 5 segments (4 from real ABS Cat. 8731
non-residential approvals; RES is a labelled placeholder pending ABS Cat. 8752):
CRE / RET / CON are *slowing* (softness 2.9–3.2, PD ×1.1); IND and RES *neutral*.

Plus **`industry_financial_benchmarks.csv`** (APG 220 §64 ratios per industry)
and three explainability panels (`business_cycle_panel`, `property_cycle_panel`,
`property_market_overlays_by_building_type`).

**A two-variant report** in [`outputs/reports/`](outputs/reports/) —
`Industry_Analysis_Q1_2026_Board` and `_Technical` in `.md` / `.html` / `.docx`.
The **Board** variant opens with a plain-English executive summary; the
**Technical** variant adds full source inventory, transformations, and validation.

### Not included (pending real data)

Three exports were **removed** because they could not be built from real public
data without staging additional sources. They will return — with no synthetic
fallback — once the real source is staged:

| Removed export | Real source it needs |
| --- | --- |
| `industry_failure_rates` | ASIC Series 1A insolvency statistics ÷ ABS Counts of Australian Businesses (Cat. 8165.0) |
| `property_market_detail` | ABS Residential Property Price Indexes (Cat. 6416.0 / 6432.0) + city/region series |
| `macro_context` | ABS CPI (Cat. 6401.0) and PPI (Cat. 6427.0) |

---

## What this demonstrates (for a credit-risk role)

| Area | In this project |
| --- | --- |
| **PD overlays** | Per-industry base risk scores and a `pd_multiplier` per ANZSIC division, ready to condition a PD model or scorecard. |
| **LGD / collateral** | Property-market overlays (cycle stage, softness, region risk) feeding LGD and collateral assumptions. |
| **Stress testing** | Base / mild / moderate / severe PD, LGD, CCF multipliers + property haircuts for scenario and EL analysis. |
| **APRA APG 220 grounding** | Per-industry medians of the financial ratios APG 220 §64 names as standard credit-assessment benchmarks. |
| **Australian regulatory landscape** | Works directly with ABS industry/building-approval/labour releases, the RBA cash-rate table and FSR, and the Payment Times Reporting Scheme. |
| **Data engineering & governance** | ETL from XLSX/CSV/PDF into validated CSV contracts; source inventory + lineage in every report; reproducible outputs; 124-test pytest suite; real-data-only discipline with assumptions labelled, never presented as data. |

Written in **Python** (pandas, openpyxl, pdfplumber, python-docx, matplotlib).
The skills transfer directly to SAS/SQL/R model-development and validation work.

---

## How it works

```text
   Real public sources           This engine                    Outputs
 ┌──────────────────────┐   ┌────────────────────────────┐   ┌──────────────┐
 │ ABS industry /       │   │ public_data/  load inputs   │   │ 8 CSV        │
 │   building approvals │──▶│ panels/       build panels  │──▶│ contracts    │
 │ RBA F1 cash rate,FSR │   │ overlays/     risk scores,  │   │              │
 │ Payment Times (PTRS) │   │               downturn,     │   │ Board +      │
 │                      │   │               property      │   │ Technical    │
 │                      │   │ reporting/    render report │   │ md/html/docx │
 └──────────────────────┘   └────────────────────────────┘   └──────────────┘
```

Two ideas hold the design together:

- **Every number is traceable, and assumptions are labelled.** The report
  carries a full source inventory and a transformation table. Methodology
  assumptions (stress multipliers, the qualitative arrears baseline) are marked
  `ASSUMPTION` in the data itself — never presented as observed data.
- **The same inputs always produce the same outputs.** No randomness, no hidden
  state; rerunning on the same real inputs yields identical contracts.

---

## Running it — one command

Clone, install, run. **`run_pipeline.py` auto-downloads the real public data
(ABS/RBA/PTRS); if any source is unreachable it falls back to a committed
real-data cache**, so it always produces the reports — online or offline.

```bash
python -m venv .venv
.venv\Scripts\activate                 # Windows; macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py
```

That runs the whole flow end to end: **fetch real data (live → cache fallback)
→ build panels + overlays → export the 8 CSV contracts → validate → render the
Board + Technical report** (md / html / docx). Outputs land in `outputs/`
(contracts in `outputs/contracts/`, reports in `outputs/reports/`). The data
vintage is pinned (`DATA_AS_OF = 2026-02-28`); the committed cache and its
source attribution live in [`data/cache/`](data/cache/).

Each run prints, per source, whether it came from the **live** download or the
**cache**. To regenerate the parquet mirrors + README charts: `python src/make_readme_assets.py`.

Methodology is documented in
[`docs/methodology_cash_flow_lending.md`](docs/methodology_cash_flow_lending.md)
and
[`docs/methodology_property_backed_lending.md`](docs/methodology_property_backed_lending.md).

---

## Data sources (all real, public)

| Source | Provides |
| --- | --- |
| ABS — Australian Industry (8155.0), Business Indicators (5676.0), Labour Force (6291.0) | Industry financial ratios, activity, employment |
| ABS — Building Approvals, non-residential (8731.0) | Property-cycle and segment signals |
| RBA — F1 cash-rate table, Financial Stability Review, SMP, Chart Pack | Rate regime and stress context |
| Payment Times Reporting Scheme (PTRS) | Payment-stress signal |

---

## Repository layout

```text
industry-analysis/
├── run_pipeline.py             # ONE command: fetch -> build -> validate -> report
├── src/
│   ├── public_data/
│   │   ├── fetch_public_data.py   # Live download (ABS/RBA/PTRS) + cache fallback
│   │   └── ...                    # Loaders for the ABS/RBA inputs
│   ├── panels/                 # Business-cycle and property-cycle panels
│   ├── overlays/               # Industry risk scores, downturn + property overlays
│   ├── reporting/              # Report builder + markdown/html/docx renderers
│   ├── export_contracts.py     # Write the 8 CSV contracts
│   ├── build_board_report.py   # Render the report
│   └── make_readme_assets.py   # Parquet mirrors + README charts
├── outputs/
│   ├── contracts/              # The 8 model-ready CSV contracts
│   └── reports/                # Board + Technical report (md / html / docx)
├── notebooks/                  # 00–05 guided walkthrough
├── docs/                       # Methodology notes + charts/
├── data/
│   ├── cache/                  # Committed real-data snapshot (fallback) + ATTRIBUTION
│   ├── raw/                    # Live-fetched inputs (gitignored)
│   └── processed/              # Intermediate panels
└── tests/                      # 124 tests (unit + report-render + fetch fallback)
```

---

## How this fits with my other projects

This repo is the **macro / industry / property overlay** layer of a single
commercial credit-risk stack — the upstream context a lender applies *before*
modelling individual borrowers:

| Layer | Repo | What it does |
| --- | --- | --- |
| **Macro & industry overlays** | **this repo** | ABS/RBA/PTRS → industry risk scores, property overlays, downturn stress |
| **External benchmarks** | [external-benchmark](https://github.com/Jane511/external-benchmark) | Bank & regulator Pillar 3 disclosures → PD / LGD / EAD reference points |
| **Consumer modelling** | [consumer-credit-pd-ead-scorecard](https://github.com/Jane511/consumer-credit-pd-ead-scorecard) | Borrower-level PD / EAD scorecards |
| **Mortgage modelling** | mortgage PD/LGD/EAD repo *(link pending)* | Property-backed PD / LGD / EAD |

The flow: **macro/industry overlays + external benchmarks → modelling →
validation**. This repo and `external-benchmark` are complementary — this one is
*top-down* (sector data from ABS/RBA/PTRS); `external-benchmark` is *bottom-up*
(bank/regulator disclosures). The modelling repos consume both.

---

## Scope — what it does and does not decide

The engine assembles and scores **public, sector-level** signals into reusable
overlays. It deliberately does **not** set a borrower's final PD, an
internal-portfolio LGD, a regulatory capital number, or any loan-level model —
those belong to the modelling repos that consume these overlays. Keeping that
boundary sharp — public reference data here, modelling judgement there — is what
makes the outputs trustworthy as an industry benchmark.

---

*Built by Jane Wu. Real public data only (ABS/RBA/PTRS); a sector-level
reference layer, not a firm-level credit model.*
