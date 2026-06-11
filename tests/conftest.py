"""Shared pytest configuration.

Enables the ASIC Series 1A synthetic stub by default for every test, mirror
the "development / CI" intent of the test suite. Individual tests that
want to exercise the fail-loud production default must explicitly call
``monkeypatch.delenv(ASIC_STUB_ENV_VAR)``.
"""

from __future__ import annotations

import os

from src.public_data.download_asic_insolvency import ASIC_STUB_ENV_VAR


def pytest_configure(config) -> None:
    # pytest imports test modules before fixtures run, so set the env var
    # at configure time rather than in a fixture. Tests that need to
    # simulate production unset it via monkeypatch.
    os.environ.setdefault(ASIC_STUB_ENV_VAR, "1")
