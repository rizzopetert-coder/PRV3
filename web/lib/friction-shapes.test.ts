import { describe, it, expect } from "vitest";
import {
  buildResultsText, frictionTypicalLossText, frictionReceiptsOf, groupLedgerRows,
  FRICTION_TYPICAL_LOSS_LABEL,
} from "./output-text";
import type { PrivateOutputPayload } from "./types";
import { BASE_PRIVATE_PAYLOAD } from "./friction-test-base";
import {
  NEW_ESTIMATE, CAPPED_ESTIMATE, NEW_RECEIPTS, NEW_LEDGER, OLD_ESTIMATE, OLD_LEDGER, FRICTION_DOLLAR_STRINGS,
} from "./friction-test-fixtures";

// Stage 6 consumer tests for lib/output-text.ts: the helpers and buildResultsText
// (Copy results) read the new, older and missing shapes without throwing.
const withFriction = (over: Record<string, unknown>) =>
  ({ ...BASE_PRIVATE_PAYLOAD, ...over }) as unknown as PrivateOutputPayload;

describe("frictionTypicalLossText", () => {
  it("new shape: the dollar figure to 3 significant figures", () => {
    expect(frictionTypicalLossText(NEW_ESTIMATE)).toBe("$63,900");
  });
  it("new shape at the cap: the percent of payroll", () => {
    expect(frictionTypicalLossText(CAPPED_ESTIMATE)).toBe("9.2% of payroll");
  });
  it("old shape: the older range", () => {
    expect(frictionTypicalLossText(OLD_ESTIMATE)).toBe("$1,230,000 – $1,730,000");
  });
  it("missing or unusable: null, never a throw", () => {
    for (const bad of [null, undefined, {}, "x", 5, [], { typical_baseline: null }, { typical_baseline: {} },
                       { typical_baseline: { total: {} } }, { low: "a", high: 1 }, { low: 1 }]) {
      expect(frictionTypicalLossText(bad)).toBeNull();
    }
  });
});

describe("frictionReceiptsOf", () => {
  it("prefers the sibling friction_receipts", () => {
    expect(frictionReceiptsOf({ friction_receipts: NEW_RECEIPTS, friction_tax_estimate: OLD_ESTIMATE })).toEqual(NEW_RECEIPTS);
  });
  it("falls back to the older estimate's driving_factors", () => {
    expect(frictionReceiptsOf({ friction_tax_estimate: OLD_ESTIMATE })?.[0].category).toBe("Payroll baseline");
  });
  it("missing: undefined", () => {
    for (const p of [{}, { friction_tax_estimate: null }, { friction_receipts: null }, { friction_tax_estimate: NEW_ESTIMATE }]) {
      expect(frictionReceiptsOf(p)).toBeUndefined();
    }
  });
  it("an empty friction_receipts is returned as is, so the estimate's old factors do not resurface", () => {
    expect(frictionReceiptsOf({ friction_receipts: [], friction_tax_estimate: OLD_ESTIMATE })).toEqual([]);
  });
});

describe("groupLedgerRows", () => {
  it("groups new rows (no dollar_exposure) by evidence set and carries no figure", () => {
    const rows = [
      { ...NEW_LEDGER[0], state_id: "a", top_contributing_answers: ["x", "y"] },
      { ...NEW_LEDGER[0], state_id: "b", top_contributing_answers: ["y", "x"] },
      { ...NEW_LEDGER[0], state_id: "c", top_contributing_answers: [] },
    ];
    const groups = groupLedgerRows(rows);
    expect(groups).toHaveLength(2);
    expect(groups[0].conditions.map((c) => c.state_id)).toEqual(["a", "b"]);
    expect("dollar_exposure" in groups[0]).toBe(false);
  });
  it("old rows (with dollar_exposure) group the same and the figure is ignored", () => {
    const groups = groupLedgerRows([...OLD_LEDGER, { ...OLD_LEDGER[0], state_id: "b" }]);
    expect(groups).toHaveLength(1);
    expect(groups[0].conditions).toHaveLength(2);
    expect(JSON.stringify(groups)).not.toContain("555555");
  });
  it("a row with no top_contributing_answers array does not throw", () => {
    const row = { state_id: "a", state_name: "A", risk_label: "Emerging", channels: [] } as never;
    expect(() => groupLedgerRows([row])).not.toThrow();
  });
});

describe("buildResultsText, every shape", () => {
  const shapes: Array<[string, Record<string, unknown>]> = [
    ["new", { friction_tax_estimate: NEW_ESTIMATE, friction_receipts: NEW_RECEIPTS, friction_tax_ledger: NEW_LEDGER }],
    ["capped", { friction_tax_estimate: CAPPED_ESTIMATE, friction_receipts: NEW_RECEIPTS, friction_tax_ledger: NEW_LEDGER }],
    ["old", { friction_tax_estimate: OLD_ESTIMATE, friction_tax_ledger: OLD_LEDGER }],
    ["missing", { friction_tax_estimate: null }],
    ["absent", {}],
    ["null ledger", { friction_tax_estimate: null, friction_tax_ledger: null, friction_receipts: null }],
  ];
  for (const [name, over] of shapes) {
    it(`${name}: friction hidden (default) shows no friction figure and does not throw`, () => {
      const text = buildResultsText(withFriction(over));
      for (const s of FRICTION_DOLLAR_STRINGS) expect(text).not.toContain(s);
      expect(text).not.toContain(FRICTION_TYPICAL_LOSS_LABEL);
      expect(text).toContain("Legal exposure, one-time if a claim arises");
    });
    it(`${name}: friction visible does not throw`, () => {
      expect(() => buildResultsText(withFriction(over), undefined, { frictionDollarsVisible: true })).not.toThrow();
    });
  }
  it("new shape visible: the typical-loss line, receipts, ledger rows with no per-row figure", () => {
    const text = buildResultsText(withFriction(shapes[0][1]), undefined, { frictionDollarsVisible: true });
    expect(text).toContain(`— ${FRICTION_TYPICAL_LOSS_LABEL}: $63,900`);
    expect(text).toContain("How the friction tax was calculated:\n— Payroll baseline: Estimated annual payroll for 12 Retail & Hospitality employees: $504,000.");
    expect(text).toContain("Friction tax ledger:\n— Built to Fail (Emerging)\n  Some processes here are out of date or inconsistently followed.");
    expect(text).not.toContain("Estimates are calculated");
    expect(text).not.toContain("Highest standalone");
  });
  it("capped visible: the percent of payroll line, no estimate dollar figure", () => {
    const text = buildResultsText(withFriction(shapes[1][1]), undefined, { frictionDollarsVisible: true });
    expect(text).toContain(`— ${FRICTION_TYPICAL_LOSS_LABEL}: 9.2% of payroll`);
  });
  it("old visible: the older range and the driving_factors receipts", () => {
    const text = buildResultsText(withFriction(shapes[2][1]), undefined, { frictionDollarsVisible: true });
    expect(text).toContain(`— ${FRICTION_TYPICAL_LOSS_LABEL}: $1,230,000 – $1,730,000`);
    expect(text).toContain("How the friction tax was calculated:\n— Payroll baseline: Estimated annual payroll: $9,870,000.");
  });
  it("R5: the cost comparison never reads inaction_cost fields and shows two separate lines", () => {
    const text = buildResultsText(withFriction(shapes[0][1]), undefined, { frictionDollarsVisible: true });
    expect(text).toContain("Cost comparison:");
    expect(text).toContain("— Legal exposure, one-time if a claim arises: $100,000 – $450,000");
    expect(text).not.toContain("inaction");
  });
});
