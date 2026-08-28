"""
tools/scdwcs_validator.py

SCD-WCS Component 1: regression validator. Evaluates a candidate change
against the full calibration suite -- either a single state's
dimensional_vector and/or SALIENCE_PROFILES entry, or a joint candidate
across multiple states applied simultaneously -- reporting whether the
candidate's own dedicated profiles are reclaimed (per state, and in
aggregate for joint candidates) and what blast radius the change has on
every other state's own rank-1/top-3 standing.

Multi-state extension (this session, following the rank-3/IPM cluster-
wide mechanism diagnosis -- see prompts/scd-wcs-remediation-tracker.md,
the "Stage 4" entry): evaluate_candidate() accepts either a single
state_id string (original contract, unchanged) or a list of (state_id,
new_vector, new_salience) tuples, applied atomically and simultaneously
before scoring. This exists because SCD-WCS's per-state self-
normalization makes single-state-at-a-time evaluation of a joint
candidate mathematically invalid -- a candidate touching all 8 rank-3
members has to be scored with all 8 mutations live at once, not one at
a time while the other 7 sit at baseline. No automated multi-state
search is implemented here or planned -- this remains a pure evaluation
engine for manually-authored joint hypotheses; candidate authoring
stays a human decision, same as the existing single-state contract.

Consolidates three blast-radius methodologies previously reimplemented
ad hoc across 31 untracked tools/_scdwcs_*.py / _candidate*.py scratch
scripts (full inventory and independent verification of this design:
see tools/_mob.txt, session log entries for this build):

  - mode="rank1"      (hard gate): only rank-1 identity changes count.
  - mode="top3"       (DEFAULT, verified sound this session): rank-1
    changes are hard flags (rank1_flips); rank 2-3 displacement is
    softer ripple context (top3_ripples). Chosen as the default because
    the other two real methodologies each have a confirmed blind spot:
    coarse suite-level pass/fail (calibration_runner.py's
    SCD_WCS_CLUSTER_WINDOW = 0.35 cluster criterion) can miss a real
    rank-1 flip entirely if the flip lands inside that window -- the
    suite's own pass/fail text never goes red. Full score-diff flags
    every floating-point epsilon wobble on every state as
    "contamination," most of it not a real signal.
  - mode="score_diff" (--diff-scores, diagnostic only): every state,
    every profile, any score movement at all versus a freshly-computed
    baseline. Real signal, but buried in noise unless you already know
    what you're looking for -- opt-in, never the default, not used by
    the candidate-search sweep loop.

Uses tools/calibration_runner.py's _run_profile_core() directly -- the
same trusted, unmodified measurement core every existing scratch script
already shared (confirmed this session: every one of the 31 scripts
calls into this same primitive, none reimplement their own scoring
math). calibration_runner.py itself is never modified by this file.

Baseline: tools/data/scdwcs_baseline.json, committed and tracked in git
(unlike the untracked scratch corpus this replaces). Loaded once, on
first use, and asserted against the live ALL_PROFILES/STATE_PROFILES
counts -- a mismatch raises BaselineStalenessError rather than silently
comparing against a baseline that no longer reflects the real taxonomy.
Rebaseline only via the --rebaseline CLI flag (or the rebaseline()
function directly) -- never automatic, never implicit inside
evaluate_candidate().

CLI usage (ad hoc single-candidate check, mirrors evaluate_candidate()):
  python tools/scdwcs_validator.py --state STATE_ID \\
      --vector field=value [field=value ...] \\
      --salience field=value [field=value ...] \\
      [--mode rank1|top3|score_diff] [--diff-scores]

  python tools/scdwcs_validator.py --rebaseline
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.salience import SALIENCE_PROFILES
from tools.calibration_runner import ALL_PROFILES, _run_profile_core

BASELINE_PATH = REPO_ROOT / "tools" / "data" / "scdwcs_baseline.json"

VALID_MODES = ("rank1", "top3", "score_diff")
DEFAULT_MODE = "top3"


class BaselineStalenessError(RuntimeError):
    """
    Raised when the committed baseline's integrity header (taxonomy_state_
    count, profile_count) doesn't match the live STATE_PROFILES/ALL_PROFILES
    counts, or when no baseline file exists yet. Never silently proceeds
    on a stale or missing baseline -- the caller must run --rebaseline
    explicitly.
    """


# ---------------------------------------------------------------------------
# Report shapes
# ---------------------------------------------------------------------------

@dataclass
class RankFlip:
    test_id: str
    target_state: str
    baseline_rank1: Optional[str]
    candidate_rank1: Optional[str]


@dataclass
class Top3Ripple:
    test_id: str
    target_state: str
    state_id: str
    baseline_rank: Optional[int]
    candidate_rank: Optional[int]


@dataclass
class ScoreDelta:
    test_id: str
    target_state: str
    state_id: str
    baseline_score: Optional[float]
    candidate_score: Optional[float]


@dataclass
class ValidationReport:
    modified_states: list           # list[str] -- 1 entry for a single-state call, N for a joint candidate
    mode: str
    target_reclaimed: bool          # True iff EVERY state in modified_states reclaims 100% of its own profiles
    target_rank1_count: int         # sum of own_wins across modified_states
    target_profile_count: int       # sum of total_own across modified_states
    per_state_breakdown: dict = field(default_factory=dict)  # state_id -> {own_wins, total_own, reclaimed, min_headroom_gap, min_headroom_test_id}
    rank1_flips: list = field(default_factory=list)      # list[RankFlip]
    top3_ripples: list = field(default_factory=list)      # list[Top3Ripple]
    min_headroom_gap: Optional[float] = None
    min_headroom_test_id: Optional[str] = None
    score_diff: Optional[list] = None                     # list[ScoreDelta], score_diff mode only

    def summary_line(self) -> str:
        recl = "RECLAIMED" if self.target_reclaimed else "not reclaimed"
        gap = f"{self.min_headroom_gap:.6f}" if self.min_headroom_gap is not None else "N/A"
        states_label = (
            self.modified_states[0] if len(self.modified_states) == 1
            else f"{len(self.modified_states)} states ({', '.join(self.modified_states)})"
        )
        return (
            f"{states_label} [{self.mode}]: {recl} "
            f"({self.target_rank1_count}/{self.target_profile_count} own profiles) -- "
            f"rank1_flips={len(self.rank1_flips)} top3_ripples={len(self.top3_ripples)} "
            f"min_headroom_gap={gap}"
        )


# ---------------------------------------------------------------------------
# Baseline: load / integrity check / rebaseline
# ---------------------------------------------------------------------------

_BASELINE_CACHE: Optional[dict] = None


def _git_head_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _rank_top3_for_output(output: dict) -> tuple:
    sd = output.get("state_distribution", [])
    sd_sorted = sorted(sd, key=lambda e: e["rank"])
    rank1 = sd_sorted[0]["state_id"] if sd_sorted else None
    top3 = [e["state_id"] for e in sd_sorted[:3]]
    return rank1, top3, sd


def rebaseline() -> dict:
    """
    Regenerate tools/data/scdwcs_baseline.json from the CURRENT live
    committed engine state (whatever STATE_PROFILES/SALIENCE_PROFILES
    presently are -- no monkeypatch, no candidate applied). Explicit
    only -- never called automatically by evaluate_candidate() or
    get_baseline().
    """
    profiles = {}
    for tc in ALL_PROFILES:
        output, _sev = _run_profile_core(tc)
        rank1, top3, _sd = _rank_top3_for_output(output)
        profiles[tc.test_id] = {
            "target_state": tc.target_state,
            "rank1": rank1,
            "top3": top3,
        }

    baseline = {
        "taxonomy_state_count": len(STATE_PROFILES),
        "profile_count": len(ALL_PROFILES),
        "commit_sha": _git_head_sha(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profiles": profiles,
    }

    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2, sort_keys=True)
        f.write("\n")

    global _BASELINE_CACHE
    _BASELINE_CACHE = baseline
    return baseline


def _load_baseline() -> dict:
    if not BASELINE_PATH.exists():
        raise BaselineStalenessError(
            f"No committed baseline found at {BASELINE_PATH}. "
            f"Run `python tools/scdwcs_validator.py --rebaseline` first."
        )
    with open(BASELINE_PATH, encoding="utf-8") as f:
        baseline = json.load(f)

    live_state_count = len(STATE_PROFILES)
    live_profile_count = len(ALL_PROFILES)
    if baseline.get("taxonomy_state_count") != live_state_count:
        raise BaselineStalenessError(
            f"Baseline taxonomy_state_count={baseline.get('taxonomy_state_count')} "
            f"does not match live STATE_PROFILES count={live_state_count}. "
            f"The taxonomy has changed since this baseline was generated -- "
            f"rebaseline via --rebaseline before evaluating any candidate."
        )
    if baseline.get("profile_count") != live_profile_count:
        raise BaselineStalenessError(
            f"Baseline profile_count={baseline.get('profile_count')} "
            f"does not match live ALL_PROFILES count={live_profile_count}. "
            f"The calibration suite has changed since this baseline was "
            f"generated -- rebaseline via --rebaseline before evaluating "
            f"any candidate."
        )
    return baseline


def get_baseline() -> dict:
    """Loaded once, cached in-process. Raises BaselineStalenessError on
    any staleness or absence -- never silently proceeds."""
    global _BASELINE_CACHE
    if _BASELINE_CACHE is None:
        _BASELINE_CACHE = _load_baseline()
    return _BASELINE_CACHE


# ---------------------------------------------------------------------------
# Candidate application (monkeypatch + guaranteed restore)
# ---------------------------------------------------------------------------

class _CandidateApplied:
    """Context manager: temporarily applies N (state_id, new_vector,
    new_salience) candidate specs to the live engine data, ALL active
    simultaneously, guaranteed to restore every touched state's exact
    original values on exit (including exception paths, and including a
    failure partway through __enter__ itself) -- same always-restore
    discipline every existing scratch script already followed for the
    single-state case, generalized here to N states applied atomically.

    Multi-state extension: originally took a single (modified_state,
    new_vector, new_salience) triple. Now takes a list of such triples
    so a joint candidate's blast radius can be measured with every
    state's mutation live at once -- required for correctness under
    SCD-WCS's per-state self-normalization (see the module docstring
    and evaluate_candidate()'s own docstring for why sequential
    single-state application of a joint candidate would be invalid)."""

    def __init__(self, candidate_specs: list):
        self.specs = candidate_specs
        self._saved: list = []  # [(state_id, orig_vector, had_salience_entry, orig_salience), ...]

    def __enter__(self):
        self._saved = []
        try:
            for state_id, new_vector, new_salience in self.specs:
                orig_vector = STATE_PROFILES[state_id].dimensional_vector
                had_salience_entry = state_id in SALIENCE_PROFILES
                orig_salience = (
                    dict(SALIENCE_PROFILES[state_id]) if had_salience_entry else None
                )
                # Recorded before this state's mutation is applied, so a
                # failure on THIS state (or a later one) still rolls this
                # one back correctly.
                self._saved.append((state_id, orig_vector, had_salience_entry, orig_salience))

                if new_vector is not None:
                    STATE_PROFILES[state_id].dimensional_vector = replace(
                        orig_vector, **new_vector
                    )
                if new_salience is not None:
                    # Partial update -- merge with the current committed entry
                    # (or a uniform 1.0 default per field if the state has no
                    # custom SALIENCE_PROFILES entry at all), same convention
                    # every existing scratch script follows (e.g.
                    # `cand = dict(PS_ORIGINAL_SALIENCE); cand["field"] = mag`).
                    # A bare wholesale replacement would silently drop every
                    # field not explicitly passed -- confirmed as a real bug
                    # via a smoke test before this fix, not assumed safe.
                    base_salience = (
                        dict(orig_salience) if orig_salience is not None
                        else {f: 1.0 for f in DIMENSIONAL_FIELDS}
                    )
                    SALIENCE_PROFILES[state_id] = {**base_salience, **new_salience}
        except Exception:
            # Python's context-manager protocol never calls __exit__ if
            # __enter__ itself raises -- without this, a failure on spec
            # K of N would leave specs 1..K-1 permanently mutated with no
            # rollback. Roll back everything applied so far, then re-raise.
            self._rollback()
            raise
        return self

    def _rollback(self) -> None:
        for state_id, orig_vector, had_salience_entry, orig_salience in reversed(self._saved):
            STATE_PROFILES[state_id].dimensional_vector = orig_vector
            if had_salience_entry:
                SALIENCE_PROFILES[state_id] = orig_salience
            elif state_id in SALIENCE_PROFILES:
                del SALIENCE_PROFILES[state_id]

    def __exit__(self, exc_type, exc, tb):
        self._rollback()
        return False  # never suppress exceptions


def _run_all_profiles() -> dict:
    """One full pass over ALL_PROFILES under whatever engine state is
    currently live. Returns {test_id: {target_state, rank1, top3, sd_by_id}}."""
    results = {}
    for tc in ALL_PROFILES:
        output, _sev = _run_profile_core(tc)
        rank1, top3, sd = _rank_top3_for_output(output)
        results[tc.test_id] = {
            "target_state": tc.target_state,
            "rank1": rank1,
            "top3": top3,
            "sd_by_id": {e["state_id"]: (e["score"], e["rank"]) for e in sd},
        }
    return results


# ---------------------------------------------------------------------------
# evaluate_candidate() -- the public contract
# ---------------------------------------------------------------------------

def evaluate_candidate(
    candidates,
    new_vector: Optional[dict] = None,
    new_salience: Optional[dict] = None,
    mode: str = DEFAULT_MODE,
) -> ValidationReport:
    """
    Evaluate one candidate change against the committed baseline -- a
    single state, or a joint candidate across multiple states applied
    simultaneously.

    Single-state form (original contract, unchanged):
        evaluate_candidate("state_id", new_vector={...}, new_salience={...})
    new_vector / new_salience: partial dicts of only the fields being
    changed (unspecified fields keep their current committed value).
    At least one must be provided.

    Joint multi-state form (new): pass a list of (state_id, new_vector,
    new_salience) tuples as `candidates` instead of a single state_id
    string. The top-level new_vector/new_salience keyword args are
    single-state-form-only and must be omitted here -- each state's own
    change travels inside its own tuple. All N states' mutations are
    applied atomically and are live simultaneously for the single
    _run_all_profiles() pass that scores every profile -- evaluating
    them one at a time while the others sit at baseline would measure
    the wrong thing under SCD-WCS's per-state self-normalization (see
    the module docstring).

    Restores every touched state's original vector/salience before
    returning or raising, regardless of outcome -- no candidate mutation
    is ever left applied to the live in-process engine state after this
    call.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of {VALID_MODES}, got {mode!r}")

    is_joint = not isinstance(candidates, str)
    if is_joint:
        if new_vector is not None or new_salience is not None:
            raise ValueError(
                "new_vector/new_salience are single-state-form-only arguments -- "
                "for a joint multi-state candidate, pass each state's own "
                "new_vector/new_salience inside its own (state_id, new_vector, "
                "new_salience) tuple in the `candidates` list instead."
            )
        candidate_specs = list(candidates)
        if not candidate_specs:
            raise ValueError("candidates list must not be empty")
    else:
        candidate_specs = [(candidates, new_vector, new_salience)]

    modified_states: list = []
    seen_states: set = set()
    for state_id, spec_vector, spec_salience in candidate_specs:
        if state_id not in STATE_PROFILES:
            raise KeyError(f"Unknown state_id: {state_id!r}")
        if state_id in seen_states:
            raise ValueError(f"state_id {state_id!r} appears more than once in candidates")
        seen_states.add(state_id)
        if spec_vector is None and spec_salience is None:
            raise ValueError(f"At least one of new_vector or new_salience must be provided for {state_id!r}")
        if spec_vector is not None:
            unknown_fields = set(spec_vector) - set(DIMENSIONAL_FIELDS)
            if unknown_fields:
                raise ValueError(f"Unknown dimensional_vector field(s) for {state_id!r}: {sorted(unknown_fields)}")
        if spec_salience is not None:
            unknown_fields = set(spec_salience) - set(DIMENSIONAL_FIELDS)
            if unknown_fields:
                raise ValueError(f"Unknown salience field(s) for {state_id!r}: {sorted(unknown_fields)}")
        modified_states.append(state_id)

    modified_set = set(modified_states)

    # Raises BaselineStalenessError here, before any monkeypatching, if
    # the committed baseline is missing or stale -- fail before touching
    # any live state.
    baseline = get_baseline()
    base_profiles = baseline["profiles"]

    fresh_baseline_scores = None
    if mode == "score_diff":
        # Diagnostic mode only: the committed baseline stores rank
        # identities, not raw scores, so a full score-diff needs a
        # fresh pass against the CURRENT (pre-candidate) live state.
        # Not part of the default hot path -- acceptable extra cost for
        # an explicitly opt-in diagnostic.
        fresh_baseline_scores = _run_all_profiles()

    with _CandidateApplied(candidate_specs):
        candidate_profiles = _run_all_profiles()

    # Per-state own-profile reclaim, computed against the FULL joint
    # mutation (all N states already live in candidate_profiles above) --
    # never re-scored one state at a time.
    per_state_breakdown: dict = {}
    for state_id in modified_states:
        own_ids = [tid for tid, p in candidate_profiles.items() if p["target_state"] == state_id]
        own_wins = sum(1 for tid in own_ids if candidate_profiles[tid]["rank1"] == state_id)
        reclaimed = bool(own_ids) and (own_wins == len(own_ids))

        state_min_gap = None
        state_min_gap_tid = None
        for tid, p in candidate_profiles.items():
            sd_by_id = p["sd_by_id"]
            if state_id not in sd_by_id:
                continue
            state_score, state_rank = sd_by_id[state_id]
            if state_rank == 1:
                continue
            rank1_score = next((sc for sid, (sc, rk) in sd_by_id.items() if rk == 1), None)
            if rank1_score is None:
                continue
            gap = rank1_score - state_score
            if state_min_gap is None or gap < state_min_gap:
                state_min_gap = gap
                state_min_gap_tid = tid

        per_state_breakdown[state_id] = {
            "own_wins": own_wins,
            "total_own": len(own_ids),
            "reclaimed": reclaimed,
            "min_headroom_gap": state_min_gap,
            "min_headroom_test_id": state_min_gap_tid,
        }

    # Joint target_reclaimed: True iff EVERY modified state individually
    # reclaims 100% of its own dedicated profiles -- for a single-state
    # call this is exactly the original per-state result, unchanged.
    target_reclaimed = all(b["reclaimed"] for b in per_state_breakdown.values())
    target_rank1_count = sum(b["own_wins"] for b in per_state_breakdown.values())
    target_profile_count = sum(b["total_own"] for b in per_state_breakdown.values())

    # Top-line min-headroom: tightest margin found anywhere across the
    # whole joint set -- for a single-state call this collapses to
    # exactly that one state's own min_gap, byte-identical to before.
    min_gap = None
    min_gap_tid = None
    for b in per_state_breakdown.values():
        if b["min_headroom_gap"] is not None and (min_gap is None or b["min_headroom_gap"] < min_gap):
            min_gap = b["min_headroom_gap"]
            min_gap_tid = b["min_headroom_test_id"]

    rank1_flips: list = []
    top3_ripples: list = []
    score_diffs: Optional[list] = [] if mode == "score_diff" else None

    for tid, cand_p in candidate_profiles.items():
        base_p = base_profiles.get(tid)
        if base_p is None:
            continue  # shouldn't happen once counts match, but never assume

        # Joint candidates restrict ripple detection to third-party
        # profiles only (target_state not in the modified set) -- a
        # modified state's own dedicated profiles flipping is expected
        # work of the candidate, already reported via
        # per_state_breakdown, and would otherwise clutter blast-radius
        # review with N*3 "flips" that aren't surprises at 8-state
        # scale. Single-state calls keep the ORIGINAL, unfiltered-by-
        # target behavior unchanged -- a state's own profile reclaiming
        # has always been visible in rank1_flips there, and existing
        # callers (tools/scdwcs_candidate_search.py, every prior pilot)
        # rely on that, so this filter only activates for is_joint.
        if is_joint and cand_p["target_state"] in modified_set:
            continue

        base_rank1 = base_p["rank1"]
        cand_rank1 = cand_p["rank1"]
        if base_rank1 != cand_rank1:
            rank1_flips.append(RankFlip(
                test_id=tid, target_state=cand_p["target_state"],
                baseline_rank1=base_rank1, candidate_rank1=cand_rank1,
            ))
            continue  # a rank-1 flip is reported once, not doubled as a top3 ripple too

        if mode == "top3":
            base_top3 = base_p["top3"]
            cand_top3 = cand_p["top3"]
            base_ranked = {sid: i + 1 for i, sid in enumerate(base_top3)}
            cand_ranked = {sid: i + 1 for i, sid in enumerate(cand_top3)}
            for sid in set(base_ranked) | set(cand_ranked):
                if sid in modified_set:
                    continue
                b_rank = base_ranked.get(sid)
                c_rank = cand_ranked.get(sid)
                if b_rank != c_rank:
                    top3_ripples.append(Top3Ripple(
                        test_id=tid, target_state=cand_p["target_state"],
                        state_id=sid, baseline_rank=b_rank, candidate_rank=c_rank,
                    ))

        if mode == "score_diff":
            base_sd = fresh_baseline_scores[tid]["sd_by_id"]
            cand_sd = cand_p["sd_by_id"]
            for sid, (c_score, _c_rank) in cand_sd.items():
                if sid in modified_set:
                    continue
                b_entry = base_sd.get(sid)
                b_score = b_entry[0] if b_entry else None
                if b_score != c_score:
                    score_diffs.append(ScoreDelta(
                        test_id=tid, target_state=cand_p["target_state"],
                        state_id=sid, baseline_score=b_score, candidate_score=c_score,
                    ))

    return ValidationReport(
        modified_states=modified_states,
        mode=mode,
        target_reclaimed=target_reclaimed,
        target_rank1_count=target_rank1_count,
        target_profile_count=target_profile_count,
        per_state_breakdown=per_state_breakdown,
        rank1_flips=rank1_flips,
        top3_ripples=top3_ripples,
        min_headroom_gap=min_gap,
        min_headroom_test_id=min_gap_tid,
        score_diff=score_diffs,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_field_values(pairs: list) -> dict:
    out = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"Expected field=value, got {pair!r}")
        field_name, value = pair.split("=", 1)
        out[field_name] = float(value)
    return out


def _print_report(report: ValidationReport) -> None:
    print(report.summary_line())
    if report.rank1_flips:
        print(f"\n  RANK-1 FLIPS ({len(report.rank1_flips)}):")
        for f in report.rank1_flips:
            print(f"    {f.test_id:14s} target={f.target_state:34s} "
                  f"{f.baseline_rank1} -> {f.candidate_rank1}")
    if report.top3_ripples:
        print(f"\n  TOP-3 RIPPLES ({len(report.top3_ripples)}):")
        for r in report.top3_ripples[:30]:
            print(f"    {r.test_id:14s} target={r.target_state:34s} "
                  f"state={r.state_id:34s} rank {r.baseline_rank} -> {r.candidate_rank}")
        if len(report.top3_ripples) > 30:
            print(f"    ... and {len(report.top3_ripples) - 30} more")
    if report.score_diff:
        print(f"\n  SCORE DIFFS ({len(report.score_diff)}):")
        for d in report.score_diff[:30]:
            print(f"    {d.test_id:14s} state={d.state_id:34s} "
                  f"{d.baseline_score} -> {d.candidate_score}")
        if len(report.score_diff) > 30:
            print(f"    ... and {len(report.score_diff) - 30} more")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rebaseline", action="store_true", help="Regenerate tools/data/scdwcs_baseline.json from current live state, then exit.")
    parser.add_argument("--state", help="State_id being modified.")
    parser.add_argument("--vector", nargs="*", default=[], help="dimensional_vector field=value pairs.")
    parser.add_argument("--salience", nargs="*", default=[], help="SALIENCE_PROFILES field=value pairs.")
    parser.add_argument("--mode", default=DEFAULT_MODE, choices=VALID_MODES)
    parser.add_argument("--diff-scores", action="store_true", help="Shortcut for --mode score_diff.")
    args = parser.parse_args()

    if args.rebaseline:
        baseline = rebaseline()
        print(f"Rebaselined: {baseline['profile_count']} profiles, "
              f"{baseline['taxonomy_state_count']} states, commit {baseline['commit_sha']}")
        return

    if not args.state:
        parser.error("--state is required unless --rebaseline is given")

    mode = "score_diff" if args.diff_scores else args.mode
    new_vector = _parse_field_values(args.vector) if args.vector else None
    new_salience = _parse_field_values(args.salience) if args.salience else None

    report = evaluate_candidate(args.state, new_vector, new_salience, mode=mode)
    _print_report(report)


if __name__ == "__main__":
    main()
