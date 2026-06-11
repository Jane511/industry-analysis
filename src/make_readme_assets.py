"""Regenerate parquet mirrors and README chart assets from the real CSV contracts.

Reads the canonical CSV contracts in ``outputs/contracts/`` (built from real
ABS/RBA/PTRS data by ``src/export_contracts.py``) and:

1. Mirrors each to ``data/exports/<key>.parquet`` for parquet consumers.
2. Writes two labelled PNG charts to ``docs/charts/`` for the README.

Run after ``python src/export_contracts.py``. No synthetic data is involved.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.config import ALL_CONTRACT_EXPORTS, LEGACY_PARQUET_EXPORTS_DIR

CHARTS_DIR = ROOT / "docs" / "charts"

LEVEL_COLOURS = {
    "Low": "#2e7d32",
    "Medium": "#9e9d24",
    "Moderate-high": "#ef6c00",
    "Elevated": "#c62828",
    "High": "#7b1fa2",
}


def mirror_parquet() -> None:
    LEGACY_PARQUET_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for key, csv_path in ALL_CONTRACT_EXPORTS.items():
        df = pd.read_csv(csv_path)
        df.to_parquet(LEGACY_PARQUET_EXPORTS_DIR / f"{key}.parquet", index=False)
    print(f"Mirrored {len(ALL_CONTRACT_EXPORTS)} contracts to parquet.")


def chart_industry_risk() -> Path:
    df = pd.read_csv(ALL_CONTRACT_EXPORTS["industry_risk_scores"])
    df = df.sort_values("industry_base_risk_score")
    colours = [LEVEL_COLOURS.get(lvl, "#607d8b") for lvl in df["industry_base_risk_level"]]
    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.barh(df["industry"], df["industry_base_risk_score"], color=colours)
    ax.set_xlabel("Industry base risk score (1 = low, 5 = high)")
    ax.set_title("Australian industry credit-risk scores by ANZSIC division\n"
                 "Real ABS + RBA data — sorted low to high")
    ax.axvline(2.75, color="#444", linestyle="--", linewidth=0.8)
    ax.text(2.77, 0.2, "Elevated threshold (2.75)", fontsize=8, color="#444")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in
               ("#2e7d32", "#9e9d24", "#ef6c00", "#c62828")]
    ax.legend(handles, ["Low", "Medium", "Moderate-high", "Elevated"],
              title="Risk band", fontsize=8, loc="lower right")
    fig.tight_layout()
    out = CHARTS_DIR / "industry_risk_scores.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def chart_downturn_multipliers() -> Path:
    df = pd.read_csv(ALL_CONTRACT_EXPORTS["downturn_overlay_table"])
    order = ["base", "mild", "moderate", "severe"]
    df["scenario"] = pd.Categorical(df["scenario"], order, ordered=True)
    df = df.sort_values("scenario")
    x = range(len(df))
    width = 0.27
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([i - width for i in x], df["pd_multiplier"], width, label="PD multiplier", color="#c62828")
    ax.bar(list(x), df["lgd_multiplier"], width, label="LGD multiplier", color="#1565c0")
    ax.bar([i + width for i in x], df["ccf_multiplier"], width, label="CCF multiplier", color="#2e7d32")
    ax.set_xticks(list(x))
    ax.set_xticklabels([s.title() for s in df["scenario"]])
    ax.set_ylabel("Multiplier (×)")
    ax.set_title("Downturn stress multipliers by scenario\n"
                 "ASSUMPTION (illustrative scenario parameters), nudged by real ABS property softness")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = CHARTS_DIR / "downturn_multipliers.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def print_samples() -> None:
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    irs = pd.read_csv(ALL_CONTRACT_EXPORTS["industry_risk_scores"])
    cols = ["anzsic_division_code", "industry", "industry_base_risk_score", "industry_base_risk_level", "pd_multiplier"]
    print("\n### industry_risk_scores (top 5 by risk)\n")
    print(irs.sort_values("industry_base_risk_score", ascending=False)[cols].head(5).to_string(index=False))
    print("\n### downturn_overlay_table\n")
    dn = pd.read_csv(ALL_CONTRACT_EXPORTS["downturn_overlay_table"])
    print(dn[["scenario", "pd_multiplier", "lgd_multiplier", "ccf_multiplier", "property_value_haircut"]].to_string(index=False))
    print("\n### macro_regime_flags\n")
    mr = pd.read_csv(ALL_CONTRACT_EXPORTS["macro_regime_flags"])
    print(mr.to_string(index=False))
    print("\n### property_market_overlays\n")
    po = pd.read_csv(ALL_CONTRACT_EXPORTS["property_market_overlays"])
    print(po[["property_segment_code", "property_segment", "cycle_stage", "market_softness_score", "pd_multiplier"]].to_string(index=False))


def main() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    mirror_parquet()
    c1 = chart_industry_risk()
    c2 = chart_downturn_multipliers()
    print(f"Charts: {c1.name}, {c2.name}")
    print_samples()


if __name__ == "__main__":
    main()
