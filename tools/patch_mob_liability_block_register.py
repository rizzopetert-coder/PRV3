"""
PRV3 -- Decision Register addition: test_contract.py section 12
liability_block KeyError (pre-existing, unrelated, informational).

Confirmed not already tracked as a Section 13a row (only mentioned in
Section 16 session-log narrative, reconfirmed multiple times across
sessions but never given its own named entry). Adds one new row so a
future session doesn't have to re-discover and re-confirm it's not a
regression every time it surfaces in a test run.

Informational only -- no locked decision, no rule change, no material
workstream status change, so MOB version is NOT bumped per CLAUDE.md's
own increment rule.

Usage:
  python tools/patch_mob_liability_block_register.py --dry-run
  python tools/patch_mob_liability_block_register.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

ANCHOR = (
    '| "Same Rules, Different Results" (draft rename of expansion-state '
    '"Disparate Impact Architecture," public/diagnostic-facing only) | 3 '
    '| Provisional Hold, not Locked | Attorney review — same gate as '
    'LinkedIn/coaching template, not yet scheduled | This session | '
    'Legal-characterization risk (naming a user\'s org with an '
    'EEOC-recognized legal term), not just a voice question. Revisit '
    'whenever the attorney-review gate opens, not before |\n'
)

NEW_ROW = (
    '| test_contract.py section 12 liability_block KeyError -- '
    'pre-existing, confirmed unrelated | 3 | Open, informational -- no '
    'urgency, not chased down | engine/contract.py\'s private_output '
    'block construction does not set a "liability_block" key that '
    'test_contract.py\'s section 12 assertion (line ~422) expects -- a '
    'pre-existing mismatch between the test and the real contract, '
    'confirmed via git stash this session to predate the descriptive_prose '
    'schema work (and every other change made this session), consistent '
    'with the "confirmed since Session 57" finding already on record in '
    'session-log narrative. Crashes the whole script with an uncaught '
    'KeyError rather than a caught check() failure, so it never reaches '
    'its own final PASS/FAIL tally print -- every run since must manually '
    'confirm the earlier sections (1-11) passed before treating a crash '
    'here as unrelated, rather than reading a clean summary line directly. '
    'Not fixed here, out of scope for the work that surfaced it each time '
    '| This session (Claude Code) -- reconfirmed via git stash, not fixed '
    '| No forced check-in -- worth a real fix whenever engine/contract.py\'s '
    'private_output block or test_contract.py\'s section 12 gets touched '
    'for an unrelated reason, at which point it is a cheap fix to make '
    'while already in that code |\n'
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = MOB_FILE.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count == 0:
        print("ABORT -- anchor not found", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- anchor not unique ({count} matches)", file=sys.stderr)
        sys.exit(1)

    print("New Decision Register row (Section 13a), inserted after the")
    print('"Same Rules, Different Results" row:')
    print("=" * 72)
    print(NEW_ROW.rstrip("\n"))
    print("=" * 72)
    print("No version bump -- informational addition only, per CLAUDE.md's")
    print("own increment rule (locked decisions / rule changes / material")
    print("workstream status changes only).")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROW)
    MOB_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {MOB_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
