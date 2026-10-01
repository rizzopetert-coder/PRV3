// Shared fixtures for the Stage 6 consumer tests (friction tax rebuild): the three
// shapes a friction estimate and its ledger and receipts can arrive in at a web
// reader, the two-channel shape, the older { low, high } shape (a Preview record,
// or the minutes between the web and engine deploys), and missing.
import type { EvidenceReceipt, FrictionTaxEstimate, FrictionTaxLedgerEntry } from "./types";

// Hand-computed, 12 employees in Retail & Hospitality (spec 6b, R3).
export const NEW_ESTIMATE: FrictionTaxEstimate = {
  currency: "USD",
  typical_baseline: {
    total: { amount: 63923.24, percent_of_payroll: 12.6759 },
    channels: [
      { channel: "engagement", amount: 35401.02, percent_of_payroll: 7.02, inputs: [] },
      { channel: "turnover", amount: 28522.22, percent_of_payroll: 5.6559, inputs: [] },
    ],
  },
  excess: null,
};

// At the 1,000 intake cap every amount is null and only the percent is shown.
export const CAPPED_ESTIMATE: FrictionTaxEstimate = {
  currency: "USD",
  typical_baseline: {
    total: { amount: null, percent_of_payroll: 9.2018 },
    channels: [
      { channel: "engagement", amount: null, percent_of_payroll: 7.02, inputs: [] },
      { channel: "turnover", amount: null, percent_of_payroll: 2.1818, inputs: [] },
    ],
  },
  excess: null,
};

export const NEW_RECEIPTS: EvidenceReceipt[] = [
  { category: "Payroll baseline", rationale: "Estimated annual payroll for 12 Retail & Hospitality employees: $504,000." },
  { category: "Total", rationale: "Together, what organizations like yours typically lose is 12.68% of payroll, about $63,900 a year." },
];

export const NEW_LEDGER: FrictionTaxLedgerEntry[] = [{
  state_id: "built_to_fail", state_name: "Built to Fail", risk_label: "Emerging",
  channels: ["engagement", "turnover", "decision_time"],
  top_contributing_answers: ["Some processes here are out of date or inconsistently followed."],
}];

// The older shape, cast because the types no longer allow it.
export const OLD_ESTIMATE = {
  low: 1234567, high: 1728394, currency: "USD",
  driving_factors: [{ category: "Payroll baseline", rationale: "Estimated annual payroll: $9,870,000." }],
} as unknown as FrictionTaxEstimate;

export const OLD_LEDGER = [{
  state_id: "built_to_fail", state_name: "Built to Fail", risk_label: "Emerging",
  dollar_exposure: { low: 555555, high: 777777, currency: "USD" },
  top_contributing_answers: ["Some processes here are out of date or inconsistently followed."],
}] as unknown as FrictionTaxLedgerEntry[];

// Figures the hidden state must never show, from any of the shapes.
export const FRICTION_DOLLAR_STRINGS = [
  "$63,900", "$35,400", "$28,500", "$504,000", "12.68", "7.02%",
  "$1,230,000", "$1,730,000", "$556,000", "$778,000", "$9,870,000",
];
