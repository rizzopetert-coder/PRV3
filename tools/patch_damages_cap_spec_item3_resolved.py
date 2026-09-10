"""
prompts/damages-cap-treatment-phase1-spec.md: item 3 (Cluster 4b's
ceiling for the 23 uncapped states) is now resolved -- Pete's decision:
keep the existing federal ceiling table, but render it as a floor
rather than a hard ceiling (append "+" to the displayed figure, add a
clarifying note that real exposure may exceed it). Display/output-layer
decision only -- the underlying (v,v) computation is unchanged. Updates
the item 3 section header/content and the Status section to reflect
this as resolved, no longer a Phase 1 blocker.

Usage:
    python tools/patch_damages_cap_spec_item3_resolved.py --dry-run
    python tools/patch_damages_cap_spec_item3_resolved.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('prompts/damages-cap-treatment-phase1-spec.md')

ITEM3_OLD = '''### 3. Cluster 4b uncapped-state fix — OPEN QUESTION, NOT RESOLVED, BLOCKS PHASE 1 COMPLETION

**This is the one piece of this plan that cannot be built as scoped.
Flagging prominently, not guessing at an answer.**

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

For any of the 23 `uncapped` states, this federal ceiling table is
currently applied to Cluster 4b claims regardless — but an `uncapped`
state, by definition, has **no independent state cap to fall back to**.
Capping an uncapped state's exposure at the federal Title VII ceiling
silently understates real exposure for exactly the states where the
real law says there is no ceiling at all.

**Full 23-state `uncapped` list this fix must cover** (verified
directly against `STATE_COVERAGE_THRESHOLDS`, not the 5-6 illustrative
examples Gemini's review named): CA, CT, DC, HI, IA, IN, KY, LA, MA,
MI, MN, MT, NE, NH, NJ, NM, NY, OR, PA, RI, SD, VT, WA.

**What was NOT resolved by either review, and needs Pete's input before
this piece can be built:** if an uncapped state's real law imposes no
statutory ceiling, what ceiling (if any) should Cluster 4b actually use
for that state's dollar output? Options that exist but are not
adjudicated here — a materially higher synthetic ceiling, an
open-ended/qualitative-only treatment instead of a point dollar figure,
some other design — no recommendation is made in this document. This
is a real clinical/product judgment call, not an engineering detail,
and Phase 1 is not complete until it's answered.'''

ITEM3_NEW = '''### 3. Cluster 4b uncapped-state fix — RESOLVED, Pete's decision

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
pending pricing decision.'''

TAIL_OLD = '''## Status

Plan only. Not started. Item 3 (Cluster 4b's uncapped-state ceiling)
is an open decision blocking Phase 1 completion — needs Pete's input,
not further investigation, before implementation can proceed on that
piece. Items 1, 2, 4, and 5 have no open questions blocking them.'''

TAIL_NEW = '''## Status

Plan only. Not started. Item 3 (Cluster 4b's uncapped-state ceiling)
is now resolved — Pete's decision, recorded above; a display-layer
instruction for whenever Legal/Compliance output wiring is built, not
a pending decision. No item in this plan currently blocks Phase 1
completion.'''

EDITS = [
    ('item 3: resolved per Pete\'s decision', ITEM3_OLD, ITEM3_NEW),
    ('Status: no remaining blockers', TAIL_OLD, TAIL_NEW),
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
