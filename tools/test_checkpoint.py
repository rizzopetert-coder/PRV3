"""
PRV3 Checkpoint Engine — Section III Integration Test

Verifies:
  1. scores_to_probabilities: normalizes correctly, handles zero sum
  2. compute_entropy: uniform dist = log2(n), single-state = 0, known values
  3. MAX_ENTROPY: correct for the current state-taxonomy count
  4. top_cluster_by_score: returns dominant cluster by aggregate score
  5. evaluate_checkpoint Q11: fires when entropy > threshold, correct cluster
  6. evaluate_checkpoint Q19: fires when entropy > threshold
  7. evaluate_checkpoint Q27: fires narrative_trigger, no distinguishers
  8. evaluate_checkpoint: does NOT fire when entropy <= threshold
  9. narrative_should_fire: standard Q34 always fires, early Q27 conditional
 10. narrative_should_fire: already_fired blocks re-firing (replaces rule)
 11. build_narrative_prompt_context: correct top-n state structure
 12. CheckpointEngine: stateful orchestration, record_asked deduplication
 13. CheckpointEngine: Q34 narrative blocked after Q27 early fire
"""

import sys
from math import log2, isclose
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

from engine.checkpoint import (
    scores_to_probabilities, compute_entropy, MAX_ENTROPY,
    top_cluster_by_score, evaluate_checkpoint, select_distinguisher_questions,
    narrative_should_fire, build_narrative_prompt_context, CheckpointEngine,
    THRESHOLD_Q11, THRESHOLD_Q19, THRESHOLD_Q27,
)
from engine.accumulation import StateRanking, AccumulationEngine, IntakeData
from engine.data.states import STATE_PROFILES, CLUSTERS

PASS = []
FAIL = []

def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Checkpoint Engine — Section III Integration Test")
print("=" * 64)

n = len(STATE_PROFILES)


# ── Helper: build synthetic rankings ──────────────────────────────────────────

def uniform_rankings():
    """All states at equal score (baseline, no accumulation)."""
    score = 1.0 / n
    return [
        StateRanking(rank=i+1, state_id=sid, distance=0.5, score=score)
        for i, sid in enumerate(STATE_PROFILES)
    ]

def concentrated_rankings(top_state_id: str, top_score: float = 0.9):
    """One state with top_score, remainder share what's left equally."""
    remaining = (1.0 - top_score) / (n - 1)
    rankings = []
    rank = 1
    for sid in STATE_PROFILES:
        s = top_score if sid == top_state_id else remaining
        rankings.append(StateRanking(rank=rank, state_id=sid, distance=0.1, score=s))
        rank += 1
    rankings.sort(key=lambda r: -r.score)
    for i, r in enumerate(rankings):
        r.rank = i + 1
    return rankings


# ── 1. scores_to_probabilities ─────────────────────────────────────────────────
print("\n1. scores_to_probabilities")

uniform = uniform_rankings()
probs_uniform = scores_to_probabilities(uniform)

check("Probabilities sum to 1.0",
      isclose(sum(probs_uniform.values()), 1.0, rel_tol=1e-9),
      f"sum={sum(probs_uniform.values())}")
check("Uniform rankings → equal probabilities",
      all(isclose(p, 1.0/n, rel_tol=1e-9) for p in probs_uniform.values()),
      f"sample: {list(probs_uniform.values())[:3]}")
check("All state_ids represented",
      set(probs_uniform.keys()) == set(STATE_PROFILES.keys()),
      f"missing: {set(STATE_PROFILES.keys()) - set(probs_uniform.keys())}")


# ── 2. compute_entropy ─────────────────────────────────────────────────────────
print("\n2. compute_entropy")

# Uniform distribution → maximum entropy
h_uniform = compute_entropy(probs_uniform)
check("Uniform entropy equals log2(47)",
      isclose(h_uniform, log2(n), rel_tol=1e-9),
      f"got {h_uniform:.6f}, expected {log2(n):.6f}")

# Single-state certainty → entropy = 0
probs_certain = {sid: (1.0 if sid == "the_unformed_leader" else 0.0)
                 for sid in STATE_PROFILES}
h_certain = compute_entropy(probs_certain)
check("Certain single-state: entropy = 0.0",
      isclose(h_certain, 0.0, abs_tol=1e-12),
      f"got {h_certain}")

# Two equal states → entropy = log2(2) = 1.0
probs_two = {sid: (0.5 if sid in ("the_unformed_leader", "decision_paralysis") else 0.0)
             for sid in STATE_PROFILES}
h_two = compute_entropy(probs_two)
check("Two-state equal: entropy = 1.0 bit",
      isclose(h_two, 1.0, rel_tol=1e-9),
      f"got {h_two:.6f}")

print(f"  MAX_ENTROPY (47 states): {MAX_ENTROPY:.6f} bits")
print(f"  Uniform entropy: {h_uniform:.6f} bits")


# ── 3. MAX_ENTROPY ─────────────────────────────────────────────────────────────
print("\n3. MAX_ENTROPY")

check("MAX_ENTROPY = log2(n)",
      isclose(MAX_ENTROPY, log2(n), rel_tol=1e-9),
      f"got {MAX_ENTROPY}")
check("MAX_ENTROPY matches uniform entropy",
      isclose(MAX_ENTROPY, h_uniform, rel_tol=1e-9),
      f"MAX={MAX_ENTROPY}, H={h_uniform}")


# ── 4. top_cluster_by_score ────────────────────────────────────────────────────
print("\n4. top_cluster_by_score")

# Elevate a C-Manager state (the_overloaded_manager)
rankings_manager = []
for i, (sid, profile) in enumerate(STATE_PROFILES.items()):
    score = 0.9 if sid == "the_overloaded_manager" else 0.01
    rankings_manager.append(StateRanking(rank=i+1, state_id=sid, distance=0.1, score=score))

top = top_cluster_by_score(rankings_manager)
check("C-Manager member elevated → top_cluster = C-Manager",
      top == "C-Manager",
      f"got {top!r}")

# Elevate a C-Culture state
rankings_culture = []
for i, (sid, profile) in enumerate(STATE_PROFILES.items()):
    score = 0.8 if sid == "culture_drift" else 0.01
    rankings_culture.append(StateRanking(rank=i+1, state_id=sid, distance=0.1, score=score))
top_culture = top_cluster_by_score(rankings_culture)
check("C-Culture member elevated → top_cluster = C-Culture",
      top_culture == "C-Culture",
      f"got {top_culture!r}")

# Non-cluster state elevated — cluster with highest aggregate still wins
# (non-cluster states don't contribute to any cluster score)
rankings_non_cluster = []
for i, (sid, profile) in enumerate(STATE_PROFILES.items()):
    # Elevate the_founders_grip (no cluster) but also slightly elevate a C-Manager state
    if sid == "the_founders_grip":
        score = 0.8
    elif sid == "the_unformed_leader":
        score = 0.1
    else:
        score = 0.01
    rankings_non_cluster.append(StateRanking(rank=i+1, state_id=sid, distance=0.1, score=score))
top_nc = top_cluster_by_score(rankings_non_cluster)
check("Non-cluster state dominant but C-Manager has aggregate advantage → C-Manager",
      top_nc == "C-Manager",
      f"got {top_nc!r}")


# ── 5. evaluate_checkpoint — Q11 fires ────────────────────────────────────────
print("\n5. evaluate_checkpoint — Q11 fires")

# Uniform distribution has entropy = log2(47) >> THRESHOLD_Q11 (0.6)
result_q11 = evaluate_checkpoint("Q11", uniform)

check("Q11 with uniform distribution: fires=True",
      result_q11.fires is True,
      f"entropy={result_q11.entropy:.4f}, threshold={result_q11.threshold}")
check("Q11 checkpoint position recorded",
      result_q11.checkpoint == "Q11",
      f"got {result_q11.checkpoint!r}")
check("Q11 threshold is THRESHOLD_Q11",
      result_q11.threshold == THRESHOLD_Q11,
      f"got {result_q11.threshold}")
check("Q11 entropy equals uniform entropy",
      isclose(result_q11.entropy, h_uniform, rel_tol=1e-9),
      f"got {result_q11.entropy:.6f}")
check("Q11 fires: narrative_trigger = False (distinguisher path, not narrative)",
      result_q11.narrative_trigger is False,
      f"narrative_trigger={result_q11.narrative_trigger}")

print(f"  Q11 entropy: {result_q11.entropy:.4f} bits (threshold {THRESHOLD_Q11})")
print(f"  Q11 top_cluster: {result_q11.top_cluster!r} (question library empty - 0 distinguishers)")


# ── 6. evaluate_checkpoint — Q19 fires ────────────────────────────────────────
print("\n6. evaluate_checkpoint — Q19 fires")

result_q19 = evaluate_checkpoint("Q19", uniform)
check("Q19 with uniform distribution: fires=True",
      result_q19.fires is True,
      f"entropy={result_q19.entropy:.4f}")
check("Q19 threshold is THRESHOLD_Q19",
      result_q19.threshold == THRESHOLD_Q19,
      f"got {result_q19.threshold}")
check("Q19 fires: narrative_trigger = False",
      result_q19.narrative_trigger is False,
      f"narrative_trigger={result_q19.narrative_trigger}")


# ── 7. evaluate_checkpoint — Q27 fires (narrative_trigger) ────────────────────
print("\n7. evaluate_checkpoint — Q27 fires")

result_q27 = evaluate_checkpoint("Q27", uniform)
check("Q27 with uniform distribution: fires=True",
      result_q27.fires is True,
      f"entropy={result_q27.entropy:.4f}")
check("Q27 fires: narrative_trigger=True",
      result_q27.narrative_trigger is True,
      f"narrative_trigger={result_q27.narrative_trigger}")
check("Q27 fires: no distinguishers (narrative path, not distinguisher path)",
      result_q27.distinguishers == [],
      f"distinguishers: {result_q27.distinguishers}")
check("Q27 fires: top_cluster is None (Q27 is verdict gate, not cluster route)",
      result_q27.top_cluster is None,
      f"top_cluster={result_q27.top_cluster!r}")

print(f"  Q27 entropy: {result_q27.entropy:.4f} bits (threshold {THRESHOLD_Q27})")


# ── 8. evaluate_checkpoint — does NOT fire when below threshold ────────────────
print("\n8. evaluate_checkpoint — below threshold (no fire)")

# Highly concentrated distribution: entropy should be near 0
concentrated = concentrated_rankings("the_unformed_leader", top_score=0.999)
probs_conc = scores_to_probabilities(concentrated)
h_conc = compute_entropy(probs_conc)
print(f"  Concentrated distribution entropy: {h_conc:.6f} bits")

result_q27_conc = evaluate_checkpoint("Q27", concentrated)
check("Q27 with concentrated distribution below threshold: fires=False",
      result_q27_conc.fires is False,
      f"entropy={result_q27_conc.entropy:.6f}, threshold={result_q27_conc.threshold}")
check("Q27 no-fire: narrative_trigger=False",
      result_q27_conc.narrative_trigger is False,
      f"narrative_trigger={result_q27_conc.narrative_trigger}")

# the_unformed_leader is in C-Manager — cluster_override fires Q11 even below threshold
result_q11_conc = evaluate_checkpoint("Q11", concentrated)
check("Q11 with concentrated C-Manager state: fires=True via cluster_override",
      result_q11_conc.fires is True,
      f"entropy={h_conc:.6f}, threshold={THRESHOLD_Q11}")
check("Q11 cluster_override: trigger_path=cluster_override",
      result_q11_conc.trigger_path == "cluster_override",
      f"trigger_path={result_q11_conc.trigger_path!r}")


# ── 9. narrative_should_fire ───────────────────────────────────────────────────
print("\n9. narrative_should_fire")

# Q34 always fires (standard trigger)
check("Q34: narrative always fires (standard trigger)",
      narrative_should_fire("Q34", entropy=5.0) is True,
      "Q34 should always return True")
check("Q34: narrative fires even at zero entropy",
      narrative_should_fire("Q34", entropy=0.0) is True,
      "Q34 zero entropy should still fire")

# Q27: early trigger conditional on entropy > THRESHOLD_Q27
check("Q27: fires when entropy > THRESHOLD_Q27",
      narrative_should_fire("Q27", entropy=THRESHOLD_Q27 + 0.01) is True,
      f"entropy={THRESHOLD_Q27 + 0.01}, threshold={THRESHOLD_Q27}")
check("Q27: does not fire when entropy <= THRESHOLD_Q27",
      narrative_should_fire("Q27", entropy=THRESHOLD_Q27) is False,
      f"entropy={THRESHOLD_Q27} (equal to threshold → no fire)")
check("Q27: does not fire when entropy below threshold",
      narrative_should_fire("Q27", entropy=THRESHOLD_Q27 - 0.01) is False,
      f"entropy={THRESHOLD_Q27 - 0.01}")

# Unknown checkpoint — does not fire
check("Unknown checkpoint position: does not fire",
      narrative_should_fire("Q11", entropy=5.0) is False,
      "Q11 is not a narrative trigger position")


# ── 10. already_fired blocks re-firing ────────────────────────────────────────
print("\n10. narrative_should_fire — already_fired blocks re-fire (replaces rule)")

check("Q34 blocked when already_fired=True",
      narrative_should_fire("Q34", entropy=5.0, already_fired=True) is False,
      "already_fired should block Q34 standard trigger")
check("Q27 blocked when already_fired=True",
      narrative_should_fire("Q27", entropy=5.0, already_fired=True) is False,
      "already_fired should block Q27 early trigger")


# ── 11. build_narrative_prompt_context ────────────────────────────────────────
print("\n11. build_narrative_prompt_context")

context = build_narrative_prompt_context(uniform, top_n=3)
check("Context has 'top_states' key", "top_states" in context)
check("Context has 'entropy' key", "entropy" in context)
check("Context has 'max_entropy' key", "max_entropy" in context)
check("top_states contains 3 entries", len(context["top_states"]) == 3,
      f"got {len(context['top_states'])}")
check("top_states entries have required fields",
      all("rank" in s and "state_id" in s and "score" in s and "distance" in s
          for s in context["top_states"]),
      f"missing fields: {context['top_states']}")
check("Context max_entropy matches MODULE MAX_ENTROPY",
      isclose(context["max_entropy"], MAX_ENTROPY, rel_tol=1e-3),
      f"context={context['max_entropy']}, module={MAX_ENTROPY}")


# ── 12. CheckpointEngine — stateful orchestration ─────────────────────────────
print("\n12. CheckpointEngine — stateful orchestration")

engine = CheckpointEngine()
check("Initial questions_asked is empty", engine.questions_asked == [])
check("Initial narrative_fired is False", engine.narrative_fired is False)
check("Initial results is empty dict", engine.results == {})

# Record some asked questions
engine.record_asked("DIST-CM-01")
engine.record_asked("DIST-CM-02")
check("record_asked adds to questions_asked",
      "DIST-CM-01" in engine.questions_asked and "DIST-CM-02" in engine.questions_asked)
check("record_asked deduplicates",
      engine.questions_asked.count("DIST-CM-01") == 1,
      "duplicate detected")

# Re-record same question — should not duplicate
engine.record_asked("DIST-CM-01")
check("record_asked called twice on same ID: no duplicate",
      engine.questions_asked.count("DIST-CM-01") == 1,
      f"count={engine.questions_asked.count('DIST-CM-01')}")

# Evaluate Q11
result = engine.evaluate("Q11", uniform)
check("Engine.evaluate stores result in engine.results",
      "Q11" in engine.results,
      f"results keys: {list(engine.results.keys())}")
check("Engine.evaluate result matches standalone evaluate_checkpoint",
      result.fires == True and result.checkpoint == "Q11",
      f"fires={result.fires}, checkpoint={result.checkpoint!r}")

# Evaluate Q27 with uniform (fires → sets narrative_fired)
result_27 = engine.evaluate("Q27", uniform)
check("Engine.evaluate Q27: narrative_trigger sets engine.narrative_fired",
      engine.narrative_fired is True,
      f"narrative_fired={engine.narrative_fired}")


# ── 13. Q34 blocked after Q27 early fire ──────────────────────────────────────
print("\n13. CheckpointEngine — Q34 blocked after Q27 early narrative")

check("should_fire_narrative_at_q34 returns False after Q27 early fire",
      engine.should_fire_narrative_at_q34(uniform) is False,
      "Q34 should be blocked when narrative already fired at Q27")

# Fresh engine — Q34 should fire
fresh_engine = CheckpointEngine()
check("should_fire_narrative_at_q34 returns True when not yet fired",
      fresh_engine.should_fire_narrative_at_q34(uniform) is True,
      "Q34 should fire on fresh engine")


# ── 14. select_distinguisher_questions — populated library ─────────────────────
print("\n14. select_distinguisher_questions — populated library")

# C-Manager pool: DIST-CM-01, DIST-CM-02 (max 2 returned)
result_cm = select_distinguisher_questions("C-Manager", already_asked=[])
check("C-Manager pool returns 2 distinguishers",
      len(result_cm) == 2,
      f"got {len(result_cm)}")
check("C-Manager pool contains DIST-CM-01",
      any(q.question_id == "DIST-CM-01" for q in result_cm),
      f"ids: {[q.question_id for q in result_cm]}")

# Already-asked filtering excludes asked questions
result_cm_filtered = select_distinguisher_questions(
    "C-Manager", already_asked=["DIST-CM-01"]
)
check("already_asked filtering: 1 asked → 1 returned",
      len(result_cm_filtered) == 1 and result_cm_filtered[0].question_id == "DIST-CM-02",
      f"got {[q.question_id for q in result_cm_filtered]}")

# C-Culture pool: DIST-CC-01, DIST-CC-02 (max 2 returned)
result_cc = select_distinguisher_questions("C-Culture", already_asked=[])
check("C-Culture pool returns 2 distinguishers",
      len(result_cc) == 2,
      f"got {len(result_cc)}")

# Invalid cluster still returns empty list
result_dq_invalid = select_distinguisher_questions("INVALID_CLUSTER", already_asked=[])
check("Invalid cluster_id returns empty list",
      result_dq_invalid == [],
      f"got {result_dq_invalid}")


# ── 15. Invalid checkpoint position raises ValueError ─────────────────────────
print("\n15. evaluate_checkpoint — invalid position raises ValueError")

try:
    evaluate_checkpoint("Q34", uniform)
    check("Invalid checkpoint raises ValueError", False, "No exception raised")
except ValueError:
    check("Invalid checkpoint raises ValueError", True)


# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\nAll checks passed. Section III checkpoint engine is structurally valid.")
print("=" * 64)

sys.exit(1 if FAIL else 0)
