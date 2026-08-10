"""
PRV3 -- A1 (free-text "Other" elaboration for significant_events), Phase 2
(engine/). Gemini architecture review: CLEARED TO BUILD WITH STRUCTURAL
AIRGAP. See tools/patch_a1_free_text_other_phase1.py's docstring for the
two Gemini claims independently verified before this build (EVENT_LABEL_
LOOKUP does not exist -- the real mechanism is PRIOR_ADJUSTER_INDEX; the
_INTAKE_FIELDS org_size/headcount question checked out accurate).

Necessary plumbing not explicitly named in Gemini's phase list (which only
called out engine/contract.py and engine/output_synthesis.py) but required
for the field to actually reach either of those two named touch points:
significant_event_elaboration has to exist on IntakeData
(engine/accumulation.py) and be populated at both of its construction
sites (engine/main.py -- Path 1's _locked_intake_to_engine_intake() and
Path B's run_engine()) before contract.py's assemble_output() can echo it
or output_synthesis.py can read it.

"other" is deliberately NOT added to PRIOR_ADJUSTER_INDEX
(engine/data/intake.py) -- it never existed as a Mechanism-1 event type,
so a PriorAdjuster entry for it would need fabricated elevated_states/
multiplier values for a mechanism already confirmed dead. Handled instead
as a special case in the new format_event_for_synthesis(), using the
respondent's own elaboration text in place of a lookup label.

Path B (run_engine()) uses .get() with an empty-string default for the
new field, not bracket access like its five sibling keys -- Path B's
camelCase payload shape predates this field and no existing caller sends
significantEventElaboration; requiring it would break every existing
Path B caller for a field that path's UI doesn't even collect.

Usage:
  python tools/patch_a1_free_text_other_phase2.py --dry-run
  python tools/patch_a1_free_text_other_phase2.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


ACCUMULATION = "engine/accumulation.py"
MAIN = "engine/main.py"
CONTRACT = "engine/contract.py"
SYNTHESIS = "engine/output_synthesis.py"

# ═══════════════════════════════════════════════════════════════════════
# engine/accumulation.py -- IntakeData gains the 7th field, defaulted so
# every existing constructor call (Path B, calibration_runner.py, tests)
# keeps working unchanged.
# ═══════════════════════════════════════════════════════════════════════

edit(
    ACCUMULATION,
    '    Complete intake form result. All six intake fields.\n'
    '    Spec reference: Section I.3\n'
    '    """\n'
    '    headcount:          int   # precise headcount (engine/data/intake.py\'s HEADCOUNT_FIELD_SPEC)\n'
    '    industry:           str   # from INTAKE_FIELDS["industry"]\n'
    '    org_type:           str   # from INTAKE_FIELDS["org_type"]\n'
    '    jurisdictions:      list  # list of state abbreviations, e.g. ["CA", "TX"]\n'
    '    significant_events: list  # list of event_ids\n'
    '    principal_role:     str   # from INTAKE_FIELDS["principal_role"]',
    '    Complete intake form result. Six locked intake fields plus one\n'
    '    optional field (A1, this session).\n'
    '    Spec reference: Section I.3\n'
    '    """\n'
    '    headcount:          int   # precise headcount (engine/data/intake.py\'s HEADCOUNT_FIELD_SPEC)\n'
    '    industry:           str   # from INTAKE_FIELDS["industry"]\n'
    '    org_type:           str   # from INTAKE_FIELDS["org_type"]\n'
    '    jurisdictions:      list  # list of state abbreviations, e.g. ["CA", "TX"]\n'
    '    significant_events: list  # list of event_ids\n'
    '    principal_role:     str   # from INTAKE_FIELDS["principal_role"]\n'
    '    # A1 -- free-text elaboration, populated only when "other" is among\n'
    '    # significant_events. Synthesis-only narrative metadata, same as\n'
    '    # significant_events itself post-Mechanism-1-deprecation -- never a\n'
    '    # scoring input. Defaulted so every pre-existing IntakeData\n'
    '    # constructor call (Path B, calibration_runner.py, tests) keeps\n'
    '    # working unchanged.\n'
    '    significant_event_elaboration: str = ""',
)

# ═══════════════════════════════════════════════════════════════════════
# engine/main.py -- both IntakeData construction sites.
# ═══════════════════════════════════════════════════════════════════════

# Path B (run_engine()) -- .get() with a safe default; existing callers
# never send this key.
edit(
    MAIN,
    '    intake_data = IntakeData(\n'
    '        headcount=intake_dict["headcount"],\n'
    '        industry=intake_dict["industry"],\n'
    '        org_type=intake_dict["orgType"],\n'
    '        jurisdictions=intake_dict["jurisdictions"],\n'
    '        significant_events=intake_dict["significantEvents"],\n'
    '        principal_role=intake_dict["principalRole"],\n'
    '    )',
    '    intake_data = IntakeData(\n'
    '        headcount=intake_dict["headcount"],\n'
    '        industry=intake_dict["industry"],\n'
    '        org_type=intake_dict["orgType"],\n'
    '        jurisdictions=intake_dict["jurisdictions"],\n'
    '        significant_events=intake_dict["significantEvents"],\n'
    '        principal_role=intake_dict["principalRole"],\n'
    '        # A1 -- optional, .get() not bracket access: this camelCase\n'
    '        # payload shape predates the field and Path B\'s UI doesn\'t\n'
    '        # collect it, so no existing caller sends it.\n'
    '        significant_event_elaboration=intake_dict.get("significantEventElaboration", ""),\n'
    '    )',
)

# Path 1 (_locked_intake_to_engine_intake()) -- the field the live
# diagnostic UI actually populates.
edit(
    MAIN,
    '        significant_events=intake.get("significant_events") or ["none"],\n'
    '        principal_role=intake.get("role_level", ""),',
    '        significant_events=intake.get("significant_events") or ["none"],\n'
    '        principal_role=intake.get("role_level", ""),\n'
    '        # A1 -- free-text elaboration, present only when "other" was\n'
    '        # selected in the checkbox multi-select (validated server-side\n'
    '        # in validateIntake(), required non-empty when "other" is\n'
    '        # selected).\n'
    '        significant_event_elaboration=intake.get("significant_event_elaboration", ""),',
)

# ═══════════════════════════════════════════════════════════════════════
# engine/contract.py -- _INTAKE_FIELDS gains the key; intake_obj echoes it.
# ═══════════════════════════════════════════════════════════════════════

edit(
    CONTRACT,
    '_INTAKE_FIELDS = {\n'
    '    "headcount", "org_size", "industry", "org_type",\n'
    '    "jurisdictions", "significant_events", "principal_role",\n'
    '}',
    '_INTAKE_FIELDS = {\n'
    '    "headcount", "org_size", "industry", "org_type",\n'
    '    "jurisdictions", "significant_events", "principal_role",\n'
    '    "significant_event_elaboration",\n'
    '}',
)

edit(
    CONTRACT,
    '    intake_obj = {\n'
    '        "headcount":          session.intake.headcount,\n'
    '        "org_size":           session.intake.headcount,   # org_size band — resolved by friction_tax\n'
    '        "industry":           session.intake.industry,\n'
    '        "org_type":           session.intake.org_type,\n'
    '        "jurisdictions":      list(session.intake.jurisdictions),\n'
    '        "significant_events": list(session.intake.significant_events),\n'
    '        "principal_role":     session.intake.principal_role,',
    '    intake_obj = {\n'
    '        "headcount":          session.intake.headcount,\n'
    '        "org_size":           session.intake.headcount,   # org_size band — resolved by friction_tax\n'
    '        "industry":           session.intake.industry,\n'
    '        "org_type":           session.intake.org_type,\n'
    '        "jurisdictions":      list(session.intake.jurisdictions),\n'
    '        "significant_events": list(session.intake.significant_events),\n'
    '        "principal_role":     session.intake.principal_role,\n'
    '        "significant_event_elaboration": session.intake.significant_event_elaboration,',
)

# ═══════════════════════════════════════════════════════════════════════
# engine/output_synthesis.py -- format_event_for_synthesis(), keyed off
# the real PRIOR_ADJUSTER_INDEX (not the fabricated EVENT_LABEL_LOOKUP),
# special-cased for "other". Wired into _build_synthesis_prompt()'s event
# loop.
# ═══════════════════════════════════════════════════════════════════════

edit(
    SYNTHESIS,
    '# ── LLM call ──────────────────────────────────────────────────────────────────\n'
    '\n'
    'def _build_synthesis_prompt(',
    '# ── LLM call ──────────────────────────────────────────────────────────────────\n'
    '\n'
    'def format_event_for_synthesis(event_id: str, elaboration: str) -> Optional[str]:\n'
    '    """\n'
    '    Maps a single significant_events entry to its synthesis-prompt label.\n'
    '\n'
    '    "none" returns None (nothing to render). Any of the 8 real Mechanism-1\n'
    '    event types returns PRIOR_ADJUSTER_INDEX\'s full, untrimmed clinical\n'
    '    label. "other" (A1, this session) has no PRIOR_ADJUSTER_INDEX\n'
    '    counterpart -- it never existed as a Mechanism-1 event type -- so it\n'
    '    is special-cased here using the respondent\'s own elaboration text\n'
    '    instead of a lookup label, falling back to None if elaboration is\n'
    '    empty or whitespace-only (a defensive floor; the web UI already\n'
    '    requires non-empty elaboration whenever "other" is selected).\n'
    '    Any other unrecognized id also returns None, same as an absent\n'
    '    PRIOR_ADJUSTER_INDEX entry always has.\n'
    '    """\n'
    '    if event_id == "none":\n'
    '        return None\n'
    '    if event_id == "other":\n'
    '        stripped = elaboration.strip()\n'
    '        return stripped if stripped else None\n'
    '    adjuster = PRIOR_ADJUSTER_INDEX.get(event_id)\n'
    '    return adjuster.event_label if adjuster else None\n'
    '\n'
    '\n'
    'def _build_synthesis_prompt(',
)

edit(
    SYNTHESIS,
    '    # significant_events is now real, user-submitted synthesis-only\n'
    '    # narrative metadata (Mechanism 1 deprecation, this session -- Decision\n'
    '    # Register). Mapped through PRIOR_ADJUSTER_INDEX\'s full, untrimmed\n'
    '    # clinical text (not web/lib/types.ts\'s SIGNIFICANT_EVENT_OPTIONS\n'
    '    # checkbox-trimmed copy -- no UI-space constraint here, and the fuller\n'
    '    # specificity gives Sonnet more to ground the narrative in). Omitted\n'
    '    # entirely when missing, empty, or exactly ["none"] -- a literal\n'
    '    # "None" or empty section would read as an unknown value rather than\n'
    '    # "nothing significant happened."\n'
    '    significant_events = intake.get("significant_events") or []\n'
    '    event_labels = [\n'
    '        PRIOR_ADJUSTER_INDEX[e].event_label\n'
    '        for e in significant_events\n'
    '        if e != "none" and e in PRIOR_ADJUSTER_INDEX\n'
    '    ]',
    '    # significant_events is now real, user-submitted synthesis-only\n'
    '    # narrative metadata (Mechanism 1 deprecation, this session -- Decision\n'
    '    # Register). Mapped through format_event_for_synthesis() -- for the 8\n'
    '    # real Mechanism-1 event types, PRIOR_ADJUSTER_INDEX\'s full, untrimmed\n'
    '    # clinical text (not web/lib/types.ts\'s SIGNIFICANT_EVENT_OPTIONS\n'
    '    # checkbox-trimmed copy -- no UI-space constraint here, and the fuller\n'
    '    # specificity gives Sonnet more to ground the narrative in); for\n'
    '    # "other" (A1), the respondent\'s own free-text elaboration instead.\n'
    '    # Omitted entirely when missing, empty, or exactly ["none"] -- a\n'
    '    # literal "None" or empty section would read as an unknown value\n'
    '    # rather than "nothing significant happened."\n'
    '    significant_events = intake.get("significant_events") or []\n'
    '    elaboration = intake.get("significant_event_elaboration") or ""\n'
    '    event_labels = []\n'
    '    for e in significant_events:\n'
    '        label = format_event_for_synthesis(e, elaboration)\n'
    '        if label is not None:\n'
    '            event_labels.append(label)',
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
