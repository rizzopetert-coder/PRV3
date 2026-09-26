import { NextResponse } from "next/server";
import { completeSession, type DiagnosticSession } from "@/lib/session-store";
import { invokeComplete, invokeQuestionCopy } from "@/lib/engine-client";
import type {
  PrivateOutputPayload,
  StateRef,
  SynthesisFields,
  TacticalSectionResult,
} from "@/lib/types";
import {
  translateResolutionFamily,
  HR_DIAGNOSTIC_RESOLUTION_FAMILY,
} from "@/lib/resolution-family";
import { TACTICAL_QUESTION_META } from "@/data/tactical-question-meta";
import { getTacticalReferrals } from "@/data/tactical-referrals";

// hr-dx.com only. Resolves session.answers_log's TC-* entries into
// display-ready results, grouped by section. Fetches question_text/
// option_text live via invokeQuestionCopy() (one call per answered TC
// question, run concurrently) -- matches this codebase's standing
// principle that question copy is never hand-duplicated in TypeScript
// (get_question_copy()'s own docstring, engine/main.py). intent and
// question_set_id have no engine-side existence, so those come from the
// small TS-only lookup (web/data/tactical-question-meta.ts) instead.
export async function resolveTacticalResults(
  session: DiagnosticSession,
): Promise<TacticalSectionResult[] | undefined> {
  if (session.brand !== "hr_diagnostic") return undefined;

  const tacticalEntries = session.answers_log.filter((e) =>
    e.question_id.startsWith("TC-"),
  );
  if (tacticalEntries.length === 0) return undefined;

  const resolved = await Promise.all(
    tacticalEntries.map(async (entry) => {
      const meta = TACTICAL_QUESTION_META[entry.question_id];
      const copy = await invokeQuestionCopy(entry.question_id);
      const selectedOptionId = entry.option_ids[0];
      const selectedOptionText =
        copy.options.find((o) => o.option_id === selectedOptionId)?.option_text ??
        selectedOptionId;
      return {
        question_set_id: meta?.question_set_id ?? "unknown",
        intent: meta?.intent ?? "",
        result: {
          question_id: entry.question_id,
          question_text: copy.question_text,
          selected_option_text: selectedOptionText,
          intent: meta?.intent ?? "",
        },
      };
    }),
  );

  const bySection = new Map<string, TacticalSectionResult>();
  for (const { question_set_id, result } of resolved) {
    if (!bySection.has(question_set_id)) {
      bySection.set(question_set_id, {
        question_set_id,
        referral: getTacticalReferrals(question_set_id),
        answers: [],
      });
    }
    bySection.get(question_set_id)!.answers.push(result);
  }

  // Section order matches TACTICAL_QUESTION_META's own key insertion
  // order (the JSON's question_sets array order), not re-sorted.
  const sectionOrder = [
    ...new Set(Object.values(TACTICAL_QUESTION_META).map((m) => m.question_set_id)),
  ];
  return sectionOrder
    .map((id) => bySection.get(id))
    .filter((s): s is TacticalSectionResult => s !== undefined);
}

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
    // Pure Stateful Modulation with Completion Re-ranking (this
    // session's fix) -- see session-store.ts's own field comment.
    pre_narrative_vector: session.pre_narrative_vector ?? undefined,
    brand: session.brand,
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

  const isHrDiagnostic = session.brand === "hr_diagnostic";
  const rawRouting = engineResult.private_output.resolution_routing;

  const privatePayload: PrivateOutputPayload = {
    synthesis,

    primary_state: stateRefs[0],
    secondary_states: stateRefs.slice(1),

    severity: engineResult.severity.tier,
    severity_by_state: engineResult.severity.by_state,

    // hr_diagnostic: both fields are brand-safe display text -- PrivateOutput
    // renders resolution_routing raw as a fallback (Blocks 2/4, Copy
    // Results), so the raw engine name must not pass through either.
    // Empty routing stays empty, same as principal_resolution.
    resolution_family: isHrDiagnostic
      ? (rawRouting ? HR_DIAGNOSTIC_RESOLUTION_FAMILY : "")
      : translateResolutionFamily(rawRouting),
    resolution_routing: isHrDiagnostic
      ? (rawRouting ? HR_DIAGNOSTIC_RESOLUTION_FAMILY : "")
      : rawRouting,

    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,
    friction_tax_ledger: engineResult.private_output.friction_tax_ledger,
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

  const tacticalResults = await resolveTacticalResults(session);

  return NextResponse.json({
    status: "complete",
    result: privatePayload,
    ...(tacticalResults ? { tactical_results: tacticalResults } : {}),
  });
}
