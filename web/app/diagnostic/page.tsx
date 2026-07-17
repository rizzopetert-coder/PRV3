"use client";

import { useState } from "react";
import {
  signatures,
  states,
  getDominantSignature,
  uiCopy,
} from "@/data/taxonomy";
import type { State } from "@/data/taxonomy";
import type { PrivateOutputPayload } from "@/lib/types";
import type { EnginePayload } from "@/lib/engine-client";
import SignatureCard from "@/components/SignatureCard";
import AssemblyPanel from "@/components/AssemblyPanel";
import PrivateOutput from "@/components/PrivateOutput";
import { StateDrawer } from "@/components/StateDrawer";
import { SelfSelectionProvider, useSelfSelection } from "@/context/SelfSelectionContext";
import DiagnosticFlow from "@/components/DiagnosticFlow";

type DiagnosticPath = "diagnostic" | "self-select" | null;

interface DiagnosticState {
  path: DiagnosticPath;
  currentPhase: number;
}

// ── Gate ──────────────────────────────────────────────────────────────────────

function DiagnosticGate({
  onChoose,
}: {
  onChoose: (path: DiagnosticPath) => void;
}) {
  return (
    <div className="max-w-2xl mx-auto px-6 py-16">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => onChoose("diagnostic")}
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
        <button
          onClick={() => onChoose("self-select")}
          className="text-left p-6 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-all duration-300 animate-fade-up"
        >
          <h2 className="font-display text-lg font-semibold text-charcoal mb-2">
            Start by recognizing.
          </h2>
          <p className="font-ui text-sm text-gray-600">
            Select what looks familiar. See what it means together.
          </p>
        </button>
      </div>
    </div>
  );
}

// ── Self-Selection Interface ───────────────────────────────────────────────────

interface SelfSelectionInterfaceProps {
  currentPhase: number;
  onPhaseAdvance: (phase: number) => void;
}

function SelfSelectionInterface({
  currentPhase,
  onPhaseAdvance,
}: SelfSelectionInterfaceProps) {
  const { selectedStateIds, selectedSignatureIds } = useSelfSelection();

  const [interpretation, setInterpretation] = useState<string | null>(null);
  const [isLoadingInterpretation, setIsLoadingInterpretation] = useState(false);
  const [resultPayload, setResultPayload] = useState<PrivateOutputPayload | null>(null);
  const [intakeForShare, setIntakeForShare] = useState<EnginePayload["intake"] | null>(null);
  const [isLoadingResult, setIsLoadingResult] = useState(false);

  const selectedStates: State[] = states.filter((s) =>
    selectedStateIds.has(s.id)
  );

  const showPhase1Bar =
    currentPhase === 1 &&
    (selectedStateIds.size >= 3 || selectedSignatureIds.size >= 1);
  const showPhase2Bar = currentPhase === 2;

  async function handleSeeWhatThisMeans() {
    if (selectedStateIds.size === 0) return;

    if (selectedStateIds.size === 1) {
      setInterpretation(uiCopy.singleStateEdgeCase);
      onPhaseAdvance(3);
      return;
    }

    const dominant = getDominantSignature([...selectedStateIds]);
    if (dominant && dominant.percentage >= 0.7) {
      const sig = signatures.find((s) => s.id === dominant.signatureId);
      setInterpretation(sig?.coexistenceInterpretation ?? null);
      onPhaseAdvance(3);
      return;
    }

    onPhaseAdvance(3);
    setIsLoadingInterpretation(true);
    try {
      const payload = selectedStates.map((s) => ({
        name: s.name,
        signatureId: s.signatureId,
      }));
      const res = await fetch("/api/interpret", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ states: payload }),
      });
      const data = await res.json();
      setInterpretation(data.interpretation ?? null);
    } finally {
      setIsLoadingInterpretation(false);
    }
  }

  async function handleTakeDiagnostic() {
    if (selectedStateIds.size === 0) return;
    const intake: EnginePayload["intake"] = {
      headcount: "",
      industry: "",
      orgType: "",
      jurisdictions: [],
      significantEvents: [],
      principalRole: "",
    };
    setIntakeForShare(intake);
    setIsLoadingResult(true);
    try {
      const res = await fetch("/api/result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selectedStateIds: [...selectedStateIds], intake }),
      });
      if (!res.ok) return;
      const payload = (await res.json()) as PrivateOutputPayload;
      setResultPayload(payload);
      onPhaseAdvance(5);
    } finally {
      setIsLoadingResult(false);
    }
  }

  // Phase 5 — PrivateOutput
  if (currentPhase === 5 && resultPayload && intakeForShare) {
    return (
      <PrivateOutput
        payload={resultPayload}
        selectedStateIds={[...selectedStateIds]}
        intake={intakeForShare}
      />
    );
  }

  return (
    <div className="flex min-h-screen bg-paper">
      <main className="flex-1 min-w-0 px-6 py-10 md:px-10 md:py-14 pb-36 md:pb-14">
        <div className={`max-w-5xl ${currentPhase === 1 ? "mx-auto" : ""}`}>

          {/* Phase 1 orientation block */}
          {currentPhase === 1 && (
            <div className="mb-8 max-w-2xl">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-3">
                What you&apos;re looking at
              </p>
              <p className="text-sm leading-relaxed text-gray-700 mb-2">
                Below are five patterns we see frequently in organizations
                experiencing friction. Each one is a cluster of conditions that
                tend to appear together. Read through them. Select the individual
                conditions that resemble what you&apos;re seeing in your
                organization. What you select will shape your signature.
              </p>
              <p className="text-sm leading-relaxed text-gray-500">
                You don&apos;t need to be certain. Select what sounds familiar.
              </p>
            </div>
          )}

          {/* Signature cards — phases 1–4 */}
          {currentPhase < 5 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 [&>*:last-child]:md:col-start-2">
              {signatures.map((sig) => (
                <div key={sig.id}>
                  <SignatureCard signature={sig} />
                  <StateDrawer signature={sig} />
                </div>
              ))}
            </div>
          )}

          {/* Phase 3 — Coexistence interpretation */}
          {currentPhase === 3 && (
            <div className="mt-10 pt-10 border-t border-gray-200 max-w-2xl">
              {isLoadingInterpretation ? (
                <p className="text-sm text-gray-400">Loading&hellip;</p>
              ) : (
                <p className="text-charcoal text-base leading-relaxed">
                  {interpretation}
                </p>
              )}
              {!isLoadingInterpretation && (
                <div className="mt-6">
                  <button
                    onClick={() => onPhaseAdvance(4)}
                    className="bg-charcoal text-white font-ui text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    {uiCopy.phase3CTALabel}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Phase 4 — Transition */}
          {currentPhase === 4 && (
            <div className="mt-10 pt-10 border-t border-gray-200 max-w-2xl">
              <p className="text-charcoal text-base leading-relaxed mb-6">
                {uiCopy.phase4Copy}
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={handleTakeDiagnostic}
                  disabled={isLoadingResult}
                  className="flex-1 bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {isLoadingResult ? "Synthesizing…" : uiCopy.diagnosticCTA}
                </button>
                <button className="flex-1 border border-charcoal text-charcoal font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-100 transition-colors">
                  {uiCopy.conversationCTA}
                </button>
              </div>
            </div>
          )}

        </div>
      </main>

      {/* Assembly Panel — phases 2–4 */}
      {currentPhase >= 2 && currentPhase < 5 && <AssemblyPanel />}

      {/* Phase 1 → Phase 2 transition bar */}
      {showPhase1Bar && (
        <div className="fixed bottom-0 left-0 right-0 z-30 bg-white border-t border-gray-200 px-6 py-4 flex justify-between items-center animate-fade-up">
          <span className="font-ui text-sm text-gray-500">
            {selectedStateIds.size}{" "}
            {selectedStateIds.size === 1 ? "condition" : "conditions"} selected
          </span>
          <button
            onClick={() => onPhaseAdvance(2)}
            className="bg-charcoal text-white font-ui text-sm font-medium px-6 py-2 hover:bg-gray-700 transition-colors rounded"
          >
            Let&apos;s take a closer look.
          </button>
        </div>
      )}

      {/* Phase 2 → Phase 3 transition bar */}
      {showPhase2Bar && (
        <div className="fixed bottom-0 left-0 right-0 z-30 bg-white border-t border-gray-200 px-6 py-4 flex justify-between items-center animate-fade-up">
          {selectedStateIds.size < 2 ? (
            <span className="font-ui text-xs text-gray-400">
              Select at least two conditions to continue.
            </span>
          ) : (
            <span className="font-ui text-sm text-gray-500">
              {selectedStateIds.size} conditions selected
            </span>
          )}
          <button
            onClick={handleSeeWhatThisMeans}
            disabled={selectedStateIds.size < 2}
            className="bg-charcoal text-white font-ui text-sm font-medium px-6 py-2 hover:bg-gray-700 transition-colors rounded disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {uiCopy.seeWhatThisMeans}
          </button>
        </div>
      )}
    </div>
  );
}

// ── Main export ───────────────────────────────────────────────────────────────

export default function DiagnosticPage() {
  const [diagnosticState, setDiagnosticState] = useState<DiagnosticState>({
    path: null,
    currentPhase: 0,
  });

  if (diagnosticState.path === null) {
    return (
      <div className="min-h-screen bg-paper transition-opacity duration-300">
        <DiagnosticGate
          onChoose={(path) =>
            setDiagnosticState({ path, currentPhase: 1 })
          }
        />
      </div>
    );
  }

  if (diagnosticState.path === "diagnostic") {
    return (
      <div className="min-h-screen bg-paper">
        <DiagnosticFlow />
      </div>
    );
  }

  return (
    <SelfSelectionProvider>
      <SelfSelectionInterface
        currentPhase={diagnosticState.currentPhase}
        onPhaseAdvance={(phase) =>
          setDiagnosticState((prev) => ({ ...prev, currentPhase: phase }))
        }
      />
    </SelfSelectionProvider>
  );
}
