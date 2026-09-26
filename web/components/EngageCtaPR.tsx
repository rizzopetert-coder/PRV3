"use client";

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
