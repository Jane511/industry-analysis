# --- business_cycle_panel null pattern diagnosis ---
path = Path("data/exports/business_cycle_panel.parquet")
if path.exists():
    df = pd.read_parquet(path)

    # Check that core scoring columns are fully populated
    scoring_cols = [
        "classification_risk_score",
        "macro_risk_score",
        "industry_base_risk_score",
        "industry_base_risk_level",
    ]
    for col in scoring_cols:
        if col in df.columns and df[col].isna().any():
            flag("business_cycle_panel", "HIGH",
                 f"core scoring column {col} has {df[col].isna().sum()} nulls — "
                 "downstream models will silently drop rows")

    # Check that null-bearing columns have their paired est_source flag
    null_cols = [c for c in df.columns if df[c].isna().any()]
    diagnostic_flag_cols = [c for c in df.columns if c.endswith("_est_source") or c.endswith("_source")]

    if null_cols and not diagnostic_flag_cols:
        flag("business_cycle_panel", "MEDIUM",
             f"{len(null_cols)} columns have nulls but no *_est_source flag columns exist "
             "to record whether data is missing by design")
    elif null_cols:
        # Show which null columns have or lack a source/flag companion
        null_summary = {c: int(df[c].isna().sum()) for c in null_cols}
        flag("business_cycle_panel", "LOW",
             f"null pattern: {null_summary} — diagnostic flag columns present: {diagnostic_flag_cols}")

    # Check whether nulls concentrate in service-sector rows (expected behaviour)
    if "industry" in df.columns and null_cols:
        service_keywords = [
            "health", "education", "financial", "professional",
            "information", "admin", "arts", "other services",
        ]
        null_rows = df[df[null_cols[0]].isna()]
        if "industry" in null_rows.columns:
            industries_with_nulls = null_rows["industry"].str.lower().tolist()
            service_hits = sum(
                1 for ind in industries_with_nulls
                if any(kw in ind for kw in service_keywords)
            )
            non_service = len(industries_with_nulls) - service_hits
            flag("business_cycle_panel", "LOW",
                 f"null rows span {len(industries_with_nulls)} industry entries; "
                 f"{service_hits} match service-sector keywords, {non_service} do not. "
                 f"Null concentration in services = expected ABS data gap.")