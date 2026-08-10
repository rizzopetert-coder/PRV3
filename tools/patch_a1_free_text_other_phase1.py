"""
PRV3 -- A1 (free-text "Other" elaboration for significant_events), Phase 1
(web/lib/types.ts + the UI + every intermediate type carrying intake data
on the private-only path). Gemini architecture review: CLEARED TO BUILD
WITH STRUCTURAL AIRGAP.

Two of Gemini's specific technical claims were independently verified
against real source before this script was written, per this project's
standing "verify before adopting" discipline:
  1. EVENT_LABEL_LOOKUP (cited by Gemini for engine/output_synthesis.py)
     does not exist anywhere in the repo -- confirmed via repo-wide grep,
     zero hits. The real, already-wired mechanism is PRIOR_ADJUSTER_INDEX
     (engine/data/intake.py), already imported and used in
     output_synthesis.py exactly as the MOB's Mechanism-1-deprecation
     Phase 3 record describes. Phase 2 of this build keys off
     PRIOR_ADJUSTER_INDEX, not the fabricated name.
  2. engine/contract.py's _INTAKE_FIELDS already contains both "headcount"
     and "org_size" as separate real keys -- confirmed via direct read.
     Gemini's listing was accurate here; only significant_event_elaboration
     needs adding (Phase 2), nothing to correct.

Three further corrections found while tracing the real data path, not in
Gemini's condensed summary (same discipline applied to the summary itself,
not just its two flagged items):
  - web/app/api/diagnostic/session/answer/route.ts has no mapIntake()
    function at all -- it passes session.intake straight through
    unchanged. Once DiagnosticSession.intake is typed PrivateIntakeEcho
    (this phase), the field reaches PrivateOutputPayload with zero code
    change there.
  - web/app/api/share/create/route.ts's mapIntake() needs no destructure-
    strip step -- it already builds the shareable object field-by-field
    explicitly, never spreading the engine's raw intake dict, so it
    structurally excludes elaboration already. Only its return-type
    annotation changes (Phase 3).
  - None of Gemini's 3 named phases touch the actual UI. The checkbox +
    free-text box a respondent types into lives in
    web/components/DiagnosticFlow.tsx's SignificantEventsField, added here.

Product decisions confirmed with Pete before writing:
  - Elaboration is REQUIRED when "other" is checked (mirrors the existing
    none/other-events mutual-exclusivity pattern already in this
    component -- an incomplete submission, gated by isComplete, not a
    separate error state).
  - Textarea, 500-char cap (room for a real sentence or two; caps
    synthesis-prompt size).

Scope of this phase: web/lib/types.ts (SIGNIFICANT_EVENT_OPTIONS +
IntakeEcho split into ShareableIntakeEcho / PrivateIntakeEcho + the two
payload types retyped), web/components/DiagnosticFlow.tsx (the actual UI),
and three files that carry intake data on the private-only path end to
end -- web/lib/session-store.ts, web/lib/engine-client.ts,
web/lib/dev-diagnostic-preview.ts -- retyped to PrivateIntakeEcho so the
type system enforces the airgap all the way from browser to Redis to the
engine POST body, not just at the two payload boundaries. Engine-side
(Phase 2) and route-handler-side (Phase 3) changes are separate scripts.

Usage:
  python tools/patch_a1_free_text_other_phase1.py --dry-run
  python tools/patch_a1_free_text_other_phase1.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


TYPES = "web/lib/types.ts"
FLOW = "web/components/DiagnosticFlow.tsx"
STORE = "web/lib/session-store.ts"
CLIENT = "web/lib/engine-client.ts"
DEV_PREVIEW = "web/lib/dev-diagnostic-preview.ts"

# ═══════════════════════════════════════════════════════════════════════
# web/lib/types.ts
# ═══════════════════════════════════════════════════════════════════════

# 1. Add "other" to the canonical vocabulary; update the comment's stale
#    "9 values" count and note the new option isn't in PRIOR_ADJUSTER_INDEX.
edit(
    TYPES,
    '// Canonical significant-events vocabulary -- mirrors engine/data/intake.py\'s\n'
    '// PRIOR_ADJUSTERS event_id/event_label pairs. Mechanism 1 (prior-probability\n'
    '// scoring) was deprecated this session (Decision Register); these 9 values\n'
    '// now flow through as synthesis-only narrative metadata, never a scoring\n'
    '// input. Two labels lightly trimmed for checkbox-length readability\n'
    '// (attitude_departure, aptitude_redesign) -- see Decision Register for the\n'
    '// approved copy; the other 7 are verbatim. Single source of truth, imported\n'
    '// by both the intake UI (web/components/DiagnosticFlow.tsx) and server-side\n'
    '// validation (web/app/api/diagnostic/session/start/route.ts).\n'
    'export const SIGNIFICANT_EVENT_OPTIONS: readonly SignificantEventOption[] = [\n'
    '  { value: "acquisition_or_merger", label: "Acquisition or merger" },\n'
    '  { value: "external_legal_claim", label: "External legal claim or regulatory inquiry" },\n'
    '  { value: "restructuring_or_layoff", label: "Restructuring or layoff" },\n'
    '  { value: "rapid_growth", label: "Rapid growth 25%+" },\n'
    '  { value: "leadership_departure", label: "Leadership departure or transition" },\n'
    '  { value: "attitude_conduct", label: "A known performance or conduct issue involving a specific individual remains unresolved." },\n'
    '  { value: "attitude_departure", label: "A termination or unexpected departure revealed something about how the organization operates that you\'re still addressing." },\n'
    '  { value: "aptitude_redesign", label: "A role, team, or function was created, redesigned, or eliminated in the past 18 months." },\n'
    '  { value: "none", label: "None" },\n'
    '];',
    '// Canonical significant-events vocabulary -- mirrors engine/data/intake.py\'s\n'
    '// PRIOR_ADJUSTERS event_id/event_label pairs. Mechanism 1 (prior-probability\n'
    '// scoring) was deprecated this session (Decision Register); these 10 values\n'
    '// now flow through as synthesis-only narrative metadata, never a scoring\n'
    '// input. Two labels lightly trimmed for checkbox-length readability\n'
    '// (attitude_departure, aptitude_redesign) -- see Decision Register for the\n'
    '// approved copy; the other 7 are verbatim. "other" (A1, this session) has\n'
    '// no PRIOR_ADJUSTER_INDEX counterpart -- it never existed as a Mechanism-1\n'
    '// event type, so engine/output_synthesis.py\'s format_event_for_synthesis()\n'
    '// special-cases it using the free-text significant_event_elaboration field\n'
    '// instead of a lookup label. Single source of truth, imported by both the\n'
    '// intake UI (web/components/DiagnosticFlow.tsx) and server-side validation\n'
    '// (web/app/api/diagnostic/session/start/route.ts).\n'
    'export const SIGNIFICANT_EVENT_OPTIONS: readonly SignificantEventOption[] = [\n'
    '  { value: "acquisition_or_merger", label: "Acquisition or merger" },\n'
    '  { value: "external_legal_claim", label: "External legal claim or regulatory inquiry" },\n'
    '  { value: "restructuring_or_layoff", label: "Restructuring or layoff" },\n'
    '  { value: "rapid_growth", label: "Rapid growth 25%+" },\n'
    '  { value: "leadership_departure", label: "Leadership departure or transition" },\n'
    '  { value: "attitude_conduct", label: "A known performance or conduct issue involving a specific individual remains unresolved." },\n'
    '  { value: "attitude_departure", label: "A termination or unexpected departure revealed something about how the organization operates that you\'re still addressing." },\n'
    '  { value: "aptitude_redesign", label: "A role, team, or function was created, redesigned, or eliminated in the past 18 months." },\n'
    '  { value: "other", label: "Other" },\n'
    '  { value: "none", label: "None" },\n'
    '];',
)

# 2. Split IntakeEcho -> ShareableIntakeEcho / PrivateIntakeEcho.
edit(
    TYPES,
    'export interface IntakeEcho {\n'
    '  // string | number is TEMPORARY -- see the Priority Queue\'s dated\n'
    '  // follow-up to collapse this to number-only once ShareableOutputPayload\'s\n'
    '  // 30-day KV TTL has fully cycled past this deployment and no legacy\n'
    '  // string-bucket records remain.\n'
    '  organization_size: string | number;\n'
    '  industry: string;\n'
    '  role_level: string;\n'
    '  tenure_in_role: string;\n'
    '  direct_reports: string;\n'
    '  jurisdiction: string;\n'
    '  significant_events: string[];\n'
    '}',
    'export interface ShareableIntakeEcho {\n'
    '  // string | number is TEMPORARY -- see the Priority Queue\'s dated\n'
    '  // follow-up to collapse this to number-only once ShareableOutputPayload\'s\n'
    '  // 30-day KV TTL has fully cycled past this deployment and no legacy\n'
    '  // string-bucket records remain.\n'
    '  organization_size: string | number;\n'
    '  industry: string;\n'
    '  role_level: string;\n'
    '  tenure_in_role: string;\n'
    '  direct_reports: string;\n'
    '  jurisdiction: string;\n'
    '  significant_events: string[];\n'
    '}\n'
    '\n'
    '// Private-only superset of ShareableIntakeEcho -- A1 (free-text "Other"\n'
    '// elaboration), Gemini-cleared with a structural airgap: this field exists\n'
    '// on the private type only, never on ShareableIntakeEcho, so the\n'
    '// TypeScript compiler blocks it from ever reaching ShareableOutputPayload\n'
    '// rather than relying on a runtime flag or a strip step. Populated only\n'
    '// when "other" is among significant_events -- the diagnostic UI\n'
    '// (DiagnosticFlow.tsx) requires non-empty elaboration text in that case.\n'
    'export interface PrivateIntakeEcho extends ShareableIntakeEcho {\n'
    '  significant_event_elaboration?: string;\n'
    '}',
)

# 3. PrivateOutputPayload.intake -> PrivateIntakeEcho
edit(
    TYPES,
    '  // Intake echo — all six fields for recognition framing\n'
    '  intake: IntakeEcho;',
    '  // Intake echo — all six fields for recognition framing, plus\n'
    '  // significant_event_elaboration when "other" was selected (private only).\n'
    '  intake: PrivateIntakeEcho;',
)

# 4. ShareableOutputPayload.intake -> ShareableIntakeEcho
edit(
    TYPES,
    '  // Intake echo — grounds friction_tax_estimate math for external audience\n'
    '  intake: IntakeEcho;',
    '  // Intake echo — grounds friction_tax_estimate math for external audience.\n'
    '  // ShareableIntakeEcho specifically -- significant_event_elaboration (if\n'
    '  // any) never reaches this payload, enforced at the type level (see\n'
    '  // PrivateIntakeEcho above).\n'
    '  intake: ShareableIntakeEcho;',
)

# ═══════════════════════════════════════════════════════════════════════
# web/components/DiagnosticFlow.tsx
# ═══════════════════════════════════════════════════════════════════════

# 1. IntakeFormState + EMPTY_INTAKE -- add the elaboration field.
edit(
    FLOW,
    'interface IntakeFormState {\n'
    '  // number once selected; "" is the shared not-yet-selected sentinel,\n'
    '  // same convention as every other field below. significant_events is the\n'
    '  // one array-valued field -- [] is its own not-yet-selected sentinel,\n'
    '  // handled separately in isComplete below since [] !== "" trivially.\n'
    '  organization_size: number | "";\n'
    '  industry: string;\n'
    '  role_level: string;\n'
    '  tenure_in_role: string;\n'
    '  direct_reports: string;\n'
    '  jurisdiction: string;\n'
    '  significant_events: string[];\n'
    '}\n'
    '\n'
    'const EMPTY_INTAKE: IntakeFormState = {\n'
    '  organization_size: "",\n'
    '  industry: "",\n'
    '  role_level: "",\n'
    '  tenure_in_role: "",\n'
    '  direct_reports: "",\n'
    '  jurisdiction: "",\n'
    '  significant_events: [],\n'
    '};',
    'interface IntakeFormState {\n'
    '  // number once selected; "" is the shared not-yet-selected sentinel,\n'
    '  // same convention as every other field below. significant_events is the\n'
    '  // one array-valued field -- [] is its own not-yet-selected sentinel,\n'
    '  // handled separately in isComplete below since [] !== "" trivially.\n'
    '  organization_size: number | "";\n'
    '  industry: string;\n'
    '  role_level: string;\n'
    '  tenure_in_role: string;\n'
    '  direct_reports: string;\n'
    '  jurisdiction: string;\n'
    '  significant_events: string[];\n'
    '  // A1 -- free-text elaboration, required when "other" is among\n'
    '  // significant_events (enforced in isComplete below), ignored otherwise.\n'
    '  significant_event_elaboration: string;\n'
    '}\n'
    '\n'
    'const EMPTY_INTAKE: IntakeFormState = {\n'
    '  organization_size: "",\n'
    '  industry: "",\n'
    '  role_level: "",\n'
    '  tenure_in_role: "",\n'
    '  direct_reports: "",\n'
    '  jurisdiction: "",\n'
    '  significant_events: [],\n'
    '  significant_event_elaboration: "",\n'
    '};',
)

# 2. isComplete gate -- "other" without elaboration blocks submission.
edit(
    FLOW,
    '  const isComplete =\n'
    '    intake.organization_size !== "" &&\n'
    '    intake.industry !== "" &&\n'
    '    intake.role_level !== "" &&\n'
    '    intake.tenure_in_role !== "" &&\n'
    '    intake.direct_reports !== "" &&\n'
    '    intake.jurisdiction !== "" &&\n'
    '    intake.significant_events.length > 0;',
    '  // A1: "other" without elaboration text is an incomplete submission,\n'
    '  // same treatment as any other unfilled required field -- not a\n'
    '  // separate error state.\n'
    '  const otherRequiresElaboration =\n'
    '    !intake.significant_events.includes("other") ||\n'
    '    intake.significant_event_elaboration.trim().length > 0;\n'
    '\n'
    '  const isComplete =\n'
    '    intake.organization_size !== "" &&\n'
    '    intake.industry !== "" &&\n'
    '    intake.role_level !== "" &&\n'
    '    intake.tenure_in_role !== "" &&\n'
    '    intake.direct_reports !== "" &&\n'
    '    intake.jurisdiction !== "" &&\n'
    '    intake.significant_events.length > 0 &&\n'
    '    otherRequiresElaboration;',
)

# 3. SignificantEventsField -- add elaboration prop + conditional textarea.
edit(
    FLOW,
    '  function SignificantEventsField({\n'
    '    value,\n'
    '    onChange,\n'
    '  }: {\n'
    '    value: string[];\n'
    '    onChange: (next: string[]) => void;\n'
    '  }) {\n'
    '    function toggle(eventValue: string) {\n'
    '      if (eventValue === "none") {\n'
    '        onChange(value.includes("none") ? [] : ["none"]);\n'
    '        return;\n'
    '      }\n'
    '      const withoutNone = value.filter((v) => v !== "none");\n'
    '      onChange(\n'
    '        withoutNone.includes(eventValue)\n'
    '          ? withoutNone.filter((v) => v !== eventValue)\n'
    '          : [...withoutNone, eventValue]\n'
    '      );\n'
    '    }\n'
    '\n'
    '    return (\n'
    '      <div className="mb-5">\n'
    '        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">\n'
    '          Any significant events in the past 18 months?\n'
    '        </label>\n'
    '        <div className="space-y-2.5 border border-gray-200 rounded-lg px-3 py-3 bg-white">\n'
    '          {SIGNIFICANT_EVENT_OPTIONS.map((opt) => (\n'
    '            <label\n'
    '              key={opt.value}\n'
    '              className="flex items-start gap-2 font-ui text-sm text-charcoal cursor-pointer"\n'
    '            >\n'
    '              <input\n'
    '                type="checkbox"\n'
    '                checked={value.includes(opt.value)}\n'
    '                onChange={() => toggle(opt.value)}\n'
    '                className="mt-0.5 shrink-0"\n'
    '              />\n'
    '              <span>{opt.label}</span>\n'
    '            </label>\n'
    '          ))}\n'
    '        </div>\n'
    '      </div>\n'
    '    );\n'
    '  }',
    '  function SignificantEventsField({\n'
    '    value,\n'
    '    elaboration,\n'
    '    onChange,\n'
    '    onElaborationChange,\n'
    '  }: {\n'
    '    value: string[];\n'
    '    elaboration: string;\n'
    '    onChange: (next: string[]) => void;\n'
    '    onElaborationChange: (next: string) => void;\n'
    '  }) {\n'
    '    function toggle(eventValue: string) {\n'
    '      if (eventValue === "none") {\n'
    '        onChange(value.includes("none") ? [] : ["none"]);\n'
    '        return;\n'
    '      }\n'
    '      const withoutNone = value.filter((v) => v !== "none");\n'
    '      onChange(\n'
    '        withoutNone.includes(eventValue)\n'
    '          ? withoutNone.filter((v) => v !== eventValue)\n'
    '          : [...withoutNone, eventValue]\n'
    '      );\n'
    '    }\n'
    '\n'
    '    return (\n'
    '      <div className="mb-5">\n'
    '        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">\n'
    '          Any significant events in the past 18 months?\n'
    '        </label>\n'
    '        <div className="space-y-2.5 border border-gray-200 rounded-lg px-3 py-3 bg-white">\n'
    '          {SIGNIFICANT_EVENT_OPTIONS.map((opt) => (\n'
    '            <label\n'
    '              key={opt.value}\n'
    '              className="flex items-start gap-2 font-ui text-sm text-charcoal cursor-pointer"\n'
    '            >\n'
    '              <input\n'
    '                type="checkbox"\n'
    '                checked={value.includes(opt.value)}\n'
    '                onChange={() => toggle(opt.value)}\n'
    '                className="mt-0.5 shrink-0"\n'
    '              />\n'
    '              <span>{opt.label}</span>\n'
    '            </label>\n'
    '          ))}\n'
    '        </div>\n'
    '        {value.includes("other") && (\n'
    '          <textarea\n'
    '            value={elaboration}\n'
    '            onChange={(e) => onElaborationChange(e.target.value)}\n'
    '            maxLength={500}\n'
    '            placeholder="Briefly describe what happened…"\n'
    '            rows={3}\n'
    '            className="mt-2.5 w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal resize-none"\n'
    '          />\n'
    '        )}\n'
    '      </div>\n'
    '    );\n'
    '  }',
)

# 4. Call site -- wire elaboration through.
edit(
    FLOW,
    '      <SignificantEventsField\n'
    '        value={intake.significant_events}\n'
    '        onChange={(next) => onChange({ ...intake, significant_events: next })}\n'
    '      />',
    '      <SignificantEventsField\n'
    '        value={intake.significant_events}\n'
    '        elaboration={intake.significant_event_elaboration}\n'
    '        onChange={(next) => onChange({ ...intake, significant_events: next })}\n'
    '        onElaborationChange={(next) =>\n'
    '          onChange({ ...intake, significant_event_elaboration: next })\n'
    '        }\n'
    '      />',
)

# ═══════════════════════════════════════════════════════════════════════
# web/lib/session-store.ts -- DiagnosticSession carries the full private
# intake (including elaboration) for the session's lifetime.
# ═══════════════════════════════════════════════════════════════════════

edit(
    STORE,
    'import type { IntakeEcho } from "@/lib/types";',
    'import type { PrivateIntakeEcho } from "@/lib/types";',
)

edit(
    STORE,
    '  intake: IntakeEcho;',
    '  intake: PrivateIntakeEcho;',
)

edit(
    STORE,
    'export async function createSession(intake: IntakeEcho): Promise<DiagnosticSession> {',
    'export async function createSession(intake: PrivateIntakeEcho): Promise<DiagnosticSession> {',
)

# ═══════════════════════════════════════════════════════════════════════
# web/lib/engine-client.ts -- both Path 1 payloads to the Python engine
# carry the full private intake.
# ═══════════════════════════════════════════════════════════════════════

edit(
    CLIENT,
    'import type { IntakeEcho, FrictionTaxEstimate, LegalTailRiskExposure } from "@/lib/types";',
    'import type { PrivateIntakeEcho, FrictionTaxEstimate, LegalTailRiskExposure } from "@/lib/types";',
)

edit(
    CLIENT,
    'export interface AccumulatePayload {\n'
    '  accumulated_vector: AccumulatedVector;\n'
    '  question_id: string;\n'
    '  option_id: string;\n'
    '  intake: IntakeEcho;\n'
    '}',
    'export interface AccumulatePayload {\n'
    '  accumulated_vector: AccumulatedVector;\n'
    '  question_id: string;\n'
    '  option_id: string;\n'
    '  intake: PrivateIntakeEcho;\n'
    '}',
)

edit(
    CLIENT,
    'export interface CompletePayload {\n'
    '  accumulated_vector: AccumulatedVector;\n'
    '  intake: IntakeEcho;\n'
    '  answered_question_count: number;',
    'export interface CompletePayload {\n'
    '  accumulated_vector: AccumulatedVector;\n'
    '  intake: PrivateIntakeEcho;\n'
    '  answered_question_count: number;',
)

# ═══════════════════════════════════════════════════════════════════════
# web/lib/dev-diagnostic-preview.ts -- mirrors PrivateOutputPayload's
# shape (same reasoning: dev-only viewer for a real completed session).
# ═══════════════════════════════════════════════════════════════════════

edit(
    DEV_PREVIEW,
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
    'import type {\n'
    '  SynthesisFields,\n'
    '  StateRef,\n'
    '  SeverityTier,\n'
    '  ResolutionFamily,\n'
    '  FrictionTaxEstimate,\n'
    '  LegalTailRiskExposure,\n'
    '  PrivateIntakeEcho,\n'
    '  DimensionSummary,\n'
    '} from "@/lib/types";',
)

edit(
    DEV_PREVIEW,
    '  intake: IntakeEcho;',
    '  intake: PrivateIntakeEcho;',
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
