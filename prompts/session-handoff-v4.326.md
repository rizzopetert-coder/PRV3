# Session handoff -- MOB v4.326 (2026-09-26, terminal Claude Code)

Derived from Section 16's 2026-09-26 closeout entry in `tools/_mob.txt`. If the two ever disagree, Section 16 is authoritative.

## Summary

hr-dx.com (hr_diagnostic) is live in Production on the two-project Vercel architecture (`prv-3` web + `prv3-engine` FastAPI), with a verified bundle-level airgap (hr-dx downloads no PR content), brand-safe results and AI text ("HR Consulting"), and the engine on `claude-sonnet-5`. `vercel-routing-migration` was fast-forward merged to `main` (`6c99e55..e368d8d`), which also ended a ~35-hour Production build freeze.

## Shipped this session

| Area | Commits |
|---|---|
| Route-group split, chrome off hr-dx | `f855d0a` |
| Chrome restored on PR `/diagnostic` + 404s, airgapped | `d301975` |
| Self-select physical route airgap (taxonomy) | `879103c` |
| Item E / item G / PrivateOutput brand code-split | `0643e8e` |
| F/I/J brand-safe results + AI text + backup copy | `ed46564`, `cd514c3`, `95a4491` |
| `vercel.json` engine rewrites removed | `e9eefd9` |
| Model `claude-sonnet-4-6` -> `claude-sonnet-5` + diagnostic log | `f278676` |
| TEMPORARY diagnostics removed | `e368d8d` |
| Fast-forward merge to `main`, Production verified | `e368d8d` |

## Vercel config state (non-git)

- `prv-3` `ENGINE_BASE_URL`: Production = `https://prv3-engine-peter-rizzos-projects.vercel.app` (stable prod alias). Preview (`vercel-routing-migration`) = branch engine alias. Preview (general) = stale `https://hr-dx-peter-rizzos-projects.vercel.app` (open item).
- `prv3-engine`: `ANTHROPIC_API_KEY` Production (`prv3-engine-production` key) + Preview (`vercel-routing-migration`). `ENGINE_SECRET` Production + Preview. SSO protection off project-wide (approved). Bypass secret rotated.
- Domains on `prv-3` Production: `hr-dx.com`, `www.hr-dx.com`, `principalresolution.com`, `www.principalresolution.com`, `prv-3.vercel.app`.

## Open

- Delete two Production test records from Redis `diagnostic-aggregate` (Pete -- see 13b for identification: industry "Technology", organization_size 175, top state "Built to Fail", completed_at ~2026-09-26T23:59:5xZ and ~2026-09-27T00:00:3xZ, remove with `LREM`). Unverified whether Preview shares the same Upstash instance.
- hr-dx "About this report" drawer copy revisit -- due now that F/I/J is live.
- Copy residuals: PR compound grammar ("A and B is built..."), occasional em-dash in AI-generated narrative questions.
- Stale general-Preview `ENGINE_BASE_URL`.
- `.claude/launch.json` unstaged local change (kept out of every commit).
- `vercel-routing-migration` branch still exists (fully merged, safe to delete -- Pete's call).
- `tools/diagnostic_fast_forward.py` rework-or-retire (stale intake, no narrative handling).
- Section 16 logging gap for the 2026-09-24/25 pre-session hr-dx work (flagged, not backfilled).

## Parked

Unchanged from Section 13b's "Explicitly parked" list.

## Dated items

- Next Quarterly Step-Back due **2026-10-03**.

## Files to attach next session

- Always: `tools/_mob.txt`.
- hr-dx copy work: `engine/output_synthesis.py`, `engine/narrative.py`, `engine/resolution_families.py`, `web/data/orientation-copy.ts`, `web/components/ResultsOrientationHR.tsx`, this file.
- fast_forward rework: `tools/diagnostic_fast_forward.py`, `web/app/api/diagnostic/session/start/route.ts`, `web/app/api/diagnostic/session/narrative/route.ts`.
- Vercel config changes: this file.
