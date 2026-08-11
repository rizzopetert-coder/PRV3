"""
PRV3 -- A.3 (back/forward/reset), reset + look-back only this batch, per
Pete's explicit descope. Confirmed via direct source read before this
build: zero navigation controls existed anywhere in DiagnosticFlow.tsx
(the only prior "Start over" button lived on the error phase only, never
shown during a normal in-progress session) -- the original 2026-08-09
report was still fully accurate, nothing had changed since.

Edit-and-replay (going back and changing a previous answer, given the
splice/checkpoint re-evaluation question already scoped in the prior
report) is deliberately NOT built here -- parked as its own item, logged
in the Decision Register on close.

Both additions are genuinely read-only / non-mutating with respect to
session/engine state:
  - Reset: identical in kind to the pre-existing error-phase "Start over"
    button (already just discards client state, no backend delete/expire
    call -- an abandoned session already ages out via its existing 6-hour
    sliding TTL regardless of how it was abandoned, same as a closed
    browser tab today). Now also reachable during a normal in-progress
    session, not just after an error, and now clears intake + history too
    (the pre-existing button only reset `state`).
  - Look-back: a client-side mirror of what was already rendered and
    submitted in this browser tab as the respondent progressed --
    accumulated_vector, question_sequence, checkpoints, and severity_inputs
    are never read or touched. Built as local React state (not a new
    backend endpoint) since Phase 1 is single-tab/single-sitting by
    design -- the dev-only ?session= resume param is a different,
    narrower mechanism (jumps to current position, doesn't carry history)
    and is untouched by this change.

Usage:
  python tools/patch_a3_reset_lookback.py --dry-run
  python tools/patch_a3_reset_lookback.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


FLOW = "web/components/DiagnosticFlow.tsx"

# ═══════════════════════════════════════════════════════════════════════
# State + a small read-only HistoryPanel component, plus handleReset().
# ═══════════════════════════════════════════════════════════════════════

edit(
    FLOW,
    'export default function DiagnosticFlow() {\n'
    '  const [state, setState] = useState<FlowState>({ phase: "intake" });\n'
    '  const [intake, setIntake] = useState<IntakeFormState>(EMPTY_INTAKE);\n',
    '// A.3 (reset + look-back), this session -- a purely client-side mirror\n'
    '// of what this browser tab has already rendered and submitted. Never\n'
    '// reads or touches accumulated_vector/question_sequence/checkpoints/\n'
    '// severity_inputs; read-only by construction.\n'
    'interface AnsweredEntry {\n'
    '  questionText: string;\n'
    '  selectedOptionTexts: string[];\n'
    '}\n'
    '\n'
    'function HistoryPanel({ history }: { history: AnsweredEntry[] }) {\n'
    '  if (history.length === 0) {\n'
    '    return (\n'
    '      <div className="max-w-xl mx-auto px-6 pb-4">\n'
    '        <p className="font-ui text-xs text-gray-400">No answers yet.</p>\n'
    '      </div>\n'
    '    );\n'
    '  }\n'
    '  return (\n'
    '    <div className="max-w-xl mx-auto px-6 pb-6 space-y-3 border-b border-gray-200 mb-2">\n'
    '      {history.map((entry, i) => (\n'
    '        <div key={i}>\n'
    '          <p className="font-ui text-xs text-gray-400">{entry.questionText}</p>\n'
    '          <p className="font-ui text-sm text-charcoal">{entry.selectedOptionTexts.join(", ")}</p>\n'
    '        </div>\n'
    '      ))}\n'
    '    </div>\n'
    '  );\n'
    '}\n'
    '\n'
    'export default function DiagnosticFlow() {\n'
    '  const [state, setState] = useState<FlowState>({ phase: "intake" });\n'
    '  const [intake, setIntake] = useState<IntakeFormState>(EMPTY_INTAKE);\n'
    '  const [history, setHistory] = useState<AnsweredEntry[]>([]);\n'
    '  const [showHistory, setShowHistory] = useState(false);\n'
    '\n'
    '  // Reset -- same kind of action as the pre-existing error-phase "Start\n'
    '  // over" button (client-state discard only, no backend delete/expire\n'
    '  // call; an abandoned session already ages out via its existing 6-hour\n'
    '  // sliding TTL, same as a closed browser tab today), now also clearing\n'
    '  // intake + history and reachable during a normal in-progress session,\n'
    '  // not just after an error.\n'
    '  function handleReset() {\n'
    '    setState({ phase: "intake" });\n'
    '    setIntake(EMPTY_INTAKE);\n'
    '    setHistory([]);\n'
    '    setShowHistory(false);\n'
    '  }\n',
)

# ═══════════════════════════════════════════════════════════════════════
# handleAnswer -- append to history on confirmed submission, before
# advancing state. Uses the closure's own `question` (the one just
# answered), not the response's next question.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FLOW,
    '      if (!res.ok) {\n'
    '        setState({ phase: "error", message: ERROR_COPY });\n'
    '        return;\n'
    '      }\n'
    '      const data = await res.json();\n'
    '      if (data.status === "complete") {',
    '      if (!res.ok) {\n'
    '        setState({ phase: "error", message: ERROR_COPY });\n'
    '        return;\n'
    '      }\n'
    '      const selectedTexts = optionIds.map(\n'
    '        (id) => question.options.find((o) => o.option_id === id)?.option_text ?? id,\n'
    '      );\n'
    '      setHistory((prev) => [\n'
    '        ...prev,\n'
    '        { questionText: question.question_text, selectedOptionTexts: selectedTexts },\n'
    '      ]);\n'
    '      const data = await res.json();\n'
    '      if (data.status === "complete") {',
)

# ═══════════════════════════════════════════════════════════════════════
# Error-phase reset button -- reuse handleReset() instead of an inline
# partial reset.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FLOW,
    '        <button\n'
    '          onClick={() => setState({ phase: "intake" })}\n'
    '          className="bg-charcoal text-white font-ui text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"\n'
    '        >\n'
    '          Start over\n'
    '        </button>',
    '        <button\n'
    '          onClick={handleReset}\n'
    '          className="bg-charcoal text-white font-ui text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"\n'
    '        >\n'
    '          Start over\n'
    '        </button>',
)

# ═══════════════════════════════════════════════════════════════════════
# Question-phase render -- add the review-answers toggle + reset control
# above QuestionView, and the read-only panel when toggled on.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FLOW,
    '  if (state.phase === "question") {\n'
    '    return (\n'
    '      <QuestionView\n'
    '        question={state.question}\n'
    '        label={state.label}\n'
    '        onAnswer={handleAnswer}\n'
    '      />',
    '  if (state.phase === "question") {\n'
    '    return (\n'
    '      <>\n'
    '        <div className="max-w-xl mx-auto px-6 pt-6 flex items-center justify-between">\n'
    '          <button\n'
    '            onClick={() => setShowHistory((s) => !s)}\n'
    '            className="font-ui text-xs text-gray-400 hover:text-charcoal transition-colors"\n'
    '          >\n'
    '            {showHistory ? "Hide" : "Review"} your answers so far\n'
    '          </button>\n'
    '          <button\n'
    '            onClick={handleReset}\n'
    '            className="font-ui text-xs text-gray-400 hover:text-charcoal transition-colors"\n'
    '          >\n'
    '            Start over\n'
    '          </button>\n'
    '        </div>\n'
    '        {showHistory && <HistoryPanel history={history} />}\n'
    '        <QuestionView\n'
    '          question={state.question}\n'
    '          label={state.label}\n'
    '          onAnswer={handleAnswer}\n'
    '        />\n'
    '      </>',
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
