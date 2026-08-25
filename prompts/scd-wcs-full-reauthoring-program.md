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

---

## Phase 3 — Joint Salience Derivation

Date: 2026-08-24. All six candidate vectors from Batch 1 and Batch 2. No dry-run testing yet — that's Phase 4, run once against the full six-state set together. Salience derived fresh from each candidate's new vector shape, per instruction — not reused from current shipped salience, except where noted and explained below.

**Conventions used — both already established in this taxonomy, no new pattern invented:**
- **Standard flat (single-axis states):** dominant field 2.5/2.5 (liability/asset), all three others 0.4/0.4. Used taxonomy-wide for HIGH- and MEDIUM-tier single-axis states, including `built_to_fail`'s own current salience.
- **Dual-elevated (genuine two-axis states):** primary field 2.5/2.5, secondary field 2.0/2.0, remaining two fields 0.4/0.4. This is `silosolation`'s and `the_arbitrary_standard`'s own already-shipped convention (commits `cf2abeb`, `e9a2750`) — reused here as an existing precedent for every other candidate that turned out dual-axis, not invented fresh per state. The 2.0 secondary weight itself was empirically margin-searched only once before (`the_arbitrary_standard`'s own shipped fix) — reused here as a reasonable starting point, not re-validated for the other three dual-axis candidates. **Phase 4 needs to confirm 2.0 is sufficient in each new case, same as every magnitude choice in this program.**

Both fields of every liability/asset pair are kept at the identical weight (e.g. `aptitude_liability` and `aptitude_asset` always match) — this pairing is universal across every existing `SALIENCE_PROFILES` entry checked this session, and no Phase 2 candidate proposed differentiating a field's liability half from its asset half, so there's no basis to break the pattern here.

### `invisible_performance_management` (IPM)

**Candidate vector shape:** single-axis, Authority-primary (0.60/0.10 HIGH tier).

**Current shipped salience:** standard flat, Aptitude-primary (2.5/2.5 aptitude, 0.4/0.4 elsewhere) — matched the *old* vector's axis, now stale.

**New candidate:** standard flat, moved to the new primary — `authority_liability/asset 2.5/2.5`, `aptitude_liability/asset 0.4/0.4`, `alliance_liability/asset 0.4/0.4`, `attitude_liability/asset 0.4/0.4`.

**Citation:** the candidate vector is single-axis with no secondary grounding (Phase 1, Phase 2), so the standard flat template applies directly — salience simply follows the vector's own axis flip, weighting the field that's now actually dominant. No compensating elevation proposed beyond the standard template; the vector correction itself (0.20→0.60 on Authority) is expected to carry the differentiation, consistent with how every other single-axis state in the taxonomy is weighted.

**Watch item for Phase 4, not a flag against this derivation:** `the_founders_grip` is also HIGH-tier, Authority-primary (0.60/0.10), and was independently identified in the Session 17 retrospective as a secondary "sink" for Authority-heavy profiles. Standard flat salience doesn't address IPM/`the_founders_grip` overlap one way or the other — worth checking in Phase 4's drift comparison, not something Phase 3's salience choice should try to pre-solve without evidence.

### `the_paper_tiger`

**Candidate vector shape:** dual-axis, Authority-primary/Attitude-secondary (0.35/0.25 LOW/CLUSTER).

**Current shipped salience:** individually reshaped to compensate for the *old*, wrong (Aptitude-primary, inherited) vector — attitude 1.5/1.5 (highest), authority 1.0/1.0, aptitude 1.0/1.0, alliance 0.4/0.4 (lowest). This shape exists specifically because the vector was wrong; now that the vector itself is being corrected, this salience is obsolete on its own terms, not just superseded by convention.

**New candidate:** dual-elevated, matched to the new vector — `authority_liability/asset 2.5/2.5` (primary), `attitude_liability/asset 2.0/2.0` (secondary), `aptitude_liability/asset 0.4/0.4`, `alliance_liability/asset 0.4/0.4`.

**Citation:** matches the candidate vector's own primary/secondary split exactly (Authority > Attitude), using the dual-elevated convention already established for `silosolation`/`the_arbitrary_standard`. This is a genuinely new derivation, not a reuse — none of the four current shipped weights survive unchanged (aptitude drops from 1.0 to 0.4, authority rises from 1.0 to 2.5, alliance stays lowest but the relative gap changes, attitude drops from the current highest position 1.5 to 2.0's secondary position). The old salience's job (compensating for a bad vector) no longer exists once the vector itself is fixed.

### `built_to_fail`

**Candidate vector shape:** single-axis, Aptitude-primary, decreased concentration (0.50/0.15).

**Current shipped salience:** standard flat, Aptitude-primary (2.5/2.5 aptitude, 0.4/0.4 elsewhere) — unmodified since this state's original tier assignment.

**New candidate: unchanged — standard flat, same field.** `aptitude_liability/asset 2.5/2.5`, all three others `0.4/0.4`.

**Flagged explicitly, per instruction — this is a considered derivation that lands on the same value as today, not a lazy reuse:** the axis hasn't changed (still Aptitude, still single-axis, per Phase 1's third confirmation of zero secondary-axis grounding), so the standard flat template still applies mechanically. **The real question is whether salience should be elevated beyond the flat template to compensate for the vector's own reduced magnitude (0.60→0.50) — and the answer here is deliberately no.** Elevating salience to compensate would partially undo the vector correction through a different mechanism, working directly against the goal Pete confirmed last turn (reduce `built_to_fail`'s false-rank-1 count by reducing its geometric reach, not preserve its old reach through a different lever). Salience and vector magnitude both contribute to a state's effective dominance in the weighted cosine formula; using one to backfill what the other was deliberately reduced to achieve would be self-defeating. **Kept at the standard, unelevated flat template on purpose.**

### `silosolation`

**Candidate vector shape:** dual-axis, Alliance-primary/Authority-secondary (0.35/0.25 LOW/CLUSTER).

**Current shipped salience:** Alliance 2.5/2.5 (primary), Authority 2.0/2.0 (secondary), Aptitude/Attitude 0.4/0.4 — already dual-elevated, shipped in commit `cf2abeb`.

**New candidate: identical to current shipped salience.** `alliance_liability/asset 2.5/2.5`, `authority_liability/asset 2.0/2.0`, `aptitude_liability/asset 0.4/0.4`, `attitude_liability/asset 0.4/0.4`.

**Flagged explicitly, per instruction — this is not a reuse in violation of the "derive fresh" instruction, it's the expected outcome of the vector correction's own design.** Batch 2's `silosolation` candidate was authored specifically to make the vector "catch up" to a salience that was already correctly diagnosing Authority as real (see Batch 2 above) — the salience was never the broken half of this pair, the vector was. Re-deriving salience fresh from the new vector's shape via the dual-elevated convention necessarily produces the same weights that already exist, because the new vector's shape (Alliance-primary/Authority-secondary) is exactly what the existing salience was already built for. Confirming this independently (rather than assuming it) is the point of doing the derivation at all — it is a coincidence in *outcome*, not in *method*.

**One real change worth naming:** this salience's role shifts. Previously documented as "honest partial fix, tie-break-only" (`cf2abeb`'s own comment) because it was compensating for a vector `silosolation` shared with two other states. Now that the vector itself is genuinely distinct (Batch 2), salience is doing its normal job — weighting an already-differentiated shape — not emergency tie-breaking. The numbers are unchanged; what they're accomplishing is not.

### `the_arbitrary_standard`

**Candidate vector shape:** dual-axis, Authority-primary/Alliance-secondary (0.35/0.25 LOW/CLUSTER) — the mirror of `silosolation`'s shape, axes swapped.

**Current shipped salience:** Authority 2.0/2.0 (secondary-weighted today), Alliance 2.5/2.5 (primary-weighted today) — shipped in commit `e9a2750`, matched to the *old* shared Alliance-primary vector.

**New candidate:** the weights flip to match the new vector's own axis flip — `authority_liability/asset 2.5/2.5` (now primary), `alliance_liability/asset 2.0/2.0` (now secondary), `aptitude_liability/asset 0.4/0.4`, `attitude_liability/asset 0.4/0.4`.

**Citation:** a genuine, substantive change, not a reuse — the field carrying 2.5 and the field carrying 2.0 swap outright, matching the origin investigation's own finding (this program's prior work) that `the_arbitrary_standard`'s text is more purely Authority-centered than `silosolation`'s, and the Batch 2 vector candidate's own axis flip (Authority now primary in the vector, not just a same-cluster secondary). Salience now matches vector shape for the first time since this state's original tier assignment — every prior version of this state's salience was compensating for a vector it didn't actually match (first the shared flat template, then the partial Authority-secondary fix against an unchanged Alliance-primary vector).

### `the_second_close`

**Candidate vector shape:** dual-axis, Alliance-primary (increased to 0.55, budget-expanded) / Aptitude-secondary (0.20, new).

**Current shipped salience:** standard flat, Alliance-primary (2.5/2.5 alliance, 0.4/0.4 elsewhere) — never individually touched before this program.

**New candidate:** dual-elevated — `alliance_liability/asset 2.5/2.5` (unchanged, still primary), `aptitude_liability/asset 0.4 → 2.0/2.0` (new secondary), `authority_liability/asset 0.4/0.4` (unchanged), `attitude_liability/asset 0.4/0.4` (unchanged).

**Citation:** matches the vector's own new shape — Alliance stays dominant (unchanged weight, since the vector's own primary field increased but the axis itself didn't move), Aptitude gets the same 2.0 secondary elevation used for the other three dual-axis candidates, grounded in Phase 1's formalized misdiagnosis-signal finding (sentence 3, "wasn't the actual cause") now that the vector itself carries a real, non-floor Aptitude value to weight. No flag here — unlike `built_to_fail`, this state's vector change was a deliberate *increase* in both primary magnitude and secondary presence, both aimed at the same goal (closing the gap against `built_to_fail`), so elevating the matching salience field works with the vector correction's intent rather than against it.

---

## Not done yet (Phase 3)

No dry-run testing (Phase 4) for any of the six states — none of these candidate salience profiles have been run against the live pipeline, individually or as a set. Nothing written to `engine/data/salience.py` or `engine/data/states.py`. `the_uninitiated` untouched, out of scope. Two derivations flagged above as landing on unchanged values (`built_to_fail`, `silosolation`) — both explained as considered outcomes, not unreflective reuse; Phase 4 should treat all six candidates with equal scrutiny regardless of which changed on paper.

---

## Phase 4 — Dry-Run Testing (all six candidates, simultaneous)

Date: 2026-08-24. Full 175-profile sweep, all six candidate vectors + salience applied together in-memory (not sequentially), against a fresh baseline sweep of the current shipped values. Script and methodology: purpose-built harness reusing `tools/calibration_runner.py`'s own `_run_profile_core()`/`_build_suite_v23()`, cross-validated against the independently-authored `tools/_scdwcs_full_hierarchy_measurement.py` for the baseline numbers (see methodology note below). Nothing written to `engine/data/states.py` or `engine/data/salience.py` — in-memory mutation only, restored before exit.

**A real bug was caught and fixed before any result below was trusted, per this program's own standing discipline.** The first pass of this dry run counted every profile's rank-1 winner as a "false-rank-1," including cases where a state correctly won its own dedicated profile — inflating `built_to_fail`'s baseline to 65/175 instead of the correct 62/175 (its own 3 legitimate profile wins, double-counted as false positives). Caught by cross-checking against the independently-authored `tools/_scdwcs_full_hierarchy_measurement.py`, which reproduced the previously-established 62/43/5 baseline exactly. Fixed (exclude `rank1 == target_state` from the false-rank-1 tally) and the full sweep re-run. All numbers below are post-fix.

### 1. False-rank-1 delta, in-scope states

| State | Before | After | Delta | Own profiles won |
|---|---|---|---|---|
| `invisible_performance_management` | 43 | **0** | **−43** | 0/3 → 0/3 |
| `the_paper_tiger` | 0 | 2 | **+2** | 0/4 → 0/4 |
| `built_to_fail` | 62 | **100** | **+38** | 3/3 → 3/3 |
| `silosolation` | 0 | 1 | +1 | 0/3 → 0/3 |
| `the_arbitrary_standard` | 0 | 0 | +0 | 0/3 → 0/3 |
| `the_second_close` | 5 | 1 | **−4** | 0/3 → 0/3 |

**2 of 6 improved (IPM sharply, `the_second_close` moderately), 1 flat (`the_arbitrary_standard`), 3 worsened (`the_paper_tiger`, `silosolation` slightly; `built_to_fail` severely — a 61% relative increase, the single largest false-rank-1 count recorded anywhere in this program's history for any state).**

### 2. Drift on other states — named and explained, not aggregated

8 of the ~52 out-of-scope states moved, all by ±1 or ±2:

| State | Before → After | Plausible mechanism |
|---|---|---|
| `distributed_culture_fragmentation` | 0 → 1 | Alliance-axis state; `the_second_close`/`silosolation`/`the_arbitrary_standard`'s Alliance-field redistribution plausibly shifts adjacent Alliance signal. |
| `planning_authority_gap` | 5 → 6 | Authority-axis state; three of the six candidates (IPM, `the_paper_tiger`, `the_arbitrary_standard`) moved onto or strengthened Authority this batch. |
| `the_fracture` | 0 → 2 | Alliance-axis, already documented as adjacent to the rank-6 cluster; `the_second_close`'s sharper Alliance concentration (0.45→0.55) plausibly redirects some Alliance-adjacent signal here. |
| `the_overloaded_manager` | 9 → 8 | Aptitude/Authority dual-axis; modest improvement plausibly from `built_to_fail`'s reduced Aptitude concentration freeing one profile. |
| `the_undefined_role` | 3 → 4 | Aptitude-primary; plausibly affected by the same Aptitude-axis reshuffling as `built_to_fail`'s own expansion (see mechanism diagnostic below). |
| `the_unexamined_algorithm` | 5 → 7 | Authority-primary, one of the four known non-0.90-sum states, already flagged this session for cross-cluster asymmetry; plausibly affected by the Authority-axis moves. |
| `the_unformed_leader` | 8 → 7 | Aptitude/Attitude dual-axis; modest improvement, same direction as `the_overloaded_manager`. |
| `the_uninitiated` | 19 → 18 | Rank-2 Authority cluster; modest improvement, plausibly from Authority-axis redistribution. `the_uninitiated` itself untouched, per standing instruction. |

All eight moves are small (≤2 profiles) and directionally explicable as ripple from the batch's own axis reshuffling (three states added to or strengthened on Authority; Alliance redistributed within the rank-6 cluster). **No unexplained or large-magnitude drift found** — the drift itself is not what fires the fallback trigger; the in-scope regressions are (Section 1).

### 3. IPM / `the_founders_grip` watch item — resolved clean

`the_founders_grip`: 0 → 0. **No new collision.** IPM's axis flip to Authority-primary did not create any measurable overlap with `the_founders_grip`'s own HIGH-tier Authority vector in this sweep. The watch item flagged in Phase 3 does not materialize as a problem — noted for completeness, not a factor in the fallback trigger below.

### 4. Full calibration suite

**Before: 171/175. After: 168/175 — a 3-point regression.** Consistent with, and smaller in magnitude than, the false-rank-1 findings above (the suite's lenient cluster/prominence pass criteria absorb most of `built_to_fail`'s expansion, same documented gap this program has flagged every time it's measured both metrics together — the suite undercounts real rank-1 degradation, but here it still moved, unlike the 3-state search's candidates which held the suite flat at 171/175 while false-rank-1 still changed underneath).

### Mechanism diagnostic — why `built_to_fail` grew so much, run to ground rather than left as a number

**Not a narrow, single-axis effect.** `built_to_fail`'s 38 new false-rank-1 wins are NOT concentrated on former Aptitude-axis rivals (IPM, `the_paper_tiger` no longer compete there at all). The victim list spans every dimension: `the_wrong_reward` and `culture_drift` (Attitude, 3 each), `pay_exposure`, `the_unexamined_algorithm`, `compression_crisis` (Authority), `distributed_culture_fragmentation` (Alliance), `the_arbitrary_standard` (this batch's own Authority-primary candidate, now also a `built_to_fail` victim) — 15 different states lost at least one profile to `built_to_fail`, 41 profiles total.

**Root cause, traced empirically rather than assumed: raising the floor, not lowering the primary, is what broadened `built_to_fail`'s footprint.** The candidate's intent was to *reduce* dominance by softening concentration (0.60→0.50 primary, 0.10→0.15 floor). But weighted cosine similarity's numerator is a dot product summed across **all eight fields** — raising the floor on Authority/Alliance/Attitude from 0.10 to 0.15 increases `built_to_fail`'s raw alignment with *any* profile carrying signal on those axes, not just Aptitude ones, while the denominator (the vector's own magnitude) grows more slowly (square-root scaling). The primary-field decrease reduced `built_to_fail`'s edge on genuinely Aptitude-heavy profiles as intended, but the floor increase — intended only as "don't introduce a fake secondary axis, just soften the shape" — turned out to be the dominant effect, and it works in the *opposite* direction from what the Phase 2 citation predicted. **This reverses this program's own working theory from Phase 2:** the risk wasn't sharper concentration on the primary field, it was raising the uniform floor. A future candidate, if this cluster is revisited, should treat these as two independently-tunable levers, not a single "soften the state" move — and the flag process that caught the original 0.60→0.70 error should have also caught this, since it's the same class of insufficiently-tested magnitude assumption.

**Two new candidate-vs-candidate collisions, not visible until all six were tested together — the entire reason this phase specified testing the set, not sequentially.** `the_paper_tiger` (candidate: Authority 0.35/Attitude 0.25) and `the_arbitrary_standard` (candidate: Authority 0.35/Alliance 0.25) now share an identical Authority-primary magnitude, differing only in secondary axis — geometrically closer to each other than either was to anything else pre-batch. `the_paper_tiger`'s 2 new false wins are both against `hr_capture` (`AUT-HC-01`, `AUT-HC-02`), not `the_arbitrary_standard` directly, but the shared-magnitude proximity is a real, newly-introduced structural risk worth tracking if either candidate is revised. `silosolation` (Alliance 0.35/Authority 0.25) and `the_arbitrary_standard` (Authority 0.35/Alliance 0.25) are exact axis-mirrors of each other — `silosolation`'s 1 new false win is against `the_burned_credibility` (`ATT-BC-03`), not `the_arbitrary_standard` either, but the mirrored shape is the same category of newly-introduced proximity risk.

**A residual finding independent of the fallback trigger, worth carrying forward regardless of what happens to this candidate set: neither IPM nor `the_paper_tiger` wins any of its own dedicated profiles even after the axis correction (0/3 and 0/4, both unchanged from baseline).** The re-authoring fixed the *textual* misalignment (Phase 1's whole premise) and dramatically cut IPM's false-rank-1 footprint (43→0), but did not yet achieve either state's most basic practical goal of winning its own profiles outright. Something beyond axis correction — likely magnitude, now that the axis itself is right — is still needed for these two specifically.

---

## FALLBACK TRIGGER FIRED — stopping per standing safeguard, nothing shipped

Per this program's own condition (same safeguard the 3-state search used): **the trigger fires when an in-scope state's count fails to improve.** Three of six do here — `the_paper_tiger` (+2), `silosolation` (+1), and `built_to_fail` (+38, severe). `built_to_fail`'s regression alone — the largest false-rank-1 count measured anywhere in this program's history — is sufficient on its own to trigger a stop.

**Nothing written to `engine/data/states.py` or `engine/data/salience.py`, as instructed regardless of outcome.** No candidate from this six-state set is safe to ship as authored. The clearest, most actionable finding is `built_to_fail`'s floor-increase mechanism (above) — this is a concrete, falsifiable lead for a revised candidate, not just a negative result: the fix likely needs to separate "lower the primary" from "raise the floor" and test each lever's contribution independently, rather than moving both simultaneously as Batch 1's candidate did. IPM's and `the_second_close`'s improvements are real and worth preserving in any revision. `the_arbitrary_standard`'s flat result and the two new candidate-vs-candidate proximity risks (`the_paper_tiger`/`the_arbitrary_standard`, `silosolation`/`the_arbitrary_standard`) are also worth weighing before any re-attempt. `the_uninitiated` untouched throughout. Awaiting Pete's direction — revise `built_to_fail`'s candidate specifically (isolating the floor-vs-primary levers) and re-test, revise more broadly, or pause this cluster.

---

## Phase 4b — Lever Isolation, `built_to_fail` Only

Date: 2026-08-24. Direction: the other five Batch 1/2 candidates don't need changes from Phase 4's result — isolate `built_to_fail`'s two conflated levers instead of revising the whole batch. Each candidate tested **alone**, with all other 57 states (including the other five candidates) left at their current shipped values, not their Batch 1/2 candidates — a clean single-state isolation, same methodology as the original 3-state search. Baseline reconfirmed at 62/175, matching every prior measurement this session. Nothing written to disk.

**Candidate A — floor-only:** `authority_liability`/`alliance_liability`/`attitude_liability` 0.10 → 0.15, `aptitude_liability` unchanged at 0.60. All asset fields unchanged at 0.10.

**Candidate B — primary-only:** `aptitude_liability` 0.60 → 0.50, all three floor liability fields unchanged at 0.10. All asset fields unchanged at 0.10.

### Results

| | `built_to_fail` false-rank-1 | Delta | Own profiles won | Suite |
|---|---|---|---|---|
| Baseline | 62 | — | 3/3 | 171/175 |
| **Candidate A (floor-only)** | **84** | **+22** | 3/3 | 171/175 |
| **Candidate B (primary-only)** | **72** | **+10** | 3/3 | 171/175 |
| (for reference) Phase 4's combined candidate | 100 | +38 | 3/3 | 168/175 |

**Neither lever improves `built_to_fail`'s own count in isolation — both make it worse.** Candidate A (floor-only) is more than twice as harmful as Candidate B (primary-only): +22 vs +10. This confirms the Phase 4 mechanism finding — raising the floor is the more damaging move — but it also shows something Phase 4 alone couldn't: **lowering the primary alone doesn't help either, it still hurts, just less.** The original Phase 2 theory (concentration decrease reduces false-rank-1) is wrong in both isolated directions, not just wrong because of how the two levers interacted when combined.

**Confirmed non-additive, worse than either lever's sum:** 22 + 10 = 32, but the combined candidate measured 38 in Phase 4 — a genuine superadditive interaction, not just "the bigger of the two problems." Isolating the levers didn't just identify which one is worse, it revealed that combining them costs more than either contributes on its own.

**Side effect worth naming, not part of the isolation question itself:** in both candidates, IPM's own false-rank-1 count dropped as a side effect of `built_to_fail`'s vector change alone — 43→23 (−20) under Candidate A, 43→32 (−11) under Candidate B — even though IPM's own vector was untouched in this test. `built_to_fail` becoming more competitive on Authority/Alliance/Attitude (Candidate A) or less dominant on Aptitude (Candidate B) both appear to pull some of IPM's own false wins toward `built_to_fail` instead, rather than genuinely resolving them. Net across the pair: Candidate A is +22/−20 (net +2), Candidate B is +10/−11 (net −1) — closer to redistribution between the two states than a real fix to either, the same whack-a-mole shape this program's very first constrained search already found for this exact pair.

**Known-rival and full drift:** clean under both candidates. Candidate A: one small drift (`the_unformed_leader` 8→7, −1) plus `the_overloaded_manager` (9→8, −1) outside the named rival list; nothing else moved. Candidate B: one small drift (`the_unexamined_algorithm` 5→6, +1); nothing else moved. No large or unexplained drift under either isolated candidate — the severe, broad-spectrum drift Phase 4 found (41 profiles across 15 victim states) was specific to the *combined* candidate, not present in either lever alone.

### Reading this plainly

Both candidates fail the same standard Phase 4's did — neither improves `built_to_fail`'s own false-rank-1 count, so neither is shippable as tested. But this isn't a wash: it rules out the entire "soften `built_to_fail`'s concentration, either by raising the floor or lowering the primary" family of fixes at these magnitudes, in isolation or combined, and it reframes the IPM interaction as redistribution rather than resolution. Consistent with the program's very first finding (the 3-state search's own fallback trigger): `built_to_fail`'s dominance keeps resisting every magnitude-only lever tested so far, isolated or combined, textually grounded or not. **Not shipped. No new candidate proposed here** — this was isolation and measurement only, per the dispatch.

### Flagged for the record, no action taken

- **IPM and `the_paper_tiger`'s own-profile win rate is still 0/3 and 0/4 even after their axis corrections**, reconfirmed unchanged in this phase's baseline reruns. Logged as a known open gap for a later phase — not folded into this isolation test, per instruction.
- **`the_paper_tiger` and `the_arbitrary_standard` now share an identical Authority-primary magnitude (0.35) post-candidate** — a new proximity risk first surfaced in Phase 4, logged here as a standing watch item, same treatment as the IPM/`the_founders_grip` flag from Phase 3/4. No testing performed on this in Phase 4b; carried forward only.
