import { describe, it, expect } from "vitest";
import {
  PHASE_1_QUESTION_SEQUENCE,
  spliceDistinguishers,
  isLastQuestionInSequence,
  validateIndexInvariant,
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
    expect(template).toHaveLength(34);

    // Output matches Stage 3's hand-traced shape exactly.
    expect(result).toHaveLength(36);
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

describe("regression — Stage 3 trace (c): three compounding checkpoint splices", () => {
  it("Q11+2, Q19+1, Q27B+3 compound correctly, landing Q34 at index 39 of a length-40 sequence", () => {
    let sequence: string[] = [...PHASE_1_QUESTION_SEQUENCE];

    // Q11 fires with 2 distinguishers.
    let currentIndex = sequence.indexOf("Q11");
    expect(currentIndex).toBe(10);
    sequence = spliceDistinguishers(sequence, currentIndex, [
      "DIST-CM-01",
      "DIST-CM-02",
    ]);
    expect(sequence).toHaveLength(36);

    // Q19 fires with 1 distinguisher — its index has shifted +2 from the
    // first splice.
    currentIndex = sequence.indexOf("Q19");
    expect(currentIndex).toBe(20);
    sequence = spliceDistinguishers(sequence, currentIndex, ["DIST-CC-01"]);
    expect(sequence).toHaveLength(37);

    // Q27B fires with 3 distinguishers — its index has shifted +3
    // cumulative from the first two splices.
    currentIndex = sequence.indexOf("Q27B");
    expect(currentIndex).toBe(29);
    sequence = spliceDistinguishers(sequence, currentIndex, [
      "DIST-X-01",
      "DIST-X-02",
      "DIST-X-03",
    ]);
    expect(sequence).toHaveLength(40);

    // Q34 lands at the true final index after all three splices compound.
    const q34Index = sequence.indexOf("Q34");
    expect(q34Index).toBe(39);
    expect(isLastQuestionInSequence(sequence, q34Index)).toBe(true);
  });
});
