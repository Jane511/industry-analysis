"""Fetch real public data (ABS / RBA / PTRS) with a committed-cache fallback.

The pipeline runs on real public data only. For each source this module tries a
live download first (from a pinned URL); if the source is unreachable it falls
back to the committed real-data snapshot under ``data/cache/`` so the reports
are fully reproducible even offline. Every download handles network errors
gracefully — it never crashes silently.

Required sources (the ABS industry/building workbooks + the RBA cash rate) always
resolve to either a live file or the cache. PTRS PDFs are best-effort only (not
required to build the reports, and not cached).
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import requests

from src.config import (
    PUBLIC_SOURCE_URLS,
    RAW_PUBLIC_DIR,
    RAW_PUBLIC_DIR_ABS,
    RAW_PUBLIC_DIR_PTRS,
    REPO_ROOT,
)

# Vintage of the committed real-data cache. Pin this so the report is
# reproducible and clearly dated regardless of when a reviewer runs it.
DATA_AS_OF = "2026-02-28"

CACHE_DIR = REPO_ROOT / "data" / "cache"

_USER_AGENT = (
    "industry-analysis-reference-layer/1.0 (public-data fetch; "
    "https://github.com/Jane511/industry-analysis)"
)
_MIN_BYTES = 1024  # treat a tiny response as a failed/blocked download


@dataclass(frozen=True)
class SourceSpec:
    key: str  # key into PUBLIC_SOURCE_URLS for the live URL
    label: str  # human-readable label for status output
    dest_dir: Path  # where the pipeline expects the file (matches staged-file glob)
    dest_filename: str  # canonical filename (the staged-file glob matches this)
    cache_relpath: str | None  # path under data/cache/, or None for best-effort only
    required: bool  # if True, a miss aborts the pipeline


# Required real sources for the 8 surviving contracts — each is cache-backed.
REQUIRED_SOURCES: tuple[SourceSpec, ...] = (
    SourceSpec("australian_industry_xlsx", "ABS 8155.0 Australian Industry",
               RAW_PUBLIC_DIR_ABS, "81550DO001_202324.xlsx", "abs/81550DO001_202324.xlsx", True),
    SourceSpec("business_indicators_profit_ratio_xlsx", "ABS 5676.0 Business Indicators (profit)",
               RAW_PUBLIC_DIR_ABS, "56760022_dec2025_profit_ratio.xlsx", "abs/56760022_dec2025_profit_ratio.xlsx", True),
    SourceSpec("business_indicators_inventory_ratio_xlsx", "ABS 5676.0 Business Indicators (inventories)",
               RAW_PUBLIC_DIR_ABS, "56760023_dec2025_inventory_ratio.xlsx", "abs/56760023_dec2025_inventory_ratio.xlsx", True),
    SourceSpec("labour_force_industry_xlsx", "ABS 6291.0 Labour Force, Detailed",
               RAW_PUBLIC_DIR_ABS, "6291004_feb2026_labour_force_industry.xlsx", "abs/6291004_feb2026_labour_force_industry.xlsx", True),
    SourceSpec("building_approvals_nonres_xlsx", "ABS 8731.0 Building Approvals (non-residential)",
               RAW_PUBLIC_DIR_ABS, "87310051_feb2026_building_approvals_nonres.xlsx", "abs/87310051_feb2026_building_approvals_nonres.xlsx", True),
    SourceSpec("rba_cash_rate_csv", "RBA F1 cash-rate table",
               RAW_PUBLIC_DIR, "rba_f1_data.csv", "rba/rba_f1_data.csv", True),
)

# Best-effort sources: downloaded live when reachable, not required, not cached.
OPTIONAL_SOURCES: tuple[SourceSpec, ...] = (
    SourceSpec("ptrs_cycle_8_pdf", "PTRS regulator update (Jul 2025)",
               RAW_PUBLIC_DIR_PTRS, "reg-update-july-2025.pdf", None, False),
    SourceSpec("ptrs_cycle_9_pdf", "PTRS regulators update (Jan 2026)",
               RAW_PUBLIC_DIR_PTRS, "regulators-update-202601.pdf", None, False),
    SourceSpec("ptrs_guidance", "PTRS guidance materials (Mar 2025)",
               RAW_PUBLIC_DIR_PTRS, "ptrs-guidance-materials-march2025.pdf", None, False),
)


class FetchError(RuntimeError):
    """Raised when a required source resolves to neither live download nor cache."""


def _download(url: str, dest: Path, timeout: int = 60) -> None:
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": _USER_AGENT})
    resp.raise_for_status()
    if len(resp.content) < _MIN_BYTES:
        raise ValueError(f"response too small ({len(resp.content)} bytes) — likely blocked")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(resp.content)


def _copy_from_cache(spec: SourceSpec, dest: Path) -> bool:
    if not spec.cache_relpath:
        return False
    cache_file = CACHE_DIR / spec.cache_relpath
    if not cache_file.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cache_file, dest)
    return True


def fetch_source(spec: SourceSpec, *, prefer_cache: bool = False) -> tuple[str, str]:
    """Resolve one source to a file on disk. Returns ``(status, detail)``.

    ``status`` is one of ``live`` / ``cache`` / ``skipped``. Raises
    :class:`FetchError` only when a *required* source cannot be resolved at all.
    """
    dest = spec.dest_dir / spec.dest_filename
    url = PUBLIC_SOURCE_URLS.get(spec.key)

    if prefer_cache and _copy_from_cache(spec, dest):
        return ("cache", "used committed cache (prefer_cache)")

    live_error = "no live URL configured"
    if url:
        try:
            _download(url, dest)
            return ("live", url)
        except Exception as exc:  # noqa: BLE001 — any network/parse error degrades to cache
            live_error = f"{type(exc).__name__}: {exc}"

    if _copy_from_cache(spec, dest):
        return ("cache", f"live download failed ({live_error}); used committed cache")

    if spec.required:
        raise FetchError(
            f"Required source '{spec.key}' could not be downloaded and is not in the cache "
            f"({live_error})."
        )
    return ("skipped", f"live download failed ({live_error}); no cache (optional source)")


def fetch_all(*, prefer_cache: bool = False, include_optional: bool = True) -> dict[str, dict[str, str]]:
    """Fetch every source. Prints a per-source status line; returns the status map."""
    specs = list(REQUIRED_SOURCES) + (list(OPTIONAL_SOURCES) if include_optional else [])
    results: dict[str, dict[str, str]] = {}
    icon = {"live": "  live ", "cache": " cache ", "skipped": " skip  "}
    for spec in specs:
        status, detail = fetch_source(spec, prefer_cache=prefer_cache)
        results[spec.key] = {"status": status, "detail": detail, "label": spec.label}
        print(f"[{icon.get(status, status)}] {spec.label}")
        if status != "live":
            print(f"            -> {detail}")
    n_live = sum(1 for r in results.values() if r["status"] == "live")
    n_cache = sum(1 for r in results.values() if r["status"] == "cache")
    print(f"\nData sources: {n_live} live, {n_cache} from cache, "
          f"{len(results) - n_live - n_cache} skipped (vintage {DATA_AS_OF}).")
    return results


def main() -> None:
    fetch_all()


if __name__ == "__main__":
    import sys

    _root = Path(__file__).resolve().parents[2]
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    main()
