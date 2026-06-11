"""Download direct public-source files declared in ``src.config``.

Landing pages are intentionally skipped here because they need source-specific
scrapers. Successful direct downloads are recorded in
``data/raw/public/_manifest.json`` so downstream reports can show source
lineage even when no structured parquet export is produced for a file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlretrieve

from src.config import (
    PUBLIC_SOURCE_URLS,
    RAW_PUBLIC_DIR,
    RAW_PUBLIC_DIR_ABS,
    RAW_PUBLIC_DIR_PTRS,
    RAW_PUBLIC_DIR_RBA,
    REPO_ROOT,
)


DIRECT_DOWNLOAD_EXTENSIONS = {".xlsx", ".xls", ".csv", ".pdf"}
MANIFEST_PATH = RAW_PUBLIC_DIR / "_manifest.json"

ABS_KEY_PREFIXES = (
    "cpi_",
    "ppi_",
    "lending_",
    "dwelling_",
    "property_price_",
    "total_value_",
    "business_indicators_",
    "labour_force_",
    "building_",
    "australian_industry_",
    "anzsic_",
)


def is_direct_download_url(url: str) -> bool:
    """Return True when ``url`` points directly at a supported file type."""
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix in DIRECT_DOWNLOAD_EXTENSIONS


def filename_from_url(url: str) -> str:
    name = Path(urlparse(url).path).name
    if not name:
        raise ValueError(f"Could not derive filename from URL: {url}")
    return name


def destination_dir_for_key(key: str) -> Path:
    """Route a source key to its per-source raw-public directory."""
    if key.startswith("rba_"):
        return RAW_PUBLIC_DIR_RBA
    if key.startswith("ptrs_"):
        return RAW_PUBLIC_DIR_PTRS
    if key.startswith(ABS_KEY_PREFIXES) or "abs" in key:
        return RAW_PUBLIC_DIR_ABS
    return RAW_PUBLIC_DIR


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_mtime(headers: Any) -> int | None:
    if headers is None:
        return None
    last_modified = headers.get("Last-Modified") if hasattr(headers, "get") else None
    if not last_modified:
        return None
    try:
        parsed = parsedate_to_datetime(last_modified)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp())


def _relative_to_repo(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Manifest must contain a JSON object: {path}")
    return data


def write_manifest_entry(
    key: str,
    url: str,
    local_path: Path,
    headers: Any = None,
    manifest_path: Path | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if manifest_path is None:
        manifest_path = MANIFEST_PATH
    manifest = load_manifest(manifest_path)
    entry = {
        "url": url,
        "local_path": _relative_to_repo(local_path),
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_mtime": _source_mtime(headers),
        "sha256": _sha256(local_path),
        "size_bytes": local_path.stat().st_size,
    }
    if extra:
        entry.update(extra)
    manifest[key] = entry
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return entry


def _empty_summary() -> dict[str, list[dict[str, str]]]:
    return {
        "downloaded": [],
        "cached": [],
        "skipped_landing_pages": [],
        "failed": [],
    }


def _append(summary: dict[str, list[dict[str, str]]], bucket: str, key: str, url: str, path: Path | None = None) -> None:
    row = {"key": key, "url": url}
    if path is not None:
        row["path"] = str(path)
    summary[bucket].append(row)


def _print_summary(summary: dict[str, list[dict[str, str]]]) -> None:
    print("Public data download summary")
    for bucket in ("downloaded", "cached", "skipped_landing_pages", "failed"):
        print(f"  {bucket}: {len(summary[bucket])}")


def _rebuild_panels_and_overlays() -> None:
    commands = [
        [sys.executable, str(REPO_ROOT / "scripts" / "build_public_panels.py")],
        [sys.executable, str(REPO_ROOT / "scripts" / "build_overlays.py")],
    ]
    for command in commands:
        subprocess.run(command, cwd=REPO_ROOT, check=True)


def download_all_public(force_refresh: bool = False, rebuild_panels: bool = False) -> dict[str, list[dict[str, str]]]:
    """Download every direct file URL in ``PUBLIC_SOURCE_URLS``.

    URLs that look like landing pages are skipped and reported. Network or
    filesystem failures are collected in the returned summary instead of
    stopping the whole run.
    """
    summary = _empty_summary()

    for key, url in PUBLIC_SOURCE_URLS.items():
        if not is_direct_download_url(url):
            print(f"Skipping landing page {key}: {url}")
            _append(summary, "skipped_landing_pages", key, url)
            continue

        dest_dir = destination_dir_for_key(key)
        dest_dir.mkdir(parents=True, exist_ok=True)
        destination = dest_dir / filename_from_url(url)

        if destination.exists() and not force_refresh:
            print(f"cached {key} -> {destination}")
            _append(summary, "cached", key, url, destination)
            continue

        print(f"Downloading {key} -> {destination}")
        try:
            _, headers = urlretrieve(url, destination)
            write_manifest_entry(key, url, destination, headers)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            print(f"FAILED {key}: {url} ({exc})", file=sys.stderr)
            _append(summary, "failed", key, url, destination)
            continue

        _append(summary, "downloaded", key, url, destination)

    _print_summary(summary)

    if rebuild_panels and summary["downloaded"] and not summary["failed"]:
        _rebuild_panels_and_overlays()
    elif summary["downloaded"]:
        print(
            "Next step: run `python src/build_public_panels.py` then "
            "`python src/build_overlays.py` to propagate refreshed inputs.",
            file=sys.stderr,
        )

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Download direct public-data source files.")
    parser.add_argument("--force", action="store_true", help="Re-download files even when cached.")
    parser.add_argument(
        "--rebuild-panels",
        action="store_true",
        help="Run build_public_panels.py and build_overlays.py after successful downloads.",
    )
    args = parser.parse_args()
    download_all_public(force_refresh=args.force, rebuild_panels=args.rebuild_panels)


if __name__ == "__main__":
    main()
