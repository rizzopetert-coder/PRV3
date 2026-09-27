"""
MOB 13b: one Tier 1 backlog item for two asset-scoring calibration issues
(Pete, 2026-09-27). Not a code change. The severity-follow-up 0.25 seeding
was only ever reported in chat, never logged, so it is logged here together
with the Q18-E finding, as Pete asked. Inserted after the driver
answer-steering item. MOB is CRLF.

Usage:
    python tools/patch_mob_13b_asset_calibration.py --dry-run
    python tools/patch_mob_13b_asset_calibration.py --write
"""
import argparse, pathlib, sys

MOB = pathlib.Path('tools/_mob.txt')
ANCHOR = '- `tools/diagnostic_fast_forward.py` answer-steering is too weak'
ITEM = (
    '- Asset-scoring calibration, Tier 1 (logged 2026-09-27, not started, data-first per CLAUDE.md: '
    'dry-run, Pete, commit). Two places where the question library adds asset signal the respondent\'s '
    'answer does not earn. (1) Placeholder seeding: the 28 fixed-value SEVER-* follow-ons plus Q03B and '
    'Q03A-D-FOLLOW add +0.25 to all four *_asset fields whatever the answer (the library\'s own "Phase 1 '
    'calibration will refine these values" seeding). Follow-ons fire on problem answers, so asset totals '
    'rise with problem severity. Phase 1\'s asset_evidence subtracts it at report time '
    '(`_build_asset_evidence`, engine/contract.py), but the raw accumulated_vector, and the asset_score '
    'fed to Call 1, still carry it. First raised in a 2026-09-27 chat report, not logged until now. '
    '(2) Q18-E ("Safety and security concerns here have gone unaddressed longer than they should have") '
    'scores conditionally: attitude_liability +0.6 in high-hazard industries, but attitude_asset +0.3 in '
    'every other industry, so a problem answer raises an asset score. observation_valence (`12fa91d`) '
    'keeps its text out of the strengths list, not out of the scores.'
)

def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
    a = ap.parse_args()
    t = MOB.read_bytes().decode('utf-8')
    key = '\r\n' + ANCHOR
    if t.count(key) != 1:
        print(f'ERROR: anchor found {t.count(key)} times', file=sys.stderr); sys.exit(1)
    if 'Asset-scoring calibration, Tier 1' in t:
        print('ERROR: already logged', file=sys.stderr); sys.exit(1)
    end = t.index('\r\n', t.index(key) + 2)
    t = t[:end] + '\r\n' + ITEM + t[end:]
    print('[MOB :: 13b asset-scoring calibration item] OK')
    print('semicolons:', ITEM.count(';'))
    if a.dry_run:
        print('DRY RUN -- nothing written.'); return
    MOB.write_text(t, encoding='utf-8', newline=''); print('WROTE', MOB)

if __name__ == '__main__':
    main()
