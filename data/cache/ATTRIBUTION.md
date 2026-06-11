# Committed real-data cache — sources & attribution

This folder holds a committed snapshot of the **real public data** the pipeline
needs, so the reports are reproducible even if a live download fails. It is the
guaranteed fallback: `run_pipeline.py` tries the live download first and only
copies from here when a source is unreachable.

**Data vintage (`DATA_AS_OF`): 2026-02-28.** No synthetic or proprietary data is
included — every file below is an unmodified public release.

## Australian Bureau of Statistics (ABS) — `abs/`

© Commonwealth of Australia, Australian Bureau of Statistics. Licensed under
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

| File | ABS catalogue | Release |
| --- | --- | --- |
| `81550DO001_202324.xlsx` | 8155.0 Australian Industry | 2023–24 |
| `56760022_dec2025_profit_ratio.xlsx` | 5676.0 Business Indicators (profit) | Dec 2025 |
| `56760023_dec2025_inventory_ratio.xlsx` | 5676.0 Business Indicators (inventories) | Dec 2025 |
| `6291004_feb2026_labour_force_industry.xlsx` | 6291.0 Labour Force, Detailed | Feb 2026 |
| `87310051_feb2026_building_approvals_nonres.xlsx` | 8731.0 Building Approvals (non-residential) | Feb 2026 |

Source: <https://www.abs.gov.au/>

## Reserve Bank of Australia (RBA) — `rba/`

© Reserve Bank of Australia. RBA statistical tables are published for free public
use with attribution.

| File | RBA table |
| --- | --- |
| `rba_f1_data.csv` | F1 — Interest Rates and Yields: Money Market (cash rate) |

Source: <https://www.rba.gov.au/statistics/tables/>

---

*PTRS (Payment Times Reporting Scheme) PDFs are fetched best-effort at run time
and are not cached here — they are large and are not required to build the
reports.*
