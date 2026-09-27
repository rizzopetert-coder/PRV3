"""
PRV3 Engine -- Executive summary (Phase 1 report redesign, Call 3).
Gemini-reviewed spec (2026-09-27).

One LLM call, run AFTER Call 1 (core synthesis) and Call 2 (tactical
synthesis) and only when both succeeded. Input is deliberately narrow: Call
1's liability_condition_text plus the raw tactical counts. Output is a 2-3
sentence summary bridging the organizational finding and the HR practices
review. Any failure returns ("", False, error): the UI omits the section, and
nothing else in the result changes.
"""
from __future__ import annotations

import os

from engine.narrative import _enforce_house_punctuation


def _debug_fail(call: str) -> bool:
    """Non-production test hook for the live forced-failure check."""
    return (
        os.environ.get("VERCEL_ENV") != "production"
        and os.environ.get("PRV3_DEBUG_FAIL_CALL") == call
    )


EXEC_SUMMARY_SYSTEM_PROMPT: str = """\
You write the executive summary that opens an organizational diagnostic \
report. The reader is the leader of the organization. The report has two \
parts: what the diagnostic found about how the organization is operating, and \
a review of its HR practices and compliance.

Write 2 to 3 sentences that connect the two: what the organizational finding \
means, and how the HR practices review adds to or sharpens that picture. \
Speak to the reader directly, the way a trusted advisor would.

RULES
- Plain, direct language. No jargon, no clinical or assessment language.
- Do not name a condition, pattern, or diagnosis. Do not quote numbers other \
than the gap counts you are given, and do not mention dollar figures.
- Do not name any firm, service, product, or program.
- Never use em dashes, en dashes used as dashes, double hyphens, or semicolons.
- Output only the summary text. No heading, no quotation marks, no markdown.
"""


def _build_exec_prompt(liability_condition_text: str, totals: dict) -> str:
    return (
        f"Organizational finding:\n{liability_condition_text}\n\n"
        f"HR practices review: {totals['flagged_count']} of {totals['total_count']} answers show a gap, "
        f"{totals['severe_count']} of them significant or unknown, across "
        f"{totals['sections_with_gaps']} of {totals['sections_total']} areas reviewed."
    )


def generate_executive_summary(
    liability_condition_text: str,
    totals: dict,
    model: str = "claude-sonnet-5",
    client=None,
    timeout: float = 15.0,
) -> tuple:
    """Call 3. Returns (text, ok, error). ("", False, error) on any failure."""
    if not liability_condition_text.strip():
        return "", False, "no liability_condition_text"
    try:
        if _debug_fail("exec"):
            raise RuntimeError("PRV3_DEBUG_FAIL_CALL=exec (non-production test hook)")
        if client is None:
            import anthropic as _anthropic
            client = _anthropic.Anthropic(max_retries=0)
        message = client.messages.create(
            model=model,
            max_tokens=300,
            thinking={"type": "disabled"},
            system=EXEC_SUMMARY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": _build_exec_prompt(liability_condition_text, totals)}],
            timeout=timeout,
        )
        text = _enforce_house_punctuation(message.content[0].text.strip())
        if not text:
            return "", False, "empty response"
        return text, True, ""
    except Exception as e:  # never crash the session
        return "", False, f"executive summary error: {e}"
