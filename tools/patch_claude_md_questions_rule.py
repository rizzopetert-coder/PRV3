"""
CLAUDE.md Engine Rules: replace the stale "questions.py registry is
intentionally empty" line (Pete, 2026-09-27).

History, from git: the line came in with c79179b (2026-05-03, MOB v1.4), when
engine/data/questions.py was only the schema and its own docstring read "The
registry is empty at this stage -- question content is a separate
deliverable." That was a build-sequencing note, not a standing constraint.
The registry was populated from Session 9 on (MOB Section 16: Session 10,
50 entries), so the rule has been stale since May 2026, not since the
2026-09-24 TC-* addition.

The replacement keeps the one piece of context worth keeping (it was empty
only at the scaffold stage, and why) and states current fact: what the
registry holds, and that option dimensional_contributions are calibration
values under the existing data-first rule. No new rule is introduced.

Usage:
    python tools/patch_claude_md_questions_rule.py --dry-run
    python tools/patch_claude_md_questions_rule.py --write
"""
import argparse
import pathlib
import sys

CLAUDE = pathlib.Path('CLAUDE.md')
OLD = ('- `engine/data/questions.py` registry is intentionally empty — question population is a '
       'separate deliverable\r\n')
NEW = ('- `engine/data/questions.py` holds the live question registry (`QUESTION_LIBRARY`, 141 entries as of '
       '2026-09-27: the core Q-series and its follow-up chains, the SEVER-* severity follow-ons, and 40 '
       'hr-dx-only TC-* questions). It was empty only at the engine-scaffold stage (`c79179b`, MOB v1.4, '
       '2026-05-03), when question content was still a separate deliverable, and has been populated since '
       'Session 9. Option `dimensional_contributions` are calibration values, so the data-first calibration '
       'rule below applies to them. The TC-* questions are zero-signal by design (no dimensional '
       'contributions, `state_targets=[]`), verified inert against the 175-profile calibration suite at '
       '`d384262`.\r\n')


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    text = CLAUDE.read_bytes().decode('utf-8')
    if text.count(OLD) != 1:
        print(f'ERROR: stale rule line found {text.count(OLD)} times.', file=sys.stderr)
        sys.exit(1)
    new_text = text.replace(OLD, NEW, 1)
    print('[CLAUDE.md :: questions.py rule] OK')
    print('BEFORE:', OLD.rstrip())
    print('AFTER: ', NEW.rstrip())
    print('semicolons/em-dashes in new line:', NEW.count(';'), NEW.count('—'))
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    CLAUDE.write_text(new_text, encoding='utf-8', newline='')
    print(f'WROTE: {CLAUDE}')


if __name__ == '__main__':
    main()
