"use client";

import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import type { PrivateOutputPayload } from "@/lib/types";
import PrivateOutput from "@/components/PrivateOutput";

// ---------------------------------------------------------------------------
// Path 1 (Session 71, Phase 1) — live sequential-question diagnostic.
//
// One question at a time. Checkpoint distinguishers, severity follow-ons,
// and Q28's Q06-conditional splice are all live -- the question label
// (below) reflects whichever of those the session/answer route resolves,
// not a hardcoded position. No narrative textbox, no Aptitude addenda.
// ---------------------------------------------------------------------------

// Mirrors web/lib/session-store.ts's QuestionLabel exactly -- redeclared
// here rather than imported since that module pulls in server-only Redis
// code ("use client" can't import it), same reason QuestionCopy below is
// its own local type rather than imported from engine-client.ts.
type QuestionLabel =
  | { kind: "core"; position: number; total: number }
  | { kind: "spliced"; label: string };

// Value vocabularies mirror engine/data/intake.py's INTAKE_FIELDS wherever
// an engine equivalent exists (organization_size <- headcount, industry,
// role_level <- principal_role) so form values actually match what
// is_high_hazard / ROLE_COEFFICIENTS lookups expect server-side, rather
// than free text that silently falls back to "Other". tenure_in_role,
// direct_reports, and the jurisdiction list have no engine equivalent —
// new Phase-1-only fields (session-store.ts / MOB Section 5 locked spec).
const ORGANIZATION_SIZE_OPTIONS = [
  "Under 25", "25-99", "100-249", "250-499", "500-999", "1000+",
];
const INDUSTRY_OPTIONS = [
  "Professional Services", "Healthcare & Life Sciences", "Financial Services",
  "Technology", "Manufacturing & Industrial", "Retail & Hospitality",
  "Nonprofit & Education", "Government & Public Sector", "Other",
];
const ROLE_LEVEL_OPTIONS = [
  "Owner or founder", "C-suite", "VP or senior director", "HR leader",
  "Board member", "Other",
];
const TENURE_OPTIONS = [
  "Under 1 year", "1-3 years", "3-5 years", "5-10 years", "10+ years",
];
const DIRECT_REPORTS_OPTIONS = ["0", "1-5", "6-15", "16-50", "50+"];
const JURISDICTION_OPTIONS = [
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
  "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
  "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
  "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
  "WV", "WI", "WY",
];

interface IntakeFormState {
  organization_size: string;
  industry: string;
  role_level: string;
  tenure_in_role: string;
  direct_reports: string;
  jurisdiction: string;
}

const EMPTY_INTAKE: IntakeFormState = {
  organization_size: "",
  industry: "",
  role_level: "",
  tenure_in_role: "",
  direct_reports: "",
  jurisdiction: "",
};

interface QuestionCopy {
  question_id: string;
  question_text: string;
  options: Array<{ option_id: string; option_text: string }>;
}

type FlowState =
  | { phase: "intake" }
  | { phase: "loading" }
  | { phase: "question"; sessionId: string; question: QuestionCopy; label: QuestionLabel }
  | { phase: "complete"; result: PrivateOutputPayload }
  | { phase: "error"; message: string };

const ERROR_COPY = "Something went wrong. Please try again.";

// ── Intake form ────────────────────────────────────────────────────────────

function IntakeForm({
  intake,
  onChange,
  onSubmit,
}: {
  intake: IntakeFormState;
  onChange: (next: IntakeFormState) => void;
  onSubmit: () => void;
}) {
  const isComplete = Object.values(intake).every((v) => v !== "");

  function field(
    label: string,
    key: keyof IntakeFormState,
    options: string[],
  ) {
    return (
      <div className="mb-5">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          {label}
        </label>
        <select
          value={intake[key]}
          onChange={(e) => onChange({ ...intake, [key]: e.target.value })}
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
        >
          <option value="">Select…</option>
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto px-6 py-16">
      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">
        Before you start
      </p>
      <h2 className="font-display text-2xl text-charcoal mb-8">
        A few things about your organization.
      </h2>

      {field("Organization size", "organization_size", ORGANIZATION_SIZE_OPTIONS)}
      {field("Industry", "industry", INDUSTRY_OPTIONS)}
      {field("Your role level", "role_level", ROLE_LEVEL_OPTIONS)}
      {field("Tenure in this role", "tenure_in_role", TENURE_OPTIONS)}
      {field("Direct reports", "direct_reports", DIRECT_REPORTS_OPTIONS)}
      {field("Primary jurisdiction", "jurisdiction", JURISDICTION_OPTIONS)}

      <button
        onClick={onSubmit}
        disabled={!isComplete}
        className="w-full bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed mt-3"
      >
        Begin the diagnostic
      </button>
    </div>
  );
}

// ── Question view ───────────────────────────────────────────────────────────

function QuestionView({
  question,
  label,
  onAnswer,
}: {
  question: QuestionCopy;
  label: QuestionLabel;
  onAnswer: (optionId: string) => void;
}) {
  return (
    <div className="max-w-xl mx-auto px-6 py-16">
      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-6">
        {label.kind === "core"
          ? `Question ${label.position} of ${label.total}`
          : `Follow-up ${label.label}`}
      </p>
      <h2 className="font-display text-xl md:text-2xl text-charcoal mb-8 leading-snug">
        {question.question_text}
      </h2>
      <div className="space-y-3">
        {question.options.map((opt) => (
          <button
            key={opt.option_id}
            onClick={() => onAnswer(opt.option_id)}
            className="w-full text-left p-4 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-colors font-ui text-sm text-charcoal"
          >
            {opt.option_text}
          </button>
        ))}
      </div>
    </div>
  );
}

// ── Main export ───────────────────────────────────────────────────────────

export default function DiagnosticFlow() {
  const [state, setState] = useState<FlowState>({ phase: "intake" });
  const [intake, setIntake] = useState<IntakeFormState>(EMPTY_INTAKE);

  // Additive resume capability (not part of the original Session 71 build):
  // a ?session=<id> query param, if present, skips the intake form entirely
  // and jumps straight to that session's current question -- used by
  // tools/diagnostic_fast_forward.py's Mode 2 and any Pete-held mid-flow
  // link. resumeAttempted guards against re-firing on re-render (searchParams
  // is not a stable reference across renders); absent the param, this effect
  // is a no-op and `state` never leaves its initial { phase: "intake" } --
  // the normal path every real respondent uses is untouched.
  const searchParams = useSearchParams();
  const resumeAttempted = useRef(false);

  async function handleResume(sessionId: string) {
    setState({ phase: "loading" });
    try {
      const res = await fetch("/api/diagnostic/session/resume", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      if (!res.ok) {
        setState({
          phase: "error",
          message:
            "This session could not be resumed. It may have expired, already completed, or the link may be invalid.",
        });
        return;
      }
      const data = await res.json();
      setState({
        phase: "question",
        sessionId,
        question: data.question,
        label: data.label,
      });
    } catch {
      setState({ phase: "error", message: ERROR_COPY });
    }
  }

  useEffect(() => {
    if (resumeAttempted.current) return;
    resumeAttempted.current = true;
    const sessionId = searchParams.get("session");
    if (!sessionId) return;
    // One-time mount check for a URL-driven resume, mirroring handleStart's
    // own async-fetch-then-setState shape (triggered by mount instead of a
    // click) -- not a synchronous setState cascade despite the rule's
    // generic pattern match.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    handleResume(sessionId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleStart() {
    setState({ phase: "loading" });
    try {
      const res = await fetch("/api/diagnostic/session/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(intake),
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
        label: data.label,
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
      const res = await fetch("/api/diagnostic/session/answer", {
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
      if (data.status === "complete") {
        setState({ phase: "complete", result: data.result as PrivateOutputPayload });
      } else {
        setState({
          phase: "question",
          sessionId,
          question: data.question,
          label: data.label,
        });
      }
    } catch {
      setState({ phase: "error", message: ERROR_COPY });
    }
  }

  if (state.phase === "complete") {
    const { result } = state;
    return (
      <div className="max-w-2xl mx-auto px-6 py-16">
        <PrivateOutput
          payload={result}
          selectedStateIds={[
            result.primary_state.id,
            ...result.secondary_states.map((s) => s.id),
          ]}
          intake={{
            headcount: "",
            industry: "",
            orgType: "",
            jurisdictions: [],
            significantEvents: [],
            principalRole: "",
          }}
          enableSharing={false}
        />
      </div>
    );
  }

  if (state.phase === "error") {
    return (
      <div className="max-w-2xl mx-auto px-6 py-16 text-center">
        <p className="font-display text-2xl text-charcoal mb-4">{state.message}</p>
        <button
          onClick={() => setState({ phase: "intake" })}
          className="bg-charcoal text-white font-ui text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"
        >
          Start over
        </button>
      </div>
    );
  }

  if (state.phase === "loading") {
    return (
      <div className="max-w-2xl mx-auto px-6 py-16 text-center">
        <p className="font-ui text-sm text-gray-400">Loading…</p>
      </div>
    );
  }

  if (state.phase === "question") {
    return (
      <QuestionView
        question={state.question}
        label={state.label}
        onAnswer={handleAnswer}
      />
    );
  }

  // state.phase === "intake"
  return <IntakeForm intake={intake} onChange={setIntake} onSubmit={handleStart} />;
}
