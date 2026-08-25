# `/book/toc` Visual Identity Migration — Plan Doc

Durable plan file for the last unmigrated route in the Visual Identity v3 rollout. Read this first each session this migration is active. Structural decision touching the theme system — per standing discipline, routes through Gemini architecture review before any build. **No build has started. This file currently holds re-verification results and a drafted (not sent) Gemini request only.**

---

## Re-verification against current live code (2026-08-25)

Prior findings: `prompts/book-toc-gemini-recommendations-verification.md` (2026-08-24). Per standing discipline, re-checked fresh rather than assumed still valid — a file confirmed once doesn't stay valid after real commits land.

### 1. `/book/toc/page.tsx` — still fully unmigrated, confirmed

`grep -c "useTheme" web/app/book/toc/page.tsx` → **0**. Same v1 markers as the prior pass, confirmed by direct re-read: `text-charcoal` (lines 80, 98, 206, 212, 263, 328), `bg-charcoal`/`border-charcoal` (348), bare `bg-white` (186, 309, 324), `text-gray-*`/`bg-gray-*`/`border-gray-*` throughout, bare `text-slate`/`border-slate`/`bg-slate` (198, 370-371). **Nothing has touched this file's migration status.** Last commit touching it: `54b2275` (2026-08-23, "replace hardcoded hover:text-charcoal with named --hover-ink token, 20 sites/8 files") — a hover-color token rename, unrelated to theme migration, predates even the prior verification pass. No drift.

### 2. Drawer/portal token gap — still exists exactly as described

`Drawer.Content` at line 324: `className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-2xl max-h-[80vh] flex flex-col md:hidden"` — bare `bg-white`, confirmed. Zero occurrences of `bg-[color:var(...)]` or `border-[color:var(...)]` anywhere in the file — the arbitrary-value token syntax used elsewhere on migrated pages hasn't been touched here at all. Gap confirmed live, unchanged.

### 3. `--color-slate` separation — still deliberate, still documented, `SignatureCard.tsx` still live

`web/app/globals.css` lines 22-27, confirmed present verbatim:

> "`--slate` here is intentionally NOT mirrored into the Tailwind `@theme` block below as `--color-slate` — that name is already taken by the Session 58 palette's `--color-slate` (#4A6B85), live today via `border-slate` in `SignatureCard.tsx`. Consume the new `--slate` via arbitrary-value syntax (e.g. `text-[color:var(--slate)]`) or inline style, not a bare `slate` utility class."

`--color-slate: #4A6B85` confirmed unchanged at `globals.css:144` (fixed hex, not `var(--slate)`). `SignatureCard.tsx:41` confirmed still live: `"border-slate bg-paper"` — real, active "selected card" styling. Both files' last touch is the same commit as `/book/toc`'s (`54b2275`) — nothing has moved since either was last checked. **This constrains the migration approach, not something to fix in this pass** — `/book/toc`'s bare `text-slate`/`border-slate`/`bg-slate` usage (lines 198, 370-371) resolves through the same fixed `--color-slate` value as `SignatureCard.tsx` today; any change to that behavior for `/book/toc` specifically needs a scoping decision (see the drafted request below), not an assumption either way.

**All three re-verified findings hold. No drift since 2026-08-24.**

---

## Drafted Gemini architecture review request — NOT SENT, for Pete's review

`prompts/book-toc-gemini-migration-review-request.md` will hold the sent version once approved; the draft is reproduced here for review first.

### Draft

---

**Architecture Review — `/book/toc` Visual Identity Migration (last unmigrated route, v3 rollout)**

**Context.** The Visual Identity v3 token pattern (`useTheme()` from `@/components/ThemeSwitcher`, `data-theme`-driven Warm/Dark/Neutral palettes, arbitrary-value consumption of CSS custom properties like `bg-[color:var(--field)]`/`border-[color:var(--line)]`) is already shipped and proven across `/about/*`, `/ask`, the `/book` hub, and all 87 piece pages. `/book/toc` is the last unmigrated route in this rollout — confirmed fresh today (zero `useTheme()`, same v1 markers as when last checked). This request scopes the migration itself before any build.

**Scope to cover:**
1. Applying `useTheme()` and the established token pattern to the page's dimension/signature filter chips (currently `text-charcoal`/`text-gray-*` throughout).
2. `resolution_family` badges and media-link states (currently bare `text-charcoal`, `hover:text-hover-ink`, bare `bg-white` containers).
3. The Drawer/portal component specifically — confirmed today to have zero `bg-[color:var(...)]`/`border-[color:var(...)]` wiring anywhere; the mobile Terminology Guide `Drawer.Content` is bare `bg-white` with no theme-reactive field/line tokens at all. This needs the same wiring the rest of the page gets, in the same pass — not deferred, since an unmigrated Drawer inside an otherwise-migrated page is exactly the kind of half-themed surface this rollout has been designed to avoid.

**Scoping question — not a request to assume the answer:**

`/book/toc`'s dimension-tag chips (lines 198, 370-371) currently use bare `text-slate`/`border-slate`/`bg-slate`, which resolve through `--color-slate: #4A6B85` — a fixed, non-theme-reactive value, deliberately kept separate from the real per-theme `--slate` token (documented in `globals.css`, lines 22-27) specifically so introducing the new token would never silently change `SignatureCard.tsx`'s live "selected card" styling, which still depends on the old bare-`slate` behavior today.

Two real options for `/book/toc`'s chips specifically:

- **(a) Leave them on the old fixed `--color-slate` value**, matching `SignatureCard.tsx`'s existing precedent. Simplest, no new work, but these specific chips would stay non-theme-reactive even after the rest of the page migrates — a small, deliberate exception inside an otherwise fully-migrated page.
- **(b) Migrate these specific chips to the documented arbitrary-value syntax** (`text-[color:var(--slate)]`, etc.), matching the rest of the page's migration and giving genuine theme-awareness. Small additional scope, but introduces the first real consumer of the "new" `--slate` token via arbitrary-value syntax anywhere on the site, which is exactly the usage pattern the `globals.css` comment already anticipated and named as the correct way to consume it.

**Which of these is the right call for this migration, and why?** Not asking for a default — genuinely undecided, flagged here as a scoping decision for review, not something to assume before this migration starts.

**Not asked here:** no build plan, no component-level implementation detail, no recommendation on sequencing against other open work. Scope and the slate question only.

---

## Not done yet

No Gemini submission sent. No build started. No file touched beyond this new plan doc. Awaiting Pete's review of the drafted request above before it goes out.
