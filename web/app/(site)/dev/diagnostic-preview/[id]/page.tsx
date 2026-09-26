import { notFound } from "next/navigation";
import { getDevPreview, isPreviewEnvironment } from "@/lib/dev-diagnostic-preview";
import PrivateOutput from "@/components/PrivateOutput";

// ---------------------------------------------------------------------------
// DEV / TEST ONLY -- Preview environment exclusively.
//
// Renders a completed diagnostic result produced by
// tools/diagnostic_fast_forward.py (Mode 1) through the same <PrivateOutput>
// component a real respondent sees -- this is never a real respondent's
// data, only synthetic state/severity-targeted output. Not reachable in
// Production: notFound() fires immediately, before Redis is ever touched.
//
// Server Component, direct Redis read (no intermediate GET API route) --
// this page has no other consumer, so a dedicated fetch-from-own-route hop
// (the pattern /share/[id]/page.tsx uses) would add a file without adding
// value here.
//
// Not the same tool as /dev/diagnostic-fixture (web/app/dev/diagnostic-fixture),
// intentionally: this page only ever renders a REAL engine-computed result
// (via tools/diagnostic_fast_forward.py), which is the entire reason it's
// worth looking at. /dev/diagnostic-fixture renders hand-picked/arbitrary
// values instead, for fast UI/interaction iteration, with no engine and no
// Redis involved. Keep both; neither should be merged into or replace the
// other.
// ---------------------------------------------------------------------------

interface DevPreviewPageProps {
  params: Promise<{ id: string }>;
}

export default async function DevDiagnosticPreviewPage({ params }: DevPreviewPageProps) {
  if (!isPreviewEnvironment()) {
    notFound();
  }

  const { id } = await params;
  const payload = await getDevPreview(id);
  if (!payload) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-paper px-6 py-10 md:px-10 md:py-14">
      <div className="max-w-2xl mx-auto mb-8 rounded-lg border-2 border-dashed border-amber-400 bg-amber-50 px-4 py-3">
        <p className="font-ui text-sm font-semibold text-amber-900">
          DEV / TEST ONLY
        </p>
        <p className="font-ui text-xs text-amber-800 mt-1">
          Synthetic result from tools/diagnostic_fast_forward.py — not a real
          respondent&apos;s diagnosis. Preview environment only.
        </p>
      </div>
      <div className="max-w-2xl mx-auto">
        <PrivateOutput
          payload={payload}
          selectedStateIds={[
            payload.primary_state.id,
            ...payload.secondary_states.map((s) => s.id),
          ]}
          intake={{
            headcount: "",
            industry: "",
            orgType: "",
            jurisdictions: [],
            significantEvents: [],
            principalRole: "",
          }}
          enableSharing={false}
          enableEngage={false}
        />
      </div>
    </main>
  );
}
