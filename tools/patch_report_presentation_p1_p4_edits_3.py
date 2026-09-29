# Anchor/replacement data for tools/patch_report_presentation_p1_p4.py, part 3:
# Pete's additions A1-A3 (2026-09-28), applied after parts 1-2 in the same
# namespace, so every anchor here is the text as parts 1-2 leave it.
#
#   A1  Every dollar figure shown to 3 significant figures, half up, never
#       "$0" for a nonzero value, screen and Copy results and the condensed
#       report, display-only (payload values unrounded). One formatter per
#       language, same rule: formatUsd/formatUsdRange in output-text.ts for
#       every web figure, _usd in contract.py for the calculation-step text
#       the engine writes. (ShareableOutput renders no dollar figures.)
#   A2  Grouped ledger rows on screen: first 3 names with badges, then an
#       "and N more" toggle. Copy results keeps the full list.
#   A3  Ledger evidence ranks on *_liability only (same rule as P3's
#       ranking), and zero-weight answers are left out, so an answer with
#       asset-only signal (Q18-E outside high-hazard industries) never
#       appears as ledger evidence.

# ── A1 + A3: engine/contract.py ───────────────────────────────────────────────
EDITS["engine/contract.py"] += [
    ("import uuid\n", "import math\nimport uuid\n"),
    (
        "def _usd(value: float) -> str:\n"
        "    return f\"${value:,.0f}\"\n",
        "def _usd(value: float) -> str:\n"
        "    \"\"\"Display dollars to 3 significant figures, half up (A1). Same rule as\n"
        "    formatUsd in web/lib/output-text.ts. Payload values stay unrounded.\n"
        "    A nonzero value never renders as $0.\"\"\"\n"
        "    if value == 0:\n"
        "        return \"$0\"\n"
        "    unit = 10 ** max(0, math.floor(math.log10(abs(value))) + 1 - 3)\n"
        "    rounded = int(math.floor(value / unit + 0.5)) * unit\n"
        "    return f\"${rounded:,}\" if rounded else \"under $1\"\n",
    ),
    (
        "            _usd(b[\"low\"]) if b[\"low\"] == b[\"high\"]\n",
        "            _usd(b[\"low\"]) if _usd(b[\"low\"]) == _usd(b[\"high\"])\n",
    ),
    (
        "                    weight = sum(\n"
        "                        contribution.get(f, 0.0) * salience.get(f, 0.0)\n"
        "                        for f in DIMENSIONAL_FIELDS\n"
        "                    )\n"
        "                    scored.append((weight, option))\n",
        "                    # A3: liability fields only, and zero-weight answers\n"
        "                    # left out, same ranking rule as receipt evidence.\n"
        "                    weight = sum(\n"
        "                        contribution.get(f, 0.0) * salience.get(f, 0.0)\n"
        "                        for f in _LIABILITY_FIELDS\n"
        "                    )\n"
        "                    if weight > 0:\n"
        "                        scored.append((weight, option))\n",
    ),
]

# ── A1: web/lib/output-text.ts ────────────────────────────────────────────────
EDITS["web/lib/output-text.ts"] += [
    (
        "function money(low: number, high: number): string {\n"
        "  const f = (v: number) => `$${Math.round(v).toLocaleString()}`;\n"
        "  return low === high ? f(low) : `${f(low)} – ${f(high)}`;\n"
        "}\n",
        "// Display-only dollar rounding (A1, Pete 2026-09-28): every dollar figure\n"
        "// in the report, on screen and in Copy results, is shown to 3 significant\n"
        "// figures, half up (4,839,283 -> $4,840,000, 16,550 -> $16,600, 450 ->\n"
        "// $450). A nonzero value never renders as $0. Payload values stay\n"
        "// unrounded. The engine's calculation-step text uses the same rule\n"
        "// (engine/contract.py _usd).\n"
        "export function formatUsd(value: number): string {\n"
        "  if (value === 0) return \"$0\";\n"
        "  const unit = 10 ** Math.max(0, Math.floor(Math.log10(Math.abs(value))) + 1 - 3);\n"
        "  const rounded = Math.floor(value / unit + 0.5) * unit;\n"
        "  return rounded === 0 ? \"under $1\" : `$${rounded.toLocaleString(\"en-US\")}`;\n"
        "}\n"
        "\n"
        "// A range, collapsed to one figure when both ends round to the same value.\n"
        "export function formatUsdRange(low: number, high: number): string {\n"
        "  const a = formatUsd(low);\n"
        "  const b = formatUsd(high);\n"
        "  return a === b ? a : `${a} – ${b}`;\n"
        "}\n"
        "\n"
        "function money(low: number, high: number): string {\n"
        "  return formatUsdRange(low, high);\n"
        "}\n",
    ),
    (
        "      const sym = legal.currency === \"USD\" ? \"$\" : \"\";\n"
        "      block.push(\n"
        "        legal.low === legal.high\n"
        "          ? `Estimated exposure: ${sym}${legal.low!.toLocaleString()}`\n"
        "          : `${sym}${legal.low!.toLocaleString()} – ${sym}${legal.high!.toLocaleString()}`,\n"
        "      );\n",
        "      const figure = formatUsdRange(legal.low!, legal.high!);\n"
        "      block.push(figure.includes(\"–\") ? figure : `Estimated exposure: ${figure}`);\n",
    ),
    (
        "      const sym = d?.currency === \"USD\" ? \"$\" : \"\";\n"
        "      const grouped = group.conditions.length > 1;\n"
        "      const figure = d\n"
        "        ? d.low === d.high\n"
        "          ? `${sym}${d.low.toLocaleString()}`\n"
        "          : `${sym}${d.low.toLocaleString()} – ${sym}${d.high.toLocaleString()}`\n"
        "        : null;\n"
        "      const amount = figure === null\n"
        "        ? `Estimate not available for ${grouped ? \"these conditions\" : \"this condition\"}.`\n"
        "        : grouped\n"
        "          ? `highest standalone estimate in this group, ${figure}`\n"
        "          : d!.low === d!.high ? `Estimated exposure: ${figure}` : figure;\n",
        "      const grouped = group.conditions.length > 1;\n"
        "      const figure = d ? formatUsdRange(d.low, d.high) : null;\n"
        "      const amount = figure === null\n"
        "        ? `Estimate not available for ${grouped ? \"these conditions\" : \"this condition\"}.`\n"
        "        : grouped\n"
        "          ? `highest standalone estimate in this group, ${figure}`\n"
        "          : figure.includes(\"–\") ? figure : `Estimated exposure: ${figure}`;\n",
    ),
]

# ── A1 + A2: web/components/PrivateOutput.tsx ─────────────────────────────────
EDITS["web/components/PrivateOutput.tsx"] += [
    (
        "  groupLedgerRows, joinNames, OHIO_NET_WORTH_CAVEAT,\n",
        "  formatUsdRange, groupLedgerRows, joinNames, OHIO_NET_WORTH_CAVEAT,\n",
    ),
    (
        "interface PrivateOutputProps {\n",
        "// One ledger condition name with its tier badge (A2).\n"
        "function LedgerConditionBadge({ name, tier }: { name: string; tier: SeverityTier }) {\n"
        "  const accent = severityAccentTokens(tier);\n"
        "  return (\n"
        "    <span className=\"flex items-center gap-2\">\n"
        "      <span className=\"text-[13px] text-charcoal\">{name}</span>\n"
        "      <span\n"
        "        className=\"text-[10px] rounded-md px-1.5 py-0.5 border\"\n"
        "        style={{ borderColor: accent.stroke, color: accent.text }}\n"
        "      >\n"
        "        {tier}\n"
        "      </span>\n"
        "    </span>\n"
        "  );\n"
        "}\n"
        "\n"
        "// A grouped ledger row shows at most this many names before \"and N more\".\n"
        "const LEDGER_NAMES_SHOWN = 3;\n"
        "\n"
        "interface PrivateOutputProps {\n",
    ),
    (
        "              {legal.low === legal.high ? (\n"
        "                <>\n"
        "                  Estimated exposure: {legal.currency === \"USD\" ? \"$\" : \"\"}\n"
        "                  {legal.low!.toLocaleString()}\n"
        "                </>\n"
        "              ) : (\n"
        "                <>\n"
        "                  {legal.currency === \"USD\" ? \"$\" : \"\"}\n"
        "                  {legal.low!.toLocaleString()} – {legal.currency === \"USD\" ? \"$\" : \"\"}\n"
        "                  {legal.high!.toLocaleString()}\n"
        "                </>\n"
        "              )}\n",
        "              {(() => {\n"
        "                const figure = formatUsdRange(legal.low!, legal.high!);\n"
        "                return figure.includes(\"–\") ? figure : `Estimated exposure: ${figure}`;\n"
        "              })()}\n",
    ),
    (
        "              const d = group.dollar_exposure;\n"
        "              const sym = d?.currency === \"USD\" ? \"$\" : \"\";\n"
        "              return (\n"
        "                <li key={group.conditions[0].state_id}>\n"
        "                  <div className=\"flex flex-wrap items-center gap-x-3 gap-y-1 mb-1\">\n"
        "                    {group.conditions.map((c) => {\n"
        "                      const accent = severityAccentTokens(c.risk_label);\n"
        "                      return (\n"
        "                        <span key={c.state_id} className=\"flex items-center gap-2\">\n"
        "                          <span className=\"text-[13px] text-charcoal\">{c.name}</span>\n"
        "                          <span\n"
        "                            className=\"text-[10px] rounded-md px-1.5 py-0.5 border\"\n"
        "                            style={{ borderColor: accent.stroke, color: accent.text }}\n"
        "                          >\n"
        "                            {c.risk_label}\n"
        "                          </span>\n"
        "                        </span>\n"
        "                      );\n"
        "                    })}\n"
        "                  </div>\n",
        "              const d = group.dollar_exposure;\n"
        "              const figure = d ? formatUsdRange(d.low, d.high) : null;\n"
        "              const hidden = group.conditions.slice(LEDGER_NAMES_SHOWN);\n"
        "              return (\n"
        "                <li key={group.conditions[0].state_id}>\n"
        "                  <div className=\"flex flex-wrap items-center gap-x-3 gap-y-1 mb-1\">\n"
        "                    {group.conditions.slice(0, LEDGER_NAMES_SHOWN).map((c) => (\n"
        "                      <LedgerConditionBadge key={c.state_id} name={c.name} tier={c.risk_label} />\n"
        "                    ))}\n"
        "                    {/* A2: the rest of a large group behind a toggle. */}\n"
        "                    {hidden.length > 0 && (\n"
        "                      <details>\n"
        "                        <summary className=\"text-[12px] text-slate cursor-pointer hover:underline\">\n"
        "                          and {hidden.length} more\n"
        "                        </summary>\n"
        "                        <div className=\"flex flex-wrap items-center gap-x-3 gap-y-1 mt-1\">\n"
        "                          {hidden.map((c) => (\n"
        "                            <LedgerConditionBadge key={c.state_id} name={c.name} tier={c.risk_label} />\n"
        "                          ))}\n"
        "                        </div>\n"
        "                      </details>\n"
        "                    )}\n"
        "                  </div>\n",
    ),
    (
        "                    {d ? (\n"
        "                      <>\n"
        "                        {grouped ? (\n"
        "                          <span className=\"text-slate\">Highest standalone estimate in this group: </span>\n"
        "                        ) : d.low === d.high ? (\n"
        "                          \"Estimated exposure: \"\n"
        "                        ) : null}\n"
        "                        {d.low === d.high\n"
        "                          ? `${sym}${d.low.toLocaleString()}`\n"
        "                          : `${sym}${d.low.toLocaleString()} – ${sym}${d.high.toLocaleString()}`}\n"
        "                      </>\n",
        "                    {figure ? (\n"
        "                      <>\n"
        "                        {grouped ? (\n"
        "                          <span className=\"text-slate\">Highest standalone estimate in this group: </span>\n"
        "                        ) : figure.includes(\"–\") ? null : (\n"
        "                          \"Estimated exposure: \"\n"
        "                        )}\n"
        "                        {figure}\n"
        "                      </>\n",
    ),
]

# ── A1: web/components/ReportDetails.tsx (cost comparison) ────────────────────
EDITS["web/components/ReportDetails.tsx"] = [
    (
        "} from \"@/lib/types\";\n",
        "} from \"@/lib/types\";\n"
        "import { formatUsdRange } from \"@/lib/output-text\";\n",
    ),
    (
        "function usd(value: number): string {\n"
        "  return `$${Math.round(value).toLocaleString()}`;\n"
        "}\n",
        "",
    ),
    (
        "function rangeText(low: number, high: number): string {\n"
        "  return low === high ? usd(low) : `${usd(low)} – ${usd(high)}`;\n"
        "}\n",
        "// Dollars to the nearest $1,000 (A1), the shared report formatter.\n"
        "function rangeText(low: number, high: number): string {\n"
        "  return formatUsdRange(low, high);\n"
        "}\n",
    ),
]

# ── Tests ─────────────────────────────────────────────────────────────────────
EDITS["web/lib/output-text.test.ts"] += [
    (
        "  FRICTION_TAX_LEDGER_STANDALONE_NOTE, groupLedgerRows,\n",
        "  FRICTION_TAX_LEDGER_STANDALONE_NOTE, groupLedgerRows, formatUsd, formatUsdRange,\n",
    ),
    (
        '          dollar_exposure: { low: 100, high: 140, currency: "USD" }, top_contributing_answers: shared },\n',
        '          dollar_exposure: { low: 100400, high: 140560, currency: "USD" }, top_contributing_answers: shared },\n',
    ),
    (
        '          dollar_exposure: { low: 300, high: 420, currency: "USD" }, top_contributing_answers: [...shared].reverse() },\n',
        '          dollar_exposure: { low: 300499, high: 420699, currency: "USD" }, top_contributing_answers: [...shared].reverse() },\n',
    ),
    (
        '          dollar_exposure: { low: 200, high: 280, currency: "USD" }, top_contributing_answers: ["Answer three."] },\n',
        '          dollar_exposure: { low: 200500, high: 280700, currency: "USD" }, top_contributing_answers: ["Answer three."] },\n',
    ),
    (
        "highest standalone estimate in this group, $300 – $420\\n",
        "highest standalone estimate in this group, $300,000 – $421,000\\n",
    ),
    (
        '    expect(grouped).toContain("— Cond C (Emerging): $200 – $280\\n  Answer three.");\n',
        '    expect(grouped).toContain("— Cond C (Emerging): $201,000 – $281,000\\n  Answer three.");\n',
    ),
    (
        '  it("groupLedgerRows never groups rows that have no evidence", () => {\n',
        '  it("formats every dollar figure to 3 significant figures, half up, never $0 (A1)", () => {\n'
        '    expect(formatUsd(4839283)).toBe("$4,840,000");\n'
        '    expect(formatUsd(604214.4)).toBe("$604,000");\n'
        '    expect(formatUsd(1800)).toBe("$1,800");\n'
        '    expect(formatUsd(16550)).toBe("$16,600");\n'
        '    expect(formatUsd(450)).toBe("$450");\n'
        '    expect(formatUsd(16381908.3)).toBe("$16,400,000");\n'
        '    expect(formatUsd(0.3)).not.toBe("$0");\n'
        '    expect(formatUsd(0)).toBe("$0");\n'
        '    expect(formatUsdRange(604214.4, 626278.8)).toBe("$604,000 – $626,000");\n'
        '    expect(formatUsdRange(604214.4, 604400)).toBe("$604,000");\n'
        '    const legal = buildResultsText({\n'
        '      ...phase3,\n'
        '      legal_tail_risk_exposure: { ...phase3.legal_tail_risk_exposure!, low: 604214.4, high: 626278.8 },\n'
        '    });\n'
        '    expect(legal).toContain("Legal/Compliance exposure:\\n$604,000 – $626,000");\n'
        '    expect(legal).not.toMatch(/\\$[0-9,]+\\.[0-9]/);\n'
        '  });\n'
        '  it("groupLedgerRows never groups rows that have no evidence", () => {\n',
    ),
]

EDITS["tools/test_phase1_report_data.py"] += [
    (
        "check(\"P3: floor is 0.20\", _RECEIPT_EVIDENCE_MIN_WEIGHT == 0.20)\n",
        "check(\"P3: floor is 0.20\", _RECEIPT_EVIDENCE_MIN_WEIGHT == 0.20)\n"
        "\n"
        "# A3: ledger evidence ranks on *_liability only, zero-weight answers left out\n"
        "_led_q18 = _build_friction_tax_ledger(\n"
        "    [{\"state_id\": \"invisible_performance_management\", \"state_name\": \"x\"}],\n"
        "    [{\"state_id\": \"invisible_performance_management\", \"tier\": \"Emerging\"}],\n"
        "    [{\"question_id\": \"Q18\", \"option_ids\": [\"E\"]}], INTAKE)\n"
        "check(\"A3: Q18-E in a non-hazard industry never appears as ledger evidence\",\n"
        "      INTAKE.industry not in __import__(\"engine.data.intake\", fromlist=[\"x\"]).HIGH_HAZARD_INDUSTRIES\n"
        "      and all(_q18e.observation_text not in r[\"top_contributing_answers\"] for r in _led_q18), str(_led_q18))\n"
        "\n"
        "# A1: calculation-step dollars to 3 significant figures, half up, never $0\n"
        "from engine.contract import _usd\n"
        "_a1 = tuple(_usd(v) for v in (4839283, 604214.4, 1800, 16550, 450, 16381908.3, 2499.99))\n"
        "check(\"A1: _usd rounds to 3 significant figures, half up\",\n"
        "      _a1 == (\"$4,840,000\", \"$604,000\", \"$1,800\", \"$16,600\", \"$450\", \"$16,400,000\", \"$2,500\"), str(_a1))\n"
        "check(\"A1: _usd never renders $0 for a nonzero value\", _usd(0.3) != \"$0\" and _usd(0) == \"$0\")\n",
    ),
]

# ── A1: web/components/CondensedOutput.tsx (condensed report figure) ──────────
EDITS["web/components/CondensedOutput.tsx"] = [
    (
        'import type { CondensedOutputPayload } from "@/lib/types";\n',
        'import type { CondensedOutputPayload } from "@/lib/types";\n'
        'import { formatUsdRange } from "@/lib/output-text";\n',
    ),
    (
        '            {currency === "USD" ? "$" : ""}\n'
        '            {low!.toLocaleString()} – {currency === "USD" ? "$" : ""}\n'
        '            {high!.toLocaleString()}{" "}\n',
        '            {formatUsdRange(low!, high!)}{" "}\n',
    ),
    (
        "  const { low, high, currency } = payload.financial_range;\n",
        "  const { low, high } = payload.financial_range;\n",
    ),
]

# ── Pete's decision (a) on the A3 conflict: tools/test_contract.py ───────────
EDITS["tools/test_contract.py"] = [
    (
        'check(\n'
        '    "friction_tax_ledger row: top_contributing_answers is non-empty and ranked "\n'
        '    "-- Q01/B\'s real authored observation_text must appear (both Q01 and Q06 "\n'
        '    "were logged, capped at _LEDGER_TOP_ANSWERS_MAX=3)",\n'
        '    isinstance(ledger_row.get("top_contributing_answers"), list)\n'
        '    and 0 < len(ledger_row["top_contributing_answers"]) <= 3\n'
        '    and "Bigger decisions get complicated here even when smaller ones don\'t." in ledger_row["top_contributing_answers"],\n'
        '    f"got {ledger_row.get(\'top_contributing_answers\')}",\n'
        ')\n',
        '# Q01-B carries negative authority_liability (-0.15), so its liability-only\n'
        '# weight is below zero and the ledger\'s weight filter (A3, weight > 0)\n'
        '# excludes it. Its scoring is logged for calibration. Q06 still supplies\n'
        '# real evidence, so the row is non-empty.\n'
        'check(\n'
        '    "friction_tax_ledger row: top_contributing_answers is non-empty and ranked "\n'
        '    "-- Q01/B (negative weight) is ABSENT, capped at _LEDGER_TOP_ANSWERS_MAX=3",\n'
        '    isinstance(ledger_row.get("top_contributing_answers"), list)\n'
        '    and 0 < len(ledger_row["top_contributing_answers"]) <= 3\n'
        '    and "Bigger decisions get complicated here even when smaller ones don\'t." not in ledger_row["top_contributing_answers"],\n'
        '    f"got {ledger_row.get(\'top_contributing_answers\')}",\n'
        ')\n',
    ),
]
