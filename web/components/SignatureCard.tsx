"use client";

import { useEffect, useState } from "react";
import { getStatesForSignature } from "@/data/taxonomy";
import type { Signature } from "@/data/taxonomy";
import { useSelfSelection } from "@/context/SelfSelectionContext";

interface SignatureCardProps {
  signature: Signature;
}

export default function SignatureCard({ signature }: SignatureCardProps) {
  const { selectedSignatureIds, selectedStateIds, toggleSignature, setActiveSheet } =
    useSelfSelection();

  const isClusterSelected = selectedSignatureIds.has(signature.id);
  const stateIds = getStatesForSignature(signature.id).map((s) => s.id);
  const hasAnyStateSelected = stateIds.some((id) => selectedStateIds.has(id));

  const [pulse, setPulse] = useState(false);

  function handleClusterToggle() {
    toggleSignature(signature.id, stateIds);
    setPulse(true);
  }

  useEffect(() => {
    if (!pulse) return;
    const t = setTimeout(() => setPulse(false), 150);
    return () => clearTimeout(t);
  }, [pulse]);

  const isSelected = isClusterSelected || hasAnyStateSelected;

  return (
    <div
      className={`rounded-xl border transition-colors ${
        pulse ? "animate-card-pulse" : ""
      } ${
        isSelected
          ? "border-gray-900 bg-[#EFEDE8]"
          : "border-gray-200 bg-white"
      }`}
    >
      {/* Card header — cluster select affordance top-right */}
      <div className="px-5 pt-5 pb-4 flex justify-between items-start gap-3">
        <h3 className="font-display text-xl font-bold text-gray-900 leading-snug">
          {signature.name}
        </h3>
        <button
          onClick={handleClusterToggle}
          className="font-ui text-xs text-gray-500 hover:text-gray-900 transition-colors shrink-0 mt-1"
          aria-label={
            isClusterSelected
              ? `Deselect all conditions in ${signature.name}`
              : `Select all conditions in ${signature.name}`
          }
        >
          {isClusterSelected ? "Deselect all" : "Select all"}
        </button>
      </div>

      {/* Recognition copy */}
      <p className="font-display text-base text-gray-700 leading-relaxed px-5 pb-4">
        {signature.description}
      </p>

      {/* Drawer trigger */}
      <div className="px-5 pb-5">
        <button
          onClick={() => setActiveSheet(signature.id)}
          className="font-ui text-sm text-gray-500 hover:text-gray-900 transition-colors text-left"
        >
          See the conditions inside →
        </button>
      </div>
    </div>
  );
}
