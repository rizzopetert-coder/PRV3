"""
Brand code-split for the three remaining hr-dx.com bundle leaks, found by
the 2026-09-26 chunk scan of hr-dx /diagnostic (clean 879103c build):
  - item E: "Principal Resolution's services" (DiagnosticFlow intake copy)
  - item G: all four PR tier names (orientation-copy.ts RESULTS_FAMILY_DETAIL)
  - PrivateOutput: "/book/toc" state links + "Start the engagement" CTA

Conditional rendering is not enough -- Next bundles by import graph, so a
brand ternary still ships the PR strings. Mechanism: next/dynamic inside
CLIENT components (DiagnosticFlow, PrivateOutput). Each brand-specific
module becomes its own chunk, fetched only when rendered. Confirmed against
this Next version's own docs (node_modules/next/dist/docs/01-app/02-guides/
lazy-loading.md): code splitting works for Client Components, and is
explicitly NOT supported when a Server Component dynamically imports one --
which is why the earlier server-layout attempt failed.

New modules (PR-only content never imported statically by shared code):
  - components/BeforeYouBeginCopyPR.tsx   PR copy, unchanged wording
  - components/BeforeYouBeginCopyHR.tsx   Pete-approved hr-dx copy
  - data/results-family-detail-pr.ts      RESULTS_FAMILY_DETAIL, moved verbatim
  - components/ResultsOrientationPR.tsx   drawer with PR tier-keyed details
  - components/ResultsOrientationHR.tsx   drawer with the existing fallback
                                          ("The recommended next step is
                                          below, matched to what was found.")
                                          -- already-shipped wording, no new
                                          copy invented
  - components/StateBookLinkPR.tsx        /book/toc state link
  - components/EngageCtaPR.tsx            "Ready to move on this?" block

ShareableOutput (share/[id], inside (site), PR-only, 404 on hr-dx) imports
the PR detail map statically -- no split needed there.

Usage:
    python tools/patch_brand_codesplit_e_g_output.py --dry-run
    python tools/patch_brand_codesplit_e_g_output.py --write
"""
import argparse
import pathlib
import sys

W = pathlib.Path('web')

NEW_FILES = {
    W / 'components/BeforeYouBeginCopyPR.tsx': '''"use client";

// principal_resolution half of DiagnosticFlow's "Before you begin"
// paragraph. Loaded via next/dynamic from DiagnosticFlow.tsx only when
// brand is principal_resolution -- never import this statically from
// shared code, or its text ships to hr-dx.com in the shared chunk.
export default function BeforeYouBeginCopyPR() {
  return (
    <>
      That&apos;s intentional — this is a starting point, not a full picture.
      Principal Resolution&apos;s services bring more objective data and a solution
      roadmap next, through a separate process built for exactly that.
    </>
  );
}
''',
    W / 'components/BeforeYouBeginCopyHR.tsx': '''"use client";

// hr_diagnostic half of DiagnosticFlow's "Before you begin" paragraph
// (Pete-approved copy). Loaded via next/dynamic from DiagnosticFlow.tsx
// only when brand is hr_diagnostic. Must never reference Principal
// Resolution or any PR service tier name.
export default function BeforeYouBeginCopyHR() {
  return (
    <>
      That&apos;s intentional: this is a starting point, not a full picture.
      OneDigital HR Consulting can bring more objective data and a solution
      roadmap next, through a separate process built for exactly that.
    </>
  );
}
''',
    W / 'data/results-family-detail-pr.ts': '''// principal_resolution-only: "About this report" drawer details keyed by
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
''',
    W / 'components/ResultsOrientationPR.tsx': '''"use client";

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
''',
    W / 'components/ResultsOrientationHR.tsx': '''"use client";

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
''',
    W / 'components/StateBookLinkPR.tsx': '''"use client";

import { stateIdToSlug } from "@/lib/state-slug";

// principal_resolution-only: co-occurring condition name linking into
// /book/toc. Loaded via next/dynamic from PrivateOutput.tsx only when
// brand is principal_resolution -- /book is walled off on hr-dx.com, and
// the route string itself must not ship there either.
export default function StateBookLinkPR({ id, name }: { id: string; name: string }) {
  return (
    <a
      href={`/book/toc#${stateIdToSlug(id)}`}
      className="font-display text-lg text-charcoal hover:underline"
    >
      {name}
    </a>
  );
}
''',
    W / 'components/EngageCtaPR.tsx': '''"use client";

import Link from "next/link";

// principal_resolution-only: Block 6 Engage CTA (Real Transaction Path,
// Phase 1). Links out to the standalone /engage intake (name + email
// only, per Phase 1's e-signature-only scope) rather than carrying any
// diagnostic result data forward -- Dropbox Sign's hosted signing flow
// needs nothing from this payload. Loaded via next/dynamic from
// PrivateOutput.tsx only when shown, which is never on hr-dx.com.
export default function EngageCtaPR() {
  return (
    <div className="mt-6 pt-6 border-t border-gray-200">
      <p className="text-[11px] uppercase tracking-wide text-slate mb-3">
        Ready to move on this?
      </p>
      <Link
        href="/engage"
        className="inline-block bg-charcoal text-white font-ui text-sm font-medium px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors"
      >
        Start the engagement →
      </Link>
    </div>
  );
}
''',
}

EDITS = [
    # ── orientation-copy.ts: PR tier-keyed map moves out ──────────────────────
    (W / 'data/orientation-copy.ts',
     'import type { ResolutionFamily, SeverityTier } from "@/lib/types";\n',
     'import type { SeverityTier } from "@/lib/types";\n',
     'drop ResolutionFamily import'),
    (W / 'data/orientation-copy.ts',
     '''// Commercial-name correction (this session): "People Tactics and Strategy"
// -> "People Tactics & Strategy" (ampersand), "Intervention" -> "First Call".
// Keyed by the live ResolutionFamily commercial name, not an engine key --
// a stale key here silently falls through to RESULTS_FAMILY_DETAIL_FALLBACK
// below rather than erroring, so this dict must be kept in lockstep with
// engine/resolution_families.py's ENGINE_TO_COMMERCIAL_NAME.
const RESULTS_FAMILY_DETAIL: Record<string, string> = {
  "People Tactics & Strategy":
    "The recommended next step below is practical and tactical -- specific actions, not a long engagement.",
  "Training & Development":
    "The recommended next step below is building a capability that isn't there yet, not fixing a single incident.",
  "First Call":
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
''',
     '''// Family-conditional half lives in data/results-family-detail-pr.ts, NOT
// here: it is keyed by PR commercial tier name, and this file is loaded on
// hr-dx.com (DiagnosticFlow imports ORIENTATION_COPY). Callers pass the
// looked-up detail string in; hr_diagnostic passes nothing and gets the
// generic fallback.
const RESULTS_FAMILY_DETAIL_FALLBACK =
  "The recommended next step is below, matched to what was found.";

export function getResultsOrientation(
  severityTier: SeverityTier,
  familyDetail?: string,
): OrientationCopy {
  return {
    title: "About this report",
    summary: RESULTS_SEVERITY_SUMMARY[severityTier],
    details: familyDetail ?? RESULTS_FAMILY_DETAIL_FALLBACK,
  };
}
''',
     'move RESULTS_FAMILY_DETAIL out'),

    # ── ShareableOutput.tsx: PR-only route, static import is fine ─────────────
    (W / 'components/ShareableOutput.tsx',
     'import { getResultsOrientation } from "@/data/orientation-copy";\n',
     'import { getResultsOrientation } from "@/data/orientation-copy";\n'
     '// PR-only surface (share/[id] sits inside (site), 404 on hr-dx.com), so a\n'
     '// static import of the PR tier-keyed map is safe here.\n'
     'import { RESULTS_FAMILY_DETAIL } from "@/data/results-family-detail-pr";\n',
     'import PR detail map'),
    (W / 'components/ShareableOutput.tsx',
     '          topic="output-shareable"\n'
     '          {...getResultsOrientation(payload.severity, payload.resolution_family)}\n',
     '          topic="output-shareable"\n'
     '          {...getResultsOrientation(payload.severity, RESULTS_FAMILY_DETAIL[payload.resolution_family])}\n',
     'ShareableOutput call site'),

    # ── DiagnosticFlow.tsx: item E ─────────────────────────────────────────────
    (W / 'components/DiagnosticFlow.tsx',
     'import { useSearchParams } from "next/navigation";\n',
     'import { useSearchParams } from "next/navigation";\n'
     'import dynamic from "next/dynamic";\n',
     'import dynamic'),
    (W / 'components/DiagnosticFlow.tsx',
     'import { ORIENTATION_COPY } from "@/data/orientation-copy";\n',
     'import { ORIENTATION_COPY } from "@/data/orientation-copy";\n'
     'import { useBrand } from "@/components/BrandContext";\n'
     '\n'
     '// Brand-specific "Before you begin" copy, code-split rather than a\n'
     '// ternary over inline strings: Next bundles by import graph, so inline\n'
     '// PR copy here would ship to hr-dx.com even when not rendered. Each half\n'
     '// is its own chunk, fetched only for the brand that renders it.\n'
     'const BeforeYouBeginCopyPR = dynamic(() => import("@/components/BeforeYouBeginCopyPR"));\n'
     'const BeforeYouBeginCopyHR = dynamic(() => import("@/components/BeforeYouBeginCopyHR"));\n',
     'import useBrand + dynamic copy'),
    (W / 'components/DiagnosticFlow.tsx',
     '  onSubmit: () => void;\n'
     '}) {\n'
     '  // Explicit field-by-field rather than the prior Object.values().every()\n',
     '  onSubmit: () => void;\n'
     '}) {\n'
     '  const brand = useBrand();\n'
     '  // Explicit field-by-field rather than the prior Object.values().every()\n',
     'IntakeForm brand read'),
    (W / 'components/DiagnosticFlow.tsx',
     "        What follows draws entirely on your own perceptions of your organization.\n"
     "        That's intentional — this is a starting point, not a full picture.\n"
     "        Principal Resolution's services bring more objective data and a solution\n"
     "        roadmap next, through a separate process built for exactly that.\n",
     "        What follows draws entirely on your own perceptions of your organization.{\" \"}\n"
     "        {brand === \"hr_diagnostic\" ? <BeforeYouBeginCopyHR /> : <BeforeYouBeginCopyPR />}\n",
     'Before you begin copy'),

    # ── PrivateOutput.tsx: item G + /book/toc + engage CTA ─────────────────────
    (W / 'components/PrivateOutput.tsx',
     '"use client";\n\nimport Link from "next/link";\n',
     '"use client";\n\nimport dynamic from "next/dynamic";\n',
     'Link -> dynamic import'),
    (W / 'components/PrivateOutput.tsx',
     'import { stateIdToSlug } from "@/lib/state-slug";\n'
     'import ContextOrientation from "@/components/ContextOrientation";\n'
     'import { getResultsOrientation } from "@/data/orientation-copy";\n',
     '',
     'drop now-unused imports'),
    (W / 'components/PrivateOutput.tsx',
     'import { useBrand } from "@/components/BrandContext";\n',
     'import { useBrand } from "@/components/BrandContext";\n'
     '\n'
     '// Brand-specific pieces, code-split rather than conditionally rendered:\n'
     '// Next bundles by import graph, so PR-only strings (tier names, /book/toc,\n'
     '// the engage CTA) imported statically here would ship to hr-dx.com even\n'
     '// when never rendered. Each is its own chunk, fetched only when rendered.\n'
     'const ResultsOrientationPR = dynamic(() => import("@/components/ResultsOrientationPR"));\n'
     'const ResultsOrientationHR = dynamic(() => import("@/components/ResultsOrientationHR"));\n'
     'const StateBookLinkPR = dynamic(() => import("@/components/StateBookLinkPR"));\n'
     'const EngageCtaPR = dynamic(() => import("@/components/EngageCtaPR"));\n',
     'dynamic brand components'),
    (W / 'components/PrivateOutput.tsx',
     '        <ContextOrientation\n'
     '          variant="inline"\n'
     '          topic="output-private"\n'
     '          {...getResultsOrientation(payload.severity, payload.resolution_family)}\n'
     '        />\n',
     '        {brand === "hr_diagnostic" ? (\n'
     '          <ResultsOrientationHR topic="output-private" severity={payload.severity} />\n'
     '        ) : (\n'
     '          <ResultsOrientationPR\n'
     '            topic="output-private"\n'
     '            severity={payload.severity}\n'
     '            resolutionFamily={payload.resolution_family}\n'
     '          />\n'
     '        )}\n',
     'results orientation'),
    (W / 'components/PrivateOutput.tsx',
     '                ) : (\n'
     '                  <a\n'
     '                    href={`/book/toc#${stateIdToSlug(s.id)}`}\n'
     '                    className="font-display text-lg text-charcoal hover:underline"\n'
     '                  >\n'
     '                    {s.name}\n'
     '                  </a>\n'
     '                )}\n',
     '                ) : (\n'
     '                  <StateBookLinkPR id={s.id} name={s.name} />\n'
     '                )}\n',
     'state /book/toc link'),
    (W / 'components/PrivateOutput.tsx',
     '      {/* Block 6 — Engage CTA (Real Transaction Path, Phase 1). Links out\n'
     '          to the standalone /engage intake (name + email only, per Phase\n'
     '          1\'s e-signature-only scope) rather than carrying any diagnostic\n'
     '          result data forward — Dropbox Sign\'s hosted signing flow needs\n'
     '          nothing from this payload. enableEngage mirrors enableSharing\'s\n'
     '          suppression pattern exactly (see prop doc comment above). */}\n'
     '      {showEngageCta && (\n'
     '        <div className="mt-6 pt-6 border-t border-gray-200">\n'
     '          <p className="text-[11px] uppercase tracking-wide text-slate mb-3">\n'
     '            Ready to move on this?\n'
     '          </p>\n'
     '          <Link\n'
     '            href="/engage"\n'
     '            className="inline-block bg-charcoal text-white font-ui text-sm font-medium px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors"\n'
     '          >\n'
     '            Start the engagement →\n'
     '          </Link>\n'
     '        </div>\n'
     '      )}\n',
     '      {/* Block 6 — Engage CTA, principal_resolution only (see\n'
     '          EngageCtaPR.tsx). enableEngage mirrors enableSharing\'s\n'
     '          suppression pattern exactly (see prop doc comment above). */}\n'
     '      {showEngageCta && <EngageCtaPR />}\n',
     'engage CTA'),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    for path in NEW_FILES:
        if path.exists():
            print(f'ERROR: {path} already exists.', file=sys.stderr)
            sys.exit(1)
    hr = NEW_FILES[W / 'components/BeforeYouBeginCopyHR.tsx'] + NEW_FILES[W / 'components/ResultsOrientationHR.tsx']
    for bad in ('Principal Resolution', 'People Tactics', 'Training & Development', 'First Call', 'Executive Advisory', 'results-family-detail-pr', '/book', '/engage'):
        if bad in hr:
            print(f'ERROR: HR module contains {bad!r}.', file=sys.stderr)
            sys.exit(1)

    edited = {}
    for path, old, new, label in EDITS:
        text = edited.get(path, path.read_text(encoding='utf-8'))
        count = text.count(old)
        if count != 1:
            print(f'ERROR: {path} :: {label} anchor found {count} times, expected exactly 1.', file=sys.stderr)
            sys.exit(1)
        edited[path] = text.replace(old, new, 1)
        print(f'[{path} :: {label}] OK')

    for path, content in NEW_FILES.items():
        print(f'=== NEW {path} ===\n{content}')

    if args.dry_run:
        print('DRY RUN -- all anchors found, all edits would apply cleanly. Nothing written.')
        return

    for path, content in NEW_FILES.items():
        path.write_text(content, encoding='utf-8')
        print(f'WROTE: {path}')
    for path, text in edited.items():
        path.write_text(text, encoding='utf-8')
        print(f'WROTE (edited): {path}')


if __name__ == '__main__':
    main()
