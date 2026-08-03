"""
PRV3 -- Rework tools/test_friction_tax.py for the Option A rescale +
multi-state compounding redesign (engine/friction_tax.py, written this
session per commit 8e26267's methodology docs).

DRY-RUN ONLY UNTIL PETE GIVES EXPLICIT GO-AHEAD.

The old test suite's "monkey-patch STATE_MULTIPLIERS[sid].multiplier"
strategy no longer isolates tests from real calibration data, because the
new compute_friction_tax() reads each state's criteria scores directly
(Steps 1-3) and never consults the stored .multiplier field at runtime.
4 of the original 37 checks failed for exactly this reason when the
engine patch landed (verified via a live run against the real module,
not assumed):
  - the two checks built on the old _test_multiplier_entry(0.1) fixture
    (single-state low, Endemic severity) -- fixture now needs to set real
    criteria scores, not a bare multiplier
  - "multi-state averaging: mean_multiplier is the real arithmetic mean"
    -- fundamentally wrong under the new design, which explicitly
    replaces plain averaging with anchor-plus-diminishing-layers
  - the STATE_MULTIPLIERS range assertion, still checking [1.0, 1.4]

Full rework (not a minimal patch): replaces the fixture, replaces the
multi-state test with hand-derived Step 1/Step 3 math (geometric decay,
breadth, K=0.05), and adds explicit coverage for properties Pete flagged
as critical that the old suite never tested at all -- single-state
continuity across several real states, the N=1 guard, and extrapolation
beyond R_max=6. Every hand-derived expected value in the new file was
verified by actually running it against the live engine before this
patch script was written, not just reasoned about.

Usage:
  python tools/patch_test_friction_tax_option_a_compounding.py --dry-run
  python tools/patch_test_friction_tax_option_a_compounding.py --write   # DO NOT RUN without Pete's explicit go-ahead
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "test_friction_tax.py"
NEW_CONTENT_PATH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad\test_friction_tax_new.py"
)

# Marker confirming the file is still the pre-rework version this script
# was written against -- if the mean_multiplier language is gone, the
# file changed since this script was authored and it must not proceed.
_MARKER = "mean_multiplier is the real arithmetic mean of both states"


def apply(dry_run: bool) -> int:
    current = TARGET.read_text(encoding="utf-8")
    if _MARKER not in current:
        print(f"ERROR: expected marker not found in {TARGET}: {_MARKER!r}")
        print("  File may have changed since this script was written, aborting.")
        return 1

    new_content = NEW_CONTENT_PATH.read_text(encoding="utf-8")

    if dry_run:
        print(f"OK (dry-run): {TARGET.relative_to(REPO_ROOT)} -- marker confirmed present, "
              f"would rewrite ({len(current)} -> {len(new_content)} chars)")
        print("DRY RUN -- no file written. Awaiting explicit go-ahead before --write.")
    else:
        TARGET.write_text(new_content, encoding="utf-8")
        print(f"WRITTEN: {TARGET.relative_to(REPO_ROOT)} ({len(current)} -> {len(new_content)} chars)")

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
