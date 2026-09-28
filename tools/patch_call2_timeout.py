"""
Call 2 (tactical synthesis) timeout 15s -> 30s (Pete, 2026-09-28). Measured
Call 2 latency ran 12-14.4s (14.4s with all 40 TC answers flagged), too close
to the 15s ceiling. 30s is about 2x the worst case. Call 1 (output_synthesis,
15s LOCKED) and Call 3 (exec_summary, 15s) are unchanged.

Budget: Call 1 || Call 2 then Call 3 -> worst case max(15, 30) + 15 = 45s of
synthesis, against the engine function's maxDuration 300 (vercel.json).

main.py calls synthesize_tactical(tactical_summary) with no timeout argument,
so the default parameter is the live value. No test pins it.

Usage: python tools/patch_call2_timeout.py --dry-run | --write
"""
import argparse, pathlib, sys

P = pathlib.Path('engine/tactical_synthesis.py')
OLD = '''    client=None,
    timeout: float = 15.0,
) -> tuple:
    """
    Call 2.'''
NEW = '''    client=None,
    timeout: float = 30.0,
) -> tuple:
    """
    Call 2. timeout 30s (2026-09-28): about 2x the worst measured latency
    (14.4s with all 40 TC answers flagged), which crowded the old 15s.'''

ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
a = ap.parse_args(); t = P.read_text(encoding='utf-8')
if t.count(OLD) != 1:
    print(f'ERROR anchor x{t.count(OLD)}', file=sys.stderr); sys.exit(1)
t = t.replace(OLD, NEW, 1); print(f'[{P} :: timeout 15.0 -> 30.0] OK')
if a.dry_run:
    print('DRY RUN -- nothing written.')
else:
    P.write_text(t, encoding='utf-8'); print('WROTE')
