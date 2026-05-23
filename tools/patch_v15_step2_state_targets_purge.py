"""
Patch: engine/data/questions.py — Step 2 state_targets Purge (v15)

Changes (all in _QDATA state_targets):
  Q07: remove built_to_fail, the_untouchable, the_diversity_ceiling,
       the_inside_track, invisible_burnout, the_unformed_leader,
       the_overloaded_manager, the_dormant_talent
       (post-drain Q07 is pure Alliance; zero signal for non-Alliance states)
  Q09: remove decision_paralysis
       (post-drain Q09 is pure Alliance; zero authority signal for Authority state)

Usage:
  python tools/patch_v15_step2_state_targets_purge.py --dry-run
  python tools/patch_v15_step2_state_targets_purge.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"

CHANGES = [
    {
        "description": (
            "Q07 state_targets: remove 8 non-Alliance states "
            "(retain the_fracture, silosolation)"
        ),
        "old": (
            '        ["the_fracture", "silosolation", "built_to_fail", "the_untouchable",\n'
            '         "the_diversity_ceiling", "the_inside_track", "invisible_burnout",\n'
            '         "the_unformed_leader", "the_overloaded_manager", "the_dormant_talent"],'
        ),
        "new": (
            '        ["the_fracture", "silosolation"],'
        ),
    },
    {
        "description": (
            "Q09 state_targets: remove decision_paralysis "
            "(retain the_fracture, silosolation)"
        ),
        "old": (
            '        ["the_fracture", "silosolation", "decision_paralysis"],'
        ),
        "new": (
            '        ["the_fracture", "silosolation"],'
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
    print(f"patch_v15_step2_state_targets_purge.py — {mode}")
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
