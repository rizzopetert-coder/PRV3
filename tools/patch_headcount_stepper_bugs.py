"""
PRV3 -- Tier 1 bug fix, web/components/DiagnosticFlow.tsx's employee-count
stepper (Path 1 intake form, first field). Two live production bugs found
via direct browser walkthrough of prv-3.vercel.app/diagnostic this session
(screenshots, not inferred from code review).

Root-caused directly against the live repo, not assumed:

BUG 1 -- decrement button renders the literal text "\\u2212" instead of a
minus-sign glyph. Confirmed at line 171: the escape sequence is written as
bare JSX child text (`\\u2212` sitting directly between <button> tags), not
inside a JS string/template literal. JSX text content is never escape-
interpreted -- \\uXXXX sequences only resolve inside an actual string, which
this wasn't. Fix: wrap in a JS string expression container, `{"\\u2212"}`,
matching what the original author clearly intended.

BUG 2 -- flaky, timing-dependent number input on the same field (three
different inconsistent outcomes from similar keystroke sequences).
Root-caused via component-identity tracing, not guessed: HeadcountStepper
is declared as a nested function INSIDE IntakeForm's render body (lines
138-193, original file). IntakeForm re-executes on every keystroke (typing
-> handleTextChange -> onChange -> setIntake in the parent -> new `intake`
prop -> IntakeForm's function body runs again) -- which redeclares
HeadcountStepper as a brand-new function object every single render. React
compares JSX element types by reference; a changed function reference at
<HeadcountStepper .../> means React treats it as an entirely different
component and unmounts + remounts it, destroying and recreating the real
<input> DOM node on every keystroke. That remount races against the
browser's native keystroke handling, which explains all three observed
symptoms (fast "60" -> "6"; "6" then "0" after a pause -> "0" dropped;
"6" then "5" fast -> empty).

NOT the same root cause as Bug 1 -- confirmed by inspecting HeadcountStepper's
own body: it closes over nothing from IntakeForm's scope (HEADCOUNT_MAX and
stepHeadcount() are already module-level; value/onChange are its own
function parameters), so it is trivially hoistable with zero logic change.
Fix: move the function declaration out of IntakeForm to module scope (same
file, placed after stepHeadcount()) so it has a stable identity across
re-renders. Both fixes land in the same relocated block, which is why one
patch covers both -- not because they share a cause.

Scope confirmed via repo-wide grep: HeadcountStepper is not exported, not
imported anywhere else -- both bugs are scoped to this one file/field, not
shared elsewhere.

Related, NOT fixed here (out of scope -- no other bug report for these):
IntakeForm's other two nested helpers, field() and SignificantEventsField(),
carry the identical anti-pattern (declared inside IntakeForm's body,
recreated every render) but haven't manifested a visible bug -- select
dropdowns and checkboxes aren't sensitive to remounting mid-keystroke the
way a free-text input is. Flagged for awareness, not touched, per Tier 1
scope discipline (fix what was reported).

No test coverage exists for this component (web/ has zero .test.tsx files
anywhere, a pre-existing, already-logged gap) -- verification here relies
on tsc --noEmit plus Pete's live re-test on Preview, not an automated suite.

Usage:
  python tools/patch_headcount_stepper_bugs.py --dry-run
  python tools/patch_headcount_stepper_bugs.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DF = "web/components/DiagnosticFlow.tsx"

# ---------------------------------------------------------------------
# 1. Remove HeadcountStepper from inside IntakeForm's body.
# ---------------------------------------------------------------------

edit(
    DF,
    "  function HeadcountStepper({\n"
    "    value,\n"
    "    onChange,\n"
    "  }: {\n"
    "    value: number | \"\";\n"
    "    onChange: (next: number | \"\") => void;\n"
    "  }) {\n"
    "    const display = value === \"\" ? \"\" : value >= HEADCOUNT_MAX ? \"1000+\" : String(value);\n"
    "\n"
    "    function handleTextChange(raw: string) {\n"
    "      if (raw.trim() === \"\") {\n"
    "        onChange(\"\");\n"
    "        return;\n"
    "      }\n"
    "      const digitsOnly = raw.replace(/[^\\d]/g, \"\");\n"
    "      if (digitsOnly === \"\") return;\n"
    "      const parsed = parseInt(digitsOnly, 10);\n"
    "      onChange(Math.max(1, Math.min(HEADCOUNT_MAX, parsed)));\n"
    "    }\n"
    "\n"
    "    return (\n"
    "      <div className=\"mb-5\">\n"
    "        <label className=\"block font-ui text-sm font-medium text-charcoal mb-1.5\">\n"
    "          About how many employees?\n"
    "        </label>\n"
    "        <div className=\"flex items-center gap-2\">\n"
    "          <button\n"
    "            type=\"button\"\n"
    "            onClick={() => onChange(value === \"\" ? 1 : stepHeadcount(value, -1))}\n"
    "            disabled={value !== \"\" && value <= 1}\n"
    "            className=\"w-9 h-9 shrink-0 rounded-lg border border-gray-200 text-charcoal font-ui text-lg disabled:opacity-30\"\n"
    "            aria-label=\"Decrease\"\n"
    "          >\n"
    "            \\u2212\n"
    "          </button>\n"
    "          <input\n"
    "            type=\"text\"\n"
    "            inputMode=\"numeric\"\n"
    "            value={display}\n"
    "            onChange={(e) => handleTextChange(e.target.value)}\n"
    "            placeholder=\"e.g. 60\"\n"
    "            className=\"w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal text-center focus:outline-none focus:border-charcoal\"\n"
    "          />\n"
    "          <button\n"
    "            type=\"button\"\n"
    "            onClick={() => onChange(value === \"\" ? 1 : stepHeadcount(value, 1))}\n"
    "            disabled={value === HEADCOUNT_MAX}\n"
    "            className=\"w-9 h-9 shrink-0 rounded-lg border border-gray-200 text-charcoal font-ui text-lg disabled:opacity-30\"\n"
    "            aria-label=\"Increase\"\n"
    "          >\n"
    "            +\n"
    "          </button>\n"
    "        </div>\n"
    "      </div>\n"
    "    );\n"
    "  }\n"
    "\n"
    "  function field(\n",
    "  function field(\n",
)

# ---------------------------------------------------------------------
# 2. Re-add HeadcountStepper at module scope, right after stepHeadcount(),
#    with Bug 1's fix applied (\u2212 now inside a real string expression).
# ---------------------------------------------------------------------

edit(
    DF,
    "function stepHeadcount(value: number, direction: 1 | -1): number {\n"
    "  const next = value + direction * headcountStepSize(value);\n"
    "  return Math.max(1, Math.min(HEADCOUNT_MAX, next));\n"
    "}\n",
    "function stepHeadcount(value: number, direction: 1 | -1): number {\n"
    "  const next = value + direction * headcountStepSize(value);\n"
    "  return Math.max(1, Math.min(HEADCOUNT_MAX, next));\n"
    "}\n"
    "\n"
    "// Hoisted to module scope (was nested inside IntakeForm) -- a nested\n"
    "// function component is redeclared on every parent render, which made\n"
    "// React remount this <input> (destroying and recreating the DOM node)\n"
    "// on every keystroke, racing against the browser's native input\n"
    "// handling. Closes over nothing from IntakeForm's scope (HEADCOUNT_MAX\n"
    "// and stepHeadcount are already module-level), so hoisting is a pure\n"
    "// move, zero logic change.\n"
    "function HeadcountStepper({\n"
    "  value,\n"
    "  onChange,\n"
    "}: {\n"
    "  value: number | \"\";\n"
    "  onChange: (next: number | \"\") => void;\n"
    "}) {\n"
    "  const display = value === \"\" ? \"\" : value >= HEADCOUNT_MAX ? \"1000+\" : String(value);\n"
    "\n"
    "  function handleTextChange(raw: string) {\n"
    "    if (raw.trim() === \"\") {\n"
    "      onChange(\"\");\n"
    "      return;\n"
    "    }\n"
    "    const digitsOnly = raw.replace(/[^\\d]/g, \"\");\n"
    "    if (digitsOnly === \"\") return;\n"
    "    const parsed = parseInt(digitsOnly, 10);\n"
    "    onChange(Math.max(1, Math.min(HEADCOUNT_MAX, parsed)));\n"
    "  }\n"
    "\n"
    "  return (\n"
    "    <div className=\"mb-5\">\n"
    "      <label className=\"block font-ui text-sm font-medium text-charcoal mb-1.5\">\n"
    "        About how many employees?\n"
    "      </label>\n"
    "      <div className=\"flex items-center gap-2\">\n"
    "        <button\n"
    "          type=\"button\"\n"
    "          onClick={() => onChange(value === \"\" ? 1 : stepHeadcount(value, -1))}\n"
    "          disabled={value !== \"\" && value <= 1}\n"
    "          className=\"w-9 h-9 shrink-0 rounded-lg border border-gray-200 text-charcoal font-ui text-lg disabled:opacity-30\"\n"
    "          aria-label=\"Decrease\"\n"
    "        >\n"
    "          {\"\\u2212\"}\n"
    "        </button>\n"
    "        <input\n"
    "          type=\"text\"\n"
    "          inputMode=\"numeric\"\n"
    "          value={display}\n"
    "          onChange={(e) => handleTextChange(e.target.value)}\n"
    "          placeholder=\"e.g. 60\"\n"
    "          className=\"w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal text-center focus:outline-none focus:border-charcoal\"\n"
    "        />\n"
    "        <button\n"
    "          type=\"button\"\n"
    "          onClick={() => onChange(value === \"\" ? 1 : stepHeadcount(value, 1))}\n"
    "          disabled={value === HEADCOUNT_MAX}\n"
    "          className=\"w-9 h-9 shrink-0 rounded-lg border border-gray-200 text-charcoal font-ui text-lg disabled:opacity-30\"\n"
    "          aria-label=\"Increase\"\n"
    "        >\n"
    "          +\n"
    "        </button>\n"
    "      </div>\n"
    "    </div>\n"
    "  );\n"
    "}\n",
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
