from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.panels.build_business_cycle_panel import build_business_cycle_panel
from src.panels.build_macro_regime_flags import build_macro_regime_flags
from src.panels.build_property_cycle_panel import build_property_cycle_panel


def build_public_panels() -> dict[str, int]:
    business_cycle_panel = build_business_cycle_panel()
    property_cycle_panel = build_property_cycle_panel()
    macro_regime_flags = build_macro_regime_flags()
    return {
        "business_cycle_panel_rows": len(business_cycle_panel),
        "property_cycle_panel_rows": len(property_cycle_panel),
        "macro_regime_flags_rows": len(macro_regime_flags),
    }


def main() -> None:
    counts = build_public_panels()
    print(f"Built public panels: {counts}")


if __name__ == "__main__":
    main()
