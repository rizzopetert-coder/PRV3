"use client";

import { useState } from "react";

// ---------------------------------------------------------------------------
// First Call Crisis Intake -- low-friction entry point for a client already
// in crisis. Routes to Pete for manual follow-up; no automatic agreement
// generation, no pricing shown here (matches web/app/engage/page.tsx's
// Phase 1 scope discipline for its own, different, purpose). Redis-only
// build this session -- see web/app/api/first-call/initiate/route.ts for the
// tracked Resend fast-follow.
// ---------------------------------------------------------------------------

type FirstCallState =
  | { phase: "form" }
  | { phase: "loading" }
  | { phase: "sent" }
  | { phase: "error"; message: string };

const ERROR_COPY =
  "Something went wrong. Please try again, or reach out directly at pete@principalresolution.com.";

const PERSONNEL_DISCLAIMER =
  "We do not handle union organizing, collective bargaining, or decertification. We will refer you to labor counsel. We do advise on established union relationship matters (such as grievances, day-to-day labor relations, and contract administration).";

const CRISIS_CATEGORIES = [
  {
    id: "safety",
    label: "Safety",
    examples:
      "Workplace violence or a credible threat, an OSHA-reportable injury or death stemming from an organizational failure, imminent physical safety risk.",
  },
  {
    id: "financial",
    label: "Financial",
    examples:
      "Filed legal action (lawsuit, EEOC/agency charge, DOL complaint, subpoena), an active regulatory investigation, discovered fraud or embezzlement.",
  },
  {
    id: "personnel",
    label: "Personnel",
    examples:
      "A sudden leadership departure creating an operational gap, a harassment or misconduct allegation against a senior leader, credible risk of mass departure.",
  },
] as const;

export default function FirstCallPage() {
  const [state, setState] = useState<FirstCallState>({ phase: "form" });
  const [organizationName, setOrganizationName] = useState("");
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [crisisCategories, setCrisisCategories] = useState<string[]>([]);
  const [description, setDescription] = useState("");

  const isComplete =
    organizationName.trim().length > 0 &&
    contactName.trim().length > 0 &&
    contactEmail.trim().length > 0 &&
    crisisCategories.length > 0;

  function toggleCategory(id: string) {
    setCrisisCategories((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  }

  async function handleSubmit() {
    if (!isComplete) return;
    setState({ phase: "loading" });
    try {
      const res = await fetch("/api/first-call/initiate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          organizationName,
          contactName,
          contactEmail,
          contactPhone: contactPhone || undefined,
          crisisCategories,
          description: description || undefined,
        }),
      });
      if (!res.ok) {
        setState({ phase: "error", message: ERROR_COPY });
        return;
      }
      setState({ phase: "sent" });
    } catch {
      setState({ phase: "error", message: ERROR_COPY });
    }
  }

  if (state.phase === "sent") {
    return (
      <main className="max-w-md mx-auto px-6 py-16 text-center">
        <h1 className="font-display text-2xl text-charcoal mb-4">We&apos;ve got this.</h1>
        <p className="font-ui text-sm text-slate leading-relaxed">
          Your submission is in. Pete will follow up directly at {contactEmail}.
        </p>
      </main>
    );
  }

  if (state.phase === "error") {
    return (
      <main className="max-w-md mx-auto px-6 py-16 text-center">
        <p className="font-display text-xl text-charcoal mb-6">{state.message}</p>
        <button
          onClick={() => setState({ phase: "form" })}
          className="bg-charcoal text-white font-ui text-sm font-medium px-5 py-2.5 rounded-lg hover:opacity-90 transition-opacity"
        >
          Try again
        </button>
      </main>
    );
  }

  const isLoading = state.phase === "loading";

  return (
    <main className="max-w-md mx-auto px-6 py-16">
      <p className="font-ui text-xs tracking-widest uppercase text-slate mb-2">First Call</p>
      <h1 className="font-display text-2xl text-charcoal mb-3">Tell us what&apos;s happening.</h1>
      <p className="font-ui text-sm text-slate leading-relaxed mb-10">
        This routes directly to Pete for follow-up. No pricing or agreement is generated here.
      </p>

      <div className="mb-5">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Organization name
        </label>
        <input
          type="text"
          value={organizationName}
          onChange={(e) => setOrganizationName(e.target.value)}
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
        />
      </div>

      <div className="mb-5">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Contact name
        </label>
        <input
          type="text"
          value={contactName}
          onChange={(e) => setContactName(e.target.value)}
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
        />
      </div>

      <div className="mb-5">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Contact email
        </label>
        <input
          type="email"
          value={contactEmail}
          onChange={(e) => setContactEmail(e.target.value)}
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
        />
      </div>

      <div className="mb-8">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Contact phone <span className="text-slate font-normal">(optional)</span>
        </label>
        <input
          type="tel"
          value={contactPhone}
          onChange={(e) => setContactPhone(e.target.value)}
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
        />
      </div>

      <div className="mb-8">
        <p className="font-ui text-sm font-medium text-charcoal mb-3">
          Crisis category <span className="text-slate font-normal">(select all that apply)</span>
        </p>
        <div className="space-y-4">
          {CRISIS_CATEGORIES.map((category) => (
            <div key={category.id}>
              <label className="flex items-start gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={crisisCategories.includes(category.id)}
                  onChange={() => toggleCategory(category.id)}
                  className="mt-0.5"
                />
                <span className="font-ui text-sm text-charcoal font-medium">{category.label}</span>
              </label>
              <p className="font-ui text-xs text-slate leading-relaxed mt-1 ml-6">
                {category.examples}
              </p>
              {category.id === "personnel" && crisisCategories.includes("personnel") && (
                <p className="font-ui text-xs text-charcoal leading-relaxed mt-2 ml-6 border-l-2 border-gray-200 pl-3">
                  {PERSONNEL_DISCLAIMER}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mb-8">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Brief description <span className="text-slate font-normal">(optional)</span>
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal resize-none"
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={!isComplete || isLoading}
        className="w-full bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {isLoading ? "Sending…" : "Send to Pete"}
      </button>
    </main>
  );
}
