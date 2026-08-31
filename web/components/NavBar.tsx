"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { ThemeSwitcher } from "@/components/ThemeSwitcher";

export function NavBar() {
  const [aboutOpen, setAboutOpen] = useState(false);
  const aboutRef = useRef<HTMLDivElement>(null);

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
    <nav className="flex justify-between items-center px-6 py-4 border-b border-line bg-field">
      <Link
        href="/"
        className="font-ui text-sm font-semibold text-ink hover:text-(--slate) transition-colors"
      >
        Principal Resolution
      </Link>
      <div className="flex items-center gap-6">
        <Link
          href="/book"
          className="font-ui text-sm text-(--slate) hover:text-ink transition-colors"
        >
          The Book
        </Link>
        <div
          ref={aboutRef}
          className="relative flex items-center gap-1"
          onMouseEnter={() => setAboutOpen(true)}
          onMouseLeave={() => setAboutOpen(false)}
        >
          <Link
            href="/about"
            className="font-ui text-sm text-(--slate) hover:text-ink transition-colors"
          >
            About
          </Link>
          <button
            type="button"
            className="text-(--slate) hover:text-ink transition-colors p-1"
            aria-haspopup="true"
            aria-expanded={aboutOpen}
            aria-label="Toggle About menu"
            onClick={() => setAboutOpen((o) => !o)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                setAboutOpen((o) => !o);
              }
              if (e.key === "Escape") setAboutOpen(false);
            }}
          >
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden="true">
              <path
                d="M2 3.5L5 6.5L8 3.5"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          {aboutOpen && (
            <div className="absolute right-0 top-full pt-2 z-50">
              <div className="bg-field border border-line py-2 min-w-[160px]">
                <Link
                  href="/about/story"
                  className="block px-4 py-2 font-ui text-sm text-(--slate) hover:text-ink hover:bg-field-raise transition-colors"
                  onClick={() => setAboutOpen(false)}
                >
                  The Story
                </Link>
                <Link
                  href="/about/services"
                  className="block px-4 py-2 font-ui text-sm text-(--slate) hover:text-ink hover:bg-field-raise transition-colors"
                  onClick={() => setAboutOpen(false)}
                >
                  The Services
                </Link>
                <Link
                  href="/about/method"
                  className="block px-4 py-2 font-ui text-sm text-(--slate) hover:text-ink hover:bg-field-raise transition-colors"
                  onClick={() => setAboutOpen(false)}
                >
                  The Method
                </Link>
              </div>
            </div>
          )}
        </div>
        <ThemeSwitcher />
      </div>
    </nav>
  );
}
