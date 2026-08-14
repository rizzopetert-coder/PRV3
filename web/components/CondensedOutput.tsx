import type { CondensedOutputPayload } from "@/lib/types";
import { severityAccentTokens } from "@/components/ConstellationField";

// ---------------------------------------------------------------------------
// Category D (free condensed diagnostic), this session -- deliberately NOT
// PrivateOutput.tsx and NOT a mode flag on it. Separate rendering target
// for a separate, much smaller payload shape (CondensedOutputPayload,
// web/lib/types.ts) -- see the Decision Register for the architecture
// reasoning (Gemini round 3, this session).
//
// No ConstellationField -- Pete's resolved decision: an 8-10-question
// dimension_summary is too thin to fill the shape convincingly, and using
// it risks quietly misrepresenting an org's real profile from a fraction
// of the full diagnostic's signal. The condensed report is deliberately,
// honestly thin rather than simulating data it doesn't have.
//
// Indicators ship fully locked, zero shown -- not a partial reveal.
// get_fallback_synthesis()'s observable_indicators is hardcoded empty by
// design (engine/data/fallback_synthesis.py), so there is no real
// per-respondent indicator content to partially show; a locked section
// with explicit unlock-framing copy is honest about what's actually
// available, matching this feature's "the limitation is part of the
// pitch" design (prompts/category-d-build-scope.md, Section 1).
// ---------------------------------------------------------------------------

interface CondensedOutputProps {
  payload: CondensedOutputPayload;
}

export default function CondensedOutput({ payload }: CondensedOutputProps) {
  const accent = severityAccentTokens(payload.severity);
  const { low, high, currency } = payload.financial_range;
  const hasFinancialRange = low !== null && high !== null;

  return (
    <div className="max-w-2xl">
      {/* Block 1 -- condition header. Same visual language as
          PrivateOutput.tsx's own Block 1 (hero name + severity badge),
          deliberately not copy-pasted -- this report has no dimensional
          shape, no descriptive_prose paragraph, no headline block. */}
      <div className="pb-4">
        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
          Most prominent pattern
        </p>
        <div className="flex items-center gap-3 flex-wrap mb-3">
          <span className="font-display text-3xl font-semibold text-charcoal">
            {payload.primary_state.name}
          </span>
          <span
            className="text-[11px] rounded-md px-2 py-0.5 border"
            style={{ borderColor: accent.stroke, color: accent.text }}
          >
            {payload.severity}
          </span>
        </div>
        {payload.verdict_text && (
          <p className="text-sm leading-[1.65] text-charcoal">{payload.verdict_text}</p>
        )}
      </div>

      <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />

      {/* Block 2 -- indicators, fully locked. Not a partial reveal --
          there is no real per-respondent indicator content behind this
          (see file header). */}
      <div className="py-4">
        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
          Observable indicators
        </p>
        <div className="rounded-md border border-dashed border-gray-300 bg-gray-50 px-4 py-4">
          <p className="text-sm text-gray-500 leading-relaxed">
            All indicators locked — unlock the full diagnostic to see what&apos;s driving this
            result.
          </p>
        </div>
      </div>

      <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />

      {/* Block 3 -- financial benchmark. Null-path: the financial range
          is omitted entirely with an explicit unavailable note, never a
          broken or missing figure, when get_industry_wage() returned
          None for an unrecognized industry (Decision Register, this
          session). */}
      <div className="py-4">
        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
          Estimated cost of one departure in this pattern
        </p>
        {hasFinancialRange ? (
          <p className="text-sm text-charcoal">
            {currency === "USD" ? "$" : ""}
            {low!.toLocaleString()} – {currency === "USD" ? "$" : ""}
            {high!.toLocaleString()}{" "}
            <span className="text-gray-400">
              (roughly 50–75% of one departing employee&apos;s estimated salary)
            </span>
          </p>
        ) : (
          <p className="text-sm text-gray-400">
            A benchmark figure isn&apos;t available for the industry provided.
          </p>
        )}
      </div>

      <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />

      {/* Block 4 -- resolution family + CTA. UPDATE, this session (Pete's own
          live production test caught this): resolution_family used to be
          empty in multi-state mode (the common case -- ~100% of real
          profiles) because run_condensed_engine() read it from
          OutputPackage.private, only ever populated in single-state mode.
          FIXED in engine/main.py -- now sourced from the lead
          QualifiedState directly, which works in both routing modes. This
          badge renders unconditionally (still no empty-state copy), but
          the value behind it should now be real in practice, not
          structurally blank. PrivateOutput.tsx's own separate copy of
          this same gap (engine/contract.py's assemble_output(), still
          reading output_package.private the old way) is untouched --
          that's the full diagnostic's own code path, out of scope here,
          and remains a real, open, shared-engine-level item if ever
          wanted there. */}
      <div className="py-4 space-y-3">
        <div className="space-y-1">
          <p className="text-[11px] uppercase tracking-wide text-gray-400">
            Resolution pathway
          </p>
          <p className="text-[13px] font-medium text-charcoal">{payload.resolution_family}</p>
        </div>
        <a
          href="/diagnostic"
          className="inline-block font-ui text-sm font-medium text-charcoal border border-charcoal rounded-md px-4 py-2 hover:bg-charcoal hover:text-white transition-colors"
        >
          Get your full diagnostic
        </a>
      </div>
    </div>
  );
}
