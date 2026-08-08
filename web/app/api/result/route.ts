import { NextRequest, NextResponse } from "next/server";
import type {
  PrivateOutputPayload,
  StateRef,
  IntakeEcho,
  SynthesisFields,
} from "@/lib/types";
import { invokeEngine } from "@/lib/engine-client";
import { translateResolutionFamily } from "@/lib/resolution-family";

// ---------------------------------------------------------------------------
// Payload separation contract:
//   PrivateOutput is returned to the browser. Never written to KV.
//   ShareableOutput is never constructed here.
//   No KV write of any kind occurs in this handler.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Weight computation
// Path B: equal weight (1 / n) for all selected states.
// Path A: normalized cosine scores.
// ---------------------------------------------------------------------------

function computeWeights(
  states: Array<{ id: string; name: string; score: number; descriptive_prose: string }>,
  path: "A" | "B"
): StateRef[] {
  if (states.length === 0) return [];
  if (path === "B") {
    const w = 1 / states.length;
    return states.map((s) => ({ id: s.id, name: s.name, weight: w, descriptive_prose: s.descriptive_prose }));
  }
  const total = states.reduce((sum, s) => sum + s.score, 0);
  return states.map((s) => ({
    id: s.id,
    name: s.name,
    weight: total > 0 ? s.score / total : 1 / states.length,
    descriptive_prose: s.descriptive_prose,
  }));
}

// ---------------------------------------------------------------------------
// Intake mapping — engine echo fields → IntakeEcho contract
// ---------------------------------------------------------------------------

// Never throws. Real headcount int passes through unchanged; a numeric
// string (defensive -- shouldn't occur from the Python side, but the web
// boundary shouldn't trust that) parses to a number; a legacy bucket
// string ("100-249") is not numeric and passes through as-is; missing/
// null falls back to "".
function parseOrgSize(value: unknown): string | number {
  if (typeof value === "number") return value;
  if (value === null || value === undefined) return "";
  if (typeof value === "string") {
    const parsed = Number(value);
    return value.trim() !== "" && Number.isFinite(parsed) ? parsed : value;
  }
  return "";
}

function mapIntake(engineIntake: Record<string, unknown>): IntakeEcho {
  const jurisdictions = Array.isArray(engineIntake.jurisdictions)
    ? (engineIntake.jurisdictions as string[])
    : [];
  const significantEvents = Array.isArray(engineIntake.significant_events)
    ? (engineIntake.significant_events as string[])
    : ["none"];
  return {
    // headcount is the real Python IntakeData field; org_size is a
    // fallback for any caller still on the pre-Phase-1 engine shape.
    organization_size: parseOrgSize(engineIntake.headcount ?? engineIntake.org_size),
    industry: (engineIntake.industry as string) ?? "",
    role_level: (engineIntake.principal_role as string) ?? "",
    tenure_in_role: "",
    direct_reports: "",
    jurisdiction: jurisdictions[0] ?? "",
    significant_events: significantEvents,
  };
}


// ---------------------------------------------------------------------------
// Request schema
// ---------------------------------------------------------------------------

interface ResultRequest {
  selectedStateIds: string[];
  intake: {
    headcount: string;
    industry: string;
    orgType: string;
    jurisdictions: string[];
    significantEvents: string[];
    principalRole: string;
  };
}

function validateRequest(body: unknown): body is ResultRequest {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    Array.isArray(b.selectedStateIds) &&
    b.selectedStateIds.every((id) => typeof id === "string") &&
    typeof b.intake === "object" &&
    b.intake !== null
  );
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!validateRequest(body)) {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  const { selectedStateIds, intake } = body;

  const engineResult = await invokeEngine({ selectedStateIds, intake });

  const allEngineStates = engineResult.identified_states;
  if (allEngineStates.length === 0) {
    return NextResponse.json({ error: "Engine returned no states" }, { status: 500 });
  }

  const stateRefs = computeWeights(
    allEngineStates.map((s) => ({
      id: s.state_id,
      name: s.state_name,
      score: s.score,
      descriptive_prose: s.descriptive_prose,
    })),
    "B"
  );

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

    resolution_family: translateResolutionFamily(engineResult.private_output.resolution_routing),
    // resolution_routing: legacy service-name string from states.py profile (old naming, pre-S32)
    resolution_routing: engineResult.private_output.resolution_routing,

    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,
    legal_tail_risk_exposure: engineResult.private_output.legal_tail_risk_exposure,

    // causation_pattern -- new plumbing this build. Confirmed real,
    // computed value on Path B (Round 2/3 verification: driven entirely by
    // qualified_state_count when accumulated_vector={}, single_point/diffuse
    // are the common case, not just insufficient_signal).
    causation_pattern: engineResult.private_output.causation_pattern,

    intake: mapIntake(engineResult.intake as Record<string, unknown>),

    dimension_summary: engineResult.dimension_summary,
    primary_asset_domain: engineResult.asset_score.primary_asset_domain,
  };

  // ShareableOutput is NEVER serialized into this response.
  return NextResponse.json(privatePayload);
}
