"""
Phase 1 (report redesign), commit 3 (Pete, 2026-09-27):

  1. all_qualified_states (new top-level output key, Pete's "new field,
     silent" call): every above-floor state from routing.qualified_states,
     score-descending, in BOTH single and multi mode. identified_states is
     unchanged, so friction tax, legal exposure, ledger rows, and every live
     dollar figure stay exactly as they are today. Phase 3 decides use.
  2. private_output.service_cost_comparison (Pete: ship with nulls):
     target_service_name   brand-derived: hr_diagnostic -> "HR Consulting"
                           (HR_DIAGNOSTIC_FAMILY_NAME) when routing exists,
                           principal_resolution -> translate_resolution_family()
                           of the effective routing. "" when there is none.
     inaction_cost_low/high  friction tax + legal exposure, each counted only
                           when priced. None when neither is.
     service_estimate_low/high  None (no pricing exists, parked decision).
     pricing_model_note    "" (same).
     Present whenever the result identifies at least one state.

assemble_output() gains brand (default "principal_resolution", so every
existing caller is unchanged). run_accumulated_engine() passes its brand.

Usage:
    python tools/patch_phase1_states_and_cost.py --dry-run
    python tools/patch_phase1_states_and_cost.py --write
"""
import argparse
import pathlib
import sys

CT = pathlib.Path('engine/contract.py')
MN = pathlib.Path('engine/main.py')

CT_EDITS = [
    ('from engine.resolution_families import apply_causation_override\n',
     'from engine.resolution_families import (\n'
     '    apply_causation_override, translate_resolution_family, HR_DIAGNOSTIC_FAMILY_NAME,\n'
     ')\n',
     'imports'),
    ('def assemble_output(\n'
     '    session: SessionData, synthesis_result=None, trajectory_result=None, answers_log=None,\n'
     ') -> dict:\n',
     'def assemble_output(\n'
     '    session: SessionData, synthesis_result=None, trajectory_result=None, answers_log=None,\n'
     '    brand: str = "principal_resolution",\n'
     ') -> dict:\n',
     'brand param'),
    ('    private_output = {\n'
     '        "opening_text":            priv.state_name if priv else "",\n',
     '    # service_cost_comparison (Phase 1, Pete: ship with nulls). Inaction\n'
     '    # cost counts friction tax and legal exposure only where each is priced.\n'
     '    _cost_parts = [\n'
     '        (friction_tax_estimate["low"], friction_tax_estimate["high"])\n'
     '        if friction_tax_estimate else None,\n'
     '        (legal_tail_risk_exposure["low"], legal_tail_risk_exposure["high"])\n'
     '        if legal_tail_risk_exposure and legal_tail_risk_exposure["low"] is not None else None,\n'
     '    ]\n'
     '    _cost_parts = [p for p in _cost_parts if p is not None]\n'
     '    if brand == "hr_diagnostic":\n'
     '        _target_service = HR_DIAGNOSTIC_FAMILY_NAME if effective_resolution_routing else ""\n'
     '    else:\n'
     '        _target_service = translate_resolution_family(effective_resolution_routing)\n'
     '    service_cost_comparison = (\n'
     '        {\n'
     '            "target_service_name":   _target_service,\n'
     '            "inaction_cost_low":     round(sum(p[0] for p in _cost_parts), 2) if _cost_parts else None,\n'
     '            "inaction_cost_high":    round(sum(p[1] for p in _cost_parts), 2) if _cost_parts else None,\n'
     '            "service_estimate_low":  None,\n'
     '            "service_estimate_high": None,\n'
     '            "pricing_model_note":    "",\n'
     '        }\n'
     '        if identified_states else None\n'
     '    )\n'
     '    private_output = {\n'
     '        "opening_text":            priv.state_name if priv else "",\n',
     'service cost comparison'),
    ('    if asset_evidence is not None:\n'
     '        private_output["asset_evidence"] = asset_evidence\n',
     '    if asset_evidence is not None:\n'
     '        private_output["asset_evidence"] = asset_evidence\n'
     '    if service_cost_comparison is not None:\n'
     '        private_output["service_cost_comparison"] = service_cost_comparison\n',
     'attach cost comparison'),
    ('        "identified_states":    identified_states,\n'
     '        "severity":             severity_obj,\n',
     '        "identified_states":    identified_states,\n'
     '        # Every above-floor state, score-descending, in single AND multi\n'
     '        # mode (identified_states keeps only the lead in single mode, and\n'
     '        # every dollar figure is computed from identified_states, so this\n'
     '        # is a separate silent field -- Pete, Phase 1).\n'
     '        "all_qualified_states": [\n'
     '            {\n'
     '                "state_id":          qs.state_id,\n'
     '                "state_name":        qs.state_name,\n'
     '                "score":             round(qs.score, 6),\n'
     '                "descriptive_prose": STATE_PROFILES[qs.state_id].descriptive_prose\n'
     '                                     if qs.state_id in STATE_PROFILES else "",\n'
     '            }\n'
     '            for qs in routing.qualified_states\n'
     '        ],\n'
     '        "severity":             severity_obj,\n',
     'all_qualified_states'),
]

MN_EDITS = [
    ('    return assemble_output(\n'
     '        session_data, synthesis_result=synthesis_result, trajectory_result=trajectory_result,\n'
     '        answers_log=answers_log,\n'
     '    )\n',
     '    return assemble_output(\n'
     '        session_data, synthesis_result=synthesis_result, trajectory_result=trajectory_result,\n'
     '        answers_log=answers_log, brand=brand,\n'
     '    )\n',
     'pass brand'),
]


def apply(path, edits):
    t = path.read_text(encoding='utf-8')
    for old, new, label in edits:
        n = t.count(old)
        if n != 1:
            print(f'ERROR: {path} :: {label} anchor found {n} times.', file=sys.stderr)
            sys.exit(1)
        t = t.replace(old, new, 1)
        print(f'[{path} :: {label}] OK')
    return t


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    ct = apply(CT, CT_EDITS)
    mn = apply(MN, MN_EDITS)
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    CT.write_text(ct, encoding='utf-8')
    MN.write_text(mn, encoding='utf-8')
    print(f'WROTE: {CT}, {MN}')


if __name__ == '__main__':
    main()
