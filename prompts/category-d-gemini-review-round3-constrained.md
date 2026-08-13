# Category D — Gemini Review, Round 3: Constrained Confirmation Only

Status: ready to send. Not an open architecture review. Two prior rounds
(prompts/category-d-gemini-review-package.md and its predecessor) each produced fabricated
proposals — a dead rendering function proposed twice, two independently invented financial
formulas, and a wrong question-count reconstruction, all despite explicit written correction in
the prior round's own prompt. Full pattern on record: tools/_mob.txt Decision Register,
"Gemini fails to incorporate explicit, verbatim correction across review rounds."

This round asks for exactly two things. Nothing else is open for reinvention.

---

## What to confirm or reject — exactly this, no substitutions

**1. Rendering target.**

> The rendering target for Category D's condensed output is a new, separate component,
> `web/components/CondensedOutput.tsx` — NOT `web/lib/output-renderer.ts`'s
> `renderPrivateOutput()` (confirmed dead code, zero callers, do not propose it again under any
> framing). Confirm this is architecturally sound given `PrivateOutput.tsx`'s real existing
> structure, or state a specific objection. Do not propose an alternative rendering path.

**2. Financial mechanic.**

> The financial mechanic is: `low = get_industry_wage(industry) x 0.50`, `high =
> get_industry_wage(industry) x 0.75` — a per-departing-employee percentage range, headcount NOT
> involved. This is final, not a starting point for a different formula. Confirm this
> calculation is correctly implemented as described against `get_industry_wage()`'s real
> signature, or state a specific objection to the math as written. Do not propose an alternative
> formula, range, or additional data source.

`get_industry_wage()`'s real, already-verified signature (`engine/friction_tax.py`, proposed
placement immediately after `_INDUSTRY_WAGE_DATA`, before `resolve_headcount_bucket()`):

```python
def get_industry_wage(industry: str) -> Optional[float]:
    """
    Public accessor for _INDUSTRY_WAGE_DATA's per-employee mean annual wage
    (BLS OEWS May 2023), keyed by the same 9 industry categories intake
    already collects (engine/data/intake.py INTAKE_FIELDS["industry"]).
    Returns None on an unrecognized industry -- matches this file's
    existing lookup convention (PAYROLL_BASELINE_GRID.get(),
    ORG_TYPE_SCALARS.get()), not an exception.
    """
    entry = _INDUSTRY_WAGE_DATA.get(industry)
    return entry[0] if entry is not None else None
```

---

## What counts as a well-formed response

A well-formed answer to each item is **one of exactly two things**:

- **(a) Confirmed as sound.**
- **(b) A specific, narrow objection** to what's actually proposed above — not a replacement for
  it.

**Any response that reads as a new formula, a new function, a new data source, or an alternative
rendering path is non-responsive to what was asked.** Do not evaluate such a response on its own
merits or treat it as a usable proposal — it means the constraint wasn't followed, and the
correct handling is to flag that plainly, the same as the last two rounds, not to extract
something buildable from it.

---

Standard discipline applies on the way back in: whatever Gemini returns gets independently
verified against real source before anything is treated as final — same as every round before
this one.
