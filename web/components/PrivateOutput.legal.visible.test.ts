import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { PrivateOutputPayload } from "@/lib/types";
import { BASE_PRIVATE_PAYLOAD, RENDER_PROPS } from "@/lib/friction-test-base";
import { LEGAL_MARKERS, LEGAL_RICH } from "@/lib/legal-test-fixtures";

// The restorable state: with the flag forced true (a mock, LEGAL_DOLLARS_VISIBLE itself
// stays false in lib/output-text.ts) every legal element renders, so the hidden test in
// PrivateOutput.legal.test.ts is checking something that would otherwise show.
vi.mock("next/dynamic", () => ({ default: () => () => null }));
vi.mock("@/lib/output-text", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/output-text")>()),
  LEGAL_DOLLARS_VISIBLE: true,
}));

import PrivateOutput from "./PrivateOutput";

function render(over: Record<string, unknown> = {}): string {
  const payload = { ...BASE_PRIVATE_PAYLOAD, legal_tail_risk_exposure: LEGAL_RICH, ...over } as unknown as PrivateOutputPayload;
  return renderToStaticMarkup(createElement(PrivateOutput, { payload, ...RENDER_PROPS })).replace(/<!-- -->/g, "");
}

describe("PrivateOutput with legal dollars forced visible", () => {
  it("renders the figure, heading, caveats, unpriced note and receipts", () => {
    const html = render();
    expect(html).toContain("$123,000 – $456,000");
    expect(html).toContain("Legal/Compliance exposure");
    for (const s of LEGAL_MARKERS) expect(html).toContain(s);
    expect(html).toContain("How this figure was calculated");
  });
  it("renders the legal line in the cost comparison", () => {
    expect(render()).toContain("Legal exposure, one-time if a claim arises");
  });
});

describe("PrivateOutput with legal dollars forced visible: the Cost comparison card is unchanged", () => {
  it("keeps the Cost comparison title, the legal line and the service card, with no Pricing title", () => {
    const html = render({ service_cost_comparison: { target_service_name: "People Tactics & Strategy", service_estimate_low: null, service_estimate_high: null, pricing_model_note: "" } });
    expect(html).toContain("Cost comparison");
    expect(html).toContain("If these conditions go unaddressed");
    expect(html).toContain("Legal exposure, one-time if a claim arises");
    expect(html).toContain("Ask for pricing");
    expect(html).not.toContain("Pricing</p>");
  });
});
