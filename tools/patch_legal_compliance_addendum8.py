"""
PRV3 -- Fold Legal/Compliance Addendum 8 (Cluster 5 design decision
locked: statutory max + actual average, both as a range; OSHA State
Plan research now 11 of 22 states touched, scope expanded to include
backfill) into prompts/friction-tax-legal-compliance-methodology.md,
following Addendum 7. Updates the doc's Status line and tools/_mob.txt
item 4.

Usage:
  python tools/patch_legal_compliance_addendum8.py --dry-run
  python tools/patch_legal_compliance_addendum8.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDENDUM8_CONTENT_PATH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad\addendum8_fixed.md"
)

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-legal-compliance-methodology.md"

edit(
    DOC,
    """**Status:** Design in progress. Direction has shifted several times this session as real data
falsified earlier approaches. All 30 Legal-scoring states are classified into 5 mechanism
clusters -- `the_untouchable` reclassified Cluster 2 -> Cluster 1 (Addendum 4, resolving
Gemini's review flag). Cluster 3's interpolation is locked: scope-modulated, not
path-modulated (Addendum 4). Cluster 4 fully resolved into three org_type-gated sub-tracks
(Addendum 5). All 5 clusters now have sourced dollar curves, and the cross-state aggregation
design (Addendum 3) is UNBLOCKED and ready for Gemini review. Systematic jurisdictions
pass complete for California across all 5 clusters (Addendum 6). **OSHA State Plan research
for Cluster 5 IN PROGRESS, 7 of 22 states (Addendum 7)** -- California, Washington, Oregon,
Alaska, Hawaii, Arizona, Indiana researched; variation confirmed genuinely bidirectional
(exceeds federal flat, exceeds federal conditionally/outcome-triggered, clean statutory
parity, statutory parity with documented under-enforcement, and genuinely below federal, all
represented across just 7 states) -- NOT a finished input for implementation, 15 states
remain. Explicitly scoped, not assumed complete: the other 49 states outside Cluster 5's OSHA
research, and the 15 remaining OSHA State Plan states specifically, have NOT been checked --
flagged in the design as known-incomplete jurisdictional treatment, not silently treated as
accurate everywhere outside what's actually been researched. NOT yet implemented. Does not
supersede the Option A attritional-criteria rescale (turnover/productivity/decision-quality),
which proceeds independently -- this doc is specifically the deferred Legal/Compliance item
that Option A explicitly excluded.""",
    """**Status:** Design in progress. Direction has shifted several times this session as real data
falsified earlier approaches. All 30 Legal-scoring states are classified into 5 mechanism
clusters -- `the_untouchable` reclassified Cluster 2 -> Cluster 1 (Addendum 4, resolving
Gemini's review flag). Cluster 3's interpolation is locked: scope-modulated, not
path-modulated (Addendum 4). Cluster 4 fully resolved into three org_type-gated sub-tracks
(Addendum 5). All 5 clusters now have sourced dollar curves, and the cross-state aggregation
design (Addendum 3) is UNBLOCKED and ready for Gemini review. Systematic jurisdictions pass
complete for California across all 5 clusters (Addendum 6). **Cluster 5 design decision
LOCKED (Addendum 8): models both statutory maximum (worst-case ceiling) and actual average
assessed penalty (realistic expected value) as a low/high pair**, consistent with how every
other part of this design already presents a range rather than a single point estimate --
the two numbers can diverge enormously within the same state (Oregon: $16,131 statutory vs.
$604 actual average, a ~27x gap). OSHA State Plan research now 11 of 22 states touched
(Addendum 7 + Addendum 8) -- but locking the both-numbers design expanded scope rather than
closing it: only Oregon currently has both figures confirmed; the other 10 touched states
need actual-average data backfilled, on top of the ~11 states still fully unresearched.
Explicitly scoped, not assumed complete: the other 49 states outside Cluster 5's OSHA
research, the ~11 remaining fully-unresearched OSHA State Plan states, and the actual-average
backfill for the 10 already-touched states, have NOT been completed -- flagged in the design
as known-incomplete jurisdictional treatment, not silently treated as accurate everywhere
outside what's actually been researched. NOT yet implemented. Does not supersede the Option A
attritional-criteria rescale (turnover/productivity/decision-quality), which proceeds
independently -- this doc is specifically the deferred Legal/Compliance item that Option A
explicitly excluded.""",
)

edit(
    DOC,
    """## Structural implications (bigger than Option A)""",
    "__ADDENDUM8_PLACEHOLDER__\n\n## Structural implications (bigger than Option A)",
)


# ============================================================
# tools/_mob.txt
# ============================================================

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.90",
    "\\\\\\#\\\\\\# MOB v4.91",
)

edit(
    "tools/_mob.txt",
    '''Jurisdictions pass, Cluster 5 -- 7 of 22 OSHA State Plan states researched (CA, WA, OR, AK, HI, AZ, IN), 15 remaining (Addendum 7). Every state checked so far has produced a genuinely distinct finding -- no simple pattern has emerged, treat remaining research as comparable effort per state, not diminishing.''',
    '''Jurisdictions pass, Cluster 5 -- design locked (Addendum 8): statutory max + actual average, both as a range, consistent with the rest of the design's low/high presentation -- the two numbers can diverge enormously within one state (Oregon: $16,131 statutory vs. $604 actual average, ~27x gap). 11/22 states touched. Real gap: only Oregon has both numbers -- 10 states need backfill on actual-average data, ~11 states still fully unresearched. Scope larger than originally estimated: locking the both-numbers design expanded remaining work rather than closing it. Every state checked so far has produced a genuinely distinct finding -- no simple pattern has emerged, treat remaining research as comparable effort per state, not diminishing.''',
)


def apply(dry_run: bool) -> int:
    changed = 0
    addendum8_text = ADDENDUM8_CONTENT_PATH.read_text(encoding="utf-8").rstrip("\n")
    addendum8_nested = addendum8_text.replace(
        "# Addendum 8 — Cluster 5 Models Both Statutory Max and Actual Average, Scope Expanded",
        "## Addendum 8 — Cluster 5 Models Both Statutory Max and Actual Average, Scope Expanded",
        1,
    ).replace("\n## ", "\n### ")

    for rel_path, old, new in EDITS:
        if "__ADDENDUM8_PLACEHOLDER__" in new:
            new = new.replace("__ADDENDUM8_PLACEHOLDER__", addendum8_nested)
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
