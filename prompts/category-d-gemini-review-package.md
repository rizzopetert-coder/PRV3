# Category D — Gemini Architecture Review Package (corrected re-review)

Status: ready to send. This is a **corrected** re-review, not a fresh review — Gemini's first
pass on Category D contained two confirmed-wrong claims (dead-code rendering target, a fabricated
financial formula) and one confirmed-wrong fact (core question count). All three are stated
explicitly below so this review starts from an accurate baseline instead of re-deriving one.
Full context: prompts/category-d-build-scope.md (the governing document — read that first) and
prompts/category-d-condensed-diagnostic.md (original concept).

Standard discipline applies on the way back in: whatever Gemini returns here gets independently
verified against real source before anything is treated as buildable — same as both prior passes
on this feature.

---

## 1. The finalized 9-question set

**Final 9, locked, no further changes expected:** Q01, Q05, Q07, Q12, Q14, Q15, Q26, Q47, Q50 —
all drawn from the live 42-question `PHASE_1_QUESTION_SEQUENCE` (`web/lib/session-store.ts`),
each individually checked against `checkpointIdMap` — re-verified directly against
`web/app/api/diagnostic/session/answer/route.ts` for this package: the map's real keys are
`Q11`, `Q19`, `Q27A`, `Q27B` (both Q27 branches present, both mapping to the same canonical
`"Q27"` checkpoint position; Phase 1's locked intake adapter always takes the Q27B branch, but
the map doesn't hardcode that assumption) — and against every
option's `severity_trigger`/`severity_follow_on_id` in `engine/data/questions.py` — not assumed
safe from `state_targets` alone. Full table, exclusion reasoning (Q34/Q41/Q46), and the Q11
drop/Q15 replacement history are in `prompts/category-d-build-scope.md` Section 3 — reproduce
that table rather than re-deriving question selection here.

**Why this matters architecturally, not just editorially:** the reason Q11 got dropped is
structural, not stylistic — `checkpointIdMap` fires real checkpoint/severity-follow-on splicing
keyed to literal question IDs, regardless of what sequence they're embedded in. This is why
Category D needs its own separate session/API infrastructure (see prompts/category-d-build-scope.md
and the architecture verification already run) rather than reusing `session/answer/route.ts`
with a mode flag — reuse would risk silently invoking full-diagnostic calibration machinery
inside a condensed flow that was never designed to carry it. Confirm this reasoning holds for
whatever session/API shape gets proposed for the condensed flow.

---

## 2. Rendering target — output-renderer.ts is dead, propose a real path

**Confirmed fact, not in dispute:** `web/lib/output-renderer.ts`'s `renderPrivateOutput()` has
**zero callers anywhere in the repo** (verified by direct repo-wide grep this session). This is
the same dead function Category E Direction 3 already found and deliberately left untouched.
Gemini's first review routed Category D's rendering through it — that proposal would compile
clean and render nothing a respondent would ever see. Do not propose this function again.

**Starting point for a real proposal, not a blank slate:** `web/components/PrivateOutput.tsx` is
the real, live component every actual respondent's result renders through today. It reads a
`PrivateOutputPayload` directly (no view-model layer in between) and is organized as a sequence
of clearly-bounded blocks (condition header, dimensional shape, observable indicators, liability
text, asset/resolution text, co-occurring states, CTA) — several of which Category D's condensed
report plausibly wants (condition header, a truncated indicator list, resolution routing), and
several of which it plausibly doesn't (the full co-occurring-states cluster, friction tax's own
Block 6).

Given the same reasoning that justified separate session/API infrastructure in Section 1 above —
avoid entangling condensed-tier logic with the full diagnostic's already-shipped, already-tested
surface — the direction that's consistent with what's already been established is a **new,
separate component** (e.g. `web/components/CondensedOutput.tsx`), not a mode flag bolted onto
`PrivateOutput.tsx` itself. It would take a smaller, condensed-specific payload shape and add the
visible-truncation UI (Section 1 of the build scope doc — greyed/locked additional indicators,
explicit count) that has no equivalent in the full report at all.

**Resolved, not open for Gemini's review:** the condensed report does **not** include
`ConstellationField` (live mode). Pete's decision — an 8-10-question `dimension_summary` is too
thin to fill the shape convincingly, and using it risks quietly misrepresenting an org's real
profile from a fraction of the full diagnostic's signal. That's a credibility problem, not just a
visual one, and it cuts against the same "credibility over calculation" principle already
governing the financial mechanic in Section 3 below. The condensed report is deliberately,
honestly thin — primary verdict, 2-3 indicators, the locked-truncation affordance — rather than
simulating having data it doesn't have. `CondensedOutput.tsx` should not import or reference
`ConstellationField` at all.

---

## 3. The financial mechanic — build exactly this, not a re-derivation

Gemini's first review proposed `Estimated Consequence = Headcount × BLS Mean Industry Wage ×
Attritional Tax% (12%–18%)`. This is confirmed fabricated: that formula, that range, and the
phrase "Attritional Tax %" do not exist anywhere in this codebase. Repo-wide search found no
match. The closest real thing is `engine/friction_tax.py`'s `_attritional_fraction()` — a real
function, but it maps a *state's own calibration score* to a **5%–25%** range (not 12–18%) for
the full paid diagnostic's multi-state compounding math, a structurally different mechanism
serving a different metric (aggregate multi-state organizational exposure, not one departing
employee's replacement cost). Likely cross-contamination from the word "attritional" appearing
elsewhere in this project's Friction Tax documentation, not a real proposal grounded in what was
sent. **Do not build Section 4 of Gemini's first review under any framing.**

**What was actually scoped, quoted verbatim (one continuous sentence) from
prompts/category-d-build-scope.md Section 2's own "Recommendation:" line,** for Gemini to review
this time instead of re-deriving its own version:

> Use the midpoint of the general (non-executive) range, roughly 50%–75% of one estimated
> departing employee's salary, explicitly framed as a range rather than a single number, and
> avoid the executive-tier 100%–200% figures entirely for this free, intentionally-simple
> mechanic — reserve any role-tiered precision for the full paid Dx if ever built there.

Mechanic: `low = industry_wage × 0.50`, `high = industry_wage × 0.75`, where `industry_wage`
comes from the new `get_industry_wage()` accessor (Section 4 below) keyed on the respondent's
already-collected `industry` intake field. Headcount is not part of this specific figure — the
benchmark is per-departing-employee, not org-wide. This is a single, honestly-labeled range, not
a computed-precision number, and explicitly NOT Friction Tax's multi-state compounding model.

---

## 4. `get_industry_wage()` — real proposed code, for line-by-line review

`_INDUSTRY_WAGE_DATA` (`engine/friction_tax.py`, currently module-private, `dict[str,
tuple[float, str, str]]` keyed by the 9 industry categories intake already collects) needs a
small public accessor. Proposed placement: immediately after `_INDUSTRY_WAGE_DATA`'s definition
(closes at line 341) and before `resolve_headcount_bucket()` (line 343) — same file region,
grouping the two small public lookup helpers together.

Proposed signature, matching this file's own real, confirmed convention
(`PAYROLL_BASELINE_GRID.get()`, `ORG_TYPE_SCALARS.get()` — every lookup in this file resolves an
unrecognized key to `None`, never raises):

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

This is Claude Code's proposal, informed by direct trace of the file's real conventions — not
yet Gemini-cleared, not yet built. Confirm this signature/placement is sound, or propose a
corrected version grounded in the same real conventions (not a new pattern unrelated to how this
file already works).
