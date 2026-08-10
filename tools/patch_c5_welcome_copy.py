"""
PRV3 -- Category C, item C.5: add welcome/intro copy above the
existing "Before you start" intake screen. Same "intake" phase, no
FlowState change -- purely additional static content prepended to
IntakeForm's existing return JSX. Styling matches the existing
eyebrow/headline pattern already established by "Before you start" /
"A few things about your organization." (font-ui eyebrow, font-display
headline), with a font-ui body paragraph in between, consistent with
this file's existing font-ui-for-body-text / font-display-for-headings
convention.

Usage:
  python tools/patch_c5_welcome_copy.py --dry-run
  python tools/patch_c5_welcome_copy.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


D = "web/components/DiagnosticFlow.tsx"

edit(
    D,
    "  return (\n"
    '    <div className="max-w-md mx-auto px-6 py-16">\n'
    '      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">\n'
    "        Before you start\n"
    "      </p>\n"
    '      <h2 className="font-display text-2xl text-charcoal mb-8">\n'
    "        A few things about your organization.\n"
    "      </h2>\n",
    "  return (\n"
    '    <div className="max-w-md mx-auto px-6 py-16">\n'
    '      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">\n'
    "        Before you begin\n"
    "      </p>\n"
    '      <h2 className="font-display text-2xl text-charcoal mb-3">\n'
    "        This reflects what you see.\n"
    "      </h2>\n"
    '      <p className="font-ui text-sm text-gray-500 leading-relaxed mb-10">\n'
    "        What follows draws entirely on your own perceptions of your organization.\n"
    "        That's intentional — this is a starting point, not a full picture.\n"
    "        Principal Resolution's services bring more objective data and a solution\n"
    "        roadmap next, through a separate process built for exactly that.\n"
    "      </p>\n"
    "\n"
    '      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">\n'
    "        Before you start\n"
    "      </p>\n"
    '      <h2 className="font-display text-2xl text-charcoal mb-8">\n'
    "        A few things about your organization.\n"
    "      </h2>\n",
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
