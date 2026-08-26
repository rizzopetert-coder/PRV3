import { NextResponse } from "next/server";
import { completeSession, type DiagnosticSession } from "@/lib/session-store";
import { invokeComplete } from "@/lib/engine-client";
import type {
  PrivateOutputPayload,
  StateRef,
  SynthesisFields,
} from "@/lib/types";
import { translateResolutionFamily } from "@/lib/resolution-family";

// ---------------------------------------------------------------------------
// Shared completion path -- extracted from session/answer/route.ts's own
// completion branch (Narrative modulation, Phase 3, this session), since
// the same sequence (invokeComplete -> weighting -> synthesis ->
// PrivateOutputPayload -> completeSession) is now needed from TWO call
// sites: session/answer's own last-question branch (narrative already
// fired earlier, at Q27), and session/narrative's completion path
// (narrative just fired as the standard/end-of-sequence trigger).
// Genuinely new code authored in two places at once, not a refactor of
// already-shipped adjacent code -- extracting at time of authoring avoids
// duplicating this block rather than un-duplicating it later.
//
// Threads session.narrative_* fields into CompletePayload whenever
// narrative fired this session (all six left undefined otherwise,
// preserving the exact pre-narrative payload shape for any session that
// never triggers it) -- so assemble_output()'s narrative_modulation
// output block reports real values, not defaults.
// ---------------------------------------------------------------------------

export async function completeDiagnosticSession(
  session: DiagnosticSession,
): Promise<NextResponse> {
  const engineResult = await invokeComplete({
    accumulated_vector: session.accumulated_vector,
    intake: session.intake,
    answered_question_count: session.answers_log.length,
    checkpoint_results: {
      q11: session.checkpoint_q11,
      q19: session.checkpoint_q19,
      q27: session.checkpoint_q27,
    },
    severity_inputs: session.severity_inputs,
    answers_log: session.answers_log,
    narrative_response: session.narrative_fired ? session.narrative_response : undefined,
    narrative_severity_addition: session.narrative_fired ? session.narrative_severity_addition : undefined,
    narrative_trigger_point: session.narrative_trigger_point ?? undefined,
    narrative_overall_confidence: session.narrative_fired ? session.narrative_overall_confidence : undefined,
    narrative_signals_count: session.narrative_fired ? session.narrative_signals_count : undefined,
    pre_narrative_rankings: session.pre_narrative_rankings ?? undefined,
    post_narrative_rankings: session.post_narrative_rankings ?? undefined,
  });

  const allEngineStates = engineResult.identified_states;
  if (allEngineStates.length === 0) {
    return NextResponse.json({ error: "Engine returned no states" }, { status: 500 });
  }

  // Path A weighting — real normalized cosine scores, not Path B's equal
  // weight. Mirrors the doc comment already on StateRef in web/lib/types.ts:
  // "Path A (full diagnostic): weight = score_i / sum(all_returned_scores)".
  const totalScore = allEngineStates.reduce((sum, s) => sum + s.score, 0);
  const stateRefs: StateRef[] = allEngineStates.map((s) => ({
    id: s.state_id,
    name: s.state_name,
    weight: totalScore > 0 ? s.score / totalScore : 1 / allEngineStates.length,
    descriptive_prose: s.descriptive_prose,
  }));

  const engSynthesis = engineResult.synthesis;
  const synthesis: SynthesisFields = engSynthesis
    ? {
        liability_condition_text:     engSynthesis.liability_condition_text,
        asset_resolution_anchor_text: engSynthesis.asset_resolution_anchor_text,
        framing_text:                 engSynthesis.framing_text,
        observable_indicators:        engSynthesis.observable_indicators,
        resolution_framing_text:      engSynthesis.resolution_framing_text,
        headline:                     engSynthesis.headline,
        synthesis_confidence:         engSynthesis.synthesis_confidence,
        is_fallback:                  engSynthesis.is_fallback,
      }
    : {
        liability_condition_text:     "",
        asset_resolution_anchor_text: "",
        framing_text:                 "",
        observable_indicators:        [],
        resolution_framing_text:      "",
        headline:                     "",
        synthesis_confidence:         0.0,
        is_fallback:                  true,
      };

  const privatePayload: PrivateOutputPayload = {
    synthesis,

    primary_state: stateRefs[0],
    secondary_states: stateRefs.slice(1),

    severity: engineResult.severity.tier,
    severity_by_state: engineResult.severity.by_state,

    resolution_family: translateResolutionFamily(engineResult.private_output.resolution_routing),
    resolution_routing: engineResult.private_output.resolution_routing,

    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,
    legal_tail_risk_exposure: engineResult.private_output.legal_tail_risk_exposure,

    cascade_risk: engineResult.private_output.cascade_risk,
    causation_pattern: engineResult.private_output.causation_pattern,
    trajectory: engineResult.private_output.trajectory,
    urgency_window: engineResult.private_output.urgency_window,

    intake: session.intake,

    dimension_summary: engineResult.dimension_summary,
    primary_asset_domain: engineResult.asset_score.primary_asset_domain,
  };

  // Transition Rule — strips identifiable data the moment status becomes
  // complete. session itself is never marked "complete" and re-saved; it
  // is deleted outright inside completeSession().
  await completeSession(
    session,
    stateRefs.map((s) => ({ id: s.id, name: s.name, weight: s.weight })),
  );

  return NextResponse.json({ status: "complete", result: privatePayload });
}
