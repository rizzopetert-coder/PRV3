# Global Chrome Migration — Gemini Follow-Up: Two Corrections

Narrow, constrained follow-up to the Global Chrome Migration architecture review. Live-source verification (Claude Code, this repo, direct file reads) found two factual errors in the review. Everything else in that review — the `bg-field` vs `bg-background` semantic reasoning, the `hover:text-ink` universal-swap recommendation itself, the `--slate` reuse for quiet secondary text, the shadow/border-elevation approach for Dark, and the scope boundaries in Section 6 — was independently verified clean and does not need re-review. Please respond only to the two items below.

---

## Correction 1 — Precedent citation was wrong

The review cited `AssemblyPanel.tsx` and `StateDrawer.tsx` as existing precedent for `bg-field`/`bg-field-raise`/`border-line-strong`. Verified directly against live source: **neither file uses any of those tokens.**

Quoted, exact:

**`AssemblyPanel.tsx`**
- L65: `border-l border-gray-200 bg-paper`
- L83: `bg-paper border-t border-gray-200`
- L95: `bg-paper rounded-t-2xl border-t border-gray-200`

**`StateDrawer.tsx`**
- L22: `bg-white border-l border-gray-200`
- L26: `border-b border-gray-100`
- L70: `bg-white rounded-t-2xl`
- L73: `border-b border-gray-100`

Both files run entirely on flat v1 tokens (`bg-paper`, `bg-white`) and raw Tailwind gray utilities (`border-gray-200`/`border-gray-100`) — zero v2 tokens anywhere in either file.

Separately: `border-line-strong` is a real, defined CSS variable (`globals.css`, confirmed present in all three `[data-theme]` blocks) but has **zero usages anywhere in the entire `web` component tree** — confirmed via a repo-wide grep across all `.tsx` files. It has never been consumed as a live class.

The pattern described in the review — `bg-field`/`bg-field-raise` for chrome surfaces, `border-line` for their borders — **is real**, just attributed to the wrong files. The actual precedent is `ContextOrientation.tsx`:
- L97: `variant === "floating" ? "bg-field-raise" : "bg-field"`
- L38, L106, L114: `border-line` (three separate usages)
- L171: `bg-field` on its mobile `Drawer.Content`

**Ask**: Confirm the `bg-field`/`bg-field-raise` recommendation still holds against this corrected precedent (`ContextOrientation.tsx`, not `AssemblyPanel.tsx`/`StateDrawer.tsx`). Separately, for the quiet-icon-border role: either recommend `border-line` (the real, already-used token) instead of `border-line-strong`, or explicitly justify introducing `border-line-strong` as its first-ever real usage in this codebase — don't carry it forward as "precedent-backed" when it isn't.

---

## Correction 2 — `hover:text-ink` contrast figures were measurably off

Independently recomputed via the standard WCAG relative-luminance formula (same method this project has used and cross-verified in prior sessions — the Neutral figure below matches a value this project's own decision log already independently verified in an earlier round-trip).

| Theme | Review's figure | Corrected figure |
|---|---|---|
| Warm | 13.29:1 | **14.56:1** |
| Dark | 14.88:1 | **15.17:1** |
| Neutral | 11.72:1 | **11.82:1** |

Computed against the confirmed live values: `--ink` (`#14171A` Warm / `#EDEAE3` Dark / `#34383C` Neutral) and `--field` (`#E9E7E2` Warm / `#171512` Dark / `#FFFFFF` Neutral).

All three corrected figures are *safer* than what the review reported, so the pass/fail conclusion for the fix to the confirmed 1.18:1 critical bug is unaffected. This is not a rounding difference — every figure moved, consistently in the same direction (understated), which suggests a formula or input-value discrepancy on the review's side rather than simple imprecision.

**Ask**: Please issue corrected figures for the record (the three values above), since this fix is going into this project's decision log with exact numbers, not approximate ones. No re-analysis needed — just confirm/adopt the corrected figures.
