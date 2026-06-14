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

type Phase = 1 | 2 | 3 | 4 | 5;

export default function Home() {
  const [phase, setPhase] = useState<Phase>(1);
  const [selectedStateIds, setSelectedStateIds] = useState<string[]>([]);
  const [expandedSignatureIds, setExpandedSignatureIds] = useState<string[]>(
    []
  );
  const [interpretation, setInterpretation] = useState<string | null>(null);
  const [isLoadingInterpretation, setIsLoadingInterpretation] = useState(false);
  const [resultPayload, setResultPayload] = useState<PrivateOutputPayload | null>(null);
  const [intakeForShare, setIntakeForShare] = useState<EnginePayload["intake"] | null>(null);
  const [isLoadingResult, setIsLoadingResult] = useState(false);

  const selectedStates: State[] = states.filter((s) =>
    selectedStateIds.includes(s.id)
  );

  function handleSelectState(stateId: string) {
    setSelectedStateIds((prev) => {
      const next = prev.includes(stateId)
        ? prev.filter((id) => id !== stateId)
        : [...prev, stateId];
      return next;
    });
  }

  function handleRemoveState(stateId: string) {
    setSelectedStateIds((prev) => prev.filter((id) => id !== stateId));
  }

  function handleToggleExpand(signatureId: string) {
    setExpandedSignatureIds((prev) =>
      prev.includes(signatureId)
        ? prev.filter((id) => id !== signatureId)
        : [...prev, signatureId]
    );
  }

  async function handleSeeWhatThisMeans() {
    if (selectedStateIds.length === 0) return;

    if (selectedStateIds.length === 1) {
      setInterpretation(uiCopy.singleStateEdgeCase);
      setPhase(3);
      return;
    }

    const dominant = getDominantSignature(selectedStateIds);
    if (dominant && dominant.percentage >= 0.7) {
      const sig = signatures.find((s) => s.id === dominant.signatureId);
      setInterpretation(sig?.coexistenceInterpretation ?? null);
      setPhase(3);
      return;
    }

    setPhase(3);
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
    if (selectedStateIds.length === 0) return;
    // Path B: intake fields not yet collected in self-selection flow.
    // Engine uses selectedStateIds as declared diagnosis; intake is echoed only.
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
        body: JSON.stringify({ selectedStateIds, intake }),
      });
      if (!res.ok) {
        return;
      }
      const payload = (await res.json()) as PrivateOutputPayload;
      setResultPayload(payload);
      setPhase(5);
    } finally {
      setIsLoadingResult(false);
    }
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <main className="flex-1 min-w-0 px-6 py-10 md:px-10 md:py-14 pb-20 md:pb-14">
        <div className={`max-w-2xl ${phase === 1 ? "mx-auto" : ""}`}>

          {/* Phase 5 — Private Output (result view, no assembly panel) */}
          {phase === 5 && resultPayload && intakeForShare && (
            <PrivateOutput
              payload={resultPayload}
              selectedStateIds={selectedStateIds}
              intake={intakeForShare}
            />
          )}

          {/* Phases 1–4: self-selection interface */}
          {phase < 5 && (
            <>
              {/* Phase 1 instruction */}
              {phase === 1 && (
                <p className="text-sm text-gray-500 mb-8 leading-relaxed">
                  {uiCopy.phase1Instruction}
                </p>
              )}

              {/* Signature cards — visible in phases 1–4 */}
              <div className="space-y-3">
                {signatures.map((sig) => {
                  const sigSelected = selectedStates.some(
                    (s) => s.signatureId === sig.id
                  );
                  return (
                    <SignatureCard
                      key={sig.id}
                      signature={sig}
                      isSelected={sigSelected}
                      isExpanded={expandedSignatureIds.includes(sig.id)}
                      selectedStateIds={selectedStateIds}
                      onSelect={() => handleToggleExpand(sig.id)}
                      onToggleExpand={() => handleToggleExpand(sig.id)}
                      onSelectState={handleSelectState}
                    />
                  );
                })}
              </div>

              {/* Phase 1 CTA */}
              {phase === 1 && selectedStateIds.length > 0 && (
                <div className="mt-8">
                  <button
                    onClick={() => setPhase(2)}
                    className="bg-gray-900 text-white text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    {uiCopy.transitionTrigger}
                  </button>
                </div>
              )}

              {/* Phase 2 CTA */}
              {phase === 2 && selectedStateIds.length > 0 && (
                <div className="mt-8">
                  <button
                    onClick={handleSeeWhatThisMeans}
                    className="bg-gray-900 text-white text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    {uiCopy.seeWhatThisMeans}
                  </button>
                </div>
              )}

              {/* Phase 3 — Coexistence Interpretation */}
              {phase === 3 && (
                <div className="mt-10 pt-10 border-t border-gray-200">
                  {isLoadingInterpretation ? (
                    <p className="text-sm text-gray-400">Loading&hellip;</p>
                  ) : (
                    <p className="text-gray-900 text-base leading-relaxed">
                      {interpretation}
                    </p>
                  )}
                  {!isLoadingInterpretation && (
                    <div className="mt-6">
                      <button
                        onClick={() => setPhase(4)}
                        className="bg-gray-900 text-white text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"
                      >
                        {uiCopy.phase3CTALabel}
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Phase 4 — Transition */}
              {phase === 4 && (
                <div className="mt-10 pt-10 border-t border-gray-200">
                  <p className="text-gray-900 text-base leading-relaxed mb-6">
                    {uiCopy.phase4Copy}
                  </p>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <button
                      onClick={handleTakeDiagnostic}
                      disabled={isLoadingResult}
                      className="flex-1 bg-gray-900 text-white text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                      {isLoadingResult ? "Synthesizing…" : uiCopy.diagnosticCTA}
                    </button>
                    <button className="flex-1 border border-gray-900 text-gray-900 text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-100 transition-colors">
                      {uiCopy.conversationCTA}
                    </button>
                  </div>
                </div>
              )}
            </>
          )}

        </div>
      </main>

      {/* Assembly Panel — visible from Phase 2 through Phase 4 */}
      {phase >= 2 && phase < 5 && (
        <AssemblyPanel
          selectedStates={selectedStates}
          onRemove={handleRemoveState}
        />
      )}
    </div>
  );
}
