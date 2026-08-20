"use client";

import type { PrivateOutputPayload, SeverityTier, StateRef } from "@/lib/types";
import type { EnginePayload } from "@/lib/engine-client";
import ShareButton from "@/components/ShareButton";
import { ConstellationField, severityAccentTokens } from "@/components/ConstellationField";
import { stateIdToSlug } from "@/lib/state-slug";

// First-sentence extraction for a secondary state's short-version summary
// (Block 4b) -- splits on the first sentence-ending period, not a hard
// character-count truncation. Falls through to the whole string when no
// internal ". " boundary exists (confirmed against all 58 real
// descriptive_prose values this session -- one state, cultural_overtime,
// is a single sentence with no internal boundary; this is that case
// resolving correctly, not a bug).
function firstSentence(text: string): string {
  const match = text.match(/\.\s/);
  if (!match || match.index === undefined) return text;
  return text.slice(0, match.index + 1);
}

// Core cluster bucketing (Direction 3, Category E, this session) --
// Gemini-reviewed design: delta-weight bucket at 0.08 of the primary
// state's normalized weight, core cluster capped at 5, everything else
// folds into a "+N co-occurring conditions" overflow count. Replaces a
// fixed 2/3-state tier, ruled out by real distribution data (58 real
// high_confidence profiles: median 7 qualified states, 50% displaying
// an identical percentage -- see
// prompts/category-e-direction3-cluster-display.md). secondary_states
// arrives already sorted descending by weight (both construction sites
// -- session/answer/route.ts and result/route.ts -- build it straight
// from the engine's own rank-sorted rankings), so no re-sort here.
const CORE_CLUSTER_DELTA = 0.08;
const CORE_CLUSTER_CAP = 5;

function buildCoreCluster(
  secondaryStates: StateRef[],
  primaryWeight: number,
): { core: StateRef[]; overflowCount: number } {
  const withinDelta = secondaryStates.filter(
    (s) => primaryWeight - s.weight <= CORE_CLUSTER_DELTA,
  );
  const core = withinDelta.slice(0, CORE_CLUSTER_CAP);
  return { core, overflowCount: secondaryStates.length - core.length };
}

// Tier-based LOCKED copy — mirrors engine/severity.py SEVERITY_TIER_DESCRIPTIONS.
const SEVERITY_ANCHOR: Record<SeverityTier, string> = {
  Emerging:
    "Something is wrong and you can see it. It hasn't settled into the organization yet. The consequences are coming but haven't fully arrived. This is the easiest moment to move.",
  Entrenched:
    "The condition has been here long enough that people have stopped treating it as a problem to solve. Workarounds exist. Expectations have adjusted. The organization has absorbed it without resolving it.",
  Endemic:
    "This is how the organization works now. The condition isn't something that happens inside the organization anymore. It is part of the operating environment itself. People make decisions inside it without questioning it. Resolution means changing the environment, not just addressing the condition.",
};

// Visualize Your Data (Layer 3). Mirrors engine/severity.py's
// classify_severity() CALIBRATION TARGET default boundaries (0-100
// scale; EMERGING_MAX/ENTRENCHED_MAX confirmed None/live-on-default
// at HEAD) -- same accepted mirror-drift risk SEVERITY_ANCHOR above
// already carries for SEVERITY_TIER_DESCRIPTIONS, not a new pattern.
const SEVERITY_TIER_BAND: Record<SeverityTier, { min: number; max: number }> = {
  Emerging:   { min: 0,  max: 33 },
  Entrenched: { min: 33, max: 66 },
  Endemic:    { min: 66, max: 100 },
};

function tierFillPercent(tier: SeverityTier, score: number): number {
  const { min, max } = SEVERITY_TIER_BAND[tier];
  const fraction = (score - min) / (max - min);
  return Math.max(0, Math.min(1, fraction)) * 100;
}

function Rule() {
  return (
    <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />
  );
}

interface PrivateOutputProps {
  payload: PrivateOutputPayload;
  selectedStateIds: string[];
  intake: EnginePayload["intake"];
  // Path 1 (Session 71, Phase 1): ShareButton re-invokes /api/share/create
  // with Path B's declared-diagnosis logic (equal weight, selectedStateIds
  // as the diagnosis), which would silently recompute — and corrupt — Path
  // 1's real cosine-similarity-derived weights. ShareableOutput generation
  // for Path 1 is explicitly out of scope this phase. Default true —
  // existing self-select callers are unaffected.
  enableSharing?: boolean;
}

export default function PrivateOutput({
  payload,
  selectedStateIds,
  intake,
  enableSharing = true,
}: PrivateOutputProps) {
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

  // Severity-conditional accent — reuses the same tested function live-mode
  // ConstellationField uses for its own rings, rather than a parallel
  // implementation. --urgency/--urgency-text only at genuine Endemic;
  // --oxide/--oxide-text at Emerging/Entrenched.
  const accent = severityAccentTokens(payload.severity);

  // Direction 3, this session -- see buildCoreCluster() above.
  const { core: coreCluster, overflowCount } = buildCoreCluster(
    payload.secondary_states,
    payload.primary_state.weight,
  );

  // Visualize Your Data (Layer 3). severity_by_state entries carry
  // state_id only -- both real builders derive primary_state/
  // secondary_states from the exact same identified_states array
  // severity_by_state comes from, so this lookup always resolves.
  const stateNameById = new Map<string, string>([
    [payload.primary_state.id, payload.primary_state.name],
    ...payload.secondary_states.map((s): [string, string] => [s.id, s.name]),
  ]);

  return (
    <div className="max-w-2xl">

      {/* Block 1 — Condition header. Hero typographic treatment
          (Direction 3, this session): the primary condition name gets
          the largest type in the report (font-display/Lora), replacing
          the prior text-[13px] treatment -- still one verdict named
          with confidence, per Output Precision. Eyebrow softened from
          "Condition identified" (implies singularity) to "Most
          prominent pattern" (signals rank without claiming exclusivity)
          -- per prompts/category-e-direction3-cluster-display.md. */}
      <div className="pb-4">
        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
          Most prominent pattern
        </p>
        <div className="flex items-center gap-3 flex-wrap mb-2">
          <span className="font-display text-3xl font-semibold text-charcoal">
            {payload.primary_state.name}
          </span>
          <span
            className="text-[11px] rounded-md px-2 py-0.5 border"
            style={{ borderColor: accent.stroke, color: accent.text }}
          >
            {payload.severity}
          </span>
        </div>
        {payload.primary_state.descriptive_prose && (
          <p className="text-[12px] text-gray-400 leading-relaxed mb-2">
            {payload.primary_state.descriptive_prose}
          </p>
        )}
        <p className="text-[12px] text-gray-400 leading-relaxed">
          {SEVERITY_ANCHOR[payload.severity]}
        </p>
      </div>

      {/* Block 1a — Headline (omit entirely if empty) */}
      {headline && (
        <div className="pb-4">
          <p className="text-base font-medium leading-relaxed text-charcoal">{headline}</p>
        </div>
      )}

      {/* Block 1b — Weighted dimensional shape (live mode). Placeholder
          mock weights from Stage 3's scaffolding replaced with the real
          dimension_summary field (shipped commit 9c52e7d) — confirmed
          present in this payload at runtime for both Path A and Path B,
          not just in the type. */}
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
      <Rule />

      {/* Block 2 — Observable indicators (omit entirely if empty) */}
      {observableIndicators.length > 0 && (
        <>
          <div className="py-4">
            <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
              Observable indicators
            </p>
            <ul className="space-y-1">
              {observableIndicators.map((indicator, i) => (
                <li key={i} className="flex gap-2 text-[13px] leading-[1.6] text-gray-500">
                  <span className="text-gray-300 shrink-0" aria-hidden>—</span>
                  <span>{indicator}</span>
                </li>
              ))}
            </ul>
          </div>
          <Rule />
        </>
      )}

      {/* Block 2b — Liability condition */}
      <div className="py-4">
        <p className="text-sm leading-[1.65] text-charcoal">
          {liabilityText || payload.resolution_routing}
        </p>
      </div>
      <Rule />

      {/* Block 2c — Framing text (omit entirely if empty) */}
      {framingText && (
        <>
          <div className="py-4">
            <p className="text-sm leading-[1.65] text-charcoal">{framingText}</p>
          </div>
          <Rule />
        </>
      )}

      {/* Block 3 — Asset resolution anchor + primary asset domain (omit entirely if both empty) */}
      {(anchorText || primaryAssetDomain) && (
        <>
          <div className="py-4">
            {primaryAssetDomain && (
              <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
                Primary asset domain: {primaryAssetDomain}
              </p>
            )}
            {anchorText && (
              <p className="text-[13px] text-gray-500">{anchorText}</p>
            )}
          </div>
          <Rule />
        </>
      )}

      {/* Block 4 — Resolution pathway */}
      <div className="py-4 space-y-1">
        <p className="text-[11px] uppercase tracking-wide text-gray-400">
          Resolution pathway
        </p>
        <p className="text-[13px] font-medium text-charcoal">
          {payload.resolution_family}
        </p>
        {resolutionFramingText ? (
          <p className="text-[13px] text-gray-500">{resolutionFramingText}</p>
        ) : (
          !usedRoutingInBlock2 && payload.resolution_routing && (
            <p className="text-[13px] text-gray-500">{payload.resolution_routing}</p>
          )
        )}
      </div>

      {/* Block 4b — Core cluster of co-occurring conditions (Direction
          3, this session). Replaces the flat "Also present" bulleted
          list (with its per-state percentage that a fixed 2/3-state
          tier and near-uniform real weights made frequently
          uninformative -- confirmed via real distribution data, see
          prompts/category-e-direction3-cluster-display.md) with a
          variable-length cluster: real typographic presence
          (font-display/Lora, uniform "secondary" weight -- a clear step
          down from the Block 1 hero, not graduated per member) for
          every state in the core cluster, plus a "+N co-occurring
          conditions" overflow affordance for the rest. Section label
          softened from "Also present" to "Co-occurring conditions" --
          signals real co-existence, not an afterthought footnote.
          Percentage intentionally dropped from display -- see this
          patch script's own docstring for the full rationale. */}
      {payload.secondary_states.length > 0 && (
        <div className="py-4">
          <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-3">
            Co-occurring conditions
          </p>
          <ul className="space-y-4">
            {coreCluster.map((s) => (
              <li key={s.id}>
                <a
                  href={`/book/toc#${stateIdToSlug(s.id)}`}
                  className="font-display text-lg text-charcoal hover:underline"
                >
                  {s.name}
                </a>
                {s.descriptive_prose && (
                  <p className="text-[12px] text-gray-500 leading-relaxed mt-0.5">
                    {firstSentence(s.descriptive_prose)}
                  </p>
                )}
              </li>
            ))}
          </ul>
          {overflowCount > 0 && (
            <p className="font-ui text-[12px] text-gray-400 mt-3">
              +{overflowCount} co-occurring condition{overflowCount === 1 ? "" : "s"}
            </p>
          )}
        </div>
      )}

      {/* Block 4c — Visualize Your Data (Layer 3): per-state severity
          comparison, one row per state in severity_by_state.
          Deliberately NOT lead-state-anchored -- a departure from
          Block 1's hero treatment, by design
          (prompts/visualize-your-data-build-scope.md). Omitted
          entirely when severity_by_state is absent or empty, same
          idiom as every other optional block in this component --
          never a partial/broken render. Row order is
          severity_by_state's own array order (primary state first,
          secondary_states rank-sorted); no re-sort here, matching
          "no sorting/ranking implied by row position." Renders for
          single-state results too (one row) -- the literal settled
          design, not gated to multi-state only. */}
      {payload.severity_by_state && payload.severity_by_state.length > 0 && (
        <div className="py-4">
          <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-3">
            Severity across conditions
          </p>
          <ul className="space-y-3">
            {payload.severity_by_state.map((entry) => {
              const rowAccent = severityAccentTokens(entry.tier);
              return (
                <li key={entry.state_id}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[13px] text-charcoal">
                      {stateNameById.get(entry.state_id) ?? entry.state_id}
                    </span>
                    <span
                      className="text-[10px] rounded-md px-1.5 py-0.5 border"
                      style={{ borderColor: rowAccent.stroke, color: rowAccent.text }}
                    >
                      {entry.tier}
                    </span>
                  </div>
                  <div className="h-1 rounded-full bg-gray-100">
                    <div
                      className="h-1 rounded-full"
                      style={{
                        width: `${tierFillPercent(entry.tier, entry.score_0_100)}%`,
                        backgroundColor: rowAccent.stroke,
                      }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
          <p className="text-[11px] text-gray-400 mt-3 leading-relaxed">
            A short bar at Emerging reflects a real finding, not a
            partial or uncertain one — Emerging is the floor of the
            severity scale.
          </p>
        </div>
      )}

      {/* Block 5 — ShareButton */}
      {enableSharing && (
        <div className="mt-2 w-full">
          <ShareButton selectedStateIds={selectedStateIds} intake={intake} />
        </div>
      )}

      {/* Block 6 — friction_tax_estimate: null in Path B — render nothing */}
    </div>
  );
}
