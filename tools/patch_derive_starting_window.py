"""
MC_CENTROID_39 recalibration -- window warm-start fix.

Adds derive_starting_window() verbatim from Gemini's review, and swaps
main()'s hardcoded `window = 0.20` for a call to it -- the counterpart to
derive_scalars()'s existing warm-start, closing the gap found this
session (scalars warm-started correctly to Step 3's converged values,
but window was still hardcoded to 0.20 instead of the committed 0.3500,
producing a 102/172 Round-0 baseline instead of 113/172).

Confirmed before writing: the integration point (main() line 414, before
Round 0's dry-run smoke test) sits well above the existing baseline_cal
call (Round-0 calibration pass, under "Baseline sink-count capture"),
which itself is unchanged -- no duplicate calibration-pass call
introduced, Rule A/B and baseline_tier_counts wiring untouched.

derive_starting_window() added exactly as given (no reconciliation --
Pete's explicit instruction, it's self-contained and doesn't touch
anything from the last commit). Only the single-line swap plus a
matching print statement are new integration surface.

Usage:
  python tools/patch_derive_starting_window.py --dry-run
  python tools/patch_derive_starting_window.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS_PATH = REPO_ROOT / "tools" / "harness_s27_autonomous_calibration.py"

EDITS: list[tuple[str, str]] = []


def edit(old: str, new: str):
    EDITS.append((old, new))


# 1. Add derive_starting_window() verbatim, right after derive_scalars(),
#    before the "Step 2" section heading.
edit(
    '        return dict(CENTROID_FIELD_SCALARS), "warm_start"\n'
    '\n'
    '    print("[HARNESS] CENTROID_FIELD_SCALARS empty — cold-start from _QDATA")\n'
    '    scalars = compute_primary_target_counts()\n'
    '    return scalars, "cold_start"\n'
    '\n'
    '\n'
    '# ── Step 2: Write CENTROID_FIELD_SCALARS to accumulation.py ───────────────────\n',
    '        return dict(CENTROID_FIELD_SCALARS), "warm_start"\n'
    '\n'
    '    print("[HARNESS] CENTROID_FIELD_SCALARS empty — cold-start from _QDATA")\n'
    '    scalars = compute_primary_target_counts()\n'
    '    return scalars, "cold_start"\n'
    '\n'
    '\n'
    'def derive_starting_window() -> tuple[float, str]:\n'
    '    """\n'
    '    Dynamically read the committed SCD_WCS_CLUSTER_WINDOW from tools/calibration_runner.py.\n'
    '\n'
    '    Returns:\n'
    '        tuple[float, str]: (window_value, source_description)\n'
    '    """\n'
    '    try:\n'
    '        from tools.calibration_runner import SCD_WCS_CLUSTER_WINDOW\n'
    '        if SCD_WCS_CLUSTER_WINDOW is not None and isinstance(SCD_WCS_CLUSTER_WINDOW, (int, float)):\n'
    '            return float(SCD_WCS_CLUSTER_WINDOW), "tools.calibration_runner (warm-start)"\n'
    '    except (ImportError, AttributeError):\n'
    '        pass\n'
    '\n'
    '    return 0.20, "hardcoded_default (cold-start fallback)"\n'
    '\n'
    '\n'
    '# ── Step 2: Write CENTROID_FIELD_SCALARS to accumulation.py ───────────────────\n',
)

# 2. Swap the hardcoded window init for the warm-start call, with a
#    matching print statement (derive_starting_window() itself, as given,
#    doesn't print anything -- unlike derive_scalars(), which prints its
#    own diagnostic lines internally).
edit(
    '    # ── Derive starting scalars ────────────────────────────────────────────────\n'
    '    scalars, scalar_source = derive_scalars()\n'
    '    window = 0.20  # v23 starting value\n',
    '    # ── Derive starting scalars ────────────────────────────────────────────────\n'
    '    scalars, scalar_source = derive_scalars()\n'
    '    window, window_source = derive_starting_window()\n'
    '    print(f"[HARNESS] Loaded cluster window from: {window_source}")\n'
    '    print(f"[HARNESS] Initial window: {window:.4f}")\n',
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = HARNESS_PATH.read_text(encoding="utf-8")
    for i, (old, new) in enumerate(EDITS, 1):
        count = content.count(old)
        if count != 1:
            print(f"ABORT: edit {i}: expected exactly 1 match for anchor, found {count}")
            print(f"  anchor (first 150 chars): {old[:150]!r}")
            sys.exit(1)
        content = content.replace(old, new, 1)

    if args.dry_run:
        print(f"=== tools/harness_s27_autonomous_calibration.py: {len(EDITS)} edit(s) would apply cleanly ===")
    else:
        HARNESS_PATH.write_text(content, encoding="utf-8")
        print(f"=== tools/harness_s27_autonomous_calibration.py: {len(EDITS)} edit(s) written ===")


if __name__ == "__main__":
    main()
