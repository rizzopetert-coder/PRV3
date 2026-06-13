"use client";

import { useState } from "react";
import {
  signatures,
  states,
  getDominantSignature,
  uiCopy,
} from "@/data/taxonomy";
import type { State } from "@/data/taxonomy";
import SignatureCard from "@/components/SignatureCard";
import AssemblyPanel from "@/components/AssemblyPanel";

type Phase = 1 | 2 | 3 | 4;

export default function Home() {
  const [phase, setPhase] = useState<Phase>(1);
  const [selectedStateIds, setSelectedStateIds] = useState<string[]>([]);
  const [expandedSignatureIds, setExpandedSignatureIds] = useState<string[]>(
    []
  );
  const [interpretation, setInterpretation] = useState<string | null>(null);
  const [isLoadingInterpretation, setIsLoadingInterpretation] = useState(false);

  const selectedStates: State[] = states.filter((s) =>
    selectedStateIds.includes(s.id)
  );

  function handleSelectState(stateId: string) {
    setSelectedStateIds((prev) => {
      const next = prev.includes(stateId)
        ? prev.filter((id) => id !== stateId)
        : [...prev, stateId];
      if (phase === 1 && next.length > 0) setPhase(2);
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

  return (
    <div>
      <main>
        {/* Phases 1 + 2 — Signature Recognition and State Assembly */}
        <section>
          {phase === 1 && <p>{uiCopy.phase1Instruction}</p>}

          <div>
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

          {phase === 1 && selectedStateIds.length > 0 && (
            <button onClick={() => setPhase(2)}>
              {uiCopy.transitionTrigger}
            </button>
          )}

          {phase === 2 && selectedStateIds.length > 0 && (
            <button onClick={handleSeeWhatThisMeans}>
              {uiCopy.seeWhatThisMeans}
            </button>
          )}
        </section>

        {/* Phase 3 — Coexistence Interpretation */}
        {phase === 3 && (
          <section>
            {isLoadingInterpretation ? (
              <p>Loading&hellip;</p>
            ) : (
              <p>{interpretation}</p>
            )}
            {!isLoadingInterpretation && (
              <button onClick={() => setPhase(4)}>{uiCopy.phase4Copy}</button>
            )}
          </section>
        )}

        {/* Phase 4 — Transition */}
        {phase === 4 && (
          <section>
            <p>{uiCopy.phase4Copy}</p>
            <button>{uiCopy.diagnosticCTA}</button>
            <button>{uiCopy.conversationCTA}</button>
          </section>
        )}
      </main>

      {/* Assembly Panel — visible from Phase 2 onward */}
      {phase >= 2 && (
        <AssemblyPanel
          selectedStates={selectedStates}
          onRemove={handleRemoveState}
        />
      )}
    </div>
  );
}
