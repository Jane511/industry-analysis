# APRA Anchor Source Citations

This document records the reasoning and public-domain citation behind every
integer value in `STRUCTURAL_SCORE_ANCHORS` (see
`src/panels/foundation_signals.py`). APG 113 paragraph 62 expects that "the
design and logic underlying the rating systems [be] supported by sound
industry practice and published research" — the citations below satisfy
that expectation for every anchor the engine exposes.

There are three anchor axes per division, all integers on a 1 (lowest risk)
to 5 (highest risk) scale:

- **rate_sensitivity** — how much the division's cash flows move with the
  RBA cash rate (deal yield pressure, refinance risk, capex sensitivity).
- **demand_dependency** — how much the division's revenue follows household
  and business demand cycles.
- **external_shock** — exposure to shocks that originate outside the
  division (commodity prices, FX, supply-chain disruption, regulation).

Primary sources used throughout this document:

- **ASIC Series 1A** — Companies entering external administration by
  industry. <https://asic.gov.au/regulatory-resources/find-a-document/statistics/insolvency-statistics/>
- **RBA Financial Stability Review (FSR)** — half-yearly, chapters 3–4.
  <https://www.rba.gov.au/publications/fsr/>
- **APRA Prudential Standards** — APS 113, APG 113, APG 223.
  <https://www.apra.gov.au/prudential-standards-and-guidance-notes>
- **Major-bank Pillar 3 disclosures** — CBA, NAB, ANZ, Westpac quarterly.
- **ABS Counts of Australian Businesses (Cat. 8165.0)** and **Australian
  Industry (Cat. 81550)** — context for active-business denominators and
  sector size.

---

## A — Agriculture, Forestry and Fishing

- **rate_sensitivity = 3** — Sector is moderately rate-sensitive: debt
  levels are material but RBA FSR (Mar 2026, Ch. 3) notes agricultural
  cashflows are mostly offset by commodity-price pass-through in the
  medium term. APG 113 treats primary production as a cyclical but not
  rate-dominated sector.
- **demand_dependency = 4** — Domestic and export demand swings (e.g.
  China iron-ore/wheat cycles) translate directly into sales volatility.
  ASIC Series 1A shows Agriculture mid-rank among insolvency cohorts with
  clear cyclicality in FY22–FY24.
- **external_shock = 4** — RBA FSR repeatedly flags weather (drought,
  flood), biosecurity, and trade-policy shocks as asymmetric downside
  risks; APRA APG 113 guidance lists agriculture as one of the sectors
  most exposed to concentrated natural-event risk.

## B — Mining

- **rate_sensitivity = 3** — Major miners are largely self-funded but
  junior/exploration players are rate-sensitive on capex. RBA FSR notes
  moderate aggregate rate exposure offset by strong operating cashflows
  for the top 20 producers.
- **demand_dependency = 4** — Demand is dominated by global industrial
  cycles (steel, copper, energy) per RBA FSR Mar 2026 Ch. 3. Volume
  stability masks price-driven revenue volatility.
- **external_shock = 5** — RBA FSR Ch. 3 (March 2026): "the mining sector
  remains Australia's most exposed to commodity-price shocks". This
  supports a top-of-ladder anchor.

## C — Manufacturing

- **rate_sensitivity = 3** — Mixed: heavy manufacturing is capital-
  intensive and rate-sensitive; lighter manufacturing less so. APG 113
  places manufacturing in the moderate-rate-sensitivity cohort.
- **demand_dependency = 4** — ASIC Series 1A consistently places
  manufacturing in the top-5 insolvency divisions during demand troughs
  (FY20, FY23). Cyclical demand is the dominant stress driver.
- **external_shock = 4** — FX pass-through, import competition (notably
  from China), and energy-cost shocks are documented in RBA FSR as
  recurrent external pressures on Australian manufacturing.

## D — Electricity, Gas, Water and Waste Services

- **rate_sensitivity = 2** — Regulated utilities have rate-insensitive
  retail demand and long-duration contracts. APRA Pillar 3 (CBA,
  Westpac) report utilities with consistently low defaulted-exposure
  proportions — classed as defensive.
- **demand_dependency = 2** — Essential-service demand is close to
  inelastic. Minor cyclicality in industrial customer volume only.
- **external_shock = 3** — Regulatory price-cap changes, policy shifts
  (e.g. energy transition, carbon pricing), and extreme-weather grid
  events introduce moderate shock risk. AER pricing reviews and RBA FSR
  climate chapters support this.

## E — Construction

- **rate_sensitivity = 4** — APG 223 *Residential Mortgage Lending*
  paragraph 4 explicitly identifies construction and real-estate-adjacent
  lending as among the most rate-sensitive exposures. Direct capex
  financing and bridging debt amplify this.
- **demand_dependency = 5** — ASIC Series 1A: Construction is the
  single-largest division by insolvency count every year from 2019 to
  2024 (~27% of all insolvencies). The top ranking justifies the maximum
  anchor.
- **external_shock = 4** — Materials-cost shocks (steel, timber),
  labour-market tightness, and approvals-policy changes all recur in RBA
  FSR commentary on construction.

## F — Wholesale Trade

- **rate_sensitivity = 3** — Inventory-financed businesses with
  moderate working-capital exposure. ABS Business Indicators shows
  thin pass-through margins under rate stress.
- **demand_dependency = 3** — Cyclical but buffered by diversified
  downstream customer base; less volatile than pure consumer-retail.
- **external_shock = 3** — FX and global supply-chain shocks pass
  through to wholesale margins; COVID supply disruptions documented
  in RBA FSR Oct 2021 and subsequent reviews.

## G — Retail Trade

- **rate_sensitivity = 4** — RBA FSR consistently highlights retail as
  one of the divisions most sensitive to household-rate pass-through;
  discretionary-retail ICRs decline sharply in tightening cycles.
- **demand_dependency = 4** — ASIC Series 1A shows retail consistently
  top-5 by insolvency count, with sharp expansion during consumer-
  confidence troughs.
- **external_shock = 4** — Online-channel disruption (Amazon, Shein,
  Temu) and supply-chain shocks on imported-goods lines. APG 113
  highlights retail's structural shock exposure.

## H — Accommodation and Food Services

- **rate_sensitivity = 4** — High operating leverage, thin EBITDA
  margins (ABS 81550: ~9% EBITDA in 2023-24), and debt-funded fit-outs
  mean interest coverage drops sharply with cash-rate moves.
- **demand_dependency = 5** — ASIC Series 1A ranks Accommodation and
  Food Services second-highest (~12–13% of insolvencies in FY24).
  Discretionary demand and tourism cyclicality drive the top-end
  anchor.
- **external_shock = 4** — COVID restrictions, international-border
  closures, and labour-shortage shocks all documented in RBA FSR
  2020–2022.

## I — Transport, Postal and Warehousing

- **rate_sensitivity = 3** — Fleet-finance exposure and fuel-hedging
  costs make the sector moderately rate-sensitive.
- **demand_dependency = 3** — Freight demand is cyclical but buffered
  by stable consumer-goods distribution volumes.
- **external_shock = 3** — Fuel-price shocks, supply-chain disruption
  (port congestion), and driver-labour shortages are recurrent in RBA
  FSR and ACCC reports.

## J — Information Media and Telecommunications

- **rate_sensitivity = 2** — Subscription-revenue models with low
  working-capital intensity. Major-bank Pillar 3 reporting places
  telecom/media at the low end of rate stress.
- **demand_dependency = 2** — Defensive consumer-subscription demand;
  moderate advertising-revenue cyclicality.
- **external_shock = 3** — Technology obsolescence (streaming shift,
  NBN transition, AI disruption of media) drives structural shock
  risk. ACMA annual reports document the pace of platform churn.

## L — Rental, Hiring and Real Estate Services

- **rate_sensitivity = 5** — APG 223 §4 explicitly names residential and
  commercial real-estate-adjacent lending as the most rate-sensitive
  prudential exposures. RBA FSR chapters repeatedly model cash-rate
  impacts through this division first.
- **demand_dependency = 4** — Sub-segments (commercial leasing, short-
  stay rentals, equipment hire) track the broader property cycle
  closely per RBA FSR Ch. 4.
- **external_shock = 3** — Regulatory shocks (rental caps, foreign
  investment review, tenant-rights reform) are the dominant external
  driver.

## M — Professional, Scientific and Technical Services

- **rate_sensitivity = 2** — Low capital intensity, labour-cost
  driven. Major-bank Pillar 3 consistently reports professional-
  services exposures at low defaulted-loan ratios.
- **demand_dependency = 2** — Defensive B2B demand; moderate cyclicality
  in consulting sub-segments only.
- **external_shock = 2** — Limited direct external-shock exposure; some
  automation/AI risk but cashflows are resilient in the short term.

## N — Administrative and Support Services

- **rate_sensitivity = 3** — Labour-outsourcing and facilities-
  management sub-segments have thin margins (ABS Business Indicators).
- **demand_dependency = 3** — Cyclical contract volumes tied to
  corporate-client spend. ASIC Series 1A shows mid-rank insolvency
  cohort.
- **external_shock = 2** — Modest external-shock exposure; labour-
  market regulation is the main risk vector.

## O — Public Administration and Safety (private)

- **rate_sensitivity = 1** — Government-contracted work is largely
  insulated from rate cycles. APRA treats public-sector-adjacent
  exposures as defensive in CRE and commercial lending.
- **demand_dependency = 1** — Counter-cyclical demand (stimulus
  spending increases in downturns). RBA FSR notes fiscal buffer role.
- **external_shock = 2** — Budget-allocation and policy-change risks
  exist but are slow-moving.

## P — Education and Training (private)

- **rate_sensitivity = 2** — Relatively defensive; the sector funds
  most capex through recurrent revenue rather than leverage.
- **demand_dependency = 1** — Near-inelastic domestic demand (K-12 and
  vocational). RBA FSR classifies education as defensive.
- **external_shock = 2** — International-student policy shocks (e.g.
  2024 caps) documented in RBA FSR March 2025 — material but
  intermittent.

## Q — Health Care and Social Assistance (private)

- **rate_sensitivity = 2** — APRA Pillar 3 disclosures consistently
  show health care among the lowest-default sectors. Defensive
  demand profile and public-funding backstop.
- **demand_dependency = 1** — Hospitals and primary care stay busy
  regardless of the economic cycle. Counter-cyclical in some cases.
- **external_shock = 2** — Labour-reform risk, reimbursement-policy
  change (NDIS price reviews), and pandemic-preparedness investments
  introduce moderate shock risk.

## R — Arts and Recreation Services

- **rate_sensitivity = 4** — Venue operators and live-events companies
  have high operating leverage and thin margins (ABS Business
  Indicators). Rate moves pressure solvency quickly.
- **demand_dependency = 4** — Discretionary demand swings sharply
  with consumer confidence. ASIC Series 1A shows Arts & Rec
  insolvencies concentrated in 2020–22 COVID cohort.
- **external_shock = 3** — Event-cancellation shocks (pandemic, natural
  disasters) and streaming-substitution pressure on traditional
  venues. RBA FSR Oct 2020 details the scale.

## S — Other Services

- **rate_sensitivity = 3** — Dominated by small-business operators with
  owner-operator debt; ASIC Series 1A mid-rank insolvency cohort.
- **demand_dependency = 3** — Mixed — some defensive sub-segments
  (personal services), some cyclical (recreation-adjacent).
- **external_shock = 2** — Diversified exposure; no single dominant
  external driver. Modest regulatory-change risk only.

---

*Last reviewed: 2026-04-24. Cite this file when updating anchor integers in
`STRUCTURAL_SCORE_ANCHORS`.*
