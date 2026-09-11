# Session Handoff — MOB v4.298

Direct extract/reformatting of `tools/_mob.txt` Section 16's 2026-09-10
closeout entry (five workstreams shipped). Section 16 is authoritative;
this file is a portable copy for quick reference at the start of the next
session, not an independent record.

## One-line summary

Five workstreams this session, all shipped and live: (1) a 4-paragraph
homepage VoiceSection copy update; (2) `damages_cap_treatment` Phase 1 —
scoped at the prior closeout, actually built this session across two
rounds (initial build, then a corrections round after diff review caught
two real gaps); (3) `damages_cap_treatment` Phase 2 — a spec written
after finding real heterogeneity across the 9 `state_specific_tiers`
states, then Phase 2a (7 of those 9) built and shipped, with Phase 2b/2c
explicitly parked, not abandoned; (4) the mobile Phase 2 CTA collision
(flagged unconfirmed at the prior closeout) root-caused, fixed, and
verified live on both local and production; (5) EXP-IPM-02, a
low-priority calibration gap flagged at the prior closeout, root-caused
to a genuinely new bug class (stale question wiring, not a repeat of the
`primary_dimension` label bug) and fixed. All five shipped, committed,
pushed, and live — the two engine-touching items (`damages_cap_treatment`,
EXP-IPM-02) each triggered an automatic API redeploy, confirmed READY and
live-round-trip-verified (401 clean auth rejection, not 500) after every
push.

## Shipped this session

1. **VoiceSection homepage copy** — 3 → 4 paragraphs, inline link to
   `/book/methodology/symptoms-states-and-why-the-distinction-matters`,
   three named leadership behaviors given the hero's existing emphasis
   treatment. Verified live in both themes. Commits `87ccb57` + `bfe93fc`.
2. **`damages_cap_treatment` Phase 1** — built and corrected (two rounds).
   `resolve_damages_treatment()`, `_resolve_flat_cap()`, the
   `no_damages_available` federal-floor branch, `is_floor` (extended to
   `state_specific_tiers` in corrections), `flat_cap` clamp for
   FL/ID/KS/VA. Suite: 120 → 144 (`test_friction_tax.py`), 857 → 861
   (full suite). Commits `07325f3`, `2ef8278`, `59e2733`, `06f1e6a`,
   `c69a2f5`. API redeploy confirmed, live round trip 401.
3. **`damages_cap_treatment` Phase 2** — spec written
   (`prompts/damages-cap-treatment-phase2-spec.md`), Phase 2a (AR, DE, TN,
   MD, MO, TX, CO) built and shipped. New `is_combined_cap` field
   (MD/MO); TX needed zero code (already inherited `is_floor=True`); CO's
   federal-deferral via new `_co_drives_federal_tier_deferral()` helper,
   reusing existing constants/helpers, no new mechanism. Suite: 144 → 164
   (`test_friction_tax.py`), 861 → 881 (full suite). Commits `7f96739`,
   `7361aaf`, `54e5013`, `6707290`. API redeploy confirmed, live round
   trip 401. **Phase 2b (OH) and Phase 2c (ME) explicitly parked, not
   abandoned** — see Priority Queue below.
4. **Mobile z-index collision (AssemblyPanel vs. Phase 2 bar)** —
   root-caused (two `fixed bottom-0` full-width elements, no offset,
   higher z-index covering the lower one's CTA — confirmed click-
   unreachable via `elementFromPoint()`, not just visually crowded).
   Fixed via runtime-measured `ResizeObserver` + `SelfSelectionContext`
   (existing state pattern, no new mechanism). Verified at 375px/320px,
   locally and on production. Commits `85587c7`, `daf50b4`, `a4d94af`,
   `b8ef1a3`. No API redeploy (web/ only).
5. **EXP-IPM-02 (`invisible_performance_management`, moderate tier)** —
   `primary_dimension` confirmed still correct (no regression). Real bug:
   `Q35`, this state's only wired calibration question, had zero
   positive-authority options — stale from before the SCD-WCS
   re-authoring, in a data structure the earlier label-bug audit never
   checked. Registry-wide audit confirmed isolated (`the_paper_tiger`,
   `the_arbitrary_standard` both checked clean). Fixed by adding option
   `E` to `Q35`, confirmed zero behavior change for the question's other
   3 wired states. Suite: 170/175 → 171/175. Honest result: score 0.556 →
   0.770, rank 49 → 41 of ~58 — clears the prominence margin, but is NOT
   rank-1 and NOT structurally strong (still only 1 wired question).
   Commits `e8f82a8`, `b4a28e9`. API redeploy confirmed, live round trip
   401.

## New flagged items, not fixed

- `built_to_fail`'s false-rank-1 baseline drift: 52/175 (Phase 9) → 80/175
  (measured live this session). Unexplained, independent of anything
  fixed this session.
- `invisible_performance_management` / `the_founders_grip` share a
  byte-identical `dimensional_vector` and `salience_weights` — confirmed
  real. Not causing any current failure; a latent taxonomy question.
- `invisible_performance_management`'s thin question-wiring (1 of 52 core
  questions) — EXP-IPM-02 passes on margin, not distinctiveness.
- AssemblyPanel/Phase-2-CTA merge (Option C) — a future design pass to
  reduce the ~142px of stacked bottom mobile UI the shipped fix
  introduces. Not urgent.

## Updated Priority Queue

1. `damages_cap_treatment` Phase 2b (OH) — gated on intake-schema
   expansion (`economic_loss`, `net_worth`).
2. `damages_cap_treatment` Phase 2c (ME) — gated on primary-source
   re-verification of 5 M.R.S. §4613(2)(B)(7)-(8)'s 15+ tier breakpoints.
3. `built_to_fail` false-rank-1 baseline drift (52 → 80) — needs its own
   dedicated investigation.
4. AssemblyPanel/CTA merge (Option C) — design pass, not urgent.
5. `invisible_performance_management` thin question-wiring — low
   priority, revisit if the calibration bar tightens.
6. `invisible_performance_management`/`the_founders_grip` vector
   duplicate — latent, no urgency.
7. **Quarterly Step-Back** — last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.

## Files to attach next session, by likely task

- **Always:** `tools/_mob.txt` (current version), `CLAUDE.md`.
- **If picking up Phase 2b (OH):** `prompts/damages-cap-treatment-phase2-spec.md`,
  `engine/friction_tax.py`, and whatever governs the intake schema
  (`engine/data/intake.py`) — `economic_loss`/`net_worth` need to be
  added there before Phase 2b is buildable.
- **If picking up Phase 2c (ME):** `prompts/damages-cap-treatment-phase2-spec.md`
  and a chief-researcher-style verification pass against Maine's own
  statute (5 M.R.S. §4613(2)(B)(7)-(8)) — no engine file needed until that
  verification lands.
- **If picking up the `built_to_fail` false-rank-1 drift investigation:**
  `tools/calibration_runner.py`, `engine/data/salience.py`.
- **If picking up the AssemblyPanel/CTA merge (Option C):**
  `web/app/diagnostic/page.tsx`, `web/components/AssemblyPanel.tsx`.
- **If running the overdue Quarterly Step-Back:** no specific files —
  full project assessment per the dual-sourced format (CLAUDE.md's own
  Quarterly Step-Back section).
