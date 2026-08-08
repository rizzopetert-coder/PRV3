"""
Unplanned-but-necessary fix, found while running Phase 2's tsc --noEmit
verification (Mechanism 1 deprecation session): making IntakeEcho.
significant_events required broke type-checking in three files outside
the four Pete named, all constructing IntakeEcho-shaped object literals
field-by-field rather than passing a full IntakeEcho through:

  1. web/app/api/result/route.ts's mapIntake() -- converts the engine's
     own echoed intake dict (Python IntakeData shape, which has always
     carried significant_events -- engine/contract.py's _INTAKE_FIELDS,
     confirmed already present pre-Phase-2) back to IntakeEcho for
     Path B. Now maps engineIntake.significant_events through, with a
     defensive ["none"] fallback for any caller whose echoed intake
     predates this field or isn't shaped as expected.
  2. web/app/api/share/create/route.ts's mapIntake() -- same shape,
     independently duplicated (matching this codebase's existing
     pattern of duplicating small mapping functions across route
     handlers rather than sharing them -- same rationale already on
     record for getPrimaryFamily()/translateResolutionFamily()). Same
     fix, not consolidated into a shared function -- out of scope to
     refactor that now.
  3. web/lib/engine-client.test.ts's BASE_INTAKE fixture -- one shared
     constant, fixes all 4 compile errors at once. significant_events:
     ["none"] -- an arbitrary-but-valid fixture value, these tests don't
     assert anything about intake content itself (they test
     CompletePayload's checkpoint_results/severity_inputs shape).

Usage:
  python tools/patch_phase2_intakeecho_fallout.py --dry-run
  python tools/patch_phase2_intakeecho_fallout.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================================
# 1. web/app/api/result/route.ts
# ============================================================================

edit(
    "web/app/api/result/route.ts",
    '''  return {
    // headcount is the real Python IntakeData field; org_size is a
    // fallback for any caller still on the pre-Phase-1 engine shape.
    organization_size: parseOrgSize(engineIntake.headcount ?? engineIntake.org_size),
    industry: (engineIntake.industry as string) ?? "",
    role_level: (engineIntake.principal_role as string) ?? "",
    tenure_in_role: "",
    direct_reports: "",
    jurisdiction: jurisdictions[0] ?? "",
  };''',
    '''  const significantEvents = Array.isArray(engineIntake.significant_events)
    ? (engineIntake.significant_events as string[])
    : ["none"];
  return {
    // headcount is the real Python IntakeData field; org_size is a
    // fallback for any caller still on the pre-Phase-1 engine shape.
    organization_size: parseOrgSize(engineIntake.headcount ?? engineIntake.org_size),
    industry: (engineIntake.industry as string) ?? "",
    role_level: (engineIntake.principal_role as string) ?? "",
    tenure_in_role: "",
    direct_reports: "",
    jurisdiction: jurisdictions[0] ?? "",
    significant_events: significantEvents,
  };''',
)

# ============================================================================
# 2. web/app/api/share/create/route.ts
# ============================================================================

edit(
    "web/app/api/share/create/route.ts",
    '''function mapIntake(engineIntake: Record<string, unknown>): IntakeEcho {
  const jurisdictions = Array.isArray(engineIntake.jurisdictions)
    ? (engineIntake.jurisdictions as string[])
    : [];
  return {
    organization_size: (engineIntake.org_size as string) ?? "",
    industry: (engineIntake.industry as string) ?? "",
    role_level: (engineIntake.principal_role as string) ?? "",''',
    '''function mapIntake(engineIntake: Record<string, unknown>): IntakeEcho {
  const jurisdictions = Array.isArray(engineIntake.jurisdictions)
    ? (engineIntake.jurisdictions as string[])
    : [];
  const significantEvents = Array.isArray(engineIntake.significant_events)
    ? (engineIntake.significant_events as string[])
    : ["none"];
  return {
    organization_size: (engineIntake.org_size as string) ?? "",
    industry: (engineIntake.industry as string) ?? "",
    role_level: (engineIntake.principal_role as string) ?? "",''',
)

# ============================================================================
# 3. web/lib/engine-client.test.ts
# ============================================================================

edit(
    "web/lib/engine-client.test.ts",
    '''const BASE_INTAKE = {
  organization_size: "51-200",
  industry: "Technology",
  role_level: "CEO",
  tenure_in_role: "",
  direct_reports: "",
  jurisdiction: "US-CA",
};''',
    '''const BASE_INTAKE = {
  organization_size: "51-200",
  industry: "Technology",
  role_level: "CEO",
  tenure_in_role: "",
  direct_reports: "",
  jurisdiction: "US-CA",
  significant_events: ["none"],
};''',
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    # Need to find the actual mapIntake block in share/create/route.ts
    # precisely -- verify it separately since its return statement's
    # remaining fields weren't captured in the anchor above (only the
    # function opening + first 3 return fields, to keep the anchor
    # short and avoid over-matching against result/route.ts's near-
    # identical but not-identical function).

    by_file: dict[str, list[tuple[str, str]]] = {}
    for path, old, new in EDITS:
        by_file.setdefault(path, []).append((old, new))

    for rel_path, pairs in by_file.items():
        full_path = REPO_ROOT / rel_path
        content = full_path.read_text(encoding="utf-8")
        for old, new in pairs:
            count = content.count(old)
            if count != 1:
                print(f"ABORT: {rel_path}: expected exactly 1 match for anchor, found {count}")
                print(f"  anchor (first 150 chars): {old[:150]!r}")
                sys.exit(1)
            content = content.replace(old, new, 1)

        if args.dry_run:
            print(f"=== {rel_path}: {len(pairs)} edit(s) would apply cleanly ===")
        else:
            full_path.write_text(content, encoding="utf-8")
            print(f"=== {rel_path}: {len(pairs)} edit(s) written ===")

    if args.dry_run:
        print("\nDry run complete. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
