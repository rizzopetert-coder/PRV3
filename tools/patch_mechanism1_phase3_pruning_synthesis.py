"""
Mechanism 1 deprecation, Phase 3 (narrowed scope per Pete's option (b)
decision -- leave _QDATA content in place, don't touch calibration
harness branching, just document + wire synthesis).

Two real edits:
  1. engine/data/questions.py -- deprecation comments above Q03A/
     Q03A-D-FOLLOW and Q27A (neither currently has one), plus a short
     addendum appended to Q31's EXISTING comment (preserved verbatim,
     not replaced -- its self-contradicting-condition reason is real,
     separate, and still the primary explanation; the addendum just
     ties it into this session's broader documentation sweep for
     consistency). All four: same message -- structurally excluded from
     PHASE_1_QUESTION_SEQUENCE, real content preserved for
     tools/calibration_runner.py's calibration-only use and possible
     future reactivation, not for production routing. Zero logic
     change -- comments only.

  2. engine/output_synthesis.py -- _build_synthesis_prompt() completes
     synthesize()'s own docstring promise ("intake: org_size, industry,
     role, significant events") that was never implemented. Maps
     significant_events through engine/data/intake.py's
     PRIOR_ADJUSTER_INDEX (full, untrimmed clinical text -- not web/
     lib/types.ts's checkbox-trimmed SIGNIFICANT_EVENT_OPTIONS copy, no
     UI-space constraint here). Omitted entirely when missing, empty,
     or exactly ["none"] -- matching signal_map_context's existing
     conditional-inclusion pattern.

     New test coverage added to tools/test_output_synthesis.py (checks
     31-33): significant_events' full label text appears when present,
     omitted when ["none"], omitted when absent from intake entirely.

Usage:
  python tools/patch_mechanism1_phase3_pruning_synthesis.py --dry-run
  python tools/patch_mechanism1_phase3_pruning_synthesis.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================================
# 1a. engine/data/questions.py -- Q03A/Q03A-D-FOLLOW deprecation comment
# ============================================================================

edit(
    "engine/data/questions.py",
    '''    (
        "Q03A",
        "You mentioned some significant changes in the past 18 months."''',
    '''    # PARKED (Mechanism 1 deprecation, this session): Q03A and its
    # follow-up Q03A-D-FOLLOW were authored assuming significant_events
    # would be collected mid-session and could branch live question
    # routing -- structurally excluded from web/lib/session-store.ts's
    # PHASE_1_QUESTION_SEQUENCE from the start (Phase 1's locked intake
    # adapter always took the Q03B branch; confirmed no code anywhere
    # ever branched core-question routing on significant_events).
    # significant_events is now collected for real at intake (Phase 2),
    # but as synthesis-only narrative metadata (see
    # _build_synthesis_prompt(), engine/output_synthesis.py), never as a
    # session-routing trigger. Real content preserved here, not deleted:
    # tools/calibration_runner.py's generate_answers() (_CONDITIONAL_PAIRS)
    # still exercises Q03A/Q03B for calibration-only scoring signal --
    # deliberately untouched by this session's work. Possible future
    # reactivation if live intake-driven question branching is ever
    # built; not scheduled, not designed.
    (
        "Q03A",
        "You mentioned some significant changes in the past 18 months."''',
)

# ============================================================================
# 1b. engine/data/questions.py -- Q27A deprecation comment
# ============================================================================

edit(
    "engine/data/questions.py",
    '''    (
        "Q27A",
        "How would you describe where the integration stands right now?",''',
    '''    # PARKED (Mechanism 1 deprecation, this session): same treatment as
    # Q03A above -- structurally excluded from PHASE_1_QUESTION_SEQUENCE,
    # real content preserved for tools/calibration_runner.py's
    # generate_answers() (_CONDITIONAL_PAIRS -- "Q27A" is selected there
    # for any profile whose significant_events includes
    # acquisition_or_merger) and possible future reactivation. SEVER-09
    # remains wired to this question's B/C/D options, untouched --
    # calibration-only today, not reachable in production.
    (
        "Q27A",
        "How would you describe where the integration stands right now?",''',
)

# ============================================================================
# 1c. engine/data/questions.py -- Q31 addendum (appended, not replacing)
# ============================================================================

edit(
    "engine/data/questions.py",
    '''    # self-contradicting one). See tools/_mob.txt Section 14 for the full
    # investigation.
    (
        "Q31",''',
    '''    # self-contradicting one). See tools/_mob.txt Section 14 for the full
    # investigation.
    #
    # ADDENDUM (Mechanism 1 deprecation, this session): unrelated to the
    # self-contradicting-condition reason above, but grouped here for
    # consistency -- Q31 gets the same "parked, not deleted" documentation
    # pass as Q03A/Q03A-D-FOLLOW/Q27A this session, all four structurally
    # excluded from PHASE_1_QUESTION_SEQUENCE for their own distinct
    # reasons. Real content preserved for tools/calibration_runner.py's
    # calibration-only use, untouched by this session's work.
    (
        "Q31",''',
)

# ============================================================================
# 2. engine/output_synthesis.py -- significant_events wired into the prompt
# ============================================================================

edit(
    "engine/output_synthesis.py",
    "from engine.data.fallback_synthesis import get_fallback_synthesis\n",
    "from engine.data.fallback_synthesis import get_fallback_synthesis\n"
    "from engine.data.intake import PRIOR_ADJUSTER_INDEX\n",
)

edit(
    "engine/output_synthesis.py",
    '''    intake_lines = (
        f"  organization_size: {intake.get('organization_size', intake.get('org_size', ''))}\\n"
        f"  industry: {intake.get('industry', '')}\\n"
        f"  role: {intake.get('role_level', intake.get('principal_role', ''))}"
    )
    parts = [''',
    '''    intake_lines = (
        f"  organization_size: {intake.get('organization_size', intake.get('org_size', ''))}\\n"
        f"  industry: {intake.get('industry', '')}\\n"
        f"  role: {intake.get('role_level', intake.get('principal_role', ''))}"
    )
    # significant_events is now real, user-submitted synthesis-only
    # narrative metadata (Mechanism 1 deprecation, this session -- Decision
    # Register). Mapped through PRIOR_ADJUSTER_INDEX's full, untrimmed
    # clinical text (not web/lib/types.ts's SIGNIFICANT_EVENT_OPTIONS
    # checkbox-trimmed copy -- no UI-space constraint here, and the fuller
    # specificity gives Sonnet more to ground the narrative in). Omitted
    # entirely when missing, empty, or exactly ["none"] -- a literal
    # "None" or empty section would read as an unknown value rather than
    # "nothing significant happened."
    significant_events = intake.get("significant_events") or []
    event_labels = [
        PRIOR_ADJUSTER_INDEX[e].event_label
        for e in significant_events
        if e != "none" and e in PRIOR_ADJUSTER_INDEX
    ]
    if event_labels:
        intake_lines += "\\n  significant_events:\\n" + "\\n".join(
            f"    - {label}" for label in event_labels
        )
    parts = [''',
)

# ============================================================================
# 3. tools/test_output_synthesis.py -- new coverage, checks 31-33
# ============================================================================

edit(
    "tools/test_output_synthesis.py",
    "  30. _parse_synthesis_response: genuinely broken fenced response still falls back correctly\n\"\"\"",
    "  30. _parse_synthesis_response: genuinely broken fenced response still falls back correctly\n"
    "  31. _build_synthesis_prompt: includes significant_events full label text when present\n"
    "  32. _build_synthesis_prompt: omits significant_events section when [\"none\"]\n"
    "  33. _build_synthesis_prompt: omits significant_events section when absent from intake\n\"\"\"",
)

edit(
    "tools/test_output_synthesis.py",
    '''check(
    "_build_synthesis_prompt: includes narrative_response",
    "Leadership keeps deferring the hard calls." in prompt_text,
    "narrative_response not found",
)


# ── 24–25. OutputSynthesisEngine stateful interface ──────────────────────────''',
    '''check(
    "_build_synthesis_prompt: includes narrative_response",
    "Leadership keeps deferring the hard calls." in prompt_text,
    "narrative_response not found",
)


# ── 31–33. _build_synthesis_prompt: significant_events (Mechanism 1 deprecation) ──

prompt_with_events = _build_synthesis_prompt(
    state_name="Decision Paralysis",
    severity_tier="Entrenched",
    resolution_family="Groundwork",
    asset_score=0.15,
    liability_score=0.60,
    narrative_response="Leadership keeps deferring the hard calls.",
    intake={
        "organization_size": "medium", "industry": "healthcare", "role_level": "director",
        "significant_events": ["acquisition_or_merger"],
    },
)
check(
    "_build_synthesis_prompt: includes significant_events full label text when present",
    "Acquisition or merger" in prompt_with_events,
    "acquisition_or_merger label not found",
)

prompt_none_event = _build_synthesis_prompt(
    state_name="Decision Paralysis",
    severity_tier="Entrenched",
    resolution_family="Groundwork",
    asset_score=0.15,
    liability_score=0.60,
    narrative_response="Leadership keeps deferring the hard calls.",
    intake={
        "organization_size": "medium", "industry": "healthcare", "role_level": "director",
        "significant_events": ["none"],
    },
)
check(
    "_build_synthesis_prompt: omits significant_events section when [\\"none\\"]",
    "significant_events" not in prompt_none_event,
    "significant_events section present despite [\\"none\\"]",
)

prompt_missing_event = _build_synthesis_prompt(
    state_name="Decision Paralysis",
    severity_tier="Entrenched",
    resolution_family="Groundwork",
    asset_score=0.15,
    liability_score=0.60,
    narrative_response="Leadership keeps deferring the hard calls.",
    intake={"organization_size": "medium", "industry": "healthcare", "role_level": "director"},
)
check(
    "_build_synthesis_prompt: omits significant_events section when absent from intake",
    "significant_events" not in prompt_missing_event,
    "significant_events section present despite missing intake field",
)


# ── 24–25. OutputSynthesisEngine stateful interface ──────────────────────────''',
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    by_file: dict[str, list[tuple[str, str]]] = {}
    for path, old, new in EDITS:
        by_file.setdefault(path, []).append((old, new))

    for rel_path, pairs in by_file.items():
        full_path = REPO_ROOT / rel_path
        content = full_path.read_text(encoding="utf-8")
        for old, new in pairs:
            count = content.count(old)
            if count != 1:
                print(f"ABORT: {rel_path}: expected exactly 1 match for anchor, found {count}")
                print(f"  anchor (first 150 chars): {old[:150]!r}")
                sys.exit(1)
            content = content.replace(old, new, 1)

        if args.dry_run:
            print(f"=== {rel_path}: {len(pairs)} edit(s) would apply cleanly ===")
        else:
            full_path.write_text(content, encoding="utf-8")
            print(f"=== {rel_path}: {len(pairs)} edit(s) written ===")

    if args.dry_run:
        print("\nDry run complete. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
