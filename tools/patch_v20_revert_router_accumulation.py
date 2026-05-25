"""
Patch: engine/accumulation.py — revert Two-Tier Router additions (v20 revert)

Removes the four changes applied by patch_v20_router_accumulation.py:
  1. Remove _DIMENSION_TIE_PRIORITY, _DIMENSION_FIELD_MAP, identify_dominant_dimension()
  2. Remove dominant_dimension: Optional[str] = None from rank_states() signature
  3. Remove profiles_to_rank filter from rank_states() body
  4. Remove use_router: bool = False from AccumulationEngine.rank()

Restores full 47-state rank_states() path. states.py + salience.py reverts remain.

v20: Session 23, 2026-05-24.

Usage:
  python tools/patch_v20_revert_router_accumulation.py --dry-run
  python tools/patch_v20_revert_router_accumulation.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "accumulation.py"

# ── Revert 1: remove constants + identify_dominant_dimension() ────────────────

OLD_1 = (
    'def compute_session_magnitude(accumulated: dict, fields: list) -> float:\n'
    '    """L2 norm of the accumulated session vector. Interpretable as session intensity."""\n'
    '    return math.sqrt(sum(accumulated.get(f, 0.0) ** 2 for f in fields))\n'
    '\n'
    '\n'
    '_DIMENSION_TIE_PRIORITY: list = ["Authority", "Aptitude", "Alliance", "Attitude"]\n'
    '\n'
    '_DIMENSION_FIELD_MAP: dict = {\n'
    '    "Aptitude":  ("aptitude_liability",  "aptitude_asset"),\n'
    '    "Authority": ("authority_liability", "authority_asset"),\n'
    '    "Alliance":  ("alliance_liability",  "alliance_asset"),\n'
    '    "Attitude":  ("attitude_liability",  "attitude_asset"),\n'
    '}\n'
    '\n'
    '\n'
    'def identify_dominant_dimension(accumulated_vector: dict) -> tuple:\n'
    '    """\n'
    '    Identify the dimension with the highest summed magnitude in the accumulated\n'
    '    vector. Sums liability + asset per dimension. Tie-break order:\n'
    '    Authority > Aptitude > Alliance > Attitude.\n'
    '    Returns (dominant_dimension_name, {dim: magnitude} dict).\n'
    '    """\n'
    '    magnitudes = {\n'
    '        dim: (\n'
    '            accumulated_vector.get(lib_f, 0.0)\n'
    '            + accumulated_vector.get(asset_f, 0.0)\n'
    '        )\n'
    '        for dim, (lib_f, asset_f) in _DIMENSION_FIELD_MAP.items()\n'
    '    }\n'
    '    dominant = max(\n'
    '        _DIMENSION_TIE_PRIORITY,\n'
    '        key=lambda d: (magnitudes[d], -_DIMENSION_TIE_PRIORITY.index(d)),\n'
    '    )\n'
    '    return dominant, magnitudes\n'
)

NEW_1 = (
    'def compute_session_magnitude(accumulated: dict, fields: list) -> float:\n'
    '    """L2 norm of the accumulated session vector. Interpretable as session intensity."""\n'
    '    return math.sqrt(sum(accumulated.get(f, 0.0) ** 2 for f in fields))\n'
)

# ── Revert 2: rank_states() signature — remove dominant_dimension ─────────────

OLD_2 = (
    'def rank_states(\n'
    '    accumulated_vector: dict,\n'
    '    salience_weights: Optional[dict] = None,\n'
    '    dominant_dimension: Optional[str] = None,\n'
    ') -> list:\n'
)

NEW_2 = (
    'def rank_states(\n'
    '    accumulated_vector: dict,\n'
    '    salience_weights: Optional[dict] = None,\n'
    ') -> list:\n'
)

# ── Revert 3: rank_states() body — restore STATE_PROFILES.items() loop ────────

OLD_3 = (
    '    fields = list(DIMENSIONAL_FIELDS)\n'
    '    results = []\n'
    '    profiles_to_rank = (\n'
    '        {sid: p for sid, p in STATE_PROFILES.items()\n'
    '         if p.primary_dimension == dominant_dimension}\n'
    '        if dominant_dimension is not None\n'
    '        else STATE_PROFILES\n'
    '    )\n'
    '    for sid, profile in profiles_to_rank.items():\n'
)

NEW_3 = (
    '    fields = list(DIMENSIONAL_FIELDS)\n'
    '    results = []\n'
    '    for sid, profile in STATE_PROFILES.items():\n'
)

# ── Revert 4: AccumulationEngine.rank() — remove use_router ──────────────────

OLD_4 = (
    '    def rank(self, salience_weights: Optional[dict] = None, use_router: bool = False) -> list:\n'
    '        """\n'
    '        Return full state ranking sorted ascending by distance (1 - similarity).\n'
    '        Call after all answers have been applied.\n'
    '        salience_weights: pass SALIENCE_PROFILES from engine.data.salience to\n'
    '          activate weighted cosine mode. None = unweighted (default).\n'
    '        use_router: when True, calls identify_dominant_dimension() and restricts\n'
    '          ranking to states whose primary_dimension matches the dominant dimension.\n'
    '        """\n'
    '        if use_router:\n'
    '            dominant_dim, _ = identify_dominant_dimension(self.session.accumulated_vector)\n'
    '            return rank_states(self.session.accumulated_vector, salience_weights, dominant_dim)\n'
    '        return rank_states(self.session.accumulated_vector, salience_weights)\n'
)

NEW_4 = (
    '    def rank(self, salience_weights: Optional[dict] = None) -> list:\n'
    '        """\n'
    '        Return full state ranking sorted ascending by distance (1 - similarity).\n'
    '        Call after all answers have been applied.\n'
    '        salience_weights: pass SALIENCE_PROFILES from engine.data.salience to\n'
    '          activate weighted cosine mode. None = unweighted (default).\n'
    '        """\n'
    '        return rank_states(self.session.accumulated_vector, salience_weights)\n'
)

CHANGES = [
    ("remove _DIMENSION_TIE_PRIORITY + _DIMENSION_FIELD_MAP + identify_dominant_dimension()", OLD_1, NEW_1),
    ("rank_states() signature: remove dominant_dimension parameter",                          OLD_2, NEW_2),
    ("rank_states() body: restore full STATE_PROFILES.items() loop",                         OLD_3, NEW_3),
    ("AccumulationEngine.rank(): remove use_router parameter and router dispatch",            OLD_4, NEW_4),
]


def run(dry_run: bool):
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v20_revert_router_accumulation.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'=' * 72}\n")

    text = TARGET.read_text(encoding="utf-8")
    validated = []
    for label, old, new in CHANGES:
        if old not in text:
            print(f"[FAIL] '{label}' — old block not found. Aborting.")
            sys.exit(1)
        if text.count(old) > 1:
            print(f"[FAIL] '{label}' — old block not unique. Aborting.")
            sys.exit(1)
        validated.append((label, old, new))

    if dry_run:
        print("Reverts to apply:\n")
        for label, _, _ in validated:
            print(f"  [DRY-RUN] Would apply: {label}")
        print(f"\n  Outcome: full 47-state rank_states() path restored.")
        print(f"  states.py + salience.py reverts remain. questions.py Q20 retained.")
        print(f"\n[DRY-RUN COMPLETE] {len(validated)} revert(s) validated. No file written.")
    else:
        for label, old, new in validated:
            text = text.replace(old, new, 1)
            print(f"  [APPLIED] {label}")
        TARGET.write_text(text, encoding="utf-8")
        print(f"\n[DONE] {TARGET} written. {len(validated)} revert(s) applied.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
