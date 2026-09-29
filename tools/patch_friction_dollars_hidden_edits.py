# Anchor/replacement data for tools/patch_friction_dollars_hidden.py.
# Executed with HEADING, NOTE and RULE in scope. Each entry: (exact old, new).

EDITS = {}

# ── web/lib/output-text.ts ────────────────────────────────────────────────────
EDITS["web/lib/output-text.ts"] = [
    (
        "// One ledger row per distinct evidence set (P2). Rows whose\n",
        "// Friction dollar switch (Pete, 2026-09-28, option C): friction-tax dollar\n"
        "// figures are hidden on both brands until the friction methodology is\n"
        "// rebuilt. The engine still computes them and the payload still carries\n"
        "// them. Set to true to restore the dollar ledger, its calculation steps,\n"
        "// its footnotes and the friction line in the cost comparison. Legal\n"
        "// exposure is not affected by this switch.\n"
        "export const FRICTION_DOLLARS_VISIBLE = false;\n"
        "\n"
        "// Ledger copy while friction dollars are hidden.\n"
        f'export const FRICTION_LEDGER_HEADING_NO_DOLLARS = "{HEADING}";\n'
        f'export const FRICTION_LEDGER_NOTE_NO_DOLLARS = "{NOTE}";\n'
        "\n"
        "// One ledger row per distinct evidence set (P2). Rows whose\n",
    ),
    (
        "export function buildResultsText(\n"
        "  payload: PrivateOutputPayload,\n"
        "  tacticalResults?: TacticalSectionResult[],\n"
        "): string {\n",
        "// options.frictionDollarsVisible defaults to FRICTION_DOLLARS_VISIBLE, the\n"
        "// same switch the screen reads. Tests pass it to cover both states.\n"
        "export function buildResultsText(\n"
        "  payload: PrivateOutputPayload,\n"
        "  tacticalResults?: TacticalSectionResult[],\n"
        "  options: { frictionDollarsVisible?: boolean } = {},\n"
        "): string {\n"
        "  const frictionVisible = options.frictionDollarsVisible ?? FRICTION_DOLLARS_VISIBLE;\n",
    ),
    (
        "  const ledger = payload.friction_tax_ledger ?? [];\n"
        "  if (ledger.length > 0) {\n"
        "    const block = [\"Friction tax ledger:\"];\n",
        "  const ledger = payload.friction_tax_ledger ?? [];\n"
        "  if (ledger.length > 0 && !frictionVisible) {\n"
        "    // Friction dollars hidden: the conditions and the answers behind\n"
        "    // them. No figures, no footnotes, no calculation steps.\n"
        "    const block = [`${FRICTION_LEDGER_HEADING_NO_DOLLARS}:`];\n"
        "    for (const group of groupLedgerRows(ledger, stateNameById)) {\n"
        "      block.push(`— ${group.conditions.map((c) => `${c.name} (${c.risk_label})`).join(\", \")}`);\n"
        "      for (const t of group.top_contributing_answers) block.push(`  ${t}`);\n"
        "    }\n"
        "    add(block);\n"
        "    add([FRICTION_LEDGER_NOTE_NO_DOLLARS]);\n"
        "  } else if (ledger.length > 0) {\n"
        "    const block = [\"Friction tax ledger:\"];\n",
    ),
    (
        "  const friction = payload.friction_tax_estimate;\n"
        "  const scc = payload.service_cost_comparison;\n",
        "  const friction = frictionVisible ? payload.friction_tax_estimate : null;\n"
        "  const scc = payload.service_cost_comparison;\n",
    ),
]

# ── web/components/PrivateOutput.tsx ──────────────────────────────────────────
EDITS["web/components/PrivateOutput.tsx"] = [
    (
        "  buildConditionRows, FRICTION_TAX_LEDGER_FOOTNOTE, FRICTION_TAX_LEDGER_STANDALONE_NOTE,\n",
        "  buildConditionRows, FRICTION_DOLLARS_VISIBLE, FRICTION_LEDGER_HEADING_NO_DOLLARS,\n"
        "  FRICTION_LEDGER_NOTE_NO_DOLLARS, FRICTION_TAX_LEDGER_FOOTNOTE, FRICTION_TAX_LEDGER_STANDALONE_NOTE,\n",
    ),
    (
        "          <summary className=\"text-[11px] uppercase tracking-wide text-slate mb-3 cursor-pointer\">\n"
        "            Friction tax ledger\n"
        "          </summary>\n",
        "          <summary className=\"text-[11px] uppercase tracking-wide text-slate mb-3 cursor-pointer\">\n"
        "            {FRICTION_DOLLARS_VISIBLE ? \"Friction tax ledger\" : FRICTION_LEDGER_HEADING_NO_DOLLARS}\n"
        "          </summary>\n",
    ),
    (
        "                  <p className=\"text-[13px] text-charcoal mb-1\">\n"
        "                    {figure ? (\n",
        "                  {/* Option C: no figure line while friction dollars are hidden. */}\n"
        "                  {FRICTION_DOLLARS_VISIBLE && (\n"
        "                  <p className=\"text-[13px] text-charcoal mb-1\">\n"
        "                    {figure ? (\n",
    ),
    (
        "                        Estimate not available for {grouped ? \"these conditions\" : \"this condition\"}.\n"
        "                      </span>\n"
        "                    )}\n"
        "                  </p>\n",
        "                        Estimate not available for {grouped ? \"these conditions\" : \"this condition\"}.\n"
        "                      </span>\n"
        "                    )}\n"
        "                  </p>\n"
        "                  )}\n",
    ),
    (
        "          <p className=\"text-[11px] text-slate mt-3 leading-relaxed\">\n"
        "            {FRICTION_TAX_LEDGER_STANDALONE_NOTE}\n"
        "          </p>\n"
        "          <p className=\"text-[11px] text-slate mt-2 leading-relaxed\">\n"
        "            {FRICTION_TAX_LEDGER_FOOTNOTE}\n"
        "          </p>\n"
        "          <EvidenceReceipts receipts={payload.friction_tax_estimate?.driving_factors} />\n",
        "          {FRICTION_DOLLARS_VISIBLE ? (\n"
        "            <>\n"
        "              <p className=\"text-[11px] text-slate mt-3 leading-relaxed\">\n"
        "                {FRICTION_TAX_LEDGER_STANDALONE_NOTE}\n"
        "              </p>\n"
        "              <p className=\"text-[11px] text-slate mt-2 leading-relaxed\">\n"
        "                {FRICTION_TAX_LEDGER_FOOTNOTE}\n"
        "              </p>\n"
        "              <EvidenceReceipts receipts={payload.friction_tax_estimate?.driving_factors} />\n"
        "            </>\n"
        "          ) : (\n"
        "            <p className=\"text-[11px] text-slate mt-3 leading-relaxed\">\n"
        "              {FRICTION_LEDGER_NOTE_NO_DOLLARS}\n"
        "            </p>\n"
        "          )}\n",
    ),
    (
        "        friction={payload.friction_tax_estimate}\n",
        "        friction={FRICTION_DOLLARS_VISIBLE ? payload.friction_tax_estimate : null}\n",
    ),
]

# ── Engine prompt rule, both brands (Call 1 and Call 2) ───────────────────────
EDITS["engine/output_synthesis.py"] = [
    (
        "Short sentences preferred over long ones. Plain words preferred over elevated ones.\n",
        "Short sentences preferred over long ones. Plain words preferred over elevated ones.\n"
        f"{RULE}\n",
    ),
]
EDITS["engine/tactical_synthesis.py"] = [
    (
        "- Do not cite specific laws, statutes, penalty amounts, or deadlines.\n",
        "- Do not cite specific laws, statutes, penalty amounts, or deadlines.\n"
        f"- {RULE}\n",
    ),
]

# ── vitest: web/lib/output-text.test.ts ───────────────────────────────────────
_HIDDEN_TESTS = r'''  it("friction dollars hidden (default): conditions and their answers, no friction figure or footnote", () => {
    const hidden = buildResultsText(phase3);
    expect(FRICTION_DOLLARS_VISIBLE).toBe(false);
    expect(hidden).toContain(`${FRICTION_LEDGER_HEADING_NO_DOLLARS}:\n— The Paper Tiger (Entrenched)\n  Decisions get made, then get reopened.\n— State B (Emerging)`);
    expect(hidden).toContain(FRICTION_LEDGER_NOTE_NO_DOLLARS);
    for (const s of ["$20,000", "$28,000", "$50,000", "$70,000", "$1,000,000", "Friction tax", "friction tax",
                     "How the friction tax", "highest standalone", "Highest standalone", "Sources include",
                     "Estimates are calculated", "Drives cost through", FRICTION_TAX_LEDGER_STANDALONE_NOTE]) {
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
          dollar_exposure: { low: 100400, high: 140560, currency: "USD" }, top_contributing_answers: shared },
        { state_id: "b", state_name: "Cond B", risk_label: "Entrenched",
          dollar_exposure: { low: 300499, high: 420699, currency: "USD" }, top_contributing_answers: [...shared].reverse() },
      ],
    });
    expect(g).toContain("— Cond A (Emerging), Cond B (Entrenched)\n  Answer one.\n  Answer two.");
    expect(g.split("Answer one.").length - 1).toBe(1);
    // The ledger's own figures ($100,400 -> $100,000 collides with the legal
    // fixture, so the other three are checked) never appear.
    for (const s of ["$141,000", "$300,000", "$421,000"]) expect(g).not.toContain(s);
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
'''

EDITS["web/lib/output-text.test.ts"] = [
    (
        "  FRICTION_TAX_LEDGER_STANDALONE_NOTE, groupLedgerRows, formatUsd, formatUsdRange,\n",
        "  FRICTION_TAX_LEDGER_STANDALONE_NOTE, groupLedgerRows, formatUsd, formatUsdRange,\n"
        "  FRICTION_DOLLARS_VISIBLE, FRICTION_LEDGER_HEADING_NO_DOLLARS, FRICTION_LEDGER_NOTE_NO_DOLLARS,\n",
    ),
    (
        "  const text = buildResultsText(phase3);\n",
        "  // The dollar ledger path, with the switch on (the restorable state).\n"
        "  const text = buildResultsText(phase3, undefined, { frictionDollarsVisible: true });\n",
    ),
    (
        "      ],\n"
        "    });\n"
        "    expect(grouped).toContain(\n",
        "      ],\n"
        "    }, undefined, { frictionDollarsVisible: true });\n"
        "    expect(grouped).toContain(\n",
    ),
    (
        '  it("formats every dollar figure to 3 significant figures, half up, never $0 (A1)", () => {\n',
        _HIDDEN_TESTS
        + '  it("formats every dollar figure to 3 significant figures, half up, never $0 (A1)", () => {\n',
    ),
]

# ── Python: the prompt rule is present in Call 1 and Call 2 ───────────────────
EDITS["tools/test_phase1_report_data.py"] = [
    (
        "# ── 9. Lead resolution family in both routing modes ─────────────────────────────\n",
        "# Option C: Call 1 and Call 2 may not state dollar figures or payroll shares\n"
        f"_RULE = {RULE!r}\n"
        "check(\"Option C: Call 1 system prompt carries the no-dollar-figures rule\",\n"
        "      _RULE in OUTPUT_SYNTHESIS_SYSTEM_PROMPT)\n"
        "check(\"Option C: Call 2 system prompt carries the no-dollar-figures rule\",\n"
        "      \"- \" + _RULE in TACTICAL_SYNTHESIS_SYSTEM_PROMPT)\n"
        "\n"
        "\n"
        "# ── 9. Lead resolution family in both routing modes ─────────────────────────────\n",
    ),
]

# ── New screen-render test (server render, no DOM needed) ─────────────────────
NEW_FILES = {}
NEW_FILES["web/components/PrivateOutput.friction.test.ts"] = r'''import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { PrivateOutputPayload } from "@/lib/types";

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
  friction_tax_estimate: {
    low: 1234567, high: 1728394, currency: "USD",
    driving_factors: [{ category: "Payroll baseline", rationale: "Estimated annual payroll: $9,870,000." }],
  },
  friction_tax_ledger: [{
    state_id: "built_to_fail", state_name: "Built to Fail", risk_label: "Emerging",
    dollar_exposure: { low: 555555, high: 777777, currency: "USD" },
    top_contributing_answers: ["Some processes here are out of date or inconsistently followed."],
  }],
  legal_tail_risk_exposure: {
    low: 100000, high: 450000, currency: "USD", band: "Elevated",
    caveat: "A directional estimate.", has_unpriced_conditions: false, unpriced_state_ids: [],
    coverage_basis: "state", has_partial_jurisdictions: false, has_uncollected_net_worth_caveat: false,
    specific_caveat: null,
  },
  service_cost_comparison: {
    target_service_name: "People Tactics & Strategy", inaction_cost_low: 1334567, inaction_cost_high: 2178394,
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
    for (const s of ["$1,230,000", "$1,730,000", "$556,000", "$778,000", "$9,870,000",
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
'''
