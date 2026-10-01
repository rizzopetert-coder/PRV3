import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { PrivateOutputPayload } from "@/lib/types";
import { BASE_PRIVATE_PAYLOAD, RENDER_PROPS } from "@/lib/friction-test-base";
import {
  NEW_ESTIMATE, CAPPED_ESTIMATE, NEW_RECEIPTS, NEW_LEDGER, OLD_ESTIMATE, OLD_LEDGER,
} from "@/lib/friction-test-fixtures";

// Stage 6 consumer test, the restorable state: with the flag forced true the report
// must still render without throwing for the new, older and missing shapes, and show
// the right figure for each. This is only a mock, FRICTION_DOLLARS_VISIBLE itself
// stays false in lib/output-text.ts.
vi.mock("next/dynamic", () => ({ default: () => () => null }));
vi.mock("@/lib/output-text", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/output-text")>()),
  FRICTION_DOLLARS_VISIBLE: true,
  LEGAL_DOLLARS_VISIBLE: true,
}));

import PrivateOutput from "./PrivateOutput";

function render(over: Record<string, unknown>): string {
  const payload = { ...BASE_PRIVATE_PAYLOAD, ...over } as unknown as PrivateOutputPayload;
  return renderToStaticMarkup(createElement(PrivateOutput, { payload, ...RENDER_PROPS })).replace(/<!-- -->/g, "");
}

describe("PrivateOutput, friction forced visible, every shape", () => {
  it("new shape: the typical-loss line, the receipts from friction_receipts, the ledger without a figure", () => {
    const html = render({ friction_tax_estimate: NEW_ESTIMATE, friction_receipts: NEW_RECEIPTS, friction_tax_ledger: NEW_LEDGER });
    expect(html).toContain("What organizations like yours typically lose to friction each year");
    expect(html).toContain("$63,900");
    expect(html).toContain("Together, what organizations like yours typically lose");
    expect(html).toContain("Friction tax ledger");
    expect(html).not.toContain("Highest standalone");
    expect(html).not.toContain("Estimate not available");
  });
  it("new shape at the 1,000 cap: percent of payroll only, no dollar figure from the estimate", () => {
    const html = render({ friction_tax_estimate: CAPPED_ESTIMATE, friction_receipts: [], friction_tax_ledger: NEW_LEDGER });
    expect(html).toContain("9.2% of payroll");
    expect(html).not.toContain("$63,900");
  });
  it("old shape: the older range and the driving_factors receipts still render", () => {
    const html = render({ friction_tax_estimate: OLD_ESTIMATE, friction_tax_ledger: OLD_LEDGER });
    expect(html).toContain("$1,230,000 – $1,730,000");
    expect(html).toContain("Payroll baseline");
    expect(html).toContain("Estimated annual payroll: $9,870,000.");
  });
  it("missing: no friction line, no throw, legal still renders", () => {
    for (const over of [{ friction_tax_estimate: null }, {}, { friction_tax_estimate: null, friction_tax_ledger: null, friction_receipts: null }]) {
      const html = render(over);
      expect(html).not.toContain("What organizations like yours typically lose to friction");
      expect(html).toContain("$100,000 – $450,000");
    }
  });
});
