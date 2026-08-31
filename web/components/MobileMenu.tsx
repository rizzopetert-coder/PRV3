"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

// Homepage restructure (this session) -- real, current gap: no mobile menu
// exists anywhere in this codebase before this component. Deliberately NOT
// wired into NavBar.tsx (Pete's explicit instruction, 2026-08-29 -- the
// real global nav, including the About dropdown and its aboutOpen/aboutRef
// state machine, is out of scope for this task, full stop). Instead this
// component renders its own trigger button (fixed, md:hidden) and mounts
// as a sibling to <NavBar /> in web/app/layout.tsx.
//
// Link set mirrors what the real global nav actually offers, not the
// original four-link homepage-mockup set: Diagnostic is a genuine gap fix
// (nothing today reaches it from any nav), Services gets its own entry
// because a flat About link goes to /about, a different page than
// /about/services -- "About covers it" isn't true, they're sibling routes.
// About itself is a flat link here, not a replica of the desktop hover
// dropdown -- the standard mobile pattern for a desktop dropdown is linking
// to the parent page and letting it surface Story/Services/Method from
// there. No Begin CTA -- that was never a real ask for global nav, only the
// homepage's own hero/closer sections carry it.
const LINKS = [
  { href: "/diagnostic", label: "Diagnostic" },
  { href: "/book/toc", label: "The Book" },
  { href: "/services", label: "Services" },
  { href: "/about", label: "About" },
];

export function MobileMenu() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prevOverflow;
    };
  }, [open]);

  return (
    <>
      {/* top-20 (80px), not top-4 -- clears NavBar.tsx's own rendered
          height at every mobile width without touching that file. Measured
          live: 53px at 375-767px, 73px at 320px (wraps to two lines at
          that width) -- 80px clears both with margin. A fixed trigger
          can't read NavBar's real height at runtime without adding a
          dependency on its internals, so this is a measured constant, not
          a computed one; revisit if NavBar.tsx's own height ever changes. */}
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Open menu"
        aria-haspopup="true"
        aria-expanded={open}
        className="fixed top-20 right-6 z-50 md:hidden p-2 bg-field border border-line shadow-sm"
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
          <line x1="3" y1="6" x2="17" y2="6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="3" y1="10" x2="17" y2="10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <line x1="3" y1="14" x2="17" y2="14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      </button>

      {open && (
        <div className="fixed inset-0 z-50 bg-field md:hidden flex flex-col">
          <div className="flex justify-end p-6">
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close menu"
              className="p-2 text-ink"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <line x1="4" y1="4" x2="16" y2="16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                <line x1="16" y1="4" x2="4" y2="16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
          </div>
          <nav className="flex flex-col items-center justify-center flex-1 gap-8 px-6">
            {LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="font-display text-2xl text-ink hover:text-(--slate) transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </>
  );
}
