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
#
# Commercial-name correction (this session): "People Tactics and Strategy" ->
# "People Tactics & Strategy" (ampersand), "Intervention" -> "First Call".
# The dict KEYS below (the raw engine routing names, e.g. "Intervention") are
# UNCHANGED and never renamed -- engine/data/states.py's per-state
# resolution_family values and STATE_CAUSATION_OVERRIDES below both still use
# "Intervention" as an internal routing key. Only the commercial/display
# VALUE for that key changes. Mirrored exactly in
# web/lib/resolution-family.ts -- keep both in lockstep.

ENGINE_TO_COMMERCIAL_NAME: dict[str, str] = {
    "Roadmap":           "People Tactics & Strategy",
    "Development":       "Training & Development",
    "Intervention":      "First Call",
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



# ── hr_diagnostic (hr-dx.com) brand mapping ────────────────────────────────────
# PR's commercial tier names must never reach an hr-dx.com session. Every
# engine family maps to "HR Consulting" (the display value the web layer
# uses for resolution_family / resolution_routing on that brand), with the
# mapped OneDigital service references and an urgency cue carried into the
# AI synthesis context string below. Mapping per Pete, 2026-09-26. Mirrored
# on the web side by web/lib/resolution-family.ts's
# HR_DIAGNOSTIC_RESOLUTION_FAMILY -- keep both in lockstep.

HR_DIAGNOSTIC_FAMILY_NAME: str = "HR Consulting"

HR_DIAGNOSTIC_FAMILY_REFERENCES: dict[str, str] = {
    "Development":       "Employee Training & Education and Learning & Development Consulting",
    "Executive Counsel": "Employee Development, Coaching & Performance Management",
}

_HR_DIAGNOSTIC_URGENT_FAMILY = "Intervention"
_HR_DIAGNOSTIC_KNOWN_FAMILIES = ("Roadmap", "Development", "Intervention", "Executive Counsel")


def _hr_parts(engine_family_str: str) -> list[str]:
    # Unknown parts are dropped, never passed through -- a pass-through could
    # carry a PR name onto hr-dx.com.
    return [
        p.strip() for p in engine_family_str.split(" + ")
        if p.strip() in _HR_DIAGNOSTIC_KNOWN_FAMILIES
    ]


def hr_diagnostic_synthesis_family(engine_family_str: str) -> str:
    """
    hr_diagnostic replacement for translate_resolution_family() at the AI
    synthesis call site. Returns the resolution_family context string the
    synthesis prompt receives -- "HR Consulting", plus ", through <refs>"
    for Development / Executive Counsel and ", engaged immediately" when
    Intervention is present. Empty or wholly-unknown input returns "" (same
    as the PR path's empty-routing case).
    """
    parts = _hr_parts(engine_family_str)
    if not parts:
        return ""
    refs: list[str] = []
    for p in parts:
        ref = HR_DIAGNOSTIC_FAMILY_REFERENCES.get(p)
        if ref and ref not in refs:
            refs.append(ref)
    text = HR_DIAGNOSTIC_FAMILY_NAME
    if refs:
        text += ", through " + " and ".join(refs)
    if _HR_DIAGNOSTIC_URGENT_FAMILY in parts:
        text += ", engaged immediately"
    return text


# Failure-case backup copy for hr_diagnostic -- NEW COPY (2026-09-26),
# pending Pete's review. Tier-agnostic, one entry per engine family. Same
# fill pattern as the PR table (fallback_synthesis._make_entry puts the
# one string into liability/framing/resolution_framing text alike).
HR_DIAGNOSTIC_FALLBACK_COPY: dict[str, str] = {
    "Roadmap": (
        "The conditions producing this live in how the organization is designed, not in the people "
        "working inside it. HR Consulting addresses that structure directly, targeted at what the "
        "diagnostic found rather than at the symptoms."
    ),
    "Development": (
        "There is a capability gap. HR Consulting addresses it through Employee Training & Education "
        "and Learning & Development Consulting, built around the specific skills and practices the "
        "diagnostic identified."
    ),
    "Executive Counsel": (
        "The decisions this situation requires sit at the leadership level. HR Consulting supports "
        "them through Employee Development, Coaching & Performance Management, with an outside "
        "perspective that is hard to get from inside the organization."
    ),
    "Intervention": (
        "What the diagnostic found is active now and should not wait. HR Consulting engages directly "
        "and promptly, while there is still room to shape the outcome."
    ),
}


def hr_diagnostic_fallback_copy(engine_family_str: str) -> str:
    """
    Backup copy for an hr_diagnostic session. Compounds use the
    highest-priority family: Intervention (urgency) first, then the first
    of Development / Executive Counsel in order, then Roadmap.
    """
    parts = _hr_parts(engine_family_str)
    if not parts:
        return ""
    if _HR_DIAGNOSTIC_URGENT_FAMILY in parts:
        return HR_DIAGNOSTIC_FALLBACK_COPY[_HR_DIAGNOSTIC_URGENT_FAMILY]
    for p in parts:
        if p in HR_DIAGNOSTIC_FAMILY_REFERENCES:
            return HR_DIAGNOSTIC_FALLBACK_COPY[p]
    return HR_DIAGNOSTIC_FALLBACK_COPY[parts[0]]


def _build_hr_fallback_by_context() -> dict[str, str]:
    # Keyed by the exact context string synthesize() receives, so
    # get_fallback_synthesis() can resolve it without a brand parameter.
    # Every ordered combination of distinct known families (lengths 1-4),
    # so any compound the taxonomy or a causation override produces is
    # covered. Two engine strings can share a context string (e.g. Roadmap
    # + Intervention / Intervention + Roadmap) -- asserted to map to the
    # same copy, never silently overwritten.
    from itertools import permutations
    table: dict[str, str] = {}
    for n in range(1, len(_HR_DIAGNOSTIC_KNOWN_FAMILIES) + 1):
        for combo in permutations(_HR_DIAGNOSTIC_KNOWN_FAMILIES, n):
            engine_str = " + ".join(combo)
            ctx = hr_diagnostic_synthesis_family(engine_str)
            copy = hr_diagnostic_fallback_copy(engine_str)
            existing = table.get(ctx)
            if existing is not None and existing != copy:
                raise ValueError(f"hr_diagnostic fallback conflict for context {ctx!r}")
            table[ctx] = copy
    return table


HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT: dict[str, str] = _build_hr_fallback_by_context()


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
# CLOSED, 2026-09-03/04: all 19 mechanically-reachable states (every state
# with a single, non-compound default resolution_family) have now been
# explicitly reviewed and decided, Pete's own clinical judgment throughout.
# 15 carry real entries below; 4 were deliberately excluded with documented
# reasoning (see below) -- zero silent decisions either way. Authored across
# 4 groups, by each state's real shipped resolution_family default at the
# time (not a task-header label -- see the 2026-09-03 Section 16 entries in
# tools/_mob.txt for the "Executive Counsel group" naming correction):
# leadership_deafness/the_broken_compass ("Executive Counsel"),
# the_unformed_leader ("Development"), 8 of 9 "Intervention"-default states
# (the_uninitiated, what_nobody_says, the_diversity_ceiling,
# identity_erosion, the_culture_that_wasnt, the_burned_credibility,
# the_unreported_hazard, wellbeing_theater), and pay_exposure/
# compression_crisis/silosolation plus paper_shield ("Roadmap"-default
# states -- paper_shield itself was a standalone worked example decided
# earlier, not a group member). All defaults confirmed single-family
# (non-compound) directly against engine/data/states.py before authoring.
#
# Every entry below carries only one key -- diffuse-default states carry a
# "diffuse" key, single_point-default states carry a "single_point" key --
# the other causation_pattern is meant to fall through to the existing
# default via apply_causation_override()'s own dict.get() fallback, sparse
# by design, not an oversight. silosolation was the one exception carrying
# both keys through 2026-09-04, deliberately routing neither pattern to its
# then-shipped "Development" default -- its descriptive_prose ("the
# isolation isn't hostile. It's structural") sat in tension with that
# default. RESOLVED 2026-09-04, Pete's confirmed decision: the base default
# itself corrected to "Roadmap" in engine/data/states.py (not just an
# override), so the "diffuse" key became redundant (it now matches what
# diffuse would fall through to anyway) and was removed -- silosolation now
# follows the same single-key pattern as every other entry. Independent
# Gemini architecture review of this correction disputed the real vector
# values cited above and asserted a fabricated alternative -- see
# tools/_mob.txt's Key Learnings fabrication-pattern record for the full
# instance; the substantive recommendation (change the default, simplify
# the entry) was correct and was acted on based on independent verification,
# not the disputed claim.
#
# 4 states are DELIBERATELY EXCLUDED from any override -- do not add
# entries for any of them:
#   culture_drift ("Intervention" default) -- (1) descriptive_prose
#     ("drifted apart gradually enough that no single moment marks the
#     change... nobody decided") is definitionally diffuse-only, no
#     coherent single_point reading exists; (2) it is this test suite's
#     synthetic grounding fixture for the no-override-entry fallback path
#     (tools/test_resolution_families.py's _SINGLE_DEFAULT tests) -- those
#     assertions depend on it having no real entry here.
#   the_undefined_role ("Roadmap" default) -- chronic/structural drag
#     language ("duplicates... unclaimed... paying for a function that
#     isn't reliably producing"), no acute-crisis framing. One role or
#     many, the fix is the same kind of work (define the boundaries) --
#     Roadmap already absorbs scope differences, no distinct single_point
#     resolution exists.
#   the_policy_lag ("Roadmap" default) -- same reasoning: "quietly
#     diverged" is passive/chronic, not urgent. One stale policy or many,
#     same kind of fix.
#   the_pay_fog ("Roadmap" default) -- definitionally diffuse-only, same
#     category as culture_drift: its own prose ("hard to see from inside
#     any one decision, impossible to miss once someone lines them all up")
#     means the concept only exists as a cross-decision pattern -- a
#     "single_point" pay fog isn't a coherent state.
STATE_CAUSATION_OVERRIDES: dict[str, dict[str, str]] = {
    "paper_shield": {"single_point": "Intervention", "diffuse": "Roadmap"},
    "leadership_deafness": {"diffuse": "Roadmap"},
    "the_broken_compass": {"diffuse": "Intervention"},
    "the_unformed_leader": {"diffuse": "Roadmap"},
    "silosolation": {"single_point": "Intervention"},
    "the_uninitiated": {"diffuse": "Development"},
    "what_nobody_says": {"diffuse": "Roadmap"},
    "the_diversity_ceiling": {"diffuse": "Roadmap"},
    "identity_erosion": {"diffuse": "Roadmap"},
    "the_culture_that_wasnt": {"diffuse": "Roadmap"},
    "the_burned_credibility": {"diffuse": "Roadmap"},
    "pay_exposure": {"single_point": "Intervention"},
    "compression_crisis": {"single_point": "Intervention"},
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
#
# Commercial-name correction (this session): every key and prose value below
# using "People Tactics and Strategy" or "Intervention" as a commercial/
# display name is updated to "People Tactics & Strategy" / "First Call".
# This dict is entirely commercial-name space (its own docstring: "Keyed by
# (commercial_name, severity_tier)") -- unlike STATE_CAUSATION_OVERRIDES
# above, nothing here is a raw engine key, so every occurrence in this block
# was safe to rename.

RESOLUTION_FALLBACK_COPY: dict[tuple[str, str | None], str] = {

    # People Tactics & Strategy — engine: Roadmap
    ("People Tactics & Strategy", "Emerging"): (
        "A structural problem requires structural work. People Tactics & Strategy brings in the right expertise, "
        "targeted at what the diagnostic found, before it has time to settle in deeper."
    ),
    ("People Tactics & Strategy", "Entrenched"): (
        "The conditions producing this live in how your organization is designed, not in the people "
        "navigating it. People Tactics & Strategy addresses that level directly — expert, targeted, and aimed "
        "at the architecture rather than the symptoms."
    ),
    ("People Tactics & Strategy", "Endemic"): (
        "When a condition becomes the environment, adjusting what happens inside it is not enough. "
        "People Tactics & Strategy is the structural redesign — expert work at the level where the problem actually lives."
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
    ("People Tactics & Strategy + First Call", None): (
        "The structure needs redesigning and the situation it created is live right now. "
        "People Tactics & Strategy addresses the architecture. First Call addresses the present."
    ),
    ("First Call + People Tactics & Strategy", None): (
        "First Call handles what is active. People Tactics & Strategy follows — so what produced it does not reassemble."
    ),
    ("Executive Advisory + First Call", None): (
        "Executive Advisory provides the honest read on what the situation requires. First Call executes it."
    ),
    ("First Call + Executive Advisory", None): (
        "First Call is present in the work. Executive Advisory is the confidential relationship running alongside it "
        "for the decisions the work produces."
    ),
    ("Training & Development + People Tactics & Strategy", None): (
        "Training & Development addresses the capability gap. People Tactics & Strategy addresses the structural conditions "
        "that keep recreating it."
    ),
    ("People Tactics & Strategy + Training & Development", None): (
        "People Tactics & Strategy redesigns the environment. Training & Development follows — because capability built "
        "inside a broken structure does not hold."
    ),
    ("Training & Development + First Call", None): (
        "First Call addresses what is live. Training & Development addresses what the organization needs to be "
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


