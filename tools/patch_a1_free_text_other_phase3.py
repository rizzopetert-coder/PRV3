"""
PRV3 -- A1 (free-text "Other" elaboration for significant_events), Phase 3
(web/app/api/ route handlers). Gemini architecture review: CLEARED TO
BUILD WITH STRUCTURAL AIRGAP.

Corrections to Gemini's phase-3 file list, found while tracing the real
data path (see Phase 1's docstring for the full account):
  - session/answer/route.ts is NOT touched by this script. It has no
    mapIntake() function -- it passes session.intake straight through
    unchanged (line 318 of that file). Once DiagnosticSession.intake is
    PrivateIntakeEcho (Phase 1), that passthrough already carries
    significant_event_elaboration with zero code change needed here.
  - share/create/route.ts's mapIntake() needs no destructure-strip logic.
    It already builds the shareable object field-by-field, explicitly --
    never spreading the engine's raw intake dict -- so it structurally
    excludes elaboration already. Only its return-type annotation changes,
    from IntakeEcho to the new ShareableIntakeEcho, completing the
    compile-time airgap Gemini's review committed to (the function body
    is untouched).

Real scope: session/start/route.ts (validateIntake() gains the new
optional field, with the same "required when 'other' is selected" rule as
the client-side isComplete gate -- this is the real server-side trust
boundary, not the browser) and result/route.ts (mapIntake() threads
significant_event_elaboration through from the engine's intake echo).

Usage:
  python tools/patch_a1_free_text_other_phase3.py --dry-run
  python tools/patch_a1_free_text_other_phase3.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


START = "web/app/api/diagnostic/session/start/route.ts"
RESULT = "web/app/api/result/route.ts"
SHARE = "web/app/api/share/create/route.ts"

# ═══════════════════════════════════════════════════════════════════════
# session/start/route.ts -- the real server-side trust boundary.
# ═══════════════════════════════════════════════════════════════════════

edit(
    START,
    'import { SIGNIFICANT_EVENT_OPTIONS, type IntakeEcho } from "@/lib/types";',
    'import { SIGNIFICANT_EVENT_OPTIONS, type PrivateIntakeEcho } from "@/lib/types";',
)

edit(
    START,
    'function validateIntake(body: unknown): body is IntakeEcho {\n'
    '  if (typeof body !== "object" || body === null) return false;\n'
    '  const b = body as Record<string, unknown>;\n'
    '  // Soft transition (locked decision) -- accepts a real int from the new\n'
    '  // stepper UI or a legacy non-empty bucket string, never hard-rejects\n'
    '  // an old-format submission.\n'
    '  const validOrgSize =\n'
    '    (typeof b.organization_size === "number" && Number.isFinite(b.organization_size)) ||\n'
    '    (typeof b.organization_size === "string" && b.organization_size.length > 0);\n'
    '  const validSignificantEvents =\n'
    '    Array.isArray(b.significant_events) &&\n'
    '    b.significant_events.length > 0 &&\n'
    '    b.significant_events.every(\n'
    '      (v): v is string => typeof v === "string" && VALID_SIGNIFICANT_EVENTS.has(v)\n'
    '    );\n'
    '  return (\n'
    '    validOrgSize &&\n'
    '    typeof b.industry === "string" &&\n'
    '    typeof b.role_level === "string" &&\n'
    '    typeof b.tenure_in_role === "string" &&\n'
    '    typeof b.direct_reports === "string" &&\n'
    '    typeof b.jurisdiction === "string" &&\n'
    '    validSignificantEvents\n'
    '  );\n'
    '}',
    'function validateIntake(body: unknown): body is PrivateIntakeEcho {\n'
    '  if (typeof body !== "object" || body === null) return false;\n'
    '  const b = body as Record<string, unknown>;\n'
    '  // Soft transition (locked decision) -- accepts a real int from the new\n'
    '  // stepper UI or a legacy non-empty bucket string, never hard-rejects\n'
    '  // an old-format submission.\n'
    '  const validOrgSize =\n'
    '    (typeof b.organization_size === "number" && Number.isFinite(b.organization_size)) ||\n'
    '    (typeof b.organization_size === "string" && b.organization_size.length > 0);\n'
    '  const validSignificantEvents =\n'
    '    Array.isArray(b.significant_events) &&\n'
    '    b.significant_events.length > 0 &&\n'
    '    b.significant_events.every(\n'
    '      (v): v is string => typeof v === "string" && VALID_SIGNIFICANT_EVENTS.has(v)\n'
    '    );\n'
    '  // A1 -- elaboration is optional in general, but required non-empty\n'
    '  // whenever "other" is among significant_events. This is the real\n'
    '  // server-side trust boundary, not the browser -- the client\'s own\n'
    '  // isComplete gate (DiagnosticFlow.tsx) enforces the same rule, but\n'
    '  // this is what actually stops a bad submission.\n'
    '  const elaboration = b.significant_event_elaboration;\n'
    '  const validElaboration =\n'
    '    elaboration === undefined || typeof elaboration === "string";\n'
    '  const otherSatisfied =\n'
    '    !validSignificantEvents ||\n'
    '    !(b.significant_events as unknown[]).includes("other") ||\n'
    '    (typeof elaboration === "string" && elaboration.trim().length > 0);\n'
    '  return (\n'
    '    validOrgSize &&\n'
    '    typeof b.industry === "string" &&\n'
    '    typeof b.role_level === "string" &&\n'
    '    typeof b.tenure_in_role === "string" &&\n'
    '    typeof b.direct_reports === "string" &&\n'
    '    typeof b.jurisdiction === "string" &&\n'
    '    validSignificantEvents &&\n'
    '    validElaboration &&\n'
    '    otherSatisfied\n'
    '  );\n'
    '}',
)

# ═══════════════════════════════════════════════════════════════════════
# result/route.ts -- mapIntake() threads elaboration through from the
# engine's own intake echo (undefined for Path B, which doesn't collect
# it -- forward-compatible either way, same pattern as org_size's
# existing headcount-fallback comment right above it).
# ═══════════════════════════════════════════════════════════════════════

edit(
    RESULT,
    '  IntakeEcho,\n'
    '  SynthesisFields,',
    '  PrivateIntakeEcho,\n'
    '  SynthesisFields,',
)

edit(
    RESULT,
    '// Intake mapping — engine echo fields → IntakeEcho contract',
    '// Intake mapping — engine echo fields → PrivateIntakeEcho contract',
)

edit(
    RESULT,
    'function mapIntake(engineIntake: Record<string, unknown>): IntakeEcho {\n'
    '  const jurisdictions = Array.isArray(engineIntake.jurisdictions)\n'
    '    ? (engineIntake.jurisdictions as string[])\n'
    '    : [];\n'
    '  const significantEvents = Array.isArray(engineIntake.significant_events)\n'
    '    ? (engineIntake.significant_events as string[])\n'
    '    : ["none"];\n'
    '  return {\n'
    '    // headcount is the real Python IntakeData field; org_size is a\n'
    '    // fallback for any caller still on the pre-Phase-1 engine shape.\n'
    '    organization_size: parseOrgSize(engineIntake.headcount ?? engineIntake.org_size),\n'
    '    industry: (engineIntake.industry as string) ?? "",\n'
    '    role_level: (engineIntake.principal_role as string) ?? "",\n'
    '    tenure_in_role: "",\n'
    '    direct_reports: "",\n'
    '    jurisdiction: jurisdictions[0] ?? "",\n'
    '    significant_events: significantEvents,\n'
    '  };\n'
    '}',
    'function mapIntake(engineIntake: Record<string, unknown>): PrivateIntakeEcho {\n'
    '  const jurisdictions = Array.isArray(engineIntake.jurisdictions)\n'
    '    ? (engineIntake.jurisdictions as string[])\n'
    '    : [];\n'
    '  const significantEvents = Array.isArray(engineIntake.significant_events)\n'
    '    ? (engineIntake.significant_events as string[])\n'
    '    : ["none"];\n'
    '  return {\n'
    '    // headcount is the real Python IntakeData field; org_size is a\n'
    '    // fallback for any caller still on the pre-Phase-1 engine shape.\n'
    '    organization_size: parseOrgSize(engineIntake.headcount ?? engineIntake.org_size),\n'
    '    industry: (engineIntake.industry as string) ?? "",\n'
    '    role_level: (engineIntake.principal_role as string) ?? "",\n'
    '    tenure_in_role: "",\n'
    '    direct_reports: "",\n'
    '    jurisdiction: jurisdictions[0] ?? "",\n'
    '    significant_events: significantEvents,\n'
    '    // A1 -- undefined for Path B (doesn\'t collect it); Path 1 always\n'
    '    // echoes a real string ("" when "other" wasn\'t selected).\n'
    '    significant_event_elaboration: engineIntake.significant_event_elaboration as string | undefined,\n'
    '  };\n'
    '}',
)

# ═══════════════════════════════════════════════════════════════════════
# share/create/route.ts -- return-type change only. mapIntake()'s body
# already excludes elaboration by construction (no destructure-strip
# needed -- see docstring).
# ═══════════════════════════════════════════════════════════════════════

edit(
    SHARE,
    '  ShareableOutputPayload,\n'
    '  StateRef,\n'
    '  IntakeEcho,\n'
    '  ShareableSynthesisFields,',
    '  ShareableOutputPayload,\n'
    '  StateRef,\n'
    '  ShareableIntakeEcho,\n'
    '  ShareableSynthesisFields,',
)

edit(
    SHARE,
    'function mapIntake(engineIntake: Record<string, unknown>): IntakeEcho {',
    'function mapIntake(engineIntake: Record<string, unknown>): ShareableIntakeEcho {',
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
