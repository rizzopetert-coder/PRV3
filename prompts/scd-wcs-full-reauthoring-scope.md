# SCD-WCS Full Taxonomy-Wide Re-Authoring — Scoping Document

Date: 2026-08-24. Scoping only. No vector values proposed, no candidates searched, no code touched, no Gemini submission drafted or sent. `the_uninitiated` completely out of scope here, per explicit instruction — separate track, separate future work.

---

## 1. What "full re-authoring" actually means, concretely — three things now on the table that weren't before

The just-completed constrained search held two things fixed by design: each state's own total liability sum (0.90) and its `SALIENCE_PROFILES` template. Its failure — no candidate brought `built_to_fail` and IPM's counts down together — specifically implicates both of those constraints, plus a third dimension never touched at all:

**(a) The total liability budget itself.** The constrained search only ever moved mass *between* the four liability fields, always summing back to 0.90. Full re-authoring can change the total — e.g., if `built_to_fail`'s real dominance genuinely warrants a sharper, more concentrated vector than 0.90 allows, or if a state's asset fields (currently pinned to tier standards, 0.10/0.15, confirmed taxonomy-wide except one known exception) should also move. The failed search couldn't test this because it wasn't allowed to.

**(b) The dimensional shape / axis choice.** Already tested within-budget for liability fields; full re-authoring extends this to asset fields too, which the constrained search never touched at all.

**(c) The `SALIENCE_PROFILES` template each state draws from.** Held completely fixed throughout the constrained search (confirmed: every candidate tested only the four `DimensionalVector` liability fields, salience untouched in every run). This is the most significant new lever. `the_paper_tiger` — sharing `built_to_fail`'s exact vector — has *already* had its own salience individually adjusted away from the standard flat template (see Section 2) to partially compensate for a vector that doesn't match its own real text. That's real, existing precedent inside this taxonomy for salience-level re-authoring as a genuine tool, not just liability-value redistribution.

**Why the failure specifically implies all three are now in scope, not just "worth trying anyway":** the search found that improving IPM's own metric reliably drove `built_to_fail`'s worse, in every tested magnitude, with zero exception. That's the signature of a genuine zero-sum competition *within a fixed budget* — moving liability mass around only changes who wins a shared pool of "signal," it can't create new distinguishing signal. Changing the budget, the asset shape, or the salience weighting are the only levers left that could plausibly break that zero-sum structure rather than just relocating it again.

---

## 2. Real blast radius — checked directly, not assumed

Pulled every state's real `dimensional_vector` and compared for exact matches, live:

- **`built_to_fail`** shares its exact vector with **`the_paper_tiger`** — one other state, not zero.
- **`invisible_performance_management`** — confirmed unique. No other state shares its vector. Self-contained; re-authoring IPM's vector has no direct blast radius via shared-vector siblings.
- **`the_second_close`** shares its exact vector with **two** other states: **`silosolation`** and **`the_arbitrary_standard`**.

**This is not stale sharing left over from before the taxonomy's own salience-based fixes — these siblings are still genuinely vector-identical today, only differentiated by salience:**

| State | Real prose theme | Current salience (vs. standard flat 2.5/0.4 template) |
|---|---|---|
| `built_to_fail` | Pure aptitude/resource-scope | Standard flat aptitude-primary (2.5/0.4/0.4/0.4) — unmodified |
| `the_paper_tiger` | Documentation gap between verbal management and written record; surfaces "in front of the people with the least patience" | **Individually re-shaped**: attitude_liability=1.5 (now dominant), aptitude=1.0, authority=1.0, alliance=0.4 (lowest) — no longer the standard template at all |
| `the_second_close` | Alliance/trust, with a real misdiagnosis-of-root-cause undertone (see Section 3) | Standard flat alliance-primary (2.5/0.4/0.4/0.4) — unmodified |
| `silosolation` | Teams not sharing information across structural boundaries | Authority=2.0 **and** alliance=2.5 (dual-elevated) |
| `the_arbitrary_standard` | Inconsistent rule application, unnoticed by leadership | Authority=2.0 **and** alliance=2.5 (dual-elevated) — **identical to `silosolation`'s salience**, confirming these two are still genuinely tied with each other, even though both are now differentiated from `the_second_close` |

**Direct implication for re-authoring:** touching `built_to_fail`'s vector cannot be scoped in isolation — `the_paper_tiger`'s real text already argues for a genuinely different shape (attitude-dominant, not aptitude-dominant) and has only ever been partially compensated via salience, not vector correction. Any `built_to_fail` re-authoring pass should treat `the_paper_tiger` as needing its own real vector correction in the same pass, not something to "keep in sync" with whatever `built_to_fail` becomes. Same logic for `the_second_close`: `silosolation` and `the_arbitrary_standard` are a **separate, still-unresolved pair** (tied with each other, not with `the_second_close`) whose own real prose (structural information-silos vs. inconsistent-enforcement) doesn't obviously argue for sharing a vector with each other either — a second, distinct re-authoring question sitting adjacent to this one, not folded into the 3-state scope but real work the same investigation will eventually need to address.

---

## 3. What the real text actually supports — independent of what makes the numbers work

**`built_to_fail`**: *"The role's scope exceeds what any reasonable allocation of resources could support, and each person who holds it is told to make it work rather than given what making it work would require. The organization treats each departure as an individual hiring failure rather than a structural one. The next person inherits the same impossible math."* Purely single-dimension aptitude/capability-scope content, confirmed again — no secondary-axis material anywhere in this text. Full re-authoring doesn't change this fact; there's still nothing to redistribute *into*. If this state's vector needs to change at all, the textual case supports adjusting its own magnitude/concentration (how sharp 0.60 aptitude actually needs to be, or what its total budget should be), not adding a second dimension that isn't there.

**`invisible_performance_management`**: *"...carries no evidentiary weight when a decision needs defending... an absence of documentation..."* Real authority-adjacent content already present and already reflected in the current vector's secondary field. Unchanged from the constrained search's finding — the text was never the limiting factor for IPM, the shared-budget competition with `built_to_fail` was.

**`the_second_close`, examined in full depth here for the first time**: *"A relationship or agreement was renegotiated once already, and the same underlying issue that forced the first renegotiation is resurfacing. Whatever the first fix addressed, it wasn't the actual cause. The people involved are less willing to extend trust a second time."* Breaking this down sentence by sentence rather than taking the whole paragraph as one alliance-flavored block: sentence 1 and 4 are genuinely alliance (a relationship, trust eroding). **Sentences 2 and 3 are a real, substantive aptitude signal — a misdiagnosis, a failure to correctly identify the actual root cause** ("wasn't the actual cause" is a direct claim about a diagnostic failure, not a relationship failure). This is a stronger, more central aptitude signal than the constrained search's candidates treated it as — half the state's own prose is about diagnostic accuracy, not just a smaller "undertone." **This doesn't change the search's own finding that a modest liability redistribution didn't help** (Section 4 below explains why), but it does mean the real textual case for a genuine dual-axis (alliance + aptitude) shape for this state is stronger than previously credited, worth carrying into any future re-authoring pass as real grounding, not just a minor secondary note.

---

## 4. `the_second_close`'s specific situation — is the gap structural, or just budget-limited?

The constrained search found `the_second_close`'s own-profile score (0.703) sits 0.157 below `built_to_fail`'s (0.860) on the profiles it loses, and that even a fairly aggressive within-budget redistribution barely moved that number.

**Reasoned through structurally, not just re-tested with bigger within-budget numbers:** SCD-WCS is a weighted cosine similarity. `built_to_fail`'s vector is *sharp* — one field at 0.60, everything else at the floor — which is exactly the shape that scores highest against any session showing even a modest aptitude signal, because cosine similarity rewards directional concentration. `the_second_close`'s vector is comparatively *diffuse* even at its own dominant field (0.45, well below `built_to_fail`'s 0.60), which structurally caps how strongly it can ever compete on any profile where `built_to_fail`'s dominant axis has any real presence at all.

**This is the key finding for this item: the constrained search could never have tested the actual lever that might matter here, because it held the total budget fixed at 0.90 for both states.** If `the_second_close`'s real signal concentration is genuinely lower than `built_to_fail`'s by design (a legitimately more "diffuse" condition, per its own alliance-plus-aptitude dual-signal text), then no amount of redistribution *within* a fixed 0.90 can close a gap that's fundamentally about *how sharp the state's own peak is*, not *which axis carries it*. Full re-authoring — specifically the freedom to change the total budget, not just where it's allocated — is the one lever that could plausibly test this directly (e.g., a genuinely stronger alliance concentration, closer to `built_to_fail`'s own 0.60-class magnitude, grounded in the text's real relationship-and-trust framing).

**Stated honestly, not optimistically: this is a real, structurally distinct hypothesis the current evidence doesn't rule out — it is not a confirmed fix.** The failed search ruled out "redistribute within 0.90." It did not and could not test "raise the total." Worth testing directly in the next phase; not assumed to work here.

---

## 5. What Gemini's review should actually be asked — draft questions, not sent

Different in kind from the constrained search's 3-question structure (which asked "is this claim accurate," now already answered). This phase needs Gemini's judgment on scope and risk, not fact-verification:

1. **Budget-flexibility question, `the_second_close` specifically:** given the structural-concentration hypothesis in Section 4, is raising `the_second_close`'s total liability budget (not redistributing within it) a sound approach, and what real ceiling should that budget respect — is there a principled reason total liability shouldn't exceed some bound, or was 0.90 itself just an emergent pattern (54/58 states) rather than a real design constraint worth preserving even during re-authoring?
2. **`the_paper_tiger` and the silosolation/`the_arbitrary_standard` pair — does the re-authoring scope need to expand to include them now, given Section 2's finding that they're still genuinely vector-tied to the 3 target states (or to each other) and their own real text doesn't match the shared vector either?** Is a 3-state re-authoring pass that ignores its own direct vector-sharing siblings coherent, or does this need to become (at minimum) a 5-state pass: `built_to_fail`/`the_paper_tiger` together, `the_second_close`/`silosolation`/`the_arbitrary_standard` together?
3. **Salience-template re-authoring specifically for `built_to_fail`:** given Section 3 reconfirms no secondary-axis textual content exists for this state at all, is there any principled, text-grounded way to reduce its dominance that doesn't require inventing a secondary dimension the text doesn't support — e.g., adjusting its own salience *magnitude* (is 2.5 the right peak weight, independent of which field it's on) rather than its shape?
4. **Sequencing and safety:** given this project would touch shared-vector states beyond the original 3, what's the right order to re-author in — one cluster fully (vector + salience + ripple-audit) before starting the next, or a single combined pass — and does the existing 175-profile calibration suite, already confirmed to under-report real rank-1 degradation (Section on the 171/175 gap in the prior search's report), need a supplementary check built specifically for this phase before any candidate is trusted?

---

## 6. Realistic size/session estimate — honest, not optimistic

**This is not a single future session. It looks like its own multi-phase program, comparable in shape to the original 8-phase SCD-WCS remediation program, not a simple continuation of the just-completed 3-state search.**

Reasons, concretely:
- The real scope just grew from 3 states to at least 5 (`built_to_fail`+`the_paper_tiger`, `the_second_close`+`silosolation`+`the_arbitrary_standard`), confirmed via direct vector-sharing checks in Section 2 — not a future risk, an already-confirmed fact.
- Three genuinely different levers are now in play (budget, asset-field shape, salience template) where the prior program used one (salience-only) or two (liability redistribution). Each needs its own textual-grounding pass, its own candidate search, and its own full ripple-audit against all 58 states × 175 profiles — the same rigor this session's 3-state search already required, now multiplied across more states and more degrees of freedom per state.
- `built_to_fail` itself remains the hardest open question in the whole cluster: Section 3 reconfirms there's still no textual grounding for a second dimension, meaning its own fix (if one exists) likely requires either a genuinely novel approach (magnitude-only adjustment, or accepting some states simply can't be perfectly separated) or a scope decision from Pete about what "acceptable" looks like for this state specifically — not something a mechanical search is likely to resolve on its own, however thorough.
- The 171/175 calibration suite's own confirmed blind spot (doesn't reflect real rank-1/false-rank-1 behavior) means this phase can't lean on the existing pass/fail gate the way earlier, smaller fixes could — every candidate needs the same full false-rank-1 sweep this session's search already established as necessary, which is real, non-trivial compute and analysis time per candidate, now across a larger state set.

**A reasonable expectation: a dedicated multi-session program, gated by Gemini at its outset (per the questions in Section 5) and likely again at least once mid-program once real candidate results are in — not a single follow-up session, and not safely compressible into one without real risk of exactly the kind of unrigorous, single-pass mistake this whole investigation exists to avoid.**

---

## Not done here, per explicit instruction

No vector values proposed. No candidates searched. No code touched. No Gemini submission drafted or sent — the questions in Section 5 are prepared for a future submission, not dispatched. `the_uninitiated` untouched and out of scope throughout.
