from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.overlays.export_contracts import export_contracts


def main() -> None:
    try:
        outputs = export_contracts()
    except RuntimeError as exc:
        raise SystemExit(str(exc))
    print(f"Exported canonical contracts: {sorted(outputs.keys())}")


if __name__ == "__main__":
    main()
