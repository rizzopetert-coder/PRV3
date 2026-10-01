"""
Friction tax rebuild, Stage 1 (spec Section 10 step 2, as amended by the Phase
0 addendum): create engine/data/state_criteria.py and point Legal and the
receipt channel switch at it.

  1. NEW engine/data/state_criteria.py: STATE_CRITERIA, four integer scores per
     state (turnover, productivity, decision_quality, legal), generated from the
     live STATE_MULTIPLIERS so the values are copied, never retyped.
  2. engine/friction_tax.py: the LEGAL_COMPLIANCE_CLUSTER assertion and
     _single_state_legal_pricing() read STATE_CRITERIA[...].legal instead of
     STATE_MULTIPLIERS[...].criteria["legal"].score. compute_friction_tax() is
     NOT touched here, it keeps STATE_MULTIPLIERS until Stage 4.
  3. engine/contract.py: the import and the receipt channel switch read
     STATE_CRITERIA instead of STATE_MULTIPLIERS.

Legal/Compliance output must stay byte-identical:
    python tools/capture_legal_baseline.py --check

Usage:
    python tools/patch_stage1_state_criteria.py --dry-run [--only module|friction|contract]
    python tools/patch_stage1_state_criteria.py --write   [--only module|friction|contract]
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

MODULE = REPO / "engine" / "data" / "state_criteria.py"
FRICTION = REPO / "engine" / "friction_tax.py"
CONTRACT = REPO / "engine" / "contract.py"

HEADER = '''"""
Per-state criterion scores (0, 1 or 2) for the four friction/legal criteria.

Scores only. Each value was copied from the live
engine.friction_tax.STATE_MULTIPLIERS[state].criteria[criterion].score on
2026-09-30 by tools/patch_stage1_state_criteria.py (friction tax rebuild,
Stage 1, prompts/friction-tax-rebuild-build-spec.md Section 4 and Section 10
step 2). The rationale text stays in STATE_MULTIPLIERS until that table is
removed in Stage 4.

Uses:
  turnover, productivity, decision_quality
      A score above 0 switches the matching friction channel on for a state
      (turnover -> Turnover channel, productivity -> Engagement channel,
      decision_quality -> decision-time receipt). Read by
      engine/contract.py's receipts today and by the two-channel function after
      Stage 4.
  legal
      Read by Legal/Compliance (engine/friction_tax.py). Legal must not depend
      on a friction module's internals, which is why this lives here. A score of
      0 means not applicable, 1 or 2 selects the Legal pricing domain.

Keys are the state ids in engine/data/states.py (58 states).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StateCriteria:
    turnover: int
    productivity: int
    decision_quality: int
    legal: int


STATE_CRITERIA: dict[str, StateCriteria] = {
'''

FOOTER = '''}

for _sid, _c in STATE_CRITERIA.items():
    for _name in ("turnover", "productivity", "decision_quality", "legal"):
        _v = getattr(_c, _name)
        assert isinstance(_v, int) and not isinstance(_v, bool) and 0 <= _v <= 2, (
            f"{_sid}.{_name}: score {_v!r} is not an int in [0, 2]"
        )
del _sid, _c, _name, _v
'''


def build_module() -> str:
    from engine.friction_tax import STATE_MULTIPLIERS
    from engine.data.states import STATE_PROFILES
    ids = list(STATE_MULTIPLIERS.keys())
    assert set(ids) == set(STATE_PROFILES), "STATE_MULTIPLIERS and STATE_PROFILES ids differ"
    body = ""
    for sid in ids:
        c = STATE_MULTIPLIERS[sid].criteria
        body += (
            f'    "{sid}": StateCriteria(turnover={c["turnover"].score}, '
            f'productivity={c["productivity"].score}, '
            f'decision_quality={c["decision_quality"].score}, legal={c["legal"].score}),\n'
        )
    return HEADER + body + FOOTER


# (file, [(old, new)]) each old must occur exactly once
FRICTION_EDITS = [
    ("from engine.data.jurisdiction import JURISDICTION_TABLE\n",
     "from engine.data.jurisdiction import JURISDICTION_TABLE\nfrom engine.data.state_criteria import STATE_CRITERIA\n"),
    ("    assert _lc_sid in STATE_MULTIPLIERS, (\n",
     "    assert _lc_sid in STATE_CRITERIA, (\n"),
    ('    _lc_score = STATE_MULTIPLIERS[_lc_sid].criteria["legal"].score\n',
     "    _lc_score = STATE_CRITERIA[_lc_sid].legal\n"),
    ("    entry = STATE_MULTIPLIERS.get(state_id)\n    if entry is None:\n        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,\n            coverage_confidence=\"NOT_APPLICABLE\", partial_state_flag=False)\n    score = entry.criteria[\"legal\"].score\n",
     "    entry = STATE_CRITERIA.get(state_id)\n    if entry is None:\n        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,\n            coverage_confidence=\"NOT_APPLICABLE\", partial_state_flag=False)\n    score = entry.legal\n"),
]

CONTRACT_EDITS = [
    ("    compute_legal_per_state_breakdown, STATE_MULTIPLIERS,\n)\n",
     "    compute_legal_per_state_breakdown,\n)\nfrom engine.data.state_criteria import STATE_CRITERIA\n"),
    ('        entry = STATE_MULTIPLIERS.get(s["state_id"])\n',
     '        entry = STATE_CRITERIA.get(s["state_id"])\n'),
    ("            if entry.criteria[key].score > 0\n",
     "            if getattr(entry, key) > 0\n"),
]


def edit(path: Path, edits, write: bool) -> None:
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"{path.name}: anchor count {n} (need 1): {old[:70]!r}")
        text = text.replace(old, new)
    print(f"{path.name}: {len(edits)} edits ok ({'CRLF' if crlf else 'LF'})")
    if write:
        path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
        print("  WROTE", path.name)


def main() -> int:
    write = "--write" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else "all"
    if only in ("all", "module"):
        if MODULE.exists():
            print("state_criteria.py exists, skipping module step")
        else:
            src = build_module()
            print(f"state_criteria.py: {src.count('StateCriteria(')-1} states")
            if write:
                MODULE.write_bytes(src.encode("utf-8"))
                print("  WROTE", MODULE.name)
    if only in ("all", "friction"):
        edit(FRICTION, FRICTION_EDITS, write)
    if only in ("all", "contract"):
        edit(CONTRACT, CONTRACT_EDITS, write)
    print("WRITE" if write else "DRY RUN, nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
