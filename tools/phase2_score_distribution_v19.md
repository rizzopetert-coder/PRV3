# PRV3 Phase 2 Score Distribution v19

## Session 23 · Angular Separation: culture_drift Salience 1.85 + Q20 Amplification + Authority Vector Sharpening · 2026-05-24

---

## Run Configuration

| Field | Value |
|---|---|
| Mode | Signal-driven — generate_answers() per profile type |
| Engine changes | salience.py: culture_drift attitude 2.5→1.85; questions.py: Q20-C/D aptitude 0.60→0.80; states.py: the_uninitiated compressed (0.45/0.15→0.40/0.10), six HIGH Authority states sharpened (0.60/0.10→0.70/0.05) |
| Metric | Weighted cosine similarity (SALIENCE_PROFILES) — unchanged |
| Profiles run | 142 (47 HC + 1 extreme HC + 47 moderate + 47 weak) |
| Floor multipliers | Authority 1.00×; non-Authority 1.08×; ceiling 0.9650 |
| Baseline source | recalibrate_floor_v18.py (run post-v19 writes) — N=1000, seed=42, Q01–Q39 |
| Baseline mean | 0.8915 (v18: 0.8970 — delta −0.0055) |
| culture_drift baseline | 0.9261 (v18: 0.9323 — delta −0.0062); floor 0.9650 (ceiling-capped) |
| the_uninitiated baseline | 0.9339 (v18: 0.9439 — delta −0.0100); floor 0.9339 |
| Six HIGH Authority states | 0.8751 (v18: 0.9147 — delta −0.0396); floor 0.8751 |

---

## Section 1 — Top-Line Result

| Version | Pass | HC | Extreme | Moderate | Weak | Dominant sink |
|---|---|---|---|---|---|---|
| v13 | **13/142** | 0/47 | 0/1 | 4/47 | 9/47 | the_uninitiated (~81) |
| v14 | **19/142** | 0/47 | 0/1 | 3/47 | 16/47 | the_uninitiated (~90+) |
| v15 | **15/142** | 0/47 | 0/1 | 3/47 | 12/47 | the_uninitiated (dominant) |
| v16 | **17/142** | 0/47 | 0/1 | 4/47 | 13/47 | the_uninitiated (dominant); culture_drift secondary |
| v17 | **18/142** | 0/47 | 0/1 | 7/47 | 11/47 | culture_drift (99); the_uninitiated (12) |
| v18 | **20/142** | 0/47 | 0/1 | 10/47 | 10/47 | culture_drift (60); the_overloaded_manager (48) |
| v19 | **21/142** | 0/47 | 0/1 | 9/47 | 12/47 | culture_drift (50); the_overloaded_manager (48); leadership_continuity_risk (14) |

**Net change: +1 from v18.** Weak +2. Moderate −1. HC unchanged at 0/47.
**Hard stop triggered:** HC pass count is 0/47 — seventh consecutive version. Do not commit without Pete's decision.
**2 gains** (the_exposed +1, the_unsolved_problem +1). **1 regression** (the_uninitiated −1). Gemini target: first non-zero HC — not achieved.

---

## Section 2 — By-State Results

| State | v19 | v18 | Delta |
|---|---|---|---|
| built_to_fail | 2/3 | 2/3 | — |
| culture_drift | 1/3 | 1/3 | — |
| decision_blindness | 0/3 | 0/3 | — |
| decision_paralysis | 1/3 | 1/3 | — |
| dueling_narratives | 0/3 | 0/3 | — |
| groundhog_day | 0/3 | 0/3 | — |
| heard_and_ignored | 0/3 | 0/3 | — |
| hr_capture | 0/3 | 0/3 | — |
| identity_erosion | 1/3 | 1/3 | — |
| invisible_burnout | 0/3 | 0/3 | — |
| invisible_influence_architecture | 0/3 | 0/3 | — |
| leadership_continuity_risk | 2/3 | 2/3 | — |
| leadership_deafness | 1/3 | 1/3 | — |
| narrative_lock | 0/3 | 0/3 | — |
| paper_shield | 0/3 | 0/3 | — |
| pay_exposure | 0/3 | 0/3 | — |
| silosolation | 1/3 | 1/3 | — |
| the_arbitrary_standard | 0/3 | 0/3 | — |
| the_basement_standard | 0/3 | 0/3 | — |
| the_broken_compass | 0/3 | 0/3 | — |
| the_burned_credibility | 0/3 | 0/3 | — |
| the_culture_that_wasnt | 0/3 | 0/3 | — |
| the_diversity_ceiling | 0/3 | 0/3 | — |
| the_dormant_talent | 1/3 | 1/3 | — |
| the_exposed | 1/3 | 0/3 | **+1** |
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
| the_uninitiated | 1/3 | 2/3 | **−1** |
| the_unlocked_door | 0/3 | 0/3 | — |
| the_unreported_hazard | 0/3 | 0/3 | — |
| the_unsolved_problem | 1/3 | 0/3 | **+1** |
| the_untouchable | 0/3 | 0/3 | — |
| the_wrong_reward | 0/3 | 0/3 | — |
| transition_paralysis | 1/3 | 1/3 | — |
| what_nobody_says | 0/3 | 0/3 | — |

**States at 0/3: 31** (v18: 32). 2 recoveries (the_exposed, the_unsolved_problem). 0 new zeros. Net −1 in zero count.

---

## Section 3 — Confusion Matrix Analysis

### Sink summary

| Rank-1 sink | v19 captures | vs v18 |
|---|---|---|
| culture_drift | **50** | −10 from v18 (60). Track 1 attitude compression working directionally |
| the_overloaded_manager | **48** | Unchanged. Still co-dominant. Track 3 did not reduce aptitude-primary pull |
| leadership_continuity_risk | **14** | NEW secondary sink. Authority vector sharpening created intra-dimension routing |
| built_to_fail | 7 | Minor. the_paper_tiger captures unchanged |
| leadership_deafness | 4 | |
| the_unexamined_algorithm | 3 | |
| the_suppression_filter | 3 | |
| identity_erosion | 3 | |

### leadership_continuity_risk — new secondary sink (14 captures)

Not a hard stop (threshold: >60). Root cause: Authority vector sharpening (six HIGH states 0.60→0.70) increased the authority_liability contribution of HIGH Authority HC best-option picks. leadership_continuity_risk is an Authority MEDIUM state whose dimensional vector (0.45/0.15) now provides a stronger cosine match against the accumulated authority-heavy vectors of profiles trying to reach HIGH Authority states (decision_paralysis, heard_and_ignored, invisible_influence_architecture, the_founders_grip, the_lost_map). These profiles accumulate more authority than leadership_continuity_risk's floor requires, but the sharpened HIGH states' cosine separation from leadership_continuity_risk is insufficient.

### culture_drift — reduced, not suppressed (50 captures)

Attitude primary reduction (2.5→1.85) produced a −10 reduction in captures. The absolute number (50) remains above the >60 hard stop threshold. The remaining captures are predominantly from Attitude-primary states where culture_drift's salience (1.85) still provides a strong cosine match vs the target state's narrower profile.

### the_overloaded_manager — unchanged (48 captures)

Track 3 did not affect Aptitude state routing. The overloaded_manager's aptitude primary (2.5 in salience) remains the dominant attractor for profiles with mixed aptitude+authority accumulation. No Track in v19 targeted the_overloaded_manager's salience or vector directly.

### HC routing — unchanged at 0/47

HC profiles continue to route to culture_drift (dominant), the_overloaded_manager, and Authority sinks. The diagnostic from v18 (44/47 HC profiles above their floor, failing on rank-ordering) remains the active constraint. The v19 interventions reduced sink attractiveness marginally but did not produce cosine separation sufficient to flip HC rank-1 from sink to target.

---

## Section 4 — What Worked / What Did Not

### What worked

- **+1 net improvement from v18.** 20→21.
- **the_exposed and the_unsolved_problem — both gained passes.** Authority vector sharpening (0.60/0.10→0.70/0.05) lowered floors (0.9147→0.8751) and increased weak profile cosine scores on these states. Double effect: lower threshold, better signal ratio.
- **culture_drift captures reduced 60→50.** Track 1 directionally effective. −10 from attitude compression.
- **402/402 tests pass.**

### What did not work

- **HC routing: unchanged at 0/47.** Seventh consecutive version at 0/47. Hard stop.
- **the_overloaded_manager unchanged at 48 captures.** v19 did not target this sink directly.
- **the_uninitiated regression −1.** Vector compression (0.45→0.40) slightly reduced the_uninitiated's attractiveness for profiles that were previously borderline-passing; one moderate profile shifted out.
- **leadership_continuity_risk new secondary sink — 14 captures.** Authority sharpening created intra-Authority dimension confusion. HIGH Authority states now route to leadership_continuity_risk (MEDIUM Authority) for some profiles.
- **Moderate −1.** Net decline in moderate despite gains. the_uninitiated regression offset gains.

---

## Section 5 — Root Cause Assessment

**Seven-version HC plateau (v13–v19):** The HC failure mode identified in the v18 diagnostic persists: 44/47 HC profiles clear their target floor but sinks (culture_drift, the_overloaded_manager) outscore targets by 0.01–0.10 cosine margin. The v19 interventions compressed sink attractiveness by reducing culture_drift's salience weight and increasing target-state vector sharpness for Authority states. Neither was sufficient to flip HC rank-1.

**The floor-clearing problem is solved — the rank-ordering problem is not.** From v18 diagnostic: target scores range 0.87–0.98, sinks score 0.92–0.98. The margin between target and sink is 0.01–0.03 for most HC profiles. The interventions applied in v17–v19 move this margin by ±0.005 per step — insufficient to flip rank-1 at the scale needed (47 profiles simultaneously).

**What would produce first HC passes:** A larger discontinuous intervention on either (a) target-state specificity (make the target cosine score meaningfully higher than the sink's, not marginally) or (b) sink exclusion (structural architectural change — floor gate or dimension gate that prevents sink states from routing for profiles with strong off-axis signal). The incremental parameter approach is approaching diminishing returns.

---

## Section 6 — Open Items Carried to v20

| Item | Status |
|---|---|
| HC routing failure — 0/47 across v13–v19 | PRIORITY. Hard stop. Seven versions at 0/47. Architecture review required before v20 spec. |
| the_overloaded_manager co-dominant sink — 48 captures | Unchanged from v18. Aptitude primary salience (2.5) not addressed in v19. |
| culture_drift residual sink — 50 captures | Reduced 60→50. Further attitude compression (1.85→lower) risks culture_drift own profile failure. |
| leadership_continuity_risk new secondary sink — 14 captures | Authority sharpening side-effect. Intra-Authority confusion between HIGH and MEDIUM states. |
| Mode 2 floor deficits (Track 4) — deferred | the_arbitrary_standard, what_nobody_says, the_dormant_talent, the_overloaded_manager still below floor. Deferred to v20 per Gemini handoff. |
| APT-PT-00 (the_paper_tiger) — still 0/4 | Routing to built_to_fail (×3) + culture_drift (×1). No change. |
| the_fracture — still 0/3 | Routing to the_suppression_filter (×2) + the_overloaded_manager (×1). No change. |
| Q06 neutral drain | Skipped v17–v19. Carries to v20. |
| VERIFY-Q25 copy review | Queued. |
| Q23-A SEVER-05 paths | Queued. |
| Negative accumulated values assertion | Queued. |
| Construction and Logistics intake expansion | Queued. |
| The Dormant Talent Signal Map correction | Queued. |
