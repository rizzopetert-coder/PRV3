# Session Handoff — MOB v4.302

Direct extract/reformatting of `tools/_mob.txt` Section 16's 2026-09-13
closeout entry. Section 16 is authoritative; this file is a portable copy
for quick reference at the start of the next session, not an independent
record.

## One-line summary

Two builds from this session's earlier report-only investigation are now
committed, pushed, and live: the AssemblyPanel/Phase-2-CTA merge
(Option C, web-only) and Q05's new option E wiring
`invisible_performance_management`'s second question (engine-touching,
redeploy confirmed READY, live round-trip 401). Mid-session, Pete reported
two new bugs from a real device (Pixel 10 Pro, Chrome mobile); both were
investigated and confirmed unrelated to the pending push — reported
plainly, neither fixed. The IPM/`the_founders_grip` vector-duplicate
record is corrected.

## Shipped this session

**Build 1 — AssemblyPanel/Phase-2-CTA merge (Option C).** Commits
`6663a3e`, `00910a4`, `e9e8562`. Two stacked mobile bars (141.4px
combined) become one (65px). Verified live at 375px/320px. Web-only, no
redeploy needed. **Shipped without the Gemini architecture-gate review**
this project's standing protocol calls for — Pete confirmed push-as-is
given full live functional verification and low architectural stakes,
not a silent skip.

**Build 2 — Q05 option E (IPM's second question).** Commits `369c1c9`,
`d7d90ff`, `ff813d9`, `9cf694e`. Same fix shape as Q35's own option E.
Zero regression confirmed to Q05's original 4 options/6 target states.
**Live round-trip confirmed this session:** deployment
`prv-3-1ncy9mvmm-peter-rizzos-projects.vercel.app` READY, live
`POST /api/engine` → 401 (clean auth rejection, not 500).

**IPM's own-profile capture rate remains 0/3 — still open.** This fix
closed the wiring-density gap (1 of 52 core questions → 2), not the
deeper calibration question.

**Two process slips, both self-caught before any commit:** a direct Edit
to `questions.py` (bypassed the patch-script discipline, reverted and
redone properly) and a `git stash` that stashed the entire working tree
instead of one file (caught immediately, restored via `git stash pop`,
confirmed nothing lost).

**Part B — IPM/`the_founders_grip` duplicate record corrected.**
Confirmed deliberate at ship time (the `f88a7c2` commit's own comment
says so), part of an already-diagnosed 8-state rank-3 cluster
(`prompts/scd-wcs-remediation-tracker.md`), confirmed latent not live.

**Mid-session bug investigation, both reported, neither fixed:**
- **Bug 1 (long screenshot):** inner-scroll-container mechanism ruled
  out (natural document flow, confirmed live). Fixed-element mechanism
  present but modest (1–2 visible fixed elements per phase; Build 1
  reduced Phase 2's count from 3 to 2). No clean repro obtainable in
  this environment. Not fixed — would require restructuring
  persistent nav, which routes through the architecture gate first.
- **Bug 2 (back button):** confirmed never built on either diagnostic
  path — net-new feature request, not a regression.

## Updated Priority Queue

1. `built_to_fail` false-rank-1 baseline drift — CLOSED (v4.301).
2. `built_to_fail`'s 16-profile ripple from `f88a7c2` — confirmed real,
   mechanism not identified, needs its own dedicated session.
3. AssemblyPanel/Phase-2-CTA merge — CLOSED, shipped and live.
4. IPM's thin question-wiring — CLOSED, shipped and live. Own-profile
   capture rate (0/3) remains open under item 5.
5. IPM/`the_founders_grip` vector duplicate — corrected record, latent,
   no urgency.
6. **NEW** — Diagnostic result export (copy-as-text). Proposed by
   Claude.ai, unscoped. Sidesteps the screenshot bug entirely and serves
   Pete's actual underlying need (getting output to Claude for review).
7. **NEW** — Long-screenshot capture bug. Root cause unconfirmed, no
   repro obtainable here. Not worth restructuring nav to chase given
   item 6 covers the real need. Revisit only if item 6 doesn't fully
   cover it.
8. **NEW** — Diagnostic back button. Confirmed never built either path.
   Needs product scoping before any build.
9. `_oh_is_small_employer()` — built, not wired in.
10. NAICS-vs-"Manufacturing & Industrial" mapping gap (OH) — documented
    approximation, revisit only if wired into a real pricing path.
11. Quarterly Step-Back — due next week per Pete's correction (not
    overdue).

## Files to attach next session, by likely task

- **Always:** `tools/_mob.txt` (current version), `CLAUDE.md`.
- **If picking up the `built_to_fail` 16-profile ripple:**
  `tools/calibration_runner.py`, `engine/data/states.py`,
  `engine/data/salience.py` — expect to need git worktrees at `322ea93`
  and `f88a7c2` again for per-profile winner diffs.
- **If scoping the diagnostic result export (item 6):**
  `web/components/PrivateOutput.tsx` (the output page), `web/app/
  diagnostic/page.tsx`.
- **If scoping the diagnostic back button (item 8):**
  `web/app/diagnostic/page.tsx`, `web/components/DiagnosticFlow.tsx`,
  `web/context/SelfSelectionContext.tsx`.
- **If wiring `_oh_is_small_employer()` into a real pricing path:**
  `engine/friction_tax.py`, `engine/data/intake.py`.
- **If running the Quarterly Step-Back:** no specific files — full
  project assessment per the dual-sourced format (CLAUDE.md's own
  Quarterly Step-Back section).
