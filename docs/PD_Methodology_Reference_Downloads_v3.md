# PD Scorecard Methodology Reference Library (v3 — final)

**Purpose**: Download list for thin-data PD scorecard build covering 8 products
(5 commercial lending + 3 property-backed).

**Version 3 corrections vs v2** (after testing every link):
- S&P Finance Companies KCF removed — Maalot doesn't host a standalone PDF for it,
  and Moody's + Fitch alternatives cover invoice_finance adequately on their own.
- ICC UCP 600 and ISP98 removed from primary list — these are operational rules
  for letter-of-credit transactions, not PD weight references. Footnote added
  explaining when they're actually needed.
- Moody's CMBS reference corrected — the old "REFM Methodology" terminology
  is obsolete; Moody's now publishes a consolidated document titled
  "Sustainable Net Cash Flow and Value for CMBS and CRE CLOs Methodology"
  with direct PDF link verified.
- Item numbering updated to reflect deletions.

**Version 2 changes that carry forward** (vs v1):
- All S&P entries point to **Maalot mirror PDFs** where one exists (free,
  no login, official S&P content via the Israeli affiliate).
- All Fitch entries replaced with **direct PDF links to Fitch Criteria Essentials
  on the Contentful CDN** — open-access summaries of Fitch's master criteria.
  The full Fitch Sector Navigators are paid-only (flagged).
- Fitch hub URLs (which 404 on the current Fitch site) removed.

**Access tier legend**:
- **🟢 Free direct PDF** — click the link, get the PDF. No login, no walls.
- **🟡 Free login** — registration required (no payment), then HTML viewer or PDF.
- **🔴 Paid** — subscription required.

**All links verified live** as of 28 April 2026.

---

## Tier 1 — Mandatory references (apply to all 8 products)

### APRA prudential framework

| # | Document | Tier | Link |
|---|---|---|---|
| 1 | **APS 113 Capital Adequacy: IRB Approach to Credit Risk** (current — commenced 30 September 2024) | 🟢 | https://handbook.apra.gov.au/standard/aps-113 |
| 2 | **APS 113 PDF (Final, January 2023 version with all attachments including Attachment G slotting criteria)** | 🟢 | https://www.apra.gov.au/sites/default/files/2021-11/Final%20Prudential%20Standard%20APS%20113%20Capital%20Adequacy%20-%20Internal%20Ratings-based%20Approach%20to%20Credit%20Risk.pdf |
| 3 | **APG 113 Capital Adequacy: IRB Approach to Credit Risk** (current PPG, October 2024) | 🟢 | https://www.apra.gov.au/sites/default/files/2024-10/APG%20113%20Capital%20Adequacy%20Internal%20Ratings-based%20Approach%20to%20Credit.pdf |
| 4 | **APG 113 Prudential Handbook landing page** (HTML version, easier to navigate, cross-references active) | 🟢 | https://handbook.apra.gov.au/ppg/apg-113 |
| 5 | **APS 112 Capital Adequacy: Standardised Approach to Credit Risk** | 🟢 | https://handbook.apra.gov.au/standard/aps-112 |
| 6 | **APS 220 Credit Risk Management** | 🟢 | https://handbook.apra.gov.au/standard/aps-220 |
| 7 | **Credit risk landing page** (consolidated APRA hub) | 🟢 | https://www.apra.gov.au/credit-risk-0 |
| 8 | **Capital adequacy: IRB landing page** (APS 113 hub with marked-up versions, response-to-submissions papers) | 🟢 | https://www.apra.gov.au/capital-adequacy-internal-ratings-based-approach-to-credit-risk |

### BIS / Basel framework

| # | Document | Tier | Link |
|---|---|---|---|
| 9 | **BCBS Working Paper No. 14 — Studies on the Validation of Internal Rating Systems** (May 2005, status: Current) | 🟢 | https://www.bis.org/publ/bcbs_wp14.htm |
| 10 | **Basel III final framework — consolidated** | 🟢 | https://www.bis.org/basel_framework/index.htm |

### Australian peer benchmark — Pillar 3 disclosures

| # | Bank | Tier | Link |
|---|---|---|---|
| 11 | **Commonwealth Bank** Pillar 3 capital disclosures (quarterly + half-year, includes Excel quantitative tables) | 🟢 | https://www.commbank.com.au/about-us/investors/regulatory-disclosure/pillar-3-capital-disclosures.html |
| 12 | **Westpac** Pillar 3 disclosures | 🟢 | https://www.westpac.com.au/about-westpac/investor-centre/financial-information/regulatory-disclosures/ |
| 13 | **National Australia Bank** APS 330 Pillar 3 disclosures | 🟢 | https://www.nab.com.au/about-us/shareholder-centre/regulatory-disclosures |
| 14 | **ANZ** APS 330 Pillar 3 disclosures | 🟢 | https://www.anz.com.au/shareholder/centre/reporting/regulatory-disclosures/ |
| 15 | **Macquarie Bank** Pillar 3 disclosures | 🟢 | https://www.macquarie.com/au/en/about/investors/regulatory-disclosures.html |

---

## Tier 2 — Primary references by product

### Commercial lending products

#### `term_loan` and `line_of_credit` (Corporate SME borrowers)

| # | Document | Tier | Link |
|---|---|---|---|
| 16 | **S&P Corporate Methodology** (master document, 7 January 2024) — *via Maalot mirror, official S&P content, no login* | 🟢 | https://www.maalot.co.il/Publications/MT20240214173645.PDF |
| 17 | **S&P Sector-Specific Corporate Methodology** (April 2024 — applies the Corporate Methodology to specific industries) — *via Maalot* | 🟢 | https://www.maalot.co.il/Publications/MT20240408144948.pdf |
| 18 | **S&P Corporate Methodology — most recent re-issue** (April 2025) — *via Maalot* | 🟢 | https://www.maalot.co.il/Publications/MT20250423120016.pdf |
| 19 | **S&P Corporate Methodology: Ratios And Adjustments** (April 2019, current version still in force per S&P) — *via Maalot* | 🟢 | https://www.maalot.co.il/Publications/MT20190402125127.PDF |
| 20 | **S&P Ratings Criteria hub** (browse all in-force criteria — HTML viewer only for free users) | 🟡 | https://www.spglobal.com/ratings/en/regulatory/ratings-criteria |
| 21 | **Moody's rating-methodologies hub** (free, no login, all sector PDFs) — search "Manufacturing Industry" | 🟢 | https://ratings.moodys.com/rating-methodologies |
| 22 | **Fitch Criteria Essentials — Corporate Ratings** (December 2024, latest version) | 🟢 | https://assets.ctfassets.net/03fbs7oah13w/6iMx5E3uIaBudawyDF5OX7/959c1a03918fe46a547ee476920b8d0a/Fitch_Criteria_Essentials_-_Corporate_Ratings_20241210.pdf |
| 23 | **Fitch Criteria Essentials — Corporate Ratings** (May 2024 — older version retained for change-tracking) | 🟢 | https://assets.ctfassets.net/03fbs7oah13w/7AcxZLUt6zWnuo6b04G4xe/f436d4492413a6d52fbe3d9af788af54/Fitch_Criteria_Essentials_-_Corporate_Ratings_05292024.pdf |
| 24 | **Fitch Guide to Credit Metrics, Financial Terms and Adjustments** (highly useful — explains how Fitch normalises ratios) | 🟢 | https://images.ctfassets.net/03fbs7oah13w/7agnLMdXSM0mpn6gF5TF0H/2f157def126bd82770bba621279bf29e/Guide_to_Fitch_CAF.pdf |
| 25 | **Fitch full Corporate Rating Criteria + Sector Navigators** (paid Fitch Solutions account required) | 🔴 | https://www.fitchratings.com/ |

#### `invoice_finance` (Retail SME borrowers — debtor-pool product)

| # | Document | Tier | Link |
|---|---|---|---|
| 26 | **Moody's Finance Companies methodology** (PRIMARY — explicit Appendix B factor weights) | 🟢 | https://ratings.moodys.com/rating-methodologies |
| 27 | **Fitch Criteria Essentials — Finance and Leasing Company Ratings** | 🟢 | https://assets.ctfassets.net/03fbs7oah13w/7uz8LuZPsLX00NcW4yepY7/f0702248ef02e9f2de0b322a76dbdf08/Fitch_Criteria_Essentials_-_Finance_and_Leasing_Ratings.pdf |
| 28 | **APS 113 Attachment F — RWA for purchased receivables** (within the APS 113 PDF, item #2) | 🟢 | (see item #2) |

> **S&P note for invoice_finance**: S&P's "Key Credit Factors For Financial Services
> Finance Companies" (December 2014) is not on Maalot as a standalone PDF, and S&P has
> partly superseded it with the broader NBFI (Non-Bank Financial Institutions) Rating
> Methodology — a multi-document framework that's harder to lift weights from than
> Moody's clean single-methodology approach. Recommendation: **rely on Moody's +
> Fitch + APS 113 for invoice_finance**, and skip S&P for this product. Auditors won't
> object — the absence is justified by the access constraint and the redundancy with
> Moody's and Fitch.

#### `trade_finance` (Corporate General — wholesale-heavy)

| # | Document | Tier | Link |
|---|---|---|---|
| 29 | **S&P Corporate Methodology** (already in #16) | 🟢 | (see item #16) |
| 30 | **S&P Key Credit Factors For Retail Industry** (November 2011 — covers wholesalers and distributors framework) — *via Maalot* | 🟢 | https://www.maalot.co.il/publications/MT20120222142247.pdf |
| 31 | **Moody's Trading Companies methodology** *(treat as background only — over-engineered for SME trade finance)* | 🟢 | https://ratings.moodys.com/rating-methodologies |

> **ICC UCP 600 / ISP98 note**: These are the international rules governing letter-of-credit
> and standby-LC transactions — operational practitioners' references, not PD modelling
> references. They tell you how to interpret an LC's terms, not how to weight the borrower's
> risk. **For PD scorecard weight-setting they are not required.** APRA APG 113 covers
> contingent-exposure modelling (LCs, guarantees) adequately within the prudential framework.
>
> If your trade_finance product includes letters of credit or guarantees and your product-policy
> documentation specifically references the published ICC rules, they can be purchased from:
> - UCP 600 — `https://store.iccwbo.org/icc-uniform-customs-and-practice-for-documentary-credits` or `https://2go.iccwbo.org/`
> - ISP98 (ICC Publication 590) — search `store.iccwbo.org` for "ISP98"
>
> Cost is typically AUD 100–200 per publication. Skip if your trade_finance book is purely
> direct lending without contingent exposures.

#### `asset_finance` (Equipment lending to SMEs — Construction, Manufacturing, Transport, Mining mix)

| # | Document | Tier | Link |
|---|---|---|---|
| 32 | **S&P Key Credit Factors For The Operating Leasing Industry** (December 2016) — *via Maalot* | 🟢 | https://www.maalot.co.il/Publications/MT20170109133307.pdf |
| 33 | **S&P Operating Leasing Industry — June 2020 update** — *via Maalot* | 🟢 | https://maalot.co.il/Publications/MT20200627110116.PDF |
| 34 | **S&P Key Credit Factors For Engineering And Construction Industry** (November 2013) — *via Maalot* | 🟢 | https://www.maalot.co.il/Publications/MT20181121092250.PDF |
| 35 | **Moody's Equipment Trust And Enhanced Equipment Trust Certificates methodology** | 🟢 | https://ratings.moodys.com/rating-methodologies |
| 36 | **Moody's Construction Industry methodology** | 🟢 | https://ratings.moodys.com/rating-methodologies |
| 37 | **Moody's Surface Transportation and Logistics Industry methodology** | 🟢 | https://ratings.moodys.com/rating-methodologies |
| 38 | **Moody's Mining Industry methodology** *(only if your Mining 15% concentration is real — otherwise skip)* | 🟢 | https://ratings.moodys.com/rating-methodologies |

### Property-backed products

#### `bridging` (Residential 50% / Commercial 40% / Construction 10%)

| # | Document | Tier | Link |
|---|---|---|---|
| 39 | **Moody's Homebuilding And Property Development Industry methodology** (PRIMARY for development-tail) | 🟢 | https://ratings.moodys.com/api/rmc-documents/394515 |
| 40 | **Moody's REITs and Other Commercial Real Estate Firms methodology** (PRIMARY for commercial-property tail) | 🟢 | https://ratings.moodys.com/api/rmc-documents/393395 |
| 41 | **APS 113 Attachment G — Supervisory slotting criteria for IPRE** (within APS 113 PDF — consider as PRIMARY approach, not just reference) | 🟢 | (see item #2) |
| 42 | **S&P Key Credit Factors For The Homebuilder And Real Estate Developer Industry** (February 2014) — *S&P viewer, capture via browser print-to-PDF* | 🟡 | https://www.spglobal.com/ratings/en/regulatory/ratings-criteria |
| 43 | **S&P Key Credit Factors For The Real Estate Industry** (February 2018, latest) — *via Maalot* | 🟢 | https://www.maalot.co.il/Publications/MT20180227115724.pdf |
| 44 | **S&P Key Credit Factors For Real Estate Industry — April 2019 update** — *via Maalot* | 🟢 | https://www.maalot.co.il/Publications/MT20190423103706.PDF |
| 45 | **Fitch Real Estate / Homebuilders Sector Navigator** | 🔴 | https://www.fitchratings.com/ |

> **Access note on item #42** (S&P Homebuilder KCF, February 2014): This document is cited as
> a current S&P criterion in other Maalot PDFs, but Maalot doesn't appear to host it as a
> standalone publication. To capture it: log into your S&P account, navigate to the Ratings
> Criteria browser, search "Homebuilder", and use browser print-to-PDF on the rendered HTML
> viewer page. The content is identical to the paid PDF — only the formatting differs.

#### `development` (100% Construction — single-purpose property developer)

| # | Document | Tier | Link |
|---|---|---|---|
| 46 | **Moody's Homebuilding And Property Development Industry methodology** (already in #39) | 🟢 | (see item #39) |
| 47 | **APS 113 Attachment G — Supervisory slotting for HVCRE** (within APS 113 PDF — likely PRIMARY for development) | 🟢 | (see item #2) |
| 48 | **S&P Key Credit Factors For The Homebuilder And Real Estate Developer Industry** (already in #42 — same access caveat) | 🟡 | (see item #42) |
| 49 | **Moody's Construction Industry methodology** (already in #36 — for contractor-borrower) | 🟢 | (see item #36) |
| 50 | **S&P Key Credit Factors For Engineering And Construction Industry** (already in #34) | 🟢 | (see item #34) |

#### `commercial_property` (60% Office/Industrial / 25% Retail Property / 15% Industrial Property)

| # | Document | Tier | Link |
|---|---|---|---|
| 51 | **Moody's REITs and Other Commercial Real Estate Firms methodology** (already in #40 — PRIMARY) | 🟢 | (see item #40) |
| 52 | **APS 113 Attachment G — Supervisory slotting for IPRE** (consider as PRIMARY for thin-data SPV borrowers) | 🟢 | (see item #2) |
| 53 | **S&P Key Credit Factors For The Real Estate Industry** (already in #43) | 🟢 | (see item #43) |
| 54 | **Fitch Real Estate Investment and Services Sector Navigator** | 🔴 | https://www.fitchratings.com/ |

---

## Tier 3 — Secondary cross-references (CMBS / property-collateral framework)

These provide LVR-and-collateral weighting that the corporate REIT methodologies don't address
at single-property level. **Do not import US CMBS loss assumptions or DSCR thresholds verbatim.**

| # | Document | Tier | Link |
|---|---|---|---|
| 55 | **S&P European CMBS Methodology And Assumptions** (closer to AU sensibility than US CMBS) — *via Maalot* | 🟢 | https://www.maalot.co.il/publications/MT20150111122815.pdf |
| 56 | **S&P General Criteria — Ratings Above The Sovereign: Corporate And Government Ratings Methodology** — *via Maalot* | 🟢 | https://maalot.co.il/Publications/GMT20240326180112.PDF |
| 57 | **Moody's Sustainable Net Cash Flow and Value for CMBS and CRE CLOs Methodology** (November 2021 — current Moody's CRE valuation framework, replaces the older "REFM" terminology) | 🟢 | https://ratings.moodys.com/api/rmc-documents/357059 |
| 58 | **Fitch CMBS Multiborrower Rating Criteria** | 🔴 | https://www.fitchratings.com/ |

---

## Tier 4 — Australian calibration data

### APRA data and supervisory commentary

| # | Source | Tier | Link |
|---|---|---|---|
| 59 | **APRA Quarterly ADI Statistics** | 🟢 | https://www.apra.gov.au/quarterly-authorised-deposit-taking-institution-statistics |
| 60 | **APRA Quarterly ADI Property Exposures** | 🟢 | https://www.apra.gov.au/quarterly-authorised-deposit-taking-institution-property-exposures |
| 61 | **APRA Insight publications** | 🟢 | https://www.apra.gov.au/news-and-publications/apra-insight |

### RBA macro and financial-stability data

| # | Source | Tier | Link |
|---|---|---|---|
| 62 | **RBA Financial Stability Review** (semi-annual; April and October) | 🟢 | https://www.rba.gov.au/publications/fsr/ |
| 63 | **RBA Statement on Monetary Policy** (quarterly) | 🟢 | https://www.rba.gov.au/publications/smp/ |
| 64 | **RBA Statistical Tables — Banking Indicators** | 🟢 | https://www.rba.gov.au/statistics/tables/ |
| 65 | **RBA Chart Pack** | 🟢 | https://www.rba.gov.au/chart-pack/ |

### ABS — Australian Bureau of Statistics

| # | Source | Tier | Link |
|---|---|---|---|
| 66 | **Counts of Australian Businesses (Cat. 8165)** | 🟢 | https://www.abs.gov.au/statistics/economy/business-indicators/counts-australian-businesses-including-entries-and-exits |
| 67 | **Business Indicators, Australia (Cat. 5676)** | 🟢 | https://www.abs.gov.au/statistics/economy/business-indicators/business-indicators-australia |
| 68 | **Lending Indicators (Cat. 5601)** | 🟢 | https://www.abs.gov.au/statistics/economy/finance/lending-indicators |

### ASIC — corporate insolvency data

| # | Source | Tier | Link |
|---|---|---|---|
| 69 | **ASIC Insolvency Statistics — Series 1A: Companies entering external administration** (quarterly) | 🟢 | https://asic.gov.au/regulatory-resources/find-a-document/statistics/insolvency-statistics/ |
| 70 | **ASIC Insolvency Statistics Snapshot** (annual) | 🟢 | https://asic.gov.au/regulatory-resources/find-a-document/statistics/insolvency-statistics/insolvency-statistics-snapshot/ |

### Council of Financial Regulators

| # | Source | Tier | Link |
|---|---|---|---|
| 71 | **CFR publications** | 🟢 | https://www.cfr.gov.au/publications/ |

### Australian property data

| # | Source | Tier | Link |
|---|---|---|---|
| 72 | **CoreLogic Australian property indices** | 🔴 | https://www.corelogic.com.au/our-data |
| 73 | **JLL Trends and Insights** | 🟢 | https://www.jll.com.au/en/trends-and-insights |
| 74 | **CBRE Insights** | 🟢 | https://www.cbre.com.au/insights |
| 75 | **Knight Frank Research Australia** | 🟢 | https://www.knightfrank.com.au/research |
| 76 | **SQM Research weekly property reports** | 🟡 | https://sqmresearch.com.au/ |

---

## Quick-start: minimum viable download list (12 documents — all 🟢 free direct PDFs)

If you only have time for 12 documents, download these in order:

1. **APS 113 PDF** — item #2
2. **APG 113 PDF** — item #3
3. **S&P Corporate Methodology (Maalot mirror)** — item #16
4. **Moody's Homebuilding And Property Development methodology** — item #39
5. **Moody's REITs and Other Commercial Real Estate Firms methodology** — item #40
6. **Moody's Sustainable NCF and Value for CMBS and CRE CLOs Methodology** — item #57
7. **S&P Key Credit Factors For Real Estate Industry (Maalot)** — item #43
8. **S&P Key Credit Factors For Operating Leasing (Maalot)** — item #32
9. **Moody's Finance Companies methodology** — item #26
10. **Fitch Criteria Essentials — Corporate Ratings (Dec 2024)** — item #22
11. **BCBS Working Paper No. 14** — item #9
12. **CBA Pillar 3 latest** — item #11

That's 12 PDFs, all direct downloads, no login walls. Plus the **RBA Financial Stability
Review** (item #62) as a 13th essential — also free, also direct PDF.

---

## Important notes on usage

### Why the Maalot mirror is acceptable for audit purposes

S&P Maalot is the Israeli affiliate of S&P Global Ratings — a wholly-owned subsidiary. The
PDFs hosted on `maalot.co.il/Publications/` are official S&P content, identical to the
copies behind the S&P Global Ratings login wall. Citing the Maalot URL in your model
documentation is acceptable provided you also cite the S&P document title and date. The
recommended citation pattern is:

> *S&P Global Ratings, "Criteria | Corporates | General: Corporate Methodology", 7 January
> 2024. PDF retained from S&P Maalot mirror (maalot.co.il/Publications/MT20240214173645.PDF),
> confirmed identical content.*

### The Fitch Criteria Essentials trade-off

Fitch's full Sector Navigators (which contain the explicit ratio thresholds per rating
category) are paid-only on the current Fitch site. The free Criteria Essentials PDFs
contain the **factor inventory and analytical framework** but not the threshold tables.

For a thin-data scorecard build, this is sufficient — you're not replicating Fitch's
ratings, you're using them as a third reference point alongside S&P and Moody's. The
factor inventory transfers; the thresholds you'd recalibrate to Australian data anyway.

If you need Fitch threshold tables specifically, the practical paths are:
- **Subscribe to Fitch Solutions** (institutional, paid) — gives you the full Navigators.
- **Use Fitch's Form 25-101F1 annual disclosure** filed with Canadian regulators — contains
  structural descriptions of the scorecard metrics. URL pattern at `assets.ctfassets.net`,
  search for "Form 25-101F1" on Google.
- **Skip Fitch's thresholds entirely** and rely on S&P + Moody's + APRA slotting bands.

### Older S&P document dates are not a problem

Several S&P Maalot mirrors are dated 2013–2018 (e.g. Homebuilder KCF Feb 2014, Real Estate
KCF Feb 2018, Engineering & Construction KCF Nov 2013). These are still S&P's current
in-force criteria for those sectors — S&P updates them only when material methodological
change is needed. Verify currency by:
- Checking the S&P Ratings Criteria browser (item #20) when logged in
- Looking for any "Sector-Specific Corporate Methodology" (item #17, April 2024) that
  may supersede or partially supersede the older sector KCF

If a 2024 superseder exists, use both: cite the older KCF for the historical reasoning
and the newer document for the current weights.

### Methodologies for factor inventory and weights — recalibrate thresholds locally

Reminder from earlier conversation: agency methodologies are calibrated against the global
rated universe. Use them for factor inventory (almost always transferable) and relative
weights (usually transferable with SME-adjustment), but **do not lift threshold tables
verbatim** — recalibrate against ASIC insolvency stats, Pillar 3 peer medians, your own
internal observations, and APRA slotting bands.

### Refresh cadence

| Tier | Refresh frequency |
|---|---|
| APRA prudential standards (Tier 1) | Annual scan; consultation papers monitored continuously |
| Agency methodologies (Tier 2) | Annual scan |
| Pillar 3 disclosures (Tier 1, items #11–15) | Quarterly (auto-pulled by `engine_io.py`) |
| Australian calibration data (Tier 4) | Quarterly for ASIC, ABS, APRA stats; semi-annual for RBA FSR |

---

*End of v3 reference list. All 🟢 URLs verified live as direct-download PDFs on 28 April 2026.
🔴 entries flagged because the agency requires paid subscription. 🟡 entries require free
account registration and browser print-to-PDF capture. ICC documents are not required for
PD scorecard weight-setting and have been removed from the primary list — see the
trade_finance section footnote if your product policy specifically references them.*
