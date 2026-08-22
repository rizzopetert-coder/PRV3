# Session Handoff — MOB v4.221

Direct extract/reformatting of `tools/_mob.txt` Section 16's closeout entry for this session (SCD-WCS/primary-state ranking remediation, Phases 1-8), plus the companion Section 13a (Decision Register) and Section 13b (Session Priority Queue) updates. Section 16 is authoritative — this file is a portable quick-reference copy, not an independent record.

## Shipped this session

- **Rank-5 pilot** (commit `f11daf6`): `invisible_influence_architecture` / `planning_authority_gap` Alliance secondary differentiation, breaking the 3-way tie on every pairing.
- **paper_shield re-clustered** Authority → Aptitude (commit `7b6281f`), 12-candidate search, a genuine taxonomy-correctness fix, not a calibration fix.
- **Rank-6 pilot** (commit `cf2abeb`): `silosolation` Authority secondary, an honest partial fix (breaks the exact tie, doesn't achieve outright own-profile dominance).
- **the_arbitrary_standard's Authority secondary** (0.4 → 2.0, margin-searched, commit `e9a2750`), closing rank-6 entirely.
- **the_unsolved_problem re-clustered** Authority → Aptitude (commit `2deb461`, 9-candidate search), closing rank-3's one `resolution_family` outlier.
- **Ranks 1, 2, 3, 4, 11 fully diagnosed** (Program Phases 1-6) — all confirmed SAME-CLUSTER DIFF, real fixes deferred to Phase 8/Track 2 given low practical stakes.
- **Phase 8 (Track 2) run to completion**: full 58-state taxonomy census, plus paper_shield/the_unsolved_problem manufactured-dominance mitigations (commit `4c1a5de`), both closed to 0/175 false-rank-1 with zero regression.

Full 175-profile regression held at 171/175 (same 4 known pre-existing failures: `identity_erosion`, `invisible_burnout`, `leadership_deafness`, `the_untouchable`) throughout every change, verified against disk after every write.

## Key findings

- **Program Phase 2's cross-cluster asymmetry theory** — validated, refined once for dimension-crowding (rank-1's Attitude family being the taxonomy's largest).
- **A bidirectional `dimension_summary` confound** spanning 20 states across 4 phases — Authority-flavored profiles showing Attitude-dominant real signal and vice versa. Resolved practically via mechanical falsification testing (not raw ranking); root cause in `generate_answers()` still uninvestigated.
- **A full ripple audit** — 32 newly-surfaced winner instances across 6 clusters from this session's vector/salience changes, zero new counted regressions.
- **Phase 8's taxonomy-wide census**: 37 of 58 states share the standard "primary-only" salience template + liability-skewed vector (a systemic authoring pattern, not isolated states); only 6 actually manifest false-rank-1 dominance — `invisible_performance_management` (44), `built_to_fail` (41), `the_unsolved_problem` (19), `the_uninitiated` (17), `paper_shield` (9), `the_second_close` (5).
- **Whack-a-mole finding**: reducing any single dominant state's or any combination's own salience caps real payoff at 1 of 19 currently-masked states gaining anything, since suppressing the pool just promotes the next-most-extreme member. Confirmed NOT fixable via salience.

## Open / carried forward

- **4 pre-existing unresolved dominant states**: `built_to_fail`, `invisible_performance_management`, `the_uninitiated`, `the_second_close`. Confirmed not fixable via any single-state or combined salience lever tested — needs a future taxonomy-wide vector/template re-authoring project, a distinct and much larger undertaking than anything piloted this session. Not scoped further.
- **The confound's own root cause** — why `generate_answers()` cross-wires Authority/Attitude (and apparently Aptitude) — still uninvestigated, independent of any single cluster's remediation work.
- **Methodological gap**: full-175-profile false-rank-1 screening should become standard practice for any future re-vectoring work, alongside regression/collision checks. Neither `paper_shield`'s nor `the_unsolved_problem`'s original re-clustering searches could have caught their manufactured footprint without it — this measurement didn't exist until Phase 8.

## Parked (unchanged from before this session)

Confidentiality template field wording, attorney review of engagement agreement Section 3, LinkedIn 19-week content calendar, Category E Direction 2 (shelved). Do not resurface unless Pete reopens.

## Time-anchored

**Quarterly Step-Back due ~August 23, 2026** (2 days out as of this session's start) — not yet run. Prep material was pulled by a separate same-day session (visual-identity-philosophy question, real Principal Brief quotes, live `globals.css` token values, the Session 58 palette-lock MOB entry, a confirmed Production-only click-through checklist) — no decisions made yet, still queued.

## Files to attach next session

- **Always**: `tools/_mob.txt` (current version).
- **If resuming Track 2 / taxonomy-wide vector-template re-authoring work**: `prompts/scd-wcs-remediation-tracker.md` (full per-state disposition), `engine/data/salience.py` (`SALIENCE_PROFILES`), `engine/data/states.py` (`dimensional_vector`).
- **If resuming the ~August 23 Quarterly Step-Back**: the existing staged prep material from before this session (see Time-anchored above).
