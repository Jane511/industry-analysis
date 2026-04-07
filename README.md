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
- Highest current industry base risk score: `Health Care and Social Assistance` at `3.32`
- Lowest current industry base risk score: `Transport, Postal and Warehousing` at `1.95`
- Highest current borrower archetype score: `Health Care & Social Assistance Archetype` at `2.97`
- No current sector breaches concentration limits
- Highest concentration utilisation: `Retail Trade` at `85.0%` of limit
- Weakest employment trend: `Wholesale Trade` at `-8.7%` YoY
- Largest average stress scenario uplift: `Demand shock`

## How To Read The Repository

If you are reviewing this repository as an interviewer, the most useful reading order is:

1. [Executive Summary](docs/deliverables/executive_summary.md)
2. [Formal PDF Report](docs/deliverables/industry_risk_formal_report.pdf)
3. [Methodology](docs/reference/methodology.md)
4. [Output Data Provenance](docs/reference/output_data_provenance.md)
5. [Australian Bank Practice Review](docs/research/australian_bank_industry_risk_practice_review.md)

## Repository Structure

```text
industry-risk-analysis-australia/
├── docs/
│   ├── deliverables/          # Portfolio-facing outputs
│   ├── reference/             # Methodology, data sources, provenance
│   ├── research/              # Supporting research notes
│   └── README.md              # Docs index
├── scripts/
│   └── run_pipeline.py        # Main entrypoint
├── src/                       # Implementation modules
├── data/
│   ├── raw/public/            # Downloaded ABS / RBA input files
│   └── processed/             # Intermediate pipeline outputs
├── output/
│   ├── charts/                # Temporary chart workspace
│   └── tables/                # Generated CSV output tables
├── tests/
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Main Deliverables

### Portfolio-facing documents
- [Executive Summary](docs/deliverables/executive_summary.md)
- [Chart Explanations](docs/deliverables/chart_explanations.md)
- [Formal Report PDF](docs/deliverables/industry_risk_formal_report.pdf)

### Reference documents
- [Docs Index](docs/README.md)
- [Methodology](docs/reference/methodology.md)
- [Data Sources](docs/reference/data_sources.md)
- [Output Data Provenance](docs/reference/output_data_provenance.md)
- [Australian Bank Practice Review](docs/research/australian_bank_industry_risk_practice_review.md)

### Core generated outputs
- `output/tables/industry_base_risk_scorecard.csv`
- `output/tables/industry_public_benchmarks.csv`
- `output/tables/industry_generated_benchmarks.csv`
- `output/tables/borrower_industry_risk_scorecard.csv`
- `output/tables/pricing_grid.csv`
- `output/tables/policy_overlay.csv`
- `output/tables/concentration_limits.csv`
- `output/tables/watchlist_triggers.csv`
- `output/tables/chart_table.csv`

## Project Logic

The pipeline follows eight layers:

1. `Foundation`
Maps target sectors to ANZSIC-aligned industry views and produces structural classification scores.

2. `Macro View`
Adds employment, profitability, inventory, demand, and cash-rate signals from ABS and RBA.

3. `Benchmarks`
Builds industry benchmark proxies. Public EBITDA margin is used directly; leverage, coverage, and working-capital metrics are generated from deterministic rules because public datasets do not publish them directly.

4. `Bottom-Up`
Generates one synthetic borrower archetype per sector and scores it against the sector benchmark set.

5. `Scorecard`
Combines classification, macro, and bottom-up views into a final borrower industry risk score.

6. `Credit Application`
Maps risk results into illustrative pricing, policy, and concentration outputs.

7. `Bank Practice Overlay`
Adds industry appetite strategy, stress testing, and ESG sensitivity outputs aligned to APRA themes and observed Australian bank disclosure practice.

8. `Reporting`
Generates a workbook-backed chart pack and consolidated PDF report.

## Public Data Used

The live pipeline currently uses six raw public files:
- ABS Australian Industry 2023-24
- ABS Business Indicators profit ratio
- ABS Business Indicators inventory ratio
- ABS Labour Force Detailed by industry
- ABS Building Approvals non-residential
- RBA cash rate table F1

See [Data Sources](docs/reference/data_sources.md) for the full list with local file names, source URLs, and usage.

## Important Limitation

This project is intentionally transparent about what is public and what is not.

The following banking fields are not published directly in the ABS/RBA public data used here, so they remain explicit non-public assumptions inside the workflow:
- sector debt / EBITDA benchmarks
- sector ICR benchmarks
- sector AR / AP day benchmarks
- borrower-level financial statements
- bank portfolio exposure by sector
- bank pricing and policy settings

The same limitation applies to internal borrower grades, true portfolio concentrations, exception tracking, covenant compliance, and workout data. Those are not replicated here.

The repository documents those assumptions in:
- [Methodology](docs/reference/methodology.md)
- [Output Data Provenance](docs/reference/output_data_provenance.md)
- [Executive Summary](docs/deliverables/executive_summary.md)

## Run The Project

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py
```

Outputs are generated to:
- `data/processed/`
- `output/tables/`
- `docs/deliverables/`

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
