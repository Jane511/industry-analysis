from __future__ import annotations

import json
from email.message import Message
from pathlib import Path

import pytest

from src.public_data import download_rba_publications as rba


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "rba"


def _fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


@pytest.fixture
def rba_pages(monkeypatch):
    pages = {
        "https://www.rba.gov.au/publications/fsr/": _fixture("fsr_landing.html"),
        "https://www.rba.gov.au/publications/fsr/2026/mar/": _fixture("fsr_publication.html"),
        "https://www.rba.gov.au/publications/smp/": _fixture("smp_landing.html"),
        "https://www.rba.gov.au/publications/smp/2026/feb/": _fixture("smp_publication.html"),
        "https://www.rba.gov.au/chart-pack/": _fixture("chart_pack_landing.html"),
    }

    def fake_fetch_html(url: str) -> str:
        return pages[url]

    monkeypatch.setattr(rba, "_fetch_html", fake_fetch_html)
    return pages


def test_discovers_latest_fsr_pdf_from_fixture(rba_pages) -> None:
    discovered = rba._discover_latest_url(rba.FSR)

    assert discovered.pdf_url == (
        "https://www.rba.gov.au/publications/fsr/2026/mar/pdf/"
        "financial-stability-review-2026-03.pdf"
    )
    assert discovered.period == "March 2026"


def test_discovers_latest_smp_pdf_from_fixture(rba_pages) -> None:
    discovered = rba._discover_latest_url(rba.SMP)

    assert discovered.pdf_url == (
        "https://www.rba.gov.au/publications/smp/2026/feb/pdf/"
        "statement-on-monetary-policy-2026-02.pdf"
    )
    assert discovered.period == "February 2026"


def test_discovers_latest_chart_pack_pdf_from_fixture(rba_pages) -> None:
    discovered = rba._discover_latest_url(rba.CHART_PACK)

    assert discovered.pdf_url == "https://www.rba.gov.au/chart-pack/pdf/chart-pack.pdf"
    assert discovered.period == "March 2026"


def test_download_latest_writes_manifest_with_period(monkeypatch, tmp_path, rba_pages) -> None:
    monkeypatch.setattr(rba, "MANIFEST_PATH", tmp_path / "_manifest.json")

    def fake_urlretrieve(url: str, destination: Path):
        destination.write_bytes(b"%PDF fixture")
        headers = Message()
        headers["Last-Modified"] = "Thu, 19 Mar 2026 00:00:00 GMT"
        return str(destination), headers

    monkeypatch.setattr(rba, "urlretrieve", fake_urlretrieve)

    path = rba.download_latest_fsr(tmp_path)

    assert path.name == "financial-stability-review-2026-03.pdf"
    manifest = json.loads((tmp_path / "_manifest.json").read_text(encoding="utf-8"))
    entry = manifest["rba_fsr_pdf"]
    assert entry["period"] == "March 2026"
    assert entry["landing_page_url"] == "https://www.rba.gov.au/publications/fsr/"
    assert entry["overlay"] == "RBA FSR (forward-looking)"
    assert entry["primary_source"] == "RBA Financial Stability Review"


def test_download_latest_skips_cached_file(monkeypatch, tmp_path, rba_pages) -> None:
    cached = tmp_path / "chart-pack.pdf"
    cached.write_bytes(b"cached")

    calls = []

    def fake_urlretrieve(url: str, destination: Path):
        calls.append(url)
        destination.write_bytes(b"new")
        return str(destination), Message()

    monkeypatch.setattr(rba, "urlretrieve", fake_urlretrieve)

    path = rba.download_latest_chart_pack(tmp_path)

    assert path == cached
    assert path.read_bytes() == b"cached"
    assert calls == []


def test_download_error_names_selector_and_landing_page(monkeypatch) -> None:
    monkeypatch.setattr(rba, "_fetch_html", lambda url: "<html><body>No latest link</body></html>")

    with pytest.raises(rba.DownloadError) as excinfo:
        rba._discover_latest_url(rba.FSR)

    message = str(excinfo.value)
    assert "https://www.rba.gov.au/publications/fsr/" in message
    assert "latest publication link" in message
