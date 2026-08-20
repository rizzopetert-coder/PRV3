"""
Add the rank-8 pilot result (built_to_fail/the_paper_tiger, commit
58a19a0) to prompts/scd-wcs-cluster-map-findings.md. Framed as two
explicitly separate parts per Pete's instruction, not collapsed into one
result: (1) the tie-break itself, mechanically identical in kind to
rank-7's success; (2) the dominance finding -- built_to_fail's 28%
false-rank-1 rate is a taxonomy-wide pattern, not a tie artifact, and
this pilot's real significance is reframing built_to_fail specifically
as the first evidence-backed candidate for the dimensional_vector
re-authoring layer.

Usage:
    python patch_scdwcs_findings_rank8_pilot.py --dry-run
    python patch_scdwcs_findings_rank8_pilot.py --write
"""
import argparse
import difflib
from pathlib import Path

DOC_PATH = Path("prompts/scd-wcs-cluster-map-findings.md")

OLD_TAIL = (
    "**Logged as:** a real tie, accurately authored given the available\n"
    "textual grounding, low practical/product stakes — not prioritized for\n"
    "further pursuit. Not a candidate for a salience or vector remediation\n"
    "pass unless the underlying descriptive_prose for one of these two states\n"
    "changes.\n"
    "\n"
    "## Cross-references\n"
)
NEW_TAIL = (
    "**Logged as:** a real tie, accurately authored given the available\n"
    "textual grounding, low practical/product stakes — not prioritized for\n"
    "further pursuit. Not a candidate for a salience or vector remediation\n"
    "pass unless the underlying descriptive_prose for one of these two states\n"
    "changes.\n"
    "\n"
    "## Pilot result — rank-8 cluster (`built_to_fail` / `the_paper_tiger`)\n"
    "\n"
    "Third pilot for this investigation. Commit `58a19a0`, 2026-08-20. Two\n"
    "explicitly separate parts — the tie-break succeeded mechanically; the\n"
    "pilot's real significance is a taxonomy-wide finding it surfaced, not\n"
    "the tie-break itself.\n"
    "\n"
    "### Part 1 — the tie-break: real, safe, same kind of success as rank-7\n"
    "\n"
    "`SALIENCE_PROFILES` confirmed byte-identical for both states before this\n"
    "change (APTITUDE — HIGH tier), `dimensional_vector` confirmed identical —\n"
    "combined, a guaranteed exact-tie score, 175/175 calibration profiles tied.\n"
    "\n"
    "`built_to_fail`'s salience is unchanged — approved as-is, clean\n"
    "aptitude-dominant read. `the_paper_tiger` differentiated on two axes per\n"
    "its real `descriptive_prose`: aptitude reduced (not a skill/resourcing\n"
    "story), authority raised (a structural gap — no one held responsible for\n"
    "keeping documentation current — the same magnitude class as\n"
    "`the_suppression_filter`'s own Authority secondary, real precedent, not\n"
    "invented), attitude raised (operational avoidance — *\"managed\n"
    "verbally... discovers the record doesn't match reality\"*). alliance\n"
    "untouched on both — no textual basis to move it. `dimensional_vector`\n"
    "deliberately untouched — salience-only, by design.\n"
    "\n"
    "4 candidates searched against the real calibration pipeline (aptitude\n"
    "1.0–2.0, authority 1.0–1.2, attitude 1.3–1.5), all passed identically\n"
    "clean. Landed on aptitude=1.0/authority=1.0/attitude=1.5 — best\n"
    "worst-case gap floor (min 0.0195, also best max 0.254) among candidates\n"
    "tested, no further search needed given every candidate passed cleanly.\n"
    "\n"
    "**Mechanically validated, same four checks as rank-7:**\n"
    "- Tie fully broken: 175/175 tied before → 0/175 after.\n"
    "- Zero cross-contamination: full 58-state × 175-profile comparison.\n"
    "  (One methodology note for the record: the first verification pass\n"
    "  showed 350 apparent contamination hits — a stale-baseline bug on this\n"
    "  session's own end, comparing against a snapshot predating the\n"
    "  already-committed rank-7 change. Regenerated a correct current-HEAD\n"
    "  baseline and re-ran; zero once compared correctly.)\n"
    "- Full regression exactly at the 171/175 baseline — same 4 pre-existing\n"
    "  failures, nothing new, confirmed across all 4 candidates tested, not\n"
    "  just the landed one.\n"
    "- Real margin: `built_to_fail`'s own 3 profiles stay at a perfect 0.0000\n"
    "  self-match, entirely unaffected (its salience never changed).\n"
    "  `the_paper_tiger`'s 4 profiles pass with a 0.077–0.143 gap to rank-1 —\n"
    "  well inside the pass window, not a bare clear.\n"
    "\n"
    "### Part 2 — the dominance finding: this pilot's actually significant result\n"
    "\n"
    "This cluster was chosen because `built_to_fail` wins a false rank-1 in\n"
    "**49 of 175 calibration profiles (28%)** — quantified directly from the\n"
    "full-suite snapshot, not estimated. Only 3 of its 52 total rank-1 wins are\n"
    "genuinely correct.\n"
    "\n"
    "**That rate does not move, at any tested magnitude.** Confirmed\n"
    "empirically across all 4 candidates (a wide spread — aptitude 1.0 to 2.0,\n"
    "more than double) — `btf_false_rank1` sat at exactly 49/175 every single\n"
    "time. Traced to why, not just observed: `built_to_fail` and\n"
    "`the_paper_tiger` share an identical `dimensional_vector`, and\n"
    "`built_to_fail`'s own aptitude weight (its only real vector signal) stays\n"
    "fixed at 2.5. No `the_paper_tiger`-only salience reweighting can out-score\n"
    "a fixed, full-weighted identical vector on `the_paper_tiger`'s own\n"
    "aptitude-flavored calibration profiles (`APT-PT-00/01/02/03`) — confirmed\n"
    "directly: `built_to_fail` wins those 4 by a consistent gap in every\n"
    "candidate tested. This is a mechanical ceiling, not a search-tuning\n"
    "problem.\n"
    "\n"
    "**Of the 49 false-rank-1 profiles, only 4 belong to `the_paper_tiger`. The\n"
    "other 45 are unrelated states entirely** — states that share no vector\n"
    "with `built_to_fail` at all. This pilot's scope (one paired state) never\n"
    "touches them, by design, same as rank-7 and rank-9's scope discipline.\n"
    "\n"
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
