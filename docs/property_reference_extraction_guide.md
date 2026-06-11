# Property reference extraction guide

This guide covers the manual quarterly extraction workflow for the property-reference layer's HTML- and PDF-only sources. The pattern matches the existing ASIC manual extraction. Each source has a target CSV path under `data/raw/public/<source>/` and a canonical schema. Loaders pick the latest file by naming convention (`<source>_<YYYYQN>.csv`); template files (`*_TEMPLATE.csv`) are skipped.

The build never fails when a manual extract is absent — loaders return an empty DataFrame with the canonical columns and the panel publishes nulls plus a `data_completeness_pct` value reflecting the gap.

---

## 1. Cotality free monthly Home Value Index

- **URL:** https://www.cotality.com/au/news-research/insights/home-value-index/
- **Cadence:** monthly. Aggregate the 3 months of a quarter's headline media releases into one CSV per quarter.
- **Target file:** `data/raw/public/cotality/cotality_hvi_<YYYYQN>.csv`
- **Schema:**

```
as_of_date, region, property_type, median_value_aud,
monthly_pct_change, quarterly_pct_change, annual_pct_change,
peak_to_trough_decline_pct, source_note
```

`region` accepts: `national`, `sydney`, `melbourne`, `brisbane`, `adelaide`, `perth`, `hobart`, `darwin`, `canberra`, `combined_capitals`, `combined_regional`. `property_type` accepts `combined`, `houses`, `units`.

Example values from a typical Cotality December release:

```csv
2025-12-31,sydney,combined,1180000,0.4,1.5,4.8,0.0,Cotality HVI Dec 2025 release
2025-12-31,melbourne,combined,790000,-0.1,-0.4,1.2,3.8,Cotality HVI Dec 2025 release
```

---

## 2. Cotality weekly auction clearance — quarterly aggregation

- **URL:** https://www.cotality.com/au/our-data/auction-results
- **Cadence:** weekly. Average the ~13 weekly observations within the quarter into one row per region.
- **Target file:** `data/raw/public/cotality/cotality_auction_clearance_<YYYYQN>.csv`
- **Schema:**

```
as_of_date, region, quarter_avg_clearance_rate_pct,
quarter_min_clearance_rate_pct, quarter_max_clearance_rate_pct,
total_auctions_held_count, source_note
```

`region` accepts the same set as Cotality HVI but with `tasmania` rather than `hobart` (Cotality bundles the auction figure at state level for Tas).

---

## 3. Domain Quarterly House Price Report

- **URL:** https://www.domain.com.au/research/house-price-report/
- **Cadence:** quarterly PDF.
- **Target file:** `data/raw/public/domain/domain_quarterly_<YYYYQN>.csv`
- **Schema:**

```
as_of_date, region_type, region, state, property_type,
median_price_aud, quarterly_pct_change, annual_pct_change,
median_days_on_market, median_vendor_discount_pct,
median_rental_yield_gross_pct, source_note
```

`region_type` is `capital` for capital-city aggregates and `suburb` for the per-suburb data Domain prints in the back of the PDF (typically the top 50–100 suburbs per capital). Capture only the suburbs Domain explicitly publishes — never extrapolate or impute.

---

## 4. SQM Research free headline

- **URL:** https://sqmresearch.com.au/
- **Cadence:** weekly headline numbers; aggregate to one row per capital per quarter.
- **Target file:** `data/raw/public/sqm/sqm_headline_<YYYYQN>.csv`
- **Schema:**

```
as_of_date, region, vacancy_rate_pct, vendor_discount_pct,
stock_on_market_count, asking_price_houses_aud,
asking_price_units_aud, source_note
```

`region` accepts the 8 capital city names (Title Case).

---

## 5. State government rental bond data (8 states/territories)

This is the **only** free source for genuine suburb-level rents — every Australian state and territory publishes it.

- **NSW** — NSW Fair Trading Rental Bond Board (https://www.fairtrading.nsw.gov.au/) → `data/raw/public/state_rental_bonds/nsw_rental_bonds_<YYYYQN>.csv`
- **VIC** — Department of Families, Fairness and Housing Rental Report (https://www.dffh.vic.gov.au/publications/rental-report) → `vic_rental_report_<YYYYQN>.csv`
- **QLD** — Residential Tenancies Authority (https://www.rta.qld.gov.au/about-the-rta/research-and-reports/median-rents-quarterly-data) → `qld_median_rents_<YYYYQN>.csv`
- **SA** — Consumer and Business Services SA → `sa_rental_<YYYYQN>.csv`
- **WA** — Department of Mines, Industry Regulation and Safety → `wa_rental_<YYYYQN>.csv`
- **TAS** — Consumer, Building and Occupational Services → `tas_rental_<YYYYQN>.csv`
- **NT** — Consumer Affairs NT → `nt_rental_<YYYYQN>.csv`
- **ACT** — ACT Civil and Administrative Tribunal → `act_rental_<YYYYQN>.csv`

**Canonical schema (every state's CSV uses the same columns):**

```
as_of_date, state, region_type, region, property_type, bedrooms,
median_weekly_rent_aud, sample_size_n, source_note
```

`region_type` accepts `suburb`, `sa3`, `sa4`, `postcode`. If a state's underlying publication doesn't break out a particular dimension (e.g. NT doesn't break out by bedrooms), use `combined` for that field and document it in `source_note`.

---

## 6. RBA Statistical Table E2 (Housing Loan Payments)

- **URL:** https://www.rba.gov.au/statistics/tables/xls/e02hist.xls
- **Cadence:** quarterly. Direct XLS download — no manual extraction required.
- **Target file:** `data/raw/public/rba/rba_e2_housing_loan_payments_<MMMYYYY>.xls`

---

## 7. RBA Financial Stability Review aggregates

- **URL:** https://www.rba.gov.au/publications/fsr/
- **Cadence:** semi-annual PDF.
- **Target file:** `data/raw/public/rba/rba_fsr_aggregates_<MMMYYYY>.csv`
- **Schema:**

```
as_of_date, metric, value, source_note, chart_reference
```

The `metric` field is a free-form string drawn from the FSR's chart titles. The macro context panel currently consumes:

- `total_household_debt_to_disposable_income`
- `national_arrears_30d_pct`
- `national_negative_equity_pct`
- `non_performing_housing_loans_pct`

`chart_reference` carries the FSR chart citation (e.g. `"FSR Oct 2025 Chart 4.5"`) for audit traceability.

---

## Summary of refresh cadence

| Source | Cadence | Manual / automated |
|---|---|---|
| Cotality HVI | Monthly → quarterly aggregation | Manual |
| Cotality auction clearance | Weekly → quarterly aggregation | Manual |
| Domain Quarterly | Quarterly | Manual (PDF extract) |
| SQM headline | Weekly → quarterly | Manual |
| State rental bonds (8) | Quarterly | Manual (per state) |
| RBA Table E2 | Quarterly | Automated (direct XLS download) |
| RBA FSR aggregates | Semi-annual | Manual (PDF extract) |
| ABS Cat. 6416.0 / 6432.0 / 5601.0 | Quarterly / monthly | Manual XLSX download |

Each refresh produces a new file alongside the prior one — the loader picks the lexicographically-latest non-template match.
