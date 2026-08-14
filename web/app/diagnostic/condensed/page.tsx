import CondensedDiagnosticFlow from "@/components/CondensedDiagnosticFlow";

// ---------------------------------------------------------------------------
// Category D (free condensed diagnostic), this session -- the missing front
// door found during Pete's own live verification: the backend
// (web/app/api/diagnostic/condensed) and the result screen
// (CondensedOutput.tsx) both worked, but no page existed to reach them.
// ---------------------------------------------------------------------------

export default function CondensedDiagnosticPage() {
  return (
    <div className="min-h-screen bg-paper">
      <CondensedDiagnosticFlow />
    </div>
  );
}
