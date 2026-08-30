"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";

// Homepage restructure (this session) -- kept homepage-local per P-12 scope
// discipline, not promoted to a shared web/lib/hooks/ location. No second
// consumer exists yet.
//
// isMounted and prefersReducedMotion both via useSyncExternalStore, not
// useEffect+setState, matching this repo's existing hydration-safe pattern
// (see ThemeSwitcher.tsx) -- avoids both the SSR/hydration mismatch and the
// react-hooks/set-state-in-effect lint rule this repo enforces. Neither
// subscribe function needs to notify for isMounted (the snapshot never
// changes again after the client's first render); the reduced-motion one
// does, via matchMedia's own change event, in case the OS preference flips
// mid-session.

function subscribeMounted(): () => void {
  return () => {};
}
function getMountedSnapshot(): boolean {
  return true;
}
function getMountedServerSnapshot(): boolean {
  return false;
}

function subscribeReducedMotion(onChange: () => void): () => void {
  const mql = window.matchMedia("(prefers-reduced-motion: reduce)");
  mql.addEventListener("change", onChange);
  return () => mql.removeEventListener("change", onChange);
}
function getReducedMotionSnapshot(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
function getReducedMotionServerSnapshot(): boolean {
  return false;
}

// !mounted branch (see className below): content renders fully visible
// before hydration and for the brief window before mount, rather than
// starting hidden -- avoids a permanently-invisible section for any
// visitor whose JS never runs (no-JS, a JS error, a crawler). Standard
// tradeoff for IntersectionObserver-driven reveals (the same one AOS,
// Framer's whileInView, etc. all make) -- a few-ms visible-then-hide-then-
// reveal blip on a normal load, not permanent invisibility on a broken one.
export function useScrollReveal<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const mounted = useSyncExternalStore(subscribeMounted, getMountedSnapshot, getMountedServerSnapshot);
  const prefersReducedMotion = useSyncExternalStore(
    subscribeReducedMotion,
    getReducedMotionSnapshot,
    getReducedMotionServerSnapshot,
  );
  const [observedRevealed, setObservedRevealed] = useState(false);

  useEffect(() => {
    if (prefersReducedMotion) return;
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setObservedRevealed(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [prefersReducedMotion]);

  const revealed = prefersReducedMotion || observedRevealed;
  const className = !mounted ? "" : revealed ? "animate-fade-up-gated" : "opacity-0";
  return { ref, className };
}
