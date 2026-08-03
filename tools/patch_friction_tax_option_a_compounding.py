"""
PRV3 Engine -- Friction Tax Option A rescale + multi-state compounding
redesign, per prompts/friction-tax-state-multiplier-methodology.md and
prompts/friction-tax-multistate-compounding-methodology.md (both current
as of commit 8e26267).

DRY-RUN ONLY UNTIL PETE GIVES EXPLICIT GO-AHEAD. Per standing protocol,
--write must not be run without that confirmation, tests must be updated
only after --write, and the result reported back for review before any
commit.

What this rewrites in engine/friction_tax.py:

1. Per-state multiplier + raw_score recompute (all 57 states): raw_score
   changes from a 4-criterion sum (0-8) to a 3-criterion sum (0-6,
   turnover + productivity + decision_quality -- legal excluded from the
   sum but its StateCriterionScore entry is left untouched in each
   state's criteria dict, since Track 2 / the Legal/Compliance
   methodology still needs those scores). multiplier changes from the
   old [1.0, 1.4] interpolation to attritional_fraction(R) = 0.05 + 0.20
   * (R / 6), landing in [0.05, 0.25]. Old and new values for every state
   are computed here from the CURRENTLY LIVE criteria scores (imported
   directly from the module, not retyped), so this is a pure recompute,
   not a re-scoring.

2. Validation block (_STATE_MULTIPLIER_CRITERIA_KEYS loop): raw_score
   check now sums only the 3 attritional criteria (criteria dict still
   carries all 4 keys, including legal); multiplier range assertion
   updated from [1.0, 1.4] to [0.05, 0.25].

3. compute_friction_tax()'s core combination logic replaced entirely:
   mean_multiplier (plain arithmetic mean across identified states) is
   replaced with the Step 1-3 anchor-plus-diminishing-layers design --
   per-criterion aggregation across identified states (geometric decay,
   w_i = 0.5**(i-1)), mapped through the same attritional_fraction
   formula, times multi_channel_severity_loading (K=0.05, breadth 1-3,
   N=1 guard forcing loading=1.0 for a single identified state).

4. Module docstring + STATE_MULTIPLIERS section comment + dataclass
   docstrings updated to describe the new methodology instead of the
   retired 4-criterion / [1.0, 1.4] one.

Usage:
  python tools/patch_friction_tax_option_a_compounding.py --dry-run
  python tools/patch_friction_tax_option_a_compounding.py --write   # DO NOT RUN without Pete's explicit go-ahead
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "engine" / "friction_tax.py"

# Imported fresh so the per-state criteria scores driving the recompute
# are the CURRENTLY LIVE ones, not a stale manual transcription.
sys.path.insert(0, str(REPO_ROOT))
from engine.friction_tax import STATE_MULTIPLIERS  # noqa: E402

_R_MIN = 0.0
_R_MAX = 6.0
_FRACTION_MIN = 0.05
_FRACTION_MAX = 0.25


def _new_multiplier(raw_score: int) -> float:
    # Deliberately NOT rounded. Must be the bit-identical float that
    # _attritional_fraction() (inserted into engine/friction_tax.py below)
    # produces at runtime for a single-state case, so the stored per-state
    # constant and the live multi-state computation collapse to the exact
    # same value at N=1 -- verified, not assumed, per Pete's explicit
    # continuity requirement. Confirmed by direct computation: this
    # produces "ugly" literals like 0.15000000000000002 for raw_score=3
    # rather than a clean 0.15 -- that imprecision is the correct choice
    # here, not a bug, since it matches what the runtime formula actually
    # computes bit-for-bit.
    return _FRACTION_MIN + (_FRACTION_MAX - _FRACTION_MIN) * ((raw_score - _R_MIN) / (_R_MAX - _R_MIN))


# ============================================================
# Part 1 -- per-state multiplier / raw_score recompute (57 states)
# ============================================================

_STATE_BLOCK_RE = re.compile(
    r'"(?P<sid>[a-z_]+)":\s*StateMultiplierEntry\(\s*\n'
    r'\s*multiplier=(?P<old_mult>[0-9.]+),\s*\n'
    r'\s*raw_score=(?P<old_raw>\d+),\s*\n'
)


def _recompute_state_blocks(text: str) -> tuple[str, list[str]]:
    report: list[str] = []

    def _sub(m: re.Match) -> str:
        sid = m.group("sid")
        entry = STATE_MULTIPLIERS[sid]
        old_mult_src = m.group("old_mult")
        old_raw_src = int(m.group("old_raw"))

        # Sanity cross-check: the source text's old values must match what
        # the currently-imported module actually holds for this state --
        # if not, the file changed since this script was written and it
        # must not proceed blindly.
        if old_raw_src != entry.raw_score or float(old_mult_src) != entry.multiplier:
            raise AssertionError(
                f"{sid}: source ({old_mult_src}, {old_raw_src}) does not match "
                f"imported module ({entry.multiplier}, {entry.raw_score}) -- "
                f"file has changed since this script was written, aborting."
            )

        t = entry.criteria["turnover"].score
        p = entry.criteria["productivity"].score
        d = entry.criteria["decision_quality"].score
        new_raw = t + p + d
        new_mult = _new_multiplier(new_raw)

        report.append(
            f"  {sid:<38} raw {old_raw_src} -> {new_raw:<3} "
            f"mult {entry.multiplier:<6} -> {new_mult}"
        )

        return (
            f'"{sid}": StateMultiplierEntry(\n'
            f"        multiplier={new_mult},\n"
            f"        raw_score={new_raw},\n"
        )

    new_text, count = _STATE_BLOCK_RE.subn(_sub, text)
    if count != 57:
        raise AssertionError(f"expected 57 state blocks matched, got {count}")
    return new_text, report


# ============================================================
# Part 2 -- validation block
# ============================================================

_OLD_VALIDATION = '''_STATE_MULTIPLIER_CRITERIA_KEYS = {"turnover", "productivity", "decision_quality", "legal"}

for _sid, _entry in STATE_MULTIPLIERS.items():
    assert set(_entry.criteria.keys()) == _STATE_MULTIPLIER_CRITERIA_KEYS, (
        f"{_sid}: criteria keys {set(_entry.criteria.keys())} != "
        f"{_STATE_MULTIPLIER_CRITERIA_KEYS}"
    )
    _criteria_sum = sum(_c.score for _c in _entry.criteria.values())
    assert _criteria_sum == _entry.raw_score, (
        f"{_sid}: raw_score {_entry.raw_score} != sum of criteria scores {_criteria_sum}"
    )
    for _cname, _c in _entry.criteria.items():
        assert 0 <= _c.score <= 2, f"{_sid}.{_cname}: score {_c.score} out of [0, 2]"
    assert 1.0 <= _entry.multiplier <= 1.4, (
        f"{_sid}: multiplier {_entry.multiplier} out of [1.0, 1.4]"
    )
del _sid, _entry, _criteria_sum, _cname, _c'''

_NEW_VALIDATION = '''_STATE_MULTIPLIER_CRITERIA_KEYS = {"turnover", "productivity", "decision_quality", "legal"}
_ATTRITIONAL_CRITERIA_KEYS = ("turnover", "productivity", "decision_quality")
# "legal" remains a required key on every state's criteria dict -- its score
# is still recorded (needed by the separate Legal/Compliance mechanism-aware
# design, prompts/friction-tax-legal-compliance-methodology.md) but is no
# longer part of this rubric's raw_score sum or its multiplier -- see
# prompts/friction-tax-state-multiplier-methodology.md.

for _sid, _entry in STATE_MULTIPLIERS.items():
    assert set(_entry.criteria.keys()) == _STATE_MULTIPLIER_CRITERIA_KEYS, (
        f"{_sid}: criteria keys {set(_entry.criteria.keys())} != "
        f"{_STATE_MULTIPLIER_CRITERIA_KEYS}"
    )
    _criteria_sum = sum(_entry.criteria[_k].score for _k in _ATTRITIONAL_CRITERIA_KEYS)
    assert _criteria_sum == _entry.raw_score, (
        f"{_sid}: raw_score {_entry.raw_score} != sum of the 3 attritional "
        f"criteria scores {_criteria_sum} (legal excluded from this sum)"
    )
    for _cname, _c in _entry.criteria.items():
        assert 0 <= _c.score <= 2, f"{_sid}.{_cname}: score {_c.score} out of [0, 2]"
    assert 0.05 <= _entry.multiplier <= 0.25, (
        f"{_sid}: multiplier {_entry.multiplier} out of [0.05, 0.25]"
    )
del _sid, _entry, _criteria_sum, _cname, _c'''


# ============================================================
# Part 3 -- compute_friction_tax() core logic replacement
# ============================================================

_OLD_CORE = '''    state_multiplier_values = [
        STATE_MULTIPLIERS[sid].multiplier if sid in STATE_MULTIPLIERS else None
        for sid in state_ids
    ]

    calibration_complete = (
        payroll_floor is not None
        and org_type_scalar is not None
        and bool(state_ids)
        and all(v is not None for v in state_multiplier_values)
    )

    if not calibration_complete:
        return {
            "low": None,
            "high": None,
            "currency": "USD",
            "org_size_label": org_size,
            "severity_scalar": severity_scalar,
            "calibration_complete": False,
        }

    adjusted_baseline = payroll_floor * org_type_scalar  # type: ignore[operator]
    mean_multiplier = sum(state_multiplier_values) / len(state_multiplier_values)  # type: ignore[arg-type]

    low = round(adjusted_baseline * mean_multiplier * severity_scalar, 2)
    high = round(low * 1.4, 2)'''

_NEW_CORE = '''    state_entries = [STATE_MULTIPLIERS.get(sid) for sid in state_ids]

    calibration_complete = (
        payroll_floor is not None
        and org_type_scalar is not None
        and bool(state_ids)
        and all(e is not None for e in state_entries)
    )

    if not calibration_complete:
        return {
            "low": None,
            "high": None,
            "currency": "USD",
            "org_size_label": org_size,
            "severity_scalar": severity_scalar,
            "calibration_complete": False,
        }

    adjusted_baseline = payroll_floor * org_type_scalar  # type: ignore[operator]

    # Step 1 (Factor A) -- per-criterion aggregation across identified
    # states, anchor-plus-diminishing-layers, geometric decay w_i = 0.5**(i-1).
    # With exactly one identified state this collapses to that state's own
    # criterion scores untouched (single term, weight 1.0) -- verified by
    # tools/test_friction_tax.py's continuity assertions, not just assumed.
    combined_criterion_scores = {
        k: sum(
            (0.5 ** i) * score
            for i, score in enumerate(
                sorted((e.criteria[k].score for e in state_entries), reverse=True)  # type: ignore[union-attr]
            )
        )
        for k in _ATTRITIONAL_CRITERIA_KEYS
    }
    combined_raw_total = sum(combined_criterion_scores.values())

    # Step 2 -- map the combined criterion profile to a payroll-fraction
    # multiplier via the same frozen [0, 6] -> [0.05, 0.25] mapping used
    # for a single state (prompts/friction-tax-state-multiplier-
    # methodology.md). Extrapolates linearly beyond 0.25 if combined_raw_total
    # exceeds 6 -- intentional, per that doc's frozen-range design.
    combined_multiplier = _attritional_fraction(combined_raw_total)

    # Step 3 (Factor B) -- multi-channel severity loading. N=1 guard: with
    # exactly one identified state, loading MUST be exactly 1.0 regardless
    # of how many criteria that state's own scores touch -- explicit, not
    # inferred from the breadth formula, so single-state continuity holds
    # by construction rather than by coincidence.
    breadth = sum(1 for v in combined_criterion_scores.values() if v > 0)
    if len(state_entries) == 1:
        multi_channel_severity_loading = 1.0
    else:
        multi_channel_severity_loading = 1.0 + _MULTI_CHANNEL_SEVERITY_LOADING_K * (breadth - 1)

    low = round(
        adjusted_baseline * combined_multiplier * multi_channel_severity_loading * severity_scalar,
        2,
    )
    high = round(low * 1.4, 2)'''

_NEW_HELPERS = '''

# -- Multi-state compounding (Steps 1-3) -------------------------------------------
# prompts/friction-tax-multistate-compounding-methodology.md. K=0.05 CLOSED
# (Pete's final decision) -- breadth range [1, 3], Legal/Compliance fully
# split out (see prompts/friction-tax-legal-compliance-methodology.md), not
# part of this loop.

_MULTI_CHANNEL_SEVERITY_LOADING_K: float = 0.05


def _attritional_fraction(raw_total: float) -> float:
    """
    Frozen [0, 6] -> [0.05, 0.25] linear mapping (Option A rescale,
    prompts/friction-tax-state-multiplier-methodology.md). R_min/R_max are
    fixed theoretical constants, not derived from observed data, so this
    same function serves both a single state's own raw_score (0-6) and a
    multi-state combined_raw_total (Step 1), which can exceed 6 -- in
    which case this extrapolates linearly past 0.25 rather than clamping,
    intentionally.
    """
    return _FRACTION_MIN + (_FRACTION_MAX - _FRACTION_MIN) * ((raw_total - _R_MIN) / (_R_MAX - _R_MIN))
'''

_R_MIN_CONST = '''_R_MIN: float = 0.0
_R_MAX: float = 6.0
_FRACTION_MIN: float = 0.05
_FRACTION_MAX: float = 0.25
'''


# ============================================================
# Part 4 -- docstring / comment updates (pure documentation, no behavior change)
# ============================================================

_DOC_EDITS: list[tuple[str, str]] = [
    (
        '''Computes an estimated financial consequence range for the identified
organizational state cluster. All three calibration axes are now
populated: PAYROLL_BASELINE_GRID (all 54 cells, industry_wage x
headcount_midpoint), ORG_TYPE_SCALARS, and STATE_MULTIPLIERS (all 57
states scored across the 4-criterion rubric -- see
prompts/friction-tax-state-multiplier-methodology.md).
calibration_complete now returns True for any real, recognized
(org_size, industry, org_type, state_ids) combination. ORG_TYPE_SCALARS
and HEADCOUNT_MIDPOINTS were finalized 2026-08-01, STATE_MULTIPLIERS
2026-08-02 -- see the source note on each entry.''',
        '''Computes an estimated financial consequence range for the identified
organizational state cluster. All three calibration axes are now
populated: PAYROLL_BASELINE_GRID (all 54 cells, industry_wage x
headcount_midpoint), ORG_TYPE_SCALARS, and STATE_MULTIPLIERS (all 57
states scored across a 3-criterion attritional rubric -- turnover,
productivity, decision_quality; Legal/Compliance is fully split out to
its own mechanism-aware design, prompts/friction-tax-legal-compliance-
methodology.md, and is no longer part of this rubric's raw score or
multiplier -- see prompts/friction-tax-state-multiplier-methodology.md).
calibration_complete now returns True for any real, recognized
(org_size, industry, org_type, state_ids) combination. ORG_TYPE_SCALARS
and HEADCOUNT_MIDPOINTS were finalized 2026-08-01, STATE_MULTIPLIERS
2026-08-02, rescaled (Option A) and multi-state compounding redesign
implemented 2026-08-03 -- see the source note on each entry and
prompts/friction-tax-multistate-compounding-methodology.md.''',
    ),
    (
        '''# -- State multiplier table -------------------------------------------------------
# Per-state friction multiplier applied to the adjusted payroll baseline
# (payroll basis, not revenue -- see prompts/friction-tax-unit-decision.md).
# FINALIZED 2026-08-02 -- all 57 states scored across a 4-criterion rubric
# (turnover/retention, productivity/output, decision-quality/velocity,
# legal/compliance), each 0-2, min-max interpolated onto [1.0, 1.4]. See
# prompts/friction-tax-state-multiplier-methodology.md for full methodology.
# Keys: state_id strings matching engine/data/states.py registry (57 states).''',
        '''# -- State multiplier table -------------------------------------------------------
# Per-state attritional_fraction applied to the adjusted payroll baseline
# (payroll basis, not revenue -- see prompts/friction-tax-unit-decision.md).
# FINALIZED 2026-08-02, RESCALED 2026-08-03 (Option A) -- all 57 states
# scored across a 3-criterion attritional rubric (turnover/retention,
# productivity/output, decision-quality/velocity), each 0-2, min-max
# interpolated onto [0.05, 0.25] (payroll fraction), replacing the
# original 4-criterion / [1.0, 1.4] design. Legal/Compliance is no longer
# part of this rubric's raw_score or multiplier -- each state's
# StateCriterionScore for "legal" is still recorded below (needed by the
# separate mechanism-aware design, prompts/friction-tax-legal-compliance-
# methodology.md) but is excluded from raw_score's sum. See
# prompts/friction-tax-state-multiplier-methodology.md for full
# methodology and prompts/friction-tax-multistate-compounding-
# methodology.md for how multiple identified states combine.
# Keys: state_id strings matching engine/data/states.py registry (57 states).''',
    ),
    (
        '''@dataclass(frozen=True)
class StateMultiplierEntry:
    """One state's friction multiplier and its 4-criterion scoring basis."""
    multiplier: float
    raw_score: int
    criteria: dict[str, StateCriterionScore]''',
        '''@dataclass(frozen=True)
class StateMultiplierEntry:
    """
    One state's standalone attritional_fraction (as if it were the only
    identified state) and its scoring basis. raw_score sums only the 3
    attritional criteria (turnover, productivity, decision_quality);
    criteria still carries all 4 keys including "legal", whose score is
    retained for the separate Legal/Compliance design but excluded from
    raw_score and multiplier.
    """
    multiplier: float
    raw_score: int
    criteria: dict[str, StateCriterionScore]''',
    ),
    (
        '''    Sequence: (1) look up (org_size, industry) in PAYROLL_BASELINE_GRID,
    (2) apply ORG_TYPE_SCALARS[org_type].scalar to the grid result, (3)
    compute mean_multiplier via the existing, unchanged averaging logic
    across state_ids, (4) apply severity_scalar (unchanged, LOCKED), (5)
    low = adjusted_baseline * mean_multiplier * severity_scalar,
    high = low * 1.4 (unchanged, LOCKED).''',
        '''    Sequence: (1) look up (org_size, industry) in PAYROLL_BASELINE_GRID,
    (2) apply ORG_TYPE_SCALARS[org_type].scalar to the grid result, (3)
    aggregate each of the 3 attritional criteria across identified states
    via anchor-plus-diminishing-layers (Step 1, geometric decay), (4) map
    the combined criterion total through the same frozen [0, 6] -> [0.05,
    0.25] mapping used for a single state (Step 2, extrapolates linearly
    past 0.25 for combined totals above 6), (5) apply
    multi_channel_severity_loading (Step 3, K=0.05, breadth 1-3, forced to
    1.0 when exactly one state is identified), (6) apply severity_scalar
    (unchanged, LOCKED), (7) low = adjusted_baseline * combined_multiplier
    * multi_channel_severity_loading * severity_scalar, high = low * 1.4
    (unchanged, LOCKED). See prompts/friction-tax-multistate-compounding-
    methodology.md for the full Steps 1-3 design.''',
    ),
]


def apply(dry_run: bool) -> int:
    text = TARGET.read_text(encoding="utf-8")
    report_lines: list[str] = []

    # --- Part 1: per-state recompute ---
    text, state_report = _recompute_state_blocks(text)
    report_lines.append("Per-state recompute (57 states):")
    report_lines.extend(state_report)

    # --- Part 2: validation block ---
    if text.count(_OLD_VALIDATION) != 1:
        print("ERROR: validation block not found or not unique")
        return 1
    text = text.replace(_OLD_VALIDATION, _NEW_VALIDATION, 1)
    report_lines.append("\nValidation block: raw_score check -> 3-criterion sum, multiplier range -> [0.05, 0.25]")

    # --- Part 3: core logic + helpers ---
    if text.count(_OLD_CORE) != 1:
        print("ERROR: compute_friction_tax() core block not found or not unique")
        return 1
    text = text.replace(_OLD_CORE, _NEW_CORE, 1)
    report_lines.append("compute_friction_tax(): mean_multiplier replaced with Steps 1-3 (combined_criterion_score + multi_channel_severity_loading)")

    # Insert helper constants + _attritional_fraction() right before the
    # "-- Core computation --" section marker, so they're defined before
    # compute_friction_tax() uses them.
    marker = "# -- Core computation ---------------------------------------------------------------"
    if text.count(marker) != 1:
        print("ERROR: core computation marker not found or not unique")
        return 1
    text = text.replace(
        marker,
        _R_MIN_CONST + _NEW_HELPERS + "\n" + marker,
        1,
    )
    report_lines.append("Helpers added: _R_MIN/_R_MAX/_FRACTION_MIN/_FRACTION_MAX, _attritional_fraction(), _MULTI_CHANNEL_SEVERITY_LOADING_K")

    # --- Part 4: docstring / comment updates ---
    for i, (old, new) in enumerate(_DOC_EDITS, 1):
        count = text.count(old)
        if count != 1:
            print(f"ERROR: doc edit #{i} -- expected 1 match, found {count}")
            print(f"  old (first 100 chars): {old[:100]!r}")
            return 1
        text = text.replace(old, new, 1)
    report_lines.append(f"Docstrings/comments updated: {len(_DOC_EDITS)} blocks (module header, STATE_MULTIPLIERS section comment, StateMultiplierEntry docstring, compute_friction_tax() docstring)")

    print("\n".join(report_lines))
    print()

    if dry_run:
        print("DRY RUN -- no file written. Awaiting explicit go-ahead before --write.")
    else:
        TARGET.write_text(text, encoding="utf-8")
        print(f"WRITTEN: {TARGET.relative_to(REPO_ROOT)}")

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
