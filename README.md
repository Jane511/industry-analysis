# Commercial Industry Analysis & Macro Overlay Engine

This repository is the upstream public-data and overlay engine for the commercial credit-risk portfolio stack.

## What This Repo Does (Plain English)

This repo turns **public Australian economic and property data** (ABS/RBA/PTRS and optional staged extracts) into:

- consistent **panels** (cleaned tables that summarise the state of the business cycle and property cycle)
- **overlay tables** (industry/property risk signals and downturn scenario assumptions)
- stable **contract exports** (`data/exports/*.parquet`) that downstream modelling repos can consume

## Role in Portfolio Stack

- Owns public-data ingestion, cleaning, standardisation, panel construction, and overlay exports.
- Publishes canonical contract outputs under `data/exports/` for downstream repos.
- Does **not** own loan-level model fitting, borrower scorecard engines, pricing engines, or portfolio stress engines.

## Canonical Structure

- `data/raw/public/`
- `data/raw/manual/`
- `data/processed/public/`
- `data/exports/`
- `src/public_data/`
- `src/panels/`
- `src/overlays/`
- `outputs/tables/`
- `outputs/charts/`
- `docs/`

## Canonical Exports

- `data/exports/business_cycle_panel.parquet`
- `data/exports/property_cycle_panel.parquet`
- `data/exports/macro_regime_flags.parquet`
- `data/exports/industry_risk_scores.parquet`
- `data/exports/property_market_overlays.parquet`
- `data/exports/downturn_overlay_table.parquet`

CSV inspection outputs:

- `outputs/tables/industry_risk_scores.csv`
- `outputs/tables/property_market_overlays.csv`
- `outputs/tables/downturn_overlay_table.csv`

## Canonical Workflow

```powershell
python -m pip install -r requirements.txt
python scripts/download_public_data.py
python scripts/build_public_panels.py
python scripts/build_overlays.py
python scripts/export_contracts.py
python scripts/validate_upstream.py
```

## What Each Script Does

- `scripts/download_public_data.py`: Downloads **network-dependent** PTRS public PDFs and rebuilds the PTRS workbook used as a public payment-times reference (`data/raw/public/ptrs/`).
- `scripts/build_public_panels.py`: Builds the core upstream panels (business-cycle panel, property-cycle panel, macro regime flags) and writes CSV inspection outputs under `data/processed/public/`.
- `scripts/build_overlays.py`: Builds the overlay tables (industry risk scores, property market overlays, downturn overlay table) and writes human-readable CSVs to `outputs/tables/`.
- `scripts/export_contracts.py`: Writes the **canonical downstream contract exports** to `data/exports/` as parquet files.
- `scripts/validate_upstream.py`: Runs simple “must-exist and non-empty” checks over both the in-memory outputs and the exported contract files.

## Troubleshooting

- Missing parquet engine (`pyarrow`/`fastparquet`): run `python -m pip install -r requirements.txt` and rerun `python scripts/export_contracts.py`.
- Network-restricted environment: `scripts/download_public_data.py` downloads PTRS public files and requires outbound HTTPS; if blocked, stage files under `data/raw/public/ptrs/` manually.
- Manual context datasets: optional staged inputs belong in `data/raw/manual/`; they are not downloaded by `scripts/download_public_data.py`.

## Notebooks

- `notebooks/00_repo_overview.ipynb`: Quick orientation (repo role, where outputs land).
- `notebooks/01_public_data_ingestion.ipynb`: Public-data ingestion walkthrough (PTRS download + how to stage optional manual extracts).
- `notebooks/02_business_cycle_and_macro_panels.ipynb`: Business-cycle panel walkthrough (industry structural + macro signals).
- `notebooks/03_property_cycle_panels.ipynb`: Property-cycle panel walkthrough (approvals/activity signals and segment-level cycle stage).
- `notebooks/04_overlay_build_and_exports.ipynb`: Overlay build + contract export walkthrough (what downstream repos consume).
- `notebooks/05_validation_and_contract_outputs.ipynb`: Validation walkthrough (what “done” looks like before handoff).

## Methodology Manuals

- `docs/methodology_cash_flow_lending.md`: How the repo supports cash-flow lending overlays (industry + macro).
- `docs/methodology_property_backed_lending.md`: How the repo supports property-backed lending overlays (property cycle + downturn overlays).

## Notes

- PTRS reconstruction remains in-repo for public-data support workflows.
- This repo exposes a single canonical upstream workflow via the five scripts above.
