# Category D — Gemini Review, Round 4: Severity-Trigger Handling, Constrained Confirmation Only

Status: ready to send. Same constrained format as round 3
(prompts/category-d-gemini-review-round3-constrained.md), which was the first Category D round
to actually engage with a correction rather than restate a prior fabrication — reusing that
format deliberately. One item, already fully specified. Not an open review.

Context: re-verifying the locked 9-question set against the real `_QDATA` (programmatic check,
not memory) found that the severity/checkpoint screening applied to Q11's replacement was never
retroactively applied to the other 8 already-selected questions. It has been now.

---

## What to confirm or reject — exactly this, no substitutions

> 5 of the condensed session's 9 questions (Q01, Q05, Q12, Q14, Q26) carry real severity
> triggers with real follow-on IDs (SEVER-28, SEVER-25, SEVER-29, SEVER-17, SEVER-08
> respectively). Proposed handling: the condensed session store consumes only
> `accumulated_vector` from the engine's response at every call site, and never reads or acts on
> `severity_follow_on_id` / `severity_input` — the field is computed statelessly by
> `accumulate_one_answer()` regardless of caller, but nothing requires the caller to implement
> the follow-on splice. This is inert by deliberate omission, documented in code as an explicit
> design decision, not a silent gap. Confirm this handling is sound and sufficient to keep
> Category D at zero calibration risk, or state a specific objection. Do not propose an
> alternative session architecture.

---

## What counts as a well-formed response

A well-formed answer is **one of exactly two things**:

- **(a) Confirmed as sound.**
- **(b) A specific, narrow objection** to the proposed handling above — not a replacement
  architecture.

**Any response that proposes an alternative session design, a different accumulation function,
or new session-store fields is non-responsive to what was asked.** Do not evaluate such a
response on its own merits — flag it plainly, same as rounds 1 and 2, not extract something
buildable from it.

---

Standard discipline applies on the way back in: whatever comes back gets independently verified
against real source before treating it as final, then the dry-run proceeds.
