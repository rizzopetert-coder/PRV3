"""
PRV3 -- Track 1 of Pete's question-text edit list this session: 17
text-only edits across engine/data/questions.py, zero mechanism
changes, zero dimensional_contributions changes -- same safe category
as the six rewrites in commit 52e99ac (question_text is display-copy
only, accumulate_one_answer() reads option_id -> dimensional_contributions
exclusively via QUESTION_LIBRARY, never question_text content).

Every old-text value below was verified directly against the live repo
before this script was written, not assumed -- including the four
(Q40, Q42, Q47, Q50) already rewritten in commit 52e99ac, confirmed
still holding their post-rewrite text.

Item 10 (Q32) is not explicitly in Pete's original numbered list but is
covered by the newly locked house-style rule (appositive lists ->
"(such as X, Y, and Z)"), applied here for consistency with items 6,
8, 9, 11, which use the identical construction.

Usage:
  python tools/patch_track1_text_edits.py --dry-run
  python tools/patch_track1_text_edits.py --write
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
CLAUDE = "CLAUDE.md"

# 1. Q05
edit(
    Q,
    '        "Q05",\n'
    '        "When someone in your organization isn\'t performing — really isn\'t performing"\n'
    '        " — what happens?",\n'
    '        "forced_choice", 5, "early",',
    '        "Q05",\n'
    '        "When someone in your organization stands out because of their"\n'
    '        " underperformance, what happens?",\n'
    '        "forced_choice", 5, "early",',
)

# 2. Q07
edit(
    Q,
    '        "Q07",\n'
    '        "When you lose people you didn\'t want to lose, what\'s the pattern?",\n'
    '        "forced_choice", 7, "early",',
    '        "Q07",\n'
    '        "When it comes to losing people you don\'t want to lose, is there a pattern?",\n'
    '        "forced_choice", 7, "early",',
)

# 3. Q11
edit(
    Q,
    '        "Q11",\n'
    '        "How well do your organization\'s actions reflect what it says it values"\n'
    '        " — in who gets ahead, what gets tolerated, and how decisions get made?",\n'
    '        "forced_choice", 11, "early",',
    '        "Q11",\n'
    '        "How well do your organization\'s actions reflect what it says it values"\n'
    '        " — who gets ahead, what gets tolerated, and how decisions get made?",\n'
    '        "forced_choice", 11, "early",',
)

# 4. Q13
edit(
    Q,
    '        "Q13",\n'
    '        "How well does your organization understand where it\'s going"\n'
    '        " — and believe it will get there?",\n'
    '        "forced_choice", 13, "mid",',
    '        "Q13",\n'
    '        "How well does your organization understand where it\'s going, and how"\n'
    '        " much belief exists that it will get there?",\n'
    '        "forced_choice", 13, "mid",',
)

# 5. Q14
edit(
    Q,
    '        "Q14",\n'
    '        "How would you describe your organization\'s relationship with compensation right now?",\n'
    '        "forced_choice", 14, "mid",',
    '        "Q14",\n'
    '        "How would you describe your organization\'s approach to compensation right now?",\n'
    '        "forced_choice", 14, "mid",',
)

# 6. Q17
edit(
    Q,
    '        "Q17",\n'
    '        "When your organization tries to change something — a new initiative, a cultural shift,"\n'
    '        " a structural change — what typically happens?",\n'
    '        "forced_choice", 17, "mid",',
    '        "Q17",\n'
    '        "When your organization tries to change something (such as a new"\n'
    '        " initiative, a cultural shift, or a structural change), what typically"\n'
    '        " happens?",\n'
    '        "forced_choice", 17, "mid",',
)

# 7. Q19
edit(
    Q,
    '        "Q19",\n'
    '        "How consistent is what your organization says publicly — about its culture, values,"\n'
    '        " and commitments — with what\'s actually happening internally?",\n'
    '        "forced_choice", 19, "mid",',
    '        "Q19",\n'
    '        "How consistent is what your organization says publicly with what\'s"\n'
    '        " actually happening internally?",\n'
    '        "forced_choice", 19, "mid",',
)

# 8. Q22
edit(
    Q,
    '        "Q22",\n'
    '        "How current and complete are your organization\'s people policies"\n'
    '        " — employee handbook, HR documentation, compliance obligations?",\n'
    '        "forced_choice", 22, "late",',
    '        "Q22",\n'
    '        "How current and complete are your organization\'s people policies"\n'
    '        " (such as employee handbook, HR documentation, compliance obligations)?",\n'
    '        "forced_choice", 22, "late",',
)

# 9. Q30
edit(
    Q,
    '        "Q30",\n'
    '        "How well do people in your organization know what\'s happening — decisions that have"\n'
    '        " been made, where things are headed, what leadership is thinking?",\n'
    '        "forced_choice", 30, "late",',
    '        "Q30",\n'
    '        "How well do people in your organization know what\'s happening (such as"\n'
    '        " decisions that have been made, where things are headed, what leadership"\n'
    '        " is thinking)?",\n'
    '        "forced_choice", 30, "late",',
)

# 10. Q32 -- not in Pete's original numbered list, covered by the new house-style
#     rule (same appositive-list construction as items 6, 8, 9, 11).
edit(
    Q,
    '        "Q32",\n'
    '        "As an organization, how well do you learn from experience"\n'
    '        " — your own mistakes, prior initiatives, external feedback?",\n'
    '        "forced_choice", 32, "late",',
    '        "Q32",\n'
    '        "As an organization, how well do you learn from experience (such as your"\n'
    '        " own mistakes, prior initiatives, external feedback)?",\n'
    '        "forced_choice", 32, "late",',
)

# 11. Q33
edit(
    Q,
    '        "Q33",\n'
    '        "How current and well-maintained is your operational infrastructure"\n'
    '        " — continuity plans, technology governance, organizational network documentation?",\n'
    '        "forced_choice", 33, "late",',
    '        "Q33",\n'
    '        "How current and well-maintained is your operational infrastructure"\n'
    '        " (such as continuity plans, technology governance, organizational"\n'
    '        " network documentation)?",\n'
    '        "forced_choice", 33, "late",',
)

# 12. Q34
edit(
    Q,
    '        "Q34",\n'
    '        "Looking at everything you\'ve shared — if you had to name what kind of problem this is,"\n'
    '        " what would you say?",\n'
    '        "forced_choice", 34, "late",',
    '        "Q34",\n'
    '        "Looking at everything you\'ve shared — if you had to name your"\n'
    '        " organization\'s most pressing people-problem, what would you say?",\n'
    '        "forced_choice", 34, "late",',
)

# 13. Q40 (already rewritten in commit 52e99ac -- editing its post-rewrite text)
edit(
    Q,
    '        "Q40",\n'
    '        "Has anyone held your role prior to you — and if so, what\'s the"\n'
    '        " organization\'s read on why they left?",\n'
    '        "forced_choice", 40, "late",',
    '        "Q40",\n'
    '        "Has anyone held your role prior to you, and if so, what\'s the"\n'
    '        " organization\'s read on why they left?",\n'
    '        "forced_choice", 40, "late",',
)

# 14. Q42 (already rewritten in commit 52e99ac -- editing its post-rewrite text)
edit(
    Q,
    '        "Q42",\n'
    '        "When a decision needs approval from one specific person — and that"\n'
    '        " person is unavailable — what happens?",\n'
    '        "forced_choice", 42, "late",',
    '        "Q42",\n'
    '        "When a decision needs approval from one specific person and that"\n'
    '        " person is unavailable, what happens?",\n'
    '        "forced_choice", 42, "late",',
)

# 15. Q47 (already rewritten in commit 52e99ac -- editing its post-rewrite text)
edit(
    Q,
    '        "Q47",\n'
    '        "Think of a manager you\'d describe as stretched thin or overloaded."\n'
    '        " Has anything changed for them — additional support, delegated"\n'
    '        " authority, or reduced scope — since that became clear?",\n'
    '        "forced_choice", 47, "late",',
    '        "Q47",\n'
    '        "Think of a manager you\'d describe as stretched thin or overloaded."\n'
    '        " Has anything changed for them (such as additional support, delegated"\n'
    '        " authority, or reduced scope) since that became clear?",\n'
    '        "forced_choice", 47, "late",',
)

# 16. Q50 (already rewritten in commit 52e99ac -- editing its post-rewrite text)
edit(
    Q,
    '        "Q50",\n'
    '        "Every organization has a group of people who are especially trusted"\n'
    '        " or protected — an inner circle. When someone in that group makes a"\n'
    '        " costly mistake, what happens to them?",\n'
    '        "forced_choice", 50, "late",',
    '        "Q50",\n'
    '        "Every organization has an inner circle or group of people who are"\n'
    '        " especially trusted or protected. When someone in that group makes a"\n'
    '        " costly mistake, what happens to them?",\n'
    '        "forced_choice", 50, "late",',
)

# 17. Q51
edit(
    Q,
    '        "Q51",\n'
    '        "How would you describe who gets included in the decisions"\n'
    '        " that matter here?",\n'
    '        "forced_choice", 51, "late",',
    '        "Q51",\n'
    '        "How would you describe who gets included in the decisions"\n'
    '        " that matter at your organization?",\n'
    '        "forced_choice", 51, "late",',
)

# ---------------------------------------------------------------------
# CLAUDE.md -- new house-style rule, appositive-list construction.
# ---------------------------------------------------------------------

edit(
    CLAUDE,
    "- No em-dashes as default connective tissue. An em-dash is permitted only to "
    "mark a genuine interruption or pivot for emphasis, something a comma, colon, "
    "or rephrase can't do as well, not a habitual way to link two clauses. Default "
    "to a comma, colon, or rephrase first. When used, write a real em-dash, never a "
    '"--" placeholder. In LLM system-prompt content specs, avoid entirely.',
    "- No em-dashes as default connective tissue. An em-dash is permitted only to "
    "mark a genuine interruption or pivot for emphasis, something a comma, colon, "
    "or rephrase can't do as well, not a habitual way to link two clauses. Default "
    "to a comma, colon, or rephrase first. When used, write a real em-dash, never a "
    '"--" placeholder. In LLM system-prompt content specs, avoid entirely.\n'
    '- Multi-item appositive lists (e.g. "your policies — handbook, documentation, '
    'compliance obligations") convert to "(such as X, Y, and Z)" parenthetical '
    "style rather than an em-dash-set-off list. Locked Aug 2026, distinct from the "
    "general em-dash-overuse rule above -- this is specifically about the "
    "list-appositive construction.",
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
