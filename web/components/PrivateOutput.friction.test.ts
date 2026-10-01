import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { PrivateOutputPayload } from "@/lib/types";
import { NEW_ESTIMATE, NEW_RECEIPTS, NEW_LEDGER, FRICTION_DOLLAR_STRINGS } from "@/lib/friction-test-fixtures";

// Option C (friction dollars hidden): render the real report component on
// the server and confirm no friction-derived dollar figure reaches the
// screen, while legal exposure still does. next/dynamic's lazy
// brand-specific pieces (orientation drawer, book links, engage CTA) are
// stubbed out, since they carry no figures.
vi.mock("next/dynamic", () => ({ default: () => () => null }));

import PrivateOutput from "./PrivateOutput";

const payload = {
  synthesis: {
    liability_condition_text: "Decisions stall at the top.",
    asset_resolution_anchor_text: "",
    framing_text: "",
    observable_indicators: [],
    resolution_framing_text: "A path.",
    headline: "A headline.",
    synthesis_confidence: 0.8,
    is_fallback: false,
    executive_summary: "",
  },
  primary_state: { id: "built_to_fail", name: "Built to Fail", weight: 1, descriptive_prose: "Prose." },
  secondary_states: [],
  severity: "Emerging",
  severity_by_state: [{ state_id: "built_to_fail", tier: "Emerging", score_0_100: 20 }],
  resolution_family: "People Tactics & Strategy",
  resolution_routing: "Roadmap",
  friction_tax_estimate: NEW_ESTIMATE,
  friction_receipts: NEW_RECEIPTS,
  friction_tax_ledger: NEW_LEDGER,
  legal_tail_risk_exposure: {
    low: 100000, high: 450000, currency: "USD", band: "Elevated",
    caveat: "A directional estimate.", has_unpriced_conditions: false, unpriced_state_ids: [],
    coverage_basis: "state", has_partial_jurisdictions: false, has_uncollected_net_worth_caveat: false,
    specific_caveat: null,
  },
  service_cost_comparison: {
    target_service_name: "People Tactics & Strategy",
    service_estimate_low: null, service_estimate_high: null, pricing_model_note: "",
  },
  cascade_risk: 0,
  intake: {
    organization_size: 175, industry: "Technology", org_type: "Founder-led", role_level: "C-suite",
    tenure_in_role: "1-3 years", direct_reports: "6-15", jurisdiction: "NY", significant_events: ["none"],
  },
  dimension_summary: { aptitude: 0.25, authority: 0.25, alliance: 0.25, attitude: 0.25 },
  primary_asset_domain: "Governance Discipline",
  tactical_findings: [],
  all_qualified_states: [],
} as unknown as PrivateOutputPayload;

describe("PrivateOutput with friction dollars hidden (option C)", () => {
  const html = renderToStaticMarkup(createElement(PrivateOutput, {
    payload,
    selectedStateIds: [],
    intake: { headcount: "175", industry: "Technology", orgType: "Founder-led", jurisdictions: ["NY"],
              significantEvents: ["none"], principalRole: "C-suite" },
    enableSharing: false,
    enableEngage: false,
  })).replace(/<!-- -->/g, "");

  it("renders no friction-derived figure, heading, footnote or calculation step", () => {
    for (const s of [...FRICTION_DOLLAR_STRINGS,
                     "Friction tax", "Highest standalone", "Payroll baseline", "recurring every year",
                     "Sources include", "Drives cost through"]) {
      expect(html).not.toContain(s);
    }
  });
  it("renders the replacement heading, the conditions, their answers and the note", () => {
    expect(html).toContain("The answers behind these conditions");
    expect(html).toContain("Built to Fail");
    expect(html).toContain("Some processes here are out of date or inconsistently followed.");
    expect(html).toContain("Conditions that rest on the same answers share a row.");
  });
  it("still renders legal exposure, and the cost comparison without a friction line", () => {
    expect(html).toContain("$100,000 – $450,000");
    expect(html).toContain("Legal exposure, one-time if a claim arises");
    expect(html).toContain("Ask for pricing");
  });
});
