"""Validate salience profile field counts and values."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.states import DIMENSIONAL_FIELDS
from engine.data.salience import SALIENCE_PROFILES

VALID_WEIGHTS = {2.5, 0.4}
errors = []

for sid, weights in SALIENCE_PROFILES.items():
    if set(weights.keys()) != set(DIMENSIONAL_FIELDS):
        errors.append(f"{sid}: wrong fields {set(weights.keys())}")
    for f, v in weights.items():
        if v not in VALID_WEIGHTS:
            errors.append(f"{sid}.{f}: invalid weight {v} (must be 2.5 or 0.4)")

if errors:
    print(f"[FAIL] {len(errors)} error(s):")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print(f"[PASS] {len(SALIENCE_PROFILES)} states validated.")
    print("  All entries: 8 fields, values in {2.5, 0.4}.")
    sys.exit(0)
