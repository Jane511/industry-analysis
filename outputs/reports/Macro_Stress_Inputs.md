# Macro Stress Inputs — scenario paths, portfolio drivers, demo EL

> **Illustrative scenario design — not calibrated regulatory stress.** Base levels are current observed values from the named public series; per-scenario shocks and the portfolio elasticities are illustrative assumptions. Variables tagged `assumption` have no clean free public series. No diversification benefit is assumed in the portfolio roll-up.

## 1. Macro scenario paths (stressed levels by scenario)

| Variable | Unit | Source | base | mild | moderate | severe |
| --- | --- | --- | --- | --- | --- | --- |
| GDP growth (real, YoY %) | % yoy | ABS 5206 National Accounts | 1.8 | 0.0 | -1.5 | -3.5 |
| Unemployment rate (%) | % | ABS 6202 Labour Force | 4.1 | 5.3 | 6.6 | 8.1 |
| Cash rate (%) | % | RBA F1 cash-rate table | 3.85 | 4.1 | 4.35 | 4.6 |
| Inflation (CPI, YoY %) | % yoy | ABS 6401 CPI | 3.2 | 4.0 | 4.7 | 5.7 |
| Wage growth (WPI, YoY %) | % yoy | ABS 6345 Wage Price Index | 3.5 | 3.0 | 2.5 | 1.7 |
| House-price growth (YoY %) | % yoy | ABS 6416 Residential Property Price Index | 4.0 | -4.0 | -11.0 | -21.0 |
| Exchange rate (TWI, % change) | % change | RBA F11 exchange rates | 0.0 | -5.0 | -10.0 | -15.0 |
| Industry / sector output (YoY %) | % yoy | ABS 8155 Australian Industry + 5676 Business Indicators | 2.0 | 0.0 | -2.0 | -5.0 |
| Commercial-property prices (% change) | % change | assumption | 0.0 | -7.0 | -15.0 | -28.0 |
| Vacancy rate (office, %) | % | assumption | 12.0 | 14.0 | 16.0 | 19.0 |
| CRE rents (% change) | % change | assumption | 0.0 | -4.0 | -9.0 | -16.0 |
| CRE cap rates (%) | % | assumption | 6.0 | 6.4 | 6.9 | 7.6 |

_mild = technical-recession proxy (two consecutive quarters of ~zero GDP growth); moderate / severe are progressively deeper internally-consistent paths._

## 2. Portfolio → macro-driver sensitivity (illustrative weights, not betas)

| Segment | Parameter | Driver | Weight | Source |
| --- | --- | --- | --- | --- |
| residential_mortgages | PD | unemployment | 0.45 | ABS 6202 Labour Force |
| residential_mortgages | PD | cash_rate | 0.25 | RBA F1 cash-rate table |
| residential_mortgages | PD | wage_growth | 0.2 | ABS 6345 Wage Price Index |
| residential_mortgages | PD | inflation | 0.1 | ABS 6401 CPI |
| residential_mortgages | LGD | house_price_growth | 0.7 | ABS 6416 Residential Property Price Index |
| residential_mortgages | LGD | unemployment | 0.2 | ABS 6202 Labour Force |
| residential_mortgages | LGD | cash_rate | 0.1 | RBA F1 cash-rate table |
| residential_mortgages | EAD | cash_rate | 0.5 | RBA F1 cash-rate table |
| residential_mortgages | EAD | unemployment | 0.3 | ABS 6202 Labour Force |
| residential_mortgages | EAD | gdp_growth | 0.2 | ABS 5206 National Accounts |
| credit_cards | PD | unemployment | 0.5 | ABS 6202 Labour Force |
| credit_cards | PD | wage_growth | 0.3 | ABS 6345 Wage Price Index |
| credit_cards | PD | inflation | 0.2 | ABS 6401 CPI |
| credit_cards | LGD | unemployment | 0.5 | ABS 6202 Labour Force |
| credit_cards | LGD | inflation | 0.3 | ABS 6401 CPI |
| credit_cards | LGD | wage_growth | 0.2 | ABS 6345 Wage Price Index |
| credit_cards | EAD | gdp_growth | 0.4 | ABS 5206 National Accounts |
| credit_cards | EAD | cash_rate | 0.35 | RBA F1 cash-rate table |
| credit_cards | EAD | unemployment | 0.25 | ABS 6202 Labour Force |
| sme_lending | PD | gdp_growth | 0.35 | ABS 5206 National Accounts |
| sme_lending | PD | unemployment | 0.25 | ABS 6202 Labour Force |
| sme_lending | PD | cash_rate | 0.2 | RBA F1 cash-rate table |
| sme_lending | PD | industry_output | 0.2 | ABS 8155 Australian Industry + 5676 Business Indicators |
| sme_lending | LGD | commercial_property_prices | 0.45 | assumption |
| sme_lending | LGD | house_price_growth | 0.35 | ABS 6416 Residential Property Price Index |
| sme_lending | LGD | industry_output | 0.2 | ABS 8155 Australian Industry + 5676 Business Indicators |
| sme_lending | EAD | cash_rate | 0.4 | RBA F1 cash-rate table |
| sme_lending | EAD | gdp_growth | 0.35 | ABS 5206 National Accounts |
| sme_lending | EAD | industry_output | 0.25 | ABS 8155 Australian Industry + 5676 Business Indicators |
| corporate_lending | PD | gdp_growth | 0.4 | ABS 5206 National Accounts |
| corporate_lending | PD | industry_output | 0.3 | ABS 8155 Australian Industry + 5676 Business Indicators |
| corporate_lending | PD | cash_rate | 0.15 | RBA F1 cash-rate table |
| corporate_lending | PD | exchange_rate_twi | 0.15 | RBA F11 exchange rates |
| corporate_lending | LGD | industry_output | 0.45 | ABS 8155 Australian Industry + 5676 Business Indicators |
| corporate_lending | LGD | commercial_property_prices | 0.3 | assumption |
| corporate_lending | LGD | exchange_rate_twi | 0.25 | RBA F11 exchange rates |
| corporate_lending | EAD | cash_rate | 0.45 | RBA F1 cash-rate table |
| corporate_lending | EAD | gdp_growth | 0.35 | ABS 5206 National Accounts |
| corporate_lending | EAD | industry_output | 0.2 | ABS 8155 Australian Industry + 5676 Business Indicators |
| commercial_property | PD | commercial_property_prices | 0.3 | assumption |
| commercial_property | PD | vacancy_rate | 0.3 | assumption |
| commercial_property | PD | cre_rents | 0.2 | assumption |
| commercial_property | PD | cash_rate | 0.2 | RBA F1 cash-rate table |
| commercial_property | LGD | commercial_property_prices | 0.4 | assumption |
| commercial_property | LGD | cre_cap_rates | 0.35 | assumption |
| commercial_property | LGD | cre_rents | 0.25 | assumption |
| commercial_property | EAD | cash_rate | 0.5 | RBA F1 cash-rate table |
| commercial_property | EAD | vacancy_rate | 0.3 | assumption |
| commercial_property | EAD | commercial_property_prices | 0.2 | assumption |
| development_finance | PD | commercial_property_prices | 0.35 | assumption |
| development_finance | PD | gdp_growth | 0.25 | ABS 5206 National Accounts |
| development_finance | PD | vacancy_rate | 0.2 | assumption |
| development_finance | PD | cash_rate | 0.2 | RBA F1 cash-rate table |
| development_finance | LGD | commercial_property_prices | 0.55 | assumption |
| development_finance | LGD | cre_cap_rates | 0.25 | assumption |
| development_finance | LGD | cre_rents | 0.2 | assumption |
| development_finance | EAD | cash_rate | 0.45 | RBA F1 cash-rate table |
| development_finance | EAD | commercial_property_prices | 0.3 | assumption |
| development_finance | EAD | gdp_growth | 0.25 | ABS 5206 National Accounts |

## 3. Macro-derived segment multipliers (PD / LGD / EAD)

| Segment | Scenario | PD x | LGD x | EAD x |
| --- | --- | --- | --- | --- |
| residential_mortgages | base | 1.0 | 1.0 | 1.0 |
| residential_mortgages | mild | 1.4129 | 1.1523 | 1.0649 |
| residential_mortgages | moderate | 1.8357 | 1.2936 | 1.1291 |
| residential_mortgages | severe | 2.35 | 1.48 | 1.2 |
| credit_cards | base | 1.0 | 1.0 | 1.0 |
| credit_cards | mild | 1.4906 | 1.1267 | 1.0786 |
| credit_cards | moderate | 1.9886 | 1.2535 | 1.1533 |
| credit_cards | severe | 2.65 | 1.42 | 1.24 |
| sme_lending | base | 1.0 | 1.0 | 1.0 |
| sme_lending | mild | 1.5241 | 1.1521 | 1.0906 |
| sme_lending | moderate | 2.0259 | 1.3053 | 1.1757 |
| sme_lending | severe | 2.65 | 1.54 | 1.28 |
| corporate_lending | base | 1.0 | 1.0 | 1.0 |
| corporate_lending | mild | 1.4823 | 1.1549 | 1.0913 |
| corporate_lending | moderate | 1.9307 | 1.3156 | 1.177 |
| corporate_lending | severe | 2.5 | 1.54 | 1.28 |
| commercial_property | base | 1.0 | 1.0 | 1.0 |
| commercial_property | mild | 1.5409 | 1.18 | 1.0968 |
| commercial_property | moderate | 2.127 | 1.3973 | 1.1958 |
| commercial_property | severe | 2.95 | 1.72 | 1.32 |
| development_finance | base | 1.0 | 1.0 | 1.0 |
| development_finance | mild | 1.6664 | 1.195 | 1.1116 |
| development_finance | moderate | 2.3292 | 1.4273 | 1.2219 |
| development_finance | severe | 3.25 | 1.78 | 1.36 |

## 4. Demonstration — facility roll-up to portfolio EL (illustrative demo book)

| Scenario | Facilities | Base EL ($) | Stressed EL ($) | EL uplift x |
| --- | --- | --- | --- | --- |
| base | 6 | 79293.72 | 79293.72 | 1.0 |
| mild | 6 | 79293.72 | 153321.21 | 1.934 |
| moderate | 6 | 79293.72 | 256331.65 | 3.233 |
| severe | 6 | 79293.72 | 447755.57 | 5.647 |

**Reverse stress:** the moderate scenario (EL uplift 3.23x) first breaches a 2.0x illustrative appetite ceiling.

## 5. Governance

- Illustrative scenario parameters and elasticities, not calibrated regulatory stress. In production the paths would come from a macro model and the weights from estimated betas; both would be independently validated at least annually.
- No diversification benefit assumed in the portfolio roll-up (conservative).
- A bank normally develops **separate models per material portfolio** or a **pooled model with portfolio / sector effects**; this layer supplies the macro-credit linkage either approach consumes.
