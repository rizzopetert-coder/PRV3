"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useBrand } from "@/components/BrandContext";
import { useSearchParams } from "next/navigation";
import DiagnosticFlow from "@/components/DiagnosticFlow";

// Path B (self-select) lives at app/(site)/diagnostic/self-select/page.tsx,
// not here. It used to be an in-page branch of this file, which meant this
// route statically imported @/data/taxonomy -- and Next bundles by import
// graph, not by which branch renders, so hr-dx.com's /diagnostic shipped
// PRV3's full state taxonomy in its JS even with the branch hidden. This
// file must never import @/data/taxonomy, or any component that does
// (AssemblyPanel, SignatureCard, StateDrawer), directly or transitively.

// ── Gate ──────────────────────────────────────────────────────────────────────

function DiagnosticGate({ onChooseDiagnostic }: { onChooseDiagnostic: () => void }) {
  // hr_diagnostic: self-select (Path B) is hidden here and walled off at the
  // routing layer -- /diagnostic/self-select, /api/result and /api/interpret
  // all 404 on that hostname (see middleware.ts) since Path B exposes PRV3's
  // full 58-state taxonomy, which this hostname must never reveal.
  const brand = useBrand();
  const diagnosticOnly = brand === "hr_diagnostic";

  return (
    <div className="max-w-2xl mx-auto px-6 py-16">
      <div
        className={
          diagnosticOnly
            ? "grid grid-cols-1 gap-4"
            : "grid grid-cols-1 md:grid-cols-2 gap-4"
        }
      >
        <button
          onClick={onChooseDiagnostic}
          className="text-left p-6 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-all duration-300 animate-fade-up"
        >
          <h2 className="font-display text-lg font-semibold text-charcoal mb-2">
            Take the diagnostic.
          </h2>
          <p className="font-ui text-sm text-gray-600">
            Answer questions. Get a complete read of what your organization is
            carrying.
          </p>
        </button>
        {!diagnosticOnly && (
          <Link
            href="/diagnostic/self-select"
            className="block text-left p-6 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-all duration-300 animate-fade-up"
          >
            <h2 className="font-display text-lg font-semibold text-charcoal mb-2">
              Start by recognizing.
            </h2>
            <p className="font-ui text-sm text-gray-600">
              Select what looks familiar. See what it means together.
            </p>
          </Link>
        )}
      </div>
    </div>
  );
}

// ── Main export ───────────────────────────────────────────────────────────────

// DiagnosticPage is a thin Suspense wrapper -- useSearchParams() (below, for
// the ?session= resume link) requires a Suspense boundary so a production
// static prerender of this route doesn't fail the build. Has no effect on
// the no-param path's rendered output.
export default function DiagnosticPage() {
  return (
    <Suspense fallback={null}>
      <DiagnosticPageInner />
    </Suspense>
  );
}

function DiagnosticPageInner() {
  // ?session=<id>, if present, skips the DiagnosticGate entirely and goes
  // straight to DiagnosticFlow (which itself resumes that session -- see
  // DiagnosticFlow.tsx) -- true "skip straight to the question view," not
  // just DiagnosticFlow resuming after a manual gate click. Lazy useState
  // initializer so this is decided once, on first render, from the URL
  // actually requested.
  const searchParams = useSearchParams();
  const [started, setStarted] = useState<boolean>(() =>
    Boolean(searchParams.get("session"))
  );

  if (!started) {
    return (
      <div className="min-h-screen bg-paper transition-opacity duration-300">
        <DiagnosticGate onChooseDiagnostic={() => setStarted(true)} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-paper">
      <DiagnosticFlow />
    </div>
  );
}
