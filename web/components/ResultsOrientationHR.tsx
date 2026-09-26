"use client";

import ContextOrientation from "@/components/ContextOrientation";
import { getResultsOrientation } from "@/data/orientation-copy";
import type { SeverityTier } from "@/lib/types";

// hr_diagnostic "About this report" drawer -- no family-specific details
// (those are keyed by PR tier name), so details falls back to
// orientation-copy.ts's existing generic RESULTS_FAMILY_DETAIL_FALLBACK.
// Loaded via next/dynamic from PrivateOutput.tsx only when brand is
// hr_diagnostic.
export default function ResultsOrientationHR({
  topic,
  severity,
}: {
  topic: string;
  severity: SeverityTier;
}) {
  return (
    <ContextOrientation
      variant="inline"
      topic={topic}
      {...getResultsOrientation(severity)}
    />
  );
}
