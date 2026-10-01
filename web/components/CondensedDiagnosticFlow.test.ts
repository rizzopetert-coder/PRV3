import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import CondensedDiagnosticFlow from "./CondensedDiagnosticFlow";

// The condensed intro must not promise a cost or dollar figure while the figure is
// hidden (R2, Stage 3a). Pete's approved line, 2026-09-30.
describe("CondensedDiagnosticFlow intro", () => {
  const html = renderToStaticMarkup(createElement(CondensedDiagnosticFlow));

  it("renders the approved intro line", () => {
    expect(html.replace(/\s+/g, " ")).toContain(
      "It names the most prominent pattern in your answers. The full diagnostic goes further.",
    );
  });

  it("promises no cost or dollar figure", () => {
    expect(html).not.toMatch(/rough sense/i);
    expect(html).not.toMatch(/what it costs/i);
    expect(html).not.toMatch(/\$\s?\d/);
  });

  it("still renders the industry select and Begin", () => {
    expect(html).toContain("Industry");
    expect(html).toContain("Begin");
  });
});
