// Homepage restructure (this session) -- replaces <ConstellationField
// mode="ambient" /> in the hero. That component turned out to render a
// plainer visual than the approved mockup (no breathing rings, no vertex
// dots, no ambient motion -- a static outline) once compared against a
// live screenshot. ConstellationField.tsx is explicitly off-limits for
// modification (shared, live, drives real diagnostic output elsewhere) --
// this is a fully separate, homepage-local component, not an edit to it.
//
// No "use client" -- pure declarative SVG plus CSS keyframe animations
// (globals.css), no hooks, no interactivity. Renders correctly server-side;
// prefers-reduced-motion gating happens entirely in CSS (see globals.css's
// signature-ring-breathe/signature-quad-breathe, same gating pattern as
// .animate-fade-up-gated), so there's no JS matchMedia check to duplicate.
//
// Geometry is a fixed, static resting frame -- NOT a reimplementation of
// AmbientField's continuous 9-keyframe interpolation loop. Copied as literal
// coordinates from ConstellationField.tsx's own real constants (VIEW_W=900,
// VIEW_H=640, CENTER={x:450,y:320}, MAX_R=580, KEYFRAMES[0] weights
// {apt:0.35, auth:0.3, all:0.25, att:0.3}) via the identical polarPoint
// formula that file uses, hand-computed once here since importing from a
// file we're forbidden to modify (and don't want to create a live coupling
// to) isn't the right call for four fixed numbers that never change.

const VIEW_W = 900;
const VIEW_H = 640;
const CENTER = { x: 450, y: 320 };

const QUAD_POINTS = "450,117 624,320 450,465 276,320";

const VERTEX_DOTS = [
  { cx: 450, cy: 117 }, // Aptitude (top)
  { cx: 624, cy: 320 }, // Authority (right)
  { cx: 450, cy: 465 }, // Alliance (bottom)
  { cx: 276, cy: 320 }, // Attitude (left)
];

// Three concentric rings framing the quad, staggered breathing animation
// (negative animation-delay so each ring appears mid-cycle from first
// paint, rather than popping in from a shared start). Base opacity here is
// the resting/reduced-motion value -- signature-ring-breathe's own 0%/100%
// keyframe (0.16) and 50% keyframe (0.38) only apply when the animation is
// active; this inline value is what a reduced-motion viewer actually sees.
const RING_RADII = [220, 280, 340];
const RING_DELAY_STEP_S = 1.4;

export function SignatureField() {
  return (
    <div className="relative aspect-900/640 w-full">
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
        role="img"
        aria-label="Weighted four-axis diagnostic field: Aptitude, Authority, Alliance, Attitude"
      >
        {RING_RADII.map((r, i) => (
          <circle
            key={r}
            cx={CENTER.x}
            cy={CENTER.y}
            r={r}
            fill="none"
            stroke="var(--home-slate)"
            strokeWidth="1"
            className="signature-ring-breathe"
            style={{ opacity: 0.27, animationDelay: `${-i * RING_DELAY_STEP_S}s` }}
          />
        ))}
        <g className="signature-quad-breathe">
          <polygon
            points={QUAD_POINTS}
            fill="color-mix(in srgb, var(--home-slate) 10%, transparent)"
            stroke="var(--home-slate)"
            strokeWidth="1.4"
          />
          {VERTEX_DOTS.map((p) => (
            <circle key={`${p.cx}-${p.cy}`} cx={p.cx} cy={p.cy} r={3.5} fill="var(--home-slate)" />
          ))}
        </g>
      </svg>
      <span className="absolute top-2 left-1/2 -translate-x-1/2 font-mono text-[10px] tracking-widest text-(--home-slate)">
        APTITUDE
      </span>
      <span className="absolute right-1 top-1/2 -translate-y-1/2 font-mono text-[10px] tracking-widest text-(--home-slate)">
        AUTHORITY
      </span>
      <span className="absolute bottom-2 left-1/2 -translate-x-1/2 font-mono text-[10px] tracking-widest text-(--home-slate)">
        ALLIANCE
      </span>
      <span className="absolute left-1 top-1/2 -translate-y-1/2 font-mono text-[10px] tracking-widest text-(--home-slate)">
        ATTITUDE
      </span>
    </div>
  );
}
