# Session handoff -- MOB v4.327 (2026-09-26/27, terminal Claude Code)

Derived from Section 16's 2026-09-26/27 closeout entry in `tools/_mob.txt`. If the two ever disagree, Section 16 is authoritative.

## Summary

Every hr-dx follow-up from the v4.326 closeout is closed: the six-item polish batch, the family-specific drawer copy with a plain "HR Consulting" Executive Advisory context, `prv-3` Previews moved off the Production engine onto a new `engine-preview` branch with its own Preview key, the dead key row removed, and the 2026-09-24/25 Section 16 gap backfilled.

## Shipped this session

| Area | Commits |
|---|---|
| `is_test` on aggregate records | `5d81c1c` |
| Compound-family grammar ("A with B") | `ce9ad29` |
| Narrative-question punctuation (prompt rule + guard) | `b675d9f` |
| fast_forward reworked into the permanent driver | `e836d79` |
| `.claude/launch.json` tracked | `7fbc77c` |
| hr-dx drawer copy + Executive Advisory context | `d60107c` |
| 13b driver answer-steering item | `5e1eda9` |
| `engine-preview` branch (empty build triggers) | `fdf3d60`, `e8fa02e` |

## Vercel config state (non-git)

- `prv-3` `ENGINE_BASE_URL`: Production = `https://prv3-engine-peter-rizzos-projects.vercel.app`. General Preview = `https://prv3-engine-git-engine-preview-peter-rizzos-projects.vercel.app`.
- `prv3-engine`: `ANTHROPIC_API_KEY` Production + general Preview (Pete-added). `ENGINE_SECRET` Production + Preview. SSO protection off project-wide (approved 2026-09-26). The dead branch-scoped key row is removed.
- `engine-preview` branch: long-lived, exists for the stable Preview alias. Refresh by merging `main` into it and pushing, not fast-forward. Do not delete while the Preview row points at it.
- Verified end to end: tagged Preview session through `engine-preview`, `is_fallback: false`, Anthropic 200 in that deployment's logs.

## Records

- Section 16 backfill for 2026-09-24/25 (reconstructed from git, reflog, and Vercel deployment records, gaps listed in the entry).
- CLAUDE.md step-back date corrected to 2026-10-03.

## Open

- Driver answer-steering: hr-dx structure, capability, and leadership pathways and the Executive Advisory context are verified by tests only, not live.
- Separate Upstash database for Preview: backlog, deferred by Pete.
- Untracked `uv.lock` (2026-09-24 pyproject work): keep or remove, Pete's call.
- 13b numbered priorities 1-5 unchanged.

## Parked

Unchanged from Section 13b's "Explicitly parked" list.

## Dated items

- Next Quarterly Step-Back due **2026-10-03**.

## Files to attach next session

- Always: `tools/_mob.txt`.
- hr-dx copy work: `web/data/results-pathway-detail-hr.ts`, `engine/resolution_families.py`, `engine/output_synthesis.py`, `engine/narrative.py`.
- Driver steering: `tools/diagnostic_fast_forward.py`, `engine/data/states.py`, `web/lib/resolution-family.ts`.
- Vercel config changes: this file.

## Anything Pete should know

- Startup Protocol did not run at the start of this continued session. Run it in full next time.
- `diagnostic-aggregate` holds this session's tagged test records (at least 16 Production, 1 Preview). Exclude `is_test: true`.
