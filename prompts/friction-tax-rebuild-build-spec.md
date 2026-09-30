# Friction Tax Rebuild: Build Spec

Status: DRAFT, not Gemini-cleared. No engine code written. Research and decisions: `prompts/friction-tax-rebuild-source-verification.md` (Sections 1 to 5 and "Decisions (Pete, 2026-09-30)" items 1 to 11). MOB reference: 13b FRICTION TAX REBUILD entry (`tools/_mob.txt:1505`). Every code reference below was read live on 2026-09-30.

## Open questions (Pete), up front

Resolved 2026-09-30 and folded into the design: a state set with no dollar channel returns a null estimate, receipts move to `private_output.friction_receipts` (Section 6), headcount below 1 returns null (Section 2), the state criteria move to `engine/data/state_criteria.py` (Section 4), the decision-time receipt stays inside the `FRICTION_DOLLARS_VISIBLE` branch, the bucket-mean fallback is removed, and the Nonprofit & Education rate is recomputed (Section 3). The share-path headcount bug is being fixed separately ahead of the rebuild.

1. **Headcount ceiling.** The intake clamps headcount to 1 through 1,000 (`web/components/DiagnosticFlow.tsx:53`, clamp at `:95` and `:62-63`) and displays 1,000 as "1000+". An organization of 1,200 or 5,000 therefore reaches the engine as 1,000 and is priced at 1,000 employees. The 1,200-employee example in Section 6b is outside what intake can send. Decide whether to lift the cap, or to state the limit on the output.
2. **Legal snapshot method.** The byte-identical test (Section 8) needs a committed baseline taken before the refactor. Confirm that the baseline is taken at the parent of the first refactor commit, stored under `tools/fixtures/`, and never regenerated.
3. **JOLTS annualization.** Table 22 (verified 2026-09-30) is an average monthly rate by its footnote. I found no annualized quits table (t18 to t21 returned no readable caption). The spec uses monthly x 12. Nonprofit & Education weights private educational services (3,344,880) and NAICS 813 (1,429,400), using the JOLTS "Other services" row (2.2) as the stand-in for 813, which JOLTS does not publish separately. Result 1.64.
4. **`inaction_cost_*`.** Recommend two lines, not a sum (Section 6).
5. **Qualifying margin (display).** Still open, display only, does not affect costing.
6. **One-employee organizations.** Intake allows headcount 1 (`engine/data/intake.py:54-55`). The formulas run, but a 1-person organization is outside every source's population.

## 1. Current compute path (live code) and disposition

| Piece | Where | Now | Disposition |
|---|---|---|---|
| `compute_friction_tax` | `engine/friction_tax.py:1877-2016`, callers `engine/contract.py:1125` (aggregate), `:466` (per state) | grid payroll x org scalar x state fraction x breadth loading x severity scalar, `high = low * 1.4` (`:1953-1993`) | REPLACE with the two-channel function (Section 2). Signature drops `severity_tier` and `org_type` |
| `STATE_MULTIPLIERS` | `engine/friction_tax.py:543`, asserts `:1830-1845` | 58 states, rubric scores mapped to 5% to 25% of payroll, no citation | REPLACE with scores-only table (Section 4) |
| Magnitude constants | `_R_MIN/_R_MAX` and `_FRACTION_MIN/_FRACTION_MAX` `:1846-1851`, `_MULTI_CHANNEL_SEVERITY_LOADING_K` `:1860`, `_attritional_fraction` `:1863` | rubric to fraction mapping, breadth loading | REMOVE |
| `SEVERITY_SCALAR` | `engine/friction_tax.py:75-81` | 0.6/1.0/1.4 | REMOVE (P6, Section 14 lock superseded once shipped) |
| `PAYROLL_BASELINE_GRID` | `:404`, 66 cells | bucket mean x wage | REMOVE. P = headcount x W computed directly |
| `HEADCOUNT_MIDPOINTS`, `HEADCOUNT_BUCKETS` | `:88`, `:124` | Census SUSB 2022 bucket means | KEEP for Legal only (`:4121`, Cluster 3). Friction no longer uses them |
| `resolve_headcount_bucket` | `:361`, called at `:1927` (friction), `:4389`, `:4527` (Legal) | int to bucket label, strings and non-numbers return None | KEEP unchanged for Legal. Friction stops calling it. Do not reintroduce string tolerance |
| `_INDUSTRY_WAGE_DATA` | `:230` (May 2023) | mean wage per engine industry, 11 keys | REPLACE with OEWS May 2025 (Section 3), new citation ids |
| `get_industry_wage` | `:345`, used only at `api/engine.py:284` | wage accessor | KEEP, returns May 2025 |
| `ORG_TYPE_SCALARS` | `:436` | 1.00 x5, Government 1.05 | REMOVE (Decision 11, build step 4) |
| Web share path | `web/components/DiagnosticFlow.tsx:916`, `web/app/api/share/create/route.ts:93` | sends a numeric string | Fixed separately ahead of the rebuild. See the share-path headcount fix |
| Ledger | `engine/contract.py:405-532`, `dollar_exposure` `:473-481` | single-state dollars | CHANGE: `dollar_exposure` dropped, add `channels` (the channels that state switches on) |
| Receipts | `engine/contract.py:693-757`, uses `STATE_MULTIPLIERS` at `:719`, channel labels `:588` | narrates grid, org scalar, loading, severity, 1.4x | REWRITE as per-channel inputs with vintages |
| Payload assembly | `engine/contract.py:1125-1150`, `:1184`, `:1191-1207`, `:1217-1218` | `friction_tax_estimate {low, high, currency, driving_factors}` | CHANGE (Section 6) |
| Condensed cost of one departure | `api/engine.py:260-294`, `:283-289` (wage x 0.50 to 0.75) | range | REPLACE with wage x 0.333 (P9), single value |
| Display switch | `web/lib/output-text.ts:157`, gates `:271`, `:385-389`, `:415`, `:419-423`, `web/components/PrivateOutput.tsx:378`, `:408`, `:437`, `:445`, `:458` | `FRICTION_DOLLARS_VISIBLE = false` | KEEP false until Gemini and Pete clear the rebuild. Flipping it is a public-number change (Tier 4) |
| Legal exposure | `engine/friction_tax.py:4317`, `:4508` | separate mechanism | KEEP unchanged |

## 2. Channels (two dollar channels, one receipt)

Notation: N = employees, W = all-occupation mean annual wage for the engine industry (OEWS May 2025), P = N x W. q = annual quit rate = JOLTS monthly rate x 12.

| Channel | Formula | Inputs |
|---|---|---|
| Engagement | P x 0.69 x 0.18 x (1 - q x 0.5) | 0.18: Gallup 2020 article. 0.69 = 1 minus Gallup engaged 31% (May 2026 indicator). 0.5 = f, the P2 partial-year factor, an assumption (exits spread evenly across the year, Decision 7). The (1 - q x 0.5) term discounts leavers' lost year |
| Turnover | P x q x 0.42 x 0.333 | 0.42 = Gallup preventable share (July 2024, verification doc Section 5). 0.333 = Work Institute (2017 Retention Report, low-wage derivation, Section 5). q = JOLTS 2025 |
| Decision time (receipt only) | no dollar value | McKinsey 2019: 37% of time on decisions, 58% of it ineffective. Text only. `W_m` and the 11-0000 share are removed from the engine design and stay in the verification doc as research |

Headcount rule (Decision 10, corrected 2026-09-30): N = the intake number when `isinstance(headcount, (int, float))` and N is at least 1 (Pete, 2026-09-30: below 1 returns null). The engine rule is the backstop, because `web/app/api/diagnostic/session/start/route.ts:22-23` checks only `typeof number` and `Number.isFinite` and accepts 0 and negatives, and `engine/main.py:220` defaults a missing value to 0. Anything else ("", a numeric string, None, 0, negative) is uncalibrated, so `friction_tax_estimate` is null. There is no bucket-mean fallback. A live-path review on 2026-09-30 found no path that supplies a bucket label:

| Path | Headcount supplied | Reference | Result |
|---|---|---|---|
| Path 1 session complete | number, validated only as finite | `web/app/api/diagnostic/session/start/route.ts:22-23`, `engine/main.py:220` | integer, OK. The route does not reject 0 or negative values, the intake UI clamps to 1 through 1,000 (`web/components/DiagnosticFlow.tsx:62-63`) |
| Self-select `/api/result` | number from the modal, or "" sentinel | `web/components/SelfSelectIntakeModal.tsx:82`, `web/lib/engine-client.ts:84` | integer, or uncalibrated on "" (by design) |
| Condensed | none, friction is never computed | `engine/main.py:1075-1078` | not applicable |
| Dev preview and fixture picker | "" in the intake echo only, payload is stored | `web/app/(site)/dev/diagnostic-preview/[id]/page.tsx:62`, `web/components/DiagnosticFixturePicker.tsx:189` | not applicable |
| Share `/api/share/create` | numeric string | `web/components/DiagnosticFlow.tsx:916`, `web/app/api/share/create/route.ts:93` | uncalibrated today. Fixed separately ahead of the rebuild. See the share-path headcount fix |

Vintages (every figure):

| Figure | Source | Vintage | Verification status |
|---|---|---|---|
| 18% of salary, not-engaged | Gallup, "Increase Productivity at the Lowest Possible Cost" | 2020 article | Verification doc Section 1a |
| 31% engaged (NE = 0.69) | Gallup Global Indicator: Employee Engagement (gallup.com/394373), 31% engaged and 17% actively disengaged | May 2026 | Verification doc Section 5 |
| 42% preventable | Gallup, Tatel and Wigert, "42% of Employee Turnover Is Preventable but Often Ignored" (gallup.com/workplace/646538) | July 2024 | Verification doc Section 5. Self-reported by voluntary leavers. The 2019 figure was 52% |
| 33.3% of salary per voluntary exit | Work Institute | 2017 Retention Report, derived from $5,506 on an $8/hour ($16,640) employee. Current method 33.3% of base salary (about 11% direct, 22% indirect) | Verification doc Section 5. Low-wage derivation applied to all salaries |
| Quits rates by industry | BLS JOLTS Table 22, annual average quits rates, not seasonally adjusted | 2025 (release shows 2026 M01) | Verified by Claude Code 2026-09-30 |
| W by industry | BLS OEWS national 3-digit NAICS file `nat3d_M2025_dl.xlsx` | May 2025 | Verified, recomputed mean |
| 37% and 58% | McKinsey "Decision making in the age of urgency" | April 2019, survey Feb 2018, n=1,259 | Verification doc Section 4 |

## 3. Input tables

| Engine industry | W, May 2025 (replaces `:230`) | W now (May 2023) | JOLTS 2025 monthly quits rate (proposed row) | q (x12) |
|---|---:|---:|---|---:|
| Professional Services | $108,640 | $102,670 | 2.3 Professional and business services | 27.6% |
| Healthcare & Life Sciences | $71,770 | $67,320 | 2.0 Health care and social assistance | 24.0% |
| Financial Services | $100,842 | $94,150 | 1.3 Finance and insurance | 15.6% |
| Technology | $115,030 | $108,110 | 1.3 Information | 15.6% |
| Manufacturing | $69,131 | $64,440 | 1.4 Manufacturing | 16.8% |
| Retail & Hospitality | $42,024 | $39,651 | 3.37, Retail trade 2.6 and Accommodation and food services 4.2 weighted by OEWS employment | 40.4% |
| Nonprofit & Education | $69,984 | $57,770 | 1.64, private educational services 1.4 (3,344,880) and Other services 2.2 standing in for NAICS 813 (1,429,400), weighted by OEWS May 2025 employment | 19.7% |
| Government & Public Sector | $80,290 | $74,410 | 0.8 Government | 9.6% |
| Construction | $72,146 | $67,430 | 1.8 Construction | 21.6% |
| Transportation & Warehousing | $64,331 | $59,320 | 2.2 Transportation, warehousing, and utilities | 26.4% |
| Other | $67,977 | $63,446 | 2.2 Total private (Decision 9) | 26.4% |

W (May 2025) is the employment-weighted mean of the 3-digit NAICS all-occupation wages in the mapping committed in the verification doc Section 2b, computed 2026-09-30, not a published BLS sector wage.

## 4. Option A: where the channel switches live

Decision 4: a state switches a channel on when its criterion score is above 0. The mapping of criteria to channels is `turnover` to Turnover, `productivity` to Engagement, `decision_quality` to the decision-time receipt. No magnitude survives: no fractions, compounding, severity scalar, or raw score.

Adopted home (Pete, 2026-09-30): new `engine/data/state_criteria.py`, `STATE_CRITERIA: dict[str, StateCriteria]` with four integer fields per state (`turnover`, `productivity`, `decision_quality`, `legal`), values copied from the current `STATE_MULTIPLIERS[state].criteria[k].score`. Reasons:
- `legal` must survive (`engine/friction_tax.py:2172-2176`, `:4166-4170`) and Legal/Compliance must not depend on a friction module's internals.
- The 1,300-line literal at `:543-1828` leaves `engine/friction_tax.py`, which matches where other registries live (`engine/data/states.py`).
- `engine/contract.py:35` and `:719` import from the new module instead.

Switch rule over the identified set: a channel is on if any identified state scores above 0 on it. Channels are never stacked or scaled by state count. The receipt rule today is the same test (`engine/contract.py:724`).

Does `decision_quality` still gate the receipt? Yes, recommended. The decision-time receipt appears when any identified state scores above 0 on it (49 of 58 states). It carries no dollar figure and cites McKinsey 2019 with its stated limit (senior-skewed sample, larger than PRV3's clients).

Switch coverage of the 58 states (computed 2026-09-30): turnover, productivity and decision quality all above 0 for 35, turnover and productivity only 5, turnover and decision quality 9, productivity and decision quality 4, turnover only 4, decision quality only 1 (`paper_shield`).

## 5. How severity and state affect a result

Severity does not move the dollar figure (Decision 4). The dollar total is a function of industry, headcount, and which channels the identified states switch on. The same industry and headcount with the same switches always gives the same figure. The lead state's severity tier still drives everything outside the friction figure (severity display, `engine/contract.py:957`). `excess` is null because P4 leaves no cited basis for one (Decision 2).

## 6. Payload and every web consumer that changes

New shape (point estimate, Decision 6):

`friction_tax_estimate: { currency, typical_baseline: { total, channels: [ { channel, amount, inputs: [ { name, value, source, vintage } ] } ] }, excess: null, driving_factors }`. The decision-time receipt is a driving factor with no `amount`. `low` and `high` are removed. `friction_tax_estimate` is null when uncalibrated or when no dollar channel is selected (for example only `paper_shield` identified). Receipts, including the decision-time receipt, move to a sibling `private_output.friction_receipts` so they can render when the estimate is null (adopted 2026-09-30). They still render only inside the `FRICTION_DOLLARS_VISIBLE` branch (`web/components/PrivateOutput.tsx:437-445`).

Engine (Python): `engine/contract.py:1137-1149` (build), `:693-757` (receipts), `:405-532` (ledger, drop `dollar_exposure`, add `channels`), `:1191-1207` (`_cost_parts` and `inaction_cost_*`), `:35` and `:719` (import), `api/engine.py:283-289` (condensed).

Web consumers that change (all read live):
- `web/lib/types.ts:147-153` (`FrictionTaxEstimate`, removes `low`/`high`), `:178-182` (`FrictionTaxLedgerEntry.dollar_exposure`), `:377`, `:384`, `:520` (payload fields), `:581` (`inaction_cost_*`).
- `web/lib/engine-client.ts:147-148` (engine response types), `:525` (`condensed_financial_range`).
- `web/lib/output-renderer.ts:32-39` (`FrictionTax`: `low`, `high`, `severityScalar`, `calibrationComplete`) and `:120` (`payload.friction_tax_estimate`).
- `web/lib/output-text.ts:170-209` (`groupLedgerRows`, `higherEstimate` read `dollar_exposure`), `:386-415` (ledger and receipts lines), `:419-423` (`money(friction.low, friction.high)` in the cost comparison).
- `web/components/PrivateOutput.tsx:171`, `:384` (`group.dollar_exposure`), `:445` (receipts source moves to `friction_receipts`), `:458`.
- `web/components/ReportDetails.tsx:72`, `:88-90` (`rangeText(friction.low, friction.high)`).
- `web/lib/dev-diagnostic-preview.ts:8`, `:43`.
- `web/lib/diagnostic-completion.ts:197-198`, `web/app/api/result/route.ts:181-182`, `web/app/api/share/create/route.ts:189` (pass-through, type changes only).
- `web/components/DiagnosticFixturePicker.tsx:163` (sets null, likely no change).
- Condensed: `web/app/api/diagnostic/condensed/answer/route.ts:155`, `web/components/CondensedOutput.tsx:130` (range to single value).
- `inaction_cost_*` (`engine/contract.py:1191-1207`, `web/lib/output-text.ts:419-423`, `web/components/PrivateOutput.tsx:457`): recommend two lines (typical-loss point estimate, tail-risk legal range) instead of a sum, since one is a point and the other a range. Open (question 8).
- Display stays hidden (`web/lib/output-text.ts:157`). Call 1 and Call 2 keep the no-dollar rule (`engine/output_synthesis.py:50`).

## 6b. Worked figures (two channels, actual headcount, May 2025 inputs)

f = 0.5, NE = 0.69, q = JOLTS monthly x 12.

| Employees / industry | W | Quit rate (monthly, annual) | Payroll | Engagement | Turnover | Total | Eng % | Turn % | Total % of payroll |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 12 / Retail & Hospitality | $42,024 | 3.37, 40.4% | $504,288 | $49,979 | $28,497 | $78,477 | 9.9% | 5.7% | 15.6% FLAG |
| 12 / Other | $67,977 | 2.20, 26.4% | $815,724 | $87,940 | $30,119 | $118,059 | 10.8% | 3.7% | 14.5% |
| 60 / Construction | $72,146 | 1.80, 21.6% | $4,328,760 | $479,568 | $130,771 | $610,339 | 11.1% | 3.0% | 14.1% |
| 60 / Government & Public Sector | $80,290 | 0.80, 9.6% | $4,817,400 | $569,602 | $64,681 | $634,283 | 11.8% | 1.3% | 13.2% |
| 175 / Technology | $115,030 | 1.30, 15.6% | $20,130,250 | $2,305,163 | $439,205 | $2,744,368 | 11.5% | 2.2% | 13.6% |
| 175 / Professional Services | $108,640 | 2.30, 27.6% | $19,012,000 | $2,035,432 | $733,889 | $2,769,321 | 10.7% | 3.9% | 14.6% |
| 400 / Nonprofit & Education | $69,984 | 1.64, 19.7% | $27,993,600 | $3,134,788 | $770,281 | $3,905,070 | 11.2% | 2.8% | 13.9% |
| 400 / Manufacturing | $69,131 | 1.40, 16.8% | $27,652,400 | $3,145,936 | $649,734 | $3,795,670 | 11.4% | 2.3% | 13.7% |
| 800 / Healthcare & Life Sciences | $71,770 | 2.00, 24.0% | $57,416,000 | $6,275,339 | $1,927,248 | $8,202,588 | 10.9% | 3.4% | 14.3% |
| 800 / Transportation & Warehousing | $64,331 | 2.20, 26.4% | $51,464,800 | $5,548,194 | $1,900,237 | $7,448,431 | 10.8% | 3.7% | 14.5% |
| 1,200 / Financial Services | $100,842 | 1.30, 15.6% | $121,010,400 | $13,857,191 | $2,640,224 | $16,497,416 | 11.5% | 2.2% | 13.6% |

The 1,200-employee row is outside what intake can send today (open question 1). Totals run 13.2% to 15.6% of payroll. One profile exceeds the 15% flag line (Retail & Hospitality, driven by a 40.4% annual quit rate). Percent of payroll does not depend on headcount, only dollars do.

What the benchmarks do and do not show:
- **The engagement channel's only benchmark is Gallup's own worked example** (verification doc Section 1a: 10,000 x 67% x $50,000 x 18% = $60.3M on $500M payroll, 12.06%). That is circular. The channel applies Gallup's formula, so landing at 9.9% to 11.8% against Gallup's 12.06% confirms arithmetic, not magnitude. No independent check of the engagement magnitude was found.
- Turnover has no independent payroll-percentage benchmark either. The SHRM 50% to 200% of salary range (`prompts/friction-tax-unit-decision.md:16`) is a per-exit cost and is not comparable.
- Old engine range, for orientation only: 5% to 25% of payroll before the severity scalar (`prompts/friction-tax-state-multiplier-methodology.md:48`).

## 7. Demographic Applicability Filter (`prompts/demographic-applicability-filter-protocol.md`)

Intake fields: headcount (integer, minimum 1, `engine/data/intake.py:54-62`), industry (11 values, `:283`), org type (6 values, `:296`), jurisdictions. Extremes tested: 1 to 12 employees, 1,200+ employees, Government, Nonprofit & Education, Retail & Hospitality, Technology.

| Source | Assumption | Eligibility boundary (what I could establish) | Extremes | Status |
|---|---|---|---|---|
| Gallup 18% and engaged 31% | An average not-engaged US employee costs 18% of salary at any employer | US workforce, not segmented by employer size or industry in the verification doc material | 12 employees: Gallup's share is not testable for a single small team. Government and nonprofit: US sample includes them, not confirmed from source | Partly unverified |
| Gallup 42% preventable (July 2024) | Share of voluntary exits that were preventable | Self-reported by leavers (their own view of preventability), not an employer record | Unknown by size and industry | Self-report limit |
| Work Institute 33.3% | Cost per voluntary exit is a flat 33.3% of salary | Low-wage derivation (2017 Retention Report, $8/hour basis). Gallup's same July 2024 article gives role tiers: about 200% of salary for leaders and managers, 80% technical, 40% frontline | High-wage end: Technology ($115,030), Professional Services ($108,640), Financial Services ($100,842) are where a flat 33.3% is most likely to understate. Low-wage end (Retail & Hospitality $42,024) is the derivation's home range | Limit at the high-wage end |
| JOLTS Table 22 | The industry quits rate applies to a client in that industry | Verified: nonfarm establishment survey, sector and supersector rows, no size-class cut in Table 22 | 12 and 1,200 employees get the same blended industry rate. Nonprofit & Education and Other are built or blended rows | Applies to industry, untested by size |
| OEWS May 2025 wage W | Industry all-occupation mean wage represents a client's average wage | Verified: wage and salary workers at establishments of all sizes, excludes owners and self-employed | 12 employees: occupation mix and owner-operators differ from the industry blend. Sectors 61, 62, 99 blend public ownership | Small end untested |
| McKinsey 2019 (receipt only) | Managers spend 37% of time on decisions, 58% ineffective | Executives and managers, senior-skewed, 62% at companies under $1B, no first-line supervisors | Weakest under about 100 employees. No dollar is computed, so the receipt must state the limit | Receipt with stated limit |

The Gallup 18% with the 69% population and the JOLTS rate assume US employers. PRV3 intake collects jurisdictions, and nothing in the formulas varies by them.

## 8. Tests to add or change

- `tools/test_friction_tax.py` (2,292 lines): remove section 1 (`SEVERITY_SCALAR`, `:165-180`), rewrite the compute sections (2-13, 20-21), remove the grid sections (14-15, `:512-527`) and the `STATE_MULTIPLIERS` sections (17-19), replace with: one hand-computed fixture per channel with each input named, the headcount rule (integer and float priced at actual N, "", None, "150", 0 and negative all uncalibrated, no bucket fallback), channel switch rule against the new `STATE_CRITERIA`, the `paper_shield`-only case, multi-state sets do not stack, severity changes nothing, `excess` is null, every industry has a W and a q, vintage strings present.
- `engine/data/state_criteria.py` needs a registry test (58 state ids match `engine/data/states.py`) and a legal score assertion equivalent to `engine/friction_tax.py:2172-2176`.
- **Required: Legal/Compliance outputs byte-identical before and after the refactor.** Before any refactor commit, record a baseline from the unchanged code: `compute_legal_compliance_exposure` and `compute_legal_per_state_breakdown` (`engine/friction_tax.py:4317`, `:4508`) for every one of the 58 states as a single-state input across a fixed grid (integer headcounts 12, 60, 175, 400, 800, 1200, all 11 industries, all 6 org types, a fixed jurisdiction set), plus `private_output.legal_tail_risk_exposure` for each of the 175 calibration profiles (`engine/test_profiles*.py`, run through the `tools/calibration_runner.py` pipeline). Store canonical JSON and its sha256 under `tools/fixtures/`. After the refactor the same calls must produce identical bytes. A single differing byte fails the test and blocks the build.
- `tools/test_contract.py`: `:441` estimate shape, `:1047-1150` ledger (`dollar_exposure` cross-check becomes a `channels` check), `inaction_cost` assertions.
- Web: `web/lib/output-text.test.ts:294,372` (keep the hidden-flag assertion), `web/components/PrivateOutput.friction.test.ts:33-49`, `web/lib/diagnostic-completion-brand.test.ts:172-190`, plus the server-render test that no friction dollar reaches the report screen (stays as is).
- New: framing-rule assertion ("what organizations like yours typically lose", absence of "normal" or "acceptable") on any surface showing the figure.
- Calibration impact: expected none. `tools/calibration_runner.py` and `engine/test_suite.py` do not reference friction tax. Confirm by re-running the 175-profile suite after the build.
- Live production round-trip check required for the payload and condensed route changes (CLAUDE.md, 2026-08-27).

## 9. Gemini gate questions

1. Is Option A (states select channels, severity inert) defensible under P4?
2. Is JOLTS annualization correct as specified (monthly quits rate x 12 from Table 22's footnote definition)?
3. Is Work Institute's flat 33.3% acceptable versus Gallup's role-tiered 40/80/200% for a population whose role mix is unknown?
4. Is a two-channel baseline of roughly 13% to 15.5% of payroll defensible under the framing rule?
5. Is f = 0.5 sound?
6. Is a point estimate preferable to a range with no cited uncertainty?
7. Does removing decision time leave any remaining double count between the engagement and turnover channels?
8. Is moving the per-state criteria out of `STATE_MULTIPLIERS` into a scores-only `engine/data/state_criteria.py` safe for Legal/Compliance, given the byte-identical before and after test specified in Section 8?

## 10. Build steps (proposed order, no code until the spec clears Gemini and Pete)

Precondition: the share-path headcount bug (`web/components/DiagnosticFlow.tsx:916`) is fixed separately ahead of the rebuild. See the share-path headcount fix.

1. **Legal baseline.** Record the byte-identical baseline (Section 8) from unchanged code and commit it.
2. **State criteria refactor.** Create `engine/data/state_criteria.py`, point Legal (`engine/friction_tax.py:2172-2176`, `:4166-4170`) and `engine/contract.py:35`, `:719` at it, then run the byte-identical test.
3. **Org type list ownership.** Move the "source of truth" note for the org type option list from `ORG_TYPE_SCALARS` to `INTAKE_FIELDS["org_type"]` (`engine/data/intake.py:296`) in `web/components/DiagnosticFlow.tsx:187` and `web/components/SelfSelectIntakeModal.tsx:11`, and add a test that both web lists equal the intake list. Do this before `ORG_TYPE_SCALARS` is removed.
4. **Wage refresh.** Replace `_INDUSTRY_WAGE_DATA` (`engine/friction_tax.py:230`) with the May 2025 values in Section 3 and new citation ids. This also changes `get_industry_wage` (`:345`) for the condensed range.
5. **Two-channel function.** Replace `compute_friction_tax` (`:1877-2016`) and remove the magnitude constants, `SEVERITY_SCALAR`, `PAYROLL_BASELINE_GRID` and `ORG_TYPE_SCALARS`. Apply the headcount rule in Section 2. Update `engine/contract.py` (`:405-532`, `:693-757`, `:1125-1150`, `:1184-1207`) and add `friction_receipts`.
6. **Condensed.** Replace the range at `api/engine.py:283-289` with wage x 0.333.
7. **Web types and consumers.** Update every consumer listed in Section 6, keeping `FRICTION_DOLLARS_VISIBLE` false (`web/lib/output-text.ts:157`).
8. **Tests.** Section 8, then the 175-profile calibration run (expected no change) and the Legal byte-identical test.
9. **Production round-trip** on the payload and condensed routes before anything is marked done.
