import { describe, it, expect, vi } from "vitest";

// ---------------------------------------------------------------------------
// resolveTacticalResults() (HRdiagnostic.com only), this session.
//
// Substitutes for a genuine live end-to-end session completion, which is
// currently blocked in this local environment: .env.local's own comment
// documents that UPSTASH_REDIS_REST_URL/TOKEN were deliberately removed
// locally after a `vercel env pull` left a broken [SENSITIVE] placeholder --
// "absent is the working local state." That blocks ANY session locally
// (hr_diagnostic or not), not something this feature introduced. Rather
// than inject Redis credentials into a shared instance without knowing
// whether a genuinely separate dev/test instance exists, this test proves
// the actual new logic -- section grouping, referral attachment, intent
// wiring -- directly and permanently, following this suite's own established
// mocking convention (session/undo/route.test.ts: fake @upstash/redis,
// mocked @/lib/engine-client). A real HTTP round-trip check is still owed
// before this ships -- see the session's own report -- on a Vercel preview
// deploy where real env vars exist, not deferred indefinitely.
//
// question_text/option_text below are copied verbatim from
// tactical-compliance-questions-schema-compliant.json (TC-HRPOL-01 and
// TC-HIRE-01, the real first questions of two different sections) --
// not invented copy, matching this suite's existing "not invented numbers"
// discipline for mocked engine responses.
// ---------------------------------------------------------------------------

const mockInvokeQuestionCopy = vi.fn();

vi.mock("@/lib/engine-client", () => ({
  invokeComplete: vi.fn(),
  invokeQuestionCopy: (...args: unknown[]) => mockInvokeQuestionCopy(...args),
}));

vi.mock("@/lib/session-store", () => ({
  completeSession: vi.fn(),
}));

import { resolveTacticalResults } from "@/lib/diagnostic-completion";
import type { DiagnosticSession } from "@/lib/session-store";

const ZERO_VECTOR = {
  aptitude_liability: 0, aptitude_asset: 0,
  authority_liability: 0, authority_asset: 0,
  alliance_liability: 0, alliance_asset: 0,
  attitude_liability: 0, attitude_asset: 0,
};

function baseSession(overrides: Partial<DiagnosticSession>): DiagnosticSession {
  return {
    session_id: "test",
    brand: "principal_resolution",
    intake: {} as DiagnosticSession["intake"],
    next_question_id: "TC-HRPOL-01",
    accumulated_vector: { ...ZERO_VECTOR },
    answers_log: [],
    status: "in_progress",
    checkpoint_q11: null,
    checkpoint_q19: null,
    checkpoint_q27: null,
    question_sequence: [],
    severity_inputs: [],
    severity_follow_on_origins: {},
    question_labels: {},
    narrative_fired: false,
    narrative_response: "",
    narrative_severity_addition: 0,
    narrative_trigger_point: null,
    narrative_overall_confidence: 0,
    narrative_signals_count: 0,
    pre_narrative_vector: null,
    pending_narrative_prompt: null,
    pending_completion: false,
    ...overrides,
  };
}

describe("resolveTacticalResults", () => {
  it("returns undefined for principal_resolution sessions regardless of answers_log", async () => {
    const session = baseSession({
      brand: "principal_resolution",
      answers_log: [{ question_id: "TC-HRPOL-01", option_ids: ["A"] }],
    });
    const result = await resolveTacticalResults(session);
    expect(result).toBeUndefined();
    expect(mockInvokeQuestionCopy).not.toHaveBeenCalled();
  });

  it("returns undefined for hr_diagnostic sessions with no TC-* answers", async () => {
    const session = baseSession({
      brand: "hr_diagnostic",
      answers_log: [{ question_id: "Q01", option_ids: ["A"] }],
    });
    const result = await resolveTacticalResults(session);
    expect(result).toBeUndefined();
  });

  it("groups TC-* answers by section, attaches referral and intent, preserves section order", async () => {
    mockInvokeQuestionCopy.mockImplementation(async (questionId: string) => {
      if (questionId === "TC-HRPOL-01") {
        return {
          question_id: "TC-HRPOL-01",
          question_text:
            "When was your employee handbook last substantively revised -- not reformatted, actually reviewed against current law and current practice?",
          format: "forced_choice",
          options: [
            { option_id: "A", option_text: "Reviewed and revised within the past 12 months, against current law." },
            { option_id: "B", option_text: "Reviewed within the past 1-3 years, but not specifically against current law." },
            { option_id: "C", option_text: "Formatted or lightly edited since then, but not substantively reviewed." },
            { option_id: "D", option_text: "Not sure when it was last genuinely reviewed." },
          ],
        };
      }
      if (questionId === "TC-HIRE-01") {
        return {
          question_id: "TC-HIRE-01",
          question_text:
            "How much of your interview process is actually structured -- consistent questions, consistent scoring -- versus left to whoever's in the room that day?",
          format: "forced_choice",
          options: [
            { option_id: "A", option_text: "Fully structured -- consistent questions and scoring across every candidate." },
            { option_id: "B", option_text: "Structured for some roles, informal for others." },
            { option_id: "C", option_text: "Loosely guided, but mostly left to whoever's interviewing." },
            { option_id: "D", option_text: "No structure -- entirely up to the interviewer." },
          ],
        };
      }
      throw new Error(`unexpected questionId in test: ${questionId}`);
    });

    // Answered out of section order (HIRE before HRPOL) to prove output
    // order follows TACTICAL_QUESTION_META's section order, not
    // answers_log's order.
    const session = baseSession({
      brand: "hr_diagnostic",
      answers_log: [
        { question_id: "TC-HIRE-01", option_ids: ["C"] },
        { question_id: "TC-HRPOL-01", option_ids: ["D"] },
      ],
    });

    const result = await resolveTacticalResults(session);

    expect(result).toBeDefined();
    expect(result!.map((s) => s.question_set_id)).toEqual([
      "TC-HR_POLICIES",
      "TC-HIRING_ONBOARDING",
    ]);

    const hrPolicies = result!.find((s) => s.question_set_id === "TC-HR_POLICIES")!;
    expect(hrPolicies.referral).toEqual(["HR Consulting", "HR Compliance Consulting"]);
    expect(hrPolicies.answers).toHaveLength(1);
    expect(hrPolicies.answers[0]).toMatchObject({
      question_id: "TC-HRPOL-01",
      selected_option_text: "Not sure when it was last genuinely reviewed.",
    });
    expect(hrPolicies.answers[0].intent).toBeTruthy();

    const hiring = result!.find((s) => s.question_set_id === "TC-HIRING_ONBOARDING")!;
    expect(hiring.referral).toEqual(["HR Consulting", "Talent Acquisition", "Recruiting"]);
    expect(hiring.answers[0]).toMatchObject({
      question_id: "TC-HIRE-01",
      selected_option_text: "Loosely guided, but mostly left to whoever's interviewing.",
    });
  });
});
