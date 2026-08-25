# Verifying Gemini's Global Canvas (`--background`/`--foreground`) Fix Proposal — 5 Items Checked

**CLOSED — SHIPPED, commit `db42abc`.** Both verification rounds below held up (one small, non-consequential numeric discrepancy in Round 2, noted there). Applied via `tools/patch_global_canvas_theme_reactive.py` (dry-run reviewed and approved before write); post-write re-read confirmed byte-for-byte identical to the reviewed dry-run. `tsc --noEmit` clean, vitest 45/45, live compiled CSS re-confirmed. The concrete downstream case (`/book/toc`'s resting filter chips, Dark theme) recomputes from 2.78:1 (failing WCAG AA) to 5.93:1 (passing) against Dark's new real `--background`. Full closing detail: `tools/_mob.txt` Section 13a (Decision Register).

Date: 2026-08-25. Full verification pass against live source, same standard as the `built_to_fail` and `/book/toc` reviews. **Nothing cleared for build — this is verification only. `globals.css` not touched.**

---

## 1. Consumer audit — **VERIFIED, with one citation inaccuracy**

Zero TSX usage of `bg-background`, `text-background`, `bg-foreground`, or `text-foreground` anywhere in `web/app` or `web/components`, confirmed via direct grep of both directories independently (not reused from Gemini's count). Broadened further than Gemini's own scope: a grep of the entire `web/` tree for the literal strings `--background`/`--foreground` (not just the Tailwind utility forms) returns exactly one file, `web/app/globals.css` — no JS/TS file anywhere reads either token via `getComputedStyle`, CSS-in-JS, or any other mechanism. This fully confirms the "zero architectural risk" premise for item 5 below, not just the narrower utility-class claim Gemini checked.

The four cited `globals.css` locations, confirmed line-for-line:
- Lines 4-5: `--background: #F6F3ED;` / `--foreground: #26241F;` — exact match.
- Lines 139-140: `--color-background: var(--background);` / `--color-foreground: var(--foreground);` — exact match.
- Lines 279-280: `background: var(--background);` / `color: var(--foreground);` — exact match.

**One real citation inaccuracy:** Gemini cited "line 10" for the comment mentioning `--background`/`--foreground`. The actual line is **11**: `* palette above (--background/--foreground, and --color-paper/-charcoal/`. Line 10 itself reads `* model, Gemini-cleared). ADDITIVE ONLY: these coexist with the Session 58` — no mention of either token. Minor, doesn't change the substance of the claim, but flagged per the verification-citation requirement.

## 2. `--field` values cited as justification — **VERIFIED**

`web/app/globals.css`:
- Line 51 (`:root`, Warm): `--field: #E9E7E2;` — matches Gemini's cited Warm value exactly.
- Line 112 (`[data-theme="neutral"]`): `--field: #FFFFFF;` — matches Gemini's cited Neutral value exactly.

## 3. Proposed Dark/Neutral values — **PARTIALLY VERIFIED, with a real, unexplained asymmetry**

Checked whether Gemini's proposed new hex values already exist elsewhere in `globals.css` under a different token name, per the specific question asked.

**Dark — both proposed values are exact duplicates of existing tokens, confirmed:**
- Proposed `--background: #171512` = `globals.css:85`, Dark's own `--field` value, **exactly**.
- Proposed `--foreground: #EDEAE3` = `globals.css:82`, Dark's own `--ink` value, **exactly**.

**Neutral — only one of the two matches Gemini's own stated logic:**
- Proposed `--foreground: #34383C` = `globals.css:109`, Neutral's own `--ink` value, **exactly** — consistent with the Dark pattern.
- Proposed `--background: #F6F3ED` — this is **not** Neutral's `--field` (`#FFFFFF`, confirmed above). It is instead **byte-identical to the current, unmodified `:root` fallback value** (`globals.css:4`). Under Gemini's own literal proposed values, Neutral's page canvas background would not change at all from what it is today.

**This is a real, load-bearing inconsistency in the proposal, not a citation slip.** Two readings are both plausible from what I can verify, and I can't resolve which one is intended from the summary given:
- **Deliberate, and arguably well-grounded:** `web/components/ServicesPageContent.tsx`'s own header comment (an already-shipped Dark/Neutral surface) explicitly states that page "uses `bg-paper`, not `--field`" for Neutral specifically — a real, existing precedent for Neutral content staying anchored to the paper/cream tone rather than migrating to `--field`'s pure white. If Gemini's Neutral `--background` choice is knowingly reusing that precedent, it's defensible.
- **An oversight:** nothing in the summary provided states this reasoning explicitly, and if it wasn't deliberate, this proposal would leave Neutral's canvas non-theme-reactive under the exact same mechanism (a value not redefined per theme) that this whole review exists to fix — just less severely, since Neutral's canvas already happens to pass contrast either way (see item 4).

**This needs to go back to Gemini as an explicit question before build, not be assumed either way:** is Neutral's `--background` staying at `#F6F3ED` deliberate (and if so, on what basis), or should it move to `#FFFFFF` to match `--field` the same way Dark's proposed values match Dark's `--field`/`--ink`?

## 4. WCAG contrast recomputation — **VERIFIED for the number given, but the framing needs correction**

Independently recomputed via the standard WCAG relative-luminance formula (not taken as given):

- Dark `--oxide-text` (`#C9825C`) against Gemini's proposed Dark `--background` (`#171512`): **5.93:1** — matches Gemini's claimed number exactly.
- **This is not a new computation on Gemini's part — it's the identical number already established in this project's own record.** Because Gemini's proposed Dark `--background` is byte-identical to Dark's real `--field` (item 3), this is the exact same pairing already computed and logged during the `/book/toc` verification (commit `67b8416`, MOB v4.242 entry): `text-oxide-text` on `bg-field`, Dark theme, 5.93:1. Gemini's number checks out, but it should be presented as confirming an already-known value, not as new evidence for the proposal's soundness.
- For completeness, the Neutral-side equivalent under Gemini's *actual* proposed value: `text-oxide-text` (`#3D5A72`) against the proposed `--background` (`#F6F3ED`, unchanged) computes to **6.53:1** — still passes AA, but this is *lower* than the **7.23:1** already established against Neutral's real `--field` (`#FFFFFF`) in the same `/book/toc` record. Both pass, so this isn't a failure, but it's a second, concrete symptom of item 3's asymmetry: Neutral's canvas under this proposal genuinely behaves differently from Neutral's own `--field`, not just nominally.

## 5. "Confines to four lines" / mechanism validity — **VERIFIED**

The `[data-theme="dark"]` (`globals.css:81-106`) and `[data-theme="neutral"]` (`globals.css:108-135`) blocks already redefine `--ink`, `--field`, `--field-raise`, `--oxide`, `--oxide-text`, `--slate`, `--line`, `--line-strong`, `--cta-text`, `--urgency`, and `--urgency-text` using the identical attribute-selector CSS custom-property override pattern the fix would need for `--background`/`--foreground`. This is not a different or novel mechanism — it's the same cascade/inheritance behavior already proven working for eleven other tokens in this exact file, confirmed by direct read of both blocks. Adding two new declaration lines to each block (four total) is mechanically sound and requires no change to the `:root` block or the `body` rule itself, both of which already correctly reference `var(--background)`/`var(--foreground)` and would pick up the new per-theme values automatically through the existing cascade. Combined with item 1's confirmed zero-external-consumer finding, "zero architectural risk" holds for the mechanism itself — contingent on item 3's Neutral asymmetry being resolved first, since that's a real open question about the *values*, not the *mechanism*.

---

## Summary table

| # | Claim | Verdict |
|---|---|---|
| 1 | Consumer audit (four `globals.css` sites, zero TSX usage) | **VERIFIED** — one citation off by one line (10 vs. 11), substance unaffected |
| 2 | `--field` values (`#E9E7E2` Warm, `#FFFFFF` Neutral) | **VERIFIED** |
| 3 | Proposed Dark/Neutral values | **PARTIALLY VERIFIED** — Dark's two values and Neutral's `--foreground` are exact reuses of existing `--field`/`--ink` values, confirmed. Neutral's proposed `--background` is *not* Neutral's `--field` — it's the unmodified current fallback, a real unexplained asymmetry needing an explicit answer from Gemini before build |
| 4 | WCAG contrast (5.93:1 Dark) | **VERIFIED as computed**, but it's a restatement of an already-established number, not new evidence; Neutral's real number under the actual proposed value (6.53:1) differs from what's already on record for `--field` (7.23:1) |
| 5 | "Zero architectural risk / four lines" | **VERIFIED** — same proven mechanism as eleven other tokens, zero external consumers confirmed, contingent on item 3 being resolved |

## Bottom line

Nothing fabricated. The consumer audit, the `--field` citations, and the mechanism claim all hold up cleanly. The real finding is item 3: Gemini's own proposed values are internally asymmetric between Dark and Neutral in a way the summary given doesn't explain, and it has a measurable (if currently non-failing) downstream effect on Neutral's actual contrast numbers. **Before this clears for build:** send this asymmetry back to Gemini as a direct, explicit question — is Neutral's `--background` staying fixed deliberate (and tied to the real `ServicesPageContent.tsx` precedent), or should it move to `#FFFFFF` to match `--field` the same way Dark's values do. Not acted on — Pete's call on how to proceed.

---

## Round 2 — Verifying Gemini's follow-up (Neutral `--background` correction) — 4 items checked

Date: 2026-08-25 (continued). Gemini's follow-up acknowledges the `#F6F3ED` value was unexamined inheritance, not deliberate, and proposes Neutral `--background` move to `#FFFFFF` to match Neutral `--field`. **Still verification only — `globals.css` not touched.**

### 1. Recomputed contrast (Neutral `--oxide-text`/`--ink`/`--oxide` against `#FFFFFF`) — **VERIFIED, with one real numeric discrepancy**

Independently recomputed via the same WCAG formula used throughout this project:

| Token | Gemini's claim | Recomputed | Match |
|---|---|---|---|
| `--oxide-text` (`#3D5A72`) | 7.24:1 | **7.23:1** | Effectively exact (rounding) |
| `--ink` (`#34383C`) | 11.72:1 | **11.82:1** | **Real discrepancy, 0.10** |
| `--oxide` (`#4A6B85`) | 5.63:1 | **5.63:1** | Exact |

The `--ink` number is off by a real 0.10, not just rounding noise (recomputed at full precision: 11.818129). **Doesn't change the substantive conclusion** — both Gemini's number and the real one clear WCAG AAA (7:1) by a wide margin, so nothing here would flip a pass/fail determination. Flagged per the standing verification discipline (report the discrepancy regardless of whether it's consequential), not glossed over because it's small.

### 2. Cited line ranges (`globals.css:81-85` Dark, `:108-112` Neutral) — **VERIFIED**

Re-confirmed both ranges directly:
- Lines 81-85 (Dark): `[data-theme="dark"] {` / `--ink: #EDEAE3;` / 2-line `--hover-ink` comment / `--field: #171512;` — exact match.
- Lines 108-112 (Neutral): `[data-theme="neutral"] {` / `--ink: #34383C;` / 2-line `--hover-ink` comment / `--field: #FFFFFF;` — exact match.

Both ranges are structurally identical (selector, `--ink`, comment, `--field`), confirming the two blocks are genuinely parallel at this point in the file, consistent with the pattern already confirmed for the other eleven tokens in Round 1. The cited ranges don't by themselves disambiguate an exact insertion line for the two new declarations — addressed directly in the prepared diff below.

### 3. `ServicesPageContent.tsx`'s comment — **VERIFIED, Gemini's characterization holds**

Real comment, `web/components/ServicesPageContent.tsx` lines 23-24, quoted exactly:

> `Neutral (tiers taken against paper, since this page uses bg-paper, not --field -- three of Neutral's seven colors change tier between the two): taupe is Pete's pick among three equally-valid LARGE/DECORATIVE-ONLY candidates...`

And line 46: `<main className="bg-paper min-h-screen">` — the component sets `bg-paper` on its own wrapper directly, in its own JSX. The comment is explaining why *this component's* own tier derivation used paper instead of `--field` — it says nothing about the sitewide canvas, makes no claim of setting a precedent beyond itself, and the styling choice is scoped entirely to this one component's own `className`. Gemini's characterization — a component-level choice, not a sitewide claim — matches the real text and code exactly.

### 4. "Inverted canvas hierarchy" consistency with Dark's confirmed pattern — **VERIFIED**

Round 1 already confirmed Dark's proposed `--background` (`#171512`) equals Dark's own `--field` exactly, and Dark's proposed `--foreground` (`#EDEAE3`) equals Dark's own `--ink` exactly. With this round's correction, Neutral's proposed `--background` (`#FFFFFF`) now also equals Neutral's own `--field` (`globals.css:112`) exactly, and Neutral's `--foreground` (`#34383C`, unchanged from Round 1) equals Neutral's own `--ink` (`globals.css:109`) exactly. Both themes now follow the identical `--background = --field`, `--foreground = --ink` pattern — genuinely symmetric, confirmed by direct hex comparison in both directions, not just asserted.

### Round 2 summary

| # | Claim | Verdict |
|---|---|---|
| 1 | Recomputed contrast | **VERIFIED** — `--ink`'s 11.72:1 is off by a real 0.10 (actual: 11.82:1), doesn't affect the pass/fail conclusion |
| 2 | Line ranges | **VERIFIED** |
| 3 | `ServicesPageContent.tsx` characterization | **VERIFIED** — quoted exactly, genuinely component-scoped |
| 4 | Dark/Neutral pattern consistency | **VERIFIED** — both themes now symmetric, `--background`=`--field`, `--foreground`=`--ink` |

**Bottom line:** the Round 1 open question is resolved. Three of four items check out exactly; the fourth (`--ink` contrast) has a small, real numeric inaccuracy that doesn't change any conclusion. The proposal is substantively sound and internally consistent now. Dry-run diff prepared below, not applied — commit requires Pete's explicit go-ahead regardless of this verification's outcome, per standing instruction.
