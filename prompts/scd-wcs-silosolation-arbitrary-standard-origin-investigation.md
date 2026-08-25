# Origin and Rationale of the `silosolation` / `the_arbitrary_standard` Tie — Fact-Finding Only

Date: 2026-08-24. Requested before any candidate work on this pair. **No direction proposed, no candidate vectors drafted.** This is source material for a decision only Pete has standing to make: differentiate the two states fully, or keep them tied and reshape together.

---

## 1. Origin — git log / git blame, both files

**The vector tie is a confirmed, single-commit, mechanical artifact — not an individual authoring judgment that these two states represent the same real-world pattern.**

Both states were introduced together in the very first commit (`c79179b`, "scoring engine complete + PRV3 session protocol"), at which point they had **genuinely different `liability_axes` metadata**:
- `silosolation`: `["Operational & Structural", "Financial & Economic", "Cultural & Behavioral"]`
- `the_arbitrary_standard`: `["Cultural & Behavioral", "Talent & Retention", "Legal & Compliance"]`

No numeric `dimensional_vector` existed yet at that point (the schema only had `signal_weight`/`liability_axes` at this stage). Both states did already share `primary_dimension="Alliance"` and `signal_weight="medium"`.

**The tie was created in commit `253b345`** ("Session 17: global tier standardization (HIGH 0.60/0.10, MEDIUM 0.45/0.15, LOW/CLUSTER 0.35/0.25/0.15)..." — 2026-05-17). This commit introduced `dimensional_vector` for the first time across the whole taxonomy via a companion script, `tools/patch_v10_tier_standardization.py`, whose own docstring states the mechanism plainly:

```
HIGH  (11): primary=0.60, all others=0.10
MEDIUM(21): primary=0.45, all others=0.15
LOW/CLUSTER(15): primary=0.35, secondary=0.25, all others=0.15
```

The script's `TIERS` table maps `(state_id, primary_dimension)` pairs mechanically to one of three fixed template vectors. `silosolation` and `the_arbitrary_standard` — along with `the_second_close` — all appear in the same `MEDIUM` list with `primary="alliance_liability"`, immediately adjacent to each other in the source. The diff confirms all three states received the byte-identical vector `(0.15, 0.15, 0.15, 0.15, 0.45, 0.15, 0.15, 0.15)` **in the same commit, in the same patch run** — not authored individually and later found to coincide.

The companion doc from that session, `tools/phase2_score_distribution_v10.md`, frames the whole exercise as a taxonomy-wide uniformity pass aimed at score-distribution and "sink" behavior (which state absorbs false-rank-1s), not as per-state textual authoring — it explicitly discusses the *side effects* of tier standardization creating new dominant sinks, with no discussion anywhere of `silosolation`/`the_arbitrary_standard` individually or of whether their real-world scenarios are similar.

**Conclusion on origin: the vector tie is an artifact of a global mechanical tier-assignment procedure applied to all 47 states at once, keyed only on `(primary_dimension, signal_weight)` — a metadata coincidence, not a considered judgment that these two states are conceptually similar.**

**The salience tie is different in kind — independent convergence, not a shared origin.** `silosolation`'s Authority secondary was raised 0.4→2.0 in commit `cf2abeb` (2026-08-21, 11:52am). `the_arbitrary_standard`'s was raised 0.4→2.0 separately, in commit `e9a2750` (2026-08-21, 4:49pm — same day, ~5 hours later). Both commits' own code comments show independent, real margin searches against each state's own text, arriving at the same magnitude by coincidence — `e9a2750`'s comment explicitly notes this: *"matches silosolation's own shipped score exactly on ALL-AS-01 (0.710304)"*, flagged as an observed coincidence at ship time, not a target. So: **the vector tie is one mechanical event; the salience tie is two independent authoring events that happened to land on the same number.**

## 2. Prior discussion — every mention treats the tie as a problem, never as intentional design

Searched all 14 `prompts/` files referencing `silosolation` plus `tools/_mob.txt`. No file, anywhere, characterizes the tie as deliberate or desirable. Representative direct evidence:

- `cf2abeb`'s own code comment (in `engine/data/salience.py`, not just a prompts/ doc): *"previously shared this exact tuple with the_second_close and the_arbitrary_standard — all three tied exactly on every calibration profile"* — logged as the problem the commit exists to partially fix.
- `prompts/scd-wcs-cluster-map-findings.md` lists it as "Cluster 6" among several other uniform-vector clusters found taxonomy-wide, all catalogued for potential remediation, no distinction drawn for this pair as special or intentional.
- `prompts/scd-wcs-remediation-program-v1.md` (Phase 7) frames `the_arbitrary_standard` as "the one already-diagnosed leftover" from rank-6 cleanup — explicitly a to-do item, not a closed design decision.
- `prompts/scd-wcs-remediation-tracker.md`'s own per-state rows for both states: fix-type flag "SAME-CLUSTER DIFF (confirmed)," status "SHIPPED (honest partial fix)" / "SHIPPED" — both rows explicitly describe the current state as a partial fix, with `the_arbitrary_standard`'s row stating plainly the salience tie between the two "still genuinely tied with each other" is a "separate, still-unresolved pair."
- The 2026-08-24 scope-expansion document (this session) is the first place either state's *own* text is weighed against the other's rather than just against `the_second_close` — meaning the two-way `silosolation`/`the_arbitrary_standard` question specifically (as opposed to their shared question against `the_second_close`) has never been directly investigated before this thread.

**No prior document, commit message, or code comment anywhere in the project's history asserts these two states were designed to represent the same organizational condition.**

## 3. Textual distinctness — re-read fresh, characterized precisely

**`silosolation`:** *"Teams that need each other's information to do their jobs well are operating as if they don't, each optimizing for its own metrics without visibility into how that affects anyone else. The isolation isn't hostile. It's structural, and it produces the same friction hostility would."*

**`the_arbitrary_standard`:** *"The rules that govern who gets what treatment aren't applied consistently, and the pattern of who benefits isn't accidental even if nobody designed it on purpose. People notice the inconsistency well before anyone in leadership does."*

These describe **two different organizational patterns, not variations on one theme:**

| | `silosolation` | `the_arbitrary_standard` |
|---|---|---|
| Relationship axis | Horizontal — team-to-team | Vertical — individual-to-rule/leadership |
| What's broken | Information flow / cross-functional visibility | Consistency of rule application |
| Who's affected | Teams/functions as units | Individual people receiving differential treatment |
| The "gap" named | A structural blind spot between peer units | An awareness gap between rank-and-file and leadership |
| Real-world instance | Two departments not coordinating on shared work | A promotion/discipline decision applied unevenly across people |

**Genuine overlap exists, but it's structural/rhetorical, not substantive:** both use the taxonomy's recurring "not deliberate but still real" disclaiming construction (`silosolation`: "isn't hostile... structural"; `the_arbitrary_standard`: "isn't accidental even if nobody designed it on purpose") — a phrasing pattern shared with several other states in this taxonomy (`culture_drift`'s "nobody decided to abandon the values," already noted in the tracker as a recognized recurring shape). Both also carry "Governance Discipline" as one of two `asset_axes`, giving them a shared institutional/structural flavor. But the actual scenario, actors, and mechanism in each text are unrelated — one is about cross-team coordination, the other about fairness in rule enforcement. **This reads as two genuinely distinct organizational patterns that happen to share a rhetorical register and a nominal "Alliance" classification, not one pattern with two names.**

## 4. Calibration-suite evidence — the suite treats them as distinct scenarios; it just never tests them against each other

Pulled both states' three dedicated profiles directly from `engine/test_profiles_alliance.py`:

- `silosolation`'s profiles (`ALL-SI-01/02/03`): a manufacturing company's Ops/Finance dependency deadlock, a tech company's Sales/Engineering prioritization conflict, and a vague "departments don't communicate well" impression. Multi-state companions: `the_fracture`, `the_lost_map`.
- `the_arbitrary_standard`'s profiles (`ALL-AS-01/02/03`): an EEOC-triggered promotion-review finding undocumented, differential treatment; a PIP applied to one employee but not another for the same behavior; a vague "rules apply differently" impression. Multi-state companions: `the_inside_track` (both times).

**These are substantively different fact patterns, clearly authored with different real-world scenarios in mind** — one is a coordination-failure story, the other is a fairness/EEOC-adjacent story. Confirmed by grepping every `test_profiles_*.py` file in `engine/` for both state names: `silosolation` co-occurs only with `the_fracture`, `the_lost_map`, and `distributed_culture_fragmentation` across the full suite; `the_arbitrary_standard` co-occurs only with `the_inside_track`, `disparate_impact_architecture`, `decision_blindness`, and `sequential_decision_blindness`. **The two states never appear together in any profile's expected output, anywhere in the suite, and their companion-state sets are completely disjoint.**

**But no profile anywhere expects the two states to be distinguished from each other directly** — there is no test case where both `silosolation` and `the_arbitrary_standard` are plausible candidates and the suite checks that the engine picks the textually-correct one. Each state's own profiles are lenient enough (`pass_criterion` defaults to cluster/top-3, not strict rank-1) that the suite has never been positioned to catch the fact that the two states are mathematically identical underneath their distinct scenario text. **The suite's authors clearly conceived of these as different situations; the suite's own leniency is simply why the tie has never surfaced as a failure.**

---

## Bottom line — facts only, no recommendation

1. **Origin:** the vector tie is a one-commit, mechanical side effect of a global 47-state tier-standardization pass keyed on shared metadata (`Alliance` + `medium`), not an individual design choice about these two states. The salience tie is two independent, coincidental convergences on the same margin-search result, five hours apart, same day.
2. **Prior discussion:** every single mention across 14 files and two shipped commits treats the tie as an open problem or partial fix — never as intentional.
3. **Textual distinctness:** the two states describe genuinely different organizational patterns (horizontal team-coordination failure vs. vertical rule-application inconsistency), sharing only a rhetorical disclaiming pattern and a nominal Alliance classification — not a case of near-duplicate content.
4. **Calibration suite:** all 6 dedicated profiles for both states describe clearly distinct real-world scenarios with fully disjoint companion-state sets, but the suite has never contained a test that requires distinguishing the two from each other directly — which is why the tie has persisted without ever failing calibration.
