# Visual Identity v3 — Palette Expansion (Pete-Approved Direction, 2026-08-22)

Status: **DIRECTION APPROVED AND IN ACTIVE ROLLOUT.** The `--oxide` decoupling question (below) is resolved by Pete. Full 21-color contrast verification is CLOSED — every color across all three themes has a defined usage tier (see below), none left undefined or unusable — and the pop-color rule is LOCKED (Pete-confirmed). All three themes' tokens are wired into `globals.css` (Warm: commit 76815a7; Dark/Neutral: commit 2373654) and live-piloted across every page in `/about/*` — `/about/services`, `/about/story`, `/about/method`, and the `/about` hub. `ThemeSwitcher` is mounted, scoped to `/about/*` only; Gemini's architecture review of that mounting/general-accent question is independently verified (`prompts/gemini-themeswitcher-review-verification.md`, commit 1ffb3e7). This file remains the record of the original decision; implementation status is tracked here as it changes, not re-litigated.

## STANDING GOTCHA — three unrelated, visually similar green/blue tokens

Confirmed via `prompts/gemini-themeswitcher-review-verification.md` (commit 1ffb3e7): this codebase currently carries three genuinely different tokens that are easily confused by name and by eye — all muted blue-green, from three different token generations, serving different roles:

- **v1 `--color-slate` = `#4A6B85`** — the original Session 58 palette's general accent, live today via bare `border-slate`/`text-slate`/`bg-slate` Tailwind utilities (e.g. `SignatureCard.tsx`, `book/toc/page.tsx`'s signature-tag pills).
- **v2 `--slate` = `#5C6B66`** — the OD-07 general-accent layer, deliberately NOT mapped to a bare Tailwind utility (would collide with the v1 name above), only reachable via arbitrary-value syntax (`text-[color:var(--slate)]`) or inline style.
- **v3 `--moss` = `#5C6B4A`** — one of Warm's 7 new palette-expansion colors (this file), TEXT-SAFE tier, wired into `globals.css` but not yet consumed by any live component.

These are unrelated tokens that happen to land on similar hex values, not three names for the same thing and not a naming conflict to resolve. **Check which generation's token you actually mean before touching any color value in this codebase** — the name alone won't tell you, and getting this wrong silently changes the wrong theme layer.

## DECISION — `--oxide` decouples into general-content use (2026-08-22), confirmed by Pete

**Confirmed directly by Pete, not inferred:** `--oxide` decouples from its original severity-pairing design intent into general-content use. This applies to the full 7-color-per-theme palette approved this session, not just `--oxide` itself — the palette was built as `--oxide`'s natural extension into general UI, so the decoupling decision covers the whole set.

**This formally resolves Gemini's stated blocking question from the original OD-07-extension architecture review** ("Pete must formally approve decoupling `--oxide` into a universal content accent token... before code is written for `/about`") — answered, on the record, this session.

**What stays unchanged:** `--urgency`/rust remains fully Endemic-exclusive in every theme, untouched by this decision, out of scope permanently unless a future session explicitly reopens it.

**What this decision does NOT resolve, still open:** full contrast verification across the 7-color palette (Warm now checked below; Dark and Neutral remain unchecked) and final Gemini sign-off confirming this decision actually satisfies their stated requirement — Pete's approval resolves the design-intent question, not the technical-clearance one.

## Origin

This session is a continuation of the Quarterly Step-Back that `prompts/visual-identity-philosophy-open-question.md` was staged for — that file's "craft problem vs. philosophy problem" fork is resolved here on the philosophy side: Pete has confirmed the restrained 3-color palette itself is not serving as an effective differentiator for this business, independent of craft execution quality. This is a governing-principle-level decision, not a craft note, and not something Claude Code or Claude.ai proposed — Pete's own call, recorded here.

## What's locked, unchanged, out of scope

`--urgency`/`--urgency-text` stays fully Endemic-exclusive, in every theme, unchanged. **No decorative use of rust anywhere, ever.** This constraint is not part of this expansion and was not reconsidered here.

## The approved direction — 7-color-per-theme palette (draft hex, not finalized)

Expands the OD-07-cleared 2-value general-accent system (`--oxide`/`--oxide-text` per theme) to a 21-color system (7 × 3 themes). `--oxide`/`--oxide-text` are retained as the first two colors in each theme's set below — not replaced, extended.

### Warm
| Role | Hex |
|---|---|
| oxide | `#8C4A2F` |
| ochre | `#B8863D` |
| moss | `#5C6B4A` |
| taupe | `#857C6E` |
| umber | `#5A3A28` |
| dusk blue | `#6B8299` |
| pop / berry | `#A62C6B` |

### Dark
| Role | Hex |
|---|---|
| oxide | `#B8663D` |
| oxide-text | `#C9825C` |
| amber | `#D4A24C` |
| sage | `#7C8A6B` |
| warm gray | `#9C9186` |
| dusty blue | `#7691A8` |
| pop / fuchsia | `#D6559E` |

### Neutral
| Role | Hex |
|---|---|
| oxide | `#4A6B85` |
| oxide-text | `#3D5A72` |
| taupe | `#8C7A6B` |
| sage gray | `#6B7864` |
| cool gray | `#6B7280` |
| muted gold | `#A68A4A` |
| pop / plum | `#9B2C6F` |

Note the asymmetry: Warm lists `oxide` once (no separate `oxide-text` row) — reflects the confirmed identical-value state from the current `globals.css` (see Cross-references below), not a formatting inconsistency. Dark and Neutral each list `oxide`/`oxide-text` as two distinct rows, matching their existing split values.

## Rust / --urgency exclusion, explicit

Rust and `--urgency`/`--urgency-text` are excluded entirely from all three palettes above. Confirmed still Endemic-exclusive, untouched by this expansion — this is a general-accent palette expansion, not a reserved-signal change.

## The pop color — role not yet specified, open question

Each theme's 7th color is labeled "pop" (berry / fuchsia / plum) and is intended as a true accent-of-accent — sparing use (a single CTA, one highlight moment), not a general-palette color on par with the other six. **Usage discipline is not yet formally specified.** Flagged as an open question for whoever scopes actual component-level usage rules: how sparing is "sparing," which component types it's eligible for, whether it needs its own lock language the way rust has.

## Scope, stated plainly

This is a genuine expansion, not a refinement:
- From 2 general-accent values per theme (`oxide`/`oxide-text`) to 7.
- **None of these values have been contrast-checked** — no WCAG verification against `--field`/`--field-raise` backgrounds in any theme, for text or CTA use.
- **No Gemini architecture review** has happened on this specific 21-color expansion.
- **Nothing is committed to `globals.css`** — this file records draft hex values only.
- This is a **Pete-approved DIRECTION**, not a finalized, buildable palette. Treat every hex value above as provisional until a real build pass verifies contrast and gets structural clearance.

## Cross-references — this decision is downstream of two other open items from this same session

**(a) Warm theme's `oxide`/`oxide-text` identical-value gap.** Confirmed via direct source read and full git history: Warm's `--oxide`/`--oxide-text` share an identical hex (`#8C4A2F`) in the current live `globals.css`, authored in a single commit (`2d063f7`, 2026-07-21, all three themes together, never revisited since) — not an incomplete multi-pass process left dangling, but also not defended in the source comment as a deliberate final choice the way Neutral's divergence explicitly is. **This new 7-color Warm palette effectively supersedes that narrow question** — Warm now gets real range (ochre, moss, taupe, umber, dusk blue, berry) regardless of how the original 2-value identical-value question would have been answered in isolation. Not fixed at the token level; superseded by broader scope.

**(b) The Gemini question of whether `--oxide` decouples into a general accent or stays severity-adjacent — RESOLVED, 2026-08-22.** Raised in this session's architecture-review pass (`prompts/gemini-visual-identity-v2-about-pilot-handoff.md`) — the one place `--oxide` was ever design-intended to mean something was as the non-Endemic half of a severity-signaling pair, sitting directly beside `--urgency`. **See the DECISION section at the top of this file** — Pete has now confirmed the decoupling directly, formally answering Gemini's stated blocking question. What remains open is technical clearance (contrast, full Gemini sign-off), not the design-intent question this cross-reference originally flagged.

## Contrast verification — all three themes, real WCAG-computed — CLOSED / FULLY RESOLVED (2026-08-22)

**Status: CLOSED.** Every one of the 21 colors across all three themes now has an explicit, decided usage role. This closes the full contrast-verification thread for the 21-color palette — no color is left in an undefined or "unusable" state.

Real relative-luminance/contrast-ratio computation (WCAG 2.x formula, sRGB gamma-corrected), not estimated — formula verified against the standard reference values (`#000000` on `#FFFFFF` = 21.00, `#767676` on `#FFFFFF` = 4.54) before trusting the results below. All 21 colors (7 per theme) checked against each theme's own `--field` as the primary reference background (Warm and Neutral also checked against `--background`/paper — see the per-theme notes for where that changes a color's tier).

### Usage tier model — three tiers, BACKGROUND-FILL-ONLY replacing the retired "NOT SAFE" label

An explicit usage tier per color, since "fails 4.5:1" does not mean "unusable" — it means the color needs a role that doesn't require text-level contrast, which is a real, buildable constraint, not a rejection. (Note on count: the prior pass had three tiers ending in a bare "NOT SAFE" label; this pass replaces that third tier's definition with the legitimate BACKGROUND-FILL-ONLY role below — still three tiers total, not four, since removing the old label and adding the new role are the same single change, not two.)

- **TEXT-SAFE** — cleared 4.5:1. Usable for body copy, links, and small UI text, no restriction.
- **LARGE/DECORATIVE-ONLY** — cleared 3:1 but not 4.5:1. Usable for headings 24px+, icons, borders, and fills — **never body text or small links.**
- **BACKGROUND-FILL-ONLY** — solid fill with dark charcoal/ink text on top only — never as the foreground color itself (never text, never icon, never border, on any background). Confirmed by Pete, 2026-08-22: ochre and muted gold (specifically when paired with `--background`/paper) get this role. Hex values unchanged from approved (`#B8863D` ochre, `#A68A4A` muted gold) — no darkening, no dropping.

### Warm (vs. `--field` #E9E7E2, primary; `--background`/paper #F6F3ED noted where it changes the tier)

| Color | Hex | Contrast (field / paper) | Tier |
|---|---|---|---|
| oxide | `#8C4A2F` | 5.42 / 6.05 | TEXT-SAFE |
| moss | `#5C6B4A` | 4.65 / 5.19 | TEXT-SAFE |
| umber | `#5A3A28` | 8.21 / 9.16 | TEXT-SAFE |
| berry/pop | `#A62C6B` | 5.32 / 5.94 | TEXT-SAFE |
| taupe | `#857C6E` | 3.33 / 3.71 | LARGE/DECORATIVE-ONLY |
| dusk blue | `#6B8299` | 3.22 / 3.59 | LARGE/DECORATIVE-ONLY |
| ochre | `#B8863D` | 2.61 / 2.91 | **BACKGROUND-FILL-ONLY** — solid fill, dark charcoal/ink text on top, never as foreground |

### Dark (vs. `--field` #171512)

| Color | Hex | Contrast | Tier |
|---|---|---|---|
| oxide-text | `#C9825C` | 5.93 | TEXT-SAFE |
| amber | `#D4A24C` | 7.87 | TEXT-SAFE |
| sage | `#7C8A6B` | 4.95 | TEXT-SAFE |
| warm gray | `#9C9186` | 5.91 | TEXT-SAFE |
| dusty blue | `#7691A8` | 5.54 | TEXT-SAFE |
| pop/fuchsia | `#D6559E` | 4.90 | TEXT-SAFE |
| oxide | `#B8663D` | 4.34 | LARGE/DECORATIVE-ONLY |

**Explicit rule for Dark's oxide/oxide-text pair, not a new decision:** `oxide-text` is the correct choice for ANY text or link role in Dark; plain `oxide` is decorative/large-only. This is the existing `oxide`/`oxide-text` split — built into the token system since the original OD-07 commit specifically so a general accent and its text-safe variant could diverge per theme — doing exactly the job it was built for, now with a concrete measured reason attached rather than an assumed one. Dark is the only theme where every non-oxide color is TEXT-SAFE — the cleanest of the three.

### Neutral (vs. `--field` #FFFFFF, primary; `--background`/paper #F6F3ED noted — several colors' tier changes by background here)

| Color | Hex | Contrast (field / paper) | Tier |
|---|---|---|---|
| oxide | `#4A6B85` | 5.63 / 5.08 | TEXT-SAFE |
| oxide-text | `#3D5A72` | 7.23 / 6.53 | TEXT-SAFE |
| pop/plum | `#9B2C6F` | 7.04 / 6.36 | TEXT-SAFE |
| sage gray | `#6B7864` | 4.67 / 4.22 | TEXT-SAFE vs. field; **drops to LARGE/DECORATIVE-ONLY vs. paper** |
| cool gray | `#6B7280` | 4.83 / 4.37 | TEXT-SAFE vs. field; **drops to LARGE/DECORATIVE-ONLY vs. paper** |
| taupe | `#8C7A6B` | 4.11 / 3.71 | LARGE/DECORATIVE-ONLY (both backgrounds) |
| muted gold | `#A68A4A` | 3.30 / 2.98 | LARGE/DECORATIVE-ONLY vs. field; **BACKGROUND-FILL-ONLY vs. paper** — solid fill, dark charcoal/ink text on top, never as foreground on that background |

Neutral is the only theme where the background choice itself changes a color's tier for three of the seven — `/about` build guidance should pick `--field` or paper deliberately for Neutral and re-check against whichever is actually chosen, not assume `--field`'s results carry over.

### Summary across all three themes — every color has a defined role

| | TEXT-SAFE | LARGE/DECORATIVE-ONLY | BACKGROUND-FILL-ONLY |
|---|---|---|---|
| Warm | 4 | 2 | 1 (ochre) |
| Dark | 6 | 1 (oxide) | 0 |
| Neutral (vs. field) | 5 | 2 | 0 |
| Neutral (vs. paper) | 3 | 3 | 1 (muted gold) |

All 21 colors resolved into one of the three tiers — none left unusable or undefined. **This does not block the direction itself** — Pete's decoupling decision (above) is about design intent, not implementation-readiness — and this tier model means it no longer blocks implementation either. Any component-level usage spec (see the pop-color rule below for the one role already specified) needs to route each color to its correct tier, not use the palette as if all 21 colors were interchangeable.

**Ochre darkening, reference only, not actioned:** a prior session pass binary-searched how much darkening (same hue/saturation) would move ochre into TEXT-SAFE or LARGE/DECORATIVE-ONLY territory — 3.5 lightness points (L 48.0%→44.5%, `#AA7C39`) clears 3:1; 13.1 points (L→35.0%, `#86612C`) clears 4.5:1, though that's a materially darker, more olive-brown result than the current ochre. **Superseded by the BACKGROUND-FILL-ONLY resolution above — ochre's hex value is unchanged, no darkening was adopted.** Logged here only as a reference point in case a future session wants to revisit tightening the value for a different role than background-fill. Do not action this without a separate, explicit decision.

## What this file is not

Not a build plan. Not a component-usage spec. Not a contrast/accessibility audit. Not a Gemini-cleared architecture decision. Each of those is separate, future, unscoped work — this file's only job is to record that Pete approved this direction, with these draft values, on this date, downstream of the two open items named above.

## Pop-color usage rule (2026-08-22) — LOCKED, Pete-confirmed

Distinct from everything else in this file: this is a proposed rule, not a confirmed decision like the decoupling above. Recorded here for review, not treated as locked.

**Proposed rule:** the pop color (berry/fuchsia/plum per theme) is used exactly once per page, on the single primary call-to-action only — button fill, no other application. Never on navigation, body links, icons, secondary buttons, or decorative elements. If a page has no clear single primary action, the pop color is not used on that page at all — it does not default to any fallback role.

**Flagged alternative, reserved not adopted:** a pull-quote accent treatment (slim border or opening quotation mark) for the Saint-Exupéry quote specifically — narratively fitting given this session's philosophy resolution, but explicitly NOT to be combined with the CTA application on the same page if ever used. Would need its own separate page/context to avoid diluting the CTA's exclusivity. Not adopted, kept on record as a considered-and-set-aside option, not a live candidate.

**Applies uniformly across all three themes** (Warm/Dark/Neutral) once each ships — the CTA-only discipline, not the specific hex value, is the governing constraint. Same rule, three different pop hex values.

**Status: LOCKED, Pete-confirmed** — the same standard as `--urgency`'s Endemic-exclusivity. Build against this rule as settled.
