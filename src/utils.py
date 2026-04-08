import re
import pandas as pd

def normalise_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()

def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))

def risk_band(score: float) -> str:
    if score <= 2.0:
        return "Low"
    if score <= 3.0:
        return "Medium"
    if score <= 4.0:
        return "Elevated"
    return "High"

def score_employment_growth(x: float) -> int:
    if pd.isna(x): return 3
    if x < 0: return 5
    if x < 1: return 4
    if x < 2.5: return 3
    if x < 4: return 2
    return 1

def score_margin_level(x: float) -> int:
    if pd.isna(x): return 3
    if x <= 1:
        if x < 0.08: return 5
        if x < 0.12: return 4
        if x < 0.18: return 3
        if x < 0.25: return 2
        return 1
    if x < 8: return 5
    if x < 12: return 4
    if x < 18: return 3
    if x < 25: return 2
    return 1

def score_margin_trend(x: float) -> int:
    if pd.isna(x): return 3
    if -1 <= x <= 1:
        if x < -0.03: return 5
        if x < -0.01: return 4
        if x < 0.01: return 3
        if x < 0.03: return 2
        return 1
    if x < -5: return 5
    if x < -2: return 4
    if x < 0: return 3
    if x < 2: return 2
    return 1

def score_inventory_ratio(x: float) -> int:
    if pd.isna(x): return 3
    if x > 0.70: return 5
    if x > 0.50: return 4
    if x > 0.30: return 3
    if x > 0.15: return 2
    return 1

def score_demand_growth(x: float) -> int:
    if pd.isna(x): return 3
    if x < -20: return 5
    if x < -5: return 4
    if x < 5: return 3
    if x < 20: return 2
    return 1

def score_gap_higher_is_worse(actual: float, benchmark: float) -> int:
    if pd.isna(actual) or pd.isna(benchmark): return 3
    gap = actual - benchmark
    if gap <= 0: return 1
    if gap <= benchmark * 0.15: return 2
    if gap <= benchmark * 0.35: return 3
    if gap <= benchmark * 0.60: return 4
    return 5

def score_gap_lower_is_worse(actual: float, benchmark: float) -> int:
    if pd.isna(actual) or pd.isna(benchmark): return 3
    gap = actual - benchmark
    if gap >= 5: return 1
    if gap >= 0: return 2
    if gap >= -5: return 3
    if gap >= -10: return 4
    return 5

def score_icr(actual: float, benchmark: float) -> int:
    if pd.isna(actual) or pd.isna(benchmark): return 3
    if actual >= benchmark + 1.5: return 1
    if actual >= benchmark: return 2
    if actual >= benchmark - 0.5: return 3
    if actual >= benchmark - 1.0: return 4
    return 5

def score_change_pct(value: float) -> float:
    if pd.isna(value):
        return 3.0
    value = float(value)
    if value <= -40:
        return 5.0
    if value <= -15:
        return 4.0
    if value < 10:
        return 3.0
    if value < 30:
        return 2.0
    return 1.0

def average_scores(*values: float) -> float:
    clean_values = [float(value) for value in values if pd.notna(value)]
    if not clean_values:
        return 3.0
    return round(sum(clean_values) / len(clean_values), 2)

def trend_label_from_score(score: float) -> str:
    if score <= 1.5:
        return "Strong expansion"
    if score <= 2.5:
        return "Improving"
    if score <= 3.5:
        return "Mixed"
    if score <= 4.25:
        return "Softening"
    return "Sharp contraction"

def classify_directional_trend(yoy_change: float, momentum_change: float | None = None) -> tuple[float, str]:
    score = average_scores(score_change_pct(yoy_change), score_change_pct(momentum_change))
    return score, trend_label_from_score(score)

def cycle_stage_from_score(score: float) -> str:
    if score <= 1.75:
        return "growth"
    if score <= 2.75:
        return "neutral"
    if score <= 4.0:
        return "slowing"
    return "downturn"
