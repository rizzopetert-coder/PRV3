"""
PRV3 Data Layer — Section I Validation
Run after any change to the data layer to verify structural integrity.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from engine.data.states import (
    STATE_PROFILES, CLUSTERS, BASELINE_VALUE, DIMENSIONAL_FIELDS,
    SEVERITY_TIERS, SIGNAL_WEIGHTS, CLUSTER_IDS,
    LIABILITY_CATEGORIES, ASSET_DOMAINS,
)
from engine.data.questions import (
    QUESTION_LIBRARY, CORE_SEQUENCE_IDS, SEVERITY_FOLLOW_ON_IDS,
)
from engine.data.intake import (
    PRIOR_ADJUSTERS, PRIOR_ADJUSTER_INDEX, AXIS_MODIFIERS,
    ROLE_COEFFICIENTS, INTAKE_FIELDS, CALIBRATION_TARGET,
)
from engine.data.jurisdiction import (
    JURISDICTION_TABLE, resolve_jurisdiction_flags,
)

PASS = []
FAIL = []

def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Data Layer — Section I Validation")
print("=" * 64)


# ── State profiles ─────────────────────────────────────────────────────────────
print("\nSTATE PROFILES")

n = len(STATE_PROFILES)
print(f"  Total states: {n}")
check("State count is 58", n == 58, f"got {n}")

# Dimensional vectors all at baseline
bad_vectors = [
    sid for sid, p in STATE_PROFILES.items()
    if any(getattr(p.dimensional_vector, f) != BASELINE_VALUE for f in DIMENSIONAL_FIELDS)
]
check("All dimensional vectors at 0.25 baseline", not bad_vectors,
      f"non-baseline: {bad_vectors}")

# signal_weight values
bad_sw = [sid for sid, p in STATE_PROFILES.items() if p.signal_weight not in SIGNAL_WEIGHTS]
check("All signal_weight values valid", not bad_sw, f"invalid: {bad_sw}")

# cluster_id values
bad_cl = [sid for sid, p in STATE_PROFILES.items()
          if p.cluster_id is not None and p.cluster_id not in CLUSTER_IDS]
check("All cluster_id values valid", not bad_cl, f"invalid: {bad_cl}")

# States with cluster signal_weight must have a cluster_id
bad_cw = [sid for sid, p in STATE_PROFILES.items()
          if p.signal_weight == "cluster" and p.cluster_id is None]
check("All cluster-weight states have cluster_id", not bad_cw, f"missing: {bad_cw}")

# severity_range tiers
bad_sev = [sid for sid, p in STATE_PROFILES.items()
           if p.severity_range.min not in SEVERITY_TIERS
           or p.severity_range.max not in SEVERITY_TIERS]
check("All severity_range tier values valid", not bad_sev, f"invalid: {bad_sev}")

# severity min <= max (using tier ordering)
tier_order = {t: i for i, t in enumerate(SEVERITY_TIERS)}
bad_order = [sid for sid, p in STATE_PROFILES.items()
             if tier_order[p.severity_range.min] > tier_order[p.severity_range.max]]
check("All severity_range min <= max", not bad_order, f"inverted: {bad_order}")

# liability_axes values
bad_la = []
for sid, p in STATE_PROFILES.items():
    for ax in p.liability_axes:
        if ax not in LIABILITY_CATEGORIES:
            bad_la.append(f"{sid}:{ax}")
check("All liability_axes values from framework", not bad_la, f"invalid: {bad_la}")

# asset_axes values
bad_aa = []
for sid, p in STATE_PROFILES.items():
    for ax in p.asset_axes:
        if ax not in ASSET_DOMAINS:
            bad_aa.append(f"{sid}:{ax}")
check("All asset_axes values from framework", not bad_aa, f"invalid: {bad_aa}")

# resolution_family not empty
bad_rf = [sid for sid, p in STATE_PROFILES.items() if not p.resolution_family]
check("All resolution_family values present", not bad_rf, f"empty: {bad_rf}")

# Clusters
print("\n  Cluster membership:")
for cid, members in CLUSTERS.items():
    states_in_profile = [s for s in members if s in STATE_PROFILES]
    print(f"    {cid}: {members}")
    check(f"Cluster {cid} members exist in STATE_PROFILES",
          len(states_in_profile) == len(members),
          f"missing: {set(members)-set(states_in_profile)}")

# Dimension counts
dim_counts = {}
for p in STATE_PROFILES.values():
    d = p.primary_dimension
    dim_counts[d] = dim_counts.get(d, 0) + 1
print(f"\n  States per dimension: {dim_counts}")
check("Aptitude count = 7",  dim_counts.get("Aptitude",  0) == 7,  f"got {dim_counts.get('Aptitude',0)}")
check("Authority count = 22", dim_counts.get("Authority", 0) == 22, f"got {dim_counts.get('Authority',0)}")
check("Alliance count = 7",  dim_counts.get("Alliance",  0) == 7,  f"got {dim_counts.get('Alliance',0)}")
check("Attitude count = 22", dim_counts.get("Attitude",  0) == 22, f"got {dim_counts.get('Attitude',0)}")


# ── Question library ───────────────────────────────────────────────────────────
print("\nQUESTION LIBRARY")
print(f"  Questions registered: {len(QUESTION_LIBRARY)} (expected 0 at this build stage)")
check("Question library schema importable", True)


# ── Intake tables ──────────────────────────────────────────────────────────────
print("\nINTAKE TABLES")

# Prior adjusters
print(f"  Prior adjusters: {len(PRIOR_ADJUSTERS)}")
# Prior adjuster "none" event existence/multiplier checks removed this
# session (Mechanism 1 deprecation follow-up, Priority Queue item 7) --
# both tested deprecated scoring-mechanism semantics with zero live
# consumer (engine/output_synthesis.py's PRIOR_ADJUSTER_INDEX usage
# explicitly skips "none" and never reads .multiplier). Referential-
# integrity check below kept -- different in kind, still useful
# regardless of Mechanism 1's live/dormant status. See Decision Register.

# All elevated state_ids in prior adjusters exist in STATE_PROFILES
bad_pa = []
for adj in PRIOR_ADJUSTERS:
    for sid in adj.elevated_states:
        if sid not in STATE_PROFILES:
            bad_pa.append(f"{adj.event_id}:{sid}")
check("All prior adjuster state_ids exist in STATE_PROFILES", not bad_pa, f"missing: {bad_pa}")

# Calibration targets are None
cal_tgt_adjusters = [a.event_id for a in PRIOR_ADJUSTERS if a.multiplier is CALIBRATION_TARGET]
print(f"  Prior adjusters with CALIBRATION_TARGET multiplier: {cal_tgt_adjusters}")

# Role coefficients
roles_defined = list(ROLE_COEFFICIENTS.keys())
print(f"  Principal roles with coefficients: {roles_defined}")
check("'Other' role coefficient exists (LOCKED neutral baseline)", "Other" in ROLE_COEFFICIENTS)

# All coefficient tables cover all 8 fields
for role, coeff_map in ROLE_COEFFICIENTS.items():
    bad_fields = [f for f in DIMENSIONAL_FIELDS if f not in coeff_map]
    check(f"Role '{role}' coefficients cover all 8 fields", not bad_fields,
          f"missing fields: {bad_fields}")

# Axis modifiers
print(f"  Axis modifiers: {len(AXIS_MODIFIERS)}")
cal_tgt_mods = [m.modifier_id for m in AXIS_MODIFIERS if m.multiplier is CALIBRATION_TARGET]
print(f"  Axis modifiers with CALIBRATION_TARGET: {cal_tgt_mods}")


# ── Jurisdiction table ─────────────────────────────────────────────────────────
print("\nJURISDICTION TABLE")
print(f"  Jurisdictions: {len(JURISDICTION_TABLE)}")
check("51 jurisdictions (50 states + DC)", len(JURISDICTION_TABLE) == 51,
      f"got {len(JURISDICTION_TABLE)}")

# Transparency True jurisdictions
transparency_true = [jid for jid, j in JURISDICTION_TABLE.items() if j.transparency]
print(f"  Transparency = True: {sorted(transparency_true)}")
check("CA transparency = True", JURISDICTION_TABLE["CA"].transparency is True)
check("CO transparency = True", JURISDICTION_TABLE["CO"].transparency is True)
check("NY transparency = True", JURISDICTION_TABLE["NY"].transparency is True)
check("WA transparency = True", JURISDICTION_TABLE["WA"].transparency is True)
check("IL transparency = True", JURISDICTION_TABLE["IL"].transparency is True)
check("MA transparency = True", JURISDICTION_TABLE["MA"].transparency is True)
check("TX transparency = False", JURISDICTION_TABLE["TX"].transparency is False)

# retaliation and procedural are all None
bad_ret = [jid for jid, j in JURISDICTION_TABLE.items() if j.retaliation is not None]
bad_pro = [jid for jid, j in JURISDICTION_TABLE.items() if j.procedural is not None]
check("All retaliation values = None (legal review pending)", not bad_ret, f"non-null: {bad_ret}")
check("All procedural values = None (legal review pending)", not bad_pro, f"non-null: {bad_pro}")

# resolve_jurisdiction_flags — single state
flags_tx = resolve_jurisdiction_flags(["TX"])
check("TX single-jurisdiction: transparency False", flags_tx["transparency"] is False)
check("TX single-jurisdiction: retaliation None",  flags_tx["retaliation"]  is None)
check("TX single-jurisdiction: multi_state False",  not flags_tx["multi_state_flag"])

# resolve_jurisdiction_flags — multi-state with high-regulation
flags_multi = resolve_jurisdiction_flags(["TX", "CA", "FL", "OH", "NY", "PA"])
check("Multi-state (6 jurisdictions): multi_state_flag True", flags_multi["multi_state_flag"])
check("Multi-state with CA+NY: transparency True", flags_multi["transparency"] is True)

# resolve_jurisdiction_flags — empty
flags_empty = resolve_jurisdiction_flags([])
check("Empty jurisdiction list: returns False/None defaults", not flags_empty["transparency"])


# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\nAll checks passed. Data layer is structurally valid.")
print("=" * 64)

sys.exit(1 if FAIL else 0)
