"""
PRV3 -- correction: Pete's live before/after check on Category E
Directions 1 and 3 already happened within this session (both verified
via claude-in-chrome against Production, post-push) -- the Decision
Register rows and the Section 16 session-close entry were written before
Pete reported back and still described the check as pending. Corrected
here with the real outcome, not left stale.

Direction 1: rust-gating, gradient fill, and depth stacking all confirmed
correct against a real Endemic-tier result.
Direction 3: hero typography, softened eyebrow, cluster display, and
overflow affordance all confirmed correct -- after catching and resolving
a deploy-propagation lag that initially showed a stale state before the
real deployment caught up.

Both Decision Register rows' "next check-in" fields updated from
"reopen if the live check surfaces an issue" to "Closed -- passed."

Version bump v4.149 -> v4.150 -- two Decision Register items move from
open-pending to closed-verified, a real status change.

Usage:
  python tools/patch_mob_direction1_3_live_check_confirmed.py --dry-run
  python tools/patch_mob_direction1_3_live_check_confirmed.py --write
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

# ═══════════════════════════════════════════════════════════════════════
# Direction 1 row -- verification sentence + closing "next check-in".
# ═══════════════════════════════════════════════════════════════════════

edit(
    MOB,
    "Live before/after screenshot verification held for Pete via claude-in-chrome against Production post-push, same method already used for Q05 and the A.2/A.3 checks this session -- no browser tool available in this Claude Code session, confirmed via fresh tool search before asking, not assumed. Diff reviewed and approved by Pete before commit.",
    "Live before/after verification completed by Pete via claude-in-chrome against Production post-push, same method already used for Q05 and the A.2/A.3 checks this session -- confirmed correct: rust-gating, gradient fill, and depth stacking all verified against a real Endemic-tier result. Diff reviewed and approved by Pete before commit.",
)

edit(
    MOB,
    "Pete's call -- reopen if the live before/after check surfaces a rendering issue; otherwise closed, Directions 2/3 stay concept-level per the existing sequencing row until Pete decides to explore further |",
    "Closed -- live before/after check passed, no issues found. Directions 2/3 stay concept-level per the existing sequencing row until Pete decides to explore further |",
)

# ═══════════════════════════════════════════════════════════════════════
# Direction 3 row -- verification sentence + closing "next check-in".
# ═══════════════════════════════════════════════════════════════════════

edit(
    MOB,
    "Logic-level only -- cannot confirm visual layout without a browser, held for Pete's live check.",
    "Logic-level verification only at commit time; Pete's subsequent live check via claude-in-chrome against Production confirmed the visual build directly -- hero typography, softened eyebrow, cluster display, and overflow affordance all live and correct, after catching and resolving a deploy-propagation lag that initially showed a stale state before the real deployment caught up.",
)

edit(
    MOB,
    "Pete's call -- reopen if the live before/after check surfaces a rendering issue, or if the dropped-percentage decision doesn't read well live and needs reverting. Category E's three-direction sequencing is now fully explored",
    "Closed -- live before/after check passed, no issues found, dropped-percentage decision confirmed reading well live. Category E's three-direction sequencing is now fully explored",
)

# ═══════════════════════════════════════════════════════════════════════
# Section 16 session-close entry -- verification sentence.
# ═══════════════════════════════════════════════════════════════════════

edit(
    MOB,
    "Live browser before/after verification for both Category E directions held for Pete via claude-in-chrome post-push -- no browser tool available in this Claude Code session, confirmed via fresh tool search before asking each time, not assumed from earlier context.",
    "Live browser before/after verification for both Category E directions completed by Pete via claude-in-chrome post-push -- Direction 1 confirmed correct (rust-gating, gradient fill, depth stacking, verified against an Endemic-tier result); Direction 3 confirmed correct (hero typography, softened eyebrow, cluster display, overflow affordance), after catching and resolving a deploy-propagation lag before confirming the final live state matched the build.",
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

    version_edits = [
        (MOB, "\\\\\\#\\\\\\# MOB v4.149", "\\\\\\#\\\\\\# MOB v4.150"),
        ("CLAUDE.md", "| MOB version | v4.149 |", "| MOB version | v4.150 |"),
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

    print(f"\n{changed}/{len(EDITS) + 2} edits {'validated' if dry_run else 'applied'}.")
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
