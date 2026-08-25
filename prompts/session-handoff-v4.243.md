# PRV3 Session Handoff — MOB v4.243

Direct extract/reformatting of the 2026-08-25 Section 16 closeout entry (continued) in `tools/_mob.txt`. Not independently authored — if this ever appears to contradict Section 16, Section 16 is authoritative.

This is a continuation of the same session as `prompts/session-handoff-v4.242.md` — Pete's own live visual check of the `/book/toc` migration surfaced a real, pre-existing structural gap after that closeout had already committed.

## What this continuation covered

**Global page canvas never became theme-reactive across the Visual Identity v3 rollout — a real correction to standing "shipped" claims, not a new bug.** Pete ran the first real visual Dark/Neutral theme-toggle check this rollout has ever had, on `/about`, and found the page background doesn't change between themes at all. Confirmed directly against source: `web/app/globals.css` line 279-280, `body { background: var(--background); color: var(--foreground); }` — and `--background`/`--foreground` are defined once in the bare `:root` block, never redefined under `[data-theme="dark"]` or `[data-theme="neutral"]`, unlike every other themed token. The `data-theme` mechanism itself works correctly (text/link colors did shift in Pete's screenshots); the gap is specifically that the page canvas was never wired to a theme-reactive token by any prior session's work — affects `/about/*`, `/ask`, and all of `/book`, not just one page. Logged as its own Decision Register row (Section 13a), not fixed — `globals.css` and the `body` rule untouched, gated on a Gemini architecture review before any build.

**`/book/toc`'s own migrated surfaces re-verified against the corrected expectation — all clean.** State cards, the Drawer sheet, and the desktop terms panel recolor via their own `bg-field`; active chips via `bg-ink`/`text-cta-text`. Computed WCAG contrast: `text-oxide-text` on `bg-field` — 5.42:1 (Warm), 5.93:1 (Dark), 7.23:1 (Neutral), all AA. `text-cta-text` on `bg-ink` — 14.56:1 (Warm), 15.17:1 (Dark), 11.82:1 (Neutral), AAA in all three.

**Real, concrete downstream consequence found while running this check, folded into the same Decision Register row.** Resting (unselected) filter chips have no background of their own and sit directly on the still-fixed page canvas. Computed contrast for their text against the real fixed canvas (`#F6F3ED`): 6.05:1 (Warm, pass), **2.78:1 (Dark, FAILS WCAG AA)**, 6.53:1 (Neutral, pass). **This is a live accessibility failure in production today, not a hypothetical** — and very likely not unique to `/book/toc`: `BookPieceContent.tsx`'s teaser/body text uses the identical `text-oxide-text`-on-unstyled-canvas convention across all 87 published `/book` pieces, exposed the same way since Dark/Neutral shipped there. Flagged as possibly warranting faster turnaround than the typical structural-review cadence — sequencing is Pete's call.

No fix attempted anywhere in this arc — confirmed, quantified, and logged only, per Pete's explicit instruction at every step.

## Status at close

`/book/toc`'s own migration remains closed and correctly verified — nothing about it was wrong. The newly-discovered `--background`/`--foreground` gap is a separate, pre-existing, sitewide issue this check surfaced, now tracked as its own Decision Register item with a confirmed live accessibility impact, not just a theoretical risk.

## Open — updated this continuation

1. **Global page canvas never theme-reactive (`--background`/`--foreground`)** — new this continuation. Confirmed sitewide (`/about/*`, `/ask`, all of `/book`). Blocked on Gemini architecture review before any build. Confirmed live WCAG AA failure in Dark theme for `text-oxide-text` on unstyled canvas (2.78:1) — likely present on all 87 published `/book` pieces via `BookPieceContent.tsx`. Pete's call on whether this warrants expedited review sequencing.
2. All items carried from `session-handoff-v4.242.md` remain open and unchanged by this continuation (MemPalace migration completion, MemPalace root cause, `/book/toc`'s deferred slate-token question, Engagement Agreement, transaction path, Preview environment, Deployment Protection).

## Closed this continuation

Nothing new closed — this continuation is a finding-and-logging pass, not a build.

## Files to attach next session

- Always: `tools/_mob.txt` (current version, v4.243).
- **If picking up the `--background`/`--foreground` gap:** `web/app/globals.css` (lines 1-135, 279-280), this Decision Register row (Section 13a, `tools/_mob.txt`).
- **If checking whether the Dark-theme WCAG failure extends beyond `/book/toc`:** `web/components/BookPieceContent.tsx`, and spot-check a live `/book` piece page in Dark theme.
- All other files-to-attach guidance from `session-handoff-v4.242.md` still applies unchanged.
