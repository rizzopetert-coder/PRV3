# Verifying Gemini's Response to the `built_to_fail` Structural Review — 6 Items Checked

Date: 2026-08-24. Full verification pass against live source, not a skim. **No action taken on the "halt built_to_fail search" recommendation or anything else in Gemini's response — verification only, per instruction.**

---

## 1. `_weighted_cosine_similarity()` / `rank_states()` formula, 8-field sum, displacement — **VERIFIED (formula), CONTRADICTED (citation)**

**The formula and 8-field sum are real and match exactly.** Pulled `rank_states()` fresh, `engine/accumulation.py:524-594`:

```python
# engine/accumulation.py:557-586
mu_N = np.array([MC_CENTROID_39[f] * CENTROID_FIELD_SCALARS.get(f, 1.0) * scale for f in fields])
vec_A = np.array([accumulated_vector.get(f, 0.0) for f in fields])
vec_A_displaced = vec_A - mu_N
...
num = np.sum(w * vec_A_displaced * vec_B)
den = (np.sqrt(np.sum(w * vec_A_displaced ** 2)) *
       np.sqrt(np.sum(w * vec_B ** 2)))
sim = float(num / den) if den > 1e-5 else 0.0
```

This matches Gemini's quoted formula element-for-element: weighted dot product over all 8 fields, displaced session vector, undisplaced profile vector, weighted magnitude normalization in the denominator.

**But the citation to `_weighted_cosine_similarity()` as jointly implementing this is wrong.** That function is real (`engine/accumulation.py:318-339`) but:
- It takes plain `accumulated`/`profile_vector` dicts with **no `mu_N`, no displacement logic anywhere in its own body** — it computes undisplaced cosine similarity only.
- `rank_states()` does **not call it** — confirmed via `grep -rn "_weighted_cosine_similarity(" engine/*.py tools/*.py`: the only hits are the function's own definition and three historical patch scripts (`tools/patch_accumulation_weighted_cosine.py`, `tools/patch_v21_cdwcs.py`, `tools/patch_v21_cdwcs_corrected.py`). `rank_states()` does its own inline numpy computation instead (the block quoted above).
- This means `_weighted_cosine_similarity()` is **dead code in the current live pipeline** — real, but unused. Gemini's citation appears to be reasoning from an earlier version of the codebase (the v21 patch scripts *did* call this function with displaced vectors — `tools/patch_v21_cdwcs_corrected.py:112: sim = _weighted_cosine_similarity(a_d, b_d, w, fields)`), not the current implementation.

**Verdict: the mathematical claim holds against `rank_states()`; the specific function citation does not hold against live code.**

---

## 2. `MC_CENTROID_39` / `CENTROID_FIELD_SCALARS` formula — **VERIFIED, exactly**

Both confirmed to exist, `engine/accumulation.py:46-55` and `:66-75`, both dicts keyed by all 8 dimensional fields:

```python
MC_CENTROID_39: dict = {
    "aptitude_liability": 3.1590, "aptitude_asset": 0.5272,
    "authority_liability": 5.3306, "authority_asset": 1.4412,
    ...
}
CENTROID_FIELD_SCALARS = {
    "aptitude_liability": 0.2415, "aptitude_asset": 0.4000, ...
}
```

The formula at `accumulation.py:557` — `MC_CENTROID_39[f] * CENTROID_FIELD_SCALARS.get(f, 1.0) * scale` where `scale = N/42.0` (`:555`) — matches Gemini's claimed μ_N = MC_CENTROID_39 × CENTROID_FIELD_SCALARS × (N/42.0) exactly, not approximately.

---

## 3. `generate_answers()` / weak-branch behavior — **NOT SUBSTANTIATED, describes a different mechanism than the real one**

Gemini's claim: *"synthetic profiles generate answers where off-axis noise accumulates systematically... the geometry correctly classifies what it was fed."* Cites `generate_answers()` and the file, no line, no quoted logic.

**The real, already-documented confound is different in kind.** `_damped_weak_option()`'s own docstring, `tools/calibration_runner.py:228-233`:

> "Known limitation, accepted as-is: operates at dimension granularity, not state granularity. **Any two states sharing a primary_dimension receive byte-for-byte identical weak-branch answer vectors under this rule** (for wired questions; unwired questions now diverge further via the tighter down-weighted threshold) — downstream cosine similarity against each state's own distinct profile vector still differentiates them."

The actual selection logic (`:235-243`) picks the option with the **largest positive contribution on the target state's own primary-dimension field** — this is **on-axis signal shared identically across same-dimension states**, not "off-axis noise." Gemini's framing ("off-axis noise," "noise accumulates") describes a different mechanism than what the function does, doesn't cite a line or quote the actual logic (failing the verification requirement built into the request), and doesn't engage with the real documented confound at all.

**Verdict: does not hold as stated. Not flatly false in isolation, but unsubstantiated as cited, and mischaracterizes the real, more specific, already-known mechanism.**

---

## 4. Margin gating / dimensional significance floor in `engine/output.py` — **EXISTS AND IS LIVE, but Gemini's characterization of what it does is wrong**

Gemini presented this as something that could be *added* ("Applying an absolute dimensional significance floor... before global cosine ranking prevents states from winning..."). **It already exists and is already live** — not hypothetical:

- `SCD_WCS_MARGIN_GATE: float = 0.0500` — `engine/output.py:42`, described in-line as "Hybrid gate: absolute floor + relative margin constraint" (`:38-39`).
- `apply_signal_floor()` — `engine/output.py:339`, confirmed **called** at `engine/output.py:794` inside `OutputEngine.build()`.

**But it runs after ranking, not before, and does not change which state wins rank-1.** Confirmed via `engine/contract.py:372-384`, where `state_distribution`'s `rank` and `score` fields are built directly from `rankings` (the raw, unmodified output of `rank_states()`):

```python
# engine/contract.py:372-380
state_distribution = [
    {
        "state_id":   r.state_id,
        "score":      round(r.score, 6),
        "rank":       r.rank,
        "above_floor": any(
            qs.state_id == r.state_id and qs.cleared_floor
            for qs in routing.all_evaluated
        ),
        ...
```

The margin-gate's own output (`routing.all_evaluated`, `qs.cleared_floor`) only populates the separate `above_floor` boolean — it never touches `r.rank` or `r.score`. This is the exact `state_distribution` structure every false-rank-1 measurement in this entire program (Phase 4, 4b, 4c, the original 3-state search) has been reading `rank1 = max(sd_list, key=score)` from.

**Verdict: the mechanism is real and live, contrary to how it's framed as a proposal — but it structurally cannot do what Gemini says it would do. It's a post-ranking output-presentation gate, not a pre-ranking geometry change, and would not move the false-rank-1 metric this program has measured throughout.** This is the most consequential finding in this verification pass — it directly undermines Section 2's "genuine reduction" answer, one of the two candidate mechanisms offered.

---

## 5. Asset-field tier defaults (0.10 HIGH / 0.15 MED/LOW) — **VERIFIED**

Confirmed two ways:
- **Source of the convention**, `tools/patch_v10_tier_standardization.py`'s `high_vec()`/`medium_vec()`/`low_vec()` builders: HIGH tier sets all non-primary fields (including all four asset fields) to 0.10; MEDIUM and LOW/CLUSTER tiers set them to 0.15.
- **Live values**, already pulled directly this program: `built_to_fail`'s four asset fields = 0.10 uniformly (HIGH tier); `invisible_performance_management`'s, `the_second_close`'s, `silosolation`'s, `the_arbitrary_standard`'s asset fields = 0.15 uniformly (MEDIUM/LOW tier).

---

## 6. Section 4's proposed orthogonalized-basis test — **NOT DIRECTLY EXECUTABLE; its own stated scope is numerically wrong**

**The measurement half is real and already proven working** — this program's own Phase 4/4b/4c dry-run scripts already do exactly this (reuse `_run_profile_core()` + `_build_suite_v23()`, mutate `STATE_PROFILES` in memory, tally a false-rank-1 Counter across the full 175-profile sweep). No new tooling needed for that part.

**The orthogonalization half does not exist anywhere in this codebase.** `grep -rn "orthogonal|gram_schmidt|np.linalg.qr|orthonormal" engine/*.py tools/calibration_runner.py` returns exactly one hit — an unrelated docstring in `engine/severity.py` using "orthogonal" informally ("Severity accumulation is independent and orthogonal from dimensional vector [accumulation]"), not a linear-algebra utility. Constructing genuinely orthogonalized basis vectors "spanning the same subspace" would be new code, not a config change to existing tooling — and the test's own operationalization (which subspace, exactly, and how the resulting basis vectors map back onto specific states) isn't specified precisely enough to implement as written.

**The test's stated scope is also directly checkable and wrong.** Gemini's test refers to "the 6 Aptitude state vectors." Pulled live: **9 states currently carry `primary_dimension == "Aptitude"`** — `the_unformed_leader`, `the_overloaded_manager`, `the_dormant_talent`, `built_to_fail`, `the_undefined_role`, `the_paper_tiger`, `invisible_performance_management`, `the_unsolved_problem`, `paper_shield`. Not 6.

**Verdict: partially executable (the sweep/measurement harness is real and reusable today) but the test as specified requires genuinely new code for its core novel step, and its own premise about the population size is wrong.**

---

## Summary table

| # | Claim | Verdict |
|---|---|---|
| 1 | Formula / 8-field sum / displacement | **VERIFIED** (formula, vs. `rank_states()`) / **CONTRADICTED** (citation to `_weighted_cosine_similarity()`, which is dead code and doesn't itself displace) |
| 2 | `MC_CENTROID_39` × `CENTROID_FIELD_SCALARS` × (N/42.0) | **VERIFIED**, exactly |
| 3 | `generate_answers()` "off-axis noise accumulates systematically" | **UNVERIFIED** — uncited, and describes a different mechanism than the real, documented one (on-axis answer identity across same-dimension states, not off-axis noise) |
| 4 | Margin gating / significance floor in `engine/output.py` | **EXISTS, live** (not hypothetical) — but **CONTRADICTED** on function: runs post-ranking, never changes rank-1, would not move the false-rank-1 metric |
| 5 | Asset-field tier defaults 0.10 HIGH / 0.15 MED/LOW | **VERIFIED** |
| 6 | Orthogonalized-basis test executability | **PARTIALLY EXECUTABLE** — measurement half real and reusable; orthogonalization half requires new code; stated population ("6 states") is wrong, real count is 9 |

## Bottom line

The core mathematical formula (items 1's formula, item 2) is solid and matches live code precisely. Everything downstream of that — the answer-generation mechanism (item 3), the margin-gate proposal (item 4), and the proposed direct test (item 6) — has a real, checkable problem. Item 4 is the most consequential: Gemini offered "margin gating" as one of two candidate paths to a genuine (non-redistributive) reduction, without apparently checking that this mechanism already exists in the live pipeline and, by its own placement in the code, cannot influence the rank-1 winner this whole program measures. This doesn't resolve the structural question Gemini was asked (whether the geometry conserves false-rank-1 mass within a cluster) — it just means one of the two answers offered for "what would a genuine reduction require" doesn't hold up, and the "halt the search" recommendation in Section 3 was reasoned partly from claims that don't verify cleanly. Not acted on. Pete's call on how to weigh this before any next step.
