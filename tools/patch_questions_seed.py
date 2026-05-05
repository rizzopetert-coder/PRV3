#!/usr/bin/env python
"""
PRV3 — patch_questions_seed.py
Seeds dimensional_contributions in engine/data/questions.py using
Signal Map tier assignments (Session 11, pre-calibration pass).

Source: PRV3_Signal_Map (Drive 1LMx13dWDvAMWwxYHG7ikd9moZLndphNZw66hbejfLqI)

Seeding rules:
  HIGH  (0.60): primary dimension(s) of target state seeded to 0.60
  MEDIUM (0.40): primary dimension(s) of target state seeded to 0.40
  LOW / CLUSTER: no entry — remain at 0.25 baseline

Per-question seeding: highest-weight non-cluster state in state_targets;
first occurrence in targets list when tier is tied. Cluster-only questions
and questions with only LOW-tier states are not seeded.

No asset fields are seeded — liability-only pass.

Usage:
  python tools/patch_questions_seed.py --dry-run
  python tools/patch_questions_seed.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"

# ---------------------------------------------------------------------------
# Seedings table: {qid: (source_state, tier_label, {dim: value})}
# Used for dry-run display and for building NEW_BUILD.
# ---------------------------------------------------------------------------
_SEEDINGS_META = {
    "Q01":           ("the_founders_grip",             "HIGH",   {"authority_liability": 0.60}),
    "Q02":           ("the_exposed",                   "HIGH",   {"authority_liability": 0.60, "aptitude_liability": 0.60}),
    "Q03A":          ("the_unsolved_problem",           "HIGH",   {"authority_liability": 0.60, "attitude_liability": 0.60}),
    "Q03A-D-FOLLOW": ("the_fracture",                  "HIGH",   {"authority_liability": 0.60, "alliance_liability": 0.60}),
    "Q04":           ("hr_capture",                    "HIGH",   {"authority_liability": 0.60, "attitude_liability": 0.60}),
    "Q05":           ("the_untouchable",               "HIGH",   {"attitude_liability": 0.60}),
    "Q06":           ("heard_and_ignored",              "HIGH",   {"authority_liability": 0.60, "attitude_liability": 0.60}),
    "Q07":           ("the_fracture",                  "HIGH",   {"authority_liability": 0.60, "alliance_liability": 0.60}),
    "Q09":           ("the_fracture",                  "HIGH",   {"authority_liability": 0.60, "alliance_liability": 0.60}),
    "Q10":           ("the_paper_tiger",               "HIGH",   {"authority_liability": 0.60, "aptitude_liability": 0.60}),
    "Q11":           ("the_wrong_reward",              "MEDIUM", {"authority_liability": 0.40, "attitude_liability": 0.40}),
    "Q12":           ("the_untouchable",               "HIGH",   {"attitude_liability": 0.60}),
    "Q13":           ("the_lost_map",                  "MEDIUM", {"authority_liability": 0.40, "alliance_liability": 0.40}),
    "Q14":           ("pay_exposure",                  "MEDIUM", {"authority_liability": 0.40, "aptitude_liability": 0.40}),
    "Q15":           ("the_diversity_ceiling",         "MEDIUM", {"attitude_liability": 0.40, "authority_liability": 0.40}),
    "Q16":           ("the_diversity_ceiling",         "MEDIUM", {"attitude_liability": 0.40, "authority_liability": 0.40}),
    "Q17":           ("the_burned_credibility",        "MEDIUM", {"attitude_liability": 0.40, "alliance_liability": 0.40}),
    "Q19":           ("dueling_narratives",            "MEDIUM", {"authority_liability": 0.40, "attitude_liability": 0.40}),
    "Q20":           ("built_to_fail",                 "HIGH",   {"authority_liability": 0.60, "aptitude_liability": 0.60}),
    "Q21":           ("decision_paralysis",            "MEDIUM", {"authority_liability": 0.40, "alliance_liability": 0.40}),
    "Q22":           ("the_policy_lag",                "MEDIUM", {"authority_liability": 0.40, "aptitude_liability": 0.40}),
    "Q23":           ("leadership_continuity_risk",    "MEDIUM", {"authority_liability": 0.40, "aptitude_liability": 0.40}),
    "Q24":           ("invisible_burnout",             "MEDIUM", {"attitude_liability": 0.40, "alliance_liability": 0.40}),
    "Q25":           ("leadership_continuity_risk",    "MEDIUM", {"authority_liability": 0.40, "aptitude_liability": 0.40}),
    "Q26":           ("the_fracture",                  "HIGH",   {"authority_liability": 0.60, "alliance_liability": 0.60}),
    "Q27A":          ("the_second_close",              "MEDIUM", {"alliance_liability": 0.40}),
    "Q28":           ("the_unsolved_problem",           "HIGH",   {"authority_liability": 0.60, "attitude_liability": 0.60}),
    "Q29":           ("the_diversity_ceiling",         "MEDIUM", {"attitude_liability": 0.40, "authority_liability": 0.40}),
    "Q30":           ("the_lost_map",                  "MEDIUM", {"authority_liability": 0.40, "alliance_liability": 0.40}),
    "Q31":           ("the_unsolved_problem",           "HIGH",   {"authority_liability": 0.60, "attitude_liability": 0.60}),
    "Q32":           ("groundhog_day",                 "MEDIUM", {"authority_liability": 0.40, "alliance_liability": 0.40}),
    "Q33":           ("leadership_continuity_risk",    "MEDIUM", {"authority_liability": 0.40, "aptitude_liability": 0.40}),
    "Q34":           ("the_broken_compass",            "MEDIUM", {"attitude_liability": 0.40, "alliance_liability": 0.40}),
    "SEVER-01":      ("the_diversity_ceiling",         "MEDIUM", {"attitude_liability": 0.40, "authority_liability": 0.40}),
    "SEVER-02":      ("built_to_fail",                 "HIGH",   {"authority_liability": 0.60, "aptitude_liability": 0.60}),
    "SEVER-03":      ("decision_paralysis",            "MEDIUM", {"authority_liability": 0.40, "alliance_liability": 0.40}),
    "SEVER-04":      ("the_policy_lag",                "MEDIUM", {"authority_liability": 0.40, "aptitude_liability": 0.40}),
    "SEVER-05":      ("leadership_continuity_risk",    "MEDIUM", {"authority_liability": 0.40, "aptitude_liability": 0.40}),
    "SEVER-06":      ("invisible_burnout",             "MEDIUM", {"attitude_liability": 0.40, "alliance_liability": 0.40}),
    "SEVER-07":      ("leadership_continuity_risk",    "MEDIUM", {"authority_liability": 0.40, "aptitude_liability": 0.40}),
    "SEVER-08":      ("the_fracture",                  "HIGH",   {"authority_liability": 0.60, "alliance_liability": 0.60}),
    "SEVER-09":      ("the_second_close",              "MEDIUM", {"alliance_liability": 0.40}),
    "SEVER-11":      ("the_unsolved_problem",           "HIGH",   {"authority_liability": 0.60, "attitude_liability": 0.60}),
    "SEVER-12":      ("the_diversity_ceiling",         "MEDIUM", {"attitude_liability": 0.40, "authority_liability": 0.40}),
    "SEVER-13":      ("the_broken_compass",            "MEDIUM", {"attitude_liability": 0.40, "alliance_liability": 0.40}),
    # Q03B, Q08, Q18, Q27B, SEVER-10: no entry — remain at 0.25 (cluster-only or no seeded states)
}

# ---------------------------------------------------------------------------
# Old _build_library — exact text to find and replace
# ---------------------------------------------------------------------------
OLD_BUILD = '''\
def _build_library():
    lib = {}
    _base = {
        "aptitude_liability": 0.25, "aptitude_asset": 0.25,
        "authority_liability": 0.25, "authority_asset": 0.25,
        "alliance_liability": 0.25, "alliance_asset": 0.25,
        "attitude_liability": 0.25, "attitude_asset": 0.25,
    }
    for (qid, text, fmt, pos, seg, opts, targets, sev) in _QDATA:
        lib[qid] = QuestionDefinition(
            question_id=qid,
            question_text=text,
            format=fmt,
            sequence_position=pos,
            checkpoint_segment=seg,
            answer_options=[
                AnswerOption(
                    option_id=o[0],
                    option_text=o[1],
                    dimensional_contributions=dict(_base),
                    severity_trigger=o[2],
                    severity_follow_on_id=o[3],
                )
                for o in opts
            ],
            state_targets=list(targets),
            severity_trigger=sev,
        )
    return lib'''

NEW_BUILD = '''\
def _build_library():
    lib = {}
    _uniform = {
        "aptitude_liability":  0.25, "aptitude_asset":  0.25,
        "authority_liability": 0.25, "authority_asset": 0.25,
        "alliance_liability":  0.25, "alliance_asset":  0.25,
        "attitude_liability":  0.25, "attitude_asset":  0.25,
    }
    # Signal Map tier seedings (Session 11 pre-calibration pass).
    # Source: PRV3_Signal_Map (Drive 1LMx13dWDvAMWwxYHG7ikd9moZLndphNZw66hbejfLqI)
    # Rule: highest-weight non-cluster state in state_targets; primary dim(s) seeded.
    # HIGH->0.60, MEDIUM->0.40. LOW/Cluster questions absent (remain at 0.25).
    # Asset fields not seeded — liability-only pass.
    _seed = {
        "Q01":           {"authority_liability": 0.60},
        "Q02":           {"authority_liability": 0.60, "aptitude_liability": 0.60},
        "Q03A":          {"authority_liability": 0.60, "attitude_liability": 0.60},
        "Q03A-D-FOLLOW": {"authority_liability": 0.60, "alliance_liability": 0.60},
        "Q04":           {"authority_liability": 0.60, "attitude_liability": 0.60},
        "Q05":           {"attitude_liability": 0.60},
        "Q06":           {"authority_liability": 0.60, "attitude_liability": 0.60},
        "Q07":           {"authority_liability": 0.60, "alliance_liability": 0.60},
        "Q09":           {"authority_liability": 0.60, "alliance_liability": 0.60},
        "Q10":           {"authority_liability": 0.60, "aptitude_liability": 0.60},
        "Q11":           {"authority_liability": 0.40, "attitude_liability": 0.40},
        "Q12":           {"attitude_liability": 0.60},
        "Q13":           {"authority_liability": 0.40, "alliance_liability": 0.40},
        "Q14":           {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "Q15":           {"attitude_liability": 0.40, "authority_liability": 0.40},
        "Q16":           {"attitude_liability": 0.40, "authority_liability": 0.40},
        "Q17":           {"attitude_liability": 0.40, "alliance_liability": 0.40},
        "Q19":           {"authority_liability": 0.40, "attitude_liability": 0.40},
        "Q20":           {"authority_liability": 0.60, "aptitude_liability": 0.60},
        "Q21":           {"authority_liability": 0.40, "alliance_liability": 0.40},
        "Q22":           {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "Q23":           {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "Q24":           {"attitude_liability": 0.40, "alliance_liability": 0.40},
        "Q25":           {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "Q26":           {"authority_liability": 0.60, "alliance_liability": 0.60},
        "Q27A":          {"alliance_liability": 0.40},
        "Q28":           {"authority_liability": 0.60, "attitude_liability": 0.60},
        "Q29":           {"attitude_liability": 0.40, "authority_liability": 0.40},
        "Q30":           {"authority_liability": 0.40, "alliance_liability": 0.40},
        "Q31":           {"authority_liability": 0.60, "attitude_liability": 0.60},
        "Q32":           {"authority_liability": 0.40, "alliance_liability": 0.40},
        "Q33":           {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "Q34":           {"attitude_liability": 0.40, "alliance_liability": 0.40},
        "SEVER-01":      {"attitude_liability": 0.40, "authority_liability": 0.40},
        "SEVER-02":      {"authority_liability": 0.60, "aptitude_liability": 0.60},
        "SEVER-03":      {"authority_liability": 0.40, "alliance_liability": 0.40},
        "SEVER-04":      {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "SEVER-05":      {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "SEVER-06":      {"attitude_liability": 0.40, "alliance_liability": 0.40},
        "SEVER-07":      {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "SEVER-08":      {"authority_liability": 0.60, "alliance_liability": 0.60},
        "SEVER-09":      {"alliance_liability": 0.40},
        "SEVER-11":      {"authority_liability": 0.60, "attitude_liability": 0.60},
        "SEVER-12":      {"attitude_liability": 0.40, "authority_liability": 0.40},
        "SEVER-13":      {"attitude_liability": 0.40, "alliance_liability": 0.40},
    }
    for (qid, text, fmt, pos, seg, opts, targets, sev) in _QDATA:
        base = dict(_uniform)
        base.update(_seed.get(qid, {}))
        lib[qid] = QuestionDefinition(
            question_id=qid,
            question_text=text,
            format=fmt,
            sequence_position=pos,
            checkpoint_segment=seg,
            answer_options=[
                AnswerOption(
                    option_id=o[0],
                    option_text=o[1],
                    dimensional_contributions=dict(base),
                    severity_trigger=o[2],
                    severity_follow_on_id=o[3],
                )
                for o in opts
            ],
            state_targets=list(targets),
            severity_trigger=sev,
        )
    return lib'''

# Module-level docstring line replacements
OLD_DOC_LINE1 = "All dimensional_contributions: 0.25 baseline across all 8 fields."
NEW_DOC_LINE1 = "dimensional_contributions: seeded from Signal Map tier assignments (Session 11)."

OLD_DOC_LINE2 = "Calibration target - weights differentiated after Phase 1 calibration."
NEW_DOC_LINE2 = "HIGH->0.60, MEDIUM->0.40, LOW/Cluster->0.25 baseline. Asset fields at 0.25."

OLD_DOC_LINE3 = "Do not set speculative weights."
NEW_DOC_LINE3 = "Phase 1 calibration will refine these values against test suite results."

# AnswerOption docstring replacements
OLD_OPT_DOC1 = "    dimensional_contributions: all 8 fields initialized at 0.25 (baseline)."
NEW_OPT_DOC1 = "    dimensional_contributions: seeded per Signal Map tier (Session 11)."

OLD_OPT_DOC2 = "    Calibration target - do not set speculative weights."
NEW_OPT_DOC2 = "    HIGH->0.60, MEDIUM->0.40, LOW/Cluster->0.25. Asset fields at 0.25."


def _dim_summary(dims: dict) -> str:
    parts = []
    for dim, val in sorted(dims.items()):
        parts.append(f"{dim}={val}")
    return ", ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed dimensional_contributions in engine/data/questions.py"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print proposed changes without writing")
    parser.add_argument("--write", action="store_true",
                        help="Apply changes to questions.py")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.print_help()
        sys.exit(1)

    if not TARGET.exists():
        print(f"ERROR: target not found: {TARGET}")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8")

    # Verify OLD_BUILD is present
    if OLD_BUILD not in text:
        print("ERROR: OLD_BUILD not found in target — file may already be patched or has diverged.")
        sys.exit(1)

    if args.dry_run:
        print(f"DRY RUN — target: {TARGET}")
        print(f"  50 questions total; {len(_SEEDINGS_META)} will be seeded; "
              f"{50 - len(_SEEDINGS_META)} unchanged (cluster/low/empty)")
        print()
        print(f"  {'QID':<16} {'tier':<8} {'source_state':<34} {'seedings'}")
        print(f"  {'-'*16} {'-'*8} {'-'*34} {'-'*40}")
        high_count = medium_count = 0
        for qid, (state, tier, dims) in _SEEDINGS_META.items():
            print(f"  {qid:<16} {tier:<8} {state:<34} {_dim_summary(dims)}")
            if tier == "HIGH":
                high_count += 1
            else:
                medium_count += 1
        print()
        print(f"  HIGH (0.60): {high_count} questions")
        print(f"  MEDIUM (0.40): {medium_count} questions")
        unchanged = [
            "Q03B", "Q08", "Q18", "Q27B", "SEVER-10",
        ]
        print(f"  Unchanged (0.25): {len(unchanged)} questions — {', '.join(unchanged)}")
        print()
        print("  Docstring updates:")
        print(f"    '{OLD_DOC_LINE1}'")
        print(f"    -> '{NEW_DOC_LINE1}'")
        print(f"    '{OLD_DOC_LINE2}'")
        print(f"    -> '{NEW_DOC_LINE2}'")
        print(f"    '{OLD_DOC_LINE3}'")
        print(f"    -> '{NEW_DOC_LINE3}'")
        return

    # Apply all replacements
    new_text = text
    new_text = new_text.replace(OLD_BUILD, NEW_BUILD, 1)
    new_text = new_text.replace(OLD_DOC_LINE1, NEW_DOC_LINE1, 1)
    new_text = new_text.replace(OLD_DOC_LINE2, NEW_DOC_LINE2, 1)
    new_text = new_text.replace(OLD_DOC_LINE3, NEW_DOC_LINE3, 1)
    new_text = new_text.replace(OLD_OPT_DOC1, NEW_OPT_DOC1, 1)
    new_text = new_text.replace(OLD_OPT_DOC2, NEW_OPT_DOC2, 1)

    if new_text == text:
        print("ERROR: no changes produced — check that OLD_BUILD matches exactly.")
        sys.exit(1)

    TARGET.write_text(new_text, encoding="utf-8")
    print(f"WRITTEN: {TARGET}")
    print(f"  {len(_SEEDINGS_META)} questions seeded")
    print(f"  5 questions unchanged (Q03B, Q08, Q18, Q27B, SEVER-10)")
    print(f"  Docstring lines updated: 5")


if __name__ == "__main__":
    main()
