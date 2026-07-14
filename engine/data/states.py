"""
PRV3 Scoring Engine — Section I.1
State Profile Schema and Registry

All 47 confirmed states. Dimensional vectors seeded from Signal Map tier
assignments (Session 12): primary liability field -> high=0.60, medium=0.40,
low/cluster=0.25 (baseline). Asset fields at 0.25. Salience weights for
residual collisions derived from Phase 1 Confusion Matrix analysis.

Source documents:
  - State names and signal architecture: PRV3_Question_Signal_Map.docx (May 2026)
  - Severity range, resolution family, axis descriptions: PRV3_State_Taxonomy_Profiles.docx (April 2026)
  - Canonical dimension/cluster assignments: PRV3_MOB_v1.2.md (May 2026)

NOTE — COUNT: Aptitude (7), Authority (22), Alliance (7), Attitude (21) = 57.
Taxonomy expansion (Session 65 decision, Session 67 implementation): 10 states added.
Per-state classification fields (signal_weight, cluster_id, axes, severity_range,
resolution_family, dimensional_vector) for the 10 new states are DRAFT — authored
this session from consolidation-mapping-trace.md disposition rationale and analogy
to the closest existing state, NOT independently Gemini-reviewed. See
prompts/gemini-handoff-taxonomy-expansion-57.md.
Rename applied: invisible_performance_management → the_paper_tiger (moved to Aptitude).
Second removal pending Pete confirmation per state_removal_final.md step 4.

NOTE — NAME MAPPING: The April 2026 profiles document uses clinical working names
for 28 states that the May 2026 QSM and MOB renamed to evocative canonical names.
Severity range and resolution family for those 28 states were drawn from the
profiles document via conceptual matching. Inferred mappings are marked below.
Pete to verify if any mapping is incorrect.

Inferred mappings (QSM canonical name <- profiles doc working name):
  The Dormant Talent          <- Manager Investment Failure
  Built to Fail               <- Structural Overload
  The Undefined Role          <- Role Clarity Deficit
  The Policy Lag              <- Policy Currency Gap
  The Unexamined Algorithm    <- AI Governance Failure
  Heard & Ignored             <- Internal Reporting Failure
  The Tolerated Violation     <- Compliance Normalization
  Dueling Narratives          <- Disclosure Misalignment
  The Unsolved Problem        <- Recidivism Risk
  Paper Shield                <- Resilience Architecture Gap
  The Lost Map                <- Information Architecture Failure
  Pay Exposure                <- Market Exposure
  The Pay Fog                 <- Compensation Incoherence
  The Suppression Filter      <- Information Suppression Cascade
  The Arbitrary Standard      <- Process Justice Failure
  Decision Blindness          <- Sequential Decision Blindness
  What Nobody Says            <- Psychological Safety Collapse
  Leadership Deafness         <- Organizational Deafness
  The Diversity Ceiling       <- Performative Equity
  The Culture That Wasn't     <- Values Misrepresentation
  The Burned Credibility      <- Change Absorption Failure
  The Basement Standard       <- Unmanaged Underperformance
  The Inside Track            <- Favoritism Architecture
  Groundhog Day               <- Learning Architecture Failure
  The Wrong Reward            <- Motivational Architecture Failure
  The Unreported Hazard       <- Safety Culture Deficit
  The Unlocked Door           <- Security Culture Gap
  The Broken Compass          <- Implementation Courage Deficit
"""

from dataclasses import dataclass, field
from typing import Optional

# ── Enumerations (string constants — not Python enum to keep JSON-serialisable) ──

DIMENSIONS = ("Aptitude", "Authority", "Alliance", "Attitude")

SEVERITY_TIERS = ("Emerging", "Entrenched", "Endemic")

SIGNAL_WEIGHTS = ("high", "medium", "low", "cluster")

CLUSTER_IDS = ("C-Manager", "C-Culture", "C-Silence", "C-InfoFlow")

# Liability Risk Framework categories (source: PRV3_Frameworks.docx)
LIABILITY_CATEGORIES = (
    "Legal & Compliance",
    "Financial & Economic",
    "Governance & Authority",
    "Talent & Retention",
    "Cultural & Behavioral",
    "Operational & Structural",
    "Reputational & Brand",
    "Safety & Wellbeing",
    "Strategic",
)

# Leadership Competency Framework domains (source: PRV3_Frameworks.docx)
ASSET_DOMAINS = (
    "Accountability Architecture",
    "Adaptive Capacity",
    "Communication Integrity",
    "Governance Discipline",
    "People Development Capability",
    "Relational Trust",
    "Strategic Execution Capacity",
    "Cultural Stewardship",
)

DIMENSIONAL_FIELDS = (
    "aptitude_liability",
    "aptitude_asset",
    "authority_liability",
    "authority_asset",
    "alliance_liability",
    "alliance_asset",
    "attitude_liability",
    "attitude_asset",
)

BASELINE_VALUE = 0.25  # Equal-weight calibration baseline — CALIBRATION TARGET


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class DimensionalVector:
    """
    Eight-field vector representing a state's target profile in dimensional space.
    All fields initialize at BASELINE_VALUE (0.25) until Phase 1 calibration.
    Each field: float 0.0–1.0.
    """
    aptitude_liability:  float = BASELINE_VALUE
    aptitude_asset:      float = BASELINE_VALUE
    authority_liability: float = BASELINE_VALUE
    authority_asset:     float = BASELINE_VALUE
    alliance_liability:  float = BASELINE_VALUE
    alliance_asset:      float = BASELINE_VALUE
    attitude_liability:  float = BASELINE_VALUE
    attitude_asset:      float = BASELINE_VALUE

    def as_dict(self) -> dict:
        return {f: getattr(self, f) for f in DIMENSIONAL_FIELDS}


@dataclass
class SeverityRange:
    """Minimum and maximum severity tier this state can manifest."""
    min: str  # Emerging | Entrenched | Endemic
    max: str  # Emerging | Entrenched | Endemic


@dataclass
class StateProfile:
    """
    Complete profile for one diagnostic state.
    Spec reference: Section I.1
    """
    state_id:           str                  # lowercase_snake_case
    state_name:         str                  # Display name
    primary_dimension:  str                  # Aptitude | Authority | Alliance | Attitude
    dimensional_vector: DimensionalVector
    signal_weight:      str                  # high | medium | low | cluster
    cluster_id:         Optional[str]        # C-Manager | C-Culture | C-Silence | C-InfoFlow | None
    liability_axes:     list                 # From Liability Risk Framework
    asset_axes:         list                 # From Leadership Competency Framework
    severity_range:     SeverityRange
    resolution_family:  str                  # One of the five service offerings


# ── Helper ─────────────────────────────────────────────────────────────────────

_DIM_LIABILITY_FIELD: dict = {
    "Aptitude":  "aptitude_liability",
    "Authority": "authority_liability",
    "Alliance":  "alliance_liability",
    "Attitude":  "attitude_liability",
}

_SIGNAL_WEIGHT_TO_VALUE: dict = {
    "high":    0.60,
    "medium":  0.40,
    "low":     BASELINE_VALUE,
    "cluster": BASELINE_VALUE,
}


def _profile(
    state_id, state_name, primary_dimension,
    signal_weight, cluster_id,
    liability_axes, asset_axes,
    sev_min, sev_max,
    resolution_family,
):
    """Construct a StateProfile with seeded dimensional vector.

    Primary liability field seeded from Signal Map tier assignment:
      high -> 0.60 | medium -> 0.40 | low/cluster -> 0.25 (BASELINE_VALUE)
    All other fields remain at BASELINE_VALUE (0.25).
    Asset fields unchanged -- Phase 1 calibration target.

    Source: Signal Map tier assignments (Session 12).
    Spec reference: Section I.1
    """
    seed_val  = _SIGNAL_WEIGHT_TO_VALUE.get(signal_weight, BASELINE_VALUE)
    lib_field = _DIM_LIABILITY_FIELD.get(primary_dimension, "")
    vec_kwargs = (
        {lib_field: seed_val}
        if lib_field and seed_val != BASELINE_VALUE
        else {}
    )

    return StateProfile(
        state_id=state_id,
        state_name=state_name,
        primary_dimension=primary_dimension,
        dimensional_vector=DimensionalVector(**vec_kwargs),
        signal_weight=signal_weight,
        cluster_id=cluster_id,
        liability_axes=liability_axes,
        asset_axes=asset_axes,
        severity_range=SeverityRange(min=sev_min, max=sev_max),
        resolution_family=resolution_family,
    )


# ── State Registry ─────────────────────────────────────────────────────────────
# Ordered by: Aptitude → Authority → Alliance → Attitude (matching MOB taxonomy)

STATE_PROFILES: dict[str, StateProfile] = {}

def _reg(profile: StateProfile) -> StateProfile:
    STATE_PROFILES[profile.state_id] = profile
    return profile


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  APTITUDE  (6 states)                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

_reg(_profile(
    state_id="the_unformed_leader",
    state_name="The Unformed Leader",
    primary_dimension="Aptitude",
    signal_weight="cluster",
    cluster_id="C-Manager",
    liability_axes=["Talent & Retention", "Financial & Economic"],
    asset_axes=["People Development Capability", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Endemic",
    resolution_family="Development",
))
STATE_PROFILES["the_unformed_leader"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.35,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.25,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_overloaded_manager",
    state_name="The Overloaded Manager",
    primary_dimension="Aptitude",
    signal_weight="cluster",
    cluster_id="C-Manager",
    liability_axes=["Talent & Retention", "Operational & Structural"],
    asset_axes=["People Development Capability", "Governance Discipline"],
    sev_min="Emerging", sev_max="Entrenched",
    resolution_family="Development + Roadmap",
))
STATE_PROFILES["the_overloaded_manager"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.35,
    aptitude_asset=0.15,
    authority_liability=0.25,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_dormant_talent",
    state_name="The Dormant Talent",
    primary_dimension="Aptitude",
    signal_weight="cluster",
    cluster_id="C-Manager",
    liability_axes=["Talent & Retention", "Cultural & Behavioral"],
    asset_axes=["Accountability Architecture", "People Development Capability"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Manager Investment Failure
    resolution_family="Executive Counsel + Intervention",
))
STATE_PROFILES["the_dormant_talent"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.35,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.25,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="built_to_fail",
    state_name="Built to Fail",
    primary_dimension="Aptitude",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Operational & Structural", "Financial & Economic", "Talent & Retention"],
    asset_axes=["Governance Discipline", "Strategic Execution Capacity"],
    sev_min="Emerging", sev_max="Endemic",
    # Inferred from profiles doc: Structural Overload
    resolution_family="Roadmap + Intervention",
))
STATE_PROFILES["built_to_fail"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.60,
    aptitude_asset=0.10,
    authority_liability=0.10,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="the_undefined_role",
    state_name="The Undefined Role",
    primary_dimension="Aptitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Operational & Structural", "Financial & Economic"],
    asset_axes=["Governance Discipline", "Communication Integrity"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Role Clarity Deficit
    resolution_family="Roadmap",
))
STATE_PROFILES["the_undefined_role"].dimensional_vector = DimensionalVector(  # S29 Rank 3: dual-axis reshape, was single-axis apt_l=0.45
    aptitude_liability=0.35,
    aptitude_asset=0.15,
    authority_liability=0.35,
    authority_asset=0.15,
    alliance_liability=0.10,
    alliance_asset=0.15,
    attitude_liability=0.10,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_paper_tiger",
    state_name="The Paper Tiger",
    primary_dimension="Aptitude",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Financial & Economic"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Entrenched", sev_max="Entrenched",
    # Renamed from clinical name: Invisible Performance Management (profiles doc #33)
    resolution_family="Development + Roadmap",
))
STATE_PROFILES["the_paper_tiger"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.60,
    aptitude_asset=0.10,
    authority_liability=0.10,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)


# ============================================================
# TAXONOMY EXPANSION (47→57) — Session 67 draft, Gemini review complete Session 68.
# State names + dimension assignments: LOCKED (Session 65).
# signal_weight, severity range, resolution family, liability/asset axes,
# dimensional vectors, salience, signature clustering: CONFIRMED per-state below
# (see each entry's own comment — most confirmed as-drafted; wellbeing_theater and
# human_displacement_anxiety were revised). Full detail in
# prompts/gemini-handoff-taxonomy-expansion-57.md. Calibration (test-profile pass
# rate) is separately still in progress — see engine/test_profiles_expansion.py and
# tools/calibration_runner.py; a CONFIRMED classification does not imply a
# calibrated dimensional_vector yet.
# ============================================================
_reg(_profile(
    state_id="invisible_performance_management",
    state_name="Invisible Performance Management",
    primary_dimension="Aptitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Talent & Retention"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Entrenched",
    # CONFIRMED — Gemini review complete (round two, Session 68). E2 #06
    # (consolidation-mapping-trace.md Batch A). No changes from the Session 67 draft.
    # NAMING HISTORY: this exact state_id/name was previously used pre-rename for what
    # is now the_paper_tiger (see NOTE — NAME MAPPING above, profiles doc #33, and
    # the_paper_tiger's own "Renamed from clinical name" comment below). That entry was
    # fully removed from this registry years ago (state_removal_final.md, 45-vs-47 count
    # question, resolved at 47) -- no live id collision. This is a mechanistically
    # distinct NEW state per Session 65's disposition: accurate managerial judgment
    # rendered legally indefensible solely by lack of documentation, distinct from
    # The Paper Tiger's active-concealment mechanism. Gemini's condition for accepting
    # the reuse -- confirm no legacy analysis/migration script string-matches the
    # retired identifier against old log files -- was checked Session 68: the only
    # repo hits are this new state's own files and inert historical prose
    # (state_removal_final.md, state_removal_v3.md, state_count_resolved.md); no
    # executable script references it. Condition satisfied.
    resolution_family="Development + Roadmap",
))
STATE_PROFILES["invisible_performance_management"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.45,
    aptitude_asset=0.15,
    authority_liability=0.25,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.10,
    attitude_asset=0.15,
)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  AUTHORITY  (22 states)                                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

_reg(_profile(
    state_id="the_founders_grip",
    state_name="The Founder's Grip",
    primary_dimension="Authority",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Governance & Authority", "Talent & Retention", "Strategic"],
    asset_axes=["Governance Discipline", "Adaptive Capacity"],
    sev_min="Entrenched", sev_max="Endemic",
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["the_founders_grip"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.60,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="the_exposed",
    state_name="The Exposed",
    primary_dimension="Authority",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Financial & Economic"],
    asset_axes=["Governance Discipline", "Relational Trust"],
    sev_min="Emerging", sev_max="Entrenched",
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["the_exposed"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.60,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="the_uninitiated",
    state_name="The Uninitiated",
    primary_dimension="Authority",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Governance & Authority", "Legal & Compliance", "Strategic"],
    asset_axes=["Adaptive Capacity", "Governance Discipline"],
    sev_min="Emerging", sev_max="Emerging",  # Acute by definition
    resolution_family="Intervention",
))
STATE_PROFILES["the_uninitiated"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.45,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="leadership_continuity_risk",
    state_name="Leadership Continuity Risk",
    primary_dimension="Authority",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Governance & Authority", "Financial & Economic", "Strategic"],
    asset_axes=["Governance Discipline", "People Development Capability"],
    sev_min="Emerging", sev_max="Entrenched",
    resolution_family="Roadmap + Development",
))
STATE_PROFILES["leadership_continuity_risk"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.45,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="hr_capture",
    state_name="HR Capture",
    primary_dimension="Authority",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Cultural & Behavioral"],
    asset_axes=["Governance Discipline", "Relational Trust"],
    sev_min="Entrenched", sev_max="Endemic",
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["hr_capture"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.60,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="decision_paralysis",
    state_name="Decision Paralysis",
    primary_dimension="Authority",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Governance & Authority", "Financial & Economic", "Operational & Structural"],
    asset_axes=["Governance Discipline", "Strategic Execution Capacity"],
    sev_min="Emerging", sev_max="Entrenched",
    resolution_family="Roadmap + Intervention",
))
STATE_PROFILES["decision_paralysis"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.45,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_policy_lag",
    state_name="The Policy Lag",
    primary_dimension="Authority",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Financial & Economic"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Policy Currency Gap
    resolution_family="Roadmap",
))
STATE_PROFILES["the_policy_lag"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.45,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_unexamined_algorithm",
    state_name="The Unexamined Algorithm",
    primary_dimension="Authority",
    signal_weight="low",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Safety & Wellbeing"],
    asset_axes=["Governance Discipline", "Adaptive Capacity"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: AI Governance Failure
    resolution_family="Roadmap + Executive Counsel",
))
STATE_PROFILES["the_unexamined_algorithm"].dimensional_vector = DimensionalVector(
    authority_liability=0.50,
    aptitude_liability=0.35,
    authority_asset=0.10,
    aptitude_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)


_reg(_profile(
    state_id="heard_and_ignored",
    state_name="Heard & Ignored",
    primary_dimension="Authority",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Cultural & Behavioral"],
    asset_axes=["Governance Discipline", "Relational Trust"],
    sev_min="Entrenched", sev_max="Endemic",
    # Inferred from profiles doc: Internal Reporting Failure
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["heard_and_ignored"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.60,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="the_tolerated_violation",
    state_name="The Tolerated Violation",
    primary_dimension="Authority",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Cultural & Behavioral", "Financial & Economic"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Entrenched", sev_max="Endemic",
    # Inferred from profiles doc: Compliance Normalization
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["the_tolerated_violation"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.60,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="dueling_narratives",
    state_name="Dueling Narratives",
    primary_dimension="Authority",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Reputational & Brand", "Legal & Compliance", "Governance & Authority"],
    asset_axes=["Governance Discipline", "Communication Integrity"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Disclosure Misalignment
    resolution_family="Executive Counsel + Roadmap",
))
STATE_PROFILES["dueling_narratives"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.45,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_unsolved_problem",
    state_name="The Unsolved Problem",
    primary_dimension="Authority",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Financial & Economic", "Cultural & Behavioral"],
    asset_axes=["Adaptive Capacity", "Governance Discipline"],
    sev_min="Entrenched", sev_max="Entrenched",  # Fixed tier
    # Inferred from profiles doc: Recidivism Risk
    resolution_family="Intervention + Roadmap",
))
STATE_PROFILES["the_unsolved_problem"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.60,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="transition_paralysis",
    state_name="Transition Paralysis",
    primary_dimension="Authority",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Operational & Structural", "Talent & Retention", "Financial & Economic"],
    asset_axes=["Strategic Execution Capacity", "Adaptive Capacity"],
    sev_min="Emerging", sev_max="Entrenched",
    resolution_family="Intervention + Roadmap",
))
STATE_PROFILES["transition_paralysis"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.45,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="paper_shield",
    state_name="Paper Shield",
    primary_dimension="Authority",
    signal_weight="low",
    cluster_id=None,
    liability_axes=["Governance & Authority", "Operational & Structural", "Financial & Economic"],
    asset_axes=["Adaptive Capacity", "Governance Discipline"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Resilience Architecture Gap
    resolution_family="Roadmap",
))
STATE_PROFILES["paper_shield"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.35,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_lost_map",
    state_name="The Lost Map",
    primary_dimension="Authority",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Operational & Structural", "Talent & Retention", "Cultural & Behavioral"],
    asset_axes=["Communication Integrity", "Governance Discipline"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Information Architecture Failure
    resolution_family="Roadmap + Development",
))
STATE_PROFILES["the_lost_map"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.45,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="invisible_influence_architecture",
    state_name="Invisible Influence Architecture",
    primary_dimension="Authority",
    signal_weight="low",
    cluster_id=None,
    liability_axes=["Operational & Structural", "Talent & Retention", "Strategic"],
    asset_axes=["Communication Integrity", "Adaptive Capacity"],
    sev_min="Emerging", sev_max="Entrenched",
    resolution_family="Roadmap + Executive Counsel",
))
STATE_PROFILES["invisible_influence_architecture"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.35,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="pay_exposure",
    state_name="Pay Exposure",
    primary_dimension="Authority",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Talent & Retention", "Financial & Economic", "Strategic"],
    asset_axes=["Governance Discipline", "Strategic Execution Capacity"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Market Exposure
    resolution_family="Roadmap",
))
STATE_PROFILES["pay_exposure"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.45,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_pay_fog",
    state_name="The Pay Fog",
    primary_dimension="Authority",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Financial & Economic", "Reputational & Brand"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Compensation Incoherence
    resolution_family="Roadmap",
))
STATE_PROFILES["the_pay_fog"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.45,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)


_reg(_profile(
    state_id="compression_crisis",
    state_name="Compression Crisis",
    primary_dimension="Authority",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Talent & Retention", "Financial & Economic", "Legal & Compliance"],
    asset_axes=["Governance Discipline", "Strategic Execution Capacity"],
    sev_min="Emerging", sev_max="Entrenched",
    # CONFIRMED — Gemini review complete (round two, Session 68). E6
    # (consolidation-mapping-trace.md Batch C). No changes from the Session 67 draft.
    resolution_family="Roadmap",
))
STATE_PROFILES["compression_crisis"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.45,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="sequential_decision_blindness",
    state_name="Sequential Decision Blindness",
    primary_dimension="Authority",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Financial & Economic"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Entrenched",
    # CONFIRMED — Gemini review complete (round two, Session 68). E2
    # (consolidation-mapping-trace.md Batch E). No changes from the Session 67 draft.
    # NAMING COLLISION (Session 65 required mitigation): "Sequential Decision Blindness"
    # is also the profiles-doc inferred-mapping source name for the LOCKED Alliance-
    # dimension state decision_blindness (see NOTE — NAME MAPPING above). Confirmed
    # distinct per trace: retaliation-liability pattern from uncoordinated sequential
    # decisions (this state, Authority), vs. decision_blindness's single-decision
    # coordination failure (Alliance). Different dimension, different mechanism.
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["sequential_decision_blindness"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.60,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="disparate_impact_architecture",
    state_name="Disparate Impact Architecture",
    primary_dimension="Authority",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Financial & Economic", "Reputational & Brand"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Entrenched", sev_max="Endemic",
    # CONFIRMED — Gemini review complete (round two, Session 68). E2 #02
    # (consolidation-mapping-trace.md Batch C). No changes from the Session 67 draft.
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["disparate_impact_architecture"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.60,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="planning_authority_gap",
    state_name="Planning Authority Gap",
    primary_dimension="Authority",
    signal_weight="low",
    cluster_id=None,
    liability_axes=["Operational & Structural", "Strategic", "Talent & Retention"],
    asset_axes=["Strategic Execution Capacity", "Governance Discipline"],
    sev_min="Emerging", sev_max="Entrenched",
    # CONFIRMED — Gemini review complete (round two, Session 68). E6
    # (consolidation-mapping-trace.md Batch F). No changes from the Session 67 draft.
    resolution_family="Roadmap + Executive Counsel",
))
STATE_PROFILES["planning_authority_gap"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.35,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  ALLIANCE  (7 states)                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

_reg(_profile(
    state_id="the_fracture",
    state_name="The Fracture",
    primary_dimension="Alliance",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Talent & Retention", "Cultural & Behavioral", "Financial & Economic"],
    asset_axes=["Relational Trust", "Governance Discipline"],
    sev_min="Entrenched", sev_max="Endemic",
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["the_fracture"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.10,
    authority_asset=0.10,
    alliance_liability=0.60,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="the_second_close",
    state_name="The Second Close",
    primary_dimension="Alliance",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Talent & Retention", "Strategic", "Cultural & Behavioral"],
    asset_axes=["Strategic Execution Capacity", "Cultural Stewardship"],
    sev_min="Emerging", sev_max="Entrenched",
    resolution_family="Development + Intervention",
))
STATE_PROFILES["the_second_close"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.45,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="silosolation",
    state_name="Silosolation",
    primary_dimension="Alliance",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Operational & Structural", "Financial & Economic", "Cultural & Behavioral"],
    asset_axes=["Governance Discipline", "Relational Trust"],
    sev_min="Entrenched", sev_max="Endemic",
    resolution_family="Development",
))
STATE_PROFILES["silosolation"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.45,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_suppression_filter",
    state_name="The Suppression Filter",
    primary_dimension="Alliance",
    signal_weight="cluster",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Governance & Authority", "Strategic"],
    asset_axes=["Communication Integrity", "Relational Trust"],
    sev_min="Entrenched", sev_max="Endemic",
    # Inferred from profiles doc: Information Suppression Cascade
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["the_suppression_filter"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.25,
    authority_asset=0.15,
    alliance_liability=0.35,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_arbitrary_standard",
    state_name="The Arbitrary Standard",
    primary_dimension="Alliance",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Legal & Compliance"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Process Justice Failure
    resolution_family="Intervention + Roadmap",
))
STATE_PROFILES["the_arbitrary_standard"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.45,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="decision_blindness",
    state_name="Decision Blindness",
    primary_dimension="Alliance",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Financial & Economic"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Sequential Decision Blindness
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["decision_blindness"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.10,
    authority_asset=0.10,
    alliance_liability=0.60,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)


_reg(_profile(
    state_id="distributed_culture_fragmentation",
    state_name="Distributed Culture Fragmentation",
    primary_dimension="Alliance",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Operational & Structural"],
    asset_axes=["Cultural Stewardship", "Relational Trust"],
    sev_min="Emerging", sev_max="Entrenched",
    # CONFIRMED — Gemini review complete (round two, Session 68). E6
    # (consolidation-mapping-trace.md Batch F). No changes from the Session 67 draft.
    resolution_family="Development + Intervention",
))
STATE_PROFILES["distributed_culture_fragmentation"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.45,
    alliance_asset=0.15,
    attitude_liability=0.25,
    attitude_asset=0.15,
)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  ATTITUDE  (21 states)                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

_reg(_profile(
    state_id="the_untouchable",
    state_name="The Untouchable",
    primary_dimension="Attitude",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Legal & Compliance"],
    asset_axes=["Accountability Architecture", "Governance Discipline"],
    sev_min="Entrenched", sev_max="Endemic",
    resolution_family="Executive Counsel + Intervention",
))
STATE_PROFILES["the_untouchable"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.10,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.60,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="what_nobody_says",
    state_name="What Nobody Says",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Governance & Authority", "Strategic"],
    asset_axes=["Relational Trust", "Communication Integrity"],
    sev_min="Emerging", sev_max="Endemic",
    # Inferred from profiles doc: Psychological Safety Collapse
    resolution_family="Intervention",
))
STATE_PROFILES["what_nobody_says"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.35,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="leadership_deafness",
    state_name="Leadership Deafness",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id=None,
    liability_axes=["Governance & Authority", "Cultural & Behavioral", "Strategic"],
    asset_axes=["Communication Integrity", "Adaptive Capacity"],
    sev_min="Entrenched", sev_max="Endemic",
    # Inferred from profiles doc: Organizational Deafness
    resolution_family="Executive Counsel",
))
STATE_PROFILES["leadership_deafness"].dimensional_vector = DimensionalVector(  # v23: att_l=0.50, all others=0.10
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.10,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.50,
    attitude_asset=0.10,
)

_reg(_profile(
    state_id="the_diversity_ceiling",
    state_name="The Diversity Ceiling",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Talent & Retention", "Reputational & Brand"],
    asset_axes=["People Development Capability", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Endemic",
    # Inferred from profiles doc: Performative Equity
    resolution_family="Intervention",
))
STATE_PROFILES["the_diversity_ceiling"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="culture_drift",
    state_name="Culture Drift",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id="C-Culture",
    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Reputational & Brand"],
    asset_axes=["Cultural Stewardship", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Endemic",
    resolution_family="Intervention",
))
STATE_PROFILES["culture_drift"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.25,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.35,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="identity_erosion",
    state_name="Identity Erosion",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id="C-Culture",
    liability_axes=["Talent & Retention", "Cultural & Behavioral", "Reputational & Brand"],
    asset_axes=["Cultural Stewardship", "Communication Integrity"],
    sev_min="Emerging", sev_max="Endemic",
    resolution_family="Intervention",
))
STATE_PROFILES["identity_erosion"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.35,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_culture_that_wasnt",
    state_name="The Culture That Wasn't",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id="C-Culture",
    liability_axes=["Talent & Retention", "Reputational & Brand", "Financial & Economic"],
    asset_axes=["Cultural Stewardship", "Communication Integrity"],
    sev_min="Emerging", sev_max="Emerging",  # Acute at point of discovery
    # Inferred from profiles doc: Values Misrepresentation
    resolution_family="Intervention",
))
STATE_PROFILES["the_culture_that_wasnt"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.35,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_burned_credibility",
    state_name="The Burned Credibility",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Strategic", "Financial & Economic"],
    asset_axes=["Adaptive Capacity", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Endemic",
    # Inferred from profiles doc: Change Absorption Failure
    resolution_family="Intervention",
))
STATE_PROFILES["the_burned_credibility"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="invisible_burnout",
    state_name="Invisible Burnout",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Talent & Retention", "Safety & Wellbeing", "Financial & Economic"],
    asset_axes=["People Development Capability", "Governance Discipline"],
    sev_min="Emerging", sev_max="Entrenched",
    resolution_family="Development + Intervention",
))
STATE_PROFILES["invisible_burnout"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_basement_standard",
    state_name="The Basement Standard",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Financial & Economic"],
    asset_axes=["Accountability Architecture", "Governance Discipline"],
    sev_min="Entrenched", sev_max="Endemic",
    # Inferred from profiles doc: Unmanaged Underperformance
    resolution_family="Intervention + Roadmap",
))
STATE_PROFILES["the_basement_standard"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_inside_track",
    state_name="The Inside Track",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Legal & Compliance"],
    asset_axes=["Accountability Architecture", "Governance Discipline"],
    sev_min="Entrenched", sev_max="Endemic",
    # Inferred from profiles doc: Favoritism Architecture
    resolution_family="Intervention + Roadmap",
))
STATE_PROFILES["the_inside_track"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="narrative_lock",
    state_name="Narrative Lock",
    primary_dimension="Attitude",
    signal_weight="low",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Strategic", "Financial & Economic"],
    asset_axes=["Adaptive Capacity", "Relational Trust"],
    sev_min="Entrenched", sev_max="Endemic",
    resolution_family="Executive Counsel + Intervention",
))
STATE_PROFILES["narrative_lock"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.35,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="groundhog_day",
    state_name="Groundhog Day",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Strategic", "Financial & Economic", "Cultural & Behavioral"],
    asset_axes=["Adaptive Capacity", "Governance Discipline"],
    sev_min="Entrenched", sev_max="Endemic",
    # Inferred from profiles doc: Learning Architecture Failure
    resolution_family="Roadmap + Executive Counsel",
))
STATE_PROFILES["groundhog_day"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_wrong_reward",
    state_name="The Wrong Reward",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Operational & Structural", "Talent & Retention"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Entrenched", sev_max="Endemic",
    # Inferred from profiles doc: Motivational Architecture Failure
    resolution_family="Intervention + Roadmap",
))
STATE_PROFILES["the_wrong_reward"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_unreported_hazard",
    state_name="The Unreported Hazard",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id=None,
    liability_axes=["Safety & Wellbeing", "Legal & Compliance", "Cultural & Behavioral"],
    asset_axes=["Relational Trust", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Safety Culture Deficit
    resolution_family="Intervention",
))
STATE_PROFILES["the_unreported_hazard"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.35,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_unlocked_door",
    state_name="The Unlocked Door",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id=None,
    liability_axes=["Safety & Wellbeing", "Legal & Compliance", "Financial & Economic"],
    asset_axes=["Cultural Stewardship", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Security Culture Gap
    resolution_family="Development + Intervention",
))
STATE_PROFILES["the_unlocked_door"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.35,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="the_broken_compass",
    state_name="The Broken Compass",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Strategic", "Cultural & Behavioral", "Financial & Economic"],
    asset_axes=["Strategic Execution Capacity"],
    sev_min="Entrenched", sev_max="Entrenched",  # Fixed tier
    # Inferred from profiles doc: Implementation Courage Deficit
    resolution_family="Executive Counsel",
))
STATE_PROFILES["the_broken_compass"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)


# ── Cluster registries ─────────────────────────────────────────────────────────

CLUSTERS: dict[str, list[str]] = {
    "C-Manager": [
        "the_unformed_leader",
        "the_overloaded_manager",
        "the_dormant_talent",
    ],
    "C-Culture": [
        "culture_drift",
        "identity_erosion",
        "the_culture_that_wasnt",
    ],
}

_reg(_profile(
    state_id="wellbeing_theater",
    state_name="Wellbeing Theater",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id="C-Culture",
    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Financial & Economic"],
    asset_axes=["Cultural Stewardship", "People Development Capability"],
    sev_min="Emerging", sev_max="Entrenched",
    # CONFIRMED — Gemini review complete (round two, Session 68). E6
    # (consolidation-mapping-trace.md Batch F). Source text self-describes as "a
    # specific variant of Culture Drift"; Gemini's review rejected C-Culture cluster
    # membership specifically (kept cluster_id/signal_weight as drafted, but this
    # state does NOT belong in CLUSTERS["C-Culture"] -- removed below). Also
    # confirmed: resolution_family (4-bucket, engine/resolution_families.py) is
    # "structural", not the "directional" drafted in Session 67.
    resolution_family="Intervention",
))
STATE_PROFILES["wellbeing_theater"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.25,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.35,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="human_displacement_anxiety",
    state_name="Human Displacement Anxiety",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Talent & Retention", "Cultural & Behavioral", "Strategic"],
    asset_axes=["Adaptive Capacity", "People Development Capability"],
    sev_min="Emerging", sev_max="Entrenched",
    # CONFIRMED — Gemini review complete (round two, Session 68). E6
    # (consolidation-mapping-trace.md Batch D). Revised from the Session 67 draft:
    # resolution_family (4-bucket, engine/resolution_families.py) is "structural",
    # not "directional"; taxonomy.ts signatureId is "culture_erosion", not
    # "stunted_growth".
    resolution_family="Development + Intervention",
))
STATE_PROFILES["human_displacement_anxiety"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="motivational_architecture_failure",
    state_name="Motivational Architecture Failure",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Operational & Structural"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Entrenched", sev_max="Endemic",
    # CONFIRMED — Gemini review complete (round two, Session 68). E7
    # (consolidation-mapping-trace.md Batch D). No changes from the Session 67 draft
    # to signal_weight/severity/axes/resolution_family/dimensional_vector.
    # NAMING COLLISION (found during implementation, not in Session 65's mitigation
    # list): "Motivational Architecture Failure" is also the profiles-doc inferred-
    # mapping source name for the LOCKED state the_wrong_reward (see NOTE — NAME
    # MAPPING above, and the_wrong_reward's own "Inferred from profiles doc" comment
    # below). Confirmed distinct per trace: clinical controlled/amotivated workforce
    # condition via reward-system failure (this state), vs. The Wrong Reward's rational
    # strategic optimization for the real, unstated incentive system. RESOLUTION
    # (Pete's call, Session 68): keep this state_id and external label as-is -- do
    # NOT rename to "systemic_amotivation" or any variant Gemini's review floated.
    # Collision resolved via inline documentation cross-reference only, same pattern
    # as Sequential Decision Blindness vs. Decision Blindness above.
    resolution_family="Intervention + Roadmap",
))
STATE_PROFILES["motivational_architecture_failure"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)

_reg(_profile(
    state_id="cultural_overtime",
    state_name="Cultural Overtime",
    primary_dimension="Attitude",
    signal_weight="medium",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Financial & Economic", "Cultural & Behavioral"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Emerging", sev_max="Entrenched",
    # CONFIRMED — Gemini review complete (round two, Session 68). E2 #08
    # (consolidation-mapping-trace.md Batch C). No changes from the Session 67 draft.
    resolution_family="Intervention + Roadmap",
))
STATE_PROFILES["cultural_overtime"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.45,
    attitude_asset=0.15,
)
