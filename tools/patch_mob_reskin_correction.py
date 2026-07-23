"""
PRV3 MOB Update -- Correct the DiagnosticFlow.tsx record (Stage 3 token
content confirmed live on origin/main per Pete's explicit decision, not
an oversight) and log the reskin planning-document process gap honestly

Updates tools/_mob.txt:
  - Section 14 (Locked Decisions Log): new entry appended after the
    Q28/Q31 build entry (ascending order, this section's newest tail)
  - Section 16 (Session Log): new one-line entry prepended before the
    prior entry's log line (descending order, this section's newest head)
  - Version bump v4.60 -> v4.61 (material workstream status change --
    corrects a standing inaccuracy and logs a real process gap)

Updates CLAUDE.md:
  - MOB version cross-reference v4.60 -> v4.61

Documentation-only change -- no product code touched by this script.

Usage:
  python tools/patch_mob_reskin_correction.py --dry-run
  python tools/patch_mob_reskin_correction.py --write
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
    "\\\\\\#\\\\\\# MOB v4.60",
    "\\\\\\#\\\\\\# MOB v4.61",
)

# --- Section 14 (Locked Decisions Log, ascending -- append after newest tail) ---

Q28_ENTRY_TAIL = (
    "**Open item carried, per Pete's explicit instruction:** non-integer "
    "parent ID labeling (Q03B/Q27B + letter format) deferred, documented "
    "only -- no current live case triggers it; spliceLabel() falls back "
    "to the raw parent ID rather than crashing if this is ever hit before "
    "it's resolved. MOB v4.60. |"
)

CORRECTION_ENTRY = (
    "| **July 2026 — Record correction (DiagnosticFlow.tsx reskin) + "
    "reskin planning-document process gap logged** | Two items, both "
    "surfaced by Pete's own status-report request, neither reconstructed "
    "from guesswork. **Correction:** the prior entry's closing note -- "
    "'both now sit uncommitted in the same file until Pete decides how to "
    "handle the reskin' -- was wrong. Confirmed via git status/git show "
    "investigation (not assumed): staging a whole file (`git add "
    "web/components/DiagnosticFlow.tsx`) captures its entire current "
    "diff, not a curated subset -- so commit 290ce8d (the counter/label "
    "logic fix) also carried DiagnosticFlow.tsx's Stage 3 token-"
    "substitution content (text-charcoal->text-ink, font-display->"
    "font-serif across 8 sites) along with it, already pushed to "
    "origin/main before this was caught. **Pete's explicit decision, "
    "this session: the already-shipped content stays as-is, not "
    "reverted.** Corrects the standing record rather than leaving the "
    "earlier inaccurate claim uncorrected. **Process gap, logged "
    "honestly rather than reconstructed:** the original 5-stage "
    "/diagnostic route reskin plan and its 'Option C' scope decision "
    "(reskin the entire route, all phases, internal staged-build "
    "discipline) were never written to a durable file -- they existed "
    "only in conversational context that was later compacted and lost. "
    "Confirmed via direct search across prompts/*.md, the full "
    "tools/_mob.txt, and MemPalace for 'reskin the entire,' 'internal "
    "staged-build discipline,' 'Stage 3 of 5,' and related phrases -- "
    "zero matches anywhere. **What's recoverable, confirmed from the "
    "actual diffs, not the missing plan document:** Stage 3 = the "
    "token-substitution sweep (charcoal->ink, font-display->font-serif, "
    "bg-paper->bg-field), now complete across DiagnosticFlow.tsx (shipped "
    "290ce8d), web/app/diagnostic/page.tsx, and the token portion of "
    "PrivateOutput.tsx (which also separately carries the Stage 2 "
    "ConstellationField live-mode wiring -- results-surface integration, "
    "not a token swap, hand-verified against two real dimension_summary "
    "payloads, one Entrenched from tonight's live round trip and one "
    "Endemic from a fresh direct engine invocation, both producing "
    "correctly differentiated --oxide/--urgency accent tokens with no "
    "NaN or undefined anywhere in the computed shape). **What's NOT "
    "recoverable: Stages 4 and 5's actual intended scope is genuinely "
    "unknown** -- flagged as such rather than inferred from the stage "
    "numbers alone. To be rescoped by Pete from scratch whenever this "
    "thread is picked back up, written to a durable file this time "
    "(prompts/*.md or its own MOB Decision Register row) rather than "
    "left in session context alone. MOB v4.61. |"
)

edit("tools/_mob.txt", Q28_ENTRY_TAIL, Q28_ENTRY_TAIL + "\n" + CORRECTION_ENTRY)

# --- Section 16 (Session Log, descending -- prepend before newest head) ---

Q28_LOG_HEAD = (
    "| **July 2026 — Splice counter bug, leaked annotation, Q28/Q31 "
    "design gap: investigated and fixed** | Counter root cause confirmed "
    "(DiagnosticFlow.tsx's fixed TOTAL_QUESTIONS=34 constant plus a naive "
    "per-answer increment with no splice awareness) and replaced with a "
    "static indexOf+1 lookup plus a '[parent][letter]' label scheme for "
    "spliced questions. Leaked dev annotation and an unresolved "
    "'[earlier legal/compliance/HR matter]' placeholder both stripped "
    "from Q28/Q31's question_text. Q28/Q31's self-contradicting guard "
    "investigated via the original pre-implementation Question Signal "
    "Map (confirms real spec-to-implementation numbering drift); "
    "Claude Code's first-pass guard-based proposal was course-corrected "
    "by Pete (same 'don't build correct-but-inert code' principle as "
    "Trajectory) -- Q28 built as a real conditional splice off Q06, Q31 "
    "excluded from the live sequence entirely and marked PARKED, content "
    "intact. vitest 36/36, tsc clean, 172-profile v23 suite unchanged at "
    "169/172. Full detail in Section 14. MOB v4.60. |"
)

CORRECTION_LOG_LINE = (
    "| **July 2026 — DiagnosticFlow.tsx reskin record corrected, planning-"
    "document gap logged** | Corrected an inaccurate prior claim: "
    "DiagnosticFlow.tsx's Stage 3 token content shipped inside commit "
    "290ce8d (whole-file staging swept it in alongside the counter fix), "
    "not held separate as previously reported -- Pete's explicit call: "
    "leave it shipped, not revert. The original 5-stage reskin plan and "
    "its Option C scope decision were never written to a durable file, "
    "confirmed via exhaustive search (prompts/*.md, tools/_mob.txt, "
    "MemPalace) -- zero matches. Stage 3 (token sweep) now confirmed "
    "complete across all three touched files; Stages 4/5's actual scope "
    "is genuinely unrecoverable, flagged for Pete to rescope from "
    "scratch and write down this time. Full detail in Section 14. "
    "MOB v4.61. |"
)

edit("tools/_mob.txt", Q28_LOG_HEAD, CORRECTION_LOG_LINE + "\n" + Q28_LOG_HEAD)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.60 |",
    "| MOB version | v4.61 |",
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
    print(f"MOB RESKIN-CORRECTION PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
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
