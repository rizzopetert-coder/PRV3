"""
Patch: engine/data/questions.py — v17 Signal Amplification + Neutral Drain

Step 1 — Signal Amplification (6 options, 6 questions):
  Q07-B: alliance_liability 0.60 -> 0.80 (Alliance HC active path)
  Q11-D: attitude_liability 0.50 -> 0.75 (Attitude HC; C locked S18, D is next pick)
  Q15-D: attitude_liability 0.50 -> 0.75 (Attitude HC; C locked S18, D is next pick)
  Q26-C: alliance_liability 0.60 -> 0.80 (Alliance HC; authority_liability=-0.30 retained)
  Q35-B: aptitude_liability 0.60 -> 0.80 (Aptitude HC; authority_liability=-0.35 retained)
  Q36-E: aptitude_liability 0.60 -> 0.80 (Aptitude HC; authority_liability=-0.40 retained)

Step 2 — Neutral Drain Extension (3 options, 3 questions; Q06 skipped — neutral shift):
  Q01-B: authority_liability 0.25 -> -0.15 (neutral pick; authority drain)
  Q13-E: authority_liability -0.15 appended (neutral pick; currently authority_asset only)
  Q28-B: authority_liability 0.25 -> -0.15 (neutral pick; authority drain)

Resolution notes:
  Q11/Q15: C is best_option_for_state() pick but locked (S18). D applied instead.
    After D amplification (0.75 > C 0.50), best_option shifts to D — correct behavior.
  Q06: neutral pick (E) would shift to C after injection — skipped this session.
  Q01-B/Q28-B: "append -0.15" = SET authority_liability to -0.15 (replacing 0.25).

Session 23. Pete confirmed. 2026-05-23.

Usage:
  python tools/patch_v17_signal_amp_neutral_drain.py --dry-run
  python tools/patch_v17_signal_amp_neutral_drain.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"

CHANGES = [
    # ── Step 1: Signal Amplification ───────────────────────────────────────────

    {
        "description": "Q01-B: authority_liability 0.25 -> -0.15 (neutral drain, Step 2)",
        "old": (
            '        "Q01": {  # Authority HIGH (founders_grip). Single-seeded.\n'
            '            "A": {**_z, "authority_asset":    0.40},                    # F\n'
            '            "B": {**_z, "authority_liability": 0.25},                   # A\n'
            '            "C": {**_z, "authority_liability": 0.60},                   # P\n'
            '            "D": {**_z, "authority_liability": 0.60},                   # P\n'
            '            "E": {**_z, "authority_liability": 0.60},                   # P\n'
            '        },'
        ),
        "new": (
            '        "Q01": {  # Authority HIGH (founders_grip). Single-seeded. Neutral drain B v17.\n'
            '            "A": {**_z, "authority_asset":    0.40},                    # F\n'
            '            "B": {**_z, "authority_liability": -0.15},                  # A — neutral drain v17\n'
            '            "C": {**_z, "authority_liability": 0.60},                   # P\n'
            '            "D": {**_z, "authority_liability": 0.60},                   # P\n'
            '            "E": {**_z, "authority_liability": 0.60},                   # P\n'
            '        },'
        ),
    },
    {
        "description": "Q07-B: alliance_liability 0.60 -> 0.80 (Alliance HC amplification)",
        "old": (
            '        "Q07": {  # Alliance HIGH (the_fracture). Authority drain v15.\n'
            '            "A": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "B": {**_z, "alliance_liability": 0.60},                    # P\n'
            '            "C": {**_z, "alliance_liability": 0.60},                    # P\n'
            '            "D": {**_z, "alliance_liability": 0.60},                    # P\n'
            '        },'
        ),
        "new": (
            '        "Q07": {  # Alliance HIGH (the_fracture). Authority drain v15; amplify B v17.\n'
            '            "A": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "B": {**_z, "alliance_liability": 0.80},                    # P — amplify v17\n'
            '            "C": {**_z, "alliance_liability": 0.60},                    # P\n'
            '            "D": {**_z, "alliance_liability": 0.60},                    # P\n'
            '        },'
        ),
    },
    {
        "description": "Q11-D: attitude_liability 0.50 -> 0.75 (Attitude HC amplification; C locked S18)",
        "old": (
            '        "Q11": {  # Attitude MED + Authority (dual).\n'
            '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "attitude_liability": 0.25},                    # A\n'
            '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.05},  # P\n'
            '            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '            "E": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '        },'
        ),
        "new": (
            '        "Q11": {  # Attitude MED + Authority (dual). Amplify D v17 (C locked S18).\n'
            '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "attitude_liability": 0.25},                    # A\n'
            '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.05},  # P — LOCKED S18\n'
            '            "D": {**_z, "attitude_liability": 0.75, "authority_liability": 0.25},  # P — amplify v17\n'
            '            "E": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '        },'
        ),
    },
    {
        "description": "Q13-E: authority_liability -0.15 appended (neutral drain, Step 2)",
        "old": (
            '        "Q13": {  # Authority MED + Alliance (dual).\n'
            '            "A": {**_z, "alliance_liability":  0.30, "authority_liability": 0.20, "authority_asset": 0.15},  # DE\n'
            '            "B": {**_z, "authority_liability": 0.50, "alliance_liability":  0.25},                           # P\n'
            '            "C": {**_z, "authority_liability": 0.50, "alliance_liability":  0.25},                           # P\n'
            '            "D": {**_z, "authority_liability": 0.50, "alliance_liability":  0.25},                           # P\n'
            '            "E": {**_z, "authority_asset":     0.40},                                                        # F\n'
            '        },'
        ),
        "new": (
            '        "Q13": {  # Authority MED + Alliance (dual). Neutral drain E v17.\n'
            '            "A": {**_z, "alliance_liability":  0.30, "authority_liability": 0.20, "authority_asset": 0.15},  # DE\n'
            '            "B": {**_z, "authority_liability": 0.50, "alliance_liability":  0.25},                           # P\n'
            '            "C": {**_z, "authority_liability": 0.50, "alliance_liability":  0.25},                           # P\n'
            '            "D": {**_z, "authority_liability": 0.50, "alliance_liability":  0.25},                           # P\n'
            '            "E": {**_z, "authority_asset":     0.40, "authority_liability": -0.15},                          # F — neutral drain v17\n'
            '        },'
        ),
    },
    {
        "description": "Q15-D: attitude_liability 0.50 -> 0.75 (Attitude HC amplification; C locked S18)",
        "old": (
            '        "Q15": {  # Attitude MED (diversity_ceiling) + Authority (dual).\n'
            '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "attitude_liability": 0.25},                    # A\n'
            '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25, "alliance_liability": -0.15},  # P\n'
            '            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '            "E": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '        },'
        ),
        "new": (
            '        "Q15": {  # Attitude MED (diversity_ceiling) + Authority (dual). Amplify D v17 (C locked S18).\n'
            '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "attitude_liability": 0.25},                    # A\n'
            '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25, "alliance_liability": -0.15},  # P — LOCKED S18\n'
            '            "D": {**_z, "attitude_liability": 0.75, "authority_liability": 0.25},  # P — amplify v17\n'
            '            "E": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '        },'
        ),
    },
    {
        "description": "Q26-C: alliance_liability 0.60 -> 0.80 (Alliance HC amplification; authority_liability=-0.30 retained)",
        "old": (
            '        "Q26": {  # Alliance HIGH (the_fracture). Authority drain v15; contrast C v16.\n'
            '            "A": {**_z, "alliance_asset":     0.40},                    # F\n'
            '            "B": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "C": {**_z, "alliance_liability": 0.60, "authority_liability": -0.30},  # P — contrast v16\n'
            '            "D": {**_z, "alliance_liability": 0.60},                    # P\n'
            '        },'
        ),
        "new": (
            '        "Q26": {  # Alliance HIGH (the_fracture). Authority drain v15; contrast C v16; amplify C v17.\n'
            '            "A": {**_z, "alliance_asset":     0.40},                    # F\n'
            '            "B": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "C": {**_z, "alliance_liability": 0.80, "authority_liability": -0.30},  # P — contrast v16, amplify v17\n'
            '            "D": {**_z, "alliance_liability": 0.60},                    # P\n'
            '        },'
        ),
    },
    {
        "description": "Q28-B: authority_liability 0.25 -> -0.15 (neutral drain, Step 2)",
        "old": (
            '        "Q28": {  # Authority HIGH (unsolved_problem) + Attitude (dual).\n'
            '            "A": {**_z, "authority_asset":     0.40},                   # F\n'
            '            "B": {**_z, "authority_liability": 0.25},                   # A\n'
            '            "C": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30},  # P\n'
            '            "D": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30},  # P\n'
            '        },'
        ),
        "new": (
            '        "Q28": {  # Authority HIGH (unsolved_problem) + Attitude (dual). Neutral drain B v17.\n'
            '            "A": {**_z, "authority_asset":     0.40},                   # F\n'
            '            "B": {**_z, "authority_liability": -0.15},                  # A — neutral drain v17\n'
            '            "C": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30},  # P\n'
            '            "D": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30},  # P\n'
            '        },'
        ),
    },
    {
        "description": "Q35-B: aptitude_liability 0.60 -> 0.80 (Aptitude HC amplification; authority_liability=-0.35 retained)",
        "old": (
            '        "Q35": {  # Contrast B v16.\n'
            '            "A": {**_z, "aptitude_liability": 0.25},\n'
            '            "B": {**_z, "aptitude_liability": 0.60, "authority_liability": -0.35},  # contrast v16\n'
            '            "C": {**_z, "aptitude_liability": 0.40},\n'
            '            "D": {**_z, "aptitude_liability": 0.40},\n'
            '        },'
        ),
        "new": (
            '        "Q35": {  # Contrast B v16; amplify B v17.\n'
            '            "A": {**_z, "aptitude_liability": 0.25},\n'
            '            "B": {**_z, "aptitude_liability": 0.80, "authority_liability": -0.35},  # contrast v16, amplify v17\n'
            '            "C": {**_z, "aptitude_liability": 0.40},\n'
            '            "D": {**_z, "aptitude_liability": 0.40},\n'
            '        },'
        ),
    },
    {
        "description": "Q36-E: aptitude_liability 0.60 -> 0.80 (Aptitude HC amplification; authority_liability=-0.40 retained)",
        "old": (
            '        "Q36": {  # Contrast E v16 (APT-PT-00 decoupling).\n'
            '            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.40},\n'
            '            "B": {**_z, "aptitude_liability": 0.40},\n'
            '            "C": {**_z, "aptitude_liability": 0.40},\n'
            '            "D": {**_z, "aptitude_liability": 0.40, "attitude_liability": 0.40},\n'
            '            "E": {**_z, "aptitude_liability": 0.60, "authority_liability": -0.40},  # contrast v16\n'
            '        },'
        ),
        "new": (
            '        "Q36": {  # Contrast E v16 (APT-PT-00 decoupling); amplify E v17.\n'
            '            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.40},\n'
            '            "B": {**_z, "aptitude_liability": 0.40},\n'
            '            "C": {**_z, "aptitude_liability": 0.40},\n'
            '            "D": {**_z, "aptitude_liability": 0.40, "attitude_liability": 0.40},\n'
            '            "E": {**_z, "aptitude_liability": 0.80, "authority_liability": -0.40},  # contrast v16, amplify v17\n'
            '        },'
        ),
    },
]


def apply(content: str, dry_run: bool) -> tuple[str, list[str]]:
    log = []
    for change in CHANGES:
        old, new, desc = change["old"], change["new"], change["description"]
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
    print(f"\n{'='*72}")
    print(f"patch_v17_signal_amp_neutral_drain.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'='*72}\n")
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
        print(f"\n[DRY-RUN COMPLETE] {len(CHANGES)} change(s) validated. No file written.")
    sys.exit(0)


if __name__ == "__main__":
    main()
