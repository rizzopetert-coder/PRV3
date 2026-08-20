"""
Add the full 11-cluster characterization pass to
prompts/scd-wcs-cluster-map-findings.md -- characterization-only result,
no code touched, no numbers proposed. Covers the 8 remaining clusters
(ranks 1,2,3,4,5,6,10,11), reconciled against the 3 already-piloted/
checked clusters (7,8,9) in one consolidated table, plus the separately
flagged invisible_performance_management finding (pure vector-strength
dominance, not a tie/cluster question).

Usage:
    python patch_scdwcs_findings_full_characterization.py --dry-run
    python patch_scdwcs_findings_full_characterization.py --write
"""
import argparse
import difflib
from pathlib import Path

DOC_PATH = Path("prompts/scd-wcs-cluster-map-findings.md")

OLD_TAIL = (
    "**What this means for sequencing:** `built_to_fail`'s dominance is not a\n"
    "tie artifact this or any other salience pilot can resolve. It's the\n"
    "**first concrete, evidence-backed candidate in the whole SCD-WCS\n"
    "investigation for the `dimensional_vector` re-authoring layer** —\n"
    "pointing at a *specific* state as high-value for that work, rather than\n"
    "treating the remaining 43+ states needing vector re-authoring as an\n"
    "undifferentiated backlog. Not scoped or actioned here — Pete's call on\n"
    "if/when the vector re-authoring layer opens, and whether `built_to_fail`\n"
    "leads it.\n"
    "\n"
    "## Cross-references\n"
)
NEW_TAIL = (
    "**What this means for sequencing:** `built_to_fail`'s dominance is not a\n"
    "tie artifact this or any other salience pilot can resolve. It's the\n"
    "**first concrete, evidence-backed candidate in the whole SCD-WCS\n"
    "investigation for the `dimensional_vector` re-authoring layer** —\n"
    "pointing at a *specific* state as high-value for that work, rather than\n"
    "treating the remaining 43+ states needing vector re-authoring as an\n"
    "undifferentiated backlog. Not scoped or actioned here — Pete's call on\n"
    "if/when the vector re-authoring layer opens, and whether `built_to_fail`\n"
    "leads it.\n"
    "\n"
    "## Full cluster characterization — all 11 clusters\n"
    "\n"
    "**Characterization-only, 2026-08-20. No code touched, no weight numbers\n"
    "proposed anywhere in this section.** Same verification depth as the\n"
    "rank-8/rank-9 checks (live `SALIENCE_PROFILES`, live `descriptive_prose`\n"
    "for every state, `dimensional_vector` confirmation, `resolution_family`\n"
    "per state), applied to the 8 remaining clusters (ranks 1, 2, 3, 4, 5, 6,\n"
    "10, 11) and reconciled against the 3 already-piloted/checked clusters\n"
    "(7, 8, 9) in one table. This is input for a sequencing decision, not a\n"
    "further pilot commitment.\n"
    "\n"
    "| Rank | Size | Tie status | Stakes (`resolution_family` match) | Narrative-splittable? | Dominance (false rank-1) |\n"
    "|---|---|---|---|---|---|\n"
    "| 1 | 11 | Full uniform tie | **High** — 5 distinct family combos across the 11 states | **Yes** — 11 genuinely distinct mechanisms (diversity ceiling, broken promises, hidden burnout, low-performance norm, favoritism, no institutional learning, misaligned incentives, execution-courage gap, AI/automation anxiety, reward-system collapse, unstated-overtime/legal exposure) | None — 0/175 for all 11 |\n"
    "| 2 | 10 | Full uniform tie | **High** — Intervention-only vs. Roadmap-only vs. several mixed combos | **Yes** — 10 distinct mechanisms | **`the_uninitiated`: 22/175 (12.6%)** — second-strongest dominance signal found this session |\n"
    "| 3 | 8 | Full uniform tie | **Mostly low** — 7/8 share \"Intervention + Executive Counsel\" exactly; `the_unsolved_problem` alone differs (\"Intervention + Roadmap\") | **Partial** — 4 states (`the_exposed`, `hr_capture`, `heard_and_ignored`, `the_tolerated_violation`) share a real family resemblance (\"the correction mechanism doesn't act\"); `the_founders_grip` (bottleneck) and `sequential_decision_blindness`/`disparate_impact_architecture` (aggregate/statistical pattern, no bad actor) are genuinely different in kind | None |\n"
    "| 4 | 6 (1 already split: `what_nobody_says`) | 5-way tie remains among the other 5 | **Partial** — 3/5 share \"Intervention\"; `narrative_lock` and `the_unlocked_door` differ | **Yes** for the remaining 5 — distinct (self-narrative rigidity vs. safety-reporting culture vs. neglected security practice, etc.) | `identity_erosion`: 1/175 (minimal) |\n"
    "| 5 | 3 | Full uniform tie | **Partial** — `invisible_influence_architecture` + `planning_authority_gap` share a family; `paper_shield` differs | **Yes** — `paper_shield` (untested plans) is a different failure kind from the other two (informal-power/formal-authority mismatch) | `paper_shield`: 1/175 (minimal) |\n"
    "| 6 | 3 | Full uniform tie | **High** — all 3 states have *different* `resolution_family`, no two match | **Yes** — 3 distinct mechanisms | **`the_second_close`: 5/175 (2.9%)** — real, smaller-scale dominance |\n"
    "| 7 *(piloted)* | 2 | Resolved, commit 043b8ad | — | `the_unformed_leader`/`the_dormant_talent`, aptitude/attitude split landed; narrative compromise (aptitude stayed dominant on both, not the attitude-dominant read the text argued for) | Residual: `the_unformed_leader` 8/175, `the_dormant_talent` 6/175 — unrelated to the tie itself |\n"
    "| 8 *(piloted)* | 2 | Resolved, commit 58a19a0 | Real — differing families (Roadmap+Intervention vs. Development+Roadmap) | `built_to_fail`=structural/resourcing, `the_paper_tiger`=documentation/accountability, real split | **`built_to_fail`: 49/175 (28%)** — largest dominance signal among any tied-cluster state, structurally unresolvable via salience alone (see Pilot result above) |\n"
    "| 9 *(checked)* | 2 | Confirmed tie, not pursued | Low/cosmetic — same `resolution_family` | **No** — text doesn't support the tested hypothesis; tie reads accurately authored | None |\n"
    "| 10 | 2 | **Already differentiated** (`the_untouchable` custom salience, `the_inner_circle` uniform default) | **Low in substance** — same two families, reordered strings (\"Executive Counsel + Intervention\" vs. \"Intervention + Executive Counsel\") | **Yes** — individual exemption vs. systemic clique; the existing differentiation is well-grounded, self-validating precedent | None — 0/175 for both |\n"
    "| 11 | 2 | Full uniform tie | **Low** — both \"Intervention\" | **Yes** — gradual value drift vs. performative wellness programs, real distinction despite low stakes | **`culture_drift`: 5/175 (2.9%)** — real dominance despite low tie-stakes |\n"
    "\n"
    "### Sequencing read (analysis, not a decision)\n"
    "\n"
    "- **Rank 1 and rank 2** are large (10-11 states each), high-stakes\n"
    "  (real `resolution_family` spread), and narratively real (every member\n"
    "  reads as a genuinely distinct mechanism) — but that scale puts them\n"
    "  closer to the full `dimensional_vector` re-authoring project than to a\n"
    "  quick 2-3-state pilot. An 11-way or 10-way differentiation is a\n"
    "  different kind of undertaking than what ranks 7/8/9 tested.\n"
    "- **Rank 6 and rank 5** read as the cleanest remaining small-pilot\n"
    "  candidates if that path continues — rank 6 has the cleanest possible\n"
    "  stakes signal (all 3 states carry a different `resolution_family`,\n"
    "  no two match) with a real, if modest, dominance finding\n"
    "  (`the_second_close`); rank 5 has partial stakes and a clean 1-vs-2\n"
    "  narrative split.\n"
    "- **Rank 3, rank 9, and rank 11** read as low-value/cosmetic — same\n"
    "  category as rank 9's already-logged finding (real ties, accurately\n"
    "  authored, low practical stakes). Not prioritized.\n"
    "- **Rank 4 and rank 10** are partially resolved already. Rank 10's\n"
    "  existing split is confirmed well-grounded (its own real narrative\n"
    "  distinction backs it up) — a validated precedent, not an open item.\n"
    "  Rank 4's remaining 5-way tie has real partial stakes and real\n"
    "  narrative distinction if it's ever prioritized, but `what_nobody_says`\n"
    "  is already correctly split out.\n"
    "\n"
    "## Separately flagged — pure vector-strength dominance (not a tie or cluster question)\n"
    "\n"
    "**A structurally different kind of finding from everything else in this\n"
    "document.** Surfaced as a side effect of the dominance check applied to\n"
    "the 11 clusters, but these three states have **no cluster-mate to\n"
    "characterize against and no tie to break** — they have genuinely unique\n"
    "`dimensional_vector`s (confirmed in the original cluster map, \"The 7\n"
    "states with genuinely unique vectors\" above) and win false rank-1 purely\n"
    "on raw vector alignment against unrelated profiles, not shared-vector\n"
    "confusion:\n"
    "\n"
    "| State | False rank-1 | True rank-1 |\n"
    "|---|---|---|\n"
    "| `invisible_performance_management` | **59/175 (33.7%)** | **0** |\n"
    "| `the_unexamined_algorithm` | 11/175 (6.3%) | 0 |\n"
    "| `the_overloaded_manager` | 4/175 (2.3%) | 0 |\n"
    "\n"
    "`invisible_performance_management` is **the single largest dominance\n"
    "problem in the entire taxonomy** — larger than `built_to_fail`'s 28%,\n"
    "and it has never once been the genuinely correct rank-1 answer across\n"
    "all 175 profiles. No salience or tie remediation touches this class of\n"
    "problem at all — there is no cluster-mate to differentiate against, and\n"
    "no shared-vector confusion to resolve. This needs its own future\n"
    "investigation, independent of the cluster/tie remediation track this\n"
    "whole document has been about. Not scoped or actioned here.\n"
    "\n"
    "## Cross-references\n"
)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = DOC_PATH.read_text(encoding="utf-8")

    count = text.count(OLD_TAIL)
    if count != 1:
        raise SystemExit(f"ABORT: expected exactly 1 match, found {count}")
    text = text.replace(OLD_TAIL, NEW_TAIL, 1)

    if args.dry_run:
        original = DOC_PATH.read_text(encoding="utf-8")
        print(f"\n{'=' * 80}\nDIFF: {DOC_PATH}\n{'=' * 80}")
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            text.splitlines(keepends=True),
            fromfile=f"{DOC_PATH} (before)",
            tofile=f"{DOC_PATH} (after)",
        )
        print("".join(diff))
        print("\nDry run complete. No files written. Re-run with --write to apply.")
    else:
        DOC_PATH.write_text(text, encoding="utf-8")
        print(f"WROTE: {DOC_PATH}")


if __name__ == "__main__":
    main()
