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
| `macro_scenario_paths.csv` | One row per scenario x macro variable | Core downstream contract | Macro stress paths for PD/LGD/EAD, ICAAP, scenario design |
| `portfolio_macro_sensitivity.csv` | One row per segment x parameter x driver | Core downstream contract | Portfolio/facility macro-to-PD/LGD/EAD multiplier mapping |
| `macro_context.csv` | One row per macro variable (current state) | Core downstream contract | PD macro features, ECL FLI, stress testing, Board cycle commentary |
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

## Macro stress contracts (facility + portfolio level)

Two contracts translate macroeconomic scenarios into portfolio/facility stress
(codename MACRO-STRESS; engine `src/overlays/macro_stress_core.py`, config
`config/macro_scenarios.yaml`).

**`macro_scenario_paths.csv`** — one row per `scenario x variable` for the 12
macro variables (GDP growth, unemployment, cash rate, inflation, wage growth,
house-price growth, exchange-rate TWI, industry output — ABS/RBA-anchored; plus
commercial-property prices, vacancy, CRE rents, CRE cap rates — labelled
assumptions). Columns: `scenario, variable, label, unit, stress_direction,
base_level, shock, stressed_level, shock_norm, source_or_assumption,
macro_note`. `shock_norm` is the sign-oriented shock normalised onto a common
0..1 stress scale (severe = 1.0).

**`portfolio_macro_sensitivity.csv`** — one row per `segment x parameter x
driver` mapping each portfolio segment (residential mortgages, credit cards,
SME, corporate, commercial property, development finance) to its material macro
drivers per PD / LGD / EAD. Columns: `segment, parameter, driver,
sensitivity_weight, driver_stress_direction, source_or_assumption`. Weights are
the driver **mix** (sum to 1.0 per segment x parameter); a per-segment beta in
the config scales overall magnitude. Illustrative elasticities, not estimated
betas.

**Consumption (facility -> portfolio).** A consuming PD/LGD model computes, per
segment and scenario, `multiplier[s,p,k] = clamp(1 + intensity[p] * beta[s,p] *
Σ_d weight[s,p,d] * shock_norm[d,k])`, then applies it to each facility:
`stressed_PD_i = base_PD_i × multiplier(segment_i, PD, k)` (same for LGD/EAD) and
sums `stressed_EL_i` with **no diversification benefit** for the portfolio total.
The repo demonstrates this on `data/raw/demo_portfolio.csv`; the worked tables
and a reverse-stress line are **Section 9 of the Board / Technical report**
(`outputs/reports/Industry_Analysis_Q1_2026_*.md`), backed by supporting CSVs
(`macro_stress_segment_multipliers.csv`, `macro_stress_demo_portfolio.csv`,
`macro_stress_demo_summary.csv`).

**Separate vs pooled models.** A bank normally develops separate models per
material portfolio, or a pooled model with portfolio/sector effects; this layer
supplies the macro-credit linkage either approach consumes. Independently
validated annually; illustrative, not calibrated regulatory stress.
