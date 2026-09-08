"""
Patch tools/_mob.txt: append the Section 16 closeout entry for this
continuation session (Legal/Compliance coverage_basis wiring, the Sept 5
Step-Back correction, the Gemini fabrication catch) verbatim as provided,
and bump the MOB version header v4.287 -> v4.288.

Usage:
    python tools/patch_mob_section16_legal_coverage_closeout.py --dry-run
    python tools/patch_mob_section16_legal_coverage_closeout.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

ENTRY = r"""
## SESSION CLOSEOUT (2026-09-07, continuation session)

### One-line summary

Legal/Compliance coverage-sourcing signal (coverage_basis,
has_partial_jurisdictions, restored unpriced_state_ids) designed,
architecture-reviewed, built, and live-verified end-to-end -- plus a
significant correction to the Sept 5 Quarterly Step-Back's central
finding on this module, and one Gemini fabrication caught before it
reached code.

### Shipped and closed this session

1. **Gemini fabrication caught pre-build.** Asked to propose wiring
   architecture for the Legal/Compliance module, Gemini fabricated
   nonexistent files (`engine/contract_2.py`, `engine/friction_tax_2.py`)
   to support its claim that wiring already existed. Filenames confirmed
   fabricated via direct repo check. Per standing verification discipline,
   nothing was built on this response until independently confirmed.

2. **Major correction to the Sept 5 Quarterly Step-Back's Legal/Compliance
   finding -- CORRECTED.** That session's "cold pass" concluded
   `compute_legal_compliance_exposure()` had zero client-facing wiring.
   This was wrong. The engine -> `contract.py` -> `types.ts` chain has been
   fully wired since **commit `46c1e0c`, 2026-08-04** -- over a month
   before the Sept 5 finding. Root cause: a stale section-header comment
   in `friction_tax.py` (~lines 1986-1994) still claimed "NOT wired,"
   and the Sept 5 verification pass trusted that comment instead of
   tracing the actual call graph, despite claiming to have done so. The
   real gap was narrower than tracked: `contract.py` and `types.ts` were
   already correct; `PrivateOutput.tsx` simply never rendered the field
   (zero references, confirmed by grep). The stale comment has now been
   corrected in the same commit that extends the wiring (see below).

3. **coverage_basis / has_partial_jurisdictions / unpriced_state_ids
   wiring -- DESIGNED, ARCHITECTURE-REVIEWED, BUILT, LIVE-VERIFIED, CLOSED.**
   Product decision (Pete): the UI must eventually distinguish
   federal-penalty exposure from state-penalty exposure. Data-layer work
   to support that is complete; UI rendering explicitly deferred to a
   separate follow-on spec (not scoped this session).
   - Gemini proposed the original architecture (aggregate flags over
     per-state array; correct call given aggregation happens before any
     sourcing signal could attach).
   - Claude Code verified the proposal against live source and caught a
     real domain error: Gemini's proposal hardcoded
     `coverage_confidence="FEDERAL_FALLBACK"` for Clusters 3, 4a, 4c, and
     5, none of which ever call `resolve_coverage_gate()` at all -- no
     coverage question is asked for them, so `FEDERAL_FALLBACK` would
     have falsely implied a coverage check occurred and defaulted to
     federal. Corrected to an explicit third value, `"NOT_APPLICABLE"`
     (Pete's call -- explicit signal over a bare `None`, so the UI can
     later distinguish "no jurisdiction question applies" from "unknown").
   - Claude Code drafted the corrected design (three-value
     `coverage_confidence`, `NOT_APPLICABLE`-filtering in aggregation,
     `coverage_basis: null` at the aggregate level rather than a 4th enum
     value, `LegalCurveLookup` field-threading for Cluster 4's early
     4a/4c returns vs. the real gate-touching 4b fallthrough) -- correctly
     flagged by CC itself as a draft requiring Gemini's actual review, not
     a decided architecture. Sent back through Gemini, confirmed clean on
     all four review points, including an alternative-design question
     (hoisting the gate call vs. field-threading) resolved in favor of
     the threaded approach to preserve lazy execution for 4a/4c.
   - Built in 4 per-file commits: `5a08052` (`engine/friction_tax.py` --
     dataclasses, all construction sites, aggregation logic, stale
     comment fix), `fcc20f3` (`engine/contract.py` -- mapping, including
     restored `unpriced_state_ids`), `b3c011e` (`web/lib/types.ts` --
     interface), `6bdbb83` (`tools/test_friction_tax.py` -- 20 fixture
     updates for the two new keys; mechanical, no logic changes).
   - Engine test suite: 838/838 assertions, 0 failures, exact match to
     pre-session baseline. `tsc --noEmit`: clean, 0 errors.
   - **Live-verified in production**, 3 of 4 target branches with real
     200s and exact expected values: CONFIRMED (`coverage_basis:
     "state_specific"`), FEDERAL_FALLBACK (`"federal_baseline"`),
     NOT_APPLICABLE-only (`coverage_basis: null`), and a cross-cluster
     case (CONFIRMED + NOT_APPLICABLE together) confirming the exclusion
     logic holds in practice, not just in the test suite.
   - One test-input error during live verification (`headcount` sent as
     a JSON string) produced a 500/400; correctly diagnosed via Vercel
     runtime logs as CC's own test payload, not a regression, before any
     assumption was made. Corrected and retested clean.

### Named exception to live-verification practice -- do not silently fold
    into "done"

- **True "mixed" `coverage_basis` (CONFIRMED + FEDERAL_FALLBACK together)
  is structurally unreachable from a single live request today.**
  `resolve_coverage_gate()` runs with identical `(headcount, jurisdictions,
  claim_type="general")` for every Cluster 1/2/4b state in one call, so
  every gate call in a request shares one outcome. This is not a bug in
  what shipped -- the `"mixed"` branch is correct logic for whenever
  per-state gate resolution exists -- but this session's live testing
  could only exercise 3 of the 4 possible `coverage_basis` outcomes.
  Tracked in Decision Register: `"mixed"` remains logic-verified via the
  test suite but not live-verified, pending either a genuinely
  multi-jurisdiction-confidence test profile or per-state gate resolution
  work that doesn't exist yet.
- **`PrivateOutput.tsx` runtime safety (item 4 of the live round-trip) --
  code-level guarantee only, not a literal "loaded the page, watched it
  render" confirmation.** CC could not locate a live UI path that
  actually invokes `/api/result` and renders results this session (the
  two terminal CTAs found were a different diagnostic path and a
  contact/sales link; neither called the engine). CC stopped rather than
  keep guessing at production CTA behavior, correctly avoiding an
  unintended production side effect. Substitute evidence accepted as
  sufficient: `PrivateOutput.tsx` has zero references to
  `legal_tail_risk_exposure` (confirmed by grep this session and last),
  so a component that never reads the field cannot be broken by its
  shape changing; `tsc --noEmit` passes clean end-to-end both before and
  after. This is a deliberate, named exception, not a gap to be
  rediscovered later as an oversight.

### On the horizon -- updated

- **New Priority Queue item (UI rendering follow-on):** `PrivateOutput.tsx`
  needs a rendering block for `legal_tail_risk_exposure`, now including
  `coverage_basis`/`has_partial_jurisdictions`/`unpriced_state_ids`. UX
  decisions needed (how `coverage_basis` affects visual hierarchy, caveat
  copy for `has_partial_jurisdictions`, how to name unpriced clusters via
  `unpriced_state_ids`). Explicitly out of scope this session by design.
  This is now the actual remaining piece of what Priority Queue item 1
  originally meant -- not "wire the module" (already true since 2026-08-04,
  previously mistracked) but "render what's already computed."
- Prior Priority Queue items 2-4 (PARTIAL state verification,
  `extreme_high_confidence` investigation, v2 token migration) unchanged,
  not touched this session.
"""

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.287"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.288"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')

    count = content.count(OLD_VERSION_HEADER)
    if count != 1:
        print(f'ERROR: version header found {count} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content + ENTRY
    new_content = new_content.replace(OLD_VERSION_HEADER, NEW_VERSION_HEADER, 1)

    if args.dry_run:
        print('DRY RUN -- version header found exactly once, append would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
