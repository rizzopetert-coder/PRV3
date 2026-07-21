"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeSwitcher } from "@/components/ThemeSwitcher";

// NavBar is shared across every route (mounted once in the root layout) —
// NOT homepage-specific. The Stage 4 brief scopes the theme switcher to
// "the homepage nav" while also requiring every other route stay
// untouched. Since there is no separate homepage-only nav, the switcher
// is mounted here but gated on pathname === "/" — every other route
// renders this component exactly as before (confirmed via the Stage 4
// production-build diff), only the homepage additionally shows it.
export function NavBar() {
  const [aboutOpen, setAboutOpen] = useState(false);
  const aboutRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();
  const isHomepage = pathname === "/";

  useEffect(() => {
    if (!aboutOpen) return;
    function handleClickOutside(e: MouseEvent) {
      if (aboutRef.current && !aboutRef.current.contains(e.target as Node)) {
        setAboutOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [aboutOpen]);

  return (
    <nav className="flex justify-between items-center px-6 py-4 border-b border-gray-100 bg-white">
      <Link
        href="/"
        className="font-ui text-sm font-semibold text-charcoal hover:text-gray-600 transition-colors"
      >
        Principal Resolution
      </Link>
      <div className="flex items-center gap-6">
        <Link
          href="/book"
          className="font-ui text-sm text-gray-600 hover:text-charcoal transition-colors"
        >
          The Book
        </Link>
        <div
          ref={aboutRef}
          className="relative"
          onMouseEnter={() => setAboutOpen(true)}
          onMouseLeave={() => setAboutOpen(false)}
        >
          <button
            className="font-ui text-sm text-gray-600 hover:text-charcoal transition-colors"
            aria-haspopup="true"
            aria-expanded={aboutOpen}
            onClick={() => setAboutOpen((o) => !o)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                setAboutOpen((o) => !o);
              }
              if (e.key === "Escape") setAboutOpen(false);
            }}
          >
            About
          </button>
          {aboutOpen && (
            <div className="absolute right-0 top-full pt-2 z-50">
              <div className="bg-white border border-gray-100 shadow-sm py-2 min-w-[160px]">
                <Link
                  href="/about/story"
                  className="block px-4 py-2 font-ui text-sm text-gray-600 hover:text-charcoal hover:bg-paper transition-colors"
                  onClick={() => setAboutOpen(false)}
                >
                  The Story
                </Link>
                <Link
                  href="/about/services"
                  className="block px-4 py-2 font-ui text-sm text-gray-600 hover:text-charcoal hover:bg-paper transition-colors"
                  onClick={() => setAboutOpen(false)}
                >
                  The Services
                </Link>
              </div>
            </div>
          )}
        </div>
        {isHomepage && (
          <div className="w-55">
            <ThemeSwitcher />
          </div>
        )}
      </div>
    </nav>
  );
}
