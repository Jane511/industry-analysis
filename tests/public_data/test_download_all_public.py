from __future__ import annotations

import json
from email.message import Message
from pathlib import Path
from urllib.error import URLError

import pytest

from src.public_data import download_all_public as dap
from src.reporting.industry_analysis_report import _append_manifest_sources


def test_is_direct_download_url_classifies_files_and_landing_pages() -> None:
    assert dap.is_direct_download_url("https://example.test/file.xlsx")
    assert dap.is_direct_download_url("https://example.test/file.xls")
    assert dap.is_direct_download_url("https://example.test/file.csv")
    assert dap.is_direct_download_url("https://example.test/file.pdf")

    assert not dap.is_direct_download_url("https://example.test/publications/")
    assert not dap.is_direct_download_url("https://example.test/publications/latest")
    assert not dap.is_direct_download_url("https://example.test/page.html")


@pytest.mark.parametrize(
    ("key", "expected_name"),
    [
        ("rba_cash_rate_csv", "rba"),
        ("ptrs_cycle_8_pdf", "ptrs"),
        ("cotality_hvi_page", "cotality"),
        ("domain_quarterly_page", "domain"),
        ("sqm_headline_page", "sqm"),
        ("nsw_rental_bonds", "state_rental_bonds"),
        ("business_indicators_profit_ratio_xlsx", "abs"),
        ("labour_force_industry_xlsx", "abs"),
    ],
)
def test_destination_dir_for_key_routes_to_source_directory(monkeypatch, tmp_path, key: str, expected_name: str) -> None:
    paths = {
        "RAW_PUBLIC_DIR": tmp_path / "public",
        "RAW_PUBLIC_DIR_RBA": tmp_path / "rba",
        "RAW_PUBLIC_DIR_PTRS": tmp_path / "ptrs",
        "RAW_PUBLIC_DIR_COTALITY": tmp_path / "cotality",
        "RAW_PUBLIC_DIR_DOMAIN": tmp_path / "domain",
        "RAW_PUBLIC_DIR_SQM": tmp_path / "sqm",
        "RAW_PUBLIC_DIR_STATE_RENTAL_BONDS": tmp_path / "state_rental_bonds",
        "RAW_PUBLIC_DIR_ABS": tmp_path / "abs",
    }
    for attr, value in paths.items():
        monkeypatch.setattr(dap, attr, value)

    assert dap.destination_dir_for_key(key) == tmp_path / expected_name


def test_download_all_public_downloads_skips_cached_and_writes_manifest(monkeypatch, tmp_path) -> None:
    source_urls = {
        "rba_cash_rate_csv": "https://example.test/f1-data.csv",
        "rba_fsr_page": "https://example.test/publications/fsr/",
        "ptrs_cycle_8_pdf": "https://example.test/cycle8.pdf",
    }
    monkeypatch.setattr(dap, "PUBLIC_SOURCE_URLS", source_urls)
    monkeypatch.setattr(dap, "RAW_PUBLIC_DIR_RBA", tmp_path / "rba")
    monkeypatch.setattr(dap, "RAW_PUBLIC_DIR_PTRS", tmp_path / "ptrs")
    monkeypatch.setattr(dap, "RAW_PUBLIC_DIR", tmp_path)
    monkeypatch.setattr(dap, "MANIFEST_PATH", tmp_path / "_manifest.json")

    cached = tmp_path / "ptrs" / "cycle8.pdf"
    cached.parent.mkdir(parents=True)
    cached.write_bytes(b"already here")

    calls: list[str] = []

    def fake_urlretrieve(url: str, destination: Path):
        calls.append(url)
        destination.write_bytes(f"downloaded from {url}".encode("utf-8"))
        headers = Message()
        headers["Last-Modified"] = "Wed, 01 Jan 2025 00:00:00 GMT"
        return str(destination), headers

    monkeypatch.setattr(dap, "urlretrieve", fake_urlretrieve)

    summary = dap.download_all_public()

    assert calls == ["https://example.test/f1-data.csv"]
    assert [row["key"] for row in summary["downloaded"]] == ["rba_cash_rate_csv"]
    assert [row["key"] for row in summary["cached"]] == ["ptrs_cycle_8_pdf"]
    assert [row["key"] for row in summary["skipped_landing_pages"]] == ["rba_fsr_page"]
    assert not summary["failed"]

    manifest = json.loads((tmp_path / "_manifest.json").read_text(encoding="utf-8"))
    entry = manifest["rba_cash_rate_csv"]
    assert entry["url"] == "https://example.test/f1-data.csv"
    assert entry["source_mtime"] == 1735689600
    assert entry["size_bytes"] > 0
    assert len(entry["sha256"]) == 64


def test_download_all_public_records_failures_and_continues(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(dap, "PUBLIC_SOURCE_URLS", {
        "rba_cash_rate_csv": "https://example.test/f1-data.csv",
        "ptrs_cycle_8_pdf": "https://example.test/cycle8.pdf",
    })
    monkeypatch.setattr(dap, "RAW_PUBLIC_DIR_RBA", tmp_path / "rba")
    monkeypatch.setattr(dap, "RAW_PUBLIC_DIR_PTRS", tmp_path / "ptrs")
    monkeypatch.setattr(dap, "MANIFEST_PATH", tmp_path / "_manifest.json")

    def fake_urlretrieve(url: str, destination: Path):
        if url.endswith("f1-data.csv"):
            raise URLError("offline")
        destination.write_bytes(b"ok")
        return str(destination), Message()

    monkeypatch.setattr(dap, "urlretrieve", fake_urlretrieve)

    summary = dap.download_all_public()

    assert [row["key"] for row in summary["failed"]] == ["rba_cash_rate_csv"]
    assert [row["key"] for row in summary["downloaded"]] == ["ptrs_cycle_8_pdf"]


def test_append_manifest_sources_adds_manifest_only_rows() -> None:
    import pandas as pd

    sources = pd.DataFrame([
        {"Overlay": "industry_risk_scores", "Primary source": "ABS", "URL": "https://abs.test", "Refreshed": "2026-01-01"}
    ])
    manifest = {
        "rba_cash_rate_csv": {
            "url": "https://example.test/f1-data.csv",
            "fetched_at": "2026-04-28T00:00:00+00:00",
        }
    }

    out = _append_manifest_sources(sources, manifest)

    row = out[out["Overlay"] == "rba_cash_rate_csv"].iloc[0]
    assert row["Primary source"] == "Downloaded public source"
    assert row["URL"] == "https://example.test/f1-data.csv"
    assert row["Refreshed"] == "2026-04-28T00:00:00+00:00"
