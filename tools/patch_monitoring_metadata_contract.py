#!/usr/bin/env python
"""
PRV3 -- patch_monitoring_metadata_contract.py
Patches engine/contract.py with monitoring_metadata support (Session 11, Task 2).

Changes applied:
  1. ENGINE_VERSION: 0.1.0 -> 0.2.0
  2. SessionData: adds q_signal_decision_blindness: bool = False
  3. Adds _PROTECTED_ACTIVITY_INTAKE_EVENTS, _DB_* constants
  4. Adds _assemble_monitoring_metadata() helper before assemble_output()
  5. assemble_output() return dict: adds "monitoring_metadata" (14 fields total)
  6. _TOP_LEVEL_SCHEMA: adds "monitoring_metadata": dict
  7. Adds _MONITORING_METADATA_FIELDS and _FLAG_REQUIRED_FIELDS constants
  8. validate_schema(): adds monitoring_metadata sub-field validation
  9. validate_schema() docstring: 13 -> 14 top-level fields

Usage:
  python tools/patch_monitoring_metadata_contract.py --dry-run
  python tools/patch_monitoring_metadata_contract.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "contract.py"

# ---------------------------------------------------------------------------
# Change 1: ENGINE_VERSION bump
# ---------------------------------------------------------------------------
OLD_VERSION = 'ENGINE_VERSION: str = "0.1.0"  # Incremented at each build milestone'
NEW_VERSION = 'ENGINE_VERSION: str = "0.2.0"  # Incremented at each build milestone'

# ---------------------------------------------------------------------------
# Change 2: SessionData -- add q_signal_decision_blindness field
# ---------------------------------------------------------------------------
OLD_SESSION_TAIL = '''\
    checkpoint_q11:      Optional[CheckpointResult] = None
    checkpoint_q19:      Optional[CheckpointResult] = None
    checkpoint_q27:      Optional[CheckpointResult] = None

    @staticmethod'''
NEW_SESSION_TAIL = '''\
    checkpoint_q11:      Optional[CheckpointResult] = None
    checkpoint_q19:      Optional[CheckpointResult] = None
    checkpoint_q27:      Optional[CheckpointResult] = None

    q_signal_decision_blindness: bool = False

    @staticmethod'''

# ---------------------------------------------------------------------------
# Change 3+4: constants + _assemble_monitoring_metadata() before assemble_output()
# Inserted immediately before def assemble_output (unique signature in file).
# ---------------------------------------------------------------------------
OLD_BEFORE_ASSEMBLY = "def assemble_output(session: SessionData) -> dict:"

NEW_BEFORE_ASSEMBLY = '''\
# ── monitoring_metadata constants ─────────────────────────────────────────────

_PROTECTED_ACTIVITY_INTAKE_EVENTS = frozenset(["external_legal_matter"])

_DB_FLAG_ID = "decision_blindness_protected_activity"
_DB_SEVERITY_FLOOR = "entrenched"
_DB_RECOMMENDED_ROUTES = ["executive_counsel", "intervention"]
_DB_INTERNAL_NOTE = (
    "Decision Blindness signal present with confirmed protected activity context. "
    "Prioritize engagement review before diagnostic output is shared."
)


def _assemble_monitoring_metadata(session: SessionData) -> dict:
    """
    Assemble monitoring_metadata for one scoring session.

    Always present in engine output. Excluded from shareable output package.

    Decision Blindness protected-activity flag (decision_blindness_protected_activity)
    fires when both conditions are met:
      (1) decision_blindness score >= noise_baseline for that state
      (2) protected activity confirmed from at least one source:
            intake_significant_events: significant_events contains a protected
                                       activity event (e.g. external_legal_matter)
            q_signal:                  session.q_signal_decision_blindness is True
                                       (set by session orchestrator from Q06 answers)

    Flag is always present in the flags list. triggered=True only when both
    conditions are met. priority is always "high" for this flag type.
    any_high_priority reflects whether any triggered flag carries high priority.

    Spec reference: Section VII.1 -- monitoring_metadata
    """
    db_entry = next(
        (qs for qs in session.output_package.routing.all_evaluated
         if qs.state_id == "decision_blindness"),
        None,
    )
    db_score = db_entry.score if db_entry else 0.0
    db_noise = db_entry.noise_baseline if db_entry else 0.0
    db_above_baseline = db_score >= db_noise

    pa_sources = []
    if any(e in _PROTECTED_ACTIVITY_INTAKE_EVENTS
           for e in session.intake.significant_events):
        pa_sources.append("intake_significant_events")
    if session.q_signal_decision_blindness:
        pa_sources.append("q_signal")

    protected_activity_confirmed = len(pa_sources) > 0
    flag_triggered = db_above_baseline and protected_activity_confirmed

    db_flag = {
        "flag_id":   _DB_FLAG_ID,
        "triggered": flag_triggered,
        "trigger_conditions": {
            "state_id":                    "decision_blindness",
            "score_at_trigger":            round(db_score, 6),
            "score_threshold":             "noise_baseline",
            "protected_activity_confirmed": protected_activity_confirmed,
            "protected_activity_sources":   pa_sources,
        },
        "severity_context": {
            "decision_blindness_severity_floor": _DB_SEVERITY_FLOOR,
            "current_severity_reading": (
                session.severity_result.tier.lower()
                if session.severity_result.tier else ""
            ),
        },
        "recommended_routes":           list(_DB_RECOMMENDED_ROUTES),
        "priority":                     "high",
        "internal_note":                _DB_INTERNAL_NOTE,
        "visible_to_principal":         False,
        "visible_to_resolution_specialist": True,
    }

    flags = [db_flag]
    return {
        "flags":            flags,
        "flag_count":       len(flags),
        "any_high_priority": any(
            f["triggered"] and f["priority"] == "high" for f in flags
        ),
    }


def assemble_output(session: SessionData) -> dict:'''

# ---------------------------------------------------------------------------
# Change 5: assemble_output() return dict -- add monitoring_metadata
# ---------------------------------------------------------------------------
OLD_RETURN_DICT = '''\
    return {
        "session_id":          session.session_id,
        "intake":              intake_obj,
        "state_distribution":  state_distribution,
        "output_type":         output_type,
        "identified_states":   identified_states,
        "severity":            severity_obj,
        "asset_score":         asset_obj,
        "narrative_modulation": narrative_obj,
        "checkpoint_log":      checkpoint_log,
        "jurisdiction_flags":  jurisdiction_flags,
        "private_output":      private_output,
        "shareable_output":    shareable_output,
        "engine_version":      ENGINE_VERSION,
    }'''

NEW_RETURN_DICT = '''\
    return {
        "session_id":          session.session_id,
        "intake":              intake_obj,
        "state_distribution":  state_distribution,
        "output_type":         output_type,
        "identified_states":   identified_states,
        "severity":            severity_obj,
        "asset_score":         asset_obj,
        "narrative_modulation": narrative_obj,
        "checkpoint_log":      checkpoint_log,
        "jurisdiction_flags":  jurisdiction_flags,
        "private_output":      private_output,
        "shareable_output":    shareable_output,
        "engine_version":      ENGINE_VERSION,
        "monitoring_metadata": _assemble_monitoring_metadata(session),
    }'''

# ---------------------------------------------------------------------------
# Change 6: _TOP_LEVEL_SCHEMA -- add monitoring_metadata
# ---------------------------------------------------------------------------
OLD_TOP_SCHEMA = '''\
_TOP_LEVEL_SCHEMA: dict[str, type] = {
    "session_id":          str,
    "intake":              dict,
    "state_distribution":  list,
    "output_type":         str,
    "identified_states":   list,
    "severity":            dict,
    "asset_score":         dict,
    "narrative_modulation": dict,
    "checkpoint_log":      dict,
    "jurisdiction_flags":  dict,
    "private_output":      dict,
    "shareable_output":    dict,
    "engine_version":      str,
}'''

NEW_TOP_SCHEMA = '''\
_TOP_LEVEL_SCHEMA: dict[str, type] = {
    "session_id":          str,
    "intake":              dict,
    "state_distribution":  list,
    "output_type":         str,
    "identified_states":   list,
    "severity":            dict,
    "asset_score":         dict,
    "narrative_modulation": dict,
    "checkpoint_log":      dict,
    "jurisdiction_flags":  dict,
    "private_output":      dict,
    "shareable_output":    dict,
    "engine_version":      str,
    "monitoring_metadata": dict,
}'''

# ---------------------------------------------------------------------------
# Change 7: add _MONITORING_METADATA_FIELDS and _FLAG_REQUIRED_FIELDS after
#           _INTAKE_FIELDS
# ---------------------------------------------------------------------------
OLD_INTAKE_FIELDS = '''\
_INTAKE_FIELDS = {
    "headcount", "industry", "org_type",
    "jurisdictions", "significant_events", "principal_role",
}'''

NEW_INTAKE_FIELDS = '''\
_INTAKE_FIELDS = {
    "headcount", "industry", "org_type",
    "jurisdictions", "significant_events", "principal_role",
}

_MONITORING_METADATA_FIELDS = {"flags", "flag_count", "any_high_priority"}

_FLAG_REQUIRED_FIELDS = {
    "flag_id", "triggered", "trigger_conditions", "severity_context",
    "recommended_routes", "priority", "internal_note",
    "visible_to_principal", "visible_to_resolution_specialist",
}'''

# ---------------------------------------------------------------------------
# Change 8: validate_schema() -- add monitoring_metadata validation
# ---------------------------------------------------------------------------
OLD_VALIDATE_END = '''\
    # intake echo fields
    for f in _INTAKE_FIELDS:
        if f not in output["intake"]:
            violations.append(f"intake MISSING field {f!r}")

    return violations'''

NEW_VALIDATE_END = '''\
    # intake echo fields
    for f in _INTAKE_FIELDS:
        if f not in output["intake"]:
            violations.append(f"intake MISSING field {f!r}")

    # monitoring_metadata
    mm = output["monitoring_metadata"]
    for f in _MONITORING_METADATA_FIELDS:
        if f not in mm:
            violations.append(f"monitoring_metadata MISSING field {f!r}")
    for i, flag in enumerate(mm.get("flags", [])):
        for f in _FLAG_REQUIRED_FIELDS:
            if f not in flag:
                violations.append(
                    f"monitoring_metadata.flags[{i}] MISSING field {f!r}"
                )

    return violations'''

# ---------------------------------------------------------------------------
# Change 9: validate_schema() docstring -- 13 -> 14
# ---------------------------------------------------------------------------
OLD_VALIDATE_DOC = "      - All 13 top-level fields present with correct types"
NEW_VALIDATE_DOC = "      - All 14 top-level fields present with correct types"


CHANGES = [
    ("ENGINE_VERSION bump",              OLD_VERSION,          NEW_VERSION),
    ("SessionData: q_signal field",      OLD_SESSION_TAIL,     NEW_SESSION_TAIL),
    ("monitoring_metadata helper",       OLD_BEFORE_ASSEMBLY,  NEW_BEFORE_ASSEMBLY),
    ("assemble_output return dict",      OLD_RETURN_DICT,      NEW_RETURN_DICT),
    ("_TOP_LEVEL_SCHEMA",                OLD_TOP_SCHEMA,       NEW_TOP_SCHEMA),
    ("_INTAKE_FIELDS + new constants",   OLD_INTAKE_FIELDS,    NEW_INTAKE_FIELDS),
    ("validate_schema end",              OLD_VALIDATE_END,     NEW_VALIDATE_END),
    ("validate_schema docstring",        OLD_VALIDATE_DOC,     NEW_VALIDATE_DOC),
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Patch engine/contract.py with monitoring_metadata support"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.print_help()
        sys.exit(1)

    if not TARGET.exists():
        print(f"ERROR: target not found: {TARGET}")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8")

    if args.dry_run:
        print(f"DRY RUN -- target: {TARGET}")
        print(f"  {len(CHANGES)} changes to apply:")
        all_ok = True
        for label, old, new in CHANGES:
            found = old in text
            status = "OK  " if found else "MISS"
            if not found:
                all_ok = False
            print(f"  [{status}] {label}")
        if not all_ok:
            print("\n  ERROR: one or more OLD strings not found in target.")
            sys.exit(1)
        print("\n  Summary of changes:")
        print("    ENGINE_VERSION: 0.1.0 -> 0.2.0")
        print("    SessionData: +q_signal_decision_blindness: bool = False")
        print("    New constants: _PROTECTED_ACTIVITY_INTAKE_EVENTS, _DB_FLAG_ID, etc.")
        print("    New function: _assemble_monitoring_metadata(session) -> dict")
        print("    assemble_output() return: 13 fields -> 14 fields")
        print("    _TOP_LEVEL_SCHEMA: 13 entries -> 14 entries")
        print("    New constants: _MONITORING_METADATA_FIELDS, _FLAG_REQUIRED_FIELDS")
        print("    validate_schema(): monitoring_metadata sub-field validation added")
        print("    validate_schema() docstring: 13 -> 14 top-level fields")
        return

    # Verify all OLD strings present before writing
    for label, old, new in CHANGES:
        if old not in text:
            print(f"ERROR: OLD string not found for '{label}' -- aborting.")
            sys.exit(1)

    new_text = text
    for label, old, new in CHANGES:
        new_text = new_text.replace(old, new, 1)

    if new_text == text:
        print("ERROR: no changes produced.")
        sys.exit(1)

    TARGET.write_text(new_text, encoding="utf-8")
    print(f"WRITTEN: {TARGET}")
    print(f"  {len(CHANGES)} changes applied")
    print("  ENGINE_VERSION: 0.1.0 -> 0.2.0")
    print("  monitoring_metadata: assembled and validated")


if __name__ == "__main__":
    main()
