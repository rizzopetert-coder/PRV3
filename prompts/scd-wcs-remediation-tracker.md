# SCD-WCS Remediation Tracker

Plain-language guide + working tracker for fixing which condition gets
named as "the" primary finding when a session's answers could point to
more than one state.

Pete has chosen the full clinical-completion path: individually correct
the vector/salience authoring across every affected state, not just
close the investigation with a summary. This file is the single place to
come back to across future sessions — read it first, update it as work
happens.

Full technical detail behind everything summarized here lives in
`prompts/scd-wcs-cluster-map-findings.md`. This file is the plain-language
index and the working tracker; that file is the record of how each
finding was actually verified.

---

## The four patterns found so far (plain language)

1. **Blends in** — this state looks mathematically identical to one or
   more others, so the engine picks between them almost at random. Fix:
   usually just needs a clearer, more specific "fingerprint."
2. **Overpowers everything** — this state wins way more often than it
   should, against many unrelated states, not just one twin. Fix: needs a
   real redesign of its fingerprint, not just a tweak.
3. **Steals from a whole other group** — this state doesn't have one
   obvious twin, it out-competes an entire cluster of other states at
   once. Fix: not yet understood, needs its own investigation.
4. **Unexplained** — doesn't fit any of the above yet, too little data
   to know why it happens.

## Legend for status column

- **NOT STARTED** — nobody's looked at this state yet.
- **DIAGNOSED** — we know what's wrong, haven't fixed it.
- **PILOT DONE** — a fix was tried and tested.
- **SHIPPED** — fix is live and verified.
- **DECLINED** — looked at it, decided on purpose not to fix it (real
  reason noted, not skipped by accident).

---

## Per-state tracker

| State | Pattern (1–4 above) | Cluster/rivals | Status | Pete's call: what actually makes this state different in real life | Dimension (optional) | Notes |
|---|---|---|---|---|---|---|
| `the_unformed_leader` | 1 — Blends in | Paired with `the_dormant_talent` (rank-7) | SHIPPED | | | Aptitude stayed dominant (capability gap — "without having been equipped for it"). Commit 043b8ad, 58a19a0-adjacent (second pass). |
| `the_dormant_talent` | 1 — Blends in | Paired with `the_unformed_leader` (rank-7) | SHIPPED | | | Landed magnitude keeps aptitude dominant, not the attitude-dominant read the real text argued for ("can name precisely... consistently doesn't act on it") — every candidate that made attitude dominant failed calibration. Narrative compromise, not a finished clinical differentiation. |
| `built_to_fail` | 2 — Overpowers everything | Broad — 49/175 profiles (28%), spans all 4 dimensions, not one rival | DIAGNOSED (broad issue) / SHIPPED (narrow tie-break only) | | | The tie specifically against `the_paper_tiger` is SHIPPED (commit 58a19a0). The much bigger "overpowers everything" problem is confirmed structurally unfixable via salience alone — needs real vector-level work. First named Track 2 candidate. |
| `the_paper_tiger` | — (paired state, not itself an "overpowers" case) | Paired with `built_to_fail` (rank-8) | SHIPPED | | | Own salience differentiated (aptitude down, authority + attitude up, per real descriptive_prose: documentation/accountability gap). Tie with `built_to_fail` broken. Still occasionally loses to `built_to_fail` on `built_to_fail`'s own turf — expected, untouched by this fix. |
| `the_fracture` | — (declined) | Paired with `decision_blindness` (rank-9) | DECLINED | | | Real tie, but accurately authored given the actual text — no textual basis found for the tested differentiation hypothesis. Both states already route to the same `resolution_family`, so the tie has low practical stakes regardless. Not prioritized. |
| `decision_blindness` | — (declined) | Paired with `the_fracture` (rank-9) | DECLINED | | | Same reasoning as `the_fracture` — see above. |
| `the_uninitiated` | 3 — Steals from a whole other group | rank-2 (own cluster, tie only) vs. rank-3 (real target, 7 of 8 states) | DIAGNOSED | | | Not a clean pairing. 6 of 22 false-rank-1 profiles are just rank-2's own known cluster tie (not new). The real signal (14 of 16 genuine wins) is `the_uninitiated` beating almost all of rank-3 — despite rank-2's vector being LESS sharp than rank-3's. Contradicts "sharper vector wins." Needs its own diagnosis before any fix — would mean reweighting against a whole 8-state cluster, not one rival. |
| `the_unexamined_algorithm` | 3 (partial) / smaller-scale 2 | No cluster of its own (unique vector). Genuine wins spread: rank-3 (55%), rank-2 (36%), rank-9 (9%) | DIAGNOSED | | | Zero tie-artifacts possible (no cluster-mate to tie with) — all 11 stolen profiles are genuine wins, just spread across three different clusters rather than concentrated on one. A smaller, milder version of the "overpowers" shape. |
| `the_second_close` | 1 (tie-artifact) — real signal negligible once decomposed | rank-6 (own cluster, tie w/ `silosolation`) | DIAGNOSED (likely low priority) | | | 3 of 5 false-rank-1 profiles are just rank-6's own known tie (not new). Only 2 genuine wins remain, both against `the_fracture` (rank-9, already DECLINED above). Almost no real problem left once the tie-artifact is subtracted out. |
| `culture_drift` | 3 (partial), smaller scale | rank-11 (own cluster, tie w/ `wellbeing_theater`) vs. rank-1 (75% of genuine wins) and rank-10 (25%) | DIAGNOSED | | | 1 of 5 is a tie-artifact (own cluster). Remaining 4 genuine wins split across two other clusters, not one. |
| `invisible_performance_management` | 2 — Overpowers everything | No cluster of its own (unique vector). Broad — 59/175 (33.7%), zero true rank-1 ever | DIAGNOSED | | | The single largest dominance problem in the whole taxonomy — bigger than `built_to_fail`. No cluster-mate, no tie to break — pure vector-strength dominance. Not yet piloted or searched at all. |
| `the_overloaded_manager` | 4 — Unexplained | No cluster of its own (unique vector). Small — 4/175 (2.3%), all against attitude-dominant targets despite being aptitude-dominant itself | DIAGNOSED (anomaly, unexplained) | | | Doesn't fit any other pattern. Checked one case directly at the session-vector level — didn't explain the win either. Sample too small (n=4) to trust a theory yet. Flagged for more data. |
| `what_nobody_says` | 1 — Blends in (already resolved) | rank-4 (was tied with the other 5, already split out) | SHIPPED (pre-existing, before this investigation) | | | Already carries a distinct salience entry (alliance-dominant vs. the other 5's attitude-dominant) — confirmed well-grounded, a validated precedent, not an open item. |
| `identity_erosion` | 1 — Blends in | rank-4, 5-way tie remains (`identity_erosion`, `the_culture_that_wasnt`, `narrative_lock`, `the_unreported_hazard`, `the_unlocked_door`) | NOT STARTED | | | Part of rank-4's still-uniform 5-way tie. Real partial stakes (3/5 share "Intervention", `narrative_lock`/`the_unlocked_door` differ) and real narrative distinction if prioritized. Minor dominance signal (1/175) also on record. |
| `the_culture_that_wasnt` | 1 — Blends in | rank-4, same 5-way tie | NOT STARTED | | | See `identity_erosion`. |
| `narrative_lock` | 1 — Blends in | rank-4, same 5-way tie | NOT STARTED | | | See `identity_erosion`. Its own `resolution_family` ("Executive Counsel + Intervention") differs from the other 4. |
| `the_unreported_hazard` | 1 — Blends in | rank-4, same 5-way tie | NOT STARTED | | | See `identity_erosion`. |
| `the_unlocked_door` | 1 — Blends in | rank-4, same 5-way tie | NOT STARTED | | | See `identity_erosion`. Its own `resolution_family` ("Development + Intervention") differs from the other 4. |
| `the_untouchable` | — (already resolved) | rank-10, paired with `the_inner_circle` | SHIPPED (pre-existing, before this investigation) | | | Already carries a distinct salience entry — confirmed well-grounded this session (individual exemption vs. systemic clique, a real narrative distinction). |
| `the_inner_circle` | — (already resolved) | rank-10, paired with `the_untouchable` | SHIPPED (pre-existing, before this investigation) | | | Uniform-default salience (no custom entry) is enough to break the tie against `the_untouchable`'s sharp entry. `resolution_family` match is cosmetic in substance (same two families, different order) but the differentiation itself is real and validated. |
| `wellbeing_theater` | 1 — Blends in | rank-11, paired with `culture_drift` | NOT STARTED | | | Still tied with `culture_drift` (1 of `culture_drift`'s stolen profiles is this exact tie). Both route to the same `resolution_family` ("Intervention") — low stakes. |
| `the_founders_grip` | 1 — Blends in | rank-3, full 8-way tie | NOT STARTED | | | Also the biggest single share of `the_uninitiated`'s cross-cluster theft (3 profiles). Whatever happens to rank-3 needs to account for that relationship, not just rank-3's own internal tie. |
| `the_exposed` | 1 — Blends in | rank-3, full 8-way tie | NOT STARTED | | | |
| `hr_capture` | 1 — Blends in | rank-3, full 8-way tie | NOT STARTED | | | |
| `heard_and_ignored` | 1 — Blends in | rank-3, full 8-way tie | NOT STARTED | | | |
| `the_tolerated_violation` | 1 — Blends in | rank-3, full 8-way tie | NOT STARTED | | | |
| `the_unsolved_problem` | 1 — Blends in | rank-3, full 8-way tie | NOT STARTED | | | The one rank-3 outlier on `resolution_family` ("Intervention + Roadmap" vs. the other 7's "Intervention + Executive Counsel"). |
| `sequential_decision_blindness` | 1 — Blends in | rank-3, full 8-way tie | NOT STARTED | | | |
| `disparate_impact_architecture` | 1 — Blends in | rank-3, full 8-way tie | NOT STARTED | | | |
| `leadership_continuity_risk` | 1 — Blends in | rank-2, full 10-way tie | NOT STARTED | | | |
| `decision_paralysis` | 1 — Blends in | rank-2, full 10-way tie | NOT STARTED | | | Also one of the two states caught in `the_uninitiated`'s tie-artifact count (not new dominance, just the existing rank-2 tie). |
| `the_policy_lag` | 1 — Blends in | rank-2, full 10-way tie | NOT STARTED | | | |
| `dueling_narratives` | 1 — Blends in | rank-2, full 10-way tie | NOT STARTED | | | |
| `transition_paralysis` | 1 — Blends in | rank-2, full 10-way tie | NOT STARTED | | | |
| `the_lost_map` | 1 — Blends in | rank-2, full 10-way tie | NOT STARTED | | | Also caught in `the_uninitiated`'s tie-artifact count, same as `decision_paralysis`. |
| `pay_exposure` | 1 — Blends in | rank-2, full 10-way tie | NOT STARTED | | | |
| `the_pay_fog` | 1 — Blends in | rank-2, full 10-way tie | NOT STARTED | | | |
| `compression_crisis` | 1 — Blends in | rank-2, full 10-way tie | NOT STARTED | | | |
| `paper_shield` | 1 — Blends in | rank-5, full 3-way tie | NOT STARTED | | | Minor dominance signal on record (1/175). |
| `invisible_influence_architecture` | 1 — Blends in | rank-5, full 3-way tie | NOT STARTED | | | |
| `planning_authority_gap` | 1 — Blends in | rank-5, full 3-way tie | NOT STARTED | | | |
| `silosolation` | 1 — Blends in | rank-6, full 3-way tie w/ `the_second_close`, `the_arbitrary_standard` | NOT STARTED | | | The state `the_second_close` ties against — see `the_second_close`'s row, this is that same known tie, not separately new. |
| `the_arbitrary_standard` | 1 — Blends in | rank-6, full 3-way tie | NOT STARTED | | | |
| `the_diversity_ceiling` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | Rank-1 is the largest untouched cluster (11 states), real stakes (5 distinct `resolution_family` combos), real narrative distinctions throughout — closer in scale to a dedicated project than a quick pilot. |
| `the_burned_credibility` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | |
| `invisible_burnout` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | |
| `the_basement_standard` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | |
| `the_inside_track` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | |
| `groundhog_day` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | |
| `the_wrong_reward` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | |
| `the_broken_compass` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | One of `culture_drift`'s 4 genuine wins (3 profiles) targets this state specifically. |
| `human_displacement_anxiety` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | |
| `motivational_architecture_failure` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | |
| `cultural_overtime` | 1 — Blends in | rank-1, full 11-way tie | NOT STARTED | | | |

---

## Open investigative questions (separate from the per-state tracker)

| Question | Plain-language description | Status | Notes |
|---|---|---|---|
| Cross-cluster asymmetry mechanism | When two whole clusters compete on the same dimension (like rank-2 vs. rank-3), what actually decides which one wins? We ruled out "the sharper/more concentrated vector wins" — it's backwards in the one case checked (`the_uninitiated`, the less concentrated one, beats rank-3, the sharper one). No replacement theory yet. | OPEN | Confirmed relevant to at least `the_uninitiated`, `the_unexamined_algorithm`, and `culture_drift` — three separate cases showing some version of this, not just one. |
| Rank-5 / rank-6 decomposition check | The 8-cluster characterization pass gave rank-5 and rank-6 a stakes/narrative read, but never ran the tie-vs-genuine decomposition check (the one that found `the_uninitiated`, `the_unexamined_algorithm`, `the_second_close`, and `culture_drift` were all more complicated than they looked). `the_second_close`'s check is done (it's part of rank-6); `silosolation`, `the_arbitrary_standard` (rest of rank-6), and all of rank-5 haven't been checked this way yet. | NOT STARTED | Was going to be the natural "next pilot" candidates before the 0-for-4 Track 1 result — worth checking with the full method before assuming they're clean either. |
| `the_overloaded_manager` anomaly | Steals only from attitude-dominant targets despite being aptitude-dominant itself, with an authority secondary — doesn't match its own vector on any axis. One case checked at the session-vector level, still unexplained. | OPEN | n=4 is too small to trust any theory yet. Needs more data (more theft profiles as other clusters get worked, or a deeper trace of the actual centroid-displaced vector) before this gets its own theory. |

---

## How to use this

Pete fills in the "Pete's call" column whenever he has a real instinct
about what makes a state distinct — no pressure to fill every row, no
deadline. Claude.ai/CC read this file at the start of any SCD-WCS work to
pick up wherever Pete's left notes, and update the Status column as work
happens. This file is the single source of truth for this investigation's
discretionary judgment calls — don't duplicate this content into MOB
Section 13a beyond a pointer reference.
