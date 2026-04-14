from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.overlays.build_downturn_overlay_tables import build_downturn_overlay_tables
from src.overlays.build_industry_risk_scores import build_industry_risk_scores
from src.overlays.build_property_market_overlays import build_property_market_overlays
from src.panels.build_business_cycle_panel import build_business_cycle_panel
from src.panels.build_property_cycle_panel import build_property_cycle_panel


def build_overlays() -> dict[str, int]:
    business_cycle_panel = build_business_cycle_panel()
    property_cycle_panel = build_property_cycle_panel()
    industry_risk_scores = build_industry_risk_scores(panel=business_cycle_panel)
    property_market_overlays = build_property_market_overlays(panel=property_cycle_panel)
    downturn_overlay_table = build_downturn_overlay_tables(property_cycle_panel=property_cycle_panel)
    return {
        "industry_risk_scores_rows": len(industry_risk_scores),
        "property_market_overlays_rows": len(property_market_overlays),
        "downturn_overlay_table_rows": len(downturn_overlay_table),
    }


def main() -> None:
    counts = build_overlays()
    print(f"Built overlays: {counts}")


if __name__ == "__main__":
    main()
