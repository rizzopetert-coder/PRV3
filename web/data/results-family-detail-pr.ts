// principal_resolution-only: "About this report" drawer details keyed by
// PR commercial tier name. Moved out of orientation-copy.ts (which hr-dx.com
// loads) so the tier names never reach hr-dx's bundle. Import only from
// PR-only modules (ResultsOrientationPR.tsx, ShareableOutput.tsx) -- never
// from shared code.
//
// Commercial-name correction (this session): "People Tactics and Strategy"
// -> "People Tactics & Strategy" (ampersand), "Intervention" -> "First Call".
// Keyed by the live ResolutionFamily commercial name, not an engine key --
// a stale key here silently falls through to orientation-copy.ts's
// RESULTS_FAMILY_DETAIL_FALLBACK rather than erroring, so this dict must be
// kept in lockstep with engine/resolution_families.py's
// ENGINE_TO_COMMERCIAL_NAME.
export const RESULTS_FAMILY_DETAIL: Record<string, string> = {
  "People Tactics & Strategy":
    "The recommended next step below is practical and tactical -- specific actions, not a long engagement.",
  "Training & Development":
    "The recommended next step below is building a capability that isn't there yet, not fixing a single incident.",
  "First Call":
    "The recommended next step below is direct, hands-on involvement -- this isn't something to wait out.",
  "Executive Advisory":
    "The recommended next step below is advisory -- working through the decision at the leadership level, not a program rollout.",
};
