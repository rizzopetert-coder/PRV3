"use client";

import { useState } from "react";
import type { QuestionCopy } from "@/lib/engine-client";
import type { CondensedOutputPayload } from "@/lib/types";
import { INDUSTRY_OPTIONS } from "@/components/DiagnosticFlow";
import CondensedOutput from "@/components/CondensedOutput";

// ---------------------------------------------------------------------------
// Category D (free condensed diagnostic), this session -- the missing piece
// found during Pete's own live verification: a working backend
// (web/app/api/diagnostic/condensed/{start,answer}) and a working result
// screen (CondensedOutput.tsx) existed with no page driving a visitor
// through the actual question-by-question flow between them. This is that
// page's flow component, mirroring DiagnosticFlow.tsx's real fetch/state-
// machine pattern (session/start, session/answer, phase state) but
// deliberately much smaller -- industry-only intake (one <select>, not the
// full 7-field IntakeForm), no multi-select handling (none of the 9 fixed
// questions use weighted_multi_select), no resume-by-URL, no checkpoints.
// ---------------------------------------------------------------------------

const ERROR_COPY = "Something went wrong. Please try again.";

type FlowState =
  | { phase: "intake" }
  | { phase: "loading" }
  | { phase: "question"; sessionId: string; question: QuestionCopy; position: number; total: number }
  | { phase: "complete"; result: CondensedOutputPayload }
  | { phase: "error"; message: string };

export default function CondensedDiagnosticFlow() {
  const [state, setState] = useState<FlowState>({ phase: "intake" });
  const [industry, setIndustry] = useState(INDUSTRY_OPTIONS[0]);

  async function handleStart() {
    setState({ phase: "loading" });
    try {
      const res = await fetch("/api/diagnostic/condensed/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ industry }),
      });
      if (!res.ok) {
        setState({ phase: "error", message: ERROR_COPY });
        return;
      }
      const data = await res.json();
      setState({
        phase: "question",
        sessionId: data.session_id,
        question: data.question,
        position: data.position,
        total: data.total,
      });
    } catch {
      setState({ phase: "error", message: ERROR_COPY });
    }
  }

  async function handleAnswer(optionId: string) {
    if (state.phase !== "question") return;
    const { sessionId, question } = state;

    setState({ phase: "loading" });
    try {
      const res = await fetch("/api/diagnostic/condensed/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          question_id: question.question_id,
          option_id: optionId,
        }),
      });
      if (!res.ok) {
        setState({ phase: "error", message: ERROR_COPY });
        return;
      }
      const data = await res.json();
      if (data.completed) {
        setState({ phase: "complete", result: data.result as CondensedOutputPayload });
      } else {
        setState({
          phase: "question",
          sessionId,
          question: data.question,
          position: data.position,
          total: data.total,
        });
      }
    } catch {
      setState({ phase: "error", message: ERROR_COPY });
    }
  }

  if (state.phase === "intake") {
    return (
      <div className="max-w-xl mx-auto px-6 py-16">
        <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-6">
          Free condensed diagnostic
        </p>
        <h2 className="font-display text-xl md:text-2xl text-charcoal mb-2 leading-snug">
          A quick read — 9 questions, under 5 minutes.
        </h2>
        <p className="text-sm text-gray-500 leading-relaxed mb-8">
          This is a thinner version of the full diagnostic. It names the most prominent pattern
          and gives you a rough sense of what it costs — the full diagnostic goes further.
        </p>
        <label className="block mb-6">
          <span className="font-ui text-xs text-gray-500 mb-1 block">Industry</span>
          <select
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm font-ui"
          >
            {INDUSTRY_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </label>
        <button
          onClick={handleStart}
          className="w-full bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors"
        >
          Begin
        </button>
      </div>
    );
  }

  if (state.phase === "loading") {
    return (
      <div className="max-w-xl mx-auto px-6 py-16">
        <p className="text-sm text-gray-400">Loading&hellip;</p>
      </div>
    );
  }

  if (state.phase === "error") {
    return (
      <div className="max-w-xl mx-auto px-6 py-16">
        <p className="text-sm text-charcoal">{state.message}</p>
      </div>
    );
  }

  if (state.phase === "complete") {
    return (
      <div className="max-w-2xl mx-auto px-6 py-16">
        <CondensedOutput payload={state.result} />
      </div>
    );
  }

  // phase === "question" -- forced_choice only, no multi-select handling:
  // none of Q01/Q05/Q07/Q12/Q14/Q15/Q26/Q47/Q50 use weighted_multi_select
  // (confirmed against the real _QDATA during the original candidate pull).
  const { question, position, total } = state;
  return (
    <div className="max-w-xl mx-auto px-6 py-16">
      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-6">
        Question {position} of {total}
      </p>
      <h2 className="font-display text-xl md:text-2xl text-charcoal mb-8 leading-snug">
        {question.question_text}
      </h2>
      <div className="space-y-3">
        {question.options.map((opt) => (
          <button
            key={opt.option_id}
            onClick={() => handleAnswer(opt.option_id)}
            className="w-full text-left p-4 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-colors font-ui text-sm text-charcoal"
          >
            {opt.option_text}
          </button>
        ))}
      </div>
    </div>
  );
}
