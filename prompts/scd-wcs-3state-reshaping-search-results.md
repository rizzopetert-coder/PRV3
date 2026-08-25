# SCD-WCS 3-State Vector Reshaping Search — Full Results

Date: 2026-08-24. Pete-approved search, per Gemini's architecture review + this session's baseline verification. Scope: `built_to_fail`, `invisible_performance_management` (IPM), `the_second_close`. `the_uninitiated` untouched throughout, per explicit instruction. **Dry-run only — nothing written to `engine/data/states.py`. Stopping before writing, per mandatory safeguard #4, and reporting the fallback-trigger outcome below rather than proceeding.**

## Bottom line

**No candidate found across this search is safe to ship. The mandatory fallback trigger (safeguard #5) fires: redistribution within each state's own real 0.90 liability budget cannot bring `built_to_fail`'s and IPM's false-rank-1 counts down together — every move that helps one makes the other substantially worse. Full taxonomy-wide re-authoring is needed for this cluster, not a marginal within-budget fix. This confirms, via a fresh and independently rigorous path, the same conclusion this program's own earlier whack-a-mole investigation already reached.**

---

## Baseline, confirmed fresh (not cited from the tracker)

Full 175-profile sweep against the live pipeline, current vectors:

| State | False-rank-1 | Own-profile result |
|---|---|---|
| `built_to_fail` | 62/175 (35.4%) | Wins all 3 own profiles cleanly (rank 1, score 0.97-0.99) |
| `invisible_performance_management` | 43/175 (24.6%) | Loses all 3 own profiles to `built_to_fail` (own_rank 2, ~0.02-0.05 margin) |
| `the_second_close` | 5/175 (2.9%) | Loses all 3 own profiles badly to `built_to_fail` (own_rank 10, own_score 0.703 vs. `built_to_fail`'s 0.860 — a 0.157 gap) |

**`built_to_fail`'s count is notably higher than the last recorded figure (49/175, 28%)** — plausibly shifted by Candidate C's edit to IPM this session, which reduced IPM's competing aptitude signal and may have made `built_to_fail` relatively more dominant in cases where they compete. Not chased down further here, noted as context.

All three states' own dedicated profiles that lose, lose specifically **to `built_to_fail`** — confirming it's the common attractor behind all three states' problems, not three independent issues.

## Textual grounding gate — checked before any value was proposed, per safeguard #1

Real `descriptive_prose` pulled fresh for all three states:

**`built_to_fail`**: *"The role's scope exceeds what any reasonable allocation of resources could support, and each person who holds it is told to make it work rather than given what making it work would require..."* — a purely single-dimension aptitude/capability-scope problem. No real alliance or attitude content. At most a very weak, arguable authority undertone ("told" vs. "given"). **No strong grounding found for any off-axis redistribution.** Flagged before any value was tested, not after.

**IPM**: *"...carries no evidentiary weight when a decision needs defending. This isn't concealment. It's an absence of documentation..."* — real authority-adjacent content already present (defending a decision, evidentiary weight), grounding a modest aptitude→authority shift specifically. No alliance or attitude content.

**`the_second_close`**: *"...the same underlying issue that forced the first renegotiation is resurfacing. Whatever the first fix addressed, it wasn't the actual cause."* — real aptitude-adjacent content (misdiagnosis of the actual root cause) alongside the dominant alliance signal, grounding a modest alliance→aptitude shift specifically.

## Full candidate search — all 5 tested, not just the best

Each candidate: dry-run, in-memory only, full 175-profile re-sweep, own-profile check, and a full 58-state × 175-profile drift comparison against baseline (confirming **zero score change on any unrelated state** in every case, reported per candidate below).

| Candidate | State | Change | Own state's false-rank-1 | `built_to_fail`'s false-rank-1 | `the_second_close`'s false-rank-1 | Own-profile rank | Drift on other 57 states |
|---|---|---|---|---|---|---|---|
| IPM-1 | IPM | apt 0.45→0.40, auth 0.20→0.25 | 43→38 (−5) | 62→**72 (+10)** | 5→5 (+0) | 2,2,2 → 2,**5**,2 (one profile regressed) | Zero |
| IPM-2 | IPM | apt 0.45→0.35, auth 0.20→0.30 | 43→**17 (−26)** | 62→**78 (+16)** | 5→6 (+1) | 2,2,2 → **4,6,4** (all three regressed) | Zero |
| BTF-1 (weak grounding, tested for information only) | `built_to_fail` | apt 0.60→0.55, auth 0.10→0.15 | 62→**82 (+20, worse)** | n/a (self) | 5→5 (+0) | 1,1,1 → 1,1,1 (unchanged) | Zero |
| SC-1 | `the_second_close` | all 0.45→0.40, apt 0.15→0.20 | 5→**7 (+2, worse)** | 62→62 (+0) | 43→41 (−2) | own_rank 10→8, own_score 0.703→0.714 (still far from winning) | Zero |
| SC-2 | `the_second_close` | all 0.45→0.35, apt 0.15→0.25 | 5→**7 (+2, worse)** | 62→62 (+0) | 43→38 (−5) | own_rank 10→8, own_score 0.703→0.721 (still far from winning) | Zero |

**Zero drift confirmed on every candidate, across all 58 states × 175 profiles, excluding the candidate state itself** — the redistribution mechanism is real and precisely isolated when tested; the problem is not measurement noise or an implementation bug, it's the underlying dominance structure.

### Why 5 candidates, not 12 per state

The paper_shield precedent's 12-candidate search was appropriate there because the result was genuinely close and needed fine discrimination between similar-magnitude options. Here, the pattern across all 5 tests is unambiguous and consistent in direction, not borderline: every IPM-improving move drives `built_to_fail` substantially worse; weakening `built_to_fail` makes its own metric worse, not better; every `the_second_close` move fails to meaningfully close its own 0.157-point gap and makes its own metric worse in the process. Additional candidates at intermediate magnitudes would very likely interpolate between these same results, not reverse the qualitative finding. Stated plainly rather than silently narrowing scope.

## Full calibration regression check — held, but doesn't tell the whole story

Ran the complete 175-profile calibration suite (not just the 3-state sweep) under IPM-2, the single most aggressive candidate tested: **171/175, unchanged from baseline** — same overall pass rate. This confirms the mandatory safeguard #3 baseline holds at the official calibration metric's own lenient (cluster/top-3/prominence) pass bar.

**This is the same gap this whole program has repeatedly found and documented: the calibration suite's lenient pass criterion doesn't fully reflect the live margin gate's actual rank-1 behavior.** IPM-2 shows an unchanged 171/175 *and* a real, substantial 16-profile increase in `built_to_fail`'s false-rank-1 rate simultaneously — both are true at once, because the calibration suite doesn't require rank-1 to pass. Reported precisely rather than letting the reassuring 171/175 number stand alone.

## Fallback trigger — fired, per safeguard #5's own stated condition

*"If redistribution within the 0.90 budget can't bring built_to_fail/IPM's false-rank-1 counts down without causing more than 3 non-high-confidence regressions, stop cleanly and report that full re-authoring is needed instead."*

No candidate brings **both** `built_to_fail`'s and IPM's counts down together — the two moved in opposite directions in every test that touched either state directly or indirectly. `built_to_fail` itself has no viable candidate at all (no textual grounding, and the one test run made its own metric worse, not better). `the_second_close`'s own gap is too large (0.157) for any budget-neutral move to meaningfully close, confirmed by two separate candidates barely moving its own score.

**This condition is met. Stopping cleanly, as instructed, rather than forcing a marginal fix.**

## What this confirms, connecting back to the program's own prior work

This is a fresh, independent confirmation — via real dry-run testing against the live 175-profile pipeline, not just theoretical reasoning — of what this session's earlier taxonomy-wide re-authoring scoping already concluded (`prompts/phase3-item10-scd-wcs-taxonomy-reauthoring-scoping.md`): `built_to_fail`'s dominance cannot be fixed via salience or constrained within-budget vector redistribution; it requires genuine re-authoring. The 3-state constrained-search approach Gemini proposed was worth testing rigorously rather than dismissed on theory alone — and the rigorous test confirms the same conclusion the earlier whack-a-mole finding already reached, now with concrete, specific numbers for this exact cluster of 3 states rather than a general pattern claim.

## Not done, per explicit instruction

Nothing written to `engine/data/states.py`. `the_uninitiated` not touched, proposed, or searched. No candidate recommended for shipping. Pete's call on whether/when to open the full taxonomy-wide re-authoring project this finding points toward.
