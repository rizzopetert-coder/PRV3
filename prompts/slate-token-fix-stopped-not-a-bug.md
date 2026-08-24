# `--color-slate` "Fix" — Stopped Before Writing. It Was Never a Bug.

Date: 2026-08-24. This task was dispatched to fix a "hardcoding bug" this session itself had identified during the Visual Identity Phase 3/Gemini reconciliation. Direct inspection before writing the change found the premise was wrong — the fix is not made, nothing is committed, nothing is pushed.

## What the blast-radius grep found — 4 sites, not more

```
web/app/book/toc/page.tsx:198   text-slate border border-slate     (signature tag badge)
web/app/book/toc/page.tsx:370   border-slate bg-slate text-paper   (signature filter, active state)
web/app/book/toc/page.tsx:371   hover:border-slate                 (signature filter, inactive hover)
web/components/SignatureCard.tsx:41   border-slate bg-paper        (selected-card state, self-selection flow)
```

Small blast radius by file count — but reading the actual context of one of these sites changed the whole finding.

## The comment that was missed the first time — `web/app/globals.css` lines 22-27

```css
/* --slate here is intentionally NOT mirrored into the Tailwind @theme
 * block below as --color-slate — that name is already taken by the
 * Session 58 palette's --color-slate (#4A6B85), live today via
 * `border-slate` in SignatureCard.tsx. Consume the new --slate via
 * arbitrary-value syntax (e.g. text-[color:var(--slate)]) or inline
 * style, not a bare `slate` utility class.
 */
```

This is an explicit, deliberate, already-documented design decision, not an oversight: **there are two different colors, both informally called "slate," on purpose kept apart under different Tailwind exposure paths specifically so they would not collide.**

1. **Session 58's `--color-slate: #4A6B85`** — a single, non-theme-varying value, exposed as the bare `text-slate`/`bg-slate`/`border-slate` Tailwind utilities. `SignatureCard.tsx` depends on this exact value for its "selected" card styling — confirmed live, active code: real `useSelfSelection()` context, real cluster-toggle logic, not stale or dead.
2. **Visual Identity v2's `--slate`** — a newer, genuinely per-theme value (Warm `#5C6B66`, Dark `#8FA39C`, Neutral `#7A7E82`), deliberately given a *different* consumption path (`text-[color:var(--slate)]` arbitrary-value syntax, or inline style) so that introducing it would never silently change what the bare `slate` utility already meant to existing consumers.

## What this means for the requested fix

Changing `--color-slate: #4A6B85` to `--color-slate: var(--slate)` in the `@theme inline` block does exactly what the comment warns against: it collapses the two intentionally-separate tokens into one, and every consumer of the bare `slate` utility — including `SignatureCard.tsx`'s live "selected" state — would silently start rendering the *other* color instead of the one it was written for. Since `SignatureCard.tsx` has no theme-awareness of its own, it sits permanently in the base `:root` scope — this isn't a "only visible in Dark theme" edge case; it's an immediate, unconditional visual change to a real, currently-used diagnostic-flow component, the first time anyone loads it after the change ships.

**This is not a "restore correct behavior" fix. It's a real regression, exactly of the shape this task's own instructions asked to be watched for and flagged rather than assumed safe.**

## A correction to this session's own earlier work, not just a non-fix

`prompts/book-toc-gemini-recommendations-verification.md` (this session, earlier) stated the slate-token claim was "CONFIRMED ACCURATE, precisely" and characterized it as "a real, deeper token-wiring bug in `globals.css` itself." That characterization was wrong — the comment explaining why `--slate` was deliberately kept separate from `--color-slate` was present in the file at the time of that check and was missed. Gemini's original claim (which prompted that verification) described the mechanism correctly — two same-named tokens do resolve differently — but framed it as an unintentional gap rather than the deliberate, already-documented separation it actually is. Neither this session's own follow-through nor Gemini caught the comment; this pass did, only because the specific instruction here was to check for exactly this kind of "does something rely on the old behavior" risk before writing anything.

## `book/toc/page.tsx`'s own bare `slate` usage — reframed, not a separate issue

Given the above, `book/toc/page.tsx`'s bare `text-slate`/`border-slate`/`bg-slate` at lines 198/370/371 were never a broken attempt at consuming the new v2/v3 color — they're using the same Session 58 `--color-slate` value `SignatureCard.tsx` correctly uses, entirely consistent with the rest of that page's confirmed-still-v1 styling (already on record this session — `book/toc` hasn't been migrated at all). This isn't a distinct bug sitting inside an otherwise-migrated page; it's simply part of the page's overall not-yet-migrated state.

**If `book/toc` is migrated in a future pass** and Pete wants those specific signature badges to pick up the real, theme-aware slate color, the correct fix at that time is to change `book/toc/page.tsx`'s own classes from the bare utility to the documented arbitrary-value syntax (`text-[color:var(--slate)]`, `border-[color:var(--slate)]`, `bg-[color:var(--slate)]`) — matching the pattern the `globals.css` comment already specifies — not to touch the shared `--color-slate` mapping, which would collaterally break `SignatureCard.tsx`.

## Outcome

**No change made to `globals.css`. No commit. No push.** Per the explicit instruction to stop and report rather than proceed when the blast-radius check gives real reason for caution — it did.
