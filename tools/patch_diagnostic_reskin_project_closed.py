"""
PRV3 -- Close the /diagnostic Visual Identity Reskin project entirely,
not just the OD-07 rollback specifically. Confirmed this session via a
full-site grep sweep (see conversation) that every file the rescope doc
named as still needing the v2 rename was already correctly on v1 and
never touched by OD-07. Also fixes the last stale comment this project
left behind (layout.tsx's anti-flash script, which still referenced a
"Stage 4" that shipped and was then reverted).

Usage:
  python tools/patch_diagnostic_reskin_project_closed.py --dry-run
  python tools/patch_diagnostic_reskin_project_closed.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ---------------------------------------------------------------------
# 1. layout.tsx -- fix the stale "until Stage 4" anti-flash comment
# ---------------------------------------------------------------------

edit(
    "web/app/layout.tsx",
    "        {/*\n"
    "          Visual identity v2 theme persistence (OD-07, Stage 1) — blocking\n"
    "          script, runs before first paint, sets data-theme on <html> from\n"
    "          localStorage before React hydrates. Inert today: no page writes\n"
    "          to prv3-theme yet (ThemeSwitcher isn't mounted anywhere until\n"
    "          Stage 4), so this never fires in practice until then. Prevents\n"
    "          flash-of-wrong-theme once it does. suppressHydrationWarning\n"
    "          above is required because this attribute is set outside React's\n"
    "          render, after the server-rendered markup (which never has\n"
    "          data-theme) is sent.\n"
    "        */}",
    "        {/*\n"
    "          Visual identity v2 theme persistence (OD-07, Stage 1) — blocking\n"
    "          script, runs before first paint, sets data-theme on <html> from\n"
    "          localStorage before React hydrates. ThemeSwitcher (OD-07) is not\n"
    "          currently mounted anywhere -- infrastructure left dormant after\n"
    "          the v1 rollback, commit b8860b5. This script may still fire for a\n"
    "          returning visitor with a stale prv3-theme value in localStorage,\n"
    "          but doing so has no visible effect today -- no live page consumes\n"
    "          the resulting data-theme-scoped CSS variables. suppressHydrationWarning\n"
    "          above is required because this attribute is set outside React's\n"
    "          render, after the server-rendered markup (which never has\n"
    "          data-theme) is sent.\n"
    "        */}",
)

# ---------------------------------------------------------------------
# 2. tools/_mob.txt -- version bump
# ---------------------------------------------------------------------

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.94",
    "\\\\\\#\\\\\\# MOB v4.95",
)

# ---------------------------------------------------------------------
# 3. tools/_mob.txt -- new Section 13a Decision Register row, CLOSED
# ---------------------------------------------------------------------

edit(
    "tools/_mob.txt",
    "| Untracked pre-existing file pile (~94 entries: documents/*.docx, prompts/*.md, various tools/patch_*.py and diagnostic scripts) | N/A — repo hygiene, not a Tier 1-4 workflow item | Open, deliberately deferred |",
    "| /diagnostic Visual Identity Reskin — Stages 4-5 — CLOSED, no work required | 3 | Closed | Confirmed via a full-site grep sweep this session (text-ink/bg-ink/border-ink, bg-field, font-serif as a Tailwind class, ThemeSwitcher import/usage, data-theme, and all six OD-07 var() tokens) plus direct reads of every file the rescope doc (prompts/diagnostic-reskin-stages-4-5-rescope.md) named as still needing the v2 rename: AssemblyPanel.tsx, SignatureCard.tsx, StateDrawer.tsx, ShareButton.tsx, ShareableOutput.tsx, and every route under /about, /ask, /book, /share, /dev/diagnostic-preview. All confirmed already on locked v1 tokens (charcoal/paper/slate/rust, font-display) -- never touched by OD-07 in the first place, not files that happened to be skipped. With OD-07 rolled back to v1 across the four files it did reach (commit b8860b5), there is nothing left anywhere in the site for Stages 4/5 as originally conceived (extending v2/OD-07 outward) to do. Closes the /diagnostic reskin project entirely, not just the OD-07 rollback specifically | This session (Claude Code) | Closed -- no further check-in. If OD-07 or a future visual identity version is deliberately revisited later, that is new, unscoped work, not a reopening of this row |\n"
    "| Untracked pre-existing file pile (~94 entries: documents/*.docx, prompts/*.md, various tools/patch_*.py and diagnostic scripts) | N/A — repo hygiene, not a Tier 1-4 workflow item | Open, deliberately deferred |",
)

# ---------------------------------------------------------------------
# 4. tools/_mob.txt -- Section 13b Priority Queue: remove item 1, renumber
# ---------------------------------------------------------------------

edit(
    "tools/_mob.txt",
    "Priority order for next session, in sequence:\n"
    "\n"
    "1. /diagnostic Stages 4-5 rescoping -- TOP PRIORITY, reconfirmed this session by both Pete and Claude.ai as the highest-leverage next step: a live, user-facing surface gap with no implemented competitor for attention, unlike the Legal/Compliance items below, which remain entirely in design and unshipped. No surviving plan doc -- requires Pete to rescope from scratch.\n"
    "2. Option A rescale + multi-state compounding redesign IMPLEMENTED and verified this session (engine/friction_tax.py) -- CLOSES the item open since the output-ceiling bug was caught earlier this session. All 57 states' raw_score/multiplier recomputed under the new [0.05, 0.25] / [0, 6] mapping (Legal/Compliance excluded from the sum, its score preserved for the separate design); compute_friction_tax()'s mean_multiplier fully replaced with the Step 1-3 anchor-plus-diminishing-layers aggregation (geometric decay, K=0.05 breadth loading, N=1 guard forcing loading=1.0 for a single identified state). Verified, not just reasoned about: tools/test_friction_tax.py rewritten 37->45 checks, 45/45 pass, including explicit single-state continuity (bit-for-bit exact match across 10 real states), the N=1 guard, hand-derived Step 1/Step 3 multi-state math (two breadth scenarios), and extrapolation beyond R_max=6. All other engine test suites pass unaffected; 172-profile calibration suite unchanged at 169/172, confirming this change is isolated to Friction Tax and doesn't touch state routing/scoring; tsc clean (FrictionTaxEstimate's {low, high, currency} shape unaffected by the internal formula change).\n"
    '3. Reopen the deferred "urgency window" (Diagnostic Dimension Expansion) alongside #2 -- same compounding design conversation applied to urgency, not dollar cost, done together rather than re-deriving the reasoning separately later.\n'
    "4. Legal/Compliance package -- ready for Gemini review as-is (full classification across 5 clusters, 5 sourced dollar curves, cross-state aggregation design, Cluster 4's org_type-gated reframe). See prompts/friction-tax-legal-compliance-methodology.md, Addenda 1-5. Send now, don't wait on jurisdictional research (item 5 below).\n"
    "5. OSHA jurisdictional research -- PAUSED, not abandoned (Addendum 9). Full scope documented for pickup without rediscovery: 11/22 OSHA State Plan states researched, 11 fully unresearched (Nevada, New Mexico, North Carolina, Puerto Rico, Tennessee, Utah, Vermont, Virginia, Wyoming, plus formal Minnesota/Michigan writeup), 10 of the 11 researched states need actual-average-penalty backfill (only Oregon currently has both statutory-max and actual-average figures). Resume directly from Addendum 9's scope list when reprioritized -- no rescoping needed, unlike item 1 above.\n"
    '6. Intake headcount precision redesign -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-headcount-precision-redesign.md). SCHEMA-LEVEL SCOPE -- larger than any other Friction Tax proposal this session: replaces the 6-value headcount bucket dropdown with a precise numeric "about how many employees" stepper (variable increment: steps of 1 from 1-50, 5 from 50-250, 25 from 250-500, 100 above 500). Originates directly from the Demographic Applicability Filter\'s ADA (15+ employees) / FMLA (50+ employees) coverage-threshold lead for Clusters 1 and 2 -- a precise number resolves the bucket-boundary ambiguity completely. Also affects Cluster 4\'s Title VII damage-cap tiers (100/200/500) and Cluster 5\'s OSHA penalty-reduction tiers (25/100/250), both currently approximating against bucket edges that don\'t align with the real statutory boundaries. Blocks nothing currently in progress, but should be SEQUENCED BEFORE Clusters 1, 2, 4, 5 are finalized against Gemini, since their threshold logic changes once headcount is precise rather than bucketed -- reviewing those clusters against Gemini before this resolves risks reviewing logic that\'s about to change underneath it. Confirmed this session: no bucket-derivation logic exists anywhere in the codebase today -- PAYROLL_BASELINE_GRID and HEADCOUNT_MIDPOINTS (engine/friction_tax.py) are both keyed directly by the 6 bucket strings (built via `for headcount in HEADCOUNT_BUCKETS`), with no function anywhere that maps a precise int to a bucket; this would need to be built from scratch as part of implementation, not adapted from something existing. IntakeData.headcount\'s type change (str -> int) and whether IntakeEcho should echo a precise number or bucket-like language client-facing are both still open questions in the doc, not yet decided.\n'
    "7. Intake industry taxonomy expansion -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-industry-taxonomy-expansion.md). SCHEMA-LEVEL SCOPE, same flag as item 6 -- second intake-schema proposal this session, kept deliberately separate from the headcount-precision redesign per Pete's direction, not combined. Adds \"Construction\" (NAICS Sector 23) and \"Transportation & Warehousing\" (NAICS Sectors 48-49) to INTAKE_FIELDS[\"industry\"], expanding 9 -> 11 values. Originates from the Demographic Applicability Filter's Cluster 5 finding that is_high_hazard (HIGH_HAZARD_INDUSTRIES) can only ever fire for 2 of the 9 current industry values, while BLS ranks construction and transportation/warehousing among the highest injury/fatality-rate industries nationally -- both currently fall into \"Other,\" indistinguishable from anything else that doesn't fit. REAL DEPENDENCY, not just a code change: PAYROLL_BASELINE_GRID expands from 6x9=54 cells to 6x11=66 cells -- 12 new cells (Construction and Transportation & Warehousing x all 6 headcount buckets) need genuine SUSB/BLS payroll-baseline research sourced before this is implementation-ready, comparable in scope to the original 54-cell population work, not trivial. HIGH_HAZARD_INDUSTRIES update itself is straightforward (add both new values to the existing set).\n"
    "8. causation_pattern -> resolution_families.py routing influence -- split off from Diagnostic Dimension Expansion, not started, no scoping doc.\n"
    "9. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).",
    "Priority order for next session, in sequence:\n"
    "\n"
    "1. Option A rescale + multi-state compounding redesign IMPLEMENTED and verified this session (engine/friction_tax.py) -- CLOSES the item open since the output-ceiling bug was caught earlier this session. All 57 states' raw_score/multiplier recomputed under the new [0.05, 0.25] / [0, 6] mapping (Legal/Compliance excluded from the sum, its score preserved for the separate design); compute_friction_tax()'s mean_multiplier fully replaced with the Step 1-3 anchor-plus-diminishing-layers aggregation (geometric decay, K=0.05 breadth loading, N=1 guard forcing loading=1.0 for a single identified state). Verified, not just reasoned about: tools/test_friction_tax.py rewritten 37->45 checks, 45/45 pass, including explicit single-state continuity (bit-for-bit exact match across 10 real states), the N=1 guard, hand-derived Step 1/Step 3 multi-state math (two breadth scenarios), and extrapolation beyond R_max=6. All other engine test suites pass unaffected; 172-profile calibration suite unchanged at 169/172, confirming this change is isolated to Friction Tax and doesn't touch state routing/scoring; tsc clean (FrictionTaxEstimate's {low, high, currency} shape unaffected by the internal formula change).\n"
    '2. Reopen the deferred "urgency window" (Diagnostic Dimension Expansion) alongside #1 -- same compounding design conversation applied to urgency, not dollar cost, done together rather than re-deriving the reasoning separately later.\n'
    "3. Legal/Compliance package -- ready for Gemini review as-is (full classification across 5 clusters, 5 sourced dollar curves, cross-state aggregation design, Cluster 4's org_type-gated reframe). See prompts/friction-tax-legal-compliance-methodology.md, Addenda 1-5. Send now, don't wait on jurisdictional research (item 4 below).\n"
    "4. OSHA jurisdictional research -- PAUSED, not abandoned (Addendum 9). Full scope documented for pickup without rediscovery: 11/22 OSHA State Plan states researched, 11 fully unresearched (Nevada, New Mexico, North Carolina, Puerto Rico, Tennessee, Utah, Vermont, Virginia, Wyoming, plus formal Minnesota/Michigan writeup), 10 of the 11 researched states need actual-average-penalty backfill (only Oregon currently has both statutory-max and actual-average figures). Resume directly from Addendum 9's scope list when reprioritized -- no rescoping needed.\n"
    '5. Intake headcount precision redesign -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-headcount-precision-redesign.md). SCHEMA-LEVEL SCOPE -- larger than any other Friction Tax proposal this session: replaces the 6-value headcount bucket dropdown with a precise numeric "about how many employees" stepper (variable increment: steps of 1 from 1-50, 5 from 50-250, 25 from 250-500, 100 above 500). Originates directly from the Demographic Applicability Filter\'s ADA (15+ employees) / FMLA (50+ employees) coverage-threshold lead for Clusters 1 and 2 -- a precise number resolves the bucket-boundary ambiguity completely. Also affects Cluster 4\'s Title VII damage-cap tiers (100/200/500) and Cluster 5\'s OSHA penalty-reduction tiers (25/100/250), both currently approximating against bucket edges that don\'t align with the real statutory boundaries. Blocks nothing currently in progress, but should be SEQUENCED BEFORE Clusters 1, 2, 4, 5 are finalized against Gemini, since their threshold logic changes once headcount is precise rather than bucketed -- reviewing those clusters against Gemini before this resolves risks reviewing logic that\'s about to change underneath it. Confirmed this session: no bucket-derivation logic exists anywhere in the codebase today -- PAYROLL_BASELINE_GRID and HEADCOUNT_MIDPOINTS (engine/friction_tax.py) are both keyed directly by the 6 bucket strings (built via `for headcount in HEADCOUNT_BUCKETS`), with no function anywhere that maps a precise int to a bucket; this would need to be built from scratch as part of implementation, not adapted from something existing. IntakeData.headcount\'s type change (str -> int) and whether IntakeEcho should echo a precise number or bucket-like language client-facing are both still open questions in the doc, not yet decided.\n'
    "6. Intake industry taxonomy expansion -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-industry-taxonomy-expansion.md). SCHEMA-LEVEL SCOPE, same flag as item 5 -- second intake-schema proposal this session, kept deliberately separate from the headcount-precision redesign per Pete's direction, not combined. Adds \"Construction\" (NAICS Sector 23) and \"Transportation & Warehousing\" (NAICS Sectors 48-49) to INTAKE_FIELDS[\"industry\"], expanding 9 -> 11 values. Originates from the Demographic Applicability Filter's Cluster 5 finding that is_high_hazard (HIGH_HAZARD_INDUSTRIES) can only ever fire for 2 of the 9 current industry values, while BLS ranks construction and transportation/warehousing among the highest injury/fatality-rate industries nationally -- both currently fall into \"Other,\" indistinguishable from anything else that doesn't fit. REAL DEPENDENCY, not just a code change: PAYROLL_BASELINE_GRID expands from 6x9=54 cells to 6x11=66 cells -- 12 new cells (Construction and Transportation & Warehousing x all 6 headcount buckets) need genuine SUSB/BLS payroll-baseline research sourced before this is implementation-ready, comparable in scope to the original 54-cell population work, not trivial. HIGH_HAZARD_INDUSTRIES update itself is straightforward (add both new values to the existing set).\n"
    "7. causation_pattern -> resolution_families.py routing influence -- split off from Diagnostic Dimension Expansion, not started, no scoping doc.\n"
    "8. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).",
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
