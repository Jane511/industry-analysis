# Project Overview - industry-analysis

`industry-analysis` is the upstream public-data and overlay repo in the commercial credit-risk portfolio stack.

This overview is written so a non-technical reviewer can understand what the repo does, what it produces, and what it does not do.

## One-Sentence Summary

This repo converts public Australian macro/industry/property datasets into reusable overlay tables and exports them as stable contract files for downstream credit modelling projects.

## Scope

This repo owns:

- public-data ingestion (download + optional staged manual extracts)
- public-data cleaning and standardisation
- business-cycle, macro-regime, industry-risk, and property-cycle panel construction
- canonical overlay exports for downstream repos

This repo does not own:

- loan-level model fitting (PD/LGD/EAD/cure/path)
- borrower scorecard engines (as decision systems)
- pricing decision engines
- portfolio stress engines

## Who Uses This Repo (Downstream)

Downstream repos typically consume `data/exports/*.parquet` and then:

- fit borrower/facility models (PD/LGD/EL)
- run portfolio stress scenarios
- apply pricing overlays and return-hurdle logic
- produce portfolio reporting and governance packs

## Canonical Output Contract

All downstream repos should consume exports under `data/exports/`.

Core downstream contract (required):

- `industry_risk_scores.parquet`: ranked industry overlay table for downstream conditioning
- `property_market_overlays.parquet`: property market overlay table for downstream conditioning
- `downturn_overlay_table.parquet`: downturn scenario overlay table (illustrative multipliers/haircuts)
- `macro_regime_flags.parquet`: compact regime flags for conditioning downstream models

Optional explainability exports:

- `business_cycle_panel.parquet`: industry + macro panel used for cash-flow lending overlays
- `property_cycle_panel.parquet`: property-cycle panel used for property-backed lending overlays

Secondary inspection outputs are CSV files in `outputs/tables/`, derived from canonical parquet exports.

## Canonical Scripts (What They Do)

- `scripts/download_public_data.py`: downloads the network-dependent PTRS source PDFs and rebuilds the PTRS workbook reference.
- `scripts/build_public_panels.py`: builds explainability and reference panel CSVs in `data/processed/public/`.
- `scripts/build_overlays.py`: builds overlay tables in-memory for quick sanity checks.
- `scripts/export_contracts.py`: writes canonical parquet exports to `data/exports/` and derives CSV inspection outputs to `outputs/tables/`.
- `scripts/validate_upstream.py`: validates core contract outputs as required and explainability panels as optional.

## Methodology

- Cash-flow lending manual: `docs/methodology_cash_flow_lending.md`
- Property-backed lending manual: `docs/methodology_property_backed_lending.md`

## Primary Execution

```powershell
python -m pip install -r requirements.txt
python scripts/download_public_data.py
python scripts/export_contracts.py
python scripts/validate_upstream.py
```

## Operational Notes

- `scripts/download_public_data.py` requires outbound HTTPS. If your environment blocks network access, stage PTRS files manually under `data/raw/public/ptrs/`.
- Parquet exports require `pyarrow` or `fastparquet`. If exports fail, reinstall dependencies from `requirements.txt`.
