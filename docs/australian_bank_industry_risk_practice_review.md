# APRA Practice Alignment Review

## Research summary

Industry risk analysis for credit assessment typically operates within the APRA prudential framework together with organisation-specific portfolio controls.

This note should be read as a practice-alignment review, not a claim that the repository reproduces an internal institutional methodology. The repo aligns most closely on governance themes, sector overlays, monitoring, appetite framing, and stress/ESG concepts. It is materially less realistic on borrower-level analytics, internal grading, pricing, and concentration measurement because those require internal data and policy infrastructure.

### Core prudential expectations

- APRA APS 220 requires ADIs to maintain a credit risk appetite statement, credit risk management strategy, prudent policies across the full credit life-cycle, sound credit assessment and approval criteria, ongoing portfolio administration, and early identification and management of problem exposures.
- APRA APS 220 also requires willingness to accept credit risk to be described by exposure type, industry sector, geography, currency and maturity, with attention to risk/reward and sustainability of earnings.
- APRA APS 221 requires Board-approved policies for large exposures and risk concentrations, including consideration of counterparties, industries, countries and asset classes.
- APRA APG 220 describes sound practice including internal portfolio limits, sector and geographic concentration controls, internal credit risk grading, stress testing, covenants, collateral/guarantees, watch-lists and remedial management.

### Observed public practice references

- Public prudential and disclosure references commonly emphasise concentration controls across industries, countries and counterparties, ESG-sensitive sectors, delegated approval settings, and end-to-end credit lifecycle controls.

## Source links

- APRA APS 220 Credit Risk Management
  - https://handbook.apra.gov.au/standard/aps-220
- APRA APG 220 Credit risk management
  - https://handbook.apra.gov.au/ppg/apg-220
- APRA APS 221 Large Exposures
  - https://handbook.apra.gov.au/standard/aps-221
- Pillar 3 disclosure example, March 2025
  - https://www.westpac.com.au/content/dam/public/wbc/documents/pdf/aw/ic/wbc-pillar-3-report-march-2025.pdf
- ESG risk management example
  - https://www.nab.com.au/about-us/sustainability/reporting-policies-approach/esg-risk-management

## Coverage assessment of this repo

Covered before this review:

- public macro and industry signal ingestion
- industry-level scoring
- concentration limits
- pricing overlay
- policy overlay
- watchlist triggers

Missing before this review:

- explicit industry credit appetite strategy
- explicit industry stress testing matrix
- explicit ESG-sensitive sector overlay
- documented mapping between repo outputs and prudential practice references

## What was built

The repo now includes three additional practice-alignment outputs:

- `industry_credit_appetite_strategy.csv`
  - sector stance, tenor guidance, covenant intensity, collateral expectation, review frequency and ESG due diligence standard
- `industry_stress_test_matrix.csv`
  - sector stress outcomes across rate shock, demand shock, margin squeeze and employment decline scenarios
- `industry_esg_sensitivity_overlay.csv`
  - ESG-sensitive sector flags and associated credit policy overlays

These outputs are generated from the existing public-data sector risk results and align to the prudential themes above. They should be described as APRA-informed proxies rather than direct replicas of internal frameworks.

## Remaining limitations

The repo still does not replicate internal institution-only capabilities such as:

- actual internal borrower ratings and default history
- institution-specific delegated authorities and exception data
- observed portfolio exposure and utilisation by sector
- customer-level covenant compliance and arrears trends
- workout/provisioning data
- internal relationship-adjusted pricing, return hurdles, and cost-of-capital models
- borrower-level cash flow, security, sponsor, and structure analysis used in real credit approval
- severe-but-plausible stress testing linked to portfolio systems and management actions

Those would require internal systems or proprietary datasets rather than additional ABS/RBA downloads.
