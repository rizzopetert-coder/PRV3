"""
Friction tax rebuild, Stage 4, engine/contract.py (spec Section 6 and the Phase 0
addendum R5).

  - friction_tax_estimate is the two-channel estimate straight from
    compute_friction_tax() (shape in the spec, Section 6), null when uncalibrated.
  - friction_receipts is a new sibling of friction_tax_estimate in private_output,
    so receipts render when the estimate is null (for example only paper_shield).
    The receipts moved out of the estimate, which no longer carries driving_factors.
  - The ledger drops dollar_exposure and carries channels (the channels each state
    switches on), and no longer calls compute_friction_tax.
  - service_cost_comparison drops inaction_cost_low and inaction_cost_high with no
    replacement (R5). The two lines read from friction_tax_estimate and
    legal_tail_risk_exposure directly.

Usage: python tools/patch_stage4_contract.py --dry-run | --write
"""
import sys
from pathlib import Path

CT = Path(__file__).resolve().parents[1] / "engine/contract.py"

NEW_RECEIPTS = '''def _pct(value: float) -> str:
    """A percent of payroll to at most 2 decimals, trailing zeros dropped."""
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _friction_receipts(
    friction_result: dict, identified_states: list, intake_data, answers_log: list,
) -> list:
    """The friction figure's receipts, step by step, from compute_friction_tax()'s
    own result: payroll, each dollar channel with its cited inputs, the conditions
    that switch channels on (each quoting the respondent's own evidence), the
    decision-time context with no dollar value, and the total. Receipts render
    even when the estimate is null, so a state set with no dollar channel (only
    paper_shield) still gets its condition and decision-time receipts. At the
    intake cap no receipt carries a dollar figure and the cap is stated. [] when
    nothing applies."""
    receipts: list = []
    estimate = friction_result.get("estimate")
    withheld = friction_result.get("amounts_withheld")
    channels = {}
    if estimate:
        base = estimate["typical_baseline"]
        channels = {c["channel"]: c for c in base["channels"]}
        if withheld:
            receipts.append(_receipt(
                "Payroll baseline",
                "Intake counts organizations up to 1,000 employees and prices any larger "
                "organization as 1,000. Dollar amounts are withheld for that reason and "
                "only percent of payroll is shown.",
            ))
        else:
            receipts.append(_receipt(
                "Payroll baseline",
                f"Estimated annual payroll for {friction_result['headcount']:,.0f} "
                f"{intake_data.industry} employees at the {intake_data.industry} average "
                f"wage of {_usd(friction_result['wage'])}: {_usd(friction_result['payroll'])}.",
            ))

    def with_amount(text: str, channel: dict) -> str:
        if channel["amount"] is None:
            return text + "."
        return text + f", about {_usd(channel['amount'])} a year."

    if "engagement" in channels:
        c = channels["engagement"]
        receipts.append(_receipt(
            "Engagement",
            with_amount(
                f"This is {FRICTION_FRAMING_ENGAGEMENT_GAP}. Gallup finds "
                f"{ENGAGEMENT_US:.0%} of U.S. employees engaged against an average of "
                f"{ENGAGEMENT_BEST_PRACTICE:.0%} in its best-practice organizations, and "
                f"each employee below that level costs about {NOT_ENGAGED_COST_SHARE:.0%} "
                f"of salary. That is {_pct(c['percent_of_payroll'])}% of payroll", c,
            ),
        ))
    if "turnover" in channels:
        c = channels["turnover"]
        receipts.append(_receipt(
            "Turnover",
            with_amount(
                f"{friction_result['annual_quit_rate_percent']:.1f}% of employees in "
                f"{intake_data.industry} leave each year (BLS JOLTS, 2025). Gallup finds "
                f"{TURNOVER_PREVENTABLE_SHARE:.0%} of voluntary exits are preventable, and "
                f"Work Institute puts the cost of each exit at about "
                f"{TURNOVER_COST_SHARE:.1%} of salary. That is "
                f"{_pct(c['percent_of_payroll'])}% of payroll", c,
            ),
        ))
    used_answers: set = set()
    for s in identified_states:
        entry = STATE_CRITERIA.get(s["state_id"])
        if entry is None:
            continue
        labels = [
            label for key, label in _FRICTION_CHANNEL_LABELS.items()
            if getattr(entry, key) > 0
        ]
        if not labels:
            continue
        receipts.append(_receipt(
            "Condition",
            f"{s['state_name']} adds cost through {_join_words(labels)}.",
            _pick_distinct(
                _top_observation_texts(
                    s["state_id"], answers_log, intake_data, limit=None,
                    min_weight=_RECEIPT_EVIDENCE_MIN_WEIGHT,
                ),
                used_answers,
            ),
        ))
    if friction_result.get("decision_time_receipt"):
        receipts.append(_receipt(
            "Decision time",
            f"Managers spend about {DECISION_TIME_SHARE_OF_TIME:.0%} of their time on "
            f"decisions and about {DECISION_TIME_INEFFECTIVE_SHARE:.0%} of that time is used "
            f"ineffectively (McKinsey, 2019). No dollar value is applied. The survey sample "
            f"skews toward senior leaders at larger companies than most clients, so this is "
            f"context and not a priced channel.",
        ))
    if estimate:
        total = estimate["typical_baseline"]["total"]
        text = (
            f"Together, {FRICTION_FRAMING_TOTAL} is "
            f"{_pct(total['percent_of_payroll'])}% of payroll"
        )
        text += "." if total["amount"] is None else f", about {_usd(total['amount'])} a year."
        receipts.append(_receipt("Total", text))
    return receipts
'''

# (old, new) pairs, each old must occur exactly once
EDITS = [
    ("""from engine.friction_tax import (
    compute_friction_tax, compute_legal_compliance_exposure,
    compute_legal_per_state_breakdown,
)
""", """from engine.friction_tax import (
    compute_friction_tax, compute_legal_compliance_exposure,
    compute_legal_per_state_breakdown,
    ENGAGEMENT_BEST_PRACTICE, ENGAGEMENT_US, NOT_ENGAGED_COST_SHARE,
    TURNOVER_PREVENTABLE_SHARE, TURNOVER_COST_SHARE,
    DECISION_TIME_SHARE_OF_TIME, DECISION_TIME_INEFFECTIVE_SHARE,
    FRICTION_FRAMING_TOTAL, FRICTION_FRAMING_ENGAGEMENT_GAP,
)
"""),
    ("""    Per-condition/state friction tax ledger row: risk label, dollar
    exposure, and a ranked top-contributing-answers list -- one row per
    entry in identified_states, in that same order.
""", """    Per-condition/state friction tax ledger row: risk label, the channels
    the state switches on, and a ranked top-contributing-answers list -- one
    row per entry in identified_states, in that same order.
"""),
    ("""    dollar_exposure reuses compute_friction_tax() called with a single-
    element state_ids list, using THIS state's own tier (not the lead
    state's, unlike the aggregate friction_tax_estimate above) -- with
    exactly one identified state, compute_friction_tax()'s own combined-
    criterion aggregation collapses to that state's untouched criterion
    scores (confirmed by that function's own docstring and
    tools/test_friction_tax.py's continuity assertions), so this is a
    real per-state standalone estimate, not an approximation. None when
    that single-state call isn't calibration_complete (same null
    contract as friction_tax_estimate itself).
""", """    channels lists which friction channels this state switches on
    (engagement when its productivity score is above 0, turnover when its
    turnover score is above 0, decision_time when its decision_quality
    score is above 0), read from engine/data/state_criteria.py. No dollar
    figure is carried per state (friction tax rebuild, Stage 4).
"""),
    ("""        friction_result = compute_friction_tax(
            state_ids=[state_id],
            severity_tier=risk_label,
            org_size=intake_data.headcount,
            industry=intake_data.industry,
            org_type=intake_data.org_type,
        )
        dollar_exposure = (
            {
                "low":      friction_result["low"],
                "high":     friction_result["high"],
                "currency": friction_result["currency"],
            }
            if friction_result["calibration_complete"]
            else None
        )
""", """        criteria = STATE_CRITERIA.get(state_id)
        channels = [
            name for name, field in (
                ("engagement", "productivity"), ("turnover", "turnover"),
                ("decision_time", "decision_quality"),
            )
            if criteria is not None and getattr(criteria, field) > 0
        ]
"""),
    ("""            "dollar_exposure":          dollar_exposure,
""", """            "channels":                 channels,
"""),
    ("""def _friction_driving_factors(
    friction_result: dict, identified_states: list, severity_tier: str,
    intake_data, answers_log: list,
) -> list:
    \"\"\"The friction tax math, step by step, from compute_friction_tax()'s
    own intermediate figures. [] when uncalibrated.\"\"\"
""", "@@REPLACE_FRICTION_RECEIPTS@@"),
    ("""    friction_tax_result = compute_friction_tax(
        state_ids=[s["state_id"] for s in identified_states],
        # Checkpoint 3: lead_severity_tier, not sev.tier. compute_friction_tax()
        # itself is unchanged (out of scope, not one of this checkpoint's
        # named files) -- it takes one severity_tier scalar applied across
        # the full state_ids list, so the lead state's own tier is the only
        # per-state value this single-scalar call site can meaningfully use.
        severity_tier=lead_severity_tier,
        org_size=session.intake.headcount,
        industry=session.intake.industry,
        org_type=session.intake.org_type,
    )
    friction_tax_estimate = (
        {
            "low":      friction_tax_result["low"],
            "high":     friction_tax_result["high"],
            "currency": friction_tax_result["currency"],
            "driving_factors": _friction_driving_factors(
                friction_tax_result, identified_states, lead_severity_tier,
                session.intake, answers_log or [],
            ),
        }
        if friction_tax_result["calibration_complete"]
        else None
    )
""", """    # Two-channel friction estimate (Stage 4): identified states only switch
    # channels on, severity is not an input. Receipts are a sibling field so
    # they exist even when the estimate is null.
    friction_tax_result = compute_friction_tax(
        state_ids=[s["state_id"] for s in identified_states],
        org_size=session.intake.headcount,
        industry=session.intake.industry,
    )
    friction_tax_estimate = friction_tax_result["estimate"]
    friction_receipts = _friction_receipts(
        friction_tax_result, identified_states, session.intake, answers_log or [],
    )
"""),
    ("""    # service_cost_comparison (Phase 1, Pete: ship with nulls). Inaction
    # cost counts friction tax and legal exposure only where each is priced.
    _cost_parts = [
        (friction_tax_estimate["low"], friction_tax_estimate["high"])
        if friction_tax_estimate else None,
        (legal_tail_risk_exposure["low"], legal_tail_risk_exposure["high"])
        if legal_tail_risk_exposure and legal_tail_risk_exposure["low"] is not None else None,
    ]
    _cost_parts = [p for p in _cost_parts if p is not None]
""", """    # service_cost_comparison (Phase 1, Pete: ship with nulls). R5: no inaction
    # cost fields. The typical-loss line reads friction_tax_estimate and the
    # tail-risk line reads legal_tail_risk_exposure, never a sum.
"""),
    ("""            "inaction_cost_low":     round(sum(p[0] for p in _cost_parts), 2) if _cost_parts else None,
            "inaction_cost_high":    round(sum(p[1] for p in _cost_parts), 2) if _cost_parts else None,
""", ""),
    ("""        "friction_tax_ledger":     friction_tax_ledger,
        "legal_tail_risk_exposure": legal_tail_risk_exposure,
""", """        "friction_tax_ledger":     friction_tax_ledger,
        "friction_receipts":       friction_receipts,
        "legal_tail_risk_exposure": legal_tail_risk_exposure,
"""),
    ("""    "friction_tax_ledger", "legal_tail_risk_exposure", "cascade_risk",
""", """    "friction_tax_ledger", "friction_receipts", "legal_tail_risk_exposure", "cascade_risk",
"""),
]


def transform(t: str) -> str:
    for old, new in EDITS:
        assert t.count(old) == 1, f"anchor count {t.count(old)}: {old[:70]!r}"
        if new == "@@REPLACE_FRICTION_RECEIPTS@@":
            # replace the whole old function through its closing return
            i = t.index(old)
            j = t.index("def _legal_driving_factors(", i)
            t = t[:i] + NEW_RECEIPTS + "\n\n" + t[j:]
        else:
            t = t.replace(old, new)
    return t


if __name__ == "__main__":
    raw = CT.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = transform(raw.replace("\r\n", "\n"))
    print(f"contract.py: {len(raw.splitlines())} -> {len(t.splitlines())} lines ({'CRLF' if crlf else 'LF'})")
    if "--write" in sys.argv:
        CT.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
        print("WROTE")
    else:
        print("DRY RUN")
