# CoreLogic Engine Inventory

## Summary

Audit date: 2026-05-05

Exact search terms run from the repository root:

- `rg -n -i --hidden -g '!node_modules/**' -g '!.git/**' -g '!**/.venv/**' -g '!**/venv/**' -g '!**/env/**' "corelogic" .`
- `rg -n -i --hidden -g '!node_modules/**' -g '!.git/**' -g '!**/.venv/**' -g '!**/venv/**' -g '!**/env/**' "core logic" .`
- `rg -n -i --hidden -g '!node_modules/**' -g '!.git/**' -g '!**/.venv/**' -g '!**/venv/**' -g '!**/env/**' "rp data" .`

Exact CoreLogic-family matches:

- Documentation references: 69 line matches across 3 files
- Adapter stubs: 0
- Active integrations: 0
- Test references: 0
- Configuration references: 0

File count by category:

- Documentation reference files: 3
- Adapter stub files: 0
- Active integration files: 0
- Test reference files: 0
- Configuration reference files: 0

Checkpoint conclusion: the exact requested `CoreLogic`, `Core Logic`, and `RP Data` audit is clean of active engine code. No engine code currently loads, parses, or consumes data under those exact names.

Important related finding: CoreLogic announced a global rebrand to Cotality in March 2025. A separate search for `cotality` found active public/free Cotality HVI and auction-clearance loaders already in this engine. These are not the future paid CoreLogic canonical consumer adapter described in Phase 3e, but they should be treated as a boundary clarification item because Cotality is the current CoreLogic brand. Source for rebrand: https://www.cotality.com/press-releases/meet-cotality

## Documentation References

| File | Line | Context |
|---|---:|---|
| `docs/PD_Methodology_Reference_Downloads_v3.md` | 238 | Lists CoreLogic Australian property indices as a red-tier property data source. |
| `report update.md` | 85 | Calls out CoreLogic as a paid or gated source that should be explicitly listed as not captured or out of scope. |
| `phase_3e_corelogic_audit.md` | 1 | Phase 3e audit title for CoreLogic data scoping. |
| `phase_3e_corelogic_audit.md` | 3 | States the audit purpose: find existing CoreLogic references and scope data needed by the separate CoreLogic project. |
| `phase_3e_corelogic_audit.md` | 4 | States that implementation belongs in the separate CoreLogic project. |
| `phase_3e_corelogic_audit.md` | 5 | Defines the boundary that paid CoreLogic data should not be ingested in this engine. |
| `phase_3e_corelogic_audit.md` | 11 | Introduces CoreLogic references in the IPRE PD build-out methodology. |
| `phase_3e_corelogic_audit.md` | 13 | Identifies CoreLogic SA2 turnover as a Step 4 scorecard driver input. |
| `phase_3e_corelogic_audit.md` | 14 | Identifies CoreLogic property-segment loss data as a Step 8 validation benchmark. |
| `phase_3e_corelogic_audit.md` | 16 | Notes earlier discussion of CoreLogic property-price indices as out of scope for the engine. |
| `phase_3e_corelogic_audit.md` | 18 | States that CoreLogic has been referenced but not built into the engine. |
| `phase_3e_corelogic_audit.md` | 26 | Starts the requested repo search instructions. |
| `phase_3e_corelogic_audit.md` | 28 | Specifies the exact `corelogic` grep search. |
| `phase_3e_corelogic_audit.md` | 29 | Specifies the exact `core logic` grep search. |
| `phase_3e_corelogic_audit.md` | 30 | Specifies the exact `rp data` grep search. |
| `phase_3e_corelogic_audit.md` | 39 | Defines the active integration category for CoreLogic data. |
| `phase_3e_corelogic_audit.md` | 40 | Defines the test reference category for CoreLogic data. |
| `phase_3e_corelogic_audit.md` | 41 | Defines the configuration reference category for CoreLogic data. |
| `phase_3e_corelogic_audit.md` | 45 | Specifies this inventory output path. |
| `phase_3e_corelogic_audit.md` | 50 | Provides the target inventory heading. |
| `phase_3e_corelogic_audit.md` | 62 | Gives an example table row for an out-of-scope CoreLogic price-index reference. |
| `phase_3e_corelogic_audit.md` | 72 | Requires escalation if active CoreLogic integration exists. |
| `phase_3e_corelogic_audit.md` | 76 | Starts the CoreLogic data-needs scoping section. |
| `phase_3e_corelogic_audit.md` | 78 | States that Section B documents CoreLogic project data needs. |
| `phase_3e_corelogic_audit.md` | 80 | Defines Section B as the interface between this engine and the CoreLogic project. |
| `phase_3e_corelogic_audit.md` | 86 | Identifies residential capital-value indices as the primary CoreLogic data need. |
| `phase_3e_corelogic_audit.md` | 106 | Repeats the Step 4 need for CoreLogic SA2 turnover. |
| `phase_3e_corelogic_audit.md` | 116 | Repeats the Step 8 need for CoreLogic property-segment loss data. |
| `phase_3e_corelogic_audit.md` | 123 | Starts the expected CoreLogic interface format section. |
| `phase_3e_corelogic_audit.md` | 125 | States that the engine will consume CoreLogic data through a clean interface. |
| `phase_3e_corelogic_audit.md` | 129 | Describes CoreLogic project outputs as CSV or Parquet at a known location. |
| `phase_3e_corelogic_audit.md` | 131 | Names the future engine-side CoreLogic consumer adapter path. |
| `phase_3e_corelogic_audit.md` | 132 | Recommends a versioned CoreLogic project output directory. |
| `phase_3e_corelogic_audit.md` | 145 | Includes CoreLogic publication identifier in the canonical schema. |
| `phase_3e_corelogic_audit.md` | 146 | Includes CoreLogic publication date in the canonical schema. |
| `phase_3e_corelogic_audit.md` | 160 | Starts the CoreLogic project delivery requirements. |
| `phase_3e_corelogic_audit.md` | 162 | Frames the section as instructions for the CoreLogic project owner. |
| `phase_3e_corelogic_audit.md` | 164 | Requires the four CoreLogic subscription data categories. |
| `phase_3e_corelogic_audit.md` | 177 | Requires CoreLogic publication date vintage discipline. |
| `phase_3e_corelogic_audit.md` | 181 | Requires licensing constraints for CoreLogic data use. |
| `phase_3e_corelogic_audit.md` | 183 | Requires provenance sufficient for CoreLogic citation in MRC reporting. |
| `phase_3e_corelogic_audit.md` | 185 | Starts the section defining what the engine will not do with CoreLogic data. |
| `phase_3e_corelogic_audit.md` | 189 | States that the engine does not subscribe to CoreLogic. |
| `phase_3e_corelogic_audit.md` | 190 | States that the engine does not parse CoreLogic raw outputs. |
| `phase_3e_corelogic_audit.md` | 191 | States that the engine does not store CoreLogic raw data. |
| `phase_3e_corelogic_audit.md` | 192 | States that the engine does not redistribute CoreLogic data without licensing review. |
| `phase_3e_corelogic_audit.md` | 198 | States that the CoreLogic consumer adapter is not a Phase 3.D, 3.E, or 3.F deliverable. |
| `phase_3e_corelogic_audit.md` | 200 | Introduces the engine/CoreLogic project sequencing table. |
| `phase_3e_corelogic_audit.md` | 202 | Lists current audit work for CoreLogic references. |
| `phase_3e_corelogic_audit.md` | 204 | Lists provisional Phase 3.G engine adapter work. |
| `phase_3e_corelogic_audit.md` | 205 | Lists provisional Phase 3.H consumption of CoreLogic data. |
| `phase_3e_corelogic_audit.md` | 215 | Lists this inventory as a Section A deliverable. |
| `phase_3e_corelogic_audit.md` | 218 | Requires a checkpoint recommendation on whether active CoreLogic code exists. |
| `phase_3e_corelogic_audit.md` | 226 | Lists the CoreLogic data interface document as a Section B deliverable. |
| `phase_3e_corelogic_audit.md` | 227 | Requires communication to the CoreLogic project owner for sign-off. |
| `phase_3e_corelogic_audit.md` | 228 | Requires capturing the CoreLogic project owner's response. |
| `phase_3e_corelogic_audit.md` | 234 | Marks implementation of the CoreLogic consumer adapter out of scope. |
| `phase_3e_corelogic_audit.md` | 235 | Marks CoreLogic subscription ownership by this engine out of scope. |
| `phase_3e_corelogic_audit.md` | 236 | Marks CoreLogic raw-output parsing out of scope for this engine. |
| `phase_3e_corelogic_audit.md` | 237 | Marks building an internal redistributed CoreLogic copy out of scope. |
| `phase_3e_corelogic_audit.md` | 238 | Marks use of CoreLogic as a derivative-model calibration target out of scope without licensing review. |
| `phase_3e_corelogic_audit.md` | 244 | Repeats that active CoreLogic integration requires immediate escalation. |
| `phase_3e_corelogic_audit.md` | 246 | Requires negotiation if the CoreLogic project response conflicts with engine canonical patterns. |
| `phase_3e_corelogic_audit.md` | 253 | Lists this inventory file in the path summary. |
| `phase_3e_corelogic_audit.md` | 256 | Lists the CoreLogic data interface file in the path summary. |
| `phase_3e_corelogic_audit.md` | 257 | Lists the future response capture file in the path summary. |
| `phase_3e_corelogic_audit.md` | 260 | Lists the future engine CoreLogic consumer adapter path. |
| `phase_3e_corelogic_audit.md` | 261 | Lists the future CoreLogic consumer adapter test path. |
| `phase_3e_corelogic_audit.md` | 266 | States that the separate CoreLogic project is untouched by this audit. |

## Adapter Stubs

No adapter stubs were found for the exact requested CoreLogic search terms.

## Active Integrations

No active integrations were found for the exact requested CoreLogic search terms.

## Test References

No test references were found for the exact requested CoreLogic search terms.

## Configuration References

No configuration references were found for the exact requested CoreLogic search terms.

## Related Cotality Finding

Because CoreLogic has rebranded to Cotality, a supplementary `cotality` search was run to avoid missing the current brand name. This search found active public/free property-reference functionality:

| Category | Files | Context |
|---|---|---|
| Active related integration | `src/property_reference/load_cotality_free.py`; `src/panels/build_property_reference_panel.py`; `src/overlays/build_property_market_overlays.py` | Manual public/free Cotality HVI and auction-clearance extracts are loaded into the property reference panel and summarised into the residential overlay enrichment. |
| Configuration reference | `src/config.py`; `src/public_data/download_all_public.py` | Defines the raw public Cotality directory, manual file globs, source URLs, and URL routing. |
| Test reference | `tests/test_property_reference_loaders.py`; `tests/test_residential_overlay_no_longer_placeholder.py`; `tests/public_data/test_download_all_public.py` | Tests the public/free Cotality loader and downstream residential overlay enrichment behavior. |
| Documentation reference | `README.md`; `README_technical.md`; `PROJECT_OVERVIEW.md`; `docs/property_reference_extraction_guide.md` | Documents public/free Cotality HVI and auction-clearance staging as part of the property reference panel. |

Recommendation: keep the future paid CoreLogic/Cotality canonical consumer adapter separate from this existing public/free Cotality pathway unless the project owner explicitly decides to merge the boundaries. The current engine is clean of paid CoreLogic canonical ingestion, but it is not clean of all Cotality-branded references.
