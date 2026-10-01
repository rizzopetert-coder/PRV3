import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { CondensedOutputPayload } from "@/lib/types";

// Teeth for CondensedOutput.test.ts: with the flag forced true the block and
// its copy do render, so the hidden-state assertions there are not vacuous.
vi.mock("@/lib/output-text", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/output-text")>()),
  FRICTION_DOLLARS_VISIBLE: true,
}));

import CondensedOutput from "./CondensedOutput";

const base: CondensedOutputPayload = {
  primary_state: { id: "built_to_fail", name: "Built to Fail" },
  severity: "Emerging",
  resolution_family: "Roadmap",
  headline: "A headline.",
  verdict_text: "Decisions stall at the top.",
  additional_condition_count: 0,
  financial_range: { low: 33000, high: 49500, currency: "USD" },
};

describe("CondensedOutput with the flag forced visible", () => {
  it("renders the figure block and the existing copy", () => {
    const html = renderToStaticMarkup(createElement(CondensedOutput, { payload: base }));
    expect(html).toContain("Estimated cost of one departure");
    expect(html).toMatch(/\$33,000/);
    expect(html).toContain("roughly 50");
  });

  it("renders the unavailable note when the range is null", () => {
    const html = renderToStaticMarkup(createElement(CondensedOutput, {
      payload: { ...base, financial_range: { low: null, high: null, currency: "USD" } },
    }));
    expect(html).toContain("benchmark figure isn");
  });
});
