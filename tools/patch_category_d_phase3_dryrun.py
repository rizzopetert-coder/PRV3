"""
PRV3 -- Category D, Phase 3 build. Four existing-file edits (engine/
friction_tax.py, engine/main.py, api/engine.py, web/lib/engine-client.ts);
four new files handled separately via Write. All four Gemini architecture
gates cleared this session (rendering target, financial mechanic,
get_industry_wage() signature, severity-trigger handling) -- see
tools/_mob.txt Decision Register.

Run with --dry-run first (default). Pass --write to apply.
"""
import argparse
import pathlib
import sys

FT_PATH = pathlib.Path("engine/friction_tax.py")
MAIN_PATH = pathlib.Path("engine/main.py")
API_PATH = pathlib.Path("api/engine.py")
CLIENT_PATH = pathlib.Path("web/lib/engine-client.ts")

# ---------------------------------------------------------------------------
# (1) engine/friction_tax.py -- get_industry_wage()
# ---------------------------------------------------------------------------

OLD_FT = '''def resolve_headcount_bucket(headcount: int) -> str:'''

NEW_FT = '''def get_industry_wage(industry: str) -> Optional[float]:
    """
    Public accessor for _INDUSTRY_WAGE_DATA's per-employee mean annual wage
    (BLS OEWS May 2023), keyed by the same 9 industry categories intake
    already collects (engine/data/intake.py INTAKE_FIELDS["industry"]).
    Returns None on an unrecognized industry -- matches this file's
    existing lookup convention (PAYROLL_BASELINE_GRID.get(),
    ORG_TYPE_SCALARS.get()), not an exception. Category D (free condensed
    diagnostic), this session -- the only consumer of this accessor;
    PAYROLL_BASELINE_GRID's own headcount x industry_wage math is
    untouched, this is a standalone single-value lookup.
    """
    entry = _INDUSTRY_WAGE_DATA.get(industry)
    return entry[0] if entry is not None else None


def resolve_headcount_bucket(headcount: int) -> str:'''

# ---------------------------------------------------------------------------
# (2) engine/main.py -- run_condensed_engine()
# ---------------------------------------------------------------------------

OLD_MAIN_IMPORTS = '''from engine.output_synthesis import OutputSynthesisEngine
from engine.resolution_families import translate_resolution_family'''

NEW_MAIN_IMPORTS = '''from engine.output_synthesis import OutputSynthesisEngine, SynthesisResult
from engine.resolution_families import translate_resolution_family
from engine.data.fallback_synthesis import get_fallback_synthesis'''

# Anchored on run_accumulated_engine()'s own closing return + blank lines,
# so the new function lands immediately after it -- same file region,
# same category of function (Path 1 completion orchestrator).
OLD_MAIN_ANCHOR = '''    return assemble_output(session_data, synthesis_result=synthesis_result, trajectory_result=trajectory_result)'''

NEW_MAIN_ANCHOR = '''    return assemble_output(session_data, synthesis_result=synthesis_result, trajectory_result=trajectory_result)


def run_condensed_engine(
    accumulated_vector: dict,
    intake: dict,
    answered_question_count: int,
) -> dict:
    """
    Category D (free condensed diagnostic) completion orchestrator, this
    session. Mirrors run_accumulated_engine()'s ranking/severity/
    resolution_family steps exactly, but never calls the real
    OutputSynthesisEngine -- Pete's locked decision (Decision Register,
    this session): a free, anonymous, ungated tool must not invoke a
    paid, timeout-exposed LLM endpoint per submission. Uses
    get_fallback_synthesis() directly instead -- the same static,
    already-approved copy the full diagnostic's own LLM-failure path
    already relies on, keyed on (resolution_family, severity_tier).

    No checkpoints, no severity follow-ons, no trajectory context --
    Category D's condensed session never collects any of these inputs by
    design (web/lib/condensed-session-store.ts never reads
    severity_follow_on_id/severity_input from /api/accumulate's
    response). severity_result is therefore always "Emerging" --
    SeverityEngine with zero inputs, same behavior as Path B, not a bug
    introduced here.

    asset_score/liability_score/signal_map_context are intentionally not
    computed here -- they exist solely to feed the real synthesis
    prompt, which this function never calls.
    """
    final_rankings = rank_states(accumulated_vector, answered_question_count, SALIENCE_PROFILES)

    severity_result = SeverityEngine().score()

    output_engine = OutputEngine()
    output_engine.set_noise_baseline()
    output_package = output_engine.build(final_rankings, severity_result)

    synthesis_result = None
    if final_rankings:
        commercial_family = translate_resolution_family(
            output_package.private.resolution_family
            if output_package.private else ""
        )
        fb = get_fallback_synthesis(commercial_family, severity_result.tier)
        synthesis_result = SynthesisResult(
            **fb,
            synthesis_confidence=0.0,
            is_fallback=True,
        )

    intake_data = _locked_intake_to_engine_intake(intake)
    session_data = SessionData(
        session_id=SessionData.new_session_id(),
        intake=intake_data,
        final_rankings=final_rankings,
        accumulated_vector=accumulated_vector,
        output_package=output_package,
        severity_result=severity_result,
        checkpoint_q11=checkpoint_result_from_wire("Q11", None),
        checkpoint_q19=checkpoint_result_from_wire("Q19", None),
        checkpoint_q27=checkpoint_result_from_wire("Q27", None),
    )

    return assemble_output(session_data, synthesis_result=synthesis_result, trajectory_result=None)'''

# ---------------------------------------------------------------------------
# (3) api/engine.py -- new /api/condensed-complete route
# ---------------------------------------------------------------------------

OLD_API_IMPORTS = '''from engine.main import (
    run_engine,
    accumulate_answers,
    run_checkpoint,
    run_accumulated_engine,
    get_question_copy,
)'''

NEW_API_IMPORTS = '''from engine.main import (
    run_engine,
    accumulate_answers,
    run_checkpoint,
    run_accumulated_engine,
    run_condensed_engine,
    get_question_copy,
)
from engine.friction_tax import get_industry_wage'''

OLD_API_ANCHOR = '''@app.post("/api/question-copy")
async def question_copy(request: Request):'''

NEW_API_ANCHOR = '''@app.post("/api/condensed-complete")
async def condensed_complete(request: Request):
    # Category D (free condensed diagnostic), this session -- completion
    # endpoint for the separate condensed session flow. No checkpoint_
    # results/severity_inputs/answers_log params (run_accumulated_engine()
    # has them) -- Category D's condensed session never collects any of
    # them by design. Merges the financial benchmark range into the same
    # response so the TS caller makes one round trip, not two -- the
    # get_industry_wage() lookup is a pure function, no reason to split
    # it into its own endpoint.
    _check_secret(request)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        accumulated_vector = payload.get("accumulated_vector", {}) if isinstance(payload, dict) else {}
        intake = payload.get("intake", {}) if isinstance(payload, dict) else {}
        answered_question_count = payload.get("answered_question_count", 0) if isinstance(payload, dict) else 0
        result = run_condensed_engine(accumulated_vector, intake, answered_question_count)

        industry = intake.get("industry", "") if isinstance(intake, dict) else ""
        wage = get_industry_wage(industry)
        result["condensed_financial_range"] = (
            {"low": round(wage * 0.50, 2), "high": round(wage * 0.75, 2), "currency": "USD"}
            if wage is not None
            else {"low": None, "high": None, "currency": "USD"}
        )

        return JSONResponse(content=result)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Unknown state ID: {e}")
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except Exception:
        raise HTTPException(status_code=500, detail="Engine error")


@app.post("/api/question-copy")
async def question_copy(request: Request):'''

# ---------------------------------------------------------------------------
# (4) web/lib/types.ts -- CondensedOutputPayload
# ---------------------------------------------------------------------------

TYPES_PATH = pathlib.Path("web/lib/types.ts")

OLD_TYPES_ANCHOR = '''  primary_asset_domain: string;
}

// ---------------------------------------------------------------------------
// ShareableOutputPayload
// ---------------------------------------------------------------------------'''

NEW_TYPES_ANCHOR = '''  primary_asset_domain: string;
}

// ---------------------------------------------------------------------------
// CondensedOutputPayload -- Category D (free condensed diagnostic), this
// session. Deliberately NOT PrivateOutputPayload -- a much smaller, purpose-
// built contract: no secondary_states/observable_indicators/full synthesis
// (indicators ship fully locked, zero content to carry -- Decision
// Register, this session), no dimension_summary (ConstellationField
// excluded from the condensed report, Pete's resolved decision), no
// friction_tax_estimate (a different mechanic -- get_industry_wage()-based
// financial_range instead). Built in web/app/api/diagnostic/condensed/
// answer/route.ts from CondensedCompleteResult (web/lib/engine-client.ts),
// same separation of concerns as PrivateOutputPayload's own route-builds-
// contract, component-renders-contract pattern.
// ---------------------------------------------------------------------------
export interface CondensedOutputPayload {
  primary_state: {
    id: string;
    name: string;
  };
  // Always "Emerging" in practice -- Category D's condensed session never
  // collects severity_inputs (Decision Register, this session), so
  // SeverityEngine always scores with zero inputs. Typed as the full
  // SeverityTier union for correctness, not narrowed to the literal, in
  // case that ever changes.
  severity: SeverityTier;
  resolution_family: ResolutionFamily;
  headline: string;
  // get_fallback_synthesis()'s liability_condition_text -- the condensed
  // report's one-paragraph verdict. Static, already-approved copy, not a
  // live synthesis call (Decision Register, this session).
  verdict_text: string;
  financial_range: {
    low: number | null;
    high: number | null;
    currency: "USD";
  };
}

// ---------------------------------------------------------------------------
// ShareableOutputPayload
// ---------------------------------------------------------------------------'''

# ---------------------------------------------------------------------------
# (5) web/lib/engine-client.ts -- invokeCondensedComplete()
# ---------------------------------------------------------------------------

OLD_CLIENT_ANCHOR = '''export async function invokeQuestionCopy(
'''

NEW_CLIENT_ANCHOR = '''export interface CondensedFinancialRange {
  low: number | null;
  high: number | null;
  currency: "USD";
}

// Category D (free condensed diagnostic), this session. Deliberately a
// much smaller payload than CompletePayload above -- no checkpoint_
// results/severity_inputs/answers_log, since the condensed session never
// collects any of them by design (web/lib/condensed-session-store.ts).
// intake is industry-only (CondensedIntake), not the full
// PrivateIntakeEcho -- nothing else the 9 selected questions' scoring or
// get_industry_wage() consumes.
export interface CondensedCompletePayload {
  accumulated_vector: AccumulatedVector;
  intake: { industry: string };
  answered_question_count: number;
}

export type CondensedCompleteResult = EngineResult & {
  condensed_financial_range: CondensedFinancialRange;
};

export async function invokeCondensedComplete(
  payload: CondensedCompletePayload,
): Promise<CondensedCompleteResult> {
  const response = await engineFetch(resolveEnginePath("/api/condensed-complete"), payload);

  if (!response.ok) {
    throw new Error(`Condensed complete invocation failed: ${response.status}`);
  }

  return response.json() as Promise<CondensedCompleteResult>;
}

export async function invokeQuestionCopy(
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    edits = [
        (FT_PATH, OLD_FT, NEW_FT, "friction_tax.py"),
        (MAIN_PATH, OLD_MAIN_IMPORTS, NEW_MAIN_IMPORTS, "main.py imports"),
        (MAIN_PATH, OLD_MAIN_ANCHOR, NEW_MAIN_ANCHOR, "main.py run_condensed_engine"),
        (API_PATH, OLD_API_IMPORTS, NEW_API_IMPORTS, "api/engine.py imports"),
        (API_PATH, OLD_API_ANCHOR, NEW_API_ANCHOR, "api/engine.py route"),
        (TYPES_PATH, OLD_TYPES_ANCHOR, NEW_TYPES_ANCHOR, "types.ts CondensedOutputPayload"),
        (CLIENT_PATH, OLD_CLIENT_ANCHOR, NEW_CLIENT_ANCHOR, "engine-client.ts"),
    ]

    contents = {}
    originals = {}
    for path, old, new, label in edits:
        if path not in contents:
            contents[path] = path.read_text(encoding="utf-8")
            originals[path] = contents[path]
        count = contents[path].count(old)
        if count != 1:
            print(f"FAIL ({label}): expected 1 match, found {count}")
            sys.exit(1)
        contents[path] = contents[path].replace(old, new, 1)

    for path in contents:
        diff = len(contents[path]) - len(originals[path])
        print(f"{path}: {diff:+d} chars")

    if args.write:
        for path, content in contents.items():
            path.write_text(content, encoding="utf-8")
        print("WRITTEN.")
    else:
        print("DRY RUN -- no files written. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
