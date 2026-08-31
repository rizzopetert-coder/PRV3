"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";

// Visual identity v2 theme switcher (OD-07). Icon button + popover —
// redesigned from the original always-visible 3-tab row (Warm/Dark/
// Neutral, underline on active) after that row shipped as a full-width
// band competing with page content. Underlying mechanism is unchanged
// from that original build: same data-theme attribute on
// document.documentElement, same localStorage key, same
// useSyncExternalStore wiring below. Only the trigger/popover shell
// around it is new.
//
// No existing theme-persistence pattern in this repo (no next-themes or
// similar, confirmed before building this) — hand-rolled, localStorage
// key "prv3-theme", matching the anti-flash blocking script in
// app/layout.tsx that reads the same key before first paint and applies
// data-theme to <html> directly (before this component even mounts).
// This component only reflects that state in the UI and applies changes
// on user interaction — useSyncExternalStore subscribing to localStorage,
// not useEffect+setState (avoids both the SSR/hydration mismatch and the
// react-hooks/set-state-in-effect lint rule this repo enforces).
//
// Mounted sitewide in NavBar.tsx (global chrome) as of this pass — no
// longer /about/*-scoped. The popover reuses NavBar's own existing
// About-dropdown pattern (useRef + mousedown-outside listener). Both now
// run on the reactive --field/--line/--ink/--slate tokens (global chrome
// migration, Gemini-reviewed, two rounds), not the flat bg-white/
// border-gray-100 treatment this comment used to describe.

export type ThemeName = "warm" | "dark" | "neutral";

const THEME_STORAGE_KEY = "prv3-theme";

const THEMES: { value: ThemeName; label: string }[] = [
  { value: "warm", label: "Warm" },
  { value: "dark", label: "Dark" },
  { value: "neutral", label: "Neutral" },
];

function applyTheme(theme: ThemeName): void {
  if (theme === "warm") {
    document.documentElement.removeAttribute("data-theme");
  } else {
    document.documentElement.setAttribute("data-theme", theme);
  }
}

function readTheme(): ThemeName {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === "dark" || stored === "neutral") return stored;
  } catch {
    // localStorage unavailable — fall through to the warm default.
  }
  return "warm";
}

// getServerSnapshot always returns "warm" (the server has no localStorage)
// — React uses this for SSR and the initial client hydration pass to
// guarantee a match, then re-renders with the real readTheme() value
// immediately after, with no manual mounted-flag bookkeeping needed.
function getServerSnapshot(): ThemeName {
  return "warm";
}

const listeners = new Set<() => void>();

function subscribe(onStoreChange: () => void): () => void {
  listeners.add(onStoreChange);
  return () => listeners.delete(onStoreChange);
}

function selectTheme(next: ThemeName): void {
  applyTheme(next);
  try {
    localStorage.setItem(THEME_STORAGE_KEY, next);
  } catch {
    // localStorage unavailable — selection still applies for this load,
    // just won't persist across sessions.
  }
  listeners.forEach((listener) => listener());
}

// Reusable reactive theme read, exported so other components can render
// theme-conditional content without duplicating the useSyncExternalStore
// wiring above -- first consumer: /about/services (Dark/Neutral pilot,
// this session), since role-specific token names (e.g. Warm's dusk-blue,
// Dark's amber) don't share a cross-theme CSS variable name the way
// oxide/oxide-text do, so picking the right Tailwind class per role
// requires knowing the live theme, not just a CSS cascade.
export function useTheme(): ThemeName {
  return useSyncExternalStore(subscribe, readTheme, getServerSnapshot);
}

export function ThemeSwitcher() {
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  return (
    <div ref={ref} className="relative flex items-center">
      <button
        type="button"
        className="text-(--slate) hover:text-ink transition-colors p-1.5"
        aria-haspopup="true"
        aria-expanded={open}
        aria-label="Change theme"
        onClick={() => setOpen((o) => !o)}
        onKeyDown={(e) => {
          if (e.key === "Escape") setOpen(false);
        }}
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="8" cy="8" r="6.25" stroke="currentColor" strokeWidth="1.5" />
          <path d="M8 1.75a6.25 6.25 0 0 1 0 12.5z" fill="currentColor" />
        </svg>
      </button>
      {open && (
        <div className="absolute right-0 top-full pt-2 z-50">
          <div
            role="radiogroup"
            aria-label="Theme"
            className="bg-field border border-line py-2 min-w-30"
          >
            {THEMES.map(({ value, label }) => {
              const active = theme === value;
              return (
                <button
                  key={value}
                  type="button"
                  role="radio"
                  aria-checked={active}
                  onClick={() => {
                    selectTheme(value);
                    setOpen(false);
                  }}
                  className={`flex items-center gap-2 w-full px-4 py-2 font-ui text-sm transition-colors ${
                    active ? "text-oxide-text" : "text-(--slate) hover:text-ink hover:bg-field-raise"
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${active ? "bg-oxide-text" : "bg-transparent"}`}
                    aria-hidden="true"
                  />
                  {label}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
