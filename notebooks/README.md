# Notebooks

This folder contains guided notebook walkthroughs for the project.

The notebooks currently reflect these staged source vintages: annual ABS data through FY `2023-24`, quarterly ABS Business Indicators through `December 2025`, monthly ABS labour and approvals through `February 2026`, the local `RBA F1` snapshot published `2 April 2026` with the latest staged observation dated `16 March 2026`, and `PTRS` Cycle `8` (`July 2025`) plus Cycle `9` (`January 2026`). If those source files are refreshed, rerun `python scripts/run_pipeline.py` before reopening the notebooks.

- `01_results_and_report_walkthrough.ipynb`
  Portfolio-facing walkthrough of the current sector, borrower, portfolio, working-capital, and monitoring results.
- `02_methodology_and_output_map.ipynb`
  Guided explanation of the public datasets, derivation logic, output tables, and how the final industry analysis is assembled.

The notebooks are designed to complement, not replace, the source-of-truth pipeline code in `src/`.
