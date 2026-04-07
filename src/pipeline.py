from src.config import RAW_PUBLIC_DIR_ABS, PROCESSED_DIR, OUTPUT_CHARTS_DIR, OUTPUT_TABLES_DIR, DELIVERABLES_DIR
from src.build_foundation import build_foundation
from src.build_macro_view import build_macro_view
from src.build_benchmarks import build_industry_benchmarks
from src.build_portfolio import build_portfolio_proxy
from src.build_bottom_up import build_bottom_up
from src.build_scorecard import build_scorecard
from src.bank_practice import (
    build_industry_credit_appetite_strategy,
    build_industry_stress_test_matrix,
    build_industry_esg_overlay,
)
from src.credit_application import build_pricing_grid, build_policy_overlay, build_concentration_limits
from src.portfolio_monitoring import build_watchlist
from src.reporting import build_reporting_workbook, build_formal_chart_report
from src.output import save_csv


def run_pipeline() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

    # --- Stage 1-4: core risk scoring ---
    foundation = build_foundation(RAW_PUBLIC_DIR_ABS, PROCESSED_DIR)
    macro = build_macro_view(foundation, RAW_PUBLIC_DIR_ABS, PROCESSED_DIR)
    benchmarks = build_industry_benchmarks(macro, PROCESSED_DIR)
    save_csv(benchmarks, OUTPUT_TABLES_DIR / 'industry_generated_benchmarks.csv')
    borrower_compare = build_bottom_up(macro, benchmarks, PROCESSED_DIR)
    scorecard = build_scorecard(borrower_compare, PROCESSED_DIR, OUTPUT_TABLES_DIR)

    # --- Summary tables ---
    macro_out = macro[['industry', 'classification_risk_score', 'macro_risk_score',
                       'industry_base_risk_score', 'industry_base_risk_level',
                       'employment_yoy_growth_pct', 'ebitda_margin_pct_latest',
                       'gross_operating_profit_to_sales_ratio_latest',
                       'inventories_to_sales_ratio_latest',
                       'demand_proxy_building_type', 'demand_yoy_growth_pct',
                       'cash_rate_latest_pct', 'cash_rate_change_1y_pctpts']
                      ].sort_values('industry_base_risk_score', ascending=False)
    save_csv(macro_out, OUTPUT_TABLES_DIR / 'industry_base_risk_scorecard.csv')

    public_benchmark = macro[['industry', 'ebitda_margin_pct_latest', 'ebitda_margin_change_pctpts',
                              'gross_operating_profit_to_sales_ratio_latest',
                              'gross_operating_profit_to_sales_ratio_yoy_change',
                              'inventories_to_sales_ratio_latest',
                              'inventories_to_sales_ratio_yoy_change',
                              'employment_yoy_growth_pct',
                              'demand_proxy_building_type', 'demand_yoy_growth_pct']]
    save_csv(public_benchmark, OUTPUT_TABLES_DIR / 'industry_public_benchmarks.csv')

    appetite = build_industry_credit_appetite_strategy(macro, PROCESSED_DIR)
    save_csv(appetite, OUTPUT_TABLES_DIR / 'industry_credit_appetite_strategy.csv')

    stress = build_industry_stress_test_matrix(macro, PROCESSED_DIR)
    save_csv(stress, OUTPUT_TABLES_DIR / 'industry_stress_test_matrix.csv')

    esg_overlay = build_industry_esg_overlay(macro, PROCESSED_DIR)
    save_csv(esg_overlay, OUTPUT_TABLES_DIR / 'industry_esg_sensitivity_overlay.csv')

    # --- Stage 5: credit application ---
    cash_rate = float(macro['cash_rate_latest_pct'].iloc[0])
    pricing = build_pricing_grid(scorecard, cash_rate)
    save_csv(pricing, OUTPUT_TABLES_DIR / 'pricing_grid.csv')

    policy = build_policy_overlay(scorecard)
    save_csv(policy, OUTPUT_TABLES_DIR / 'policy_overlay.csv')

    portfolio = build_portfolio_proxy(macro, PROCESSED_DIR)
    save_csv(portfolio, OUTPUT_TABLES_DIR / 'industry_portfolio_proxy.csv')
    concentration = build_concentration_limits(macro, portfolio)
    save_csv(concentration, OUTPUT_TABLES_DIR / 'concentration_limits.csv')

    # --- Stage 6: portfolio monitoring ---
    watchlist = build_watchlist(macro)
    save_csv(watchlist, OUTPUT_TABLES_DIR / 'watchlist_triggers.csv')

    workbook_path = build_reporting_workbook(
        foundation,
        macro,
        benchmarks,
        borrower_compare,
        scorecard,
        pricing,
        policy,
        concentration,
        watchlist,
        stress,
        PROCESSED_DIR / 'industry_risk_reporting_workbook.xlsx',
        OUTPUT_TABLES_DIR / 'chart_table.csv',
    )

    build_formal_chart_report(
        workbook_path,
        OUTPUT_CHARTS_DIR,
        DELIVERABLES_DIR / 'industry_risk_formal_report.pdf',
        DELIVERABLES_DIR / 'chart_explanations.md',
    )
