"""
PRV3 -- MOB update: Q46 topical-mismatch flag closed, resolved-by-decision.

The A5 + Structure 3 combined recalibration row (Section 13a) closed with
an open note: "Q46's topical-continuity mismatch with Q44/Q45 remains a
separate, real, unresolved content item -- not reopened or fixed here,
flagged for whenever Pete schedules that work." Pete's call this session:
that flag only ever mattered in the context of whether to chain Q46 under
Q45 -- since chaining was already declined during Structure 3 (Q46 left
untouched, standalone), there's no remaining code or content issue. New
row added rather than editing the original (preserves the historical
record of what was actually decided at the time), per Pete's explicit
"new Decision Register row" framing.

No code changes. Version bump v4.141 -> v4.142: a Decision Register item
closes.

Usage:
  python tools/patch_mob_q46_closed.py --dry-run
  python tools/patch_mob_q46_closed.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


MOB = "tools/_mob.txt"

ANCHOR = (
    "| Category D (free condensed diagnostic) -- concept sketch drafted | 3 | **Exploratory, not approved for build** | N/A | prompts/category-d-condensed-diagnostic.md written -- a durable planning artifact, no code changes, no engine writes. Concept: a <5-minute free experience (8-10 questions, drawn entirely from the existing 42 core questions -- zero new content, zero new taxonomy, zero calibration risk) producing a real-but-thin report as a lead-capture point funneling toward the paid full Dx. Result shape truncates the full report structurally (top state only, 2-3 indicators, one-paragraph synthesis, a simple single-benchmark financial figure instead of full Friction Tax) with truncation shown visibly, not silently omitted. The financial mechanic is explicitly NOT Friction Tax's multi-state compounding model -- flagged as needing its own (lighter) Demographic Applicability Filter pass per the existing locked protocol before any real benchmark figure ships. Full diagnostic stays exactly as-is (free, ungated) regardless of this build -- any paywall/lead-capture gating decision for the full Dx is explicitly a separate, later decision, not blocking. Three open questions logged unresolved, Pete's call: exact question count (8-10, or review concrete candidates first), visible-truncation UI treatment, and the full-Dx gating mechanism. | This session (Claude Code) | Pete's call -- reopen when ready to review concrete candidate questions and move toward a build decision, not a forced check-in |"
)

NEW_ROW = (
    '\n'
    '| Q46 topical mismatch -- CLOSED, no action needed | 3 | **Closed -- resolved by decision, not deferred** | N/A | Originally flagged during Structure 3\'s Gemini review: Q46 (the_arbitrary_standard) shares no topical continuity with Q44/Q45 (the_tolerated_violation), so chaining it under Q45 was explicitly declined -- Q46 left standalone, untouched, in the A5 + Structure 3 combined recalibration (Section 13a above). That row\'s own close-out carried the mismatch forward as a separate open item ("remains a separate, real, unresolved content item... flagged for whenever Pete schedules that work"). Pete\'s call this session: the flag only ever mattered in the context of whether to chain Q46 under Q45 -- since that chaining was already declined, not left pending, there is no remaining code or content issue to schedule. Q46 stays a standalone core question permanently, confirmed as the intended design, not a gap. | This session (Claude Code) | Closed -- no further check-in |\n'
)


def apply(dry_run: bool) -> int:
    changed = 0
    path = REPO_ROOT / MOB
    text = path.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count != 1:
        print(f"ERROR: {MOB} -- expected 1 match for anchor, found {count}")
        return 1
    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROW, 1)
    if dry_run:
        print(f"OK (dry-run): {MOB} -- anchor found, would insert 1 new row")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"WRITTEN: {MOB} -- 1 new row inserted")
    changed += 1

    version_edits = [
        (MOB, "\\\\\\#\\\\\\# MOB v4.141", "\\\\\\#\\\\\\# MOB v4.142"),
        ("CLAUDE.md", "| MOB version | v4.141 |", "| MOB version | v4.142 |"),
    ]
    for rel_path, old, new in version_edits:
        p = REPO_ROOT / rel_path
        t = p.read_text(encoding="utf-8")
        c = t.count(old)
        if c != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {c}")
            return 1
        nt = t.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            p.write_text(nt, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1

    print(f"\n{changed}/3 edits {'validated' if dry_run else 'applied'}.")
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
