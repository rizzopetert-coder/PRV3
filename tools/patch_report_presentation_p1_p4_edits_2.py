# Anchor/replacement data for tools/patch_report_presentation_p1_p4.py, part 2:
# the screen (PrivateOutput.tsx) and the tests. Executed after part 1 into the
# same namespace (EDITS, LEDGER_NOTE, LEGAL_TOTAL_NEW_TEXT already defined).

# ── P1 + P2: web/components/PrivateOutput.tsx ─────────────────────────────────
_OLD_LEDGER_ROWS = """            {frictionTaxLedger.map((row) => {
              const rowAccent = severityAccentTokens(row.risk_label);
              return (
                <li key={row.state_id}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[13px] text-charcoal">
                      {stateNameById.get(row.state_id) ?? row.state_name}
                    </span>
                    <span
                      className="text-[10px] rounded-md px-1.5 py-0.5 border"
                      style={{ borderColor: rowAccent.stroke, color: rowAccent.text }}
                    >
                      {row.risk_label}
                    </span>
                  </div>
                  <p className="text-[13px] text-charcoal mb-1">
                    {row.dollar_exposure ? (
                      row.dollar_exposure.low === row.dollar_exposure.high ? (
                        <>
                          Estimated exposure: {row.dollar_exposure.currency === "USD" ? "$" : ""}
                          {row.dollar_exposure.low.toLocaleString()}
                        </>
                      ) : (
                        <>
                          {row.dollar_exposure.currency === "USD" ? "$" : ""}
                          {row.dollar_exposure.low.toLocaleString()} –{" "}
                          {row.dollar_exposure.currency === "USD" ? "$" : ""}
                          {row.dollar_exposure.high.toLocaleString()}
                        </>
                      )
                    ) : (
                      <span className="text-slate">Estimate not available for this condition.</span>
                    )}
                  </p>
                  {row.top_contributing_answers.length > 0 && (
                    <ul className="text-[12px] text-slate leading-relaxed list-disc pl-4 space-y-0.5">
                      {row.top_contributing_answers.map((text, i) => (
                        <li key={i}>{text}</li>
                      ))}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
          <p className="text-[11px] text-slate mt-3 leading-relaxed">
            {FRICTION_TAX_LEDGER_FOOTNOTE}
          </p>
"""

_NEW_LEDGER_ROWS = """            {/* P2: rows citing the same evidence set share one row. */}
            {groupLedgerRows(frictionTaxLedger, stateNameById).map((group) => {
              const grouped = group.conditions.length > 1;
              const d = group.dollar_exposure;
              const sym = d?.currency === "USD" ? "$" : "";
              return (
                <li key={group.conditions[0].state_id}>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mb-1">
                    {group.conditions.map((c) => {
                      const accent = severityAccentTokens(c.risk_label);
                      return (
                        <span key={c.state_id} className="flex items-center gap-2">
                          <span className="text-[13px] text-charcoal">{c.name}</span>
                          <span
                            className="text-[10px] rounded-md px-1.5 py-0.5 border"
                            style={{ borderColor: accent.stroke, color: accent.text }}
                          >
                            {c.risk_label}
                          </span>
                        </span>
                      );
                    })}
                  </div>
                  <p className="text-[13px] text-charcoal mb-1">
                    {d ? (
                      <>
                        {grouped ? (
                          <span className="text-slate">Highest standalone estimate in this group: </span>
                        ) : d.low === d.high ? (
                          "Estimated exposure: "
                        ) : null}
                        {d.low === d.high
                          ? `${sym}${d.low.toLocaleString()}`
                          : `${sym}${d.low.toLocaleString()} – ${sym}${d.high.toLocaleString()}`}
                      </>
                    ) : (
                      <span className="text-slate">
                        Estimate not available for {grouped ? "these conditions" : "this condition"}.
                      </span>
                    )}
                  </p>
                  {group.top_contributing_answers.length > 0 && (
                    <ul className="text-[12px] text-slate leading-relaxed list-disc pl-4 space-y-0.5">
                      {group.top_contributing_answers.map((text, i) => (
                        <li key={i}>{text}</li>
                      ))}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
          <p className="text-[11px] text-slate mt-3 leading-relaxed">
            {FRICTION_TAX_LEDGER_STANDALONE_NOTE}
          </p>
          <p className="text-[11px] text-slate mt-2 leading-relaxed">
            {FRICTION_TAX_LEDGER_FOOTNOTE}
          </p>
"""

EDITS["web/components/PrivateOutput.tsx"] = [
    (
        'import { buildConditionRows, FRICTION_TAX_LEDGER_FOOTNOTE, joinNames, OHIO_NET_WORTH_CAVEAT } from "@/lib/output-text";',
        'import {\n'
        '  buildConditionRows, FRICTION_TAX_LEDGER_FOOTNOTE, FRICTION_TAX_LEDGER_STANDALONE_NOTE,\n'
        '  groupLedgerRows, joinNames, OHIO_NET_WORTH_CAVEAT,\n'
        '} from "@/lib/output-text";',
    ),
    ("  const primaryAssetDomain = payload.primary_asset_domain;\n", ""),
    (
        "        {(anchorText || primaryAssetDomain || payload.asset_evidence) && (\n"
        "          <div>\n"
        "            {primaryAssetDomain && (\n"
        "              <p className=\"text-[11px] uppercase tracking-wide text-slate mb-2\">\n"
        "                Primary asset domain: {primaryAssetDomain}\n"
        "              </p>\n"
        "            )}\n"
        "            {anchorText && (\n",
        "        {/* P1: the primary asset domain describes the lead condition, not\n"
        "            this respondent, so it is not shown. */}\n"
        "        {(anchorText || payload.asset_evidence) && (\n"
        "          <div>\n"
        "            {anchorText && (\n",
    ),
    (_OLD_LEDGER_ROWS, _NEW_LEDGER_ROWS),
]

# ── vitest ────────────────────────────────────────────────────────────────────
_GROUP_TESTS = r'''  it("groups ledger rows with the same evidence set into one row, highest standalone estimate, evidence once", () => {
    const shared = ["Answer one.", "Answer two."];
    const grouped = buildResultsText({
      ...phase3,
      friction_tax_ledger: [
        { state_id: "a", state_name: "Cond A", risk_label: "Emerging",
          dollar_exposure: { low: 100, high: 140, currency: "USD" }, top_contributing_answers: shared },
        { state_id: "b", state_name: "Cond B", risk_label: "Entrenched",
          dollar_exposure: { low: 300, high: 420, currency: "USD" }, top_contributing_answers: [...shared].reverse() },
        { state_id: "c", state_name: "Cond C", risk_label: "Emerging",
          dollar_exposure: { low: 200, high: 280, currency: "USD" }, top_contributing_answers: ["Answer three."] },
      ],
    });
    expect(grouped).toContain(
      "— Cond A (Emerging), Cond B (Entrenched): highest standalone estimate in this group, $300 – $420\n  Answer one.\n  Answer two.",
    );
    expect(grouped.split("Answer one.").length - 1).toBe(1);
    expect(grouped).toContain("— Cond C (Emerging): $200 – $280\n  Answer three.");
    expect(grouped).toContain(FRICTION_TAX_LEDGER_STANDALONE_NOTE);
  });
  it("groupLedgerRows never groups rows that have no evidence", () => {
    const groups = groupLedgerRows([
      { state_id: "a", state_name: "A", risk_label: "Emerging", dollar_exposure: null, top_contributing_answers: [] },
      { state_id: "b", state_name: "B", risk_label: "Emerging", dollar_exposure: null, top_contributing_answers: [] },
    ]);
    expect(groups).toHaveLength(2);
  });
  it("ledger note: plain language, no dashes or semicolons", () => {
    expect(FRICTION_TAX_LEDGER_STANDALONE_NOTE).not.toMatch(/[—–;]|--/);
  });
'''

_CALL2 = '  it("on Call 2 failure, copies what the screen shows: referral chips over each section\'s answers", () => {\n'

EDITS["web/lib/output-text.test.ts"] = [
    (
        'import { buildResultsText, firstSentence, joinNames, buildCoreCluster, OHIO_NET_WORTH_CAVEAT } from "./output-text";\n',
        'import {\n'
        '  buildResultsText, firstSentence, joinNames, buildCoreCluster, OHIO_NET_WORTH_CAVEAT,\n'
        '  FRICTION_TAX_LEDGER_STANDALONE_NOTE, groupLedgerRows,\n'
        '} from "./output-text";\n',
    ),
    (
        '    expect(text).toContain("Primary asset domain: Governance Discipline");\n',
        '    // P1: the primary asset domain describes the lead condition, not the\n'
        '    // respondent, and is not shown.\n'
        '    expect(text).not.toContain("Primary asset domain");\n'
        '    expect(text).not.toContain("Governance Discipline");\n',
    ),
    (
        '      "The liability condition text.", "Primary asset domain:", "Resolution pathway:",\n',
        '      "The liability condition text.", "The asset resolution anchor text.", "Resolution pathway:",\n',
    ),
    (_CALL2, _GROUP_TESTS + _CALL2),
]

# ── Python tests ──────────────────────────────────────────────────────────────
_P3_P4_TESTS = (
    "# P3: receipt evidence ranks on *_liability only and respects the weight floor\n"
    "_q18e = next(o for o in L[\"Q18\"].answer_options if o.option_id == \"E\")\n"
    "check(\"P3: Q18-E in a non-hazard industry (asset-only signal) never ranks as problem evidence\",\n"
    "      _q18e.observation_text not in _top_observation_texts(\n"
    "          \"invisible_performance_management\", [{\"question_id\": \"Q18\", \"option_ids\": [\"E\"]}], INTAKE, limit=None))\n"
    "_all_ranked = _top_observation_texts(\"built_to_fail\", log, INTAKE, limit=None)\n"
    "_floor_ranked = _top_observation_texts(\"built_to_fail\", log, INTAKE, limit=None, min_weight=_RECEIPT_EVIDENCE_MIN_WEIGHT)\n"
    "check(\"P3: the weight floor only removes answers, never reorders them\",\n"
    "      _floor_ranked == [t for t in _all_ranked if t in _floor_ranked] and len(_floor_ranked) <= len(_all_ranked))\n"
    "check(\"P3: floor is 0.20\", _RECEIPT_EVIDENCE_MIN_WEIGHT == 0.20)\n"
    "\n"
    "# P4: the legal Total receipt describes the halving for any number of conditions\n"
    "_lg = [r for r in _legal_driving_factors(bd, [{\"state_id\": b[\"state_id\"], \"state_name\": b[\"state_id\"]} for b in bd],\n"
    "                                         INTAKE, []) if r[\"category\"] == \"Total\"]\n"
    f"check(\"P4: legal Total wording\", bool(_lg) and _lg[0][\"rationale\"] == {LEGAL_TOTAL_NEW_TEXT!r}, str(_lg))\n"
    "\n"
    "\n"
)
_SECTION9 = "# ── 9. Lead resolution family in both routing modes ─────────────────────────────\n"

EDITS["tools/test_phase1_report_data.py"] = [
    (
        'check("_pick_distinct reuses the top answer when all are used", _pick_distinct(["a"], {"a"}) == "a")\n',
        'check("_pick_distinct: every candidate used -> None, no repeat (P3)", _pick_distinct(["a"], {"a"}) is None)\n',
    ),
    (
        "for s, pick in zip(many, picked):\n"
        "    ranked = _top_observation_texts(s, log_p, INTAKE, limit=None)\n"
        "    if pick is None:\n"
        "        ok = ok and not ranked\n"
        "        continue\n"
        "    if any(t not in used for t in ranked) and pick in used:\n"
        "        ok = False\n"
        "    used.add(pick)\n"
        "check(\"friction receipts vary: a condition only repeats an answer when it has no unused alternative\", ok, str(picked))\n",
        "from engine.contract import _RECEIPT_EVIDENCE_MIN_WEIGHT\n"
        "for s, pick in zip(many, picked):\n"
        "    ranked = _top_observation_texts(s, log_p, INTAKE, limit=None, min_weight=_RECEIPT_EVIDENCE_MIN_WEIGHT)\n"
        "    if pick is None:\n"
        "        ok = ok and all(t in used for t in ranked)\n"
        "        continue\n"
        "    if pick in used or pick != next((t for t in ranked if t not in used), None):\n"
        "        ok = False\n"
        "    used.add(pick)\n"
        "check(\"friction receipts: never repeat an answer, and omit the line only when no unused answer clears the floor (P3)\",\n"
        "      ok, str(picked))\n",
    ),
    (_SECTION9, _P3_P4_TESTS + _SECTION9),
]
