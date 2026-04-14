"""Validation helpers for upstream overlay exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import (
    CORE_CONTRACT_EXPORTS,
    OPTIONAL_EXPLAINABILITY_EXPORTS,
)


def _build_contract_checks(
    outputs: dict[str, pd.DataFrame],
    export_paths: dict[str, Path],
    check_prefix: str,
    required_for_pass: bool,
) -> list[dict[str, object]]:
    checks = []
    for key, export_path in export_paths.items():
        present = key in outputs and isinstance(outputs[key], pd.DataFrame) and not outputs[key].empty
        checks.append(
            {
                "check_name": f"{check_prefix}_output::{key}",
                "status": bool(present),
                "required_for_pass": required_for_pass,
                "detail": "present and non-empty" if present else "missing or empty",
            }
        )

        exists = export_path.exists()
        has_content = exists and export_path.stat().st_size > 0
        checks.append(
            {
                "check_name": f"{check_prefix}_export_file::{export_path.name}",
                "status": bool(has_content),
                "required_for_pass": required_for_pass,
                "detail": str(export_path) if has_content else f"missing or empty file at {export_path}",
            }
        )
    return checks


def validate_upstream_outputs(outputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    checks = _build_contract_checks(
        outputs=outputs,
        export_paths=CORE_CONTRACT_EXPORTS,
        check_prefix="core",
        required_for_pass=True,
    )
    checks.extend(
        _build_contract_checks(
            outputs=outputs,
            export_paths=OPTIONAL_EXPLAINABILITY_EXPORTS,
            check_prefix="optional",
            required_for_pass=False,
        )
    )
    return pd.DataFrame(checks)
