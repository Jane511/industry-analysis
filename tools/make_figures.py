"""
tools/make_figures.py — regenerate the README charts for this repo.

Every figure is built from the committed contract CSVs in outputs/contracts/
(aggregated, public-source industry signals only), so the charts regenerate
reproducibly with:

    python tools/make_figures.py

Outputs PNGs into outputs/charts/.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CON = ROOT / "outputs" / "contracts"
FIG = ROOT / "outputs" / "charts"
FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130,
    "font.size": 12.5, "axes.titlesize": 15, "axes.titleweight": "bold",
    "axes.labelsize": 12.5, "axes.grid": True, "grid.alpha": 0.25,
    "axes.spines.top": False, "axes.spines.right": False,
})
LEVEL_COLOR = {"Low": "#1a9850", "Medium": "#fee08b", "Moderate-high": "#fdae61",
               "Elevated": "#f46d43", "High": "#a50026", "Severe": "#a50026"}
BLUE = "#2166ac"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name)
    plt.close(fig)
    print("wrote", FIG / name)


# 1. Industry risk scores ranked (riskiest at top) ---------------------------
risk = pd.read_csv(CON / "industry_risk_scores.csv").sort_values("industry_base_risk_score")
fig, ax = plt.subplots(figsize=(8.6, 6.4))
colors = [LEVEL_COLOR.get(lv, BLUE) for lv in risk.industry_base_risk_level]
bars = ax.barh(risk.industry, risk.industry_base_risk_score, color=colors, edgecolor="white")
for y, v in enumerate(risk.industry_base_risk_score):
    ax.text(v, y, f" {v:.2f}", va="center", fontsize=9.5)
ax.set_xlabel("industry base risk score (1 = low → 5 = high)")
fig.suptitle("Which industries are riskiest right now", fontsize=15, fontweight="bold")
ax.grid(axis="y", alpha=0)
levels = ["Medium", "Moderate-high", "Elevated"]
handles = [plt.Rectangle((0, 0), 1, 1, color=LEVEL_COLOR[k]) for k in levels]
ax.legend(handles, levels, frameon=False, loc="lower right", title="risk level")
save(fig, "industry_risk_scores_ranked.png")

# 2. Downturn scenario overlay multipliers -----------------------------------
ov = pd.read_csv(CON / "downturn_overlay_table.csv")
order = ["base", "mild", "moderate", "severe"]
ov = ov[ov.scenario.isin(order)].set_index("scenario").reindex(order).reset_index()
fig, ax = plt.subplots(figsize=(8.0, 4.8))
x = range(len(ov))
w = 0.2
ax.bar([i - 1.5 * w for i in x], ov.pd_multiplier, w, label="PD ×", color="#b2182b")
ax.bar([i - 0.5 * w for i in x], ov.lgd_multiplier, w, label="LGD ×", color="#ef8a62")
ax.bar([i + 0.5 * w for i in x], ov.ccf_multiplier, w, label="CCF ×", color="#67a9cf")
ax.bar([i + 1.5 * w for i in x], 1 + ov.property_value_haircut, w, label="property value (1 − haircut)", color="#2166ac")
ax.set_xticks(list(x)); ax.set_xticklabels([s.title() for s in ov.scenario])
ax.axhline(1.0, color="#4d4d4d", linewidth=0.8)
ax.set_ylabel("multiplier applied to base")
ax.set_title("Downturn overlay: stress multipliers by scenario")
ax.legend(frameon=False, ncol=2, fontsize=10)
save(fig, "downturn_scenario_multipliers.png")

# 3. Property-market softness by segment -------------------------------------
prop = pd.read_csv(CON / "property_cycle_panel.csv").sort_values("market_softness_score")
fig, ax = plt.subplots(figsize=(8.4, 5.2))
colors = [LEVEL_COLOR.get(b, BLUE) for b in prop.market_softness_band]
bars = ax.barh(prop.property_segment, prop.market_softness_score, color=colors, edgecolor="white")
for y, (v, st) in enumerate(zip(prop.market_softness_score, prop.cycle_stage)):
    ax.text(v, y, f" {v:.1f}  ({st})", va="center", fontsize=9)
ax.set_xlabel("market softness score (higher = softer / weaker demand)")
ax.set_title("Commercial property softness by segment (ABS approvals)")
ax.grid(axis="y", alpha=0)
save(fig, "property_market_softness.png")

# 4. Macro-derived segment PD multipliers by scenario ------------------------
mult = pd.read_csv(ROOT / "outputs" / "reports" / "macro_stress_segment_multipliers.csv")
scen_order = ["mild", "moderate", "severe"]
scen_color = {"mild": "#fee08b", "moderate": "#fdae61", "severe": "#d73027"}
segments = list(mult[mult.scenario == "severe"].sort_values("pd_multiplier").segment)
fig, ax = plt.subplots(figsize=(9.4, 5.4))
n = len(scen_order)
width = 0.8 / n
for i, scen in enumerate(scen_order):
    sub = mult[mult.scenario == scen].set_index("segment").reindex(segments)
    xs = [j + (i - (n - 1) / 2) * width for j in range(len(segments))]
    ax.bar(xs, sub.pd_multiplier, width=width, label=scen, color=scen_color[scen], edgecolor="white")
ax.set_xticks(range(len(segments)))
ax.set_xticklabels([s.replace("_", "\n") for s in segments], fontsize=9.5)
ax.axhline(1.0, color="#444", lw=1, ls="--")
ax.set_ylabel("PD multiplier (x base)")
ax.set_title("Macro-derived PD stress multipliers by portfolio segment")
ax.legend(title="scenario", frameon=False)
ax.grid(axis="x", alpha=0)
save(fig, "macro_scenario_paths.png")

print("\nAll figures written to", FIG)
