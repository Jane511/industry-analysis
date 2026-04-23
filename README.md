# Commercial Industry Analysis & Macro Overlay Engine

This repository is the upstream public-data and overlay engine for the commercial credit-risk portfolio stack. It turns public Australian economic and property data into canonical parquet contracts, and ships a board-ready industry-analysis report built from those contracts.

## What This Repo Does

This repo turns **public Australian economic and property data** (ABS/RBA/PTRS and optional staged extracts) into:

- consistent **panels** (cleaned tables that summarise the state of the business cycle and property cycle)
- **overlay tables** (industry/property risk signals and downturn scenario assumptions)
- stable **contract exports** (`data/exports/*.parquet`) that downstream modelling repos can consume
- a **board-ready industry-analysis report** in markdown, DOCX, and HTML, rendered from those same contracts

## Role in Portfolio Stack

- Owns public-data ingestion, cleaning, standardisation, panel construction, overlay exports, and the board-report renderer.
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
- `src/reporting/` — board-report content builder + markdown/DOCX/HTML renderers
- `outputs/tables/` — secondary CSV inspection outputs
- `outputs/reports/` — rendered board reports
- `tests/` — contract tests + renderer tests (77 cases)
- `docs/`

## Canonical Exports

Core downstream contract (required):

- `data/exports/industry_risk_scores.parquet`
- `data/exports/property_market_overlays.parquet`
- `data/exports/downturn_overlay_table.parquet`
- `data/exports/macro_regime_flags.parquet`

Optional explainability panels (published but not required for core joins):

- `data/exports/business_cycle_panel.parquet`
- `data/exports/property_cycle_panel.parquet`

Secondary CSV inspection outputs (derived from the canonical parquet exports):

- `outputs/tables/industry_risk_scores.csv`
- `outputs/tables/property_market_overlays.csv`
- `outputs/tables/downturn_overlay_table.csv`

## Canonical Workflow

```powershell
python -m pip install -r requirements.txt
python scripts/download_public_data.py
python scripts/export_contracts.py
python scripts/validate_upstream.py
python scripts/build_board_report.py --format all --output outputs/reports/Industry_Analysis_Q1_2026
```

Optional preflight scripts:

```powershell
python scripts/build_public_panels.py
python scripts/build_overlays.py
```

## What Each Script Does

- `scripts/download_public_data.py`: Downloads **network-dependent** PTRS public PDFs and rebuilds the PTRS workbook used as a public payment-times reference (`data/raw/public/ptrs/`).
- `scripts/build_public_panels.py`: Builds the explainability panels and reference CSVs under `data/processed/public/`.
- `scripts/build_overlays.py`: Builds overlay tables in-memory for quick row-count sanity checks.
- `scripts/export_contracts.py`: Writes canonical parquet contracts to `data/exports/` and derives secondary CSV inspection tables in `outputs/tables/`.
- `scripts/validate_upstream.py`: Validates core contract outputs as required checks and explainability panels as optional checks.
- `scripts/build_board_report.py`: Renders the industry-analysis board report from the canonical parquet contracts. Supports `--format markdown|docx|html|all`; `all` emits six files (Board + Technical × three formats).

## Board Report

The `src/reporting/` package produces a variant-aware industry-analysis report from the canonical parquet exports. The content tree is built once; three renderers consume it without re-reading parquet files.

- **Board** variant — summary view for non-technical reviewers.
- **Technical** variant — full-detail view for MRC, audit, and model-risk review. Includes per-row commentary, source URLs, and an audit-log appendix.

Generated files land in `outputs/reports/`:

- `Industry_Analysis_<period>_Board.md` / `_Technical.md`
- `Industry_Analysis_<period>_Board.docx` / `_Technical.docx`
- `Industry_Analysis_<period>_Board.html` / `_Technical.html`

## Tests

```powershell
python -m pytest -v
```

77 tests across:

- `tests/test_export_contracts.py` — parametrized contract tests over all four core exports (file exists on disk, minimum row count, required columns, no all-null columns) plus downturn-multiplier invariants (monotonic base → severe, base scenario = 1.0).
- `tests/test_report_renderers.py` — cross-renderer tests (deterministic markdown, six-file CLI output, Construction callout placement in the DOCX Board variant, Appendix A only in Technical, no unresolved `{placeholder}` strings in HTML).
- Foundation, macro, reference-layer, PTRS-reconstruction, and utility test suites covering the overlay build path.

## Troubleshooting

- Missing parquet engine (`pyarrow`/`fastparquet`): run `python -m pip install -r requirements.txt` and rerun `python scripts/export_contracts.py`.
- Missing `python-docx`: install via `python -m pip install -r requirements.txt`; required only for `--format docx` and `--format all` report builds.
- Network-restricted environment: `scripts/download_public_data.py` downloads PTRS public files and requires outbound HTTPS; if blocked, stage files under `data/raw/public/ptrs/` manually.
- Manual context datasets: optional staged inputs belong in `data/raw/manual/`; they are not downloaded by `scripts/download_public_data.py`.

## Notebooks

- `notebooks/00_repo_overview.ipynb`: Quick orientation (repo role, where outputs land).
- `notebooks/01_public_data_ingestion.ipynb`: Public-data ingestion walkthrough (PTRS download + how to stage optional manual extracts).
- `notebooks/02_business_cycle_and_macro_panels.ipynb`: Business-cycle panel walkthrough (industry structural + macro signals).
- `notebooks/03_property_cycle_panels.ipynb`: Property-cycle panel walkthrough (approvals/activity signals and segment-level cycle stage).
- `notebooks/04_overlay_build_and_exports.ipynb`: Overlay build + contract export walkthrough (what downstream repos consume).
- `notebooks/05_validation_and_contract_outputs.ipynb`: Validation walkthrough (what "done" looks like before handoff).

## Methodology Manuals

- `docs/methodology_cash_flow_lending.md`: How the repo supports cash-flow lending overlays (industry + macro).
- `docs/methodology_property_backed_lending.md`: How the repo supports property-backed lending overlays (property cycle + downturn overlays).

## Notes

- PTRS reconstruction remains in-repo for public-data support workflows.
- Upstream handoff contract is the canonical parquet export set under `data/exports/`.
- The board report is a downstream consumer of that contract set, not part of it — regenerating reports does not mutate any parquet file.
