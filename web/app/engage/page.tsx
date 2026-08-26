"use client";

import { useState } from "react";

// ---------------------------------------------------------------------------
// Real Transaction Path — Phase 1 (e-signature only). Architecture proposed,
// Gemini-reviewed, and finalized this session -- see
// prompts/real-transaction-path-phase1-gemini-request.md.
//
// Name and email are genuinely the only fields Dropbox Sign's hosted
// signing flow requires (confirmed directly against Dropbox Sign's API
// reference, not assumed) -- no headcount/industry/jurisdiction carried
// over from the diagnostic. Standalone entry point, reachable from
// PrivateOutput's Engage CTA or directly. On submit, Dropbox Sign emails
// the signer directly (hosted mode) -- this page never sees a signing_url
// or the document itself, and no payment is collected anywhere in this
// flow (decision 1, Phase 1 scope).
// ---------------------------------------------------------------------------

type EngageState =
  | { phase: "form" }
  | { phase: "loading" }
  | { phase: "sent" }
  | { phase: "error"; message: string };

const ERROR_COPY =
  "Something went wrong. Please try again, or reach out directly at pete@principalresolution.com.";

export default function EngagePage() {
  const [state, setState] = useState<EngageState>({ phase: "form" });
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  const isComplete = name.trim().length > 0 && email.trim().length > 0;

  async function handleSubmit() {
    if (!isComplete) return;
    setState({ phase: "loading" });
    try {
      const res = await fetch("/api/engage/initiate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email }),
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
        <h1 className="font-display text-2xl text-charcoal mb-4">Check your email.</h1>
        <p className="font-ui text-sm text-gray-500 leading-relaxed">
          The engagement agreement is on its way to {email}. Sign it there —
          there&apos;s nothing further to do on this page.
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
          className="bg-charcoal text-white font-ui text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"
        >
          Try again
        </button>
      </main>
    );
  }

  const isLoading = state.phase === "loading";

  return (
    <main className="max-w-md mx-auto px-6 py-16">
      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">
        Engagement
      </p>
      <h1 className="font-display text-2xl text-charcoal mb-3">
        Start the engagement.
      </h1>
      <p className="font-ui text-sm text-gray-500 leading-relaxed mb-10">
        We&apos;ll send the engagement agreement to your email for signature.
        No payment is collected here.
      </p>

      <div className="mb-5">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Your name
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
        />
      </div>
      <div className="mb-8">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Your email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={!isComplete || isLoading}
        className="w-full bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {isLoading ? "Sending…" : "Send the agreement"}
      </button>
    </main>
  );
}
