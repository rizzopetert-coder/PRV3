"""
PRV3 -- Fold Legal/Compliance Addendum 2 (Cluster 2 two-tier restructure,
Cluster 3 sourced formula) into prompts/friction-tax-legal-compliance-
methodology.md, correct the DOL liquidated-damages multiplier error in
experiment-2-employment-litigation-taxonomy.html, and update tools/_mob.txt.

IMPORTANT VERIFICATION NOTE: Addendum 2's own text claims "All 4 spots
need '2-4x' corrected" (referring to the 4 spots fixed earlier this
session for the DOL figure/mechanism caveat). Direct re-check of the live
file found this is not quite right -- only 2 of those 4 spots (lines 643
and 1018) actually contain multiplier language ("3-4x" and "2-4x"
respectively); the other 2 (626, the DOL Recovery data label; 1124, the
closing findings sentence) never stated a multiplier at all and need no
further correction. Only the 2 real instances are fixed here -- flagged
to Pete rather than silently "fixing" 4 spots when only 2 exist.

Usage:
  python tools/patch_legal_compliance_addendum2_and_dol_correction.py --dry-run
  python tools/patch_legal_compliance_addendum2_and_dol_correction.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDENDUM2_CONTENT_PATH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad\addendum2_fixed.md"
)

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================
# research/seven-experiments/experiment-2-employment-litigation-taxonomy.html
# ============================================================

E2 = "research/seven-experiments/experiment-2-employment-litigation-taxonomy.html"

edit(
    E2,
    'The 3–4x liquidated-damages multiplier still applies if an employee pursues litigation — it no longer applies to the administrative path most employers actually face.',
    'The liquidated-damages multiplier — 2x under federal law; some states separately permit treble damages under state law — still applies if an employee pursues litigation; it no longer applies to the administrative path most employers actually face.',
)

edit(
    E2,
    'DOL recovered $259M in back wages FY2025. Liquidated damages (2–4x back wages) no longer apply to pre-litigation administrative settlements as of mid-2025 — the multiplier now applies only if litigation is pursued.',
    'DOL recovered $259M in back wages FY2025. Liquidated damages — 2x back wages under federal law; some states separately permit treble damages under state law — no longer apply to pre-litigation administrative settlements as of mid-2025; the multiplier now applies only if litigation is pursued.',
)


# ============================================================
# prompts/friction-tax-legal-compliance-methodology.md
# ============================================================

DOC = "prompts/friction-tax-legal-compliance-methodology.md"

edit(
    DOC,
    """**Status:** Design in progress. Direction has shifted twice already this session as real data
falsified two earlier approaches. All 30 Legal-scoring states are now classified into 5
mechanism clusters, with 4 of 5 clusters' dollar curves sourced (Addendum, below) -- ready
for Gemini architecture review. NOT yet implemented. Does not supersede the Option A
attritional-criteria rescale (turnover/productivity/decision-quality), which proceeds
independently -- this doc is specifically the deferred Legal/Compliance item that Option A
explicitly excluded.""",
    """**Status:** Design in progress. Direction has shifted twice already this session as real data
falsified two earlier approaches. All 30 Legal-scoring states are now classified into 5
mechanism clusters, and all 5 clusters now have sourced dollar curves (Addenda 1 and 2,
below) -- ready for Gemini architecture review. NOT yet implemented. Does not supersede the
Option A attritional-criteria rescale (turnover/productivity/decision-quality), which
proceeds independently -- this doc is specifically the deferred Legal/Compliance item that
Option A explicitly excluded.""",
)

edit(
    DOC,
    """## Structural implications (bigger than Option A)""",
    "__ADDENDUM2_PLACEHOLDER__\n\n## Structural implications (bigger than Option A)",
)


# ============================================================
# tools/_mob.txt
# ============================================================

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.80",
    "\\\\\\#\\\\\\# MOB v4.81",
)

edit(
    "tools/_mob.txt",
    "3. Legal/Compliance tail-risk methodology -- mechanism classification COMPLETE this session: all 30 Legal-scoring states classified across 5 mechanism clusters (individual claim, class-discrimination, wage-hour, whistleblower, and a newly split-out safety/regulatory cluster), 4 of 5 clusters' dollar curves sourced, see prompts/friction-tax-legal-compliance-methodology.md (Addendum). Two sub-items remain before implementation: (a) a third verified per-claimant rate for Cluster 2 (currently rests on exactly two verified data points, Beck v. Boeing and Velez v. Novartis), (b) the Cluster 3 wage-and-hour multiplier formula, given DOL's mid-2025 liquidated-damages policy change. Ready for Gemini architecture review in parallel with resolving those two.",
    "3. Legal/Compliance tail-risk methodology -- CLOSED this session: mechanism classification complete (all 30 states across 5 clusters) AND all 5 clusters now have sourced dollar curves (Addendum 2: Cluster 2 restructured into two tiers, compensatory ~$1,800-2,500/claimant vs. punitive-inclusive ~$25,000-31,000/claimant, resolved via a third verified data point, Jock v. Sterling Jewelers; Cluster 3 fully sourced, administrative path $1,465/worker, litigation path $2,930/worker, using the corrected FLSA 2x multiplier). See prompts/friction-tax-legal-compliance-methodology.md (Addenda 1 and 2). Design-level open items remain (tier-selection logic is a judgment call, not sourced evidence; per-cluster rubric-score-to-dollar-curve shape not decided; Cluster 3's affected-subgroup definition needs data-availability confirmation) but the sourcing gap blocking implementation is closed. Ready for Gemini architecture review.",
)

edit(
    "tools/_mob.txt",
    '| MemPalace mine -- silent non-persistence, confirmed recurring | 3 | Open -- confirmed twice, root cause unknown | mempalace mine ran without error but did not persist new drawers, verified by direct search rather than assumed from exit status. First observed Session 70 (Section 13\'s general Open Items list, not this register: "MemPalace mine -- Session 70 run did not persist" -- 413 files scanned, prv3 wing, 5 rooms, but drawer count unchanged at 8775 before/after, and a direct search for that session\'s new content, patch_weak_damped_routing_s70, returned nothing). Second confirmed instance this session (August 2, 2026), immediately following the Set 3/compounding closeout Diary Write -- verified by search per standing "verify, don\'t assume" practice, not just trusted. Elevated from a general Priority Queue housekeeping line (Section 13b, item 7) to its own row because two confirmed instances make this a repeatable gap, not a one-off flake, and it specifically undermines MemPalace\'s value as a cross-session searchable record -- the exact retrieval path that was needed and came up empty earlier this session. **Impact if unresolved:** this session\'s full work (Set 3 closure, compounding design, governance cadence repair) has no MemPalace-searchable trace despite a successful Diary Write -- durable record currently exists only in tools/_mob.txt and git history, not in MemPalace | This session (Claude Code) -- confirmed, not fixed | Pete\'s call -- not urgent tonight, but should not silently persist across many more sessions unexamined given confirmed recurrence. Related follow-up (not urgent, logged for future reference): worth a deliberate comparison of MemPalace\'s actual feature set and reliability against open-source alternatives (e.g. mcp-memory-service/doobidoo -- SQLite-based, no embeddings, positioned for reliability via simplicity; Cognee -- graph+vector, native Claude Code plugin, more complete but more moving parts; mem0 self-hosted; Graphiti/Neo4j-backed options for more complex needs) before deciding whether to keep, fix, or replace MemPalace. Not a recommendation to switch -- a note that this comparison hasn\'t been done and should happen before any replacement decision, given the specific failure mode here is silent non-persistence on writes that report success, which argues for weighing simplicity/reliability as its own axis, not just feature completeness |',
    '''| MemPalace mine -- silent non-persistence, confirmed recurring | 3 | Open -- confirmed twice, root cause unknown | mempalace mine ran without error but did not persist new drawers, verified by direct search rather than assumed from exit status. First observed Session 70 (Section 13's general Open Items list, not this register: "MemPalace mine -- Session 70 run did not persist" -- 413 files scanned, prv3 wing, 5 rooms, but drawer count unchanged at 8775 before/after, and a direct search for that session's new content, patch_weak_damped_routing_s70, returned nothing). Second confirmed instance this session (August 2, 2026), immediately following the Set 3/compounding closeout Diary Write -- verified by search per standing "verify, don't assume" practice, not just trusted. Elevated from a general Priority Queue housekeeping line (Section 13b, item 7) to its own row because two confirmed instances make this a repeatable gap, not a one-off flake, and it specifically undermines MemPalace's value as a cross-session searchable record -- the exact retrieval path that was needed and came up empty earlier this session. **Impact if unresolved:** this session's full work (Set 3 closure, compounding design, governance cadence repair) has no MemPalace-searchable trace despite a successful Diary Write -- durable record currently exists only in tools/_mob.txt and git history, not in MemPalace | This session (Claude Code) -- confirmed, not fixed | Pete's call -- not urgent tonight, but should not silently persist across many more sessions unexamined given confirmed recurrence. Related follow-up (not urgent, logged for future reference): worth a deliberate comparison of MemPalace's actual feature set and reliability against open-source alternatives (e.g. mcp-memory-service/doobidoo -- SQLite-based, no embeddings, positioned for reliability via simplicity; Cognee -- graph+vector, native Claude Code plugin, more complete but more moving parts; mem0 self-hosted; Graphiti/Neo4j-backed options for more complex needs) before deciding whether to keep, fix, or replace MemPalace. Not a recommendation to switch -- a note that this comparison hasn't been done and should happen before any replacement decision, given the specific failure mode here is silent non-persistence on writes that report success, which argues for weighing simplicity/reliability as its own axis, not just feature completeness |
| DOL liquidated-damages multiplier correction -- RESOLVED (self-correction, same session) | 3 | Closed -- corrected before this session's work is committed | N/A | The DOL mechanism-caveat fix committed earlier this session (research/seven-experiments/experiment-2-employment-litigation-taxonomy.html, 4 spots) stated the litigation-path liquidated-damages multiplier as a range ("3-4x" in one spot, "2-4x" in another) without independent verification at the time. Confirmed via multiple independent legal sources during this session's Legal/Compliance Addendum 2 work: the federal FLSA liquidated-damages standard is a flat 2x (back wages plus an equal amount, "double damages") -- there is no federal 3x or 4x tier. A small number of states (Massachusetts confirmed) separately permit treble (3x) damages under state wage law, a distinct legal avenue, not an extension of the federal multiplier. This corrects content committed earlier this SAME session, not a legacy error carried forward from a prior one. Direct re-check also found Addendum 2's own framing ("all 4 spots need '2-4x' corrected") was not quite right: only 2 of the 4 originally-fixed spots (lines 643 and 1018) actually contained multiplier language -- the other 2 (626, the DOL Recovery data label; 1124, the closing findings sentence) never stated a multiplier and needed no further correction, confirmed by direct re-check of the live file rather than assumed from the addendum's own count. | This session (Claude Code) | Closed -- no further check-in |''',
)


def apply(dry_run: bool) -> int:
    changed = 0
    addendum2_text = ADDENDUM2_CONTENT_PATH.read_text(encoding="utf-8").rstrip("\n")
    addendum2_nested = addendum2_text.replace(
        "# Addendum 2 — Cluster 2 Two-Tier Restructure, Cluster 3 Sourced Formula, DOL Multiplier Correction",
        "## Addendum 2 — Cluster 2 Two-Tier Restructure, Cluster 3 Sourced Formula, DOL Multiplier Correction",
        1,
    ).replace("\n## ", "\n### ")

    for rel_path, old, new in EDITS:
        if "__ADDENDUM2_PLACEHOLDER__" in new:
            new = new.replace("__ADDENDUM2_PLACEHOLDER__", addendum2_nested)
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
