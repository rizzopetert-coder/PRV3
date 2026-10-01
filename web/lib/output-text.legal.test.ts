import { describe, it, expect } from "vitest";
import { buildResultsText } from "./output-text";
import * as outputText from "./output-text";
import type { PrivateOutputPayload } from "./types";
import { BASE_PRIVATE_PAYLOAD } from "./friction-test-base";
import { LEGAL_MARKERS, LEGAL_RICH } from "./legal-test-fixtures";

// Copy results mirrors the screen. While LEGAL_DOLLARS_VISIBLE is false it carries no
// legal figure, band, caveat, receipt or legal cost-comparison line. Forcing the option
// true proves the assertions have teeth.
const payload = {
  ...BASE_PRIVATE_PAYLOAD,
  legal_tail_risk_exposure: LEGAL_RICH,
  service_cost_comparison: {
    target_service_name: "People Tactics & Strategy", service_estimate_low: 20000, service_estimate_high: 30000, pricing_model_note: "A note.",
  },
} as unknown as PrivateOutputPayload;

describe("buildResultsText with legal dollars hidden", () => {
  it("the flag is false", () => {
    expect((outputText as Record<string, unknown>).LEGAL_DOLLARS_VISIBLE).toBe(false);
  });
  it("carries no legal figure, heading, caveat, unpriced note or receipt", () => {
    const text = buildResultsText(payload);
    for (const s of LEGAL_MARKERS) expect(text).not.toContain(s);
    expect(text).not.toMatch(/\$\s?123,000/);
    expect(text).not.toContain("Legal/Compliance exposure");
    expect(text).not.toContain("How the legal figure was calculated");
    expect(text).not.toContain("Legal exposure, one-time if a claim arises");
    expect(text).not.toContain("Estimated exposure");
  });
  it("does not throw on a null or missing legal block", () => {
    expect(() => buildResultsText({ ...payload, legal_tail_risk_exposure: null } as PrivateOutputPayload)).not.toThrow();
    expect(() => buildResultsText({ ...payload, legal_tail_risk_exposure: undefined } as unknown as PrivateOutputPayload)).not.toThrow();
  });
});

describe("buildResultsText with legal dollars forced visible", () => {
  it("carries the figure, heading, caveats, receipts and the legal cost-comparison line", () => {
    const text = buildResultsText(payload, undefined, { legalDollarsVisible: true });
    expect(text).toContain("Legal/Compliance exposure:\n$123,000 – $456,000");
    for (const s of LEGAL_MARKERS) expect(text).toContain(s);
    expect(text).toContain("How the legal figure was calculated:");
    expect(text).toContain("— Legal exposure, one-time if a claim arises: $123,000 – $456,000");
  });
});

describe("buildResultsText Pricing block while legal dollars are hidden", () => {
  const withScc = (scc: unknown) => ({ ...payload, service_cost_comparison: scc } as unknown as PrivateOutputPayload);
  it("mirrors the Pricing card, unpriced", () => {
    const text = buildResultsText(withScc({ target_service_name: "People Tactics & Strategy", service_estimate_low: null, service_estimate_high: null, pricing_model_note: "" }));
    expect(text).toContain("Pricing:\n— People Tactics & Strategy: Ask for pricing. Scoped to what this diagnostic found.");
    expect(text).not.toContain("Cost comparison:");
  });
  it("mirrors the Pricing card, priced", () => {
    const text = buildResultsText(payload);
    expect(text).toContain("Pricing:\n— People Tactics & Strategy: $20,000 – $30,000. A note.");
    expect(text).not.toContain("Cost comparison:");
    expect(text).not.toContain("Legal exposure, one-time if a claim arises");
  });
  it("forced visible keeps the Cost comparison block and has no Pricing block", () => {
    const text = buildResultsText(payload, undefined, { legalDollarsVisible: true });
    expect(text).toContain("Cost comparison:\n— Legal exposure, one-time if a claim arises: $123,000 – $456,000");
    expect(text).not.toContain("Pricing:");
  });
});
