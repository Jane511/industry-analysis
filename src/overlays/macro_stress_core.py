"""Macro-driven stress engine (codename MACRO-STRESS).

Turns a panel of macroeconomic scenario paths (config/macro_scenarios.yaml)
and a portfolio -> driver sensitivity matrix into **macro-derived PD / LGD /
EAD multipliers** per portfolio segment, and demonstrates facility-level and
portfolio-level stressed expected loss on the committed demo portfolio.

Boundary (see MACRO_STRESS_PROJECT_PLAN.md / repo README "Role in Portfolio
Stack"): this repo is a reference/overlay layer, **not a loan book**. The
exported contract (the scenario paths + the sensitivity matrix) is the product;
the demo expected-loss roll-up is an *illustrative demonstration* only, kept in
clearly separate functions so the boundary is unmistakable.

All numbers are ILLUSTRATIVE scenario design / illustrative elasticities — not
calibrated regulatory stress parameters or estimated betas. Variables and
weights tagged ``assumption`` have no clean free public series.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pandas as pd
import yaml

from src.config import CONTRACTS_DIR, OUTPUT_REPORTS_DIR, RAW_DIR, REPO_ROOT
from src.output import save_csv

CONFIG_PATH = REPO_ROOT / "config" / "macro_scenarios.yaml"
PARAMETERS = ("PD", "LGD", "EAD")
REVERSE_STRESS_THRESHOLD = 2.0  # illustrative demo appetite ceiling (EL uplift x)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_macro_config(path: Optional[Path] = None) -> dict[str, Any]:
    with (path or CONFIG_PATH).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def apply_live_macro_levels(cfg: dict) -> set[str]:
    """Overlay live ABS headline levels onto the config base levels, in place.

    Updates ``base_level`` + ``source_or_assumption`` for the macro variables
    that have a clean public series (GDP growth, unemployment, CPI, WPI) using
    :func:`download_macro_indicators.load_macro_indicators`. The scenario SHOCK
    deltas are left untouched, so the stress multipliers — which depend on the
    *relative* shock path (``shock_norm``), not the base level — are unchanged.
    Returns the set of variable keys that were overlaid (empty if no staged or
    cached file is available, in which case the committed config base levels
    stand).
    """
    try:
        from src.public_data.download_macro_indicators import load_macro_indicators

        live = load_macro_indicators()
    except Exception:
        return set()
    overlaid: set[str] = set()
    variables = cfg.get("variables", {})
    for key, info in live.items():
        if key in variables:
            variables[key]["base_level"] = float(info["value"])
            variables[key]["source_or_assumption"] = info["source"]
            overlaid.add(key)
    return overlaid


def _flatten(text: object) -> str:
    return " ".join(str(text or "").split())


def _oriented(shock: float, direction: str) -> float:
    """Orient a shock so an adverse move is positive (common stress scale)."""
    return shock if direction == "up" else -shock


# ---------------------------------------------------------------------------
# MS-1 — macro scenario paths
# ---------------------------------------------------------------------------

def build_macro_scenario_paths(cfg: Optional[dict] = None) -> pd.DataFrame:
    cfg = cfg or load_macro_config()
    scenarios = cfg["meta"]["scenarios"]
    rows: list[dict[str, Any]] = []
    for variable, body in cfg["variables"].items():
        direction = body["stress_direction"]
        base = float(body["base_level"])
        shocks = body["shocks"]
        severe_oriented = _oriented(float(shocks["severe"]), direction)
        for scenario in scenarios:
            shock = float(shocks[scenario])
            oriented = _oriented(shock, direction)
            shock_norm = (
                0.0 if severe_oriented == 0 else max(0.0, oriented / severe_oriented)
            )
            rows.append({
                "scenario": scenario,
                "variable": variable,
                "label": body["label"],
                "unit": body["unit"],
                "stress_direction": direction,
                "base_level": round(base, 4),
                "shock": round(shock, 4),
                "stressed_level": round(base + shock, 4),
                "shock_norm": round(shock_norm, 4),
                "source_or_assumption": body["source_or_assumption"],
                "macro_note": _flatten(body.get("macro_note", "")),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# MS-2 — portfolio -> macro-driver sensitivity matrix
# ---------------------------------------------------------------------------

def build_portfolio_macro_sensitivity(cfg: Optional[dict] = None) -> pd.DataFrame:
    cfg = cfg or load_macro_config()
    panel_vars = set(cfg["variables"].keys())
    rows: list[dict[str, Any]] = []
    for segment, params in cfg["portfolio_sensitivities"].items():
        for parameter, drivers in params.items():
            for driver, weight in drivers.items():
                if driver not in panel_vars:
                    raise ValueError(
                        f"sensitivity driver '{driver}' for {segment}/{parameter} "
                        "is not in the macro variable panel"
                    )
                rows.append({
                    "segment": segment,
                    "parameter": parameter,
                    "driver": driver,
                    "sensitivity_weight": round(float(weight), 4),
                    "driver_stress_direction": cfg["variables"][driver]["stress_direction"],
                    "source_or_assumption": cfg["variables"][driver]["source_or_assumption"],
                })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# MS-3 — multiplier engine + demo roll-up
# ---------------------------------------------------------------------------

def compute_segment_multipliers(
    cfg: Optional[dict] = None,
    *,
    paths: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """multiplier[s,p,k] = clamp(1 + intensity[p] * Σ_d w[s,p,d]*shock_norm[d,k])."""
    cfg = cfg or load_macro_config()
    paths = build_macro_scenario_paths(cfg) if paths is None else paths
    scenarios = cfg["meta"]["scenarios"]
    intensity = cfg["meta"]["parameter_intensity"]
    ceiling = cfg["meta"]["multiplier_ceiling"]
    betas = cfg.get("segment_beta", {})
    norm = {
        (row["scenario"], row["variable"]): float(row["shock_norm"])
        for _, row in paths.iterrows()
    }
    rows: list[dict[str, Any]] = []
    for segment, params in cfg["portfolio_sensitivities"].items():
        seg_beta = betas.get(segment, {})
        for scenario in scenarios:
            row: dict[str, Any] = {"segment": segment, "scenario": scenario}
            for parameter in PARAMETERS:
                drivers = params.get(parameter, {})
                weighted = sum(
                    float(weight) * norm[(scenario, driver)]
                    for driver, weight in drivers.items()
                )
                beta = float(seg_beta.get(parameter, 1.0))
                mult = 1.0 + float(intensity[parameter]) * beta * weighted
                mult = min(max(mult, 1.0), float(ceiling[parameter]))
                row[f"{parameter.lower()}_multiplier"] = round(mult, 4)
            rows.append(row)
    return pd.DataFrame(rows)


def build_demo_portfolio_stress(
    demo: pd.DataFrame,
    cfg: Optional[dict] = None,
    *,
    multipliers: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Facility-level stressed EL (illustrative demonstration only)."""
    cfg = cfg or load_macro_config()
    mult = compute_segment_multipliers(cfg) if multipliers is None else multipliers
    seg_map = cfg["demo_segment_map"]
    scenarios = cfg["meta"]["scenarios"]
    mult_idx = {(r["segment"], r["scenario"]): r for _, r in mult.iterrows()}
    rows: list[dict[str, Any]] = []
    for _, fac in demo.iterrows():
        seg_label = str(fac["segment"])
        canonical = seg_map.get(seg_label, "corporate_lending")
        base_pd, base_lgd, base_ead = float(fac["pd"]), float(fac["lgd"]), float(fac["ead"])
        base_el = base_pd * base_lgd * base_ead
        for scenario in scenarios:
            m = mult_idx[(canonical, scenario)]
            s_pd = min(base_pd * float(m["pd_multiplier"]), 1.0)
            s_lgd = min(base_lgd * float(m["lgd_multiplier"]), 1.0)
            s_ead = base_ead * float(m["ead_multiplier"])
            s_el = s_pd * s_lgd * s_ead
            rows.append({
                "facility_id": fac.get("facility_id", ""),
                "segment_demo": seg_label,
                "segment_canonical": canonical,
                "scenario": scenario,
                "base_pd": round(base_pd, 6),
                "base_lgd": round(base_lgd, 6),
                "base_ead": round(base_ead, 2),
                "base_el": round(base_el, 2),
                "stressed_pd": round(s_pd, 6),
                "stressed_lgd": round(s_lgd, 6),
                "stressed_ead": round(s_ead, 2),
                "stressed_el": round(s_el, 2),
                "el_uplift_x": round(s_el / base_el, 3) if base_el > 0 else 0.0,
            })
    return pd.DataFrame(rows)


def build_demo_portfolio_summary(facility_stress: pd.DataFrame) -> pd.DataFrame:
    """Portfolio-level roll-up: simple exposure sum, NO diversification benefit."""
    rows: list[dict[str, Any]] = []
    for scenario, group in facility_stress.groupby("scenario", sort=False):
        base = float(group["base_el"].sum())
        stressed = float(group["stressed_el"].sum())
        rows.append({
            "scenario": scenario,
            "n_facilities": int(len(group)),
            "portfolio_base_el": round(base, 2),
            "portfolio_stressed_el": round(stressed, 2),
            "portfolio_el_uplift_x": round(stressed / base, 3) if base > 0 else 0.0,
        })
    return pd.DataFrame(rows)


def reverse_stress_scenario(
    summary: pd.DataFrame, threshold: float = REVERSE_STRESS_THRESHOLD,
) -> str:
    """First scenario whose portfolio EL uplift breaches an illustrative ceiling."""
    breaching = summary[summary["portfolio_el_uplift_x"] >= threshold]
    if breaching.empty:
        return f"no scenario breaches a {threshold:.1f}x EL uplift on the demo book"
    first = breaching.iloc[0]
    return (
        f"the {first['scenario']} scenario (EL uplift "
        f"{first['portfolio_el_uplift_x']:.2f}x) first breaches a "
        f"{threshold:.1f}x illustrative appetite ceiling"
    )


def build_macro_context(
    cfg: Optional[dict] = None, *, observed_keys: Optional[set[str]] = None,
) -> pd.DataFrame:
    """Current macro-state snapshot: base-scenario readings + live cash rate.

    Replaces the legacy (orphaned, broken) macro_context_panel. One row per
    macro driver at its latest level, tagged by ``reading_type``:
      * ``live``       — fetched now (the RBA F1 cash rate),
      * ``observed``   — live ABS headline level fetched this run (GDP,
                         unemployment, CPI, WPI — see ``observed_keys``),
      * ``stated``     — current level cited from the named public series
                         (not auto-fetched in this reference layer),
      * ``assumption`` — no clean free public series.
    """
    cfg = cfg or load_macro_config()
    base = build_macro_scenario_paths(cfg)
    base = (
        base[base["scenario"] == "base"][
            ["variable", "label", "unit", "base_level", "source_or_assumption", "macro_note"]
        ]
        .rename(columns={"base_level": "current_level"})
        .reset_index(drop=True)
    )
    base["reading_type"] = base["source_or_assumption"].apply(
        lambda s: "assumption" if str(s).strip().lower() == "assumption" else "stated"
    )
    if observed_keys:
        base.loc[base["variable"].isin(observed_keys), "reading_type"] = "observed"

    # Overlay the live RBA F1 cash rate when the staged file is available;
    # otherwise keep the config base level (offline-safe).
    try:
        from src.public_data.download_rba_rates import load_cash_rate_summary

        cr = load_cash_rate_summary()
        live = round(float(cr["cash_rate_latest_pct"].iloc[0]), 2)
        chg = float(cr["cash_rate_change_1y_pctpts"].iloc[0])
        mask = base["variable"] == "cash_rate"
        base.loc[mask, "current_level"] = live
        base.loc[mask, "source_or_assumption"] = f"RBA F1 cash-rate table ({chg:+.2f}pp 1y)"
        base.loc[mask, "reading_type"] = "live"
    except Exception:
        pass

    return base[[
        "variable", "label", "unit", "current_level", "reading_type",
        "source_or_assumption", "macro_note",
    ]]


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def build_and_export_macro_stress(
    *,
    contracts_dir: Path = CONTRACTS_DIR,
    reports_dir: Path = OUTPUT_REPORTS_DIR,
    demo_path: Optional[Path] = None,
) -> dict[str, pd.DataFrame]:
    """Write the 2 macro-stress contracts + demo support artifacts.

    The human-readable macro-stress section is rendered into the main Board /
    Technical report (Section 9), not a standalone file.
    """
    cfg = load_macro_config()
    observed = apply_live_macro_levels(cfg)  # live ABS base levels (GDP/unemp/CPI/WPI)
    paths = build_macro_scenario_paths(cfg)
    sensitivity = build_portfolio_macro_sensitivity(cfg)
    multipliers = compute_segment_multipliers(cfg, paths=paths)

    demo = pd.read_csv(demo_path or (RAW_DIR / "demo_portfolio.csv"))
    facility = build_demo_portfolio_stress(demo, cfg, multipliers=multipliers)
    summary = build_demo_portfolio_summary(facility)

    contracts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    # Downstream contracts.
    save_csv(paths, contracts_dir / "macro_scenario_paths.csv")
    save_csv(sensitivity, contracts_dir / "portfolio_macro_sensitivity.csv")
    save_csv(build_macro_context(cfg, observed_keys=observed), contracts_dir / "macro_context.csv")
    # Supporting demo artifacts (not core contracts).
    save_csv(multipliers, reports_dir / "macro_stress_segment_multipliers.csv")
    save_csv(facility, reports_dir / "macro_stress_demo_portfolio.csv")
    save_csv(summary, reports_dir / "macro_stress_demo_summary.csv")
    return {
        "macro_scenario_paths": paths,
        "portfolio_macro_sensitivity": sensitivity,
        "segment_multipliers": multipliers,
        "demo_facility_stress": facility,
        "demo_summary": summary,
    }
