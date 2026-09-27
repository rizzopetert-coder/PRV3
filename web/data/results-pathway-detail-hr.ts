import type { HrPathway } from "@/lib/types";

// hr_diagnostic "About this report" drawer details, keyed by the neutral
// hr_pathway the server computes (web/lib/resolution-family.ts
// hrPathwayForRouting). Pete-approved copy, 2026-09-27. Imported only by
// ResultsOrientationHR.tsx (code-split, hr_diagnostic only). No PR service
// tier names -- hr-dx must never download those.
export const RESULTS_PATHWAY_DETAIL_HR: Record<HrPathway, string> = {
  structure:
    "This pathway addresses how the organization is structured to operate, not just the people currently working within it. HR Consulting looks at where decision rights, role clarity, and reporting lines interact with what this diagnostic found, and builds a plan from there.",
  capability:
    "This pathway addresses a capability gap the diagnostic surfaced. HR Consulting, through Employee Training & Education and Learning & Development Consulting, builds a plan targeted at what was actually found, not a generic curriculum.",
  leadership:
    "This pathway centers on decisions that sit at the leadership level. HR Consulting brings an outside perspective to those decisions and practical support in acting on them.",
  urgent:
    "This pathway is for something that needs attention now, not on the usual planning cycle. HR Consulting can engage directly and quickly, working alongside leadership on what the diagnostic found before it develops further.",
};
