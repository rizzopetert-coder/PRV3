"""
PRV3 -- Remove vestigial PrivateOutputBlock.friction_tax_estimate field.

Pre-write confirmation (direct grep, not assumed from the handoff):
  - engine/output.py:286 is the ONLY place this dataclass field is
    declared. Constructed exactly once (build_private_block(),
    engine/output.py:551), which never assigns it -- confirmed via
    direct read of that function, it only receives one QualifiedState
    and a SeverityResult, not the intake context needed.
  - engine/contract.py's `friction_tax_estimate` references (lines 433,
    445, 556) are all the LOCAL variable/dict key computed fresh by
    compute_friction_tax() in assemble_output() -- NOT reads of
    priv.friction_tax_estimate. contract.py stopped reading that
    dataclass field the moment the private-path wiring landed
    (commit 86b2ba4).
  - No asdict()/reflection-based serialization of PrivateOutputBlock
    exists anywhere (checked).
  - Historical patch scripts (patch_cascade_risk_wiring_step1.py,
    patch_causation_pattern_wiring_step2.py,
    patch_trajectory_wiring_step3.py) do contain
    `priv.friction_tax_estimate if priv else None` -- these are already-
    applied, one-off audit-trail scripts representing OLD contract.py
    state before the wiring task replaced that line. Not live code,
    not re-run, left untouched.
  - web/lib/output-renderer.ts:120 reads `payload.friction_tax_estimate`
    -- a different thing entirely (a TypeScript payload field, not this
    Python dataclass field), and confirmed dead code earlier this
    session (zero imports of that file anywhere). Not touched.

Two genuinely live test assertions found and handled:
  - tools/test_output.py:327-328 directly accesses
    `private.friction_tax_estimate` on a real PrivateOutputBlock
    instance -- WOULD raise AttributeError once the field is removed.
    Removed, this specific assertion only.
  - tools/test_contract.py:427-428 checks
    `priv["friction_tax_estimate"] is None` on the ASSEMBLED OUTPUT
    DICT (contract.py's local variable/dict key, not the dataclass
    field) -- unaffected by this removal, confirmed and left untouched.

Usage:
  python tools/patch_remove_vestigial_friction_tax_field.py --dry-run
  python tools/patch_remove_vestigial_friction_tax_field.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PY = REPO_ROOT / "engine" / "output.py"
TEST_OUTPUT_PY = REPO_ROOT / "tools" / "test_output.py"

OUTPUT_PY_EDITS = [
    (
        '      5. resolution_family — one of the five service offerings. LOCKED.\n'
        '      6. friction_tax_estimate — always None here. The real value is\n'
        '         computed directly in engine/contract.py\'s assemble_output(),\n'
        '         which has access to org_size/industry/org_type and the full\n'
        '         multi-state state_ids list that this per-state block does not.\n',

        '      5. resolution_family — one of the five service offerings. LOCKED.\n',
    ),
    (
        '    asset_resolution_anchor_text: str = ""  # LLM-generated at application layer\n'
        '    friction_tax_estimate:      Optional[dict] = None  # {low, high, currency} once computed -- always None here, see build_private_block()\n',

        '    asset_resolution_anchor_text: str = ""  # LLM-generated at application layer\n',
    ),
]

TEST_OUTPUT_PY_EDITS = [
    (
        'check("PrivateOutputBlock liability_condition_text empty (LLM-generated)",\n'
        '      private.liability_condition_text == "")\n'
        'check("PrivateOutputBlock asset_resolution_anchor_text empty (LLM-generated)",\n'
        '      private.asset_resolution_anchor_text == "")\n'
        'check("PrivateOutputBlock friction_tax_estimate None (CALIBRATION TARGET)",\n'
        '      private.friction_tax_estimate is None)\n',

        'check("PrivateOutputBlock liability_condition_text empty (LLM-generated)",\n'
        '      private.liability_condition_text == "")\n'
        'check("PrivateOutputBlock asset_resolution_anchor_text empty (LLM-generated)",\n'
        '      private.asset_resolution_anchor_text == "")\n',
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
    test_output_text, test_output_diffs = _apply(TEST_OUTPUT_PY, TEST_OUTPUT_PY_EDITS)

    print("=" * 72)
    _print_diff("engine/output.py", output_diffs)
    _print_diff("tools/test_output.py", test_output_diffs)
    print("=" * 72)

    if args.dry_run:
        print("DRY RUN -- no files written.")
        return

    OUTPUT_PY.write_text(output_text, encoding="utf-8")
    TEST_OUTPUT_PY.write_text(test_output_text, encoding="utf-8")
    print("WROTE engine/output.py")
    print("WROTE tools/test_output.py")


if __name__ == "__main__":
    main()
