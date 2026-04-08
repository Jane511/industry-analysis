# Australian Industry Risk Analysis for Credit Assessment

This repository is a portfolio project that demonstrates how Australian public data can be converted into an APRA-informed, bank-inspired industry risk framework for credit analysis.

The project uses downloaded ABS and RBA datasets to build:
- industry classification risk views
- macro and sector trend overlays
- deterministic benchmark ratios where public data does not publish banking metrics directly
- sector archetype borrower scorecards
- pricing, policy, concentration, stress testing, ESG, and watchlist outputs
- a formal chart report for portfolio presentation

## What This Project Demonstrates

This repository is designed to show an interviewer that the project can:
- translate public macro and industry data into credit-relevant signals
- structure industry analysis using concepts commonly seen in Australian bank credit risk frameworks
- separate directly observed public metrics from derived and hard-coded banking assumptions
- turn qualitative sector judgement into repeatable scoring logic
- connect industry analysis to illustrative downstream credit decisions such as pricing, policy, concentration, and monitoring
- present technical work in a clear portfolio format rather than only as code

The repository does not claim to reproduce any bank's internal risk model, internal rating methodology, pricing engine, or portfolio MIS. Where public data does not provide a banking field directly, the project uses transparent proxy logic and synthetic examples.

## Current Headline Findings

Based on the latest generated outputs:
- Highest current industry base risk score: `Agriculture, Forestry And Fishing` at `3.50`
- Joint highest current industry base risk score: `Manufacturing` at `3.50`
- Lowest current industry base risk score: `Transport, Postal and Warehousing` at `2.14`
- Highest current borrower archetype score: `Agriculture, Forestry And Fishing Archetype` at `3.09`
- 2 current sector concentration breaches: `Retail Trade` and `Wholesale Trade`
- Highest concentration utilisation: `Retail Trade` at `113.3%` of limit
- Weakest employment trend: `Wholesale Trade` at `-8.7%` YoY
- Largest average stress scenario uplift: `Demand shock`

## How To Read The Repository

If you are reviewing this repository as an interviewer, the most useful reading order is:

1. [Executive Summary](output/executive_summary.md)
2. [Formal PDF Report](industry_risk_formal_report.pdf)
3. [Clean Methodology Reference](METHODOLOGY.md)
4. [Output Data Provenance](docs/output_data_provenance.md)
5. [Australian Bank Practice Review](docs/australian_bank_industry_risk_practice_review.md)

## How It Works

- Uses public ABS, RBA, and PTRS data as the starting point for all sector analysis.
- Builds structural industry scores first, then overlays current macro, margin, inventory, employment, demand, and rate signals.
- Converts public sector signals into benchmark-style credit metrics such as AR days, AP days, inventory days, leverage, and coverage.
- Generates one synthetic borrower archetype per industry so the sector view can be translated into a borrower-style scorecard.
- Separates working-capital analysis into AR, AP, inventory, cash-conversion-cycle, and PD / LGD-style overlays.
- Combines structural, macro, and borrower views into one final industry risk score for each borrower archetype.
- Maps the results into illustrative pricing, policy, concentration, stress-testing, ESG, and watchlist outputs.
- Produces a workbook-backed executive summary, chart pack, notebooks, and formal PDF report for reviewer-friendly presentation.

## Repository Structure

```text
industry-risk-analysis-australia/
├── METHODOLOGY.md
├── data/
│   ├── methodology.md         # Technical appendix
│   ├── raw/public/            # Downloaded ABS / RBA / PTRS input files
│   └── processed/             # Intermediate pipeline outputs
├── notebooks/
│   ├── 01_results_and_report_walkthrough.ipynb
│   ├── 02_methodology_and_output_map.ipynb
│   └── README.md
├── docs/
│   ├── data_sources.md
│   ├── output_data_provenance.md
│   ├── australian_bank_industry_risk_practice_review.md
│   └── README.md
├── scripts/
│   └── run_pipeline.py        # Main entrypoint
├── src/                       # Implementation modules
│   ├── foundation.py
│   ├── macro.py
│   ├── benchmarks.py
│   ├── borrowers.py
│   ├── working_capital.py
│   ├── portfolio.py
│   ├── credit.py
│   ├── pipeline.py
│   └── ...
├── output/
│   ├── executive_summary.md   # Portfolio-facing outputs
│   ├── chart_explanations.md
│   ├── charts/                # Temporary chart workspace
│   └── tables/                # Generated CSV output tables
├── industry_risk_formal_report.pdf
├── tests/
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Main Deliverables

### Portfolio-facing documents
- [Executive Summary](output/executive_summary.md)
- [Chart Explanations](output/chart_explanations.md)
- [Formal Report PDF](industry_risk_formal_report.pdf)

### Reference documents
- [Docs Index](docs/README.md)
- [Clean Methodology Reference](METHODOLOGY.md)
- [Technical Methodology Appendix](data/methodology.md)
- [Notebook Index](notebooks/README.md)
- [Data Sources](docs/data_sources.md)
- [Output Data Provenance](docs/output_data_provenance.md)
- [Australian Bank Practice Review](docs/australian_bank_industry_risk_practice_review.md)

### Core generated outputs
- `output/tables/industry_base_risk_scorecard.csv`
- `output/tables/industry_public_benchmarks.csv`
- `output/tables/industry_generated_benchmarks.csv`
- `output/tables/industry_working_capital_risk_metrics.csv`
- `output/tables/borrower_working_capital_risk_metrics.csv`
- `output/tables/borrower_industry_risk_scorecard.csv`
- `output/tables/pricing_grid.csv`
- `output/tables/policy_overlay.csv`
- `output/tables/concentration_limits.csv`
- `output/tables/watchlist_triggers.csv`
- `output/tables/chart_table.csv`

### Guided notebooks
- [Results Walkthrough](notebooks/01_results_and_report_walkthrough.ipynb)
- [Methodology and Output Map](notebooks/02_methodology_and_output_map.ipynb)

## Script and Output Numbering

To make the workflow easier to follow, the repo uses this numbered script-to-output map:

1. `Script 1`: `scripts/download_ptrs_public_data.py`
   `Output 1.1`: Cycle 8 PTRS PDF
   `Output 1.2`: Cycle 9 PTRS PDF
   `Output 1.3`: PTRS guidance PDF
   `Workbook 1.4`: `data/raw/public/ptrs/PTRS_MultiCycle_AR_Days_Model_Official.xlsx`

2. `Script 2`: `scripts/rebuild_ptrs_workbook.py`
   `Workbook 2.1`: `data/raw/public/ptrs/PTRS_MultiCycle_AR_Days_Model_Official.xlsx`

3. `Script 3`: `scripts/run_pipeline.py`
   `Table 3.1`: `output/tables/industry_base_risk_scorecard.csv`
   `Table 3.2`: `output/tables/industry_public_benchmarks.csv`
   `Table 3.3`: `output/tables/industry_generated_benchmarks.csv`
   `Table 3.4`: `output/tables/industry_working_capital_risk_metrics.csv`
   `Table 3.5`: `output/tables/borrower_working_capital_risk_metrics.csv`
   `Table 3.6`: `output/tables/borrower_industry_risk_scorecard.csv`
   `Table 3.7`: `output/tables/pricing_grid.csv`
   `Table 3.8`: `output/tables/policy_overlay.csv`
   `Table 3.9`: `output/tables/concentration_limits.csv`
   `Table 3.10`: `output/tables/watchlist_triggers.csv`
   `Table 3.11`: `output/tables/industry_credit_appetite_strategy.csv`
   `Table 3.12`: `output/tables/industry_stress_test_matrix.csv`
   `Table 3.13`: `output/tables/industry_esg_sensitivity_overlay.csv`
   `Table 3.14`: `output/tables/industry_portfolio_proxy.csv`
   `Table 3.15`: `output/tables/chart_table.csv`
   `Workbook 3.16`: `data/processed/industry_risk_reporting_workbook.xlsx`
   `Report 3.17`: `output/executive_summary.md`
   `Report 3.18`: `output/chart_explanations.md`
   `Report 3.19`: `industry_risk_formal_report.pdf`

## Project Logic

The pipeline follows nine layers:

1. `Foundation`
Maps target sectors to ANZSIC-aligned industry views and produces structural classification scores.

2. `Macro View`
Adds employment, profitability, inventory, demand, and cash-rate signals from ABS and RBA.

3. `Benchmarks`
Builds industry benchmark proxies. Public EBITDA margin is used directly; inventory days are estimated from ABS quarterly inventories/sales ratios where available; leverage, coverage, and the remaining working-capital metrics are generated from deterministic rules where public datasets do not publish them directly.

4. `Working Capital`
Builds separate AR, AP, inventory, cash-conversion-cycle, and PD / scorecard / LGD overlay metrics so working-capital signals can be reviewed independently from the core borrower scorecard.

5. `Bottom-Up`
Generates one synthetic borrower archetype per sector and scores it against the sector benchmark set.

6. `Scorecard`
Combines classification, macro, and bottom-up views into a final borrower industry risk score.

7. `Credit Application`
Maps risk results into illustrative pricing, policy, and concentration outputs.

8. `Bank Practice Overlay`
Adds industry appetite strategy, stress testing, and ESG sensitivity outputs aligned to APRA themes and observed Australian bank disclosure practice.

9. `Reporting`
Generates a workbook-backed chart pack, generated executive summary, and consolidated PDF report.

## Maintained Source Modules

The live `src/` package is now organised by analysis domain rather than by legacy build-script naming:

- `src/foundation.py`: structural industry classification signals
- `src/macro.py`: macro, demand, inventory, and rate signals
- `src/benchmarks.py`: benchmark proxy construction including PTRS-linked AR/AP inputs
- `src/borrowers.py`: borrower archetype generation and final borrower scorecard
- `src/working_capital.py`: AR, AP, inventory, CCC, and PD/LGD overlay metrics
- `src/portfolio.py`: appetite, stress, ESG, concentration, exposure proxy, and watchlist outputs
- `src/credit.py`: pricing and borrower policy overlays
- `src/reporting.py`: workbook, chart metadata, and PDF generation
- `src/visualisation.py`: chart rendering helpers
- `src/load_public_data.py` and `src/ptrs_reconstruction.py`: data ingestion and PTRS reconstruction utilities

## Public Data Used

The live pipeline currently uses six raw public files:
- ABS Australian Industry 2023-24
- ABS Business Indicators profit ratio
- ABS Business Indicators inventory ratio
- ABS Labour Force Detailed by industry
- ABS Building Approvals non-residential
- RBA cash rate table F1

The pipeline can also use:
- PTRS multi-cycle AR/AP benchmark workbook reconstructed automatically from official Payment Times Reporting Scheme publications

See [Data Sources](docs/data_sources.md) for the full list with local file names, source URLs, and usage.

## Important Limitation

This project is intentionally transparent about what is public and what is not.

The following banking fields are not published directly in the ABS/RBA public data used here, so they remain explicit non-public assumptions inside the workflow:
- sector debt / EBITDA benchmarks
- sector ICR benchmarks
- sector AP day benchmarks when PTRS is not supplied
- direct official industry inventory-turnover-days series
- borrower-level financial statements
- bank portfolio exposure by sector
- bank pricing and policy settings

AR and AP days are no longer treated as purely generic proxy formulas when PTRS source files are available: the pipeline downloads the official publications, reconstructs the workbook automatically, and then uses those public payment-times tables as the primary AR/AP benchmark source.
Inventory days are also no longer handled as a simple annualised placeholder. The pipeline now estimates inventory days from ABS quarterly inventories/sales ratios using a quarter-length conversion and a margin-based COGS proxy, with a separate stock-build risk flag and a transparent fallback for sectors where the ABS ratio is unavailable.

To stage the latest official PTRS source files into the repo, run:

```bash
python scripts/download_ptrs_public_data.py
```

That script downloads the official Cycle 8 and Cycle 9 PTRS PDFs and automatically reconstructs `data/raw/public/ptrs/PTRS_MultiCycle_AR_Days_Model_Official.xlsx` for pipeline use.

If the PDFs are already staged locally and you only want to rebuild the workbook, run:

```bash
python scripts/rebuild_ptrs_workbook.py
```

The same limitation applies to internal borrower grades, true portfolio concentrations, exception tracking, covenant compliance, and workout data. Those are not replicated here.

The repository documents those assumptions in:
- [Clean Methodology Reference](METHODOLOGY.md)
- [Technical Methodology Appendix](data/methodology.md)
- [Output Data Provenance](docs/output_data_provenance.md)
- [Executive Summary](output/executive_summary.md)

## Run The Project

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py
```

Outputs are generated to:
- `data/processed/`
- `output/tables/`
- `output/`

## Run Tests

```bash
pytest tests/
```

## Why This Is Portfolio-Relevant

This project is not only a data pipeline. It is intended to show end-to-end credit thinking:
- how industry analysis can feed borrower decisioning
- how portfolio controls can be linked to sector risk
- how prudential expectations can be translated into practical analytics
- how to present technical credit work clearly for senior stakeholders

## Usage Note

This repository is for education and portfolio demonstration. It is not production credit advice and does not represent any individual bank's internal model, policy, or delegated authority framework.
