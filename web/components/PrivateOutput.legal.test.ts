import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { PrivateOutputPayload } from "@/lib/types";
import { BASE_PRIVATE_PAYLOAD, RENDER_PROPS } from "@/lib/friction-test-base";
import * as outputText from "@/lib/output-text";
import { LEGAL_MARKERS, LEGAL_RICH } from "@/lib/legal-test-fixtures";

// While LEGAL_DOLLARS_VISIBLE is false the report must show no legal dollar figure,
// band, caveat, calculation step or receipt, on the screen the respondent sees, with a
// fully populated legal payload present. PrivateOutput is the one render path for both
// brands. PrivateOutput.legal.visible.test.ts forces the flag true and proves these
// assertions have teeth. The payload and engine are unchanged, only the display is gated.
vi.mock("next/dynamic", () => ({ default: () => () => null }));

import PrivateOutput from "./PrivateOutput";

function render(over: Record<string, unknown> = {}): string {
  const payload = { ...BASE_PRIVATE_PAYLOAD, legal_tail_risk_exposure: LEGAL_RICH, ...over } as unknown as PrivateOutputPayload;
  return renderToStaticMarkup(createElement(PrivateOutput, { payload, ...RENDER_PROPS })).replace(/<!-- -->/g, "");
}

describe("PrivateOutput with legal dollars hidden", () => {
  it("the flag is false", () => {
    expect((outputText as Record<string, unknown>).LEGAL_DOLLARS_VISIBLE).toBe(false);
  });

  it("renders without throwing", () => {
    expect(render().length).toBeGreaterThan(1000);
  });

  it("renders no legal figure, band, heading, caveat, unpriced note or receipt", () => {
    const html = render();
    for (const s of LEGAL_MARKERS) expect(html).not.toContain(s);
    expect(html).not.toMatch(/\$\s?123,000/);
    expect(html).not.toMatch(/\$\s?456,000/);
    expect(html).not.toContain("Legal/Compliance exposure");
    expect(html).not.toContain("Estimated exposure");
    expect(html).not.toContain("How this figure was calculated");
  });

  it("the cost comparison carries no legal line", () => {
    const html = render({ service_cost_comparison: {
      target_service_name: "People Tactics & Strategy", service_estimate_low: 20000, service_estimate_high: 30000, pricing_model_note: "A note.",
    } });
    expect(html).not.toContain("Legal exposure, one-time if a claim arises");
    expect(html).not.toContain("$123,000");
  });

  it("tolerates a missing or null legal block", () => {
    for (const over of [{ legal_tail_risk_exposure: null }, { legal_tail_risk_exposure: undefined }]) {
      expect(() => render(over)).not.toThrow();
      expect(render(over)).not.toContain("Legal/Compliance exposure");
    }
  });

  it("the rest of the report still renders", () => {
    const html = render();
    expect(html).toContain("A headline.");
    expect(html).toContain("Resolution pathway");
  });
});

describe("PrivateOutput Pricing card while legal dollars are hidden", () => {
  const unpriced = { target_service_name: "People Tactics & Strategy", service_estimate_low: null, service_estimate_high: null, pricing_model_note: "" };
  const priced = { target_service_name: "People Tactics & Strategy", service_estimate_low: 20000, service_estimate_high: 30000, pricing_model_note: "A pricing note." };

  it("renders a pricing-only card titled Pricing, with Ask for pricing when unpriced", () => {
    const html = render({ service_cost_comparison: unpriced });
    expect(html).toContain("Pricing</p>");
    expect(html).toContain("People Tactics &amp; Strategy");
    expect(html).toContain("Ask for pricing");
    expect(html).toContain("Scoped to what this diagnostic found.");
  });
  it("renders the range and its note when priced", () => {
    const html = render({ service_cost_comparison: priced });
    expect(html).toContain("$20,000 – $30,000");
    expect(html).toContain("A pricing note.");
    expect(html).not.toContain("Ask for pricing");
  });
  it("is not the Cost comparison card: no title, no unaddressed lead-in, no legal line", () => {
    const html = render({ service_cost_comparison: unpriced });
    expect(html).not.toContain("Cost comparison");
    expect(html).not.toContain("If these conditions go unaddressed");
    expect(html).not.toContain("Legal exposure, one-time if a claim arises");
  });
  it("renders nothing for the card when there is no service_cost_comparison", () => {
    const html = render({ service_cost_comparison: undefined });
    expect(html).not.toContain("Pricing</p>");
    expect(html).not.toContain("Cost comparison");
  });
});
