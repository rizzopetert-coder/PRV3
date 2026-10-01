import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { CondensedOutputPayload } from "@/lib/types";
import { FRICTION_DOLLARS_VISIBLE } from "@/lib/output-text";
import CondensedOutput from "./CondensedOutput";

// Stage 3a (R2): while FRICTION_DOLLARS_VISIBLE is false the condensed report
// must show no dollar figure, no "cost of one departure" block and none of the
// "roughly 50-75%" copy, with a real priced range in the payload, and the rest
// of the report must still render. The companion file
// CondensedOutput.visible.test.ts proves this assertion has teeth by flipping
// the flag and seeing the block appear.
const payload: CondensedOutputPayload = {
  primary_state: { id: "built_to_fail", name: "Built to Fail" },
  severity: "Emerging",
  resolution_family: "Roadmap",
  headline: "A headline for the lead condition.",
  verdict_text: "Decisions stall at the top.",
  additional_condition_count: 2,
  financial_range: { low: 33000, high: 49500, currency: "USD" },
};

describe("CondensedOutput with friction dollars hidden", () => {
  it("the flag is false", () => {
    expect(FRICTION_DOLLARS_VISIBLE).toBe(false);
  });

  const html = renderToStaticMarkup(createElement(CondensedOutput, { payload }));

  it("renders no dollar figure", () => {
    expect(html).not.toMatch(/\$\s?\d/);
    expect(html).not.toContain("33,000");
    expect(html).not.toContain("49,500");
  });

  it("renders neither the cost-of-one-departure block nor the 50-75% copy", () => {
    expect(html).not.toContain("Estimated cost of one departure");
    expect(html).not.toMatch(/50\s*[–-]\s*75/);
    expect(html).not.toContain("roughly 50");
    expect(html).not.toContain("departing employee");
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
