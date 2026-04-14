from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import CORE_CONTRACT_EXPORTS, OPTIONAL_EXPLAINABILITY_EXPORTS
from src.overlays.export_contracts import export_contracts


def main() -> None:
    try:
        outputs = export_contracts()
    except RuntimeError as exc:
        raise SystemExit(str(exc))
    print(f"Exported core contracts: {list(CORE_CONTRACT_EXPORTS.keys())}")
    print(f"Exported optional explainability panels: {list(OPTIONAL_EXPLAINABILITY_EXPORTS.keys())}")
    print(f"Materialized output keys: {sorted(outputs.keys())}")


if __name__ == "__main__":
    main()
