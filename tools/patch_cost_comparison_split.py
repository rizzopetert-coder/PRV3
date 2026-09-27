"""
Cost comparison: show the two inaction figures separately with their
timeframes (Pete, 2026-09-27). The engine's inaction_cost_low/high adds the
friction tax (annual, payroll-based) to legal exposure (one-time, per claim),
so the "combined" figure mixed two kinds of number. The card now shows:
  - Friction tax, recurring every year  (payload.friction_tax_estimate)
  - Legal exposure, one-time if a claim arises  (legal_tail_risk_exposure,
    only when priced)
straight from the figures already in the payload. The engine's summed
inaction_cost_* fields stay in the payload but are no longer rendered.

Usage: python tools/patch_cost_comparison_split.py --dry-run | --write
"""
import argparse
import pathlib
import sys

RD = pathlib.Path('web/components/ReportDetails.tsx')
PO = pathlib.Path('web/components/PrivateOutput.tsx')

START = 'export function CostComparison({\n'
END = 'const AXIS_NAMES: Record<AssetAxis, string> = {\n'
NEW_FN = '''function rangeText(low: number, high: number): string {
  return low === high ? usd(low) : `${usd(low)} – ${usd(high)}`;
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

'''

RD_IMPORT_OLD = '  EvidenceReceipt,\n  ServiceCostComparison,\n'
RD_IMPORT_NEW = ('  EvidenceReceipt,\n  FrictionTaxEstimate,\n  LegalTailRiskExposure,\n'
                 '  ServiceCostComparison,\n')
PO_OLD = ('      <CostComparison\n'
          '        comparison={payload.service_cost_comparison}\n'
          '        fallbackServiceName={payload.resolution_family}\n'
          '      />\n')
PO_NEW = ('      <CostComparison\n'
          '        comparison={payload.service_cost_comparison}\n'
          '        friction={payload.friction_tax_estimate}\n'
          '        legal={payload.legal_tail_risk_exposure}\n'
          '        fallbackServiceName={payload.resolution_family}\n'
          '      />\n')


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    a = ap.parse_args()
    rd = RD.read_text(encoding='utf-8')
    for anchor in (START, END, RD_IMPORT_OLD):
        if rd.count(anchor) != 1:
            print(f'ERROR anchor x{rd.count(anchor)}: {anchor[:40]!r}', file=sys.stderr)
            sys.exit(1)
    s, e = rd.index(START), rd.index(END)
    rd = rd[:s] + NEW_FN + rd[e:]
    rd = rd.replace(RD_IMPORT_OLD, RD_IMPORT_NEW, 1)
    print(f'[{RD} :: CostComparison split + imports] OK')
    po = PO.read_text(encoding='utf-8')
    if po.count(PO_OLD) != 1:
        print('ERROR call site', file=sys.stderr)
        sys.exit(1)
    po = po.replace(PO_OLD, PO_NEW, 1)
    print(f'[{PO} :: call site] OK')
    if a.dry_run:
        print('DRY RUN -- nothing written.')
        return
    RD.write_text(rd, encoding='utf-8')
    PO.write_text(po, encoding='utf-8')
    print('WROTE')


if __name__ == '__main__':
    main()
