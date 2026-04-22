# Industry-Analysis Project — Review, Polish, and Board Report

## Context for Claude Code

**Project:** `industry-analysis`
**Location:** User's sibling project alongside `external_benchmark_engine`
**Language:** Python 3.13, Windows/PowerShell
**Owns:** Public-data ingestion, panel construction, and overlay exports for downstream credit modelling repos

**Goal of this session:** Do for `industry-analysis` what the prior sessions did for `external_benchmark_engine`:

1. Audit the current state (what actually works vs what's documented)
2. Fix any silent data-quality issues (the equivalent of the CR9 pollution bug)
3. Add a board-style report that lets a non-technical reviewer see all industry analysis with commentary
4. Document what's clean, what's broken, and what remains as follow-up

This session is a **defensive audit + polish** — not a new feature build. Do not add new overlay logic. Do not invent new data sources. Work with what exists.

## Project structure (from prior inspection)

```
industry-analysis/
├── data/
│   ├── raw/
│   │   ├── public/               # Downloaded by scripts/download_public_data.py
│   │   └── manual/               # Manually staged inputs (user places here)
│   ├── processed/public/         # Intermediate reference CSVs
│   └── exports/                  # THE CONTRACT — parquet files downstream consumes
│       ├── industry_risk_scores.parquet        ← core
│       ├── property_market_overlays.parquet    ← core
│       ├── downturn_overlay_table.parquet      ← core
│       ├── macro_regime_flags.parquet          ← core
│       ├── business_cycle_panel.parquet        ← optional explainability
│       └── property_cycle_panel.parquet        ← optional explainability
├── src/
│   ├── public_data/              # Download + parse raw public sources
│   ├── panels/                   # Build cleaned panels from raw
│   ├── overlays/                 # Build overlay scores from panels
│   ├── arrears_environment.py
│   ├── config.py
│   ├── output.py
│   ├── ptrs_reconstruction.py
│   ├── utils.py
│   └── validation.py
├── scripts/
│   ├── download_public_data.py
│   ├── build_public_panels.py
│   ├── build_overlays.py
│   ├── export_contracts.py
│   └── validate_upstream.py
├── tests/
│   ├── test_foundation_and_macro.py
│   ├── test_ptrs_reconstruction.py
│   ├── test_reference_layer.py
│   └── test_utils.py
├── outputs/tables/               # Derived inspection CSVs (auto-generated)
├── notebooks/                    # 6 walkthrough notebooks
├── docs/
│   ├── methodology_cash_flow_lending.md
│   └── methodology_property_backed_lending.md
└── pyproject.toml, requirements.txt, README.md, PROJECT_OVERVIEW.md
```

## What we already know about current state

Sample outputs visible in `outputs/tables/`:

- `industry_risk_scores.csv` — 9+ industries ranked with `classification_risk_score`, `macro_risk_score`, `industry_base_risk_score`, `industry_base_risk_level`, `cash_rate_latest_pct`
- `property_market_overlays.csv` — 9+ property segments with `cycle_stage`, `market_softness_score`, `region_risk_score`, `market_softness_band`
- `downturn_overlay_table.csv` — 4 scenarios (base / mild / moderate / severe) with PD/LGD/CCF multipliers and property haircuts, dated 2026-03-16

Core contract is delivering reasonable-looking output. Tests exist but coverage breadth unknown.

---

## The work to do (6 phases)

### Phase 1 — Establish baseline (no code changes)

Before changing anything, capture the current state so any regression is visible.

**Step 1.1 — Run the test suite**

```powershell
cd industry-analysis
pytest -v 2>&1 | tee outputs/baseline_pytest.log
```

Record:
- Total tests
- Passing / failing / skipped
- Any warnings
- Total time

**Step 1.2 — Run the full pipeline**

```powershell
python -m pip install -r requirements.txt
python scripts/download_public_data.py 2>&1 | tee outputs/baseline_download.log
python scripts/build_public_panels.py 2>&1 | tee outputs/baseline_panels.log
python scripts/build_overlays.py 2>&1 | tee outputs/baseline_overlays.log
python scripts/export_contracts.py 2>&1 | tee outputs/baseline_export.log
python scripts/validate_upstream.py 2>&1 | tee outputs/baseline_validate.log
```

Record:
- Does each script complete?
- Which ones emit warnings / errors / stack traces?
- Does `validate_upstream.py` report all green or does it flag anything?

**Step 1.3 — Inspect the parquet exports**

Create `audit_exports.py` in the project root:

```python
"""Inspect each parquet contract export for schema, row count, nulls, and freshness."""
import pandas as pd
from pathlib import Path

EXPORTS = [
    "industry_risk_scores",
    "property_market_overlays",
    "downturn_overlay_table",
    "macro_regime_flags",
    "business_cycle_panel",
    "property_cycle_panel",
]

exports_dir = Path("data/exports")
print(f"{'Export':<30} {'Rows':>8} {'Cols':>6} {'Nulls':>8} {'Latest date':>15}")
print("-" * 75)

for name in EXPORTS:
    path = exports_dir / f"{name}.parquet"
    if not path.exists():
        print(f"{name:<30} MISSING")
        continue
    df = pd.read_parquet(path)

    # Find date-ish columns
    date_cols = [c for c in df.columns if "date" in c.lower()]
    latest = "n/a"
    if date_cols:
        d = pd.to_datetime(df[date_cols[0]], errors="coerce")
        if d.notna().any():
            latest = str(d.max().date())

    null_count = df.isna().sum().sum()
    print(f"{name:<30} {len(df):>8} {len(df.columns):>6} {null_count:>8} {latest:>15}")

print()
print("=" * 75)
print("Full schema per export:")
print("=" * 75)

for name in EXPORTS:
    path = exports_dir / f"{name}.parquet"
    if not path.exists():
        continue
    df = pd.read_parquet(path)
    print(f"\n--- {name} ({len(df)} rows) ---")
    print(df.dtypes.to_string())
```

Run:

```powershell
python audit_exports.py > outputs/baseline_audit.txt
```

Review the output for:
- Any export with 0 rows → pipeline is silently producing empty data
- Any export with all-null columns → downstream will fail silently
- Any stale `latest date` (older than 12 months) → data is out of date

**Step 1.4 — Record findings**

Create `outputs/baseline_state.md` summarising:
- Test pass/fail count
- Which scripts complete without warnings
- Any stale or empty exports
- Any unexpected schemas
- Validator output

**STOP GATE:** Show the baseline findings to the user before proceeding to Phase 2. If anything is already broken, we fix *that* before adding polish.

---

### Phase 2 — Data-quality audit (the "CR9 hunt")

In the benchmark engine, a silent extraction bug was misclassifying one regulatory table as another (CR9 as CR6). The polluted values were small but monotonic — telltale signs of wrong-column extraction. Apply the same discipline here.

**Step 2.1 — Check for implausible values in each overlay**

Create `scan_for_anomalies.py`:

```python
"""Scan each overlay export for implausible or suspicious values.

The overlays use bounded ranges for scores and multipliers. Anything outside
those ranges is either a bug or needs a documented override.
"""
import pandas as pd
from pathlib import Path

findings = []

def flag(export: str, severity: str, message: str):
    findings.append({"export": export, "severity": severity, "message": message})


# --- industry_risk_scores ---
df = pd.read_parquet("data/exports/industry_risk_scores.parquet")
for col in ["classification_risk_score", "macro_risk_score", "industry_base_risk_score"]:
    if col not in df.columns:
        flag("industry_risk_scores", "HIGH", f"missing column: {col}")
        continue
    # Scores are typically 1-5 in Australian credit risk frameworks
    out_of_range = df[(df[col] < 1) | (df[col] > 5)]
    if not out_of_range.empty:
        flag("industry_risk_scores", "MEDIUM",
             f"{col} has {len(out_of_range)} rows outside [1, 5]")
    if df[col].isna().any():
        flag("industry_risk_scores", "MEDIUM",
             f"{col} has nulls; downstream joins will drop rows")

# --- property_market_overlays ---
df = pd.read_parquet("data/exports/property_market_overlays.parquet")
for col in ["market_softness_score", "region_risk_score"]:
    if col not in df.columns:
        flag("property_market_overlays", "HIGH", f"missing column: {col}")
        continue
    oor = df[(df[col] < 1) | (df[col] > 5)]
    if not oor.empty:
        flag("property_market_overlays", "MEDIUM",
             f"{col} has {len(oor)} rows outside [1, 5]")

# Cycle stage should be one of a known set
if "cycle_stage" in df.columns:
    known_stages = {"growth", "neutral", "slowing", "downturn"}
    unknown = set(df["cycle_stage"].dropna().unique()) - known_stages
    if unknown:
        flag("property_market_overlays", "MEDIUM",
             f"cycle_stage has unknown values: {unknown}")

# --- downturn_overlay_table ---
df = pd.read_parquet("data/exports/downturn_overlay_table.parquet")
expected_scenarios = {"base", "mild", "moderate", "severe"}
got = set(df["scenario"].unique()) if "scenario" in df.columns else set()
if expected_scenarios - got:
    flag("downturn_overlay_table", "HIGH",
         f"missing scenarios: {expected_scenarios - got}")

# Multipliers must be monotonic: base <= mild <= moderate <= severe
if "scenario" in df.columns:
    sorted_df = df.set_index("scenario").reindex(["base", "mild", "moderate", "severe"])
    for mult in ["pd_multiplier", "lgd_multiplier", "ccf_multiplier"]:
        if mult in sorted_df.columns:
            vals = sorted_df[mult].dropna().tolist()
            if vals != sorted(vals):
                flag("downturn_overlay_table", "HIGH",
                     f"{mult} not monotonic base->severe: {vals}")

    # Base scenario must have multiplier=1.0 (no adjustment)
    base_row = sorted_df.loc["base"]
    for mult in ["pd_multiplier", "lgd_multiplier", "ccf_multiplier"]:
        if mult in base_row and base_row[mult] != 1.0:
            flag("downturn_overlay_table", "MEDIUM",
                 f"base scenario {mult}={base_row[mult]}, expected 1.0")

# --- macro_regime_flags ---
df = pd.read_parquet("data/exports/macro_regime_flags.parquet")
if df.empty:
    flag("macro_regime_flags", "HIGH", "zero rows in export")

# --- business_cycle_panel (optional) ---
path = Path("data/exports/business_cycle_panel.parquet")
if path.exists():
    df = pd.read_parquet(path)
    if df.empty:
        flag("business_cycle_panel", "LOW", "optional panel is empty")

# --- property_cycle_panel (optional) ---
path = Path("data/exports/property_cycle_panel.parquet")
if path.exists():
    df = pd.read_parquet(path)
    if df.empty:
        flag("property_cycle_panel", "LOW", "optional panel is empty")


# --- Print report ---
if not findings:
    print("No anomalies found. All overlays within expected ranges.")
else:
    by_sev = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for f in findings:
        by_sev[f["severity"]].append(f)

    for sev in ["HIGH", "MEDIUM", "LOW"]:
        items = by_sev[sev]
        if not items:
            continue
        print(f"\n{sev} severity ({len(items)} findings):")
        for f in items:
            print(f"  [{f['export']}] {f['message']}")

    print(f"\nTotal findings: {len(findings)}")
```

Run:

```powershell
python scan_for_anomalies.py > outputs/anomaly_scan.txt
```

**Step 2.2 — Review findings with the user**

**STOP GATE:** Show anomaly findings before fixing anything. Same discipline as the benchmark engine: diagnose first, fix only after hypothesis confirmed.

Expected outcomes:

- **Zero findings** → overlays are healthy; skip to Phase 3
- **LOW only** → nothing urgent; proceed to Phase 3 and note in final log
- **MEDIUM findings** → investigate each; most are likely null handling or range edges
- **HIGH findings** → stop and investigate; these are equivalent to the CR9 bug

For any HIGH finding, trace back through the pipeline:
1. Which script produced the bad value?
2. Which source file did it read from?
3. Is the issue in the raw data, the cleaning step, or the scoring logic?

Do NOT add a filter or threshold to hide bad values. Fix root cause.

---

### Phase 3 — Test coverage audit

**Step 3.1 — Map tests to source modules**

Create `test_coverage_map.py`:

```python
"""Map which source modules have direct test coverage."""
import ast
from pathlib import Path

src_files = {p.stem for p in Path("src").rglob("*.py") if p.stem != "__init__"}
test_files = {p for p in Path("tests").rglob("test_*.py")}

# Find imports in each test file
coverage = {}
for test in test_files:
    tree = ast.parse(test.read_text())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("src"):
            parts = node.module.split(".")
            if len(parts) >= 2:
                imports.add(parts[-1])
    for imp in imports:
        coverage.setdefault(imp, []).append(test.name)

print(f"{'Source module':<40} {'Tested by':<40}")
print("-" * 80)
for src in sorted(src_files):
    tested_by = coverage.get(src, [])
    status = ", ".join(tested_by) if tested_by else "(untested)"
    print(f"{src:<40} {status}")

untested = [s for s in src_files if s not in coverage]
print(f"\n{len(untested)} / {len(src_files)} source modules have no direct test import")
```

```powershell
python test_coverage_map.py > outputs/test_coverage.txt
```

**Step 3.2 — Add minimum viable tests for critical uncovered modules**

Focus on overlay builders and export contract — these are what downstream repos consume.

For each untested critical module in `src/overlays/` and `src/panels/`, add one or two tests that:
- Call the module's main build function with minimal inputs
- Assert the output has the expected schema (column names, dtypes)
- Assert no all-null columns
- Assert row count > 0

Example structure for `tests/test_overlay_exports.py`:

```python
"""Basic contract tests for overlay builders.

These tests guarantee each overlay produces output with the expected schema,
row count, and no silent nulls. They do not check business logic; they check
that the pipeline doesn't produce empty or malformed contracts.
"""
import pandas as pd
import pytest
from pathlib import Path


REQUIRED_EXPORTS = {
    "industry_risk_scores": ["industry", "industry_base_risk_score", "industry_base_risk_level"],
    "property_market_overlays": ["property_segment", "cycle_stage", "market_softness_score"],
    "downturn_overlay_table": ["scenario", "pd_multiplier", "lgd_multiplier"],
    "macro_regime_flags": [],  # columns depend on implementation; just assert non-empty
}


@pytest.mark.parametrize("export_name,required_cols", REQUIRED_EXPORTS.items())
def test_export_has_required_schema(export_name, required_cols):
    path = Path(f"data/exports/{export_name}.parquet")
    if not path.exists():
        pytest.skip(f"{export_name} not yet built (run export_contracts.py first)")
    df = pd.read_parquet(path)
    assert len(df) > 0, f"{export_name} has zero rows"
    for col in required_cols:
        assert col in df.columns, f"{export_name} missing required column {col}"


@pytest.mark.parametrize("export_name", REQUIRED_EXPORTS.keys())
def test_export_has_no_all_null_columns(export_name):
    path = Path(f"data/exports/{export_name}.parquet")
    if not path.exists():
        pytest.skip(f"{export_name} not yet built")
    df = pd.read_parquet(path)
    all_null = [c for c in df.columns if df[c].isna().all()]
    assert not all_null, f"{export_name} has all-null columns: {all_null}"


def test_downturn_overlay_scenarios_are_monotonic():
    """Multipliers must increase from base -> severe."""
    path = Path("data/exports/downturn_overlay_table.parquet")
    if not path.exists():
        pytest.skip("downturn_overlay_table not yet built")
    df = pd.read_parquet(path).set_index("scenario")

    # Skip if expected scenarios missing (will be flagged elsewhere)
    required = ["base", "mild", "moderate", "severe"]
    if not all(s in df.index for s in required):
        pytest.skip("downturn scenarios incomplete")

    ordered = df.reindex(required)
    for mult in ["pd_multiplier", "lgd_multiplier", "ccf_multiplier"]:
        if mult not in ordered.columns:
            continue
        vals = ordered[mult].tolist()
        assert vals == sorted(vals), (
            f"{mult} is not monotonic base->severe: {vals}"
        )
```

Run:

```powershell
pytest -v
```

Confirm new tests pass against the existing parquet files. If they fail, that's an anomaly finding to resolve.

---

### Phase 4 — Board report (the main deliverable)

Build a board-facing report equivalent to the benchmark engine's Report 1. The user has explicitly asked for this so they can see all industry analysis with commentary.

**Design goals:**

- Mirrors the style of `external_benchmark_engine`'s Report 1 v4: narrative lead-ins, tables, grouped findings, MRC-ready formatting
- Renders in three formats: DOCX, HTML, Markdown (both Board and Technical variants)
- Readable by a non-technical reviewer
- Surfaces commentary alongside every table (no raw data dumps)

**Step 4.1 — Create `reports/` directory**

```
industry-analysis/
└── reports/
    ├── __init__.py
    ├── industry_analysis_report.py   # Main report builder
    └── docx_helpers.py               # Reusable DOCX formatting helpers
```

**Step 4.2 — Report structure (10 sections)**

1. **Executive Summary** — headline counts, current macro regime, 1-2 flagship findings
2. **Macro Regime** — cash rate, unemployment, regime flags with interpretation
3. **Industry Risk Rankings** — all industries ranked with risk level bands (Low/Medium/Elevated/High)
4. **Top Risk Industries** — top 5 most at-risk with commentary on why
5. **Property Market Overlays** — all property segments with cycle stage and softness score
6. **Property Cycle Interpretation** — segments in downturn, segments in growth, what it means
7. **Downturn Scenarios** — the 4-scenario multiplier table with scenario narrative
8. **Data Sources and Freshness** — what feeds each overlay, last refresh date
9. **Validation and Caveats** — what the validator says, known gaps, staleness warnings
10. **Methodology References** — pointers to `docs/methodology_*.md` files

Each section has:

- A 1-3 sentence narrative lead-in (written for non-technical audience)
- The relevant table(s)
- A short "what this means" paragraph after each major table

**Step 4.3 — Reuse DOCX helpers from the benchmark engine**

Copy the pattern established in `external_benchmark_engine/reports/docx_helpers.py`:

- Arial font, 11pt default
- US Letter, 1-inch margins
- Page numbers in footer
- Header with report name + period
- Flag boxes for alerts (orange / red)
- Styled tables with header row shading
- Narrative paragraphs above each table

**Step 4.4 — Narrative templates**

Use `_SECTION_NARRATIVES` dict pattern from the benchmark engine:

```python
_SECTION_NARRATIVES = {
    "executive_summary": (
        "This report summarises the current state of Australian industry and "
        "property market risk using public macro, industry, and property data. "
        "Overlays cover {industry_count} industries and {property_segment_count} "
        "property segments. Macro regime: {macro_regime_summary}. "
        "{headline_finding}."
    ),
    "macro_regime": (
        "The macro-regime block combines cash rate, unemployment, and growth signals "
        "into a compact regime flag that downstream credit models use for conditioning. "
        "Latest cash rate: {cash_rate_pct}%. Latest regime flags are below."
    ),
    "industry_rankings": (
        "Industries are ranked by a weighted combination of classification risk "
        "(structural attributes like cyclicality and concentration) and macro risk "
        "(current economic sensitivity). Scores range 1 (low) to 5 (high). "
        "Level bands: Low (<2), Medium (2–2.75), Elevated (2.75–3.5), High (>3.5)."
    ),
    "top_risk_industries": (
        "The following {top_n} industries carry the highest combined risk in "
        "the current environment. Review these first when calibrating portfolio "
        "concentration limits."
    ),
    "property_overlays": (
        "Property market overlays track commercial and residential property "
        "segments through the cycle. Segments in 'downturn' or 'slowing' "
        "warrant elevated caution for property-backed lending."
    ),
    "property_interpretation": (
        "{downturn_count} segments are currently in downturn; {growth_count} "
        "in growth. {cycle_commentary}."
    ),
    "downturn_scenarios": (
        "Downturn overlays provide illustrative multipliers for PD, LGD, and "
        "CCF under four scenarios (base / mild / moderate / severe). These are "
        "NOT calibrated regulatory stress parameters — they support scenario "
        "analysis and conservative pricing, not capital calculations."
    ),
    "data_sources": (
        "Each overlay is built from public data sources refreshed on a "
        "published cadence. Latest refresh: {latest_refresh}."
    ),
    "validation": (
        "Contract validation runs before every downstream handoff. "
        "Current status: {validation_status}."
    ),
    "methodology": (
        "Detailed methodology manuals are maintained in the repo docs folder. "
        "These describe how each overlay is constructed from raw inputs."
    ),
}
```

**Step 4.5 — CLI integration**

Add a report command to the existing scripts:

```powershell
python scripts/build_board_report.py --format docx --output outputs/reports/Industry_Analysis_Q1_2026.docx
python scripts/build_board_report.py --format html --output outputs/reports/Industry_Analysis_Q1_2026.html
python scripts/build_board_report.py --format markdown --output outputs/reports/Industry_Analysis_Q1_2026.md
```

Markdown format emits two files per the benchmark engine pattern:
- `Industry_Analysis_Q1_2026_Board.md` (summary for non-technical readers)
- `Industry_Analysis_Q1_2026_Technical.md` (full detail for MRC/audit)

**Step 4.6 — Verification**

Open the DOCX in Word and check:
- All 10 sections present
- Each section has narrative text before its tables
- Tables render correctly
- No raw Python object dumps or malformed formatting
- Page numbers in footer
- Header shows "Industry Analysis Report | Q1 2026"

---

### Phase 5 — Run the full pipeline end-to-end

**Step 5.1 — Full refresh**

```powershell
python scripts/download_public_data.py
python scripts/build_public_panels.py
python scripts/build_overlays.py
python scripts/export_contracts.py
python scripts/validate_upstream.py
pytest -v
python scripts/build_board_report.py --format docx --output outputs/reports/Industry_Analysis_Q1_2026.docx
python scripts/build_board_report.py --format html --output outputs/reports/Industry_Analysis_Q1_2026.html
python scripts/build_board_report.py --format markdown --output outputs/reports/Industry_Analysis_Q1_2026.md
```

**Step 5.2 — Verify all outputs exist**

```powershell
dir outputs\reports\Industry_Analysis_Q1_2026*
```

Expected:
- `Industry_Analysis_Q1_2026.docx`
- `Industry_Analysis_Q1_2026.html`
- `Industry_Analysis_Q1_2026_Board.md`
- `Industry_Analysis_Q1_2026_Technical.md`

All non-empty, all >= 10 KB.

---

### Phase 6 — Audit log and handoff

Create `outputs/industry_analysis_audit_log.md` capturing:

```markdown
# Industry Analysis Project — Audit and Polish Log

**Date:** [today]
**Scope:** Baseline audit, data quality scan, test coverage review, board report build

## Baseline findings

- Tests: X passing, Y failing, Z skipped
- Pipeline scripts: [which complete cleanly, which emit warnings]
- Validator output: [summary]
- Exports status: [X/6 populated, schema as expected]

## Anomaly scan findings

- HIGH severity: [count, list]
- MEDIUM severity: [count, list]
- LOW severity: [count, list]

## Fixes applied

[For each fix:]
- What was broken
- Root cause
- Fix applied
- Test added to prevent regression

## Test coverage

- Before: X tests across Y source modules
- After: X+N tests with N new coverage tests for overlay builders and exports
- Untested modules remaining: [list with explanation]

## Board report

- Generated in 4 formats (docx, html, board.md, technical.md)
- 10 sections with narrative + tables
- Location: outputs/reports/Industry_Analysis_Q1_2026.*

## Known gaps (not fixed this session)

- [Gap 1]: why not fixed, follow-up effort estimate
- [Gap 2]: ...

## Next session candidates

- Wire industry-analysis parquet exports into external_benchmark_engine 
  to enable Report 2 (Environment overlay)
- [other]

## Success criteria

- [ ] Baseline captured
- [ ] Anomaly scan run
- [ ] HIGH findings resolved at root cause (or escalated)
- [ ] Test coverage extended to overlay builders
- [ ] Board report generated in 4 formats
- [ ] Audit log written
```

---

## Stop gates

Stop and ask the user before:

1. **Baseline shows unexpected broken state** — if tests fail or scripts error on a fresh run, report the state and ask whether to fix before polishing
2. **Anomaly scan finds HIGH severity issues** — show the findings; do not auto-fix
3. **A source module has zero tests and unclear semantics** — don't guess at what to test; ask for clarification
4. **Any of the 4 final report files fail to generate or are empty**

## What NOT to do

- **Don't add new overlays.** This session is an audit + report; not a feature build
- **Don't add new data sources.** Work with what's in `data/raw/`
- **Don't rewrite existing overlay logic.** If it produces healthy output, leave it alone
- **Don't change the canonical parquet contract.** Downstream repos depend on the schema
- **Don't hide anomalies behind filters.** Root-cause or escalate
- **Don't skip the baseline capture.** That's what makes regressions visible
- **Don't commit the board report PDFs if LibreOffice isn't available** — follow the same Option D approach from the benchmark engine session if PDF generation blocks

## Success summary for the user after completion

```
Industry-analysis project audit and polish complete.

Baseline:
  - Tests: X/Y passing
  - Pipeline: all N scripts run cleanly
  - Exports: 6/6 present, schemas verified

Anomaly scan: N findings
  - HIGH: [count] — [resolved/escalated]
  - MEDIUM: [count] — [resolved/noted]
  - LOW: [count] — noted in audit log

Test coverage:
  - Before: X tests
  - After: X+N tests (contract tests for all 4 core exports)

Board report generated:
  - outputs/reports/Industry_Analysis_Q1_2026.docx  (N KB — MRC-ready)
  - outputs/reports/Industry_Analysis_Q1_2026.html  (N KB — browser)
  - outputs/reports/Industry_Analysis_Q1_2026_Board.md       (summary)
  - outputs/reports/Industry_Analysis_Q1_2026_Technical.md   (full detail)

Audit log: outputs/industry_analysis_audit_log.md

Next session candidate: wire industry-analysis parquet exports into
external_benchmark_engine to enable Report 2.
```
