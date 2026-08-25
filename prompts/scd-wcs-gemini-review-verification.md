# Verifying Gemini's SCD-WCS Review Before Acting — 3 Claims Checked

Date: 2026-08-24. Diagnostic only. **No reshaping search started, `the_uninitiated` untouched, Gemini's "cleared to proceed" not treated as authorization.** All values pulled fresh from `engine/data/states.py` via live Python import, not cited from the tracker or trusted from Gemini's transcription.

## 1. The "0.90 Total Liability Invariant" — **mostly true, not universal as Gemini presented it**

Computed the real liability-field sum (`aptitude_liability + authority_liability + alliance_liability + attitude_liability`) for all 58 states directly:

| Sum | # of states |
|---|---|
| **0.90** | **54** |
| 1.00 | 2 |
| 0.95 | 1 |
| 0.80 | 1 |

**54/58 (93.1%) genuinely sum to exactly 0.90 — a real, strong pattern. But 4 states do not, and Gemini presented this as an unconditional rule ("must sum to exactly 0.90 for every state"), which is false as stated.** The 4 exceptions, with their real current values:

- `the_unexamined_algorithm` — sum 1.00 (0.30 apt / 0.50 auth / 0.10 all / 0.10 att)
- `the_unsolved_problem` — sum 0.95 (0.50 apt / 0.15 auth / 0.15 all / 0.15 att)
- `distributed_culture_fragmentation` — sum 1.00 (0.15 apt / 0.15 auth / 0.45 all / 0.25 att)
- `leadership_deafness` — sum 0.80 (0.10 apt / 0.10 auth / 0.10 all / 0.50 att)

**Checked whether this session's own recent edits caused any of these violations, rather than assuming either way:** two of the four (`the_unexamined_algorithm`, `the_unsolved_problem`) were touched by this session's earlier remediation work. Directly confirmed neither violation was introduced by that work:
- `the_unexamined_algorithm`'s pre-Candidate-C value (from `tools/patch_scdwcs_candidateC_ship.py`'s own `OLD_UEA` constant) was `aptitude_liability=0.35`, giving a pre-edit sum of **1.05** — *further* from 0.90 than the current 1.00. Candidate C's shipped change (0.35→0.30) moved this state closer to the invariant, not further from it. The violation traces back at least to commit `e2be5ea` ("Session 20... unexamined_algorithm vector patch," 2026-05) — a much older authoring artifact, not something introduced this session.
- `the_unsolved_problem`'s Phase 8 mitigation this session changed only `aptitude_asset` (an asset field), never touched any liability field — its 0.95 liability sum was already 0.95 before and after that edit, unaffected.

**Asset-field "pinned to 0.10 HIGH / 0.15 MEDIUM-LOW" claim: 99.6% true, one known exception.** Checked all 232 asset-field values (58 states × 4 fields) directly: 60 at 0.10, 171 at 0.15, and exactly **one** at 0.20 — `the_unsolved_problem`'s `aptitude_asset`, which is this session's own deliberate Phase 8 "shape adjustment" edit, already on record. Not a new finding, but confirms the asset-tier claim is a real, strong pattern with one known, intentional exception, not a universal rule either.

## 2. `built_to_fail` and IPM's real vectors — **`built_to_fail` matches exactly; IPM does not**

Pulled fresh, not assumed correctly transcribed:

**`built_to_fail`:** `aptitude_liability=0.60`, all others (`authority_liability`, `alliance_liability`, `attitude_liability`) at the 0.10 floor, all four assets at 0.10. **Matches Gemini's claim exactly.**

**`invisible_performance_management`:** `aptitude_liability=0.45` (matches Gemini), but **`authority_liability=0.20` in live code today — Gemini claimed 0.25.** This is not a rounding difference; it's the *pre-Candidate-C* value. Candidate C shipped this session (commit `322ea93`) changed IPM's `authority_liability` from 0.25 → 0.20 specifically. **Gemini's review is working from a snapshot that predates this session's own shipped fix.** Full current IPM vector: `aptitude_liability=0.45 / authority_liability=0.20 / alliance_liability=0.15 / attitude_liability=0.10`, assets all `0.15`.

## 3. Arithmetic compatibility of the proposed reshaping mechanism

**The good news, checked directly rather than assumed:** all four of the *actual* reshaping targets — `built_to_fail`, `invisible_performance_management`, `the_uninitiated` (0.15/0.45/0.15/0.15, sum 0.90), and `the_second_close` (0.15/0.15/0.45/0.15, sum 0.90) — currently sum to exactly 0.90. **A "redistribute within a fixed 0.90 budget" framing is arithmetically valid for the specific 4 states this project actually concerns**, even though the invariant isn't universal across all 58 states in the wider taxonomy.

**But this needs rescoping before any candidate search starts, for two concrete reasons, not zero:**

1. **Any specific numeric redistribution proposal for IPM needs to be re-derived against the real current vector (0.20 authority_liability), not Gemini's stale 0.25.** If Gemini's own proposed "redistribute 0.05-0.10 from the dominant field" language was computed using 0.25 as IPM's starting authority_liability, the resulting candidate values are wrong for the state as it actually exists today post-Candidate-C. The *mechanism* (move some budget from the dominant field into secondary off-axis fields, within the state's own real total) can likely still work — but any concrete number Gemini already proposed for IPM specifically should be treated as needing recomputation, not reused.
2. **The 0.90 figure is a real, strong pattern for the 4 target states specifically, not a taxonomy-wide law — worth stating precisely rather than either overclaiming or dismissing it.** If the reshaping search's own ripple-audit step (checking whether a candidate creates new collisions against *other* states, per this project's own standing SCD-WCS discipline) ever needs to compare against one of the 4 known exception states, that comparison state won't behave like a "typical" 0.90-sum state — worth keeping in mind if/when ripple-audit output looks anomalous for those specific four states, not a reason to distrust the audit generally.

## Bottom line

Gemini's invariant claim is a real, load-bearing pattern (93-99% true depending on which field family) that was overstated as an absolute rule — the actual 4 states this project targets happen to be on the correct side of it, so the reshaping approach's core arithmetic isn't broken, but at least one specific input value (IPM's `authority_liability`) is stale and needs correcting before any candidate numbers derived from it are trusted. Recommend: correct the IPM baseline, drop the "for every state" framing in favor of "for the 4 target states, confirmed directly," and only then consider starting a candidate search — none of that decided here, reported for Pete's call as instructed.
