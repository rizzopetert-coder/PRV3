# Verifying Gemini's `/book/toc` Migration Review — 5 Items Checked

Date: 2026-08-25. Full verification pass against live source, same standard as the `built_to_fail` review. **Nothing cleared for build — this is verification only.**

---

## 1. All 8 named CSS variables — **VERIFIED to exist with real per-theme values, one nuance flagged**

Confirmed directly in `web/app/globals.css`, all three theme blocks (`:root`/Warm lines ~30-58, `[data-theme="dark"]` ~82-92, `[data-theme="neutral"]` ~109-119):

| Token | Warm | Dark | Neutral |
|---|---|---|---|
| `--ink` | `#14171A` | `#EDEAE3` | `#34383C` |
| `--field` | `#E9E7E2` | `#171512` | `#FFFFFF` |
| `--field-raise` | `#DFDCD5` | `#201E1A` | `#EFE6D0` |
| `--line` | `rgba(20,23,26,.14)` | `rgba(237,234,227,.09)` | `rgba(52,56,60,.10)` |
| `--oxide-text` | `#8C4A2F` | `#C9825C` | `#3D5A72` |
| `--cta-text` | `#E9E7E2` | `#171512` | `#FFFFFF` |
| `--slate` | `#5C6B66` | `#8FA39C` | `#7A7E82` |

**One real nuance, not caught by a simple existence check:** `--hover-ink` (`#26241F`) is confirmed to exist but is **deliberately not theme-reactive** — comments at `globals.css:83` and `:110` state explicitly "`--hover-ink` deliberately NOT overridden here... Stays `#26241F` in every theme." It's real and usable, but doesn't vary like the other seven. If any implementation guidance treats it as varying per theme the way `--ink`/`--field`/etc. do, that would be wrong.

## 2. Drawer.Content line 324 / bare `bg-white` — **VERIFIED, unchanged**

`sed -n '324p'` confirms byte-identical to the earlier re-verification pass today: `<Drawer.Content className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-2xl max-h-[80vh] flex flex-col md:hidden">`.

## 3. `bg-[color:var(--ink)]` as active/selected background — **NOT PROVEN as existing precedent; real nuance on both sides**

**No precedent anywhere.** `grep -rn "\[color:var(--" web/app web/components` returns exactly one hit sitewide — the `globals.css:26` *comment* recommending this syntax for `--slate` specifically. Zero live usage of bracket arbitrary-value syntax for any token, anywhere, on any migrated page.

**The two closest "selected state" precedents found (`SignatureCard.tsx:36-43`, `StateDrawer.tsx:45-49`) use the opposite visual pattern** — a light `bg-paper` fill with a colored border (`border-slate bg-paper` / `border-charcoal bg-paper`), not a dark ink fill. Both components are themselves still unmigrated v1 code, not real Visual Identity v3 precedent either way.

**But it's not invented from nothing.** `book/toc/page.tsx`'s own *existing* filter-chip active state (lines 348-349, 370-371) already uses a dark-fill pattern: `"border-charcoal bg-charcoal text-paper"` / `"border-slate bg-slate text-paper"`. Gemini's `bg-[color:var(--ink)]` proposal reads as a direct theme-reactive substitution for `bg-charcoal`, not a new visual concept — reasonable, but genuinely unproven in its migrated form.

**Separately, worth flagging: the bracket syntax may be unnecessary here at all.** `--ink`, `--field`, `--field-raise`, `--line`, `--oxide-text`, `--cta-text` all have real `--color-X: var(--X)` mappings in the `@theme inline` block (`globals.css:149-179`), meaning plain Tailwind utilities (`bg-ink`, `border-line`, etc.) work and are theme-reactive — confirmed live via `web/components/BookPieceContent.tsx:49`'s `border-line`. The documented reason for bracket syntax (`globals.css:22-27`) is specifically that `--slate` lacks a `--color-slate` mapping. If Gemini's guidance uses brackets for tokens that already have plain utilities, that's a real, avoidable inconsistency with the one confirmed live pattern.

## 4. `--cta-text` and the pop-color rule — **VERIFIED to exist and be real, but the rule doesn't govern `--cta-text` directly — flagged as a likely real misuse if used standalone**

The "locked pop-color rule" is real, confirmed at `prompts/visual-identity-v3-palette-expansion.md:170`: *"the pop color (berry/fuchsia/plum per theme) is used exactly once per page, on the single primary call-to-action only — button fill, no other application."* `--cta-text` is real and is the confirmed pairing token (`globals.css` comments at lines 72, 100, 130 all reference "same pop-color rule"; `prompts/visual-identity-v3-ask-book-migration-audit.md:65` documents it was chosen via real computed WCAG contrast — 4.9-7.04:1 — specifically against each theme's own pop-color fill).

**The precise distinction that matters:** the "once per page" constraint governs the **pop-color background** (berry/fuchsia/plum), not `--cta-text` by itself. `--cta-text` was never validated for contrast against anything *other than* the pop-color it's paired with. **Using `--cta-text` as a general filter-chip text color — not paired with a pop-color background — wouldn't violate the letter of the once-per-page rule, but it would be a real, uncontrolled contrast risk**, since it was computed for one specific background pairing, not general use. If Gemini's guidance proposes `--cta-text` on filter chips sitting on `--field`/`--field-raise` backgrounds (not the pop-color), this needs its own contrast check before use, not an assumption that "the token is designated for CTAs" makes it safe anywhere.

## 5. `termsHovered`/`termsTapped` naming — **VERIFIED accurate, correctly distinct from Category E's different naming**

`web/app/book/toc/page.tsx:230-231` confirms exactly `termsHovered`/`termsTapped` (two independent booleans), live in the current file, with an explicit comment at line 224 referencing this as a reused pattern from this page's own prior Gestalt Pass work. Cross-checked against `prompts/book-toc-gestalt-pass-gemini-review.md:47`, which specified this exact naming for this exact page.

**The concern raised — that Gemini might be pattern-matching from Category E's differently-named implementation — does not materialize.** `prompts/category-e-direction1-refinement-addendum-gemini-review.md` confirms that work uses `hoveredDimension`/`tappedDimension` (different names, and a different shape — a single nullable `AxisKey | null` discriminator, not two independent booleans) in a different component (`ConstellationField.tsx`). Gemini's citation matches `/book/toc`'s own real naming, not Category E's. A reasonable thing to check, and it checked out clean.

---

## Summary table

| # | Claim | Verdict |
|---|---|---|
| 1 | All 8 tokens exist, real per-theme values | **VERIFIED** — with `--hover-ink` flagged as deliberately non-theme-reactive |
| 2 | Drawer.Content line 324, bare `bg-white` | **VERIFIED**, unchanged |
| 3 | `bg-[color:var(--ink)]` active-state precedent | **NOT PROVEN as existing precedent anywhere** — reasonable mapping of book/toc's own current pattern, but genuinely unproven in migrated form; bracket syntax itself may be unnecessary given plain utilities exist and are the one confirmed live pattern |
| 4 | `--cta-text` + pop-color rule | **VERIFIED to exist**, but the locked rule governs the pop-color background, not `--cta-text` directly — standalone use on filter chips is a real, uncontrolled contrast risk, not pre-cleared by the CTA designation |
| 5 | `termsHovered`/`termsTapped` naming | **VERIFIED**, matches live code exactly, correctly distinct from Category E's different naming |

## Bottom line

Nothing here is flatly fabricated. Two items (2, 5) check out clean. Two items (1, 4) are real but carry a nuance that changes how they should be used, not whether they exist. One item (3) is the substantive gap: the proposed active-state pattern has zero live precedent anywhere in the migrated corpus, and the bracket syntax itself may not even be the right tool for tokens that already have plain utility classes. **Before any build:** resolve item 3's syntax question (plain `bg-ink`/`border-line` vs. bracket syntax) against the one confirmed live pattern, and get a real contrast check for `--cta-text` on filter chips per item 4 before using it there. Not acted on — Pete's call on how to proceed.
