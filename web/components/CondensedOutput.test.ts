import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { CondensedOutputPayload } from "@/lib/types";
import { FRICTION_DOLLARS_VISIBLE } from "@/lib/output-text";
import CondensedOutput from "./CondensedOutput";

// Stage 3a (R2) and Stage 5: while FRICTION_DOLLARS_VISIBLE is false the condensed
// report must show no dollar figure, no "cost of one departure" block and none of
// the departure-cost copy, with a real priced value in the payload, and the rest of
// the report must still render. The companion file CondensedOutput.visible.test.ts
// proves this assertion has teeth by flipping the flag and seeing the block appear.
// Stage 5 also requires every read of the figure to tolerate the new single value,
// the old range payload and a missing value (the web and engine deploy separately).
const base = {
  primary_state: { id: "built_to_fail", name: "Built to Fail" },
  severity: "Emerging",
  resolution_family: "Roadmap",
  headline: "A headline for the lead condition.",
  verdict_text: "Decisions stall at the top.",
  additional_condition_count: 2,
} as const;

const SHAPES: Array<[string, unknown]> = [
  ["new single value", { ...base, departure_cost: { amount: 38305, currency: "USD" } }],
  ["new, null amount (unknown industry)", { ...base, departure_cost: { amount: null, currency: "USD" } }],
  ["old range payload", { ...base, financial_range: { low: 33000, high: 49500, currency: "USD" } }],
  ["missing", { ...base }],
];

function render(payload: unknown): string {
  return renderToStaticMarkup(createElement(CondensedOutput, { payload: payload as CondensedOutputPayload }));
}

describe("CondensedOutput with friction dollars hidden", () => {
  it("the flag is false", () => {
    expect(FRICTION_DOLLARS_VISIBLE).toBe(false);
  });

  for (const [name, payload] of SHAPES) {
    describe(name, () => {
      it("renders without throwing", () => {
        expect(() => render(payload)).not.toThrow();
      });
      const html = render(payload);
      it("renders no dollar figure", () => {
        expect(html).not.toMatch(/\$\s?\d/);
        for (const s of ["38,305", "38,300", "33,000", "49,500"]) expect(html).not.toContain(s);
      });
      it("renders neither the cost-of-one-departure block nor its copy", () => {
        expect(html).not.toContain("Estimated cost of one departure");
        expect(html).not.toMatch(/50\s*[–-]\s*75/);
        expect(html).not.toContain("roughly 50");
        expect(html).not.toContain("departing employee");
        expect(html).not.toContain("one third");
        expect(html).not.toContain("Work Institute");
      });
      it("does not show the unavailable note either, since nothing is missing", () => {
        expect(html).not.toContain("benchmark figure isn");
      });
      it("still renders the rest of the report", () => {
        expect(html).toContain("Observable indicators");
        expect(html).toContain("Decisions stall at the top.");
        expect(html).toContain("A headline for the lead condition.");
        expect(html).toContain("2 more conditions surfaced");
        expect(html).toContain("Resolution pathway");
        expect(html).toContain("Roadmap");
        expect(html).toContain("Get your full diagnostic");
      });
    });
  }
});
