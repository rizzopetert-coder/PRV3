# Contextual Orientation Affordance — Build Plan

Status: ready to build. Architecture verified against live source across two independent
passes (this session) — all claims confirmed, no open discrepancies on the core
component/token/drawer architecture. This document covers implementation specifics
discovered during pre-build exploration that weren't part of either verification pass,
plus explicit flags on a few places where the original spec's wording doesn't map
1:1 onto real code — resolved here, not silently reinterpreted.

---

## 1. Deviations from the spec, flagged explicitly before building

**These are not disagreements with the architecture — they're places where a literal
field/state name in the spec doesn't exist in real code, so a substitution was needed.
Flagging per standing verification discipline rather than quietly picking one.**

1. **No literal "checkpoint" flow state.** `DiagnosticFlow.tsx`'s real `FlowState` union
   is `intake | loading | question | narrative | complete | error`. Checkpoints are a
   sub-case of `question` (`label.kind === "spliced"` vs. `"core"`), not a distinct
   phase. Templating "by flow state (intake / core questions / checkpoint)" as spec'd
   isn't literally possible — building instead: `intake`, `question` (core), `question`
   (spliced/checkpoint, via `label.kind`), `narrative`. Four real copy variants, covering
   the same ground the spec asked for under the real state shape.

2. **No `routingMode` field.** `PrivateOutputPayload` has `resolution_family:
   ResolutionFamily` (`"People Tactics and Strategy" | "Training & Development" |
   "Intervention" | "Executive Advisory"`) and `resolution_routing: string` (free
   prose, not an enum). `getResultsOrientation(severityTier, routingMode)` will be
   built as `getResultsOrientation(severityTier: SeverityTier, resolutionFamily:
   ResolutionFamily)` — `resolution_family` is the real categorical field that plays
   the role "routingMode" was describing.

3. **Token utility classes, not bracket syntax, for everything except `--slate`.**
   Confirmed via `globals.css`'s `@theme inline` block: `--line`, `--field`,
   `--field-raise`, `--ink`, `--oxide-text` are all real, already-mirrored Tailwind
   utilities (`border-line`, `bg-field`, `bg-field-raise`, `text-ink`, `text-oxide-text`)
   — already used exactly this way in `BookPieceContent.tsx`. Only `--slate` (v2) is
   deliberately excluded from `@theme` (collides with the v1 `--color-slate` name),
   so it alone needs `text-[color:var(--slate)]`. Building with plain utility classes
   everywhere they exist, bracket syntax only for `--slate` — same visual result as
   the spec's literal bracket-everywhere wording, more idiomatic, matches the one real
   precedent file that already does this.

4. **`modal-drawer` variant: implemented, not used this pass.** None of the 5 rollout
   surfaces calls for a desktop modal specifically — all five map cleanly onto
   `inline` (hover/focus-anchored panel, in document flow) or `floating` (fixed-position
   trigger, for the diagnostic flow where content scrolls under it). `modal-drawer` is
   built as a real, working third variant (desktop: click-triggered centered overlay
   instead of hover-anchored panel; mobile: identical `vaul` drawer as the other two)
   so the component's API matches the full spec, but nothing in this rollout invokes it.
   Available for a future surface that needs it.

5. **Homepage: confirming claim 1, not just agreeing by default.** `web/app/page.tsx`
   lines 43–68 already carry hand-authored orientation copy directly above the three
   entry points, with its own header comment: "Orientation copy — closes the site-wide
   orientation gap (Section 13, item 5)." This shipped already, in a prior session, and
   reads as intentional, in-voice copy, not a placeholder. **No new affordance on the
   homepage.** Also worth noting for context (not a reason to change anything here):
   `DiagnosticGate`'s self-select intake (`diagnostic/page.tsx`, Phase 1) and
   `IntakeForm` (`DiagnosticFlow.tsx`, lines 314–325) both already carry their own
   hand-authored orienting copy too — the new `intake`-phase trigger is additive and
   kept short, not a replacement for that existing copy.

6. **`data-emphasis="secondary"` — no genuinely obvious use found.** Checked for a
   "previously viewed" case per the spec's own suggested example; none of the 5
   surfaces has an existing seen/unseen tracking mechanism, and building one is out
   of scope for this task (adds `localStorage` state management not requested
   anywhere in the spec). Not used. Only `receded`/`primary` this pass.

---

## 2. Component: `web/components/ContextOrientation.tsx`

```ts
export type OrientationVariant = "inline" | "floating" | "modal-drawer";

interface ContextOrientationProps {
  variant: OrientationVariant;
  topic: string;      // stable id, used for aria-label and the drawer's sr-only title
  title: string;
  summary: string;    // one line, shown at the top of the resolved panel/drawer
  details: string;    // body copy
  className?: string; // wrapper override for per-surface trigger placement
}
```

**Desktop (md+), `inline`/`floating`:** direct port of `book/toc/page.tsx`'s
`termsHovered`/`termsTapped` pattern (lines 409–437) — `relative inline-block` trigger
(`inline`) or `fixed` positioned trigger (`floating`), `onMouseEnter`/`onFocus` resolve
a `hidden md:block` anchored panel, `onKeyDown` Enter/Space calls `preventDefault()`
per the spec's accessibility requirement. Panel and trigger both carry
`data-emphasis="receded"` at rest, `data-emphasis="primary"` when resolved — real,
already-shipped `globals.css` utilities (lines 279–292), untouched.

**Desktop, `modal-drawer`:** click (not hover) opens a `fixed inset-0` centered overlay
panel, `data-emphasis="primary"` while open, closes on backdrop click or Escape.

**Mobile (<md), all variants:** exact `Drawer.Root`/`Drawer.Portal`/`Drawer.Overlay`/
`Drawer.Content`/`Drawer.Title` shape from `book/toc/page.tsx` lines 443–455 —
`sr-only` title, `open`/`onOpenChange` wired to local `open` state, `bg-field
rounded-t-2xl`, `md:hidden` on the drawer parts so desktop never renders it.

**Accessibility:** desktop trigger gets `aria-describedby={panelId}` (via `useId()`)
pointing at the resolved panel; mobile trigger gets `aria-haspopup="dialog"
aria-expanded={open}`; both.

**Tokens used (hard constraints from the spec, confirmed against real utilities per
§1.3 above):**
- Receded trigger/text: `text-[color:var(--slate)]` (only bracket-syntax exception)
- Border: `border-line`
- Resolved surface: `bg-field` (inline/modal-drawer panel) or `bg-field-raise`
  (floating trigger's panel, for a slight visual lift off the page — matches the
  distinction the spec drew between the two `bg-*` options rather than picking one
  and ignoring the other)
- Resolved headline: `text-ink`
- Resolved body: `text-oxide-text`
- **Never**: `--color-rust`, `--urgency`, `--urgency-text`, in any form (utility class
  or bracket syntax), anywhere in this file. Verified by a post-build grep sweep
  (§5 below) before anything is committed.

---

## 3. Data: `web/data/orientation-copy.ts` (net-new, confirmed no existing file)

```ts
export interface OrientationCopy {
  title: string;
  summary: string;
  details: string;
}

// Static, hand-authored per surface.
export const ORIENTATION_COPY: Record<string, OrientationCopy> = {
  "diagnostic-intake": { ... },
  "diagnostic-question": { ... },
  "diagnostic-checkpoint": { ... },   // label.kind === "spliced"
  "diagnostic-narrative": { ... },
  "book-toc": { ... },
  "output-private": { ... },
  "output-shareable": { ... },
};

export function getBookPieceOrientation(
  contentType: BookContentType,   // "memo" | "methodology" | "case_pattern"
  voice: BookVoice,                // "standard" | "from_the_author"
): OrientationCopy { ... }

export function getResultsOrientation(
  severityTier: SeverityTier,                 // "Emerging" | "Entrenched" | "Endemic"
  resolutionFamily: ResolutionFamily,          // see §1.2 — substituted for "routingMode"
): OrientationCopy { ... }
```

All copy written against P-14's actual locked text (`tools/_mob.txt` line 137):
*"When brand voice risks obscuring meaning, plain language wins — don't make the reader
do the work of decoding what could just be said directly."* Plain operational language
throughout — what this screen shows, what to do next — no diagnostic metaphor, no
internal taxonomy terms (state names, dimension names, SCD-WCS, tier mechanics) in the
orientation copy itself, even though those terms appear correctly elsewhere on the
same screens.

---

## 4. Per-surface wiring

| Surface | File | Variant | Anchor point | Copy source |
|---|---|---|---|---|
| Homepage | — | — | **No change** — already has orientation copy (§1.5) | — |
| Diagnostic flow | `web/components/DiagnosticFlow.tsx` | `floating` | Rendered alongside each non-loading/error phase's return | `ORIENTATION_COPY["diagnostic-intake" \| "diagnostic-question" \| "diagnostic-checkpoint" \| "diagnostic-narrative"]`, keyed off `state.phase` and, for `question`, `state.label.kind` |
| Conditions explorer | `web/app/book/toc/page.tsx` | `inline` | New trigger, placed near but visually distinct from the existing `TERMS_GUIDE_TRIGGER_TEXT` button (own `topic`, own copy — not reusing `TermsGuideContent`) | `ORIENTATION_COPY["book-toc"]` |
| `/book/[type]/[slug]` articles | `web/components/BookPieceContent.tsx` | `inline` | Between the JSON-LD `<script>` and the `<h1>` (line 36) | `getBookPieceOrientation(piece.contentType, piece.voice)` |
| Output — private | `web/components/PrivateOutput.tsx` | `inline` | Immediately before Block 1 (line 141, before the `pb-4` condition-header div) | `getResultsOrientation(payload.severity, payload.resolution_family)` |
| Output — shareable | `web/components/ShareableOutput.tsx` | `inline` | Immediately before Block 1 (line 56, before the header-bar div) | `getResultsOrientation(payload.severity, payload.resolution_family)` |

---

## 5. Verification before commit

- `tsc --noEmit` clean
- `npm run test` (vitest) — no regression from current 45/45 baseline
- Visual check across Warm/Dark/Neutral (compiled CSS / computed values, no browser
  tool available in this environment — same documented limitation as every prior
  theme-rollout session; flagged, not silently skipped)
- **Grep sweep, mandatory:** `--color-rust`, `--urgency`, `--urgency-text` — zero
  matches inside `ContextOrientation.tsx` or `orientation-copy.ts`, and zero *new*
  matches introduced anywhere else touched this pass. Reported explicitly in the
  diff summary before push, per Pete's explicit ask.

---

## 6. Commits (grouped, not one giant commit)

1. Component + no wiring yet: `web/components/ContextOrientation.tsx`
2. Data file: `web/data/orientation-copy.ts`
3. Diagnostic flow wiring: `web/components/DiagnosticFlow.tsx`
4. `/book/toc` wiring: `web/app/book/toc/page.tsx`
5. `/book/[type]/[slug]` wiring: `web/components/BookPieceContent.tsx`
6. Output screens wiring: `web/components/PrivateOutput.tsx`, `web/components/ShareableOutput.tsx`
7. `tools/_mob.txt` — locked decision + session log + version bump (separate, after
   the build is confirmed clean, not bundled with any code commit)

No push until Pete reviews the diff summary and gives explicit go-ahead, per the task's
own instruction — this overrides the usual stage+commit+push-together default.

---

## 7. MOB update (after build, own commit)

- New Decision Register / Locked Decisions entry: standing design rule for contextual
  orientation. Open call, stated here rather than guessed silently: **P-15** (new
  entry) vs. an amendment to an existing P-##. Recommendation worked out during build
  once the actual shape of the rule is settled by what got built — this plan doesn't
  pre-decide it.
- Session log entry, version bump per standing discipline (locked decision + status
  change qualifies).
