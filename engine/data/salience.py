"""
PRV3 Scoring Engine — Section II.4 Supplemental
Per-State Salience Weight Profiles

SALIENCE_PROFILES: dict mapping state_id -> {field: weight}

Seeding rule (Gemini-specified, Session 21):
  Target fields (primary dimension + secondary dimension, both axes): 2.5
  Off-axis fields (all other dimensions, both axes): 0.4

Used by rank_states() when salience_weights is passed explicitly.
Import: from engine.data.salience import SALIENCE_PROFILES
"""

SALIENCE_PROFILES = {

    # ── APTITUDE — HIGH tier (primary only) ───────────────────────────────────
    "built_to_fail": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_paper_tiger": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── APTITUDE — MEDIUM tier (primary only) ─────────────────────────────────
    "the_undefined_role": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── APTITUDE — LOW/CLUSTER (primary=Aptitude, secondary=Attitude) ─────────
    "the_unformed_leader": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_dormant_talent": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },

    # ── APTITUDE — LOW/CLUSTER (primary=Aptitude, secondary=Authority) ────────
    "the_overloaded_manager": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── AUTHORITY — HIGH tier (primary only) ──────────────────────────────────
    "the_founders_grip": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_exposed": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "hr_capture": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "heard_and_ignored": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_tolerated_violation": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_unsolved_problem": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── AUTHORITY — MEDIUM tier (primary only) ────────────────────────────────
    "the_uninitiated": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "leadership_continuity_risk": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "decision_paralysis": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_policy_lag": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "dueling_narratives": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "transition_paralysis": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_lost_map": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "pay_exposure": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_pay_fog": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── AUTHORITY — LOW/CLUSTER (primary=Authority, secondary=Aptitude) ───────
    "the_unexamined_algorithm": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── AUTHORITY — LOW/CLUSTER (primary=Authority, secondary=Alliance) ───────
    "paper_shield": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "invisible_influence_architecture": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── ALLIANCE — HIGH tier (primary only) ───────────────────────────────────
    "the_fracture": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "decision_blindness": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── ALLIANCE — MEDIUM tier (primary only) ─────────────────────────────────
    "the_second_close": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "silosolation": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_arbitrary_standard": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── ALLIANCE — LOW/CLUSTER (primary=Alliance, secondary=Authority) ────────
    "the_suppression_filter": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── ATTITUDE — HIGH tier (primary only) ───────────────────────────────────
    "the_untouchable": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },

    # ── ATTITUDE — MEDIUM tier (primary only) ─────────────────────────────────
    "the_diversity_ceiling": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_burned_credibility": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "invisible_burnout": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_basement_standard": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_inside_track": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "groundhog_day": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_wrong_reward": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_broken_compass": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },

    # ── ATTITUDE — LOW/CLUSTER (primary=Attitude, secondary=Alliance) ─────────
    "narrative_lock": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "what_nobody_says": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "leadership_deafness": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "identity_erosion": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_culture_that_wasnt": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_unreported_hazard": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_unlocked_door": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },

    # ── ATTITUDE — LOW/CLUSTER (primary=Attitude, secondary=Authority) ────────
    "culture_drift": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
}
