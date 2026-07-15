"""
Session 70 -- weak-branch damped primary-dimension routing.

Targeted change to tools/calibration_runner.py ONLY:
  1. Adds WEAK_DAMPED_THRESHOLD constant and _damped_weak_option() helper,
     placed immediately after the existing _neutral_option() definition.
  2. Changes generate_answers()'s weak branch (the `else:` clause) from an
     unconditional _neutral_option(q) call to _damped_weak_option(q, target_state).
     high_confidence / extreme_high_confidence / moderate branches untouched.

Rule implemented (Pete-confirmed): among AnswerOptions with a positive
contribution <= 0.25 on the target state's primary_dimension liability field,
pick the one with the LARGEST such contribution. Falls back to the real,
unmodified _neutral_option(q) when no qualifying option exists for that
question. This is exactly the rule the Session 70 dry-run script tested
(max-contribution, not secondary-noise-minimizing).

Usage:
    python tools/patch_weak_damped_routing_s70.py --dry-run
    python tools/patch_weak_damped_routing_s70.py --write
"""

import argparse
import difflib
from pathlib import Path

TARGET = Path(__file__).parent / "calibration_runner.py"

OLD_NEUTRAL_BLOCK = '''def _neutral_option(question):
    """Return option with minimum absolute sum of all dimensional contributions."""
    def _abs_sum(opt):
        return sum(
            abs(v) for v in opt.dimensional_contributions.values()
            if isinstance(v, (int, float))
        )
    return min(question.answer_options, key=_abs_sum)
'''

NEW_NEUTRAL_BLOCK = '''def _neutral_option(question):
    """Return option with minimum absolute sum of all dimensional contributions."""
    def _abs_sum(opt):
        return sum(
            abs(v) for v in opt.dimensional_contributions.values()
            if isinstance(v, (int, float))
        )
    return min(question.answer_options, key=_abs_sum)


# CALIBRATION TARGET -- Session 70. Weak-branch damped primary-dimension routing.
WEAK_DAMPED_THRESHOLD: float = 0.25


def _damped_weak_option(question, target_state_id: str):
    """
    Weak-branch damped primary-dimension routing -- Session 70.

    Prefer the option with the largest positive contribution (<= WEAK_DAMPED_THRESHOLD)
    on target_state's primary_dimension liability field. Falls back to the real,
    unmodified _neutral_option(question) when no qualifying option exists for this
    question.

    Confirmed via Session 70 dry-run against 4 states (decision_paralysis,
    the_arbitrary_standard, the_untouchable, sequential_decision_blindness):
    2 fail-to-pass flips, 0 pass-to-fail regressions at threshold 0.25.

    Known limitation, accepted as-is: operates at dimension granularity, not state
    granularity. Any two states sharing a primary_dimension receive byte-for-byte
    identical weak-branch answer vectors under this rule -- downstream cosine
    similarity against each state's own distinct profile vector still differentiates
    them.
    """
    profile = STATE_PROFILES.get(target_state_id)
    field = _DIM_TO_LIABILITY_FIELD.get(profile.primary_dimension, "") if profile else ""
    candidates = [
        opt for opt in question.answer_options
        if 0.0 < opt.dimensional_contributions.get(field, 0.0) <= WEAK_DAMPED_THRESHOLD
    ]
    if not candidates:
        return _neutral_option(question)
    return max(candidates, key=lambda opt: opt.dimensional_contributions.get(field, 0.0))
'''

OLD_WEAK_BRANCH = '''        else:
            opt = _neutral_option(q)
        answers.append(TestAnswer(question_id=qid, selected_option_ids=[opt.option_id]))'''

NEW_WEAK_BRANCH = '''        else:
            opt = _damped_weak_option(q, test_case.target_state)
        answers.append(TestAnswer(question_id=qid, selected_option_ids=[opt.option_id]))'''

OLD_DOCSTRING_LINE = "    weak: neutral option throughout.\n"
NEW_DOCSTRING_LINE = (
    "    weak: damped primary-dimension routing (Session 70) -- prefers a lightly-loading\n"
    "          positive option on target's primary_dimension liability field (<= 0.25),\n"
    "          neutral fallback otherwise.\n"
)


def build_new_content(original: str) -> str:
    if OLD_NEUTRAL_BLOCK not in original:
        raise SystemExit("OLD_NEUTRAL_BLOCK not found -- file has changed, aborting.")
    if OLD_WEAK_BRANCH not in original:
        raise SystemExit("OLD_WEAK_BRANCH not found -- file has changed, aborting.")
    if OLD_DOCSTRING_LINE not in original:
        raise SystemExit("OLD_DOCSTRING_LINE not found -- file has changed, aborting.")

    updated = original.replace(OLD_NEUTRAL_BLOCK, NEW_NEUTRAL_BLOCK, 1)
    updated = updated.replace(OLD_WEAK_BRANCH, NEW_WEAK_BRANCH, 1)
    updated = updated.replace(OLD_DOCSTRING_LINE, NEW_DOCSTRING_LINE, 1)
    return updated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    original = TARGET.read_text(encoding="utf-8")
    updated = build_new_content(original)

    if args.write:
        TARGET.write_text(updated, encoding="utf-8")
        print(f"WRITTEN: {TARGET}")
        return

    # default / --dry-run: show diff, do not write
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        updated.splitlines(keepends=True),
        fromfile=str(TARGET),
        tofile=str(TARGET) + " (proposed)",
    )
    print("".join(diff))


if __name__ == "__main__":
    main()
