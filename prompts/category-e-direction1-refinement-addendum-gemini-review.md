# Category E, Direction 1 Refinement Addendum — Gestalt Interpretability
## Gemini Review: Constrained Confirmation Only

Status: ready to send. Not an open architecture review. Full context:
`prompts/category-e-direction1-refinement-addendum-gestalt-interpretability.md` (the original
concept/scope doc) and `web/components/ConstellationField.tsx` (the real, shipped component this
touches — commit `451f5a7`, Direction 1 Refinement).

This follows the same discipline that has now cleared cleanly twice on this project (Category
D's rounds 3–4, `/book/toc`'s Phase 2): state what's already confirmed against real source
plainly, ask for confirm-or-reject only, no room for reinventing a third option.

## Locked, not open for reinvention

- **Copy is final.** Title "How to read this," three short points (distance-from-center meaning,
  the rust/Endemic hard-binary rule, single-vertex vs. multi-vertex reading). Already through
  Pete's own P-10 brand-voice pass. Do not propose alternative copy or a different point count.
- **Tab order is decided.** This affordance receives focus before the four axis hit-areas
  (gestalt-first), not after. Pete's explicit call. Not open for reconsideration.
- **Placement is decided.** A visually distinct, single affordance near the shape — not a fifth
  vertex-style hit-area, not competing with the four axis labels at rest.

## What's actually being asked — one structural choice, two options, no third

The four axis hit-areas (`apt`/`auth`/`all`/`att`) already share a single pair of state
variables — `hoveredDimension` and `tappedDimension`, both typed `AxisKey | null` — driving one
desktop reveal panel and one `Drawer.Root` (vaul) instance for mobile. Confirmed by direct read
of the real, current file, not the pre-build trace:

```tsx
const [hoveredDimension, setHoveredDimension] = useState<AxisKey | null>(null);
const [tappedDimension, setTappedDimension] = useState<AxisKey | null>(null);
```

Two structural options for adding the fifth, gestalt-level affordance:

**(a) Fully separate.** A second pair of state variables (e.g. `gestaltOpen: boolean`) and a
second `Drawer.Root` instance dedicated to the gestalt panel, independent of the four axes'
state and markup entirely.

**(b) Shared.** Widen `hoveredDimension`/`tappedDimension` to `AxisKey | "gestalt" | null`,
reusing the one existing `Drawer.Root` instance and the one existing desktop-panel block, with
new conditional branches for the `"gestalt"` case.

## What option (b) concretely requires — confirmed this session against the real shipped code

This is more specific than the original trace could be, since it predates the actual build.
Confirmed by direct read of `ConstellationField.tsx`'s current `LiveField`, not re-derived from
the mockup:

1. `hoveredInfo`/`tappedInfo` are currently derived as `axisToDimensionKey(hoveredDimension)` →
   `PUBLIC_DIMENSION_LABELS[...]`, a `{title, description}` pair. `axisToDimensionKey` has no
   `"gestalt"` case, and the addendum's own three-bullet copy doesn't fit that shape. Option (b)
   needs a new branch here, not just a wider type.
2. `labelPositions` (the desktop panel's positioning source, keyed by `AxisKey`) has no
   `"gestalt"` entry — the gestalt affordance's desktop panel would need either a new fixed
   position added to that same lookup or an entirely separate positioning branch.
3. The four axis hit-areas render via one `(Object.keys(AXES) as AxisKey[]).map(...)` loop,
   intrinsically bound to the real `AXES` const (4 entries, no more). A fifth, gestalt affordance
   cannot join that loop — it needs its own standalone JSX element (icon or text link, per the
   locked placement/visual-distinctness requirement above), which then sets the same
   `hoveredDimension`/`tappedDimension` state to the literal `"gestalt"`.
4. `Drawer.Content`'s body currently renders `tappedInfo.title`/`tappedInfo.description`
   unconditionally when `tappedInfo` is set. Option (b) needs a conditional branch there too, to
   render the three-bullet gestalt copy instead of a title+description pair when
   `tappedDimension === "gestalt"`.

Net: option (b)'s "shared `Drawer.Root`" is real and available — nothing in the shipped build
forecloses it — but it is not a one-line type-widen. It touches four real spots in the existing
render logic, all listed above, because the gestalt content's shape (three bullets) genuinely
differs from the four axes' shape (title + description).

## Corner-position math — re-verified, still holds

The original trace's "all four diagonal corners are empty" finding was re-checked against the
real shipped coordinates (not the mockup): `LIVE_VIEW_W`/`LIVE_VIEW_H` = 600×600,
`LIVE_CENTER` = (300, 300), `LIVE_MAX_R` = 220. The four axis hit-area rects sit at fixed
`labelPositions`, not the data-driven vertex points:

| Axis | Position | Hit-area rect (68×32) |
|---|---|---|
| apt | top-center | x:[266,334] y:[49,81] |
| auth | right-center | x:[506,574] y:[289,321] |
| all | bottom-center | x:[266,334] y:[529,561] |
| att | left-center | x:[26,94] y:[289,321] |

All four cluster at cardinal edge midpoints. None comes within roughly 150px of any of the
canvas's four diagonal corners. Confirmed — a gestalt affordance placed in a diagonal-corner
region would not visually or functionally compete with any of the four existing hit-areas,
under either option (a) or (b).

## `StateDrawer.tsx` as the reference pattern — re-confirmed unchanged

`web/components/StateDrawer.tsx` was last touched in commit `0e13fa4` (2026-07-05, a
token/color-only pass), before both the original addendum trace and the actual Direction 1
Refinement build (`451f5a7`) — confirmed via `git log`, not assumed stable. Its
desktop-panel/mobile-`Drawer.Root` split, driven by one shared open/close value, is the exact
pattern `ConstellationField.tsx`'s `LiveField` already adopted for the four axes. It remains the
correct reference point for either option.

## The ask — confirm or reject, nothing else

> Given the four concrete implementation touch-points listed above for option (b), and the
> locked copy/placement/tab-order constraints, which of options (a) or (b) is architecturally
> sound to build against the real shipped `ConstellationField.tsx`? State a specific objection
> to the option you reject, if any. Do not propose a third structural option (e.g. a context
> provider, a separate component extraction, or a different state-sharing mechanism) — the
> choice is between (a) and (b) as described, not open redesign.

### What counts as a well-formed response

- **(a) or (b), confirmed as sound**, optionally with a specific, narrow objection to the
  other.
- **Not well-formed:** a third structural option, a proposal to change the locked copy, tab
  order, or placement, or a rendering-target/file-path claim not checked against the real
  `ConstellationField.tsx` and `StateDrawer.tsx` paths above.

Standard discipline applies on the way back in: whatever Gemini returns gets independently
verified against real source before anything is treated as final, same as every round before
this one.
