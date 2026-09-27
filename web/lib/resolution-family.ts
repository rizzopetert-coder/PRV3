// PRV3 -- Engine → commercial resolution-family name translation.
//
// Mirrors engine/resolution_families.py's ENGINE_TO_COMMERCIAL_NAME +
// translate_resolution_family() exactly. No TS equivalent existed before
// this build -- three route files (result/route.ts, session/answer/
// route.ts, share/create/route.ts) had each independently duplicated a
// getPrimaryFamily() reading a dead Python system (engine/resolution_
// families.py's own get_family()/STATE_RESOLUTION_FAMILY, confirmed zero
// real callers), causing PrivateOutputPayload/ShareableOutputPayload.
// resolution_family to diverge from the real engine output for 50 of 57
// states. This file is the single, shared source those three routes now
// import instead of re-duplicating the mapping a fourth time.
//
// Scope: resolution_family only (the field that renders client-facing on
// PrivateOutput.tsx and ShareableOutput.tsx). resolution_routing stays
// raw/untranslated, read directly from
// engineResult.private_output.resolution_routing -- that field is
// already the correct, real engine value (confirmed: private_output.
// resolution_routing is never translated anywhere in the Python
// pipeline) and is not touched by this file.

import type { HrPathway, ResolutionFamily } from "@/lib/types";

// hr_diagnostic (hr-dx.com) display value for resolution_family and
// resolution_routing -- every engine family and compound maps here, so
// no PR tier name reaches that brand. Mirrors engine/resolution_
// families.py's HR_DIAGNOSTIC_FAMILY_NAME; keep both in lockstep.
// Server-side only (imported by route/lib code, never a client component).
export const HR_DIAGNOSTIC_RESOLUTION_FAMILY: ResolutionFamily = "HR Consulting";

// hr_diagnostic drawer pathway from the raw engine routing. Same compound
// priority as the hr backup copy (engine/resolution_families.py
// _HR_DIAGNOSTIC_SPECIALTY_PRIORITY): Intervention first, then the first
// of Development / Executive Counsel in order, then the first part.
// Unknown or empty routing -> undefined (drawer uses its generic text).
const HR_PATHWAY_BY_ENGINE_FAMILY: Record<string, HrPathway> = {
  Roadmap: "structure",
  Development: "capability",
  "Executive Counsel": "leadership",
  Intervention: "urgent",
};

export function hrPathwayForRouting(engineFamilyStr: string): HrPathway | undefined {
  const parts = engineFamilyStr
    .split(" + ")
    .map((p) => p.trim())
    .filter((p) => p in HR_PATHWAY_BY_ENGINE_FAMILY);
  if (parts.length === 0) return undefined;
  if (parts.includes("Intervention")) return "urgent";
  const specialty = parts.find((p) => p === "Development" || p === "Executive Counsel");
  return HR_PATHWAY_BY_ENGINE_FAMILY[specialty ?? parts[0]];
}

// Commercial-name correction (this session): "People Tactics and Strategy"
// -> "People Tactics & Strategy" (ampersand), "Intervention" -> "First Call".
// Dict KEYS (raw engine routing names) are unchanged -- only the VALUES.
// Mirrors engine/resolution_families.py's ENGINE_TO_COMMERCIAL_NAME exactly;
// keep both in lockstep.
export const ENGINE_TO_COMMERCIAL_NAME: Record<string, string> = {
  Roadmap:           "People Tactics & Strategy",
  Development:       "Training & Development",
  Intervention:      "First Call",
  "Executive Counsel": "Executive Advisory",
};

// Translates a raw engine resolution_family string (e.g. "Roadmap" or the
// compound "Roadmap + Intervention") to its commercial equivalent.
// Compound handling matches the Python source exactly: split on " + ",
// translate each part independently, rejoin with " + ". Unknown parts
// pass through unchanged. Empty input passes through unchanged (matches
// priv-None sessions, where resolution_routing is already "").
export function translateResolutionFamily(engineFamilyStr: string): ResolutionFamily {
  const parts = engineFamilyStr.split(" + ").map((p) => p.trim());
  const translated = parts.map((p) => ENGINE_TO_COMMERCIAL_NAME[p] ?? p);
  return translated.join(" + ") as ResolutionFamily;
}
