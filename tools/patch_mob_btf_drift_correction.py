"""
tools/_mob.txt: correct the built_to_fail false-rank-1 drift record
(Priority Queue item 1, carried since MOB v4.300) with this session's
findings, and split the residual into its own scoped follow-on item.

No engine code change accompanies this patch. The one concretely
identified fix candidate this session surfaced (the_arbitrary_standard's
primary_dimension label desync) was already shipped in commit 49f8796
(2026-09-10, the prior session) before this investigation began --
confirmed directly via `git show 49f8796 -- engine/data/states.py`, not
assumed from memory or from this session's own report phrasing. Flagged
to Pete before writing anything; Pete confirmed folding it into the
existing -7 recovery rather than tracking it as a separate still-open
item.

Bumps MOB version v4.300 -> v4.301 (workstream status changes
materially: an investigation closes, its record is corrected, and a new
scoped item enters the queue). Appends a new closeout-style entry after
the existing v4.300 entry's own trailing Priority Queue snapshot, which
is left untouched as a historical record -- matching this file's
existing pattern where each entry's own "On the horizon" section is a
dated snapshot and only the most recently appended one is live.

Usage:
    python tools/patch_mob_btf_drift_correction.py --dry-run
    python tools/patch_mob_btf_drift_correction.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

VERSION_OLD = r'\\\#\\\# MOB v4.300'
VERSION_NEW = r'\\\#\\\# MOB v4.301'

TAIL_ANCHOR_OLD = '''(`damages_cap_treatment` Phase 2 -- 2a, 2b, and 2c -- is now fully
shipped and dropped from this list entirely.)'''

NEW_ENTRY = '''

## SESSION CLOSEOUT (2026-09-11, continuation session) -- built_to_fail
## false-rank-1 drift investigated and corrected, no engine code change

### One-line summary
Root-caused the `built_to_fail` false-rank-1 drift carried at MOB v4.300
Priority Queue item 1. The "52/175 -> 80/175" figure in that record was
wrong -- confirmed the real number is 70/175, twice-confirmed and
reproducible; the incidental "80" observed during EXP-IPM-02 reflected a
stale intermediate state, not a fresh HEAD measurement. Full git-blame
decomposition of the confirmed 52 -> 70 drift completed via isolated git
worktrees at every contributing commit (`4c1a5de`, `322ea93`, `f88a7c2`,
`49f8796`, `e8f82a8`, HEAD) plus full 175-profile per-commit winner
diffs, not just aggregate counts. No code changed: the one concretely
identified fix candidate (`the_arbitrary_standard`'s primary_dimension
label desync) turned out to already be shipped, in `49f8796`
(2026-09-10, the prior session), before this investigation began --
confirmed directly via `git show`, not assumed. Flagged to Pete before
writing anything further; Pete confirmed folding it into the corrected
record below rather than tracking it as new work.

### Decomposition of the confirmed 52 -> 70 drift
- **+10, deliberate, understood:** Candidate C (`322ea93`) -- IPM's
  authority_liability reduction (0.25 -> 0.20) = +8, UEA's
  aptitude_liability reduction (0.35 -> 0.30) = +2. Not a bug.
- **+18, `f88a7c2`'s five-state re-authoring** -- NOT explained by the
  five states' own vector changes affecting their own profiles (the
  the_paper_tiger's and IPM's own-profile losses to `built_to_fail`
  were byte-for-byte identical, same exact test IDs, at baseline,
  `322ea93`, and `f88a7c2` alike -- unchanged by this commit). Only
  `the_arbitrary_standard`'s own +2 is directly attributable to this
  commit, via the primary_dimension/vector desync bug (its vector was
  re-authored to an authority-dominant shape but its label stayed
  "Alliance"). The remaining +16 is a confirmed real ripple across 13
  unrelated states never touched by this commit -- now its own scoped
  item, Priority Queue item 2 below.
- **-10, already shipped before this investigation began, not new work
  from this session:** `49f8796` (2026-09-10) corrected the stale
  primary_dimension label on three states at once (`the_paper_tiger`,
  `invisible_performance_management`, `the_arbitrary_standard`),
  recovering -7; `e8f82a8` (2026-09-10, the unrelated EXP-IPM-02 Q35
  fix) recovered IPM's remaining -3 as a side effect. Root cause of the
  the_paper_tiger/`the_arbitrary_standard` share of this -7, confirmed
  directly: `built_to_fail`'s current vector is a byte-identical legacy
  duplicate of `the_paper_tiger`'s pre-`f88a7c2` vector (a known
  template-inheritance artifact from commit `58a19a0`, pre-dating Phase
  8/9, salience-only differentiated). Because
  `best_option_for_state()` generates a state's own calibration answers
  from its primary_dimension LABEL rather than its actual vector, the
  stale "Aptitude" label kept generating answers that exactly matched
  `built_to_fail`'s vector regardless of what the_paper_tiger's real
  vector was re-authored to. This means the the_paper_tiger/IPM share
  of the loss was already baked into Phase 9's own original 52 baseline,
  not new damage introduced by any commit in this drift's own range --
  `49f8796`/`e8f82a8` fixed a pre-existing bug, they did not undo new
  damage.

Background, out of scope for this drift, not actioned: `the_second_close`
loses 3 of its own dedicated profiles to `built_to_fail` constantly,
unchanged, confirmed at every commit checked from Phase 9's own baseline
through today -- its vector is alliance-dominant, nowhere near
`built_to_fail`'s aptitude-dominant shape, so it is not the same
mechanism as the_paper_tiger's. Matches a prior MOB note describing a
"separate, distinct, flat" own-loss problem. No action taken.

### Verification discipline note
This session's own working notes, mid-investigation, initially proposed
writing a code fix for `the_arbitrary_standard`'s primary_dimension
label per Pete's task framing. Checked before writing anything, per this
project's standing discipline against writing what was assumed rather
than verified: `git show 49f8796 -- engine/data/states.py` showed the
label was already "Authority" and already matched the vector's dominant
field (authority_liability=0.35), fixed the day before. Surfaced to Pete
via AskUserQuestion rather than silently applying a no-op fix or
silently dropping the discrepancy.

### Files changed
`tools/_mob.txt` (this entry, Priority Queue correction, version bump).
No engine files touched -- `engine/data/states.py`'s
`the_arbitrary_standard` entry is unchanged by this session, already
correct as of `49f8796`. No redeploy or live round-trip required as a
result of this session's work.

Files changed: `tools/_mob.txt` (this entry, version bump). No engine or
test files touched this session. | This session (Claude Code),
2026-09-11 | Next: the 16-profile `f88a7c2` ripple (Priority Queue item
2 below) is the next `built_to_fail`-adjacent item if picked up again,
but it is explicitly scoped as its own dedicated investigation, not a
quick follow-up. |

### On the horizon -- updated Priority Queue
1. `built_to_fail` false-rank-1 baseline drift -- CLOSED, this session.
   Corrected figure: 70/175 (not 80/175 as previously recorded), full
   decomposition above. No code change resulted -- see above.
2. `built_to_fail`'s 16-profile ripple from `f88a7c2` -- confirmed real,
   mechanism NOT identified. 16 of 175 calibration profiles across 13
   states none of which `f88a7c2` directly touched
   (`what_nobody_says`, `culture_drift`, `the_wrong_reward`,
   `distributed_culture_fragmentation`, `compression_crisis`,
   `transition_paralysis`, `pay_exposure`, `the_pay_fog`,
   `the_uninitiated`, `the_unformed_leader`, `cultural_overtime`,
   `the_dormant_talent`, `the_unexamined_algorithm`) flipped toward
   `built_to_fail` at the exact commit that re-authored five completely
   different states' vectors. Working theory, unconfirmed: re-authoring
   those five states' vectors away from certain regions of the scoring
   space had a systemic effect on nearby states' own next-best-match
   resolution, rather than a direct edit to any of the 13 affected
   states themselves. Needs its own dedicated investigation session,
   not a quick follow-up.
3. AssemblyPanel/Phase-2-CTA merge (Option C) -- design pass to reduce
   stacked bottom UI on mobile, not urgent, current fix fully
   functional.
4. `invisible_performance_management`'s thin question-wiring -- low
   priority, revisit if the moderate-tier calibration bar ever
   tightens.
5. `invisible_performance_management`/`the_founders_grip` vector
   duplicate -- latent taxonomy question, no urgency.
6. `_oh_is_small_employer()` -- built and tested, not wired into any
   pricing branch. Revisit whenever a real compensatory-damages/
   net-worth pricing path for OH is scoped.
7. NAICS-vs-"Manufacturing & Industrial" mapping gap (OH) -- documented
   approximation in `_oh_is_small_employer()`'s docstring and OH's
   citation comment. No NAICS-level intake data exists to resolve it
   precisely; revisit only if OH's small-employer routing is ever wired
   into a real pricing path.
8. Quarterly Step-Back -- last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.'''

EDITS = [
    ('version header 4.300 -> 4.301', VERSION_OLD, VERSION_NEW),
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

    tail_count = content.count(TAIL_ANCHOR_OLD)
    if tail_count != 1:
        errors.append(f'tail anchor found {tail_count} times, expected exactly 1.')
    if not content.rstrip().endswith(TAIL_ANCHOR_OLD.split(chr(10))[-1]):
        errors.append('tail anchor is not at the true end of the file -- refusing to append blind.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    new_content = new_content.rstrip('\n') + '\n' + NEW_ENTRY + '\n'

    if args.dry_run:
        print(f'DRY RUN -- all anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
