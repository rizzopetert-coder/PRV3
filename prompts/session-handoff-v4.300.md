# Session Handoff — MOB v4.300

Direct extract/reformatting of `tools/_mob.txt` Section 16's 2026-09-11
closeout entry. Section 16 is authoritative; this file is a portable copy
for quick reference at the start of the next session, not an independent
record.

## One-line summary

`damages_cap_treatment` Phase 2c (ME), listed gated at the prior closeout
on primary-source re-verification of its own flagged 15+ employee tier
breakpoints, was re-verified directly against mainelegislature.org this
session and built — data population only, zero engine logic change, same
shape as Phase 2a's AR/DE/TN. **This closes the entire `damages_cap_treatment`
Phase 2 initiative:** 2a (7 states) shipped earlier this session, 2b (OH)
shipped at the prior closeout, 2c (ME) shipped now.

## Shipped this session

**`damages_cap_treatment` Phase 2c (ME)** — confirmed before building
(not assumed) that ME sat at the exact generic `state_specific_tiers`
fallthrough Pete flagged, same "before" state OH was in — zero engine
logic changes needed, only a citation-comment correction.

Two corrections to the prior citation, both confirmed against primary
source (mainelegislature.org, current through Oct. 1, 2025):
1. 5 M.R.S. §4613(2)(B)(7) and (8) are two separate remedies, not one
   joint provision as the prior citation cited them ("(7)-(8)"). (7) is
   civil penal damages (non-employment/≤14-employee cases, tiered by
   violation order). (8) is the real employment tier table (15+
   employees, tiered by headcount). Split into two citations.
2. The prior comment's "top bracket $500,000" claim was wrong — that's
   the 201-500 tier's own figure. The real top bracket (501+) is
   **$1,000,000**. Corrected against the full four-tier table: $100,000
   (15-100) / $300,000 (101-200) / $500,000 (201-500) / $1,000,000
   (501+).

Two unmodeled carve-outs added, stated by the statute itself:
§4613(2)(B)(8)(f) (doesn't limit 42 U.S.C. §1981 recovery, itself
uncapped — real stacking exposure) and (8)(h) (tier caps don't apply to
disparate-impact-only claims). `is_floor=True` (already automatic) is
the caveat mechanism for both, same semantics as TX's own carve-out.

Tests: six boundary-headcount checks at ME's real tier edges (100/101,
200/201, 500/501), one Cluster 4b check, one aggregate-shape check.
Suite: `tools/test_friction_tax.py` 179 → 188. Full 11-script suite: 900
→ 909.

Commits `d7a775d`, `404c2f8`, `92f7262`, `1b89507`. Pushed, live — API
redeploy confirmed READY, live round trip returned 401 (clean auth
rejection, not 500).

## Status: damages_cap_treatment Phase 2 — fully shipped

All 9 `state_specific_tiers` states from the original Phase 1 deferral
are now either fully resolved (`QUALITATIVE_ONLY` for OH) or carry an
accurate, source-verified citation comment documenting their real
statutory mechanics, even where the dollar figures remain unconsumed by
pricing logic (AR/DE/TN/TX/MD/MO/CO/ME).

## Updated Priority Queue

1. `built_to_fail` false-rank-1 baseline drift (52 → 80) — needs its own
   dedicated investigation.
2. AssemblyPanel/CTA merge (Option C) — design pass, not urgent.
3. `invisible_performance_management` thin question-wiring — low
   priority, revisit if the calibration bar tightens.
4. `invisible_performance_management`/`the_founders_grip` vector
   duplicate — latent, no urgency.
5. `_oh_is_small_employer()` — built and tested, not wired in. Revisit
   when a real OH pricing path is scoped.
6. NAICS-vs-"Manufacturing & Industrial" mapping gap (OH) — documented
   approximation, revisit only if wired into a real pricing path.
7. **Quarterly Step-Back** — last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.

(`damages_cap_treatment` Phase 2 — 2a, 2b, and 2c — is now fully shipped
and dropped from this list entirely.)

## Files to attach next session, by likely task

- **Always:** `tools/_mob.txt` (current version), `CLAUDE.md`.
- **If picking up the `built_to_fail` false-rank-1 drift investigation:**
  `tools/calibration_runner.py`, `engine/data/salience.py`.
- **If picking up the AssemblyPanel/CTA merge (Option C):**
  `web/app/diagnostic/page.tsx`, `web/components/AssemblyPanel.tsx`.
- **If wiring `_oh_is_small_employer()` into a real pricing path:**
  `engine/friction_tax.py`, `engine/data/intake.py` (if net_worth/
  economic_loss ever get added).
- **If running the overdue Quarterly Step-Back:** no specific files —
  full project assessment per the dual-sourced format (CLAUDE.md's own
  Quarterly Step-Back section).
