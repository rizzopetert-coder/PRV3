"""
TC-* questions display "FOLLOW-UP TC-HRPOL-01" (Pete, 2026-09-27 bug report 2).

Root cause (web only): resolveQuestionLabel() knows two kinds -- core
(a PHASE_1_QUESTION_SEQUENCE member) or spliced (checkpoint distinguishers,
SEVER-* follow-ons, Q28/Q45). TC-* questions are appended to hr_diagnostic
sessions in createSession() but are neither, and have no stored splice
label, so they fell through to the spliced branch's raw-ID fallback, which
QuestionView renders as "Follow-up <label>". The engine side is correct:
TC-* questions carry checkpoint_segment "tactical" and sequence_position
None, but no web code reads checkpoint_segment for labeling.

Fix:
  - QuestionLabel gains a third kind, { kind: "tactical", position, total },
    resolved from TACTICAL_QUESTION_META's own order (40 questions).
  - QuestionView renders it as "Tactical & compliance review · Question N of
    40", reusing the results page's existing section heading rather than
    inventing per-section names (those would be new copy, Pete's call).
  - The spliced fallback no longer returns the raw question_id: an unlabeled
    spliced question now shows plain "Follow-up". The existing test pinning
    the raw-ID fallback is updated to the new contract (raw IDs are never
    user-facing, per Pete).

Usage:
    python tools/patch_tactical_question_label.py --dry-run
    python tools/patch_tactical_question_label.py --write
"""
import argparse
import pathlib
import sys

EDITS = [
    ('web/lib/session-store.ts',
     'export type QuestionLabel =\n'
     '  | { kind: "core"; position: number; total: number }\n'
     '  | { kind: "spliced"; label: string };\n',
     'export type QuestionLabel =\n'
     '  | { kind: "core"; position: number; total: number }\n'
     '  | { kind: "spliced"; label: string }\n'
     '  // hr_diagnostic TC-* module (appended in createSession()). Its own\n'
     '  // kind so it is never mislabeled as a follow-up, positioned within the\n'
     '  // 40-question module in TACTICAL_QUESTION_META\'s order.\n'
     '  | { kind: "tactical"; position: number; total: number };\n'
     '\n'
     'const TACTICAL_QUESTION_IDS: readonly string[] = Object.keys(TACTICAL_QUESTION_META);\n',
     'QuestionLabel type'),
    ('web/lib/session-store.ts',
     '    return { kind: "core", position: corePosition, total: TOTAL_CORE_QUESTIONS };\n'
     '  }\n'
     '  return { kind: "spliced", label: spliceLabels[questionId] ?? questionId };\n',
     '    return { kind: "core", position: corePosition, total: TOTAL_CORE_QUESTIONS };\n'
     '  }\n'
     '  const tacticalIndex = TACTICAL_QUESTION_IDS.indexOf(questionId);\n'
     '  if (tacticalIndex !== -1) {\n'
     '    return { kind: "tactical", position: tacticalIndex + 1, total: TACTICAL_QUESTION_IDS.length };\n'
     '  }\n'
     '  // Never fall back to the raw question_id -- internal IDs are not\n'
     '  // user-facing. An unlabeled splice renders as plain "Follow-up".\n'
     '  return { kind: "spliced", label: spliceLabels[questionId] ?? "" };\n',
     'resolveQuestionLabel'),
    ('web/components/DiagnosticFlow.tsx',
     'type QuestionLabel =\n'
     '  | { kind: "core"; position: number; total: number }\n'
     '  | { kind: "spliced"; label: string };\n',
     'type QuestionLabel =\n'
     '  | { kind: "core"; position: number; total: number }\n'
     '  | { kind: "spliced"; label: string }\n'
     '  | { kind: "tactical"; position: number; total: number };\n',
     'client QuestionLabel type'),
    ('web/components/DiagnosticFlow.tsx',
     '        {label.kind === "core"\n'
     '          ? `Question ${label.position} of ${label.total}`\n'
     '          : `Follow-up ${label.label}`}\n',
     '        {label.kind === "core"\n'
     '          ? `Question ${label.position} of ${label.total}`\n'
     '          : label.kind === "tactical"\n'
     '            ? `Tactical & compliance review · Question ${label.position} of ${label.total}`\n'
     '            : label.label\n'
     '              ? `Follow-up ${label.label}`\n'
     '              : "Follow-up"}\n',
     'header render'),
    ('web/lib/session-store.test.ts',
     '  it("falls back to the raw question_id if a spliced question has no stored label", () => {\n'
     '    const label = resolveQuestionLabel("SEVER-99", {});\n'
     '    expect(label).toEqual({ kind: "spliced", label: "SEVER-99" });\n'
     '  });\n',
     '  it("never falls back to the raw question_id when a spliced question has no stored label", () => {\n'
     '    const label = resolveQuestionLabel("SEVER-99", {});\n'
     '    expect(label).toEqual({ kind: "spliced", label: "" });\n'
     '  });\n'
     '\n'
     '  it("resolves TC-* questions to the tactical kind, not a follow-up", () => {\n'
     '    expect(resolveQuestionLabel("TC-HRPOL-01", {})).toEqual({ kind: "tactical", position: 1, total: 40 });\n'
     '    expect(resolveQuestionLabel("TC-HRPOL-03", {})).toEqual({ kind: "tactical", position: 3, total: 40 });\n'
     '    expect(resolveQuestionLabel("TC-PERF-04", {})).toEqual({ kind: "tactical", position: 40, total: 40 });\n'
     '  });\n',
     'tests'),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    edited = {}
    for rel, old, new, label in EDITS:
        p = pathlib.Path(rel)
        t = edited.get(p, p.read_text(encoding='utf-8'))
        if t.count(old) != 1:
            print(f'ERROR: {p} :: {label} anchor found {t.count(old)} times.', file=sys.stderr)
            sys.exit(1)
        edited[p] = t.replace(old, new, 1)
        print(f'[{p} :: {label}] OK')
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    for p, t in edited.items():
        p.write_text(t, encoding='utf-8')
        print(f'WROTE: {p}')


if __name__ == '__main__':
    main()
