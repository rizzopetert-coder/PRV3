import { describe, it, expect } from "vitest";
import { departureCostAmount, departureCostFromEngine } from "./condensed-departure-cost";

// Stage 5 deploy race: the web and engine deploy separately from one push, so every
// read of the condensed figure tolerates the new single value, the old { low, high }
// range and a missing value. Nothing throws.
describe("departureCostFromEngine (the answer route's read of the engine result)", () => {
  it("new single value: passed through", () => {
    expect(departureCostFromEngine({ condensed_departure_cost: { amount: 38304.99, currency: "USD" } }))
      .toEqual({ amount: 38304.99, currency: "USD" });
  });
  it("new, null amount (unknown industry): null amount", () => {
    expect(departureCostFromEngine({ condensed_departure_cost: { amount: null, currency: "USD" } }).amount).toBeNull();
  });
  it("old range (the previous engine): read as no figure, not converted", () => {
    const r = departureCostFromEngine({ condensed_financial_range: { low: 57515, high: 86272.5, currency: "USD" } });
    expect(r).toEqual({ amount: null, currency: "USD" });
  });
  it("missing: no figure", () => {
    expect(departureCostFromEngine({})).toEqual({ amount: null, currency: "USD" });
  });
  it("both fields present: the new one wins", () => {
    expect(departureCostFromEngine({
      condensed_departure_cost: { amount: 13993.99, currency: "USD" },
      condensed_financial_range: { low: 1, high: 2, currency: "USD" },
    }).amount).toBe(13993.99);
  });
  it("garbage never throws and gives no figure", () => {
    for (const bad of [null, undefined, "x", 5, [], { condensed_departure_cost: null },
                       { condensed_departure_cost: "x" }, { condensed_departure_cost: { amount: "38305" } },
                       { condensed_departure_cost: { amount: Number.NaN } }, { condensed_departure_cost: { amount: Infinity } }]) {
      expect(departureCostFromEngine(bad).amount).toBeNull();
    }
  });
});

describe("departureCostAmount (the component's read of the payload)", () => {
  it("new single value", () => {
    expect(departureCostAmount({ departure_cost: { amount: 38305, currency: "USD" } })).toBe(38305);
  });
  it("old range payload: no figure", () => {
    expect(departureCostAmount({ financial_range: { low: 33000, high: 49500, currency: "USD" } })).toBeNull();
  });
  it("missing or unusable: no figure, no throw", () => {
    for (const bad of [{}, null, undefined, "x", { departure_cost: null }, { departure_cost: {} }, { departure_cost: { amount: null } }]) {
      expect(departureCostAmount(bad)).toBeNull();
    }
  });
});
