"""
PRV3 -- Session closeout, 2026-08-11. Two new Section 14 (Locked
Decisions Log) entries for the genuinely architectural decisions this
session (Section 14 covers engine/data-contract level locks, per
precedent -- Category E's presentation-layer work, thoroughly covered in
Section 13a, is deliberately not duplicated here, same precedent as
Category C's /book/toc work not getting its own Section 14 row). One new
Section 16 (Session Log) entry summarizing the full session. Version
bump v4.148 -> v4.149 -- new locked-decision entries, not a session-log-
only change.

Usage:
  python tools/patch_mob_session_close_2026_08_11.py --dry-run
  python tools/patch_mob_session_close_2026_08_11.py --write
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
# Section 14 -- two new locked-decision entries, appended after the
# Mechanism 1 deprecation row (the section's current last entry).
# ═══════════════════════════════════════════════════════════════════════

SEC14_ANCHOR = (
    "| **August 2026 — Mechanism 1 (Prior Probability Adjusters) deprecated, significant_events redefined as synthesis-only** | significant_events no longer feeds any scoring mechanism -- initialize_priors() (engine/accumulation.py) is now an unconditional flat baseline, regardless of intake. Real, user-submitted synthesis-only narrative metadata as of this session's Phase 2 (web intake collection, strict validation against 9 canonical event keys) and Phase 3 (synthesis prompt wiring, engine/output_synthesis.py). PRIOR_ADJUSTER_INDEX/PRIOR_ADJUSTERS kept in place, deprecated not deleted -- engine/data/validate.py's referential-integrity check against STATE_PROFILES still runs; its two now-irrelevant \"none\"-event checks were separately removed (Priority Queue item 7). Q03A/Q03A-D-FOLLOW/Q27A/Q31 (engine/data/questions.py) also kept in place, parked -- calibration-harness profiles still depend on them for scoring signal, confirmed before any deletion was even considered. Full detail across all three phases: Section 13a Decision Register. Commits 2b57084/78c966e/e9cedc8. MOB v4.129. |"
)

SEC14_NEW_ROWS = (
    '\n'
    '| **August 2026 — A5 + Structure 3 combined recalibration: core question count 44 -> 42** | Q29 removed from PHASE_1_QUESTION_SEQUENCE as a literal duplicate of Q16 -- its severity follow-on (SEVER-12) re-chained off SEVER-01 instead of a standalone core slot (same mechanism as the already-shipped SEVER-30 -> SEVER-31 chain), preserving ATT-DC-01\'s locked Endemic reachability with zero content loss. Q45 converted from core to a Q44-conditional splice (fires on B/C/D only); Q46 deliberately left untouched, its topical mismatch with Q44/Q45 later closed as resolved-by-decision, not a gap. MC_CENTROID_39 regenerated via Monte Carlo (N=1000, seed=42) against the real live 42-question sequence, rank_states() divisor updated 44.0 -> 42.0, harness_s27_autonomous_calibration.py reconvergence RESOLVED in 2 rounds (not an impasse) at 58/58 HC. Full 172(+3)-profile regression: 171/175, net +1 over baseline, zero regressions, verified via git-stash before/after comparison. Gemini\'s fabricated \"100% pass criterion\" stripped per standing instruction before evaluation; a second, real discrepancy (Structure 3\'s true scope -1 not the originally assumed -2/-3) also corrected before build. Full detail: Section 13a Decision Register. Commit c6104a7. MOB v4.138. |\n'
    '| **August 2026 — Q06 weighted_multi_select: answer wire contract widened to option_ids: string[]** | Q06 was genuinely authored as format="weighted_multi_select" in the data model ("Select all that apply") but the full stack -- get_question_copy()\'s wire payload, QuestionCopy, QuestionView\'s rendering, AnswerRequest/AccumulatePayload -- was single-option end to end; never built past the data model, not a stale report. New accumulate_answers() wrapper (engine/main.py) loops the unchanged accumulate_one_answer() once per selected option, threading accumulated_vector sequentially -- confirmed necessary, not hypothetical: Q06\'s A and D options independently carry severity_trigger=true (SEVER-27/SEVER-21), so a real multi-select answer can fire two severity follow-ons from one submission. Wire contract widened uniformly (every single-select caller now sends a 1-element array -- one code path, not a dual branch) across engine/main.py, api/engine.py, web/lib/engine-client.ts, web/lib/session-store.ts, web/app/api/diagnostic/session/answer/route.ts, web/components/DiagnosticFlow.tsx, plus tools/diagnostic_fast_forward.py and web/lib/session-store.test.ts kept in sync with the same live contract. Full detail: Section 13a Decision Register. Commit 29b4373. MOB v4.140. |\n'
)

edit(MOB, SEC14_ANCHOR, SEC14_ANCHOR + SEC14_NEW_ROWS)

# ═══════════════════════════════════════════════════════════════════════
# Section 16 -- one new session-summary entry.
# ═══════════════════════════════════════════════════════════════════════

# Short, unique tail anchor rather than the full ~6000-char entry --
# safer against transcription mismatches (the full entry contains a
# literal "−" escape-sequence text fragment, documenting a historical
# rendering bug, that doesn't survive round-tripping through a shell/
# Python string literal cleanly). Confirmed via direct grep against the
# live file before use, not assumed.
SEC16_ANCHOR = (
    'item 7 (PRIOR_ADJUSTER_INDEX validate.py checks) confirmed fully closed this session, not just the pre-session "contained half." | This session (Claude Code) | MOB v4.136 |'
)

SEC16_NEW_ROW = (
    '\n'
    '| 2026-08-11 -- Session close: A1/A2/A3 shipped, A5+Structure3 recalibration (N 44->42), diagnostic question audit tool, Category D/book-toc concept sketches, Category E Directions 1+3 shipped, ~15 commits pushed clean (4772cfc..454ba3e), MOB v4.136 -> v4.148 | Full detail throughout Section 13a Decision Register -- this entry is the chronological summary, not a duplicate. **A1 (4772cfc):** Q06 free-text "Other" elaboration for significant_events, full stack -- format added to the wire, PrivateIntakeEcho/ShareableIntakeEcho type split for a compile-time P-03 airgap rather than a runtime flag. Established the SEVER-01 -> SEVER-12 chain pattern later reused. **A5 + Structure 3 combined recalibration (c6104a7):** core question count 44 -> 42 -- full detail in the new Section 14 entry above and Section 13a. Gemini\'s fabricated "100% pass criterion" stripped (repeat instance of an already-logged pattern); Structure 3\'s true scope corrected from the assumed -2/-3 to the real -1 before build. New tools/diagnostic_question_audit.py (a8fd33c) built and run in the same arc -- reads QUESTION_LIBRARY and splice logic directly, no browser dependency, found SEVER-09 as a newly-discovered dead trigger (its only parent, Q27A, is itself unreachable) among 22 total unreachable questions; adopted as the standing method for future A6-style option-adequacy reviews. **A.2 + A.3 (29b4373):** Q06 multi-select checkbox UI plus session reset/look-back -- full detail in the new Section 14 entry above. Edit-and-replay (going back and changing a prior answer) explicitly parked as its own scoped item, truncate-and-replay approach already designed. **Category E Direction 1 (94f9226):** ConstellationField rendering-quality upgrade -- centroid-tracking radial gradient fill, per-axis feGaussianBlur vertex glow scaled to real dimension_summary weights, depth stacking, CSS-only recede/resolve motion upgrade (no Framer Motion, confirmed absent from package.json, Pete\'s explicit call). Two Gemini claims corrected before build: the OD-07 rollback (b8860b5) recolored ConstellationField, never unmounted it -- live mode was already actively wired to real data in production, better than Gemini\'s framing implied; the data-emphasis enum Gemini\'s motion snippet used ("primary"|"dimmed") doesn\'t exist anywhere in the codebase, real enum is "primary"|"secondary"|"receded". **Category E Direction 3 (454ba3e):** editorial/typographic hero cluster display. Read-only investigation ran FIRST, before any design lock -- 58 real high_confidence calibration profiles through the actual engine pipeline found 100% land in multi-state output mode, qualified-state count median 7 (max 32), and in 50% of profiles every qualified state rounds to the identical displayed percentage -- real numbers that killed the originally-scoped fixed 2/3-state tier and replaced it with a variable-length cluster (delta-weight bucket 0.08, capped at 5, "+N co-occurring conditions" overflow). Two more Gemini claims corrected: wrong PrivateOutput.tsx path (a nonexistent web/app/diagnostic/ location); web/lib/output-renderer.ts\'s renderPrivateOutput() confirmed to have zero callers anywhere -- dead scaffolding Gemini\'s Phase 1 plan would have patched with zero real effect, left completely untouched per Pete\'s instruction, bucketing logic built inline in PrivateOutput.tsx instead. Per-state percentages dropped from the cluster display (Pete-confirmed, reversible) -- showing near-identical numbers repeated up to 5 times was the exact symptom motivating the redesign. Edge cases verified against 3 real profiles (n=2/25/32) both in Python and by running the actual shipped buildCoreCluster() code in Node -- exact match, no crashes at either extreme. **Flagged, not built:** primary-state/intended-target match rate found to be 1/58 in the same real data pull -- contextualized against this project\'s long-locked cluster/top_3-not-rank-1 calibration philosophy and the gap between the calibration pass bar (0.35) and the live display\'s actual margin gate (0.05), not presented as an alarm; standalone investigation candidate, Pete\'s call. tools/diagnostic_fast_forward.py confirmed structurally unusable against current infrastructure -- its own _guard_not_production() correctly refuses the Production host, and no Preview environment exists to point it at instead; not a bug introduced this session, a real consequence of infrastructure that changed after the tool was built. **Concept sketches, no code (durable prompts/*.md files):** Category D (free condensed diagnostic, 8-10 core questions, truncated report shape), /book/toc\'s fuller vision (dimension/signature tag filters, resolution_family badges linking to services), and Category E\'s own full 3-direction spec (Directions 1 and 3 now shipped, Direction 2 -- four-dial instrument panel -- stays concept-level). Q46\'s topical-mismatch flag (carried from the A5+Structure3 row) separately closed as resolved-by-decision, not a gap -- chaining under Q45 was already declined, not left pending. **Verification discipline, held constant across every commit:** tsc --noEmit clean at every step; full 172(+3)-profile regression run and compared byte-for-byte against baseline at every engine/calibration-touching commit (zero unintended regressions, confirmed via git-stash before/after where needed, not assumed); the same pre-existing 6 session-store.test.ts failures (stale sequence-length assertions predating this session\'s own N=44->42 change) reconfirmed unrelated at every Category E commit, still not fixed, flagged as a real, separate gap worth its own pass. Live browser before/after verification for both Category E directions held for Pete via claude-in-chrome post-push -- no browser tool available in this Claude Code session, confirmed via fresh tool search before asking each time, not assumed from earlier context. **Pattern worth carrying forward, reconfirmed 5+ times this session alone:** verifying a Gemini architecture-review claim against real source before writing any diff caught a real, consequential error every single time it was applied this session (a fabricated pass criterion, two wrong file paths, one dead-code target function, one fabricated CSS enum value, one misleading rollback characterization) -- zero times was a Gemini claim taken on faith and turned out wrong once actually built. | This session (Claude Code) | MOB v4.149 |\n'
)

edit(MOB, SEC16_ANCHOR, SEC16_ANCHOR + SEC16_NEW_ROW)


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
        (MOB, "\\\\\\#\\\\\\# MOB v4.148", "\\\\\\#\\\\\\# MOB v4.149"),
        ("CLAUDE.md", "| MOB version | v4.148 |", "| MOB version | v4.149 |"),
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
