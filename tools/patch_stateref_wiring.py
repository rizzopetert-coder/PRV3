"""
PRV3 -- Tier 4 content population, Part B: complete deferred StateRef
wiring for descriptive_prose now that real content exists (Part A).

Four files, four edits:
  1. web/lib/engine-client.ts -- add descriptive_prose: string to the
     inline EngineResult.state_distribution / .identified_states mirror
     type (an inline mirror, not a shared reference to StateRef -- won't
     pick up the field automatically, same pattern-fix cascade_risk and
     headline needed earlier this session).
  2. web/app/api/diagnostic/session/answer/route.ts (Path 1) -- one-line
     addition to the engineResult.identified_states -> StateRef[] map,
     now that EngineResult carries the field.
  3. web/app/api/result/route.ts -- widen computeWeights()'s input type
     and both its return branches, plus the call-site narrowing map that
     currently discards descriptive_prose before computeWeights() ever
     sees it.
  4. web/app/api/share/create/route.ts -- identical shape to #3.

Usage:
  python tools/patch_stateref_wiring.py --dry-run
  python tools/patch_stateref_wiring.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_CLIENT_TS = REPO_ROOT / "web" / "lib" / "engine-client.ts"
ANSWER_ROUTE_TS = REPO_ROOT / "web" / "app" / "api" / "diagnostic" / "session" / "answer" / "route.ts"
RESULT_ROUTE_TS = REPO_ROOT / "web" / "app" / "api" / "result" / "route.ts"
SHARE_CREATE_ROUTE_TS = REPO_ROOT / "web" / "app" / "api" / "share" / "create" / "route.ts"

# ── 1. engine-client.ts ──────────────────────────────────────────────────────

ENGINE_CLIENT_EDITS = [
    (
        '  state_distribution: Array<{\n'
        '    state_id: string;\n'
        '    state_name: string;\n'
        '    score: number;\n'
        '    rank: number;\n'
        '    above_floor: boolean;\n'
        '  }>;\n',

        '  state_distribution: Array<{\n'
        '    state_id: string;\n'
        '    state_name: string;\n'
        '    score: number;\n'
        '    rank: number;\n'
        '    above_floor: boolean;\n'
        '    descriptive_prose: string;\n'
        '  }>;\n',
    ),
    (
        '  identified_states: Array<{\n'
        '    state_id: string;\n'
        '    state_name: string;\n'
        '    score: number;\n'
        '    distinguishing_language: string | null;\n'
        '  }>;\n',

        '  identified_states: Array<{\n'
        '    state_id: string;\n'
        '    state_name: string;\n'
        '    score: number;\n'
        '    descriptive_prose: string;\n'
        '    distinguishing_language: string | null;\n'
        '  }>;\n',
    ),
]

# ── 2. answer/route.ts ───────────────────────────────────────────────────────

ANSWER_ROUTE_EDITS = [
    (
        '  const stateRefs: StateRef[] = allEngineStates.map((s) => ({\n'
        '    id: s.state_id,\n'
        '    name: s.state_name,\n'
        '    weight: totalScore > 0 ? s.score / totalScore : 1 / allEngineStates.length,\n'
        '  }));\n',

        '  const stateRefs: StateRef[] = allEngineStates.map((s) => ({\n'
        '    id: s.state_id,\n'
        '    name: s.state_name,\n'
        '    weight: totalScore > 0 ? s.score / totalScore : 1 / allEngineStates.length,\n'
        '    descriptive_prose: s.descriptive_prose,\n'
        '  }));\n',
    ),
]

# ── 3 & 4. result/route.ts and share/create/route.ts (identical shape) ───────

def _compute_weights_edits():
    old_fn = (
        'function computeWeights(\n'
        '  states: Array<{ id: string; name: string; score: number }>,\n'
        '  path: "A" | "B"\n'
        '): StateRef[] {\n'
        '  if (states.length === 0) return [];\n'
        '  if (path === "B") {\n'
        '    const w = 1 / states.length;\n'
        '    return states.map((s) => ({ id: s.id, name: s.name, weight: w }));\n'
        '  }\n'
        '  const total = states.reduce((sum, s) => sum + s.score, 0);\n'
        '  return states.map((s) => ({\n'
        '    id: s.id,\n'
        '    name: s.name,\n'
        '    weight: total > 0 ? s.score / total : 1 / states.length,\n'
        '  }));\n'
        '}\n'
    )
    new_fn = (
        'function computeWeights(\n'
        '  states: Array<{ id: string; name: string; score: number; descriptive_prose: string }>,\n'
        '  path: "A" | "B"\n'
        '): StateRef[] {\n'
        '  if (states.length === 0) return [];\n'
        '  if (path === "B") {\n'
        '    const w = 1 / states.length;\n'
        '    return states.map((s) => ({ id: s.id, name: s.name, weight: w, descriptive_prose: s.descriptive_prose }));\n'
        '  }\n'
        '  const total = states.reduce((sum, s) => sum + s.score, 0);\n'
        '  return states.map((s) => ({\n'
        '    id: s.id,\n'
        '    name: s.name,\n'
        '    weight: total > 0 ? s.score / total : 1 / states.length,\n'
        '    descriptive_prose: s.descriptive_prose,\n'
        '  }));\n'
        '}\n'
    )
    return old_fn, new_fn


RESULT_ROUTE_EDITS = [
    _compute_weights_edits(),
    (
        '  const stateRefs = computeWeights(\n'
        '    allEngineStates.map((s) => ({\n'
        '      id: s.state_id,\n'
        '      name: s.state_name,\n'
        '      score: s.score,\n'
        '    })),\n'
        '    "B"\n'
        '  );\n',

        '  const stateRefs = computeWeights(\n'
        '    allEngineStates.map((s) => ({\n'
        '      id: s.state_id,\n'
        '      name: s.state_name,\n'
        '      score: s.score,\n'
        '      descriptive_prose: s.descriptive_prose,\n'
        '    })),\n'
        '    "B"\n'
        '  );\n',
    ),
]

SHARE_CREATE_ROUTE_EDITS = [
    _compute_weights_edits(),
    (
        '  const allStateRefs = computeWeights(\n'
        '    allEngineStates.map((s) => ({\n'
        '      id: s.state_id,\n'
        '      name: s.state_name,\n'
        '      score: s.score,\n'
        '    })),\n'
        '    "B"\n'
        '  );\n',

        '  const allStateRefs = computeWeights(\n'
        '    allEngineStates.map((s) => ({\n'
        '      id: s.state_id,\n'
        '      name: s.state_name,\n'
        '      score: s.score,\n'
        '      descriptive_prose: s.descriptive_prose,\n'
        '    })),\n'
        '    "B"\n'
        '  );\n',
    ),
]


def _apply(path: Path, edits: list) -> tuple[str, list]:
    text = path.read_text(encoding="utf-8")
    diffs = []
    for old, new in edits:
        count = text.count(old)
        if count == 0:
            print(f"ABORT -- anchor not found in {path}:\n{old!r}", file=sys.stderr)
            sys.exit(1)
        if count > 1:
            print(f"ABORT -- anchor not unique ({count} matches) in {path}:\n{old!r}", file=sys.stderr)
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

    engine_client_text, engine_client_diffs = _apply(ENGINE_CLIENT_TS, ENGINE_CLIENT_EDITS)
    answer_text, answer_diffs = _apply(ANSWER_ROUTE_TS, ANSWER_ROUTE_EDITS)
    result_text, result_diffs = _apply(RESULT_ROUTE_TS, RESULT_ROUTE_EDITS)
    share_text, share_diffs = _apply(SHARE_CREATE_ROUTE_TS, SHARE_CREATE_ROUTE_EDITS)

    print("=" * 72)
    _print_diff("web/lib/engine-client.ts", engine_client_diffs)
    _print_diff("web/app/api/diagnostic/session/answer/route.ts", answer_diffs)
    _print_diff("web/app/api/result/route.ts", result_diffs)
    _print_diff("web/app/api/share/create/route.ts", share_diffs)
    print("=" * 72)

    if args.dry_run:
        print("DRY RUN -- no files written.")
        return

    ENGINE_CLIENT_TS.write_text(engine_client_text, encoding="utf-8")
    ANSWER_ROUTE_TS.write_text(answer_text, encoding="utf-8")
    RESULT_ROUTE_TS.write_text(result_text, encoding="utf-8")
    SHARE_CREATE_ROUTE_TS.write_text(share_text, encoding="utf-8")
    print("WROTE web/lib/engine-client.ts")
    print("WROTE web/app/api/diagnostic/session/answer/route.ts")
    print("WROTE web/app/api/result/route.ts")
    print("WROTE web/app/api/share/create/route.ts")


if __name__ == "__main__":
    main()
