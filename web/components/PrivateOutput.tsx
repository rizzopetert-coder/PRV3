"use client";

import dynamic from "next/dynamic";
import type {
  PrivateOutputPayload,
  SeverityTier,
  LegalTailRiskBand,
  TacticalSectionResult,
} from "@/lib/types";
import type { EnginePayload } from "@/lib/engine-client";
import ShareButton from "@/components/ShareButton";
import CopyResultsButton from "@/components/CopyResultsButton";
import { ConstellationField, severityAccentTokens } from "@/components/ConstellationField";
import { joinNames } from "@/lib/output-text";
import ConditionsList, { type ConditionRow } from "@/components/ConditionsList";
import {
  AssetStrength,
  CostComparison,
  EvidenceReceipts,
  ExecutiveSummary,
  TacticalReview,
} from "@/components/ReportDetails";
import { useBrand } from "@/components/BrandContext";

// Brand-specific pieces, code-split rather than conditionally rendered:
// Next bundles by import graph, so PR-only strings (tier names, /book/toc,
// the engage CTA) imported statically here would ship to hr-dx.com even
// when never rendered. Each is its own chunk, fetched only when rendered.
const ResultsOrientationPR = dynamic(() => import("@/components/ResultsOrientationPR"));
const ResultsOrientationHR = dynamic(() => import("@/components/ResultsOrientationHR"));
const StateBookLinkPR = dynamic(() => import("@/components/StateBookLinkPR"));
const EngageCtaPR = dynamic(() => import("@/components/EngageCtaPR"));

// Tier-based LOCKED copy — mirrors engine/severity.py SEVERITY_TIER_DESCRIPTIONS.
const SEVERITY_ANCHOR: Record<SeverityTier, string> = {
  Emerging:
    "Something is wrong and you can see it. It hasn't settled into the organization yet. The consequences are coming but haven't fully arrived. This is the easiest moment to move.",
  Entrenched:
    "The condition has been here long enough that people have stopped treating it as a problem to solve. Workarounds exist. Expectations have adjusted. The organization has absorbed it without resolving it.",
  Endemic:
    "This is how the organization works now. The condition isn't something that happens inside the organization anymore. It is part of the operating environment itself. People make decisions inside it without questioning it. Resolution means changing the environment, not just addressing the condition.",
};


// Friction tax ledger -- Block 4f. One shared footnote for the whole
// ledger, not per-row (per spec) -- hardcoded here rather than sent over
// the wire since it's invariant across every session, same convention as
// this component's other static section labels. Pete-approved final copy
// (supersedes the earlier draft, which was cross-checked against
// prompts/friction-tax-client-copy.md and found to diverge in several
// ways -- named sources, a missing severity-scaling step, a different
// "why a range" justification -- all resolved in this final text).
const FRICTION_TAX_LEDGER_FOOTNOTE =
  "Estimates are calculated from your organization's size, industry, and " +
  "structure, then scaled to how deeply organizational risk conditions " +
  "have taken root. The financial risk range draws on published research " +
  "including public wage and compensation data and studies on turnover, " +
  "disengagement, and lost productivity. Sources include McKinsey, SHRM, " +
  "Gallup, and other widely-recognized credible sources. Figures shown as " +
  "a range reflect the actual uncertainty identified in your diagnostic " +
  "result, and are not indicative of imprecision in the diagnosis.";

// Legal/Compliance tail-risk exposure -- Block 4d. Typographic
// differentiation only (font-weight/size) by band, no color ramp --
// --color-rust is reserved for genuine Endemic severity signaling
// (ConstellationField.tsx, severityAccentTokens()) and must never be
// reused here. band is guaranteed non-null whenever low is non-null
// (engine/friction_tax.py's _legal_exposure_band() returns null only
// when low is null) -- Record typed on the non-null union for that
// reason, with a defensive fallback at the render call site.
const LEGAL_BAND_WEIGHT: Record<LegalTailRiskBand, string> = {
  Minor: "font-normal",
  Moderate: "font-medium",
  Elevated: "font-semibold",
  Significant: "font-semibold text-sm",
};

function Rule() {
  return (
    <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />
  );
}

interface PrivateOutputProps {
  payload: PrivateOutputPayload;
  // hr-dx.com only -- undefined for every principal_resolution
  // session, and for hr_diagnostic sessions where no TC-* question was
  // ever reached (shouldn't happen in practice, but not assumed).
  tacticalResults?: TacticalSectionResult[];
  selectedStateIds: string[];
  intake: EnginePayload["intake"];
  // Path 1 (Session 71, Phase 1): ShareButton re-invokes /api/share/create
  // with Path B's declared-diagnosis logic (equal weight, selectedStateIds
  // as the diagnosis), which would silently recompute — and corrupt — Path
  // 1's real cosine-similarity-derived weights. ShareableOutput generation
  // for Path 1 is explicitly out of scope this phase. Default true —
  // existing self-select callers are unaffected.
  enableSharing?: boolean;
  // Real Transaction Path, Phase 1 (e-signature only, this session).
  // Suppresses the Engage CTA (Block 6) — identical suppression pattern to
  // enableSharing above. Default true; set false on the dev/test preview
  // viewer (web/app/dev/diagnostic-preview/[id]/page.tsx) so a synthetic,
  // fast-forwarded result can never trigger a real Dropbox Sign request.
  enableEngage?: boolean;
}

export default function PrivateOutput({
  payload,
  tacticalResults,
  selectedStateIds,
  intake,
  enableSharing = true,
  enableEngage = true,
}: PrivateOutputProps) {
  const brand = useBrand();
  // enableEngage defaults true and DiagnosticFlow.tsx never overrides it --
  // the Engage CTA below links to /engage, which middleware.ts blocks
  // entirely on hr_diagnostic. Same dead-link class as the self-select
  // gate found and fixed last pass -- suppressed here rather than left
  // visibly broken.
  const showEngageCta = enableEngage && brand !== "hr_diagnostic";
  const liabilityText = payload.synthesis.liability_condition_text;
  const anchorText = payload.synthesis.asset_resolution_anchor_text;
  const resolutionFramingText = payload.synthesis.resolution_framing_text;
  const framingText = payload.synthesis.framing_text;
  const observableIndicators = payload.synthesis.observable_indicators ?? [];
  const primaryAssetDomain = payload.primary_asset_domain;
  const headline = payload.synthesis.headline;

  // Block 2 uses resolution_routing as fallback when liability_condition_text is empty.
  // Block 4 must not repeat it if it was already used in block 2.
  const usedRoutingInBlock2 = !liabilityText && Boolean(payload.resolution_routing);

  // Phase 2 conditions list: every qualifying state, descending score.
  // all_qualified_states (Pass 1) is already score-sorted by the engine and
  // includes every above-floor state even in single mode; older payloads,
  // self-select, and dev fixtures fall back to primary + secondary. Severity
  // badge/bar only where severity_by_state has the state.
  const severityById = new Map(
    (payload.severity_by_state ?? []).map((e) => [e.state_id, e] as const),
  );
  const qualifiedSource =
    payload.all_qualified_states && payload.all_qualified_states.length > 0
      ? payload.all_qualified_states.map((s) => ({
          id: s.state_id, name: s.state_name, prose: s.descriptive_prose,
        }))
      : [payload.primary_state, ...payload.secondary_states].map((s) => ({
          id: s.id, name: s.name, prose: s.descriptive_prose ?? "",
        }));
  const conditionRows: ConditionRow[] = qualifiedSource.map((s, i) => {
    const entry = severityById.get(s.id);
    return {
      ...s,
      tier: entry?.tier ?? (i === 0 ? payload.severity : null),
      severity: entry ? { tier: entry.tier, score_0_100: entry.score_0_100 } : null,
    };
  });

  // Names for the legal/ledger blocks below, which carry state_id only.
  const stateNameById = new Map<string, string>([
    [payload.primary_state.id, payload.primary_state.name],
    ...payload.secondary_states.map((s): [string, string] => [s.id, s.name]),
    ...conditionRows.map((r): [string, string] => [r.id, r.name]),
  ]);

  // Block 4d -- Legal/Compliance tail-risk exposure derived values.
  // coverage_basis/has_partial_jurisdictions caveats only apply when a
  // priced range exists (legal.low !== null) -- coverage_basis is
  // meaningless without one, per the spec this block was built from.
  const legal = payload.legal_tail_risk_exposure;
  const legalHasPrice = legal !== null && legal.low !== null && legal.high !== null;
  const legalCoverageCaveat =
    legalHasPrice && legal!.coverage_basis === "federal_baseline"
      ? "This range applies a federal coverage threshold, since no confirmed state-specific threshold applied to the jurisdictions on file. Actual state law in those jurisdictions could set a materially lower bar than what's reflected here."
      : legalHasPrice && legal!.coverage_basis === "mixed"
      ? "This range blends a confirmed state-specific threshold with a federal coverage threshold used where no confirmed state-specific one applied. In the jurisdictions relying on the federal threshold, actual state law could set a materially lower bar than what's reflected here."
      : null;
  const unpricedStateNames = legal
    ? legal.unpriced_state_ids.map((id) => stateNameById.get(id) ?? id)
    : [];

  // Block 4f -- friction tax ledger. One row per condition, in the
  // array's own order (same as identified_states/severity_by_state
  // above). Gemini's Q5 finding (7-32 rows per profile, exact
  // distribution unverified) raised a real flat-list-vs-accordion
  // question -- resolved by Pete: default-open accordion, rendered
  // below via <details open>.
  const frictionTaxLedger = payload.friction_tax_ledger ?? [];

  return (
    <div className="max-w-2xl">

      {/* Contextual orientation — highest-value surface per the reviewed
          architecture. Sits above Block 1, singleton per render (one
          result, one orientation), not per-block. */}
      <div className="mb-3">
        {brand === "hr_diagnostic" ? (
          <ResultsOrientationHR
            topic="output-private"
            severity={payload.severity}
            pathway={payload.hr_pathway}
          />
        ) : (
          <ResultsOrientationPR
            topic="output-private"
            severity={payload.severity}
            resolutionFamily={payload.resolution_family}
          />
        )}
      </div>

      {/* Phase 3: executive summary opens the report when present. */}
      <ExecutiveSummary text={payload.synthesis.executive_summary} />

      {/* Phase 2 lead (Pete, 2026-09-27): the constellation, then the
          observable indicators, open the report. The former "Most prominent
          pattern" hero and "Severity across conditions" section are merged
          into ConditionsList below. */}
      <div className="max-w-70 mx-auto pb-4">
        <ConstellationField
          mode="live"
          weights={{
            apt: payload.dimension_summary.aptitude,
            auth: payload.dimension_summary.authority,
            all: payload.dimension_summary.alliance,
            att: payload.dimension_summary.attitude,
          }}
          severityTier={payload.severity}
        />
      </div>

      {observableIndicators.length > 0 && (
        <div className="pb-4">
          <p className="text-[11px] uppercase tracking-wide text-slate mb-2">
            Observable indicators
          </p>
          <ul className="space-y-1">
            {observableIndicators.map((indicator, i) => (
              <li key={i} className="flex gap-2 text-[13px] leading-[1.6] text-charcoal">
                <span className="text-gray-300 shrink-0" aria-hidden>—</span>
                <span>{indicator}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      <Rule />

      <ConditionsList
        rows={conditionRows}
        leadDetail={SEVERITY_ANCHOR[payload.severity]}
        renderExtra={
          brand === "hr_diagnostic"
            ? undefined
            : (row) => <StateBookLinkPR id={row.id} name={row.name} small />
        }
      />
      <Rule />

      {/* Narrative: headline, liability condition, framing text, and the
          asset resolution anchor, one continuous block. */}
      <div className="py-4 space-y-4">
        {headline && (
          <p className="text-base font-medium leading-relaxed text-charcoal">{headline}</p>
        )}

        <p className="text-sm leading-[1.65] text-charcoal">
          {liabilityText || payload.resolution_routing}
        </p>

        {framingText && (
          <p className="text-sm leading-[1.65] text-charcoal">{framingText}</p>
        )}

        {(anchorText || primaryAssetDomain || payload.asset_evidence) && (
          <div>
            {primaryAssetDomain && (
              <p className="text-[11px] uppercase tracking-wide text-slate mb-2">
                Primary asset domain: {primaryAssetDomain}
              </p>
            )}
            {anchorText && (
              <p className="text-[13px] text-charcoal">{anchorText}</p>
            )}
            <AssetStrength evidence={payload.asset_evidence} />
          </div>
        )}
      </div>
      <Rule />

      {/* Block 4 — Resolution pathway */}
      <div className="pb-4 space-y-1">
        <p className="text-[11px] uppercase tracking-wide text-slate">
          Resolution pathway
        </p>
        <p className="text-[13px] font-medium text-charcoal">
          {payload.resolution_family}
        </p>
        {resolutionFramingText ? (
          <p className="text-[13px] text-charcoal">{resolutionFramingText}</p>
        ) : (
          !usedRoutingInBlock2 && payload.resolution_routing && (
            <p className="text-[13px] text-charcoal">{payload.resolution_routing}</p>
          )
        )}
      </div>
      <Rule />

      {/* Block 4d — Legal/Compliance tail-risk exposure (Addendum 11).
          Omitted entirely when legal_tail_risk_exposure is null, same
          idiom as every other optional block in this component.
          coverage_basis/has_partial_jurisdictions caveats only apply
          when a priced range exists (low !== null) -- coverage_basis
          is meaningless without one. Band gets typographic
          differentiation only via LEGAL_BAND_WEIGHT -- see that
          const's own comment for why --color-rust is off-limits here.
          unpriced_state_ids resolved to names via stateNameById
          (Block 4c's own map) -- never rendered as raw state_ids, and
          the PRICED/QUALITATIVE_ONLY/DATA_INTEGRITY_GAP distinction
          behind them is never surfaced to the user. */}
      {legal && (
        <div className="py-4">
          <p className="text-[11px] uppercase tracking-wide text-slate mb-2">
            Legal/Compliance exposure
          </p>

          {legalHasPrice && (
            <p
              className={`text-[13px] text-charcoal mb-2 ${
                LEGAL_BAND_WEIGHT[legal.band ?? "Minor"]
              }`}
            >
              {legal.low === legal.high ? (
                <>
                  Estimated exposure: {legal.currency === "USD" ? "$" : ""}
                  {legal.low!.toLocaleString()}
                </>
              ) : (
                <>
                  {legal.currency === "USD" ? "$" : ""}
                  {legal.low!.toLocaleString()} – {legal.currency === "USD" ? "$" : ""}
                  {legal.high!.toLocaleString()}
                </>
              )}
            </p>
          )}

          {legalCoverageCaveat && (
            <p className="text-[12px] font-medium text-charcoal leading-relaxed mb-2">
              {legalCoverageCaveat}
            </p>
          )}

          {legalHasPrice && legal.has_partial_jurisdictions && (
            <p className="text-[11px] text-slate mt-1 mb-2 leading-relaxed">
              State law in this jurisdiction was not independently
              verified and may set a different threshold than what's
              reflected here.
            </p>
          )}

          {legalHasPrice && legal.has_uncollected_net_worth_caveat && (
            <p className="text-[11px] text-slate mt-1 mb-2 leading-relaxed">
              This figure reflects twice the compensatory-damages
              estimate above, capped at Ohio&apos;s $350,000 ceiling --
              not the net-worth alternative Ohio law also applies
              (R.C. 2315.21(D)(2)(b)). Since net worth isn&apos;t
              collected here, the true cap could be materially lower
              than what&apos;s reflected here.
            </p>
          )}

          {legalHasPrice && legal.specific_caveat && (
            <p className="text-[11px] text-slate mt-1 mb-2 leading-relaxed">
              {legal.specific_caveat}
            </p>
          )}

          {legal.unpriced_state_ids.length > 0 && (
            <p className="text-[12px] text-slate leading-relaxed mb-2">
              Real exposure current data can&apos;t price precisely for:{" "}
              {joinNames(unpricedStateNames)}.
            </p>
          )}

          <p className="text-[11px] text-slate mt-1 leading-relaxed">
            {legal.caveat}
          </p>
          <EvidenceReceipts receipts={legal.driving_factors} />
        </div>
      )}

      {/* Block 4f — Friction tax ledger (per-condition risk/dollar/
          top-contributing-answers). Omitted entirely when the ledger is
          empty, same idiom as every other optional block in this
          component. Accordion, defaulting OPEN (Pete's decision) --
          native <details open>/<summary>, the only accordion pattern
          already established anywhere in this codebase
          (DiagnosticFixturePicker.tsx), reused rather than a new
          interaction pattern invented for this one block. `open` is an
          uncontrolled default here, not tracked in React state -- the
          user can still collapse it, this only sets the initial render
          state. Risk label reuses severityAccentTokens for visual
          consistency with the "Severity across conditions" block above,
          since risk_label IS that same severity tier, not a new scale. */}
      {frictionTaxLedger.length > 0 && (
        <details open className="py-4">
          <summary className="text-[11px] uppercase tracking-wide text-slate mb-3 cursor-pointer">
            Friction tax ledger
          </summary>
          <ul className="space-y-4 mt-3">
            {frictionTaxLedger.map((row) => {
              const rowAccent = severityAccentTokens(row.risk_label);
              return (
                <li key={row.state_id}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[13px] text-charcoal">
                      {stateNameById.get(row.state_id) ?? row.state_name}
                    </span>
                    <span
                      className="text-[10px] rounded-md px-1.5 py-0.5 border"
                      style={{ borderColor: rowAccent.stroke, color: rowAccent.text }}
                    >
                      {row.risk_label}
                    </span>
                  </div>
                  <p className="text-[13px] text-charcoal mb-1">
                    {row.dollar_exposure ? (
                      row.dollar_exposure.low === row.dollar_exposure.high ? (
                        <>
                          Estimated exposure: {row.dollar_exposure.currency === "USD" ? "$" : ""}
                          {row.dollar_exposure.low.toLocaleString()}
                        </>
                      ) : (
                        <>
                          {row.dollar_exposure.currency === "USD" ? "$" : ""}
                          {row.dollar_exposure.low.toLocaleString()} –{" "}
                          {row.dollar_exposure.currency === "USD" ? "$" : ""}
                          {row.dollar_exposure.high.toLocaleString()}
                        </>
                      )
                    ) : (
                      <span className="text-slate">Estimate not available for this condition.</span>
                    )}
                  </p>
                  {row.top_contributing_answers.length > 0 && (
                    <ul className="text-[12px] text-slate leading-relaxed list-disc pl-4 space-y-0.5">
                      {row.top_contributing_answers.map((text, i) => (
                        <li key={i}>{text}</li>
                      ))}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
          <p className="text-[11px] text-slate mt-3 leading-relaxed">
            {FRICTION_TAX_LEDGER_FOOTNOTE}
          </p>
          <EvidenceReceipts receipts={payload.friction_tax_estimate?.driving_factors} />
        </details>
      )}

      {/* Phase 3: inaction cost beside the resolution service. */}
      <CostComparison
        comparison={payload.service_cost_comparison}
        friction={payload.friction_tax_estimate}
        legal={payload.legal_tail_risk_exposure}
        fallbackServiceName={payload.resolution_family}
      />

      {/* Block 4e — Copy results as text (this session). Comprehensive
          scope, visible to every respondent regardless of path -- NOT
          gated behind enableSharing/enableEngage, unlike Blocks 5/6.
          No backend round-trip: payload is already fully present
          client-side by the time this renders. */}
      <div className="mt-2 w-full">
        <CopyResultsButton payload={payload} />
      </div>

      {/* Block 5 — ShareButton */}
      {enableSharing && (
        <div className="mt-2 w-full">
          <ShareButton selectedStateIds={selectedStateIds} intake={intake} />
        </div>
      )}

      {/* Block 6 — Engage CTA, principal_resolution only (see
          EngageCtaPR.tsx). enableEngage mirrors enableSharing's
          suppression pattern exactly (see prop doc comment above). */}
      {showEngageCta && <EngageCtaPR />}

      {/* Block 7 — friction_tax_estimate: null in Path B — render nothing */}

      {/* Block 8 -- Tactical & Compliance review (hr-dx.com only). Phase 3:
          per-section synthesis from tactical_findings, raw answers kept
          collapsed. Referral chips unchanged. */}
      {tacticalResults && tacticalResults.length > 0 && (
        <TacticalReview sections={tacticalResults} findings={payload.tactical_findings} />
      )}
    </div>
  );
}
