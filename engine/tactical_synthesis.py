"""
PRV3 Engine -- Tactical & Compliance synthesis (Phase 1 report redesign,
Call 2). Gemini-reviewed spec, Pete-approved section names (2026-09-27).

Two parts:
  build_tactical_summary(answers_log)  deterministic pre-aggregation of the
      TC-* answers: bucketed by answer position (A solid, B minor gap,
      C/D severe gap or unknown), grouped by section. No LLM.
  synthesize_tactical(summary)  one LLM call that writes a short finding for
      each section with gaps, from the pre-aggregation ONLY (no core
      diagnostic data, no intake). Any failure returns ([], False, error):
      it never raises, never touches Call 1, and never triggers the core
      synthesis fallback.

Brand-agnostic: runs whenever a session has TC-* answers.
"""
from __future__ import annotations

import json
import os
import re
from typing import Optional

from engine.data.questions import QUESTION_LIBRARY
from engine.narrative import _enforce_house_punctuation

# (question-id prefix, question_set_id, display name). Order = report order,
# the same 10-section order as web/data/tactical-question-meta.ts.
TACTICAL_SECTIONS: tuple = (
    ("TC-HRPOL", "TC-HR_POLICIES",       "HR Practices & Policies"),
    ("TC-HIRE",  "TC-HIRING_ONBOARDING", "Hiring & Onboarding"),
    ("TC-PAY",   "TC-PAYROLL",           "Payroll & Wage-Hour"),
    ("TC-COMPC", "TC-COMP_COMPLIANCE",   "Compensation Compliance"),
    ("TC-BEN",   "TC-BENEFITS",          "Benefits Compliance"),
    ("TC-LEAVE", "TC-LEAVE_MANAGEMENT",  "Leave Management"),
    ("TC-SAFE",  "TC-SAFETY",            "Workplace Safety"),
    ("TC-REC",   "TC-RECORDS",           "Records & Privacy"),
    ("TC-TECH",  "TC-TECHNOLOGY",        "HR Systems & Data"),
    ("TC-PERF",  "TC-PERFORMANCE_MGMT",  "Performance Management"),
)
_SECTION_BY_PREFIX = {prefix: (sid, name) for prefix, sid, name in TACTICAL_SECTIONS}

# Answer-position schema, verified against all 40 TC-* questions: A is always
# the solid answer, D is either a missing process or "not sure".
_GAP_BY_OPTION = {"A": None, "B": "minor", "C": "severe", "D": "severe"}


def _debug_fail(call: str) -> bool:
    """Non-production test hook for the live forced-failure check."""
    return (
        os.environ.get("VERCEL_ENV") != "production"
        and os.environ.get("PRV3_DEBUG_FAIL_CALL") == call
    )


def build_tactical_summary(answers_log: list) -> dict:
    """
    Deterministic pre-aggregation of TC-* answers, keyed by question_set_id
    in report order. Each section: section_id, section_name, total,
    flagged_count, flagged_items [{question_id, option_id, severity,
    question_text, answer_text}]. answer_text is prompt input only and is
    stripped before the findings leave the engine. {} when the session has
    no TC-* answers.
    """
    buckets: dict = {}
    for entry in answers_log or []:
        if not isinstance(entry, dict):
            continue
        qid = entry.get("question_id") or ""
        if not qid.startswith("TC-"):
            continue
        section = _SECTION_BY_PREFIX.get(qid.rsplit("-", 1)[0])
        question = QUESTION_LIBRARY.get(qid)
        option_ids = entry.get("option_ids")
        if section is None or question is None or not isinstance(option_ids, list) or not option_ids:
            continue
        option = next((o for o in question.answer_options if o.option_id == option_ids[0]), None)
        if option is None:
            continue
        sid, name = section
        b = buckets.setdefault(sid, {
            "section_id": sid, "section_name": name,
            "total": 0, "flagged_count": 0, "flagged_items": [],
        })
        b["total"] += 1
        gap = _GAP_BY_OPTION.get(option.option_id)
        if gap is not None:
            b["flagged_count"] += 1
            b["flagged_items"].append({
                "question_id":   qid,
                "option_id":     option.option_id,
                "severity":      gap,
                "question_text": question.question_text,
                "answer_text":   option.option_text,
            })
    return {sid: buckets[sid] for _, sid, _ in TACTICAL_SECTIONS if sid in buckets}


def tactical_totals(summary: dict) -> dict:
    """Raw counts across all sections, for Call 3."""
    sections = list(summary.values())
    return {
        "flagged_count":      sum(s["flagged_count"] for s in sections),
        "total_count":        sum(s["total"] for s in sections),
        "severe_count":       sum(1 for s in sections for i in s["flagged_items"] if i["severity"] == "severe"),
        "sections_with_gaps": sum(1 for s in sections if s["flagged_count"]),
        "sections_total":     len(sections),
    }


TACTICAL_SYNTHESIS_SYSTEM_PROMPT: str = """\
You write short findings for the HR practices and compliance review section of \
an organizational diagnostic report. The reader is the leader of the \
organization. They answered questions about how their HR practices actually \
run, and some answers show gaps.

For each section you are given, write 1 to 2 sentences that distill what the \
answers show and the practical risk that gap creates, for example exposure in \
an audit, a claim, or a dispute. Base every finding only on the answers \
provided.

RULES
- Plain, direct language, the way a trusted advisor would say it. No jargon.
- Do not cite specific laws, statutes, penalty amounts, or deadlines.
- Do not recommend vendors, products, or services, and do not name any firm.
- Do not use bullet points. Never use em dashes, en dashes used as dashes, \
double hyphens, or semicolons.
- Output strict JSON only: an object mapping each section_id you were given to \
its finding text. No preamble, no markdown.
"""


def _build_tactical_prompt(flagged_sections: list) -> str:
    lines = ["Sections with gaps:"]
    for s in flagged_sections:
        lines.append(f"\nsection_id: {s['section_id']}")
        lines.append(f"section: {s['section_name']} ({s['flagged_count']} of {s['total']} answers show a gap)")
        for item in s["flagged_items"]:
            label = "significant gap or unknown" if item["severity"] == "severe" else "minor gap"
            lines.append(f"- Q: {item['question_text']}")
            lines.append(f"  A: {item['answer_text']} [{label}]")
    return "\n".join(lines)


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def synthesize_tactical(
    summary: dict,
    model: str = "claude-sonnet-5",
    client=None,
    timeout: float = 30.0,
) -> tuple:
    """
    Call 2. timeout 30s (2026-09-28): about 2x the worst measured latency
    (14.4s with all 40 TC answers flagged), which crowded the old 15s. Returns (findings, ok, error). findings is a TacticalFinding list
    for every answered section (clean sections get synthesis_text ""),
    flagged_items without answer_text. On any failure: ([], False, error).
    A session whose answers show no gaps at all makes no LLM call.
    """
    def _findings(texts: dict) -> list:
        return [
            {
                "section_id":     s["section_id"],
                "section_name":   s["section_name"],
                "flagged_count":  s["flagged_count"],
                "total_count":    s["total"],
                "synthesis_text": texts.get(s["section_id"], ""),
                "flagged_items":  [
                    {k: v for k, v in item.items() if k != "answer_text"}
                    for item in s["flagged_items"]
                ],
            }
            for s in summary.values()
        ]

    if not summary:
        return [], False, "no tactical answers"
    flagged = [s for s in summary.values() if s["flagged_count"]]
    if not flagged:
        return _findings({}), True, ""

    try:
        if _debug_fail("tactical"):
            raise RuntimeError("PRV3_DEBUG_FAIL_CALL=tactical (non-production test hook)")
        if client is None:
            import anthropic as _anthropic
            client = _anthropic.Anthropic(max_retries=0)
        message = client.messages.create(
            model=model,
            max_tokens=1200,
            thinking={"type": "disabled"},
            system=TACTICAL_SYNTHESIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_tactical_prompt(flagged)}],
            timeout=timeout,
        )
        raw = message.content[0].text
        match = _JSON_OBJECT_RE.search(raw)
        data = json.loads(match.group(0) if match else raw)
        texts = {
            s["section_id"]: _enforce_house_punctuation(str(data.get(s["section_id"], "")).strip())
            for s in flagged
        }
        missing = [sid for sid, text in texts.items() if not text]
        if missing:
            return [], False, f"missing findings for {missing}"
        return _findings(texts), True, ""
    except Exception as e:  # never crash the session
        return [], False, f"tactical synthesis error: {e}"
