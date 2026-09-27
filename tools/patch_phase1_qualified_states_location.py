"""
Phase 1 follow-up (2026-09-27): move all_qualified_states from the top
level into private_output. tools/test_contract.py pins exactly 16 top-level
fields (VII.1: "Key names, data types, and field presence are immutable"),
and c80f877 made it 17. private_output is validated by required fields only
and already carries the other Phase 1 additions. Same content, still silent.

Usage:
    python tools/patch_phase1_qualified_states_location.py --dry-run
    python tools/patch_phase1_qualified_states_location.py --write
"""
import argparse, pathlib, sys

CT = pathlib.Path('engine/contract.py')
T = pathlib.Path('tools/test_phase1_report_data.py')

TOP = ('        # Every above-floor state, score-descending, in single AND multi\n'
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
       '        ],\n')
ATTACH_OLD = ('    if service_cost_comparison is not None:\n'
              '        private_output["service_cost_comparison"] = service_cost_comparison\n')
ATTACH_NEW = (ATTACH_OLD +
              '    # Every above-floor state, score-descending, in single AND multi mode\n'
              '    # (identified_states keeps only the lead in single mode, and every\n'
              '    # dollar figure is computed from identified_states, so this is a\n'
              '    # separate silent field -- Pete, Phase 1). In private_output, not the\n'
              '    # top level, which is pinned at 16 fields.\n'
              '    private_output["all_qualified_states"] = [\n'
              '        {\n'
              '            "state_id":          qs.state_id,\n'
              '            "state_name":        qs.state_name,\n'
              '            "score":             round(qs.score, 6),\n'
              '            "descriptive_prose": STATE_PROFILES[qs.state_id].descriptive_prose\n'
              '                                 if qs.state_id in STATE_PROFILES else "",\n'
              '        }\n'
              '        for qs in routing.qualified_states\n'
              '    ]\n')

def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
    a = ap.parse_args()
    c = CT.read_text(encoding='utf-8')
    for old, label in ((TOP, 'top-level block'), (ATTACH_OLD, 'attach point')):
        if c.count(old) != 1:
            print(f'ERROR: {label} found {c.count(old)} times', file=sys.stderr); sys.exit(1)
    c = c.replace(TOP, '', 1).replace(ATTACH_OLD, ATTACH_NEW, 1)
    print('[contract.py] all_qualified_states moved into private_output OK')
    t = T.read_text(encoding='utf-8')
    old_t = '    aqs = out["all_qualified_states"]\n'
    if t.count(old_t) != 1:
        print('ERROR: test anchor', file=sys.stderr); sys.exit(1)
    t = t.replace(old_t, '    aqs = out["private_output"]["all_qualified_states"]\n'
                         '    check(f"[{brand}] top level stays at the pinned 16 fields", len(out) == 16, str(len(out)))\n', 1)
    print('[test] updated OK')
    if a.dry_run:
        print('DRY RUN -- nothing written.'); return
    CT.write_text(c, encoding='utf-8'); T.write_text(t, encoding='utf-8'); print('WROTE')

if __name__ == '__main__':
    main()
