"""
PRV3 -- Append "Resolving intra-state variance" section to
prompts/friction-tax-state-multiplier-methodology.md, between "Scoring
criteria" and "Combination function". Content supplied verbatim by
Pete. No other section touched.

Usage:
  python tools/patch_friction_tax_methodology_intra_variance.py --dry-run
  python tools/patch_friction_tax_methodology_intra_variance.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "prompts" / "friction-tax-state-multiplier-methodology.md"

ANCHOR = (
    "A one-line rationale is required per criterion score, per state, "
    "for audit-trail defensibility — not just the numeric total.\n"
    "\n"
    "## Combination function\n"
)

NEW_SECTION = (
    "A one-line rationale is required per criterion score, per state, "
    "for audit-trail defensibility — not just the numeric total.\n"
    "\n"
    "## Resolving intra-state variance\n"
    "\n"
    "Some states' cost profile varies by context — e.g., role level, "
    "team size, or which sub-case of the condition is present. When a "
    "criterion's score would differ depending on context, score for the "
    "TYPICAL / MODAL instance of the condition, not the worst-case or an "
    "averaged range. Edge cases are deliberately ignored in scoring, "
    "though a rationale may still note them for context.\n"
    "\n"
    "This rule was surfaced during scoring of built_to_fail's "
    "Legal/Compliance criterion, where the initial rationale reasoned "
    "about role-level variance (leadership vs. mid-level incumbents) "
    "rather than committing to a single typical case.\n"
    "\n"
    "## Combination function\n"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = TARGET_FILE.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count == 0:
        print("ABORT -- anchor not found", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- anchor not unique ({count} matches)", file=sys.stderr)
        sys.exit(1)

    print(f"Target: {TARGET_FILE.relative_to(REPO_ROOT)}")
    print("=" * 72)
    print("- " + ANCHOR.rstrip("\n").replace("\n", "\n- "))
    print()
    print("+ " + NEW_SECTION.rstrip("\n").replace("\n", "\n+ "))
    print("=" * 72)
    print("No other section touched.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    new_text = text.replace(ANCHOR, NEW_SECTION)
    TARGET_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
