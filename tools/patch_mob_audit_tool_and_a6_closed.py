"""
PRV3 -- MOB update: three new Decision Register rows. (1) The diagnostic
question/option audit tool built and verified this session. (2) SEVER-09
dead-trigger finding, logged PARKED. (3) A6 (Section A.6, diagnostic-
usability-findings-2026-08-09.md) closed as "no structural issue found,"
using the new tool's output as the review artifact.

Version bump v4.138 -> v4.139: new tooling + a closed Tier-1-adjacent
content review, not a session-log-only change.

Usage:
  python tools/patch_mob_audit_tool_and_a6_closed.py --dry-run
  python tools/patch_mob_audit_tool_and_a6_closed.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


MOB = "tools/_mob.txt"

ANCHOR = (
    '| Infrastructure findings -- no Preview environment; no custom domain yet (SSO gates public access) | 3 | Confirmed, informational -- not a gap, working as intended | N/A | Two infrastructure facts confirmed directly this session, not assumed. (1) prv-3 has no separate Vercel Preview environment -- every commit to main deploys straight to production. This resolved a standing ambiguity in the session\'s working assumptions and changed the default workflow going forward: dry-run -> Pete confirms -> write -> full regression -> commit -> push in one pass by default, holding only for unretested production-facing surfaces, structural decisions not yet through Gemini review, or anything that feels higher-risk in the moment. (2) prv-3 has no custom domain yet (Porkbun wiring pending) -- Vercel\'s Deployment Protection (SSO gate) currently blocks public/unauthenticated access to the deployed app. Confirmed this is expected, pre-launch behavior, not a bug or regression -- logged so a future session doesn\'t rediscover it as a surprise or spend time debugging apparent inaccessibility. | This session (Claude Code) | No forced check-in -- reopen only if Pete begins the custom-domain/Porkbun work, at which point the SSO-gating behavior needs a deliberate decision about what replaces it |'
)

NEW_ROWS = (
    '\n'
    '| Diagnostic question/option audit tool (tools/diagnostic_question_audit.py) -- built, verified, shipped | N/A -- read-only tooling, not a Tier 1-4 workflow item | Shipped -- no Gemini gate needed (Pete\'s explicit call, confirmed correct: new standalone script, touches no existing file\'s behavior/data contract/integration surface, same category as the other tools/diag_*.py scripts already in this repo) | N/A | Built to replace live-browser walkthroughs for A6-style option-adequacy reviews (today\'s live walk via Claude.ai + claude-in-chrome proved the concept but hit real limits: slow, timeouts every ~15 steps, only sees whatever single answer-path was walked, captured options but not full stems). Reads engine/data/questions.py\'s real QUESTION_LIBRARY and web/lib/session-store.ts\'s real PHASE_1_QUESTION_SEQUENCE directly, in-process, no browser, no network -- runs in seconds against real repo state. Exhaustive, not path-dependent: dumps all 101 questions in the library, not just what one path reaches. Computes reachability via graph traversal (BFS) over severity_follow_on_id edges, seeded from CORE + the two hardcoded content-splices (Q06->Q28, Q44->Q45) + all DIST-* checkpoint-distinguisher questions -- three categories, not two: CORE (42, always asked), SPLICED (37, real live conditional trigger, including multi-hop chains like SEVER-01->SEVER-12), UNREACHABLE (22, zero live trigger path anywhere -- a category the original ask didn\'t anticipate but the data required, found empirically not assumed). Heuristic flags only, never a verdict, per A6\'s own framing as Pete\'s judgment call: option count < 3, binary (2-option, flagged for review not assumed broken), and a keyword scan for absent doesn\'t-apply/none/N-A-style options. Self-correction caught before delivery: the first draft\'s summary paragraph hand-described the UNREACHABLE list from memory and got the count wrong (said 20, real count 22, missed SEVER-09 entirely) -- rewritten to generate from the actual audit data instead of hand-maintained prose, so the report can\'t drift from what the tool actually found. Output published as an Artifact (https://claude.ai/code/artifact/72fcd919-cf4e-422c-a3f6-b6e0c27dc037) and committed as tools/diagnostic_question_audit_output.md. | This session (Claude Code) | Closed -- no further check-in. Standard method for future A6-style reviews going forward, replacing live-browser walks |\n'
    '| SEVER-09 dead trigger -- found via the new audit tool, PARKED | 3 | Parked, not scheduled -- informational, harmless | N/A | SEVER-09\'s only trigger anywhere in the codebase is Q27A, which is itself unreachable in live Phase 1 (the locked intake adapter always takes the Q27B branch) -- SEVER-09 has never had a live path, despite being a normally-numbered severity follow-on indistinguishable from a working one by inspection alone. Distinct from SEVER-11\'s already-known dual-parent case (Q28 live, Q31 dead) -- SEVER-11 still fires via its live parent; SEVER-09 has no live parent at all. Found by the new diagnostic question/option audit tool\'s reachability graph, not previously logged anywhere. Same treatment as other harmless-but-real dead-code findings already on record (the cluster_id gap, etc.) -- not urgent, no live-scoring impact (severity_follow_on questions carry zero weight until fired). | This session (Claude Code) | Not scheduled -- flag for whenever Pete wants a dedicated dead-severity-follow-on sweep (SEVER-09 may not be the only one this class of finding could surface with the tool now available to check) |\n'
    '| A6 (Section A.6, diagnostic-usability-findings-2026-08-09.md -- option-count/adequacy review) -- CLOSED, no structural issue found | 3 | **Closed -- reviewed via the new audit tool, no action needed** | N/A | 101 total questions audited (42 core, 37 spliced-live, 22 unreachable). Option-count signal: only 2 questions flagged as binary (2-option), both core -- Q41 and Q43 (Structure 1/2\'s yes/no gates) -- same legitimate factual-gate pattern already confirmed in this session\'s earlier live walkthrough for Q33/Q35-equivalent questions, not perception scales being forced into two options. The "no doesn\'t-apply/N-A option" keyword scan hit 96/101 questions -- logged as weak signal, not a finding, per Pete\'s explicit framing: that heuristic is near-universal across the library as currently worded and should not be re-run as if it were meaningful without narrowing it first (e.g. scoping to questions where an N-A option would plausibly change the respondent\'s ability to answer honestly, not a blanket keyword absence check). | This session (Claude Code) | Closed -- no further check-in. Reopen only if Pete wants a narrower pass at the "no N/A option" signal specifically, or if the audit tool surfaces something new on a future re-run |\n'
)


def apply(dry_run: bool) -> int:
    changed = 0
    path = REPO_ROOT / MOB
    text = path.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count != 1:
        print(f"ERROR: {MOB} -- expected 1 match for anchor, found {count}")
        return 1
    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROWS, 1)
    if dry_run:
        print(f"OK (dry-run): {MOB} -- anchor found, would insert 3 new rows")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"WRITTEN: {MOB} -- 3 new rows inserted")
    changed += 1

    version_edits = [
        (MOB, "\\\\\\#\\\\\\# MOB v4.138", "\\\\\\#\\\\\\# MOB v4.139"),
        ("CLAUDE.md", "| MOB version | v4.138 |", "| MOB version | v4.139 |"),
    ]
    for rel_path, old, new in version_edits:
        p = REPO_ROOT / rel_path
        t = p.read_text(encoding="utf-8")
        c = t.count(old)
        if c != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {c}")
            return 1
        nt = t.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            p.write_text(nt, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1

    print(f"\n{changed}/3 edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
