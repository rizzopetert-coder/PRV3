# PRV3 Phase 2 Score Distribution v18

## Session 23 · Three-Tier Salience Architecture + Floor Ceiling 0.9650 · 2026-05-24

---

## Run Configuration

| Field | Value |
|---|---|
| Mode | Signal-driven — generate_answers() per profile type |
| Engine changes | salience.py: 15 LOW/CLUSTER states secondary 2.5→1.0 (three-tier); output.py: SIGNAL_FLOOR_CEILING=0.9650 + _PRECOMPUTED_NOISE_BASELINE v18 |
| Metric | Weighted cosine similarity (SALIENCE_PROFILES) — unchanged from v17 |
| Profiles run | 142 (47 HC + 1 extreme HC + 47 moderate + 47 weak) |
| Floor multipliers | Authority 1.00×; non-Authority 1.08×; ceiling 0.9650 |
| Baseline source | recalibrate_floor_v18.py — N=1000, seed=42, Q01–Q39, weighted cosine |
| Baseline mean | 0.8970 (v17: 0.8968 — delta +0.0002) |
| culture_drift baseline | 0.9323 (v17: 0.9318 — delta +0.0005); floor capped at 0.9650 |
| the_uninitiated baseline | 0.9439 (v17: 0.9439 — delta 0.0000) |

---

## Section 1 — Top-Line Result

| Version | Pass | HC | Extreme | Moderate | Weak | Dominant sink |
|---|---|---|---|---|---|---|
| v13 | **13/142** | 0/47 | 0/1 | 4/47 | 9/47 | the_uninitiated (~81) |
| v14 | **19/142** | 0/47 | 0/1 | 3/47 | 16/47 | the_uninitiated (~90+) |
| v15 | **15/142** | 0/47 | 0/1 | 3/47 | 12/47 | the_uninitiated (dominant) |
| v16 | **17/142** | 0/47 | 0/1 | 4/47 | 13/47 | the_uninitiated (dominant); culture_drift secondary |
| v17 | **18/142** | 0/47 | 0/1 | 7/47 | 11/47 | culture_drift (99 captures); the_uninitiated secondary (12) |
| v18 | **20/142** | 0/47 | 0/1 | 10/47 | 10/47 | culture_drift (60); the_overloaded_manager (48); the_uninitiated (11) |

**Net change: +2 from v17.** Moderate +3. Weak −1. HC unchanged at 0/47.
**Hard stop triggered:** HC pass count is 0/47. Flag immediately per v18 handoff. Do not commit without Pete's decision.
**4 gains** (identity_erosion +1, leadership_continuity_risk +1, leadership_deafness +1, the_uninitiated +1). **2 regressions** (culture_drift −1, the_burned_credibility −1). Gemini target 22+/47 HC: not achieved.

---

## Section 2 — By-State Results

| State | v18 | v17 | Delta |
|---|---|---|---|
| built_to_fail | 2/3 | 2/3 | — |
| culture_drift | 1/3 | 2/3 | **−1** |
| decision_blindness | 0/3 | 0/3 | — |
| decision_paralysis | 1/3 | 1/3 | — |
| dueling_narratives | 0/3 | 0/3 | — |
| groundhog_day | 0/3 | 0/3 | — |
| heard_and_ignored | 0/3 | 0/3 | — |
| hr_capture | 0/3 | 0/3 | — |
| identity_erosion | 1/3 | 0/3 | **+1** |
| invisible_burnout | 0/3 | 0/3 | — |
| invisible_influence_architecture | 0/3 | 0/3 | — |
| leadership_continuity_risk | 2/3 | 1/3 | **+1** |
| leadership_deafness | 1/3 | 0/3 | **+1** |
| narrative_lock | 0/3 | 0/3 | — |
| paper_shield | 0/3 | 0/3 | — |
| pay_exposure | 0/3 | 0/3 | — |
| silosolation | 1/3 | 1/3 | — |
| the_arbitrary_standard | 0/3 | 0/3 | — |
| the_basement_standard | 0/3 | 0/3 | — |
| the_broken_compass | 0/3 | 0/3 | — |
| the_burned_credibility | 0/3 | 1/3 | **−1** |
| the_culture_that_wasnt | 0/3 | 0/3 | — |
| the_diversity_ceiling | 0/3 | 0/3 | — |
| the_dormant_talent | 1/3 | 1/3 | — |
| the_exposed | 0/3 | 0/3 | — |
| the_founders_grip | 1/3 | 1/3 | — |
| the_fracture | 0/3 | 0/3 | — |
| the_inside_track | 0/3 | 0/3 | — |
| the_lost_map | 0/3 | 0/3 | — |
| the_overloaded_manager | 1/3 | 1/3 | — |
| the_paper_tiger | 0/4 | 0/4 | — |
| the_pay_fog | 0/3 | 0/3 | — |
| the_policy_lag | 1/3 | 1/3 | — |
| the_second_close | 0/3 | 0/3 | — |
| the_suppression_filter | 0/3 | 0/3 | — |
| the_tolerated_violation | 0/3 | 0/3 | — |
| the_undefined_role | 2/3 | 2/3 | — |
| the_unexamined_algorithm | 0/3 | 0/3 | — |
| the_unformed_leader | 2/3 | 2/3 | — |
| the_uninitiated | 2/3 | 1/3 | **+1** |
| the_unlocked_door | 0/3 | 0/3 | — |
| the_unreported_hazard | 0/3 | 0/3 | — |
| the_unsolved_problem | 0/3 | 0/3 | — |
| the_untouchable | 0/3 | 0/3 | — |
| the_wrong_reward | 0/3 | 0/3 | — |
| transition_paralysis | 1/3 | 1/3 | — |
| what_nobody_says | 0/3 | 0/3 | — |

**States at 0/3: 32** (v17: 33). 2 recoveries (identity_erosion, leadership_deafness). 1 new zero (the_burned_credibility). Net −1 in zero count.

---

## Section 3 — Confusion Matrix Analysis

### Sink summary

| Rank-1 sink | v18 captures | vs v17 |
|---|---|---|
| culture_drift | **60** | Reduced from 99 (−39); no longer unconstrained. Floor now 0.9650 (was 1.0063) |
| the_overloaded_manager | **48** | NEW co-dominant sink. Emerged as culture_drift's capture cone narrowed |
| the_uninitiated | 11 | Slightly reduced from 12 |
| built_to_fail | 6 | Minor sink; captures the_paper_tiger (×3) + others |
| the_unexamined_algorithm | 3 | Captures the_policy_lag (×2) + leadership_continuity_risk (×1) |
| the_suppression_filter | 3 | Captures the_fracture (×2) + partial others |
| paper_shield | 2 | |
| the_unformed_leader | 2 | |

### culture_drift — reduced but still dominant

v17: 99 captures (45/47 states). v18: 60 captures. Three-tier salience change (authority secondary 2.5→1.0) narrowed culture_drift's capture cone as designed. States previously routing exclusively to culture_drift now split between culture_drift and the_overloaded_manager. culture_drift floor is now 0.9650 (capped from 1.0063) — gateable, but still high relative to achievable signal for non-CD profiles.

### the_overloaded_manager — new co-dominant sink (HARD STOP condition)

v17: minor sink. v18: 48 captures across approximately 30+ states. Root cause: the_overloaded_manager (Aptitude primary, Authority secondary) has primary salience 2.5 on aptitude_liability. As culture_drift's authority secondary was reduced (2.5→1.0), profiles with moderate aptitude signal that previously aligned to culture_drift's authority+attitude pattern now route to the_overloaded_manager's aptitude+authority pattern. the_overloaded_manager's secondary (authority) remains at 1.0 post-three-tier (reduced from 2.5), but the aptitude primary is a broad attractor across all states that accumulate any aptitude-liability signal through neutral traversal.

**Hard stop check — v18 handoff:** "A new LOW/CLUSTER state becomes dominant sink in v18" — the_overloaded_manager is LOW/CLUSTER tier and is now co-dominant with culture_drift. This condition is satisfied. Flag to Pete.

### HC routing — unchanged at 0/47

All 47 HC profiles still fail to clear their target state's floor. HC profiles route primarily to culture_drift (estimated 20–26 captures) and the_overloaded_manager (estimated 15–20 captures). The three-tier salience change and floor ceiling did not change the fundamental signal deficit: HC profiles accumulate insufficient primary-dimension signal on the target state's primary axis relative to the floor.

---

## Section 4 — What Worked / What Did Not

### What worked

- **+2 net improvement from v17.** 18→20/142.
- **culture_drift capture reduced: 99→60 (−39).** Three-tier salience change narrowed culture_drift's capture cone as designed. The authority secondary reduction (2.5→1.0) weakened culture_drift's pull on mixed authority+attitude vectors.
- **culture_drift now gateable.** Floor ceiling 0.9650 resolved the 1.0063 anomaly. culture_drift profiles that score ≥0.9650 now pass floor gate.
- **4 new state gains.** identity_erosion, leadership_continuity_risk, leadership_deafness, the_uninitiated all gained at least one passing profile.
- **Moderate +3.** Moderate profiles benefited most from both the_uninitiated recovery and culture_drift floor correction.
- **402/402 tests pass.** Engine structurally valid.
- **Zero-state count reduced: 33→32.** Net improvement.

### What did not work

- **HC routing: unchanged at 0/47.** Gemini target 22+/47 HC: not achieved. Hard stop.
- **the_overloaded_manager co-dominant sink: 48 captures.** Emerged as culture_drift's cone narrowed. Low/CLUSTER hard stop condition met.
- **2 regressions from v17.** culture_drift lost 1 passing profile (weaker capture cone means the CD-targeting profiles face a tighter alignment). the_burned_credibility lost its one passing weak profile.

---

## Section 5 — Root Cause Assessment

**Three-tier salience effect on the_overloaded_manager:** The_overloaded_manager's secondary (authority) was reduced 2.5→1.0 in v18. However, its primary (aptitude_liability, 2.5) remains a broad attractor. Neutral traversal questions accumulate aptitude_liability on all profiles (Q35-B/Q36-E amplify aptitude for specific states but even neutral picks contribute small positive aptitude values). As culture_drift's authority secondary weakened, profiles with moderate authority+aptitude content shifted from the culture_drift attractor to the_overloaded_manager attractor. The_overloaded_manager's aptitude primary dominates when authority accumulation is moderate rather than high.

**HC signal deficit — persists:** The fundamental constraint is that HC profiles must accumulate sufficient primary-dimension signal on their target state's salience vector to clear a floor of 0.9650 (ceiling-capped). The neutral traversal on 30+ non-target questions continues to dilute the cosine ratio. Signal amplification (v17) raised specific option values (0.80 for aptitude/alliance, 0.75 for attitude) but the target floor also rose with the new baseline. The relative gap between profile score and floor threshold has not closed.

**What would break the the_overloaded_manager lock:** Either (a) reduce the_overloaded_manager's aptitude primary salience weight (architectural change, affects all aptitude-primary states), (b) install negative aptitude signal on neutral-traversal options for the high-capture questions, or (c) install sufficiently strong positive primary-dimension signal on HC target questions so the target state's floor is cleared before the_overloaded_manager captures rank-1. Option (c) is the direction consistent with v17 signal amplification; option (b) would re-create the neutral drain problem at the aptitude axis.

---

## Section 6 — Open Items Carried to v19

| Item | Status |
|---|---|
| HC routing failure — 0/47 across v13–v18 | PRIORITY. Hard stop. culture_drift reduced (99→60) but the_overloaded_manager emerged as co-dominant (48). v19 brief required. |
| the_overloaded_manager co-dominant sink — hard stop | NEW. 48 captures. Root cause: aptitude primary 2.5 absorbs profiles displaced from culture_drift. Three-tier reduced secondary but primary remains broad attractor. |
| culture_drift still significant sink — 60 captures | Reduced from 99. Floor ceiling now 0.9650 (resolved 1.0063 anomaly). Still captures ~42% of failures. Further secondary reduction may help. |
| 2 regressions from v17 | culture_drift (−1), the_burned_credibility (−1). Both from attractor shift to the_overloaded_manager. |
| APT-PT-00 (the_paper_tiger) — still 0/4 | Routing to built_to_fail (×3). No change. |
| the_fracture — still 0/3 | Routing to the_suppression_filter (×2) + others. No change. |
| Q06 neutral drain — skipped v17, v18 | Neutral pick shift hard stop not resolved. Carries to v19. |
| recalibrate_floor.py cosmetic 1.15× label fix | Queued. |
| VERIFY-Q25 copy review | Queued. |
| Q23-A test profiles SEVER-05 paths | Queued. |
| Negative accumulated values runtime assertion | Queued. |
| Construction and Logistics intake expansion | Queued. |
| The Dormant Talent Signal Map correction | Queued. |
