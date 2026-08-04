# /diagnostic Visual Identity Reskin — Stages 4-5 Rescope

**Status:** Rescoped from commit evidence after the original plan was confirmed permanently
lost to compaction (commit `99e729a`). No surviving plan doc existed; this was reconstructed
by Claude Code from file-touch chronology and confirmed by Pete as trustworthy (no independent
memory either way). Distinct from the unrelated "Stage 1-4" numbering used for Path 1's Redis/
accumulation build (Session 71) -- that one is closed and unrelated.

## Confirmed history (not inference)

- **Stage 1** (likely, not formally labeled at the time): v1 palette (`paper`/`charcoal`/
  `slate`/`rust`) locked and rolled site-wide across 18 files, commit `0e13fa4`.
- **Stage 2** (likely): v2 token rename (`charcoal`->`ink`, `paper`->`field`, `font-display`->
  `font-serif`) proven on the homepage first, commit `f5c36ac`.
- **Stage 3** (confirmed complete): v2 tokens applied to `/diagnostic`'s primary flow -- three
  files: `DiagnosticFlow.tsx` (`290ce8d`), `page.tsx` (`478a2d0`), `PrivateOutput.tsx`
  (`a93afa8`).

## New finding this session: Stage 3's "complete" status has a live gap

`NavBar.tsx` is still on v1 tokens and is global -- it wraps every page, including the three
Stage-3-complete files. This means the diagnostic flow currently renders a v1-styled nav bar
on top of v2-styled page content in production right now. This is not a Stage 4/5 scope
question -- it's a bug in already-shipped work, being fixed immediately, separately from the
staged rollout below.

## Rescoped plan (working hypothesis, evidence-based, not a recovered original)

**Immediate, standalone (not staged):** Fix `NavBar.tsx` to v2 tokens now, independent of
Stage 4/5 sequencing, since it's currently visible on every page including the ones already
marked done.

**Stage 4:** `/diagnostic`'s remaining self-select-path supporting components, still on v1,
functionally part of the same surface Stage 3 already mostly finished: `AssemblyPanel.tsx`,
`SignatureCard.tsx`, `StateDrawer.tsx`, `ShareButton.tsx`, `ShareableOutput.tsx`.

**Stage 5:** The rest of the site, still on v1: `/about/*`, `/ask`, `/book/*`, `/share/[id]`,
`/dev/diagnostic-preview`. (NavBar removed from this stage's scope -- handled immediately per
above, not as part of Stage 5.)

## Rationale for this grouping

Matches the pattern already visible in the confirmed history: each stage moved from broader
scope to narrower, more load-bearing surfaces (whole site -> one proof-point page -> the
primary diagnostic flow), then logically continues to the diagnostic surface's remaining
supporting pieces before finishing the rest of the site. This is a reasonable inference from
the pattern, not a rediscovered plan -- if new evidence surfaces (e.g. Pete recalls something
that contradicts this grouping), revise this doc rather than treating it as locked history.

## Next steps

1. Fix `NavBar.tsx` to v2 tokens -- immediate, standalone.
2. Dry-run Stage 4 (5 files) per standing CC protocol, review before write.
3. Stage 5 after Stage 4 confirmed complete and reviewed.
