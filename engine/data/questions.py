"""
PRV3 Scoring Engine — Section I.2
Question Library Schema and Registry

Defines the schema for all question objects in the diagnostic sequence.
The registry is empty at this stage — question content is a separate deliverable.
Questions will be added as Q01–Q34 core, SEVER-01 through SEVER-12 severity
follow-ons, and DIST-[cluster]-## distinguisher questions are written and confirmed.

Spec reference: Section I.2
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Answer option ──────────────────────────────────────────────────────────────

@dataclass
class AnswerOption:
    """
    One selectable option within a question.

    dimensional_contributions maps each of the eight dimensional fields to a float.
    Positive values add weight in that axis direction.
    These values are defined per option in the question library — they are
    not derivable from question text and must be set by the question designers.

    Spec reference: Section I.2 answer_vectors
    """
    option_id:   str   # e.g. "A", "B", "C" or "1", "2", "3"
    option_text: str

    dimensional_contributions: dict = field(default_factory=lambda: {
        "aptitude_liability":   0.0,
        "aptitude_asset":       0.0,
        "authority_liability":  0.0,
        "authority_asset":      0.0,
        "alliance_liability":   0.0,
        "alliance_asset":       0.0,
        "attitude_liability":   0.0,
        "attitude_asset":       0.0,
    })

    axis_targets:          list            = field(default_factory=list)
    # Tags routing intake axis modifiers (Section I.3.2) to this answer.
    # Examples: "Safety & Wellbeing", "authority_liability", "compensation_authority"

    severity_trigger:      bool            = False
    severity_follow_on_id: Optional[str]   = None  # e.g. "SEVER-03"


# ── Question definition ────────────────────────────────────────────────────────

@dataclass
class QuestionDefinition:
    """
    Complete definition of one diagnostic question.

    question_id formats:
      Q01–Q34          Core sequence
      SEVER-01 to -12  Conditional severity follow-ons
      DIST-CM-##       C-Manager distinguisher questions
      DIST-CC-##       C-Culture distinguisher questions
      DIST-CS-##       C-Silence distinguisher questions
      DIST-CI-##       C-InfoFlow distinguisher questions

    Spec reference: Section I.2
    """
    question_id:         str
    question_text:       str
    format:              str            # forced_choice | weighted_multi_select | likert
    sequence_position:   Optional[int]  # int for Q01–Q34; None for conditional questions
    checkpoint_segment:  str            # early | mid | late | conditional

    answer_options: list = field(default_factory=list)  # list[AnswerOption]

    state_targets:   list = field(default_factory=list)  # list of state_ids
    severity_trigger: bool = False


# ── Question registry ──────────────────────────────────────────────────────────

# Empty at this stage. Questions are a separate deliverable.
# Keys are question_id strings. Values are QuestionDefinition objects.
QUESTION_LIBRARY: dict[str, QuestionDefinition] = {}


# ── Expected question ID patterns (for validation) ────────────────────────────

CORE_SEQUENCE_IDS    = [f"Q{i:02d}" for i in range(1, 35)]   # Q01–Q34
SEVERITY_FOLLOW_ON_IDS = [f"SEVER-{i:02d}" for i in range(1, 13)]  # SEVER-01–SEVER-12

DISTINGUISHER_CLUSTER_PREFIXES = {
    "C-Manager":  "DIST-CM",
    "C-Culture":  "DIST-CC",
    "C-Silence":  "DIST-CS",
    "C-InfoFlow": "DIST-CI",
}

CHECKPOINT_SEGMENTS = {
    "early":       range(1, 12),   # Q01–Q11
    "mid":         range(12, 20),  # Q12–Q19
    "late":        range(20, 35),  # Q20–Q34
    "conditional": None,           # severity follow-ons and distinguisher questions
}
