"""
Patch tools/_mob.txt for session closeout (2026-09-07):
1. Close the Redis token-rotation follow-up (Section 13a Redis row's
   trailing open question) -- Pete confirmed rotation complete.
2. Rewrite Section 13b's Priority Queue numbered list wholesale, per
   Pete's explicit 4-item resequencing, carrying forward still-open
   items not in that list and noting what this session's own work
   superseded/closed entirely.
Bumps MOB version v4.285 -> v4.286.

Usage:
    python tools/patch_mob_session_closeout_20260907.py --dry-run
    python tools/patch_mob_session_closeout_20260907.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

REDIS_OLD = (
    "Closed -- no further check-in on the masking asymmetry itself. "
    "Separate, still-open question for Pete: whether to rotate the Upstash "
    "Redis token given it was pasted into this session's chat transcript. |"
)

REDIS_NEW = (
    "Closed -- no further check-in. The separate rotation question is also "
    "now resolved: Pete confirmed (2026-09-07) the Upstash Redis token was "
    "regenerated and updated in Vercel for both Preview and Production, "
    "with app reconnection confirmed on his end -- the transcript-exposure "
    "concern is fully closed, not just the masking fix. |"
)

PRIORITY_OLD_START = "Priority order for next session, in sequence."
PRIORITY_OLD_END_MARKER = "No item in this rewrite carries an actual calendar deadline"

PRIORITY_NEW = """Priority order for next session, in sequence. **Rewritten wholesale 2026-09-07** (session closeout, Pete's explicit resequencing after this session's ssoProtection/Redis/domain/homepage-dark-theme closures):

1. Legal/Compliance friction-tax module wiring -- a real product decision, not an engineering one: `compute_legal_compliance_exposure()` is fully built (all 5 clusters, the coverage-threshold gate) but wired into zero client-facing output (confirmed, Section 13a, 2026-09-05 row). Highest priority: core product functionality, and the longest-standing open decision item.
2. ~30 of 44 PARTIAL coverage-threshold states still need primary-statute verification (7 CONFIRMED, 44 PARTIAL total, Section 13a). Large scope, genuinely non-blocking -- PARTIAL data never drives a dollar-affecting determination today.
3. `extreme_high_confidence` calibration tier at 0/1 -- confirmed via a fresh 2026-09-05 calibration run, the one profile in this tier fails outright while every other tier passes at or above its historical rate. Worth a dedicated investigation into what's specifically misclassifying. Lower urgency than items 1-2.
4. v2 token migration for the homepage -- a real, separate architectural question surfaced this session (Section 13a, 2026-09-07 row): whether the homepage should retire its Session-58-era `text-charcoal`/`--color-charcoal` usage in favor of the v2 `--ink` system outright, rather than the isolated `--home-ink` token shipped this session. Architectural/cosmetic only, no functional urgency -- last in sequence.

Still open, not resequenced this pass, carried forward from the prior rewrite -- the 4-item priority order above is Pete's sequencing call on what to pick up next, not a claim that these no longer exist:
- Service Expectations page -- full draft copy, attorney-unreviewed, awaiting Pete's own read.
- SEVER-09 dead trigger (Q27A's only parent, unreachable in live Phase 1) -- parked, harmless.
- `tools/diagnostic_fast_forward.py` -- confirmed structurally unusable against current infrastructure, rework-or-retire decision needed whenever picked up.
- OSHA actual-average-penalty backfill -- 17 of 22 states still need it, explicitly not urgent.
- ADA/FMLA/OSHA headcount-threshold gating for Legal/Compliance Clusters 1, 2, 5 -- does not exist yet, would be new logic.

Superseded by this session's own closures, dropped from the active list entirely -- Section 13a and Section 16 carry the full record, not reproduced here: the ssoProtection discrepancy (RESOLVED -- Hobby-plan Standard Protection scope, not a bug), the Preview Redis credential-masking asymmetry (CLOSED -- both vars Sensitive-masked, token also rotated per Pete's separate confirmation), the `principalresolution.com` domain reassignment from `prv-2` to `prv-3` (CLOSED, live-verified), and the homepage dark/neutral theme-reactivity bug (CLOSED -- both `--home-slate` and `--home-ink` shipped and live-verified on production).

"""

LAST_UPDATED_OLD = (
    "Last updated: This session (Claude Code), 2026-09-04 -- STATE_CAUSATION_OVERRIDES "
    "workstream closed (all 19 states reviewed and decided) and dropped from the active "
    "list entirely, having sat as item 8 across several intervening sessions. Item 9 "
    "renumbered down to item 8. No other item content changed. (Prior update: 2026-08-29 "
    "-- homepage restructure closed and dropped from the active list, items renumbered 1-9.)"
)

LAST_UPDATED_NEW = (
    "Last updated: This session (Claude Code), 2026-09-07 -- full resequencing per Pete's "
    "explicit 4-item priority order (Legal/Compliance wiring, PARTIAL coverage-threshold "
    "verification, extreme_high_confidence investigation, v2 token migration), issued at "
    "session closeout after this session's ssoProtection/Redis/domain/homepage-dark-theme "
    "closures. Previously-tracked still-open items not in that list carried forward "
    "separately, not dropped. (Prior update: 2026-09-04 -- STATE_CAUSATION_OVERRIDES closed.)"
)

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.285"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.286"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')

    if content.count(REDIS_OLD) != 1:
        print(f'ERROR: Redis anchor found {content.count(REDIS_OLD)} times, expected 1.', file=sys.stderr)
        sys.exit(1)
    if content.count(LAST_UPDATED_OLD) != 1:
        print(f'ERROR: Last-updated anchor found {content.count(LAST_UPDATED_OLD)} times, expected 1.', file=sys.stderr)
        sys.exit(1)
    if content.count(OLD_VERSION_HEADER) != 1:
        print(f'ERROR: version header found {content.count(OLD_VERSION_HEADER)} times, expected 1.', file=sys.stderr)
        sys.exit(1)

    start = content.find(PRIORITY_OLD_START)
    end = content.find(PRIORITY_OLD_END_MARKER)
    if start == -1 or end == -1 or end <= start:
        print('ERROR: priority list start/end markers not found correctly.', file=sys.stderr)
        sys.exit(1)

    new_content = content[:start] + PRIORITY_NEW + content[end:]
    new_content = new_content.replace(REDIS_OLD, REDIS_NEW, 1)
    new_content = new_content.replace(LAST_UPDATED_OLD, LAST_UPDATED_NEW, 1)
    new_content = new_content.replace(OLD_VERSION_HEADER, NEW_VERSION_HEADER, 1)

    if args.dry_run:
        print('DRY RUN -- all anchors found exactly once, replacements would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
        print('--- new priority list ---')
        print(PRIORITY_NEW)
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
