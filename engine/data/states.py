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
    descriptive_prose:  str = ""             # Static per-state prose, authored separately (Tier 4)


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
STATE_PROFILES["the_unformed_leader"].descriptive_prose = "A manager occupies the role without having been equipped for it. Direction is inconsistent, feedback arrives late or not at all, and the team absorbs the gap by lowering its own expectations. Turnover concentrates among the people who had other options."

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
STATE_PROFILES["the_overloaded_manager"].descriptive_prose = "A manager who was competent for the original scope of the role is now carrying more than the role was designed to hold. Development conversations have been replaced by status updates, and decisions queue behind everything else competing for the same attention. The organization redesigned the job without redesigning the resources around it."

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
STATE_PROFILES["the_dormant_talent"].descriptive_prose = "The manager can name precisely what each person needs to grow and consistently doesn't act on it. Development stalls while the manager's own visibility and standing continue to rise. The people with the clearest read on the gap are also the ones most able to leave."

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
STATE_PROFILES["built_to_fail"].descriptive_prose = "The role's scope exceeds what any reasonable allocation of resources could support, and each person who holds it is told to make it work rather than given what making it work would require. The organization treats each departure as an individual hiring failure rather than a structural one. The next person inherits the same impossible math."

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
STATE_PROFILES["the_undefined_role"].descriptive_prose = "The role's actual boundaries were never defined, so what lands on the desk, what gets escalated, and what falls through are all matters of local negotiation rather than design. Work duplicates in some places and goes unclaimed in others. The organization is paying for a function that isn't reliably producing what anyone assumes it produces."

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
    # SCD-WCS full re-authoring, Phase 2 Batch 1 (2026-08-24), staged
    # Phase 5 (2026-08-25) -- prompts/scd-wcs-full-reauthoring-
    # program.md. Full re-authoring, independent of built_to_fail for
    # the first time -- this state's own text ("written record no
    # longer matches what everyone privately knows", "documented
    # cause", "managing one employee on paper and a different one in
    # practice") is Authority-primary/Attitude-secondary, not the
    # Aptitude-primary shape inherited wholesale from built_to_fail.
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.35,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.25,
    attitude_asset=0.15,
)
STATE_PROFILES["the_paper_tiger"].descriptive_prose = "A performance problem has been managed verbally for long enough that the written record no longer matches what everyone privately knows. When the organization finally needs to act on documented cause, it discovers it has been managing one employee on paper and a different one in practice. The gap surfaces in front of the people with the least patience for it."


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
    # SCD-WCS full re-authoring, Phase 2 Batch 1 (2026-08-24), staged
    # Phase 5 (2026-08-25) -- prompts/scd-wcs-full-reauthoring-
    # program.md. Full axis flip, supersedes Candidate C: real text
    # ("a manager's read... is accurate... a sound judgment") directly
    # disclaims Aptitude as the liability -- the entire deficiency
    # described is evidentiary/documentation weight (Authority).
    # Dry-run confirmed clean (Phase 4c): false-rank-1 43 -> 0/175,
    # zero new collision against the_founders_grip.
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.60,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)
STATE_PROFILES["invisible_performance_management"].descriptive_prose = "A manager's read on an underperforming employee is accurate but was never written down, so it carries no evidentiary weight when a decision needs defending. This isn't concealment. It's an absence of documentation that turns a sound judgment into an exposed one."


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
STATE_PROFILES["the_founders_grip"].descriptive_prose = "One person's approval gates nearly every consequential decision, and that person is stretched too thin to make those calls on current information. Work either waits in queue or routes around the bottleneck entirely. The senior people who could tolerate neither option have already left."

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
STATE_PROFILES["the_exposed"].descriptive_prose = "There is no function in the organization whose job it actually is to manage employee-related risk. Concerns have nowhere reliable to land, and obligations accumulate without anyone tracking them. The organization isn't between HR leaders. It's accumulating liability on a clock nobody is watching."

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
STATE_PROFILES["the_uninitiated"].descriptive_prose = "A significant organizational event is underway, and the people leading it have never done this before. They are capable in general and unprepared for this specific kind of decision, which means the costliest mistakes are the ones nobody on the team knows to watch for."

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
STATE_PROFILES["leadership_continuity_risk"].descriptive_prose = "Authority concentrated in a small number of people has no defined path to anyone else if one of them leaves. The organization can name who is critical but not who would replace them or how. That gap becomes a crisis the moment it stops being theoretical."

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
STATE_PROFILES["hr_capture"].descriptive_prose = "The function responsible for protecting the organization and its people has been repurposed to protect specific leaders instead. Complaints against the powerful get managed differently than complaints against everyone else, and the people making that distinction know exactly what they're doing."

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
STATE_PROFILES["decision_paralysis"].descriptive_prose = "Decisions that should move at operational speed are instead stalling in a governance structure that was never built to render verdicts quickly. Nobody is refusing to decide. The structure itself doesn't produce clear ownership of the call."

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
STATE_PROFILES["the_policy_lag"].descriptive_prose = "The organization's written policies describe an operating reality that no longer exists. Practice has moved on without the documentation catching up, so the rules on paper and the rules people actually follow have quietly diverged."

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
    # Candidate C, SHIPPED 2026-08-23 (prompts/scd-wcs-remediation-
    # tracker.md) -- aptitude_liability 0.35 -> 0.30. The one
    # genuinely double-field-grounded collision found in the whole
    # invisible_performance_management investigation: this state's
    # own text names both an unverified-capability problem (aptitude)
    # AND an explicit "no governance layer reviewing" decision-rights
    # gap (authority) -- real signal on both sides, not a forced
    # same-cluster tie-break. Reduces false-rank-1 against
    # invisible_performance_management's own profiles (9->5/175).
    authority_liability=0.50,
    aptitude_liability=0.30,
    authority_asset=0.10,
    aptitude_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.10,
    attitude_asset=0.10,
)
STATE_PROFILES["the_unexamined_algorithm"].descriptive_prose = "An automated or algorithmic system is making or materially influencing consequential decisions with no governance layer reviewing what it's actually doing. Nobody owns auditing its outputs for bias, error, or drift. The organization finds out something was wrong only after it's been wrong for a while."


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
STATE_PROFILES["heard_and_ignored"].descriptive_prose = "Concerns are being raised through the organization's own channels and are reliably not acted on. The reporting mechanism exists and functions as a formality, not a corrective one. People stop using it once they've tested it enough times to know what happens when they do."

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
STATE_PROFILES["the_tolerated_violation"].descriptive_prose = "A known violation of policy, law, or basic standard has been allowed to continue long enough that it now reads as normal rather than exceptional. Everyone involved can describe the violation accurately. Nobody with the authority to stop it has been willing to be the one who does."

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
STATE_PROFILES["dueling_narratives"].descriptive_prose = "Different parts of the organization are telling meaningfully different versions of the same set of facts, and nobody has reconciled them into one account. Each version is defensible in isolation. Together they create exposure the moment anyone outside the organization compares notes."

_reg(_profile(
    state_id="the_unsolved_problem",
    state_name="The Unsolved Problem",
    # SCD-WCS re-clustering (this session, Program Phase 4): was
    # "Authority" -- confirmed mis-clustered. Full descriptive_prose
    # carries zero decision-rights/accountability content anywhere --
    # a pure root-cause-solving-capability story ("each fix treats
    # the most recent symptom rather than whatever keeps
    # regenerating it"). resolution_family "Roadmap" was already
    # this cluster's only outlier (its 7 siblings share "Intervention
    # + Executive Counsel" uniformly) -- independent corroborating
    # evidence, "Roadmap"/"Development" correlate with 6 of 7
    # existing Aptitude-dominant states. See
    # prompts/scd-wcs-remediation-tracker.md for the full text
    # analysis, precedent check, and 9-candidate vector search.
    primary_dimension="Aptitude",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Financial & Economic", "Cultural & Behavioral"],
    asset_axes=["Adaptive Capacity", "Governance Discipline"],
    sev_min="Entrenched", sev_max="Entrenched",  # Fixed tier
    # Inferred from profiles doc: Recidivism Risk
    resolution_family="Intervention + Roadmap",
))
STATE_PROFILES["the_unsolved_problem"].dimensional_vector = DimensionalVector(
    # Re-vectored (this session): aptitude=0.50/0.15 asymmetric,
    # matching every other Aptitude-dominant state's liability>asset
    # pattern. Authority/alliance/attitude all dropped to flat 0.15
    # -- the real text carries zero secondary-axis content on any of
    # the three. 0.50 is the smallest magnitude confirmed safe by a
    # 9-candidate search against the real calibration pipeline:
    # below it (0.35/0.40), the_unsolved_problem newly threatens
    # the_untouchable's already-marginal profile; at 0.45 it
    # collides exactly with paper_shield's vector; at 0.50 and above
    # the full 171/175 baseline holds with zero new failures
    # anywhere. Confirmed not byte-identical to any existing state's
    # vector.
    #
    # SCD-WCS Phase 8 mitigation (later same session): this
    # re-clustering manufactured a 19/175 false-rank-1 footprint
    # that measured 0/175 before it (see
    # prompts/scd-wcs-remediation-tracker.md). No secondary axis
    # exists in the text -- fresh re-read confirmed genuinely
    # single-axis-pure. aptitude_asset raised 0.15 -> 0.20
    # (liability held at 0.50, reducing the skew from 3.33:1 to
    # 2.5:1) instead. Lowering it further was tested and
    # backfires catastrophically (0.10 -> 100/175, 0.05 -> 123/175
    # plus a new regression failure) -- raising it is the correct
    # direction. Margin-searched (0.16-0.25, full 175-profile
    # suite): 0.20 is the smallest value where the binding
    # near-miss constraint stabilizes on one profile with a
    # margin ~7x the razor-thin low end, zero regression cost,
    # zero vector collision with any other state.
    aptitude_liability=0.50,
    aptitude_asset=0.20,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)
STATE_PROFILES["the_unsolved_problem"].descriptive_prose = "A specific problem has been addressed before, more than once, and keeps returning in close to the same form. Each fix treats the most recent symptom rather than whatever keeps regenerating it. The organization is paying repeatedly for a resolution that has never actually resolved anything."

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
STATE_PROFILES["transition_paralysis"].descriptive_prose = "An organizational transition has started and then stalled somewhere in the middle, with the old structure partly dismantled and the new one not yet functional. People are operating in the gap, uncertain which authority actually governs their work day to day."

_reg(_profile(
    state_id="paper_shield",
    state_name="Paper Shield",
    # SCD-WCS re-clustering (this session): was "Authority" --
    # confirmed mis-clustered. Full descriptive_prose carries zero
    # decision-rights/accountability content anywhere -- a pure
    # capability-verification story ("never been tested against
    # anything real... the gap between documented readiness and
    # actual readiness"). See
    # prompts/scd-wcs-remediation-tracker.md for the full text
    # analysis, precedent comparison, and 12-candidate vector search.
    primary_dimension="Aptitude",
    signal_weight="low",
    cluster_id=None,
    liability_axes=["Governance & Authority", "Operational & Structural", "Financial & Economic"],
    asset_axes=["Adaptive Capacity", "Governance Discipline"],
    sev_min="Emerging", sev_max="Entrenched",
    # Inferred from profiles doc: Resilience Architecture Gap
    resolution_family="Roadmap",
))
STATE_PROFILES["paper_shield"].dimensional_vector = DimensionalVector(
    # Re-vectored (this session): aptitude=0.45/0.15 asymmetric,
    # matching every other Aptitude-dominant state's liability>asset
    # pattern (the_unformed_leader 0.35/0.15, built_to_fail 0.60/0.10,
    # invisible_performance_management 0.45/0.15). Authority/alliance/
    # attitude all dropped to flat 0.15 -- the real text carries zero
    # secondary-axis content on any of the three. 0.45 is the smallest
    # magnitude confirmed safe by a 12-candidate search against the
    # real calibration pipeline: below it, paper_shield newly
    # out-competes the_untouchable on one of its own already-marginal
    # profiles; at 0.45 and above, the full 171/175 baseline holds
    # with zero new failures anywhere. Confirmed not byte-identical
    # to any existing state's vector.
    aptitude_liability=0.45,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.15,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)
STATE_PROFILES["paper_shield"].descriptive_prose = "Contingency and continuity plans exist in writing and have never been tested against anything real. The organization believes it is prepared because the documentation says so. The gap between documented readiness and actual readiness surfaces exactly once, at the worst time to discover it."

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
STATE_PROFILES["the_lost_map"].descriptive_prose = "Institutional knowledge lives in individual heads rather than in any system the organization actually maintains. When someone leaves, whatever they knew leaves with them, and the organization relearns it the expensive way."

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
STATE_PROFILES["invisible_influence_architecture"].descriptive_prose = "Real influence over decisions runs through informal channels that don't match the org chart anyone would draw. The formally accountable people are not always the ones actually deciding outcomes. New arrivals spend real time discovering who actually has to say yes."

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
STATE_PROFILES["pay_exposure"].descriptive_prose = "Compensation has drifted out of alignment with what the market is currently paying for comparable roles, and the organization is discovering this reactively, through departures, rather than proactively. Each departure it triggers is a preventable one."

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
STATE_PROFILES["the_pay_fog"].descriptive_prose = "Pay decisions across the organization don't follow a consistent, defensible logic, even though each individual decision might have made sense in the moment it was made. That inconsistency is hard to see from inside any one decision and impossible to miss once someone lines them all up."


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
STATE_PROFILES["compression_crisis"].descriptive_prose = "Layers of management have been compressed or eliminated faster than the remaining structure can absorb the load, concentrating decision-making into fewer people than the work actually requires. What looks like efficiency on an org chart is strain everywhere it actually gets executed."

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
STATE_PROFILES["sequential_decision_blindness"].descriptive_prose = "A series of individually defensible decisions, made by different people without coordination, adds up to a pattern that looks like retaliation or targeting when viewed together. No single decision-maker intended that outcome. The exposure exists in the aggregate, not in any one decision anyone can point to."

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
STATE_PROFILES["disparate_impact_architecture"].descriptive_prose = "A policy or practice applies the same rule to everyone and produces meaningfully different outcomes across different groups, in a pattern that would be recognizable to anyone who looked at the aggregate data. Neutral intent doesn't change what the data shows."

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
STATE_PROFILES["planning_authority_gap"].descriptive_prose = "The people responsible for planning don't hold the authority to make the decisions their plans depend on, and the people who hold that authority aren't the ones doing the planning. Plans get built and then wait for approval from someone who wasn't part of building them."


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
STATE_PROFILES["the_fracture"].descriptive_prose = "A working relationship between two people, teams, or functions that the organization depends on has broken down past the point of informal repair. Work still moves, but it moves around the fracture rather than through it."

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
    # SCD-WCS full re-authoring, Phase 2 Batch 2 (2026-08-24), staged
    # Phase 5 (2026-08-25) -- prompts/scd-wcs-full-reauthoring-
    # program.md. Deliberate budget expansion (0.90 -> 1.05), this
    # program's first: within-budget redistribution (SC-2, the
    # original 3-state search) already tested insufficient. Aptitude
    # secondary grounded in "whatever the first fix addressed, it
    # wasn't the actual cause" -- a real diagnostic-failure claim, not
    # incidental undertone. Alliance concentration raised toward (not
    # to) built_to_fail's own HIGH-tier magnitude, reflecting this
    # state's genuine dual-axis shape.
    aptitude_liability=0.20,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.55,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)
STATE_PROFILES["the_second_close"].descriptive_prose = "A relationship or agreement was renegotiated once already, and the same underlying issue that forced the first renegotiation is resurfacing. Whatever the first fix addressed, it wasn't the actual cause. The people involved are less willing to extend trust a second time."

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
    # SCD-WCS full re-authoring, Phase 2 Batch 2 (2026-08-24), staged
    # Phase 5 (2026-08-25) -- prompts/scd-wcs-full-reauthoring-
    # program.md. Ends the mechanical tier-template tie with
    # the_second_close/the_arbitrary_standard (origin: commit 253b345,
    # a global metadata-keyed tier pass, not a content decision -- see
    # prompts/scd-wcs-silosolation-arbitrary-standard-origin-
    # investigation.md). Vector now catches up to the salience, which
    # already correctly identified Authority as real ("isn't hostile.
    # It's structural").
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.25,
    authority_asset=0.15,
    alliance_liability=0.35,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)
STATE_PROFILES["silosolation"].descriptive_prose = "Teams that need each other's information to do their jobs well are operating as if they don't, each optimizing for its own metrics without visibility into how that affects anyone else. The isolation isn't hostile. It's structural, and it produces the same friction hostility would."

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
STATE_PROFILES["the_suppression_filter"].descriptive_prose = "Bad news gets filtered, softened, or dropped entirely as it moves up through the organization's layers, so the people with authority to act on it are consistently the last to hear an accurate version. Each layer believes it's protecting leadership from noise."

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
    # SCD-WCS full re-authoring, Phase 2 Batch 2 (2026-08-24), staged
    # Phase 5 (2026-08-25) -- prompts/scd-wcs-full-reauthoring-
    # program.md. Genuine axis flip, mirrors silosolation on the same
    # two axes with primacy reversed: this state's text is Authority-
    # centered ("rules that govern", "before anyone in leadership
    # does"), corroborated independently by its own asset_axes
    # ("Accountability Architecture", not "Relational Trust") carried
    # unchanged since the very first commit. Ends the mechanical tier-
    # template tie -- see silosolation's block above and
    # prompts/scd-wcs-silosolation-arbitrary-standard-origin-
    # investigation.md.
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.35,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.15,
    attitude_asset=0.15,
)
STATE_PROFILES["the_arbitrary_standard"].descriptive_prose = "The rules that govern who gets what treatment aren't applied consistently, and the pattern of who benefits isn't accidental even if nobody designed it on purpose. People notice the inconsistency well before anyone in leadership does."

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
STATE_PROFILES["decision_blindness"].descriptive_prose = "A single significant decision was made without input from the people who held the information that would have changed it. The decision-maker wasn't negligent. The information simply never reached them, because nobody's job was making sure it did."


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
STATE_PROFILES["distributed_culture_fragmentation"].descriptive_prose = "Teams operating in different locations, functions, or time zones have developed genuinely different norms for how work gets done, and nobody has reconciled them into one coherent culture. The friction shows up exactly at the seams where the teams have to work together."


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
STATE_PROFILES["the_untouchable"].descriptive_prose = "One person's results or position have made them functionally exempt from the standards everyone else is held to. Everyone around them can name the exemption specifically. The cost isn't just what that person does. It's what everyone watching learns about what the organization actually values."

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
STATE_PROFILES["what_nobody_says"].descriptive_prose = "There is a specific, known problem that people in the organization can describe accurately in private and will not raise anywhere it might reach someone with the authority to fix it. The silence isn't accidental. It's a rational response to what happened, or is believed to happen, to the last person who spoke up."

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
STATE_PROFILES["leadership_deafness"].descriptive_prose = "Leadership is operating on a version of organizational reality that the people below them stopped believing months or years ago. The gap isn't intentional deception so much as an accumulated pattern of information getting softened on its way up."

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
STATE_PROFILES["the_diversity_ceiling"].descriptive_prose = "The organization's stated commitment to diversity and inclusion is visible in messaging and invisible in outcomes. Representation doesn't advance past a specific point in the hierarchy no matter how the numbers look at entry level. People below that ceiling can see exactly where it sits."

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
STATE_PROFILES["culture_drift"].descriptive_prose = "The organization's stated values and its actual day-to-day behavior have drifted apart gradually enough that no single moment marks the change. Nobody decided to abandon the values. They just stopped being what got rewarded."

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
STATE_PROFILES["identity_erosion"].descriptive_prose = "The organization has lost a clear, shared answer to what it actually is and what makes it different from anywhere else someone could work. That uncertainty shows up first in retention and recruiting, before it shows up anywhere leadership is looking."

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
STATE_PROFILES["the_culture_that_wasnt"].descriptive_prose = "What was described during hiring and what actually exists inside the organization are two different cultures, and new hires discover the gap almost immediately. The mismatch is sharpest and most damaging in the first few months, before anyone has built enough tenure to rationalize it."

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
STATE_PROFILES["the_burned_credibility"].descriptive_prose = "Leadership has announced significant changes before and either didn't follow through or followed through badly enough that people stopped believing the announcements. The next initiative, however well designed, inherits the skepticism earned by the last one."

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
STATE_PROFILES["invisible_burnout"].descriptive_prose = "People are burning out while their output looks fine, which means the organization's usual signals for catching the problem aren't catching it. The cost surfaces later, all at once, as a resignation or a mistake that looks sudden but wasn't."

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
STATE_PROFILES["the_basement_standard"].descriptive_prose = "A standard of performance well below what the organization would say it expects has become the accepted baseline, because nobody has been willing to enforce the standard that's actually on paper. The best performers notice the gap first, and leave."

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
STATE_PROFILES["the_inside_track"].descriptive_prose = "Advancement and opportunity flow disproportionately to a specific, identifiable group through channels that aren't the organization's stated process. Everyone outside that group can name it, usually specifically."

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
STATE_PROFILES["narrative_lock"].descriptive_prose = "The organization keeps telling itself and its people a story about who it is that stopped being accurate some time ago, and it can't update that story even when the facts on the ground contradict it. Anyone who challenges the story is treated as the problem rather than the messenger."

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
STATE_PROFILES["groundhog_day"].descriptive_prose = "The same class of mistake recurs across projects, teams, or cycles, and the organization has no mechanism for capturing what it learned the last time so it doesn't happen again. Each recurrence gets treated as a new problem rather than a repeat of an old one."

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
STATE_PROFILES["the_wrong_reward"].descriptive_prose = "The organization is getting exactly the behavior its incentive structure actually rewards, and that behavior is not the one leadership says it wants. People are responding rationally to the real incentives, not the stated ones."

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
STATE_PROFILES["the_unreported_hazard"].descriptive_prose = "Real safety concerns exist and are not reliably making it into the organization's reporting system, for reasons that have more to do with culture than process. People have learned that reporting doesn't change much and might cost them something personally."

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
STATE_PROFILES["the_unlocked_door"].descriptive_prose = "Security or safety practices that were adequate for an earlier version of the organization haven't kept pace with how the organization actually operates now. Nobody decided to leave the door open. It's simply never been revisited."

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
STATE_PROFILES["the_broken_compass"].descriptive_prose = "The organization can articulate the right strategic direction clearly and consistently fails to actually move in it when the moment requires a hard call. The gap isn't a knowledge problem. It's a courage problem, and it shows up at exactly the moments that matter most."


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
STATE_PROFILES["wellbeing_theater"].descriptive_prose = "The organization has visible wellbeing programming that isn't changing the underlying conditions actually driving people's stress and dissatisfaction. The initiatives address the symptom the organization is comfortable addressing rather than the cause it would rather not name."

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
STATE_PROFILES["human_displacement_anxiety"].descriptive_prose = "People across the organization are anxious about being displaced by automation or AI, and that anxiety is affecting engagement and decision-making whether or not the organization has any actual plans in that direction. Silence from leadership doesn't read as reassurance. It reads as confirmation."

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
STATE_PROFILES["motivational_architecture_failure"].descriptive_prose = "The organization's reward system has stopped functioning as a source of motivation at all, for enough of the workforce that engagement has flattened across the board rather than in any one identifiable group. People haven't misread the incentives. They've stopped believing the incentives connect to anything real."

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
STATE_PROFILES["cultural_overtime"].descriptive_prose = "Extended hours have become an unstated cultural expectation rather than an occasional operational necessity, and the organization is carrying real legal and financial exposure from that norm without having decided, on paper, that it wants to run this way."

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  ATTITUDE  (MC_CENTROID_39 recalibration, Step 1 -- 58th state)            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

_reg(_profile(
    state_id="the_inner_circle",
    state_name="The Inner Circle",
    primary_dimension="Attitude",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Governance & Authority"],
    asset_axes=["Accountability Architecture", "Governance Discipline"],
    sev_min="Emerging", sev_max="Endemic",
    resolution_family="Intervention + Executive Counsel",
))
STATE_PROFILES["the_inner_circle"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.10,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.60,
    attitude_asset=0.10,
)
STATE_PROFILES["the_inner_circle"].descriptive_prose = "There's a group at the top of this organization who look out for each other first. Decisions get made in rooms you're not in, by people who protect each other's mistakes as readily as their own. It isn't about one person getting away with something — it's a whole layer that answers to itself instead of any standard. The people outside the circle have figured out exactly what that means for them."
