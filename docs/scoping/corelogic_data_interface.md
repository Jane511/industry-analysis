# CoreLogic Data Interface

Status: draft for CoreLogic project owner sign-off

This document defines the interface between the external benchmark engine and the separate CoreLogic project. The engine will not subscribe to CoreLogic, parse CoreLogic raw outputs, or redistribute CoreLogic data. The CoreLogic project owns sourcing, licensing, raw parsing, and canonical output production.

## Current Boundary

The Phase 3e inventory found no active engine integration under the exact `CoreLogic`, `Core Logic`, or `RP Data` search terms. It did find an active related Cotality public/free pathway, because CoreLogic rebranded to Cotality in March 2025 (source: https://www.cotality.com/press-releases/meet-cotality). That pathway loads manually staged public/free Cotality HVI and auction-clearance extracts for the property reference panel.

This interface is for the future paid CoreLogic/Cotality canonical output feed. It must remain separate from the existing public/free Cotality property-reference pathway unless both project owners approve a boundary change.

## Required Data Categories

### Residential Capital-Value Indices

Residential capital-value indices are the primary requirement because the property-backed bridging book is concentrated in residential security.

| Series | Granularity | Cadence | IPRE use |
|---|---|---|---|
| Hedonic dwelling price index | National, capital city, SA4 | Monthly | Exit-channel proxy for residential bridging loans; Step 4 driver and Step 8 validation context. |
| Houses vs units split | Capital city | Monthly | Asset-class differentiation for the residential bridging book. |
| 12-month percentage change | National, capital city, SA4 | Monthly | Direct exit-risk signal for 6-18 month bridging tenor. |
| Days on market | Capital city, SA4 | Monthly | Liquidity proxy for refinance or sale exit. |

### Commercial Property Indices

Commercial indices are secondary because they are slower and less granular, but they support commercial bridging context.

| Series | Granularity | Cadence | IPRE use |
|---|---|---|---|
| Commercial capital-value index | Asset class by capital city | Quarterly | Commercial bridging exit-channel proxy. |
| Commercial yields | Asset class by capital city | Quarterly | Cap-rate trend signal for commercial loan stress. |

Commercial asset classes: `office`, `retail`, `industrial`.

### SA2 Location Liquidity

SA2 liquidity metrics support the Step 4 project-location liquidity score.

| Series | Granularity | Cadence | IPRE use |
|---|---|---|---|
| SA2 turnover rate | SA2 | Quarterly | Scorecard driver input for project-location liquidity. |
| SA2 days on market | SA2 | Quarterly | Finer-grained liquidity proxy than capital city or SA4. |
| SA2 vendor discounting | SA2 | Quarterly | Local-market stress signal. |

### Property-Segment Loss Data

Loss and stress data support Step 8 validation of slot-implied PDs.

| Series | Granularity | Cadence | IPRE use |
|---|---|---|---|
| Property-segment realised loss rates | Asset class by geography | Annual or as published | Validation benchmark for slot-implied PDs. |
| Distressed-sale share | Capital city, SA4 | Quarterly | Exit-channel stress signal. |

## Canonical Output Contract

The CoreLogic project should publish canonical outputs to a versioned directory, for example:

```text
output/corelogic/{vintage_date}/corelogic_canonical.csv
output/corelogic/{vintage_date}/corelogic_canonical.parquet
```

The engine-side consumer adapter is a future Phase 3.G deliverable and should read only these canonical outputs. It should not parse raw CoreLogic files, reports, APIs, or subscription exports.

Future engine-side adapter path:

```text
ingestion/adapters/corelogic_consumer_adapter.py
```

### Required Columns

| Column | Type | Required | Notes |
|---|---|---:|---|
| `as_of_date` | date | yes | Observation date for the metric. |
| `series` | enum string | yes | Closed taxonomy value. Unknown series must raise. |
| `geography_level` | enum string | yes | `national`, `capital_city`, `sa4`, `sa2`, or agreed extension. |
| `geography_value` | string | yes | Human-readable name or official geography code. |
| `asset_class` | enum string nullable | yes | `houses`, `units`, `dwelling`, `office`, `retail`, `industrial`, or null where not applicable. |
| `metric` | enum string | yes | Closed metric taxonomy value. |
| `value` | decimal | yes | Numeric observation. |
| `unit` | string | yes | Examples: `index`, `pct`, `days`, `aud`, `rate`. |
| `source_publication` | string | yes | Publication or extract identifier. |
| `source_vintage` | date | yes | CoreLogic/Cotality publication date. |
| `source_url` | string nullable | no | Include when licence allows storing the URL. |
| `license_constraint` | string | yes | Short controlled description of permitted use and redistribution limits. |
| `provenance_note` | string nullable | no | Optional clarification for manually supplied or non-standard rows. |

### Series Taxonomy

Initial closed `series` values:

| Series | Description |
|---|---|
| `hedonic_dwelling_price_index` | Residential HVI or equivalent all-dwelling index. |
| `hedonic_house_price_index` | Residential houses index. |
| `hedonic_unit_price_index` | Residential units index. |
| `residential_days_on_market` | Residential days-on-market metric. |
| `commercial_capital_value_index` | Commercial capital-value index. |
| `commercial_yield` | Commercial yield or cap-rate metric. |
| `sa2_turnover_rate` | SA2 turnover-rate metric. |
| `sa2_days_on_market` | SA2 days-on-market metric. |
| `sa2_vendor_discounting` | SA2 vendor discounting metric. |
| `property_segment_realised_loss_rate` | Realised loss-rate benchmark by property segment. |
| `distressed_sale_share` | Distressed-sale share metric. |

### Metric Taxonomy

Initial closed `metric` values:

| Metric | Description |
|---|---|
| `value` | Raw index, rate, amount, or point-in-time value. |
| `monthly_pct_change` | Month-on-month percentage change. |
| `quarterly_pct_change` | Quarter-on-quarter percentage change. |
| `annual_pct_change` | 12-month percentage change. |
| `days_on_market` | Median or agreed days-on-market measure. |
| `turnover_rate` | Sales turnover rate. |
| `vendor_discount_pct` | Vendor discounting percentage. |
| `realised_loss_rate` | Realised loss-rate benchmark. |
| `distressed_sale_share` | Distressed-sale share percentage. |

Adding any new `series`, `metric`, `geography_level`, or `asset_class` value requires a coordinated contract change before the engine accepts the file.

## Cadence And Freshness

| Data category | Expected cadence |
|---|---|
| Residential price indices | Monthly |
| Residential days on market | Monthly |
| Commercial indices and yields | Quarterly |
| SA2 liquidity metrics | Quarterly |
| Distressed-sale share | Quarterly |
| Realised loss rates | Annual or as published |

Freshness rules:

- The engine reads the latest available vintage by default.
- A `vintage_filter` parameter should allow historical replay for backtesting.
- The engine must not synthesise dates or silently carry forward stale observations.
- If the requested vintage is missing, the adapter must raise a clear error.
- Every row must carry `source_vintage`; missing vintage metadata is a contract failure.

## CoreLogic Project Deliverables

The CoreLogic project should deliver:

1. The four required data categories listed above.
2. CSV or Parquet canonical files in the agreed versioned output directory.
3. Complete provenance and licensing metadata on every row.
4. A closed taxonomy manifest matching this document.
5. Refresh evidence for each production run, including source vintage, row counts, and validation status.
6. A written response to this interface specification captured in `docs/scoping/corelogic_interface_response.md`.

## Engine Responsibilities

The external benchmark engine will:

- Consume only the canonical output files from the CoreLogic project.
- Validate the schema, taxonomy, dates, and required provenance fields.
- Refuse unknown series or metrics.
- Refuse missing `source_vintage` values.
- Tag downstream rows with licensing constraints where CoreLogic-derived values are used.
- Cite CoreLogic/Cotality publication and vintage in any internal report that uses the values.

## Engine Non-Responsibilities

The external benchmark engine will not:

- Subscribe to CoreLogic/Cotality.
- Parse raw CoreLogic/Cotality subscription outputs.
- Store raw CoreLogic/Cotality data.
- Redistribute CoreLogic/Cotality values without licensing review.
- Use CoreLogic/Cotality values as a calibration target for an in-house derivative model without licensing review.

## Sign-Off Request

CoreLogic project owner should confirm:

- The required data categories are available under the relevant subscription.
- The proposed schema can be produced as written.
- The closed taxonomies are acceptable or required changes are listed.
- The cadence and no-synthetic-dates rule are acceptable.
- Licensing constraints can be captured at row level.
- Any redistribution or model-use restrictions are explicitly documented.
