# `decision_paralysis` / `the_lost_map` Tie-Break Reversal — Root Cause Found

Date: 2026-08-24. Investigated the open question flagged in `prompts/scd-wcs-remediation-tracker.md` (line 134): a prior "closed" finding claimed `decision_paralysis` and `the_lost_map` "genuinely win their own 3 dedicated profiles outright" via the rank-2 10-way internal tie; a later pass found `the_uninitiated` now wins those same tied profiles instead, with the actual root cause explicitly flagged as unknown.

## Root cause, found and confirmed directly from source

`engine/accumulation.py`'s `rank_states()` (line 590): `results.sort(key=lambda r: r.distance)`. Python's `sort()` is a **stable sort** — when two states score an exact tie (byte-identical `distance`), whichever entry appears earlier in the pre-sort list order keeps its earlier rank position. That pre-sort order comes directly from `for sid, profile in STATE_PROFILES.items()` (line 572) — **`STATE_PROFILES`'s dict insertion order silently determines who wins an exact tie.**

Confirmed directly: `STATE_PROFILES` dict position — `the_uninitiated`: **9**, `decision_paralysis`: **12**, `the_lost_map`: **21**. `the_uninitiated` sits earlier in insertion order than both, so it mechanically wins any exact tie against either, under this sort. This is the complete, confirmed mechanism — not inferred, verified by reading the actual sort call and the actual dict ordering.

## Was this a change, or was the original claim wrong from the start?

The dict's insertion order is set once, at each state's original `_reg(_profile(state_id=...))` construction call — later `STATE_PROFILES["x"].dimensional_vector = ...` reassignment blocks (the pattern used throughout this session's own SCD-WCS work, including Candidate C) **do not** change dict insertion order in Python; reassigning an existing key's value never moves its position. Confirmed the actual construction-call line numbers: `the_uninitiated` at line 486, `decision_paralysis` at line 555, `the_lost_map` at line 839 — the same relative order as the dict positions.

**Conclusion, with appropriate honesty about its limits:** this ordering is very likely original — state definitions in this file don't get casually reordered (new states are appended via taxonomy expansion, not inserted mid-file), and no reordering-shaped commit was found touching these three states' construction order. The most likely explanation is that **the original "decision_paralysis/the_lost_map genuinely win" claim was inaccurate when first written**, not a real behavior change that happened later — not a regression, a documentation error caught late. This is a strong, well-supported conclusion, not a fully proven one — confirming it beyond doubt would require checking out the exact historical commit from when that original claim was first written and diffing the file's state order at that point, which wasn't done here given the time this item warranted relative to the rest of this session's scope.

## Recommendation: no fix needed, document the mechanism instead

Per the standing preference for a clear recommendation over open-ended deferral, and because the evidence here points clearly one way: **this does not need a "fix."**

- The tie-break winner among exactly-tied states carries no real signal either way — none of the tied states is more "correct" than another purely by which line happens to appear earlier in a source file. Reordering `engine/data/states.py` to make a different state win an arbitrary tie would be a cosmetic change with its own regression-testing overhead, for zero real accuracy gain.
- It doesn't move any counted pass/fail metric — confirmed already in the tracker's own notes (the lenient prominence criterion accepts a tie regardless of which specific state wins it), reconfirmed here.
- The actual value of this investigation is documenting the **mechanism** for future SCD-WCS work: `rank_states()`'s tie-break behavior is insertion-order-based, not a deliberate design choice, and any future taxonomy reordering (including the taxonomy-wide re-authoring project scoped in Item 10) should know this is a real, silent side effect of where a state's construction call happens to sit in the file — worth a one-line comment near `rank_states()`'s sort call, not a behavior change.

This closes the open question in `prompts/scd-wcs-remediation-tracker.md` (line 134) with a definitive mechanism, distinct from and complementary to the taxonomy-wide re-authoring scoping in Item 10 below — this finding doesn't change that project's scope, since it's about tie-break cosmetics, not the real magnitude-dominance problem that project addresses.
