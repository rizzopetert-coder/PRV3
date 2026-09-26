"use client";

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
