# PRV3 Phase 2 Score Distribution v12
## Session 19 · signal-driven calibration — first answer-populated run · 2026-05-18

---

## Run Configuration

| Field | Value |
|---|---|
| Change from v11 | calibration_runner.py refactored: _neutral_option() fixed to use absolute sum of all dimensional fields (not signed liability-only sum). _conditional sentinel values skipped. --signal flag added. Mode label updated. |
| Floor multipliers | Authority 1.00× (LOCKED Session 16) / non-Authority 1.08× |
| Profiles | 142 (47 HC + 47 moderate + 47 weak + 1 extreme HC) |
| Baseline | v11 (mean 0.8011) — unchanged, Monte Carlo confirmed stable |

---

## Section 1 — Result

| Metric | v10 | v11 | v12 | Delta v11→v12 |
|---|---|---|---|---|
| Total pass | 3/142 | 3/142 | 14/142 | +11 |
| HC pass | 0/47 | 0/47 | 0/47 | 0 |
| Moderate pass | 0/47 | 0/47 | 5/47 | +5 |
| Weak pass | 3/47 | 3/47 | 9/47 | +6 |

**Passing states (v12, 11 states):**

| State | Pass count | Passing profile type |
|---|---|---|
| `built_to_fail` | 1/3 | weak |
| `culture_drift` | 1/3 | moderate |
| `decision_paralysis` | 1/3 | weak |
| `leadership_continuity_risk` | 2/3 | weak + moderate |
| `the_founders_grip` | 1/3 | weak |
| `the_policy_lag` | 1/3 | weak |
| `the_undefined_role` | 1/3 | weak |
| `the_unexamined_algorithm` | 2/3 | weak + moderate |
| `the_unformed_leader` | 1/3 | weak |
| `the_uninitiated` | 2/3 | weak + moderate |
| `transition_paralysis` | 1/3 | weak |

**Confirmed: `paper_shield` is no longer the dominant sink.** It appears 0/3 passing in v12 (was 1/3 weak pass in v11). Signal-driven neutral selection broke its geometric capture mechanism. The `_neutral_option()` fix — using absolute sum of all dimensional fields — prevents F-options (asset-only) from being treated as maximally neutral, which was injecting spurious asset signals into moderate and weak profiles that aligned well with paper_shield's cross-dimensional vector.

**New dominant sink: `the_unexamined_algorithm`** (auth_l=0.35, apt_l=0.25, others=0.15, floor=0.8926 × Auth 1.00× = 0.8926). Absorbs rank-1 from built_to_fail (3/3), culture_drift (2/3), decision_blindness (2/3), dueling_narratives (2/3), heard_and_ignored (2/3), hr_capture (2/3+), and many others. Its cross-dimensional (Authority + Aptitude) vector captures profiles where best_option_for_state() across all 39 questions accumulates mixed Authority/Aptitude signal — common because many questions carry dual-dimension seedings.

**States with 0/3 across all profile types (36 states — flagged):**
decision_blindness, dueling_narratives, groundhog_day, heard_and_ignored, hr_capture, identity_erosion, invisible_burnout, invisible_influence_architecture, leadership_deafness, narrative_lock, paper_shield, pay_exposure, silosolation, the_arbitrary_standard, the_basement_standard, the_broken_compass, the_burned_credibility, the_culture_that_wasnt, the_diversity_ceiling, the_dormant_talent, the_exposed, the_fracture, the_inside_track, the_lost_map, the_overloaded_manager, the_paper_tiger, the_pay_fog, the_second_close, the_suppression_filter, the_tolerated_violation, the_unlocked_door, the_unreported_hazard, the_unsolved_problem, the_untouchable, the_wrong_reward, what_nobody_says.

---

## Section 2 — Sink Character Shift

| Version | Dominant rank-1 sink | Type | Floor | Mechanism |
|---|---|---|---|---|
| v9 | `the_uninitiated` | Authority MEDIUM | 0.8431 | Geometric — auth_l=0.40 |
| v10 | `paper_shield` | Authority LOW/CLUSTER | 0.8790 | Cross-dim — auth_l=0.35, all_l=0.25; F-option neutral injection |
| v11 | `paper_shield` | Authority LOW/CLUSTER | 0.8785 | Same — neutral fix not yet applied |
| v12 | `the_unexamined_algorithm` | Authority LOW/CLUSTER | 0.8926 | Cross-dim — auth_l=0.35, apt_l=0.25; mixed signal capture |

**The mechanism shift.** In v10/v11, `_neutral_option()` picked F-options (authority_asset=0.40 liability sum = 0) as "neutral" for many questions. F-option selections injected asset signals that had weak cross-dimensional spread — geometrically similar to paper_shield's broad low-signal vector. The fix: absolute sum of all fields deprioritizes F-options (authority_asset=0.40 → abs sum = 0.40) in favor of lower-total-signal options. This removed the asset-signal bias that was feeding paper_shield.

**Why the_unexamined_algorithm replaces it.** HC profiles use best_option_for_state() across all 39 questions regardless of whether the question targets the state. For Authority states, this maximizes authority_liability at every question — but many questions carry secondary aptitude_liability in their strongest options (dual-seeded questions). The accumulated vector for many Authority HC profiles has both high authority_liability and non-trivial aptitude_liability. The_unexamined_algorithm (auth_l=0.35, apt_l=0.25) is geometrically closest to this mixed two-field profile. Its Auth 1.00× floor (0.8926) remains below the cosine scores these mixed profiles achieve.

---

## Section 3 — HC Failure Mode Analysis

HC pass rate: 0/47. The failure modes split cleanly into two patterns:

**Pattern A — multi_state contamination (most HC failures).**
The target state IS at rank-1, but one or more other states simultaneously clear the floor. Output becomes `multi_state` where `single_state` is required. From verbose output: invisible_burnout rank-3, the_basement_standard rank-4, the_inside_track rank-5, groundhog_day rank-6, the_wrong_reward rank-7, the_broken_compass rank-8, culture_drift rank-9. All fail with output_type='multi_state' — signal routing is working, floor contamination is the barrier.

**Pattern B — rank-1 misclassification.**
The_unexamined_algorithm captures rank-1 for many states. Built_to_fail, decision_blindness, and several Authority states route to the_unexamined_algorithm instead of the target. Mechanism: mixed auth + apt signal from dual-seeded HC answer selections.

**Severity tier mismatch — compound failure.**
Many HC profiles also fail on severity: `tier='Emerging', expected 'Endemic'`. This is an independent dimension of failure — the severity engine is under-scoring even when signal routing is correct. This is a calibration gap in the severity model, not a question routing problem.

---

## Section 4 — Correct-Routing Progress

States with at least one correct rank-1 profile in v12:

| State | Correct rank-1 count | Passing | Failure mode for non-passing |
|---|---|---|---|
| `built_to_fail` | 1/3 | Yes (weak) | HC/mod: the_unexamined_algorithm at rank-1 |
| `culture_drift` | 1/3 | Yes (moderate) | HC: rank-9, multi_state; weak: rank-14, below floor |
| `decision_paralysis` | 1/3 | Yes (weak) | HC: multi_state or wrong rank-1 |
| `leadership_continuity_risk` | 2/3 | Yes (weak+mod) | HC: multi_state |
| `the_founders_grip` | 1/3 | Yes (weak) | HC: multi_state |
| `the_policy_lag` | 1/3 | Yes (weak) | HC/mod: multi_state or wrong rank-1 |
| `the_undefined_role` | 1/3 | Yes (weak) | HC/mod: multi_state or wrong rank-1 |
| `the_unexamined_algorithm` | 2/3 | Yes (weak+mod) | HC: multi_state |
| `the_unformed_leader` | 1/3 | Yes (weak) | HC/mod: multi_state |
| `the_uninitiated` | 2/3 | Yes (weak+mod) | HC: multi_state |
| `transition_paralysis` | 1/3 | Yes (weak) | HC: multi_state |

Notable: the_second_close HC is rank-2 (very close). The_burned_credibility HC is rank-2. Multiple states are near-miss at rank-2 with multi_state contamination.

**36 states with 0/3 — structural gap.** These states are not routing correctly even at the weak level. The primary mechanisms are: (a) the_unexamined_algorithm absorbing their profiles, (b) their signal questions not discriminating strongly enough at the noise floor, or (c) they share signal space with higher-floor states.

---

## Section 5 — Recommended Next Steps

**v12 establishes the first meaningful signal-driven baseline.** 14/142 is a real result, not a noise artefact. The paper_shield sink is confirmed resolved. Three structural issues now visible:

**Issue 1 — the_unexamined_algorithm as new dominant sink.**
Floor = 0.8926 (Auth 1.00×). Cross-dimensional (auth + apt) vector absorbs mixed-signal profiles. Two paths:
- Raise the_unexamined_algorithm's floor by sharpening its vector (reduces geometric breadth)
- Adjust HC answer generation to prefer single-dimension options where available (reduces auth+apt co-accumulation in non-Authority profiles)

**Issue 2 — HC multi_state contamination.**
Target state is at rank-1 but floor-clearing contamination prevents single_state output. The floor threshold for non-target states needs to be higher, or the target state's signal needs to be more concentrated. Signal sharpening through more targeted question seedings is the structural fix.

**Issue 3 — 36 states with 0/3.**
Many of these states fall in Attitude (LOW/CLUSTER: narrative_lock, what_nobody_says, etc.) and Authority (heard_and_ignored, the_exposed, hr_capture). Their signal questions may not produce enough discrimination relative to the_unexamined_algorithm's absorption. Requires per-cluster analysis.

**Pete decides direction. Engine changes require Gemini brief first.**
