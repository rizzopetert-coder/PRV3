"""
PRV3 -- Append Addendum 10 to prompts/friction-tax-legal-compliance-
methodology.md: locks the score-interpolation formula for Clusters 1,
4a, 4b, and 5 (log-scale, anchored to the real 1-2 domain), sets
Cluster 3's scope percentages (25%/75%, explicit design judgment not
sourced data), locks Cluster 5 to statutory-max-only for now, writes
INDUSTRY_NON_EXEMPT_RATIO into the doc as source of record, and
documents why this addendum exists -- a formula and percentages were
referenced in conversation as already-decided when neither had been
captured anywhere, caught by a verification search before anything
was written into code.

Usage:
  python tools/patch_legal_compliance_addendum10.py --dry-run
  python tools/patch_legal_compliance_addendum10.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-legal-compliance-methodology.md"

# ---------------------------------------------------------------------
# 1. Status line update
# ---------------------------------------------------------------------

edit(
    DOC,
    "Does not supersede the Option A\n"
    "attritional-criteria rescale (turnover/productivity/decision-quality), which proceeds\n"
    "independently -- this doc is specifically the deferred Legal/Compliance item that Option A\n"
    "explicitly excluded.",
    "Does not supersede the Option A\n"
    "attritional-criteria rescale (turnover/productivity/decision-quality), which proceeds\n"
    "independently -- this doc is specifically the deferred Legal/Compliance item that Option A\n"
    "explicitly excluded. **Addendum 10 locks the score-interpolation formula (Clusters 1, 4a,\n"
    "4b, 5) and Cluster 3's scope percentages** -- the last open design questions blocking\n"
    "implementation. Full five-cluster implementation (classification tables,\n"
    "INDUSTRY_NON_EXEMPT_RATIO, dollar curves, cross-state aggregation) proceeding now.",
)

# ---------------------------------------------------------------------
# 2. Append Addendum 10, before the trailing "Structural implications"
#    section (the tail of the original parent doc, kept at the end)
# ---------------------------------------------------------------------

ADDENDUM_10 = '''## Addendum 10 — Score-Interpolation Formula Locked, Cluster 3 Scope Percentages Set, Provenance Failure Corrected

**Status:** Closes the "still open" score-to-dollar-position question left unresolved since
Addendum 2, for the three clusters where it remained genuinely undecided (1, 4a/4b, 5). Also
documents INDUSTRY_NON_EXEMPT_RATIO as the source-of-record BLS table Cluster 3's scope math
depends on. Written specifically because the content below was decided verbally with Pete and
never captured in any document -- see "Why this addendum exists" below. Ready to implement.

### The score-interpolation formula (Clusters 1, 4a, 4b, 5)

```
fraction(score) = floor x (ceiling / floor) ^ (score - 1)
```

Anchored to the real 1-2 domain a classified state can actually score, not the nominal 0-2
range the rubric allows in the abstract -- no state classified into any of these clusters has
ever been scored 0 (a 0 would mean the state carries no legal exposure at all, which is
inconsistent with it being in one of these clusters in the first place). Using 0-2 as the
interpolation domain would make each cluster's own stated floor mathematically unreachable by
any real state, since score=0 would map below the floor. At score=1, this formula returns floor
exactly; at score=2, it returns ceiling exactly -- log-scale (geometric), not linear, matching
the precedent set by the attritional multiplier design.

Each cluster supplies its own floor/ceiling, all previously sourced:

- **Cluster 1** (individual/isolated claim): floor $50,000, ceiling $450,000 -- Addendum 1's
  original range, unchanged.
- **Cluster 4a** (SEC/Dodd-Frank, org_type = "Publicly traded"): floor $25,000 (EEOC mediation
  average), ceiling $33,000,000 -- the midpoint of Addendum 5's real average-total-
  organizational-sanction range ($16.5M-$49.5M), used as the score=2 anchor. The $279M historic
  single-award outlier is NOT used as the formula's ceiling -- it stays documented in Addendum 5
  as real context (the single largest award on record), but a per-state formula anchored to a
  rare outlier would overstate every other Cluster 4a state. This mirrors the same reasoning
  that rejected anchoring the original single-curve design to Beck v. Boeing's raw settlement
  figure back in the parent methodology doc.
- **Cluster 4b** (general private-sector retaliation): floor $25,000 (same EEOC mediation
  average as 4a -- the pre-litigation path doesn't depend on org_type). Ceiling is NOT one fixed
  number -- it's the specific client's own real Title VII statutory bracket from Addendum 5's
  headcount-bucket table, so score=2 maps to whatever that client's bracket ceiling actually is.
  For the 100-249 bucket, which itself straddles the 100-employee statutory line
  ($50,000-$100,000), this addendum applies the same midpoint convention just established for
  Cluster 4a's ceiling -- $75,000 -- for internal consistency, not because Pete specified this
  particular sub-case; flagged here explicitly so it's correctable if that wasn't the intent.
  California's FEHA uncapped-damages override (Addendum 5, Addendum 6) still applies on top of
  this formula for CA clients regardless of headcount bucket.
- **Cluster 5** (Safety/regulatory) -- statutory-max curve only: floor $16,550 (single
  serious/other-than-serious violation), ceiling $165,514 (willful/repeat violation). Explicitly
  excludes the $500K+ aggregate multi-violation example (real context, not a formula anchor) and
  excludes the actual-average-assessed-penalty curve entirely -- see "Cluster 5 scoping
  decision" below.

**Cluster 2 is not part of this formula.** Its existing Addendum 2 mechanism (score selects a
discrete tier -- 1 defaults to Tier 2a compensatory, 2 defaults to Tier 2b punitive) already
resolves the same underlying question for that cluster by a different, already-documented
mechanism. Nothing here changes Cluster 2.

### Cluster 3 scope percentages -- design judgment, not sourced evidence

Unlike the interpolation formula above (built entirely from already-sourced dollar anchors) and
unlike INDUSTRY_NON_EXEMPT_RATIO below (real BLS data), these two percentages have no external
source. Labeled as design judgment explicitly so a future session doesn't mistake them for
verified figures:

- **score=1:** 25% of the affected non-exempt subgroup
- **score=2:** 75% of the affected non-exempt subgroup

Where the affected non-exempt subgroup itself = `headcount_midpoint x
INDUSTRY_NON_EXEMPT_RATIO[industry]` (see below).

100% was the initial proposal for score=2, revised down to 75% on the reasoning that even a
severe, company-wide wage-and-hour pattern realistically rarely touches every single non-exempt
employee without exception -- some fraction is plausibly outside the affected pattern's actual
reach (different location, different manager, different shift) even in a severe case. This
revision itself is also judgment, not data -- flagged the same way.

### Cluster 5 scoping decision: statutory-max only, actual-average deferred

Cluster 5 implements using only the statutory-maximum curve (floor $16,550, ceiling $165,514)
for now. The actual-average-assessed-penalty curve that Addendum 8 locked as part of the
both-numbers design (statutory max as worst-case ceiling, actual average as realistic expected
value) is explicitly deferred, alongside the paused OSHA State Plan jurisdictional research
(Addendum 9) -- both depend on the same unfinished research (only Oregon currently has both
numbers; actual-average data is missing for the other 10 touched states and all 11 unresearched
states). Implementing the actual-average curve now would mean either fabricating placeholder
averages for 49 states that don't have real ones, or shipping a curve that's only real for one
state out of fifty -- neither is acceptable, so this stays a real, named future step rather than
a silent gap.

### INDUSTRY_NON_EXEMPT_RATIO -- source of record

Real BLS data, feeding Cluster 3's affected-subgroup calculation (`headcount_midpoint x
INDUSTRY_NON_EXEMPT_RATIO[industry]`). Sources: BLS CPS tables cpsaat18c.pdf (total employed by
industry, 2025) and cpsaat45.pdf (hourly-paid workers by industry, 2025); BLS CES (state/local
government employment, June 2026); BLS nonprofit sector research data (2022, most recent
available). Confidence varies by industry, documented per entry:

| Industry | Ratio | Confidence note |
|---|---|---|
| Manufacturing & Industrial | 0.557 | -- |
| Healthcare & Life Sciences | 0.560 | -- |
| Financial Services | 0.285 | -- |
| Professional Services | 0.227 | -- |
| Retail & Hospitality | 0.662 | -- |
| Technology | 0.280 | BLS "Information" sector -- narrower than colloquial "Technology," likely understates the real ratio |
| Government & Public Sector | 0.44 | Blends CPS + CES surveys, softer confidence than the others |
| Nonprofit & Education | 0.135 | Education component only -- "Nonprofit" is genuinely untracked by BLS (confirmed via a 2024 Senate oversight letter to DOL), not a research gap on this project's end |
| Other | 0.556 | Real national aggregate, BLS 2025 |

### Why this addendum exists

A score-interpolation formula and a set of Cluster 3 scope percentages were referenced in
conversation as though already decided and documented, when neither had actually been captured
anywhere -- not in this methodology doc, not in any Gemini review artifact, not in the
MemPalace. The gap surfaced because Claude Code's standing verification practice (checking
tools/gemini_responses/, tools/gemini_prompts/, and a MemPalace search before treating a
referenced decision as real) came back empty, and that gap was raised explicitly rather than the
missing formula being reconstructed from guesswork or silently assumed. Caught before anything
was written into engine code or even into this doc -- this addendum is the fix: writing the
actual decision down in full, with sourced content (the formula's dollar anchors,
INDUSTRY_NON_EXEMPT_RATIO) explicitly distinguished from design judgment (Cluster 3's
percentages, the 4b 100-249 midpoint convention), so this doesn't have to be reconstructed from
memory again.

## Structural implications (bigger than Option A)'''

edit(
    DOC,
    'unlike /diagnostic\'s Stages 4-5, which lost its plan entirely to compaction. This doc is\n'
    'written specifically so that doesn\'t happen here too.\n'
    '\n'
    '## Structural implications (bigger than Option A)',
    'unlike /diagnostic\'s Stages 4-5, which lost its plan entirely to compaction. This doc is\n'
    'written specifically so that doesn\'t happen here too.\n'
    '\n'
    + ADDENDUM_10,
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 120 chars): {old[:120]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
