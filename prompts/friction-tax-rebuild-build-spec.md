# Friction Tax Rebuild: Build Spec

Status: DRAFT, Gemini round 2 partial (2026-09-30), follow-up pending. No engine code written. Research and decisions: `prompts/friction-tax-rebuild-source-verification.md` (Sections 1 to 5 and "Decisions (Pete, 2026-09-30)" items 1 to 11). MOB reference: 13b FRICTION TAX REBUILD entry (`tools/_mob.txt:1505`). Every code reference below was read live on 2026-09-30.

## Open questions (Pete), up front

Resolved 2026-09-30 and folded into the design: a state set with no dollar channel returns a null estimate, receipts move to `private_output.friction_receipts` (Section 6), the state criteria move to `engine/data/state_criteria.py` (Section 4), the decision-time receipt stays inside the `FRICTION_DOLLARS_VISIBLE` branch, the bucket-mean fallback is removed, and the Nonprofit & Education rate is recomputed (Section 3). The partial-year factor is withdrawn (verification doc decision 7 correction). Wages use privately owned OEWS rows where published (Decision 12, Section 3). The headcount guard requires N of at least 2 and null below that (Decision 13, Section 2). `inaction_cost_*` ships as two lines (Decision 14, Section 6). The 1,000 intake cap stays and is stated on the output (Decision 15, Section 2 and Section 6). The Legal byte-identical test baseline is taken at the parent of the first refactor commit, stored under `tools/fixtures/` and never regenerated (Section 8). The share-path headcount bug is latent: Path 1 sharing is disabled (`web/components/DiagnosticFlow.tsx:930`), fix when sharing is enabled.

Remaining open:

1. **Qualifying margin (display).** Still open, display only, does not affect costing.

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
| Web share path | `web/components/DiagnosticFlow.tsx:916`, `web/app/api/share/create/route.ts:93` | sends a numeric string | latent: Path 1 sharing is disabled (DiagnosticFlow.tsx:930). Fix when sharing is enabled. |
| Ledger | `engine/contract.py:405-532`, `dollar_exposure` `:473-481` | single-state dollars | CHANGE: `dollar_exposure` dropped, add `channels` (the channels that state switches on) |
| Receipts | `engine/contract.py:693-757`, uses `STATE_MULTIPLIERS` at `:719`, channel labels `:588` | narrates grid, org scalar, loading, severity, 1.4x | REWRITE as per-channel inputs with vintages |
| Payload assembly | `engine/contract.py:1125-1150`, `:1184`, `:1191-1207`, `:1217-1218` | `friction_tax_estimate {low, high, currency, driving_factors}` | CHANGE (Section 6) |
| Condensed cost of one departure | `api/engine.py:260-294`, `:283-289` (wage x 0.50 to 0.75) | range | REPLACE with wage x 0.333 (P9), single value |
| Display switch | `web/lib/output-text.ts:157`, gates `:271`, `:385-389`, `:415`, `:419-423`, `web/components/PrivateOutput.tsx:378`, `:408`, `:437`, `:445`, `:458` | `FRICTION_DOLLARS_VISIBLE = false` | KEEP false until Gemini and Pete clear the rebuild. Flipping it is a public-number change (Tier 4) |
| Legal exposure | `engine/friction_tax.py:4317`, `:4508` | separate mechanism | KEEP unchanged |

## 2. Channels (two dollar channels, one receipt)

Notation: N = employees, W = all-occupation mean annual wage for the engine industry (OEWS May 2025, privately owned rows where published, Decision 12), P = N x W. q = annual quit rate = JOLTS monthly rate x 12. q enters the turnover channel only.

| Channel | Formula | Inputs |
|---|---|---|
| Engagement | P x 0.69 x 0.18 | 0.18: Gallup 2020 article. 0.69 = 1 minus Gallup engaged 31% (May 2026 indicator). The channel prices position-years of payroll, so there is no partial-year discount: a leaver's remaining year is filled by the replacement (verification doc decision 7 correction) |
| Turnover | P x q x 0.42 x 0.333 | 0.42 = Gallup preventable share (July 2024, verification doc Section 5). 0.333 = Work Institute (2017 Retention Report, low-wage derivation, Section 5). q = JOLTS 2025 |
| Decision time (receipt only) | no dollar value | McKinsey 2019: 37% of time on decisions, 58% of it ineffective. Text only. `W_m` and the 11-0000 share are removed from the engine design and stay in the verification doc as research |

Known limits:
- Vacancy gap between leaver and replacement is counted in both the engagement channel and Work Institute's indirect ~22%. Small and disclosed, not adjusted.
- Intake clamps headcount to 1 through 1,000 (`web/components/DiagnosticFlow.tsx:53`, `:62-63`, `:95`), so any larger organization is priced as 1,000 employees. Percent of payroll is unaffected, dollars for larger organizations would be understated. At N = 1000 the output therefore shows percent of payroll only, with every dollar amount null and no dollar figure in any receipt (Decisions 15 and 17, Gemini round 2 failure mode 2). N = 999 carries both. The output states the cap.

Headcount guard (Decisions 10 and 13): N is the intake value only when it is an `int` or `float`, is not a `bool`, is finite, and is at least 2. Anything else returns an uncalibrated result and `friction_tax_estimate` is null: "", a numeric string, None, True, `float("inf")`, `float("nan")`, 0, negatives, and 1 (a solo principal has no workforce the sources measure). There is no bucket-mean fallback. Note `bool` is a subclass of `int` in Python, so the guard must test it explicitly. The engine rule is the backstop, because `web/app/api/diagnostic/session/start/route.ts:22-23` checks only `typeof number` and `Number.isFinite` and accepts 0 and negatives, and `engine/main.py:220` defaults a missing value to 0. A live-path review on 2026-09-30 found no path that supplies a bucket label:

| Path | Headcount supplied | Reference | Result |
|---|---|---|---|
| Path 1 session complete | number, validated only as finite | `web/app/api/diagnostic/session/start/route.ts:22-23`, `engine/main.py:220` | integer, OK. The route does not reject 0 or negative values, the intake UI clamps to 1 through 1,000 (`web/components/DiagnosticFlow.tsx:62-63`) |
| Self-select `/api/result` | number from the modal, or "" sentinel | `web/components/SelfSelectIntakeModal.tsx:82`, `web/lib/engine-client.ts:84` | integer, or uncalibrated on "" (by design) |
| Condensed | none, friction is never computed | `engine/main.py:1075-1078` | not applicable |
| Dev preview and fixture picker | "" in the intake echo only, payload is stored | `web/app/(site)/dev/diagnostic-preview/[id]/page.tsx:62`, `web/components/DiagnosticFixturePicker.tsx:189` | not applicable |
| Share `/api/share/create` | numeric string | `web/components/DiagnosticFlow.tsx:916`, `web/app/api/share/create/route.ts:93` | never reached today, latent: Path 1 sharing is disabled (DiagnosticFlow.tsx:930). Fix when sharing is enabled. |

CORRECTION 2026-09-30: an earlier draft described this as live. Path 1 sharing is off, so the string headcount is never sent.

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

| Engine industry | W, May 2025, private rows where published (replaces `:230`) | W now (May 2023) | JOLTS 2025 monthly quits rate (proposed row) | q (x12) |
|---|---:|---:|---|---:|
| Professional Services | $108,640 | $102,670 | 2.3 Professional and business services | 27.6% |
| Healthcare & Life Sciences | $70,969 | $67,320 | 2.0 Health care and social assistance | 24.0% |
| Financial Services | $100,842 | $94,150 | 1.3 Finance and insurance | 15.6% |
| Technology | $115,030 | $108,110 | 1.3 Information | 15.6% |
| Manufacturing | $69,131 | $64,440 | 1.4 Manufacturing | 16.8% |
| Retail & Hospitality | $42,024 | $39,651 | 3.37, Retail trade 2.6 and Accommodation and food services 4.2 weighted by OEWS employment | 40.4% |
| Nonprofit & Education | $72,765 | $57,770 | 1.64, private educational services 1.4 (3,344,880) and Other services 2.2 standing in for NAICS 813 (1,429,400), weighted by OEWS May 2025 employment | 19.7% |
| Government & Public Sector | $80,290 | $74,410 | 0.8 Government | 9.6% |
| Construction | $72,146 | $67,430 | 1.8 Construction | 21.6% |
| Transportation & Warehousing | $64,331 | $59,320 | 2.2 Transportation, warehousing, and utilities | 26.4% |
| Other | $67,977 | $63,446 | 2.2 Total private (Decision 9) | 26.4% |

W (May 2025) is the employment-weighted mean of the 3-digit NAICS all-occupation wages in the mapping committed in the verification doc Section 2b, computed 2026-09-30, not a published BLS sector wage. Ownership (Decision 12), from `nat3d_owner_M2025_dl.xlsx` in the same oesm25in4.zip:
- The ownership file publishes split rows only for NAICS 611 and 622. Privately owned (ownership code 5): 611 = 3,344,880 employees at $73,400 (state 2,098,490 at $80,660 and local 8,408,680 at $65,740 excluded), 622 = 5,570,850 at $89,460 (state 445,500 and local 696,410 excluded).
- Nonprofit & Education = 611 private plus 813 (1,429,400 at $71,280): 4,774,280 employees, $72,765 (was $69,984 blended). Healthcare & Life Sciences = 621, 622 private, 623, 624: 22,889,480 employees, $70,969 (was $71,770 blended).
- Every other mapped industry is already a private-only row in the standard file, except three that carry a blended or government ownership code with no privately owned row published: 713 and 721 (code 57, inside Other and Retail & Hospitality) and 491 Postal Service (federal, inside Transportation & Warehousing). They are left as published and disclosed. Not substituted.
- Government & Public Sector stays all-ownership ($80,290).

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

`friction_tax_estimate: { currency, typical_baseline: { total: { amount, percent_of_payroll }, channels: [ { channel, amount, percent_of_payroll, inputs: [ { name, value, source, vintage } ] } ] }, excess: null, driving_factors }`. `percent_of_payroll` is present on every channel and on the total at every N (engagement 12.42 for every profile, turnover q x 0.42 x 0.333 x 100). `amount` is null at N = 1000, the intake cap (Decision 17), and a number below it. The decision-time receipt is a driving factor with no `amount`. `low` and `high` are removed. `friction_tax_estimate` is null when uncalibrated or when no dollar channel is selected (for example only `paper_shield` identified). Receipts, including the decision-time receipt, move to a sibling `private_output.friction_receipts` so they can render when the estimate is null (adopted 2026-09-30). They still render only inside the `FRICTION_DOLLARS_VISIBLE` branch (`web/components/PrivateOutput.tsx:437-445`).

Engine (Python): `engine/contract.py:1137-1149` (build), `:693-757` (receipts), `:405-532` (ledger, drop `dollar_exposure`, add `channels`), `:1191-1207` (`_cost_parts` and `inaction_cost_*`), `:35` and `:719` (import), `api/engine.py:283-289` (condensed).

Web consumers that change (all read live):
- `web/lib/types.ts:147-153` (`FrictionTaxEstimate`, removes `low`/`high`), `:178-182` (`FrictionTaxLedgerEntry.dollar_exposure`), `:377`, `:384`, `:520` (payload fields), `:581` (`inaction_cost_*`).
- `web/lib/engine-client.ts:147-148` (engine response types), `:525` (`condensed_financial_range`).
- `web/lib/output-renderer.ts`: mark for deletion, not for update. `renderPrivateOutput` (`:113`) and `renderShareableOutput` (`:171`) have no callers (checked 2026-09-30), so the `FrictionTax` type (`:32-39`) and the `friction_tax_estimate` read (`:120`) go with the file.
- `web/lib/output-text.ts:170-209` (`groupLedgerRows`, `higherEstimate` read `dollar_exposure`), `:386-415` (ledger and receipts lines), `:419-423` (`money(friction.low, friction.high)` in the cost comparison).
- `web/components/PrivateOutput.tsx:171`, `:384` (`group.dollar_exposure`), `:445` (receipts source moves to `friction_receipts`), `:458`.
- `web/components/ReportDetails.tsx:72`, `:88-90` (`rangeText(friction.low, friction.high)`).
- `web/lib/dev-diagnostic-preview.ts:8`, `:43`.
- `web/lib/diagnostic-completion.ts:197-198`, `web/app/api/result/route.ts:181-182`, `web/app/api/share/create/route.ts:189` (pass-through, type changes only).
- `web/components/DiagnosticFixturePicker.tsx:163` (sets null, likely no change).
- Condensed: `web/app/api/diagnostic/condensed/answer/route.ts:155`, `web/components/CondensedOutput.tsx:130` (range to single value).
- `inaction_cost_*` (`engine/contract.py:1191-1207`, `web/lib/output-text.ts:419-423`, `web/components/PrivateOutput.tsx:457`): two lines (typical-loss point estimate, tail-risk legal range), not a sum, since one is a point and the other a range (Decision 14).
- **Consumers that must render percent-only at the cap** (`amount` null at N = 1000):
  - `web/components/ReportDetails.tsx:72`, `:88-90` (`rangeText(friction.low, friction.high)` becomes a percent line when `amount` is null).
  - `web/lib/output-text.ts:386-415` (receipts text and ledger lines) and `:419-423` (the friction line in the cost comparison, `money(...)`, becomes "X% of payroll").
  - `web/components/PrivateOutput.tsx:437-458` (the gated block, the receipts source `friction_receipts`, and the `friction=` prop passed to `ReportDetails`).
  - Engine receipts, `engine/contract.py:693-757`: at the cap no receipt text may contain a dollar figure (the payroll baseline receipt names dollars today).
  - `service_cost_comparison` (`engine/contract.py:1191-1207`, `web/lib/types.ts:581`): the typical-loss line is null in dollars at the cap, the legal range line is unaffected.
  - The Copy results text (`web/lib/output-text.ts`, same functions) follows the same rule.
- Display stays hidden (`web/lib/output-text.ts:157`). Call 1 and Call 2 keep the no-dollar rule (`engine/output_synthesis.py:50`).

## 6b. Worked figures (two channels, actual headcount, May 2025 inputs)

NE = 0.69, no partial-year discount, q = JOLTS monthly x 12. Engagement is 12.42% of payroll for every profile (0.69 x 0.18). Only the turnover channel varies by industry.

| Employees / industry | W | Quit rate (monthly, annual) | Payroll | Engagement | Turnover | Total | Eng % | Turn % | Total % of payroll |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 12 / Retail & Hospitality | $42,024 | 3.37, 40.4% | $504,288 | $62,633 | $28,497 | $91,130 | 12.4% | 5.7% | 18.1% above line |
| 12 / Other | $67,977 | 2.20, 26.4% | $815,724 | $101,313 | $30,119 | $131,432 | 12.4% | 3.7% | 16.1% above line |
| 60 / Construction | $72,146 | 1.80, 21.6% | $4,328,760 | $537,632 | $130,771 | $668,403 | 12.4% | 3.0% | 15.4% above line |
| 60 / Government & Public Sector | $80,290 | 0.80, 9.6% | $4,817,400 | $598,321 | $64,681 | $663,002 | 12.4% | 1.3% | 13.8% |
| 175 / Technology | $115,030 | 1.30, 15.6% | $20,130,250 | $2,500,177 | $439,205 | $2,939,382 | 12.4% | 2.2% | 14.6% |
| 175 / Professional Services | $108,640 | 2.30, 27.6% | $19,012,000 | $2,361,290 | $733,889 | $3,095,179 | 12.4% | 3.9% | 16.3% above line |
| 400 / Nonprofit & Education | $72,765 | 1.64, 19.7% | $29,106,000 | $3,614,965 | $800,891 | $4,415,856 | 12.4% | 2.8% | 15.2% above line |
| 400 / Manufacturing | $69,131 | 1.40, 16.8% | $27,652,400 | $3,434,428 | $649,734 | $4,084,162 | 12.4% | 2.3% | 14.8% |
| 800 / Healthcare & Life Sciences | $70,969 | 2.00, 24.0% | $56,775,200 | $7,051,480 | $1,905,739 | $8,957,219 | 12.4% | 3.4% | 15.8% above line |
| 800 / Transportation & Warehousing | $64,331 | 2.20, 26.4% | $51,464,800 | $6,391,928 | $1,900,237 | $8,292,165 | 12.4% | 3.7% | 16.1% above line |
| 1,000 / Financial Services (at the cap) | $100,842 | 1.30, 15.6% | withheld | null | null | null | 12.4% | 2.2% | 14.6% |
| 1 / any industry | | | null | null | null | null | | | null (N below 2, Decision 13) |

The largest row is 1,000 employees, the intake ceiling (known limit, Section 2), where dollars are withheld and only percent of payroll is shown (Decision 17). Totals run 13.8% to 18.1% of payroll. 7 of the 11 priced profiles are above 15%. The 15% line is Claude.ai's reference line, not a cited threshold. The removal of the partial-year discount raises every total (0.6 to 2.5 points of payroll depending on the industry quit rate). Percent of payroll does not depend on headcount, only dollars do.

What the benchmarks do and do not show:
- **The engagement channel's only benchmark is Gallup's own worked example** (verification doc Section 1a: 10,000 x 67% x $50,000 x 18% = $60.3M on $500M payroll, 12.06%). That is circular. The channel applies Gallup's formula, so 12.42% against Gallup's 12.06% confirms arithmetic, not magnitude. No independent check of the engagement magnitude was found.
- Turnover has no independent payroll-percentage benchmark either. The SHRM 50% to 200% of salary range (`prompts/friction-tax-unit-decision.md:16`) is a per-exit cost and is not comparable.
- Old engine range, for orientation only: 5% to 25% of payroll before the severity scalar (`prompts/friction-tax-state-multiplier-methodology.md:48`).

## 7. Demographic Applicability Filter (`prompts/demographic-applicability-filter-protocol.md`)

Intake fields: headcount (integer, minimum 1, `engine/data/intake.py:54-62`), industry (11 values, `:283`), org type (6 values, `:296`), jurisdictions. Extremes tested: 1 to 12 employees, 1,000 employees (the intake ceiling), Government, Nonprofit & Education, Retail & Hospitality, Technology.

| Source | Assumption | Eligibility boundary (what I could establish) | Extremes | Status |
|---|---|---|---|---|
| Gallup 18% and engaged 31% | An average not-engaged US employee costs 18% of salary at any employer | The 18% comes from a global example ("Globally, 67%...") paired with a US engaged share (31%, May 2026), a geographic mismatch disclosed, not adjusted. Not segmented by employer size or industry in the material | 12 employees: Gallup's share is not testable for a single small team. Government and nonprofit: US sample includes them, not confirmed from source | Partly unverified |
| Gallup 42% preventable (July 2024) | Share of voluntary exits that were preventable | Self-reported by leavers (their own view of preventability), not an employer record | Unknown by size and industry | Self-report limit |
| Work Institute 33.3% | Cost per voluntary exit is a flat 33.3% of salary | Low-wage derivation (2017 Retention Report, $8/hour basis). Gallup's same July 2024 article gives role tiers: about 200% of salary for leaders and managers, 80% technical, 40% frontline | High-wage end: Technology ($115,030), Professional Services ($108,640), Financial Services ($100,842) are where a flat 33.3% is most likely to understate. Low-wage end (Retail & Hospitality $42,024) is the derivation's home range | Limit at the high-wage end |
| JOLTS Table 22 | The industry quits rate applies to a client in that industry | Verified: nonfarm establishment survey, sector and supersector rows, no size-class cut in Table 22 | 12 and 1,000 employees get the same blended industry rate. Nonprofit & Education and Other are built or blended rows | Applies to industry, untested by size |
| OEWS May 2025 wage W | Industry all-occupation mean wage represents a client's average wage | Verified: wage and salary workers at establishments of all sizes, excludes owners and self-employed | 12 employees: occupation mix and owner-operators differ from the industry blend. Sectors 61, 62, 99 blend public ownership | Small end untested |
| McKinsey 2019 (receipt only) | Managers spend 37% of time on decisions, 58% ineffective | Executives and managers, senior-skewed, 62% at companies under $1B, no first-line supervisors | Weakest under about 100 employees. No dollar is computed, so the receipt must state the limit | Receipt with stated limit |

The Gallup 18% with the 69% population and the JOLTS rate assume US employers. PRV3 intake collects jurisdictions, and nothing in the formulas varies by them.

## 8. Tests to add or change

- `tools/test_friction_tax.py` (2,292 lines): remove section 1 (`SEVERITY_SCALAR`, `:165-180`), rewrite the compute sections (2-13, 20-21), remove the grid sections (14-15, `:512-527`) and the `STATE_MULTIPLIERS` sections (17-19), replace with: one hand-computed fixture per channel with each input named, the headcount guard (int and float of at least 2 priced at actual N, and uncalibrated for "", None, "150", True, `float("inf")`, `float("nan")`, 0, negatives and 1, no bucket fallback), channel switch rule against the new `STATE_CRITERIA`, the `paper_shield`-only case, multi-state sets do not stack, severity changes nothing, `excess` is null, every industry has a W and a q, vintage strings present.
- `engine/data/state_criteria.py` needs a registry test (58 state ids match `engine/data/states.py`) and a legal score assertion equivalent to `engine/friction_tax.py:2172-2176`.
- **Required: Legal/Compliance outputs byte-identical before and after the refactor.** Before any refactor commit, record a baseline from the unchanged code: `compute_legal_compliance_exposure` and `compute_legal_per_state_breakdown` (`engine/friction_tax.py:4317`, `:4508`) for every one of the 58 states as a single-state input across a fixed grid (integer headcounts 12, 60, 175, 400, 800, 1200, all 11 industries, all 6 org types, a fixed jurisdiction set), plus `private_output.legal_tail_risk_exposure` for each of the 175 calibration profiles (`engine/test_profiles*.py`, run through the `tools/calibration_runner.py` pipeline). Store canonical JSON and its sha256 under `tools/fixtures/`. After the refactor the same calls must produce identical bytes. A single differing byte fails the test and blocks the build.
- `tools/test_contract.py`: `:441` estimate shape, `:1047-1150` ledger (`dollar_exposure` cross-check becomes a `channels` check), `inaction_cost` assertions.
- Web: `web/lib/output-text.test.ts:294,372` (keep the hidden-flag assertion), `web/components/PrivateOutput.friction.test.ts:33-49`, `web/lib/diagnostic-completion-brand.test.ts:172-190`, plus the server-render test that no friction dollar reaches the report screen (stays as is).
- Cap tests (Decision 17): N = 1000 returns `percent_of_payroll` on each channel and the total with every `amount` null and no dollar figure in any `driving_factors` text, N = 999 returns percents and amounts, `percent_of_payroll` is present at every N, and the web consumers above render percent-only when `amount` is null.
- New: framing-rule assertion ("what organizations like yours typically lose", absence of "normal" or "acceptable") on any surface showing the figure.
- Calibration impact: expected none. `tools/calibration_runner.py` and `engine/test_suite.py` do not reference friction tax. Confirm by re-running the 175-profile suite after the build.
- Live production round-trip check required for the payload and condensed route changes (CLAUDE.md, 2026-08-27).

## 9. Gemini gate questions

1. Is Option A (states select channels, severity inert) defensible under P4?
2. Is JOLTS annualization correct as specified (monthly quits rate x 12 from Table 22's footnote definition)?
3. Is Work Institute's flat 33.3% acceptable versus Gallup's role-tiered 40/80/200% for a population whose role mix is unknown?
4. Is a two-channel baseline of roughly 13.8% to 18.1% of payroll defensible under the framing rule?
5. Is the vacancy-gap overlap between the engagement channel and Work Institute's indirect cost small enough to disclose rather than adjust?
6. Is a point estimate preferable to a range with no cited uncertainty?
7. Does removing decision time leave any remaining double count between the engagement and turnover channels?
8. Is moving the per-state criteria out of `STATE_MULTIPLIERS` into a scores-only `engine/data/state_criteria.py` safe for Legal/Compliance, given the byte-identical before and after test specified in Section 8?

## 10. Build steps (proposed order, no code until the spec clears Gemini and Pete)

Note: the share-path headcount bug (`web/components/DiagnosticFlow.tsx:916`) is latent: Path 1 sharing is disabled (DiagnosticFlow.tsx:930). Fix when sharing is enabled.

1. **Legal baseline.** Record the byte-identical baseline (Section 8) from unchanged code and commit it.
2. **State criteria refactor.** Create `engine/data/state_criteria.py`, point Legal (`engine/friction_tax.py:2172-2176`, `:4166-4170`) and `engine/contract.py:35`, `:719` at it, then run the byte-identical test.
3. **Org type list ownership.** Move the "source of truth" note for the org type option list from `ORG_TYPE_SCALARS` to `INTAKE_FIELDS["org_type"]` (`engine/data/intake.py:296`) in `web/components/DiagnosticFlow.tsx:187` and `web/components/SelfSelectIntakeModal.tsx:11`, and add a test that both web lists equal the intake list. Do this before `ORG_TYPE_SCALARS` is removed.
4. **Wage refresh.** Replace `_INDUSTRY_WAGE_DATA` (`engine/friction_tax.py:230`) with the May 2025 values in Section 3 (privately owned rows where published, Decision 12) and new citation ids. This also changes `get_industry_wage` (`:345`) for the condensed range.
5. **Two-channel function.** Replace `compute_friction_tax` (`:1877-2016`) and remove the magnitude constants, `SEVERITY_SCALAR`, `PAYROLL_BASELINE_GRID` and `ORG_TYPE_SCALARS`. Apply the headcount guard in Section 2 and state the 1,000 cap on the output and withhold dollars at the cap (Decisions 15 and 17). Update `engine/contract.py` (`:405-532`, `:693-757`, `:1125-1150`, `:1184-1207`) and add `friction_receipts`.
6. **Condensed.** Replace the range at `api/engine.py:283-289` with wage x 0.333.
7. **Web types and consumers.** Update every consumer listed in Section 6, keeping `FRICTION_DOLLARS_VISIBLE` false (`web/lib/output-text.ts:157`).
8. **Tests.** Section 8, then the 175-profile calibration run (expected no change) and the Legal byte-identical test.
9. **Production round-trip** on the payload and condensed routes before anything is marked done.

## 11. Gemini gate record

Round 2 (2026-09-30):
- Q1, Q2, Q3, Q6, Q8: CONFIRM, accepted.
- Q5: Gemini answered the pre-revision question (remove the discount). This agrees with decision 7's withdrawal, but the revised Q5 (vacancy-gap overlap) is unanswered.
- Q4: CONFIRM addressed arithmetic, not magnitude.
- Q7: CONFIRM overstated. Gallup's exclusion of turnover does not cover Work Institute's ~22% indirect cost, which overlaps the engagement channel during vacancy and ramp-up. Claude.ai verification, 2026-09-30.
- Failure modes: (1) mapping lock, resolved by decision 16. (2) cap understatement, resolved by decision 17.
- Follow-up sent on Q4 and Q5.
