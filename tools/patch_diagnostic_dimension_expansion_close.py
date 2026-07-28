"""
PRV3 -- Diagnostic Dimension Expansion plan file: append closing status
for the three BUILD candidates now committed (Steps 1-3 complete).

Updates prompts/diagnostic-dimension-expansion.md under "## Decisions":
  - Item 1 (Trajectory): DONE, 518545a, open calibration item on
    TRAJECTORY_STABILITY_THRESHOLD flagged explicitly.
  - Item 2 (Cascade risk): DONE, f4ee405.
  - Item 4 (SPOF vs. diffuse causation): DONE, 1b75a1b,
    resolution_families.py routing influence still split off.

Items 3 (Reversibility -- parked) and 5 (Urgency window -- deferred) are
untouched, per explicit instruction.

Usage:
  python tools/patch_diagnostic_dimension_expansion_close.py --dry-run
  python tools/patch_diagnostic_dimension_expansion_close.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "prompts" / "diagnostic-dimension-expansion.md"

EDITS: list[tuple[str, str, str]] = []

EDITS.append((
    "item 1 (Trajectory) closing status",
    '''1. **Trajectory / directionality — BUILD.**
   Derive from answers_log early/late-session vector delta + duration_band.
   No new questions, no new vector fields, no new intake.''',
    '''1. **Trajectory / directionality — BUILD.**
   Derive from answers_log early/late-session vector delta + duration_band.
   No new questions, no new vector fields, no new intake.
   -> DONE. Committed 518545a. Open calibration item:
      TRAJECTORY_STABILITY_THRESHOLD = 0.20 (engine/accumulation.py) is
      an explicitly-flagged, unvalidated starting hypothesis --
      live smoke test showed a real decelerating case crossing it
      decisively but a real escalating case landing below it. Needs
      real calibration data before being treated as reliable, not
      adjusted ad hoc.''',
))

EDITS.append((
    "item 2 (Cascade risk) closing status",
    '''2. **Cascade risk — BUILD.**
   Wire existing compute_cascade_risk() into assemble_output() /
   contract.py private_output shape / PrivateOutputPayload (types.ts) /
   answer/route.ts plumbing for Path 1.''',
    '''2. **Cascade risk — BUILD.**
   Wire existing compute_cascade_risk() into assemble_output() /
   contract.py private_output shape / PrivateOutputPayload (types.ts) /
   answer/route.ts plumbing for Path 1.
   -> DONE. Committed f4ee405.''',
))

EDITS.append((
    "item 4 (SPOF vs. diffuse causation) closing status",
    '''4. **SPOF vs. diffuse causation — BUILD, output contract only.**
   Wire existing compute_causation_pattern() into assemble_output() /
   contract.py / PrivateOutputPayload / route plumbing, same shape as
   cascade risk. resolution_families.py routing influence explicitly
   SPLIT OFF — routing functions are pure state_id lookups today with no
   signal input; adding causation_pattern-based routing is new surface
   area (new parameter or new function) and is a separate later decision,
   not in this build.''',
    '''4. **SPOF vs. diffuse causation — BUILD, output contract only.**
   Wire existing compute_causation_pattern() into assemble_output() /
   contract.py / PrivateOutputPayload / route plumbing, same shape as
   cascade risk. resolution_families.py routing influence explicitly
   SPLIT OFF — routing functions are pure state_id lookups today with no
   signal input; adding causation_pattern-based routing is new surface
   area (new parameter or new function) and is a separate later decision,
   not in this build.
   -> DONE. Committed 1b75a1b. resolution_families.py routing influence
      remains split off, not started.''',
))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = TARGET_FILE.read_text(encoding="utf-8")

    for label, old, new in EDITS:
        count = text.count(old)
        if count != 1:
            print(f"ABORT -- anchor for '{label}' matched {count} times, need exactly 1", file=sys.stderr)
            sys.exit(1)

    print("=" * 100)
    for label, old, new in EDITS:
        print(f"\n--- {label} ---")
        print("BEFORE:")
        print(old)
        print("AFTER:")
        print(new)
    print("\n" + "=" * 100)

    new_text = text
    for label, old, new in EDITS:
        new_text = new_text.replace(old, new, 1)

    print(f"File: {len(text)} chars -> {len(new_text)} chars ({len(new_text) - len(text):+d})")
    print("\nItems 3 (Reversibility) and 5 (Urgency window) confirmed untouched.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    TARGET_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
