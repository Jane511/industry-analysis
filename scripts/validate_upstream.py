from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.overlays.export_contracts import export_contracts
from src.validation import validate_upstream_outputs


def validate_upstream() -> bool:
    outputs = export_contracts()
    checks = validate_upstream_outputs(outputs)
    print(checks.to_string(index=False))
    return bool(checks["status"].all())


def main() -> None:
    try:
        success = validate_upstream()
    except RuntimeError as exc:
        raise SystemExit(str(exc))
    if not success:
        raise SystemExit("Upstream validation failed.")
    print("Upstream validation passed.")


if __name__ == "__main__":
    main()
