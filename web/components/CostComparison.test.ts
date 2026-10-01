import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { LegalTailRiskExposure, ServiceCostComparison } from "@/lib/types";
import { CostComparison } from "./ReportDetails";
import { NEW_ESTIMATE, CAPPED_ESTIMATE, OLD_ESTIMATE } from "@/lib/friction-test-fixtures";

// Stage 6 consumer test, ReportDetails CostComparison: the friction line follows
// decision 14 (the typical-loss point estimate and the legal tail-risk range as two
// lines, never a sum), and reads the two-channel estimate, the percent at the cap,
// the older range, or nothing without throwing.
const comparison: ServiceCostComparison = {
  target_service_name: "People Tactics & Strategy",
  service_estimate_low: null, service_estimate_high: null, pricing_model_note: "",
};
const legal = {
  low: 100000, high: 450000, currency: "USD", band: "Elevated", caveat: "x",
  has_unpriced_conditions: false, unpriced_state_ids: [], coverage_basis: "state",
  has_partial_jurisdictions: false, has_uncollected_net_worth_caveat: false, specific_caveat: null,
} as unknown as LegalTailRiskExposure;

function render(friction: unknown, legalBlock: LegalTailRiskExposure | null = legal): string {
  return renderToStaticMarkup(createElement(CostComparison, {
    comparison, friction: friction as never, legal: legalBlock, fallbackServiceName: "x",
  })).replace(/<!-- -->/g, "");
}

describe("CostComparison friction line", () => {
  it("new shape: the typical loss as a dollar figure, and the legal range as a separate line", () => {
    const html = render(NEW_ESTIMATE);
    expect(html).toContain("$63,900");
    expect(html).toContain("What organizations like yours typically lose to friction each year");
    expect(html).toContain("$100,000 – $450,000");
    expect(html).toContain("Legal exposure, one-time if a claim arises");
    expect(html).not.toContain("$164,000");
  });
  it("new shape at the 1,000 cap: percent of payroll, no dollar figure", () => {
    const html = render(CAPPED_ESTIMATE);
    expect(html).toContain("9.2% of payroll");
    expect(html).not.toContain("$63,900");
  });
  it("old shape: the older range", () => {
    expect(render(OLD_ESTIMATE)).toContain("$1,230,000 – $1,730,000");
  });
  it("missing friction with a priced legal range: legal only", () => {
    const html = render(null);
    expect(html).toContain("$100,000 – $450,000");
    expect(html).not.toContain("What organizations like yours typically lose to friction");
  });
  it("unusable friction values render no friction line and do not throw", () => {
    for (const bad of [{}, { typical_baseline: {} }, { typical_baseline: { total: {} } }, "x", 5, { low: "a", high: 1 }]) {
      const html = render(bad);
      expect(html).not.toContain("What organizations like yours typically lose to friction");
    }
  });
  it("renders nothing when neither friction nor legal is priced", () => {
    expect(render(null, null)).toBe("");
  });
});
