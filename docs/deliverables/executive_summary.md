# Executive Summary

This reporting pack now uses a workbook-backed flow for charts and formal reporting. Public ABS and RBA datasets remain the source for industry metrics, while the following items remain explicit proxy or synthetic inputs because they are not published directly in the public sector datasets used here:

- sector debt / EBITDA benchmarks
- sector ICR benchmarks
- borrower-level financial statements
- bank portfolio exposure by sector
- bank pricing and policy settings

Sector AR and AP days now follow a cleaner public-data path. The repo can download the official PTRS publications, reconstruct `PTRS_MultiCycle_AR_Days_Model_Official.xlsx` automatically, and use those official payment-times tables as the primary AR/AP benchmark source. The fallback proxy formulas are only used when PTRS source files are unavailable.

Inventory risk now follows a stronger public-data method as well. Instead of treating inventory days as a simple annualised placeholder, the pipeline estimates inventory days from ABS quarterly inventories/sales ratios, derives a YoY change in those estimated days, and flags stock-build risk where inventories appear to be rising into weaker trading conditions.

This is an APRA-informed portfolio demonstration rather than a replica of an Australian bank's internal industry risk methodology. The sector overlays, appetite framing, monitoring triggers, stress themes, and ESG treatment are bank-inspired, while borrower metrics, benchmark ratios, concentration exposure, and pricing remain transparent proxies or synthetic assumptions.

## Current Deliverables

- Workbook: `data/processed/industry_risk_reporting_workbook.xlsx`
- Chart table: `output/tables/chart_table.csv`
- Chart explanations: `docs/deliverables/chart_explanations.md`
- Formal PDF report: `docs/deliverables/industry_risk_formal_report.pdf`

## Current Sector View

- Highest current industry base risk score: **Agriculture, Forestry and Fishing** at **3.50**
- Joint highest: **Manufacturing** at **3.50**
- Lowest current industry base risk score: **Transport, Postal and Warehousing** at **2.14**
- Strongest employment growth: **Professional, Scientific and Technical Services** at **+5.5% YoY**
- Weakest employment growth: **Wholesale Trade** at **-8.7% YoY**

## Borrower and Portfolio View

- Highest borrower archetype score: **Agriculture, Forestry and Fishing Archetype** at **3.09**
- Joint highest borrower archetype score: **Manufacturing Archetype** at **3.09**
- Lowest borrower archetype score: **Transport, Postal and Warehousing Archetype** at **2.20**
- Highest concentration utilisation: **Retail Trade** at **113.3%** of limit
- Current concentration breaches: **Retail Trade** and **Wholesale Trade**

## Monitoring View

- Most watchlist triggers: **Agriculture, Forestry and Fishing** with **5**
- Other sectors with multiple triggers: **Manufacturing**, **Wholesale Trade**, and **Retail Trade**

## Report Use

The PDF is designed as a formal portfolio-style chart pack for credit and portfolio discussion. Each chart is tied to a workbook source sheet and includes a written explanation so the chart set can be reviewed without reopening the raw pipeline code.
