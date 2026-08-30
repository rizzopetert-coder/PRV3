"use client";

import Link from "next/link";
import type { ReactElement } from "react";
import { useScrollReveal } from "./useScrollReveal";

// Homepage restructure (this session) -- hand-rolled inline SVG line icons,
// stroke="currentColor" so each inherits its card's text-(--home-slate),
// matching the currentColor convention NavBar.tsx's own caret icon already
// uses. No icon library in package.json -- not introducing one for four
// icons that only need to exist here.

function DiagnosticIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="10" cy="10" r="6" stroke="currentColor" strokeWidth="1.5" />
      <line x1="14.6" y1="14.6" x2="20" y2="20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

function BookIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M3 6c3-1.5 6-1.5 9 0v13c-3-1.5-6-1.5-9 0V6Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path
        d="M21 6c-3-1.5-6-1.5-9 0v13c3-1.5 6-1.5 9 0V6Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// Six radiating lines at 60-degree intervals, r=5 to r=9 from (12,12).
// Hardcoded literals, not a Math.cos/sin computation at render time --
// transcendental functions aren't guaranteed bit-identical across engines
// (confirmed live: SSR under Node's V8 and hydration under Chromium's V8
// produced a 1-ULP difference on the same expression, e.g. 7.669872981077808
// vs ...807, which React's hydration diffing flags and refuses to patch).
// Fixed literals remove the possibility entirely.
const SERVICES_ICON_LINES = [
  { x1: 17, y1: 12, x2: 21, y2: 12 },
  { x1: 14.5, y1: 16.33, x2: 16.5, y2: 19.79 },
  { x1: 9.5, y1: 16.33, x2: 7.5, y2: 19.79 },
  { x1: 7, y1: 12, x2: 3, y2: 12 },
  { x1: 9.5, y1: 7.67, x2: 7.5, y2: 4.21 },
  { x1: 14.5, y1: 7.67, x2: 16.5, y2: 4.21 },
];

function ServicesIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.5" />
      {SERVICES_ICON_LINES.map((l, i) => (
        <line key={i} x1={l.x1} y1={l.y1} x2={l.x2} y2={l.y2} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      ))}
    </svg>
  );
}

function AboutIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="8" r="3.2" stroke="currentColor" strokeWidth="1.5" />
      <path
        d="M5.5 20c0-4.5 3-7 6.5-7s6.5 2.5 6.5 7"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

interface WayfindingCard {
  num: string;
  title: string;
  desc: string;
  arrowLabel: string;
  href: string;
  Icon: () => ReactElement;
}

const CARDS: WayfindingCard[] = [
  {
    num: "01",
    title: "The Diagnostic",
    desc: "Answer questions. Get a precise read of your organization's real friction points.",
    arrowLabel: "Begin →",
    href: "/diagnostic",
    Icon: DiagnosticIcon,
  },
  {
    num: "02",
    title: "The Book",
    desc: "The research and thinking establishing the intellectual foundation of our work.",
    arrowLabel: "Read →",
    href: "/book/toc",
    Icon: BookIcon,
  },
  {
    num: "03",
    title: "Services",
    desc: "Resolution strategies, advisory, and how client engagements work.",
    arrowLabel: "Explore →",
    href: "/services",
    Icon: ServicesIcon,
  },
  {
    num: "04",
    title: "About",
    desc: "Who's behind this, and why the practice is built the way it is.",
    arrowLabel: "Learn more →",
    href: "/about",
    Icon: AboutIcon,
  },
];

export function WayfindingGrid() {
  const { ref, className } = useScrollReveal<HTMLDivElement>();

  return (
    <div ref={ref} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {CARDS.map((card, i) => (
        <Link
          key={card.num}
          href={card.href}
          className={`group block bg-(--home-field-raise) p-6 hover:opacity-90 transition-opacity ${className}`}
          style={className ? { animationDelay: `${i * 80}ms` } : undefined}
        >
          <div className="flex items-start justify-between mb-4">
            <span className="font-mono text-xs text-(--home-slate) tracking-wide">{card.num}</span>
            <span className="text-(--home-slate)">
              <card.Icon />
            </span>
          </div>
          <h3 className="font-display text-lg font-semibold text-charcoal mb-2">{card.title}</h3>
          <p className="font-ui text-sm text-charcoal opacity-70 mb-4">{card.desc}</p>
          <span className="font-ui text-sm font-medium text-(--home-slate) group-hover:underline">
            {card.arrowLabel}
          </span>
        </Link>
      ))}
    </div>
  );
}
