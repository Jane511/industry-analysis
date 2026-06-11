"""ASIC insolvency public-data loader and fetcher.

ASIC publishes Series 1A ("Companies entering external administration by
industry") weekly, two weeks in arrears. Coverage starts July 2013. The
workbook is distributed at:

    https://asic.gov.au/regulatory-resources/find-a-document/statistics/insolvency-statistics/

Expected filename pattern for real data:
    asic-insolvency-statistics-series-1a-published-*.xlsx

Loader contract:

* ``load_optional_asic_insolvency_extract()`` returns a DataFrame with the
  columns ``[as_of_month, anzsic_division_code, industry, insolvency_count,
  source_note]``. When no real source file is staged, the loader raises a
  clear ``RuntimeError`` so production runs fail visibly.
* The committed synthetic stub file
  (``SYNTHETIC_DEVELOPMENT_STUB_asic_series_1a.csv``) is **never loaded by
  default**. Set the environment variable ``ASIC_USE_STUB=1`` to opt into
  the stub — this is for local development and CI only and prints a clear
  stderr warning every time it runs. Production schedulers must not set
  this variable.
* ``download_asic_series_1a(dest_dir)`` attempts a live fetch from the
  ASIC statistics page. When network access is not available, it raises a
  clear ``RuntimeError`` that names the expected URL and the fallback
  staging directory so operators know exactly what to do.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import pandas as pd

from src.config import RAW_MANUAL_DIR, RAW_PUBLIC_DIR
from src.utils import normalise_text


ASIC_INSOLVENCY_PAGE_URL = (
    "https://asic.gov.au/regulatory-resources/find-a-document/statistics/insolvency-statistics/"
)

RAW_PUBLIC_DIR_ASIC = RAW_PUBLIC_DIR / "asic"

# Real-data filename patterns. These must NEVER match the synthetic stub —
# the stub's filename is prefixed with ``SYNTHETIC_DEVELOPMENT_STUB_`` so it
# is impossible to pick up by accident via these globs.
SERIES_1A_FILENAME_PATTERNS: tuple[str, ...] = (
    "asic-insolvency-statistics-series-1a-published-*.xlsx",
    "asic-insolvency-statistics-series-1a-published-*.csv",
    "asic-insolvency-statistics-series-1a-*.xlsx",
    "asic-insolvency-statistics-series-1a-*.csv",
)

OPTIONAL_ASIC_INSOLVENCY_FILES = (
    "asic_insolvency_series_1a.csv",
    "asic_insolvency_series_1a.xlsx",
    "asic_insolvency_extract.csv",
    "asic_insolvency_extract.xlsx",
)

# Opt-in environment variable. When set to "1", the loader reads the
# committed synthetic stub file instead of failing. Intended for local
# development, CI, and test runs.
ASIC_STUB_ENV_VAR = "ASIC_USE_STUB"

STUB_FILENAME = "SYNTHETIC_DEVELOPMENT_STUB_asic_series_1a.csv"


def _stub_is_enabled() -> bool:
    return os.environ.get(ASIC_STUB_ENV_VAR, "0") == "1"


def _resolve_stub_file() -> Path | None:
    for directory in (RAW_PUBLIC_DIR_ASIC, RAW_PUBLIC_DIR, RAW_MANUAL_DIR):
        if not directory.exists():
            continue
        candidate = directory / STUB_FILENAME
        if candidate.exists():
            return candidate
    return None


SERIES_1A_SCHEMA = ("as_of_month", "anzsic_division_code", "industry", "insolvency_count", "source_note")


# Canonical ANZSIC division names and their single-letter codes. K (Financial
# and Insurance Services) is out of scope for this overlay but we still
# accept rows labelled "K" or "Financial..." from the source file — they are
# simply dropped downstream by the panel build.
ANZSIC_DIVISION_NAME_TO_CODE: dict[str, str] = {
    "agriculture forestry and fishing": "A",
    "mining": "B",
    "manufacturing": "C",
    "electricity gas water and waste services": "D",
    "construction": "E",
    "wholesale trade": "F",
    "retail trade": "G",
    "accommodation and food services": "H",
    "transport postal and warehousing": "I",
    "information media and telecommunications": "J",
    "financial and insurance services": "K",
    "rental hiring and real estate services": "L",
    "professional scientific and technical services": "M",
    "administrative and support services": "N",
    "public administration and safety": "O",
    "education and training": "P",
    "health care and social assistance": "Q",
    "arts and recreation services": "R",
    "other services": "S",
}


def _canonical_division_code(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    raw = str(value).strip()
    if not raw:
        return None
    if len(raw) == 1 and raw.upper() in ANZSIC_DIVISION_NAME_TO_CODE.values():
        return raw.upper()
    key = normalise_text(raw)
    # ABS publishes three divisions with a trailing "(private)" modifier.
    if key.endswith(" private"):
        key = key[: -len(" private")].strip()
    if key in ANZSIC_DIVISION_NAME_TO_CODE:
        return ANZSIC_DIVISION_NAME_TO_CODE[key]
    return None


def _canonical_division_name(code: str) -> str:
    for name, letter in ANZSIC_DIVISION_NAME_TO_CODE.items():
        if letter == code:
            return name.title()
    return code


def _resolve_existing_file(search_dirs: tuple[Path, ...]) -> Path | None:
    for directory in search_dirs:
        if not directory.exists():
            continue
        for pattern in SERIES_1A_FILENAME_PATTERNS:
            matches = sorted(directory.glob(pattern))
            if matches:
                return matches[-1]
        for candidate in OPTIONAL_ASIC_INSOLVENCY_FILES:
            candidate_path = directory / candidate
            if candidate_path.exists():
                return candidate_path
    return None


def _empty_series_1a() -> pd.DataFrame:
    return pd.DataFrame({column: pd.Series(dtype="object") for column in SERIES_1A_SCHEMA})


def _read_series_1a_file(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    # Tolerate several column-name conventions as ASIC has reshuffled the
    # workbook headers across releases.
    rename_map = {}
    for candidate in df.columns:
        lower = str(candidate).strip().lower()
        if lower in {"month", "period", "as_of_month", "reporting_month"}:
            rename_map[candidate] = "as_of_month"
        elif lower in {"division", "anzsic_division", "anzsic division", "industry_division"}:
            rename_map[candidate] = "industry"
        elif lower in {"anzsic_division_code", "division_code"}:
            rename_map[candidate] = "anzsic_division_code"
        elif lower in {"external_administrations", "insolvency_count", "count", "companies_entering_external_administration"}:
            rename_map[candidate] = "insolvency_count"
    df = df.rename(columns=rename_map)

    if "anzsic_division_code" not in df.columns and "industry" in df.columns:
        df["anzsic_division_code"] = df["industry"].apply(_canonical_division_code)

    if "industry" not in df.columns and "anzsic_division_code" in df.columns:
        df["industry"] = df["anzsic_division_code"].apply(_canonical_division_name)

    required = {"as_of_month", "anzsic_division_code", "insolvency_count"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(
            f"{path.name} is missing required columns: {sorted(missing)}"
        )

    df["as_of_month"] = pd.to_datetime(df["as_of_month"], errors="coerce").dt.to_period("M").astype(str)
    df["insolvency_count"] = pd.to_numeric(df["insolvency_count"], errors="coerce")
    df["anzsic_division_code"] = df["anzsic_division_code"].apply(_canonical_division_code)
    df["industry"] = df.get("industry", df["anzsic_division_code"].apply(_canonical_division_name))
    df["industry"] = df["industry"].astype(str)
    df["source_note"] = df.get(
        "source_note",
        f"ASIC Series 1A external-administration workbook ({path.name})",
    )

    df = df.dropna(subset=["as_of_month", "anzsic_division_code", "insolvency_count"])
    return df[list(SERIES_1A_SCHEMA)].reset_index(drop=True)


def load_optional_asic_insolvency_extract() -> pd.DataFrame:
    """Load the staged ASIC Series 1A workbook.

    Resolution order:

    1. A real ASIC Series 1A workbook staged under ``data/raw/public/asic/``,
       ``data/raw/public/``, or ``data/raw/manual/`` and matching
       ``SERIES_1A_FILENAME_PATTERNS`` / ``OPTIONAL_ASIC_INSOLVENCY_FILES``.
       If found, this is loaded and returned.
    2. If no real file is found and ``ASIC_USE_STUB=1`` is in the
       environment, the committed synthetic development stub is loaded and
       a clear warning is printed to stderr.
    3. Otherwise a ``RuntimeError`` is raised that names the expected
       staging directory, the expected filename pattern, the opt-in env
       var, and the ASIC URL to fetch from. Production runs fail here.

    Returns the canonical Series 1A frame with the schema
    ``[as_of_month, anzsic_division_code, industry, insolvency_count,
    source_note]``.
    """
    real_path = _resolve_existing_file((RAW_PUBLIC_DIR_ASIC, RAW_PUBLIC_DIR, RAW_MANUAL_DIR))
    if real_path is not None:
        return _read_series_1a_file(real_path)

    if _stub_is_enabled():
        stub_path = _resolve_stub_file()
        if stub_path is not None:
            print(
                "[WARNING] ASIC_USE_STUB=1 — reading the committed synthetic "
                f"development stub ({stub_path.name}). Production runs must "
                "stage a real ASIC Series 1A workbook and unset ASIC_USE_STUB.",
                file=sys.stderr,
                flush=True,
            )
            frame = _read_series_1a_file(stub_path)
            if not frame.empty:
                marker = "SYNTHETIC DEVELOPMENT STUB"
                frame["source_note"] = frame["source_note"].astype(str).apply(
                    lambda note: note if marker in note else f"{marker} — {note}"
                )
            return frame
        raise RuntimeError(
            f"ASIC_USE_STUB=1 was set but the stub file was not found. "
            f"Expected {STUB_FILENAME} under {RAW_PUBLIC_DIR_ASIC}."
        )

    raise RuntimeError(
        "ASIC Series 1A workbook not found in "
        f"{RAW_PUBLIC_DIR_ASIC} (expected filename pattern "
        "'asic-insolvency-statistics-series-1a-published-*.xlsx'). "
        "Either (a) run `src.public_data.download_asic_insolvency."
        "download_asic_series_1a` to fetch it, "
        "(b) stage a real workbook manually under "
        f"{RAW_PUBLIC_DIR_ASIC}, or "
        "(c) for development / CI only, set ASIC_USE_STUB=1 to load the "
        f"committed synthetic stub ({STUB_FILENAME}). "
        f"ASIC page: {ASIC_INSOLVENCY_PAGE_URL}"
    )


def load_empty_series_1a_frame() -> pd.DataFrame:
    """Return an empty canonical Series 1A frame (for tests)."""
    return _empty_series_1a()


def download_asic_series_1a(dest_dir: Path) -> Path:
    """Fetch the ASIC Series 1A workbook into ``dest_dir`` and return the path.

    When network access is not available (or when the remote fetch fails
    for any reason) this raises a ``RuntimeError`` that names (a) the
    expected URL and (b) the fallback staging directory. Operators can
    then stage the file manually at ``data/raw/public/asic/`` and reruns
    will pick it up via ``load_optional_asic_insolvency_extract``.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / "asic-insolvency-statistics-series-1a-published-latest.xlsx"

    request = Request(ASIC_INSOLVENCY_PAGE_URL, headers={"User-Agent": "industry-analysis/1.0"})
    try:
        with urlopen(request, timeout=30) as response:  # noqa: S310 — trusted public URL
            body = response.read()
    except (URLError, OSError) as exc:
        raise RuntimeError(
            "Unable to fetch ASIC Series 1A workbook from "
            f"{ASIC_INSOLVENCY_PAGE_URL}. Stage the file manually under "
            f"{dest_dir} (matching pattern "
            "'asic-insolvency-statistics-series-1a-published-*.xlsx'). "
            f"Underlying error: {exc}"
        ) from exc

    # ASIC's URL is an HTML landing page; we leave the downloaded payload
    # on disk so operators can see what was retrieved and, if necessary,
    # extract the workbook link by hand.
    target.write_bytes(body)
    return target
