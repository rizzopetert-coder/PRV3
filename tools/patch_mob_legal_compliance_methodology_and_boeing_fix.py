"""
PRV3 MOB update -- Legal/Compliance tail-risk methodology doc committed +
Priority Queue item 3 replaced + Boeing/Allstate open-item row corrected.

Updates tools/_mob.txt:
  - Version bump v4.76 -> v4.77 (new design-direction doc + factual
    correction to a live tracked row + Priority Queue reorder)
  - Section 13b: Priority Queue item 3 replaced -- was a stub referencing
    the old Decision Register entry, now reflects the mechanism-aware
    design direction locked this session in
    prompts/friction-tax-legal-compliance-methodology.md
  - Section 13 (general Open Items): Boeing/Allstate row corrected --
    this session's direct grep confirmed experiment-2-employment-
    litigation-taxonomy.html has been clean since commit c8e3c6c
    (2026-07-06), contradicting the S71 entry that reported it as still
    broken. Historical Section 14/16 narrative entries left untouched
    (append-only history), only the live-tracked row is corrected.

New file: prompts/friction-tax-legal-compliance-methodology.md (written
separately via the Write tool, not by this script -- mojibake from the
source paste corrected byte-by-byte before writing).

Usage:
  python tools/patch_mob_legal_compliance_methodology_and_boeing_fix.py --dry-run
  python tools/patch_mob_legal_compliance_methodology_and_boeing_fix.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================
# tools/_mob.txt
# ============================================================

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.76",
    "\\\\\\#\\\\\\# MOB v4.77",
)

# Section 13b -- Priority Queue item 3 replacement
edit(
    "tools/_mob.txt",
    '3. Legal/Compliance actuarial tail-risk distinction (Decision Register item, explicitly queued behind #1) -- whether Legal/Compliance needs separate tail-risk treatment rather than blending into the same 0-2 scale as the other three criteria.',
    '3. Legal/Compliance tail-risk methodology -- mechanism-aware design in progress, see prompts/friction-tax-legal-compliance-methodology.md. Next concrete step: classify which of the 57 states carry a Legal score and which mechanism bucket each represents (individual claim / class-discrimination / wage-hour / whistleblower) -- real taxonomy work, not started.',
)

# Section 13 (general Open Items) -- Boeing/Allstate row corrected
edit(
    "tools/_mob.txt",
    '| Boeing/Allstate citations — CONFIRMED PROBLEMATIC (S71) | Closed with a finding, not a clean bill. Scope was narrower than the original S58 coherence-check framing — the confirmed problem is in experiment-2-employment-litigation-taxonomy.html\'s disparate_impact_architecture financial-consequence sourcing, not the general E2 prose Session 58 already fixed. Allstate cited there as "$17.5M race discrimination" — the only verifiable EEOC Allstate settlement is $4.5M age discrimination (2009): wrong amount, wrong claim type, no matching case found for the cited figure. Boeing cited as "$38M age discrimination" — closest verifiable match is Beck v. Boeing, a $40.6M-$72.5M gender wage discrimination settlement: wrong claim type, wrong figure. Neither company name currently appears in taxonomy.ts (confirmed clean) — the bad citations are contained to the research layer and have not reached client-facing copy. Standing guidance going forward: do not cite Boeing or Allstate by name for disparate_impact_architecture. The verified EEOC FY2023 $513M aggregate recovery figure (corrected from FY2022 at S58) checks out independently and remains usable without naming specific companies. Full detail in Session 71 (continued) entry, Section 14. |',
    '| Boeing/Allstate citations — RESOLVED, S71 finding did not match committed file state (confirmed this session) | Direct grep of experiment-2-employment-litigation-taxonomy.html at current HEAD, plus its consolidation_source_corpus.json extraction, found zero occurrences of the figures S71 flagged as still broken ("$17.5M race discrimination" Allstate, "$38M age discrimination" Boeing) anywhere in the repository. The file has exactly one commit since its original recovery -- c8e3c6c (2026-07-06, "seven-experiment citation audit E2+E7, 8 errors corrected") -- which fixed Boeing to Beck v. Boeing and Allstate to Tilkey v. Allstate, and it has held in that corrected state continuously since, including through S71 (2026-07-23), which nonetheless reported the pre-fix figures as present. No commit lands between c8e3c6c and this session, so the S71 finding cannot be explained by a later regression -- it does not match what the file has contained at any point since July 6. Root cause of the S71 discrepancy (stale render, wrong artifact, misattribution) undetermined, not investigated further. The original S71 standing guidance (do not cite Boeing or Allstate by name for disparate_impact_architecture) is retained regardless -- neither name currently appears in taxonomy.ts or web/content/book, confirmed by direct search, and that guidance was never contingent on this file\'s state. DOL WHD figure ($274M) separately re-confirmed unchanged in this file and never corrected by c8e3c6c or any later commit -- not a new finding, matches citation-audit.md Section 1\'s own record, re-verified while investigating this row. |',
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
