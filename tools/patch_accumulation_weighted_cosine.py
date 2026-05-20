"""
Patch: engine/accumulation.py — weighted cosine similarity (Session 21)

Changes:
  1. File header: "Euclidean Distance" -> "Cosine Similarity" in section title
  2. New function: _weighted_cosine_similarity()
  3. rank_states(): wire salience_weights parameter into weighted path
  4. AccumulationEngine.rank(): update docstring

Usage:
  python tools/patch_accumulation_weighted_cosine.py --dry-run
  python tools/patch_accumulation_weighted_cosine.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "accumulation.py"


CHANGES = [
    # ── Change 1 — header docstring ──────────────────────────────────────────
    {
        "description": "File header: 'Euclidean Distance Calculation and State Ranking' -> 'Cosine Similarity and State Ranking'",
        "old": "II.4  Euclidean Distance Calculation and State Ranking",
        "new": "II.4  Cosine Similarity and State Ranking",
    },
    # ── Change 2 — insert _weighted_cosine_similarity after _cosine_similarity ─
    {
        "description": "Insert _weighted_cosine_similarity() after _cosine_similarity()",
        "old": (
            "def compute_session_magnitude(accumulated: dict, fields: list) -> float:\n"
            '    """L2 norm of the accumulated session vector. Interpretable as session intensity."""\n'
            "    return math.sqrt(sum(accumulated.get(f, 0.0) ** 2 for f in fields))"
        ),
        "new": (
            "def _weighted_cosine_similarity(\n"
            "    accumulated: dict,\n"
            "    profile_vector: dict,\n"
            "    weights: dict,\n"
            "    fields: list,\n"
            ") -> float:\n"
            '    """\n'
            "    Weighted cosine similarity between accumulated session vector and a state\n"
            "    profile vector, using per-field salience weights.\n"
            "\n"
            "    WCS(A, B, W) = sum(W_i * A_i * B_i) / (sqrt(sum(W_i * A_i^2)) * sqrt(sum(W_i * B_i^2)))\n"
            "\n"
            "    Returns 0.0 if either weighted magnitude is zero (undefined direction).\n"
            '    """\n'
            "    weighted_dot   = sum(weights.get(f, 1.0) * accumulated.get(f, 0.0) * profile_vector.get(f, 0.0) for f in fields)\n"
            "    weighted_mag_a = math.sqrt(sum(weights.get(f, 1.0) * accumulated.get(f, 0.0) ** 2 for f in fields))\n"
            "    weighted_mag_b = math.sqrt(sum(weights.get(f, 1.0) * profile_vector.get(f, 0.0) ** 2 for f in fields))\n"
            "\n"
            "    if weighted_mag_a == 0.0 or weighted_mag_b == 0.0:\n"
            "        return 0.0\n"
            "\n"
            "    return weighted_dot / (weighted_mag_a * weighted_mag_b)\n"
            "\n"
            "\n"
            "def compute_session_magnitude(accumulated: dict, fields: list) -> float:\n"
            '    """L2 norm of the accumulated session vector. Interpretable as session intensity."""\n'
            "    return math.sqrt(sum(accumulated.get(f, 0.0) ** 2 for f in fields))"
        ),
    },
    # ── Change 3 — rank_states() docstring + implementation ──────────────────
    {
        "description": "rank_states(): wire salience_weights into weighted cosine path, update docstring",
        "old": (
            'def rank_states(\n'
            '    accumulated_vector: dict,\n'
            '    salience_weights: Optional[dict] = None,\n'
            ') -> list:\n'
            '    """\n'
            '    Compute cosine similarity from accumulated_vector to each state profile vector.\n'
            '    Return list of StateRanking sorted ascending by distance (rank 1 = best match).\n'
            '\n'
            '    distance = 1 - cosine_similarity, so rank 1 has the smallest distance and\n'
            '    the highest cosine similarity score.\n'
            '\n'
            '    salience_weights: reserved for future per-state per-field weighting.\n'
            '      CALIBRATION TARGET — not applied in cosine mode.\n'
            '\n'
            '    Spec reference: Section II.4\n'
            '    """\n'
            '    fields = list(DIMENSIONAL_FIELDS)\n'
            '    results = []\n'
            '    for sid, profile in STATE_PROFILES.items():\n'
            '        profile_vec = profile.dimensional_vector.as_dict()\n'
            '        sim = _cosine_similarity(accumulated_vector, profile_vec, fields)\n'
            '        d = 1.0 - sim\n'
            '        results.append(StateRanking(rank=0, state_id=sid, distance=d, score=sim))\n'
            '\n'
            '    results.sort(key=lambda r: r.distance)\n'
            '    for i, r in enumerate(results):\n'
            '        r.rank = i + 1\n'
            '\n'
            '    return results'
        ),
        "new": (
            'def rank_states(\n'
            '    accumulated_vector: dict,\n'
            '    salience_weights: Optional[dict] = None,\n'
            ') -> list:\n'
            '    """\n'
            '    Compute similarity from accumulated_vector to each state profile vector.\n'
            '    Return list of StateRanking sorted ascending by distance (rank 1 = best match).\n'
            '\n'
            '    distance = 1 - similarity, so rank 1 has the smallest distance and\n'
            '    the highest similarity score.\n'
            '\n'
            '    salience_weights: optional dict mapping state_id -> {field: weight_value}.\n'
            '      When provided, uses weighted cosine similarity per state (WCS). This is\n'
            '      the Phase 2+ calibration path. When None, falls back to standard unweighted\n'
            '      cosine similarity — backward-compatible with all existing tests.\n'
            '      Missing state entries fall back to uniform weights (1.0 per field).\n'
            '\n'
            '    Spec reference: Section II.4\n'
            '    """\n'
            '    fields = list(DIMENSIONAL_FIELDS)\n'
            '    results = []\n'
            '    for sid, profile in STATE_PROFILES.items():\n'
            '        profile_vec = profile.dimensional_vector.as_dict()\n'
            '        if salience_weights is not None:\n'
            '            w = salience_weights.get(sid, {f: 1.0 for f in fields})\n'
            '            sim = _weighted_cosine_similarity(accumulated_vector, profile_vec, w, fields)\n'
            '        else:\n'
            '            sim = _cosine_similarity(accumulated_vector, profile_vec, fields)\n'
            '        d = 1.0 - sim\n'
            '        results.append(StateRanking(rank=0, state_id=sid, distance=d, score=sim))\n'
            '\n'
            '    results.sort(key=lambda r: r.distance)\n'
            '    for i, r in enumerate(results):\n'
            '        r.rank = i + 1\n'
            '\n'
            '    return results'
        ),
    },
    # ── Change 4 — AccumulationEngine.rank() docstring ───────────────────────
    {
        "description": "AccumulationEngine.rank(): update stale docstring",
        "old": (
            '    def rank(self, salience_weights: Optional[dict] = None) -> list:\n'
            '        """\n'
            '        Return full state ranking sorted ascending by Euclidean distance.\n'
            '        Call after all answers have been applied.\n'
            '        """'
        ),
        "new": (
            '    def rank(self, salience_weights: Optional[dict] = None) -> list:\n'
            '        """\n'
            '        Return full state ranking sorted ascending by distance (1 - similarity).\n'
            '        Call after all answers have been applied.\n'
            '        salience_weights: pass SALIENCE_PROFILES from engine.data.salience to\n'
            '          activate weighted cosine mode. None = unweighted (default).\n'
            '        """'
        ),
    },
]


def apply(content: str, dry_run: bool) -> tuple[str, list[str]]:
    log = []
    for change in CHANGES:
        old = change["old"]
        new = change["new"]
        desc = change["description"]
        if old not in content:
            log.append(f"  [ERROR] Not found: {desc}")
            continue
        count = content.count(old)
        if count > 1:
            log.append(f"  [ERROR] Ambiguous match ({count}x): {desc}")
            continue
        if dry_run:
            log.append(f"  [DRY-RUN] Would apply: {desc}")
        else:
            content = content.replace(old, new)
            log.append(f"  [APPLIED] {desc}")
    return content, log


def main():
    dry_run = "--write" not in sys.argv
    mode = "DRY-RUN" if dry_run else "WRITE"

    print(f"\n{'='*64}")
    print(f"patch_accumulation_weighted_cosine.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'='*64}\n")

    if not TARGET.exists():
        print("[ERROR] Target file not found.")
        sys.exit(1)

    content = TARGET.read_text(encoding="utf-8")
    new_content, log = apply(content, dry_run)

    errors = [l for l in log if "[ERROR]" in l]
    for line in log:
        print(line)

    if errors:
        print(f"\n[ABORT] {len(errors)} error(s). No changes written.")
        sys.exit(1)

    if not dry_run:
        TARGET.write_text(new_content, encoding="utf-8")
        print(f"\n[DONE] {TARGET} written.")
    else:
        print(f"\n[DRY-RUN COMPLETE] {len(CHANGES)} change(s) validated. Run with --write to apply.")

    sys.exit(0)


if __name__ == "__main__":
    main()
