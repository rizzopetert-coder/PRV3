"""
Tests for engine/data/state_criteria.py (friction tax rebuild, Stage 1).

  1. Registry: the 58 state ids match engine/data/states.py exactly
  2. Every state carries four integer scores in [0, 2], none a bool
  3. Frozen sha256 fingerprint of the score table and eight hardcoded spot checks
     (replaced the interim equality with STATE_MULTIPLIERS, removed in Stage 4)
  4. Legal: every LEGAL_COMPLIANCE_CLUSTER state has a legal score in {1, 2}
     (the assertion engine/friction_tax.py makes at import time), and the one
     state with a legal score but no cluster is the known the_inner_circle
  5. Channel switch: the criteria that map to channels are exactly turnover,
     productivity and decision_quality, and the coverage counts match the spec
     (Section 4, computed 2026-09-30)

Usage: python tools/test_state_criteria.py
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.state_criteria import STATE_CRITERIA, StateCriteria
from engine.data.states import STATE_PROFILES
import hashlib
import json

from engine.friction_tax import LEGAL_COMPLIANCE_CLUSTER

PASS = []
FAIL = []


def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


FIELDS = ("turnover", "productivity", "decision_quality", "legal")

print("=" * 64)
print("PRV3 State Criteria Registry -- Unit Tests")
print("=" * 64)

# -- 1. registry -------------------------------------------------------------
check("STATE_CRITERIA has 58 entries", len(STATE_CRITERIA) == 58, f"got {len(STATE_CRITERIA)}")
check("STATE_CRITERIA ids equal engine/data/states.py STATE_PROFILES ids exactly",
      set(STATE_CRITERIA) == set(STATE_PROFILES),
      f"missing {set(STATE_PROFILES) - set(STATE_CRITERIA)}, extra {set(STATE_CRITERIA) - set(STATE_PROFILES)}")
check("every value is a StateCriteria", all(isinstance(v, StateCriteria) for v in STATE_CRITERIA.values()))

# -- 2. scores ---------------------------------------------------------------
bad = [(sid, f, getattr(c, f)) for sid, c in STATE_CRITERIA.items() for f in FIELDS
       if not (isinstance(getattr(c, f), int) and not isinstance(getattr(c, f), bool) and 0 <= getattr(c, f) <= 2)]
check("every score is an int in [0, 2] and not a bool", not bad, f"bad: {bad[:5]}")
check("StateCriteria has exactly the four fields", tuple(StateCriteria.__dataclass_fields__) == FIELDS,
      f"got {tuple(StateCriteria.__dataclass_fields__)}")

# -- 3. frozen fingerprint (replaces the interim equality with STATE_MULTIPLIERS) ----
# sha256 of the canonical 58 x 4 score table, captured 2026-10-01 while
# STATE_MULTIPLIERS still existed and every score was equal to it. Editing any
# score changes the hash and fails here, a deliberate score change updates this
# constant in the same commit.
_canon = json.dumps(
    {sid: [c.turnover, c.productivity, c.decision_quality, c.legal] for sid, c in sorted(STATE_CRITERIA.items())},
    separators=(",", ":"), sort_keys=True,
)
check("the 58 x 4 score table matches its frozen fingerprint",
      hashlib.sha256(_canon.encode()).hexdigest() == "4eb21b87c9feedec2f86259251d9d7a0f1dedff787aa9eb617e32139f56de251",
      f"got {hashlib.sha256(_canon.encode()).hexdigest()}")
_spot = {
    "the_overloaded_manager": (2, 1, 1, 0), "decision_paralysis": (1, 2, 2, 0), "paper_shield": (0, 0, 2, 0),
    "the_founders_grip": (2, 2, 2, 0), "the_basement_standard": (1, 2, 2, 1), "the_inner_circle": (1, 0, 2, 1),
    "the_paper_tiger": (1, 0, 0, 2), "the_lost_map": (0, 2, 2, 0),
}
check("eight spot-checked states hold their hardcoded scores (turnover, productivity, decision_quality, legal)",
      all((c.turnover, c.productivity, c.decision_quality, c.legal) == _spot[s] for s, c in STATE_CRITERIA.items() if s in _spot)
      and all(s in STATE_CRITERIA for s in _spot))

# -- 4. legal ----------------------------------------------------------------
check("every LEGAL_COMPLIANCE_CLUSTER state exists in STATE_CRITERIA with a legal score in {1, 2}",
      all(sid in STATE_CRITERIA and STATE_CRITERIA[sid].legal in (1, 2) for sid in LEGAL_COMPLIANCE_CLUSTER))
check("LEGAL_COMPLIANCE_CLUSTER classifies 30 states", len(LEGAL_COMPLIANCE_CLUSTER) == 30, f"got {len(LEGAL_COMPLIANCE_CLUSTER)}")
unclustered = sorted(sid for sid, c in STATE_CRITERIA.items() if c.legal > 0 and sid not in LEGAL_COMPLIANCE_CLUSTER)
check("the only state with legal > 0 and no cluster is the_inner_circle (pre-existing, Legal treats it as not applicable)",
      unclustered == ["the_inner_circle"], f"got {unclustered}")
check("31 states carry legal > 0", sum(1 for c in STATE_CRITERIA.values() if c.legal > 0) == 31)

# -- 5. channel switch coverage (spec Section 4) -----------------------------
combo = Counter(
    tuple(f for f in ("turnover", "productivity", "decision_quality") if getattr(c, f) > 0)
    for c in STATE_CRITERIA.values()
)
check("all three channels on for 35 states", combo[("turnover", "productivity", "decision_quality")] == 35)
check("turnover and productivity only for 5 states", combo[("turnover", "productivity")] == 5)
check("turnover and decision_quality for 9 states", combo[("turnover", "decision_quality")] == 9)
check("productivity and decision_quality for 4 states", combo[("productivity", "decision_quality")] == 4)
check("turnover only for 4 states", combo[("turnover",)] == 4)
check("decision_quality only for 1 state, paper_shield",
      combo[("decision_quality",)] == 1 and STATE_CRITERIA["paper_shield"].decision_quality > 0
      and STATE_CRITERIA["paper_shield"].turnover == 0 and STATE_CRITERIA["paper_shield"].productivity == 0)
check("decision_quality above 0 for 49 states", sum(1 for c in STATE_CRITERIA.values() if c.decision_quality > 0) == 49)

print(f"\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  {f}")
else:
    print("All tests passed.")

sys.exit(0 if not FAIL else 1)
