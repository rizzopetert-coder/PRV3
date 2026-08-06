"""
PRV3 Calibration Harness Fix -- generate_answers() severity follow-on
deduplication, discovered via the Track A regression check.

Real bug, confirmed empirically: AUT-UP-01/02/03 (the_unsolved_problem) are
wired to BOTH Q28 and Q31, and since the Bucket 1 Q31 tie-break fix
(commit 44e85fc), both now select a severity_trigger=True option routing
to the SAME follow-on, SEVER-11. generate_answers() spliced SEVER-11 in
TWICE (once per firing core question), and run_profile()'s accumulation
loop summed both -- raw=2.00+2.00=4.00, producing Endemic when the locked
expected value is Entrenched (raw=2.00 is correct, single-count).

The real live app already guards against exactly this
(severityFollowOnAlreadyAsked() in web/lib/session-store.ts, the
"dual-parent" case its own header comment references) -- the calibration
harness was simply missing the equivalent. This fix mirrors that guard: a
local set tracks which follow-on IDs have already been spliced in for this
profile's answer generation; a later core question that also fires an
already-spliced follow-on is a no-op, matching real production behavior.

Confirmed this is the only latent case in the current 172-profile suite via
the full before/after regression (see Track A session report) -- other
Track A additions do not share a follow-on across multiple firing core
questions the way SEVER-11 (Q28 + Q31) does.

Usage:
  python tools/patch_generate_answers_dedup.py --dry-run
  python tools/patch_generate_answers_dedup.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = '''    answers = []
    for qid in sorted(_CORE_QUESTION_IDS):'''

NEW = '''    answers = []
    # Dedup guard, mirroring the real live app's severityFollowOnAlreadyAsked()
    # (web/lib/session-store.ts) -- a follow-on with multiple real parent
    # questions (SEVER-11 via Q28 and Q31, the "dual-parent" case that
    # module's own header comment already documents) must only ever be
    # spliced in once per session. Without this, a later core question
    # that also fires an already-spliced follow-on would double-count its
    # raw contribution -- confirmed as a real, latent bug via the Track A
    # regression check (AUT-UP-01/02/03 overshot to Endemic instead of
    # their locked Entrenched, SEVER-11 fired twice, raw summed to 4.00
    # instead of the correct single-count 2.00).
    already_spliced_followons = set()
    for qid in sorted(_CORE_QUESTION_IDS):'''

OLD2 = '''        if opt.severity_trigger and opt.severity_follow_on_id:
            target_value = _SEVERITY_FOLLOW_ON_TARGETS.get(test_case.test_id, {}).get(
                opt.severity_follow_on_id
            )
            if target_value is not None:
                follow_on_q = QUESTION_LIBRARY[opt.severity_follow_on_id]
                follow_on_opt = select_severity_follow_on_option(follow_on_q, target_value)
                answers.append(TestAnswer(
                    question_id=opt.severity_follow_on_id,
                    selected_option_ids=[follow_on_opt.option_id],
                ))
    return answers'''

NEW2 = '''        if (
            opt.severity_trigger
            and opt.severity_follow_on_id
            and opt.severity_follow_on_id not in already_spliced_followons
        ):
            target_value = _SEVERITY_FOLLOW_ON_TARGETS.get(test_case.test_id, {}).get(
                opt.severity_follow_on_id
            )
            if target_value is not None:
                follow_on_q = QUESTION_LIBRARY[opt.severity_follow_on_id]
                follow_on_opt = select_severity_follow_on_option(follow_on_q, target_value)
                answers.append(TestAnswer(
                    question_id=opt.severity_follow_on_id,
                    selected_option_ids=[follow_on_opt.option_id],
                ))
                already_spliced_followons.add(opt.severity_follow_on_id)
    return answers'''


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = TARGET.read_text(encoding="utf-8")
    for label, old, new in (("guard init", OLD, NEW), ("splice check", OLD2, NEW2)):
        count = content.count(old)
        if count != 1:
            print(f"ABORT: {label}: expected exactly 1 match, found {count}")
            sys.exit(1)
        content = content.replace(old, new, 1)

    if args.dry_run:
        print("=== Would apply 2 edits to generate_answers() in tools/calibration_runner.py ===")
        print("Dry run complete. Re-run with --write to apply.")
    else:
        TARGET.write_text(content, encoding="utf-8")
        print("=== Written: 2 edits applied ===")


if __name__ == "__main__":
    main()
