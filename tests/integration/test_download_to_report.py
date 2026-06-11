from __future__ import annotations

import json
from email.message import Message
from pathlib import Path

from src.public_data import download_all_public as dap
from src.public_data import download_rba_publications as rba
from src.reporting.industry_analysis_report import build_report


RBA_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "rba"


def test_download_manifest_sources_surface_in_section_8(monkeypatch, tmp_path) -> None:
    source_urls = {
        "test_abs_xlsx": "https://example.test/abs.xlsx",
        "test_rba_csv": "https://example.test/rba.csv",
        "test_ptrs_pdf": "https://example.test/ptrs.pdf",
    }
    monkeypatch.setattr(dap, "PUBLIC_SOURCE_URLS", source_urls)
    monkeypatch.setattr(dap, "RAW_PUBLIC_DIR", tmp_path / "public")
    monkeypatch.setattr(dap, "RAW_PUBLIC_DIR_ABS", tmp_path / "public" / "abs")
    monkeypatch.setattr(dap, "RAW_PUBLIC_DIR_RBA", tmp_path / "public" / "rba")
    monkeypatch.setattr(dap, "RAW_PUBLIC_DIR_PTRS", tmp_path / "public" / "ptrs")
    monkeypatch.setattr(dap, "MANIFEST_PATH", tmp_path / "public" / "_manifest.json")

    def fake_urlretrieve(url: str, destination):
        destination.write_bytes(f"fixture for {url}".encode("utf-8"))
        headers = Message()
        headers["Last-Modified"] = "Tue, 28 Apr 2026 00:00:00 GMT"
        return str(destination), headers

    monkeypatch.setattr(dap, "urlretrieve", fake_urlretrieve)

    summary = dap.download_all_public()
    manifest = dap.load_manifest(tmp_path / "public" / "_manifest.json")
    report = build_report(manifest=manifest)

    data_sources = next(section for section in report["sections"] if section["id"] == "data_sources_inventory")
    sources_table = next(
        payload["data"]
        for kind, payload in data_sources["elements"]
        if kind == "table" and payload["caption"] == "Data Sources Inventory"
    )

    assert len(summary["downloaded"]) == 3
    assert set(manifest) == {"test_abs_xlsx", "test_rba_csv", "test_ptrs_pdf"}
    for key in manifest:
        row = sources_table[sources_table["Source key"] == key].iloc[0]
        assert row["URL or landing page"] == source_urls[key]
        assert row["Retrieved / fetched timestamp"] == manifest[key]["fetched_at"]


def test_rba_publication_downloads_surface_named_rows_in_section_8(monkeypatch, tmp_path) -> None:
    pages = {
        "https://www.rba.gov.au/publications/fsr/": (RBA_FIXTURE_DIR / "fsr_landing.html").read_text(encoding="utf-8"),
        "https://www.rba.gov.au/publications/fsr/2026/mar/": (RBA_FIXTURE_DIR / "fsr_publication.html").read_text(encoding="utf-8"),
        "https://www.rba.gov.au/publications/smp/": (RBA_FIXTURE_DIR / "smp_landing.html").read_text(encoding="utf-8"),
        "https://www.rba.gov.au/publications/smp/2026/feb/": (RBA_FIXTURE_DIR / "smp_publication.html").read_text(encoding="utf-8"),
        "https://www.rba.gov.au/chart-pack/": (RBA_FIXTURE_DIR / "chart_pack_landing.html").read_text(encoding="utf-8"),
    }
    monkeypatch.setattr(rba, "_fetch_html", lambda url: pages[url])
    monkeypatch.setattr(rba, "RAW_PUBLIC_DIR_RBA", tmp_path / "public" / "rba")
    monkeypatch.setattr(rba, "MANIFEST_PATH", tmp_path / "public" / "_manifest.json")

    def fake_urlretrieve(url: str, destination):
        destination.write_bytes(f"fixture for {url}".encode("utf-8"))
        return str(destination), Message()

    monkeypatch.setattr(rba, "urlretrieve", fake_urlretrieve)

    rba.download_all_rba_publications()
    manifest = json.loads((tmp_path / "public" / "_manifest.json").read_text(encoding="utf-8"))
    report = build_report(manifest=manifest)

    data_sources = next(section for section in report["sections"] if section["id"] == "data_sources_inventory")
    sources_table = next(
        payload["data"]
        for kind, payload in data_sources["elements"]
        if kind == "table" and payload["caption"] == "Data Sources Inventory"
    )

    expected = {
        "rba_fsr_pdf": ("Reserve Bank of Australia", "https://www.rba.gov.au/publications/fsr/", "March 2026"),
        "rba_smp_pdf": ("Reserve Bank of Australia", "https://www.rba.gov.au/publications/smp/", "February 2026"),
        "rba_chart_pack_pdf": ("Reserve Bank of Australia", "https://www.rba.gov.au/chart-pack/", "March 2026"),
    }
    for source_key, (publisher, url, period) in expected.items():
        row = sources_table[sources_table["Source key"] == source_key].iloc[0]
        assert row["Publisher / origin"] == publisher
        assert row["URL or landing page"] == url
        assert row["Period or vintage"] == period
