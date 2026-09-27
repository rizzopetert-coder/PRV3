"""
Causation override reached the displayed pathway but not the synthesis
(Pete, 2026-09-27, real bug, longstanding).

Trace (before this patch):
  displayed  engine/contract.py assemble_output(): private_output.
             resolution_routing = apply_causation_override(lead_id,
             lead_resolution_family(routing, priv), causation pattern of the
             accumulated vector). The web shows this (translateResolutionFamily
             for PR, "HR Consulting" plus hr_pathway from it for hr-dx), and
             service_cost_comparison names it.
  synthesis  engine/main.py run_accumulated_engine(): engine_family =
             lead_resolution_family(routing, priv), NO override. It feeds Call 1's
             resolution_family (commercial name, or the hr context string) and
             the backup-copy key (PR commercial name / hr fallback key).
             engine/main.py run_engine() (self-select, Path B): the raw
             output_package.private.resolution_family, NO override and single-
             mode only ("" in multi-state), while its display goes through the
             same assemble_output() (lead family + override).
  So any lead among the 15 STATE_CAUSATION_OVERRIDES states whose causation
  pattern matched an override (diffuse or single_point) showed one service in
  the pathway and described another in the text. Live example:
  the_uninitiated + diffuse -> pathway Training & Development, text First Call.

Fix: new contract.effective_resolution_family(routing, private_block,
accumulated_vector) is the one definition of the result's family (lead state's
family in both routing modes, then the causation override). assemble_output(),
run_accumulated_engine(), and run_engine() all use it, so the displayed
pathway is the single source of truth for Call 1, the backup copy, and the hr
fallback key. Each caller passes the same accumulated vector assemble_output()
later sees (Path B: {} in both places), so the pattern and result are identical.

Other re-routes checked: STATE_CAUSATION_OVERRIDES / apply_causation_override()
is the engine's only family re-route. The web only translates names
(translateResolutionFamily, hrPathwayForRouting from the displayed routing).
The condensed engine applies no override to display or synthesis, so it is
internally consistent.

Usage: python tools/patch_effective_family_synthesis.py --dry-run | --write
"""
import argparse
import pathlib
import sys

CT = pathlib.Path('engine/contract.py')
MN = pathlib.Path('engine/main.py')
PT = pathlib.Path('tools/test_phase1_report_data.py')

HELPER_ANCHOR = '\n\n# ── Phase 1 show-your-work: evidence receipts'
HELPER = '''

def effective_resolution_family(routing, private_block, accumulated_vector) -> str:
    """
    The result's resolution family exactly as the report displays it: the
    lead state's family (lead_resolution_family) with the state's causation
    override applied (apply_causation_override, keyed by the causation
    pattern of accumulated_vector). The single source of truth for the
    displayed pathway AND the synthesis family (Call 1, the backup copy, the
    hr fallback key), so pathway and narrative always name the same service.
    """
    lead_id = (
        routing.lead_state.state_id if routing is not None and routing.lead_state
        else (routing.qualified_states[0].state_id
              if routing is not None and routing.qualified_states else None)
    )
    pattern_obj = compute_causation_pattern(accumulated_vector or {}, routing)
    pattern_type = pattern_obj.get("pattern") if isinstance(pattern_obj, dict) else None
    return apply_causation_override(
        state_id=lead_id,
        default_family=lead_resolution_family(routing, private_block),
        causation_pattern=pattern_type,
    )
'''

CT_EDITS = [
    ('    # Lead state\'s family in both routing modes (private.resolution_family\n'
     '    # is single-mode only), same source as run_condensed_engine().\n'
     '    default_routing_str = lead_resolution_family(routing, priv)\n'
     '    effective_resolution_routing = apply_causation_override(\n'
     '        state_id=lead_id,\n'
     '        default_family=default_routing_str,\n'
     '        causation_pattern=pattern_type,\n'
     '    )\n',
     '    # One definition shared with the synthesis call sites (engine/main.py),\n'
     '    # so the displayed pathway and the narrative name the same service.\n'
     '    effective_resolution_routing = effective_resolution_family(\n'
     '        routing, priv, session.accumulated_vector,\n'
     '    )\n',
     'assemble_output uses the shared helper'),
]

MN_EDITS = [
    ('    SessionData, assemble_output, _compute_asset_score, _compute_liability_score,\n'
     '    lead_resolution_family,\n'
     ')\n',
     '    SessionData, assemble_output, _compute_asset_score, _compute_liability_score,\n'
     '    effective_resolution_family,\n'
     ')\n',
     'import'),
    ('        # Lead state\'s family in both routing modes (private.resolution_family\n'
     '        # is single-mode only), same source as run_condensed_engine().\n'
     '        engine_family = lead_resolution_family(output_package.routing, output_package.private)\n',
     '        # The family exactly as the report displays it (lead family plus the\n'
     '        # causation override), so Call 1, the backup copy, and the hr\n'
     '        # fallback key describe the same service the pathway names.\n'
     '        engine_family = effective_resolution_family(\n'
     '            output_package.routing, output_package.private, accumulated_vector,\n'
     '        )\n',
     'run_accumulated_engine synthesis family'),
    ('        commercial_family = translate_resolution_family(\n'
     '            output_package.private.resolution_family\n'
     '            if output_package.private else ""\n'
     '        )\n',
     '        # Same family the displayed pathway uses (assemble_output() receives\n'
     '        # accumulated_vector={} on this path, passed identically here).\n'
     '        commercial_family = translate_resolution_family(\n'
     '            effective_resolution_family(output_package.routing, output_package.private, {})\n'
     '        )\n',
     'run_engine (self-select) synthesis family'),
]

TEST = '''
# ── 12. Causation override: displayed pathway == synthesis family ───────────────
import engine.contract as _ct
from engine.contract import effective_resolution_family
from engine.resolution_families import STATE_CAUSATION_OVERRIDES, translate_resolution_family as _tr
_orig_ccp = _ct.compute_causation_pattern
def _force_pattern(p):
    _ct.compute_causation_pattern = lambda vec, routing: {"pattern": p, "dispersion": 0.0, "qualified_state_count": 1}
_single_uninit = route_output([_qs("the_uninitiated", 0.9, 1)])
try:
    _force_pattern("diffuse")
    check("helper: the_uninitiated + diffuse resolves to the override (Development)",
          effective_resolution_family(_single_uninit, None, {}) == "Development")
    _force_pattern("single_point")
    check("helper: no override for a pattern the state doesn't list",
          effective_resolution_family(_single_uninit, None, {}) == "Intervention")
finally:
    _ct.compute_causation_pattern = _orig_ccp

# End to end: whatever the lead and pattern, Call 1's family == the displayed routing
def _call1_family(out_calls):
    p = next(c[1] for c in out_calls if c[0] == "call1")["messages"][0]["content"]
    return p.split("resolution_family:")[1].splitlines()[0].strip()
_checked = 0
for _pattern in ("diffuse", "single_point"):
    for sid in STATE_CAUSATION_OVERRIDES:
        vec_s = {f: float(getattr(_SP[sid].dimensional_vector, f)) * 3.0 for f in _SP[sid].dimensional_vector.__dataclass_fields__} \\
            if hasattr(_SP[sid].dimensional_vector, "__dataclass_fields__") else None
        if vec_s is None:
            continue
        _force_pattern(_pattern)
        try:
            FAIL.clear(); CALLS.clear()
            sys.modules["anthropic"] = _fake_mod
            try:
                _out = _m.run_accumulated_engine(vec_s, INTAKE_WIRE, 27, {}, [], [], brand="principal_resolution")
            finally:
                if _real_mod is not None: sys.modules["anthropic"] = _real_mod
                else: sys.modules.pop("anthropic", None)
        finally:
            _ct.compute_causation_pattern = _orig_ccp
        _routing = _out["private_output"]["resolution_routing"]
        if not _routing or not any(c[0] == "call1" for c in CALLS):
            continue
        from engine.output_synthesis import _family_as_prose
        if _call1_family(CALLS) != _family_as_prose(_tr(_routing)):
            check(f"[{sid} / {_pattern}] Call 1 family matches the displayed pathway", False,
                  f"call1={_call1_family(CALLS)!r} displayed={_tr(_routing)!r}")
        _checked += 1
check(f"end to end: Call 1's family equals the displayed pathway for every override state and pattern ({_checked} runs)",
      _checked > 0)
# Fallback path uses the displayed family too
_force_pattern("diffuse")
try:
    FAIL.clear(); FAIL.add("call1"); CALLS.clear()
    sys.modules["anthropic"] = _fake_mod
    try:
        vec_u = {f: float(getattr(_SP["the_uninitiated"].dimensional_vector, f)) * 3.0
                 for f in _SP["the_uninitiated"].dimensional_vector.__dataclass_fields__}
        _fo = _m.run_accumulated_engine(vec_u, INTAKE_WIRE, 27, {}, [], [], brand="principal_resolution")
    finally:
        if _real_mod is not None: sys.modules["anthropic"] = _real_mod
        else: sys.modules.pop("anthropic", None)
finally:
    _ct.compute_causation_pattern = _orig_ccp
    FAIL.clear()
from engine.data.fallback_synthesis import get_fallback_synthesis
_disp = _tr(_fo["private_output"]["resolution_routing"])
check("fallback path: backup copy is the displayed family's copy",
      _fo["synthesis"]["is_fallback"] and
      _fo["synthesis"]["resolution_framing_text"] == get_fallback_synthesis(_disp, _fo["severity"]["tier"])["resolution_framing_text"],
      f"displayed={_disp!r}")
'''


def apply(path, edits):
    t = path.read_text(encoding='utf-8')
    for old, new, label in edits:
        if t.count(old) != 1:
            print(f'ERROR {path} :: {label} x{t.count(old)}', file=sys.stderr)
            sys.exit(1)
        t = t.replace(old, new, 1)
        print(f'[{path} :: {label}] OK')
    return t


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    a = ap.parse_args()
    ct = apply(CT, CT_EDITS)
    if ct.count(HELPER_ANCHOR) != 1 or 'def effective_resolution_family' in ct:
        print('ERROR: helper anchor', file=sys.stderr)
        sys.exit(1)
    ct = ct.replace(HELPER_ANCHOR, HELPER + HELPER_ANCHOR, 1)
    print(f'[{CT} :: effective_resolution_family helper] OK')
    if 'from engine.output import (' not in ct or 'compute_causation_pattern' not in ct.split('def effective_resolution_family')[0]:
        print('ERROR: compute_causation_pattern not imported before the helper', file=sys.stderr)
        sys.exit(1)
    mn = apply(MN, MN_EDITS)
    pt = PT.read_text(encoding='utf-8')
    i = pt.index('RESULT: {passed} passed')
    ls = pt.rindex('\n', 0, i) + 1
    pt = pt[:ls] + TEST.lstrip('\n') + '\n' + pt[ls:]
    print(f'[{PT} :: override consistency tests] OK')
    if a.dry_run:
        print('DRY RUN -- nothing written.')
        return
    CT.write_text(ct, encoding='utf-8')
    MN.write_text(mn, encoding='utf-8')
    PT.write_text(pt, encoding='utf-8')
    print('WROTE')


if __name__ == '__main__':
    main()
