#!/usr/bin/env python3
"""
PRV3 v10 Tier Standardization Patch -- Session 17
Three-tier global vector standardization across all 47 states.

HIGH  (11): primary=0.60, all others=0.10
MEDIUM(21): primary=0.45, all others=0.15
LOW/CLUSTER(15): primary=0.35, secondary=0.25, all others=0.15

Usage:
    python tools/patch_v10_tier_standardization.py --dry-run
    python tools/patch_v10_tier_standardization.py --write
"""

import argparse, re, sys
from pathlib import Path

BASE        = Path(__file__).parent.parent
STATES_PATH = BASE / "engine" / "data" / "states.py"

ALL_FIELDS = [
    "aptitude_liability",  "aptitude_asset",
    "authority_liability", "authority_asset",
    "alliance_liability",  "alliance_asset",
    "attitude_liability",  "attitude_asset",
]

# ── Vector builders ───────────────────────────────────────────────────────────

def high_vec(primary):
    v = {f: 0.10 for f in ALL_FIELDS}
    v[primary] = 0.60
    return v

def medium_vec(primary):
    v = {f: 0.15 for f in ALL_FIELDS}
    v[primary] = 0.45
    return v

def low_vec(primary, secondary):
    v = {f: 0.15 for f in ALL_FIELDS}
    v[primary]   = 0.35
    v[secondary] = 0.25
    return v

# ── Tier assignments ──────────────────────────────────────────────────────────
# Format: state_id -> (tier_label, vector_dict)

TIERS = {}

# HIGH TIER — 11 states — primary=0.60, others=0.10
for _sid, _prim in [
    ("built_to_fail",          "aptitude_liability"),
    ("the_paper_tiger",        "aptitude_liability"),
    ("the_founders_grip",      "authority_liability"),
    ("the_exposed",            "authority_liability"),
    ("hr_capture",             "authority_liability"),
    ("heard_and_ignored",      "authority_liability"),
    ("the_tolerated_violation","authority_liability"),
    ("the_unsolved_problem",   "authority_liability"),
    ("the_fracture",           "alliance_liability"),
    ("decision_blindness",     "alliance_liability"),
    ("the_untouchable",        "attitude_liability"),
]:
    TIERS[_sid] = ("HIGH", high_vec(_prim))

# MEDIUM TIER — 21 states — primary=0.45, others=0.15
for _sid, _prim in [
    ("the_undefined_role",         "aptitude_liability"),
    ("the_uninitiated",            "authority_liability"),
    ("leadership_continuity_risk", "authority_liability"),
    ("decision_paralysis",         "authority_liability"),
    ("the_policy_lag",             "authority_liability"),
    ("dueling_narratives",         "authority_liability"),
    ("transition_paralysis",       "authority_liability"),
    ("the_lost_map",               "authority_liability"),
    ("pay_exposure",               "authority_liability"),
    ("the_pay_fog",                "authority_liability"),
    ("the_second_close",           "alliance_liability"),
    ("silosolation",               "alliance_liability"),
    ("the_arbitrary_standard",     "alliance_liability"),
    ("the_diversity_ceiling",      "attitude_liability"),
    ("the_burned_credibility",     "attitude_liability"),
    ("invisible_burnout",          "attitude_liability"),
    ("the_basement_standard",      "attitude_liability"),
    ("the_inside_track",           "attitude_liability"),
    ("groundhog_day",              "attitude_liability"),
    ("the_wrong_reward",           "attitude_liability"),
    ("the_broken_compass",         "attitude_liability"),
]:
    TIERS[_sid] = ("MEDIUM", medium_vec(_prim))

# LOW/CLUSTER TIER — 15 states — primary=0.35, secondary=0.25, others=0.15
for _sid, _prim, _sec in [
    ("the_unformed_leader",              "aptitude_liability",  "attitude_liability"),
    ("the_overloaded_manager",           "aptitude_liability",  "authority_liability"),
    ("the_dormant_talent",               "aptitude_liability",  "attitude_liability"),
    ("the_unexamined_algorithm",         "authority_liability", "aptitude_liability"),
    ("paper_shield",                     "authority_liability", "alliance_liability"),
    ("invisible_influence_architecture", "authority_liability", "alliance_liability"),
    ("the_suppression_filter",           "alliance_liability",  "authority_liability"),
    ("narrative_lock",                   "attitude_liability",  "alliance_liability"),
    ("what_nobody_says",                 "attitude_liability",  "alliance_liability"),
    ("leadership_deafness",              "attitude_liability",  "alliance_liability"),
    ("culture_drift",                    "attitude_liability",  "authority_liability"),
    ("identity_erosion",                 "attitude_liability",  "alliance_liability"),
    ("the_culture_that_wasnt",           "attitude_liability",  "alliance_liability"),
    ("the_unreported_hazard",            "attitude_liability",  "alliance_liability"),
    ("the_unlocked_door",                "attitude_liability",  "alliance_liability"),
]:
    TIERS[_sid] = ("LOW/CLUSTER", low_vec(_prim, _sec))

assert len(TIERS) == 47, f"Tier table has {len(TIERS)} entries, expected 47"

# States that currently have STATE_PROFILES[...].dimensional_vector overrides in states.py.
# All others are auto-seeded by _profile() and need INSERT.
HAS_OVERRIDE = {
    "the_unformed_leader", "the_overloaded_manager", "the_dormant_talent",
    "the_founders_grip", "the_exposed", "hr_capture",
    "the_unexamined_algorithm", "heard_and_ignored", "the_tolerated_violation",
    "the_unsolved_problem", "paper_shield", "invisible_influence_architecture",
    "the_suppression_filter", "what_nobody_says", "leadership_deafness",
    "culture_drift", "identity_erosion", "the_culture_that_wasnt",
    "the_unreported_hazard", "the_unlocked_door", "narrative_lock",
}

# File-order list for dry-run display (matches states.py dimension ordering)
FILE_ORDER = [
    # Aptitude
    "the_unformed_leader", "the_overloaded_manager", "the_dormant_talent",
    "built_to_fail", "the_undefined_role", "the_paper_tiger",
    # Authority
    "the_founders_grip", "the_exposed", "the_uninitiated",
    "leadership_continuity_risk", "hr_capture", "decision_paralysis",
    "the_policy_lag", "the_unexamined_algorithm", "heard_and_ignored",
    "the_tolerated_violation", "dueling_narratives", "the_unsolved_problem",
    "transition_paralysis", "paper_shield", "the_lost_map",
    "invisible_influence_architecture", "pay_exposure", "the_pay_fog",
    # Alliance
    "the_fracture", "the_second_close", "silosolation",
    "the_suppression_filter", "the_arbitrary_standard", "decision_blindness",
    # Attitude
    "the_untouchable", "what_nobody_says", "leadership_deafness",
    "the_diversity_ceiling", "culture_drift", "identity_erosion",
    "the_culture_that_wasnt", "the_burned_credibility", "invisible_burnout",
    "the_basement_standard", "the_inside_track", "narrative_lock",
    "groundhog_day", "the_wrong_reward", "the_unreported_hazard",
    "the_unlocked_door", "the_broken_compass",
]

assert len(FILE_ORDER) == 47, f"FILE_ORDER has {len(FILE_ORDER)} entries, expected 47"
assert set(FILE_ORDER) == set(TIERS), "FILE_ORDER and TIERS keys don't match"

# ── Block helpers ─────────────────────────────────────────────────────────────

def format_block(state_id, vec):
    """Return the STATE_PROFILES[state_id].dimensional_vector = DimensionalVector(...) block."""
    lines = [f'STATE_PROFILES["{state_id}"].dimensional_vector = DimensionalVector(']
    for f in ALL_FIELDS:
        lines.append(f'    {f}={vec[f]:.2f},')
    lines.append(')')
    return '\n'.join(lines)

def find_override_span(content, state_id):
    """Return (start, end) of existing DimensionalVector override block for state_id."""
    m = re.search(
        r'STATE_PROFILES\["' + re.escape(state_id) + r'"\]\.dimensional_vector'
        r' = DimensionalVector\([^)]+\)',
        content, re.DOTALL
    )
    return (m.start(), m.end()) if m else (-1, -1)

def find_reg_close(content, state_id):
    """Return position immediately after the )) that closes _reg(_profile(...)) for state_id."""
    marker = f'    state_id="{state_id}",'
    idx = content.find(marker)
    if idx == -1:
        return -1
    pos = idx
    while pos < len(content) - 2:
        if content[pos] == '\n' and content[pos+1:pos+3] == '))':
            return pos + 3   # right after \n))
        pos += 1
    return -1

# ── Core logic ────────────────────────────────────────────────────────────────

def build_changes(content):
    """
    Build list of (start, end, new_text, state_id, tier, action) tuples.
    For UPDATEs: content[start:end] replaced by new_text.
    For INSERTs: new_text inserted at start (end == start).
    Returns (changes, errors).
    """
    changes, errors = [], []

    for state_id in FILE_ORDER:
        tier, vec = TIERS[state_id]
        new_block = format_block(state_id, vec)

        if state_id in HAS_OVERRIDE:
            start, end = find_override_span(content, state_id)
            if start == -1:
                errors.append(f"UPDATE anchor not found: {state_id}")
                continue
            changes.append((start, end, new_block, state_id, tier, "UPDATE"))
        else:
            pos = find_reg_close(content, state_id)
            if pos == -1:
                errors.append(f"INSERT anchor not found: {state_id}")
                continue
            changes.append((pos, pos, '\n' + new_block, state_id, tier, "INSERT"))

    return changes, errors

def apply_changes(content, changes):
    """Apply changes in reverse position order to avoid offset shifts."""
    ordered = sorted(changes, key=lambda c: c[0], reverse=True)
    result = content
    for start, end, new_text, *_ in ordered:
        result = result[:start] + new_text + result[end:]
    return result

def verify_all(content):
    """Check that every state's marker is present. Return list of missing state_ids."""
    return [sid for sid in TIERS
            if f'STATE_PROFILES["{sid}"].dimensional_vector' not in content]

# ── Dry-run display ───────────────────────────────────────────────────────────

def _vec_summary(tier, vec):
    if tier == "HIGH":
        pf = next(f for f, v in vec.items() if v == 0.60)
        return f"{pf}=0.60  |  others=0.10"
    if tier == "MEDIUM":
        pf = next(f for f, v in vec.items() if v == 0.45)
        return f"{pf}=0.45  |  others=0.15"
    # LOW/CLUSTER
    pf = next(f for f, v in vec.items() if v == 0.35)
    sf = next(f for f, v in vec.items() if v == 0.25)
    return f"{pf}=0.35  |  {sf}=0.25  |  others=0.15"

def print_dry_run(content, changes):
    change_map = {c[3]: c for c in changes}   # state_id -> change tuple

    SECTIONS = [
        ("APTITUDE  (6)",
         ["the_unformed_leader","the_overloaded_manager","the_dormant_talent",
          "built_to_fail","the_undefined_role","the_paper_tiger"]),
        ("AUTHORITY (18)",
         ["the_founders_grip","the_exposed","the_uninitiated","leadership_continuity_risk",
          "hr_capture","decision_paralysis","the_policy_lag","the_unexamined_algorithm",
          "heard_and_ignored","the_tolerated_violation","dueling_narratives",
          "the_unsolved_problem","transition_paralysis","paper_shield","the_lost_map",
          "invisible_influence_architecture","pay_exposure","the_pay_fog"]),
        ("ALLIANCE  (6)",
         ["the_fracture","the_second_close","silosolation",
          "the_suppression_filter","the_arbitrary_standard","decision_blindness"]),
        ("ATTITUDE  (17)",
         ["the_untouchable","what_nobody_says","leadership_deafness",
          "the_diversity_ceiling","culture_drift","identity_erosion",
          "the_culture_that_wasnt","the_burned_credibility","invisible_burnout",
          "the_basement_standard","the_inside_track","narrative_lock",
          "groundhog_day","the_wrong_reward","the_unreported_hazard",
          "the_unlocked_door","the_broken_compass"]),
    ]

    print()
    print("=" * 80)
    print("DRY RUN -- 47 STATE VECTOR CHANGES")
    print("Tiers: HIGH (0.60/0.10) | MEDIUM (0.45/0.15) | LOW/CLUSTER (0.35/0.25/0.15)")
    print("=" * 80)

    n = 0
    for section_title, states in SECTIONS:
        print(f"\n-- {section_title} " + "-" * (74 - len(section_title)))
        for sid in states:
            n += 1
            _, _, _, state_id, tier, action = change_map[sid]
            _, vec = TIERS[sid]
            summary = _vec_summary(tier, vec)
            print(f"  {n:2d}. {sid:<44} [{tier:<11}] {action:<6}  {summary}")

    print()
    print(f"Total: {n} states  |  UPDATEs: {sum(1 for c in changes if c[5]=='UPDATE')}"
          f"  |  INSERTs: {sum(1 for c in changes if c[5]=='INSERT')}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PRV3 v10 tier standardization")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write",   action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("PRV3 v10 Tier Standardization -- 47 states")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'WRITE'}")
    print("=" * 60)

    content = STATES_PATH.read_text(encoding='utf-8')
    changes, errors = build_changes(content)

    if errors:
        print("\nERRORS -- cannot proceed:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    if args.dry_run:
        print_dry_run(content, changes)
        print("DRY RUN complete -- no files written")
    else:
        result = apply_changes(content, changes)
        STATES_PATH.write_text(result, encoding='utf-8')
        verify = STATES_PATH.read_text(encoding='utf-8')
        missing = verify_all(verify)
        if missing:
            print(f"\nVERIFY FAILED -- markers missing after write: {missing}")
            sys.exit(1)
        print(f"\nWRITE complete -- all 47 state vectors updated")
        print(f"VERIFIED -- all 47 STATE_PROFILES markers present in file")

if __name__ == "__main__":
    main()
