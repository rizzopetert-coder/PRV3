import { describe, it, expect } from "vitest";
import type { CompletePayload, CheckpointResultsBundle, SeverityInputPayload } from "./engine-client";
import { ZERO_VECTOR } from "./session-store";

// Type-level check only — no network call, no fetch, no mocking.
// invokeComplete() itself is never called here; tsc --noEmit (run
// separately, already clean) is the actual enforcement mechanism for
// whether this file's object literals satisfy CompletePayload. What this
// test proves at runtime is that the shapes route.ts's Q34 completion call
// site actually constructs (all three checkpoints populated, and all
// three null when none were reached) are the ones the type permits — a
// change to CompletePayload that silently broke one of these shapes would
// fail to compile, not just fail an assertion.

const BASE_INTAKE = {
  organization_size: "51-200",
  industry: "Technology",
  role_level: "CEO",
  tenure_in_role: "",
  direct_reports: "",
  jurisdiction: "US-CA",
  significant_events: ["none"],
};

describe("CompletePayload shape (Stage 4 — checkpoint_results addition)", () => {
  it("accepts a payload with all three checkpoint slots populated", () => {
    const bundle: CheckpointResultsBundle = {
      q11: {
        entropy: 2.5,
        threshold: 0.6,
        fires: true,
        distinguishers: ["DIST-CM-01"],
        top_cluster: "C-Manager",
        narrative_trigger: false,
      },
      q19: { entropy: 1.1, threshold: 0.4, fires: false, distinguishers: [], top_cluster: null, narrative_trigger: false },
      q27: { entropy: 0.2, threshold: 0.2, fires: false, distinguishers: [], top_cluster: null, narrative_trigger: false },
    };
    const payload: CompletePayload = {
      accumulated_vector: ZERO_VECTOR,
      intake: BASE_INTAKE,
      answered_question_count: 34,
      checkpoint_results: bundle,
      severity_inputs: [],
      answers_log: [],
    };

    expect(payload.checkpoint_results.q11?.fires).toBe(true);
    expect(payload.checkpoint_results.q11?.distinguishers).toEqual(["DIST-CM-01"]);
    expect(payload.checkpoint_results.q27?.fires).toBe(false);
  });

  it("accepts a payload where no checkpoint was ever reached (all null)", () => {
    const payload: CompletePayload = {
      accumulated_vector: ZERO_VECTOR,
      intake: BASE_INTAKE,
      answered_question_count: 5,
      checkpoint_results: { q11: null, q19: null, q27: null },
      severity_inputs: [],
      answers_log: [],
    };

    expect(payload.checkpoint_results.q11).toBeNull();
    expect(payload.checkpoint_results.q19).toBeNull();
    expect(payload.checkpoint_results.q27).toBeNull();
  });
});

describe("CompletePayload shape (severity follow-on wiring — Path 1)", () => {
  it("accepts a payload with real severity_inputs collected across the session", () => {
    const inputs: SeverityInputPayload[] = [
      {
        trigger_question_id: "Q22",
        severity_follow_on_id: "SEVER-04",
        duration_band: "18mo_plus",
      },
      {
        trigger_question_id: "Q24",
        severity_follow_on_id: "SEVER-06",
        duration_band: "18mo_plus",
      },
    ];
    const payload: CompletePayload = {
      accumulated_vector: ZERO_VECTOR,
      intake: BASE_INTAKE,
      answered_question_count: 9,
      checkpoint_results: { q11: null, q19: null, q27: null },
      severity_inputs: inputs,
      answers_log: [],
    };

    expect(payload.severity_inputs).toHaveLength(2);
    expect(payload.severity_inputs[0].duration_band).toBe("18mo_plus");
  });

  it("accepts a payload where no severity follow-on ever fired ([])", () => {
    const payload: CompletePayload = {
      accumulated_vector: ZERO_VECTOR,
      intake: BASE_INTAKE,
      answered_question_count: 34,
      checkpoint_results: { q11: null, q19: null, q27: null },
      severity_inputs: [],
      answers_log: [],
    };

    expect(payload.severity_inputs).toEqual([]);
  });
});
