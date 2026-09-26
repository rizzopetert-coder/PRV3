import { notFound } from "next/navigation";
import { isPreviewEnvironment } from "@/lib/dev-diagnostic-preview";
import DiagnosticFixturePicker from "@/components/DiagnosticFixturePicker";

// ---------------------------------------------------------------------------
// DEV / TEST ONLY -- not reachable in Production.
//
// A picker UI that constructs a synthetic PrivateOutput payload from a
// handful of controls (severity tier, primary/secondary states, dimension
// weights) and renders <PrivateOutput> directly -- no question flow, no
// session store, no engine call, no Redis write of any kind. Built to
// replace repeated manual click-throughs of all 42 questions when testing
// PrivateOutput/ConstellationField visual and interaction changes (same
// category as tools/diagnostic_question_audit.py -- a real, durable
// internal tool, not a one-off).
//
// Reuses isPreviewEnvironment() (web/lib/dev-diagnostic-preview.ts) --
// the exact same guard the existing /dev/diagnostic-preview route already
// uses, already proven correct: excludes real Production (VERCEL_ENV ===
// "production") and nothing else, so this works from local `next dev`
// (VERCEL_ENV unset there) despite this project having no Preview
// deployment to test against otherwise.
//
// Not the same tool as /dev/diagnostic-preview (web/app/dev/diagnostic-preview),
// intentionally: that route renders a REAL engine-computed result (fed by
// tools/diagnostic_fast_forward.py driving a real session), which is the
// entire reason it's worth looking at -- provenance is the point. This
// route is the opposite by design: arbitrary/hand-picked values, no engine,
// no Redis (producer and consumer are the same browser tab here), built for
// fast rendering/interaction iteration rather than engine-correctness
// verification. Keep both; neither should be merged into or replace the
// other.
// ---------------------------------------------------------------------------

export default function DiagnosticFixturePage() {
  if (!isPreviewEnvironment()) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-paper px-6 py-10 md:px-10 md:py-14">
      <div className="max-w-4xl mx-auto mb-8 rounded-lg border-2 border-dashed border-amber-400 bg-amber-50 px-4 py-3">
        <p className="font-ui text-sm font-semibold text-amber-900">
          DEV / TEST ONLY
        </p>
        <p className="font-ui text-xs text-amber-800 mt-1">
          Synthetic PrivateOutput fixture -- not a real respondent&apos;s
          diagnosis, never touches Redis, the engine, or the session store.
          Not reachable in Production.
        </p>
      </div>
      <DiagnosticFixturePicker />
    </main>
  );
}
