"""
web/components/PrivateOutput.tsx: add Block 4d -- legal_tail_risk_exposure
UI rendering. Placed after Block 4c (Severity across conditions), before
Block 5 (ShareButton). Whole block omitted when legal_tail_risk_exposure
is null, same idiom as every other optional block in this component.

Design per Pete's spec (architecture cleared by Gemini):
  - Dollar range only rendered when low !== null (never "$null-$null").
  - coverage_basis-driven caveat (federal_baseline/mixed) only applies
    when low !== null -- coverage_basis is meaningless without a priced
    range. state_specific carries no extra caveat beyond the standing
    `caveat` field text. Copy kept qualitative -- no specific
    employee-count figure cited (a Gemini-proposed "1-4 employees"
    figure did not check out against STATE_COVERAGE_THRESHOLDS, whose
    real CONFIRMED range is 1-12 employees; not carried into this copy).
  - has_partial_jurisdictions renders a secondary, visually lighter
    caveat under whichever primary caveat applies -- same visual tier
    as Block 4c's existing "short bar at Emerging" footnote.
  - unpriced_state_ids resolved to names via the existing stateNameById
    map (never raw state_ids); the PRICED/QUALITATIVE_ONLY/
    DATA_INTEGRITY_GAP distinction is never surfaced to the user.
  - Band gets typographic differentiation only (font-weight/size), no
    color ramp -- confirmed against ConstellationField.tsx that
    --color-rust is reserved for genuine Endemic severity signaling
    and must not be reused here.

Four anchored edits in one file, applied atomically (all four must
match or nothing is written):
  1. Import line -- add LegalTailRiskBand.
  2. New LEGAL_BAND_WEIGHT const + joinNames() helper, before Rule().
  3. New derived-values block, before the component's `return (`.
  4. New Block 4d JSX, before the Block 5 comment.

Usage:
    python tools/patch_legal_ui_block4d.py --dry-run
    python tools/patch_legal_ui_block4d.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/components/PrivateOutput.tsx')

EDIT_1_OLD = (
    'import type { PrivateOutputPayload, SeverityTier, StateRef } from "@/lib/types";'
)
EDIT_1_NEW = (
    'import type { PrivateOutputPayload, SeverityTier, StateRef, LegalTailRiskBand } from "@/lib/types";'
)

EDIT_2_OLD = '''function Rule() {
  return (
    <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />
  );
}'''

EDIT_2_NEW = '''// Legal/Compliance tail-risk exposure -- Block 4d. Typographic
// differentiation only (font-weight/size) by band, no color ramp --
// --color-rust is reserved for genuine Endemic severity signaling
// (ConstellationField.tsx, severityAccentTokens()) and must never be
// reused here. band is guaranteed non-null whenever low is non-null
// (engine/friction_tax.py's _legal_exposure_band() returns null only
// when low is null) -- Record typed on the non-null union for that
// reason, with a defensive fallback at the render call site.
const LEGAL_BAND_WEIGHT: Record<LegalTailRiskBand, string> = {
  Minor: "font-normal",
  Moderate: "font-medium",
  Elevated: "font-semibold",
  Significant: "font-semibold text-sm",
};

// Oxford-comma join for unpriced_state_ids names -- the only inline
// text-list formatting need in this component (observable indicators
// render as a bullet list, not inline text).
function joinNames(names: string[]): string {
  if (names.length === 0) return "";
  if (names.length === 1) return names[0];
  if (names.length === 2) return `${names[0]} and ${names[1]}`;
  return `${names.slice(0, -1).join(", ")}, and ${names[names.length - 1]}`;
}

function Rule() {
  return (
    <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />
  );
}'''

EDIT_3_OLD = '''  const stateNameById = new Map<string, string>([
    [payload.primary_state.id, payload.primary_state.name],
    ...payload.secondary_states.map((s): [string, string] => [s.id, s.name]),
  ]);

  return ('''

EDIT_3_NEW = '''  const stateNameById = new Map<string, string>([
    [payload.primary_state.id, payload.primary_state.name],
    ...payload.secondary_states.map((s): [string, string] => [s.id, s.name]),
  ]);

  // Block 4d -- Legal/Compliance tail-risk exposure derived values.
  // coverage_basis/has_partial_jurisdictions caveats only apply when a
  // priced range exists (legal.low !== null) -- coverage_basis is
  // meaningless without one, per the spec this block was built from.
  const legal = payload.legal_tail_risk_exposure;
  const legalHasPrice = legal !== null && legal.low !== null && legal.high !== null;
  const legalCoverageCaveat =
    legalHasPrice && legal!.coverage_basis === "federal_baseline"
      ? "This range applies a federal coverage threshold, since no confirmed state-specific threshold applied to the jurisdictions on file. Actual state law in those jurisdictions could set a materially lower bar than what's reflected here."
      : legalHasPrice && legal!.coverage_basis === "mixed"
      ? "This range blends a confirmed state-specific threshold with a federal coverage threshold used where no confirmed state-specific one applied. In the jurisdictions relying on the federal threshold, actual state law could set a materially lower bar than what's reflected here."
      : null;
  const unpricedStateNames = legal
    ? legal.unpriced_state_ids.map((id) => stateNameById.get(id) ?? id)
    : [];

  return ('''

EDIT_4_OLD = '''      {/* Block 5 — ShareButton */}'''

EDIT_4_NEW = '''      {/* Block 4d — Legal/Compliance tail-risk exposure (Addendum 11).
          Omitted entirely when legal_tail_risk_exposure is null, same
          idiom as every other optional block in this component.
          coverage_basis/has_partial_jurisdictions caveats only apply
          when a priced range exists (low !== null) -- coverage_basis
          is meaningless without one. Band gets typographic
          differentiation only via LEGAL_BAND_WEIGHT -- see that
          const's own comment for why --color-rust is off-limits here.
          unpriced_state_ids resolved to names via stateNameById
          (Block 4c's own map) -- never rendered as raw state_ids, and
          the PRICED/QUALITATIVE_ONLY/DATA_INTEGRITY_GAP distinction
          behind them is never surfaced to the user. */}
      {legal && (
        <div className="py-4">
          <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
            Legal/Compliance exposure
          </p>

          {legalHasPrice && (
            <p
              className={`text-[13px] text-charcoal mb-2 ${
                LEGAL_BAND_WEIGHT[legal.band ?? "Minor"]
              }`}
            >
              {legal.currency === "USD" ? "$" : ""}
              {legal.low!.toLocaleString()} – {legal.currency === "USD" ? "$" : ""}
              {legal.high!.toLocaleString()}
            </p>
          )}

          {legalCoverageCaveat && (
            <p className="text-[12px] font-medium text-charcoal leading-relaxed mb-2">
              {legalCoverageCaveat}
            </p>
          )}

          {legalHasPrice && legal.has_partial_jurisdictions && (
            <p className="text-[11px] text-gray-400 mt-1 mb-2 leading-relaxed">
              An unverified-confidence jurisdiction is present alongside a
              confirmed one here and could change this determination.
            </p>
          )}

          {legal.unpriced_state_ids.length > 0 && (
            <p className="text-[12px] text-gray-500 leading-relaxed mb-2">
              Real exposure current data can&apos;t price precisely for:{" "}
              {joinNames(unpricedStateNames)}.
            </p>
          )}

          <p className="text-[11px] text-gray-400 mt-1 leading-relaxed">
            {legal.caveat}
          </p>
        </div>
      )}

      {/* Block 5 — ShareButton */}'''

EDITS = [
    ('import line (add LegalTailRiskBand)', EDIT_1_OLD, EDIT_1_NEW),
    ('LEGAL_BAND_WEIGHT + joinNames const block', EDIT_2_OLD, EDIT_2_NEW),
    ('component derived-values block', EDIT_3_OLD, EDIT_3_NEW),
    ('Block 4d JSX', EDIT_4_OLD, EDIT_4_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    errors = []
    for label, old, new in EDITS:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
