"""
PRV3 -- MOB update: new Decision Register row for the no-ai-slop DETECT
audit of the full 87-article /book corpus.

Confirmed ~438 findings across 87 published articles, zero clean files.
Most significant finding: a near-uniform structural template across the
majority of methodology pieces (hook paragraph, three bolded pseudo-
bullet diagnostic-sign sentences, aphoristic closing kicker, and in
many cases an identical "Question We Ask" CTA/signature closing block),
plus several literal verbatim sentence reuses across unrelated
articles. Full detail: prompts/no-ai-slop-book-audit-findings.md,
commit 6e42d36.

Flagged as directly connected to the already-queued visual-identity-
philosophy Quarterly Step-Back item -- same underlying "does this read
as professionally crafted or as AI-generated template" concern, now
with objective textual evidence rather than a subjective visual read.
Recommended as a third Step-Back agenda item. Status OPEN, no work
started, pending Pete's direction on approach and priority.

Version bump v4.181 -> v4.182: new Decision Register row, material
enough to warrant a bump per standing convention -- not a session-log-
only change.

Usage:
  python tools/patch_mob_no_ai_slop_decision_register.py --dry-run
  python tools/patch_mob_no_ai_slop_decision_register.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB = "tools/_mob.txt"
CLAUDE = "CLAUDE.md"

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


ANCHOR = (
    "| Severity follow-on state scoping (SEVER-19 and 13 more) -- OPEN DESIGN QUESTION, real production defect still live, unpatched | 3 | **OPEN. Not a build in progress. Two gate designs tried and falsified against real engine data this session; no third design proposed. Working tree reverted, nothing committed to engine code.** | No known gate design closes the leak without breaking something else -- see the real-data findings themselves | Defect: `tools/test_aut_ps_01_q23_d_forced.py` (drives engine/main.py's real production functions, not the calibration harness) caught AUT-PS-01 (paper_shield) landing at Endemic instead of its locked Entrenched, because severity_trigger firing (engine/main.py:301) has zero per-state awareness -- purely a property of the answered option. A full-library scan found the identical shape in 13 more follow-on IDs beyond the original SEVER-19/Q33 finding (SEVER-02, 10, 17, 18, 20, 21, 22, 23, 24, 25, 27, 28, 29) -- nearly the entirety of this session's Bucket 2/3 severity-wiring effort. SEVERITY_FOLLOW_ON_INTENDED_STATES (which state(s) each of the 14 was actually authored for, sourced from each fix's own MOB session-log record) is authored and not in question -- full derivation in prompts/severity-follow-on-state-scoping-fix.md. **Gate design 1 (any-qualifying-state via apply_signal_floor().cleared_floor):** Gemini-confirmed as a narrow confirm-or-reject, then dry-run tested against real engine traces and falsified -- AUT-PS-01's own session had 21/58 states simultaneously clearing the signal floor including both paper_shield and invisible_influence_architecture at once; the_broken_compass's own natural session had 42/58 qualifying, including the_burned_credibility (one of SEVER-23/24's intended states), so the documented overshoot protection for the_broken_compass did not survive contact with real qualifying-state breadth. **Gate design 2 (top-1-only via rank_states()):** fixed AUT-PS-01 exactly (Entrenched/33.33) and precisely restored the_broken_compass's SEVER-23/24 protection (isolated the math: SEVER-13 alone, untouched by this fix, produces exactly Entrenched/33.33 -- the residual Endemic in the full trace is fully attributable to the separate, explicitly out-of-scope Q23/SEVER-05 issue). But 4 further spot-checks against each state's own natural, unforced answer path found top-1 strips legitimate triggers almost universally -- none of AUT-IA-01/ATT-UT-01/AUT-DN-01/ATT-BS-01 ranked themselves top-1 in their own real session, and two (ATT-UT-01, ATT-BS-01) landed one full tier short of their locked target (Entrenched instead of Endemic) because both of their own legitimately-intended triggers were stripped. **Diagnostic pass (31 rows, all 14 follow-on IDs' intended states through their own natural best-case answer path):** rank spans 1 to 58 of 58, margin-from-top-1 spans 0.0000 to 0.3753 -- no global rank/score/margin cutoff separates legitimately-intended states from unrelated co-qualifiers, confirmed not assumed. **Follow-up per-state-threshold hypothesis, falsified more decisively:** sampled 6 states across the rank spectrum and inspected real neighbors at nearby rank positions in the same session -- 5 of 6 sampled states (built_to_fail, narrative_lock, heard_and_ignored, the_basement_standard, cultural_overtime) share BIT-FOR-BIT IDENTICAL SCD-WCS scores with 3-7 completely unrelated states simultaneously in that same session (e.g. narrative_lock at rank 8 tied exactly with 5 other unrelated states at 0.9544; heard_and_ignored at rank 19 tied exactly with 6 others at 0.9508). No threshold, global or per-state, can separate numerically identical values -- points to something structural in how SCD-WCS similarity resolves for this dimensional space, not a tunable-number problem. **Direct connection, not a coincidence:** this is the same underlying ranking-distribution behavior already on record as the primary-state/intended-target match rate (1/58 in real calibration data) Decision Register item (Session Priority Queue item 5, prompts/primary-state-target-match-finding.md) -- now quantified at much larger scale and tied to a real, live scoring-integrity defect rather than an output-display observation. Consistent explanation for why the calibration suite stayed byte-for-byte at 171/175 through every gate design tested: SCD_WCS_CLUSTER_WINDOW (0.35, the harness's own pass criterion) is far looser than SCD_WCS_MARGIN_GATE (0.05, what actually gates live output), so the harness structurally cannot detect this class of leak in either direction. Full investigation record: prompts/severity-follow-on-gate-investigation-findings.md. **Current state, explicit so it isn't mistaken for further along than it is:** working tree confirmed clean and reverted -- engine/main.py and engine/data/questions.py carry neither gate design. tools/patch_severity_follow_on_state_scoping.py exists on disk, uncommitted, currently encoding the top-1 design (the last one tested) -- investigation scaffolding, not a decision, not deleted in case it's a useful starting point later. **The defect itself remains live and unpatched in production today**, unchanged from before this investigation began -- severity_trigger firing has no per-state gating anywhere in engine/main.py. | This session (Claude Code), 2026-08-16 | Should be evaluated jointly with the primary-state/intended-target match rate item above, not independently -- very likely the same root cause wearing two names. Pete's call on whether/when to open a third design attempt; no forced check-in, but should not sit indefinitely given it's a live, unpatched scoring-integrity defect, not a cosmetic gap |"
)

NEW_ROW = (
    "\n"
    '| No-AI-slop DETECT audit of the full 87-article /book corpus -- OPEN, flagged for the Quarterly Step-Back, no work started | 3 | **OPEN. Investigation only, no content edited. Recommended as a third ~August 23 Quarterly Step-Back agenda item.** | Pete\'s direction needed on approach and priority -- no work scheduled | Full detail: prompts/no-ai-slop-book-audit-findings.md, commit 6e42d36. Every one of the 87 published /book articles was audited (confirmed via direct book-manifest.ts parse against the real status field, not assumed) using the newly-installed no-ai-slop skill\'s DETECT methodology, in 6 parallel batches. Result: **~438 findings, zero clean files.** Most significant finding is structural, not lexical -- the majority of the methodology-type pieces (the largest content type, roughly 58 of the 87) share what reads as one underlying template rather than independent authorship: a hook paragraph, a horizontal rule, a "diagnostic signs" section using exactly three bolded lead-sentence pseudo-bullets dressed as prose, in roughly half the files a "First/Second/Third" bolded fix-list using the identical device, a closing aphoristic "kicker" line, and in a subset an identical closing block ("## The Question We Ask" header, italicized diagnostic question, "If you\'re ready to ___, we should talk." CTA, "-- Principal Resolution" signature). Second-most dominant: the "X isn\'t Y. It\'s Z." binary-contrast construction, present in essentially every file, used repeatedly as a section heading rather than an occasional device. Third: near-universal em-dash clustering, several files exceeding the 3-per-piece threshold by a wide margin (two files at 19 each). Fourth: several sentences and framing devices reused near-verbatim across unrelated pieces, not just shared structure -- e.g. one sentence identical word-for-word between toxic-culture.md and silosolation.md, a closing aphorism ("Every organization has that window...") near-verbatim across 5 of 6 case_pattern files, an opening naming template ("[State] does not always look like X. Sometimes it looks like Y.") across the same set. /book/toc\'s own copy (143 entries, taxonomy.ts/book-state-index.ts/book-taxonomy-labels.ts/page.tsx SIGNATURE_DEFINITIONS/ConstellationField.tsx GESTALT_INFO) came back far cleaner -- 8 minor findings total, confirmed via the same methodology. **Directly connected to the visual-identity-philosophy open question already queued for the Quarterly Step-Back (row above the Priority Queue item 5 cross-reference, prompts/visual-identity-philosophy-open-question.md) -- same underlying "does this read as professionally crafted or as AI-generated template" concern Pete raised about the site\'s visual character, now with objective textual evidence at the article-copy layer rather than a subjective visual read.** Explicitly noted in the findings doc: tonight\'s earlier glossary-intersection candidate filter labels (prompts/book-toc-glossary-intersection-findings.md) remain provisional -- this audit doesn\'t retract them (their source corpus, /book/toc, came back mostly clean) but surfaces a much larger, separate problem that arguably needs addressing first, before treating new user-facing copy work as ready to build. | This session (Claude Code), 2026-08-16 | Recommended: add as a third ~August 23 Quarterly Step-Back agenda item, alongside the visual-identity-philosophy question already queued. Status OPEN, no work started, pending Pete\'s direction on approach and priority. |\n'
)

edit(MOB, ANCHOR, ANCHOR + NEW_ROW)
edit(MOB, "\\\\\\#\\\\\\# MOB v4.181", "\\\\\\#\\\\\\# MOB v4.182")
edit(CLAUDE, "| MOB version | v4.181 |", "| MOB version | v4.182 |")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    contents: dict[str, str] = {}
    for path, _, _ in EDITS:
        if path not in contents:
            contents[path] = (REPO_ROOT / path).read_text(encoding="utf-8")

    for i, (path, old, new) in enumerate(EDITS, 1):
        count = contents[path].count(old)
        if count != 1:
            print(f"ABORT: edit #{i} ({path}): expected exactly 1 match, found {count}")
            print(f"  anchor (first 150 chars): {old[:150]!r}")
            sys.exit(1)
        contents[path] = contents[path].replace(old, new, 1)

    if args.dry_run:
        print(f"=== {len(EDITS)} edit(s) across {len(contents)} file(s) would apply cleanly ===")
        print("\nDry run complete. Re-run with --write to apply.")
    else:
        for path, content in contents.items():
            (REPO_ROOT / path).write_text(content, encoding="utf-8")
        print(f"=== {len(EDITS)} edit(s) written across {len(contents)} file(s) ===")


if __name__ == "__main__":
    main()
