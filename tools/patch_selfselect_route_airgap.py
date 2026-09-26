"""
Physical route airgap for Path B (self-select), Gemini-approved Option 2.

Problem (found empirically 2026-09-26, local production build): app/diagnostic/
page.tsx statically imported @/data/taxonomy (plus AssemblyPanel,
SignatureCard, StateDrawer, all taxonomy importers) for its in-page
self-select branch. hr-dx.com hides that branch in the UI, but Next bundles
by import graph, not by which branch renders -- so hr-dx /diagnostic loaded a
JS chunk containing PRV3's full state taxonomy (state names, signature
interpretations, self-select copy), exactly what middleware's /api/result +
/api/interpret block exists to prevent.

Fix: self-select moves out of app/diagnostic/page.tsx into its own route,
app/(site)/diagnostic/self-select/page.tsx (URL /diagnostic/self-select).
Inside (site), so on principalresolution.com it renders with the PRV3 chrome
like every other PRV3 page. Not in middleware.ts's hr_diagnostic allowlist,
so hr-dx.com 404s it before Next's router runs -- same gating as before,
now physical rather than UI-only. /api/result and /api/interpret stay
blocked on hr-dx exactly as before (middleware untouched).

app/diagnostic/page.tsx keeps: the gate, the ?session= resume shortcut,
and Path 1 (DiagnosticFlow). The gate's self-select button becomes a Link
to /diagnostic/self-select, still hidden on hr_diagnostic via useBrand().
No import path, direct or transitive, to @/data/taxonomy remains -- verified
by import-graph trace and a chunk grep after build, not assumed.

SelfSelectionInterface and the CONVERSATION_MAILTO_HREF block are moved
byte-for-byte (sliced from the original file by anchor, not retyped).

Usage:
    python tools/patch_selfselect_route_airgap.py --dry-run
    python tools/patch_selfselect_route_airgap.py --write
"""
import argparse
import pathlib
import sys

DIAG_PAGE = pathlib.Path('web/app/diagnostic/page.tsx')
SELF_SELECT_PAGE = pathlib.Path('web/app/(site)/diagnostic/self-select/page.tsx')

MAILTO_START = '// Phase 4\'s "Start a conversation" CTA'
MAILTO_END = 'type DiagnosticPath = '
IFACE_START = '// ── Self-Selection Interface'
IFACE_END = '// ── Main export'

NEW_DIAG_PAGE = '''"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useBrand } from "@/components/BrandContext";
import { useSearchParams } from "next/navigation";
import DiagnosticFlow from "@/components/DiagnosticFlow";

// Path B (self-select) lives at app/(site)/diagnostic/self-select/page.tsx,
// not here. It used to be an in-page branch of this file, which meant this
// route statically imported @/data/taxonomy -- and Next bundles by import
// graph, not by which branch renders, so hr-dx.com's /diagnostic shipped
// PRV3's full state taxonomy in its JS even with the branch hidden. This
// file must never import @/data/taxonomy, or any component that does
// (AssemblyPanel, SignatureCard, StateDrawer), directly or transitively.

// ── Gate ──────────────────────────────────────────────────────────────────────

function DiagnosticGate({ onChooseDiagnostic }: { onChooseDiagnostic: () => void }) {
  // hr_diagnostic: self-select (Path B) is hidden here and walled off at the
  // routing layer -- /diagnostic/self-select, /api/result and /api/interpret
  // all 404 on that hostname (see middleware.ts) since Path B exposes PRV3's
  // full 58-state taxonomy, which this hostname must never reveal.
  const brand = useBrand();
  const diagnosticOnly = brand === "hr_diagnostic";

  return (
    <div className="max-w-2xl mx-auto px-6 py-16">
      <div
        className={
          diagnosticOnly
            ? "grid grid-cols-1 gap-4"
            : "grid grid-cols-1 md:grid-cols-2 gap-4"
        }
      >
        <button
          onClick={onChooseDiagnostic}
          className="text-left p-6 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-all duration-300 animate-fade-up"
        >
          <h2 className="font-display text-lg font-semibold text-charcoal mb-2">
            Take the diagnostic.
          </h2>
          <p className="font-ui text-sm text-gray-600">
            Answer questions. Get a complete read of what your organization is
            carrying.
          </p>
        </button>
        {!diagnosticOnly && (
          <Link
            href="/diagnostic/self-select"
            className="block text-left p-6 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-all duration-300 animate-fade-up"
          >
            <h2 className="font-display text-lg font-semibold text-charcoal mb-2">
              Start by recognizing.
            </h2>
            <p className="font-ui text-sm text-gray-600">
              Select what looks familiar. See what it means together.
            </p>
          </Link>
        )}
      </div>
    </div>
  );
}

// ── Main export ───────────────────────────────────────────────────────────────

// DiagnosticPage is a thin Suspense wrapper -- useSearchParams() (below, for
// the ?session= resume link) requires a Suspense boundary so a production
// static prerender of this route doesn't fail the build. Has no effect on
// the no-param path's rendered output.
export default function DiagnosticPage() {
  return (
    <Suspense fallback={null}>
      <DiagnosticPageInner />
    </Suspense>
  );
}

function DiagnosticPageInner() {
  // ?session=<id>, if present, skips the DiagnosticGate entirely and goes
  // straight to DiagnosticFlow (which itself resumes that session -- see
  // DiagnosticFlow.tsx) -- true "skip straight to the question view," not
  // just DiagnosticFlow resuming after a manual gate click. Lazy useState
  // initializer so this is decided once, on first render, from the URL
  // actually requested.
  const searchParams = useSearchParams();
  const [started, setStarted] = useState<boolean>(() =>
    Boolean(searchParams.get("session"))
  );

  if (!started) {
    return (
      <div className="min-h-screen bg-paper transition-opacity duration-300">
        <DiagnosticGate onChooseDiagnostic={() => setStarted(true)} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-paper">
      <DiagnosticFlow />
    </div>
  );
}
'''

SELF_SELECT_HEADER = '''"use client";

import { useState } from "react";
import Link from "next/link";
import {
  signatures,
  states,
  getDominantSignature,
  uiCopy,
} from "@/data/taxonomy";
import type { State } from "@/data/taxonomy";
import type { PrivateOutputPayload } from "@/lib/types";
import type { EnginePayload } from "@/lib/engine-client";
import { buildMailtoLink } from "@/lib/contact";
import SignatureCard from "@/components/SignatureCard";
import AssemblyPanel from "@/components/AssemblyPanel";
import PrivateOutput from "@/components/PrivateOutput";
import { StateDrawer } from "@/components/StateDrawer";
import { SelfSelectionProvider, useSelfSelection } from "@/context/SelfSelectionContext";
import SelfSelectIntakeModal from "@/components/SelfSelectIntakeModal";

// Path B (self-select), relocated from app/diagnostic/page.tsx's in-page
// branch into its own route inside (site) -- a physical airgap, not a UI
// one. This is the only diagnostic route allowed to import @/data/taxonomy.
// Reached from /diagnostic's gate ("Start by recognizing.") on
// principalresolution.com only: middleware.ts 404s /diagnostic/self-select
// on hr-dx.com (not in its allowlist), alongside the /api/result and
// /api/interpret blocks this flow depends on. SelfSelectionInterface below
// is moved verbatim from the original file.

'''

SELF_SELECT_FOOTER = '''// ── Main export ───────────────────────────────────────────────────────────────

export default function SelfSelectPage() {
  // Starts at Phase 1 -- the same state the original in-page gate click
  // produced ({ path: "self-select", currentPhase: 1 }).
  const [currentPhase, setCurrentPhase] = useState(1);

  return (
    <SelfSelectionProvider>
      <SelfSelectionInterface
        currentPhase={currentPhase}
        onPhaseAdvance={setCurrentPhase}
      />
    </SelfSelectionProvider>
  );
}
'''


def slice_between(text: str, start: str, end: str, label: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        print(f'ERROR: {label} anchors not unique (start={text.count(start)}, end={text.count(end)}).', file=sys.stderr)
        sys.exit(1)
    a, b = text.index(start), text.index(end)
    if a >= b:
        print(f'ERROR: {label} anchors out of order.', file=sys.stderr)
        sys.exit(1)
    return text[a:b]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    if SELF_SELECT_PAGE.exists():
        print(f'ERROR: {SELF_SELECT_PAGE} already exists.', file=sys.stderr)
        sys.exit(1)

    original = DIAG_PAGE.read_text(encoding='utf-8')
    mailto_block = slice_between(original, MAILTO_START, MAILTO_END, 'mailto block')
    iface_block = slice_between(original, IFACE_START, IFACE_END, 'SelfSelectionInterface block')

    self_select = SELF_SELECT_HEADER + mailto_block + iface_block + SELF_SELECT_FOOTER

    print(f'=== NEW {SELF_SELECT_PAGE} ===\n{self_select}')
    print(f'=== OVERWRITE {DIAG_PAGE} ===\n{NEW_DIAG_PAGE}')

    for bad in ('@/data/taxonomy', 'AssemblyPanel', 'SignatureCard', 'StateDrawer', 'SelfSelection'):
        if bad in NEW_DIAG_PAGE.split('// ── Gate')[1]:
            print(f'ERROR: new {DIAG_PAGE} code still references {bad}.', file=sys.stderr)
            sys.exit(1)

    if args.dry_run:
        print('DRY RUN -- anchors found, blocks sliced cleanly. Nothing written.')
        return

    SELF_SELECT_PAGE.parent.mkdir(parents=True, exist_ok=True)
    SELF_SELECT_PAGE.write_text(self_select, encoding='utf-8')
    print(f'WROTE: {SELF_SELECT_PAGE}')
    DIAG_PAGE.write_text(NEW_DIAG_PAGE, encoding='utf-8')
    print(f'WROTE (overwrite): {DIAG_PAGE}')


if __name__ == '__main__':
    main()
