// A private-output payload with no friction fields, for the Stage 6 render tests.
// The legal block carries a priced range so the legal line renders in every case.
import type { PrivateOutputPayload } from "./types";

export const BASE_PRIVATE_PAYLOAD = {
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

export const RENDER_PROPS = {
  selectedStateIds: [] as string[],
  intake: {
    headcount: "175", industry: "Technology", orgType: "Founder-led", jurisdictions: ["NY"],
    significantEvents: ["none"], principalRole: "C-suite",
  },
  enableSharing: false,
  enableEngage: false,
};
