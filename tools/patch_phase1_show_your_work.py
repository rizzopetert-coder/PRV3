"""
Phase 1 (report redesign), commit 1: show-your-work exports (Pete,
2026-09-27, Gemini-reviewed spec). Silent: the web passes
friction_tax_estimate and legal_tail_risk_exposure through whole, and no
UI reads driving_factors until Phase 3.

engine/friction_tax.py -- no existing math or return value changes:
  - compute_friction_tax(): the calibrated result gains an additive
    "components" key (payroll floor, org-type scalar, adjusted baseline,
    per-channel combined criterion scores, combined multiplier, breadth,
    multi-channel loading, severity scalar, state count). low/high unchanged.
  - NEW compute_legal_per_state_breakdown(): one entry per PRICED state
    (state_id, cluster, low, high, weight), priced by the same
    _single_state_legal_pricing() call and weighted exactly as
    compute_legal_compliance_exposure() aggregates (1.0 for N=1, else
    0.5**i within a cluster ranked by low, highest first, stable on ties),
    so sum(weight * low) == that function's low. A separate function, not a
    new key on compute_legal_compliance_exposure()'s result: 22 pinned tests
    compare that result dict exactly, and it stays byte-identical.

engine/contract.py:
  - EvidenceReceipt dicts {category, rationale, triggering_answer?}.
    triggering_answer is present ONLY when the condition has an authored
    observation_text answer (replay-and-rank, the same technique
    _build_friction_tax_ledger() uses). Never raw option_text.
  - friction_tax_estimate and legal_tail_risk_exposure gain driving_factors.

Usage:
    python tools/patch_phase1_show_your_work.py --dry-run
    python tools/patch_phase1_show_your_work.py --write
"""
import argparse
import pathlib
import sys

FT = pathlib.Path('engine/friction_tax.py')
CT = pathlib.Path('engine/contract.py')

LEGAL_BREAKDOWN_FN = '''

def compute_legal_per_state_breakdown(
    state_ids: list[str],
    org_size: int,
    industry: str,
    org_type: str,
    jurisdictions: Optional[list[str]] = None,
) -> list[dict]:
    """
    The per-state figures behind compute_legal_compliance_exposure()'s
    total (Phase 1 show-your-work). One entry per PRICED state:
    {"state_id", "cluster", "low", "high", "weight"}. Priced by the same
    _single_state_legal_pricing() call with the same inputs, and weighted
    exactly as that function aggregates: N=1 -> 1.0, otherwise 0.5**i within
    each cluster ranked by low (highest first, stable on ties like its own
    sort), so sum(weight * low) == its returned low. Unpriced and
    not-applicable states are excluded, same as the total.
    """
    headcount = org_size
    jurisdictions = jurisdictions or []
    org_size = resolve_headcount_bucket(org_size)
    per_state_ranges: dict[str, tuple[float, float]] = {}
    for sid in state_ids:
        result = _single_state_legal_pricing(
            sid, org_size, industry, org_type, headcount, jurisdictions
        )
        if result.status == LegalPricingStatus.PRICED:
            per_state_ranges[sid] = result.dollar_range

    if len(per_state_ranges) == 1:
        (sid, (low, high)), = per_state_ranges.items()
        return [{
            "state_id": sid, "cluster": LEGAL_COMPLIANCE_CLUSTER[sid],
            "low": round(low, 2), "high": round(high, 2), "weight": 1.0,
        }]

    breakdown: list[dict] = []
    by_cluster_ids: dict[int, list[str]] = {}
    for sid in per_state_ranges:
        by_cluster_ids.setdefault(LEGAL_COMPLIANCE_CLUSTER[sid], []).append(sid)
    for cluster, sids in by_cluster_ids.items():
        ranked = sorted(sids, key=lambda s: per_state_ranges[s][0], reverse=True)
        for i, sid in enumerate(ranked):
            low, high = per_state_ranges[sid]
            breakdown.append({
                "state_id": sid, "cluster": cluster,
                "low": round(low, 2), "high": round(high, 2), "weight": 0.5 ** i,
            })
    return breakdown
'''

FT_EDITS = [
    ('        "severity_scalar": severity_scalar,\n'
     '        "calibration_complete": True,\n'
     '    }\n',
     '        "severity_scalar": severity_scalar,\n'
     '        "calibration_complete": True,\n'
     '        # Intermediate figures behind low/high (Phase 1 show-your-work),\n'
     '        # additive: nothing above changed, contract.py turns these into\n'
     '        # driving_factors receipts.\n'
     '        "components": {\n'
     '            "payroll_floor":                  payroll_floor,\n'
     '            "org_type_scalar":                org_type_scalar,\n'
     '            "adjusted_baseline":              adjusted_baseline,\n'
     '            "combined_criterion_scores":      dict(combined_criterion_scores),\n'
     '            "combined_multiplier":            combined_multiplier,\n'
     '            "breadth":                        breadth,\n'
     '            "multi_channel_severity_loading": multi_channel_severity_loading,\n'
     '            "severity_scalar":                severity_scalar,\n'
     '            "state_count":                    len(state_entries),\n'
     '        },\n'
     '    }\n',
     'friction components'),
]

CT_EDITS = [
    ('from engine.friction_tax import compute_friction_tax, compute_legal_compliance_exposure\n',
     'from engine.friction_tax import (\n'
     '    compute_friction_tax, compute_legal_compliance_exposure,\n'
     '    compute_legal_per_state_breakdown, STATE_MULTIPLIERS,\n'
     ')\n',
     'imports'),
    ('def assemble_output(\n',
     '# ── Phase 1 show-your-work: evidence receipts ──────────────────────────────\n'
     '#\n'
     '# EvidenceReceipt: {"category": str, "rationale": str, "triggering_answer"?: str}.\n'
     '# triggering_answer is included ONLY when an authored observation_text\n'
     '# exists for the condition. It is never padded with raw option_text.\n'
     '\n'
     '_LEGAL_CLUSTER_LABELS = {\n'
     '    1: "Individual employment claims",\n'
     '    2: "Class or systemic discrimination",\n'
     '    3: "Wage and hour",\n'
     '    4: "Whistleblower and retaliation",\n'
     '    5: "Workplace safety and regulatory",\n'
     '}\n'
     '\n'
     '_FRICTION_CHANNEL_LABELS = {\n'
     '    "turnover":         "turnover",\n'
     '    "productivity":     "lost productivity",\n'
     '    "decision_quality": "weaker decisions",\n'
     '}\n'
     '\n'
     '\n'
     'def _usd(value: float) -> str:\n'
     '    return f"${value:,.0f}"\n'
     '\n'
     '\n'
     'def _join_words(items: list) -> str:\n'
     '    if len(items) <= 1:\n'
     '        return "".join(items)\n'
     '    if len(items) == 2:\n'
     '        return f"{items[0]} and {items[1]}"\n'
     '    return ", ".join(items[:-1]) + f", and {items[-1]}"\n'
     '\n'
     '\n'
     'def _top_observation_texts(\n'
     '    state_id: str, answers_log: list, intake_data, limit: int = 1,\n'
     ') -> list:\n'
     '    """\n'
     '    The respondent\'s own answers most relevant to state_id, as authored\n'
     '    observation_text only. Same replay-and-rank technique as\n'
     '    _build_friction_tax_ledger() (a scratch AccumulationSession per\n'
     '    selected option, salience-weighted against SALIENCE_PROFILES), kept\n'
     '    separate rather than refactoring the ledger. Unauthored options are\n'
     '    skipped, never replaced with raw option_text.\n'
     '    """\n'
     '    salience = SALIENCE_PROFILES.get(state_id)\n'
     '    if not salience or not answers_log:\n'
     '        return []\n'
     '    scored: list = []\n'
     '    for entry in answers_log:\n'
     '        if not isinstance(entry, dict):\n'
     '            continue\n'
     '        question = QUESTION_LIBRARY.get(entry.get("question_id"))\n'
     '        option_ids = entry.get("option_ids")\n'
     '        if question is None or not isinstance(option_ids, list):\n'
     '            continue\n'
     '        for option_id in option_ids:\n'
     '            option = next((o for o in question.answer_options if o.option_id == option_id), None)\n'
     '            if option is None or not option.observation_text:\n'
     '                continue\n'
     '            scratch = AccumulationSession()\n'
     '            accumulate_answer(scratch, option, intake_data, entry.get("question_id"))\n'
     '            weight = sum(\n'
     '                scratch.accumulated_vector.get(f, 0.0) * salience.get(f, 0.0)\n'
     '                for f in DIMENSIONAL_FIELDS\n'
     '            )\n'
     '            if weight > 0:\n'
     '                scored.append((weight, option.observation_text))\n'
     '    scored.sort(key=lambda pair: pair[0], reverse=True)\n'
     '    texts: list = []\n'
     '    for _, text in scored:\n'
     '        if text not in texts:\n'
     '            texts.append(text)\n'
     '        if len(texts) == limit:\n'
     '            break\n'
     '    return texts\n'
     '\n'
     '\n'
     'def _receipt(category: str, rationale: str, triggering_answer: Optional[str] = None) -> dict:\n'
     '    receipt = {"category": category, "rationale": rationale}\n'
     '    if triggering_answer:\n'
     '        receipt["triggering_answer"] = triggering_answer\n'
     '    return receipt\n'
     '\n'
     '\n'
     'def _friction_driving_factors(\n'
     '    friction_result: dict, identified_states: list, severity_tier: str,\n'
     '    intake_data, answers_log: list,\n'
     ') -> list:\n'
     '    """The friction tax math, step by step, from compute_friction_tax()\'s\n'
     '    own intermediate figures. [] when uncalibrated."""\n'
     '    c = friction_result.get("components")\n'
     '    if not friction_result.get("calibration_complete") or not c:\n'
     '        return []\n'
     '    if c["org_type_scalar"] == 1.0:\n'
     '        org_type_text = f"No adjustment for {intake_data.org_type} organizations."\n'
     '    else:\n'
     '        org_type_text = (\n'
     '            f"Adjusted by a factor of {c[\'org_type_scalar\']:.2f} for {intake_data.org_type} "\n'
     '            f"organizations, giving a baseline of {_usd(c[\'adjusted_baseline\'])}."\n'
     '        )\n'
     '    receipts = [\n'
     '        _receipt(\n'
     '            "Payroll baseline",\n'
     '            f"Estimated annual payroll for a {friction_result[\'org_size_label\']} person "\n'
     '            f"{intake_data.industry} organization: {_usd(c[\'payroll_floor\'])}.",\n'
     '        ),\n'
     '        _receipt("Organization type", org_type_text),\n'
     '    ]\n'
     '    for s in identified_states:\n'
     '        entry = STATE_MULTIPLIERS.get(s["state_id"])\n'
     '        if entry is None:\n'
     '            continue\n'
     '        channels = [\n'
     '            label for key, label in _FRICTION_CHANNEL_LABELS.items()\n'
     '            if entry.criteria[key].score > 0\n'
     '        ]\n'
     '        if not channels:\n'
     '            continue\n'
     '        observed = _top_observation_texts(s["state_id"], answers_log, intake_data)\n'
     '        receipts.append(_receipt(\n'
     '            "Condition",\n'
     '            f"{s[\'state_name\']} adds cost through {_join_words(channels)}.",\n'
     '            observed[0] if observed else None,\n'
     '        ))\n'
     '    share = (\n'
     '        f"Together these conditions put {c[\'combined_multiplier\']:.1%} of that baseline at risk"\n'
     '    )\n'
     '    if c["multi_channel_severity_loading"] > 1.0:\n'
     '        share += (\n'
     '            f", raised by a factor of {c[\'multi_channel_severity_loading\']:.2f} because "\n'
     '            f"the cost spreads across {c[\'breadth\']} channels"\n'
     '        )\n'
     '    receipts.append(_receipt("Share of payroll at risk", share + "."))\n'
     '    receipts.append(_receipt(\n'
     '        "Severity",\n'
     '        f"Multiplied by {c[\'severity_scalar\']:.2f} for {severity_tier} severity.",\n'
     '    ))\n'
     '    receipts.append(_receipt(\n'
     '        "Estimate",\n'
     '        f"Low estimate {_usd(friction_result[\'low\'])}. The high estimate is 1.4 times "\n'
     '        f"the low, {_usd(friction_result[\'high\'])}.",\n'
     '    ))\n'
     '    return receipts\n'
     '\n'
     '\n'
     'def _legal_driving_factors(\n'
     '    breakdown: list, identified_states: list, intake_data, answers_log: list,\n'
     ') -> list:\n'
     '    """One receipt per priced condition from\n'
     '    compute_legal_per_state_breakdown(), plus how they combine. [] when\n'
     '    nothing was priced."""\n'
     '    if not breakdown:\n'
     '        return []\n'
     '    names = {s["state_id"]: s["state_name"] for s in identified_states}\n'
     '    receipts = []\n'
     '    for b in breakdown:\n'
     '        name = names.get(b["state_id"], b["state_id"])\n'
     '        amount = (\n'
     '            _usd(b["low"]) if b["low"] == b["high"]\n'
     '            else f"{_usd(b[\'low\'])} to {_usd(b[\'high\'])}"\n'
     '        )\n'
     '        rationale = f"{name}: {amount}"\n'
     '        if b["weight"] < 1.0:\n'
     '            rationale += (\n'
     '                f", counted at {b[\'weight\']:.0%} because a larger exposure in the "\n'
     '                "same category is already included"\n'
     '            )\n'
     '        observed = _top_observation_texts(b["state_id"], answers_log, intake_data)\n'
     '        receipts.append(_receipt(\n'
     '            _LEGAL_CLUSTER_LABELS.get(b["cluster"], "Legal exposure"),\n'
     '            rationale + ".",\n'
     '            observed[0] if observed else None,\n'
     '        ))\n'
     '    if len(breakdown) > 1:\n'
     '        receipts.append(_receipt(\n'
     '            "Total",\n'
     '            "Within a category, overlapping exposures count at decreasing weight "\n'
     '            "(full, half, then a quarter). Categories are then added together.",\n'
     '        ))\n'
     '    return receipts\n'
     '\n'
     '\n'
     'def assemble_output(\n',
     'receipt helpers'),
    ('    friction_tax_estimate = (\n'
     '        {\n'
     '            "low":      friction_tax_result["low"],\n'
     '            "high":     friction_tax_result["high"],\n'
     '            "currency": friction_tax_result["currency"],\n'
     '        }\n',
     '    friction_tax_estimate = (\n'
     '        {\n'
     '            "low":      friction_tax_result["low"],\n'
     '            "high":     friction_tax_result["high"],\n'
     '            "currency": friction_tax_result["currency"],\n'
     '            "driving_factors": _friction_driving_factors(\n'
     '                friction_tax_result, identified_states, lead_severity_tier,\n'
     '                session.intake, answers_log or [],\n'
     '            ),\n'
     '        }\n',
     'friction driving_factors'),
    ('            "specific_caveat": _SPECIFIC_CAVEAT_TEXT.get(legal_result["specific_caveat_jurisdiction"]),\n'
     '        }\n',
     '            "specific_caveat": _SPECIFIC_CAVEAT_TEXT.get(legal_result["specific_caveat_jurisdiction"]),\n'
     '            "driving_factors": _legal_driving_factors(\n'
     '                compute_legal_per_state_breakdown(\n'
     '                    state_ids=[s["state_id"] for s in identified_states],\n'
     '                    org_size=session.intake.headcount,\n'
     '                    industry=session.intake.industry,\n'
     '                    org_type=session.intake.org_type,\n'
     '                    jurisdictions=session.intake.jurisdictions,\n'
     '                ),\n'
     '                identified_states, session.intake, answers_log or [],\n'
     '            ),\n'
     '        }\n',
     'legal driving_factors'),
]


def apply(path, edits):
    t = path.read_text(encoding='utf-8')
    for old, new, label in edits:
        n = t.count(old)
        if n != 1:
            print(f'ERROR: {path} :: {label} anchor found {n} times.', file=sys.stderr)
            sys.exit(1)
        t = t.replace(old, new, 1)
        print(f'[{path} :: {label}] OK')
    return t


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    ft = apply(FT, FT_EDITS)
    if 'def compute_legal_per_state_breakdown' in ft:
        print('ERROR: compute_legal_per_state_breakdown already exists.', file=sys.stderr)
        sys.exit(1)
    ft = ft.rstrip('\n') + '\n' + LEGAL_BREAKDOWN_FN
    print(f'[{FT} :: compute_legal_per_state_breakdown appended] OK')
    ct = apply(CT, CT_EDITS)
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    FT.write_text(ft, encoding='utf-8')
    CT.write_text(ct, encoding='utf-8')
    print(f'WROTE: {FT}, {CT}')


if __name__ == '__main__':
    main()
