# Australian Property & Industry Risk Reference Layer

## Purpose

This repository now acts as a reusable reference layer for downstream:

- property-backed PD overlays
- LGD overlays
- EL scenario engines
- broader property and industry portfolio monitoring

The repo is not positioned as a final PD, LGD, or EL model. Its job is to stage public Australian inputs, convert them into reusable reference tables, and expose those outputs cleanly to downstream projects.

## Current Reference-Layer Outputs

The live build now generates four property-reference outputs:

- `data/output/region_risk/region_risk_table.csv`
- `data/output/property_cycle/property_cycle_table.csv`
- `data/output/arrears_environment/base_arrears_environment.csv`
- `data/output/downturn_overlays/property_downturn_overlays.csv`

It also retains the original industry-analysis workflow and report pack under `output/` as a legacy layer.

## Current Staged Source Coverage

The property-reference layer currently uses these staged local files:

- `ABS Building Approvals (Non-residential)` through `February 2026`
- `RBA F1 cash-rate table` snapshot published `2 April 2026`, latest staged observation dated `16 March 2026`

The repo does not yet include staged local files for:

- `ABS Building Activity`
- `ABS Lending Indicators`
- `APRA` property or arrears context

Because those inputs are not yet staged, the current build is intentionally transparent about its fallbacks:

- the region table is currently a national segment-level reference table rather than a state/regional geography table
- building-activity fields fall back to approvals-trend proxies when no staged activity extract exists
- housing-finance and arrears context fall back to the RBA cash-rate backdrop plus the local transformation-instruction baseline

Those fallbacks are labelled explicitly in the output `source_note` fields.

## Build Workflow

Run the full repo build:

```bash
python scripts/run_pipeline.py
```

Run only the reference-layer outputs:

```bash
python scripts/run_reference_layer.py
```

Run tests:

```bash
pytest tests/
```

## Reference-Layer Build Logic

1. Load staged ABS approvals, the RBA cash-rate series, and any optional ABS/APRA/RBA property extracts.
2. Build processed property-reference summaries under `data/processed/property/`.
3. Convert those summaries into region risk bands and property-cycle bands.
4. Publish one macro arrears environment table and one illustrative downturn-overlay table.
5. Leave final loan-level PD, LGD, and EL calculations to downstream repos.

## Legacy Industry Workflow

The remaining sections of this README describe the original industry-analysis workflow that is still included in the repo for continuity and reviewer context.

### Sample Outputs / Charts / Screenshots

| Industry | Base Risk Score | Risk Level | Employment YoY | Demand YoY |
| --- | --- | --- | --- | --- |
| Agriculture, Forestry And Fishing | 3.50 | Elevated | -5.1% | 58.4% |
| Manufacturing | 3.50 | Elevated | -0.9% | 55.5% |
| Wholesale Trade | 3.23 | Elevated | -8.7% | 69.3% |
| Retail Trade | 3.23 | Elevated | -0.5% | 68.5% |
| Accommodation And Food Services | 2.68 | Medium | 0.7% | 113.7% |

- Quick-review deliverables: `output/executive_summary.md`, `output/chart_explanations.md`, and `industry_risk_formal_report.pdf`

![Highest current industry base risk scores](output/charts/readme_industry_base_risk_scores.png)

## What This Project Demonstrates

This repository is designed to show that the project can:
- translate public macro and industry data into credit-relevant signals
- structure industry analysis using concepts commonly seen in prudential credit risk frameworks
- separate directly observed public metrics from derived and hard-coded banking assumptions
- turn qualitative sector judgement into repeatable scoring logic
- connect industry analysis to illustrative downstream credit decisions such as pricing, policy, concentration, and monitoring
- present technical work in a clear portfolio format rather than only as code

The repository does not claim to reproduce any institution's internal risk model, internal rating methodology, pricing engine, or portfolio MIS. Where public data does not provide an internal credit field directly, the project uses transparent proxy logic and synthetic examples.

## Legacy Industry Headline Findings

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

If you want the current reference-layer workflow, read in this order:

1. [Docs Index](docs/README.md)
2. [Project Overview](docs/project_overview.md)
3. [Region Risk Methodology](docs/methodology_region_risk.md)
4. [Property Cycle Methodology](docs/methodology_property_cycle.md)
5. [Arrears Environment Methodology](docs/methodology_arrears_environment.md)
6. [Downturn Overlay Methodology](docs/methodology_downturn_overlays.md)

If you want the retained legacy industry workflow and report pack, read in this order:

1. [Executive Summary](output/executive_summary.md)
2. [Formal PDF Report](industry_risk_formal_report.pdf)
3. [Clean Methodology Reference](METHODOLOGY.md)
4. [Output Data Provenance](docs/output_data_provenance.md)
5. [APRA Practice Alignment Review](docs/australian_bank_industry_risk_practice_review.md)

## How The Legacy Industry Layer Works

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
industry-risk-reference-layer/
├── README.md
├── requirements.txt
├── .gitignore
├── METHODOLOGY.md
├── data/
│   ├── raw/
│   │   ├── abs/
│   │   ├── apra/
│   │   ├── rba/
│   │   ├── manual/
│   │   └── public/
│   ├── processed/
│   │   ├── property/          # Current reference-layer processed tables
│   │   └── industry/          # Current legacy industry processed tables
│   └── output/
│       ├── region_risk/
│       ├── property_cycle/
│       ├── arrears_environment/
│       └── downturn_overlays/
├── notebooks/                 # Reference-layer scaffolds plus legacy walkthroughs
│   ├── README.md
│   └── ...
├── docs/
│   ├── project_overview.md
│   ├── methodology_region_risk.md
│   ├── methodology_property_cycle.md
│   ├── methodology_arrears_environment.md
│   ├── methodology_downturn_overlays.md
│   ├── methodology_arrears.md            # Compatibility copy
│   ├── methodology_downturn.md           # Compatibility copy
│   ├── limitations_and_assumptions.md
│   ├── data_sources.md
│   ├── output_data_provenance.md
│   ├── australian_bank_industry_risk_practice_review.md
│   └── README.md
├── scripts/
│   ├── run_reference_layer.py
│   └── run_pipeline.py
├── src/
│   ├── reference_layer.py
│   ├── data_loader_abs.py
│   ├── data_loader_apra.py
│   ├── data_loader_rba.py
│   ├── region_risk.py
│   ├── property_cycle.py
│   ├── arrears_environment.py
│   ├── downturn_overlay.py
│   ├── foundation.py
│   ├── macro.py
│   ├── benchmarks.py
│   ├── borrowers.py
│   ├── working_capital.py
│   ├── portfolio.py
│   ├── credit.py
│   ├── reporting.py
│   └── ...
├── output/                    # Legacy industry-analysis report pack
├── industry_risk_formal_report.pdf
├── tests/
├── pyproject.toml
└── transform.pdf
```

## Main Deliverables

### Current reference-layer documents
- [Docs Index](docs/README.md)
- [Project Overview](docs/project_overview.md)
- [Region Risk Methodology](docs/methodology_region_risk.md)
- [Property Cycle Methodology](docs/methodology_property_cycle.md)
- [Arrears Environment Methodology](docs/methodology_arrears_environment.md)
- [Downturn Overlay Methodology](docs/methodology_downturn_overlays.md)
- [Limitations And Assumptions](docs/limitations_and_assumptions.md)
- [Notebook Index](notebooks/README.md)

### Legacy industry documents and report pack
- [Executive Summary](output/executive_summary.md)
- [Chart Explanations](output/chart_explanations.md)
- [Formal Report PDF](industry_risk_formal_report.pdf)
- [Clean Methodology Reference](METHODOLOGY.md)
- [Data Sources](docs/data_sources.md)
- [Output Data Provenance](docs/output_data_provenance.md)
- [APRA Practice Alignment Review](docs/australian_bank_industry_risk_practice_review.md)

### Current reference-layer outputs
- `data/output/region_risk/region_risk_table.csv`
- `data/output/property_cycle/property_cycle_table.csv`
- `data/output/arrears_environment/base_arrears_environment.csv`
- `data/output/downturn_overlays/property_downturn_overlays.csv`

### Legacy industry generated outputs
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

### Guided legacy notebooks
- [Results Walkthrough](notebooks/01_results_and_report_walkthrough.ipynb)
- [Methodology and Output Map](notebooks/02_methodology_and_output_map.ipynb)

## Script and Output Numbering

To make the workflow easier to follow, the repo uses this numbered script-to-output map. `scripts/run_pipeline.py` is the full build and calls the reference-layer pipeline at the end; `scripts/run_reference_layer.py` runs only the reference-layer subset.

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
   `Workbook 3.16`: `data/processed/industry/industry_risk_reporting_workbook.xlsx`
   `Report 3.17`: `output/executive_summary.md`
   `Report 3.18`: `output/chart_explanations.md`
   `Report 3.19`: `industry_risk_formal_report.pdf`

4. `Script 4`: `scripts/run_reference_layer.py`
   `Table 4.1`: `data/processed/property/building_approvals_segment_metrics.csv`
   `Table 4.2`: `data/processed/property/building_activity_segment_metrics.csv`
   `Table 4.3`: `data/processed/property/housing_finance_segment_metrics.csv`
   `Table 4.4`: `data/processed/property/cash_rate_reference_summary.csv`
   `Table 4.5`: `data/processed/property/reference_input_availability.csv`
   `Table 4.6`: `data/output/region_risk/region_risk_table.csv`
   `Table 4.7`: `data/output/property_cycle/property_cycle_table.csv`
   `Table 4.8`: `data/output/arrears_environment/base_arrears_environment.csv`
   `Table 4.9`: `data/output/downturn_overlays/property_downturn_overlays.csv`

## Legacy Industry Project Logic

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

8. `Practice Alignment Overlay`
Adds industry appetite strategy, stress testing, and ESG sensitivity outputs aligned to APRA themes and public prudential disclosure references.

9. `Reporting`
Generates a workbook-backed chart pack, generated executive summary, and consolidated PDF report.

## Maintained Source Modules

The live `src/` package now has two maintained layers.

### Current reference-layer modules

- `src/reference_layer.py`: orchestrates the current property-reference build
- `src/data_loader_abs.py`: approvals, building-activity, and lending-indicator staging
- `src/data_loader_apra.py`: optional APRA property-context staging
- `src/data_loader_rba.py`: cash-rate and housing-context staging
- `src/region_risk.py`: region-risk reference table generation
- `src/property_cycle.py`: property-cycle and softness-band generation
- `src/arrears_environment.py`: base arrears-environment output
- `src/downturn_overlay.py`: PD / LGD / CCF / value-haircut scenario overlays

### Legacy industry modules

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

## Legacy Industry Data Used

The retained industry pipeline currently uses six raw public files:
- ABS Australian Industry 2023-24
- ABS Business Indicators profit ratio
- ABS Business Indicators inventory ratio
- ABS Labour Force Detailed by industry
- ABS Building Approvals non-residential
- RBA cash rate table F1

The pipeline can also use:
- PTRS multi-cycle AR/AP benchmark workbook reconstructed automatically from official Payment Times Reporting Scheme publications

See [Data Sources](docs/data_sources.md) for the full list with local file names, source URLs, and usage.

## Legacy Industry Data Vintages

The current legacy industry model run in this repository is based on these staged source periods:

- `ABS Australian Industry`: FY `2022-23` and FY `2023-24` annual values from the `2023-24` release. Refresh annually when the next release is available.
- `ABS Business Indicators - Gross Operating Profit / Sales Ratio`: quarterly series through `December 2025`. Refresh quarterly.
- `ABS Business Indicators - Inventories / Sales Ratio`: quarterly series through `December 2025`. Refresh quarterly.
- `ABS Labour Force, Australia, Detailed`: monthly industry series through `February 2026`. Refresh monthly.
- `ABS Building Approvals - Non-Residential`: monthly series through `February 2026`. Refresh monthly.
- `RBA F1 cash-rate table`: local CSV snapshot published `2 April 2026`, with the latest staged daily observation dated `16 March 2026`. Refresh when a newer RBA snapshot is staged or when the policy-rate series changes.
- `PTRS`: Cycle `8` (`July 2025`) and Cycle `9` (`January 2026`) publications, plus `March 2025` guidance used to rebuild the local PTRS workbook. Refresh when a new PTRS cycle publication is released.

The current reference-layer staged inputs are summarised near the top of this README and in [Docs Index](docs/README.md).

After any of those source files are refreshed, rerun `python scripts/run_pipeline.py` so the CSV outputs, workbook, markdown summaries, and PDF report are rebuilt from the new vintages.

## Important Limitation

This project is intentionally transparent about what is public and what is not.

The following banking fields are not published directly in the ABS/RBA public data used here, so they remain explicit non-public assumptions inside the workflow:
- sector debt / EBITDA benchmarks
- sector ICR benchmarks
- sector AP day benchmarks when PTRS is not supplied
- direct official industry inventory-turnover-days series
- borrower-level financial statements
- internal portfolio exposure by sector
- internal pricing and policy settings

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
- [Limitations And Assumptions](docs/limitations_and_assumptions.md)
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

This repository is for education and structured analysis. It is not production credit advice and does not represent any institution's internal model, policy, or delegated authority framework.
