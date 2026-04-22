# Industry Analysis — Enhancement Plan

## Project Context

This is the enhancement plan for the `industry-analysis` repo. This project is a standalone upstream public-data engine that produces overlay tables consumed by downstream credit-risk models.

**Sibling project:** `external-benchmark-engine` (separate repo, separate plan). That project consumes this project's `data/exports/*.parquet` contract outputs as one of its ingestion sources.

**This plan does NOT touch the external benchmark engine.** It only modifies the industry-analysis repo.

---

## Current State (Confirmed by Code Review)

### What works well (DO NOT CHANGE)
- All `src/` modules are actively used — zero orphaned code
- All `scripts/` are referenced and functional
- 4 test files, 553 lines of tests
- 6 contract exports produced correctly
- Methodology docs exist for both lending types
- Download → build → export → validate pipeline works end-to-end

### What needs work

| Issue | Severity | Action |
|---|---|---|
| ASIC insolvency loader exists but is orphaned (never called by pipeline) | Medium | Integrate into business cycle panel |
| No ASIC insolvency data file exists | Medium | Add ASIC data download or staging instructions |
| No ABS Counts of Australian Businesses (cat. 8165) for failure rate denominator | Medium | Add loader for ABS business counts |
| `__pycache__/` directories committed to git | Low | Add to .gitignore, remove from tracking |
| No data freshness checking | Medium | Add freshness check script |
| No `.claude/` session management | Low | Add for Claude Code continuity |
| No committee-ready report generation | High | Add report builder for Credit Committee / management |
| No explicit link to external benchmark engine in docs | Low | Update README and PROJECT_OVERVIEW |
| CoreLogic export spec not documented anywhere | Medium | Add CoreLogic export guide to docs |

---

## Implementation Tiers

### Tier 1: Cleanup & Hygiene

**1.1 Fix .gitignore**
- Add `__pycache__/` and `*.pyc` to `.gitignore`
- These are already committed; `git rm -r --cached` all `__pycache__` dirs

**1.2 Add `.claude/` session management**
- Create `.claude/.gitignore` (ignoring `CURRENT_STATE.md`)
- Create `.claude/CURRENT_STATE.md` with initial project status

**1.3 Update README.md**
Add these sections:
- "Integration with External Benchmark Engine" — explain that `data/exports/*.parquet` is consumed by the sibling project
- "Optional data staging" — how to stage ASIC insolvency and APRA property context files
- "CoreLogic export guide" — reference to `docs/corelogic_export_guide.md`

**1.4 Update PROJECT_OVERVIEW.md**
Add:
- Mention of external benchmark engine as primary downstream consumer
- Note that industry_risk_scores feed ANZSIC adjustment multipliers
- Note that downturn_overlay_table feeds downturn calibration

### Tier 2: ASIC Insolvency Integration

**2.1 Wire ASIC loader into pipeline**

`src/public_data/download_asic_insolvency.py` already has `load_optional_asic_insolvency_extract()`. Currently it is NOT imported or called anywhere.

Modify `src/panels/build_business_cycle_panel.py`:
```python
from src.public_data.download_asic_insolvency import load_optional_asic_insolvency_extract

def build_business_cycle_panel(...):
    ...
    # After foundation + macro panel is built:
    asic_df = load_optional_asic_insolvency_extract()
    if not asic_df.empty:
        # Merge insolvency counts by industry (map ASIC industry names → sector_key)
        # Add column: insolvency_signal (high/medium/low based on count relative to sector size)
        panel = _enrich_with_asic_insolvency(panel, asic_df)
    return panel
```

This is OPTIONAL enrichment — if no ASIC file is staged, the panel builds exactly as before (graceful empty DataFrame handling already exists in the loader).

**2.2 Add ABS Counts of Australian Businesses loader**

Create `src/public_data/load_abs_business_counts.py`:
- Load ABS cat. 8165 (Counts of Australian Businesses, Including Entries and Exits)
- Published annually as XLSX by ABS
- Extract: total business count by ANZSIC division
- Output columns: `anzsic_division_code, industry, business_count, as_of_year`

**2.3 Compute business failure rate**

When BOTH ASIC insolvency data AND ABS business counts are available:
```python
failure_rate = insolvency_count / business_count
```
Add `failure_rate` and `failure_rate_band` columns to `industry_risk_scores` output.

When either source is missing, these columns are NaN (graceful degradation).

**2.4 Add ABS cat. 8165 URL to config.py**

```python
PUBLIC_SOURCE_URLS = {
    ...
    "abs_business_counts_xlsx": "https://www.abs.gov.au/statistics/economy/business-indicators/counts-australian-businesses-including-entries-and-exits/latest-release",
}
```

**2.5 Update download_public_data.py**

Add ABS cat. 8165 to the download list (if URL is stable; otherwise document manual staging).

**2.6 Tests**
- Test that `build_business_cycle_panel()` still works with no ASIC data (existing behavior preserved)
- Test that when ASIC data is provided, `insolvency_signal` column appears
- Test that when both ASIC + ABS counts exist, `failure_rate` is computed correctly
- Test failure rate bounds: must be ∈ [0, 0.10]

### Tier 3: Data Freshness Checker

**3.1 Create `scripts/check_data_freshness.py`**

Scans `data/raw/public/` for data files and reports staleness:

```python
EXPECTED_REFRESH = {
    "abs": 90,       # Quarterly
    "rba": 30,       # Monthly
    "ptrs": 180,     # Semi-annual
    "asic": 90,      # Quarterly (when staged)
}
```

Logic:
- Parse date from filename (e.g., `6291004_feb2026_labour_force_industry.xlsx` → Feb 2026)
- Compare to today
- Report: file, extracted date, age in days, expected refresh days, status (fresh/stale/missing)

Output: print to console + optionally write `outputs/data_freshness_report.csv`

**3.2 Add freshness check to validate_upstream.py**

After validating contract outputs, also run freshness check and warn (but don't fail) if any source is stale.

### Tier 4: CoreLogic Export Guide

**4.1 Create `docs/corelogic_export_guide.md`**

This documents exactly what data to export from your CoreLogic subscription for use by the external benchmark engine's LGD decomposition.

Contents:
- Which CoreLogic reports/products to access
- What fields to export
- Expected CSV format with column names and example rows
- Where to save the exported CSV (in external benchmark engine's `data/corelogic/` directory, NOT in this repo)
- How the external benchmark engine uses each field

Data points needed:

| CoreLogic report | Field to export | Engine use | CSV column name |
|---|---|---|---|
| Home Value Index | Median dwelling price by region + property type | Collateral value input | `median_price` |
| Home Value Index (historical) | Peak-to-trough worst decline by region | Downturn haircut calibration | `peak_to_trough_decline` |
| Home Value Index (quarterly) | Current quarterly price change | Normal haircut derivation | `quarterly_price_change` |
| Market Trends | Median days on market by region + property type | Time to recovery (LGD component) | `days_on_market` |
| Market Trends | Vendor discount % below listing | Forced-sale haircut premium | `vendor_discount` |
| Auction Results | Weekly clearance rate by capital city | Market liquidity flag | `auction_clearance_rate` |

Expected CSV format:
```csv
region,property_type,metric_name,value,unit,as_of_date,source_note
Sydney_metro,house,median_price,1450000,dollars,2025-12-31,CoreLogic HVI Dec 2025
Sydney_metro,house,peak_to_trough_decline,0.147,ratio,2025-12-31,CoreLogic historical worst
Sydney_metro,house,days_on_market,32,days,2025-12-31,CoreLogic Market Trends Dec 2025
Sydney_metro,unit,median_price,820000,dollars,2025-12-31,CoreLogic HVI Dec 2025
Regional_NSW,house,median_price,650000,dollars,2025-12-31,CoreLogic HVI Dec 2025
Regional_NSW,house,peak_to_trough_decline,0.22,ratio,2025-12-31,CoreLogic historical worst
Melbourne_metro,house,auction_clearance_rate,0.62,ratio,2025-12-31,CoreLogic Auction Results
Brisbane_metro,house,auction_clearance_rate,0.71,ratio,2025-12-31,CoreLogic Auction Results
```

Regions to cover: Sydney metro, Melbourne metro, Brisbane metro, Perth metro, Adelaide metro, Regional NSW, Regional VIC, Regional QLD.

Property types: house, unit (residential); commercial (if available).

**Note:** CoreLogic data stays in the external benchmark engine project, NOT in this repo. This repo only documents what to export.

### Tier 5: Committee Report Generation

**5.1 Create `reports/` folder**

```
industry-analysis/
├── reports/
│   ├── __init__.py
│   ├── environment_report.py    ← Industry & Property Environment report
│   └── templates/               ← Optional DOCX templates
```

**5.2 Build `reports/environment_report.py`**

Class `EnvironmentReport` that reads contract exports and generates a committee-ready report.

```python
class EnvironmentReport:
    def __init__(self, exports_dir: Path):
        """Read all contract parquet exports."""
        self.industry_risk = pd.read_parquet(exports_dir / "industry_risk_scores.parquet")
        self.property_overlays = pd.read_parquet(exports_dir / "property_market_overlays.parquet")
        self.downturn_overlay = pd.read_parquet(exports_dir / "downturn_overlay_table.parquet")
        self.macro_regime = pd.read_parquet(exports_dir / "macro_regime_flags.parquet")
        self.business_cycle = pd.read_parquet(exports_dir / "business_cycle_panel.parquet")
        self.property_cycle = pd.read_parquet(exports_dir / "property_cycle_panel.parquet")
    
    def generate(self) -> dict:
        """Return structured report content."""
        return {
            "executive_summary": self._build_executive_summary(),
            "macro_environment": self._build_macro_section(),
            "industry_risk_scores": self._build_industry_section(),
            "business_cycle_detail": self._build_business_cycle_section(),
            "property_cycle": self._build_property_cycle_section(),
            "property_market_overlays": self._build_property_overlays_section(),
            "downturn_scenarios": self._build_downturn_section(),
            "data_freshness": self._build_freshness_section(),
            "methodology_summary": self._build_methodology_section(),
        }
    
    def to_docx(self, path: Path):
        """Generate Word document for Credit Committee."""
        ...
    
    def to_html(self, path: Path):
        """Generate HTML report for internal distribution."""
        ...
```

**Report sections:**

| Section | Content | Source |
|---|---|---|
| 1. Executive summary | Overall macro regime, key sector movements, property cycle position | All exports combined |
| 2. Macro environment | Cash rate regime, arrears environment, trend direction | `macro_regime_flags.parquet` |
| 3. Industry risk scores | ANZSIC sector risk ranking with classification and macro components | `industry_risk_scores.parquet` |
| 4. Business cycle detail | Full panel: margins, employment, sales growth, inventory signals | `business_cycle_panel.parquet` |
| 5. Property cycle | Segment-level cycle stage, softness scores, approvals momentum | `property_cycle_panel.parquet` |
| 6. Property market overlays | Compact risk bands for downstream systems | `property_market_overlays.parquet` |
| 7. Downturn scenarios | Base/mild/moderate/severe multipliers and haircuts | `downturn_overlay_table.parquet` |
| 8. Data freshness | Age of each raw data source, traffic light status | `check_data_freshness.py` output |
| 9. Methodology summary | How scores are derived, links to methodology docs | Static text + links |

**5.3 Add CLI command**

Add to a new `scripts/generate_reports.py`:

```bash
python scripts/generate_reports.py --format docx --output outputs/reports/
python scripts/generate_reports.py --format html --output outputs/reports/
```

**5.4 DOCX formatting**

For the Word document output:
- Title page: "Industry & Property Environment Report — [Quarter] [Year]"
- Credit Committee header format
- Tables for industry risk scores and property cycle
- Traffic light indicators for data freshness (green/amber/red)
- Methodology appendix with links to full methodology docs

Use `python-docx` as optional dependency:
```toml
[project.optional-dependencies]
reports = ["python-docx>=1.0", "matplotlib>=3.8"]
```

**5.5 Tests**
- Test report generation with existing fixture data
- Test to_docx produces non-empty file with expected section headings
- Test to_html produces valid HTML
- Test graceful degradation when optional parquets (business_cycle_panel, property_cycle_panel) are missing

### Tier 6: Integration Contract Documentation

**6.1 Create `docs/integration_contract.md`**

Documents the exact contract between this repo and the external benchmark engine:

```markdown
# Integration Contract: industry-analysis → external-benchmark-engine

## Contract Outputs

The external benchmark engine's ingestion layer imports these files:

| File | Fields consumed | Engine module |
|---|---|---|
| industry_risk_scores.parquet | industry, industry_base_risk_score, industry_base_risk_level | adjustments.py (ANZSIC multiplier) |
| downturn_overlay_table.parquet | scenario, pd_multiplier, lgd_multiplier, property_value_haircut | downturn.py (uplift factors) |
| property_market_overlays.parquet | property_segment, cycle_stage, market_softness_score | downturn.py (condition selection) |
| macro_regime_flags.parquet | cash_rate_regime, arrears_environment_level, arrears_trend | calibration_feed.py (cycle adjustment) |

## ANZSIC Risk Score → Industry Multiplier Mapping

The external benchmark engine maps industry_base_risk_score to adjustment multipliers:

| Risk score range | Risk level | Industry multiplier (PC) |
|---|---|---|
| 1.0 – 1.5 | Low | 0.50x |
| 1.5 – 2.0 | Low-Medium | 0.70x |
| 2.0 – 2.5 | Medium | 0.85x |
| 2.5 – 3.0 | Medium-Elevated | 1.00x |
| 3.0 – 3.5 | Elevated | 1.30x |
| 3.5 – 4.0 | High | 1.60x |
| 4.0 – 5.0 | Very High | 2.00x |

## Refresh Cadence

Industry-analysis should refresh quarterly (aligned with ABS quarterly data).
External benchmark engine re-imports after each refresh.

## Breaking Changes

Do NOT rename or remove columns from contract exports without updating the
external benchmark engine's ingestion/industry_analysis_import.py.
```

---

## Implementation Order

1. **Tier 1: Cleanup** — .gitignore, .claude/, README updates (30 min)
2. **Tier 2: ASIC integration** — wire loader, add ABS business counts, compute failure rates (60-90 min)
3. **Tier 3: Data freshness** — check_data_freshness.py (30 min)
4. **Tier 4: CoreLogic guide** — docs/corelogic_export_guide.md (20 min, documentation only)
5. **Tier 5: Committee reports** — environment_report.py + CLI + DOCX export (60-90 min)
6. **Tier 6: Integration docs** — docs/integration_contract.md (20 min, documentation only)

Each tier's tests must pass before moving to the next.

---

## Prompt for Claude Code

```
Read docs/enhancement_plan.md and execute all tiers in order.

Current project state:
- All src/ modules work correctly, zero orphaned code
- 6 contract exports producing correctly
- 4 test files, 553 lines
- Pipeline: download → build panels → export contracts → validate

Build tiers 1-6 without stopping:

Tier 1: Cleanup
- Add __pycache__/ and *.pyc to .gitignore
- Create .claude/ folder with .gitignore and CURRENT_STATE.md
- Update README.md with integration notes and optional staging instructions

Tier 2: ASIC Integration  
- Wire load_optional_asic_insolvency_extract() into build_business_cycle_panel.py
- Create src/public_data/load_abs_business_counts.py for ABS cat. 8165
- Compute failure_rate = insolvency_count / business_count when both available
- Add failure_rate column to industry_risk_scores output
- Graceful degradation: NaN when data missing (preserve existing behavior)
- Tests for all paths

Tier 3: Data Freshness
- Create scripts/check_data_freshness.py
- Parse dates from filenames in data/raw/public/
- Report staleness vs expected refresh (ABS 90d, RBA 30d, PTRS 180d)
- Output to console + optional CSV

Tier 4: CoreLogic Guide
- Create docs/corelogic_export_guide.md with exact export spec
- List 6 data points, CSV format, regions, property types
- Note: data goes to external benchmark engine, not this repo

Tier 5: Committee Reports
- Create reports/environment_report.py
- Read all 6 contract parquets
- Generate structured report with 9 sections
- to_docx() for Credit Committee (lazy import python-docx)
- to_html() for internal distribution
- Add scripts/generate_reports.py CLI
- Tests

Tier 6: Integration Contract
- Create docs/integration_contract.md
- Document exact fields consumed by external benchmark engine
- Document ANZSIC risk score → multiplier mapping
- Document refresh cadence and breaking change rules

Update .claude/CURRENT_STATE.md when done.
```

---

## Verification

1. All existing tests still pass (zero regression)
2. `python scripts/export_contracts.py` produces all 6 parquet exports
3. `python scripts/validate_upstream.py` passes
4. `python scripts/check_data_freshness.py` reports freshness for all raw data files
5. `python scripts/generate_reports.py --format html` produces readable HTML report
6. `industry_risk_scores.parquet` still has 9 sectors; if ASIC data staged, has `failure_rate` column
7. `docs/corelogic_export_guide.md` exists with complete CSV spec
8. `docs/integration_contract.md` exists with field-level contract
9. `.claude/CURRENT_STATE.md` reflects completion status
