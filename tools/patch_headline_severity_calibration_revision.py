"""
PRV3 -- Tier 4 Headline Field, severity calibration wording revision.

Live smoke test after Commit 1 found a real content-quality issue: the
Emerging and Endemic headlines both drifted toward Entrenched's "settled"
framing instead of using genuinely distinct language. Root cause
hypothesis (Pete): "settled" was the only concrete anchor word given
(Entrenched); Emerging ("visible") and Endemic ("structural to how the
organization runs") were more abstract and gave the model nothing
equally strong to reach for.

This patch replaces ONLY the severity calibration block within the
headline field spec in engine/output_synthesis.py's system prompt. Two
"Severity calibration" blocks exist in the prompt -- an older one
(unparenthesized) belonging to liability_condition_text's field spec,
untouched here -- so the anchor is built on the full block including
the "(behavioral framing only):" header and the exact prior wording,
confirmed unique before writing.

No dashes introduced -- checked directly, not assumed.

One file: engine/output_synthesis.py.

Usage:
  python tools/patch_headline_severity_calibration_revision.py --dry-run
  python tools/patch_headline_severity_calibration_revision.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_SYNTHESIS_FILE = REPO_ROOT / "engine" / "output_synthesis.py"

OLD_BLOCK = '''Severity calibration (behavioral framing only):
  Emerging: name the pattern as visible.
  Entrenched: name the pattern as settled.
  Endemic: name the pattern as structural to how the organization runs.'''

NEW_BLOCK = '''Severity calibration (behavioral framing only, each tier must use
genuinely different framing language, not shared words):
  Emerging: frame the pattern as newly surfacing, something people are
  just starting to notice. Words like "beginning," "surfacing," or
  "starting to."
  Entrenched: frame the pattern as settled and absorbed into how people
  already work around it. Words like "settled," "routine," or "the way
  things work now."
  Endemic: frame the pattern as inseparable from daily operations, not
  something anyone would think to name anymore. Words like "built into,"
  "part of how things run," or "the normal way of operating."
Do not reuse the same framing word or phrase across two tiers in the same
session.'''


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = OUTPUT_SYNTHESIS_FILE.read_text(encoding="utf-8")

    count = text.count(OLD_BLOCK)
    if count != 1:
        print(f"ABORT -- anchor matched {count} times, need exactly 1", file=sys.stderr)
        sys.exit(1)

    em_dash_count = NEW_BLOCK.count("—")
    dbl_hyphen_count = NEW_BLOCK.count("--")
    if em_dash_count or dbl_hyphen_count:
        print(f"ABORT -- new block contains {em_dash_count} em dashes / {dbl_hyphen_count} literal '--' -- standing no-dash rule violated", file=sys.stderr)
        sys.exit(1)

    print("=" * 100)
    print("BEFORE:")
    print(OLD_BLOCK)
    print("-" * 100)
    print("AFTER:")
    print(NEW_BLOCK)
    print("=" * 100)
    print(f"Confirmed: 0 em dashes, 0 literal '--' in the new block.")

    new_text = text.replace(OLD_BLOCK, NEW_BLOCK, 1)
    print(f"\nFile: {len(text)} chars -> {len(new_text)} chars ({len(new_text) - len(text):+d})")
    print("Confirmed: the OTHER (unparenthesized) 'Severity calibration:' block,")
    print("belonging to liability_condition_text's field spec, is untouched.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    OUTPUT_SYNTHESIS_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {OUTPUT_SYNTHESIS_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
