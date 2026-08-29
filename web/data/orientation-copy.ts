import type { BookContentType, BookVoice } from "@/lib/book-manifest";
import type { ResolutionFamily, SeverityTier } from "@/lib/types";

// Contextual orientation copy -- the content half of the ContextOrientation
// component. Net-new file (confirmed no existing orientation-copy.ts or
// equivalent before this was written).
//
// Every entry here follows P-14 verbatim (tools/_mob.txt line 137): "When
// brand voice risks obscuring meaning, plain language wins -- don't make the
// reader do the work of decoding what could just be said directly." Plain
// operational language only -- what this screen shows, what to do next.
// State names, dimension names, severity-tier mechanics, and taxonomy terms
// belong to the diagnostic content itself, not to the copy explaining how to
// read that content -- keep that boundary even where a nearby block already
// uses those terms correctly.

export interface OrientationCopy {
  title: string;
  summary: string;
  details: string;
}

// ── Static registry -- one entry per hand-authored surface ─────────────────

export const ORIENTATION_COPY: Record<string, OrientationCopy> = {
  "diagnostic-intake": {
    title: "About this step",
    summary: "A few questions about your organization before you start.",
    details:
      "Nothing here is scored. It just gives the questions that follow the right context -- your industry, size, and role change which questions apply. Answer as accurately as you can; there's no way to get this part wrong.",
  },
  "diagnostic-question": {
    title: "About this question",
    summary: "Pick whichever answer is closest to true, even if none feel exact.",
    details:
      "Each question adds a small amount of signal. There's no way to see how any single answer affects the outcome, and that's by design -- answering for what's actually true, not what you think should be true, is what makes the result accurate.",
  },
  "diagnostic-checkpoint": {
    title: "About this question",
    summary: "This question is here because your earlier answers pointed somewhere specific.",
    details:
      "It's not a different kind of question, just one chosen based on what you've said so far, to get a more precise read faster. Answer it the same way as the others.",
  },
  "diagnostic-narrative": {
    title: "About this step",
    summary: "Optional. Write as much or as little as you want.",
    details:
      "This is the one place you can add something in your own words instead of picking from a list. It's used to sharpen the result, not required to get one -- skip it if nothing comes to mind.",
  },
  "book-toc": {
    title: "About this list",
    summary: "58 conditions the diagnostic can identify, browsable without taking it.",
    details:
      "Use the tags to narrow the list down to what sounds relevant. Selecting a condition shows what it looks like in practice and what tends to resolve it. This is for browsing and recognition -- it doesn't produce a diagnosis. Only the diagnostic itself does that.",
  },
};

// ── Templated helper: /book article pages ───────────────────────────────────

const BOOK_PIECE_BASE: Record<BookContentType, { title: string; summary: string; details: string }> = {
  memo: {
    title: "About this piece",
    summary: "A short, focused note on one specific idea.",
    details: "This is a memo -- a single point, made directly, not a full methodology writeup.",
  },
  methodology: {
    title: "About this piece",
    summary: "A longer explanation of how a specific part of the work actually operates.",
    details: "This piece goes into how something works, not just what it is -- expect more depth than a memo.",
  },
  case_pattern: {
    title: "About this piece",
    summary: "A composite pattern drawn from real engagements, not a single client story.",
    details: "Details are combined and altered so nothing here identifies a real organization or person -- the pattern itself is real, the specifics aren't traceable to any one case.",
  },
};

const FROM_THE_AUTHOR_ADDENDUM =
  " Written in first person -- this one reflects a direct, personal view rather than the site's usual voice.";

export function getBookPieceOrientation(
  contentType: BookContentType,
  voice: BookVoice,
): OrientationCopy {
  const base = BOOK_PIECE_BASE[contentType];
  return {
    title: base.title,
    summary: base.summary,
    details: voice === "from_the_author" ? base.details + FROM_THE_AUTHOR_ADDENDUM : base.details,
  };
}

// ── Templated helper: output screens ─────────────────────────────────────────
//
// Composed from two independent halves (severity-conditional + family-
// conditional) rather than 12 hand-authored severity x resolution_family
// combinations -- avoids drift between entries that should stay in sync,
// same reasoning as SEVERITY_ANCHOR/SEVERITY_TIER_BAND staying in one place
// in PrivateOutput.tsx. This copy explains how to read the SCREEN, not what
// the severity tier itself means (that's SEVERITY_ANCHOR's job, already
// shown elsewhere on the same screen) -- deliberately not duplicated here.

const RESULTS_SEVERITY_SUMMARY: Record<SeverityTier, string> = {
  Emerging: "This is a private read of what's showing up right now, early.",
  Entrenched: "This is a private read of a condition that's been present for a while.",
  Endemic: "This is a private read of a condition that's become how the organization operates.",
};

const RESULTS_FAMILY_DETAIL: Record<string, string> = {
  "People Tactics and Strategy":
    "The recommended next step below is practical and tactical -- specific actions, not a long engagement.",
  "Training & Development":
    "The recommended next step below is building a capability that isn't there yet, not fixing a single incident.",
  "Intervention":
    "The recommended next step below is direct, hands-on involvement -- this isn't something to wait out.",
  "Executive Advisory":
    "The recommended next step below is advisory -- working through the decision at the leadership level, not a program rollout.",
};

const RESULTS_FAMILY_DETAIL_FALLBACK =
  "The recommended next step is below, matched to what was found.";

export function getResultsOrientation(
  severityTier: SeverityTier,
  resolutionFamily: ResolutionFamily,
): OrientationCopy {
  return {
    title: "About this report",
    summary: RESULTS_SEVERITY_SUMMARY[severityTier],
    details:
      RESULTS_FAMILY_DETAIL[resolutionFamily] ?? RESULTS_FAMILY_DETAIL_FALLBACK,
  };
}
