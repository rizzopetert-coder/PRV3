import { describe, it, expect } from "vitest";
import {
  buildResultsText, firstSentence, joinNames, buildCoreCluster, OHIO_NET_WORTH_CAVEAT,
  groupLedgerRows, formatUsd, formatUsdRange, FRICTION_TYPICAL_LOSS_LABEL,
  FRICTION_DOLLARS_VISIBLE, FRICTION_LEDGER_HEADING_NO_DOLLARS, FRICTION_LEDGER_NOTE_NO_DOLLARS,
} from "./output-text";
import type { PrivateOutputPayload, StateRef, TacticalSectionResult } from "./types";

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
  resolution_family: "People Tactics & Strategy",
  resolution_routing: "Routing description text.",
  friction_tax_estimate: {
    currency: "USD",
    typical_baseline: {
      total: { amount: 63923.24, percent_of_payroll: 12.6759 },
      channels: [
        { channel: "engagement", amount: 35401.02, percent_of_payroll: 7.02, inputs: [] },
        { channel: "turnover", amount: 28522.22, percent_of_payroll: 5.6559, inputs: [] },
      ],
    },
    excess: null,
  },
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
  resolution_family: "People Tactics & Strategy",
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

  it("lists every condition with its tier and prose, severity paragraph on the lead only", () => {
    expect(text).toContain("Conditions identified:");
    expect(text).toContain("— The Paper Tiger (Entrenched)\n  Primary state descriptive prose.");
    expect(text).toContain("— State B (Emerging)\n  State B's own prose. Second sentence.");
    // State D has no severity entry and is not the lead, so no tier badge.
    expect(text).toContain("— State D\n  State D's own prose, far below the delta.");
    expect(text.split("The condition has been here long enough").length - 1).toBe(1);
  });

  it("includes the headline", () => {
    expect(text).toContain("The headline.");
  });

  it("includes observable indicators", () => {
    expect(text).toContain("First indicator.");
    expect(text).toContain("Second indicator.");
  });

  it("includes liability condition text, framing text, and asset resolution text", () => {
    expect(text).toContain("The liability condition text.");
    expect(text).toContain("The framing text.");
    expect(text).toContain("The asset resolution anchor text.");
    // P1: the primary asset domain describes the lead condition, not the
    // respondent, and is not shown.
    expect(text).not.toContain("Primary asset domain");
    expect(text).not.toContain("Governance Discipline");
  });

  it("includes the resolution pathway", () => {
    expect(text).toContain("Resolution pathway: People Tactics & Strategy");
    expect(text).toContain("The resolution framing text.");
  });

  it("includes legal/compliance exposure, the coverage caveat, the partial-jurisdiction caveat, the unpriced-state caveat, and the base caveat", () => {
    expect(text).toContain("$100,000 – $450,000");
    expect(text).toContain("federal coverage threshold");
    expect(text).toContain("not independently verified");
    expect(text).toContain("Real exposure current data can't price precisely for: State B.");
    expect(text).toContain("This is a directional estimate, not a legal opinion.");
  });

  it("copies nothing the screen does not show", () => {
    for (const s of [
      "Dimensional shape", "60%", "Co-occurring conditions", "co-occurring condition",
      "Severity across conditions", "62/100", "/100",
      "Additional diagnostic detail", "Cascade risk", "Causation pattern", "dispersion",
      "Trajectory", "delta:", "Urgency window", "Synthesis confidence", "Synthesis is fallback",
      "Friction tax estimate:", "Intake:", "Organization size", "Role level",
      "Significant event elaboration",
    ]) {
      expect(text).not.toContain(s);
    }
  });

  it("follows the on-screen order", () => {
    const order = [
      "Observable indicators:", "Conditions identified:", "The headline.",
      "The liability condition text.", "The asset resolution anchor text.", "Resolution pathway:",
      "Legal/Compliance exposure:",
    ];
    const idx = order.map((m) => text.indexOf(m));
    idx.forEach((v) => expect(v).toBeGreaterThan(-1));
    expect([...idx].sort((a, b) => a - b)).toEqual(idx);
  });

  it("contains no literal markdown syntax that would look wrong pasted as plain text", () => {
    expect(text).not.toMatch(/[*#]/);
  });
});

describe("buildResultsText -- minimal payload, optional fields absent/null", () => {
  const text = buildResultsText(MINIMAL_PAYLOAD);

  it("never emits an empty paragraph", () => {
    expect(text).not.toMatch(/\n\n\n/);
    expect(text.startsWith("\n")).toBe(false);
  });

  it("omits observable indicators entirely when empty", () => {
    expect(text).not.toContain("Observable indicators:");
  });

  it("omits framing text and asset-resolution block when both are empty", () => {
    expect(text).not.toContain("The framing text.");
    expect(text).not.toContain("Primary asset domain:");
  });

  it("falls back to the primary state for the conditions list, with the payload tier", () => {
    expect(text).toContain("Conditions identified:\n— The Paper Tiger (Emerging)");
  });

  it("omits the entire legal/compliance block when legal_tail_risk_exposure is null", () => {
    expect(text).not.toContain("Legal/Compliance exposure:");
  });

  it("omits the friction tax ledger when there is none", () => {
    expect(text).not.toContain("Friction tax ledger:");
  });

  it("still uses resolution_routing once, in the pathway, when liability text is present", () => {
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

describe("buildResultsText -- conditions list source", () => {
  it("uses all_qualified_states when present, in its order", () => {
    const text = buildResultsText({
      ...MINIMAL_PAYLOAD,
      all_qualified_states: [
        { state_id: "q1", state_name: "Q One", score: 0.9, descriptive_prose: "Q one prose." },
        { state_id: "q2", state_name: "Q Two", score: 0.7, descriptive_prose: "Q two prose." },
      ],
    });
    expect(text.indexOf("— Q One (Emerging)")).toBeGreaterThan(-1);
    expect(text.indexOf("— Q Two")).toBeGreaterThan(text.indexOf("— Q One"));
    expect(text).not.toContain("The Paper Tiger");
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


describe("buildResultsText -- Phase 3 sections", () => {
  const phase3: PrivateOutputPayload = {
    ...FULL_PAYLOAD,
    synthesis: { ...FULL_PAYLOAD.synthesis, executive_summary: "The summary sentence." },
    friction_tax_estimate: {
      currency: "USD",
      typical_baseline: {
        total: { amount: 63923.24, percent_of_payroll: 12.6759 },
        channels: [
          { channel: "engagement", amount: 35401.02, percent_of_payroll: 7.02, inputs: [] },
          { channel: "turnover", amount: 28522.22, percent_of_payroll: 5.6559, inputs: [] },
        ],
      },
      excess: null,
    },
    friction_receipts: [{ category: "Payroll baseline", rationale: "Estimated annual payroll: $1,000,000." }],
    friction_tax_ledger: [
      {
        state_id: "the_paper_tiger", state_name: "The Paper Tiger", risk_label: "Entrenched",
        channels: ["turnover"],
        top_contributing_answers: ["Decisions get made, then get reopened."],
      },
      {
        state_id: "state_b", state_name: "State B", risk_label: "Emerging",
        channels: [], top_contributing_answers: [],
      },
    ],
    legal_tail_risk_exposure: {
      ...FULL_PAYLOAD.legal_tail_risk_exposure!,
      driving_factors: [{ category: "Wage and hour", rationale: "State X: $100,000.", triggering_answer: "Time records are informal." }],
    },
    service_cost_comparison: {
      target_service_name: "",
      service_estimate_low: null, service_estimate_high: null, pricing_model_note: "",
    },
    asset_evidence: {
      strongest_axes: ["attitude"],
      contributing_signals: [{ axis: "attitude", observation_text: "Most managers here develop their people and produce results." }],
      net_scores: { aptitude: 0, authority: 1.4, alliance: 0, attitude: 1.9 },
    },
    tactical_findings: [{
      section_id: "TC-PAYROLL", section_name: "Payroll & Wage-Hour", flagged_count: 2, total_count: 4,
      synthesis_text: "Overtime classifications may have drifted.", flagged_items: [],
    }],
  };
  // The dollar ledger path, with the switch on (the restorable state).
  const text = buildResultsText(phase3, undefined, { frictionDollarsVisible: true });

  it("opens with the executive summary", () => {
    expect(text.startsWith("Executive summary:\nThe summary sentence.")).toBe(true);
  });
  it("includes where strength shows up as the on-screen sentence and evidence, without scores", () => {
    expect(text).toContain(
      "Where strength shows up:\nYour answers show the most strength in Attitude.\n— Most managers here develop their people and produce results.",
    );
    expect(text).not.toContain("1.9");
    expect(text).not.toContain("net asset signal");
  });
  it("includes the friction tax ledger rows (no per-row figure) and the friction receipts", () => {
    expect(text).toContain("Friction tax ledger:\n— The Paper Tiger (Entrenched)\n  Decisions get made, then get reopened.\n— State B (Emerging)");
    expect(text).not.toContain("Estimates are calculated");
    expect(text).not.toContain("Estimate not available");
    expect(text).toContain("How the friction tax was calculated:\n— Payroll baseline: Estimated annual payroll: $1,000,000.");
  });
  it("includes the legal receipts, with the triggering answer when present", () => {
    expect(text).toContain("How the legal figure was calculated:");
    expect(text).toContain("— Wage and hour: State X: $100,000.");
    expect(text).toContain("  Based on your answers: Time records are informal.");
  });
  it("includes the cost comparison with separate timeframes, never a combined total", () => {
    expect(text).toContain("Cost comparison:");
    expect(text).toContain(`— ${FRICTION_TYPICAL_LOSS_LABEL}: $63,900`);
    expect(text).toContain("— Legal exposure, one-time if a claim arises: $100,000 – $450,000");
    expect(text).toContain("— People Tactics & Strategy: Ask for pricing.");
    expect(text).not.toContain("520,000");
  });
  it("includes the tactical review", () => {
    expect(text).toContain("— Payroll & Wage-Hour: 2 of 4 answers show a gap.");
    expect(text).toContain("  Overtime classifications may have drifted.");
  });
  it("hides the strength panel when every net score is 0, like the screen", () => {
    const zero = buildResultsText({
      ...phase3,
      asset_evidence: { strongest_axes: [], contributing_signals: [], net_scores: { aptitude: 0, authority: 0, alliance: 0, attitude: 0 } },
    });
    expect(zero).not.toContain("Where strength shows up");
  });
  it("groups ledger rows with the same evidence set into one row, evidence once", () => {
    const shared = ["Answer one.", "Answer two."];
    const grouped = buildResultsText({
      ...phase3,
      friction_tax_ledger: [
        { state_id: "a", state_name: "Cond A", risk_label: "Emerging",
          channels: ["turnover"], top_contributing_answers: shared },
        { state_id: "b", state_name: "Cond B", risk_label: "Entrenched",
          channels: ["engagement"], top_contributing_answers: [...shared].reverse() },
        { state_id: "c", state_name: "Cond C", risk_label: "Emerging",
          channels: [], top_contributing_answers: ["Answer three."] },
      ],
    }, undefined, { frictionDollarsVisible: true });
    expect(grouped).toContain(
      "— Cond A (Emerging), Cond B (Entrenched)\n  Answer one.\n  Answer two.",
    );
    expect(grouped.split("Answer one.").length - 1).toBe(1);
    expect(grouped).toContain("— Cond C (Emerging)\n  Answer three.");
    expect(grouped).not.toContain("highest standalone");
  });
  it("friction dollars hidden (default): conditions and their answers, no friction figure or footnote", () => {
    const hidden = buildResultsText(phase3);
    expect(FRICTION_DOLLARS_VISIBLE).toBe(false);
    expect(hidden).toContain(`${FRICTION_LEDGER_HEADING_NO_DOLLARS}:\n— The Paper Tiger (Entrenched)\n  Decisions get made, then get reopened.\n— State B (Emerging)`);
    expect(hidden).toContain(FRICTION_LEDGER_NOTE_NO_DOLLARS);
    for (const s of ["$20,000", "$28,000", "$63,900", "$35,400", "$1,000,000", "Friction tax", "friction tax",
                     "How the friction tax", "highest standalone", "Highest standalone", "Sources include",
                     "Estimates are calculated", "Drives cost through", "Each row estimates"]) {
      expect(hidden).not.toContain(s);
    }
    // Legal exposure and the rest of the cost comparison are unchanged.
    expect(hidden).toContain("Legal/Compliance exposure:\n$100,000 – $450,000");
    expect(hidden).toContain("Cost comparison:\n— Legal exposure, one-time if a claim arises: $100,000 – $450,000\n— People Tactics & Strategy: Ask for pricing.");
  });
  it("friction dollars hidden: a grouped row names every condition, evidence once", () => {
    const shared = ["Answer one.", "Answer two."];
    const g = buildResultsText({
      ...phase3,
      friction_tax_ledger: [
        { state_id: "a", state_name: "Cond A", risk_label: "Emerging",
          channels: ["turnover"], top_contributing_answers: shared },
        { state_id: "b", state_name: "Cond B", risk_label: "Entrenched",
          channels: ["engagement"], top_contributing_answers: [...shared].reverse() },
      ],
    });
    expect(g).toContain("— Cond A (Emerging), Cond B (Entrenched)\n  Answer one.\n  Answer two.");
    expect(g.split("Answer one.").length - 1).toBe(1);
  });
  it("friction dollars hidden, no priced legal exposure: the cost comparison is omitted entirely", () => {
    const t = buildResultsText({ ...phase3, legal_tail_risk_exposure: null });
    expect(t).not.toContain("Cost comparison:");
    expect(t).not.toContain("Ask for pricing");
  });
  it("hidden-state copy: plain language, no dashes or semicolons", () => {
    for (const s of [FRICTION_LEDGER_HEADING_NO_DOLLARS, FRICTION_LEDGER_NOTE_NO_DOLLARS]) {
      expect(s).not.toMatch(/[—–;]|--/);
    }
  });
  it("formats every dollar figure to 3 significant figures, half up, never $0 (A1)", () => {
    expect(formatUsd(4839283)).toBe("$4,840,000");
    expect(formatUsd(604214.4)).toBe("$604,000");
    expect(formatUsd(1800)).toBe("$1,800");
    expect(formatUsd(16550)).toBe("$16,600");
    expect(formatUsd(450)).toBe("$450");
    expect(formatUsd(16381908.3)).toBe("$16,400,000");
    expect(formatUsd(0.3)).not.toBe("$0");
    expect(formatUsd(0)).toBe("$0");
    expect(formatUsdRange(604214.4, 626278.8)).toBe("$604,000 – $626,000");
    expect(formatUsdRange(604214.4, 604400)).toBe("$604,000");
    const legal = buildResultsText({
      ...phase3,
      legal_tail_risk_exposure: { ...phase3.legal_tail_risk_exposure!, low: 604214.4, high: 626278.8 },
    });
    expect(legal).toContain("Legal/Compliance exposure:\n$604,000 – $626,000");
    expect(legal).not.toMatch(/\$[0-9,]+\.[0-9]/);
  });
  it("groupLedgerRows never groups rows that have no evidence", () => {
    const groups = groupLedgerRows([
      { state_id: "a", state_name: "A", risk_label: "Emerging", channels: [], top_contributing_answers: [] },
      { state_id: "b", state_name: "B", risk_label: "Emerging", channels: [], top_contributing_answers: [] },
    ]);
    expect(groups).toHaveLength(2);
  });
  it("on Call 2 failure, copies what the screen shows: referral chips over each section's answers", () => {
    const tactical: TacticalSectionResult[] = [{
      question_set_id: "TC-PAYROLL",
      referral: ["HR Consulting", "Managed Payroll"],
      answers: [{
        question_id: "TC-PAY-01", question_text: "How are overtime hours tracked?",
        selected_option_text: "Informally, by each manager.", intent: "",
      }],
    }];
    const failed = buildResultsText({ ...phase3, tactical_findings: [] }, tactical);
    expect(failed).toContain(
      "Tactical & compliance review:\n— HR Consulting, Managed Payroll\n  How are overtime hours tracked?\n    Informally, by each manager.",
    );
    expect(failed).not.toContain("answers show a gap");
    // With findings present the tactical results are not read (unchanged behavior).
    const ok = buildResultsText(phase3, tactical);
    expect(ok).not.toContain("Managed Payroll");
    expect(ok).toContain("— Payroll & Wage-Hour: 2 of 4 answers show a gap.");
  });
  it("copies the Ohio net-worth caveat from the shared constant, with no spaced double hyphen", () => {
    const ohio = buildResultsText({
      ...phase3,
      legal_tail_risk_exposure: { ...phase3.legal_tail_risk_exposure!, has_uncollected_net_worth_caveat: true },
    });
    expect(ohio).toContain(OHIO_NET_WORTH_CAVEAT);
    expect(OHIO_NET_WORTH_CAVEAT).not.toContain("--");
  });
  it("omits every Phase 3 section when the payload has none", () => {
    const plain = buildResultsText(MINIMAL_PAYLOAD);
    for (const s of ["Executive summary:", "Where strength shows up", "How the legal figure", "Cost comparison:", "Tactical & compliance review:", "Friction tax ledger:", "Ohio"]) {
      expect(plain).not.toContain(s);
    }
  });
});
