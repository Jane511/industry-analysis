# Industry Analysis Report — Q1 2026

*Technical Detail variant. Generated 2026-04-23.*



Macro and downturn overlays as of 2026-03-16. Property cycle data as of 2026-02-01.

This is the full-detail variant for MRC, audit, and model-risk review. It includes per-row technical commentary, source URLs, the full Construction methodology review item, and the audit log as an appendix.



## 1. Executive Summary

This report summarises the current state of Australian industry and property market risk using public macro, industry, and property data. Overlays cover 9 industries and 11 property segments. Cash rate sits at 3.85%, 0.25pp lower than a year ago; arrears environment is Low and improving. 4 of 9 industries currently score Elevated on the base risk scale. 1 property segment is in downturn, 1 is slowing, and 3 are in growth. Headline finding: 4 of 9 industries score Elevated (Agriculture, Forestry And Fishing, Manufacturing, Wholesale Trade, Retail Trade). Macro regime flag: 'base' (cash_rate_regime='neutral_easing'). Data freshness: macro and downturn overlays as of 2026-03-16; property cycle data as of 2026-02-01. Report generated 2026-04-23.

> **How to read this report**
>
> This report uses a 1–5 risk-score scale with four bands:
> - Low (< 2.0) — defensive, structurally resilient
> - Medium (2.0 – 2.75) — neutral, typical business-cycle exposure
> - Elevated (2.75 – 3.5) — cyclical or rate-sensitive; monitor closely
> - High (> 3.5) — stressed or structurally vulnerable
>
> These bands are defined in `src.utils.risk_band` and tested in `tests.test_utils`.

## 2. Macro Regime

Macro conditions shape how every industry and property segment is stressed. The cash rate is the dominant conditioning variable; the arrears backdrop confirms whether rate moves are already showing in borrower behaviour. The regime flag combines cash rate, arrears level, and arrears trend into a single compact label that downstream credit models consume without having to re-read the underlying series.

*Macro regime snapshot as of 2026-03-16*

| Metric | Value | Source |
| --- | --- | --- |
| Cash rate (latest) | 3.85% | RBA F1 |
| Cash rate 1y change | -0.25pp | RBA F1 |
| Cash rate regime | neutral_easing | Derived from RBA F1 |
| Arrears environment | Low | Staged arrears context |
| Arrears trend | Improving | Staged arrears context |
| Macro regime flag | base | RBA F1 cash-rate table + staged arrears context |

Combined with a low arrears backdrop, this suggests borrowers are absorbing rate pressure; credit models should weight structural over cyclical factors in current calibration. The downturn overlays currently apply the 'base' scenario (no uplift to PD/LGD/CCF). The `macro_regime_flag` value of 'base' is the hook downstream repos use to select the corresponding row of `downturn_overlay_table.parquet`. Any change to this flag propagates automatically; recalibration of the underlying overlay is out of scope here.

## 3. Industry Risk Rankings

Industries are ranked by a combined base risk score that blends structural classification risk (cyclicality, concentration, capital intensity) with current macro sensitivity. The table below is ordered highest-risk first. Scores range 1 (low) to 5 (high). Level bands: Low (<2), Medium (2.00–2.75), Elevated (2.75–3.50), High (>3.50). Both component scores and the blended `industry_base_risk_score` are shown. Source: `data/exports/industry_risk_scores.parquet` (refreshed from `build_business_cycle_panel` at pipeline build time).

*All 9 industries ranked by base risk score*

| Rank | Industry | Classification | Macro | Base score | Level |
| --- | --- | --- | --- | --- | --- |
| 1 | Agriculture, Forestry And Fishing | 3.75 | 3.20 | 3.50 | Elevated |
| 2 | Manufacturing | 3.75 | 3.20 | 3.50 | Elevated |
| 3 | Wholesale Trade | 3.25 | 3.20 | 3.23 | Elevated |
| 4 | Retail Trade | 3.25 | 3.20 | 3.23 | Elevated |
| 5 | Accommodation And Food Services | 2.75 | 2.60 | 2.68 | Medium |
| 6 | Construction | 2.75 | 2.60 | 2.68 | Medium |
| 7 | Health Care and Social Assistance | 1.75 | 2.80 | 2.22 | Medium |
| 8 | Professional, Scientific And Technical Services | 2.00 | 2.40 | 2.18 | Medium |
| 9 | Transport, Postal And Warehousing | 2.25 | 2.00 | 2.14 | Medium |

> **Construction ranking**
>
> **Methodology note.** Construction base risk score (2.68, 'Medium') reflects structural classification risk only, not current insolvency pressure. See Section 9 for methodology context and the active review item.

The top 4 industries all sit in the 'Elevated' band, driven by structural cyclicality and current rate sensitivity. Defensive sectors (Health Care; Professional, Scientific and Technical) sit at the lower end, as expected. The Base score is a weighted blend; see `src/overlays/build_industry_risk_scores.py` for the formula. All rows share the same `cash_rate_latest_pct` (3.85%) because the macro component is a single environment-wide conditioner, not an industry-specific signal.

## 4. Top Risk Industries

These are the five industries with the highest combined base risk score in the current environment. Review these first when calibrating portfolio concentration limits or sector caps. Industries are sorted descending on `industry_base_risk_score`. Ties are broken by DataFrame order; this should not be relied on for downstream sorting.

*Top 5 industries by base risk score*

| Industry | Classification | Macro | Base score | Level |
| --- | --- | --- | --- | --- |
| Agriculture, Forestry And Fishing | 3.75 | 3.20 | 3.50 | Elevated |
| Manufacturing | 3.75 | 3.20 | 3.50 | Elevated |
| Wholesale Trade | 3.25 | 3.20 | 3.23 | Elevated |
| Retail Trade | 3.25 | 3.20 | 3.23 | Elevated |
| Accommodation And Food Services | 2.75 | 2.60 | 2.68 | Medium |

The table below adds operational context from `business_cycle_panel.parquet` for the same five industries. Nulls in 'Demand growth YoY %' reflect sectors where ABS does not publish the relevant series; the underlying scoring logic maps nulls to a neutral factor score (3). See Section 9.

*Operational detail for top 5 industries (Technical only)*

| Industry | Employment (000s) | Sales ($m) | EBITDA margin % | Demand growth YoY % | Inventory build risk |
| --- | --- | --- | --- | --- | --- |
| Agriculture, Forestry And Fishing | 411.0 | 119,772 | 14.58 | +58.37 | Low |
| Manufacturing | 901.7 | 514,199 | 9.15 | +55.53 | Moderate |
| Wholesale Trade | 604.2 | 772,255 | 6.12 | +69.32 | Moderate |
| Retail Trade | 1,509.6 | 643,421 | 7.80 | +68.47 | Low |
| Accommodation And Food Services | 1,217.9 | 152,965 | 11.38 | +113.70 | Low |

## 5. Property Market Overlays

Property overlays track 11 commercial and non-residential segments through the cycle. Each segment is classified into one of four cycle stages (downturn, slowing, neutral, growth) using approvals momentum as the primary signal. Commencements and completions are proxied from the approvals trend in this cycle because ABS building activity has not been staged; see `source_note` in `property_cycle_panel.parquet` for per-row provenance.

*All 11 segments grouped by cycle stage (as of 2026-02-01)*

| Segment | Cycle | Softness score | Softness band | Region risk | Region band | Approvals Δ % |
| --- | --- | --- | --- | --- | --- | --- |
| Offices | downturn | 4.30 | soft | 4.03 | High | -35.72 |
| Education buildings | slowing | 3.25 | softening | 3.38 | Elevated | -21.37 |
| Retail and wholesale trade buildings | neutral | 3.15 | normal | 2.95 | Medium | +68.47 |
| Aged care facilities | neutral | 2.70 | normal | 2.73 | Medium | +219.88 |
| Agricultural and aquacultural buildings | neutral | 2.65 | normal | 2.58 | Medium | +58.37 |
| Total Non-residential | neutral | 2.60 | normal | 2.55 | Medium | +71.46 |
| Industrial Buildings - Total | neutral | 2.40 | normal | 2.45 | Medium | +55.53 |
| Warehouses | neutral | 2.20 | normal | 2.35 | Medium | +69.32 |
| Short term accommodation buildings | growth | 2.85 | supportive | 2.55 | Medium | +113.70 |
| Commercial Buildings - Total | growth | 2.30 | supportive | 2.15 | Medium | +165.42 |
| Health buildings | growth | 1.65 | supportive | 1.82 | Low | +355.03 |

Segments are grouped with downturn first, then slowing, neutral, and growth. Offices is the only segment flagged in downturn; Health buildings, Commercial Buildings Total, and Short-term accommodation are the three segments in growth. Within each cycle stage, segments are sorted on softness score descending so the softer segments within each bucket appear first. Approvals Δ % is the year-on-year change in ABS building approvals for the segment; extreme values (e.g. +355% for Health buildings) reflect low prior-period base effects rather than a calibrated trend signal.

## 6. Property Cycle Interpretation

1 segment is currently in downturn (Offices). 1 is slowing (Education buildings). 6 segments sit in neutral, and 3 are in growth (Short term accommodation buildings, Commercial Buildings - Total, Health buildings). For property-backed lending, Offices warrants elevated caution; the growth-stage segments look supportive but should be read alongside the approvals-base-effect caveat below. Cycle-stage assignment is rule-based on approvals momentum and softness score; it is not a forecast. A segment in 'growth' today can pivot to 'slowing' in the next refresh if approvals pull back. The overlay is a conditioning signal, not a predictive one.

## 7. Downturn Scenarios

Downturn overlays provide illustrative multipliers for PD, LGD, and CCF, plus property value haircuts, under four scenarios. These support scenario analysis and conservative pricing; they are not calibrated regulatory stress parameters. Multipliers are monotonic base → severe by construction; the base scenario is always 1.0 (no adjustment), and the contract-test suite (`tests/test_export_contracts.py`) locks this invariant.

*Illustrative downturn multipliers (as of 2026-03-16)*

| Scenario | PD × | LGD × | CCF × | Property haircut | Notes |
| --- | --- | --- | --- | --- | --- |
| base | 1.00 | 1.00 | 1.00 | 0.00 | Current staged environment. Anchored to a low / improving arrears backdrop and an average property-cycle softness score of 2.73. |
| mild | 1.20 | 1.10 | 1.05 | 0.05 | Illustrative mild downturn overlay for conservative portfolio calibration. |
| moderate | 1.50 | 1.20 | 1.10 | 0.10 | Illustrative moderate downturn overlay for stressed pricing and EL scenario analysis. |
| severe | 2.00 | 1.30 | 1.20 | 0.20 | Illustrative severe downturn overlay. Not a calibrated regulatory stress parameter. |

Apply multiplicatively to modelled PD/LGD/CCF; haircut applies to property valuations in collateral-backed lines. The severe scenario doubles PD; mild and moderate are graduated. Current environment selects the 'base' row (see Section 2).

## 8. Data Sources and Freshness

Each overlay is built from public data refreshed on a published cadence. The table below lists the primary source and last-refresh date for each contract. A full chain-of-custody exists in `scripts/download_public_data.py` and `scripts/build_public_panels.py`; the most recent baseline run completed cleanly with no warnings (see `outputs/baseline_state.md`).

*Primary sources and refresh dates*

| Overlay | Primary source | URL | Refreshed |
| --- | --- | --- | --- |
| industry_risk_scores | ABS Economic Activity Survey + RBA F1 | https://www.abs.gov.au/statistics/industry | 2026-03-16 |
| property_market_overlays | ABS Building Approvals (non-residential) | https://www.abs.gov.au/statistics/industry/building-and-construction/building-approvals-australia | 2026-02-01 |
| downturn_overlay_table | Staged arrears context + property softness | (internal staging) | 2026-03-16 |
| macro_regime_flags | RBA F1 cash-rate table + arrears staging | https://www.rba.gov.au/statistics/tables/ | 2026-03-16 |
| business_cycle_panel | ABS EAS + RBA F1 (panel assembly) | (derived) | 2026-03-16 |
| property_cycle_panel | ABS Building Approvals | (derived) | 2026-02-01 |

## 9. Validation and Caveats

Contract validation runs automatically before every downstream handoff. All 12 current checks passed on the latest pipeline run. This section also documents active methodology review items and known gaps. The validator is `scripts/validate_upstream.py`, backed by `src/validation.py`. It verifies presence and non-emptiness of all 4 core contract exports plus 2 optional explainability panels. End-to-end test coverage is locked via `tests/test_export_contracts.py` (schema, row counts, no all-null columns, downturn monotonicity, and base-scenario unity multipliers).

*Contract validation summary*

| Check category | Items | Status |
| --- | --- | --- |
| Core contract presence | 4 | Pass |
| Core contract file on disk | 4 | Pass |
| Optional panel presence | 2 | Pass |
| Optional panel file on disk | 2 | Pass |

Two caveats to flag: (1) Construction's 'Medium' rating reflects structural factors only, not current insolvency pressure — see the callout below. (2) Property overlay commencements and completions are proxied from approvals in this cycle, not directly observed. (3) `business_cycle_panel` carries 21 nulls across 6 diagnostic columns, all concentrated in sectors where ABS does not publish inventory-to-sales ratios (Agriculture, Construction, Health, Professional, Transport). Core scoring columns are fully populated; scoring functions in `src/utils.py` map nulls to a neutral factor score (3). The null pattern is confirmed documented-by-design via the `inventory_days_est_source` flag column. (4) The `cash_rate_latest_pct` field is broadcast uniformly to every industry row; it is a conditioner, not a per-industry observation.

> **Methodology review item: Construction ranking**
>
> The current `industry_base_risk_score` for Construction is 2.68 ('Medium'), tied with Accommodation/Food Services and below Manufacturing/Agriculture (3.50 each).
>
> Market evidence suggests Construction warrants an 'Elevated' classification in the current cycle:
> - Australian builder insolvencies have been elevated through 2024–2026 (Porter Davis, Probuild, Clough collapses).
> - Subcontractor arrears remain at multi-year highs.
> - Fixed-price-contract plus materials-inflation squeeze is ongoing.
>
> Why the score does not reflect this: the methodology weights structural classification factors (cyclicality, market concentration) and macro sensitivity (rates, growth) but does not currently incorporate sector-specific insolvency or arrears flow data into the base risk score. The downturn overlay table provides scenario adjustments, but those apply uniformly across industries rather than tilted toward sectors under specific stress.
>
> This is a methodology design choice — defensible if you treat insolvency rates as a separate 'current state' overlay distinct from 'structural risk'. But it produces base scores that may understate near-term credit risk for sectors going through a sector-specific stress event.
>
> **Options for next methodology review:**
> 1. **Accept the design as-is** (structural vs current-state separation).
> 2. **Add an industry-stress overlay** that lifts the base score when ASIC insolvency rates exceed a threshold for a specific ANZSIC division.
> 3. **Document the limitation** in the methodology manual and downstream consumer documentation.
>
> **This session: noted, not fixed.** Methodology change is out of scope for an audit + polish pass.

## 10. Methodology References

Full methodology manuals are maintained in the repo `docs/` folder. These describe how each overlay is constructed from raw inputs.

*Methodology documents*

| Area | Document |
| --- | --- |
| Cash-flow lending | docs/methodology_cash_flow_lending.md |
| Property-backed lending | docs/methodology_property_backed_lending.md |
| Audit + polish log (this session) | outputs/industry_analysis_audit_log.md |
| Baseline state | outputs/baseline_state.md |

## Appendix A — Audit log (this session)

**Date:** 2026-04-23  
**Scope:** Phase 1 baseline audit, Phase 2 anomaly scan, Phase 3 test-coverage audit + contract tests, Phase 4a markdown report build.

### Phase 1 — Baseline
- Test suite: 54 passed, 0 failed, 0 skipped, 0 warnings (pre-Phase-3).
- Pipeline scripts: all five completed cleanly after raw ABS/RBA data was copied from the main checkout into the worktree (git-ignored by design).
- Validator: 12/12 checks green.
- Exports: 6/6 present and non-empty. Dated exports within ~2 months of today; not stale.

### Phase 2 — Anomaly scan
- HIGH findings: 0. MEDIUM findings: 0. LOW findings: 2 (both informational, from the null-pattern diagnostic block).
- 21 nulls in `business_cycle_panel` confirmed as documented-by-design. Every null-bearing row is labelled 'Fallback' in `inventory_days_est_source`; every non-null row labelled 'ABS quarterly'. Zero exceptions.
- Core scoring columns (`classification_risk_score`, `macro_risk_score`, `industry_base_risk_score`, `industry_base_risk_level`) have 0 nulls.
- Scoring functions in `src/utils.py` map null inputs to a neutral factor score (3) — null-tolerant by design.

### Phase 3 — Test coverage
- Baseline: 15 of 23 source modules had direct test imports; 8 untested.
- Added `tests/test_export_contracts.py` (6 test functions expanding to 18 parametrized cases) covering the canonical contract boundary (`src/overlays/export_contracts.py`).
- Final count: 72 tests passing.
- Deferred Tier-2 builder tests: the 6 top-level `build_*` functions are smoke-tested via `test_reference_layer.py::test_canonical_panel_overlay_builders_are_importable`. End-to-end coverage is provided by the new contract tests plus the Phase 1 parquet-inspection. Adding per-builder contract tests would be duplication.
- Defensible gaps remaining: `src/validation.py` (end-to-end only via script), `src/config.py` (constants), `src/output.py` (small helper surface), `src/public_data/download_*.py` (thin network wrappers), `src/public_data/load_abs_manual_exports_helpers.py` (helpers for a tested parent module).

### Phase 4a — Markdown board report
- Added `reports/` package (`__init__.py`, `industry_analysis_report.py`, `render_markdown.py`).
- Added `scripts/build_board_report.py` CLI.
- Two markdown files generated per run: Board (summary) and Technical (full detail).
- DOCX and HTML renderers deferred to Phase 4b.

### Methodology observations (not bugs)
- **Construction base risk score (2.68, 'Medium')** — logged as an active methodology review item. See Section 9 of this report. Session: noted, not fixed.

### Dev-ergonomics notes
- Fresh git worktrees do not carry the git-ignored raw ABS/RBA staging directories. Copy them from a primary checkout, or add a `bootstrap_worktree.py` helper. Not urgent; logged for future consideration.
