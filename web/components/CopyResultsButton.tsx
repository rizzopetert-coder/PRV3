"use client";

import { useState } from "react";
import type { PrivateOutputPayload, TacticalSectionResult } from "@/lib/types";
import { buildResultsText } from "@/lib/output-text";

// "Copy results as text" -- this session. Same UX pattern as
// ShareButton.tsx's own copy step: a copied boolean, a 2s timeout reset,
// and a label toggle -- no new interaction idiom introduced. Unlike
// ShareButton, no backend round-trip is needed at all: payload is already
// fully present client-side by the time this renders, so there's no
// "creating"/"ready" state machine to build, just copy-or-not.
interface CopyResultsButtonProps {
  payload: PrivateOutputPayload;
  // hr-dx TC answers, copied only when Call 2 failed (see buildResultsText).
  tacticalResults?: TacticalSectionResult[];
}

export default function CopyResultsButton({ payload, tacticalResults }: CopyResultsButtonProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(buildResultsText(payload, tacticalResults));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <button
      onClick={handleCopy}
      className="w-full border border-charcoal text-charcoal text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-100 transition-colors"
    >
      {copied ? "Copied" : "Copy results"}
    </button>
  );
}
