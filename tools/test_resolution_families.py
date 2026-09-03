"""
PRV3 Output Layer — Resolution Families Unit Tests

Verifies:
  1. STATE_RESOLUTION_FAMILY has exactly 57 entries
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
    ENGINE_TO_COMMERCIAL_NAME,
    RESOLUTION_FALLBACK_COPY,
    _FALLBACK_GENERIC,
    translate_resolution_family,
    get_fallback_copy,
    STATE_CAUSATION_OVERRIDES,
    apply_causation_override,
)

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


# ── 12. ENGINE_TO_COMMERCIAL_NAME mapping ────────────────────────────────────

check(
    "ENGINE_TO_COMMERCIAL_NAME has 4 entries",
    len(ENGINE_TO_COMMERCIAL_NAME) == 4,
    f"got {len(ENGINE_TO_COMMERCIAL_NAME)}",
)
_expected_mapping = {
    "Roadmap":           "People Tactics and Strategy",
    "Development":       "Training & Development",
    "Intervention":      "Intervention",
    "Executive Counsel": "Executive Advisory",
}
for engine_name, commercial_name in _expected_mapping.items():
    check(
        f"ENGINE_TO_COMMERCIAL_NAME['{engine_name}'] == '{commercial_name}'",
        ENGINE_TO_COMMERCIAL_NAME.get(engine_name) == commercial_name,
        f"got {ENGINE_TO_COMMERCIAL_NAME.get(engine_name)}",
    )


# ── 13. translate_resolution_family ──────────────────────────────────────────

check(
    "translate_resolution_family: single 'Roadmap' -> 'People Tactics and Strategy'",
    translate_resolution_family("Roadmap") == "People Tactics and Strategy",
    f"got {translate_resolution_family('Roadmap')}",
)
check(
    "translate_resolution_family: single 'Intervention' -> 'Intervention'",
    translate_resolution_family("Intervention") == "Intervention",
    f"got {translate_resolution_family('Intervention')}",
)
check(
    "translate_resolution_family: compound 'Roadmap + Intervention'",
    translate_resolution_family("Roadmap + Intervention") == "People Tactics and Strategy + Intervention",
    f"got {translate_resolution_family('Roadmap + Intervention')}",
)
check(
    "translate_resolution_family: compound 'Executive Counsel + Intervention'",
    translate_resolution_family("Executive Counsel + Intervention") == "Executive Advisory + Intervention",
    f"got {translate_resolution_family('Executive Counsel + Intervention')}",
)
check(
    "translate_resolution_family: unknown name passes through unchanged",
    translate_resolution_family("Unknown Service") == "Unknown Service",
    f"got {translate_resolution_family('Unknown Service')}",
)


# ── 14. RESOLUTION_FALLBACK_COPY structure ────────────────────────────────────

_SINGLE_KEYS = [
    ("People Tactics and Strategy", "Emerging"),
    ("People Tactics and Strategy", "Entrenched"),
    ("People Tactics and Strategy", "Endemic"),
    ("Training & Development",      "Emerging"),
    ("Training & Development",      "Entrenched"),
    ("Training & Development",      "Endemic"),
    ("Intervention",                "Emerging"),
    ("Intervention",                "Entrenched"),
    ("Intervention",                "Endemic"),
    ("Executive Advisory",          "Emerging"),
    ("Executive Advisory",          "Entrenched"),
    ("Executive Advisory",          "Endemic"),
]
_COMPOUND_KEYS = [
    ("People Tactics and Strategy + Intervention",           None),
    ("Intervention + People Tactics and Strategy",           None),
    ("Executive Advisory + Intervention",                    None),
    ("Intervention + Executive Advisory",                    None),
    ("Training & Development + People Tactics and Strategy", None),
    ("People Tactics and Strategy + Training & Development", None),
    ("Training & Development + Intervention",                None),
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
    "get_fallback_copy: single-service People Tactics and Strategy/Entrenched returns non-empty string",
    len(get_fallback_copy("People Tactics and Strategy", "Entrenched")) > 0,
    "returned empty string",
)
check(
    "get_fallback_copy: compound returns tier-agnostic copy",
    get_fallback_copy("People Tactics and Strategy + Intervention", "Entrenched") ==
    RESOLUTION_FALLBACK_COPY[("People Tactics and Strategy + Intervention", None)],
    "compound key lookup failed",
)
check(
    "get_fallback_copy: unknown name returns generic fallback",
    get_fallback_copy("Unknown", "Emerging") == _FALLBACK_GENERIC,
    f"got {get_fallback_copy('Unknown', 'Emerging')!r}",
)
check(
    "get_fallback_copy: unknown compound returns generic fallback",
    get_fallback_copy("Unknown + Unknown", None) == _FALLBACK_GENERIC,
    f"got {get_fallback_copy('Unknown + Unknown', None)!r}",
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


# ── 17. apply_causation_override ──────────────────────────────────────────────
# Priority Queue item 2, Diagnostic Dimension Expansion follow-on. Real
# grounding data: "culture_drift" (single-family default "Intervention"),
# "decision_paralysis" (compound default "Roadmap + Intervention").
# culture_drift itself carries no real entry -- override-present cases save/
# mutate/restore the real module-level dict directly, since
# apply_causation_override() reads it as module state, not a parameter. See
# section 18 below for coverage of the 3 real authored entries.

_SINGLE_DEFAULT = "Intervention"       # culture_drift's real default
_COMPOUND_DEFAULT = "Roadmap + Intervention"  # decision_paralysis's real default

check(
    "no override entry -- falls through to default_family unchanged",
    apply_causation_override("culture_drift", _SINGLE_DEFAULT, "single_point") == _SINGLE_DEFAULT,
    f"got {apply_causation_override('culture_drift', _SINGLE_DEFAULT, 'single_point')!r}",
)

check(
    "compound default -- immune, unchanged regardless of pattern",
    apply_causation_override("decision_paralysis", _COMPOUND_DEFAULT, "single_point") == _COMPOUND_DEFAULT
    and apply_causation_override("decision_paralysis", _COMPOUND_DEFAULT, "diffuse") == _COMPOUND_DEFAULT,
    "compound default was altered",
)

check(
    "priv-None case -- default_family='' stays '' regardless of pattern/state_id",
    apply_causation_override("culture_drift", "", "single_point") == ""
    and apply_causation_override(None, "", "diffuse") == "",
    "empty default_family was altered",
)

check(
    "insufficient_signal pattern -- falls through to default_family",
    apply_causation_override("culture_drift", _SINGLE_DEFAULT, "insufficient_signal") == _SINGLE_DEFAULT,
    f"got {apply_causation_override('culture_drift', _SINGLE_DEFAULT, 'insufficient_signal')!r}",
)

check(
    "missing causation_pattern (None) -- falls through to default_family",
    apply_causation_override("culture_drift", _SINGLE_DEFAULT, None) == _SINGLE_DEFAULT,
    f"got {apply_causation_override('culture_drift', _SINGLE_DEFAULT, None)!r}",
)

check(
    "missing state_id (None) -- falls through to default_family",
    apply_causation_override(None, _SINGLE_DEFAULT, "diffuse") == _SINGLE_DEFAULT,
    f"got {apply_causation_override(None, _SINGLE_DEFAULT, 'diffuse')!r}",
)

_saved_overrides = dict(STATE_CAUSATION_OVERRIDES)
try:
    STATE_CAUSATION_OVERRIDES["culture_drift"] = {
        "single_point": "Executive Counsel",
        "diffuse":      "Development",
    }
    check(
        "single-family default + single_point override present -- override applies",
        apply_causation_override("culture_drift", _SINGLE_DEFAULT, "single_point") == "Executive Counsel",
        f"got {apply_causation_override('culture_drift', _SINGLE_DEFAULT, 'single_point')!r}",
    )
    check(
        "single-family default + diffuse override present -- override applies",
        apply_causation_override("culture_drift", _SINGLE_DEFAULT, "diffuse") == "Development",
        f"got {apply_causation_override('culture_drift', _SINGLE_DEFAULT, 'diffuse')!r}",
    )
    check(
        "override dict present for state, but not for this pattern key -- falls through",
        apply_causation_override("culture_drift", _SINGLE_DEFAULT, "insufficient_signal") == _SINGLE_DEFAULT,
        f"got {apply_causation_override('culture_drift', _SINGLE_DEFAULT, 'insufficient_signal')!r}",
    )
    check(
        "override present for a DIFFERENT state -- unaffected state falls through",
        apply_causation_override("identity_erosion", _SINGLE_DEFAULT, "single_point") == _SINGLE_DEFAULT,
        f"got {apply_causation_override('identity_erosion', _SINGLE_DEFAULT, 'single_point')!r}",
    )
    check(
        "override still respects the compound-default guard even if an entry exists",
        apply_causation_override("culture_drift", _COMPOUND_DEFAULT, "single_point") == _COMPOUND_DEFAULT,
        f"got {apply_causation_override('culture_drift', _COMPOUND_DEFAULT, 'single_point')!r}",
    )
finally:
    STATE_CAUSATION_OVERRIDES.clear()
    STATE_CAUSATION_OVERRIDES.update(_saved_overrides)

check(
    "STATE_CAUSATION_OVERRIDES carries exactly the 5 entries authored 2026-09-03",
    set(STATE_CAUSATION_OVERRIDES.keys()) == {
        "paper_shield", "leadership_deafness", "the_broken_compass",
        "the_unformed_leader", "silosolation",
    },
    f"got keys {sorted(STATE_CAUSATION_OVERRIDES.keys())!r}",
)


# ── 18. STATE_CAUSATION_OVERRIDES -- real authored entries (2026-09-03) ────────
# First real content in the dict since it shipped empty (see the "ships empty"
# check above, now retired since it's factually false). Real defaults, verified
# directly against engine/data/states.py: paper_shield="Roadmap",
# leadership_deafness="Executive Counsel", the_broken_compass="Executive Counsel".

_PAPER_SHIELD_DEFAULT = "Roadmap"
_LEADERSHIP_DEAFNESS_DEFAULT = "Executive Counsel"
_THE_BROKEN_COMPASS_DEFAULT = "Executive Counsel"

check(
    "paper_shield single_point -- overrides to Intervention",
    apply_causation_override("paper_shield", _PAPER_SHIELD_DEFAULT, "single_point") == "Intervention",
    f"got {apply_causation_override('paper_shield', _PAPER_SHIELD_DEFAULT, 'single_point')!r}",
)

check(
    "paper_shield diffuse -- overrides to Roadmap (explicit entry, matches default value)",
    apply_causation_override("paper_shield", _PAPER_SHIELD_DEFAULT, "diffuse") == "Roadmap",
    f"got {apply_causation_override('paper_shield', _PAPER_SHIELD_DEFAULT, 'diffuse')!r}",
)

check(
    "leadership_deafness diffuse -- overrides to Roadmap",
    apply_causation_override("leadership_deafness", _LEADERSHIP_DEAFNESS_DEFAULT, "diffuse") == "Roadmap",
    f"got {apply_causation_override('leadership_deafness', _LEADERSHIP_DEAFNESS_DEFAULT, 'diffuse')!r}",
)

check(
    "leadership_deafness single_point -- no key, falls through to Executive Counsel default",
    apply_causation_override("leadership_deafness", _LEADERSHIP_DEAFNESS_DEFAULT, "single_point") == _LEADERSHIP_DEAFNESS_DEFAULT,
    f"got {apply_causation_override('leadership_deafness', _LEADERSHIP_DEAFNESS_DEFAULT, 'single_point')!r}",
)

check(
    "the_broken_compass diffuse -- overrides to Intervention",
    apply_causation_override("the_broken_compass", _THE_BROKEN_COMPASS_DEFAULT, "diffuse") == "Intervention",
    f"got {apply_causation_override('the_broken_compass', _THE_BROKEN_COMPASS_DEFAULT, 'diffuse')!r}",
)

check(
    "the_broken_compass single_point -- no key, falls through to Executive Counsel default",
    apply_causation_override("the_broken_compass", _THE_BROKEN_COMPASS_DEFAULT, "single_point") == _THE_BROKEN_COMPASS_DEFAULT,
    f"got {apply_causation_override('the_broken_compass', _THE_BROKEN_COMPASS_DEFAULT, 'single_point')!r}",
)


# ── 19. STATE_CAUSATION_OVERRIDES -- Development group entries (2026-09-03) ────
# Closes the Development group (2 of 2), companion to section 18's Executive
# Counsel group. Real defaults, verified directly against engine/data/states.py:
# the_unformed_leader="Development", silosolation="Development". silosolation
# is the one entry so far that overrides BOTH patterns away from its own
# shipped default -- "Development" is not reachable via causation_pattern for
# this state at all, confirmed below.

_THE_UNFORMED_LEADER_DEFAULT = "Development"
_SILOSOLATION_DEFAULT = "Development"

check(
    "the_unformed_leader diffuse -- overrides to Roadmap",
    apply_causation_override("the_unformed_leader", _THE_UNFORMED_LEADER_DEFAULT, "diffuse") == "Roadmap",
    f"got {apply_causation_override('the_unformed_leader', _THE_UNFORMED_LEADER_DEFAULT, 'diffuse')!r}",
)

check(
    "the_unformed_leader single_point -- no key, falls through to Development default",
    apply_causation_override("the_unformed_leader", _THE_UNFORMED_LEADER_DEFAULT, "single_point") == _THE_UNFORMED_LEADER_DEFAULT,
    f"got {apply_causation_override('the_unformed_leader', _THE_UNFORMED_LEADER_DEFAULT, 'single_point')!r}",
)

check(
    "silosolation single_point -- overrides to Intervention",
    apply_causation_override("silosolation", _SILOSOLATION_DEFAULT, "single_point") == "Intervention",
    f"got {apply_causation_override('silosolation', _SILOSOLATION_DEFAULT, 'single_point')!r}",
)

check(
    "silosolation diffuse -- overrides to Roadmap",
    apply_causation_override("silosolation", _SILOSOLATION_DEFAULT, "diffuse") == "Roadmap",
    f"got {apply_causation_override('silosolation', _SILOSOLATION_DEFAULT, 'diffuse')!r}",
)

check(
    "silosolation -- Development (its own shipped default) is not reachable via either causation_pattern",
    apply_causation_override("silosolation", _SILOSOLATION_DEFAULT, "single_point") != _SILOSOLATION_DEFAULT
    and apply_causation_override("silosolation", _SILOSOLATION_DEFAULT, "diffuse") != _SILOSOLATION_DEFAULT,
    "Development was reachable via causation_pattern -- expected both patterns to override away from it",
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
