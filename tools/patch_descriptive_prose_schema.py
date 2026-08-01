"""
PRV3 -- Tier 4 state-prose schema addition: descriptive_prose

Schema-only addition (Option C, Gemini-reviewed: static field, no LLM/
synthesis involvement). No content populated for any of the 57 states --
that is a separate follow-on task. StateRef gets the field as optional
(Pete's explicit Option 2 call) -- engine-client.ts and the three route
handlers (answer/route.ts, result/route.ts, share/create/route.ts) are
deliberately NOT touched in this task, deferred to the content-
population follow-on when there's a real value and a render target.

Three files, four edits:
  1. engine/data/states.py -- descriptive_prose: str = "" as the 11th
     StateProfile field (default, so _profile()'s signature and every
     existing _profile() call site need zero changes). Future content
     population uses the same post-construction assignment pattern
     already used for dimensional_vector at all 57 registration sites.
  2. engine/contract.py -- add the key to both _IDENTIFIED_STATE_FIELDS
     and _STATE_DISTRIBUTION_ENTRY_FIELDS; validate_schema() picks this
     up automatically since both checks iterate the dicts' .items().
  3. engine/contract.py -- thread STATE_PROFILES[state_id].
     descriptive_prose through all 3 construction points in
     assemble_output(): state_distribution, identified_states
     single-branch, identified_states multi-branch. Same defensive
     "if state_id in STATE_PROFILES else ''" pattern state_name
     already uses.
  4. web/lib/types.ts -- descriptive_prose?: string (optional) on
     StateRef only.

Usage:
  python tools/patch_descriptive_prose_schema.py --dry-run
  python tools/patch_descriptive_prose_schema.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
STATES_PY = REPO_ROOT / "engine" / "data" / "states.py"
CONTRACT_PY = REPO_ROOT / "engine" / "contract.py"
TYPES_TS = REPO_ROOT / "web" / "lib" / "types.ts"

# ── engine/data/states.py ───────────────────────────────────────────────────

STATES_EDITS = [
    (
        '    severity_range:     SeverityRange\n'
        '    resolution_family:  str                  # One of the five service offerings\n',
        '    severity_range:     SeverityRange\n'
        '    resolution_family:  str                  # One of the five service offerings\n'
        '    descriptive_prose:  str = ""             # Static per-state prose, authored separately (Tier 4)\n',
    ),
]

# ── engine/contract.py ───────────────────────────────────────────────────────

CONTRACT_EDITS = [
    # Edit 1: schema constants
    (
        '_STATE_DISTRIBUTION_ENTRY_FIELDS = {\n'
        '    "state_id": str, "state_name": str, "score": float,\n'
        '    "rank": int, "above_floor": bool,\n'
        '}\n'
        '\n'
        '_IDENTIFIED_STATE_FIELDS = {\n'
        '    "state_id": str, "state_name": str, "score": float,\n'
        '    # distinguishing_language: str or None — validated separately\n'
        '}\n',

        '_STATE_DISTRIBUTION_ENTRY_FIELDS = {\n'
        '    "state_id": str, "state_name": str, "score": float,\n'
        '    "rank": int, "above_floor": bool, "descriptive_prose": str,\n'
        '}\n'
        '\n'
        '_IDENTIFIED_STATE_FIELDS = {\n'
        '    "state_id": str, "state_name": str, "score": float,\n'
        '    "descriptive_prose": str,\n'
        '    # distinguishing_language: str or None — validated separately\n'
        '}\n',
    ),
    # Edit 2: state_distribution construction
    (
        '    state_distribution = [\n'
        '        {\n'
        '            "state_id":   r.state_id,\n'
        '            "state_name": STATE_PROFILES[r.state_id].state_name\n'
        '                          if r.state_id in STATE_PROFILES else r.state_id,\n'
        '            "score":      round(r.score, 6),\n'
        '            "rank":       r.rank,\n'
        '            "above_floor": any(\n'
        '                qs.state_id == r.state_id and qs.cleared_floor\n'
        '                for qs in routing.all_evaluated\n'
        '            ),\n'
        '        }\n'
        '        for r in sorted(session.final_rankings, key=lambda r: -r.score)\n'
        '    ]\n',

        '    state_distribution = [\n'
        '        {\n'
        '            "state_id":   r.state_id,\n'
        '            "state_name": STATE_PROFILES[r.state_id].state_name\n'
        '                          if r.state_id in STATE_PROFILES else r.state_id,\n'
        '            "score":      round(r.score, 6),\n'
        '            "rank":       r.rank,\n'
        '            "above_floor": any(\n'
        '                qs.state_id == r.state_id and qs.cleared_floor\n'
        '                for qs in routing.all_evaluated\n'
        '            ),\n'
        '            "descriptive_prose": STATE_PROFILES[r.state_id].descriptive_prose\n'
        '                          if r.state_id in STATE_PROFILES else "",\n'
        '        }\n'
        '        for r in sorted(session.final_rankings, key=lambda r: -r.score)\n'
        '    ]\n',
    ),
    # Edit 3: identified_states single-branch + multi-branch
    (
        '    identified_states = []\n'
        '    if routing.mode == "single" and routing.lead_state:\n'
        '        identified_states = [{\n'
        '            "state_id":              routing.lead_state.state_id,\n'
        '            "state_name":            routing.lead_state.state_name,\n'
        '            "score":                 round(routing.lead_state.score, 6),\n'
        '            "distinguishing_language": None,  # null for single-state per spec\n'
        '        }]\n'
        '    elif routing.mode == "multi":\n'
        '        identified_states = [\n'
        '            {\n'
        '                "state_id":              qs.state_id,\n'
        '                "state_name":            qs.state_name,\n'
        '                "score":                 round(qs.score, 6),\n'
        '                "distinguishing_language": "",  # LLM-generated at application layer\n'
        '            }\n'
        '            for qs in routing.qualified_states\n'
        '        ]\n',

        '    identified_states = []\n'
        '    if routing.mode == "single" and routing.lead_state:\n'
        '        identified_states = [{\n'
        '            "state_id":              routing.lead_state.state_id,\n'
        '            "state_name":            routing.lead_state.state_name,\n'
        '            "score":                 round(routing.lead_state.score, 6),\n'
        '            "descriptive_prose":     STATE_PROFILES[routing.lead_state.state_id].descriptive_prose\n'
        '                                     if routing.lead_state.state_id in STATE_PROFILES else "",\n'
        '            "distinguishing_language": None,  # null for single-state per spec\n'
        '        }]\n'
        '    elif routing.mode == "multi":\n'
        '        identified_states = [\n'
        '            {\n'
        '                "state_id":              qs.state_id,\n'
        '                "state_name":            qs.state_name,\n'
        '                "score":                 round(qs.score, 6),\n'
        '                "descriptive_prose":     STATE_PROFILES[qs.state_id].descriptive_prose\n'
        '                                         if qs.state_id in STATE_PROFILES else "",\n'
        '                "distinguishing_language": "",  # LLM-generated at application layer\n'
        '            }\n'
        '            for qs in routing.qualified_states\n'
        '        ]\n',
    ),
]

# ── web/lib/types.ts ─────────────────────────────────────────────────────────

TYPES_EDITS = [
    (
        'export interface StateRef {\n'
        '  id: string;\n'
        '  name: string;\n'
        '  weight: number;\n'
        '}\n',

        'export interface StateRef {\n'
        '  id: string;\n'
        '  name: string;\n'
        '  weight: number;\n'
        '  descriptive_prose?: string;\n'
        '}\n',
    ),
]


def _apply(text: str, edits: list, label: str) -> tuple[str, list]:
    diffs = []
    for old, new in edits:
        count = text.count(old)
        if count == 0:
            print(f"ABORT -- anchor not found in {label}:\n{old!r}", file=sys.stderr)
            sys.exit(1)
        if count > 1:
            print(f"ABORT -- anchor not unique ({count} matches) in {label}:\n{old!r}", file=sys.stderr)
            sys.exit(1)
        text = text.replace(old, new)
        diffs.append((old, new))
    return text, diffs


def _print_diff(label: str, diffs: list) -> None:
    print(f"--- {label} ---")
    for old, new in diffs:
        for line in old.splitlines():
            print(f"- {line}")
        for line in new.splitlines():
            print(f"+ {line}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    states_text = STATES_PY.read_text(encoding="utf-8")
    contract_text = CONTRACT_PY.read_text(encoding="utf-8")
    types_text = TYPES_TS.read_text(encoding="utf-8")

    states_text, states_diffs = _apply(states_text, STATES_EDITS, "engine/data/states.py")
    contract_text, contract_diffs = _apply(contract_text, CONTRACT_EDITS, "engine/contract.py")
    types_text, types_diffs = _apply(types_text, TYPES_EDITS, "web/lib/types.ts")

    print("=" * 72)
    _print_diff("engine/data/states.py", states_diffs)
    _print_diff("engine/contract.py", contract_diffs)
    _print_diff("web/lib/types.ts", types_diffs)
    print("=" * 72)

    if args.dry_run:
        print("DRY RUN -- no files written.")
        return

    STATES_PY.write_text(states_text, encoding="utf-8")
    CONTRACT_PY.write_text(contract_text, encoding="utf-8")
    TYPES_TS.write_text(types_text, encoding="utf-8")
    print("WROTE engine/data/states.py")
    print("WROTE engine/contract.py")
    print("WROTE web/lib/types.ts")


if __name__ == "__main__":
    main()
