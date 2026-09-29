"""
Part B -- executive summary without TC answers (aligns the code to the
Section 14 lock, MOB v4.328: the three-call report architecture is locked
for both brands, but Call 3 only ran when Call 2 succeeded, and Call 2 is
never attempted without TC answers, so principalresolution.com never got
an executive summary).

  engine/main.py         Call 3 runs when Call 1 is not a fallback AND
                         (Call 2 succeeded OR Call 2 was never attempted).
                         Call 2 attempted and failed still skips Call 3.
  engine/exec_summary.py No-TC variant only: the gap-count line is left out
                         of the input, and the two-part task instructions
                         are replaced with Pete's paragraph (verbatim). The
                         length rule and RULES block are kept. The TC
                         (hr-dx) system prompt and input are unchanged.
  tools/test_phase1_report_data.py
                         Flips the "no TC answers" check (PR now runs Call 1
                         + Call 3), adds the no-TC, byte-identity and
                         punctuation checks.
  tools/test_hr_diagnostic_brand.py
                         Picks Call 1 by its system prompt instead of the
                         last captured call, since Call 3 now follows it.

Usage (from repo root):
    python tools/patch_exec_summary_no_tc.py --dry-run
    python tools/patch_exec_summary_no_tc.py --write
    --root <dir>  apply against another checkout (verification worktree)
"""
import argparse
import difflib
import pathlib
import sys

NO_TC_PARAGRAPH = (
    "Tell this leader, in plain language, what the diagnostic found and what it means "
    "for them. Start with what is happening, then what it is costing the organization "
    "in working terms, then what would have to change. Use only what is in the input, "
    "and describe only what the diagnostic assessed."
)
BANNED = {"em-dash": "\u2014", "en-dash": "\u2013", "double hyphen": "--", "semicolon": ";"}

EDITS = {
    "engine/main.py": [
        (
            "    # Phase 1 Step B: Call 3 (executive summary), sequential, only when\n"
            "    # Call 1 produced real synthesis and Call 2 succeeded.\n"
            "    executive_summary, exec_ok, exec_err, _call_3_s = \"\", False, \"skipped\", 0.0\n"
            "    if synthesis_result is not None and not synthesis_result.is_fallback and tactical_ok:\n"
            "        _t = time.monotonic()\n"
            "        executive_summary, exec_ok, exec_err = generate_executive_summary(\n"
            "            synthesis_result.liability_condition_text, tactical_totals(tactical_summary),\n"
            "        )\n",
            "    # Phase 1 Step B: Call 3 (executive summary), sequential, only when\n"
            "    # Call 1 produced real synthesis and Call 2 either succeeded or was\n"
            "    # never attempted (no TC answers, e.g. every principal_resolution\n"
            "    # session). Call 2 attempted and failed still skips Call 3.\n"
            "    call_2_attempted = _call_2_future is not None\n"
            "    executive_summary, exec_ok, exec_err, _call_3_s = \"\", False, \"skipped\", 0.0\n"
            "    if (synthesis_result is not None and not synthesis_result.is_fallback\n"
            "            and (tactical_ok or not call_2_attempted)):\n"
            "        _t = time.monotonic()\n"
            "        executive_summary, exec_ok, exec_err = generate_executive_summary(\n"
            "            synthesis_result.liability_condition_text,\n"
            "            tactical_totals(tactical_summary) if call_2_attempted else None,\n"
            "        )\n",
        ),
    ],
    "engine/exec_summary.py": [
        (
            "One LLM call, run AFTER Call 1 (core synthesis) and Call 2 (tactical\n"
            "synthesis) and only when both succeeded. Input is deliberately narrow: Call\n"
            "1's liability_condition_text plus the raw tactical counts. Output is a 2-3\n"
            "sentence summary bridging the organizational finding and the HR practices\n"
            "review. Any failure returns (\"\", False, error): the UI omits the section, and\n"
            "nothing else in the result changes.\n",
            "One LLM call, run AFTER Call 1 (core synthesis) and Call 2 (tactical\n"
            "synthesis), when Call 1 succeeded and Call 2 either succeeded or was never\n"
            "attempted. Input is deliberately narrow: Call 1's liability_condition_text\n"
            "plus the raw tactical counts. With TC answers (hr-dx) the output is a 2-3\n"
            "sentence summary bridging the organizational finding and the HR practices\n"
            "review. Without TC answers (totals=None) the counts line is left out and\n"
            "EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC asks for the finding alone. Any failure\n"
            "returns (\"\", False, error): the UI omits the section, and nothing else in\n"
            "the result changes.\n",
        ),
        (
            "_SENTENCE_END_RE = re.compile(",
            "# No-TC variant (Pete, 2026-09-28): the same prompt with the two-part task\n"
            "# replaced, so the length rule and RULES block stay shared. Derived by\n"
            "# replacement rather than a second literal, so the TC prompt above is\n"
            "# untouched and the two cannot drift apart outside the task text.\n"
            "_TWO_PART_TASK: str = (\n"
            "    \" The report has two parts: what the diagnostic found about how the \"\n"
            "    \"organization is operating, and a review of its HR practices and compliance.\"\n"
            "    \"\\n\\nWrite exactly 2 or 3 sentences, and no more than 70 words in total, that \"\n"
            "    \"connect the two: what the organizational finding means, and how the HR \"\n"
            "    \"practices review adds to or sharpens that picture.\"\n"
            ")\n"
            "_NO_TC_TASK: str = (\n"
            "    \"\\n\\n\"\n"
            "    \"Tell this leader, in plain language, what the diagnostic found and what it means \"\n"
            "    \"for them. Start with what is happening, then what it is costing the organization \"\n"
            "    \"in working terms, then what would have to change. Use only what is in the input, \"\n"
            "    \"and describe only what the diagnostic assessed.\"\n"
            "    \"\\n\\nWrite exactly 2 or 3 sentences, and no more than 70 words in total.\"\n"
            ")\n"
            "# No gap counts exist without TC answers, so the numbers rule drops them.\n"
            "_GAP_COUNT_RULE: str = \"Do not quote numbers other than the gap counts you are given\"\n"
            "EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC: str = EXEC_SUMMARY_SYSTEM_PROMPT.replace(\n"
            "    _TWO_PART_TASK, _NO_TC_TASK, 1,\n"
            ").replace(_GAP_COUNT_RULE, \"Do not quote numbers\", 1)\n"
            "\n"
            "\n"
            "_SENTENCE_END_RE = re.compile(",
        ),
        (
            "def _build_exec_prompt(liability_condition_text: str, totals: dict) -> str:\n"
            "    return (\n",
            "def _build_exec_prompt(liability_condition_text: str, totals: dict | None) -> str:\n"
            "    if totals is None:\n"
            "        return f\"Organizational finding:\\n{liability_condition_text}\"\n"
            "    return (\n",
        ),
        (
            "    liability_condition_text: str,\n"
            "    totals: dict,\n"
            "    model: str = \"claude-sonnet-5\",\n",
            "    liability_condition_text: str,\n"
            "    totals: dict | None,\n"
            "    model: str = \"claude-sonnet-5\",\n",
        ),
        (
            "    \"\"\"Call 3. Returns (text, ok, error). (\"\", False, error) on any failure.\"\"\"\n",
            "    \"\"\"Call 3. Returns (text, ok, error). (\"\", False, error) on any failure.\n"
            "    totals=None means no TC answers: no-TC prompt, no counts line.\"\"\"\n",
        ),
        (
            "            system=EXEC_SUMMARY_SYSTEM_PROMPT,\n",
            "            system=EXEC_SUMMARY_SYSTEM_PROMPT if totals is not None else EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC,\n",
        ),
    ],
    "tools/test_phase1_report_data.py": [
        (
            "from engine.exec_summary import EXEC_SUMMARY_SYSTEM_PROMPT\n",
            "from engine.exec_summary import EXEC_SUMMARY_SYSTEM_PROMPT, EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC\n",
        ),
        (
            "            EXEC_SUMMARY_SYSTEM_PROMPT: \"call3\"}.get(system, \"other\")\n",
            "            EXEC_SUMMARY_SYSTEM_PROMPT: \"call3\", EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC: \"call3\"}.get(system, \"other\")\n",
        ),
        (
            "FAIL.clear()\n"
            "pr_out = _complete(_log, brand=\"principal_resolution\")\n"
            "check(\"no TC answers: Call 2 and Call 3 never run, findings [], summary ''\",\n"
            "      [c[0] for c in CALLS] == [\"call1\"] and pr_out[\"private_output\"][\"tactical_findings\"] == []\n"
            "      and pr_out[\"synthesis\"][\"executive_summary\"] == \"\")\n",
            "FAIL.clear()\n"
            "pr_out = _complete(_log, brand=\"principal_resolution\")\n"
            "check(\"no TC answers: Call 2 never runs, Call 3 does (Section 14 lock, both brands)\",\n"
            "      [c[0] for c in CALLS] == [\"call1\", \"call3\"] and pr_out[\"private_output\"][\"tactical_findings\"] == [],\n"
            "      str([c[0] for c in CALLS]))\n"
            "check(\"no TC answers: PR-shaped payload gets an executive summary\",\n"
            "      pr_out[\"synthesis\"][\"executive_summary\"] != \"\")\n"
            "_nt = next(c[1] for c in CALLS if c[0] == \"call3\")\n"
            "_nt_all = _nt[\"system\"] + \"\\n\" + _nt[\"messages\"][0][\"content\"]\n"
            "check(\"no-TC Call 3 uses the no-TC system prompt\", _nt[\"system\"] == EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC)\n"
            "check(\"no-TC Call 3 prompt mentions no HR review, compliance, or empty counts\",\n"
            "      not any(s in _nt_all for s in (\"HR practices\", \"compliance\", \"0 of 0\", \"show a gap\")), _nt_all)\n"
            "check(\"no-TC Call 3 input is the finding alone\",\n"
            "      _nt[\"messages\"][0][\"content\"] == \"Organizational finding:\\nDecisions stall at the top.\")\n"
            f"_NO_TC_PARAGRAPH = {NO_TC_PARAGRAPH!r}\n"
            "check(\"no-TC system prompt carries Pete's paragraph verbatim and keeps the length rule\",\n"
            "      _NO_TC_PARAGRAPH in EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC\n"
            "      and \"Write exactly 2 or 3 sentences, and no more than 70 words in total.\" in EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC\n"
            "      and \"RULES\" in EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC)\n"
            "check(\"no-TC numbers rule: 'Do not quote numbers.' with no mention of gap counts\",\n"
            "      \"Do not quote numbers, and do not mention dollar figures.\" in EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC\n"
            "      and \"gap counts\" not in EXEC_SUMMARY_SYSTEM_PROMPT_NO_TC\n"
            "      and \"gap counts you are given\" in EXEC_SUMMARY_SYSTEM_PROMPT)\n"
            "check(\"no-TC paragraph: no em-dash, en-dash, double hyphen, or semicolon\",\n"
            "      not any(ch in _NO_TC_PARAGRAPH for ch in (\"\\u2014\", \"\\u2013\", \"--\", \";\")))\n"
            "FAIL.clear(); FAIL.add(\"call1\")\n"
            "pr_fb = _complete(_log, brand=\"principal_resolution\")\n"
            "check(\"no TC answers + Call 1 fallback: Call 3 still skipped\",\n"
            "      \"call3\" not in [c[0] for c in CALLS] and pr_fb[\"synthesis\"][\"executive_summary\"] == \"\")\n"
            "FAIL.clear()\n"
            "\n"
            "# hr-dx (TC present): Call 3's system prompt and input are byte-identical to\n"
            "# before the no-TC change (frozen copies of the pre-change strings).\n"
            "_FROZEN_TC_SYSTEM = {FROZEN_SYSTEM}\n"
            "_FROZEN_TC_INPUT = {FROZEN_INPUT}\n"
            "check(\"hr-dx: Call 3 system prompt byte-identical to pre-change\",\n"
            "      EXEC_SUMMARY_SYSTEM_PROMPT == _FROZEN_TC_SYSTEM and call3_prompt_system == _FROZEN_TC_SYSTEM)\n"
            "check(\"hr-dx: Call 3 input byte-identical to pre-change\", call3_prompt == _FROZEN_TC_INPUT, call3_prompt)\n",
        ),
        (
            "call3_prompt = next(c[1] for c in CALLS if c[0] == \"call3\")[\"messages\"][0][\"content\"]\n",
            "call3_prompt = next(c[1] for c in CALLS if c[0] == \"call3\")[\"messages\"][0][\"content\"]\n"
            "call3_prompt_system = next(c[1] for c in CALLS if c[0] == \"call3\")[\"system\"]\n",
        ),
    ],
}

# test_hr_diagnostic_brand.py read captured[-1] as Call 1's prompt. With Call 3
# now running when there are no TC answers, Call 3 is the last call captured,
# so Call 1 is picked by its system prompt instead.
EDITS["tools/test_hr_diagnostic_brand.py"] = [
    (
        "fake_anthropic = types.ModuleType(\"anthropic\")\n",
        "from engine.output_synthesis import OUTPUT_SYNTHESIS_SYSTEM_PROMPT\n"
        "\n"
        "\n"
        "def _call1(calls):\n"
        "    # Call 3 also runs when there are no TC answers (both brands), so the\n"
        "    # last captured call is not necessarily Call 1.\n"
        "    return next(c for c in calls if c.get(\"system\") == OUTPUT_SYNTHESIS_SYSTEM_PROMPT)\n"
        "\n"
        "\n"
        "fake_anthropic = types.ModuleType(\"anthropic\")\n",
    ),
    (
        "        prompt = captured[-1][\"messages\"][0][\"content\"]\n",
        "        prompt = _call1(captured)[\"messages\"][0][\"content\"]\n",
    ),
    (
        "        pr_line = next((l for l in captured[-1][\"messages\"][0][\"content\"].splitlines() if l.startswith(\"resolution_family:\")), \"\")\n",
        "        pr_line = next((l for l in _call1(captured)[\"messages\"][0][\"content\"].splitlines() if l.startswith(\"resolution_family:\")), \"\")\n",
    ),
]


def frozen_strings(root: pathlib.Path):
    """The TC-case strings as they are before this patch, from the unpatched source."""
    sys.path.insert(0, str(root))
    from engine.exec_summary import EXEC_SUMMARY_SYSTEM_PROMPT, _build_exec_prompt
    from engine.tactical_synthesis import build_tactical_summary, tactical_totals
    # Same TC answers and Call 1 text the test harness uses (test_phase1_report_data.py
    # tc_log and the fake Call 1 response), so the frozen input is what that run sends.
    tc_log = [
        {"question_id": "Q05", "option_ids": ["C"]},
        {"question_id": "TC-HIRE-01", "option_ids": ["A"]},
        {"question_id": "TC-HRPOL-01", "option_ids": ["A"]},
        {"question_id": "TC-HRPOL-02", "option_ids": ["B"]},
        {"question_id": "TC-HRPOL-03", "option_ids": ["C"]},
        {"question_id": "TC-HRPOL-04", "option_ids": ["D"]},
        {"question_id": "TC-NOPE-01", "option_ids": ["A"]},
    ]
    tc_input = _build_exec_prompt(
        "Decisions stall at the top.", tactical_totals(build_tactical_summary(tc_log)),
    )
    return EXEC_SUMMARY_SYSTEM_PROMPT, tc_input


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    root = pathlib.Path(args.root).resolve()

    hits = [n for n, ch in BANNED.items() if ch in NO_TC_PARAGRAPH]
    print(f"[CHECK] no-TC paragraph punctuation: {hits or 'clean'}")
    if hits:
        return 1

    sys_prompt, tc_input = frozen_strings(root)
    out = {}
    for rel, edits in EDITS.items():
        src = (root / rel).read_text(encoding="utf-8")
        new = src
        for old, rep in edits:
            rep = rep.replace("{FROZEN_SYSTEM}", repr(sys_prompt)).replace("{FROZEN_INPUT}", repr(tc_input))
            if new.count(old) != 1:
                print(f"[FAIL] {rel}: anchor found {new.count(old)} times: {old[:60]!r}")
                return 1
            new = new.replace(old, rep, 1)
        out[rel] = (src, new)

    for rel, (src, new) in out.items():
        if args.dry_run:
            sys.stdout.writelines(difflib.unified_diff(
                src.splitlines(True), new.splitlines(True), f"a/{rel}", f"b/{rel}"))
        else:
            (root / rel).write_text(new, encoding="utf-8")
            print(f"[WROTE] {rel}")
    if args.dry_run:
        print("\nDry run only, nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
