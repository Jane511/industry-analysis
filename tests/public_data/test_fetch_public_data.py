"""Fetch-or-cache behaviour for the real-public-data extraction module.

Network is never touched: ``_download`` is monkeypatched to fail, so these
tests exercise the committed-cache fallback deterministically.
"""

from __future__ import annotations

import pytest

import src.public_data.fetch_public_data as fpd


def _always_fail(url, dest, timeout=60):  # noqa: ANN001 - test stub
    raise ConnectionError("simulated: source unreachable")


def test_required_source_falls_back_to_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(fpd, "_download", _always_fail)
    # Real cache file shipped in data/cache/abs/.
    spec = fpd.SourceSpec(
        key="australian_industry_xlsx",
        label="ABS 8155 (test)",
        dest_dir=tmp_path,
        dest_filename="out.xlsx",
        cache_relpath="abs/81550DO001_202324.xlsx",
        required=True,
    )
    status, detail = fpd.fetch_source(spec)
    assert status == "cache"
    assert (tmp_path / "out.xlsx").exists()
    assert "committed cache" in detail


def test_optional_source_skips_when_no_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(fpd, "_download", _always_fail)
    spec = fpd.SourceSpec(
        key="ptrs_cycle_8_pdf",
        label="PTRS (test)",
        dest_dir=tmp_path,
        dest_filename="x.pdf",
        cache_relpath=None,
        required=False,
    )
    status, _ = fpd.fetch_source(spec)
    assert status == "skipped"
    assert not (tmp_path / "x.pdf").exists()


def test_required_source_with_no_cache_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(fpd, "_download", _always_fail)
    spec = fpd.SourceSpec(
        key="does_not_exist",
        label="missing (test)",
        dest_dir=tmp_path,
        dest_filename="x.bin",
        cache_relpath="abs/this_file_is_not_in_cache.xlsx",
        required=True,
    )
    with pytest.raises(fpd.FetchError):
        fpd.fetch_source(spec)


def test_committed_cache_has_all_required_sources():
    """Every cache-backed required source must ship a real file in data/cache/."""
    for spec in fpd.REQUIRED_SOURCES:
        assert spec.cache_relpath is not None, spec.key
        assert (fpd.CACHE_DIR / spec.cache_relpath).exists(), spec.cache_relpath
