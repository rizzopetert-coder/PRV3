"""
PRV3 -- Report Depth Initiative, Tier 1 (pure rendering/payload, no
Gemini gate). One commit, three sub-items.

Actual touch points, confirmed by direct read before writing anything --
differ from the plan doc's description in one place (sub-item 3):

  1. framing_text / observable_indicators -- PrivateOutput.tsx ONLY.
     Both fields already exist on SynthesisFields (web/lib/types.ts) and
     are already populated every session; already rendered in
     ShareableOutput.tsx. Purely additive rendering, confirmed by direct
     read of the current PrivateOutput.tsx (5 blocks, no framing_text/
     observable_indicators anywhere).

  2. secondary_states -- PrivateOutput.tsx ONLY. Already a required
     top-level field on PrivateOutputPayload (StateRef[], `weight: number`
     confirmed on StateRef), already populated by
     web/app/api/diagnostic/session/answer/route.ts
     (`secondary_states: stateRefs.slice(1)`). Zero references to
     `secondary_states` anywhere in PrivateOutput.tsx before this patch --
     confirmed by direct read, not assumed.

  3. asset_score.primary_asset_domain -- CORRECTION to the plan doc's
     framing. The doc describes this as dropped "at the route.ts layer,"
     implying the field exists on PrivateOutputPayload but goes unused.
     Direct read found otherwise: `primary_asset_domain` has exactly ONE
     occurrence anywhere in web/ -- inside EngineResult.asset_score
     (engine-client.ts). PrivateOutputPayload has NO field for it at all,
     and route.ts never references engineResult.asset_score in any form.
     The real gap is one layer earlier than described: the destination
     field doesn't exist yet, it's not just unused. Fix touches:
       - web/lib/types.ts: new primary_asset_domain?: string field
       - web/app/api/diagnostic/session/answer/route.ts: thread
         engineResult.asset_score.primary_asset_domain through (already
         real and present on EngineResult -- confirmed, not touched)
       - web/components/PrivateOutput.tsx: new render

     Confirmed with Pete before writing: unlike
     cascade_risk/causation_pattern/trajectory (Diagnostic Dimension
     Expansion), primary_asset_domain is NOT Path-dependent --
     _compute_asset_score() runs unconditionally for both Path 1 and
     Path B, so EngineResult.asset_score is equally real on both paths.
     Threaded into BOTH PrivateOutputPayload builders this commit --
     web/app/api/diagnostic/session/answer/route.ts (Path 1) AND
     web/app/api/result/route.ts (Path B, confirmed via fresh direct-read
     grep as the real Path B builder -- NOT
     web/app/api/share/create/route.ts, which builds ShareableOutputPayload
     and has zero asset_score references). Since both builders now
     populate it unconditionally, the field is REQUIRED on
     PrivateOutputPayload, not optional -- no remaining path can leave it
     undefined.

No engine/ files touched -- all three sub-items are web-layer only, since
every underlying Python computation already exists and is already
returned by assemble_output().

Usage:
  python tools/patch_report_depth_tier1.py --dry-run
  python tools/patch_report_depth_tier1.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_FILE = REPO_ROOT / "web" / "components" / "PrivateOutput.tsx"
TYPES_FILE = REPO_ROOT / "web" / "lib" / "types.ts"
ANSWER_ROUTE_FILE = REPO_ROOT / "web" / "app" / "api" / "diagnostic" / "session" / "answer" / "route.ts"

EDITS: list[tuple[Path, str, str, str]] = []

# --- web/lib/types.ts: 1 edit --------------------------------------------------

EDITS.append((
    TYPES_FILE,
    "types.ts: PrivateOutputPayload.primary_asset_domain (new field -- did not exist before)",
    '''  // Per-axis asset ratio for the live-mode ConstellationField visualization.
  dimension_summary: DimensionSummary;
}''',
    '''  // Per-axis asset ratio for the live-mode ConstellationField visualization.
  dimension_summary: DimensionSummary;

  // Report Depth Initiative Tier 1: engine-computed via
  // _compute_asset_score(), already present on EngineResult.asset_score --
  // was never threaded through to this payload (no field existed here at
  // all, not just unused). Required, not optional: unlike
  // cascade_risk/causation_pattern/trajectory this is NOT Path-dependent --
  // both PrivateOutputPayload builders (answer/route.ts, result/route.ts)
  // populate it unconditionally from the same always-present EngineResult
  // field, so there is no path left where it could be missing.
  primary_asset_domain: string;
}''',
))

# --- web/app/api/diagnostic/session/answer/route.ts: 1 edit (Path 1) ---------

EDITS.append((
    ANSWER_ROUTE_FILE,
    "answer/route.ts (Path 1): thread primary_asset_domain into privatePayload",
    '''    intake: session.intake,

    dimension_summary: engineResult.dimension_summary,
  };''',
    '''    intake: session.intake,

    dimension_summary: engineResult.dimension_summary,
    primary_asset_domain: engineResult.asset_score.primary_asset_domain,
  };''',
))

# --- web/app/api/result/route.ts: 1 edit (Path B) ------------------------------

RESULT_ROUTE_FILE = REPO_ROOT / "web" / "app" / "api" / "result" / "route.ts"

EDITS.append((
    RESULT_ROUTE_FILE,
    "result/route.ts (Path B): thread primary_asset_domain into privatePayload",
    '''    intake: mapIntake(engineResult.intake as Record<string, unknown>),

    dimension_summary: engineResult.dimension_summary,
  };''',
    '''    intake: mapIntake(engineResult.intake as Record<string, unknown>),

    dimension_summary: engineResult.dimension_summary,
    primary_asset_domain: engineResult.asset_score.primary_asset_domain,
  };''',
))

# --- web/components/PrivateOutput.tsx: 3 edits ---------------------------------

EDITS.append((
    COMPONENT_FILE,
    "PrivateOutput.tsx: new const declarations",
    '''  const liabilityText = payload.synthesis.liability_condition_text;
  const anchorText = payload.synthesis.asset_resolution_anchor_text;
  const resolutionFramingText = payload.synthesis.resolution_framing_text;''',
    '''  const liabilityText = payload.synthesis.liability_condition_text;
  const anchorText = payload.synthesis.asset_resolution_anchor_text;
  const resolutionFramingText = payload.synthesis.resolution_framing_text;
  const framingText = payload.synthesis.framing_text;
  const observableIndicators = payload.synthesis.observable_indicators ?? [];
  const primaryAssetDomain = payload.primary_asset_domain;''',
))

EDITS.append((
    COMPONENT_FILE,
    "PrivateOutput.tsx: framing_text + observable_indicators blocks, primary_asset_domain folded into Block 3",
    '''      {/* Block 2 — Liability condition */}
      <div className="py-4">
        <p className="text-sm leading-[1.65] text-ink">
          {liabilityText || payload.resolution_routing}
        </p>
      </div>
      <Rule />

      {/* Block 3 — Asset resolution anchor (omit entirely if empty) */}
      {anchorText && (
        <>
          <div className="py-4">
            <p className="text-[13px] text-gray-500">{anchorText}</p>
          </div>
          <Rule />
        </>
      )}''',
    '''      {/* Block 2 — Liability condition */}
      <div className="py-4">
        <p className="text-sm leading-[1.65] text-ink">
          {liabilityText || payload.resolution_routing}
        </p>
      </div>
      <Rule />

      {/* Block 2b — Framing text (omit entirely if empty) */}
      {framingText && (
        <>
          <div className="py-4">
            <p className="text-sm leading-[1.65] text-ink">{framingText}</p>
          </div>
          <Rule />
        </>
      )}

      {/* Block 2c — Observable indicators (omit entirely if empty) */}
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
      )}''',
))

EDITS.append((
    COMPONENT_FILE,
    "PrivateOutput.tsx: secondary_states acknowledgment block before ShareButton",
    '''      {/* Block 5 — ShareButton */}
      {enableSharing && (''',
    '''      {/* Block 4b — Secondary states acknowledgment (omit entirely if none) */}
      {payload.secondary_states.length > 0 && (
        <div className="py-4">
          <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
            Also present
          </p>
          <p className="text-[13px] text-gray-500">
            {payload.secondary_states
              .map((s) => `${s.name} (${(s.weight * 100).toFixed(0)}%)`)
              .join(", ")}
          </p>
        </div>
      )}

      {/* Block 5 — ShareButton */}
      {enableSharing && (''',
))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    file_texts: dict[Path, str] = {}
    for path in {e[0] for e in EDITS}:
        file_texts[path] = path.read_text(encoding="utf-8")

    for path, label, old, new in EDITS:
        count = file_texts[path].count(old)
        if count != 1:
            print(f"ABORT -- anchor for '{label}' matched {count} times in {path.relative_to(REPO_ROOT)}, need exactly 1", file=sys.stderr)
            sys.exit(1)

    print("=" * 100)
    for path, label, old, new in EDITS:
        print(f"\n--- {label} ({path.relative_to(REPO_ROOT)}) ---")
        print("BEFORE:")
        print(old)
        print("AFTER:")
        print(new)
    print("\n" + "=" * 100)

    new_texts: dict[Path, str] = dict(file_texts)
    for path, label, old, new in EDITS:
        new_texts[path] = new_texts[path].replace(old, new, 1)

    print("Files touched:")
    for path in file_texts:
        delta = len(new_texts[path]) - len(file_texts[path])
        print(f"  {path.relative_to(REPO_ROOT)}: {delta:+d} chars")

    print("\nweb/app/api/share/create/route.ts, share/[id]/route.ts (build ShareableOutputPayload, not")
    print("PrivateOutputPayload -- confirmed zero asset_score references), and engine/ (all Python):")
    print("confirmed NOT touched by this script.")

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    for path, text in new_texts.items():
        path.write_text(text, encoding="utf-8")
        print(f"\nWROTE {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
