# Australian Industry & Property Risk Reference Layer

**A reproducible Python pipeline that turns public Australian macro, industry,
and property data into credit-risk overlays — industry risk scores, property
cycle signals, and PD/LGD downturn-stress multipliers — with a board-ready
report.**

Lenders need to know which industries and property segments are getting
riskier *before* it shows up in arrears. This project reads public data from
the ABS, RBA, ASIC, and the Payment Times Reporting Scheme, scores all 18
ANZSIC industry divisions and 5 commercial-property segments, and emits a set
of model-ready CSV "contracts" plus a plain-English report a credit committee
can read.

Every figure traces back to a named public source and a reporting date, and
the same inputs always produce the same outputs — the discipline a model-risk
or credit-risk function expects.

---

## What this project demonstrates

A portfolio project for credit-risk / quantitative-modelling roles. What it shows:

| Area | In this project |
| --- | --- |
| **PD overlays** | Per-industry base risk scores (classification + macro) and a `pd_multiplier` per ANZSIC division, ready to condition a PD model or scorecard. |
| **LGD / collateral** | Property-market overlays (cycle stage, softness, region risk) and property-value haircuts feeding LGD and collateral assumptions. |
| **Stress testing** | A downturn-overlay table with base / mild / moderate / severe PD, LGD, and CCF multipliers and property haircuts for scenario and EL analysis. |
| **IFRS 9 / ECL inputs** | Industry failure rates, financial benchmarks, and macro-context panels that anchor current-state ECL and challenger overlays. |
| **Regulatory grounding (APRA APG 220)** | Per-industry medians of the financial ratios APG 220 §64 names as standard credit-assessment benchmarks (EBITDA margin, wages-to-sales, inventory days, sales/employment growth). |
| **Australian regulatory landscape** | Works directly with ABS industry/building/CPI/labour releases, the RBA cash-rate table, FSR/SMP, ASIC insolvency series, and the Payment Times Reporting Scheme. |
| **Data engineering & governance** | ETL from XLSX/CSV/PDF into validated CSV contracts; a full source inventory and lineage in every report; reproducible outputs; and a 148-test pytest suite. |

Written in **Python** (pandas, openpyxl, pdfplumber, python-docx). The skills
transfer directly to SAS/SQL/R model-development and validation work.

---

## What it produces

**Eleven CSV "contracts"** in [`outputs/contracts/`](outputs/contracts/) — the
stable interface any downstream PD/LGD/ECL model reads:

| Contract | What it provides |
| --- | --- |
| `industry_risk_scores.csv` | Per-industry classification + macro + base risk score, band, and PD multiplier |
| `property_market_overlays.csv` | Per-segment cycle stage, softness, region risk, PD multiplier |
| `downturn_overlay_table.csv` | Base/mild/moderate/severe PD, LGD, CCF multipliers + property haircuts |
| `macro_regime_flags.csv` | Cash-rate regime, arrears level/trend, macro regime flag |
| `industry_failure_rates.csv` | Realised insolvency rate per ANZSIC division (ASIC ÷ ABS active businesses) |
| `industry_financial_benchmarks.csv` | APG 220 §64 financial ratios per industry |
| `business_cycle_panel.csv` / `property_cycle_panel.csv` | Wide diagnostics behind the overlays |
| `macro_context.csv` | CPI/PPI/labour/cash-rate macro panel |
| `property_market_detail.csv` / `..._by_building_type.csv` | Multi-source property panels |

**A two-variant report** in [`outputs/reports/`](outputs/reports/) —
`Industry_Analysis_Q1_2026_Board` and `_Technical`, each in `.md` / `.html` /
`.docx`. The **Board** variant opens with a plain-English executive summary
(what the numbers mean for credit risk) and headline figures; the **Technical**
variant adds full source inventory, transformations, lineage, and validation.

A sample of the headline picture this cycle: the cash rate is 3.85% (−0.25pp
over the year) with a low/improving arrears backdrop, so the macro regime is
`base`; **4 of 18 industries score Elevated**, **0 of 5 property segments are
in downturn**, and the severe scenario applies **2.0× PD**.

---

## How it works

```text
   Public sources                 This engine                    Outputs
 ┌──────────────────────┐   ┌────────────────────────────┐   ┌──────────────┐
 │ ABS industry / build │   │ public_data/  download+load │   │ 11 CSV       │
 │ approvals / CPI / PPI │──▶│ panels/       build panels  │──▶│ contracts    │
 │ RBA cash rate, FSR    │   │ overlays/     risk scores,  │   │              │
 │ ASIC insolvency       │   │               downturn,     │   │ Board +      │
 │ Payment Times (PTRS)  │   │               property      │   │ Technical    │
 │ Cotality/Domain/SQM   │   │ reporting/    render report │   │ md/html/docx │
 └──────────────────────┘   └────────────────────────────┘   └──────────────┘
```

Two ideas hold the design together:

- **Every number is traceable.** The report carries a full source inventory and
  a transformation table — each contract lists its inputs, builder script, row
  count, and validation status. Synthetic development stubs are labelled as
  such, never silently presented as real data.
- **The same inputs always produce the same outputs.** No randomness, no hidden
  state; rerunning the pipeline on the same staged data yields identical
  contracts, which is what makes the outputs auditable.

---

## Running it

```bash
# 1. Install
python -m venv .venv
.venv\Scripts\activate                 # Windows; macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 2. Download / stage public inputs (network-dependent)
python src/download_public_data.py

# 3. Build panels, overlays, and the CSV contracts
python src/build_public_panels.py
python src/export_contracts.py
python src/validate_upstream.py

# 4. Render the board + technical report (markdown / html / docx)
python src/build_board_report.py --format all --output outputs/reports/Industry_Analysis_Q1_2026
```

Methodology is documented in
[`docs/methodology_cash_flow_lending.md`](docs/methodology_cash_flow_lending.md)
and
[`docs/methodology_property_backed_lending.md`](docs/methodology_property_backed_lending.md).

---

## Data sources

| Source | Provides |
| --- | --- |
| ABS — Australian Industry (8155.0), Business Indicators (5676.0), Labour Force (6291.0) | Industry financial ratios, activity, employment |
| ABS — Building Approvals (8731.0), Property Price Indexes (6416.0/6432.0) | Property cycle and segment signals |
| ABS — CPI (6401.0), PPI (6427.0) | Macro-context panel |
| RBA — F1 cash-rate table, Financial Stability Review, SMP, Chart Pack | Rate regime and stress context |
| ASIC — insolvency series (Series 1A) | Realised industry failure rates |
| Payment Times Reporting Scheme | Payment-stress signal |
| Cotality, Domain, SQM, state rental bond authorities | Property detail panel |

---

## Repository layout

```text
industry-analysis/
├── src/
│   ├── public_data/            # Download + load ABS / RBA / ASIC / PTRS inputs
│   ├── panels/                 # Business-cycle, property-cycle, macro panels
│   ├── overlays/               # Industry risk scores, downturn + property overlays
│   ├── reporting/              # Report builder + markdown/html/docx renderers
│   ├── validation.py           # Risk bands + upstream validation
│   ├── build_board_report.py   # CLI: render the report (entry point)
│   ├── build_public_panels.py  # CLI: build panels
│   ├── export_contracts.py     # CLI: write the 11 CSV contracts
│   └── validate_upstream.py    # CLI: check inputs before a build
├── outputs/
│   ├── contracts/              # The 11 model-ready CSV contracts
│   └── reports/                # Board + Technical report (md / html / docx)
├── data/                       # Staged + processed public data (raw is gitignored)
├── tests/                      # 148 tests (unit + report-render integration)
└── docs/                       # Methodology notes
```

---

## Scope — what it does and does not decide

The engine assembles and scores **public, sector-level** signals into reusable
overlays. It deliberately does **not** set a borrower's final PD, an
internal-portfolio LGD, or a regulatory capital number — those are calibration
decisions that belong to the PD/LGD/ECL model that consumes these overlays.
Keeping that boundary sharp — public reference data here, modelling judgement
there — is what makes the outputs trustworthy as an industry benchmark.

---

*Built by Jane Wu. Public data only; sector-level reference layer, not a
firm-level credit model.*
