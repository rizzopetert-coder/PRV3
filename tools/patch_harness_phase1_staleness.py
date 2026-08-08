"""
PRV3 MC_CENTROID_39 recalibration -- Phase 1 (harness/runner modernization
only, no scoring-constant changes). Gemini-reviewed and cleared, two
corrections applied after independent verification (see Decision Register
row for full detail).

Fixes 3 of the 4 flagged staleness items in
tools/harness_s27_autonomous_calibration.py:

1. RESOLUTION_TARGET (was hardcoded 47) -- now derived from
   len(STATE_PROFILES) at runtime. Confirmed via direct check this
   session: STATE_PROFILES currently has exactly 57 entries, and all 57
   have at least one high_confidence-tier test profile, so the target is
   achievable, not aspirational. Also fixes 4 other hardcoded "47"
   literals (lines 308/317/338/462 in the pre-patch file) that displayed
   percentages/targets against the same stale number -- fixing only
   RESOLUTION_TARGET and leaving these would have produced visibly
   broken output (e.g. "57/47 HC", over 100%). Docstring references
   (module header) updated too, same staleness class.

2. overall_total fallback (was `cal.get("overall_total", 142)`) -- 142
   was the old 47-state suite size. Confirmed via direct read of
   calibration_runner.py's --output-json branch: "overall_total" is
   unconditionally set from suite["total"] in every JSON emission, never
   conditionally omitted -- the fallback is dead code in practice, and a
   missing key would indicate a genuine schema mismatch between this
   harness and calibration_runner.py's output, not a normal condition to
   paper over. Changed to direct indexing (cal["overall_total"]) so a
   real mismatch fails loudly with a clear KeyError instead of silently
   computing percentages against an already-stale hardcoded number that
   would need updating again at the next taxonomy change.

3. derive_scalars()'s N = 39 -- confirmed len(QUESTION_LIBRARY) is NOT
   usable directly (87 entries: includes SEVER-##, DIST-##, VERIFY-Q##,
   FOLLOW variants, not just core questions). Also confirmed neither
   len(QUESTION_LIBRARY) nor len(_CORE_QUESTION_IDS) matches the true
   live PHASE_1_QUESTION_SEQUENCE length (32, defined in
   web/lib/session-store.ts -- not importable from Python, and already
   on record this session as diverging from _CORE_QUESTION_IDS by
   excluding the Q35-39 Aptitude addenda). Used
   tools.calibration_runner._CORE_QUESTION_IDS (currently 41) instead --
   the closest already-existing "core question" concept in the Python
   codebase, and the one this harness's own downstream calibration loop
   actually iterates over via generate_answers(), so it's internally
   consistent with what's actually being calibrated, even though it is
   NOT identical to the live product's respondent-facing count.

Item 4 (V23_SINKS) is deliberately NOT touched here -- confirmed via a
real run this session that the set is badly out of date on both ends
(2 of 4 original sinks are gone, several large new sinks are undetected),
but the fix requires Pete's decision on mechanism (dynamic detection vs.
manually re-verified static set), not a code change. See report.

Usage:
  python tools/patch_harness_phase1_staleness.py --dry-run
  python tools/patch_harness_phase1_staleness.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS_PATH = REPO_ROOT / "tools" / "harness_s27_autonomous_calibration.py"

EDITS: list[tuple[str, str]] = []


def edit(old: str, new: str):
    EDITS.append((old, new))


# -- 1a. Module docstring -- remove hardcoded 47/47 references --------------

edit(
    'Iterates on CENTROID_FIELD_SCALARS (Path B) and SCD_WCS_CLUSTER_WINDOW (Path C)\n'
    'until 47/47 HC, 5 consecutive flat rounds (impasse), or an escalation trigger.',
    'Iterates on CENTROID_FIELD_SCALARS (Path B) and SCD_WCS_CLUSTER_WINDOW (Path C)\n'
    'until every HC-tier state passes (RESOLUTION_TARGET, derived from the live\n'
    'state registry), 5 consecutive flat rounds (impasse), or an escalation trigger.',
)

edit(
    'Pete is pinged (loop stops) on:\n'
    '  RESOLVED   — 47/47 HC\n'
    '  IMPASSE    — 5 consecutive flat rounds\n'
    '  ESCALATING — regression cascade, new sink, or test suite failure',
    'Pete is pinged (loop stops) on:\n'
    '  RESOLVED   — RESOLUTION_TARGET/RESOLUTION_TARGET HC\n'
    '  IMPASSE    — 5 consecutive flat rounds\n'
    '  ESCALATING — regression cascade, new sink, or test suite failure',
)

# -- 1b. Top-level import + RESOLUTION_TARGET --------------------------------

edit(
    'PROJECT_ROOT = str(Path(__file__).parents[1])\n'
    'sys.path.insert(0, PROJECT_ROOT)\n'
    '\n'
    '# ── Configuration ───────────────────────────────────────────────────────────────\n'
    '\n'
    'RESOLUTION_TARGET       = 47      # HC states that must pass to declare resolution',
    'PROJECT_ROOT = str(Path(__file__).parents[1])\n'
    'sys.path.insert(0, PROJECT_ROOT)\n'
    '\n'
    'from engine.data.states import STATE_PROFILES\n'
    '\n'
    '# ── Configuration ───────────────────────────────────────────────────────────────\n'
    '\n'
    '# Derived dynamically from the live state registry (was hardcoded 47, the\n'
    '# pre-taxonomy-expansion state count) -- confirmed this resolves to 57 today,\n'
    '# and confirmed all 57 states have at least one high_confidence-tier profile\n'
    '# in the suite, so the target is achievable, not aspirational.\n'
    'RESOLUTION_TARGET       = len(STATE_PROFILES)  # HC states that must pass to declare resolution',
)

# -- 1c. Remaining hardcoded "47" literals (percentage calc + display) ------

edit(
    '    hc_pct      = round(hc_count / 47 * 100, 1)',
    '    hc_pct      = round(hc_count / RESOLUTION_TARGET * 100, 1)',
)

edit(
    '        f"• HC pass rate:            {hc_count}/47 ({hc_pct}%)",',
    '        f"• HC pass rate:            {hc_count}/{RESOLUTION_TARGET} ({hc_pct}%)",',
)

edit(
    '    print(f"[HARNESS] Target: {RESOLUTION_TARGET}/47 HC | "',
    '    print(f"[HARNESS] Target: {RESOLUTION_TARGET}/{RESOLUTION_TARGET} HC | "',
)

edit(
    '            print(f"[HARNESS] Final HC: {hc_count}/47")',
    '            print(f"[HARNESS] Final HC: {hc_count}/{RESOLUTION_TARGET}")',
)

# -- 2. overall_total: fail loudly instead of a stale silent fallback -------

edit(
    '        overall_total = cal.get("overall_total", 142)',
    '        # Fail loudly rather than silently fall back to a stale hardcoded\n'
    '        # count -- confirmed this key is unconditionally set by\n'
    '        # calibration_runner.py\'s --output-json branch (suite["total"]),\n'
    '        # never omitted, so a KeyError here means a real schema mismatch\n'
    '        # worth surfacing immediately, not papering over.\n'
    '        overall_total = cal["overall_total"]',
)

# -- 3. derive_scalars()'s N = 39 --------------------------------------------

edit(
    '    Count questions that target each primary dimension (via state_targets).\n'
    '    Scalar = count / 39 (question sequence length).\n'
    '    Falls back to Gemini hardcoded values if library is empty.\n'
    '    Returns (scalars_dict, source_label).\n'
    '    """\n'
    '    from engine.data.questions import QUESTION_LIBRARY\n'
    '    from engine.data.states import STATE_PROFILES\n',
    '    Count questions that target each primary dimension (via state_targets).\n'
    '    Scalar = count / N, where N is the live core-question count.\n'
    '    Falls back to Gemini hardcoded values if library is empty.\n'
    '    Returns (scalars_dict, source_label).\n'
    '\n'
    '    N source, confirmed this session: len(QUESTION_LIBRARY) is NOT usable\n'
    '    directly -- it includes SEVER-##, DIST-##, VERIFY-Q##, and FOLLOW\n'
    '    variants, not just core questions (87 vs. 41 core, confirmed by direct\n'
    '    count). Uses tools.calibration_runner._CORE_QUESTION_IDS instead --\n'
    '    the closest existing "core question" concept in this codebase, and the\n'
    '    one this harness\'s own calibration loop actually iterates over via\n'
    '    generate_answers(). Note this is NOT identical to the live product\'s\n'
    '    respondent-facing PHASE_1_QUESTION_SEQUENCE (32, defined in\n'
    '    web/lib/session-store.ts, not importable from Python, and already on\n'
    '    record as diverging from _CORE_QUESTION_IDS by excluding the Q35-39\n'
    '    Aptitude addenda) -- this value is internally consistent with what the\n'
    '    calibration harness itself simulates, which is what this scalar seed is\n'
    '    for.\n'
    '    """\n'
    '    from engine.data.questions import QUESTION_LIBRARY\n'
    '    from engine.data.states import STATE_PROFILES\n'
    '    from tools.calibration_runner import _CORE_QUESTION_IDS\n',
)

edit(
    '    N = 39\n'
    '    scalars = {',
    '    N = len(_CORE_QUESTION_IDS)\n'
    '    scalars = {',
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = HARNESS_PATH.read_text(encoding="utf-8")
    for i, (old, new) in enumerate(EDITS, 1):
        count = content.count(old)
        if count != 1:
            print(f"ABORT: edit {i}: expected exactly 1 match for anchor, found {count}")
            print(f"  anchor (first 150 chars): {old[:150]!r}")
            sys.exit(1)
        content = content.replace(old, new, 1)

    if args.dry_run:
        print(f"=== tools/harness_s27_autonomous_calibration.py: {len(EDITS)} edit(s) would apply cleanly ===")
        print()
        print("--- Full proposed file content follows the same edits shown in this script's ---")
        print("--- EDITS list above (old -> new). No file written in dry-run mode. ---")
    else:
        HARNESS_PATH.write_text(content, encoding="utf-8")
        print(f"=== tools/harness_s27_autonomous_calibration.py: {len(EDITS)} edit(s) written ===")


if __name__ == "__main__":
    main()
