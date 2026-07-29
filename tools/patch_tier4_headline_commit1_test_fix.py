"""
PRV3 -- Tier 4 Headline Field, Commit 1 follow-up fix.

Running the full tools/test_output_synthesis.py suite after Commit 1
landed surfaced real, legitimate failures -- not because Commit 1's core
edits were wrong, but because they were incomplete. The file has 4
sample-JSON fixtures used to test _parse_synthesis_response()'s various
parsing paths (markdown-fence stripping, prose-embedded-JSON recovery,
etc.), and 3 of them (valid_json, not_list_json, fenced_json) don't
include a "headline" key. Since headline is now folded into the
required-fields check (`if not liability or not framing or not
resolution or not headline`), the parser was correctly routing all of
these fixtures to the fallback path -- exactly as designed, just not
what those specific tests expected, since they predate headline.

The 4th fixture, missing_liability_json, intentionally leaves
liability_condition_text empty to test that ANY missing required field
triggers fallback -- it doesn't need headline added, since it already
correctly triggers fallback regardless (confirmed, not assumed: it was
not among the failures).

Also fixes REQUIRED_KEYS (used by the get_fallback_synthesis structure
check) and its check label, which still said "5 correct keys" -- this
one wasn't a silent risk, it was an active, visible test failure caught
in the same run: `get_fallback_synthesis: returns dict with 5 correct
keys` failed with `got keys: {...6 keys including headline...}`.

One file: tools/test_output_synthesis.py.

Usage:
  python tools/patch_tier4_headline_commit1_test_fix.py --dry-run
  python tools/patch_tier4_headline_commit1_test_fix.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_FILE = REPO_ROOT / "tools" / "test_output_synthesis.py"

TEST_HEADLINE = "The pattern has become part of how this organization runs."

EDITS: list[tuple[str, str, str]] = []

EDITS.append((
    "valid_json fixture gains headline",
    '''valid_json = json.dumps({
    "liability_condition_text":     "The decision-making pattern is structural.",
    "asset_resolution_anchor_text": "Governance discipline is intact.",
    "framing_text":                 "An organizational pattern is affecting decision-making.",
    "observable_indicators":        ["Decisions escalate to senior leadership.", "Projects stall."],
    "resolution_framing_text":      "Groundwork at this stage produces a clear structural account.",
    "synthesis_confidence":         0.82,
})''',
    f'''valid_json = json.dumps({{
    "liability_condition_text":     "The decision-making pattern is structural.",
    "asset_resolution_anchor_text": "Governance discipline is intact.",
    "framing_text":                 "An organizational pattern is affecting decision-making.",
    "observable_indicators":        ["Decisions escalate to senior leadership.", "Projects stall."],
    "resolution_framing_text":      "Groundwork at this stage produces a clear structural account.",
    "headline":                     "{TEST_HEADLINE}",
    "synthesis_confidence":         0.82,
}})''',
))

EDITS.append((
    "not_list_json fixture gains headline",
    '''not_list_json = json.dumps({
    "liability_condition_text":     "Some liability text.",
    "asset_resolution_anchor_text": "",
    "framing_text":                 "Some framing text.",
    "observable_indicators":        "should be a list not a string",
    "resolution_framing_text":      "Some resolution text.",
    "synthesis_confidence":         0.6,
})''',
    f'''not_list_json = json.dumps({{
    "liability_condition_text":     "Some liability text.",
    "asset_resolution_anchor_text": "",
    "framing_text":                 "Some framing text.",
    "observable_indicators":        "should be a list not a string",
    "resolution_framing_text":      "Some resolution text.",
    "headline":                     "{TEST_HEADLINE}",
    "synthesis_confidence":         0.6,
}})''',
))

EDITS.append((
    "fenced_json fixture gains headline (reused by 4 downstream test groups: fenced, bare-fenced, unfenced regression guard, prose-embedded)",
    '''fenced_json = json.dumps({
    "liability_condition_text":     "The decision-making pattern is structural.",
    "asset_resolution_anchor_text": "Governance discipline is intact.",
    "framing_text":                 "An organizational pattern is affecting decision-making.",
    "observable_indicators":        ["Decisions escalate to senior leadership."],
    "resolution_framing_text":      "Groundwork at this stage produces a clear structural account.",
    "synthesis_confidence":         0.82,
})''',
    f'''fenced_json = json.dumps({{
    "liability_condition_text":     "The decision-making pattern is structural.",
    "asset_resolution_anchor_text": "Governance discipline is intact.",
    "framing_text":                 "An organizational pattern is affecting decision-making.",
    "observable_indicators":        ["Decisions escalate to senior leadership."],
    "resolution_framing_text":      "Groundwork at this stage produces a clear structural account.",
    "headline":                     "{TEST_HEADLINE}",
    "synthesis_confidence":         0.82,
}})''',
))

EDITS.append((
    "REQUIRED_KEYS gains headline + check label corrected",
    '''REQUIRED_KEYS = {
    "liability_condition_text",
    "asset_resolution_anchor_text",
    "framing_text",
    "observable_indicators",
    "resolution_framing_text",
}

fb_entry = get_fallback_synthesis("Groundwork", "Entrenched")

check(
    "get_fallback_synthesis: returns dict with 5 correct keys",
    set(fb_entry.keys()) == REQUIRED_KEYS,
    f"got keys: {set(fb_entry.keys())}",
)''',
    '''REQUIRED_KEYS = {
    "liability_condition_text",
    "asset_resolution_anchor_text",
    "framing_text",
    "observable_indicators",
    "resolution_framing_text",
    "headline",
}

fb_entry = get_fallback_synthesis("Groundwork", "Entrenched")

check(
    "get_fallback_synthesis: returns dict with 6 correct keys",
    set(fb_entry.keys()) == REQUIRED_KEYS,
    f"got keys: {set(fb_entry.keys())}",
)''',
))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = TEST_FILE.read_text(encoding="utf-8")

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
    print("\nmissing_liability_json fixture confirmed NOT touched -- already correctly")
    print("triggers fallback via its intentionally-empty liability_condition_text,")
    print("headline presence/absence doesn't change that test's outcome.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    TEST_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {TEST_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
