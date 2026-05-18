# PRV3 Phase 2 Score Distribution v10
## Session 17 · global tier standardization · 2026-05-17

---

## Run Configuration

| Field | Value |
|---|---|
| Change from v9 | Global three-tier vector standardization: HIGH=0.60/0.10 (11 states), MEDIUM=0.45/0.15 (21 states), LOW/CLUSTER=0.35/0.25/0.15 (15 states). All 47 states overridden. Monte Carlo baselines recomputed (N=1000, seed=42). |
| Floor multipliers | Authority 1.00× (LOCKED Session 16) / non-Authority 1.08× |
| Profiles | 142 (47 HC + 47 moderate + 47 weak + 1 extreme HC) |
| Question library | Q01–Q39 (39 questions, answers populated: 0/142 — question population deferred) |

---

## Section 1 — Result

| Metric | v8 | v9 | v10 | Delta v9→v10 |
|---|---|---|---|---|
| Total pass | 1/142 | 1/142 | 3/142 | +2 |
| HC pass | 0/47 | 0/47 | 0/47 | 0 |
| Moderate pass | 0/47 | 0/47 | 0/47 | 0 |
| Weak pass | 1/47 | 1/47 | 3/47 | +2 |

Passing states (v10): `invisible_influence_architecture` (weak), `paper_shield` (weak), `the_unexamined_algorithm` (weak).

**The_uninitiated is no longer the dominant sink.** Its baseline rose from 0.8431 to 0.8971 — a 0.054 increase — pushing it above the threshold that generic Authority signal profiles can clear. The v9 geometric sink mechanism has been broken.

**New dominant sink: `paper_shield`.** Appears as rank-1 misclassification for 30+ states. Mechanism: LOW/CLUSTER Authority vector (authority_l=0.35, alliance_l=0.25, others=0.15) provides broad cross-dimensional coverage — geometrically closer to mixed-signal profiles than more concentrated HIGH or MEDIUM state vectors. Floor = 0.8790 × 1.00 = 0.8790 (Authority 1.00× multiplier).

**Secondary sink: `the_founders_grip`.** Appears as rank-1 for strong Authority-signal profiles. HIGH Authority vector (authority_l=0.60, others=0.10), floor = 0.8679. Its concentration on authority_liability makes it geometrically closest to answer patterns with heavy Authority signal.

---

## Section 2 — Sink Character Shift

| Version | Dominant rank-1 sink | Type | Floor | Mechanism |
|---|---|---|---|---|
| v5 | `the_unexamined_algorithm` | Authority LOW, centroid | 0.7730 | All-0.25 vector, Auth 1.00× |
| v6 | `paper_shield` | Authority LOW, centroid | 0.7730 | All-0.25 vector, Auth 1.00× |
| v7 | `invisible_influence_architecture` | Authority LOW, centroid | 0.7730 | All-0.25 vector, Auth 1.00× |
| v8 | `narrative_lock` | Attitude LOW, centroid | 0.8348 | All-0.25 vector, non-Auth 1.08× |
| v9 | `the_uninitiated` | Authority MEDIUM, seeded | 0.8431 | authority_l=0.40, Auth 1.00× |
| v10 | `paper_shield` | Authority LOW/CLUSTER | 0.8790 | authority_l=0.35, alliance_l=0.25, Auth 1.00× |

**v10 sink is structurally different from all prior sinks.** It is not centroid (v5–v8) and not a uniform medium-seeded state (v9). It is a cross-dimensional LOW/CLUSTER state whose two-field vector (Authority primary, Alliance secondary) spans more of the cosine space than single-dimension HIGH or MEDIUM vectors. This is a new geometric pattern.

**The_founders_grip secondary sink** is also new: a HIGH Authority state absorbing concentrated Authority signal profiles. This indicates that the HIGH tier concentration (0.60 on authority_l, 0.10 everywhere else) makes these states too geometrically accessible to any Authority-heavy profile — not just the target state's profile.

---

## Section 3 — Correct-Routing Progress

States with at least 1 correctly-routing profile (rank-1 = target state):

| State | Correct rank-1 count | Passing | Failure mode |
|---|---|---|---|
| `culture_drift` | 2/3 | No | `paper_shield` also clears floor → multi_state |
| `invisible_influence_architecture` | 1/3 | Yes (weak) | — |
| `paper_shield` | 1/3 | Yes (weak) | — |
| `the_suppression_filter` | 1/3 | No | `what_nobody_says` or `paper_shield` also clears → multi_state |
| `the_unexamined_algorithm` | 1/3 | Yes (weak) | — |

`culture_drift` at 2/3 correct rank-1 is the most advanced routing observed this session. It fails output only because `paper_shield` simultaneously clears the floor — direct evidence that eliminating `paper_shield` as a sink would convert `culture_drift` to a passing state.

---

## Section 4 — The_uninitiated Sink: Resolved vs. Replaced

The v9 recommendation was to raise the_uninitiated's vector to authority_l=0.45. The v10 tier standardization did exactly this (all MEDIUM Authority states now authority_l=0.45, floor = 0.8971). The_uninitiated no longer appears as dominant sink in the confusion matrix. The recommendation worked.

However, the sink shifted to `paper_shield` rather than being eliminated. This is the cascade problem Gemini identified: each centroid/sink patch displaces the sink to the next most absorptive state. The v10 tier standardization has:
- Eliminated the centroid trap (all states now differentiated)
- Raised all medium-Authority floors to 0.8971
- Shifted the sink to a cross-dimensional LOW/CLUSTER state

The sink cascade has now reached the LOW/CLUSTER layer.

---

## Section 5 — Recommended Next Step

**Diagnosis:** `paper_shield` (authority_l=0.35, alliance_l=0.25, others=0.15, floor=0.8790) is the new geometric sink. Its cross-dimensional two-field vector gives it broad cosine accessibility. The question library being empty (0/142 answers populated) means profiles run on noise — and `paper_shield`'s geometry captures noise profiles across dimensions.

**The deeper issue:** With 0/142 answers populated, the calibration runner produces only noise profiles. All pass/fail results at this stage are artefacts of noise geometry, not signal routing. The calibration suite cannot validate correct routing until the question library is populated and profiles carry real answer data.

**Two parallel paths:**

1. **Question population (Step 2 — deferred):** Populate Q01–Q39 with answer options and signal weights per the Signal Map. This is the primary unlock — real answers produce real signal profiles that can validate routing.

2. **Contrast field injection (Step 2 design):** Per Pete's handoff, this requires a separate Gemini brief before execution. Do not touch questions.py this session.

**Holding pattern:** v10 establishes a geometrically clean state layer. The sink cascade has reached a natural stopping point — further vector adjustments without real answer signal would be speculative. Question population is the required next deliverable.

Pete decides direction before any further engine changes.
