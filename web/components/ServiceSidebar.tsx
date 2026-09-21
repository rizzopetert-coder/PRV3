"use client";

import { useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

// ---------------------------------------------------------------------------
// Persistent service sidebar (this session, Gemini-cleared architecture:
// see tools/_mob.txt). Layout-level, mounted in web/app/layout.tsx wrapping
// {children} directly -- takes over the flex-row/flex-column wiring itself
// rather than layout.tsx hardcoding one shape, since the two modes below
// need genuinely different structure, not just a different sidebar child.
//
// Suppressed on /diagnostic: that route already has two right-side panels
// of its own (AssemblyPanel.tsx, a sticky w-72 aside; StateDrawer.tsx, a
// fixed w-80 drawer), both of which also become Vaul bottom sheets on
// mobile -- a third persistent right column there would fight both for
// space and z-index. The diagnostic is also a deliberately private,
// reflective experience; a persistent sales/service nav on screen while
// someone answers vulnerable questions undermines that, independent of
// the layout math. Collapses to a small top-nav trigger there instead of
// returning null outright, so the four services stay one click away.
//
// The trigger is a thin, full-width, in-flow strip directly below NavBar
// -- NOT a `fixed` floating chip. A `fixed` version was tried first and
// rejected after live verification: AssemblyPanel is `sticky top-0
// h-screen` at the right edge starting immediately below NavBar with no
// gap, so any fixed top-right element beyond NavBar's own height visibly
// overlapped AssemblyPanel's heading the moment Phase 2+ rendered
// (confirmed live in the browser preview, not assumed). Rendering the
// trigger in normal flow, pushing diagnostic content down by one thin
// strip instead of floating over it, removes the collision entirely by
// construction rather than by picking a luckier pixel offset.
//
// First Call's section carries a permanent bg-rust fill -- a deliberate,
// Pete-approved exception to --color-rust's standing reservation for
// genuine Endemic-severity signaling in the live diagnostic output
// (ConstellationField.tsx, PrivateOutput.tsx, ShareableOutput.tsx all
// still enforce that reservation unchanged; this sidebar is the first and
// only place bg-rust is used as a background fill anywhere in this
// codebase, confirmed via direct grep before building this).
// ---------------------------------------------------------------------------

interface ServiceLink {
  id: string;
  name: string;
  teaser: string;
  cta: string;
  href: string;
  rust?: boolean;
}

// Display names match engine/resolution_families.py's ENGINE_TO_COMMERCIAL_NAME
// exactly (this session's commercial-name correction) -- Pete's explicit
// decision to unify the sidebar/landing-page labels with the engine's
// commercial names rather than let the two naming schemes diverge.
const SERVICES: ServiceLink[] = [
  {
    id: "people-tactics-and-strategy",
    name: "People Tactics & Strategy",
    teaser:
      "We find the organizational conditions producing your problems and resolve them at the structure, not just the symptom.",
    cta: "Begin →",
    href: "/people-tactics-and-strategy",
  },
  {
    id: "training-and-development",
    name: "Training & Development",
    teaser:
      "Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.",
    cta: "Learn more →",
    href: "/training-and-development",
  },
  {
    id: "first-call",
    name: "First Call",
    teaser:
      "Something happened today, and you need someone who has handled it before. Reach out. You will hear back the same day.",
    cta: "Get help now →",
    href: "/first-call",
    rust: true,
  },
  {
    id: "executive-advisory",
    name: "Executive Advisory",
    teaser:
      "A standing relationship, built over time. When the hardest decisions arrive, you have someone who already understands your organization instead of starting from scratch.",
    cta: "Set it up →",
    href: "/executive-advisory",
  },
];

function ServiceDropdownLinks({ onNavigate }: { onNavigate: () => void }) {
  return (
    <>
      {SERVICES.map((s) => (
        <Link
          key={s.id}
          href={s.href}
          onClick={onNavigate}
          className={`block px-4 py-2 font-ui text-sm transition-colors ${
            s.rust
              ? "bg-rust text-white hover:opacity-90"
              : "text-(--slate) hover:text-ink hover:bg-field-raise"
          }`}
        >
          {s.name}
        </Link>
      ))}
    </>
  );
}

export function ServiceSidebar({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const isDiagnostic = pathname.startsWith("/diagnostic");

  if (isDiagnostic) {
    return (
      <div className="flex flex-col flex-1 min-h-0">
        <div className="relative border-b border-line bg-field shrink-0 z-40">
          <div className="flex justify-start px-6 py-1.5">
            <button
              type="button"
              onClick={() => setIsOpen((o) => !o)}
              aria-haspopup="true"
              aria-expanded={isOpen}
              aria-label="Services"
              className="font-ui text-xs uppercase tracking-wide text-(--slate) hover:text-ink transition-colors px-2 py-1"
            >
              Services
            </button>
          </div>
          {isOpen && (
            <div className="absolute left-6 top-full bg-field border border-line py-1 min-w-[200px] shadow-sm z-50">
              <ServiceDropdownLinks onNavigate={() => setIsOpen(false)} />
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0 min-h-0">{children}</div>
      </div>
    );
  }

  return (
    <div className="flex flex-1">
      <aside className="hidden md:flex md:flex-col w-72 shrink-0 border-r border-line bg-field sticky top-0 h-screen">
        {SERVICES.map((s) => (
          <Link
            key={s.id}
            href={s.href}
            className={`flex-1 flex flex-col justify-center px-6 py-6 border-b-8 border-field last:border-b-0 transition-colors ${
              s.rust ? "bg-rust text-white hover:opacity-90" : "text-(--slate) hover:bg-field-raise hover:text-ink"
            }`}
          >
            <h2 className="font-display text-lg font-semibold mb-2">{s.name}</h2>
            <p className={`font-ui text-sm leading-relaxed mb-3 ${s.rust ? "" : "opacity-80"}`}>
              {s.teaser}
            </p>
            <span className="font-ui text-sm font-medium">{s.cta}</span>
          </Link>
        ))}
      </aside>
      <div className="flex-1 min-w-0">{children}</div>
    </div>
  );
}
