# SCD-WCS Full Taxonomy-Wide Re-Authoring Program

Durable plan file for the multi-phase re-authoring program confirmed necessary by the 2026-08-24 session (3-state constrained search, full scoping pass, two independent Gemini-review verifications — see `prompts/scd-wcs-remediation-tracker.md`, `prompts/scd-wcs-full-reauthoring-scope.md`, `prompts/scd-wcs-3state-reshaping-search-results.md`, `prompts/scd-wcs-gemini-review-verification.md`, `prompts/scd-wcs-scope-expansion-gemini-verification.md`). This file is the working tracker for the program itself — read it first each session this program is active, update it as phases complete. `the_uninitiated` stays completely out of scope throughout, per standing instruction — separate track.

---

## Scope

Two shared-vector clusters plus one standalone state, six states total:

- **Cluster A — `built_to_fail` / `the_paper_tiger`.** Share an exact `dimensional_vector` (aptitude-dominant, 0.60/0.10/0.10/0.10/0.10/0.10/0.10/0.10). Differentiated today only by `the_paper_tiger`'s individually reshaped salience.
- **Cluster B — `the_second_close` / `silosolation` / `the_arbitrary_standard`.** Share an exact `dimensional_vector` (alliance-dominant, 0.15/0.15/0.15/0.15/0.45/0.15/0.15/0.15). Differentiated today only by salience — `silosolation` and `the_arbitrary_standard` share an *identical* salience profile to each other, still a live unresolved tie between those two specifically.
- **Standalone — `invisible_performance_management` (IPM).** Unique vector, no shared-vector sibling. In scope because it is one of the two confirmed real dominance attractors this program exists to fix.

## Real attackers vs. victims — confirmed, not assumed

Only three of the six states are independent false-rank-1 sources. The other three are shared-vector siblings losing profiles *to* the attackers, not attractors in their own right:

| Role | State | Evidence |
|---|---|---|
| **Attacker** | `built_to_fail` | 62/175 (35.4%) false-rank-1, freshest full sweep, 2026-08-24 |
| **Attacker** | `invisible_performance_management` | 43/175 (24.6%) false-rank-1, freshest full sweep, 2026-08-24 |
| **Attacker** | `the_second_close` | 5/175 (2.9%) false-rank-1, freshest full sweep, 2026-08-24 (composition: 2 genuine external wins vs. `the_fracture` + 3 internal tie-artifact wins vs. `silosolation`) |
| Victim | `the_paper_tiger` | Shares `built_to_fail`'s vector. No independent global false-rank-1 count — loses its own dedicated profiles *to* `built_to_fail` (own_rank 8-9, confirmed 2026-08-24 Gemini-verification pass). |
| Victim | `silosolation` | Shares `the_second_close`'s vector. Loses its own 3 dedicated profiles to `the_second_close`'s tie-break (already counted inside `the_second_close`'s 5/175 above) and to Track 2 (`built_to_fail`/IPM). Not an independent attractor. |
| Victim | `the_arbitrary_standard` | Same shape as `silosolation` — tie-break loser to `the_second_close`, own profiles lost to Track 2. Not an independent attractor. |

This distinction matters for sequencing: fixing the two clusters means re-authoring the attacker's vector (which the victim currently borrows) in a way that resolves *both* the attacker's over-dominance and gives the victim(s) a genuinely distinct, text-grounded shape of their own — not two separate problems, one shared-vector problem per cluster.

## Why constrained single-field moves are ruled out

The 2026-08-24 3-state constrained search (`prompts/scd-wcs-3state-reshaping-search-results.md`) tested exactly this — redistributing liability mass *within* each state's own fixed 0.90 total, guided by real textual grounding, across 5 candidates spanning `built_to_fail`, IPM, and `the_second_close`. Result: **the mandatory fallback trigger fired.** Every candidate that reduced IPM's false-rank-1 count drove `built_to_fail`'s substantially worse (IPM 43→17 traded directly for `built_to_fail` 62→78, in the most aggressive candidate tested) — confirmed empirically, not theoretically, with zero drift on the other 57 states in every case, meaning the mechanism is real and precisely isolated, not measurement noise. `built_to_fail` itself has no textual grounding for any off-axis redistribution at all (its prose is purely single-dimension aptitude/capability-scope content). `the_second_close`'s own gap against `built_to_fail` (0.157 own-profile score) barely moved under any tested magnitude.

This is the signature of a genuine zero-sum competition within a fixed budget: moving liability mass around only changes who wins a shared pool of signal, it cannot create new distinguishing signal. **Full re-authoring — changing the total liability budget, extending redistribution to asset fields, and re-deriving salience jointly with any new vector shape — are the only levers left that could plausibly break that zero-sum structure rather than just relocating it again.** This program exists to use those three levers deliberately, in sequence, with a real fallback protocol if they also fail.

---

## Phases 1-5

**Phase 1 — Grounding audit.** Read each of the six states' full `descriptive_prose` fresh, independent of current vector values. Document what dimensional emphasis the text actually supports, compare against the current `dimensional_vector`/`SALIENCE_PROFILES`, and flag every divergence precisely — this is the actionable signal the rest of the program works from. No candidate vectors. Executed below.

**Phase 2 — Candidate vector authoring.** For each state where Phase 1 found a real divergence, author candidate `dimensional_vector` values grounded directly in the cited text — not numerically convenient values chosen to pass calibration. Both clusters authored together (attacker + its victim(s) in the same pass, not sequenced), since the two states in each cluster are structurally coupled. Explore all three re-authoring levers confirmed in scope (total budget, asset-field shape, axis choice) — not just liability redistribution within 0.90. Gemini review happens here, not before (see below).

**Phase 3 — Joint salience derivation.** Re-derive `SALIENCE_PROFILES` for every touched state alongside its new vector, not reused from the old vector's calibration. The 2026-08-24 Gemini-review-verification pass found composing a new vector with old, uncoordinated salience actively made `the_paper_tiger`'s own-profile rank worse, not better — salience and vector are coupled, not sequential, for any state being re-authored.

**Phase 4 — Dry-run testing.** Full 175-profile sweep, own-profile check, and full 58-state × 175-profile drift comparison against baseline for every candidate — same rigor as the 3-state search. Nothing written to `engine/data/states.py` or `engine/data/salience.py` until a candidate clears this phase and Pete confirms.

**Phase 5 — Fallback protocol.** If Phase 4 finds no candidate set improves the real attackers' false-rank-1 counts without unacceptable regression elsewhere (mirroring the 3-state search's own fallback trigger, generalized to the full 3-lever search space), stop cleanly and report rather than force a marginal fix. Includes the standing caution already on record: the 171/175 calibration suite is confirmed to under-report real rank-1 degradation, so Phase 4's own full false-rank-1 sweep is the real gate, not the calibration suite's pass/fail count alone.

## Gemini's role — deliberately deferred to Phase 2+

Not brought in during Phase 1. Two separate stale-input findings this program has already caught — Gemini's IPM baseline (`authority_liability=0.25`, actually 0.20 post-Candidate-C) and its `the_paper_tiger` proposal (values summing to 0.90 with no room left for Alliance, breaking Gemini's own stated invariant) — both traced to Gemini working from context that predated a live-code check. The pattern both times: Gemini's *mechanism* reasoning held up, but a specific *input value* didn't. Phase 1 exists to produce a verified, live-pulled baseline first, so Gemini's Phase 2 architecture/candidate review has a correct starting point rather than needing its own inputs corrected after the fact a third time.

---

## Not done yet

No candidate vectors proposed. No code touched. No Gemini submission drafted. `the_uninitiated` untouched, out of scope. Phase 1 findings below; Phase 2 is a separate future pass, not started here.

---

## Phase 1 — Grounding Audit Findings

Date: 2026-08-24. All `descriptive_prose`, `dimensional_vector`, and `SALIENCE_PROFILES` values pulled fresh via live Python import from `engine/data/states.py` / `engine/data/salience.py` for this pass — confirmed unchanged from the same-day verification pass immediately prior (no commits have touched either file since `322ea93`), so vector/salience values are reused rather than re-pulled, per instruction; `descriptive_prose` text is read here for the first time at full length for all six states in one pass.

### `built_to_fail`

**Full text:** *"The role's scope exceeds what any reasonable allocation of resources could support, and each person who holds it is told to make it work rather than given what making it work would require. The organization treats each departure as an individual hiring failure rather than a structural one. The next person inherits the same impossible math."*

**Text-supported emphasis:** Purely single-dimension. Sentence 1 is a direct capability/resource-scope claim — Aptitude, unambiguous. Sentence 3 restates the same structural-scope point. Sentence 2 ("treats each departure as an individual hiring failure rather than a structural one") is the only candidate for secondary content — a misattribution/misdiagnosis framing structurally similar to `the_second_close`'s "wasn't the actual cause" — but it describes the *organization's* explanatory error about the role, not a second dimension of the role's own condition; there is no rules/governance, relationship, or motivation content anywhere in the text. **Confirmed again, a third time this program: no secondary axis is textually grounded for this state.**

**Current vector/salience:** apt_lia 0.60 (all others 0.10 floor); salience standard flat aptitude-primary (2.5/2.5/0.4/0.4/0.4/0.4/0.4/0.4), unmodified.

**Divergence:** None on axis choice — the vector's aptitude-primary shape is textually correct. The only viable lever for this state is **magnitude/concentration**, not shape: whether 0.60 is sharper than it needs to be, or whether the total budget itself (not just its allocation) should change. This is Phase 2's hardest open question, carried forward as already flagged in the scoping document — a mechanical text-to-vector mapping cannot resolve it, since there is no missing dimension to encode, only a magnitude judgment.

### `the_paper_tiger`

**Full text:** *"A performance problem has been managed verbally for long enough that the written record no longer matches what everyone privately knows. When the organization finally needs to act on documented cause, it discovers it has been managing one employee on paper and a different one in practice. The gap surfaces in front of the people with the least patience for it."*

**Text-supported emphasis:** **Authority-dominant**, not Aptitude. "Written record," "documented cause," "managing one employee on paper" are the same evidentiary/documentation vocabulary this taxonomy already uses to mark Authority content elsewhere (compare IPM's "carries no evidentiary weight," "absence of documentation" below — near-identical thematic register). Secondary: a real Attitude signal — the say/do gap between what is verbally managed and what is formally documented is a performative discrepancy, the same shape this taxonomy already encodes as Attitude elsewhere (e.g. `the_diversity_ceiling`'s stated-vs-actual gap). No Aptitude content at all — nothing about capability, resource scope, or skill anywhere in this text.

**Current vector/salience:** Identical to `built_to_fail` — apt_lia 0.60 dominant, all else 0.10 floor. Salience individually reshaped: attitude 1.5 (highest), authority 1.0, aptitude 1.0, alliance 0.4 (lowest).

**Divergence: the largest and cleanest in this entire audit.** The vector's dominant field (Aptitude) has zero textual support for this state — it is inherited wholesale from `built_to_fail`, a state with a completely unrelated narrative (resource scope vs. documentation gap). The existing salience fix already shows the taxonomy's own authors reaching for the correct axes (Attitude highest, Authority elevated, Aptitude *de-emphasized relative to the standard template* by pairing 1.0 with 1.0 instead of leaving Aptitude at the template's dominant 2.5) — but salience cannot fully correct a vector whose *shape* is wrong, only reweight within it, and the taxonomy's own documented mechanism (silosolation's row, same file) confirms salience alone cannot efficiently overcome a shared vector's structural dominance. **This state needs an actual vector re-shape to Authority-primary with an Attitude secondary, not a salience adjustment layered on a borrowed Aptitude-primary shape.**

### `invisible_performance_management`

**Full text:** *"A manager's read on an underperforming employee is accurate but was never written down, so it carries no evidentiary weight when a decision needs defending. This isn't concealment. It's an absence of documentation that turns a sound judgment into an exposed one."*

**Text-supported emphasis:** **Authority-dominant**, and the text goes further than most states in this taxonomy by *explicitly ruling out* an Aptitude problem — "accurate," "sound judgment" are direct, unambiguous statements that the manager's underlying capability/diagnostic read is *not* the deficiency. The entire liability described is evidentiary/documentation-standing (Authority): the judgment exists and is correct, but carries no institutional weight because it isn't recorded. No Alliance or Attitude content anywhere.

**Current vector/salience:** apt_lia 0.45 (dominant), auth_lia 0.20 (secondary), all_lia 0.15, att_lia 0.10. Salience standard flat aptitude-primary, unmodified.

**Divergence: the starkest in the whole set, more so than `the_paper_tiger`'s.** The current vector's dominant field is Aptitude — the exact dimension the text explicitly and directly disclaims ("accurate... sound judgment"). Authority, the dimension the text is entirely about, sits at less than half the dominant field's weight (0.20 vs 0.45). This is not a missing-secondary-axis problem like `the_second_close`'s — it is the dominant axis itself being on the wrong dimension, with the text providing no support for treating Aptitude as a liability at all. This is the single clearest text-to-vector contradiction found in this audit and the primary actionable signal for Phase 2's IPM work.

### `the_second_close`

**Full text:** *"A relationship or agreement was renegotiated once already, and the same underlying issue that forced the first renegotiation is resurfacing. Whatever the first fix addressed, it wasn't the actual cause. The people involved are less willing to extend trust a second time."*

**Text-supported emphasis, sentence by sentence:**
- S1 ("A relationship or agreement was renegotiated once already") — Alliance: establishes the relational frame.
- S2 ("the same underlying issue... is resurfacing") — connective, sets up the causal claim in S3.
- S3 ("Whatever the first fix addressed, it wasn't the actual cause") — **Aptitude**, and substantive, not incidental. This is a direct, unhedged claim of diagnostic failure: the wrong problem was identified and fixed the first time. It is structurally the same kind of misattribution claim as `built_to_fail`'s "individual hiring failure rather than structural" (see above) — but here it is the narrative's causal engine, not a side remark.
- S4 ("The people involved are less willing to extend trust a second time") — Alliance: the consequence of S1-S3, trust eroding specifically *because* the real issue was never fixed.

**Formalizing the misdiagnosis signal:** the prior session's scope-expansion document (`prompts/scd-wcs-full-reauthoring-scope.md`, Section 3) flagged this as "a real, substantive aptitude signal... a stronger, more central signal than the constrained search's candidates treated it as." Precisely stated: **half of this state's four-sentence prose (S2-S3, functionally) exists to explain *why* the relationship is failing a second time — because the underlying diagnostic work was wrong, not because the relationship itself is inherently fragile.** The Alliance content (S1, S4) describes the *symptom and setting*; the Aptitude content (S3) describes the *mechanism*. This is a materially stronger claim than "alliance with an aptitude undertone" — it is a state whose narrative logic is Alliance-framed but Aptitude-caused. A dual-axis vector (Alliance-primary, Aptitude-secondary at real, non-floor magnitude) is textually warranted, not merely permissible.

**Current vector/salience:** all_lia 0.45 (dominant), apt_lia/auth_lia/att_lia all at 0.15 — the bare floor, zero differentiation between Aptitude and the two dimensions (Authority, Attitude) that have no textual support at all. **This is the divergence:** the text's real, substantive secondary signal (Aptitude, via S3) is currently encoded identically to two dimensions with no textual grounding whatsoever. A text-faithful vector would differentiate Aptitude from Authority/Attitude, not treat all three as equivalent floor noise.

### `silosolation`

**Full text:** *"Teams that need each other's information to do their jobs well are operating as if they don't, each optimizing for its own metrics without visibility into how that affects anyone else. The isolation isn't hostile. It's structural, and it produces the same friction hostility would."*

**Text-supported emphasis:** **Alliance-dominant** (cross-team collaboration failure, information-sharing breakdown) — clear and consistent with the current vector's dominant field. Secondary: **Authority** — "structural" is doing real work here, explicitly distinguishing this state from a motivation/relationship failure ("isn't hostile") and attributing the isolation to organizational design/visibility structures instead. "Optimizing for its own metrics" reinforces a governance/accountability-structure reading (metrics and visibility are Authority-axis concerns in this taxonomy's own established vocabulary, matching `planning_authority_gap`'s "Operational & Structural" framing already cited as precedent for this state's shipped salience choice). No Aptitude or Attitude content.

**Current vector/salience:** Identical to `the_second_close` — all_lia 0.45 dominant, everything else 0.15 floor (Authority not actually elevated in the vector). Salience: Authority already raised 0.4→2.0 (dual-elevated with Alliance).

**Divergence:** The salience fix is textually correct in *direction* (Authority is the real secondary axis) but the tracker's own record already confirms it is insufficient in *mechanism* — `silosolation` still loses all 3 of its own dedicated profiles to `the_second_close` even at extreme salience magnitude, because the underlying vector's Authority field is still at the bare 0.15 floor, identical to `the_second_close`'s own untouched Authority field. Consistent with `the_paper_tiger`'s finding: **the text argues for raising Authority in the actual vector shape, not just its salience weight** — the existing fix already correctly identified the axis and has already been shown, empirically, not to be sufficient on its own.

### `the_arbitrary_standard`

**Full text:** *"The rules that govern who gets what treatment aren't applied consistently, and the pattern of who benefits isn't accidental even if nobody designed it on purpose. People notice the inconsistency well before anyone in leadership does."*

**Text-supported emphasis:** **Authority-dominant**, arguably more purely so than `silosolation`. "Rules that govern," "applied consistently," and especially "before anyone in leadership does" are direct governance/rule-enforcement/leadership-visibility content — squarely Authority. "Who gets what treatment... isn't accidental" carries a thin Alliance-adjacent undertone (differential treatment of people), but the sentence's actual subject is the *pattern's non-randomness*, not a relational dynamic between people — weaker Alliance grounding than `silosolation`'s genuine cross-team collaboration narrative. "Even if nobody designed it on purpose" explicitly disclaims Attitude/deliberate intent, the same disclaiming shape already noted in the tracker as shared with `silosolation`'s "isn't hostile."

**Current vector/salience:** Identical to `the_second_close`/`silosolation` — all_lia 0.45 dominant, Authority at 0.15 floor in the vector. Salience: Authority raised 0.4→2.0, identical to `silosolation`'s salience.

**Divergence:** Same shape as `silosolation` — Authority is the real dominant-or-co-dominant axis textually, encoded only in salience, not in the vector itself, with the same taxonomy-documented insufficiency (salience cannot efficiently overcome a shared, untouched vector anchor). **Additionally:** `the_arbitrary_standard`'s text reads as *more* Authority-centered than `silosolation`'s (leadership visibility, rule application, vs. silosolation's genuinely cross-team Alliance narrative) — meaning if Cluster B's vector is re-authored, these two states likely need to land in textually distinguishable places from each other, not just both be nudged toward Authority-secondary from a shared Alliance-primary base. Their still-live mutual salience tie (identical Authority/Alliance salience today) is not fully resolved by the current fix and the text supports treating them as two distinct shapes, not one shape with matching salience.

---

## Summary — what Phase 1 actually found

Two states (`built_to_fail`, `silosolation`'s Alliance-primacy) have vectors that are textually *correct in dominant axis* but under-differentiated or magnitude-limited. Four states have a real, text-confirmed divergence between what the text supports and what the vector currently encodes:

- **`the_paper_tiger`** — wrong dominant axis entirely (Aptitude, should be Authority-primary/Attitude-secondary). Largest divergence.
- **`invisible_performance_management`** — wrong dominant axis entirely (Aptitude, should be Authority-primary), with the text explicitly disclaiming the axis currently encoded as dominant. Starkest divergence — text directly contradicts current shape, not merely under-represents an alternative.
- **`the_second_close`** — correct dominant axis (Alliance), but a substantive, textually-central secondary axis (Aptitude, via the misdiagnosis mechanism) is encoded at floor level, indistinguishable from two dimensions with zero grounding.
- **`silosolation`** / **`the_arbitrary_standard`** — correct dominant axis (Alliance for silosolation; arguably Authority for the_arbitrary_standard), correct secondary axis identified (Authority) but encoded only in salience, already empirically shown insufficient; the two states' texts also argue for distinguishing them from each other, not just from `the_second_close`.

No candidate vectors proposed here, per instruction. This is the input Phase 2 works from.

---

## Decision — `silosolation` / `the_arbitrary_standard` Differentiation (Pete, 2026-08-24)

**Decision: differentiate `silosolation` and `the_arbitrary_standard` fully — author two distinct vectors, ending the tie.** Full fact-finding behind this decision: `prompts/scd-wcs-silosolation-arbitrary-standard-origin-investigation.md`.

**Rationale:**
1. The shared vector originated as a mechanical artifact of a global template-mapping pass (commit `253b345`, "Session 17: tier standardization") that assigned both states the identical `(0.15,0.15,0.15,0.15,0.45,0.15,0.15,0.15)` vector purely because they shared `(primary_dimension="Alliance", signal_weight="medium")` metadata — not a content decision that these two states represent the same real-world pattern.
2. Every prior mention of the tie, across 14 `prompts/` files and both salience-fix commits (`cf2abeb`, `e9a2750`), treats it as a problem to close — never as intentional design.
3. The two texts describe genuinely different organizational patterns: `silosolation` is horizontal, team-to-team information/coordination failure; `the_arbitrary_standard` is vertical, individual-to-rule fairness and leadership-visibility failure.
4. No calibration profile has ever tested the two states against each other — all 6 dedicated profiles describe disjoint real-world scenarios with fully disjoint companion-state sets, so the tie has been invisible rather than validated by any test.

**Note on program sequencing:** no "Phase 2 — Batch 1" section exists yet in this file — the `built_to_fail`/`the_paper_tiger`/IPM candidate-authoring pass has not been executed under this program. "Batch 2" numbering here follows Pete's own framing of this dispatch and reflects that `the_second_close` was originally grouped with that cluster in the 2026-08-24 constrained search, then held back from any full-re-authoring candidate work pending this origin investigation. It does not imply Batch 1 is complete — flagged here so the numbering isn't misread later as a completed step.

---

## Phase 2 — Candidate Vectors (Batch 2)

Date: 2026-08-24. `silosolation`, `the_arbitrary_standard`, `the_second_close`. Candidate `dimensional_vector` values only — no salience derivation (Phase 3, done jointly once all three are set), no dry-run testing (Phase 4). Every value below cites the specific text supporting it; magnitude choices are flagged as provisional pending Phase 4's empirical confirmation, consistent with this program's own standing discipline that a candidate is a starting hypothesis, not a shipped value.

### `silosolation`

**Current:** alliance_liability 0.45 (dominant) / aptitude, authority, attitude all 0.15 (floor) — the shared Cluster-B template.

**Candidate:** `alliance_liability 0.35` (primary, down from 0.45) / `authority_liability 0.25` (new secondary, up from 0.15 floor) / `aptitude_liability 0.15` (unchanged) / `attitude_liability 0.15` (unchanged). All asset fields unchanged at 0.15. Liability sum: 0.90 (unchanged, within-budget redistribution — no magnitude case found for expanding this state's total).

**Citation:** Alliance stays dominant — three separate clauses carry it: "Teams that need each other's information to do their jobs well," "operating as if they don't," "the same friction hostility would [produce]." Authority becomes a real secondary, not floor noise — the text's own pivot sentence exists specifically to redirect the causal explanation away from a relational reading: *"The isolation isn't hostile. It's structural"* is a direct authorial move stating the mechanism is organizational/governance-structural, not interpersonal. "Each optimizing for its own metrics without visibility into how that affects anyone else" reinforces this — metrics and visibility are accountability-structure concerns, matching this taxonomy's own established Authority vocabulary (see `planning_authority_gap`'s parallel "Operational & Structural" framing, already cited as precedent for this state's existing salience choice). Aptitude and Attitude stay at floor — no textual grounding for either; Attitude is in fact explicitly disclaimed ("isn't hostile" rules out a motivation-based reading).

**Directly answers the framing question:** this candidate makes the vector catch up to the existing salience (Authority already at 2.0, dual-elevated with Alliance's 2.5) rather than the reverse — the salience was already correctly diagnosing Authority as real; the vector previously had nothing there for it to weight.

**Magnitude note:** 0.35/0.25 matches this taxonomy's own existing "real dual-axis" convention (the LOW/CLUSTER tier, used by 15 other states for exactly this shape — a genuine primary + genuine secondary, both text-grounded). Chosen for consistency with existing precedent rather than an arbitrary new split; Phase 4 should confirm this magnitude is sufficient to break the tie and win `silosolation`'s own dedicated profiles, not assumed.

### `the_arbitrary_standard`

**Current:** alliance_liability 0.45 (dominant) / aptitude, authority, attitude all 0.15 (floor) — same shared template as `silosolation`.

**Candidate:** `authority_liability 0.35` (new primary — axis flip, up from 0.15 floor) / `alliance_liability 0.25` (retained secondary, down from 0.45) / `aptitude_liability 0.15` (unchanged) / `attitude_liability 0.15` (unchanged). All asset fields unchanged at 0.15. Liability sum: 0.90.

**Citation:** this is a genuine axis flip, not a same-cluster secondary addition, because the text's center of gravity is Authority, not Alliance. Four of the state's textual elements are governance/rule-enforcement content: "The rules that govern who gets what treatment," "aren't applied consistently," "the pattern of who benefits isn't accidental," and — the clearest single marker — "People notice the inconsistency well before anyone in leadership does," a direct leadership-visibility/governance-awareness gap claim. Alliance is retained as a real secondary, not eliminated, because "who gets what treatment" and "who benefits" do describe a genuine differential impact on people, distinguishing this state from a pure process-compliance story. "Even if nobody designed it on purpose" disclaims Attitude, same disclaiming pattern as `silosolation`'s "isn't hostile" — both floor.

**Independent corroborating evidence, not derived from the prose itself:** this state's `asset_axes` — `["Governance Discipline", "Accountability Architecture"]` — have carried an Authority-flavored pairing since the very first commit (`c79179b`), untouched by any tier-standardization pass. `silosolation`'s asset pairing is `["Governance Discipline", "Relational Trust"]` — explicitly relational. The two states were never given matching asset-axis metadata even when their liability vectors were made identical, which independently supports treating `the_arbitrary_standard` as Authority-primary and `silosolation` as Alliance-primary/Authority-secondary, not the same shape with different labels.

**Resulting differentiation from `silosolation`:** both states now involve the same two dimensions (Alliance, Authority) but with primacy reversed — `silosolation` 0.35 Alliance / 0.25 Authority, `the_arbitrary_standard` 0.35 Authority / 0.25 Alliance. A mirrored, text-grounded distinction rather than an arbitrary numeric split.

### `the_second_close`

**Current:** alliance_liability 0.45 (dominant) / aptitude, authority, attitude all 0.15 (floor).

**Candidate:** `alliance_liability 0.55` (concentration increase, up from 0.45) / `aptitude_liability 0.20` (new secondary, up from 0.15 floor) / `authority_liability 0.15` (unchanged) / `attitude_liability 0.15` (unchanged). All asset fields unchanged at 0.15. Liability sum: **1.05 — a deliberate budget expansion, this program's first use of lever (a)** (Section 1a), not a within-0.90 redistribution.

**Citation for the Aptitude secondary:** formalized in Phase 1 — sentence 3, *"Whatever the first fix addressed, it wasn't the actual cause,"* is a direct, unhedged diagnostic-failure claim, not incidental undertone. It is the narrative's causal engine: the relationship is failing a second time specifically *because* the underlying diagnostic work was wrong the first time. Alliance (S1, "renegotiated once already"; S4, "less willing to extend trust a second time") remains the dominant frame — the state is still fundamentally about a relationship under strain — but Aptitude is the stated mechanism, not a side remark, and belongs off the floor.

**Citation and rationale for the budget expansion (not just redistribution):** this program's own prior empirical work already tested a within-budget dual-axis move for this exact state and found it insufficient. `SC-2` (the 2026-08-24 3-state search) tested alliance 0.45→0.35 / aptitude 0.15→0.25 — functionally the same LOW/CLUSTER-convention shape now proposed for `silosolation` above — and found `the_second_close`'s own-profile rank moved only 10→8, still losing badly to `built_to_fail` (own_score 0.703→0.721, a 0.157-point gap barely dented). Section 4 of the scoping document already diagnosed why: `the_second_close`'s dominant field (0.45) is structurally *diffuse* relative to `built_to_fail`'s sharp 0.60 concentration, and weighted cosine similarity rewards concentration — no amount of within-budget redistribution can close a gap that is fundamentally about peak sharpness, not axis choice. The scoping document's own Section 5 question 1 flagged this directly: raising the total budget, not just reallocating it, is the one untested lever for this state. **0.55 is chosen as a middle position, not `built_to_fail`'s full 0.60**, because `the_second_close` is genuinely dual-axis (per the Aptitude finding above) rather than single-axis like `built_to_fail` — a real secondary claims some of the budget increase rather than all of it going to sharpen Alliance alone. For reference, this taxonomy's own HIGH tier (single-axis, 0.60/0.10) is used by other pure Alliance-primary states (`the_fracture`, `decision_blindness`); 0.55 sits deliberately just under that ceiling to reflect this state's real secondary content, not at the ceiling itself.

**Flagged explicitly: this is the first candidate in this program that changes a state's total liability budget, not just its allocation.** Phase 4 needs to confirm this actually improves `the_second_close`'s own-profile standing without disproportionate drift elsewhere — a budget expansion is a larger structural move than anything tested in the 3-state search, and untested at this magnitude.

---

## Not done yet (Batch 2)

No salience derived for any of the three states (Phase 3). No dry-run testing (Phase 4) — none of these candidates have been run against the live pipeline. Nothing written to `engine/data/states.py`. `the_uninitiated` untouched, out of scope. Batch 1 (`built_to_fail`/`the_paper_tiger`/IPM) not started.

---

## Verification — does anything in the scoring engine assume a fixed/capped vector sum?

Date: 2026-08-24. Requested before `the_second_close`'s Batch 2 candidate (liability sum 1.05, vs. the 0.90 convention 54/58 states follow) proceeds any further. **No changes made — read-only verification.**

**Answer: No.** Nothing in `rank_states()`, the salience-pairing logic, or SCD-WCS's normalization math assumes, requires, or is calibrated against a fixed state-vector total. Checked exhaustively, not just at the formula level:

1. **`rank_states()` / `_weighted_cosine_similarity` (`engine/accumulation.py:524-593`).** A state's `dimensional_vector` is read in exactly one place in the entire engine — line 573, `profile_dict = profile.dimensional_vector.as_dict()` — and used directly as `vec_B` in the weighted cosine formula: `sim = sum(w*A*B) / (sqrt(sum(w*A^2)) * sqrt(sum(w*B^2)))`. The denominator's `sqrt(sum(w * vec_B ** 2))` term computes each state's own magnitude fresh, per state, from whatever values it actually holds — there is no external normalization constant, no division by an assumed total, no reference to 0.90 or any other fixed budget anywhere in the function. This is also *why* the earlier scale-invariance test held empirically (uniformly scaling `the_second_close`'s vector by ×1.3 left its score unchanged) — the formula is self-normalizing per-vector by construction, not because of an assumed fixed sum.
2. **Salience-pairing (`SALIENCE_PROFILES` → `rank_states()`'s `salience_weights` parameter).** Consumed as a flat per-field multiplier dict (`w = np.array([sw.get(f, 1.0) ...])`), applied identically to both the numerator cross-term and both halves of the denominator. No sum-based logic, no dependency on the paired state's vector total.
3. **`engine/contract.py`'s `_compute_asset_score()` / `_compute_liability_score()`.** These do divide by a total (`total_liability / total_all`), but operate on the **session's** `accumulated_vector`, never on a state's `dimensional_vector` — confirmed via the same grep: `dimensional_vector` appears in exactly one file (`accumulation.py`, the `rank_states()` line above) across the entire live engine, outside of `engine/data/states.py` itself.
4. **`compute_liability_dispersion()` / `compute_cascade_risk()` (`engine/accumulation.py:355-438`).** Same distinction — entropy/dispersion math operates on the session's `accumulated_vector`, not any state's profile vector.
5. **Retired floor-multiplier system (`engine/output.py:34-36, 172-186`, `SIGNAL_FLOOR_MULTIPLIER_*`, `SIGNAL_FLOOR_CEILING`).** Explicitly marked "RETIRED v21" in-line. Confirmed dead: `grep` for `compute_floor`/`SIGNAL_FLOOR`/`floors[` across `engine/*.py` returns zero call sites outside `output.py`'s own retired block. Not part of the live `rank_states()` path (which is v21+, SCD-WCS).
6. **`DimensionalVector` dataclass and `_profile()`/`_reg()` (`engine/data/states.py`).** No `assert`, validation, or normalization step anywhere in the class or its construction helpers checking a field sum. `engine/data/validate.py`'s only vector-related check is whether a state is still at the uncalibrated `BASELINE_VALUE` placeholder (0.25 across all fields) — a "has this been calibrated yet" check, unrelated to budget totals.

**Existing production evidence corroborating this, not just code-reading:** 4 of the 58 states already ship with non-0.90 liability sums today (`the_unexamined_algorithm` 1.00, `the_unsolved_problem` 0.95, `distributed_culture_fragmentation` 1.00, `leadership_deafness` 0.80 — confirmed in the earlier Gemini-review-verification pass), and the engine has been scoring and ranking against all of them in every calibration run this entire program, without incident. `the_second_close`'s proposed 1.05 would be a fifth exception, not a first-of-its-kind risk.

**Conclusion: the budget expansion is safe to test in Phase 4 as far as engine-level assumptions go.** Whether 1.05 is the *right* magnitude for `the_second_close` specifically is an empirical question for Phase 4, not a structural risk to the pipeline.

---

## Phase 2 — Candidate Vectors (Batch 1)

Date: 2026-08-24. `invisible_performance_management`, `the_paper_tiger`, `built_to_fail` — the original 3-state constrained-search cluster, now re-authored under full re-authoring rather than within-budget redistribution. No salience derivation (Phase 3), no dry-run testing (Phase 4).

### `invisible_performance_management` (IPM)

**Current:** aptitude_liability 0.45 (dominant) / authority_liability 0.20 / alliance_liability 0.15 / attitude_liability 0.10. Sum 0.90.

**Candidate:** `authority_liability 0.60` (new primary, up from 0.20) / `aptitude_liability 0.10` (down from 0.45, to floor) / `alliance_liability 0.10` (down from 0.15, to floor) / `attitude_liability 0.10` (unchanged). All asset fields moved uniformly to 0.10 (from 0.15) for tier-shape consistency, see note below. Liability sum: 0.90 (unchanged — a full axis flip within the existing budget, not an expansion).

**Citation:** the starkest single divergence in this whole program (Phase 1). The text is entirely about evidentiary weight and documentation — *"carries no evidentiary weight when a decision needs defending... an absence of documentation"* — with no Alliance or Attitude content anywhere. Critically, it does not merely omit an Aptitude case, it **directly disclaims one**: *"A manager's read on an underperforming employee is accurate... a sound judgment"* is an unambiguous statement that the underlying capability/diagnostic read is not the deficiency. This is the only state in the audit where the text actively argues against its own vector's current dominant field, rather than simply not supporting it. Authority becomes the sole real axis; this is a single-axis state, matching the shape this taxonomy already uses for `built_to_fail` itself and 10 other states — the **HIGH tier** (0.60 primary / 0.10 floor elsewhere), chosen over a dual-axis shape because the text gives no grounding for any second dimension once Aptitude is correctly removed.

**Asset-floor note (flagged, not text-grounded):** moving IPM's four asset fields from 0.15 to 0.10 is a tier-shape consistency choice, not something the prose argues for directly — it matches the HIGH tier's established convention (uniform 0.10 across all non-primary fields, liability and asset alike) and avoids introducing a mixed-floor shape (0.10 liability / 0.15 asset) that has no precedent anywhere in the current taxonomy. Noted explicitly per this program's own discipline of citing what's text-grounded versus structurally chosen.

### `the_paper_tiger`

**Current:** identical to `built_to_fail` — aptitude_liability 0.60 (dominant) / authority, alliance, attitude all 0.10 (floor). Sum 0.90.

**Candidate:** `authority_liability 0.35` (new primary, up from 0.10) / `attitude_liability 0.25` (new secondary, up from 0.10) / `aptitude_liability 0.15` (down from 0.60, to floor) / `alliance_liability 0.15` (up from 0.10, floor-to-floor convention shift, see below). All asset fields moved to 0.15 (from 0.10). Liability sum: 0.90.

**Citation:** the largest shape divergence found in Phase 1, authored here fully independent of `built_to_fail` for the first time. Authority-primary: *"the written record no longer matches what everyone privately knows,"* *"act on documented cause,"* *"managing one employee on paper"* — three separate, direct evidentiary/documentation references, the same register this taxonomy already uses to mark Authority content (compare IPM's near-identical vocabulary above). Attitude-secondary: the say/do gap is itself the state's central mechanism, not incidental — *"it has been managing one employee on paper and a different one in practice"* is a direct performative discrepancy between stated/recorded behavior and actual behavior, the same shape this taxonomy already encodes as Attitude elsewhere (`the_diversity_ceiling`'s stated-vs-actual gap, already noted as precedent in Phase 1). No Aptitude content anywhere — the 0.60 aptitude figure was confirmed in Phase 1 to be wholesale inherited from `built_to_fail`, not independently authored; dropped to floor. This is a genuine dual-axis state, so it moves to the **LOW/CLUSTER tier** shape (0.35 primary / 0.25 secondary / 0.15 floor elsewhere) — the same convention already applied to `silosolation` in Batch 2 for the same reason (two real, text-grounded axes).

**Asset-floor note (flagged, not text-grounded):** as with IPM, the asset-field shift (0.10→0.15) is a tier-convention-consistency move matching the LOW/CLUSTER shape's established uniform floor, not an independently text-grounded change.

### `built_to_fail`

**Current:** aptitude_liability 0.60 (dominant, HIGH tier) / authority, alliance, attitude all 0.10 (floor). Sum 0.90. Already the sharpest single-axis magnitude in the entire taxonomy, tied with 10 other HIGH-tier states.

**CORRECTED, replacing the withdrawn 0.60→0.70 candidate above (Pete confirmed the flag: that direction was backwards — the goal is reducing false-rank-1, and the Session 17 retrospective's own language ties HIGH-tier concentration directly to the "too geometrically accessible" mechanism causing this state's dominance).**

**Candidate:** `aptitude_liability 0.60 → 0.50` (concentration decrease) / `authority_liability 0.10 → 0.15`, `alliance_liability 0.10 → 0.15`, `attitude_liability 0.10 → 0.15` (floor raised uniformly, no secondary axis introduced — all three non-primary fields move together, none singled out). All asset fields moved to 0.15 (from 0.10), matching the new floor for consistency, same convention-only caveat as IPM's and `the_paper_tiger`'s asset-floor notes above. Liability sum: 0.90 → **0.95**.

**Citation for keeping this single-axis:** Phase 1's finding stands, confirmed a fourth time here — *"The role's scope exceeds what any reasonable allocation of resources could support... told to make it work rather than given what making it work would require... the next person inherits the same impossible math"* carries no Authority, Alliance, or Attitude content anywhere. No secondary axis is introduced; this is a magnitude-only correction, exactly as scoped.

**Citation for the specific magnitude (0.50, not an arbitrary point between 0.45 and 0.60):** this is not a newly invented shape — it matches an **existing, already-shipped precedent in this exact taxonomy**: `the_unsolved_problem`'s own current vector is `aptitude_liability=0.50 / authority_liability=0.15 / alliance_liability=0.15 / attitude_liability=0.15` (liability sum 0.95). `the_unsolved_problem` is directly relevant precedent, not an arbitrary comparison — it is one of the two Aptitude-axis states (`paper_shield`, `the_unsolved_problem`) already re-clustered onto this axis this session specifically because they compete with `built_to_fail` for the same signal, and the tracker's own record already notes `built_to_fail` wins all 3 of `the_unsolved_problem`'s dedicated profiles outright even after its own fix. Landing `built_to_fail` at the same 0.50/0.15 shape doesn't just pick a round number — it puts `built_to_fail` on **equal concentration footing with the specific rival it currently dominates**, rather than sitting alone at the taxonomy's sharpest tier while competing against a rival authored at a visibly lower concentration. If 0.50/0.15 is a viable single-axis shape for `the_unsolved_problem` today (it passes calibration as shipped), it is a defensible, non-arbitrary target for `built_to_fail` too, not a step chosen by feel.

**Directional check against the flagged mechanism:** lowering the primary field and raising the floor both reduce vector sharpness (increase entropy/dispersion), the opposite of the HIGH-tier concentration effect the Session 17 retrospective and origin investigation identified as the likely driver of `built_to_fail`'s over-reach. This candidate is the untested alternative flagged in the withdrawn candidate's own note — Phase 4 should confirm it actually reduces false-rank-1 without unacceptable erosion of `built_to_fail`'s own 3 legitimate profiles (currently won at score 0.97-0.99, a wide enough margin that some erosion is expected to be tolerable, but not assumed).

---

## Not done yet (Batch 1)

No salience derived (Phase 3). No dry-run testing (Phase 4). Nothing written to `engine/data/states.py`. `the_uninitiated` untouched, out of scope. `built_to_fail`'s direction corrected (concentration decrease, 0.60→0.50) per Pete's confirmation, after the withdrawn 0.60→0.70 candidate was flagged as backwards — the correction's own text above names and explains what was withdrawn and why, so the flag-and-correct sequence stays on record even though the original candidate's numbers were replaced, not struck through.
