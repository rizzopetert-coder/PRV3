"""
PRV3 -- Category C, item C.1: reorder PrivateOutput.tsx's synthesis
render blocks. Pure JSX reorder, each block's own conditional-render
logic (omit entirely if empty) is byte-for-byte unchanged, only the
order of the three blocks changes. Block comment labels relabeled to
match the new visual order (2 = observable indicators, 2b = liability
condition, 2c = framing text) so a future reader isn't misled by
"Block 2c" appearing before "Block 2".

Usage:
  python tools/patch_c1_reorder_synthesis.py --dry-run
  python tools/patch_c1_reorder_synthesis.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


P = "web/components/PrivateOutput.tsx"

edit(
    P,
    "      {/* Block 2 — Liability condition */}\n"
    '      <div className="py-4">\n'
    '        <p className="text-sm leading-[1.65] text-charcoal">\n'
    "          {liabilityText || payload.resolution_routing}\n"
    "        </p>\n"
    "      </div>\n"
    "      <Rule />\n"
    "\n"
    "      {/* Block 2b — Framing text (omit entirely if empty) */}\n"
    "      {framingText && (\n"
    "        <>\n"
    '          <div className="py-4">\n'
    '            <p className="text-sm leading-[1.65] text-charcoal">{framingText}</p>\n'
    "          </div>\n"
    "          <Rule />\n"
    "        </>\n"
    "      )}\n"
    "\n"
    "      {/* Block 2c — Observable indicators (omit entirely if empty) */}\n"
    "      {observableIndicators.length > 0 && (\n"
    "        <>\n"
    '          <div className="py-4">\n'
    '            <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">\n'
    "              Observable indicators\n"
    "            </p>\n"
    '            <ul className="space-y-1">\n'
    "              {observableIndicators.map((indicator, i) => (\n"
    '                <li key={i} className="flex gap-2 text-[13px] leading-[1.6] text-gray-500">\n'
    '                  <span className="text-gray-300 shrink-0" aria-hidden>—</span>\n'
    "                  <span>{indicator}</span>\n"
    "                </li>\n"
    "              ))}\n"
    "            </ul>\n"
    "          </div>\n"
    "          <Rule />\n"
    "        </>\n"
    "      )}",
    "      {/* Block 2 — Observable indicators (omit entirely if empty) */}\n"
    "      {observableIndicators.length > 0 && (\n"
    "        <>\n"
    '          <div className="py-4">\n'
    '            <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">\n'
    "              Observable indicators\n"
    "            </p>\n"
    '            <ul className="space-y-1">\n'
    "              {observableIndicators.map((indicator, i) => (\n"
    '                <li key={i} className="flex gap-2 text-[13px] leading-[1.6] text-gray-500">\n'
    '                  <span className="text-gray-300 shrink-0" aria-hidden>—</span>\n'
    "                  <span>{indicator}</span>\n"
    "                </li>\n"
    "              ))}\n"
    "            </ul>\n"
    "          </div>\n"
    "          <Rule />\n"
    "        </>\n"
    "      )}\n"
    "\n"
    "      {/* Block 2b — Liability condition */}\n"
    '      <div className="py-4">\n'
    '        <p className="text-sm leading-[1.65] text-charcoal">\n'
    "          {liabilityText || payload.resolution_routing}\n"
    "        </p>\n"
    "      </div>\n"
    "      <Rule />\n"
    "\n"
    "      {/* Block 2c — Framing text (omit entirely if empty) */}\n"
    "      {framingText && (\n"
    "        <>\n"
    '          <div className="py-4">\n'
    '            <p className="text-sm leading-[1.65] text-charcoal">{framingText}</p>\n'
    "          </div>\n"
    "          <Rule />\n"
    "        </>\n"
    "      )}",
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
