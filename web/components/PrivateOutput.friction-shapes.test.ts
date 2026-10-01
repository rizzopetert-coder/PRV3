import { describe, it, expect, vi } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { PrivateOutputPayload } from "@/lib/types";
import { BASE_PRIVATE_PAYLOAD, RENDER_PROPS } from "@/lib/friction-test-base";
import {
  NEW_ESTIMATE, CAPPED_ESTIMATE, NEW_RECEIPTS, NEW_LEDGER, OLD_ESTIMATE, OLD_LEDGER, FRICTION_DOLLAR_STRINGS,
} from "@/lib/friction-test-fixtures";

// Stage 6 consumer test, PrivateOutput with friction dollars hidden (the flag stays
// false): the report must render without throwing, and show no friction-derived
// figure, whether the friction fields arrive in the new shape, the older shape, or
// are missing. The legal figure still renders in every case.
vi.mock("next/dynamic", () => ({ default: () => () => null }));
// Legal is forced visible here, see PrivateOutput.legal.test.ts for the default-hidden tests.
vi.mock("@/lib/output-text", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/output-text")>()),
  LEGAL_DOLLARS_VISIBLE: true,
}));

import PrivateOutput from "./PrivateOutput";

function render(over: Record<string, unknown>): string {
  const payload = { ...BASE_PRIVATE_PAYLOAD, ...over } as unknown as PrivateOutputPayload;
  return renderToStaticMarkup(createElement(PrivateOutput, { payload, ...RENDER_PROPS })).replace(/<!-- -->/g, "");
}

const CASES: Array<[string, Record<string, unknown>]> = [
  ["new shape", { friction_tax_estimate: NEW_ESTIMATE, friction_receipts: NEW_RECEIPTS, friction_tax_ledger: NEW_LEDGER }],
  ["new shape at the 1,000 cap", { friction_tax_estimate: CAPPED_ESTIMATE, friction_receipts: NEW_RECEIPTS, friction_tax_ledger: NEW_LEDGER }],
  ["old shape", { friction_tax_estimate: OLD_ESTIMATE, friction_tax_ledger: OLD_LEDGER }],
  ["missing", { friction_tax_estimate: null }],
  ["missing, fields absent entirely", {}],
  ["null ledger and receipts", { friction_tax_estimate: null, friction_tax_ledger: null, friction_receipts: null }],
  ["old estimate with a new ledger", { friction_tax_estimate: OLD_ESTIMATE, friction_tax_ledger: NEW_LEDGER }],
  ["new estimate with an old ledger", { friction_tax_estimate: NEW_ESTIMATE, friction_receipts: NEW_RECEIPTS, friction_tax_ledger: OLD_LEDGER }],
];

describe("PrivateOutput, friction hidden, every shape", () => {
  for (const [name, over] of CASES) {
    describe(name, () => {
      it("renders without throwing", () => {
        expect(render(over).length).toBeGreaterThan(1000);
      });
      it("shows no friction-derived figure, receipt or typical-loss line", () => {
        const html = render(over);
        for (const s of FRICTION_DOLLAR_STRINGS) expect(html).not.toContain(s);
        expect(html).not.toContain("Together, what organizations like yours typically lose");
        expect(html).not.toContain("What organizations like yours typically lose to friction");
      });
      it("still renders legal exposure and the cost comparison without a friction line", () => {
        const html = render(over);
        expect(html).toContain("$100,000 – $450,000");
        expect(html).toContain("Legal exposure, one-time if a claim arises");
      });
    });
  }

  it("a ledger in the new or old shape renders its conditions and answers", () => {
    for (const ledger of [NEW_LEDGER, OLD_LEDGER]) {
      const html = render({ friction_tax_estimate: null, friction_tax_ledger: ledger });
      expect(html).toContain("The answers behind these conditions");
      expect(html).toContain("Some processes here are out of date or inconsistently followed.");
    }
  });
});
