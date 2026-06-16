#!/usr/bin/env python
"""One-command, fully-reproducible pipeline for the industry-analysis engine.

Runs the whole flow end to end on **real public data only** (ABS / RBA / PTRS):

    fetch (live download, with committed-cache fallback)
      -> build panels + overlays + export the 8 CSV contracts
      -> validate the contracts
      -> render the Board + Technical report (markdown / html / docx)

A reviewer only needs:

    python -m venv .venv
    .venv\\Scripts\\activate            # Windows;  source .venv/bin/activate on macOS/Linux
    pip install -r requirements.txt
    python run_pipeline.py

Outputs land in ``outputs/`` (contracts in ``outputs/contracts/``, reports in
``outputs/reports/``). No synthetic or proprietary data is used.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.public_data.fetch_public_data import DATA_AS_OF, fetch_all
from src.overlays.export_contracts import export_contracts
from src.overlays.macro_stress_core import build_and_export_macro_stress
from src.validate_upstream import validate_upstream
from src.reporting.industry_analysis_report import build_report
from src.reporting.render_docx import write_docx_variants
from src.reporting.render_html import write_html_variants
from src.reporting.render_markdown import write_markdown_variants

REPORT_STEM = "outputs/reports/Industry_Analysis_Q1_2026"


def _banner(text: str) -> None:
    print("\n" + "=" * 68)
    print(text)
    print("=" * 68)


def main() -> int:
    _banner(f"Industry-analysis reproducible pipeline  |  data vintage {DATA_AS_OF}")
    print("Real public data only (ABS / RBA / PTRS); committed cache fallback.\n")

    print("[1/4] Fetching real public data (live download -> cache fallback)")
    print("-" * 68)
    try:
        fetch_all()
    except Exception as exc:  # FetchError or unexpected — surface clearly, do not crash silently
        print(f"\nFATAL: could not resolve a required data source.\n  {exc}", file=sys.stderr)
        return 2

    print("\n[2/4] Building panels, overlays, and the 8 CSV contracts")
    print("-" * 68)
    outputs = export_contracts()
    print(f"Wrote {len(outputs)} contracts to outputs/contracts/.")

    macro = build_and_export_macro_stress()
    print(
        "Wrote macro-stress contracts (macro_scenario_paths, "
        "portfolio_macro_sensitivity) + demo roll-up to outputs/."
    )

    print("\n[3/4] Validating contracts")
    print("-" * 68)
    if validate_upstream():
        print("Validation PASSED — all required contracts present and non-empty.")
    else:
        print("WARNING: upstream validation reported issues (see above).", file=sys.stderr)

    print("\n[4/4] Rendering the report (markdown / html / docx)")
    print("-" * 68)
    report = build_report()
    for writer in (write_markdown_variants, write_docx_variants, write_html_variants):
        for variant, path in writer(report, REPORT_STEM).items():
            size_kb = Path(path).stat().st_size / 1024
            print(f"  wrote {variant:<10} -> {path} ({size_kb:.1f} KB)")

    _banner("Done. Open outputs/reports/Industry_Analysis_Q1_2026.md (or .docx / .html).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
