"""
MC_CENTROID_39 recalibration -- Step 3: update engine/accumulation.py's
MC_CENTROID_39 values and the 39.0 divisor in rank_states() to reflect
the Step 2 regeneration (N=1000, seed=42, against the new 44-question
live PHASE_1_QUESTION_SEQUENCE).

Deliberately NOT renaming MC_CENTROID_39 -- that's a separate naming
decision (Gemini suggested MC_CENTROID_LIVE) Pete hasn't signed off on.
The variable name stays as-is; only its values and the divisor change.
This intentionally leaves the name referencing "39" while the value/
divisor reflect 44 -- a known, deliberate, temporary state pending the
separate rename decision, not an oversight.

Four edits, all in engine/accumulation.py:
  1. MC_CENTROID_39 dict values + its own derivation comment.
  2. CENTROID_FIELD_SCALARS's adjacent derivation comment (references the
     same divisor -- left stale here would recreate the exact
     documented-vs-real mismatch pattern this whole session has been
     correcting elsewhere; the mechanism itself (CENTROID_FIELD_SCALARS
     values) is untouched, Step 4's concern, not this one).
  3. rank_states()'s own docstring formula (mu_N = ... / 39.0 -> / 44.0).
  4. The real code: scale = N / 39.0 -> N / 44.0.

CENTROID_FIELD_SCALARS's actual values are NOT touched here -- they're
managed by tools/harness_s27_autonomous_calibration.py (Step 4), and the
comment says so explicitly ("do not hand-edit").

Usage:
  python tools/patch_step3_accumulation_constants.py --dry-run
  python tools/patch_step3_accumulation_constants.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ACCUMULATION_PATH = REPO_ROOT / "engine" / "accumulation.py"

EDITS: list[tuple[str, str]] = []


def edit(old: str, new: str):
    EDITS.append((old, new))


# 1. MC_CENTROID_39 dict + its own derivation comment
edit(
    '# Empirical noise centroid — per-field mean of accumulated vector across N=1000\n'
    '# random simulations, seed=42, Q01-Q39, v20 clean engine state.\n'
    '# Derived from tools/diag_v21_accumulated_centroid.py. LOCKED.\n'
    'MC_CENTROID_39: dict = {\n'
    '    "aptitude_liability":  3.9565,\n'
    '    "aptitude_asset":      0.6800,\n'
    '    "authority_liability": 5.3601,\n'
    '    "authority_asset":     1.6503,\n'
    '    "alliance_liability":  2.9859,\n'
    '    "alliance_asset":      0.1924,\n'
    '    "attitude_liability":  4.8137,\n'
    '    "attitude_asset":      0.9795,\n'
    '}\n',
    '# Empirical noise centroid — per-field mean of accumulated vector across N=1000\n'
    '# random simulations, seed=42, across the 44 live PHASE_1_QUESTION_SEQUENCE\n'
    '# questions (web/lib/session-store.ts, read live at generation time) --\n'
    '# regenerated this session after Q40-Q51 were added (32 -> 44 live questions).\n'
    '# Original values (37 real questions -- Q03/Q27 were silently unreachable\n'
    '# under the old range-based generation, not 39 despite the name; see\n'
    '# tools/_mob.txt Decision Register for the full MC_CENTROID_39/core-\n'
    '# question-count coupling finding): aptitude_liability 3.9565, aptitude_\n'
    '# asset 0.6800, authority_liability 5.3601, authority_asset 1.6503,\n'
    '# alliance_liability 2.9859, alliance_asset 0.1924, attitude_liability\n'
    '# 4.8137, attitude_asset 0.9795.\n'
    '# Name intentionally NOT changed to reflect 44 -- separate rename decision\n'
    '# (Gemini suggested MC_CENTROID_LIVE), not yet signed off by Pete.\n'
    '# Derived from tools/diag_v21_accumulated_centroid.py. LOCKED.\n'
    'MC_CENTROID_39: dict = {\n'
    '    "aptitude_liability":  3.5307,\n'
    '    "aptitude_asset":      0.5296,\n'
    '    "authority_liability": 6.2624,\n'
    '    "authority_asset":     1.3872,\n'
    '    "alliance_liability":  3.0468,\n'
    '    "alliance_asset":      0.4396,\n'
    '    "attitude_liability":  6.3701,\n'
    '    "attitude_asset":      1.3307,\n'
    '}\n',
)

# 2. CENTROID_FIELD_SCALARS derivation comment (adjacent, same divisor)
edit(
    '# Field-specific centroid displacement scalars — Path B, Session 27.\n'
    '# Scales MC_CENTROID_39 per field: mu_focused[f] = MC_CENTROID_39[f] * scalar[f] * (N/39).\n'
    '# Derived from state_targets coverage per dimension / 39 questions.\n'
    '# Managed by tools/harness_s27_autonomous_calibration.py — do not hand-edit.\n',
    '# Field-specific centroid displacement scalars — Path B, Session 27.\n'
    '# Scales MC_CENTROID_39 per field: mu_focused[f] = MC_CENTROID_39[f] * scalar[f] * (N/44).\n'
    '# Derived from state_targets coverage per dimension / 44 live questions\n'
    '# (updated this session -- was /39, see MC_CENTROID_39 comment above).\n'
    '# Values below are stale pending Step 4 (harness reconvergence) -- not\n'
    '# updated by this step, per Pete\'s explicit Step 3 scope.\n'
    '# Managed by tools/harness_s27_autonomous_calibration.py — do not hand-edit.\n',
)

# 3. rank_states() docstring formula
edit(
    "      mu_N    = MC_CENTROID_39 * (answered_question_count / 39.0)\n",
    "      mu_N    = MC_CENTROID_39 * (answered_question_count / 44.0)\n",
)

# 4. Real code: the divisor itself
edit(
    "    scale = N / 39.0\n",
    "    scale = N / 44.0\n",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = ACCUMULATION_PATH.read_text(encoding="utf-8")
    for i, (old, new) in enumerate(EDITS, 1):
        count = content.count(old)
        if count != 1:
            print(f"ABORT: edit {i}: expected exactly 1 match for anchor, found {count}")
            print(f"  anchor (first 150 chars): {old[:150]!r}")
            sys.exit(1)
        content = content.replace(old, new, 1)

    if args.dry_run:
        print(f"=== engine/accumulation.py: {len(EDITS)} edit(s) would apply cleanly ===")
    else:
        ACCUMULATION_PATH.write_text(content, encoding="utf-8")
        print(f"=== engine/accumulation.py: {len(EDITS)} edit(s) written ===")


if __name__ == "__main__":
    main()
