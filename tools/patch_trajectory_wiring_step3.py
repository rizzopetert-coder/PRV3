"""
PRV3 -- Diagnostic Dimension Expansion, Step 3 of 3: Trajectory /
Directionality

New derived-signal logic (not pure wiring, unlike Steps 1-2): compares
early-half vs. late-half answered-sequence liability signal within a Path
1 session, plus a dispersion-delta (added per Pete's confirmation, reusing
compute_liability_dispersion the same way SPOF/Diffuse Causation already
does), plus an honest duration_band passthrough (never blended into a
formula -- deliberate, given this session already found two fabricated
Gemini multiplier claims).

Six files:
  1. engine/accumulation.py -- new compute_trajectory(early_vector,
     late_vector, duration_band) -> dict, pure vector math, placed next
     to compute_cascade_risk. New TRAJECTORY_STABILITY_THRESHOLD constant,
     explicitly CALIBRATION TARGET (starting hypothesis 0.20, same order
     of magnitude as WEAK_DAMPED_THRESHOLD/MODERATE_PROMINENCE_DELTA
     elsewhere in this codebase -- not yet data-validated).
  2. engine/main.py -- new MIN_ANSWERS_FOR_TRAJECTORY = 4 structural guard
     (not a calibration target -- need >=2 real answers per half for a
     split to mean anything), new _replay_partial_vector() helper
     (duplicates the scratch-replay TECHNIQUE _build_signal_map_context()
     already uses, applied differently: one shared scratch session
     accumulated across an entire slice, not a fresh scratch per
     individual answer -- not a byte-identical copy, same underlying
     primitive used for a different purpose), new _compute_trajectory_
     context() orchestrator (position-split answers_log, replay each
     half, call compute_trajectory()). Call site in
     run_accumulated_engine(): extracts duration_band from severity_inputs
     (it's not a standalone parameter anywhere -- lives inside each
     SeverityInput-shaped dict), computes trajectory_result, threads it
     into the final assemble_output() call as a new kwarg.
  3. engine/contract.py -- assemble_output() gains trajectory_result=None
     optional kwarg (exact mirror of the existing synthesis_result=None
     pattern). private_output dict gains "trajectory": trajectory_result
     (passthrough -- real dict for Path 1, None for Path B/any caller not
     passing it, matching friction_tax_estimate's existing nullable
     precedent). _PRIVATE_OUTPUT_FIELDS gains "trajectory" -- safe because
     the key is now always present (value may be null), same as
     friction_tax_estimate.
  4. web/lib/engine-client.ts -- EngineResult.private_output.trajectory
     typed `{...} | null` (always-present key, matching
     friction_tax_estimate's `number | null` pattern -- NOT optional,
     since assemble_output() always includes this key in the JSON).
  5. web/lib/types.ts -- PrivateOutputPayload.trajectory typed
     `{...} | null` OPTIONAL (`trajectory?: {...} | null`) -- optional
     because Path B's route.ts never sets this key at all (same Path-B-
     untouched scoping as cascade_risk/causation_pattern), but allowing
     `| null` too since EngineResult's own field can genuinely be null
     and route.ts does a direct passthrough with no `?? undefined`
     massaging.
  6. web/app/api/diagnostic/session/answer/route.ts -- threads
     engineResult.private_output.trajectory into privatePayload.

web/app/api/result/route.ts (Path B) deliberately NOT touched, matching
Steps 1-2's scoping decision.

design note -- delta does NOT clamp negative per-field values to 0 before
summing, unlike compute_liability_dispersion()'s clamp (which exists
because entropy is undefined over negative "probabilities" -- a math
requirement specific to that function, not a general policy). delta is a
plain signed-sum comparison; clamping would silently discard real signal
from negative-signed answer contributions (confirmed these exist --
compute_liability_dispersion's own docstring cites
"authority_liability: -0.15" as a real example).

Usage:
  python tools/patch_trajectory_wiring_step3.py --dry-run
  python tools/patch_trajectory_wiring_step3.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
ACCUMULATION_FILE = REPO_ROOT / "engine" / "accumulation.py"
MAIN_FILE = REPO_ROOT / "engine" / "main.py"
CONTRACT_FILE = REPO_ROOT / "engine" / "contract.py"
ENGINE_CLIENT_FILE = REPO_ROOT / "web" / "lib" / "engine-client.ts"
TYPES_FILE = REPO_ROOT / "web" / "lib" / "types.ts"
ANSWER_ROUTE_FILE = REPO_ROOT / "web" / "app" / "api" / "diagnostic" / "session" / "answer" / "route.ts"

EDITS: list[tuple[Path, str, str, str]] = []

# --- engine/accumulation.py: 1 edit (new constant + function) ----------------

EDITS.append((
    ACCUMULATION_FILE,
    "accumulation.py: add TRAJECTORY_STABILITY_THRESHOLD + compute_trajectory()",
    '''    # max(0.0, ...) is a floor against the same -0.0 propagation described
    # in compute_liability_dispersion() above.
    return max(0.0, round(dispersion * intensity, 4))


def rank_states(''',
    '''    # max(0.0, ...) is a floor against the same -0.0 propagation described
    # in compute_liability_dispersion() above.
    return max(0.0, round(dispersion * intensity, 4))


# Bucketing threshold for compute_trajectory()'s direction classification.
# CALIBRATION TARGET -- starting hypothesis, same order of magnitude as
# WEAK_DAMPED_THRESHOLD / MODERATE_PROMINENCE_DELTA elsewhere in this
# codebase. Not yet data-validated.
TRAJECTORY_STABILITY_THRESHOLD: float = 0.20  # CALIBRATION TARGET


def compute_trajectory(
    early_vector: dict,
    late_vector: dict,
    duration_band: Optional[str] = None,
) -> dict:
    """
    Trajectory / Directionality -- Diagnostic Dimension Expansion Step 3.
    Derived output only: zero new signal collection, zero modification to
    the 8-field accumulation model or rank_states(). A framing input for
    output_synthesis, not a new scored dimension -- same convention as
    Cascade Risk and SPOF/Diffuse Causation.

    early_vector / late_vector: independently-accumulated vectors from the
    first half and second half of a session's answered-question sequence
    (position-based split -- answers_log carries no timestamp field, so
    "early/late" means early/late in answer order, not wall-clock time).
    Each is its own scratch accumulation, not cumulative-through-midpoint
    vs. final -- this measures whether the session's SECOND HALF alone
    carried more or less liability signal than its FIRST HALF, not
    whether a running total grew (which contributions being signed would
    make a non-monotonic, misleading read anyway).

    delta -- sum(late 4 liability fields) - sum(early 4 liability fields),
    RAW values, not clamped to 0.0 the way compute_liability_dispersion()
    clamps (that clamp exists because entropy is undefined over negative
    "probabilities" -- a requirement specific to entropy math, not a
    general policy here). Positive: liability signal denser in the
    session's second half than its first. Negative: denser in the first
    half. Same DIMENSIONAL_FIELDS liability-only filtering Cascade Risk
    and compute_liability_dispersion() already use.

    dispersion_delta -- compute_liability_dispersion(late_vector) -
    compute_liability_dispersion(early_vector), the identical Shannon-
    entropy term Cascade Risk and SPOF/Diffuse Causation already use,
    reused rather than reinvented. Positive: liability spread across more
    axes in the second half than the first (broadening). Negative:
    concentrated into fewer axes in the second half (narrowing).

    direction -- delta bucketed against TRAJECTORY_STABILITY_THRESHOLD:
      delta >=  threshold -> "escalating"
      delta <= -threshold -> "decelerating"
      otherwise            -> "stable"

    duration_band -- passthrough only, not blended into delta/direction by
    any formula. Real value ("0_6mo" | "6_18mo" | "18mo_plus") only when a
    severity follow-on collecting it fired this session; None otherwise.
    Reported alongside the intra-session read, not fused with it.

    Spec reference: Diagnostic Dimension Expansion decision record
    (prompts/diagnostic-dimension-expansion.md), Candidate 1.
    """
    liability_fields = [f for f in DIMENSIONAL_FIELDS if f.endswith("_liability")]
    early_sum = sum(early_vector.get(f, 0.0) for f in liability_fields)
    late_sum = sum(late_vector.get(f, 0.0) for f in liability_fields)
    delta = round(late_sum - early_sum, 4)

    dispersion_delta = round(
        compute_liability_dispersion(late_vector) - compute_liability_dispersion(early_vector),
        4,
    )

    if delta >= TRAJECTORY_STABILITY_THRESHOLD:
        direction = "escalating"
    elif delta <= -TRAJECTORY_STABILITY_THRESHOLD:
        direction = "decelerating"
    else:
        direction = "stable"

    return {
        "delta": delta,
        "dispersion_delta": dispersion_delta,
        "direction": direction,
        "duration_band": duration_band,
    }


def rank_states(''',
))

# --- engine/main.py: 4 edits --------------------------------------------------

EDITS.append((
    MAIN_FILE,
    "main.py: import compute_trajectory",
    '''from engine.accumulation import (
    IntakeData,
    StateRanking,
    AccumulationSession,
    accumulate_answer,
    rank_states,
)''',
    '''from engine.accumulation import (
    IntakeData,
    StateRanking,
    AccumulationSession,
    accumulate_answer,
    rank_states,
    compute_trajectory,
)''',
))

EDITS.append((
    MAIN_FILE,
    "main.py: new _replay_partial_vector() + _compute_trajectory_context() helpers",
    '''    return " ".join(observations)


def run_accumulated_engine(''',
    '''    return " ".join(observations)


# Need >=2 real answers per half for a split to mean anything --
# structural correctness guard, not an empirical calibration constant.
MIN_ANSWERS_FOR_TRAJECTORY: int = 4


def _replay_partial_vector(answers_log_slice: list, intake_data: IntakeData) -> dict:
    """
    Replay a slice of answers_log through ONE shared scratch
    AccumulationSession to get the real accumulated vector for just that
    slice. Reuses the same accumulate_answer()-against-a-scratch-session
    technique _build_signal_map_context() uses above, applied differently:
    one shared scratch session per slice (cumulative across the whole
    slice), not a fresh scratch per individual answer (which is what
    _build_signal_map_context() needs to isolate each answer's own
    contribution in isolation). Duplicated rather than extracted into a
    shared helper -- same precedent as the STATE_RESOLUTION_FAMILY
    triplication elsewhere in this codebase, per the standing rule
    against refactoring adjacent code mid-build.
    """
    scratch = AccumulationSession()
    for entry in answers_log_slice:
        question_id = entry.get("question_id") if isinstance(entry, dict) else None
        option_id = entry.get("option_id") if isinstance(entry, dict) else None
        question = QUESTION_LIBRARY.get(question_id)
        if question is None:
            continue
        option = next(
            (o for o in question.answer_options if o.option_id == option_id),
            None,
        )
        if option is None:
            continue
        accumulate_answer(scratch, option, intake_data, question_id)
    return scratch.accumulated_vector


def _compute_trajectory_context(
    answers_log: list,
    intake_data: IntakeData,
    duration_band: Optional[str],
) -> dict:
    """
    Split answers_log by position (first half vs. second half of the
    answered sequence) and diff the two halves' independently-replayed
    vectors via compute_trajectory(). Below MIN_ANSWERS_FOR_TRAJECTORY,
    returns the defined "insufficient_data" default rather than a
    degenerate/misleading delta -- same convention as
    compute_causation_pattern()'s "insufficient_signal" and
    compute_cascade_risk()'s 0.0-on-no-signal. duration_band is still
    passed through even in this case -- it is independently real data,
    unrelated to whether the intra-session split was viable.
    """
    if len(answers_log) < MIN_ANSWERS_FOR_TRAJECTORY:
        return {
            "delta": 0.0,
            "dispersion_delta": 0.0,
            "direction": "insufficient_data",
            "duration_band": duration_band,
        }

    midpoint = len(answers_log) // 2
    early_vector = _replay_partial_vector(answers_log[:midpoint], intake_data)
    late_vector = _replay_partial_vector(answers_log[midpoint:], intake_data)

    return compute_trajectory(early_vector, late_vector, duration_band)


def run_accumulated_engine(''',
))

EDITS.append((
    MAIN_FILE,
    "main.py: call site -- compute trajectory_result before session_data",
    '''    checkpoint_results = checkpoint_results or {}
    session_data = SessionData(''',
    '''    duration_band = next(
        (si.get("duration_band") for si in (severity_inputs or []) if si.get("duration_band")),
        None,
    )
    trajectory_result = _compute_trajectory_context(answers_log or [], intake_data, duration_band)

    checkpoint_results = checkpoint_results or {}
    session_data = SessionData(''',
))

EDITS.append((
    MAIN_FILE,
    "main.py: thread trajectory_result into assemble_output()",
    '''        checkpoint_q27=checkpoint_result_from_wire("Q27", checkpoint_results.get("q27")),
    )

    return assemble_output(session_data, synthesis_result=synthesis_result)''',
    '''        checkpoint_q27=checkpoint_result_from_wire("Q27", checkpoint_results.get("q27")),
    )

    return assemble_output(session_data, synthesis_result=synthesis_result, trajectory_result=trajectory_result)''',
))

# --- engine/contract.py: 3 edits -----------------------------------------------

EDITS.append((
    CONTRACT_FILE,
    "contract.py: assemble_output() gains trajectory_result kwarg",
    "def assemble_output(session: SessionData, synthesis_result=None) -> dict:",
    "def assemble_output(session: SessionData, synthesis_result=None, trajectory_result=None) -> dict:",
))

EDITS.append((
    CONTRACT_FILE,
    "contract.py: private_output dict construction",
    '''    private_output = {
        "opening_text":          priv.state_name if priv else "",
        "resolution_routing":    priv.resolution_family if priv else "",
        "friction_tax_estimate": priv.friction_tax_estimate if priv else None,
        "cascade_risk":          compute_cascade_risk(session.accumulated_vector),
        "causation_pattern":     compute_causation_pattern(session.accumulated_vector, routing),
    }''',
    '''    private_output = {
        "opening_text":          priv.state_name if priv else "",
        "resolution_routing":    priv.resolution_family if priv else "",
        "friction_tax_estimate": priv.friction_tax_estimate if priv else None,
        "cascade_risk":          compute_cascade_risk(session.accumulated_vector),
        "causation_pattern":     compute_causation_pattern(session.accumulated_vector, routing),
        "trajectory":            trajectory_result,
    }''',
))

EDITS.append((
    CONTRACT_FILE,
    "contract.py: _PRIVATE_OUTPUT_FIELDS validation set",
    '''_PRIVATE_OUTPUT_FIELDS = {
    "opening_text", "resolution_routing", "friction_tax_estimate", "cascade_risk",
    "causation_pattern",
}''',
    '''_PRIVATE_OUTPUT_FIELDS = {
    "opening_text", "resolution_routing", "friction_tax_estimate", "cascade_risk",
    "causation_pattern", "trajectory",
}''',
))

# --- web/lib/engine-client.ts: 1 edit -----------------------------------------

EDITS.append((
    ENGINE_CLIENT_FILE,
    "engine-client.ts: EngineResult.private_output.trajectory",
    '''  private_output: {
    opening_text: string;
    resolution_routing: string;
    friction_tax_estimate: number | null;
    cascade_risk: number;
    causation_pattern: {
      pattern: "single_point" | "diffuse" | "insufficient_signal";
      dispersion: number;
      qualified_state_count: number;
    };
  };''',
    '''  private_output: {
    opening_text: string;
    resolution_routing: string;
    friction_tax_estimate: number | null;
    cascade_risk: number;
    causation_pattern: {
      pattern: "single_point" | "diffuse" | "insufficient_signal";
      dispersion: number;
      qualified_state_count: number;
    };
    trajectory: {
      delta: number;
      dispersion_delta: number;
      direction: "escalating" | "stable" | "decelerating" | "insufficient_data";
      duration_band: "0_6mo" | "6_18mo" | "18mo_plus" | null;
    } | null;
  };''',
))

# --- web/lib/types.ts: 1 edit --------------------------------------------------

EDITS.append((
    TYPES_FILE,
    "types.ts: PrivateOutputPayload.trajectory (optional -- Path B not wired this commit)",
    '''  // SPOF vs. Diffuse Causation. Same Path 1 / Path B scoping as
  // cascade_risk above -- optional, Path B not wired this commit.
  causation_pattern?: {
    pattern: "single_point" | "diffuse" | "insufficient_signal";
    dispersion: number;
    qualified_state_count: number;
  };''',
    '''  // SPOF vs. Diffuse Causation. Same Path 1 / Path B scoping as
  // cascade_risk above -- optional, Path B not wired this commit.
  causation_pattern?: {
    pattern: "single_point" | "diffuse" | "insufficient_signal";
    dispersion: number;
    qualified_state_count: number;
  };

  // Trajectory / Directionality. Same Path 1 / Path B scoping as the two
  // fields above -- optional, Path B not wired this commit. `| null`
  // included because the raw engine field can genuinely be null (Path B
  // calls assemble_output() without trajectory_result), passed through
  // directly from engine-client.ts with no undefined-coercion.
  trajectory?: {
    delta: number;
    dispersion_delta: number;
    direction: "escalating" | "stable" | "decelerating" | "insufficient_data";
    duration_band: "0_6mo" | "6_18mo" | "18mo_plus" | null;
  } | null;''',
))

# --- web/app/api/diagnostic/session/answer/route.ts: 1 edit -------------------

EDITS.append((
    ANSWER_ROUTE_FILE,
    "answer/route.ts: thread trajectory into privatePayload",
    '''    cascade_risk: engineResult.private_output.cascade_risk,
    causation_pattern: engineResult.private_output.causation_pattern,

    intake: session.intake,''',
    '''    cascade_risk: engineResult.private_output.cascade_risk,
    causation_pattern: engineResult.private_output.causation_pattern,
    trajectory: engineResult.private_output.trajectory,

    intake: session.intake,''',
))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    file_texts: dict[Path, str] = {}
    for path in {e[0] for e in EDITS}:
        file_texts[path] = path.read_text(encoding="utf-8")

    for path, label, old, new in EDITS:
        count = file_texts[path].count(old)
        if count != 1:
            print(f"ABORT -- anchor for '{label}' matched {count} times in {path.relative_to(REPO_ROOT)}, need exactly 1", file=sys.stderr)
            sys.exit(1)

    print("=" * 100)
    for path, label, old, new in EDITS:
        print(f"\n--- {label} ({path.relative_to(REPO_ROOT)}) ---")
        print("BEFORE:")
        print(old)
        print("AFTER:")
        print(new)
    print("\n" + "=" * 100)

    new_texts: dict[Path, str] = dict(file_texts)
    for path, label, old, new in EDITS:
        new_texts[path] = new_texts[path].replace(old, new, 1)

    print("Files touched:")
    for path in file_texts:
        delta = len(new_texts[path]) - len(file_texts[path])
        print(f"  {path.relative_to(REPO_ROOT)}: {delta:+d} chars")

    print("\nweb/app/api/result/route.ts (Path B): confirmed NOT touched by this script.")

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    for path, text in new_texts.items():
        path.write_text(text, encoding="utf-8")
        print(f"\nWROTE {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
