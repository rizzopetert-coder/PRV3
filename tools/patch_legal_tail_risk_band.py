"""
PRV3 -- Implement legal_tail_risk_band per Addendum 11 + Gemini
structural review (2026-08-04). Verified against real files before
writing, per standing protocol:

- _legal_exposure_band() and its wiring into compute_legal_compliance_
  exposure()'s 3 return paths ALREADY EXIST (built in an earlier
  commit, 46c1e0c) -- confirmed via direct read, not re-added. Boundary
  inequalities confirmed correct by trace ($100K/$500K/$2M land in the
  band above them, matching "Under $X" wording), and both None-
  producing paths (0 legal-scoring states; Cluster 4c/Government-only)
  confirmed to actually produce low=None in the real code.
- Gemini's cited "_TOP_LEVEL_SCHEMA" IS a real constant (contract.py
  line 539) -- but it type-checks the *top-level* output keys
  (private_output itself as a dict), not private_output's own
  sub-fields. That's _PRIVATE_OUTPUT_FIELDS (line 586), already
  correctly identified and already updated for legal_tail_risk_exposure
  in an earlier commit. Flagging the mismatch rather than silently
  substituting, per standing practice. No schema constant needs
  touching for this patch either way -- legal_tail_risk_exposure has no
  nested per-field validator anywhere in contract.py (unlike
  asset_score, dimension_summary, etc.), so adding "band" inside it
  isn't a schema change.
- Gemini's cited "shareablePayload" IS the real variable name
  (route.ts line 221) -- confirmed, no mismatch.
- New gap, not in the original 5-point list: LegalTailRiskExposure
  (web/lib/types.ts) does not currently declare a "band" field --
  deliberately excluded in an earlier turn ("private output doesn't
  need it"). Adding "band" to the Python dict without adding it here
  too would mean route.ts can't read .band without a tsc error. Fixed
  by adding band: LegalTailRiskBand | null to the interface -- this
  propagates automatically to engine-client.ts's EngineResult.private_
  output, which already imports and reuses this same type, so no
  separate engine-client.ts edit is needed.
- Addenda 1 and 5 confirmed current (no renumbering since either was
  written) -- safe to cite in a permanent code comment.

Changes:
1. engine/friction_tax.py -- new architecture-note comment above
   compute_legal_compliance_exposure(), documenting deliberate
   headcount-independence and the extreme-tail behavior confirmed via
   a real worked-example plausibility pass, citing Addenda 1 and 5.
2. engine/contract.py -- "band": legal_result["band"] added to the
   existing legal_tail_risk_exposure dict construction. No schema
   constant changed.
3. web/lib/types.ts -- LegalTailRiskExposure gains band: LegalTailRiskBand
   | null; both interfaces' doc comments updated to reflect the
   now-complete private-to-shareable pipeline. ShareableOutputPayload's
   legal_tail_risk_band changes from optional to required (nullable) --
   route.ts now always populates it.
4. web/app/api/share/create/route.ts -- legal_tail_risk_band extracted
   from engineResult.private_output.legal_tail_risk_exposure?.band,
   null-safe.
5. tools/test_friction_tax.py -- new boundary-threshold test section
   for _legal_exposure_band() at all four cutoffs, confirming the real
   inequality direction (>= lands in the higher band, not the lower).

Usage:
  python tools/patch_legal_tail_risk_band.py --dry-run
  python tools/patch_legal_tail_risk_band.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


FT = "engine/friction_tax.py"
CONTRACT = "engine/contract.py"
TYPES = "web/lib/types.ts"
ROUTE = "web/app/api/share/create/route.ts"
TEST_FILE = "tools/test_friction_tax.py"

# ---------------------------------------------------------------------
# 1. engine/friction_tax.py -- architecture-note comment
# ---------------------------------------------------------------------

edit(
    FT,
    "def compute_legal_compliance_exposure(\n"
    "    state_ids: list[str],\n"
    "    org_size: str,\n"
    "    industry: str,\n"
    "    org_type: str,\n"
    ") -> dict:",
    "# Architecture note (confirmed via a real worked-example plausibility\n"
    "# pass, 2026-08-04, Gemini structural review): this function's dollar\n"
    "# output is deliberately headcount-independent -- Legal/Compliance\n"
    "# claims don't scale with org size the way attritional costs do\n"
    "# (Addendum 1's original rationale for rejecting a payroll-fraction\n"
    "# mapping here). One real consequence, confirmed with actual numbers,\n"
    "# not theoretical: a severe multi-cluster profile on a very small org\n"
    "# (e.g. \"Under 25\" headcount) can produce a low figure that exceeds\n"
    "# that org's own total payroll baseline -- by a wide margin at the\n"
    "# extreme tail (observed up to ~2.5x payroll stacking every real\n"
    "# Legal-scoring state at once, and far higher for the structurally\n"
    "# valid but practically unlikely combination of a tiny headcount with\n"
    "# org_type == \"Publicly traded\", since Cluster 4a's ceiling is not\n"
    "# headcount-scaled either). This is an accepted, understood property\n"
    "# of the design, not a bug -- Legal/Compliance is priced by mechanism\n"
    "# and severity, not by ability to pay. Cluster 4's org_type gating\n"
    "# (Addendum 5) is the other half of this picture: the SAME severity\n"
    "# profile can differ by >20x between \"Publicly traded\" (Cluster 4a,\n"
    "# SEC-anchored, ceiling $33M) and every other org_type (Cluster 4b,\n"
    "# Title VII-capped, max $300K) -- also intentional, and the main\n"
    "# driver of when the \"Significant\" band (_legal_exposure_band()\n"
    "# above) is actually reachable in practice for a realistic profile.\n"
    "def compute_legal_compliance_exposure(\n"
    "    state_ids: list[str],\n"
    "    org_size: str,\n"
    "    industry: str,\n"
    "    org_type: str,\n"
    ") -> dict:",
)

# ---------------------------------------------------------------------
# 2. engine/contract.py -- add "band" to legal_tail_risk_exposure
# ---------------------------------------------------------------------

edit(
    CONTRACT,
    '    legal_tail_risk_exposure = (\n'
    '        {\n'
    '            "low":                     legal_result["low"],\n'
    '            "high":                    legal_result["high"],\n'
    '            "currency":                legal_result["currency"],\n'
    '            "caveat":                  LEGAL_TAIL_RISK_CAVEAT_TEXT,\n'
    '            "has_unpriced_conditions": legal_result["has_unpriced_conditions"],\n'
    '        }\n'
    '        if legal_result["low"] is not None or legal_result["has_unpriced_conditions"]\n'
    '        else None\n'
    '    )',
    '    legal_tail_risk_exposure = (\n'
    '        {\n'
    '            "low":                     legal_result["low"],\n'
    '            "high":                    legal_result["high"],\n'
    '            "currency":                legal_result["currency"],\n'
    '            "band":                    legal_result["band"],\n'
    '            "caveat":                  LEGAL_TAIL_RISK_CAVEAT_TEXT,\n'
    '            "has_unpriced_conditions": legal_result["has_unpriced_conditions"],\n'
    '        }\n'
    '        if legal_result["low"] is not None or legal_result["has_unpriced_conditions"]\n'
    '        else None\n'
    '    )',
)

# ---------------------------------------------------------------------
# 3. web/lib/types.ts
# ---------------------------------------------------------------------

edit(
    TYPES,
    "/**\n"
    " * Legal/Compliance tail-risk exposure (private output only).\n"
    " * prompts/friction-tax-legal-compliance-methodology.md, Addendum 11.\n"
    " * Non-null when either a real dollar range exists or at least one\n"
    " * identified state carries real-but-unpriced exposure\n"
    " * (has_unpriced_conditions) -- see compute_legal_compliance_exposure()\n"
    " * in engine/friction_tax.py for the exact trigger logic.\n"
    " */\n"
    "export interface LegalTailRiskExposure {\n"
    "  low: number;\n"
    "  high: number;\n"
    "  currency: string;\n"
    "  caveat: string;\n"
    "  has_unpriced_conditions: boolean;\n"
    "}\n"
    "\n"
    "/**\n"
    " * Qualitative severity band for legal tail-risk exposure in the\n"
    " * shareable output only -- no dollar figure exposed publicly (Addendum\n"
    " * 11: a specific number in a shareable artifact could function as\n"
    " * documented notice of a contingent liability). Deliberately a bare\n"
    " * string union rather than a {low, high, caveat}-shaped interface like\n"
    " * LegalTailRiskExposure -- the shareable path has no caveat text of its\n"
    " * own yet (Finding 1: friction_tax_estimate is still hardcoded null\n"
    " * there). Revisit this shape once Finding 1's fix builds out real\n"
    " * shareable-path caveat copy -- a bare string may no longer be enough\n"
    " * once that lands.\n"
    " */\n"
    'export type LegalTailRiskBand = "Minor" | "Moderate" | "Elevated" | "Significant";',
    "/**\n"
    " * Legal/Compliance tail-risk exposure (private output only).\n"
    " * prompts/friction-tax-legal-compliance-methodology.md, Addendum 11.\n"
    " * Non-null when either a real dollar range exists or at least one\n"
    " * identified state carries real-but-unpriced exposure\n"
    " * (has_unpriced_conditions) -- see compute_legal_compliance_exposure()\n"
    " * in engine/friction_tax.py for the exact trigger logic. band is the\n"
    " * same qualitative value ShareableOutputPayload.legal_tail_risk_band\n"
    " * carries publicly -- present here too so the shareable-path builder\n"
    " * (web/app/api/share/create/route.ts) can read it straight off\n"
    " * engineResult.private_output without a separate computation.\n"
    " */\n"
    "export interface LegalTailRiskExposure {\n"
    "  low: number;\n"
    "  high: number;\n"
    "  currency: string;\n"
    "  band: LegalTailRiskBand | null;\n"
    "  caveat: string;\n"
    "  has_unpriced_conditions: boolean;\n"
    "}\n"
    "\n"
    "/**\n"
    " * Qualitative severity band for legal tail-risk exposure. Computed\n"
    " * server-side in engine/friction_tax.py's _legal_exposure_band() and\n"
    " * carried through LegalTailRiskExposure.band (private output) into\n"
    " * ShareableOutputPayload.legal_tail_risk_band (shareable output) --\n"
    " * the shareable path never gets a dollar figure, only this band\n"
    " * (Addendum 11: a specific number in a shareable artifact could\n"
    " * function as documented notice of a contingent liability).\n"
    " */\n"
    'export type LegalTailRiskBand = "Minor" | "Moderate" | "Elevated" | "Significant";',
)

edit(
    TYPES,
    "  // Legal/Compliance qualitative band (nullable, optional) -- Addendum 11.\n"
    "  // Optional because web/app/api/share/create/route.ts isn't wired to\n"
    "  // populate this yet (deferred alongside Finding 1's fix) -- present\n"
    "  // in the type now so that wiring is a small addition later, not a\n"
    "  // schema change.\n"
    "  legal_tail_risk_band?: LegalTailRiskBand | null;",
    "  // Legal/Compliance qualitative band (nullable) -- Addendum 11.\n"
    "  // web/app/api/share/create/route.ts populates this from\n"
    "  // engineResult.private_output.legal_tail_risk_exposure?.band.\n"
    "  legal_tail_risk_band: LegalTailRiskBand | null;",
)

# ---------------------------------------------------------------------
# 4. web/app/api/share/create/route.ts
# ---------------------------------------------------------------------

edit(
    ROUTE,
    "    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,\n"
    "\n"
    "    intake: mapIntake(engineResult.intake as Record<string, unknown>),",
    "    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,\n"
    "    legal_tail_risk_band: engineResult.private_output.legal_tail_risk_exposure?.band ?? null,\n"
    "\n"
    "    intake: mapIntake(engineResult.intake as Record<string, unknown>),",
)

# ---------------------------------------------------------------------
# 5. tools/test_friction_tax.py -- boundary-threshold tests
# ---------------------------------------------------------------------

edit(
    TEST_FILE,
    "\n# -- Results ---------------------------------------------------------------------",
    '''

# -- 32. _legal_exposure_band() -- exact boundary-threshold behavior -------------
# Confirms the real inequality direction matches Addendum 11's "Under $100K" /
# "$100K-$500K" / "$500K-$2M" / "$2M+" wording -- each cutoff value itself
# lands in the HIGHER band, not the lower one.

check(
    "_legal_exposure_band(None) -> None",
    _ft._legal_exposure_band(None) is None,
    f"got {_ft._legal_exposure_band(None)}",
)
check(
    "_legal_exposure_band(0.0) -> Minor (zero floor, still a real number)",
    _ft._legal_exposure_band(0.0) == "Minor",
    f"got {_ft._legal_exposure_band(0.0)}",
)
check(
    "_legal_exposure_band(99_999.99) -> Minor (just under $100K)",
    _ft._legal_exposure_band(99_999.99) == "Minor",
    f"got {_ft._legal_exposure_band(99_999.99)}",
)
check(
    "_legal_exposure_band(100_000.0) -> Moderate ($100K itself, not Minor)",
    _ft._legal_exposure_band(100_000.0) == "Moderate",
    f"got {_ft._legal_exposure_band(100_000.0)}",
)
check(
    "_legal_exposure_band(499_999.99) -> Moderate (just under $500K)",
    _ft._legal_exposure_band(499_999.99) == "Moderate",
    f"got {_ft._legal_exposure_band(499_999.99)}",
)
check(
    "_legal_exposure_band(500_000.0) -> Elevated ($500K itself, not Moderate)",
    _ft._legal_exposure_band(500_000.0) == "Elevated",
    f"got {_ft._legal_exposure_band(500_000.0)}",
)
check(
    "_legal_exposure_band(1_999_999.99) -> Elevated (just under $2M)",
    _ft._legal_exposure_band(1_999_999.99) == "Elevated",
    f"got {_ft._legal_exposure_band(1_999_999.99)}",
)
check(
    "_legal_exposure_band(2_000_000.0) -> Significant ($2M itself, not Elevated)",
    _ft._legal_exposure_band(2_000_000.0) == "Significant",
    f"got {_ft._legal_exposure_band(2_000_000.0)}",
)
check(
    "_legal_exposure_band(50_000_000.0) -> Significant (well above $2M)",
    _ft._legal_exposure_band(50_000_000.0) == "Significant",
    f"got {_ft._legal_exposure_band(50_000_000.0)}",
)


# -- Results ---------------------------------------------------------------------''',
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
