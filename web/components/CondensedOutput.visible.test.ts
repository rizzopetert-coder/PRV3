import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { CondensedOutputPayload } from "@/lib/types";

// Teeth for CondensedOutput.test.ts: with the flag forced true the block and its copy
// do render, so the hidden-state assertions there are not vacuous. Stage 5: the figure
// is the single value wage x 0.333, and the copy (UNREVIEWED, drafted in Stage 5)
// states that basis in place of the old "roughly 50-75%" text. The mock does not
// change FRICTION_DOLLARS_VISIBLE itself, which stays false in lib/output-text.ts.
vi.mock("@/lib/output-text", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/output-text")>()),
  FRICTION_DOLLARS_VISIBLE: true,
}));

import CondensedOutput from "./CondensedOutput";

const base = {
  primary_state: { id: "built_to_fail", name: "Built to Fail" },
  severity: "Emerging",
  resolution_family: "Roadmap",
  headline: "A headline.",
  verdict_text: "Decisions stall at the top.",
  additional_condition_count: 0,
} as const;

function render(payload: unknown): string {
  return renderToStaticMarkup(createElement(CondensedOutput, { payload: payload as CondensedOutputPayload }));
}

describe("CondensedOutput with the flag forced visible", () => {
  it("new single value: the heading, the figure to 3 significant figures and the new basis copy", () => {
    const html = render({ ...base, departure_cost: { amount: 38305, currency: "USD" } });
    expect(html).toContain("Estimated cost of one departure");
    expect(html).toContain("$38,300");
    expect(html).toContain("about one third of one employee");
    expect(html).toContain("Work Institute");
  });

  it("the retired 50-75% copy is gone from the visible branch", () => {
    const html = render({ ...base, departure_cost: { amount: 38305, currency: "USD" } });
    expect(html).not.toMatch(/50\s*[–-]\s*75/);
    expect(html).not.toContain("roughly 50");
    expect(html).not.toContain("estimated salary");
  });

  it("null amount (unknown industry): the unavailable note", () => {
    const html = render({ ...base, departure_cost: { amount: null, currency: "USD" } });
    expect(html).toContain("benchmark figure isn");
    expect(html).not.toContain("one third");
  });

  it("old range payload: no figure, the unavailable note, no throw", () => {
    const html = render({ ...base, financial_range: { low: 33000, high: 49500, currency: "USD" } });
    expect(html).toContain("benchmark figure isn");
    expect(html).not.toContain("33,000");
    expect(html).not.toContain("49,500");
  });

  it("missing value: the unavailable note, no throw", () => {
    const html = render({ ...base });
    expect(html).toContain("benchmark figure isn");
  });
});
