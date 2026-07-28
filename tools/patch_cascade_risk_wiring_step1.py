"""
PRV3 -- Diagnostic Dimension Expansion, Step 1 of 3: Cascade Risk wiring

Wires compute_cascade_risk(session.accumulated_vector) -- real, bare-float
return, already unit-tested in tools/test_accumulation.py -- into
assemble_output()'s private_output dict, following the same in-body pure-
function-call pattern already used for _compute_asset_score() /
_compute_dimension_summary() in engine/contract.py.

Field placement confirmed with Pete: nests inside private_output, not a
top-level output key.

Four files touched -- one more than the three originally scoped, found by
direct read while building this patch, not assumed:
  1. engine/contract.py -- two separate field-list sites found by grep, not
     just the one constant originally cited: the private_output dict
     construction (~line 419) AND the _PRIVATE_OUTPUT_FIELDS validation
     set (~line 527). Both updated together so validate_schema() and the
     actual output stay in sync.
  2. web/lib/engine-client.ts -- EngineResult.private_output (~line 126) is
     a SEPARATE strict type mirroring the raw Python engine response,
     distinct from PrivateOutputPayload. Not in the original file list,
     but structurally required for route.ts to type-check when it reads
     engineResult.private_output.cascade_risk. Confirmed necessary by
     direct read, not a judgment call.
  3. web/lib/types.ts -- PrivateOutputPayload.cascade_risk, landed OPTIONAL
     (cascade_risk?: number) per Pete's explicit confirmation: Path B's
     web/app/api/result/route.ts also constructs a PrivateOutputPayload
     object literal and is explicitly out of scope for this commit: making
     the field required would force touching that file too. Optional keeps
     this commit to exactly Path 1, flip to required + wire Path B in a
     later, separate step once decided.
  4. web/app/api/diagnostic/session/answer/route.ts -- Path 1's mapping
     point, threads engineResult.private_output.cascade_risk into the
     privatePayload construction at Q34.

Scope discipline: web/app/api/result/route.ts (Path B) is deliberately NOT
touched this commit, per explicit instruction and the optional-field
decision above.

Usage:
  python tools/patch_cascade_risk_wiring_step1.py --dry-run
  python tools/patch_cascade_risk_wiring_step1.py --write
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

EDITS: list[tuple[Path, str, str, str]] = []  # (file, label, old, new)

# --- engine/contract.py: 3 edits ---------------------------------------------

EDITS.append((
    CONTRACT_FILE,
    "contract.py: import compute_cascade_risk",
    "from engine.accumulation import IntakeData, StateRanking",
    "from engine.accumulation import IntakeData, StateRanking, compute_cascade_risk",
))

EDITS.append((
    CONTRACT_FILE,
    "contract.py: private_output dict construction",
    '''    private_output = {
        "opening_text":          priv.state_name if priv else "",
        "resolution_routing":    priv.resolution_family if priv else "",
        "friction_tax_estimate": priv.friction_tax_estimate if priv else None,
    }''',
    '''    private_output = {
        "opening_text":          priv.state_name if priv else "",
        "resolution_routing":    priv.resolution_family if priv else "",
        "friction_tax_estimate": priv.friction_tax_estimate if priv else None,
        "cascade_risk":          compute_cascade_risk(session.accumulated_vector),
    }''',
))

EDITS.append((
    CONTRACT_FILE,
    "contract.py: _PRIVATE_OUTPUT_FIELDS validation set",
    '''_PRIVATE_OUTPUT_FIELDS = {
    "opening_text", "resolution_routing", "friction_tax_estimate",
}''',
    '''_PRIVATE_OUTPUT_FIELDS = {
    "opening_text", "resolution_routing", "friction_tax_estimate", "cascade_risk",
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
  };''',
    '''  private_output: {
    opening_text: string;
    resolution_routing: string;
    friction_tax_estimate: number | null;
    cascade_risk: number;
  };''',
))

# --- web/lib/types.ts: 1 edit --------------------------------------------------

EDITS.append((
    TYPES_FILE,
    "types.ts: PrivateOutputPayload.cascade_risk (optional -- Path B not wired this commit)",
    '''  // Economic (nullable)
  friction_tax_estimate: FrictionTaxEstimate | null;''',
    '''  // Economic (nullable)
  friction_tax_estimate: FrictionTaxEstimate | null;

  // Cross-Dimensional Cascade Risk -- Shannon-entropy liability dispersion
  // x session intensity, [0.0, 1.0]. Optional: Path 1 populates this
  // (web/app/api/diagnostic/session/answer/route.ts); Path B
  // (web/app/api/result/route.ts) does not yet -- deliberate, separate
  // decision, not an oversight.
  cascade_risk?: number;''',
))

# --- web/app/api/diagnostic/session/answer/route.ts: 1 edit -------------------

EDITS.append((
    ANSWER_ROUTE_FILE,
    "answer/route.ts: thread cascade_risk into privatePayload",
    '''    // friction_tax_estimate: null — CALIBRATION TARGET, STATE_MULTIPLIERS
    // not set, same as Path B.
    friction_tax_estimate: null,

    intake: session.intake,''',
    '''    // friction_tax_estimate: null — CALIBRATION TARGET, STATE_MULTIPLIERS
    // not set, same as Path B.
    friction_tax_estimate: null,

    cascade_risk: engineResult.private_output.cascade_risk,

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
