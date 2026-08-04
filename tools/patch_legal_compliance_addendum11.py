"""
PRV3 -- Append Addendum 11 to prompts/friction-tax-legal-compliance-
methodology.md: closes the output-integration relay gap (the abbreviated
"boundaries already given" reference CC correctly refused to act on).
Full spec for legal_tail_risk_exposure (private_output) and
legal_tail_risk_band (shareable output), plus two pre-existing findings
(friction_tax_estimate hardcoded null in the shareable path;
ShareableOutputPayload assembled in TypeScript, not Python) and three
open questions CC is holding on pending Pete's resolution -- no
implementation in this patch, documentation only.

Usage:
  python tools/patch_legal_compliance_addendum11.py --dry-run
  python tools/patch_legal_compliance_addendum11.py --write
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
    "explicitly excluded. **Addendum 10 locks the score-interpolation formula (Clusters 1, 4a,\n"
    "4b, 5) and Cluster 3's scope percentages** -- the last open design questions blocking\n"
    "implementation. Full five-cluster implementation (classification tables,\n"
    "INDUSTRY_NON_EXEMPT_RATIO, dollar curves, cross-state aggregation) proceeding now.",
    "explicitly excluded. **Addendum 10 locks the score-interpolation formula (Clusters 1, 4a,\n"
    "4b, 5) and Cluster 3's scope percentages** -- the last open design questions blocking\n"
    "implementation. Full five-cluster implementation (classification tables,\n"
    "INDUSTRY_NON_EXEMPT_RATIO, dollar curves, cross-state aggregation) is DONE and committed\n"
    "(compute_legal_compliance_exposure(), LegalPricingStatus). **Addendum 11 specifies output\n"
    "integration** (legal_tail_risk_exposure in private_output, legal_tail_risk_band in the\n"
    "shareable output) and flags two pre-existing gaps found along the way -- NOT yet\n"
    "implemented, three open questions held for Pete's resolution.",
)

# ---------------------------------------------------------------------
# 2. Append Addendum 11
# ---------------------------------------------------------------------

ADDENDUM_11 = '''## Addendum 11 — Output Integration: Full Spec, and Two Pre-Existing Gaps

**Status:** Closes a relay gap, not a fabrication -- this design was genuinely decided in
conversation with Pete but abbreviated when first relayed to Claude Code ("the boundaries
already given"), which CC correctly could not act on since it only sees what's explicitly
provided. Full spec below. Also documents two real findings from CC's investigation of the
actual current codebase, both pre-existing and unrelated to Legal/Compliance specifically.
NOT yet implemented -- three open questions below held for Pete's resolution.

### Private output: legal_tail_risk_exposure

Added to private_output in engine/contract.py's assemble_output(), alongside the existing
friction_tax_estimate:

    "legal_tail_risk_exposure": (
        {
            "low": legal_result["low"],
            "high": legal_result["high"],
            "currency": legal_result["currency"],
            "caveat": LEGAL_TAIL_RISK_CAVEAT_TEXT,
            "has_unpriced_conditions": legal_result["has_unpriced_conditions"],
        }
        if legal_result["low"] is not None or legal_result["has_unpriced_conditions"]
        else None
    )

Caveat text, module-level constant:

    LEGAL_TAIL_RISK_CAVEAT_TEXT = (
        "This estimate reflects contingent exposure -- a range of what could be at "
        "stake if this pattern were ever formally challenged, not a prediction that "
        "it will be. Most organizations carrying a similar pattern never face an "
        "actual claim. This figure combines identified conditions across legal and "
        "regulatory categories, using publicly available case outcomes, agency "
        "enforcement data, and statutory penalty schedules as reference points -- "
        "not a legal opinion, and not specific to your organization's actual risk "
        "of being challenged. If any of these conditions concern you, this is worth "
        "a conversation with employment counsel, not just this number."
    )

### Shareable output: legal_tail_risk_band

Qualitative severity band, no dollar figure -- decided explicitly this way over "rounded
range" or "full numbers with caveat" after flagging a real liability concern: a specific
dollar figure in a publicly shareable artifact could function as documented notice of a
contingent liability, discoverable in future litigation. Boundaries (first pass, not yet
stress-tested against real multi-cluster worked examples -- flagged as needing the same
plausibility check as everything else in this design once real output is available):

    Under $100K   -> "Minor"
    $100K-$500K   -> "Moderate"
    $500K-$2M     -> "Elevated"
    $2M+          -> "Significant"

Non-null only when legal_result["low"] is not None -- does not fire for
has_unpriced_conditions-only cases, since there's no dollar figure to band.

### Finding 1: friction_tax_estimate is hardcoded null in the shareable path, pre-existing

web/app/api/share/create/route.ts currently sets friction_tax_estimate: null
unconditionally, never reading engineResult's actual computed value. The inline comment
("null in Path B (CALIBRATION TARGET)") is stale -- predates Option A's calibration
completion, same staleness pattern already caught multiple times this session (the OD-07
MOB row, the FrictionTaxEstimate types.ts comment, the DOL figures in E2). This is a
real, separate bug, not something Legal/Compliance introduced -- worth fixing alongside
this work since it's the same code path, but tracked as its own fix.

### Finding 2: shareable output assembly lives in TypeScript, not Python

ShareableOutputPayload is NOT assembled in engine/contract.py the way private_output is.
It's built in web/app/api/share/create/route.ts, directly from invokeEngine()'s result.
This means legal_tail_risk_band cannot simply be a Python-side dict key alongside
private_output the way legal_tail_risk_exposure is -- the band computation needs to
either happen in Python and be exposed through whatever engineResult already carries
across that boundary, or be computed in route.ts itself from the raw low/high numbers.
Real cross-language plumbing question, not decided here -- needs scoping before CC builds
against it.

### Open, needs resolution before implementation

1. Where should _legal_exposure_band() actually live -- Python (engine/friction_tax.py,
   exposed through whatever engineResult already surfaces) or TypeScript (route.ts,
   computed from raw numbers already available there)? This determines whether
   compute_legal_compliance_exposure() itself should optionally return a band, or whether
   band logic stays entirely out of the Python engine.
2. Should Finding 1 (the hardcoded null) be fixed in the same commit as this integration,
   or tracked and fixed separately? They touch the same file and the same underlying gap
   (friction tax data not reaching the shareable path), but are logically distinct bugs.
3. The band boundaries need the same plausibility check as everything else in this
   session -- run real worked multi-cluster examples through them once
   compute_legal_compliance_exposure() has real test data to check against, before
   treating $100K/$500K/$2M as final.

## Structural implications (bigger than Option A)'''

edit(
    DOC,
    "actual decision down in full, with sourced content (the formula's dollar anchors,\n"
    "INDUSTRY_NON_EXEMPT_RATIO) explicitly distinguished from design judgment (Cluster 3's\n"
    "percentages, the 4b 100-249 midpoint convention), so this doesn't have to be reconstructed from\n"
    "memory again.\n"
    "\n"
    "## Structural implications (bigger than Option A)",
    "actual decision down in full, with sourced content (the formula's dollar anchors,\n"
    "INDUSTRY_NON_EXEMPT_RATIO) explicitly distinguished from design judgment (Cluster 3's\n"
    "percentages, the 4b 100-249 midpoint convention), so this doesn't have to be reconstructed from\n"
    "memory again.\n"
    "\n"
    + ADDENDUM_11,
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
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
