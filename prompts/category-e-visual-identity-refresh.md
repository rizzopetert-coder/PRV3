# Category E — Visual Identity Refresh: Studio Direction

Status: DRAFT, exploratory. Pete has approved the overall direction and sequencing below, 
but no specific build has started and no Gemini review has happened yet. This is the concept 
brief, not an approved implementation.

## Context
Session opened on "the site looks sterile" (never reached until this session). Pete's specific 
critique: not colorful enough, not dynamic enough, the existing 4-axis quadrilateral 
visualization (OD-07's ConstellationField) "looks cheap and rudimentary." Site doesn't yet 
read as professionally designed.

## Governing constraint
Per the Principal Brief's central design principle (Saint-Exupéry — "nothing left to take 
away," discipline not minimalism-as-aesthetic) and the Core Reframe ("magnanimous but 
unflinching" — genuine empathy plus willingness to say hard things), the fix is NOT to add 
decoration to the existing locked 3-color palette. It's to raise execution/craft quality within 
the existing discipline. The rust-reserved-for-Endemic-severity rule stays untouched — that 
restraint is a genuine asset (when full color finally appears, it should land as a diagnosis, 
not a UI state change), not a limitation to work around.

## Sequencing, approved by Pete: start with Direction 1, then explore 2 and 3

### Direction 1 — Rendering quality upgrade (START HERE)
Keep the existing structural concept (4-axis weighted quadrilateral, vertices from real 
dimension_summary data, Constellation's dimensional-read model preserving P-11's dual-axis 
read) but rebuild the actual rendering quality: soft radial gradients instead of flat fill, 
vertex glow intensity scaled to real severity data, layering/depth so it reads as an instrument 
reading rather than a flat polygon. Lowest-risk path since no new visual metaphor needs 
validation — this tests whether "cheap-looking" is a craft-execution problem (most likely) 
rather than a concept problem.

Reactivates OD-07's dormant infrastructure (globals.css tokens, ThemeSwitcher.tsx — confirmed 
still present, not deleted, per the OD-07 rollback record) as the starting point rather than 
building from zero.

Also in scope for Direction 1: motion quality on the existing recede/resolve interaction 
mechanic. Likely currently linear/ease-out fades — upgrade to spring physics and layered 
timing (same felt-quality jump as Linear/Stripe-style interfaces), which is probably a smaller 
engineering lift than any new visual concept but may be the single biggest contributor to 
"feels professionally made."

### Direction 2 — Instrument-panel reframe (explore after 1)
Four radial gauges/dials (one per Aptitude/Authority/Alliance/Attitude dimension) instead of 
one combined quadrilateral. More visually rich by construction (four distinct rendered 
elements vs. one shape), ties directly to "diagnostic instrument" as literal metaphor. Higher 
build cost than Direction 1, more distinctive result.

### Direction 3 — Editorial/typographic hero (explore after 1)
De-emphasizes the geometric shape entirely. Hero of the results experience becomes bold, 
confident typography (state name, severity tier) rendered with real craft — the Output 
Precision principle ("a verdict that names one true thing is worth more than a report that 
names nothing new") taken literally, in the register of high-end data journalism (Bloomberg, 
the Pudding) rather than a chart. The quadrilateral/dial becomes a supporting element, not the 
star. Most differentiated option, biggest departure from what's built today.

## Next steps (not started)
1. Direction 1 build: needs Gemini architecture review before any code changes (structural/
   rendering-system decision, per standing protocol — no exceptions for visual-only changes 
   when they touch shipped architecture like OD-07's token system).
2. Directions 2 and 3 stay concept-level until Direction 1's result is seen — Pete's own 
   sequencing call, not a technical dependency.
3. No visual mockups exist yet for any direction. Actual rendering prototypes are Gemini/CC's 
   work once a direction is greenlit for real build, not something drafted in this file.
