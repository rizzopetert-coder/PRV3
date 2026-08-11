"""
PRV3 -- MOB update: A5 + Structure 3 combined recalibration CLOSED.
Decision Register rows updated (both prior "parked" rows -- Structure 3
and the Q16/Q29 duplicate -- now closed, full outcome recorded), Priority
Queue item 2 closed out, stale "files to attach" pointer removed.

Version bump v4.137 -> v4.138: two Tier 3 items closed with real shipped
implementation, not a session-log-only change.

Usage:
  python tools/patch_mob_a5_structure3_closed.py --dry-run
  python tools/patch_mob_a5_structure3_closed.py --write
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
# Decision Register -- Structure 3 row -> CLOSED, full outcome.
# ═══════════════════════════════════════════════════════════════════════

edit(
    MOB,
    '| Structure 3 (diagnostic Q37/38/39 core-to-splice conversion) parked alongside A5 | 3 | Parked, not scheduled | Structure 3 (diagnostic Q37/38/39 core-to-splice conversion) parked alongside A5 (Q16/Q29 duplicate removal) -- both require the same MC_CENTROID-style recalibration effort (core question count change triggers engine/accumulation.py:539\'s scale = N / 44.0 coupling). Confirmed via Gemini architecture review + this session\'s own A5 regression test, not assumed. See prompts/diagnostic-usability-findings-2026-08-09.md, B-addendum-3, for full detail. Structures 1 and 2 (same review) cleared independently, no calibration risk, proceeding separately. | This session (Claude Code) | Not scheduled -- Pete to reopen alongside A5 when ready to commit to the recalibration effort |',
    '| A5 + Structure 3 combined recalibration -- CLOSED (N: 44 -> 42) | 3 | **Closed -- built, verified, net improvement, zero regression** | N/A | Gemini architecture review returned: CLEARED, combined single-pass recalibration. Fabricated pass criterion stripped per standing instruction -- Gemini\'s plan stated "100% pass across all HC profiles," the same "100% rank-1 / pytest" fabrication already caught and stripped twice during the original MC_CENTROID_39 arc and once during the Mechanism 1 review, confirmed a recurring pattern from this specific reviewer, not a one-off. Evaluated instead via Rule A (5% overall-suite floor) / Rule B (3-profile moderate/weak cap) through tools/harness_s27_autonomous_calibration.py, terminal state reported as-is. Both of Gemini\'s cited technical claims independently verified before writing any diff: constant name (still MC_CENTROID_39 -- the MC_CENTROID_LIVE rename Gemini once proposed was never signed off by Pete, not reopened) and centroid tooling (tools/diag_v21_accumulated_centroid.py confirmed real and current via git log, used in the original arc\'s actual regeneration commit d91e017 -- the "not committed" note traced to a stale untracked doc snapshot, not the live repo). TWO FURTHER DISCREPANCIES found beyond what was flagged, same verification discipline applied to Gemini\'s own summary: (1) "Q37/38/39" is display-position shorthand for real engine IDs Q44/Q45/Q46 (confirmed by counting PHASE_1_QUESTION_SEQUENCE) -- Q44 and Q45 share a state target (the_tolerated_violation) and read as a genuine sequential pair; Q46 targets a DIFFERENT state (the_arbitrary_standard) with zero topical continuity, already flagged unresolved in the prior B-addendum-3 record and NOT resolved here. Pete\'s explicit scope: Q44 stays core, only Q45 becomes a Q44-conditional splice (fires on B/C/D only -- Q44\'s "A" means "actively addressed," making Q45\'s question moot), Q46 left fully untouched pending its own future content redesign. Structure 3\'s real contribution is -1, not the task\'s originally assumed -2/-3. (2) A5 (Q29 removal) was not a clean deletion -- Q16 and Q29 are literal duplicate TEXT but not duplicate FUNCTION: Q16\'s B/C/D options trigger SEVER-01, Q29\'s B/C/D options trigger SEVER-12, and Q29 was SEVER-12\'s ONLY trigger anywhere in the codebase. tools/calibration_runner.py:410 has an explicit locked dependency: ATT-DC-01 needs BOTH SEVER-01 and SEVER-12 (each duration_band=18mo_plus) to reach its locked Endemic tier, either alone caps at Entrenched -- deleting Q29 outright would have silently broken this. Resolved per Pete\'s direct question ("why can\'t the function wired to Q29 get its input from Q16?"): SEVER-12 now chains off SEVER-01 unconditionally (all 5 options), same mechanism as the already-shipped SEVER-30 -> SEVER-31 chain (Structure 1) -- zero content loss, Q29 fully removable. Combined: 44 - 1 (Q29) - 1 (Q45) = **42**, not the task\'s original 40. HARNESS GAP found and fixed in the same pass: tools/calibration_runner.py\'s generate_answers() only ever simulated ONE level of severity-follow-on chaining -- Structure 1/2\'s SEVER-30/31/32 chains already shipped live but are exercised by zero calibration profiles (confirmed via grep of _SEVERITY_FOLLOW_ON_TARGETS), so this gap was latent until ATT-DC-01/SEVER-01->SEVER-12 became the first profile actually needing 2-deep chain simulation. Fixed by looping the follow-on block instead of a single `if`, bounded by the existing dedup set so it cannot run away -- same category as two previously-logged instances of the harness and live app silently diverging on shared splice logic (SEVER-11 double-splice dedup gap, Track A). BUILD: Step 1 (sequence/content wiring, engine/data/questions.py + web/lib/session-store.ts + web/app/api/diagnostic/session/answer/route.ts + tools/calibration_runner.py, dry-run validated 9/9 edits before write). Step 2 (centroid regenerated via the confirmed-real tools/diag_v21_accumulated_centroid.py, run directly against the live 42-question PHASE_1_QUESTION_SEQUENCE post-Step-1). Step 3 (engine/accumulation.py: new MC_CENTROID_39 values + rank_states() divisor 44.0 -> 42.0, dry-run validated 4/4 edits before write; CENTROID_FIELD_SCALARS values deliberately left untouched, only its adjacent comments corrected, per the same Step-3-scope convention as the original arc). Step 4 (tools/harness_s27_autonomous_calibration.py, warm-started from the live CENTROID_FIELD_SCALARS/SCD_WCS_CLUSTER_WINDOW): **RESOLVED in 2 rounds** -- 58/58 HC, a genuine resolution, not the original arc\'s IMPASSE. Step 5 (full regression): 171/175 overall, up from the 170/175 pre-change baseline. Delta verified via git-stash before/after comparison (not assumed) -- the ONLY change is transition_paralysis flipping from fail (2/3) to pass (3/3); the same 4 pre-existing gaps (identity_erosion, invisible_burnout, leadership_deafness, the_untouchable) are byte-for-byte untouched -- zero regressions. tsc --noEmit clean. All Python unit suites clean: test_main 36/36, test_accumulation 43/43, test_output 112/112, test_checkpoint 58/58, test_severity 56/56, test_resolution_families 84/84, test_output_synthesis 56/56, test_contract 140/140. engine/data/validate.py 40/41 -- the one failure is the same pre-existing, unrelated cluster_id gap (identical 5 states, confirmed). Held for Pete\'s explicit confirmation before commit/push per this task\'s own instruction (Tier 3 structural/calibration change touching live scoring math) -- confirmed, both discrepancy resolutions approved as built, no rework needed. | This session (Claude Code) | Closed -- no further check-in. Q46\'s topical-continuity mismatch with Q44/Q45 remains a separate, real, unresolved content item -- not reopened or fixed here, flagged for whenever Pete schedules that work |',
)

# ═══════════════════════════════════════════════════════════════════════
# Decision Register -- Q16/Q29 duplicate row -> CLOSED, pointer to the row
# above for full detail.
# ═══════════════════════════════════════════════════════════════════════

edit(
    MOB,
    '| Q16/Q29 duplicate question -- removal attempted and reverted, parked | 3 | Parked, not scheduled | Q16/Q29 duplicate question (confirmed 2026-08-09, prompts/diagnostic-usability-findings-2026-08-09.md Section A.5) -- removal attempted and reverted. Root cause: engine/accumulation.py:539\'s rank_states() hardcodes scale = N / 44.0, the same MC_CENTROID_39 question-count coupling that required a full Monte Carlo recalibration arc when Q40-51 was added (32->44). Removing Q29 (44->43) reproduces the identical problem in reverse -- regression confirmed: 170/175->163/175, 58/58->57/58 HC (ATT-UT-01/the_untouchable newly failing). Reverted cleanly, working tree back to true baseline, confirmed via git checkout. Needs its own scoped recalibration effort (Monte Carlo regen + CENTROID_FIELD_SCALARS reconvergence for N=43) before Q29 can be safely removed -- not a quick fix, comparable scope to the original MC_CENTROID_39 arc. Not scheduled -- Pete to reopen when ready to commit to that effort. Q16/Q29 duplicate remains live in the meantime -- known and logged, not silently present. | This session (Claude Code) | Not scheduled -- Pete to reopen when ready to commit to the recalibration effort |',
    '| Q16/Q29 duplicate question -- CLOSED, Q29 removed | 3 | **Closed -- Q29 removed, zero content loss** | N/A | Superseded by the combined A5 + Structure 3 recalibration row directly above -- full detail there (SEVER-12 re-chained off SEVER-01 before Q29\'s removal, preserving ATT-DC-01\'s locked Endemic reachability; N=44->42 regenerated and reconverged; 171/175 net result, zero regressions). This row kept as the historical record of the original attempted-and-reverted finding that first surfaced the engine/accumulation.py:539 N-count coupling for Q29 specifically. | This session (Claude Code) | Closed -- no further check-in |',
)

# ═══════════════════════════════════════════════════════════════════════
# Priority Queue -- item 2 closed out.
# ═══════════════════════════════════════════════════════════════════════

edit(
    MOB,
    '2. A5 (Q16/Q29 duplicate removal) + Structure 3 (diagnostic Q37/38/39 core-to-splice conversion) -- parked together, both blocked on the same landmine: engine/accumulation.py:539\'s `scale = N / 44.0` core-question-count coupling, confirmed via the A5 regression test (170/175->163/175, 58/58->57/58 HC) and Gemini architecture review. Needs a dedicated MC_CENTROID-style recalibration effort (Monte Carlo regen + CENTROID_FIELD_SCALARS reconvergence) before either can proceed -- not a quick fix, comparable scope to the original MC_CENTROID_39 arc. Not scheduled -- Pete to reopen when ready to commit to that effort.',
    '2. CLOSED (this session) -- A5 + Structure 3 combined recalibration shipped, N: 44 -> 42, 171/175 (net +1, zero regressions), 58/58 HC RESOLVED. Full detail in Decision Register (Section 13a). Nothing left parked -- both original items fully shipped.',
)

edit(
    MOB,
    '- If picking up the A5/Structure 3 recalibration effort: engine/accumulation.py, tools/harness_s27_autonomous_calibration.py, tools/calibration_runner.py (same files as any MC_CENTROID-style effort).\n',
    '',
)

# ═══════════════════════════════════════════════════════════════════════
# Version bump.
# ═══════════════════════════════════════════════════════════════════════

edit(
    MOB,
    "\\\\\\#\\\\\\# MOB v4.137",
    "\\\\\\#\\\\\\# MOB v4.138",
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
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
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
