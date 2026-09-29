"use client";

import type {
  AssetAxis,
  AssetEvidence,
  EvidenceReceipt,
  FrictionTaxEstimate,
  LegalTailRiskExposure,
  ServiceCostComparison,
  TacticalFinding,
  TacticalSectionResult,
} from "@/lib/types";
import { formatUsdRange } from "@/lib/output-text";

// Phase 3 report blocks (Pete, 2026-09-27). Brand-neutral: every brand-
// specific value (service names, referral chips) arrives as data.


function joinWords(items: string[]): string {
  if (items.length <= 1) return items.join("");
  if (items.length === 2) return `${items[0]} and ${items[1]}`;
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
}

export function ExecutiveSummary({ text }: { text?: string }) {
  if (!text) return null;
  return (
    <div className="pb-4">
      <p className="text-[11px] uppercase tracking-wide text-slate mb-2">Executive summary</p>
      <p className="text-base leading-relaxed text-charcoal">{text}</p>
    </div>
  );
}

export function EvidenceReceipts({ receipts }: { receipts?: EvidenceReceipt[] }) {
  if (!receipts || receipts.length === 0) return null;
  return (
    <details className="mt-3">
      <summary className="text-[12px] text-slate cursor-pointer hover:underline">
        How this figure was calculated
      </summary>
      <ol className="mt-2 space-y-2.5 border-l border-gray-200 pl-3">
        {receipts.map((r, i) => (
          <li key={i} className="text-[12px] leading-relaxed">
            <p className="text-[10px] uppercase tracking-wide text-slate">{r.category}</p>
            <p className="text-charcoal">{r.rationale}</p>
            {r.triggering_answer && (
              <p className="text-slate">Based on your answers: {r.triggering_answer}</p>
            )}
          </li>
        ))}
      </ol>
    </details>
  );
}

// Dollars to the nearest $1,000 (A1), the shared report formatter.
function rangeText(low: number, high: number): string {
  return formatUsdRange(low, high);
}

// The two inaction figures stay separate, each with its timeframe: the
// friction tax is annual (payroll-based), legal exposure is one-time per
// claim. Adding them would mix two kinds of number.
export function CostComparison({
  comparison,
  friction,
  legal,
  fallbackServiceName,
}: {
  comparison?: ServiceCostComparison;
  friction: FrictionTaxEstimate | null;
  legal: LegalTailRiskExposure | null;
  fallbackServiceName: string;
}) {
  if (!comparison) return null;
  const legalPriced = legal !== null && legal.low !== null && legal.high !== null;
  if (!friction && !legalPriced) return null;
  const service = comparison.target_service_name || fallbackServiceName;
  const priced =
    comparison.service_estimate_low !== null && comparison.service_estimate_high !== null;
  return (
    <div className="py-4">
      <p className="text-[11px] uppercase tracking-wide text-slate mb-3">Cost comparison</p>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-md border border-gray-200 px-4 py-3 space-y-2">
          <p className="text-[11px] text-slate">If these conditions go unaddressed</p>
          {friction && (
            <div>
              <p className="text-sm font-medium text-charcoal">{rangeText(friction.low, friction.high)}</p>
              <p className="text-[11px] text-slate">Friction tax, recurring every year</p>
            </div>
          )}
          {legalPriced && (
            <div>
              <p className="text-sm font-medium text-charcoal">{rangeText(legal!.low!, legal!.high!)}</p>
              <p className="text-[11px] text-slate">Legal exposure, one-time if a claim arises</p>
            </div>
          )}
        </div>
        <div className="rounded-md border border-gray-200 px-4 py-3">
          {service && <p className="text-[11px] text-slate mb-1">{service}</p>}
          {priced ? (
            <p className="text-sm font-medium text-charcoal">
              {rangeText(comparison.service_estimate_low!, comparison.service_estimate_high!)}
            </p>
          ) : (
            <p className="text-sm font-medium text-charcoal">Ask for pricing</p>
          )}
          <p className="text-[11px] text-slate mt-1">
            {priced && comparison.pricing_model_note
              ? comparison.pricing_model_note
              : "Scoped to what this diagnostic found."}
          </p>
        </div>
      </div>
    </div>
  );
}

const AXIS_NAMES: Record<AssetAxis, string> = {
  aptitude: "Aptitude",
  authority: "Authority",
  alliance: "Alliance",
  attitude: "Attitude",
};

export function AssetStrength({ evidence }: { evidence?: AssetEvidence }) {
  if (!evidence) return null;
  const axes = Object.keys(AXIS_NAMES) as AssetAxis[];
  const max = Math.max(...axes.map((a) => evidence.net_scores[a] ?? 0));
  if (max <= 0) return null;
  const strongest = evidence.strongest_axes.map((a) => AXIS_NAMES[a]);
  return (
    <div className="mt-3">
      <p className="text-[11px] uppercase tracking-wide text-slate mb-1.5">Where strength shows up</p>
      <p className="text-[13px] text-charcoal mb-2">
        Your answers show the most strength in {joinWords(strongest)}.
      </p>
      <ul className="space-y-1.5 max-w-sm">
        {axes.map((a) => (
          <li key={a} className="flex items-center gap-2">
            <span className="w-20 shrink-0 text-[11px] text-slate">{AXIS_NAMES[a]}</span>
            <div className="flex-1 h-1 rounded-full bg-gray-100">
              <div
                className="h-1 rounded-full"
                style={{
                  width: `${((evidence.net_scores[a] ?? 0) / max) * 100}%`,
                  backgroundColor: "var(--color-slate)",
                }}
              />
            </div>
          </li>
        ))}
      </ul>
      {evidence.contributing_signals.length > 0 && (
        <ul className="mt-2 space-y-1">
          {evidence.contributing_signals.map((s, i) => (
            <li key={i} className="text-[12px] text-charcoal leading-relaxed">
              {s.observation_text}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function AnswerList({
  section,
  flagged,
}: {
  section: TacticalSectionResult;
  flagged: Map<string, "minor" | "severe">;
}) {
  return (
    <ul className="space-y-3">
      {section.answers.map((a) => {
        const gap = flagged.get(a.question_id);
        return (
          <li key={a.question_id}>
            <p className="text-sm font-medium text-charcoal">{a.question_text}</p>
            <p className="text-sm text-slate">
              {a.selected_option_text}
              {gap && (
                <span className="ml-2 text-[10px] uppercase tracking-wide text-charcoal">
                  {gap === "severe" ? "Significant gap or unknown" : "Minor gap"}
                </span>
              )}
            </p>
          </li>
        );
      })}
    </ul>
  );
}

export function TacticalReview({
  sections,
  findings,
}: {
  sections: TacticalSectionResult[];
  findings?: TacticalFinding[];
}) {
  if (sections.length === 0) return null;
  const byId = new Map((findings ?? []).map((f) => [f.section_id, f] as const));
  return (
    <div className="mt-8 pt-8 border-t border-gray-200">
      <p className="text-[11px] uppercase tracking-wide text-slate mb-4">
        Tactical &amp; compliance review
      </p>
      <div className="space-y-6">
        {sections.map((section) => {
          const f = byId.get(section.question_set_id);
          const flagged = new Map(
            (f?.flagged_items ?? []).map((i) => [i.question_id, i.severity] as const),
          );
          return (
            <div key={section.question_set_id}>
              {f && <p className="font-display text-lg text-charcoal mb-1">{f.section_name}</p>}
              <div className="flex flex-wrap gap-2 mb-2">
                {section.referral.map((r) => (
                  <span
                    key={r}
                    className="text-[10px] uppercase tracking-wide bg-gray-100 text-charcoal rounded-full px-2 py-0.5"
                  >
                    {r}
                  </span>
                ))}
              </div>
              {f ? (
                <>
                  <p className="text-[12px] text-slate mb-1">
                    {f.flagged_count === 0
                      ? `No gaps in these ${f.total_count} answers.`
                      : `${f.flagged_count} of ${f.total_count} answers show a gap.`}
                  </p>
                  {f.synthesis_text && (
                    <p className="text-sm text-charcoal leading-relaxed mb-2">{f.synthesis_text}</p>
                  )}
                  <details>
                    <summary className="text-[12px] text-slate cursor-pointer hover:underline">
                      Your answers
                    </summary>
                    <div className="mt-2">
                      <AnswerList section={section} flagged={flagged} />
                    </div>
                  </details>
                </>
              ) : (
                <AnswerList section={section} flagged={flagged} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
