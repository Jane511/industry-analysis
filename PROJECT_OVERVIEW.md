# Project Overview - industry-analysis

This repo is the commercial industry-risk and macro-overlay layer in the public credit-risk stack. It translates public-data-style sector signals into reusable tables that can feed borrower scoring, LGD interpretation, stress testing, and pricing workflows.

## Portfolio role

`industry-analysis` is the Australian industry-risk and macro-overlay engine for the non-mortgage commercial portfolio.

## Upstream inputs

- Australian public-data style sector and macro inputs staged under `data/`
- retained `data/output/` reference-layer tables used by the legacy support layer

## Downstream consumers

- `PD-and-scorecard-commercial`
- `LGD-commercial`
- `expected-loss-engine-commercial`
- `stress-testing-commercial`
- `RAROC-pricing-and-return-hurdle`

## Current structure choice

- `outputs/` is the canonical top-level output convention for the current portfolio-facing artifacts.
- `outputs/reports/` and `outputs/tables/` hold the active report pack and chart-linked tables.
- `outputs/legacy/` and `docs/legacy/` are reserved for archived reviewer material and methodology references.
- `data/output/` remains part of the reference-layer build and is separate from the top-level output convention.

## Key deliverables

- Portfolio-facing tables in `outputs/tables`
- Current methodology and assumptions in `docs/`
- Current report-pack artifacts in `outputs/reports`
- Archived reviewer references in `outputs/legacy/` and `docs/legacy/`
- End-to-end Codex demo pipeline: `python -m src.codex_run_pipeline`
