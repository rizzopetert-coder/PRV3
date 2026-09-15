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

## Not decided / open

- **Normalization base — not chosen.** State population (Census) vs.
  state private-sector employment (BLS). Two options, tradeoffs laid
  out below, not decided:
  - **Option A — Census state population.** *For:* simplest, single
    well-known figure per state, no ambiguity about which employment
    category counts, easy to source and re-verify each cycle.
    *Against:* an EEOC charge is filed by an employee against an
    employer — population includes children, retirees, the unemployed,
    and everyone else who structurally cannot generate a charge. A
    state with an older or less working-age population would look
    artificially "safer" by this measure for reasons that have nothing
    to do with actual employment-litigation exposure.
  - **Option B — BLS private-sector employment (e.g. QCEW or CES,
    state-level).** *For:* directly matches the population capable of
    generating a charge in the first place — closer to a genuine
    per-employee filing rate, and consistent with this codebase's
    existing sourcing standard (`_INDUSTRY_WAGE_DATA` is already BLS
    OEWS). *Against:* introduces a second live BLS dataset to source,
    verify, and keep in sync on its own refresh cycle, separate from
    the wage table; "private-sector" vs. "total nonfarm" vs.
    "civilian labor force" are different BLS series with different
    scope (e.g. public-sector employees can also file EEOC charges
    against government employers) — which exact series is the right
    denominator isn't yet researched, just the general category.
  Not picked here — Pete/Claude.ai's call.
- Once a normalization base is chosen: compute the actual per-state
  rate (FY2025 Total Charges ÷ chosen denominator, per state) and
  report the numbers with verification notes. No engine integration
  yet, no Gemini submission yet at that point either — still gated by
  the Process section below. The raw numerator (FY2025 Total Charges,
  all 50 states + DC) is already pulled and verified above; only the
  denominator choice is blocking the actual rate computation.
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

## Appendix — EEOC Table E1b, FY2025 Total Charges by state (raw
## numerator, verified 2026-09-15b, not yet normalized)

Pulled directly from the verified public XLSX (column 566, "FY 2025
Total Charges"), filtered to the 50 states + DC only (territories
excluded — see suppression note above). This is the raw numerator
only — no denominator applied yet, since the normalization base isn't
chosen. Not yet used anywhere in the engine.

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

## Process

- This entire methodology (new pricing capability, new legal-content
  claim) requires the Gemini architecture gate before any code is
  written — not yet submitted.
- Multiplier research status (2026-09-15): concept resolved (EEOC
  charge-filing frequency, normalized) and primary source verified
  (see "Decided, 2026-09-15" above and the Appendix's raw numerator).
  Still open: normalization base (Census population vs. BLS
  employment, options laid out above, not chosen) and, once chosen,
  the actual per-state rate computation. Every claim gets
  independently verified against primary source before use, per
  standing verification discipline, given Gemini's documented pattern
  of citation fabrication in this exact codebase (real source,
  invented precision — Financial Services and Technology sector wage
  corrections this same file already required).
