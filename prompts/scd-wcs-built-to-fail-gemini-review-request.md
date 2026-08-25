# Architecture Review — Does SCD-WCS Conserve False-Rank-1 "Mass" Within a Dimension Cluster?

**DRAFT — not sent. For Pete's review before dispatch.**

## Context

`built_to_fail` is the largest false-rank-1 source in the SCD-WCS taxonomy (62/175 profiles, 35.4%, against a currently-shipped single-axis Aptitude vector: `aptitude_liability=0.60`, all other fields at the 0.10 floor). A multi-phase re-authoring program has tried four independent approaches to reduce this, all of which failed — not marginally, but in a way that's starting to look structural rather than a matter of finding the right candidate. Before proposing any further candidate, we want your read on whether the scoring geometry itself makes this cluster of states mutually incompressible — i.e., whether the problem as scoped is even solvable by authoring a better `built_to_fail` vector, or whether it requires a different kind of intervention entirely.

**This is a structural question, not a request to propose a fix.** We have a working mechanistic hypothesis (below) and want it stress-tested, not confirmed at face value — tell us where it's incomplete or wrong before we act on it either way.

## The real formula, for reference (`engine/accumulation.py::rank_states()`)

```
mu_N            = MC_CENTROID_39 * (answered_question_count / 42.0)
vec_A_displaced = accumulated_vector - mu_N          # session, centroid-displaced
vec_B           = profile.dimensional_vector          # state profile, undisplaced

num = sum(w_i * A_displaced_i * B_i)                  # dot product, all 8 fields
den = sqrt(sum(w_i * A_displaced_i^2)) * sqrt(sum(w_i * B_i^2))
sim = num / den
```

Weighted cosine similarity, summed across all eight dimensional fields (`aptitude_liability/asset`, `authority_liability/asset`, `alliance_liability/asset`, `attitude_liability/asset`) simultaneously — not per-axis. `w` is the state's own `SALIENCE_PROFILES` entry (defaults to 1.0 per field if absent).

## What's confirmed — four independent negative results for `built_to_fail` specifically

1. **Constrained single-axis redistribution** (original 3-state search, within `built_to_fail`'s own fixed 0.90 liability budget) — ruled out. No candidate brought `built_to_fail`'s and a rival's (`invisible_performance_management`) false-rank-1 counts down together; every move that helped one made the other substantially worse.
2. **Combined magnitude-only candidate** (primary lowered 0.60→0.50 *and* floor raised 0.10→0.15, simultaneously) — made it worse: 62→100 (+38), the largest false-rank-1 count measured anywhere in this program's history for any state.
3. **Both magnitude-only levers, tested in isolation** — both independently made it worse. Floor-only (0.10→0.15, primary unchanged): 62→84 (+22). Primary-only (0.60→0.50, floor unchanged): 62→72 (+10). **Confirmed non-additive**: 22+10=32, but the combined test above measured +38 — combining the two levers costs more than either contributes alone.
4. **No textual grounding exists for any shape change.** `built_to_fail`'s `descriptive_prose` — *"The role's scope exceeds what any reasonable allocation of resources could support... told to make it work rather than given what making it work would require... the next person inherits the same impossible math"* — carries zero secondary-axis content, confirmed independently on four separate passes across this program. There is no textual basis for adding a second dimension; every lever tested has been magnitude-only, on the single Aptitude axis, and all of them failed.

## A fifth finding — not `built_to_fail`-specific, and possibly the more important one

Separately, we tested whether the *other* states sharing `built_to_fail`'s general Aptitude-cluster neighborhood could be fixed independently, leaving `built_to_fail` completely untouched (reverted to its exact shipped vector/salience). Two of those states — `invisible_performance_management` and `the_paper_tiger` — were re-authored to move fully off the Aptitude axis onto Authority (both had genuine textual grounding for this; `invisible_performance_management`'s text explicitly disclaims an Aptitude reading — *"a manager's read... is accurate... a sound judgment"* — while being entirely about evidentiary/documentation weight).

**With `built_to_fail` completely unchanged, its own false-rank-1 count still rose from 62 to 80 (+18), purely as a side effect of its two rivals vacating the Aptitude axis.** A further +20 landed across three more Aptitude-adjacent states that were never touched by any candidate at all: `the_unformed_leader` (8→18, +10), `the_overloaded_manager` (9→15, +6), `the_undefined_role` (3→7, +4).

**The total — +38, spread across `built_to_fail` and three neighbors — is nearly identical in magnitude to Result #2 above (+38, concentrated entirely in `built_to_fail` alone when its own vector was also changed).** Same total, different distribution depending on what `built_to_fail`'s own vector looked like at the time. This is the observation the structural question below is really about.

## Working hypothesis to stress-test — not to confirm

**Because the cosine numerator sums a dot product across all eight fields at once, any state's vector movement changes its alignment with every profile it's compared against, not just profiles on its own primary axis.** Raising `built_to_fail`'s floor from 0.10 to 0.15 on three unrelated fields increased its raw dot-product contribution against *any* profile carrying signal on those fields, not just Aptitude-heavy ones — which is one candidate explanation for why "softening" the vector (Result #2/#3) made things worse rather than better: it broadened the vector's reach rather than narrowing it. Separately, when `invisible_performance_management` and `the_paper_tiger` vacate the Aptitude axis, whatever session-level Aptitude signal used to be split three ways now concentrates onto `built_to_fail` (and its nearest under-differentiated neighbors) by default, regardless of `built_to_fail`'s own magnitude — which is one candidate explanation for Result #5.

**The structural question, stated plainly: does this scoring geometry — weighted cosine similarity summed across all eight fields, with no per-axis independence — inherently conserve some quantity of "false-rank-1 mass" within a cluster of states that share a dominant dimension, such that no candidate authored *within* that cluster (touching only the cluster's own vectors/salience) can reduce the cluster's total false-rank-1 count, only redistribute it among the cluster's members?** If true, this would mean `built_to_fail`'s problem was never really solvable by finding a better `built_to_fail` vector — the four negative results above would be expected outcomes of the geometry itself, not failures of candidate selection. If false, we want to know what's actually different about the candidates tried so far versus what a working fix would need to do differently.

## Questions for you

1. Is the "conserved mass within a shared-dimension cluster" framing mathematically sound for weighted cosine similarity as implemented here, or is there a real degree of freedom we haven't tried that could reduce the cluster's total false-rank-1 count rather than just move it? (E.g., does touching asset fields rather than only liability fields behave differently? Does the salience weighting itself, independent of vector shape, have unused leverage here?)
2. If the conservation framing is correct in general but not absolute, what would a genuine reduction (not redistribution) actually require — a change outside the six-state cluster entirely (e.g., adjusting `MC_CENTROID_39` or the centroid-displacement mechanism itself, which no candidate in this program has touched), a change to the metric (weighted cosine vs. some alternative), or something else?
3. Given four negative results specific to `built_to_fail` and a fifth showing its dominance is coupled to its neighbors' shape rather than just its own, is continuing to search for a `built_to_fail`-specific vector candidate a reasonable use of further search effort, or does this cluster need a different category of intervention (e.g., accepting a documented, permanent limitation for this specific cluster, revisiting the calibration suite's own profile design for Aptitude-cluster states, or something structural we haven't considered)?
4. Is there a way to test the conservation hypothesis directly and cheaply, independent of authoring another candidate — e.g., a theoretical bound on total false-rank-1 count achievable within a fixed-dimension-count cluster given this specific similarity metric, rather than another empirical trial-and-error pass?

## Not asked here

No candidate vector is proposed in this document. No recommendation on whether to keep searching, pause, or accept a limitation is made — that's Pete's call, informed by your answer to the structural question above.
