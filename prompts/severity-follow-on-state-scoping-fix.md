# Severity Follow-On State Scoping Fix — Gemini Review, Confirm-or-Reject Only

Status: ready to send. Not an open architecture review — one mechanism, one data
authoring decision, one explicit design choice (any-qualifying-state vs. top-1),
all three fully specified below. Nothing here is open for reinvention.

---

## The defect, confirmed via the real engine, not the calibration harness

`tools/test_aut_ps_01_q23_d_forced.py` — a regression test that drives
`engine/main.py`'s real production functions directly, not
`tools/calibration_runner.py`'s harness — failed. AUT-PS-01 (`paper_shield`,
locked `expected.severity_tier = Entrenched`) landed at `Endemic` instead,
because the real session collected two `SeverityInput`s (SEVER-05 and
SEVER-19) instead of the one it was calibrated against.

Root cause, confirmed directly against the live question data and
`engine/main.py:301`:

```python
severity_follow_on_id = option.severity_follow_on_id if option.severity_trigger else None
```

`severity_trigger` firing is purely a property of the *answered option* — it
has no concept of which state the respondent is heading toward. But
`tools/calibration_runner.py`'s `_SEVERITY_FOLLOW_ON_TARGETS` (the mechanism
used throughout this session's Bucket 2/3 severity-wiring work to describe
"this fix applies to state X") **is** state-scoped — it's keyed by calibration
`test_id`, gating which simulated profile exercises a given follow-on. That
gating has no production equivalent. Q33's option D was deliberately scoped
(commit 5bd5ea3, MOB v4.122, "extended `_SEVERITY_FOLLOW_ON_TARGETS` for
AUT-IA-01 only") to `invisible_influence_architecture` — but Q33's real
`state_targets` also includes `paper_shield` and `leadership_continuity_risk`,
and production fires SEVER-19 for either of those too, with zero gating.

**This is not a one-question bug.** A full scan of every `severity_trigger`
option against its question's real `state_targets`, cross-referenced against
which states each fix's harness extension actually named, found the identical
shape in **13 more cases** — nearly the entirety of this session's Bucket 2/3
severity-wiring effort. In every fix, the "zero blast radius" verification
that was actually run checked *dimensional/ranking* safety for the other
wired states (confirming the trigger option didn't change who those states
matched against) — it never checked *severity* safety, because production has
no mechanism to prevent a severity contribution intended for one state from
being collected on behalf of another, unrelated state a real respondent
happens to be heading toward on the same shared question.

One of the 13 is a named, on-the-record casualty: `the_broken_compass` was
explicitly, deliberately excluded from both SEVER-23 (Q17) and SEVER-24 (Q34)
specifically to protect it from an overshoot (MOB, "Q17/Q34/the_broken_compass
collision... Q17/Q34 are structurally safe by the same per-profile-ID gate
protecting every other external state this session"). That protection exists
only in the calibration harness today. In production, a real respondent
heading toward `the_broken_compass` who answers Q17=B or Q34=C gets the exact
overshoot that finding was written to prevent.

**Explicitly excluded from this fix, on purpose:** Q23/SEVER-05 (`paper_shield`
/ `leadership_continuity_risk`) has zero harness opt-in for *either* wired
state — that's a different defect (never calibration-tested at all, not a
leak from one intended state to another) and needs its own calibration test
authored, not this filter. Not touched here.

---

## Item 1 — `SEVERITY_FOLLOW_ON_INTENDED_STATES`, new real production data

Proposed placement: `engine/data/questions.py`, alongside `QUESTION_LIBRARY`
(same file that already authors `severity_trigger`/`severity_follow_on_id` on
each `AnswerOption` — colocating the intended-state record with the content
whose intent it describes, not a separate/parallel data file).

Every entry below was cross-verified against the MOB's own session-log record
of the specific commit that shipped it (v4.113 through ~v4.127), not just
re-derived from the harness table in isolation — in one case (SEVER-27 /
`heard_and_ignored`) the two sources initially looked like they disagreed;
tracing both rounds showed row 2246 declined it as an unnecessary "bonus
closure" *at that time*, and row 2248 later approved reusing it as a genuine
second trigger — both true, sequential, and consistent with the harness's
current (final) state. Two entries (SEVER-02, SEVER-28, SEVER-29 partially)
were only nameable at question/option granularity in prose, not by their
internal SEVER-## ID directly — for those, the shipped commit's own
`_SEVERITY_FOLLOW_ON_TARGETS` extension is the record, since the commit is
what was actually decided and built, prose or not.

```python
# Maps a severity follow-on's ID to the state(s) it was actually authored
# and design-reviewed for. A follow-on ID absent from this dict is
# unaffected by state-scoped filtering (see engine/main.py) -- this is
# an allowlist for the 14 follow-ons confirmed to share a question with
# state(s) they were never intended to apply to, not a general policy
# for every severity follow-on in the library.
#
# Source: tools/_mob.txt Section 16 session log, commits shipping each
# fix (MOB v4.113 through v4.127), cross-verified against
# tools/calibration_runner.py's _SEVERITY_FOLLOW_ON_TARGETS opt-in table.
SEVERITY_FOLLOW_ON_INTENDED_STATES: "dict[str, list[str]]" = {
    "SEVER-02": ["built_to_fail", "the_undefined_role"],
    "SEVER-10": ["culture_drift", "identity_erosion", "wellbeing_theater"],
    "SEVER-17": ["compression_crisis", "pay_exposure"],
    "SEVER-18": ["dueling_narratives"],
    "SEVER-19": ["invisible_influence_architecture"],
    "SEVER-20": [
        "cultural_overtime", "motivational_architecture_failure",
        "the_basement_standard", "the_inside_track", "the_wrong_reward",
    ],
    "SEVER-21": ["the_paper_tiger"],
    "SEVER-22": [
        "heard_and_ignored", "hr_capture", "leadership_deafness",
        "what_nobody_says",
    ],
    "SEVER-23": ["groundhog_day", "the_burned_credibility"],
    "SEVER-24": ["narrative_lock", "the_burned_credibility"],
    "SEVER-25": [
        "the_basement_standard", "the_inside_track", "the_untouchable",
    ],
    "SEVER-27": [
        "disparate_impact_architecture", "heard_and_ignored",
        "the_tolerated_violation",
    ],
    "SEVER-28": ["the_founders_grip"],
    "SEVER-29": ["the_untouchable"],
}
```

## Item 2 — Filter point: `engine/main.py`, `run_accumulated_engine()`

`rank_states()` (line 610) already runs before severity scoring (lines
612-615) — no reordering needed. Confirmed the qualifying-state computation
(`apply_signal_floor()`, `engine/output.py`) takes only `rankings` and an
optional `noise_baseline`, with zero dependency on `severity_result` — no
circular dependency with `OutputEngine.build()`'s later, independent call to
the same function. Confirmed `apply_signal_floor()`'s default
`noise_baseline=None` path resolves to the identical `_PRECOMPUTED_NOISE_BASELINE`
constant that `OutputEngine.set_noise_baseline()` (called moments later, line
618) also resolves to via its class-level `_cached_baseline` — both calls see
the same baseline, zero risk of the pre-check diverging from the
build-time recomputation. (Aside, confirmed non-blocking: that constant is a
pre-existing 47-entry dict, stale relative to the current 58-state roster —
irrelevant here since `cleared_floor` never reads `noise_baseline`, only
`score_lift_pct`, a cosmetic field, does.)

```python
final_rankings = rank_states(accumulated_vector, answered_question_count, SALIENCE_PROFILES)

qualifying_state_ids = {
    qs.state_id for qs in apply_signal_floor(final_rankings) if qs.cleared_floor
}

severity_engine = SeverityEngine()
for severity_input in (severity_inputs or []):
    intended_states = SEVERITY_FOLLOW_ON_INTENDED_STATES.get(
        severity_input["severity_follow_on_id"]
    )
    if intended_states is not None and qualifying_state_ids.isdisjoint(intended_states):
        continue
    severity_engine.add_input(SeverityInput(**severity_input))
severity_result = severity_engine.score()
```

New imports required in `engine/main.py`:
`from engine.output import OutputEngine, apply_signal_floor` (extends the
existing `OutputEngine`-only import) and
`from engine.data.questions import QUESTION_LIBRARY, SEVERITY_FOLLOW_ON_INTENDED_STATES`
(extends the existing `QUESTION_LIBRARY`-only import).

A follow-on ID **not** in `SEVERITY_FOLLOW_ON_INTENDED_STATES` is untouched —
`intended_states is None` short-circuits the filter, preserving current
behavior exactly for every follow-on outside this 14-item scope, including
Q23/SEVER-05 (explicitly excluded, see above).

## Item 3 — Why "any qualifying state," not top-1

The product already treats a multi-state result as real, not an edge case —
`OutputRouting.qualified_states`, the "multi" output mode, and the whole
Category E cluster-display work all operate on "did this state clear the
signal floor," not "is this state rank 1." Gating the severity filter on
top-1 only would mean: a session that genuinely qualifies for both state X
(the one a given follow-on was authored for) and state Y (the top-ranked
state) would have that follow-on's real, intended severity contribution
silently dropped — even though X is a real, qualifying, presented-to-the-user
condition for that session, just not the highest-scoring one. That's
inconsistent with the product's own existing definition of "this state
applies to this session." Gating on any qualifying state matches
`cleared_floor` exactly — the same test the product already uses everywhere
else a session's real state set matters.

---

## What to confirm or reject — exactly this, no substitutions

1. Does filtering `severity_inputs` against `SEVERITY_FOLLOW_ON_INTENDED_STATES`
   (gated on **any** qualifying state via `apply_signal_floor()`'s
   `cleared_floor`, not top-1 — see Item 3's reasoning above), inserted
   immediately after `rank_states()` and before the `SeverityEngine.add_input()`
   loop, correctly close the leak for all 14 follow-on IDs listed above,
   without side effects to any severity path outside this list?

## What counts as a well-formed response

- **(a) Confirmed as sound.**
- **(b) A specific, narrow objection** to what's actually proposed above — a
  wrong state in the mapping, a real edge case in the filter logic, a genuine
  ordering/dependency problem missed in the trace above. Not a reason to
  reopen the top-1-vs-any-qualifying-state choice from scratch (Item 3 is
  asking for confirmation of that choice specifically, not an open
  re-litigation) and not a proposal for a different mechanism entirely.

Any response proposing a different filtering mechanism, a different data
structure, or additional follow-on IDs beyond the 14 named above is
non-responsive to what was asked — flag it plainly rather than treating it as
a usable proposal, per this project's standing verification discipline.

---

On a clean confirm: dry-run the implementation, run the full calibration
suite against it, and report results before any commit or push. This is a
scoring-integrity fix touching live production behavior — held for Pete's
explicit go-ahead per standing discipline, same as every Tier 1 change in
this project.
