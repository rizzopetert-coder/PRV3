"""
prompts/damages-cap-treatment-phase1-spec.md: item 4 (the flat-cap
clamp for FL/ID/KS/VA) gets the same treatment item 3 just got. Clamp
logic stays as specified (min(curve.ceiling, flat_cap)) -- the display
gets the same floor-not-ceiling "+" and clarifying-note pattern as the
uncapped-state fix, applied uniformly to all four states since the
narrow-vs-broad scope of the non-flat-capped damage types is confirmed
only for ID and unconfirmed either way for FL/KS/VA. VA's Cluster 4b
no-op (flat_cap $350k never binds against a $300k max generic ceiling)
is noted as informational, not a bug. Updates the Status section to
confirm no items remain blocking Phase 1.

Usage:
    python tools/patch_damages_cap_spec_item4_resolved.py --dry-run
    python tools/patch_damages_cap_spec_item4_resolved.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('prompts/damages-cap-treatment-phase1-spec.md')

ITEM4_OLD = '''### 4. Flat-cap clamp for `state_specific_flat` states

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

Clamp: `min(curve.ceiling, flat_cap)`.

**Scoping caveat, not previously flagged by either review:** these four
caps are not all the same *kind* of cap. FL and VA cap punitive damages
specifically; KS caps non-economic (pain/suffering/humiliation) damages
specifically; ID caps punitive-per-willful-violation specifically. None
of the four caps stated in the underlying statutes are a cap on total
dollar exposure the way Cluster 1/4b's curve represents a single
blended figure. The clamp as specified treats `flat_cap` as if it
bounds the same quantity the curve's `ceiling` represents — that
equivalence is an implicit simplification this plan is adopting, not a
verified fact about how these four statutes actually work. Worth
Pete's awareness even though it isn't being escalated as a blocker on
the same level as item 3.'''

ITEM4_NEW = '''### 4. Flat-cap clamp for `state_specific_flat` states — RESOLVED, Pete's decision

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
change the number for a given headcount bucket.'''

TAIL_OLD = '''## Status

Plan only. Not started. Item 3 (Cluster 4b's uncapped-state ceiling)
is now resolved — Pete's decision, recorded above; a display-layer
instruction for whenever Legal/Compliance output wiring is built, not
a pending decision. No item in this plan currently blocks Phase 1
completion.'''

TAIL_NEW = '''## Status

Plan only. Not started. Items 3 and 4 (Cluster 4b's uncapped-state
ceiling; the flat-cap clamp's display for FL/ID/KS/VA) are both now
resolved — Pete's decisions, recorded above, both display-layer
instructions for whenever Legal/Compliance output wiring is built, not
pending decisions. No item in this plan has an open question blocking
Phase 1 completion.'''

EDITS = [
    ('item 4: resolved per Pete\'s decision', ITEM4_OLD, ITEM4_NEW),
    ('Status: both items 3 and 4 resolved', TAIL_OLD, TAIL_NEW),
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
