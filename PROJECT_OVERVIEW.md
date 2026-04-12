# Project Overview - industry-analysis

This repo is the commercial industry-risk and macro-overlay layer in the public credit-risk stack. It translates public-data-style sector signals into reusable tables that can feed borrower scoring, LGD interpretation, stress testing, and pricing workflows.

## Portfolio role

`industry-analysis` is the Australian industry-risk and macro-overlay engine for the non-mortgage commercial portfolio.

## Current structure choice

- `outputs/` is the canonical top-level output convention for the current portfolio-facing artifacts.
- `output/` is a retained legacy report-pack directory kept only for older reviewer material and compatibility with older notebooks.
- `data/output/` remains part of the reference-layer build and is separate from the top-level output convention.

## Key deliverables

- Portfolio-facing tables in `outputs/tables`
- Current methodology and assumptions in `docs/`
- Legacy report-pack references retained in `output/` and the root legacy files
- End-to-end Codex demo pipeline: `python -m src.codex_run_pipeline`
