"""
Full engine: resolution family for multi-state results (Pete, 2026-09-27).

OutputPackage.private.resolution_family is only populated in single-state
routing, so in multi-state mode (most real results) the full engine produced
"" for resolution_routing: PR's "Resolution pathway" block rendered blank, the
Phase 3 service card had no name, hr-dx had no hr_pathway drawer, and Call 1
(synthesis) and the hr backup-copy key got an empty family. The condensed
engine already fixed this by reading the lead QualifiedState's family.

Fix, mirroring run_condensed_engine(): new contract.lead_resolution_family()
returns private.resolution_family when present, else the lead state's family
(routing.lead_state, set in both single and multi mode, else
qualified_states[0]), else "". Used at both full-engine sites:
  - assemble_output(): the default family fed to apply_causation_override()
    (resolution_routing, service_cost_comparison.target_service_name).
  - run_accumulated_engine(): engine_family for Call 1's commercial family
    and the hr_diagnostic backup-copy key.

Correction to an earlier report: hr-dx sessions that returned no routing were
not "below the routing threshold", they were multi-state results hitting this
empty family.

Usage: python tools/patch_lead_resolution_family.py --dry-run | --write
"""
import argparse, pathlib, sys

CT = pathlib.Path('engine/contract.py')
MN = pathlib.Path('engine/main.py')

HELPER = '''

def lead_resolution_family(routing, private_block) -> str:
    """
    The result's resolution family in both routing modes. private.resolution_family
    is only populated in single-state mode, so multi-state results (most real
    results) fall back to the lead QualifiedState's family, the same source
    run_condensed_engine() uses. "" only when nothing qualified.
    """
    if private_block is not None and private_block.resolution_family:
        return private_block.resolution_family
    if routing is not None and routing.lead_state is not None:
        return routing.lead_state.resolution_family
    if routing is not None and routing.qualified_states:
        return routing.qualified_states[0].resolution_family
    return ""
'''

CT_EDITS = [
    ('    default_routing_str = priv.resolution_family if priv else ""\n',
     '    # Lead state\'s family in both routing modes (private.resolution_family\n'
     '    # is single-mode only), same source as run_condensed_engine().\n'
     '    default_routing_str = lead_resolution_family(routing, priv)\n',
     'assemble_output default family'),
]
MN_EDITS = [
    ('from engine.contract import SessionData, assemble_output, _compute_asset_score, _compute_liability_score\n',
     'from engine.contract import (\n'
     '    SessionData, assemble_output, _compute_asset_score, _compute_liability_score,\n'
     '    lead_resolution_family,\n'
     ')\n',
     'import'),
    ('        engine_family = (\n'
     '            output_package.private.resolution_family\n'
     '            if output_package.private else ""\n'
     '        )\n',
     '        # Lead state\'s family in both routing modes (private.resolution_family\n'
     '        # is single-mode only), same source as run_condensed_engine().\n'
     '        engine_family = lead_resolution_family(output_package.routing, output_package.private)\n',
     'run_accumulated_engine engine_family'),
]


def apply(path, edits, extra=None):
    t = path.read_text(encoding='utf-8')
    for old, new, label in edits:
        if t.count(old) != 1:
            print(f'ERROR {path} :: {label} x{t.count(old)}', file=sys.stderr); sys.exit(1)
        t = t.replace(old, new, 1); print(f'[{path} :: {label}] OK')
    return t


def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
    a = ap.parse_args()
    ct = apply(CT, CT_EDITS)
    anchor = '\n\n# ── Phase 1 show-your-work: evidence receipts'
    if ct.count(anchor) != 1 or 'def lead_resolution_family' in ct:
        print('ERROR helper anchor', file=sys.stderr); sys.exit(1)
    ct = ct.replace(anchor, HELPER + anchor, 1); print(f'[{CT} :: lead_resolution_family helper] OK')
    mn = apply(MN, MN_EDITS)
    if a.dry_run:
        print('DRY RUN -- nothing written.'); return
    CT.write_text(ct, encoding='utf-8'); MN.write_text(mn, encoding='utf-8'); print('WROTE')


if __name__ == '__main__':
    main()
