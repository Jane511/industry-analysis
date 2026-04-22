# Industry Analysis Report — Q1 2026

*Board Summary variant. Generated 2026-04-23.*



Macro and downturn overlays as of 2026-03-16. Property cycle data as of 2026-02-01.

This is a summary view for non-technical reviewers. Every table and chart in this document traces back to the canonical parquet contracts in `data/exports/`. For full per-column detail, methodology references, and the audit-log appendix, see the Technical variant.



## 1. Executive Summary

This report summarises the current state of Australian industry and property market risk using public macro, industry, and property data. Overlays cover 9 industries and 11 property segments. Cash rate sits at 3.85%, 0.25pp lower than a year ago; arrears environment is Low and improving. 4 of 9 industries currently score Elevated on the base risk scale. 1 property segment is in downturn, 1 is slowing, and 3 are in growth.

> **How to read this report**
>
> This report uses a 1–5 risk-score scale with four bands:
> - Low (< 2.0) — defensive, structurally resilient
> - Medium (2.0 – 2.75) — neutral, typical business-cycle exposure
> - Elevated (2.75 – 3.5) — cyclical or rate-sensitive; monitor closely
> - High (> 3.5) — stressed or structurally vulnerable

## 2. Macro Regime

Macro conditions shape how every industry and property segment is stressed. The cash rate is the dominant conditioning variable; the arrears backdrop confirms whether rate moves are already showing in borrower behaviour.

*Macro regime snapshot as of 2026-03-16*

| Metric | Value |
| --- | --- |
| Cash rate (latest) | 3.85% |
| Cash rate 1y change | -0.25pp |
| Cash rate regime | neutral_easing |
| Arrears environment | Low |
| Arrears trend | Improving |
| Macro regime flag | base |

Combined with a low arrears backdrop, this suggests borrowers are absorbing rate pressure; credit models should weight structural over cyclical factors in current calibration. The downturn overlays currently apply the 'base' scenario (no uplift to PD/LGD/CCF).

## 3. Industry Risk Rankings

Industries are ranked by a combined base risk score that blends structural classification risk (cyclicality, concentration, capital intensity) with current macro sensitivity. The table below is ordered highest-risk first.

*All 9 industries ranked by base risk score*

| Rank | Industry | Base score | Level |
| --- | --- | --- | --- |
| 1 | Agriculture, Forestry And Fishing | 3.50 | Elevated |
| 2 | Manufacturing | 3.50 | Elevated |
| 3 | Wholesale Trade | 3.23 | Elevated |
| 4 | Retail Trade | 3.23 | Elevated |
| 5 | Accommodation And Food Services | 2.68 | Medium |
| 6 | Construction | 2.68 | Medium |
| 7 | Health Care and Social Assistance | 2.22 | Medium |
| 8 | Professional, Scientific And Technical Services | 2.18 | Medium |
| 9 | Transport, Postal And Warehousing | 2.14 | Medium |

> **Construction ranking**
>
> **Methodology note.** Construction base risk score (2.68, 'Medium') reflects structural classification risk only, not current insolvency pressure. See Section 9 for methodology context and the active review item.

The top 4 industries all sit in the 'Elevated' band, driven by structural cyclicality and current rate sensitivity. Defensive sectors (Health Care; Professional, Scientific and Technical) sit at the lower end, as expected.

## 4. Top Risk Industries

These are the five industries with the highest combined base risk score in the current environment. Review these first when calibrating portfolio concentration limits or sector caps.

*Top 5 industries by base risk score*

| Industry | Base score | Level |
| --- | --- | --- |
| Agriculture, Forestry And Fishing | 3.50 | Elevated |
| Manufacturing | 3.50 | Elevated |
| Wholesale Trade | 3.23 | Elevated |
| Retail Trade | 3.23 | Elevated |
| Accommodation And Food Services | 2.68 | Medium |

## 5. Property Market Overlays

Property overlays track 11 commercial and non-residential segments through the cycle. Each segment is classified into one of four cycle stages (downturn, slowing, neutral, growth) using approvals momentum as the primary signal.

*All 11 segments grouped by cycle stage (as of 2026-02-01)*

| Segment | Cycle | Softness score | Region band |
| --- | --- | --- | --- |
| Offices | downturn | 4.30 | High |
| Education buildings | slowing | 3.25 | Elevated |
| Retail and wholesale trade buildings | neutral | 3.15 | Medium |
| Aged care facilities | neutral | 2.70 | Medium |
| Agricultural and aquacultural buildings | neutral | 2.65 | Medium |
| Total Non-residential | neutral | 2.60 | Medium |
| Industrial Buildings - Total | neutral | 2.40 | Medium |
| Warehouses | neutral | 2.20 | Medium |
| Short term accommodation buildings | growth | 2.85 | Medium |
| Commercial Buildings - Total | growth | 2.30 | Medium |
| Health buildings | growth | 1.65 | Low |

Segments are grouped with downturn first, then slowing, neutral, and growth. Offices is the only segment flagged in downturn; Health buildings, Commercial Buildings Total, and Short-term accommodation are the three segments in growth.

## 6. Property Cycle Interpretation

1 segment is currently in downturn (Offices). 1 is slowing (Education buildings). 6 segments sit in neutral, and 3 are in growth (Short term accommodation buildings, Commercial Buildings - Total, Health buildings). For property-backed lending, Offices warrants elevated caution; the growth-stage segments look supportive but should be read alongside the approvals-base-effect caveat below.

## 7. Downturn Scenarios

Downturn overlays provide illustrative multipliers for PD, LGD, and CCF, plus property value haircuts, under four scenarios. These support scenario analysis and conservative pricing; they are not calibrated regulatory stress parameters.

*Illustrative downturn multipliers (as of 2026-03-16)*

| Scenario | PD × | LGD × | CCF × | Property haircut |
| --- | --- | --- | --- | --- |
| base | 1.00 | 1.00 | 1.00 | 0.00 |
| mild | 1.20 | 1.10 | 1.05 | 0.05 |
| moderate | 1.50 | 1.20 | 1.10 | 0.10 |
| severe | 2.00 | 1.30 | 1.20 | 0.20 |

Apply multiplicatively to modelled PD/LGD/CCF; haircut applies to property valuations in collateral-backed lines. The severe scenario doubles PD; mild and moderate are graduated. Current environment selects the 'base' row (see Section 2).

## 8. Data Sources and Freshness

Each overlay is built from public data refreshed on a published cadence. The table below lists the primary source and last-refresh date for each contract.

*Primary sources and refresh dates*

| Overlay | Primary source | Refreshed |
| --- | --- | --- |
| industry_risk_scores | ABS Economic Activity Survey + RBA F1 | 2026-03-16 |
| property_market_overlays | ABS Building Approvals (non-residential) | 2026-02-01 |
| downturn_overlay_table | Staged arrears context + property softness | 2026-03-16 |
| macro_regime_flags | RBA F1 cash-rate table + arrears staging | 2026-03-16 |
| business_cycle_panel | ABS EAS + RBA F1 (panel assembly) | 2026-03-16 |
| property_cycle_panel | ABS Building Approvals | 2026-02-01 |

## 9. Validation and Caveats

Contract validation runs automatically before every downstream handoff. All 12 current checks passed on the latest pipeline run. This section also documents active methodology review items and known gaps.

*Contract validation summary*

| Check category | Items | Status |
| --- | --- | --- |
| Core contract presence | 4 | Pass |
| Core contract file on disk | 4 | Pass |
| Optional panel presence | 2 | Pass |
| Optional panel file on disk | 2 | Pass |

Two caveats to flag: (1) Construction's 'Medium' rating reflects structural factors only, not current insolvency pressure — see the callout below. (2) Property overlay commencements and completions are proxied from approvals in this cycle, not directly observed.

> **Methodology review item: Construction ranking**
>
> Construction scores 2.68 ('Medium'). Market narrative (builder insolvencies, subcontractor arrears, fixed-price-contract pressure) suggests this understates near-term credit risk. The Australian construction sector has seen three major builder collapses (Porter Davis, Probuild, Clough) over 2024-2026; this sector-specific stress isn't captured in structural risk scoring. Logged as an active methodology review item; this session did not apply a fix — the Technical variant of this report documents the full discussion and three review options.

## 10. Methodology References

Full methodology manuals are maintained in the repo `docs/` folder. These describe how each overlay is constructed from raw inputs.

*Methodology documents*

| Area | Document |
| --- | --- |
| Cash-flow lending | docs/methodology_cash_flow_lending.md |
| Property-backed lending | docs/methodology_property_backed_lending.md |
| Audit + polish log (this session) | outputs/industry_analysis_audit_log.md |
| Baseline state | outputs/baseline_state.md |
