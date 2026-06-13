"""
PRV3 Scoring Engine — Output Layer
Resolution Families

Maps each of the 47 organizational states to one of four resolution
families. The family description characterizes the nature of resolution
required — not the specific service that delivers it.

CONSTRAINT (locked S34): No service names appear in this file or in
any output derived from it. The family description is the only
user-facing text associated with resolution routing.

All family description copy is flagged COPY PENDING.

Spec reference: PRV3 Output Layer Brief — Step 3
"""

from __future__ import annotations


# ── Resolution family definitions ──────────────────────────────────────────────
# Four families. Descriptions are COPY PENDING — placeholders below.
# family_id is an internal routing key, not user-facing.

RESOLUTION_FAMILY_DESCRIPTIONS: dict[str, dict] = {
    "structural": {
        "family_id":   "structural",
        "description": "COPY PENDING",  # COPY PENDING — structural design resolution copy
    },
    "developmental": {
        "family_id":   "developmental",
        "description": "COPY PENDING",  # COPY PENDING — capability development resolution copy
    },
    "investigative": {
        "family_id":   "investigative",
        "description": "COPY PENDING",  # COPY PENDING — investigative / compliance resolution copy
    },
    "directional": {
        "family_id":   "directional",
        "description": "COPY PENDING",  # COPY PENDING — strategic direction / culture resolution copy
    },
}


# ── State → resolution family mapping ─────────────────────────────────────────
# All 47 states. One family per state.
# Assignment reflects the primary resolution modality, not the only one.

STATE_RESOLUTION_FAMILY: dict[str, str] = {
    # ── Developmental — capability, talent, performance architecture ───────────
    "the_unformed_leader":              "developmental",
    "the_overloaded_manager":           "developmental",
    "the_dormant_talent":               "developmental",
    "built_to_fail":                    "developmental",
    "the_uninitiated":                  "developmental",
    "groundhog_day":                    "developmental",

    # ── Structural — organizational design, authority, governance ──────────────
    "the_undefined_role":               "structural",
    "the_paper_tiger":                  "structural",
    "the_founders_grip":                "structural",
    "leadership_continuity_risk":       "structural",
    "decision_paralysis":               "structural",
    "the_policy_lag":                   "structural",
    "dueling_narratives":               "structural",
    "the_unsolved_problem":             "structural",
    "transition_paralysis":             "structural",
    "the_lost_map":                     "structural",
    "invisible_influence_architecture": "structural",
    "the_fracture":                     "structural",
    "silosolation":                     "structural",
    "the_broken_compass":               "structural",

    # ── Investigative — compliance, legal exposure, protected concerns ─────────
    "the_exposed":                      "investigative",
    "hr_capture":                       "investigative",
    "the_unexamined_algorithm":         "investigative",
    "heard_and_ignored":                "investigative",
    "the_tolerated_violation":          "investigative",
    "paper_shield":                     "investigative",
    "pay_exposure":                     "investigative",
    "the_pay_fog":                      "investigative",
    "the_second_close":                 "investigative",
    "the_suppression_filter":           "investigative",
    "the_arbitrary_standard":           "investigative",
    "decision_blindness":               "investigative",
    "the_untouchable":                  "investigative",
    "what_nobody_says":                 "investigative",
    "the_diversity_ceiling":            "investigative",
    "the_unreported_hazard":            "investigative",
    "the_unlocked_door":                "investigative",

    # ── Directional — culture, identity, strategic and behavioral realignment ──
    "culture_drift":                    "directional",
    "identity_erosion":                 "directional",
    "the_culture_that_wasnt":           "directional",
    "the_burned_credibility":           "directional",
    "invisible_burnout":                "directional",
    "the_basement_standard":            "directional",
    "the_inside_track":                 "directional",
    "narrative_lock":                   "directional",
    "the_wrong_reward":                 "directional",
    "leadership_deafness":              "directional",
}

# Verify count at import — must be 47
assert len(STATE_RESOLUTION_FAMILY) == 47, (
    f"STATE_RESOLUTION_FAMILY has {len(STATE_RESOLUTION_FAMILY)} entries, expected 47"
)


# ── Lookup helpers ─────────────────────────────────────────────────────────────

def get_family(state_id: str) -> dict:
    """
    Return the resolution family dict for a state_id.
    Falls back to structural if state_id is not in the registry.
    """
    family_id = STATE_RESOLUTION_FAMILY.get(state_id, "structural")
    return RESOLUTION_FAMILY_DESCRIPTIONS[family_id]


def get_primary_family(state_ids: list[str]) -> dict:
    """
    Return the resolution family for the primary (first) identified state.
    Used when a single family must be surfaced to the principal.
    """
    if not state_ids:
        return RESOLUTION_FAMILY_DESCRIPTIONS["structural"]
    return get_family(state_ids[0])


def get_all_families(state_ids: list[str]) -> list[dict]:
    """
    Return a deduplicated list of resolution family dicts for a state cluster,
    preserving order of first occurrence.
    """
    seen: set[str] = set()
    result = []
    for sid in state_ids:
        fam = get_family(sid)
        fid = fam["family_id"]
        if fid not in seen:
            seen.add(fid)
            result.append(fam)
    return result
