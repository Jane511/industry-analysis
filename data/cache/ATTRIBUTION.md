# Committed real-data cache — sources & attribution

This folder holds a committed snapshot of the **real public data** the pipeline
needs, so the reports are reproducible even if a live download fails. It is the
guaranteed fallback: `run_pipeline.py` tries the live download first and only
copies from here when a source is unreachable.

**Data vintage (`DATA_AS_OF`): 2026-06-16.** Every quarterly / monthly ABS series
reports through the **March 2026 quarter** (the end of Q1 2026). No synthetic or
proprietary data is included — every file below is an unmodified public release.

## Australian Bureau of Statistics (ABS) — `abs/`

© Commonwealth of Australia, Australian Bureau of Statistics. Licensed under
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

| File | ABS catalogue | Release |
| --- | --- | --- |
| `81550DO001_202324.xlsx` | 8155.0 Australian Industry | 2023–24 |
| `56760022_mar2026_profit_ratio.xlsx` | 5676.0 Business Indicators (profit) | Mar 2026 |
| `56760023_mar2026_inventory_ratio.xlsx` | 5676.0 Business Indicators (inventories) | Mar 2026 |
| `6291004_mar2026_labour_force_industry.xlsx` | 6291.0 Labour Force, Detailed | Mar 2026 |
| `87310051_mar2026_building_approvals_nonres.xlsx` | 8731.0 Building Approvals (non-residential) | Mar 2026 |
| `5206001_mar2026_national_accounts.xlsx` | 5206.0 National Accounts (real GDP) | Mar 2026 quarter |
| `6202001_mar2026_labour_force.xlsx` | 6202.0 Labour Force (unemployment rate) | Mar 2026 |
| `64010001_mar2026_cpi_all_groups.xlsx` | 6401.0 Consumer Price Index | Mar 2026 quarter |
| `63450001_mar2026_wpi.xlsx` | 6345.0 Wage Price Index | Mar 2026 quarter |

The last four supply the live economy-wide headline levels (GDP, unemployment,
CPI, WPI) parsed by `src/public_data/download_macro_indicators.py`; the pipeline
fetches them live each run and falls back to these committed copies offline.

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
