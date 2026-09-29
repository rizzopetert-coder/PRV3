# Anchor/replacement data for tools/patch_report_presentation_p1_p4.py.
# Executed by that script with ts_concat, py_concat, LEDGER_NOTE and
# LEGAL_TOTAL_NEW_TEXT in scope. Each entry: (exact old text, new text).

EDITS = {}

# ── P3 + P4: engine/contract.py ───────────────────────────────────────────────
EDITS["engine/contract.py"] = [
    (
        "def _top_observation_texts(\n"
        "    state_id: str, answers_log: list, intake_data, limit: Optional[int] = 1,\n"
        ") -> list:\n",
        "# Receipt evidence (P3, Pete 2026-09-28): problem answers are ranked on\n"
        "# *_liability contributions only, so an answer's asset signal can never\n"
        "# make it look like evidence of a problem. A receipt quotes an answer only\n"
        "# when its salience-weighted weight reaches _RECEIPT_EVIDENCE_MIN_WEIGHT.\n"
        "# Calibration picks (175 profiles) cluster near 0.12 and near 0.6, with\n"
        "# 4% between 0.20 and 0.30, so 0.20 separates weak matches from real ones.\n"
        "_LIABILITY_FIELDS = tuple(f for f in DIMENSIONAL_FIELDS if f.endswith(\"_liability\"))\n"
        "_RECEIPT_EVIDENCE_MIN_WEIGHT = 0.20\n"
        "\n"
        "\n"
        "def _top_observation_texts(\n"
        "    state_id: str, answers_log: list, intake_data, limit: Optional[int] = 1,\n"
        "    min_weight: float = 0.0,\n"
        ") -> list:\n",
    ),
    (
        "    valences (PROBLEM_CONTEXT_VALENCES) are cited. limit=None returns the\n"
        "    full ranking.\n",
        "    valences (PROBLEM_CONTEXT_VALENCES) are cited, ranked on *_liability\n"
        "    contributions only. Answers below min_weight are left out. limit=None\n"
        "    returns the full ranking.\n",
    ),
    (
        "                for f in DIMENSIONAL_FIELDS\n"
        "            )\n"
        "            if weight > 0:\n"
        "                scored.append((weight, option.observation_text))\n",
        "                for f in _LIABILITY_FIELDS\n"
        "            )\n"
        "            if weight > 0 and weight >= min_weight:\n"
        "                scored.append((weight, option.observation_text))\n",
    ),
    (
        "    the same receipt list. Falls back to the top one when every candidate\n"
        "    is already used (reused rather than dropped). Records the pick.\"\"\"\n"
        "    if not ranked:\n"
        "        return None\n"
        "    pick = next((t for t in ranked if t not in used), ranked[0])\n"
        "    used.add(pick)\n"
        "    return pick\n",
        "    the same receipt list. None when every candidate is already used: the\n"
        "    receipt then carries no evidence line rather than a repeat (P3).\n"
        "    Records the pick.\"\"\"\n"
        "    pick = next((t for t in ranked if t not in used), None)\n"
        "    if pick is not None:\n"
        "        used.add(pick)\n"
        "    return pick\n",
    ),
    (
        "                _top_observation_texts(s[\"state_id\"], answers_log, intake_data, limit=None),\n",
        "                _top_observation_texts(\n"
        "                    s[\"state_id\"], answers_log, intake_data, limit=None,\n"
        "                    min_weight=_RECEIPT_EVIDENCE_MIN_WEIGHT,\n"
        "                ),\n",
    ),
    (
        "                _top_observation_texts(b[\"state_id\"], answers_log, intake_data, limit=None),\n",
        "                _top_observation_texts(\n"
        "                    b[\"state_id\"], answers_log, intake_data, limit=None,\n"
        "                    min_weight=_RECEIPT_EVIDENCE_MIN_WEIGHT,\n"
        "                ),\n",
    ),
    (
        '            "Within a category, overlapping exposures count at decreasing weight "\n'
        '            "(full, half, then a quarter). Categories are then added together.",\n',
        py_concat(LEGAL_TOTAL_NEW_TEXT, "            ") + ",\n",
    ),
]

# ── P1 + P2: web/lib/output-text.ts ───────────────────────────────────────────
EDITS["web/lib/output-text.ts"] = [
    (
        'import type { EvidenceReceipt, PrivateOutputPayload, SeverityTier, StateRef, TacticalSectionResult } from "@/lib/types";',
        'import type {\n'
        '  EvidenceReceipt, FrictionTaxLedgerEntry, PrivateOutputPayload, SeverityTier, StateRef, TacticalSectionResult,\n'
        '} from "@/lib/types";',
    ),
    (
        '  "result, and are not indicative of imprecision in the diagnosis.";\n',
        '  "result, and are not indicative of imprecision in the diagnosis.";\n'
        '\n'
        '// Ledger note (P2, Pete 2026-09-28): rows are standalone estimates and do\n'
        '// not add up to the friction tax total. Shared with PrivateOutput.tsx.\n'
        'export const FRICTION_TAX_LEDGER_STANDALONE_NOTE =\n'
        + ts_concat(LEDGER_NOTE) + ';\n'
        '\n'
        '// One ledger row per distinct evidence set (P2). Rows whose\n'
        '// top_contributing_answers are the same set (order ignored) merge into\n'
        '// one group that names every condition and carries the highest standalone\n'
        '// estimate among them. Rows with no evidence are never grouped: an empty\n'
        '// list is not shared evidence. Group order follows first appearance.\n'
        'export interface LedgerGroup {\n'
        '  conditions: Array<{ state_id: string; name: string; risk_label: SeverityTier }>;\n'
        '  dollar_exposure: FrictionTaxLedgerEntry["dollar_exposure"];\n'
        '  top_contributing_answers: string[];\n'
        '}\n'
        '\n'
        'function higherEstimate(\n'
        '  a: FrictionTaxLedgerEntry["dollar_exposure"],\n'
        '  b: FrictionTaxLedgerEntry["dollar_exposure"],\n'
        '): boolean {\n'
        '  if (!a) return false;\n'
        '  if (!b) return true;\n'
        '  return a.high > b.high || (a.high === b.high && a.low > b.low);\n'
        '}\n'
        '\n'
        'export function groupLedgerRows(\n'
        '  ledger: FrictionTaxLedgerEntry[],\n'
        '  nameById?: Map<string, string>,\n'
        '): LedgerGroup[] {\n'
        '  const groups: LedgerGroup[] = [];\n'
        '  const byEvidence = new Map<string, LedgerGroup>();\n'
        '  for (const row of ledger) {\n'
        '    const condition = {\n'
        '      state_id: row.state_id,\n'
        '      name: nameById?.get(row.state_id) ?? row.state_name,\n'
        '      risk_label: row.risk_label,\n'
        '    };\n'
        '    const key = row.top_contributing_answers.length > 0\n'
        '      ? JSON.stringify([...row.top_contributing_answers].sort())\n'
        '      : null;\n'
        '    const existing = key ? byEvidence.get(key) : undefined;\n'
        '    if (existing) {\n'
        '      existing.conditions.push(condition);\n'
        '      if (higherEstimate(row.dollar_exposure, existing.dollar_exposure)) {\n'
        '        existing.dollar_exposure = row.dollar_exposure;\n'
        '      }\n'
        '      continue;\n'
        '    }\n'
        '    const group: LedgerGroup = {\n'
        '      conditions: [condition],\n'
        '      dollar_exposure: row.dollar_exposure,\n'
        '      top_contributing_answers: row.top_contributing_answers,\n'
        '    };\n'
        '    groups.push(group);\n'
        '    if (key) byEvidence.set(key, group);\n'
        '  }\n'
        '  return groups;\n'
        '}\n',
    ),
    (
        "  // Asset block: primary asset domain, anchor text, where strength shows up\n"
        "  // (the sentence and the quoted evidence, never the bar values).\n"
        "  const ev = payload.asset_evidence;\n"
        "  if (payload.synthesis.asset_resolution_anchor_text || payload.primary_asset_domain || ev) {\n"
        "    const block: string[] = [];\n"
        "    if (payload.primary_asset_domain) block.push(`Primary asset domain: ${payload.primary_asset_domain}`);\n"
        "    if (payload.synthesis.asset_resolution_anchor_text) block.push(payload.synthesis.asset_resolution_anchor_text);\n"
        "    add(block);\n"
        "  }\n",
        "  // Asset block: anchor text, then where strength shows up (the sentence\n"
        "  // and the quoted evidence, never the bar values). The primary asset\n"
        "  // domain is a property of the lead condition, not of this respondent,\n"
        "  // so it is not shown (P1).\n"
        "  const ev = payload.asset_evidence;\n"
        "  if (payload.synthesis.asset_resolution_anchor_text) add([payload.synthesis.asset_resolution_anchor_text]);\n",
    ),
    (
        "    for (const row of ledger) {\n"
        "      const d = row.dollar_exposure;\n"
        "      const sym = d?.currency === \"USD\" ? \"$\" : \"\";\n"
        "      const amount = d\n"
        "        ? d.low === d.high\n"
        "          ? `Estimated exposure: ${sym}${d.low.toLocaleString()}`\n"
        "          : `${sym}${d.low.toLocaleString()} – ${sym}${d.high.toLocaleString()}`\n"
        "        : \"Estimate not available for this condition.\";\n"
        "      block.push(`— ${stateNameById.get(row.state_id) ?? row.state_name} (${row.risk_label}): ${amount}`);\n"
        "      for (const t of row.top_contributing_answers) block.push(`  ${t}`);\n"
        "    }\n"
        "    add(block);\n"
        "    add([FRICTION_TAX_LEDGER_FOOTNOTE]);\n",
        "    for (const group of groupLedgerRows(ledger, stateNameById)) {\n"
        "      const d = group.dollar_exposure;\n"
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
        "          : d!.low === d!.high ? `Estimated exposure: ${figure}` : figure;\n"
        "      const names = group.conditions.map((c) => `${c.name} (${c.risk_label})`).join(\", \");\n"
        "      block.push(`— ${names}: ${amount}`);\n"
        "      for (const t of group.top_contributing_answers) block.push(`  ${t}`);\n"
        "    }\n"
        "    add(block);\n"
        "    add([FRICTION_TAX_LEDGER_STANDALONE_NOTE]);\n"
        "    add([FRICTION_TAX_LEDGER_FOOTNOTE]);\n",
    ),
]
