import { describe, it, expect } from "vitest";
import { buildResultsText, firstSentence, joinNames, buildCoreCluster } from "./output-text";
import type { PrivateOutputPayload, StateRef } from "./types";

// A full payload with every optional field populated -- confirms every
// listed field (visible Blocks 1-4d, plus the fields PrivateOutput.tsx
// never renders) actually appears in the assembled text.
const FULL_PAYLOAD: PrivateOutputPayload = {
  synthesis: {
    liability_condition_text: "The liability condition text.",
    asset_resolution_anchor_text: "The asset resolution anchor text.",
    framing_text: "The framing text.",
    observable_indicators: ["First indicator.", "Second indicator."],
    resolution_framing_text: "The resolution framing text.",
    headline: "The headline.",
    synthesis_confidence: 0.87,
    is_fallback: false,
  },
  primary_state: {
    id: "the_paper_tiger",
    name: "The Paper Tiger",
    weight: 1.0,
    descriptive_prose: "Primary state descriptive prose.",
  },
  secondary_states: [
    { id: "state_b", name: "State B", weight: 0.95, descriptive_prose: "State B's own prose. Second sentence." },
    { id: "state_c", name: "State C", weight: 0.93, descriptive_prose: "State C's own prose." },
    { id: "state_d", name: "State D", weight: 0.5, descriptive_prose: "State D's own prose, far below the delta." },
  ],
  severity: "Entrenched",
  severity_by_state: [
    { state_id: "the_paper_tiger", tier: "Entrenched", score_0_100: 62 },
    { state_id: "state_b", tier: "Emerging", score_0_100: 20 },
  ],
  resolution_family: "People Tactics and Strategy",
  resolution_routing: "Routing description text.",
  friction_tax_estimate: { low: 50000, high: 120000, currency: "USD" },
  legal_tail_risk_exposure: {
    low: 100000,
    high: 450000,
    currency: "USD",
    band: "Elevated",
    caveat: "This is a directional estimate, not a legal opinion.",
    has_unpriced_conditions: true,
    unpriced_state_ids: ["state_b"],
    coverage_basis: "federal_baseline",
    has_partial_jurisdictions: true,
    has_uncollected_net_worth_caveat: false,
    specific_caveat: null,
  },
  cascade_risk: 0.42,
  causation_pattern: { pattern: "single_point", dispersion: 0.23, qualified_state_count: 3 },
  trajectory: { delta: 0.15, dispersion_delta: 0.05, direction: "escalating", duration_band: "6_18mo" },
  urgency_window: { time_to_consequence: "Acute", response_window: "Immediate" },
  intake: {
    organization_size: 152,
    industry: "Professional Services",
    org_type: "Founder-led",
    role_level: "C-suite",
    tenure_in_role: "1-3 years",
    direct_reports: "6-15",
    jurisdiction: "CA",
    significant_events: ["leadership_change", "other"],
    significant_event_elaboration: "A merger completed six months ago.",
  },
  dimension_summary: { aptitude: 0.6, authority: 0.25, alliance: 0.1, attitude: 0.05 },
  primary_asset_domain: "Governance Discipline",
};

// Optional fields absent/null throughout -- confirms no empty labeled
// section is emitted for genuinely absent data.
const MINIMAL_PAYLOAD: PrivateOutputPayload = {
  synthesis: {
    liability_condition_text: "The liability condition text.",
    asset_resolution_anchor_text: "",
    framing_text: "",
    observable_indicators: [],
    resolution_framing_text: "",
    headline: "",
    synthesis_confidence: 0.5,
    is_fallback: true,
  },
  primary_state: { id: "the_paper_tiger", name: "The Paper Tiger", weight: 1.0 },
  secondary_states: [],
  severity: "Emerging",
  resolution_family: "People Tactics and Strategy",
  resolution_routing: "Routing description text.",
  friction_tax_estimate: null,
  legal_tail_risk_exposure: null,
  intake: {
    organization_size: 50,
    industry: "Technology",
    org_type: "Founder-led",
    role_level: "Manager",
    tenure_in_role: "Less than 1 year",
    direct_reports: "0",
    jurisdiction: "TX",
    significant_events: ["none"],
  },
  dimension_summary: { aptitude: 0.25, authority: 0.25, alliance: 0.25, attitude: 0.25 },
  primary_asset_domain: "",
};

describe("buildResultsText -- full payload, every field present", () => {
  const text = buildResultsText(FULL_PAYLOAD);

  it("includes the primary state, severity, and descriptive_prose", () => {
    expect(text).toContain("The Paper Tiger (Entrenched)");
    expect(text).toContain("Primary state descriptive prose.");
  });

  it("includes the headline", () => {
    expect(text).toContain("The headline.");
  });

  it("includes the dimensional shape as a plain text line with real values", () => {
    expect(text).toContain("Dimensional shape: Aptitude: 60% | Authority: 25% | Alliance: 10% | Attitude: 5%");
  });

  it("includes observable indicators", () => {
    expect(text).toContain("First indicator.");
    expect(text).toContain("Second indicator.");
  });

  it("includes liability condition text, framing text, and asset resolution text", () => {
    expect(text).toContain("The liability condition text.");
    expect(text).toContain("The framing text.");
    expect(text).toContain("The asset resolution anchor text.");
    expect(text).toContain("Primary asset domain: Governance Discipline");
  });

  it("includes the resolution pathway", () => {
    expect(text).toContain("Resolution pathway: People Tactics and Strategy");
    expect(text).toContain("The resolution framing text.");
  });

  it("includes co-occurring states with their first-sentence summaries, and folds the rest into an overflow count", () => {
    expect(text).toContain("State B: State B's own prose.");
    expect(text).toContain("State C: State C's own prose.");
    expect(text).not.toContain("State D");
    expect(text).toContain("+1 co-occurring condition");
  });

  it("includes severity-by-state with the numeric score, unlike the on-screen bar", () => {
    expect(text).toContain("The Paper Tiger: Entrenched (62/100)");
    expect(text).toContain("State B: Emerging (20/100)");
  });

  it("includes legal/compliance exposure, the coverage caveat, the partial-jurisdiction caveat, the unpriced-state caveat, and the base caveat", () => {
    expect(text).toContain("$100,000 – $450,000");
    expect(text).toContain("federal coverage threshold");
    expect(text).toContain("not independently verified");
    expect(text).toContain("Real exposure current data can't price precisely for: State B.");
    expect(text).toContain("This is a directional estimate, not a legal opinion.");
  });

  it("includes every field PrivateOutput.tsx never renders, in the additional-detail section", () => {
    expect(text).toContain("Cascade risk: 0.42");
    expect(text).toContain("Causation pattern: single_point (dispersion: 0.23, qualified states: 3)");
    expect(text).toContain("Trajectory: escalating (delta: 0.15, dispersion delta: 0.05, duration: 6_18mo)");
    expect(text).toContain("Urgency window: time to consequence: Acute, response window: Immediate");
    expect(text).toContain("Synthesis confidence: 0.87");
    expect(text).toContain("Synthesis is fallback: false");
    expect(text).toContain("Friction tax estimate: $50,000 – $120,000");
    expect(text).toContain("Organization size: 152");
    expect(text).toContain("Industry: Professional Services");
    expect(text).toContain("Role level: C-suite");
    expect(text).toContain("Tenure in role: 1-3 years");
    expect(text).toContain("Direct reports: 6-15");
    expect(text).toContain("Jurisdiction: CA");
    expect(text).toContain("Significant events: leadership_change, other");
    expect(text).toContain("Significant event elaboration: A merger completed six months ago.");
  });

  it("places the additional-detail section after all visible content, correctly ordered", () => {
    const markerIndex = text.indexOf("--- Additional diagnostic detail ---");
    expect(markerIndex).toBeGreaterThan(-1);

    // Everything visible (Blocks 1-4d) appears before the marker.
    const visibleMarkers = [
      "The Paper Tiger (Entrenched)",
      "Dimensional shape:",
      "Resolution pathway:",
      "Co-occurring conditions:",
      "Severity across conditions:",
      "Legal/Compliance exposure:",
    ];
    for (const marker of visibleMarkers) {
      expect(text.indexOf(marker)).toBeLessThan(markerIndex);
      expect(text.indexOf(marker)).toBeGreaterThan(-1);
    }

    // Everything additional-detail-only appears after the marker.
    const detailMarkers = ["Cascade risk:", "Causation pattern:", "Trajectory:", "Urgency window:", "Synthesis confidence:", "Intake:"];
    for (const marker of detailMarkers) {
      expect(text.indexOf(marker)).toBeGreaterThan(markerIndex);
    }
  });

  it("contains no literal markdown syntax that would look wrong pasted as plain text", () => {
    expect(text).not.toMatch(/[*#]/);
  });
});

describe("buildResultsText -- minimal payload, optional fields absent/null", () => {
  const text = buildResultsText(MINIMAL_PAYLOAD);

  it("omits the headline section entirely rather than emitting an empty line for it", () => {
    // The headline block would otherwise insert a blank-then-empty pair;
    // confirm no stray double-blank artifact from an empty headline.
    expect(text).not.toMatch(/\n\n\n/);
  });

  it("omits observable indicators entirely when empty", () => {
    expect(text).not.toContain("Observable indicators:");
  });

  it("omits framing text and asset-resolution block when both are empty", () => {
    expect(text).not.toContain("The framing text.");
    expect(text).not.toContain("Primary asset domain:");
  });

  it("omits co-occurring conditions when secondary_states is empty", () => {
    expect(text).not.toContain("Co-occurring conditions:");
  });

  it("omits severity-by-state when absent", () => {
    expect(text).not.toContain("Severity across conditions:");
  });

  it("omits the entire legal/compliance block when legal_tail_risk_exposure is null", () => {
    expect(text).not.toContain("Legal/Compliance exposure:");
  });

  it("omits cascade_risk, causation_pattern, trajectory, and urgency_window when absent", () => {
    expect(text).not.toContain("Cascade risk:");
    expect(text).not.toContain("Causation pattern:");
    expect(text).not.toContain("Trajectory:");
    expect(text).not.toContain("Urgency window:");
  });

  it("omits friction_tax_estimate when null (Path B)", () => {
    expect(text).not.toContain("Friction tax estimate:");
  });

  it("omits significant_event_elaboration when not provided", () => {
    expect(text).not.toContain("Significant event elaboration:");
  });

  it("still includes the always-present fields -- synthesis confidence/fallback and full intake", () => {
    expect(text).toContain("Synthesis confidence: 0.5");
    expect(text).toContain("Synthesis is fallback: true");
    expect(text).toContain("Organization size: 50");
    expect(text).toContain("Significant events: none");
  });

  it("still uses resolution_routing as the Block 2b fallback when liability text is present but framing text is empty", () => {
    // liability_condition_text IS present in MINIMAL_PAYLOAD -- confirm it
    // renders directly rather than falling back, and resolution_routing
    // still appears once, in Block 4 (not duplicated per the same
    // usedRoutingInBlock2 logic PrivateOutput.tsx itself uses).
    expect(text).toContain("The liability condition text.");
    const routingCount = text.split("Routing description text.").length - 1;
    expect(routingCount).toBe(1);
  });
});

describe("buildResultsText -- Block 2b fallback to resolution_routing", () => {
  it("uses resolution_routing in Block 2b, and does not duplicate it in Block 4, when liability_condition_text is empty", () => {
    const payload: PrivateOutputPayload = {
      ...MINIMAL_PAYLOAD,
      synthesis: { ...MINIMAL_PAYLOAD.synthesis, liability_condition_text: "", resolution_framing_text: "" },
    };
    const text = buildResultsText(payload);
    const routingCount = text.split("Routing description text.").length - 1;
    expect(routingCount).toBe(1);
  });
});

describe("output-text -- shared pure helpers (moved from PrivateOutput.tsx, unchanged)", () => {
  it("firstSentence splits on the first sentence boundary", () => {
    expect(firstSentence("First sentence. Second sentence.")).toBe("First sentence.");
  });

  it("firstSentence falls through to the whole string when no internal boundary exists", () => {
    expect(firstSentence("One sentence with no internal period")).toBe("One sentence with no internal period");
  });

  it("joinNames applies an Oxford comma for 3+ names", () => {
    expect(joinNames(["A", "B", "C"])).toBe("A, B, and C");
    expect(joinNames(["A", "B"])).toBe("A and B");
    expect(joinNames(["A"])).toBe("A");
    expect(joinNames([])).toBe("");
  });

  it("buildCoreCluster caps at 5 and reports the overflow count", () => {
    const secondary: StateRef[] = Array.from({ length: 7 }, (_, i) => ({
      id: `s${i}`, name: `S${i}`, weight: 1.0,
    }));
    const { core, overflowCount } = buildCoreCluster(secondary, 1.0);
    expect(core).toHaveLength(5);
    expect(overflowCount).toBe(2);
  });
});
