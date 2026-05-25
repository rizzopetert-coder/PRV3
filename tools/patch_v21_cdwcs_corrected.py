"""
PRV3 — SCD-WCS Correction Patch (Session 24)

Replaces the symmetric CDWCS rank_states() body with the corrected
asymmetric SCD-WCS formulation:
  - Session vector displaced by mu_N (centroid scaled to question count)
  - Profile vector left undisplaced (native space)
  - numpy arrays for vector math

Also adds `import numpy as np` to engine/accumulation.py imports.

Only changes: engine/accumulation.py
  1. numpy import added
  2. rank_states() body replaced

All other Step 3 changes (signature, call sites, narrative threading)
are correct and remain in place.

Usage:
  python tools/patch_v21_cdwcs_corrected.py --dry-run
  python tools/patch_v21_cdwcs_corrected.py --write
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
ACC_PATH = ROOT / "engine" / "accumulation.py"


def apply_patch(path: Path, old: str, new: str, label: str, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        print(f"  [ERROR] '{label}' — old string not found")
        return False
    if count > 1:
        print(f"  [ERROR] '{label}' — matched {count} times (ambiguous)")
        return False
    new_text = text.replace(old, new, 1)
    if dry_run:
        print(f"  [DRY-RUN] {path.relative_to(ROOT)} — {label}")
        old_lines = old.splitlines()
        new_lines = new.splitlines()
        for ln in old_lines[:5]:
            print(f"    - {ln}")
        for ln in new_lines[:5]:
            print(f"    + {ln}")
        if len(old_lines) > 5:
            print(f"    ... ({len(old_lines)} lines total -> {len(new_lines)} lines)")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"  [WRITE]   {path.relative_to(ROOT)} — {label}")
    return True


def run(dry_run: bool):
    errors = []

    # ── 1. Add numpy import ───────────────────────────────────────────────────
    ok = apply_patch(
        ACC_PATH,
        old="import math\nfrom dataclasses import dataclass, field\nfrom typing import Optional",
        new="import math\nimport numpy as np\nfrom dataclasses import dataclass, field\nfrom typing import Optional",
        label="add numpy import",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("numpy import")

    # ── 2. Replace rank_states() body with SCD-WCS ───────────────────────────
    ok = apply_patch(
        ACC_PATH,
        old="""def rank_states(
    accumulated_vector: dict,
    answered_question_count: int,
    salience_weights: Optional[dict] = None,
) -> list:
    \"\"\"
    Compute CDWCS similarity from accumulated_vector to each state profile vector.
    Return list of StateRanking sorted ascending by distance (rank 1 = best match).

    CDWCS — Centroid-Displaced Weighted Cosine Similarity (v21):
      Both the session vector and each profile vector are displaced by the
      empirical noise centroid scaled to the current question count before
      computing cosine similarity. This centers similarity on the deviation
      from expected noise rather than absolute signal magnitude.

      mu_N[f] = MC_CENTROID_39[f] * (answered_question_count / 39.0)
      A_d[f]  = accumulated[f] - mu_N[f]
      B_d[f]  = profile[f] - mu_N[f]
      sim = WCS(A_d, B_d, W) if salience_weights else cosine(A_d, B_d)

    salience_weights: optional dict mapping state_id -> {field: weight_value}.
      When provided, uses weighted cosine similarity per state (WCS). When None,
      falls back to standard unweighted cosine similarity.

    Spec reference: Section II.4 (CDWCS update, v21)
    \"\"\"
    fields = list(DIMENSIONAL_FIELDS)
    scale = answered_question_count / 39.0
    mu = {f: MC_CENTROID_39[f] * scale for f in fields}
    a_d = {f: accumulated_vector.get(f, 0.0) - mu[f] for f in fields}

    results = []
    for sid, profile in STATE_PROFILES.items():
        profile_vec = profile.dimensional_vector.as_dict()
        b_d = {f: profile_vec.get(f, 0.0) - mu[f] for f in fields}
        if salience_weights is not None:
            w = salience_weights.get(sid, {f: 1.0 for f in fields})
            sim = _weighted_cosine_similarity(a_d, b_d, w, fields)
        else:
            sim = _cosine_similarity(a_d, b_d, fields)
        d = 1.0 - sim
        results.append(StateRanking(rank=0, state_id=sid, distance=d, score=sim))

    results.sort(key=lambda r: r.distance)
    for i, r in enumerate(results):
        r.rank = i + 1

    return results""",
        new="""def rank_states(
    accumulated_vector: dict,
    answered_question_count: int,
    salience_weights: Optional[dict] = None,
) -> list:
    \"\"\"
    Compute SCD-WCS similarity from accumulated_vector to each state profile vector.
    Return list of StateRanking sorted ascending by distance (rank 1 = best match).

    SCD-WCS — Session-Centroid-Displaced Weighted Cosine Similarity (v21):
      Only the session vector is displaced by the empirical noise centroid
      (scaled to the current question count). Profile vectors remain in their
      native space. This measures the session's deviation from expected noise
      in the direction of each state profile.

      mu_N    = MC_CENTROID_39 * (answered_question_count / 39.0)
      A_d     = accumulated - mu_N     (session: centroid-displaced)
      B       = profile                 (profile: undisplaced, native space)
      sim = WCS(A_d, B, W) if salience_weights else cosine(A_d, B)

    Magnitude guard: if displaced session vector magnitude < 1e-5 (zero-signal
    or exactly-at-centroid session), all states return score 0.0.

    salience_weights: optional dict mapping state_id -> {field: weight_value}.
      When provided, uses weighted cosine similarity per state. When None,
      falls back to standard unweighted cosine similarity.

    Spec reference: Section II.4 (SCD-WCS update, v21)
    \"\"\"
    fields = list(DIMENSIONAL_FIELDS)
    N = float(answered_question_count)
    scale = N / 39.0

    mu_N = np.array([MC_CENTROID_39[f] * scale for f in fields])
    vec_A = np.array([accumulated_vector.get(f, 0.0) for f in fields])
    vec_A_displaced = vec_A - mu_N

    # Zero-signal or exactly-at-centroid session: no directional information
    if np.linalg.norm(vec_A_displaced) < 1e-5:
        zero_results = [
            StateRanking(rank=0, state_id=sid, distance=1.0, score=0.0)
            for sid in STATE_PROFILES
        ]
        for i, r in enumerate(zero_results):
            r.rank = i + 1
        return zero_results

    results = []
    for sid, profile in STATE_PROFILES.items():
        profile_dict = profile.dimensional_vector.as_dict()
        vec_B = np.array([profile_dict.get(f, 0.0) for f in fields])

        if salience_weights is not None:
            sw = salience_weights.get(sid, {f: 1.0 for f in fields})
            w = np.array([sw.get(f, 1.0) for f in fields])
        else:
            w = np.ones(len(fields))

        num = np.sum(w * vec_A_displaced * vec_B)
        den = (np.sqrt(np.sum(w * vec_A_displaced ** 2)) *
               np.sqrt(np.sum(w * vec_B ** 2)))

        sim = float(num / den) if den > 1e-5 else 0.0
        d = 1.0 - sim
        results.append(StateRanking(rank=0, state_id=sid, distance=d, score=sim))

    results.sort(key=lambda r: r.distance)
    for i, r in enumerate(results):
        r.rank = i + 1

    return results""",
        label="rank_states() — replace symmetric CDWCS with SCD-WCS",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("rank_states() SCD-WCS body")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    if errors:
        print(f"ERRORS ({len(errors)}) — patch NOT applied:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        mode = "DRY-RUN" if dry_run else "WRITTEN"
        print(f"Both patches {mode} successfully. 1 file affected.")
        if dry_run:
            print("Run with --write to apply.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
