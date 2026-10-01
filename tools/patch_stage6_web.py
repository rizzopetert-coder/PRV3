"""
Friction tax rebuild, Stage 6 (pulled ahead of Stage 5): web types and consumers.

  web/lib/types.ts            two-channel FrictionTaxEstimate, ledger channels,
                              friction_receipts, no inaction_cost fields
  web/lib/output-text.ts      frictionTypicalLossText() and frictionReceiptsOf()
                              read the old, new or missing shape without throwing,
                              ledger groups carry no dollar figure, the visible
                              branch stops printing the two ledger notes that
                              described the old severity-scaled estimate
  web/components/PrivateOutput.tsx, ReportDetails.tsx
                              read the new shape through those helpers
  web/lib/engine-client.ts, diagnostic-completion.ts, app/api/result/route.ts,
  web/lib/dev-diagnostic-preview.ts
                              carry friction_receipts through
  web/lib/output-renderer.ts  deleted (no callers)

FRICTION_DOLLARS_VISIBLE is not touched.

Usage: python tools/patch_stage6_web.py --dry-run | --write
"""
import sys
from pathlib import Path

W = Path(__file__).resolve().parents[1] / "web"


def edit_file(path: Path, edits, write: bool) -> None:
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")
    for e in edits:
        if e[0] == "between":
            _, start, end, new = e
            assert t.count(start) == 1, f"{path.name}: start count {t.count(start)}: {start[:60]!r}"
            i = t.index(start)
            j = t.index(end, i)
            t = t[:i] + new + t[j:]
        else:
            old, new = e
            assert t.count(old) == 1, f"{path.name}: count {t.count(old)}: {old[:70]!r}"
            t = t.replace(old, new)
    print(f"{path.name}: {len(edits)} edits ok ({'CRLF' if crlf else 'LF'})")
    if write:
        path.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


TYPES_NEW = """/**
 * Friction tax estimate (two-channel rebuild). A point estimate of what
 * organizations like the client's typically lose each year, as two dollar
 * channels (engagement and turnover) built from cited inputs, shown as the gap to
 * the best-run organizations and never as a normal or acceptable level.
 * percent_of_payroll is present on every channel and on the total. amount is null
 * at the 1,000 intake cap (dollars withheld, only the percent is shown). The whole
 * estimate is null when the headcount cannot be priced or no identified state
 * switches on a dollar channel. Receipts are a sibling field,
 * PrivateOutputPayload.friction_receipts, not part of this object.
 *
 * Older payloads carried { low, high, driving_factors } (a Preview record, or the
 * minutes between the web and engine deploys of the rebuild), so every reader goes
 * through frictionTypicalLossText() and frictionReceiptsOf() in lib/output-text.ts
 * and tolerates that shape, this one, or null. Components render Option B
 * treatment when null.
 */
export interface FrictionChannelInput {
  name: string;
  value: number;
  source: string;
  vintage: string;
}

export interface FrictionChannel {
  channel: "engagement" | "turnover";
  amount: number | null;
  percent_of_payroll: number;
  inputs: FrictionChannelInput[];
}

export interface FrictionTaxEstimate {
  currency: string;
  typical_baseline: {
    total: { amount: number | null; percent_of_payroll: number };
    channels: FrictionChannel[];
  };
  excess: null;
}

/** The friction channels a state switches on (engine/contract.py ledger rows). */
export type FrictionLedgerChannel = "engagement" | "turnover" | "decision_time";

/**
 * Friction tax ledger row -- one per condition/state in identified_states,
 * same order. Sibling to friction_tax_estimate on PrivateOutputPayload.
 * Gemini-cleared architecture, built in engine/contract.py's
 * _build_friction_tax_ledger().
 *
 * risk_label reuses the state's own severity tier (same value StateSeverityEntry
 * carries) -- no new risk classification invented.
 *
 * channels lists which friction channels this state switches on (read from
 * engine/data/state_criteria.py). There is no per-state dollar figure: the
 * rebuild prices the state set once, not per state. Older rows carried
 * dollar_exposure, readers ignore it.
 *
 * top_contributing_answers is a ranked list of authored
 * AnswerOption.observation_text strings (skip-and-backfill: an unauthored
 * option is omitted, never padded with raw option_text), reusing
 * _build_signal_map_context()'s replay-and-rank technique against this
 * state's own SALIENCE_PROFILES entry. [] when answers_log was empty
 * (Path B/self-select) or nothing authored yet.
 */
export interface FrictionTaxLedgerEntry {
  state_id: string;
  state_name: string;
  risk_label: SeverityTier;
  channels: FrictionLedgerChannel[];
  top_contributing_answers: string[];
}

"""

OUTPUT_TEXT_HELPERS = """function money(low: number, high: number): string {
  return formatUsdRange(low, high);
}

// A percent of payroll to at most 2 decimals, trailing zeros dropped (7.02, 12.68).
function formatPercent(value: number): string {
  return value.toFixed(2).replace(/0+$/, "").replace(/\\.$/, "");
}

// The typical-loss line for a friction estimate, tolerant of every shape that can
// reach the client: the two-channel estimate (a dollar figure, or the percent of
// payroll at the 1,000 intake cap where amounts are withheld), the older
// { low, high } shape (a Preview record, or the minutes between the web and engine
// deploys), or null and anything else. Never throws.
export function frictionTypicalLossText(friction: unknown): string | null {
  if (!friction || typeof friction !== "object") return null;
  const f = friction as Record<string, unknown>;
  const baseline = f.typical_baseline;
  const total = baseline && typeof baseline === "object"
    ? (baseline as Record<string, unknown>).total
    : undefined;
  if (total && typeof total === "object") {
    const t = total as Record<string, unknown>;
    if (typeof t.amount === "number" && Number.isFinite(t.amount)) return formatUsd(t.amount);
    if (typeof t.percent_of_payroll === "number" && Number.isFinite(t.percent_of_payroll)) {
      return `${formatPercent(t.percent_of_payroll)}% of payroll`;
    }
    return null;
  }
  if (typeof f.low === "number" && typeof f.high === "number") return formatUsdRange(f.low, f.high);
  return null;
}

// The friction receipts, from the sibling field (new) or the estimate's own
// driving_factors (older payloads). undefined when neither exists.
export function frictionReceiptsOf(
  payload: { friction_receipts?: unknown; friction_tax_estimate?: unknown },
): EvidenceReceipt[] | undefined {
  if (Array.isArray(payload.friction_receipts)) return payload.friction_receipts as EvidenceReceipt[];
  const est = payload.friction_tax_estimate;
  if (est && typeof est === "object") {
    const legacy = (est as Record<string, unknown>).driving_factors;
    if (Array.isArray(legacy)) return legacy as EvidenceReceipt[];
  }
  return undefined;
}

// Shared label for the typical-loss line (screen and Copy results).
export const FRICTION_TYPICAL_LOSS_LABEL =
  "What organizations like yours typically lose to friction each year";
"""

GROUPS_NEW = """// One ledger row per distinct evidence set (P2). Rows whose
// top_contributing_answers are the same set (order ignored) merge into
// one group that names every condition. Rows with no evidence are never
// grouped: an empty list is not shared evidence. Group order follows first
// appearance. Rows carry no dollar figure (the rebuild prices the state set
// once), and an older row's dollar_exposure is ignored.
export interface LedgerGroup {
  conditions: Array<{ state_id: string; name: string; risk_label: SeverityTier }>;
  top_contributing_answers: string[];
}

export function groupLedgerRows(
  ledger: FrictionTaxLedgerEntry[],
  nameById?: Map<string, string>,
): LedgerGroup[] {
  const groups: LedgerGroup[] = [];
  const byEvidence = new Map<string, LedgerGroup>();
  for (const row of ledger) {
    const condition = {
      state_id: row.state_id,
      name: nameById?.get(row.state_id) ?? row.state_name,
      risk_label: row.risk_label,
    };
    const answers = Array.isArray(row.top_contributing_answers) ? row.top_contributing_answers : [];
    const key = answers.length > 0 ? JSON.stringify([...answers].sort()) : null;
    const existing = key ? byEvidence.get(key) : undefined;
    if (existing) {
      existing.conditions.push(condition);
      continue;
    }
    const group: LedgerGroup = {
      conditions: [condition],
      top_contributing_answers: answers,
    };
    groups.push(group);
    if (key) byEvidence.set(key, group);
  }
  return groups;
}
"""

LEDGER_TEXT_NEW = """  // Friction tax ledger. While friction dollars are hidden: the conditions and
  // the answers behind them, no figures, no receipts. Visible: the same rows,
  // then the calculation receipts. Rows carry no per-condition dollar figure.
  const ledger = Array.isArray(payload.friction_tax_ledger) ? payload.friction_tax_ledger : [];
  if (ledger.length > 0) {
    const block = [frictionVisible ? "Friction tax ledger:" : `${FRICTION_LEDGER_HEADING_NO_DOLLARS}:`];
    for (const group of groupLedgerRows(ledger, stateNameById)) {
      block.push(`— ${group.conditions.map((c) => `${c.name} (${c.risk_label})`).join(", ")}`);
      for (const t of group.top_contributing_answers) block.push(`  ${t}`);
    }
    add(block);
    if (!frictionVisible) add([FRICTION_LEDGER_NOTE_NO_DOLLARS]);
  }
  if (frictionVisible) {
    add(receiptLines("How the friction tax was calculated:", frictionReceiptsOf(payload)));
  }

  // Cost comparison (same gate as the on-screen CostComparison).
  const friction = frictionVisible ? payload.friction_tax_estimate : null;
  const frictionText = frictionTypicalLossText(friction);
  const scc = payload.service_cost_comparison;
  if (scc && (frictionText || legalHasPrice)) {
    const block = ["Cost comparison:"];
    if (frictionText) block.push(`— ${FRICTION_TYPICAL_LOSS_LABEL}: ${frictionText}`);
"""


def main():
    write = "--write" in sys.argv

    # ---- types.ts -------------------------------------------------------------
    edit_file(W / "lib/types.ts", [
        ("between", "/**\n * Friction tax estimate.\n", "/**\n * Legal/Compliance tail-risk exposure (private output only).", TYPES_NEW),
        ("  friction_tax_ledger?: FrictionTaxLedgerEntry[];\n",
         "  friction_tax_ledger?: FrictionTaxLedgerEntry[];\n\n"
         "  // Friction receipts (two-channel rebuild): payroll, each channel with its\n"
         "  // cited inputs, the conditions that switch channels on, the decision-time\n"
         "  // context (no dollar value) and the total. A sibling of friction_tax_estimate\n"
         "  // so it exists even when the estimate is null. Optional: older payloads and\n"
         "  // DevDiagnosticPreviewPayload predate it. Never shared, see share-store.ts.\n"
         "  friction_receipts?: EvidenceReceipt[];\n"),
        ("  inaction_cost_low: number | null;\n  inaction_cost_high: number | null;\n", ""),
    ], write)

    # ---- output-text.ts ----------------------------------------------------------
    raw = (W / "lib/output-text.ts").read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")

    def sub(old, new):
        nonlocal t
        assert t.count(old) == 1, f"output-text.ts count {t.count(old)}: {old[:70]!r}"
        t = t.replace(old, new)

    sub("function money(low: number, high: number): string {\n  return formatUsdRange(low, high);\n}\n", OUTPUT_TEXT_HELPERS)
    # remove the two ledger note constants
    # the footnote and standalone-note constants sit directly before the friction
    # dollar switch, which stays untouched
    i = t.index("// Block 4f footnote. Shared with PrivateOutput.tsx")
    j = t.index("// Friction dollar switch (Pete, 2026-09-28, option C)")
    t = t[:i] + t[j:]
    # groups
    i = t.index("// One ledger row per distinct evidence set (P2).")
    j = t.index("\n", t.index("  return groups;\n}\n", i) + len("  return groups;\n}\n") - 1)
    end = t.index("  return groups;\n}\n", i) + len("  return groups;\n}\n")
    t = t[:i] + GROUPS_NEW + t[end:]
    # the visible/hidden ledger text and the cost comparison head
    i = t.index("  // Friction tax ledger, with its footnote and calculation steps.")
    k_old = """  // Cost comparison (same gate as the on-screen CostComparison).
  const friction = frictionVisible ? payload.friction_tax_estimate : null;
  const scc = payload.service_cost_comparison;
  if (scc && (friction || legalHasPrice)) {
    const block = ["Cost comparison:"];
    if (friction) block.push(`— Friction tax, recurring every year: ${money(friction.low, friction.high)}`);
"""
    assert t.count(k_old) == 1, "cost comparison head"
    end = t.index(k_old) + len(k_old)
    t = t[:i] + LEDGER_TEXT_NEW + t[end:]
    if write:
        (W / "lib/output-text.ts").write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print(f"output-text.ts: ok ({'CRLF' if crlf else 'LF'})")

    # ---- PrivateOutput.tsx ---------------------------------------------------------
    edit_file(W / "components/PrivateOutput.tsx", [
        ("  FRICTION_LEDGER_NOTE_NO_DOLLARS, FRICTION_TAX_LEDGER_FOOTNOTE, FRICTION_TAX_LEDGER_STANDALONE_NOTE,\n  formatUsdRange, groupLedgerRows, joinNames, OHIO_NET_WORTH_CAVEAT,\n",
         "  FRICTION_LEDGER_NOTE_NO_DOLLARS, frictionReceiptsOf,\n  formatUsdRange, groupLedgerRows, joinNames, OHIO_NET_WORTH_CAVEAT,\n"),
        ("              const grouped = group.conditions.length > 1;\n              const d = group.dollar_exposure;\n              const figure = d ? formatUsdRange(d.low, d.high) : null;\n",
         ""),
        ("between",
         "                  {/* Option C: no figure line while friction dollars are hidden. */}\n",
         "                  {group.top_contributing_answers.length > 0 && (",
         ""),
        ("""          {FRICTION_DOLLARS_VISIBLE ? (
            <>
              <p className="text-[11px] text-slate mt-3 leading-relaxed">
                {FRICTION_TAX_LEDGER_STANDALONE_NOTE}
              </p>
              <p className="text-[11px] text-slate mt-2 leading-relaxed">
                {FRICTION_TAX_LEDGER_FOOTNOTE}
              </p>
              <EvidenceReceipts receipts={payload.friction_tax_estimate?.driving_factors} />
            </>
          ) : (
            <p className="text-[11px] text-slate mt-3 leading-relaxed">
              {FRICTION_LEDGER_NOTE_NO_DOLLARS}
            </p>
          )}
""", """          {FRICTION_DOLLARS_VISIBLE ? (
            <EvidenceReceipts receipts={frictionReceiptsOf(payload)} />
          ) : (
            <p className="text-[11px] text-slate mt-3 leading-relaxed">
              {FRICTION_LEDGER_NOTE_NO_DOLLARS}
            </p>
          )}
"""),
    ], write)

    # ---- ReportDetails.tsx ------------------------------------------------------------
    edit_file(W / "components/ReportDetails.tsx", [
        ('import { formatUsdRange } from "@/lib/output-text";\n',
         'import {\n  formatUsdRange, frictionTypicalLossText, FRICTION_TYPICAL_LOSS_LABEL,\n} from "@/lib/output-text";\n'),
        ("  friction: FrictionTaxEstimate | null;\n  legal: LegalTailRiskExposure | null;\n  fallbackServiceName: string;\n}) {\n  if (!comparison) return null;\n  const legalPriced = legal !== null && legal.low !== null && legal.high !== null;\n  if (!friction && !legalPriced) return null;\n",
         "  friction: FrictionTaxEstimate | null;\n  legal: LegalTailRiskExposure | null;\n  fallbackServiceName: string;\n}) {\n  if (!comparison) return null;\n  const legalPriced = legal !== null && legal.low !== null && legal.high !== null;\n  // Tolerant of the two-channel estimate (a dollar figure, or the percent of\n  // payroll at the intake cap), the older { low, high } shape, or null.\n  const frictionText = frictionTypicalLossText(friction);\n  if (!frictionText && !legalPriced) return null;\n"),
        ("""          {friction && (
            <div>
              <p className="text-sm font-medium text-charcoal">{rangeText(friction.low, friction.high)}</p>
              <p className="text-[11px] text-slate">Friction tax, recurring every year</p>
            </div>
          )}
""", """          {frictionText && (
            <div>
              <p className="text-sm font-medium text-charcoal">{frictionText}</p>
              <p className="text-[11px] text-slate">{FRICTION_TYPICAL_LOSS_LABEL}</p>
            </div>
          )}
"""),
    ], write)

    # ---- engine-client.ts ----------------------------------------------------------------
    edit_file(W / "lib/engine-client.ts", [
        ("  PrivateIntakeEcho, FrictionTaxEstimate, FrictionTaxLedgerEntry, LegalTailRiskExposure,\n",
         "  PrivateIntakeEcho, FrictionTaxEstimate, FrictionTaxLedgerEntry, LegalTailRiskExposure,\n  EvidenceReceipt,\n"),
        ("    friction_tax_ledger: FrictionTaxLedgerEntry[];\n    legal_tail_risk_exposure: LegalTailRiskExposure | null;\n",
         "    friction_tax_ledger: FrictionTaxLedgerEntry[];\n    friction_receipts?: EvidenceReceipt[];\n    legal_tail_risk_exposure: LegalTailRiskExposure | null;\n"),
    ], write)

    # ---- diagnostic-completion.ts / result route ---------------------------------------------
    edit_file(W / "lib/diagnostic-completion.ts", [
        ("    friction_tax_ledger: engineResult.private_output.friction_tax_ledger,\n",
         "    friction_tax_ledger: engineResult.private_output.friction_tax_ledger,\n    friction_receipts: engineResult.private_output.friction_receipts ?? [],\n"),
    ], write)
    edit_file(W / "app/api/result/route.ts", [
        ("    friction_tax_ledger: engineResult.private_output.friction_tax_ledger,\n",
         "    friction_tax_ledger: engineResult.private_output.friction_tax_ledger,\n    friction_receipts: engineResult.private_output.friction_receipts ?? [],\n"),
    ], write)

    # ---- dev-diagnostic-preview.ts --------------------------------------------------------------
    edit_file(W / "lib/dev-diagnostic-preview.ts", [
        ("  FrictionTaxEstimate,\n  LegalTailRiskExposure,\n", "  FrictionTaxEstimate,\n  EvidenceReceipt,\n  LegalTailRiskExposure,\n"),
        ("  friction_tax_estimate: FrictionTaxEstimate | null;\n  legal_tail_risk_exposure",
         "  friction_tax_estimate: FrictionTaxEstimate | null;\n  friction_receipts?: EvidenceReceipt[];\n  legal_tail_risk_exposure"),
    ], write)

    # ---- delete output-renderer.ts --------------------------------------------------------------
    r = W / "lib/output-renderer.ts"
    print("output-renderer.ts:", "delete" if r.exists() else "already gone")
    if write and r.exists():
        r.unlink()
    print("WRITE" if write else "DRY RUN")


main()
