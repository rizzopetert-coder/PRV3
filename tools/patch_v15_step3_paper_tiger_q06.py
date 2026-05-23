"""
Patch: engine/data/questions.py — Step 3 Paper Tiger Q06 Fix (v15)

Changes:
  Change A — Q06 state_targets: append the_paper_tiger
  Change B — Q06 option D vector:
    aptitude_liability 0.25 -> 0.60 (capability failure signal)
    authority_liability 0.60 -> 0.00 (authority stripped)
    attitude_liability 0.30 retained

Option D text: "A known practice that you're aware isn't fully compliant
but hasn't been addressed." — sole candidate for capability/architectural
failure on Q06. Unambiguous.

Usage:
  python tools/patch_v15_step3_paper_tiger_q06.py --dry-run
  python tools/patch_v15_step3_paper_tiger_q06.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"

CHANGES = [
    {
        "description": "Q06 state_targets: append the_paper_tiger",
        "old": (
            '        ["heard_and_ignored", "the_unsolved_problem", "decision_blindness",\n'
            '         "the_tolerated_violation", "the_policy_lag"],'
        ),
        "new": (
            '        ["heard_and_ignored", "the_unsolved_problem", "decision_blindness",\n'
            '         "the_tolerated_violation", "the_policy_lag", "the_paper_tiger"],'
        ),
    },
    {
        "description": (
            "Q06 option D: aptitude_liability 0.25->0.60, "
            "authority_liability 0.60->0.00, attitude_liability 0.30 retained"
        ),
        "old": (
            '            "D": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30, "aptitude_liability": 0.25},  # P'
        ),
        "new": (
            '            "D": {**_z, "aptitude_liability": 0.60, "attitude_liability": 0.30},  # P — APT-PT fix v15'
        ),
    },
]


def apply(content: str, dry_run: bool) -> tuple[str, list[str]]:
    log = []
    for change in CHANGES:
        old, new, desc = change["old"], change["new"], change["description"]
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
    print(f"patch_v15_step3_paper_tiger_q06.py — {mode}")
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
        print(f"\n[DRY-RUN COMPLETE] {len(CHANGES)} change(s) validated.")
    sys.exit(0)


if __name__ == "__main__":
    main()
