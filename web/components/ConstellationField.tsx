"use client";

import { useEffect, useId, useRef, useState } from "react";
import { Drawer } from "vaul";
import type { SeverityTier } from "@/lib/types";
import type { DimensionKey } from "@/lib/book-manifest";
import { PUBLIC_DIMENSION_LABELS } from "@/lib/book-taxonomy-labels";

// ConstellationField (OD-07 visual identity v2 — hybrid
// Constellation-Topology model). Two modes:
//
// "ambient" (Stage 2) — decorative, self-animating, hero use. Ported from
// mockups/pr-ambient-constellation-animation.html: linear interpolation
// (not eased, see TRANSITION_MS below), overflow-carried segment timing,
// dominant-axis point recalculated continuously each frame. HARD CAP:
// never uses --color-rust, enforced structurally — render()
// hardcodes stroke to var(--color-slate) unconditionally, no code path in
// ambient mode can ever reference --color-rust. A decorative loop cycling
// through "Endemic" with nothing actually wrong would devalue the signal
// the reserved token exists to protect. Respects prefers-reduced-motion:
// renders once at the resting keyframe, no animation loop, checked once
// at mount.
//
// "live" (Stage 3) — static, results-page use, real per-dimension weights
// and severity tier as props. Ported from
// mockups/pr-results-constellation-mockup.html. --color-rust
// ONLY when severityTier is genuinely "Endemic"; --color-slate at
// Emerging/Entrenched. Confirmed from the mockup (only one severity
// example shown, cross-checked against its own weight percentages, not
// guessed): ring visibility/count/opacity is a FIXED 5-ring pattern that
// does NOT vary by severity tier at all — severity only ever changes
// which color token is used, never ring count or intensity. The weighted
// shape itself (fill/stroke) and non-dominant vertex dots/labels are
// ALWAYS --color-slate, never severity-conditional — only the dominant
// vertex's rings + center dot + axis label switch color.
//
// weights prop is populated from the real dimension_summary field in the
// output contract (engine/contract.py's assemble_output(), Gemini-cleared,
// per-axis normalized [0,1] score) — wired live in web/components/
// PrivateOutput.tsx, confirmed present in this payload at runtime for both
// Path A and Path B, not just in the type. This comment previously said
// "not wired yet, pending separate review" — stale as of the Direction 1
// build (Category E, this session), corrected here.

const VIEW_W = 900;
const VIEW_H = 640;
const CENTER = { x: 450, y: 320 };
const MAX_R = 200;

export type AxisKey = "apt" | "auth" | "all" | "att";

// Aptitude top / Authority right / Alliance bottom / Attitude left — SVG
// angle convention (0deg = right, 90deg = down, since y increases
// downward), matching the brief's four-axis layout exactly.
export const AXES: Record<AxisKey, number> = {
  apt: -90,
  auth: 0,
  all: 90,
  att: 180,
};

export interface Keyframe {
  w: Record<AxisKey, number>;
  ring: number;
}

// Verbatim from the reference mockup — working values, not redesigned.
export const KEYFRAMES: Keyframe[] = [
  { w: { apt: 0.35, auth: 0.3, all: 0.25, att: 0.3 }, ring: 0.0 },
  { w: { apt: 0.15, auth: 0.58, all: 0.12, att: 0.22 }, ring: 1.1 },
  { w: { apt: 0.15, auth: 0.58, all: 0.12, att: 0.22 }, ring: 1.6 },
  { w: { apt: 0.55, auth: 0.22, all: 0.15, att: 0.3 }, ring: 0.9 },
  { w: { apt: 0.55, auth: 0.22, all: 0.15, att: 0.3 }, ring: 1.4 },
  { w: { apt: 0.22, auth: 0.18, all: 0.28, att: 0.56 }, ring: 1.0 },
  { w: { apt: 0.22, auth: 0.18, all: 0.28, att: 0.56 }, ring: 1.5 },
  { w: { apt: 0.28, auth: 0.15, all: 0.52, att: 0.2 }, ring: 0.9 },
  { w: { apt: 0.28, auth: 0.15, all: 0.52, att: 0.2 }, ring: 1.4 },
];

// Linear, not ease-in-out — per-segment ease-in-out was tried and
// rejected: it decelerates to zero velocity at every waypoint, which
// reads as a stutter even with zero hold time. Constant motion needs
// continuous velocity straight through each handoff.
const TRANSITION_MS = 3200;

const RING_RADII = [14, 26, 38, 50, 62, 74];
const RING_BASE_OPACITY = [0.85, 0.68, 0.52, 0.38, 0.26, 0.16];

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

// Shared polar-to-cartesian core for both modes — ambient and live use
// different canvas dimensions (different center/max radius), same math.
export function polarPoint(
  weight: number,
  angleDeg: number,
  center: { x: number; y: number },
  maxR: number,
): { x: number; y: number } {
  const rad = (angleDeg * Math.PI) / 180;
  const r = maxR * weight;
  return { x: center.x + r * Math.cos(rad), y: center.y + r * Math.sin(rad) };
}

export function pointFor(weight: number, angleDeg: number): { x: number; y: number } {
  return polarPoint(weight, angleDeg, CENTER, MAX_R);
}

// Tie-break order (auth, apt, all, att) matches the reference mockup
// exactly. Shared by ambient's continuous per-frame recalculation and
// live's one-time static calculation.
export function dominantAxis(w: Record<AxisKey, number>): AxisKey {
  return w.auth >= w.apt && w.auth >= w.all && w.auth >= w.att
    ? "auth"
    : w.apt >= w.all && w.apt >= w.att
      ? "apt"
      : w.all >= w.att
        ? "all"
        : "att";
}

export interface Frame {
  w: Record<AxisKey, number>;
  ring: number;
  domKey: AxisKey;
}

export function computeFrame(kfA: Keyframe, kfB: Keyframe, t: number): Frame {
  const w = {} as Record<AxisKey, number>;
  (Object.keys(AXES) as AxisKey[]).forEach((k) => {
    w[k] = lerp(kfA.w[k], kfB.w[k], t);
  });
  const ring = lerp(kfA.ring, kfB.ring, t);
  // Dominant point recalculated continuously from the CURRENT interpolated
  // weights (not a static per-keyframe label) — the ring cluster glides
  // across the shape during transitions rather than jumping.
  return { w, ring, domKey: dominantAxis(w) };
}

export function pointsAttr(frame: Frame): string {
  const p = (Object.keys(AXES) as AxisKey[]).reduce(
    (acc, k) => {
      acc[k] = pointFor(frame.w[k], AXES[k]);
      return acc;
    },
    {} as Record<AxisKey, { x: number; y: number }>,
  );
  return `${p.apt.x},${p.apt.y} ${p.auth.x},${p.auth.y} ${p.all.x},${p.all.y} ${p.att.x},${p.att.y}`;
}

// Static resting frame (keyframe 0, t=0) computed ahead of time so the
// initial markup already shows the correct shape before any JS runs —
// no flash of a placeholder, unlike the reference mockup (which has
// hardcoded placeholder SVG points immediately overwritten by its own
// load-time script call).
export const RESTING_FRAME = computeFrame(KEYFRAMES[0], KEYFRAMES[0], 0);

// ---------------------------------------------------------------------------
// Live mode (Stage 3) — static, results-page use.
// Ported from mockups/pr-results-constellation-mockup.html.
// ---------------------------------------------------------------------------

const LIVE_VIEW_W = 600;
const LIVE_VIEW_H = 600;
export const LIVE_CENTER = { x: 300, y: 300 };
// Confirmed by back-solving the mockup's own example against its labeled
// percentages (Authority 55% -> vertex at x=421, i.e. 121px from center;
// 121 / 0.55 = 220), not assumed — same MAX_R for all four axes, checked
// against all four vertices, all four matched exactly.
export const LIVE_MAX_R = 220;

// Reference guide diamonds at 25% / 50% / 75% of LIVE_MAX_R — always
// #e5e7eb, never severity-conditional.
const LIVE_GUIDE_RING_FRACTIONS = [0.25, 0.5, 0.75];

// Fixed 5-ring pattern — does NOT vary by severity tier. Confirmed from
// the mockup: severity only changes color (see severityAccentTokens),
// never count, radii, or opacity.
export const LIVE_RING_RADII = [14, 28, 42, 56, 70];
export const LIVE_RING_OPACITY = [0.9, 0.7, 0.5, 0.35, 0.22];

// Vertex glow (Direction 1, Category E, this session) — data-driven,
// scaled per axis to the real dimension_summary weight (0.0-1.0), not a
// fixed effect applied uniformly. Both blur radius (feGaussianBlur
// stdDeviation) and opacity interpolate between these min/max pairs.
const GLOW_BASE_R = 10;
const GLOW_STD_MIN = 2;
const GLOW_STD_MAX = 9;
const GLOW_OPACITY_MIN = 0.12;
const GLOW_OPACITY_MAX = 0.42;

const AXIS_LABELS: Record<AxisKey, string> = {
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
}

// --color-rust ONLY when severityTier is genuinely "Endemic".
// --color-slate at Emerging/Entrenched. This is the one piece of
// real branching logic live mode introduces — pure function, tested in
// isolation (ConstellationField.test.ts).
export function severityAccentTokens(tier: SeverityTier): {
  stroke: string;
  text: string;
} {
  if (tier === "Endemic") {
    return { stroke: "var(--color-rust)", text: "var(--color-rust)" };
  }
  return { stroke: "var(--color-slate)", text: "var(--color-slate)" };
}

function AmbientField() {
  // Unique per instance so the SVG filter id can't collide with another
  // instance of this component, or any other SVG def, on the same page.
  const filterId = useId();

  const shapeRef = useRef<SVGPolygonElement>(null);
  const ringGroupRef = useRef<SVGGElement>(null);
  const ringRefs = useRef<(SVGCircleElement | null)[]>([]);

  useEffect(() => {
    function render(frame: Frame) {
      const shape = shapeRef.current;
      const ringGroup = ringGroupRef.current;
      if (!shape || !ringGroup) return;

      shape.setAttribute("points", pointsAttr(frame));

      const domPoint = pointFor(frame.w[frame.domKey], AXES[frame.domKey]);
      ringGroup.setAttribute(
        "transform",
        `translate(${domPoint.x - CENTER.x}, ${domPoint.y - CENTER.y})`,
      );
      // HARD CAP: always --color-slate, never --color-rust. See file header.
      ringGroup.setAttribute("stroke", "var(--color-slate)");

      ringRefs.current.forEach((el, i) => {
        if (!el) return;
        const visible = Math.max(0, Math.min(1, frame.ring - i * 0.32));
        el.setAttribute("opacity", (visible * RING_BASE_OPACITY[i]).toFixed(3));
      });
    }

    // Unconditional initial render at the resting frame, matching the
    // reference mockup's own call order (renders once, then decides
    // whether to start the loop).
    render(RESTING_FRAME);

    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    if (prefersReducedMotion) {
      return;
    }

    let kfIndex = 0;
    let segmentStart = performance.now();
    let rafId: number;

    function tick(now: number) {
      let elapsed = now - segmentStart;

      // Carry overflow into the next segment instead of resetting to
      // `now` — resetting would eat a few ms every loop and, over many
      // segments, introduce exactly the kind of micro-pause this
      // technique exists to avoid.
      while (elapsed >= TRANSITION_MS) {
        elapsed -= TRANSITION_MS;
        segmentStart += TRANSITION_MS;
        kfIndex = (kfIndex + 1) % KEYFRAMES.length;
      }

      const kfB = KEYFRAMES[(kfIndex + 1) % KEYFRAMES.length];
      const t = elapsed / TRANSITION_MS;
      render(computeFrame(KEYFRAMES[kfIndex], kfB, t));

      rafId = requestAnimationFrame(tick);
    }

    rafId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafId);
  }, []);

  return (
    <svg
      className="absolute inset-0 w-full h-full"
      style={{ opacity: 0.55 }}
      viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
    >
      <defs>
        <filter
          id={filterId}
          x="-60%"
          y="-60%"
          width="220%"
          height="220%"
        >
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.03"
            numOctaves={2}
            seed={5}
            result="n"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="n"
            scale={6}
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>
      </defs>
      <g stroke="#e5e7eb" strokeWidth="1" fill="none">
        <line x1={CENTER.x} y1={CENTER.y - 190} x2={CENTER.x} y2={CENTER.y + 190} />
        <line x1={CENTER.x - 190} y1={CENTER.y} x2={CENTER.x + 190} y2={CENTER.y} />
      </g>
      <polygon
        ref={shapeRef}
        points={pointsAttr(RESTING_FRAME)}
        fill="color-mix(in srgb, var(--color-slate) 10%, transparent)"
        stroke="var(--color-slate)"
        strokeWidth="1.4"
        opacity="0.8"
      />
      <g
        ref={ringGroupRef}
        filter={`url(#${filterId})`}
        fill="none"
        stroke="var(--color-slate)"
        strokeWidth="1"
      >
        {RING_RADII.map((r, i) => (
          <circle
            key={r}
            ref={(el) => {
              ringRefs.current[i] = el;
            }}
            cx={0}
            cy={0}
            r={r}
            opacity={0}
          />
        ))}
      </g>
    </svg>
  );
}

interface LiveFieldProps {
  weights: Record<AxisKey, number>;
  severityTier: SeverityTier;
}

function LiveField({ weights, severityTier }: LiveFieldProps) {
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
}

export type ConstellationFieldProps =
  | { mode: "ambient" }
  | ({ mode: "live" } & LiveFieldProps);

export function ConstellationField(props: ConstellationFieldProps) {
  if (props.mode === "live") {
    return <LiveField weights={props.weights} severityTier={props.severityTier} />;
  }
  return <AmbientField />;
}
