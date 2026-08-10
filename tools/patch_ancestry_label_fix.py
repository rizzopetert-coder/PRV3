"""
PRV3 -- Part 1 (ancestry-labeling fix), prerequisite for Structures 1/2.

Verified before writing (Part 0): Gemini's snippet assumed
answers_log entries carry spliced_question_id/parent_question_id
fields. They don't -- AnswerLogEntry is exactly {question_id,
option_id}, confirmed by direct read of web/lib/session-store.ts.
The real mechanism is session.question_labels (question_id -> already-
computed label string, populated once at splice time), and
spliceLabel(parentQuestionId, letterIndex) currently falls back to the
raw parent ID string when coreQuestionPosition(parentQuestionId)
returns null (i.e. the parent is itself a spliced, non-core question)
-- that's the actual bug this fixes, not a missing data field.

Fix: spliceLabel() takes a third parameter, the session's existing
question_labels map, and looks up the parent's OWN already-resolved
label when the parent isn't core, instead of falling back to its raw
ID. Format kept consistent with the existing house style ("6A", "11A",
"23A") rather than Gemini's "Question X - Follow-up N" format, which
doesn't match anything currently live -- a depth-2 follow-up off core
position 34's first child ("34A") becomes "34AA", not a new verbose
string shape.

Usage:
  python tools/patch_ancestry_label_fix.py --dry-run
  python tools/patch_ancestry_label_fix.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


S = "web/lib/session-store.ts"
R = "web/app/api/diagnostic/session/answer/route.ts"

# ---------------------------------------------------------------------
# 1. spliceLabel() -- new third parameter, ancestry-aware fallback.
# ---------------------------------------------------------------------

edit(
    S,
    "// letterIndex is 0-based (0 -> \"A\", 1 -> \"B\", ...) -- the firing order of\n"
    "// this question among any siblings spliced from the same parent in the\n"
    "// same call (checkpoints can splice up to 2 at once; severity follow-ons\n"
    "// and Q28 only ever splice one, so letterIndex is always 0 for those).\n"
    "export function spliceLabel(parentQuestionId: string, letterIndex: number): string {\n"
    "  const parentPosition = coreQuestionPosition(parentQuestionId);\n"
    "  const letter = String.fromCharCode(65 + letterIndex);\n"
    "  // parentPosition should never be null in practice -- every current splice\n"
    "  // mechanism fires from a real core question. Falls back to the raw\n"
    "  // parent ID rather than throwing, so a label always renders instead of\n"
    "  // crashing the session on an unexpected edge case.\n"
    "  return `${parentPosition ?? parentQuestionId}${letter}`;\n"
    "}",
    "// letterIndex is 0-based (0 -> \"A\", 1 -> \"B\", ...) -- the firing order of\n"
    "// this question among any siblings spliced from the same parent in the\n"
    "// same call (checkpoints can splice up to 2 at once; severity follow-ons\n"
    "// and Q28 only ever splice one, so letterIndex is always 0 for those).\n"
    "//\n"
    "// existingLabels: the session's current question_labels map. Needed for\n"
    "// ancestry-aware labeling -- when the parent is itself a spliced (non-\n"
    "// core) question, coreQuestionPosition(parentQuestionId) returns null,\n"
    "// and the correct label is the parent's OWN already-resolved label\n"
    "// (looked up here) with this splice's letter appended, not the parent's\n"
    "// raw ID string. E.g. a follow-up of \"34A\" becomes \"34AA\", not\n"
    "// \"SEVER-30A\". Falls back to the raw parent ID only if the parent's own\n"
    "// label genuinely isn't in existingLabels yet, which should not happen\n"
    "// in practice -- every splice call site sets question_labels for a\n"
    "// question before it can ever be answered (and thus become a parent).\n"
    "export function spliceLabel(\n"
    "  parentQuestionId: string,\n"
    "  letterIndex: number,\n"
    "  existingLabels: Record<string, string>,\n"
    "): string {\n"
    "  const parentPosition = coreQuestionPosition(parentQuestionId);\n"
    "  const letter = String.fromCharCode(65 + letterIndex);\n"
    "  const parentLabel =\n"
    "    parentPosition !== null\n"
    "      ? String(parentPosition)\n"
    "      : existingLabels[parentQuestionId] ?? parentQuestionId;\n"
    "  return `${parentLabel}${letter}`;\n"
    "}",
)

# ---------------------------------------------------------------------
# 2. Three call sites in answer/route.ts -- pass session.question_labels.
# ---------------------------------------------------------------------

edit(
    R,
    'session.question_labels[severityFollowOnId] = spliceLabel(question_id, 0);',
    'session.question_labels[severityFollowOnId] = spliceLabel(question_id, 0, session.question_labels);',
)

edit(
    R,
    'session.question_labels["Q28"] = spliceLabel("Q06", 0);',
    'session.question_labels["Q28"] = spliceLabel("Q06", 0, session.question_labels);',
)

edit(
    R,
    "session.question_labels[distinguisherId] = spliceLabel(question_id, letterIndex);",
    "session.question_labels[distinguisherId] = spliceLabel(question_id, letterIndex, session.question_labels);",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
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
