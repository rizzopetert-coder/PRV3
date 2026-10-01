"""
Friction tax rebuild, Stage 4: comment and docstring cleanup only. Names the
structures that now exist instead of the ones Stage 4 removed. No code change.

Usage: python tools/patch_stage4_comments.py --dry-run | --write
"""
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
FT = R / "engine/friction_tax.py"
SCR = R / "engine/data/state_criteria.py"

FT_EDITS = [
    ("# citation. Defined before PAYROLL_BASELINE_GRID -- a real input to the\n# payroll_floor_annual formula, not just a documentation reference.\n",
     "# citation. Read by Legal (cluster 3 affected-worker math) and\n# resolve_headcount_bucket(), no longer by the friction figure.\n"),
    ("# Section 3). Read by get_industry_wage() and the PAYROLL_BASELINE_GRID build,\n",
     "# Section 3). Read by get_industry_wage() and compute_friction_tax(),\n"),
    ("""    existing lookup convention (PAYROLL_BASELINE_GRID.get(),
    ORG_TYPE_SCALARS.get()), not an exception. Category D (free condensed
    diagnostic), this session -- the only consumer of this accessor;
    PAYROLL_BASELINE_GRID's own headcount x industry_wage math is
    untouched, this is a standalone single-value lookup.
""", """    existing lookup convention (dict .get(), not an exception). Category D
    (free condensed diagnostic) reads it through api/engine.py, and
    compute_friction_tax() reads the same table for W.
"""),
    ("""# STATE_MULTIPLIERS[state_id].criteria["legal"].score, already recorded
# above.
""", """# STATE_CRITERIA[state_id].legal (engine/data/state_criteria.py).
"""),
]
SCR_EDITS = [
    ("""Scores only. Each value was copied from the live
engine.friction_tax.STATE_MULTIPLIERS[state].criteria[criterion].score on
2026-09-30 by tools/patch_stage1_state_criteria.py (friction tax rebuild,
Stage 1, prompts/friction-tax-rebuild-build-spec.md Section 4 and Section 10
step 2). The rationale text stays in STATE_MULTIPLIERS until that table is
removed in Stage 4.
""", """Scores only. Each value was copied from the former
engine.friction_tax.STATE_MULTIPLIERS[state].criteria[criterion].score on
2026-09-30 by tools/patch_stage1_state_criteria.py (friction tax rebuild,
Stage 1, prompts/friction-tax-rebuild-build-spec.md Section 4 and Section 10
step 2). STATE_MULTIPLIERS, with its per-score rationale text, was removed in
Stage 4. The rationale text is in git history before that commit, and
tools/test_state_criteria.py pins these scores with a frozen fingerprint.
"""),
    ("decision_quality -> decision-time receipt). Read by\n      engine/contract.py's receipts today and by the two-channel function after\n",
     "decision_quality -> decision-time receipt). Read by\n      engine/contract.py's receipts and ledger and by the two-channel function in\n"),
]


def apply(path, edits, write):
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")
    for o, n in edits:
        assert t.count(o) == 1, f"{path.name}: count {t.count(o)}: {o[:60]!r}"
        t = t.replace(o, n)
    print(f"{path.name}: {len(edits)} edits ok")
    if write:
        path.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


w = "--write" in sys.argv
apply(FT, FT_EDITS, w)
apply(SCR, SCR_EDITS, w)
print("WRITE" if w else "DRY RUN")
