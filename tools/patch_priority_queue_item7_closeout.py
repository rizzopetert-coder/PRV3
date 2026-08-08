"""
Priority Queue item 7 closeout -- the contained half only. Two
unrelated fixes:

  1. engine/data/validate.py -- removes the two PRIOR_ADJUSTER_INDEX
     "none" event checks (existence, multiplier == 1.0): both test
     deprecated Mechanism 1 scoring semantics with zero live consumer
     (engine/output_synthesis.py's PRIOR_ADJUSTER_INDEX usage explicitly
     skips "none" and never reads .multiplier). The third check
     (elevated_states referential integrity against STATE_PROFILES) is
     left completely untouched -- different in kind, still useful
     regardless of Mechanism 1's live/dormant status.

  2. CLAUDE.md's locked "Engine state count" bumped 57 -> 58, now that
     the_inner_circle is genuinely complete, tested, and committed
     (8f36282, 58/58 HC passing). engine/data/validate.py's two
     dependent literals (state count, Attitude dimension count) updated
     to match -- the_inner_circle's primary_dimension is Attitude, so
     both counts moved by exactly 1.

Deliberately NOT touched, per explicit instruction: CLAUDE.md's "Test
suite minimum" and "Shannon Entropy max" lines (also reference 57,
also now stale, out of scope for this pass); validate.py's "all vectors
at 0.25 baseline" and "cluster-weight states have cluster_id" failures
(flagged separately, future-session investigations).

Usage:
  python tools/patch_priority_queue_item7_closeout.py --dry-run
  python tools/patch_priority_queue_item7_closeout.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================================
# 1. engine/data/validate.py -- remove the 2 deprecated-mechanism checks
# ============================================================================

edit(
    "engine/data/validate.py",
    '''check("Prior adjuster for none event exists", "none" in PRIOR_ADJUSTER_INDEX)
check("None event multiplier is 1.0", PRIOR_ADJUSTER_INDEX["none"].multiplier == 1.0)

# All elevated state_ids in prior adjusters exist in STATE_PROFILES''',
    '''# Prior adjuster "none" event existence/multiplier checks removed this
# session (Mechanism 1 deprecation follow-up, Priority Queue item 7) --
# both tested deprecated scoring-mechanism semantics with zero live
# consumer (engine/output_synthesis.py's PRIOR_ADJUSTER_INDEX usage
# explicitly skips "none" and never reads .multiplier). Referential-
# integrity check below kept -- different in kind, still useful
# regardless of Mechanism 1's live/dormant status. See Decision Register.

# All elevated state_ids in prior adjusters exist in STATE_PROFILES''',
)

# ============================================================================
# 2a. engine/data/validate.py -- state count literal 57 -> 58
# ============================================================================

edit(
    "engine/data/validate.py",
    'check("State count is 57", n == 57, f"got {n}")',
    'check("State count is 58", n == 58, f"got {n}")',
)

# ============================================================================
# 2b. engine/data/validate.py -- Attitude dimension count literal 21 -> 22
# ============================================================================

edit(
    "engine/data/validate.py",
    'check("Attitude count = 21", dim_counts.get("Attitude",  0) == 21, f"got {dim_counts.get(\'Attitude\',0)}")',
    'check("Attitude count = 22", dim_counts.get("Attitude",  0) == 22, f"got {dim_counts.get(\'Attitude\',0)}")',
)

# ============================================================================
# 2c. CLAUDE.md -- locked Engine state count 57 -> 58
# ============================================================================

edit(
    "CLAUDE.md",
    "| Engine state count | 57 (locked) |",
    "| Engine state count | 58 (locked) |",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    by_file: dict[str, list[tuple[str, str]]] = {}
    for path, old, new in EDITS:
        by_file.setdefault(path, []).append((old, new))

    for rel_path, pairs in by_file.items():
        full_path = REPO_ROOT / rel_path
        content = full_path.read_text(encoding="utf-8")
        for old, new in pairs:
            count = content.count(old)
            if count != 1:
                print(f"ABORT: {rel_path}: expected exactly 1 match for anchor, found {count}")
                print(f"  anchor (first 150 chars): {old[:150]!r}")
                sys.exit(1)
            content = content.replace(old, new, 1)

        if args.dry_run:
            print(f"=== {rel_path}: {len(pairs)} edit(s) would apply cleanly ===")
        else:
            full_path.write_text(content, encoding="utf-8")
            print(f"=== {rel_path}: {len(pairs)} edit(s) written ===")

    if args.dry_run:
        print("\nDry run complete. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
