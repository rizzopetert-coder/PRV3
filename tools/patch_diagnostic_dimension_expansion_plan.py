"""
PRV3 -- Durable Plan Write: Diagnostic Dimension Expansion (5-Candidate Decision)

Creates prompts/diagnostic-dimension-expansion.md, matching the existing
prompts/*.md handoff-doc convention (e.g. prompts/report-depth-initiative.md).
Content supplied verbatim by Pete, with "[today's date]" filled in.

This script is a plan-write only -- no engine/, contract.py, types.ts, or
route.ts changes happen here, per explicit instruction not to begin
implementation of candidates 1/2/4 in this pass.

Usage:
  python tools/patch_diagnostic_dimension_expansion_plan.py --dry-run
  python tools/patch_diagnostic_dimension_expansion_plan.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "prompts" / "diagnostic-dimension-expansion.md"

DECISION_DATE = "2026-07-27"

CONTENT = f"""# Diagnostic Dimension Expansion — Decision Record

Decided {DECISION_DATE}, Pete confirmed each candidate individually after two
rounds of Gemini reconciliation, the first round containing fabricated
mechanism detail (caught and corrected via direct CC source read), the
second round verified clean against real ground truth.

## Ground truth (verified, engine/*.py, CC direct-read)

- `compute_cascade_risk(accumulated_vector: dict) -> float`
  engine/accumulation.py:381. Shannon-entropy dispersion across the 4
  `*_liability` fields only, × intensity vs. locked MC_CENTROID_39,
  capped at 1.0. Real, unit-tested (tools/test_accumulation.py checks
  11-12), unwired — zero references in contract.py/main.py/
  resolution_families.py.

- `compute_causation_pattern(accumulated_vector: dict, routing: OutputRouting) -> dict`
  engine/output.py:459. Returns
  `{{"pattern": "single_point"|"diffuse"|"insufficient_signal",
  "dispersion": float, "qualified_state_count": int}}`.
  qualified_state_count (via routing.qualified_states) is the primary
  signal; dispersion is a tiebreak only when exactly 1 state qualifies.
  Real, unit-tested, unwired.

- `_PRIVATE_OUTPUT_FIELDS` — real constant, engine/contract.py:527,
  currently `{{"opening_text", "resolution_routing", "friction_tax_estimate"}}`.

- `PrivateOutputPayload` — web/lib/types.ts:122. Current shape: synthesis,
  primary_state/secondary_states, severity, resolution_family/
  resolution_routing, friction_tax_estimate, intake, dimension_summary.

- Path 1 mapping point: web/app/api/diagnostic/session/answer/route.ts,
  builds PrivateOutputPayload at Q34 (line 357). Confirmed the only other
  file besides web/app/api/result/route.ts (Path B) importing
  PrivateOutputPayload.

- `resolution_families.py`: three pure state_id-only lookup functions
  (get_family, get_primary_family, get_all_families) — no signal input
  of any kind today. No existing hook for causation_pattern to attach to.

- `engine/data/states.py` StateProfile fields: state_id, state_name,
  primary_dimension, dimensional_vector, signal_weight, cluster_id,
  liability_axes, asset_axes, severity_range, resolution_family. No
  reversibility-adjacent field exists — a reversibility_tier would be
  genuinely new, not an extension.

- `compute_friction_tax(state_ids, severity_tier, org_size) -> dict` —
  engine/friction_tax.py:152. No urgency/time parameter exists. Only
  severity-tied multiplier is LOCKED SEVERITY_SCALAR
  {{Emerging: 0.6, Entrenched: 1.0, Endemic: 1.4}}. STATE_MULTIPLIERS and
  _ORG_SIZE_BANDS.band_low are still None/CALIBRATION TARGET everywhere
  — calibration_complete is False for every real call today.

## Decisions

1. **Trajectory / directionality — BUILD.**
   Derive from answers_log early/late-session vector delta + duration_band.
   No new questions, no new vector fields, no new intake.

2. **Cascade risk — BUILD.**
   Wire existing compute_cascade_risk() into assemble_output() /
   contract.py private_output shape / PrivateOutputPayload (types.ts) /
   answer/route.ts plumbing for Path 1.

3. **Reversibility / structural momentum — PARK as internal synthesis
   context only.**
   Not a surfaced output field, not a UI element. Feeds
   engine/output_synthesis.py's prompt context if/when built. Rationale
   (Gemini, unchallenged): existing Entrenched/Endemic severity-tier
   prose already carries an implicit escalating-entrenchment read; a
   formal score risks over-engineering for taxonomy completeness (P-12).

4. **SPOF vs. diffuse causation — BUILD, output contract only.**
   Wire existing compute_causation_pattern() into assemble_output() /
   contract.py / PrivateOutputPayload / route plumbing, same shape as
   cascade risk. resolution_families.py routing influence explicitly
   SPLIT OFF — routing functions are pure state_id lookups today with no
   signal input; adding causation_pattern-based routing is new surface
   area (new parameter or new function) and is a separate later decision,
   not in this build.

5. **Time-to-consequence / urgency window — DEFER.**
   No real existing signal to derive from (friction_tax has no
   urgency/time parameter; the earlier 0.8x-1.5x claim connecting them
   was fabricated by Gemini and does not exist in code). Would require
   genuinely new intake. Not started.

## Build order (proposed, not yet sequenced by Pete)

Candidates 1, 2, and 4's output-contract portion all touch the same three
files (contract.py, types.ts, answer/route.ts) — sequencing and whether
they land as one PR or three is an open implementation question for
Claude Code to raise before starting, not decided here.
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
