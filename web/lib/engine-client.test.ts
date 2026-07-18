import { describe, it, expect } from "vitest";
import type { CompletePayload, CheckpointResultsBundle } from "./engine-client";
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
      },
      q19: { entropy: 1.1, threshold: 0.4, fires: false, distinguishers: [], top_cluster: null },
      q27: { entropy: 0.2, threshold: 0.2, fires: false, distinguishers: [], top_cluster: null },
    };
    const payload: CompletePayload = {
      accumulated_vector: ZERO_VECTOR,
      intake: BASE_INTAKE,
      answered_question_count: 34,
      checkpoint_results: bundle,
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
    };

    expect(payload.checkpoint_results.q11).toBeNull();
    expect(payload.checkpoint_results.q19).toBeNull();
    expect(payload.checkpoint_results.q27).toBeNull();
  });
});
