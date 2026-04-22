# Industry-Analysis — Phase 1 Baseline State

**Date:** 2026-04-22
**Worktree:** `.claude/worktrees/practical-wu-f936ab` (branch `claude/practical-wu-f936ab`)

## 1. Test suite

- **Collected:** 54 tests across 4 files
- **Result:** 54 passed, 0 failed, 0 skipped
- **Duration:** 1.61s
- **Warnings:** none

## 2. Pipeline scripts

| Script | Result | Notes |
|---|---|---|
| `download_public_data.py` | clean | Downloaded 3 PTRS PDFs, rebuilt PTRS workbook |
| `build_public_panels.py` | clean (after data copy) | Initially failed because worktree lacked git-ignored raw ABS/RBA staged data. Copied from main checkout; then built 9 business-cycle rows, 11 property-cycle rows, 1 macro-regime row |
| `build_overlays.py` | clean | 9 industry rows, 11 property rows, 4 downturn scenarios |
| `export_contracts.py` | clean | 4 core + 2 optional parquet exports written |
| `validate_upstream.py` | all green | 12 checks, all `True`; "Upstream validation passed" |

No warnings or stack traces on any script after data was staged.

## 3. Export inspection

| Export | Rows | Cols | Nulls | Latest date |
|---|---|---|---|---|
| industry_risk_scores | 9 | 7 | 0 | n/a (no date col) |
| property_market_overlays | 11 | 9 | 0 | n/a (no date col) |
| downturn_overlay_table | 4 | 7 | 0 | 2026-03-16 |
| macro_regime_flags | 1 | 6 | 0 | 2026-03-16 |
| business_cycle_panel | 9 | 32 | 21 | n/a (no date col) |
| property_cycle_panel | 11 | 12 | 0 | 2026-02-01 |

All 6 exports present, non-empty. Dated exports are within ~2 months of today (2026-04-22); not stale.

### Nulls in `business_cycle_panel`

21 nulls spread across 6 diagnostic columns (not core scoring columns):

- `gross_operating_profit_to_sales_ratio_latest` (2)
- `gross_operating_profit_to_sales_ratio_yoy_change` (2)
- `inventories_to_sales_ratio_latest` (5)
- `inventories_to_sales_ratio_yoy_change` (5)
- `demand_yoy_growth_pct` (2)
- `inventory_days_yoy_change` (5)

Core columns (`classification_risk_score`, `macro_risk_score`, `industry_base_risk_score`, `industry_base_risk_level`) are all populated. The nulls appear to reflect sectors where ABS does not publish the relevant ratio (e.g., service sectors without meaningful inventory-to-sales); `inventory_days_est_source` is already used to flag proxy/missing cases. Phase 2 anomaly scan will confirm.

## 4. Unexpected schemas

None. Schemas match what `improvements.md` describes:
- `industry_risk_scores` has `classification_risk_score`, `macro_risk_score`, `industry_base_risk_score`, `industry_base_risk_level`, `cash_rate_latest_pct`
- `property_market_overlays` has `property_segment`, `cycle_stage`, `market_softness_score`, `region_risk_score`, `market_softness_band`
- `downturn_overlay_table` has 4 scenarios with PD/LGD/CCF multipliers + `property_value_haircut` + `as_of_date=2026-03-16`

## 5. Validator output

`validate_upstream.py` reports 12 checks, all `status=True`:
- 4 core outputs present and non-empty
- 4 core export files exist on disk
- 2 optional outputs present and non-empty
- 2 optional export files exist on disk

Final line: `Upstream validation passed.`

## 6. Things that look off

Only two items worth flagging; neither looks broken:

1. **Worktree missing raw data.** The worktree started without `data/raw/public/abs/` and `data/raw/public/rba_f1_data.csv` (git-ignored). Expected on a fresh worktree; copied from the main checkout to proceed. No code fix needed — this is a developer-ergonomics note, not a pipeline defect.
2. **`business_cycle_panel` has 21 nulls in 6 diagnostic columns.** Concentrated in ratios that ABS does not publish for service sectors. Likely by design, but Phase 2 should verify the nulls correspond to the expected sectors and that no downstream scoring logic consumes these columns directly.

Nothing blocks Phase 2.
