"""
Mechanism 1 deprecation, Phase 2 (web schema & UI wiring). Gemini-
reviewed, both decision points and all four file diffs approved by
Pete as diffed.

Four files, five edits:
  1. web/lib/types.ts -- new SIGNIFICANT_EVENT_OPTIONS canonical list
     (single source of truth, imported by both the client UI and the
     server route) + significant_events added to IntakeEcho.
  2. web/app/api/diagnostic/session/start/route.ts -- validateIntake()
     rejects unknown event values against the 9 canonical keys,
     requires at least one selection.
  3. engine/main.py -- _locked_intake_to_engine_intake() reads the real
     significant_events value instead of hardcoding ["none"]. org_type
     unchanged (separate, unrelated gap).
  4. web/components/DiagnosticFlow.tsx -- IntakeFormState/EMPTY_INTAKE
     gain significant_events, isComplete restructured (the old
     Object.values().every(v => v !== "") pattern silently passed once
     one field became an array), new SignificantEventsField component
     (nested inside IntakeForm, matching field()/HeadcountStepper's
     existing pattern) with None/other-events mutual exclusivity,
     rendered after jurisdiction.

Copy for the 9 checkbox labels: verbatim engine/data/intake.py
PRIOR_ADJUSTERS text for 7 of 9; attitude_departure and
aptitude_redesign lightly trimmed for checkbox-length readability
(dropped redundant "in the past 18 months" / "significantly"),
preserving the specific clinical claim in each -- approved copy, see
Decision Register.

Usage:
  python tools/patch_mechanism1_phase2_web_schema_ui.py --dry-run
  python tools/patch_mechanism1_phase2_web_schema_ui.py --write
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
# 1. web/lib/types.ts
# ============================================================================

edit(
    "web/lib/types.ts",
    '''export interface IntakeEcho {
  // string | number is TEMPORARY -- see the Priority Queue's dated
  // follow-up to collapse this to number-only once ShareableOutputPayload's
  // 30-day KV TTL has fully cycled past this deployment and no legacy
  // string-bucket records remain.
  organization_size: string | number;
  industry: string;
  role_level: string;
  tenure_in_role: string;
  direct_reports: string;
  jurisdiction: string;
}
''',
    '''export interface SignificantEventOption {
  value: string;
  label: string;
}

// Canonical significant-events vocabulary -- mirrors engine/data/intake.py's
// PRIOR_ADJUSTERS event_id/event_label pairs. Mechanism 1 (prior-probability
// scoring) was deprecated this session (Decision Register); these 9 values
// now flow through as synthesis-only narrative metadata, never a scoring
// input. Two labels lightly trimmed for checkbox-length readability
// (attitude_departure, aptitude_redesign) -- see Decision Register for the
// approved copy; the other 7 are verbatim. Single source of truth, imported
// by both the intake UI (web/components/DiagnosticFlow.tsx) and server-side
// validation (web/app/api/diagnostic/session/start/route.ts).
export const SIGNIFICANT_EVENT_OPTIONS: readonly SignificantEventOption[] = [
  { value: "acquisition_or_merger", label: "Acquisition or merger" },
  { value: "external_legal_claim", label: "External legal claim or regulatory inquiry" },
  { value: "restructuring_or_layoff", label: "Restructuring or layoff" },
  { value: "rapid_growth", label: "Rapid growth 25%+" },
  { value: "leadership_departure", label: "Leadership departure or transition" },
  { value: "attitude_conduct", label: "A known performance or conduct issue involving a specific individual remains unresolved." },
  { value: "attitude_departure", label: "A termination or unexpected departure revealed something about how the organization operates that you're still addressing." },
  { value: "aptitude_redesign", label: "A role, team, or function was created, redesigned, or eliminated in the past 18 months." },
  { value: "none", label: "None" },
];

export interface IntakeEcho {
  // string | number is TEMPORARY -- see the Priority Queue's dated
  // follow-up to collapse this to number-only once ShareableOutputPayload's
  // 30-day KV TTL has fully cycled past this deployment and no legacy
  // string-bucket records remain.
  organization_size: string | number;
  industry: string;
  role_level: string;
  tenure_in_role: string;
  direct_reports: string;
  jurisdiction: string;
  significant_events: string[];
}
''',
)

# ============================================================================
# 2. web/app/api/diagnostic/session/start/route.ts
# ============================================================================

edit(
    "web/app/api/diagnostic/session/start/route.ts",
    'import type { IntakeEcho } from "@/lib/types";\n',
    'import { SIGNIFICANT_EVENT_OPTIONS, type IntakeEcho } from "@/lib/types";\n'
    '\n'
    'const VALID_SIGNIFICANT_EVENTS = new Set(SIGNIFICANT_EVENT_OPTIONS.map((o) => o.value));\n',
)

edit(
    "web/app/api/diagnostic/session/start/route.ts",
    '''  const validOrgSize =
    (typeof b.organization_size === "number" && Number.isFinite(b.organization_size)) ||
    (typeof b.organization_size === "string" && b.organization_size.length > 0);
  return (
    validOrgSize &&
    typeof b.industry === "string" &&
    typeof b.role_level === "string" &&
    typeof b.tenure_in_role === "string" &&
    typeof b.direct_reports === "string" &&
    typeof b.jurisdiction === "string"
  );
}''',
    '''  const validOrgSize =
    (typeof b.organization_size === "number" && Number.isFinite(b.organization_size)) ||
    (typeof b.organization_size === "string" && b.organization_size.length > 0);
  const validSignificantEvents =
    Array.isArray(b.significant_events) &&
    b.significant_events.length > 0 &&
    b.significant_events.every(
      (v): v is string => typeof v === "string" && VALID_SIGNIFICANT_EVENTS.has(v)
    );
  return (
    validOrgSize &&
    typeof b.industry === "string" &&
    typeof b.role_level === "string" &&
    typeof b.tenure_in_role === "string" &&
    typeof b.direct_reports === "string" &&
    typeof b.jurisdiction === "string" &&
    validSignificantEvents
  );
}''',
)

# ============================================================================
# 3. engine/main.py
# ============================================================================

edit(
    "engine/main.py",
    '''def _locked_intake_to_engine_intake(intake: dict) -> IntakeData:
    """
    Adapts the locked canonical intake schema (Section 5 of the MOB:
    organization_size, industry, role_level, tenure_in_role, direct_reports,
    jurisdiction -- also web/lib/types.ts IntakeEcho) to the engine's
    IntakeData contract (headcount, industry, org_type, jurisdictions,
    significant_events, principal_role).

    Phase 1's intake form does not collect org_type or significant_events --
    neither has a locked-spec equivalent. Both default to values confirmed
    inert for Phase 1 (Session 71 architecture decision, confirmed with Pete
    before this build):
      - org_type defaults to "" -- the org_type_founder_led axis modifier
        (engine/accumulation.py _apply_axis_modifiers) only fires on the
        literal value "Founder-led", so any other string is a safe no-op.
      - significant_events defaults to ["none"] -- no PRIOR_ADJUSTER_INDEX
        entry matches "none" (a no-op for prior initialization, which is
        itself never consumed downstream by rank_states/severity/output --
        see AccumulationEngine.priors), and it means Q03A/Q27A conditional
        routing never fires in Phase 1 -- always the Q03B/Q27B "no
        significant event" branch (see web/lib/session-store.ts
        PHASE_1_QUESTION_SEQUENCE, which hardcodes this same assumption).

    tenure_in_role and direct_reports have no IntakeData equivalent at all --
    stored in the session for calibration/analytics purposes only (Task 1),
    never consumed by engine math.

    Revisit if a richer Phase 2+ intake form ever collects org_type or
    significant_events directly.
    """
    jurisdiction = intake.get("jurisdiction", "")
    return IntakeData(
        headcount=intake.get("organization_size", ""),
        industry=intake.get("industry", ""),
        org_type="",
        jurisdictions=[jurisdiction] if jurisdiction else [],
        significant_events=["none"],
        principal_role=intake.get("role_level", ""),
    )''',
    '''def _locked_intake_to_engine_intake(intake: dict) -> IntakeData:
    """
    Adapts the locked canonical intake schema (Section 5 of the MOB:
    organization_size, industry, role_level, tenure_in_role, direct_reports,
    jurisdiction, significant_events -- also web/lib/types.ts IntakeEcho) to
    the engine's IntakeData contract (headcount, industry, org_type,
    jurisdictions, significant_events, principal_role).

    significant_events is now collected directly by the intake form
    (web/components/DiagnosticFlow.tsx's checkbox multi-select, validated
    server-side against the 9 canonical PRIOR_ADJUSTER_INDEX keys in
    validateIntake()) and passed through here. This session's Mechanism 1
    deprecation (Decision Register) means it no longer drives any scoring
    math -- initialize_priors() (engine/accumulation.py) is now an
    unconditional flat baseline -- but it IS now real, user-submitted
    synthesis-only narrative metadata rather than a hardcoded ["none"]
    default. Falls back to ["none"] only if the field is absent or empty
    (defensive -- the validated web path always sends a non-empty list, but
    this adapter has no way to enforce that on its own callers).

    org_type has no locked-spec intake equivalent -- unrelated to
    significant_events, unchanged: still defaults to "" (Session 71
    architecture decision) -- the org_type_founder_led axis modifier only
    fires on the literal value "Founder-led", so any other string
    (including "") is a safe no-op.

    tenure_in_role and direct_reports have no IntakeData equivalent at all --
    stored in the session for calibration/analytics purposes only (Task 1),
    never consumed by engine math.
    """
    jurisdiction = intake.get("jurisdiction", "")
    return IntakeData(
        headcount=intake.get("organization_size", ""),
        industry=intake.get("industry", ""),
        org_type="",
        jurisdictions=[jurisdiction] if jurisdiction else [],
        significant_events=intake.get("significant_events") or ["none"],
        principal_role=intake.get("role_level", ""),
    )''',
)

# ============================================================================
# 4. web/components/DiagnosticFlow.tsx
# ============================================================================

edit(
    "web/components/DiagnosticFlow.tsx",
    'import type { PrivateOutputPayload } from "@/lib/types";\n',
    'import type { PrivateOutputPayload } from "@/lib/types";\n'
    'import { SIGNIFICANT_EVENT_OPTIONS } from "@/lib/types";\n',
)

edit(
    "web/components/DiagnosticFlow.tsx",
    '''interface IntakeFormState {
  // number once selected; "" is the shared not-yet-selected sentinel,
  // same convention as every other field below.
  organization_size: number | "";
  industry: string;
  role_level: string;
  tenure_in_role: string;
  direct_reports: string;
  jurisdiction: string;
}

const EMPTY_INTAKE: IntakeFormState = {
  organization_size: "",
  industry: "",
  role_level: "",
  tenure_in_role: "",
  direct_reports: "",
  jurisdiction: "",
};''',
    '''interface IntakeFormState {
  // number once selected; "" is the shared not-yet-selected sentinel,
  // same convention as every other field below. significant_events is the
  // one array-valued field -- [] is its own not-yet-selected sentinel,
  // handled separately in isComplete below since [] !== "" trivially.
  organization_size: number | "";
  industry: string;
  role_level: string;
  tenure_in_role: string;
  direct_reports: string;
  jurisdiction: string;
  significant_events: string[];
}

const EMPTY_INTAKE: IntakeFormState = {
  organization_size: "",
  industry: "",
  role_level: "",
  tenure_in_role: "",
  direct_reports: "",
  jurisdiction: "",
  significant_events: [],
};''',
)

edit(
    "web/components/DiagnosticFlow.tsx",
    '  const isComplete = Object.values(intake).every((v) => v !== "");\n',
    '''  // Explicit field-by-field rather than the prior Object.values().every()
  // pattern -- that pattern silently broke once significant_events became
  // array-valued ([] !== "" is trivially true, so it would never have
  // blocked submission on its own).
  const isComplete =
    intake.organization_size !== "" &&
    intake.industry !== "" &&
    intake.role_level !== "" &&
    intake.tenure_in_role !== "" &&
    intake.direct_reports !== "" &&
    intake.jurisdiction !== "" &&
    intake.significant_events.length > 0;
''',
)

edit(
    "web/components/DiagnosticFlow.tsx",
    '''  return (
    <div className="max-w-md mx-auto px-6 py-16">
      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">
        Before you start
      </p>
      <h2 className="font-display text-2xl text-charcoal mb-8">
        A few things about your organization.
      </h2>

      <HeadcountStepper
        value={intake.organization_size}
        onChange={(next) => onChange({ ...intake, organization_size: next })}
      />
      {field("Industry", "industry", INDUSTRY_OPTIONS)}
      {field("Your role level", "role_level", ROLE_LEVEL_OPTIONS)}
      {field("Tenure in this role", "tenure_in_role", TENURE_OPTIONS)}
      {field("Direct reports", "direct_reports", DIRECT_REPORTS_OPTIONS)}
      {field("Primary jurisdiction", "jurisdiction", JURISDICTION_OPTIONS)}

      <button''',
    '''  // None/other-events mutual exclusivity: checking "none" clears any other
  // selections, checking anything else clears "none" -- both being checked
  // simultaneously would be a logical contradiction the data model
  // shouldn't allow.
  function SignificantEventsField({
    value,
    onChange,
  }: {
    value: string[];
    onChange: (next: string[]) => void;
  }) {
    function toggle(eventValue: string) {
      if (eventValue === "none") {
        onChange(value.includes("none") ? [] : ["none"]);
        return;
      }
      const withoutNone = value.filter((v) => v !== "none");
      onChange(
        withoutNone.includes(eventValue)
          ? withoutNone.filter((v) => v !== eventValue)
          : [...withoutNone, eventValue]
      );
    }

    return (
      <div className="mb-5">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Any significant events in the past 18 months?
        </label>
        <div className="space-y-2.5 border border-gray-200 rounded-lg px-3 py-3 bg-white">
          {SIGNIFICANT_EVENT_OPTIONS.map((opt) => (
            <label
              key={opt.value}
              className="flex items-start gap-2 font-ui text-sm text-charcoal cursor-pointer"
            >
              <input
                type="checkbox"
                checked={value.includes(opt.value)}
                onChange={() => toggle(opt.value)}
                className="mt-0.5 shrink-0"
              />
              <span>{opt.label}</span>
            </label>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto px-6 py-16">
      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">
        Before you start
      </p>
      <h2 className="font-display text-2xl text-charcoal mb-8">
        A few things about your organization.
      </h2>

      <HeadcountStepper
        value={intake.organization_size}
        onChange={(next) => onChange({ ...intake, organization_size: next })}
      />
      {field("Industry", "industry", INDUSTRY_OPTIONS)}
      {field("Your role level", "role_level", ROLE_LEVEL_OPTIONS)}
      {field("Tenure in this role", "tenure_in_role", TENURE_OPTIONS)}
      {field("Direct reports", "direct_reports", DIRECT_REPORTS_OPTIONS)}
      {field("Primary jurisdiction", "jurisdiction", JURISDICTION_OPTIONS)}
      <SignificantEventsField
        value={intake.significant_events}
        onChange={(next) => onChange({ ...intake, significant_events: next })}
      />

      <button''',
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

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
