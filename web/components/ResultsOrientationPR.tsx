"use client";

import ContextOrientation from "@/components/ContextOrientation";
import { getResultsOrientation } from "@/data/orientation-copy";
import { RESULTS_FAMILY_DETAIL } from "@/data/results-family-detail-pr";
import type { ResolutionFamily, SeverityTier } from "@/lib/types";

// principal_resolution "About this report" drawer -- details keyed by PR
// tier name. Loaded via next/dynamic from PrivateOutput.tsx only when brand
// is principal_resolution.
export default function ResultsOrientationPR({
  topic,
  severity,
  resolutionFamily,
}: {
  topic: string;
  severity: SeverityTier;
  resolutionFamily: ResolutionFamily;
}) {
  return (
    <ContextOrientation
      variant="inline"
      topic={topic}
      {...getResultsOrientation(severity, RESULTS_FAMILY_DETAIL[resolutionFamily])}
    />
  );
}
