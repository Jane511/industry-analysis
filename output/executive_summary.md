# Executive Summary

This reporting pack now generates a separate working-capital layer for AR, AP, and inventory signals because those metrics can inform borrower scorecards today and can later support PD and LGD thinking. Public ABS and RBA datasets remain the source for the sector view, PTRS becomes the primary AR/AP benchmark source when available, and the remaining borrower, policy, and pricing fields remain explicit proxies or synthetic assumptions.

This is an APRA-informed portfolio demonstration rather than a replica of an Australian bank's internal industry risk methodology. The sector overlays, appetite framing, monitoring triggers, stress themes, and ESG treatment are bank-inspired, while borrower metrics, benchmark ratios, concentration exposure, and pricing remain transparent proxies or synthetic assumptions.

## Current Deliverables

- Workbook: `data/processed/industry_risk_reporting_workbook.xlsx`
- Chart table: `output/tables/chart_table.csv`
- Chart explanations: `output/chart_explanations.md`
- Formal PDF report: `output/industry_risk_formal_report.pdf`

## Current Sector View

- Highest current industry base risk score: **Agriculture, Forestry And Fishing** at **3.50**
- Lowest current industry base risk score: **Transport, Postal And Warehousing** at **2.14**
- Strongest employment growth: **Professional, Scientific And Technical Services** at **+5.5% YoY**
- Weakest employment growth: **Wholesale Trade** at **-8.7% YoY**

## Borrower and Portfolio View

- Highest borrower archetype score: **Agriculture, Forestry And Fishing Archetype** at **3.09**
- Lowest borrower archetype score: **Transport, Postal And Warehousing Archetype** at **2.20**
- Highest concentration utilisation: **Retail Trade** at **113.3%** of limit
- Current concentration breaches: **Retail Trade, Wholesale Trade**

## Working-Capital View

- Highest sector AR benchmark: **Manufacturing** at **33.7 days**
- Largest AR stress uplift: **Manufacturing** at **+14.3 days**
- Highest sector AP benchmark: **Manufacturing** at **33.7 days**
- Highest inventory benchmark: **Manufacturing** at **52.7 days** with **Moderate** stock-build risk
- Highest working-capital scorecard overlay: **Manufacturing** at **4.08**
- Highest working-capital PD overlay: **Manufacturing** at **3.58**
- Highest working-capital LGD overlay: **Manufacturing** at **3.89**
- Highest borrower working-capital PD metric score: **Manufacturing Archetype** at **2.65**

## Monitoring View

- Most watchlist triggers: **Agriculture, Forestry And Fishing** with **5**
- Largest average stress scenario uplift: **Demand shock** at **0.23** score points

## Report Use

The PDF is designed as a formal portfolio-style chart pack for credit and portfolio discussion. Each chart is tied to a workbook source sheet and includes a written explanation so the chart set can be reviewed without reopening the raw pipeline code.