"""
Closeout Step 2a: prompts/session-handoff-v4.328.md, derived from Section
16's 2026-09-27/28 entry (tools/_mob.txt). New file, never overwritten.

Usage: python tools/patch_session_handoff_v4_328.py --dry-run | --write
"""
import argparse, pathlib, sys

OUT = pathlib.Path('prompts/session-handoff-v4.328.md')
BODY = r'''# Session handoff -- MOB v4.328 (2026-09-27/28, terminal Claude Code)

Derived from Section 16's 2026-09-27/28 closeout entry in `tools/_mob.txt`. If the two ever disagree, Section 16 is authoritative. That entry is a reconstruction from `git log 7546b41..b9174e9`, session reports and deployed state, and its gaps are listed there and below.

## Summary

The report was redesigned for both brands (silent engine data, then a new layout and five new sections), four user-facing bugs and three copy passes were fixed, the causation override now drives the narrative as well as the pathway, and Call 2's timeout was doubled after a live worst case of 13.9s.

## Shipped this session

| Area | Commits |
|---|---|
| Narrative question "principal" read as a school | `9148aba` |
| TC labels: raw IDs and "Follow-up" | `50b573e` |
| Back after an early narrative erased the session | `a02e9b8` |
| Intake "Other" field focus loss | `f10d407` |
| TC-HRPOL-01, 20 TC rewrites, Q51 | `176e201`, `de4af1a`, `553cd27` |
| RESOLUTION_FALLBACK_COPY: 2 compounds, 11 em-dash fixes, zero left | `70f43bb`, `15ff117` |
| Phase 1 engine data (receipts, asset evidence, qualified states, cost comparison, three calls, web types) | `5792efd`, `fa10703`, `c80f877`, `2a0728e`, `0141a63`, `05afed3` |
| observation_valence (109 tagged: 103 liability, 6 neutral, 0 asset) | `12fa91d` |
| 13b asset-calibration item | `c9858cc` |
| Phase 2 (conditions list, airgap fix, condensed redesign, count cap, silhouette) | `1e8841f`, `c827e4a`, `ee6d9fc`, `911852c`, `cb65cdc` |
| Phase 3 (exec summary, tactical synthesis, receipts, cost comparison, asset strength) | `53d2d4d` |
| Phase 3 follow-ups (lead family, 2-3 sentences, split costs, Copy results) | `9c55695`, `6c56571`, `bc80783`, `aa1c646` |
| Causation override feeds synthesis (effective_resolution_family) | `79c419d` |
| hr drawer reads the overridden routing (vitest only) | `f990922` |
| Call 2 timeout 15s to 30s | `b9174e9` |

Live measurements: override fix verified on principalresolution.com (two tagged Production sessions, `the_uninitiated` plus diffuse, pathway and Call 1 both Training & Development). Call 2 worst case on hr-dx (`SMpZ1p2mHkjfT_-S0CLnC`, 40 of 40 flagged): call1 8.0s, call2 13.9s, call3 2.2s, 19.0s final request.

## Locked this session (Section 14)

- Report architecture: three AI calls with isolated inputs, a Call 2 or 3 failure degrades that piece only.
- Evidence rule: authored observation text only, valence-gated, never raw option text.
- All qualifying states pass through, collapsed by default.
- Condensed report: locked silhouette, count capped at "Several more" above 3.
- Pathway, Call 1 and backup copy all read effective_resolution_family.

Flagged, not moved: the 2026-09-26 hr-dx lock row (v4.326) sits in Section 16's table, not Section 14. Pete's call.

## Lapses

- `engine/tactical_synthesis.py`, `engine/exec_summary.py` and one vitest block were written directly, not through dry-run patch scripts.
- `c80f877` was committed past a failing `tools/test_contract.py`, fixed by `2a0728e` before any push.

## Discovery

Before `9c55695`, most hr-dx results were multi-state with an empty resolution family, so the drawer showed generic copy on most results until then.

## Open (13b)

- Asset calibration, Tier 1 (SEVER-* 0.25 seeding, Q18-E), logged `c9858cc`.
- Pass 2 content: about 325 missing observation texts (187 core, 138 SEVER-*), plus strength-phrased text for the asset-signal core answers (reported as 37, raw count 67, pin the scope). The asset strength panel shows no quoted evidence until this is written.
- ShareableOutput never live-tested (compile, lint and build only).
- 205 spaced dashes across 91 core questions.
- Driver steering: cannot reach `dueling_narratives` or an hr-dx override state.
- Narrative intake grounding: Gemini reviewed, `role_level` UNVERIFIED against the live intake, not built.
- Web routes' function duration limit unverified, check `prv-3` Functions settings in the dashboard.
- PR condensed verdict copy ("First Call is present in the work...").
- Condensed locked-indicators line still has an em-dash.
- `inaction_cost_low/high` still in the payload, mixed timeframe, not rendered.
- Executive summary voice ("Here's the thing:"), length fixed, voice not.
- `engine-preview` upkeep (merged `main` at `448a9ef`), `diagnostic-aggregate` holds many `is_test` records.
- 13b numbered priorities 1-5 unchanged.

## Parked

Unchanged from Section 13b's "Explicitly parked" list.

## Dated items

- Next Quarterly Step-Back due **2026-10-03**.

## Files to attach next session

- Always: `tools/_mob.txt`.
- Report work (both brands): `engine/contract.py`, `engine/main.py`, `engine/tactical_synthesis.py`, `engine/exec_summary.py`, `web/components/ReportDetails.tsx`, `web/components/ConditionsList.tsx`, `web/components/PrivateOutput.tsx`, `web/lib/output-text.ts`, `tools/test_phase1_report_data.py`.
- Pass 2 content: `engine/data/questions.py`, `engine/contract.py` (`_build_asset_evidence`, `_top_observation_texts`).
- Condensed report: `web/components/CondensedOutput.tsx`, `engine/resolution_families.py`.
- Asset calibration: `engine/data/questions.py`, `tools/calibration_runner.py`.
- hr-dx copy: `web/data/results-pathway-detail-hr.ts`, `engine/resolution_families.py`, `engine/output_synthesis.py`, `engine/narrative.py`.
- Driver steering: `tools/diagnostic_fast_forward.py`, `engine/data/states.py`, `web/lib/resolution-family.ts`.
- Vercel config: `prompts/session-handoff-v4.327.md`.

## Gaps in this reconstruction

- Production READY confirmed directly only for the engine deploys of `79c419d` and `b9174e9`.
- Pre-compaction live-test session IDs not all recoverable.
- Which vitest block was written directly is not pinned.
- "37 asset-signal answers" not reproduced (raw count 67).
- An earlier in-session report said "11 hr-dx runs" for the override check. The accurate count is 7 completed runs.

## Anything Pete should know

- Startup Protocol did not run at the start of this continued session. Run it in full next time.
- Test state at close: 13 Python suites pass (report-data 100/100), vitest 130/130, tsc clean.
'''

ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
a = ap.parse_args()
if OUT.exists():
    print(f'ERROR {OUT} already exists (additive only)', file=sys.stderr); sys.exit(1)
print(f'[{OUT}] {len(BODY.splitlines())} lines')
if a.dry_run:
    print('DRY RUN -- nothing written.')
else:
    OUT.write_text(BODY, encoding='utf-8'); print('WROTE')
