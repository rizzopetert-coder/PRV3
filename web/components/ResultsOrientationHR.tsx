"use client";

import ContextOrientation from "@/components/ContextOrientation";
import { getResultsOrientation } from "@/data/orientation-copy";
import { RESULTS_PATHWAY_DETAIL_HR } from "@/data/results-pathway-detail-hr";
import type { HrPathway, SeverityTier } from "@/lib/types";

// hr_diagnostic "About this report" drawer. Details come from the neutral
// hr_pathway (server-computed, no PR tier names); absent pathway (empty
// routing) falls back to orientation-copy.ts's generic
// RESULTS_FAMILY_DETAIL_FALLBACK. Loaded via next/dynamic from
// PrivateOutput.tsx only when brand is hr_diagnostic.
export default function ResultsOrientationHR({
  topic,
  severity,
  pathway,
}: {
  topic: string;
  severity: SeverityTier;
  pathway?: HrPathway;
}) {
  return (
    <ContextOrientation
      variant="inline"
      topic={topic}
      {...getResultsOrientation(severity, pathway ? RESULTS_PATHWAY_DETAIL_HR[pathway] : undefined)}
    />
  );
}
