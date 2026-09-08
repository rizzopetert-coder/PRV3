"use client";

import { useState } from "react";
import type { EnginePayload } from "@/lib/engine-client";
import {
  HeadcountStepper,
  INDUSTRY_OPTIONS,
  JURISDICTION_OPTIONS,
} from "@/components/DiagnosticFlow";

// Source of truth is engine/friction_tax.py's ORG_TYPE_SCALARS keys --
// verified verbatim against that table (2026-09-08), not assumed.
// Keep in sync manually if that table's keys ever change; also mirrors
// engine/data/intake.py's INTAKE_FIELDS["org_type"] list.
const ORG_TYPE_OPTIONS = [
  "Founder-led",
  "PE or VC-backed",
  "Privately held professional leadership",
  "Nonprofit",
  "Publicly traded",
  "Government",
];

interface SelfSelectIntakeModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (intake: EnginePayload["intake"]) => void;
}

// Collects the four fields compute_friction_tax() and
// compute_legal_compliance_exposure() actually need (headcount,
// industry, org_type, jurisdictions) before the self-select flow
// invokes /api/result -- previously sent entirely blank
// (app/diagnostic/page.tsx's handleTakeDiagnostic()), which this
// session's earlier engine-side fix made degrade cleanly rather than
// 500, but still meant no self-select result was ever priced.
// significantEvents/principalRole stay at their existing blank/locked
// defaults -- neither consuming function needs them, confirmed this
// session -- out of scope for this modal.
export default function SelfSelectIntakeModal({
  open,
  onClose,
  onSubmit,
}: SelfSelectIntakeModalProps) {
  const [headcount, setHeadcount] = useState<number | "">("");
  const [industry, setIndustry] = useState("");
  const [orgType, setOrgType] = useState("");
  const [jurisdictions, setJurisdictions] = useState<string[]>([]);

  if (!open) return null;

  function toggleJurisdiction(code: string) {
    setJurisdictions((prev) =>
      prev.includes(code) ? prev.filter((j) => j !== code) : [...prev, code],
    );
  }

  const isComplete =
    headcount !== "" && industry !== "" && orgType !== "" && jurisdictions.length > 0;

  function handleSubmit() {
    // Strict completeness gate -- same standard as DiagnosticFlow's
    // IntakeForm.isComplete. The two consuming engine functions
    // already degrade cleanly on missing input (this session's
    // earlier fix), but this modal's entire purpose is to close that
    // gap, not leave a partial-submission escape hatch open. Checked
    // inline here (not via the isComplete alias above) so TypeScript
    // narrows headcount: number | "" to a definite number below.
    if (headcount === "" || industry === "" || orgType === "" || jurisdictions.length === 0) {
      return;
    }
    // headcount is a real number here, narrowed by the check above --
    // asserted explicitly, not just relied on implicitly. A
    // stringified headcount would silently degrade to
    // friction_tax_estimate: null and NOT_APPLICABLE coverage rather
    // than erroring (resolve_headcount_bucket()'s
    // isinstance(headcount, (int, float)) guard, engine/friction_tax.py,
    // can't tell a valid numeric string from garbage) -- exactly the
    // failure mode this modal exists to close, so it must not slip
    // back in here.
    onSubmit({
      headcount,
      industry,
      orgType,
      jurisdictions,
      significantEvents: [],
      principalRole: "",
    });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-md max-h-[90vh] overflow-y-auto rounded-xl bg-white p-6">
        <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">
          Before you see what this means
        </p>
        <h2 className="font-display text-xl text-charcoal mb-6">
          A few things about your organization.
        </h2>

        <HeadcountStepper value={headcount} onChange={setHeadcount} />

        <div className="mb-5">
          <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
            Industry
          </label>
          <select
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
          >
            <option value="">Select…</option>
            {INDUSTRY_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>

        <div className="mb-5">
          <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
            Organization type
          </label>
          <select
            value={orgType}
            onChange={(e) => setOrgType(e.target.value)}
            className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
          >
            <option value="">Select…</option>
            {ORG_TYPE_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>

        <div className="mb-6">
          <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
            Jurisdictions (select all that apply)
          </label>
          <div className="max-h-40 overflow-y-auto grid grid-cols-4 gap-1.5 border border-gray-200 rounded-lg px-3 py-3 bg-white">
            {JURISDICTION_OPTIONS.map((code) => (
              <label
                key={code}
                className="flex items-center gap-1.5 font-ui text-sm text-charcoal cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={jurisdictions.includes(code)}
                  onChange={() => toggleJurisdiction(code)}
                  className="shrink-0"
                />
                <span>{code}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 border border-charcoal text-charcoal font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!isComplete}
            className="flex-1 bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
