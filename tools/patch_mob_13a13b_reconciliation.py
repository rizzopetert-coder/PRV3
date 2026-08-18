"""
MOB update -- 13a/13b reconciliation pass (2026-08-18).

Closes 3 stale Priority Queue items (Category E Direction 1 Refinement incl.
gestalt addendum; Category D; /book/toc fuller vision -- all confirmed genuinely
shipped via git log + live-file checks, not inferred from prose). Rewrites
Section 13b wholesale per standing convention, folding in 5 newly-discovered
items (severity follow-on gate defect, primary-state/target match cross-ref,
exact-score-tie hypothesis, Service Expectations draft copy, no-ai-slop /book
Step-Back item) and correcting a mischaracterization of the severity follow-on
item's status ("ready for Gemini" -> confirmed still OPEN DESIGN QUESTION per
its own Section 13a row and findings doc). Adds one Section 16 backfill entry
for Category D's closure. Adds one Section 13a row flagging the Section 16
logging-gap finding (not backfilling it, per explicit scope limit). Adds one
Section 14 row closing a real cross-referencing gap for P-13 (locked
2026-08-16, present in Section 2's Governing Principles list, absent from
Section 14 until now).

Re-verified fresh before writing: MOB header confirmed v4.183 (line 9),
CLAUDE.md cross-reference confirmed v4.183 (line 183), Section 14's last row
confirmed ending "...Commit 29b4373. MOB v4.140. |" (line 1600), Section 13a's
last row confirmed the no-ai-slop audit row (line 1388), Section 13b's full
span confirmed lines 1405-1437, Section 16's last row confirmed the 2026-08-17
em-dash-cap closeout (line 2264).

Usage:
    python patch_mob_13a13b_reconciliation.py --dry-run
    python patch_mob_13a13b_reconciliation.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_PATH = Path("CLAUDE.md")

P13_ROW = (
    '| **August 2026 -- P-13 locked: structural complexity needs framing** | Cross-referencing gap '
    'closed, found during this session\'s 13a/13b reconciliation pass -- P-13 ("Structural complexity '
    'needs a \'how to read this\' affordance before or alongside it, not after -- unexplained taxonomy '
    'reads as gimmick, not rigor.") was locked 2026-08-16 (commit df307da) and correctly appears in '
    'Section 2\'s Governing Principles list, but had no corresponding Section 14 row -- a real gap '
    'against the standing closeout-protocol rule that new locked decisions appear in both places, not '
    'just flagged forward this time. Source: Pete\'s own framing that session -- "It cannot be '
    'overstated how turned off our clients will be if they explore this AI-generated site and only see '
    'a gimmicky taxonomy without context. The taxonomy may be the least important detail." First two '
    'applications, both shipped before the principle was formally named, retroactively confirmed as its '
    'precedent: the ConstellationField gestalt-interpretability addendum (Category E) and the '
    '/book/toc Gestalt Pass\'s Terminology Guide -- both independently built the same shape, a "what do '
    'these terms mean" affordance placed before or alongside the complex structural element itself, not '
    'after. MOB v4.184. |\n'
)

DECISION_REGISTER_GAP_ROW = (
    '| Section 16 (Session Log) logging gap, roughly MOB v4.150-v4.163 -- OPEN, flagged not backfilled '
    '| 3 | **OPEN. No work scheduled. Flagged as part of this session\'s 13a/13b reconciliation pass, '
    'not actioned beyond one targeted backfill (see Section 16).** | Backfill effort/priority is Pete\'s '
    'call, not urgent -- no defect results from the gap itself, only reduced session-log narrative '
    'continuity for that stretch | Section 16 has zero entries between the 2026-08-11 close (ending MOB '
    'v4.149) and the 2026-08-16 close (opening at MOB v4.164) -- an entire work arc shipped with no '
    'dedicated session-log entry: Category D\'s full build-through-close (v4.154-164), Category E '
    'Direction 1 Refinement\'s base build (v4.151), and the Direction 1 Refinement addendum\'s initial '
    'Gemini-prep (v4.170). Root cause of Section 13b\'s parallel staleness, discovered this pass: 13b '
    'was rewritten once mid-arc (v4.151, right after Direction 1 Refinement was opened but before it or '
    'Category D actually shipped) and never revisited for the rest of that stretch, closing 3 items '
    'that were genuinely done while still marked open or parked. One entry (Category D\'s closure) '
    'backfilled this session as a targeted fix, not a full repair -- the remaining gap (chiefly '
    'v4.150-163, plus whatever portion of v4.165-175 the 2026-08-16 closeout entry doesn\'t already '
    'cover) stays open. | This session (Claude Code), 2026-08-18 | Pete\'s call whether a fuller Section '
    '16 backfill is worth the effort versus leaving it as a known, bounded gap -- no forcing deadline, '
    're-raise if a future session needs the missing narrative context. |\n'
)

CATEGORY_D_BACKFILL_ROW = (
    '| 2026-08-13 -- Session log backfill: Category D (free condensed diagnostic) shipped and fully '
    'closed | Backfills a real Section 16 gap found during this session\'s 13a/13b reconciliation pass '
    '-- this work happened 2026-08-13 (MOB v4.155-164) but was never given its own session-log entry; '
    'Section 16 jumps directly from the 2026-08-11 close (v4.149) to the 2026-08-16 close (opening at '
    'v4.164). **Phase 3 full build (commit 5573bd4):** engine/friction_tax.py gained '
    'get_industry_wage(industry) -> Optional[float], a public accessor matching the file\'s existing '
    '.get()-returns-None-on-miss convention. engine/main.py gained run_condensed_engine(), a separate '
    'completion orchestrator that deliberately does not call assemble_output() -- found via a real '
    'crash during verification that assemble_output() unconditionally computes the full Friction Tax '
    'figure, which requires a numeric headcount Category D\'s industry-only intake doesn\'t collect; '
    'rebuilt to construct a minimal, self-contained result directly (rank_states + severity + '
    'resolution_family + get_fallback_synthesis()), skipping Friction Tax, legal exposure, narrative '
    'modulation, and every other full-diagnostic-only field. No live LLM call, Pete\'s locked decision '
    '-- a free/anonymous/ungated tool must not invoke a paid, timeout-exposed endpoint per submission. '
    'New /api/condensed-complete route; new web/lib/condensed-session-store.ts (separate session '
    'infrastructure from the full diagnostic\'s, fixed 9-question set, 5 of 9 carrying real severity '
    'triggers deliberately never read back -- inert by design, Gemini-confirmed sound); new condensed '
    'intake routes; new CondensedOutput.tsx (no ConstellationField, thin-signal/credibility-risk call; '
    'financial range omits entirely with an explicit unavailable note rather than a broken figure on a '
    'null industry match). Verification that session: tsc clean, tools/test_main.py 36/36, full '
    '172(+3)-profile regression 171/175 exact baseline zero movement, real end-to-end Python run '
    'confirmed working. **Two follow-on fixes same day:** a missing front door (/diagnostic/condensed '
    'page + flow, commit 106105c) and a vercel.json routing gap (commit b7ec5ac) both found and fixed; '
    'a verdict-text bug (falling back to fully generic copy, commit 6398e11) found and fixed. **Final '
    'closure (commit 642b14d):** Pete ran two independent live-production tests, different answer '
    'paths, different resulting states (the_untouchable, then the_fracture) -- both completed cleanly '
    'with correct resolution_family, real state-specific verdict text, and a correctly-computed '
    'financial_range (108110 x 0.50/0.75 against real BLS wage data), confirming both prior-round '
    'content bugs resolved against real data across two runs, not a single lucky reproduction. '
    'build-scope.md\'s Phase 4 marked complete. Category D confirmed genuinely shippable. Live in the '
    'repo today: web/app/diagnostic/condensed/, web/app/api/diagnostic/condensed/{start,answer}/, '
    'web/components/CondensedOutput.tsx -- reconfirmed present this session, not inferred from commit '
    'messages alone. MOB version bumped to v4.184 as part of this session\'s reconciliation pass -- '
    'closes 3 Priority Queue items (this one, /book/toc fuller vision, Category E Direction 1 '
    'Refinement, all confirmed shipped via git log + live-file checks), backfills this Section 16 '
    'entry, and fixes a real Section 14 cross-referencing gap (P-13), together warranting a bump per '
    'the closeout protocol. | This session (Claude Code), 2026-08-18 | MOB v4.184 |\n'
)

SCRATCH_DIR = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\9354bfe3-2f47-478f-ac95-6d59ebb8dbc1\scratchpad"
)
SECTION_13B_OLD = (SCRATCH_DIR / "section13b_raw.txt").read_text(encoding="utf-8")
SECTION_13B_NEW = (SCRATCH_DIR / "section13b_new.txt").read_text(encoding="utf-8")

REPLACEMENTS = [
    (
        CLAUDE_PATH,
        "CLAUDE.md MOB version cross-reference",
        "| MOB version | v4.183 |",
        "| MOB version | v4.184 |",
    ),
    (
        MOB_PATH,
        "append P-13 row at end of Section 14",
        'Commit 29b4373. MOB v4.140. |\n',
        'Commit 29b4373. MOB v4.140. |\n' + P13_ROW,
    ),
    (
        MOB_PATH,
        "append Section 16 logging-gap row at end of Section 13a",
        'Recommended: add as a third ~August 23 Quarterly Step-Back agenda item, alongside the '
        'visual-identity-philosophy question already queued. Status OPEN, no work started, pending '
        'Pete\'s direction on approach and priority. |\n',
        'Recommended: add as a third ~August 23 Quarterly Step-Back agenda item, alongside the '
        'visual-identity-philosophy question already queued. Status OPEN, no work started, pending '
        'Pete\'s direction on approach and priority. |\n' + DECISION_REGISTER_GAP_ROW,
    ),
    (
        MOB_PATH,
        "append Category D backfill row at end of Section 16",
        'Diary written (AAAK, topic no-ai-slop-book-remediation). Mine run at closeout. | This session '
        '(Claude Code) | MOB v4.183 |\n',
        'Diary written (AAAK, topic no-ai-slop-book-remediation). Mine run at closeout. | This session '
        '(Claude Code) | MOB v4.183 |\n' + CATEGORY_D_BACKFILL_ROW,
    ),
    (
        MOB_PATH,
        "wholesale rewrite of Section 13b",
        SECTION_13B_OLD,
        SECTION_13B_NEW.rstrip("\n"),
    ),
]


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    file_texts = {}
    for path, _label, _old, _new in REPLACEMENTS:
        if path not in file_texts:
            file_texts[path] = path.read_text(encoding="utf-8")

    for path, label, old, new in REPLACEMENTS:
        text = file_texts[path]
        count = text.count(old)
        if count != 1:
            raise SystemExit(
                f"ABORT [{label}] in {path}: expected exactly 1 match, found {count}"
            )
        file_texts[path] = text.replace(old, new, 1)

    # Header version bump: index-based, since the section-header line uses
    # escaped-hash markdown (\\\#\\\#) that isn't a safe plain-substring anchor
    # on its own (the bare string "MOB v4.183" also appears in body prose).
    mob_text = file_texts[MOB_PATH]
    mob_lines = mob_text.split("\n")
    header_idx = 8  # 0-indexed line 9
    assert mob_lines[header_idx].endswith("MOB v4.183"), (
        f"ABORT [header bump]: line 9 does not end with 'MOB v4.183': {mob_lines[header_idx]!r}"
    )
    mob_lines[header_idx] = mob_lines[header_idx].replace("v4.183", "v4.184")
    file_texts[MOB_PATH] = "\n".join(mob_lines)

    for path, new_text in file_texts.items():
        original = path.read_text(encoding="utf-8")
        if args.dry_run:
            print(f"\n{'=' * 80}\nDIFF: {path}\n{'=' * 80}")
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"{path} (before)",
                tofile=f"{path} (after)",
            )
            print("".join(diff))
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WROTE: {path}")

    if args.dry_run:
        print("\nDry run complete. No files written. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
