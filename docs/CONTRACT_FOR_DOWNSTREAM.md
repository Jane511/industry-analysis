# Downstream CSV Contract

Canonical published exports live in `outputs/contracts/`. These CSVs replace
parquet as the downstream contract format. The legacy `data/exports/*.parquet`
files may remain during migration, but consumers should read the CSVs listed
here.

CSV does not preserve dtypes. Python consumers should read through
`src.csv_io` helpers; non-Python consumers must apply the dtypes documented by
the header and data dictionary in their own ingestion layer.

| CSV file | Grain | Contract role | Primary downstream consumers |
|---|---|---|---|
| `industry_risk_scores.csv` | One row per ANZSIC division | Core downstream contract | PD scorecard build, pricing, stress testing |
| `industry_failure_rates.csv` | One row per ANZSIC division | Core downstream contract | PD validation, portfolio monitoring |
| `industry_financial_benchmarks.csv` | One row per ANZSIC division | Core downstream contract | PD scorecard input, ECL forward-looking adjustment |
| `property_market_overlays.csv` | One row per property segment | Core downstream contract | PD property-backed multiplier, LGD overlay, stress testing |
| `property_market_detail.csv` | One row per region x property type x quarter | Core downstream contract | PD deal context, LGD collateral-region sensitivity, scenario builder |
| `downturn_overlay_table.csv` | One row per scenario | Core downstream contract | PD/LGD/EAD stress, ICAAP |
| `macro_context.csv` | One row per quarter | Core downstream contract | PD macro features, ECL FLI, stress testing, Board cycle commentary |
| `macro_regime_flags.csv` | One row per quarter | Core downstream contract | ECL staging trigger, PIT PD overlay, scenario weighting |
| `business_cycle_panel.csv` | Wide industry diagnostics | Optional explainability panel | PD explainability, validation diagnostics, challenger model analysis |
| `property_cycle_panel.csv` | Property segment-by-region diagnostics | Optional explainability panel | LGD explainability, property stress interpretation |
| `property_market_overlays_by_building_type.csv` | Per-building-type non-residential detail | Optional explainability panel | Construction-loan diagnostics, property stress refinement |

## Consumer Mapping

| Product | CSV files consumed |
|---|---|
| `term_loan` | `industry_risk_scores.csv`, `industry_failure_rates.csv`, `industry_financial_benchmarks.csv`, `macro_context.csv`, `macro_regime_flags.csv` |
| `line_of_credit` | `industry_risk_scores.csv`, `industry_failure_rates.csv`, `industry_financial_benchmarks.csv`, `macro_context.csv`, `macro_regime_flags.csv` |
| `invoice_finance` | `industry_risk_scores.csv`, `industry_failure_rates.csv`, `industry_financial_benchmarks.csv`, `macro_context.csv`, `macro_regime_flags.csv` |
| `trade_finance` | `industry_risk_scores.csv`, `industry_failure_rates.csv`, `industry_financial_benchmarks.csv`, `macro_context.csv`, `macro_regime_flags.csv` |
| `asset_finance` | `industry_risk_scores.csv`, `industry_failure_rates.csv`, `industry_financial_benchmarks.csv`, `macro_context.csv`, `macro_regime_flags.csv` |
| `bridging` | `property_market_overlays.csv`, `property_market_detail.csv`, `downturn_overlay_table.csv`, `macro_context.csv`, `macro_regime_flags.csv` |
| `development` | `property_market_overlays.csv`, `property_market_detail.csv`, `downturn_overlay_table.csv`, `macro_context.csv`, `macro_regime_flags.csv`, `property_market_overlays_by_building_type.csv` |
| `commercial_property` | `property_market_overlays.csv`, `property_market_detail.csv`, `downturn_overlay_table.csv`, `macro_context.csv`, `macro_regime_flags.csv`, `property_market_overlays_by_building_type.csv` |

## Engineering Mapping

| Engineering project | CSVs consumed | Purpose |
|---|---|---|
| PD scorecard build / Thin Data Workbook | `industry_risk_scores.csv`, `industry_financial_benchmarks.csv`, `macro_context.csv` | Industry multiplier table, financial benchmarks, macro context |
| PD validation | `industry_failure_rates.csv`, `business_cycle_panel.csv` | Realised failure rates and explainability panels |
| LGD overlay | `property_market_overlays.csv`, `property_market_detail.csv`, `property_market_overlays_by_building_type.csv` | Segment multipliers, collateral-region sensitivity, building-type detail |
| ECL / IFRS 9 staging | `macro_context.csv`, `macro_regime_flags.csv` | FLI and regime flags |
| EAD stress | `downturn_overlay_table.csv` | CCF multipliers per scenario |
| Stress testing engine | `industry_risk_scores.csv`, `property_market_overlays.csv`, `downturn_overlay_table.csv`, `macro_context.csv`, `macro_regime_flags.csv` | Industry shocks, property shocks, downturn scenarios |
| Pricing | `industry_risk_scores.csv` | Deal-level industry multiplier |
| Portfolio monitoring | `industry_failure_rates.csv`, `property_market_overlays.csv` | Sector watchlist and property concentration |
| Board / governance reporting | all 11 CSVs | Embedded report tables and traceability |

## Downturn overlays: stress framework notes

`downturn_overlay_table.csv` is the macro-credit linkage step of a stress
test: it translates a named macroeconomic path into PD / LGD / CCF (EAD)
multipliers and a property-value haircut that a consuming portfolio applies
to its own exposures. The following framework points govern its use.

**Scenario set and macro path (ST-IA-1).** Scenarios are `base / mild /
moderate / severe`. Each row carries a `macro_path` note so the multipliers
read as *derived from* a scenario, not standalone dials. The **mild**
scenario is the **Basel CRE36.51 mandatory minimum — two consecutive
quarters of zero GDP growth**; severe is a GFC-like path. Multipliers remain
illustrative assumptions (not calibrated regulatory parameters), nudged by
the real ABS property-softness backdrop and the RBA-FSR arrears baseline.

**No diversification (APG 113 para 92).** The overlays are applied per
sector/segment with **no diversification benefit assumed** — a consuming
book must not net these shocks down for portfolio correlation. This is also
stated in each published overlay row's `notes`.

**Reverse-stress view (APS 220).** Because the overlays are *relative*
multipliers, reverse stress is read off the combined `pd_multiplier ×
lgd_multiplier` uplift: that combined factor is ≈1.0× (base), ≈1.3× (mild),
≈1.8× (moderate) and ≈2.6× (severe). A consuming portfolio sets the loss /
appetite threshold it cannot exceed and reads back the **scenario (and
sector) at which its overlaid PD × LGD breaches that threshold** — i.e.
"which downturn breaks the limit?". For a book whose appetite ceiling is a
2.0× EL uplift, that breach point sits between the moderate and severe
scenarios.

**Feeds stress → limits / appetite (ST-IA-2).** The downstream loop is:
overlay multipliers → stressed portfolio PD × LGD (× CCF for EAD) → compare
to risk-appetite limits → if breached, management action (tighten
origination, reprice, reduce sector limits). The overlays are the
macro-credit input to that loop, not the limit framework itself (which lives
in the consuming monitoring/ICAAP project).

**Independent validation (ST-IA-3, APS 220 para 76).** The overlay
assumptions and macro paths are documented here and in
`src/overlays/downturn_overlay_core.py`, and would be **independently
reviewed/validated and refreshed on the documented schedule** (see the
assumptions register / `docs/anchor_sources.md`). They are honestly labelled
as illustrative, not calibrated regulatory stress parameters.
