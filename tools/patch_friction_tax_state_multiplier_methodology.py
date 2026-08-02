"""
PRV3 -- Durable write: prompts/friction-tax-state-multiplier-methodology.md

New file, content supplied verbatim by Pete. Follows the existing
prompts/*.md handoff-doc convention (e.g. friction-tax-unit-decision.md,
friction-tax-architecture-decision.md). Methodology documentation only --
STATE_MULTIPLIERS remains fully unpopulated (57 x None). No code changes,
no values written, no scoring performed. Do not touch
engine/friction_tax.py from this script.

Usage:
  python tools/patch_friction_tax_state_multiplier_methodology.py --dry-run
  python tools/patch_friction_tax_state_multiplier_methodology.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "prompts" / "friction-tax-state-multiplier-methodology.md"

CONTENT = """# Friction Tax — STATE_MULTIPLIERS Methodology (Calibration Set 3)

**Status:** Methodology locked. Scoring not yet started. STATE_MULTIPLIERS remains fully unpopulated (57 x None) until scoring is complete and this doc's output is applied.

## Purpose

STATE_MULTIPLIERS[state] represents a given friction state's inherent cost profile — independent of how severe the condition currently is for a specific org. Severity is handled entirely separately by the existing, locked SEVERITY_SCALAR dict (Emerging 0.6 / Entrenched 1.0 / Endemic 1.4), which multiplies the final friction tax figure downstream of this table. These two factors are deliberately kept separate and must never be combined or allowed to double-count each other:

- STATE_MULTIPLIERS[state] = "how costly is this kind of condition, inherently"
- SEVERITY_SCALAR[tier] = "how deep has this condition taken root for this org"

Confirmed via direct read of compute_friction_tax() (engine/friction_tax.py:464-546): the two scalars are applied as independent, sequential multiplications against the same adjusted_baseline, with no branching or interaction between them. This methodology preserves that separation deliberately — severity must never be folded into a state's score.

## Scoring criteria (applied per state, by Pete)

Each of the 57 states is scored 0-2 on each of four criteria. These are business-recognizable cost channels, chosen so a skeptical outside reader (HR leader, CFO, attorney) can evaluate the framework without needing PRV3 taxonomy vocabulary:

1. **Turnover/retention cost** — does this condition drive people out the door?
2. **Productivity/output loss** — does it degrade the work itself, even if people stay?
3. **Decision-quality/velocity cost** — does it cause bad or slow decisions?
4. **Legal/compliance exposure** — does it carry real liability risk (discrimination, retaliation, safety)?

Scale per criterion: 0 = negligible, 1 = moderate, 2 = significant.
Total raw score range: 0-8 per state.
A one-line rationale is required per criterion score, per state, for audit-trail defensibility — not just the numeric total.

## Combination function

Multiplier = linear interpolation of each state's raw total score onto a [1.0, 1.4] range, using min-max normalization against the ACTUAL observed low and high raw totals across all 57 scored states (not the theoretical 0-8 range).

Formula, once all 57 raw totals are known:

  observed_min = min(raw_total across all 57 states)
  observed_max = max(raw_total across all 57 states)
  multiplier(state) = 1.0 + ((raw_total(state) - observed_min) / (observed_max - observed_min)) * 0.4

Floor and ceiling are not arbitrary:
- **Floor = 1.0**: a diagnosed friction state should never multiply below baseline parity — the instrument's premise is that every identified condition costs the org something, never that it saves money relative to baseline.
- **Ceiling = 1.4**: reuses the constant already locked elsewhere in the same function (SEVERITY_SCALAR's Endemic tier, and the existing high = low * 1.4 relationship) rather than inventing an unrelated ratio for the same conceptual role of "upper-bound amplification."

Sequencing requirement: do not derive the interpolation formula's observed_min/observed_max until all 57 states are scored. Scoring must happen first; the mapping is derived from real data, not assumed in advance.

## Explicitly out of scope for this table

- Severity — handled entirely by SEVERITY_SCALAR, never folded into a state's score.
- Multi-state averaging logic — unchanged, already implemented (plain arithmetic mean across state_ids in compute_friction_tax()).

## Known adjacent issue (not blocking, logged for awareness)

STATE_MULTIPLIERS.get(sid, _DEFAULT_MULTIPLIER) falls back to _DEFAULT_MULTIPLIER = 0.0 for any unrecognized state_id, silently pulling the mean toward zero rather than raising an error. Not a Set 3 scoping concern today (all 57 known states will be populated), but worth a Tier 3 Decision Register entry if the taxonomy ever expands past 57 without a corresponding STATE_MULTIPLIERS update.

## Next steps (in order)

1. Pete scores all 57 states against the 4 criteria (manual judgment work — not derived from external research or engine internals).
2. Once scoring is complete, apply the min-max interpolation formula above to derive final multiplier values.
3. Gemini architecture review of the resulting schema/type approach before any code is written (consistent with the OrgTypeScalarEntry pattern used for Calibration Set 1).
4. CC populates STATE_MULTIPLIERS, runs tests, commits under dry-run-before-write protocol.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if TARGET_FILE.exists():
        print(f"ABORT -- {TARGET_FILE.relative_to(REPO_ROOT)} already exists", file=sys.stderr)
        sys.exit(1)

    print(f"New file: {TARGET_FILE.relative_to(REPO_ROOT)}")
    print("=" * 72)
    print(CONTENT)
    print("=" * 72)
    print("No other files touched by this script.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    TARGET_FILE.write_text(CONTENT, encoding="utf-8")
    print(f"\nWROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
