import { describe, it, expect, vi, beforeEach } from "vitest";

// ---------------------------------------------------------------------------
// completeDiagnosticSession() brand handling (items F/I/J). hr_diagnostic
// payloads must carry no PR tier name in resolution_family or the raw
// resolution_routing fallback, and must send brand to the engine so the AI
// synthesis is brand-safe too. principal_resolution must be unchanged.
// Local Path 1 completion is blocked (no Upstash credentials locally, see
// diagnostic-completion.test.ts's header), so this proves the assembly
// logic directly; the live round-trip is owed on a Preview deploy.
// ---------------------------------------------------------------------------

const mockInvokeComplete = vi.fn();

vi.mock("@/lib/engine-client", () => ({
  invokeComplete: (...args: unknown[]) => mockInvokeComplete(...args),
  invokeQuestionCopy: vi.fn(),
}));

vi.mock("@/lib/session-store", () => ({
  completeSession: vi.fn(),
}));

import { completeDiagnosticSession } from "@/lib/diagnostic-completion";
import type { DiagnosticSession } from "@/lib/session-store";

const PR_TERMS = [
  "People Tactics", "Training & Development", "First Call", "Executive Advisory",
  "Principal Resolution", "Roadmap", "Intervention", "Executive Counsel",
];

const ZERO_VECTOR = {
  aptitude_liability: 0, aptitude_asset: 0,
  authority_liability: 0, authority_asset: 0,
  alliance_liability: 0, alliance_asset: 0,
  attitude_liability: 0, attitude_asset: 0,
};

function session(brand: DiagnosticSession["brand"]): DiagnosticSession {
  return {
    session_id: "t", brand, intake: {} as DiagnosticSession["intake"], next_question_id: "Q01",
    accumulated_vector: { ...ZERO_VECTOR }, answers_log: [], status: "in_progress",
    checkpoint_q11: null, checkpoint_q19: null, checkpoint_q27: null, question_sequence: [],
    severity_inputs: [], severity_follow_on_origins: {}, question_labels: {},
    narrative_fired: false, narrative_response: "", narrative_severity_addition: 0,
    narrative_trigger_point: null, narrative_overall_confidence: 0, narrative_signals_count: 0,
    pre_narrative_vector: null, pending_narrative_prompt: null, pending_completion: false,
  };
}

function engineResult(routing: string, withSynthesis: boolean) {
  return {
    identified_states: [{ state_id: "the_founders_grip", state_name: "The Founder's Grip", score: 1, descriptive_prose: "" }],
    synthesis: withSynthesis
      ? {
          liability_condition_text: "l", asset_resolution_anchor_text: "a", framing_text: "f",
          observable_indicators: [], resolution_framing_text: "r", headline: "h",
          synthesis_confidence: 1, is_fallback: false,
        }
      : null,
    severity: { tier: "Entrenched", by_state: {} },
    private_output: {
      resolution_routing: routing, friction_tax_estimate: null, friction_tax_ledger: null,
      legal_tail_risk_exposure: null, cascade_risk: null, causation_pattern: null,
      trajectory: null, urgency_window: null,
    },
    dimension_summary: {},
    asset_score: { primary_asset_domain: null },
  };
}

async function run(brand: DiagnosticSession["brand"], routing: string, withSynthesis = true) {
  mockInvokeComplete.mockResolvedValueOnce(engineResult(routing, withSynthesis));
  const res = await completeDiagnosticSession(session(brand));
  return (await res.json()).result;
}

describe("completeDiagnosticSession brand handling", () => {
  beforeEach(() => mockInvokeComplete.mockReset());

  const ROUTINGS = ["Roadmap", "Development", "Intervention", "Executive Counsel",
    "Intervention + Executive Counsel", "Roadmap + Intervention", "Development + Roadmap"];

  for (const routing of ROUTINGS) {
    it(`hr_diagnostic [${routing}]: resolution_family and resolution_routing are "HR Consulting"`, async () => {
      const result = await run("hr_diagnostic", routing, false);
      expect(result.resolution_family).toBe("HR Consulting");
      expect(result.resolution_routing).toBe("HR Consulting");
      const blob = `${result.resolution_family} ${result.resolution_routing}`;
      for (const t of PR_TERMS) expect(blob).not.toContain(t);
    });
  }

  it("hr_diagnostic: empty routing stays empty (same as principal_resolution)", async () => {
    const result = await run("hr_diagnostic", "");
    expect(result.resolution_family).toBe("");
    expect(result.resolution_routing).toBe("");
  });

  it("sends brand to the engine for both brands", async () => {
    await run("hr_diagnostic", "Intervention");
    expect(mockInvokeComplete.mock.calls[0][0].brand).toBe("hr_diagnostic");
    await run("principal_resolution", "Intervention");
    expect(mockInvokeComplete.mock.calls[1][0].brand).toBe("principal_resolution");
  });

  it("principal_resolution unchanged: translated family, raw routing", async () => {
    const result = await run("principal_resolution", "Intervention + Roadmap");
    expect(result.resolution_family).toBe("First Call + People Tactics & Strategy");
    expect(result.resolution_routing).toBe("Intervention + Roadmap");
  });
});
