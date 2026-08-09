"use client";

import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import type { PrivateOutputPayload } from "@/lib/types";
import { SIGNIFICANT_EVENT_OPTIONS } from "@/lib/types";
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
// Intake Redesign -- Precise Headcount via "About How Many" Stepper
// (prompts/intake-headcount-precision-redesign.md). Increment schedule
// mirrors engine/data/intake.py's HEADCOUNT_FIELD_SPEC exactly. Stepping
// down uses the CURRENT bracket's increment, same as stepping up -- a
// real simplification right at a boundary crossing (e.g. 250 - 25 lands
// on 225, using the 250-500 bracket's step rather than switching to
// 100-249's), not hidden, flagged for review.
const HEADCOUNT_MAX = 1000;

function headcountStepSize(value: number): number {
  if (value < 50) return 1;
  if (value < 250) return 5;
  if (value < 500) return 25;
  return 100;
}

function stepHeadcount(value: number, direction: 1 | -1): number {
  const next = value + direction * headcountStepSize(value);
  return Math.max(1, Math.min(HEADCOUNT_MAX, next));
}

// Hoisted to module scope (was nested inside IntakeForm) -- a nested
// function component is redeclared on every parent render, which made
// React remount this <input> (destroying and recreating the DOM node)
// on every keystroke, racing against the browser's native input
// handling. Closes over nothing from IntakeForm's scope (HEADCOUNT_MAX
// and stepHeadcount are already module-level), so hoisting is a pure
// move, zero logic change.
function HeadcountStepper({
  value,
  onChange,
}: {
  value: number | "";
  onChange: (next: number | "") => void;
}) {
  const display = value === "" ? "" : value >= HEADCOUNT_MAX ? "1000+" : String(value);

  function handleTextChange(raw: string) {
    if (raw.trim() === "") {
      onChange("");
      return;
    }
    const digitsOnly = raw.replace(/[^\d]/g, "");
    if (digitsOnly === "") return;
    const parsed = parseInt(digitsOnly, 10);
    onChange(Math.max(1, Math.min(HEADCOUNT_MAX, parsed)));
  }

  return (
    <div className="mb-5">
      <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
        About how many employees?
      </label>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => onChange(value === "" ? 1 : stepHeadcount(value, -1))}
          disabled={value !== "" && value <= 1}
          className="w-9 h-9 shrink-0 rounded-lg border border-gray-200 text-charcoal font-ui text-lg disabled:opacity-30"
          aria-label="Decrease"
        >
          {"\u2212"}
        </button>
        <input
          type="text"
          inputMode="numeric"
          value={display}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder="e.g. 60"
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal text-center focus:outline-none focus:border-charcoal"
        />
        <button
          type="button"
          onClick={() => onChange(value === "" ? 1 : stepHeadcount(value, 1))}
          disabled={value === HEADCOUNT_MAX}
          className="w-9 h-9 shrink-0 rounded-lg border border-gray-200 text-charcoal font-ui text-lg disabled:opacity-30"
          aria-label="Increase"
        >
          +
        </button>
      </div>
    </div>
  );
}

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
  // number once selected; "" is the shared not-yet-selected sentinel,
  // same convention as every other field below. significant_events is the
  // one array-valued field -- [] is its own not-yet-selected sentinel,
  // handled separately in isComplete below since [] !== "" trivially.
  organization_size: number | "";
  industry: string;
  role_level: string;
  tenure_in_role: string;
  direct_reports: string;
  jurisdiction: string;
  significant_events: string[];
}

const EMPTY_INTAKE: IntakeFormState = {
  organization_size: "",
  industry: "",
  role_level: "",
  tenure_in_role: "",
  direct_reports: "",
  jurisdiction: "",
  significant_events: [],
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
  // Explicit field-by-field rather than the prior Object.values().every()
  // pattern -- that pattern silently broke once significant_events became
  // array-valued ([] !== "" is trivially true, so it would never have
  // blocked submission on its own).
  const isComplete =
    intake.organization_size !== "" &&
    intake.industry !== "" &&
    intake.role_level !== "" &&
    intake.tenure_in_role !== "" &&
    intake.direct_reports !== "" &&
    intake.jurisdiction !== "" &&
    intake.significant_events.length > 0;

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

  // None/other-events mutual exclusivity: checking "none" clears any other
  // selections, checking anything else clears "none" -- both being checked
  // simultaneously would be a logical contradiction the data model
  // shouldn't allow.
  function SignificantEventsField({
    value,
    onChange,
  }: {
    value: string[];
    onChange: (next: string[]) => void;
  }) {
    function toggle(eventValue: string) {
      if (eventValue === "none") {
        onChange(value.includes("none") ? [] : ["none"]);
        return;
      }
      const withoutNone = value.filter((v) => v !== "none");
      onChange(
        withoutNone.includes(eventValue)
          ? withoutNone.filter((v) => v !== eventValue)
          : [...withoutNone, eventValue]
      );
    }

    return (
      <div className="mb-5">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Any significant events in the past 18 months?
        </label>
        <div className="space-y-2.5 border border-gray-200 rounded-lg px-3 py-3 bg-white">
          {SIGNIFICANT_EVENT_OPTIONS.map((opt) => (
            <label
              key={opt.value}
              className="flex items-start gap-2 font-ui text-sm text-charcoal cursor-pointer"
            >
              <input
                type="checkbox"
                checked={value.includes(opt.value)}
                onChange={() => toggle(opt.value)}
                className="mt-0.5 shrink-0"
              />
              <span>{opt.label}</span>
            </label>
          ))}
        </div>
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

      <HeadcountStepper
        value={intake.organization_size}
        onChange={(next) => onChange({ ...intake, organization_size: next })}
      />
      {field("Industry", "industry", INDUSTRY_OPTIONS)}
      {field("Your role level", "role_level", ROLE_LEVEL_OPTIONS)}
      {field("Tenure in this role", "tenure_in_role", TENURE_OPTIONS)}
      {field("Direct reports", "direct_reports", DIRECT_REPORTS_OPTIONS)}
      {field("Primary jurisdiction", "jurisdiction", JURISDICTION_OPTIONS)}
      <SignificantEventsField
        value={intake.significant_events}
        onChange={(next) => onChange({ ...intake, significant_events: next })}
      />

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
            headcount: String(intake.organization_size),
            industry: intake.industry,
            // Not collected by Phase 1's intake form -- matches the locked
            // server-side default (_locked_intake_to_engine_intake(),
            // engine/main.py, Session 71 architecture decision).
            orgType: "",
            jurisdictions: intake.jurisdiction ? [intake.jurisdiction] : [],
            // Not collected by Phase 1's intake form -- matches the locked
            // server-side sentinel exactly (same function/decision as
            // orgType above), not an empty array.
            significantEvents: ["none"],
            principalRole: intake.role_level,
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
