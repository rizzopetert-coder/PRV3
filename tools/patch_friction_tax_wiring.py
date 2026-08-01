"""
PRV3 -- Wire compute_friction_tax() into the private-output path only.

Scope: private output only (Path 1 + Path B). Shareable path deliberately
untouched (Pete's Option 3 call) -- web/app/api/share/create/route.ts,
assemble_output()'s shareable_output construction, and web/lib/types.ts
are NOT touched by this script.

Five files, five edits:
  1. engine/output.py -- PrivateOutputBlock.friction_tax_estimate's type
     fixed from the wrong Optional[float] to Optional[dict] (the real
     {low, high, currency} shape). build_private_block() is NOT changed
     to assign it -- confirmed it structurally can't: it only receives
     one QualifiedState and a SeverityResult, not the intake data
     (org_size/industry/org_type) or the full multi-state state_ids list
     compute_friction_tax() requires. The real value is computed fresh in
     contract.py's assemble_output() (edit 2), which has that context.
     This makes PrivateOutputBlock.friction_tax_estimate permanently
     unassigned (same as before, just correctly typed) and no longer
     read by contract.py at all after this change -- flagged, not fixed
     here (removing the now-dead field is a separate, unprompted cleanup
     question).
  2. engine/contract.py -- replaces the always-None
     `priv.friction_tax_estimate` read at the private_output construction
     site with a real compute_friction_tax() call: state_ids derived from
     the already-built identified_states list's "state_id" keys (confirmed
     against the live shape), severity_tier from sev.tier, org_size/
     industry/org_type from session.intake. Result becomes {low, high,
     currency} when calibration_complete is True, null otherwise -- no
     calibration_complete/org_size_label/severity_scalar surfaced.
  3. web/lib/engine-client.ts -- EngineResult.private_output.
     friction_tax_estimate's inline mirror type fixed from the stale
     `number | null` to `FrictionTaxEstimate | null`, imported from
     @/lib/types (the file already imports IntakeEcho the same way) --
     same recurring inline-mirror-type gap flagged repeatedly this
     session, caught here before it caused a real tsc error once the
     Python-side shape changed.
  4. web/app/api/diagnostic/session/answer/route.ts (Path 1) -- hardcoded
     `friction_tax_estimate: null` replaced with the real pass-through,
     matching the existing pattern used for cascade_risk/causation_pattern/
     trajectory on the same object literal.
  5. web/app/api/result/route.ts (Path B) -- same fix as #4.

web/app/api/share/create/route.ts and web/lib/types.ts are deliberately
NOT included in this script's edits.

Usage:
  python tools/patch_friction_tax_wiring.py --dry-run
  python tools/patch_friction_tax_wiring.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PY = REPO_ROOT / "engine" / "output.py"
CONTRACT_PY = REPO_ROOT / "engine" / "contract.py"
ENGINE_CLIENT_TS = REPO_ROOT / "web" / "lib" / "engine-client.ts"
ANSWER_ROUTE_TS = REPO_ROOT / "web" / "app" / "api" / "diagnostic" / "session" / "answer" / "route.ts"
RESULT_ROUTE_TS = REPO_ROOT / "web" / "app" / "api" / "result" / "route.ts"

# ── 1. engine/output.py ──────────────────────────────────────────────────────

OUTPUT_PY_EDITS = [
    (
        '      6. friction_tax_estimate — CALIBRATION TARGET (separate spec task).\n',
        '      6. friction_tax_estimate — always None here. The real value is\n'
        '         computed directly in engine/contract.py\'s assemble_output(),\n'
        '         which has access to org_size/industry/org_type and the full\n'
        '         multi-state state_ids list that this per-state block does not.\n',
    ),
    (
        '    friction_tax_estimate:      Optional[float] = None  # CALIBRATION TARGET\n',
        '    friction_tax_estimate:      Optional[dict] = None  # {low, high, currency} once computed -- always None here, see build_private_block()\n',
    ),
]

# ── 2. engine/contract.py ────────────────────────────────────────────────────

CONTRACT_PY_EDITS = [
    (
        'from engine.severity import SeverityResult, SEVERITY_TIER_DESCRIPTIONS\n',
        'from engine.severity import SeverityResult, SEVERITY_TIER_DESCRIPTIONS\n'
        'from engine.friction_tax import compute_friction_tax\n',
    ),
    (
        '    # ── private_output ──\n'
        '    priv = session.output_package.private\n'
        '    private_output = {\n'
        '        "opening_text":          priv.state_name if priv else "",\n'
        '        "resolution_routing":    priv.resolution_family if priv else "",\n'
        '        "friction_tax_estimate": priv.friction_tax_estimate if priv else None,\n'
        '        "cascade_risk":          compute_cascade_risk(session.accumulated_vector),\n'
        '        "causation_pattern":     compute_causation_pattern(session.accumulated_vector, routing),\n'
        '        "trajectory":            trajectory_result,\n'
        '    }\n',

        '    # ── private_output ──\n'
        '    priv = session.output_package.private\n'
        '    friction_tax_result = compute_friction_tax(\n'
        '        state_ids=[s["state_id"] for s in identified_states],\n'
        '        severity_tier=sev.tier,\n'
        '        org_size=session.intake.headcount,\n'
        '        industry=session.intake.industry,\n'
        '        org_type=session.intake.org_type,\n'
        '    )\n'
        '    friction_tax_estimate = (\n'
        '        {\n'
        '            "low":      friction_tax_result["low"],\n'
        '            "high":     friction_tax_result["high"],\n'
        '            "currency": friction_tax_result["currency"],\n'
        '        }\n'
        '        if friction_tax_result["calibration_complete"]\n'
        '        else None\n'
        '    )\n'
        '    private_output = {\n'
        '        "opening_text":          priv.state_name if priv else "",\n'
        '        "resolution_routing":    priv.resolution_family if priv else "",\n'
        '        "friction_tax_estimate": friction_tax_estimate,\n'
        '        "cascade_risk":          compute_cascade_risk(session.accumulated_vector),\n'
        '        "causation_pattern":     compute_causation_pattern(session.accumulated_vector, routing),\n'
        '        "trajectory":            trajectory_result,\n'
        '    }\n',
    ),
]

# ── 3. web/lib/engine-client.ts ──────────────────────────────────────────────

ENGINE_CLIENT_EDITS = [
    (
        'import type { IntakeEcho } from "@/lib/types";\n',
        'import type { IntakeEcho, FrictionTaxEstimate } from "@/lib/types";\n',
    ),
    (
        '    friction_tax_estimate: number | null;\n',
        '    friction_tax_estimate: FrictionTaxEstimate | null;\n',
    ),
]

# ── 4. answer/route.ts ───────────────────────────────────────────────────────

ANSWER_ROUTE_EDITS = [
    (
        '    // friction_tax_estimate: null — CALIBRATION TARGET, STATE_MULTIPLIERS\n'
        '    // not set, same as Path B.\n'
        '    friction_tax_estimate: null,\n',

        '    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,\n',
    ),
]

# ── 5. result/route.ts ───────────────────────────────────────────────────────

RESULT_ROUTE_EDITS = [
    (
        '    // friction_tax_estimate: null in Path B (CALIBRATION TARGET — STATE_MULTIPLIERS not set)\n'
        '    friction_tax_estimate: null,\n',

        '    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,\n',
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

    output_text, output_diffs = _apply(OUTPUT_PY, OUTPUT_PY_EDITS)
    contract_text, contract_diffs = _apply(CONTRACT_PY, CONTRACT_PY_EDITS)
    engine_client_text, engine_client_diffs = _apply(ENGINE_CLIENT_TS, ENGINE_CLIENT_EDITS)
    answer_text, answer_diffs = _apply(ANSWER_ROUTE_TS, ANSWER_ROUTE_EDITS)
    result_text, result_diffs = _apply(RESULT_ROUTE_TS, RESULT_ROUTE_EDITS)

    print("=" * 72)
    _print_diff("engine/output.py", output_diffs)
    _print_diff("engine/contract.py", contract_diffs)
    _print_diff("web/lib/engine-client.ts", engine_client_diffs)
    _print_diff("web/app/api/diagnostic/session/answer/route.ts", answer_diffs)
    _print_diff("web/app/api/result/route.ts", result_diffs)
    print("=" * 72)
    print("NOT touched (explicitly out of scope): web/app/api/share/create/route.ts, web/lib/types.ts")
    print("NOT touched (confirmed no change needed): web/components/PrivateOutput.tsx")

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    OUTPUT_PY.write_text(output_text, encoding="utf-8")
    CONTRACT_PY.write_text(contract_text, encoding="utf-8")
    ENGINE_CLIENT_TS.write_text(engine_client_text, encoding="utf-8")
    ANSWER_ROUTE_TS.write_text(answer_text, encoding="utf-8")
    RESULT_ROUTE_TS.write_text(result_text, encoding="utf-8")
    print("\nWROTE engine/output.py")
    print("WROTE engine/contract.py")
    print("WROTE web/lib/engine-client.ts")
    print("WROTE web/app/api/diagnostic/session/answer/route.ts")
    print("WROTE web/app/api/result/route.ts")


if __name__ == "__main__":
    main()
