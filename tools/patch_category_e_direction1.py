"""
PRV3 -- Category E, Direction 1 (visual identity refresh: rendering
quality upgrade). Gemini architecture-review cleared, with two of its four
verification-gate claims corrected before this build (see the prior
session's verification report): mounting-point framing was misleading (the
OD-07 rollback recolored, never unmounted -- live-mode ConstellationField
was already actively wired to real dimension_summary data in
PrivateOutput.tsx, better than assumed) and the data-emphasis enum
Gemini's motion snippet used ("primary"|"dimmed") does not exist -- the
real, live enum is "primary"|"secondary"|"receded". Both are further
instances of the standing Gemini-verification-catches-real-errors pattern
already logged multiple times this project.

Scope, confirmed with Pete: live mode only (LiveField) -- the vertex glow
effect is explicitly data-driven from real dimension_summary weights,
which don't exist in ambient mode (KEYFRAMES-driven, decorative). Ambient
mode's own craft upgrade, if wanted, is a separate future pass, not
bundled here. No Framer Motion, no new dependency -- the recede/resolve
motion upgrade is pure CSS, exploiting the standard technique where a
transition's timing is picked up from the property's NEW computed value
(the target state), not the old one -- so scoping `transition` per
data-emphasis value (rather than one shared rule) gives a real, distinct
duration/easing for entering "primary" (resolve, 350ms) versus entering
"secondary"/"receded" (recede, 250ms), with zero JS.

Tier-gated color resolver (severityAccentTokens()) needs no changes --
already correctly hard-gates --color-rust to severity_tier === "Endemic"
with no interpolation, confirmed on the prior verification pass.

Also fixes two stale doc-comment/file-header instances found during that
same verification pass (web/lib/types.ts's DimensionSummary comment,
ConstellationField.tsx's own file header) -- both said "not yet wired,
pending separate review" when live mode has been actively consuming real
data in production for some time. Same status-line-not-swept staleness
pattern already logged multiple times this project.

Usage:
  python tools/patch_category_e_direction1.py --dry-run
  python tools/patch_category_e_direction1.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


FIELD = "web/components/ConstellationField.tsx"
TYPES = "web/lib/types.ts"
CSS = "web/app/globals.css"

# ═══════════════════════════════════════════════════════════════════════
# ConstellationField.tsx -- file header staleness fix.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FIELD,
    '// weights prop is a PLACEHOLDER interface pending a real dimension_summary\n'
    '// field in the output contract (confirmed absent from PrivateOutputPayload\n'
    '// and EngineResult during Stage 3\'s investigation — held for separate\n'
    '// Gemini clearance before any Python/contract-side implementation, not\n'
    '// built here). Callers must supply representative data themselves; no\n'
    '// mock data is baked into this component.',
    '// weights prop is populated from the real dimension_summary field in the\n'
    '// output contract (engine/contract.py\'s assemble_output(), Gemini-cleared,\n'
    '// per-axis normalized [0,1] score) — wired live in web/components/\n'
    '// PrivateOutput.tsx, confirmed present in this payload at runtime for both\n'
    '// Path A and Path B, not just in the type. This comment previously said\n'
    '// "not wired yet, pending separate review" — stale as of the Direction 1\n'
    '// build (Category E, this session), corrected here.',
)

# ═══════════════════════════════════════════════════════════════════════
# ConstellationField.tsx -- glow tuning constants, alongside the existing
# LIVE_RING_RADII/LIVE_RING_OPACITY constants.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FIELD,
    '// Fixed 5-ring pattern — does NOT vary by severity tier. Confirmed from\n'
    '// the mockup: severity only changes color (see severityAccentTokens),\n'
    '// never count, radii, or opacity.\n'
    'export const LIVE_RING_RADII = [14, 28, 42, 56, 70];\n'
    'export const LIVE_RING_OPACITY = [0.9, 0.7, 0.5, 0.35, 0.22];',
    '// Fixed 5-ring pattern — does NOT vary by severity tier. Confirmed from\n'
    '// the mockup: severity only changes color (see severityAccentTokens),\n'
    '// never count, radii, or opacity.\n'
    'export const LIVE_RING_RADII = [14, 28, 42, 56, 70];\n'
    'export const LIVE_RING_OPACITY = [0.9, 0.7, 0.5, 0.35, 0.22];\n'
    '\n'
    '// Vertex glow (Direction 1, Category E, this session) — data-driven,\n'
    '// scaled per axis to the real dimension_summary weight (0.0-1.0), not a\n'
    '// fixed effect applied uniformly. Both blur radius (feGaussianBlur\n'
    '// stdDeviation) and opacity interpolate between these min/max pairs.\n'
    'const GLOW_BASE_R = 10;\n'
    'const GLOW_STD_MIN = 2;\n'
    'const GLOW_STD_MAX = 9;\n'
    'const GLOW_OPACITY_MIN = 0.12;\n'
    'const GLOW_OPACITY_MAX = 0.42;',
)

# ═══════════════════════════════════════════════════════════════════════
# ConstellationField.tsx -- LiveField: centroid computation + glow filter
# ids, inserted right after `points` is computed.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FIELD,
    '  const shapePoints = `${points.apt.x},${points.apt.y} ${points.auth.x},${points.auth.y} ${points.all.x},${points.all.y} ${points.att.x},${points.att.y}`;\n'
    '  const domPoint = points[domKey];',
    '  const shapePoints = `${points.apt.x},${points.apt.y} ${points.auth.x},${points.auth.y} ${points.all.x},${points.all.y} ${points.att.x},${points.att.y}`;\n'
    '  const domPoint = points[domKey];\n'
    '\n'
    '  // Centroid-tracking radial gradient origin (Direction 1, this session) —\n'
    '  // arithmetic mean of the four real weighted vertices, not the fixed\n'
    '  // LIVE_CENTER. Shifts with the real shape, same dynamism the flat\n'
    '  // color-mix fill it replaces couldn\'t express.\n'
    '  const centroid = {\n'
    '    x: (points.apt.x + points.auth.x + points.all.x + points.att.x) / 4,\n'
    '    y: (points.apt.y + points.auth.y + points.all.y + points.att.y) / 4,\n'
    '  };\n'
    '\n'
    '  const gradientId = `${filterId}-gradient`;\n'
    '  const glowFilterId = (k: AxisKey) => `${filterId}-glow-${k}`;',
)

# ═══════════════════════════════════════════════════════════════════════
# ConstellationField.tsx -- <defs>: add the radial gradient + 4 per-axis
# glow filters, right after the existing displacement filter.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FIELD,
    '      <defs>\n'
    '        <filter id={filterId} x="-40%" y="-40%" width="180%" height="180%">\n'
    '          <feTurbulence\n'
    '            type="fractalNoise"\n'
    '            baseFrequency="0.025"\n'
    '            numOctaves={2}\n'
    '            seed={19}\n'
    '            result="n"\n'
    '          />\n'
    '          <feDisplacementMap\n'
    '            in="SourceGraphic"\n'
    '            in2="n"\n'
    '            scale={7}\n'
    '            xChannelSelector="R"\n'
    '            yChannelSelector="G"\n'
    '          />\n'
    '        </filter>\n'
    '      </defs>',
    '      <defs>\n'
    '        <filter id={filterId} x="-40%" y="-40%" width="180%" height="180%">\n'
    '          <feTurbulence\n'
    '            type="fractalNoise"\n'
    '            baseFrequency="0.025"\n'
    '            numOctaves={2}\n'
    '            seed={19}\n'
    '            result="n"\n'
    '          />\n'
    '          <feDisplacementMap\n'
    '            in="SourceGraphic"\n'
    '            in2="n"\n'
    '            scale={7}\n'
    '            xChannelSelector="R"\n'
    '            yChannelSelector="G"\n'
    '          />\n'
    '        </filter>\n'
    '\n'
    '        {/* Centroid-tracking radial fill (Direction 1, this session) --\n'
    '            slate/charcoal core fading to paper at the shape\'s edge, origin\n'
    '            at the real weighted centroid computed above, not a fixed point. */}\n'
    '        <radialGradient\n'
    '          id={gradientId}\n'
    '          gradientUnits="userSpaceOnUse"\n'
    '          cx={centroid.x}\n'
    '          cy={centroid.y}\n'
    '          r={LIVE_MAX_R * 0.85}\n'
    '        >\n'
    '          <stop offset="0%" stopColor="var(--color-charcoal)" stopOpacity="0.22" />\n'
    '          <stop offset="55%" stopColor="var(--color-slate)" stopOpacity="0.16" />\n'
    '          <stop offset="100%" stopColor="var(--color-paper)" stopOpacity="0" />\n'
    '        </radialGradient>\n'
    '\n'
    '        {/* Per-axis vertex glow filters (Direction 1, this session) -- one\n'
    '            per axis so each blur radius can scale independently to that\n'
    '            axis\'s own real weight, not one shared, fixed-intensity filter. */}\n'
    '        {(Object.keys(AXES) as AxisKey[]).map((k) => (\n'
    '          <filter\n'
    '            key={`glowfilter-${k}`}\n'
    '            id={glowFilterId(k)}\n'
    '            x="-200%"\n'
    '            y="-200%"\n'
    '            width="500%"\n'
    '            height="500%"\n'
    '          >\n'
    '            <feGaussianBlur stdDeviation={GLOW_STD_MIN + weights[k] * (GLOW_STD_MAX - GLOW_STD_MIN)} />\n'
    '          </filter>\n'
    '        ))}\n'
    '      </defs>',
)

# ═══════════════════════════════════════════════════════════════════════
# ConstellationField.tsx -- shape polygon: gradient fill instead of flat
# color-mix, plus a depth-stacking backing stroke immediately before it.
# Vertex glow circles inserted immediately after (beneath the crisp
# dots/rings that already exist).
# ═══════════════════════════════════════════════════════════════════════

edit(
    FIELD,
    '      {/* The weighted shape — ALWAYS --color-slate, never severity-conditional.\n'
    '          Confirmed from the mockup: only the dominant vertex\'s rings,\n'
    '          center dot, and axis label switch to --color-rust at Endemic. */}\n'
    '      <polygon\n'
    '        points={shapePoints}\n'
    '        fill="color-mix(in srgb, var(--color-slate) 14%, transparent)"\n'
    '        stroke="var(--color-slate)"\n'
    '        strokeWidth="1.5"\n'
    '      />\n'
    '\n'
    '      {/* Non-dominant vertex dots — always --color-slate. */}\n'
    '      {(Object.keys(AXES) as AxisKey[])\n'
    '        .filter((k) => k !== domKey)\n'
    '        .map((k) => (\n'
    '          <circle key={k} cx={points[k].x} cy={points[k].y} r={4} fill="var(--color-slate)" />\n'
    '        ))}',
    '      {/* Depth stacking (Direction 1, this session) -- a low-alpha charcoal\n'
    '          backing stroke immediately behind the real shape, same points,\n'
    '          giving the shape a subtle sense of thickness/depth rather than a\n'
    '          flat single outline. Never severity-conditional -- depth is a\n'
    '          rendering-quality property, not a signal. */}\n'
    '      <polygon\n'
    '        points={shapePoints}\n'
    '        fill="none"\n'
    '        stroke="var(--color-charcoal)"\n'
    '        strokeWidth="4"\n'
    '        opacity="0.08"\n'
    '      />\n'
    '\n'
    '      {/* The weighted shape — fill is the centroid-tracking radial gradient\n'
    '          defined above (Direction 1, this session), replacing the prior flat\n'
    '          color-mix. Stroke stays ALWAYS --color-slate, never severity-\n'
    '          conditional. Confirmed from the mockup: only the dominant vertex\'s\n'
    '          rings, center dot, and axis label switch to --color-rust at Endemic. */}\n'
    '      <polygon\n'
    '        points={shapePoints}\n'
    '        fill={`url(#${gradientId})`}\n'
    '        stroke="var(--color-slate)"\n'
    '        strokeWidth="1.5"\n'
    '      />\n'
    '\n'
    '      {/* Vertex glow (Direction 1, this session) -- data-driven, scaled per\n'
    '          axis to that axis\'s real dimension_summary weight (see the\n'
    '          per-axis feGaussianBlur filters above). Dominant vertex glows in\n'
    '          the tier-gated accent color; all others stay --color-slate --\n'
    '          same color rule the crisp dots/rings below already use, not a\n'
    '          new one. Rendered beneath those dots/rings, purely additive. */}\n'
    '      {(Object.keys(AXES) as AxisKey[]).map((k) => (\n'
    '        <circle\n'
    '          key={`glow-${k}`}\n'
    '          cx={points[k].x}\n'
    '          cy={points[k].y}\n'
    '          r={GLOW_BASE_R}\n'
    '          fill={k === domKey ? accent.stroke : "var(--color-slate)"}\n'
    '          opacity={GLOW_OPACITY_MIN + weights[k] * (GLOW_OPACITY_MAX - GLOW_OPACITY_MIN)}\n'
    '          filter={`url(#${glowFilterId(k)})`}\n'
    '        />\n'
    '      ))}\n'
    '\n'
    '      {/* Non-dominant vertex dots — always --color-slate. */}\n'
    '      {(Object.keys(AXES) as AxisKey[])\n'
    '        .filter((k) => k !== domKey)\n'
    '        .map((k) => (\n'
    '          <circle key={k} cx={points[k].x} cy={points[k].y} r={4} fill="var(--color-slate)" />\n'
    '        ))}',
)

# ═══════════════════════════════════════════════════════════════════════
# web/lib/types.ts -- DimensionSummary doc comment staleness fix.
# ═══════════════════════════════════════════════════════════════════════

edit(
    TYPES,
    '/**\n'
    ' * Per-axis normalized asset ratio (aptitude/authority/alliance/attitude),\n'
    ' * each 0.0-1.0. From engine/contract.py\'s dimension_summary field\n'
    ' * (assemble_output() — Gemini-cleared, single normalized scalar per axis,\n'
    ' * not the raw liability/asset split, per P-03). Always present — computed\n'
    ' * unconditionally alongside asset_score, never optional.\n'
    ' *\n'
    ' * Not yet consumed by any component — the live-mode ConstellationField\n'
    ' * (web/components/ConstellationField.tsx) that will read this is built\n'
    ' * and tested against representative mock data but not wired to this real\n'
    ' * field yet, pending a separate review of that wiring step.\n'
    ' */',
    '/**\n'
    ' * Per-axis normalized asset ratio (aptitude/authority/alliance/attitude),\n'
    ' * each 0.0-1.0. From engine/contract.py\'s dimension_summary field\n'
    ' * (assemble_output() — Gemini-cleared, single normalized scalar per axis,\n'
    ' * not the raw liability/asset split, per P-03). Always present — computed\n'
    ' * unconditionally alongside asset_score, never optional.\n'
    ' *\n'
    ' * Consumed live by the live-mode ConstellationField (web/components/\n'
    ' * ConstellationField.tsx), wired in web/components/PrivateOutput.tsx. This\n'
    ' * comment previously said "not yet consumed, pending separate review" --\n'
    ' * stale as of the Direction 1 build (Category E, this session), corrected\n'
    ' * here.\n'
    ' */',
)

# ═══════════════════════════════════════════════════════════════════════
# globals.css -- asymmetric recede/resolve motion. Standard CSS technique:
# a transition's timing is picked up from the property's NEW computed
# value (the target state), not the old one -- scoping `transition` per
# data-emphasis value instead of one shared rule gives entering "primary"
# (resolve) a genuinely different duration/curve than entering
# "secondary"/"receded" (recede), with zero JS/new dependency.
# ═══════════════════════════════════════════════════════════════════════

edit(
    CSS,
    '  [data-emphasis] {\n'
    '    transition: opacity 200ms ease, transform 200ms ease;\n'
    '  }\n'
    '  [data-emphasis="primary"] {\n'
    '    opacity: 1;\n'
    '    transform: scale(1);\n'
    '  }\n'
    '  [data-emphasis="secondary"] {\n'
    '    opacity: 0.7;\n'
    '  }\n'
    '  [data-emphasis="receded"] {\n'
    '    opacity: 0.55;\n'
    '    transform: scale(0.98);\n'
    '  }',
    '  /* Recede/resolve motion upgrade (Direction 1, Category E, this session).\n'
    '     transition is now scoped per target state, not shared -- CSS picks up\n'
    '     the transition timing from the value being transitioned TO, so\n'
    '     entering "primary" (resolve) genuinely uses a different duration/curve\n'
    '     than entering "secondary" or "receded" (recede). No JS, no new\n'
    '     dependency (Pete\'s explicit call: CSS only, not Framer Motion). */\n'
    '  [data-emphasis="primary"] {\n'
    '    opacity: 1;\n'
    '    transform: scale(1);\n'
    '    transition: opacity 350ms cubic-bezier(0.16, 1, 0.3, 1), transform 350ms cubic-bezier(0.16, 1, 0.3, 1);\n'
    '  }\n'
    '  [data-emphasis="secondary"] {\n'
    '    opacity: 0.7;\n'
    '    transition: opacity 250ms cubic-bezier(0.4, 0, 0.2, 1), transform 250ms cubic-bezier(0.4, 0, 0.2, 1);\n'
    '  }\n'
    '  [data-emphasis="receded"] {\n'
    '    opacity: 0.55;\n'
    '    transform: scale(0.98);\n'
    '    transition: opacity 250ms cubic-bezier(0.4, 0, 0.2, 1), transform 250ms cubic-bezier(0.4, 0, 0.2, 1);\n'
    '  }',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
