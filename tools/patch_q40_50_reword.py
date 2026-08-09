"""
PRV3 -- Implement six question-text rewrites from prompts/diagnostic-
usability-findings-2026-08-09.md's B-addendum-2 (Pete-approved, this
session). Stem-only changes plus one option-text change (Q41-D).

Confirmed zero recalibration needed before this patch was written:
question_text is display-copy only (engine/main.py's get_question_copy()
is the only place it's read), accumulate_one_answer() reads
question_id -> option_id -> dimensional_contributions exclusively via
QUESTION_LIBRARY lookup, never question_text or option_text content.
dimensional_contributions values are UNCHANGED on every option across
all six questions -- confirmed by this patch only touching the
_QDATA question_text/option_text string literals, never the
_opt_contrib table.

Usage:
  python tools/patch_q40_50_reword.py --dry-run
  python tools/patch_q40_50_reword.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


Q = "engine/data/questions.py"

# ---------------------------------------------------------------------
# Q40 -- question_text only.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q40",\n'
    '        "How many people have held this exact role before you,"\n'
    '        " and what\'s the organization\'s read on why they left?",\n'
    '        "forced_choice", 40, "late",',
    '        "Q40",\n'
    '        "Has anyone held your role prior to you — and if so, what\'s the"\n'
    '        " organization\'s read on why they left?",\n'
    '        "forced_choice", 40, "late",',
)

# ---------------------------------------------------------------------
# Q41 -- question_text AND option D text.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q41",\n'
    '        "When you\'ve raised the gap between the scope and the resources"\n'
    '        " you actually have, what\'s happened?",\n'
    '        "forced_choice", 41, "late",\n'
    "        [\n"
    '            ("A", "It got acknowledged and something changed.", False, None),\n'
    '            ("B", "It got acknowledged, but nothing\'s changed yet.", False, None),\n'
    '            ("C", "I was told to figure it out — the responsibility landed on me, not the structure.", False, None),\n'
    '            ("D", "I\'ve been told that directly, and I know the person before me was told the same thing — it\'s clearly the standard answer to this role, not advice specific to me.", True, None),\n'
    "        ],",
    '        "Q41",\n'
    '        "When you\'ve raised the gap between what this role is responsible"\n'
    '        " for and the resources you actually have to do it, what\'s happened?",\n'
    '        "forced_choice", 41, "late",\n'
    "        [\n"
    '            ("A", "It got acknowledged and something changed.", False, None),\n'
    '            ("B", "It got acknowledged, but nothing\'s changed yet.", False, None),\n'
    '            ("C", "I was told to figure it out — the responsibility landed on me, not the structure.", False, None),\n'
    '            ("D", "I\'ve been told that directly — and it\'s clearly the standard response to this role, not advice specific to my situation.", True, None),\n'
    "        ],",
)

# ---------------------------------------------------------------------
# Q42 -- question_text only.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q42",\n'
    '        "When a decision needs that one person\'s approval and they\'re"\n'
    '        " unavailable, what happens?",\n'
    '        "forced_choice", 42, "late",',
    '        "Q42",\n'
    '        "When a decision needs approval from one specific person — and that"\n'
    '        " person is unavailable — what happens?",\n'
    '        "forced_choice", 42, "late",',
)

# ---------------------------------------------------------------------
# Q44 -- question_text only.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q44",\n'
    '        "Who actually knows about this, and what\'s happened as a result?",\n'
    '        "forced_choice", 44, "late",',
    '        "Q44",\n'
    '        "Think of something in your organization that\'s been allowed to"\n'
    '        " continue even though it\'s a known problem. Who actually knows about"\n'
    '        " it, and what\'s happened as a result?",\n'
    '        "forced_choice", 44, "late",',
)

# ---------------------------------------------------------------------
# Q47 -- question_text only.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q47",\n'
    '        "Has anything changed for this manager — additional support,"\n'
    '        " delegated authority, or reduced scope — since it became clear"\n'
    '        " they were stretched?",\n'
    '        "forced_choice", 47, "late",',
    '        "Q47",\n'
    '        "Think of a manager you\'d describe as stretched thin or overloaded."\n'
    '        " Has anything changed for them — additional support, delegated"\n'
    '        " authority, or reduced scope — since that became clear?",\n'
    '        "forced_choice", 47, "late",',
)

# ---------------------------------------------------------------------
# Q50 -- question_text only.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q50",\n'
    '        "When someone in this group makes a costly mistake,"\n'
    '        " what happens to them?",\n'
    '        "forced_choice", 50, "late",',
    '        "Q50",\n'
    '        "Every organization has a group of people who are especially trusted"\n'
    '        " or protected — an inner circle. When someone in that group makes a"\n'
    '        " costly mistake, what happens to them?",\n'
    '        "forced_choice", 50, "late",',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
