"""
PRV3 -- Report Depth Initiative plan doc: Tier 1 closing status + Tier 2
note (overlap with the independently-tracked Diagnostic Dimension
Expansion effort, which wired both Tier 2 functions before this doc's own
Gemini gate was invoked).

Updates prompts/report-depth-initiative.md. Tiers 3 and 4 untouched.

Usage:
  python tools/patch_report_depth_initiative_tier_status.py --dry-run
  python tools/patch_report_depth_initiative_tier_status.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "prompts" / "report-depth-initiative.md"

EDITS: list[tuple[str, str, str]] = []

EDITS.append((
    "Tier 1 closing status",
    '''**Status: ready to build, no Gemini gate needed.** Pure rendering and payload pass-through — no new data flow, no new architecture, no new LLM call shape.

---

## Tier 2''',
    '''**Status: ready to build, no Gemini gate needed.** Pure rendering and payload pass-through — no new data flow, no new architecture, no new LLM call shape.

**Status update: DONE. Committed 3710f37.** All three sub-items built in one commit: framing_text/observable_indicators rendered in PrivateOutput.tsx, secondary_states rendered as closing acknowledgment, primary_asset_domain threaded through both Path 1 (answer/route.ts) and Path B (result/route.ts) plus PrivateOutput.tsx render. One correction to this doc's original framing: primary_asset_domain was not "dropped at the route.ts layer" as originally described -- it had no field on PrivateOutputPayload at all yet, one layer earlier than stated. One scope addition beyond original plan: Path B was included (not originally scoped as Path-1-only, but the value is Path-independent so both routes now carry it). Follow-on fix required: DevDiagnosticPreviewPayload (web/lib/dev-diagnostic-preview.ts) needed a matching field addition, caught by tsc, not proactive discovery -- worth remembering that grep-based searches for PrivateOutputPayload references will miss deliberately-separate matching-shape types.

---

## Tier 2''',
))

EDITS.append((
    "Tier 2 closing status",
    '''**Status: needs a Gemini structural review before building.** The underlying math already exists and is already cleared, but adding either to the output contract is genuine output-contract/architecture surface area (new top-level payload fields, new client-facing meaning) — **not yet sent to Gemini.**

---

## Tier 3''',
    '''**Status: needs a Gemini structural review before building.** The underlying math already exists and is already cleared, but adding either to the output contract is genuine output-contract/architecture surface area (new top-level payload fields, new client-facing meaning) — **not yet sent to Gemini.**

**Status update: DONE, ahead of this initiative's own sequencing.** Both compute_causation_pattern() and compute_cascade_risk() were wired into the output contract under a separately-tracked effort (Diagnostic Dimension Expansion, see prompts/diagnostic-dimension-expansion.md), committed 1b75a1b and f4ee405 respectively, before this doc's own "needs a Gemini structural review before building" gate was invoked. This happened because the two initiatives were scoped and tracked independently and the overlap wasn't caught until Report Depth Initiative's Tier 1 build began. No harm done -- Gemini did review compute_cascade_risk() during Diagnostic Dimension Expansion's own process (see that doc), so the substance of the gate was satisfied, just not procedurally through this doc's own sequencing. Flagging for the record: when two plan docs reference the same underlying engine functions, check for overlap before either one's build phase starts, not after.

---

## Tier 3''',
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
    print("\nTiers 3 and 4 confirmed untouched.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    TARGET_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
