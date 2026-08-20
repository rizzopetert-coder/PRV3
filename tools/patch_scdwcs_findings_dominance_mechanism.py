"""
Add the cross-cutting dominance-mechanism investigation (7 states, not
per-state) and a two-track sequencing synthesis to
prompts/scd-wcs-cluster-map-findings.md. Diagnostic only -- no code
touched, no weight numbers proposed. The synthesis is explicitly framed
as a recommendation for Pete's decision, not a decision already made.

Usage:
    python patch_scdwcs_findings_dominance_mechanism.py --dry-run
    python patch_scdwcs_findings_dominance_mechanism.py --write
"""
import argparse
import difflib
from pathlib import Path

DOC_PATH = Path("prompts/scd-wcs-cluster-map-findings.md")

OLD_TAIL = (
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
NEW_TAIL = (
    "`invisible_performance_management` is **the single largest dominance\n"
    "problem in the entire taxonomy** — larger than `built_to_fail`'s 28%,\n"
    "and it has never once been the genuinely correct rank-1 answer across\n"
    "all 175 profiles. No salience or tie remediation touches this class of\n"
    "problem at all — there is no cluster-mate to differentiate against, and\n"
    "no shared-vector confusion to resolve. This needs its own future\n"
    "investigation, independent of the cluster/tie remediation track this\n"
    "whole document has been about. Not scoped or actioned here.\n"
    "\n"
    "## Dominance-mechanism investigation — cross-cutting, not per-state\n"
    "\n"
    "**Diagnostic only, 2026-08-20. No code touched, no weight numbers\n"
    "proposed.** Seven states flagged this session with meaningful\n"
    "false-rank-1 dominance, spanning both tied clusters and\n"
    "genuinely-unique vectors, examined together rather than one at a time:\n"
    "`built_to_fail` (28%), `invisible_performance_management` (33.7%),\n"
    "`the_uninitiated` (12.6%), `the_unexamined_algorithm` (6.3%),\n"
    "`the_second_close` (2.9%), `culture_drift` (2.9%),\n"
    "`the_overloaded_manager` (2.3%). For each: `dimensional_vector`\n"
    "magnitude/concentration on its dominant field, `SALIENCE_PROFILES`\n"
    "entry (presence and magnitude), and — pulled directly, not\n"
    "inferred — every profile ID it steals rank-1 from and that profile's\n"
    "true target's own dominant vector field.\n"
    "\n"
    "| State | Dominance | Vector dominant field (magnitude) | Vector concentration (dom/total) | Salience | Theft pattern |\n"
    "|---|---|---|---|---|---|\n"
    "| `invisible_performance_management` | **33.7%** | aptitude, 0.45 | 0.290 | Custom, sharp: aptitude=2.5, rest 0.4 | **Broad, cross-dimensional** — steals from Alliance-, Aptitude-, Attitude-, and Authority-dominant targets alike |\n"
    "| `built_to_fail` | **28.0%** | aptitude, 0.60 (highest raw magnitude of the 7) | 0.462 (sharpest/most peaked) | Custom, sharp: aptitude=2.5, rest 0.4 | **Broad, cross-dimensional** — all 4 target dimensions represented among its 49 stolen profiles |\n"
    "| `the_uninitiated` | 12.6% | authority, 0.45 | 0.300 | Custom, sharp: authority=2.5, rest 0.4 | **Narrow, same-dimension** — 20 of 22 stolen targets are authority-dominant |\n"
    "| `the_unexamined_algorithm` | 6.3% | authority, 0.50 | 0.345 | Custom: authority=2.5, aptitude=1.0 secondary, rest 0.4 | **Narrow, same-dimension** — 10 of 11 stolen targets are authority-dominant |\n"
    "| `the_second_close` | 2.9% | alliance, 0.45 | 0.300 | Custom, sharp: alliance=2.5, rest 0.4 | **Narrow, same-dimension** — all 5 stolen targets are alliance-dominant |\n"
    "| `culture_drift` | 2.9% | attitude, 0.35 | 0.233 | Custom: attitude=2.5, authority=1.0 secondary, rest 0.4 | **Narrow, same-dimension** — all 5 stolen targets are attitude-dominant |\n"
    "| `the_overloaded_manager` | 2.3% | aptitude, 0.35 | 0.233 | Custom: aptitude=2.5, authority=1.0 secondary, rest 0.4 | **Anomalous** — all 4 stolen targets are attitude-dominant, not aptitude (its own dimension) or authority (its secondary) |\n"
    "\n"
    "### Three direct findings\n"
    "\n"
    "**(a) Salience presence/magnitude does not correlate with dominance —\n"
    "it's a constant across all 7, not a variable.** Every one of the 7 has a\n"
    "custom, sharply-weighted salience entry (2.5 on its dominant field),\n"
    "from the biggest dominator (33.7%) to the smallest (2.3%). This falsifies\n"
    "the \"lacking a custom entry = generalist attractor\" hypothesis outright\n"
    "— nothing in this set lacks an entry.\n"
    "\n"
    "**(b) Vector magnitude/concentration on the dominant field does not\n"
    "correlate with dominance magnitude, and not even in a consistent\n"
    "direction.** `invisible_performance_management` has the *lowest*\n"
    "concentration (0.290) of the top two dominators yet wins the most\n"
    "(33.7%); `built_to_fail` has the *highest* concentration of all 7\n"
    "(0.462, a sharp single-spike vector) and wins second-most.\n"
    "`the_unexamined_algorithm` has higher raw magnitude (0.50) than\n"
    "`the_uninitiated` (0.45) but roughly half its dominance (6.3% vs.\n"
    "12.6%). No single metric here predicts dominance magnitude\n"
    "monotonically.\n"
    "\n"
    "**(c) The aptitude-signal-correlation hypothesis specifically checked\n"
    "against `built_to_fail` does NOT hold — confirmed directly, not\n"
    "assumed.** `built_to_fail`'s 49 stolen profiles span all four\n"
    "dimensions in roughly even measure (Alliance, Aptitude, Attitude, and\n"
    "Authority targets all represented), not concentrated on\n"
    "aptitude-flavored targets. What the theft data actually shows instead\n"
    "is a **magnitude-of-dominance split**: the two biggest dominators\n"
    "(`invisible_performance_management`, `built_to_fail`, both >25%) steal\n"
    "broadly across all four dimensions; four of the remaining five\n"
    "(`the_uninitiated`, `the_unexamined_algorithm`, `the_second_close`,\n"
    "`culture_drift`) steal almost exclusively from targets sharing their\n"
    "*own* dominant dimension — a narrow same-dimension \"neighbor\" effect,\n"
    "structurally different from a broad attractor effect.\n"
    "\n"
    "### Genuine anomaly, logged as open rather than forced into a pattern\n"
    "\n"
    "`the_overloaded_manager` fits neither pattern. It's aptitude-dominant\n"
    "with an authority secondary, but all 4 profiles it steals are\n"
    "attitude-dominant — a dimension where it has no elevated presence in\n"
    "either vector or salience. Checked one case directly (`ATT-IT-02`'s\n"
    "`dimension_summary`: authority 0.44, attitude 0.40, alliance 0.25,\n"
    "aptitude 0.15 — aptitude is actually the *lowest* of the four, not\n"
    "elevated); it doesn't explain the win either. Small sample (n=4) —\n"
    "flagged for more data before any theory is trusted, not resolved here.\n"
    "\n"
    "## Sequencing synthesis — two-track recommendation (Pete's call, not decided here)\n"
    "\n"
    "**A proposal for Pete's decision, drawn directly from the theft-pattern\n"
    "split above — not a decision already made, and nothing here has been\n"
    "built.** The broad-vs-narrow theft distinction maps onto two\n"
    "structurally different remediation problems that likely need different\n"
    "handling.\n"
    "\n"
    "**Track 1 — narrow neighbor-stealers.** `the_uninitiated`,\n"
    "`the_unexamined_algorithm`, `the_second_close`, `culture_drift`, and by\n"
    "extension any other state found later with the same narrow,\n"
    "same-dimension theft signature. Salience-only differentiation is a\n"
    "*plausible* fix for this shape of problem — structurally similar to\n"
    "rank-7's confirmed success (`the_unformed_leader`/`the_dormant_talent`,\n"
    "also a narrow within-cluster tie, resolved via salience alone without\n"
    "touching `dimensional_vector`). Candidate for continued pilot-style\n"
    "remediation, cluster by cluster, same process as rank-7/8/9 — dry-run,\n"
    "search against the real calibration suite, full verification, Pete\n"
    "confirms before commit.\n"
    "\n"
    "**Track 2 — broad cross-dimensional attractors.**\n"
    "`invisible_performance_management` and `built_to_fail`. Confirmed NOT\n"
    "fixable via salience alone — direct evidence from rank-8's actual pilot\n"
    "(searched 4 magnitudes spanning a wide range, `built_to_fail`'s false\n"
    "rank-1 rate never moved), now reinforced by this session's broader\n"
    "theft-pattern data showing the dominance isn't concentrated on any one\n"
    "paired opponent or dimension to reweight against. These need\n"
    "`dimensional_vector`-level attention — likely reducing peak\n"
    "concentration or reshaping the vector itself, not just reweighting a\n"
    "paired opponent, since there often isn't a single clean opponent to\n"
    "pair against (the theft is spread across many unrelated states). This\n"
    "is real clinical/taxonomic authoring work, comparable in kind to the\n"
    "still-undated `STATE_CAUSATION_OVERRIDES` item — the harder of the two\n"
    "tracks, and should be sequenced with that in mind rather than attempted\n"
    "piecemeal alongside Track 1's lighter-weight pilots.\n"
    "\n"
    "**`the_overloaded_manager`** sits outside both tracks — logged as an\n"
    "open, small-sample anomaly, not assigned to either track until more\n"
    "data (more theft profiles, or a deeper trace of the actual\n"
    "centroid-displaced accumulated_vector rather than the derived\n"
    "`dimension_summary`) clarifies what's actually happening.\n"
    "\n"
    "Not scoped or actioned here. Both tracks, their relative priority\n"
    "against each other and against `invisible_performance_management`'s\n"
    "own unscoped investigation, and whether Track 1 continues at all given\n"
    "rank-1/rank-2's scale (see \"Full cluster characterization\" above) are\n"
    "all Pete's call.\n"
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
