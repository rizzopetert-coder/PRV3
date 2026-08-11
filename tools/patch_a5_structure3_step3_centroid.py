"""
PRV3 -- A5 + Structure 3 combined recalibration, Step 3 (engine/accumulation.py:
new MC_CENTROID_39 values + rank_states() divisor 44.0 -> 42.0). Step 2
(centroid regeneration via tools/diag_v21_accumulated_centroid.py, run
directly against the real live 42-question PHASE_1_QUESTION_SEQUENCE
after Step 1's sequence wiring) produced the new values below -- script
output, not hand-computed.

CENTROID_FIELD_SCALARS is deliberately left untouched here -- its values
are stale pending this recalibration's own Step 4 (harness reconvergence),
same scoping Pete set explicitly for the original MC_CENTROID_39 arc's
equivalent step. Only its adjacent comments are corrected (/44 -> /42) so
they don't describe a stale divisor while pointing at values that are
about to be regenerated anyway.

MC_CENTROID_39's name deliberately NOT changed -- verified this session
(engine/accumulation.py's own comment) that a rename to MC_CENTROID_LIVE
was proposed by Gemini once already and never signed off by Pete; not
reopened here, consistent with the name surviving the prior 39->44 count
change unchanged too.

Usage:
  python tools/patch_a5_structure3_step3_centroid.py --dry-run
  python tools/patch_a5_structure3_step3_centroid.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


ACCUMULATION = "engine/accumulation.py"

# ═══════════════════════════════════════════════════════════════════════
# MC_CENTROID_39 -- new values + provenance comment (prior values kept in
# the trail, same convention the original arc used for the 37->44 jump).
# ═══════════════════════════════════════════════════════════════════════

edit(
    ACCUMULATION,
    '# Empirical noise centroid — per-field mean of accumulated vector across N=1000\n'
    '# random simulations, seed=42, across the 44 live PHASE_1_QUESTION_SEQUENCE\n'
    '# questions (web/lib/session-store.ts, read live at generation time) --\n'
    '# regenerated this session after Q40-Q51 were added (32 -> 44 live questions).\n'
    '# Original values (37 real questions -- Q03/Q27 were silently unreachable\n'
    '# under the old range-based generation, not 39 despite the name; see\n'
    '# tools/_mob.txt Decision Register for the full MC_CENTROID_39/core-\n'
    '# question-count coupling finding): aptitude_liability 3.9565, aptitude_\n'
    '# asset 0.6800, authority_liability 5.3601, authority_asset 1.6503,\n'
    '# alliance_liability 2.9859, alliance_asset 0.1924, attitude_liability\n'
    '# 4.8137, attitude_asset 0.9795.\n'
    '# Name intentionally NOT changed to reflect 44 -- separate rename decision\n'
    '# (Gemini suggested MC_CENTROID_LIVE), not yet signed off by Pete.\n'
    '# Derived from tools/diag_v21_accumulated_centroid.py. LOCKED.\n'
    'MC_CENTROID_39: dict = {\n'
    '    "aptitude_liability":  3.5307,\n'
    '    "aptitude_asset":      0.5296,\n'
    '    "authority_liability": 6.2624,\n'
    '    "authority_asset":     1.3872,\n'
    '    "alliance_liability":  3.0468,\n'
    '    "alliance_asset":      0.4396,\n'
    '    "attitude_liability":  6.3701,\n'
    '    "attitude_asset":      1.3307,\n'
    '}\n',
    '# Empirical noise centroid — per-field mean of accumulated vector across N=1000\n'
    '# random simulations, seed=42, across the 42 live PHASE_1_QUESTION_SEQUENCE\n'
    '# questions (web/lib/session-store.ts, read live at generation time) --\n'
    '# regenerated this session (A5 + Structure 3 combined recalibration,\n'
    '# 44 -> 42: Q29 removed as a literal duplicate of Q16, its severity\n'
    '# follow-on SEVER-12 re-chained off SEVER-01; Q45 converted from core\n'
    '# to a Q44-conditional splice, Q46 deliberately untouched).\n'
    '# Prior values (44 real questions, post Q40-Q51 expansion): aptitude_\n'
    '# liability 3.5307, aptitude_asset 0.5296, authority_liability 6.2624,\n'
    '# authority_asset 1.3872, alliance_liability 3.0468, alliance_asset\n'
    '# 0.4396, attitude_liability 6.3701, attitude_asset 1.3307.\n'
    '# Original values (37 real questions -- Q03/Q27 were silently unreachable\n'
    '# under the old range-based generation, not 39 despite the name; see\n'
    '# tools/_mob.txt Decision Register for the full MC_CENTROID_39/core-\n'
    '# question-count coupling finding): aptitude_liability 3.9565, aptitude_\n'
    '# asset 0.6800, authority_liability 5.3601, authority_asset 1.6503,\n'
    '# alliance_liability 2.9859, alliance_asset 0.1924, attitude_liability\n'
    '# 4.8137, attitude_asset 0.9795.\n'
    '# Name intentionally NOT changed to reflect 42 -- separate rename decision\n'
    '# (Gemini suggested MC_CENTROID_LIVE), not yet signed off by Pete.\n'
    '# Derived from tools/diag_v21_accumulated_centroid.py. LOCKED.\n'
    'MC_CENTROID_39: dict = {\n'
    '    "aptitude_liability":  3.1590,\n'
    '    "aptitude_asset":      0.5272,\n'
    '    "authority_liability": 5.3306,\n'
    '    "authority_asset":     1.4412,\n'
    '    "alliance_liability":  3.0959,\n'
    '    "alliance_asset":      0.4204,\n'
    '    "attitude_liability":  5.9345,\n'
    '    "attitude_asset":      1.2334,\n'
    '}\n',
)

# ═══════════════════════════════════════════════════════════════════════
# CENTROID_FIELD_SCALARS -- comment-only correction (/44 -> /42). Values
# untouched -- stale pending this recalibration's own Step 4.
# ═══════════════════════════════════════════════════════════════════════

edit(
    ACCUMULATION,
    '# Field-specific centroid displacement scalars — Path B, Session 27.\n'
    '# Scales MC_CENTROID_39 per field: mu_focused[f] = MC_CENTROID_39[f] * scalar[f] * (N/44).\n'
    '# Derived from state_targets coverage per dimension / 44 live questions\n'
    '# (updated this session -- was /39, see MC_CENTROID_39 comment above).\n'
    '# Values below are stale pending Step 4 (harness reconvergence) -- not\n'
    '# updated by this step, per Pete\'s explicit Step 3 scope.',
    '# Field-specific centroid displacement scalars — Path B, Session 27.\n'
    '# Scales MC_CENTROID_39 per field: mu_focused[f] = MC_CENTROID_39[f] * scalar[f] * (N/42).\n'
    '# Derived from state_targets coverage per dimension / 42 live questions\n'
    '# (updated this session -- was /44, see MC_CENTROID_39 comment above).\n'
    '# Values below are stale pending this recalibration\'s own Step 4\n'
    '# (harness reconvergence) -- not updated by this step, per Pete\'s\n'
    '# explicit Step 3 scope.',
)

# ═══════════════════════════════════════════════════════════════════════
# rank_states() -- docstring formula + the real divisor.
# ═══════════════════════════════════════════════════════════════════════

edit(
    ACCUMULATION,
    '      mu_N    = MC_CENTROID_39 * (answered_question_count / 44.0)',
    '      mu_N    = MC_CENTROID_39 * (answered_question_count / 42.0)',
)

edit(
    ACCUMULATION,
    '    scale = N / 44.0',
    '    scale = N / 42.0',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
