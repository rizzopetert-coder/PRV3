#!/usr/bin/env python
"""
PRV3 -- patch_monitoring_metadata_tests.py
Patches tools/test_contract.py with monitoring_metadata test coverage (Session 11, Task 2).

Changes applied:
  1. Section 1: expected_fields list +monitoring_metadata; count 13->14
  2. Section 3: adds violation test for missing monitoring_metadata.flag_count
  3. Section 19 (new): 27 monitoring_metadata tests
     Structure, flag fields, trigger conditions, firing logic (4 scenarios)

New test count: 95 + 29 = 124 tests in test_contract.py
Total engine tests after patch: 363 + 29 = 392

Usage:
  python tools/patch_monitoring_metadata_tests.py --dry-run
  python tools/patch_monitoring_metadata_tests.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "tools" / "test_contract.py"

# ---------------------------------------------------------------------------
# Change 1: Section 1 -- expected_fields + count check
# ---------------------------------------------------------------------------
OLD_EXPECTED_FIELDS = '''\
expected_fields = [
    "session_id", "intake", "state_distribution", "output_type",
    "identified_states", "severity", "asset_score", "narrative_modulation",
    "checkpoint_log", "jurisdiction_flags", "private_output",
    "shareable_output", "engine_version",
]
for f in expected_fields:
    check(f"Field {f!r} present", f in output, f"missing from output")
check("Exactly 13 top-level fields", len(output) == 13, f"got {len(output)}")'''

NEW_EXPECTED_FIELDS = '''\
expected_fields = [
    "session_id", "intake", "state_distribution", "output_type",
    "identified_states", "severity", "asset_score", "narrative_modulation",
    "checkpoint_log", "jurisdiction_flags", "private_output",
    "shareable_output", "engine_version", "monitoring_metadata",
]
for f in expected_fields:
    check(f"Field {f!r} present", f in output, f"missing from output")
check("Exactly 14 top-level fields", len(output) == 14, f"got {len(output)}")'''

# ---------------------------------------------------------------------------
# Change 2: Section 3 -- add monitoring_metadata violation test
# (inserted after the existing checkpoint sub-field test)
# ---------------------------------------------------------------------------
OLD_CHECKPOINT_TEST = '''\
# Missing checkpoint sub-field
bad_cp = copy.deepcopy(output)
del bad_cp["checkpoint_log"]["q11"]["entropy"]
v_cp = validate_schema(bad_cp)
check("Missing checkpoint_log.q11.entropy detected",
      any("q11" in v and "entropy" in v for v in v_cp),
      f"got: {v_cp}")'''

NEW_CHECKPOINT_TEST = '''\
# Missing checkpoint sub-field
bad_cp = copy.deepcopy(output)
del bad_cp["checkpoint_log"]["q11"]["entropy"]
v_cp = validate_schema(bad_cp)
check("Missing checkpoint_log.q11.entropy detected",
      any("q11" in v and "entropy" in v for v in v_cp),
      f"got: {v_cp}")

# Missing monitoring_metadata sub-field
bad_mm = copy.deepcopy(output)
del bad_mm["monitoring_metadata"]["flag_count"]
v_mm = validate_schema(bad_mm)
check("Missing monitoring_metadata.flag_count detected",
      any("monitoring_metadata" in v and "flag_count" in v for v in v_mm),
      f"got: {v_mm}")'''

# ---------------------------------------------------------------------------
# Change 3: Section 19 (new) + updated summary section
# Replaces the existing summary block with section 19 + summary.
# ---------------------------------------------------------------------------
OLD_SUMMARY = '''\
# ── Summary ────────────────────────────────────────────────────────────────────
print("\\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\\nAll checks passed. Section VII output contract is structurally valid.")
print("=" * 64)

sys.exit(1 if FAIL else 0)'''

NEW_SUMMARY = '''\
# ── 19. monitoring_metadata ────────────────────────────────────────────────────
print("\\n19. monitoring_metadata")

mm = output.get("monitoring_metadata", {})

# Structure
check("monitoring_metadata present in output",
      "monitoring_metadata" in output)
check("monitoring_metadata.flags is a list",
      isinstance(mm.get("flags"), list))
check("monitoring_metadata.flag_count is int",
      isinstance(mm.get("flag_count"), int))
check("monitoring_metadata.any_high_priority is bool",
      isinstance(mm.get("any_high_priority"), bool))
check("monitoring_metadata.flag_count equals len(flags)",
      mm.get("flag_count") == len(mm.get("flags", [])))
check("monitoring_metadata has exactly 1 flag (Phase 1)",
      len(mm.get("flags", [])) == 1,
      f"got {len(mm.get('flags', []))}")

# Flag field structure (using existing session with none intake)
flag0 = mm["flags"][0] if mm.get("flags") else {}
check("flag.flag_id correct",
      flag0.get("flag_id") == "decision_blindness_protected_activity")
check("flag.triggered is bool",
      isinstance(flag0.get("triggered"), bool))
check("flag.trigger_conditions is dict",
      isinstance(flag0.get("trigger_conditions"), dict))
check("flag.severity_context is dict",
      isinstance(flag0.get("severity_context"), dict))
check("flag.recommended_routes is list",
      isinstance(flag0.get("recommended_routes"), list))
check("flag.priority is str",
      isinstance(flag0.get("priority"), str))
check("flag.internal_note is str",
      isinstance(flag0.get("internal_note"), str))
check("flag.visible_to_principal is False",
      flag0.get("visible_to_principal") is False)
check("flag.visible_to_resolution_specialist is True",
      flag0.get("visible_to_resolution_specialist") is True)

# trigger_conditions sub-fields
tc0 = flag0.get("trigger_conditions", {})
check("trigger_conditions.state_id is decision_blindness",
      tc0.get("state_id") == "decision_blindness")
check("trigger_conditions.score_threshold is noise_baseline",
      tc0.get("score_threshold") == "noise_baseline")
check("trigger_conditions.protected_activity_sources is list",
      isinstance(tc0.get("protected_activity_sources"), list))

# With none intake + q_signal=False: flag should not be triggered
check("flag not triggered with none intake and no q_signal",
      flag0.get("triggered") is False,
      f"triggered={flag0.get('triggered')}")


# ── Firing condition tests ────────────────────────────────────────────────────

def _make_db_session(intake_events, q_signal=False, db_score_mult=1.1):
    """
    Session where decision_blindness has score = db_score_mult * noise_baseline.
    db_score_mult > 1.0  -> DB above baseline -> condition (1) met.
    db_score_mult < 1.0  -> DB below baseline -> condition (1) not met.
    """
    from engine.accumulation import IntakeData, StateRanking
    from engine.contract import SessionData
    pa_intake = IntakeData(
        headcount="100-249",
        industry="Technology",
        org_type="PE or VC-backed",
        jurisdictions=["CA"],
        significant_events=intake_events,
        principal_role="C-suite",
    )
    db_score = baseline_score * db_score_mult
    other_score = baseline_score * 0.5
    db_rankings = []
    for i, sid in enumerate(STATE_PROFILES):
        s = db_score if sid == "decision_blindness" else other_score
        db_rankings.append(StateRanking(rank=i+1, state_id=sid, distance=0.3, score=s))
    db_rankings.sort(key=lambda r: -r.score)
    for i, r in enumerate(db_rankings):
        r.rank = i + 1
    db_pkg = out_engine.build(db_rankings, sev)
    return SessionData(
        session_id=SessionData.new_session_id(),
        intake=pa_intake,
        final_rankings=db_rankings,
        accumulated_vector=acc_vector,
        output_package=db_pkg,
        severity_result=sev,
        q_signal_decision_blindness=q_signal,
    )


# Scenario A: DB above baseline + external_legal_matter -> triggered
sess_a = _make_db_session(["external_legal_matter"])
out_a = assemble_output(sess_a)
mm_a = out_a.get("monitoring_metadata", {})
flag_a = mm_a["flags"][0] if mm_a.get("flags") else {}
check("Scenario A: flag triggered (DB above baseline + external_legal_matter)",
      flag_a.get("triggered") is True,
      f"triggered={flag_a.get('triggered')}, "
      f"tc={flag_a.get('trigger_conditions')}")
check("Scenario A: intake_significant_events in protected_activity_sources",
      "intake_significant_events" in flag_a.get(
          "trigger_conditions", {}).get("protected_activity_sources", []))
check("Scenario A: any_high_priority is True",
      mm_a.get("any_high_priority") is True)

# Scenario B: DB above baseline + q_signal -> triggered
sess_b = _make_db_session(["none"], q_signal=True)
out_b = assemble_output(sess_b)
mm_b = out_b.get("monitoring_metadata", {})
flag_b = mm_b["flags"][0] if mm_b.get("flags") else {}
check("Scenario B: flag triggered (DB above baseline + q_signal)",
      flag_b.get("triggered") is True,
      f"triggered={flag_b.get('triggered')}")
check("Scenario B: q_signal in protected_activity_sources",
      "q_signal" in flag_b.get(
          "trigger_conditions", {}).get("protected_activity_sources", []))

# Scenario C: DB below baseline -> not triggered even with protected activity
sess_c = _make_db_session(["external_legal_matter"], db_score_mult=0.5)
out_c = assemble_output(sess_c)
mm_c = out_c.get("monitoring_metadata", {})
flag_c = mm_c["flags"][0] if mm_c.get("flags") else {}
check("Scenario C: flag not triggered (DB below baseline)",
      flag_c.get("triggered") is False,
      f"triggered={flag_c.get('triggered')}")
check("Scenario C: any_high_priority is False",
      mm_c.get("any_high_priority") is False)

# Scenario D: DB above baseline but no protected activity -> not triggered
sess_d = _make_db_session(["none"], q_signal=False)
out_d = assemble_output(sess_d)
mm_d = out_d.get("monitoring_metadata", {})
flag_d = mm_d["flags"][0] if mm_d.get("flags") else {}
check("Scenario D: flag not triggered (no protected activity)",
      flag_d.get("triggered") is False,
      f"triggered={flag_d.get('triggered')}, "
      f"tc={flag_d.get('trigger_conditions')}")
check("Scenario D: protected_activity_sources empty",
      flag_d.get("trigger_conditions", {}).get("protected_activity_sources") == [])


# ── Summary ────────────────────────────────────────────────────────────────────
print("\\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\\nAll checks passed. Section VII output contract is structurally valid.")
print("=" * 64)

sys.exit(1 if FAIL else 0)'''

CHANGES = [
    ("Section 1: expected_fields + count",       OLD_EXPECTED_FIELDS,  NEW_EXPECTED_FIELDS),
    ("Section 3: monitoring_metadata violation",  OLD_CHECKPOINT_TEST,  NEW_CHECKPOINT_TEST),
    ("Section 19 + summary",                      OLD_SUMMARY,          NEW_SUMMARY),
]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Patch tools/test_contract.py with monitoring_metadata tests"
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
        for label, old, _ in CHANGES:
            found = old in text
            status = "OK  " if found else "MISS"
            if not found:
                all_ok = False
            print(f"  [{status}] {label}")
        if not all_ok:
            print("\n  ERROR: one or more OLD strings not found in target.")
            sys.exit(1)
        print()
        print("  New tests added:")
        print("    Section 1: +1 (monitoring_metadata field check + count 13->14)")
        print("    Section 3: +1 (monitoring_metadata.flag_count violation)")
        print("    Section 19: +27 (structure, fields, 4 firing scenarios)")
        print("    Total new tests: 29")
        print("    test_contract.py: 95 -> 124 tests")
        print("    Total engine tests: 363 -> 392")
        return

    for label, old, _ in CHANGES:
        if old not in text:
            print(f"ERROR: OLD string not found for '{label}' -- aborting.")
            sys.exit(1)

    new_text = text
    for _, old, new in CHANGES:
        new_text = new_text.replace(old, new, 1)

    if new_text == text:
        print("ERROR: no changes produced.")
        sys.exit(1)

    TARGET.write_text(new_text, encoding="utf-8")
    print(f"WRITTEN: {TARGET}")
    print(f"  {len(CHANGES)} changes applied")
    print("  29 new tests added (sections 1, 3, 19)")
    print("  test_contract.py: 95 -> 124 tests")


if __name__ == "__main__":
    main()
