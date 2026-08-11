"""
PRV3 -- A5 + Structure 3 combined recalibration, Step 1 (sequence & content
wiring). Gemini architecture review: CLEARED, combined single-pass
recalibration. N: 44 -> 42.

Corrections to the task as originally relayed, found via direct
verification before writing any diff (same "verify before adopting"
discipline the task itself invoked re: the fabricated 100% pass criterion):

1. Structure 3's actual scope, per the existing committed record
   (prompts/diagnostic-usability-findings-2026-08-09.md, B-addendum-3) and
   direct content inspection: "Q37/38/39" is DISPLAY-position shorthand for
   real engine IDs Q44/Q45/Q46 (confirmed by counting PHASE_1_QUESTION_
   SEQUENCE). Q44 and Q45 both target the_tolerated_violation and read as
   a genuine sequential pair; Q46 targets a DIFFERENT state
   (the_arbitrary_standard) with no topical continuity to Q44/Q45 -- this
   was already flagged unresolved in the existing record and is NOT
   resolved here. Pete's explicit call: Q44 stays core, only Q45 becomes a
   conditional splice off it, Q46 stays untouched. This makes Structure
   3's contribution -1 (not the task's assumed -2 or -3).

2. A5 (Q29 removal) is not a clean deletion. Q16 and Q29 are literal
   duplicate TEXT but not duplicate FUNCTION: Q16's B/C/D options trigger
   SEVER-01, Q29's B/C/D options trigger SEVER-12 -- two different
   questions, and Q29 is SEVER-12's ONLY trigger anywhere in the
   codebase. tools/calibration_runner.py:410 has an explicit locked
   dependency: ATT-DC-01 needs BOTH SEVER-01 and SEVER-12 (each at
   duration_band=18mo_plus) to reach its locked Endemic tier -- either
   alone caps at Entrenched. Deleting Q29 outright would silently break
   this. Resolution (Pete-confirmed): chain SEVER-12 off SEVER-01 instead
   (same mechanism as the already-shipped SEVER-30 -> SEVER-31 chain,
   Structure 1) -- unconditional across all 5 of SEVER-01's options,
   matching Q16/Q29's current always-fires-together behavior. Q29 is then
   fully removable with zero content loss.

Combined: 44 - 1 (Q29) - 1 (Q45) = 42.

Harness gap found and fixed in the same pass: tools/calibration_runner.py's
generate_answers() only ever simulated ONE level of severity-follow-on
chaining (core question -> one follow-on), never checking whether that
follow-on's own chosen option chains further. Structure 1/2's SEVER-30/31/
32 chains already shipped live but are exercised by zero calibration
profiles (confirmed via grep of _SEVERITY_FOLLOW_ON_TARGETS), so this gap
was latent. ATT-DC-01/SEVER-01->SEVER-12 is the first profile that
actually needs 2-deep chain simulation -- fixed here by looping the
follow-on block instead of a single `if`, bounded by the existing dedup
set (already_spliced_followons), so it cannot run away. Same category as
two previously-logged instances of the harness and live app silently
diverging on shared splice logic (SEVER-11 double-splice dedup gap, Track
A this session).

Usage:
  python tools/patch_a5_structure3_step1_sequence.py --dry-run
  python tools/patch_a5_structure3_step1_sequence.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


QUESTIONS = "engine/data/questions.py"
STORE = "web/lib/session-store.ts"
ANSWER_ROUTE = "web/app/api/diagnostic/session/answer/route.ts"
RUNNER = "tools/calibration_runner.py"

# ═══════════════════════════════════════════════════════════════════════
# engine/data/questions.py -- Q29 removed (4 locations); SEVER-01's 5
# options wired to chain to SEVER-12 (question-level severity_trigger
# flipped True to match).
# ═══════════════════════════════════════════════════════════════════════

# 1. Main _QDATA tuple.
edit(
    QUESTIONS,
    '    (\n'
    '        "Q29",\n'
    '        "How would you describe the relationship between diversity and advancement"\n'
    '        " in your organization?",\n'
    '        "forced_choice", 29, "late",\n'
    '        [\n'
    '            ("A", "Consistent — diverse talent advances at the same rate as everyone else.", False, None),\n'
    '            ("B", "We\'re diverse at entry levels but the composition changes as you move up.", True, "SEVER-12"),\n'
    '            ("C", "We\'ve invested in diversity but I\'m not sure it\'s translating into advancement.", True, "SEVER-12"),\n'
    '            ("D", "We\'re losing diverse talent before they reach senior levels and I\'m not sure why.", True, "SEVER-12"),\n'
    '            ("E", "This isn\'t something we\'ve looked at closely enough to answer with confidence.", False, None),\n'
    '        ],\n'
    '        ["the_diversity_ceiling"],\n'
    '        True,\n'
    '    ),\n',
    '    # Q29 REMOVED (A5 + Structure 3 combined recalibration, this session,\n'
    '    # N: 44 -> 42) -- was a literal duplicate of Q16\'s question text.\n'
    '    # Its severity_follow_on (SEVER-12) now chains off SEVER-01 instead\n'
    '    # of firing from its own standalone core slot -- see SEVER-01\'s\n'
    '    # entry below. Zero content loss: SEVER-12 stays reachable,\n'
    '    # ATT-DC-01\'s locked Endemic tier (needs both SEVER-01 and\n'
    '    # SEVER-12) is preserved.\n',
)

# 2. Seed dimensional-contribution dict entry.
edit(
    QUESTIONS,
    '        "Q29":           {"attitude_liability": 0.40, "authority_liability": 0.40},\n',
    '',
)

# 3. Per-option dimensional-contribution override dict entry.
edit(
    QUESTIONS,
    '        "Q29": {  # Attitude MED (diversity_ceiling). Authority partial drain v15.\n'
    '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
    '            "B": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
    '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
    '            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
    '            "E": {**_z, "attitude_liability": 0.25},                    # A\n'
    '        },\n',
    '',
)

# 4. Observation-text tag dict entry.
edit(
    QUESTIONS,
    '        "Q29": {\n'
    '            "B": "This organization is diverse at entry levels, but that changes as people move up.",\n'
    '            "C": "This organization has invested in diversity, but it\'s not clear that\'s translating into advancement.",\n'
    '            "D": "This organization is losing diverse talent before it reaches senior levels, and the reason isn\'t clear.",\n'
    '            "E": "This isn\'t something this organization has looked at closely enough to answer with confidence.",\n'
    '        },\n',
    '',
)

# 5. SEVER-01 -- wire all 5 options to chain to SEVER-12 (unconditional,
#    matching Q16/Q29's current always-fires-together behavior); flip the
#    question-level severity_trigger rollup True to match (was False,
#    correctly reflecting zero severity-trigger options before this).
edit(
    QUESTIONS,
    '    (\n'
    '        "SEVER-01",\n'
    '        "Is this something leadership has named and addressed, or is it more of a recognized"\n'
    '        " pattern that hasn\'t been tackled directly?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "Named and actively addressed — we have a specific plan and owners.", False, None),\n'
    '            ("B", "Named but not yet addressed — we know it\'s there but haven\'t moved on it.", False, None),\n'
    '            ("C", "Recognized informally but not officially named.", False, None),\n'
    '            ("D", "I\'m not sure leadership has seen it the same way I\'m describing it.", False, None),\n'
    '            ("E", "It\'s been recognized in some form for years without real traction.", False, None),\n'
    '        ],\n'
    '        ["the_diversity_ceiling"],\n'
    '        False,\n'
    '    ),\n',
    '    # A5 + Structure 3 combined recalibration, this session -- SEVER-01\n'
    '    # now chains to SEVER-12 unconditionally (all 5 options), same\n'
    '    # mechanism as the already-shipped SEVER-30 -> SEVER-31 chain\n'
    '    # (Structure 1). Replaces Q29\'s removed standalone core slot as\n'
    '    # SEVER-12\'s trigger -- preserves ATT-DC-01\'s locked Endemic path\n'
    '    # (needs both SEVER-01 and SEVER-12 at duration_band=18mo_plus).\n'
    '    (\n'
    '        "SEVER-01",\n'
    '        "Is this something leadership has named and addressed, or is it more of a recognized"\n'
    '        " pattern that hasn\'t been tackled directly?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "Named and actively addressed — we have a specific plan and owners.", True, "SEVER-12"),\n'
    '            ("B", "Named but not yet addressed — we know it\'s there but haven\'t moved on it.", True, "SEVER-12"),\n'
    '            ("C", "Recognized informally but not officially named.", True, "SEVER-12"),\n'
    '            ("D", "I\'m not sure leadership has seen it the same way I\'m describing it.", True, "SEVER-12"),\n'
    '            ("E", "It\'s been recognized in some form for years without real traction.", True, "SEVER-12"),\n'
    '        ],\n'
    '        ["the_diversity_ceiling"],\n'
    '        True,\n'
    '    ),\n',
)

# ═══════════════════════════════════════════════════════════════════════
# web/lib/session-store.ts -- Q29 and Q45 removed from
# PHASE_1_QUESTION_SEQUENCE (44 -> 42).
# ═══════════════════════════════════════════════════════════════════════

edit(
    STORE,
    '  "Q21", "Q22", "Q23", "Q24", "Q25", "Q26", "Q27B", "Q29", "Q30",',
    '  "Q21", "Q22", "Q23", "Q24", "Q25", "Q26", "Q27B", "Q30",',
)

edit(
    STORE,
    '  "Q40", "Q41", "Q42", "Q43", "Q44", "Q45", "Q46", "Q47", "Q48", "Q49",\n'
    '  "Q50", "Q51",\n'
    '];',
    '  "Q40", "Q41", "Q42", "Q43", "Q44", "Q46", "Q47", "Q48", "Q49",\n'
    '  "Q50", "Q51",\n'
    '  // A5 + Structure 3 combined recalibration (N: 44 -> 42), this session --\n'
    '  // Q29 removed (literal duplicate of Q16; its severity_follow_on\n'
    '  // (SEVER-12) now chains off SEVER-01 instead, same pattern as\n'
    '  // SEVER-30 -> SEVER-31). Q45 converted from core to a Q44-conditional\n'
    '  // splice (fires only when Q44\'s answer is B/C/D, mirroring Q06 -> Q28,\n'
    '  // see session/answer/route.ts). Q46 deliberately untouched -- confirmed\n'
    '  // no topical continuity with Q44/Q45 (different state target); its own\n'
    '  // content redesign is a separate future item.\n'
    '];',
)

# ═══════════════════════════════════════════════════════════════════════
# web/app/api/diagnostic/session/answer/route.ts -- Q44 -> Q45 conditional
# splice, same shape as the existing Q06 -> Q28 block immediately above it.
# ═══════════════════════════════════════════════════════════════════════

edit(
    ANSWER_ROUTE,
    '  if (question_id === "Q06" && (option_id === "A" || option_id === "B")) {\n'
    '    session.question_sequence = spliceDistinguishers(\n'
    '      session.question_sequence,\n'
    '      currentIndex,\n'
    '      ["Q28"],\n'
    '    );\n'
    '    session.question_labels["Q28"] = spliceLabel("Q06", 0, session.question_labels);\n'
    '  }\n',
    '  if (question_id === "Q06" && (option_id === "A" || option_id === "B")) {\n'
    '    session.question_sequence = spliceDistinguishers(\n'
    '      session.question_sequence,\n'
    '      currentIndex,\n'
    '      ["Q28"],\n'
    '    );\n'
    '    session.question_labels["Q28"] = spliceLabel("Q06", 0, session.question_labels);\n'
    '  }\n'
    '\n'
    '  // Q45 conditional splice (A5 + Structure 3 combined recalibration,\n'
    '  // this session) -- same shape as Q06 -> Q28 above. Q44\'s "A" option\n'
    '  // means "actively addressed by people with the authority to fix it,"\n'
    '  // which makes Q45\'s question ("what\'s the honest reason this hasn\'t\n'
    '  // been addressed?") not applicable -- so the splice fires on B/C/D\n'
    '  // only, not unconditionally. Q45 itself carries no severity_trigger\n'
    '  // of its own.\n'
    '  if (question_id === "Q44" && (option_id === "B" || option_id === "C" || option_id === "D")) {\n'
    '    session.question_sequence = spliceDistinguishers(\n'
    '      session.question_sequence,\n'
    '      currentIndex,\n'
    '      ["Q45"],\n'
    '    );\n'
    '    session.question_labels["Q45"] = spliceLabel("Q44", 0, session.question_labels);\n'
    '  }\n',
)

# ═══════════════════════════════════════════════════════════════════════
# tools/calibration_runner.py -- generate_answers() rewrite: Q45 excluded
# from unconditional iteration, answered conditionally right after Q44
# (mirroring the live splice); severity-follow-on block loop-ified to
# support the new SEVER-01 -> SEVER-12 chain (and any future chain).
# ═══════════════════════════════════════════════════════════════════════

edit(
    RUNNER,
    '    Handles Q03A/Q03B and Q27A/Q27B conditional pairs from intake.\n'
    '    """\n'
    '    from engine.test_suite import TestAnswer\n'
    '    events = test_case.intake.get("significant_events", ["none"])\n'
    '    has_acq = "acquisition_or_merger" in events\n'
    '    include = {\n'
    '        "Q03A" if events != ["none"] else "Q03B",\n'
    '        "Q27A" if has_acq else "Q27B",\n'
    '    }\n'
    '\n'
    '    answers = []\n'
    '    # Dedup guard, mirroring the real live app\'s severityFollowOnAlreadyAsked()\n'
    '    # (web/lib/session-store.ts) -- a follow-on with multiple real parent\n'
    '    # questions (SEVER-11 via Q28 and Q31, the "dual-parent" case that\n'
    '    # module\'s own header comment already documents) must only ever be\n'
    '    # spliced in once per session. Without this, a later core question\n'
    '    # that also fires an already-spliced follow-on would double-count its\n'
    '    # raw contribution -- confirmed as a real, latent bug via the Track A\n'
    '    # regression check (AUT-UP-01/02/03 overshot to Endemic instead of\n'
    '    # their locked Entrenched, SEVER-11 fired twice, raw summed to 4.00\n'
    '    # instead of the correct single-count 2.00).\n'
    '    already_spliced_followons = set()\n'
    '    for qid in sorted(_CORE_QUESTION_IDS):\n'
    '        excluded = any(\n'
    '            (qid == a and a not in include) or (qid == b and b not in include)\n'
    '            for a, b in _CONDITIONAL_PAIRS.items()\n'
    '        )\n'
    '        if excluded:\n'
    '            continue\n'
    '        q = QUESTION_LIBRARY.get(qid)\n'
    '        if q is None or not q.answer_options:\n'
    '            continue\n'
    '        strategy = test_case.profile_type\n'
    '        if strategy in ("high_confidence", "extreme_high_confidence"):\n'
    '            opt = (best_option_for_state(q, test_case.target_state)\n'
    '                   if test_case.target_state in (q.state_targets or [])\n'
    '                   else _neutral_option(q))\n'
    '        elif strategy == "moderate":\n'
    '            opt = (best_option_for_state(q, test_case.target_state)\n'
    '                   if test_case.target_state in (q.state_targets or [])\n'
    '                   else _neutral_option(q))\n'
    '        else:\n'
    '            # "weak" -- weighted-damping redesign, this session. Wired\n'
    '            # questions get real full-strength signal (same as moderate/\n'
    '            # high_confidence); unwired questions keep the Session 70 damped\n'
    '            # dimension-level signal but at a further down-weighted threshold,\n'
    '            # rather than the reverted hard-gate attempt\'s zeroed _neutral_option().\n'
    '            if test_case.target_state in (q.state_targets or []):\n'
    '                opt = best_option_for_state(q, test_case.target_state)\n'
    '            else:\n'
    '                opt = _damped_weak_option(\n'
    '                    q, test_case.target_state,\n'
    '                    threshold=WEAK_DAMPED_THRESHOLD * WEAK_UNWIRED_DAMPING_FACTOR,\n'
    '                )\n'
    '        answers.append(TestAnswer(question_id=qid, selected_option_ids=[opt.option_id]))\n'
    '\n'
    '        # Severity follow-on simulation -- opt-in only, via\n'
    '        # _SEVERITY_FOLLOW_ON_TARGETS. A test_id absent from that table\n'
    '        # (168 of 172 profiles) produces byte-for-byte identical answers to\n'
    '        # before this build -- no follow-on ever gets spliced in for them.\n'
    '        if (\n'
    '            opt.severity_trigger\n'
    '            and opt.severity_follow_on_id\n'
    '            and opt.severity_follow_on_id not in already_spliced_followons\n'
    '        ):\n'
    '            target_value = _SEVERITY_FOLLOW_ON_TARGETS.get(test_case.test_id, {}).get(\n'
    '                opt.severity_follow_on_id\n'
    '            )\n'
    '            if target_value is not None:\n'
    '                follow_on_q = QUESTION_LIBRARY[opt.severity_follow_on_id]\n'
    '                follow_on_opt = select_severity_follow_on_option(follow_on_q, target_value)\n'
    '                answers.append(TestAnswer(\n'
    '                    question_id=opt.severity_follow_on_id,\n'
    '                    selected_option_ids=[follow_on_opt.option_id],\n'
    '                ))\n'
    '                already_spliced_followons.add(opt.severity_follow_on_id)\n'
    '    return answers\n',
    '    Handles Q03A/Q03B and Q27A/Q27B conditional pairs from intake.\n'
    '\n'
    '    A5 + Structure 3 combined recalibration (this session): Q45 is\n'
    '    excluded from the unconditional core loop below and answered\n'
    '    conditionally right after Q44 instead, mirroring the live app\'s\n'
    '    Q44 -> Q45 splice exactly (session/answer/route.ts). The severity\n'
    '    follow-on block is looped rather than a single check, to support\n'
    '    SEVER-01 -> SEVER-12 (replacing Q29\'s removed standalone slot) and\n'
    '    any future chain -- bounded by the existing dedup set, so it cannot\n'
    '    run away.\n'
    '    """\n'
    '    from engine.test_suite import TestAnswer\n'
    '    events = test_case.intake.get("significant_events", ["none"])\n'
    '    has_acq = "acquisition_or_merger" in events\n'
    '    include = {\n'
    '        "Q03A" if events != ["none"] else "Q03B",\n'
    '        "Q27A" if has_acq else "Q27B",\n'
    '    }\n'
    '\n'
    '    def pick_option(q):\n'
    '        strategy = test_case.profile_type\n'
    '        if strategy in ("high_confidence", "extreme_high_confidence", "moderate"):\n'
    '            return (best_option_for_state(q, test_case.target_state)\n'
    '                    if test_case.target_state in (q.state_targets or [])\n'
    '                    else _neutral_option(q))\n'
    '        # "weak" -- weighted-damping redesign, Session 70/71. Wired\n'
    '        # questions get real full-strength signal (same as moderate/\n'
    '        # high_confidence); unwired questions keep the damped\n'
    '        # dimension-level signal at a further down-weighted threshold,\n'
    '        # rather than a zeroed _neutral_option().\n'
    '        if test_case.target_state in (q.state_targets or []):\n'
    '            return best_option_for_state(q, test_case.target_state)\n'
    '        return _damped_weak_option(\n'
    '            q, test_case.target_state,\n'
    '            threshold=WEAK_DAMPED_THRESHOLD * WEAK_UNWIRED_DAMPING_FACTOR,\n'
    '        )\n'
    '\n'
    '    answers = []\n'
    '    # Dedup guard, mirroring the real live app\'s severityFollowOnAlreadyAsked()\n'
    '    # (web/lib/session-store.ts) -- a follow-on with multiple real parent\n'
    '    # questions (SEVER-11 via Q28 and Q31, the "dual-parent" case that\n'
    '    # module\'s own header comment already documents) must only ever be\n'
    '    # spliced in once per session. Without this, a later core question\n'
    '    # that also fires an already-spliced follow-on would double-count its\n'
    '    # raw contribution -- confirmed as a real, latent bug via the Track A\n'
    '    # regression check (AUT-UP-01/02/03 overshot to Endemic instead of\n'
    '    # their locked Entrenched, SEVER-11 fired twice, raw summed to 4.00\n'
    '    # instead of the correct single-count 2.00).\n'
    '    already_spliced_followons = set()\n'
    '    for qid in sorted(_CORE_QUESTION_IDS):\n'
    '        excluded = any(\n'
    '            (qid == a and a not in include) or (qid == b and b not in include)\n'
    '            for a, b in _CONDITIONAL_PAIRS.items()\n'
    '        )\n'
    '        if excluded:\n'
    '            continue\n'
    '        # Q45 (A5 + Structure 3, this session): converted from an\n'
    '        # unconditional core question to a Q44-conditional splice.\n'
    '        # _CORE_QUESTION_IDS still lists it (derived from the full\n'
    '        # QUESTION_LIBRARY, not the live sequence -- same reason it\n'
    '        # also still lists Q28/Q31/Q35-39), so it must be explicitly\n'
    '        # skipped here or it would be double-answered against the new\n'
    '        # N=42 divisor.\n'
    '        if qid == "Q45":\n'
    '            continue\n'
    '        q = QUESTION_LIBRARY.get(qid)\n'
    '        if q is None or not q.answer_options:\n'
    '            continue\n'
    '        opt = pick_option(q)\n'
    '        answers.append(TestAnswer(question_id=qid, selected_option_ids=[opt.option_id]))\n'
    '\n'
    '        # Q45 conditional splice, mirroring the live app\'s Q44 -> Q45\n'
    '        # rule exactly (B/C/D only -- Q44\'s "A" means "actively\n'
    '        # addressed," making Q45\'s question moot).\n'
    '        if qid == "Q44" and opt.option_id in ("B", "C", "D"):\n'
    '            q45 = QUESTION_LIBRARY["Q45"]\n'
    '            opt45 = pick_option(q45)\n'
    '            answers.append(TestAnswer(question_id="Q45", selected_option_ids=[opt45.option_id]))\n'
    '\n'
    '        # Severity follow-on simulation -- opt-in only, via\n'
    '        # _SEVERITY_FOLLOW_ON_TARGETS. A test_id absent from that table\n'
    '        # produces byte-for-byte identical answers to before this build --\n'
    '        # no follow-on ever gets spliced in for them. Looped (not a\n'
    '        # single `if`) since SEVER-01 -> SEVER-12 (A5, this session) is\n'
    '        # this harness\'s first real 2-deep chain requirement --\n'
    '        # Structure 1/2\'s SEVER-30 -> SEVER-31/SEVER-32 chains exist\n'
    '        # live but no calibration profile currently exercises them, so\n'
    '        # this gap was latent until now.\n'
    '        current_opt = opt\n'
    '        while (\n'
    '            current_opt.severity_trigger\n'
    '            and current_opt.severity_follow_on_id\n'
    '            and current_opt.severity_follow_on_id not in already_spliced_followons\n'
    '        ):\n'
    '            follow_on_id = current_opt.severity_follow_on_id\n'
    '            target_value = _SEVERITY_FOLLOW_ON_TARGETS.get(test_case.test_id, {}).get(\n'
    '                follow_on_id\n'
    '            )\n'
    '            if target_value is None:\n'
    '                break\n'
    '            follow_on_q = QUESTION_LIBRARY[follow_on_id]\n'
    '            follow_on_opt = select_severity_follow_on_option(follow_on_q, target_value)\n'
    '            answers.append(TestAnswer(\n'
    '                question_id=follow_on_id,\n'
    '                selected_option_ids=[follow_on_opt.option_id],\n'
    '            ))\n'
    '            already_spliced_followons.add(follow_on_id)\n'
    '            current_opt = follow_on_opt\n'
    '    return answers\n',
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
