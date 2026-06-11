"""Tests for the ASIC Series 1A failure-rate panel (Output B).

The loader is production-safe: without ``ASIC_USE_STUB=1`` and without a
real staged file it raises a clear ``RuntimeError``. These tests exercise
both paths — the opt-in stub load (for development/CI) and the fail-loud
default.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from src.overlays.build_industry_risk_scores import build_industry_risk_scores
from src.panels.build_industry_failure_rates import (
    FALLBACK_ACTIVE_BUSINESSES_COUNTS,
    build_industry_failure_rates,
)
from src.public_data.download_asic_insolvency import (
    ASIC_STUB_ENV_VAR,
    SERIES_1A_SCHEMA,
    load_empty_series_1a_frame,
    load_optional_asic_insolvency_extract,
)


@pytest.fixture
def stub_enabled(monkeypatch):
    """Enable the synthetic ASIC stub for a single test."""
    monkeypatch.setenv(ASIC_STUB_ENV_VAR, "1")


def _isolate_asic_search_paths(monkeypatch, empty_dir: Path) -> None:
    """Redirect the loader's search paths to an empty directory.

    Used by tests that need to simulate a production-like environment where
    no real ASIC file is staged.
    """
    import src.public_data.download_asic_insolvency as module

    monkeypatch.setattr(module, "RAW_PUBLIC_DIR_ASIC", empty_dir)
    monkeypatch.setattr(module, "RAW_PUBLIC_DIR", empty_dir)
    monkeypatch.setattr(module, "RAW_MANUAL_DIR", empty_dir)


def test_load_empty_series_1a_frame_returns_canonical_schema() -> None:
    df = load_empty_series_1a_frame()
    assert list(df.columns) == list(SERIES_1A_SCHEMA)
    assert df.empty


def test_loader_raises_runtime_error_when_no_real_file_and_stub_disabled(
    monkeypatch, tmp_path: Path
) -> None:
    """Production default: no real file + no env var = RuntimeError naming
    the expected path and URL."""
    empty_dir = tmp_path / "nowhere"
    empty_dir.mkdir()
    _isolate_asic_search_paths(monkeypatch, empty_dir)
    monkeypatch.delenv(ASIC_STUB_ENV_VAR, raising=False)

    with pytest.raises(RuntimeError) as exc_info:
        load_optional_asic_insolvency_extract()

    message = str(exc_info.value)
    assert "ASIC Series 1A" in message
    assert "ASIC_USE_STUB" in message
    assert "asic.gov.au" in message


def test_loader_uses_stub_when_opt_in_env_var_is_set(stub_enabled) -> None:
    df = load_optional_asic_insolvency_extract()
    assert list(df.columns) == list(SERIES_1A_SCHEMA)
    # The stub covers the 18 canonical ANZSIC divisions over 22+ months.
    assert not df.empty
    assert df["source_note"].astype(str).str.contains("SYNTHETIC").all()


def test_build_produces_one_row_per_covered_anzsic_division(stub_enabled) -> None:
    df = build_industry_failure_rates(as_of=date(2026, 4, 24))

    assert len(df) == len(FALLBACK_ACTIVE_BUSINESSES_COUNTS)
    assert set(df["anzsic_division_code"]) == set(FALLBACK_ACTIVE_BUSINESSES_COUNTS)

    rates = df["failure_rate_pct"]
    assert rates.between(0, 100).all(), (
        f"failure_rate_pct out of [0, 100]: {rates.tolist()}"
    )


def test_failure_rates_join_cleanly_to_industry_risk_scores(stub_enabled) -> None:
    rates = build_industry_failure_rates(as_of=date(2026, 4, 24))
    scores = build_industry_risk_scores()

    merged = scores.merge(
        rates,
        on="anzsic_division_code",
        how="inner",
        suffixes=("_score", "_rate"),
    )

    assert len(merged) == len(scores), (
        "inner join dropped rows — industry_risk_scores and failure_rates "
        "should cover the same ANZSIC divisions"
    )
    assert merged["failure_rate_pct"].notna().all()
    assert merged["pd_multiplier"].notna().all()


def test_build_fails_loud_when_no_real_file_and_stub_disabled(
    monkeypatch, tmp_path: Path
) -> None:
    """Ensure the failure-rates builder propagates the loader's
    RuntimeError rather than silently emitting zeros. This is the
    production safety property — on-call must see the gap."""
    empty_dir = tmp_path / "nowhere"
    empty_dir.mkdir()
    _isolate_asic_search_paths(monkeypatch, empty_dir)
    monkeypatch.delenv(ASIC_STUB_ENV_VAR, raising=False)

    with pytest.raises(RuntimeError):
        build_industry_failure_rates(as_of=date(2026, 4, 24))


def test_stub_source_note_is_clearly_marked(stub_enabled) -> None:
    """Every stub-derived row must be obviously tagged as synthetic so a
    downstream consumer that drops the source_note column still cannot be
    silently contaminated at the filename level."""
    df = build_industry_failure_rates(as_of=date(2026, 4, 24))
    assert df["source_note"].astype(str).str.contains("SYNTHETIC").all()
