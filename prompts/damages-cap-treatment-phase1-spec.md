# damages_cap_treatment Phase 1 — Build Plan (Gemini-Reviewed, CC-Verified, Corrected)

## Why this exists

`damages_cap_treatment` has existed on `StateCoverageThreshold` since the
PARTIAL-state coverage-threshold verification workstream (completed
2026-09-10, all 51 jurisdictions CONFIRMED), but is fully unconsumed by
any pricing logic today — confirmed directly, not assumed: grepped every
occurrence of the field in `engine/friction_tax.py` and every
`.damages_cap_treatment` attribute access; zero hits outside data-row
assignments and docstring/comment text. `state-coverage-threshold-
design.md`'s own Next Steps section flagged this as a "separate, larger
design question" from the applicability gate it built. This is that
design question's Phase 1 build plan — write-the-plan-down step only,
per standing discipline. **Nothing in this document has been built.**

## Two corrections applied against the original Gemini proposal

Both caught by independent verification against live code before this
plan was written down, not accepted at face value:

1. **"Reuse existing `federal_cap_applies` branching logic" — corrected
   to net-new.** Gemini's proposal described item 2 below as reusing an
   existing code path. Confirmed directly (grep + attribute-access
   search, `engine/friction_tax.py`): no code anywhere distinguishes
   `federal_cap_applies` from `uncapped` today. Nothing reads
   `damages_cap_treatment` at all. There is nothing to reuse — the
   federal-floor branch in item 2 is net-new logic, not an extension of
   something that already exists.
2. **The uncapped-state list used to scope item 3 — verified, not
   assumed.** Gemini's review named CA/NY/NJ/WA/MA/IL as an illustrative
   uncapped-state example set. Confirmed directly against
   `STATE_COVERAGE_THRESHOLDS`: **IL is `federal_cap_applies`, not
   `uncapped`** — it does not belong in this set. The real, full
   `uncapped` list is 23 states, not the 5-6 named as examples (full
   list under item 3 below). Item 3's fix must be scoped to all 23, not
   just the named examples.

## Scope

### 1. `resolve_damages_treatment(jurisdictions: list[str]) -> str`

New helper. Highest-exposure-wins across selected CONFIRMED
jurisdictions, in this priority order:

```
uncapped > state_specific_tiers / state_specific_flat > federal_cap_applies > no_damages_available
```

`state_specific_tiers` and `state_specific_flat` are peers in this
ordering (both represent "a real independent state cap exists," ranked
below `uncapped` and above `federal_cap_applies` — the two don't need a
relative order against each other for this helper's purpose, since a
downstream caller cares whether a cap exists and how it's shaped, not
which shape wins a multi-state tie).

### 2. Federal-floor branch for `no_damages_available` (NET-NEW logic)

Confirmed net-new per the correction above — nothing to extend, nothing
to reuse.

- `headcount >= 15`: treat as `federal_cap_applies`, price against the
  existing generic curve normally (no new ceiling logic needed here —
  falls through to whatever `federal_cap_applies` states already do,
  once item 3's open question is resolved for the general case).
- `headcount < 15`: return `LegalPricingStatus.NOT_APPLICABLE`,
  `dollar_range=None`, `coverage_confidence="CONFIRMED"` — state law
  bars damages outright and federal coverage doesn't attach at this
  headcount, so there is genuinely no exposure to price, not an
  unpriced-but-real one.

The 7 `no_damages_available` states this branch applies to (verified
directly against `STATE_COVERAGE_THRESHOLDS`, count and membership
confirmed): **AZ, ND, OK, SC, UT, WI, WY.**

### 3. Cluster 4b uncapped-state fix — RESOLVED, Pete's decision

**No longer a Phase 1 blocker.** Resolved as a display/output-layer
decision, not a new pricing mechanism — the underlying `(v, v)`
computation is unchanged for these states.

Cluster 4b's real ceiling table (`_CLUSTER_4B_CEILING_BY_HEADCOUNT`,
confirmed live): floor `$25,000`; ceiling ranges `$50,000` (Under 25 /
25-99) → `$75,000` (100-249) → `$200,000` (250-499) → `$300,000`
(500-999 / 1000+). This table is a mapped approximation of the federal
Title VII/ADA statutory bracket table (42 U.S.C. § 1981a(b)(3)) onto
this project's own headcount-bucket scheme — not a literal reproduction
of the statute's own 15-100/101-200/201-500/500+ tiers, and the
100-249 bucket's `$75,000` value is itself a midpoint approximation of
the statute's $50k-$100k straddle (Addendum 10's documented design
choice), not a number pulled directly from source.

**Pete's decision:** keep applying this same federal ceiling table to
the 23 `uncapped` states' Cluster 4b claims — do not build a new
pricing path or a materially different synthetic ceiling for them.
Instead, change how the figure is *displayed* for these 23 states
specifically: append a `+` to the rendered dollar figure (e.g.
"$300,000+"), and add a small clarifying note underneath stating that
real exposure may exceed this amount, since the state imposes no
statutory cap. The federal table is being reframed as a floor for
these states, not a hard ceiling — the number itself doesn't change,
only the framing around it.

**Full 23-state `uncapped` list this covers** (verified directly
against `STATE_COVERAGE_THRESHOLDS`, not the 5-6 illustrative examples
Gemini's review named): CA, CT, DC, HI, IA, IN, KY, LA, MA, MI, MN, MT,
NE, NH, NJ, NM, NY, OR, PA, RI, SD, VT, WA.

**Where this actually gets built:** this is output-layer work (the `+`
character and the clarifying note render wherever Legal/Compliance
dollar figures eventually reach a client, e.g. `PrivateOutput.tsx` per
`state-coverage-threshold-design.md`'s own output-generation-constraint
section) — and per that same document, Legal/Compliance dollar output
isn't wired into any client-facing surface at all today. This is a spec
note for whenever that output wiring is built, not something to
implement against a real component right now. Phase 1's own pricing
logic (Cluster 4b's `(v, v)` computation) needs no change for this
item — it's fully resolved as a future-output-layer instruction, not a
pending pricing decision.

### 4. Flat-cap clamp for `state_specific_flat` states — RESOLVED, Pete's decision

**No longer an open question.** Same resolution pattern as item 3:
clamp logic unchanged, display treatment fixed to reflect what the
number actually represents.

New field on `StateCoverageThreshold`: `flat_cap: Optional[float]`.
Populate for the 4 `state_specific_flat` states, values pulled directly
from each state's existing citation comment (verified against live
source, not transcribed from the task description unchecked):

| State | flat_cap | Source (verbatim from the live comment) |
|---|---|---|
| FL | `$100,000` | "flat $100,000 punitive cap, no size-based tiers, Fla. Stat. §760.11(5)" |
| ID | `$1,000` | "punitive damages capped at a flat $1,000 per willful violation" |
| KS | `$2,000` | "$2,000 flat cap on pain/suffering/humiliation damages specifically" |
| VA | `$350,000` | "flat $350,000 punitive cap, Va. Code §8.01-38.1" |

Clamp stays exactly as specified: `min(curve.ceiling, flat_cap)`.

**Verification finding (prior pass, this session):** these four caps
are not all the same *kind* of cap, and none of them bound total dollar
exposure the way Cluster 1/4b's curve ceiling represents a single
blended figure. FL and VA cap punitive damages specifically; KS caps
non-economic (pain/suffering/humiliation) damages specifically; ID caps
punitive-per-willful-violation specifically. **Confirmed directly, not
inferred, for ID:** its own live comment states economic/actual damages
are "available separately, uncapped by this provision" — the $1,000
figure has near-zero relationship to ID's real total exposure once
economic damages are added. **Unconfirmed either way for FL/KS/VA:**
none of their three comments say anything about how the state treats
damage types outside their own narrow cap — plausibly the same pattern
as ID, but not verified from what exists in this codebase.

**Pete's decision:** treat all four states uniformly rather than
assuming FL/KS/VA are narrow like ID or broad like nothing at all.
Clamp logic is unchanged for all four — `min(curve.ceiling, flat_cap)`
still produces the displayed dollar figure. What changes is the
*display*: the same floor-not-ceiling pattern as item 3's uncapped-state
fix — append a `+` to the rendered figure (e.g. "$100,000+") and add a
clarifying note stating the number reflects only the specific
damage-type slice the state's flat cap actually governs (punitive,
non-economic, etc.), not the client's full real exposure. Same
output-layer scope as item 3: this renders wherever Legal/Compliance
dollar output eventually reaches a client (e.g. `PrivateOutput.tsx`),
which per `state-coverage-threshold-design.md`'s own
output-generation-constraint section has no real consumer yet — a spec
note for that future wiring, not something to implement against a real
component today.

**VA's Cluster 4b no-op, noted as-is (informational, not a bug):**
VA's `flat_cap` ($350,000) never actually binds under Cluster 4b at any
headcount bucket, confirmed directly — the generic ceiling tops out at
$300,000 (500-999 / 1000+ buckets), already below VA's own cap, so
`min(300000, 350000) = 300000` everywhere in that cluster. The clamp
does bind under Cluster 1, whose $450,000 ceiling sits above VA's
$350,000 cap. Nothing to fix here — VA's Cluster 4b output should still
get the same `+`/note display treatment as the other three states,
since the underlying ambiguity (does the generic ceiling reflect VA's
real total exposure?) is identical whether or not the clamp happens to
change the number for a given headcount bucket.

### 5. Explicitly deferred to Phase 2: `state_specific_tiers`

**9 states, verified against `STATE_COVERAGE_THRESHOLDS`: AR, CO, DE,
MD, ME, MO, OH, TN, TX.**

No schema exists for tiered or formula-based cap data today (`StateCoverageThreshold`
has no field that could hold a tier table or a formula). Ohio
specifically cannot be represented as a simple lookup table even if one
existed — its real cap is a formula ("greater of $250,000 or 3x
economic loss, max $350,000" for compensatory; "2x compensatory, or
10% of net worth up to $350,000" for punitive, with a separate
small-employer carve-out), confirmed directly from its own live
comment. Building real support for this class is out of scope for
Phase 1.

**Phase 1's obligation for these 9 states:** whenever
`coverage_basis == "state_specific"` resolves to one of these 9 states,
attach an explicit output caveat noting the ceiling shown does **not**
yet reflect that state's real, independently-capped exposure — the
generic curve's ceiling is being shown as a placeholder, not a
verified figure, for these 9 specifically.

## Not in scope for this document

- Per-state claim-type mapping (harassment vs. general) — separately
  tracked in `state-coverage-threshold-design.md`'s own Next Steps,
  unchanged by this plan.
- The aggregate-vs-in-state-only headcount-counting question — same,
  unchanged, tracked in the same document.
- Any actual code change. This is a plan, not a diff.

## Verification standard applied to this document

Every number and list in this file was independently confirmed against
live `engine/friction_tax.py` source before being written down here —
not transcribed from the task description or the Gemini review
unchecked. Specifically re-verified for this document: NJ's live entry;
the full live `_CLUSTER_4B_CEILING_BY_HEADCOUNT`/`_CLUSTER_4B_FLOOR`
values; the absence of any `damages_cap_treatment` branching logic
anywhere in the file; the full 7-member `no_damages_available` list;
the full 23-member `uncapped` list (including the IL correction); and
all four `state_specific_flat` dollar figures against their own live
citation comments.

## Status

Plan only. Not started. Items 3 and 4 (Cluster 4b's uncapped-state
ceiling; the flat-cap clamp's display for FL/ID/KS/VA) are both now
resolved — Pete's decisions, recorded above, both display-layer
instructions for whenever Legal/Compliance output wiring is built, not
pending decisions. No item in this plan has an open question blocking
Phase 1 completion.
