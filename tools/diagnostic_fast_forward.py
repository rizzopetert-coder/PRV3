#!/usr/bin/env python
"""
PRV3 -- tools/diagnostic_fast_forward.py

Dev-only diagnostic fast-forward tool. PREVIEW ONLY. Drives the REAL live
Path 1 API (session/start, session/answer, and the new session/resume) on
a given Preview deployment -- not the offline calibration_runner.py
harness -- reusing that harness's state-targeting logic
(best_option_for_state / _neutral_option) UNMODIFIED, so the same math
already trusted for calibration decides which option to submit at each
live step. The only genuinely new targeting logic here is severity
targeting (see _severity_option_for_target below), which
generate_answers() never had to solve -- it never simulates severity
follow-ons at all (a known, already-logged gap).

Two modes:
  complete -- answer every question through to completion (target state,
              target severity), including whatever checkpoint
              distinguishers / severity follow-ons / Q28 fire along the
              way -- these are dynamically spliced by the live route, so
              this is a loop following whatever question_id comes back at
              each step, not a precomputed list. On completion, POSTs the
              result to the dev-only /api/dev/diagnostic-preview route and
              prints the resulting browser-viewable URL. Reports the
              ACTUALLY achieved severity read from the real engine result
              -- never assumes the target tier was hit, since only
              duration_band currently carries proven non-zero calibration
              weight (population_band/prior_failed_resolution/
              financial_indicators/named_condition are all still None).
  jump     -- identical driving logic, but stops right before the live
              flow would present the core question at the requested
              static position N (regardless of how many spliced questions
              appeared before it), and prints a /diagnostic?session=<id>
              resume URL instead of completing.

Constraints:
  - Preview only. --base-url must be an explicit Preview deployment URL;
    the known stable Production alias (prv-3.vercel.app) is refused
    outright, before any network call is made.
  - Does not touch engine/question/weight content -- this only calls the
    existing live HTTP endpoints as a scripted user would.
  - No external Python dependencies -- uses urllib.request (stdlib) so
    this runs with zero pip install.

Usage:
  python tools/diagnostic_fast_forward.py complete \\
      --base-url https://prv-3-xxxxx-peter-rizzos-projects.vercel.app \\
      --state the_overloaded_manager --severity Entrenched

  python tools/diagnostic_fast_forward.py jump \\
      --base-url https://prv-3-xxxxx-peter-rizzos-projects.vercel.app \\
      --state the_overloaded_manager --severity Endemic --question 15

Requires VERCEL_AUTOMATION_BYPASS_SECRET in the environment (same bypass
pattern used all session for reaching a Deployment-Protection-gated
Preview deployment) unless passed explicitly via --bypass-secret.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.questions import QUESTION_LIBRARY
from engine.data.states import STATE_PROFILES
from tools.calibration_runner import best_option_for_state, _neutral_option

PRODUCTION_HOST = "prv-3.vercel.app"

TOTAL_CORE_QUESTIONS = 32  # web/lib/session-store.ts's PHASE_1_QUESTION_SEQUENCE.length

DEFAULT_INTAKE = {
    # Numeric midpoint of the old "100-249" bucket -- was a legacy string,
    # confirmed the live source of 4 stale AnonymizedCompletion records in
    # Redis's diagnostic-aggregate list (organization_size collapse recon,
    # 2026-08-29). Fixed ahead of the string|number type collapse so this
    # tool stops producing new legacy-format entries once that ships.
    "organization_size": 175,
    "industry": "Technology",
    "role_level": "C-suite",
    "tenure_in_role": "3-5 years",
    "direct_reports": "6-15",
    "jurisdiction": "CA",
}

# Severity rank, low -> high. Matches the 3-tier SeverityTier vocabulary
# (Emerging/Entrenched/Endemic) engine/severity.py scores against.
_SEVERITY_RANK = {"Emerging": 0, "Entrenched": 1, "Endemic": 2}
_DURATION_BAND_RANK = {"0_6mo": 0, "6_18mo": 1, "18mo_plus": 2}
_POPULATION_BAND_RANK = {"under_10pct": 0, "10_30pct": 1, "30pct_plus": 2}


def _field_rank(field: str, value) -> int:
    if field == "duration_band":
        return _DURATION_BAND_RANK.get(value, 1)
    if field == "population_band":
        return _POPULATION_BAND_RANK.get(value, 1)
    if isinstance(value, bool):
        return 2 if value else 0
    return 1


def _severity_option_for_target(question, target_severity: str):
    """
    Pick the answer_option whose severity_input_mapping pushes closest to
    target_severity's rank. NOT reused from calibration_runner.py --
    generate_answers() never simulates severity follow-ons at all (Session
    72, already logged). Only duration_band currently carries proven
    non-zero calibration weight; whether a requested tier is actually
    reachable depends on how many duration_band-mapped follow-ons happen to
    fire along the state-targeting path chosen elsewhere in this script --
    this function has no control over that. The caller reports the
    ACTUALLY achieved severity from the real engine result at the end.
    """
    target_rank = _SEVERITY_RANK[target_severity]
    best_opt = None
    best_distance = None
    for opt in question.answer_options:
        mapping = opt.severity_input_mapping
        if not mapping:
            continue
        (field, value), = mapping.items()  # exactly one field per option, per questions.py's own contract
        distance = abs(_field_rank(field, value) - target_rank)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_opt = opt
    if best_opt is None:
        # No option carries a severity_input_mapping -- shouldn't happen for
        # a real SEVER-## question, but fall back rather than crash a live
        # session mid-flow.
        return question.answer_options[0]
    return best_opt


def choose_option_id(question_id: str, target_state: str, target_severity: str) -> str:
    """
    Decide which option_id to submit for a live-returned question_id.
    Looks the question up in the SAME QUESTION_LIBRARY the live API's
    get_question_copy() reads from -- option_id values always match what
    the live response returned, by construction (same source of truth).
    """
    question = QUESTION_LIBRARY.get(question_id)
    if question is None:
        raise RuntimeError(f"Unknown question_id from live API: {question_id!r}")

    if question_id.startswith("SEVER-"):
        opt = _severity_option_for_target(question, target_severity)
    else:
        # Core questions, DIST-* checkpoint distinguishers, and Q28 all
        # carry real dimensional_contributions + state_targets -- same
        # logic generate_answers() already uses for high_confidence/
        # moderate profiles, reused unmodified.
        if target_state in (question.state_targets or []):
            opt = best_option_for_state(question, target_state)
        else:
            opt = _neutral_option(question)
    return opt.option_id


class PreviewClient:
    def __init__(self, base_url: str, bypass_secret: str | None):
        self.base_url = base_url.rstrip("/")
        self.bypass_secret = bypass_secret

    def post(self, path: str, body: dict) -> dict:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json", "Origin": self.base_url}
        if self.bypass_secret:
            headers["x-vercel-protection-bypass"] = self.bypass_secret
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raw_err = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"POST {path} failed: HTTP {e.code} -- {raw_err[:500]}") from e
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"POST {path} returned non-JSON (first 300 chars): {raw[:300]!r}. "
                "If this looks like an HTML login page, the Deployment Protection "
                "bypass secret is likely missing or wrong -- check "
                "VERCEL_AUTOMATION_BYPASS_SECRET / --bypass-secret."
            ) from e


def _guard_not_production(base_url: str) -> None:
    host = urlparse(base_url).netloc
    if host == PRODUCTION_HOST:
        raise SystemExit(
            f"REFUSED: {base_url!r} is the known Production alias ({PRODUCTION_HOST}). "
            "This tool is Preview-only -- pass an actual Preview deployment URL, "
            "e.g. https://prv-3-xxxxx-peter-rizzos-projects.vercel.app"
        )


def drive_session(
    client: PreviewClient,
    target_state: str,
    target_severity: str,
    intake: dict,
    stop_before_question: int | None = None,
) -> dict:
    """
    Drives session/start -> session/answer in a loop, following whatever
    question_id the live route actually returns at each step (core,
    DIST-*, SEVER-*, or Q28) rather than a precomputed list -- checkpoints
    and severity follow-ons only exist once the live route decides to
    splice them in.

    If stop_before_question is set (Mode 2), stops right before answering
    the core question at that STATIC position (matching the position
    numbering a real respondent sees, e.g. "Question 15 of 32" --
    unaffected by how many spliced questions preceded it) and returns the
    session_id + next question info instead of completing.
    """
    start_resp = client.post("/api/diagnostic/session/start", intake)
    session_id = start_resp["session_id"]
    question = start_resp["question"]
    label = start_resp["label"]

    while True:
        question_id = question["question_id"]

        if (
            stop_before_question is not None
            and label.get("kind") == "core"
            and label.get("position") == stop_before_question
        ):
            return {
                "mode": "jump",
                "session_id": session_id,
                "next_question": question,
                "label": label,
            }

        option_id = choose_option_id(question_id, target_state, target_severity)

        answer_resp = client.post(
            "/api/diagnostic/session/answer",
            {"session_id": session_id, "question_id": question_id, "option_ids": [option_id]},
        )

        if answer_resp["status"] == "complete":
            return {"mode": "complete", "session_id": session_id, "result": answer_resp["result"]}

        question = answer_resp["question"]
        label = answer_resp["label"]


def main():
    parser = argparse.ArgumentParser(
        description="PRV3 diagnostic fast-forward tool -- Preview only, dev/test.",
    )
    parser.add_argument("mode", choices=["complete", "jump"])
    parser.add_argument(
        "--base-url", required=True,
        help="Preview deployment base URL, e.g. https://prv-3-xxxxx-peter-rizzos-projects.vercel.app",
    )
    parser.add_argument("--state", required=True, help="Target state_id, e.g. the_overloaded_manager")
    parser.add_argument("--severity", required=True, choices=["Emerging", "Entrenched", "Endemic"])
    parser.add_argument(
        "--question", type=int, default=None,
        help="Required for 'jump' mode: stop before this core question number (1-%d)" % TOTAL_CORE_QUESTIONS,
    )
    parser.add_argument(
        "--bypass-secret", default=os.environ.get("VERCEL_AUTOMATION_BYPASS_SECRET"),
        help="Deployment Protection bypass secret (defaults to VERCEL_AUTOMATION_BYPASS_SECRET env var)",
    )
    args = parser.parse_args()

    _guard_not_production(args.base_url)

    if args.state not in STATE_PROFILES:
        raise SystemExit(
            f"Unknown state: {args.state!r}. Must be a real state_id in engine.data.states.STATE_PROFILES."
        )

    if args.mode == "jump":
        if args.question is None:
            raise SystemExit("--question is required for 'jump' mode")
        if not (1 <= args.question <= TOTAL_CORE_QUESTIONS):
            raise SystemExit(f"--question must be between 1 and {TOTAL_CORE_QUESTIONS}")

    if not args.bypass_secret:
        print(
            "WARNING: no bypass secret set -- this will fail if the target deployment "
            "has Deployment Protection enabled. Set VERCEL_AUTOMATION_BYPASS_SECRET or "
            "pass --bypass-secret.",
            file=sys.stderr,
        )

    client = PreviewClient(args.base_url, args.bypass_secret)

    print(
        f"Starting session against {args.base_url} -- "
        f"target_state={args.state} target_severity={args.severity}"
        + (f" stop_before_question={args.question}" if args.mode == "jump" else "")
    )

    outcome = drive_session(
        client,
        target_state=args.state,
        target_severity=args.severity,
        intake=DEFAULT_INTAKE,
        stop_before_question=args.question if args.mode == "jump" else None,
    )

    if outcome["mode"] == "jump":
        resume_url = f"{args.base_url}/diagnostic?session={outcome['session_id']}"
        print(f"\nStopped before question {args.question}.")
        print(f"session_id: {outcome['session_id']}")
        print(f"Resume in a browser: {resume_url}")
        return

    result = outcome["result"]
    achieved_severity = result["severity"]
    match_note = (
        "(MATCH)"
        if achieved_severity == args.severity
        else "(DID NOT MATCH TARGET -- reporting actual result, not assuming)"
    )
    print("\nSession complete.")
    print(f"Target severity: {args.severity}  |  Actually achieved: {achieved_severity}  {match_note}")
    print(
        f"Primary state: {result['primary_state']['id']} ({result['primary_state']['name']}), "
        f"weight={result['primary_state']['weight']:.3f}"
    )

    preview_resp = client.post("/api/dev/diagnostic-preview", result)
    print(f"\nView the completed report: {preview_resp['url']}")


if __name__ == "__main__":
    main()
