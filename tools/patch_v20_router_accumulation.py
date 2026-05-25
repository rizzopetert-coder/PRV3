"""
Patch: engine/accumulation.py — Two-Tier Hierarchical Router (v20)

Four targeted changes to accumulation.py:
  1. Insert _DIMENSION_TIE_PRIORITY, _DIMENSION_FIELD_MAP, identify_dominant_dimension()
     after compute_session_magnitude().
  2. Add dominant_dimension: Optional[str] = None to rank_states() signature.
  3. Filter STATE_PROFILES by dominant_dimension inside rank_states() body.
  4. Add use_router: bool = False to AccumulationEngine.rank(); call router when True.

Backward compatible: existing tests pass dominant_dimension=None (default) and
use_router=False (default) — full 47-state path preserved.

v20: Session 23, 2026-05-24.

Usage:
  python tools/patch_v20_router_accumulation.py --dry-run
  python tools/patch_v20_router_accumulation.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "accumulation.py"

# ── Change 1: insert constants + identify_dominant_dimension() ────────────────

OLD_1 = (
    'def compute_session_magnitude(accumulated: dict, fields: list) -> float:\n'
    '    """L2 norm of the accumulated session vector. Interpretable as session intensity."""\n'
    '    return math.sqrt(sum(accumulated.get(f, 0.0) ** 2 for f in fields))\n'
)

NEW_1 = (
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

# ── Change 2: rank_states() signature — add dominant_dimension ────────────────

OLD_2 = (
    'def rank_states(\n'
    '    accumulated_vector: dict,\n'
    '    salience_weights: Optional[dict] = None,\n'
    ') -> list:\n'
)

NEW_2 = (
    'def rank_states(\n'
    '    accumulated_vector: dict,\n'
    '    salience_weights: Optional[dict] = None,\n'
    '    dominant_dimension: Optional[str] = None,\n'
    ') -> list:\n'
)

# ── Change 3: rank_states() body — filter by dominant_dimension ───────────────

OLD_3 = (
    '    fields = list(DIMENSIONAL_FIELDS)\n'
    '    results = []\n'
    '    for sid, profile in STATE_PROFILES.items():\n'
)

NEW_3 = (
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

# ── Change 4: AccumulationEngine.rank() — add use_router ─────────────────────

OLD_4 = (
    '    def rank(self, salience_weights: Optional[dict] = None) -> list:\n'
    '        """\n'
    '        Return full state ranking sorted ascending by distance (1 - similarity).\n'
    '        Call after all answers have been applied.\n'
    '        salience_weights: pass SALIENCE_PROFILES from engine.data.salience to\n'
    '          activate weighted cosine mode. None = unweighted (default).\n'
    '        """\n'
    '        return rank_states(self.session.accumulated_vector, salience_weights)\n'
)

NEW_4 = (
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

CHANGES = [
    ("insert _DIMENSION_TIE_PRIORITY + _DIMENSION_FIELD_MAP + identify_dominant_dimension()", OLD_1, NEW_1),
    ("rank_states() signature: add dominant_dimension: Optional[str] = None",                 OLD_2, NEW_2),
    ("rank_states() body: filter profiles_to_rank by dominant_dimension",                     OLD_3, NEW_3),
    ("AccumulationEngine.rank(): add use_router: bool = False + router dispatch",             OLD_4, NEW_4),
]


def run(dry_run: bool):
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v20_router_accumulation.py — {mode}")
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
        print("Proposed changes:\n")
        print("  Change 1 — INSERT after compute_session_magnitude():")
        print("    _DIMENSION_TIE_PRIORITY: list = [\"Authority\", \"Aptitude\", \"Alliance\", \"Attitude\"]")
        print("    _DIMENSION_FIELD_MAP: dict = { 4-dimension field pair map }")
        print("    def identify_dominant_dimension(accumulated_vector: dict) -> tuple:")
        print("        Sums liability+asset per dimension, returns dominant dim + magnitude dict.")
        print("        Tie-break: Authority > Aptitude > Alliance > Attitude.")
        print()
        print("  Change 2 — rank_states() signature:")
        print("    OLD: def rank_states(accumulated_vector, salience_weights=None) -> list")
        print("    NEW: def rank_states(accumulated_vector, salience_weights=None,")
        print("                         dominant_dimension=None) -> list")
        print()
        print("  Change 3 — rank_states() body:")
        print("    OLD: for sid, profile in STATE_PROFILES.items():")
        print("    NEW: profiles_to_rank = (")
        print("             {sid: p for sid, p in STATE_PROFILES.items()")
        print("              if p.primary_dimension == dominant_dimension}")
        print("             if dominant_dimension is not None else STATE_PROFILES")
        print("         )")
        print("         for sid, profile in profiles_to_rank.items():")
        print()
        print("  Change 4 — AccumulationEngine.rank():")
        print("    OLD: def rank(self, salience_weights=None) -> list:")
        print("             return rank_states(accumulated_vector, salience_weights)")
        print("    NEW: def rank(self, salience_weights=None, use_router=False) -> list:")
        print("             if use_router:")
        print("                 dominant_dim, _ = identify_dominant_dimension(accumulated_vector)")
        print("                 return rank_states(accumulated_vector, salience_weights, dominant_dim)")
        print("             return rank_states(accumulated_vector, salience_weights)")
        print()
        print("  Backward compat: dominant_dimension=None and use_router=False preserve")
        print("  full 47-state path. All 402 existing tests unchanged.")
        print()
        for label, _, _ in validated:
            print(f"  [DRY-RUN] Would apply: {label}")
        print(f"\n[DRY-RUN COMPLETE] {len(validated)} change(s) validated. No file written.")
    else:
        for label, old, new in validated:
            text = text.replace(old, new, 1)
            print(f"  [APPLIED] {label}")
        TARGET.write_text(text, encoding="utf-8")
        print(f"\n[DONE] {TARGET} written. {len(validated)} change(s) applied.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
