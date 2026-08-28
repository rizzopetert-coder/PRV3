"""
tools/scdwcs_candidate_search.py

SCD-WCS Component 2: candidate search tool. Sweeps one dimensional_vector
or SALIENCE_PROFILES field, on one state, across a uniform linear grid,
calling tools/scdwcs_validator.py's evaluate_candidate() for every step
and printing a human-actionable trade-off table: own-profile recovery
versus blast radius (rank-1 flips + headroom gap), for every candidate
tested.

Uniform linear/fine-grid sweep ONLY. Coarse-then-refine and bisection
are deliberately NOT implemented -- confirmed this session, against real
engine data, that _weighted_cosine_similarity()'s score response to a
single field's weight is genuinely non-monotonic (not just theoretically
possible: 34 of 175 real profiles showed a real direction reversal at
the exact grid density these search scripts already use). A
coarse-then-refine or bisecting search assumes a single trend to
converge on and can walk straight past a narrow stability basin that a
uniform sweep would have caught. See tools/_mob.txt for the full
verification trail.

evaluate_candidate() is the ONLY evaluation engine this file calls --
Component 2 consumes Component 1, per the reviewed interface boundary.
No blast-radius logic is duplicated here.

No auto-apply, no auto-selection of a "winner" beyond presenting the
full table. Final judgment stays human, per this project's own
precedent: the_tolerated_violation pilot was declined on judgment
grounds even where a candidate might have looked technically
acceptable on paper -- this tool reports, it does not decide.

CLI:
  python tools/scdwcs_candidate_search.py --state STATE_ID --axis FIELD \\
      --range MIN MAX STEP --type salience|vector [--mode rank1|top3|score_diff]

Example (reproduces this session's the_tolerated_violation pilot):
  python tools/scdwcs_candidate_search.py --state the_tolerated_violation \\
      --axis attitude --range 0.5 2.2 0.1 --type salience
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.scdwcs_validator import evaluate_candidate, DEFAULT_MODE, VALID_MODES, BaselineStalenessError

# Salience axes conventionally move both liability and asset fields
# together on a state's dominant/secondary axis -- matching every
# existing scratch script's own sweep convention (e.g.
# tools/_scdwcs_tolerated_violation_attitude_search.py's
# attitude_liability=attitude_asset pairing). Vector-type sweeps move a
# single named field only, since dimensional_vector fields are not
# conventionally paired the same way.
SALIENCE_AXIS_FIELD_PAIRS = {
    "aptitude": ("aptitude_liability", "aptitude_asset"),
    "authority": ("authority_liability", "authority_asset"),
    "alliance": ("alliance_liability", "alliance_asset"),
    "attitude": ("attitude_liability", "attitude_asset"),
}


def _frange(lo: float, hi: float, step: float) -> list:
    if step <= 0:
        raise ValueError(f"--range step must be positive, got {step}")
    if hi < lo:
        raise ValueError(f"--range max ({hi}) must be >= min ({lo})")
    n = round((hi - lo) / step)
    values = [round(lo + i * step, 10) for i in range(n + 1)]
    if values[-1] < hi - 1e-9:
        values.append(hi)
    return values


def _build_candidate(sweep_type: str, axis: str, value: float) -> tuple:
    """Returns (new_vector, new_salience) for one sweep step."""
    if sweep_type == "salience":
        if axis in SALIENCE_AXIS_FIELD_PAIRS:
            liability_field, asset_field = SALIENCE_AXIS_FIELD_PAIRS[axis]
            return None, {liability_field: value, asset_field: value}
        # A bare field name (e.g. "attitude_liability" alone, not the
        # paired axis) -- moves only that one field.
        return None, {axis: value}
    elif sweep_type == "vector":
        return {axis: value}, None
    else:
        raise ValueError(f"--type must be 'salience' or 'vector', got {sweep_type!r}")


def run_sweep(state: str, sweep_type: str, axis: str, lo: float, hi: float, step: float, mode: str = DEFAULT_MODE) -> list:
    values = _frange(lo, hi, step)
    rows = []
    for value in values:
        new_vector, new_salience = _build_candidate(sweep_type, axis, value)
        report = evaluate_candidate(state, new_vector=new_vector, new_salience=new_salience, mode=mode)
        rows.append((value, report))
    return rows


def print_trade_off_table(state: str, sweep_type: str, axis: str, rows: list) -> None:
    print("=" * 100)
    print(f"SCD-WCS CANDIDATE SEARCH -- state={state}  type={sweep_type}  axis={axis}  "
          f"steps={len(rows)}")
    print("=" * 100)
    header = f"{'value':>10s}  {'own_reclaimed':>14s}  {'rank1_flips':>11s}  {'top3_ripples':>12s}  {'min_headroom_gap':>17s}  {'at':<14s}"
    print(header)
    print("-" * len(header))
    for value, report in rows:
        recl = f"{report.target_rank1_count}/{report.target_profile_count}" + (" *" if report.target_reclaimed else "")
        gap = f"{report.min_headroom_gap:.6f}" if report.min_headroom_gap is not None else "N/A"
        at = report.min_headroom_test_id or ""
        print(f"{value:>10.4f}  {recl:>14s}  {len(report.rank1_flips):>11d}  {len(report.top3_ripples):>12d}  {gap:>17s}  {at:<14s}")

    print()
    reclaimed_rows = [(v, r) for v, r in rows if r.target_reclaimed]
    zero_flip_rows = [(v, r) for v, r in rows if len(r.rank1_flips) == 0]
    print(f"Candidates with own profiles fully reclaimed: {len(reclaimed_rows)}/{len(rows)}")
    print(f"Candidates with zero rank-1 flips elsewhere:   {len(zero_flip_rows)}/{len(rows)}")
    if reclaimed_rows and zero_flip_rows:
        both = [(v, r) for v, r in rows if r.target_reclaimed and len(r.rank1_flips) == 0]
        print(f"Candidates satisfying BOTH (reclaimed AND zero flips): {len(both)}/{len(rows)}")
        if both:
            print("  (These are the only candidates worth a human look for this axis --")
            print("   this tool does not pick one; that judgment stays with you.)")
    else:
        print("No candidate in the tested range both reclaims the target's own profiles")
        print("and produces zero rank-1 flips elsewhere. This is a real, reportable")
        print("result on its own -- not every axis has a fix, and this tool does not")
        print("pretend otherwise or force a partial-credit selection.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--state", required=True, help="State_id being tested.")
    parser.add_argument("--axis", required=True, help="Field or axis name (e.g. 'attitude' for the paired salience axis, or a bare dimensional_vector field name for --type vector).")
    parser.add_argument("--range", nargs=3, type=float, metavar=("MIN", "MAX", "STEP"), required=True)
    parser.add_argument("--type", choices=("salience", "vector"), required=True)
    parser.add_argument("--mode", default=DEFAULT_MODE, choices=VALID_MODES)
    args = parser.parse_args()

    lo, hi, step = args.range
    try:
        rows = run_sweep(args.state, args.type, args.axis, lo, hi, step, mode=args.mode)
    except BaselineStalenessError as e:
        print(f"BASELINE STALE OR MISSING: {e}", file=sys.stderr)
        sys.exit(1)

    print_trade_off_table(args.state, args.type, args.axis, rows)


if __name__ == "__main__":
    main()
