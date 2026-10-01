// A fully populated legal block for the legal-hidden tests: every element the report
// can show (figure, band, coverage caveat, partial-jurisdiction caveat, net-worth
// caveat, specific caveat, unpriced note, base caveat, calculation receipts). Each
// carries a marker string so a test can look for it.
export const LEGAL_MARKERS = [
  "LEGAL-CAVEAT-MARKER",
  "LEGAL-SPECIFIC-MARKER",
  "LEGAL-RECEIPT-RATIONALE",
  "LEGAL-RECEIPT-ANSWER",
  "This range applies a federal coverage threshold",
  "State law in this jurisdiction was not independently",
  "Real exposure current data can",
];

export const LEGAL_RICH = {
  low: 123000,
  high: 456000,
  currency: "USD",
  band: "Significant",
  caveat: "LEGAL-CAVEAT-MARKER",
  has_unpriced_conditions: true,
  unpriced_state_ids: ["built_to_fail"],
  coverage_basis: "federal_baseline",
  has_partial_jurisdictions: true,
  has_uncollected_net_worth_caveat: true,
  specific_caveat: "LEGAL-SPECIFIC-MARKER",
  driving_factors: [
    { category: "Wage and hour", rationale: "LEGAL-RECEIPT-RATIONALE", triggering_answer: "LEGAL-RECEIPT-ANSWER" },
  ],
};
