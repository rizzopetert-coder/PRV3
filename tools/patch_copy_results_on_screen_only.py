"""
Part C -- Copy results emits only what PrivateOutput renders on screen
(Pete, 2026-09-28). Removes the dimensional shape, net asset scores, the old
co-occurring and severity-score sections, and the whole additional-detail
section (engine metadata and intake echo). Conditions come from the same
derivation as the on-screen list (buildConditionRows, moved here from
PrivateOutput.tsx), the friction ledger and its footnote are added since the
screen shows them, and the ledger footnote becomes one shared constant.

Additions (Pete, 2026-09-28):
  1. Call 2 failure: the copy includes what the screen shows for the
     tactical review (each section's referral chips over its answer list).
     CopyResultsButton now receives tacticalResults for this.
  2. The Ohio net-worth caveat's spaced "--" is fixed at its source: one
     shared constant (OHIO_NET_WORTH_CAVEAT), two sentences, used by both
     the screen and the copy.

Usage (from repo root):
    python tools/patch_copy_results_on_screen_only.py --dry-run
    python tools/patch_copy_results_on_screen_only.py --write
    --root <dir>  apply against another checkout (verification worktree)
"""
import argparse
import difflib
import pathlib
import sys

NEW_TAIL = r'''// ---------------------------------------------------------------------------
// buildResultsText -- the "Copy results as text" assembly.
//
// Emits only what PrivateOutput.tsx renders on screen, in its render order,
// with its own omit-when-empty rules (Pete, 2026-09-28). Nothing the screen
// does not show is copied: no dimensional percentages, no net asset scores,
// no numeric severity scores, no engine metadata, no intake echo. The
// calculation steps stay, since the screen shows them too.
//
// Brand: the text is built from payload fields only, which are already
// brand-safe by the time they reach the client (diagnostic-completion.ts).
// The screen's brand-specific extras (PR book links, the PR engage CTA, the
// "About this report" drawer) are links or help text, not report content,
// and are left out on both brands.
//
// No markdown syntax -- plain labels and blank-line separation only. List
// items use an em dash prefix, the same idiom the on-screen lists use.
// ---------------------------------------------------------------------------
function money(low: number, high: number): string {
  const f = (v: number) => `$${Math.round(v).toLocaleString()}`;
  return low === high ? f(low) : `${f(low)} – ${f(high)}`;
}

function receiptLines(title: string, receipts: EvidenceReceipt[] | undefined): string[] {
  if (!receipts || receipts.length === 0) return [];
  const out = [title];
  for (const r of receipts) {
    out.push(`— ${r.category}: ${r.rationale}`);
    if (r.triggering_answer) out.push(`  Based on your answers: ${r.triggering_answer}`);
  }
  return out;
}

const ASSET_AXIS_NAMES: Record<string, string> = {
  aptitude: "Aptitude",
  authority: "Authority",
  alliance: "Alliance",
  attitude: "Attitude",
};

// Block 4f footnote. Shared with PrivateOutput.tsx so the screen and the
// copied text cannot drift.
export const FRICTION_TAX_LEDGER_FOOTNOTE =
  "Estimates are calculated from your organization's size, industry, and " +
  "structure, then scaled to how deeply organizational risk conditions " +
  "have taken root. The financial risk range draws on published research " +
  "including public wage and compensation data and studies on turnover, " +
  "disengagement, and lost productivity. Sources include McKinsey, SHRM, " +
  "Gallup, and other widely-recognized credible sources. Figures shown as " +
  "a range reflect the actual uncertainty identified in your diagnostic " +
  "result, and are not indicative of imprecision in the diagnosis.";

// Block 4d Ohio punitive-cap caveat. Shared with PrivateOutput.tsx so the
// screen and the copied text cannot drift.
export const OHIO_NET_WORTH_CAVEAT =
  "This figure reflects twice the compensatory-damages estimate above, capped " +
  "at Ohio's $350,000 ceiling. It does not reflect the net-worth alternative " +
  "Ohio law also applies (R.C. 2315.21(D)(2)(b)). Since net worth isn't " +
  "collected here, the true cap could be materially lower than what's " +
  "reflected here.";

// Conditions list rows (Phase 2): every qualifying state, descending score.
// all_qualified_states is already score-sorted by the engine; older
// payloads, self-select, and dev fixtures fall back to primary + secondary.
// Shared with PrivateOutput.tsx so the on-screen list and the copied text
// come from one derivation. Same shape as ConditionsList.tsx's ConditionRow.
export interface ConditionRowData {
  id: string;
  name: string;
  prose: string;
  tier: SeverityTier | null;
  severity: { tier: SeverityTier; score_0_100: number } | null;
}

export function buildConditionRows(payload: PrivateOutputPayload): ConditionRowData[] {
  const severityById = new Map(
    (payload.severity_by_state ?? []).map((e) => [e.state_id, e] as const),
  );
  const source =
    payload.all_qualified_states && payload.all_qualified_states.length > 0
      ? payload.all_qualified_states.map((s) => ({
          id: s.state_id, name: s.state_name, prose: s.descriptive_prose,
        }))
      : [payload.primary_state, ...payload.secondary_states].map((s) => ({
          id: s.id, name: s.name, prose: s.descriptive_prose ?? "",
        }));
  return source.map((s, i) => {
    const entry = severityById.get(s.id);
    return {
      ...s,
      tier: entry?.tier ?? (i === 0 ? payload.severity : null),
      severity: entry ? { tier: entry.tier, score_0_100: entry.score_0_100 } : null,
    };
  });
}

// tacticalResults: the hr-dx TC answers, the same data PrivateOutput passes
// to TacticalReview. Only read when Call 2 failed (no tactical_findings),
// where the screen shows referral chips over the answer list.
export function buildResultsText(
  payload: PrivateOutputPayload,
  tacticalResults?: TacticalSectionResult[],
): string {
  // Each block is one paragraph or list; blocks are separated by a blank line.
  const blocks: string[][] = [];
  const add = (block: string[]) => {
    if (block.length > 0) blocks.push(block);
  };

  const legal = payload.legal_tail_risk_exposure;
  const legalHasPrice = legal !== null && legal.low !== null && legal.high !== null;
  const conditionRows = buildConditionRows(payload);
  const stateNameById = new Map<string, string>([
    [payload.primary_state.id, payload.primary_state.name],
    ...payload.secondary_states.map((s): [string, string] => [s.id, s.name]),
    ...conditionRows.map((r): [string, string] => [r.id, r.name]),
  ]);

  // Executive summary (Call 3), when present.
  if (payload.synthesis.executive_summary) {
    add(["Executive summary:", payload.synthesis.executive_summary]);
  }

  // Observable indicators. (The constellation above it is visual only.)
  const indicators = payload.synthesis.observable_indicators ?? [];
  if (indicators.length > 0) {
    add(["Observable indicators:", ...indicators.map((i) => `— ${i}`)]);
  }

  // Conditions identified: name and tier badge, full prose (every card is
  // expandable on screen), severity paragraph on the lead only.
  if (conditionRows.length > 0) {
    const block = ["Conditions identified:"];
    conditionRows.forEach((row, i) => {
      block.push(`— ${row.name}${row.tier ? ` (${row.tier})` : ""}`);
      if (row.prose) block.push(`  ${row.prose}`);
      if (i === 0) block.push(`  ${SEVERITY_ANCHOR[payload.severity]}`);
    });
    add(block);
  }

  // Narrative: headline, liability condition (or the routing fallback the
  // screen uses), framing text.
  const usedRoutingInBlock2 =
    !payload.synthesis.liability_condition_text && Boolean(payload.resolution_routing);
  if (payload.synthesis.headline) add([payload.synthesis.headline]);
  const block2 = payload.synthesis.liability_condition_text || payload.resolution_routing;
  if (block2) add([block2]);
  if (payload.synthesis.framing_text) add([payload.synthesis.framing_text]);

  // Asset block: primary asset domain, anchor text, where strength shows up
  // (the sentence and the quoted evidence, never the bar values).
  const ev = payload.asset_evidence;
  if (payload.synthesis.asset_resolution_anchor_text || payload.primary_asset_domain || ev) {
    const block: string[] = [];
    if (payload.primary_asset_domain) block.push(`Primary asset domain: ${payload.primary_asset_domain}`);
    if (payload.synthesis.asset_resolution_anchor_text) block.push(payload.synthesis.asset_resolution_anchor_text);
    add(block);
  }
  if (ev) {
    const max = Math.max(...Object.keys(ASSET_AXIS_NAMES).map(
      (a) => ev.net_scores[a as keyof typeof ev.net_scores] ?? 0,
    ));
    if (max > 0) {
      const strongest = ev.strongest_axes.map((a) => ASSET_AXIS_NAMES[a] ?? a);
      add([
        "Where strength shows up:",
        `Your answers show the most strength in ${joinNames(strongest)}.`,
        ...ev.contributing_signals.map((s) => `— ${s.observation_text}`),
      ]);
    }
  }

  // Resolution pathway.
  const pathway = [`Resolution pathway: ${payload.resolution_family}`];
  if (payload.synthesis.resolution_framing_text) {
    pathway.push(payload.synthesis.resolution_framing_text);
  } else if (!usedRoutingInBlock2 && payload.resolution_routing) {
    pathway.push(payload.resolution_routing);
  }
  add(pathway);

  // Legal/Compliance exposure, with its calculation steps.
  if (legal) {
    const block = ["Legal/Compliance exposure:"];
    if (legalHasPrice) {
      const sym = legal.currency === "USD" ? "$" : "";
      block.push(
        legal.low === legal.high
          ? `Estimated exposure: ${sym}${legal.low!.toLocaleString()}`
          : `${sym}${legal.low!.toLocaleString()} – ${sym}${legal.high!.toLocaleString()}`,
      );
    }
    if (legalHasPrice && legal.coverage_basis === "federal_baseline") {
      block.push(
        "This range applies a federal coverage threshold, since no confirmed state-specific threshold applied to the jurisdictions on file. Actual state law in those jurisdictions could set a materially lower bar than what's reflected here.",
      );
    } else if (legalHasPrice && legal.coverage_basis === "mixed") {
      block.push(
        "This range blends a confirmed state-specific threshold with a federal coverage threshold used where no confirmed state-specific one applied. In the jurisdictions relying on the federal threshold, actual state law could set a materially lower bar than what's reflected here.",
      );
    }
    if (legalHasPrice && legal.has_partial_jurisdictions) {
      block.push(
        "State law in this jurisdiction was not independently verified and may set a different threshold than what's reflected here.",
      );
    }
    if (legalHasPrice && legal.has_uncollected_net_worth_caveat) {
      block.push(OHIO_NET_WORTH_CAVEAT);
    }
    if (legalHasPrice && legal.specific_caveat) block.push(legal.specific_caveat);
    if (legal.unpriced_state_ids.length > 0) {
      const names = legal.unpriced_state_ids.map((id) => stateNameById.get(id) ?? id);
      block.push(`Real exposure current data can't price precisely for: ${joinNames(names)}.`);
    }
    block.push(legal.caveat);
    add(block);
    add(receiptLines("How the legal figure was calculated:", legal.driving_factors));
  }

  // Friction tax ledger, with its footnote and calculation steps. The screen
  // shows the friction receipts inside the ledger, so they share its gate.
  const ledger = payload.friction_tax_ledger ?? [];
  if (ledger.length > 0) {
    const block = ["Friction tax ledger:"];
    for (const row of ledger) {
      const d = row.dollar_exposure;
      const sym = d?.currency === "USD" ? "$" : "";
      const amount = d
        ? d.low === d.high
          ? `Estimated exposure: ${sym}${d.low.toLocaleString()}`
          : `${sym}${d.low.toLocaleString()} – ${sym}${d.high.toLocaleString()}`
        : "Estimate not available for this condition.";
      block.push(`— ${stateNameById.get(row.state_id) ?? row.state_name} (${row.risk_label}): ${amount}`);
      for (const t of row.top_contributing_answers) block.push(`  ${t}`);
    }
    add(block);
    add([FRICTION_TAX_LEDGER_FOOTNOTE]);
    add(receiptLines("How the friction tax was calculated:", payload.friction_tax_estimate?.driving_factors));
  }

  // Cost comparison (same gate as the on-screen CostComparison).
  const friction = payload.friction_tax_estimate;
  const scc = payload.service_cost_comparison;
  if (scc && (friction || legalHasPrice)) {
    const block = ["Cost comparison:"];
    if (friction) block.push(`— Friction tax, recurring every year: ${money(friction.low, friction.high)}`);
    if (legalHasPrice) block.push(`— Legal exposure, one-time if a claim arises: ${money(legal!.low!, legal!.high!)}`);
    const service = scc.target_service_name || payload.resolution_family;
    const priced = scc.service_estimate_low !== null && scc.service_estimate_high !== null;
    block.push(
      priced
        ? `— ${service}: ${money(scc.service_estimate_low!, scc.service_estimate_high!)}${scc.pricing_model_note ? `. ${scc.pricing_model_note}` : ""}`
        : `— ${service ? `${service}: ` : ""}Ask for pricing. Scoped to what this diagnostic found.`,
    );
    add(block);
  }

  // Tactical & compliance review (hr-dx only in practice).
  const findings = payload.tactical_findings ?? [];
  if (findings.length > 0) {
    const block = ["Tactical & compliance review:"];
    for (const f of findings) {
      const count = f.flagged_count === 0
        ? `No gaps in these ${f.total_count} answers.`
        : `${f.flagged_count} of ${f.total_count} answers show a gap.`;
      block.push(`— ${f.section_name}: ${count}`);
      if (f.synthesis_text) block.push(`  ${f.synthesis_text}`);
    }
    add(block);
  } else if (tacticalResults && tacticalResults.length > 0) {
    // Call 2 failed: the screen shows each section's referral chips over its
    // answer list, with no section heading or count (ReportDetails.tsx).
    const block = ["Tactical & compliance review:"];
    for (const section of tacticalResults) {
      if (section.referral.length > 0) block.push(`— ${section.referral.join(", ")}`);
      for (const a of section.answers) {
        block.push(`  ${a.question_text}`, `    ${a.selected_option_text}`);
      }
    }
    add(block);
  }

  return blocks.map((b) => b.join("\n")).join("\n\n");
}
'''
NEW_TESTS = r'''describe("buildResultsText -- full payload, every field present", () => {
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
    expect(text).toContain("Primary asset domain: Governance Discipline");
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
      "The liability condition text.", "Primary asset domain:", "Resolution pathway:",
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
      low: 50000, high: 70000, currency: "USD",
      driving_factors: [{ category: "Payroll baseline", rationale: "Estimated annual payroll: $1,000,000." }],
    },
    friction_tax_ledger: [
      {
        state_id: "the_paper_tiger", state_name: "The Paper Tiger", risk_label: "Entrenched",
        dollar_exposure: { low: 20000, high: 28000, currency: "USD" },
        top_contributing_answers: ["Decisions get made, then get reopened."],
      },
      {
        state_id: "state_b", state_name: "State B", risk_label: "Emerging",
        dollar_exposure: null, top_contributing_answers: [],
      },
    ],
    legal_tail_risk_exposure: {
      ...FULL_PAYLOAD.legal_tail_risk_exposure!,
      driving_factors: [{ category: "Wage and hour", rationale: "State X: $100,000.", triggering_answer: "Time records are informal." }],
    },
    service_cost_comparison: {
      target_service_name: "", inaction_cost_low: 150000, inaction_cost_high: 520000,
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
  const text = buildResultsText(phase3);

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
  it("includes the friction tax ledger rows, the footnote, and the friction receipts", () => {
    expect(text).toContain("— The Paper Tiger (Entrenched): $20,000 – $28,000\n  Decisions get made, then get reopened.");
    expect(text).toContain("— State B (Emerging): Estimate not available for this condition.");
    expect(text).toContain("Estimates are calculated from your organization's size");
    expect(text).toContain("How the friction tax was calculated:\n— Payroll baseline: Estimated annual payroll: $1,000,000.");
  });
  it("includes the legal receipts, with the triggering answer when present", () => {
    expect(text).toContain("How the legal figure was calculated:");
    expect(text).toContain("— Wage and hour: State X: $100,000.");
    expect(text).toContain("  Based on your answers: Time records are informal.");
  });
  it("includes the cost comparison with separate timeframes, never a combined total", () => {
    expect(text).toContain("Cost comparison:");
    expect(text).toContain("— Friction tax, recurring every year: $50,000 – $70,000");
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
'''

OT = "web/lib/output-text.ts"
OTT = "web/lib/output-text.test.ts"
PO = "web/components/PrivateOutput.tsx"
CRB = "web/components/CopyResultsButton.tsx"

PCT = """function pct(ratio: number): string {
  return `${Math.round(ratio * 100)}%`;
}

"""
TAIL_ANCHOR = "// ---------------------------------------------------------------------------\n// buildResultsText -- the full"
OT_IMPORT_OLD = 'import type { EvidenceReceipt, PrivateOutputPayload, SeverityTier, StateRef } from "@/lib/types";'
OT_IMPORT_NEW = 'import type { EvidenceReceipt, PrivateOutputPayload, SeverityTier, StateRef, TacticalSectionResult } from "@/lib/types";'

TEST_ANCHOR = 'describe("buildResultsText -- full payload, every field present", () => {'
TEST_IMPORT_OLD = (
    'import { buildResultsText, firstSentence, joinNames, buildCoreCluster } from "./output-text";\n'
    'import type { PrivateOutputPayload, StateRef } from "./types";\n'
)
TEST_IMPORT_NEW = (
    'import { buildResultsText, firstSentence, joinNames, buildCoreCluster, OHIO_NET_WORTH_CAVEAT } from "./output-text";\n'
    'import type { PrivateOutputPayload, StateRef, TacticalSectionResult } from "./types";\n'
)

PO_IMPORT_OLD = 'import { joinNames } from "@/lib/output-text";'
PO_IMPORT_NEW = 'import { buildConditionRows, FRICTION_TAX_LEDGER_FOOTNOTE, joinNames, OHIO_NET_WORTH_CAVEAT } from "@/lib/output-text";'
PO_FOOTNOTE_START = "// Friction tax ledger -- Block 4f. One shared footnote for the whole"
PO_FOOTNOTE_END = '"result, and are not indicative of imprecision in the diagnosis.";\n\n'
PO_ROWS_START = "  // Phase 2 conditions list: every qualifying state, descending score."
PO_ROWS_END = "      severity: entry ? { tier: entry.tier, score_0_100: entry.score_0_100 } : null,\n    };\n  });\n"
PO_ROWS_NEW = (
    "  // Phase 2 conditions list: every qualifying state, descending score.\n"
    "  // Shared derivation with the Copy results text (output-text.ts).\n"
    "  const conditionRows: ConditionRow[] = buildConditionRows(payload);\n"
)
PO_OHIO_OLD = (
    "              This figure reflects twice the compensatory-damages\n"
    "              estimate above, capped at Ohio&apos;s $350,000 ceiling --\n"
    "              not the net-worth alternative Ohio law also applies\n"
    "              (R.C. 2315.21(D)(2)(b)). Since net worth isn&apos;t\n"
    "              collected here, the true cap could be materially lower\n"
    "              than what&apos;s reflected here.\n"
)
PO_OHIO_NEW = "              {OHIO_NET_WORTH_CAVEAT}\n"
PO_COPY_OLD = "        <CopyResultsButton payload={payload} />\n"
PO_COPY_NEW = "        <CopyResultsButton payload={payload} tacticalResults={tacticalResults} />\n"

CRB_EDITS = [
    ('import type { PrivateOutputPayload } from "@/lib/types";',
     'import type { PrivateOutputPayload, TacticalSectionResult } from "@/lib/types";'),
    ("interface CopyResultsButtonProps {\n  payload: PrivateOutputPayload;\n}\n",
     "interface CopyResultsButtonProps {\n  payload: PrivateOutputPayload;\n"
     "  // hr-dx TC answers, copied only when Call 2 failed (see buildResultsText).\n"
     "  tacticalResults?: TacticalSectionResult[];\n}\n"),
    ("export default function CopyResultsButton({ payload }: CopyResultsButtonProps) {",
     "export default function CopyResultsButton({ payload, tacticalResults }: CopyResultsButtonProps) {"),
    ("    await navigator.clipboard.writeText(buildResultsText(payload));",
     "    await navigator.clipboard.writeText(buildResultsText(payload, tacticalResults));"),
]


def once(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit(f"[FAIL] anchor found {text.count(old)} times: {label}")
    return text.replace(old, new, 1)


def cut(text, start, end, label):
    i = text.find(start)
    j = text.find(end, i)
    if i < 0 or j < 0 or text.count(start) != 1:
        raise SystemExit(f"[FAIL] anchor not unique/found: {label}")
    return text[:i], text[j + len(end):]


def plan(root: pathlib.Path) -> dict:
    out = {}
    t = (root / OT).read_text(encoding="utf-8")
    t = once(t, OT_IMPORT_OLD, OT_IMPORT_NEW, "output-text import")
    t = once(t, PCT, "", "pct helper")
    if t.count(TAIL_ANCHOR) != 1:
        raise SystemExit("[FAIL] output-text.ts tail anchor")
    out[OT] = t[: t.index(TAIL_ANCHOR)] + NEW_TAIL

    t = (root / OTT).read_text(encoding="utf-8")
    t = once(t, TEST_IMPORT_OLD, TEST_IMPORT_NEW, "test imports")
    if t.count(TEST_ANCHOR) != 1:
        raise SystemExit("[FAIL] output-text.test.ts anchor")
    out[OTT] = t[: t.index(TEST_ANCHOR)] + NEW_TESTS

    t = (root / PO).read_text(encoding="utf-8")
    t = once(t, PO_IMPORT_OLD, PO_IMPORT_NEW, "PrivateOutput import")
    a, b = cut(t, PO_FOOTNOTE_START, PO_FOOTNOTE_END, "footnote const")
    t = a + b
    a, b = cut(t, PO_ROWS_START, PO_ROWS_END, "conditionRows block")
    t = a + PO_ROWS_NEW + b
    t = once(t, PO_OHIO_OLD, PO_OHIO_NEW, "Ohio caveat JSX")
    t = once(t, PO_COPY_OLD, PO_COPY_NEW, "CopyResultsButton call")
    out[PO] = t

    t = (root / CRB).read_text(encoding="utf-8")
    for old, new in CRB_EDITS:
        t = once(t, old, new, "CopyResultsButton")
    out[CRB] = t
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # the diff carries em-dashes
    root = pathlib.Path(args.root)
    new = plan(root)
    for rel, content in new.items():
        old = (root / rel).read_text(encoding="utf-8")
        if args.dry_run:
            sys.stdout.writelines(difflib.unified_diff(
                old.splitlines(True), content.splitlines(True), f"a/{rel}", f"b/{rel}"))
        else:
            (root / rel).write_text(content, encoding="utf-8")
            print(f"[WROTE] {rel}")
    if args.dry_run:
        print("\nDry run only, nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
