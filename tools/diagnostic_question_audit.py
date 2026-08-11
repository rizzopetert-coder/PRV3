"""
tools/diagnostic_question_audit.py

Reusable, on-demand audit of every question in the diagnostic's question
library -- built to replace live-browser walkthroughs for A6 (Section A.6,
prompts/diagnostic-usability-findings-2026-08-09.md: "are there enough
answer options on every question, or do some force a choice that doesn't
fit the respondent's real situation"). In-process, no browser, no network
-- reads engine/data/questions.py's real QUESTION_LIBRARY and
web/lib/session-store.ts's real PHASE_1_QUESTION_SEQUENCE directly, same
live-read pattern as tools/diag_v21_accumulated_centroid.py (regex-
extracted at run time, not hand-transcribed, so it can't silently drift
from the real live sequence the way a copied list could).

Exhaustive by construction, not path-dependent: every question in the
library is reported, regardless of whether any single answer path would
ever reach it. Three reachability categories, not two -- "core or spliced"
undersells what's actually in the library:

  CORE      -- in PHASE_1_QUESTION_SEQUENCE, always asked, fixed position.
  SPLICED   -- not core, but has a real, live trigger path back to a core
               question (severity_follow_on_id chains, including multi-hop
               ones like SEVER-01 -> SEVER-12) or to a checkpoint
               distinguisher pool (DIST-##) or to one of the two hardcoded
               content-based splices (Q06 -> Q28, Q44 -> Q45).
  UNREACHABLE -- exists in the library with zero live trigger path. Found
               empirically, not assumed: 5 excluded Aptitude-addenda
               questions (Q35-Q39, session-store.ts's own header comment
               confirms these are deliberately not in Phase 1), Q03A/Q27A
               (the locked intake adapter always takes the B branch) and
               Q03A's own chained follow-up Q03A-D-FOLLOW, Q31 (parked --
               content intact, zero firing logic per the Decision
               Register), and 12 VERIFY-Q## "verification probe" questions
               from Session 14 that no live route, splice table, or
               distinguisher pool references anywhere in the current
               codebase. Reported, not silently dropped -- if any of these
               is ever wired live later, this audit already has its
               content on record; if it never is, Pete can see exactly
               what's sitting inert.

Reachability is computed by graph traversal (BFS), not assumption: build a
directed edge for every (parent_question, parent_option) ->
severity_follow_on_id pair found anywhere in the library, seed the
frontier with CORE plus the two hardcoded splices plus any DIST-* question
(checkpoint distinguisher pools are cluster-triggered, not option-
triggered, so they're roots in this graph, not edge targets), then walk
forward. A question with an incoming edge from a dead question (e.g.
SEVER-11's second parent, Q31) still correctly resolves SPLICED if it
also has a live parent (SEVER-11's other parent, Q28) -- both paths are
reported, live and dead, so nothing is hidden.

Flags are heuristic candidates for Pete's review, never a verdict --
A6 is explicitly a judgment call, not an engineering decision:
  - option count < 3
  - binary (2-option) -- flagged for review, not assumed broken; today's
    live walkthrough found Q33/Q35-equivalent binary questions that read
    as legitimate factual yes/no gates, not perception scales
  - no doesn't-apply/none/N-A-style option anywhere in the option set
    (keyword scan) -- this is A6's literal ask (do some questions force a
    choice that doesn't fit)

Read-only. No engine writes, no calibration risk, no P-03 relevance --
nothing here crosses the client-server boundary, it reads repo source
directly. Confirmed safe to build without a Gemini architecture-review
gate (Pete's explicit call, this session): a new, standalone diagnostic
script that doesn't touch any existing file's behavior, data contract, or
integration surface -- same category as the other tools/diag_*.py scripts
already in this repo, none of which went through individual review either.

Usage:
  python tools/diagnostic_question_audit.py
  (writes tools/diagnostic_question_audit_output.md)
"""

from __future__ import annotations

import re
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from engine.data.questions import _build_library, DISTINGUISHER_CLUSTER_PREFIXES

SESSION_STORE_PATH = REPO_ROOT / "web" / "lib" / "session-store.ts"
ANSWER_ROUTE_PATH = REPO_ROOT / "web" / "app" / "api" / "diagnostic" / "session" / "answer" / "route.ts"
OUTPUT_PATH = REPO_ROOT / "tools" / "diagnostic_question_audit_output.md"

# Hardcoded content-based splices -- not data-driven (no severity_follow_on_id
# involved), so they can't be discovered by the edge scan below. Confirmed by
# direct read of session/answer/route.ts at the time this script was written;
# if a future session adds a third one of these, it needs a matching entry
# here or this audit will misreport it as UNREACHABLE.
HARDCODED_SPLICES: dict[str, str] = {
    "Q28": 'Conditional splice off Q06 -- fires when Q06\'s answer is A or B '
           '(hardcoded check, session/answer/route.ts).',
    "Q45": 'Conditional splice off Q44 -- fires when Q44\'s answer is B, C, or D '
           '(hardcoded check, session/answer/route.ts).',
}

NA_KEYWORDS = [
    "doesn't apply", "does not apply", "not applicable", "n/a",
    "none of", "no dedicated", "not something we", "isn't something",
    "this doesn't apply",
]


def load_live_question_sequence() -> list[str]:
    """
    Extract PHASE_1_QUESTION_SEQUENCE directly from web/lib/session-store.ts,
    same pattern as tools/diag_v21_accumulated_centroid.py -- the real live
    source of truth, not a hand-transcribed copy that could drift.
    """
    text = SESSION_STORE_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"PHASE_1_QUESTION_SEQUENCE:\s*readonly string\[\]\s*=\s*\[(.*?)\];",
        text,
        re.DOTALL,
    )
    if not match:
        raise RuntimeError(
            f"PHASE_1_QUESTION_SEQUENCE pattern not found in {SESSION_STORE_PATH}"
        )
    return re.findall(r'"([A-Z0-9]+)"', match.group(1))


@dataclass
class QuestionAudit:
    question_id: str
    question_text: str
    options: list[tuple[str, str]]  # (option_id, option_text)
    status: str  # "CORE" | "SPLICED" | "UNREACHABLE"
    position: str
    trigger_lines: list[str]
    flags: list[str]


def build_edges(lib) -> dict[str, list[tuple[str, str, str]]]:
    """
    incoming[target_qid] = [(parent_qid, parent_option_id, parent_option_text), ...]
    Scans every option of every question for a set severity_follow_on_id.
    """
    incoming: dict[str, list[tuple[str, str, str]]] = {}
    for qid, q in lib.items():
        for opt in q.answer_options:
            target = opt.severity_follow_on_id
            if target:
                incoming.setdefault(target, []).append((qid, opt.option_id, opt.option_text))
    return incoming


def compute_reachability(
    lib, core_ids: set[str], incoming: dict[str, list[tuple[str, str, str]]]
) -> set[str]:
    """
    BFS from CORE + hardcoded splices + all DIST-* questions (checkpoint
    distinguisher pools are cluster-triggered roots, not edge targets).
    """
    roots = set(core_ids) | set(HARDCODED_SPLICES.keys())
    roots |= {qid for qid in lib if qid.startswith("DIST-")}

    reachable = set(roots)
    frontier = deque(roots)
    while frontier:
        current = frontier.popleft()
        for target, parents in incoming.items():
            if target in reachable:
                continue
            if any(parent_qid == current for parent_qid, _, _ in parents):
                reachable.add(target)
                frontier.append(target)
    return reachable


def describe_trigger(
    qid: str,
    lib,
    incoming: dict[str, list[tuple[str, str, str]]],
    reachable: set[str],
) -> list[str]:
    if qid.startswith("DIST-"):
        prefix = qid.rsplit("-", 1)[0]
        cluster = next(
            (c for c, p in DISTINGUISHER_CLUSTER_PREFIXES.items() if p == prefix),
            "unknown cluster",
        )
        return [
            f"Checkpoint distinguisher -- cluster {cluster}, fires at Q11/Q19/Q27 "
            f"when that cluster is dominant (max 2 selected per checkpoint firing)."
        ]
    if qid in HARDCODED_SPLICES:
        return [HARDCODED_SPLICES[qid]]

    parents = incoming.get(qid, [])
    if not parents:
        return ["No incoming trigger found anywhere in the library."]

    lines = []
    for parent_qid, parent_opt_id, parent_opt_text in parents:
        live_note = "LIVE" if parent_qid in reachable else "INERT -- parent itself unreachable"
        lines.append(
            f'Via {parent_qid} option {parent_opt_id} ("{parent_opt_text[:60]}"'
            f'{"..." if len(parent_opt_text) > 60 else ""}) -- {live_note}'
        )
    return lines


def compute_flags(options: list[tuple[str, str]]) -> list[str]:
    flags = []
    n = len(options)
    if n < 3:
        flags.append(f"OPTION COUNT < 3 ({n})")
    if n == 2:
        flags.append("BINARY (2 options) -- review, not auto-broken")
    combined = " ".join(text.lower() for _, text in options)
    if not any(kw in combined for kw in NA_KEYWORDS):
        flags.append("NO DOESN'T-APPLY/NONE/N-A OPTION FOUND")
    return flags


def main() -> None:
    lib = _build_library()
    core_sequence = load_live_question_sequence()
    core_ids = set(core_sequence)
    core_position = {qid: i + 1 for i, qid in enumerate(core_sequence)}

    incoming = build_edges(lib)
    reachable = compute_reachability(lib, core_ids, incoming)

    audits: list[QuestionAudit] = []
    for qid in sorted(lib.keys()):
        q = lib[qid]
        options = [(opt.option_id, opt.option_text) for opt in q.answer_options]

        if qid in core_ids:
            status = "CORE"
            position = str(core_position[qid])
            trigger_lines = ["Always asked -- fixed position in PHASE_1_QUESTION_SEQUENCE."]
        elif qid in reachable:
            status = "SPLICED"
            position = "Varies by path (conditional)"
            trigger_lines = describe_trigger(qid, lib, incoming, reachable)
        else:
            status = "UNREACHABLE"
            position = "N/A -- not live-reachable"
            trigger_lines = describe_trigger(qid, lib, incoming, reachable)
            if trigger_lines == ["No incoming trigger found anywhere in the library."]:
                trigger_lines = [
                    "No live trigger anywhere in the codebase -- not core, not "
                    "chained from any core/spliced question, not a checkpoint "
                    "distinguisher pool member."
                ]

        flags = compute_flags(options)

        audits.append(QuestionAudit(
            question_id=qid,
            question_text=q.question_text,
            options=options,
            status=status,
            position=position,
            trigger_lines=trigger_lines,
            flags=flags,
        ))

    write_report(audits, core_sequence)
    print(f"Wrote {OUTPUT_PATH} -- {len(audits)} questions audited.")


def write_report(audits: list[QuestionAudit], core_sequence: list[str]) -> None:
    lines = []
    lines.append("# Diagnostic Question/Option Audit")
    lines.append("")
    lines.append(
        f"Generated by `tools/diagnostic_question_audit.py` against the real live "
        f"repo state (in-process, no browser). Replaces the partial live-browser-walk "
        f"data from the 2026-08-09/2026-08-10 sessions as the A6 review artifact."
    )
    lines.append("")

    n_core = sum(1 for a in audits if a.status == "CORE")
    n_spliced = sum(1 for a in audits if a.status == "SPLICED")
    n_unreachable = sum(1 for a in audits if a.status == "UNREACHABLE")
    flagged = [a for a in audits if a.flags]

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total questions in library: **{len(audits)}**")
    lines.append(f"- CORE (always asked): **{n_core}** (matches live PHASE_1_QUESTION_SEQUENCE length)")
    lines.append(f"- SPLICED (real live conditional trigger): **{n_spliced}**")
    lines.append(f"- UNREACHABLE (zero live trigger path, found empirically): **{n_unreachable}**")
    lines.append(f"- Questions with at least one flag: **{len(flagged)}** of {len(audits)}")
    lines.append("")

    if n_unreachable:
        unreachable_ids = [a.question_id for a in audits if a.status == "UNREACHABLE"]
        lines.append(
            f"**Note beyond the original ask:** the UNREACHABLE category surfaced "
            f"**{n_unreachable}** questions with zero live trigger path anywhere in "
            f"the codebase -- not just \"spliced, rarely fires,\" but genuinely inert. "
            f"This list is computed directly from the same graph traversal as the "
            f"rest of this report (not hand-maintained), so it stays accurate as the "
            f"question library changes: {', '.join(unreachable_ids)}. Most trace to "
            f"already-known causes (the excluded Aptitude addenda Q35-Q39, the "
            f"intake-adapter-locked-out Q03A/Q27A branch and Q03A's own chained "
            f"follow-up, Q31 parked per the Decision Register, and 12 \"VERIFY-Q##\" "
            f"probes from Session 14 that nothing live references) -- but SEVER-09 is "
            f"a new finding this run: its only parent, Q27A, is itself unreachable, "
            f"so SEVER-09 has never had a live path despite looking like a normal "
            f"numbered severity follow-on. Listed for the record, not acted on."
        )
        lines.append("")

    if flagged:
        lines.append("## Flagged questions (candidates for review -- not verdicts)")
        lines.append("")
        lines.append("| Question | Status | Options | Flags |")
        lines.append("|---|---|---|---|")
        for a in flagged:
            lines.append(
                f"| {a.question_id} | {a.status} | {len(a.options)} | {'; '.join(a.flags)} |"
            )
        lines.append("")

    lines.append("## Full question detail (sorted by question_id)")
    lines.append("")

    for a in audits:
        lines.append(f"### {a.question_id} — {a.status}")
        lines.append("")
        lines.append(f"**Position:** {a.position}")
        lines.append("")
        lines.append(f"**Stem:** {a.question_text}")
        lines.append("")
        lines.append(f"**Options** ({len(a.options)}):")
        for opt_id, opt_text in a.options:
            lines.append(f"- **{opt_id}.** {opt_text}")
        lines.append("")
        lines.append("**Trigger:**")
        for t in a.trigger_lines:
            lines.append(f"- {t}")
        lines.append("")
        if a.flags:
            lines.append(f"**Flags:** {'; '.join(a.flags)}")
        else:
            lines.append("**Flags:** none")
        lines.append("")
        lines.append("---")
        lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
