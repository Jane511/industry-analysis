from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import CORE_CONTRACT_EXPORTS, OPTIONAL_EXPLAINABILITY_EXPORTS
from src.overlays.export_contracts import export_contracts
from src.public_data.download_asic_insolvency import ASIC_STUB_ENV_VAR


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the canonical contract-export pipeline. "
            "Without ASIC_USE_STUB set, the run fails if real ASIC Series 1A "
            "data is not staged — that is intentional, so production runs "
            "surface missing inputs rather than silently exporting zeros."
        )
    )
    parser.add_argument(
        "--allow-stub-export",
        action="store_true",
        help=(
            "Required in addition to ASIC_USE_STUB=1 to actually write "
            "synthetic-stub-derived output to the committed CSVs. "
            "This double-gate prevents a production scheduler that "
            "accidentally inherits ASIC_USE_STUB from publishing stub data."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    stub_enabled = os.environ.get(ASIC_STUB_ENV_VAR, "0") == "1"

    if stub_enabled and not args.allow_stub_export:
        raise SystemExit(
            f"{ASIC_STUB_ENV_VAR}=1 is set, so the ASIC loader would read the "
            "synthetic development stub. Exporting stub-derived numbers to the "
            "committed CSVs requires --allow-stub-export to be passed as well. "
            "For production runs, unset " f"{ASIC_STUB_ENV_VAR} and stage real "
            "ASIC data instead."
        )

    if stub_enabled:
        print(
            f"[WARNING] {ASIC_STUB_ENV_VAR}=1 + --allow-stub-export — export "
            "will write stub-derived industry_failure_rates. Do NOT use this "
            "output for production decisions.",
            file=sys.stderr,
            flush=True,
        )

    try:
        outputs = export_contracts()
    except RuntimeError as exc:
        raise SystemExit(str(exc))
    print(f"Exported core contracts: {list(CORE_CONTRACT_EXPORTS.keys())}")
    print(f"Exported optional explainability panels: {list(OPTIONAL_EXPLAINABILITY_EXPORTS.keys())}")
    print(f"Materialized output keys: {sorted(outputs.keys())}")


if __name__ == "__main__":
    main()
