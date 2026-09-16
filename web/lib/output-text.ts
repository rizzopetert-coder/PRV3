// "Copy results as text" -- this session. Pure text-assembly logic,
// testable in isolation, following the same extract-shared-pure-logic
// discipline as session-store.ts's helpers (single-step undo build).
//
// firstSentence/joinNames/buildCoreCluster moved here from
// PrivateOutput.tsx (unchanged behavior) so both the visible rendering
// and this text export use the identical logic -- not a parallel
// reimplementation that could drift between what's shown on screen and
// what gets copied.

import type { PrivateOutputPayload, SeverityTier, StateRef } from "@/lib/types";

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

function pct(ratio: number): string {
  return `${Math.round(ratio * 100)}%`;
}

// ---------------------------------------------------------------------------
// buildResultsText -- the full "Copy results as text" assembly.
//
// Section 1 mirrors PrivateOutput.tsx's own render order and its own
// omit-when-empty conventions exactly (Blocks 1 through 4d) -- a
// respondent copying this should see the same narrative they saw on
// screen, not a differently-curated one.
//
// Section 2 surfaces fields PrivateOutputPayload carries that
// PrivateOutput.tsx never renders at all (confirmed by direct grep of
// that component this session): cascade_risk, causation_pattern,
// trajectory, urgency_window, synthesis.synthesis_confidence,
// synthesis.is_fallback, friction_tax_estimate, and intake. Labeled
// distinctly and separately so it reads as supplementary, not folded
// into the normal narrative.
//
// intake comes from payload.intake (PrivateIntakeEcho) -- confirmed this
// session to be the fuller, more accurate source. PrivateOutputProps
// also receives a separate `intake` prop (EnginePayload["intake"]) used
// only to drive ShareButton's recreate flow, and Path 1's own call site
// (DiagnosticFlow.tsx) populates that separate prop with deliberately
// partial data (blank orgType, a hardcoded significantEvents sentinel) --
// not the right source for a comprehensive text export.
//
// No markdown syntax (no *, #, -, as literal leading characters that
// would look like literal asterisks/hashes pasted into a plain text
// field) -- plain labels and blank-line separation only. List items use
// an em dash prefix (same visual idiom PrivateOutput.tsx's own bulleted
// blocks use), which reads fine as plain text either pasted into a chat
// or opened in a text file.
// ---------------------------------------------------------------------------
export function buildResultsText(payload: PrivateOutputPayload): string {
  const lines: string[] = [];

  const legal = payload.legal_tail_risk_exposure;
  const legalHasPrice = legal !== null && legal.low !== null && legal.high !== null;
  const stateNameById = new Map<string, string>([
    [payload.primary_state.id, payload.primary_state.name],
    ...payload.secondary_states.map((s): [string, string] => [s.id, s.name]),
  ]);

  // Block 1 -- condition header.
  lines.push(`${payload.primary_state.name} (${payload.severity})`);
  if (payload.primary_state.descriptive_prose) {
    lines.push("", payload.primary_state.descriptive_prose);
  }
  lines.push("", SEVERITY_ANCHOR[payload.severity]);

  // Block 1a -- headline.
  if (payload.synthesis.headline) {
    lines.push("", payload.synthesis.headline);
  }

  // Block 1b -- dimensional shape. Visual-only on screen (ConstellationField
  // has no text equivalent there) -- rendered here as a plain text line.
  const d = payload.dimension_summary;
  lines.push(
    "",
    `Dimensional shape: Aptitude: ${pct(d.aptitude)} | Authority: ${pct(d.authority)} | Alliance: ${pct(d.alliance)} | Attitude: ${pct(d.attitude)}`,
  );

  // Block 2 -- observable indicators.
  const indicators = payload.synthesis.observable_indicators ?? [];
  if (indicators.length > 0) {
    lines.push("", "Observable indicators:");
    for (const indicator of indicators) {
      lines.push(`— ${indicator}`);
    }
  }

  // Block 2b -- liability condition (or resolution_routing fallback, same
  // fallback PrivateOutput.tsx itself uses).
  const usedRoutingInBlock2 = !payload.synthesis.liability_condition_text && Boolean(payload.resolution_routing);
  lines.push("", payload.synthesis.liability_condition_text || payload.resolution_routing);

  // Block 2c -- framing text.
  if (payload.synthesis.framing_text) {
    lines.push("", payload.synthesis.framing_text);
  }

  // Block 3 -- asset resolution anchor + primary asset domain.
  if (payload.synthesis.asset_resolution_anchor_text || payload.primary_asset_domain) {
    lines.push("");
    if (payload.primary_asset_domain) {
      lines.push(`Primary asset domain: ${payload.primary_asset_domain}`);
    }
    if (payload.synthesis.asset_resolution_anchor_text) {
      lines.push(payload.synthesis.asset_resolution_anchor_text);
    }
  }

  // Block 4 -- resolution pathway.
  lines.push("", `Resolution pathway: ${payload.resolution_family}`);
  if (payload.synthesis.resolution_framing_text) {
    lines.push(payload.synthesis.resolution_framing_text);
  } else if (!usedRoutingInBlock2 && payload.resolution_routing) {
    lines.push(payload.resolution_routing);
  }

  // Block 4b -- co-occurring conditions.
  if (payload.secondary_states.length > 0) {
    const { core, overflowCount } = buildCoreCluster(
      payload.secondary_states,
      payload.primary_state.weight,
    );
    lines.push("", "Co-occurring conditions:");
    for (const s of core) {
      const summary = s.descriptive_prose ? `: ${firstSentence(s.descriptive_prose)}` : "";
      lines.push(`— ${s.name}${summary}`);
    }
    if (overflowCount > 0) {
      lines.push(`+${overflowCount} co-occurring condition${overflowCount === 1 ? "" : "s"}`);
    }
  }

  // Block 4c -- severity across conditions. score_0_100 included as a
  // number here (unlike the on-screen proportional bar) -- this is the
  // comprehensive/internal-facing version, per this build's own scope.
  if (payload.severity_by_state && payload.severity_by_state.length > 0) {
    lines.push("", "Severity across conditions:");
    for (const entry of payload.severity_by_state) {
      const name = stateNameById.get(entry.state_id) ?? entry.state_id;
      lines.push(`— ${name}: ${entry.tier} (${entry.score_0_100}/100)`);
    }
  }

  // Block 4d -- Legal/Compliance tail-risk exposure.
  if (legal) {
    lines.push("", "Legal/Compliance exposure:");
    if (legalHasPrice) {
      const currencySymbol = legal.currency === "USD" ? "$" : "";
      lines.push(
        `${currencySymbol}${legal.low!.toLocaleString()} – ${currencySymbol}${legal.high!.toLocaleString()}`,
      );
    }
    if (legalHasPrice && legal.coverage_basis === "federal_baseline") {
      lines.push(
        "This range applies a federal coverage threshold, since no confirmed state-specific threshold applied to the jurisdictions on file. Actual state law in those jurisdictions could set a materially lower bar than what's reflected here.",
      );
    } else if (legalHasPrice && legal.coverage_basis === "mixed") {
      lines.push(
        "This range blends a confirmed state-specific threshold with a federal coverage threshold used where no confirmed state-specific one applied. In the jurisdictions relying on the federal threshold, actual state law could set a materially lower bar than what's reflected here.",
      );
    }
    if (legalHasPrice && legal.has_partial_jurisdictions) {
      lines.push(
        "State law in this jurisdiction was not independently verified and may set a different threshold than what's reflected here.",
      );
    }
    if (legalHasPrice && legal.has_uncollected_net_worth_caveat) {
      lines.push(
        "This figure reflects twice the compensatory-damages estimate above, capped at Ohio's $350,000 ceiling -- not the net-worth alternative Ohio law also applies (R.C. 2315.21(D)(2)(b)). Since net worth isn't collected here, the true cap could be materially lower than what's reflected here.",
      );
    }
    if (legal.unpriced_state_ids.length > 0) {
      const unpricedNames = legal.unpriced_state_ids.map((id) => stateNameById.get(id) ?? id);
      lines.push(`Real exposure current data can't price precisely for: ${joinNames(unpricedNames)}.`);
    }
    lines.push(legal.caveat);
  }

  // ── Section 2 -- additional diagnostic detail (never shown on screen) ──
  lines.push("", "--- Additional diagnostic detail ---");

  if (payload.cascade_risk !== undefined) {
    lines.push("", `Cascade risk: ${payload.cascade_risk}`);
  }

  if (payload.causation_pattern) {
    const cp = payload.causation_pattern;
    lines.push(
      "",
      `Causation pattern: ${cp.pattern} (dispersion: ${cp.dispersion}, qualified states: ${cp.qualified_state_count})`,
    );
  }

  if (payload.trajectory) {
    const t = payload.trajectory;
    lines.push(
      "",
      `Trajectory: ${t.direction} (delta: ${t.delta}, dispersion delta: ${t.dispersion_delta}, duration: ${t.duration_band ?? "unknown"})`,
    );
  }

  if (payload.urgency_window) {
    const u = payload.urgency_window;
    lines.push(
      "",
      `Urgency window: time to consequence: ${u.time_to_consequence ?? "unknown"}, response window: ${u.response_window ?? "unknown"}`,
    );
  }

  lines.push("", `Synthesis confidence: ${payload.synthesis.synthesis_confidence}`);
  lines.push(`Synthesis is fallback: ${payload.synthesis.is_fallback}`);

  if (payload.friction_tax_estimate) {
    const f = payload.friction_tax_estimate;
    const currencySymbol = f.currency === "USD" ? "$" : "";
    lines.push(
      "",
      `Friction tax estimate: ${currencySymbol}${f.low.toLocaleString()} – ${currencySymbol}${f.high.toLocaleString()}`,
    );
  }

  const intake = payload.intake;
  lines.push(
    "",
    "Intake:",
    `Organization size: ${intake.organization_size}`,
    `Industry: ${intake.industry}`,
    `Role level: ${intake.role_level}`,
    `Tenure in role: ${intake.tenure_in_role}`,
    `Direct reports: ${intake.direct_reports}`,
    `Jurisdiction: ${intake.jurisdiction}`,
    `Significant events: ${intake.significant_events.join(", ")}`,
  );
  if (intake.significant_event_elaboration) {
    lines.push(`Significant event elaboration: ${intake.significant_event_elaboration}`);
  }

  return lines.join("\n");
}
