"""
PRV3 -- Diagnostic Dimension Expansion, Step 2 of 3: SPOF vs. Diffuse
Causation wiring

Wires compute_causation_pattern(session.accumulated_vector, routing)
(engine/output.py:459, real, unit-tested, previously unwired) into
assemble_output()'s private_output dict, following the exact same pattern
Step 1 established for cascade_risk. `routing` is already a local variable
in assemble_output() (line 311: routing = session.output_package.routing),
in scope well before the private_output construction -- no new plumbing
needed to reach it.

Real return shape (engine/output.py:459, confirmed by direct read):
  {"pattern": "single_point"|"diffuse"|"insufficient_signal",
   "dispersion": float, "qualified_state_count": int}

Field placement: nested inside private_output, alongside opening_text,
resolution_routing, friction_tax_estimate, cascade_risk -- same decision
as Step 1, extended.

Four files touched, matching Step 1's precedent exactly:
  1. engine/contract.py -- import compute_causation_pattern from
     engine.output (existing import line already has OutputPackage,
     OutputRouting); add to private_output dict construction and
     _PRIVATE_OUTPUT_FIELDS.
  2. web/lib/engine-client.ts -- EngineResult.private_output gains
     causation_pattern with the real 3-key nested shape.
  3. web/lib/types.ts -- PrivateOutputPayload gains causation_pattern,
     landed OPTIONAL (same Path-B-untouched scoping as cascade_risk).
  4. web/app/api/diagnostic/session/answer/route.ts -- threads
     engineResult.private_output.causation_pattern into privatePayload.

web/app/api/result/route.ts (Path B) deliberately NOT touched, matching
Step 1's scoping decision.

Usage:
  python tools/patch_causation_pattern_wiring_step2.py --dry-run
  python tools/patch_causation_pattern_wiring_step2.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACT_FILE = REPO_ROOT / "engine" / "contract.py"
ENGINE_CLIENT_FILE = REPO_ROOT / "web" / "lib" / "engine-client.ts"
TYPES_FILE = REPO_ROOT / "web" / "lib" / "types.ts"
ANSWER_ROUTE_FILE = REPO_ROOT / "web" / "app" / "api" / "diagnostic" / "session" / "answer" / "route.ts"

EDITS: list[tuple[Path, str, str, str]] = []

# --- engine/contract.py: 3 edits ---------------------------------------------

EDITS.append((
    CONTRACT_FILE,
    "contract.py: import compute_causation_pattern",
    "from engine.output import OutputPackage, OutputRouting",
    "from engine.output import OutputPackage, OutputRouting, compute_causation_pattern",
))

EDITS.append((
    CONTRACT_FILE,
    "contract.py: private_output dict construction",
    '''    private_output = {
        "opening_text":          priv.state_name if priv else "",
        "resolution_routing":    priv.resolution_family if priv else "",
        "friction_tax_estimate": priv.friction_tax_estimate if priv else None,
        "cascade_risk":          compute_cascade_risk(session.accumulated_vector),
    }''',
    '''    private_output = {
        "opening_text":          priv.state_name if priv else "",
        "resolution_routing":    priv.resolution_family if priv else "",
        "friction_tax_estimate": priv.friction_tax_estimate if priv else None,
        "cascade_risk":          compute_cascade_risk(session.accumulated_vector),
        "causation_pattern":     compute_causation_pattern(session.accumulated_vector, routing),
    }''',
))

EDITS.append((
    CONTRACT_FILE,
    "contract.py: _PRIVATE_OUTPUT_FIELDS validation set",
    '''_PRIVATE_OUTPUT_FIELDS = {
    "opening_text", "resolution_routing", "friction_tax_estimate", "cascade_risk",
}''',
    '''_PRIVATE_OUTPUT_FIELDS = {
    "opening_text", "resolution_routing", "friction_tax_estimate", "cascade_risk",
    "causation_pattern",
}''',
))

# --- web/lib/engine-client.ts: 1 edit -----------------------------------------

EDITS.append((
    ENGINE_CLIENT_FILE,
    "engine-client.ts: EngineResult.private_output type",
    '''  private_output: {
    opening_text: string;
    resolution_routing: string;
    friction_tax_estimate: number | null;
    cascade_risk: number;
  };''',
    '''  private_output: {
    opening_text: string;
    resolution_routing: string;
    friction_tax_estimate: number | null;
    cascade_risk: number;
    causation_pattern: {
      pattern: "single_point" | "diffuse" | "insufficient_signal";
      dispersion: number;
      qualified_state_count: number;
    };
  };''',
))

# --- web/lib/types.ts: 1 edit --------------------------------------------------

EDITS.append((
    TYPES_FILE,
    "types.ts: PrivateOutputPayload.causation_pattern (optional -- Path B not wired this commit)",
    '''  // Cross-Dimensional Cascade Risk -- Shannon-entropy liability dispersion
  // x session intensity, [0.0, 1.0]. Optional: Path 1 populates this
  // (web/app/api/diagnostic/session/answer/route.ts); Path B
  // (web/app/api/result/route.ts) does not yet -- deliberate, separate
  // decision, not an oversight.
  cascade_risk?: number;''',
    '''  // Cross-Dimensional Cascade Risk -- Shannon-entropy liability dispersion
  // x session intensity, [0.0, 1.0]. Optional: Path 1 populates this
  // (web/app/api/diagnostic/session/answer/route.ts); Path B
  // (web/app/api/result/route.ts) does not yet -- deliberate, separate
  // decision, not an oversight.
  cascade_risk?: number;

  // SPOF vs. Diffuse Causation. Same Path 1 / Path B scoping as
  // cascade_risk above -- optional, Path B not wired this commit.
  causation_pattern?: {
    pattern: "single_point" | "diffuse" | "insufficient_signal";
    dispersion: number;
    qualified_state_count: number;
  };''',
))

# --- web/app/api/diagnostic/session/answer/route.ts: 1 edit -------------------

EDITS.append((
    ANSWER_ROUTE_FILE,
    "answer/route.ts: thread causation_pattern into privatePayload",
    '''    cascade_risk: engineResult.private_output.cascade_risk,

    intake: session.intake,''',
    '''    cascade_risk: engineResult.private_output.cascade_risk,
    causation_pattern: engineResult.private_output.causation_pattern,

    intake: session.intake,''',
))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    file_texts: dict[Path, str] = {}
    for path in {e[0] for e in EDITS}:
        file_texts[path] = path.read_text(encoding="utf-8")

    for path, label, old, new in EDITS:
        count = file_texts[path].count(old)
        if count != 1:
            print(f"ABORT -- anchor for '{label}' matched {count} times in {path.relative_to(REPO_ROOT)}, need exactly 1", file=sys.stderr)
            sys.exit(1)

    print("=" * 100)
    for path, label, old, new in EDITS:
        print(f"\n--- {label} ({path.relative_to(REPO_ROOT)}) ---")
        print("BEFORE:")
        print(old)
        print("AFTER:")
        print(new)
    print("\n" + "=" * 100)

    new_texts: dict[Path, str] = dict(file_texts)
    for path, label, old, new in EDITS:
        new_texts[path] = new_texts[path].replace(old, new, 1)

    print("Files touched:")
    for path in file_texts:
        delta = len(new_texts[path]) - len(file_texts[path])
        print(f"  {path.relative_to(REPO_ROOT)}: {delta:+d} chars")

    print("\nweb/app/api/result/route.ts (Path B): confirmed NOT touched by this script.")

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    for path, text in new_texts.items():
        path.write_text(text, encoding="utf-8")
        print(f"\nWROTE {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
