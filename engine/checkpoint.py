"""
PRV3 Scoring Engine — Section III
Checkpoint and Branching Logic

III.1  Shannon Entropy Calculation
III.2  Checkpoint Logic and Distinguisher Question Routing
III.3  Narrative Prompt Trigger Conditions and Generation Parameters

Three checkpoints operate at Q11, Q19, Q27. At each checkpoint the engine
calculates Shannon Entropy on the normalized score distribution. If entropy
exceeds the threshold, the engine routes to distinguisher questions (Q11, Q19)
or fires the narrative prompt early (Q27).

Spec reference: PRV3_Scoring_Architecture_Spec_v1.docx, Section III
"""

from dataclasses import dataclass, field
from math import log2
from typing import Optional

from engine.data.states import CLUSTERS, STATE_PROFILES
from engine.data.questions import (
    QUESTION_LIBRARY, DISTINGUISHER_CLUSTER_PREFIXES,
)
from engine.accumulation import StateRanking


# ── III.1  Shannon Entropy ─────────────────────────────────────────────────────

# Maximum entropy: uniform distribution across all 47 states
# Spec references 45 states (documentation artifact); confirmed count is 47.
MAX_ENTROPY: float = log2(len(STATE_PROFILES))  # ≈ 5.554 bits

# Checkpoint entropy thresholds — CALIBRATION TARGET
# Starting hypotheses from spec III.1. Adjust based on Phase 1 false-positive
# rate and narrative prompt trigger frequency.
THRESHOLD_Q11: float = 0.6  # CALIBRATION TARGET — cluster direction gate
THRESHOLD_Q19: float = 0.4  # CALIBRATION TARGET — state family resolution gate
THRESHOLD_Q27: float = 0.2  # CALIBRATION TARGET — verdict gate

# Maximum distinguisher questions per checkpoint activation — LOCKED
MAX_DISTINGUISHERS_PER_CHECKPOINT: int = 2

CHECKPOINT_POSITIONS = ("Q11", "Q19", "Q27")
CHECKPOINT_THRESHOLDS = {
    "Q11": THRESHOLD_Q11,
    "Q19": THRESHOLD_Q19,
    "Q27": THRESHOLD_Q27,
}


def scores_to_probabilities(rankings: list) -> dict:
    """
    Convert a ranked state list's similarity scores to a probability distribution
    by normalizing scores to sum 1.0.

    p(s) = score(s) / sum_of_all_scores

    Spec reference: Section III.1 — "p(s) is derived from the state score
    distribution — convert similarity scores to probabilities by normalizing
    to sum to 1.0"
    """
    total = sum(r.score for r in rankings)
    if total == 0.0:
        n = len(rankings)
        return {r.state_id: 1.0 / n for r in rankings}
    return {r.state_id: r.score / total for r in rankings}


def compute_entropy(probabilities: dict) -> float:
    """
    Shannon Entropy of a state probability distribution.

    H = -sum( p(s) * log2(p(s)) ) for all s where p(s) > 0

    Returns entropy in bits. Range: [0, log2(n_states)].
    Lower entropy = higher diagnostic concentration = greater confidence.

    Spec reference: Section III.1
    """
    h = 0.0
    for p in probabilities.values():
        if p > 0.0:
            h -= p * log2(p)
    return h


# ── III.2  Checkpoint Logic and Distinguisher Question Routing ─────────────────

def top_cluster_by_score(rankings: list) -> Optional[str]:
    """
    Identify which named cluster (C-Manager, C-Culture, C-Silence, C-InfoFlow)
    carries the most signal in the current distribution.

    Aggregate method: sum similarity scores for each cluster's member states.
    Returns the cluster_id with the highest aggregate score.
    Returns None if all clusters have zero score.

    Used at Q11 checkpoint to select the distinguisher question pool.

    Spec reference: Section III.2 — "Engine identifies which dimension cluster
    carries the most signal"
    """
    score_by_id = {r.state_id: r.score for r in rankings}
    cluster_scores = {}
    for cluster_id, member_ids in CLUSTERS.items():
        cluster_scores[cluster_id] = sum(
            score_by_id.get(sid, 0.0) for sid in member_ids
        )

    best_cluster = max(cluster_scores, key=lambda c: cluster_scores[c])
    if cluster_scores[best_cluster] == 0.0:
        return None
    return best_cluster


def select_distinguisher_questions(
    cluster_id: str,
    already_asked: list,
    max_questions: int = MAX_DISTINGUISHERS_PER_CHECKPOINT,
) -> list:
    """
    Select up to max_questions distinguisher questions for the given cluster
    from the question library, excluding any already asked this session.

    Question IDs follow DIST-[prefix]-## pattern (e.g. DIST-CM-01).
    Pool prefix per cluster: DISTINGUISHER_CLUSTER_PREFIXES.

    Returns a list of QuestionDefinition objects (empty if library not yet
    populated or pool exhausted).

    Spec reference: Section III.2 — "Questions tagged DIST-[cluster]-##"
    Max 2 per checkpoint activation — LOCKED.
    """
    prefix = DISTINGUISHER_CLUSTER_PREFIXES.get(cluster_id)
    if prefix is None:
        return []

    pool = [
        q for qid, q in QUESTION_LIBRARY.items()
        if qid.startswith(prefix) and qid not in already_asked
    ]
    # Select closest-match questions first — when question_library has targeting
    # metadata, sort by relevance to current top states. At this build stage
    # the library is empty; ordering deferred to question-writing phase.
    return pool[:max_questions]


@dataclass
class CheckpointResult:
    """
    Result of evaluating one checkpoint against the current state distribution.

    fires:             True if entropy > threshold OR cluster override fires.
    top_cluster:       Dominant named cluster (populated at Q11 and Q19; None at Q27).
    distinguishers:    Questions selected for firing (empty list if none available).
    narrative_trigger: True if this checkpoint fires the early narrative prompt (Q27 only).
    trigger_path:      "entropy" | "cluster_override" | "none"

    Spec reference: Section III.2 and III.3
    """
    checkpoint:        str             # "Q11" | "Q19" | "Q27"
    entropy:           float           # computed Shannon Entropy in bits
    threshold:         float           # threshold applied at this checkpoint
    fires:             bool            # entropy > threshold OR cluster override
    top_cluster:       Optional[str]   # dominant cluster, or None
    distinguishers:    list            # list of QuestionDefinition
    narrative_trigger: bool            # III.3 early trigger
    trigger_path:      str = "none"   # "entropy" | "cluster_override" | "none"


def evaluate_checkpoint(
    checkpoint_position: str,
    rankings: list,
    already_asked: Optional[list] = None,
) -> CheckpointResult:
    """
    Evaluate one checkpoint against the current state distribution.

    Steps:
      1. Convert scores to probabilities.
      2. Compute Shannon Entropy.
      3. Compare to threshold for this checkpoint.
      4. If fires and Q11/Q19: identify top cluster, select distinguisher questions.
      5. If fires and Q27: set narrative_trigger = True.

    If entropy > threshold: checkpoint fires (action required).
    If entropy <= threshold: continue standard path.

    Spec reference: Section III.2
    """
    if checkpoint_position not in CHECKPOINT_POSITIONS:
        raise ValueError(
            f"Invalid checkpoint: {checkpoint_position!r}. "
            f"Must be one of {CHECKPOINT_POSITIONS}"
        )

    asked = already_asked or []
    threshold = CHECKPOINT_THRESHOLDS[checkpoint_position]

    probabilities = scores_to_probabilities(rankings)
    entropy = compute_entropy(probabilities)
    fires = entropy > threshold
    trigger_path = "entropy" if fires else "none"
    top_cluster = None
    distinguishers = []
    narrative_trigger = False

    CLUSTER_TRIGGER_TARGETS = ["C-Manager", "C-Culture"]

    if fires:
        if checkpoint_position in ("Q11", "Q19"):
            top_cluster = top_cluster_by_score(rankings)
        elif checkpoint_position == "Q27":
            narrative_trigger = True

    elif checkpoint_position in ("Q11", "Q19"):
        top_3_ids = [r.state_id for r in rankings[:3]]
        for state_id in top_3_ids:
            for cluster_name in CLUSTER_TRIGGER_TARGETS:
                if state_id in CLUSTERS[cluster_name]:
                    fires = True
                    top_cluster = cluster_name
                    trigger_path = "cluster_override"
                    break
            if top_cluster:
                break

    if fires and top_cluster:
        distinguishers = select_distinguisher_questions(top_cluster, asked)

    return CheckpointResult(
        checkpoint=checkpoint_position,
        entropy=entropy,
        threshold=threshold,
        fires=fires,
        top_cluster=top_cluster,
        distinguishers=distinguishers,
        narrative_trigger=narrative_trigger,
        trigger_path=trigger_path,
    )


# ── III.3  Narrative Prompt Trigger Conditions ─────────────────────────────────

def narrative_should_fire(
    checkpoint_position: str,
    entropy: float,
    already_fired: bool = False,
) -> bool:
    """
    Determine whether the narrative prompt should fire at this point.

    Rules (Section III.3):
      Standard trigger: always fires after Q34, regardless of entropy.
      Early trigger:    fires at Q27 if entropy > THRESHOLD_Q27.
      Replaces rule:    if narrative fired at Q27 (early), it does NOT fire at Q34.

    Parameters:
      checkpoint_position: "Q27" | "Q34"
      entropy:             current Shannon Entropy at this checkpoint
      already_fired:       True if narrative has already fired this session

    Spec reference: Section III.3
    """
    if already_fired:
        return False
    if checkpoint_position == "Q27":
        return entropy > THRESHOLD_Q27
    if checkpoint_position == "Q34":
        return True
    return False


def build_narrative_prompt_context(
    rankings: list,
    top_n: int = 3,
) -> dict:
    """
    Assemble the context passed to the LLM for narrative prompt generation.

    Returns the top N states by rank for use as the provisional picture.
    Does not include state names in the principal-facing prompt — that is
    enforced at the LLM call layer (Section IV). This context is for the
    system prompt, not the principal-facing question text.

    Spec reference: Section III.3
      "Draws from the top 1–3 states in the current distribution."
      "Does not name states — observational framing only."
    """
    top_states = rankings[:top_n]
    return {
        "top_states": [
            {
                "rank":     r.rank,
                "state_id": r.state_id,
                "score":    round(r.score, 4),
                "distance": round(r.distance, 4),
            }
            for r in top_states
        ],
        "entropy":      round(compute_entropy(scores_to_probabilities(rankings)), 4),
        "max_entropy":  round(MAX_ENTROPY, 4),
    }


# ── CheckpointEngine ───────────────────────────────────────────────────────────

class CheckpointEngine:
    """
    Stateful orchestrator for all three checkpoints in one scoring session.

    Tracks questions already asked, whether the narrative has fired, and
    which checkpoints have been evaluated.

    Usage:
        cp_engine = CheckpointEngine()
        # After Q11 answers are accumulated:
        result_q11 = cp_engine.evaluate("Q11", rankings)
        if result_q11.fires:
            for q in result_q11.distinguishers:
                # present q to principal, accumulate answer
                cp_engine.record_asked(q.question_id)
        # After Q19 answers:
        result_q19 = cp_engine.evaluate("Q19", rankings)
        # After Q27 answers:
        result_q27 = cp_engine.evaluate("Q27", rankings)
        if result_q27.narrative_trigger:
            context = cp_engine.narrative_context(rankings)
            # pass context to Section IV narrative engine

    Spec reference: Section III (all subsections)
    """

    def __init__(self):
        self.questions_asked: list = []
        self.narrative_fired: bool = False
        self.results: dict = {}  # checkpoint_position → CheckpointResult

    def record_asked(self, question_id: str) -> None:
        """Record a question as asked to prevent re-selection."""
        if question_id not in self.questions_asked:
            self.questions_asked.append(question_id)

    def evaluate(self, checkpoint_position: str, rankings: list) -> CheckpointResult:
        """
        Evaluate one checkpoint. Records result and updates narrative_fired flag.
        """
        result = evaluate_checkpoint(
            checkpoint_position, rankings, self.questions_asked
        )
        self.results[checkpoint_position] = result
        if result.narrative_trigger:
            self.narrative_fired = True
        return result

    def should_fire_narrative_at_q34(self, rankings: list) -> bool:
        """
        Check whether narrative should fire at Q34 (standard trigger).
        Returns False if it already fired early at Q27.
        """
        entropy = compute_entropy(scores_to_probabilities(rankings))
        return narrative_should_fire("Q34", entropy, self.narrative_fired)

    def narrative_context(self, rankings: list, top_n: int = 3) -> dict:
        """Build context dict for the LLM narrative prompt (Section IV)."""
        return build_narrative_prompt_context(rankings, top_n)
