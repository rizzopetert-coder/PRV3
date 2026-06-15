const ENGINE_SECRET = process.env.ENGINE_SECRET ?? "";

function resolveEngineUrl(): string {
  if (process.env.ENGINE_URL) {
    return process.env.ENGINE_URL;
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}/api/engine`;
  }
  return "http://localhost:3000/api/engine";
}

export interface EnginePayload {
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

export interface EngineResult {
  session_id: string;
  intake: Record<string, unknown>;
  state_distribution: Array<{
    state_id: string;
    state_name: string;
    score: number;
    rank: number;
    above_floor: boolean;
  }>;
  output_type: "single_state" | "multi_state" | "no_signal";
  identified_states: Array<{
    state_id: string;
    state_name: string;
    score: number;
    distinguishing_language: string | null;
  }>;
  severity: {
    tier: "Emerging" | "Entrenched" | "Endemic";
    score: number;
    anchor_text: string;
    inputs: Record<string, unknown>;
  };
  asset_score: {
    score: number;
    primary_asset_domain: string;
    resolution_anchor_text: string;
  };
  narrative_modulation: {
    fired: boolean;
    trigger_point: string | null;
    overall_confidence: number;
    signals_extracted: number;
    state_delta: number;
    severity_delta: number;
  };
  checkpoint_log: Record<string, unknown>;
  jurisdiction_flags: Record<string, unknown>;
  private_output: {
    opening_text: string;
    resolution_routing: string;
    friction_tax_estimate: number | null;
  };
  shareable_output: {
    attribution_text: string;
  };
  synthesis: {
    liability_condition_text:     string;
    asset_resolution_anchor_text: string;
    framing_text:                 string;
    observable_indicators:        string[];
    resolution_framing_text:      string;
    synthesis_confidence:         number;
    is_fallback:                  boolean;
  } | null;
  engine_version: string;
  monitoring_metadata: Record<string, unknown>;
}

export async function invokeEngine(payload: EnginePayload): Promise<EngineResult> {
  const url = resolveEngineUrl();

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-engine-secret": ENGINE_SECRET,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Engine invocation failed: ${response.status}`);
  }

  return response.json() as Promise<EngineResult>;
}
