"""
tools/scdwcs_validator.py

SCD-WCS Component 1: regression validator. Evaluates a single candidate
change to a state's dimensional_vector and/or SALIENCE_PROFILES entry
against the full calibration suite, reporting whether the candidate's
own dedicated profiles are reclaimed and what blast radius the change
has on every other state's own rank-1/top-3 standing.

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
    modified_state: str
    mode: str
    target_reclaimed: bool
    target_rank1_count: int
    target_profile_count: int
    rank1_flips: list = field(default_factory=list)      # list[RankFlip]
    top3_ripples: list = field(default_factory=list)      # list[Top3Ripple]
    min_headroom_gap: Optional[float] = None
    min_headroom_test_id: Optional[str] = None
    score_diff: Optional[list] = None                     # list[ScoreDelta], score_diff mode only

    def summary_line(self) -> str:
        recl = "RECLAIMED" if self.target_reclaimed else "not reclaimed"
        gap = f"{self.min_headroom_gap:.6f}" if self.min_headroom_gap is not None else "N/A"
        return (
            f"{self.modified_state} [{self.mode}]: {recl} "
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
    """Context manager: temporarily applies new_vector/new_salience to
    modified_state's live engine data, guaranteed to restore the exact
    original values on exit (including exception paths) -- same
    always-restore discipline every existing scratch script already
    follows, enforced structurally here instead of by convention."""

    def __init__(self, modified_state: str, new_vector: Optional[dict], new_salience: Optional[dict]):
        self.modified_state = modified_state
        self.new_vector = new_vector
        self.new_salience = new_salience
        self._orig_vector = None
        self._orig_salience = None
        self._had_salience_entry = False

    def __enter__(self):
        self._orig_vector = STATE_PROFILES[self.modified_state].dimensional_vector
        self._had_salience_entry = self.modified_state in SALIENCE_PROFILES
        self._orig_salience = (
            dict(SALIENCE_PROFILES[self.modified_state]) if self._had_salience_entry else None
        )

        if self.new_vector is not None:
            STATE_PROFILES[self.modified_state].dimensional_vector = replace(
                self._orig_vector, **self.new_vector
            )
        if self.new_salience is not None:
            # Partial update -- merge with the current committed entry
            # (or a uniform 1.0 default per field if the state has no
            # custom SALIENCE_PROFILES entry at all), same convention
            # every existing scratch script follows (e.g.
            # `cand = dict(PS_ORIGINAL_SALIENCE); cand["field"] = mag`).
            # A bare wholesale replacement would silently drop every
            # field not explicitly passed -- confirmed as a real bug
            # via a smoke test before this fix, not assumed safe.
            base_salience = (
                dict(self._orig_salience) if self._orig_salience is not None
                else {f: 1.0 for f in DIMENSIONAL_FIELDS}
            )
            SALIENCE_PROFILES[self.modified_state] = {**base_salience, **self.new_salience}
        return self

    def __exit__(self, exc_type, exc, tb):
        STATE_PROFILES[self.modified_state].dimensional_vector = self._orig_vector
        if self._had_salience_entry:
            SALIENCE_PROFILES[self.modified_state] = self._orig_salience
        elif self.modified_state in SALIENCE_PROFILES:
            del SALIENCE_PROFILES[self.modified_state]
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
    modified_state: str,
    new_vector: Optional[dict] = None,
    new_salience: Optional[dict] = None,
    mode: str = DEFAULT_MODE,
) -> ValidationReport:
    """
    Evaluate one candidate change to modified_state's dimensional_vector
    and/or SALIENCE_PROFILES entry against the committed baseline.

    new_vector / new_salience: partial dicts of only the fields being
    changed (unspecified fields keep their current committed value).
    At least one must be provided.

    Restores modified_state's original vector/salience before returning
    or raising, regardless of outcome -- no candidate mutation is ever
    left applied to the live in-process engine state after this call.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of {VALID_MODES}, got {mode!r}")
    if modified_state not in STATE_PROFILES:
        raise KeyError(f"Unknown state_id: {modified_state!r}")
    if new_vector is None and new_salience is None:
        raise ValueError("At least one of new_vector or new_salience must be provided")
    if new_vector is not None:
        unknown_fields = set(new_vector) - set(DIMENSIONAL_FIELDS)
        if unknown_fields:
            raise ValueError(f"Unknown dimensional_vector field(s): {sorted(unknown_fields)}")
    if new_salience is not None:
        unknown_fields = set(new_salience) - set(DIMENSIONAL_FIELDS)
        if unknown_fields:
            raise ValueError(f"Unknown salience field(s): {sorted(unknown_fields)}")

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

    with _CandidateApplied(modified_state, new_vector, new_salience):
        candidate_profiles = _run_all_profiles()

    own_ids = [tid for tid, p in candidate_profiles.items() if p["target_state"] == modified_state]
    own_wins = sum(1 for tid in own_ids if candidate_profiles[tid]["rank1"] == modified_state)
    target_reclaimed = bool(own_ids) and (own_wins == len(own_ids))

    min_gap = None
    min_gap_tid = None
    for tid, p in candidate_profiles.items():
        sd_by_id = p["sd_by_id"]
        if modified_state not in sd_by_id:
            continue
        state_score, state_rank = sd_by_id[modified_state]
        if state_rank == 1:
            continue
        rank1_score = next((sc for sid, (sc, rk) in sd_by_id.items() if rk == 1), None)
        if rank1_score is None:
            continue
        gap = rank1_score - state_score
        if min_gap is None or gap < min_gap:
            min_gap = gap
            min_gap_tid = tid

    rank1_flips: list = []
    top3_ripples: list = []
    score_diffs: Optional[list] = [] if mode == "score_diff" else None

    for tid, cand_p in candidate_profiles.items():
        base_p = base_profiles.get(tid)
        if base_p is None:
            continue  # shouldn't happen once counts match, but never assume

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
                if sid == modified_state:
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
                if sid == modified_state:
                    continue
                b_entry = base_sd.get(sid)
                b_score = b_entry[0] if b_entry else None
                if b_score != c_score:
                    score_diffs.append(ScoreDelta(
                        test_id=tid, target_state=cand_p["target_state"],
                        state_id=sid, baseline_score=b_score, candidate_score=c_score,
                    ))

    return ValidationReport(
        modified_state=modified_state,
        mode=mode,
        target_reclaimed=target_reclaimed,
        target_rank1_count=own_wins,
        target_profile_count=len(own_ids),
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
