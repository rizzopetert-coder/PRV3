"""
PRV3 -- A.2 (Q06 select-all-that-apply, real functional gap). Confirmed via
direct source read, not a live-browser walk: Q06 is genuinely authored as
format="weighted_multi_select" in the data model ("Select all that apply"),
but get_question_copy() strips `format` before it reaches the wire, and
every layer downstream (QuestionCopy, QuestionView, AnswerRequest,
AccumulatePayload, accumulate_one_answer) is single-option end to end. Not
stale, not a design misread -- never built.

Design, confirmed with Pete before this build:
- "None of the above" is mutually-exclusive-clearing, matching the intake
  form's SignificantEventsField pattern exactly (same interaction
  convention, detected by text match -- "none of the above" -- not a
  hardcoded option_id, so it generalizes to any future multi-select
  question without a code change).
- accumulate_one_answer() itself is UNCHANGED -- a new accumulate_answers()
  wrapper loops it once per selected option_id, threading
  accumulated_vector through sequentially. Confirmed necessary, not
  hypothetical: Q06's own A option (SEVER-27) and D option (SEVER-21) are
  BOTH severity_trigger=True, so a real multi-select answer (e.g. A+D
  together) can legitimately fire two severity follow-ons from one
  submission -- the route now splices all of them, not just one, reusing
  spliceDistinguishers()'s existing multi-ID capability (already proven by
  the checkpoint-distinguisher path, up to 2 at once).
- The wire contract widens to option_ids: string[] everywhere (not a dual
  option_id/option_ids branch) -- every existing single-select caller now
  sends a 1-element array, so there is exactly one code path, not two.

Touch list: engine/main.py (format on the wire; new accumulate_answers()
wrapper), api/engine.py (/api/accumulate reads option_ids, calls the new
wrapper), web/lib/engine-client.ts (QuestionCopy.format,
AccumulatePayload.option_ids, AccumulateResult severity_inputs/
severity_follow_on_ids pluralized), web/lib/session-store.ts
(AnswerLogEntry.option_ids), web/app/api/diagnostic/session/answer/
route.ts (AnswerRequest, splice-loop for multiple follow-ons, Q06->Q28 and
Q44->Q45 conditions rewritten as .includes() checks), web/components/
DiagnosticFlow.tsx (QuestionView gets a checkbox-plus-continue path gated
on format, single-select path unchanged in behavior),
web/lib/session-store.test.ts (3 literals updated to the new shape),
tools/diagnostic_fast_forward.py (same live wire contract, updated to
match or it would silently break next run).

Usage:
  python tools/patch_a2_q06_multiselect.py --dry-run
  python tools/patch_a2_q06_multiselect.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


MAIN = "engine/main.py"
API_ENGINE = "api/engine.py"
CLIENT = "web/lib/engine-client.ts"
STORE = "web/lib/session-store.ts"
ANSWER_ROUTE = "web/app/api/diagnostic/session/answer/route.ts"
FLOW = "web/components/DiagnosticFlow.tsx"
STORE_TEST = "web/lib/session-store.test.ts"
FAST_FORWARD = "tools/diagnostic_fast_forward.py"

# ═══════════════════════════════════════════════════════════════════════
# engine/main.py
# ═══════════════════════════════════════════════════════════════════════

edit(
    MAIN,
    '    return {\n'
    '        "question_id": question.question_id,\n'
    '        "question_text": question.question_text,\n'
    '        "options": [\n'
    '            {"option_id": opt.option_id, "option_text": opt.option_text}\n'
    '            for opt in question.answer_options\n'
    '        ],\n'
    '    }\n',
    '    return {\n'
    '        "question_id": question.question_id,\n'
    '        "question_text": question.question_text,\n'
    '        # format ("forced_choice" | "weighted_multi_select") -- A.2, this\n'
    '        # session. Not scoring-sensitive (a UI rendering hint, not\n'
    '        # dimensional_contributions/axis_targets/severity_trigger/\n'
    '        # severity_follow_on_id), safe to include -- P-03 boundary\n'
    '        # unaffected.\n'
    '        "format": question.format,\n'
    '        "options": [\n'
    '            {"option_id": opt.option_id, "option_text": opt.option_text}\n'
    '            for opt in question.answer_options\n'
    '        ],\n'
    '    }\n',
)

edit(
    MAIN,
    '    Raises KeyError on an unknown question_id or option_id -- the caller\n'
    '    (api/engine.py) maps this to a 400.\n'
    '    """\n'
    '    question = QUESTION_LIBRARY.get(question_id)\n'
    '    if question is None:\n'
    '        raise KeyError(f"Unknown question_id: {question_id!r}")\n'
    '\n'
    '    option = next(\n'
    '        (o for o in question.answer_options if o.option_id == option_id),\n'
    '        None,\n'
    '    )\n'
    '    if option is None:\n'
    '        raise KeyError(f"Unknown option_id {option_id!r} for question {question_id!r}")\n'
    '\n'
    '    intake_data = _locked_intake_to_engine_intake(intake)\n'
    '    session = AccumulationSession(accumulated_vector=dict(accumulated_vector))\n'
    '    accumulate_answer(session, option, intake_data, question_id)\n',
    '    Raises KeyError on an unknown question_id or option_id -- the caller\n'
    '    (api/engine.py) maps this to a 400.\n'
    '    """\n'
    '    question = QUESTION_LIBRARY.get(question_id)\n'
    '    if question is None:\n'
    '        raise KeyError(f"Unknown question_id: {question_id!r}")\n'
    '\n'
    '    option = next(\n'
    '        (o for o in question.answer_options if o.option_id == option_id),\n'
    '        None,\n'
    '    )\n'
    '    if option is None:\n'
    '        raise KeyError(f"Unknown option_id {option_id!r} for question {question_id!r}")\n'
    '\n'
    '    intake_data = _locked_intake_to_engine_intake(intake)\n'
    '    session = AccumulationSession(accumulated_vector=dict(accumulated_vector))\n'
    '    accumulate_answer(session, option, intake_data, question_id)\n',
)

# New accumulate_answers() wrapper -- inserted immediately after
# accumulate_one_answer()'s closing, before the next top-level def. Anchored
# on the VI.4/next-section marker via the return statement + blank lines
# pattern already used elsewhere in this file for insertion anchors.
edit(
    MAIN,
    'def run_checkpoint(',
    'def accumulate_answers(\n'
    '    accumulated_vector: dict,\n'
    '    question_id: str,\n'
    '    option_ids: list,\n'
    '    intake: dict,\n'
    '    trigger_question_id: str = "",\n'
    ') -> dict:\n'
    '    """\n'
    '    Multi-option wrapper around accumulate_one_answer() -- A.2 (Q06\n'
    '    multi-select), this session. Loops accumulate_one_answer() once per\n'
    '    selected option_id, threading accumulated_vector through\n'
    '    sequentially (each call\'s output feeds the next call\'s input) --\n'
    '    exactly the stateless-per-option contract accumulate_one_answer()\n'
    '    already guarantees. That function itself is UNCHANGED; this is a\n'
    '    second caller, not a modification, per its own docstring\'s "KNOWN\n'
    '    CALLER IMPACT" convention.\n'
    '\n'
    '    Every existing single-select caller now sends a 1-element list --\n'
    '    this function\'s behavior for len(option_ids) == 1 is byte-for-byte\n'
    '    identical to calling accumulate_one_answer() directly once, so it\n'
    '    fully replaces the old single-option call path everywhere (one code\n'
    '    path, not a dual branch).\n'
    '\n'
    '    Aggregates severity_input/severity_follow_on_id across every\n'
    '    selected option into lists (plural) rather than a single optional\n'
    '    value -- confirmed necessary, not hypothetical: Q06\'s own A option\n'
    '    (severity_trigger=True -> SEVER-27) and D option\n'
    '    (severity_trigger=True -> SEVER-21) mean a real multi-select answer\n'
    '    selecting both can legitimately fire two severity follow-ons from\n'
    '    one submission.\n'
    '\n'
    '    Raises KeyError (same as accumulate_one_answer(), same caller\n'
    '    handling in api/engine.py) if option_ids is empty or any entry is\n'
    '    invalid for question_id.\n'
    '    """\n'
    '    if not option_ids:\n'
    '        raise KeyError(f"option_ids must be non-empty for question {question_id!r}")\n'
    '\n'
    '    vector = dict(accumulated_vector)\n'
    '    severity_inputs = []\n'
    '    severity_follow_on_ids = []\n'
    '    for option_id in option_ids:\n'
    '        step = accumulate_one_answer(vector, question_id, option_id, intake, trigger_question_id)\n'
    '        vector = step["accumulated_vector"]\n'
    '        if step["severity_input"] is not None:\n'
    '            severity_inputs.append(step["severity_input"])\n'
    '        if step["severity_follow_on_id"] is not None:\n'
    '            severity_follow_on_ids.append(step["severity_follow_on_id"])\n'
    '\n'
    '    return {\n'
    '        "accumulated_vector": vector,\n'
    '        "severity_inputs": severity_inputs,\n'
    '        "severity_follow_on_ids": severity_follow_on_ids,\n'
    '    }\n'
    '\n'
    '\n'
    'def run_checkpoint(',
)

# ═══════════════════════════════════════════════════════════════════════
# api/engine.py
# ═══════════════════════════════════════════════════════════════════════

edit(
    API_ENGINE,
    'from engine.main import (\n'
    '    run_engine,\n'
    '    accumulate_one_answer,\n'
    '    run_checkpoint,\n'
    '    run_accumulated_engine,\n'
    '    get_question_copy,\n'
    ')',
    'from engine.main import (\n'
    '    run_engine,\n'
    '    accumulate_answers,\n'
    '    run_checkpoint,\n'
    '    run_accumulated_engine,\n'
    '    get_question_copy,\n'
    ')',
)

edit(
    API_ENGINE,
    '        accumulated_vector = payload.get("accumulated_vector", {}) if isinstance(payload, dict) else {}\n'
    '        question_id = payload.get("question_id", "") if isinstance(payload, dict) else ""\n'
    '        option_id = payload.get("option_id", "") if isinstance(payload, dict) else ""\n'
    '        intake = payload.get("intake", {}) if isinstance(payload, dict) else {}\n'
    '        # accumulate_one_answer() returns {"accumulated_vector", "severity_input",\n'
    '        # "severity_follow_on_id"} -- passed straight through as the response\n'
    '        # body. The Next.js caller unpacks accumulated_vector for the session\'s\n'
    '        # own vector, persists severity_input (when present) into\n'
    '        # session.severity_inputs, and splices severity_follow_on_id (when\n'
    '        # present) into question_sequence, mirroring checkpoint distinguishers.\n'
    '        result = accumulate_one_answer(accumulated_vector, question_id, option_id, intake)\n'
    '        return JSONResponse(content=result)',
    '        accumulated_vector = payload.get("accumulated_vector", {}) if isinstance(payload, dict) else {}\n'
    '        question_id = payload.get("question_id", "") if isinstance(payload, dict) else ""\n'
    '        option_ids = payload.get("option_ids", []) if isinstance(payload, dict) else []\n'
    '        intake = payload.get("intake", {}) if isinstance(payload, dict) else {}\n'
    '        # accumulate_answers() (A.2, this session -- wraps\n'
    '        # accumulate_one_answer() once per selected option) returns\n'
    '        # {"accumulated_vector", "severity_inputs", "severity_follow_on_ids"}\n'
    '        # -- passed straight through as the response body. The Next.js\n'
    '        # caller unpacks accumulated_vector for the session\'s own vector,\n'
    '        # persists every severity_input into session.severity_inputs, and\n'
    '        # splices every severity_follow_on_id into question_sequence,\n'
    '        # mirroring checkpoint distinguishers.\n'
    '        result = accumulate_answers(accumulated_vector, question_id, option_ids, intake)\n'
    '        return JSONResponse(content=result)',
)

# ═══════════════════════════════════════════════════════════════════════
# web/lib/engine-client.ts
# ═══════════════════════════════════════════════════════════════════════

edit(
    CLIENT,
    'export interface AccumulatePayload {\n'
    '  accumulated_vector: AccumulatedVector;\n'
    '  question_id: string;\n'
    '  option_id: string;\n'
    '  intake: PrivateIntakeEcho;\n'
    '}',
    'export interface AccumulatePayload {\n'
    '  accumulated_vector: AccumulatedVector;\n'
    '  question_id: string;\n'
    '  option_ids: string[];\n'
    '  intake: PrivateIntakeEcho;\n'
    '}',
)

edit(
    CLIENT,
    '// Mirrors accumulate_one_answer()\'s return shape exactly (engine/main.py).\n'
    'export interface AccumulateResult {\n'
    '  accumulated_vector: AccumulatedVector;\n'
    '  // Populated only when question_id itself is a SEVER-01..13 follow-on\n'
    '  // whose answer maps to a real SeverityInput field -- null for every\n'
    '  // other question, including the core question that triggered the\n'
    '  // follow-on.\n'
    '  severity_input: SeverityInputPayload | null;\n'
    '  // Populated only when the just-answered option carries\n'
    '  // severity_trigger=true (a core question option) -- the SEVER-##\n'
    '  // question_id to splice into the sequence next. Null otherwise,\n'
    '  // including on SEVER-01..13 answers themselves (those never trigger a\n'
    '  // further follow-on).\n'
    '  severity_follow_on_id: string | null;\n'
    '}',
    '// Mirrors accumulate_answers()\'s return shape exactly (engine/main.py) --\n'
    '// A.2, this session: pluralized from accumulate_one_answer()\'s single-\n'
    '// option shape, since a weighted_multi_select answer (Q06) can select\n'
    '// more than one severity_trigger=true option at once (confirmed real,\n'
    '// not hypothetical: Q06\'s A -> SEVER-27 and D -> SEVER-21 are both\n'
    '// severity_trigger=true).\n'
    'export interface AccumulateResult {\n'
    '  accumulated_vector: AccumulatedVector;\n'
    '  // One entry per selected option whose answer maps to a real\n'
    '  // SeverityInput field -- [] when none do, including every core\n'
    '  // question that only triggers a follow-on without itself carrying one.\n'
    '  severity_inputs: SeverityInputPayload[];\n'
    '  // One entry per selected option carrying severity_trigger=true -- the\n'
    '  // SEVER-## question_id(s) to splice into the sequence next. [] when\n'
    '  // none do, including on SEVER-01..13 answers themselves (those never\n'
    '  // trigger a further follow-on... except via an explicit chain, e.g.\n'
    '  // SEVER-01 -> SEVER-12, which is exactly this same mechanism firing\n'
    '  // again one level deeper).\n'
    '  severity_follow_on_ids: string[];\n'
    '}',
)

edit(
    CLIENT,
    'export interface QuestionCopy {\n'
    '  question_id: string;\n'
    '  question_text: string;\n'
    '  options: Array<{ option_id: string; option_text: string }>;\n'
    '}',
    '// format ("forced_choice" | "weighted_multi_select") -- A.2, this\n'
    '// session. Drives QuestionView\'s rendering branch (checkbox-plus-\n'
    '// continue vs. single-click-advance) in web/components/DiagnosticFlow.tsx.\n'
    'export interface QuestionCopy {\n'
    '  question_id: string;\n'
    '  question_text: string;\n'
    '  format: "forced_choice" | "weighted_multi_select";\n'
    '  options: Array<{ option_id: string; option_text: string }>;\n'
    '}',
)

# ═══════════════════════════════════════════════════════════════════════
# web/lib/session-store.ts
# ═══════════════════════════════════════════════════════════════════════

edit(
    STORE,
    'export interface AnswerLogEntry {\n'
    '  question_id: string;\n'
    '  option_id: string;\n'
    '}',
    '// option_ids widened from a single option_id -- A.2, this session (Q06\n'
    '// weighted_multi_select). Every existing single-select entry now stores\n'
    '// a 1-element array -- one shape, not a dual-format union.\n'
    'export interface AnswerLogEntry {\n'
    '  question_id: string;\n'
    '  option_ids: string[];\n'
    '}',
)

# ═══════════════════════════════════════════════════════════════════════
# web/app/api/diagnostic/session/answer/route.ts
# ═══════════════════════════════════════════════════════════════════════

edit(
    ANSWER_ROUTE,
    'interface AnswerRequest {\n'
    '  session_id: string;\n'
    '  question_id: string;\n'
    '  option_id: string;\n'
    '}\n'
    '\n'
    'function validateRequest(body: unknown): body is AnswerRequest {\n'
    '  if (typeof body !== "object" || body === null) return false;\n'
    '  const b = body as Record<string, unknown>;\n'
    '  return (\n'
    '    typeof b.session_id === "string" &&\n'
    '    typeof b.question_id === "string" &&\n'
    '    typeof b.option_id === "string"\n'
    '  );\n'
    '}',
    '// option_ids widened from a single option_id -- A.2, this session (Q06\n'
    '// weighted_multi_select). Every single-select submission now sends a\n'
    '// 1-element array -- one code path, not a dual-format branch.\n'
    'interface AnswerRequest {\n'
    '  session_id: string;\n'
    '  question_id: string;\n'
    '  option_ids: string[];\n'
    '}\n'
    '\n'
    'function validateRequest(body: unknown): body is AnswerRequest {\n'
    '  if (typeof body !== "object" || body === null) return false;\n'
    '  const b = body as Record<string, unknown>;\n'
    '  return (\n'
    '    typeof b.session_id === "string" &&\n'
    '    typeof b.question_id === "string" &&\n'
    '    Array.isArray(b.option_ids) &&\n'
    '    b.option_ids.length > 0 &&\n'
    '    b.option_ids.every((v): v is string => typeof v === "string")\n'
    '  );\n'
    '}',
)

edit(
    ANSWER_ROUTE,
    '  const { session_id, question_id, option_id } = body;',
    '  const { session_id, question_id, option_ids } = body;',
)

edit(
    ANSWER_ROUTE,
    '  const accumulateResult = await invokeAccumulate({\n'
    '    accumulated_vector: session.accumulated_vector,\n'
    '    question_id,\n'
    '    option_id,\n'
    '    intake: session.intake,\n'
    '  });\n'
    '\n'
    '  const answerEntry: AnswerLogEntry = { question_id, option_id };\n'
    '  session.accumulated_vector = accumulateResult.accumulated_vector;\n'
    '  session.answers_log = [...session.answers_log, answerEntry];\n'
    '\n'
    '  // Severity follow-on wiring (Path 1): question_id itself was a SEVER-##\n'
    '  // follow-on that maps to a real SeverityInput field -- collect it for\n'
    '  // threading into invokeComplete() at Q34.\n'
    '  if (accumulateResult.severity_input) {\n'
    '    session.severity_inputs = [...session.severity_inputs, accumulateResult.severity_input];\n'
    '  }',
    '  const accumulateResult = await invokeAccumulate({\n'
    '    accumulated_vector: session.accumulated_vector,\n'
    '    question_id,\n'
    '    option_ids,\n'
    '    intake: session.intake,\n'
    '  });\n'
    '\n'
    '  const answerEntry: AnswerLogEntry = { question_id, option_ids };\n'
    '  session.accumulated_vector = accumulateResult.accumulated_vector;\n'
    '  session.answers_log = [...session.answers_log, answerEntry];\n'
    '\n'
    '  // Severity follow-on wiring (Path 1): question_id itself was a SEVER-##\n'
    '  // follow-on that maps to a real SeverityInput field -- collect it for\n'
    '  // threading into invokeComplete() at Q34. Plural (A.2, this session) --\n'
    '  // a weighted_multi_select answer can select more than one option that\n'
    '  // independently maps to a SeverityInput field.\n'
    '  if (accumulateResult.severity_inputs.length > 0) {\n'
    '    session.severity_inputs = [...session.severity_inputs, ...accumulateResult.severity_inputs];\n'
    '  }',
)

edit(
    ANSWER_ROUTE,
    '  // Severity follow-on splice — simple per-answer boolean check on the\n'
    '  // just-answered option\'s own severity_trigger flag (already present on\n'
    '  // AnswerOption, previously unread), NOT an entropy calculation like\n'
    '  // checkpoints use. Mirrors spliceDistinguishers()\'s existing pattern\n'
    '  // exactly, reusing the same function (a single-element distinguishers\n'
    '  // list is exactly what it already handles) rather than a parallel\n'
    '  // reimplementation. Guarded against re-firing an already-asked follow-on\n'
    '  // (SEVER-11\'s parked Q31 alternate parent means this only matters for\n'
    '  // Q28 today, but the guard is real, general infrastructure -- see\n'
    '  // session-store.ts).\n'
    '  const severityFollowOnId = accumulateResult.severity_follow_on_id;\n'
    '  if (\n'
    '    severityFollowOnId &&\n'
    '    !severityFollowOnAlreadyAsked(session.answers_log, severityFollowOnId)\n'
    '  ) {\n'
    '    session.question_sequence = spliceDistinguishers(\n'
    '      session.question_sequence,\n'
    '      currentIndex,\n'
    '      [severityFollowOnId],\n'
    '    );\n'
    '    session.question_labels[severityFollowOnId] = spliceLabel(question_id, 0, session.question_labels);\n'
    '  }',
    '  // Severity follow-on splice — per-answer boolean check on each\n'
    '  // selected option\'s own severity_trigger flag (already present on\n'
    '  // AnswerOption), NOT an entropy calculation like checkpoints use.\n'
    '  // Plural (A.2, this session): a weighted_multi_select answer can\n'
    '  // select more than one severity_trigger option at once (confirmed\n'
    '  // real for Q06: A -> SEVER-27, D -> SEVER-21), so this splices every\n'
    '  // new one from this submission in a single call, mirroring the\n'
    '  // checkpoint-distinguisher path\'s existing multi-ID + letterIndex\n'
    '  // labeling pattern below rather than a parallel reimplementation.\n'
    '  // Guarded per-ID against re-firing an already-asked follow-on (same\n'
    '  // severityFollowOnAlreadyAsked() infrastructure as before).\n'
    '  const newFollowOnIds = accumulateResult.severity_follow_on_ids.filter(\n'
    '    (id) => !severityFollowOnAlreadyAsked(session.answers_log, id),\n'
    '  );\n'
    '  if (newFollowOnIds.length > 0) {\n'
    '    session.question_sequence = spliceDistinguishers(\n'
    '      session.question_sequence,\n'
    '      currentIndex,\n'
    '      newFollowOnIds,\n'
    '    );\n'
    '    newFollowOnIds.forEach((followOnId, letterIndex) => {\n'
    '      session.question_labels[followOnId] = spliceLabel(question_id, letterIndex, session.question_labels);\n'
    '    });\n'
    '  }',
)

edit(
    ANSWER_ROUTE,
    '  if (question_id === "Q06" && (option_id === "A" || option_id === "B")) {',
    '  if (question_id === "Q06" && (option_ids.includes("A") || option_ids.includes("B"))) {',
)

edit(
    ANSWER_ROUTE,
    '  if (question_id === "Q44" && (option_id === "B" || option_id === "C" || option_id === "D")) {',
    '  if (question_id === "Q44" && (option_ids.includes("B") || option_ids.includes("C") || option_ids.includes("D"))) {',
)

# ═══════════════════════════════════════════════════════════════════════
# web/components/DiagnosticFlow.tsx
# ═══════════════════════════════════════════════════════════════════════

edit(
    FLOW,
    '// Mirrors web/lib/session-store.ts\'s QuestionLabel exactly -- redeclared\n'
    '// here rather than imported since that module pulls in server-only Redis\n'
    '// code ("use client" can\'t import it), same reason QuestionCopy below is\n'
    '// its own local type rather than imported from engine-client.ts.',
    '// Mirrors web/lib/session-store.ts\'s QuestionLabel exactly -- redeclared\n'
    '// here rather than imported since that module pulls in server-only Redis\n'
    '// code ("use client" can\'t import it), same reason QuestionCopy below is\n'
    '// its own local type rather than imported from engine-client.ts. format\n'
    '// added -- A.2, this session (Q06 weighted_multi_select).',
)

edit(
    FLOW,
    'interface QuestionCopy {\n'
    '  question_id: string;\n'
    '  question_text: string;\n'
    '  options: Array<{ option_id: string; option_text: string }>;\n'
    '}',
    'interface QuestionCopy {\n'
    '  question_id: string;\n'
    '  question_text: string;\n'
    '  format: "forced_choice" | "weighted_multi_select";\n'
    '  options: Array<{ option_id: string; option_text: string }>;\n'
    '}',
)

edit(
    FLOW,
    'function QuestionView({\n'
    '  question,\n'
    '  label,\n'
    '  onAnswer,\n'
    '}: {\n'
    '  question: QuestionCopy;\n'
    '  label: QuestionLabel;\n'
    '  onAnswer: (optionId: string) => void;\n'
    '}) {\n'
    '  return (\n'
    '    <div className="max-w-xl mx-auto px-6 py-16">\n'
    '      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-6">\n'
    '        {label.kind === "core"\n'
    '          ? `Question ${label.position} of ${label.total}`\n'
    '          : `Follow-up ${label.label}`}\n'
    '      </p>\n'
    '      <h2 className="font-display text-xl md:text-2xl text-charcoal mb-8 leading-snug">\n'
    '        {question.question_text}\n'
    '      </h2>\n'
    '      <div className="space-y-3">\n'
    '        {question.options.map((opt) => (\n'
    '          <button\n'
    '            key={opt.option_id}\n'
    '            onClick={() => onAnswer(opt.option_id)}\n'
    '            className="w-full text-left p-4 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-colors font-ui text-sm text-charcoal"\n'
    '          >\n'
    '            {opt.option_text}\n'
    '          </button>\n'
    '        ))}\n'
    '      </div>',
    '// A6-audit-style "none of the above" detection by text, not a hardcoded\n'
    '// option_id -- matches the intake form\'s SignificantEventsField\n'
    '// convention in spirit (a known escape-hatch option gets mutual-\n'
    '// exclusivity), generalizes to any future weighted_multi_select\n'
    '// question without a code change.\n'
    'function isNoneOption(optionText: string): boolean {\n'
    '  return optionText.trim().toLowerCase().startsWith("none of the above");\n'
    '}\n'
    '\n'
    'function QuestionView({\n'
    '  question,\n'
    '  label,\n'
    '  onAnswer,\n'
    '}: {\n'
    '  question: QuestionCopy;\n'
    '  label: QuestionLabel;\n'
    '  onAnswer: (optionIds: string[]) => void;\n'
    '}) {\n'
    '  const [selected, setSelected] = useState<string[]>([]);\n'
    '\n'
    '  // New question -- clear any in-progress multi-select state from the\n'
    '  // previous one. Keyed on question_id, not label, since spliced\n'
    '  // follow-ups reuse label shapes but never question_ids.\n'
    '  useEffect(() => {\n'
    '    setSelected([]);\n'
    '  }, [question.question_id]);\n'
    '\n'
    '  const isMultiSelect = question.format === "weighted_multi_select";\n'
    '\n'
    '  // None/other-options mutual exclusivity -- same convention as the\n'
    '  // intake form\'s SignificantEventsField.toggle(): selecting the none-\n'
    '  // option clears everything else; selecting anything else clears it.\n'
    '  function toggle(optionId: string) {\n'
    '    const opt = question.options.find((o) => o.option_id === optionId);\n'
    '    if (opt && isNoneOption(opt.option_text)) {\n'
    '      setSelected(selected.includes(optionId) ? [] : [optionId]);\n'
    '      return;\n'
    '    }\n'
    '    const noneId = question.options.find((o) => isNoneOption(o.option_text))?.option_id;\n'
    '    const withoutNone = selected.filter((id) => id !== noneId);\n'
    '    setSelected(\n'
    '      withoutNone.includes(optionId)\n'
    '        ? withoutNone.filter((id) => id !== optionId)\n'
    '        : [...withoutNone, optionId],\n'
    '    );\n'
    '  }\n'
    '\n'
    '  return (\n'
    '    <div className="max-w-xl mx-auto px-6 py-16">\n'
    '      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-6">\n'
    '        {label.kind === "core"\n'
    '          ? `Question ${label.position} of ${label.total}`\n'
    '          : `Follow-up ${label.label}`}\n'
    '      </p>\n'
    '      <h2 className="font-display text-xl md:text-2xl text-charcoal mb-8 leading-snug">\n'
    '        {question.question_text}\n'
    '      </h2>\n'
    '      {isMultiSelect ? (\n'
    '        <>\n'
    '          <div className="space-y-3">\n'
    '            {question.options.map((opt) => (\n'
    '              <label\n'
    '                key={opt.option_id}\n'
    '                className="flex items-start gap-3 w-full text-left p-4 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-colors font-ui text-sm text-charcoal cursor-pointer"\n'
    '              >\n'
    '                <input\n'
    '                  type="checkbox"\n'
    '                  checked={selected.includes(opt.option_id)}\n'
    '                  onChange={() => toggle(opt.option_id)}\n'
    '                  className="mt-0.5 shrink-0"\n'
    '                />\n'
    '                <span>{opt.option_text}</span>\n'
    '              </label>\n'
    '            ))}\n'
    '          </div>\n'
    '          <button\n'
    '            onClick={() => onAnswer(selected)}\n'
    '            disabled={selected.length === 0}\n'
    '            className="w-full bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed mt-3"\n'
    '          >\n'
    '            Continue\n'
    '          </button>\n'
    '        </>\n'
    '      ) : (\n'
    '        <div className="space-y-3">\n'
    '          {question.options.map((opt) => (\n'
    '            <button\n'
    '              key={opt.option_id}\n'
    '              onClick={() => onAnswer([opt.option_id])}\n'
    '              className="w-full text-left p-4 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-colors font-ui text-sm text-charcoal"\n'
    '            >\n'
    '              {opt.option_text}\n'
    '            </button>\n'
    '          ))}\n'
    '        </div>\n'
    '      )}',
)

edit(
    FLOW,
    '  async function handleAnswer(optionId: string) {\n'
    '    if (state.phase !== "question") return;\n'
    '    const { sessionId, question } = state;\n'
    '\n'
    '    setState({ phase: "loading" });\n'
    '    try {\n'
    '      const res = await fetch("/api/diagnostic/session/answer", {\n'
    '        method: "POST",\n'
    '        headers: { "Content-Type": "application/json" },\n'
    '        body: JSON.stringify({\n'
    '          session_id: sessionId,\n'
    '          question_id: question.question_id,\n'
    '          option_id: optionId,\n'
    '        }),\n'
    '      });',
    '  async function handleAnswer(optionIds: string[]) {\n'
    '    if (state.phase !== "question") return;\n'
    '    const { sessionId, question } = state;\n'
    '\n'
    '    setState({ phase: "loading" });\n'
    '    try {\n'
    '      const res = await fetch("/api/diagnostic/session/answer", {\n'
    '        method: "POST",\n'
    '        headers: { "Content-Type": "application/json" },\n'
    '        body: JSON.stringify({\n'
    '          session_id: sessionId,\n'
    '          question_id: question.question_id,\n'
    '          option_ids: optionIds,\n'
    '        }),\n'
    '      });',
)


# ═══════════════════════════════════════════════════════════════════════
# web/lib/session-store.test.ts -- 3 literals updated to the widened shape.
# ═══════════════════════════════════════════════════════════════════════

edit(
    STORE_TEST,
    '    const log: AnswerLogEntry[] = [{ question_id: "Q22", option_id: "D" }];',
    '    const log: AnswerLogEntry[] = [{ question_id: "Q22", option_ids: ["D"] }];',
)

edit(
    STORE_TEST,
    '    const log: AnswerLogEntry[] = [\n'
    '      { question_id: "Q22", option_id: "D" },\n'
    '      { question_id: "SEVER-04", option_id: "D" },\n'
    '    ];',
    '    const log: AnswerLogEntry[] = [\n'
    '      { question_id: "Q22", option_ids: ["D"] },\n'
    '      { question_id: "SEVER-04", option_ids: ["D"] },\n'
    '    ];',
)

edit(
    STORE_TEST,
    '    const log: AnswerLogEntry[] = [\n'
    '      { question_id: "Q28", option_id: "C" },\n'
    '      { question_id: "SEVER-11", option_id: "B" },\n'
    '    ];',
    '    const log: AnswerLogEntry[] = [\n'
    '      { question_id: "Q28", option_ids: ["C"] },\n'
    '      { question_id: "SEVER-11", option_ids: ["B"] },\n'
    '    ];',
)

# ═══════════════════════════════════════════════════════════════════════
# tools/diagnostic_fast_forward.py -- same live wire contract, updated to
# match or it would silently break next run.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FAST_FORWARD,
    '        answer_resp = client.post(\n'
    '            "/api/diagnostic/session/answer",\n'
    '            {"session_id": session_id, "question_id": question_id, "option_id": option_id},\n'
    '        )',
    '        answer_resp = client.post(\n'
    '            "/api/diagnostic/session/answer",\n'
    '            {"session_id": session_id, "question_id": question_id, "option_ids": [option_id]},\n'
    '        )',
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
