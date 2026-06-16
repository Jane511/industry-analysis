"""Fetch the economy-wide macro **headline levels** from real ABS releases.

The macro-stress panel's base levels live in ``config/macro_scenarios.yaml``.
For most of the panel those are stated readings; this module turns the four
that have a clean public time series — **GDP growth, unemployment, CPI, WPI** —
into live values parsed from the relevant ABS workbook, mirroring how
``download_rba_rates`` already supplies the live cash rate.

Each indicator resolves to a single latest headline figure parsed from the
``Data1`` sheet of the ABS time-series workbook, with a plausibility bound. On
any failure (network, format change, out-of-bound value) the indicator is
omitted so the caller falls back to the committed config base level — the same
offline-safe contract as the rest of the pipeline.

Not auto-fetched here (no clean current free public series; kept as stated /
assumption in config, see README §1):
  * house-price growth — the ABS RPPI (Cat. 6416.0) was **discontinued after
    the Dec-2021 quarter**; no current free public price index exists.
  * exchange rate (TWI) and the all-industry output proxy.
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import requests

from src.config import RAW_PUBLIC_DIR_ABS, REPO_ROOT

_UA = (
    "industry-analysis-reference-layer/1.0 (public-data fetch; "
    "https://github.com/Jane511/industry-analysis)"
)
_CACHE_ABS = REPO_ROOT / "data" / "cache" / "abs"
_TIMEOUT = 120


# ---------------------------------------------------------------------------
# ABS Data1 time-series helpers
# ---------------------------------------------------------------------------

def _data1(content: bytes) -> pd.DataFrame:
    return pd.read_excel(io.BytesIO(content), sheet_name="Data1", header=None)


def _pick_series(df: pd.DataFrame, predicate: Callable[[str, str], bool]) -> Optional[pd.DataFrame]:
    """First column whose (title row 0, series-type row 2) match; NA dropped."""
    dates = pd.to_datetime(df.iloc[9:, 0], format="mixed", errors="coerce")
    for j in range(1, df.shape[1]):
        title, stype = str(df.iloc[0, j]), str(df.iloc[2, j])
        if predicate(title, stype):
            values = pd.to_numeric(df.iloc[9:, j], errors="coerce")
            out = pd.DataFrame({"date": dates, "value": values}).dropna()
            if len(out):
                return out
    return None


def _latest_level(df: pd.DataFrame, predicate) -> float:
    series = _pick_series(df, predicate)
    if series is None:
        raise ValueError("no matching series")
    return float(series["value"].iloc[-1])


def _latest_yoy(df: pd.DataFrame, predicate) -> float:
    series = _pick_series(df, predicate)
    if series is None or len(series) < 5:
        raise ValueError("series missing or too short for YoY")
    latest, year_ago = float(series["value"].iloc[-1]), float(series["value"].iloc[-5])
    if not year_ago:
        raise ValueError("zero base for YoY")
    return (latest / year_ago - 1) * 100


# ---------------------------------------------------------------------------
# Per-indicator extraction (each reproduces a validated headline figure)
# ---------------------------------------------------------------------------

def _gdp_yoy(df: pd.DataFrame) -> float:
    # Real GDP, seasonally adjusted chain-volume LEVEL -> through-the-year change.
    return _latest_yoy(df, lambda t, s: (
        "gross domestic product: chain volume measures ;" in t.lower()
        and "percentage" not in t.lower()
        and "seasonally adjusted" in s.lower()
    ))


def _unemployment_level(df: pd.DataFrame) -> float:
    return _latest_level(df, lambda t, s: (
        t.strip().lower().startswith("unemployment rate ;")
        and "persons" in t.lower()
        and "seasonally adjusted" in s.lower()
    ))


def _cpi_yoy(df: pd.DataFrame) -> float:
    return _latest_yoy(df, lambda t, s: (
        "index numbers" in t.lower()
        and "all groups cpi" in t.lower()
        and "australia" in t.lower()
    ))


def _wpi_yoy(df: pd.DataFrame) -> float:
    # Headline WPI: total hourly rates excl bonuses, all sectors, all industries,
    # seasonally adjusted, percentage change from corresponding quarter prior year.
    return _latest_level(df, lambda t, s: (
        "corresponding quarter of previous year" in t.lower()
        and "total hourly rates of pay excluding bonuses" in t.lower()
        and "all industries" in t.lower()
        and "private and public" in t.lower()
        and "seasonally adjusted" in s.lower()
    ))


@dataclass(frozen=True)
class MacroIndicator:
    key: str                 # macro variable key in macro_scenarios.yaml
    url: str                 # live ABS download
    glob: str                # staged/cache filename glob (under abs dirs)
    source: str              # human-readable source + reference period
    sane: tuple[float, float]  # plausibility bound on the extracted value
    extract: Callable[[pd.DataFrame], float]


_REF = "Mar 2026"
INDICATORS: tuple[MacroIndicator, ...] = (
    MacroIndicator(
        "gdp_growth",
        "https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-national-income-expenditure-and-product/mar-2026/5206001_key_aggregates.xlsx",
        "5206001*national_accounts*.xlsx",
        f"ABS 5206 National Accounts ({_REF}, real SA, through-the-year)",
        (-10.0, 10.0), _gdp_yoy,
    ),
    MacroIndicator(
        "unemployment",
        "https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/mar-2026/6202001.xlsx",
        "6202001*labour_force*.xlsx",
        f"ABS 6202 Labour Force ({_REF}, seasonally adjusted)",
        (0.0, 20.0), _unemployment_level,
    ),
    MacroIndicator(
        "inflation",
        "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/mar-2026/640101.xlsx",
        "64010001*.xlsx",
        f"ABS 6401 CPI ({_REF} quarter, all groups, through-the-year)",
        (-5.0, 20.0), _cpi_yoy,
    ),
    MacroIndicator(
        "wage_growth",
        "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia/mar-2026/634501.xlsx",
        "63450001*.xlsx",
        f"ABS 6345 Wage Price Index ({_REF} quarter, through-the-year)",
        (-5.0, 20.0), _wpi_yoy,
    ),
)


def _content_for(ind: MacroIndicator) -> bytes:
    """Read the staged workbook (``data/raw/public/abs/`` — refreshed live by
    ``fetch_all``) or the committed cache fallback; live-download only as a last
    resort. Keeps builders offline-safe and fast (no network in tests)."""
    for directory in (RAW_PUBLIC_DIR_ABS, _CACHE_ABS):
        hits = sorted(directory.glob(ind.glob)) if directory.exists() else []
        if hits:
            return hits[-1].read_bytes()
    resp = requests.get(ind.url, timeout=_TIMEOUT, headers={"User-Agent": _UA})
    resp.raise_for_status()
    if len(resp.content) < 1024:
        raise ValueError("response too small — likely blocked")
    return resp.content


def load_macro_indicators() -> dict[str, dict]:
    """Return ``{variable_key: {value, source}}`` for the indicators that
    resolve cleanly. Any indicator that fails (missing file, format change,
    out-of-bound value) is omitted, so the caller keeps the config base level."""
    out: dict[str, dict] = {}
    for ind in INDICATORS:
        try:
            value = round(float(ind.extract(_data1(_content_for(ind)))), 1)
        except Exception:
            continue
        if not (ind.sane[0] <= value <= ind.sane[1]):
            continue
        out[ind.key] = {"value": value, "source": ind.source}
    return out


if __name__ == "__main__":
    import sys

    root = Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    for key, info in load_macro_indicators().items():
        print(f"{key:14} {info['value']:>7}  {info['source']}")
