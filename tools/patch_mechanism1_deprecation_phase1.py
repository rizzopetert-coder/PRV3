"""
Mechanism 1 deprecation, Phase 1 (engine scoring cleanup). Gemini-
reviewed across 3 rounds, both decision points approved by Pete as
recommended:

  1. PRIOR_ADJUSTER_INDEX/PRIOR_ADJUSTERS/PriorAdjuster (engine/data/
     intake.py) -- deprecated in place, NOT deleted. engine/data/
     validate.py imports these by name for two real, currently-passing
     checks -- deleting would break that file's import, a third file
     outside this phase's named scope. Comment-only marking, zero
     behavior change to intake.py itself.

  2. initialize_priors() (engine/accumulation.py) -- rewritten to an
     unconditional flat baseline (1/n for every state), removing BOTH
     the significant_events-driven elevation (Mechanism 1 proper) AND
     the headcount<25 -> the_founders_grip elevation (technically filed
     under "Mechanism 2" in intake.py's own docs, but functionally the
     same dead-weight prior-mutation pattern -- confirmed via
     AccumulationEngine.priors's one getter having zero callers
     repo-wide, so removing it changes no live scoring output). The
     call site (AccumulationEngine.__init__) drops the now-unused
     intake_data argument to initialize_priors().

  3. tools/_mob.txt Priority Queue -- new item 7, flagging validate.py's
     two now-stale-in-spirit (but still passing) PRIOR_ADJUSTER_INDEX
     checks for whenever that file is next touched. Not fixed here --
     explicitly out of Phase 1's scope per Pete's direction.

Usage:
  python tools/patch_mechanism1_deprecation_phase1.py --dry-run
  python tools/patch_mechanism1_deprecation_phase1.py --write
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
# 1. engine/data/intake.py -- deprecation comment, no logic change
# ============================================================================

edit(
    "engine/data/intake.py",
    "# ── Prior Probability Adjusters — Section I.3.1 ────────────────────────────────\n",
    "# DEPRECATED (Mechanism 1) -- this session. PRIOR_ADJUSTER_INDEX/\n"
    "# PRIOR_ADJUSTERS/PriorAdjuster below are no longer consumed by\n"
    "# initialize_priors() (engine/accumulation.py) or any live scoring path.\n"
    "# Confirmed before deprecating: AccumulationEngine.priors's one getter has\n"
    "# zero callers repo-wide, so this data never reached real ranking/output --\n"
    "# this change makes that structural rather than incidental.\n"
    "# significant_events is now synthesis-only narrative metadata (Phase 3),\n"
    "# never a scoring input. Kept in place, not deleted: engine/data/validate.py\n"
    "# still imports these names for two structural checks (\"none\" event exists,\n"
    "# its multiplier is 1.0) that remain harmless but check a now-deprecated\n"
    "# mechanism -- flagged in tools/_mob.txt's Priority Queue, not addressed\n"
    "# here. See Decision Register for the full deprecation record.\n"
    "# ── Prior Probability Adjusters — Section I.3.1 ────────────────────────────────\n",
)

# ============================================================================
# 2. engine/accumulation.py -- initialize_priors() flattened, import + call
#    site updated
# ============================================================================

edit(
    "engine/accumulation.py",
    "from engine.data.intake import (\n"
    "    PRIOR_ADJUSTER_INDEX,\n"
    "    ROLE_COEFFICIENTS,\n"
    "    AXIS_MODIFIER_INDEX,\n"
    "    HIGH_HAZARD_INDUSTRIES,\n"
    ")\n",
    "from engine.data.intake import (\n"
    "    ROLE_COEFFICIENTS,\n"
    "    AXIS_MODIFIER_INDEX,\n"
    "    HIGH_HAZARD_INDUSTRIES,\n"
    ")\n",
)

edit(
    "engine/accumulation.py",
    'def initialize_priors(intake_data: IntakeData) -> dict:\n'
    '    """\n'
    '    Build the initial state probability distribution from intake data.\n'
    '    Returns {state_id: prior_probability} normalized to sum 1.0.\n'
    '\n'
    '    Steps:\n'
    '      1. Equal baseline prior: 1/n across all states.\n'
    '      2. Significant event multipliers applied to elevated state lists.\n'
    '      3. Headcount < 25 elevates the_founders_grip (CALIBRATION TARGET value).\n'
    '      4. Proportional normalization.\n'
    '\n'
    '    Spec reference: Section II.1\n'
    '    """\n'
    '    n = len(STATE_PROFILES)\n'
    '    priors = {sid: 1.0 / n for sid in STATE_PROFILES}\n'
    '\n'
    '    # Significant event adjustments (Section I.3.1)\n'
    '    for event_id in intake_data.significant_events:\n'
    '        adjuster = PRIOR_ADJUSTER_INDEX.get(event_id)\n'
    '        if adjuster is None:\n'
    '            continue\n'
    '        m = _coeff(adjuster.multiplier)\n'
    '        for sid in adjuster.elevated_states:\n'
    '            if sid in priors:\n'
    '                priors[sid] *= m\n'
    '\n'
    '    # Headcount < 25: elevate the_founders_grip prior\n'
    '    if intake_data.headcount < 25 and "the_founders_grip" in priors:\n'
    '        modifier = AXIS_MODIFIER_INDEX.get("headcount_small_founders_grip")\n'
    '        if modifier is not None:\n'
    '            priors["the_founders_grip"] *= _coeff(modifier.multiplier)\n'
    '\n'
    '    # Proportional normalization — full distribution must sum to 1.0\n'
    '    total = sum(priors.values())\n'
    '    if total > 0:\n'
    '        priors = {sid: v / total for sid, v in priors.items()}\n'
    '\n'
    '    return priors\n',
    'def initialize_priors() -> dict:\n'
    '    """\n'
    '    Flat, neutral baseline prior distribution -- 1/n for every state,\n'
    '    unconditionally. Mechanism 1 (Prior Probability Adjusters, Section\n'
    '    I.3.1 -- significant-events-driven and headcount-driven prior\n'
    '    elevation) is DEPRECATED this session: confirmed nothing in the real\n'
    '    ranking/output pipeline ever reads AccumulationEngine.priors (its one\n'
    '    getter, below, has zero callers repo-wide), so elevating this\n'
    '    distribution never affected live scoring output. significant_events is\n'
    '    now synthesis-only narrative metadata (Phase 3), never a scoring input.\n'
    '\n'
    '    Kept as a real function, not inlined at its one call site, to preserve\n'
    '    AccumulationSession.priors\'s existing contract (dict[state_id, float]\n'
    '    summing to 1.0) for AccumulationEngine.priors\'s getter, even though\n'
    '    nothing currently reads it.\n'
    '\n'
    '    Spec reference: Section II.1 (superseded -- see Decision Register).\n'
    '    """\n'
    '    n = len(STATE_PROFILES)\n'
    '    return {sid: 1.0 / n for sid in STATE_PROFILES}\n',
)

edit(
    "engine/accumulation.py",
    "        self.session = AccumulationSession(\n"
    "            priors=initialize_priors(intake_data),\n"
    "        )\n",
    "        self.session = AccumulationSession(\n"
    "            priors=initialize_priors(),\n"
    "        )\n",
)

# ============================================================================
# 3. tools/_mob.txt -- Priority Queue, new item 7
# ============================================================================

PQ_ANCHOR = (
    "consequence of (b), 0 of 3 suite cases pass. Not fixed this session -- "
    "flagged rather than silently expanded into, matching the same "
    "discipline used throughout the headcount-precision-redesign build."
)

PQ_NEW_ITEM = (
    "\n7. DATED, this session: engine/data/validate.py's two PRIOR_ADJUSTER_INDEX "
    "structural checks (\"Prior adjuster for none event exists\", \"None event "
    "multiplier is 1.0\") now verify a deprecated mechanism -- Mechanism 1 "
    "(Prior Probability Adjusters) was deprecated this session as part of "
    "the significant_events synthesis-only redesign (Decision Register, "
    "Section 13a). Both checks still pass and are harmless (the underlying "
    "PRIOR_ADJUSTER_INDEX data was kept in place, not deleted, specifically "
    "so validate.py's import wouldn't break), but they're checking "
    "something no longer live. Not fixed now -- explicitly out of Phase 1's "
    "scope, flagged so it isn't silently lost. Revisit whenever "
    "validate.py is next touched for an unrelated reason, or when "
    "Mechanism 1's deprecation reaches a natural cleanup point."
)

edit("tools/_mob.txt", PQ_ANCHOR, PQ_ANCHOR + PQ_NEW_ITEM)


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
