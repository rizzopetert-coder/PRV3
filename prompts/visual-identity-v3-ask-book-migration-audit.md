# Visual Identity v3 — `/ask` + `/book/*` Migration Audit

2026-08-23. Mandatory pre-migration verification gate (Gemini-cleared batch, `prompts/gemini-themeswitcher-review-verification.md`-style claim-checking, this session), run before writing any migration code, per explicit instruction. Every match of `text-charcoal`, `hover:text-charcoal`, `bg-paper`, `text-paper`, bare `gray-*` utilities, and bare `slate` utilities in each target file, categorized as an **intentional invariant** (left as-is, with why) or a **required conversion** (migrated, with the role it maps to). Four ambiguous role questions were surfaced to Pete before writing any code rather than defaulted — see the end of this file for those decisions.

Scope: `/ask`, `/book` (hub), `/book/[type]/[slug]` (87 pieces), `/book/state/[stateSlug]`, `/book/dimension/[dimensionSlug]`, `/book/pillar/[pillarSlug]`. Explicitly excluded from this pass (per the task): `/diagnostic`, `/diagnostic/condensed`, `/dev/*`, `/share/[id]`, `/book/toc`, and `/` (homepage).

## `/ask/page.tsx`

| Match | Category | Disposition |
|---|---|---|
| `text-charcoal` (h1 "Just Ask.") | Required conversion | → heading accent, per Pete's decision (see below) |
| `text-gray-500` (body paragraph) | Required conversion | → `oxide-text` (body-copy tier) |
| `bg-charcoal` + `hover:bg-gray-700` (CTA button) | Required conversion, different role entirely | → pop-color background fill + theme's own `text-cta-text`, per Pete's decision — the button's *background*, not a text-color hover state, so out of the `hover:text-charcoal` pattern this whole audit started from. First real application of the locked pop-color rule. |

No `bg-paper`/`text-paper`/`slate` matches. `<main>` carries no explicit background class at all — inherits `body`'s `--background` (`#F6F3ED`, fixed, unscoped, identical to `--color-paper`) — not itself a conversion target; no route in this rollout has migrated a background to `--field` yet.

## `/book/page.tsx` (hub)

| Match | Category | Disposition |
|---|---|---|
| `text-charcoal` (h1 "The Book") | Required conversion | → heading accent |
| `text-gray-600` (intro paragraph) | Required conversion | → `oxide-text` |
| `text-gray-400` ("Coming soon." fallback) | Required conversion | → `oxide-text`, per Pete's teaser/secondary-text decision |
| `text-charcoal` ×2 (list-item title, both voice branches) | Required conversion | → `oxide-text`, per Pete's decision (link/body role, not heading) |
| `text-gray-500` (list-item teaser) | Required conversion | → `oxide-text`, per Pete's decision |

No `bg-paper`/`text-paper`/`slate` matches. `divide-y divide-gray-100` (list dividers) not in the grep scope — structural, matches the precedent already set by `/about/story`'s identical unmigrated dividers.

## `/book/[type]/[slug]/page.tsx` (piece detail, 87 pieces)

| Match | Category | Disposition |
|---|---|---|
| `text-charcoal` ×2 (h1, both voice branches) | Required conversion | → heading accent |
| `text-gray-400` (teaser) | Required conversion | → `oxide-text` |
| `text-charcoal` (markdown `h2`) | Required conversion | → heading accent — direct match to `/about/story`'s own section-heading precedent, not separately asked |
| `text-charcoal` (markdown `h3`) | Required conversion | → heading accent, same reasoning |
| `text-gray-600` (markdown `p`) | Required conversion | → `oxide-text` |
| `border-gray-100` (markdown `hr`) | **Intentional invariant** | Structural divider, not a text-color role — matches `divide-gray-100` precedent above |
| `text-charcoal` (markdown `strong`) | Required conversion, but not to a token | Dropped entirely — inline emphasis inside a paragraph that's already `oxide-text`; now inherits via the cascade instead of carrying a separate, redundant color |
| `text-gray-600` (markdown `ol`) | Required conversion | → `oxide-text` |

No `bg-paper`/`text-paper`/`slate` matches.

## `/book/state/[stateSlug]/page.tsx`, `/book/dimension/[dimensionSlug]/page.tsx`, `/book/pillar/[pillarSlug]/page.tsx`

Structurally identical grep results across all three (h1 + optional description + pieces-list-or-"Coming soon."):

| Match | Category | Disposition |
|---|---|---|
| `text-charcoal` (h1) | Required conversion | → heading accent |
| `text-gray-600` (description, dimension/pillar only — state has none) | Required conversion | → `oxide-text` |
| `text-gray-400` ("Coming soon.") | Required conversion | → `oxide-text` |
| `text-charcoal` ×2 (list-item title, both voice branches) | Required conversion | → `oxide-text` |
| `text-gray-500` (list-item teaser) | Required conversion | → `oxide-text` |

No `bg-paper`/`text-paper`/`slate` matches in any of the three. `divide-y divide-gray-100` present in all three, same structural-invariant treatment.

## Four role-mapping decisions surfaced to Pete before writing code

None of these had a principled answer derivable from the existing `/about/*` pattern alone — that pattern never had page-level h1s (its own hub's h1 was explicitly left unmigrated), list-item titles, or a teaser/secondary-text role, and never had a filled CTA button. Asked rather than defaulted:

1. **H1 page titles** (`/ask`, `/book` hub, `/book/state|dimension|pillar` hubs, and each piece's own h1) — **migrate to heading accent color**, extending that role beyond section headings to page titles. (Diverges from `/about` hub's own h1, which stays `text-charcoal` — a prior, separate decision not reopened here.)
2. **List-item titles** (the clickable piece-title text in every list view) — **migrate to `oxide-text`** (body-copy tier), not a heading role, since the whole row is a `Link`.
3. **Teaser/secondary text** (muted gray description lines, "Coming soon." fallbacks) — **migrate to `oxide-text`**, not left neutral gray the way `/about/story`'s eyebrow labels were — a different role (real descriptive content, not a structural label).
4. **`/ask`'s CTA button** — **apply the locked pop-color rule now**, its first real use: background fill (berry/fuchsia/plum per theme), paired with each theme's own `text-cta-text` rather than a hardcoded white. Real WCAG contrast computed, not estimated, before deciding the text-color pairing: white on Dark's fuchsia is 3.72:1 (fails 4.5:1 for normal-size button text); each theme's own `--cta-text` clears 4.5:1 against its own pop color (4.9–7.04:1 across all three).

## Architecture note

`/book/[type]/[slug]`, `/book/state/[stateSlug]`, `/book/dimension/[dimensionSlug]`, and `/book/pillar/[pillarSlug]` all carry `generateStaticParams()`, which requires a Server Component — combined with each needing live theme reactivity (`useTheme()`) for the heading-accent role, each was split into a thin Server Component (`page.tsx`, keeps `generateStaticParams`/`notFound`/data lookup) rendering a new Client Component that receives the resolved data as props. `/book/state`, `/book/dimension`, and `/book/pillar` share genuinely identical rendering (h1, optional intro paragraph, pieces list or "Coming soon.") once split from their differing data-fetching logic, so they share one new component (`BookTaxonomyListContent.tsx`) rather than three near-duplicates. `/ask` and `/book` (hub) had neither `generateStaticParams` nor a `metadata` export, so both convert to Client Components directly, no split needed.

The shared role-token module (`web/lib/about-theme-tokens.ts`) was renamed to `web/lib/theme-role-tokens.ts` and its export renamed `ABOUT_HEADING_CLASS` → `HEADING_ACCENT_CLASS`, since it's no longer `/about/*`-specific — extended per the task's own instruction ("extending it rather than duplicating it"), all three pre-existing consumers (`ServicesPageContent.tsx`, `StoryPageContent.tsx`, `MethodPageContent.tsx`) updated to the new import.

## Verification

`tsc` clean, `next build` succeeds — all 87 pieces, 6 states, 4 dimensions, 5 pillars still statically generated, matching pre-migration counts exactly. Live Playwright verification (canvas pixel-color comparison, not raw `getComputedStyle` string matching — Tailwind's `color-mix()`-based utilities serialize in `oklab()`) confirmed real computed colors change correctly across all three themes on every migrated route, including the new CTA pop-color/`cta-text` pairing, and confirmed via `git status` that zero diagnostic-content component (`ConstellationField`, `PrivateOutput`, `CondensedOutput`, `ShareableOutput`) was touched.

`ThemeSwitcher`'s mount point was not moved — stays scoped to `/about/*` only (`web/app/about/layout.tsx`), per explicit instruction. Gemini's own stated transition criterion for a NavBar-level mount (`/` and all `/book/*` routes migrated, plus `/diagnostic` route-level guards) still isn't met — `/` and `/book/toc` remain unmigrated, and no `/diagnostic` guard work was done this pass.
