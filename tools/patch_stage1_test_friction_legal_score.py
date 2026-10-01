"""
Stage 1 follow-up: tools/test_friction_tax.py patched built_to_fail's legal
score to 0 through STATE_MULTIPLIERS. Legal now reads
engine/data/state_criteria.py STATE_CRITERIA, so the monkey-patch targets that
table instead. Same scenario, same expected result.

Usage: python tools/patch_stage1_test_friction_legal_score.py --dry-run | --write
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools" / "test_friction_tax.py"
OLD = '''_original_btf = STATE_MULTIPLIERS.get("built_to_fail")
_ft.STATE_MULTIPLIERS["built_to_fail"] = _synthetic_entry(
    turnover=_original_btf.criteria["turnover"].score,
    productivity=_original_btf.criteria["productivity"].score,
    decision_quality=_original_btf.criteria["decision_quality"].score,
    legal=0,
)
'''
NEW = '''import dataclasses as _dc
# Legal reads engine/data/state_criteria.py STATE_CRITERIA (Stage 1), so the
# monkey-patch targets that table, not STATE_MULTIPLIERS.
_original_btf = _ft.STATE_CRITERIA["built_to_fail"]
_ft.STATE_CRITERIA["built_to_fail"] = _dc.replace(_original_btf, legal=0)
'''
OLD2 = '_ft.STATE_MULTIPLIERS["built_to_fail"] = _original_btf\n'
NEW2 = '_ft.STATE_CRITERIA["built_to_fail"] = _original_btf\n'

raw = P.read_bytes().decode("utf-8"); crlf = "\r\n" in raw; t = raw.replace("\r\n", "\n")
for o in (OLD, OLD2):
    assert t.count(o) == 1, f"anchor count {t.count(o)}: {o[:50]!r}"
t = t.replace(OLD, NEW).replace(OLD2, NEW2)
print("2 edits ok", "CRLF" if crlf else "LF")
if "--write" in sys.argv:
    P.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8")); print("WROTE")
else:
    print("DRY RUN")
