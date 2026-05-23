"""
Patch: engine/data/questions.py — Step 1 Authority Drain (v15)

Changes (all in _opt_contrib):
  Q07 B/C/D: authority_liability 0.30 -> 0.00 (full strip)
  Q09 C/D/E: authority_liability 0.30 -> 0.00 (full strip)
  Q16 B/C/D: authority_liability 0.25 -> 0.10 (partial reduction)
  Q29 B/C/D: authority_liability 0.25 -> 0.10 (partial reduction)
  Q20 C/D:   authority_liability 0.30 -> 0.00 (full strip)
  Q26 C/D:   authority_liability 0.30 -> 0.00 (full strip)

Usage:
  python tools/patch_v15_step1_authority_drain.py --dry-run
  python tools/patch_v15_step1_authority_drain.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"

CHANGES = [
    {
        "description": "Q07 B/C/D: strip authority_liability 0.30 -> 0.00",
        "old": (
            '        "Q07": {  # Alliance HIGH (the_fracture) + Authority (dual).\n'
            '            "A": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "B": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P\n'
            '            "C": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P\n'
            '            "D": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P\n'
            "        },"
        ),
        "new": (
            '        "Q07": {  # Alliance HIGH (the_fracture). Authority drain v15.\n'
            '            "A": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "B": {**_z, "alliance_liability": 0.60},                    # P\n'
            '            "C": {**_z, "alliance_liability": 0.60},                    # P\n'
            '            "D": {**_z, "alliance_liability": 0.60},                    # P\n'
            "        },"
        ),
    },
    {
        "description": "Q09 C/D/E: strip authority_liability 0.30 -> 0.00",
        "old": (
            '        "Q09": {  # Alliance HIGH (the_fracture) + Authority (dual).\n'
            '            "A": {**_z, "alliance_asset":     0.40},                    # F\n'
            '            "B": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "C": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P\n'
            '            "D": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P\n'
            '            "E": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P\n'
            "        },"
        ),
        "new": (
            '        "Q09": {  # Alliance HIGH (the_fracture). Authority drain v15.\n'
            '            "A": {**_z, "alliance_asset":     0.40},                    # F\n'
            '            "B": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "C": {**_z, "alliance_liability": 0.60},                    # P\n'
            '            "D": {**_z, "alliance_liability": 0.60},                    # P\n'
            '            "E": {**_z, "alliance_liability": 0.60},                    # P\n'
            "        },"
        ),
    },
    {
        "description": "Q16 B/C/D: reduce authority_liability 0.25 -> 0.10",
        "old": (
            '        "Q16": {  # Attitude MED (diversity_ceiling) + Authority (dual).\n'
            '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '            "E": {**_z, "attitude_liability": 0.25},                    # A\n'
            "        },"
        ),
        "new": (
            '        "Q16": {  # Attitude MED (diversity_ceiling). Authority partial drain v15.\n'
            '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
            '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
            '            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
            '            "E": {**_z, "attitude_liability": 0.25},                    # A\n'
            "        },"
        ),
    },
    {
        "description": "Q29 B/C/D: reduce authority_liability 0.25 -> 0.10",
        "old": (
            '        "Q29": {  # Attitude MED (diversity_ceiling) + Authority (dual).\n'
            '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P\n'
            '            "E": {**_z, "attitude_liability": 0.25},                    # A\n'
            "        },"
        ),
        "new": (
            '        "Q29": {  # Attitude MED (diversity_ceiling). Authority partial drain v15.\n'
            '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
            '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
            '            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
            '            "E": {**_z, "attitude_liability": 0.25},                    # A\n'
            "        },"
        ),
    },
    {
        "description": "Q20 C/D: strip authority_liability 0.30 -> 0.00",
        "old": (
            '        "Q20": {  # Aptitude HIGH (built_to_fail) + Authority (dual).\n'
            '            "A": {**_z, "aptitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "aptitude_liability": 0.25},                    # A\n'
            '            "C": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.30},  # P\n'
            '            "D": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.30},  # P\n'
            "        },"
        ),
        "new": (
            '        "Q20": {  # Aptitude HIGH (built_to_fail). Authority drain v15.\n'
            '            "A": {**_z, "aptitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "aptitude_liability": 0.25},                    # A\n'
            '            "C": {**_z, "aptitude_liability": 0.60},                    # P\n'
            '            "D": {**_z, "aptitude_liability": 0.60},                    # P\n'
            "        },"
        ),
    },
    {
        "description": "Q26 C/D: strip authority_liability 0.30 -> 0.00",
        "old": (
            '        "Q26": {  # Alliance HIGH (the_fracture) + Authority (dual).\n'
            '            "A": {**_z, "alliance_asset":     0.40},                    # F\n'
            '            "B": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "C": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P\n'
            '            "D": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P\n'
            "        },"
        ),
        "new": (
            '        "Q26": {  # Alliance HIGH (the_fracture). Authority drain v15.\n'
            '            "A": {**_z, "alliance_asset":     0.40},                    # F\n'
            '            "B": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "C": {**_z, "alliance_liability": 0.60},                    # P\n'
            '            "D": {**_z, "alliance_liability": 0.60},                    # P\n'
            "        },"
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
    print(f"\n{'='*64}")
    print(f"patch_v15_step1_authority_drain.py — {mode}")
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
        print(f"\n[DRY-RUN COMPLETE] {len(CHANGES)} change(s) validated.")
    sys.exit(0)


if __name__ == "__main__":
    main()
