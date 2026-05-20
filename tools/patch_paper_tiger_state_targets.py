"""
Patch: engine/data/questions.py — add the_paper_tiger to Q05 and Q12 state_targets (Session 21)

Q06 excluded — held for Gemini review (Authority-primary question, cross-axis signal risk).

Changes:
  1. Q05 state_targets: append "the_paper_tiger"
  2. Q12 state_targets: append "the_paper_tiger"

Usage:
  python tools/patch_paper_tiger_state_targets.py --dry-run
  python tools/patch_paper_tiger_state_targets.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"

CHANGES = [
    {
        "description": 'Q05 state_targets: append "the_paper_tiger"',
        "old": (
            '        ["the_basement_standard", "the_untouchable", "the_inside_track",\n'
            '         "the_arbitrary_standard", "the_wrong_reward"],'
        ),
        "new": (
            '        ["the_basement_standard", "the_untouchable", "the_inside_track",\n'
            '         "the_arbitrary_standard", "the_wrong_reward", "the_paper_tiger"],'
        ),
    },
    {
        "description": 'Q12 state_targets: append "the_paper_tiger"',
        "old": (
            '        ["the_unformed_leader", "the_overloaded_manager", "the_dormant_talent",\n'
            '         "the_untouchable", "leadership_deafness", "the_suppression_filter"],'
        ),
        "new": (
            '        ["the_unformed_leader", "the_overloaded_manager", "the_dormant_talent",\n'
            '         "the_untouchable", "leadership_deafness", "the_suppression_filter",\n'
            '         "the_paper_tiger"],'
        ),
    },
]


def apply(content: str, dry_run: bool) -> tuple[str, list[str]]:
    log = []
    for change in CHANGES:
        old = change["old"]
        new = change["new"]
        desc = change["description"]
        if old not in content:
            log.append(f"  [ERROR] Not found: {desc}")
            continue
        count = content.count(old)
        if count > 1:
            log.append(f"  [ERROR] Ambiguous match ({count}x): {desc}")
            continue
        if dry_run:
            log.append(f"  [DRY-RUN] Would apply: {desc}")
        else:
            content = content.replace(old, new)
            log.append(f"  [APPLIED] {desc}")
    return content, log


def main():
    dry_run = "--write" not in sys.argv
    mode = "DRY-RUN" if dry_run else "WRITE"

    print(f"\n{'='*64}")
    print(f"patch_paper_tiger_state_targets.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'='*64}\n")

    if not TARGET.exists():
        print("[ERROR] Target file not found.")
        sys.exit(1)

    content = TARGET.read_text(encoding="utf-8")
    new_content, log = apply(content, dry_run)

    errors = [l for l in log if "[ERROR]" in l]
    for line in log:
        print(line)

    if errors:
        print(f"\n[ABORT] {len(errors)} error(s). No changes written.")
        sys.exit(1)

    if not dry_run:
        TARGET.write_text(new_content, encoding="utf-8")
        print(f"\n[DONE] {TARGET} written.")
    else:
        print(f"\n[DRY-RUN COMPLETE] {len(CHANGES)} change(s) validated. Run with --write to apply.")

    sys.exit(0)


if __name__ == "__main__":
    main()
