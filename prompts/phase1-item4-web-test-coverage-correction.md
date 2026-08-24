# Web Test Coverage Baseline — Correction to a Standing MOB Claim

Date: 2026-08-24. This is a **correction**, not a confirmation — the standing MOB claim was wrong, not just imprecise.

## The standing claim (Section 13a Decision Register, repeated in the prior comprehensive assessment)

*"Zero automated test coverage in the web (TypeScript) layer... Confirmed, not assumed: no `test` script in `web/package.json`, no `.test.*`/`.spec.*` files anywhere under `web/` (including `engine-client.ts`)..."*

## What's actually there — verified directly, this session

**`web/package.json` has a real test script:** `"test": "vitest run"`.

**Four real test files exist:**
- `web/components/ConstellationField.test.ts`
- `web/lib/engine-client.test.ts` — the exact file the standing claim named as an example of what was missing
- `web/lib/resolution-family.test.ts`
- `web/lib/session-store.test.ts`

**`web/vitest.config.ts` exists**, confirming a real, configured test runner, not stray orphan files.

**A real run (`npx vitest run`, executed fresh, not cited from memory):**

```
Test Files  1 failed | 3 passed (4)
     Tests  6 failed | 39 passed (45)
```

45 real tests exist and run. 39 pass. 6 fail (all in `session-store.test.ts`, all related to checkpoint-splice/core-sequence-length assumptions — full detail in `prompts/phase1-item1-path1-phases2-4-status.md`, since this is the same evidence that resolved Item 1's Phase 2 status).

## Root cause of the discrepancy — when the claim went stale, not just wrong

First commit adding `vitest.config.ts`: `bc72daf` — **"Wire checkpoint evaluation into session/answer, stand up vitest."** This is the same commit that wired Phase 2 checkpoints into Path 1 (see Item 1). The "zero test coverage" MOB claim was accurate at the time it was first written, but became stale the moment `bc72daf` landed — and was then repeated multiple times afterward (including by this session's own comprehensive assessment) without being re-checked against the commit that had already superseded it. **The MOB's own session-log narrative already references this vitest suite elsewhere** — entries like "Full vitest run surfaced 6 pre-existing `session-store.test.ts` failures" appear in the Category E build entries — meaning this project's own records already knew about these 6 failures in a different context, while a separate Decision Register row kept asserting zero coverage existed at all. Two parts of the same document disagreed with each other; this correction reconciles them.

## Corrected baseline for Phase 2's decision prep

Not zero. **45 real tests, 4 files, a working `vitest` runner, 39/45 passing, 6 known (now more precisely characterized) failures.** This is a real, if partial, test suite — the actual gap is narrower than "no tests exist": it's "test coverage exists for `ConstellationField`, `engine-client`, `resolution-family`, and `session-store` specifically, with no broader coverage across the rest of the web layer, and 6 known failures needing investigation." Phase 2's Deployment Protection options brief should be built on this corrected baseline, not the old "zero" framing.
