# Session Handoff — MOB v4.222

Direct extract/reformatting of `tools/_mob.txt` Section 16's closeout entry for this session (SCD-WCS Track 2 diagnostic deep-dive — `invisible_performance_management`/`built_to_fail`/`the_uninitiated`/`the_second_close`), plus the companion Section 13a (Decision Register) and Section 13b (Session Priority Queue) updates. Section 16 is authoritative — this file is a portable quick-reference copy, not an independent record.

**Zero code, vector, or salience changes this entire pass** — diagnostic and documentation only. Confirmed via `git status` on `engine/data/states.py`/`engine/data/salience.py` at multiple checkpoints throughout.

## Diagnostic work this session (nothing shipped to code — dry-run/scratch only)

- **Stale-baseline correction, the session's first real finding**: the Phase 8 census's "44/41/17/5" false-rank-1 figures for the 4 pre-existing dominant states were measured in a transient window — after `paper_shield`/`the_unsolved_problem` re-clustered onto Aptitude, before their own Phase 8 mitigation reverted that competition — and never re-verified after.
- **Real corrected baseline**, cross-validated two independent ways each: `invisible_performance_management` **59/175** (unchanged from pre-investigation), `built_to_fail` **52/175** (drifted UP, not down — inherited the other 3 re-clustered states' own-profile losses once their footprints reverted), `the_uninitiated` **17/175** and `the_second_close` **5/175** (both confirmed genuinely unchanged, outside the Aptitude-axis window that caused the drift). All four now carry explicit "supersedes" annotations in the tracker.
- **`invisible_performance_management` fully diagnosed as a genuine dual problem**: ~61% of its 59 false-rank-1 profiles trace to vector concentration/magnitude, ~39% to real field-level collision (4 coincidental, non-textual `authority_liability` matches CLOSED as not real collisions; one genuine double-field collision with `the_unexamined_algorithm`, textually grounded on both sides).
- **A separate, distinct problem confirmed**: `invisible_performance_management` never wins any of its own 3 dedicated profiles at any concentration tested (sandbox 1:1–20:1, this pass's pilot 3.5:1–50:1) — always loses to `built_to_fail` specifically. Opened as its own dedicated investigation.
- **Concentration-sharpening pilot run to completion, RULED OUT at pilot scale**: reaches 0/175 at high skew ratios, but produces 130–183 top-3 rank ripples across the rest of the taxonomy (own score shifts on 118–128 of 175 profiles) — hard measured evidence, not just prior theory, for the standing taxonomy-wide re-authoring need.
- **`the_unexamined_algorithm` differentiation (Candidate C)** — `invisible_performance_management.authority_liability` 0.25→0.20 + `the_unexamined_algorithm.aptitude_liability` 0.35→0.30 — a real, well-grounded, textually-honest small fix. Substantially smaller ripple footprint than sharpening (36 vs. 130–183), zero score contamination, zero new regression. **READY BUT HELD**, not committed, pending sequencing.
- **Combined concentration+differentiation candidates tested, confirmed non-additive/counterproductive** (61/175 and 33/175, both worse than either lever alone) — not pursued further.

## Key findings

- **Mechanism isolated, not just observed**: `built_to_fail`'s leakage into Candidate C's ripples is `invisible_performance_management`-driven regardless of method (37% present in an isolated single-field test). `the_uninitiated`'s leakage is `the_unexamined_algorithm`-driven and is **partially suppressed, not compounded**, by the combined candidate (38% isolated vs. 11% combined) — direct profile-level cross-check found `invisible_performance_management`'s own change reverses `the_unexamined_algorithm`'s effect on 3 specific `AUT-PL` profiles.
- **Incidental catch**: `decision_paralysis`/`the_lost_map`'s own-profile tie-break winner has silently flipped to `the_uninitiated` since a prior "closed" Program Phase 5 finding. Root cause not chased down. Doesn't move any counted pass/fail number — invisible to the regression suite by construction.
- **Standing discipline confirmed again**: this pass's own opening stale-baseline finding is itself an instance of the exact pattern this project keeps needing — verify against freshly-measured real output, never a prior session's recorded number, even a recent, previously-confirmed-correct one. Every headline number this pass was cross-validated two independent ways before being trusted.

## Open / carried forward

- **Sequencing recommendation on record, not decided**: resolve `built_to_fail`'s own open-profile-loss investigation first, then re-run Candidate C's ripple check against whatever baseline that leaves — a `built_to_fail` fix would likely reshape the ripple picture. Pete's call.
- **`built_to_fail` own-profile-loss investigation** — why it specifically (not some other state) wins `invisible_performance_management`'s own best-case test profiles, independent of the broad theft problem. Not a magnitude question (confirmed flat at every tested concentration). Natural next step if Track 2 work resumes before the full re-authoring project.
- **The 4 pre-existing dominant states, full taxonomy-wide re-authoring project** — still not scoped, still the larger standing question underneath all of this session's diagnostic work. Not started.
- **`decision_paralysis`/`the_lost_map` tie-break reversal** — flagged, not chased down, not blocking Track 2.
- **The `dimension_summary` confound's own root cause** (`generate_answers()` investigation) — still uninvestigated, unchanged from before this session.

## Parked (unchanged from before this session)

Confidentiality template field wording, attorney review of engagement agreement Section 3, LinkedIn 19-week content calendar, Category E Direction 2 (shelved). Do not resurface unless Pete reopens.

## Time-anchored

**Quarterly Step-Back due ~August 23, 2026 — now imminent.** Still not run. Flag for Pete at next session open per standing practice.

## Files to attach next session

- **Always**: `tools/_mob.txt` (current version, v4.222).
- **If resuming `built_to_fail`'s own-profile-loss investigation**: `prompts/scd-wcs-remediation-tracker.md` (the closing section and Phase 9 rows from this pass carry the full mechanism detail), `engine/data/salience.py`, `engine/data/states.py`.
- **If resuming Candidate C's commit decision**: same two engine files, plus the tracker's flagged-state overlap tables (Candidate A/B/C comparison) for the exact ripple detail behind the "held" call.
- **If resuming the full taxonomy-wide vector/template re-authoring project**: `prompts/scd-wcs-remediation-tracker.md` in full (per-state disposition for all tracked states, not just Track 2), `prompts/scd-wcs-remediation-program-v1.md` (phase structure).
- **If resuming the ~August 23 Quarterly Step-Back**: the existing staged prep material from the 2026-08-21 session before this one (visual-identity-philosophy question, real Principal Brief quotes, live `globals.css` token values, the Session 58 palette-lock MOB entry).
