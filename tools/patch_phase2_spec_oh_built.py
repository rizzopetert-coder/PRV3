"""
prompts/damages-cap-treatment-phase2-spec.md: supersede Phase 2b (OH)'s
original economic_loss/net_worth schema-gap framing with the corrected
QUALITATIVE_ONLY treatment actually built this session.

Two investigation passes preceded this build (not reflected in the spec
until now): the first found the original framing was imprecise --
economic_loss was never the real blocker (no cluster in this codebase
computes a compensatory-damages figure at all, so there's nothing to
multiply economic_loss against even if it existed), and OH's live
STATE_COVERAGE_THRESHOLDS entry was already resolving PRICED via the
generic curve, not gated at DATA_INTEGRITY_GAP/NOT_APPLICABLE as
originally assumed. The second verified specific claims from Gemini's
QUALITATIVE_ONLY architecture review against live code before treating
any of it as cleared for build (unpriced_state_ids real and confirmed;
PrivateOutput.tsx's quoted copy close but not verbatim; Cluster 4c is
NOT the only QUALITATIVE_ONLY consumer -- Cluster 3's unclassifiable-
headcount branch is a second, structurally different one, and the
closer precedent for OH; the intake-aware routing gate's mechanics are
valid against the real stored headcount int).

Usage:
    python tools/patch_phase2_spec_oh_built.py --dry-run
    python tools/patch_phase2_spec_oh_built.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('prompts/damages-cap-treatment-phase2-spec.md')

OH_SECTION_OLD = '''## Phase 2b — deferred, gated: OH

**Blocked on new intake fields that don't exist today:**
`economic_loss` and `net_worth`. Neither appears in the current intake
schema (`engine/data/intake.py`'s `INTAKE_FIELDS`) — confirmed absent,
not merely unused.

OH's real cap, per its own live comment, is a formula, not a table:

> H.B. 352 (Employment Law Uniformity Act), eff. Apr. 15, 2021, codified
> Ohio's Tort Reform Act caps onto R.C. ch. 4112 claims. R.C. 2315.18:
> non-economic compensatory capped at the greater of $250,000 or 3x
> economic loss, max $350,000. R.C. 2315.21: punitive capped at 2x
> compensatory, or for "small employers" (<=100 employees, 500 for
> manufacturing) at 10% of net worth up to $350,000.

Both branches of this formula (compensatory's `3x economic_loss` term,
punitive's `10% of net_worth` alternate path) require inputs PRV3 does
not collect. There is no honest way to compute either branch without
those two numbers — approximating them (a default economic-loss
assumption, an assumed net worth) would produce a number that looks
authoritative but is actually the user's or PRV3's own guess dressed in
arithmetic.

**Deferral reason, cited correctly this time:** the Financial
Consequence Architecture section's stated delivery rule (Section 5,
`PRV3-Principal-Brief.docx`, "Financial Consequence Architecture"
subsection — verified directly against source this session, real
verbatim text, **not** one of the 12 numbered Locked Principles in
Section 7):

> "Three rules govern delivery: credibility over calculation — no
> computed figures derived from user estimates..."

OH's formula, run against inputs PRV3 doesn't have, is exactly the
"computed figures derived from user estimates" failure mode this rule
exists to prevent. Deferring OH until `economic_loss`/`net_worth` exist
as real intake fields is a direct application of that rule, not an
arbitrary scope cut.'''

OH_SECTION_NEW = '''## Phase 2b — BUILT: OH resolves QUALITATIVE_ONLY

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
fields).'''

STATUS_OLD = '''**Phase 2b (OH): explicitly parked, not abandoned.** Gated on
`economic_loss`/`net_worth` becoming real intake fields. Revisit when
that intake-schema expansion is scheduled.'''

STATUS_NEW = '''**Phase 2b (OH): BUILT.** Resolves `QUALITATIVE_ONLY` in Clusters 1, 2,
and 4b, following Cluster 3's unclassifiable-headcount precedent. No
intake schema or UI change needed -- confirmed both `unpriced_state_ids`
and `PrivateOutput.tsx`'s unpriced-state copy already existed and needed
nothing new. `economic_loss`/`net_worth` remain genuinely absent from
intake and remain the reason no real dollar figure can be computed for
OH -- that gap blocks a future pricing build, not this status routing.'''

EDITS = [
    ('Phase 2b OH section -- superseded with built status', OH_SECTION_OLD, OH_SECTION_NEW),
    ('Status section -- Phase 2b built', STATUS_OLD, STATUS_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    errors = []
    for label, old, new in EDITS:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
