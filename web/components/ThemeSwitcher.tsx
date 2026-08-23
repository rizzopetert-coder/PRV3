"use client";

import { useSyncExternalStore } from "react";

// Visual identity v2 theme switcher (OD-07, Stage 1). Three-way segmented
// control — Warm (default, no data-theme attribute) / Dark / Neutral.
// Active state is a 2px bottom border in --oxide-text, never
// --urgency-text and never a background-color swatch (inconsistent
// contrast across themes — already caught and fixed once per the brief).
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
// Mounted /about/*-scoped only (web/app/about/layout.tsx), per Gemini's
// cleared architecture review — see prompts/gemini-themeswitcher-review-
// verification.md (commit 1ffb3e7). Not mounted in NavBar.tsx or the
// root layout, and not on the homepage — that original Stage 1 plan was
// superseded by the review before it was ever built.

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

  return (
    <div role="radiogroup" aria-label="Theme" className="flex w-full">
      {THEMES.map(({ value, label }) => {
        const active = theme === value;
        return (
          <button
            key={value}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => selectTheme(value)}
            className={`flex-1 py-2 text-sm font-medium border-b-2 transition-colors ${
              active
                ? "border-oxide-text"
                : "border-transparent opacity-70 hover:opacity-100"
            }`}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}
