import { NextRequest, NextResponse } from "next/server";
import type { PrivateOutputPayload } from "@/lib/output-renderer";

// ---------------------------------------------------------------------------
// Payload shape — PrivateOutput only
// ShareableOutput is NEVER serialized into this response.
// ---------------------------------------------------------------------------

interface ResultRequest {
  sessionId: string;
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
    typeof b.sessionId === "string" &&
    Array.isArray(b.selectedStateIds) &&
    b.selectedStateIds.every((id) => typeof id === "string") &&
    typeof b.intake === "object" &&
    b.intake !== null
  );
}

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

  // TODO(S39): Call PRV3 scoring engine to produce ranked state output.
  // Engine call returns the full contract VII.1 output. Extract only
  // the private_output fields for serialization here.
  // ShareableOutput is assembled separately and never returned here.

  const privatePayload: PrivateOutputPayload = {
    sessionId: body.sessionId,
    outputType:
      body.selectedStateIds.length === 0
        ? "no_signal"
        : body.selectedStateIds.length === 1
          ? "single_state"
          : "multi_state",
    identifiedStates: body.selectedStateIds.map((id, i) => ({
      state_id: id,
      state_name: id,        // TODO(S39): resolve state_name from engine output
      score: 1.0 - i * 0.1, // TODO(S39): replace with engine scores
      distinguishing_language: null,
    })),
    severity: {
      tier: "Entrenched",             // TODO(S39): from engine severity_result
      score: 50,                      // TODO(S39): from engine severity_result
      anchor_text: "COPY PENDING",    // TODO(S39): from engine severity_result
    },
    privateOutput: {
      opening_text: "COPY PENDING",       // TODO(S39): from engine private_output
      liability_block: "COPY PENDING",    // TODO(S39): LLM-generated
      asset_anchor_text: "COPY PENDING",  // TODO(S39): LLM-generated
      resolution_routing: "structural",   // TODO(S39): from resolution_families.py
      friction_tax_estimate: null,        // TODO(S39): from compute_friction_tax()
    },
    // synthesis populated async — not included in initial response
    // Pass 1 synthesis arrives via a separate request or SSE
  };

  // ShareableOutput is NEVER serialized into this response.
  return NextResponse.json(privatePayload);
}
