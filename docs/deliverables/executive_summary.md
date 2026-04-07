# Executive Summary

This reporting pack now uses a workbook-backed flow for charts and formal reporting. Public ABS and RBA datasets remain the source for industry metrics, while the following items are intentionally retained as hard-coded workbook inputs because they are not published directly in public sector datasets:

- sector debt / EBITDA benchmarks
- sector ICR benchmarks
- sector AR / AP day benchmarks
- borrower-level financial statements
- bank portfolio exposure by sector
- bank pricing and policy settings

This is an APRA-informed portfolio demonstration rather than a replica of an Australian bank's internal industry risk methodology. The sector overlays, appetite framing, monitoring triggers, stress themes, and ESG treatment are bank-inspired, while borrower metrics, benchmark ratios, concentration exposure, and pricing remain transparent proxies or synthetic assumptions.

## Current Deliverables

- Workbook: `data/processed/industry_risk_reporting_workbook.xlsx`
- Chart table: `output/tables/chart_table.csv`
- Chart explanations: `docs/deliverables/chart_explanations.md`
- Formal PDF report: `docs/deliverables/industry_risk_formal_report.pdf`

## Current Sector View

- Highest current industry base risk score: **Health Care and Social Assistance** at **3.32**
- Next highest: **Professional, Scientific and Technical Services** at **3.09**
- Lowest current industry base risk score: **Transport, Postal and Warehousing** at **1.95**
- Strongest employment growth: **Professional, Scientific and Technical Services** at **+5.5% YoY**
- Weakest employment growth: **Wholesale Trade** at **-8.7% YoY**

## Borrower and Portfolio View

- Highest borrower archetype score: **Health Care & Social Assistance Archetype** at **2.97**
- Lowest borrower archetype score: **Transport, Postal and Warehousing Archetype** at **2.09**
- Highest concentration utilisation: **Retail Trade** at **85.0%** of limit
- No sector currently breaches the concentration limits in the latest workbook-backed report

## Monitoring View

- Most watchlist triggers: **Agriculture, Forestry and Fishing** with **4**
- Other sectors with multiple triggers: **Wholesale Trade** and **Retail Trade**

## Report Use

The PDF is designed as a formal portfolio-style chart pack for credit and portfolio discussion. Each chart is tied to a workbook source sheet and includes a written explanation so the chart set can be reviewed without reopening the raw pipeline code.
