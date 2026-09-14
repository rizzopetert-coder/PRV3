# Session Handoff — MOB v4.303

Direct extract/reformatting of `tools/_mob.txt` Section 16's 2026-09-13
closeout entry. Section 16 is authoritative; this file is a portable copy
for quick reference at the start of the next session, not an independent
record.

## One-line summary

Priority Queue item 2 (`built_to_fail`'s 16-profile ripple from
`f88a7c2`) is **CLOSED**. Confirmed local one-state substitution, not a
global/systemic scoring dependency — report-only investigation, no fix,
no build.

## Root cause, confirmed

All 16 flipped profiles trace to exactly one displaced state —
`invisible_performance_management` (IPM) — which was Aptitude-dominant
before `f88a7c2` re-authored it onto Authority. `built_to_fail` (the
taxonomy's only other strong Aptitude attractor, untouched throughout,
byte-identical vector/salience and byte-identical own score before and
after in all 16 cases) simply inherited the #1 spot once IPM moved
off-axis.

- **Ruled out structurally:** `rank_states()` (`engine/accumulation.py:524-594`)
  computes every state's score in isolation — no percentile/softmax/
  population-relative step. One state's score cannot depend on another's
  by construction.
- **Not a new mechanism:** `prompts/scd-wcs-remediation-tracker.md`'s
  Stage 3 already named this exact pattern for one profile
  (`the_exposed`) and explicitly declined to chase it further. This
  investigation enumerates the other 15.
- **No overlap with the rank-3 cluster** (item 5): confirmed neither
  `built_to_fail` nor any of the 13 flipped-to states is a member. IPM
  itself only joined that cluster as a side effect of `f88a7c2` — a
  separate fact, unrelated to this ripple's mechanism.
- Two extra flipped rows (`the_arbitrary_standard`) are correctly
  excluded — that state's own-profile loss is the already-documented,
  separate primary_dimension desync mechanism (MOB v4.301).

## Updated Priority Queue

1. `built_to_fail` false-rank-1 baseline drift — CLOSED (v4.301).
2. `built_to_fail`'s 16-profile ripple from `f88a7c2` — **CLOSED, this
   session.** See root cause above.
3. AssemblyPanel/Phase-2-CTA merge — CLOSED (v4.302).
4. IPM's thin question-wiring — CLOSED (v4.302).
5. IPM/`the_founders_grip` vector duplicate — corrected record (v4.302),
   latent, no urgency.
6. Diagnostic result export (copy-as-text) — **SHIPPED**, this session.
7. Long-screenshot capture bug — root cause unconfirmed, not worth
   chasing given item 6 covers the real need.
8. Diagnostic back button — **single-step undo SHIPPED**, this session,
   question-by-question path only. Self-select path still has none —
   net-new feature request there, unscoped.
9. `_oh_is_small_employer()` — built, not wired in.
10. NAICS-vs-"Manufacturing & Industrial" mapping gap (OH) — documented
    approximation, revisit only if wired into a real pricing path.
11. Quarterly Step-Back — due next week per Pete's correction (not
    overdue).

**Note on this handoff's scope:** Pete's task for this closeout asked
specifically to correct item 2. Items 6 and 8's status lines were also
updated in this pass (both shipped earlier the same session, by direct
commits already pushed) — flagged here rather than left stale, not a
silent scope expansion.

## Files to attach next session, by likely task

- **Always:** `tools/_mob.txt` (current version), `CLAUDE.md`.
- **If picking up the self-select path's back button (item 8):**
  `web/app/diagnostic/page.tsx`, `web/context/SelfSelectionContext.tsx` —
  needs product scoping first (which phase does it return to, does it
  preserve or clear prior selections).
- **If revisiting the long-screenshot bug (item 7):** only if Pete
  confirms the copy-as-text export doesn't fully cover the need.
- **If wiring `_oh_is_small_employer()` into a real pricing path:**
  `engine/friction_tax.py`, `engine/data/intake.py`.
- **If running the Quarterly Step-Back:** no specific files — full
  project assessment per the dual-sourced format.
