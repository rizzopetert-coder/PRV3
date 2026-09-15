# Ohio Compensatory-Damages Pricing Plan (plan only, not built, not Gemini-reviewed)

Priority Queue item 9 scope, decided 2026-09-14. This is a durable
multi-session plan doc, capturing what was decided and what remains
open — not a build, and not yet submitted to the Gemini architecture
gate.

## Goal

Wire `_oh_is_small_employer()` (`engine/friction_tax.py:3222`) into a
real R.C. 2315.21 compensatory-damages pricing path for Ohio —
currently both of that statute's branches resolve to
`QUALITATIVE_ONLY` because no compensatory-damages base figure exists
anywhere in the codebase for any jurisdiction (confirmed by
investigation this session).

## Decided

- **Salary-range basis:** reuse the existing `_INDUSTRY_WAGE_DATA`
  table (real BLS OEWS May 2023 mean annual wages by industry, already
  wired into `compute_friction_tax()`) as the compensatory-damages
  salary basis, rather than sourcing a new dataset.
- **No individual/case-specific salary collection** — Pete explicitly
  ruled this out. The output will always be an industry-average-
  derived estimate, never anchored to the actual terminated employee's
  real wages. This is permanent, not a fallback for when case data is
  missing.
- **Consequence, flagged and accepted:** because `_INDUSTRY_WAGE_DATA`
  is a MEAN, not a distribution, any known citation-accuracy
  imprecision already living in that table (e.g. the Technology
  sector's "Sector 51 Information" being broader than a clean
  Technology label, documented in the table's own source notes) now
  carries legal-accuracy weight it didn't carry when it only fed a
  friction-cost estimate. This needs explicit review, not silent
  inheritance, when this plan reaches the Gemini gate.
- **State+industry multipliers on top of the salary base:** still
  undefined. Represents litigation-outcome/settlement-variance by
  jurisdiction (not yet confirmed whether that's the right framing vs.
  something else) — scoped as a research task, not yet started.

## Decided, 2026-09-15 (research session)

- **Multiplier concept, resolved: EEOC charge-filing frequency by
  state, normalized per capita or per employment base — NOT
  dollar-based settlement/verdict variance.** This is a relative
  jurisdiction-risk multiplier ("how often claims get filed here"),
  conceptually distinct from "how large awards are" — Pete explicitly
  confirmed this is useful even though it doesn't produce a dollar
  figure directly, but any framing/documentation of it must stay
  honest about that distinction, never blur the two into something
  that reads like a settlement-size signal.
- **Rejected source: U.S. Chamber Institute for Legal Reform data**
  (Tort Costs in America, Lawsuit Climate Survey). Pete's call: an
  advocacy organization's data isn't an acceptable source here — wants
  reputable/neutral sourcing, consistent with this codebase's existing
  BLS/Census standard (same bar `_INDUSTRY_WAGE_DATA` was held to).
- **Primary source identified and independently verified, 2026-09-15b:**
  EEOC Table E1b, "Charge Receipts by State (includes U.S. Territories)
  and Basis or Statute (All Statutes)," FY 2009 – FY 2025, XLSX. Found
  via https://www.eeoc.gov/data/enforcement-and-litigation-statistics-0.
  **Correct public URL (verified, HTTP 200, `Content-Type:
  application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`,
  served from host `eeoc-web-prod`):**
  https://www.eeoc.gov/sites/default/files/2026-04/Table_E1b._Charge_Receipts_by_State_%28includes_U.S._Territories%29_and_Basis_or_Statute_%28All_Statutes%29_FY_2009_-_FY_2025_suppressed_0.xlsx
  The `edit-www.eeoc.gov` variant originally found on the public page
  returns `403 Forbidden` (confirmed directly, with and without a
  browser user-agent header) — it's a CMS staging subdomain leaking
  into the live page's HTML, not a usable link. Swapping `edit-www` for
  plain `www` is the fix; both concerns flagged in the prior session
  are now resolved:
  1. **Staging-link concern — resolved.** `www.eeoc.gov` (same path)
     is the real public URL, confirmed live.
  2. **Suppression concern — resolved, not a blocker.** Downloaded and
     inspected the file directly (`openpyxl`, one sheet, 72 rows ×
     603 columns — 17 fiscal years × ~35 columns/year, FY2025's "Total
     Charges" column at column 566). All 50 states + DC carry real,
     non-suppressed numeric FY2025 Total Charges values. The only
     suppressed (`*`) rows are 6 small U.S. territories/compact
     entities outside the multiplier's scope anyway: APO/AFO,
     Federated States of Micronesia, Marshall Islands, Northern
     Mariana Islands, Palau, Wake Island/Atoll. FY2025 US-wide total:
     88,201 charges (row 65). One footnote worth carrying forward
     (row 68): the per-basis sub-columns (Race/Sex/etc.) double-count
     charges filed under multiple bases — irrelevant to the "Total
     Charges" column itself, but worth remembering if a future pass
     ever uses a basis-specific column instead.

## Decided, 2026-09-15c (normalization base + denominator sourcing)

- **Normalization base: BLS employment, not Census population.** Pete's
  call, over the two options laid out in the prior research pass —
  reasoning: per-capita population structurally penalizes
  retirement-heavy states with an artificially low rate (population
  includes children, retirees, and everyone else who structurally
  cannot generate a charge, understating real exposure for states with
  an older population skew), and BLS keeps sourcing consistent with
  this codebase's existing standard (`_INDUSTRY_WAGE_DATA` is already
  BLS OEWS).
- **EEOC charge-population coverage confirmed: private sector + state
  and local government, excluding federal.** Checked against Table
  E1b's own file first, per explicit instruction, not assumed from a
  general EEOC statement — and that file itself (title, column
  headers, all 8 footnote rows) contains **no explicit scope
  statement** on this question at all. That's a real documentation gap
  in the source file, reported plainly rather than glossed over.
  What corroborates the private + state/local (excl. federal) framing
  instead, from primary sources independent of Table E1b itself:
  - EEOC's own "FY 2018-2022 Charge Report Submitted to Congress"
    repeatedly frames "charges" — the same term Table E1b's title
    uses — as covering "private sector and state and local government
    workplaces," not as an isolated marketing line but as that
    report's core, repeated scope statement.
  - **Statutory/regulatory structure, independently verifiable:** Title
    VII's charge-filing mechanism (42 U.S.C. § 2000e-5) governs private
    and state/local government employers. Federal employees are
    covered under a categorically separate section (42 U.S.C. §
    2000e-16) and process (29 C.F.R. Part 1614) that EEOC's own
    regulations describe using "complaint," not "charge" — federal
    employees do not file charges with an EEOC field office "in the
    same manner as private sector employees." This is a structural
    fact about the two systems, not a phrasing choice on one webpage.
  Treated as sufficiently confirmed to proceed on this corroboration
  chain — flagged here precisely because it's inference across primary
  sources, not a literal sentence inside Table E1b, so a future session
  (or the Gemini gate) can weigh that evidentiary basis for themselves
  rather than inheriting it as unconditional fact.
- **Matching BLS denominator: QCEW 2025 annual averages, Total Covered
  (`own_code=0`) minus Federal Government (`own_code=1`), all
  industries (`industry_code='10'`), per state** — i.e. Private + State
  Government + Local Government, NOT simple "Total Nonfarm" (which
  would include federal employment Table E1b's charges don't reflect).
  Sourced via BLS's Open Data CSV API
  (`https://data.bls.gov/cew/data/api/2025/a/area/{state_fips}000.csv`),
  one request per state, confirmed live 2026-09-15 (verified against
  Michigan's own numbers before running all 51: total=4,408,446,
  federal=55,758, private+state+local=4,352,688 — DC's own numbers
  also sanity-check: federal is 25% of DC's total employment, as
  expected for that jurisdiction specifically). **Current availability
  confirmed, not assumed:** 2025 is the most recent QCEW annual-average
  year published (file `Last-Modified: 2026-08-21`) — the closest
  available match to EEOC's FY2025 (Oct 2024–Sep 2025) window, given
  QCEW's inherent lag. All 51 state/DC pulls returned a real number
  with an empty `disclosure_code` (zero suppression).

## Decided, 2026-09-15d (rate-to-multiplier mechanism)

This closes the multiplier-sourcing research task in full — concept,
source, normalization base, denominator, and now the actual
rate-to-multiplier conversion are all decided.

- **National reference point: size-weighted aggregate national rate**
  — sum of all 51 jurisdictions' FY2025 EEOC Total Charges ÷ sum of
  all 51 jurisdictions' 2025 QCEW Private+State+Local employment ×
  100,000. **Not** a plain mean of the 51 individual state rates —
  that would let 51 small-denominator states pull the reference point
  away from where most of the actual workforce sits.
- **Multiplier = state rate ÷ aggregate national rate.**
- **Clamped, asymmetrically** — see "Decided, 2026-09-15e" below for
  the finalized bounds; the first-pass 0.8x–1.2x figure this bullet
  originally proposed was replaced after distribution analysis showed
  it clamped 78% of jurisdictions, well past a small-noise guard.

## Decided, 2026-09-15e (finalized clamp bounds: floor 0.25, ceiling
## 2.30; DC excluded from the multiplier table)

Pete-confirmed. This replaces the 0.8x–1.2x figure above outright —
that number is not carried forward as a default anywhere in this plan.

- **DC excluded from the multiplier table entirely.** DC's rate
  (146.197/100k, the highest of all 51 jurisdictions) is a structural
  artifact of this denominator's own design, not sample noise and not
  reliable litigation-risk signal: roughly 25% of DC's total
  employment is federal (confirmed in the QCEW pull, "Decided,
  2026-09-15c" above), and federal employment is deliberately excluded
  from the Private+State+Local denominator by design — mechanically
  shrinking DC's denominator and inflating its rate independent of
  actual filing behavior. DC's raw numerator, denominator, and
  unclamped rate remain unchanged in both Appendices above — only its
  row in the multiplier table below is omitted, footnoted there with
  this same reasoning.
- **Floor: 0.25.** Grounded in a raw-charge-count reliability gap, not
  a percentile or a ratio-value cutoff picked in isolation. Ranked by
  ratio (DC excluded, n=50), ranks 1–6 (ID, MT, ME, VT, NH, WY — ratios
  0.1092 to 0.2409) are *all* built on fewer than 100 raw EEOC charges
  for the entire fiscal year. Rank 7 (NE, ratio 0.2720) jumps to 157
  charges — a >4x increase in sample size. There's no meaningful gap in
  the *ratio* values at that boundary (0.2409 → 0.2720 is a small
  step) — the meaningful gap is in the raw counts, which a percentile
  cutoff on the ratio distribution would not reveal. 0.25 sits in that
  gap (above WY, below NE), clamping exactly the 6-state thin-sample
  cluster and nothing else.
- **Methodological finding, kept on record for future sessions: raw
  charge count alone does not select which states need floor
  protection.** AK (83 charges) and ND (99 charges) are just as
  statistically thin as the 6-state cluster above, but their ratios
  (0.4545 and 0.4096) aren't extreme — their QCEW employment
  denominators are proportionally small too, so the resulting rate
  lands mid-pack rather than at an implausible low. A blanket "any
  state under ~100 charges gets clamped" rule would have force-lowered
  these two from ordinary-looking values for no real reason. The floor
  is a clamp on the *ratio value* (`max(raw_ratio, 0.25)`), which
  naturally only touches whichever states' ratios happen to fall below
  it — raw charge count is what justifies *where* that value sits, not
  a rule for *which states* get overridden. AK and ND are correctly
  untouched under floor=0.25; a future session revisiting these bounds
  should re-derive the floor the same way (find the reliability gap in
  raw counts, then check where it lands on the ratio scale) rather
  than assume "low count" and "gets clamped" are the same test.
- **Ceiling: 2.30.** Grounded in the real non-DC maximum (AR, 2.2691 —
  not GA, which is third-highest at 2.2074, one place below AR), plus
  a small round-number margin for headroom, not an arbitrary figure
  picked without reference to the data. Confirmed this preserves every
  named real-signal state at its actual computed ratio, uncompressed:
  GA 2.2074, AL 1.7777, TN 1.5951, AR 2.2691, MS 1.9724, NC 1.5271, and
  every other non-DC state (all ≤ AR's 2.2691). Worth recording
  explicitly: even the 95th percentile of the 50-state distribution
  (1.8848) sits below MS's own ratio (1.9724) — a percentile-based
  ceiling could not have satisfied "don't compress the real-signal
  states" here at any reasonable percentile; only a ceiling grounded in
  the actual maximum could.
- **Net effect:** 6 of 50 jurisdictions clamped (12%), all at the floor
  — down from the first-pass bounds' 40 of 51 (78%). The ceiling
  affects zero jurisdictions this year; it exists purely as a
  forward-looking backstop against a future year's data exceeding
  this year's real maximum.

## Not decided / open

- Output framing: given no case-specific data is ever collected, the
  UI-facing presentation needs to read as a rough, heavily-caveated
  range, not anything resembling a real case estimate — exact
  language/framing not yet drafted.
- Whether this needs a new field on `LegalPricingResult`/
  `LegalCurveLookup` or reuses an existing shape.
- The broader gap this plan sits inside: no compensatory-damages base
  exists for ANY jurisdiction today, not just OH — this plan only
  solves it for OH. Whether that's the right scope boundary (OH-only)
  or whether the multiplier/base-salary mechanism should be built
  jurisdiction-agnostic from the start is an open architecture
  question for the Gemini gate, not decided here.

**Resolved this session, no longer open:** the clamp bounds. The
original 0.8x–1.2x first-pass figure clamped 78% of jurisdictions —
replaced with floor 0.25 / ceiling 2.30 (12% clamped, all at the
floor), derived from the actual data's reliability structure rather
than a guessed round number. Full reasoning: "Decided, 2026-09-15e"
above.

## Appendix — EEOC Table E1b, FY2025 Total Charges by state (raw
## numerator, verified 2026-09-15b, not yet normalized)

Pulled directly from the verified public XLSX (column 566, "FY 2025
Total Charges"), filtered to the 50 states + DC only (territories
excluded — see suppression note above). This is the raw numerator
kept on its own for reference; the normalized version (with the BLS
denominator applied) is the next Appendix below. Not yet used anywhere
in the engine.

```
AK: 83      HI: 218     MA: 696     NM: 505     SD: 121
AL: 2107    IA: 267     MD: 2146    NV: 1396    TN: 2942
AR: 1675    ID: 54      ME: 58      NY: 4132    TX: 9360
AZ: 1940    IL: 5180    MI: 2486    OH: 2892    UT: 408
CA: 4750    IN: 1876    MN: 1078    OK: 1004    VA: 2767
CO: 1290    KS: 759     MO: 2259    OR: 405     VT: 30
CT: 338     KY: 805     MS: 1300    PA: 4732    WA: 1724
DC: 813     LA: 1337    MT: 37      RI: 185     WI: 1002
DE: 310     -           NC: 4266    SC: 1177    WV: 132
FL: 6784    -           ND: 99      -           WY: 38
GA: 6064
```

FY2025 US-wide total (all states, DC, and territories, per the file's
own "Total" row): 88,201 charges. Ohio (`OH`): 2,892 charges, 3.3% of
the US total for FY2025.

## Appendix — computed per-state rate (EEOC FY2025 charges per 100,000
## private + state + local employees), verified 2026-09-15c

Numerator: EEOC Table E1b FY2025 Total Charges (Appendix above).
Denominator: BLS QCEW 2025 annual-average Total Covered minus Federal
Government employment, per state (this section's own sourcing note
above). Rate = charges ÷ employment × 100,000. Sorted highest to
lowest. This is a relative jurisdiction-risk signal only — explicitly
NOT a dollar figure, per the multiplier-concept decision above. Not
yet used anywhere in the engine.

| State | Charges | Priv+State+Local emp. | Rate /100k |
|---|---:|---:|---:|
| DC | 813 | 556,100 | 146.197 |
| AR | 1,675 | 1,284,297 | 130.422 |
| GA | 6,064 | 4,779,581 | 126.873 |
| MS | 1,300 | 1,146,746 | 113.364 |
| AL | 2,107 | 2,062,121 | 102.176 |
| TN | 2,942 | 3,209,041 | 91.678 |
| NV | 1,396 | 1,547,223 | 90.226 |
| NC | 4,266 | 4,860,387 | 87.771 |
| IL | 5,180 | 5,987,775 | 86.510 |
| MD | 2,146 | 2,603,713 | 82.421 |
| PA | 4,732 | 5,952,205 | 79.500 |
| MO | 2,259 | 2,843,602 | 79.441 |
| LA | 1,337 | 1,896,463 | 70.500 |
| VA | 2,767 | 3,961,540 | 69.847 |
| FL | 6,784 | 9,756,081 | 69.536 |
| TX | 9,360 | 13,887,434 | 67.399 |
| DE | 310 | 474,967 | 65.268 |
| AZ | 1,940 | 3,177,231 | 61.059 |
| OK | 1,004 | 1,648,462 | 60.905 |
| NM | 505 | 846,777 | 59.638 |
| IN | 1,876 | 3,150,977 | 59.537 |
| MI | 2,486 | 4,352,688 | 57.114 |
| KS | 759 | 1,406,687 | 53.957 |
| OH | 2,892 | 5,452,486 | 53.040 |
| SC | 1,177 | 2,283,169 | 51.551 |
| WA | 1,724 | 3,523,948 | 48.922 |
| CO | 1,290 | 2,836,914 | 45.472 |
| NY | 4,132 | 9,679,488 | 42.688 |
| KY | 805 | 1,955,240 | 41.171 |
| RI | 185 | 487,812 | 37.924 |
| NJ | 1,569 | 4,234,240 | 37.055 |
| MN | 1,078 | 2,911,560 | 37.025 |
| HI | 218 | 609,478 | 35.768 |
| WI | 1,002 | 2,915,609 | 34.367 |
| SD | 121 | 449,014 | 26.948 |
| CA | 4,750 | 17,962,398 | 26.444 |
| AK | 83 | 317,705 | 26.125 |
| UT | 408 | 1,700,830 | 23.988 |
| ND | 99 | 420,491 | 23.544 |
| OR | 405 | 1,959,447 | 20.669 |
| CT | 338 | 1,673,769 | 20.194 |
| WV | 132 | 669,784 | 19.708 |
| MA | 696 | 3,589,352 | 19.391 |
| IA | 267 | 1,540,614 | 17.331 |
| NE | 157 | 1,004,397 | 15.631 |
| WY | 38 | 274,439 | 13.846 |
| NH | 82 | 680,142 | 12.056 |
| VT | 30 | 301,478 | 9.951 |
| ME | 58 | 633,951 | 9.149 |
| MT | 37 | 498,739 | 7.419 |
| ID | 54 | 860,258 | 6.277 |

51 rows — every state + DC, no omissions, no truncation. Ohio's own
rate (53.040 per 100k) ranks 24th of 51 — solidly mid-pack, not an
outlier in either direction. For context: DC's rate (146.197, the
highest) is driven by an unusually small denominator (DC's
private+state+local employment is only 556,100 — a quarter of DC's
total employment is federal, per the QCEW pull above) rather than
necessarily a higher underlying filing rate. **Resolved, 2026-09-15e:**
this is exactly why DC is excluded from the computed-multiplier
Appendix below (structural artifact, not signal) — DC's own numerator/
denominator/rate stay unchanged here, only its multiplier-table row is
omitted.

## Appendix — computed clamped multiplier, 50 jurisdictions (DC
## excluded), finalized 2026-09-15e

Computed directly from the two appendices above (no new data pulled).
Supersedes the first-pass 0.8x–1.2x table this appendix previously
held — that table and its bounds are not carried forward as a default
anywhere in this plan.

**DC excluded from this table.** DC's own numerator (813 charges),
denominator (556,100), and unclamped rate (146.197/100k) are unchanged
in the two Appendices above — omitted here only, because DC's rate is
a structural artifact of ~25% of its total employment being federal
(excluded from this denominator by design), not sample noise and not
reliable litigation-risk signal. See "Decided, 2026-09-15e" above for
the full reasoning.

**Aggregate national rate (size-weighted, unchanged from
"Decided, 2026-09-15d" — DC's real charges/employment remain part of
the true national baseline even though DC has no row below):**
57.4765 per 100,000.

`raw multiplier = state rate ÷ 57.4765`, then `clamped = min(2.30, max(0.25, raw multiplier))`.

| State | Rate /100k | Raw multiplier | Clamped | Hit bound |
|---|---:|---:|---:|:---:|
| AR | 130.422 | 2.2691 | 2.2691 | — |
| GA | 126.873 | 2.2074 | 2.2074 | — |
| MS | 113.364 | 1.9724 | 1.9724 | — |
| AL | 102.176 | 1.7777 | 1.7777 | — |
| TN | 91.678 | 1.5951 | 1.5951 | — |
| NV | 90.226 | 1.5698 | 1.5698 | — |
| NC | 87.771 | 1.5271 | 1.5271 | — |
| IL | 86.510 | 1.5051 | 1.5051 | — |
| MD | 82.421 | 1.4340 | 1.4340 | — |
| PA | 79.500 | 1.3832 | 1.3832 | — |
| MO | 79.441 | 1.3822 | 1.3822 | — |
| LA | 70.500 | 1.2266 | 1.2266 | — |
| VA | 69.847 | 1.2152 | 1.2152 | — |
| FL | 69.536 | 1.2098 | 1.2098 | — |
| TX | 67.399 | 1.1726 | 1.1726 | — |
| DE | 65.268 | 1.1356 | 1.1356 | — |
| AZ | 61.059 | 1.0623 | 1.0623 | — |
| OK | 60.905 | 1.0597 | 1.0597 | — |
| NM | 59.638 | 1.0376 | 1.0376 | — |
| IN | 59.537 | 1.0359 | 1.0359 | — |
| MI | 57.114 | 0.9937 | 0.9937 | — |
| KS | 53.957 | 0.9388 | 0.9388 | — |
| **OH** | **53.040** | **0.9228** | **0.9228** | **—** |
| SC | 51.551 | 0.8969 | 0.8969 | — |
| WA | 48.922 | 0.8512 | 0.8512 | — |
| CO | 45.472 | 0.7911 | 0.7911 | — |
| NY | 42.688 | 0.7427 | 0.7427 | — |
| KY | 41.171 | 0.7163 | 0.7163 | — |
| RI | 37.924 | 0.6598 | 0.6598 | — |
| NJ | 37.055 | 0.6447 | 0.6447 | — |
| MN | 37.025 | 0.6442 | 0.6442 | — |
| HI | 35.768 | 0.6223 | 0.6223 | — |
| WI | 34.367 | 0.5979 | 0.5979 | — |
| SD | 26.948 | 0.4689 | 0.4689 | — |
| CA | 26.444 | 0.4601 | 0.4601 | — |
| AK | 26.125 | 0.4545 | 0.4545 | — |
| UT | 23.988 | 0.4174 | 0.4174 | — |
| ND | 23.544 | 0.4096 | 0.4096 | — |
| OR | 20.669 | 0.3596 | 0.3596 | — |
| CT | 20.194 | 0.3513 | 0.3513 | — |
| WV | 19.708 | 0.3429 | 0.3429 | — |
| MA | 19.391 | 0.3374 | 0.3374 | — |
| IA | 17.331 | 0.3015 | 0.3015 | — |
| NE | 15.631 | 0.2720 | 0.2720 | — |
| WY | 13.846 | 0.2409 | 0.2500 | floor |
| NH | 12.056 | 0.2098 | 0.2500 | floor |
| VT | 9.951 | 0.1731 | 0.2500 | floor |
| ME | 9.149 | 0.1592 | 0.2500 | floor |
| MT | 7.419 | 0.1291 | 0.2500 | floor |
| ID | 6.277 | 0.1092 | 0.2500 | floor |

50 rows, DC excluded as documented above. **6 of 50 clamped (12%)**,
all at the floor — down from the first-pass bounds' 40 of 51 (78%).
Zero jurisdictions hit the 2.30 ceiling this year (real non-DC max is
AR at 2.2691); the ceiling is a forward-looking backstop only. AK and
ND (both under 100 raw charges, same reliability profile as the 6
floored states) are correctly untouched — their own ratios aren't
extreme, per the methodological finding in "Decided, 2026-09-15e"
above.

Ohio's own multiplier: **0.9228**, unclamped — Ohio's raw ratio already
falls inside the band, confirmed as the plausibility check this
appendix exists to support: no sign error, no order-of-magnitude
error, no clamp artifact. Ohio's rate sits just under the national
average (53.040 vs. 57.4765 per 100k), producing a mild below-average
multiplier — directionally sane and unremarkable, exactly what a
plausibility check should find.

## Process

- **This mechanism is now fully specified and ready for Gemini
  architecture-gate submission (2026-09-15e).** No code has been
  written — this remains documentation only. Everything the
  methodology needs is decided:
  - Salary basis: `_INDUSTRY_WAGE_DATA` (existing BLS OEWS table), no
    individual/case-specific salary collection, ever (top of this
    document, under "Decided" — settled in the prior session).
  - Multiplier source: EEOC Table E1b charge-filing frequency,
    verified public URL, suppression checked and cleared.
  - Normalization base: BLS QCEW employment (Total Covered minus
    Federal Government), matched to Table E1b's own private +
    state/local (excl. federal) coverage.
  - National reference: size-weighted aggregate rate, not a mean of
    state rates.
  - Clamp: floor 0.25 / ceiling 2.30, asymmetric, both grounded in the
    actual data's reliability structure (raw-count gap; real non-DC
    maximum) rather than guessed round numbers — Pete-confirmed,
    2026-09-15e.
  - DC excluded from the multiplier table, footnoted, as a documented
    structural artifact rather than silently dropped or silently kept.
  See "Decided, 2026-09-15" through "2026-09-15e" and all three
  Appendices above for the full derivation and verification trail.
- **Genuinely open items remaining for the Gemini gate itself, not
  further research:** output framing (not yet drafted, given no
  case-specific data is ever collected), whether a new
  `LegalPricingResult`/`LegalCurveLookup` field is needed, the
  OH-only-vs-jurisdiction-agnostic scope question, and the
  `_INDUSTRY_WAGE_DATA` mean-vs-distribution citation-accuracy
  consequence flagged under "Decided" above — all listed in "Not
  decided / open," all explicitly for Gemini to weigh, not resolved
  unilaterally here.
- Every claim was independently verified against primary source before
  use, per standing verification discipline, given Gemini's documented
  pattern of citation fabrication in this exact codebase (real source,
  invented precision — Financial Services and Technology sector wage
  corrections this same file already required).
