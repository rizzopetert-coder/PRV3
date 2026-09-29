// "Copy results as text" -- this session. Pure text-assembly logic,
// testable in isolation, following the same extract-shared-pure-logic
// discipline as session-store.ts's helpers (single-step undo build).
//
// firstSentence/joinNames/buildCoreCluster moved here from
// PrivateOutput.tsx (unchanged behavior) so both the visible rendering
// and this text export use the identical logic -- not a parallel
// reimplementation that could drift between what's shown on screen and
// what gets copied.

import type {
  EvidenceReceipt, FrictionTaxLedgerEntry, PrivateOutputPayload, SeverityTier, StateRef, TacticalSectionResult,
} from "@/lib/types";

// First-sentence extraction for a secondary state's short-version summary
// (Block 4b) -- splits on the first sentence-ending period, not a hard
// character-count truncation. Falls through to the whole string when no
// internal ". " boundary exists (confirmed against all 58 real
// descriptive_prose values this session -- one state, cultural_overtime,
// is a single sentence with no internal boundary; this is that case
// resolving correctly, not a bug).
export function firstSentence(text: string): string {
  const match = text.match(/\.\s/);
  if (!match || match.index === undefined) return text;
  return text.slice(0, match.index + 1);
}

// Core cluster bucketing (Direction 3, Category E) -- Gemini-reviewed
// design: delta-weight bucket at 0.08 of the primary state's normalized
// weight, core cluster capped at 5, everything else folds into a
// "+N co-occurring conditions" overflow count.
export const CORE_CLUSTER_DELTA = 0.08;
export const CORE_CLUSTER_CAP = 5;

export function buildCoreCluster(
  secondaryStates: StateRef[],
  primaryWeight: number,
): { core: StateRef[]; overflowCount: number } {
  const withinDelta = secondaryStates.filter(
    (s) => primaryWeight - s.weight <= CORE_CLUSTER_DELTA,
  );
  const core = withinDelta.slice(0, CORE_CLUSTER_CAP);
  return { core, overflowCount: secondaryStates.length - core.length };
}

// Oxford-comma join for unpriced_state_ids names.
export function joinNames(names: string[]): string {
  if (names.length === 0) return "";
  if (names.length === 1) return names[0];
  if (names.length === 2) return `${names[0]} and ${names[1]}`;
  return `${names.slice(0, -1).join(", ")}, and ${names[names.length - 1]}`;
}

// Tier-based LOCKED copy -- mirrors PrivateOutput.tsx's own SEVERITY_ANCHOR
// exactly (engine/severity.py SEVERITY_TIER_DESCRIPTIONS). Duplicated
// rather than imported from PrivateOutput.tsx because it's a plain data
// constant, not logic -- importing a data table from a "use client"
// component into a lib module consumed by that same component would be a
// backwards dependency direction for no real benefit. If this ever drifts
// from PrivateOutput.tsx's own copy of the same table, that's a real bug
// to catch, not a design this file tries to prevent structurally.
const SEVERITY_ANCHOR: Record<SeverityTier, string> = {
  Emerging:
    "Something is wrong and you can see it. It hasn't settled into the organization yet. The consequences are coming but haven't fully arrived. This is the easiest moment to move.",
  Entrenched:
    "The condition has been here long enough that people have stopped treating it as a problem to solve. Workarounds exist. Expectations have adjusted. The organization has absorbed it without resolving it.",
  Endemic:
    "This is how the organization works now. The condition isn't something that happens inside the organization anymore. It is part of the operating environment itself. People make decisions inside it without questioning it. Resolution means changing the environment, not just addressing the condition.",
};

// ---------------------------------------------------------------------------
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
// Display-only dollar rounding (A1, Pete 2026-09-28): every dollar figure
// in the report, on screen and in Copy results, is shown to 3 significant
// figures, half up (4,839,283 -> $4,840,000, 16,550 -> $16,600, 450 ->
// $450). A nonzero value never renders as $0. Payload values stay
// unrounded. The engine's calculation-step text uses the same rule
// (engine/contract.py _usd).
export function formatUsd(value: number): string {
  if (value === 0) return "$0";
  const unit = 10 ** Math.max(0, Math.floor(Math.log10(Math.abs(value))) + 1 - 3);
  const rounded = Math.floor(value / unit + 0.5) * unit;
  return rounded === 0 ? "under $1" : `$${rounded.toLocaleString("en-US")}`;
}

// A range, collapsed to one figure when both ends round to the same value.
export function formatUsdRange(low: number, high: number): string {
  const a = formatUsd(low);
  const b = formatUsd(high);
  return a === b ? a : `${a} – ${b}`;
}

function money(low: number, high: number): string {
  return formatUsdRange(low, high);
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

// Ledger note (P2, Pete 2026-09-28): rows are standalone estimates and do
// not add up to the friction tax total. Shared with PrivateOutput.tsx.
export const FRICTION_TAX_LEDGER_STANDALONE_NOTE =
  "Each row estimates what that condition would cost on its own. Conditions " +
  "that rest on the same answers share a row, which shows the highest of their " +
  "individual estimates. The rows do not add up to the friction tax total, " +
  "because the total counts overlapping conditions at decreasing weight rather " +
  "than adding them in full.";

// Friction dollar switch (Pete, 2026-09-28, option C): friction-tax dollar
// figures are hidden on both brands until the friction methodology is
// rebuilt. The engine still computes them and the payload still carries
// them. Set to true to restore the dollar ledger, its calculation steps,
// its footnotes and the friction line in the cost comparison. Legal
// exposure is not affected by this switch.
export const FRICTION_DOLLARS_VISIBLE = false;

// Ledger copy while friction dollars are hidden.
export const FRICTION_LEDGER_HEADING_NO_DOLLARS = "The answers behind these conditions";
export const FRICTION_LEDGER_NOTE_NO_DOLLARS = "Conditions that rest on the same answers share a row.";

// One ledger row per distinct evidence set (P2). Rows whose
// top_contributing_answers are the same set (order ignored) merge into
// one group that names every condition and carries the highest standalone
// estimate among them. Rows with no evidence are never grouped: an empty
// list is not shared evidence. Group order follows first appearance.
export interface LedgerGroup {
  conditions: Array<{ state_id: string; name: string; risk_label: SeverityTier }>;
  dollar_exposure: FrictionTaxLedgerEntry["dollar_exposure"];
  top_contributing_answers: string[];
}

function higherEstimate(
  a: FrictionTaxLedgerEntry["dollar_exposure"],
  b: FrictionTaxLedgerEntry["dollar_exposure"],
): boolean {
  if (!a) return false;
  if (!b) return true;
  return a.high > b.high || (a.high === b.high && a.low > b.low);
}

export function groupLedgerRows(
  ledger: FrictionTaxLedgerEntry[],
  nameById?: Map<string, string>,
): LedgerGroup[] {
  const groups: LedgerGroup[] = [];
  const byEvidence = new Map<string, LedgerGroup>();
  for (const row of ledger) {
    const condition = {
      state_id: row.state_id,
      name: nameById?.get(row.state_id) ?? row.state_name,
      risk_label: row.risk_label,
    };
    const key = row.top_contributing_answers.length > 0
      ? JSON.stringify([...row.top_contributing_answers].sort())
      : null;
    const existing = key ? byEvidence.get(key) : undefined;
    if (existing) {
      existing.conditions.push(condition);
      if (higherEstimate(row.dollar_exposure, existing.dollar_exposure)) {
        existing.dollar_exposure = row.dollar_exposure;
      }
      continue;
    }
    const group: LedgerGroup = {
      conditions: [condition],
      dollar_exposure: row.dollar_exposure,
      top_contributing_answers: row.top_contributing_answers,
    };
    groups.push(group);
    if (key) byEvidence.set(key, group);
  }
  return groups;
}

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
// options.frictionDollarsVisible defaults to FRICTION_DOLLARS_VISIBLE, the
// same switch the screen reads. Tests pass it to cover both states.
export function buildResultsText(
  payload: PrivateOutputPayload,
  tacticalResults?: TacticalSectionResult[],
  options: { frictionDollarsVisible?: boolean } = {},
): string {
  const frictionVisible = options.frictionDollarsVisible ?? FRICTION_DOLLARS_VISIBLE;
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

  // Asset block: anchor text, then where strength shows up (the sentence
  // and the quoted evidence, never the bar values). The primary asset
  // domain is a property of the lead condition, not of this respondent,
  // so it is not shown (P1).
  const ev = payload.asset_evidence;
  if (payload.synthesis.asset_resolution_anchor_text) add([payload.synthesis.asset_resolution_anchor_text]);
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
  const pathway = [
    payload.resolution_family ? `Resolution pathway: ${payload.resolution_family}` : "Resolution pathway:",
  ];
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
      const figure = formatUsdRange(legal.low!, legal.high!);
      block.push(figure.includes("–") ? figure : `Estimated exposure: ${figure}`);
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
  if (ledger.length > 0 && !frictionVisible) {
    // Friction dollars hidden: the conditions and the answers behind
    // them. No figures, no footnotes, no calculation steps.
    const block = [`${FRICTION_LEDGER_HEADING_NO_DOLLARS}:`];
    for (const group of groupLedgerRows(ledger, stateNameById)) {
      block.push(`— ${group.conditions.map((c) => `${c.name} (${c.risk_label})`).join(", ")}`);
      for (const t of group.top_contributing_answers) block.push(`  ${t}`);
    }
    add(block);
    add([FRICTION_LEDGER_NOTE_NO_DOLLARS]);
  } else if (ledger.length > 0) {
    const block = ["Friction tax ledger:"];
    for (const group of groupLedgerRows(ledger, stateNameById)) {
      const d = group.dollar_exposure;
      const grouped = group.conditions.length > 1;
      const figure = d ? formatUsdRange(d.low, d.high) : null;
      const amount = figure === null
        ? `Estimate not available for ${grouped ? "these conditions" : "this condition"}.`
        : grouped
          ? `highest standalone estimate in this group, ${figure}`
          : figure.includes("–") ? figure : `Estimated exposure: ${figure}`;
      const names = group.conditions.map((c) => `${c.name} (${c.risk_label})`).join(", ");
      block.push(`— ${names}: ${amount}`);
      for (const t of group.top_contributing_answers) block.push(`  ${t}`);
    }
    add(block);
    add([FRICTION_TAX_LEDGER_STANDALONE_NOTE]);
    add([FRICTION_TAX_LEDGER_FOOTNOTE]);
    add(receiptLines("How the friction tax was calculated:", payload.friction_tax_estimate?.driving_factors));
  }

  // Cost comparison (same gate as the on-screen CostComparison).
  const friction = frictionVisible ? payload.friction_tax_estimate : null;
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
