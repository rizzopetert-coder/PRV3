"""
PRV3 -- Update web/lib/session-store.test.ts for spliceLabel()'s new
required third parameter (Part 1, ancestry-labeling fix). Updates the
4 existing calls (all core parents, where existingLabels is never
actually consulted) and adds a new test exercising the real fix: a
depth-2 chain where the parent is itself a spliced, non-core question.

Usage:
  python tools/patch_ancestry_label_test.py --dry-run
  python tools/patch_ancestry_label_test.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


T = "web/lib/session-store.test.ts"

edit(
    T,
    'describe("spliceLabel", () => {\n'
    "  it(\"builds [parent][letter] from a real core parent's position\", () => {\n"
    '    expect(spliceLabel("Q11", 0)).toBe("11A");\n'
    '    expect(spliceLabel("Q11", 1)).toBe("11B");\n'
    '    expect(spliceLabel("Q22", 0)).toBe("22A");\n'
    "  });\n"
    "\n"
    "  it(\"Q28's conditional splice off Q06 labels as 6A\", () => {\n"
    '    expect(spliceLabel("Q06", 0)).toBe("6A");\n'
    "  });\n"
    "});",
    'describe("spliceLabel", () => {\n'
    "  it(\"builds [parent][letter] from a real core parent's position\", () => {\n"
    '    expect(spliceLabel("Q11", 0, {})).toBe("11A");\n'
    '    expect(spliceLabel("Q11", 1, {})).toBe("11B");\n'
    '    expect(spliceLabel("Q22", 0, {})).toBe("22A");\n'
    "  });\n"
    "\n"
    "  it(\"Q28's conditional splice off Q06 labels as 6A\", () => {\n"
    '    expect(spliceLabel("Q06", 0, {})).toBe("6A");\n'
    "  });\n"
    "\n"
    "  // Ancestry-labeling fix (Structures 1/2, this session): when the parent\n"
    "  // is itself a spliced (non-core) question, coreQuestionPosition() returns\n"
    "  // null for it -- the label must resolve from the parent's OWN already-\n"
    "  // computed entry in existingLabels, not fall back to its raw ID string.\n"
    '  it("resolves ancestry through a non-core parent instead of falling back to its raw ID", () => {\n'
    '    // SEVER-30 is core-less (splice off Q41, position 34) -- its own label\n'
    '    // "34A" is already in existingLabels by the time SEVER-31 is spliced.\n'
    '    const existingLabels = { "SEVER-30": "34A" };\n'
    '    expect(spliceLabel("SEVER-30", 0, existingLabels)).toBe("34AA");\n'
    "  });\n"
    "\n"
    '  it("falls back to the raw parent ID only if the parent truly has no resolved label yet", () => {\n'
    '    expect(spliceLabel("SEVER-30", 0, {})).toBe("SEVER-30A");\n'
    "  });\n"
    "});",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 200 chars): {old[:200]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
