"""
Unplanned-but-necessary fix, found while running Phase 1's regression
(Mechanism 1 deprecation session): tools/test_accumulation.py calls
initialize_priors(INTAKE_BASIC) / initialize_priors(INTAKE_EVENT) /
initialize_priors(INTAKE_HEADCOUNT_SMALL) -- all three now crash
(TypeError) against the new zero-arg initialize_priors() signature,
confirmed via direct run before writing this fix.

Sections 2 and 3 (significant-event elevation, headcount elevation)
tested a mechanism that no longer exists -- not fixed to call the new
signature, removed, since there's nothing left for them to meaningfully
assert (initialize_priors() ignores all input now; keeping them would
either not type-check or just redundantly re-test section 1's flat-
baseline fact under a misleading section header). Section 1 (flat
baseline) is the one still-accurate test, updated to call
initialize_priors() with no argument.

INTAKE_HEADCOUNT_SMALL removed -- was referenced only by the now-removed
section 3, otherwise unused (confirmed via grep before removing).
INTAKE_BASIC and INTAKE_EVENT are kept -- both still exercised later in
this file by AccumulationEngine(...)'s own constructor tests, which
still takes intake_data (only the pass-through into initialize_priors()
was removed, not AccumulationEngine's own parameter).

Usage:
  python tools/patch_test_accumulation_mechanism1_cleanup.py --dry-run
  python tools/patch_test_accumulation_mechanism1_cleanup.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_PATH = REPO_ROOT / "tools" / "test_accumulation.py"

OLD = '''INTAKE_HEADCOUNT_SMALL = IntakeData(
    headcount=4,
    industry="Professional Services",
    org_type="Founder-led",
    jurisdictions=["TX"],
    significant_events=["none"],
    principal_role="Owner or founder",
)


# ── 1. Baseline prior — equal probability ─────────────────────────────────────
print("\\n1. Prior initialization — baseline (no events)")

priors_basic = initialize_priors(INTAKE_BASIC)
n = len(STATE_PROFILES)
expected = 1.0 / n

check("Prior dict covers all states", len(priors_basic) == n, f"got {len(priors_basic)}")
check("Prior sums to 1.0",
      isclose(sum(priors_basic.values()), 1.0, rel_tol=1e-9),
      f"sum={sum(priors_basic.values())}")
check("None-event: uniform prior (all states equal)",
      all(isclose(v, expected, rel_tol=1e-9) for v in priors_basic.values()),
      f"non-uniform: sample={list(priors_basic.values())[:3]}")


# ── 2. Significant event — elevated states then normalized ─────────────────────
print("\\n2. Prior initialization — significant event (acquisition_or_merger)")

priors_event = initialize_priors(INTAKE_EVENT)
# acquisition_or_merger elevates: the_second_close, identity_erosion, transition_paralysis
# multiplier is CALIBRATION_TARGET (None) → treated as 1.0 → distribution stays uniform
elevated_ids = ["the_second_close", "identity_erosion", "transition_paralysis"]

check("Event prior sums to 1.0",
      isclose(sum(priors_event.values()), 1.0, rel_tol=1e-9),
      f"sum={sum(priors_event.values())}")

# With CALIBRATION_TARGET multiplier (1.0), distribution is still uniform
check("CALIBRATION_TARGET multiplier = 1.0 → uniform prior preserved",
      all(isclose(priors_event[sid], expected, rel_tol=1e-9)
          for sid in elevated_ids),
      f"non-uniform: {[(s, priors_event[s]) for s in elevated_ids]}")


# ── 3. Headcount < 25 — founders_grip elevated (CALIBRATION_TARGET = 1.0) ─────
print("\\n3. Prior initialization — headcount Under 25")

priors_small = initialize_priors(INTAKE_HEADCOUNT_SMALL)
check("Headcount prior sums to 1.0",
      isclose(sum(priors_small.values()), 1.0, rel_tol=1e-9),
      f"sum={sum(priors_small.values())}")
check("Headcount CALIBRATION_TARGET (1.0) → founders_grip at baseline",
      isclose(priors_small["the_founders_grip"], expected, rel_tol=1e-9),
      f"founders_grip={priors_small['the_founders_grip']}, expected={expected}")
'''

NEW = '''# ── 1. Baseline prior — flat, unconditional (Mechanism 1 deprecated) ──────────
print("\\n1. Prior initialization — flat baseline, unconditional")

# initialize_priors() no longer takes intake_data -- Mechanism 1 (Prior
# Probability Adjusters: significant-events-driven and headcount-driven
# prior elevation) was deprecated this session (Decision Register):
# confirmed nothing in the real ranking/output pipeline ever read
# AccumulationEngine.priors, so this is now a pure equal-baseline function,
# always. The former sections 2/3 (event elevation, headcount elevation)
# are removed -- there's no mechanism left to test. INTAKE_EVENT/
# INTAKE_BASIC are still exercised below by AccumulationEngine's own
# constructor tests, which still takes intake_data (only the pass-through
# into initialize_priors() was removed).
priors_basic = initialize_priors()
n = len(STATE_PROFILES)
expected = 1.0 / n

check("Prior dict covers all states", len(priors_basic) == n, f"got {len(priors_basic)}")
check("Prior sums to 1.0",
      isclose(sum(priors_basic.values()), 1.0, rel_tol=1e-9),
      f"sum={sum(priors_basic.values())}")
check("Flat baseline: uniform prior (all states equal)",
      all(isclose(v, expected, rel_tol=1e-9) for v in priors_basic.values()),
      f"non-uniform: sample={list(priors_basic.values())[:3]}")
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = TEST_PATH.read_text(encoding="utf-8")
    count = content.count(OLD)
    if count != 1:
        print(f"ABORT: expected exactly 1 match for anchor, found {count}")
        sys.exit(1)
    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print("=== tools/test_accumulation.py: sections 1-3 would be collapsed to a flat-baseline-only test ===")
    else:
        TEST_PATH.write_text(new_content, encoding="utf-8")
        print("=== tools/test_accumulation.py: written ===")


if __name__ == "__main__":
    main()
