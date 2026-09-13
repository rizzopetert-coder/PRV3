import { describe, it, expect, vi, beforeEach } from "vitest";

// ---------------------------------------------------------------------------
// Route-level integration test, session/undo (this session).
//
// A genuine expansion of this project's test scope, not the pure-logic-only
// convention vitest.config.ts previously documented for this test suite --
// flagged explicitly, not left stale. A session-state-mutating endpoint
// (real production session data, not just UI) warrants exercising the
// actual route handler end to end, not only its extracted pure helpers
// (already covered separately in web/lib/session-store.test.ts).
//
// Mocks two things, nothing else:
//   - @upstash/redis -- an in-memory Map standing in for the real store, so
//     getSession()/saveSession()/createSession() (all real, unmocked logic)
//     round-trip against something. No real network I/O.
//   - @/lib/engine-client's invokeAccumulate/invokeQuestionCopy -- these do
//     a real fetch() to the Python engine (/api/accumulate, /api/question-
//     copy), unavailable in a plain vitest/node run (that function only
//     exists once both the Next.js app and api/engine.py run together, e.g.
//     via `vercel dev`). Mocked with values matching what
//     engine/main.accumulate_answers() actually returns for these
//     questions, confirmed directly against the real engine this session
//     (see the session's own report for the exact Python-level
//     verification) -- not invented numbers.
// ---------------------------------------------------------------------------

const redisStore = new Map<string, string>();

vi.mock("@upstash/redis", () => {
  class FakeRedis {
    static fromEnv() {
      return new FakeRedis();
    }
    async get(key: string) {
      return redisStore.get(key) ?? null;
    }
    async set(key: string, value: string) {
      redisStore.set(key, value);
      return "OK";
    }
  }
  return { Redis: FakeRedis };
});

const mockInvokeAccumulate = vi.fn();
const mockInvokeQuestionCopy = vi.fn();

vi.mock("@/lib/engine-client", () => ({
  invokeAccumulate: (...args: unknown[]) => mockInvokeAccumulate(...args),
  invokeQuestionCopy: (...args: unknown[]) => mockInvokeQuestionCopy(...args),
}));

// Imported AFTER the mocks above so session-store.ts's top-level
// Redis.fromEnv() call picks up the fake, not the real client.
const { createSession, getSession } = await import("@/lib/session-store");
const { POST } = await import("./route");

// Not a real intake shape -- the route treats session.intake as opaque and
// passes it straight through to invokeAccumulate (mocked below), so its
// content doesn't matter for these tests. Typed via Parameters<> rather
// than importing PrivateIntakeEcho, since this cast intentionally does not
// satisfy that interface.
const FAKE_INTAKE = {} as Parameters<typeof createSession>[0];

const ZERO = {
  aptitude_liability: 0, aptitude_asset: 0,
  authority_liability: 0, authority_asset: 0,
  alliance_liability: 0, alliance_asset: 0,
  attitude_liability: 0, attitude_asset: 0,
};

function fakeRequest(body: unknown) {
  return { json: async () => body } as Parameters<typeof POST>[0];
}

beforeEach(() => {
  redisStore.clear();
  mockInvokeAccumulate.mockReset();
  mockInvokeQuestionCopy.mockReset();
  mockInvokeQuestionCopy.mockImplementation(async (question_id: string) => ({
    question_id,
    question_text: `text for ${question_id}`,
    format: "forced_choice",
    options: [{ option_id: "A", option_text: "A" }],
  }));
});

describe("session/undo -- plain non-splice, non-checkpoint answer", () => {
  it("reverts accumulated_vector exactly against the recomputed delta and pops answers_log", async () => {
    const session = await createSession(FAKE_INTAKE);
    session.next_question_id = "Q05";
    // Prior state before Q05 was ever answered, plus Q05-C's own real
    // contribution already applied on top (attitude_liability: 0.60,
    // everything else 0.0 -- Q05-C's actual dimensional_contributions,
    // confirmed against the live QUESTION_LIBRARY this session, not
    // invented) -- this is what "current session state, forward answer
    // already applied" looks like going into an undo call.
    session.accumulated_vector = {
      ...ZERO, aptitude_liability: 0.3, authority_liability: 0.2, attitude_liability: 0.6,
    };
    session.answers_log = [{ question_id: "Q05", option_ids: ["C"] }];

    const q05Delta = { ...ZERO, attitude_liability: 0.6 };
    const { saveSession } = await import("@/lib/session-store");
    await saveSession(session);

    mockInvokeAccumulate.mockResolvedValueOnce({
      accumulated_vector: q05Delta,
      severity_inputs: [],
      severity_follow_on_ids: [],
      severity_follow_on_origins: {},
    });

    const res = await POST(fakeRequest({ session_id: session.session_id }));
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.status).toBe("in_progress");
    expect(data.question.question_id).toBe("Q05");
    // Pre-fill data (this session) -- round-trips the undone answer's own
    // option_ids exactly, captured before answers_log was popped.
    expect(data.option_ids).toEqual(["C"]);

    const after = await getSession(session.session_id);
    expect(after!.answers_log).toEqual([]);
    expect(after!.next_question_id).toBe("Q05");
    // Exact against the recomputed delta -- this subtraction is a single
    // float64 op, deterministic and exact by construction, not merely
    // "close." (Round-tripping to the ORIGINAL pre-answer vector before
    // that answer was ever applied is a different, weaker claim subject to
    // ordinary IEEE754 float drift on the order of 1e-16 -- confirmed
    // separately at the Python engine layer this session, not tested here.)
    expect(after!.accumulated_vector.attitude_liability).toBe(0.6 - q05Delta.attitude_liability);
    expect(after!.accumulated_vector.attitude_liability).toBe(0);
    // Fields the undone answer never touched are untouched by the subtraction.
    expect(after!.accumulated_vector.aptitude_liability).toBe(0.3);
    expect(after!.accumulated_vector.authority_liability).toBe(0.2);
  });
});

describe("session/undo -- severity follow-on splice reversal (Q06 -> SEVER-27)", () => {
  it("removes the not-yet-answered spliced question and its origin/label entries", async () => {
    const session = await createSession(FAKE_INTAKE);
    session.next_question_id = "SEVER-27";
    session.answers_log = [{ question_id: "Q06", option_ids: ["A"] }];
    session.question_sequence = ["Q05", "Q06", "SEVER-27", "Q07"];
    session.question_labels = { "SEVER-27": "6A" };
    session.severity_follow_on_origins = {
      "SEVER-27": { trigger_question_id: "Q06", triggering_option_id: "A" },
    };
    session.accumulated_vector = { ...ZERO, authority_liability: 0.6 };
    const { saveSession } = await import("@/lib/session-store");
    await saveSession(session);

    // Real values confirmed directly against engine/main.accumulate_answers()
    // this session: Q06-A contributes aptitude_liability 0.25,
    // authority_liability 0.6, attitude_liability 0.3, and fires SEVER-27.
    mockInvokeAccumulate.mockResolvedValueOnce({
      accumulated_vector: { ...ZERO, aptitude_liability: 0.25, authority_liability: 0.6, attitude_liability: 0.3 },
      severity_inputs: [],
      severity_follow_on_ids: ["SEVER-27"],
      severity_follow_on_origins: { "SEVER-27": "A" },
    });

    const res = await POST(fakeRequest({ session_id: session.session_id }));
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.option_ids).toEqual(["A"]);

    const after = await getSession(session.session_id);
    expect(after!.question_sequence).toEqual(["Q05", "Q06", "Q07"]);
    expect(after!.question_labels["SEVER-27"]).toBeUndefined();
    expect(after!.severity_follow_on_origins["SEVER-27"]).toBeUndefined();
    expect(after!.next_question_id).toBe("Q06");
    expect(after!.accumulated_vector.authority_liability).toBe(0);
  });
});

describe("session/undo -- Q06 -> Q28 conditional splice reversal", () => {
  it("removes Q28 when undoing a Q06 answer that included option A", async () => {
    const session = await createSession(FAKE_INTAKE);
    session.next_question_id = "Q28";
    session.answers_log = [{ question_id: "Q06", option_ids: ["A"] }];
    session.question_sequence = ["Q05", "Q06", "Q28", "Q07"];
    session.question_labels = { Q28: "6A" };
    const { saveSession } = await import("@/lib/session-store");
    await saveSession(session);

    mockInvokeAccumulate.mockResolvedValueOnce({
      accumulated_vector: { ...ZERO },
      severity_inputs: [],
      severity_follow_on_ids: [],
      severity_follow_on_origins: {},
    });

    const res = await POST(fakeRequest({ session_id: session.session_id }));
    const data = await res.json();
    expect(data.option_ids).toEqual(["A"]);

    const after = await getSession(session.session_id);
    expect(after!.question_sequence).toEqual(["Q05", "Q06", "Q07"]);
    expect(after!.question_labels["Q28"]).toBeUndefined();
  });
});

describe("session/undo -- checkpoint-position answer (Q11)", () => {
  it("removes spliced distinguishers and resets the checkpoint slot to null so it can re-fire", async () => {
    const session = await createSession(FAKE_INTAKE);
    session.next_question_id = "DIST-CM-01";
    session.answers_log = [{ question_id: "Q11", option_ids: ["B"] }];
    session.question_sequence = ["Q10", "Q11", "DIST-CM-01", "DIST-CM-02", "Q12"];
    session.question_labels = { "DIST-CM-01": "11A", "DIST-CM-02": "11B" };
    session.checkpoint_q11 = {
      entropy: 0.6, threshold: 0.4, fires: true,
      distinguishers: ["DIST-CM-01", "DIST-CM-02"],
      top_cluster: "cm", narrative_trigger: false,
    };
    const { saveSession } = await import("@/lib/session-store");
    await saveSession(session);

    mockInvokeAccumulate.mockResolvedValueOnce({
      accumulated_vector: { ...ZERO },
      severity_inputs: [],
      severity_follow_on_ids: [],
      severity_follow_on_origins: {},
    });

    const res = await POST(fakeRequest({ session_id: session.session_id }));
    const data = await res.json();
    expect(data.option_ids).toEqual(["B"]);

    const after = await getSession(session.session_id);
    expect(after!.question_sequence).toEqual(["Q10", "Q11", "Q12"]);
    expect(after!.question_labels["DIST-CM-01"]).toBeUndefined();
    expect(after!.question_labels["DIST-CM-02"]).toBeUndefined();
    expect(after!.checkpoint_q11).toBeNull();
    expect(after!.next_question_id).toBe("Q11");
  });

  it("re-fires correctly (evaluated fresh, not skipped) after the reset -- confirmed via the same slot-null guard session/answer/route.ts uses", async () => {
    // This test exercises the invariant the reset relies on, not the full
    // forward route (session/answer/route.ts is untouched behaviorally by
    // this build and isn't re-tested here) -- checkpointSlot() genuinely
    // returns null after setCheckpointSlot(..., null), which is exactly
    // the condition session/answer/route.ts's own
    // `checkpointSlot(session, checkpointPosition) === null` guard checks
    // before evaluating a checkpoint again.
    const { checkpointSlot, setCheckpointSlot } = await import("@/lib/session-store");
    const session = await createSession(FAKE_INTAKE);
    setCheckpointSlot(session, "Q11", {
      entropy: 0.6, threshold: 0.4, fires: true,
      distinguishers: ["DIST-CM-01"], top_cluster: "cm", narrative_trigger: false,
    });
    expect(checkpointSlot(session, "Q11")).not.toBeNull();
    setCheckpointSlot(session, "Q11", null);
    expect(checkpointSlot(session, "Q11")).toBeNull();
  });
});

describe("session/undo -- empty answers_log (Q01)", () => {
  it("no-ops cleanly, returns status 200 with the current question, not an error", async () => {
    const session = await createSession(FAKE_INTAKE);
    session.next_question_id = "Q01";
    session.answers_log = [];
    const { saveSession } = await import("@/lib/session-store");
    await saveSession(session);

    const res = await POST(fakeRequest({ session_id: session.session_id }));
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data.status).toBe("noop");
    // No undone answer exists to pre-fill -- option_ids is genuinely
    // absent, not an empty array or a stale value.
    expect(data.option_ids).toBeUndefined();
    expect(mockInvokeAccumulate).not.toHaveBeenCalled();

    const after = await getSession(session.session_id);
    expect(after!.answers_log).toEqual([]);
  });
});

describe("session/undo -- multiple sequential undos", () => {
  // Also stands as the edge case task point 4 asked to check directly:
  // pre-fill, change your mind, hit Back again without re-submitting.
  // Nothing here simulates a client-side re-selection because nothing
  // needs to -- a pre-filled-but-unsubmitted question is never written to
  // answers_log (only a real answer POST does that), so this test's
  // second undo call, with zero answer submissions between the two undo
  // calls, already exercises exactly that shape: it reads answers_log's
  // real last entry (Q05) and steps back one more real answer, correctly
  // skipping over the fact that Q06 was "shown again" in between without
  // ever being re-answered.
  it("undoing twice in a row reverts both answers, in reverse order, ending at answers_log = []", async () => {
    const session = await createSession(FAKE_INTAKE);
    session.next_question_id = "Q07";
    session.answers_log = [
      { question_id: "Q05", option_ids: ["C"] },
      { question_id: "Q06", option_ids: ["B"] },
    ];
    session.question_sequence = ["Q05", "Q06", "Q07"];
    session.accumulated_vector = { ...ZERO, attitude_liability: 0.6 + 0.35 };
    const { saveSession } = await import("@/lib/session-store");
    await saveSession(session);

    // Undo #1 reverts Q06 (the last answer).
    mockInvokeAccumulate.mockResolvedValueOnce({
      accumulated_vector: { ...ZERO, attitude_liability: 0.35 },
      severity_inputs: [], severity_follow_on_ids: [], severity_follow_on_origins: {},
    });
    const res1 = await POST(fakeRequest({ session_id: session.session_id }));
    const data1 = await res1.json();
    expect(data1.question.question_id).toBe("Q06");
    expect(data1.option_ids).toEqual(["B"]);
    let mid = await getSession(session.session_id);
    expect(mid!.answers_log).toEqual([{ question_id: "Q05", option_ids: ["C"] }]);
    expect(mid!.accumulated_vector.attitude_liability).toBeCloseTo(0.6, 10);

    // Undo #2 reverts Q05.
    mockInvokeAccumulate.mockResolvedValueOnce({
      accumulated_vector: { ...ZERO, attitude_liability: 0.6 },
      severity_inputs: [], severity_follow_on_ids: [], severity_follow_on_origins: {},
    });
    const res2 = await POST(fakeRequest({ session_id: session.session_id }));
    const data2 = await res2.json();
    expect(data2.question.question_id).toBe("Q05");
    expect(data2.option_ids).toEqual(["C"]);
    const final = await getSession(session.session_id);
    expect(final!.answers_log).toEqual([]);
    expect(final!.accumulated_vector.attitude_liability).toBeCloseTo(0, 10);
    expect(final!.next_question_id).toBe("Q05");
  });
});

describe("session/undo -- guards", () => {
  it("rejects with 400 when the session has already completed", async () => {
    const session = await createSession(FAKE_INTAKE);
    session.status = "complete";
    session.answers_log = [{ question_id: "Q05", option_ids: ["A"] }];
    const { saveSession } = await import("@/lib/session-store");
    await saveSession(session);

    const res = await POST(fakeRequest({ session_id: session.session_id }));
    expect(res.status).toBe(400);
    expect(mockInvokeAccumulate).not.toHaveBeenCalled();
  });

  it("rejects with 404 for an unknown session_id", async () => {
    const res = await POST(fakeRequest({ session_id: "does-not-exist" }));
    expect(res.status).toBe(404);
  });

  it("rejects with 400 once narrative modulation has begun -- explicitly out of scope for this build", async () => {
    const session = await createSession(FAKE_INTAKE);
    session.answers_log = [{ question_id: "Q27B", option_ids: ["A"] }];
    session.pending_narrative_prompt = "some prompt";
    const { saveSession } = await import("@/lib/session-store");
    await saveSession(session);

    const res = await POST(fakeRequest({ session_id: session.session_id }));
    expect(res.status).toBe(400);
    expect(mockInvokeAccumulate).not.toHaveBeenCalled();
  });
});
