# Global Page Canvas (`--background`/`--foreground`) Gap — Gemini Architecture Review Request

Durable request file. Structural decision touching the base token layer every themed page depends on — per standing discipline, routes through Gemini architecture review before any build. **No build has started. No file has been touched beyond this request doc.** Full record of the finding itself: `tools/_mob.txt` Section 13a (Decision Register), commit `73bd08d`.

---

## Context

`web/app/globals.css` line 279-280:

```css
body {
  background: var(--background);
  color: var(--foreground);
}
```

`--background` (`#F6F3ED`) and `--foreground` (`#26241F`) are defined exactly once, in the bare `:root` block (`globals.css` lines 4-5), and never redefined under `[data-theme="dark"]` or `[data-theme="neutral"]`. Every other themed token — `--field`, `--ink`, `--oxide-text`, `--slate`, `--line`, `--cta-text`, and the rest — *is* properly redefined in both of those blocks. Confirmed directly against source, not assumed.

Practical effect: the page canvas (`<body>`'s own background and text color) never changes when the theme switches. Only elements that explicitly opt into a theme-reactive token (a component's own `bg-field`, `text-oxide-text`, and so on) recolor. The `data-theme` mechanism itself works correctly — confirmed via a live screenshot comparison of `/about` in Warm/Dark/Neutral, where text and link colors visibly shifted per theme while the background stayed the fixed cream color in all three.

This affects every route logged as shipped in the Visual Identity v3 rollout across multiple sessions — `/about/*`, `/ask`, all of `/book` (hub, piece pages, aggregation pages, `/book/toc`) — not one isolated page. None of those prior "shipped" sessions were wrong about the elements they actually touched; the gap is specifically that the surrounding page canvas was never part of what any of those passes wired up.

**Confirmed live consequence, not theoretical.** Computed directly from `globals.css`'s real per-theme hex values: `--oxide-text`'s Dark value (`#C9825C`) against the fixed canvas (`#F6F3ED`) computes to **2.78:1** — fails WCAG AA's 4.5:1 minimum for normal text outright. Confirmed on `/book/toc`'s resting (unselected) filter chips, which have no background of their own and sit directly on the fixed canvas. Very likely present on all 87 published `/book` pieces via `BookPieceContent.tsx`'s teaser/body text, which uses the identical `text-oxide-text`-on-unstyled-canvas convention and has since Dark/Neutral shipped there — not independently confirmed on those 87 pages specifically, flagged as a strong inference from the identical mechanism, not verified page-by-page.

A quick grep before drafting this request (not a substitute for your own verification below): `--background`/`--foreground` appear in exactly four places sitewide, all inside `globals.css` itself — the `:root` definition (lines 4-5), the `@theme inline` mapping to `--color-background`/`--color-foreground` (lines 139-140, which is what would expose `bg-background`/`text-foreground` as Tailwind utility classes), and the `body` rule (lines 279-280). No `.tsx` file anywhere references `bg-background`, `text-background`, `bg-foreground`, or `text-foreground` as a Tailwind class. This suggests the only live consumer is the `body` element via the raw CSS custom property, not the generated Tailwind utilities — but this needs your own independent verification, not reuse of this grep result as given.

---

## The structural question

Two real candidate fixes:

**(a) Redefine `--background`/`--foreground` per theme directly** — add real values for both under `[data-theme="dark"]` and `[data-theme="neutral"]`, the same pattern every other token already follows. Simplest, smallest diff. Risk: if anything in the codebase relies on `--background`/`--foreground` staying a *fixed* reference point regardless of theme (a stable "always-cream, always-charcoal" value used deliberately, not just by omission), redefining them per theme would be a real behavior change there, not just a fix.

**(b) Migrate the `body` rule to point at the already-theme-reactive `--field`/`--ink` pair instead**, and retire `--background`/`--foreground` entirely. Removes a redundant token pair rather than growing it. Bigger structural change — touches the base layer every single themed page depends on, and needs confirmation that `--field`/`--ink`'s existing values are actually correct as a full-page canvas background/foreground (they were designed and validated as component-level surface tokens — cards, panels — not necessarily audited as a whole-page canvas replacement).

**Before recommending either path: identify every real consumer of `--background`/`--foreground` specifically** (not `--field`/`--ink`, not `--color-charcoal`/`--color-paper`, not any other token in this file). Cite exact file and line for each. A wrong assumption here has sitewide blast radius, since this token pair sits under every page in the app via the global `body` rule. Do not extrapolate from the grep result in the Context section above without independently confirming it.

---

## Expedited handling question

This gap carries a confirmed live WCAG AA failure in production today, not a theoretical downstream risk — real users in Dark theme are currently seeing sub-AA contrast text on at least one shipped surface, likely more. Standing practice on this project is to route structural theme-system changes through architecture review at normal cadence, alongside whatever else is queued. **Given the confirmed live accessibility impact, should this specific review be expedited ahead of other queued structural items, or is normal cadence appropriate here?** Not asking for a default — this is Pete's sequencing call to make once your review is back, not decided in advance by this request. State your own view on urgency if you have one, but the decision itself stays with Pete.

---

## Verification requirement

Same standard as every prior architecture review on this project. Any claim about consumers, blast radius, or which fix is correct must cite the exact file and line it's grounded in — not a restatement of the mechanism in prose, not a plausible-sounding description of what the code "should" do. If a claim can't be pinned to a specific, checkable line, say so explicitly rather than presenting it with the same confidence as a verified one.

---

## Not asked here

No build plan. No component-level implementation detail. No recommendation on sequencing against other open work beyond the expedited-handling question above. Scope, consumer identification, and the choice between (a) and (b) only.
