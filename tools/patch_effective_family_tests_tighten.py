"""
Tighten the causation-override consistency tests (section 12 of
tools/test_phase1_report_data.py). A negative control against the pre-fix
main.py showed the end-to-end loop catches the bug (4 mismatches) but the
fallback check passed on the old code too: the_uninitiated's profile vector
does not make it the lead, so no override fired there. Now the loop records
the runs where the override actually changed the family, requires at least
one, and the fallback check reuses one of those runs.

Usage: python tools/patch_effective_family_tests_tighten.py --dry-run | --write
"""
import argparse, pathlib, sys

PT = pathlib.Path('tools/test_phase1_report_data.py')
EDITS = [
    ('_checked = 0\n', '_checked = 0\n_fired = []  # (sid, pattern, vec) where the override changed the family\n', 'fired list'),
    ('        _checked += 1\n',
     '        _checked += 1\n'
     '        _lead = _SP[sid].resolution_family\n'
     '        if _routing != _lead and STATE_CAUSATION_OVERRIDES[sid].get(_pattern) == _routing:\n'
     '            _fired.append((sid, _pattern, vec_s))\n', 'record fired'),
    ('      _checked > 0)\n',
     '      _checked > 0)\n'
     'check(f"end to end: the override actually re-routed some runs ({len(_fired)}), so the check has teeth",\n'
     '      len(_fired) > 0, str([(s, p) for s, p, _ in _fired]))\n', 'require fired'),
    ('# Fallback path uses the displayed family too\n_force_pattern("diffuse")\n',
     '# Fallback path uses the displayed family too, on a run where the override fired\n'
     '_fb_sid, _fb_pattern, _fb_vec = _fired[0]\n'
     '_force_pattern(_fb_pattern)\n', 'fallback uses fired run'),
    ('        vec_u = {f: float(getattr(_SP["the_uninitiated"].dimensional_vector, f)) * 3.0\n'
     '                 for f in _SP["the_uninitiated"].dimensional_vector.__dataclass_fields__}\n'
     '        _fo = _m.run_accumulated_engine(vec_u,',
     '        _fo = _m.run_accumulated_engine(_fb_vec,', 'fallback vector'),
    ('check("fallback path: backup copy is the displayed family\'s copy",\n',
     'check(f"fallback path ({_fb_sid} / {_fb_pattern}): backup copy is the displayed (overridden) family\'s copy",\n', 'label'),
]

ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
a = ap.parse_args(); t = PT.read_text(encoding='utf-8')
for old, new, label in EDITS:
    if t.count(old) != 1:
        print(f'ERROR {label} x{t.count(old)}', file=sys.stderr); sys.exit(1)
    t = t.replace(old, new, 1); print(f'[{PT} :: {label}] OK')
if a.dry_run:
    print('DRY RUN -- nothing written.')
else:
    PT.write_text(t, encoding='utf-8'); print('WROTE')
