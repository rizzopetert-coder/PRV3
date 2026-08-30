# Homepage Restructure — Build Plan

Status: ready for review. No code written yet. Architecture verified against
live source (see the 7-part Gemini claim-verification report, this session);
copy is Pete's final approved text, provided verbatim, this session.

## Scope recap (locked, not re-litigated here)

- Palette: Option A, strict local scope — new tokens apply only inside the
  homepage's own wrapper, never touch `globals.css`'s flat `--color-slate`/
  `--color-paper`/`--color-charcoal`/`--color-rust` (confirmed: `--color-slate`
  is literally the render color for every non-Endemic severity badge via
  `ConstellationField.tsx`'s `severityAccentTokens()` — a global change would
  silently recolor live client diagnostic output).
- `/services` → `/about/services` via a new `next.config.ts` rewrite (none
  exists today — net-new block, not an extension).
- Diagnostic entry unchanged: homepage links straight to `/diagnostic`
  (mounts the existing `DiagnosticGate` → Phase 0 flow, untouched).
- `ConstellationField mode="ambient"` reused directly, unmodified — confirmed
  zero-parameter, self-contained, no data-shape risk.
- Mobile menu is new construction (nothing like it exists today), built as a
  shared component since `NavBar.tsx` is global chrome.
- Wayfinding grid built homepage-local (`web/components/home/`), not a
  universal card system, per P-12 scope discipline.
- Scroll-reveal reuses the existing `fade-up` keyframe but gets real
  `prefers-reduced-motion` gating — confirmed today's `.animate-fade-up` has
  none, and is a live, in-use class (`web/app/diagnostic/page.tsx`), so this
  build adds a new gated class rather than touching that one.

## Nav-scope decision (resolved, 2026-08-29)

Reading 2, not reading 1. `NavBar.tsx` is **out of scope for this task, full
stop** — the real global nav (Book + About dropdown with Story/Services/
Method, `aboutOpen`/`aboutRef` state machine, click-outside handler) stays
exactly as it is today, unmodified, on every page including the homepage.
No Diagnostic link, no Begin CTA, no dropdown removal in global nav.

MobileMenu.tsx still gets built — a real, current gap regardless of this
project — but now mirrors what the real global nav actually offers, not the
four-link mockup set. See the revised MobileMenu.tsx section below.

The homepage's own page-level content (hero, wayfinding grid with its own
Diagnostic/Book/Services/About cards, closer CTA) is unaffected — that's
page content, not global chrome.

### Mechanical consequence: how MobileMenu gets triggered without touching NavBar.tsx
No hamburger button can be added inside `NavBar.tsx`'s own markup under this
constraint. `MobileMenu.tsx` is built as a fully self-contained component —
it renders its own fixed-position, `md:hidden` trigger button *and* the
overlay drawer — and gets mounted as a sibling to `<NavBar />` in
`web/app/layout.tsx` (the shared root layout, not `NavBar.tsx` itself):
```tsx
<NavBar />
<MobileMenu />
{children}
```
This is a `layout.tsx` touch, not a `NavBar.tsx` touch — added to the file
list below. Trigger button is positioned to visually sit where a hamburger
normally would (`fixed top-4 right-6 z-50 md:hidden`), styled with the same
existing global tokens `NavBar.tsx` already uses. If the visual-verification
pass shows it overlapping `NavBar.tsx`'s own content awkwardly at any
breakpoint, I'll adjust positioning then — flagging now that this is a
workaround for the "don't touch NavBar.tsx" constraint, not the ideal
long-term home for a hamburger trigger.

## File-by-file plan

### 1. `web/next.config.ts` — modify
Add the rewrite block (verified against the real Next 16.2.9 `rewrites()`
API in `node_modules/next/dist/docs`, no breaking changes found):
```ts
async rewrites() {
  return [
    { source: "/services", destination: "/about/services" },
  ];
},
```

### 2. `web/app/globals.css` — modify, additive only
- New scoped palette block, own rule (not inside `:root`, so it only applies
  under `.home-scope`):
  ```css
  .home-scope {
    --home-paper: #F1F3F1;
    --home-field-raise: #E6E9E7;
    --home-slate: #2458A4;
  }
  ```
  Using `--home-*` names rather than bare `--paper`/`--slate` is a deliberate
  choice, not what you specified literally — bare `--slate` on a wrapper
  would shadow the real v2 `--slate` token (`#5C6B66` at `:root`, different
  value) for any descendant that ever consumes it, and "isolation is not
  optional" per your instruction reads as ruling that out even though
  nothing inside the homepage tree consumes v2 `--slate` today. Say if you'd
  rather I use the bare names — implementation detail, your call either way.
- New gated scroll-reveal utility, additive, doesn't touch the existing bare
  `.animate-fade-up` (leaves `diagnostic/page.tsx`'s live usage untouched):
  ```css
  @media (prefers-reduced-motion: no-preference) {
    .animate-fade-up-gated {
      animation: fade-up 300ms ease-out both;
    }
  }
  ```

### 3. `web/components/MobileMenu.tsx` — new, shared, self-contained component
Renders its own trigger button (fixed, `md:hidden`) plus a full-screen
overlay drawer, large tap targets, close button. Link set mirrors what the
real global nav actually offers, not the original four-link mockup set —
resolved per the nav-scope decision above:
- Diagnostic (`/diagnostic`) — real, current gap in mobile nav today,
  unrelated to the dropdown question, worth fixing regardless.
- The Book (`/book/toc`)
- Services (`/services`) — included as its own entry, not folded into
  "About." A flat About link goes to `/about`, a different page than
  `/about/services` — "About covers it" isn't actually true (they're
  sibling routes, not sections of one page), so omitting Services would
  make it genuinely unreachable from mobile nav, not just redundant.
- About (`/about`) — flat link, not a replica of the desktop dropdown.
  Standard mobile pattern for a desktop hover dropdown: link to the parent
  page, let it surface Story/Services/Method from there.

No Begin CTA — that was never a real ask for global nav, only the
homepage's own hero/closer sections carry that CTA. Styled with the
*existing* global tokens (charcoal/white/gray-100), not the homepage-local
palette — this is sitewide chrome, it shouldn't carry the homepage's own
accent color.

### 4. `web/app/layout.tsx` — modify (new to this plan, not `NavBar.tsx`)
Mount `<MobileMenu />` as a sibling to `<NavBar />`, per the mechanical
consequence noted above. One-line addition, no other change.

### 5. `web/components/home/useScrollReveal.ts` — new hook
```ts
"use client";
import { useEffect, useRef, useState } from "react";

export function useScrollReveal<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [mounted, setMounted] = useState(false);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    setMounted(true);
    const el = ref.current;
    if (!el) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setRevealed(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setRevealed(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const className = !mounted ? "" : revealed ? "animate-fade-up-gated" : "opacity-0";
  return { ref, className };
}
```
Note on the `!mounted` branch: content renders fully visible before
hydration and for the split second before the effect runs, rather than
starting hidden — avoids a permanently-invisible section for any visitor
whose JS never runs (no-JS, JS error, crawler). Standard tradeoff for
IntersectionObserver-driven reveals; the visible-then-hide-then-reveal blip
on a normal load is a few ms and matches how this pattern works everywhere
it's used (AOS, Framer's `whileInView`, etc.).

Kept homepage-local per P-12, not promoted to a shared `web/lib/hooks/` —
no second consumer exists yet.

### 6. `web/components/home/WayfindingGrid.tsx` — new component
Four cards, numbered 01–04, hand-rolled inline SVG line icons (`currentColor`
stroke, matching `NavBar.tsx`'s existing caret-icon convention — no icon
library in `package.json`, not introducing one for four icons):
1. Diagnostic → `/diagnostic` — magnifying glass (circle + diagonal handle)
2. The Book → `/book/toc` — open book (two facing angled polylines)
3. Services → `/services` — compass/radiating-lines mark (circle + short
   radiating lines)
4. About → `/about` — person silhouette (circle head + shoulder arc)

Card copy exactly as provided. Cards styled `bg-(--home-field-raise)`,
accent/arrow-label `text-(--home-slate)` — matching the existing
`bg-(--slate)`/`border-(--slate)` arbitrary-value convention already live in
`web/app/book/toc/page.tsx:590-591`.

### 7. `web/app/page.tsx` — full rewrite
Structure, top to bottom:
- `<main className="home-scope bg-(--home-paper) ...">` wrapper — scopes the
  local palette.
- **Hero**: eyebrow ("PRINCIPAL RESOLUTION"), H1 with `<em>` around
  "structural" only, 8-tag row, hero sub paragraph. Two-column layout at
  `lg:` (text left, signature field right in a `aspect-[900/640]` container
  so `ConstellationField mode="ambient"` can't overflow the text column at
  any breakpoint); stacked on mobile/tablet.
- **Signature field axis labels**: APTITUDE/AUTHORITY/ALLIANCE/ATTITUDE as
  four absolutely-positioned text labels around the `aspect-[900/640]`
  container (top/right/bottom/left) — built as a homepage-local overlay, NOT
  a change to `ConstellationField.tsx` itself. `AmbientField()` today renders
  no axis labels at all (only `LiveField` does); modifying the shared
  component to add them would be new risk on a component you explicitly
  asked to reuse "directly... no data-shape risk." The overlay achieves the
  same visual without touching it.
- **Credential band**: "58 STATES · 4 DIMENSIONS · 1 INSTRUMENT".
- **Voice/perspective section**: eyebrow ("THE PERSPECTIVE"), three
  paragraphs (para 1: `font-display` / Lora, larger; paras 2-3: `font-ui` /
  Inter, smaller), "P" initial circle + "Founder, Principal Resolution" (no
  name, per your explicit instruction to leave it out for now). Wrapped in
  `useScrollReveal`.
- **Wayfinding**: header "WHERE TO GO FROM HERE" + `<WayfindingGrid />`,
  wrapped in `useScrollReveal` (staggered per-card via a small index-based
  delay, CSS `animation-delay`, not a second hook instance per card).
- **Closer**: H2 "Give the Diagnostic a try.", sub, CTA button → `/diagnostic`.
- **Footer**: "Principal Resolution." (unchanged from today).

All copy exactly as provided — no paraphrasing.

## Verification (before this is marked done)

- `tsc --noEmit`, full `vitest run`.
- `next.config.ts` rewrite is a new URL-to-destination mapping — qualifies
  for the standing live-production-round-trip rule (locked 2026-08-27).
  Since push is being held separately this session per your instruction,
  **the live-prod round trip on `/services` can't run until after a future
  push + deploy** — I'll flag this as an open verification item at closeout
  rather than claim it done prematurely.
- Visual check across breakpoints (375 / 768 / 1440) via local dev server —
  Playwright is already a devDependency, I'll use it for the actual
  screenshots rather than describing the layout unverified.
- Confirm `prefers-reduced-motion: reduce` genuinely suppresses the new
  reveal animation (both the CSS media-query gate and the JS `matchMedia`
  check in `useScrollReveal`).

## Commits (grouped, not one giant commit)

1. `next.config.ts` rewrite
2. `globals.css` additions (scoped palette + gated reveal utility)
3. `MobileMenu.tsx` + `layout.tsx` (mount only — `NavBar.tsx` untouched)
4. `home/useScrollReveal.ts` + `home/WayfindingGrid.tsx`
5. `page.tsx` rewrite
6. MOB update (Decision Register entry for the restructure + the scoped-
   palette decision + the NavBar-out-of-scope correction), own commit,
   version bump

Push held separately per your instruction — will report the full diff and
wait for explicit go-ahead before any commit, and hold push even after
commit approval until you say so.
