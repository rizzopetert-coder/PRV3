"""
PRV3 Taxonomy Expansion 47 -> 57 — Core Patch (Session 67)

Applies the Session 65 Gemini-approved taxonomy expansion (10 new states) to:
  - web/data/taxonomy.ts        (state entries, signatureId membership, count comment)
  - engine/data/states.py       (StateProfile registry entries, cluster membership, count comment)
  - engine/data/validate.py     (count assertions)
  - engine/resolution_families.py (STATE_RESOLUTION_FAMILY mappings, assert)
  - engine/data/salience.py     (SALIENCE_PROFILES weight entries)
  - engine/checkpoint.py        (entropy comment)
  - engine/friction_tax.py      (STATE_MULTIPLIERS CALIBRATION TARGET entries)
  - engine/test_suite.py        (Phase 1 minimum comment)
  - CLAUDE.md                   (count references)
  - web/content/book/methodology/symptoms-states-and-why-the-distinction-matters.md

DRAFT STATUS: The per-state classification fields this script writes (signal_weight,
cluster_id, liability_axes, asset_axes, severity_range, resolution_family in both the
legacy states.py sense and the live resolution_families.py 4-bucket sense, salience
weights, and taxonomy.ts signatureId) were NOT part of Session 65's Gemini-reviewed
scope -- that review approved state names, dimension assignment, and disposition only.
These values are authored here from scratch, grounded in research/seven-experiments/
consolidation-mapping-trace.md's own disposition rationale and analogy to the closest
existing state in each dimension. See prompts/gemini-handoff-taxonomy-expansion-57.md
for the full rationale per field. Per Pete's direction this session: draft now, route
through Gemini for architecture review before locking.

Usage:
  python tools/patch_taxonomy_expansion_57.py --dry-run
  python tools/patch_taxonomy_expansion_57.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Each entry: (relative_path, old_string, new_string, expected_count)
# expected_count = how many times old_string must appear (1 unless noted).
# ---------------------------------------------------------------------------

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ═══════════════════════════════════════════════════════════════════════════
# 1. web/data/taxonomy.ts
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "web/data/taxonomy.ts",
    "// States — 47 total\n// ---------------------------------------------------------------------------",
    "// States — 57 total (47 locked Session 5 + 10 added Session 67, taxonomy expansion,\n"
    "// DRAFT pending Gemini architecture review of signatureId assignment)\n"
    "// ---------------------------------------------------------------------------",
)

# --- Aptitude: insert after the_paper_tiger, before "// AUTHORITY — 18 states" ---
edit(
    "web/data/taxonomy.ts",
    '  // AUTHORITY — 18 states\n',
    '  {\n'
    '    id: "invisible_performance_management",\n'
    '    name: "Invisible Performance Management",\n'
    '    signatureId: "compounding_risks",\n'
    '    description:\n'
    '      "Performance managed through relationship and conversation rather than documentation. The manager\'s judgment is accurate. The file doesn\'t support it. The termination is legally indefensible not because it\'s wrong but because it\'s undocumented.",\n'
    '  },\n\n'
    '  // AUTHORITY — 22 states\n',
)

# --- Authority: insert 4 new states after the_pay_fog, before "// ALLIANCE — 6 states" ---
edit(
    "web/data/taxonomy.ts",
    '  // ALLIANCE — 6 states\n',
    '  {\n'
    '    id: "compression_crisis",\n'
    '    name: "Compression Crisis",\n'
    '    signatureId: "compounding_risks",\n'
    '    description:\n'
    '      "New hires offered at or above salaries of longer-tenured employees in the same role. Simultaneously losing existing employees who discover the compression and constrained on offers by transparency requirements. A dynamic condition created by intersecting pressures.",\n'
    '  },\n'
    '  {\n'
    '    id: "sequential_decision_blindness",\n'
    '    name: "Sequential Decision Blindness",\n'
    '    signatureId: "compounding_risks",\n'
    '    description:\n'
    '      "Individual decisions made in isolation that constitute retaliation in sequence. No individual acts with retaliatory intent. The absence of coordinated oversight makes the sequence structurally inevitable. The organization pays for intent it didn\'t have. Distinct from Decision Blindness (Alliance) — that is a single-decision coordination failure; this is a retaliation-liability pattern produced by a sequence of uncoordinated decisions, none of them individually retaliatory.",\n'
    '  },\n'
    '  {\n'
    '    id: "disparate_impact_architecture",\n'
    '    name: "Disparate Impact Architecture",\n'
    '    signatureId: "compounding_risks",\n'
    '    description:\n'
    '      "Organizational systems designed without disparate impact analysis that produce discriminatory outcomes through their operation. The strongest financial consequence narrative in the taxonomy — class action exposure with no statutory cap.",\n'
    '  },\n'
    '  {\n'
    '    id: "planning_authority_gap",\n'
    '    name: "Planning Authority Gap",\n'
    '    signatureId: "leadership_bottleneck",\n'
    '    description:\n'
    '      "HR has the capability to do strategic workforce planning and lacks the organizational authority and credibility to have its output treated as strategic input. Distinct from HR Capture (compromised) — this is specifically about the gap between analytical capability and organizational standing to act on the analysis.",\n'
    '  },\n\n'
    '  // ALLIANCE — 7 states\n',
)

# --- Alliance: insert after decision_blindness, before "// ATTITUDE — 17 states" ---
edit(
    "web/data/taxonomy.ts",
    '  // ATTITUDE — 17 states\n',
    '  {\n'
    '    id: "distributed_culture_fragmentation",\n'
    '    name: "Distributed Culture Fragmentation",\n'
    '    signatureId: "culture_erosion",\n'
    '    description:\n'
    '      "The organization\'s culture has fractured along location lines. In-office and remote cultures have diverged to the point of producing different experiences, different leadership relationships, and different career trajectories. Culture Drift applied to a geographic dimension.",\n'
    '  },\n\n'
    '  // ATTITUDE — 21 states\n',
)

# --- Attitude: insert 4 new states after the_broken_compass, before closing "];" ---
edit(
    "web/data/taxonomy.ts",
    '      "You\'ve been in the meeting where it was diagnosed. You\'ve read the report. You\'ve heard the leadership team agree that something needs to change. That was eighteen months ago. The people with the most options — the ones the organization can least afford to lose — have stopped waiting for the next conversation to be different.",\n  },\n];',
    '      "You\'ve been in the meeting where it was diagnosed. You\'ve read the report. You\'ve heard the leadership team agree that something needs to change. That was eighteen months ago. The people with the most options — the ones the organization can least afford to lose — have stopped waiting for the next conversation to be different.",\n  },\n'
    '  {\n'
    '    id: "wellbeing_theater",\n'
    '    name: "Wellbeing Theater",\n'
    '    signatureId: "culture_erosion",\n'
    '    description:\n'
    '      "Structural mismatch between wellbeing investment and wellbeing conditions. A specific variant of Culture Drift — the stated value and the structural reality have diverged at the wellbeing dimension specifically.",\n'
    '  },\n'
    '  {\n'
    '    id: "human_displacement_anxiety",\n'
    '    name: "Human Displacement Anxiety",\n'
    '    signatureId: "stunted_growth",\n'
    '    description:\n'
    '      "AI deployed without managing the human response. Employees uncertain about role security and value in an AI-augmented environment. Produces disengagement and departure of the people who would have been most effective AI collaborators.",\n'
    '  },\n'
    '  {\n'
    '    id: "motivational_architecture_failure",\n'
    '    name: "Motivational Architecture Failure",\n'
    '    signatureId: "culture_erosion",\n'
    '    description:\n'
    '      "Reward, recognition, and performance management systems have produced a predominantly controlled or amotivated workforce. Not low engagement — a specific psychological condition where the majority of employees either perform to avoid punishment or have stopped believing their effort affects outcomes. Self-reinforcing: organizations with controlled motivation produce more controlling management. Distinct from The Wrong Reward — that is rational strategic optimization for the real, unstated incentive system; this is a clinical amotivation condition regardless of what the real incentives are.",\n'
    '  },\n'
    '  {\n'
    '    id: "cultural_overtime",\n'
    '    name: "Cultural Overtime",\n'
    '    signatureId: "culture_erosion",\n'
    '    description:\n'
    '      "Compensable work produced outside paid hours through cultural pressure rather than explicit instruction. The policy is compliant. The culture creates the liability. Distinct from Structural Overload — this is about expected availability, not volume.",\n'
    '  },\n'
    '];',
)

# --- signatures[] stateIds membership updates ---
edit(
    "web/data/taxonomy.ts",
    '      "hr_capture",\n      "the_fracture",\n    ],',
    '      "hr_capture",\n      "the_fracture",\n      "planning_authority_gap",\n    ],',
)
edit(
    "web/data/taxonomy.ts",
    '      "the_inside_track",\n      "narrative_lock",\n    ],',
    '      "the_inside_track",\n      "narrative_lock",\n      "wellbeing_theater",\n      "motivational_architecture_failure",\n      "cultural_overtime",\n      "distributed_culture_fragmentation",\n    ],',
)
edit(
    "web/data/taxonomy.ts",
    '      "invisible_burnout",\n      "the_second_close",\n    ],',
    '      "invisible_burnout",\n      "the_second_close",\n      "human_displacement_anxiety",\n    ],',
)
edit(
    "web/data/taxonomy.ts",
    '      "decision_blindness",\n      "the_arbitrary_standard",\n      "paper_shield",\n    ],',
    '      "decision_blindness",\n      "the_arbitrary_standard",\n      "paper_shield",\n      "compression_crisis",\n      "sequential_decision_blindness",\n      "disparate_impact_architecture",\n      "invisible_performance_management",\n    ],',
)


# ═══════════════════════════════════════════════════════════════════════════
# 2. engine/data/states.py
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "engine/data/states.py",
    "NOTE — COUNT: Aptitude (6), Authority (18), Alliance (6), Attitude (17) = 47.",
    "NOTE — COUNT: Aptitude (7), Authority (22), Alliance (7), Attitude (21) = 57.\n"
    "Taxonomy expansion (Session 65 decision, Session 67 implementation): 10 states added.\n"
    "Per-state classification fields (signal_weight, cluster_id, axes, severity_range,\n"
    "resolution_family, dimensional_vector) for the 10 new states are DRAFT — authored\n"
    "this session from consolidation-mapping-trace.md disposition rationale and analogy\n"
    "to the closest existing state, NOT independently Gemini-reviewed. See\n"
    "prompts/gemini-handoff-taxonomy-expansion-57.md.",
)

edit(
    "engine/data/states.py",
    '# ╔══════════════════════════════════════════════════════════════════════════════╗\n'
    '# ║  AUTHORITY  (18 states)                                                     ║\n'
    '# ╚══════════════════════════════════════════════════════════════════════════════╝',
    '_reg(_profile(\n'
    '    state_id="invisible_performance_management",\n'
    '    state_name="Invisible Performance Management",\n'
    '    primary_dimension="Aptitude",\n'
    '    signal_weight="medium",\n'
    '    cluster_id=None,\n'
    '    liability_axes=["Legal & Compliance", "Governance & Authority", "Talent & Retention"],\n'
    '    asset_axes=["Governance Discipline", "Accountability Architecture"],\n'
    '    sev_min="Emerging", sev_max="Entrenched",\n'
    '    # DRAFT — pending Gemini review. E2 #06 (consolidation-mapping-trace.md Batch A).\n'
    '    # NAMING HISTORY: this exact state_id/name was previously used pre-rename for what\n'
    '    # is now the_paper_tiger (see NOTE — NAME MAPPING above, profiles doc #33, and\n'
    '    # the_paper_tiger\'s own "Renamed from clinical name" comment below). That entry was\n'
    '    # fully removed from this registry years ago (state_removal_final.md, 45-vs-47 count\n'
    '    # question, resolved at 47) -- no live id collision. This is a mechanistically\n'
    '    # distinct NEW state per Session 65\'s disposition: accurate managerial judgment\n'
    '    # rendered legally indefensible solely by lack of documentation, distinct from\n'
    '    # The Paper Tiger\'s active-concealment mechanism.\n'
    '    resolution_family="Development + Roadmap",\n'
    '))\n'
    'STATE_PROFILES["invisible_performance_management"].dimensional_vector = DimensionalVector(\n'
    '    aptitude_liability=0.45,\n'
    '    aptitude_asset=0.15,\n'
    '    authority_liability=0.25,\n'
    '    authority_asset=0.15,\n'
    '    alliance_liability=0.15,\n'
    '    alliance_asset=0.15,\n'
    '    attitude_liability=0.10,\n'
    '    attitude_asset=0.15,\n'
    ')\n\n\n'
    '# ╔══════════════════════════════════════════════════════════════════════════════╗\n'
    '# ║  AUTHORITY  (22 states)                                                     ║\n'
    '# ╚══════════════════════════════════════════════════════════════════════════════╝',
)

edit(
    "engine/data/states.py",
    '# ╔══════════════════════════════════════════════════════════════════════════════╗\n'
    '# ║  ALLIANCE  (6 states)                                                       ║\n'
    '# ╚══════════════════════════════════════════════════════════════════════════════╝',
    '_reg(_profile(\n'
    '    state_id="compression_crisis",\n'
    '    state_name="Compression Crisis",\n'
    '    primary_dimension="Authority",\n'
    '    signal_weight="medium",\n'
    '    cluster_id=None,\n'
    '    liability_axes=["Talent & Retention", "Financial & Economic", "Legal & Compliance"],\n'
    '    asset_axes=["Governance Discipline", "Strategic Execution Capacity"],\n'
    '    sev_min="Emerging", sev_max="Entrenched",\n'
    '    # DRAFT — pending Gemini review. E6 (consolidation-mapping-trace.md Batch C).\n'
    '    resolution_family="Roadmap",\n'
    '))\n'
    'STATE_PROFILES["compression_crisis"].dimensional_vector = DimensionalVector(\n'
    '    aptitude_liability=0.15,\n'
    '    aptitude_asset=0.15,\n'
    '    authority_liability=0.45,\n'
    '    authority_asset=0.15,\n'
    '    alliance_liability=0.15,\n'
    '    alliance_asset=0.15,\n'
    '    attitude_liability=0.15,\n'
    '    attitude_asset=0.15,\n'
    ')\n\n'
    '_reg(_profile(\n'
    '    state_id="sequential_decision_blindness",\n'
    '    state_name="Sequential Decision Blindness",\n'
    '    primary_dimension="Authority",\n'
    '    signal_weight="high",\n'
    '    cluster_id=None,\n'
    '    liability_axes=["Legal & Compliance", "Governance & Authority", "Financial & Economic"],\n'
    '    asset_axes=["Governance Discipline", "Accountability Architecture"],\n'
    '    sev_min="Emerging", sev_max="Entrenched",\n'
    '    # DRAFT — pending Gemini review. E2 (consolidation-mapping-trace.md Batch E).\n'
    '    # NAMING COLLISION (Session 65 required mitigation): "Sequential Decision Blindness"\n'
    '    # is also the profiles-doc inferred-mapping source name for the LOCKED Alliance-\n'
    '    # dimension state decision_blindness (see NOTE — NAME MAPPING above). Confirmed\n'
    '    # distinct per trace: retaliation-liability pattern from uncoordinated sequential\n'
    '    # decisions (this state, Authority), vs. decision_blindness\'s single-decision\n'
    '    # coordination failure (Alliance). Different dimension, different mechanism.\n'
    '    resolution_family="Intervention + Executive Counsel",\n'
    '))\n'
    'STATE_PROFILES["sequential_decision_blindness"].dimensional_vector = DimensionalVector(\n'
    '    aptitude_liability=0.10,\n'
    '    aptitude_asset=0.10,\n'
    '    authority_liability=0.60,\n'
    '    authority_asset=0.10,\n'
    '    alliance_liability=0.10,\n'
    '    alliance_asset=0.10,\n'
    '    attitude_liability=0.10,\n'
    '    attitude_asset=0.10,\n'
    ')\n\n'
    '_reg(_profile(\n'
    '    state_id="disparate_impact_architecture",\n'
    '    state_name="Disparate Impact Architecture",\n'
    '    primary_dimension="Authority",\n'
    '    signal_weight="high",\n'
    '    cluster_id=None,\n'
    '    liability_axes=["Legal & Compliance", "Financial & Economic", "Reputational & Brand"],\n'
    '    asset_axes=["Governance Discipline", "Accountability Architecture"],\n'
    '    sev_min="Entrenched", sev_max="Endemic",\n'
    '    # DRAFT — pending Gemini review. E2 #02 (consolidation-mapping-trace.md Batch C).\n'
    '    resolution_family="Intervention + Executive Counsel",\n'
    '))\n'
    'STATE_PROFILES["disparate_impact_architecture"].dimensional_vector = DimensionalVector(\n'
    '    aptitude_liability=0.10,\n'
    '    aptitude_asset=0.10,\n'
    '    authority_liability=0.60,\n'
    '    authority_asset=0.10,\n'
    '    alliance_liability=0.10,\n'
    '    alliance_asset=0.10,\n'
    '    attitude_liability=0.10,\n'
    '    attitude_asset=0.10,\n'
    ')\n\n'
    '_reg(_profile(\n'
    '    state_id="planning_authority_gap",\n'
    '    state_name="Planning Authority Gap",\n'
    '    primary_dimension="Authority",\n'
    '    signal_weight="low",\n'
    '    cluster_id=None,\n'
    '    liability_axes=["Operational & Structural", "Strategic", "Talent & Retention"],\n'
    '    asset_axes=["Strategic Execution Capacity", "Governance Discipline"],\n'
    '    sev_min="Emerging", sev_max="Entrenched",\n'
    '    # DRAFT — pending Gemini review. E6 (consolidation-mapping-trace.md Batch F).\n'
    '    resolution_family="Roadmap + Executive Counsel",\n'
    '))\n'
    'STATE_PROFILES["planning_authority_gap"].dimensional_vector = DimensionalVector(\n'
    '    aptitude_liability=0.15,\n'
    '    aptitude_asset=0.15,\n'
    '    authority_liability=0.35,\n'
    '    authority_asset=0.15,\n'
    '    alliance_liability=0.25,\n'
    '    alliance_asset=0.15,\n'
    '    attitude_liability=0.15,\n'
    '    attitude_asset=0.15,\n'
    ')\n\n\n'
    '# ╔══════════════════════════════════════════════════════════════════════════════╗\n'
    '# ║  ALLIANCE  (7 states)                                                       ║\n'
    '# ╚══════════════════════════════════════════════════════════════════════════════╝',
)

edit(
    "engine/data/states.py",
    '# ╔══════════════════════════════════════════════════════════════════════════════╗\n'
    '# ║  ATTITUDE  (17 states)                                                      ║\n'
    '# ╚══════════════════════════════════════════════════════════════════════════════╝',
    '_reg(_profile(\n'
    '    state_id="distributed_culture_fragmentation",\n'
    '    state_name="Distributed Culture Fragmentation",\n'
    '    primary_dimension="Alliance",\n'
    '    signal_weight="medium",\n'
    '    cluster_id=None,\n'
    '    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Operational & Structural"],\n'
    '    asset_axes=["Cultural Stewardship", "Relational Trust"],\n'
    '    sev_min="Emerging", sev_max="Entrenched",\n'
    '    # DRAFT — pending Gemini review. E6 (consolidation-mapping-trace.md Batch F).\n'
    '    resolution_family="Development + Intervention",\n'
    '))\n'
    'STATE_PROFILES["distributed_culture_fragmentation"].dimensional_vector = DimensionalVector(\n'
    '    aptitude_liability=0.15,\n'
    '    aptitude_asset=0.15,\n'
    '    authority_liability=0.15,\n'
    '    authority_asset=0.15,\n'
    '    alliance_liability=0.45,\n'
    '    alliance_asset=0.15,\n'
    '    attitude_liability=0.25,\n'
    '    attitude_asset=0.15,\n'
    ')\n\n\n'
    '# ╔══════════════════════════════════════════════════════════════════════════════╗\n'
    '# ║  ATTITUDE  (21 states)                                                      ║\n'
    '# ╚══════════════════════════════════════════════════════════════════════════════╝',
)

edit(
    "engine/data/states.py",
    '# ── Cluster registries ─────────────────────────────────────────────────────────\n\n'
    'CLUSTERS: dict[str, list[str]] = {\n'
    '    "C-Manager": [\n'
    '        "the_unformed_leader",\n'
    '        "the_overloaded_manager",\n'
    '        "the_dormant_talent",\n'
    '    ],\n'
    '    "C-Culture": [\n'
    '        "culture_drift",\n'
    '        "identity_erosion",\n'
    '        "the_culture_that_wasnt",\n'
    '    ],\n'
    '}',
    '# ── Cluster registries ─────────────────────────────────────────────────────────\n\n'
    'CLUSTERS: dict[str, list[str]] = {\n'
    '    "C-Manager": [\n'
    '        "the_unformed_leader",\n'
    '        "the_overloaded_manager",\n'
    '        "the_dormant_talent",\n'
    '    ],\n'
    '    "C-Culture": [\n'
    '        "culture_drift",\n'
    '        "identity_erosion",\n'
    '        "the_culture_that_wasnt",\n'
    '    ],\n'
    '}\n\n'
    '_reg(_profile(\n'
    '    state_id="wellbeing_theater",\n'
    '    state_name="Wellbeing Theater",\n'
    '    primary_dimension="Attitude",\n'
    '    signal_weight="cluster",\n'
    '    cluster_id="C-Culture",\n'
    '    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Financial & Economic"],\n'
    '    asset_axes=["Cultural Stewardship", "People Development Capability"],\n'
    '    sev_min="Emerging", sev_max="Entrenched",\n'
    '    # DRAFT — pending Gemini review. E6 (consolidation-mapping-trace.md Batch F).\n'
    '    # Source text self-describes as "a specific variant of Culture Drift" -- cluster_id\n'
    '    # drafted to match on that basis; Gemini review should confirm or reject C-Culture\n'
    '    # membership specifically (this is a judgment call, not a mechanical mapping).\n'
    '    # CLUSTERS["C-Culture"] updated below to include this state for functional\n'
    '    # consistency with checkpoint.py\'s cluster stress-test routing.\n'
    '    resolution_family="Intervention",\n'
    '))\n'
    'STATE_PROFILES["wellbeing_theater"].dimensional_vector = DimensionalVector(\n'
    '    aptitude_liability=0.15,\n'
    '    aptitude_asset=0.15,\n'
    '    authority_liability=0.25,\n'
    '    authority_asset=0.15,\n'
    '    alliance_liability=0.15,\n'
    '    alliance_asset=0.15,\n'
    '    attitude_liability=0.35,\n'
    '    attitude_asset=0.15,\n'
    ')\n'
    'CLUSTERS["C-Culture"].append("wellbeing_theater")\n\n'
    '_reg(_profile(\n'
    '    state_id="human_displacement_anxiety",\n'
    '    state_name="Human Displacement Anxiety",\n'
    '    primary_dimension="Attitude",\n'
    '    signal_weight="medium",\n'
    '    cluster_id=None,\n'
    '    liability_axes=["Talent & Retention", "Cultural & Behavioral", "Strategic"],\n'
    '    asset_axes=["Adaptive Capacity", "People Development Capability"],\n'
    '    sev_min="Emerging", sev_max="Entrenched",\n'
    '    # DRAFT — pending Gemini review. E6 (consolidation-mapping-trace.md Batch D).\n'
    '    resolution_family="Development + Intervention",\n'
    '))\n'
    'STATE_PROFILES["human_displacement_anxiety"].dimensional_vector = DimensionalVector(\n'
    '    aptitude_liability=0.15,\n'
    '    aptitude_asset=0.15,\n'
    '    authority_liability=0.15,\n'
    '    authority_asset=0.15,\n'
    '    alliance_liability=0.15,\n'
    '    alliance_asset=0.15,\n'
    '    attitude_liability=0.45,\n'
    '    attitude_asset=0.15,\n'
    ')\n\n'
    '_reg(_profile(\n'
    '    state_id="motivational_architecture_failure",\n'
    '    state_name="Motivational Architecture Failure",\n'
    '    primary_dimension="Attitude",\n'
    '    signal_weight="medium",\n'
    '    cluster_id=None,\n'
    '    liability_axes=["Cultural & Behavioral", "Talent & Retention", "Operational & Structural"],\n'
    '    asset_axes=["Governance Discipline", "Accountability Architecture"],\n'
    '    sev_min="Entrenched", sev_max="Endemic",\n'
    '    # DRAFT — pending Gemini review. E7 (consolidation-mapping-trace.md Batch D).\n'
    '    # NAMING COLLISION (found during implementation, not in Session 65\'s mitigation\n'
    '    # list): "Motivational Architecture Failure" is also the profiles-doc inferred-\n'
    '    # mapping source name for the LOCKED state the_wrong_reward (see NOTE — NAME\n'
    '    # MAPPING above, and the_wrong_reward\'s own "Inferred from profiles doc" comment\n'
    '    # below). Confirmed distinct per trace: clinical controlled/amotivated workforce\n'
    '    # condition via reward-system failure (this state), vs. The Wrong Reward\'s rational\n'
    '    # strategic optimization for the real, unstated incentive system.\n'
    '    resolution_family="Intervention + Roadmap",\n'
    '))\n'
    'STATE_PROFILES["motivational_architecture_failure"].dimensional_vector = DimensionalVector(\n'
    '    aptitude_liability=0.15,\n'
    '    aptitude_asset=0.15,\n'
    '    authority_liability=0.15,\n'
    '    authority_asset=0.15,\n'
    '    alliance_liability=0.15,\n'
    '    alliance_asset=0.15,\n'
    '    attitude_liability=0.45,\n'
    '    attitude_asset=0.15,\n'
    ')\n\n'
    '_reg(_profile(\n'
    '    state_id="cultural_overtime",\n'
    '    state_name="Cultural Overtime",\n'
    '    primary_dimension="Attitude",\n'
    '    signal_weight="medium",\n'
    '    cluster_id=None,\n'
    '    liability_axes=["Legal & Compliance", "Financial & Economic", "Cultural & Behavioral"],\n'
    '    asset_axes=["Governance Discipline", "Accountability Architecture"],\n'
    '    sev_min="Emerging", sev_max="Entrenched",\n'
    '    # DRAFT — pending Gemini review. E2 #08 (consolidation-mapping-trace.md Batch C).\n'
    '    resolution_family="Intervention + Roadmap",\n'
    '))\n'
    'STATE_PROFILES["cultural_overtime"].dimensional_vector = DimensionalVector(\n'
    '    aptitude_liability=0.15,\n'
    '    aptitude_asset=0.15,\n'
    '    authority_liability=0.15,\n'
    '    authority_asset=0.15,\n'
    '    alliance_liability=0.15,\n'
    '    alliance_asset=0.15,\n'
    '    attitude_liability=0.45,\n'
    '    attitude_asset=0.15,\n'
    ')',
)


# ═══════════════════════════════════════════════════════════════════════════
# 3. engine/data/validate.py
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "engine/data/validate.py",
    'check("State count is 47", n == 47, f"got {n}")',
    'check("State count is 57", n == 57, f"got {n}")',
)
edit(
    "engine/data/validate.py",
    'check("Aptitude count = 6",  dim_counts.get("Aptitude",  0) == 6,  f"got {dim_counts.get(\'Aptitude\',0)}")\n'
    'check("Authority count = 18", dim_counts.get("Authority", 0) == 18, f"got {dim_counts.get(\'Authority\',0)}")\n'
    'check("Alliance count = 6",  dim_counts.get("Alliance",  0) == 6,  f"got {dim_counts.get(\'Alliance\',0)}")\n'
    'check("Attitude count = 17", dim_counts.get("Attitude",  0) == 17, f"got {dim_counts.get(\'Attitude\',0)}")',
    'check("Aptitude count = 7",  dim_counts.get("Aptitude",  0) == 7,  f"got {dim_counts.get(\'Aptitude\',0)}")\n'
    'check("Authority count = 22", dim_counts.get("Authority", 0) == 22, f"got {dim_counts.get(\'Authority\',0)}")\n'
    'check("Alliance count = 7",  dim_counts.get("Alliance",  0) == 7,  f"got {dim_counts.get(\'Alliance\',0)}")\n'
    'check("Attitude count = 21", dim_counts.get("Attitude",  0) == 21, f"got {dim_counts.get(\'Attitude\',0)}")',
)


# ═══════════════════════════════════════════════════════════════════════════
# 4. engine/resolution_families.py
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "engine/resolution_families.py",
    '# Verify count at import — must be 47\n'
    'assert len(STATE_RESOLUTION_FAMILY) == 47, (\n'
    '    f"STATE_RESOLUTION_FAMILY has {len(STATE_RESOLUTION_FAMILY)} entries, expected 47"\n'
    ')',
    '# Verify count at import — must be 57\n'
    'assert len(STATE_RESOLUTION_FAMILY) == 57, (\n'
    '    f"STATE_RESOLUTION_FAMILY has {len(STATE_RESOLUTION_FAMILY)} entries, expected 57"\n'
    ')',
)
edit(
    "engine/resolution_families.py",
    '    "leadership_deafness":              "directional",\n}',
    '    "leadership_deafness":              "directional",\n\n'
    '    # ── Taxonomy expansion (Session 67) — DRAFT, pending Gemini review ──────────\n'
    '    "invisible_performance_management":  "structural",\n'
    '    "compression_crisis":                "investigative",\n'
    '    "sequential_decision_blindness":     "investigative",\n'
    '    "disparate_impact_architecture":     "investigative",\n'
    '    "planning_authority_gap":            "structural",\n'
    '    "distributed_culture_fragmentation": "directional",\n'
    '    "wellbeing_theater":                 "directional",\n'
    '    "human_displacement_anxiety":        "directional",\n'
    '    "motivational_architecture_failure": "directional",\n'
    '    "cultural_overtime":                 "investigative",\n'
    '}',
)


# ═══════════════════════════════════════════════════════════════════════════
# 5. engine/data/salience.py
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "engine/data/salience.py",
    '    "culture_drift": {  # Tier 2 v18: authority secondary 2.5->1.0; v19 revert: attitude primary 1.85->2.5\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
    '    },',
    '    "culture_drift": {  # Tier 2 v18: authority secondary 2.5->1.0; v19 revert: attitude primary 1.85->2.5\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
    '    },\n\n'
    '    # ── TAXONOMY EXPANSION (Session 67) — DRAFT, pending Gemini review ──────────\n'
    '    # Seeded per the three-tier rule above from each state\'s draft signal_weight in\n'
    '    # engine/data/states.py; secondary bumps mirror that state\'s dimensional_vector\n'
    '    # secondary-field elevation.\n'
    '    "invisible_performance_management": {  # medium tier, primary only\n'
    '        "aptitude_liability": 2.5, "aptitude_asset": 2.5,\n'
    '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
    '    },\n'
    '    "compression_crisis": {  # medium tier, primary only\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
    '    },\n'
    '    "sequential_decision_blindness": {  # high tier, primary only\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
    '    },\n'
    '    "disparate_impact_architecture": {  # high tier, primary only\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
    '    },\n'
    '    "planning_authority_gap": {  # low tier, alliance secondary 2.5->1.0\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
    '        "alliance_liability": 1.0, "alliance_asset": 1.0,\n'
    '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
    '    },\n'
    '    "distributed_culture_fragmentation": {  # medium tier, attitude secondary 2.5->1.0\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
    '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
    '        "attitude_liability": 1.0, "attitude_asset": 1.0,\n'
    '    },\n'
    '    "wellbeing_theater": {  # cluster tier (C-Culture), authority secondary 2.5->1.0\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
    '    },\n'
    '    "human_displacement_anxiety": {  # medium tier, primary only\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
    '    },\n'
    '    "motivational_architecture_failure": {  # medium tier, primary only\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
    '    },\n'
    '    "cultural_overtime": {  # medium tier, primary only\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
    '    },',
)


# ═══════════════════════════════════════════════════════════════════════════
# 6. engine/checkpoint.py
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "engine/checkpoint.py",
    '# Maximum entropy: uniform distribution across all 47 states\n'
    '# Spec references 45 states (documentation artifact); confirmed count is 47.\n'
    'MAX_ENTROPY: float = log2(len(STATE_PROFILES))  # ≈ 5.554 bits',
    '# Maximum entropy: uniform distribution across all 57 states\n'
    '# Spec references 45 states (documentation artifact); confirmed count is 57\n'
    '# (47 locked Session 5, +10 taxonomy expansion Session 65/67).\n'
    'MAX_ENTROPY: float = log2(len(STATE_PROFILES))  # ≈ 5.833 bits',
)


# ═══════════════════════════════════════════════════════════════════════════
# 7. engine/friction_tax.py
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "engine/friction_tax.py",
    '    "the_broken_compass":               None,  # CALIBRATION TARGET\n}',
    '    "the_broken_compass":               None,  # CALIBRATION TARGET\n\n'
    '    # ── Taxonomy expansion (Session 67) ──────────────────────────────────────\n'
    '    "invisible_performance_management":  None,  # CALIBRATION TARGET\n'
    '    "compression_crisis":                None,  # CALIBRATION TARGET\n'
    '    "sequential_decision_blindness":     None,  # CALIBRATION TARGET\n'
    '    "disparate_impact_architecture":     None,  # CALIBRATION TARGET\n'
    '    "planning_authority_gap":            None,  # CALIBRATION TARGET\n'
    '    "distributed_culture_fragmentation": None,  # CALIBRATION TARGET\n'
    '    "wellbeing_theater":                 None,  # CALIBRATION TARGET\n'
    '    "human_displacement_anxiety":        None,  # CALIBRATION TARGET\n'
    '    "motivational_architecture_failure": None,  # CALIBRATION TARGET\n'
    '    "cultural_overtime":                 None,  # CALIBRATION TARGET\n'
    '}',
)


# ═══════════════════════════════════════════════════════════════════════════
# 8. engine/test_suite.py
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "engine/test_suite.py",
    "Phase 1 minimum: 3 profiles per state × 47 states = 141 test profiles.\n"
    "(Spec references 45 states × 3 = 135; confirmed count is 47.)",
    "Phase 1 minimum: 3 profiles per state × 57 states = 171 test profiles.\n"
    "(Spec references 45 states × 3 = 135; confirmed count is 57 as of Session 67\n"
    "taxonomy expansion, up from 47 locked Session 5.)",
)


# ═══════════════════════════════════════════════════════════════════════════
# 9. CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "- `engine/data/states.py` is the authoritative state registry — 47 states",
    "- `engine/data/states.py` is the authoritative state registry — 57 states",
)
edit(
    "CLAUDE.md",
    "| Engine state count | 47 (locked) |",
    "| Engine state count | 57 (locked) |",
)
edit(
    "CLAUDE.md",
    "| Test suite minimum (Phase 1) | 141 profiles across 47 states |",
    "| Test suite minimum (Phase 1) | 171 profiles across 57 states |",
)
edit(
    "CLAUDE.md",
    "| Shannon Entropy max (47 states) | 5.55 bits |",
    "| Shannon Entropy max (57 states) | 5.83 bits |",
)


# ═══════════════════════════════════════════════════════════════════════════
# 10. Published book copy
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "web/content/book/methodology/symptoms-states-and-why-the-distinction-matters.md",
    "forty-seven institutional states",
    "fifty-seven institutional states",
)


# ---------------------------------------------------------------------------

def apply(dry_run: bool):
    changed_files: dict[str, str] = {}
    errors = []

    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = changed_files.get(rel_path)
        if text is None:
            if not path.exists():
                errors.append(f"MISSING FILE: {rel_path}")
                continue
            text = path.read_text(encoding="utf-8")

        count = text.count(old)
        if count != 1:
            errors.append(
                f"{rel_path}: expected 1 match, found {count}\n"
                f"  --- anchor (first 120 chars) ---\n  {old[:120]!r}"
            )
            continue

        changed_files[rel_path] = text.replace(old, new, 1)

    print("=" * 72)
    print(f"TAXONOMY EXPANSION PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
    print("=" * 72)
    print(f"Files touched: {len(changed_files)}")
    for rel_path in changed_files:
        print(f"  - {rel_path}")

    if errors:
        print("\nERRORS — nothing written:" if not dry_run else "\nERRORS — would fail on --write:")
        for e in errors:
            print(f"\n[ERROR] {e}")
        if not dry_run:
            sys.exit(1)
        return

    if dry_run:
        print("\nDry run OK — all anchors matched exactly once. No files written.")
        return

    for rel_path, text in changed_files.items():
        (REPO_ROOT / rel_path).write_text(text, encoding="utf-8")
    print("\nAll files written.")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    apply(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
