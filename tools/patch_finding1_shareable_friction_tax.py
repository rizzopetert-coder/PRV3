"""
PRV3 -- Fix Finding 1 (Addendum 11): web/app/api/share/create/route.ts
hardcoded friction_tax_estimate: null unconditionally, never reading
engineResult's actual computed value. The comment ("null in Path B
(CALIBRATION TARGET)") predates Option A's calibration completion.
engineResult is called fresh in this route (invokeEngine(), line 169,
before the KV write) and already carries private_output.friction_tax_estimate
on the same EngineResult type the private path already reads correctly
-- confirmed via investigation, no structural gap. One-line fix, scoped
strictly to friction_tax_estimate -- legal_tail_risk_band is explicitly
NOT touched here, per Pete's direction (new functionality, not this bug
fix).

Usage:
  python tools/patch_finding1_shareable_friction_tax.py --dry-run
  python tools/patch_finding1_shareable_friction_tax.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


ROUTE = "web/app/api/share/create/route.ts"

edit(
    ROUTE,
    "    // friction_tax_estimate: null in Path B (CALIBRATION TARGET)\n"
    "    friction_tax_estimate: null,",
    "    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
