# PRV3 Phase 2 Score Distribution v5
## Session 16 · Tiered Floor Active (Authority 1.00×, Others 1.15×) · 2026-05-13

---

## Run Configuration

| Field | Value |
|---|---|
| Floor | Tiered — Authority states: baseline × 1.00; all others: baseline × 1.15 |
| v4 → v5 changes | Auth HIGH sharpened (auth_l=0.60, all others=0.15, single-axis, Gemini concession). 10 cluster centroid traps differentiated (primary_l=0.45, others=0.20). Q10/Q25/Q30 reclassified. Tiered floor introduced. |
| Metric | Cosine similarity |
| Profiles run | 142 (48 HC-tier + 47 moderate + 47 weak) |
| Noise baseline source | tools/recalibrate_floor.py — N=1000, seed=42, Q01–Q39 (37 sampled) |
| First run with floor active | v4 used floor disabled (Option C, all zeros). v5 is first floor-gated calibration run. |

---

## Section 1 — Signal Delta Table (HC profiles, all 47 states)

Delta = HC target state cosine score − v5 cosine noise baseline.
Positive delta = focused signal exceeds noise. Negative delta = inversion (**INV**).
"Clears floor?" = score > floor (floor = baseline × tiered multiplier).

| State | Dimension | v4 baseline | v5 baseline | v5 floor | HC score | Delta | Clears floor? | Rank-1 correct? |
|---|---|---|---|---|---|---|---|---|
| decision_blindness | Alliance | 0.7260 | 0.7260 | 0.8349 | 0.8781 | +0.1521 | **CLEAR** | No |
| silosolation | Alliance | 0.7635 | 0.7635 | 0.8780 | 0.9028 | +0.1393 | **CLEAR** | No |
| the_arbitrary_standard | Alliance | 0.7635 | 0.7635 | 0.8780 | 0.8799 | +0.1164 | **CLEAR** | No |
| the_fracture | Alliance | 0.7260 | 0.7260 | 0.8349 | 0.8994 | +0.1734 | **CLEAR** | No |
| the_second_close | Alliance | 0.7635 | 0.7635 | 0.8780 | 0.8796 | +0.1161 | **CLEAR** | No |
| the_suppression_filter | Alliance | 0.7730 | 0.7341 | 0.8443 | 0.8887 | +0.1546 | **CLEAR** | Yes |
| built_to_fail | Aptitude | 0.7571 | 0.7571 | 0.8706 | 0.8496 | +0.0925 | FAIL | Yes† |
| the_dormant_talent | Aptitude | 0.7730 | 0.7627 | 0.8770 | 0.8482 | +0.0855 | FAIL | No |
| the_overloaded_manager | Aptitude | 0.7730 | 0.7627 | 0.8770 | 0.8243 | +0.0616 | FAIL | No |
| the_paper_tiger | Aptitude | 0.7571 | 0.7571 | 0.8706 | 0.8190 | +0.0619 | FAIL | No |
| the_undefined_role | Aptitude | 0.7789 | 0.7789 | 0.8957 | 0.8110 | +0.0322 | FAIL | No |
| the_unformed_leader | Aptitude | 0.7627 | 0.7627 | 0.8770 | 0.8482 | +0.0855 | FAIL | No |
| culture_drift | Attitude | 0.7730 | 0.7979 | 0.9176 | 0.8895 | +0.0916 | FAIL | No |
| groundhog_day | Attitude | 0.7979 | 0.7979 | 0.9176 | 0.8635 | +0.0657 | FAIL | No |
| identity_erosion | Attitude | 0.7730 | 0.7979 | 0.9176 | 0.9058 | +0.1079 | FAIL | No |
| invisible_burnout | Attitude | 0.7979 | 0.7979 | 0.9176 | 0.8635 | +0.0657 | FAIL | No |
| leadership_deafness | Attitude | 0.7730 | 0.7979 | 0.9176 | 0.9058 | +0.1079 | FAIL | No |
| narrative_lock | Attitude | 0.7730 | 0.7730 | 0.8889 | 0.7886 | +0.0157 | FAIL | No |
| the_basement_standard | Attitude | 0.7979 | 0.7979 | 0.9176 | 0.8635 | +0.0657 | FAIL | No |
| the_broken_compass | Attitude | 0.7979 | 0.7979 | 0.9176 | 0.8635 | +0.0657 | FAIL | No |
| the_burned_credibility | Attitude | 0.7979 | 0.7979 | 0.9176 | 0.8635 | +0.0657 | FAIL | No |
| the_culture_that_wasnt | Attitude | 0.7730 | 0.7979 | 0.9176 | 0.9058 | +0.1079 | FAIL | No |
| the_diversity_ceiling | Attitude | 0.7979 | 0.7979 | 0.9176 | 0.8635 | +0.0657 | FAIL | No |
| the_inside_track | Attitude | 0.7979 | 0.7979 | 0.9176 | 0.8635 | +0.0657 | FAIL | No |
| the_unlocked_door | Attitude | 0.7730 | 0.7979 | 0.9176 | 0.9058 | +0.1079 | FAIL | No |
| the_unreported_hazard | Attitude | 0.7730 | 0.7341 | 0.8443 | 0.7122 | -0.0220 **INV** | FAIL | No |
| the_untouchable | Attitude | 0.7954 | 0.7954 | 0.9147 | 0.9115 | +0.1160 | FAIL | Yes† |
| the_wrong_reward | Attitude | 0.7979 | 0.7979 | 0.9176 | 0.8635 | +0.0657 | FAIL | No |
| what_nobody_says | Attitude | 0.7730 | 0.7341 | 0.8443 | 0.7122 | -0.0220 **INV** | FAIL | No |
| decision_paralysis | Authority | 0.8431 | 0.8431 | 0.8431 | 0.8015 | -0.0417 **INV** | FAIL | No |
| dueling_narratives | Authority | 0.8431 | 0.8431 | 0.8431 | 0.8212 | -0.0219 **INV** | FAIL | No |
| heard_and_ignored | Authority | 0.8868 | 0.8944 | 0.8944 | 0.9449 | +0.0505 | **CLEAR** | No‡ |
| hr_capture | Authority | 0.8868 | 0.8944 | 0.8944 | 0.9422 | +0.0478 | **CLEAR** | No‡ |
| invisible_influence_architecture | Authority | 0.7730 | 0.7730 | 0.7730 | 0.6882 | -0.0847 **INV** | FAIL | No |
| leadership_continuity_risk | Authority | 0.8431 | 0.8431 | 0.8431 | 0.7968 | -0.0463 **INV** | FAIL | No |
| paper_shield | Authority | 0.7730 | 0.7730 | 0.7730 | 0.7180 | -0.0550 **INV** | FAIL | No |
| pay_exposure | Authority | 0.8431 | 0.8431 | 0.8431 | 0.8212 | -0.0219 **INV** | FAIL | No |
| the_exposed | Authority | 0.8868 | 0.8944 | 0.8944 | 0.9449 | +0.0505 | **CLEAR** | No‡ |
| the_founders_grip | Authority | 0.8868 | 0.8944 | 0.8944 | 0.9537 | +0.0593 | **CLEAR** | Yes |
| the_lost_map | Authority | 0.8431 | 0.8431 | 0.8431 | 0.8212 | -0.0219 **INV** | FAIL | No |
| the_pay_fog | Authority | 0.8431 | 0.8431 | 0.8431 | 0.8212 | -0.0219 **INV** | FAIL | No |
| the_policy_lag | Authority | 0.8431 | 0.8431 | 0.8431 | 0.8212 | -0.0219 **INV** | FAIL | No |
| the_tolerated_violation | Authority | 0.8868 | 0.8944 | 0.8944 | 0.9449 | +0.0505 | **CLEAR** | No‡ |
| the_unexamined_algorithm | Authority | 0.7730 | 0.7730 | 0.7730 | 0.7180 | -0.0550 **INV** | FAIL | No |
| the_uninitiated | Authority | 0.8431 | 0.8431 | 0.8431 | 0.8015 | -0.0417 **INV** | FAIL | No |
| the_unsolved_problem | Authority | 0.8868 | 0.8944 | 0.8944 | 0.9449 | +0.0505 | **CLEAR** | No‡ |
| transition_paralysis | Authority | 0.8431 | 0.8431 | 0.8431 | 0.8212 | -0.0219 **INV** | FAIL | No |

**Positive delta (signal exceeds noise): 33 / 47** (v4: 27/47)
**Negative delta (signal inversion): 14 / 47** (v4: 20/47)
**Floor cleared: 12 / 47** (Alliance: 6/6, Authority HIGH: 6/6, all others: 0)

† Rank-1 in raw cosine rankings, but FAIL floor → engine outputs `no_signal`.

‡ All 6 Authority HIGH states share the same vector (auth_l=0.60, others=0.15 — Gemini concession). All 5 tie in cosine score for heard_and_ignored / hr_capture / the_exposed / the_tolerated_violation / the_unsolved_problem HC profiles. The_founders_grip ranks 1 by intake-specific tiebreak.

---

## Section 2 — Tier Score Table by Dimension

Mean target state cosine score across HC profiles, by dimension.
Watch: HC mean vs. noise baseline mean. Authority still inverted overall (12 non-HIGH states below baseline).

| Dimension | HC mean | Moderate mean | Weak mean | v5 Noise baseline mean | v4 HC mean | v4 noise mean | HC > noise? |
|---|---|---|---|---|---|---|---|
| Authority | 0.8404 | 0.6762 | 0.5865 | 0.8485 | 0.8196 | 0.8460 | no |
| Attitude | 0.8556 | 0.6764 | 0.6174 | 0.7888 | 0.8297 | 0.7860 | YES |
| Aptitude | 0.8313 | 0.6749 | 0.5883 | 0.7626 | 0.8109 | 0.7669 | YES |
| Alliance | 0.8881 | 0.6619 | 0.6033 | 0.7461 | 0.8803 | 0.7526 | YES |

Note: Authority HC mean (0.8404) includes 12 unpatched centroid-trap states that score below baseline. The 6 Authority HIGH states have HC mean ~0.9446 (all CLEAR).

---

## Section 3 — Rank-1 Integrity Summary

Target at rank-1 = target state is the top cosine match in raw rankings.
Floor-qualified rank-1 = target state appears in engine output at rank-1.

| Profile type | Raw rank-1 correct | Floor-qualified rank-1 | Total | v4 count |
|---|---|---|---|---|
| HC (high_confidence + extreme) | 4 | 2 | 48 | 2 |
| moderate | 1 | 0 | 47 | 1 |
| weak | 1 | 0 | 47 | 1 |

**`the_unexamined_algorithm` rank-1 capture: 94 / 142 profiles** (centroid trap, no vector override — critical)
**`the_founders_grip` rank-1 capture: 22 / 142 profiles**

Top 6 rank-1 sink states across all 142 profiles (raw rankings):

| Rank | State | Count | v4 count |
|---|---|---|---|
| 1 | the_unexamined_algorithm | 94 | — |
| 2 | the_founders_grip | 22 | 25 |
| 3 | the_untouchable | 17 | 17 |
| 4 | the_suppression_filter | 4 | — |
| 5 | built_to_fail | 3 | — |
| 6 | the_second_close | 2 | 6 |

---

## Section 4 — Score Distribution Statistics

Min/max/mean/median are for the target state cosine score per profile.
"Above baseline" = target state score > v5 noise baseline.

### HC (high_confidence + extreme_high_confidence) (n=48)

| Stat | v5 value | v4 value |
|---|---|---|
| Min target score | 0.6882 | 0.8359 |
| Max target score | 0.9537 | 0.9115 |
| Mean target score | 0.8504 | 0.8916 |
| Median target score | 0.8635 | 0.9006 |
| Target score > noise baseline | 34 / 48 | 28 / 48 |
| Target score < noise baseline (inversion) | 14 / 48 | 20 / 48 |
| Raw rank-1 correct | 4 / 48 | 2 / 48 |
| Floor-qualified rank-1 correct | 2 / 48 | n/a |

### moderate (n=47)

| Stat | v5 value | v4 value |
|---|---|---|
| Min target score | 0.4699 | 0.6537 |
| Max target score | 0.8311 | 0.8333 |
| Mean target score | 0.6743 | 0.7384 |
| Median target score | 0.6826 | 0.7362 |
| Target score > noise baseline | 0 / 47 | 0 / 47 |
| Target score < noise baseline (inversion) | 47 / 47 | 47 / 47 |
| Raw rank-1 correct | 1 / 47 | 1 / 47 |

### weak (n=47)

| Stat | v5 value | v4 value |
|---|---|---|
| Min target score | 0.4435 | 0.6426 |
| Max target score | 0.6930 | 0.6930 |
| Mean target score | 0.6001 | 0.6901 |
| Median target score | 0.6275 | 0.6930 |
| Target score > noise baseline | 0 / 47 | 0 / 47 |
| Target score < noise baseline (inversion) | 47 / 47 | 47 / 47 |
| Raw rank-1 correct | 1 / 47 | 1 / 47 |

### all profiles (n=142)

| Stat | v5 value | v4 value |
|---|---|---|
| Min target score | 0.4435 | 0.6426 |
| Max target score | 0.9537 | 0.9115 |
| Mean target score | 0.7093 | 0.7742 |
| Median target score | 0.6930 | 0.7372 |
| Target score > noise baseline | 34 / 142 | 28 / 142 |
| Target score < noise baseline (inversion) | 108 / 142 | 114 / 142 |
| Raw rank-1 correct | 6 / 142 | 4 / 142 |

---

## Section 5 — Floor Analysis (New — First Floor-Active Run)

The 1.15× floor for non-Authority states blocks all Attitude and Aptitude signal. 17 Attitude states have positive deltas but fail because the floor is ~0.92 for baseline=0.7979 states. Alliance states clear because their baselines are lower (floor ~0.84–0.88) and their HC signals are strong.

| Dimension | Floor formula | Floor range | HC score range | Clears | Fails |
|---|---|---|---|---|---|
| Authority HIGH (6) | base × 1.00 | 0.8944 | 0.9422–0.9537 | 6 / 6 | 0 / 6 |
| Authority LOW (12) | base × 1.00 | 0.7730–0.8431 | 0.6882–0.8212 | 0 / 12 | 12 / 12 |
| Attitude (17) | base × 1.15 | 0.8443–0.9176 | 0.7122–0.9115 | 0 / 17 | 17 / 17 |
| Aptitude (6) | base × 1.15 | 0.8706–0.8957 | 0.8110–0.8496 | 0 / 6 | 6 / 6 |
| Alliance (6) | base × 1.15 | 0.8349–0.8780 | 0.8781–0.9028 | 6 / 6 | 0 / 6 |

**Floor threshold observation:** For Attitude states with baseline=0.7979, floor=0.9176. HC signals reach 0.86–0.91 — 15% above baseline would require 0.92. This gap is the binding constraint for all 17 Attitude states.

---

## Issues Flagged for Pete

**1. the_unexamined_algorithm centroid trap (critical)**
Authority state, `cluster_id=None`, no vector override in Session 16 patch. Default all-0.25 vector plus lowest floor among Authority states (0.7730 × 1.00 = 0.7730) makes it absorb 94/142 rank-1 slots. Must receive a vector override. Recommendation: authority_liability=0.45, others=0.20 (same pattern as differentiated cluster states).

**2. Attitude/Aptitude 1.15× floor too aggressive**
17 Attitude states and 6 Aptitude states all have positive HC deltas but fail the 1.15× floor. The floor requires 15% above noise — these states reach only 8–12% above. Options: (a) reduce floor multiplier for Attitude/Aptitude, (b) accept that only Alliance and Authority HIGH qualify in current calibration, (c) strengthen option contributions for Attitude/Aptitude.

**3. the_unreported_hazard and what_nobody_says — wrong axis assignment**
Both are Attitude states (primary_dimension="Attitude") but Session 16 patch gave them alliance_liability=0.45. HC profiles targeting them accumulate attitude_liability, which gives low cosine to their alliance-biased vectors. Both show INV (-0.0220). Needs correction to attitude_liability=0.45.

**4. Authority LOW inversions persist (12 states)**
12 Authority states (non-HIGH) still have no vector override. All default to [0.25,...,0.25] centroid. Their HC signals score below their floors. These were not in scope for the Session 16 patch. Full Authority differentiation is a future workstream.

**5. Authority HIGH identical vector — rank-1 ties**
All 6 Authority HIGH states share auth_l=0.60/others=0.15. Their HC profiles produce scores differing only by intake-driven axis modifiers. Rank-1 among the 6 is determined by tiebreak, not signal. Test expectations for individual Authority HIGH rank-1 cannot be met. Calibration pass/fail for these 6 states requires a revised test criterion or differentiated secondary fields.

---

*PRV3 Principal Brief governs. Pete confirms everything.*
*Phase 2 v5 distribution run executed Session 16 · 2026-05-13*
*Test suite: 402/0 at time of run.*
