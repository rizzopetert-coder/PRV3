"""
Patch tools/_mob.txt: append the Section 16 closeout entry for this
session (Block 4d legal_tail_risk_exposure UI rendering, the Gemini
fabrication catch, the last-session exception correction, the
partial_state_flag structural finding, and the live production
headcount:"" bug fix) verbatim as provided, and bump the MOB version
header v4.288 -> v4.289.

Usage:
    python tools/patch_mob_section16_block4d_headcount_closeout.py --dry-run
    python tools/patch_mob_section16_block4d_headcount_closeout.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

ENTRY = r"""
## SESSION CLOSEOUT (2026-09-08)

### One-line summary
Priority Queue item 1 (legal_tail_risk_exposure UI rendering, Block 4d)
designed, Gemini-reviewed, built, and live-verified -- closed. Along the
way: one Gemini fabrication caught pre-ship, one correction to last
session's named exception, one structural engine finding documented in
code, and one live production bug (500s on empty headcount, affecting
ALL Path B self-select requests, not just legal-scoring states) found
and fixed.

### Shipped and closed this session

1. **Block 4d -- legal_tail_risk_exposure rendering, PrivateOutput.tsx.**
   Architecture-reviewed by Gemini (all four review points cleared).
   coverage_basis-tiered caveats, has_partial_jurisdictions as a
   secondary lighter caveat, unpriced_state_ids resolved to state names
   via the existing stateNameById map, band rendered typographically
   only (no color ramp -- rust remains Endemic-severity-reserved).
   types.ts's LegalTailRiskExposure.low/.high widened to `number | null`
   as a verified prerequisite (real engine behavior: low can be None
   while has_unpriced_conditions is true).

2. **Gemini fabrication caught pre-ship.** During architecture review,
   Gemini cited a specific "often 1-4 employees" figure for state
   coverage thresholds and a verbatim-quoted line from the visual
   identity doc. Independently checked against STATE_COVERAGE_THRESHOLDS:
   real CONFIRMED range is 1-12 employees (WV=12), not "often 1-4" --
   the figure was dropped from all shipped copy and comments. The quoted
   visual-identity line was also not used verbatim, pending confirmation
   against the actual source doc. Underlying conclusions (no color ramp
   for the band; low/high nullability is real) were independently
   verified against the actual code and are correct.

3. **Correction to last session's named exception.** Last session's
   handoff stated no live UI path could be found that invokes
   /api/result. This was wrong, not incomplete: DiagnosticFlow.tsx's
   /diagnostic full Q&A path renders <PrivateOutput> with real engine
   data and reaches /api/result via handleTakeDiagnostic() in
   app/diagnostic/page.tsx. Confirmed twice this session, including via
   the production bug investigation below.

4. **Structural finding, documented in code:** resolve_coverage_gate()'s
   CONFIRMED-branch partial_state_flag can never surface in the
   aggregate has_partial_jurisdictions signal -- it only sets True when
   applies=False, which forces status=NOT_APPLICABLE, which the
   aggregation loop excludes before ever reading the flag. The only
   reachable path is FEDERAL_FALLBACK+PARTIAL (no CONFIRMED jurisdiction
   present), where partial_state_flag is set unconditionally. Documented
   in a code comment at friction_tax.py's NOT_APPLICABLE exclusion line.
   Block 4d's has_partial_jurisdictions caveat copy was corrected to
   describe only the reachable case (was originally written to describe
   the unreachable one).

5. **Live production bug found and fixed.** self-select "Take the
   diagnostic" (handleTakeDiagnostic(), app/diagnostic/page.tsx)
   hardcodes headcount: "" and was 500ing on production for ANY Path B
   request through that button -- not just legal-scoring states, since
   resolve_headcount_bucket() is called unconditionally by both
   compute_friction_tax() and compute_legal_compliance_exposure() before
   any per-state logic runs. Three-part fix:
   - resolve_headcount_bucket() no longer raises on unusable headcount;
     returns None.
   - resolve_coverage_gate() guards the raw comparison, short-circuits
     to applies=False / confidence=FEDERAL_FALLBACK when headcount isn't
     a real comparable number.
   - Cluster 3's per-capita branch (_single_state_legal_pricing()) was
     found to have a latent bug in this same path: an unusable headcount
     would have produced a fabricated $0-$0 PRICED result, indistinguishable
     from genuine zero exposure. Never previously exercised (every valid
     real headcount resolves to a real bucket) -- surfaced and fixed this
     session, not a regression. Now returns QUALITATIVE_ONLY (real
     exposure, no dollar figure -- same idiom as Cluster 4c/Government),
     landed silently in unpriced_state_ids with no DATA_INTEGRITY_GAP
     warning (this is a bad input, not an internal lookup failure).
   Commits: 2188dcd (Block 4d copy fix), 0607ee2 (structural-finding
   comment), 18ddb40 (all three headcount-guard fixes, one file).
   Deploy dpl_AZMB9ozTVABNisy3jQsjdijx5BXB confirmed Ready.

### Live verification (production, real HTTP round-trips)
Seven payloads confirmed against principalresolution.com, actual
response bodies inspected:
- built_to_fail + headcount="" -- 500 -> 200, both nulls clean
- the_dormant_talent + headcount="" -- 500 -> 200, both nulls clean
- cultural_overtime (Cluster 3) + headcount="" -- QUALITATIVE_ONLY,
  unpriced_state_ids: ["cultural_overtime"], no fabricated $0-$0
- compression_crisis (Cluster 3) + headcount="" -- same shape
- state_specific (NY, headcount=152) -- unchanged, byte-identical
- federal_baseline (no jurisdictions, headcount=152) -- unchanged
- has_partial_jurisdictions (TX only, headcount=152) -- unchanged,
  also confirms item 1's corrected copy renders against this exact case

### Test suite / type check
tsc --noEmit clean throughout. Full 11-script suite: 838/838, unchanged
from pre-session baseline across every round this session, including
after the engine-touching headcount-guard fixes.

### Named exceptions -- not gaps to rediscover later
- has_partial_jurisdictions: live-triggered this session (was
  logic-verified-only as of last session's handoff). Both reachable
  and unreachable branches now understood and documented.
- headcount: "" in handleTakeDiagnostic() -- the underlying bug (crash)
  is fixed, but WHY that button hardcodes an empty headcount rather
  than collecting one first is an open product/UX question, not
  resolved this session. New Priority Queue item below.

### On the horizon -- updated Priority Queue
1. **New: why does handleTakeDiagnostic() hardcode headcount: ""?**
   Either the self-select flow never collects headcount before this
   button (a real product gap -- coverage-gated states can't be priced
   without it) or it's supposed to be wired to something and isn't.
   UX/product-scope decision, not a bug -- the crash it caused is
   already fixed.
2. PARTIAL coverage-threshold state verification (~30 of 44 states) --
   unchanged.
3. extreme_high_confidence calibration tier at 0/1 -- unchanged.
4. v2 token migration for the homepage -- unchanged, architectural only.
"""

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.288"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.289"


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
