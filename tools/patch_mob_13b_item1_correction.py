"""
MOB update -- targeted one-item correction to Section 13b (Session Priority
Queue), not a full wholesale rewrite. Item 1 (severity follow-on gate) still
read pre-reframe framing ("two designs falsified, no third proposed") after
this session's Section 13a update (commits 835f26f..362aaaf) established the
real finding: all three candidate designs sit at the wrong architectural
layer, real fix is a SeverityResult per-state redesign, not yet scoped.

13b's own convention is wholesale-rewrite-at-closeout, not incremental sync
-- deliberately overridden this once because item 1 is actively wrong at the
top of the queue right now. Every other 13b item left untouched.

Re-verified fresh before writing: MOB header confirmed v4.186 (line 9),
CLAUDE.md cross-reference confirmed v4.186 (line 183), item 1's exact current
text confirmed via direct read immediately before this script was written.

Usage:
    python patch_mob_13b_item1_correction.py --dry-run
    python patch_mob_13b_item1_correction.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_PATH = Path("CLAUDE.md")

OLD_ITEM_1 = (
    '1. Severity follow-on state scoping (SEVER-19 and 13 more) -- OPEN DESIGN QUESTION, real '
    'production defect, unpatched. severity_trigger firing (engine/main.py:301) has zero per-state '
    'awareness -- a full-library scan found the same shape across 14 follow-on IDs (SEVER-02, 10, '
    '17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29), nearly the entirety of the Bucket 2/3 severity-'
    'wiring effort. Two gate designs were tried against real engine traces and both falsified in '
    'opposite directions (any-qualifying-state: too permissive, 21-42/58 states co-qualify per '
    'session; top-1-only: too restrictive, strips a state\'s own legitimately-intended trigger '
    'almost every time since a state ranking itself top-1 is the exception not the rule). No third '
    'design proposed -- not a build in progress, working tree reverted, nothing committed to engine '
    'code. Full record: prompts/severity-follow-on-gate-investigation-findings.md; Section 13a\'s '
    'Decision Register row already reflects this exact status. Correction to how this was '
    'characterized in the prior reconciliation report: not "ready for Gemini" -- that described an '
    'intermediate state one commit before the final downgrade to open-design-question, corrected '
    'here.'
)

NEW_ITEM_1 = (
    '1. Severity follow-on gate -- REFRAMED as an output-broadcast architecture gap, not an '
    'input-filtering problem. SeverityResult (engine/severity.py) has no per-state dimension, so no '
    'design that only filters which severity inputs get counted can fix it -- confirmed via all '
    'three candidates now assessed (any-qualifying-state, top-1-only, static-intended-state-'
    'membership). Not "falsified" the way the first two were -- a more final finding that all three '
    'sit at the wrong architectural layer entirely. Real fix direction: restructure '
    'SeverityResult/build_private_block() to carry severity per-state rather than one tier broadcast '
    'to every qualifying state -- not yet scoped, needs its own dedicated session, then a Gemini '
    'architecture review before any code (Tier 3, touches a core engine data contract). Full detail, '
    'the ATT-UT-01 reproduction, and the 16-of-32-IDs-never-assessed coverage finding: Section 13a '
    'Decision Register row -- not duplicated here. Do not resume this as "try a fourth input-'
    'filtering design."'
)

REPLACEMENTS = [
    (
        CLAUDE_PATH,
        "CLAUDE.md MOB version cross-reference",
        "| MOB version | v4.186 |",
        "| MOB version | v4.187 |",
    ),
    (
        MOB_PATH,
        "13b item 1 targeted correction",
        OLD_ITEM_1,
        NEW_ITEM_1,
    ),
]


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    file_texts = {}
    for path, _label, _old, _new in REPLACEMENTS:
        if path not in file_texts:
            file_texts[path] = path.read_text(encoding="utf-8")

    for path, label, old, new in REPLACEMENTS:
        text = file_texts[path]
        count = text.count(old)
        if count != 1:
            raise SystemExit(
                f"ABORT [{label}] in {path}: expected exactly 1 match, found {count}"
            )
        file_texts[path] = text.replace(old, new, 1)

    mob_text = file_texts[MOB_PATH]
    mob_lines = mob_text.split("\n")
    header_idx = 8
    assert mob_lines[header_idx].endswith("MOB v4.186"), (
        f"ABORT [header bump]: line 9 does not end with 'MOB v4.186': {mob_lines[header_idx]!r}"
    )
    mob_lines[header_idx] = mob_lines[header_idx].replace("v4.186", "v4.187")
    file_texts[MOB_PATH] = "\n".join(mob_lines)

    for path, new_text in file_texts.items():
        original = path.read_text(encoding="utf-8")
        if args.dry_run:
            print(f"\n{'=' * 80}\nDIFF: {path}\n{'=' * 80}")
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"{path} (before)",
                tofile=f"{path} (after)",
            )
            print("".join(diff))
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WROTE: {path}")

    if args.dry_run:
        print("\nDry run complete. No files written. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
