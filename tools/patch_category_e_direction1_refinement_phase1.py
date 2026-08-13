"""
PRV3 -- Category E, Direction 1 Refinement (legibility, motion, interpretability).
Gemini-reviewed, file paths and CSS values independently re-verified against
live source this session before writing this diff (see conversation record).

Four files:
(1) web/components/ConstellationField.tsx -- legibility (axis label size/weight
    bump), motion (CSS-only stroke-dashoffset assembly animation on mount,
    prefers-reduced-motion respected via media query, no JS check needed),
    interpretability (hover/focus opens a desktop inline panel, click/tap opens
    a mobile vaul Drawer bottom sheet -- same desktop-panel/mobile-drawer split
    already established by StateDrawer.tsx, reused not reinvented). Reveal copy
    reuses PUBLIC_DIMENSION_LABELS verbatim (web/lib/book-taxonomy-labels.ts) --
    Pete's confirmed decision this session, avoiding a fresh copy-review cycle.
(2) web/app/globals.css -- new .cf-shape-entrance utility + keyframes, additive
    only, gated inside `@media (prefers-reduced-motion: no-preference)`.
(3) web/components/ConstellationField.test.ts -- one new test for the new pure
    axisToDimensionKey() mapping function.
(4) tools/_mob.txt -- standalone Decision Register row logging the recurring
    Gemini file-path citation error (3rd confirmed instance for these same two
    files), per Pete's explicit request, independent of the build itself.

Run with --dry-run first (default). Pass --write to apply.
"""
import argparse
import pathlib
import sys

CF_PATH = pathlib.Path("web/components/ConstellationField.tsx")
CSS_PATH = pathlib.Path("web/app/globals.css")
TEST_PATH = pathlib.Path("web/components/ConstellationField.test.ts")
MOB_PATH = pathlib.Path("tools/_mob.txt")

# ---------------------------------------------------------------------------
# (1) ConstellationField.tsx
# ---------------------------------------------------------------------------

OLD_CF_IMPORTS = '''"use client";

import { useEffect, useId, useRef } from "react";
import type { SeverityTier } from "@/lib/types";'''

NEW_CF_IMPORTS = '''"use client";

import { useEffect, useId, useRef, useState } from "react";
import { Drawer } from "vaul";
import type { SeverityTier } from "@/lib/types";
import type { DimensionKey } from "@/lib/book-manifest";
import { PUBLIC_DIMENSION_LABELS } from "@/lib/book-taxonomy-labels";'''

OLD_AXIS_LABELS_BLOCK = '''const AXIS_LABELS: Record<AxisKey, string> = {
  apt: "APT",
  auth: "AUTH",
  all: "ALL",
  att: "ATT",
};'''

NEW_AXIS_LABELS_BLOCK = '''const AXIS_LABELS: Record<AxisKey, string> = {
  apt: "APT",
  auth: "AUTH",
  all: "ALL",
  att: "ATT",
};

// Direction 1 Refinement (Category E, this session) -- maps the SVG's
// abbreviated AxisKey to book-taxonomy-labels.ts's full DimensionKey, so
// the hover/tap reveal can reuse the existing locked, brand-voice-approved
// PUBLIC_DIMENSION_LABELS copy verbatim rather than drafting new copy for
// this feature -- one vocabulary, not two, per the Decision Register's
// existing "Public dimension labels" locked entry.
export function axisToDimensionKey(k: AxisKey): DimensionKey {
  const map: Record<AxisKey, DimensionKey> = {
    apt: "aptitude",
    auth: "authority",
    all: "alliance",
    att: "attitude",
  };
  return map[k];
}'''

OLD_LIVEFIELD = '''function LiveField({ weights, severityTier }: LiveFieldProps) {
  const filterId = useId();
  const accent = severityAccentTokens(severityTier);
  const domKey = dominantAxis(weights);

  const points = (Object.keys(AXES) as AxisKey[]).reduce(
    (acc, k) => {
      acc[k] = polarPoint(weights[k], AXES[k], LIVE_CENTER, LIVE_MAX_R);
      return acc;
    },
    {} as Record<AxisKey, { x: number; y: number }>,
  );
  const shapePoints = `${points.apt.x},${points.apt.y} ${points.auth.x},${points.auth.y} ${points.all.x},${points.all.y} ${points.att.x},${points.att.y}`;
  const domPoint = points[domKey];

  // Centroid-tracking radial gradient origin (Direction 1, this session) —
  // arithmetic mean of the four real weighted vertices, not the fixed
  // LIVE_CENTER. Shifts with the real shape, same dynamism the flat
  // color-mix fill it replaces couldn't express.
  const centroid = {
    x: (points.apt.x + points.auth.x + points.all.x + points.att.x) / 4,
    y: (points.apt.y + points.auth.y + points.all.y + points.att.y) / 4,
  };

  const gradientId = `${filterId}-gradient`;
  const glowFilterId = (k: AxisKey) => `${filterId}-glow-${k}`;

  // Axis label positions — fixed offsets beyond the crosshair ends,
  // matching the reference mockup's exact pixel spacing at this canvas
  // size (top -15, bottom +25, right +20, left -20), not a derived
  // formula that could drift from the approved look.
  const labelPositions: Record<AxisKey, { x: number; y: number; anchor: "middle" }> = {
    apt: { x: LIVE_CENTER.x, y: LIVE_CENTER.y - LIVE_MAX_R - 15, anchor: "middle" },
    auth: { x: LIVE_CENTER.x + LIVE_MAX_R + 20, y: LIVE_CENTER.y + 5, anchor: "middle" },
    all: { x: LIVE_CENTER.x, y: LIVE_CENTER.y + LIVE_MAX_R + 25, anchor: "middle" },
    att: { x: LIVE_CENTER.x - LIVE_MAX_R - 20, y: LIVE_CENTER.y + 5, anchor: "middle" },
  };

  return (
    <svg
      className="w-full h-auto"
      viewBox={`0 0 ${LIVE_VIEW_W} ${LIVE_VIEW_H}`}
      role="img"
      aria-label={`Weighted diagnostic shape, dominant dimension ${AXIS_LABELS[domKey]}`}
    >
      <defs>
        <filter id={filterId} x="-40%" y="-40%" width="180%" height="180%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.025"
            numOctaves={2}
            seed={19}
            result="n"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="n"
            scale={7}
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>

        {/* Centroid-tracking radial fill (Direction 1, this session) --
            slate/charcoal core fading to paper at the shape's edge, origin
            at the real weighted centroid computed above, not a fixed point. */}
        <radialGradient
          id={gradientId}
          gradientUnits="userSpaceOnUse"
          cx={centroid.x}
          cy={centroid.y}
          r={LIVE_MAX_R * 0.85}
        >
          <stop offset="0%" stopColor="var(--color-charcoal)" stopOpacity="0.22" />
          <stop offset="55%" stopColor="var(--color-slate)" stopOpacity="0.16" />
          <stop offset="100%" stopColor="var(--color-paper)" stopOpacity="0" />
        </radialGradient>

        {/* Per-axis vertex glow filters (Direction 1, this session) -- one
            per axis so each blur radius can scale independently to that
            axis's own real weight, not one shared, fixed-intensity filter. */}
        {(Object.keys(AXES) as AxisKey[]).map((k) => (
          <filter
            key={`glowfilter-${k}`}
            id={glowFilterId(k)}
            x="-200%"
            y="-200%"
            width="500%"
            height="500%"
          >
            <feGaussianBlur stdDeviation={GLOW_STD_MIN + weights[k] * (GLOW_STD_MAX - GLOW_STD_MIN)} />
          </filter>
        ))}
      </defs>

      {/* Reference grid — always #e5e7eb, never severity-conditional. */}
      <g stroke="#e5e7eb" strokeWidth="1" fill="none">
        <line
          x1={LIVE_CENTER.x}
          y1={LIVE_CENTER.y - LIVE_MAX_R}
          x2={LIVE_CENTER.x}
          y2={LIVE_CENTER.y + LIVE_MAX_R}
        />
        <line
          x1={LIVE_CENTER.x - LIVE_MAX_R}
          y1={LIVE_CENTER.y}
          x2={LIVE_CENTER.x + LIVE_MAX_R}
          y2={LIVE_CENTER.y}
        />
        {LIVE_GUIDE_RING_FRACTIONS.map((frac) => {
          const r = LIVE_MAX_R * frac;
          const gp = (Object.keys(AXES) as AxisKey[]).reduce(
            (acc, k) => {
              acc[k] = polarPoint(1, AXES[k], LIVE_CENTER, r);
              return acc;
            },
            {} as Record<AxisKey, { x: number; y: number }>,
          );
          return (
            <polygon
              key={frac}
              points={`${gp.apt.x},${gp.apt.y} ${gp.auth.x},${gp.auth.y} ${gp.all.x},${gp.all.y} ${gp.att.x},${gp.att.y}`}
            />
          );
        })}
      </g>

      {/* Axis labels — always --color-slate, except the dominant axis, which
          takes the severity-conditional accent text color. */}
      {(Object.keys(AXES) as AxisKey[]).map((k) => (
        <text
          key={k}
          x={labelPositions[k].x}
          y={labelPositions[k].y}
          textAnchor={labelPositions[k].anchor}
          fill={k === domKey ? accent.text : "var(--color-slate)"}
          className="font-mono"
          fontSize="11"
          letterSpacing="1"
        >
          {AXIS_LABELS[k]}
        </text>
      ))}

      {/* Depth stacking (Direction 1, this session) -- a low-alpha charcoal
          backing stroke immediately behind the real shape, same points,
          giving the shape a subtle sense of thickness/depth rather than a
          flat single outline. Never severity-conditional -- depth is a
          rendering-quality property, not a signal. */}
      <polygon
        points={shapePoints}
        fill="none"
        stroke="var(--color-charcoal)"
        strokeWidth="4"
        opacity="0.08"
      />

      {/* The weighted shape — fill is the centroid-tracking radial gradient
          defined above (Direction 1, this session), replacing the prior flat
          color-mix. Stroke stays ALWAYS --color-slate, never severity-
          conditional. Confirmed from the mockup: only the dominant vertex's
          rings, center dot, and axis label switch to --color-rust at Endemic. */}
      <polygon
        points={shapePoints}
        fill={`url(#${gradientId})`}
        stroke="var(--color-slate)"
        strokeWidth="1.5"
      />

      {/* Vertex glow (Direction 1, this session) -- data-driven, scaled per
          axis to that axis's real dimension_summary weight (see the
          per-axis feGaussianBlur filters above). Dominant vertex glows in
          the tier-gated accent color; all others stay --color-slate --
          same color rule the crisp dots/rings below already use, not a
          new one. Rendered beneath those dots/rings, purely additive. */}
      {(Object.keys(AXES) as AxisKey[]).map((k) => (
        <circle
          key={`glow-${k}`}
          cx={points[k].x}
          cy={points[k].y}
          r={GLOW_BASE_R}
          fill={k === domKey ? accent.stroke : "var(--color-slate)"}
          opacity={GLOW_OPACITY_MIN + weights[k] * (GLOW_OPACITY_MAX - GLOW_OPACITY_MIN)}
          filter={`url(#${glowFilterId(k)})`}
        />
      ))}

      {/* Non-dominant vertex dots — always --color-slate. */}
      {(Object.keys(AXES) as AxisKey[])
        .filter((k) => k !== domKey)
        .map((k) => (
          <circle key={k} cx={points[k].x} cy={points[k].y} r={4} fill="var(--color-slate)" />
        ))}

      {/* Severity rings — fixed 5-ring pattern, radii/opacity never vary
          by severity tier. Only the color varies (accent.stroke: --color-slate
          at Emerging/Entrenched, --color-rust only at genuine Endemic). */}
      <g filter={`url(#${filterId})`} fill="none" stroke={accent.stroke} strokeWidth="1">
        {LIVE_RING_RADII.map((r, i) => (
          <circle
            key={r}
            cx={domPoint.x}
            cy={domPoint.y}
            r={r}
            opacity={LIVE_RING_OPACITY[i]}
          />
        ))}
      </g>
      <circle cx={domPoint.x} cy={domPoint.y} r={5} fill={accent.stroke} />
    </svg>
  );
}'''

NEW_LIVEFIELD = '''function LiveField({ weights, severityTier }: LiveFieldProps) {
  const filterId = useId();
  const accent = severityAccentTokens(severityTier);
  const domKey = dominantAxis(weights);

  // Direction 1 Refinement (Category E, this session) -- interpretability.
  // Two separate pieces of state, deliberately not one shared "active axis"
  // value: hoveredDimension drives the desktop inline panel (mouse hover OR
  // keyboard focus/activate -- parity for non-touch interaction methods);
  // tappedDimension drives the mobile vaul Drawer and is set ONLY by an
  // actual pointer click/tap. Kept separate so a keyboard user tabbing
  // through the chart on desktop never triggers the Drawer's open state
  // (which applies its own body-scroll-lock regardless of the `md:hidden`
  // CSS that hides its visual output) -- the Drawer only ever opens from a
  // real click, never from hover or focus alone.
  const [hoveredDimension, setHoveredDimension] = useState<AxisKey | null>(null);
  const [tappedDimension, setTappedDimension] = useState<AxisKey | null>(null);

  const points = (Object.keys(AXES) as AxisKey[]).reduce(
    (acc, k) => {
      acc[k] = polarPoint(weights[k], AXES[k], LIVE_CENTER, LIVE_MAX_R);
      return acc;
    },
    {} as Record<AxisKey, { x: number; y: number }>,
  );
  const shapePoints = `${points.apt.x},${points.apt.y} ${points.auth.x},${points.auth.y} ${points.all.x},${points.all.y} ${points.att.x},${points.att.y}`;
  const domPoint = points[domKey];

  // Centroid-tracking radial gradient origin (Direction 1, this session) —
  // arithmetic mean of the four real weighted vertices, not the fixed
  // LIVE_CENTER. Shifts with the real shape, same dynamism the flat
  // color-mix fill it replaces couldn't express.
  const centroid = {
    x: (points.apt.x + points.auth.x + points.all.x + points.att.x) / 4,
    y: (points.apt.y + points.auth.y + points.all.y + points.att.y) / 4,
  };

  const gradientId = `${filterId}-gradient`;
  const glowFilterId = (k: AxisKey) => `${filterId}-glow-${k}`;

  // Axis label positions — fixed offsets beyond the crosshair ends,
  // matching the reference mockup's exact pixel spacing at this canvas
  // size (top -15, bottom +25, right +20, left -20), not a derived
  // formula that could drift from the approved look. Direction 1
  // Refinement (this session): these fixed, always-well-separated
  // positions are also what the hover/tap hit-area anchors to, not the
  // data-driven vertex point -- vertices move with the real weights and
  // can cluster near center at low values, which would make reliable
  // touch/hover targeting on the vertex itself fragile; the label position
  // never moves.
  const labelPositions: Record<AxisKey, { x: number; y: number; anchor: "middle" }> = {
    apt: { x: LIVE_CENTER.x, y: LIVE_CENTER.y - LIVE_MAX_R - 15, anchor: "middle" },
    auth: { x: LIVE_CENTER.x + LIVE_MAX_R + 20, y: LIVE_CENTER.y + 5, anchor: "middle" },
    all: { x: LIVE_CENTER.x, y: LIVE_CENTER.y + LIVE_MAX_R + 25, anchor: "middle" },
    att: { x: LIVE_CENTER.x - LIVE_MAX_R - 20, y: LIVE_CENTER.y + 5, anchor: "middle" },
  };

  const hoveredInfo = hoveredDimension
    ? PUBLIC_DIMENSION_LABELS[axisToDimensionKey(hoveredDimension)]
    : null;
  const tappedInfo = tappedDimension
    ? PUBLIC_DIMENSION_LABELS[axisToDimensionKey(tappedDimension)]
    : null;

  return (
    <div className="relative">
      <svg
        className="w-full h-auto"
        viewBox={`0 0 ${LIVE_VIEW_W} ${LIVE_VIEW_H}`}
        role="img"
        aria-label={`Weighted diagnostic shape, dominant dimension ${AXIS_LABELS[domKey]}`}
      >
        <defs>
          <filter id={filterId} x="-40%" y="-40%" width="180%" height="180%">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.025"
              numOctaves={2}
              seed={19}
              result="n"
            />
            <feDisplacementMap
              in="SourceGraphic"
              in2="n"
              scale={7}
              xChannelSelector="R"
              yChannelSelector="G"
            />
          </filter>

          {/* Centroid-tracking radial fill (Direction 1, this session) --
              slate/charcoal core fading to paper at the shape's edge, origin
              at the real weighted centroid computed above, not a fixed point. */}
          <radialGradient
            id={gradientId}
            gradientUnits="userSpaceOnUse"
            cx={centroid.x}
            cy={centroid.y}
            r={LIVE_MAX_R * 0.85}
          >
            <stop offset="0%" stopColor="var(--color-charcoal)" stopOpacity="0.22" />
            <stop offset="55%" stopColor="var(--color-slate)" stopOpacity="0.16" />
            <stop offset="100%" stopColor="var(--color-paper)" stopOpacity="0" />
          </radialGradient>

          {/* Per-axis vertex glow filters (Direction 1, this session) -- one
              per axis so each blur radius can scale independently to that
              axis's own real weight, not one shared, fixed-intensity filter.
              Declared once per component instance via the stable useId()-
              derived filterId -- Direction 1 Refinement's hover/tap state
              (this session) toggles element attributes only, it never adds
              or removes these <filter> defs, so there is no duplicate-
              instantiation risk from interaction. */}
          {(Object.keys(AXES) as AxisKey[]).map((k) => (
            <filter
              key={`glowfilter-${k}`}
              id={glowFilterId(k)}
              x="-200%"
              y="-200%"
              width="500%"
              height="500%"
            >
              <feGaussianBlur stdDeviation={GLOW_STD_MIN + weights[k] * (GLOW_STD_MAX - GLOW_STD_MIN)} />
            </filter>
          ))}
        </defs>

        {/* Reference grid — always #e5e7eb, never severity-conditional. */}
        <g stroke="#e5e7eb" strokeWidth="1" fill="none">
          <line
            x1={LIVE_CENTER.x}
            y1={LIVE_CENTER.y - LIVE_MAX_R}
            x2={LIVE_CENTER.x}
            y2={LIVE_CENTER.y + LIVE_MAX_R}
          />
          <line
            x1={LIVE_CENTER.x - LIVE_MAX_R}
            y1={LIVE_CENTER.y}
            x2={LIVE_CENTER.x + LIVE_MAX_R}
            y2={LIVE_CENTER.y}
          />
          {LIVE_GUIDE_RING_FRACTIONS.map((frac) => {
            const r = LIVE_MAX_R * frac;
            const gp = (Object.keys(AXES) as AxisKey[]).reduce(
              (acc, k) => {
                acc[k] = polarPoint(1, AXES[k], LIVE_CENTER, r);
                return acc;
              },
              {} as Record<AxisKey, { x: number; y: number }>,
            );
            return (
              <polygon
                key={frac}
                points={`${gp.apt.x},${gp.apt.y} ${gp.auth.x},${gp.auth.y} ${gp.all.x},${gp.all.y} ${gp.att.x},${gp.att.y}`}
              />
            );
          })}
        </g>

        {/* Axis labels — always --color-slate, except the dominant axis, which
            takes the severity-conditional accent text color. Direction 1
            Refinement (this session): fontSize bumped 11 -> 14, and the
            dominant axis's label now also carries fontWeight 700 (was
            uniform 400) -- legibility fix per Pete's live-review finding
            that axis labels "read small, not reader-friendly." Each label
            is wrapped in an interactive <g> with an invisible, generously-
            sized hit-area (a transparent rect, not the tiny text glyph
            itself) carrying the hover/tap/keyboard interaction. */}
        {(Object.keys(AXES) as AxisKey[]).map((k) => {
          const info = PUBLIC_DIMENSION_LABELS[axisToDimensionKey(k)];
          return (
            <g
              key={k}
              role="button"
              tabIndex={0}
              aria-label={`${AXIS_LABELS[k]} — ${info.title}`}
              aria-expanded={hoveredDimension === k || tappedDimension === k}
              className="cf-axis-hit"
              onMouseEnter={() => setHoveredDimension(k)}
              onMouseLeave={() => setHoveredDimension((cur) => (cur === k ? null : cur))}
              onFocus={() => setHoveredDimension(k)}
              onBlur={() => setHoveredDimension((cur) => (cur === k ? null : cur))}
              onClick={() => setTappedDimension((cur) => (cur === k ? null : k))}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  setHoveredDimension((cur) => (cur === k ? null : k));
                }
              }}
            >
              <rect
                x={labelPositions[k].x - 34}
                y={labelPositions[k].y - 16}
                width={68}
                height={32}
                fill="transparent"
              />
              <text
                x={labelPositions[k].x}
                y={labelPositions[k].y}
                textAnchor={labelPositions[k].anchor}
                fill={k === domKey ? accent.text : "var(--color-slate)"}
                className="font-mono"
                fontSize="14"
                fontWeight={k === domKey ? 700 : 400}
                letterSpacing="1"
              >
                {AXIS_LABELS[k]}
              </text>
            </g>
          );
        })}

        {/* Depth stacking (Direction 1, this session) -- a low-alpha charcoal
            backing stroke immediately behind the real shape, same points,
            giving the shape a subtle sense of thickness/depth rather than a
            flat single outline. Never severity-conditional -- depth is a
            rendering-quality property, not a signal. pathLength={1} +
            cf-shape-entrance (Direction 1 Refinement, this session): a
            CSS-only stroke-dashoffset "draw-in" on mount, normalized via
            the pathLength trick so the real perimeter length never needs
            computing in JS. Only affects the stroke, never fill/opacity, so
            it can't fight this element's own opacity="0.08". Exists only
            inside a `(prefers-reduced-motion: no-preference)` media query
            in globals.css -- renders at its normal, fully-drawn state by
            default with zero JS check needed. */}
        <polygon
          points={shapePoints}
          fill="none"
          stroke="var(--color-charcoal)"
          strokeWidth="4"
          opacity="0.08"
          pathLength={1}
          className="cf-shape-entrance"
        />

        {/* The weighted shape — fill is the centroid-tracking radial gradient
            defined above (Direction 1, this session), replacing the prior flat
            color-mix. Stroke stays ALWAYS --color-slate, never severity-
            conditional. Confirmed from the mockup: only the dominant vertex's
            rings, center dot, and axis label switch to --color-rust at Endemic.
            Same cf-shape-entrance stroke draw-in as the backing polygon above. */}
        <polygon
          points={shapePoints}
          fill={`url(#${gradientId})`}
          stroke="var(--color-slate)"
          strokeWidth="1.5"
          pathLength={1}
          className="cf-shape-entrance"
        />

        {/* Vertex glow (Direction 1, this session) -- data-driven, scaled per
            axis to that axis's real dimension_summary weight (see the
            per-axis feGaussianBlur filters above). Dominant vertex glows in
            the tier-gated accent color; all others stay --color-slate --
            same color rule the crisp dots/rings below already use, not a
            new one. Rendered beneath those dots/rings, purely additive. */}
        {(Object.keys(AXES) as AxisKey[]).map((k) => (
          <circle
            key={`glow-${k}`}
            cx={points[k].x}
            cy={points[k].y}
            r={GLOW_BASE_R}
            fill={k === domKey ? accent.stroke : "var(--color-slate)"}
            opacity={GLOW_OPACITY_MIN + weights[k] * (GLOW_OPACITY_MAX - GLOW_OPACITY_MIN)}
            filter={`url(#${glowFilterId(k)})`}
          />
        ))}

        {/* Non-dominant vertex dots — always --color-slate. */}
        {(Object.keys(AXES) as AxisKey[])
          .filter((k) => k !== domKey)
          .map((k) => (
            <circle key={k} cx={points[k].x} cy={points[k].y} r={4} fill="var(--color-slate)" />
          ))}

        {/* Severity rings — fixed 5-ring pattern, radii/opacity never vary
            by severity tier. Only the color varies (accent.stroke: --color-slate
            at Emerging/Entrenched, --color-rust only at genuine Endemic). */}
        <g filter={`url(#${filterId})`} fill="none" stroke={accent.stroke} strokeWidth="1">
          {LIVE_RING_RADII.map((r, i) => (
            <circle
              key={r}
              cx={domPoint.x}
              cy={domPoint.y}
              r={r}
              opacity={LIVE_RING_OPACITY[i]}
            />
          ))}
        </g>
        <circle cx={domPoint.x} cy={domPoint.y} r={5} fill={accent.stroke} />
      </svg>

      {/* Desktop reveal panel (Direction 1 Refinement, this session) --
          hover/focus-triggered, positioned near the active axis's fixed
          label position (percentage of the viewBox, not the data-driven
          vertex point, so it never jumps around as weights differ).
          Reuses PUBLIC_DIMENSION_LABELS verbatim -- locked, brand-voice-
          approved copy, Pete's confirmed decision this session. */}
      {hoveredInfo && hoveredDimension && (
        <div
          className="hidden md:block absolute z-10 w-56 rounded-md border border-gray-200 bg-white p-3 shadow-lg pointer-events-none"
          style={{
            left: `${(labelPositions[hoveredDimension].x / LIVE_VIEW_W) * 100}%`,
            top: `${(labelPositions[hoveredDimension].y / LIVE_VIEW_H) * 100}%`,
            transform: "translate(-50%, 12px)",
          }}
        >
          <p className="font-ui text-[12px] font-semibold text-charcoal mb-1">
            {hoveredInfo.title}
          </p>
          <p className="font-ui text-[11px] text-gray-500 leading-relaxed">
            {hoveredInfo.description}
          </p>
        </div>
      )}

      {/* Mobile reveal (Direction 1 Refinement, this session) -- vaul bottom
          sheet, same desktop-panel/mobile-drawer split StateDrawer.tsx
          already established, reused rather than a new pattern. Opens only
          from an actual click/tap on the axis hit-area above -- never from
          hover or keyboard focus, so a desktop keyboard user never triggers
          the Drawer's own body-scroll-lock behavior. */}
      <Drawer.Root
        open={Boolean(tappedDimension)}
        onOpenChange={(open) => {
          if (!open) setTappedDimension(null);
        }}
      >
        <Drawer.Portal>
          <Drawer.Overlay className="fixed inset-0 bg-black/30 z-40 md:hidden" />
          <Drawer.Content className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-2xl md:hidden">
            <Drawer.Title className="sr-only">
              {tappedInfo?.title ?? "Dimension detail"}
            </Drawer.Title>
            <div className="w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-2" />
            {tappedInfo && (
              <div className="p-4 pb-8">
                <p className="font-ui text-sm font-semibold text-charcoal mb-1">
                  {tappedInfo.title}
                </p>
                <p className="font-ui text-[13px] text-gray-500 leading-relaxed">
                  {tappedInfo.description}
                </p>
              </div>
            )}
          </Drawer.Content>
        </Drawer.Portal>
      </Drawer.Root>
    </div>
  );
}'''

# ---------------------------------------------------------------------------
# (2) globals.css
# ---------------------------------------------------------------------------

OLD_CSS_ANCHOR = '''@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@layer utilities {'''

NEW_CSS_ANCHOR = '''@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ConstellationField assembly animation (Direction 1 Refinement, Category E,
   this session) -- stroke-only "draw-in" on mount for the live-mode weighted
   shape, via the pathLength={1} normalization trick (no JS perimeter-length
   computation needed). Deliberately animates stroke-dashoffset only, never
   opacity/fill -- both polygons this applies to have their own fixed
   opacity (0.08 for the depth-backing stroke, 1 implicit for the main
   gradient-filled shape), and an opacity keyframe would fight those SVG
   presentation attributes. Same cubic-bezier(0.16, 1, 0.3, 1) curve as the
   shipped Direction 1 "resolve" transition below, per Gemini's cleared
   review this session -- duration 600ms, longer than that transition's
   350ms since this is a one-time load moment, not a hover micro-transition. */
@keyframes cf-shape-assemble {
  from {
    stroke-dashoffset: 1;
  }
  to {
    stroke-dashoffset: 0;
  }
}

@layer utilities {
  /* Gated inside prefers-reduced-motion: no-preference -- when reduced
     motion IS preferred, this class does nothing at all (stroke-dasharray
     never gets set), so the shape renders at its normal, fully-drawn state
     immediately. No JS matchMedia check needed, unlike AmbientField's
     continuous animation loop. */
  @media (prefers-reduced-motion: no-preference) {
    .cf-shape-entrance {
      stroke-dasharray: 1;
      animation: cf-shape-assemble 600ms cubic-bezier(0.16, 1, 0.3, 1) both;
    }
  }
'''

# ---------------------------------------------------------------------------
# (3) ConstellationField.test.ts
# ---------------------------------------------------------------------------

OLD_TEST_IMPORT = '''import {
  AXES,
  KEYFRAMES,
  RESTING_FRAME,
  LIVE_CENTER,
  LIVE_MAX_R,
  computeFrame,
  dominantAxis,
  pointFor,
  pointsAttr,
  polarPoint,
  severityAccentTokens,
} from "./ConstellationField";'''

NEW_TEST_IMPORT = '''import {
  AXES,
  KEYFRAMES,
  RESTING_FRAME,
  LIVE_CENTER,
  LIVE_MAX_R,
  axisToDimensionKey,
  computeFrame,
  dominantAxis,
  pointFor,
  pointsAttr,
  polarPoint,
  severityAccentTokens,
} from "./ConstellationField";'''

OLD_TEST_TAIL = '''describe("live-mode vertex geometry", () => {
  it("reproduces the results mockup's own example exactly (hand-verified against its rendered SVG)", () => {
    // mockup: apt .15, auth .55, all .10, att .20 -> polygon
    // "300,267 421,300 300,322 256,300"
    expect(polarPoint(0.15, AXES.apt, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 300, y: 267 });
    expect(polarPoint(0.55, AXES.auth, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 421, y: 300 });
    expect(polarPoint(0.1, AXES.all, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 300, y: 322 });
    expect(polarPoint(0.2, AXES.att, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 256, y: 300 });
  });
});'''

NEW_TEST_TAIL = '''describe("live-mode vertex geometry", () => {
  it("reproduces the results mockup's own example exactly (hand-verified against its rendered SVG)", () => {
    // mockup: apt .15, auth .55, all .10, att .20 -> polygon
    // "300,267 421,300 300,322 256,300"
    expect(polarPoint(0.15, AXES.apt, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 300, y: 267 });
    expect(polarPoint(0.55, AXES.auth, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 421, y: 300 });
    expect(polarPoint(0.1, AXES.all, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 300, y: 322 });
    expect(polarPoint(0.2, AXES.att, LIVE_CENTER, LIVE_MAX_R)).toEqual({ x: 256, y: 300 });
  });
});

// Direction 1 Refinement (Category E, this session) -- interpretability's
// reveal copy is sourced from PUBLIC_DIMENSION_LABELS (book-taxonomy-labels.ts),
// keyed by the full DimensionKey, not the SVG's abbreviated AxisKey. Locks in
// the mapping so a future rename of either key set surfaces as a real test
// failure rather than a silent wrong-copy bug at runtime.
describe("axisToDimensionKey", () => {
  it("maps each abbreviated AxisKey to its full DimensionKey", () => {
    expect(axisToDimensionKey("apt")).toBe("aptitude");
    expect(axisToDimensionKey("auth")).toBe("authority");
    expect(axisToDimensionKey("all")).toBe("alliance");
    expect(axisToDimensionKey("att")).toBe("attitude");
  });
});'''

# ---------------------------------------------------------------------------
# (4) tools/_mob.txt -- standalone Decision Register row
# ---------------------------------------------------------------------------

MOB_ANCHOR_TAIL = (
    "Pete's call -- reopen once ready to send Direction 1 "
    "Refinement to Gemini for architecture review; no code changes "
    "before that clears. Direction 2 stays shelved indefinitely unless "
    "Pete explicitly reopens it |"
)

MOB_NEW_ROW = (
    "| Gemini file-path citation for ConstellationField.tsx / "
    "PrivateOutput.tsx -- CONFIRMED RECURRING, 3rd instance | "
    "N/A -- reviewer-behavior fact, not a Tier 1-4 workflow item | "
    "Confirmed, informational -- no code impact, both real paths already "
    "verified and used correctly in every build | N/A | Gemini's "
    "Direction 3 review (this project, prior session) cited "
    "web/app/diagnostic/components/PrivateOutput.tsx -- confirmed "
    "nonexistent at the time. Gemini's Direction 1 Refinement review "
    "(this session) repeated the identical wrong directory for BOTH "
    "files: web/app/diagnostic/components/ConstellationField.tsx and "
    "web/app/diagnostic/components/PrivateOutput.tsx. Confirmed via "
    "direct filesystem search before writing any diff: "
    "web/app/diagnostic/ contains only page.tsx, no components "
    "subdirectory exists there at all. Real paths, unchanged since "
    "Direction 1 shipped: web/components/ConstellationField.tsx, "
    "web/components/PrivateOutput.tsx. Two of Gemini's other specific "
    "claims in the same review (globals.css line numbers for "
    "--color-rust and the data-emphasis block, and the secondary "
    "state's scale value) were also wrong when checked directly -- "
    "logged in this row for pattern-tracking since it's the same "
    "review, but the file-path error is the one now confirmed across "
    "three separate reviews for these exact two files, not a one-off. "
    "Standing recommendation: any future Gemini prompt touching either "
    "file should state the real path upfront rather than re-catching "
    "this a fourth time. | This session (Claude Code), 2026-08-13 | "
    "No forced check-in -- informational, pattern-tracking only. If a "
    "fourth instance surfaces for these same two files, treat it as "
    "confirmation the standing recommendation above should become a "
    "hard rule in the Gemini handoff template, not just advisory |"
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    # --- ConstellationField.tsx ---
    cf = CF_PATH.read_text(encoding="utf-8")
    cf_orig = cf
    for old, new, label in [
        (OLD_CF_IMPORTS, NEW_CF_IMPORTS, "imports"),
        (OLD_AXIS_LABELS_BLOCK, NEW_AXIS_LABELS_BLOCK, "axisToDimensionKey"),
        (OLD_LIVEFIELD, NEW_LIVEFIELD, "LiveField"),
    ]:
        count = cf.count(old)
        if count != 1:
            print(f"FAIL (ConstellationField.tsx, {label}): expected 1 match, found {count}")
            sys.exit(1)
        cf = cf.replace(old, new, 1)
    if cf == cf_orig:
        print("FAIL: ConstellationField.tsx unchanged")
        sys.exit(1)

    # --- globals.css ---
    css = CSS_PATH.read_text(encoding="utf-8")
    css_orig = css
    count = css.count(OLD_CSS_ANCHOR)
    if count != 1:
        print(f"FAIL (globals.css): expected 1 match, found {count}")
        sys.exit(1)
    css = css.replace(OLD_CSS_ANCHOR, NEW_CSS_ANCHOR, 1)
    if css == css_orig:
        print("FAIL: globals.css unchanged")
        sys.exit(1)

    # --- ConstellationField.test.ts ---
    test = TEST_PATH.read_text(encoding="utf-8")
    test_orig = test
    for old, new, label in [
        (OLD_TEST_IMPORT, NEW_TEST_IMPORT, "import"),
        (OLD_TEST_TAIL, NEW_TEST_TAIL, "new test"),
    ]:
        count = test.count(old)
        if count != 1:
            print(f"FAIL (ConstellationField.test.ts, {label}): expected 1 match, found {count}")
            sys.exit(1)
        test = test.replace(old, new, 1)
    if test == test_orig:
        print("FAIL: ConstellationField.test.ts unchanged")
        sys.exit(1)

    # --- tools/_mob.txt ---
    mob = MOB_PATH.read_text(encoding="utf-8")
    mob_orig = mob
    count = mob.count(MOB_ANCHOR_TAIL)
    if count != 1:
        print(f"FAIL (_mob.txt): expected 1 match for anchor, found {count}")
        sys.exit(1)
    mob = mob.replace(MOB_ANCHOR_TAIL, MOB_ANCHOR_TAIL + "\n" + MOB_NEW_ROW, 1)
    if mob == mob_orig:
        print("FAIL: _mob.txt unchanged")
        sys.exit(1)

    print(f"ConstellationField.tsx diff: {len(cf) - len(cf_orig):+d} chars")
    print(f"globals.css diff: {len(css) - len(css_orig):+d} chars")
    print(f"ConstellationField.test.ts diff: {len(test) - len(test_orig):+d} chars")
    print(f"_mob.txt diff: {len(mob) - len(mob_orig):+d} chars")

    if args.write:
        CF_PATH.write_text(cf, encoding="utf-8")
        CSS_PATH.write_text(css, encoding="utf-8")
        TEST_PATH.write_text(test, encoding="utf-8")
        MOB_PATH.write_text(mob, encoding="utf-8")
        print("WRITTEN.")
    else:
        print("DRY RUN -- no files written. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
