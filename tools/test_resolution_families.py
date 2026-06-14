"""
PRV3 Output Layer — Resolution Families Unit Tests

Verifies:
  1. STATE_RESOLUTION_FAMILY has exactly 47 entries
  2. All state IDs match the engine state registry
  3. All family values are valid (structural/developmental/investigative/directional)
  4. All four families have at least one state assigned
  5. RESOLUTION_FAMILY_DESCRIPTIONS has all four families
  6. get_family: returns correct family dict for a known state
  7. get_family: fallback to structural for unknown state
  8. get_primary_family: returns first state's family
  9. get_primary_family: returns structural for empty list
  10. get_all_families: deduplicated, preserves order of first occurrence
  11. No service names appear in family descriptions (NO service names in output)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.resolution_families import (
    STATE_RESOLUTION_FAMILY,
    RESOLUTION_FAMILY_DESCRIPTIONS,
    ENGINE_TO_COMMERCIAL_NAME,
    RESOLUTION_FALLBACK_COPY,
    _FALLBACK_GENERIC,
    get_family,
    get_primary_family,
    get_all_families,
    translate_resolution_family,
    get_fallback_copy,
)
from engine.data.states import STATE_PROFILES

PASS = []
FAIL = []


def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Resolution Families — Unit Tests")
print("=" * 64)


VALID_FAMILIES = {"structural", "developmental", "investigative", "directional"}
SERVICE_NAMES = {"formation", "practicum", "counsel", "navigation"}


# ── 1. 47 entries ─────────────────────────────────────────────────────────────

check(
    "STATE_RESOLUTION_FAMILY has 47 entries",
    len(STATE_RESOLUTION_FAMILY) == 47,
    f"got {len(STATE_RESOLUTION_FAMILY)}",
)


# ── 2. All state IDs match registry ───────────────────────────────────────────

registry_ids = set(STATE_PROFILES.keys())
family_ids = set(STATE_RESOLUTION_FAMILY.keys())
missing = registry_ids - family_ids
extra = family_ids - registry_ids

check(
    "All registry states covered in family map",
    len(missing) == 0,
    f"missing: {missing}",
)
check(
    "No extra IDs not in registry",
    len(extra) == 0,
    f"extra: {extra}",
)


# ── 3. All family values valid ────────────────────────────────────────────────

invalid_families = {
    sid: fid
    for sid, fid in STATE_RESOLUTION_FAMILY.items()
    if fid not in VALID_FAMILIES
}
check(
    "All family values in valid set",
    len(invalid_families) == 0,
    f"invalid: {invalid_families}",
)


# ── 4. All four families have at least one state ──────────────────────────────

assigned_families = set(STATE_RESOLUTION_FAMILY.values())
for fam in VALID_FAMILIES:
    check(
        f"Family '{fam}' has at least one state assigned",
        fam in assigned_families,
        f"'{fam}' has 0 states",
    )


# ── 5. RESOLUTION_FAMILY_DESCRIPTIONS has all four ────────────────────────────

for fam in VALID_FAMILIES:
    check(
        f"RESOLUTION_FAMILY_DESCRIPTIONS has '{fam}' key",
        fam in RESOLUTION_FAMILY_DESCRIPTIONS,
        f"missing key '{fam}'",
    )
    if fam in RESOLUTION_FAMILY_DESCRIPTIONS:
        check(
            f"RESOLUTION_FAMILY_DESCRIPTIONS[{fam}] has family_id field",
            RESOLUTION_FAMILY_DESCRIPTIONS[fam].get("family_id") == fam,
            f"family_id mismatch: {RESOLUTION_FAMILY_DESCRIPTIONS[fam].get('family_id')}",
        )


# ── 6. get_family: known state ────────────────────────────────────────────────

fam_dict = get_family("decision_paralysis")
check(
    "get_family('decision_paralysis') returns structural",
    fam_dict.get("family_id") == "structural",
    f"got family_id={fam_dict.get('family_id')}",
)
check(
    "get_family result has description field",
    "description" in fam_dict,
    "no description field",
)


# ── 7. get_family: unknown state fallback ────────────────────────────────────

fallback = get_family("not_a_real_state")
check(
    "get_family fallback returns structural for unknown state",
    fallback.get("family_id") == "structural",
    f"got {fallback.get('family_id')}",
)


# ── 8. get_primary_family: first state's family ───────────────────────────────

primary = get_primary_family(["the_exposed", "decision_paralysis"])
check(
    "get_primary_family returns family of first state",
    primary.get("family_id") == "investigative",
    f"expected investigative, got {primary.get('family_id')}",
)


# ── 9. get_primary_family: empty list ─────────────────────────────────────────

empty_primary = get_primary_family([])
check(
    "get_primary_family returns structural for empty list",
    empty_primary.get("family_id") == "structural",
    f"got {empty_primary.get('family_id')}",
)


# ── 10. get_all_families: deduplicated, order preserved ──────────────────────

all_fams = get_all_families(["decision_paralysis", "the_fracture", "the_exposed"])
all_fam_ids = [f["family_id"] for f in all_fams]

check(
    "get_all_families result has no duplicates",
    len(all_fam_ids) == len(set(all_fam_ids)),
    f"got {all_fam_ids}",
)
check(
    "get_all_families first entry is structural (first state is structural)",
    all_fam_ids[0] == "structural",
    f"got {all_fam_ids[0]}",
)
check(
    "get_all_families includes investigative for the_exposed",
    "investigative" in all_fam_ids,
    f"got {all_fam_ids}",
)

all_single = get_all_families(["decision_paralysis", "transition_paralysis"])
check(
    "get_all_families deduplicates same-family states",
    len(all_single) == 1,
    f"got {len(all_single)} families for 2 structural states",
)


# ── 11. No service names in family descriptions ───────────────────────────────

for fam_id, fam_dict in RESOLUTION_FAMILY_DESCRIPTIONS.items():
    desc_lower = fam_dict.get("description", "").lower()
    found_service_names = [sn for sn in SERVICE_NAMES if sn in desc_lower]
    check(
        f"No service names in {fam_id} description",
        len(found_service_names) == 0,
        f"found service names: {found_service_names}",
    )


# ── 12. ENGINE_TO_COMMERCIAL_NAME mapping ────────────────────────────────────

check(
    "ENGINE_TO_COMMERCIAL_NAME has 4 entries",
    len(ENGINE_TO_COMMERCIAL_NAME) == 4,
    f"got {len(ENGINE_TO_COMMERCIAL_NAME)}",
)
_expected_mapping = {
    "Roadmap":           "Groundwork",
    "Development":       "Development",
    "Intervention":      "First Call",
    "Executive Counsel": "Advisory",
}
for engine_name, commercial_name in _expected_mapping.items():
    check(
        f"ENGINE_TO_COMMERCIAL_NAME['{engine_name}'] == '{commercial_name}'",
        ENGINE_TO_COMMERCIAL_NAME.get(engine_name) == commercial_name,
        f"got {ENGINE_TO_COMMERCIAL_NAME.get(engine_name)}",
    )


# ── 13. translate_resolution_family ──────────────────────────────────────────

check(
    "translate_resolution_family: single 'Roadmap' -> 'Groundwork'",
    translate_resolution_family("Roadmap") == "Groundwork",
    f"got {translate_resolution_family('Roadmap')}",
)
check(
    "translate_resolution_family: single 'Intervention' -> 'First Call'",
    translate_resolution_family("Intervention") == "First Call",
    f"got {translate_resolution_family('Intervention')}",
)
check(
    "translate_resolution_family: compound 'Roadmap + Intervention'",
    translate_resolution_family("Roadmap + Intervention") == "Groundwork + First Call",
    f"got {translate_resolution_family('Roadmap + Intervention')}",
)
check(
    "translate_resolution_family: compound 'Executive Counsel + Intervention'",
    translate_resolution_family("Executive Counsel + Intervention") == "Advisory + First Call",
    f"got {translate_resolution_family('Executive Counsel + Intervention')}",
)
check(
    "translate_resolution_family: unknown name passes through unchanged",
    translate_resolution_family("Unknown Service") == "Unknown Service",
    f"got {translate_resolution_family('Unknown Service')}",
)


# ── 14. RESOLUTION_FALLBACK_COPY structure ────────────────────────────────────

_SINGLE_KEYS = [
    ("Groundwork",   "Emerging"),
    ("Groundwork",   "Entrenched"),
    ("Groundwork",   "Endemic"),
    ("Development",  "Emerging"),
    ("Development",  "Entrenched"),
    ("Development",  "Endemic"),
    ("First Call",   "Emerging"),
    ("First Call",   "Entrenched"),
    ("First Call",   "Endemic"),
    ("Advisory",     "Emerging"),
    ("Advisory",     "Entrenched"),
    ("Advisory",     "Endemic"),
]
_COMPOUND_KEYS = [
    ("Groundwork + First Call",   None),
    ("First Call + Groundwork",   None),
    ("Advisory + First Call",     None),
    ("First Call + Advisory",     None),
    ("Development + Groundwork",  None),
    ("Groundwork + Development",  None),
    ("Development + First Call",  None),
]
_all_expected_keys = _SINGLE_KEYS + _COMPOUND_KEYS

check(
    "RESOLUTION_FALLBACK_COPY has 19 entries (12 single + 7 compound)",
    len(RESOLUTION_FALLBACK_COPY) == 19,
    f"got {len(RESOLUTION_FALLBACK_COPY)}",
)
for key in _all_expected_keys:
    check(
        f"RESOLUTION_FALLBACK_COPY has key {key}",
        key in RESOLUTION_FALLBACK_COPY,
        f"missing key {key}",
    )


# ── 15. get_fallback_copy: lookups ────────────────────────────────────────────

check(
    "get_fallback_copy: single-service Groundwork/Entrenched returns non-empty string",
    len(get_fallback_copy("Groundwork", "Entrenched")) > 0,
    "returned empty string",
)
check(
    "get_fallback_copy: compound returns tier-agnostic copy",
    get_fallback_copy("Groundwork + First Call", "Entrenched") ==
    RESOLUTION_FALLBACK_COPY[("Groundwork + First Call", None)],
    "compound key lookup failed",
)
check(
    "get_fallback_copy: unknown name returns generic fallback",
    get_fallback_copy("Unknown", "Emerging") == _FALLBACK_GENERIC,
    f"got {get_fallback_copy('Unknown', 'Emerging')!r}",
)
check(
    "get_fallback_copy: unknown compound returns generic fallback",
    get_fallback_copy("Unknown + Advisory", None) == _FALLBACK_GENERIC,
    f"got {get_fallback_copy('Unknown + Advisory', None)!r}",
)


# ── 16. Fallback copy quality checks ─────────────────────────────────────────

_OLD_SERVICE_NAMES = {"formation", "practicum", "counsel", "navigation"}

for key, copy_str in RESOLUTION_FALLBACK_COPY.items():
    copy_lower = copy_str.lower()
    _found_old = [sn for sn in _OLD_SERVICE_NAMES if sn in copy_lower]
    check(
        f"No old service names in fallback copy {key[0]}",
        len(_found_old) == 0,
        f"found old names: {_found_old}",
    )
    check(
        f"No semicolons in fallback copy {key[0]}",
        ";" not in copy_str,
        "contains semicolon",
    )


# ── Results ───────────────────────────────────────────────────────────────────

print(f"\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  {f}")
else:
    print("All tests passed.")

sys.exit(0 if not FAIL else 1)
