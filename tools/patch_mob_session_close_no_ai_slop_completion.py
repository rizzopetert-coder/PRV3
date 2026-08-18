"""
PRV3 -- session closeout MOB update.

Appends one new Section 16 session log row summarizing this session's
work: completion of the em-dash-cap remediation project across the full
87-file published /book corpus (Tier 1 continuation through Tier 4 plus
a worst-first sweep of the remaining queue), the citation/factual fixes
caught along the way, and the standing mojibake-detection discipline
that held throughout.

No new locked decisions, rules, or material workstream-status changes
were made this session (per CLAUDE.md's closeout protocol, this means
the MOB version number stays unchanged at v4.183 -- session log entry
only).

Usage:
  python tools/patch_mob_session_close_no_ai_slop_completion.py --dry-run
  python tools/patch_mob_session_close_no_ai_slop_completion.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_PATH = REPO_ROOT / "tools" / "_mob.txt"

ANCHOR = "| 2026-08-16 -- Session close: /book/toc Phases 1-4 shipped"

NEW_ROW = (
    "| 2026-08-17 -- Session close: no-ai-slop em-dash-cap remediation closed out "
    "end-to-end across the full 87-file published /book corpus, MOB v4.183 (unchanged -- "
    "no new locked decisions this session) | Continued a batch that started mid-file "
    "(hr-is-the-table.md) and worked worst-first through the entire remaining "
    "em-dash-over-cap queue: what-their-resistance-is-actually-telling-you, "
    "when-the-data-points-at-the-person-who-hired-you, "
    "symptoms-states-and-why-the-distinction-matters, "
    "earned-effectiveness-conversation-framework, "
    "the-problem-they-brought-you-is-not-always-the-problem, the full 6-file Tier 3 "
    "signature-closer group (matrix-organization, leadership-deafness, "
    "the-untouchable, succession-planning, no-margin-for-error, accountability), "
    "Tier 4 (intellectual-bottleneck), and a 13-file worst-first continuation "
    "(the-policy-lag, the-unlocked-door, decision-paralysis, the-lost-map, "
    "the-unreported-hazard, groundhog-day, the-overloaded-manager, the-paper-tiger, "
    "velocity-of-truth, why-your-team-stopped-disagreeing-with-you, "
    "feedback-nobody-wants-to-say, the-tolerated-violation, dueling-narratives, "
    "narrative-lock, crisis-as-catalyst-for-clarity, the-unformed-leader). "
    "**Two real citation/factual fixes caught and corrected along the way:** "
    "leadership-deafness.md's Keltner claim (\"it literally changes your brain\") "
    "was an overclaim -- Keltner's actual research is behavioral, not neural; "
    "independently verified via WebSearch against *The Power Paradox*'s real findings "
    "before correcting to \"makes you worse at reading other people,\" matching the "
    "already-corrected HC-103 wording elsewhere in the corpus. "
    "symptoms-states-and-why-the-distinction-matters.md's \"fifty-seven institutional "
    "states\" was a stale pre-taxonomy-expansion figure, corrected to \"fifty-eight\" "
    "after confirming the locked count against the live MOB. **Standing discipline held "
    "without exception across every file delivered this session:** the chat-paste "
    "channel corrupted em-dashes to a stray \"â\" character in every single delivery "
    "(dozens of times, including inside signature-closer lines), never trusted or "
    "used; Downloads/zip delivery was byte-verified clean before every write, diffed "
    "against live before applying, and independently re-verified after. Mechanical "
    "scan (tools/diag_book_mechanical_scan.py) re-run after every fix; "
    "prompts/no-ai-slop-mechanical-scan.md kept current with running totals "
    "throughout, including two self-caught errors reported plainly rather than "
    "smoothed over -- a duplicate table row from an earlier edit, and a false "
    "\"Tier 3 complete\" claim caught before commit when accountability.md turned out "
    "to have been missed (never actually sent), corrected in the same session. "
    "**Final state:** 0 of 87 files genuinely over the locked em-dash-per-8 cap. The "
    "raw mechanical scanner still nominally lists 6 files (the Tier 3 signature-closer "
    "group) because it doesn't apply the MOB v4.183 signature-line exemption -- each "
    "confirmed by hand at genuine prose count 8, at cap, not over. Near-duplicate "
    "closing pairs remain at 1 (the deliberately-accepted built-for-comfort.md/"
    "one-exception-at-a-time.md pair) and weasel-attribution files remain at 5 (all "
    "documented false positives or already-resolved citations), both unchanged and "
    "settled from earlier sessions. All content changes were pure punctuation "
    "conversions with zero wording or meaning changes, confirmed via diff before "
    "every apply. Diary written (AAAK, topic no-ai-slop-book-remediation). Mine run "
    "at closeout. | This session (Claude Code) | MOB v4.183 |"
)


def apply(dry_run: bool) -> int:
    if not MOB_PATH.exists():
        print(f"ABORT: {MOB_PATH} not found")
        return 1
    content = MOB_PATH.read_text(encoding="utf-8")
    if ANCHOR not in content:
        print("ABORT: anchor row not found -- MOB structure may have changed")
        return 1
    if NEW_ROW.split(" | ")[0] in content:
        print("ABORT: this session's row already appears to be present -- not duplicating")
        return 1

    old_row_start = content.index(ANCHOR)
    old_row_end = content.index("\n", old_row_start) + 1
    new_content = content[:old_row_end] + NEW_ROW + "\n" + content[old_row_end:]

    if dry_run:
        print(f"OK (dry-run): {MOB_PATH} -- {len(content)} chars -> {len(new_content)} chars")
        print(f"New row length: {len(NEW_ROW)} chars")
    else:
        MOB_PATH.write_text(new_content, encoding="utf-8")
        print(f"WRITTEN: {MOB_PATH}")

    if dry_run:
        print("\nDry run complete. Re-run with --write to apply.")
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
