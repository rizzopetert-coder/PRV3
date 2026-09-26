"use client";

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
