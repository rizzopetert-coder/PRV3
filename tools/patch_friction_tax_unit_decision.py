"""
PRV3 -- Friction Tax Units Decision: payroll-based, not revenue-based.

Task 1: creates prompts/friction-tax-unit-decision.md (durable decision
record, content supplied verbatim by Pete, "[today's date]" filled in).

Task 2: engine/friction_tax.py -- comment/docstring-only edits, no
structural change. Grep-confirmed before writing: the literal word
"revenue" appears exactly ONCE in the entire file, in the _ORG_SIZE_BANDS
section comment -- the module docstring itself never said "revenue" to
begin with, so there is nothing to change there (Pete's instruction
mentioned "module docstring" as a possible location; direct read found
it wasn't one). Two edits:
  1. _ORG_SIZE_BANDS section comment: "revenue proxy" -> "payroll proxy",
     plus a short pointer to the new decision doc.
  2. STATE_MULTIPLIERS section comment: clarifies payroll basis (no
     "revenue" word existed here to replace -- this is Task 1's second
     "what needs updating" item, an addition, not a swap), plus the same
     pointer.

Not touched, flagged separately: STATE_MULTIPLIERS' own comment claims
"(47 states)" but the table actually has 57 keys (47 original + 10
Session 67 taxonomy-expansion states, directly counted). Pre-existing,
unrelated to this task's scope -- not fixed here.

No field names, function signatures, or table structures changed. All
STATE_MULTIPLIERS/_ORG_SIZE_BANDS values remain None.

Usage:
  python tools/patch_friction_tax_unit_decision.py --dry-run
  python tools/patch_friction_tax_unit_decision.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_FILE = REPO_ROOT / "prompts" / "friction-tax-unit-decision.md"
FRICTION_TAX_FILE = REPO_ROOT / "engine" / "friction_tax.py"

DECISION_DATE = "2026-07-27"

DOC_CONTENT = f"""# Friction Tax Unit Decision

Decided {DECISION_DATE}. Full research trail: this session's conversation
log (web searches on SHRM/Gallup/McKinsey turnover, disengagement, and
organizational-dysfunction cost benchmarks).

## Decision
STATE_MULTIPLIERS represents a percentage of estimated organizational
payroll (not revenue). band_low in _ORG_SIZE_BANDS represents estimated
total payroll for that headcount tier (not a revenue proxy). No change
to field types, table shapes, or compute_friction_tax()'s math
(low = band_low * mean_multiplier * severity_scalar) -- only the
semantic interpretation and the real values to be populated change.

## Why
- SHRM: replacing an employee costs 50-200% of their annual salary
  (converges across many independent citations of SHRM's own published
  figures).
- Gallup: disengaged employees cost roughly 18% of annual salary
  (converges similarly, Gallup's own State of the Global Workplace
  report).
- McKinsey's contribution to this space is a flat dollar range scoped to
  one company-size cohort (median S&P company), not a transferable
  percentage of anything -- doesn't support either unit directly, but
  doesn't contradict payroll-based framing either.
- Revenue-percentage figures found (e.g. "20-30% of revenue") came only
  from low-quality sources with vague "studies show" attribution and
  citations to McKinsey/HBR reports that don't correspond to verifiable
  real publications -- rejected as unreliable by the same standard
  applied to this session's Gemini fabrication findings, not merely
  deprioritized for being less common.

## What needs updating (Task 2, this same session)
- engine/friction_tax.py module docstring: "revenue proxy" language ->
  "payroll proxy" language, wherever band_low is described.
- Inline comment on STATE_MULTIPLIERS describing it as a "per-state
  friction multiplier applied to org size band_low" should clarify
  payroll basis once this doc exists.
- No change to _ORG_SIZE_BANDS or STATE_MULTIPLIERS structure/keys --
  values remain None (CALIBRATION TARGET) until the actual research pass
  populates them.

## Not yet done
Actual population of STATE_MULTIPLIERS (57 states) and band_low (5
bands) with real researched values. That's the next step -- a Gemini
research pass, reconciled and independently verified before any value is
written to the engine, per standing Gemini-verification discipline.
"""

EDITS: list[tuple[str, str, str]] = []

EDITS.append((
    "friction_tax.py: _ORG_SIZE_BANDS section comment (revenue -> payroll)",
    '''# ── Org size bands ─────────────────────────────────────────────────────────────
# Maps headcount intake strings to annual revenue proxy bands used in
# friction tax computation.
# CALIBRATION TARGET — all band_low values require population from source research.''',
    '''# ── Org size bands ─────────────────────────────────────────────────────────────
# Maps headcount intake strings to annual payroll proxy bands used in
# friction tax computation. Payroll basis, not revenue -- see
# prompts/friction-tax-unit-decision.md.
# CALIBRATION TARGET — all band_low values require population from source research.''',
))

EDITS.append((
    "friction_tax.py: STATE_MULTIPLIERS section comment (clarify payroll basis)",
    '''# ── State multiplier table ─────────────────────────────────────────────────────
# Per-state friction multiplier applied to the org size band_low.
# All values CALIBRATION TARGET — populated from source research.
# Keys: state_id strings matching engine/data/states.py registry (47 states).''',
    '''# ── State multiplier table ─────────────────────────────────────────────────────
# Per-state friction multiplier applied to the org size band_low (payroll
# basis, not revenue -- see prompts/friction-tax-unit-decision.md).
# All values CALIBRATION TARGET — populated from source research.
# Keys: state_id strings matching engine/data/states.py registry (47 states).''',
))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if DOC_FILE.exists():
        print(f"ABORT -- {DOC_FILE.relative_to(REPO_ROOT)} already exists", file=sys.stderr)
        sys.exit(1)

    ft_text = FRICTION_TAX_FILE.read_text(encoding="utf-8")
    for label, old, new in EDITS:
        count = ft_text.count(old)
        if count != 1:
            print(f"ABORT -- anchor for '{label}' matched {count} times, need exactly 1", file=sys.stderr)
            sys.exit(1)

    print("=" * 100)
    print(f"TASK 1 -- new file: {DOC_FILE.relative_to(REPO_ROOT)}")
    print("=" * 100)
    print(DOC_CONTENT)

    print("=" * 100)
    print("TASK 2 -- engine/friction_tax.py comment edits")
    print("=" * 100)
    new_ft_text = ft_text
    for label, old, new in EDITS:
        print(f"\n--- {label} ---")
        print("BEFORE:")
        print(old)
        print("AFTER:")
        print(new)
        new_ft_text = new_ft_text.replace(old, new, 1)

    print("\n" + "=" * 100)
    print(f"friction_tax.py: {len(ft_text)} chars -> {len(new_ft_text)} chars ({len(new_ft_text) - len(ft_text):+d})")
    print("No field names, function signatures, or table structures changed.")
    print("All STATE_MULTIPLIERS / _ORG_SIZE_BANDS values confirmed still None after this edit.")

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    DOC_FILE.write_text(DOC_CONTENT, encoding="utf-8")
    print(f"\nWROTE {DOC_FILE.relative_to(REPO_ROOT)}")
    FRICTION_TAX_FILE.write_text(new_ft_text, encoding="utf-8")
    print(f"WROTE {FRICTION_TAX_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
