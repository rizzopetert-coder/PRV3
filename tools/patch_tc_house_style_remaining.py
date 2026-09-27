"""
TC-* house style: the remaining 20 spaced-dash instances across 13 TC-*
questions (Pete, 2026-09-27, drafted and approved item by item, same
treatment as TC-HRPOL-01 at 176e201).

Rules applied, as approved:
  - Question asides -> commas (e7d71f7 precedent).
  - List asides (TC-BEN-01, TC-TECH-03, TC-PERF-03) -> the locked
    "(such as X, Y, and Z)" form. All three lists are illustrative.
  - TC-HIRE-01's aside defines "structured" rather than listing examples,
    so it becomes "with consistent questions and consistent scoring".
  - Options: "Yes," takes a comma. A rating or label followed by a reason
    takes a colon, including "Not confident:" and "Not sure:" (Pete's call).

Text only. TC-* questions are zero-signal, so no option's contributions,
IDs, or order change. The vitest mock fixture that echoes TC-HIRE-01
(web/lib/diagnostic-completion.test.ts) is updated to mirror the source.

Usage:
    python tools/patch_tc_house_style_remaining.py --dry-run
    python tools/patch_tc_house_style_remaining.py --write
"""
import argparse
import pathlib
import sys

REWRITES = [
    # Questions
    ("If a relevant state law changed tomorrow, how would you find out -- and how long would it take your policies to catch up?",
     "If a relevant state law changed tomorrow, how would you find out, and how long would it take your policies to catch up?"),
    ("How much of your interview process is actually structured -- consistent questions, consistent scoring -- versus left to whoever's in the room that day?",
     "How much of your interview process is actually structured, with consistent questions and consistent scoring, versus left to whoever's in the room that day?"),
    ("How confident are you that every employee's overtime eligibility was set correctly the day they were hired -- and hasn't drifted since their role changed?",
     "How confident are you that every employee's overtime eligibility was set correctly the day they were hired, and hasn't drifted since their role changed?"),
    ("If an employee disputed their hours worked, could payroll produce a time record that would hold up -- or would it come down to someone's memory?",
     "If an employee disputed their hours worked, could payroll produce a time record that would hold up, or would it come down to someone's memory?"),
    ("Are required notices -- COBRA, plan summaries, annual disclosures -- actually being sent and tracked, or is the assumption that the broker handles it?",
     "Are required notices (such as COBRA, plan summaries, and annual disclosures) actually being sent and tracked, or is the assumption that the broker handles it?"),
    ("If a former employee never received their COBRA notice, would you know -- and could you prove when and how it was sent?",
     "If a former employee never received their COBRA notice, would you know, and could you prove when and how it was sent?"),
    ("If an employee requested their own personnel file, could you produce it -- completely, and within a reasonable timeframe?",
     "If an employee requested their own personnel file, could you produce it, completely and within a reasonable timeframe?"),
    ("Is sensitive employee data -- SSNs, banking info, medical information -- actually access-controlled within your systems, or does broad internal access exist by default?",
     "Is sensitive employee data (such as SSNs, banking info, and medical information) actually access-controlled within your systems, or does broad internal access exist by default?"),
    ("Are performance ratings actually consistent with the outcomes attached to them -- promotions, raises, terminations -- or do the numbers and the decisions sometimes not match?",
     "Are performance ratings actually consistent with the outcomes attached to them (such as promotions, raises, and terminations), or do the numbers and the decisions sometimes not match?"),
    # Options
    ("None that I'm aware of -- policy and practice line up.",
     "None that I'm aware of: policy and practice line up."),
    ("There's a defined process -- legal counsel or a compliance service flags it and policies update on a known timeline.",
     "There's a defined process: legal counsel or a compliance service flags it and policies update on a known timeline."),
    ("Fully structured -- consistent questions and scoring across every candidate.",
     "Fully structured: consistent questions and scoring across every candidate."),
    ("No structure -- entirely up to the interviewer.",
     "No structure: entirely up to the interviewer."),
    ("Very confident -- classifications are reviewed when roles change.",
     "Very confident: classifications are reviewed when roles change."),
    ("Not confident -- this hasn't been reviewed in a long time.",
     "Not confident: this hasn't been reviewed in a long time."),
    ("Yes -- a system-generated, timestamped record exists.",
     "Yes, a system-generated, timestamped record exists."),
    ("Nothing written -- it would need to be reconstructed.",
     "Nothing written: it would need to be reconstructed."),
    ("Yes -- there's follow-up after enrollment to confirm understanding.",
     "Yes, there's follow-up after enrollment to confirm understanding."),
    ("No defined schedule -- retained indefinitely by default.",
     "No defined schedule: retained indefinitely by default."),
    ("Not sure -- this hasn't been checked.",
     "Not sure: this hasn't been checked."),
]

SOURCE = pathlib.Path('engine/data/questions.py')
FIXTURE = pathlib.Path('web/lib/diagnostic-completion.test.ts')


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    if len(REWRITES) != 20:
        print(f'ERROR: expected 20 rewrites, have {len(REWRITES)}.', file=sys.stderr)
        sys.exit(1)
    src = SOURCE.read_text(encoding='utf-8')
    fix = FIXTURE.read_text(encoding='utf-8')
    fixture_hits = 0
    for i, (old, new) in enumerate(REWRITES, 1):
        n = src.count(old)
        if n != 1:
            print(f'ERROR: #{i} found {n} times in {SOURCE}: {old!r}', file=sys.stderr)
            sys.exit(1)
        if any(c in new for c in (' -- ', '—', ';')):
            print(f'ERROR: #{i} replacement still contains a dash or semicolon.', file=sys.stderr)
            sys.exit(1)
        src = src.replace(old, new, 1)
        fc = fix.count(old)
        if fc:
            fix = fix.replace(old, new)
            fixture_hits += fc
        print(f'#{i:2d} OK{"  (+fixture)" if fc else ""}')
    print(f'fixture replacements: {fixture_hits}')
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    SOURCE.write_text(src, encoding='utf-8')
    FIXTURE.write_text(fix, encoding='utf-8')
    print(f'WROTE: {SOURCE}, {FIXTURE}')


if __name__ == '__main__':
    main()
