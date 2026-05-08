"""
Phase 3 Pass 1 — Aptitude secondary signal injection (Session 13)

Injects per-option aptitude_liability overrides into engine/data/questions.py
for questions targeting Authority states with documented Aptitude dimension overlap:
  Q03A  (the_uninitiated / built_to_fail)
  Q06   (the_policy_lag)
  Q19   (the_policy_lag)

Change:
  Problem-indicating options: aptitude_liability = 0.25 (explicit secondary signal)
  Positive/neutral options:   aptitude_liability = 0.0  (removes uniform noise)
  Authority signal:           UNCHANGED (question-level seed preserved)

Mechanism:
  Adds _opt_apt dict to _build_library() and uses it in the AnswerOption
  construction via dict spread + override.

Usage:
  python tools/patch_phase3_pass1_apt.py          # dry-run
  python tools/patch_phase3_pass1_apt.py --write  # apply
"""

import sys
import argparse
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"

# ── What we're inserting ───────────────────────────────────────────────────────

# Inserted after _seed = { ... } and before the for-loop in _build_library().
_OPT_APT_BLOCK = '''    # Phase 3 Pass 1 (Session 13): per-option aptitude_liability overrides.
    # Authority-overlap questions with documented Aptitude crossover.
    # Problem options: apt = 0.25 (explicit secondary signal, enables discrimination).
    # Neutral/positive options: apt = 0.0 (removes uniform noise).
    # Primary Authority signal unchanged.
    _opt_apt = {
        "Q03A": {"A": 0.0,  "B": 0.25, "C": 0.25, "D": 0.25},
        "Q06":  {"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25, "E": 0.0},
        "Q19":  {"A": 0.0,  "B": 0.0,  "C": 0.25, "D": 0.25},
    }
'''

# The old AnswerOption dimensional_contributions line (exact string in the file)
_OLD_CONTRIBUTIONS = "                    dimensional_contributions=dict(base),"

# Replacement: per-option override applied via dict merge + key override
_NEW_CONTRIBUTIONS = """\
                    dimensional_contributions={
                        **base,
                        "aptitude_liability": _opt_apt.get(qid, {}).get(
                            o[0], base["aptitude_liability"]
                        ),
                    },"""

# Anchor: insert _OPT_APT_BLOCK just before the for-loop
_FOR_LOOP_ANCHOR = "    for (qid, text, fmt, pos, seg, opts, targets, sev) in _QDATA:"


def load_source():
    return TARGET.read_text(encoding="utf-8")


def patch(source: str) -> str:
    # Step 1: Insert _opt_apt dict before the for-loop
    if "_opt_apt" in source:
        print("  INFO: _opt_apt already present — skipping insertion.")
        patched = source
    else:
        if _FOR_LOOP_ANCHOR not in source:
            raise ValueError("Anchor for _opt_apt insertion not found in source.")
        patched = source.replace(
            _FOR_LOOP_ANCHOR,
            _OPT_APT_BLOCK + _FOR_LOOP_ANCHOR,
        )

    # Step 2: Replace uniform dimensional_contributions with per-option override
    if _OLD_CONTRIBUTIONS not in patched:
        if _NEW_CONTRIBUTIONS.strip() in patched:
            print("  INFO: dimensional_contributions override already present — skipping.")
        else:
            raise ValueError("Old dimensional_contributions pattern not found in source.")
    else:
        patched = patched.replace(_OLD_CONTRIBUTIONS, _NEW_CONTRIBUTIONS)

    return patched


def diff_summary(original: str, updated: str):
    orig_lines = original.splitlines()
    upd_lines = updated.splitlines()
    added = [l for l in upd_lines if l not in orig_lines]
    removed = [l for l in orig_lines if l not in upd_lines]
    print("\n  Lines removed:")
    for l in removed:
        print(f"    - {l}")
    print("\n  Lines added:")
    for l in added:
        print(f"    + {l}")


def dry_run():
    source = load_source()
    updated = patch(source)
    if source == updated:
        print("DRY-RUN: No changes would be made.")
        return
    print("DRY-RUN: The following changes would be applied to engine/data/questions.py:")
    diff_summary(source, updated)
    print("\nDRY-RUN complete. Run with --write to apply.")


def write():
    source = load_source()
    updated = patch(source)
    if source == updated:
        print("WRITE: No changes needed.")
        return
    TARGET.write_text(updated, encoding="utf-8")
    print("WRITE: engine/data/questions.py patched.")
    diff_summary(source, updated)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 3 Pass 1 — Aptitude secondary signal injection")
    parser.add_argument("--write", action="store_true", help="Apply changes (default: dry-run)")
    args = parser.parse_args()
    if args.write:
        write()
    else:
        dry_run()
