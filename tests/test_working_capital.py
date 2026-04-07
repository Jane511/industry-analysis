from pathlib import Path
import shutil
from uuid import uuid4

import pandas as pd

from src.build_working_capital import build_working_capital_metrics


def test_build_working_capital_metrics_creates_expected_columns() -> None:
    tmp_path = Path("tests") / ".tmp" / f"working-capital-{uuid4().hex}"
    tmp_path.mkdir(parents=True, exist_ok=True)

    benchmarks = pd.DataFrame(
        [
            {
                "sector_key": "manufacturing",
                "industry": "Manufacturing",
                "ar_days_benchmark": 33.7,
                "ar_days_stress_benchmark": 48.0,
                "ar_days_severe_benchmark": 67.0,
                "ap_days_benchmark": 33.7,
                "ap_days_stress_benchmark": 48.0,
                "ap_days_severe_benchmark": 67.0,
                "ptrs_cycle8_paid_on_time_pct": 0.661,
                "ptrs_cycle9_paid_on_time_pct": 0.621,
                "inventory_days_benchmark": 52.7,
                "inventory_days_yoy_change": -3.7,
                "inventory_stock_build_risk": "Moderate",
            }
        ]
    )
    borrower_compare = pd.DataFrame(
        [
            {
                "borrower_name": "Manufacturing Archetype",
                "industry": "Manufacturing",
                "sector_key": "manufacturing",
                "ar_days": 34.8,
                "ar_days_benchmark": 33.7,
                "ar_days_score": 2,
                "ap_days": 34.3,
                "ap_days_benchmark": 33.7,
                "ap_days_score": 2,
                "inventory_days": 54.7,
                "inventory_days_benchmark": 52.7,
                "inventory_days_score": 2,
            }
        ]
    )

    try:
        industry_wc, borrower_wc = build_working_capital_metrics(benchmarks, borrower_compare, tmp_path)

        assert (tmp_path / "industry_working_capital_risk_metrics.csv").exists()
        assert (tmp_path / "borrower_working_capital_risk_metrics.csv").exists()

        assert "cash_conversion_cycle_benchmark_days" in industry_wc.columns
        assert "working_capital_pd_overlay_score" in industry_wc.columns
        assert "working_capital_lgd_overlay_score" in industry_wc.columns

        assert industry_wc.loc[0, "cash_conversion_cycle_benchmark_days"] == 52.7
        assert industry_wc.loc[0, "ar_stress_uplift_days"] == 14.3
        assert industry_wc.loc[0, "working_capital_pd_overlay_score"] >= 2.0

        assert "cash_conversion_cycle_days" in borrower_wc.columns
        assert "working_capital_pd_metric_score" in borrower_wc.columns
        assert borrower_wc.loc[0, "cash_conversion_cycle_days"] == 55.2
        assert borrower_wc.loc[0, "receivables_headroom_to_stress_days"] == 13.2
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
