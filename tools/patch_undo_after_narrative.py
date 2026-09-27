"""
Back inside the hr-dx TC-* section errors and forces a restart (Pete,
2026-09-27 bug report 3). Reproduced on Preview: a session whose narrative
fired at the Q27B checkpoint, two TC answers later, undo returned
HTTP 400 {"error":"Cannot undo past a narrative transition"}, which the
client renders as "Something went wrong" (error phase, restart only).

Root cause: the undo guard rejects whenever session.narrative_fired is true,
not only when the undo would cross the narrative. Its own comment assumed
Back is never visible once narrative has fired, which holds for the
end-of-sequence trigger but not the early Q27 trigger: after it, the client
is back in the question phase with a non-empty history, so every later
Back click (Q28 onward, and the whole TC-* module on hr-dx) hit the 400.
Not TC-specific, and not a static-sequence assumption: undo already works
from answers_log and question_sequence. The only other static-sequence
reader is the label code (fixed separately).

Fix:
  - session.narrative_answer_count (optional): answers_log.length when the
    narrative response is recorded (session/narrative).
  - undo: pending narrative/completion still rejects. After the narrative,
    only an undo reaching back to or past that boundary rejects. Sessions
    created before this field exist keep today's reject-everything
    behavior, since their boundary is unknown.
  - Safe by construction: pre_narrative_vector is a frozen snapshot that
    later answers never update, and undo subtracts only the undone answer's
    own additive delta from the (modulated) accumulated_vector.
  - client: an undo floor at the narrative boundary hides Back there, and a
    refused undo restores the current question instead of the error phase,
    so a Back press can never cost the session.

Usage:
    python tools/patch_undo_after_narrative.py --dry-run
    python tools/patch_undo_after_narrative.py --write
"""
import argparse
import pathlib
import sys

EDITS = [
    ('web/lib/session-store.ts',
     '  narrative_fired: boolean;\n',
     '  narrative_fired: boolean;\n'
     '  // answers_log.length at the moment the narrative response was recorded\n'
     '  // -- the undo boundary. Answers after it can be undone, the narrative\n'
     '  // and anything before it cannot. Optional: sessions created before\n'
     '  // this field existed have no known boundary and keep the old\n'
     '  // reject-all-undo-after-narrative behavior.\n'
     '  narrative_answer_count?: number;\n',
     'session field'),
    ('web/app/api/diagnostic/session/narrative/route.ts',
     '  session.narrative_fired = true;\n',
     '  session.narrative_fired = true;\n'
     '  session.narrative_answer_count = session.answers_log.length;\n',
     'record boundary'),
    ('web/app/api/diagnostic/session/undo/route.ts',
     '  // Narrative modulation has already begun -- undoing across that boundary\n'
     '  // is deliberately out of scope for this pass (see tools/_mob.txt). Not a\n'
     '  // live path today: narrative is a distinct FlowState phase on the client\n'
     '  // ("narrative", not "question"), so the back button is never visible when\n'
     '  // this would fire. Kept as an explicit reject rather than an assumption,\n'
     '  // same philosophy as session/answer\'s own index invariant check.\n'
     '  if (\n'
     '    session.narrative_fired ||\n'
     '    session.pending_narrative_prompt !== null ||\n'
     '    session.pending_completion\n'
     '  ) {\n',
     '  // Undoing ACROSS the narrative is out of scope: rejected while a\n'
     '  // narrative prompt or completion is pending, and after the narrative\n'
     '  // for any answer at or before its boundary (narrative_answer_count).\n'
     '  // Answers given after the narrative undo normally -- the early Q27\n'
     '  // trigger returns the client to the question phase, so Back stays\n'
     '  // visible for Q28 onward and the hr-dx TC-* module. A session with\n'
     '  // narrative_fired but no recorded boundary predates the field and\n'
     '  // keeps the old reject.\n'
     '  const undoWouldCrossNarrative =\n'
     '    session.narrative_fired &&\n'
     '    (session.narrative_answer_count === undefined ||\n'
     '      session.answers_log.length <= session.narrative_answer_count);\n'
     '  if (\n'
     '    undoWouldCrossNarrative ||\n'
     '    session.pending_narrative_prompt !== null ||\n'
     '    session.pending_completion\n'
     '  ) {\n',
     'undo guard'),
    ('web/app/api/diagnostic/session/undo/route.test.ts',
     '  it("rejects with 400 once narrative modulation has begun -- explicitly out of scope for this build", async () => {\n',
     '  it("undoes an answer given after the narrative (early Q27 trigger, then TC-* answers)", async () => {\n'
     '    const session = await createSession(FAKE_INTAKE, "hr_diagnostic");\n'
     '    session.narrative_fired = true;\n'
     '    session.narrative_answer_count = 2;\n'
     '    session.answers_log = [\n'
     '      { question_id: "Q27A", option_ids: ["A"] },\n'
     '      { question_id: "Q27B", option_ids: ["A"] },\n'
     '      { question_id: "TC-HRPOL-01", option_ids: ["A"] },\n'
     '      { question_id: "TC-HRPOL-02", option_ids: ["B"] },\n'
     '    ];\n'
     '    session.next_question_id = "TC-HRPOL-03";\n'
     '    const { saveSession } = await import("@/lib/session-store");\n'
     '    await saveSession(session);\n'
     '    mockInvokeAccumulate.mockResolvedValue({\n'
     '      accumulated_vector: { ...ZERO },\n'
     '      severity_inputs: [], severity_follow_on_ids: [], severity_follow_on_origins: {},\n'
     '    });\n'
     '\n'
     '    const res1 = await POST(fakeRequest({ session_id: session.session_id }));\n'
     '    expect(res1.status).toBe(200);\n'
     '    const data1 = await res1.json();\n'
     '    expect(data1.question.question_id).toBe("TC-HRPOL-02");\n'
     '    expect(data1.label).toEqual({ kind: "tactical", position: 2, total: 40 });\n'
     '    const res2 = await POST(fakeRequest({ session_id: session.session_id }));\n'
     '    expect(res2.status).toBe(200);\n'
     '    expect((await res2.json()).question.question_id).toBe("TC-HRPOL-01");\n'
     '\n'
     '    // The next undo would reach the narrative-triggering answer: rejected,\n'
     '    // and nothing about the session changes.\n'
     '    const res3 = await POST(fakeRequest({ session_id: session.session_id }));\n'
     '    expect(res3.status).toBe(400);\n'
     '    const after = await getSession(session.session_id);\n'
     '    expect(after!.answers_log.map((e) => e.question_id)).toEqual(["Q27A", "Q27B"]);\n'
     '    expect(after!.next_question_id).toBe("TC-HRPOL-01");\n'
     '  });\n'
     '\n'
     '  it("keeps rejecting after the narrative for sessions with no recorded boundary (pre-fix sessions)", async () => {\n'
     '    const session = await createSession(FAKE_INTAKE);\n'
     '    session.narrative_fired = true;\n'
     '    session.answers_log = [\n'
     '      { question_id: "Q27B", option_ids: ["A"] },\n'
     '      { question_id: "Q28", option_ids: ["A"] },\n'
     '    ];\n'
     '    const { saveSession } = await import("@/lib/session-store");\n'
     '    await saveSession(session);\n'
     '\n'
     '    const res = await POST(fakeRequest({ session_id: session.session_id }));\n'
     '    expect(res.status).toBe(400);\n'
     '    expect(mockInvokeAccumulate).not.toHaveBeenCalled();\n'
     '  });\n'
     '\n'
     '  it("rejects with 400 once narrative modulation has begun -- explicitly out of scope for this build", async () => {\n',
     'tests'),
    ('web/components/DiagnosticFlow.tsx',
     '  const [history, setHistory] = useState<AnsweredEntry[]>([]);\n',
     '  const [history, setHistory] = useState<AnsweredEntry[]>([]);\n'
     '  // Undo boundary: history.length when the narrative response was\n'
     '  // accepted. Answers at or before it cannot be undone (the server\n'
     '  // rejects that too), so Back is hidden there rather than erroring.\n'
     '  const [undoFloor, setUndoFloor] = useState(0);\n',
     'undo floor state'),
    ('web/components/DiagnosticFlow.tsx',
     '    setHistory([]);\n    setShowHistory(false);\n',
     '    setHistory([]);\n    setUndoFloor(0);\n    setShowHistory(false);\n',
     'reset clears floor'),
    ('web/components/DiagnosticFlow.tsx',
     '    if (state.phase !== "question") return;\n'
     '    if (history.length === 0) return;\n'
     '    const { sessionId } = state;\n'
     '\n'
     '    setState({ phase: "loading" });\n'
     '    try {\n'
     '      const res = await fetch("/api/diagnostic/session/undo", {\n'
     '        method: "POST",\n'
     '        headers: { "Content-Type": "application/json" },\n'
     '        body: JSON.stringify({ session_id: sessionId }),\n'
     '      });\n'
     '      if (!res.ok) {\n'
     '        setState({ phase: "error", message: ERROR_COPY });\n'
     '        return;\n'
     '      }\n',
     '    if (state.phase !== "question") return;\n'
     '    if (history.length <= undoFloor) return;\n'
     '    const { sessionId } = state;\n'
     '    // A refused or failed undo restores the question the respondent was\n'
     '    // on -- never the error phase, which only offers a restart and would\n'
     '    // throw away every answer so far.\n'
     '    const current = state;\n'
     '\n'
     '    setState({ phase: "loading" });\n'
     '    try {\n'
     '      const res = await fetch("/api/diagnostic/session/undo", {\n'
     '        method: "POST",\n'
     '        headers: { "Content-Type": "application/json" },\n'
     '        body: JSON.stringify({ session_id: sessionId }),\n'
     '      });\n'
     '      if (!res.ok) {\n'
     '        setState(current);\n'
     '        return;\n'
     '      }\n',
     'handleUndo guard + restore'),
    ('web/components/DiagnosticFlow.tsx',
     '        prefillOptionIds: data.option_ids ?? null,\n'
     '      });\n'
     '    } catch {\n'
     '      setState({ phase: "error", message: ERROR_COPY });\n'
     '    }\n',
     '        prefillOptionIds: data.option_ids ?? null,\n'
     '      });\n'
     '    } catch {\n'
     '      setState(current);\n'
     '    }\n',
     'handleUndo catch restore'),
    ('web/components/DiagnosticFlow.tsx',
     '            {history.length > 0 && (\n'
     '              <button\n'
     '                onClick={handleUndo}\n',
     '            {history.length > undoFloor && (\n'
     '              <button\n'
     '                onClick={handleUndo}\n',
     'Back button visibility'),
]

# handleNarrativeSubmit's in_progress branch: set the floor. Anchored inside
# that function only, since the same setState shape also appears in
# handleAnswer.
NARR_FN = '  async function handleNarrativeSubmit(text: string) {\n'
NARR_OLD = ('      } else {\n'
            '        setState({\n'
            '          phase: "question",\n'
            '          sessionId,\n'
            '          question: data.question,\n'
            '          label: data.label,\n'
            '          prefillOptionIds: null,\n'
            '        });\n'
            '      }\n')
NARR_NEW = ('      } else {\n'
            '        setUndoFloor(history.length);\n'
            '        setState({\n'
            '          phase: "question",\n'
            '          sessionId,\n'
            '          question: data.question,\n'
            '          label: data.label,\n'
            '          prefillOptionIds: null,\n'
            '        });\n'
            '      }\n')


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
    p = pathlib.Path('web/components/DiagnosticFlow.tsx')
    t = edited[p]
    if t.count(NARR_FN) != 1:
        print('ERROR: handleNarrativeSubmit not found once.', file=sys.stderr)
        sys.exit(1)
    fn_start = t.index(NARR_FN)
    fn_end = t.index('\n  }\n', fn_start)
    region = t[fn_start:fn_end]
    if region.count(NARR_OLD) != 1:
        print(f'ERROR: in_progress branch found {region.count(NARR_OLD)} times in handleNarrativeSubmit.', file=sys.stderr)
        sys.exit(1)
    edited[p] = t[:fn_start] + region.replace(NARR_OLD, NARR_NEW, 1) + t[fn_end:]
    print(f'[{p} :: narrative submit sets floor] OK')
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    for p, t in edited.items():
        p.write_text(t, encoding='utf-8')
        print(f'WROTE: {p}')


if __name__ == '__main__':
    main()
