# Session Handoff — MOB v4.317

Direct extract/reformatting of this session's Section 16 entry (MOB v4.316 -> v4.317, terminal
Claude Code, continuation session). Section 16 is authoritative; this is a portable copy for quick
reference, not a second independent record.

## What happened, in sequence

**1. Service tier landing pages + persistent sidebar.** New layout-level `ServiceSidebar.tsx`,
mounted in `web/app/layout.tsx` wrapping `{children}` directly. Renders a four-section stacked
sidebar on every route except `/diagnostic` — confirmed necessary via direct read of
`AssemblyPanel.tsx` (sticky w-72 aside) and `StateDrawer.tsx` (fixed w-80 drawer), both already
claiming the right edge there and both switching to Vaul bottom sheets on mobile. On
`/diagnostic`, collapses to a discreet "SERVICES" trigger. **A first `fixed`-position attempt was
wrong** — visibly overlapped AssemblyPanel's sticky heading once Phase 2 rendered, caught by live
browser verification, not assumed correct from code alone. Rebuilt as an in-flow thin strip below
NavBar instead, removing the collision by construction; re-verified clean through a real Phase 2
selection flow. First Call's sidebar section carries a permanent `bg-rust` fill at all times — a
deliberate, Pete-approved, sidebar-scoped exception to `--color-rust`'s standing Endemic-severity
reservation elsewhere in the product (unchanged everywhere else). Verified live across Warm, Dark,
and Neutral themes by screenshot, not contrast math alone. `/about/services` shrunk to a brief
overview; its four section ids flagged as a live dependency (97 real `/book/toc` badge links)
*before* editing, and kept unchanged on Pete's explicit confirmation.

**2. Route renaming (Fix 1).** `/groundwork` -> `/people-tactics-and-strategy`,
`/development` -> `/training-and-development`, `/advisory` -> `/executive-advisory`
(`/first-call` unchanged) — Pete's explicit choice, route matches the final commercial name
literally. All internal links updated; `NavBar.tsx`/`WayfindingGrid.tsx` confirmed to carry zero
references. Old routes confirmed live to 404 cleanly. **Mid-task clarifying question asked and
answered:** sidebar/landing-page visible labels still read Groundwork/Development/Advisory (an
earlier-approved naming) while routes became the engine's commercial slugs — Pete confirmed
unifying the visible labels too.

**3. Commercial-name correction (Fix 2), kept independent of Fix 1.**
`ENGINE_TO_COMMERCIAL_NAME` values corrected: "People Tactics and Strategy" -> "People Tactics &
Strategy" (ampersand), "Intervention" -> "First Call". Dict keys and every engine-internal routing
use of "Intervention" (`STATE_CAUSATION_OVERRIDES`, `engine/data/states.py` defaults) explicitly
untouched — verified by classifying every remaining occurrence. All 19 `RESOLUTION_FALLBACK_COPY`
entries (12 single + 7 compound — **flagging: actual count is 19, not 26 as stated in the task
brief; 19 matches this session's own earlier MOB record**) updated, mirrored exactly in
`web/lib/resolution-family.ts` and `web/lib/types.ts`. **A stated fact in the brief didn't hold
up:** a hardcoded `getPrimaryFamily()` fallback the brief pointed at no longer exists anywhere
(confirmed via repo-wide grep) — no edit was forced to match it. **Two additional real hardcoded
occurrences** found via the requested "anywhere else in web/" search, beyond the brief's file
list: `web/data/orientation-copy.ts`'s `RESULTS_FAMILY_DETAIL` (a silent-fallback risk — a stale
key there degrades every First-Call-routed result to generic copy without erroring) and
`web/components/DiagnosticFixturePicker.tsx` (caught twice — search, then `tsc` itself). Two
published book essays corrected mechanically (ampersand spelling only, zero voice change).

**`/about/services`' 4 anchor ids left deliberately UNCHANGED** (`#people-tactics-and-strategy`,
`#training-development`, `#intervention`, `#executive-advisory`) — decoupled from both the new
route slugs and the corrected display names, since `book/toc`'s `RESOLUTION_FAMILY_ANCHORS` links
97 real badges to these exact ids. **Flagging explicitly:** a future session should not "fix" this
apparent id/label mismatch without also updating book/toc's own map.

**Correcting the record on the disputed "Session 47 -> Intervention" entries.** Section 1's "Five
service names" and "Resolution service renaming" tables corrected in place with a dated inline
note (original S47 record left unedited — it was accurate when written). **Pete's final, confirmed
standing name set:** People Tactics & Strategy, Training & Development, First Call, Executive
Advisory — a deliberate PARTIAL adoption of the S47 set, retaining First Call over "Intervention."
Full locked-decision record in Section 14 (new row this session).

**4. First Call intake form — Personnel disclaimer em-dash fix.** Two plain sentences, zero em
dashes, matching the standing copy rule. Verified live.

## Verification, all real

Full 11-script engine suite pass; `tools/test_resolution_families.py` 119/119; `tsc --noEmit`
clean; vitest 99/99 (full 57-state gold-master table included); 175-profile calibration
**171/175**, exact match to the documented baseline, confirmed unaffected. **Live output proof:**
called the actual `run_engine()` entrypoint end to end for `culture_drift` (real
Intervention-default state) — raw `resolution_routing` stayed `'Intervention'`, the same
translation function the live API layer calls now returns `'First Call'`. Route renames and
sidebar/landing-page display verified live in the browser across all affected routes.

## Open items carried forward

- `gh` CLI still not installed, local dev Upstash Redis credentials missing, Function Storage
  remediation not executed, Dropbox Sign provisioning unconfirmed — all unchanged from the prior
  closeout.
- Attorney-review gate and pilot-mechanism recommendation unchanged.
- Next Quarterly Step-Back due **2026-10-03**.
- **New:** full body copy for the four landing pages (beyond the approved sidebar teaser lines) is
  an explicit, separate follow-up pass, not started this session by design.
- This closeout's commit is still pending Pete's explicit dry-run review and go-ahead — nothing
  pushed yet as of this handoff.

## Files to attach next session, by likely task

- **Always:** `tools/_mob.txt` (current version, v4.317).
- **If picking up the four landing pages' full body copy:** `web/app/people-tactics-and-strategy/page.tsx`, `web/app/training-and-development/page.tsx`, `web/app/executive-advisory/page.tsx`, `web/app/first-call/page.tsx`, `web/components/ServiceSidebar.tsx` (the approved teaser copy lives here).
- **If touching resolution_family again:** `engine/resolution_families.py`, `web/lib/resolution-family.ts`, `web/lib/types.ts` — read the commercial-name-correction comments in each before changing anything, they document exactly what's raw-engine-key space vs. commercial-name space.
- **If touching `/about/services` or `/book/toc`'s badges:** `web/components/ServicesPageContent.tsx`, `web/app/book/toc/page.tsx` (`RESOLUTION_FAMILY_ANCHORS`) — the anchor-id/display-name decoupling is load-bearing, read the comments before renaming anything.
- **If resuming the attorney-review gate or pilot mechanism:** the Step-Back #4 docs (`prompts/prv3-quarterly-step-back-2026-09-19-cc-independent.md`, `prompts/prv3-quarterly-step-back-2026-09-19-reconciled.md`).
- **If the next Quarterly Step-Back is due:** same two Step-Back #4 docs as the last-confirmed baseline.

## MOB version confirmation

Header (`tools/_mob.txt`) reads `MOB v4.317`. CLAUDE.md's Key References table updated in the
same pass (v4.316 -> v4.317).
