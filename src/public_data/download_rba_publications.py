"""Scrape and download the latest RBA FSR, SMP, and Chart Pack PDFs.

The RBA publication pages are HTML landing pages, not stable direct PDF URLs.
This module follows the latest-publication links, finds the current PDF, and
records each download in ``data/raw/public/_manifest.json`` with an additional
``period`` string such as ``"March 2026"``.

Caveats:
- The RBA may restructure its site. If the selector assumptions break,
  ``DownloadError`` names the landing-page URL and the selector pattern that
  failed so an operator can repair the scraper quickly.
- FSR and SMP archive PDFs use date-stamped filenames; only the latest
  publication is fetched. Full historical archive scraping is a separate
  enhancement.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen, urlretrieve

from bs4 import BeautifulSoup

from src.config import PUBLIC_SOURCE_URLS, RAW_PUBLIC_DIR_RBA
from src.public_data.download_all_public import MANIFEST_PATH, write_manifest_entry


MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
PERIOD_RE = re.compile(rf"\b({'|'.join(MONTHS)})\s+(\d{{4}})\b", re.IGNORECASE)


class DownloadError(RuntimeError):
    """Raised when an RBA publication page cannot be discovered or downloaded."""


@dataclass(frozen=True)
class RbaPublication:
    key: str
    landing_key: str
    overlay: str
    primary_source: str
    latest_link_pattern: str
    pdf_link_pattern: str


@dataclass(frozen=True)
class DiscoveredPublication:
    pdf_url: str
    period: str


FSR = RbaPublication(
    key="rba_fsr_pdf",
    landing_key="rba_fsr_page",
    overlay="RBA FSR (forward-looking)",
    primary_source="RBA Financial Stability Review",
    latest_link_pattern="read the latest financial stability review|latest financial stability review",
    pdf_link_pattern="download pdf|download the complete report|read full document",
)
SMP = RbaPublication(
    key="rba_smp_pdf",
    landing_key="rba_smp_page",
    overlay="RBA SMP (forward-looking)",
    primary_source="RBA Statement on Monetary Policy",
    latest_link_pattern="read the latest statement on monetary policy|latest statement on monetary policy",
    pdf_link_pattern="download pdf|download statement|read full document",
)
CHART_PACK = RbaPublication(
    key="rba_chart_pack_pdf",
    landing_key="rba_chart_pack_page",
    overlay="RBA Chart Pack (forward-looking)",
    primary_source="RBA Chart Pack",
    latest_link_pattern="",
    pdf_link_pattern="download the complete|download chart pack|chart pack",
)


def _fetch_html(url: str) -> str:
    try:
        with urlopen(url, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise DownloadError(f"Failed to fetch RBA landing/publication page `{url}`.") from exc


def _link_text(anchor) -> str:
    return " ".join(anchor.get_text(" ", strip=True).split()).lower()


def _href(anchor) -> str:
    return str(anchor.get("href") or "")


def _find_link_by_text(soup: BeautifulSoup, pattern: str, base_url: str, selector_name: str) -> str:
    regex = re.compile(pattern, re.IGNORECASE)
    for anchor in soup.find_all("a", href=True):
        if regex.search(_link_text(anchor)):
            return urljoin(base_url, _href(anchor))
    raise DownloadError(f"Failed to find `{selector_name}` on `{base_url}` using link text pattern `{pattern}`.")


def _find_pdf_link(soup: BeautifulSoup, pattern: str, base_url: str) -> str:
    regex = re.compile(pattern, re.IGNORECASE)
    fallback: str | None = None
    for anchor in soup.find_all("a", href=True):
        href = _href(anchor)
        if not urlparse(href).path.lower().endswith(".pdf"):
            continue
        if regex.search(_link_text(anchor)) or regex.search(href):
            return urljoin(base_url, href)
        if fallback is None:
            fallback = urljoin(base_url, href)
    if fallback is not None:
        return fallback
    raise DownloadError(f"Failed to find PDF link on `{base_url}` using href ending `.pdf` and text pattern `{pattern}`.")


def _period_from_text(text: str, page_url: str) -> str:
    match = PERIOD_RE.search(text)
    if match:
        month = match.group(1).title()
        return f"{month} {match.group(2)}"

    path_match = re.search(
        r"/(?P<year>\d{4})/(?P<month>jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/",
        urlparse(page_url).path,
        re.IGNORECASE,
    )
    if path_match:
        month_lookup = {
            "jan": "January",
            "feb": "February",
            "mar": "March",
            "apr": "April",
            "may": "May",
            "jun": "June",
            "jul": "July",
            "aug": "August",
            "sep": "September",
            "oct": "October",
            "nov": "November",
            "dec": "December",
        }
        return f"{month_lookup[path_match.group('month').lower()]} {path_match.group('year')}"

    raise DownloadError(f"Failed to extract period string from `{page_url}` using `{PERIOD_RE.pattern}`.")


def _discover_latest_url(publication: RbaPublication) -> DiscoveredPublication:
    landing_url = PUBLIC_SOURCE_URLS[publication.landing_key]
    landing_soup = BeautifulSoup(_fetch_html(landing_url), "html.parser")

    if publication is CHART_PACK:
        pdf_url = _find_pdf_link(landing_soup, publication.pdf_link_pattern, landing_url)
        period = _period_from_text(landing_soup.get_text(" ", strip=True), landing_url)
        return DiscoveredPublication(pdf_url=pdf_url, period=period)

    latest_page_url = _find_link_by_text(
        landing_soup,
        publication.latest_link_pattern,
        landing_url,
        selector_name="latest publication link",
    )
    latest_soup = BeautifulSoup(_fetch_html(latest_page_url), "html.parser")
    pdf_url = _find_pdf_link(latest_soup, publication.pdf_link_pattern, latest_page_url)
    period = _period_from_text(latest_soup.get_text(" ", strip=True), latest_page_url)
    return DiscoveredPublication(pdf_url=pdf_url, period=period)


def _filename_from_pdf_url(url: str) -> str:
    name = Path(urlparse(url).path).name
    if not name:
        raise DownloadError(f"Could not derive PDF filename from `{url}`.")
    return name


def _download_publication(publication: RbaPublication, dest_dir: Path, force_refresh: bool = False) -> Path:
    discovered = _discover_latest_url(publication)
    dest_dir.mkdir(parents=True, exist_ok=True)
    destination = dest_dir / _filename_from_pdf_url(discovered.pdf_url)

    if destination.exists() and not force_refresh:
        return destination

    try:
        _, headers = urlretrieve(discovered.pdf_url, destination)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise DownloadError(f"Failed to download `{publication.key}` from `{discovered.pdf_url}`.") from exc

    write_manifest_entry(
        publication.key,
        discovered.pdf_url,
        destination,
        headers,
        manifest_path=MANIFEST_PATH,
        extra={
            "period": discovered.period,
            "landing_page_url": PUBLIC_SOURCE_URLS[publication.landing_key],
            "overlay": publication.overlay,
            "primary_source": publication.primary_source,
        },
    )
    return destination


def download_latest_fsr(dest_dir: Path, force_refresh: bool = False) -> Path:
    return _download_publication(FSR, dest_dir, force_refresh=force_refresh)


def download_latest_smp(dest_dir: Path, force_refresh: bool = False) -> Path:
    return _download_publication(SMP, dest_dir, force_refresh=force_refresh)


def download_latest_chart_pack(dest_dir: Path, force_refresh: bool = False) -> Path:
    return _download_publication(CHART_PACK, dest_dir, force_refresh=force_refresh)


def download_all_rba_publications(force_refresh: bool = False) -> dict[str, Path]:
    """Download the latest FSR, SMP, and Chart Pack PDFs to the RBA raw-public directory."""
    return {
        "rba_fsr_pdf": download_latest_fsr(RAW_PUBLIC_DIR_RBA, force_refresh=force_refresh),
        "rba_smp_pdf": download_latest_smp(RAW_PUBLIC_DIR_RBA, force_refresh=force_refresh),
        "rba_chart_pack_pdf": download_latest_chart_pack(RAW_PUBLIC_DIR_RBA, force_refresh=force_refresh),
    }
