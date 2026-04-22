"""CLI entry point for the industry-analysis board report.

Supports four output formats: `markdown`, `docx`, `html`, and `all`.
`all` emits the full six-file set (Board + Technical, in each of the three
per-file formats) from a single --output stem.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reports.industry_analysis_report import build_report
from reports.render_docx import write_docx_variants
from reports.render_html import write_html_variants
from reports.render_markdown import write_markdown_variants


FORMATS = {"markdown", "docx", "html", "all"}


def _emit(fmt: str, report, output: str) -> dict[str, dict[str, str]]:
    writers = {
        "markdown": write_markdown_variants,
        "docx": write_docx_variants,
        "html": write_html_variants,
    }
    if fmt == "all":
        return {name: writer(report, output) for name, writer in writers.items()}
    return {fmt: writers[fmt](report, output)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the industry-analysis board report.")
    parser.add_argument(
        "--format",
        required=True,
        choices=sorted(FORMATS),
        help="Output format. 'all' emits markdown + docx + html (six files total).",
    )
    parser.add_argument(
        "--output",
        required=True,
        help=(
            "Output path stem. Each format writes two files using this stem: "
            "<stem>_Board.<ext> and <stem>_Technical.<ext>."
        ),
    )
    args = parser.parse_args()

    report = build_report()
    emitted = _emit(args.format, report, args.output)

    for fmt_name, variant_map in emitted.items():
        for variant, path in variant_map.items():
            size_kb = Path(path).stat().st_size / 1024
            print(f"Wrote {fmt_name:<8} {variant:<10} -> {path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
