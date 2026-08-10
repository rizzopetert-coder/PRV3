"""
PRV3 -- C.3/C.4 completion: /book/toc hub page (built separately, see
web/app/book/toc/page.tsx, web/lib/book-state-index.ts,
web/lib/state-slug.ts) plus wiring PrivateOutput.tsx to render
descriptive_prose for the primary state (Part 2) and hyperlink +
short-version secondary states (Part 3).

Verified before writing:
  - descriptive_prose confirmed 58/58 states populated in
    engine/data/states.py, and confirmed flowing through to the live
    payload in BOTH Path 1 (answer/route.ts:273) and Path B
    (result/route.ts, multiple lines) -- not just the engine side.
  - First-sentence extraction tested against all 58 real
    descriptive_prose values: 57/58 have a clean multi-word first
    sentence at the first ". " boundary. One exception,
    cultural_overtime, is a single sentence with no internal period --
    not broken, just means its "short version" equals the full text.
    Flagged, not a bug -- the extraction logic handles it naturally
    (no match found -> falls through to the whole string).

Usage:
  python tools/patch_c3_c4_book_and_render.py --dry-run
  python tools/patch_c3_c4_book_and_render.py --write
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

# ---------------------------------------------------------------------
# 1. Imports -- stateIdToSlug for the secondary-state links.
# ---------------------------------------------------------------------

edit(
    P,
    'import { ConstellationField, severityAccentTokens } from "@/components/ConstellationField";',
    'import { ConstellationField, severityAccentTokens } from "@/components/ConstellationField";\n'
    'import { stateIdToSlug } from "@/lib/state-slug";\n'
    "\n"
    "// First-sentence extraction for a secondary state's short-version summary\n"
    "// (Block 4b) -- splits on the first sentence-ending period, not a hard\n"
    "// character-count truncation. Falls through to the whole string when no\n"
    '// internal ". " boundary exists (confirmed against all 58 real\n'
    "// descriptive_prose values this session -- one state, cultural_overtime,\n"
    "// is a single sentence with no internal boundary; this is that case\n"
    "// resolving correctly, not a bug).\n"
    "function firstSentence(text: string): string {\n"
    "  const match = text.match(/\\.\\s/);\n"
    "  if (!match || match.index === undefined) return text;\n"
    "  return text.slice(0, match.index + 1);\n"
    "}",
)

# ---------------------------------------------------------------------
# 2. Block 1 -- descriptive_prose for the primary state, mirroring the
#    severity anchor's own badge-plus-plainspoken-text pattern.
# ---------------------------------------------------------------------

edit(
    P,
    "        <p className=\"text-[12px] text-gray-400 leading-relaxed\">\n"
    "          {SEVERITY_ANCHOR[payload.severity]}\n"
    "        </p>\n"
    "      </div>\n"
    "\n"
    "      {/* Block 1a — Headline (omit entirely if empty) */}",
    "        {payload.primary_state.descriptive_prose && (\n"
    "          <p className=\"text-[12px] text-gray-400 leading-relaxed mb-2\">\n"
    "            {payload.primary_state.descriptive_prose}\n"
    "          </p>\n"
    "        )}\n"
    "        <p className=\"text-[12px] text-gray-400 leading-relaxed\">\n"
    "          {SEVERITY_ANCHOR[payload.severity]}\n"
    "        </p>\n"
    "      </div>\n"
    "\n"
    "      {/* Block 1a — Headline (omit entirely if empty) */}",
)

# ---------------------------------------------------------------------
# 3. Block 4b -- hyperlink secondary state names to /book/toc#{slug},
#    add each one's short-version descriptive_prose beneath the name.
# ---------------------------------------------------------------------

edit(
    P,
    "      {/* Block 4b — Secondary states acknowledgment (omit entirely if none) */}\n"
    "      {payload.secondary_states.length > 0 && (\n"
    '        <div className="py-4">\n'
    '          <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">\n'
    "            Also present\n"
    "          </p>\n"
    '          <p className="text-[13px] text-gray-500">\n'
    "            {payload.secondary_states\n"
    '              .map((s) => `${s.name} (${(s.weight * 100).toFixed(0)}%)`)\n'
    '              .join(", ")}\n'
    "          </p>\n"
    "        </div>\n"
    "      )}",
    "      {/* Block 4b — Secondary states acknowledgment (omit entirely if none) */}\n"
    "      {payload.secondary_states.length > 0 && (\n"
    '        <div className="py-4">\n'
    '          <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">\n'
    "            Also present\n"
    "          </p>\n"
    '          <ul className="space-y-3">\n'
    "            {payload.secondary_states.map((s) => (\n"
    '              <li key={s.id}>\n'
    '                <a\n'
    '                  href={`/book/toc#${stateIdToSlug(s.id)}`}\n'
    '                  className="text-[13px] font-medium text-charcoal hover:underline"\n'
    "                >\n"
    "                  {s.name} ({(s.weight * 100).toFixed(0)}%)\n"
    "                </a>\n"
    "                {s.descriptive_prose && (\n"
    '                  <p className="text-[12px] text-gray-500 leading-relaxed mt-0.5">\n'
    "                    {firstSentence(s.descriptive_prose)}\n"
    "                  </p>\n"
    "                )}\n"
    "              </li>\n"
    "            ))}\n"
    "          </ul>\n"
    "        </div>\n"
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
