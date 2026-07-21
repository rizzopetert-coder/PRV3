"use client";

import { useEffect, useId, useRef } from "react";

// Ambient ConstellationField (Stage 2, OD-07 visual identity v2 — hybrid
// Constellation-Topology model). Ported from the approved reference
// mockup (mockups/pr-ambient-constellation-animation.html) — same
// technique, not hand-copied static SVG: linear interpolation (not
// eased, see TRANSITION_MS below), overflow-carried segment timing,
// dominant-axis point recalculated continuously each frame, feTurbulence
// + feDisplacementMap for the organic-wavy severity rings.
//
// HARD CAP, from the brief: this mode NEVER uses --urgency/--urgency-text
// — general accent (--oxide/--oxide-text) only, always. Enforced
// structurally, not by bounding the `ring` animation parameter to some
// numeric threshold: render() below hardcodes stroke to var(--oxide)
// unconditionally — there is no code path in this component that can
// ever reference --urgency. A decorative loop cycling through "Endemic"
// with nothing actually wrong would devalue the signal the reserved
// token exists to protect. Live/severity-driven color (using --urgency
// only when a real severity tier is actually Endemic) is "live" mode —
// not built yet, gated on Stage 3's data-contract investigation.
//
// Respects prefers-reduced-motion: renders once at the resting keyframe,
// no animation loop, checked once at mount (matches the reference
// mockup's behavior exactly — not reactive to a live OS-setting change
// mid-session).

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

export function pointFor(weight: number, angleDeg: number): { x: number; y: number } {
  const rad = (angleDeg * Math.PI) / 180;
  const r = MAX_R * weight;
  return { x: CENTER.x + r * Math.cos(rad), y: CENTER.y + r * Math.sin(rad) };
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
  // across the shape during transitions rather than jumping. Tie-break
  // order (auth, apt, all, att) matches the reference mockup exactly.
  const domKey: AxisKey =
    w.auth >= w.apt && w.auth >= w.all && w.auth >= w.att
      ? "auth"
      : w.apt >= w.all && w.apt >= w.att
        ? "apt"
        : w.all >= w.att
          ? "all"
          : "att";
  return { w, ring, domKey };
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

export function ConstellationField() {
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
      // HARD CAP: always --oxide, never --urgency. See file header.
      ringGroup.setAttribute("stroke", "var(--oxide)");

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
      <g stroke="var(--line)" strokeWidth="1" fill="none">
        <line x1={CENTER.x} y1={CENTER.y - 190} x2={CENTER.x} y2={CENTER.y + 190} />
        <line x1={CENTER.x - 190} y1={CENTER.y} x2={CENTER.x + 190} y2={CENTER.y} />
      </g>
      <polygon
        ref={shapeRef}
        points={pointsAttr(RESTING_FRAME)}
        fill="color-mix(in srgb, var(--oxide) 10%, transparent)"
        stroke="var(--oxide)"
        strokeWidth="1.4"
        opacity="0.8"
      />
      <g
        ref={ringGroupRef}
        filter={`url(#${filterId})`}
        fill="none"
        stroke="var(--oxide)"
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
