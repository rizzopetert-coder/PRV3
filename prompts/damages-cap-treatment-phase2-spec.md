# damages_cap_treatment Phase 2 — Build Plan (spec only, not built)

## Why this exists

Phase 1 (`prompts/damages-cap-treatment-phase1-spec.md`, item 5) explicitly
deferred all 9 `state_specific_tiers` states to Phase 2, on the finding
that no schema existed for tiered or formula-based cap data and that at
least one state (Ohio) couldn't be represented as a lookup table even
if one existed. This document is that Phase 2 plan.

**Correction against the original single-phase proposal:** a unified
schema across all 9 states was considered and rejected. The 9 states do
not share one shape — 7 are genuinely simple lookup problems, 1 is a
formula that needs intake fields PRV3 doesn't collect today, and 1 has
an internally-flagged, unresolved data-verification gap on part of its
own figures. Building one schema to cover all three would either
under-fit the 7 clean states (waiting on OH's and ME's gates for no
reason) or over-fit them (forcing formula/verification-gap handling
onto states that don't need it). This plan splits the work into three
independently-gated sub-phases instead. **Nothing in this document has
been built.**

## Phase 2a — buildable now, zero open blockers

**7 states: AR, DE, TN, MD, MO, TX, CO.**

### AR, DE, TN — straightforward headcount-tiered dollar tables

No complications. Verified directly against each state's live comment
in `STATE_COVERAGE_THRESHOLDS`:

| State | Tiers | Citation |
|---|---|---|
| AR | $15,000 (<15) / $50,000 (15-100) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (500+) | Ark. Code §16-123-107(c)(2)(B) |
| DE | $50,000 (4-14) / $75,000 (15-100) / $175,000 (101-200) / $300,000 (201-500) / $500,000 (500+) | 19 Del. C. §715(c) |
| TN | $25,000 (8-14) / $50,000 (15-100) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (500+) | T.C.A. §4-21-313(a) |

### MD, MO — combined compensatory-and-punitive caps

New field on `StateCoverageThreshold`: `is_combined_cap: bool = False`.
Set `True` for these two states only.

| State | Tiers | Citation |
|---|---|---|
| MD | $50,000 (15-100) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (501+) — confirmed via §20-1013(e)(2) as a COMBINED cap, not compensatory-only with punitive separately uncapped | Md. State Gov't Code §20-1009(b)(3), §20-1013(e)(2) |
| MO | $50,000 (6-100) / $100,000 (101-200) / $200,000 (201-500) / $500,000 (500+) — combined non-pecuniary-and-punitive cap; back pay/front pay explicitly outside the cap | RSMo §213.111(4) |

Both states' own existing comments already state this explicitly — the
field isn't inferring anything new, it's giving that already-verified
fact a place to live in the schema.

**Why build this now, even though no output layer splits compensatory
from punitive today:** same reasoning Phase 1 applied to `is_floor` —
encode the statutory truth at the data layer as soon as it's known,
rather than waiting for a consuming feature to exist. If a future
"detailed damages breakdown" feature reads MD's or MO's cap and (not
knowing it's combined) treats it as two independent caps — one
compensatory, one punitive — it would silently double the real
exposure figure. `is_combined_cap` sitting unused today costs nothing;
the alternative (adding it retroactively, after a breakdown feature
already shipped without it) risks exactly the kind of quiet
overstatement bug this codebase has caught and fixed before.

### TX — ship with `is_floor=True`

Reuses Phase 1's existing `is_floor` field and pattern — no new
mechanism.

| State | Tiers | Citation |
|---|---|---|
| TX | $50,000 (<101) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (500+) | Tex. Lab. Code §21.2585(d) |

TX's own comment flags a real carve-out: §21.2585(f) removes this cap
entirely for sexual-assault and sex-based-harassment/retaliation claims
specifically. The schema's dollar figure is accurate for general
claims, but may overstate — or simply not apply — for that claim-type
subset. This codebase can't distinguish that subset today: claim types
are tracked only as `claim_type="general"` vs. the narrow
`"fmla"`/threshold distinctions already in `_FEDERAL_THRESHOLD_BY_CLAIM_TYPE`,
with no sexual-assault/harassment-retaliation claim-type category at
all — a separately-tracked, pre-existing limitation (Phase 1 spec's
"Not in scope" section: "Per-state claim-type mapping").

`is_floor=True` is the correct signal here for the same reason it's
correct for `uncapped` and `state_specific_tiers` states generally: the
number shown is not guaranteed to be the client's real ceiling. **TX's
shipment is not gated on fixing the broader claim-type-mapping
limitation** — that's tracked separately and remains out of scope for
this document, same as it was for Phase 1.

### CO — new connecting logic, not a new data mechanism

| State | Tiers | Citation |
|---|---|---|
| CO | $10,000 (1-4) / $25,000 (5-14), then federal Title VII tiers apply at 15+ | C.R.S. §24-34-405(3)(d)(I), (II)(A)/(II)(B) |

CO is the only one of these 7 (and the only one of all 9
`state_specific_tiers` states) whose own comment explicitly describes
deferring to federal tiers above a headcount threshold. No new data
table or new field is needed for this — every piece already exists in
`engine/friction_tax.py`, confirmed live:

- `_FEDERAL_DEFAULT_THRESHOLD = 15` — already the live constant for "federal
  considerations attach at 15+," already used by `resolve_coverage_gate()`'s
  own fallback and by Phase 1's `no_damages_available` federal-floor branch.
- `_CLUSTER_4B_CEILING_BY_HEADCOUNT` — this genuinely *is* the federal
  Title VII/ADA tier table CO's statute defers to (comment: "Addendum
  5's real Title VII/ADA statutory bracket table, 42 U.S.C. Sec
  1981a(b)(3)"). Already real data, already in production use as
  Cluster 4b's baseline ceiling for `uncapped`/`federal_cap_applies`
  states.
- `resolve_headcount_bucket(headcount)` — already converts a raw
  headcount int into exactly the bucket keys
  (`"Under 25"`/`"25-99"`/`"100-249"`/`"250-499"`/`"500-999"`/`"1000+"`)
  `_CLUSTER_4B_CEILING_BY_HEADCOUNT` is keyed by.

**What's actually needed:** a conditional branch connecting these three
existing pieces for CO specifically — at
`headcount >= _FEDERAL_DEFAULT_THRESHOLD`, look up the ceiling via
`resolve_headcount_bucket()` + `_CLUSTER_4B_CEILING_BY_HEADCOUNT` instead
of CO's own two tiers. **Structural shape to mirror:** Phase 1's
`no_damages_available` federal-floor branch (`if treatment ==
"no_damages_available" and headcount < _FEDERAL_DEFAULT_THRESHOLD: return
NOT_APPLICABLE`) is the closest existing precedent for "a headcount
comparison against `_FEDERAL_DEFAULT_THRESHOLD` changes which pricing
path runs." **The semantics are inverted, not identical** — that branch
gates coverage *off* below the threshold; CO's branch swaps *in* a
substitute dollar table above the threshold. Do not copy that branch's
logic directly; mirror its shape (a headcount check against the same
constant, placed at the same point in resolution) while building the
opposite direction of effect.

## Phase 2b — BUILT: OH resolves QUALITATIVE_ONLY

**Superseded framing, corrected across two investigation passes before
this build.** The original economic_loss/net_worth schema-gap framing
above was imprecise on its own terms, confirmed directly against live
code: `economic_loss` was never really the blocker, since no cluster in
this codebase computes a compensatory-damages figure at all (grepped —
every "compensatory" hit anywhere in `engine/friction_tax.py` is
comment/citation prose, never a computed value) — there is nothing to
multiply `economic_loss` against even if the field existed. And OH's
live `STATE_COVERAGE_THRESHOLDS` entry was never actually gated —
confirmed by running the real pipeline, it resolved `PRICED` via the
generic curve every other un-built `state_specific_tiers` state falls
through to, not `DATA_INTEGRITY_GAP`/`NOT_APPLICABLE` as first assumed.

OH's real cap, per its own citation comment
(`engine/friction_tax.py`, `STATE_COVERAGE_THRESHOLDS["OH"]`):

> H.B. 352 (Employment Law Uniformity Act), eff. Apr. 15, 2021, codified
> Ohio's Tort Reform Act caps onto R.C. ch. 4112 claims. General
> employer: punitive damages capped at 2x compensatory damages, no
> dollar ceiling, no net-worth alternative (R.C. 2315.21(D)(2)). Small
> employer (<=100 FT employees, or <=500 if NAICS-manufacturing-
> classified) or individual defendant: capped at the LESSER of 2x
> compensatory OR 10% of net worth at time of tort, up to $350,000
> (R.C. 2315.21(D)(2)(b)).

**Resolution: `QUALITATIVE_ONLY`, not a dollar figure of any kind, in
all three clusters that consult `resolve_damages_treatment()`** (1, 2,
and 4b — confirmed by reading the live code that OH's gap applies
identically to all three, unlike CO's Phase 2a fix, which only belonged
in Cluster 4b). Mirrors Cluster 3's unclassifiable-headcount precedent
(`engine/friction_tax.py`, real non-zero exposure that genuinely can't
be resolved to a number right now) rather than Cluster 4c's Government
case (no data exists by design) — confirmed this session these are two
structurally different existing `QUALITATIVE_ONLY` consumers, not one,
correcting an initial architecture-review claim that Cluster 4c was the
only precedent.

**No intake schema change, no UI change.** `unpriced_state_ids` /
`has_unpriced_conditions` already exist and already flow OH's new
status through `compute_legal_compliance_exposure()` →
`engine/contract.py`'s `legal_tail_risk_exposure` → the existing
non-null guard (`low is not None or has_unpriced_conditions`) →
`PrivateOutput.tsx`'s already-status-agnostic unpriced-state copy,
proven by the same live pipeline the Government/Cluster 4c case already
exercises. `economic_loss`/`net_worth` remain genuinely absent from
intake (confirmed again this session) and remain the right reason
nothing in this codebase computes OH's real dollar figures — but that
absence blocks a future *pricing* build for OH, not this session's
`QUALITATIVE_ONLY` routing, which needs neither field.

**Small-employer routing built but deliberately not wired into any
pricing branch.** `_oh_is_small_employer()` (headcount <= 100, OR
industry == "Manufacturing & Industrial" AND headcount <= 500 — R.C.
2315.21(D)(2)(b)'s own gate) exists as a standalone, directly-tested
helper, since both of R.C. 2315.21's branches resolve to the identical
`QUALITATIVE_ONLY` result today — calling it from the pricing path
would compute a real answer and discard it. Ready for whenever a future
citation/prose distinction or a real pricing path for either branch is
built. Flagged, not resolved: this app's "Manufacturing & Industrial"
intake bucket is not identical to OH's real NAICS-manufacturing test
(may sweep in adjacent non-manufacturing industrial activity like
utilities or mining) — noted in `_oh_is_small_employer()`'s own
docstring and in `STATE_COVERAGE_THRESHOLDS["OH"]`'s citation comment,
since no NAICS-level intake data exists to resolve it precisely.

**Credibility-over-calculation note carried forward, still accurate:**
the Financial Consequence Architecture section's stated delivery rule
(Section 5, `PRV3-Principal-Brief.docx`, "Financial Consequence
Architecture" subsection — verified directly against source, real
verbatim text, **not** one of the 12 numbered Locked Principles in
Section 7) — *"credibility over calculation — no computed figures
derived from user estimates"* — remains the reason OH gets
`QUALITATIVE_ONLY` rather than an approximated number. What changed is
only the specific mechanism (a real status this codebase already has a
tested, end-to-end path for) and the specific blocker identified
(compensatory-figure architecture, not a pair of missing intake
fields).

## Phase 2c — deferred, gated: ME

**Blocked on independent verification of ME's own flagged gap.** ME's
existing live comment already states the problem — this isn't a new
finding, it's an existing internal flag being respected rather than
built past:

> <15 employees: "civil penal damages" only (not traditional
> compensatory/punitive), tiered $20,000 (1st order) / $50,000 (2nd
> order) / $100,000 (3rd+ order). 15+ employees: traditional
> compensatory and punitive damages, tiered up to $500,000 at the top
> employer-size bracket — exceeds Title VII's $300,000 federal maximum.
> Only the <15 tiers and the $500,000 ceiling were independently
> verified this session — intermediate 15+-employee tier breakpoints
> were NOT verified; confirm against 5 M.R.S. §4613(2)(B)(7)-(8)
> directly before relying on them for anything beyond the applicability
> gate this field doesn't yet drive.

The gap is narrow: the **<15 civil-penal tiers** ($20k/$50k/$100k by
violation order) and the **confirmed $500,000 top-bracket ceiling** for
15+ employees are both already independently verified and remain
accurately captured regardless of this deferral. What's blocked is only
the **intermediate 15+ tier breakpoints** — the dollar values at
whatever brackets exist between the 15-employee floor and the top
bracket, never independently confirmed against primary statute text.

**Deferral reason, cited correctly:** this is an extension of the
existing PARTIAL/CONFIRMED data-confidence discipline (MOB Section
13a) applied to this one internally-flagged sub-detail, **not** a
separately-named "Verification Before Build" doctrine — confirmed
directly this session that no such named discipline exists anywhere in
this codebase's documentation (`CLAUDE.md`, `tools/_mob.txt`, every
`prompts/*.md` grepped directly; zero matches for "verification before
build" or close variants). ME's own top-level `confidence` field
already reads `"CONFIRMED"` — this gap is a documented sub-detail within
an otherwise-confirmed entry, the same kind of partial-confidence
situation the PARTIAL/CONFIRMED distinction exists to flag, applied at
finer granularity than the state level.

Building ME's 15+ tier structure without resolving this first would
mean shipping a specific dollar-by-headcount table whose middle values
are, by ME's own admission, unverified against source — exactly the
condition the PARTIAL/CONFIRMED discipline exists to keep out of
anything treated as CONFIRMED data.

## Not in scope for this document

- Per-state claim-type mapping (the sexual-assault/harassment-
  retaliation subset TX's carve-out needs) — unchanged, tracked
  separately per Phase 1's own "Not in scope" section.
- The aggregate-vs-in-state-only headcount-counting question — same,
  unchanged.
- Any actual code change, including CO's connecting logic. This is a
  plan, not a diff.
- Resolving OH's or ME's gates. Adding `economic_loss`/`net_worth` to
  the intake schema and re-verifying ME's 15+ breakpoints against 5
  M.R.S. §4613(2)(B)(7)-(8) are both separate pieces of work this
  document does not attempt.

## Verification standard applied to this document

Every citation, dollar figure, and existing-mechanism claim in this
file was independently confirmed against live source before being
written down — not assumed from the task description. Specifically
re-verified this session: the raw comment/citation text for all 9
`state_specific_tiers` states, read directly from
`engine/friction_tax.py`; the exact wording and section placement of
"credibility over calculation" in `PRV3-Principal-Brief.docx`
(confirmed real and verbatim, confirmed **not** a numbered Locked
Principle by reading all 12 P-01–P-12 entries directly); the absence of
any named "Verification Before Build" discipline anywhere in this
codebase's documentation (direct grep, zero matches); and the live
existence and exact behavior of `_FEDERAL_DEFAULT_THRESHOLD`,
`_CLUSTER_4B_CEILING_BY_HEADCOUNT`, `resolve_headcount_bucket()`, and
Phase 1's `no_damages_available` branch as reusable pieces for CO's
Phase 2a logic.

## Status

**Phase 2a (AR, DE, TN, MD, MO, TX, CO): zero open blockers. Ready to
build.** Every field, constant, and helper function it needs either
already exists (`is_floor`, `_FEDERAL_DEFAULT_THRESHOLD`,
`_CLUSTER_4B_CEILING_BY_HEADCOUNT`, `resolve_headcount_bucket()`) or is
a small, well-scoped addition (`is_combined_cap`) with no open design
question attached.

**Phase 2b (OH): BUILT.** Resolves `QUALITATIVE_ONLY` in Clusters 1, 2,
and 4b, following Cluster 3's unclassifiable-headcount precedent. No
intake schema or UI change needed -- confirmed both `unpriced_state_ids`
and `PrivateOutput.tsx`'s unpriced-state copy already existed and needed
nothing new. `economic_loss`/`net_worth` remain genuinely absent from
intake and remain the reason no real dollar figure can be computed for
OH -- that gap blocks a future pricing build, not this status routing.

**Phase 2c (ME): explicitly parked, not abandoned.** Gated on
independent primary-source verification of the 15+ tier breakpoints
against 5 M.R.S. §4613(2)(B)(7)-(8). Revisit when that verification
pass is scheduled — likely a small, self-contained piece of work
whenever the next PARTIAL/CONFIRMED-adjacent verification pass runs.
