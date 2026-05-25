"""
PRV3 — CDWCS v21 Implementation Patch (Session 24)

Applies Centroid-Displaced Weighted Cosine Similarity (CDWCS) to the engine.

Changes:
  engine/accumulation.py  — MC_CENTROID_39 constant, rank_states() CDWCS body,
                            answered_question_count param, AccumulationEngine.rank() update
  engine/narrative.py     — answered_question_count threaded through
                            apply_narrative_modulation() and NarrativeModulationEngine.modulate()
  engine/output.py        — rank_states() call updated (len(CORE_SEQUENCE_IDS))
  tools/calibration_runner.py      — rank_states() call updated (39)
  tools/recalibrate_floor_v20_clean.py — rank_states() call updated (len(question_ids))
  tools/test_accumulation.py       — rank_states() call updated (39)
  tools/test_narrative.py          — apply_narrative_modulation() calls updated (39)

NOT touched: tools/recalibrate_floor_v20.py (legacy, broken relative to v21 signature)

Usage:
  python tools/patch_v21_cdwcs.py --dry-run
  python tools/patch_v21_cdwcs.py --write
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]


def apply_patch(path: Path, old: str, new: str, label: str, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        print(f"  [ERROR] '{label}' — old string not found in {path.relative_to(ROOT)}")
        return False
    if count > 1:
        print(f"  [ERROR] '{label}' — old string matched {count} times (ambiguous) in {path.relative_to(ROOT)}")
        return False
    new_text = text.replace(old, new, 1)
    if dry_run:
        print(f"  [DRY-RUN] {path.relative_to(ROOT)} — {label}")
        # Show diff excerpt
        old_lines = old.splitlines()
        new_lines = new.splitlines()
        for ln in old_lines[:4]:
            print(f"    - {ln}")
        for ln in new_lines[:4]:
            print(f"    + {ln}")
        if len(old_lines) > 4:
            print(f"    ... ({len(old_lines)} lines total)")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"  [WRITE]   {path.relative_to(ROOT)} — {label}")
    return True


def run(dry_run: bool):
    errors = []

    # ── 1. engine/accumulation.py — MC_CENTROID_39 constant ──────────────────
    acc_path = ROOT / "engine" / "accumulation.py"

    ok = apply_patch(
        acc_path,
        old="""from engine.data.intake import (
    PRIOR_ADJUSTER_INDEX,
    ROLE_COEFFICIENTS,
    AXIS_MODIFIER_INDEX,
    HIGH_HAZARD_INDUSTRIES,
)""",
        new="""from engine.data.intake import (
    PRIOR_ADJUSTER_INDEX,
    ROLE_COEFFICIENTS,
    AXIS_MODIFIER_INDEX,
    HIGH_HAZARD_INDUSTRIES,
)

# Empirical noise centroid — per-field mean of accumulated vector across N=1000
# random simulations, seed=42, Q01-Q39, v20 clean engine state.
# Derived from tools/diag_v21_accumulated_centroid.py. LOCKED.
MC_CENTROID_39: dict = {
    "aptitude_liability":  3.9565,
    "aptitude_asset":      0.6800,
    "authority_liability": 5.3601,
    "authority_asset":     1.6503,
    "alliance_liability":  2.9859,
    "alliance_asset":      0.1924,
    "attitude_liability":  4.8137,
    "attitude_asset":      0.9795,
}""",
        label="add MC_CENTROID_39 constant",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("accumulation.py: MC_CENTROID_39")

    # ── 2. engine/accumulation.py — rank_states() signature + CDWCS body ─────
    ok = apply_patch(
        acc_path,
        old="""def rank_states(
    accumulated_vector: dict,
    salience_weights: Optional[dict] = None,
) -> list:
    \"\"\"
    Compute similarity from accumulated_vector to each state profile vector.
    Return list of StateRanking sorted ascending by distance (rank 1 = best match).

    distance = 1 - similarity, so rank 1 has the smallest distance and
    the highest similarity score.

    salience_weights: optional dict mapping state_id -> {field: weight_value}.
      When provided, uses weighted cosine similarity per state (WCS). This is
      the Phase 2+ calibration path. When None, falls back to standard unweighted
      cosine similarity — backward-compatible with all existing tests.
      Missing state entries fall back to uniform weights (1.0 per field).

    Spec reference: Section II.4
    \"\"\"
    fields = list(DIMENSIONAL_FIELDS)
    results = []
    for sid, profile in STATE_PROFILES.items():
        profile_vec = profile.dimensional_vector.as_dict()
        if salience_weights is not None:
            w = salience_weights.get(sid, {f: 1.0 for f in fields})
            sim = _weighted_cosine_similarity(accumulated_vector, profile_vec, w, fields)
        else:
            sim = _cosine_similarity(accumulated_vector, profile_vec, fields)
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
        label="rank_states() CDWCS body + answered_question_count param",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("accumulation.py: rank_states() body")

    # ── 3. engine/accumulation.py — AccumulationEngine.rank() call ────────────
    ok = apply_patch(
        acc_path,
        old="        return rank_states(self.session.accumulated_vector, salience_weights)",
        new="        return rank_states(self.session.accumulated_vector, len(self.session.answers_applied), salience_weights)",
        label="AccumulationEngine.rank() — pass len(answers_applied)",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("accumulation.py: AccumulationEngine.rank()")

    # ── 4. engine/narrative.py — apply_narrative_modulation() signature ───────
    narr_path = ROOT / "engine" / "narrative.py"

    ok = apply_patch(
        narr_path,
        old="""def apply_narrative_modulation(
    accumulated_vector: dict,
    extraction_result: NarrativeExtractionResult,
    pre_rankings: list,
) -> tuple:""",
        new="""def apply_narrative_modulation(
    accumulated_vector: dict,
    extraction_result: NarrativeExtractionResult,
    pre_rankings: list,
    answered_question_count: int,
) -> tuple:""",
        label="apply_narrative_modulation() — add answered_question_count param",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("narrative.py: apply_narrative_modulation() signature")

    # ── 5. engine/narrative.py — internal rank_states() call ─────────────────
    ok = apply_patch(
        narr_path,
        old="    post_rankings = rank_states(updated_vector)",
        new="    post_rankings = rank_states(updated_vector, answered_question_count)",
        label="apply_narrative_modulation() — pass answered_question_count to rank_states()",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("narrative.py: internal rank_states() call")

    # ── 6. engine/narrative.py — NarrativeModulationEngine.modulate() ─────────
    ok = apply_patch(
        narr_path,
        old="""    def modulate(
        self,
        accumulated_vector: dict,
        extraction_result: NarrativeExtractionResult,
        pre_rankings: list,
    ) -> tuple:
        \"\"\"
        Apply modulation and return (updated_vector, ceiling_enforced_rankings).
        \"\"\"
        return apply_narrative_modulation(
            accumulated_vector, extraction_result, pre_rankings
        )""",
        new="""    def modulate(
        self,
        accumulated_vector: dict,
        extraction_result: NarrativeExtractionResult,
        pre_rankings: list,
        answered_question_count: int,
    ) -> tuple:
        \"\"\"
        Apply modulation and return (updated_vector, ceiling_enforced_rankings).
        \"\"\"
        return apply_narrative_modulation(
            accumulated_vector, extraction_result, pre_rankings, answered_question_count
        )""",
        label="NarrativeModulationEngine.modulate() — add answered_question_count param",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("narrative.py: NarrativeModulationEngine.modulate()")

    # ── 7. engine/output.py — rank_states() call ─────────────────────────────
    out_path = ROOT / "engine" / "output.py"

    ok = apply_patch(
        out_path,
        old="        rankings = rank_states(accumulated)",
        new="        rankings = rank_states(accumulated, len(CORE_SEQUENCE_IDS))",
        label="output.py — pass len(CORE_SEQUENCE_IDS) to rank_states()",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("output.py: rank_states() call")

    # ── 8. tools/calibration_runner.py — rank_states() call ──────────────────
    cal_path = ROOT / "tools" / "calibration_runner.py"

    ok = apply_patch(
        cal_path,
        old="    rankings  = rank_states(synthetic_vector, SALIENCE_PROFILES)",
        new="    rankings  = rank_states(synthetic_vector, 39, SALIENCE_PROFILES)",
        label="calibration_runner.py — pass 39 to rank_states() (full synthetic traversal)",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("calibration_runner.py: rank_states() call")

    # ── 9. tools/recalibrate_floor_v20_clean.py — rank_states() call ─────────
    recal_path = ROOT / "tools" / "recalibrate_floor_v20_clean.py"

    ok = apply_patch(
        recal_path,
        old="        rankings = rank_states(accumulated, SALIENCE_PROFILES)",
        new="        rankings = rank_states(accumulated, len(question_ids), SALIENCE_PROFILES)",
        label="recalibrate_floor_v20_clean.py — pass len(question_ids) to rank_states()",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("recalibrate_floor_v20_clean.py: rank_states() call")

    # ── 10. tools/test_accumulation.py — rank_states() call ──────────────────
    ta_path = ROOT / "tools" / "test_accumulation.py"

    ok = apply_patch(
        ta_path,
        old="rankings = rank_states(zero_vector)",
        new="rankings = rank_states(zero_vector, 39)",
        label="test_accumulation.py — pass 39 to rank_states()",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("test_accumulation.py: rank_states() call")

    # ── 11–14. tools/test_narrative.py — apply_narrative_modulation() calls ───
    tn_path = ROOT / "tools" / "test_narrative.py"

    ok = apply_patch(
        tn_path,
        old="""updated_vec, final_rankings = apply_narrative_modulation(
    acc_base, low_conf_result, pre_rankings
)""",
        new="""updated_vec, final_rankings = apply_narrative_modulation(
    acc_base, low_conf_result, pre_rankings, 39
)""",
        label="test_narrative.py:266 — pass 39 (low_conf_result call)",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("test_narrative.py: call at line 266")

    ok = apply_patch(
        tn_path,
        old="vec_at_floor, _ = apply_narrative_modulation(acc_base, at_floor_result, pre_rankings)",
        new="vec_at_floor, _ = apply_narrative_modulation(acc_base, at_floor_result, pre_rankings, 39)",
        label="test_narrative.py:282 — pass 39 (at_floor_result call)",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("test_narrative.py: call at line 282")

    ok = apply_patch(
        tn_path,
        old="""vec_above, rankings_above = apply_narrative_modulation(
    acc_base, above_floor_result, pre_rankings
)""",
        new="""vec_above, rankings_above = apply_narrative_modulation(
    acc_base, above_floor_result, pre_rankings, 39
)""",
        label="test_narrative.py:293 — pass 39 (above_floor_result call)",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("test_narrative.py: call at line 293")

    ok = apply_patch(
        tn_path,
        old="updated, final = apply_narrative_modulation(acc_nonzero, ext, pre_rankings)",
        new="updated, final = apply_narrative_modulation(acc_nonzero, ext, pre_rankings, 39)",
        label="test_narrative.py:306 — pass 39 (full pipeline call)",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("test_narrative.py: call at line 306")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    if errors:
        print(f"ERRORS ({len(errors)}) — patch NOT applied:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        mode = "DRY-RUN" if dry_run else "WRITTEN"
        print(f"All 14 patches {mode} successfully. 7 files affected.")
        if dry_run:
            print("Run with --write to apply.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
