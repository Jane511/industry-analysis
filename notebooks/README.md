# Notebooks

This folder now contains both:

- new reference-layer notebook scaffolding
- the original legacy industry-analysis walkthrough notebooks

## Reference-Layer Notebook Set

- `01_project_overview.ipynb`
- `02_abs_property_data_processing.ipynb`
- `03_arrears_environment_analysis.ipynb`
- `04_region_risk_banding.ipynb`
- `05_property_cycle_banding.ipynb`
- `06_downturn_overlay_design.ipynb`
- `07_final_outputs.ipynb`

These notebooks are lightweight scaffolds that map to the new reference-layer architecture and point back to the source-of-truth logic in `src/`.

## Legacy Notebook Set

- `01_results_and_report_walkthrough.ipynb`
- `02_methodology_and_output_map.ipynb`

## Current Local Source Coverage

The current reference-layer notebooks assume staged:

- `ABS Building Approvals (Non-residential)` through `February 2026`
- `RBA F1` with the latest staged observation dated `16 March 2026`

If new local property files are staged, rerun `python scripts/run_reference_layer.py` or `python scripts/run_pipeline.py` before reopening the notebooks.
