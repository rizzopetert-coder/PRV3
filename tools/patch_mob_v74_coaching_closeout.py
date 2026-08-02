"""
PRV3 -- Combined write: tools/_mob.txt version header bump (v4.73 ->
v4.74), new Section 16 session log row (individual coaching's last
open item closed), a short Section 8 cross-reference to the existing
MOB v4.19 decision record (avoids duplicating the full narrative), and
CLAUDE.md's MOB version cross-reference update.

Framing corrected before writing, per Pete's explicit confirmation: the
individual-coaching-service-brief.md file was NOT lost or committed
this session -- direct git verification (git log) confirmed it was
already committed via 6b64fe6 in a prior session, and the decision was
already fully documented as a Section 16 entry (MOB v4.19). The only
thing this session actually did was close that entry's own remaining-
work line ("draft final confidentiality template field wording") by
drafting and approving the four verbatim category descriptions. This
entry reflects that accurately rather than repeating the stale
"reconstructed/lost this session" framing the task was initially
handed with.

Usage:
  python tools/patch_mob_v74_coaching_closeout.py --dry-run
  python tools/patch_mob_v74_coaching_closeout.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

# ── CLAUDE.md: version cross-reference ──────────────────────────────────────

CLAUDE_ANCHOR = "| MOB version | v4.73 |"
CLAUDE_REPLACEMENT = "| MOB version | v4.74 |"

# ── tools/_mob.txt: version header ──────────────────────────────────────────

MOB_HEADER_ANCHOR = "\\\\\\#\\\\\\# MOB v4.73"
MOB_HEADER_REPLACEMENT = "\\\\\\#\\\\\\# MOB v4.74"

# ── tools/_mob.txt: Section 8 cross-reference (short, no duplication) ──────

SECTION8_ANCHOR = (
    "\\*\\*Diagnostic is unaffected\\*\\* — remains branded, sits above the "
    "four as the entry-point layer per the Session 33 two-tier lock. "
    "Nothing about Diagnostic's name, position, or treatment changed.\n"
)

SECTION8_NEW_PARAGRAPH = (
    "\\*\\*Individual coaching as a service offering — locked, full "
    "decision record in Section 16 (MOB v4.19), not duplicated here:\\*\\* "
    "Nested as a delivery mode within Executive Advisory, not a fifth "
    "named service — no change to the five service names above. "
    "Confidentiality boundary (fixed-category, open-content reporting "
    "template) and its final verbatim client-facing field wording closed "
    "out August 2026 — see the \"June 2026 — Individual Coaching Service "
    "Offering\" and \"August 2026 — Individual coaching\" Section 16 "
    "entries for the complete decision and execution detail.\n"
)

# ── tools/_mob.txt: new Section 16 row ──────────────────────────────────────

SECTION16_ANCHOR = "MOB v4.73. |\n| **May 2026"

NEW_ROW = (
    "| **August 2026 — Individual coaching: confidentiality template "
    "wording closed, JSON-LD status corrected for the record** | "
    "**Individual coaching.** The individual coaching service offering "
    "decision itself was already resolved and already committed -- "
    "confirmed directly via git, not assumed: documents/individual-"
    "coaching-service-brief.md was committed as 6b64fe6 in a prior "
    "session and remains on disk unchanged, and the full decision "
    "(org-always-wins governing principle, nested as a delivery mode "
    "within Executive Advisory rather than a fifth named service, no "
    "new instrument required, the \"coaching\" verb-only copy rule, the "
    "fixed-category/open-content confidentiality template mechanism) is "
    "already on record as the \"June 2026 — Individual Coaching Service "
    "Offering\" Section 16 entry, MOB v4.19. That entry's own closing "
    "line named exactly one open item: \"draft final confidentiality "
    "template field wording.\" This session closed it -- the four "
    "category descriptions were drafted and approved in client-facing "
    "language: (1) Engagement status and cadence -- whether sessions are "
    "happening on schedule, how many have occurred, and whether the "
    "engagement is on track, paused, or nearing its planned end, no "
    "content from what's discussed; (2) Themes -- the organizational "
    "condition or pattern this work is addressing, in the same terms "
    "used in the original diagnostic, not session notes or specific "
    "things said in a given conversation; (3) Progress against stated "
    "goals -- movement toward the goals set at the start of the "
    "engagement, described in general terms, not a transcript of how "
    "that movement happened; (4) Flagged items -- anything that surfaces "
    "during the work that reflects a condition in the organization "
    "itself, not just something personal to the individual leader, "
    "routed to the org-level conversation if it belongs there -- the one "
    "category where new information can appear that wasn't anticipated "
    "at the start. The formal engagement agreement will carry additional "
    "confidentiality stipulations around this client-facing template, "
    "not replace it. Remaining gate: attorney review of engagement "
    "agreement Section 3 -- unchanged, separately PARKED per standing "
    "instruction (same gate as the LinkedIn amplification hold), not "
    "blocking or urgent, no forced check-in. Corrected in passing: an "
    "earlier framing in this session assumed the brief file had been "
    "lost to the project's session-output-evaporation pattern and "
    "needed reconstruction -- direct git verification found this was "
    "inaccurate for the current moment; that reconstruction-and-commit "
    "event already happened in a prior session, confirmed by the "
    "commit's own timestamp and the brief file's own internal note "
    "describing it. **Schema.org JSON-LD status, also corrected for the "
    "record:** a separate stale assumption earlier this session held "
    "that Step 5 (Schema.org JSON-LD) of the /book taxonomy initiative "
    "was still drafted but not executed. Direct search (prompts/, "
    "documents/, research/, full-repo grep, git log) found no separate "
    "drafted-but-unexecuted handoff exists -- Step 5 was fully built and "
    "shipped as part of commit a91a28c alongside Steps 0-4, confirmed "
    "live in the current web/app/book/[type]/[slug]/page.tsx "
    "(buildJsonLd() function, <script type=\"application/ld+json\"> "
    "render) and already on record in the MOB's own Section 13 open-"
    "items table. No code changes from either correction -- both are "
    "read-only status verifications. CLAUDE.md MOB version cross-"
    "reference updated v4.73->v4.74. MOB version bumped to v4.74 -- "
    "closes the last open item from a previously-locked decision "
    "(individual coaching's confidentiality template wording) and "
    "corrects two stale in-session assumptions for the standing record, "
    "warrants a bump per the closeout protocol. MOB v4.74. |\n"
    "| **May 2026"
)


def _apply(text: str, anchor: str, replacement: str, label: str) -> str:
    count = text.count(anchor)
    if count == 0:
        print(f"ABORT -- anchor not found: {label}", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- anchor not unique ({count} matches): {label}", file=sys.stderr)
        sys.exit(1)
    return text.replace(anchor, replacement)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    claude_text = CLAUDE_MD.read_text(encoding="utf-8")
    mob_text = MOB_FILE.read_text(encoding="utf-8")

    claude_text = _apply(claude_text, CLAUDE_ANCHOR, CLAUDE_REPLACEMENT, "CLAUDE.md MOB version cross-reference")
    mob_text = _apply(mob_text, MOB_HEADER_ANCHOR, MOB_HEADER_REPLACEMENT, "tools/_mob.txt version header")
    mob_text = _apply(mob_text, SECTION8_ANCHOR, SECTION8_ANCHOR + "\n" + SECTION8_NEW_PARAGRAPH, "tools/_mob.txt Section 8 cross-reference")
    mob_text = _apply(mob_text, SECTION16_ANCHOR, "MOB v4.73. |\n" + NEW_ROW, "tools/_mob.txt Section 16 new row")

    print("All 4 anchors found and unique. Changes:")
    print("=" * 72)
    print("1. CLAUDE.md -- MOB version v4.73 -> v4.74")
    print("2. tools/_mob.txt -- header MOB v4.73 -> v4.74")
    print("3. tools/_mob.txt -- Section 8: new short cross-reference")
    print("   paragraph pointing to the Section 16 / MOB v4.19 record")
    print("4. tools/_mob.txt -- new Section 16 row (individual coaching")
    print("   confidentiality wording closed, JSON-LD status corrected)")
    print("=" * 72)

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    CLAUDE_MD.write_text(claude_text, encoding="utf-8")
    MOB_FILE.write_text(mob_text, encoding="utf-8")
    print("\nWROTE CLAUDE.md")
    print("WROTE tools/_mob.txt")


if __name__ == "__main__":
    main()
