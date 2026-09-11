"""
tools/test_contract.py: direct test of engine/contract.py:574's
legal_tail_risk_exposure guard (`if legal_result["low"] is not None or
legal_result["has_unpriced_conditions"]`), exercised specifically by
OH's Phase 2b QUALITATIVE_ONLY resolution -- not inferred from the
Government/hr_capture case's already-proven shape (tools/
test_friction_tax.py's own OH test, previous pass), a real
engine/contract.py-level check this session confirmed had none before.

Builds a minimal, dedicated SessionData fixture (jurisdictions=["OH"],
"the_paper_tiger" as the single identified/dominant state, matching the
Cluster 1 fixture state used throughout this session's other OH tests)
rather than reusing the file's existing module-level `session` fixture
(jurisdictions=["CA"], dominant state is whichever state_id happens to
be first in STATE_PROFILES dict order -- not guaranteed Legal-scoring,
and other tests in this file already depend on that fixture's exact
shape staying unchanged). Follows _make_db_session()'s existing pattern
(~line 756) as the closest structural precedent for building a session
fixture with a specific dominant state and intake.

Usage:
    python tools/patch_test_contract_oh_legal_tail_risk.py --dry-run
    python tools/patch_test_contract_oh_legal_tail_risk.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_contract.py')

IMPORT_OLD = '''from engine.contract import (
    assemble_output, validate_schema, SessionData, ENGINE_VERSION,
    _OUTPUT_TYPE_VALUES, _SEVERITY_TIER_VALUES,
)'''

IMPORT_NEW = '''from engine.contract import (
    assemble_output, validate_schema, SessionData, ENGINE_VERSION,
    _OUTPUT_TYPE_VALUES, _SEVERITY_TIER_VALUES, LEGAL_TAIL_RISK_CAVEAT_TEXT,
)'''

ANCHOR_OLD = '''# ── Summary ────────────────────────────────────────────────────────────────────'''

ANCHOR_NEW = '''# ── engine/contract.py:574 legal_tail_risk_exposure guard -- OH QUALITATIVE_ONLY (Phase 2b) ────

def _make_rankings_for(dominant_sid, top_score=0.9):
    """Same shape as make_rankings() above, parametrized by dominant state --
    local to this test block, doesn't touch make_rankings() itself since other
    tests in this file depend on that function's existing first_sid behavior."""
    remaining = (1.0 - top_score) / (n - 1)
    rankings = []
    for i, sid in enumerate(STATE_PROFILES):
        s = top_score if sid == dominant_sid else remaining
        rankings.append(StateRanking(rank=i+1, state_id=sid, distance=0.3, score=s))
    rankings.sort(key=lambda r: -r.score)
    for i, r in enumerate(rankings):
        r.rank = i + 1
    return rankings

oh_intake = IntakeData(
    headcount=20,
    industry="Professional Services",
    org_type="Founder-led",
    jurisdictions=["OH"],
    significant_events=["none"],
    principal_role="C-suite",
)
oh_rankings = _make_rankings_for("the_paper_tiger", top_score=floor_val + 0.05)
oh_pkg = out_engine.build(oh_rankings, sev)
oh_session = SessionData(
    session_id=SessionData.new_session_id(),
    intake=oh_intake,
    final_rankings=oh_rankings,
    accumulated_vector=acc_vector,
    output_package=oh_pkg,
    severity_result=sev,
)
oh_out = assemble_output(oh_session)
oh_identified = oh_out.get("identified_states", [])
check(
    "sanity: the_paper_tiger is the single identified state for the OH session -- needed for the "
    "checks below to mean what they claim",
    len(oh_identified) == 1 and oh_identified[0].get("state_id") == "the_paper_tiger",
    f"got {oh_identified}",
)
oh_legal = oh_out.get("private_output", {}).get("legal_tail_risk_exposure")
check(
    "engine/contract.py:574 guard -- OH's QUALITATIVE_ONLY result (low=None, "
    "has_unpriced_conditions=True) still renders a non-null legal_tail_risk_exposure block, "
    "exercised directly through assemble_output() rather than inferred from the Government/"
    "hr_capture case's already-proven shape",
    oh_legal is not None,
    f"got {oh_legal!r}",
)
check(
    "OH legal_tail_risk_exposure: low/high/band all None, has_unpriced_conditions=True, "
    "unpriced_state_ids=['the_paper_tiger'] -- the exact real-pipeline shape that satisfies the "
    "guard's second OR operand rather than its first",
    oh_legal is not None
    and oh_legal.get("low") is None
    and oh_legal.get("high") is None
    and oh_legal.get("band") is None
    and oh_legal.get("has_unpriced_conditions") is True
    and oh_legal.get("unpriced_state_ids") == ["the_paper_tiger"],
    f"got {oh_legal}",
)
check(
    "OH legal_tail_risk_exposure carries the same caveat text as any other rendered block -- "
    "confirms this isn't a special-cased or truncated object, just the normal dict with "
    "low/high absent",
    oh_legal is not None and oh_legal.get("caveat") == LEGAL_TAIL_RISK_CAVEAT_TEXT,
    f"got caveat={oh_legal.get('caveat')!r}",
)


# ── Summary ────────────────────────────────────────────────────────────────────'''

EDITS = [
    ('import LEGAL_TAIL_RISK_CAVEAT_TEXT', IMPORT_OLD, IMPORT_NEW),
    ('OH legal_tail_risk_exposure guard test', ANCHOR_OLD, ANCHOR_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    errors = []
    for label, old, new in EDITS:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
