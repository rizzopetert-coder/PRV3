"""
PRV3 MOB Update -- Session 71 continued (synthesis-timeout finding, prv-3 pre-launch)

Updates tools/_mob.txt:
  - Section 13a (Decision Register): new row -- synthesis call failing/falling
    back on prv-3, reframed per Pete's direct correction as a confirmed
    pre-launch defect (must fix before cutover), not a live incident. Includes
    the prv-2/prv-3 alias clarification (prv-2 serves real traffic at
    principalresolution.com today; prv-3 is the next iteration, not yet cut
    over, cutover timing is Pete's call).
  - Version bump v4.47 -> v4.48 (new Decision Register item, material finding)

Updates CLAUDE.md:
  - MOB version cross-reference v4.47 -> v4.48

Documentation-only change -- no product code touched by this script.

Usage:
  python tools/patch_mob_s71_synthesis_prelaunch.py --dry-run
  python tools/patch_mob_s71_synthesis_prelaunch.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ═══════════════════════════════════════════════════════════════════════════
# tools/_mob.txt
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.47",
    "\\\\\\#\\\\\\# MOB v4.48",
)

# --- Section 13a (Decision Register): new row ---

ANCHOR_LAST_ROW = (
    "| vercel env pull masks Sensitive-flagged vars — value-diffing is unreliable "
    "for them | N/A — tooling/verification-method fact, not a Tier 1-4 workflow item "
    "| Open, no urgency — informational, method already adjusted | `vercel env pull` "
    "returns the literal placeholder string `[SENSITIVE]` rather than the real value "
    "for vars flagged Sensitive in Vercel — confirmed by cross-checking against a "
    "non-Sensitive var (a freshly pulled Development-scoped UPSTASH_REDIS_REST_URL), "
    "which returned its real value while Production's and Preview's (both "
    "Sensitive-flagged) returned `[SENSITIVE]` for both, making a same-session "
    "value-diff between them meaningless (comparing two identical placeholders, not "
    "real secrets). The original shared-Redis-instance finding earlier in this "
    "session is unaffected — that check ran before a CLI upgrade (50.25.1 -> "
    "56.3.1) and returned real, differently-sized content, not placeholders. This is "
    "a newly discovered behavior (or CLI-version difference), not a retroactive "
    "doubt on that earlier evidence. Scope grouping via `vercel env ls` does not "
    "depend on reading the value and remains reliable — it is now the default "
    "verification method for Sensitive-flagged env vars going forward, not "
    "value-pulling | Session 71 (Claude Code) | No forced check-in — informational "
    "finding, already incorporated into this session's verification method |"
)

NEW_ROW = (
    "| Synthesis call failing / falling back to static copy (5s LOCKED timeout, "
    "output_synthesis.py) | N/A — confirmed pre-launch defect, not a Tier 1-4 "
    "workflow item | Confirmed pre-launch defect in prv-3 — must be fixed before "
    "cutover. Zero current user impact: confirmed this session (Pete, direct) that "
    "prv-2 is the current live iteration actually serving real traffic at "
    "principalresolution.com / www.principalresolution.com; prv-3 (everything Path 1 "
    "built and tested this session, and the project this finding was found in) is "
    "the next iteration, not yet cut over — Pete controls cutover timing explicitly. "
    "An earlier framing in this same session briefly treated the alias structure as "
    "an open question / possible live-incident signal before Pete corrected it "
    "directly — noted here so it isn't rediscovered as new | Reproduced 3x "
    "identically on a Preview deployment (17.424s, 17.471s, 17.767s, all "
    "is_fallback=true) with a genuine APITimeoutError and visible Anthropic SDK "
    "auto-retry (two retry attempts logged, ~0.9s then ~0.4s backoff) — captured via "
    "temporary, uncommitted diagnostic logging added to output_synthesis.py's "
    "exception handler, deployed only to an ephemeral non-git `vercel deploy` build, "
    "then reverted via `git checkout --` and independently re-verified clean "
    "(`git status --porcelain` / `git diff` both empty) before this row was "
    "written. One Pete-authorized synthetic test call against prv-3's actual "
    "Production deployment (prv-3.vercel.app, confirmed via `vercel alias ls` as "
    "the real alias target of the current Ready Production build) also returned "
    "is_fallback=true, but with a materially different timing signature — 4.483s, "
    "too fast to contain even one full 5s-timeout-plus-retry cycle. Same symptom "
    "(fallback served instead of real synthesis), not yet confirmed to be the same "
    "root cause — the fast-fail shape is more consistent with an immediate API-level "
    "error or a different exception type than with the Preview timeout pattern. The "
    "real exception for the Production fast-fail has not been captured — doing so "
    "would require a second temporary-logging deploy, this time to Production itself "
    "rather than an ephemeral non-git build, which is a heavier and riskier action "
    "than the single plain HTTP test call already authorized; not done without a "
    "separate explicit go-ahead. No retry/timeout config has been changed anywhere — "
    "diagnosis only, per Pete's explicit instruction | Session 71 (Claude Code) | "
    "Before prv-3 cutover — must be resolved (or explicitly accepted as an understood, "
    "low-risk gap) before Pete authorizes cutting prv-3 over to serve real traffic. "
    "Not a session-number check-in |"
)

edit("tools/_mob.txt", ANCHOR_LAST_ROW, ANCHOR_LAST_ROW + "\n" + NEW_ROW)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.47 |",
    "| MOB version | v4.48 |",
)


# ---------------------------------------------------------------------------

def apply(dry_run: bool):
    changed_files: dict[str, str] = {}
    errors = []

    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = changed_files.get(rel_path)
        if text is None:
            if not path.exists():
                errors.append(f"MISSING FILE: {rel_path}")
                continue
            text = path.read_text(encoding="utf-8")

        count = text.count(old)
        if count != 1:
            errors.append(
                f"{rel_path}: expected 1 match, found {count}\n"
                f"  --- anchor (first 160 chars) ---\n  {old[:160]!r}"
            )
            continue

        changed_files[rel_path] = text.replace(old, new, 1)

    print("=" * 72)
    print(f"MOB S71 SYNTHESIS PRE-LAUNCH PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
    print("=" * 72)
    print(f"Files touched: {len(changed_files)}")
    for rel_path in changed_files:
        print(f"  - {rel_path}")

    if errors:
        print("\nERRORS:" if dry_run else "\nERRORS — nothing written:")
        for e in errors:
            print(f"\n[ERROR] {e}")
        if not dry_run:
            sys.exit(1)
        return

    if dry_run:
        print("\nDry run OK — all anchors matched exactly once. No files written.")
        return

    for rel_path, text in changed_files.items():
        (REPO_ROOT / rel_path).write_text(text, encoding="utf-8")
    print("\nAll files written.")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    apply(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
