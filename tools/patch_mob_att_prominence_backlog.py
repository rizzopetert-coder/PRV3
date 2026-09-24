"""
tools/_mob.txt -- append one backlog item to Section 13b's "Open, not
sequenced" list: the 4 pre-existing ATT-* moderate-tier prominence
calibration failures, confirmed pre-existing at HEAD and unrelated to this
session's HRdiagnostic.com Tactical & Compliance work.

Per Pete's explicit instruction: "not a fix, just a logged item." A single
additive bullet, not a wholesale 13b rewrite (that convention -- "expected
to be rewritten wholesale each time it's updated" -- applies to closeout-
time passes; this is a mid-session single-item log). The list's own
"Last updated" line (which specifically describes the last full rewrite
pass) is left untouched -- this append doesn't change what that line
claims. Version not bumped: no locked decision, no rule change, no
material workstream-status change -- a known-issue log entry only, per
CLAUDE.md's own version-bump criteria.

Usage:
    python tools/patch_mob_att_prominence_backlog.py --dry-run
    python tools/patch_mob_att_prominence_backlog.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

ANCHOR_OLD = '''- `tools/patch_*.py` accumulation -- 463 files as of 2026-09-23, replacing the stale "68-file held-recent" framing (that figure couldn't be reconciled against current state -- see Section 16's 2026-09-23 dated note). Needs its own dedicated pass.

Infrastructure carry-forwards, tracked only in Section 16 closeouts until now:'''

ANCHOR_NEW = '''- `tools/patch_*.py` accumulation -- 463 files as of 2026-09-23, replacing the stale "68-file held-recent" framing (that figure couldn't be reconciled against current state -- see Section 16's 2026-09-23 dated note). Needs its own dedicated pass.
- ATT-* moderate-tier prominence calibration failures (`ATT-UT-02`/`the_untouchable`, `ATT-IB-02`/`invisible_burnout`, `ATT-LD-02`/`leadership_deafness`, `ATT-IE-02`/`identity_erosion`) -- `tools/calibration_runner.py`'s 175-profile suite runs 171/175, all 4 failures "prominence criterion failed." Confirmed pre-existing at HEAD, 2026-09-24: `calibration_runner.py --verbose` output is byte-identical with and without that session's `engine/data/questions.py` TC-* additions (HRdiagnostic.com Tactical & Compliance module, all zero-signal), ruling out that work as the cause. Logged as a known issue, not investigated further this session -- no fix attempted.

Infrastructure carry-forwards, tracked only in Section 16 closeouts until now:'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')
    count = content.count(ANCHOR_OLD)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(ANCHOR_OLD, ANCHOR_NEW, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found, edit would apply cleanly. Nothing written.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
