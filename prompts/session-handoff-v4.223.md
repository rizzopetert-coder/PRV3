# Session Handoff — MOB v4.223

Direct extract/reformatting of `tools/_mob.txt` Section 16's closeout entry for this session (Quarterly Step-Back on visual-identity-philosophy, through to a real shipped first palette activation), plus the companion Section 13a (Decision Register) and Section 14 (Locked Decisions Log) updates. Section 16 is authoritative — this file is a portable quick-reference copy, not an independent record.

**Real code shipped this pass** (`web/app/globals.css`, `web/app/about/services/page.tsx`, commit `76815a7`) plus a governing-principle-level decision — first session-close since the SCD-WCS Track 2 pass to include an actual code change.

## Shipped this session

- **Quarterly Step-Back conducted (Claude.ai + Pete)**: the standing craft-vs-philosophy fork resolved as a PHILOSOPHY problem, not craft. Pete confirmed directly — the restrained 3-color palette itself isn't serving as an effective differentiator for this business, independent of the multiple real craft fixes already shipped this project. Governing-principle-level decision, not a craft note.
- **`--oxide` decoupling CONFIRMED**: releases from its original severity-pairing design intent into general-content use. Pete-confirmed directly, formally resolving Gemini's stated blocking question from the OD-07-extension architecture review.
- **Full 21-color palette (7 per theme × 3 themes) approved and fully WCAG-AA contrast-verified** — real computation, formula checked against known reference values first. Three-tier usage model locked for every color: **TEXT-SAFE**, **LARGE/DECORATIVE-ONLY**, and a new **BACKGROUND-FILL-ONLY** tier (added this session for `ochre` and paper-paired muted gold — hex values unchanged, no darkening adopted). Every one of the 21 colors now has a decided role. Full record: `prompts/visual-identity-v3-palette-expansion.md`.
- **Pop-color usage rule LOCKED**: berry/fuchsia/plum per theme, exactly once per page, primary CTA only, no fallback role, never combined with another pop application on the same page.
- **First real activation SHIPPED, commit `76815a7`**: `/about/services`, Warm theme only. Wired the 6 new Warm colors into `globals.css` following the exact `--oxide` token pattern. Applied per the locked tiers: body copy → `oxide-text` (TEXT-SAFE), 4 service headings → `dusk-blue` (LARGE/DECORATIVE-ONLY), 4 italic descriptor tags → `umber` (TEXT-SAFE — **not** the decorative tier originally suggested for them, since 14px regular text isn't "large text" by the WCAG definition the tier itself is built on). `ochre`/`berry` deliberately unused — no qualifying surface existed for either, not forced in. Verified before shipping: `tsc` clean, full `next build` succeeded, and confirmed directly in compiled CSS output that the new utility classes generated real rules — not just that the build didn't crash.

## Key findings / corrections

- **Stale-baseline correction, caught mid-session**: the visual-identity-philosophy Decision Register row's own claim that "`--oxide`/v2 is live only on the homepage" was FALSE, confirmed by direct source read — zero `--oxide` references in `app/page.tsx`, a stale comment in `PrivateOutput.tsx` claimed severity-accent wiring that no longer exists, `ThemeSwitcher.tsx` confirmed never mounted anywhere, ever. Real state: the v2 token layer had zero live consumption anywhere before this session.
- **`/about` structure correction**: an earlier claim that `/about` was a "header-only stub" was stale when re-checked directly. Real structure: an orphaned 7-line shell at `/about/page.tsx` (unreachable via any NavBar link, zero `href="/about"` anywhere in the codebase) with three real content-complete children — `/about/story` (111 lines), `/about/services` (83 lines, now the palette pilot), `/about/method` (48 lines) — only two of which (`story`, `services`) are linked from NavBar's About dropdown.
- **Tier-discipline catch during the build itself**: the task suggested applying a decorative-tier color to the italic descriptor tags; declined and flagged rather than silently complied with, since those tags are small (14px) regular text, not large text by the WCAG definition the tier is built on. Used a TEXT-SAFE color there instead.

## Open / carried forward

- **Dark and Neutral theme palette activation** — colors approved and contrast-verified, but zero CSS wiring exists for either theme yet. Only Warm is wired into `globals.css`.
- **`/about/method`'s missing NavBar entry** — real content, zero nav entry. Not actioned this session.
- **`/about/page.tsx`'s orphaned-stub status** — unreachable via any UI path, still a bare shell. Not actioned this session.
- **`built_to_fail`'s own-profile-loss investigation** — the separate standing open thread from this same session's earlier Track 2 work (why it specifically beats `invisible_performance_management`'s best-case test profiles, confirmed flat across every concentration tested). Not touched this pass.
- **MemPalace `mine` reliability** — failed a second consecutive session, differently each time (a hang with zero output last close, a silent exit-code-5 failure with zero diagnostic output this close). Diary write succeeded cleanly both times regardless. Worth its own look, not a one-off — three distinct failure modes now on record across recent sessions.

## Parked (unchanged from before this session)

Confidentiality template field wording, attorney review of engagement agreement Section 3, LinkedIn 19-week content calendar, Category E Direction 2 (shelved). Do not resurface unless Pete reopens.

## Time-anchored

**Quarterly Step-Back — conducted this session, 2026-08-22.** No longer a forced check-in on the philosophy question itself. Next natural check-in is whenever Dark/Neutral activation, the `/about/method` nav gap, or `/about/page.tsx`'s orphaned-stub status gets picked up — not scheduled, Pete's call.

## Files to attach next session

- **Always**: `tools/_mob.txt` (current version, v4.223).
- **If resuming Dark/Neutral palette activation**: `web/app/globals.css` (the Warm `:root` block and `@theme inline` mappings this session added are the exact pattern to replicate for `[data-theme="dark"]`/`[data-theme="neutral"]`), `prompts/visual-identity-v3-palette-expansion.md` (the approved, contrast-verified Dark/Neutral hex values and tiers).
- **If resuming the `/about/method` nav gap or `/about/page.tsx`'s orphaned-stub status**: `web/components/NavBar.tsx`, `web/app/about/page.tsx`, `web/app/about/method/page.tsx`.
- **If resuming `built_to_fail`'s own-profile-loss investigation or the full taxonomy-wide re-authoring project**: `prompts/scd-wcs-remediation-tracker.md` (closing section and Phase 9 rows carry the full mechanism detail), `engine/data/salience.py`, `engine/data/states.py`.
- **If piloting the palette on another route**: `web/app/about/services/page.tsx` and its commit (`76815a7`) as the reference implementation for how the tier discipline maps to real elements.
