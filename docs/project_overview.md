# Project Overview

## Positioning

`industry-analysis` is the public commercial portfolio's industry-risk and macro-overlay repo. Its primary role is to convert public-data-style sector signals into reusable tables for borrower scoring, LGD interpretation, stress testing, and pricing workflows.

The repo also retains two supporting layers:

- `data/output/` for the property and reference-layer tables
- `docs/legacy/` and `outputs/legacy/` for archived methodology notes and earlier reviewer-reference material

## Canonical Output Convention

The top-level canonical output convention for the current repo narrative is `outputs/`.

That means:

- `outputs/tables/` is the main current portfolio-facing output contract
- `outputs/reports/`, `outputs/charts/`, and `outputs/samples/` hold the current reviewer-facing artifacts
- `outputs/legacy/` is reserved only for archived reference material rather than the active report-pack location

## Current Portfolio Output Set

The current portfolio-facing outputs are:

- `outputs/tables/industry_risk_score_table.csv`
- `outputs/tables/benchmark_ratio_reference_table.csv`
- `outputs/tables/downturn_overlay_table.csv`
- `outputs/tables/market_softness_overlay.csv`
- `outputs/tables/concentration_support_table.csv`
- `outputs/tables/pipeline_validation_report.csv`

## Supporting Reference-Layer Output Set

The retained supporting reference-layer outputs are:

- `data/output/region_risk/region_risk_table.csv`
- `data/output/property_cycle/property_cycle_table.csv`
- `data/output/arrears_environment/base_arrears_environment.csv`
- `data/output/downturn_overlays/property_downturn_overlays.csv`

## Data Status

The current staged local build uses:

- `ABS Building Approvals (Non-residential)` through `February 2026`
- `RBA F1 cash-rate data` with the latest staged observation dated `16 March 2026`
- legacy industry source tables staged through the vintages documented in `output_data_provenance.md`

Some optional property-context inputs are still not staged locally, so the reference-layer outputs remain more limited than the main industry and macro overlay layer.

## Build Flow

1. Load staged public sector, macro, and portfolio-proxy inputs.
2. Build the main industry and macro overlay outputs used by the public commercial stack.
3. Build or refresh the supporting reference-layer tables in `data/output/`.
4. Keep older methodology notes and archived reviewer references in `docs/legacy/` and `outputs/legacy/`.

## Legacy Layer

The legacy analytical layer remains in the repo for continuity with older notebooks and reviewer materials. It is useful context, but the active report-pack and current table outputs now sit under `outputs/`.
