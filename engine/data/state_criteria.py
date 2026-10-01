"""
Per-state criterion scores (0, 1 or 2) for the four friction/legal criteria.

Scores only. Each value was copied from the former
engine.friction_tax.STATE_MULTIPLIERS[state].criteria[criterion].score on
2026-09-30 by tools/patch_stage1_state_criteria.py (friction tax rebuild,
Stage 1, prompts/friction-tax-rebuild-build-spec.md Section 4 and Section 10
step 2). STATE_MULTIPLIERS, with its per-score rationale text, was removed in
Stage 4. The rationale text is in git history before that commit, and
tools/test_state_criteria.py pins these scores with a frozen fingerprint.

Uses:
  turnover, productivity, decision_quality
      A score above 0 switches the matching friction channel on for a state
      (turnover -> Turnover channel, productivity -> Engagement channel,
      decision_quality -> decision-time receipt). Read by
      engine/contract.py's receipts and ledger and by the two-channel function in
      Stage 4.
  legal
      Read by Legal/Compliance (engine/friction_tax.py). Legal must not depend
      on a friction module's internals, which is why this lives here. A score of
      0 means not applicable, 1 or 2 selects the Legal pricing domain.

Keys are the state ids in engine/data/states.py (58 states).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StateCriteria:
    turnover: int
    productivity: int
    decision_quality: int
    legal: int


STATE_CRITERIA: dict[str, StateCriteria] = {
    "built_to_fail": StateCriteria(turnover=2, productivity=1, decision_quality=1, legal=1),
    "invisible_performance_management": StateCriteria(turnover=1, productivity=2, decision_quality=0, legal=2),
    "the_dormant_talent": StateCriteria(turnover=2, productivity=2, decision_quality=1, legal=0),
    "the_overloaded_manager": StateCriteria(turnover=2, productivity=1, decision_quality=1, legal=0),
    "the_paper_tiger": StateCriteria(turnover=1, productivity=0, decision_quality=0, legal=2),
    "the_undefined_role": StateCriteria(turnover=2, productivity=2, decision_quality=1, legal=1),
    "the_unformed_leader": StateCriteria(turnover=2, productivity=2, decision_quality=1, legal=0),
    "compression_crisis": StateCriteria(turnover=1, productivity=1, decision_quality=2, legal=1),
    "decision_paralysis": StateCriteria(turnover=1, productivity=2, decision_quality=2, legal=0),
    "disparate_impact_architecture": StateCriteria(turnover=1, productivity=1, decision_quality=1, legal=2),
    "dueling_narratives": StateCriteria(turnover=1, productivity=1, decision_quality=2, legal=1),
    "hr_capture": StateCriteria(turnover=2, productivity=0, decision_quality=1, legal=2),
    "heard_and_ignored": StateCriteria(turnover=2, productivity=0, decision_quality=1, legal=2),
    "invisible_influence_architecture": StateCriteria(turnover=1, productivity=1, decision_quality=2, legal=0),
    "leadership_continuity_risk": StateCriteria(turnover=1, productivity=1, decision_quality=2, legal=0),
    "paper_shield": StateCriteria(turnover=0, productivity=0, decision_quality=2, legal=0),
    "pay_exposure": StateCriteria(turnover=2, productivity=1, decision_quality=0, legal=1),
    "planning_authority_gap": StateCriteria(turnover=1, productivity=2, decision_quality=2, legal=0),
    "sequential_decision_blindness": StateCriteria(turnover=1, productivity=1, decision_quality=1, legal=2),
    "the_exposed": StateCriteria(turnover=1, productivity=0, decision_quality=1, legal=2),
    "the_founders_grip": StateCriteria(turnover=2, productivity=2, decision_quality=2, legal=0),
    "the_lost_map": StateCriteria(turnover=0, productivity=2, decision_quality=2, legal=0),
    "the_pay_fog": StateCriteria(turnover=2, productivity=1, decision_quality=0, legal=2),
    "the_policy_lag": StateCriteria(turnover=1, productivity=0, decision_quality=2, legal=2),
    "the_tolerated_violation": StateCriteria(turnover=2, productivity=0, decision_quality=0, legal=2),
    "the_unexamined_algorithm": StateCriteria(turnover=0, productivity=2, decision_quality=2, legal=1),
    "the_uninitiated": StateCriteria(turnover=0, productivity=2, decision_quality=2, legal=0),
    "the_unsolved_problem": StateCriteria(turnover=1, productivity=1, decision_quality=1, legal=1),
    "transition_paralysis": StateCriteria(turnover=2, productivity=2, decision_quality=1, legal=0),
    "decision_blindness": StateCriteria(turnover=2, productivity=1, decision_quality=2, legal=0),
    "distributed_culture_fragmentation": StateCriteria(turnover=0, productivity=2, decision_quality=2, legal=1),
    "silosolation": StateCriteria(turnover=1, productivity=2, decision_quality=2, legal=0),
    "the_arbitrary_standard": StateCriteria(turnover=2, productivity=1, decision_quality=1, legal=2),
    "the_fracture": StateCriteria(turnover=2, productivity=1, decision_quality=1, legal=0),
    "the_second_close": StateCriteria(turnover=1, productivity=2, decision_quality=1, legal=0),
    "the_suppression_filter": StateCriteria(turnover=2, productivity=2, decision_quality=2, legal=1),
    "cultural_overtime": StateCriteria(turnover=2, productivity=0, decision_quality=0, legal=2),
    "culture_drift": StateCriteria(turnover=2, productivity=2, decision_quality=2, legal=0),
    "groundhog_day": StateCriteria(turnover=2, productivity=1, decision_quality=1, legal=1),
    "human_displacement_anxiety": StateCriteria(turnover=2, productivity=0, decision_quality=2, legal=0),
    "identity_erosion": StateCriteria(turnover=2, productivity=0, decision_quality=1, legal=0),
    "invisible_burnout": StateCriteria(turnover=2, productivity=0, decision_quality=1, legal=1),
    "leadership_deafness": StateCriteria(turnover=2, productivity=1, decision_quality=2, legal=0),
    "motivational_architecture_failure": StateCriteria(turnover=2, productivity=2, decision_quality=1, legal=0),
    "narrative_lock": StateCriteria(turnover=2, productivity=1, decision_quality=2, legal=0),
    "the_basement_standard": StateCriteria(turnover=1, productivity=2, decision_quality=2, legal=1),
    "the_broken_compass": StateCriteria(turnover=2, productivity=1, decision_quality=2, legal=0),
    "the_burned_credibility": StateCriteria(turnover=2, productivity=2, decision_quality=0, legal=0),
    "the_culture_that_wasnt": StateCriteria(turnover=2, productivity=1, decision_quality=1, legal=0),
    "the_diversity_ceiling": StateCriteria(turnover=1, productivity=0, decision_quality=0, legal=1),
    "the_inside_track": StateCriteria(turnover=2, productivity=1, decision_quality=0, legal=1),
    "the_unlocked_door": StateCriteria(turnover=1, productivity=1, decision_quality=1, legal=1),
    "the_unreported_hazard": StateCriteria(turnover=1, productivity=0, decision_quality=2, legal=2),
    "the_untouchable": StateCriteria(turnover=1, productivity=1, decision_quality=1, legal=1),
    "the_wrong_reward": StateCriteria(turnover=1, productivity=2, decision_quality=1, legal=1),
    "wellbeing_theater": StateCriteria(turnover=1, productivity=1, decision_quality=1, legal=0),
    "what_nobody_says": StateCriteria(turnover=2, productivity=1, decision_quality=1, legal=0),
    "the_inner_circle": StateCriteria(turnover=1, productivity=0, decision_quality=2, legal=1),
}

for _sid, _c in STATE_CRITERIA.items():
    for _name in ("turnover", "productivity", "decision_quality", "legal"):
        _v = getattr(_c, _name)
        assert isinstance(_v, int) and not isinstance(_v, bool) and 0 <= _v <= 2, (
            f"{_sid}.{_name}: score {_v!r} is not an int in [0, 2]"
        )
del _sid, _c, _name, _v
