import { describe, it, expect } from "vitest";
import {
  PHASE_1_QUESTION_SEQUENCE,
  TOTAL_CORE_QUESTIONS,
  spliceDistinguishers,
  isLastQuestionInSequence,
  validateIndexInvariant,
  severityFollowOnAlreadyAsked,
  coreQuestionPosition,
  spliceLabel,
  resolveQuestionLabel,
  type AnswerLogEntry,
} from "./session-store";

// All tests exercise the same PHASE_1_QUESTION_SEQUENCE template that
// production code initializes createSession()'s question_sequence from —
// not a hand-rolled parallel array that could silently drift from it.

describe("spliceDistinguishers", () => {
  it("inserts distinguishers immediately after currentIndex without mutating the input (Stage 3 Q11 trace)", () => {
    const template = [...PHASE_1_QUESTION_SEQUENCE];
    const currentIndex = template.indexOf("Q11");
    expect(currentIndex).toBe(10);

    const result = spliceDistinguishers(template, currentIndex, [
      "DIST-CM-01",
      "DIST-CM-02",
    ]);

    // Input untouched.
    expect(template).toEqual([...PHASE_1_QUESTION_SEQUENCE]);
    expect(template).toHaveLength(32);

    // Output matches Stage 3's hand-traced shape exactly.
    expect(result).toHaveLength(34);
    expect(result[currentIndex]).toBe("Q11");
    expect(result[currentIndex + 1]).toBe("DIST-CM-01");
    expect(result[currentIndex + 2]).toBe("DIST-CM-02");
    expect(result[currentIndex + 3]).toBe("Q12");
    expect(result[result.length - 1]).toBe("Q34");
  });
});

describe("next-question resolution after a splice", () => {
  it("walks distinguisher 1 -> distinguisher 2 -> resumes the original sequence at Q12", () => {
    const template = [...PHASE_1_QUESTION_SEQUENCE];
    const q11Index = template.indexOf("Q11");
    const sequence = spliceDistinguishers(template, q11Index, [
      "DIST-CM-01",
      "DIST-CM-02",
    ]);

    // Mirrors the route's own "next = sequence[currentIndex + 1]" pattern.
    let currentIndex = q11Index;
    expect(sequence[currentIndex + 1]).toBe("DIST-CM-01");

    currentIndex = sequence.indexOf("DIST-CM-01");
    expect(sequence[currentIndex + 1]).toBe("DIST-CM-02");

    currentIndex = sequence.indexOf("DIST-CM-02");
    expect(sequence[currentIndex + 1]).toBe("Q12");
  });
});

describe("boundary — checkpoint fires on the actual last question of a sequence", () => {
  it("defers completion to the newly-spliced distinguisher instead of firing early", () => {
    const sequence = ["Q01", "Q02", "Q03"];
    const currentIndex = sequence.indexOf("Q03");

    // Before any splice, Q03 genuinely is the last question.
    expect(isLastQuestionInSequence(sequence, currentIndex)).toBe(true);

    const extended = spliceDistinguishers(sequence, currentIndex, ["DIST-X-01"]);

    expect(extended).toEqual(["Q01", "Q02", "Q03", "DIST-X-01"]);
    // Once extended, Q03 is no longer last — completion must not fire yet.
    expect(isLastQuestionInSequence(extended, currentIndex)).toBe(false);
    // The newly-inserted distinguisher is now the true last question.
    expect(isLastQuestionInSequence(extended, currentIndex + 1)).toBe(true);
  });
});

describe("validateIndexInvariant", () => {
  it("rejects an out-of-order question_id even after the sequence has been mutated by a prior splice", () => {
    const template = [...PHASE_1_QUESTION_SEQUENCE];
    const q11Index = template.indexOf("Q11");
    const sequence = spliceDistinguishers(template, q11Index, [
      "DIST-CM-01",
      "DIST-CM-02",
    ]);

    // Real next_question_id after Q11's splice, per route logic.
    const nextQuestionId = sequence[q11Index + 1]; // "DIST-CM-01"

    // Skipping ahead to Q12 (bypassing the distinguishers) must be rejected.
    expect(validateIndexInvariant("Q12", nextQuestionId)).toBe(false);
    // The actual expected next question is accepted.
    expect(validateIndexInvariant("DIST-CM-01", nextQuestionId)).toBe(true);
  });

  it("accepts a matching question_id on an unmutated sequence", () => {
    expect(validateIndexInvariant("Q01", "Q01")).toBe(true);
    expect(validateIndexInvariant("Q01", "Q02")).toBe(false);
  });
});

describe("severity follow-on splice — reuses spliceDistinguishers() directly", () => {
  it("inserts a single SEVER-## question immediately after the triggering core question", () => {
    const template = [...PHASE_1_QUESTION_SEQUENCE];
    const q22Index = template.indexOf("Q22");

    const result = spliceDistinguishers(template, q22Index, ["SEVER-04"]);

    expect(result).toHaveLength(33);
    expect(result[q22Index]).toBe("Q22");
    expect(result[q22Index + 1]).toBe("SEVER-04");
    expect(result[q22Index + 2]).toBe("Q23");
  });

  it("compounds correctly alongside a later checkpoint splice on a different question", () => {
    let sequence = [...PHASE_1_QUESTION_SEQUENCE];

    // Q22 triggers a severity follow-on.
    const q22Index = sequence.indexOf("Q22");
    sequence = spliceDistinguishers(sequence, q22Index, ["SEVER-04"]);
    expect(sequence).toHaveLength(33);

    // Q19 (checkpoint position, earlier in the sequence) — real order
    // wouldn't have Q19 fire after Q22 in a live session, but this proves
    // the two splice call sites don't corrupt each other's indices when
    // applied to the same evolving array.
    const q19Index = sequence.indexOf("Q19");
    sequence = spliceDistinguishers(sequence, q19Index, ["DIST-CC-01"]);
    expect(sequence).toHaveLength(34);

    expect(sequence[q19Index + 1]).toBe("DIST-CC-01");
    // Q22's own splice, further down the array, is unaffected in content
    // (still immediately follows Q22) even though its absolute index
    // shifted by the earlier insertion.
    const shiftedQ22Index = sequence.indexOf("Q22");
    expect(sequence[shiftedQ22Index + 1]).toBe("SEVER-04");
  });
});

describe("severityFollowOnAlreadyAsked", () => {
  it("returns false when the follow-on has never been asked", () => {
    const log: AnswerLogEntry[] = [{ question_id: "Q22", option_id: "D" }];
    expect(severityFollowOnAlreadyAsked(log, "SEVER-04")).toBe(false);
  });

  it("returns true once the follow-on itself has been answered", () => {
    const log: AnswerLogEntry[] = [
      { question_id: "Q22", option_id: "D" },
      { question_id: "SEVER-04", option_id: "D" },
    ];
    expect(severityFollowOnAlreadyAsked(log, "SEVER-04")).toBe(true);
  });

  it("a shared follow-on already asked from one parent is correctly suppressed for a second", () => {
    // General multi-parent case -- engine/data/questions.py's header
    // comment notes SEVER-11 was originally authored with two possible
    // parents (Q28 and Q31), though Q31 is now parked (excluded from the
    // live sequence entirely -- see PHASE_1_QUESTION_SEQUENCE's comment),
    // so SEVER-11 can in practice only fire from Q28 today. This test
    // exercises the guard generically, not tied to a live Q28/Q31 case.
    const log: AnswerLogEntry[] = [
      { question_id: "Q28", option_id: "C" },
      { question_id: "SEVER-11", option_id: "B" },
    ];
    expect(severityFollowOnAlreadyAsked(log, "SEVER-11")).toBe(true);
  });
});

describe("Q28/Q31 parked (live-session investigation)", () => {
  it("Q28 and Q31 are excluded from the static core sequence", () => {
    expect(PHASE_1_QUESTION_SEQUENCE).not.toContain("Q28");
    expect(PHASE_1_QUESTION_SEQUENCE).not.toContain("Q31");
  });

  it("TOTAL_CORE_QUESTIONS reflects the 32-entry sequence, not a stale hardcoded 34", () => {
    expect(TOTAL_CORE_QUESTIONS).toBe(32);
    expect(TOTAL_CORE_QUESTIONS).toBe(PHASE_1_QUESTION_SEQUENCE.length);
  });
});

describe("coreQuestionPosition", () => {
  it("returns the 1-indexed static position for a core question", () => {
    expect(coreQuestionPosition("Q01")).toBe(1);
    expect(coreQuestionPosition("Q06")).toBe(6);
    expect(coreQuestionPosition("Q34")).toBe(32);
  });

  it("returns null for a spliced or parked question_id", () => {
    expect(coreQuestionPosition("DIST-CM-01")).toBeNull();
    expect(coreQuestionPosition("SEVER-04")).toBeNull();
    // Q28 is a live splice now, not a static member -- correctly null here.
    expect(coreQuestionPosition("Q28")).toBeNull();
    // Q31 is parked -- also correctly null, same reason.
    expect(coreQuestionPosition("Q31")).toBeNull();
  });
});

describe("spliceLabel", () => {
  it("builds [parent][letter] from a real core parent's position", () => {
    expect(spliceLabel("Q11", 0)).toBe("11A");
    expect(spliceLabel("Q11", 1)).toBe("11B");
    expect(spliceLabel("Q22", 0)).toBe("22A");
  });

  it("Q28's conditional splice off Q06 labels as 6A", () => {
    expect(spliceLabel("Q06", 0)).toBe("6A");
  });
});

describe("resolveQuestionLabel", () => {
  it("resolves a core question to its static position, ignoring question_labels", () => {
    const label = resolveQuestionLabel("Q12", { Q12: "should never be read" });
    expect(label).toEqual({ kind: "core", position: 12, total: TOTAL_CORE_QUESTIONS });
  });

  it("resolves a spliced question to its stored label", () => {
    const label = resolveQuestionLabel("SEVER-04", { "SEVER-04": "22A" });
    expect(label).toEqual({ kind: "spliced", label: "22A" });
  });

  it("falls back to the raw question_id if a spliced question has no stored label", () => {
    const label = resolveQuestionLabel("SEVER-99", {});
    expect(label).toEqual({ kind: "spliced", label: "SEVER-99" });
  });
});

describe("regression — Stage 3 trace (c): three compounding checkpoint splices", () => {
  it("Q11+2, Q19+1, Q27B+3 compound correctly, landing Q34 at index 37 of a length-38 sequence", () => {
    // Base length is 32 (Q28/Q31 parked -- see PHASE_1_QUESTION_SEQUENCE's
    // comment). Q11/Q19/Q27B all sit before that removal point, so their
    // own base indices are unchanged from before; only the totals below
    // (and Q34's final index, which sits after the removal point) differ.
    let sequence: string[] = [...PHASE_1_QUESTION_SEQUENCE];

    // Q11 fires with 2 distinguishers.
    let currentIndex = sequence.indexOf("Q11");
    expect(currentIndex).toBe(10);
    sequence = spliceDistinguishers(sequence, currentIndex, [
      "DIST-CM-01",
      "DIST-CM-02",
    ]);
    expect(sequence).toHaveLength(34);

    // Q19 fires with 1 distinguisher — its index has shifted +2 from the
    // first splice.
    currentIndex = sequence.indexOf("Q19");
    expect(currentIndex).toBe(20);
    sequence = spliceDistinguishers(sequence, currentIndex, ["DIST-CC-01"]);
    expect(sequence).toHaveLength(35);

    // Q27B fires with 3 distinguishers — its index has shifted +3
    // cumulative from the first two splices.
    currentIndex = sequence.indexOf("Q27B");
    expect(currentIndex).toBe(29);
    sequence = spliceDistinguishers(sequence, currentIndex, [
      "DIST-X-01",
      "DIST-X-02",
      "DIST-X-03",
    ]);
    expect(sequence).toHaveLength(38);

    // Q34 lands at the true final index after all three splices compound.
    const q34Index = sequence.indexOf("Q34");
    expect(q34Index).toBe(37);
    expect(isLastQuestionInSequence(sequence, q34Index)).toBe(true);
  });
});
