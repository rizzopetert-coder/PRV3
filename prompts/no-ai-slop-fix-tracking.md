# No-AI-Slop Remediation — Tracking

Governing decision (Pete, this session): keep the shared structural skeleton
(diagnostic-signs triad, CTA block) — vary execution, don't eliminate the
template. Locked MOB em-dash standard governs: ≤8 per piece, not the audit
tool's own ≤3 default.

## Fixed this session (8 files, committed pending CC pass)

| File | Fix |
| --- | --- |
| toxic-culture.md | verbatim-duplicate kicker → piece-specific (values-poster image) |
| silosolation.md | verbatim-duplicate kicker → piece-specific (email-chain image) |
| everyone-is-defensive-and-no-one-knows-why.md | near-verbatim triad → piece-specific (candor imagery); em-dash 12→8 |
| the-room-that-never-pushes-back.md | near-verbatim triad → piece-specific (room/meeting imagery); em-dash 10→8 |
| built-for-comfort.md | em-dash ~21→7; "Every organization has that window..." kicker → piece-specific |
| one-exception-at-a-time.md | em-dash 17→4; same kicker → piece-specific |
| why-blaming-the-person-almost-never-fixes-the-problem.md | 4 weasel-attribution claims → named/verified citations (Mitchell & Wood 1980; Swift, Moore, Sharek & Gino 2013; Heinrich 1931; Blume, Ford, Baldwin & Huang 2010; Senge 1990); em-dash 11→7 |
| anchor.md | throat-clearing opener removed; faux-insight header renamed ("The Risk No One Talks About" → "How Anchors Fail"); two rhetorical self-answered-question setups rebuilt |

**New citations from the why-blaming fix need to actually land in
book-citations.ts** — not yet done, flagged for CC.

## Known cross-file duplicate not yet fully resolved

"Every organization has that window. Most organizations are in it right
now." — per the original audit, shared near-verbatim across 5 of 6
case_pattern pieces in batch 3. Two fixed (built-for-comfort.md,
one-exception-at-a-time.md), each given a distinct piece-specific ending.
**Three more likely affected** — batch 3's case_pattern files:
what-the-organization-decided-he-was-worth.md, the-first-one-out-the-door.md,
the-resignation-that-ended-a-department.md (exact set needs confirming
against the live files, not assumed from the audit summary alone). Fix
these three together, in the same pass, so the five endings are checked
against each other for accidental new echoes — not just against the
original line.

## Proposed next phase — mechanical pre-screen before manual review

Claude Code to run a grep-based audit (not a rewrite) across the remaining
~79 /book files and produce a structured per-file report:

1. Em-dash count per file — flag any file >8 (the locked cap, not the
   audit tool's ≤3 default).
2. Exact or near-exact duplicate sentences/closing lines shared across
   2+ files — full list, not just the ones already known.
3. Weasel-attribution phrases — "research shows," "a study found,"
   "studies have found," or similar, with no named source within the
   same sentence or the one following it.
4. Binary-contrast ("X isn't Y. It's Z.") count per file — informational
   only, not a required fix per the skeleton-stays decision, but flag any
   file where the same file uses the construction 3+ times (reads
   templated within a single piece even under the "keep skeleton" ruling).

Output to prompts/no-ai-slop-mechanical-scan.md, one row per file, so the
manual-review queue (Claude.ai + Pete) can be prioritized by severity
rather than worked in file-listing order. Any weasel-attribution hits
route to a dedicated citation-verification pass before rewriting, per the
standing citation-accuracy discipline — no invented sources, real research
first, same as the why-blaming fix this session.

## Not yet touched

Everything outside the 8 files above and the 3 batch-3 kicker duplicates
named. Full batch breakdown and per-file finding counts are in
prompts/no-ai-slop-book-audit-findings.md (original audit, unchanged).
