# Industry Analysis Report — Q1 2026

*Board Summary variant. Generated 2026-06-16.*



Macro and downturn overlays as of 2026-06-15. Property cycle data as of 2026-03-01.

This is a summary view for non-technical reviewers. Every table and chart in this document traces back to the canonical CSV contracts in `outputs/contracts/`.



## 1. Macro conditions for credit assessment & risk management

Before scoring any industry or deal, the engine reads where the economy and property markets currently sit - the conditions a credit team assesses against, and the base of every stress scenario in Section 2. The economy-wide headline rates (GDP, unemployment, CPI, WPI) are fetched live from the latest ABS releases (reading 'observed'), joining the live cash rate; a few series with no clean current public index are stated and flagged.

*Current macro & property conditions (live where a clean public series exists)*

| Condition | Current level | Reading | Source |
| --- | --- | --- | --- |
| GDP growth (real, YoY %) | 2.5 | observed | ABS 5206 National Accounts (Mar 2026, real SA, through-the-year) |
| Unemployment rate (%) | 4.3 | observed | ABS 6202 Labour Force (Mar 2026, seasonally adjusted) |
| Cash rate (%) | 4.35 | live | RBA F1 cash-rate table (+0.50pp 1y) |
| Inflation (CPI, YoY %) | 2.4 | observed | ABS 6401 CPI (Mar 2026 quarter, all groups, through-the-year) |
| Wage growth (WPI, YoY %) | 3.3 | observed | ABS 6345 Wage Price Index (Mar 2026 quarter, through-the-year) |
| House-price growth (YoY %) | 4 | stated | stated (ABS 6416 RPPI discontinued after Dec-2021; no current free public index) |
| Exchange rate (TWI, % change) | 0 | stated | RBA F11 exchange rates |
| Industry / sector output (YoY %) | 2 | stated | ABS 8155 Australian Industry + 5676 Business Indicators |
| Commercial-property prices (% change) | 0 | assumption | assumption |
| Vacancy rate (office, %) | 12 | assumption | assumption |
| CRE rents (% change) | 0 | assumption | assumption |
| CRE cap rates (%) | 6 | assumption | assumption |

Property-secured lending splits into residential and commercial. Residential house-price growth is a stated reading (the ABS RPPI was discontinued after Dec-2021). Commercial-property risk is read from real ABS non-residential building approvals - currently softest for offices, firmest for warehouses.

*Commercial property cycle by building type (ABS 8731 non-residential approvals)*

| Building type | Cycle stage | Softness (1 firm - 5 soft) | Approvals YoY % | Region-risk band |
| --- | --- | --- | --- | --- |
| Offices | downturn | 4.30 | -19.8 | High |
| Agricultural and aquacultural buildings | downturn | 3.90 | -27.0 | High |
| Commercial Buildings - Total | slowing | 3.80 | -49.7 | Elevated |
| Retail and wholesale trade buildings | slowing | 3.40 | +6.5 | Elevated |
| Total Non-residential | slowing | 3.35 | -15.9 | Elevated |
| Education buildings | slowing | 3.25 | -31.3 | Elevated |
| Aged care facilities | slowing | 3.20 | -22.0 | Elevated |
| Short term accommodation buildings | neutral | 3.10 | +112.0 | Medium |
| Health buildings | neutral | 2.40 | -36.0 | Medium |
| Industrial Buildings - Total | growth | 2.15 | +94.8 | Medium |
| Warehouses | growth | 1.70 | +108.5 | Medium |

Macro regime (as of 2026-06-15): cash-rate regime 'restrictive_rising', arrears Low / Improving, overall flag 'base'. The cash rate is 4.35% (+0.50pp over the year). A 'base' regime applies no recession overlay at current readings; Section 2 pre-computes the downturn impact.

## 2. Macro drivers for stress testing - per product and per industry

A macro-driven stress layer turns macroeconomic scenario paths into PD / LGD / EAD multipliers per portfolio segment, then rolls facility-level stress up to a portfolio expected-loss total — answering 'if the economy turns, how much worse do losses get, and for which portfolios?'.

Stress testing answers one question: if the economy turns bad, how much more does the bank lose? A scenario hurts borrowers and collateral, which shows up as higher PD (chance of default), LGD (loss if they default) and EAD (amount owed). This layer turns one scenario into ready-to-apply PD / LGD / EAD multipliers per portfolio segment and per industry - the input a downstream monitoring model multiplies onto its own facilities. It uses the simplest standard method (a multiplier map); a data-rich bank would use a statistical satellite model. Mild ~ two quarters of zero growth (Basel CRE36.51); severe is GFC-like but plausible (APS 220 s72); the roll-up takes no diversification benefit (APG 113 s92); figures are illustrative, to be validated in production (APS 220 s76).

*Macro scenario paths - stressed level by scenario*

| Variable | Unit | Source | base | mild | moderate | severe |
| --- | --- | --- | --- | --- | --- | --- |
| Cash rate (%) | % | RBA F1 cash-rate table | 4.35 | 4.6 | 4.85 | 5.1 |
| Commercial-property prices (% change) | % change | assumption | 0.0 | -7.0 | -15.0 | -28.0 |
| CRE cap rates (%) | % | assumption | 6.0 | 6.4 | 6.9 | 7.6 |
| CRE rents (% change) | % change | assumption | 0.0 | -4.0 | -9.0 | -16.0 |
| Exchange rate (TWI, % change) | % change | RBA F11 exchange rates | 0.0 | -5.0 | -10.0 | -15.0 |
| GDP growth (real, YoY %) | % yoy | ABS 5206 National Accounts (Mar 2026, real SA, through-the-year) | 2.5 | 0.7 | -0.8 | -2.8 |
| House-price growth (YoY %) | % yoy | stated (ABS 6416 RPPI discontinued after Dec-2021; no current free public index) | 4.0 | -4.0 | -11.0 | -21.0 |
| Industry / sector output (YoY %) | % yoy | ABS 8155 Australian Industry + 5676 Business Indicators | 2.0 | 0.0 | -2.0 | -5.0 |
| Inflation (CPI, YoY %) | % yoy | ABS 6401 CPI (Mar 2026 quarter, all groups, through-the-year) | 2.4 | 3.2 | 3.9 | 4.9 |
| Unemployment rate (%) | % | ABS 6202 Labour Force (Mar 2026, seasonally adjusted) | 4.3 | 5.5 | 6.8 | 8.3 |
| Vacancy rate (office, %) | % | assumption | 12.0 | 14.0 | 16.0 | 19.0 |
| Wage growth (WPI, YoY %) | % yoy | ABS 6345 Wage Price Index (Mar 2026 quarter, through-the-year) | 3.3 | 2.8 | 2.3 | 1.5 |

*Which macro drivers move which portfolio (illustrative)*

| Portfolio | Material macro drivers |
| --- | --- |
| Residential mortgages | unemployment, cash rate, wage growth, house prices |
| Credit cards | unemployment, wage growth, inflation |
| SME lending | GDP, unemployment, cash rate, sector output |
| Corporate lending | GDP, sector output, cash rate, exchange rate |
| Commercial property | property prices, vacancy, rents, cap rates, cash rate |
| Development finance | property prices, GDP, vacancy, cash rate |

*Macro-derived segment multipliers (PD / LGD / EAD)*

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

*Demonstration - facility roll-up to portfolio EL (illustrative demo book)*

| Scenario | Facilities | Base EL ($) | Stressed EL ($) | EL uplift x |
| --- | --- | --- | --- | --- |
| base | 6 | 79293.72 | 79293.72 | 1.0 |
| mild | 6 | 79293.72 | 153321.21 | 1.934 |
| moderate | 6 | 79293.72 | 256331.65 | 3.233 |
| severe | 6 | 79293.72 | 447755.57 | 5.647 |

> **Macro stress - scope and governance**
>
> Illustrative scenario design — not calibrated regulatory stress. Base levels are current values from the named ABS/RBA series; the four CRE variables (commercial-property prices, vacancy, rents, cap rates) and all elasticities are labelled assumptions. The portfolio roll-up is exposure-weighted with no diversification benefit. Reverse stress: the moderate scenario (EL uplift 3.23x) first breaches a 2.0x illustrative appetite ceiling. A bank normally builds separate models per material portfolio or a pooled model with portfolio/sector effects; this layer supplies the macro-credit linkage either consumes.

*Per-industry current-conditions drivers (feed the sector-output channel)*

| Industry | Employment YoY % | EBITDA margin % | Demand YoY % | Macro score (1-5) |
| --- | --- | --- | --- | --- |
| Accommodation and Food Services | +0.7 | 11.4 | +112 | 2.60 |
| Administrative and Support Services | +3.1 | 9.3 |  | 2.80 |
| Agriculture, Forestry and Fishing | -5.1 | 14.6 | -27 | 4.20 |
| Arts and Recreation Services | -5.8 | 13.5 | -46 | 3.60 |
| Construction | +1.5 | 10.2 | -16 | 3.20 |
| Education and Training | +5.6 | 11.7 | -31 | 3.40 |
| Electricity, Gas, Water and Waste Services | +12.3 | 21.0 |  | 2.00 |
| Health Care and Social Assistance | +3.7 | 16.7 |  | 2.80 |
| Information Media and Telecommunications | -4.8 | 20.0 |  | 2.60 |
| Manufacturing | -0.9 | 9.2 | +95 | 3.40 |
| Mining | -5.1 | 47.3 |  | 3.20 |
| Other Services | +7.1 | 5.3 |  | 2.20 |
| Professional, Scientific and Technical Services | +5.5 | 13.0 |  | 2.00 |
| Public Administration and Safety | -1.2 | 9.6 |  | 3.60 |
| Rental, Hiring and Real Estate Services | -15.1 | 40.9 |  | 2.60 |
| Retail Trade | -0.5 | 7.8 | +6 | 3.40 |
| Transport, Postal and Warehousing | +2.8 | 17.7 | -6 | 2.40 |
| Wholesale Trade | -8.7 | 6.1 | +108 | 3.40 |

## 3. How the industry credit-risk score is calculated

Each ANZSIC division gets a single 1 (low) - 5 (high) score that blends a structural view with a current-conditions view, then maps to a level and a PD overlay. Step 1 - macro score: mean of five 1-5 components from ABS business indicators (employment, margin level, margin trend, inventory, demand). Step 2 - blend: industry_base_risk_score = 0.55 x classification_risk_score + 0.45 x macro_risk_score. Step 3 - map to a five-band ladder (Low / Moderate-low / Medium / Moderate-high / Elevated) and a PD multiplier (0.90x - 1.15x).

Worked example - Agriculture, Forestry and Fishing: classification 4.12, macro 4.20 -> 0.55 x 4.12 + 0.45 x 4.20 = 4.16 -> Elevated -> 1.15x PD overlay. These are point-in-time, illustrative overlays - not calibrated PD estimates.

Headline: 5 of 18 industries score Elevated (as of 2026-06-15).

*Industry credit-risk scores (all ANZSIC divisions)*

| Industry | Classification | Macro | Base score | Level | PD overlay |
| --- | --- | --- | --- | --- | --- |
| Agriculture, Forestry and Fishing | 4.12 | 4.20 | 4.16 | Elevated | 1.15x |
| Mining | 3.88 | 3.20 | 3.57 | Elevated | 1.15x |
| Manufacturing | 3.50 | 3.40 | 3.46 | Elevated | 1.15x |
| Retail Trade | 3.25 | 3.40 | 3.32 | Elevated | 1.15x |
| Wholesale Trade | 3.12 | 3.40 | 3.25 | Elevated | 1.15x |
| Construction | 2.75 | 3.20 | 2.95 | Moderate-high | 1.10x |
| Arts and Recreation Services | 2.38 | 3.60 | 2.93 | Moderate-high | 1.10x |
| Accommodation and Food Services | 2.75 | 2.60 | 2.68 | Medium | 1.00x |
| Public Administration and Safety | 1.62 | 3.60 | 2.51 | Medium | 1.00x |
| Education and Training | 1.75 | 3.40 | 2.49 | Medium | 1.00x |
| Rental, Hiring and Real Estate Services | 2.38 | 2.60 | 2.48 | Medium | 1.00x |
| Transport, Postal and Warehousing | 2.50 | 2.40 | 2.46 | Medium | 1.00x |
| Administrative and Support Services | 2.12 | 2.80 | 2.43 | Medium | 1.00x |
| Information Media and Telecommunications | 2.12 | 2.60 | 2.34 | Medium | 1.00x |
| Other Services | 2.38 | 2.20 | 2.30 | Medium | 1.00x |
| Electricity, Gas, Water and Waste Services | 2.25 | 2.00 | 2.14 | Medium | 1.00x |
| Health Care and Social Assistance | 1.50 | 2.80 | 2.08 | Medium | 1.00x |
| Professional, Scientific and Technical Services | 1.75 | 2.00 | 1.86 | Moderate-low | 0.95x |
