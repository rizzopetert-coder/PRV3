"use client";

import { useState } from "react";
import type { DevDiagnosticPreviewPayload } from "@/lib/dev-diagnostic-preview";
import type { SeverityTier, SingleResolutionFamily, StateRef } from "@/lib/types";
import { BOOK_STATE_INDEX } from "@/lib/book-state-index";
import PrivateOutput from "@/components/PrivateOutput";

// ---------------------------------------------------------------------------
// DEV / TEST ONLY. Purely client-side -- every field here lives in React
// state, never sent anywhere, never persisted. The payload passed to
// <PrivateOutput> below is reconstructed fresh on every render from these
// controls; there is no server round-trip, no Redis key, no engine call.
//
// dimension_summary/weights don't need to sum to 1.0 here the way a real
// engine output would -- ConstellationField's polarPoint() just multiplies
// each axis's raw weight by the fixed max radius independently (see
// web/components/ConstellationField.tsx), so arbitrary slider values are
// enough to exercise every visual case (dominant axis, tight vs. spread
// vertices, rust-gating at Endemic) without needing real accumulation math.
//
// See web/app/dev/diagnostic-preview for the other dev-only PrivateOutput
// viewer -- that one renders a REAL engine-computed result, this one is
// deliberately synthetic. Both are intentional, not overlapping.
// ---------------------------------------------------------------------------

const SEVERITY_TIERS: SeverityTier[] = ["Emerging", "Entrenched", "Endemic"];
const RESOLUTION_FAMILIES: SingleResolutionFamily[] = [
  "People Tactics and Strategy",
  "Training & Development",
  "Intervention",
  "Executive Advisory",
];

type AxisPreset = "authority-dominant" | "even-spread" | "sharp-peak";

const AXIS_PRESETS: Record<AxisPreset, { aptitude: number; authority: number; alliance: number; attitude: number }> = {
  "authority-dominant": { aptitude: 0.15, authority: 0.62, alliance: 0.12, attitude: 0.22 },
  "even-spread": { aptitude: 0.28, authority: 0.26, alliance: 0.24, attitude: 0.27 },
  "sharp-peak": { aptitude: 0.08, authority: 0.85, alliance: 0.05, attitude: 0.1 },
};

function SliderField({
  label,
  value,
  onChange,
  min = 0,
  max = 1,
  step = 0.01,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
}) {
  return (
    <label className="block">
      <span className="flex justify-between font-ui text-[11px] text-gray-500 mb-1">
        <span>{label}</span>
        <span className="font-mono">{value.toFixed(2)}</span>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full"
      />
    </label>
  );
}

export default function DiagnosticFixturePicker() {
  const [severity, setSeverity] = useState<SeverityTier>("Entrenched");
  const [primaryStateId, setPrimaryStateId] = useState(BOOK_STATE_INDEX[0].id);
  const [primaryWeight, setPrimaryWeight] = useState(0.42);

  const [aptitude, setAptitude] = useState(0.3);
  const [authority, setAuthority] = useState(0.5);
  const [alliance, setAlliance] = useState(0.25);
  const [attitude, setAttitude] = useState(0.35);

  const [secondaryCount, setSecondaryCount] = useState(5);
  const [secondarySpacing, setSecondarySpacing] = useState(0.03);

  const [resolutionFamily, setResolutionFamily] = useState<SingleResolutionFamily>("Intervention");
  const [resolutionRouting, setResolutionRouting] = useState(
    "Fixture placeholder resolution routing text -- edit freely.",
  );
  const [headline, setHeadline] = useState("Fixture placeholder headline.");
  const [liabilityText, setLiabilityText] = useState(
    "Fixture placeholder liability condition text -- edit freely to test wrapping and length.",
  );
  const [framingText, setFramingText] = useState("");
  const [resolutionFramingText, setResolutionFramingText] = useState(
    "Fixture placeholder resolution framing text.",
  );
  const [anchorText, setAnchorText] = useState(
    "Fixture placeholder asset resolution anchor text.",
  );
  const [primaryAssetDomain, setPrimaryAssetDomain] = useState("Adaptive Capacity");
  const [observableIndicatorsText, setObservableIndicatorsText] = useState(
    "Fixture indicator one.\nFixture indicator two.\nFixture indicator three.",
  );

  function applyPreset(preset: AxisPreset) {
    const p = AXIS_PRESETS[preset];
    setAptitude(p.aptitude);
    setAuthority(p.authority);
    setAlliance(p.alliance);
    setAttitude(p.attitude);
  }

  const primaryEntry = BOOK_STATE_INDEX.find((s) => s.id === primaryStateId) ?? BOOK_STATE_INDEX[0];

  const primaryState: StateRef = {
    id: primaryEntry.id,
    name: primaryEntry.name,
    weight: primaryWeight,
    descriptive_prose: primaryEntry.descriptiveProse,
  };

  // Secondary states auto-generated from the real state list (excluding
  // primary), descending weight from primaryWeight by secondarySpacing per
  // step -- secondarySpacing is the single control for "how tight or spread
  // the clustering is": small spacing keeps many siblings inside
  // buildCoreCluster()'s CORE_CLUSTER_DELTA (0.08, PrivateOutput.tsx),
  // large spacing pushes them out into the overflow count quickly.
  // secondaryCount past CORE_CLUSTER_CAP (5) exercises the "+N" overflow
  // affordance directly.
  const secondaryStates: StateRef[] = BOOK_STATE_INDEX.filter((s) => s.id !== primaryStateId)
    .slice(0, secondaryCount)
    .map((s, i) => ({
      id: s.id,
      name: s.name,
      weight: Math.max(0, primaryWeight - (i + 1) * secondarySpacing),
      descriptive_prose: s.descriptiveProse,
    }));

  const payload: DevDiagnosticPreviewPayload = {
    synthesis: {
      liability_condition_text: liabilityText,
      asset_resolution_anchor_text: anchorText,
      framing_text: framingText,
      observable_indicators: observableIndicatorsText
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean),
      resolution_framing_text: resolutionFramingText,
      headline,
      synthesis_confidence: 0.85,
      is_fallback: false,
    },
    primary_state: primaryState,
    secondary_states: secondaryStates,
    severity,
    resolution_family: resolutionFamily,
    resolution_routing: resolutionRouting,
    friction_tax_estimate: null,
    legal_tail_risk_exposure: null,
    // PrivateIntakeEcho shape (web/lib/types.ts) -- the intake echo embedded
    // in the output payload itself, a DIFFERENT shape from the separate
    // `intake` prop passed to <PrivateOutput> below (EnginePayload["intake"],
    // web/lib/engine-client.ts). Not reused between the two -- the existing
    // /dev/diagnostic-preview page keeps the same split.
    intake: {
      organization_size: "",
      industry: "",
      role_level: "",
      tenure_in_role: "",
      direct_reports: "",
      jurisdiction: "",
      significant_events: [],
    },
    dimension_summary: { aptitude, authority, alliance, attitude },
    primary_asset_domain: primaryAssetDomain,
  };

  // EnginePayload["intake"] shape -- what <PrivateOutput>'s `intake` prop
  // actually expects (unrelated to payload.intake above), used only to feed
  // ShareButton's re-submission path. Fixed placeholder since enableSharing
  // is false here -- same as the existing dev-preview page.
  const privateOutputIntakeProp = {
    headcount: "",
    industry: "",
    orgType: "",
    jurisdictions: [],
    significantEvents: [],
    principalRole: "",
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-8 max-w-6xl mx-auto items-start">
      <div className="space-y-6 lg:sticky lg:top-8">
        <section className="space-y-3">
          <p className="font-ui text-[11px] uppercase tracking-wide text-gray-400">
            Severity &amp; primary state
          </p>
          <label className="block">
            <span className="font-ui text-[11px] text-gray-500 mb-1 block">Severity tier</span>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value as SeverityTier)}
              className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
            >
              {SEVERITY_TIERS.map((tier) => (
                <option key={tier} value={tier}>
                  {tier}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="font-ui text-[11px] text-gray-500 mb-1 block">Primary state</span>
            <select
              value={primaryStateId}
              onChange={(e) => setPrimaryStateId(e.target.value)}
              className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
            >
              {BOOK_STATE_INDEX.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <SliderField label="Primary weight" value={primaryWeight} onChange={setPrimaryWeight} />
        </section>

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="font-ui text-[11px] uppercase tracking-wide text-gray-400">
              Dimension weights
            </p>
            <div className="flex gap-1">
              {(Object.keys(AXIS_PRESETS) as AxisPreset[]).map((preset) => (
                <button
                  key={preset}
                  type="button"
                  onClick={() => applyPreset(preset)}
                  className="font-ui text-[10px] px-1.5 py-0.5 border border-gray-200 rounded hover:border-gray-400 text-gray-500"
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>
          <SliderField label="Aptitude" value={aptitude} onChange={setAptitude} />
          <SliderField label="Authority" value={authority} onChange={setAuthority} />
          <SliderField label="Alliance" value={alliance} onChange={setAlliance} />
          <SliderField label="Attitude" value={attitude} onChange={setAttitude} />
        </section>

        <section className="space-y-3">
          <p className="font-ui text-[11px] uppercase tracking-wide text-gray-400">
            Co-occurring states (Block 4b)
          </p>
          <SliderField
            label="Secondary state count"
            value={secondaryCount}
            onChange={(v) => setSecondaryCount(Math.round(v))}
            min={0}
            max={15}
            step={1}
          />
          <SliderField
            label="Clustering spacing (lower = tighter cluster)"
            value={secondarySpacing}
            onChange={setSecondarySpacing}
            min={0.005}
            max={0.15}
            step={0.005}
          />
        </section>

        <section className="space-y-3">
          <p className="font-ui text-[11px] uppercase tracking-wide text-gray-400">
            Resolution pathway
          </p>
          <label className="block">
            <span className="font-ui text-[11px] text-gray-500 mb-1 block">Resolution family</span>
            <select
              value={resolutionFamily}
              onChange={(e) => setResolutionFamily(e.target.value as SingleResolutionFamily)}
              className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
            >
              {RESOLUTION_FAMILIES.map((f) => (
                <option key={f} value={f}>
                  {f}
                </option>
              ))}
            </select>
          </label>
        </section>

        <details className="space-y-3">
          <summary className="font-ui text-[11px] uppercase tracking-wide text-gray-400 cursor-pointer">
            Synthesis text (optional, defaults provided)
          </summary>
          <div className="space-y-3 pt-3">
            <label className="block">
              <span className="font-ui text-[11px] text-gray-500 mb-1 block">Headline</span>
              <input
                value={headline}
                onChange={(e) => setHeadline(e.target.value)}
                className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
              />
            </label>
            <label className="block">
              <span className="font-ui text-[11px] text-gray-500 mb-1 block">
                Liability condition text
              </span>
              <textarea
                value={liabilityText}
                onChange={(e) => setLiabilityText(e.target.value)}
                rows={3}
                className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
              />
            </label>
            <label className="block">
              <span className="font-ui text-[11px] text-gray-500 mb-1 block">
                Framing text (leave blank to test the omit-if-empty path)
              </span>
              <textarea
                value={framingText}
                onChange={(e) => setFramingText(e.target.value)}
                rows={2}
                className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
              />
            </label>
            <label className="block">
              <span className="font-ui text-[11px] text-gray-500 mb-1 block">
                Observable indicators (one per line)
              </span>
              <textarea
                value={observableIndicatorsText}
                onChange={(e) => setObservableIndicatorsText(e.target.value)}
                rows={3}
                className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
              />
            </label>
            <label className="block">
              <span className="font-ui text-[11px] text-gray-500 mb-1 block">
                Resolution framing text
              </span>
              <textarea
                value={resolutionFramingText}
                onChange={(e) => setResolutionFramingText(e.target.value)}
                rows={2}
                className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
              />
            </label>
            <label className="block">
              <span className="font-ui text-[11px] text-gray-500 mb-1 block">
                Asset resolution anchor text
              </span>
              <textarea
                value={anchorText}
                onChange={(e) => setAnchorText(e.target.value)}
                rows={2}
                className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
              />
            </label>
            <label className="block">
              <span className="font-ui text-[11px] text-gray-500 mb-1 block">
                Primary asset domain
              </span>
              <input
                value={primaryAssetDomain}
                onChange={(e) => setPrimaryAssetDomain(e.target.value)}
                className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
              />
            </label>
            <label className="block">
              <span className="font-ui text-[11px] text-gray-500 mb-1 block">
                Resolution routing
              </span>
              <textarea
                value={resolutionRouting}
                onChange={(e) => setResolutionRouting(e.target.value)}
                rows={2}
                className="w-full border border-gray-200 rounded px-2 py-1 text-sm font-ui"
              />
            </label>
          </div>
        </details>
      </div>

      <div className="border border-gray-100 rounded-lg p-6 bg-white">
        <PrivateOutput
          payload={payload}
          selectedStateIds={[primaryState.id, ...secondaryStates.map((s) => s.id)]}
          intake={privateOutputIntakeProp}
          enableSharing={false}
        />
      </div>
    </div>
  );
}
