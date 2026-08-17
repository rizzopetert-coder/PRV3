"""
PRV3 -- MOB update: new Decision Register row for the severity follow-on
state scoping gate, downgraded from "scoping/build in progress" to
"open design question, unresolved, real production defect still live."

Both gate designs tried this session (any-qualifying-state, top-1-only)
were tested against real engine traces and falsified in opposite
directions -- any-qualifying too permissive (21-42/58 states co-qualify
per session), top-1 too restrictive (strips legitimate triggers,
confirmed on 2 of 4 spot-checks). A follow-up per-state calibrated
threshold hypothesis was also tested and falsified more decisively --
5 of 6 sampled states share bit-for-bit identical scores with 3-6
unrelated states in the same session. Full detail:
prompts/severity-follow-on-gate-investigation-findings.md.

Working tree confirmed reverted -- no patch applied to engine/main.py
or engine/data/questions.py. The original defect (severity_trigger
firing with no per-state gating) remains live and unpatched in
production, unchanged from before this investigation began.

Version bump v4.179 -> v4.180: new Decision Register row material
enough to warrant a bump (a defect's status materially changed from
"fix in progress, Gemini-confirmed" to "open design question,
confirmed unresolved by two falsified designs"), not a session-log-only
change -- this is not a full session closeout, so Section 16 is not
touched here.

Usage:
  python tools/patch_mob_severity_gate_open_question.py --dry-run
  python tools/patch_mob_severity_gate_open_question.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB = "tools/_mob.txt"

ANCHOR = (
    '| Gemini fails to incorporate explicit, verbatim correction across review rounds -- Category D\'s instance CLOSED (round 3 clean); general pattern stays on record | N/A -- reviewer-behavior fact, not a Tier 1-4 workflow item | Category D instance: CLOSED -- round 3 confirmed clean, both constrained items answered (a) sound, no reinvention. General pattern: still tracked, informational, no code impact, all errors caught before build in every instance across all three rounds | N/A | Distinct from the ConstellationField file-path-citation pattern (same session, separate row) -- that pattern was the same WRONG FACT repeated verbatim across reviews. This pattern is different and arguably more serious: Category D\'s second review round restated TWO explicitly, verbatim-corrected errors from the first round, simultaneously, after being told directly not to repeat them. (1) The Gemini review package (prompts/category-d-gemini-review-package.md) stated in plain language that web/lib/output-renderer.ts\'s renderPrivateOutput() is confirmed dead code with zero callers and said outright "do not propose this function again," giving PrivateOutput.tsx as the real live target. Gemini\'s second-round Section 3 routed straight back through the same dead function -- the identical proposal, a third time across two review rounds on this one question. (2) The package quoted the real scoped financial mechanic verbatim (industry_wage x 0.50 to industry_wage x 0.75, per-departing-employee, headcount explicitly not involved) and stated the prior "Attritional Tax %" formula was fabricated and should not be built under any framing. Gemini\'s second-round Section 4 proposed a different formula -- "Baseline Payroll x 0.12 to 0.18" -- built on the same rejected headcount x wage x range shape, now also citing "Census SUSB firm size midpoints" as a source. Confirmed via direct search: Census SUSB IS real (it\'s the genuine source behind HEADCOUNT_MIDPOINTS elsewhere in engine/friction_tax.py) -- so this is not a fabricated data source the way "Attritional Tax %" was a fabricated concept, but a real source pulled into a formula shape that was already explicitly ruled out. A third, separate error confirmed in the same round: Section 1\'s question-count reasoning ("Q01-Q34 core + Q40-Q51 expansion, minus Q16/Q29 duplicate and Q37-Q39 converted splices") does not match real removal history -- only Q29 was removed (not Q16, which stays core), and it\'s Q45 (not Q37-39, the always-excluded Aptitude addenda) that was converted from core to a Q44-conditional splice. Recomputed directly against PHASE_1_QUESTION_SEQUENCE: real math is 31 (Q01-34 range) + 11 (Q40-51 range, Q45 excluded) = 42, not the path Gemini described. None of the three errors were built -- all caught in the standing verification pass before anything moved toward implementation. **ROUND 3, CLOSING CATEGORY D\'S INSTANCE:** prompts/category-d-gemini-review-round3-constrained.md deliberately narrowed the ask to exactly two already-fully-specified decisions (CondensedOutput.tsx as rendering target, the get_industry_wage() x 0.50/0.75 mechanic), explicit non-responsive criteria for anything resembling a new proposal. Response came back well-formed: both items confirmed (a) sound, zero reinvention, zero repeat of any prior fabrication -- first Category D round to actually engage with the constraint as given. One new claim required its own check before treating this as fully cleared: Gemini\'s Section 2 stated a null get_industry_wage() result "safely triggers Option B null rendering downstream." Verified false as stated, on two independent counts: (1) web/components/CondensedOutput.tsx does not exist yet -- it was only ever proposed, never built, so there is categorically no designed null-handling path on the consuming side for Gemini to have verified against; (2) "Option B" is real but belongs to a DIFFERENT field (friction_tax_estimate, per a doc comment in web/lib/types.ts) -- and even there it\'s unimplemented: PrivateOutput.tsx\'s own comment at Block 6 confirms the real live behavior for a null friction_tax_estimate is "render nothing," not the Option B placeholder text the type comment describes. Pattern-matched a real but inapplicable precedent onto an unbuilt path, not a fabrication from nothing but not a verified fact either. Logged as a real, small, non-blocking Phase 3 build item (prompts/category-d-build-scope.md open items), not grounds for reopening the round-3 architecture confirmation itself. **ROUND 4:** prompts/category-d-gemini-review-round4-severity-handling.md, same constrained format, one item -- confirm the condensed session store\'s proposed severity-trigger handling (consume only accumulated_vector, never read/act on severity_follow_on_id/severity_input, inert by deliberate omission). Confirmed sound, well-formed, no reinvention -- third consecutive round in this constrained format to hold. Unlike rounds 1-3, this response asserted no new fact about the codebase (agreement with already-verified reasoning, not a new claim), so nothing required independent re-verification against source this round. **All four Category D architecture questions now cleared: rendering target (round 3), financial mechanic (round 3), get_industry_wage() signature (round 3, reconfirmed), severity-trigger handling (round 4).** | This session (Claude Code), 2026-08-13 | Category D instance: closed, no further check-in on this feature. General pattern: no forced check-in -- informational, pattern-tracking only. Two confirmed instances now (ConstellationField path citations, Category D corrected-error restatement across rounds 1-2) suggest verification-before-build isn\'t optional per-review discipline for this reviewer, it\'s load-bearing every single time, including on already-corrected material. Round 3\'s clean result shows a sufficiently narrow, constrained prompt can recover engagement after two failed rounds -- worth reusing that pattern (confirm-or-reject only, explicit non-responsive criteria) if a comparable restatement failure recurs on a future feature, rather than a fresh open-ended review request |'
)

NEW_ROW = (
    '\n'
    '| Severity follow-on state scoping (SEVER-19 and 13 more) -- OPEN DESIGN QUESTION, real production defect still live, unpatched | 3 | **OPEN. Not a build in progress. Two gate designs tried and falsified against real engine data this session; no third design proposed. Working tree reverted, nothing committed to engine code.** | No known gate design closes the leak without breaking something else -- see the real-data findings themselves | Defect: `tools/test_aut_ps_01_q23_d_forced.py` (drives engine/main.py\'s real production functions, not the calibration harness) caught AUT-PS-01 (paper_shield) landing at Endemic instead of its locked Entrenched, because severity_trigger firing (engine/main.py:301) has zero per-state awareness -- purely a property of the answered option. A full-library scan found the identical shape in 13 more follow-on IDs beyond the original SEVER-19/Q33 finding (SEVER-02, 10, 17, 18, 20, 21, 22, 23, 24, 25, 27, 28, 29) -- nearly the entirety of this session\'s Bucket 2/3 severity-wiring effort. SEVERITY_FOLLOW_ON_INTENDED_STATES (which state(s) each of the 14 was actually authored for, sourced from each fix\'s own MOB session-log record) is authored and not in question -- full derivation in prompts/severity-follow-on-state-scoping-fix.md. **Gate design 1 (any-qualifying-state via apply_signal_floor().cleared_floor):** Gemini-confirmed as a narrow confirm-or-reject, then dry-run tested against real engine traces and falsified -- AUT-PS-01\'s own session had 21/58 states simultaneously clearing the signal floor including both paper_shield and invisible_influence_architecture at once; the_broken_compass\'s own natural session had 42/58 qualifying, including the_burned_credibility (one of SEVER-23/24\'s intended states), so the documented overshoot protection for the_broken_compass did not survive contact with real qualifying-state breadth. **Gate design 2 (top-1-only via rank_states()):** fixed AUT-PS-01 exactly (Entrenched/33.33) and precisely restored the_broken_compass\'s SEVER-23/24 protection (isolated the math: SEVER-13 alone, untouched by this fix, produces exactly Entrenched/33.33 -- the residual Endemic in the full trace is fully attributable to the separate, explicitly out-of-scope Q23/SEVER-05 issue). But 4 further spot-checks against each state\'s own natural, unforced answer path found top-1 strips legitimate triggers almost universally -- none of AUT-IA-01/ATT-UT-01/AUT-DN-01/ATT-BS-01 ranked themselves top-1 in their own real session, and two (ATT-UT-01, ATT-BS-01) landed one full tier short of their locked target (Entrenched instead of Endemic) because both of their own legitimately-intended triggers were stripped. **Diagnostic pass (31 rows, all 14 follow-on IDs\' intended states through their own natural best-case answer path):** rank spans 1 to 58 of 58, margin-from-top-1 spans 0.0000 to 0.3753 -- no global rank/score/margin cutoff separates legitimately-intended states from unrelated co-qualifiers, confirmed not assumed. **Follow-up per-state-threshold hypothesis, falsified more decisively:** sampled 6 states across the rank spectrum and inspected real neighbors at nearby rank positions in the same session -- 5 of 6 sampled states (built_to_fail, narrative_lock, heard_and_ignored, the_basement_standard, cultural_overtime) share BIT-FOR-BIT IDENTICAL SCD-WCS scores with 3-7 completely unrelated states simultaneously in that same session (e.g. narrative_lock at rank 8 tied exactly with 5 other unrelated states at 0.9544; heard_and_ignored at rank 19 tied exactly with 6 others at 0.9508). No threshold, global or per-state, can separate numerically identical values -- points to something structural in how SCD-WCS similarity resolves for this dimensional space, not a tunable-number problem. **Direct connection, not a coincidence:** this is the same underlying ranking-distribution behavior already on record as the primary-state/intended-target match rate (1/58 in real calibration data) Decision Register item (Session Priority Queue item 5, prompts/primary-state-target-match-finding.md) -- now quantified at much larger scale and tied to a real, live scoring-integrity defect rather than an output-display observation. Consistent explanation for why the calibration suite stayed byte-for-byte at 171/175 through every gate design tested: SCD_WCS_CLUSTER_WINDOW (0.35, the harness\'s own pass criterion) is far looser than SCD_WCS_MARGIN_GATE (0.05, what actually gates live output), so the harness structurally cannot detect this class of leak in either direction. Full investigation record: prompts/severity-follow-on-gate-investigation-findings.md. **Current state, explicit so it isn\'t mistaken for further along than it is:** working tree confirmed clean and reverted -- engine/main.py and engine/data/questions.py carry neither gate design. tools/patch_severity_follow_on_state_scoping.py exists on disk, uncommitted, currently encoding the top-1 design (the last one tested) -- investigation scaffolding, not a decision, not deleted in case it\'s a useful starting point later. **The defect itself remains live and unpatched in production today**, unchanged from before this investigation began -- severity_trigger firing has no per-state gating anywhere in engine/main.py. | This session (Claude Code), 2026-08-16 | Should be evaluated jointly with the primary-state/intended-target match rate item above, not independently -- very likely the same root cause wearing two names. Pete\'s call on whether/when to open a third design attempt; no forced check-in, but should not sit indefinitely given it\'s a live, unpatched scoring-integrity defect, not a cosmetic gap |'
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
        (MOB, "\\\\\\#\\\\\\# MOB v4.179", "\\\\\\#\\\\\\# MOB v4.180"),
        ("CLAUDE.md", "| MOB version | v4.179 |", "| MOB version | v4.180 |"),
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
