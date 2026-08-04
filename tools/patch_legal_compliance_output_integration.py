"""
PRV3 -- Legal/Compliance output integration (Addendum 11).

1. engine/friction_tax.py: new _legal_exposure_band() helper, wired
   into all 3 of compute_legal_compliance_exposure()'s return paths as
   a "band" key.
2. engine/contract.py: compute_legal_compliance_exposure() called
   alongside compute_friction_tax() in assemble_output(); new
   LEGAL_TAIL_RISK_CAVEAT_TEXT constant; legal_tail_risk_exposure added
   to private_output (band explicitly excluded, per Pete's instruction
   -- private output doesn't need it); _PRIVATE_OUTPUT_FIELDS updated.
3. web/lib/types.ts: LegalTailRiskExposure interface, LegalTailRiskBand
   string-union type (with a comment flagging it for revisit once
   Finding 1's fix builds out real shareable-path caveat text).
   PrivateOutputPayload gains legal_tail_risk_exposure (required,
   nullable). ShareableOutputPayload gains legal_tail_risk_band
   (optional -- share/create/route.ts isn't being touched this round).
   FrictionTaxEstimate's stale doc comment corrected.
4. web/lib/engine-client.ts: EngineResult.private_output gains
   legal_tail_risk_exposure, mirroring contract.py's shape a third time
   (the hand-maintained wire-contract mirror, distinct from types.ts's
   PrivateOutputPayload).
5. Both PrivateOutputPayload builders -- web/app/api/result/route.ts
   (Path B) and web/app/api/diagnostic/session/answer/route.ts (Path 1)
   -- gain one line each populating the new field from engineResult,
   exactly like they already do for friction_tax_estimate. Neither is
   Finding 1's file (web/app/api/share/create/route.ts); that one is
   untouched, per Pete's explicit instruction.

Usage:
  python tools/patch_legal_compliance_output_integration.py --dry-run
  python tools/patch_legal_compliance_output_integration.py --write
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
ENGINE_CLIENT = "web/lib/engine-client.ts"
RESULT_ROUTE = "web/app/api/result/route.ts"
ANSWER_ROUTE = "web/app/api/diagnostic/session/answer/route.ts"
DEV_PREVIEW = "web/lib/dev-diagnostic-preview.ts"

# ---------------------------------------------------------------------
# 1. engine/friction_tax.py
# ---------------------------------------------------------------------

edit(
    FT,
    'def compute_legal_compliance_exposure(\n'
    '    state_ids: list[str],\n'
    '    org_size: str,\n'
    '    industry: str,\n'
    '    org_type: str,\n'
    ') -> dict:',
    'def _legal_exposure_band(low: Optional[float]) -> Optional[str]:\n'
    '    """\n'
    '    Addendum 11\'s qualitative severity band for the shareable output --\n'
    '    no dollar figure exposed publicly (a specific number in a shareable\n'
    '    artifact could function as documented notice of a contingent\n'
    '    liability). Applied to "low" only. Boundaries are a first pass, not\n'
    '    yet stress-tested against real multi-cluster worked examples\n'
    '    (Addendum 11\'s own open item #3) -- treat as provisional until that\n'
    '    check runs.\n'
    '    """\n'
    '    if low is None:\n'
    '        return None\n'
    '    if low < 100_000.0:\n'
    '        return "Minor"\n'
    '    if low < 500_000.0:\n'
    '        return "Moderate"\n'
    '    if low < 2_000_000.0:\n'
    '        return "Elevated"\n'
    '    return "Significant"\n'
    '\n'
    '\n'
    'def compute_legal_compliance_exposure(\n'
    '    state_ids: list[str],\n'
    '    org_size: str,\n'
    '    industry: str,\n'
    '    org_type: str,\n'
    ') -> dict:',
)

edit(
    FT,
    '    if not per_state_ranges:\n'
    '        return {\n'
    '            "low": None,\n'
    '            "high": None,\n'
    '            "currency": "USD",\n'
    '            "has_unpriced_conditions": has_unpriced_conditions,\n'
    '            "unpriced_state_ids": unpriced_state_ids,\n'
    '        }\n'
    '\n'
    '    if len(per_state_ranges) == 1:\n'
    '        low, high = next(iter(per_state_ranges.values()))\n'
    '        return {\n'
    '            "low": round(low, 2),\n'
    '            "high": round(high, 2),\n'
    '            "currency": "USD",\n'
    '            "has_unpriced_conditions": has_unpriced_conditions,\n'
    '            "unpriced_state_ids": unpriced_state_ids,\n'
    '        }',
    '    if not per_state_ranges:\n'
    '        return {\n'
    '            "low": None,\n'
    '            "high": None,\n'
    '            "currency": "USD",\n'
    '            "band": _legal_exposure_band(None),\n'
    '            "has_unpriced_conditions": has_unpriced_conditions,\n'
    '            "unpriced_state_ids": unpriced_state_ids,\n'
    '        }\n'
    '\n'
    '    if len(per_state_ranges) == 1:\n'
    '        low, high = next(iter(per_state_ranges.values()))\n'
    '        rounded_low = round(low, 2)\n'
    '        return {\n'
    '            "low": rounded_low,\n'
    '            "high": round(high, 2),\n'
    '            "currency": "USD",\n'
    '            "band": _legal_exposure_band(rounded_low),\n'
    '            "has_unpriced_conditions": has_unpriced_conditions,\n'
    '            "unpriced_state_ids": unpriced_state_ids,\n'
    '        }',
)

edit(
    FT,
    '    return {\n'
    '        "low": round(total_low, 2),\n'
    '        "high": round(total_high, 2),\n'
    '        "currency": "USD",\n'
    '        "has_unpriced_conditions": has_unpriced_conditions,\n'
    '        "unpriced_state_ids": unpriced_state_ids,\n'
    '    }',
    '    rounded_total_low = round(total_low, 2)\n'
    '    return {\n'
    '        "low": rounded_total_low,\n'
    '        "high": round(total_high, 2),\n'
    '        "currency": "USD",\n'
    '        "band": _legal_exposure_band(rounded_total_low),\n'
    '        "has_unpriced_conditions": has_unpriced_conditions,\n'
    '        "unpriced_state_ids": unpriced_state_ids,\n'
    '    }',
)

# ---------------------------------------------------------------------
# 2. engine/contract.py
# ---------------------------------------------------------------------

edit(
    CONTRACT,
    "from engine.friction_tax import compute_friction_tax",
    "from engine.friction_tax import compute_friction_tax, compute_legal_compliance_exposure\n"
    "\n"
    "# Addendum 11 -- caveat text for legal_tail_risk_exposure (private_output only).\n"
    "LEGAL_TAIL_RISK_CAVEAT_TEXT = (\n"
    '    "This estimate reflects contingent exposure -- a range of what could be at "\n'
    '    "stake if this pattern were ever formally challenged, not a prediction that "\n'
    '    "it will be. Most organizations carrying a similar pattern never face an "\n'
    '    "actual claim. This figure combines identified conditions across legal and "\n'
    '    "regulatory categories, using publicly available case outcomes, agency "\n'
    '    "enforcement data, and statutory penalty schedules as reference points -- "\n'
    '    "not a legal opinion, and not specific to your organization\'s actual risk "\n'
    '    "of being challenged. If any of these conditions concern you, this is worth "\n'
    '    "a conversation with employment counsel, not just this number."\n'
    ")",
)

edit(
    CONTRACT,
    '    friction_tax_result = compute_friction_tax(\n'
    '        state_ids=[s["state_id"] for s in identified_states],\n'
    '        severity_tier=sev.tier,\n'
    '        org_size=session.intake.headcount,\n'
    '        industry=session.intake.industry,\n'
    '        org_type=session.intake.org_type,\n'
    '    )\n'
    '    friction_tax_estimate = (\n'
    '        {\n'
    '            "low":      friction_tax_result["low"],\n'
    '            "high":     friction_tax_result["high"],\n'
    '            "currency": friction_tax_result["currency"],\n'
    '        }\n'
    '        if friction_tax_result["calibration_complete"]\n'
    '        else None\n'
    '    )\n'
    '    private_output = {\n'
    '        "opening_text":          priv.state_name if priv else "",\n'
    '        "resolution_routing":    priv.resolution_family if priv else "",\n'
    '        "friction_tax_estimate": friction_tax_estimate,\n'
    '        "cascade_risk":          compute_cascade_risk(session.accumulated_vector),\n'
    '        "causation_pattern":     compute_causation_pattern(session.accumulated_vector, routing),',
    '    friction_tax_result = compute_friction_tax(\n'
    '        state_ids=[s["state_id"] for s in identified_states],\n'
    '        severity_tier=sev.tier,\n'
    '        org_size=session.intake.headcount,\n'
    '        industry=session.intake.industry,\n'
    '        org_type=session.intake.org_type,\n'
    '    )\n'
    '    friction_tax_estimate = (\n'
    '        {\n'
    '            "low":      friction_tax_result["low"],\n'
    '            "high":     friction_tax_result["high"],\n'
    '            "currency": friction_tax_result["currency"],\n'
    '        }\n'
    '        if friction_tax_result["calibration_complete"]\n'
    '        else None\n'
    '    )\n'
    '    legal_result = compute_legal_compliance_exposure(\n'
    '        state_ids=[s["state_id"] for s in identified_states],\n'
    '        org_size=session.intake.headcount,\n'
    '        industry=session.intake.industry,\n'
    '        org_type=session.intake.org_type,\n'
    '    )\n'
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
    '    )\n'
    '    private_output = {\n'
    '        "opening_text":            priv.state_name if priv else "",\n'
    '        "resolution_routing":      priv.resolution_family if priv else "",\n'
    '        "friction_tax_estimate":   friction_tax_estimate,\n'
    '        "legal_tail_risk_exposure": legal_tail_risk_exposure,\n'
    '        "cascade_risk":            compute_cascade_risk(session.accumulated_vector),\n'
    '        "causation_pattern":       compute_causation_pattern(session.accumulated_vector, routing),',
)

edit(
    CONTRACT,
    '_PRIVATE_OUTPUT_FIELDS = {\n'
    '    "opening_text", "resolution_routing", "friction_tax_estimate", "cascade_risk",\n'
    '    "causation_pattern", "trajectory",\n'
    '}',
    '_PRIVATE_OUTPUT_FIELDS = {\n'
    '    "opening_text", "resolution_routing", "friction_tax_estimate",\n'
    '    "legal_tail_risk_exposure", "cascade_risk", "causation_pattern", "trajectory",\n'
    '}',
)

# ---------------------------------------------------------------------
# 3. web/lib/types.ts
# ---------------------------------------------------------------------

edit(
    TYPES,
    "/**\n"
    " * Friction tax estimate.\n"
    " * Always null in Path B (calibration target — no multipliers set).\n"
    " * Components render Option B treatment when null:\n"
    ' * "Economic impact estimate available after full diagnostic."\n'
    " * Phase 3 work: calibrate STATE_MULTIPLIERS, populate this field.\n"
    " */\n"
    "export interface FrictionTaxEstimate {\n"
    "  low: number;\n"
    "  high: number;\n"
    "  currency: string;\n"
    "}",
    "/**\n"
    " * Friction tax estimate.\n"
    " * Populated with a real computed value in both private-output paths\n"
    " * (web/app/api/result/route.ts, web/app/api/diagnostic/session/answer/route.ts\n"
    " * both read engineResult.private_output.friction_tax_estimate directly)\n"
    " * now that STATE_MULTIPLIERS is fully calibrated (Option A rescale,\n"
    ' * 2026-08-03) -- no longer a "Phase 3" TODO. Still hardcoded null in the\n'
    " * shareable path (web/app/api/share/create/route.ts) -- a known,\n"
    " * separate bug (prompts/friction-tax-legal-compliance-methodology.md,\n"
    " * Addendum 11, Finding 1), not a calibration gap. Components render\n"
    " * Option B treatment when null:\n"
    ' * "Economic impact estimate available after full diagnostic."\n'
    " */\n"
    "export interface FrictionTaxEstimate {\n"
    "  low: number;\n"
    "  high: number;\n"
    "  currency: string;\n"
    "}\n"
    "\n"
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
)

edit(
    TYPES,
    "  // Economic (nullable)\n"
    "  friction_tax_estimate: FrictionTaxEstimate | null;\n"
    "\n"
    "  // Cross-Dimensional Cascade Risk",
    "  // Economic (nullable)\n"
    "  friction_tax_estimate: FrictionTaxEstimate | null;\n"
    "\n"
    "  // Legal/Compliance tail-risk exposure (nullable) -- Addendum 11.\n"
    "  legal_tail_risk_exposure: LegalTailRiskExposure | null;\n"
    "\n"
    "  // Cross-Dimensional Cascade Risk",
)

edit(
    TYPES,
    "  // Economic (nullable — Option B rendering when null)\n"
    "  friction_tax_estimate: FrictionTaxEstimate | null;\n"
    "\n"
    "  // Intake echo — grounds friction_tax_estimate math for external audience",
    "  // Economic (nullable — Option B rendering when null)\n"
    "  friction_tax_estimate: FrictionTaxEstimate | null;\n"
    "\n"
    "  // Legal/Compliance qualitative band (nullable, optional) -- Addendum 11.\n"
    "  // Optional because web/app/api/share/create/route.ts isn't wired to\n"
    "  // populate this yet (deferred alongside Finding 1's fix) -- present\n"
    "  // in the type now so that wiring is a small addition later, not a\n"
    "  // schema change.\n"
    "  legal_tail_risk_band?: LegalTailRiskBand | null;\n"
    "\n"
    "  // Intake echo — grounds friction_tax_estimate math for external audience",
)

# ---------------------------------------------------------------------
# 4. web/lib/engine-client.ts
# ---------------------------------------------------------------------

edit(
    ENGINE_CLIENT,
    'import type { IntakeEcho, FrictionTaxEstimate } from "@/lib/types";',
    'import type { IntakeEcho, FrictionTaxEstimate, LegalTailRiskExposure } from "@/lib/types";',
)

edit(
    ENGINE_CLIENT,
    "  private_output: {\n"
    "    opening_text: string;\n"
    "    resolution_routing: string;\n"
    "    friction_tax_estimate: FrictionTaxEstimate | null;\n"
    "    cascade_risk: number;",
    "  private_output: {\n"
    "    opening_text: string;\n"
    "    resolution_routing: string;\n"
    "    friction_tax_estimate: FrictionTaxEstimate | null;\n"
    "    legal_tail_risk_exposure: LegalTailRiskExposure | null;\n"
    "    cascade_risk: number;",
)

# ---------------------------------------------------------------------
# 5. Both PrivateOutputPayload builders
# ---------------------------------------------------------------------

edit(
    RESULT_ROUTE,
    "    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,\n"
    "\n"
    "    intake: mapIntake(engineResult.intake as Record<string, unknown>),",
    "    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,\n"
    "    legal_tail_risk_exposure: engineResult.private_output.legal_tail_risk_exposure,\n"
    "\n"
    "    intake: mapIntake(engineResult.intake as Record<string, unknown>),",
)

edit(
    ANSWER_ROUTE,
    "    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,\n"
    "\n"
    "    cascade_risk: engineResult.private_output.cascade_risk,",
    "    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,\n"
    "    legal_tail_risk_exposure: engineResult.private_output.legal_tail_risk_exposure,\n"
    "\n"
    "    cascade_risk: engineResult.private_output.cascade_risk,",
)

# ---------------------------------------------------------------------
# 6. DevDiagnosticPreviewPayload -- a third, dev-only structural mirror
#    of PrivateOutputPayload, discovered via a real tsc failure, not
#    anticipated in the original 5-point plan. <PrivateOutput> renders
#    this type too (web/app/dev/diagnostic-preview/[id]/page.tsx), so it
#    needs every field PrivateOutputPayload requires or that assignment
#    fails to type-check. tools/diagnostic_fast_forward.py (the Python
#    tool that populates this, via /api/dev/diagnostic-preview) forwards
#    the engine's raw JSON response wholesale -- confirmed via grep, no
#    field-by-field construction there -- so no Python-side change is
#    needed, only this TypeScript interface.
# ---------------------------------------------------------------------

edit(
    DEV_PREVIEW,
    'import type {\n'
    '  SynthesisFields,\n'
    '  StateRef,\n'
    '  SeverityTier,\n'
    '  ResolutionFamily,\n'
    '  FrictionTaxEstimate,\n'
    '  IntakeEcho,\n'
    '  DimensionSummary,\n'
    '} from "@/lib/types";',
    'import type {\n'
    '  SynthesisFields,\n'
    '  StateRef,\n'
    '  SeverityTier,\n'
    '  ResolutionFamily,\n'
    '  FrictionTaxEstimate,\n'
    '  LegalTailRiskExposure,\n'
    '  IntakeEcho,\n'
    '  DimensionSummary,\n'
    '} from "@/lib/types";',
)

edit(
    DEV_PREVIEW,
    "export interface DevDiagnosticPreviewPayload {\n"
    "  synthesis: SynthesisFields;\n"
    "  primary_state: StateRef;\n"
    "  secondary_states: StateRef[];\n"
    "  severity: SeverityTier;\n"
    "  resolution_family: ResolutionFamily;\n"
    "  resolution_routing: string;\n"
    "  friction_tax_estimate: FrictionTaxEstimate | null;\n"
    "  intake: IntakeEcho;\n"
    "  dimension_summary: DimensionSummary;\n"
    "  primary_asset_domain: string;\n"
    "}",
    "export interface DevDiagnosticPreviewPayload {\n"
    "  synthesis: SynthesisFields;\n"
    "  primary_state: StateRef;\n"
    "  secondary_states: StateRef[];\n"
    "  severity: SeverityTier;\n"
    "  resolution_family: ResolutionFamily;\n"
    "  resolution_routing: string;\n"
    "  friction_tax_estimate: FrictionTaxEstimate | null;\n"
    "  legal_tail_risk_exposure: LegalTailRiskExposure | null;\n"
    "  intake: IntakeEcho;\n"
    "  dimension_summary: DimensionSummary;\n"
    "  primary_asset_domain: string;\n"
    "}",
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
