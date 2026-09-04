"""
PRV3 Scoring Engine — Output Layer
Resolution Families

Maps each of the 47 organizational states to one of four resolution
families. The family description characterizes the nature of resolution
required — not the specific service that delivers it.

CONSTRAINT (locked S34): No service names appear in this file or in
any output derived from it. The family description is the only
user-facing text associated with resolution routing.

All four family description values are final, Pete-supplied copy (shipped
commit 95fc404, 2026-07-31).

Spec reference: PRV3 Output Layer Brief — Step 3
"""

from __future__ import annotations

from typing import Optional


# ── Resolution family definitions ──────────────────────────────────────────────
# Four families. Descriptions are final, shipped copy (commit 95fc404).
# family_id is an internal routing key, not user-facing.

RESOLUTION_FAMILY_DESCRIPTIONS: dict[str, dict] = {
    "structural": {
        "family_id":   "structural",
        "description": "Something in how decisions get made, who holds authority, or how the organization is built is producing this condition. Not a person carrying it. The structure itself. It will keep producing the same outcome until that structure changes. Fixing it means no longer managing around it.",  # structural design resolution copy
    },
    "developmental": {
        "family_id":   "developmental",
        "description": "Somebody in this organization needs to be able to do something they can't do yet, and no amount of good intention closes that gap on its own. This is capability work. It's specific, it's learnable, and it requires deliberate practice aimed at exactly what the diagnostic found, not a general program hoping to cover it.",  # capability development resolution copy
    },
    "investigative": {
        "family_id":   "investigative",
        "description": "Something here needs a direct, unbiased look from someone with no stake in what they find. Not coaching. Not a communication fix. A fact-finding problem, and the resolution starts with an honest, unflinching read on what's actually happening before anyone decides what to do about it.",  # investigative / compliance resolution copy
    },
    "directional": {
        "family_id":   "directional",
        "description": "The organization is drifting, and drift doesn't correct itself. This is about realigning what the organization says it values with what it actually rewards and tolerates day to day. Resolution here means naming the gap plainly and doing the harder work of closing it, not writing a new mission statement.",  # strategic direction / culture resolution copy
    },
}


# ── Engine → commercial name mapping ──────────────────────────────────────────
# Maps resolution_family engine names (as they appear in engine/data/states.py)
# to commercial service names used in client-facing output.
# Locked Session 42. Supersedes Session 32 lock (Formation, Practicum, Counsel, Navigation).

ENGINE_TO_COMMERCIAL_NAME: dict[str, str] = {
    "Roadmap":           "People Tactics and Strategy",
    "Development":       "Training & Development",
    "Intervention":      "Intervention",
    "Executive Counsel": "Executive Advisory",
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


# ── causation_pattern routing override ─────────────────────────────────────────
# Priority Queue item 2, Diagnostic Dimension Expansion follow-on. Per-state
# authored overrides letting a session's causation_pattern (single_point vs.
# diffuse) route to a different resolution_family than the state's static
# default. Keyed sparsely by state_id -- most states carry no override.
# Naturally inert for states whose default resolution_family is compound
# (contains " + "), by design -- no separate allowlist needed, see
# apply_causation_override()'s own guard.
#
# Values MUST be raw base engine family names -- "Roadmap" | "Development" |
# "Intervention" | "Executive Counsel" -- matching ENGINE_TO_COMMERCIAL_NAME's
# keys above, never already-translated commercial names. This dict operates
# in the same untranslated namespace as StateProfile.resolution_family itself
# (confirmed: private_output["resolution_routing"] is never translated before
# reaching the output contract -- translate_resolution_family() is called
# exactly once in the live pipeline, engine/main.py, for a separate
# LLM-synthesis-input purpose, not for this field).
#
# First entries authored 2026-09-03, Pete's own clinical judgment. Groups
# closed this session, by their real shipped resolution_family default (not
# a task-header label -- see the 2026-09-03 Section 16 entries in
# tools/_mob.txt for the "Executive Counsel group" naming correction):
# leadership_deafness/the_broken_compass ("Executive Counsel"),
# the_unformed_leader/silosolation ("Development"), and 8 of 9
# "Intervention"-default states (the_uninitiated, what_nobody_says,
# the_diversity_ceiling, identity_erosion, the_culture_that_wasnt,
# the_burned_credibility, the_unreported_hazard, wellbeing_theater).
# paper_shield ("Roadmap" default) was a standalone worked example, not a
# group member. All defaults confirmed single-family (non-compound) directly
# against engine/data/states.py before authoring.
#
# Most entries carry only a "diffuse" key -- their single_point
# causation_pattern is meant to fall through to the existing default via
# apply_causation_override()'s own dict.get() fallback, sparse by design,
# not an oversight. silosolation is the one exception carrying both keys,
# deliberately routing neither pattern to its own shipped "Development"
# default -- its descriptive_prose ("the isolation isn't hostile. It's
# structural") sits in tension with that default, addressed here at the
# override level rather than by changing the default itself, out of scope
# for this pass. See tools/_mob.txt for that standalone open item.
#
# culture_drift is the 9th "Intervention"-default state in this reviewed
# group and is DELIBERATELY EXCLUDED -- do not add an entry for it. Two
# reasons: (1) its descriptive_prose ("drifted apart gradually enough that
# no single moment marks the change... nobody decided") is definitionally
# diffuse-only, no coherent single_point reading exists; (2) it is this test
# suite's synthetic grounding fixture for the no-override-entry fallback
# path (tools/test_resolution_families.py's _SINGLE_DEFAULT tests) -- those
# assertions depend on it having no real entry here.
STATE_CAUSATION_OVERRIDES: dict[str, dict[str, str]] = {
    "paper_shield": {"single_point": "Intervention", "diffuse": "Roadmap"},
    "leadership_deafness": {"diffuse": "Roadmap"},
    "the_broken_compass": {"diffuse": "Intervention"},
    "the_unformed_leader": {"diffuse": "Roadmap"},
    "silosolation": {"single_point": "Intervention", "diffuse": "Roadmap"},
    "the_uninitiated": {"diffuse": "Development"},
    "what_nobody_says": {"diffuse": "Roadmap"},
    "the_diversity_ceiling": {"diffuse": "Roadmap"},
    "identity_erosion": {"diffuse": "Roadmap"},
    "the_culture_that_wasnt": {"diffuse": "Roadmap"},
    "the_burned_credibility": {"diffuse": "Roadmap"},
    "the_unreported_hazard": {"diffuse": "Roadmap"},
    "wellbeing_theater": {"diffuse": "Roadmap"},
}


def apply_causation_override(
    state_id: Optional[str],
    default_family: str,
    causation_pattern: Optional[str],
) -> str:
    """
    Apply a causation_pattern override to a state's raw resolution_family
    string. Operates entirely in the untranslated (raw engine name) space --
    output must remain a valid input to translate_resolution_family(), never
    pre-translated at this site.

    Guarantees, in check order:
      - default_family == "" (priv was None -- multi-mode or
        insufficient_signal routing, confirmed via direct trace neither mode
        ever builds a private block) -> returns "" unchanged. The override
        mechanism never turns on a field that is structurally silent for an
        entire routing mode today.
      - default_family contains " + " (a compound default) -> returned
        unchanged. Compound states are immune by construction, not by an
        explicit allowlist -- STATE_CAUSATION_OVERRIDES entries only ever
        apply to single-family defaults.
      - state_id is None, or causation_pattern is None/"insufficient_signal"
        -> returns default_family unchanged. insufficient_signal means the
        causation-pattern read itself isn't trustworthy (too few qualified
        states); nothing for an override to respond to.
      - state_id has no entry in STATE_CAUSATION_OVERRIDES, or the entry has
        no key for this specific causation_pattern value -> falls through to
        default_family via dict.get()'s own fallback, same effect as no
        override existing.
    """
    if not default_family or " + " in default_family:
        return default_family

    if not state_id or not causation_pattern or causation_pattern == "insufficient_signal":
        return default_family

    state_overrides = STATE_CAUSATION_OVERRIDES.get(state_id, {})
    return state_overrides.get(causation_pattern, default_family)


# ── Static fallback copy ───────────────────────────────────────────────────────
# Used when output_synthesis.py LLM call times out or fails.
# Keyed by (commercial_name, severity_tier). Compound keys use severity_tier=None.
# Source: documents/PRV3_Resolution_Families_Copy_v3.0.docx — Session 42.

RESOLUTION_FALLBACK_COPY: dict[tuple[str, str | None], str] = {

    # People Tactics and Strategy — engine: Roadmap
    ("People Tactics and Strategy", "Emerging"): (
        "A structural problem requires structural work. People Tactics and Strategy brings in the right expertise, "
        "targeted at what the diagnostic found, before it has time to settle in deeper."
    ),
    ("People Tactics and Strategy", "Entrenched"): (
        "The conditions producing this live in how your organization is designed, not in the people "
        "navigating it. People Tactics and Strategy addresses that level directly — expert, targeted, and aimed "
        "at the architecture rather than the symptoms."
    ),
    ("People Tactics and Strategy", "Endemic"): (
        "When a condition becomes the environment, adjusting what happens inside it is not enough. "
        "People Tactics and Strategy is the structural redesign — expert work at the level where the problem actually lives."
    ),

    # Training & Development — engine: Development
    ("Training & Development", "Emerging"): (
        "There is a capability gap. Training & Development addresses it directly — not off-the-shelf training, "
        "but targeted work on the specific skills and practices the diagnostic identified."
    ),
    ("Training & Development", "Entrenched"): (
        "The gap has had time to become normal. Training & Development works against that — targeted, practical, "
        "and built around what your people actually need to be able to do, not a general program applied "
        "to a specific problem."
    ),
    ("Training & Development", "Endemic"): (
        "At this depth the gap is the operating norm. Training & Development at this severity is not about adding a "
        "skill. It is about rebuilding the practices that determine whether any skill takes root."
    ),

    # Intervention — engine: Intervention
    ("Intervention", "Emerging"): (
        "The situation requires someone in it, not advising from outside it. Intervention is that presence "
        "— engaged with what is happening while there is still room to shape it."
    ),
    ("Intervention", "Entrenched"): (
        "What is live right now requires more than a plan. Intervention means someone in the room, "
        "with the expertise and authority to move the situation, until it resolves."
    ),
    ("Intervention", "Endemic"): (
        "This does not respond to a plan or a program. Intervention is direct, immersive engagement "
        "— inside the situation, not above it, for as long as it takes."
    ),

    # Executive Advisory — engine: Executive Counsel
    ("Executive Advisory", "Emerging"): (
        "Yes, it is what it sounds like. A confidential relationship with someone who has no stake "
        "in the outcome except getting it right — available before you need it urgently."
    ),
    ("Executive Advisory", "Entrenched"): (
        "The honest read on your situation is not available inside the building. Executive Advisory is that read "
        "— confidential, direct, and without the organizational politics attached to every word."
    ),
    ("Executive Advisory", "Endemic"): (
        "When you are close enough to something long enough, you lose the ability to see it clearly. "
        "Executive Advisory is the ongoing relationship that makes clarity possible — for the decisions that "
        "matter most and cannot be discussed with anyone inside the organization."
    ),

    # Compound copy — tier-agnostic
    ("People Tactics and Strategy + Intervention", None): (
        "The structure needs redesigning and the situation it created is live right now. "
        "People Tactics and Strategy addresses the architecture. Intervention addresses the present."
    ),
    ("Intervention + People Tactics and Strategy", None): (
        "Intervention handles what is active. People Tactics and Strategy follows — so what produced it does not reassemble."
    ),
    ("Executive Advisory + Intervention", None): (
        "Executive Advisory provides the honest read on what the situation requires. Intervention executes it."
    ),
    ("Intervention + Executive Advisory", None): (
        "Intervention is present in the work. Executive Advisory is the confidential relationship running alongside it "
        "for the decisions the work produces."
    ),
    ("Training & Development + People Tactics and Strategy", None): (
        "Training & Development addresses the capability gap. People Tactics and Strategy addresses the structural conditions "
        "that keep recreating it."
    ),
    ("People Tactics and Strategy + Training & Development", None): (
        "People Tactics and Strategy redesigns the environment. Training & Development follows — because capability built "
        "inside a broken structure does not hold."
    ),
    ("Training & Development + Intervention", None): (
        "Intervention addresses what is live. Training & Development addresses what the organization needs to be "
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


