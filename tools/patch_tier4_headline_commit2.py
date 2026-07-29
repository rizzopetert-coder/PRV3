"""
PRV3 -- Tier 4 Headline Field, Commit 2 of 2 (web layer).

Investigation before writing found the real scope differs from the
original 6-file list in two ways:

  1. web/lib/engine-client.ts's EngineResult.synthesis is a SEPARATE
     inline type (7 fields) mirroring SynthesisFields, not a reference
     to it -- same pattern as private_output/asset_score found in
     earlier steps this session. Missed in the original Commit 2 scope
     list, found by a direct grep sweep before writing anything. Needs
     headline added or route.ts's `engSynthesis.headline` read won't
     type-check.

  2. web/lib/output-renderer.ts has FOUR "synthesis: {" occurrences, but
     they're a completely different, simplified view-model shape
     ({text, confidence, isFallback, isReady}), not a mirror of
     SynthesisFields, AND confirmed dead code -- a repo-wide grep for
     renderPrivateOutput/renderShareableOutput/RenderedPrivateOutput/
     RenderedShareableOutput/any import from this module found zero
     matches anywhere else. Not touched, matching the same "confirmed
     dead at the live path" pattern as engine/output.py's
     ShareableOutputBlock found during Commit 1 scoping.
     web/lib/dev-diagnostic-preview.ts also not touched -- it imports
     SynthesisFields directly rather than declaring its own shape, so
     it inherits headline automatically once types.ts is updated.

Confirmed: ShareableSynthesisFields (Omit<SynthesisFields, ...>,
web/lib/types.ts) still excludes only liability_condition_text and
asset_resolution_anchor_text -- headline is not in the exclusion list,
so it flows through to the shareable side automatically, exactly as
found during scoping.

Seven files:
  1. web/lib/types.ts -- SynthesisFields.headline: string (required)
  2. web/lib/engine-client.ts -- EngineResult.synthesis inline type gains
     headline: string (found during this dry-run, not in original scope)
  3. web/app/api/diagnostic/session/answer/route.ts (Path 1)
  4. web/app/api/result/route.ts (Path B)
  5. web/app/api/share/create/route.ts (shareable)
  6. web/components/PrivateOutput.tsx -- new render, proposed placement:
     right after the condition header, before the ConstellationField
     diagram (textual takeaway before the visual detail)
  7. web/components/ShareableOutput.tsx -- new render, same relative
     placement: right after "Condition identified", before "Framing text"

Usage:
  python tools/patch_tier4_headline_commit2.py --dry-run
  python tools/patch_tier4_headline_commit2.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TYPES_FILE = REPO_ROOT / "web" / "lib" / "types.ts"
ENGINE_CLIENT_FILE = REPO_ROOT / "web" / "lib" / "engine-client.ts"
ANSWER_ROUTE_FILE = REPO_ROOT / "web" / "app" / "api" / "diagnostic" / "session" / "answer" / "route.ts"
RESULT_ROUTE_FILE = REPO_ROOT / "web" / "app" / "api" / "result" / "route.ts"
SHARE_CREATE_FILE = REPO_ROOT / "web" / "app" / "api" / "share" / "create" / "route.ts"
PRIVATE_OUTPUT_FILE = REPO_ROOT / "web" / "components" / "PrivateOutput.tsx"
SHAREABLE_OUTPUT_FILE = REPO_ROOT / "web" / "components" / "ShareableOutput.tsx"

EDITS: list[tuple[Path, str, str, str]] = []

# --- 1. web/lib/types.ts ---------------------------------------------------

EDITS.append((
    TYPES_FILE,
    "types.ts: SynthesisFields.headline (required)",
    '''export interface SynthesisFields {
  liability_condition_text:     string;
  asset_resolution_anchor_text: string;
  framing_text:                 string;
  observable_indicators:        string[];
  resolution_framing_text:      string;
  synthesis_confidence:         number;
  is_fallback:                  boolean;
}''',
    '''export interface SynthesisFields {
  liability_condition_text:     string;
  asset_resolution_anchor_text: string;
  framing_text:                 string;
  observable_indicators:        string[];
  resolution_framing_text:      string;
  headline:                     string;
  synthesis_confidence:         number;
  is_fallback:                  boolean;
}''',
))

# --- 2. web/lib/engine-client.ts (found during this dry-run) --------------

EDITS.append((
    ENGINE_CLIENT_FILE,
    "engine-client.ts: EngineResult.synthesis inline type gains headline",
    '''  synthesis: {
    liability_condition_text:     string;
    asset_resolution_anchor_text: string;
    framing_text:                 string;
    observable_indicators:        string[];
    resolution_framing_text:      string;
    synthesis_confidence:         number;
    is_fallback:                  boolean;
  } | null;''',
    '''  synthesis: {
    liability_condition_text:     string;
    asset_resolution_anchor_text: string;
    framing_text:                 string;
    observable_indicators:        string[];
    resolution_framing_text:      string;
    headline:                     string;
    synthesis_confidence:         number;
    is_fallback:                  boolean;
  } | null;''',
))

# --- 3. answer/route.ts (Path 1) -------------------------------------------

EDITS.append((
    ANSWER_ROUTE_FILE,
    "answer/route.ts (Path 1): synthesis construction gains headline, both branches",
    '''  const engSynthesis = engineResult.synthesis;
  const synthesis: SynthesisFields = engSynthesis
    ? {
        liability_condition_text:     engSynthesis.liability_condition_text,
        asset_resolution_anchor_text: engSynthesis.asset_resolution_anchor_text,
        framing_text:                 engSynthesis.framing_text,
        observable_indicators:        engSynthesis.observable_indicators,
        resolution_framing_text:      engSynthesis.resolution_framing_text,
        synthesis_confidence:         engSynthesis.synthesis_confidence,
        is_fallback:                  engSynthesis.is_fallback,
      }
    : {
        liability_condition_text:     "",
        asset_resolution_anchor_text: "",
        framing_text:                 "",
        observable_indicators:        [],
        resolution_framing_text:      "",
        synthesis_confidence:         0.0,
        is_fallback:                  true,
      };''',
    '''  const engSynthesis = engineResult.synthesis;
  const synthesis: SynthesisFields = engSynthesis
    ? {
        liability_condition_text:     engSynthesis.liability_condition_text,
        asset_resolution_anchor_text: engSynthesis.asset_resolution_anchor_text,
        framing_text:                 engSynthesis.framing_text,
        observable_indicators:        engSynthesis.observable_indicators,
        resolution_framing_text:      engSynthesis.resolution_framing_text,
        headline:                     engSynthesis.headline,
        synthesis_confidence:         engSynthesis.synthesis_confidence,
        is_fallback:                  engSynthesis.is_fallback,
      }
    : {
        liability_condition_text:     "",
        asset_resolution_anchor_text: "",
        framing_text:                 "",
        observable_indicators:        [],
        resolution_framing_text:      "",
        headline:                     "",
        synthesis_confidence:         0.0,
        is_fallback:                  true,
      };''',
))

# --- 4. result/route.ts (Path B) -------------------------------------------

EDITS.append((
    RESULT_ROUTE_FILE,
    "result/route.ts (Path B): synthesis construction gains headline, both branches",
    '''  const engSynthesis = engineResult.synthesis;
  const synthesis: SynthesisFields = engSynthesis
    ? {
        liability_condition_text:     engSynthesis.liability_condition_text,
        asset_resolution_anchor_text: engSynthesis.asset_resolution_anchor_text,
        framing_text:                 engSynthesis.framing_text,
        observable_indicators:        engSynthesis.observable_indicators,
        resolution_framing_text:      engSynthesis.resolution_framing_text,
        synthesis_confidence:         engSynthesis.synthesis_confidence,
        is_fallback:                  engSynthesis.is_fallback,
      }
    : {
        liability_condition_text:     "",
        asset_resolution_anchor_text: "",
        framing_text:                 "",
        observable_indicators:        [],
        resolution_framing_text:      "",
        synthesis_confidence:         0.0,
        is_fallback:                  true,
      };''',
    '''  const engSynthesis = engineResult.synthesis;
  const synthesis: SynthesisFields = engSynthesis
    ? {
        liability_condition_text:     engSynthesis.liability_condition_text,
        asset_resolution_anchor_text: engSynthesis.asset_resolution_anchor_text,
        framing_text:                 engSynthesis.framing_text,
        observable_indicators:        engSynthesis.observable_indicators,
        resolution_framing_text:      engSynthesis.resolution_framing_text,
        headline:                     engSynthesis.headline,
        synthesis_confidence:         engSynthesis.synthesis_confidence,
        is_fallback:                  engSynthesis.is_fallback,
      }
    : {
        liability_condition_text:     "",
        asset_resolution_anchor_text: "",
        framing_text:                 "",
        observable_indicators:        [],
        resolution_framing_text:      "",
        headline:                     "",
        synthesis_confidence:         0.0,
        is_fallback:                  true,
      };''',
))

# --- 5. share/create/route.ts (shareable) ----------------------------------

EDITS.append((
    SHARE_CREATE_FILE,
    "share/create/route.ts: shareable synthesis construction gains headline, both branches",
    '''  const engSynthesis = engineResult.synthesis;
  const synthesis: ShareableSynthesisFields = engSynthesis
    ? {
        framing_text:            engSynthesis.framing_text,
        observable_indicators:   engSynthesis.observable_indicators,
        resolution_framing_text: engSynthesis.resolution_framing_text,
        synthesis_confidence:    engSynthesis.synthesis_confidence,
        is_fallback:             engSynthesis.is_fallback,
      }
    : {
        framing_text:            "",
        observable_indicators:   [],
        resolution_framing_text: "",
        synthesis_confidence:    0.0,
        is_fallback:             true,
      };''',
    '''  const engSynthesis = engineResult.synthesis;
  const synthesis: ShareableSynthesisFields = engSynthesis
    ? {
        framing_text:            engSynthesis.framing_text,
        observable_indicators:   engSynthesis.observable_indicators,
        resolution_framing_text: engSynthesis.resolution_framing_text,
        headline:                engSynthesis.headline,
        synthesis_confidence:    engSynthesis.synthesis_confidence,
        is_fallback:             engSynthesis.is_fallback,
      }
    : {
        framing_text:            "",
        observable_indicators:   [],
        resolution_framing_text: "",
        headline:                "",
        synthesis_confidence:    0.0,
        is_fallback:             true,
      };''',
))

# --- 6. PrivateOutput.tsx ---------------------------------------------------

EDITS.append((
    PRIVATE_OUTPUT_FILE,
    "PrivateOutput.tsx: new const declaration",
    '''  const framingText = payload.synthesis.framing_text;
  const observableIndicators = payload.synthesis.observable_indicators ?? [];
  const primaryAssetDomain = payload.primary_asset_domain;''',
    '''  const framingText = payload.synthesis.framing_text;
  const observableIndicators = payload.synthesis.observable_indicators ?? [];
  const primaryAssetDomain = payload.primary_asset_domain;
  const headline = payload.synthesis.headline;''',
))

EDITS.append((
    PRIVATE_OUTPUT_FILE,
    "PrivateOutput.tsx: new headline render block, before the ConstellationField diagram",
    '''      {/* Block 1b — Weighted dimensional shape (live mode). Placeholder
          mock weights from Stage 3's scaffolding replaced with the real
          dimension_summary field (shipped commit 9c52e7d) — confirmed
          present in this payload at runtime for both Path A and Path B,
          not just in the type. */}''',
    '''      {/* Block 1a — Headline (omit entirely if empty) */}
      {headline && (
        <div className="pb-4">
          <p className="text-base font-medium leading-relaxed text-ink">{headline}</p>
        </div>
      )}

      {/* Block 1b — Weighted dimensional shape (live mode). Placeholder
          mock weights from Stage 3's scaffolding replaced with the real
          dimension_summary field (shipped commit 9c52e7d) — confirmed
          present in this payload at runtime for both Path A and Path B,
          not just in the type. */}''',
))

# --- 7. ShareableOutput.tsx -------------------------------------------------

EDITS.append((
    SHAREABLE_OUTPUT_FILE,
    "ShareableOutput.tsx: new headline render block, before framing_text",
    '''      {/* Block 3 — Framing text */}
      <div className="py-4">
        <p className="text-sm leading-[1.65] text-charcoal">
          {payload.synthesis.framing_text}
        </p>
      </div>
      <Rule />''',
    '''      {/* Block 2b — Headline (omit entirely if empty) */}
      {payload.synthesis.headline && (
        <>
          <div className="py-4">
            <p className="text-base font-medium leading-relaxed text-charcoal">
              {payload.synthesis.headline}
            </p>
          </div>
          <Rule />
        </>
      )}

      {/* Block 3 — Framing text */}
      <div className="py-4">
        <p className="text-sm leading-[1.65] text-charcoal">
          {payload.synthesis.framing_text}
        </p>
      </div>
      <Rule />''',
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

    print("\nweb/lib/output-renderer.ts (confirmed dead code, zero imports anywhere)")
    print("and web/lib/dev-diagnostic-preview.ts (imports SynthesisFields directly,")
    print("inherits headline automatically) confirmed NOT touched by this script.")

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    for path, text in new_texts.items():
        path.write_text(text, encoding="utf-8")
        print(f"\nWROTE {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
