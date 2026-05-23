"""
Patch: engine/data/questions.py — v16 Step 1 Contrast Injection

Changes (8 option vectors across 6 questions):
  Q14-B/C: authority_liability 0.25 -> -0.05 (neutral drain, delta -0.30)
  Q16-B/C: authority_liability 0.10 -> -0.20 (Attitude HC active path, delta -0.30)
  Q22-B:   authority_liability 0.25 -> -0.10 (neutral drain, delta -0.35)
  Q26-C:   add authority_liability=-0.30 (Alliance HC active path)
  Q35-B:   add authority_liability=-0.35 (Aptitude HC active path)
  Q36-E:   add authority_liability=-0.40 (Aptitude HC active path, APT-PT-00)

Session 22. Gemini corrected spec. Pete confirmed 2026-05-22.

Usage:
  python tools/patch_v16_step1_contrast_injection.py --dry-run
  python tools/patch_v16_step1_contrast_injection.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"

CHANGES = [
    {
        "description": "Q14 B/C: authority_liability 0.25 -> -0.05 (neutral drain, delta -0.30)",
        "old": (
            '        "Q14": {  # Authority MED (pay_exposure, pay_fog) + Aptitude (dual).\n'
            '            "A": {**_z, "authority_asset":     0.40},                   # F\n'
            '            "B": {**_z, "authority_liability": 0.25},                   # A\n'
            '            "C": {**_z, "authority_liability": 0.25},                   # A\n'
            '            "D": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P\n'
            '            "E": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P\n'
            '        },'
        ),
        "new": (
            '        "Q14": {  # Authority MED (pay_exposure, pay_fog) + Aptitude (dual). Contrast B/C v16.\n'
            '            "A": {**_z, "authority_asset":     0.40},                   # F\n'
            '            "B": {**_z, "authority_liability": -0.05},                  # A — contrast v16\n'
            '            "C": {**_z, "authority_liability": -0.05},                  # A — contrast v16\n'
            '            "D": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P\n'
            '            "E": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P\n'
            '        },'
        ),
    },
    {
        "description": (
            "Q16 B/C: authority_liability 0.10 -> -0.20 (Attitude HC active path, delta -0.30); D unchanged"
        ),
        "old": (
            '        "Q16": {  # Attitude MED (diversity_ceiling). Authority partial drain v15.\n'
            '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
            '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
            '            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
            '            "E": {**_z, "attitude_liability": 0.25},                    # A\n'
            '        },'
        ),
        "new": (
            '        "Q16": {  # Attitude MED (diversity_ceiling). Authority partial drain v15; contrast B/C v16.\n'
            '            "A": {**_z, "attitude_asset":     0.40},                    # F\n'
            '            "B": {**_z, "attitude_liability": 0.50, "authority_liability": -0.20},  # P — contrast v16\n'
            '            "C": {**_z, "attitude_liability": 0.50, "authority_liability": -0.20},  # P — contrast v16\n'
            '            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P\n'
            '            "E": {**_z, "attitude_liability": 0.25},                    # A\n'
            '        },'
        ),
    },
    {
        "description": "Q22-B: authority_liability 0.25 -> -0.10 (neutral drain, delta -0.35)",
        "old": (
            '        "Q22": {  # Authority MED + Aptitude (dual).\n'
            '            "A": {**_z, "authority_asset":     0.40},                                                       # F\n'
            '            "B": {**_z, "authority_liability": 0.25},                                                       # A\n'
            '            "C": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},                           # P\n'
            '            "D": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},                           # P\n'
            '            "E": {**_z, "authority_liability": 0.45, "aptitude_liability": 0.25, "authority_asset": 0.10},  # DE\n'
            '        },'
        ),
        "new": (
            '        "Q22": {  # Authority MED + Aptitude (dual). Contrast B v16.\n'
            '            "A": {**_z, "authority_asset":     0.40},                                                       # F\n'
            '            "B": {**_z, "authority_liability": -0.10},                                                      # A — contrast v16\n'
            '            "C": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},                           # P\n'
            '            "D": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},                           # P\n'
            '            "E": {**_z, "authority_liability": 0.45, "aptitude_liability": 0.25, "authority_asset": 0.10},  # DE\n'
            '        },'
        ),
    },
    {
        "description": "Q26-C: add authority_liability=-0.30 (Alliance HC active path; the_fracture/silosolation)",
        "old": (
            '        "Q26": {  # Alliance HIGH (the_fracture). Authority drain v15.\n'
            '            "A": {**_z, "alliance_asset":     0.40},                    # F\n'
            '            "B": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "C": {**_z, "alliance_liability": 0.60},                    # P\n'
            '            "D": {**_z, "alliance_liability": 0.60},                    # P\n'
            '        },'
        ),
        "new": (
            '        "Q26": {  # Alliance HIGH (the_fracture). Authority drain v15; contrast C v16.\n'
            '            "A": {**_z, "alliance_asset":     0.40},                    # F\n'
            '            "B": {**_z, "alliance_liability": 0.25},                    # A\n'
            '            "C": {**_z, "alliance_liability": 0.60, "authority_liability": -0.30},  # P — contrast v16\n'
            '            "D": {**_z, "alliance_liability": 0.60},                    # P\n'
            '        },'
        ),
    },
    {
        "description": (
            "Q35-B: add authority_liability=-0.35 "
            "(Aptitude HC active path; built_to_fail/undefined_role/overloaded_manager)"
        ),
        "old": (
            '        "Q35": {\n'
            '            "A": {**_z, "aptitude_liability": 0.25},\n'
            '            "B": {**_z, "aptitude_liability": 0.60},\n'
            '            "C": {**_z, "aptitude_liability": 0.40},\n'
            '            "D": {**_z, "aptitude_liability": 0.40},\n'
            '        },'
        ),
        "new": (
            '        "Q35": {  # Contrast B v16.\n'
            '            "A": {**_z, "aptitude_liability": 0.25},\n'
            '            "B": {**_z, "aptitude_liability": 0.60, "authority_liability": -0.35},  # contrast v16\n'
            '            "C": {**_z, "aptitude_liability": 0.40},\n'
            '            "D": {**_z, "aptitude_liability": 0.40},\n'
            '        },'
        ),
    },
    {
        "description": "Q36-E: add authority_liability=-0.40 (Aptitude HC active path; APT-PT-00 decoupling)",
        "old": (
            '        "Q36": {\n'
            '            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.40},\n'
            '            "B": {**_z, "aptitude_liability": 0.40},\n'
            '            "C": {**_z, "aptitude_liability": 0.40},\n'
            '            "D": {**_z, "aptitude_liability": 0.40, "attitude_liability": 0.40},\n'
            '            "E": {**_z, "aptitude_liability": 0.60},\n'
            '        },'
        ),
        "new": (
            '        "Q36": {  # Contrast E v16 (APT-PT-00 decoupling).\n'
            '            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.40},\n'
            '            "B": {**_z, "aptitude_liability": 0.40},\n'
            '            "C": {**_z, "aptitude_liability": 0.40},\n'
            '            "D": {**_z, "aptitude_liability": 0.40, "attitude_liability": 0.40},\n'
            '            "E": {**_z, "aptitude_liability": 0.60, "authority_liability": -0.40},  # contrast v16\n'
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
    print(f"\n{'='*64}")
    print(f"patch_v16_step1_contrast_injection.py — {mode}")
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
