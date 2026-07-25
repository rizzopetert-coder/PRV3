#!/usr/bin/env python
"""
PRV3 -- patch_mob_book_golive.py
Logs the /book go-live event: 87 non-parked entries published, LIB-037
remains parked, full lineage from the staged-sequence proposal through
Pete's decision to publish all at once, the rendering fix, the status
flip, and the Production deploy. Closes Section 13a's /book publish
decision row (previously Deferred) as Closed/Live. Adds a Section 14
locked-decision entry and a Section 16 session-log entry. Bumps MOB
version v4.65 -> v4.66.

Usage:
  python tools/patch_mob_book_golive.py --dry-run
  python tools/patch_mob_book_golive.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "tools" / "_mob.txt"

CHANGES = []


def edit(label, old, new):
    CHANGES.append((label, old, new))


# ── 1. Version bump ───────────────────────────────────────────────────────────
edit(
    "MOB version v4.65 -> v4.66",
    "\\\\\\#\\\\\\# MOB v4.65",
    "\\\\\\#\\\\\\# MOB v4.66",
)

# ── 2. Section 13a: close the /book publish decision row ──────────────────────
OLD_ROW = '''| /book publish decision (88 drafted pieces, corrected from earlier 50/71 progression-snapshot figures) | 3 | Deferred | No decision made -- not blocked externally. Attorney-review scope CONFIRMED and CLOSED as a question (Pete, direct): /book content was never in scope for attorney review -- that gate covers only the LinkedIn campaign and the coaching engagement template (see the separate "Attorney review (LinkedIn + coaching template gate)" row below), not /book publication. Prior session's readiness sweep (Claude Code) still holds: nav link confirmed live on every route (mounted once in root layout, single non-responsive markup shared by desktop/mobile); manifest/content cross-reference clean (88 manifest entries, 88 content files, zero missing, zero orphans); citation-free compliance re-verified by direct read of all 36 FTA-18-FTA-53 pieces (Session 57 finding holds, zero external claims without citation, the-unexamined-algorithm's real citations confirmed still attached); shadow-model sweep clean (zero hits for Pete's name or OneDigital across all 88 files). Two gaps found that block real discoverability regardless of this decision: (1) all 88 entries are `status: draft` or `parked`, zero `published` -- both the index page and the `[type]/[slug]` page gate strictly on `published`, so `/book` currently renders 'Coming soon.' live, confirmed by fetching it; (2) the `[type]/[slug]` page never renders the markdown body, only title+teaser -- a code comment describes this as deferred to a 'content migration pass' that appears not to have happened. Neither gap is a defect from any one session -- both pre-exist, surfaced by the readiness sweep | This session (Claude Code) | Whenever Pete is ready to decide -- no attorney-review dependency anymore. The two content-rendering/publish-status gaps above need scoping alongside the publish decision itself, not discovered again after |'''

NEW_ROW = '''| /book publish decision -- CLOSED, LIVE IN PRODUCTION | 4 (irreversible, public content publish) | Closed -- live | Pete's explicit decision: publish all 87 non-parked entries at once rather than the staged 4-batch sequence originally proposed (Batch 1 evidentiary-anchor/22 cited pieces, Batch 2 conceptual-core/14, Batch 3 remaining-memos/9, Batch 4 FTA-narrative-corpus/42) -- that staged sequence is repurposed as the LinkedIn promotional posting order instead, decoupled from site publish timing entirely, not discarded. Full prerequisite chain closed this session: markdown-body rendering built and committed (4402c24) -- react-markdown, no plugins (zero links/tables/code-fences/embedded-JSX in the 88-file corpus, confirmed by direct scan before choosing an approach), components mapped to the locked visual identity rather than generic Tailwind Typography defaults, leading H1 stripped position-based (not string-matched against piece.title, avoiding fragility against wording/whitespace drift); citation-free compliance re-verified by direct read of all 36 FTA-18-53 pieces (Session 57 finding holds); shadow-model sweep clean (zero hits for Pete's name or OneDigital across all 88 files); nav confirmed live. Bulk status flip: 87 entries `draft`->`published`, LIB-037 (Organizational Assessment: Engagement SOP) deliberately excluded, stays `parked` -- verified via exact string-count checks before and after write (the comma-inclusive `status: "draft",` pattern was specifically chosen to exclude the BookPiece interface's own type-union declaration line, which contains the bare substring without a trailing comma there), commit a4aaf8f. Preview-verified before commit: 4 pieces spanning all three content types plus the corpus's only numbered-list file rendered correctly through the real status gate, /book index listed exactly 87 entries with LIB-037 absent and the "Coming soon." placeholder gone. **Production deploy confirmed live, same day:** all 4 pieces plus the index independently re-verified directly against `prv-3.vercel.app` (not just Preview) -- identical results: each piece's H1 renders exactly once, section headers/dividers/lists correct, index shows exactly 87 entries, LIB-037 confirmed absent. Tier 4 named risk categories (CLAUDE.md) checked clean before this action: citation/legal exposure (direct-read compliance sweep, not sampled), the OneDigital/shadow-model boundary (sweep clean, also direct-read), premature signaling (the rendering fix landed and was verified first, so the instrument was genuinely built to back the publish claim, not published ahead of being real). Pre-mortem, logged before proceeding: the most likely failure mode here was a citation or shadow-model miss slipping through despite the sweep, or the rendering fix silently breaking on some piece type the sample didn't cover -- neither condition was present, since both sweeps were direct-read verifications across the full corpus (not sampled) and the rendering test deliberately covered one file from each of the three structurally distinct content types plus the corpus's only outlier (the numbered list), not a single happy-path file | This session (Claude Code) | Closed -- no further check-in. /book is live in Production. If a rendering or content issue surfaces post-launch, treat it as a new incident, not a reopening of this row |'''

edit("Section 13a: close /book publish decision row as Closed/Live", OLD_ROW, NEW_ROW)

# ── 3. Section 14: new locked-decision entry ───────────────────────────────────
OLD_SECTION14_ANCHOR = "| **July 2026 — Synthesis pipeline fully resolved, live-verified (Session 42 lock reopened and re-set)**"
NEW_SECTION14_ENTRY = """| **July 2026 — /book go-live: 87 pieces published to Production** | Closes the publish decision open since Session 71's Decision Register seeding. Full lineage: a staged 4-batch publish sequence (Batch 1 evidentiary-anchor/22 cited pieces first, descending through Batch 4's 42-piece uncited FTA narrative corpus, sub-batched rather than dumped at once) was proposed for discussion, verified arithmetically clean against the manifest (zero duplicates, zero omissions, all 87 non-parked entries accounted for, two header-count labels caught and corrected). **Pete's decision: publish all 87 at once instead** -- the staged sequence is repurposed as the LinkedIn promotional posting order, decoupled entirely from site publish timing, not discarded. Two prerequisites closed first: the markdown-body rendering gap (commit 4402c24 -- react-markdown, no plugins, components mapped to the locked visual identity, position-based leading-H1 strip) and a re-confirmation that citation-free compliance and the shadow-model boundary were both still clean by direct read of the full corpus, not assumed from an earlier pass. **Bulk status flip** (commit a4aaf8f): all 87 `draft` entries in book-manifest.ts set to `published`; LIB-037 deliberately excluded, verified via exact string-count checks before and after write, not assumed from a visual diff alone. **Verified twice, not once:** on Preview before the commit, then independently again directly against `prv-3.vercel.app` Production after deploy -- both passes checked the same 4 pieces (one from each content type plus the corpus's only numbered-list file) and the /book index (exactly 87 entries listed, LIB-037 absent, "Coming soon." gone). Tier 4 named-risk categories and a pre-mortem were checked and logged before proceeding, per the CLAUDE.md Workflow Governance model -- full detail in Section 13a, which also now carries the closed Decision Register row. CLAUDE.md MOB version cross-reference updated v4.65->v4.66. MOB version bumped to v4.66 -- a Tier 4 irreversible public action going live warrants a bump per the closeout protocol. MOB v4.66. |
| **July 2026 — Synthesis pipeline fully resolved, live-verified (Session 42 lock reopened and re-set)**"""

edit("Section 14: prepend /book go-live entry", OLD_SECTION14_ANCHOR, NEW_SECTION14_ENTRY)

# ── 4. Section 16 Session Log: new entry appended at end of file ──────────────
OLD_LOG_TAIL = '''| **May 2026 — Session 1** | Taxonomy consolidation (108 to 47 states), name register audit, Liability Risk Framework, Leadership Competency Framework, Signal Map. All 47 states profiled. Four cluster identifiers confirmed. Eight root conditions named. MOB v1.0 created. |'''
NEW_LOG_ENTRY = '''| **July 2026 — /book go-live** | 87 non-parked /book pieces published to Production, LIB-037 remains parked. A staged 4-batch publish-sequence proposal (citation-weight-first ordering, arithmetically verified clean against the manifest) was superseded by Pete's decision to publish all 87 at once -- the staged sequence is repurposed as the LinkedIn promotional posting order instead, not discarded. Markdown-body rendering (commit 4402c24) and a re-confirmed citation/shadow-model compliance sweep closed as prerequisites first. Bulk status flip (commit a4aaf8f) verified via exact string counts before and after write, LIB-037 confirmed still parked. Verified twice: on Preview before commit, then independently again directly against `prv-3.vercel.app` Production after deploy -- same 4 sample pieces plus the /book index both times, identical results (87 entries listed, LIB-037 absent, "Coming soon." gone, all pieces rendering correctly). Tier 4 named-risk categories and a pre-mortem checked and logged before proceeding. Full detail in Section 14 and Section 13a. MOB v4.65->v4.66. |
| **May 2026 — Session 1** | Taxonomy consolidation (108 to 47 states), name register audit, Liability Risk Framework, Leadership Competency Framework, Signal Map. All 47 states profiled. Four cluster identifiers confirmed. Eight root conditions named. MOB v1.0 created. |'''

edit("Section 16: append /book go-live session-log entry at end of file", OLD_LOG_TAIL, NEW_LOG_ENTRY)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.print_help()
        sys.exit(1)

    if not TARGET.exists():
        print(f"ERROR: target not found: {TARGET}")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8")

    if args.dry_run:
        print(f"DRY RUN -- target: {TARGET}")
        print(f"  {len(CHANGES)} change(s) to apply:")
        all_ok = True
        for label, old, new in CHANGES:
            count = text.count(old)
            status = f"OK ({count}x)" if count == 1 else ("MISS" if count == 0 else f"AMBIGUOUS ({count}x)")
            if count != 1:
                all_ok = False
            print(f"  [{status}] {label}")
        if not all_ok:
            print("\n  ERROR: one or more OLD strings not found exactly once in target.")
            sys.exit(1)
        print("\n  All anchors matched exactly once. Ready for --write.")
        return

    for label, old, new in CHANGES:
        count = text.count(old)
        if count != 1:
            print(f"ERROR: OLD string for '{label}' matched {count} times (expected 1) -- aborting.")
            sys.exit(1)

    new_text = text
    for label, old, new in CHANGES:
        new_text = new_text.replace(old, new, 1)

    if new_text == text:
        print("ERROR: no changes produced.")
        sys.exit(1)

    TARGET.write_text(new_text, encoding="utf-8")
    print(f"WRITTEN: {TARGET}")
    print(f"  {len(CHANGES)} change(s) applied")


if __name__ == "__main__":
    main()
