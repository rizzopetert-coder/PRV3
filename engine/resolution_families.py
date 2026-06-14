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


# ── Engine → commercial name mapping ──────────────────────────────────────────
# Maps resolution_family engine names (as they appear in engine/data/states.py)
# to commercial service names used in client-facing output.
# Locked Session 42. Supersedes Session 32 lock (Formation, Practicum, Counsel, Navigation).

ENGINE_TO_COMMERCIAL_NAME: dict[str, str] = {
    "Roadmap":           "Groundwork",
    "Development":       "Development",
    "Intervention":      "First Call",
    "Executive Counsel": "Advisory",
}


def translate_resolution_family(engine_family_str: str) -> str:
    """
    Translate an engine resolution_family string to its commercial equivalent.
    Handles single names ("Roadmap") and compounds ("Roadmap + Intervention").
    Unknown parts pass through unchanged.
    """
    parts = [p.strip() for p in engine_family_str.split(" + ")]
    translated = [ENGINE_TO_COMMERCIAL_NAME.get(p, p) for p in parts]
    return " + ".join(translated)


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


# ── Static fallback copy ───────────────────────────────────────────────────────
# Used when output_synthesis.py LLM call times out or fails.
# Keyed by (commercial_name, severity_tier). Compound keys use severity_tier=None.
# Source: PRV3_Resolution_Families_Copy_v3.0.docx — Session 42.

RESOLUTION_FALLBACK_COPY: dict[tuple[str, str | None], str] = {

    # Groundwork — engine: Roadmap
    ("Groundwork", "Emerging"): (
        "A structural problem requires structural work. Groundwork brings in the right expertise, "
        "targeted at what the diagnostic found, before it has time to settle in deeper."
    ),
    ("Groundwork", "Entrenched"): (
        "The conditions producing this live in how your organization is designed, not in the people "
        "navigating it. Groundwork addresses that level directly — expert, targeted, and aimed "
        "at the architecture rather than the symptoms."
    ),
    ("Groundwork", "Endemic"): (
        "When a condition becomes the environment, adjusting what happens inside it is not enough. "
        "Groundwork is the structural redesign — expert work at the level where the problem actually lives."
    ),

    # Development — engine: Development
    ("Development", "Emerging"): (
        "There is a capability gap. Development addresses it directly — not off-the-shelf training, "
        "but targeted work on the specific skills and practices the diagnostic identified."
    ),
    ("Development", "Entrenched"): (
        "The gap has had time to become normal. Development works against that — targeted, practical, "
        "and built around what your people actually need to be able to do, not a general program applied "
        "to a specific problem."
    ),
    ("Development", "Endemic"): (
        "At this depth the gap is the operating norm. Development at this severity is not about adding a "
        "skill. It is about rebuilding the practices that determine whether any skill takes root."
    ),

    # First Call — engine: Intervention
    ("First Call", "Emerging"): (
        "The situation requires someone in it, not advising from outside it. First Call is that presence "
        "— engaged with what is happening while there is still room to shape it."
    ),
    ("First Call", "Entrenched"): (
        "What is live right now requires more than a plan. First Call means someone in the room, "
        "with the expertise and authority to move the situation, until it resolves."
    ),
    ("First Call", "Endemic"): (
        "This does not respond to a plan or a program. First Call is direct, immersive engagement "
        "— inside the situation, not above it, for as long as it takes."
    ),

    # Advisory — engine: Executive Counsel
    ("Advisory", "Emerging"): (
        "Yes, it is what it sounds like. A confidential relationship with someone who has no stake "
        "in the outcome except getting it right — available before you need it urgently."
    ),
    ("Advisory", "Entrenched"): (
        "The honest read on your situation is not available inside the building. Advisory is that read "
        "— confidential, direct, and without the organizational politics attached to every word."
    ),
    ("Advisory", "Endemic"): (
        "When you are close enough to something long enough, you lose the ability to see it clearly. "
        "Advisory is the ongoing relationship that makes clarity possible — for the decisions that "
        "matter most and cannot be discussed with anyone inside the organization."
    ),

    # Compound copy — tier-agnostic
    ("Groundwork + First Call", None): (
        "The structure needs redesigning and the situation it created is live right now. "
        "Groundwork addresses the architecture. First Call addresses the present."
    ),
    ("First Call + Groundwork", None): (
        "First Call handles what is active. Groundwork follows — so what produced it does not reassemble."
    ),
    ("Advisory + First Call", None): (
        "Advisory provides the honest read on what the situation requires. First Call executes it."
    ),
    ("First Call + Advisory", None): (
        "First Call is present in the work. Advisory is the confidential relationship running alongside it "
        "for the decisions the work produces."
    ),
    ("Development + Groundwork", None): (
        "Development addresses the capability gap. Groundwork addresses the structural conditions "
        "that keep recreating it."
    ),
    ("Groundwork + Development", None): (
        "Groundwork redesigns the environment. Development follows — because capability built "
        "inside a broken structure does not hold."
    ),
    ("Development + First Call", None): (
        "First Call addresses what is live. Development addresses what the organization needs to be "
        "able to do once it is through."
    ),
}

_FALLBACK_GENERIC: str = (
    "The diagnostic found a pattern that warrants structured resolution. "
    "The resolution path is well-defined and addressable."
)


def get_fallback_copy(commercial_name: str, severity_tier: str | None = None) -> str:
    """
    Return static fallback copy for a commercial service name and severity tier.
    Used when output_synthesis.py LLM call fails or times out.

    Single-service names: pass severity_tier ("Emerging", "Entrenched", "Endemic").
    Compound names (contain ' + '): severity_tier is ignored, copy is tier-agnostic.
    Returns generic fallback if the key is not found.
    """
    if " + " in commercial_name:
        return RESOLUTION_FALLBACK_COPY.get((commercial_name, None), _FALLBACK_GENERIC)
    return RESOLUTION_FALLBACK_COPY.get((commercial_name, severity_tier), _FALLBACK_GENERIC)


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
